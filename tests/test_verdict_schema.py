from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import pytest
from pydantic import StringConstraints, TypeAdapter, ValidationError


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
sys.path.insert(0, str(BIN))

from verdict_schema import LegVerdict, validate_verdict_file  # noqa: E402


VALID = {
    "review_id": "review-r1",
    "family": "claude",
    "content_digest": "a" * 64,
    "verdict": "SAFE",
    "criteria_checked": ["correctness", "compatibility"],
    "findings": [],
    "affected_surfaces_inspected": ["src/parser.py", "docs/contract.md"],
    "open_questions": [],
}


def test_safe_rejects_open_question():
    with pytest.raises(ValidationError, match="SAFE requires no open questions"):
        LegVerdict.model_validate({**VALID, "open_questions": ["Choose API semantics"]})


def test_safe_rejects_blocking_finding():
    finding = {
        "severity": "Major",
        "path": "src/parser.py",
        "line": 7,
        "trigger": "schema validation fails",
        "evidence": "the failure branch returns success",
        "correction": "return the validation error",
    }
    with pytest.raises(
        ValidationError, match="SAFE requires no Critical or Major finding"
    ):
        LegVerdict.model_validate({**VALID, "findings": [finding]})


def test_not_safe_requires_blocker_or_open_question():
    with pytest.raises(ValidationError, match="NOT-SAFE requires"):
        LegVerdict.model_validate({**VALID, "verdict": "NOT-SAFE"})


def test_safe_accepts_minor_finding():
    finding = {
        "severity": "Minor",
        "path": "docs/contract.md",
        "line": None,
        "trigger": "a maintainer follows the example",
        "evidence": "the example uses the former label",
        "correction": "update the example label",
    }
    review = LegVerdict.model_validate({**VALID, "findings": [finding]})
    assert review.verdict == "SAFE"
    assert review.findings[0].severity == "Minor"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("review_id", "../escape"),
        ("content_digest", "A" * 64),
        ("criteria_checked", [" "]),
        ("affected_surfaces_inspected", ["../escape.py"]),
        ("affected_surfaces_inspected", ["/absolute.py"]),
        ("affected_surfaces_inspected", ["line\nbreak.py"]),
        ("affected_surfaces_inspected", ["del\x7fname.py"]),
    ],
)
def test_rejects_unbound_or_unsafe_contract_values(field, value):
    with pytest.raises(ValidationError):
        LegVerdict.model_validate({**VALID, field: value})


@pytest.mark.parametrize(
    "changes",
    [
        {"affected_surfaces_inspected": ["."]},
        {
            "findings": [
                {
                    "severity": "Minor",
                    "path": ".",
                    "line": None,
                    "trigger": "the reviewer identifies the review root",
                    "evidence": "the result path is a standalone dot",
                    "correction": "name the exact affected relative file",
                }
            ]
        },
    ],
)
def test_rejects_standalone_dot_review_paths(changes):
    with pytest.raises(ValidationError):
        LegVerdict.model_validate({**VALID, **changes})


def test_rejects_unknown_result_fields():
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        LegVerdict.model_validate({**VALID, "batch_id": "batch-0001"})


def test_native_schema_rejects_noncanonical_review_paths():
    schema = LegVerdict.model_json_schema()
    surface_pattern = schema["properties"]["affected_surfaces_inspected"]["items"][
        "pattern"
    ]
    finding_pattern = schema["$defs"]["LegFinding"]["properties"]["path"]["pattern"]

    for pattern in (surface_pattern, finding_pattern):
        assert re.search(pattern, "src/parser.py")
        assert re.search(pattern, "docs/space name.md")
        assert re.search(pattern, ".gitignore")
        assert re.search(pattern, "..hidden")
        assert not re.search(pattern, "/absolute/path.py")
        assert not re.search(pattern, r"src\windows.py")
        assert not re.search(pattern, "src/validation/seeds/")
        assert not re.search(pattern, ".")
        assert not re.search(pattern, "..")
        assert not re.search(pattern, "./src/a.py")
        assert not re.search(pattern, "../escape.py")
        assert not re.search(pattern, "src/./a.py")
        assert not re.search(pattern, "src/../a.py")
        assert not re.search(pattern, "line\nbreak.py")
        assert not re.search(pattern, "del\x7fname.py")


