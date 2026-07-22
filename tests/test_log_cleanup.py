#!/usr/bin/env python3
"""Run-log prune + audit-rotation policy tests (stdlib-only, no pytest).

Covers: (1) stale run-log prune removes the run-log AND its `.repair.json`
pair while keeping fresh files; (2) audit() rotates the active audit.jsonl
past AUDIT_ROTATE_BYTES and bounds archives by AUDIT_MAX_ARCHIVES.

Runs in BOTH layouts: the triad source repo (tests/ beside the wrappers) and the
exported plugin (`tests/` with a `bin/` sibling).
"""
from __future__ import annotations

import fcntl
import json
import os
import stat
import subprocess
import sys
sys.dont_write_bytecode = True  # keep an installed plugin dir pristine
import tempfile
import time
import traceback
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BIN = _ROOT / "bin" if (_ROOT / "bin").is_dir() else _ROOT
sys.path.insert(0, str(_BIN))

import _common  # noqa: E402

# Module attrs each test may override; the runner snapshots + restores them so
# tests stay isolated within the single process (the pytest-monkeypatch role).
_PATCHED_ATTRS = (
    "_LOG_DIR", "AUDIT_ROTATE_BYTES", "AUDIT_MAX_ARCHIVES", "AUDIT_ARCHIVE_MAX_BYTES",
    "_RUN_LOG_MAX_FILES", "_RUN_LOG_MAX_BYTES",
)
_IMPORTED_ATTRS = {attr: getattr(_common, attr) for attr in _PATCHED_ATTRS}
_PYTEST_ATTR_SNAPSHOT: dict[str, object] | None = None


def setup_function(_function: object) -> None:
    global _PYTEST_ATTR_SNAPSHOT
    _PYTEST_ATTR_SNAPSHOT = {
        attr: getattr(_common, attr) for attr in _PATCHED_ATTRS
    }


def teardown_function(_function: object) -> None:
    global _PYTEST_ATTR_SNAPSHOT
    snapshot = _PYTEST_ATTR_SNAPSHOT
    _PYTEST_ATTR_SNAPSHOT = None
    if snapshot is not None:
        for attr, value in snapshot.items():
            setattr(_common, attr, value)


def _result(stdout: str = "x") -> "_common.RunResult":
    return _common.RunResult(
        exit_code=_common.EXIT_CLI_FAIL,
        stdout=stdout,
        stderr="err",
        elapsed_s=0.1,
        classification="unknown",
        final_answer="",
        vendor_exit_code=1,
    )


_AUDIT_CHILD_PREFIX = r"""
import errno
import json
import os
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import _common

_common._LOG_DIR = Path(sys.argv[2])
result = _common.RunResult(
    exit_code=_common.EXIT_OK,
    stdout="provider stdout",
    stderr="provider stderr",
    elapsed_s=0.25,
    classification="ok",
    final_answer="provider answer",
    vendor_exit_code=0,
)
"""

_AUDIT_CHILD_SUFFIX = r"""
started = time.monotonic()
path = _common.persist_result_artifacts(
    "gemini", ["wrapper"], ["gemini"], "prompt", result, debug=False
)
print(json.dumps({
    "elapsed": time.monotonic() - started,
    "path": str(path) if path is not None else None,
    "stdout": result.stdout,
    "answer": result.final_answer,
    "exit_code": result.exit_code,
    "classification": result.classification,
}))
"""


