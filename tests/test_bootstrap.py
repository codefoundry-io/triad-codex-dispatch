import os
import pytest
import shutil
import stat
import subprocess
import sys
import tomllib
from pathlib import Path


def _fs_case_insensitive(probe: Path) -> bool:
    """True if probe's filesystem is case-insensitive (macOS APFS default) — an
    upper- and lower-cased variant of the SAME existing path share one inode. On
    a case-sensitive FS (Linux ext4) the variant does not exist -> False. Used to
    gate the case-variant workspace-escape test to the FS class where the bypass
    is meaningful."""
    s = str(probe)
    try:
        up, lo = s.upper(), s.lower()
        if not (os.path.exists(up) and os.path.exists(lo)):
            return False
        return os.path.samestat(os.stat(up), os.stat(lo))
    except OSError:
        return False


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "bootstrap.sh"

def _fake_bin(
    tmp_path: Path,
    *names: str,
    python_script: str | None = None,
    scripts: dict[str, str] | None = None,
) -> Path:
    bin_dir = tmp_path / "fake-bin"
    bin_dir.mkdir(exist_ok=True)
    for name in names:
        path = bin_dir / name
        if scripts and name in scripts:
            path.write_text(f"#!/usr/bin/env bash\n{scripts[name]}\n", encoding="utf-8")
        elif name == "python3":
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
    (bin_dir / "triad_runtime.py").write_text(
        "#!/usr/bin/env python3\n", encoding="utf-8"
    )
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
    arg="--check",
    cwd=None,
    fake_scripts=None,
    timeout=10,
):
    if repo_root is None:
        repo_root = _make_repo_root(tmp_path, real_agents=True)
    fake_bin = _fake_bin(
        tmp_path, *fake_names, "jq", "python3",
        python_script=python_script,
        scripts=fake_scripts,
    )
    launcher_bin = tmp_path / "launchers"
    launcher_bin.mkdir(exist_ok=True)
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
    }
    if env_overrides:
        env.update(env_overrides)
    result = subprocess.run(
        ["bash", str(BOOTSTRAP), arg],
        cwd=str(cwd) if cwd is not None else ROOT,
        text=True,
        capture_output=True,
        env=env,
        timeout=timeout,
    )
    return result, env, launcher_bin


def _assert_no_repair_agents_installed(codex_home: Path) -> None:
    # Privilege-separation redesign (2026-07-05): the write-capable confused-deputy
    # repair agents are GONE. Codex-host repair is a top-level read-only analyzer
    # the owner runs in a FRESH terminal (surfaced by the dispatch SKILL Step 5).
    # Bootstrap installs NO $CODEX_HOME/agents/*.toml.
    agents_dir = codex_home / "agents"
    for name in ("claude-wrapper-repair", "gemini-wrapper-repair", "agy-wrapper-repair"):
        assert not (agents_dir / f"{name}.toml").exists()
    # No stray *-wrapper-repair.toml under agents/ at all.
    if agents_dir.exists():
        assert not list(agents_dir.glob("*-wrapper-repair.toml"))


def _assert_profile_does_not_disable_multi_agent(profile_path: Path) -> None:
    # The generated PROFILE must NOT set [features] multi_agent = false. That
    # backstop was over-broad: triad-cross-family-review's codex-host copy uses
    # codex multi-agent spawn_agent for its fresh-codex reviewer leg, so
    # disabling multi-agent breaks a legitimate subagent use. The confused-
    # deputy it defended against is already closed by removing the write-
    # capable repair agents (see _assert_no_repair_agents_installed) — nothing
    # left to defend, so the setting is removed.
    data = tomllib.loads(profile_path.read_text(encoding="utf-8"))
    assert "multi_agent" not in data.get("features", {})


