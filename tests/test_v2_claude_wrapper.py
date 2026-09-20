"""Public v2 bindings survive the real Claude extraction and audit boundary."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common
import claude_wrapper
from test_v2_producer_adapter import binding, verdict


@pytest.fixture
def invoke(tmp_path, monkeypatch, capsys):
    log_root = tmp_path.resolve() / "logs"
    monkeypatch.setattr(_common, "_LOG_DIR", log_root)
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", True)
    monkeypatch.setenv("TRIAD_WRAPPER_ALLOWED_ROOTS", str(ROOT))
    monkeypatch.setenv("TRIAD_WRAPPER_HARDENED", "1")
    calls = []
    resolutions = []

    def binary(name):
        resolutions.append(name)
        return "/fixture/claude"

    monkeypatch.setattr(claude_wrapper, "require_binary", binary)

    def run(*, output=None, raw=None, omit=None, replace=None, extra=(), vendor_exit=0):
        expected = verdict(family="claude", route=None, leg_name="claude-second")
        data = expected if output is None else {**expected, **output}
        envelope = json.dumps({"result": "", "structured_output": data}) if raw is None else raw

        def provider(cli, cmd, cwd, timeout, **kwargs):
            calls.append((cli, cmd, cwd, timeout, kwargs))
            return _common.RunResult(
                exit_code=vendor_exit, vendor_exit_code=vendor_exit,
                stdout=envelope, stderr="", elapsed_s=0.1,
            )

        monkeypatch.setattr(_common, "_run_once", provider)
        options = {
            "--pydantic": "verdict_v2:LegVerdict", "--model": "opus",
            "--effort": "high", "--timeout": "1200",
            "--expected-review-id": expected["review_id"],
            "--expected-family": "claude", "--expected-content-digest": expected["content_digest"],
            "--expected-leg-name": expected["leg_name"],
            "--expected-attempt": str(expected["attempt"]), "--expected-route": "null",
        }
        options.update(replace or {})
        if omit:
            for key in ([omit] if isinstance(omit, str) else omit):
                options.pop(key)
        argv = ["claude_wrapper.py", "--prompt", "review 한글 ' $() `text`\nnext", "--cwd", str(ROOT)]
        for key, value in options.items():
            argv.extend([key, value])
        monkeypatch.setattr(sys, "argv", argv + list(extra))
        try:
            rc = claude_wrapper.main()
        except SystemExit as error:
            rc = error.code
        stdout = capsys.readouterr().out
        audit = log_root / "claude/audit.jsonl"
        records = [json.loads(line) for line in audit.read_text().splitlines()] if audit.exists() else []
        return rc, stdout, records, calls, resolutions, expected

    return run


def test_selected_v2_sends_bound_projection_and_preserves_requested_effort_and_stdin(invoke):
    rc, stdout, records, calls, _, expected = invoke()
    assert rc == 0
    assert json.loads(stdout) == expected
    assert len(calls) == 1
    _, cmd, cwd, timeout, kwargs = calls[0]
    assert cmd[cmd.index("--model") + 1] == "opus"
    assert cmd[cmd.index("--effort") + 1] == "high"
    assert cmd[cmd.index("--permission-mode") + 1] == "plan"
    assert kwargs["stdin_text"] == "review 한글 ' $() `text`\nnext"
    assert kwargs["stdin_text"] not in cmd
    schema = json.loads(cmd[cmd.index("--json-schema") + 1])
    assert not ({"$id", "$schema", "allOf"} & schema.keys())
    for field, value in binding(expected).items():
        assert schema["properties"][field]["const"] == value
    assert records[-1]["transport"]["attempt"] == 2
    assert records[-1]["exit_code"] == 0


@pytest.mark.parametrize("changes", [
    {"leg_name": "sibling"}, {"attempt": 1}, {"route": "agy"},
    {"review_id": "different"}, {"family": "codex"}, {"content_digest": "b" * 64},
    {"open_questions": ["cannot verify"]}, {"schema_version": 1},
])
def test_mismatched_or_semantically_invalid_output_is_not_admitted(invoke, changes):
    rc, stdout, records, calls, _, _ = invoke(output=changes)
    assert rc == _common.EXIT_SCHEMA_FAIL
    assert stdout == ""
    assert len(calls) == 1
    assert records[-1]["classification"] == "schema-fail"
    assert records[-1]["transport"]["attempt"] == 2


def test_original_duplicate_member_is_not_erased_by_native_extraction(invoke):
    data = verdict(family="claude", route=None, leg_name="claude-second")
    raw = '{"result":"","structured_output":' + json.dumps(data)[:-1] + ',"attempt":2}}'
    rc, stdout, records, calls, _, _ = invoke(raw=raw)
    assert rc == _common.EXIT_SCHEMA_FAIL
    assert stdout == "" and len(calls) == 1
    assert records[-1]["classification"] == "schema-fail"


@pytest.mark.parametrize("field", [
    "--expected-review-id", "--expected-family", "--expected-content-digest",
    "--expected-leg-name", "--expected-attempt", "--expected-route",
])
def test_every_v2_binding_is_required_before_binary_resolution(invoke, field):
    rc, _, _, calls, resolutions, _ = invoke(omit=field)
    assert rc == _common.EXIT_ARG_ERROR
    assert calls == resolutions == []


@pytest.mark.parametrize("replace", [
    {"--expected-route": "agy"}, {"--expected-attempt": "0"},
    {"--expected-leg-name": "../sibling"},
    {"--pydantic": "verdict_schema:LegVerdict", "--effort": "xhigh"},
])
def test_invalid_or_legacy_mixed_binding_refuses_before_resolution(invoke, replace):
    rc, _, _, calls, resolutions, _ = invoke(replace=replace)
    assert rc == _common.EXIT_ARG_ERROR
    assert calls == resolutions == []


def test_v2_forbids_silent_model_fallback(invoke):
    rc, _, _, calls, resolutions, _ = invoke(extra=["--fallback-model", "sonnet"])
    assert rc == _common.EXIT_ARG_ERROR
    assert calls == resolutions == []


def test_failed_provider_cannot_become_success_from_valid_structured_output(invoke):
    rc, stdout, records, calls, _, _ = invoke(vendor_exit=1)
    assert rc != 0 and stdout == "" and len(calls) == 1
    assert records[-1]["vendor_exit_code"] == 1
    assert records[-1]["transport"]["attempt"] == 2