@pytest.mark.parametrize("field", ["affected_surfaces_inspected", "findings"])
@pytest.mark.parametrize(
    ("path", "accepted"),
    [
        (" ", False),
        ("   ", False),
        ("\u00a0", False),
        ("\u2003", False),
        (" \u00a0\u3000", False),
        (" leading.py", True),
        ("trailing.py ", True),
        ("src/ /file.py", True),
        (" / ", True),
        (" .", True),
        (". ", True),
        (".. ", True),
        ("\u00a0name.py", True),
        (".gitignore", True),
        ("..hidden", True),
        ("src/a.py", True),
    ],
)
def test_native_and_local_review_path_whitespace_contract(field, path, accepted):
    schema = LegVerdict.model_json_schema()
    if field == "affected_surfaces_inspected":
        pattern = schema["properties"][field]["items"]["pattern"]
        changes = {field: [path]}
    else:
        pattern = schema["$defs"]["LegFinding"]["properties"]["path"]["pattern"]
        changes = {
            field: [
                {
                    "severity": "Minor",
                    "path": path,
                    "trigger": "a reviewer cites this path",
                    "evidence": "the path identifies the affected source",
                    "correction": "preserve the existing path contract",
                }
            ]
        }

    # Exercise the emitted constraint in both Python and Pydantic's Rust engine.
    assert bool(re.search(pattern, path)) is accepted
    native = TypeAdapter(Annotated[str, StringConstraints(pattern=pattern)])
    if accepted:
        assert native.validate_python(path) == path
        verdict = LegVerdict.model_validate({**VALID, **changes})
        actual = (
            verdict.affected_surfaces_inspected[0]
            if field == "affected_surfaces_inspected"
            else verdict.findings[0].path
        )
        assert actual == path
    else:
        with pytest.raises(ValidationError):
            native.validate_python(path)
        with pytest.raises(ValidationError):
            LegVerdict.model_validate({**VALID, **changes})


def test_file_validation_binds_review_family_and_digest(tmp_path):
    result = tmp_path / "result.json"
    result.write_text(json.dumps(VALID), encoding="utf-8")

    with pytest.raises(ValueError, match="family mismatch"):
        validate_verdict_file(result.resolve(), "review-r1", "google", "a" * 64)
    with pytest.raises(ValueError, match="content digest mismatch"):
        validate_verdict_file(result.resolve(), "review-r1", "claude", "b" * 64)
    with pytest.raises(ValueError, match="review ID mismatch"):
        validate_verdict_file(result.resolve(), "review-r2", "claude", "a" * 64)


def test_file_validation_rejects_symlink(tmp_path):
    result = tmp_path / "result.json"
    result.write_text(json.dumps(VALID), encoding="utf-8")
    link = tmp_path / "result-link.json"
    link.symlink_to(result)

    with pytest.raises(ValueError, match="canonical existing regular file"):
        validate_verdict_file(link, "review-r1", "claude", "a" * 64)


def test_cli_schema_and_validation(tmp_path):
    schema = subprocess.run(
        [sys.executable, str(BIN / "verdict_schema.py"), "schema"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert schema.returncode == 0
    assert json.loads(schema.stdout)["title"] == "LegVerdict"

    result = tmp_path / "result.json"
    result.write_text(json.dumps(VALID), encoding="utf-8")
    validated = subprocess.run(
        [
            sys.executable,
            str(BIN / "verdict_schema.py"),
            "validate",
            "--result-file",
            str(result.resolve()),
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "claude",
            "--expected-content-digest",
            "a" * 64,
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert validated.returncode == 0
    assert json.loads(validated.stdout)["family"] == "claude"
