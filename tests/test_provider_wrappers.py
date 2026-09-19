from __future__ import annotations

import io
import hashlib
import json
import os
import signal
import sys
import subprocess
import time
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
sys.path.insert(0, str(BIN))

import _common  # noqa: E402
import antigravity_wrapper  # noqa: E402
import claude_wrapper  # noqa: E402
import gemini_wrapper  # noqa: E402
from verdict_schema import LegVerdict  # noqa: E402


class _StructuredAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


def _ok() -> _common.RunResult:
    return _common.RunResult(
        exit_code=0,
        stdout="",
        stderr="",
        elapsed_s=0.1,
        final_answer="ok",
        vendor_exit_code=0,
    )


def _canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
        + b"\n"
    )


def _google_selector_fixture(
    tmp_path: Path,
    *,
    review_id: str = "review-r1",
    route: str = "gemini",
    content_digest: str = "a" * 64,
    family: str = "google",
) -> tuple[Path, str, Path]:
    executable = (tmp_path / f"selected-{route}").resolve()
    executable.write_text("#!/bin/sh\nexit 91\n", encoding="utf-8")
    executable.chmod(0o755)
    wrapper = (
        BIN / ("antigravity_wrapper.py" if route == "agy" else "gemini_wrapper.py")
    ).resolve()
    record = {
        "authentication_class": (
            "personal-google" if route == "agy" else "gemini-enterprise"
        ),
        "executable": str(executable),
        "provider_started": False,
        "review_id": review_id,
        "route": route,
        "wrapper": str(wrapper),
    }
    receipt_path = (tmp_path / f"{route}-selector.json").resolve()
    receipt_payload = _canonical_json_bytes(record)
    receipt_path.write_bytes(receipt_payload)
    preflight_common = {
        "executable": str(executable),
        "google_selector_receipt_sha256": hashlib.sha256(receipt_payload).hexdigest(),
        "provider_started": False,
        "review_id": review_id,
        "route": route,
    }
    if route == "agy":
        preflight_record = {
            **preflight_common,
            "agy_version": "1.1.20",
            "effort": "high",
            "model": "gemini-3.1-pro-high",
            "route_args": [
                "--model",
                "gemini-3.1-pro-high",
                "--effort",
                "high",
            ],
        }
    else:
        preflight_record = {
            **preflight_common,
            "effective_approval_mode": "unexposed",
            "model": "auto",
            "policy": str(
                (ROOT / "bin" / "policies" / "gemini-formal-readonly.toml").resolve()
            ),
            "read_only_enforcement": "packaged-mode-independent-policy",
            "requested_approval_mode": "plan",
        }
    metadata = {
        "content_digest": content_digest,
        "family": family,
        "google_authentication_class": record["authentication_class"],
        "google_executable": record["executable"],
        "google_provider_started": False,
        "google_preflight_effort": "high" if route == "agy" else None,
        "google_preflight_model": preflight_record["model"],
        "google_preflight_receipt_sha256": hashlib.sha256(
            _canonical_json_bytes(preflight_record)
        ).hexdigest(),
        "google_route": route,
        "google_selector_receipt_sha256": hashlib.sha256(receipt_payload).hexdigest(),
        "google_wrapper": record["wrapper"],
        "review_id": review_id,
    }
    prompt = "Review metadata: " + _canonical_json_bytes(metadata).decode(
        "ascii"
    ).rstrip("\n")
    return receipt_path, prompt, executable


def _google_preflight_fixture(
    tmp_path: Path,
    selector_receipt: Path,
    executable: Path,
    *,
    review_id: str = "review-r1",
) -> Path:
    receipt = {
        "effective_approval_mode": "unexposed",
        "executable": str(executable),
        "google_selector_receipt_sha256": hashlib.sha256(
            selector_receipt.read_bytes()
        ).hexdigest(),
        "model": "auto",
        "policy": str(
            (ROOT / "bin" / "policies" / "gemini-formal-readonly.toml").resolve()
        ),
        "provider_started": False,
        "read_only_enforcement": "packaged-mode-independent-policy",
        "requested_approval_mode": "plan",
        "review_id": review_id,
        "route": "gemini",
    }
    path = (tmp_path / "gemini-preflight.json").resolve()
    path.write_bytes(_canonical_json_bytes(receipt))
    return path


def _formal_gemini_help() -> str:
    return (
        "  --model  Model  [string]\n"
        "  --approval-mode  Set the approval mode  [string] "
        '[choices: "default", "auto_edit", "yolo", "plan"]\n'
        "  --policy  Additional policy files or directories to load  [array]\n"
    )


_POSIX_PROCESS_GROUPS = all(
    hasattr(os, name) for name in ("setsid", "getpgid", "getsid", "killpg")
)


def _fixture_process_is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    if sys.platform.startswith("linux"):
        try:
            state = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
        except (FileNotFoundError, ProcessLookupError):
            return False
        if state.rsplit(") ", 1)[-1].split(maxsplit=1)[0] == "Z":
            return False
    return True


def _wait_for_fixture_path(path: Path, timeout_s: float) -> None:
    deadline = time.monotonic() + timeout_s
    while not path.exists():
        if time.monotonic() >= deadline:
            raise AssertionError(f"fixture did not publish {path.name}")
        time.sleep(0.02)


def _wait_for_fixture_exit(pid: int, timeout_s: float) -> bool:
    deadline = time.monotonic() + timeout_s
    while _fixture_process_is_running(pid):
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.02)
    return True


def _cleanup_recorded_fixture_process(
    pid: int,
    *,
    expected_pgrp: int,
    expected_sid: int,
    wrapper_pgrp: int,
    wrapper_sid: int,
) -> None:
    if not _fixture_process_is_running(pid):
        return
    try:
        actual_pgrp = os.getpgid(pid)
        actual_sid = os.getsid(pid)
    except ProcessLookupError:
        return
    assert actual_pgrp == expected_pgrp
    assert actual_sid == expected_sid
    assert actual_pgrp != wrapper_pgrp
    assert actual_sid != wrapper_sid
    os.kill(pid, signal.SIGKILL)
    assert _wait_for_fixture_exit(pid, 3.0)