def _run_audit_child(
    log_root: Path,
    *,
    before: str = "",
    timeout_s: float = 1.5,
) -> dict:
    script = _AUDIT_CHILD_PREFIX + before + _AUDIT_CHILD_SUFFIX
    # macOS exposes its temporary root through /var -> /private/var. Canonicalize
    # that trusted test-harness parent while deliberately preserving the audit
    # root leaf itself so the symlinked-ancestor case remains hostile.
    child_log_root = log_root.parent.resolve() / log_root.name
    try:
        proc = subprocess.run(
            [sys.executable, "-c", script, str(_BIN), str(child_log_root)],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired as exc:
        raise AssertionError("audit persistence blocked result delivery") from exc
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["elapsed"] < 1.0
    assert payload["path"] is None
    assert payload["stdout"] == "provider stdout"
    assert payload["answer"] == "provider answer"
    assert payload["exit_code"] == _common.EXIT_OK
    assert payload["classification"] == "ok"
    return payload


def _foreign_sentinel(tmp_path: Path) -> tuple[Path, bytes]:
    target = tmp_path / "foreign-target"
    content = b"foreign bytes must survive\n"
    target.write_bytes(content)
    return target, content


def test_audit_lock_fifo_is_advisory_and_nonblocking(tmp_path: Path) -> None:
    log_root = tmp_path / "logs"
    log_dir = log_root / "gemini"
    log_dir.mkdir(parents=True)
    os.mkfifo(log_dir / ".audit.lock", 0o600)
    foreign, content = _foreign_sentinel(tmp_path)

    _run_audit_child(log_root)

    assert stat.S_ISFIFO((log_dir / ".audit.lock").lstat().st_mode)
    assert not (log_dir / "audit.jsonl").exists()
    assert foreign.read_bytes() == content


def test_audit_log_fifo_is_advisory_and_nonblocking(tmp_path: Path) -> None:
    log_root = tmp_path / "logs"
    log_dir = log_root / "gemini"
    log_dir.mkdir(parents=True)
    os.mkfifo(log_dir / "audit.jsonl", 0o600)
    foreign, content = _foreign_sentinel(tmp_path)

    _run_audit_child(log_root)

    assert stat.S_ISFIFO((log_dir / "audit.jsonl").lstat().st_mode)
    assert foreign.read_bytes() == content


def test_audit_lock_symlink_is_advisory_and_no_follow(tmp_path: Path) -> None:
    log_root = tmp_path / "logs"
    log_dir = log_root / "gemini"
    log_dir.mkdir(parents=True)
    foreign, content = _foreign_sentinel(tmp_path)
    (log_dir / ".audit.lock").symlink_to(foreign)

    _run_audit_child(log_root)

    assert (log_dir / ".audit.lock").is_symlink()
    assert not (log_dir / "audit.jsonl").exists()
    assert foreign.read_bytes() == content


def test_audit_log_symlink_is_advisory_and_no_follow(tmp_path: Path) -> None:
    log_root = tmp_path / "logs"
    log_dir = log_root / "gemini"
    log_dir.mkdir(parents=True)
    foreign, content = _foreign_sentinel(tmp_path)
    (log_dir / "audit.jsonl").symlink_to(foreign)

    _run_audit_child(log_root)

    assert (log_dir / "audit.jsonl").is_symlink()
    assert foreign.read_bytes() == content


def test_audit_symlinked_ancestor_is_advisory_and_no_follow(tmp_path: Path) -> None:
    foreign_dir = tmp_path / "foreign-dir"
    foreign_dir.mkdir()
    foreign, content = _foreign_sentinel(foreign_dir)
    log_root = tmp_path / "logs"
    log_root.symlink_to(foreign_dir, target_is_directory=True)

    _run_audit_child(log_root)

    assert log_root.is_symlink()
    assert not (foreign_dir / "gemini").exists()
    assert foreign.read_bytes() == content


def test_audit_held_lock_is_advisory_and_bounded(tmp_path: Path) -> None:
    log_root = tmp_path / "logs"
    log_dir = log_root / "gemini"
    log_dir.mkdir(parents=True)
    lock_path = log_dir / ".audit.lock"
    lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    foreign, content = _foreign_sentinel(tmp_path)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _run_audit_child(log_root)
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)

    assert not (log_dir / "audit.jsonl").exists()
    assert foreign.read_bytes() == content


def test_audit_inode_replacement_does_not_modify_replacement(
    tmp_path: Path,
) -> None:
    log_root = tmp_path / "logs"
    log_dir = log_root / "gemini"
    log_dir.mkdir(parents=True)
    foreign, content = _foreign_sentinel(tmp_path)
    before = r"""
original_open = _common._open_regular_nofollow
_common.AUDIT_ROTATE_BYTES = 1

def replace_after_open(dir_fd, name, *args, **kwargs):
    fd = original_open(dir_fd, name, *args, **kwargs)
    if name == "audit.jsonl":
        os.rename(
            "audit.jsonl", "opened-audit.jsonl",
            src_dir_fd=dir_fd, dst_dir_fd=dir_fd,
        )
        replacement_fd = os.open(
            "audit.jsonl",
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=dir_fd,
        )
        try:
            os.write(replacement_fd, b"foreign replacement\n")
        finally:
            os.close(replacement_fd)
    return fd

_common._open_regular_nofollow = replace_after_open
"""

    _run_audit_child(log_root, before=before)

    assert (log_dir / "audit.jsonl").read_bytes() == b"foreign replacement\n"
    assert (log_dir / "opened-audit.jsonl").read_bytes() == b""
    archives = [
        path
        for path in log_dir.glob("audit.*.jsonl")
        if path.name != "audit.jsonl" and not path.is_symlink()
    ]
    assert len(archives) == 1
    assert b'"final_answer_head": "provider answer"' in archives[0].read_bytes()
    assert foreign.read_bytes() == content


