"""C9/C10: receipts reflect real delivery and survive both persistence paths."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common
from validate_v2 import load_contracts
from test_agy_web_evidence import invocation
from test_antigravity_stream_json import wrapper
from test_stdin_transport import children
from test_provider_wrappers import _google_selector_fixture, _google_preflight_fixture
import gemini_wrapper

pytestmark = pytest.mark.usefixtures("children")


@pytest.fixture
def logs(monkeypatch, tmp_path):
    root = tmp_path.resolve() / "logs"
    monkeypatch.setattr(_common, "_LOG_DIR", root)
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", True)
    monkeypatch.delenv("TRIAD_WRAPPER_HARDENED", raising=False)
    monkeypatch.delenv("TRIAD_AUDIT_REDACT_PROMPTS", raising=False)
    return root


def run(code, *, cli="claude", stdin=None, timeout=3):
    return _common._run_once(cli, [sys.executable, "-c", code], None, timeout,
                             stdin_text=stdin)


def persisted(logs, result, cli="claude"):
    assert _common.audit(cli, [sys.executable], "input", result)
    audit = json.loads((logs / cli / "audit.jsonl").read_text().splitlines()[-1])
    Draft202012Validator(load_contracts()["receipt-fields.json"]).validate(audit["transport"])
    failure = _common.emit_run_log(cli, ["wrapper"], [sys.executable], "input", result)
    if result.exit_code:
        assert failure is not None
        assert json.loads(failure.read_text())["transport"] == audit["transport"]
    else:
        assert failure is None
    return audit["transport"]


@pytest.mark.parametrize("cli,route", [("claude", "claude"), ("gemini", "gemini"),
                                       ("antigravity", "agy")])
def test_c9_no_stdin_actual_route_and_unknown_version(logs, cli, route):
    result = run("print('ok')", cli=cli)
    assert result.exit_code == 0
    assert persisted(logs, result, cli) == {
        "schema_version": 2, "stdin_delivery": "not-used", "route": route,
        "binary": sys.executable, "cli_version": None, "attempt": 1,
    }


def test_c9_full_utf8_delivery_is_complete_even_when_vendor_fails(logs):
    result = run("import sys; print(sys.stdin.read()); sys.exit(7)", stdin="한글 $ ` \\ ")
    assert result.vendor_exit_code == 7
    assert "한글 $ ` \\ " in result.stdout
    assert persisted(logs, result)["stdin_delivery"] == "complete"


def test_c9_encoding_failure_and_spawn_failure_never_claim_started(logs, tmp_path):
    encoding = run("print('must not start')", stdin="\ud800")
    assert encoding.exit_code != 0
    assert persisted(logs, encoding)["stdin_delivery"] == "not-started"
    missing = str(tmp_path / "nonexistent-cli")
    spawn = _common._run_once("claude", [missing], None, 2, stdin_text="hello")
    assert spawn.exit_code == _common.EXIT_ARG_ERROR
    receipt = persisted(logs, spawn)
    assert receipt["stdin_delivery"] == "not-started"
    assert receipt["binary"] == missing


def test_c9_broken_stdin_is_failed_without_overwriting_vendor_exit(logs):
    result = run("import os; os.close(0); raise SystemExit(7)", stdin="x" * 2_000_000)
    assert result.vendor_exit_code == 7
    assert result.exit_code == _common.EXIT_CLI_FAIL
    assert persisted(logs, result)["stdin_delivery"] == "failed"


def test_c9_timeout_with_incomplete_stdin_preserves_timeout(logs):
    result = run("import time; time.sleep(30)", stdin="x" * 2_000_000, timeout=1)
    assert result.exit_code == _common.EXIT_TIMEOUT
    assert persisted(logs, result)["stdin_delivery"] == "failed"


def test_c10_unobserved_custom_transport_is_not_guessed(logs):
    result = _common.RunResult(1, "", "custom transport failed", 0)
    assert persisted(logs, result) == {
        "schema_version": 2, "stdin_delivery": "unexposed", "route": "claude",
        "binary": None, "cli_version": None, "attempt": 1,
    }


def test_c10_observed_version_and_attempt_survive_masking(logs, monkeypatch):
    result = run("raise SystemExit(7)")
    assert result.transport is not None
    result.transport.update(cli_version="1.2.7", attempt=2)
    monkeypatch.setenv("TRIAD_WRAPPER_HARDENED", "1")
    receipt = persisted(logs, result)
    assert receipt["cli_version"] == "1.2.7"
    assert receipt["attempt"] == 2
    assert receipt == result.transport


def test_c9_agy_version_from_existing_probe_is_recorded(invocation, monkeypatch):
    _, log_root = invocation
    monkeypatch.setattr(sys, "argv", ["antigravity_wrapper.py", "--prompt", "question",
                                     "--sandbox", "read-only"])
    assert wrapper.main() == 0
    receipt = json.loads((log_root / "antigravity/audit.jsonl").read_text())["transport"]
    assert receipt["route"] == "agy"
    assert receipt["cli_version"] == "1.2.7"
    # This fixture substitutes the transport itself: do not manufacture stdin evidence.
    assert receipt["stdin_delivery"] == "unexposed"


def test_c9_gemini_carries_validated_preflight_version(logs, tmp_path, monkeypatch):
    selector, prompt, binary = _google_selector_fixture(tmp_path)
    preflight = _google_preflight_fixture(tmp_path, selector, binary)
    observed_version = json.loads(preflight.read_text())["gemini_version"]
    monkeypatch.setattr(gemini_wrapper, "run_cli_with_retry",
                        lambda *a, **k: _common.RunResult(1, "", "failed", 0))
    monkeypatch.setattr(sys, "argv", ["gemini_wrapper.py", "--prompt", prompt,
        "--google-selector-receipt", str(selector),
        "--google-preflight-receipt", str(preflight),
        "--pydantic", "verdict_schema:LegVerdict", "--expected-review-id", "review-r1",
        "--expected-family", "google", "--expected-content-digest", "a" * 64])
    assert gemini_wrapper.main() == 1
    record = json.loads((logs / "gemini/audit.jsonl").read_text())["transport"]
    assert record["cli_version"] == observed_version
    assert record["route"] == "gemini"
