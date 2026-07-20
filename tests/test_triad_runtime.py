import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import triad_runtime as runtime  # noqa: E402


def test_run_argv_preserves_hostile_value_without_shell(tmp_path: Path) -> None:
    script = tmp_path / "argv.py"
    script.write_text("import json,sys; print(json.dumps(sys.argv[1:]))\n")
    hostile = 'space "quote" \'single\' `tick` $(sub)\n한글 --dash ;|&'

    result = runtime.run_argv(
        [sys.executable, str(script), hostile], timeout_seconds=2
    )

    assert result.returncode == 0
    assert json.loads(result.stdout) == [hostile]


def test_setup_records_canonical_authorization_without_credentials(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    workspace = tmp_path / "work space"
    workspace.mkdir()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    rc = runtime.main(
        [
            "setup",
            "--workspace",
            str(workspace),
            "--authorize-external-review",
            "--approval-policy",
            "on-request",
        ]
    )

    state_path = next(
        (tmp_path / ".config" / "triad-codex-dispatch" / "setup").glob("*.json")
    )
    state = json.loads(state_path.read_text())
    assert rc == 0
    assert state == {
        "schema_version": 1,
        "workspace_root": str(workspace.resolve()),
        "external_review_authorized": True,
        "provider_routes": ["claude", "google"],
        "approval_policy": "on-request",
        "no_prompt": False,
        "required_environment_names": [
            "TRIAD_WRAPPER_ALLOWED_ROOTS",
            "TRIAD_WRAPPER_HARDENED",
            "TRIAD_CLAUDE_ENFORCE_SANDBOX",
        ],
    }
    assert "TOKEN" not in json.dumps(state)
    assert "SECRET" not in json.dumps(state)


def test_static_doctor_cannot_run_a_probe(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(runtime, "static_findings", lambda _workspace: [])
    monkeypatch.setattr(
        runtime,
        "run_argv",
        lambda *_args, **_kwargs: pytest.fail("probe executed"),
    )

    assert (
        runtime.doctor_main(
            argparse.Namespace(workspace=str(tmp_path), live=False, timeout=30, json=False)
        )
        == 0
    )


def test_no_prompt_requires_never_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    with pytest.raises(ValueError, match="no-prompt.*never"):
        runtime.main(
            [
                "setup",
                "--workspace",
                str(workspace),
                "--authorize-external-review",
                "--approval-policy",
                "on-request",
                "--no-prompt",
            ]
        )


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def test_run_argv_timeout_terminates_the_entire_process_group(tmp_path: Path) -> None:
    pid_file = tmp_path / "child.pid"
    wrapper = tmp_path / "wrapper.py"
    wrapper.write_text(
        "import subprocess, sys, time\n"
        "from pathlib import Path\n"
        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
        "Path(sys.argv[1]).write_text(str(child.pid))\n"
        "time.sleep(60)\n"
    )

    result = runtime.run_argv(
        [sys.executable, str(wrapper), str(pid_file)], timeout_seconds=1
    )

    assert result.timed_out is True
    child_pid = int(pid_file.read_text())
    deadline = time.monotonic() + 2
    while _pid_exists(child_pid) and time.monotonic() < deadline:
        time.sleep(0.02)
    assert not _pid_exists(child_pid), "timeout left a child process running"


@pytest.mark.parametrize("name", ["missing", "not-executable"])
def test_run_argv_returns_transport_for_unlaunchable_program(
    tmp_path: Path, name: str
) -> None:
    program = tmp_path / name
    if name == "not-executable":
        program.write_text("#!/bin/sh\nexit 0\n")

    result = runtime.run_argv([str(program)], timeout_seconds=1)

    assert result.returncode is None
    assert result.family == "transport"
    assert result.timed_out is False


def test_run_argv_timeout_tolerates_a_process_group_already_gone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class TimedOutProcess:
        pid = 123
        returncode = -15

        def __init__(self) -> None:
            self.calls = 0

        def communicate(self, *, timeout: int) -> tuple[str, str]:
            self.calls += 1
            if self.calls == 1:
                raise subprocess.TimeoutExpired(["probe"], timeout)
            return "", ""

    process = TimedOutProcess()
    monkeypatch.setattr(runtime.subprocess, "Popen", lambda *_args, **_kwargs: process)
    monkeypatch.setattr(
        runtime.os,
        "killpg",
        lambda *_args: (_ for _ in ()).throw(ProcessLookupError()),
    )

    result = runtime.run_argv(["probe"], timeout_seconds=1)

    assert result.timed_out is True
    assert result.family == "transport"
    assert result.returncode is None


@pytest.mark.parametrize("contents", [b"\xff", b"[]"])
def test_static_findings_rejects_invalid_or_non_object_setup_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, contents: bytes
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    state_path = runtime.setup_state_path(workspace.resolve())
    state_path.parent.mkdir(parents=True)
    state_path.write_bytes(contents)

    assert runtime.static_findings(workspace.resolve()) == ["setup state is unreadable"]


def test_setup_replace_failure_cleans_temporary_state_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    monkeypatch.setattr(
        runtime.os,
        "replace",
        lambda _source, _destination: (_ for _ in ()).throw(OSError("replace failed")),
    )

    with pytest.raises(OSError, match="replace failed"):
        runtime.main(
            [
                "setup",
                "--workspace",
                str(workspace),
                "--authorize-external-review",
                "--approval-policy",
                "never",
                "--no-prompt",
            ]
        )

    state_dir = tmp_path / ".config" / "triad-codex-dispatch" / "setup"
    assert list(state_dir.iterdir()) == []


def test_setup_rejects_relative_xdg_config_home_before_write(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", "relative-config")

    with pytest.raises(ValueError, match="XDG_CONFIG_HOME must be absolute"):
        runtime.main(
            [
                "setup",
                "--workspace",
                str(workspace),
                "--authorize-external-review",
                "--approval-policy",
                "on-request",
            ]
        )

    assert not (tmp_path / "relative-config").exists()
