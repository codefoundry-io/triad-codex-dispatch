"""C4/C5/C7: only allocated, exported evidence may be reclaimed."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import review_round


def _fixture(tmp_path):
    base = (tmp_path / "temp").resolve()
    base.mkdir()
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("retained evidence\n", encoding="utf-8")
    members = tmp_path / "members.json"
    members.write_text(json.dumps(["a.txt"]), encoding="utf-8")
    return base, source.resolve(), members.resolve()


def _prepare(tmp_path, review_id="owned", now=4_000_000.0):
    base, source, members = _fixture(tmp_path)
    prepared = review_round.prepare_review_workspace(
        review_id, source, members, temp_root=base, now=now
    )
    return base, Path(prepared.root)


@pytest.mark.parametrize("marker", [False, True])
def test_cleanup_preserves_unproven_same_uid_root(tmp_path, marker):
    base, _source, _members = _fixture(tmp_path)
    root = base / "triad-review-foreign"
    root.mkdir()
    if marker:
        (root / ".last_activity").write_bytes(b"")
    keep = root / "keep.txt"
    keep.write_text("foreign evidence", encoding="utf-8")
    with pytest.raises(review_round.RoundIntegrityError, match="allocation"):
        review_round.cleanup_review_workspace("foreign", root, temp_root=base)
    assert keep.read_text(encoding="utf-8") == "foreign evidence"


def test_cleanup_preserves_unexported_allocation(tmp_path):
    base, root = _prepare(tmp_path)
    with pytest.raises(review_round.RoundIntegrityError, match="export"):
        review_round.cleanup_review_workspace("owned", root, temp_root=base)
    assert (root / "shared/source/product/a.txt").read_text() == "retained evidence\n"


def test_stale_sweep_preserves_unproven_and_unexported_roots(tmp_path):
    base, source, members = _fixture(tmp_path)
    old = 4_000_000.0
    owned = Path(review_round.prepare_review_workspace(
        "unexported", source, members, temp_root=base, now=old
    ).root)
    foreign = base / "triad-review-foreign"
    foreign.mkdir()
    (foreign / ".last_activity").write_bytes(b"")
    (foreign / "keep.txt").write_text("foreign", encoding="utf-8")
    os.utime(foreign / ".last_activity", (old, old))
    current = review_round.prepare_review_workspace(
        "current", source, members, temp_root=base, now=old + 31 * 86400
    )
    assert owned.is_dir() and foreign.is_dir()
    assert current.swept_roots == ()
    assert set(current.skipped_roots) == {str(owned), str(foreign)}


def _export(base, root, output):
    return review_round.export_review_workspace(
        "owned", root, output.resolve(), temp_root=base
    )


def test_export_retains_bytes_and_link_text_without_following_target(tmp_path):
    base, root = _prepare(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.txt").write_text("outside secret", encoding="utf-8")
    (root / "results/link").symlink_to(outside, target_is_directory=True)
    output = tmp_path / "retained"
    _export(base, root, output)
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["inventory"]["results/link"] == {
        "kind": "symlink", "target": str(outside)
    }
    assert (output / "artifacts/shared/source/product/a.txt").read_text() == "retained evidence\n"
    assert not (output / "artifacts/results/link").exists()
    assert review_round.cleanup_review_workspace("owned", root, temp_root=base).removed
    assert (outside / "keep.txt").read_text() == "outside secret"
    assert (output / "manifest.json").is_file()
    assert not review_round.cleanup_review_workspace("owned", root, temp_root=base).removed


@pytest.mark.parametrize("change", ["late", "changed", "missing"])
def test_cleanup_refuses_evidence_drift_after_export(tmp_path, change):
    base, root = _prepare(tmp_path)
    _export(base, root, tmp_path / "retained")
    target = root / "shared/source/product/a.txt"
    if change == "late":
        (root / "results/late.txt").write_text("new evidence")
    elif change == "changed":
        target.write_text("changed evidence")
    else:
        target.unlink()
    with pytest.raises(review_round.RoundIntegrityError, match="evidence"):
        review_round.cleanup_review_workspace("owned", root, temp_root=base)
    assert root.is_dir()


def test_cleanup_reverifies_export_bytes(tmp_path):
    base, root = _prepare(tmp_path)
    output = tmp_path / "retained"
    _export(base, root, output)
    (output / "artifacts/shared/source/product/a.txt").write_text("tampered")
    with pytest.raises(review_round.RoundIntegrityError, match="export"):
        review_round.cleanup_review_workspace("owned", root, temp_root=base)
    assert root.is_dir()


@pytest.mark.parametrize("destination", ["self", "other-review", "claim"])
def test_export_refuses_reclaimable_destination(tmp_path, destination):
    base, root = _prepare(tmp_path)
    parent = root
    if destination == "other-review":
        parent = base / "triad-review-other"
        parent.mkdir()
    elif destination == "claim":
        parent = base / ".triad-review-other.cleanup"
        parent.mkdir()
    with pytest.raises(review_round.RoundIntegrityError, match="destination"):
        _export(base, root, parent / "retained")
    assert root.is_dir()


def test_export_failure_preserves_source_and_does_not_authorize_cleanup(tmp_path, monkeypatch):
    base, root = _prepare(tmp_path)
    def fail_copy(*_args):
        raise review_round.RoundIntegrityError("synthetic copy failure")
    monkeypatch.setattr(review_round, "_copy_source_member", fail_copy)
    with pytest.raises(review_round.RoundIntegrityError, match="copy failure"):
        _export(base, root, tmp_path / "failed-export")
    with pytest.raises(review_round.RoundIntegrityError, match="export"):
        review_round.cleanup_review_workspace("owned", root, temp_root=base)
    assert (root / "shared/source/product/a.txt").read_text() == "retained evidence\n"


def test_partial_cleanup_resumes_only_from_proven_claim(tmp_path, monkeypatch):
    base, root = _prepare(tmp_path)
    output = tmp_path / "retained"
    _export(base, root, output)
    original = review_round.shutil.rmtree
    def partial(path):
        (Path(path) / "shared/source/product/a.txt").unlink()
        raise OSError("synthetic partial removal")
    monkeypatch.setattr(review_round.shutil, "rmtree", partial)
    with pytest.raises(review_round.RoundIntegrityError, match="could not be removed"):
        review_round.cleanup_review_workspace("owned", root, temp_root=base)
    assert not root.exists()
    monkeypatch.setattr(review_round.shutil, "rmtree", original)
    assert review_round.cleanup_review_workspace("owned", root, temp_root=base).removed
    assert not review_round.cleanup_review_workspace("owned", root, temp_root=base).removed
    assert not list(base.iterdir())
    assert (output / "artifacts/shared/source/product/a.txt").read_text() == "retained evidence\n"


def test_cleanup_preserves_foreign_claim_directory(tmp_path):
    base, root = _prepare(tmp_path)
    _export(base, root, tmp_path / "retained")
    claim = base / ".triad-review-owned.cleanup"
    claim.mkdir()
    (claim / "keep.txt").write_text("foreign claim")
    with pytest.raises(review_round.RoundIntegrityError, match="claim"):
        review_round.cleanup_review_workspace("owned", root, temp_root=base)
    assert (claim / "keep.txt").read_text() == "foreign claim"
    assert root.is_dir()


def test_cleanup_preserves_root_replaced_before_claim(tmp_path, monkeypatch):
    base, root = _prepare(tmp_path)
    _export(base, root, tmp_path / "retained")
    original = Path.rename
    held = tmp_path / "original-held"
    def replace_before_rename(path, destination):
        if path == root:
            original(path, held)
            path.mkdir()
            (path / "keep.txt").write_text("foreign replacement")
        return original(path, destination)
    monkeypatch.setattr(Path, "rename", replace_before_rename)
    with pytest.raises(review_round.RoundIntegrityError, match="identity"):
        review_round.cleanup_review_workspace("owned", root, temp_root=base)
    assert (base / ".triad-review-owned.cleanup/root/keep.txt").read_text() == "foreign replacement"
    assert (held / "shared/source/product/a.txt").read_text() == "retained evidence\n"


@pytest.mark.parametrize("record", ["allocation", "export", "manifest"])
@pytest.mark.parametrize("damage", ["missing", "corrupt", "symlink"])
def test_cleanup_refuses_damaged_custody_records(tmp_path, record, damage):
    base, root = _prepare(tmp_path)
    output = tmp_path / "retained"
    _export(base, root, output)
    path = (output / "manifest.json" if record == "manifest"
            else base / f".triad-review-owned.{record}.json")
    original = path.read_bytes()
    path.unlink()
    if damage == "corrupt":
        path.write_bytes(b"{}\n")
    elif damage == "symlink":
        other = tmp_path / "other-record"
        other.write_bytes(original)
        path.symlink_to(other)
    with pytest.raises(review_round.RoundIntegrityError):
        review_round.cleanup_review_workspace("owned", root, temp_root=base)
    assert root.is_dir()


def test_stale_sweep_resumes_exported_claim_using_original_activity(tmp_path, monkeypatch):
    base, root = _prepare(tmp_path)
    _export(base, root, tmp_path / "retained")
    original = review_round.shutil.rmtree
    def partial(path):
        (Path(path) / ".last_activity").unlink()
        raise OSError("partial removal")
    monkeypatch.setattr(review_round.shutil, "rmtree", partial)
    with pytest.raises(review_round.RoundIntegrityError):
        review_round.cleanup_review_workspace("owned", root, temp_root=base)
    monkeypatch.setattr(review_round.shutil, "rmtree", original)
    with pytest.raises(review_round.RoundIntegrityError, match="exists"):
        review_round.prepare_review_workspace(
            "owned", (tmp_path / "source").resolve(), (tmp_path / "members.json").resolve(),
            temp_root=base, now=4_000_000 + 31 * 86400,
        )
    current = review_round.prepare_review_workspace(
        "current", (tmp_path / "source").resolve(), (tmp_path / "members.json").resolve(),
        temp_root=base, now=4_000_000 + 31 * 86400,
    )
    assert current.swept_roots == (str(root),)
    assert not (base / ".triad-review-owned.cleanup").exists()


def test_cleanup_rechecks_evidence_after_claim_move(tmp_path, monkeypatch):
    base, root = _prepare(tmp_path)
    _export(base, root, tmp_path / "retained")
    original = Path.rename
    def mutate_after_move(path, destination):
        result = original(path, destination)
        if path == root:
            (destination / "results/late.txt").write_text("late")
        return result
    monkeypatch.setattr(Path, "rename", mutate_after_move)
    with pytest.raises(review_round.RoundIntegrityError, match="evidence"):
        review_round.cleanup_review_workspace("owned", root, temp_root=base)
    assert (base / ".triad-review-owned.cleanup/root/results/late.txt").read_text() == "late"


def test_export_missing_parent_is_a_custody_refusal(tmp_path):
    base, root = _prepare(tmp_path)
    with pytest.raises(review_round.RoundIntegrityError, match="export.*preserv"):
        _export(base, root, tmp_path / "missing-parent" / "export")
    assert root.is_dir()


@pytest.mark.parametrize("operation", ["mkdir", "rename", "rmdir", "unlink"])
def test_cleanup_io_failure_is_a_custody_refusal(tmp_path, monkeypatch, operation):
    base, root = _prepare(tmp_path)
    _export(base, root, tmp_path / "retained")
    original = getattr(Path, operation)
    def fail_owned_path(path, *args, **kwargs):
        if path == root or path.name.startswith(".triad-review-owned."):
            raise PermissionError("synthetic filesystem refusal")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, operation, fail_owned_path)
    with pytest.raises(review_round.RoundIntegrityError, match="cleanup.*preserv"):
        review_round.cleanup_review_workspace("owned", root, temp_root=base)
    assert (tmp_path / "retained/artifacts/shared/source/product/a.txt").read_text() == "retained evidence\n"
    monkeypatch.setattr(Path, operation, original)
    retried = review_round.cleanup_review_workspace("owned", root, temp_root=base)
    assert retried.removed is (operation != "unlink")
    assert not list(base.iterdir())


@pytest.mark.parametrize("operation", ["copy", "digest"])
def test_guarded_source_read_refuses_fifo_without_blocking(tmp_path, monkeypatch, operation):
    source = tmp_path.resolve()
    victim = source / "a.txt"
    victim.write_text("old")
    _, expected = review_round._source_member(source, "a.txt")
    victim.unlink()
    os.mkfifo(victim)
    original = review_round.os.open
    def checked_open(path, flags, *args, **kwargs):
        if path == "a.txt":
            assert flags & os.O_NONBLOCK
        return original(path, flags, *args, **kwargs)
    monkeypatch.setattr(review_round.os, "open", checked_open)
    with pytest.raises(review_round.RoundIntegrityError, match="changed or is unsafe"):
        if operation == "copy":
            review_round._copy_source_member(source, "a.txt", expected, source / "output")
        else:
            review_round._source_member_digest(source, "a.txt", expected)


@pytest.mark.parametrize("vanished", ["root", "allocation"])
def test_prepare_rollback_disappearance_keeps_original_diagnostic(tmp_path, monkeypatch, vanished):
    base, source, members = _fixture(tmp_path)
    root = base / "triad-review-owned"
    foreign = base / "unrelated.txt"
    foreign.write_text("preserve")

    def fail_copy(*_args):
        if vanished == "root":
            review_round.shutil.rmtree(root)
        else:
            (base / ".triad-review-owned.allocation.json").unlink()
        raise review_round.RoundIntegrityError("synthetic member-copy failure")

    monkeypatch.setattr(review_round, "_copy_source_member", fail_copy)
    with pytest.raises(review_round.RoundIntegrityError, match="synthetic member-copy failure"):
        review_round.prepare_review_workspace("owned", source, members, temp_root=base)
    assert foreign.read_text() == "preserve"
