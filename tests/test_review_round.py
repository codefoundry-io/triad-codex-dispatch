from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
sys.path.insert(0, str(BIN))

from review_round import (  # noqa: E402
    ReviewBrief,
    RoundIntegrityError,
    capture_round,
    render_review_prompt,
    verify_round,
)


def _git(repo: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "TRIAD Test",
        "GIT_AUTHOR_EMAIL": "triad@example.invalid",
        "GIT_COMMITTER_NAME": "TRIAD Test",
        "GIT_COMMITTER_EMAIL": "triad@example.invalid",
    }
    return subprocess.run(
        ["git", *args], cwd=repo, env=env, text=True,
        capture_output=True, check=True,
    ).stdout


@pytest.fixture
def worktree(tmp_path: Path) -> Path:
    repo = (tmp_path / "repo").resolve()
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    (repo / "source.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(repo, "add", "source.py")
    _git(repo, "commit", "-q", "-m", "initial")
    return repo


@pytest.fixture
def prepared(tmp_path: Path) -> Path:
    path = (tmp_path / "prepared").resolve()
    (path / "src").mkdir(parents=True)
    (path / "src/source.py").write_text("VALUE = 2\n", encoding="utf-8")
    (path / "REVIEW.diff").write_text("-VALUE = 1\n+VALUE = 2\n", encoding="utf-8")
    return path


def test_capture_and_verify_round_are_stable(prepared, worktree):
    snapshot = capture_round(prepared, worktree)
    verify_round(snapshot, prepared, worktree)
    assert len(snapshot.prepared_digest) == 64
    assert len(snapshot.worktree_fingerprint) == 64


def test_verify_round_rejects_prepared_mutation(prepared, worktree):
    snapshot = capture_round(prepared, worktree)
    (prepared / "src/source.py").write_text("VALUE = 3\n", encoding="utf-8")

    with pytest.raises(RoundIntegrityError, match="prepared directory digest mismatch"):
        verify_round(snapshot, prepared, worktree)


def test_verify_round_rejects_worktree_mutation(prepared, worktree):
    snapshot = capture_round(prepared, worktree)
    (worktree / "source.py").write_text("VALUE = 4\n", encoding="utf-8")

    with pytest.raises(RoundIntegrityError, match="worktree fingerprint mismatch"):
        verify_round(snapshot, prepared, worktree)


def test_capture_round_rejects_symlinked_prepared_entry(prepared, worktree):
    (prepared / "escape").symlink_to(worktree / "source.py")

    with pytest.raises(RoundIntegrityError, match="symlink"):
        capture_round(prepared, worktree)


def test_untracked_file_content_changes_fingerprint(prepared, worktree):
    extra = worktree / "untracked.txt"
    extra.write_text("first\n", encoding="utf-8")
    first = capture_round(prepared, worktree)
    extra.write_text("second\n", encoding="utf-8")
    second = capture_round(prepared, worktree)
    assert first.worktree_fingerprint != second.worktree_fingerprint


def test_rendered_prompt_binds_focused_round_once(prepared):
    brief = ReviewBrief(
        review_id="review-r1",
        review_kind="pre-merge",
        family="google",
        objective="Check parser compatibility.",
        prepared_dir=prepared,
        content_digest="a" * 64,
        criteria=("correctness", "compatibility"),
        approved_boundary=("src/source.py", "REVIEW.diff"),
    )
    prompt = render_review_prompt(brief)

    assert prompt.count("review-r1") == 1
    assert prompt.count("a" * 64) == 1
    assert "Reviewer family: google" in prompt
    assert "Set `family` to exactly `google`" in prompt
    for field in (
        '"review_id"',
        '"content_digest"',
        '"criteria_checked"',
        '"affected_surfaces_inspected"',
        '"severity"',
        '"trigger"',
        '"correction"',
    ):
        assert field in prompt
    assert str(prepared) in prompt
    assert "LegVerdict" in prompt
    assert "BatchReceipt" not in prompt
    assert "batch_manifest" not in prompt
    assert "All paths must be prepared-directory-relative" in prompt
    assert "Do not edit or execute candidate code" in prompt


def test_cli_capture_and_verify(prepared, worktree, tmp_path):
    snapshot_file = (tmp_path / "round.json").resolve()
    captured = subprocess.run(
        [
            sys.executable, str(BIN / "review_round.py"), "capture",
            "--prepared-dir", str(prepared), "--worktree", str(worktree),
            "--output", str(snapshot_file),
        ],
        text=True, capture_output=True, check=False,
    )
    assert captured.returncode == 0
    assert json.loads(snapshot_file.read_text())["prepared_dir"] == str(prepared)

    verified = subprocess.run(
        [
            sys.executable, str(BIN / "review_round.py"), "verify",
            "--prepared-dir", str(prepared), "--worktree", str(worktree),
            "--snapshot", str(snapshot_file),
        ],
        text=True, capture_output=True, check=False,
    )
    assert verified.returncode == 0
    assert verified.stdout.strip() == "ROUND_INTEGRITY_OK"


def test_cli_renders_family_bound_prompt(prepared, tmp_path):
    prompt_file = (tmp_path / "prompt.txt").resolve()
    rendered = subprocess.run(
        [
            sys.executable,
            str(BIN / "review_round.py"),
            "render",
            "--review-id",
            "review-r1",
            "--review-kind",
            "pre-merge",
            "--family",
            "claude",
            "--objective",
            "Check compatibility.",
            "--prepared-dir",
            str(prepared),
            "--content-digest",
            "a" * 64,
            "--criterion",
            "correctness",
            "--approved-boundary",
            "all prepared files",
            "--output",
            str(prompt_file),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert rendered.returncode == 0, rendered.stderr
    prompt = prompt_file.read_text(encoding="utf-8")
    assert "Reviewer family: claude" in prompt
    assert "Set `family` to exactly `claude`" in prompt