def _read_fixture_identity(path: Path) -> tuple[int, int, int] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return (
            int(payload["pid"]),
            int(payload["pgrp"]),
            int(payload["sid"]),
        )
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _cleanup_available_fixture_receipts(
    receipt_paths: tuple[Path, ...],
    *,
    wrapper_pgrp: int,
    wrapper_sid: int,
) -> None:
    errors: list[Exception] = []
    for path in receipt_paths:
        identity = _read_fixture_identity(path)
        if identity is None:
            continue
        pid, expected_pgrp, expected_sid = identity
        try:
            _cleanup_recorded_fixture_process(
                pid,
                expected_pgrp=expected_pgrp,
                expected_sid=expected_sid,
                wrapper_pgrp=wrapper_pgrp,
                wrapper_sid=wrapper_sid,
            )
        except Exception as error:
            errors.append(error)
    if errors:
        raise AssertionError("fixture receipt cleanup failed") from errors[0]


def _reap_directly_owned_fixture_process(
    process: subprocess.Popen[str] | None,
) -> None:
    if process is None:
        return
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        process.kill()
        try:
            process.wait(timeout=3.0)
        except subprocess.TimeoutExpired as error:
            raise AssertionError("owned fixture process did not exit") from error


def _cleanup_fixture_processes(
    process: subprocess.Popen[str] | None,
    receipt_paths: tuple[Path, ...],
    *,
    wrapper_pgrp: int,
    wrapper_sid: int,
) -> None:
    errors: list[Exception] = []
    try:
        _reap_directly_owned_fixture_process(process)
    except Exception as error:
        errors.append(error)
    try:
        _cleanup_available_fixture_receipts(
            receipt_paths,
            wrapper_pgrp=wrapper_pgrp,
            wrapper_sid=wrapper_sid,
        )
    except Exception as error:
        errors.append(error)
    if errors:
        raise AssertionError("fixture cleanup failed") from errors[0]


def _write_provider_fixture(path: Path) -> None:
    path.write_text(
        """\
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


role = sys.argv[1]
state_dir = Path(sys.argv[2])
omit_aggregate = len(sys.argv) > 3 and sys.argv[3] == "omit-aggregate"
normal_exit = "normal-exit" in sys.argv[3:]
hold_output = "hold-output" in sys.argv[3:]


def write_receipt(path, payload):
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, sort_keys=True) + "\\n", encoding="utf-8")
    os.replace(temporary, path)


if role == "descendant":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    write_receipt(
        state_dir / "descendant-ready.json",
        {"pid": os.getpid(), "pgrp": os.getpgrp(), "sid": os.getsid(0)},
    )
    while True:
        time.sleep(0.05)

if role == "direct":
    term_log = state_dir / "direct-term.log"
    direct = {"pid": os.getpid(), "pgrp": os.getpgrp(), "sid": os.getsid(0)}
    write_receipt(state_dir / "direct-ready.json", direct)

    def exit_on_term(_signum, _frame):
        term_log.write_text("direct-child-received-SIGTERM\\n", encoding="utf-8")
        os._exit(0)

    signal.signal(signal.SIGTERM, exit_on_term)
    subprocess.Popen(
        [sys.executable, __file__, "descendant", str(state_dir)],
        stdin=subprocess.DEVNULL,
        stdout=None if hold_output else subprocess.DEVNULL,
        stderr=None if hold_output else subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 3.0
    descendant_receipt = state_dir / "descendant-ready.json"
    while not descendant_receipt.exists():
        if time.monotonic() >= deadline:
            raise SystemExit("descendant did not become ready")
        time.sleep(0.02)
    if not omit_aggregate:
        write_receipt(
            state_dir / "fixture-ready.json",
            {
                "direct": direct,
                "descendant": json.loads(descendant_receipt.read_text(encoding="utf-8")),
            },
        )
    if normal_exit:
        print("terminal complete", flush=True)
        os._exit(0)
    while True:
        time.sleep(0.05)

raise SystemExit(f"unknown fixture role: {role}")
""",
        encoding="utf-8",
    )


@pytest.mark.skipif(
    not _POSIX_PROCESS_GROUPS,
    reason="requires POSIX process-group APIs",
)
def test_run_once_timeout_kills_provider_descendant_after_direct_exit(
    tmp_path: Path,
) -> None:
    fixture_script = tmp_path / "provider_fixture.py"
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    _write_provider_fixture(fixture_script)
    ready_path = state_dir / "fixture-ready.json"
    direct_receipt = state_dir / "direct-ready.json"
    descendant_receipt = state_dir / "descendant-ready.json"
    term_log = state_dir / "direct-term.log"
    wrapper_pgrp = os.getpgrp()
    wrapper_sid = os.getsid(0)

    try:
        result = _common._run_once(
            "fixture",
            [sys.executable, str(fixture_script), "direct", str(state_dir)],
            None,
            timeout=1,
            classify_and_log=False,
        )
        _wait_for_fixture_path(ready_path, 1.0)
        direct = _read_fixture_identity(direct_receipt)
        descendant = _read_fixture_identity(descendant_receipt)

        assert result.exit_code == _common.EXIT_TIMEOUT
        assert term_log.read_text(encoding="utf-8") == "direct-child-received-SIGTERM\n"
        assert direct is not None
        assert descendant is not None
        assert direct[1] == direct[0]
        assert descendant[1] == direct[1]
        assert descendant[2] == direct[2]
        assert _wait_for_fixture_exit(descendant[0], 3.0)
    finally:
        _cleanup_available_fixture_receipts(
            (direct_receipt, descendant_receipt),
            wrapper_pgrp=wrapper_pgrp,
            wrapper_sid=wrapper_sid,
        )


@pytest.mark.skipif(not _POSIX_PROCESS_GROUPS, reason="requires POSIX process groups")
@pytest.mark.parametrize("hold_output", [False, True])
def test_c1_normal_exit_reconciles_owned_descendant(tmp_path, hold_output):
    script = tmp_path / "provider_fixture.py"
    state = tmp_path / "state"
    state.mkdir()
    _write_provider_fixture(script)
    receipts = (state / "direct-ready.json", state / "descendant-ready.json")
    wrapper_pgrp, wrapper_sid = os.getpgrp(), os.getsid(0)
    try:
        started = time.monotonic()
        result = _common._run_once(
            "fixture", [sys.executable, str(script), "direct", str(state),
                        "normal-exit", *( ["hold-output"] if hold_output else [])],
            str(tmp_path), timeout=5, classify_and_log=False,
        )
        assert time.monotonic() - started < 15
        assert result.vendor_exit_code == 0
        assert result.stdout.strip() == "terminal complete"
        descendant = _read_fixture_identity(receipts[1])
        assert descendant is not None
        assert _wait_for_fixture_exit(descendant[0], 3)
    finally:
        _cleanup_available_fixture_receipts(
            receipts, wrapper_pgrp=wrapper_pgrp, wrapper_sid=wrapper_sid,
        )