def test_default_install_installs_profile_rules_and_prompts_by_default(tmp_path):
    # Default-ON: a plain --install with 0 env vars installs BOTH the runtime
    # profile and the command rules (the recommended setup), and the launcher +
    # classifier + log dir install path is unchanged. Repair agents are still
    # never installed (privilege-separation redesign). Crucially the generated
    # profile still PROMPTS by default (approval_policy=on-request): defaulting
    # profile+rules ON must NOT silently auto-approve — the no-prompt `never`
    # posture stays opt-in.
    result, env, _launcher_bin = _run_bootstrap(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    home = Path(env["HOME"])
    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    _assert_no_repair_agents_installed(home / ".codex")
    assert (
        Path(env["XDG_CONFIG_HOME"])
        / "triad-codex-dispatch"
        / "classifier-patches.json"
    ).read_text(encoding="utf-8") == "{}\n"
    assert (repo_root / "bin" / "_logs").is_dir()
    # profile + rules now install by DEFAULT (no env var)
    profile = home / ".codex" / "triad-codex-dispatch.config.toml"
    assert profile.is_file()
    assert (home / ".codex" / "rules" / "triad-codex-dispatch.rules").is_file()
    # SAFETY: the default profile still prompts (does not auto-approve)
    data = tomllib.loads(profile.read_text(encoding="utf-8"))
    assert data["approval_policy"] == "on-request"
    _assert_profile_does_not_disable_multi_agent(profile)
    # The old "start a new Codex session so custom agents reload" line is gone:
    # nothing custom-agent-shaped is installed anymore.
    assert "custom agents reload" not in result.stdout
    assert "repair agents installed to personal Codex scope" not in result.stdout


def test_profile_opted_out_via_explicit_zero(tmp_path):
    # Default-ON opt-out path 1: an explicit ...=0 on both suppresses the
    # profile and rules while the rest of the install still succeeds.
    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0",
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "0",
        },
    )
    assert result.returncode == 0, result.stderr + result.stdout
    home = Path(env["HOME"])
    assert not (home / ".codex" / "triad-codex-dispatch.config.toml").exists()
    assert not (home / ".codex" / "rules" / "triad-codex-dispatch.rules").exists()
    assert (launcher_bin / "claude_wrapper.py").is_file()


def test_profile_opted_out_via_skip_flag(tmp_path):
    # Default-ON opt-out path 2: the ...SKIP_...=1 escape suppresses the profile
    # and rules while the rest of the install still succeeds.
    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={
            "TRIAD_BOOTSTRAP_SKIP_CODEX_PROFILE": "1",
            "TRIAD_BOOTSTRAP_SKIP_CODEX_RULES": "1",
        },
    )
    assert result.returncode == 0, result.stderr + result.stdout
    home = Path(env["HOME"])
    assert not (home / ".codex" / "triad-codex-dispatch.config.toml").exists()
    assert not (home / ".codex" / "rules" / "triad-codex-dispatch.rules").exists()
    assert (launcher_bin / "claude_wrapper.py").is_file()


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
    _assert_no_repair_agents_installed(codex_home)
    assert (codex_home / "triad-codex-dispatch.config.toml").is_file()
    _assert_profile_does_not_disable_multi_agent(codex_home / "triad-codex-dispatch.config.toml")
    assert (codex_home / "rules" / "triad-codex-dispatch.rules").is_file()
    assert not (Path(env["HOME"]) / ".codex" / "agents").exists()


