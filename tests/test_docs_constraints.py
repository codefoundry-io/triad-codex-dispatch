import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def test_codex_leader_docs_do_not_shell_out_to_codex_exec():
    forbidden = "codex " + "exec"
    offenders = []
    for path in _tracked_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if forbidden in text:
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def test_cross_family_review_uses_fresh_codex_subagent_only():
    skill_paths = [
        ROOT / ".agents/skills/triad-cross-family-review/SKILL.md",
        ROOT / "skills/triad-cross-family-review/SKILL.md",
    ]
    for path in skill_paths:
        text = path.read_text(encoding="utf-8")
        assert "spawn_agent" in text
        assert "fork_context=false" in text
        assert "nested" not in text.lower()
