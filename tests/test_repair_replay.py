"""Stored failure verification: real owner CLI, no vendor execution."""
import json
import copy
import os
import signal
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common

PHRASE = "u4b replay synthetic capacity marker"


def run_case(tmp_path, monkeypatch, *, cli="antigravity", stderr=PHRASE,
             stdout="", vendor_exit=7, classification="unknown", expected="server-capacity",
             change=None, learned=True, vendor_mapping=False, verify_path=None,
             original_result=None):
    # Use the actual IPC producer. Recorded commands are data, never replayed.
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", True)
    result = original_result or _common.RunResult(
        1, stdout, stderr, 0, classification=classification, vendor_exit_code=vendor_exit)
    if original_result is None:
        result.transport = {"schema_version": 2, "stdin_delivery": "complete"}
    marker = tmp_path / "recorded-command-executed"
    saved_command = [sys.executable, "-c", f"from pathlib import Path; Path({str(marker)!r}).touch()"]
    path = _common.emit_run_log(cli, saved_command, saved_command, "fixture", result)
    assert path is not None
    assert path.is_relative_to(tmp_path / "logs")
    record = json.loads(path.read_text())
    if change:
        record.update(change)
        path.write_text(json.dumps(record))
    proposal = tmp_path / "proposal.json"
    target = ({"vendor_exit_code": 7} if vendor_mapping or expected == "extraction-error"
              else {"pattern_list": "SERVER_CAPACITY_PATTERNS", "substring": PHRASE})
    proposal.write_text(json.dumps({"classification": expected, "reason": "fixture", **target}))
    extension = tmp_path / "extension.json"
    entry = ({"vendor_exit_map": {str(vendor_exit): expected}} if vendor_mapping
             else {"patterns": {"SERVER_CAPACITY_PATTERNS": [PHRASE]}})
    extension.write_text(json.dumps({cli: entry} if learned else {}))
    before = {p: p.read_bytes() for p in (path, proposal, extension)}
    env = os.environ.copy()
    # A competing shell override must not replace the explicitly selected file.
    env["TRIAD_CLASSIFIER_EXTENSION"] = str(tmp_path / "wrong-extension.json")
    completed = subprocess.run([sys.executable, str(ROOT / "bin/apply_patch.py"),
        "--cli", cli, "--classifier-file", str(extension), "--proposal-file", str(proposal),
        "--verify-run-log", str(path) if verify_path is None else verify_path],
        env=env, capture_output=True, text=True)
    assert all(p.read_bytes() == data for p, data in before.items())
    assert not (extension.parent / (extension.name + ".lock")).exists()
    assert not marker.exists()
    return completed


@pytest.mark.parametrize("cli", ["antigravity", "claude", "gemini"])
def test_verify_uses_selected_extension_and_original_failure(tmp_path, monkeypatch, cli):
    run = run_case(tmp_path, monkeypatch, cli=cli)
    assert run.returncode == 0, run.stderr
    assert "verified" in run.stdout.lower()


def test_verify_preserves_agy_wrong_channel_control(tmp_path, monkeypatch):
    stdout = json.dumps({"event": "result", "result": {"status": "ERROR", "error": PHRASE}})
    run = run_case(tmp_path, monkeypatch, stderr="", stdout=stdout)
    assert run.returncode == 3
    assert "unknown" in run.stderr


def test_verify_does_not_apply_a_missing_proposal(tmp_path, monkeypatch):
    run = run_case(tmp_path, monkeypatch, learned=False)
    assert run.returncode == 3
    assert "unknown" in run.stderr


def test_verify_uses_original_auth_carrier_before_learned_phrase(tmp_path, monkeypatch):
    run = run_case(tmp_path, monkeypatch, stderr="Authentication required. Please visit the URL to log in:\n" + PHRASE)
    assert run.returncode == 3
    assert "oauth-env" in run.stderr


@pytest.mark.parametrize("change", [
    {"classification": "timeout", "exit_code": 2},
    {"classification": "oauth-env", "exit_code": 65},
    {"classification": "ok", "exit_code": 0},
    {"cli": "gemini"},
    {"vendor_exit_code": None},
    {"vendor_exit_code": -15},
    {"vendor_exit_code": True},
    {"stdout": ["wrong type"]},
    {"transport": {"stdin_delivery": "failed"}},
])
def test_verify_rejects_ineligible_or_unusable_record(tmp_path, monkeypatch, change):
    run = run_case(tmp_path, monkeypatch, change=change)
    assert run.returncode == 3