def test_install_never_executes_provider_binaries(tmp_path: Path) -> None:
    marker = tmp_path / "provider-called"
    provider_script = (
        'if [ "${1:-}" = "--version" ]; then echo "provider 2.1.170"; '
        'else printf provider-called > "$TRIAD_PROVIDER_MARKER"; fi'
    )
    result, _env, launchers = _run_bootstrap(
        tmp_path,
        env_overrides={
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "0",
            "TRIAD_PROVIDER_MARKER": str(marker),
        },
        fake_scripts={
            "codex": provider_script,
            "claude": provider_script,
            "gemini": provider_script,
            "agy": provider_script,
        },
        arg="--install",
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert not marker.exists()
    for name in ("triad-setup", "triad-doctor"):
        launcher = launchers / name
        assert launcher.is_file()
        assert os.access(launcher, os.X_OK)
        assert "triad_runtime.py" in launcher.read_text(encoding="utf-8")


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
    _assert_no_repair_agents_installed(codex_home)
    assert (codex_home / "triad-codex-dispatch.config.toml").is_file()
    _assert_profile_does_not_disable_multi_agent(codex_home / "triad-codex-dispatch.config.toml")
    assert (codex_home / "rules" / "triad-codex-dispatch.rules").is_file()
    assert not (Path.cwd() / "~").exists()


def test_check_supports_workspace_contained_install_targets(tmp_path):
    # Install targets contained in the TOOLKIT checkout are still supported
    # when bootstrap runs from OUTSIDE those directories (cwd=ROOT here).
    # Running the same layout FROM the containing directory is a promptless
    # sandbox-escape chain and must hard-fail — see the
    # test_install_fails_when_*_inside_workspace battery below.
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
    _assert_no_repair_agents_installed(workspace_codex)
    assert (workspace_codex / "triad-codex-dispatch.config.toml").is_file()
    _assert_profile_does_not_disable_multi_agent(workspace_codex / "triad-codex-dispatch.config.toml")
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
    _assert_no_repair_agents_installed(codex_home)
    assert (codex_home / "triad-codex-dispatch.config.toml").is_file()
    _assert_profile_does_not_disable_multi_agent(codex_home / "triad-codex-dispatch.config.toml")
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
    # MUST-land 5: the generated runtime profile must use the Codex
    # permission-profile system (default_permissions + [permissions.<name>]).
    # Legacy sandbox_mode / [sandbox_workspace_write] in ANY loaded config
    # layer makes Codex ignore default_permissions entirely, which would
    # neutralize the repair agents' default_permissions="triad_repair"
    # scoping (developers.openai.com/codex/permissions, checked 2026-07-05).
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
    assert "sandbox_mode" not in data
    assert "sandbox_workspace_write" not in data
    assert data["default_permissions"] == "triad_leader"
    # The over-broad [features] multi_agent = false backstop is REMOVED: it
    # disabled triad-cross-family-review's legitimate codex-host spawn_agent
    # fresh-codex reviewer leg, while defending against a confused-deputy path
    # already closed by removing the write-capable repair agents.
    assert "multi_agent" not in data.get("features", {})
    leader = data["permissions"]["triad_leader"]
    assert leader["extends"] == ":workspace"
    fs = leader["filesystem"]
    classifier_dir = str(Path(env["XDG_CONFIG_HOME"]) / "triad-codex-dispatch")
    log_dir = str(Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]) / "bin" / "_logs")
    assert fs[classifier_dir] == "write"
    assert fs[log_dir] == "write"
    assert leader["network"]["enabled"] is True
    assert not any(".codex/agents" in key for key in fs)
    assert not any(".local/bin" in key for key in fs)
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


@pytest.mark.parametrize(
    ("name", "marker", "dangling"),
    [
        ("claude_wrapper.py", "# triad-codex-dispatch managed launcher\n", False),
        ("claude_wrapper.py", "# triad-codex-dispatch managed launcher\n", True),
        ("triad-setup", "# triad-codex-dispatch managed runtime command\n", False),
        ("triad-setup", "# triad-codex-dispatch managed runtime command\n", True),
    ],
)
def test_install_refuses_symlinked_managed_targets_without_mutating_them(
    tmp_path: Path, name: str, marker: str, dangling: bool
) -> None:
    launcher_dir = tmp_path / "linked-launchers"
    launcher_dir.mkdir()
    linked_target = tmp_path / "linked-target"
    if not dangling:
        linked_target.write_text(marker, encoding="utf-8")
        expected = linked_target.read_bytes()
    link = launcher_dir / name
    link.symlink_to(linked_target)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        pre_path=(launcher_dir,),
        env_overrides={"TRIAD_BOOTSTRAP_BIN_DIR": str(launcher_dir)},
    )

    assert result.returncode != 0
    assert link.is_symlink()
    if dangling:
        assert not linked_target.exists()
    else:
        assert linked_target.read_bytes() == expected


