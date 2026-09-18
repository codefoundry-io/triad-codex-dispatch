# Codex-host TRIAD Stdin Safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reject failed stdin delivery reliably, then send the local external Claude prompt through text stdin without changing review or provider settings.

**Architecture:** A preserves the existing subprocess/reader architecture and adds bounded writer reconciliation plus private transport state across both consumers. B switches only local Claude command construction to that proven transport. Each top-level task is a separate merge-gate unit with one behavioral claim.

**Tech Stack:** Python 3.12+, subprocess/threading, existing pytest and Pydantic.

**Spec:** `docs/superpowers/specs/2026-09-18-codex-stdin-safety-design.md`

## Global Constraints

- Work only in `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`, branch `codex/triad-adoption-stdin-safety`, base `05ca5443bece2337925e6431214981c8dc1b92b7`.
- Preserve dirty `AGENTS.md` (recorded SHA-256 `b7fc91cc9c2003984300c2e2f921e98956dbb89287e725ca208f5156db8568ee`) and unrelated work; never stage it with these slices.
- Never edit upstream/reference/snapshot repos, installed caches, provider settings, policy/configuration files, or other agents' files. Upstream handoff is already delivered.
- Keep Python 3.12 or newer; introduce no dependency/framework and no public result/schema/exit-code changes.
- No Gemini/AGY transport change, truncation, automatic chunking, extra transport-induced calls, version bump, changelog history rewrite, skill or migration change, installation, or release.
- Preserve timeout precedence for stdin calls, identical main-thread BaseException propagation, S1 cleanup, real vendor nonzero rc/classification/retry, non-stdin callers, formal bindings, and native one-call behavior.
- Never include prompt bytes or exception messages containing them in new diagnostics. Existing sensitive logs remain unchanged.
- A forecast: 65–105 net production lines, 45–75 novel-core lines, one behavioral claim. B forecast: 8–18 net production lines, under 10 novel-core lines, one behavioral claim. Total under 150; no L-class exception required.
- Root owns orchestration and final integration. No automatic final merge. The recorded 828-test baseline already passed; begin with new RED tests.

## Execution environment and records

Host tool cwd for every command below is `/Users/chaniri/codex_workspace`. Use standing authorized host execution when required, keep `workspace-write`, and use exactly the login-shell form. Before the first Python command record:

```sh
/bin/zsh -lic 'command -v python3; python3 --version; python3 -m pytest --version' triad-python
```

Keep outputs under `/Users/chaniri/codex_workspace/_runs/infra/20260918-triad-s3-implementation-gnccFU`, using distinct files for causal RED, GREEN, affected, and full results. Do not overwrite investigation evidence. Commands below pass the absolute checkout as `$1`; no installed provider calls occur in the suite.

Root commits the plan and spec before dispatching Task 1. Each implementer performs RED/GREEN and self-review, then commits only that task's owned implementation/test/documentation files. Root supplies the resulting commit and relevant unchanged source as the independent review package. Complete Task 1's independent review before Task 2; this workflow performs no formal admission. Focused/affected verification for Task 1 and one final full suite after Task 2 are sufficient unless a failure justifies more testing.

---

### Task 1: Make stdin delivery failure authoritative across existing consumers (unit A)

**Claim:** Failed or incomplete stdin delivery cannot become accepted success or induce retries, while genuine vendor errors and cancellation retain precedence.

**Files and ownership:**
- Modify `bin/_common.py`: private `RunResult` field; `_run_once` writer/reconciliation; early driver guard.
- Modify `bin/claude_wrapper.py`: optional native stdin keyword and early guard only; do not change main's argv route yet.
- Create `tests/test_stdin_transport.py`: synthetic subprocess and writer-state regressions.
- Modify `tests/test_provider_wrappers.py`: add one inherited-stdin descendant regression using its existing independent receipt cleanup; extend the existing interrupt fixture to cover stdin. Run its S1 process-group and formal binding regressions; no broad test rewrite.

