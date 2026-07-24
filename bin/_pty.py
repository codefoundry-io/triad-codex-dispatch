#!/usr/bin/env python3
"""Stdlib-pty runner for CLIs (agy) that drop stdout on a non-TTY stdout.

agy -p emits nothing and hangs when stdout is not a tty (GitHub
google-antigravity/antigravity-cli#76 — v1.0.15 fixed this on WINDOWS only;
still OPEN for macOS/Linux, both Triad targets, re-checked 2026-07-04 on
1.0.16). Driving it through a pty makes it believe it has a terminal. Retire
the pty ONLY when `agy --help` shows a JSON/plain output mode AND #76 is fixed
on macOS/Linux — a changelog "fixed #76" line alone is not sufficient. No
`script`/`pexpect` dependency (BSD vs util-linux `script` syntax differs —
would break artifact portability).
"""
from __future__ import annotations

import errno
import os
import pty
import select
import signal
import struct
import time
from dataclasses import dataclass

import _common


@dataclass
class PtyResult:
    output_bytes: bytes
    rc: int
    killed: bool


class PtyStartError(Exception):
    """Child setup failed before the vendor executable replaced the process."""

    def __init__(self, stage: str, error_number: int):
        self.stage = stage
        self.errno = error_number
        super().__init__(f"pty child start failed: stage={stage} errno={error_number}")


_START_STATUS = struct.Struct("!BI")
_START_STAGE_TO_CODE = {"chdir": 1, "exec": 2}
_START_CODE_TO_STAGE = {value: key for key, value in _START_STAGE_TO_CODE.items()}


def _report_start_error(fd: int, stage: str, exc: Exception) -> None:
    error_number = getattr(exc, "errno", None)
    if not isinstance(error_number, int) or error_number < 0:
        error_number = errno.EIO
    payload = _START_STATUS.pack(_START_STAGE_TO_CODE[stage], error_number)
    offset = 0
    while offset < len(payload):
        try:
            written = os.write(fd, payload[offset:])
        except InterruptedError:
            continue
        except OSError:
            break
        if written <= 0:
            break
        offset += written


def _read_start_error(fd: int, deadline: float) -> PtyStartError | None:
    payload = bytearray()
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("PTY child start handshake timed out")
        try:
            ready, _, _ = select.select([fd], [], [], min(remaining, 1.0))
        except InterruptedError:
            continue
        if not ready:
            continue
        try:
            chunk = os.read(fd, _START_STATUS.size - len(payload))
        except InterruptedError:
            continue
        if not chunk:
            break
        payload.extend(chunk)
        if len(payload) == _START_STATUS.size:
            break
    if not payload:
        return None
    if len(payload) != _START_STATUS.size:
        raise OSError(errno.EIO, "incomplete PTY child start status")
    stage_code, error_number = _START_STATUS.unpack(payload)
    stage = _START_CODE_TO_STAGE.get(stage_code)
    if stage is None:
        raise OSError(errno.EIO, "invalid PTY child start stage")
    return PtyStartError(stage, error_number)