@pytest.mark.parametrize(
    ("name", "marker", "dangling"),
    [
        ("claude_wrapper.py", "# triad-codex-dispatch managed launcher\n", False),
        ("claude_wrapper.py", "# triad-codex-dispatch managed launcher\n", True),
        ("triad-setup", "# triad-codex-dispatch managed runtime command\n", False),
        ("triad-setup", "# triad-codex-dispatch managed runtime command\n", True),
    ],
)
def test_remove_leaves_symlinked_targets_untouched(
    tmp_path: Path, name: str, marker: str, dangling: bool
) -> None:
    launcher_dir = tmp_path / "linked-launchers"
    launcher_dir.mkdir()
    linked_target = tmp_path / "linked-target"
    if not dangling:
        linked_target.write_text(marker, encoding="utf-8")
        expected = linked_target.read_bytes()
    link = launcher_dir / name
    link.symlink_to(linked_target)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--remove",
        env_overrides={"TRIAD_BOOTSTRAP_BIN_DIR": str(launcher_dir)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert link.is_symlink()
    if dangling:
        assert not linked_target.exists()
    else:
        assert linked_target.read_bytes() == expected


@pytest.mark.parametrize(
    ("mode", "name"),
    [
        ("--install", "claude_wrapper.py"),
        ("--install", "triad-setup"),
        ("--remove", "claude_wrapper.py"),
        ("--remove", "triad-setup"),
    ],
)
def test_fifo_targets_are_rejected_without_blocking(
    tmp_path: Path, mode: str, name: str
) -> None:
    launcher_dir = tmp_path / "fifo-launchers"
    launcher_dir.mkdir()
    target = launcher_dir / name
    os.mkfifo(target)

    try:
        result, _env, _launchers = _run_bootstrap(
            tmp_path,
            arg=mode,
            pre_path=(launcher_dir,),
            env_overrides={"TRIAD_BOOTSTRAP_BIN_DIR": str(launcher_dir)},
            timeout=2,
        )
    except subprocess.TimeoutExpired as exc:
        pytest.fail(f"bootstrap blocked while inspecting FIFO target: {exc}")

    assert stat.S_ISFIFO(target.stat().st_mode)
    if mode == "--install":
        assert result.returncode != 0
    else:
        assert result.returncode == 0, result.stderr + result.stdout


def test_unmanaged_runtime_command_preflight_prevents_partial_install(tmp_path: Path) -> None:
    launcher_dir = tmp_path / "runtime-launchers"
    launcher_dir.mkdir()
    setup = launcher_dir / "triad-setup"
    setup.write_text("#!/usr/bin/env bash\necho unmanaged\n", encoding="utf-8")

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        pre_path=(launcher_dir,),
        env_overrides={"TRIAD_BOOTSTRAP_BIN_DIR": str(launcher_dir)},
    )

    assert result.returncode != 0
    assert setup.read_text(encoding="utf-8") == "#!/usr/bin/env bash\necho unmanaged\n"
    assert not (launcher_dir / "triad-doctor").exists()


def test_reinstall_replaces_managed_wrapper_hardlink_without_mutating_peer(tmp_path: Path) -> None:
    first, env, launcher_dir = _run_bootstrap(tmp_path, arg="--install")
    assert first.returncode == 0, first.stderr + first.stdout
    launcher = launcher_dir / "claude_wrapper.py"
    peer = tmp_path / "launcher-peer"
    os.link(launcher, peer)
    with launcher.open("a", encoding="utf-8") as handle:
        handle.write("# peer must retain this byte sequence\n")
    peer_before = peer.read_bytes()

    second, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
    )

    assert second.returncode == 0, second.stderr + second.stdout
    assert peer.read_bytes() == peer_before
    assert launcher.read_bytes() != peer_before


def test_optional_gemini_launcher_remains_pinned_and_fails_closed_when_pin_is_missing(tmp_path):
    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        fake_names=("codex", "claude", "agy"),
    )

    assert result.returncode == 0, result.stderr + result.stdout
    text = (launcher_bin / "gemini_wrapper.py").read_text(encoding="utf-8")
    assert "TRIAD_REQUIRE_PINNED_VENDOR" in text
    assert 'env["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"' in text
    assert 'env.pop("TRIAD_GEMINI_BIN", None)' in text


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


# --- MUST-land 1: workspace-escape guard -----------------------------------
# The generated exec-policy allow-rules run the launcher paths OUTSIDE the
# sandbox without prompting. If any install target (or the checkout the
# launchers exec) is writable from inside the Codex workspace bootstrap runs
# from ($PWD = the sandbox-writable root), a sandboxed session can rewrite an
# allow-listed file and escape without a prompt. Bootstrap must hard-fail.