**Interfaces:**
- Retain `_run_once(cli, cmd, cwd, timeout, stdin_text=None, classify_and_log=True, remove_env=()) -> RunResult`.
- Add defaulted private `RunResult._stdin_delivery_failed: bool = False`. True means authoritative local delivery failure; vendor nonzero and timeout results retain their own cause instead.
- Add keyword-only `stdin_text: str | None = None` to `_run_native_structured_once`, passing it only when non-None. Main does not use it until B.
- Existing explicit audit/run-log dictionaries keep their fields unchanged. Use existing `extraction_error` for fixed diagnostic and `unknown`/`EXIT_CLI_FAIL` for delivery failure.

- [ ] **A1. Add all tests before production changes.** Create the following file and add the additional test definitions in A5 and A6 before running A2. A5/A6 group the fixture definitions for readability; they are part of this initial RED setup, not post-implementation additions. The recording fixture owns every synthetic direct child and independently terminates/reaps it even if production cleanup fails. These children do not fork; existing S1 tests retain their independent descendant receipt cleanup.

```python
from __future__ import annotations

import hashlib
import io
import json
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
```

- [ ] **A2. Run causal RED.** The raw/ordinary early-close tests must fail because the current wrapper accepts success; invalid Unicode must fail because it spawns. The native tests additionally expose the missing optional keyword before A. Preserve raw/ordinary assertion failures as causal evidence, not only a signature error.

```sh
/bin/zsh -lic 'python3 -m pytest -q "$1/tests/test_stdin_transport.py" "$1/tests/test_provider_wrappers.py" -k "early_close or invalid_unicode or writer_phases or inherited_stdin" --rootdir "$1" -p no:cacheprovider' triad-red /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
```

- [ ] **A3. Implement strict encoding and writer state.** Append this field to `RunResult`:

```python
    _stdin_delivery_failed: bool = False
```

Immediately after `start = time.monotonic()` in `_run_once`, before environment/spawn:

```python
    stdin_bytes = None
    if stdin_text is not None:
        try:
            stdin_bytes = stdin_text.encode("utf-8")
        except UnicodeError:
            diagnostic = "stdin delivery failed (encoding)"
            log(diagnostic)
            return RunResult(
                EXIT_CLI_FAIL, "", "", time.monotonic() - start,
                classification="unknown", extraction_error=diagnostic,
                _stdin_delivery_failed=True,
            )
```

Replace the existing writer block only (retain process-group discovery and both output drainers):

```python
    stdin_done = threading.Event()
    stdin_errors: list[str] = []
    t_in = None
    if stdin_bytes is not None and proc.stdin is not None:
        def _feed_stdin() -> None:
            try:
                written = proc.stdin.buffer.write(stdin_bytes)
                if written != len(stdin_bytes):
                    stdin_errors.append("write")
                proc.stdin.buffer.flush()
            except Exception:
                stdin_errors.append("write")
            finally:
                try:
                    proc.stdin.close()
                except Exception:
                    stdin_errors.append("close")
                finally:
                    stdin_done.set()
        t_in = threading.Thread(target=_feed_stdin, daemon=True)
        t_in.start()

    def _finish_stdin() -> None:
        if t_in is None:
            return
        t_in.join(timeout=2)
        if not stdin_done.is_set():
            _terminate_provider_process_group(
                proc, "stdin writer incomplete", provider_pgid
            )
            t_in.join(timeout=2)
```

Add `_finish_stdin()` to the existing `except BaseException` cleanup after group termination and before bounded output joins/re-raise. Also call `_finish_stdin()` once on the normal/timeout path before output joins. No parent `proc.stdin.close()` is added. Replace the result construction/classification tail from `if timed_out:` through `return result` with:

```python
    delivery_failed = stdin_bytes is not None and (
        not stdin_done.is_set() or bool(stdin_errors)
    )
    if timed_out:
        log(f"timed out elapsed={elapsed:.1f}s")
        result = RunResult(EXIT_TIMEOUT, stdout, stderr, elapsed)
    else:
        log(f"exit={rc} elapsed={elapsed:.1f}s")
        ec = EXIT_OK if rc == 0 else EXIT_CLI_FAIL
        result = RunResult(ec, stdout, stderr, elapsed)
        if rc == 0 and delivery_failed:
            phase = stdin_errors[0] if stdin_errors else "incomplete"
            result.exit_code = EXIT_CLI_FAIL
            result.classification = "unknown"
            result.extraction_error = f"stdin delivery failed ({phase})"
            result._stdin_delivery_failed = True
            log(result.extraction_error)
    result.vendor_exit_code = rc
    if classify_and_log:
        if not result._stdin_delivery_failed:
            result.classification = classify(
                cli, stderr, stdout, result.exit_code, vendor_exit_code=rc,
            )
        log(
            f"[wrapper] {cli} {result.classification} "
            f"exit={result.exit_code} vendor={result.vendor_exit_code} "
            f"elapsed={elapsed:.1f}s"
        )
    elif not result._stdin_delivery_failed:
        result.classification = "unclassified"
    return result
```

Update `_run_once`'s docstring to state strict UTF-8 bytes, bounded completion checks, and DEVNULL when no input. Do not change output decoding or the environment scrubber.

- [ ] **A4. Carry the private failure through both consumers.** In `run_cli_with_retry`, after assigning `result = r` and before `cls = r.classification`:

```python
            if r._stdin_delivery_failed or (
                prompt_via_stdin and r.exit_code == EXIT_TIMEOUT
            ):
                return r
```

In `_run_native_structured_once`, add `stdin_text: str | None = None` after its `*`. Replace the initial `_run_once` call with:

```python
    input_kwargs = {} if stdin_text is None else {"stdin_text": stdin_text}
    result = _common._run_once(
        "claude", cmd, cwd, timeout, classify_and_log=False, **input_kwargs
    )
    if result._stdin_delivery_failed or (
        stdin_text is not None and result.exit_code == _common.EXIT_TIMEOUT
    ):
        if result.exit_code == _common.EXIT_TIMEOUT:
            result.classification = "timeout"
        log(
            f"[wrapper] claude {result.classification} "
            f"exit={result.exit_code} vendor={result.vendor_exit_code} "
            f"elapsed={result.elapsed_s:.1f}s"
        )
        return result
```

No `extract_claude_answer`, JSON parsing, schema validation, or raw-pattern classification precedes this guard. Existing nonzero vendor branches remain untouched.

- [ ] **A5. Add deterministic phase and incomplete-writer tests.** Append these tests to the same new test file; they inspect behavior at the Popen boundary and do not invoke providers. The fake writer thread in the incomplete case deliberately never starts, so it creates no background thread/locked descriptor; assertions prove bounded join calls and saved-process cleanup selection. Real S1 descendant tests remain the independent process-lifecycle evidence.

```python
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
```

- [ ] **A6. Add real inherited-stdin and interrupt coverage.** Append this test to `tests/test_provider_wrappers.py`, reusing its existing receipt validation/independent cleanup helpers. Each process publishes its own receipt through an atomic replacement, and the parent validates the complete descendant receipt before exiting. A descendant keeps stdin open after its direct parent exits successfully; reconciliation must terminate the saved group and reject incomplete delivery. Capture the owned direct Popen handle independently of all receipts. The fixture deadline is independent of production joins; finally calls the existing `_cleanup_fixture_processes(process, receipt_paths, *, wrapper_pgrp, wrapper_sid)` so a missing or interrupted direct receipt does not prevent direct-child cleanup. This cleanup does not call the production helper under test.

