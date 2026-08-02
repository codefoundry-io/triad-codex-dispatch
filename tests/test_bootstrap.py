import os
import json
import hashlib
import importlib.util
import shlex
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
BOOTSTRAP_REPAIR = ROOT / "bin" / "bootstrap_repair.py"
APPLY_PATCH = ROOT / "bin" / "apply_patch.py"
FIXTURES = ROOT / "tests" / "fixtures"


def _copy_test_python_executable(target: Path) -> None:
    """Copy Python without relying on a mutable hard link to a signed binary."""
    shutil.copy2(Path(sys.executable).resolve(), target)
    target.chmod(target.stat().st_mode | stat.S_IXUSR)
    if sys.platform == "darwin":
        subprocess.run(
            ["codesign", "--force", "--sign", "-", str(target)],
            check=True,
            capture_output=True,
            text=True,
        )


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
            if python_script is None:
                if path.exists() or path.is_symlink():
                    path.unlink()
                path.symlink_to(Path(sys.executable).resolve())
                continue
            body = python_script
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
    (bin_dir / "apply_patch.py").write_text(
        "#!/usr/bin/env python3\n", encoding="utf-8"
    )
    shutil.copy2(BOOTSTRAP_REPAIR, bin_dir / "bootstrap_repair.py")
    shutil.copy2(ROOT / "requirements.txt", repo_root / "requirements.txt")
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


def _fake_pydantic_site(tmp_path: Path, surface: str = "v2") -> Path:
    site = tmp_path / f"fake-pydantic-{surface}"
    package = site / "pydantic"
    package.mkdir(parents=True, exist_ok=True)
    if surface == "absent":
        module = 'raise ImportError("pydantic deliberately absent")\n'
    elif surface == "v1":
        module = 'VERSION = "1.10.0"\nclass BaseModel: pass\n'
    else:
        module = '''\
VERSION = "2.99.0"
class BaseModel:
    model_validate = object()
    model_validate_json = object()
    model_json_schema = object()
class ConfigDict(dict): pass
class ValidationInfo: pass
def field_validator(*args, **kwargs): return lambda function: function
def model_validator(*args, **kwargs): return lambda function: function
'''
    (package / "__init__.py").write_text(module, encoding="utf-8")
    return site


def _run_bootstrap(
    tmp_path: Path,
    fake_names=("codex", "claude", "gemini", "agy"),
    repo_root=None,
    pre_path=(),
    extra_path=(),
    python_script=None,
    env_overrides=None,
    arg="--install",
    cwd=None,
    fake_scripts=None,
    timeout=10,
):
    if repo_root is None:
        repo_root = _make_repo_root(tmp_path, real_agents=True)
    fake_bin = _fake_bin(
        tmp_path, *fake_names, "python3",
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
    default_pydantic_site = _fake_pydantic_site(tmp_path)
    env = {
        **base_env,
        "HOME": str(tmp_path / "home"),
        "XDG_CONFIG_HOME": str(tmp_path / "xdg-config"),
        "PATH": os.pathsep.join(path_parts),
        "TRIAD_BOOTSTRAP_REPO_ROOT": str(repo_root),
        "TRIAD_BOOTSTRAP_BIN_DIR": str(launcher_bin),
        "PYTHONPATH": str(default_pydantic_site),
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


REPAIR_ANALYZER = "triad-repair-analyzer"
REPAIR_ANALYZER_MARKER = "# triad-codex-dispatch managed repair analyzer"
FROZEN_REPAIR_ANALYZER = (
    FIXTURES / "triad-repair-analyzer.ccc8ff09510b.toml"
).read_bytes()
MANAGED_LEGACY_REPAIR_AGENT = (
    b"# Codex named subagent for Claude wrapper repair agent\n"
    b"# Installed by bootstrap to the Codex personal agent-discovery scope\n"
    b'name = "claude-wrapper-repair"\n'
)
FROZEN_LEGACY_APPLY_LAUNCHER = (
    b"#!/usr/bin/python3 -E\n"
    b"# triad-codex-dispatch managed repair apply launcher\n"
    b"import os\n"
    b"import sys\n"
    b"os.execv('/usr/bin/python3', ['/usr/bin/python3', "
    b"'/managed/apply_patch.py'] + sys.argv[1:])\n"
)
FROZEN_PINNED_APPLY_LAUNCHER = (
    b"#!/usr/bin/python3 -E\n"
    b"# triad-codex-dispatch managed repair apply launcher\n"
    b"import os\n"
    b"import sys\n"
    b"env = os.environ.copy()\n"
    b'env["TRIAD_CLASSIFIER_EXTENSION"] = "/managed/classifier.json"\n'
    b"os.execve('/usr/bin/python3', ['/usr/bin/python3', '-E', "
    b"'/managed/apply_patch.py'] + sys.argv[1:], env)\n"
)
FROZEN_LEGACY_SHELL_ENTRY = (
    b"# >>> triad-codex-dispatch codex-triad >>>\n"
    b"# Managed by triad-codex-dispatch scripts/bootstrap.sh --install;\n"
    b"# removed by --remove. Legacy prompt-reviewed posture: wrapper root\n"
    b"# containment + hardened wrapper mode + enforced claude sandbox.\n"
    b"codex-triad() {\n"
    b'  TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}" \\\n'
    b"  TRIAD_WRAPPER_HARDENED=1 \\\n"
    b"  TRIAD_CLAUDE_ENFORCE_SANDBOX=1 \\\n"
    b'    command codex --profile triad-codex-dispatch --search "$@"\n'
    b"}\n"
    b"# <<< triad-codex-dispatch codex-triad <<<\n"
)
FROZEN_LEGACY_PROFILE = b"""# triad-codex-dispatch managed runtime profile
# Generated by scripts/bootstrap.sh --install.
# Re-run with TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 to refresh.
# Explicit external-CLI consent profile: triad dispatch may send relevant
# prompt/repo review material to authenticated claude, agy, and gemini CLIs.
# Permission-profile system (developers.openai.com/codex/permissions).
# Do NOT reintroduce legacy sandbox_mode / [sandbox_workspace_write] in this
# or any loaded config layer: legacy sandbox settings disable
# default_permissions, which would neutralize the triad_leader permission
# profile's scoping.

approval_policy = "on-request"
approvals_reviewer = "auto_review"
default_permissions = "triad_leader"

[permissions.triad_leader]
description = "Triad leader session: workspace writes plus triad runtime dirs; network on."
extends = ":workspace"

[permissions.triad_leader.filesystem]
# --- SEC-3 exec-target write-denies (wrapper .py / launchers / python3 / vendor CLIs) ---
"/opt/triad-codex-dispatch/bin" = "read"
"/Users/example/.local/bin" = "read"
"/opt/homebrew/opt/python@3.12/bin/python3.12" = "read"
"/usr/local/bin/claude" = "read"
"/usr/local/bin/agy" = "read"
# --- re-allows: log_dir/debug_dir are nested under bin_dir (more-specific-wins survives that deny); classifier_dir is a separate, non-nested directory allowed independently ---
"/Users/example/.config/triad-codex-dispatch" = "write"
"/opt/triad-codex-dispatch/bin/_logs" = "write"
"/opt/triad-codex-dispatch/bin/_debug" = "write"

[permissions.triad_leader.network]
enabled = true
"""
FROZEN_LEGACY_RULES = b"""# triad-codex-dispatch managed command rules
# Generated by scripts/bootstrap.sh --install.
# Re-run with TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 to refresh.
# These rules prompt on wrapper-specific command prefixes for approval review.
# They do not allow broad shell entrypoints such as bash -lc or zsh -lc.

prefix_rule(
    pattern = [["/Users/example/.local/bin/claude_wrapper.py"]],
    decision = "prompt",
    justification = "Require approval review; approve only an owner-authorized triad review through the Claude wrapper when the worktree, scope, and named provider match the owner's request and provider-visible input excludes credentials, tokens, cookies, authentication files, environment dumps, provider logs, and unrelated paths. This does not authorize commit, push, install, merge, or release.",
    match = [
        "/Users/example/.local/bin/claude_wrapper.py --prompt hi --sandbox read-only",
        "/Users/example/.local/bin/claude_wrapper.py --prompt-file /opt/triad-codex-dispatch/_runs/prompts/triad-prompt.txt --sandbox read-only",
    ],
    not_match = [
        "claude_wrapper.py --prompt hi --sandbox read-only",
        "/opt/triad-codex-dispatch/bin/claude_wrapper.py --prompt hi --sandbox read-only",
        "bash -lc claude_wrapper.py --prompt hi",
        "zsh -lc claude_wrapper.py --prompt hi",
        "python3 /opt/triad-codex-dispatch/bin/claude_wrapper.py --prompt hi --sandbox read-only",
        "/usr/bin/env python3 /opt/triad-codex-dispatch/bin/claude_wrapper.py --prompt hi --sandbox read-only",
        "python3 -c print('not a triad wrapper')",
    ],
)

prefix_rule(
    pattern = [["/Users/example/.local/bin/antigravity_wrapper.py"]],
    decision = "prompt",
    justification = "Require approval review; approve only an owner-authorized triad review through the Antigravity wrapper when the worktree, scope, and named provider match the owner's request and provider-visible input excludes credentials, tokens, cookies, authentication files, environment dumps, provider logs, and unrelated paths. This does not authorize commit, push, install, merge, or release.",
    match = [
        "/Users/example/.local/bin/antigravity_wrapper.py --prompt hi --sandbox read-only",
        "/Users/example/.local/bin/antigravity_wrapper.py --prompt-file /opt/triad-codex-dispatch/_runs/prompts/triad-prompt.txt --sandbox read-only",
    ],
    not_match = [
        "antigravity_wrapper.py --prompt hi --sandbox read-only",
        "/opt/triad-codex-dispatch/bin/antigravity_wrapper.py --prompt hi --sandbox read-only",
        "bash -lc antigravity_wrapper.py --prompt hi",
        "zsh -lc antigravity_wrapper.py --prompt hi",
        "python3 /opt/triad-codex-dispatch/bin/antigravity_wrapper.py --prompt hi --sandbox read-only",
        "/usr/bin/env python3 /opt/triad-codex-dispatch/bin/antigravity_wrapper.py --prompt hi --sandbox read-only",
        "python3 -c print('not a triad wrapper')",
    ],
)

prefix_rule(
    pattern = [["/Users/example/.local/bin/gemini_wrapper.py"]],
    decision = "prompt",
    justification = "Require approval review; approve only an owner-authorized triad review through the Gemini business-tier wrapper when the worktree, scope, and named provider match the owner's request and provider-visible input excludes credentials, tokens, cookies, authentication files, environment dumps, provider logs, and unrelated paths. This does not authorize commit, push, install, merge, or release.",
    match = [
        "/Users/example/.local/bin/gemini_wrapper.py --prompt hi --sandbox read-only",
        "/Users/example/.local/bin/gemini_wrapper.py --prompt-file /opt/triad-codex-dispatch/_runs/prompts/triad-prompt.txt --sandbox read-only",
    ],
    not_match = [
        "gemini_wrapper.py --prompt hi --sandbox read-only",
        "/opt/triad-codex-dispatch/bin/gemini_wrapper.py --prompt hi --sandbox read-only",
        "bash -lc gemini_wrapper.py --prompt hi",
        "zsh -lc gemini_wrapper.py --prompt hi",
        "python3 /opt/triad-codex-dispatch/bin/gemini_wrapper.py --prompt hi --sandbox read-only",
        "/usr/bin/env python3 /opt/triad-codex-dispatch/bin/gemini_wrapper.py --prompt hi --sandbox read-only",
        "python3 -c print('not a triad wrapper')",
    ],
)
"""


def _load_bootstrap_repair_module():
    spec = importlib.util.spec_from_file_location("bootstrap_repair_test", BOOTSTRAP_REPAIR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _seed_frozen_legacy_repair_state(
    helper,
    tmp_path: Path,
    *,
    launcher_bytes: bytes = FROZEN_PINNED_APPLY_LAUNCHER,
    existing_config: bool = False,
) -> tuple[list[str], Path, Path, Path]:
    analyzer = tmp_path / "agents" / f"{REPAIR_ANALYZER}.toml"
    analyzer.parent.mkdir(parents=True, exist_ok=True)
    analyzer.write_bytes(FROZEN_REPAIR_ANALYZER)
    config = tmp_path / "config.toml"
    prefix = 'owner = "preserved"\n\n' if existing_config else ""
    config.write_text(
        prefix
        + f"{helper.REG_BEGIN}\n"
        + f"# original config existed = {'true' if existing_config else 'false'}\n"
        + f"[agents.{REPAIR_ANALYZER}]\n"
        + f"description = {json.dumps(helper.REG_DESCRIPTION)}\n"
        + f"config_file = {json.dumps(str(analyzer), ensure_ascii=False)}\n"
        + f"{helper.REG_END}\n",
        encoding="utf-8",
    )
    launcher = tmp_path / "triad-apply-repair"
    launcher.write_bytes(launcher_bytes)
    launcher.chmod(0o755)
    args = [
        "remove",
        "--config",
        str(config),
        "--analyzer",
        str(analyzer),
        "--launcher",
        str(launcher),
    ]
    return args, analyzer, config, launcher


def _owner_apply_argv(stdout: str) -> tuple[list[str], list[str]]:
    line = next(
        line for line in stdout.splitlines() if line.startswith("owner apply argv: ")
    )
    outer = shlex.split(line.removeprefix("owner apply argv: "))
    assert outer[:2] == ["/bin/zsh", "-lic"]
    assert len(outer) == 3
    return outer, shlex.split(outer[2])


def _legacy_shell_entry_for_profile(profile: str) -> bytes:
    return FROZEN_LEGACY_SHELL_ENTRY.replace(
        b"--profile triad-codex-dispatch", f"--profile {profile}".encode("ascii")
    )


def _path_state_fingerprint(path: Path):
    try:
        current = os.lstat(path)
    except FileNotFoundError:
        return ("absent",)
    mode = stat.S_IMODE(current.st_mode)
    if stat.S_ISLNK(current.st_mode):
        return ("symlink", mode, os.readlink(path))
    if stat.S_ISREG(current.st_mode):
        return ("file", mode, path.read_bytes())
    if stat.S_ISDIR(current.st_mode):
        entries = tuple(
            sorted(
                (entry.name, stat.S_IFMT(os.lstat(entry).st_mode))
                for entry in path.iterdir()
            )
        )
        return ("directory", mode, entries)
    return ("non-regular", mode, current.st_size, current.st_rdev)


def _install_target_fingerprint(paths: tuple[Path, ...]):
    return {path: _path_state_fingerprint(path) for path in paths}


def _would_be_install_targets(
    tmp_path: Path,
    repo_root: Path,
    codex_home: Path,
    classifier: Path,
    shell_rc: Path,
    *extra_paths: Path,
) -> tuple[Path, ...]:
    launcher_dir = tmp_path / "launchers"
    return (
        launcher_dir,
        *(launcher_dir / name for name in (
            "claude_wrapper.py",
            "gemini_wrapper.py",
            "antigravity_wrapper.py",
            "triad-apply-repair",
        )),
        repo_root / "bin",
        repo_root / "bin" / "_logs",
        codex_home,
        codex_home / "config.toml",
        codex_home / "agents",
        codex_home / "agents" / f"{REPAIR_ANALYZER}.toml",
        *(codex_home / "agents" / name for name in (
            "claude-wrapper-repair.toml",
            "gemini-wrapper-repair.toml",
            "agy-wrapper-repair.toml",
        )),
        codex_home / "rules",
        codex_home / "rules" / "triad-codex-dispatch.rules",
        codex_home / "triad-codex-dispatch.config.toml",
        classifier.parent,
        classifier,
        shell_rc,
        *extra_paths,
    )


def _seed_managed_legacy_repair_agent(codex_home: Path) -> Path:
    legacy_agent = codex_home / "agents" / "claude-wrapper-repair.toml"
    legacy_agent.parent.mkdir(parents=True, exist_ok=True)
    legacy_agent.write_bytes(MANAGED_LEGACY_REPAIR_AGENT)
    return legacy_agent


def test_native_install_does_not_create_codex_permission_state(
    tmp_path: Path,
) -> None:
    result, env, _launcher_dir = _run_bootstrap(tmp_path, arg="--install")
    codex_home = Path(env["HOME"]) / ".codex"

    assert result.returncode == 0, result.stderr
    assert not (codex_home / "triad-codex-dispatch.config.toml").exists()
    assert not (codex_home / "rules" / "triad-codex-dispatch.rules").exists()
    assert not (codex_home / "agents" / "triad-repair-analyzer.toml").exists()
    config = codex_home / "config.toml"
    assert not config.exists() or "triad-codex-dispatch managed" not in config.read_text()


def test_native_install_emits_no_permission_environment_controls(
    tmp_path: Path,
) -> None:
    shell_rc = tmp_path / "shell rc"
    shell_rc.write_text("# owner shell rc\n", encoding="utf-8")
    result, env, launcher_dir = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc)},
    )

    assert result.returncode == 0, result.stderr
    produced = [*launcher_dir.iterdir(), shell_rc]
    codex_home = Path(env["HOME"]) / ".codex"
    if codex_home.exists():
        produced.extend(path for path in codex_home.rglob("*") if path.is_file())
    for path in produced:
        text = path.read_text(encoding="utf-8")
        assert "TRIAD_CLAUDE_ENFORCE_SANDBOX" not in text
        assert "TRIAD_WRAPPER_HARDENED" not in text


