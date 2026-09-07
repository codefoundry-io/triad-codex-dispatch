"""Fixed workspace opt-in; the public singular route remains unchanged."""
from dataclasses import replace
import hashlib
import json

import pytest

from test_review_round import (
    worktree,  # noqa: F401 - reuse the existing disposable Git fixture
    _google_selector_receipt,
    _review_metadata,
    _canonical_json_bytes,
    review_round,
    _write_google_selector_receipt,
    _write_google_preflight_receipt,
)

PRO = "gemini-3.1-pro-high"
FLASH = "gemini-3.8-flash-high"


def _brief(worktree):
    paths = [worktree / name for name in ("task.md", "status.txt", "review.diff")]
    for path in paths:
        path.write_text(path.name + "\n", encoding="utf-8")
    pro = _google_selector_receipt("four-leg-r1")
    flash = replace(pro, model=FLASH, route_args=("--model", FLASH, "--effort", "high"),
                    preflight_receipt_sha256="c" * 64)
    return review_round.WorktreeReviewBrief(
        review_id="four-leg-r1", review_kind="pre-merge", family="google",
        objective="Review the same candidate independently.", worktree=worktree,
        worktree_fingerprint=review_round._worktree_fingerprint(worktree),
        task_file=paths[0], status_file=paths[1], diff_file=paths[2],
        criteria=("Correctness and evidence-backed simplicity/code smells.",),
        review_points=("Trace changed behavior and affected callers.",),
        approved_boundary=("sanitized worktree",), google_selector_receipt=pro,
        google_flash_preflight_receipt=flash,
    )


def test_four_required_prompts_share_pair_digest(worktree):
    base = _brief(worktree)
    variants = [("claude", PRO), ("google", PRO), ("google", FLASH), ("codex", PRO)]
    prompts = [review_round.render_worktree_review_prompt(
        replace(base, family=family, google_review_model=model))
        for family, model in variants]
    records = [_review_metadata(prompt) for prompt in prompts]
    assert len({r["content_digest"] for r in records}) == 1
    assert len(set(prompts)) == 4
    assert len({json.dumps(r["google_preflight_pair"], sort_keys=True) for r in records}) == 1
    for index, receipt in ((1, base.google_selector_receipt),
                           (2, base.google_flash_preflight_receipt)):
        assert records[index]["google_preflight_model"] == receipt.model
        review_round.validate_google_selector_prompt(
            prompts[index], receipt, expected_review_id=base.review_id,
            expected_content_digest=records[index]["content_digest"])


@pytest.mark.parametrize("field", ["google_selector_receipt", "google_flash_preflight_receipt"])
def test_either_preflight_changes_common_digest(worktree, field):
    base = _brief(worktree)
    changed = replace(base, **{field: replace(getattr(base, field), preflight_receipt_sha256="d" * 64)})
    first = _review_metadata(review_round.render_worktree_review_prompt(base))
    second = _review_metadata(review_round.render_worktree_review_prompt(changed))
    assert first["content_digest"] != second["content_digest"]


@pytest.mark.parametrize("changes", [
    {"model": PRO}, {"effort": "medium"}, {"review_id": "foreign-r1"},
    {"receipt_sha256": "e" * 64}, {"route_args": ("--model", PRO, "--effort", "high")},
])
def test_pair_rejects_wrong_flash_receipt(worktree, changes):
    base = _brief(worktree)
    bad = replace(base, google_flash_preflight_receipt=replace(base.google_flash_preflight_receipt, **changes))
    with pytest.raises(review_round.RoundIntegrityError):
        review_round.render_worktree_review_prompt(bad)


def test_missing_pair_cannot_select_flash(worktree):
    base = _brief(worktree)
    with pytest.raises(review_round.RoundIntegrityError):
        review_round.render_worktree_review_prompt(replace(
            base, google_flash_preflight_receipt=None, google_review_model=FLASH))