```python
@pytest.mark.skipif(not _POSIX_PROCESS_GROUPS or not hasattr(os, "fork"),
                    reason="requires POSIX process-group APIs and fork")
def test_run_once_inherited_stdin_is_reconciled(tmp_path, monkeypatch):
    direct_receipt = tmp_path / "direct.json"
    descendant_receipt = tmp_path / "descendant.json"
    script = tmp_path / "inherited_stdin.py"
    script.write_text('''import json,os,sys,time
from pathlib import Path
def receipt(path):
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps({"pid":os.getpid(),"pgrp":os.getpgrp(),"sid":os.getsid(0)}), encoding="utf-8")
    os.replace(temporary, path)
receipt(Path(sys.argv[1]))
child = os.fork()
if child == 0:
    receipt(Path(sys.argv[2]))
    os.close(1)
    os.close(2)
    time.sleep(30)
    os._exit(0)
deadline = time.monotonic()+3
while not Path(sys.argv[2]).exists():
    if time.monotonic() > deadline:
        os._exit(90)
    time.sleep(.01)
descendant = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
assert descendant["pid"] == child
print('{"is_error":false,"result":"success"}', flush=True)
os._exit(0)
''', encoding="utf-8")
    wrapper_pgrp, wrapper_sid = os.getpgrp(), os.getsid(0)
    direct_process = None
    real_popen = subprocess.Popen
    def capture_owned_process(*args, **kwargs):
        nonlocal direct_process
        assert direct_process is None
        direct_process = real_popen(*args, **kwargs)
        return direct_process
    monkeypatch.setattr(subprocess, "Popen", capture_owned_process)
    try:
        started = time.monotonic()
        result = _common._run_once(
            "claude", [sys.executable, str(script), str(direct_receipt),
                       str(descendant_receipt)], str(tmp_path), 5,
            stdin_text="input" * 400000)
        assert time.monotonic() - started < 20
        assert result.vendor_exit_code == 0
        assert result.exit_code == _common.EXIT_CLI_FAIL
        descendant = _read_fixture_identity(descendant_receipt)
        assert descendant is not None
        assert _wait_for_fixture_exit(descendant[0], 3)
    finally:
        _cleanup_fixture_processes(
            direct_process, (direct_receipt, descendant_receipt),
            wrapper_pgrp=wrapper_pgrp, wrapper_sid=wrapper_sid)
```

Parameterize `test_run_once_interrupt_terminates_provider_process_group` with `stdin_text` values `None` and `"input"`. In that test's fake Process replace `stdin = None` with `stdin = io.TextIOWrapper(io.BytesIO()) if stdin_text is not None else None`, and pass `stdin_text=stdin_text` to `_run_once`. Keep all existing cleanup and identical-exception assertions. The exact new decorator/signature and invocation are:

```python
@pytest.mark.parametrize("stdin_text", [None, "input"])
def test_run_once_interrupt_terminates_provider_process_group(monkeypatch, stdin_text):
```

```python
        _common._run_once("claude", ["claude", "-p", "review"], None, 60,
                          stdin_text=stdin_text)
```

- [ ] **A7. Run GREEN and affected regression.** Fix only reproduced defects in the approved claim; preserve genuine existing error/retry assertions. The timeout synthetic child must be gone after return. Existing S1 tests check process descendants and identical interrupt propagation; do not weaken their receipts or fixture cleanup.

```sh
/bin/zsh -lic 'python3 -m pytest -q "$1/tests/test_stdin_transport.py" "$1/tests/test_provider_wrappers.py" "$1/tests/test_log_cleanup.py" --rootdir "$1" -p no:cacheprovider' triad-a-green /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
```

- [ ] **A8. Self-review, commit, and return this unit for independent review.** The implementer checks the diff, production size, protected-file hash, and recorded RED/GREEN evidence, then commits only Task 1's owned code/tests. Root has already committed the plan/spec. Root supplies this implementation commit as the independent review package; final merge still requires explicit owner approval.

```sh
git -C /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability add bin/_common.py bin/claude_wrapper.py tests/test_stdin_transport.py tests/test_provider_wrappers.py
git -C /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability commit -m "fix: reject incomplete stdin delivery"
```

### Task 2: Move only local Claude prompt transport to text stdin (unit B)

**Claim:** Local external Claude receives the effective prompt through text stdin while preserving native settings, output/binding validation, and call-count behavior.

**Files and ownership:**
- Modify `bin/claude_wrapper.py`: command construction and two main call sites only.
- Modify `tests/test_provider_wrappers.py`: current ordinary/native/formal command assertions and affected fake signatures.
- Modify `tests/test_stdin_transport.py`: end-to-end prompt-file to synthetic Claude tests.
- Modify `README.md`, `README.ko.md`, `SECURITY.md`: current transport/limits/security wording.

