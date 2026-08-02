from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "scripts" / "bootstrap.sh"
GUIDANCE = ROOT / "migration" / "AGENTS.recommended.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_distribution_has_no_permission_migration_templates() -> None:
    migration = ROOT / "migration"

    assert not (migration / "config-fragment.recommended.toml").exists()
    assert not (migration / "requirements.recommended.toml").exists()
    assert not (migration / "triad-codex-dispatch.rules").exists()


def test_release_headers_are_in_descending_order() -> None:
    changelog = _text(ROOT / "CHANGELOG.md")

    assert changelog.index("## 0.2.529") < changelog.index("## 0.2.528")
    assert changelog.index("## 0.2.528") < changelog.index("## 0.2.527")


def test_current_migration_guidance_is_permission_neutral() -> None:
    guidance = " ".join(_text(GUIDANCE).split())

    assert "same authenticated login terminal" in guidance
    assert "repository worktree used for development" in guidance
    assert "inherits provider permissions without changing them" in guidance
    assert "does not install a separate Codex profile, rule, permission" in guidance
    assert "pre-spawn `shell_environment_policy`" in guidance
    assert "danger-full-access" not in guidance
    assert "read-only sandbox" not in guidance
    assert "triad-repair-analyzer" not in guidance


def test_bootstrap_install_has_no_admin_permission_copy_path() -> None:
    bootstrap = _text(BOOTSTRAP)
    remove_start = bootstrap.index("run_remove() {")
    remove_end = bootstrap.index("\npreflight_classifier() {", remove_start)
    remove_only = bootstrap[remove_start:remove_end]
    install_and_creation = bootstrap[:remove_start] + bootstrap[remove_end:]

    assert "sudo cp" not in bootstrap
    assert "cp -n" not in bootstrap
    assert "requirements.recommended.toml" not in bootstrap
    assert "/etc/codex/requirements.toml" in remove_only
    assert "/etc/codex/requirements.toml" not in install_and_creation
    assert "TRIAD_CODEX_REQUIREMENTS_PATH" in remove_only
    assert "os.remove" not in remove_only
    assert "unlink" not in remove_only
