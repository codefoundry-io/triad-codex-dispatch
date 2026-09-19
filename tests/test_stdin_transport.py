from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common
import claude_wrapper
from verdict_schema import LegVerdict

PROMPT = ("한글 😀 quotes ' \" backslash \\ $() `ticks` --flag\nline2\r\ntab\tend\n" * 22000)
PAYLOAD = {
    "review_id": "review-r1", "family": "claude", "content_digest": "a" * 64,
    "verdict": "SAFE", "criteria_checked": ["correctness"], "findings": [],
    "affected_surfaces_inspected": ["bin/_common.py"], "open_questions": [],
}
SUCCESS = json.dumps({"is_error": False, "result": json.dumps(PAYLOAD),
                      "structured_output": PAYLOAD})
EARLY_CLOSE = "import os; os.read(0,1); os.close(0); print(" + repr(SUCCESS) + ")"


@pytest.fixture
def children(monkeypatch):
    owned = []
    real_popen = subprocess.Popen

    def recording_popen(*args, **kwargs):
        child = real_popen(*args, **kwargs)
        owned.append(child)
        return child

    monkeypatch.setattr(subprocess, "Popen", recording_popen)
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setenv("TRIAD_SERVER_CAP_NO_BACKOFF", "1")
    try:
        yield owned
    finally:
        for child in owned:
            if child.poll() is None:
                child.terminate()
            try:
                child.wait(timeout=3)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=3)


def run(code, tmp_path, prompt=PROMPT, timeout=3):
    return _common._run_once("claude", [sys.executable, "-c", code],
                             str(tmp_path), timeout, stdin_text=prompt)


@pytest.mark.parametrize("route", ["raw", "ordinary", "native"])
def test_stdin_early_close_is_not_success(route, tmp_path, children):
    cmd = [sys.executable, "-c", EARLY_CLOSE]
    if route == "raw":
        result = run(EARLY_CLOSE, tmp_path)
    elif route == "ordinary":
        result = _common.run_cli_with_retry(
            "claude", lambda _prompt: cmd, PROMPT, str(tmp_path), 3,
            pydantic_cls=LegVerdict, prompt_via_stdin=True)
    else:
        result = claude_wrapper._run_native_structured_once(
            cmd, str(tmp_path), 3, LegVerdict, stdin_text=PROMPT,
            expected_review_id="review-r1", expected_family="claude",
            expected_content_digest="a" * 64)
    assert result.exit_code == _common.EXIT_CLI_FAIL
    assert result.vendor_exit_code == 0
    assert result.classification == "unknown"
    assert result.final_answer == ""
    assert result.validated is None
    assert len(children) == 1


@pytest.mark.parametrize("route", ["raw", "ordinary", "native"])
def test_stdin_invalid_unicode_never_spawns(route, tmp_path, children, capsys):
    code = "import sys; sys.stdin.buffer.read(); print(" + repr(SUCCESS) + ")"
    cmd = [sys.executable, "-c", code]
    if route == "raw":
        result = run(code, tmp_path, "\ud800")
    elif route == "ordinary":
        result = _common.run_cli_with_retry(
            "claude", lambda _p: cmd, "\ud800", str(tmp_path), 3,
            prompt_via_stdin=True)
    else:
        result = claude_wrapper._run_native_structured_once(
            cmd, str(tmp_path), 3, LegVerdict, stdin_text="\ud800")
    assert result.exit_code == _common.EXIT_CLI_FAIL
    assert result.vendor_exit_code == -1
    assert result.final_answer == "" and result.validated is None
    assert not children
    assert "\\ud800" not in capsys.readouterr().err


@pytest.mark.parametrize("backpressure", [False, True])
def test_stdin_exact_utf8_and_concurrent_output(backpressure, tmp_path, children):
    code = ("import hashlib,json,sys; "
            + ("sys.stdout.write('x'*262144+'\\n'); sys.stdout.flush(); "
               if backpressure else "")
            + "d=sys.stdin.buffer.read(); print(json.dumps([len(d),hashlib.sha256(d).hexdigest()]))")
    result = run(code, tmp_path)
    expected = PROMPT.encode("utf-8")
    assert result.exit_code == 0
    assert json.loads(result.stdout.splitlines()[-1]) == [
        len(expected), hashlib.sha256(expected).hexdigest()]


@pytest.mark.parametrize("route", ["ordinary", "native"])
def test_stdin_timeout_beats_partial_capacity_envelope(route, tmp_path, children):
    envelope = json.dumps({"is_error": True, "result": "model overloaded"})
    code = "import time; print(" + repr(envelope) + ",flush=True); time.sleep(30)"
    cmd = [sys.executable, "-c", code]
    if route == "ordinary":
        result = _common.run_cli_with_retry(
            "claude", lambda _p: cmd, PROMPT, str(tmp_path), 1,
            prompt_via_stdin=True)
    else:
        result = claude_wrapper._run_native_structured_once(
            cmd, str(tmp_path), 1, LegVerdict, stdin_text=PROMPT)
    assert result.exit_code == _common.EXIT_TIMEOUT
    assert result.classification == "timeout"
    assert len(children) == 1
    assert children[0].poll() is not None


