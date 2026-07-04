import os
import shutil
import stat
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "bootstrap.sh"

def _fake_bin(tmp_path: Path, *names: str, python_script: str | None = None) -> Path:
    bin_dir = tmp_path / "fake-bin"
    bin_dir.mkdir()
    for name in names:
        path = bin_dir / name
        if name == "python3":
            body = python_script or f"exec {sys.executable} \"$@\""
            path.write_text(f"#!/usr/bin/env bash\n{body}\n", encoding="utf-8")
        else:
            path.write_text(f"#!/usr/bin/env bash\necho '{name} fake 1.0'\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return bin_dir


def _make_repo_root(
    tmp_path: Path,
    executable_wrappers=True,
    real_agents=False,
) -> Path:
    repo_root = tmp_path / "repo"
    bin_dir = repo_root / "bin"
    agents_dir = repo_root / "agents"
    skills_dir = repo_root / "skills"
    bin_dir.mkdir(parents=True)
    agents_dir.mkdir()
    mode = stat.S_IRUSR | stat.S_IWUSR
    if executable_wrappers:
        mode |= stat.S_IXUSR
    for name in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        wrapper = bin_dir / name
        wrapper.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        wrapper.chmod(mode)
    if real_agents:
        for path in (ROOT / "agents").glob("*.toml"):
            shutil.copy2(path, agents_dir / path.name)
        shutil.copytree(ROOT / "skills", skills_dir)
    else:
        for name in ("claude-wrapper-repair", "gemini-wrapper-repair", "agy-wrapper-repair"):
            (agents_dir / f"{name}.toml").write_text(
                f'name = "{name}"\ndescription = "{name}"\n',
                encoding="utf-8",
            )
    return repo_root


def _run_bootstrap(
    tmp_path: Path,
    fake_names=("codex", "claude", "gemini", "agy"),
    repo_root=None,
    pre_path=(),
    extra_path=(),
    python_script=None,
    env_overrides=None,
):
    if repo_root is None:
        repo_root = _make_repo_root(tmp_path, real_agents=True)
    fake_bin = _fake_bin(tmp_path, *fake_names, "jq", "python3", python_script=python_script)
    launcher_bin = tmp_path / "launchers"
    launcher_bin.mkdir()
    python_bin = Path(sys.executable).parent
    extra = os.pathsep.join(str(p) for p in extra_path)
    path_parts = [str(fake_bin)]
    path_parts.extend(str(p) for p in pre_path)
    path_parts.append(str(launcher_bin))
    if extra:
        path_parts.append(extra)
    path_parts.extend([str(python_bin), "/usr/bin", "/bin", "/usr/sbin", "/sbin"])
    base_env = {
        key: value
        for key, value in os.environ.items()
        if key != "CODEX_HOME" and not key.startswith("TRIAD_")
    }
    env = {
        **base_env,
        "HOME": str(tmp_path / "home"),
        "XDG_CONFIG_HOME": str(tmp_path / "xdg-config"),
        "PATH": os.pathsep.join(path_parts),
        "TRIAD_BOOTSTRAP_REPO_ROOT": str(repo_root),
        "TRIAD_BOOTSTRAP_BIN_DIR": str(launcher_bin),
        "TRIAD_BOOTSTRAP_SKIP_AUTH": "1",
    }
    if env_overrides:
        env.update(env_overrides)
    result = subprocess.run(
        ["bash", str(BOOTSTRAP), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=env,
    )
    return result, env, launcher_bin


def _assert_installed_agents_are_repair_only(codex_home: Path) -> None:
    for name in ("claude-wrapper-repair", "gemini-wrapper-repair", "agy-wrapper-repair"):
        installed = codex_home / "agents" / f"{name}.toml"
        assert installed.is_file()
        data = tomllib.loads(installed.read_text(encoding="utf-8"))
        assert "skills" not in data
        assert data["default_permissions"] == "triad_repair"


def test_check_installs_personal_repair_agents_and_classifier_file(tmp_path):
    result, env, _launcher_bin = _run_bootstrap(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    home = Path(env["HOME"])
    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    classifier_dir = Path(env["XDG_CONFIG_HOME"]) / "triad-codex-dispatch"
    fake_bin = Path(env["PATH"].split(os.pathsep)[0]).resolve()
    python_exe_dir = Path(sys.executable).resolve().parent
    python_root = Path(sys.base_prefix).resolve()
    python_prefix = Path(sys.prefix).resolve()
    for name in ("claude-wrapper-repair", "gemini-wrapper-repair", "agy-wrapper-repair"):
        installed = home / ".codex" / "agents" / f"{name}.toml"
        assert installed.is_file()
        text = installed.read_text(encoding="utf-8")
        assert "__TRIAD_REPO_ROOT__" not in text
        assert "__TRIAD_CLASSIFIER_PATH__" not in text
        assert "__TRIAD_CLASSIFIER_DIR__" not in text
        assert "__TRIAD_PYTHON3__" not in text
        assert "__TRIAD_PYTHON_READ_ROOTS__" not in text
        assert "__TRIAD_VENDOR_READ_ROOTS__" not in text
        assert str(repo_root) in text
        assert str(classifier_dir / "classifier-patches.json") in text
        data = tomllib.loads(text)
        assert "skills" not in data
        fs = data["permissions"]["triad_repair"]["filesystem"]
        assert fs[str(repo_root)] == "read"
        assert fs[str(repo_root / "bin" / "_logs")] == "write"
        assert fs[str(classifier_dir)] == "write"
        assert fs[str(python_exe_dir)] == "read"
        assert fs[str(python_root)] == "read"
        assert fs[str(python_prefix)] == "read"
        assert fs[str(fake_bin)] == "read"
    assert (
        Path(env["XDG_CONFIG_HOME"])
        / "triad-codex-dispatch"
        / "classifier-patches.json"
    ).read_text(encoding="utf-8") == "{}\n"
    assert (repo_root / "bin" / "_logs").is_dir()
    assert not (home / ".codex" / "triad-codex-dispatch.config.toml").exists()
    assert not (home / ".codex" / "rules" / "triad-codex-dispatch.rules").exists()
    assert (
        "start a new Codex session/thread after bootstrap so custom agents reload"
        in result.stdout
    )


def test_check_fails_when_repair_agent_placeholder_is_unresolved(tmp_path):
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    agent = repo_root / "agents" / "claude-wrapper-repair.toml"
    agent.write_text(
        agent.read_text(encoding="utf-8") + '\nplaceholder = "__TRIAD_UNKNOWN_PLACEHOLDER__"\n',
        encoding="utf-8",
    )

    result, _env, _launcher_bin = _run_bootstrap(tmp_path, repo_root=repo_root)

    assert result.returncode != 0
    assert "unresolved repair-agent placeholders" in result.stderr
    assert "__TRIAD_UNKNOWN_PLACEHOLDER__" in result.stderr
    assert "repair agents installed to personal Codex scope" not in result.stdout


def test_check_uses_codex_home_for_repair_agents_profile_and_rules(tmp_path):
    codex_home = tmp_path / "custom-codex-home"
    result, env, _launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1",
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "1",
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    _assert_installed_agents_are_repair_only(codex_home)
    assert (codex_home / "triad-codex-dispatch.config.toml").is_file()
    assert (codex_home / "rules" / "triad-codex-dispatch.rules").is_file()
    assert not (Path(env["HOME"]) / ".codex" / "agents").exists()


def test_default_agy_auth_probe_uses_wrapper_pty_path():
    text = BOOTSTRAP.read_text(encoding="utf-8")

    assert (
        'run_auth_probe "agy" '
        '"${TRIAD_BOOTSTRAP_AGY_AUTH_CMD:-antigravity_wrapper.py --prompt '
        in text
    )
    assert 'TRIAD_BOOTSTRAP_AGY_AUTH_CMD:-agy -p' not in text


def test_check_expands_codex_home_for_repair_agents_profile_and_rules(tmp_path):
    result, env, _launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={
            "CODEX_HOME": "~/custom-codex-home",
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1",
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "1",
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    codex_home = Path(env["HOME"]) / "custom-codex-home"
    _assert_installed_agents_are_repair_only(codex_home)
    assert (codex_home / "triad-codex-dispatch.config.toml").is_file()
    assert (codex_home / "rules" / "triad-codex-dispatch.rules").is_file()
    assert not (Path.cwd() / "~").exists()


def test_check_supports_workspace_contained_install_targets(tmp_path):
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    workspace_codex = repo_root / ".triad-codex-home"
    workspace_config = repo_root / ".triad-config"
    workspace_bin = repo_root / ".triad-bin"
    result, env, _launcher_bin = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        pre_path=(workspace_bin,),
        env_overrides={
            "CODEX_HOME": str(workspace_codex),
            "XDG_CONFIG_HOME": str(workspace_config),
            "TRIAD_BOOTSTRAP_BIN_DIR": str(workspace_bin),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1",
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "1",
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert (workspace_bin / "claude_wrapper.py").is_file()
    assert (workspace_config / "triad-codex-dispatch" / "classifier-patches.json").is_file()
    _assert_installed_agents_are_repair_only(workspace_codex)
    assert (workspace_codex / "triad-codex-dispatch.config.toml").is_file()
    assert (workspace_codex / "rules" / "triad-codex-dispatch.rules").is_file()
    assert not (Path(env["HOME"]) / ".codex").exists()
    assert not (Path(env["HOME"]) / ".config" / "triad-codex-dispatch").exists()


def test_check_ignores_python_stderr_when_parsing_install_paths(tmp_path):
    codex_home = tmp_path / "custom-codex-home"
    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        python_script=(
            "printf 'python startup warning\\n' >&2\n"
            f"exec {sys.executable} \"$@\""
        ),
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1",
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "1",
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "python startup warning" in result.stderr
    assert f"Codex runtime profile installed: {codex_home}" in result.stdout
    assert f"Codex command rules installed: {codex_home / 'rules' / 'triad-codex-dispatch.rules'}" in result.stdout
    assert (launcher_bin / "claude_wrapper.py").is_file()
    assert (codex_home / "agents" / "claude-wrapper-repair.toml").is_file()
    assert (codex_home / "triad-codex-dispatch.config.toml").is_file()
    assert (codex_home / "rules" / "triad-codex-dispatch.rules").is_file()


def test_check_warns_when_gemini_binary_is_missing(tmp_path):
    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path, fake_names=("codex", "claude", "agy")
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "optional binary not found: gemini" in result.stdout


def test_check_fails_when_required_binary_is_missing(tmp_path):
    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path, fake_names=("codex", "agy")
    )

    assert result.returncode != 0
    assert "missing required binary: claude" in result.stderr


def test_check_stops_before_install_when_python_version_fails(tmp_path):
    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        python_script="exit 1",
    )

    assert result.returncode != 0
    assert "python3 >= 3.12 required" in result.stderr
    assert "required prerequisite checks failed" in result.stderr
    assert not any(launcher_bin.iterdir())
    assert not (Path(env["HOME"]) / ".codex" / "agents").exists()


def test_check_installs_executable_launcher_scripts(tmp_path):
    result, env, launcher_bin = _run_bootstrap(tmp_path)
    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])

    assert result.returncode == 0, result.stderr + result.stdout
    for name in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        launcher = launcher_bin / name
        assert launcher.is_file()
        assert os.access(launcher, os.X_OK)
        text = launcher.read_text(encoding="utf-8")
        assert "os.execv" in text
        assert str(repo_root / "bin" / name) in text


def test_check_installs_launchers_when_repo_bin_on_path_but_not_executable(tmp_path):
    repo_root = _make_repo_root(tmp_path, executable_wrappers=False)
    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        extra_path=(repo_root / "bin",),
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "launcher scripts installed and active on PATH" in result.stdout
    for name in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        launcher = launcher_bin / name
        assert launcher.is_file()
        assert os.access(launcher, os.X_OK)


def test_check_fails_when_stale_wrapper_shadows_launcher(tmp_path):
    stale_bin = tmp_path / "stale-bin"
    stale_bin.mkdir()
    for name in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        wrapper = stale_bin / name
        wrapper.write_text("#!/usr/bin/env bash\necho stale\n", encoding="utf-8")
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IEXEC)

    result, _env, launcher_bin = _run_bootstrap(tmp_path, pre_path=(stale_bin,))

    assert result.returncode != 0
    assert "wrapper command is shadowed or stale on PATH" in result.stderr
    for name in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        assert (launcher_bin / name).is_file()


