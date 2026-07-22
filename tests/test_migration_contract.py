import ast
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "migration" / "triad-codex-dispatch.rules"
REQUIREMENTS = ROOT / "migration" / "requirements.recommended.toml"
BOOTSTRAP = ROOT / "scripts" / "bootstrap.sh"
CONFIG_FRAGMENT = ROOT / "migration" / "config-fragment.recommended.toml"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _excluded(name: str, patterns: list[str]) -> bool:
    import fnmatch

    return any(fnmatch.fnmatchcase(name.upper(), pattern.upper()) for pattern in patterns)


def test_shipped_environment_policy_uses_all_with_exact_case_insensitive_excludes() -> None:
    fragment = tomllib.loads(_text(CONFIG_FRAGMENT))["shell_environment_policy"]

    assert fragment["inherit"] == "all"
    assert fragment["exclude"] == [
        "LD_*",
        "DYLD_*",
        "NODE_OPTIONS",
        "NODE_PATH",
        "PYTHON*",
        "BASH_ENV",
        "ENV",
        "PERL5LIB",
        "RUBYOPT",
        "RUBYLIB",
    ]
    assert _excluded("lD_PreLoAd", fragment["exclude"])
    assert _excluded("dYlD_iNsErT_lIbRaRiEs", fragment["exclude"])
    assert _excluded("pYtHoNuSeRsItE", fragment["exclude"])
    assert not _excluded("TRIAD_WRAPPER_ALLOWED_ROOTS", fragment["exclude"])
    assert not _excluded("TRIAD_WRAPPER_HARDENED", fragment["exclude"])
    assert not _excluded("TRIAD_CLAUDE_ENFORCE_SANDBOX", fragment["exclude"])


def test_migration_rules_follow_the_current_bootstrap_generated_shape() -> None:
    rules = _text(RULES)

    assert "scripts/bootstrap.sh --check" not in rules
    assert "freshly\n# printed absolute" in rules
    assert "--install" in rules
    assert "Gemini 3.1 Pro (High)" not in rules
    assert "agy models" in rules

    blocks = rules.split("prefix_rule(")[1:]
    for wrapper, label in (
        ("claude_wrapper.py", "Claude wrapper"),
        ("antigravity_wrapper.py", "Antigravity wrapper"),
        ("gemini_wrapper.py", "Gemini business-tier wrapper"),
    ):
        text = next(
            block
            for block in blocks
            if f"Allow authenticated triad {label} commands outside the sandbox." in block
        )
        assert text.count('"/path/to/launcher-dir/') == 3
        assert f'"{wrapper} --prompt hi --sandbox read-only"' in text
        assert "python3 -c print('not a triad wrapper')" in text
        assert "--effort" not in text
        assert "--approval-mode" not in text
        assert "--model" not in text
        assert "workspace-write" not in text


def test_requirements_admin_copy_is_absolute_argv_safe_and_cwd_independent(
    tmp_path: Path,
) -> None:
    requirements = _text(REQUIREMENTS)
    bootstrap = _text(BOOTSTRAP)

    assert "unrelated working directory" in requirements
    assert 'subprocess.run(["codex", "plugin", "list", "--json"]' in requirements
    assert 'item["source"]["path"]' in requirements
    assert "root.is_absolute()" in requirements
    assert "shlex.join" in requirements
    assert 'root / "migration" / "requirements.recommended.toml"' in requirements
    assert '"/etc/codex/requirements.toml"' in requirements
    assert "sudo cp" not in requirements
    assert "cp -n" not in requirements
    assert "sudo cp" not in bootstrap
    assert "cp -n" not in bootstrap
    assert "Python shlex.join command printer" in bootstrap

    command = next(
        line.removeprefix("#   ")
        for line in requirements.splitlines()
        if line.startswith("#   python3 -c ")
    )
    argv = shlex.split(command)
    assert argv[:2] == ["python3", "-c"]
    outer = ast.parse(argv[2])
    copier_assignment = next(
        node
        for node in outer.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "copier" for target in node.targets)
    )
    copier = ast.literal_eval(copier_assignment.value)
    compile(copier, "<migration-admin-copy>", "exec")
    assert 'destination.open("xb")' in copier
    assert "shutil.copyfileobj" in copier
    assert "destination.exists()" not in copier
    assert "shutil.copyfile(source, destination)" not in copier

    source = tmp_path / "source file.toml"
    destination = tmp_path / "destination file.toml"
    source.write_bytes(b"new configuration\n")
    destination.write_bytes(b"owner configuration\n")
    refused = subprocess.run(
        [sys.executable, "-c", copier, str(source), str(destination)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert refused.returncode != 0
    assert destination.read_bytes() == b"owner configuration\n"

    destination.unlink()
    installed = subprocess.run(
        [sys.executable, "-c", copier, str(source), str(destination)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert installed.returncode == 0, installed.stderr
    assert destination.read_bytes() == source.read_bytes()

    hostile_source = "/tmp/plugin ' $() ` dir/migration/requirements.recommended.toml"
    rendered = shlex.join(
        ["python3", "-c", copier, hostile_source, "/etc/codex/requirements.toml"]
    )
    assert shlex.split(rendered) == [
        "python3", "-c", copier, hostile_source, "/etc/codex/requirements.toml"
    ]