def test_verify_claude_extraction_uses_real_extractor(tmp_path, monkeypatch):
    stdout = json.dumps({"is_error": True, "result": PHRASE})
    run = run_case(tmp_path, monkeypatch, cli="claude", stderr="", stdout=stdout,
                   vendor_exit=0, classification="extraction-error")
    assert run.returncode == 0, run.stderr


def test_verify_does_not_treat_diagnostic_as_vendor_input(tmp_path, monkeypatch):
    run = run_case(tmp_path, monkeypatch, stderr="", vendor_exit=0,
                   classification="extraction-error", change={"extraction_error": PHRASE})
    assert run.returncode == 3
    assert "extraction-error" in run.stderr


def test_verify_uses_raw_vendor_exit_mapping(tmp_path, monkeypatch):
    run = run_case(tmp_path, monkeypatch, cli="gemini", stderr="", vendor_mapping=True)
    assert run.returncode == 0, run.stderr


def test_verify_rejects_non_string_expected_class(tmp_path, monkeypatch):
    run = run_case(tmp_path, monkeypatch, expected=["server-capacity"])
    assert run.returncode == 3


@pytest.mark.parametrize("cli", ["antigravity", "claude", "gemini"])
def test_verify_rejects_unchanged_extraction_class(tmp_path, monkeypatch, cli):
    run = run_case(tmp_path, monkeypatch, cli=cli, stderr="", vendor_exit=0,
                   classification="extraction-error", expected="extraction-error", learned=False)
    assert run.returncode == 3


@pytest.mark.parametrize("diagnostic", [
    "stdout collection failed (incomplete)",
    "stderr collection failed (UnicodeDecodeError)",
    "process-group cleanup incomplete",
])
def test_verify_refuses_recorded_output_failure(tmp_path, monkeypatch, diagnostic):
    run = run_case(tmp_path, monkeypatch, stderr="", vendor_exit=0,
                   expected="extraction-error", learned=False,
                   change={"extraction_error": diagnostic})
    assert run.returncode == 3


def test_verify_refuses_setup_failure_despite_learned_exit(tmp_path, monkeypatch):
    run = run_case(tmp_path, monkeypatch, stderr="", vendor_mapping=True,
                   change={"extraction_error": "transport setup/wait failed (RuntimeError)"})
    assert run.returncode == 3


def test_verify_refuses_actual_reader_failure(tmp_path, monkeypatch):
    result = _common._run_once("antigravity",
        [sys.executable, "-c", "import os; os.write(1, b'\\xff')"],
        str(tmp_path), 5, classify_and_log=False)
    assert result.classification == "unknown" and result._output_transport_failed
    assert result.transport["stdin_delivery"] == "not-used"
    run = run_case(tmp_path, monkeypatch, original_result=result,
                   expected="extraction-error", learned=False)
    assert run.returncode == 3


def test_empty_verify_path_never_applies(tmp_path, monkeypatch):
    run = run_case(tmp_path, monkeypatch, verify_path="")
    assert run.returncode == 3


@pytest.mark.parametrize("cli", ["antigravity", "claude", "gemini"])
def test_nonzero_reader_failure_keeps_runtime_diagnosis(tmp_path, monkeypatch, cli):
    monkeypatch.setenv("TRIAD_CLASSIFIER_EXTENSION", str(tmp_path / "absent.json"))
    command = [sys.executable, "-c", "import os,sys; os.write(1,b'\\xff'); "
               f"print({PHRASE!r},file=sys.stderr); sys.exit(7)"]
    result = _common._run_once(cli, command, str(tmp_path), 5)
    assert result.vendor_exit_code == 7 and result.classification == "unknown"
    assert not result._output_transport_failed
    if cli == "antigravity":
        from antigravity_wrapper import _interpret_run
        result = _interpret_run(result, None)
    run = run_case(tmp_path, monkeypatch, cli=cli, original_result=result)
    assert run.returncode == 0, run.stderr
    monkeypatch.setenv("TRIAD_CLASSIFIER_EXTENSION", str(tmp_path / "extension.json"))
    actual = (_interpret_run(copy.copy(result), None).classification if cli == "antigravity"
              else _common.classify(cli, result.stderr, result.stdout, result.exit_code,
                                    vendor_exit_code=result.vendor_exit_code))
    assert actual == "server-capacity"


def test_verify_refuses_actual_interruption_record(tmp_path, monkeypatch):
    result = _common.RunResult(0, "", "", 0, vendor_exit_code=0)
    result.transport = {"schema_version": 2, "stdin_delivery": "not-used"}
    _common._mark_signal_failure(result, signal.SIGTERM, "antigravity")
    run = run_case(tmp_path, monkeypatch, original_result=result,
                   expected="extraction-error", learned=False)
    assert run.returncode == 3