def test_install_fails_when_codex_home_inside_workspace(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()

    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        cwd=workspace,
        env_overrides={"CODEX_HOME": str(workspace / ".triad-codex-home")},
    )

    assert result.returncode != 0
    assert "workspace-escape guard" in result.stderr
    assert "CODEX_HOME" in result.stderr
    assert not any(launcher_bin.iterdir())
    assert not (workspace / ".triad-codex-home").exists()
    assert not (Path(env["HOME"]) / ".codex" / "agents").exists()


def test_install_fails_when_launcher_dir_inside_workspace(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    ws_bin = workspace / ".triad-bin"

    result, env, _launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        cwd=workspace,
        pre_path=(ws_bin,),
        env_overrides={"TRIAD_BOOTSTRAP_BIN_DIR": str(ws_bin)},
    )

    assert result.returncode != 0
    assert "workspace-escape guard" in result.stderr
    assert "TRIAD_BOOTSTRAP_BIN_DIR" in result.stderr
    assert not ws_bin.exists()
    assert not (Path(env["HOME"]) / ".codex" / "agents").exists()


def test_install_fails_when_classifier_dir_inside_workspace(tmp_path):
    workspace = tmp_path / "ws"
    workspace.mkdir()

    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        cwd=workspace,
        env_overrides={"XDG_CONFIG_HOME": str(workspace / ".triad-config")},
    )

    assert result.returncode != 0
    assert "workspace-escape guard" in result.stderr
    assert "classifier" in result.stderr
    assert not any(launcher_bin.iterdir())


def test_install_fails_when_repo_root_inside_workspace(tmp_path):
    # The launchers exec <repo_root>/bin/*.py, so a checkout cloned INTO the
    # workspace is the same promptless escape chain even when the launcher
    # directory itself lives outside.
    workspace = tmp_path / "ws"
    workspace.mkdir()
    repo_root = _make_repo_root(workspace, real_agents=True)

    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        cwd=workspace,
        repo_root=repo_root,
    )

    assert result.returncode != 0
    assert "workspace-escape guard" in result.stderr
    assert "TRIAD_BOOTSTRAP_REPO_ROOT" in result.stderr
    assert not any(launcher_bin.iterdir())


# --- Fast-follow: --install primary, --check deprecated alias ---------------


def test_install_flag_is_primary_and_check_is_deprecated_alias(tmp_path):
    result, env, _launcher_bin = _run_bootstrap(tmp_path, arg="--install")
    assert result.returncode == 0, result.stderr + result.stdout
    assert "--check is deprecated" not in result.stdout

    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    result2, _env2, _launcher_bin2 = _run_bootstrap(
        tmp_path, repo_root=repo_root, arg="--bogus"
    )
    assert result2.returncode == 2


@pytest.mark.parametrize(
    ("alias", "canonical"),
    [("--check", "--install"), ("--uninstall", "--remove")],
)
def test_legacy_aliases_are_bounded(tmp_path: Path, alias: str, canonical: str) -> None:
    result, _env, _launchers = _run_bootstrap(tmp_path, arg=alias, timeout=5)

    assert result.returncode == 0, result.stderr + result.stdout
    assert f"deprecated alias for {canonical}" in result.stdout
    assert "removed in the next release after 0.2.526" in result.stdout


def test_second_install_completes_within_timeout(tmp_path: Path) -> None:
    first, env, _launchers = _run_bootstrap(tmp_path, arg="--install", timeout=5)
    assert first.returncode == 0, first.stderr + first.stdout

    second, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        arg="--install",
        timeout=5,
    )
    assert second.returncode == 0, second.stderr + second.stdout


def test_bootstrap_removes_auth_probe_configuration():
    text = BOOTSTRAP.read_text(encoding="utf-8")
    assert "run_auth_probe" not in text
    assert "check_auth" not in text
    assert "TRIAD_BOOTSTRAP_AUTH_TIMEOUT" not in text
    assert "TRIAD_BOOTSTRAP_SKIP_AUTH" not in text
    assert "TRIAD_BOOTSTRAP_CODEX_AUTH_CMD" not in text
    assert "TRIAD_BOOTSTRAP_CLAUDE_AUTH_CMD" not in text
    assert "TRIAD_BOOTSTRAP_GEMINI_AUTH_CMD" not in text
    assert "TRIAD_BOOTSTRAP_AGY_AUTH_CMD" not in text


