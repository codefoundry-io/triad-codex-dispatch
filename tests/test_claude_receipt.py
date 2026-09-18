"""Exercise Claude receipts through real extraction and audit persistence."""
from __future__ import annotations

import json
import stat
import sys
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common  # noqa: E402
import claude_wrapper  # noqa: E402


class _Answer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ok: bool


@pytest.fixture
def invoke(monkeypatch, tmp_path, capsys):
    log_root = tmp_path.resolve() / "logs"
    monkeypatch.setattr(_common, "_LOG_DIR", log_root)
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", True)
    monkeypatch.delenv("TRIAD_WRAPPER_HARDENED", raising=False)
    monkeypatch.delenv("TRIAD_AUDIT_REDACT_PROMPTS", raising=False)
    monkeypatch.setattr(claude_wrapper, "require_binary", lambda _: "/fixture/claude")
    monkeypatch.setattr(claude_wrapper, "load_pydantic_class", lambda _: _Answer)

    def run(envelope, *, native=False, raw=None):
        calls = []

        def provider(cli, cmd, cwd, timeout, **kwargs):
            calls.append((cli, cmd, kwargs))
            return _common.RunResult(
                exit_code=0,
                stdout=json.dumps(envelope) if raw is None else raw,
                stderr="",
                elapsed_s=0.1,
                vendor_exit_code=0,
            )

        monkeypatch.setattr(_common, "_run_once", provider)
        argv = ["claude_wrapper.py", "--prompt", "review", "--cwd", str(ROOT)]
        if native:
            argv += ["--pydantic", "fixture:Answer"]
        monkeypatch.setattr(sys, "argv", argv)
        rc = claude_wrapper.main()
        output = capsys.readouterr().out
        assert len(calls) == 1, "metadata must not add provider requests"
        assert calls[0][2]["stdin_text"] == "review"
        audit_path = log_root / "claude" / "audit.jsonl"
        records = [json.loads(line) for line in audit_path.read_text().splitlines()] if audit_path.exists() else []
        return rc, output, records, log_root

    return run


def envelope_with_metadata():
    # Metadata follows a result longer than audit's stdout preview.
    return {
        "result": "answer " * 600,
        "session_id": "00000000-0000-4000-8000-000000000004",
        "usage": {
            "input_tokens": 12, "output_tokens": 34,
            "cache_read_input_tokens": 56, "cache_creation_input_tokens": 78,
            "server_tool_use": {"tool_input": "DO-NOT-COPY"},
        },
        "modelUsage": {
            "claude-sonnet-example": {
                "inputTokens": 10, "outputTokens": 30,
                "cacheReadInputTokens": 50, "cacheCreationInputTokens": 70,
                "costUSD": 0.2, "tool_input": "DO-NOT-COPY",
            },
            "claude-haiku-example": {"inputTokens": 2, "outputTokens": 4},
        },
        "total_cost_usd": 0.25,
        "permission_denials": [{"tool_name": "Read", "tool_input": {"path": "DO-NOT-COPY"}}],
        "unknown": "DO-NOT-COPY",
    }


@pytest.mark.parametrize("native", [False, True])
def test_receipt_retains_metadata_after_long_result_without_changing_answer(invoke, native):
    envelope = envelope_with_metadata()
    if native:
        envelope["structured_output"] = {"ok": True}
    rc, output, records, root = invoke(envelope, native=native)
    assert rc == 0
    assert output == ('{"ok": true}\n' if native else envelope["result"] + "\n")
    assert len(records) == 1
    assert records[0]["classification"] == "ok"
    assert records[0]["vendor_exit_code"] == 0
    assert "session_id" not in records[0]["stdout_head"]
    assert records[0]["claude_receipt"] == {
        "session_id": "00000000-0000-4000-8000-000000000004",
        "usage": {"input_tokens": 12, "output_tokens": 34,
                  "cache_read_input_tokens": 56, "cache_creation_input_tokens": 78},
        "model_usage": {
            "claude-sonnet-example": {
                "input_tokens": 10, "output_tokens": 30,
                "cache_read_input_tokens": 50, "cache_creation_input_tokens": 70,
                "estimated_cost_usd": 0.2,
            },
            "claude-haiku-example": {"input_tokens": 2, "output_tokens": 4},
        },
        "estimated_cost_usd": 0.25,
        "permission_denial_count": 1,
    }
    assert "DO-NOT-COPY" not in json.dumps(records[0]["claude_receipt"])
    assert not list((root / "claude" / "runs").glob("*.json"))
    assert stat.S_IMODE((root / "claude" / "audit.jsonl").stat().st_mode) == 0o600


@pytest.mark.parametrize("invalid", [True, -1, "9", None, [], {}, 1.5, 2**53])
def test_invalid_token_counts_are_omitted_without_losing_valid_fields(invoke, invalid):
    rc, output, records, _ = invoke({
        "result": "ok", "usage": {"input_tokens": invalid, "output_tokens": 0},
        "modelUsage": {"claude-example": {"inputTokens": invalid, "outputTokens": 7}},
    })
    assert (rc, output) == (0, "ok\n")
    assert records[0]["claude_receipt"] == {
        "usage": {"output_tokens": 0},
        "model_usage": {"claude-example": {"output_tokens": 7}},
    }