def test_audit_hardlink_is_advisory_and_preserves_foreign_inode(
    tmp_path: Path,
) -> None:
    log_root = tmp_path / "logs"
    log_dir = log_root / "gemini"
    log_dir.mkdir(parents=True)
    foreign, content = _foreign_sentinel(tmp_path)
    os.link(foreign, log_dir / "audit.jsonl")

    _run_audit_child(log_root)

    assert (log_dir / "audit.jsonl").stat().st_nlink == 2
    assert foreign.read_bytes() == content


def test_audit_normalizes_safe_legacy_leaf_modes(tmp_path: Path) -> None:
    log_root = tmp_path / "logs"
    log_dir = log_root / "gemini"
    log_dir.mkdir(parents=True)
    lock_path = log_dir / ".audit.lock"
    audit_path = log_dir / "audit.jsonl"
    lock_path.write_bytes(b"")
    audit_path.write_bytes(b"")
    lock_path.chmod(0o644)
    audit_path.chmod(0o644)
    foreign, content = _foreign_sentinel(tmp_path)

    _run_audit_child(log_root)

    assert stat.S_IMODE(lock_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(audit_path.stat().st_mode) == 0o600
    assert foreign.read_bytes() == content


def test_audit_first_use_eexist_preserves_both_writer_records(
    tmp_path: Path,
) -> None:
    log_root = tmp_path / "logs"
    log_root.mkdir()
    foreign, content = _foreign_sentinel(tmp_path)
    before = r"""
original_mkdir = os.mkdir
injected = False

def competing_mkdir(path, mode=0o777, *, dir_fd=None):
    global injected
    if path == "gemini" and not injected:
        injected = True
        original_mkdir(path, mode, dir_fd=dir_fd)
        raise FileExistsError(errno.EEXIST, "simulated competing writer", path)
    return original_mkdir(path, mode, dir_fd=dir_fd)

os.mkdir = competing_mkdir
first_result = _common.RunResult(
    exit_code=_common.EXIT_OK,
    stdout="writer one stdout",
    stderr="writer one stderr",
    elapsed_s=0.20,
    classification="ok",
    final_answer="writer one answer",
    vendor_exit_code=0,
)
_common.persist_result_artifacts(
    "gemini", ["wrapper"], ["gemini"], "writer one prompt",
    first_result, debug=False,
)
os.mkdir = original_mkdir
assert first_result.stdout == "writer one stdout"
assert first_result.final_answer == "writer one answer"
assert first_result.exit_code == _common.EXIT_OK
assert first_result.classification == "ok"
"""

    _run_audit_child(log_root, before=before)

    records = [
        json.loads(line)
        for line in (log_root / "gemini" / "audit.jsonl").read_text().splitlines()
    ]
    assert [record["final_answer_head"] for record in records] == [
        "writer one answer",
        "provider answer",
    ]
    assert foreign.read_bytes() == content


def test_audit_archive_byte_cap_prunes_complete_archive(tmp_path: Path) -> None:
    log_root = tmp_path / "logs"
    foreign, content = _foreign_sentinel(tmp_path)
    before = """
_common.AUDIT_ROTATE_BYTES = 1
_common.AUDIT_MAX_ARCHIVES = 100
_common.AUDIT_ARCHIVE_MAX_BYTES = 1
"""

    _run_audit_child(log_root, before=before)

    log_dir = log_root / "gemini"
    archives = [
        path
        for path in log_dir.glob("audit.*.jsonl")
        if path.name != "audit.jsonl"
    ]
    assert archives == []
    assert (log_dir / "audit.jsonl").read_bytes() == b""
    assert foreign.read_bytes() == content


def test_audit_partial_archive_copy_keeps_complete_active_record(
    tmp_path: Path,
) -> None:
    log_root = tmp_path / "logs"
    foreign, content = _foreign_sentinel(tmp_path)
    before = r"""
_common.AUDIT_ROTATE_BYTES = 1
original_write_all = _common._write_all
write_calls = 0

def partial_archive_write(fd, data):
    global write_calls
    write_calls += 1
    if write_calls == 2:
        raw = bytes(data)
        os.write(fd, raw[:max(1, len(raw) // 2)])
        raise OSError(errno.EIO, "injected partial archive copy")
    return original_write_all(fd, data)

_common._write_all = partial_archive_write
"""

    _run_audit_child(log_root, before=before)

    log_dir = log_root / "gemini"
    records = [
        json.loads(line)
        for line in (log_dir / "audit.jsonl").read_text().splitlines()
    ]
    assert len(records) == 1
    assert records[0]["final_answer_head"] == "provider answer"
    assert not any(
        path.name != "audit.jsonl"
        for path in log_dir.glob("audit.*.jsonl")
    )
    assert foreign.read_bytes() == content


def test_audit_rotation_ignores_symlinked_archive_and_preserves_target(
    tmp_path: Path,
) -> None:
    log_root = tmp_path / "logs"
    log_dir = log_root / "gemini"
    log_dir.mkdir(parents=True)
    foreign, content = _foreign_sentinel(tmp_path)
    archive_link = log_dir / "audit.20000101T000000Z-1-deadbeef.jsonl"
    archive_link.symlink_to(foreign)
    old = time.time() - 10_000
    os.utime(foreign, (old, old))
    before = """
_common.AUDIT_ROTATE_BYTES = 1
_common.AUDIT_MAX_ARCHIVES = 0
_common.AUDIT_ARCHIVE_MAX_BYTES = 0
"""

    _run_audit_child(log_root, before=before)

    assert archive_link.is_symlink()
    assert foreign.read_bytes() == content
    assert (log_dir / "audit.jsonl").read_bytes() == b""


def test_persist_result_artifacts_keeps_success_when_audit_storage_fails(
    tmp_path: Path,
) -> None:
    _common._LOG_DIR = tmp_path / "not-a-directory"
    _common._LOG_DIR.write_text("occupied", encoding="utf-8")
    result = _common.RunResult(
        exit_code=_common.EXIT_OK,
        stdout="provider stdout",
        stderr="",
        elapsed_s=0.1,
        classification="ok",
        final_answer="provider answer",
        vendor_exit_code=0,
    )

    path = _common.persist_result_artifacts(
        "gemini", ["wrapper"], ["gemini"], "prompt", result, debug=False
    )

    assert path is None
    assert result.exit_code == _common.EXIT_OK
    assert result.final_answer == "provider answer"


def test_failed_result_uses_unique_file_ipc_when_primary_log_root_fails(
    tmp_path: Path,
) -> None:
    _common._LOG_DIR = tmp_path / "not-a-directory"
    _common._LOG_DIR.write_text("occupied", encoding="utf-8")
    result = _result(stdout="hostile '$()' `bytes`\n한글")

    path = _common.persist_result_artifacts(
        "gemini", ["wrapper"], ["gemini"], "prompt", result, debug=False
    )

    assert path is not None
    assert path.is_absolute()
    assert path.is_file()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["stdout"] == result.stdout
    assert payload["exit_code"] == result.exit_code


def _assert_symlinked_run_log_ancestor_falls_back(
    tmp_path: Path, ancestor: str
) -> None:
    managed_root = tmp_path / "managed-logs"
    foreign_root = tmp_path / "foreign"
    foreign_root.mkdir()
    if ancestor == "root":
        managed_root.symlink_to(foreign_root, target_is_directory=True)
    elif ancestor == "cli":
        managed_root.mkdir()
        (managed_root / "gemini").symlink_to(
            foreign_root, target_is_directory=True
        )
    else:
        (managed_root / "gemini").mkdir(parents=True)
        (managed_root / "gemini" / "runs").symlink_to(
            foreign_root, target_is_directory=True
        )
    _common._LOG_DIR = managed_root
    result = _result(stdout="hostile '$()' `bytes`\n한글")

    path = _common.emit_run_log(
        "gemini", ["wrapper"], ["gemini"], "prompt", result
    )

    assert path is not None
    assert path.is_file()
    assert foreign_root not in path.parents
    assert list(foreign_root.iterdir()) == []
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["stdout"] == result.stdout


def test_emit_run_log_symlinked_root_falls_back_without_foreign_write(
    tmp_path: Path,
) -> None:
    _assert_symlinked_run_log_ancestor_falls_back(tmp_path, "root")


def test_emit_run_log_symlinked_cli_falls_back_without_foreign_write(
    tmp_path: Path,
) -> None:
    _assert_symlinked_run_log_ancestor_falls_back(tmp_path, "cli")


def test_emit_run_log_symlinked_runs_falls_back_without_foreign_write(
    tmp_path: Path,
) -> None:
    _assert_symlinked_run_log_ancestor_falls_back(tmp_path, "runs")


def test_run_log_cap_prune_skips_symlinked_runs_directory(tmp_path: Path) -> None:
    foreign_runs = tmp_path / "foreign-runs"
    foreign_runs.mkdir()
    foreign = foreign_runs / "old.json"
    foreign.write_text("foreign\n", encoding="utf-8")
    stale = time.time() - _common._STALE_IPC_AGE_FLOOR_S - 1
    os.utime(foreign, (stale, stale))
    managed = tmp_path / "managed"
    managed.mkdir()
    runs_link = managed / "runs"
    runs_link.symlink_to(foreign_runs, target_is_directory=True)
    _common._RUN_LOG_MAX_FILES = 0

    _common._prune_run_logs(runs_link)

    assert runs_link.is_symlink()
    assert foreign.read_text(encoding="utf-8") == "foreign\n"


def test_run_log_cap_prune_skips_symlink_and_hardlink_leaves(
    tmp_path: Path,
) -> None:
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    foreign = tmp_path / "foreign.json"
    foreign.write_text("foreign\n", encoding="utf-8")
    symlink_leaf = runs_dir / "old-symlink.json"
    hardlink_leaf = runs_dir / "old-hardlink.json"
    symlink_leaf.symlink_to(foreign)
    os.link(foreign, hardlink_leaf)
    stale = time.time() - _common._STALE_IPC_AGE_FLOOR_S - 1
    os.utime(foreign, (stale, stale))
    _common._RUN_LOG_MAX_FILES = 0
    _common._RUN_LOG_MAX_BYTES = 0

    _common._prune_run_logs(runs_dir)

    assert symlink_leaf.is_symlink()
    assert hardlink_leaf.is_file()
    assert foreign.read_text(encoding="utf-8") == "foreign\n"


def test_run_log_prune_failure_does_not_hide_written_ipc(
    tmp_path: Path,
) -> None:
    _common._LOG_DIR = tmp_path / "logs"
    original = _common._prune_run_logs_fd
    _common._prune_run_logs_fd = lambda *_args, **_kwargs: (_ for _ in ()).throw(
        OSError("injected prune failure")
    )
    try:
        path = _common.emit_run_log(
            "gemini", ["wrapper"], ["gemini"], "prompt", _result()
        )
    finally:
        _common._prune_run_logs_fd = original

    assert path is not None
    assert path.is_file()


def test_next_run_prunes_stale_fallback_ipc_directory(tmp_path: Path) -> None:
    prefix = "triad-gemini-run-log-"
    fallback = tmp_path / f"{prefix}old"
    fallback.mkdir()
    (fallback / "run.json").write_text("{}", encoding="utf-8")
    old = time.time() - 10_000
    os.utime(fallback, (old, old))
    original_gettempdir = tempfile.gettempdir
    tempfile.gettempdir = lambda: str(tmp_path)
    try:
        _common._LOG_DIR = tmp_path / "normal-logs"
        _common.prune_stale_run_logs("gemini", age_floor_s=7200)
    finally:
        tempfile.gettempdir = original_gettempdir

    assert not fallback.exists()


def test_stale_run_log_prune_removes_repair_json_pair(tmp_path: Path) -> None:
    _common._LOG_DIR = tmp_path / "_logs"
    runs_dir = tmp_path / "_logs" / "gemini" / "runs"
    runs_dir.mkdir(parents=True)
    run_log = runs_dir / "old.json"
    repair = runs_dir / "old.json.repair.json"
    fresh = runs_dir / "fresh.json"
    for path in (run_log, repair, fresh):
        path.write_text("{}\n", encoding="utf-8")
    old = time.time() - 10_000
    os.utime(run_log, (old, old))
    os.utime(repair, (old, old))

    _common.prune_stale_run_logs("gemini", age_floor_s=7200)

    assert not run_log.exists()
    assert not repair.exists()
    assert fresh.exists()


def test_stale_run_log_prune_default_floor_is_one_hour(tmp_path: Path) -> None:
    _common._LOG_DIR = tmp_path / "_logs"
    runs_dir = tmp_path / "_logs" / "gemini" / "runs"
    runs_dir.mkdir(parents=True)
    stale = runs_dir / "stale.json"
    fresh = runs_dir / "fresh.prompt.tmp"
    unrelated = runs_dir / "unrelated.txt"
    for path in (stale, fresh, unrelated):
        path.write_text("{}\n", encoding="utf-8")
    now = time.time()
    os.utime(stale, (now - 3601, now - 3601))
    os.utime(fresh, (now - 3599, now - 3599))
    os.utime(unrelated, (now - 7201, now - 7201))

    _common.prune_stale_run_logs("gemini")

    assert not stale.exists()
    assert fresh.exists()
    assert unrelated.exists()


def test_stale_run_log_prune_skips_symlinked_managed_root_and_leaf(
    tmp_path: Path,
) -> None:
    foreign_root = tmp_path / "foreign-root"
    foreign_runs = foreign_root / "gemini" / "runs"
    foreign_runs.mkdir(parents=True)
    foreign_log = foreign_runs / "stale.json"
    foreign_log.write_text("{}\n", encoding="utf-8")
    old = time.time() - 3601
    os.utime(foreign_log, (old, old))
    managed_root = tmp_path / "managed-root"
    managed_root.symlink_to(foreign_root, target_is_directory=True)
    _common._LOG_DIR = managed_root

    _common.prune_stale_run_logs("gemini")

    assert foreign_log.exists()

    _common._LOG_DIR = tmp_path / "_logs"
    runs_dir = _common._LOG_DIR / "gemini" / "runs"
    runs_dir.mkdir(parents=True)
    foreign_leaf = tmp_path / "foreign-leaf"
    foreign_leaf.write_text("foreign\n", encoding="utf-8")
    os.utime(foreign_leaf, (old, old))
    leaf = runs_dir / "stale.json"
    leaf.symlink_to(foreign_leaf)

    _common.prune_stale_run_logs("gemini")

    assert leaf.is_symlink()
    assert foreign_leaf.exists()


def test_stale_run_log_prune_tolerates_unlink_error(tmp_path: Path, monkeypatch) -> None:
    _common._LOG_DIR = tmp_path / "_logs"
    runs_dir = tmp_path / "_logs" / "gemini" / "runs"
    runs_dir.mkdir(parents=True)
    stale = runs_dir / "stale.json"
    stale.write_text("{}\n", encoding="utf-8")
    old = time.time() - 3601
    os.utime(stale, (old, old))

    monkeypatch.setattr(
        os,
        "unlink",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("denied")),
    )

    _common.prune_stale_run_logs("gemini")

    assert stale.exists()


