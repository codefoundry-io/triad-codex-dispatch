"""C4/C5: real fallback allocation and provider-free next-run cleanup."""
import json
import os
from pathlib import Path
import sys
import tempfile
import time

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
import _common


@pytest.fixture
def fallback(tmp_path, monkeypatch):
    base = (tmp_path / "temporary").resolve()
    base.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(base))
    primary = tmp_path / "blocked-primary"
    primary.write_text("occupied")
    monkeypatch.setattr(_common, "_LOG_DIR", primary)
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", False)
    result = _common.RunResult(exit_code=1, stdout="retained answer", stderr="failure",
        elapsed_s=0.1, classification="unknown", final_answer="retained answer")
    def allocate():
        path = _common.emit_run_log("gemini", ["wrapper"], ["gemini"], "prompt", result)
        assert path is not None and path.parent.parent == base
        proof = base / f".{path.parent.name}.allocation.json"
        assert proof.is_file(), "real fallback writer must establish allocation proof"
        return path, proof
    return base, result, allocate


def age(*paths):
    old = time.time() - 7200
    for path in paths:
        os.utime(path, (old, old))


def sweep(base, floor=3600):
    _common.prune_stale_tmp_dirs("triad-gemini-run-log-", age_floor_s=floor, base=str(base))


def test_C4_unproven_old_prefix_directory_survives(tmp_path):
    root = tmp_path / "triad-gemini-run-log-unowned"
    root.mkdir()
    sentinel = root / "foreign.json"
    sentinel.write_text("foreign")
    age(root, sentinel)
    sweep(tmp_path)
    assert sentinel.read_text() == "foreign"


def test_C4_actual_fallback_proof_and_stale_removal(fallback):
    base, result, allocate = fallback
    path, proof = allocate()
    record = json.loads(proof.read_text())
    assert record["root"] == str(path.parent)
    assert record["identity"]["inode"] == path.parent.stat().st_ino
    assert json.loads(path.read_text())["stdout"] == result.stdout
    age(path, proof, path.parent)
    sweep(base)
    assert not path.parent.exists() and not proof.exists()
    sweep(base)  # repeat is a no-op


def test_C4_floor_uses_proof_and_cannot_be_lowered(fallback):
    base, _, allocate = fallback
    path, proof = allocate()
    age(path.parent, path)
    sweep(base, floor=0)
    assert path.exists() and proof.exists()
    age(proof)
    # A newer directory mtime does not restart a proven allocation's floor.
    os.utime(path.parent, None)
    sweep(base)
    assert not path.parent.exists() and not proof.exists()


@pytest.mark.parametrize("damage", ["invalid", "identity", "root", "symlink", "hardlink"])
def test_C4_invalid_or_foreign_proof_preserves_contents(fallback, damage):
    base, _, allocate = fallback
    path, proof = allocate()
    record = json.loads(proof.read_text())
    if damage == "invalid":
        proof.write_text("incomplete{")
    elif damage in ("identity", "root"):
        if damage == "identity":
            record["identity"]["inode"] += 1
        else:
            record["root"] += "-other"
        proof.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    elif damage == "symlink":
        saved = base / "foreign-proof"
        proof.rename(saved)
        proof.symlink_to(saved)
        age(saved)
    else:
        os.link(proof, base / "foreign-proof")
    age(path, path.parent)
    if not proof.is_symlink():
        age(proof)
    sweep(base)
    assert path.is_file() and proof.exists()


@pytest.mark.parametrize("extra", [".git", "nested"])
def test_C4_unexpected_subdirectory_is_not_recursively_claimed(fallback, extra):
    base, _, allocate = fallback
    path, proof = allocate()
    nested = path.parent / extra
    nested.mkdir()
    (nested / "foreign").write_text("keep")
    age(path, proof, path.parent)
    sweep(base)
    assert (nested / "foreign").read_text() == "keep"
    assert path.exists() and proof.exists()