@pytest.mark.skipif(
    not _POSIX_PROCESS_GROUPS,
    reason="requires POSIX process-group APIs",
)
def test_provider_descendant_fixture_cleanup_recovers_when_aggregate_is_missing(
    tmp_path: Path,
) -> None:
    fixture_script = tmp_path / "provider_fixture.py"
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    _write_provider_fixture(fixture_script)
    direct_receipt = state_dir / "direct-ready.json"
    descendant_receipt = state_dir / "descendant-ready.json"
    aggregate_receipt = state_dir / "fixture-ready.json"
    wrapper_pgrp = os.getpgrp()
    wrapper_sid = os.getsid(0)
    direct_process: subprocess.Popen[str] | None = None
    direct_identity: tuple[int, int, int] | None = None
    descendant: tuple[int, int, int] | None = None

    try:
        direct_process = subprocess.Popen(
            [
                sys.executable,
                str(fixture_script),
                "direct",
                str(state_dir),
                "omit-aggregate",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        _wait_for_fixture_path(direct_receipt, 3.0)
        _wait_for_fixture_path(descendant_receipt, 3.0)
        direct_identity = _read_fixture_identity(direct_receipt)
        descendant = _read_fixture_identity(descendant_receipt)
        assert direct_identity is not None
        assert descendant is not None
        assert direct_identity[0] == direct_process.pid
        assert direct_identity[1] == direct_identity[0]
        assert direct_identity[1] != wrapper_pgrp
        assert direct_identity[2] != wrapper_sid
        assert not aggregate_receipt.exists()

        os.kill(direct_process.pid, signal.SIGTERM)
        assert direct_process.wait(timeout=3.0) == 0
        assert _fixture_process_is_running(descendant[0])
        direct_receipt.unlink()
        assert _read_fixture_identity(direct_receipt) is None
    finally:
        _cleanup_fixture_processes(
            direct_process,
            (direct_receipt, descendant_receipt),
            wrapper_pgrp=wrapper_pgrp,
            wrapper_sid=wrapper_sid,
        )

    assert descendant is not None
    assert not _fixture_process_is_running(descendant[0])


@pytest.mark.skipif(
    not _POSIX_PROCESS_GROUPS,
    reason="requires POSIX process-group APIs",
)
def test_provider_descendant_fixture_cleanup_reaps_owned_direct_before_receipts(
    tmp_path: Path,
) -> None:
    fixture_script = tmp_path / "provider_fixture.py"
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    _write_provider_fixture(fixture_script)
    direct_receipt = state_dir / "direct-ready.json"
    descendant_receipt = state_dir / "descendant-ready.json"
    wrapper_pgrp = os.getpgrp()
    wrapper_sid = os.getsid(0)
    direct_process: subprocess.Popen[str] | None = None
    descendant: tuple[int, int, int] | None = None

    try:
        direct_process = subprocess.Popen(
            [
                sys.executable,
                str(fixture_script),
                "direct",
                str(state_dir),
                "omit-aggregate",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        _wait_for_fixture_path(direct_receipt, 3.0)
        _wait_for_fixture_path(descendant_receipt, 3.0)
        descendant = _read_fixture_identity(descendant_receipt)
        assert descendant is not None
        assert direct_process.poll() is None

        _cleanup_fixture_processes(
            direct_process,
            (direct_receipt, descendant_receipt),
            wrapper_pgrp=wrapper_pgrp,
            wrapper_sid=wrapper_sid,
        )
    finally:
        _cleanup_fixture_processes(
            direct_process,
            (direct_receipt, descendant_receipt),
            wrapper_pgrp=wrapper_pgrp,
            wrapper_sid=wrapper_sid,
        )

    assert descendant is not None
    assert not _fixture_process_is_running(descendant[0])


@pytest.mark.skipif(
    not _POSIX_PROCESS_GROUPS or not hasattr(os, "fork"),
    reason="requires POSIX process-group APIs and fork",
)
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


@pytest.mark.parametrize("stdin_text", [None, "input"])
def test_run_once_interrupt_terminates_provider_process_group(
    monkeypatch, stdin_text
) -> None:
    interruption = KeyboardInterrupt("cancel invalid round")
    signals: list[tuple[int, int]] = []
    getpgid_calls: list[int] = []

    class InterruptingProcess:
        pid = 4242
        stdin = io.TextIOWrapper(io.BytesIO()) if stdin_text is not None else None
        stdout = io.StringIO("")
        stderr = io.StringIO("")
        returncode = None

        def __init__(self) -> None:
            self.wait_calls: list[int] = []

        def wait(self, timeout: int) -> int:
            self.wait_calls.append(timeout)
            if len(self.wait_calls) == 1:
                raise interruption
            self.returncode = -signal.SIGTERM
            return self.returncode

    process = InterruptingProcess()
    monkeypatch.setattr(subprocess, "Popen", lambda *_a, **_k: process)
    monkeypatch.setattr(
        os,
        "getpgid",
        lambda pid: getpgid_calls.append(pid) or pid,
    )
    monkeypatch.setattr(os, "getpgrp", lambda: 7)
    monkeypatch.setattr(os, "killpg", lambda pgid, sig: signals.append((pgid, sig)))

    with pytest.raises(KeyboardInterrupt) as caught:
        _common._run_once("claude", ["claude", "-p", "review"], None, 60,
                          stdin_text=stdin_text)

    assert caught.value is interruption
    assert getpgid_calls == [process.pid]
    assert signals == [
        (process.pid, signal.SIGTERM),
        (process.pid, 0),
        (process.pid, signal.SIGKILL),
    ]
    assert process.wait_calls == [60, 5, 5]


def test_run_once_uses_direct_fallback_for_an_unsafe_child_process_group(
    monkeypatch,
) -> None:
    group_signals: list[tuple[int, int]] = []

    class TimeoutProcess:
        pid = 4242
        stdin = None
        stdout = io.StringIO("")
        stderr = io.StringIO("")
        returncode = None

        def __init__(self) -> None:
            self.terminate_calls = 0
            self.kill_calls = 0
            self.wait_calls: list[int] = []

        def terminate(self) -> None:
            self.terminate_calls += 1

        def kill(self) -> None:
            self.kill_calls += 1

        def wait(self, timeout: int) -> int:
            self.wait_calls.append(timeout)
            if len(self.wait_calls) == 1:
                raise subprocess.TimeoutExpired("fixture", timeout)
            self.returncode = -signal.SIGTERM
            return self.returncode

    process = TimeoutProcess()
    monkeypatch.setattr(subprocess, "Popen", lambda *_a, **_k: process)
    monkeypatch.setattr(os, "getpgid", lambda _pid: process.pid)
    monkeypatch.setattr(os, "getpgrp", lambda: process.pid)
    monkeypatch.setattr(
        os,
        "killpg",
        lambda pgid, sig: group_signals.append((pgid, sig)),
    )

    result = _common._run_once("claude", ["claude", "-p", "review"], None, 60)

    assert result.exit_code == _common.EXIT_TIMEOUT
    assert group_signals == []
    assert process.terminate_calls == 1
    assert process.kill_calls == 0
    assert process.wait_calls == [60, 5, 5]


def test_terminate_provider_process_group_fallback_kills_unreaped_child(
    monkeypatch,
) -> None:
    group_signals: list[tuple[int, int]] = []

    class UnreapedProcess:
        pid = 4242

        def __init__(self) -> None:
            self.terminate_calls = 0
            self.kill_calls = 0
            self.wait_calls: list[int] = []

        def terminate(self) -> None:
            self.terminate_calls += 1

        def kill(self) -> None:
            self.kill_calls += 1

        def wait(self, timeout: int) -> int:
            self.wait_calls.append(timeout)
            if len(self.wait_calls) == 1:
                raise subprocess.TimeoutExpired("fixture", timeout)
            return -signal.SIGKILL

    process = UnreapedProcess()
    monkeypatch.setattr(
        os,
        "killpg",
        lambda pgid, sig: group_signals.append((pgid, sig)),
    )

    _common._terminate_provider_process_group(process, "fixture", None)

    assert group_signals == []
    assert process.terminate_calls == 1
    assert process.kill_calls == 1
    assert process.wait_calls == [5, 5]


def test_packaged_leg_verdict_loads_under_hardened_wrapper(monkeypatch) -> None:
    monkeypatch.setenv("TRIAD_WRAPPER_HARDENED", "1")
    monkeypatch.delenv("TRIAD_ALLOW_PYDANTIC_IMPORT", raising=False)

    schema = _common.load_pydantic_class("verdict_schema:LegVerdict")

    assert schema.__name__ == "LegVerdict"
    assert "batch_id" not in schema.model_fields


def test_packaged_leg_verdict_loads_in_a_clean_python_process() -> None:
    program = (
        "import sys; "
        f"sys.path.insert(0, {str(BIN)!r}); "
        "import _common; "
        "cls = _common.load_pydantic_class('verdict_schema:LegVerdict'); "
        "print(cls.model_json_schema()['title'])"
    )
    result = subprocess.run(
        [sys.executable, "-c", program],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "LegVerdict"


def test_hardened_wrapper_requires_opt_in_for_arbitrary_schema(monkeypatch) -> None:
    monkeypatch.setenv("TRIAD_WRAPPER_HARDENED", "1")
    monkeypatch.delenv("TRIAD_ALLOW_PYDANTIC_IMPORT", raising=False)

    with pytest.raises(PermissionError, match="trusted schema modules"):
        _common.load_pydantic_class("tests.fake:Schema")


@pytest.mark.parametrize(
    "module",
    [claude_wrapper, gemini_wrapper],
)
def test_provider_wrappers_reject_retired_review_and_permission_flags(
    module, monkeypatch
) -> None:
    modules = (antigravity_wrapper, module) if module is claude_wrapper else (module,)
    for current_module in modules:
        for retired in (
            "--sandbox",
            "--sealed-packet-root",
            "--expected-packet-sha256",
            "--dangerously-skip-permissions",
        ):
            monkeypatch.setattr(
                sys,
                "argv",
                [current_module.__file__, "--prompt", "x", retired, "x"],
            )
            with pytest.raises(SystemExit) as caught:
                current_module.main()
            assert caught.value.code == 2


def test_claude_route_forwards_model_effort_and_native_json(
    monkeypatch, capsys
) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude"
    )
    monkeypatch.setattr(
        claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )

    def fake_driver(_cli, builder, prompt, **kwargs):
        captured["cmd"] = builder(prompt)
        captured["kwargs"] = kwargs
        return _ok()

    monkeypatch.setattr(claude_wrapper, "run_cli_with_retry", fake_driver)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--model",
            "opus",
            "--effort",
            "xhigh",
        ],
    )

    assert claude_wrapper.main() == 0
    assert capsys.readouterr().out == "ok\n"
    assert captured["cmd"] == [
        "/opt/bin/claude",
        "--print",
        "--input-format",
        "text",
        "--output-format",
        "json",
        "--model",
        "opus",
        "--effort",
        "xhigh",
    ]
    assert captured["kwargs"]["prompt_via_stdin"] is True


def test_claude_structured_route_uses_native_schema_once(monkeypatch, capsys) -> None:
    calls: list[list[str]] = []
    pruned: list[str] = []
    monkeypatch.setattr(
        claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude"
    )
    monkeypatch.setattr(
        claude_wrapper, "load_pydantic_class", lambda _spec: _StructuredAnswer
    )
    monkeypatch.setattr(
        claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", pruned.append)
    monkeypatch.setattr(
        claude_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: (_ for _ in ()).throw(
            AssertionError("generic retry path used")
        ),
    )

    def fake_once(_cli, cmd, _cwd, _timeout, *, classify_and_log, stdin_text=None):
        calls.append(cmd)
        assert stdin_text == "review"
        assert "review" not in cmd
        assert cmd[1:6] == ["--print", "--input-format", "text", "--output-format", "json"]
        assert classify_and_log is False
        return _common.RunResult(
            exit_code=0,
            stdout='{"is_error":false,"result":"{\\"ok\\":true}","structured_output":{"ok":true}}',
            stderr="",
            elapsed_s=0.2,
            vendor_exit_code=0,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--model",
            "opus",
            "--effort",
            "xhigh",
            "--pydantic",
            "fake:Answer",
        ],
    )

    assert claude_wrapper.main() == 0
    assert capsys.readouterr().out == '{"ok": true}\n'
    assert len(calls) == 1
    assert "--tools" not in calls[0]
    for forbidden in (
        "--safe-mode",
        "--strict-mcp-config",
        "--mcp-config",
        "--allowedTools",
        "--disallowedTools",
    ):
        assert not any(
            arg == forbidden or arg.startswith(f"{forbidden}=") for arg in calls[0]
        )
    assert "--json-schema" in calls[0]
    assert pruned == ["claude"]


def test_claude_formal_leg_binds_native_schema_and_local_admission(
    monkeypatch, capsys
) -> None:
    calls: list[list[str]] = []
    payload = {
        "review_id": "review-r1",
        "family": "claude",
        "content_digest": "a" * 64,
        "verdict": "SAFE",
        "criteria_checked": ["correctness"],
        "findings": [],
        "affected_surfaces_inspected": ["src/parser.py"],
        "open_questions": [],
    }
    monkeypatch.setattr(
        claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude"
    )
    monkeypatch.setattr(claude_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, _cwd, _timeout, *, classify_and_log, stdin_text=None):
        calls.append(cmd)
        assert stdin_text == "review"
        assert "review" not in cmd
        assert cmd[1:6] == ["--print", "--input-format", "text", "--output-format", "json"]
        assert _timeout == 1200
        schema = json.loads(cmd[cmd.index("--json-schema") + 1])
        properties = schema["properties"]
        assert properties["review_id"]["const"] == "review-r1"
        assert properties["family"]["const"] == "claude"
        assert properties["content_digest"]["const"] == "a" * 64
        return _common.RunResult(
            exit_code=0,
            stdout=json.dumps(
                {
                    "is_error": False,
                    "result": json.dumps(payload),
                    "structured_output": payload,
                }
            ),
            stderr="",
            elapsed_s=0.2,
            vendor_exit_code=0,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--model",
            "opus",
            "--effort",
            "xhigh",
            "--timeout",
            "1200",
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "claude",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert claude_wrapper.main() == 0
    assert json.loads(capsys.readouterr().out) == payload
    assert len(calls) == 1
    for option in ("--model", "--effort", "--permission-mode", "--json-schema"):
        assert calls[0].count(option) == 1
    assert calls[0][calls[0].index("--model") + 1] == "opus"
    assert calls[0][calls[0].index("--effort") + 1] == "xhigh"
    assert calls[0][calls[0].index("--permission-mode") + 1] == "plan"
    assert "--fallback-model" not in calls[0]


def test_claude_formal_leg_rejects_locally_valid_binding_mismatch(
    monkeypatch, capsys
) -> None:
    payload = {
        "review_id": "review-r1",
        "family": "claude",
        "content_digest": "b" * 64,
        "verdict": "SAFE",
        "criteria_checked": ["correctness"],
        "findings": [],
        "affected_surfaces_inspected": ["src/parser.py"],
        "open_questions": [],
    }
    monkeypatch.setattr(
        claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude"
    )
    monkeypatch.setattr(claude_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(
        _common,
        "_run_once",
        lambda *_a, **_k: _common.RunResult(
            exit_code=0,
            stdout=json.dumps(
                {
                    "is_error": False,
                    "result": json.dumps(payload),
                    "structured_output": payload,
                }
            ),
            stderr="",
            elapsed_s=0.2,
            vendor_exit_code=0,
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--model",
            "opus",
            "--effort",
            "xhigh",
            "--timeout",
            "1200",
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "claude",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert claude_wrapper.main() == _common.EXIT_SCHEMA_FAIL
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    "route_args",
    (
        ("--effort", "xhigh", "--timeout", "1200"),
        ("--model", "sonnet", "--effort", "xhigh", "--timeout", "1200"),
        ("--model", "opus", "--timeout", "1200"),
        ("--model", "opus", "--effort", "high", "--timeout", "1200"),
        ("--model", "opus", "--effort", "xhigh"),
        ("--model", "opus", "--effort", "xhigh", "--timeout", "1199"),
        ("--model", "opus", "--effort", "xhigh", "--timeout", "1201"),
        (
            "--model",
            "opus",
            "--effort",
            "xhigh",
            "--timeout",
            "1200",
            "--fallback-model",
            "sonnet",
        ),
        (
            "--model",
            "opus",
            "--effort",
            "xhigh",
            "--timeout",
            "1200",
            "--fallback-model",
            "",
        ),
    ),
    ids=(
        "missing-model",
        "wrong-model",
        "missing-effort",
        "wrong-effort",
        "default-timeout",
        "timeout-below",
        "timeout-above",
        "fallback-model",
        "empty-fallback-model",
    ),
)
def test_claude_formal_leg_rejects_unpinned_route_before_provider_resolution(
    monkeypatch, capsys, route_args
) -> None:
    monkeypatch.setattr(claude_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        claude_wrapper,
        "require_binary",
        lambda _name: pytest.fail("provider resolved"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "claude",
            "--expected-content-digest",
            "a" * 64,
            *route_args,
        ],
    )

    assert claude_wrapper.main() == _common.EXIT_ARG_ERROR
    assert (
        "formal Claude route requires --model opus --effort xhigh --timeout 1200 "
        "and forbids --fallback-model" in capsys.readouterr().err
    )


@pytest.mark.parametrize(
    ("binding_args", "expected_error"),
    (
        (
            (),
            "formal verdict schema requires all formal verdict bindings",
        ),
        (
            ("--expected-review-id", "review-r1"),
            "formal verdict schema requires all formal verdict bindings",
        ),
        (
            (
                "--expected-review-id",
                "review-r1",
                "--expected-family",
                "claude",
                "--expected-content-digest",
                "a" * 64,
                "--pydantic",
                f"{__name__}:_StructuredAnswer",
            ),
            "formal verdict bindings require --pydantic verdict_schema:LegVerdict",
        ),
        (
            (
                "--expected-review-id",
                "invalid/review",
                "--expected-family",
                "claude",
                "--expected-content-digest",
                "a" * 64,
            ),
            "expected review ID has invalid syntax",
        ),
        (
            (
                "--expected-review-id",
                "review-r1",
                "--expected-family",
                "claude",
                "--expected-content-digest",
                "A" * 64,
            ),
            "expected content digest must be 64 lowercase hexadecimal characters",
        ),
    ),
)
def test_claude_formal_leg_rejects_invalid_bindings_before_provider_resolution(
    monkeypatch, capsys, binding_args, expected_error
) -> None:
    monkeypatch.setattr(
        claude_wrapper,
        "require_binary",
        lambda _name: (_ for _ in ()).throw(AssertionError("provider resolved")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "verdict_schema:LegVerdict",
            *binding_args,
        ],
    )

    assert claude_wrapper.main() == _common.EXIT_ARG_ERROR
    assert expected_error in capsys.readouterr().err


def test_claude_wrapper_rejects_removed_formal_read_tools_flag(
    monkeypatch, capsys
) -> None:
    monkeypatch.setattr(
        claude_wrapper,
        "require_binary",
        lambda _name: (_ for _ in ()).throw(AssertionError("provider resolved")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "fake:Answer",
            "--formal-read-tools",
        ],
    )

    with pytest.raises(SystemExit) as exc:
        claude_wrapper.main()

    assert exc.value.code == 2
    assert "unrecognized arguments: --formal-read-tools" in capsys.readouterr().err


def test_claude_structured_route_rejects_result_text_fallback(
    monkeypatch, capsys
) -> None:
    calls = 0
    monkeypatch.setattr(
        claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude"
    )
    monkeypatch.setattr(
        claude_wrapper, "load_pydantic_class", lambda _spec: _StructuredAnswer
    )
    monkeypatch.setattr(
        claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, _cmd, _cwd, _timeout, *, classify_and_log, stdin_text=None):
        nonlocal calls
        calls += 1
        assert stdin_text == "review"
        assert classify_and_log is False
        return _common.RunResult(
            exit_code=0,
            stdout='{"is_error":false,"result":"{\\"ok\\":true}"}',
            stderr="",
            elapsed_s=0.2,
            vendor_exit_code=0,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "fake:Answer",
        ],
    )

    assert claude_wrapper.main() == _common.EXIT_SCHEMA_FAIL
    assert capsys.readouterr().out == ""
    assert calls == 1


def test_claude_rejects_repair_mode_on_structured_route(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        claude_wrapper, "load_pydantic_class", lambda _spec: _StructuredAnswer
    )
    monkeypatch.setattr(
        claude_wrapper,
        "require_binary",
        lambda _name: (_ for _ in ()).throw(AssertionError("provider resolved")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "fake:Answer",
            "--repair-mode",
        ],
    )

    assert claude_wrapper.main() == _common.EXIT_ARG_ERROR
    assert capsys.readouterr().out == ""


def test_gemini_route_keeps_native_json_without_review_protocol(
    monkeypatch, capsys
) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        gemini_wrapper, "require_binary", lambda _name: "/opt/bin/gemini"
    )
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )

    def fake_driver(_cli, builder, prompt, **kwargs):
        captured["cmd"] = builder(prompt)
        return _ok()

    monkeypatch.setattr(gemini_wrapper, "run_cli_with_retry", fake_driver)
    monkeypatch.setattr(
        sys,
        "argv",
        ["gemini_wrapper.py", "--prompt", "review", "--model", "gemini-enterprise"],
    )

    assert gemini_wrapper.main() == 0
    assert capsys.readouterr().out == "ok\n"
    assert captured["cmd"] == [
        "/opt/bin/gemini",
        "-p",
        "review",
        "--output-format",
        "json",
        "-m",
        "gemini-enterprise",
    ]


def test_gemini_formal_leg_uses_plan_policy_scrubbed_oauth_and_bound_result(
    monkeypatch, capsys, tmp_path
) -> None:
    captured: dict[str, object] = {}
    payload = {
        "review_id": "review-r1",
        "family": "google",
        "content_digest": "a" * 64,
        "verdict": "SAFE",
        "criteria_checked": ["correctness"],
        "findings": [],
        "affected_surfaces_inspected": ["src/parser.py"],
        "open_questions": [],
    }
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.1-pro")
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )

    def fake_driver(_cli, builder, prompt, **kwargs):
        captured["cmd"] = builder(prompt)
        captured["kwargs"] = kwargs
        return _common.RunResult(
            exit_code=0,
            stdout="",
            stderr="",
            elapsed_s=0.1,
            final_answer=json.dumps(payload),
            validated=payload,
            vendor_exit_code=0,
        )

    monkeypatch.setattr(gemini_wrapper, "run_cli_with_retry", fake_driver)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
            "--timeout",
            "600",
        ],
    )

    assert gemini_wrapper.main() == 0
    assert json.loads(capsys.readouterr().out) == payload
    cmd = captured["cmd"]
    assert cmd[0] == str(selected)
    assert cmd[cmd.index("--approval-mode") + 1] == "plan"
    policy = Path(cmd[cmd.index("--policy") + 1])
    assert policy == ROOT / "bin" / "policies" / "gemini-formal-readonly.toml"
    assert policy.is_file()
    assert cmd.count("-m") == 1
    assert cmd[cmd.index("-m") + 1] == "auto"
    kwargs = captured["kwargs"]
    assert kwargs["timeout"] == 600
    assert kwargs["single_provider_call"] is True
    assert set(kwargs["remove_env"]) == {
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_GENAI_USE_VERTEXAI",
        "GOOGLE_GEMINI_BASE_URL",
        "GOOGLE_VERTEX_BASE_URL",
        "CLOUD_SHELL",
        "GEMINI_CLI_USE_COMPUTE_ADC",
        "GEMINI_MODEL",
    }