def test_claude_version_minimum_warns_on_old_version(tmp_path):
    # default fake claude prints "claude fake 1.0" -> parsed 1.0 < 2.1.170
    result, _env, _launcher_bin = _run_bootstrap(tmp_path, arg="--install")

    assert result.returncode == 0, result.stderr + result.stdout
    warn_lines = [
        line
        for line in result.stdout.splitlines()
        if "[warn]" in line and "claude version" in line
    ]
    assert warn_lines, result.stdout
    assert any("2.1.170" in line for line in warn_lines)


def test_claude_version_minimum_passes_on_current_version(tmp_path):
    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        fake_scripts={"claude": "echo '2.1.170 (Claude Code)'"},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert any(
        "[ok]" in line and "claude version 2.1.170" in line
        for line in result.stdout.splitlines()
    )


# --- MUST-land 6: pinned no-prompt entry (codex-triad) -----------------------


def test_shell_entry_installs_pinned_codex_triad_function(tmp_path):
    shell_rc = tmp_path / "shellrc"
    overrides = {
        "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
        "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
    }

    result, env, _launcher_bin = _run_bootstrap(
        tmp_path, arg="--install", env_overrides=overrides
    )

    assert result.returncode == 0, result.stderr + result.stdout
    text = shell_rc.read_text(encoding="utf-8")
    assert text.count("codex-triad()") == 1
    assert 'TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}"' in text
    assert "TRIAD_WRAPPER_HARDENED=1" in text
    assert "TRIAD_CLAUDE_ENFORCE_SANDBOX=1" in text
    assert 'command codex --profile triad-codex-dispatch --search "$@"' in text
    # bootstrap verifies the pinned posture and never emits a bare
    # `codex --profile ...` start as the primary path.
    assert "no-prompt entry verified" in result.stdout
    assert "codex --profile" not in result.stdout

    # idempotent re-run: managed block refreshed in place, not duplicated
    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    result2, _env2, _launcher_bin2 = _run_bootstrap(
        tmp_path, repo_root=repo_root, arg="--install", env_overrides=overrides
    )
    assert result2.returncode == 0, result2.stderr + result2.stdout
    assert shell_rc.read_text(encoding="utf-8").count("codex-triad()") == 1


def test_shell_entry_refuses_unmanaged_codex_triad_function(tmp_path):
    shell_rc = tmp_path / "shellrc"
    unmanaged = 'codex-triad() { command codex --profile old --search "$@"; }\n'
    shell_rc.write_text(unmanaged, encoding="utf-8")

    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert "refusing to modify unmanaged codex-triad shell entry" in result.stderr
    assert shell_rc.read_text(encoding="utf-8") == unmanaged


# --- Fast-follow: --remove uninstall path ------------------------------------


def test_remove_uninstalls_managed_artifacts_and_shell_entry(tmp_path):
    shell_rc = tmp_path / "shellrc"
    overrides = {
        "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
        "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1",
        "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "1",
    }
    result, env, launcher_bin = _run_bootstrap(
        tmp_path, arg="--install", env_overrides=overrides
    )
    assert result.returncode == 0, result.stderr + result.stdout
    home = Path(env["HOME"])
    classifier = (
        Path(env["XDG_CONFIG_HOME"]) / "triad-codex-dispatch" / "classifier-patches.json"
    )
    assert classifier.is_file()
    assert (launcher_bin / "claude_wrapper.py").is_file()
    assert (home / ".codex" / "triad-codex-dispatch.config.toml").is_file()

    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    result2, _env2, _launcher_bin2 = _run_bootstrap(
        tmp_path, repo_root=repo_root, arg="--remove", env_overrides=overrides
    )
    assert result2.returncode == 0, result2.stderr + result2.stdout
    for name in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        assert not (launcher_bin / name).exists()
    for name in ("claude-wrapper-repair", "gemini-wrapper-repair", "agy-wrapper-repair"):
        assert not (home / ".codex" / "agents" / f"{name}.toml").exists()
    assert not (home / ".codex" / "triad-codex-dispatch.config.toml").exists()
    assert not (home / ".codex" / "rules" / "triad-codex-dispatch.rules").exists()
    assert "codex-triad" not in shell_rc.read_text(encoding="utf-8")
    # learned classifier patches are user data and must survive --remove
    assert classifier.is_file()