@pytest.mark.parametrize("change", [None, "new", "modified"])
def test_C5_interrupted_cleanup_keeps_proof_and_checks_remaining_subset(fallback, monkeypatch, change):
    base, _, allocate = fallback
    path, proof = allocate()
    repair = path.with_name(path.name + ".repair.json")
    repair.write_text("{}")
    age(path, repair, proof, path.parent)
    unlink = os.unlink
    def interrupted(name, *args, **kwargs):
        if str(name) == repair.name:
            raise OSError("synthetic interruption")
        return unlink(name, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(os, "unlink", interrupted)
        sweep(base)
    assert not path.exists() and repair.exists() and proof.exists()
    # Directory and proof may now be fresh; a started removal resumes without
    # waiting another hour, but never takes newly added/changed data with it.
    if change == "new":
        (repair.parent / "new.json").write_text("foreign")
    elif change == "modified":
        repair.write_text("changed")
    sweep(base)
    if change is None:
        assert not repair.parent.exists() and not proof.exists()
    else:
        assert repair.exists() and proof.exists()


@pytest.mark.parametrize("companion", [False, True])
def test_C4_owned_leaf_symlink_is_removed_without_touching_target(fallback, companion):
    base, _, allocate = fallback
    path, proof = allocate()
    target = base / "outside-allocation.txt"
    target.write_text("keep")
    leaf = path.with_name(path.name + ".repair.json") if companion else path
    if not companion:
        path.unlink()
    leaf.symlink_to(target)
    age(proof, path.parent)
    sweep(base)
    assert target.read_text() == "keep"
    assert not path.parent.exists() and not proof.exists()


def test_C5_orphan_proof_is_removed_after_owned_root_is_gone(fallback):
    base, _, allocate = fallback
    path, proof = allocate()
    path.unlink()
    path.parent.rmdir()  # this test owns the fixture
    age(proof)
    sweep(base)
    assert not proof.exists()


def test_C4_proof_storage_failure_does_not_hide_existing_failure_ipc(fallback, monkeypatch):
    base, result, _ = fallback
    original = _common._open_regular_nofollow
    def fail_proof(fd, name, **kwargs):
        if name.endswith(".allocation.json"):
            raise OSError("proof storage unavailable")
        return original(fd, name, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(_common, "_open_regular_nofollow", fail_proof)
        path = _common.emit_run_log("gemini", ["wrapper"], ["gemini"], "prompt", result)
    assert path is not None and json.loads(path.read_text())["stdout"] == result.stdout
    assert result.exit_code == 1 and result.final_answer == "retained answer"
    age(path, path.parent)
    sweep(base)
    assert path.exists()


def test_C5_partial_start_waits_then_checks_current_contents(fallback):
    base, _, allocate = fallback
    path, proof = allocate()
    with proof.open("ab") as stream:
        stream.write(b'{"deleting":')
    sweep(base)
    assert path.exists() and proof.exists()
    # Incomplete start data never authorizes a subset-only resumed deletion.
    foreign = path.parent / "foreign.json"
    foreign.write_text("keep")
    age(proof)
    sweep(base)
    assert foreign.read_text() == "keep" and path.exists()
    foreign.unlink()  # this test owns the fixture
    sweep(base)
    assert not path.parent.exists() and not proof.exists()


@pytest.mark.parametrize("unexpected", [False, True])
def test_C4_failed_fallback_write_rolls_back_only_own_empty_directory(
    fallback, monkeypatch, unexpected
):
    base, result, _ = fallback
    def fail_write(fd, payload):
        if unexpected:
            root = next(base.glob("triad-gemini-run-log-*"))
            (root / "foreign").write_text("keep")
        raise OSError("synthetic fallback leaf write failure")
    with monkeypatch.context() as patch:
        patch.setattr(_common, "_write_all", fail_write)
        with pytest.raises(OSError, match="synthetic fallback leaf write failure"):
            _common.emit_run_log("gemini", ["wrapper"], ["gemini"], "prompt", result)
    roots = list(base.glob("triad-gemini-run-log-*"))
    if unexpected:
        assert len(roots) == 1 and (roots[0] / "foreign").read_text() == "keep"
    else:
        assert roots == []
    assert result.exit_code == 1 and result.final_answer == "retained answer"


def test_C5_overlapping_sweeps_cannot_replace_started_inventory(fallback, monkeypatch):
    from threading import Event, Thread, current_thread

    base, _, allocate = fallback
    path, proof = allocate()
    repair = path.with_name(path.name + ".repair.json")
    repair.write_text("original")
    age(path, repair, proof, path.parent)
    first_ready, release_first = Event(), Event()
    second_ready, release_second = Event(), Event()
    inventory, unlink = _common._fallback_inventory, os.unlink
    errors = []

    def gated_inventory(fd, run_log):
        if current_thread().name == "second-sweep":
            # Before the fix, this caller has read an unstarted proof. After
            # serialization it skips the busy allocation before reaching here.
            second_ready.set()
            assert release_second.wait(10), "second sweep was not released"
        result = inventory(fd, run_log)
        if current_thread().name == "first-sweep":
            # Pause before ftruncate/write can refresh the proof's age, so
            # the other reader really observes the same old unstarted proof.
            first_ready.set()
            assert release_first.wait(10), "first sweep was not released"
        return result

    def interrupted(name, *args, **kwargs):
        if current_thread().name == "first-sweep" and str(name) == repair.name:
            raise OSError("synthetic interruption after deleting the original log")
        return unlink(name, *args, **kwargs)

    def run():
        try:
            sweep(base)
        except BaseException as error:
            errors.append(error)
        finally:
            if current_thread().name == "second-sweep":
                second_ready.set()

    first = Thread(target=run, name="first-sweep")
    second = Thread(target=run, name="second-sweep")
    with monkeypatch.context() as patch:
        patch.setattr(_common, "_fallback_inventory", gated_inventory)
        patch.setattr(os, "unlink", interrupted)
        try:
            first.start()
            assert first_ready.wait(10)
            assert proof.stat().st_mtime < time.time() - 3600
            assert len(proof.read_bytes().splitlines()) == 1
            second.start()
            assert second_ready.wait(10)
            release_first.set()
            first.join(10)
            assert not first.is_alive() and not errors
            assert not path.exists() and repair.exists()
            started = proof.read_bytes()
            repair.write_text("changed after the first deletion started")
        finally:
            release_first.set()
            release_second.set()
            first.join(10)
            if second.ident is not None:
                second.join(10)
    assert not first.is_alive() and not second.is_alive() and not errors
    assert repair.exists(), "overlapping sweep deleted the changed remainder"
    assert proof.read_bytes() == started, "overlapping sweep replaced the start record"
    # A later non-overlapping resume also preserves that changed remainder.
    sweep(base)
    assert repair.read_text() == "changed after the first deletion started"
    assert proof.read_bytes() == started
