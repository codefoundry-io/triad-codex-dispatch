import os
import re
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _fake_agy_dir(tmp_path: Path) -> str:
    fixture = tmp_path / "fake_agy.py"
    fixture.write_text(
        "import os, re, sys\n"
        "open(os.environ['ARGV_FILE'], 'w', encoding='utf-8').write('\\n'.join(sys.argv[1:]))\n"
        "prompt = sys.argv[sys.argv.index('-p') + 1]\n"
        "marker = re.search(r'<<<([^>]+)>>>', prompt).group(1)\n"
        "print('FAKE-AGY-OK')\n"
        "print(f'<<<{marker}>>>')\n",
        encoding="utf-8",
    )
    shim = tmp_path / "agy"
    shim.write_text(f"#!/usr/bin/env bash\nexec python3 {fixture} \"$@\"\n", encoding="utf-8")
    shim.chmod(shim.stat().st_mode | stat.S_IEXEC)
    return str(tmp_path)


def _run(tmp_path: Path, *extra: str):
    argv_file = tmp_path / "argv.txt"
    env = dict(
        os.environ,
        PATH=_fake_agy_dir(tmp_path) + os.pathsep + os.environ["PATH"],
        ARGV_FILE=str(argv_file),
        AGY_SETTINGS_PATH=str(tmp_path / "settings.json"),
        AGY_NO_BACKOFF="1",
    )
    env.pop("TRIAD_WRAPPER_ALLOWED_ROOTS", None)
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "bin/antigravity_wrapper.py"),
            "--prompt",
            "hi",
            *extra,
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
    )
    argv = argv_file.read_text(encoding="utf-8") if argv_file.exists() else ""
    return result, argv


def test_workspace_write_cwd_sets_fresh_agy_project_and_add_dir(tmp_path):
    result, argv = _run(
        tmp_path,
        "--sandbox",
        "workspace-write",
        "--cwd",
        str(tmp_path),
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "FAKE-AGY-OK" in result.stdout
    assert "--new-project" in argv
    assert f"--add-dir\n{tmp_path}" in argv


def test_readonly_without_cwd_does_not_create_agy_project(tmp_path):
    result, argv = _run(tmp_path, "--sandbox", "read-only")

    assert result.returncode == 0, result.stderr + result.stdout
    assert "--new-project" not in argv
    assert "--add-dir" not in argv