def test_remove_leaves_unmanaged_launcher_and_profile_in_place(tmp_path):
    custom_bin = tmp_path / "custom-bin"
    custom_bin.mkdir()
    custom_launcher = custom_bin / "claude_wrapper.py"
    custom_launcher.write_text(
        "#!/usr/bin/env bash\necho custom claude wrapper\n", encoding="utf-8"
    )
    custom_launcher.chmod(custom_launcher.stat().st_mode | stat.S_IEXEC)
    profile = tmp_path / "home" / ".codex" / "triad-codex-dispatch.config.toml"
    profile.parent.mkdir(parents=True)
    profile.write_text('approval_policy = "never"\n', encoding="utf-8")

    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--remove",
        env_overrides={"TRIAD_BOOTSTRAP_BIN_DIR": str(custom_bin)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert custom_launcher.is_file()
    assert profile.read_text(encoding="utf-8") == 'approval_policy = "never"\n'


# --- MUST-land 5 adjacency: legacy sandbox settings disable profiles ---------


def test_install_warns_when_base_config_has_legacy_sandbox_mode(tmp_path):
    codex_home = tmp_path / "home" / ".codex"
    codex_home.mkdir(parents=True)
    (codex_home / "config.toml").write_text(
        'sandbox_mode = "workspace-write"\n', encoding="utf-8"
    )

    result, _env, _launcher_bin = _run_bootstrap(tmp_path, arg="--install")

    assert result.returncode == 0, result.stderr + result.stdout
    assert any(
        "[warn]" in line and "sandbox_mode" in line
        for line in result.stdout.splitlines()
    )


def test_install_fails_when_codex_home_inside_workspace_via_case_variant(tmp_path):
    """macOS case-insensitivity workspace-escape bypass (finding #2, 2026-07-05).

    A CODEX_HOME that resolves INSIDE the sandbox-writable workspace through a
    case-variant path (WS vs ws) is the SAME promptless escape chain as the
    plain inside-workspace battery and MUST hard-fail. The guard compared with
    Path.is_relative_to (case-SENSITIVE), so on a case-insensitive FS (macOS APFS
    default) a mixed-case install target slipped past the guard and installed
    into the writable workspace. Skips on a case-sensitive FS (Linux ext4), where
    the case-variant is genuinely a distinct directory and no bypass exists.
    """
    workspace = tmp_path / "ws"
    workspace.mkdir()
    if not _fs_case_insensitive(workspace):
        pytest.skip(
            "case-insensitive FS only (macOS APFS); on a case-sensitive FS the "
            "case-variant path is a distinct directory, so there is no bypass"
        )
    # On a case-insensitive FS, ".../WS/..." and ".../ws/..." are the SAME inode:
    # this target resolves inside the workspace, but its casing differs from the
    # resolved workspace root, which is exactly what defeated is_relative_to.
    variant_codex_home = tmp_path / "WS" / ".triad-codex-home"

    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        cwd=workspace,
        env_overrides={"CODEX_HOME": str(variant_codex_home)},
    )

    assert result.returncode != 0
    assert "workspace-escape guard" in result.stderr
    assert "CODEX_HOME" in result.stderr
    assert not any(launcher_bin.iterdir())
    assert not variant_codex_home.exists()


def test_migration_rules_claude_examples_use_effort_not_reasoning():
    # finding #8 (2026-07-05): claude_wrapper takes --effort (low/medium/high/
    # xhigh/max), NOT codex's --reasoning. A shipped rules example with --reasoning
    # would be copy-pasted and rejected by argparse. Guard the shipped example.
    rules = (ROOT / "migration" / "triad-codex-dispatch.rules").read_text(encoding="utf-8")
    for line in rules.splitlines():
        if "claude_wrapper.py" in line:
            assert "--reasoning" not in line, (
                f"claude_wrapper example must use --effort, not --reasoning: {line.strip()}"
            )
