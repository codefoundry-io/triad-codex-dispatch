import os
import json
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
    migration_dir = repo_root / "migration"
    migration_dir.mkdir()
    shutil.copy2(
        ROOT / "migration" / "requirements.recommended.toml",
        migration_dir / "requirements.recommended.toml",
    )
    if real_agents:
        for path in (ROOT / "agents").glob("*.toml"):
            shutil.copy2(path, agents_dir / path.name)
        shutil.copytree(ROOT / "skills", skills_dir)
    else:
        shutil.copy2(
            ROOT / "agents" / f"{REPAIR_ANALYZER}.toml",
            agents_dir / f"{REPAIR_ANALYZER}.toml",
        )
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
    arg="--check",
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


def _load_bootstrap_repair_module():
    spec = importlib.util.spec_from_file_location("bootstrap_repair_test", BOOTSTRAP_REPAIR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_bootstrap_help_describes_google_route_fallback() -> None:
    result = subprocess.run(
        ["bash", str(BOOTSTRAP), "--help"],
        text=True,
        capture_output=True,
        timeout=5,
    )

    assert result.returncode == 2
    assert "agy, or configured Gemini Enterprise/Business" in result.stderr


def test_bootstrap_repair_help_exposes_explicit_install_and_remove() -> None:
    result = subprocess.run(
        [sys.executable, str(BOOTSTRAP_REPAIR), "--help"],
        text=True,
        capture_output=True,
        timeout=5,
    )

    assert result.returncode == 0, result.stderr
    assert "install" in result.stdout
    assert "remove" in result.stdout


def test_bootstrap_routes_classifier_artifacts_and_config_mutations_through_helper() -> None:
    text = BOOTSTRAP.read_text(encoding="utf-8")

    assert "bootstrap_repair.py\" classifier" in text
    assert "bootstrap_repair.py\" managed-artifact" in text
    assert "bootstrap_repair.py\" config-fragment" in text
    assert "profile_path.write_text" not in text
    assert "rules_path.write_text" not in text
    assert "Path(str(config_path) + \".bak\").write_bytes" not in text
    assert "os.replace(tmp_name, config_path)" not in text
    assert "config_path.unlink()" not in text


def test_bootstrap_repair_refuses_embedded_provenance_marker(tmp_path: Path) -> None:
    helper = _load_bootstrap_repair_module()
    source = tmp_path / "source.toml"
    source.write_text(
        f'{REPAIR_ANALYZER_MARKER}\nname = "{REPAIR_ANALYZER}"\n', encoding="utf-8"
    )
    analyzer = tmp_path / "agents" / f"{REPAIR_ANALYZER}.toml"
    analyzer.parent.mkdir()
    foreign = f'description = "{REPAIR_ANALYZER_MARKER}"\n'
    analyzer.write_text(foreign, encoding="utf-8")
    config = tmp_path / "config.toml"
    apply_patch = tmp_path / "apply_patch.py"
    apply_patch.write_text("# apply\n", encoding="utf-8")

    status = helper.main(
        [
            "install", "--source", str(source), "--config", str(config),
            "--analyzer", str(analyzer), "--launcher", str(tmp_path / "triad-apply-repair"),
            "--apply-patch", str(apply_patch),
        ]
    )

    assert status == 3
    assert analyzer.read_text(encoding="utf-8") == foreign


def test_bootstrap_repair_refuses_exact_analyzer_marker_inside_multiline_string(
    tmp_path: Path,
) -> None:
    helper, args, analyzer, _config, _launcher = _repair_install_args(tmp_path)
    analyzer.parent.mkdir()
    foreign = (
        'name = "foreign-analyzer"\n'
        'description = """\n'
        f"{helper.ANALYZER_MARKER}\n"
        'still foreign\n"""\n'
    )
    analyzer.write_text(foreign, encoding="utf-8")

    assert helper.main(args) == 3
    assert analyzer.read_text(encoding="utf-8") == foreign


def test_bootstrap_repair_refuses_exact_launcher_marker_inside_python_multiline_string(
    tmp_path: Path,
) -> None:
    helper, args, _analyzer, _config, launcher = _repair_install_args(tmp_path)
    foreign = f'payload = """\n{helper.LAUNCHER_MARKER}\nstill foreign\n"""\n'
    launcher.write_text(foreign, encoding="utf-8")

    assert helper.main(args) == 3
    assert launcher.read_text(encoding="utf-8") == foreign


def test_bootstrap_repair_preserves_config_markers_inside_multiline_string(
    tmp_path: Path,
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    foreign = (
        'description = """\n'
        f"{helper.REG_BEGIN}\n"
        f"[agents.{REPAIR_ANALYZER}]\n"
        'description = "looks generated"\n'
        f'config_file = "{analyzer}"\n'
        f"{helper.REG_END}\n"
        '"""\n'
    ).encode("utf-8")
    config.write_bytes(foreign)

    assert helper.main(args) == 0
    assert helper.main(
        ["remove", "--config", str(config), "--analyzer", str(analyzer),
         "--launcher", str(launcher)]
    ) == 0
    assert config.read_bytes() == foreign


def test_bootstrap_repair_refuses_noncanonical_marker_wrapped_registration(
    tmp_path: Path,
) -> None:
    helper, args, _analyzer, config, _launcher = _repair_install_args(tmp_path)
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


def test_bootstrap_repair_revalidates_target_before_replacement(tmp_path: Path) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "target"
    target.write_text("before\n", encoding="utf-8")
    before = helper.read_state(target)
    temp = helper.stage(target, b"after\n", 0o600)
    target.write_text("race\n", encoding="utf-8")

    with pytest.raises(helper.Refusal):
        helper.publish_to(temp, target, before, [])

    assert target.read_text(encoding="utf-8") == "race\n"
    temp.unlink()


def test_bootstrap_repair_preserves_foreign_swap_between_check_and_publish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "target"
    target.write_bytes(b"managed-before\n")
    before = helper.read_state(target)
    assert before is not None
    temp = helper.stage(target, b"managed-after\n", 0o600)
    foreign = b"foreign-between-check-and-publish\n"
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
        helper.publish_to(temp, target, before, [])

    assert injected
    assert target.read_bytes() == foreign
    helper.cleanup(temp)
    assert not list(tmp_path.glob(".*.triad-claim-*"))


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


def test_bootstrap_repair_never_clobbers_foreign_create_during_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "target"
    temp = helper.stage(target, b"managed-after\n", 0o600)
    foreign = b"foreign-created-before-link\n"
    original_link = helper.os.link
    injected = False

    def create_foreign_before_link(source, destination):
        nonlocal injected
        if destination == target and not injected:
            injected = True
            target.write_bytes(foreign)
        return original_link(source, destination)

    monkeypatch.setattr(helper.os, "link", create_foreign_before_link)
    with pytest.raises(helper.Refusal, match="without overwriting"):
        helper.publish_to(temp, target, None, [])

    assert injected
    assert target.read_bytes() == foreign
    helper.cleanup(temp)


def test_bootstrap_repair_non_bmp_config_path_is_valid_toml(tmp_path: Path) -> None:
    helper = _load_bootstrap_repair_module()
    source = tmp_path / "source.toml"
    source.write_text(
        f'{REPAIR_ANALYZER_MARKER}\nname = "{REPAIR_ANALYZER}"\n', encoding="utf-8"
    )
    codex_home = tmp_path / "codex-😀"
    analyzer = codex_home / "agents" / f"{REPAIR_ANALYZER}.toml"
    apply_patch = tmp_path / "apply_patch.py"
    apply_patch.write_text("# apply\n", encoding="utf-8")
    config = codex_home / "config.toml"

    status = helper.main(
        [
            "install", "--source", str(source), "--config", str(config),
            "--analyzer", str(analyzer), "--launcher", str(tmp_path / "triad-apply-repair"),
            "--apply-patch", str(apply_patch),
        ]
    )

    assert status == 0
    assert tomllib.loads(config.read_text(encoding="utf-8"))["agents"][REPAIR_ANALYZER]["config_file"] == str(analyzer)


def test_bootstrap_repair_apply_launcher_pins_classifier_path(tmp_path: Path) -> None:
    helper, args, _analyzer, _config, launcher = _repair_install_args(tmp_path)
    classifier = tmp_path / "config with spaces" / "classifier '$() `'.json"
    args.extend(["--classifier", str(classifier)])

    assert helper.main(args) == 0

    text = launcher.read_text(encoding="utf-8")
    assert "TRIAD_CLASSIFIER_EXTENSION" in text
    assert json.dumps(str(classifier), ensure_ascii=False) in text
    assert "os.execve(" in text


def test_installed_launchers_keep_custom_classifier_in_a_fresh_environment(
    tmp_path: Path,
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    classifier = tmp_path / "config with spaces" / "classifier '$() `'.json"
    probe = (
        "#!/usr/bin/env python3\n"
        "import os\n"
        "print(os.environ['TRIAD_CLASSIFIER_EXTENSION'])\n"
    )
    for name in ("gemini_wrapper.py", "apply_patch.py"):
        path = repo_root / "bin" / name
        path.write_text(probe, encoding="utf-8")
        path.chmod(0o755)
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
    apply = subprocess.run(
        [str(launcher_dir / "triad-apply-repair")],
        env=fresh_env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert provider.returncode == 0, provider.stderr
    assert apply.returncode == 0, apply.stderr
    assert provider.stdout.strip() == str(classifier)
    assert apply.stdout.strip() == str(classifier)


def test_bootstrap_repair_rejects_whitespace_python_shebang() -> None:
    helper = _load_bootstrap_repair_module()

    with pytest.raises(helper.Refusal, match="shebang cannot encode"):
        helper.launcher_text(Path("/tmp/python runtime/bin/python3"), Path("/tmp/apply.py"))


def test_bootstrap_repair_reports_explicit_refusal_and_success_statuses(tmp_path: Path) -> None:
    helper = _load_bootstrap_repair_module()
    missing = helper.main(
        ["install", "--source", str(tmp_path / "missing"), "--config", str(tmp_path / "config"),
         "--analyzer", str(tmp_path / "analyzer"), "--launcher", str(tmp_path / "launcher"),
         "--apply-patch", str(tmp_path / "apply")]
    )
    removed = helper.main(
        ["remove", "--config", str(tmp_path / "config"), "--analyzer", str(tmp_path / "analyzer"),
         "--launcher", str(tmp_path / "launcher")]
    )

    assert missing == 3
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
    launcher.write_bytes(helper.launcher_text(Path(sys.executable), tmp_path / "apply.py"))

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
    source = tmp_path / "source.toml"
    source.write_text(
        f'{REPAIR_ANALYZER_MARKER}\nname = "{REPAIR_ANALYZER}"\n', encoding="utf-8"
    )
    apply_patch = tmp_path / "apply_patch.py"
    apply_patch.write_text("# apply\n", encoding="utf-8")
    analyzer, config, launcher = (
        tmp_path / "agents" / f"{REPAIR_ANALYZER}.toml",
        tmp_path / "config.toml",
        tmp_path / "triad-apply-repair",
    )
    assert helper.main(
        ["install", "--source", str(source), "--config", str(config),
         "--analyzer", str(analyzer), "--launcher", str(launcher),
         "--apply-patch", str(apply_patch)]
    ) == 0
    original_remove = helper.remove_state

    def fail_launcher(state, journal):
        if state.path == launcher:
            raise OSError("injected launcher removal failure")
        original_remove(state, journal)

    monkeypatch.setattr(helper, "remove_state", fail_launcher)
    assert helper.main(
        ["remove", "--config", str(config), "--analyzer", str(analyzer),
         "--launcher", str(launcher)]
    ) == 3
    assert analyzer.exists()
    assert REPAIR_ANALYZER in tomllib.loads(config.read_text(encoding="utf-8"))["agents"]


def _repair_install_args(tmp_path: Path) -> tuple[object, list[str], Path, Path, Path]:
    helper = _load_bootstrap_repair_module()
    source = tmp_path / "source.toml"
    source.write_text(
        f'{REPAIR_ANALYZER_MARKER}\nname = "{REPAIR_ANALYZER}"\n', encoding="utf-8"
    )
    apply_patch = tmp_path / "apply_patch.py"
    apply_patch.write_text("# apply\n", encoding="utf-8")
    analyzer = tmp_path / "agents" / f"{REPAIR_ANALYZER}.toml"
    config = tmp_path / "config.toml"
    launcher = tmp_path / "triad-apply-repair"
    return helper, [
        "install", "--source", str(source), "--config", str(config),
        "--analyzer", str(analyzer), "--launcher", str(launcher),
        "--apply-patch", str(apply_patch),
    ], analyzer, config, launcher


def test_bootstrap_repair_preflight_install_is_read_only(tmp_path: Path) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    source = tmp_path / "source.toml"
    apply_patch = tmp_path / "apply_patch.py"
    before = {path: path.read_bytes() for path in (source, apply_patch)}
    args[0] = "preflight-install"

    assert helper.main(args) == 0

    assert {path: path.read_bytes() for path in (source, apply_patch)} == before
    assert not analyzer.parent.exists()
    assert not config.exists()
    assert not launcher.exists()
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "apply_patch.py",
        "source.toml",
    ]


def test_bootstrap_repair_rolls_back_replace_when_parent_fsync_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    original_fsync = helper.fsync_parent
    failed = False

    def fail_config(path):
        nonlocal failed
        if path == config and not failed:
            failed = True
            raise OSError("injected config parent fsync failure")
        original_fsync(path)

    monkeypatch.setattr(helper, "fsync_parent", fail_config)
    assert helper.main(args) == 3
    assert not analyzer.exists()
    assert not config.exists()
    assert not launcher.exists()


def test_bootstrap_repair_rollback_preserves_foreign_replace_after_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    original_fsync = helper.fsync_parent
    failed = False
    foreign = b"foreign replacement\n"

    def replace_config_then_fail(path):
        nonlocal failed
        if path == config and not failed:
            failed = True
            replacement = tmp_path / "foreign-config"
            replacement.write_bytes(foreign)
            os.replace(replacement, config)
            raise OSError("injected config parent fsync failure after foreign replace")
        original_fsync(path)

    monkeypatch.setattr(helper, "fsync_parent", replace_config_then_fail)
    assert helper.main(args) == 3
    assert config.read_bytes() == foreign
    assert not analyzer.exists()
    assert not launcher.exists()


def test_bootstrap_repair_rolls_back_unlink_when_parent_fsync_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    assert helper.main(args) == 0
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
    assert helper.main(["remove", "--config", str(config), "--analyzer", str(analyzer),
                        "--launcher", str(launcher)]) == 3
    assert config.read_bytes() == before
    assert analyzer.exists()
    assert launcher.exists()


def test_bootstrap_repair_rollback_preserves_foreign_create_after_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    assert helper.main(args) == 0
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
    assert helper.main(
        ["remove", "--config", str(config), "--analyzer", str(analyzer),
         "--launcher", str(launcher)]
    ) == 3
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
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    assert helper.main(args) == 0
    config_before = config.read_bytes()
    analyzer_before = analyzer.read_bytes()
    launcher_before = launcher.read_bytes()
    original_remove = helper.remove_state

    def fail_analyzer_removal(state, journal):
        if state.path == analyzer:
            raise OSError("injected analyzer removal failure")
        return original_remove(state, journal)

    monkeypatch.setattr(helper, "remove_state", fail_analyzer_removal)
    assert helper.main(
        ["remove", "--config", str(config), "--analyzer", str(analyzer),
         "--launcher", str(launcher)]
    ) == 3
    assert config.read_bytes() == config_before
    assert analyzer.read_bytes() == analyzer_before
    assert launcher.read_bytes() == launcher_before


@pytest.mark.parametrize("swapped", ("apply", "runtime"))
def test_bootstrap_repair_rejects_apply_or_runtime_identity_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, swapped: str
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    apply_patch = Path(args[args.index("--apply-patch") + 1])
    runtime = tmp_path / "runtime"
    runtime.write_text("runtime\n", encoding="utf-8")
    args.extend(["--python", str(runtime)])
    watched = apply_patch if swapped == "apply" else runtime
    original_stage = helper.stage
    calls = 0

    def swap_after_first_stage(*stage_args):
        nonlocal calls
        calls += 1
        result = original_stage(*stage_args)
        if calls == 1:
            watched.write_text("swapped\n", encoding="utf-8")
        return result

    monkeypatch.setattr(helper, "stage", swap_after_first_stage)
    assert helper.main(args) == 3
    assert not analyzer.exists()
    assert not config.exists()
    assert not launcher.exists()
    assert not list(tmp_path.rglob(".*.tmp"))


def test_bootstrap_repair_cleans_staged_files_when_later_stage_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    original_stage = helper.stage
    calls = 0

    def fail_second_stage(*stage_args):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected later stage failure")
        return original_stage(*stage_args)

    monkeypatch.setattr(helper, "stage", fail_second_stage)
    assert helper.main(args) == 3
    assert not list(tmp_path.rglob(".*.tmp"))
    assert not analyzer.exists() and not config.exists() and not launcher.exists()


def test_bootstrap_repair_outer_cleanup_retries_one_shot_unlink_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    parsed_args = helper.parser().parse_args(args)
    original_stage = helper.stage
    original_unlink = helper.os.unlink
    stage_calls = 0
    unlink_calls = 0

    def fail_second_stage(*stage_args):
        nonlocal stage_calls
        stage_calls += 1
        if stage_calls == 2:
            raise OSError("outer primary stage failure")
        return original_stage(*stage_args)

    def fail_unlink_once(path):
        nonlocal unlink_calls
        unlink_calls += 1
        if unlink_calls == 1:
            raise OSError("one-shot outer cleanup unlink failure")
        original_unlink(path)

    with monkeypatch.context() as patcher:
        patcher.setattr(helper, "stage", fail_second_stage)
        patcher.setattr(helper.os, "unlink", fail_unlink_once)
        with pytest.raises(OSError, match="outer primary stage failure") as captured:
            helper.install(parsed_args)

    assert not isinstance(captured.value, helper.TransactionFailure)
    assert unlink_calls == 2
    assert not list(tmp_path.rglob(".*.tmp"))
    assert not analyzer.exists() and not config.exists() and not launcher.exists()


def test_bootstrap_repair_outer_cleanup_reports_persistent_unlink_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    parsed_args = helper.parser().parse_args(args)
    original_stage = helper.stage
    original_unlink = helper.os.unlink
    stage_calls = 0
    unlink_calls = 0

    def fail_second_stage(*stage_args):
        nonlocal stage_calls
        stage_calls += 1
        if stage_calls == 2:
            raise OSError("outer primary stage failure")
        return original_stage(*stage_args)

    def always_fail_unlink(_path):
        nonlocal unlink_calls
        unlink_calls += 1
        raise OSError("persistent outer cleanup unlink failure")

    with monkeypatch.context() as patcher:
        patcher.setattr(helper, "stage", fail_second_stage)
        patcher.setattr(helper.os, "unlink", always_fail_unlink)
        with pytest.raises(helper.TransactionFailure) as captured:
            helper.install(parsed_args)

    assert "outer primary stage failure" in str(captured.value)
    assert "persistent outer cleanup unlink failure" in str(captured.value)
    assert unlink_calls == 2
    leaked = list(tmp_path.rglob(".*.tmp"))
    assert len(leaked) == 1
    original_unlink(leaked[0])
    assert not analyzer.exists() and not config.exists() and not launcher.exists()


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


def test_bootstrap_repair_cleans_temps_after_publish_or_readback_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    original_link = helper.os.link

    def fail_config_publish(temp, target):
        if target == config:
            raise OSError("injected no-clobber publish failure")
        original_link(temp, target)

    monkeypatch.setattr(helper.os, "link", fail_config_publish)
    assert helper.main(args) == 3
    assert not list(tmp_path.rglob(".*.tmp"))
    assert not analyzer.exists() and not config.exists() and not launcher.exists()


def test_bootstrap_repair_rolls_back_post_replace_readback_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    original_read = helper.read_state
    config_reads = 0

    def fail_second_config_read(path):
        nonlocal config_reads
        if path == config:
            config_reads += 1
            if config_reads == 2:
                raise helper.Refusal("injected post-replace readback failure")
        return original_read(path)

    monkeypatch.setattr(helper, "read_state", fail_second_config_read)
    assert helper.main(args) == 3
    assert not analyzer.exists() and not config.exists() and not launcher.exists()
    assert not list(tmp_path.rglob(".*.tmp"))


def test_bootstrap_repair_rollback_continues_after_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper, args, analyzer, _config, launcher = _repair_install_args(tmp_path)
    assert helper.main(args) == 0
    before = analyzer.read_bytes()
    source = Path(args[args.index("--source") + 1])
    source.write_text(
        f'{REPAIR_ANALYZER_MARKER}\nname = "{REPAIR_ANALYZER}"\ndescription = "new"\n',
        encoding="utf-8",
    )
    original_fsync = helper.fsync_parent
    failed = False

    def fail_launcher_once(path):
        nonlocal failed
        if path == launcher and not failed:
            failed = True
            raise OSError("injected launcher fsync failure")
        original_fsync(path)

    monkeypatch.setattr(helper, "fsync_parent", fail_launcher_once)
    original_rollback = helper.rollback_mutation

    def refuse_launcher_rollback(mutation):
        if mutation.target == launcher:
            raise helper.Refusal("injected rollback refusal")
        original_rollback(mutation)

    monkeypatch.setattr(helper, "rollback_mutation", refuse_launcher_rollback)
    assert helper.main(args) == 3
    assert analyzer.read_bytes() == before


@pytest.mark.parametrize("unsafe", ("analyzer", "launcher"))
def test_bootstrap_repair_remove_refuses_unsafe_artifact_before_config_mutation(
    tmp_path: Path, unsafe: str
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    assert helper.main(args) == 0
    before = config.read_bytes()
    target = analyzer if unsafe == "analyzer" else launcher
    target.unlink()
    target.symlink_to(tmp_path / f"foreign-{unsafe}")

    assert helper.main(["remove", "--config", str(config), "--analyzer", str(analyzer),
                        "--launcher", str(launcher)]) == 3
    assert config.read_bytes() == before
    assert target.is_symlink()


@pytest.mark.parametrize("command", ("install", "remove"))
def test_bootstrap_repair_refuses_malformed_toml_inside_managed_markers(
    tmp_path: Path, command: str
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    malformed = (
        f"{helper.REG_BEGIN}\n[agents.{REPAIR_ANALYZER}]\nvalue = [\n{helper.REG_END}\n"
    ).encode("utf-8")
    config.write_bytes(malformed)
    if command == "install":
        status = helper.main(args)
    else:
        status = helper.main(["remove", "--config", str(config), "--analyzer", str(analyzer),
                              "--launcher", str(launcher)])
    assert status == 3
    assert config.read_bytes() == malformed
    assert not analyzer.exists() and not launcher.exists()


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
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    launcher.write_text(f'comment = "{helper.LAUNCHER_MARKER}"\n', encoding="utf-8")
    config.write_text(
        f'description = "{helper.REG_BEGIN} {helper.REG_END}"\n', encoding="utf-8"
    )
    assert helper.main(args) == 3
    assert launcher.read_text(encoding="utf-8").startswith("comment")
    assert config.read_text(encoding="utf-8").startswith("description")


@pytest.mark.parametrize("original", (b"", b'title = "no final newline"'))
def test_bootstrap_repair_config_round_trips_existing_bytes_exactly(
    tmp_path: Path, original: bytes
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    config.write_bytes(original)

    assert helper.main(args) == 0
    assert helper.main(
        ["remove", "--config", str(config), "--analyzer", str(analyzer),
         "--launcher", str(launcher)]
    ) == 0
    assert config.exists()
    assert config.read_bytes() == original


def _assert_repair_analyzer_install_state(codex_home: Path) -> None:
    """The one supported personal-scope repair agent is read-only and managed."""
    agents_dir = codex_home / "agents"
    analyzer = agents_dir / f"{REPAIR_ANALYZER}.toml"
    assert analyzer.is_file()
    text = analyzer.read_text(encoding="utf-8")
    assert REPAIR_ANALYZER_MARKER in text
    data = tomllib.loads(text)
    assert data["name"] == REPAIR_ANALYZER
    assert data["model"] == "gpt-5.6-terra"
    assert data["model_reasoning_effort"] == "high"
    assert data["sandbox_mode"] == "read-only"
    for name in ("claude-wrapper-repair", "gemini-wrapper-repair", "agy-wrapper-repair"):
        assert not (agents_dir / f"{name}.toml").exists()
    assert not list(agents_dir.glob("*-wrapper-repair.toml"))


def _assert_repair_analyzer_registration(codex_home: Path) -> None:
    text = (codex_home / "config.toml").read_text(encoding="utf-8")
    assert "# >>> triad-codex-dispatch managed repair analyzer registration >>>" in text
    data = tomllib.loads(text)
    registration = data["agents"][REPAIR_ANALYZER]
    assert registration["description"] == (
        "Read-only triad repair analyzer for untrusted vendor run logs."
    )
    assert registration["config_file"] == str(
        codex_home / "agents" / f"{REPAIR_ANALYZER}.toml"
    )


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
    # classifier + log dir install path is unchanged. It installs exactly one
    # read-only repair analyzer. Crucially the generated profile still PROMPTS
    # by default (approval_policy=on-request): defaulting profile+rules ON must
    # NOT silently auto-approve — the no-prompt `never` posture stays opt-in.
    result, env, _launcher_bin = _run_bootstrap(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    home = Path(env["HOME"])
    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    _assert_repair_analyzer_install_state(home / ".codex")
    _assert_repair_analyzer_registration(home / ".codex")
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
    assert "start a fresh Codex session" in result.stdout
    apply_launcher = _launcher_bin / "triad-apply-repair"
    assert apply_launcher.is_file()
    assert os.access(apply_launcher, os.X_OK)
    expected_python = json.dumps(str(Path(sys.executable).resolve()))
    expected_target = json.dumps(str(repo_root / "bin" / "apply_patch.py"))
    apply_text = apply_launcher.read_text(encoding="utf-8")
    assert (
        f"os.execve({expected_python}, [{expected_python}, \"-E\", {expected_target}] + sys.argv[1:], env)"
        in apply_text
    )
    assert 'env["TRIAD_CLASSIFIER_EXTENSION"]' in apply_text


def test_reinstall_refreshes_the_managed_repair_analyzer(tmp_path: Path) -> None:
    first, env, _launchers = _run_bootstrap(tmp_path, arg="--install")
    assert first.returncode == 0, first.stderr + first.stdout

    analyzer = Path(env["HOME"]) / ".codex" / "agents" / f"{REPAIR_ANALYZER}.toml"
    analyzer.write_text(
        f'{REPAIR_ANALYZER_MARKER}\nname = "{REPAIR_ANALYZER}"\n'
        'description = "stale managed content"\n',
        encoding="utf-8",
    )

    second, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        arg="--install",
    )

    assert second.returncode == 0, second.stderr + second.stdout
    assert analyzer.read_text(encoding="utf-8") == (
        Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
        / "agents"
        / f"{REPAIR_ANALYZER}.toml"
    ).read_text(encoding="utf-8")
    _assert_repair_analyzer_registration(Path(env["HOME"]) / ".codex")


def test_apply_repair_launcher_forwards_argv_unchanged(tmp_path: Path) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    capture = tmp_path / "apply-argv.json"
    (repo_root / "bin" / "apply_patch.py").write_text(
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "proposal = Path(sys.argv[sys.argv.index('--proposal-file') + 1])\n"
        "Path(os.environ['TRIAD_TEST_APPLY_ARGV']).write_text(json.dumps({\n"
        "    'argv': sys.argv[1:], 'proposal': proposal.read_text(encoding='utf-8')\n"
        "}))\n",
        encoding="utf-8",
    )
    installed, env, launcher_bin = _run_bootstrap(
        tmp_path, repo_root=repo_root, arg="--install"
    )
    assert installed.returncode == 0, installed.stderr + installed.stdout

    marker_name = "shell-injection-marker"
    proposal = tmp_path / f"proposal space ' $(touch {marker_name}) `touch {marker_name}`.json"
    proposal.write_text('{"classification":"retry"}\n', encoding="utf-8")
    args = ["--cli", "claude", "--proposal-file", str(proposal)]
    command = shlex.join([str(launcher_bin / "triad-apply-repair"), *args])
    unrelated_cwd = tmp_path / "unrelated-cwd"
    unrelated_cwd.mkdir()
    invoked = subprocess.run(
        ["/bin/sh", "-c", command],
        text=True,
        capture_output=True,
        env={**env, "TRIAD_TEST_APPLY_ARGV": str(capture)},
        cwd=unrelated_cwd,
        timeout=5,
    )

    assert invoked.returncode == 0, invoked.stderr
    recorded = json.loads(capture.read_text(encoding="utf-8"))
    assert recorded["argv"] == args
    assert recorded["proposal"] == '{"classification":"retry"}\n'
    assert not (unrelated_cwd / marker_name).exists()


def test_install_registers_repair_analyzer_without_replacing_agents_settings(
    tmp_path: Path,
) -> None:
    codex_home = tmp_path / "home" / ".codex"
    codex_home.mkdir(parents=True)
    (codex_home / "config.toml").write_text(
        "[agents]\nmax_threads = 7\n", encoding="utf-8"
    )

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0",
        },
    )

    assert result.returncode == 0, result.stderr + result.stdout
    data = tomllib.loads((codex_home / "config.toml").read_text(encoding="utf-8"))
    assert data["agents"]["max_threads"] == 7
    _assert_repair_analyzer_registration(codex_home)


def test_install_refuses_unmanaged_repair_analyzer_registration(tmp_path: Path) -> None:
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

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0",
        },
    )

    assert result.returncode != 0
    assert "unmanaged repair analyzer registration" in result.stderr
    assert config.read_text(encoding="utf-8") == foreign


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


@pytest.mark.parametrize("command", ("install", "remove"))
def test_bootstrap_repair_refuses_reversed_reserved_marker_comments(
    tmp_path: Path, command: str,
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    foreign = (
        f"{helper.REG_END}\n"
        f"{helper.REG_BEGIN}\n"
    ).encode("utf-8")
    config.write_bytes(foreign)

    if command == "install":
        status = helper.main(args)
    else:
        status = helper.main(
            ["remove", "--config", str(config), "--analyzer", str(analyzer),
             "--launcher", str(launcher)]
        )

    assert status == 3
    assert config.read_bytes() == foreign
    assert not analyzer.exists()
    assert not launcher.exists()


@pytest.mark.parametrize("command", ("install", "remove"))
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
    tmp_path: Path, command: str, markers: tuple[str, ...]
) -> None:
    helper, args, analyzer, config, launcher = _repair_install_args(tmp_path)
    marker_text = {"begin": helper.REG_BEGIN, "end": helper.REG_END}
    foreign = "".join(f"{marker_text[marker]}\n" for marker in markers).encode("utf-8")
    config.write_bytes(foreign)

    if command == "install":
        status = helper.main(args)
    else:
        status = helper.main(
            ["remove", "--config", str(config), "--analyzer", str(analyzer),
             "--launcher", str(launcher)]
        )

    assert status == 3
    assert config.read_bytes() == foreign
    assert not analyzer.exists()
    assert not launcher.exists()


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


def test_registration_publish_failure_rolls_back_new_analyzer(tmp_path: Path) -> None:
    codex_home = tmp_path / "home" / ".codex"
    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0",
            "TRIAD_BOOTSTRAP_TEST_FAIL_REPAIR_REGISTRATION_PUBLISH": "1",
        },
    )

    assert result.returncode != 0
    assert not (codex_home / "agents" / f"{REPAIR_ANALYZER}.toml").exists()
    assert not (codex_home / "config.toml").exists()