def test_permission_environment_control_producers_are_removed() -> None:
    text = BOOTSTRAP_REPAIR.read_text(encoding="utf-8")

    assert "TRIAD_CLAUDE_ENFORCE_SANDBOX" not in text
    assert "TRIAD_WRAPPER_HARDENED" not in text
    assert "def _shell_entry_block(" not in text


def test_bootstrap_source_contains_no_retired_permission_controller_names() -> None:
    text = BOOTSTRAP.read_text(encoding="utf-8")

    assert "install_codex_rules" not in text


def test_bootstrap_help_describes_google_route_fallback() -> None:
    result = subprocess.run(
        ["bash", str(BOOTSTRAP), "--help"],
        text=True,
        capture_output=True,
        timeout=5,
    )

    assert result.returncode == 2
    help_text = " ".join(result.stderr.split())
    assert "agy, or configured Gemini Enterprise/Business" in help_text
    assert "same authenticated login terminal" in help_text
    assert "inherits provider permissions" in help_text
    assert "does not install or inject a separate Codex profile" in help_text
    assert "Agent Review" not in help_text
    assert "granular.rules" not in help_text
    assert "granular.sandbox_approval" not in help_text


def test_bootstrap_usage_omits_retired_permission_install_flags() -> None:
    result = subprocess.run(
        ["bash", str(BOOTSTRAP), "--invalid-option"],
        text=True,
        capture_output=True,
        timeout=5,
    )

    assert result.returncode == 2
    help_text = " ".join(result.stderr.split())
    assert "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE" not in help_text
    assert "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY" not in help_text
    assert "TRIAD_WRAPPER_HARDENED" not in help_text
    assert "TRIAD_CLAUDE_ENFORCE_SANDBOX" not in help_text
    assert "provider launcher group" in help_text
    assert "same authenticated login terminal" in help_text


def test_bootstrap_repair_help_exposes_remove_only_repair_lifecycle() -> None:
    helper = _load_bootstrap_repair_module()
    choices = next(
        action.choices
        for action in helper.parser()._actions
        if isinstance(action, helper.argparse._SubParsersAction)
    )

    assert "install" not in choices
    assert "preflight-install" not in choices
    assert "remove" in choices
    assert "preflight-remove" in choices
    assert "commands-install" in choices
    assert "commands-remove" in choices


def test_frozen_repair_analyzer_fixture_matches_production_digest() -> None:
    helper = _load_bootstrap_repair_module()

    assert hashlib.sha256(FROZEN_REPAIR_ANALYZER).hexdigest() == (
        helper.FROZEN_REPAIR_ANALYZER_SHA256
    )


def test_apply_patch_requires_explicit_absolute_classifier_file(tmp_path: Path) -> None:
    proposal = tmp_path / "proposal.json"
    proposal.write_text(
        json.dumps(
            {
                "classification": "server-capacity",
                "reason": "Stable capacity signal.",
                "pattern_list": "SERVER_CAPACITY_PATTERNS",
                "substring": "service capacity temporarily exhausted",
            }
        ),
        encoding="utf-8",
    )
    fresh_home = tmp_path / "fresh-home"
    fresh_config = tmp_path / "fresh-config"
    env = {
        **os.environ,
        "HOME": str(fresh_home),
        "XDG_CONFIG_HOME": str(fresh_config),
    }

    def invoke(*extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(APPLY_PATCH),
                "--cli",
                "claude",
                *extra,
                "--proposal-file",
                str(proposal),
            ],
            text=True,
            capture_output=True,
            env=env,
            timeout=5,
        )

    missing = invoke()
    relative = invoke("--classifier-file", "relative.json")
    tilde = invoke("--classifier-file", "~/classifier.json")

    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    symlinked_parent = tmp_path / "linked-parent"
    symlinked_parent.symlink_to(real_parent, target_is_directory=True)
    ancestor = invoke("--classifier-file", str(symlinked_parent / "classifier.json"))

    leaf_target = tmp_path / "leaf-target.json"
    leaf_target.write_text('{"owner": true}\n', encoding="utf-8")
    symlinked_leaf = tmp_path / "classifier-link.json"
    symlinked_leaf.symlink_to(leaf_target)
    leaf = invoke("--classifier-file", str(symlinked_leaf))

    for refused in (missing, relative, tilde, ancestor, leaf):
        assert refused.returncode != 0
    assert leaf_target.read_text(encoding="utf-8") == '{"owner": true}\n'
    assert not (real_parent / "classifier.json").exists()
    assert not (tmp_path / "relative.json").exists()
    assert not (fresh_home / "classifier.json").exists()

    classifier = tmp_path / "custom" / "classifier.json"
    classifier.parent.mkdir()
    applied = invoke("--classifier-file", str(classifier))

    assert applied.returncode == 0, applied.stderr
    data = json.loads(classifier.read_text(encoding="utf-8"))
    assert data["claude"]["patterns"]["SERVER_CAPACITY_PATTERNS"] == [
        "service capacity temporarily exhausted"
    ]
    assert not (fresh_config / "triad-codex-dispatch" / "classifier-patches.json").exists()