@pytest.mark.parametrize("route", ["ordinary", "native"])
def test_stdin_failed_delivery_does_not_retry_capacity_shaped_output(
        route, tmp_path, children):
    envelope = json.dumps({"is_error": True, "result": "model overloaded"})
    code = "import os; os.read(0,1); os.close(0); print(" + repr(envelope) + ")"
    cmd = [sys.executable, "-c", code]
    if route == "ordinary":
        result = _common.run_cli_with_retry(
            "claude", lambda _p: cmd, PROMPT, str(tmp_path), 3,
            prompt_via_stdin=True)
    else:
        result = claude_wrapper._run_native_structured_once(
            cmd, str(tmp_path), 3, LegVerdict, stdin_text=PROMPT)
    assert result.exit_code == _common.EXIT_CLI_FAIL
    assert result.classification == "unknown"
    assert len(children) == 1


@pytest.mark.parametrize("message,expected,count", [
    ("payload size exceeds", _common.EXIT_TERMINAL, 1),
    ("model overloaded", _common.EXIT_RATE_GIVE_UP,
     _common.SERVER_CAP_MAX_RETRIES + 1),
])
def test_stdin_real_vendor_rejection_keeps_priority(
        message, expected, count, tmp_path, children):
    code = ("import os,sys; os.read(0,1); os.close(0); "
            "print(" + repr(message) + ",file=sys.stderr); sys.exit(1)")
    result = _common.run_cli_with_retry(
        "claude", lambda _p: [sys.executable, "-c", code], PROMPT,
        str(tmp_path), 3, prompt_via_stdin=True)
    assert result.exit_code == expected
    assert result.vendor_exit_code == 1
    assert not result._stdin_delivery_failed
    assert len(children) == count


def test_no_stdin_remains_devnull(tmp_path, children):
    result = run("import sys; print(len(sys.stdin.buffer.read()))", tmp_path, None)
    assert result.exit_code == 0 and result.stdout.strip() == "0"
    assert not result._stdin_delivery_failed


@pytest.mark.parametrize("failure", ["write", "short", "flush", "close", "none"])
def test_stdin_writer_phases_are_checked(failure, monkeypatch, tmp_path):
    class Input:
        @property
        def buffer(self):
            return self

        def write(self, data):
            assert data == b"input"
            if failure == "write":
                raise OSError("PRIVATE PROMPT BYTES")
            return 1 if failure == "short" else len(data)

        def flush(self):
            if failure == "flush":
                raise OSError("PRIVATE PROMPT BYTES")

        def close(self):
            if failure == "close":
                raise OSError("PRIVATE PROMPT BYTES")

    class Process:
        pid = -1
        returncode = 0
        stdin = Input()
        stdout = io.StringIO(SUCCESS)
        stderr = io.StringIO("")

        def wait(self, timeout):
            return 0

    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: Process())
    result = run("unused", tmp_path, "input")
    assert result.exit_code == (0 if failure == "none" else _common.EXIT_CLI_FAIL)
    assert "PRIVATE PROMPT BYTES" not in (result.extraction_error or "")
    assert result.vendor_exit_code == 0


def test_stdin_incomplete_writer_uses_bounded_join_and_cleanup(monkeypatch, tmp_path):
    joins = []
    cleanups = []
    real_thread = _common.threading.Thread

    class NeverStarted:
        def start(self):
            pass

        def join(self, timeout):
            joins.append(timeout)

    def thread(*args, **kwargs):
        if kwargs.get("target").__name__ == "_feed_stdin":
            return NeverStarted()
        return real_thread(*args, **kwargs)

    class Process:
        pid = -1
        returncode = 0
        stdin = io.StringIO()
        stdout = io.StringIO(SUCCESS)
        stderr = io.StringIO("")

        def wait(self, timeout):
            return 0

    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: Process())
    monkeypatch.setattr(_common.threading, "Thread", thread)
    monkeypatch.setattr(_common, "_terminate_provider_process_group",
                        lambda *args: cleanups.append(args))
    result = run("unused", tmp_path, "input")
    assert joins == [2, 2]
    assert len(cleanups) == 1
    assert result.exit_code == _common.EXIT_CLI_FAIL
    assert result.extraction_error == "stdin delivery failed (incomplete)"