@pytest.mark.parametrize("kind", ("symlink", "fifo"))
def test_remove_refuses_unsafe_config_and_preserves_managed_analyzer(
    tmp_path: Path, kind: str
) -> None:
    installed, env, _launchers = _run_bootstrap(tmp_path, arg="--install")
    assert installed.returncode == 0, installed.stderr + installed.stdout
    codex_home = Path(env["HOME"]) / ".codex"
    analyzer = codex_home / "agents" / f"{REPAIR_ANALYZER}.toml"
    config = codex_home / "config.toml"
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
def test_install_refuses_nonmanaged_repair_analyzer_target(
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

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode != 0
    assert "repair analyzer" in result.stderr
    assert analyzer.is_symlink() if kind == "symlink" else analyzer.is_file()
    if kind == "symlink":
        assert analyzer.readlink() == before
    else:
        assert analyzer.read_text(encoding="utf-8") == before


def test_install_refuses_nonregular_repair_analyzer_target(tmp_path: Path) -> None:
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
                "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
                "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
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
def test_install_refuses_unsafe_repair_launcher_before_any_mutation(
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
                "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
                "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
            },
            timeout=15,
        )
        assert result.returncode != 0
        assert "repair apply launcher" in result.stderr
        assert sorted(path.name for path in launchers.iterdir()) == [
            "triad-apply-repair"
        ]
        assert config.read_bytes() == config_before
        assert not list(codex_home.glob("*.config.toml"))
        assert not (codex_home / "agents").exists()
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