def test_apply_patch_rejects_parent_traversal_before_proposal_read(
    tmp_path: Path,
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    linked = tmp_path / "linked"
    linked.symlink_to(outside, target_is_directory=True)
    classifier = tmp_path / "missing" / ".." / "linked" / "classifier.json"
    missing_proposal = tmp_path / "proposal-does-not-exist.json"

    result = subprocess.run(
        [
            sys.executable,
            str(APPLY_PATCH),
            "--cli",
            "claude",
            "--classifier-file",
            str(classifier),
            "--proposal-file",
            str(missing_proposal),
        ],
        text=True,
        capture_output=True,
        timeout=5,
    )

    assert result.returncode == 3
    assert "classifier path must not contain parent traversal" in result.stderr
    assert "cannot read proposal" not in result.stderr
    assert not (outside / "classifier.json").exists()
    assert not (tmp_path / "missing").exists()


def test_bootstrap_prints_owner_apply_argv_with_pinned_classifier(
    tmp_path: Path,
) -> None:
    classifier = tmp_path / "config with spaces" / "classifier '$() `'.json"
    result, env, launcher_dir = _run_bootstrap(
        tmp_path,
        env_overrides={"TRIAD_CLASSIFIER_EXTENSION": str(classifier)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    _outer, owner = _owner_apply_argv(result.stdout)
    assert owner[:2] == [
        "python3",
        str(Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]) / "bin" / "apply_patch.py"),
    ]
    classifier_index = owner.index("--classifier-file")
    assert owner[classifier_index + 1] == str(classifier)
    for wrapper in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        launcher = (launcher_dir / wrapper).read_text(encoding="utf-8")
        assert json.dumps(str(classifier), ensure_ascii=False) in launcher


@pytest.mark.parametrize(
    "launcher_bytes",
    (FROZEN_LEGACY_APPLY_LAUNCHER, FROZEN_PINNED_APPLY_LAUNCHER),
)
def test_install_removes_only_exact_legacy_repair_agent_artifacts(
    tmp_path: Path,
    launcher_bytes: bytes,
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    helper = _load_bootstrap_repair_module()
    codex_home = tmp_path / "home" / ".codex"
    args, analyzer, config, seeded_launcher = _seed_frozen_legacy_repair_state(
        helper,
        codex_home,
        launcher_bytes=launcher_bytes,
    )
    launcher = tmp_path / "launchers" / "triad-apply-repair"
    launcher.parent.mkdir()
    seeded_launcher.replace(launcher)
    args[args.index(str(seeded_launcher))] = str(launcher)
    foreign = analyzer.parent / "foreign.toml"
    foreign.write_text('name = "foreign"\n', encoding="utf-8")

    result, _env, _launcher_dir = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        env_overrides={"CODEX_HOME": str(codex_home)},
        arg="--install",
    )

    assert result.returncode == 0, result.stderr + result.stdout
    config_text = config.read_text(encoding="utf-8") if config.exists() else ""
    _before, _after, had_registration, _original_existed = helper.split_registration(
        config_text, config, analyzer
    )
    assert not had_registration
    assert not analyzer.exists()
    assert not launcher.exists()
    assert foreign.read_text(encoding="utf-8") == 'name = "foreign"\n'


def test_bootstrap_routes_classifier_artifacts_and_config_mutations_through_helper() -> None:
    text = BOOTSTRAP.read_text(encoding="utf-8")

    assert "bootstrap_repair.py\" classifier" in text
    assert "bootstrap_repair.py\" config-fragment" in text
    assert "profile_path.write_text" not in text
    assert "rules_path.write_text" not in text
    assert "Path(str(config_path) + \".bak\").write_bytes" not in text
    assert "os.replace(tmp_name, config_path)" not in text
    assert "runtime_command_is_managed()" not in text
    assert "config_path.unlink()" not in text




def test_bootstrap_repair_refuses_exact_analyzer_marker_inside_multiline_string(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, _config, _launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    foreign = (
        'name = "foreign-analyzer"\n'
        'description = """\n'
        f"{helper.ANALYZER_MARKER}\n"
        'still foreign\n"""\n'
    )
    analyzer.write_text(foreign, encoding="utf-8")

    assert not helper.analyzer_is_managed(helper.read_state(analyzer))
    assert helper.main(args) == 0
    assert analyzer.read_text(encoding="utf-8") == foreign


def test_bootstrap_repair_preserves_and_reports_owner_edited_frozen_analyzer(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, _config, launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    owner_edited = analyzer.read_bytes() + b"# owner edit\n"
    analyzer.write_bytes(owner_edited)

    assert not helper.analyzer_is_managed(helper.read_state(analyzer))
    assert helper.main(args) == 0
    assert analyzer.read_bytes() == owner_edited
    assert not launcher.exists()
    assert "preserving unmanaged repair analyzer" in capsys.readouterr().err


@pytest.mark.parametrize(
    "launcher_bytes",
    (
        FROZEN_LEGACY_APPLY_LAUNCHER.replace(
            b"/managed/apply_patch.py", b"/managed/owner.py"
        ),
        FROZEN_PINNED_APPLY_LAUNCHER.replace(
            b'"/managed/classifier.json"',
            b'"/managed/classifier.json" + ".owner"',
        ),
    ),
)
def test_bootstrap_repair_preserves_and_reports_owner_edited_legacy_launcher(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    launcher_bytes: bytes,
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, _config, launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path, launcher_bytes=launcher_bytes
    )

    assert not helper.launcher_is_managed(helper.read_state(launcher))
    assert helper.main(args) == 0
    assert launcher.read_bytes() == launcher_bytes
    assert not analyzer.exists()
    assert "preserving unmanaged repair apply launcher" in capsys.readouterr().err


def test_bootstrap_repair_refuses_exact_launcher_marker_inside_python_multiline_string(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    args, _analyzer, _config, launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    foreign = f'payload = """\n{helper.LAUNCHER_MARKER}\nstill foreign\n"""\n'
    launcher.write_text(foreign, encoding="utf-8")

    assert not helper.launcher_is_managed(helper.read_state(launcher))
    assert helper.main(args) == 0
    assert launcher.read_text(encoding="utf-8") == foreign


def test_bootstrap_repair_preserves_exact_registration_block_inside_multiline_string(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, config, _launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    foreign = (
        'description = """\n'
        + helper.registration_block(analyzer, True)
        + '"""\n'
    ).encode("utf-8")
    config.write_bytes(foreign)

    assert helper.main(args) == 0
    assert config.read_bytes() == foreign


def test_bootstrap_repair_refuses_noncanonical_marker_wrapped_registration(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    args, _analyzer, config, _launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    foreign = (
        f"{helper.REG_BEGIN}\n"
        f"[agents.{REPAIR_ANALYZER}]\n"
        'description = "foreign"\n'
        'config_file = "/foreign/analyzer.toml"\n'
        f"{helper.REG_END}\n"
    ).encode("utf-8")
    config.write_bytes(foreign)

    assert helper.main(args) == 3
    assert config.read_bytes() == foreign






def test_bootstrap_repair_preserves_foreign_swap_between_check_and_remove(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "target"
    target.write_bytes(b"managed-before\n")
    before = helper.read_state(target)
    assert before is not None
    foreign = b"foreign-between-check-and-remove\n"
    original_same = helper.same
    injected = False

    def swap_after_successful_check(state):
        nonlocal injected
        matched = original_same(state)
        if state.path == target and matched and not injected:
            injected = True
            target.write_bytes(foreign)
        return matched

    monkeypatch.setattr(helper, "same", swap_after_successful_check)
    with pytest.raises(helper.Refusal):
        helper.remove_state(before, [])

    assert injected
    assert target.read_bytes() == foreign
    assert not list(tmp_path.glob(".*.triad-claim-*"))








def test_provider_launchers_and_owner_apply_share_custom_classifier_in_a_fresh_environment(
    tmp_path: Path,
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    shutil.copy2(APPLY_PATCH, repo_root / "bin" / "apply_patch.py")
    shutil.copy2(ROOT / "bin" / "_common.py", repo_root / "bin" / "_common.py")
    (repo_root / "bin" / "apply_patch.py").chmod(0o755)
    classifier = tmp_path / "config with spaces" / "classifier '$() `'.json"
    probe = (
        "#!/usr/bin/env python3\n"
        "import os\n"
        "print(os.environ['TRIAD_CLASSIFIER_EXTENSION'])\n"
    )
    provider_path = repo_root / "bin" / "gemini_wrapper.py"
    provider_path.write_text(probe, encoding="utf-8")
    provider_path.chmod(0o755)
    result, env, launcher_dir = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        env_overrides={"TRIAD_CLASSIFIER_EXTENSION": str(classifier)},
    )
    assert result.returncode == 0, result.stderr + result.stdout
    fresh_env = {
        "HOME": str(tmp_path / "different-home"),
        "PATH": env["PATH"],
        "XDG_CONFIG_HOME": str(tmp_path / "different-config"),
    }

    provider = subprocess.run(
        [str(launcher_dir / "gemini_wrapper.py")],
        env=fresh_env,
        text=True,
        capture_output=True,
        check=False,
    )
    _outer, owner = _owner_apply_argv(result.stdout)
    proposal = tmp_path / "proposal.json"
    proposal.write_text(
        json.dumps(
            {
                "classification": "server-capacity",
                "reason": "Stable capacity signal.",
                "pattern_list": "SERVER_CAPACITY_PATTERNS",
                "substring": "service capacity temporarily exhausted",
            }
        ),
        encoding="utf-8",
    )
    owner[owner.index("<cli>")] = "claude"
    owner[owner.index("<absolute-proposal-path>")] = str(proposal)
    apply = subprocess.run(
        ["/bin/zsh", "-lic", shlex.join(owner)],
        env=fresh_env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert provider.returncode == 0, provider.stderr
    assert apply.returncode == 0, apply.stderr
    assert provider.stdout.strip() == str(classifier)
    assert apply.stdout.strip() == "applied"
    assert json.loads(classifier.read_text(encoding="utf-8"))["claude"]
    assert not (
        Path(fresh_env["XDG_CONFIG_HOME"])
        / "triad-codex-dispatch"
        / "classifier-patches.json"
    ).exists()


def test_bootstrap_repair_rejects_whitespace_python_shebang() -> None:
    helper = _load_bootstrap_repair_module()

    with pytest.raises(helper.Refusal, match="shebang cannot encode"):
        helper.portable_python_shebang(Path("/tmp/python runtime/bin/python3"))


def test_bootstrap_repair_reports_remove_only_success_status(tmp_path: Path) -> None:
    helper = _load_bootstrap_repair_module()
    removed = helper.main(
        ["remove", "--config", str(tmp_path / "config"), "--analyzer", str(tmp_path / "analyzer"),
         "--launcher", str(tmp_path / "launcher")]
    )

    assert removed == 0


def test_bootstrap_repair_keeps_foreign_registration_but_removes_managed_launcher(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    config = tmp_path / "config.toml"
    foreign = (
        f"[agents.{REPAIR_ANALYZER}]\n"
        'description = "foreign"\nconfig_file = "/foreign/agent.toml"\n'
    )
    config.write_text(foreign, encoding="utf-8")
    launcher = tmp_path / "triad-apply-repair"
    launcher.write_bytes(FROZEN_LEGACY_APPLY_LAUNCHER)

    status = helper.main(
        ["remove", "--config", str(config), "--analyzer", str(tmp_path / "analyzer"),
         "--launcher", str(launcher)]
    )

    assert status == 0
    assert config.read_text(encoding="utf-8") == foreign
    assert not launcher.exists()


def test_bootstrap_repair_keeps_marker_bearing_analyzer_for_foreign_registration(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    analyzer = tmp_path / "agents" / f"{REPAIR_ANALYZER}.toml"
    analyzer.parent.mkdir()
    analyzer_bytes = (
        f"{helper.ANALYZER_MARKER}\nname = \"{REPAIR_ANALYZER}\"\n"
    ).encode("utf-8")
    analyzer.write_bytes(analyzer_bytes)
    config = tmp_path / "config.toml"
    config_bytes = (
        f"[agents.{REPAIR_ANALYZER}]\n"
        'description = "foreign"\n'
        f'config_file = "{analyzer}"\n'
    ).encode("utf-8")
    config.write_bytes(config_bytes)

    assert helper.main(
        ["remove", "--config", str(config), "--analyzer", str(analyzer),
         "--launcher", str(tmp_path / "missing-launcher")]
    ) == 0
    assert config.read_bytes() == config_bytes
    assert analyzer.read_bytes() == analyzer_bytes


def test_bootstrap_repair_restores_pair_when_launcher_removal_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, config, launcher = _seed_frozen_legacy_repair_state(
        helper,
        tmp_path,
    )
    original_remove = helper.remove_state

    def fail_launcher(state, journal):
        if state.path == launcher:
            raise OSError("injected launcher removal failure")
        original_remove(state, journal)

    monkeypatch.setattr(helper, "remove_state", fail_launcher)
    assert helper.main(args) == 3
    assert analyzer.exists()
    assert REPAIR_ANALYZER in tomllib.loads(config.read_text(encoding="utf-8"))["agents"]








def test_bootstrap_repair_rolls_back_unlink_when_parent_fsync_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, config, launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    before = config.read_bytes()
    original_fsync = helper.fsync_parent
    failed = False

    def fail_config(path):
        nonlocal failed
        if path == config and not failed:
            failed = True
            raise OSError("injected config unlink fsync failure")
        original_fsync(path)

    monkeypatch.setattr(helper, "fsync_parent", fail_config)
    assert helper.main(args) == 3
    assert config.read_bytes() == before
    assert analyzer.exists()
    assert launcher.exists()


def test_bootstrap_repair_rollback_preserves_foreign_create_after_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, config, launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    original_fsync = helper.fsync_parent
    failed = False
    foreign = b"foreign config created after unlink\n"

    def create_config_then_fail(path):
        nonlocal failed
        if path == config and not failed:
            failed = True
            config.write_bytes(foreign)
            raise OSError("injected config unlink fsync failure after foreign create")
        original_fsync(path)

    monkeypatch.setattr(helper, "fsync_parent", create_config_then_fail)
    assert helper.main(args) == 3
    assert config.read_bytes() == foreign
    assert analyzer.exists()
    assert launcher.exists()


def test_bootstrap_repair_remove_revalidates_absence_after_successful_parent_fsync(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "managed"
    target.write_bytes(b"managed before unlink\n")
    before = helper.read_state(target)
    assert before is not None
    foreign = b"foreign created during parent fsync\n"
    journal = []

    def create_foreign_and_succeed(path):
        assert path == target
        target.write_bytes(foreign)

    monkeypatch.setattr(helper, "fsync_parent", create_foreign_and_succeed)
    with pytest.raises(helper.Refusal, match="could not remove path"):
        helper.remove_state(before, journal)

    assert len(journal) == 1
    assert journal[0].after is None
    assert target.read_bytes() == foreign


def test_bootstrap_repair_restores_registration_when_analyzer_removal_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, config, launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    config_before = config.read_bytes()
    analyzer_before = analyzer.read_bytes()
    launcher_before = launcher.read_bytes()
    original_remove = helper.remove_state

    def fail_analyzer_removal(state, journal):
        if state.path == analyzer:
            raise OSError("injected analyzer removal failure")
        return original_remove(state, journal)

    monkeypatch.setattr(helper, "remove_state", fail_analyzer_removal)
    assert helper.main(args) == 3
    assert config.read_bytes() == config_before
    assert analyzer.read_bytes() == analyzer_before
    assert launcher.read_bytes() == launcher_before










def test_bootstrap_repair_stage_fsync_failure_does_not_mask_error_or_leak(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "target"
    monkeypatch.setattr(helper.os, "fsync", lambda _fd: (_ for _ in ()).throw(OSError("stage fsync")))
    with pytest.raises(OSError, match="stage fsync"):
        helper.stage(target, b"data", 0o600)
    assert not list(tmp_path.glob(".*.tmp"))


def test_bootstrap_repair_stage_retries_one_shot_internal_cleanup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "target"
    original_unlink = helper.os.unlink
    unlink_calls = 0

    def fail_unlink_once(path):
        nonlocal unlink_calls
        unlink_calls += 1
        if unlink_calls == 1:
            raise OSError("one-shot stage cleanup unlink failure")
        original_unlink(path)

    with monkeypatch.context() as patcher:
        patcher.setattr(
            helper.os,
            "fsync",
            lambda _fd: (_ for _ in ()).throw(OSError("stage fsync failed")),
        )
        patcher.setattr(helper.os, "unlink", fail_unlink_once)
        with pytest.raises(OSError, match="stage fsync failed"):
            helper.stage(target, b"data", 0o600)

    assert unlink_calls == 2
    assert not list(tmp_path.glob(".*.tmp"))


def test_bootstrap_repair_stage_reports_write_and_internal_cleanup_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "target"
    original_unlink = helper.os.unlink
    unlink_calls = 0

    def always_fail_unlink(_path):
        nonlocal unlink_calls
        unlink_calls += 1
        raise OSError("stage cleanup unlink failed")

    with monkeypatch.context() as patcher:
        patcher.setattr(
            helper.os,
            "fsync",
            lambda _fd: (_ for _ in ()).throw(OSError("stage fsync failed")),
        )
        patcher.setattr(
            helper.os,
            "unlink",
            always_fail_unlink,
        )
        with pytest.raises(helper.TransactionFailure) as captured:
            helper.stage(target, b"data", 0o600)

    assert "stage fsync failed" in str(captured.value)
    assert "stage cleanup unlink failed" in str(captured.value)
    assert unlink_calls == 2
    leaked = list(tmp_path.glob(".*.tmp"))
    assert len(leaked) == 1
    original_unlink(leaked[0])








@pytest.mark.parametrize("unsafe", ("analyzer", "launcher"))
def test_bootstrap_repair_remove_refuses_unsafe_artifact_before_config_mutation(
    tmp_path: Path, unsafe: str
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, config, launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    before = config.read_bytes()
    target = analyzer if unsafe == "analyzer" else launcher
    target.unlink()
    target.symlink_to(tmp_path / f"foreign-{unsafe}")

    assert helper.main(args) == 3
    assert config.read_bytes() == before
    assert target.is_symlink()


def test_bootstrap_repair_refuses_malformed_toml_inside_managed_markers(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, config, launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    malformed = (
        f"{helper.REG_BEGIN}\n[agents.{REPAIR_ANALYZER}]\nvalue = [\n{helper.REG_END}\n"
    ).encode("utf-8")
    config.write_bytes(malformed)
    status = helper.main(args)
    assert status == 3
    assert config.read_bytes() == malformed
    assert analyzer.exists() and launcher.exists()


@pytest.mark.parametrize(
    ("runtime", "expected_length", "accepted"),
    (
        (Path("/" + "a" * 249), 256, True),
        (Path("/" + "a" * 250), 257, False),
        (Path("/" + "가" * 80 + "a" * 9), 256, True),
        (Path("/" + "가" * 80 + "a" * 10), 257, False),
    ),
    ids=("ascii-256", "ascii-257", "multibyte-256", "multibyte-257"),
)
def test_portable_python_shebang_uses_filesystem_bytes_and_256_byte_limit(
    runtime: Path, expected_length: int, accepted: bool
) -> None:
    helper = _load_bootstrap_repair_module()
    expected = b"#!" + os.fsencode(runtime) + b" -E\n"
    assert len(expected) == expected_length

    if accepted:
        assert helper.portable_python_shebang(runtime) == expected
    else:
        with pytest.raises(helper.Refusal, match="exceeds 256 filesystem bytes"):
            helper.portable_python_shebang(runtime)


def test_bootstrap_repair_embedded_launcher_and_config_markers_are_foreign(tmp_path: Path) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, config, launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    launcher.write_text(f'comment = "{helper.LAUNCHER_MARKER}"\n', encoding="utf-8")
    config.write_text(
        f'description = "{helper.REG_BEGIN} {helper.REG_END}"\n', encoding="utf-8"
    )
    assert not helper.launcher_is_managed(helper.read_state(launcher))
    assert helper.main(args) == 0
    assert launcher.read_text(encoding="utf-8").startswith("comment")
    assert config.read_text(encoding="utf-8").startswith("description")


@pytest.mark.parametrize("original", (b"", b'title = "no final newline"'))
def test_bootstrap_repair_config_round_trips_existing_bytes_exactly(
    tmp_path: Path, original: bytes
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, config, _launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path, existing_config=True
    )
    block = helper.registration_block(analyzer, True).encode("utf-8")
    config.write_bytes(original + b"\n" + block)

    assert helper.main(args) == 0
    assert config.exists()
    assert config.read_bytes() == original


def test_config_fragment_round_trips_owner_bytes_without_final_newline(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    config = tmp_path / "config.toml"
    original = b'title = "owner bytes without final newline"'
    config.write_bytes(
        original
        + helper.CONFIG_FRAGMENT_INSERTED_SEPARATOR
        + helper.current_config_fragment(b"\n")
    )

    assert helper.remove_config_fragment(config) == "removed"
    assert config.read_bytes() == original


def _assert_legacy_repair_state_absent(codex_home: Path) -> None:
    assert not (codex_home / "agents" / f"{REPAIR_ANALYZER}.toml").exists()
    config = codex_home / "config.toml"
    if config.exists():
        text = config.read_text(encoding="utf-8")
        assert "managed repair analyzer registration" not in text
        assert f"[agents.{REPAIR_ANALYZER}]" not in text


def test_default_install_keeps_ordinary_codex_and_installs_wrapper_launchers(
    tmp_path: Path,
) -> None:
    result, env, launcher_bin = _run_bootstrap(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    home = Path(env["HOME"])
    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    _assert_legacy_repair_state_absent(home / ".codex")
    assert (
        Path(env["XDG_CONFIG_HOME"])
        / "triad-codex-dispatch"
        / "classifier-patches.json"
    ).read_text(encoding="utf-8") == "{}\n"
    assert (repo_root / "bin" / "_logs").is_dir()
    profile = home / ".codex" / "triad-codex-dispatch.config.toml"
    assert not profile.exists()
    assert not (home / ".codex" / "rules" / "triad-codex-dispatch.rules").exists()
    for wrapper in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        assert (launcher_bin / wrapper).is_file()
    assert "launcher Python is installer-selected" in result.stdout
    assert "trusted HOME" in result.stdout
    assert "sitecustomize/usercustomize" in result.stdout
    assert "before launcher scrubbing" in result.stdout
    assert "trusted isolated Python" in result.stdout
    assert "preserves provider login" in result.stdout
    assert "codex-triad" not in result.stdout
    assert "native permissions" in result.stdout
    assert "Agent Review" not in result.stdout
    assert "granular.rules" not in result.stdout
    apply_launcher = launcher_bin / "triad-apply-repair"
    assert not apply_launcher.exists()
    _outer, owner = _owner_apply_argv(result.stdout)
    assert owner[0] == "python3"
    assert owner[1] == str(repo_root / "bin" / "apply_patch.py")




def test_default_install_preserves_owner_codex_config_bytes(tmp_path: Path) -> None:
    codex_home = tmp_path / "owner-codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    original = (
        'approval_policy = "on-request"\n'
        'approvals_reviewer = "auto_review"\n'
    )
    config.write_text(original, encoding="utf-8")

    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert config.read_text(encoding="utf-8") == original
    assert not (codex_home / "triad-codex-dispatch.config.toml").exists()
    assert not (codex_home / "rules" / "triad-codex-dispatch.rules").exists()
    assert not (codex_home / "agents" / f"{REPAIR_ANALYZER}.toml").exists()
    assert "shell_environment_policy" not in config.read_text(encoding="utf-8")








def test_plain_install_removes_exact_managed_legacy_profile(
    tmp_path: Path,
) -> None:
    codex_home = tmp_path / "home" / ".codex"
    codex_home.mkdir(parents=True)
    profile = codex_home / "triad-codex-dispatch.config.toml"
    profile.write_bytes(FROZEN_LEGACY_PROFILE)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert str(profile) in result.stdout
    assert "removed Codex runtime profile" in result.stdout
    assert not profile.exists()


def test_plain_install_removes_exact_managed_legacy_rules(tmp_path: Path) -> None:
    codex_home = tmp_path / "home" / ".codex"
    rules = codex_home / "rules" / "triad-codex-dispatch.rules"
    rules.parent.mkdir(parents=True)
    rules.write_bytes(FROZEN_LEGACY_RULES)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert str(rules) in result.stdout
    assert "removed Codex command rules" in result.stdout
    assert not rules.exists()


@pytest.mark.parametrize("kind", ("profile", "rules"))
def test_managed_remove_preserves_marker_first_edited_legacy_policy(
    tmp_path: Path, kind: str
) -> None:
    helper = _load_bootstrap_repair_module()
    exact = FROZEN_LEGACY_PROFILE if kind == "profile" else FROZEN_LEGACY_RULES
    edited = exact + b"owner_edit = true\n"
    target = tmp_path / kind
    target.write_bytes(edited)

    assert helper.managed_removal_data_is_owned(exact, kind)
    assert not helper.managed_removal_data_is_owned(edited, kind)
    assert helper.remove_managed_artifact(target, kind) == "unmanaged"
    assert target.read_bytes() == edited


@pytest.mark.parametrize(
    ("variant", "edited"),
    (
        (
            "inserted-read",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/usr/local/bin/agy" = "read"\n',
                b'"/usr/local/bin/agy" = "read"\n"/owner/path" = "read"\n',
                1,
            ),
        ),
        (
            "inserted-write",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/opt/triad-codex-dispatch/bin/_debug" = "write"\n',
                b'"/opt/triad-codex-dispatch/bin/_debug" = "write"\n'
                b'"/owner/path" = "write"\n',
                1,
            ),
        ),
        (
            "reordered-core-slots",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/opt/triad-codex-dispatch/bin" = "read"\n'
                b'"/Users/example/.local/bin" = "read"\n',
                b'"/Users/example/.local/bin" = "read"\n'
                b'"/opt/triad-codex-dispatch/bin" = "read"\n',
                1,
            ),
        ),
        (
            "reordered-vendor-subsequence",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/usr/local/bin/claude" = "read"\n'
                b'"/usr/local/bin/agy" = "read"\n',
                b'"/usr/local/bin/agy" = "read"\n'
                b'"/usr/local/bin/claude" = "read"\n',
                1,
            ),
        ),
        (
            "inconsistent-log-parent",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/opt/triad-codex-dispatch/bin/_logs" = "write"',
                b'"/owner/bin/_logs" = "write"',
                1,
            ),
        ),
        (
            "inconsistent-debug-parent",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/opt/triad-codex-dispatch/bin/_debug" = "write"',
                b'"/owner/bin/_debug" = "write"',
                1,
            ),
        ),
        (
            "parent-traversal",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/Users/example/.local/bin" = "read"',
                b'"/Users/example/.local/../bin" = "read"',
                1,
            ),
        ),
        (
            "noncanonical-double-separator",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/Users/example/.config/triad-codex-dispatch" = "write"',
                b'"/Users/example//.config/triad-codex-dispatch" = "write"',
                1,
            ),
        ),
        (
            "noncanonical-double-root",
            FROZEN_LEGACY_PROFILE.replace(
                b"/opt/triad-codex-dispatch/bin",
                b"//opt/triad-codex-dispatch/bin",
            ),
        ),
        (
            "broad-root-fallback-file-shape",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/opt/triad-codex-dispatch/bin" = "read"',
                b'"/opt/triad-codex-dispatch/bin/_common.py" = "read"',
                1,
            ),
        ),
        (
            "slot-collision",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/Users/example/.local/bin" = "read"',
                b'"/opt/triad-codex-dispatch/bin" = "read"',
                1,
            ),
        ),
        (
            "unknown-vendor-basename",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/usr/local/bin/agy" = "read"',
                b'"/usr/local/bin/owner-tool" = "read"',
                1,
            ),
        ),
        (
            "unknown-python-basename",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/opt/homebrew/opt/python@3.12/bin/python3.12" = "read"',
                b'"/opt/homebrew/opt/python@3.12/bin/python3.owner" = "read"',
                1,
            ),
        ),
        (
            "duplicate-vendor-slot",
            FROZEN_LEGACY_PROFILE.replace(
                b'"/usr/local/bin/agy" = "read"\n',
                b'"/usr/local/bin/agy" = "read"\n'
                b'"/opt/alternate/agy" = "read"\n',
                1,
            ),
        ),
    ),
    ids=(
        "inserted-read",
        "inserted-write",
        "reordered-core-slots",
        "reordered-vendor-subsequence",
        "inconsistent-log-parent",
        "inconsistent-debug-parent",
        "parent-traversal",
        "noncanonical-double-separator",
        "noncanonical-double-root",
        "broad-root-fallback-file-shape",
        "slot-collision",
        "unknown-vendor-basename",
        "unknown-python-basename",
        "duplicate-vendor-slot",
    ),
)
def test_managed_remove_preserves_unidentifiable_legacy_profile_slots(
    tmp_path: Path, variant: str, edited: bytes
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / f"profile-{variant}"
    target.write_bytes(edited)

    assert not helper.managed_removal_data_is_owned(edited, "profile")
    assert helper.remove_managed_artifact(target, "profile") == "unmanaged"
    assert target.read_bytes() == edited


def _legacy_profile_with_directory_slot(slot: str, directory: Path) -> bytes:
    encoded = str(directory).encode("utf-8")
    if slot == "bin":
        return (
            FROZEN_LEGACY_PROFILE.replace(
                b'"/opt/triad-codex-dispatch/bin" = "read"',
                b'"' + encoded + b'" = "read"',
                1,
            )
            .replace(
                b'"/opt/triad-codex-dispatch/bin/_logs" = "write"',
                b'"' + str(directory / "_logs").encode("utf-8") + b'" = "write"',
                1,
            )
            .replace(
                b'"/opt/triad-codex-dispatch/bin/_debug" = "write"',
                b'"' + str(directory / "_debug").encode("utf-8") + b'" = "write"',
                1,
            )
        )
    if slot == "launcher":
        return FROZEN_LEGACY_PROFILE.replace(
            b'"/Users/example/.local/bin" = "read"',
            b'"' + encoded + b'" = "read"',
            1,
        )
    if slot == "classifier":
        return FROZEN_LEGACY_PROFILE.replace(
            b'"/Users/example/.config/triad-codex-dispatch" = "write"',
            b'"' + encoded + b'" = "write"',
            1,
        )
    raise AssertionError(f"unexpected profile directory slot: {slot}")


@pytest.mark.parametrize("slot", ("bin", "launcher", "classifier"))
@pytest.mark.parametrize(
    ("root_kind", "broad_directory"),
    (
        ("root", Path("/").resolve()),
        ("system", Path("/usr/local/bin").resolve()),
        ("package", Path("/opt/homebrew/bin").resolve()),
        ("home", Path.home().resolve()),
    ),
    ids=("root", "system", "package", "home"),
)
def test_managed_remove_preserves_broad_legacy_profile_directory_slots(
    tmp_path: Path, slot: str, root_kind: str, broad_directory: Path
) -> None:
    helper = _load_bootstrap_repair_module()
    edited = _legacy_profile_with_directory_slot(slot, broad_directory)
    target = tmp_path / f"profile-{slot}-{root_kind}"
    target.write_bytes(edited)

    assert not helper.managed_removal_data_is_owned(edited, "profile")
    assert helper.remove_managed_artifact(target, "profile") == "unmanaged"
    assert target.read_bytes() == edited


def test_legacy_profile_allows_python_and_vendor_files_below_broad_directories() -> None:
    helper = _load_bootstrap_repair_module()

    assert helper.managed_removal_data_is_owned(FROZEN_LEGACY_PROFILE, "profile")


@pytest.mark.parametrize("mode", ("--install", "--remove"))
@pytest.mark.parametrize("slot", ("launcher", "classifier"))
def test_bootstrap_preserves_broad_legacy_profile_directory_slots(
    tmp_path: Path, mode: str, slot: str
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    profile = codex_home / "triad-codex-dispatch.config.toml"
    edited = _legacy_profile_with_directory_slot(slot, Path("/"))
    profile.write_bytes(edited)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg=mode,
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "leaving unmanaged Codex profile" in result.stdout
    assert profile.read_bytes() == edited


def test_managed_remove_accepts_different_valid_legacy_profile_slots(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    alternate = (
        FROZEN_LEGACY_PROFILE.replace(
            b"/opt/triad-codex-dispatch/bin", b"/srv/triad/bin"
        )
        .replace(b"/Users/example/.local/bin", b"/var/lib/triad-launchers")
        .replace(
            b"/opt/homebrew/opt/python@3.12/bin/python3.12",
            b"/usr/bin/python3",
        )
        .replace(
            b"/Users/example/.config/triad-codex-dispatch",
            b"/var/lib/triad-classifier",
        )
        .replace(b"/usr/local/bin/claude", b"/opt/vendor/claude")
        .replace(b"/usr/local/bin/agy", b"/opt/vendor/agy")
    )
    target = tmp_path / "alternate-profile"
    target.write_bytes(alternate)

    assert helper.managed_removal_data_is_owned(alternate, "profile")
    assert helper.remove_managed_artifact(target, "profile") == "removed"
    assert not target.exists()


@pytest.mark.parametrize("mode", ("--install", "--remove"))
def test_bootstrap_preserves_legacy_profile_with_inserted_read_slot(
    tmp_path: Path, mode: str
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    profile = codex_home / "triad-codex-dispatch.config.toml"
    edited = FROZEN_LEGACY_PROFILE.replace(
        b'"/usr/local/bin/agy" = "read"\n',
        b'"/usr/local/bin/agy" = "read"\n"/owner/path" = "read"\n',
        1,
    )
    profile.write_bytes(edited)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg=mode,
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "leaving unmanaged Codex profile" in result.stdout
    assert profile.read_bytes() == edited


@pytest.mark.parametrize("mode", ("--install", "--remove"))
def test_bootstrap_preserves_marker_first_edited_legacy_policy(
    tmp_path: Path, mode: str
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    profile = codex_home / "triad-codex-dispatch.config.toml"
    rules = codex_home / "rules" / "triad-codex-dispatch.rules"
    rules.parent.mkdir()
    edited_profile = FROZEN_LEGACY_PROFILE + b"owner_edit = true\n"
    edited_rules = FROZEN_LEGACY_RULES + b"# owner edit\n"
    profile.write_bytes(edited_profile)
    rules.write_bytes(edited_rules)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg=mode,
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "leaving unmanaged Codex profile" in result.stdout
    assert "leaving unmanaged Codex rules file" in result.stdout
    assert profile.read_bytes() == edited_profile
    assert rules.read_bytes() == edited_rules


def test_plain_install_removes_exact_managed_legacy_shell_entry(
    tmp_path: Path,
) -> None:
    shell_rc = tmp_path / "shellrc"
    shell_rc.write_bytes(FROZEN_LEGACY_SHELL_ENTRY)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        env_overrides={"TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert str(shell_rc) in result.stdout
    assert "removed managed codex-triad shell entry" in result.stdout
    assert shell_rc.read_bytes() == b""


@pytest.mark.parametrize("profile", ("custom", "Custom_1.2-a"))
def test_plain_install_removes_exact_historical_shell_entry_with_valid_profile(
    tmp_path: Path,
    profile: str,
) -> None:
    shell_rc = tmp_path / "shellrc"
    shell_rc.write_bytes(_legacy_shell_entry_for_profile(profile))

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        env_overrides={"TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "removed managed codex-triad shell entry" in result.stdout
    assert shell_rc.read_bytes() == b""


def test_plain_install_preserves_edited_historical_shell_entry_with_custom_profile(
    tmp_path: Path,
) -> None:
    shell_rc = tmp_path / "shellrc"
    edited = _legacy_shell_entry_for_profile("custom-profile").replace(
        b"TRIAD_WRAPPER_HARDENED=1", b"TRIAD_WRAPPER_HARDENED=0"
    )
    shell_rc.write_bytes(edited)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        env_overrides={"TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "leaving unmanaged codex-triad entry" in result.stdout
    assert shell_rc.read_bytes() == edited


def test_plain_install_preserves_and_reports_safe_unmanaged_legacy_artifacts(
    tmp_path: Path,
) -> None:
    codex_home = tmp_path / "home" / ".codex"
    codex_home.mkdir(parents=True)
    profile = codex_home / "triad-codex-dispatch.config.toml"
    profile.write_text('owner = "foreign"\n', encoding="utf-8")
    shell_rc = tmp_path / "shellrc"
    shell_rc.write_text('codex-triad() { command codex --profile old "$@"; }\n', encoding="utf-8")

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "leaving unmanaged Codex profile" in result.stdout
    assert "leaving unmanaged codex-triad entry" in result.stdout
    assert profile.read_text(encoding="utf-8") == 'owner = "foreign"\n'
    assert shell_rc.read_text(encoding="utf-8") == 'codex-triad() { command codex --profile old "$@"; }\n'


def test_plain_install_cleanup_is_quiet_when_legacy_artifacts_are_absent(
    tmp_path: Path,
) -> None:
    result, _env, _launchers = _run_bootstrap(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    assert "Codex runtime profile" not in result.stdout
    assert "Codex command rules" not in result.stdout
    assert "codex-triad shell entry" not in result.stdout


@pytest.mark.parametrize("unsafe_kind", ("symlink", "fifo"))
def test_plain_install_refuses_unsafe_legacy_profile_without_mutation(
    tmp_path: Path, unsafe_kind: str,
) -> None:
    helper = _load_bootstrap_repair_module()
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    launcher_dir = tmp_path / "launchers"
    launcher_dir.mkdir()
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    profile = codex_home / "triad-codex-dispatch.config.toml"
    shell_rc = tmp_path / "shellrc"
    shell_rc.write_bytes(b"# owner shell\n")
    classifier = tmp_path / "classifier" / "patches.json"
    extra_paths: tuple[Path, ...] = ()
    if unsafe_kind == "symlink":
        referent = tmp_path / "foreign-profile.toml"
        referent.write_bytes(helper.PROFILE_MARKER + b"\nowner = true\n")
        profile.symlink_to(referent)
        extra_paths = (referent,)
    else:
        os.mkfifo(profile)
    unsafe_paths = (profile, *extra_paths)
    before = _install_target_fingerprint(unsafe_paths)

    result, _env, launchers = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert str(profile) in result.stderr
    assert _install_target_fingerprint(unsafe_paths) == before
    assert not any(launchers.iterdir())
    _assert_legacy_repair_state_absent(codex_home)
    assert not (codex_home / "rules" / "triad-codex-dispatch.rules").exists()
    assert not classifier.exists()
    assert shell_rc.read_bytes() == b"# owner shell\n"


@pytest.mark.parametrize("unsafe_kind", ("symlink-ancestor", "directory"))
def test_plain_install_refuses_unsafe_legacy_shell_without_mutation(
    tmp_path: Path, unsafe_kind: str,
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    launcher_dir = tmp_path / "launchers"
    launcher_dir.mkdir()
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    classifier = tmp_path / "classifier" / "patches.json"
    extra_paths: tuple[Path, ...] = ()
    if unsafe_kind == "symlink-ancestor":
        real_parent = tmp_path / "real-shell-parent"
        real_parent.mkdir()
        linked_parent = tmp_path / "linked-shell-parent"
        linked_parent.symlink_to(real_parent, target_is_directory=True)
        shell_rc = linked_parent / "shellrc"
        extra_paths = (linked_parent, real_parent / "shellrc")
    else:
        shell_rc = tmp_path / "shellrc"
        shell_rc.mkdir()
    unsafe_paths = (shell_rc, *extra_paths)
    before = _install_target_fingerprint(unsafe_paths)

    result, _env, launchers = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert str(shell_rc) in result.stderr
    assert _install_target_fingerprint(unsafe_paths) == before
    assert not any(launchers.iterdir())
    _assert_legacy_repair_state_absent(codex_home)
    assert not (codex_home / "rules" / "triad-codex-dispatch.rules").exists()
    assert not classifier.exists()






def test_install_cleanup_preserves_foreign_repair_analyzer_registration(
    tmp_path: Path,
) -> None:
    codex_home = tmp_path / "home" / ".codex"
    codex_home.mkdir(parents=True)
    config = codex_home / "config.toml"
    foreign = (
        "[agents]\nmax_threads = 2\n\n"
        f"[agents.{REPAIR_ANALYZER}]\n"
        'description = "foreign"\n'
        'config_file = "/foreign/agent.toml"\n'
    )
    config.write_text(foreign, encoding="utf-8")

    result, _env, launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0",
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert config.read_text(encoding="utf-8").startswith(foreign)
    assert tomllib.loads(config.read_text(encoding="utf-8"))["agents"][
        REPAIR_ANALYZER
    ]["description"] == "foreign"
    for wrapper in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        assert (launchers / wrapper).is_file()


def test_install_preserves_invalid_registration_config_without_publishing_analyzer(
    tmp_path: Path,
) -> None:
    config_text = "[agents\n"
    codex_home = tmp_path / "home" / ".codex"
    codex_home.mkdir(parents=True)
    config = codex_home / "config.toml"
    config.write_text(config_text, encoding="utf-8")

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0",
        },
    )

    assert result.returncode != 0
    assert config.read_text(encoding="utf-8") == config_text
    assert not (codex_home / "agents" / f"{REPAIR_ANALYZER}.toml").exists()


def test_bootstrap_repair_refuses_reversed_reserved_marker_comments(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, config, launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    foreign = (
        f"{helper.REG_END}\n"
        f"{helper.REG_BEGIN}\n"
    ).encode("utf-8")
    config.write_bytes(foreign)

    status = helper.main(args)

    assert status == 3
    assert config.read_bytes() == foreign
    assert analyzer.exists()
    assert launcher.exists()


@pytest.mark.parametrize(
    "markers",
    (
        ("begin",),
        ("end",),
        ("begin", "begin", "end"),
        ("begin", "end", "end"),
    ),
)
def test_bootstrap_repair_refuses_orphan_or_duplicate_reserved_marker_comments(
    tmp_path: Path, markers: tuple[str, ...]
) -> None:
    helper = _load_bootstrap_repair_module()
    args, analyzer, config, launcher = _seed_frozen_legacy_repair_state(
        helper, tmp_path
    )
    marker_text = {"begin": helper.REG_BEGIN, "end": helper.REG_END}
    foreign = "".join(f"{marker_text[marker]}\n" for marker in markers).encode("utf-8")
    config.write_bytes(foreign)

    status = helper.main(args)

    assert status == 3
    assert config.read_bytes() == foreign
    assert analyzer.exists()
    assert launcher.exists()


@pytest.mark.parametrize("kind", ("symlink", "fifo"))
def test_install_refuses_unsafe_config_without_following_or_publishing_analyzer(
    tmp_path: Path, kind: str
) -> None:
    codex_home = tmp_path / "home" / ".codex"
    codex_home.mkdir(parents=True)
    config = codex_home / "config.toml"
    target = tmp_path / "foreign-config.toml"
    if kind == "symlink":
        target.write_text("# foreign config\n", encoding="utf-8")
        config.symlink_to(target)
        before = target.read_bytes()
    else:
        os.mkfifo(config)
        before = b""
    try:
        result, _env, _launchers = _run_bootstrap(
            tmp_path,
            arg="--install",
            env_overrides={
                "CODEX_HOME": str(codex_home),
                "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0",
            },
            timeout=2,
        )
    finally:
        if kind == "fifo":
            config.unlink(missing_ok=True)

    assert result.returncode != 0
    assert not (codex_home / "agents" / f"{REPAIR_ANALYZER}.toml").exists()
    if kind == "symlink":
        assert config.is_symlink()
        assert target.read_bytes() == before


def test_registration_round_trip_preserves_unrelated_config_bytes(tmp_path: Path) -> None:
    codex_home = tmp_path / "home" / ".codex"
    codex_home.mkdir(parents=True)
    config = codex_home / "config.toml"
    original = "# retain this comment\n[agents]\nmax_threads = 3\n\n[custom]\nvalue = \"unchanged\"\n"
    config.write_text(original, encoding="utf-8")

    installed, env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0",
        },
    )
    assert installed.returncode == 0, installed.stderr + installed.stdout
    removed, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        arg="--remove",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0",
        },
    )
    assert removed.returncode == 0, removed.stderr + removed.stdout
    assert config.read_text(encoding="utf-8") == original






@pytest.mark.parametrize("kind", ("symlink", "fifo"))
def test_remove_refuses_unsafe_config_and_preserves_managed_analyzer(
    tmp_path: Path, kind: str
) -> None:
    installed, env, _launchers = _run_bootstrap(tmp_path, arg="--install")
    assert installed.returncode == 0, installed.stderr + installed.stdout
    codex_home = Path(env["HOME"]) / ".codex"
    helper = _load_bootstrap_repair_module()
    _args, analyzer, config, seeded_launcher = _seed_frozen_legacy_repair_state(
        helper, codex_home, existing_config=True
    )
    seeded_launcher.replace(_launchers / "triad-apply-repair")
    target = tmp_path / "foreign-config.toml"
    if kind == "symlink":
        original = config.read_bytes()
        target.write_bytes(original)
        config.unlink()
        config.symlink_to(target)
    else:
        config.unlink()
        os.mkfifo(config)
    try:
        removed, _env, _launchers = _run_bootstrap(
            tmp_path,
            repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
            arg="--remove",
            timeout=4,
        )
    finally:
        if kind == "fifo":
            config.unlink(missing_ok=True)

    assert removed.returncode != 0
    assert analyzer.is_file()
    if kind == "symlink":
        assert config.is_symlink()
        assert target.read_bytes() == original


@pytest.mark.parametrize("kind", ("symlink", "unmanaged"))
def test_install_cleanup_handles_foreign_legacy_repair_analyzer_target(
    tmp_path: Path, kind: str
) -> None:
    codex_home = tmp_path / "home" / ".codex"
    agents_dir = codex_home / "agents"
    agents_dir.mkdir(parents=True)
    analyzer = agents_dir / f"{REPAIR_ANALYZER}.toml"
    if kind == "symlink":
        linked = tmp_path / "foreign-agent.toml"
        linked.write_text("foreign\n", encoding="utf-8")
        analyzer.symlink_to(linked)
    else:
        analyzer.write_text('name = "foreign-agent"\n', encoding="utf-8")
    before = analyzer.readlink() if kind == "symlink" else analyzer.read_text(encoding="utf-8")

    result, _env, launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    if kind == "symlink":
        assert result.returncode != 0
        assert "repair analyzer" in result.stderr
        assert not any(launchers.iterdir())
    else:
        assert result.returncode == 0, result.stderr + result.stdout
        for wrapper in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
            assert (launchers / wrapper).is_file()
    assert analyzer.is_symlink() if kind == "symlink" else analyzer.is_file()
    if kind == "symlink":
        assert analyzer.readlink() == before
    else:
        assert analyzer.read_text(encoding="utf-8") == before


def test_install_cleanup_refuses_nonregular_legacy_repair_analyzer_target(
    tmp_path: Path,
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    agents_dir = codex_home / "agents"
    agents_dir.mkdir(parents=True)
    analyzer = agents_dir / f"{REPAIR_ANALYZER}.toml"
    os.mkfifo(analyzer)

    try:
        result, _env, launchers = _run_bootstrap(
            tmp_path,
            repo_root=repo_root,
            arg="--install",
            env_overrides={
                "CODEX_HOME": str(codex_home),
                "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            },
            timeout=15,
        )
        assert result.returncode != 0
        assert "repair analyzer" in result.stderr
        assert stat.S_ISFIFO(analyzer.lstat().st_mode)
        assert not any(launchers.iterdir())
        assert config.read_bytes() == config_before
        assert not list(codex_home.glob("*.config.toml"))
        assert not (codex_home / "rules").exists()
        assert classifier.read_text(encoding="utf-8") == '{"existing": true}\n'
        assert shell_rc.read_text(encoding="utf-8") == "# existing shell rc\n"
        assert not (repo_root / "bin" / "_logs").exists()
    finally:
        analyzer.unlink(missing_ok=True)


@pytest.mark.parametrize("kind", ("fifo", "symlink", "unmanaged"))
def test_install_cleanup_refuses_unsafe_legacy_repair_launcher_before_wrapper_publication(
    tmp_path: Path, kind: str
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    launcher_bin = tmp_path / "launchers"
    launcher_bin.mkdir()
    apply_launcher = launcher_bin / "triad-apply-repair"
    foreign = tmp_path / "foreign-apply-launcher"
    if kind == "fifo":
        os.mkfifo(apply_launcher)
    elif kind == "symlink":
        foreign.write_text("foreign\n", encoding="utf-8")
        apply_launcher.symlink_to(foreign)
    else:
        apply_launcher.write_text("#!/usr/bin/env python3\n# foreign\n", encoding="utf-8")

    try:
        result, _env, launchers = _run_bootstrap(
            tmp_path,
            repo_root=repo_root,
            arg="--install",
            env_overrides={
                "CODEX_HOME": str(codex_home),
                "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            },
            timeout=15,
        )
        if kind == "unmanaged":
            assert result.returncode == 0, result.stderr + result.stdout
            assert apply_launcher.read_text(encoding="utf-8").endswith("# foreign\n")
            for wrapper in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
                assert (launchers / wrapper).is_file()
        else:
            assert result.returncode != 0
            assert "repair apply launcher" in result.stderr
            assert sorted(path.name for path in launchers.iterdir()) == [
                "triad-apply-repair"
            ]
            assert config.read_bytes() == config_before
            assert not list(codex_home.glob("*.config.toml"))
            assert not (codex_home / "rules").exists()
            assert classifier.read_text(encoding="utf-8") == '{"existing": true}\n'
            assert shell_rc.read_text(encoding="utf-8") == "# existing shell rc\n"
            assert not (repo_root / "bin" / "_logs").exists()
        if kind == "symlink":
            assert apply_launcher.is_symlink()
            assert foreign.read_text(encoding="utf-8") == "foreign\n"
    finally:
        if kind == "fifo":
            apply_launcher.unlink(missing_ok=True)


def test_install_cleanup_refuses_symlinked_legacy_analyzer_parent_before_wrapper_publication(
    tmp_path: Path,
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    foreign_agents = tmp_path / "foreign-agents"
    foreign_agents.mkdir()
    frozen = foreign_agents / f"{REPAIR_ANALYZER}.toml"
    frozen.write_text(
        f'{REPAIR_ANALYZER_MARKER}\nname = "{REPAIR_ANALYZER}"\n',
        encoding="utf-8",
    )
    frozen_before = frozen.read_bytes()
    (codex_home / "agents").symlink_to(foreign_agents, target_is_directory=True)

    result, _env, launchers = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1",
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
        timeout=15,
    )

    assert result.returncode != 0
    assert "unsafe ancestor" in result.stderr
    assert frozen.read_bytes() == frozen_before
    assert not any(launchers.iterdir())
    assert config.read_bytes() == config_before
    assert not list(codex_home.glob("*.config.toml"))
    assert not (codex_home / "rules").exists()
    assert classifier.read_text(encoding="utf-8") == '{"existing": true}\n'
    assert shell_rc.read_text(encoding="utf-8") == "# existing shell rc\n"
    assert not (repo_root / "bin" / "_logs").exists()


def test_remove_refuses_unsafe_repair_target_before_any_mutation(tmp_path: Path) -> None:
    installed, env, launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1"},
    )
    assert installed.returncode == 0, installed.stderr + installed.stdout
    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    codex_home = Path(env["HOME"]) / ".codex"
    helper = _load_bootstrap_repair_module()
    _args, analyzer, _config, seeded_launcher = _seed_frozen_legacy_repair_state(
        helper, codex_home, existing_config=True
    )
    seeded_launcher.replace(launcher_bin / "triad-apply-repair")
    analyzer.unlink()
    os.mkfifo(analyzer)
    protected = [
        launcher_bin / name
        for name in (
            "claude_wrapper.py",
            "gemini_wrapper.py",
            "antigravity_wrapper.py",
            "triad-apply-repair",
        )
    ] + [
        codex_home / "config.toml",
        codex_home / "triad-codex-dispatch.config.toml",
        codex_home / "rules" / "triad-codex-dispatch.rules",
    ]
    before = _install_target_fingerprint(tuple(protected))

    try:
        removed, _env, _launchers = _run_bootstrap(
            tmp_path,
            repo_root=repo_root,
            arg="--remove",
            timeout=15,
        )
        assert removed.returncode != 0
        assert "repair analyzer" in removed.stderr
        assert stat.S_ISFIFO(analyzer.lstat().st_mode)
        assert _install_target_fingerprint(tuple(protected)) == before
    finally:
        analyzer.unlink(missing_ok=True)


def test_remove_refuses_symlinked_repair_analyzer_parent_before_any_mutation(
    tmp_path: Path,
) -> None:
    installed, env, launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1"},
    )
    assert installed.returncode == 0, installed.stderr + installed.stdout
    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    codex_home = Path(env["HOME"]) / ".codex"
    helper = _load_bootstrap_repair_module()
    _args, _analyzer, _config, seeded_launcher = _seed_frozen_legacy_repair_state(
        helper, codex_home, existing_config=True
    )
    seeded_launcher.replace(launcher_bin / "triad-apply-repair")
    agents = codex_home / "agents"
    foreign_agents = tmp_path / "foreign-agents"
    agents.rename(foreign_agents)
    agents.symlink_to(foreign_agents, target_is_directory=True)
    analyzer = foreign_agents / f"{REPAIR_ANALYZER}.toml"
    analyzer_before = analyzer.read_bytes()
    protected = [
        launcher_bin / name
        for name in (
            "claude_wrapper.py",
            "gemini_wrapper.py",
            "antigravity_wrapper.py",
            "triad-apply-repair",
        )
    ] + [
        codex_home / "config.toml",
        codex_home / "triad-codex-dispatch.config.toml",
        codex_home / "rules" / "triad-codex-dispatch.rules",
    ]
    before = _install_target_fingerprint(tuple(protected))

    removed, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--remove",
        timeout=15,
    )

    assert removed.returncode != 0
    assert "unsafe ancestor" in removed.stderr
    assert agents.is_symlink()
    assert analyzer.read_bytes() == analyzer_before
    assert _install_target_fingerprint(tuple(protected)) == before


def test_remove_canonicalizes_the_same_trusted_root_alias_as_install(
    tmp_path: Path,
) -> None:
    codex_home = tmp_path / "canonical-codex-home"
    codex_home.mkdir()
    codex_home_alias = tmp_path / "codex-home-alias"
    codex_home_alias.symlink_to(codex_home, target_is_directory=True)

    installed, env, launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"CODEX_HOME": str(codex_home_alias)},
    )
    assert installed.returncode == 0, installed.stderr + installed.stdout
    helper = _load_bootstrap_repair_module()
    _args, analyzer, _config, seeded_launcher = _seed_frozen_legacy_repair_state(
        helper, codex_home, existing_config=True
    )
    seeded_launcher.replace(launcher_bin / "triad-apply-repair")

    removed, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        arg="--remove",
        env_overrides={"CODEX_HOME": str(codex_home_alias)},
    )

    assert removed.returncode == 0, removed.stderr + removed.stdout
    assert not analyzer.exists()
    assert not (launcher_bin / "triad-apply-repair").exists()


def test_remove_deletes_only_managed_repair_analyzer_and_apply_launcher(tmp_path: Path) -> None:
    installed, env, launcher_bin = _run_bootstrap(tmp_path, arg="--install")
    assert installed.returncode == 0, installed.stderr + installed.stdout
    codex_home = Path(env["HOME"]) / ".codex"
    helper = _load_bootstrap_repair_module()
    _args, analyzer, _config, seeded_launcher = _seed_frozen_legacy_repair_state(
        helper, codex_home, existing_config=True
    )
    apply_launcher = launcher_bin / "triad-apply-repair"
    seeded_launcher.replace(apply_launcher)

    removed, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        arg="--remove",
    )

    assert removed.returncode == 0, removed.stderr + removed.stdout
    assert not analyzer.exists()
    assert not apply_launcher.exists()
    config = Path(env["HOME"]) / ".codex" / "config.toml"
    if config.exists():
        assert REPAIR_ANALYZER not in tomllib.loads(
            config.read_text(encoding="utf-8")
        ).get("agents", {})


def test_remove_preserves_foreign_repair_analyzer_registration(tmp_path: Path) -> None:
    codex_home = tmp_path / "home" / ".codex"
    codex_home.mkdir(parents=True)
    config = codex_home / "config.toml"
    foreign = (
        f"[agents.{REPAIR_ANALYZER}]\n"
        'description = "foreign"\n'
        'config_file = "/foreign/agent.toml"\n'
    )
    config.write_text(foreign, encoding="utf-8")

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--remove",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert config.read_text(encoding="utf-8") == foreign


@pytest.mark.parametrize("kind", ("symlink", "unmanaged"))
def test_remove_preserves_foreign_repair_analyzer_and_apply_launcher(
    tmp_path: Path, kind: str
) -> None:
    codex_home = tmp_path / "home" / ".codex"
    agents_dir = codex_home / "agents"
    launcher_dir = tmp_path / "launchers"
    agents_dir.mkdir(parents=True)
    launcher_dir.mkdir()
    analyzer = agents_dir / f"{REPAIR_ANALYZER}.toml"
    apply_launcher = launcher_dir / "triad-apply-repair"
    if kind == "symlink":
        foreign_agent = tmp_path / "foreign-agent.toml"
        foreign_launcher = tmp_path / "foreign-launcher"
        foreign_agent.write_text("foreign agent\n", encoding="utf-8")
        foreign_launcher.write_text("foreign launcher\n", encoding="utf-8")
        analyzer.symlink_to(foreign_agent)
        apply_launcher.symlink_to(foreign_launcher)
    else:
        analyzer.write_text('name = "foreign-agent"\n', encoding="utf-8")
        apply_launcher.write_text("#!/bin/sh\necho foreign\n", encoding="utf-8")

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--remove",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_BIN_DIR": str(launcher_dir),
        },
    )

    if kind == "symlink":
        assert result.returncode != 0
        assert "unsafe repair analyzer" in result.stderr
    else:
        assert result.returncode == 0, result.stderr + result.stdout
    assert analyzer.exists() or analyzer.is_symlink()
    assert apply_launcher.exists() or apply_launcher.is_symlink()






@pytest.mark.parametrize(
    ("unsafe_target", "dangling"),
    [
        ("profile", False),
        ("profile", True),
        ("rules-leaf", False),
        ("rules-leaf", True),
        ("rules-ancestor", False),
    ],
)
def test_install_rejects_unsafe_legacy_profile_or_rules_target_before_commands(
    tmp_path: Path, unsafe_target: str, dangling: bool
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    external = tmp_path / "external-target"
    profile = codex_home / "triad-codex-dispatch.config.toml"
    rules_dir = codex_home / "rules"
    rules = rules_dir / "triad-codex-dispatch.rules"

    if unsafe_target == "profile":
        unsafe = profile
    elif unsafe_target == "rules-leaf":
        rules_dir.mkdir()
        unsafe = rules
    else:
        unsafe = rules_dir
    if not dangling:
        if unsafe_target == "rules-ancestor":
            external.mkdir()
        else:
            external.write_bytes(b"foreign target\n")
    unsafe.symlink_to(external, target_is_directory=unsafe_target == "rules-ancestor")

    result, _env, launchers = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--install",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode != 0
    assert unsafe.is_symlink()
    assert not any(launchers.iterdir())
    if dangling:
        assert not external.exists()
    elif unsafe_target == "rules-ancestor":
        assert external.is_dir()
    else:
        assert external.read_bytes() == b"foreign target\n"






def test_install_rejects_dangling_classifier_before_first_persistent_mutation(
    tmp_path: Path,
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    config_before = b'# owner config\ncustom = "preserve"\n'
    config.write_bytes(config_before)
    classifier = tmp_path / "classifier" / "classifier-patches.json"
    classifier.parent.mkdir()
    external = tmp_path / "external-classifier"
    classifier.symlink_to(external)
    shell_rc = tmp_path / "shellrc"
    shell_before = b"# owner shell\n"
    shell_rc.write_bytes(shell_before)

    result, _env, launchers = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1",
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert classifier.is_symlink()
    assert not external.exists()
    assert not any(launchers.iterdir())
    assert config.read_bytes() == config_before
    assert shell_rc.read_bytes() == shell_before
    assert not (codex_home / "agents").exists()
    assert not (codex_home / "triad-codex-dispatch.config.toml").exists()
    assert not (codex_home / "rules").exists()
    assert not (repo_root / "bin" / "_logs").exists()


def test_late_classifier_failure_is_fatal_and_preserves_existing_bytes(
    tmp_path: Path,
) -> None:
    classifier = tmp_path / "classifier" / "classifier-patches.json"
    classifier.parent.mkdir()
    original = b'{"owner": "preserve"}\n'
    classifier.write_bytes(original)

    result, env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0",
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "0",
            "TRIAD_BOOTSTRAP_TEST_FAIL_CLASSIFIER_ENSURE": "1",
        },
    )

    assert result.returncode != 0
    assert "injected classifier ensure failure" in result.stderr
    assert classifier.read_bytes() == original
    assert not (Path(env["HOME"]) / ".codex" / "config.toml").exists()


def test_late_classifier_race_is_fatal_without_following_dangling_symlink(
    tmp_path: Path,
) -> None:
    classifier = tmp_path / "classifier" / "classifier-patches.json"
    external = tmp_path / "external-classifier"

    result, env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0",
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "0",
            "TRIAD_BOOTSTRAP_TEST_SWAP_CLASSIFIER_TO_SYMLINK_BEFORE_ENSURE": str(
                external
            ),
        },
    )

    assert result.returncode != 0
    assert classifier.is_symlink()
    assert not external.exists()
    assert not (Path(env["HOME"]) / ".codex" / "config.toml").exists()




def test_install_never_executes_provider_binaries(tmp_path: Path) -> None:
    marker = tmp_path / "provider-called"
    provider_script = 'printf provider-called > "$TRIAD_PROVIDER_MARKER"'
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
    assert not (launchers / "triad-setup").exists()
    assert not (launchers / "triad-doctor").exists()




def test_check_supports_workspace_contained_install_targets(tmp_path):
    # Install targets contained in the TOOLKIT checkout are still supported
    # when bootstrap runs from OUTSIDE those directories (cwd=ROOT here).
    # Running the same layout FROM the containing directory is a trusted-
    # executable rewrite chain and must hard-fail — see the
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
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert (workspace_bin / "claude_wrapper.py").is_file()
    assert (workspace_config / "triad-codex-dispatch" / "classifier-patches.json").is_file()
    _assert_legacy_repair_state_absent(workspace_codex)
    assert not (workspace_codex / "triad-codex-dispatch.config.toml").exists()
    assert not (workspace_codex / "rules" / "triad-codex-dispatch.rules").exists()
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
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "python startup warning" in result.stderr
    assert not (codex_home / "triad-codex-dispatch.config.toml").exists()
    assert not (codex_home / "rules" / "triad-codex-dispatch.rules").exists()
    for wrapper in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        assert (launcher_bin / wrapper).is_file()
    _assert_legacy_repair_state_absent(codex_home)


def test_check_warns_when_gemini_binary_is_missing(tmp_path):
    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path, fake_names=("codex", "claude", "agy")
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "optional binary not found: gemini" in result.stdout


def test_check_reports_gemini_fallback_candidate_when_agy_is_absent(tmp_path: Path) -> None:
    result, _env, _launchers = _run_bootstrap(
        tmp_path, fake_names=("codex", "claude", "gemini")
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "Gemini fallback candidate" in result.stdout
    assert "executable presence only" in result.stdout
    assert "must be proven in the owner's authenticated terminal" in result.stdout
    assert "using Gemini Enterprise/Business fallback" not in result.stdout




def test_check_prefers_agy_and_requires_one_google_route(tmp_path: Path) -> None:
    both, _env, _launchers = _run_bootstrap(
        tmp_path, fake_names=("codex", "claude", "agy", "gemini")
    )
    neither, _env, _launchers = _run_bootstrap(
        tmp_path / "neither", fake_names=("codex", "claude")
    )

    assert both.returncode == 0, both.stderr + both.stdout
    assert "found Google route: agy" in both.stdout
    assert "fallback" not in both.stdout
    assert neither.returncode != 0
    assert "missing Google route: agy or gemini" in neither.stderr


def test_check_fails_when_required_binary_is_missing(tmp_path):
    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path, fake_names=("codex", "agy")
    )

    assert result.returncode != 0
    assert "missing required binary: claude" in result.stderr


def _seed_preflight_artifacts(tmp_path: Path) -> tuple[Path, Path, Path, Path, bytes]:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    config.write_text('# existing config\ncustom = "preserve"\n', encoding="utf-8")
    classifier = tmp_path / "classifier" / "classifier-patches.json"
    classifier.parent.mkdir()
    classifier.write_text('{"existing": true}\n', encoding="utf-8")
    shell_rc = tmp_path / "shellrc"
    shell_rc.write_text("# existing shell rc\n", encoding="utf-8")
    return codex_home, config, classifier, shell_rc, config.read_bytes()


def _assert_preflight_artifacts_unchanged(
    *,
    repo_root: Path,
    launcher_bin: Path,
    codex_home: Path,
    config: Path,
    config_before: bytes,
    classifier: Path,
    shell_rc: Path,
    allowed_launcher_entries: tuple[str, ...] = (),
    allowed_profile_entries: tuple[str, ...] = (),
    allowed_rules_entries: tuple[str, ...] = (),
    shell_rc_before: bytes = b"# existing shell rc\n",
) -> None:
    assert {path.name for path in launcher_bin.iterdir()} == set(allowed_launcher_entries)
    assert config.read_bytes() == config_before
    assert not (codex_home / "agents").exists()
    assert {path.name for path in codex_home.glob("*.config.toml")} == set(
        allowed_profile_entries
    )
    rules_dir = codex_home / "rules"
    if allowed_rules_entries:
        assert rules_dir.is_dir()
        assert {path.name for path in rules_dir.iterdir()} == set(allowed_rules_entries)
    else:
        assert not rules_dir.exists()
    assert classifier.read_text(encoding="utf-8") == '{"existing": true}\n'
    assert shell_rc.read_bytes() == shell_rc_before
    assert not (repo_root / "bin" / "_logs").exists()


@pytest.mark.parametrize(
    "profile_name",
    (
        pytest.param("safe;touch-owned", id="semicolon"),
        pytest.param("safe$(touch-owned)", id="command-substitution"),
        pytest.param("safe`touch-owned`", id="backticks"),
        pytest.param("safe profile", id="space"),
        pytest.param("safe\nprofile", id="newline"),
        pytest.param(".safe", id="leading-punctuation"),
        pytest.param("safe\N{LATIN SMALL LETTER E WITH ACUTE}", id="non-ascii"),
    ),
)
def test_invalid_profile_name_is_rejected_before_artifact_mutation(
    tmp_path: Path, profile_name: str
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )

    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_CODEX_PROFILE_NAME": profile_name,
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert "invalid TRIAD_CODEX_PROFILE_NAME" in result.stderr
    assert "[A-Za-z0-9][A-Za-z0-9._-]*" in result.stderr
    _assert_preflight_artifacts_unchanged(
        repo_root=repo_root,
        launcher_bin=launcher_bin,
        codex_home=codex_home,
        config=config,
        config_before=config_before,
        classifier=classifier,
        shell_rc=shell_rc,
    )


def test_resolved_python_path_with_whitespace_is_rejected_before_artifact_mutation(
    tmp_path: Path,
) -> None:
    runtime_dir = tmp_path / "python runtime"
    runtime_dir.mkdir()
    whitespace_runtime = runtime_dir / "python3"
    _copy_test_python_executable(whitespace_runtime)

    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        python_script=f'exec {shlex.quote(str(whitespace_runtime))} "$@"',
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert "portable generated shebang cannot encode this Python runtime path" in result.stderr
    assert str(whitespace_runtime.resolve()) in result.stderr
    _assert_preflight_artifacts_unchanged(
        repo_root=repo_root,
        launcher_bin=launcher_bin,
        codex_home=codex_home,
        config=config,
        config_before=config_before,
        classifier=classifier,
        shell_rc=shell_rc,
    )


def test_oversized_python_shebang_is_rejected_before_artifact_mutation(
    tmp_path: Path,
) -> None:
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir()
    target_path_bytes = 251
    filename_size = target_path_bytes - len(os.fsencode(runtime_dir)) - 1
    assert 1 <= filename_size <= 255
    long_runtime = runtime_dir / ("p" * filename_size)
    _copy_test_python_executable(long_runtime)
    assert len(b"#!" + os.fsencode(long_runtime.resolve()) + b" -E\n") == 257

    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        python_script=f'exec {shlex.quote(str(long_runtime))} "$@"',
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert "exceeds 256 filesystem bytes" in result.stderr
    _assert_preflight_artifacts_unchanged(
        repo_root=repo_root,
        launcher_bin=launcher_bin,
        codex_home=codex_home,
        config=config,
        config_before=config_before,
        classifier=classifier,
        shell_rc=shell_rc,
    )


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


@pytest.mark.parametrize("surface", ("absent", "v1"))
def test_install_requires_pydantic_2_before_persistent_mutation(
    tmp_path: Path, surface: str
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    fake_site = _fake_pydantic_site(tmp_path, surface)
    shell_rc = tmp_path / "shellrc"

    result, env, launcher_dir = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--install",
        env_overrides={
            "PYTHONPATH": str(fake_site),
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    expected_command = shlex.join(
        [
            str(Path(sys.executable).resolve()),
            "-m",
            "pip",
            "install",
            "-r",
            str((repo_root / "requirements.txt").resolve()),
        ]
    )
    assert result.returncode != 0
    assert "Pydantic 2 formal review APIs are required" in result.stderr
    assert expected_command in result.stderr
    assert "required prerequisite checks failed" in result.stderr
    assert not any(launcher_dir.iterdir())
    assert not (Path(env["HOME"]) / ".codex").exists()
    assert not shell_rc.exists()


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


def test_generated_provider_launchers_force_audit_prompt_redaction_in_clean_environment(
    tmp_path: Path,
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    wrapper_source = '''\
import os
print(os.environ.get("TRIAD_AUDIT_REDACT_PROMPTS", "<missing>"))
print(os.environ.get("TRIAD_WRAPPER_HARDENED", "<missing>"))
'''
    for name in (
        "claude_wrapper.py",
        "gemini_wrapper.py",
        "antigravity_wrapper.py",
    ):
        (repo_root / "bin" / name).write_text(wrapper_source, encoding="utf-8")

    installed, env, launcher_bin = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--install",
    )

    assert installed.returncode == 0, installed.stderr + installed.stdout
    clean_env = {
        key: value for key, value in env.items() if not key.startswith("TRIAD_")
    }
    for name in (
        "claude_wrapper.py",
        "gemini_wrapper.py",
        "antigravity_wrapper.py",
    ):
        provider = subprocess.run(
            [str(launcher_bin / name)],
            text=True,
            capture_output=True,
            env=clean_env,
            timeout=5,
        )
        assert provider.returncode == 0, provider.stderr
        assert provider.stdout.splitlines() == ["1", "<missing>"]


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
















def test_install_preserves_unmanaged_codex_runtime_profile(tmp_path: Path) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    profile = codex_home / "triad-codex-dispatch.config.toml"
    original = b'approval_policy = "never"\n'
    profile.write_bytes(original)

    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "leaving unmanaged Codex profile" in result.stdout
    assert profile.read_bytes() == original
    assert config.read_bytes() == config_before
    assert shell_rc.read_bytes() == b"# existing shell rc\n"
    for wrapper in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        assert (launcher_bin / wrapper).is_file()




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


@pytest.mark.parametrize("arg", ("--install", "--remove"))
@pytest.mark.parametrize("placement", ("embedded", "later-line"))
def test_bootstrap_preserves_foreign_launcher_with_nonprovenance_marker(
    tmp_path: Path, arg: str, placement: str
) -> None:
    custom_bin = tmp_path / "custom-bin"
    custom_bin.mkdir()
    custom_launcher = custom_bin / "claude_wrapper.py"
    marker = "# triad-codex-dispatch managed launcher"
    if placement == "embedded":
        foreign = f'#!/usr/bin/env python3\nprint("{marker}")\n'.encode()
    else:
        foreign = f"#!/usr/bin/env python3\nprint('owner')\n{marker}\n".encode()
    custom_launcher.write_bytes(foreign)
    custom_launcher.chmod(custom_launcher.stat().st_mode | stat.S_IEXEC)

    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path,
        arg=arg,
        pre_path=(custom_bin,),
        env_overrides={"TRIAD_BOOTSTRAP_BIN_DIR": str(custom_bin)},
    )

    if arg == "--install":
        assert result.returncode != 0
        assert "refusing to overwrite unmanaged launcher" in result.stderr
    else:
        assert result.returncode == 0, result.stderr + result.stdout
    assert custom_launcher.read_bytes() == foreign


def test_bootstrap_upgrades_supported_historical_generated_launcher(
    tmp_path: Path,
) -> None:
    custom_bin = tmp_path / "custom-bin"
    custom_bin.mkdir()
    launcher = custom_bin / "claude_wrapper.py"
    launcher.write_bytes(
        b"#!/usr/bin/python3\n"
        b"# triad-codex-dispatch managed launcher\n"
        b"import os\nimport sys\n"
        b'os.environ["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"\n'
        b'os.environ["TRIAD_CLAUDE_BIN"] = "/usr/bin/claude"\n'
        b'os.execv("/usr/bin/python3", ["/usr/bin/python3", '
        b'"/old-plugin/bin/claude_wrapper.py"] + sys.argv[1:])\n'
    )
    launcher.chmod(0o755)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        pre_path=(custom_bin,),
        env_overrides={"TRIAD_BOOTSTRAP_BIN_DIR": str(custom_bin)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    installed = launcher.read_text(encoding="utf-8")
    assert "# triad-codex-dispatch managed launcher\n" in installed
    assert 'env["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"' in installed
    assert "os.execve(" in installed


def test_remove_deletes_supported_historical_runtime_commands(tmp_path: Path) -> None:
    custom_bin = tmp_path / "custom-bin"
    custom_bin.mkdir()
    for name in ("triad-setup", "triad-doctor"):
        command = name.removeprefix("triad-")
        target = custom_bin / name
        target.write_text(
            "#!/usr/bin/python3 -E\n"
            "# triad-codex-dispatch managed runtime command\n"
            "import os\nimport sys\n"
            'os.execv("/usr/bin/python3", ["/usr/bin/python3", "-E", '
            f'"/old-plugin/bin/triad_runtime.py", "{command}"] + sys.argv[1:])\n',
            encoding="utf-8",
        )
        target.chmod(0o755)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--remove",
        pre_path=(custom_bin,),
        env_overrides={"TRIAD_BOOTSTRAP_BIN_DIR": str(custom_bin)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert not (custom_bin / "triad-setup").exists()
    assert not (custom_bin / "triad-doctor").exists()


@pytest.mark.parametrize(
    ("name", "marker", "dangling"),
    [
        ("claude_wrapper.py", "# triad-codex-dispatch managed launcher\n", False),
        ("claude_wrapper.py", "# triad-codex-dispatch managed launcher\n", True),
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
        ("--remove", "claude_wrapper.py"),
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


@pytest.mark.parametrize(
    ("name", "foreign_kind"),
    [
        ("claude_wrapper.py", "fifo"),
        ("gemini_wrapper.py", "symlink"),
        ("antigravity_wrapper.py", "unmanaged"),
    ],
)
def test_any_foreign_command_target_stops_install_before_all_other_artifacts(
    tmp_path: Path, name: str, foreign_kind: str
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    launcher_dir = tmp_path / "foreign-launchers"
    launcher_dir.mkdir()
    target = launcher_dir / name
    linked_target = tmp_path / "foreign-command-peer"
    if foreign_kind == "fifo":
        os.mkfifo(target)
    elif foreign_kind == "symlink":
        linked_target.write_bytes(b"foreign symlink command\n")
        target.symlink_to(linked_target)
    else:
        target.write_bytes(b"foreign unmanaged command\n")

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--install",
        pre_path=(launcher_dir,),
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_BIN_DIR": str(launcher_dir),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    _assert_preflight_artifacts_unchanged(
        repo_root=repo_root,
        launcher_bin=launcher_dir,
        codex_home=codex_home,
        config=config,
        config_before=config_before,
        classifier=classifier,
        shell_rc=shell_rc,
        allowed_launcher_entries=(name,),
    )
    if foreign_kind == "fifo":
        assert stat.S_ISFIFO(target.stat().st_mode)
    elif foreign_kind == "symlink":
        assert target.is_symlink()
        assert linked_target.read_bytes() == b"foreign symlink command\n"
    else:
        assert target.read_bytes() == b"foreign unmanaged command\n"


def test_reinstall_replaces_managed_wrapper_hardlink_without_mutating_peer(tmp_path: Path) -> None:
    first, env, launcher_dir = _run_bootstrap(tmp_path, arg="--install")
    assert first.returncode == 0, first.stderr + first.stdout
    launcher = launcher_dir / "claude_wrapper.py"
    peer = tmp_path / "launcher-peer"
    os.link(launcher, peer)
    peer_before = peer.read_bytes()

    second, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
    )

    assert second.returncode == 0, second.stderr + second.stdout
    assert peer.read_bytes() == peer_before
    assert launcher.read_bytes() == peer_before
    assert not os.path.samestat(launcher.stat(), peer.stat())


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


def test_install_preserves_unmanaged_codex_command_rules(tmp_path: Path) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    rules = codex_home / "rules" / "triad-codex-dispatch.rules"
    rules.parent.mkdir(parents=True)
    original = b'prefix_rule(pattern = ["python3"], decision = "allow")\n'
    rules.write_bytes(original)

    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "leaving unmanaged Codex rules file" in result.stdout
    assert rules.read_bytes() == original
    assert config.read_bytes() == config_before
    assert shell_rc.read_bytes() == b"# existing shell rc\n"
    for wrapper in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        assert (launcher_bin / wrapper).is_file()


@pytest.mark.parametrize("kind", ("profile", "rules"))
def test_install_preserves_non_utf8_unmanaged_codex_target(
    tmp_path: Path, kind: str
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    if kind == "profile":
        target = codex_home / "triad-codex-dispatch.config.toml"
    else:
        target = codex_home / "rules" / "triad-codex-dispatch.rules"
        target.parent.mkdir()
    original = b"\xffnot-valid-utf8\n"
    target.write_bytes(original)

    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "leaving unmanaged Codex" in result.stdout
    assert target.read_bytes() == original
    assert config.read_bytes() == config_before
    assert shell_rc.read_bytes() == b"# existing shell rc\n"
    for wrapper in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        assert (launcher_bin / wrapper).is_file()


def test_check_rejects_invalid_codex_rules_name(tmp_path):
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "1",
            "TRIAD_CODEX_RULES_NAME": "../default.rules",
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert "invalid TRIAD_CODEX_RULES_NAME" in result.stderr
    _assert_preflight_artifacts_unchanged(
        repo_root=repo_root,
        launcher_bin=launcher_bin,
        codex_home=codex_home,
        config=config,
        config_before=config_before,
        classifier=classifier,
        shell_rc=shell_rc,
    )


def test_remove_rejects_invalid_rules_name_before_any_mutation(tmp_path: Path) -> None:
    first, env, launcher_bin = _run_bootstrap(tmp_path, arg="--install")
    assert first.returncode == 0, first.stderr + first.stdout
    codex_home = Path(env["HOME"]) / ".codex"
    rules = codex_home / "rules" / "triad-codex-dispatch.rules"
    rules.parent.mkdir(parents=True)
    rules.write_bytes(b"# triad-codex-dispatch managed command rules\nlegacy\n")
    managed_paths = [
        launcher_bin / name
        for name in (
            "claude_wrapper.py",
            "gemini_wrapper.py",
            "antigravity_wrapper.py",
        )
    ] + [rules]
    before = {path: path.read_bytes() for path in managed_paths}

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--remove",
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        env_overrides={"TRIAD_CODEX_RULES_NAME": "../default.rules"},
    )

    assert result.returncode != 0
    assert "invalid TRIAD_CODEX_RULES_NAME" in result.stderr
    assert {path: path.read_bytes() for path in managed_paths} == before




def test_remove_rolls_back_public_commands_after_late_command_failure(
    tmp_path: Path,
) -> None:
    shell_rc = tmp_path / "shellrc"
    first, env, launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc)},
    )
    assert first.returncode == 0, first.stderr + first.stdout
    public_commands = [
        launcher_bin / name
        for name in (
            "claude_wrapper.py",
            "gemini_wrapper.py",
            "antigravity_wrapper.py",
        )
    ]
    before = {path: path.read_bytes() for path in public_commands}
    codex_home = Path(env["HOME"]) / ".codex"
    helper = _load_bootstrap_repair_module()
    profile = codex_home / "triad-codex-dispatch.config.toml"
    profile.parent.mkdir(parents=True, exist_ok=True)
    profile.write_bytes(FROZEN_LEGACY_PROFILE)
    rules = codex_home / "rules" / "triad-codex-dispatch.rules"
    rules.parent.mkdir(parents=True)
    rules.write_bytes(FROZEN_LEGACY_RULES)
    config = codex_home / "config.toml"
    config.write_bytes(helper.current_config_fragment(b"\n"))
    shell_rc.write_bytes(FROZEN_LEGACY_SHELL_ENTRY)
    classifier = (
        Path(env["XDG_CONFIG_HOME"])
        / "triad-codex-dispatch"
        / "classifier-patches.json"
    )
    classifier_before = classifier.read_bytes()

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--remove",
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        env_overrides={
            "TRIAD_BOOTSTRAP_TEST_FAIL_COMMAND_REMOVE_AT": "gemini_wrapper.py",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0, result.stderr + result.stdout
    assert "injected command removal failure" in result.stderr
    assert {path: path.read_bytes() for path in public_commands} == before
    assert not profile.exists()
    assert not rules.exists()
    assert not config.exists()
    assert shell_rc.read_bytes() == b""
    assert classifier.read_bytes() == classifier_before


# --- MUST-land 1: workspace-escape guard -----------------------------------
# The generated exec-policy rules run the launcher paths OUTSIDE the sandbox
# after automatic review by default, or without review in the explicit `never`
# posture. If any install target (or the checkout the launchers exec) is writable
# from inside the Codex workspace bootstrap runs from ($PWD = the sandbox-writable
# root), a sandboxed session can rewrite a trusted executable before asking
# Codex to run it outside. Bootstrap must hard-fail.


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
    # workspace is the same executable-rewrite chain even when the launcher
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


# --- Canonical install/remove flags and expired alias rejection --------------


def test_install_flag_is_primary(tmp_path):
    result, env, _launcher_bin = _run_bootstrap(tmp_path, arg="--install")
    assert result.returncode == 0, result.stderr + result.stdout
    assert "--check is deprecated" not in result.stdout

    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    result2, _env2, _launcher_bin2 = _run_bootstrap(
        tmp_path, repo_root=repo_root, arg="--bogus"
    )
    assert result2.returncode == 2


@pytest.mark.parametrize("alias", ["--check", "--uninstall"])
def test_expired_legacy_aliases_are_rejected(tmp_path: Path, alias: str) -> None:
    result, _env, _launchers = _run_bootstrap(tmp_path, arg=alias, timeout=5)

    assert result.returncode == 2
    assert "Usage: scripts/bootstrap.sh --install" in result.stderr


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


def test_initially_absent_config_survives_three_installs(tmp_path: Path) -> None:
    first, env, _launchers = _run_bootstrap(tmp_path, arg="--install", timeout=5)
    assert first.returncode == 0, first.stderr + first.stdout
    config = Path(env["HOME"]) / ".codex" / "config.toml"
    assert not Path(str(config) + ".bak").exists()

    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    for _ in range(2):
        repeated, _env, _launchers = _run_bootstrap(
            tmp_path, repo_root=repo_root, arg="--install", timeout=5
        )
        assert repeated.returncode == 0, repeated.stderr + repeated.stdout


def test_initially_absent_config_remains_absent_after_two_installs_then_remove(
    tmp_path: Path,
) -> None:
    first, env, _launchers = _run_bootstrap(tmp_path, arg="--install", timeout=5)
    assert first.returncode == 0, first.stderr + first.stdout

    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    second, _env, _launchers = _run_bootstrap(
        tmp_path, repo_root=repo_root, arg="--install", timeout=5
    )
    assert second.returncode == 0, second.stderr + second.stdout

    removed, _env, _launchers = _run_bootstrap(
        tmp_path, repo_root=repo_root, arg="--remove", timeout=5
    )
    assert removed.returncode == 0, removed.stderr + removed.stdout
    config = Path(env["HOME"]) / ".codex" / "config.toml"
    assert not config.exists()


def test_preexisting_empty_config_survives_install_then_remove(
    tmp_path: Path,
) -> None:
    codex_home = tmp_path / "owner-codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    config.write_bytes(b"")

    installed, env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )
    assert installed.returncode == 0, installed.stderr + installed.stdout

    removed, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        arg="--remove",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert removed.returncode == 0, removed.stderr + removed.stdout
    assert config.exists()
    assert config.read_bytes() == b""


def test_preexisting_empty_config_has_no_repair_registration_before_remove(
    tmp_path: Path,
) -> None:
    codex_home = tmp_path / "owner-codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    config.write_bytes(b"")

    installed, env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )
    assert installed.returncode == 0, installed.stderr + installed.stdout

    analyzer = codex_home / "agents" / f"{REPAIR_ANALYZER}.toml"
    assert not analyzer.exists()
    assert "managed repair analyzer registration" not in config.read_text(
        encoding="utf-8"
    )

    removed, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        arg="--remove",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert removed.returncode == 0, removed.stderr + removed.stdout
    assert config.exists()
    assert config.read_bytes() == b""




def test_fresh_layout_preserves_edited_policy_across_reinstall_and_remove(
    tmp_path: Path,
) -> None:
    first, env, _launchers = _run_bootstrap(tmp_path, arg="--install", timeout=5)
    assert first.returncode == 0, first.stderr + first.stdout

    helper = _load_bootstrap_repair_module()
    config = Path(env["HOME"]) / ".codex" / "config.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    edited = helper.current_config_fragment(b"\n").replace(
        b'inherit = "all"\n', b'inherit = "all"\n# owner policy note\n', 1
    )
    config.write_bytes(edited)
    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])

    repeated, _env, _launchers = _run_bootstrap(
        tmp_path, repo_root=repo_root, arg="--install", timeout=5
    )
    assert repeated.returncode == 0, repeated.stderr + repeated.stdout
    assert config.read_bytes() == edited

    removed, _env, _launchers = _run_bootstrap(
        tmp_path, repo_root=repo_root, arg="--remove", timeout=5
    )
    assert removed.returncode == 0, removed.stderr + removed.stdout
    remaining = config.read_bytes()
    assert b"owner policy note" in remaining
    assert b"managed repair analyzer registration" not in remaining




