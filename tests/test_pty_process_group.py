from __future__ import annotations

import errno
import json
import os
import signal
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))

import _pty  # noqa: E402


def test_pty_eof_still_enforces_timeout_with_outer_watchdog(tmp_path: Path) -> None:
    child_pid_path = tmp_path / "child.pid"
    child_code = (
        "import os, sys, time\n"
        "with open(sys.argv[1], 'w', encoding='ascii') as handle:\n"
        "    handle.write(str(os.getpid()))\n"
        "for descriptor in (0, 1, 2):\n"
        "    os.close(descriptor)\n"
        "time.sleep(30)\n"
    )
    runner_code = (
        "import json, os, signal, sys\n"
        f"sys.path.insert(0, {str(BIN)!r})\n"
        "import _pty\n"
        "waitpid_calls = []\n"
        "real_waitpid = _pty.os.waitpid\n"
        "real_fork = _pty.pty.fork\n"
        "real_close = _pty.os.close\n"
        "fork_state = {'pid': None, 'master_fd': None, 'hup_sent': False}\n"
        "def observe_waitpid(pid, options):\n"
        "    result = real_waitpid(pid, options)\n"
        "    waitpid_calls.append((options, result[0]))\n"
        "    return result\n"
        "def observe_fork():\n"
        "    result = real_fork()\n"
        "    if result[0] != 0:\n"
        "        fork_state['pid'], fork_state['master_fd'] = result\n"
        "    return result\n"
        "def linux_like_close(descriptor):\n"
        "    reaped = any(waited > 0 for _options, waited in waitpid_calls)\n"
        "    if descriptor == fork_state['master_fd'] and not reaped:\n"
        "        try:\n"
        "            os.killpg(fork_state['pid'], signal.SIGHUP)\n"
        "            fork_state['hup_sent'] = True\n"
        "        except ProcessLookupError:\n"
        "            pass\n"
        "    return real_close(descriptor)\n"
        "_pty.os.waitpid = observe_waitpid\n"
        "_pty.pty.fork = observe_fork\n"
        "_pty.os.close = linux_like_close\n"
        f"child_code = {child_code!r}\n"
        "result = _pty.run_via_pty(\n"
        f"    [sys.executable, '-c', child_code, {str(child_pid_path)!r}],\n"
        "    timeout=0.2,\n"
        "    env=os.environ.copy(),\n"
        ")\n"
        "print(json.dumps({\n"
        "    'rc': result.rc,\n"
        "    'killed': result.killed,\n"
        "    'reaped': sum(1 for _options, waited in waitpid_calls if waited > 0),\n"
        "    'hup_sent': fork_state['hup_sent'],\n"
        "}))\n"
    )

    try:
        completed = subprocess.run(
            [sys.executable, "-c", runner_code],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired as exc:
        if child_pid_path.exists():
            child_pid = int(child_pid_path.read_text(encoding="ascii"))
            try:
                os.killpg(child_pid, signal.SIGKILL)
            except OSError as error:
                if error.errno != errno.ESRCH:
                    raise
        raise AssertionError("outer watchdog expired after PTY EOF") from exc

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["rc"] in {128 + signal.SIGTERM, 128 + signal.SIGKILL}
    assert payload["killed"] is True
    assert payload["reaped"] == 1
    assert payload["hup_sent"] is False


def test_killpg_uses_forkpty_pid_and_does_not_reap_during_escalation(
    monkeypatch,
) -> None:
    pid = 43210
    calls: list[tuple[int, int]] = []
    sent_kill = False

    def fake_killpg(pgid: int, sig: int) -> None:
        nonlocal sent_kill
        calls.append((pgid, sig))
        if sig == signal.SIGKILL:
            sent_kill = True
        elif sig == 0 and sent_kill:
            raise OSError(errno.ESRCH, "group is gone")

    monkeypatch.setattr(
        _pty.os,
        "getpgid",
        lambda _pid: (_ for _ in ()).throw(
            AssertionError("forkpty leader may already be a zombie")
        ),
    )
    monkeypatch.setattr(
        _pty.os,
        "waitpid",
        lambda *_args: (_ for _ in ()).throw(
            AssertionError("the caller must reap after group escalation")
        ),
    )
    monkeypatch.setattr(_pty.os, "killpg", fake_killpg)
    monkeypatch.setattr(_pty.time, "sleep", lambda _seconds: None)

    assert _pty._killpg(pid) is None
    assert all(pgid == pid for pgid, _sig in calls)
    delivered = [sig for _pgid, sig in calls if sig != 0]
    assert delivered == [signal.SIGTERM, signal.SIGKILL]