def test_check_rejects_relative_repo_root_override(tmp_path):
    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={"TRIAD_BOOTSTRAP_REPO_ROOT": "relative/repo"},
    )

    assert result.returncode != 0
    assert "TRIAD_BOOTSTRAP_REPO_ROOT must be an absolute path" in result.stderr
    assert not any(launcher_bin.iterdir())
    assert not (Path(env["HOME"]) / ".codex" / "agents").exists()


def test_check_rejects_relative_classifier_override(tmp_path):
    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={"TRIAD_CLASSIFIER_EXTENSION": "relative/classifier.json"},
    )

    assert result.returncode != 0
    assert "TRIAD_CLASSIFIER_EXTENSION must be an absolute path" in result.stderr
    assert not any(launcher_bin.iterdir())
    assert not (Path(env["HOME"]) / ".codex" / "agents").exists()


def test_check_rejects_relative_launcher_dir_override(tmp_path):
    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={"TRIAD_BOOTSTRAP_BIN_DIR": "relative/bin"},
    )

    assert result.returncode != 0
    assert "TRIAD_BOOTSTRAP_BIN_DIR must be an absolute path" in result.stderr
    assert not any(launcher_bin.iterdir())
    assert not (Path(env["HOME"]) / ".codex" / "agents").exists()


