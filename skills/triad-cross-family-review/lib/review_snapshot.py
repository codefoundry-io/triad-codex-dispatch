#!/usr/bin/env python3
"""Create and verify a code-complete read-only Git working-tree snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import NamedTuple

SCHEMA = "triad.review-snapshot.v1"
CREATE_SCHEMA = "triad.review-snapshot-create.v1"
VERIFY_SCHEMA = "triad.review-snapshot-verification.v1"
MANIFEST = "SNAPSHOT_SHA256SUMS"
RECEIPT = "SNAPSHOT_RECEIPT.json"
CONTROL_DIRS = {".git", ".pytest_cache", "__pycache__", "_runs", "_debug"}
CONTROL_SUFFIXES = (".pyc", ".pyo", ".swp", ".tmp")
HEX = re.compile(r"[0-9a-f]{64}")
CHUNK = 1024 * 1024

class SnapshotError(RuntimeError): pass
class Scan(NamedTuple):
    head: str
    branch: str | None
    tracked: tuple[str, ...]
    deleted: tuple[str, ...]
    untracked: tuple[str, ...]
    ignored: tuple[str, ...]
    index: tuple[tuple[str, str, str], ...]
def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
def _json_bytes(value: object) -> bytes:
    return (_json(value) + "\n").encode("ascii")
def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
def _canonical_dir(value: str | os.PathLike[str], label: str) -> Path:
    path = Path(value)
    if not path.is_absolute() or "\n" in str(path) or "\r" in str(path):
        raise SnapshotError(f"{label} must be a one-line absolute path")
    try:
        resolved, info = path.resolve(strict=True), path.lstat()
    except OSError as exc:
        raise SnapshotError(f"{label} is unavailable: {exc}") from exc
    if path != resolved or stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise SnapshotError(f"{label} must be a canonical real directory")
    return path
def _git(repo: Path, *args: str, rc: tuple[int, ...] = (0,)) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise SnapshotError(f"cannot execute git: {exc}") from exc
    if result.returncode not in rc:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise SnapshotError(f"git {' '.join(args)} failed ({result.returncode}): {detail}")
    return result.stdout
def _path(raw: bytes, label: str) -> str:
    value = os.fsdecode(raw)
    pure = PurePosixPath(value)
    if not value or pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise SnapshotError(f"unsafe {label} path: {value!r}")
    if "/".join(pure.parts) != value:
        raise SnapshotError(f"non-canonical {label} path: {value!r}")
    return value
def _paths(data: bytes, label: str) -> tuple[str, ...]:
    records = data.split(b"\0")
    if records[-1:] == [b""]: records.pop()
    values = tuple(sorted(_path(item, label) for item in records))
    if len(values) != len(set(values)):
        raise SnapshotError(f"duplicate {label} paths")
    return values
def _stages(data: bytes) -> tuple[tuple[str, str, str], ...]:
    values = []
    for record in data.rstrip(b"\0").split(b"\0") if data else ():
        meta, tab, raw = record.partition(b"\t")
        fields = meta.split(b" ")
        if not tab or len(fields) != 3:
            raise SnapshotError("invalid Git index record")
        mode, stage = fields[0].decode("ascii"), fields[2].decode("ascii")
        path = _path(raw, "index")
        if mode == "160000":
            raise SnapshotError(f"gitlink/submodule is unsupported: {path}")
        if mode == "120000":
            raise SnapshotError(f"tracked symlink is unsupported: {path}")
        if mode not in {"100644", "100755"} or stage != "0":
            raise SnapshotError(f"unsupported Git index entry {mode}/{stage}: {path}")
        values.append((path, mode, stage))
    return tuple(sorted(values))
def _scan(repo: Path) -> Scan:
    top = os.fsdecode(_git(repo, "rev-parse", "--show-toplevel").rstrip(b"\n"))
    if Path(top).resolve(strict=True) != repo:
        raise SnapshotError("repo must be the canonical Git top-level")
    head = _git(repo, "rev-parse", "--verify", "HEAD").decode("ascii").strip().lower()
    if re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", head) is None:
        raise SnapshotError("invalid Git HEAD")
    branch_run = subprocess.run(
        ["git", "-C", str(repo), "symbolic-ref", "--quiet", "--short", "HEAD"],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if branch_run.returncode not in (0, 1):
        raise SnapshotError("cannot determine Git branch")
    branch = os.fsdecode(branch_run.stdout.rstrip(b"\n")) if branch_run.returncode == 0 else None
    tracked = _paths(_git(repo, "ls-files", "-z", "--"), "tracked")
    deleted = _paths(_git(repo, "ls-files", "--deleted", "-z", "--"), "deleted")
    untracked = _paths(_git(repo, "ls-files", "--others", "--exclude-standard", "-z", "--"), "untracked")
    ignored = _paths(
        _git(repo, "ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--"),
        "ignored"
    )
    index = _stages(_git(repo, "ls-files", "--stage", "-z", "--"))
    if not set(deleted) <= set(tracked) or set(tracked) & set(untracked):
        raise SnapshotError("Git enumerations do not close")
    if tuple(path for path, _, _ in index) != tracked:
        raise SnapshotError("Git index and tracked paths differ")
    return Scan(head, branch, tracked, deleted, untracked, ignored, index)
def _reason(path: str) -> str | None:
    for part in PurePosixPath(path).parts:
        if part in CONTROL_DIRS:
            return f"directory:{part}"
    return next((f"suffix:{suffix}" for suffix in CONTROL_SUFFIXES if path.endswith(suffix)), None)
def _group(paths: tuple[str, ...]) -> dict[str, object]:
    listed = list(paths)
    return {"count": len(listed), "paths": listed, "paths_sha256": _sha(_json_bytes(listed))}
def _relative(path: str) -> Path:
    return Path(*PurePosixPath(path).parts)
def _open_directory(path: Path, label: str) -> int:
    required = ("O_DIRECTORY", "O_NOFOLLOW", "O_CLOEXEC")
    if any(not hasattr(os, name) for name in required):
        raise SnapshotError("O_DIRECTORY, O_NOFOLLOW, and O_CLOEXEC are required")
    try:
        before = path.lstat()
        descriptor = os.open(
            path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        )
    except OSError as exc:
        raise SnapshotError(f"cannot open {label} directory: {exc}") from exc
    opened = os.fstat(descriptor)
    if not stat.S_ISDIR(opened.st_mode) or (before.st_dev, before.st_ino) != (
        opened.st_dev, opened.st_ino
    ):
        os.close(descriptor)
        raise SnapshotError(f"{label} directory changed while opening")
    return descriptor
def _open_source_regular(repo_fd: int, path: str, label: str) -> tuple[int, os.stat_result]:
    required = ("O_DIRECTORY", "O_NOFOLLOW", "O_CLOEXEC")
    if any(not hasattr(os, name) for name in required):
        raise SnapshotError("O_DIRECTORY, O_NOFOLLOW, and O_CLOEXEC are required")
    parts = PurePosixPath(path).parts
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    leaf_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
    current = repo_fd
    opened_directories: list[int] = []
    try:
        for component in parts[:-1]:
            try:
                current = os.open(component, directory_flags, dir_fd=current)
            except (OSError, TypeError, NotImplementedError) as exc:
                raise SnapshotError(
                    f"{label} has a symlinked, unavailable, or non-directory ancestor: {exc}"
                ) from exc
            opened_directories.append(current)
        try:
            before = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        except (OSError, TypeError, NotImplementedError) as exc:
            raise SnapshotError(f"{label} is unavailable: {exc}") from exc
        if stat.S_ISLNK(before.st_mode):
            raise SnapshotError(f"{label} is a symlink")
        if not stat.S_ISREG(before.st_mode):
            raise SnapshotError(f"{label} is not a regular file")
        try:
            descriptor = os.open(parts[-1], leaf_flags, dir_fd=current)
        except (OSError, TypeError, NotImplementedError) as exc:
            raise SnapshotError(f"cannot open {label} without following symlinks: {exc}") from exc
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (
            opened.st_dev, opened.st_ino
        ):
            os.close(descriptor)
            raise SnapshotError(f"{label} changed while opening")
        return descriptor, opened
    finally:
        for descriptor in reversed(opened_directories):
            os.close(descriptor)
def _open_regular(path: Path, label: str) -> tuple[int, os.stat_result]:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_CLOEXEC"):
        raise SnapshotError("O_NOFOLLOW and O_CLOEXEC are required")
    try:
        before = path.lstat()
    except OSError as exc:
        raise SnapshotError(f"{label} is unavailable: {exc}") from exc
    if stat.S_ISLNK(before.st_mode):
        raise SnapshotError(f"{label} is a symlink")
    if not stat.S_ISREG(before.st_mode):
        raise SnapshotError(f"{label} is not a regular file")
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError as exc:
        raise SnapshotError(f"cannot open {label}: {exc}") from exc
    opened = os.fstat(descriptor)
    if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
        os.close(descriptor)
        raise SnapshotError(f"{label} changed while opening")
    return descriptor, opened
def _write_all(descriptor: int, data: bytes) -> None:
    offset = 0
    while offset < len(data):
        written = os.write(descriptor, data[offset:])
        if written <= 0:
            raise OSError("short write")
        offset += written
def _sealed_mode(mode: int) -> int:
    return 0o555 if stat.S_IMODE(mode) & 0o111 else 0o444
def _copy(repo_fd: int, candidate: Path, path: str, source: str) -> dict[str, object]:
    source_fd, before = _open_source_regular(repo_fd, path, f"source {path}")
    destination = candidate / _relative(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
    try:
        destination_fd = os.open(destination, flags, 0o600)
    except BaseException:
        os.close(source_fd)
        raise
    digest = hashlib.sha256()
    try:
        while chunk := os.read(source_fd, CHUNK):
            digest.update(chunk)
            _write_all(destination_fd, chunk)
        os.fsync(destination_fd)
        after = os.fstat(source_fd)
    finally:
        os.close(source_fd)
        os.close(destination_fd)
    stable = ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(before, item) != getattr(after, item) for item in stable):
        raise SnapshotError(f"source changed while copying: {path}")
    return {"path": path, "sealed_mode": _sealed_mode(before.st_mode),
            "sha256": digest.hexdigest(), "source": source}
def _write(path: Path, data: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
    descriptor = os.open(path, flags, 0o600)
    try:
        _write_all(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
def _read(path: Path, label: str) -> tuple[bytes, os.stat_result]:
    descriptor, before = _open_regular(path, label)
    chunks = []
    try:
        while chunk := os.read(descriptor, CHUNK):
            chunks.append(chunk)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
        after.st_size, after.st_mtime_ns, after.st_ctime_ns
    ):
        raise SnapshotError(f"{label} changed while reading")
    return b"".join(chunks), after
def _hash_regular(path: Path, label: str) -> tuple[str, os.stat_result]:
    descriptor, before = _open_regular(path, label)
    digest = hashlib.sha256()
    try:
        while chunk := os.read(descriptor, CHUNK):
            digest.update(chunk)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    stable = ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(before, item) != getattr(after, item) for item in stable):
        raise SnapshotError(f"{label} changed while hashing")
    return digest.hexdigest(), after
def _hash_source_regular(repo_fd: int, path: str, label: str) -> tuple[str, os.stat_result]:
    descriptor, before = _open_source_regular(repo_fd, path, label)
    digest = hashlib.sha256()
    try:
        while chunk := os.read(descriptor, CHUNK):
            digest.update(chunk)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    stable = ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(before, item) != getattr(after, item) for item in stable):
        raise SnapshotError(f"{label} changed while hashing")
    return digest.hexdigest(), after
def _recheck_sources(repo_fd: int, files: list[dict[str, object]]) -> None:
    for item in files:
        path = str(item["path"])
        digest, info = _hash_source_regular(repo_fd, path, f"source {path}")
        sealed_mode = _sealed_mode(info.st_mode)
        if digest != item["sha256"] or sealed_mode != item["sealed_mode"]:
            raise SnapshotError(f"source changed after copying: {path}")
def _manifest(files: list[dict[str, object]]) -> bytes:
    return "".join(
        f"{item['sha256']}  {json.dumps('candidate/' + str(item['path']), ensure_ascii=True)}\n"
        for item in files
    ).encode("ascii")
def _without_output(scan: Scan, repo: Path, output: Path) -> Scan:
    try:
        prefix = output.relative_to(repo).as_posix()
    except ValueError:
        return scan
    keep = lambda path: path != prefix and not path.startswith(prefix + "/")
    return scan._replace(
        untracked=tuple(path for path in scan.untracked if keep(path)),
        ignored=tuple(path for path in scan.ignored if keep(path)),
    )
def _check_source_universe(repo_fd: int, repo: Path, owned_output: Path | None) -> None:
    excluded: tuple[str, ...] | None = None
    if owned_output is not None:
        try:
            excluded = owned_output.relative_to(repo).parts
        except ValueError:
            pass
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    pending: list[tuple[int, tuple[str, ...], bool]] = [(repo_fd, (), False)]
    try:
        while pending:
            directory_fd, prefix, owned = pending.pop()
            try:
                try:
                    with os.scandir(directory_fd) as entries:
                        names = sorted(entry.name for entry in entries)
                except (OSError, TypeError, NotImplementedError) as exc:
                    raise SnapshotError(f"cannot inspect source tree: {exc}") from exc
                for name in names:
                    parts = (*prefix, name)
                    if name == ".git" or parts == excluded:
                        continue
                    display = PurePosixPath(*parts).as_posix()
                    try:
                        info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                    except (OSError, TypeError, NotImplementedError) as exc:
                        raise SnapshotError(f"source tree entry is unavailable: {display}: {exc}") from exc
                    if stat.S_ISLNK(info.st_mode):
                        raise SnapshotError(f"source tree entry is a symlink: {display}")
                    if stat.S_ISREG(info.st_mode):
                        continue
                    if not stat.S_ISDIR(info.st_mode):
                        raise SnapshotError(
                            f"source tree entry is not a regular file or directory: {display}"
                        )
                    try:
                        child_fd = os.open(name, flags, dir_fd=directory_fd)
                    except (OSError, TypeError, NotImplementedError) as exc:
                        raise SnapshotError(
                            f"source tree directory is unavailable or symlinked: {display}: {exc}"
                        ) from exc
                    transferred = False
                    try:
                        try:
                            opened = os.fstat(child_fd)
                        except OSError as exc:
                            raise SnapshotError(
                                f"cannot attest source tree directory: {display}: {exc}"
                            ) from exc
                        if (info.st_dev, info.st_ino) != (opened.st_dev, opened.st_ino):
                            raise SnapshotError(
                                f"source tree directory changed while opening: {display}"
                            )
                        pending.append((child_fd, parts, True))
                        transferred = True
                    finally:
                        if not transferred:
                            os.close(child_fd)
            finally:
                if owned:
                    os.close(directory_fd)
    finally:
        for descriptor, _, owned in pending:
            if owned:
                os.close(descriptor)
def _cleanup(root: Path) -> None:
    for current, directories, files in os.walk(root, topdown=False, followlinks=False):
        for name in files:
            path = Path(current, name)
            if not path.is_symlink():
                os.chmod(path, 0o600)
        for name in directories:
            path = Path(current, name)
            if not path.is_symlink():
                os.chmod(path, 0o700)
    os.chmod(root, 0o700)
    shutil.rmtree(root, ignore_errors=True)
def _seal(root: Path, files: list[dict[str, object]]) -> None:
    candidate = root / "candidate"
    for item in files:
        os.chmod(candidate / _relative(str(item["path"])), int(item["sealed_mode"]))
    directories = [path for path in candidate.rglob("*") if path.is_dir()]
    for path in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        os.chmod(path, 0o555)
    for path, mode in ((candidate, 0o555), (root / MANIFEST, 0o444), (root / RECEIPT, 0o444)):
        os.chmod(path, mode)
    os.chmod(root, 0o555)
def create_snapshot(repo: Path, output_parent: Path) -> dict[str, object]:
    repo = _canonical_dir(repo, "repo")
    repo_fd = _open_directory(repo, "repo")
    created: Path | None = None
    try:
        output_parent = _canonical_dir(output_parent, "output-parent")
        initial = _scan(repo)
        _check_source_universe(repo_fd, repo, None)
        deleted = set(initial.deleted)
        excluded = [
            {"path": path, "reason": reason, "source": "untracked_nonignored"}
            for path in initial.untracked
            if (reason := _reason(path)) is not None
        ]
        excluded_paths = {item["path"] for item in excluded}
        included = tuple(
            sorted((set(initial.tracked) - deleted) | (set(initial.untracked) - excluded_paths))
        )
        created = Path(tempfile.mkdtemp(prefix="triad-review-snapshot-", dir=output_parent))
        candidate = created / "candidate"
        candidate.mkdir()
        tracked = set(initial.tracked) - deleted
        files = [
            _copy(repo_fd, candidate, path, "tracked" if path in tracked else "untracked_nonignored")
            for path in included
        ]
        if _without_output(_scan(repo), repo, created) != initial:
            raise SnapshotError("repository enumeration changed while snapshotting")
        _recheck_sources(repo_fd, files)
        _check_source_universe(repo_fd, repo, created)
        if _without_output(_scan(repo), repo, created) != initial:
            raise SnapshotError("repository enumeration changed while snapshotting")
        _check_source_universe(repo_fd, repo, created)
        manifest = _manifest(files)
        _write(created / MANIFEST, manifest)
        receipt: dict[str, object] = {
            "schema": SCHEMA,
            "snapshot_root": str(created),
            "source": {"repo": str(repo), "head": initial.head, "branch": initial.branch},
            "enumeration": {
                "tracked": _group(initial.tracked),
                "deleted_tracked": _group(initial.deleted),
                "untracked_nonignored": _group(initial.untracked),
                "ignored_untracked": _group(initial.ignored),
                "excluded": excluded,
                "included": _group(included),
            },
            "files": files,
            "file_count": len(files),
            "manifest_sha256": _sha(manifest),
            "sealed_read_only": True,
        }
        _write(created / RECEIPT, _json_bytes(receipt))
        _seal(created, files)
        verify_snapshot(created)
        return receipt
    except BaseException:
        if created is not None:
            _cleanup(created)
        raise
    finally:
        os.close(repo_fd)
def _verify_group(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, dict) or set(value) != {"count", "paths", "paths_sha256"}:
        raise SnapshotError(f"invalid {label} path group")
    paths = value["paths"]
    if not isinstance(paths, list) or not all(isinstance(path, str) for path in paths):
        raise SnapshotError(f"invalid {label} paths")
    ordered = tuple(paths)
    if ordered != tuple(sorted(set(ordered))) or value["count"] != len(ordered):
        raise SnapshotError(f"invalid {label} path ordering/count")
    if value["paths_sha256"] != _sha(_json_bytes(paths)):
        raise SnapshotError(f"invalid {label} path digest")
    return ordered
def _candidate_tree(candidate: Path) -> tuple[set[str], set[str]]:
    files, directories, stack = set(), set(), [(candidate, PurePosixPath())]
    while stack:
        current, parent = stack.pop()
        for entry in os.scandir(current):
            relative = parent / entry.name
            name = relative.as_posix()
            if entry.is_symlink():
                raise SnapshotError(f"candidate symlink: {name}")
            info = entry.stat(follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                directories.add(name)
                stack.append((Path(entry.path), relative))
            elif stat.S_ISREG(info.st_mode):
                files.add(name)
            else:
                raise SnapshotError(f"candidate non-regular entry: {name}")
    return files, directories
def _readonly(path: Path, mode: int, label: str) -> None:
    actual = stat.S_IMODE(path.lstat().st_mode)
    if actual != mode or actual & 0o222:
        raise SnapshotError(f"read-only seal mismatch at {label}")
def verify_snapshot(snapshot_root: Path) -> dict[str, object]:
    root = _canonical_dir(snapshot_root, "snapshot-root")
    if {entry.name for entry in os.scandir(root)} != {"candidate", MANIFEST, RECEIPT}:
        raise SnapshotError("snapshot root file set mismatch")
    receipt_bytes, _ = _read(root / RECEIPT, RECEIPT)
    try:
        receipt = json.loads(receipt_bytes.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"invalid receipt JSON: {exc}") from exc
    if not isinstance(receipt, dict) or receipt_bytes != _json_bytes(receipt):
        raise SnapshotError("receipt is not canonical JSON")
    recorded_root = receipt.get("snapshot_root")
    if (
        receipt.get("schema") != SCHEMA
        or not isinstance(recorded_root, str)
        or not Path(recorded_root).is_absolute()
        or Path(recorded_root).name != root.name
    ):
        raise SnapshotError("receipt identity mismatch")
    source = receipt.get("source")
    if not isinstance(source, dict) or set(source) != {"repo", "head", "branch"}:
        raise SnapshotError("invalid receipt source")
    source_repo, source_head, source_branch = (
        source["repo"], source["head"], source["branch"]
    )
    if (
        not isinstance(source_repo, str)
        or not Path(source_repo).is_absolute()
        or "\n" in source_repo
        or "\r" in source_repo
        or not isinstance(source_head, str)
        or re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", source_head) is None
        or (
            source_branch is not None
            and (
                not isinstance(source_branch, str)
                or not source_branch
                or "\n" in source_branch
                or "\r" in source_branch
            )
        )
    ):
        raise SnapshotError("invalid receipt source identity")
    enumeration = receipt.get("enumeration")
    if not isinstance(enumeration, dict) or set(enumeration) != {
        "tracked", "deleted_tracked", "untracked_nonignored",
        "ignored_untracked", "excluded", "included",
    }:
        raise SnapshotError("invalid receipt enumeration")
    tracked = _verify_group(enumeration.get("tracked"), "tracked")
    deleted = _verify_group(enumeration.get("deleted_tracked"), "deleted")
    untracked = _verify_group(enumeration.get("untracked_nonignored"), "untracked")
    _verify_group(enumeration.get("ignored_untracked"), "ignored")
    included = _verify_group(enumeration.get("included"), "included")
    excluded = enumeration.get("excluded")
    if not isinstance(excluded, list):
        raise SnapshotError("invalid excluded receipt")
    excluded_paths = set()
    for item in excluded:
        if not isinstance(item, dict) or item.get("source") != "untracked_nonignored":
            raise SnapshotError("invalid excluded receipt entry")
        path, reason = item.get("path"), item.get("reason")
        if not isinstance(path, str) or path not in untracked or _reason(path) != reason:
            raise SnapshotError("invalid excluded receipt reason")
        excluded_paths.add(path)
    expected = tuple(sorted((set(tracked) - set(deleted)) | (set(untracked) - excluded_paths)))
    if included != expected:
        raise SnapshotError("receipt enumeration closure mismatch")
    files_value = receipt.get("files")
    if not isinstance(files_value, list):
        raise SnapshotError("invalid file receipt")
    files: dict[str, dict[str, object]] = {}
    for item in files_value:
        if not isinstance(item, dict) or set(item) != {
            "path", "sealed_mode", "sha256", "source"
        }:
            raise SnapshotError("invalid file receipt entry")
        path = item["path"]
        if not isinstance(path, str):
            raise SnapshotError("invalid file receipt path")
        _path(os.fsencode(path), "file receipt")
        expected_source = "tracked" if path in set(tracked) - set(deleted) else "untracked_nonignored"
        if (
            item["source"] != expected_source
            or type(item["sealed_mode"]) is not int
            or item["sealed_mode"] not in {0o444, 0o555}
            or not isinstance(item["sha256"], str)
            or HEX.fullmatch(item["sha256"]) is None
            or path in files
        ):
            raise SnapshotError(f"invalid file receipt metadata: {path}")
        files[path] = item
    if list(files) != sorted(files) or set(files) != set(included):
        raise SnapshotError("receipt file set mismatch")
    manifest_bytes, _ = _read(root / MANIFEST, MANIFEST)
    if receipt.get("manifest_sha256") != _sha(manifest_bytes):
        raise SnapshotError("manifest hash mismatch")
    manifest = {}
    for line in manifest_bytes.decode("ascii").splitlines():
        digest, separator, encoded = line.partition("  ")
        try:
            path = json.loads(encoded)
        except json.JSONDecodeError as exc:
            raise SnapshotError("invalid manifest path") from exc
        if not separator or not HEX.fullmatch(digest) or not isinstance(path, str):
            raise SnapshotError("invalid manifest entry")
        if not path.startswith("candidate/"):
            raise SnapshotError("manifest path escapes candidate")
        relative = path[10:]
        _path(os.fsencode(relative), "manifest")
        if relative in manifest:
            raise SnapshotError("duplicate manifest path")
        manifest[relative] = digest
    if set(manifest) != set(files):
        raise SnapshotError("manifest file set mismatch")
    candidate = root / "candidate"
    candidate_info = candidate.lstat()
    if stat.S_ISLNK(candidate_info.st_mode) or not stat.S_ISDIR(candidate_info.st_mode):
        raise SnapshotError("candidate must be a real directory")
    actual_files, actual_dirs = _candidate_tree(candidate)
    expected_dirs = {
        PurePosixPath(*PurePosixPath(path).parts[:length]).as_posix()
        for path in files
        for length in range(1, len(PurePosixPath(path).parts))
    }
    if actual_files != set(files) or actual_dirs != expected_dirs:
        raise SnapshotError("candidate file set mismatch")
    candidate_fd = _open_directory(candidate, "candidate")
    try:
        for path, item in files.items():
            if not isinstance(item.get("sha256"), str) or manifest[path] != item["sha256"]:
                raise SnapshotError(f"receipt/manifest hash mismatch: {path}")
            digest, _ = _hash_source_regular(candidate_fd, path, f"candidate/{path}")
            if digest != item["sha256"]:
                raise SnapshotError(f"candidate hash mismatch: {path}")
            _readonly(
                candidate / _relative(path), int(item["sealed_mode"]), f"candidate/{path}"
            )
    finally:
        os.close(candidate_fd)
    _readonly(root, 0o555, "snapshot root")
    _readonly(candidate, 0o555, "candidate")
    _readonly(root / MANIFEST, 0o444, MANIFEST)
    _readonly(root / RECEIPT, 0o444, RECEIPT)
    for path in actual_dirs:
        _readonly(candidate / _relative(path), 0o555, f"candidate/{path}")
    if receipt.get("file_count") != len(files) or receipt.get("sealed_read_only") is not True:
        raise SnapshotError("receipt count/seal mismatch")
    return {
        "schema": VERIFY_SCHEMA,
        "snapshot_root": str(root),
        "manifest_sha256": _sha(manifest_bytes),
        "file_count": len(files),
        "verified": True,
    }
def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("--repo", required=True)
    create.add_argument("--output-parent", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--snapshot-root", required=True)
    return parser
def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    try:
        if args.command == "create":
            receipt = create_snapshot(Path(args.repo), Path(args.output_parent))
            snapshot_root = Path(str(receipt["snapshot_root"]))
            result = {
                "schema": CREATE_SCHEMA,
                "snapshot_root": str(snapshot_root),
                "receipt_path": str(snapshot_root / RECEIPT),
                "manifest_sha256": receipt["manifest_sha256"],
                "file_count": receipt["file_count"],
                "sealed_read_only": receipt["sealed_read_only"],
            }
        else:
            result = verify_snapshot(Path(args.snapshot_root))
    except SnapshotError as exc:
        print(f"review_snapshot: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
    print(_json(result))

if __name__ == "__main__":
    main()