@pytest.mark.parametrize("cleanup", ["runs", "tmp"])
def test_public_cleanup_tolerates_directory_enumeration_error(
    tmp_path: Path, monkeypatch, cleanup: str
) -> None:
    monkeypatch.setattr(_common, "_open_directory_nofollow", lambda *_args, **_kwargs: 42)
    monkeypatch.setattr(
        os,
        "listdir",
        lambda _fd: (_ for _ in ()).throw(OSError("enumeration failed")),
    )
    if cleanup == "runs":
        monkeypatch.setattr(_common, "prune_stale_tmp_dirs", lambda *_args, **_kwargs: None)
        _common.prune_stale_run_logs("gemini")
    else:
        _common.prune_stale_tmp_dirs("triad-gemini-run-log-", base=str(tmp_path))


@pytest.mark.parametrize("cleanup", ["runs", "tmp"])
def test_public_cleanup_tolerates_directory_close_error(
    tmp_path: Path, monkeypatch, cleanup: str
) -> None:
    monkeypatch.setattr(_common, "_open_directory_nofollow", lambda *_args, **_kwargs: 42)
    monkeypatch.setattr(os, "listdir", lambda _fd: [])
    monkeypatch.setattr(
        os,
        "close",
        lambda _fd: (_ for _ in ()).throw(OSError("close failed")),
    )
    if cleanup == "runs":
        monkeypatch.setattr(_common, "prune_stale_tmp_dirs", lambda *_args, **_kwargs: None)
        _common.prune_stale_run_logs("gemini")
    else:
        _common.prune_stale_tmp_dirs("triad-gemini-run-log-", base=str(tmp_path))