def test_check_rejects_relative_codex_home_override(tmp_path):
    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={"CODEX_HOME": "relative/codex-home"},
    )

    assert result.returncode != 0
    assert "CODEX_HOME must be an absolute path" in result.stderr
    assert not any(launcher_bin.iterdir())
    assert not (Path(env["HOME"]) / ".codex" / "agents").exists()


def test_check_can_install_optional_codex_runtime_profile(tmp_path):
    result, env, _launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={"TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1"},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    profile = Path(env["HOME"]) / ".codex" / "triad-codex-dispatch.config.toml"
    assert profile.is_file()
    text = profile.read_text(encoding="utf-8")
    assert "triad-codex-dispatch managed runtime profile" in text
    data = tomllib.loads(text)
    assert "Explicit external-CLI consent profile" in text
    assert data["approval_policy"] == "on-request"
    assert data["approvals_reviewer"] == "user"
    assert data["sandbox_mode"] == "workspace-write"
    sandbox = data["sandbox_workspace_write"]
    assert sandbox["network_access"] is True
    roots = sandbox["writable_roots"]
    assert str(Path(env["XDG_CONFIG_HOME"]) / "triad-codex-dispatch") in roots
    assert str(Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]) / "bin" / "_logs") in roots
    assert not any(".codex/agents" in root for root in roots)
    assert not any(".local/bin" in root for root in roots)
    assert "Codex runtime profile installed" in result.stdout


