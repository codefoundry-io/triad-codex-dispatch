"""Observe real child launch directories through the existing audit boundary."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common  # noqa: E402


@pytest.fixture
def receipt(monkeypatch, tmp_path):
    log_root = tmp_path.resolve() / "logs"
    monkeypatch.setattr(_common, "_LOG_DIR", log_root)
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", True)
    monkeypatch.delenv("TRIAD_WRAPPER_HARDENED", raising=False)
    monkeypatch.delenv("TRIAD_AUDIT_REDACT_PROMPTS", raising=False)

    def persist(result, cli="claude"):
        assert _common.audit(cli, [cli], "review", result) is True
        return json.loads((log_root / cli / "audit.jsonl").read_text().splitlines()[-1])

    return persist


def run(cwd=None, program="import os; print(os.getcwd())", timeout=5, **kwargs):
    return _common._run_once(
        "claude", [sys.executable, "-c", program], cwd, timeout, **kwargs
    )


@pytest.mark.parametrize("cli", ["claude", "gemini", "antigravity"])
@pytest.mark.parametrize("explicit", [False, True])
def test_audit_directory_matches_real_child_and_survives_parent_chdir(
    receipt, monkeypatch, tmp_path, explicit, cli
):
    launch = tmp_path.resolve() / "launch directory 한글"
    launch.mkdir()
    if not explicit:
        monkeypatch.chdir(launch)
    result = run(str(launch) if explicit else None)
    assert result.exit_code == 0
    assert result.stdout.strip() == str(launch)
    monkeypatch.chdir(tmp_path)
    assert receipt(result, cli)["effective_cwd"] == str(launch)


@pytest.mark.parametrize("setting", ["TRIAD_WRAPPER_HARDENED", "TRIAD_AUDIT_REDACT_PROMPTS"])
def test_private_audit_masks_entire_directory(receipt, monkeypatch, tmp_path, setting):
    monkeypatch.setenv(setting, "1")
    launch = tmp_path.resolve()
    result = run(str(launch), "print('ok')")
    record = receipt(result)
    assert record["effective_cwd"] == "<redacted:cwd-path>"
    assert str(launch) not in json.dumps(record)
    assert result.exit_code == 0


@pytest.mark.parametrize(
    ("program", "timeout", "expected"),
    [("raise SystemExit(7)", 5, _common.EXIT_CLI_FAIL),
     ("import time; time.sleep(10)", 1, _common.EXIT_TIMEOUT)],
)
def test_launched_failures_keep_directory_without_changing_exit_or_ipc(
    receipt, tmp_path, program, timeout, expected
):
    launch = str(tmp_path.resolve())
    result = run(launch, program, timeout)
    assert result.exit_code == expected
    record = receipt(result)
    assert record["effective_cwd"] == launch
    assert record["exit_code"] == expected
    ipc_path = _common.emit_run_log("claude", ["wrapper"], ["claude"], "review", result)
    ipc = json.loads(ipc_path.read_text())
    assert "effective_cwd" not in ipc
    assert "_effective_cwd" not in ipc
    assert ipc["exit_code"] == expected


def test_prelaunch_failures_do_not_claim_child_directory(receipt, tmp_path):
    bad_encoding = run(str(tmp_path.resolve()), stdin_text="\ud800")
    assert bad_encoding._stdin_delivery_failed
    assert "effective_cwd" not in receipt(bad_encoding)
    spawn_failure = _common._run_once(
        "claude", [str(tmp_path / "nonexistent-executable")], str(tmp_path.resolve()), 5
    )
    assert spawn_failure.exit_code == _common.EXIT_ARG_ERROR
    assert "effective_cwd" not in receipt(spawn_failure)