def test_gemini_formal_leg_persists_literal_unexposed_runtime_identity(
    monkeypatch, capsys, tmp_path
) -> None:
    payload = {
        "review_id": "review-r1",
        "family": "google",
        "content_digest": "a" * 64,
        "verdict": "SAFE",
        "criteria_checked": ["correctness"],
        "findings": [],
        "affected_surfaces_inspected": ["src/parser.py"],
        "open_questions": [],
    }
    provider_calls = 0
    persisted: list[_common.RunResult] = []
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        gemini_wrapper,
        "persist_result_artifacts",
        lambda _cli, _argv, _cmd, _prompt, result, **_kwargs: persisted.append(result),
    )

    def fake_driver(_cli, _builder, _prompt, **_kwargs):
        nonlocal provider_calls
        provider_calls += 1
        return _common.RunResult(
            exit_code=0,
            stdout="",
            stderr="",
            elapsed_s=0.1,
            final_answer=json.dumps(payload),
            validated=payload,
            vendor_exit_code=0,
        )

    monkeypatch.setattr(gemini_wrapper, "run_cli_with_retry", fake_driver)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == 0
    assert json.loads(capsys.readouterr().out) == payload
    assert provider_calls == 1
    assert len(persisted) == 1
    assert persisted[0].runtime_identity == "unexposed"


