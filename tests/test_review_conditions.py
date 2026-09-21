"""Admission must bind conditions and toolkit bytes, not only source bytes."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from test_review_round import (
    BIN, ReviewBrief, WorktreeReviewBrief, _canonical_json_bytes,
    _google_selector_receipt, _prepared_digest, _review_metadata,
    _write_google_selector_receipt, prepared, worktree,
)
from test_provider_wrappers import _formal_gemini_help
import review_round
import gemini_wrapper


def _prepared_brief(path):
    return ReviewBrief(
        review_id="conditions-r1", review_kind="implementation-review",
        family="claude", objective="Review the complete change.",
        prepared_dir=path, content_digest=_prepared_digest(path),
        criteria=("correctness", "compatibility"),
        approved_boundary=("source", "tests"),
        google_selector_receipt=_google_selector_receipt("conditions-r1"),
    )


def _digest(brief):
    render = (review_round.render_review_prompt if isinstance(brief, ReviewBrief)
              else review_round.render_worktree_review_prompt)
    return _review_metadata(render(brief))["content_digest"]


@pytest.mark.parametrize("axis", [
    "objective", "criteria", "criteria_order", "boundary", "boundary_order",
    "review_kind", "prepared_directory", "review_id",
])
def test_prepared_condition_change_invalidates_admission(prepared, tmp_path, axis):
    first = _prepared_brief(prepared)
    changes = {
        "objective": {"objective": "Review a different decision."},
        "criteria": {"criteria": ("security", "compatibility")},
        "criteria_order": {"criteria": tuple(reversed(first.criteria))},
        "boundary": {"approved_boundary": ("source",)},
        "boundary_order": {"approved_boundary": tuple(reversed(first.approved_boundary))},
        "review_kind": {"review_kind": "design-review"},
        "review_id": {"review_id": "conditions-r2", "google_selector_receipt":
                      replace(first.google_selector_receipt, review_id="conditions-r2")},
    }
    if axis == "prepared_directory":
        other = tmp_path / "other-prepared"
        shutil.copytree(prepared, other)
        assert _prepared_digest(other) == first.content_digest
        second = replace(first, prepared_dir=other)
    else:
        second = replace(first, **changes[axis])
    assert _digest(first) != _digest(second)


@pytest.mark.parametrize("family", ["google", "codex"])
def test_family_alone_keeps_common_admission_basis(prepared, family):
    brief = _prepared_brief(prepared)
    assert _digest(brief) == _digest(replace(brief, family=family))


@pytest.mark.parametrize("route", ["prepared", "worktree"])
@pytest.mark.parametrize("member", ["review_round.py", "verdict_schema.py"])
def test_toolkit_byte_change_invalidates_both_routes(
    prepared, worktree, tmp_path, monkeypatch, route, member,
):
    toolkit = tmp_path / "toolkit"
    toolkit.mkdir()
    for name in ("review_round.py", "verdict_schema.py"):
        shutil.copy2(BIN / name, toolkit / name)
    monkeypatch.setattr(review_round, "__file__", str(toolkit / "review_round.py"))
    brief = _prepared_brief(prepared)
    if route == "worktree":
        custody = [worktree / name for name in ("TASK.md", "STATUS.txt", "REVIEW.diff")]
        for path in custody:
            path.write_text(path.name + "\n")
        brief = WorktreeReviewBrief(
            review_id=brief.review_id, review_kind=brief.review_kind,
            family=brief.family, objective=brief.objective,
            worktree=worktree, worktree_fingerprint=review_round._worktree_fingerprint(worktree),
            task_file=custody[0], status_file=custody[1], diff_file=custody[2],
            criteria=brief.criteria, review_points=("Trace consumers.",),
            approved_boundary=brief.approved_boundary,
            google_selector_receipt=brief.google_selector_receipt,
        )
    before = _digest(brief)
    with (toolkit / member).open("a") as stream:
        stream.write("\n# a different shipped toolkit byte sequence\n")
    assert _digest(brief) != before


@pytest.fixture
def gemini_policy_case(tmp_path, monkeypatch):
    toolkit = tmp_path / "policy-toolkit"
    (toolkit / "policies").mkdir(parents=True)
    for name in ("review_round.py", "verdict_schema.py", "gemini_wrapper.py"):
        shutil.copy2(BIN / name, toolkit / name)
    policy = toolkit / "policies/gemini-formal-readonly.toml"
    shutil.copy2(BIN / "policies/gemini-formal-readonly.toml", policy)
    shutil.copy2(BIN / "policies/source-manifest.json", policy.parent / "source-manifest.json")
    monkeypatch.setattr(review_round, "__file__", str(toolkit / "review_round.py"))
    monkeypatch.setattr(gemini_wrapper, "__file__", str(toolkit / "gemini_wrapper.py"))
    selected = Path(sys.executable).resolve()
    selector_path = tmp_path / "selector.json"
    _write_google_selector_receipt(selector_path, review_id="conditions-r1",
        authentication_class="gemini-enterprise", route="gemini", executable=selected,
        wrapper=toolkit / "gemini_wrapper.py")
    selector = review_round.load_google_selector_receipt(selector_path,
        expected_review_id="conditions-r1", expected_route="gemini")
    monkeypatch.setattr(gemini_wrapper.subprocess, "run", lambda argv, **kw:
        subprocess.CompletedProcess(argv, 0,
            "0.60.0" if argv[-1] == "--version" else _formal_gemini_help(), ""))
    return policy, selector_path, selector, tmp_path / "preflight.json"


def _produce(case, capsys):
    _, _, selector, receipt_path = case
    assert gemini_wrapper._run_preflight(str(selector.executable), None, 5, selector) == 0
    record = json.loads(capsys.readouterr().out)
    receipt_path.write_bytes(_canonical_json_bytes(record))
    return record


def test_preflight_hashes_the_same_policy_bytes_it_validated(
    gemini_policy_case, monkeypatch, capsys,
):
    policy, _, _, _ = gemini_policy_case
    original = policy.read_bytes()
    def help_after_edit(argv, **kwargs):
        if argv[-1] == "--version":
            return subprocess.CompletedProcess(argv, 0, "0.60.0", "")
        policy.write_bytes(original + b"\n# edit after policy validation\n")
        return subprocess.CompletedProcess(argv, 0, _formal_gemini_help(), "")
    monkeypatch.setattr(gemini_wrapper.subprocess, "run", help_after_edit)
    record = _produce(gemini_policy_case, capsys)
    assert record.get("policy_sha256") == hashlib.sha256(original).hexdigest()


def test_policy_change_refuses_old_receipt_and_unpublished_fresh_preflight(
    gemini_policy_case, capsys,
):
    policy, _, selector, receipt_path = gemini_policy_case
    _produce(gemini_policy_case, capsys)
    review_round.validate_google_preflight_receipt(
        receipt_path, selector, expected_review_id=selector.review_id)
    policy.write_bytes(policy.read_bytes() + b"\n# semantically valid different policy bytes\n")
    with pytest.raises(review_round.RoundIntegrityError, match="policy"):
        review_round.validate_google_preflight_receipt(
            receipt_path, selector, expected_review_id=selector.review_id)
    # Even a comment edit requires a new published candidate; a preflight may
    # not self-authorize different bytes under the existing provenance.
    assert gemini_wrapper._run_preflight(str(selector.executable), None, 5, selector) == 3
    evidence = capsys.readouterr()
    assert not evidence.out
    assert 'policy digest' in evidence.err


@pytest.mark.parametrize("bad_hash", [None, "", "0" * 64, 123])
def test_policy_receipt_requires_current_exact_hash(gemini_policy_case, capsys, bad_hash):
    _, _, selector, receipt_path = gemini_policy_case
    record = _produce(gemini_policy_case, capsys)
    if bad_hash is None:
        record.pop("policy_sha256", None)
    else:
        record["policy_sha256"] = bad_hash
    receipt_path.write_bytes(_canonical_json_bytes(record))
    with pytest.raises(review_round.RoundIntegrityError):
        review_round.validate_google_preflight_receipt(
            receipt_path, selector, expected_review_id=selector.review_id)


@pytest.mark.parametrize("consumer", ["render", "dispatch"])
def test_stale_policy_refused_before_render_or_dispatch(
    gemini_policy_case, prepared, monkeypatch, capsys, consumer,
):
    policy, selector_path, selector, receipt_path = gemini_policy_case
    _produce(gemini_policy_case, capsys)
    validated = review_round.validate_google_preflight_receipt(
        receipt_path, selector, expected_review_id=selector.review_id)
    brief = replace(_prepared_brief(prepared), family="google", google_selector_receipt=validated)
    prompt = review_round.render_review_prompt(brief)
    digest = _review_metadata(prompt)["content_digest"]
    policy.write_bytes(policy.read_bytes() + b"\n# changed after render\n")
    monkeypatch.setattr(gemini_wrapper, "run_cli_with_retry", lambda *a, **kw:
        pytest.fail("stale policy reached provider"))
    if consumer == "render":
        output = prepared.parent / "new-prompt.txt"
        argv = ["review_round.py", "render", "--review-id", selector.review_id,
            "--review-kind", brief.review_kind, "--family", "google",
            "--objective", brief.objective, "--prepared-dir", str(prepared),
            "--content-digest", brief.content_digest, "--criterion", "correctness",
            "--approved-boundary", "prepared source", "--output", str(output)]
        main = review_round.main
    else:
        argv = ["gemini_wrapper.py", "--prompt", prompt,
            "--pydantic", "verdict_schema:LegVerdict",
            "--expected-review-id", selector.review_id, "--expected-family", "google",
            "--expected-content-digest", digest]
        main = gemini_wrapper.main
    argv += ["--google-selector-receipt", str(selector_path),
             "--google-preflight-receipt", str(receipt_path)]
    monkeypatch.setattr(sys, "argv", argv)
    assert main() != 0
    assert "policy" in capsys.readouterr().err.lower()
    if consumer == "render":
        assert not output.exists()