def test_check_can_install_runtime_profile_with_never_policy(tmp_path):
    result, env, _launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1",
            "TRIAD_CODEX_PROFILE_APPROVAL_POLICY": "never",
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    profile = Path(env["HOME"]) / ".codex" / "triad-codex-dispatch.config.toml"
    data = tomllib.loads(profile.read_text(encoding="utf-8"))
    assert data["approval_policy"] == "never"


def test_check_rejects_invalid_runtime_profile_approval_policy(tmp_path):
    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1",
            "TRIAD_CODEX_PROFILE_APPROVAL_POLICY": "danger-full-access",
        },
    )

    assert result.returncode != 0
    assert "invalid TRIAD_CODEX_PROFILE_APPROVAL_POLICY" in result.stderr


def test_check_refuses_to_overwrite_unmanaged_codex_runtime_profile(tmp_path):
    profile = tmp_path / "home" / ".codex" / "triad-codex-dispatch.config.toml"
    profile.parent.mkdir(parents=True)
    profile.write_text('approval_policy = "never"\n', encoding="utf-8")

    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={"TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1"},
    )

    assert result.returncode != 0
    assert "refusing to overwrite unmanaged Codex profile" in result.stderr
    assert profile.read_text(encoding="utf-8") == 'approval_policy = "never"\n'