def test_gemini_formal_leg_rejects_binding_mismatch_without_stdout(
    monkeypatch, capsys, tmp_path
) -> None:
    payload = {
        "review_id": "review-r1",
        "family": "google",
        "content_digest": "b" * 64,
        "verdict": "SAFE",
        "criteria_checked": ["correctness"],
        "findings": [],
        "affected_surfaces_inspected": ["src/parser.py"],
        "open_questions": [],
    }
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(
        gemini_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: _common.RunResult(
            exit_code=0,
            stdout="",
            stderr="",
            elapsed_s=0.1,
            final_answer=json.dumps(payload),
            validated=payload,
            vendor_exit_code=0,
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema.LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_SCHEMA_FAIL
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    "binding_args",
    (
        (),
        ("--expected-review-id", "review-r1"),
        (
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
            "--pydantic",
            f"{__name__}:_StructuredAnswer",
        ),
        (
            "--expected-review-id",
            "invalid/review",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ),
        (
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "A" * 64,
        ),
        (
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
            "--timeout",
            "0",
        ),
        (
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
            "--model",
            "gemini-3.1-pro",
        ),
    ),
)
def test_gemini_formal_leg_rejects_invalid_bindings_before_provider_resolution(
    monkeypatch, binding_args
) -> None:
    monkeypatch.setattr(
        gemini_wrapper,
        "require_binary",
        lambda _name: (_ for _ in ()).throw(AssertionError("provider resolved")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "verdict_schema:LegVerdict",
            *binding_args,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR


@pytest.mark.parametrize("timeout", ("599", "601"))
def test_gemini_formal_leg_rejects_non_600_timeout_before_provider_resolution(
    monkeypatch, capsys, tmp_path, timeout
) -> None:
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(
        tmp_path, selector_receipt, selected
    )
    monkeypatch.setattr(
        gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict
    )
    monkeypatch.setattr(
        gemini_wrapper.subprocess,
        "run",
        lambda *_a, **_k: pytest.fail("provider resolved"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--timeout",
            timeout,
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert (
        "formal Gemini review requires --timeout 600 and CLI Auto model routing"
        in capsys.readouterr().err
    )


def test_gemini_preflight_reports_schema_control_before_dispatch_timeout(
    monkeypatch, capsys
) -> None:
    monkeypatch.setattr(
        gemini_wrapper,
        "require_binary",
        lambda _name: pytest.fail("provider resolved"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "preflight",
            "--preflight-only",
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--timeout",
            "599",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert (
        "Gemini formal preflight does not accept model, schema, or repair controls"
        in capsys.readouterr().err
    )


def test_gemini_formal_preflight_is_provider_free_and_scrubs_competing_auth(
    monkeypatch, capsys, tmp_path
) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []
    competing_auth = (
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_GENAI_USE_VERTEXAI",
        "GOOGLE_GEMINI_BASE_URL",
        "GOOGLE_VERTEX_BASE_URL",
        "CLOUD_SHELL",
        "GEMINI_CLI_USE_COMPUTE_ADC",
        "GEMINI_MODEL",
    )
    for name in competing_auth:
        monkeypatch.setenv(name, "must-not-reach-child")
    selector_receipt, _prompt, selected = _google_selector_fixture(tmp_path)
    monkeypatch.setattr(
        gemini_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("provider started")),
    )

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=_formal_gemini_help(),
            stderr="",
        )

    monkeypatch.setattr(gemini_wrapper.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert gemini_wrapper.main() == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["provider_started"] is False
    assert receipt["route"] == "gemini"
    assert receipt["executable"] == str(selected)
    assert receipt["review_id"] == "review-r1"
    assert (
        receipt["google_selector_receipt_sha256"]
        == hashlib.sha256(selector_receipt.read_bytes()).hexdigest()
    )
    assert receipt["requested_approval_mode"] == "plan"
    assert receipt["effective_approval_mode"] == "unexposed"
    assert receipt["model"] == "auto"
    assert receipt["read_only_enforcement"] == ("packaged-mode-independent-policy")
    assert "approval_mode" not in receipt
    assert Path(receipt["policy"]) == (
        ROOT / "bin" / "policies" / "gemini-formal-readonly.toml"
    )
    assert len(calls) == 1
    cmd, kwargs = calls[0]
    assert cmd == [str(selected), "--help"]
    child_env = kwargs["env"]
    for name in competing_auth:
        assert name not in child_env


def test_gemini_formal_preflight_rejects_unbound_help_tokens(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, _prompt, _selected = _google_selector_fixture(tmp_path)

    def fake_run(cmd, **_kwargs):
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=(
                "--approval-mode supports only default\n"
                "plan is mentioned in unrelated prose\n"
                "--policy was removed and accepts no path\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(gemini_wrapper.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "did not prove Plan Mode, policy, and Auto model support" in (
        capsys.readouterr().err
    )


def test_gemini_formal_preflight_requires_explicit_auto_model_surface(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, _prompt, _selected = _google_selector_fixture(tmp_path)

    def fake_run(cmd, **_kwargs):
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=(
                "  --approval-mode  Set the approval mode  [string] "
                '[choices: "default", "auto_edit", "yolo", "plan"]\n'
                "  --policy  Additional policy files or directories to load  [array]\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(gemini_wrapper.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "did not prove Plan Mode, policy, and Auto model support" in (
        capsys.readouterr().err
    )


def test_gemini_formal_preflight_honors_required_receipt_pin_over_path(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, _prompt, selected = _google_selector_fixture(tmp_path)
    shadow = tmp_path / "shadow" / "gemini"
    for executable in (shadow,):
        executable.parent.mkdir()
        executable.write_text("#!/bin/sh\nexit 91\n", encoding="utf-8")
        executable.chmod(0o755)
    calls: list[list[str]] = []

    def fake_run(cmd, **_kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=_formal_gemini_help(),
            stderr="",
        )

    monkeypatch.setenv("PATH", str(shadow.parent))
    monkeypatch.setenv("TRIAD_REQUIRE_PINNED_VENDOR", "1")
    monkeypatch.setenv("TRIAD_GEMINI_BIN", str(shadow))
    monkeypatch.setattr(gemini_wrapper.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert gemini_wrapper.main() == 0
    assert json.loads(capsys.readouterr().out)["executable"] == str(selected)
    assert calls == [[str(selected), "--help"]]


def test_gemini_formal_rejects_wrong_route_receipt_before_preflight(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, _prompt, _selected = _google_selector_fixture(
        tmp_path, route="agy"
    )
    monkeypatch.setattr(
        gemini_wrapper.subprocess,
        "run",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("preflight started")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "selector receipt route mismatch" in capsys.readouterr().err


def test_gemini_formal_preflight_rejects_foreign_review_before_help_probe(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, _prompt, _selected = _google_selector_fixture(
        tmp_path, review_id="foreign-r1"
    )
    monkeypatch.setattr(
        gemini_wrapper.subprocess,
        "run",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("help probed")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "selector receipt review ID mismatch" in capsys.readouterr().err


def test_gemini_formal_rejects_preflight_selector_mismatch_before_provider(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    record = json.loads(preflight_receipt.read_text(encoding="ascii"))
    record["google_selector_receipt_sha256"] = "0" * 64
    preflight_receipt.write_bytes(_canonical_json_bytes(record))
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        gemini_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("provider started")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "Google preflight receipt selector mismatch" in capsys.readouterr().err


def test_gemini_formal_rejects_prompt_receipt_mismatch_before_provider(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    mismatched_prompt = prompt.replace(str(selected), f"{selected}-other", 1)
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        gemini_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("provider started")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            mismatched_prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "formal prompt selector binding mismatch" in capsys.readouterr().err


def test_gemini_formal_rejects_non_google_prompt_before_provider(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, prompt, selected = _google_selector_fixture(
        tmp_path, family="codex"
    )
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        gemini_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("provider started")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "formal prompt selector binding mismatch" in capsys.readouterr().err


def test_gemini_formal_policy_rejects_an_additional_allow_rule(tmp_path) -> None:
    policy = tmp_path / "gemini-formal-readonly.toml"
    policy.write_text(
        gemini_wrapper._formal_policy_path().read_text(encoding="utf-8")
        + "\n[[rule]]\n"
        + 'toolName = "run_shell_command"\n'
        + 'decision = "allow"\n'
        + "priority = 999\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="exact fail-closed rule set"):
        gemini_wrapper._validate_formal_policy(policy)


def test_gemini_formal_policy_rejects_mode_scoped_rules(tmp_path) -> None:
    policy = tmp_path / "gemini-formal-readonly.toml"
    policy.write_text(
        gemini_wrapper._formal_policy_path()
        .read_text(encoding="utf-8")
        .replace(
            "priority = 999",
            'priority = 999\nmodes = ["plan"]',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="exact fail-closed rule set"):
        gemini_wrapper._validate_formal_policy(policy)


def test_gemini_formal_verdict_route_does_not_make_schema_repair_call(
    monkeypatch, capsys, tmp_path
) -> None:
    calls: list[list[str]] = []
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, cwd, timeout, *, stdin_text=None, remove_env=()):
        calls.append(cmd)
        assert cwd is None
        assert timeout == 600
        assert stdin_text is None
        assert "GEMINI_API_KEY" in remove_env
        return _common.RunResult(
            exit_code=0,
            stdout='{"response":"{}"}',
            stderr="",
            elapsed_s=0.1,
            classification="ok",
            vendor_exit_code=0,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_SCHEMA_FAIL
    assert capsys.readouterr().out == ""
    assert len(calls) == 1


def test_gemini_formal_verdict_route_does_not_make_capacity_retry_call(
    monkeypatch, capsys, tmp_path
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setenv("TRIAD_SERVER_CAP_NO_BACKOFF", "1")
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, cwd, timeout, *, stdin_text=None, remove_env=()):
        calls.append(cmd)
        assert cwd is None
        assert timeout == 600
        assert stdin_text is None
        assert "GEMINI_API_KEY" in remove_env
        return _common.RunResult(
            exit_code=_common.EXIT_CLI_FAIL,
            stdout="",
            stderr="capacity exhausted",
            elapsed_s=0.1,
            classification="server-capacity",
            vendor_exit_code=1,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_RATE_GIVE_UP
    assert capsys.readouterr().out == ""
    assert len(calls) == 1


def test_gemini_dotted_packaged_verdict_route_does_not_make_capacity_retry_call(
    monkeypatch, capsys, tmp_path
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setenv("TRIAD_SERVER_CAP_NO_BACKOFF", "1")
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, cwd, timeout, *, stdin_text=None, remove_env=()):
        calls.append(cmd)
        assert cwd is None
        assert timeout == 600
        assert stdin_text is None
        assert "GEMINI_API_KEY" in remove_env
        return _common.RunResult(
            exit_code=_common.EXIT_CLI_FAIL,
            stdout="",
            stderr="capacity exhausted",
            elapsed_s=0.1,
            classification="server-capacity",
            vendor_exit_code=1,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema.LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_RATE_GIVE_UP
    assert capsys.readouterr().out == ""
    assert len(calls) == 1


def test_gemini_custom_schema_keeps_existing_schema_repair_call(
    monkeypatch, capsys
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(
        gemini_wrapper, "require_binary", lambda _name: "/opt/bin/gemini"
    )
    monkeypatch.setattr(
        gemini_wrapper, "load_pydantic_class", lambda _spec: _StructuredAnswer
    )
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, cwd, timeout, *, stdin_text=None):
        calls.append(cmd)
        assert cwd is None
        assert timeout == 600
        assert stdin_text is None
        return _common.RunResult(
            exit_code=0,
            stdout='{"response":"{}"}',
            stderr="",
            elapsed_s=0.1,
            classification="ok",
            vendor_exit_code=0,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "example:StructuredAnswer",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_SCHEMA_FAIL
    assert capsys.readouterr().out == ""
    assert len(calls) == 2