def test_run_log_count_cap_prunes_only_stale_files_and_allows_fresh_overflow(
    tmp_path: Path,
) -> None:
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    old = runs_dir / "old.json"
    live_sibling = runs_dir / "live-sibling.prompt.tmp"
    current = runs_dir / "current.json"
    for path in (old, live_sibling, current):
        path.write_text("{}\n", encoding="utf-8")
    stale = time.time() - _common._STALE_IPC_AGE_FLOOR_S - 1
    os.utime(old, (stale, stale))
    _common._RUN_LOG_MAX_FILES = 1

    _common._prune_run_logs(runs_dir, preserve=current)

    assert not old.exists()
    assert live_sibling.exists()
    assert current.exists()
    assert len(list(runs_dir.iterdir())) == 2


def test_run_log_byte_cap_prunes_only_stale_files_and_allows_fresh_overflow(
    tmp_path: Path,
) -> None:
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    old = runs_dir / "old.json"
    live_sibling = runs_dir / "live-sibling.prompt.tmp"
    current = runs_dir / "current.json"
    old.write_bytes(b"x")
    live_sibling.write_bytes(b"fresh!")
    current.write_bytes(b"current")
    stale = time.time() - _common._STALE_IPC_AGE_FLOOR_S - 1
    os.utime(old, (stale, stale))
    _common._RUN_LOG_MAX_FILES = 100
    _common._RUN_LOG_MAX_BYTES = 1

    _common._prune_run_logs(runs_dir, preserve=current)

    assert not old.exists()
    assert live_sibling.exists()
    assert current.exists()
    assert sum(path.stat().st_size for path in runs_dir.iterdir()) > _common._RUN_LOG_MAX_BYTES


