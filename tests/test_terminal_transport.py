"""C1/C2: local terminal collection is authoritative before provider parsing."""
from __future__ import annotations

import json
import subprocess
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common
import antigravity_wrapper
import claude_wrapper
from verdict_schema import LegVerdict


PAYLOAD = {
    "review_id": "terminal-r1", "family": "claude", "content_digest": "a" * 64,
    "verdict": "SAFE", "criteria_checked": ["correctness"], "findings": [],
    "affected_surfaces_inspected": ["fixture.txt"], "open_questions": [],
}


@pytest.fixture
def owned_children(monkeypatch):
    children = []
    popen = subprocess.Popen

    def capture(*args, **kwargs):
        child = popen(*args, **kwargs)
        children.append(child)
        return child

    monkeypatch.setattr(subprocess, "Popen", capture)
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setenv("TRIAD_SERVER_CAP_NO_BACKOFF", "1")
    yield children
    # These children never fork. Cleanup does not depend on production success.
    for child in children:
        if child.poll() is None:
            child.terminate()
        try:
            child.wait(timeout=3)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=3)


def _invoke(route, code, tmp_path, timeout=3):
    cmd = [sys.executable, "-c", code]
    if route == "ordinary":
        return _common.run_cli_with_retry(
            "claude", lambda _prompt: cmd, "read fixture", str(tmp_path), timeout,
            pydantic_cls=LegVerdict,
        )
    if route == "native":
        return claude_wrapper._run_native_structured_once(
            cmd, str(tmp_path), timeout, LegVerdict,
            expected_review_id="terminal-r1", expected_family="claude",
            expected_content_digest="a" * 64,
        )
    result = _common._run_once(
        "antigravity" if route == "agy" else "claude", cmd, str(tmp_path), timeout,
        classify_and_log=route != "agy",
    )
    if route == "agy":
        return antigravity_wrapper._interpret_run(result, LegVerdict)
    return result


def _envelope(route, capacity=False):
    if route == "agy":
        return json.dumps({"event": "result", "result": {
            "status": "SUCCESS", "structured_output": PAYLOAD,
            "response": json.dumps(PAYLOAD),
        }})
    return json.dumps({
        "is_error": capacity,
        "result": "model overloaded" if capacity else json.dumps(PAYLOAD),
        "structured_output": PAYLOAD,
    })


@pytest.mark.parametrize("route", ["raw", "ordinary", "native", "agy"])
def test_c1_corrupt_stderr_cannot_admit_complete_stdout(
    route, tmp_path, owned_children,
):
    code = ("import os; print(" + repr(_envelope(route))
            + ",flush=True); os.write(2,b'\\xff')")
    result = _invoke(route, code, tmp_path)
    assert result.vendor_exit_code == 0
    assert result.exit_code == _common.EXIT_CLI_FAIL
    assert result.classification == "unknown"
    assert result.final_answer == "" and result.validated is None
    assert "stderr" in result.extraction_error
    assert len(owned_children) == 1


@pytest.mark.parametrize("route", ["ordinary", "native"])
def test_c1_reader_failure_does_not_retry_capacity_envelope(
    route, tmp_path, owned_children,
):
    code = ("import os; print(" + repr(_envelope(route, capacity=True))
            + ",flush=True); os.write(2,b'\\xff')")
    result = _invoke(route, code, tmp_path)
    assert result.exit_code == _common.EXIT_CLI_FAIL
    assert result.classification == "unknown"
    assert result.final_answer == "" and result.validated is None
    assert len(owned_children) == 1


@pytest.mark.parametrize("route", ["raw", "ordinary", "native", "agy"])
def test_c1_clean_terminal_collection_preserves_success(
    route, tmp_path, owned_children,
):
    result = _invoke(route, "print(" + repr(_envelope(route)) + ")", tmp_path)
    assert result.exit_code == 0
    assert result.vendor_exit_code == 0
    assert len(owned_children) == 1
    if route != "raw":
        assert result.validated == PAYLOAD


def test_c1_reader_error_preserves_real_vendor_exit(tmp_path, owned_children, capsys):
    result = _invoke(
        "raw", "import os,sys; os.write(1,b'\\xff'); "
        "print('payload size exceeds',file=sys.stderr); sys.exit(1)", tmp_path,
    )
    assert result.vendor_exit_code == 1
    assert result.exit_code != 0
    assert result.classification == "token-limit"
    assert len(owned_children) == 1
    assert "stdout collection failed (UnicodeDecodeError)" in capsys.readouterr().err


def test_c1_reader_error_preserves_timeout(tmp_path, owned_children, capsys):
    result = _invoke(
        "raw", "import os,time; os.write(2,b'\\xff'); time.sleep(30)",
        tmp_path, timeout=1,
    )
    assert result.exit_code == _common.EXIT_TIMEOUT
    assert result.classification == "timeout"
    assert len(owned_children) == 1 and owned_children[0].poll() is not None
    assert "stderr collection failed (UnicodeDecodeError)" in capsys.readouterr().err


def test_c1_reader_error_preserves_genuine_capacity_retry(tmp_path, owned_children, capsys):
    code = ("import os,sys; os.write(1,b'\\xff'); "
            "print('model overloaded',file=sys.stderr); sys.exit(1)")
    result = _invoke("ordinary", code, tmp_path)
    assert result.vendor_exit_code == 1
    assert result.exit_code == _common.EXIT_RATE_GIVE_UP
    assert result.classification == "server-capacity"
    assert len(owned_children) == _common.SERVER_CAP_MAX_RETRIES + 1
    assert capsys.readouterr().err.count("stdout collection failed (UnicodeDecodeError)") == len(owned_children)


@pytest.mark.parametrize("position", [1, 2, 3])
def test_c2_thread_start_failure_reaps_spawned_child(
    position, monkeypatch, tmp_path, owned_children,
):
    real_start = threading.Thread.start
    starts = 0
    threads = []

    def fail_at_position(thread):
        nonlocal starts
        starts += 1
        threads.append(thread)
        if starts == position:
            raise RuntimeError("PRIVATE THREAD START DETAIL")
        return real_start(thread)

    monkeypatch.setattr(threading.Thread, "start", fail_at_position)
    try:
        result = _common._run_once(
            "claude", [sys.executable, "-c", "import time; time.sleep(30)"],
            str(tmp_path), 3, stdin_text="input",
        )
        assert result.exit_code == _common.EXIT_CLI_FAIL
        assert result.classification == "unknown"
        assert result.final_answer == "" and result.validated is None
        assert "PRIVATE THREAD START DETAIL" not in result.extraction_error
        assert len(owned_children) == 1 and owned_children[0].poll() is not None
        assert all(not thread.is_alive() for thread in threads)
    finally:
        # A failing RED must also release its already-started pipe reader.
        for child in owned_children:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=3)
        for thread in threads:
            if thread.ident is not None:
                thread.join(timeout=3)


def test_c2_start_interrupt_preserves_identity_after_cleanup(
    monkeypatch, tmp_path, owned_children,
):
    interruption = KeyboardInterrupt("synthetic start interruption")
    monkeypatch.setattr(
        threading.Thread, "start", lambda _thread: (_ for _ in ()).throw(interruption)
    )
    with pytest.raises(KeyboardInterrupt) as caught:
        _common._run_once(
            "claude", [sys.executable, "-c", "import time; time.sleep(30)"],
            str(tmp_path), 3,
        )
    assert caught.value is interruption
    assert len(owned_children) == 1 and owned_children[0].poll() is not None