@pytest.mark.parametrize("tamper", ["pair", "selected", "digest", "remove"])
def test_dispatch_rejects_pair_or_selection_tamper(worktree, tamper):
    base = _brief(worktree)
    prompt = review_round.render_worktree_review_prompt(replace(base, google_review_model=FLASH))
    metadata = _review_metadata(prompt)
    digest = metadata["content_digest"]
    if tamper == "pair":
        metadata["google_preflight_pair"][PRO]["google_preflight_receipt_sha256"] = "d" * 64
    elif tamper == "selected":
        metadata["google_preflight_model"] = PRO
    elif tamper == "digest":
        metadata["content_digest"] = metadata["worktree_review_digest"] = "f" * 64
        digest = "f" * 64
    else:
        del metadata["google_preflight_pair"]
    with pytest.raises(review_round.RoundIntegrityError):
        review_round.validate_google_selector_prompt(
            "Review metadata: " + json.dumps(metadata), base.google_flash_preflight_receipt,
            expected_review_id=base.review_id, expected_content_digest=digest)


def test_flash_receipt_canonical_validation(tmp_path):
    pro = _google_selector_receipt("four-leg-r1")
    record = {"executable": str(pro.executable), "google_selector_receipt_sha256": pro.receipt_sha256,
              "provider_started": False, "review_id": pro.review_id, "route": "agy",
              "agy_version": "1.1.20", "effort": "high", "model": FLASH,
              "route_args": ["--model", FLASH, "--effort", "high"]}
    path = tmp_path / "flash.json"
    payload = _canonical_json_bytes(record)
    path.write_bytes(payload)
    receipt = review_round.validate_google_preflight_receipt(path, pro, expected_review_id=pro.review_id)
    assert receipt.model == FLASH
    assert receipt.preflight_receipt_sha256 == hashlib.sha256(payload).hexdigest()


def test_cli_renders_and_binds_both_real_receipts(worktree, tmp_path):
    base = _brief(worktree)
    selector_path, pro_path, flash_path = [tmp_path / name for name in
                                         ("selector.json", "pro.json", "flash.json")]
    _write_google_selector_receipt(selector_path, review_id=base.review_id,
        authentication_class="personal-google", route="agy",
        executable=base.google_selector_receipt.executable)
    _write_google_preflight_receipt(pro_path, selector_receipt=selector_path,
        review_id=base.review_id, route="agy", executable=base.google_selector_receipt.executable)
    flash_record = json.loads(pro_path.read_bytes())
    flash_record.update(model=FLASH, route_args=["--model", FLASH, "--effort", "high"])
    flash_path.write_bytes(_canonical_json_bytes(flash_record))
    selector = review_round.load_google_selector_receipt(selector_path, expected_review_id=base.review_id)
    digests = set()
    for index, (family, model) in enumerate((("claude", PRO), ("google", PRO), ("google", FLASH), ("codex", PRO))):
        output = tmp_path / f"prompt-{index}.txt"
        args = ["render-worktree", "--review-id", base.review_id, "--review-kind", "pre-merge",
                "--family", family, "--google-review-model", model,
                "--google-selector-receipt", str(selector_path), "--google-preflight-receipt", str(pro_path),
                "--google-flash-preflight-receipt", str(flash_path),
                "--objective", base.objective, "--worktree", str(worktree),
                "--worktree-fingerprint", base.worktree_fingerprint, "--task-file", str(base.task_file),
                "--status-file", str(base.status_file), "--diff-file", str(base.diff_file),
                "--criterion", base.criteria[0], "--review-point", base.review_points[0],
                "--approved-boundary", base.approved_boundary[0], "--output", str(output)]
        assert review_round.main(args) == 0
        metadata = _review_metadata(output.read_text())
        digests.add(metadata["content_digest"])
        if family == "google":
            receipt = review_round.validate_google_preflight_receipt(
                flash_path if model == FLASH else pro_path, selector, expected_review_id=base.review_id)
            review_round.validate_google_selector_prompt(output.read_text(), receipt,
                expected_review_id=base.review_id, expected_content_digest=metadata["content_digest"])
    assert len(digests) == 1