def _prune_after_final_stat_refreshes_candidate(
    runs_dir: Path, candidate: Path, current: Path
) -> None:
    original_open = _common._open_regular_nofollow
    candidate_open_calls = 0

    def open_with_final_refresh(
        dir_fd: int,
        name: str,
        *,
        flags: int,
        mode: int = 0o600,
        normalize_mode: bool = True,
    ) -> int:
        nonlocal candidate_open_calls
        if name == candidate.name:
            candidate_open_calls += 1
            if candidate_open_calls == 3:
                os.utime(candidate, None)
        return original_open(
            dir_fd,
            name,
            flags=flags,
            mode=mode,
            normalize_mode=normalize_mode,
        )

    _common._open_regular_nofollow = open_with_final_refresh
    try:
        _common._prune_run_logs(runs_dir, preserve=current)
    finally:
        _common._open_regular_nofollow = original_open


def test_run_log_count_cap_preserves_candidate_refreshed_before_unlink(
    tmp_path: Path,
) -> None:
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    candidate = runs_dir / "candidate.json"
    sibling = runs_dir / "live-sibling.prompt.tmp"
    current = runs_dir / "current.json"
    for path in (candidate, sibling, current):
        path.write_text("{}\n", encoding="utf-8")
    stale = time.time() - _common._STALE_IPC_AGE_FLOOR_S - 1
    os.utime(candidate, (stale, stale))
    _common._RUN_LOG_MAX_FILES = 1

    _prune_after_final_stat_refreshes_candidate(runs_dir, candidate, current)

    assert candidate.exists()
    assert sibling.exists()
    assert current.exists()
    assert len(list(runs_dir.iterdir())) == 3


