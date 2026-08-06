from __future__ import annotations

import json
import re
import stat
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
SKILLS = ROOT / "skills"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_manifest_describes_the_convergent_distribution() -> None:
    manifest = json.loads(_text(MANIFEST))

    assert manifest["name"] == "triad-codex-dispatch"
    assert manifest["version"] == "0.2.533"
    assert manifest["skills"] == "./skills/"
    prompts = "\n".join(manifest["interface"]["defaultPrompt"])
    assert "triad-cross-family-review" in prompts
    assert "same complete focused directory" in prompts
    assert "batched-full-coverage" not in prompts


def test_distribution_contains_only_the_four_public_skills() -> None:
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    assert [path.parent.name for path in skill_files] == [
        "triad-antigravity-dispatch",
        "triad-claude-dispatch",
        "triad-cross-family-review",
        "triad-gemini-dispatch",
    ]
    for path in skill_files:
        text = _text(path)
        assert text.startswith("---\n")
        assert f"name: {path.parent.name}\n" in text.split("---", 2)[1]
        assert len(text.splitlines()) <= 200


def test_active_skill_links_resolve_inside_each_skill() -> None:
    for skill in SKILLS.glob("*/SKILL.md"):
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", _text(skill)):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (skill.parent / target.split("#", 1)[0]).resolve()
            assert resolved.is_file(), f"broken link from {skill}: {target}"


def test_cross_family_skill_has_one_round_unit_and_owner_design_gate() -> None:
    text = _text(SKILLS / "triad-cross-family-review" / "SKILL.md")
    convergence = _text(
        SKILLS / "triad-cross-family-review" / "references" / "convergence.md"
    )
    compact = " ".join(text.split())

    assert "one Claude LegVerdict" in text
    assert "one Google LegVerdict" in text
    assert "one fresh Codex LegVerdict" in text
    assert "OWNER_DECISION_REQUIRED" in text
    assert "There is no arbitrary round cap" in text
    assert "Do not retain review batches" in compact
    assert "fresh Codex process" in compact
    for owner_slot in (
        "Proposed delta:",
        "Evidence:",
        "Impact:",
        "Decision needed:",
    ):
        assert owner_slot in convergence
    assert "Do not implement the proposed delta while asking" in convergence


def test_formal_routes_are_explicit_and_reviewer_only() -> None:
    claude = _text(SKILLS / "triad-claude-dispatch" / "SKILL.md")
    leg_contracts = _text(
        SKILLS
        / "triad-cross-family-review"
        / "references"
        / "leg-contracts.md"
    )
    agy = _text(SKILLS / "triad-antigravity-dispatch" / "SKILL.md")
    gemini = _text(SKILLS / "triad-gemini-dispatch" / "SKILL.md")

    assert "--model opus" in claude and "--effort xhigh" in claude
    assert "--timeout 1800" in claude
    assert "--timeout 1800" in leg_contracts
    assert "wake-up boundaries" in leg_contracts
    assert "1.1.10 or newer" in agy
    assert "--model gemini-3.1-pro-high" in agy
    assert "--effort high" in agy
    assert "stream-json" in agy and "json-schema" in agy
    assert "reviews only" in claude
    assert "reviews only" in agy
    assert "reviews only" in gemini


def test_retired_review_runtime_is_absent() -> None:
    retired = [
        ROOT / "bin" / "_pty.py",
        ROOT / "bin" / "review_evidence.py",
        ROOT / "bin" / "review_coverage.py",
        ROOT / "bin" / "triad_formal_review_schema.py",
        ROOT / "skills" / "triad-cross-family-review" / "references" / "fresh-codex-formal-review.md",
    ]
    assert not any(path.exists() for path in retired)


def test_current_public_docs_do_not_advertise_retired_batch_or_packet_modes() -> None:
    current = "\n".join(
        _text(ROOT / name)
        for name in ("README.md", "README.ko.md", "SECURITY.md")
    )
    for stale in (
        "batched-full-coverage",
        "full batch matrix",
        "`BatchReceipt`",
        "packet-bound `FormalReview`",
        "sealed-packet flag",
        "deterministic batch",
        "receipt contract",
        "coverage admission",
        "non-UTF-8 source",
    ):
        assert stale not in current


def test_governing_agy_documents_match_the_current_formal_route() -> None:
    governing = {
        path: _text(ROOT / path)
        for path in (
            "docs/superpowers/specs/2026-08-05-agy-1.1.10-formal-route-design.md",
            "docs/superpowers/plans/2026-08-05-agy-1.1.10-formal-route.md",
        )
    }

    for path, text in governing.items():
        assert "Historical, superseded, and non-executable" in text, path
        assert "2026-08-05-triad-0.2.533-owner-decisions-and-release.md" in text, path
        assert "--model gemini-3.1-pro-high" in text, path
        assert "--effort high" in text, path
        assert "one focused Google leg" in text, path
        assert "one provider call" in text, path


def test_current_release_docs_bind_the_superseded_agy_route_and_pending_r9_candidate() -> None:
    changelog = _text(ROOT / "CHANGELOG.md")
    handoff = _text(ROOT / "docs/status/2026-08-05-next-session-handoff.md")
    release_plan = _text(
        ROOT
        / "docs"
        / "superpowers"
        / "plans"
        / "2026-08-05-triad-0.2.533-owner-decisions-and-release.md"
    )

    assert "`gemini-3.1-pro-high --effort high`" in changelog
    assert "0.2.532 route is historical and superseded" in changelog
    assert "post-r8 bounded-correction" in handoff
    assert "final-0.2.533-r9" in handoff
    assert "final-0.2.533-r9" in release_plan
    assert "FINAL_REVIEW_ID" in release_plan
    assert "final-r2" not in release_plan
    assert "docs/references/repair-protocol.md" in handoff


def test_wrapper_sources_have_no_retired_permission_or_packet_transport() -> None:
    wrappers = "\n".join(
        _text(ROOT / "bin" / name)
        for name in (
            "antigravity_wrapper.py",
            "claude_wrapper.py",
            "gemini_wrapper.py",
        )
    )
    for stale in (
        "--sandbox",
        "--dangerously-skip-permissions",
        "--sealed-packet-root",
        "--expected-packet-sha256",
        "run_via_pty",
    ):
        assert stale not in wrappers


def test_provider_wrappers_are_packaged_as_executables() -> None:
    for name in (
        "antigravity_wrapper.py",
        "claude_wrapper.py",
        "gemini_wrapper.py",
    ):
        mode = (ROOT / "bin" / name).stat().st_mode
        assert mode & stat.S_IXUSR, name


def test_distribution_documents_fresh_process_acceptance() -> None:
    readme = _text(ROOT / "README.md")
    skill = _text(SKILLS / "triad-cross-family-review" / "SKILL.md")

    assert "session after install or update" in readme
    assert "packaged manifest and skill bytes" in skill
    assert "exact current marker" in skill