def test_remove_refuses_to_reparent_bare_key_after_managed_registration(
    tmp_path: Path,
) -> None:
    first, env, launchers = _run_bootstrap(tmp_path, arg="--install", timeout=5)
    assert first.returncode == 0, first.stderr + first.stdout

    codex_home = Path(env["HOME"]) / ".codex"
    helper = _load_bootstrap_repair_module()
    _args, analyzer, config, seeded_launcher = _seed_frozen_legacy_repair_state(
        helper, codex_home, existing_config=True
    )
    seeded_launcher.replace(launchers / "triad-apply-repair")
    marker = "# <<< triad-codex-dispatch managed repair analyzer registration <<<\n"
    edited = config.read_text(encoding="utf-8").replace(
        marker, marker + 'owner_note = "preserve"\n', 1
    )
    config.write_text(edited, encoding="utf-8")
    removed, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        arg="--remove",
        timeout=5,
    )

    assert removed.returncode != 0
    assert "malformed managed repair analyzer registration" in removed.stderr
    assert config.read_text(encoding="utf-8") == edited
    assert analyzer.exists()


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


def _managed_repair_registration(codex_home: Path) -> str:
    analyzer = codex_home / "agents" / f"{REPAIR_ANALYZER}.toml"
    return (
        "# >>> triad-codex-dispatch managed repair analyzer registration >>>\n"
        "# original config existed = true\n"
        f"[agents.{REPAIR_ANALYZER}]\n"
        'description = "Read-only triad repair analyzer for untrusted vendor run logs."\n'
        f'config_file = "{analyzer}"\n'
        "# <<< triad-codex-dispatch managed repair analyzer registration <<<\n"
    )


