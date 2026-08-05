from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError


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
    with pytest.raises(ValidationError, match="SAFE requires no Critical or Major finding"):
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
    ],
)
def test_rejects_unbound_or_unsafe_contract_values(field, value):
    with pytest.raises(ValidationError):
        LegVerdict.model_validate({**VALID, field: value})


def test_rejects_unknown_result_fields():
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        LegVerdict.model_validate({**VALID, "batch_id": "batch-0001"})


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
