"""Public-contract validation; no provider inference or network is required."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "bin/validate_v2.py"
SHARED_COMMIT = "055204c83e57bf87eeac5b2422f2b17340f7c53b"
PAYLOADS = ("leg-verdict.schema.json", "review-legs.schema.json", "receipt-fields.json")
BINDING = dict(review_id="review-v2", family="codex", content_digest="a" * 64,
               leg_name="codex-main", attempt=1, route=None)


def verdict():
    return dict(schema_version=2, **BINDING, verdict="SAFE TO MERGE",
                criteria_checked=["source correctness"], findings=[],
                affected_surfaces_inspected=["bin/review_round.py"], open_questions=[])


@pytest.fixture
def validator(monkeypatch):
    assert SCRIPT.is_file(), "the published shared v2 validator is not implemented"
    monkeypatch.syspath_prepend(str(ROOT / "bin"))
    spec = importlib.util.spec_from_file_location("validate_v2_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_valid_verdict_offline_preserves_representation(validator, monkeypatch):
    def deny_network(*args, **kwargs):
        pytest.fail("offline validation attempted network access")
    monkeypatch.setattr(socket, "socket", deny_network)
    value = verdict()
    assert validator.validate_verdict(json.dumps(value), expected=BINDING) == value


@pytest.mark.parametrize("field,value", [
    ("schema_version", 1), ("extra", True), ("review_id", "review-v2\n"),
    ("attempt", True), ("attempt", 0), ("route", "agy"),
    ("affected_surfaces_inspected", ["../outside"]),
    ("affected_surfaces_inspected", ["/absolute"]),
    ("affected_surfaces_inspected", ["file\n"]),
    ("criteria_checked", []), ("open_questions", ["unresolved"]),
])
def test_schema_rejects_invalid_public_result(validator, field, value):
    data = verdict()
    data[field] = value
    with pytest.raises(ValueError):
        validator.validate_verdict(json.dumps(data), expected=BINDING)


@pytest.mark.parametrize("field", list(verdict()))
def test_required_fields_are_not_fabricated(validator, field):
    data = verdict()
    del data[field]
    with pytest.raises(ValueError):
        validator.validate_verdict(json.dumps(data), expected=BINDING)


@pytest.mark.parametrize("severity", ["Critical", "must-fix"])
def test_safe_cannot_hide_a_blocker(validator, severity):
    data = verdict()
    data["findings"] = [dict(severity=severity, path="file.py", line=1,
                            summary="source defect", context_known=True,
                            trigger="on input", evidence="source proof")]
    with pytest.raises(ValueError):
        validator.validate_verdict(json.dumps(data), expected=BINDING)


def test_minor_only_negative_is_valid_and_unchanged(validator):
    data = verdict()
    data["verdict"] = "MERGE WITH FIXES"
    data["findings"] = [dict(severity="Minor", path="file.py", line=1,
                            summary="source defect", context_known=True,
                            trigger="on input", evidence="source proof")]
    assert validator.validate_verdict(json.dumps(data), expected=BINDING) == data


@pytest.mark.parametrize("field,value", [
    ("review_id", "other"), ("family", "claude"), ("content_digest", "b" * 64),
    ("leg_name", "other"), ("attempt", 2), ("route", "agy"),
])
def test_all_expected_binding_axes_are_checked(validator, field, value):
    expected = dict(BINDING, **{field: value})
    with pytest.raises(ValueError, match="binding"):
        validator.validate_verdict(json.dumps(verdict()), expected=expected)


def test_incomplete_expected_binding_is_rejected(validator):
    with pytest.raises(ValueError, match="binding"):
        validator.validate_verdict(json.dumps(verdict()), expected={"review_id": "review-v2"})


def test_boolean_expected_attempt_cannot_equal_integer_one(validator):
    with pytest.raises(ValueError, match="binding"):
        validator.validate_verdict(json.dumps(verdict()), expected=dict(BINDING, attempt=True))


@pytest.mark.parametrize("route", ["agy", "gemini"])
def test_both_google_routes_keep_their_own_binding(validator, route):
    data = dict(verdict(), family="google", route=route)
    expected = dict(BINDING, family="google", route=route)
    assert validator.validate_verdict(json.dumps(data), expected=expected) == data


@pytest.mark.parametrize("suffix", [',"attempt":1}', ',"findings":[{"x":1,"x":2}]}'])
def test_original_duplicate_members_rejected(validator, suffix):
    with pytest.raises(ValueError, match="duplicate"):
        validator.validate_verdict(json.dumps(verdict())[:-1] + suffix, expected=BINDING)


@pytest.mark.parametrize("raw", ["{", '{"attempt":NaN}', b"\xff"])
def test_invalid_json_is_a_validation_failure(validator, raw):
    with pytest.raises(ValueError):
        validator.validate_verdict(raw, expected=BINDING)


def test_payloads_are_pinned_to_published_commit():
    manifest = json.loads((ROOT / "contracts/source-manifest.json").read_text())
    assert manifest["source_commit"] == SHARED_COMMIT
    assert manifest["status"] == "candidate"
    assert set(manifest["sha256"]) == set(PAYLOADS)
    for name, digest in manifest["sha256"].items():
        assert hashlib.sha256((ROOT / "contracts" / name).read_bytes()).hexdigest() == digest


@pytest.fixture
def copied_contracts(validator, tmp_path, monkeypatch):
    target = tmp_path / "contracts"
    shutil.copytree(ROOT / "contracts", target)
    monkeypatch.setattr(validator, "CONTRACT_ROOT", target.resolve())
    return target


@pytest.mark.parametrize("name", [*PAYLOADS, "source-manifest.json"])
@pytest.mark.parametrize("damage", ["missing", "altered", "symlink"])
def test_missing_or_changed_contract_refuses(validator, copied_contracts, name, damage):
    path = copied_contracts / name
    if damage == "missing":
        path.unlink()
    elif damage == "altered":
        path.write_bytes(path.read_bytes() + b"invalid")
    else:
        saved = copied_contracts / "saved.json"
        path.rename(saved)
        path.symlink_to(saved)
    with pytest.raises(ValueError, match=name.replace(".", r"\.")):
        validator.validate_verdict(json.dumps(verdict()), expected=BINDING)


def test_invalid_bundled_schema_names_the_contract(validator, copied_contracts):
    name = PAYLOADS[0]
    path = copied_contracts / name
    schema = json.loads(path.read_text())
    schema["type"] = "not-a-json-schema-type"
    path.write_text(json.dumps(schema))
    manifest_path = copied_contracts / "source-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["sha256"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="invalid candidate contract: leg-verdict"):
        validator.validate_verdict(json.dumps(verdict()), expected=BINDING)


def test_external_reference_never_retrieves(validator, copied_contracts, monkeypatch):
    schema_path = copied_contracts / PAYLOADS[0]
    data = json.loads(schema_path.read_text())
    data["$ref"] = "https://example.invalid/never-fetch"
    schema_path.write_text(json.dumps(data))
    manifest_path = copied_contracts / "source-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["sha256"][PAYLOADS[0]] = hashlib.sha256(schema_path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    monkeypatch.setattr(socket, "socket", lambda *a, **k: pytest.fail("network attempted"))
    with pytest.raises(ValueError):
        validator.validate_verdict(json.dumps(verdict()), expected=BINDING)


@pytest.mark.parametrize("field,value", [
    ("source_commit", "0" * 40), ("status", "adopted"), ("sha256", {}),
])
def test_manifest_metadata_cannot_claim_another_basis(validator, copied_contracts, field, value):
    path = copied_contracts / "source-manifest.json"
    data = json.loads(path.read_text())
    data[field] = value
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="manifest"):
        validator.validate_verdict(json.dumps(verdict()), expected=BINDING)


def test_cli_and_legacy_copied_file_stay_separate(validator, tmp_path):
    result = tmp_path / "result.json"
    result.write_text(json.dumps(verdict()))
    args = ["validate", "--result-file", str(result.resolve())]
    for name, value in BINDING.items():
        args += ["--expected-" + name.replace("_", "-"), "null" if value is None else str(value)]
    completed = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == verdict()
    legacy_script = tmp_path / "legacy.py"
    shutil.copyfile(ROOT / "bin/verdict_schema.py", legacy_script)
    legacy_args = ["validate", "--result-file", str(result.resolve()),
                   "--expected-review-id", BINDING["review_id"],
                   "--expected-family", "codex", "--expected-content-digest", "a" * 64]
    rejected = subprocess.run([sys.executable, str(legacy_script), *legacy_args], capture_output=True)
    assert rejected.returncode == 2
    old = copy.deepcopy(verdict())
    for field in ("schema_version", "leg_name", "attempt", "route"):
        del old[field]
    old["verdict"] = "SAFE"
    result.write_text(json.dumps(old))
    accepted = subprocess.run([sys.executable, str(legacy_script), *legacy_args], capture_output=True)
    assert accepted.returncode == 0, accepted.stderr
    with pytest.raises(ValueError):
        validator.validate_verdict(json.dumps(old), expected=BINDING)


def test_cli_preserves_escaped_unicode_without_output_encoding_failure(tmp_path):
    data = verdict()
    data["criteria_checked"] = ["\ud800"]
    result = tmp_path / "result.json"
    result.write_text(json.dumps(data), encoding="utf-8")
    args = ["validate", "--result-file", str(result.resolve())]
    for name, value in BINDING.items():
        args += ["--expected-" + name.replace("_", "-"), "null" if value is None else str(value)]
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == data