def test_install_removes_only_the_exact_legacy_managed_environment_policy(
    tmp_path: Path,
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    begin = "# >>> triad-codex-dispatch managed shell_environment_policy >>>"
    end = "# <<< triad-codex-dispatch managed shell_environment_policy <<<"
    legacy = begin + '\n[shell_environment_policy]\ninherit = "core"\n' + end + "\n"
    prefix = "# retain this exact prefix\n[custom]\nvalue = \"unchanged\"\n\n"
    suffix = "\n" + _managed_repair_registration(codex_home)
    config.write_text(prefix + legacy + suffix, encoding="utf-8")

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert config.read_text(encoding="utf-8") == prefix
    assert not config.with_suffix(".toml.bak").exists()




@pytest.mark.parametrize(
    "managed_block",
    [
        "# >>> triad-codex-dispatch managed shell_environment_policy >>>\n"
        "[shell_environment_policy]\n"
        'inherit = "core"\n'
        "# owner-added comment\n"
        "# <<< triad-codex-dispatch managed shell_environment_policy <<<\n",
        "# >>> triad-codex-dispatch managed shell_environment_policy >>>\n"
        "[shell_environment_policy]\n"
        'inherit = "all"\n'
        'exclude = ["LD_*"]\n'
        "# <<< triad-codex-dispatch managed shell_environment_policy <<<\n",
    ],
)
def test_install_preserves_edited_managed_environment_policy(
    tmp_path: Path, managed_block: str
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    original = (
        "# owner bytes\n"
        + managed_block
        + "\n"
        + _managed_repair_registration(codex_home)
    )
    config.write_text(original, encoding="utf-8")

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert config.read_text(encoding="utf-8") == "# owner bytes\n" + managed_block
    assert not config.with_suffix(".toml.bak").exists()


def test_install_preserves_user_owned_environment_policy(tmp_path: Path) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    original = (
        '[shell_environment_policy]\ninherit = "none"\nset = { HOME = "/owner" }\n'
        + "\n"
        + _managed_repair_registration(codex_home)
    )
    config.write_text(original, encoding="utf-8")

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert config.read_text(encoding="utf-8") == (
        '[shell_environment_policy]\ninherit = "none"\nset = { HOME = "/owner" }\n'
    )
    assert not config.with_suffix(".toml.bak").exists()


def _managed_environment_policy_block(*, legacy: bool = False) -> str:
    begin = "# >>> triad-codex-dispatch managed shell_environment_policy >>>"
    end = "# <<< triad-codex-dispatch managed shell_environment_policy <<<"
    if legacy:
        body = '[shell_environment_policy]\ninherit = "core"\n'
    else:
        body = (
            '[shell_environment_policy]\ninherit = "all"\n'
            'exclude = ["LD_*", "DYLD_*", "NODE_OPTIONS", "NODE_PATH", "PYTHON*", "BASH_ENV", "ENV", "PERL5LIB", "RUBYOPT", "RUBYLIB"]\n'
        )
    return begin + "\n" + body + end + "\n"


@pytest.mark.parametrize("legacy", (False, True), ids=("current", "legacy"))
def test_remove_deletes_only_exact_managed_environment_policy_bytes(
    tmp_path: Path, legacy: bool
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    prefix = "# preserve prefix\n[custom]\nvalue = \"unchanged\"\n\n"
    suffix = "\n# preserve suffix\n\n"
    config.write_text(
        prefix + _managed_environment_policy_block(legacy=legacy) + suffix,
        encoding="utf-8",
    )

    result, _env, _launchers = _run_bootstrap(
        tmp_path, arg="--remove", env_overrides={"CODEX_HOME": str(codex_home)}
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert config.read_text(encoding="utf-8") == prefix + suffix


def test_remove_config_fragment_failure_preserves_config_after_earlier_cleanup(
    tmp_path: Path,
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    config_before = _managed_environment_policy_block().encode("utf-8")
    config.write_bytes(config_before)
    rules = codex_home / "rules" / "triad-codex-dispatch.rules"
    rules.parent.mkdir()
    rules_before = FROZEN_LEGACY_RULES
    rules.write_bytes(rules_before)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--remove",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_TEST_FAIL_CONFIG_FRAGMENT_REMOVE": "1",
        },
    )

    assert result.returncode != 0
    assert "injected config fragment remove failure" in result.stderr
    assert config.read_bytes() == config_before
    assert not rules.exists()


@pytest.mark.parametrize("legacy", (False, True), ids=("current", "legacy"))
def test_remove_preserves_edited_managed_environment_policy_bytes(
    tmp_path: Path, legacy: bool
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    block = _managed_environment_policy_block(legacy=legacy).replace(
        "# <<<", "# owner edit\n# <<<"
    )
    original = "# owner prefix\n" + block + "# owner suffix\n\n"
    config.write_text(original, encoding="utf-8")

    result, _env, _launchers = _run_bootstrap(
        tmp_path, arg="--remove", env_overrides={"CODEX_HOME": str(codex_home)}
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "could not remove the managed [shell_environment_policy] fragment" in result.stdout
    assert config.read_text(encoding="utf-8") == original


@pytest.mark.parametrize(
    "marker_text",
    [
        "# >>> triad-codex-dispatch managed shell_environment_policy >>>\n"
        '[shell_environment_policy]\ninherit = "all"\n',
        "# <<< triad-codex-dispatch managed shell_environment_policy <<<\n",
        "# >>> triad-codex-dispatch managed shell_environment_policy >>>\n"
        "# <<< triad-codex-dispatch managed shell_environment_policy <<<\n"
        "# >>> triad-codex-dispatch managed shell_environment_policy >>>\n"
        "# <<< triad-codex-dispatch managed shell_environment_policy <<<\n",
    ],
    ids=("unmatched-begin", "unmatched-end", "duplicate-markers"),
)
def test_remove_preserves_unmatched_or_duplicate_policy_markers(
    tmp_path: Path, marker_text: str
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    original = "# owner prefix\n" + marker_text + "# owner suffix\n\n"
    config.write_text(original, encoding="utf-8")

    result, _env, _launchers = _run_bootstrap(
        tmp_path, arg="--remove", env_overrides={"CODEX_HOME": str(codex_home)}
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "could not remove the managed [shell_environment_policy] fragment" in result.stdout
    assert config.read_text(encoding="utf-8") == original


def _managed_environment_policy_bytes(*, legacy: bool, newline: bytes) -> bytes:
    return _managed_environment_policy_block(legacy=legacy).encode("utf-8").replace(
        b"\n", newline
    )


@pytest.mark.parametrize("legacy", (False, True), ids=("current", "legacy"))
def test_install_removes_crlf_current_or_legacy_managed_bytes(
    tmp_path: Path, legacy: bool
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    prefix = b"# preserve CRLF prefix\r\n[custom]\r\nvalue = \"unchanged\"\r\n\r\n"
    owner_suffix = b"\r\n# preserve CRLF suffix\r\n\r\n"
    suffix = (
        owner_suffix + b"\n"
        + _managed_repair_registration(codex_home).encode("utf-8")
    )
    original = prefix + _managed_environment_policy_bytes(legacy=legacy, newline=b"\r\n") + suffix
    config.write_bytes(original)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    expected = prefix + owner_suffix
    assert config.read_bytes() == expected
    assert not config.with_suffix(".toml.bak").exists()


@pytest.mark.parametrize("legacy", (False, True), ids=("current", "legacy"))
def test_remove_preserves_crlf_outside_exact_current_or_legacy_block(
    tmp_path: Path, legacy: bool
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    prefix = b"# preserve CRLF prefix\r\n[custom]\r\nvalue = \"unchanged\"\r\n\r\n"
    suffix = b"\r\n# preserve CRLF suffix\r\n\r\n"
    config.write_bytes(
        prefix + _managed_environment_policy_bytes(legacy=legacy, newline=b"\r\n") + suffix
    )

    result, _env, _launchers = _run_bootstrap(
        tmp_path, arg="--remove", env_overrides={"CODEX_HOME": str(codex_home)}
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert config.read_bytes() == prefix + suffix


@pytest.mark.parametrize("legacy", (False, True), ids=("current", "legacy"))
@pytest.mark.parametrize(
    "owner_extension",
    ('set = { HOME = "/owner" }\n', 'include_only = ["HOME"]\n', 'include_only = [\n'),
    ids=("set", "include-only", "malformed-include-only"),
)
def test_remove_preserves_extended_or_malformed_policy_table_after_marker_end(
    tmp_path: Path, legacy: bool, owner_extension: str
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    original = (
        b"# owner prefix\n"
        + _managed_environment_policy_bytes(legacy=legacy, newline=b"\n")
        + owner_extension.encode("utf-8")
        + b"# owner suffix\n\n"
    )
    config.write_bytes(original)

    result, _env, _launchers = _run_bootstrap(
        tmp_path, arg="--remove", env_overrides={"CODEX_HOME": str(codex_home)}
    )

    if owner_extension == "include_only = [\n":
        assert result.returncode != 0
    else:
        assert result.returncode == 0, result.stderr + result.stdout
        assert "could not remove the managed [shell_environment_policy] fragment" in result.stdout
    assert config.read_bytes() == original


# --- Legacy opt-in shell entry compatibility and removal ---------------------








def test_shell_entry_refuses_unmanaged_codex_triad_function(tmp_path):
    shell_rc = tmp_path / "shellrc"
    unmanaged = 'codex-triad() { command codex --profile old --search "$@"; }\n'
    shell_rc.write_text(unmanaged, encoding="utf-8")

    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "leaving unmanaged codex-triad entry" in result.stdout
    assert shell_rc.read_text(encoding="utf-8") == unmanaged


def test_shell_entry_transaction_preserves_foreign_replacement_after_capture(
    tmp_path: Path,
) -> None:
    shell_rc = tmp_path / "shellrc"
    shell_rc.write_bytes(b"# owner prefix\n" + FROZEN_LEGACY_SHELL_ENTRY)
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    foreign = b"# foreign shell RC replacement\nowner bytes stay exact\n"
    replacement = tmp_path / "foreign-shellrc"
    replacement.write_bytes(foreign)
    raced, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--install",
        env_overrides={
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
            "TRIAD_BOOTSTRAP_TEST_SWAP_SHELL_RC_BEFORE_PUBLISH": str(replacement),
        },
    )

    assert raced.returncode != 0
    current = shell_rc.read_bytes()
    assert current == foreign
    assert b"# >>> triad-codex-dispatch codex-triad >>>" not in current
    assert b"# <<< triad-codex-dispatch codex-triad <<<" not in current


def test_install_legacy_quarantine_preserves_foreign_replacement_after_capture(
    tmp_path: Path,
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home = tmp_path / "codex-home"
    target = codex_home / "agents" / "claude-wrapper-repair.toml"
    target.parent.mkdir(parents=True)
    target.write_bytes(
        b"# Codex named subagent for Claude wrapper repair agent\n"
        b"# Installed by bootstrap to the Codex personal agent-discovery scope\n"
        b'name = "claude-wrapper-repair"\n'
    )
    foreign = b"# foreign replacement\nname = \"owner-controlled\"\n"
    replacement = tmp_path / "foreign-legacy-agent"
    replacement.write_bytes(foreign)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_TEST_SWAP_LEGACY_AGENT_BEFORE_QUARANTINE": str(
                replacement
            ),
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "could not quarantine legacy repair agent" in result.stdout
    assert target.read_bytes() == foreign
    assert not list(codex_home.glob(".triad-quarantine-*"))


@pytest.mark.parametrize("mode", ("--install", "--remove"))
@pytest.mark.parametrize("newline", (b"\n", b"\r\n"), ids=("lf", "crlf"))
@pytest.mark.parametrize(
    "marker_case",
    ("begin-only", "reversed", "duplicate", "embedded"),
)
def test_bootstrap_rejects_malformed_shell_markers_without_changing_bytes(
    tmp_path: Path, mode: str, newline: bytes, marker_case: str
) -> None:
    begin = b"# >>> triad-codex-dispatch codex-triad >>>"
    end = b"# <<< triad-codex-dispatch codex-triad <<<"
    block = begin + newline + b"codex-triad() { :; }" + newline + end + newline
    if marker_case == "begin-only":
        markers = begin + newline + b"owner tail" + newline
    elif marker_case == "reversed":
        markers = end + newline + b"owner middle" + newline + begin + newline
    elif marker_case == "embedded":
        markers = (
            b'echo "'
            + begin
            + b'"'
            + newline
            + b'echo "'
            + end
            + b'"'
            + newline
        )
    else:
        markers = block + block
    original = b"# owner prefix" + newline + markers + b"# owner suffix" + newline
    shell_rc = tmp_path / "shellrc"
    shell_rc.write_bytes(original)

    overrides = {
        "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
        "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
    }
    if mode == "--install":
        overrides["TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE"] = "1"

    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        arg=mode,
        env_overrides=overrides,
    )

    assert result.returncode != 0
    assert "malformed managed codex-triad shell markers" in result.stderr
    assert shell_rc.read_bytes() == original
    assert not any(launcher_bin.iterdir())
    assert not (Path(env["HOME"]) / ".codex").exists()


# --- Fast-follow: --remove uninstall path ------------------------------------


def test_remove_uninstalls_managed_artifacts_and_shell_entry(tmp_path):
    shell_rc = tmp_path / "shellrc"
    overrides = {"TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc)}
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
    helper = _load_bootstrap_repair_module()
    codex_home = home / ".codex"
    profile = codex_home / "triad-codex-dispatch.config.toml"
    profile.parent.mkdir(parents=True, exist_ok=True)
    profile.write_bytes(FROZEN_LEGACY_PROFILE)
    rules = codex_home / "rules" / "triad-codex-dispatch.rules"
    rules.parent.mkdir(parents=True)
    rules.write_bytes(FROZEN_LEGACY_RULES)
    config = codex_home / "config.toml"
    config.write_bytes(helper.current_config_fragment(b"\n"))
    shell_rc.write_bytes(FROZEN_LEGACY_SHELL_ENTRY)

    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    result2, _env2, _launcher_bin2 = _run_bootstrap(
        tmp_path, repo_root=repo_root, arg="--remove", env_overrides=overrides
    )
    assert result2.returncode == 0, result2.stderr + result2.stdout
    for name in ("claude_wrapper.py", "gemini_wrapper.py", "antigravity_wrapper.py"):
        assert not (launcher_bin / name).exists()
    for name in ("claude-wrapper-repair", "gemini-wrapper-repair", "agy-wrapper-repair"):
        assert not (home / ".codex" / "agents" / f"{name}.toml").exists()
    assert not profile.exists()
    assert not rules.exists()
    assert not config.exists()
    assert "codex-triad" not in shell_rc.read_text(encoding="utf-8")
    # learned classifier patches are user data and must survive --remove
    assert classifier.is_file()


def test_remove_only_preserves_owner_shell_bytes_and_mode(tmp_path: Path) -> None:
    prefix = b"# owner prefix\n"
    suffix = b"# owner suffix\n"
    shell_rc = tmp_path / "shellrc"
    shell_rc.write_bytes(prefix + FROZEN_LEGACY_SHELL_ENTRY + suffix)
    shell_rc.chmod(0o600)

    result, _env, _launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--remove",
        env_overrides={"TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "removed managed codex-triad shell entry" in result.stdout
    assert shell_rc.read_bytes() == prefix + suffix
    assert stat.S_IMODE(shell_rc.stat().st_mode) == 0o600


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


@pytest.mark.parametrize(
    ("kind", "relative_target", "marker"),
    (
        (
            "profile",
            "triad-codex-dispatch.config.toml",
            b"# triad-codex-dispatch managed runtime profile",
        ),
        (
            "rules",
            "rules/triad-codex-dispatch.rules",
            b"# triad-codex-dispatch managed command rules",
        ),
    ),
)
@pytest.mark.parametrize("placement", ("embedded", "later-line"))
def test_remove_preserves_user_artifact_with_nonleading_managed_marker(
    tmp_path: Path,
    kind: str,
    relative_target: str,
    marker: bytes,
    placement: str,
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    target = codex_home / relative_target
    target.parent.mkdir(parents=True, exist_ok=True)
    if placement == "embedded":
        original = b'owner = "' + marker + b'"\n'
    else:
        original = b"# owner file\n" + marker + b"\n"
    target.write_bytes(original)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--remove",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert target.read_bytes() == original


@pytest.mark.parametrize(
    ("kind", "relative_target", "managed", "swap_env"),
    (
        (
            "profile",
            "triad-codex-dispatch.config.toml",
            FROZEN_LEGACY_PROFILE,
            "TRIAD_BOOTSTRAP_TEST_SWAP_PROFILE_BEFORE_REMOVE",
        ),
        (
            "rules",
            "rules/triad-codex-dispatch.rules",
            FROZEN_LEGACY_RULES,
            "TRIAD_BOOTSTRAP_TEST_SWAP_RULES_BEFORE_REMOVE",
        ),
        (
            "legacy-agent",
            "agents/claude-wrapper-repair.toml",
            (
                b"# Codex named subagent for Claude wrapper repair agent\n"
                b"# Installed by bootstrap to the Codex personal agent-discovery scope\n"
                b'name = "claude-wrapper-repair"\n'
            ),
            "TRIAD_BOOTSTRAP_TEST_SWAP_LEGACY_AGENT_BEFORE_REMOVE",
        ),
    ),
)
def test_remove_preserves_foreign_swap_after_managed_ownership_check(
    tmp_path: Path,
    kind: str,
    relative_target: str,
    managed: bytes,
    swap_env: str,
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    target = codex_home / relative_target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(managed)
    foreign = b"foreign replacement must survive\n"
    swap_source = tmp_path / f"{kind}-foreign-swap"
    swap_source.write_bytes(foreign)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--remove",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            swap_env: str(swap_source),
        },
    )

    assert result.returncode != 0
    assert "path changed before transaction claim" in result.stderr
    assert target.read_bytes() == foreign


# --- MUST-land 5 adjacency: legacy sandbox settings disable profiles ---------




def test_install_fails_when_codex_home_inside_workspace_via_case_variant(tmp_path):
    """macOS case-insensitivity workspace-escape bypass (finding #2, 2026-07-05).

    A CODEX_HOME that resolves INSIDE the sandbox-writable workspace through a
    case-variant path (WS vs ws) is the SAME executable-rewrite chain as the
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