def test_check_can_install_optional_codex_command_rules(tmp_path):
    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={"TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "1"},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    rules = Path(env["HOME"]) / ".codex" / "rules" / "triad-codex-dispatch.rules"
    assert rules.is_file()
    text = rules.read_text(encoding="utf-8")
    assert "triad-codex-dispatch managed command rules" in text
    assert "Codex command rules installed" in result.stdout
    assert 'decision = "allow"' in text
    assert "bash -lc" in text
    assert "zsh -lc" in text
    assert "python3 -c" in text
    assert str(launcher_bin / "claude_wrapper.py") in text
    assert str(repo_root / "bin" / "claude_wrapper.py") in text
    assert str(launcher_bin / "antigravity_wrapper.py") in text
    assert str(repo_root / "bin" / "antigravity_wrapper.py") in text
    assert str(launcher_bin / "gemini_wrapper.py") in text
    assert str(repo_root / "bin" / "gemini_wrapper.py") in text
    assert f'pattern = [["{launcher_bin / "claude_wrapper.py"}"]]' in text
    assert f'pattern = [["{repo_root / "bin" / "claude_wrapper.py"}"]]' not in text
    assert 'pattern = [["claude_wrapper.py"' not in text
    assert 'pattern = [["gemini_wrapper.py"' not in text
    assert 'pattern = [["antigravity_wrapper.py"' not in text
    assert 'pattern = ["python3"]' not in text
    assert 'pattern = [["python3"]' not in text
    assert "pattern = [[\"/usr/bin/env\"" not in text
    assert "pattern = [[\"env\"" not in text
    assert "python3 " in text
    assert "/usr/bin/env python3 " in text

    launcher_text = (launcher_bin / "claude_wrapper.py").read_text(encoding="utf-8")
    assert launcher_text.startswith("#!")
    assert "TRIAD_REQUIRE_PINNED_VENDOR" in launcher_text
    assert "TRIAD_CLAUDE_BIN" in launcher_text
    gemini_launcher_text = (launcher_bin / "gemini_wrapper.py").read_text(
        encoding="utf-8"
    )
    assert "TRIAD_REQUIRE_PINNED_VENDOR" in gemini_launcher_text
    assert "TRIAD_GEMINI_BIN" in gemini_launcher_text


def test_check_refuses_to_overwrite_unmanaged_launcher(tmp_path):
    custom_bin = tmp_path / "custom-bin"
    custom_bin.mkdir()
    custom_launcher = custom_bin / "claude_wrapper.py"
    custom_launcher.write_text(
        "#!/usr/bin/env bash\necho custom claude wrapper\n",
        encoding="utf-8",
    )
    custom_launcher.chmod(custom_launcher.stat().st_mode | stat.S_IEXEC)

    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path,
        pre_path=(custom_bin,),
        env_overrides={"TRIAD_BOOTSTRAP_BIN_DIR": str(custom_bin)},
    )

    assert result.returncode != 0
    assert "refusing to overwrite unmanaged launcher" in result.stderr
    assert custom_launcher.read_text(encoding="utf-8") == (
        "#!/usr/bin/env bash\necho custom claude wrapper\n"
    )


def test_optional_gemini_launcher_does_not_require_missing_pinned_binary(tmp_path):
    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        fake_names=("codex", "claude", "agy"),
    )

    assert result.returncode == 0, result.stderr + result.stdout
    text = (launcher_bin / "gemini_wrapper.py").read_text(encoding="utf-8")
    assert "TRIAD_REQUIRE_PINNED_VENDOR" not in text
    assert "TRIAD_GEMINI_BIN" not in text


def test_check_refuses_to_overwrite_unmanaged_codex_command_rules(tmp_path):
    rules = tmp_path / "home" / ".codex" / "rules" / "triad-codex-dispatch.rules"
    rules.parent.mkdir(parents=True)
    rules.write_text('prefix_rule(pattern = ["python3"], decision = "allow")\n', encoding="utf-8")

    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={"TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "1"},
    )

    assert result.returncode != 0
    assert "refusing to overwrite unmanaged Codex rules file" in result.stderr
    assert rules.read_text(encoding="utf-8") == (
        'prefix_rule(pattern = ["python3"], decision = "allow")\n'
    )


def test_check_rejects_invalid_codex_rules_name(tmp_path):
    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "1",
            "TRIAD_CODEX_RULES_NAME": "../default.rules",
        },
    )

    assert result.returncode != 0
    assert "invalid TRIAD_CODEX_RULES_NAME" in result.stderr
