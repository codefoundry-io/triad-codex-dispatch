"""R-AUTH/DL-104 applier behavior using synthetic local proposals, not vendor captures.

Catches accepted authentication patches, obsolete reason/entry caps, lost existing
entries and bypassed semantic validation through the owner-facing CLI.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common


def proposal(**changes):
    value = {"classification": "server-capacity", "reason": "Local contract fixture",
             "pattern_list": "SERVER_CAPACITY_PATTERNS", "substring": "capacity fixture alpha"}
    value.update(changes)
    return value


def owner_apply(tmp_path, cli, value, extension):
    path = tmp_path / "proposal.json"
    path.write_text(json.dumps(value))
    return subprocess.run([sys.executable, str(ROOT / "bin/apply_patch.py"),
                           "--cli", cli, "--classifier-file", str(extension),
                           "--proposal-file", str(path)], capture_output=True, text=True)


@pytest.mark.parametrize("cli", ["codex", "gemini", "claude", "antigravity"])
@pytest.mark.parametrize("target", ["exit", "banner"])
@pytest.mark.parametrize("entrypoint", ["helper", "owner-cli"])
def test_auth_proposal_refused_without_touching_existing_extension(tmp_path, cli, target, entrypoint):
    extension = tmp_path / "extension.json"
    original = '{"gemini":{"patterns":{"SERVER_CAPACITY_PATTERNS":["existing fixture"]}}}\n'
    extension.write_text(original)
    value = {"classification": "oauth-env", "reason": "Local auth proposal fixture"}
    value.update({"vendor_exit_code": 77} if target == "exit" else
                 {"pattern_list": "AGY_AUTH_BANNER_PATTERNS", "substring": "login fixture banner"})
    if entrypoint == "helper":
        with pytest.raises(ValueError, match="oauth-env"):
            _common.apply_classifier_patch(cli, value, extension_path=extension)
    else:
        result = owner_apply(tmp_path, cli, value, extension)
        assert result.returncode == 3, result.stdout + result.stderr
        assert "oauth-env" in result.stderr
    assert extension.read_text() == original
    assert not extension.with_suffix(".json.lock").exists()


def test_long_nonempty_reason_does_not_reject_valid_owner_proposal(tmp_path):
    extension = tmp_path / "extension.json"
    value = proposal(reason="Observed-run evidence and source attribution. " * 30)
    result = owner_apply(tmp_path, "gemini", value, extension)
    assert result.returncode == 0, result.stderr
    assert json.loads(extension.read_text())["gemini"]["patterns"] == {
        "SERVER_CAPACITY_PATTERNS": ["capacity fixture alpha"]}


def test_existing_500_entries_do_not_prevent_one_more_valid_proposal(tmp_path):
    extension = tmp_path / "extension.json"
    existing = [f"retained fixture {i}" for i in range(500)]
    extension.write_text(json.dumps({"gemini": {"patterns": {"SERVER_CAPACITY_PATTERNS": existing}}}))
    result = owner_apply(tmp_path, "gemini", proposal(), extension)
    assert result.returncode == 0, result.stderr
    assert json.loads(extension.read_text())["gemini"]["patterns"]["SERVER_CAPACITY_PATTERNS"] == (
        existing + ["capacity fixture alpha"])


@pytest.mark.parametrize("changes", [{"reason": "  "}, {"classification": "token-limit"}])
def test_invalid_semantics_still_refuse_without_modifying_file(tmp_path, changes):
    extension = tmp_path / "extension.json"
    extension.write_text("{}\n")
    result = owner_apply(tmp_path, "gemini", proposal(**changes), extension)
    assert result.returncode == 3
    assert extension.read_text() == "{}\n"


def test_existing_curated_auth_entries_are_not_removed_by_proposal_policy(tmp_path, monkeypatch):
    extension = tmp_path / "extension.json"
    original = {"antigravity": {"patterns": {"AGY_AUTH_BANNER_PATTERNS": ["curated login fixture"]}}}
    extension.write_text(json.dumps(original))
    monkeypatch.setattr(_common, "_classifier_extension_path", lambda: extension)
    assert _common.classify("antigravity", "curated login fixture", "", 1, vendor_exit_code=1) == "oauth-env"
    assert json.loads(extension.read_text()) == original