def test_run_log_byte_cap_preserves_candidate_refreshed_before_unlink(
    tmp_path: Path,
) -> None:
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    candidate = runs_dir / "candidate.json"
    sibling = runs_dir / "live-sibling.prompt.tmp"
    current = runs_dir / "current.json"
    candidate.write_bytes(b"candidate")
    sibling.write_bytes(b"sibling")
    current.write_bytes(b"current")
    stale = time.time() - _common._STALE_IPC_AGE_FLOOR_S - 1
    os.utime(candidate, (stale, stale))
    _common._RUN_LOG_MAX_FILES = 100
    _common._RUN_LOG_MAX_BYTES = 1

    _prune_after_final_stat_refreshes_candidate(runs_dir, candidate, current)

    assert candidate.exists()
    assert sibling.exists()
    assert current.exists()
    assert sum(path.stat().st_size for path in runs_dir.iterdir()) > _common._RUN_LOG_MAX_BYTES


def test_stale_run_log_preserves_candidate_refreshed_on_final_open(
    tmp_path: Path,
) -> None:
    _common._LOG_DIR = tmp_path / "_logs"
    runs_dir = _common._LOG_DIR / "gemini" / "runs"
    runs_dir.mkdir(parents=True)
    candidate = runs_dir / "candidate.json"
    candidate.write_text("{}\n", encoding="utf-8")
    stale = time.time() - 7201
    os.utime(candidate, (stale, stale))
    original_open = _common._open_regular_nofollow
    candidate_open_calls = 0

    def open_with_final_refresh(
        dir_fd: int,
        name: str,
        *,
        flags: int,
        mode: int = 0o600,
        normalize_mode: bool = True,
    ) -> int:
        nonlocal candidate_open_calls
        if name == candidate.name:
            candidate_open_calls += 1
            if candidate_open_calls == 2:
                os.utime(candidate, None)
        return original_open(
            dir_fd,
            name,
            flags=flags,
            mode=mode,
            normalize_mode=normalize_mode,
        )

    _common._open_regular_nofollow = open_with_final_refresh
    try:
        _common.prune_stale_run_logs("gemini", age_floor_s=7200)
    finally:
        _common._open_regular_nofollow = original_open

    assert candidate.exists()


