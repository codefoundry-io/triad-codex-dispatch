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
    env = dict(os.environ, PATH=_fake_claude_on_path(tmp_path) + os.pathsep + os.environ["PATH"])
    # inject --fake-mode by appending to the prompt path is not possible; pass via env the fixture reads:
    env["FAKE_MODE"] = fake_mode
    return subprocess.run([sys.executable, str(ROOT / "bin/claude_wrapper.py"),
                           "--prompt", "hi", *extra],
                          capture_output=True, text=True, env=env)

def test_success_returns_answer(tmp_path):
    r = _run(tmp_path)
    assert r.returncode == 0
    assert "FAKE-OK" in r.stdout
    assert "[wrapper] claude ok" in r.stderr

def test_bypass_permissions_rejected():
    r = subprocess.run([sys.executable, str(ROOT / "bin/claude_wrapper.py"),
                        "--prompt", "hi", "--sandbox", "bypassPermissions"],
                       capture_output=True, text=True)
    assert r.returncode != 0
    assert "invalid choice" in r.stderr
