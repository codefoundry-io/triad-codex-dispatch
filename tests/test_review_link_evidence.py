"""Scoped link evidence is bound without silently authorizing target reads."""
from dataclasses import replace
import json

import pytest

from test_four_leg_custody import _brief
from test_review_round import (
    ROOT, _git, _google_selector_receipt, _review_metadata, review_round, worktree,
)


@pytest.mark.parametrize("family,route", [
    ("claude", "agy"), ("codex", "agy"), ("google", "agy"), ("google", "gemini"),
])
def test_guarded_review_requires_link_evidence_without_target_traversal(worktree, family, route):
    brief = _brief(worktree)
    selector = _google_selector_receipt(
        brief.review_id, route=route,
        authentication_class="gemini-enterprise" if route == "gemini" else "personal-google",
    )
    prompt = review_round.render_worktree_review_prompt(replace(
        brief, family=family, google_selector_receipt=selector,
        google_flash_preflight_receipt=None,
    ))
    assert "Review each approved symlink's path, kind, basis and exact link text from TASK" in prompt
    assert "Never follow a symlink or symlink ancestor to read or search its target" in prompt
    assert "separately authorized and bound input" in prompt
    assert "Missing link evidence or necessary target content is a coverage gap" in prompt


def test_source_skill_prepares_scoped_link_evidence_before_capture():
    skill = (ROOT / "skills/triad-cross-family-review/SKILL.md").read_text()
    reference = (ROOT / "skills/triad-cross-family-review/references/leg-contracts.md").read_text()
    assert "scoped symlink evidence" in skill
    assert "## Scoped symlink evidence" in reference
    for required in ("HEAD", "index", "working tree", "unchanged tracked", "JSON", "lstat", "readlink"):
        assert required in reference
    assert "before fingerprint capture" in " ".join(reference.split())


def test_task_link_text_changes_digest_without_refingerprinting(worktree):
    brief = _brief(worktree)
    records = []
    for target in ("../outside-a", "../outside-b"):
        brief.task_file.write_text("Symlink evidence (data):\n" + json.dumps({
            "path": "src/link", "kind": "symlink", "basis": "working tree", "link_text": target,
        }) + "\n")
        records.append(_review_metadata(review_round.render_worktree_review_prompt(brief)))
    assert records[0]["content_digest"] != records[1]["content_digest"]
    assert records[0]["worktree_fingerprint"] == records[1]["worktree_fingerprint"]


def test_tracked_link_fingerprint_binds_index_and_worktree_not_target(worktree, tmp_path):
    target = tmp_path / "external-target"
    target.write_text("outside approved review\n")
    link = worktree / "tracked-link"
    link.symlink_to(target)
    _git(worktree, "add", "--", "tracked-link")
    _git(worktree, "commit", "-m", "add link fixture")
    first = review_round._worktree_fingerprint(worktree)
    target.write_text("changed outside content\n")
    assert review_round._worktree_fingerprint(worktree) == first
    link.unlink()
    link.symlink_to("../missing-index-target")
    _git(worktree, "add", "--", "tracked-link")
    staged = review_round._worktree_fingerprint(worktree)
    assert staged != first
    link.unlink()
    link.symlink_to("../missing-worktree-target")
    assert review_round._worktree_fingerprint(worktree) != staged