def test_audit_rotation_prunes_archives_by_count(tmp_path: Path) -> None:
    _common._LOG_DIR = tmp_path.resolve() / "_logs"
    _common.AUDIT_ROTATE_BYTES = 200
    _common.AUDIT_MAX_ARCHIVES = 2
    _common.AUDIT_ARCHIVE_MAX_BYTES = 10_000
    result = _common.RunResult(
        exit_code=_common.EXIT_OK,
        stdout="x" * 500,
        stderr="provider stderr",
        elapsed_s=0.25,
        classification="ok",
        final_answer="provider answer",
        vendor_exit_code=0,
    )
    foreign, content = _foreign_sentinel(tmp_path)

    for _ in range(5):
        _common.audit("gemini", ["fake"], "prompt", result)

    log_dir = tmp_path.resolve() / "_logs" / "gemini"
    assert (log_dir / "audit.jsonl").is_file()
    assert (log_dir / "audit.jsonl").read_bytes() == b""
    assert stat.S_IMODE((log_dir / "audit.jsonl").stat().st_mode) == 0o600
    assert stat.S_IMODE((log_dir / ".audit.lock").stat().st_mode) == 0o600
    archives = [
        path
        for path in log_dir.glob("audit.*.jsonl")
        if path.name != "audit.jsonl"
    ]
    assert 1 <= len(archives) <= 2
    for archive in archives:
        archive_stat = archive.stat()
        assert stat.S_ISREG(archive_stat.st_mode)
        assert archive_stat.st_nlink == 1
        assert stat.S_IMODE(archive_stat.st_mode) == 0o600
        records = [json.loads(line) for line in archive.read_text().splitlines()]
        assert records
        assert all(record["final_answer_head"] == "provider answer" for record in records)
    assert result.stdout == "x" * 500
    assert result.final_answer == "provider answer"
    assert result.exit_code == _common.EXIT_OK
    assert result.classification == "ok"
    assert foreign.read_bytes() == content


def test_pytest_restores_common_globals_between_tests() -> None:
    assert {
        attr: getattr(_common, attr) for attr in _PATCHED_ATTRS
    } == _IMPORTED_ATTRS


TESTS = [
    test_persist_result_artifacts_keeps_success_when_audit_storage_fails,
    test_failed_result_uses_unique_file_ipc_when_primary_log_root_fails,
    test_emit_run_log_symlinked_root_falls_back_without_foreign_write,
    test_emit_run_log_symlinked_cli_falls_back_without_foreign_write,
    test_emit_run_log_symlinked_runs_falls_back_without_foreign_write,
    test_run_log_cap_prune_skips_symlinked_runs_directory,
    test_run_log_cap_prune_skips_symlink_and_hardlink_leaves,
    test_run_log_prune_failure_does_not_hide_written_ipc,
    test_next_run_prunes_stale_fallback_ipc_directory,
    test_stale_run_log_prune_removes_repair_json_pair,
    test_run_log_count_cap_prunes_only_stale_files_and_allows_fresh_overflow,
    test_run_log_byte_cap_prunes_only_stale_files_and_allows_fresh_overflow,
    test_run_log_count_cap_preserves_candidate_refreshed_before_unlink,
    test_run_log_byte_cap_preserves_candidate_refreshed_before_unlink,
    test_audit_lock_fifo_is_advisory_and_nonblocking,
    test_audit_log_fifo_is_advisory_and_nonblocking,
    test_audit_lock_symlink_is_advisory_and_no_follow,
    test_audit_log_symlink_is_advisory_and_no_follow,
    test_audit_symlinked_ancestor_is_advisory_and_no_follow,
    test_audit_held_lock_is_advisory_and_bounded,
    test_audit_inode_replacement_does_not_modify_replacement,
    test_audit_hardlink_is_advisory_and_preserves_foreign_inode,
    test_audit_normalizes_safe_legacy_leaf_modes,
    test_audit_first_use_eexist_preserves_both_writer_records,
    test_audit_archive_byte_cap_prunes_complete_archive,
    test_audit_partial_archive_copy_keeps_complete_active_record,
    test_audit_rotation_ignores_symlinked_archive_and_preserves_target,
    test_audit_rotation_prunes_archives_by_count,
]


def main() -> int:
    failed = 0
    for fn in TESTS:
        snapshot = {a: getattr(_common, a) for a in _PATCHED_ATTRS}
        with tempfile.TemporaryDirectory() as td:
            try:
                fn(Path(td).resolve())
                print(f"  PASS  {fn.__name__}")
            except Exception:
                failed += 1
                print(f"  FAIL  {fn.__name__}")
                traceback.print_exc()
            finally:
                for a, v in snapshot.items():
                    setattr(_common, a, v)
    print(f"{len(TESTS) - failed}/{len(TESTS)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