def test_install_refuses_symlinked_repair_analyzer_parent_before_any_mutation(
    tmp_path: Path,
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    foreign_agents = tmp_path / "foreign-agents"
    foreign_agents.mkdir()
    (codex_home / "agents").symlink_to(foreign_agents, target_is_directory=True)

    result, _env, launchers = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
        timeout=15,
    )

    assert result.returncode != 0
    assert "unsafe ancestor" in result.stderr
    assert not (foreign_agents / f"{REPAIR_ANALYZER}.toml").exists()
    assert not any(launchers.iterdir())
    assert config.read_bytes() == config_before
    assert not list(codex_home.glob("*.config.toml"))
    assert not (codex_home / "rules").exists()
    assert classifier.read_text(encoding="utf-8") == '{"existing": true}\n'
    assert shell_rc.read_text(encoding="utf-8") == "# existing shell rc\n"
    assert not (repo_root / "bin" / "_logs").exists()


def test_remove_refuses_unsafe_repair_target_before_any_mutation(tmp_path: Path) -> None:
    installed, env, launcher_bin = _run_bootstrap(tmp_path, arg="--install")
    assert installed.returncode == 0, installed.stderr + installed.stdout
    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    codex_home = Path(env["HOME"]) / ".codex"
    analyzer = codex_home / "agents" / f"{REPAIR_ANALYZER}.toml"
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
    before = {path: path.read_bytes() for path in protected}

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
        assert {path: path.read_bytes() for path in protected} == before
    finally:
        analyzer.unlink(missing_ok=True)


