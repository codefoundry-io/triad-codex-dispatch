import os
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "bootstrap.sh"


def _fake_bin(tmp_path: Path, *names: str) -> Path:
    bin_dir = tmp_path / "fake-bin"
    bin_dir.mkdir()
    for name in names:
        path = bin_dir / name
        if name == "python3":
            path.write_text(
                f"#!/usr/bin/env bash\nexec {sys.executable} \"$@\"\n",
                encoding="utf-8",
            )
        else:
            path.write_text(f"#!/usr/bin/env bash\necho '{name} fake 1.0'\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return bin_dir


def _run_bootstrap(tmp_path: Path, fake_names=("codex", "claude", "gemini", "agy")):
    fake_bin = _fake_bin(tmp_path, *fake_names, "jq", "python3")
    launcher_bin = tmp_path / "launchers"
    launcher_bin.mkdir()
    python_bin = Path(sys.executable).parent
    env = {
        **os.environ,
        "HOME": str(tmp_path / "home"),
        "XDG_CONFIG_HOME": str(tmp_path / "xdg-config"),
        "PATH": (
            f"{fake_bin}{os.pathsep}{launcher_bin}{os.pathsep}{python_bin}"
            f"{os.pathsep}/usr/bin{os.pathsep}/bin{os.pathsep}/usr/sbin{os.pathsep}/sbin"
        ),
        "TRIAD_BOOTSTRAP_REPO_ROOT": str(ROOT),
        "TRIAD_BOOTSTRAP_BIN_DIR": str(launcher_bin),
        "TRIAD_BOOTSTRAP_SKIP_AUTH": "1",
    }
    result = subprocess.run(
        ["bash", str(BOOTSTRAP), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=env,
    )
    return result, env, launcher_bin


def test_check_installs_personal_repair_agents_and_classifier_file(tmp_path):
    result, env, _launcher_bin = _run_bootstrap(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    home = Path(env["HOME"])
    for name in ("claude-wrapper-repair", "gemini-wrapper-repair", "agy-wrapper-repair"):
        assert (home / ".codex" / "agents" / f"{name}.toml").is_file()
    assert (
        Path(env["XDG_CONFIG_HOME"])
        / "triad-codex-dispatch"
        / "classifier-patches.json"
    ).read_text(encoding="utf-8") == "{}\n"


def test_check_fails_when_required_binary_is_missing(tmp_path):
    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path, fake_names=("codex", "claude", "agy")
    )

    assert result.returncode != 0
    assert "missing required binary: gemini" in result.stderr


def test_check_installs_executable_launcher_scripts(tmp_path):
    result, _env, launcher_bin = _run_bootstrap(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    for name in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        launcher = launcher_bin / name
        assert launcher.is_file()
        assert os.access(launcher, os.X_OK)
        text = launcher.read_text(encoding="utf-8")
        assert "exec python3" in text
        assert str(ROOT / "bin" / name) in text