**Interfaces:**
- Consumes A's `_run_native_structured_once(..., stdin_text: str | None = None)` and existing `run_cli_with_retry(..., prompt_via_stdin: bool = False)`.
- Keeps outer `--prompt` and `--prompt-file`, command-builder callback shape, output format and all flags; no new public interface.

- [ ] **B1. Add end-to-end route regression before changing main.** Append to `tests/test_stdin_transport.py`. The pinned executable is a tiny Python program accepting arbitrary flags. It records inner argv and consumed bytes then emits a valid formal envelope. Its path is supplied via the existing resolved-binary seam; real subprocess creation/draining remain intact. `--prompt-file` keeps the large input out of outer argv.

```python
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
    monkeypatch.setattr(claude_wrapper, "persist_result_artifacts", lambda *a, **k: None)
    args = ["claude_wrapper.py", "--prompt-file", str(prompt_file),
            "--cwd", str(tmp_path), "--model", "opus", "--effort", "xhigh"]
    if formal:
        args += ["--pydantic", "verdict_schema:LegVerdict", "--timeout", "1200",
                 "--expected-review-id", "review-r1", "--expected-family", "claude",
                 "--expected-content-digest", "a" * 64]
    monkeypatch.setattr(sys, "argv", args)
    assert claude_wrapper.main() == 0
    assert json.loads(capsys.readouterr().out) == PAYLOAD
    record = json.loads(receipt.read_text())
    assert record["n"] == len(loaded.encode("utf-8"))
    assert record["sha"] == hashlib.sha256(loaded.encode("utf-8")).hexdigest()
    assert len(children) == 1
    assert PROMPT not in record["argv"] and loaded not in record["argv"]
    assert record["argv"][:5] == ["-p", "--input-format", "text", "--output-format", "json"]
    assert record["argv"][record["argv"].index("--model") + 1] == "opus"
    assert record["argv"][record["argv"].index("--effort") + 1] == "xhigh"
    if formal:
        assert record["argv"][record["argv"].index("--permission-mode") + 1] == "plan"
        schema = json.loads(record["argv"][record["argv"].index("--json-schema") + 1])
        assert schema["properties"]["review_id"]["const"] == "review-r1"
        assert schema["properties"]["family"]["const"] == "claude"
        assert schema["properties"]["content_digest"]["const"] == "a" * 64
```

- [ ] **B2. Capture causal RED.** Expected current argv route fails on the large prompt before provider execution (`E2BIG`), so `main() == 0` fails. The subsequent exact-byte/argv assertions become GREEN only after the switch; they must not be weakened to match a shortened prompt.

```sh
/bin/zsh -lic 'python3 -m pytest -q "$1/tests/test_stdin_transport.py" -k prompt_file_reaches --rootdir "$1" -p no:cacheprovider' triad-b-red /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
```

- [ ] **B3. Apply minimal command/input changes.** Keep the effective-prompt callback argument for the ordinary driver's compatibility, but remove it from argv. The start of `build_cmd` becomes:

```python
        cmd = [
            claude_bin,
            "-p", "--input-format", "text",
            "--output-format", "json",
        ]
```

In main's native helper call add `stdin_text=args.prompt`; in main's ordinary driver call add `prompt_via_stdin=True`. Do not change schema generation, binding checks, formal settings, or `persist_result_artifacts`'s prompt argument.

Update `test_claude_route_forwards_model_effort_and_native_json` expected argv by replacing `"-p", "review",` with `"-p", "--input-format", "text",`; add:

```python
    assert captured["kwargs"]["prompt_via_stdin"] is True
```

For each Claude-native `fake_once` in `tests/test_provider_wrappers.py` that has explicit `*, classify_and_log`, extend it to `*, classify_and_log, stdin_text=None` and assert `stdin_text == "review"` when that test invokes main with `--prompt review`. Fakes using `**kwargs` need no signature change. Do not alter Gemini-only fakes. Keep the formal one-call, const-binding mismatch, no-fallback, and permission assertions intact. The canonical updated signature/assertion in `test_claude_structured_route_uses_native_schema_once` and `test_claude_formal_leg_binds_native_schema_and_local_admission` is:

```python
    def fake_once(_cli, cmd, _cwd, _timeout, *, classify_and_log, stdin_text=None):
        calls.append(cmd)
        assert stdin_text == "review"
        assert "review" not in cmd
        assert cmd[1:6] == ["-p", "--input-format", "text", "--output-format", "json"]
        assert classify_and_log is False
```

Retain each fake's existing return body and schema assertions after that prefix.

- [ ] **B4. Update only affected current documentation.** Insert this English paragraph near current wrapper/security usage (not historical release headings) in README.md, and equivalent wording in SECURITY.md under wrapper execution boundaries:

> The local Claude wrapper sends the effective prompt as UTF-8 text on the provider's stdin, preserving JSON and native-schema output. Use `--prompt-file` to keep the prompt out of the outer wrapper command line too. Claude documents a 10MB stdin cap; the vendor enforces that cap and model context/token limits still apply. The wrapper does not truncate, split, or add requests to bypass these limits. Failed stdin delivery cannot be accepted as success. Stdin removes prompt text from the inner provider argv; argv lists already prevent shell expansion. Existing sensitive prompt and transcript logs remain, and stdin does not encrypt input, prevent prompt injection, or reduce token usage.

Link “10MB stdin cap” to `https://code.claude.com/docs/en/headless#pipe-data-through-claude`. Do not convert the documented MB label into an invented byte constant. For README.ko.md insert:

> 로컬 Claude wrapper는 실제 전달할 prompt를 UTF-8 text stdin으로 provider에 보내며 JSON 및 native-schema 출력을 유지합니다. 바깥쪽 wrapper 명령줄에서도 prompt를 제외하려면 `--prompt-file`을 사용하세요. Claude 문서는 stdin의 10MB 한도를 명시하며 이 한도는 vendor가 적용합니다. 모델의 context/token 한도도 그대로 적용됩니다. Wrapper는 한도를 피하려고 prompt를 자르거나 나누거나 요청을 추가하지 않습니다. Stdin 전달 실패를 성공으로 받아들이지 않습니다. Stdin은 안쪽 provider argv에서 prompt를 제외합니다. 기존 argv 배열도 shell expansion을 방지합니다. 민감한 prompt/transcript 로그는 그대로 남으며 stdin이 입력 암호화, prompt injection 방지, token 사용량 감소를 제공하지는 않습니다.

Use the same official link in Korean. Add no tests that merely mirror this prose; rely on existing distribution/security contract checks and review.

- [ ] **B5. Run affected GREEN then full verification once.** Expected all pass, including A's transport tests, native one-call/binding tests, distribution and review-round contracts. No real provider invocation is needed. Preserve exact pass counts and command status; do not claim fresh installed exposure or release from these tests.

```sh
/bin/zsh -lic 'python3 -m pytest -q "$1/tests/test_stdin_transport.py" "$1/tests/test_provider_wrappers.py" "$1/tests/test_review_round.py" "$1/tests/test_distribution_contract.py" --rootdir "$1" -p no:cacheprovider' triad-b-green /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
/bin/zsh -lic 'python3 -m pytest -q "$1/tests" --rootdir "$1" -p no:cacheprovider' triad-full /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
git -C /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability diff --check
```

- [ ] **B6. Self-review, commit, and return Task 2 for independent review.** Against reviewed Task 1, the implementer checks the diff, production delta, protected state, and RED/GREEN/full-suite evidence, then commits only the listed Task 2 files. Root supplies that commit as the independent review package. Suggested commit:

```sh
git -C /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability add bin/claude_wrapper.py tests/test_provider_wrappers.py tests/test_stdin_transport.py README.md README.ko.md SECURITY.md
git -C /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability commit -m "fix: send Claude prompts through text stdin"
```

The handoff reports A/B causal RED and GREEN, full-suite count, no external configuration changes, unchanged upstream/reference trees, and the remaining explicit final-merge boundary. Do not run clean-release distribution verification, install, tag, or publish as part of these slices.
