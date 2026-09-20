"""C29: authorized research sends the shared procedure, preserving custody rules."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

from test_agy_settings import _bind, BASELINE
from test_antigravity_stream_json import ROOT, wrapper, _run_result, _stream


CLAUSE_SHA = "78bc9d8e4fc450b00715ff5b106151c1c441b714cfa8cd101feb7ad998cd6bea"
DOCUMENT_SHA = "0f65c6a8662978484d469e2688f4d8418dd006ef4eb44b8b09e5116d394a0b95"
RAW_DENIES = {"write_file(*)", "command(*)", "unsandboxed(*)", "execute_url(*)", "mcp(*)"}


@pytest.fixture
def invocation(tmp_path, monkeypatch):
    settings, backup = _bind(tmp_path, monkeypatch)
    settings.write_bytes(BASELINE)
    logs = tmp_path / "logs"
    monkeypatch.setattr(wrapper._common, "_LOG_DIR", logs)
    monkeypatch.setattr(wrapper._common, "_LOG_DIR_CONFIGURED", True)
    monkeypatch.delenv("TRIAD_WRAPPER_HARDENED", raising=False)
    monkeypatch.delenv("TRIAD_AUDIT_REDACT_PROMPTS", raising=False)
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _: "/fixture/agy")
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _: (1, 2, 7))
    commands = []

    def provider(_cli, cmd, *args, **kwargs):
        commands.append(cmd)
        assert set(json.loads(settings.read_text())["permissions"]["deny"]) == RAW_DENIES | {"command(sudo)"}
        response = {"status": "SUCCESS", "response": "research answer"}
        if "--json-schema" in cmd:
            response = {"status": "SUCCESS", "structured_output": {"ok": True}}
        return _run_result(_stream(response))

    monkeypatch.setattr(wrapper._common, "_run_once", provider)
    yield commands, logs
    assert settings.read_bytes() == BASELINE
    assert not backup.exists()


@pytest.mark.parametrize("prompt_file", [False, True])
@pytest.mark.parametrize("custom_schema", [False, True])
def test_c29_sent_prompt_preserves_caller_bytes_and_ends_with_shared_clause(
    invocation, tmp_path, monkeypatch, capsys, prompt_file, custom_schema,
):
    commands, logs = invocation
    caller = "Research 새 API; literal $(whoami) `id` 'quotes' \\ paths.\n\n  "
    args = ["antigravity_wrapper.py", "--web", "--sandbox", "read-only", "--cwd", str(tmp_path)]
    if prompt_file:
        path = tmp_path / "prompt 한글.txt"
        path.write_text(caller, encoding="utf-8")
        args += ["--prompt-file", str(path)]
    else:
        args += ["--prompt", caller]
    if custom_schema:
        args += ["--pydantic", "test_antigravity_stream_json:_Answer"]
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", args)
    assert wrapper.main() == 0
    sent = commands[0][commands[0].index("-p") + 1]
    assert sent.startswith(caller + "\n\n")
    clause = sent[len(caller) + 2:]
    assert hashlib.sha256(clause.encode()).hexdigest() == CLAUSE_SHA
    assert "--web" not in commands[0]  # Wrapper option, not a vendor flag.
    audit = json.loads((logs / "antigravity/audit.jsonl").read_text())
    assert audit["cmd"] == commands[0]
    assert audit["prompt_len"] == len(sent)
    assert not list(logs.glob("antigravity/runs/*.json"))
    answer = capsys.readouterr().out.strip()
    assert json.loads(answer) == {"ok": True} if custom_schema else answer == "research answer"


@pytest.mark.parametrize("redacted", [False, True])
def test_c29_failure_logs_use_effective_prompt_without_weakening_audit_redaction(
    invocation, monkeypatch, redacted,
):
    _, logs = invocation
    monkeypatch.setenv("TRIAD_AUDIT_REDACT_PROMPTS", "1" if redacted else "0")
    monkeypatch.setattr(wrapper._common, "_run_once", lambda *a, **k: _run_result(
        _stream({"status": "ERROR", "error": "controlled provider failure"})))
    caller = "Read an official page. " + "한" * 250
    monkeypatch.setattr(sys, "argv", ["antigravity_wrapper.py", "--prompt", caller,
                                     "--sandbox", "read-only", "--web"])
    assert wrapper.main() == wrapper._common.EXIT_TERMINAL
    audit = json.loads((logs / "antigravity/audit.jsonl").read_text())
    paths = list(logs.glob("antigravity/runs/*.json"))
    assert len(paths) == 1
    record = json.loads(paths[0].read_text())
    cmd = record["vendor_cmd"]
    sent = cmd[cmd.index("-p") + 1]
    assert sent.startswith(caller + "\n\n")
    assert hashlib.sha256(sent[len(caller) + 2:].encode()).hexdigest() == CLAUSE_SHA
    assert record["prompt_len"] == audit["prompt_len"] == len(sent)
    assert record["prompt_head"] == sent[:200]
    if redacted:
        assert caller not in json.dumps(audit, ensure_ascii=False)
        assert audit["prompt_head"] == "<redacted>"
    else:
        assert audit["cmd"] == cmd


@pytest.mark.parametrize("prompt,extra,message", [
    (" ", ["--sandbox", "read-only"], "non-empty"),
    ("question", [], "--sandbox read-only"),
    ("question", ["--sandbox", "read-only", "--preflight-only", "--expected-review-id", "r1"], "INVESTIGATION"),
    ("question", ["--sandbox", "read-only", "--pydantic", "verdict_schema:LegVerdict",
                  "--expected-review-id", "r1", "--expected-family", "google",
                  "--expected-content-digest", "a" * 64], "INVESTIGATION"),
])
def test_c29_invalid_web_requests_fail_before_provider(monkeypatch, capsys, prompt, extra, message):
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _: pytest.fail("provider probed"))
    monkeypatch.setattr(sys, "argv", ["antigravity_wrapper.py", "--prompt", prompt, "--web", *extra])
    assert wrapper.main() == wrapper._common.EXIT_ARG_ERROR
    assert message in capsys.readouterr().err


@pytest.mark.parametrize("payload", [None, b"\xff", b"no clause", b"```text\n\n```\n",
    b"```text\nunterminated", b"```text\none\n```\n```text\ntwo\n```\n"])
def test_c29_missing_or_malformed_clause_fails_before_provider(tmp_path, monkeypatch, capsys, payload):
    path = tmp_path / "investigation.md"
    if payload is not None:
        path.write_bytes(payload)
    monkeypatch.setattr(wrapper, "_WEB_EVIDENCE_PATH", path)
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _: pytest.fail("provider probed"))
    monkeypatch.setattr(sys, "argv", ["antigravity_wrapper.py", "--prompt", "question",
                                     "--web", "--sandbox", "read-only"])
    assert wrapper.main() == wrapper._common.EXIT_ARG_ERROR
    assert "web evidence" in capsys.readouterr().err


def test_c29_without_web_does_not_load_clause_or_change_prompt(invocation, tmp_path, monkeypatch):
    commands, _ = invocation
    monkeypatch.setattr(wrapper, "_WEB_EVIDENCE_PATH", tmp_path / "absent.md")
    caller = "Keep raw custom behavior.\n "
    monkeypatch.setattr(sys, "argv", ["antigravity_wrapper.py", "--prompt", caller, "--sandbox", "read-only"])
    assert wrapper.main() == 0
    assert commands[0][commands[0].index("-p") + 1] == caller


def test_c29_vendored_document_matches_shared_provenance():
    prompt_dir = ROOT / "prompts"
    manifest = json.loads((prompt_dir / "source-manifest.json").read_text())
    assert manifest["source_repository"] == "https://github.com/codefoundry-io/triad-dispatch-spec"
    assert manifest["source_commit"] == "59db77533d39e29b56b94447d28d2dc167b4b468"
    assert manifest["sha256"]["investigation.md"] == DOCUMENT_SHA
    assert hashlib.sha256((prompt_dir / "investigation.md").read_bytes()).hexdigest() == DOCUMENT_SHA