def test_stdin_reconciliation_interrupt_rethrows_and_cleans_up(
        monkeypatch, tmp_path):
    interruption = KeyboardInterrupt("cancel during stdin reconciliation")
    joins = []
    cleanups = []
    real_thread = _common.threading.Thread

    class InterruptingWriter:
        def __init__(self, target):
            self.target = target

        def start(self):
            self.target()

        def is_alive(self):
            return False  # This test double completes its target synchronously.

        def join(self, timeout):
            joins.append(timeout)
            if len(joins) == 1:
                raise interruption

    class Process:
        pid = 4242
        returncode = 0
        stdin = io.TextIOWrapper(io.BytesIO())
        stdout = io.StringIO(SUCCESS)
        stderr = io.StringIO("")

        def wait(self, timeout):
            return 0

    process = Process()

    def thread(*args, **kwargs):
        if kwargs.get("target").__name__ == "_feed_stdin":
            return InterruptingWriter(kwargs["target"])
        return real_thread(*args, **kwargs)

    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: process)
    monkeypatch.setattr(_common.threading, "Thread", thread)
    monkeypatch.setattr(os, "getpgid", lambda pid: pid)
    monkeypatch.setattr(os, "getpgrp", lambda: 7)
    monkeypatch.setattr(
        _common,
        "_terminate_provider_process_group",
        lambda *args: cleanups.append(args),
    )

    with pytest.raises(KeyboardInterrupt) as caught:
        _common._run_once(
            "claude", ["claude", "-p", "review"], str(tmp_path), 60,
            stdin_text="input",
        )

    assert caught.value is interruption
    assert cleanups == [(process, "wrapper interrupted", process.pid)]
    assert joins == [2, 2]


@pytest.mark.parametrize("formal", [False, True])
def test_claude_prompt_file_reaches_text_stdin_once(
        formal, monkeypatch, tmp_path, children, capsys):
    receipt = tmp_path / "received.json"
    provider = tmp_path / "claude-fixture"
    provider.write_text(
        "#!" + sys.executable + "\n"
        "import hashlib,json,sys\n"
        "from pathlib import Path\n"
        "d=sys.stdin.buffer.read()\n"
        "Path(" + repr(str(receipt)) + ").write_text(json.dumps({"
        "'argv':sys.argv[1:],'n':len(d),'sha':hashlib.sha256(d).hexdigest()}))\n"
        "print(" + repr(SUCCESS) + ")\n", encoding="utf-8")
    provider.chmod(0o755)
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_bytes(PROMPT.encode("utf-8"))
    loaded = _common.load_prompt_text(None, str(prompt_file))
    monkeypatch.setattr(claude_wrapper, "require_binary", lambda _name: str(provider))
    log_root = tmp_path.resolve() / "logs"
    monkeypatch.setattr(_common, "_LOG_DIR", log_root)
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", True)
    monkeypatch.setenv("TRIAD_AUDIT_REDACT_PROMPTS", "1")
    args = ["claude_wrapper.py", "--prompt-file", str(prompt_file),
            "--cwd", str(tmp_path), "--model", "opus", "--effort", "xhigh"]
    if formal:
        args += ["--pydantic", "verdict_schema:LegVerdict", "--timeout", "1200",
                 "--expected-review-id", "review-r1", "--expected-family", "claude",
                 "--expected-content-digest", "a" * 64]
    monkeypatch.setattr(sys, "argv", args)
    assert claude_wrapper.main() == 0
    output = capsys.readouterr()
    assert json.loads(output.out) == PAYLOAD
    audit = json.loads((log_root / "claude" / "audit.jsonl").read_text())
    assert "--input-format" in audit["cmd"]
    assert audit["cmd"][audit["cmd"].index("--input-format") + 1] == "text"
    assert "'--input-format', 'text'" in output.err
    assert loaded not in output.err and audit["prompt_head"] == "<redacted>"
    record = json.loads(receipt.read_text())
    assert record["n"] == len(loaded.encode("utf-8"))
    assert record["sha"] == hashlib.sha256(loaded.encode("utf-8")).hexdigest()
    assert len(children) == 1
    assert PROMPT not in record["argv"] and loaded not in record["argv"]
    assert record["argv"][:5] == ["--print", "--input-format", "text", "--output-format", "json"]
    assert record["argv"][record["argv"].index("--model") + 1] == "opus"
    assert record["argv"][record["argv"].index("--effort") + 1] == "xhigh"
    if formal:
        assert record["argv"][record["argv"].index("--permission-mode") + 1] == "plan"
        schema = json.loads(record["argv"][record["argv"].index("--json-schema") + 1])
        assert schema["properties"]["review_id"]["const"] == "review-r1"
        assert schema["properties"]["family"]["const"] == "claude"
        assert schema["properties"]["content_digest"]["const"] == "a" * 64