@pytest.mark.parametrize("invalid", [True, -0.01, "0.2", None, [], {}, float("nan"), float("inf"), 1_000_001, 10**400])
def test_invalid_cost_estimates_are_omitted(invoke, invalid):
    rc, output, records, _ = invoke({
        "result": "ok", "total_cost_usd": invalid, "permission_denials": [],
        "modelUsage": {"claude-example": {"costUSD": invalid}},
    })
    assert (rc, output) == (0, "ok\n")
    assert records[0]["claude_receipt"] == {"permission_denial_count": 0}


@pytest.mark.parametrize("metadata", [
    {},
    {"session_id": "not-a-uuid", "usage": [], "modelUsage": [], "permission_denials": {}},
    {"session_id": {"value": "00000000-0000-4000-8000-000000000004"}},
    {"modelUsage": {"bad\nmodel": {"inputTokens": 1}, "m" * 129: {"inputTokens": 1}}},
    {"modelUsage": {f"claude-{i}": {"inputTokens": 1} for i in range(17)}},
])
def test_missing_malformed_or_excessive_metadata_adds_no_receipt(invoke, metadata):
    rc, output, records, _ = invoke({"result": "ok", **metadata})
    assert (rc, output) == (0, "ok\n")
    assert "claude_receipt" not in records[0]


def test_receipt_preserves_supported_fenced_json_answer(invoke):
    raw = '```json\n{"result":"ok","usage":{"input_tokens":1}}\n```'
    rc, output, records, _ = invoke({}, raw=raw)
    assert (rc, output) == (0, "ok\n")
    assert records[0]["claude_receipt"] == {"usage": {"input_tokens": 1}}


@pytest.mark.parametrize("raw", ["not-json", "[]", "null", "[" * 2000 + "]" * 2000])
def test_malformed_envelope_preserves_extraction_failure_without_receipt(invoke, raw):
    rc, output, records, _ = invoke({}, raw=raw)
    assert rc == _common.EXIT_CLI_FAIL
    assert output == ""
    assert records[0]["classification"] == "extraction-error"
    assert "claude_receipt" not in records[0]


def test_empty_result_denials_preserve_task_blocked_and_failure_ipc(invoke):
    envelope = envelope_with_metadata()
    envelope["result"] = ""
    rc, output, records, root = invoke(envelope)
    assert (rc, output) == (_common.EXIT_TERMINAL, "")
    assert records[0]["classification"] == "task-blocked"
    assert records[0]["claude_receipt"]["permission_denial_count"] == 1
    runlogs = list((root / "claude" / "runs").glob("*.json"))
    assert len(runlogs) == 1
    ipc = json.loads(runlogs[0].read_text())
    assert "claude_receipt" not in ipc
    assert "_claude_receipt" not in ipc


@pytest.mark.parametrize("setting", ["TRIAD_AUDIT_REDACT_PROMPTS", "TRIAD_WRAPPER_HARDENED"])
def test_redacted_audit_omits_receipt_identifiers_but_keeps_numeric_totals(invoke, monkeypatch, setting):
    monkeypatch.setenv(setting, "1")
    monkeypatch.setenv("TRIAD_WRAPPER_ALLOWED_ROOTS", str(ROOT))
    rc, _, records, _ = invoke(envelope_with_metadata())
    assert rc == 0
    assert records[0]["stdout_head"] == "<redacted>"
    assert records[0]["claude_receipt"] == {
        "usage": {"input_tokens": 12, "output_tokens": 34,
                  "cache_read_input_tokens": 56, "cache_creation_input_tokens": 78},
        "estimated_cost_usd": 0.25, "permission_denial_count": 1,
    }


def test_receipt_storage_failure_is_advisory(invoke, monkeypatch):
    def storage_failure(*args):
        raise OSError("synthetic audit storage failure")

    monkeypatch.setattr(_common, "_persist_audit_record", storage_failure)
    rc, output, records, root = invoke(envelope_with_metadata())
    assert (rc, output) == (0, "answer " * 600 + "\n")
    assert records == []
    assert not list((root / "claude" / "runs").glob("*.json"))


def test_receipts_use_existing_bounded_private_audit_rotation(invoke, monkeypatch):
    monkeypatch.setattr(_common, "AUDIT_ROTATE_BYTES", 200)
    monkeypatch.setattr(_common, "AUDIT_MAX_ARCHIVES", 2)
    monkeypatch.setattr(_common, "AUDIT_ARCHIVE_MAX_BYTES", 100_000)
    for _ in range(5):
        rc, _, _, root = invoke(envelope_with_metadata())
        assert rc == 0
    archives = sorted((root / "claude").glob("audit.*.jsonl"))
    assert len(archives) == 2
    for path in archives:
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        for line in path.read_text().splitlines():
            assert json.loads(line)["claude_receipt"]["estimated_cost_usd"] == 0.25


def test_other_provider_audit_schema_stays_unchanged(invoke):
    _, _, _, root = invoke({"result": "ok"})
    result = _common.RunResult(0, "ok", "", 0.1, final_answer="ok")
    assert _common.audit("gemini", ["gemini"], "review", result) is True
    record = json.loads((root / "gemini" / "audit.jsonl").read_text())
    assert "claude_receipt" not in record