def test_remove_refuses_symlinked_repair_analyzer_parent_before_any_mutation(
    tmp_path: Path,
) -> None:
    installed, env, launcher_bin = _run_bootstrap(tmp_path, arg="--install")
    assert installed.returncode == 0, installed.stderr + installed.stdout
    repo_root = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    codex_home = Path(env["HOME"]) / ".codex"
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
    before = {path: path.read_bytes() for path in protected}

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
    assert {path: path.read_bytes() for path in protected} == before


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
    assert (codex_home / "agents" / f"{REPAIR_ANALYZER}.toml").is_file()

    removed, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        arg="--remove",
        env_overrides={"CODEX_HOME": str(codex_home_alias)},
    )

    assert removed.returncode == 0, removed.stderr + removed.stdout
    assert not (codex_home / "agents" / f"{REPAIR_ANALYZER}.toml").exists()
    assert not (launcher_bin / "triad-apply-repair").exists()


def test_remove_deletes_only_managed_repair_analyzer_and_apply_launcher(tmp_path: Path) -> None:
    installed, env, launcher_bin = _run_bootstrap(tmp_path, arg="--install")
    assert installed.returncode == 0, installed.stderr + installed.stdout
    analyzer = Path(env["HOME"]) / ".codex" / "agents" / f"{REPAIR_ANALYZER}.toml"
    apply_launcher = launcher_bin / "triad-apply-repair"

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
def test_install_rejects_unsafe_selected_profile_or_rules_target_before_commands(
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


@pytest.mark.parametrize("target_kind", ("profile", "rules"))
def test_install_rechecks_selected_target_at_final_write_boundary(
    tmp_path: Path, target_kind: str
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    external = tmp_path / "external-target"
    external.write_bytes(b"foreign target\n")
    profile = codex_home / "triad-codex-dispatch.config.toml"
    rules = codex_home / "rules" / "triad-codex-dispatch.rules"
    if target_kind == "profile":
        profile.write_text(
            "# triad-codex-dispatch managed runtime profile\n", encoding="utf-8"
        )
        overrides = {
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "0",
            "TRIAD_BOOTSTRAP_TEST_SWAP_PROFILE_TO_SYMLINK_BEFORE_WRITE": str(external),
        }
        unsafe = profile
    else:
        rules.parent.mkdir()
        rules.write_text(
            "# triad-codex-dispatch managed command rules\n", encoding="utf-8"
        )
        overrides = {
            "CODEX_HOME": str(codex_home),
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0",
            "TRIAD_BOOTSTRAP_TEST_SWAP_RULES_TO_SYMLINK_BEFORE_WRITE": str(external),
        }
        unsafe = rules

    result, _env, _launchers = _run_bootstrap(
        tmp_path, arg="--install", env_overrides=overrides
    )

    assert result.returncode != 0
    assert unsafe.is_symlink()
    assert external.read_bytes() == b"foreign target\n"


@pytest.mark.parametrize("kind", ("profile", "rules"))
def test_install_preserves_regular_replacement_at_transaction_boundary(
    tmp_path: Path, kind: str
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    if kind == "profile":
        target = codex_home / "triad-codex-dispatch.config.toml"
        marker = b"# triad-codex-dispatch managed runtime profile\n"
        swap_env = "TRIAD_BOOTSTRAP_TEST_SWAP_PROFILE_TO_REGULAR_BEFORE_WRITE"
        selection = {"TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "0"}
    else:
        target = codex_home / "rules" / "triad-codex-dispatch.rules"
        target.parent.mkdir()
        marker = b"# triad-codex-dispatch managed command rules\n"
        swap_env = "TRIAD_BOOTSTRAP_TEST_SWAP_RULES_TO_REGULAR_BEFORE_WRITE"
        selection = {"TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "0"}
    target.write_bytes(marker + b"old managed body\n")
    foreign = b"foreign regular replacement must survive\n"
    replacement = tmp_path / f"{kind}-foreign-replacement"
    replacement.write_bytes(foreign)

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            swap_env: str(replacement),
            **selection,
        },
    )

    assert result.returncode != 0
    assert target.read_bytes() == foreign


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
    _assert_repair_analyzer_install_state(codex_home)
    assert (codex_home / "triad-codex-dispatch.config.toml").is_file()
    _assert_profile_does_not_disable_multi_agent(codex_home / "triad-codex-dispatch.config.toml")
    assert (codex_home / "rules" / "triad-codex-dispatch.rules").is_file()
    assert not (Path(env["HOME"]) / ".codex" / "agents").exists()


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
    _assert_repair_analyzer_install_state(codex_home)
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
    _assert_repair_analyzer_install_state(workspace_codex)
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
    _assert_repair_analyzer_install_state(codex_home)
    assert (codex_home / "triad-codex-dispatch.config.toml").is_file()
    _assert_profile_does_not_disable_multi_agent(codex_home / "triad-codex-dispatch.config.toml")
    assert (codex_home / "rules" / "triad-codex-dispatch.rules").is_file()


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


def test_bootstrap_requirements_warning_uses_python_argv_safe_guidance(
    tmp_path: Path,
) -> None:
    result, _env, _launchers = _run_bootstrap(
        tmp_path, fake_names=("codex", "claude", "agy")
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "migration/requirements.recommended.toml" in result.stdout
    assert "Python shlex.join command printer" in result.stdout
    assert "sudo cp" not in result.stdout
    assert "cp -n" not in result.stdout


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
    try:
        os.link(Path(sys.executable).resolve(), whitespace_runtime)
    except OSError:
        shutil.copy2(Path(sys.executable).resolve(), whitespace_runtime)
    whitespace_runtime.chmod(whitespace_runtime.stat().st_mode | stat.S_IXUSR)

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
    try:
        os.link(Path(sys.executable).resolve(), long_runtime)
    except OSError:
        shutil.copy2(Path(sys.executable).resolve(), long_runtime)
    long_runtime.chmod(long_runtime.stat().st_mode | stat.S_IXUSR)
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
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1",
            "TRIAD_CODEX_PROFILE_APPROVAL_POLICY": "danger-full-access",
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert "invalid TRIAD_CODEX_PROFILE_APPROVAL_POLICY" in result.stderr
    _assert_preflight_artifacts_unchanged(
        repo_root=repo_root,
        launcher_bin=launcher_bin,
        codex_home=codex_home,
        config=config,
        config_before=config_before,
        classifier=classifier,
        shell_rc=shell_rc,
    )


def test_check_refuses_to_overwrite_unmanaged_codex_runtime_profile(tmp_path):
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
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE": "1",
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert "refusing to overwrite unmanaged Codex profile" in result.stderr
    assert profile.read_bytes() == original
    _assert_preflight_artifacts_unchanged(
        repo_root=repo_root,
        launcher_bin=launcher_bin,
        codex_home=codex_home,
        config=config,
        config_before=config_before,
        classifier=classifier,
        shell_rc=shell_rc,
        allowed_profile_entries=(profile.name,),
    )


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


def test_check_refuses_to_overwrite_unmanaged_codex_command_rules(tmp_path):
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
            "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "1",
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert "refusing to overwrite unmanaged Codex rules file" in result.stderr
    assert rules.read_bytes() == original
    _assert_preflight_artifacts_unchanged(
        repo_root=repo_root,
        launcher_bin=launcher_bin,
        codex_home=codex_home,
        config=config,
        config_before=config_before,
        classifier=classifier,
        shell_rc=shell_rc,
        allowed_rules_entries=(rules.name,),
    )


@pytest.mark.parametrize("kind", ("profile", "rules"))
def test_install_rejects_unreadable_selected_codex_target_before_any_mutation(
    tmp_path: Path, kind: str
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    if kind == "profile":
        target = codex_home / "triad-codex-dispatch.config.toml"
        allowed_profiles = (target.name,)
        allowed_rules = ()
    else:
        target = codex_home / "rules" / "triad-codex-dispatch.rules"
        target.parent.mkdir()
        allowed_profiles = ()
        allowed_rules = (target.name,)
    original = b"\xffnot-valid-utf8\n"
    target.write_bytes(original)

    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert "could not read selected Codex" in result.stderr
    assert target.read_bytes() == original
    _assert_preflight_artifacts_unchanged(
        repo_root=repo_root,
        launcher_bin=launcher_bin,
        codex_home=codex_home,
        config=config,
        config_before=config_before,
        classifier=classifier,
        shell_rc=shell_rc,
        allowed_profile_entries=allowed_profiles,
        allowed_rules_entries=allowed_rules,
    )


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
    managed_paths = [
        launcher_bin / name
        for name in (
            "claude_wrapper.py",
            "gemini_wrapper.py",
            "antigravity_wrapper.py",
            "triad-apply-repair",
        )
    ] + [
        codex_home / "config.toml",
        codex_home / "agents" / f"{REPAIR_ANALYZER}.toml",
        codex_home / "triad-codex-dispatch.config.toml",
        codex_home / "rules" / "triad-codex-dispatch.rules",
    ]
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


def test_remove_rejects_invalid_runtime_profile_approval_policy_before_any_mutation(
    tmp_path: Path,
) -> None:
    first, env, launcher_bin = _run_bootstrap(tmp_path, arg="--install")
    assert first.returncode == 0, first.stderr + first.stdout
    codex_home = Path(env["HOME"]) / ".codex"
    managed_paths = [
        launcher_bin / name
        for name in (
            "claude_wrapper.py",
            "gemini_wrapper.py",
            "antigravity_wrapper.py",
            "triad-apply-repair",
        )
    ] + [
        codex_home / "config.toml",
        codex_home / "agents" / f"{REPAIR_ANALYZER}.toml",
        codex_home / "triad-codex-dispatch.config.toml",
        codex_home / "rules" / "triad-codex-dispatch.rules",
    ]
    before = {path: path.read_bytes() for path in managed_paths}

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--remove",
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        env_overrides={"TRIAD_CODEX_PROFILE_APPROVAL_POLICY": "danger-full-access"},
    )

    assert result.returncode != 0
    assert "invalid TRIAD_CODEX_PROFILE_APPROVAL_POLICY" in result.stderr
    assert {path: path.read_bytes() for path in managed_paths} == before


def test_remove_rolls_back_public_commands_after_late_command_failure(
    tmp_path: Path,
) -> None:
    shell_rc = tmp_path / "shellrc"
    first, env, launcher_bin = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
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
    remaining = [
        shell_rc,
        codex_home / "agents" / f"{REPAIR_ANALYZER}.toml",
        codex_home / "triad-codex-dispatch.config.toml",
        codex_home / "config.toml",
        codex_home / "rules" / "triad-codex-dispatch.rules",
        Path(env["XDG_CONFIG_HOME"]) / "triad-codex-dispatch" / "classifier-patches.json",
    ]
    remaining_before = {path: path.read_bytes() for path in remaining}

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--remove",
        repo_root=Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"]),
        env_overrides={
            "TRIAD_BOOTSTRAP_TEST_FAIL_COMMAND_REMOVE_AT": "gemini_wrapper.py",
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0, result.stderr + result.stdout
    assert "injected command removal failure" in result.stderr
    assert {path: path.read_bytes() for path in public_commands} == before
    assert {path: path.read_bytes() for path in remaining} == remaining_before


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
    assert "kept through 0.2.527 and scheduled for removal after 0.2.527" in result.stdout


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


def test_install_migrates_only_the_exact_legacy_managed_environment_policy(
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
    expected = (
        begin
        + '\n[shell_environment_policy]\ninherit = "all"\n'
        + 'exclude = ["LD_*", "DYLD_*", "NODE_OPTIONS", "NODE_PATH", "PYTHON*", "BASH_ENV", "ENV", "PERL5LIB", "RUBYOPT", "RUBYLIB"]\n'
        + end
        + "\n"
    )
    assert config.read_text(encoding="utf-8") == prefix + expected + suffix
    assert config.with_suffix(".toml.bak").read_text(encoding="utf-8") == prefix + legacy + suffix


def test_install_uses_numbered_backup_and_reports_retention_guidance(
    tmp_path: Path,
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    begin = "# >>> triad-codex-dispatch managed shell_environment_policy >>>"
    end = "# <<< triad-codex-dispatch managed shell_environment_policy <<<"
    legacy = begin + '\n[shell_environment_policy]\ninherit = "core"\n' + end + "\n"
    config.write_text(legacy, encoding="utf-8")
    first_backup = Path(str(config) + ".bak")
    first_backup.write_bytes(b"existing owner backup\n")

    result, _env, _launchers = _run_bootstrap(
        tmp_path,
        arg="--install",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert 'inherit = "all"' in config.read_text(encoding="utf-8")
    assert first_backup.read_bytes() == b"existing owner backup\n"
    assert Path(str(config) + ".bak2").read_text(encoding="utf-8") == legacy
    assert f"retained config backup: {config}.bak2" in result.stderr
    assert "keep it until Codex starts normally" in result.stderr
    assert "delete it if rollback is no longer needed" in result.stderr


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
    assert config.read_text(encoding="utf-8") == original
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
    assert config.read_text(encoding="utf-8") == original
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


def test_remove_config_fragment_helper_failure_is_fatal_and_stops_later_removal(
    tmp_path: Path,
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    config_before = _managed_environment_policy_block().encode("utf-8")
    config.write_bytes(config_before)
    rules = codex_home / "rules" / "triad-codex-dispatch.rules"
    rules.parent.mkdir()
    rules_before = b"# triad-codex-dispatch managed command rules\nowned\n"
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
    assert rules.read_bytes() == rules_before


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
def test_install_preserves_crlf_current_or_migrates_legacy_bytes(
    tmp_path: Path, legacy: bool
) -> None:
    codex_home = tmp_path / "codex-home"
    codex_home.mkdir()
    config = codex_home / "config.toml"
    prefix = b"# preserve CRLF prefix\r\n[custom]\r\nvalue = \"unchanged\"\r\n\r\n"
    suffix = (
        b"\r\n# preserve CRLF suffix\r\n\r\n\n"
        + _managed_repair_registration(codex_home).encode("utf-8")
    )
    original = prefix + _managed_environment_policy_bytes(legacy=legacy, newline=b"\r\n") + suffix
    config.write_bytes(original)

    result, _env, _launchers = _run_bootstrap(
        tmp_path, arg="--install", env_overrides={"CODEX_HOME": str(codex_home)}
    )

    assert result.returncode == 0, result.stderr + result.stdout
    expected = (
        prefix
        + _managed_environment_policy_bytes(legacy=False, newline=b"\r\n")
        + suffix
    )
    assert config.read_bytes() == expected
    backup = config.with_suffix(".toml.bak")
    if legacy:
        assert backup.read_bytes() == original
    else:
        assert not backup.exists()


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


def test_shell_entry_missing_final_newline_refuses_before_any_install_mutation(
    tmp_path: Path,
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    codex_home, config, classifier, shell_rc, config_before = (
        _seed_preflight_artifacts(tmp_path)
    )
    owner_bytes = b'export OWNER_SETTING="preserve"'
    shell_rc.write_bytes(owner_bytes)

    result, _env, launcher_bin = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--install",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "TRIAD_CLASSIFIER_EXTENSION": str(classifier),
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert "shell RC must end with a newline" in result.stderr
    _assert_preflight_artifacts_unchanged(
        repo_root=repo_root,
        launcher_bin=launcher_bin,
        codex_home=codex_home,
        config=config,
        config_before=config_before,
        classifier=classifier,
        shell_rc=shell_rc,
        shell_rc_before=owner_bytes,
    )


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


@pytest.mark.parametrize(
    "scenario",
    ("install-absent", "install-append", "install-refresh", "remove"),
)
def test_shell_entry_transaction_preserves_foreign_replacement_after_capture(
    tmp_path: Path, scenario: str
) -> None:
    shell_rc = tmp_path / "shellrc"
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    overrides = {
        "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
        "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
    }
    if scenario == "install-append":
        shell_rc.write_bytes(b"# owner prefix\n")
    elif scenario in {"install-refresh", "remove"}:
        shell_rc.write_bytes(b"# owner prefix\n")
        installed, _env, _launchers = _run_bootstrap(
            tmp_path,
            repo_root=repo_root,
            arg="--install",
            env_overrides=overrides,
        )
        assert installed.returncode == 0, installed.stderr + installed.stdout

    foreign = b"# foreign shell RC replacement\nowner bytes stay exact\n"
    replacement = tmp_path / f"{scenario}-foreign-shellrc"
    replacement.write_bytes(foreign)
    raced, _env, _launchers = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        arg="--remove" if scenario == "remove" else "--install",
        env_overrides={
            **overrides,
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

    result, env, launcher_bin = _run_bootstrap(
        tmp_path,
        arg=mode,
        env_overrides={
            "TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY": "1",
            "TRIAD_BOOTSTRAP_SHELL_RC": str(shell_rc),
        },
    )

    assert result.returncode != 0
    assert "malformed managed codex-triad shell markers" in result.stderr
    assert shell_rc.read_bytes() == original
    assert not any(launcher_bin.iterdir())
    assert not (Path(env["HOME"]) / ".codex").exists()


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
            b"# triad-codex-dispatch managed runtime profile\n",
            "TRIAD_BOOTSTRAP_TEST_SWAP_PROFILE_BEFORE_REMOVE",
        ),
        (
            "rules",
            "rules/triad-codex-dispatch.rules",
            b"# triad-codex-dispatch managed command rules\n",
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
