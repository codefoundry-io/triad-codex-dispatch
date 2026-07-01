# tests/test_claude_wrapper.py
import os, subprocess, sys, shutil, stat, textwrap
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def _fake_claude_on_path(tmp_path):
    # a shim named `claude` that execs the fake fixture
    shim = tmp_path / "claude"
    shim.write_text(f'#!/usr/bin/env bash\nexec python3 {ROOT}/tests/fixtures/fake_claude.py "$@"\n')
    shim.chmod(shim.stat().st_mode | stat.S_IEXEC)
    return str(tmp_path)

def _run(tmp_path, *extra, fake_mode="success"):
    result, _argv = _run_with_argv(tmp_path, *extra, fake_mode=fake_mode)
    return result

def _run_with_argv(tmp_path, *extra, fake_mode="success"):
    argv_file = tmp_path / "argv.txt"
    env = dict(os.environ, PATH=_fake_claude_on_path(tmp_path) + os.pathsep + os.environ["PATH"])
    # inject --fake-mode by appending to the prompt path is not possible; pass via env the fixture reads:
    env["FAKE_MODE"] = fake_mode
    env["ARGV_FILE"] = str(argv_file)
    env["TRIAD_WRAPPER_ALLOWED_ROOTS"] = str(tmp_path)
    prompt_args = [] if any(str(arg).startswith("--prompt-file") for arg in extra) else ["--prompt", "hi"]
    result = subprocess.run([sys.executable, str(ROOT / "bin/claude_wrapper.py"),
                             *prompt_args, *extra],
                            capture_output=True, text=True, env=env)
    argv = argv_file.read_text(encoding="utf-8") if argv_file.exists() else ""
    return result, argv

def test_success_returns_answer(tmp_path):
    r = _run(tmp_path)
    assert r.returncode == 0
    assert "FAKE-OK" in r.stdout
    assert "[wrapper] claude ok" in r.stderr


def test_prompt_file_passes_file_body_to_vendor(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("file prompt body", encoding="utf-8")
    r, argv = _run_with_argv(tmp_path, "--prompt-file", str(prompt_file))
    assert r.returncode == 0
    assert "-p\nfile prompt body" in argv


def test_prompt_file_must_be_absolute(tmp_path):
    env = dict(os.environ, PATH=_fake_claude_on_path(tmp_path) + os.pathsep + os.environ["PATH"])
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "bin/claude_wrapper.py"),
            "--prompt-file",
            "relative-prompt.txt",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 3
    assert "--prompt-file must be an absolute path" in r.stderr


def test_prompt_file_requires_explicit_allowed_roots(tmp_path):
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("body", encoding="utf-8")
    env = dict(os.environ, PATH=_fake_claude_on_path(tmp_path) + os.pathsep + os.environ["PATH"])
    env.pop("TRIAD_WRAPPER_ALLOWED_ROOTS", None)
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "bin/claude_wrapper.py"),
            "--prompt-file",
            str(prompt_file),
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 3
    assert "TRIAD_WRAPPER_ALLOWED_ROOTS must be set" in r.stderr


def test_prompt_file_must_stay_under_allowed_runtime_root(tmp_path):
    outside = tmp_path / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    env = dict(
        os.environ,
        PATH=_fake_claude_on_path(tmp_path) + os.pathsep + os.environ["PATH"],
        TRIAD_WRAPPER_ALLOWED_ROOTS=str(allowed),
    )
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "bin/claude_wrapper.py"),
            "--prompt-file",
            str(outside),
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 3
    assert "--prompt-file must be under an allowed runtime root" in r.stderr


def test_cwd_must_stay_under_allowed_runtime_root(tmp_path):
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    env = dict(
        os.environ,
        PATH=_fake_claude_on_path(tmp_path) + os.pathsep + os.environ["PATH"],
        TRIAD_WRAPPER_ALLOWED_ROOTS=str(allowed),
    )
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "bin/claude_wrapper.py"),
            "--prompt",
            "hi",
            "--cwd",
            str(outside),
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 3
    assert "--cwd must be under an allowed runtime root" in r.stderr

def test_read_only_uses_dontask_read_allowlist(tmp_path):
    r, argv = _run_with_argv(tmp_path, "--sandbox", "read-only")
    assert r.returncode == 0
    assert "--permission-mode\ndontAsk" in argv
    assert "--allowedTools\nRead,Glob,Grep" in argv

def test_workspace_write_uses_accept_edits_without_readonly_allowlist(tmp_path):
    r, argv = _run_with_argv(tmp_path, "--sandbox", "workspace-write")
    assert r.returncode == 0
    assert "--permission-mode\nacceptEdits" in argv
    assert "--allowedTools" not in argv
    assert "Read,Glob,Grep" not in argv

def test_workspace_write_search_only_allows_web_tools(tmp_path):
    r, argv = _run_with_argv(tmp_path, "--sandbox", "workspace-write", "--search")
    assert r.returncode == 0
    assert "--permission-mode\nacceptEdits" in argv
    assert "--allowedTools\nWebSearch,WebFetch" in argv
    assert "Read,Glob,Grep" not in argv

def test_bypass_permissions_rejected():
    r = subprocess.run([sys.executable, str(ROOT / "bin/claude_wrapper.py"),
                        "--prompt", "hi", "--sandbox", "bypassPermissions"],
                       capture_output=True, text=True)
    assert r.returncode != 0
    assert "invalid choice" in r.stderr