def run_via_pty(cmd, cwd=None, timeout=600, env=None) -> PtyResult:
    """Run cmd under a pty, capture combined output, enforce timeout.

    EOF is handled cross-platform: macOS returns b"" on the master fd after the
    child closes; Linux raises OSError(EIO). The child runs in its own session
    (setsid via forkpty) so a timeout kills the whole subtree via killpg.

    This is a SEPARATE vendor-child spawn site from `_common._run_once` (Popen) —
    the agy vendor child execs here, not through Popen. For `env=None` (the agy
    wrapper's production call) it inherits the SAME scrubbed env as the Popen site
    via `_common.scrubbed_child_env()` (loader/interpreter injection vars dropped,
    I-2/I-3), so a poisoned parent env cannot reach the agy Node runtime. An
    explicit `env` is used as given (caller owns it).
    """
    full_env = _common.scrubbed_child_env() if env is None else dict(env)
    full_env.setdefault("TERM", "dumb")  # suppress TUI escapes
    deadline = time.monotonic() + timeout

    status_read_fd, status_write_fd = os.pipe()
    os.set_inheritable(status_write_fd, False)
    try:
        pid, master_fd = pty.fork()
    except BaseException:
        os.close(status_read_fd)
        os.close(status_write_fd)
        raise
    if pid == 0:  # child — own session courtesy of pty.fork()
        os.close(status_read_fd)
        try:
            if cwd:
                try:
                    os.chdir(cwd)
                except Exception as exc:
                    _report_start_error(status_write_fd, "chdir", exc)
                    os._exit(127)
            os.execvpe(cmd[0], list(cmd), full_env)
        except Exception as exc:
            _report_start_error(status_write_fd, "exec", exc)
            os._exit(127)

    os.close(status_write_fd)
    try:
        start_error = _read_start_error(status_read_fd, deadline)
    except BaseException:
        os.close(master_fd)
        _killpg(pid)
        _reap(pid)
        raise
    finally:
        os.close(status_read_fd)
    if start_error is not None:
        os.close(master_fd)
        _reap(pid)
        raise start_error

    chunks = bytearray()
    killed = False
    saw_eof = False
    rc = None
    try:
        try:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    killed = True
                    break
                r, _, _ = select.select([master_fd], [], [], min(remaining, 1.0))
                if master_fd in r:
                    try:
                        data = os.read(master_fd, 65536)
                    except OSError as e:
                        if e.errno == errno.EIO:  # Linux EOF
                            saw_eof = True
                            break
                        raise
                    if not data:  # macOS EOF
                        saw_eof = True
                        break
                    chunks.extend(data)
        finally:
            if saw_eof and not killed:
                rc = _reap_until(pid, deadline)
                if rc is None:
                    killed = True
            if killed:
                _killpg(pid)
            if rc is None:
                rc = _reap(pid)
    finally:
        os.close(master_fd)
    return PtyResult(bytes(chunks), rc, killed)


def _killpg(pid: int) -> None:
    """Signal the child's process GROUP down (SIGTERM, escalate to SIGKILL).

    ``pty.fork()`` creates a session whose process-group ID is the returned
    child PID. Use that stable ID directly: on macOS ``getpgid(pid)`` reports
    ESRCH once the leader is a zombie even while live descendants remain in
    its group. The caller deliberately reaps the leader only after this
    escalation, preventing the PID/PGID from being reused while we signal it.
    """
    pgid = pid
    for sig in (signal.SIGTERM, signal.SIGKILL):
        # Escalate only if the group still has at least one member.
        try:
            os.killpg(pgid, sig)
        except OSError as e:
            # kill(-pgid) raises ESRCH when no process remains in the group,
            # and EPERM when it could signal NO member — i.e. the pgid no
            # longer maps to a group we may signal (emptied, or reused by a
            # group we do not own). kill(-pgid) succeeds as long as it can
            # signal at least one member, so an EPERM here means there is
            # nothing left we can act on; stop escalating.
            #
            # The unreaped direct child keeps this PID/PGID reserved until the
            # caller finishes escalation. Anything other than ESRCH/EPERM is
            # unexpected — re-raise loudly.
            if e.errno not in (errno.ESRCH, errno.EPERM):
                raise
            break
        for _ in range(20):  # up to ~1s for the signal to land
            # Group-empty probe: kill(-pgid, 0) raises ESRCH when no process
            # remains, and EPERM when nothing remaining is signalable by us.
            # Either way there is nothing left for the SIGKILL escalation to
            # act on. Re-raise anything other than ESRCH/EPERM loudly.
            try:
                os.killpg(pgid, 0)
            except OSError as e:
                if e.errno not in (errno.ESRCH, errno.EPERM):
                    raise
                return None
            time.sleep(0.05)
    return None


def _status_to_rc(status: int) -> int:
    """Map one wait status to the subprocess-style return code contract."""
    if os.WIFEXITED(status):
        return os.WEXITSTATUS(status)
    if os.WIFSIGNALED(status):
        return 128 + os.WTERMSIG(status)
    return -1


def _reap_until(pid: int, deadline: float) -> int | None:
    """Poll until the child is reaped or the shared PTY deadline expires."""
    while True:
        try:
            waited, status = os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            return -1
        if waited == pid:
            return _status_to_rc(status)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        time.sleep(min(remaining, 0.05))


def _reap(pid: int) -> int:
    """Reap the direct child once after process-group escalation."""
    try:
        _, status = os.waitpid(pid, 0)
    except ChildProcessError:
        return -1
    return _status_to_rc(status)
