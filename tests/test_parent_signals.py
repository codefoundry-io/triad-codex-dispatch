"""C1: catchable parent signals retain failure evidence and reap owned children."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common


def _alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


@pytest.mark.parametrize("signum", [signal.SIGTERM, signal.SIGHUP])
@pytest.mark.parametrize("route", ["ordinary", "native", "agy"])
def test_c1_parent_signal_reaps_child_and_persists_failure(tmp_path, signum, route):
    """A complete success envelope cannot override a cancelled collection."""
    ready = tmp_path / "ready.json"
    starts = tmp_path / "starts.txt"
    logs = tmp_path / "logs"
    payload = {"review_id": "signal-r1", "family": "claude", "content_digest": "a" * 64,
               "verdict": "SAFE", "criteria_checked": ["correctness"], "findings": [],
               "affected_surfaces_inspected": ["fixture.txt"], "open_questions": []}
    envelope = {"is_error": False, "result": json.dumps(payload), "structured_output": payload}
    if route == "agy":
        envelope = {"event": "result", "result": {"status": "SUCCESS",
                    "response": json.dumps(payload), "structured_output": payload}}
    # Exit zero on TERM, so cancelling the parent must not be mistaken for success.
    child_code = f'''
import json, os, signal, time
from pathlib import Path
signal.signal(signal.SIGTERM, lambda *_: exit(0))
with Path({str(starts)!r}).open("a") as stream:
    stream.write("started\\n")
print({json.dumps(envelope)!r}, flush=True)
ready = Path({str(ready)!r})
ready.with_suffix(".tmp").write_text(json.dumps({{"pid": os.getpid()}}))
ready.with_suffix(".tmp").replace(ready)
time.sleep(60)
'''
    parent_code = f'''
import json, signal, sys, threading
from pathlib import Path
sys.path.insert(0, {str(ROOT / "bin")!r})
import _common, claude_wrapper, antigravity_wrapper
from verdict_schema import LegVerdict
cmd = [sys.executable, "-c", {child_code!r}]
original = {{s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGHUP)}}
route = {route!r}
if route == "ordinary":
    result = _common.run_cli_with_retry("claude", lambda _: cmd, "fixture", {str(tmp_path)!r}, 30, pydantic_cls=LegVerdict)
elif route == "native":
    result = claude_wrapper._run_native_structured_once(cmd, {str(tmp_path)!r}, 30, LegVerdict)
else:
    result = antigravity_wrapper._interpret_run(_common._run_once("antigravity", cmd, {str(tmp_path)!r}, 30, classify_and_log=False), LegVerdict)
cli = "antigravity" if route == "agy" else "claude"
_common.audit(cli, cmd, "fixture", result)
failure = _common.emit_run_log(cli, ["signal-fixture"], cmd, "fixture", result)
print(json.dumps({{"exit": result.exit_code, "vendor_exit": result.vendor_exit_code,
    "answer": result.final_answer, "validated": result.validated,
    "failure": str(failure) if failure else None,
    "restored": all(signal.getsignal(s) == h for s, h in original.items()),
    "threads": [t.name for t in threading.enumerate() if t is not threading.main_thread()]}}), flush=True)
'''
    env = dict(os.environ, TRIAD_DISPATCH_LOG_DIR=str(logs), TRIAD_SERVER_CAP_NO_BACKOFF="1")
    parent = subprocess.Popen([sys.executable, "-c", parent_code], env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, start_new_session=True)
    child_pid = None
    try:
        deadline = time.monotonic() + 10
        while not ready.exists() and time.monotonic() < deadline and parent.poll() is None:
            time.sleep(.02)
        assert ready.exists(), "owned child did not announce readiness"
        child_pid = json.loads(ready.read_text())["pid"]
        os.kill(parent.pid, signum)
        stdout, stderr = parent.communicate(timeout=15)
        assert parent.returncode == 0, stderr
        result = json.loads(stdout)
        assert result["exit"] == _common.EXIT_CLI_FAIL
        assert result["answer"] == "" and result["validated"] is None
        assert result["restored"] and result["threads"] == []
        assert not _alive(child_pid)
        assert starts.read_text().splitlines() == ["started"]
        cli = "antigravity" if route == "agy" else "claude"
        audit = json.loads((logs / cli / "audit.jsonl").read_text().splitlines()[-1])
        failure = json.loads(Path(result["failure"]).read_text())
        assert audit["exit_code"] == failure["exit_code"] == _common.EXIT_CLI_FAIL
        assert audit["transport"] == failure["transport"]
    finally:
        # Exact ownership only, even when production fails RED and leaves a child.
        if child_pid is not None and _alive(child_pid):
            try:
                os.killpg(child_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if parent.poll() is None:
            parent.kill()
        parent.communicate(timeout=5)


@pytest.mark.parametrize("stage", ["spawn", "collected"])
def test_c1_signal_at_ownership_boundaries_cannot_admit_success(monkeypatch, tmp_path, stage):
    before = {s: signal.getsignal(s) for s in (signal.SIGTERM, signal.SIGHUP)}
    processes = []
    captured = []
    popen = subprocess.Popen

    def deliver(signum):
        handler = signal.getsignal(signum)
        captured.append(callable(handler))
        if callable(handler):
            handler(signum, None)

    def spawn(*args, **kwargs):
        proc = popen(*args, **kwargs)
        processes.append(proc)
        if stage == "spawn":
            # The child exists but has not yet been assigned to the engine local.
            deliver(signal.SIGTERM)
        else:
            wait = proc.wait

            def wait_then_signal(*args, **kwargs):
                result = wait(*args, **kwargs)
                deliver(signal.SIGHUP)
                return result

            proc.wait = wait_then_signal
        return proc

    monkeypatch.setattr(subprocess, "Popen", spawn)
    try:
        result = _common._run_once("claude", [sys.executable, "-c", "print('ok')"], str(tmp_path), 3)
        assert captured and all(captured), "termination was not captured at ownership boundary"
        assert result.exit_code == _common.EXIT_CLI_FAIL
        assert result._output_transport_failed
        assert all(proc.poll() is not None for proc in processes)
    finally:
        for proc in processes:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=3)
        assert all(signal.getsignal(s) == h for s, h in before.items())
