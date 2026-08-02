#!/usr/bin/env python3
"""Prepare and validate deterministic full-coverage review evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence


FORMAT_VERSION = 1
DIFF_FILE_SECTIONS_PER_GROUP = 100
IMPACT_INPUT_HEADER = (
    "path\treason\treached_from\tchange_kind\tprevious_path"
)
IMPACT_OUTPUT_HEADER = (
    "path\treason\treached_from\tchange_kind\tprevious_path\tcontent_sha256"
    "\tbyte_count\tline_count\timpact_edge_id\tbatch_id"
)
PATCH_INDEX_HEADER = (
    "patch_id\tgroup_id\tsection_ordinal\thunk_ordinal\tchange_kind"
    "\tprevious_path\tpath\tsha256\tbyte_count"
)
BATCH_HEADER = (
    "path\treason\tchange_kind\tcontent_sha256\tbyte_count\tline_count"
    "\tpatch_ids\timpact_edge_ids"
)
ALLOWED_REASONS = frozenset({
    "changed",
    "import",
    "caller",
    "implementation",
    "inheritance",
    "registration",
    "schema-consumer",
    "configuration-consumer",
    "build-consumer",
    "runtime-entrypoint",
    "lifecycle",
    "error-path",
    "owner-approved-project-edge",
    "required-test-source",
})
CHANGED_KINDS = frozenset({"modified", "added", "deleted", "renamed"})
ALL_KINDS = CHANGED_KINDS | {"affected-unchanged"}
UNSUPPORTED_SEPARATORS = frozenset(
    "\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029"
)
_HUNK_HEADER = re.compile(
    rb"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?:[^\r\n]*)\n?$"
)


class EvidenceError(ValueError):
    pass


@dataclass(frozen=True)
class ImpactRow:
    path: str
    reason: str
    reached_from: str
    change_kind: str
    previous_path: str
    content_sha256: str
    byte_count: int
    line_count: int
    impact_edge_id: str
    batch_id: str


@dataclass(frozen=True)
class PatchShard:
    patch_id: str
    group_id: str
    section_ordinal: int
    hunk_ordinal: int | None
    change_kind: str
    previous_path: str
    path: str
    sha256: str
    byte_count: int


@dataclass(frozen=True)
class CandidateState:
    base_commit: str
    head_commit: str
    worktree_fingerprint: str
    canonical_diff_sha256: str


@dataclass(frozen=True)
class EvidenceSummary:
    review_root: Path = field(compare=False)
    batch_receipt_contract_path: Path = field(compare=False)
    format_version: int
    candidate_state: CandidateState
    source_tree_digest: str
    change_evidence_digest: str
    affected_paths: tuple[ImpactRow, ...]
    patch_shards: tuple[PatchShard, ...]
    group_ids: tuple[str, ...]
    diff_file_section_count: int
    patch_file_count: int
    batch_ids: tuple[str, ...]


@dataclass(frozen=True)
class _DiffSection:
    ordinal: int
    data: bytes
    header: bytes
    hunks: tuple[bytes, ...]
    change_kind: str
    previous_path: str
    path: str


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_relative_path(raw: str) -> Path:
    candidate = Path(raw)
    if (
        candidate.is_absolute()
        or not candidate.parts
        or ".." in candidate.parts
        or raw in {"", "."}
        or "//" in raw
        or raw.startswith("./")
        or raw.endswith("/")
    ):
        raise EvidenceError(f"invalid review-relative path: {raw!r}")
    return candidate


def _fixed_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["LC_ALL"] = "C"
    env.pop("GIT_EXTERNAL_DIFF", None)
    return env


def _git(repo_root: Path, *args: str, narrow: str | None = None) -> bytes:
    argv = [
        "git",
        "-c", "core.quotepath=true",
        "-c", "diff.noprefix=false",
        "-c", "diff.mnemonicPrefix=false",
        "-c", "diff.srcPrefix=a/",
        "-c", "diff.dstPrefix=b/",
        "-C", str(repo_root),
        *args,
    ]
    try:
        return subprocess.run(
            argv,
            check=True,
            capture_output=True,
            env=_fixed_env(),
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise EvidenceError(narrow or "git candidate capture failed") from exc


def _is_symlink_component(path: Path, *, include_leaf: bool = True) -> bool:
    absolute = path.absolute()
    parts = absolute.parts
    current = Path(parts[0])
    end = len(parts) if include_leaf else len(parts) - 1
    for part in parts[1:end]:
        current /= part
        try:
            if stat.S_ISLNK(current.lstat().st_mode):
                return True
        except FileNotFoundError:
            return False
    return False


def _require_canonical_existing_dir(path: Path) -> Path:
    if not path.is_absolute() or _is_symlink_component(path):
        raise EvidenceError("invalid evidence path")
    try:
        if not stat.S_ISDIR(path.lstat().st_mode):
            raise EvidenceError("invalid evidence path")
        canonical = path.resolve(strict=True)
    except (FileNotFoundError, OSError) as exc:
        raise EvidenceError("invalid evidence path") from exc
    if canonical != path:
        raise EvidenceError("invalid evidence path")
    return canonical


def _require_absolute_file(path: Path, diagnostic: str) -> bytes:
    if not path.is_absolute() or _is_symlink_component(path):
        raise EvidenceError(diagnostic)
    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        try:
            metadata = os.fstat(fd)
            if not stat.S_ISREG(metadata.st_mode):
                raise EvidenceError(diagnostic)
            chunks: list[bytes] = []
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            os.close(fd)
    except EvidenceError:
        raise
    except (FileNotFoundError, OSError) as exc:
        raise EvidenceError(diagnostic) from exc


def _source_bytes(path: Path, diagnostic: str = "prepared source differs from candidate") -> tuple[bytes, str]:
    data = _require_absolute_file(path, diagnostic)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceError("non-UTF-8 source") from exc
    if any(separator in text for separator in UNSUPPORTED_SEPARATORS):
        raise EvidenceError("unsupported source line separator")
    return data, text


def _canonical_json_object(path: Path, diagnostic: str) -> tuple[bytes, dict[str, object]]:
    data = _require_absolute_file(path, diagnostic)
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(diagnostic) from exc
    if not isinstance(value, dict):
        raise EvidenceError(diagnostic)
    expected = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8") + b"\n"
    if data != expected:
        raise EvidenceError(diagnostic)
    return data, value


def _atomic_write(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(temporary, flags, 0o600)
    try:
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(temporary, path)


def _record_digest(records: Sequence[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for relative, data in sorted(records, key=lambda item: item[0].encode("utf-8")):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(_sha256(data).encode("ascii"))
        digest.update(b"\0")
        digest.update(str(len(data)).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _tagged_record(tag: bytes, payload: bytes) -> bytes:
    return tag + b"\0" + str(len(payload)).encode("ascii") + b"\0" + payload


def _resolve_candidate_worktree(review_root: Path) -> Path:
    canonical = _require_canonical_existing_dir(review_root)
    raw = _git(canonical, "rev-parse", "--show-toplevel")
    try:
        root = Path(raw.decode("utf-8").rstrip("\n"))
    except UnicodeDecodeError as exc:
        raise EvidenceError("git candidate capture failed") from exc
    return _require_canonical_existing_dir(root)


def _require_ignored_candidate_path(repo_root: Path, path: Path) -> None:
    if not path.is_absolute():
        raise EvidenceError("leader path is not ignored")
    _git(
        repo_root,
        "check-ignore",
        "-q",
        "--no-index",
        str(path),
        narrow="leader path is not ignored",
    )


def _canonical_worktree_fingerprint(repo_root: Path) -> str:
    head = _git(repo_root, "rev-parse", "HEAD").strip()
    status_bytes = _git(
        repo_root, "status", "--porcelain=v1", "-z", "--untracked-files=all"
    )
    staged = _git(
        repo_root,
        "diff", "--cached", "--binary", "--full-index", "--no-color",
        "--no-ext-diff", "--no-textconv", "--unified=3",
        "--diff-algorithm=myers", "--no-indent-heuristic",
        "--find-renames=50%",
    )
    unstaged = _git(
        repo_root,
        "diff", "--binary", "--full-index", "--no-color", "--no-ext-diff",
        "--no-textconv", "--unified=3", "--diff-algorithm=myers",
        "--no-indent-heuristic", "--find-renames=50%",
    )
    untracked = _git(repo_root, "ls-files", "--others", "--exclude-standard", "-z")
    records = [
        _tagged_record(b"HEAD", head),
        _tagged_record(b"STATUS", status_bytes),
        _tagged_record(b"STAGED", staged),
        _tagged_record(b"UNSTAGED", unstaged),
    ]
    for raw_path in sorted(filter(None, untracked.split(b"\0"))):
        try:
            relative = raw_path.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise EvidenceError("git candidate capture failed") from exc
        target = repo_root / relative
        try:
            mode = target.lstat().st_mode
            if stat.S_ISREG(mode):
                kind = b"file"
                data = _require_absolute_file(target, "git candidate capture failed")
            elif stat.S_ISLNK(mode):
                kind = b"symlink"
                data = os.readlink(target).encode("utf-8")
            else:
                raise EvidenceError("git candidate capture failed")
        except (OSError, UnicodeEncodeError) as exc:
            raise EvidenceError("git candidate capture failed") from exc
        payload = kind + b"\0" + raw_path + b"\0" + _sha256(data).encode("ascii")
        records.append(_tagged_record(b"UNTRACKED", payload))
    return _sha256(b"".join(records))


def _validate_base_commit(repo_root: Path, base_commit: str) -> None:
    try:
        object_format = _git(repo_root, "rev-parse", "--show-object-format").decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise EvidenceError("invalid base commit") from exc
    width = {"sha1": 40, "sha256": 64}.get(object_format)
    if width is None or re.fullmatch(rf"[0-9a-f]{{{width}}}", base_commit) is None:
        raise EvidenceError("invalid base commit")
    _git(repo_root, "cat-file", "-e", f"{base_commit}^{{commit}}", narrow="invalid base commit")
    _git(repo_root, "merge-base", "--is-ancestor", base_commit, "HEAD", narrow="invalid base commit")


def _canonical_diff(repo_root: Path, base_commit: str) -> bytes:
    return _git(
        repo_root,
        "diff",
        "--binary",
        "--full-index",
        "--no-color",
        "--no-ext-diff",
        "--no-textconv",
        "--unified=3",
        "--diff-algorithm=myers",
        "--no-indent-heuristic",
        "--find-renames=50%",
        base_commit,
        "--",
    )


def _capture_candidate_state(review_root: Path, base_commit: str) -> tuple[CandidateState, bytes]:
    repo_root = _resolve_candidate_worktree(review_root)
    _validate_base_commit(repo_root, base_commit)
    untracked = _git(repo_root, "ls-files", "--others", "--exclude-standard", "-z")
    if untracked:
        raise EvidenceError("untracked candidate state")
    head = _git(repo_root, "rev-parse", "HEAD").decode("ascii").strip()
    diff = _canonical_diff(repo_root, base_commit)
    state = CandidateState(
        base_commit=base_commit,
        head_commit=head,
        worktree_fingerprint=_canonical_worktree_fingerprint(repo_root),
        canonical_diff_sha256=_sha256(diff),
    )
    return state, diff


def _candidate_state_bytes(state: CandidateState) -> bytes:
    return json.dumps(
        {
            "base_commit": state.base_commit,
            "canonical_diff_sha256": state.canonical_diff_sha256,
            "head_commit": state.head_commit,
            "worktree_fingerprint": state.worktree_fingerprint,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii") + b"\n"


def _parse_candidate_state(data: bytes) -> CandidateState:
    try:
        value = json.loads(data.decode("ascii"))
        state = CandidateState(
            base_commit=value["base_commit"],
            head_commit=value["head_commit"],
            worktree_fingerprint=value["worktree_fingerprint"],
            canonical_diff_sha256=value["canonical_diff_sha256"],
        )
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise EvidenceError("candidate state mismatch") from exc
    if data != _candidate_state_bytes(state):
        raise EvidenceError("candidate state mismatch")
    return state


def _decode_git_path(raw: bytes) -> str:
    raw = raw.strip()
    if raw == b"/dev/null":
        return "/dev/null"
    if raw.startswith(b'"'):
        if not raw.endswith(b'"'):
            raise EvidenceError("control character in TSV field")
        payload = raw[1:-1]
        decoded = bytearray()
        index = 0
        escapes = {ord("n"): 10, ord("r"): 13, ord("t"): 9, ord("b"): 8, ord("f"): 12, ord("v"): 11, ord("\\"): 92, ord('"'): 34}
        while index < len(payload):
            byte = payload[index]
            if byte != 92:
                decoded.append(byte)
                index += 1
                continue
            index += 1
            if index >= len(payload):
                raise EvidenceError("control character in TSV field")
            escaped = payload[index]
            if 48 <= escaped <= 55:
                digits = payload[index:index + 3]
                if len(digits) != 3 or any(not 48 <= item <= 55 for item in digits):
                    raise EvidenceError("control character in TSV field")
                decoded.append(int(digits, 8))
                index += 3
            else:
                decoded.append(escapes.get(escaped, escaped))
                index += 1
        raw = bytes(decoded)
    try:
        result = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceError("non-UTF-8 source") from exc
    if any(control in result for control in "\x00\n\r\t"):
        raise EvidenceError("control character in TSV field")
    return result


def _diff_header_paths(header: bytes) -> tuple[str, str]:
    first_line = header.splitlines()[0]
    prefix = b"diff --git "
    if not first_line.startswith(prefix):
        raise EvidenceError("invalid unified hunk")
    payload = first_line[len(prefix):]
    tokens: list[bytes] = []
    index = 0
    while index < len(payload):
        while index < len(payload) and payload[index] == 32:
            index += 1
        if index == len(payload):
            break
        start = index
        if payload[index] == 34:
            index += 1
            escaped = False
            while index < len(payload):
                byte = payload[index]
                index += 1
                if escaped:
                    escaped = False
                elif byte == 92:
                    escaped = True
                elif byte == 34:
                    break
            else:
                raise EvidenceError("invalid unified hunk")
        else:
            while index < len(payload) and payload[index] != 32:
                index += 1
        tokens.append(payload[start:index])
    if len(tokens) != 2:
        raise EvidenceError("invalid unified hunk")
    old_path = _decode_git_path(tokens[0])
    new_path = _decode_git_path(tokens[1])
    if old_path.startswith("a/"):
        old_path = old_path[2:]
    if new_path.startswith("b/"):
        new_path = new_path[2:]
    return old_path, new_path


def _split_diff(diff: bytes) -> tuple[_DiffSection, ...]:
    starts = [match.start() for match in re.finditer(rb"(?m)^diff --git ", diff)]
    if not starts:
        if diff:
            raise EvidenceError("invalid unified hunk")
        return ()
    if starts[0] != 0:
        raise EvidenceError("invalid unified hunk")
    sections: list[_DiffSection] = []
    starts.append(len(diff))
    for ordinal, (start, end) in enumerate(zip(starts, starts[1:]), 1):
        data = diff[start:end]
        hunk_starts = [match.start() for match in re.finditer(rb"(?m)^@@ ", data)]
        header_end = hunk_starts[0] if hunk_starts else len(data)
        header = data[:header_end]
        old_match = re.search(rb"(?m)^--- (.+)\n", header)
        new_match = re.search(rb"(?m)^\+\+\+ (.+)\n", header)
        rename_from = re.search(rb"(?m)^rename from (.+)\n", header)
        rename_to = re.search(rb"(?m)^rename to (.+)\n", header)
        if rename_from and rename_to:
            old_path = _decode_git_path(rename_from.group(1))
            new_path = _decode_git_path(rename_to.group(1))
            kind = "renamed"
        elif old_match and new_match:
            old_path = _decode_git_path(old_match.group(1))
            new_path = _decode_git_path(new_match.group(1))
            if old_path == "/dev/null":
                kind = "added"
            elif new_path == "/dev/null":
                kind = "deleted"
            else:
                kind = "modified"
            if old_path.startswith("a/"):
                old_path = old_path[2:]
            if new_path.startswith("b/"):
                new_path = new_path[2:]
        else:
            old_path, new_path = _diff_header_paths(header)
            if re.search(rb"(?m)^new file mode ", header):
                kind = "added"
            elif re.search(rb"(?m)^deleted file mode ", header):
                kind = "deleted"
            else:
                kind = "modified"
        path = old_path if kind == "deleted" else new_path
        previous = old_path if kind in {"deleted", "renamed"} else "-"
        _safe_relative_path(path)
        if previous != "-":
            _safe_relative_path(previous)
        hunks: list[bytes] = []
        for hunk_index, hunk_start in enumerate(hunk_starts):
            hunk_end = hunk_starts[hunk_index + 1] if hunk_index + 1 < len(hunk_starts) else len(data)
            hunks.append(data[hunk_start:hunk_end])
        sections.append(_DiffSection(ordinal, data, header, tuple(hunks), kind, previous, path))
    return tuple(sections)


def _validate_hunk(hunk: bytes, source: bytes) -> None:
    lines = hunk.splitlines(keepends=True)
    if not lines:
        raise EvidenceError("invalid unified hunk")
    match = _HUNK_HEADER.fullmatch(lines[0])
    if match is None:
        raise EvidenceError("invalid unified hunk")
    old_start = int(match.group(1))
    old_count = int(match.group(2) or b"1")
    new_start = int(match.group(3))
    new_count = int(match.group(4) or b"1")
    if (old_count > 0 and old_start < 1) or (old_count == 0 and old_start < 0):
        raise EvidenceError("invalid unified hunk")
    old_seen = new_seen = 0
    new_body: list[bytes] = []
    last_marker: bytes | None = None
    for line in lines[1:]:
        if line.startswith(b"\\ No newline at end of file"):
            if line.rstrip(b"\n") != b"\\ No newline at end of file" or last_marker is None:
                raise EvidenceError("invalid unified hunk")
            if last_marker in {b" ", b"+"} and new_body[-1].endswith(b"\n"):
                new_body[-1] = new_body[-1][:-1]
            last_marker = None
            continue
        if not line or line[:1] not in {b" ", b"+", b"-"}:
            raise EvidenceError("invalid unified hunk")
        marker, body = line[:1], line[1:]
        if marker in {b" ", b"-"}:
            old_seen += 1
        if marker in {b" ", b"+"}:
            new_seen += 1
            new_body.append(body)
        last_marker = marker
    if old_seen != old_count or new_seen != new_count:
        raise EvidenceError("invalid unified hunk")
    source_lines = source.splitlines(keepends=True)
    if new_count > 0:
        if new_start < 1 or new_start + new_count - 1 > len(source_lines):
            raise EvidenceError("invalid unified hunk")
        expected = b"".join(source_lines[new_start - 1:new_start - 1 + new_count])
    else:
        if not 0 <= new_start <= len(source_lines):
            raise EvidenceError("invalid unified hunk")
        expected = b""
    if b"".join(new_body) != expected:
        raise EvidenceError("invalid unified hunk")


def _parse_impact_input(path: Path) -> list[tuple[str, str, str, str, str]]:
    data = _require_absolute_file(path, "control character in TSV field")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceError("non-UTF-8 source") from exc
    if "\x00" in text or "\r" in text or not text.endswith("\n"):
        raise EvidenceError("control character in TSV field")
    lines = text.splitlines()
    if not lines or lines[0] != IMPACT_INPUT_HEADER:
        raise EvidenceError("invalid impact header")
    if any(len(line.split("\t")) != 5 for line in lines[1:]):
        raise EvidenceError("control character in TSV field")
    result: list[tuple[str, str, str, str, str]] = []
    seen: set[str] = set()
    for line in lines[1:]:
        fields = line.split("\t")
        path_value, reason, reached_from, kind, previous = fields
        for value in (path_value, reached_from, previous):
            if any(control in value for control in "\x00\n\r\t"):
                raise EvidenceError("control character in TSV field")
        _safe_relative_path(path_value)
        if previous != "-":
            _safe_relative_path(previous)
        if path_value in seen:
            raise EvidenceError("duplicate affected path")
        seen.add(path_value)
        if reason not in ALLOWED_REASONS:
            raise EvidenceError("unsupported impact reason")
        if kind not in ALL_KINDS or ((reason == "changed") != (kind in CHANGED_KINDS)):
            raise EvidenceError("reason/change_kind mismatch")
        if kind in {"modified", "added", "affected-unchanged"} and previous != "-":
            raise EvidenceError("reason/change_kind mismatch")
        if kind == "deleted" and previous != path_value:
            raise EvidenceError("reason/change_kind mismatch")
        result.append((path_value, reason, reached_from, kind, previous))
    return sorted(result, key=lambda row: row[0].encode("utf-8"))


def _parse_impact_output(path: Path) -> tuple[ImpactRow, ...]:
    data = _require_absolute_file(path, "invalid impact closure")
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise EvidenceError("invalid impact closure") from exc
    if not lines or lines[0] != IMPACT_OUTPUT_HEADER:
        raise EvidenceError("invalid impact closure")
    rows: list[ImpactRow] = []
    seen: set[str] = set()
    for line in lines[1:]:
        fields = line.split("\t")
        if len(fields) != 10:
            raise EvidenceError("invalid impact closure")
        if fields[0] in seen:
            raise EvidenceError("duplicate affected path")
        seen.add(fields[0])
        try:
            rows.append(ImpactRow(*fields[:6], int(fields[6]), int(fields[7]), fields[8], fields[9]))
        except ValueError as exc:
            raise EvidenceError("invalid impact closure") from exc
    if [row.path for row in rows] != sorted(seen, key=lambda item: item.encode("utf-8")):
        raise EvidenceError("invalid impact closure")
    return tuple(rows)


def _boundary_bytes_and_paths(path: Path, repo_root: Path) -> tuple[bytes, tuple[str, ...], tuple[str, ...]]:
    data, value = _canonical_json_object(path, "required source boundary mismatch")
    if set(value) != {"paths", "roots"} or not isinstance(value["paths"], list) or not isinstance(value["roots"], list):
        raise EvidenceError("required source boundary mismatch")
    paths = value["paths"]
    roots = value["roots"]
    if not all(isinstance(item, str) for item in paths + roots) or not roots:
        raise EvidenceError("required source boundary mismatch")
    try:
        for item in paths + roots:
            _safe_relative_path(item)
    except EvidenceError as exc:
        raise EvidenceError("required source boundary mismatch") from exc
    sorted_paths = sorted(paths, key=lambda item: item.encode("utf-8"))
    sorted_roots = sorted(roots, key=lambda item: item.encode("utf-8"))
    if paths != sorted_paths or roots != sorted_roots or len(set(paths)) != len(paths) or len(set(roots)) != len(roots):
        raise EvidenceError("required source boundary mismatch")
    root_parts = [Path(root).parts for root in roots]
    for index, left in enumerate(root_parts):
        for right in root_parts[index + 1:]:
            if left == right[:len(left)] or right == left[:len(right)]:
                raise EvidenceError("required source boundary mismatch")
    for item in paths:
        matches = [root for root in roots if Path(item).parts[:len(Path(root).parts)] == Path(root).parts]
        if len(matches) != 1:
            raise EvidenceError("required source boundary mismatch")
    path_parts = [Path(item).parts for item in paths]
    for index, left in enumerate(path_parts):
        for right in path_parts[index + 1:]:
            if left == right[:len(left)] or right == left[:len(right)]:
                raise EvidenceError("required source boundary mismatch")
    try:
        cached = set(filter(None, _git(repo_root, "ls-files", "-z", "--cached", "--", *roots).decode("utf-8").split("\0")))
        deleted = set(filter(None, _git(repo_root, "ls-files", "-z", "--deleted", "--", *roots).decode("utf-8").split("\0")))
    except UnicodeDecodeError as exc:
        raise EvidenceError("required source boundary mismatch") from exc
    current = sorted(cached - deleted, key=lambda item: item.encode("utf-8"))
    if paths != current:
        raise EvidenceError("required source boundary mismatch")
    for item in current:
        try:
            _source_bytes(repo_root / item, "required source boundary mismatch")
        except EvidenceError as exc:
            raise EvidenceError("required source boundary mismatch") from exc
    return data, tuple(paths), tuple(roots)


def _require_boundary_rows(rows: Sequence[tuple[str, str, str, str, str]] | Sequence[ImpactRow], boundary_paths: Sequence[str], diff_paths: set[str]) -> None:
    by_path = {row.path if isinstance(row, ImpactRow) else row[0]: row for row in rows}
    boundary = set(boundary_paths)
    for path in boundary:
        if path not in by_path:
            raise EvidenceError("required source boundary mismatch")
        row = by_path[path]
        reason = row.reason if isinstance(row, ImpactRow) else row[1]
        reached = row.reached_from if isinstance(row, ImpactRow) else row[2]
        kind = row.change_kind if isinstance(row, ImpactRow) else row[3]
        if path in diff_paths:
            if reason != "changed" or kind not in CHANGED_KINDS:
                raise EvidenceError("required source boundary mismatch")
        elif (reason, reached, kind) != (
            "required-test-source",
            "owner-approved-no-exclusion-test-boundary",
            "affected-unchanged",
        ):
            raise EvidenceError("required source boundary mismatch")
    for row in rows:
        path = row.path if isinstance(row, ImpactRow) else row[0]
        reason = row.reason if isinstance(row, ImpactRow) else row[1]
        if reason == "required-test-source" and path not in boundary:
            raise EvidenceError("required source boundary mismatch")


def _require_prepared_sources_match_candidate(repo_root: Path, review_root: Path, affected_paths: Sequence[ImpactRow]) -> None:
    for row in affected_paths:
        prepared = review_root / row.path
        candidate = repo_root / row.path
        if row.change_kind == "deleted":
            if prepared.exists() or prepared.is_symlink() or candidate.exists() or candidate.is_symlink():
                raise EvidenceError("deleted path has current source")
            continue
        prepared_data, prepared_text = _source_bytes(prepared)
        candidate_data, candidate_text = _source_bytes(candidate)
        if (
            prepared_data != candidate_data
            or _sha256(prepared_data) != row.content_sha256
            or len(prepared_data) != row.byte_count
            or len(prepared_text.splitlines()) != row.line_count
            or len(candidate_text.splitlines()) != row.line_count
        ):
            raise EvidenceError("prepared source differs from candidate")


def _source_tree(review_root: Path, evidence_dir: Path, declared_paths: set[str]) -> tuple[str, dict[str, bytes]]:
    records: dict[str, bytes] = {}
    for root, dirs, files in os.walk(review_root, topdown=True, followlinks=False):
        root_path = Path(root)
        kept_dirs: list[str] = []
        for name in dirs:
            child = root_path / name
            if child == evidence_dir:
                continue
            if child.is_symlink():
                relative = child.relative_to(review_root).as_posix()
                if relative in declared_paths:
                    raise EvidenceError("prepared source differs from candidate")
                raise EvidenceError("prepared file lacks closure row")
            kept_dirs.append(name)
        dirs[:] = kept_dirs
        for name in files:
            child = root_path / name
            relative = child.relative_to(review_root).as_posix()
            if child.is_symlink():
                if relative in declared_paths:
                    raise EvidenceError("prepared source differs from candidate")
                raise EvidenceError("prepared file lacks closure row")
            data, _ = _source_bytes(child)
            records[relative] = data
    if set(records) != declared_paths:
        if set(records) - declared_paths:
            raise EvidenceError("prepared file lacks closure row")
        raise EvidenceError("prepared source differs from candidate")
    return _record_digest(list(records.items())), records


def _materialize_rows(
    raw_rows: Sequence[tuple[str, str, str, str, str]],
    review_root: Path,
    sections: Sequence[_DiffSection],
    batch_byte_limit: int,
) -> tuple[tuple[ImpactRow, ...], dict[str, list[str]], tuple[str, ...]]:
    if batch_byte_limit <= 0:
        raise EvidenceError("invalid batch byte limit")
    section_by_path = {section.path: section for section in sections}
    changed_rows = {row[0] for row in raw_rows if row[1] == "changed"}
    diff_paths = set(section_by_path)
    missing_diff = changed_rows - diff_paths
    if missing_diff:
        raise EvidenceError("changed closure row lacks diff section")
    if diff_paths - changed_rows:
        raise EvidenceError("diff target lacks changed closure row")
    provisional: list[dict[str, object]] = []
    patch_ids: dict[str, list[str]] = {}
    for path, reason, reached_from, kind, previous in raw_rows:
        section = section_by_path.get(path)
        if reason == "changed":
            assert section is not None
            if section.change_kind != kind:
                if kind == "deleted":
                    raise EvidenceError("deleted row lacks deletion diff")
                raise EvidenceError("reason/change_kind mismatch")
            if section.previous_path != previous:
                raise EvidenceError("reason/change_kind mismatch")
        if kind == "deleted":
            if (review_root / path).exists() or (review_root / path).is_symlink():
                raise EvidenceError("deleted path has current source")
            data = b""
            text = ""
        else:
            data, text = _source_bytes(review_root / path)
        edge = "-" if kind != "affected-unchanged" else "edge-" + _sha256(
            path.encode("utf-8") + b"\0" + reason.encode("utf-8") + b"\0" + reached_from.encode("utf-8")
        )
        provisional.append({
            "path": path, "reason": reason, "reached_from": reached_from,
            "change_kind": kind, "previous_path": previous,
            "content_sha256": _sha256(data), "byte_count": len(data),
            "line_count": len(text.splitlines()), "impact_edge_id": edge,
        })
        patch_ids[path] = []
    batch_ids: list[str] = []
    current: list[dict[str, object]] = []
    current_size = 0
    for item in provisional:
        size = int(item["byte_count"])
        if current and current_size + size > batch_byte_limit:
            batch_id = f"batch-{len(batch_ids) + 1:04d}"
            batch_ids.append(batch_id)
            for pending in current:
                pending["batch_id"] = batch_id
            current = []
            current_size = 0
        current.append(item)
        current_size += size
        if size > batch_byte_limit:
            batch_id = f"batch-{len(batch_ids) + 1:04d}"
            batch_ids.append(batch_id)
            item["batch_id"] = batch_id
            current = []
            current_size = 0
    if current:
        batch_id = f"batch-{len(batch_ids) + 1:04d}"
        batch_ids.append(batch_id)
        for pending in current:
            pending["batch_id"] = batch_id
    rows = tuple(ImpactRow(**item) for item in provisional)
    return rows, patch_ids, tuple(batch_ids)


def _validate_materialized_rows(
    rows: Sequence[ImpactRow], sections: Sequence[_DiffSection]
) -> None:
    section_by_path = {section.path: section for section in sections}
    changed = {row.path for row in rows if row.reason == "changed"}
    if changed - set(section_by_path):
        raise EvidenceError("changed closure row lacks diff section")
    if set(section_by_path) - changed:
        raise EvidenceError("diff target lacks changed closure row")
    for row in rows:
        if row.reason not in ALLOWED_REASONS:
            raise EvidenceError("unsupported impact reason")
        if row.change_kind not in ALL_KINDS or (
            (row.reason == "changed") != (row.change_kind in CHANGED_KINDS)
        ):
            raise EvidenceError("reason/change_kind mismatch")
        if row.change_kind in {"modified", "added", "affected-unchanged"} and row.previous_path != "-":
            raise EvidenceError("reason/change_kind mismatch")
        if row.change_kind == "deleted" and row.previous_path != row.path:
            raise EvidenceError("reason/change_kind mismatch")
        if re.fullmatch(r"batch-[0-9]{4}", row.batch_id) is None:
            raise EvidenceError("invalid batch manifest")
        expected_edge = "-"
        if row.change_kind == "affected-unchanged":
            expected_edge = "edge-" + _sha256(
                row.path.encode("utf-8")
                + b"\0"
                + row.reason.encode("utf-8")
                + b"\0"
                + row.reached_from.encode("utf-8")
            )
        if row.impact_edge_id != expected_edge:
            raise EvidenceError("invalid impact closure")
        section = section_by_path.get(row.path)
        if section is not None and (
            section.change_kind != row.change_kind
            or section.previous_path != row.previous_path
        ):
            raise EvidenceError("reason/change_kind mismatch")


def _section_shard_records(
    sections: Sequence[_DiffSection], sources: dict[str, bytes]
) -> tuple[tuple[PatchShard, bytes], ...]:
    records: list[tuple[PatchShard, bytes]] = []
    for section in sections:
        group_id = f"group-{((section.ordinal - 1) // DIFF_FILE_SECTIONS_PER_GROUP) + 1:04d}"
        units = section.hunks or (b"",)
        for hunk_ordinal, hunk in enumerate(units, 1):
            ordinal_value = hunk_ordinal if section.hunks else None
            patch_id = (
                f"patch-{section.ordinal:06d}-hunk-{hunk_ordinal:04d}"
                if section.hunks
                else f"patch-{section.ordinal:06d}-file"
            )
            if section.hunks:
                _validate_hunk(hunk, sources[section.path])
                data = section.header + hunk
            else:
                data = section.data
            records.append((PatchShard(
                patch_id, group_id, section.ordinal, ordinal_value,
                section.change_kind, section.previous_path, section.path,
                _sha256(data), len(data),
            ), data))
    return tuple(records)


def _write_patch_artifacts(output_dir: Path, sections: Sequence[_DiffSection], rows: Sequence[ImpactRow]) -> tuple[tuple[PatchShard, ...], dict[str, list[str]]]:
    sources = {row.path: b"" if row.change_kind == "deleted" else _source_bytes(output_dir.parent / row.path)[0] for row in rows}
    by_path: dict[str, list[str]] = {row.path: [] for row in rows}
    shards: list[PatchShard] = []
    for shard, data in _section_shard_records(sections, sources):
        directory = output_dir / "patches" / shard.group_id
        directory.mkdir(parents=True, exist_ok=True)
        _atomic_write(directory / f"{shard.patch_id}.patch", data)
        shards.append(shard)
        by_path[shard.path].append(shard.patch_id)
    return tuple(shards), by_path


def _impact_bytes(rows: Sequence[ImpactRow]) -> bytes:
    lines = [IMPACT_OUTPUT_HEADER]
    for row in rows:
        lines.append("\t".join((
            row.path, row.reason, row.reached_from, row.change_kind,
            row.previous_path, row.content_sha256, str(row.byte_count),
            str(row.line_count), row.impact_edge_id, row.batch_id,
        )))
    return ("\n".join(lines) + "\n").encode("utf-8")


def _patch_index_bytes(shards: Sequence[PatchShard]) -> bytes:
    lines = [PATCH_INDEX_HEADER]
    for shard in shards:
        lines.append("\t".join((
            shard.patch_id, shard.group_id, str(shard.section_ordinal),
            "-" if shard.hunk_ordinal is None else str(shard.hunk_ordinal),
            shard.change_kind, shard.previous_path, shard.path, shard.sha256,
            str(shard.byte_count),
        )))
    return ("\n".join(lines) + "\n").encode("utf-8")


def _batch_bytes(rows: Sequence[ImpactRow], patch_ids: dict[str, list[str]], batch_id: str) -> bytes:
    lines = [BATCH_HEADER]
    for row in rows:
        if row.batch_id != batch_id:
            continue
        ids = sorted(patch_ids[row.path])
        edges = [] if row.impact_edge_id == "-" else [row.impact_edge_id]
        lines.append("\t".join((
            row.path, row.reason, row.change_kind, row.content_sha256,
            str(row.byte_count), str(row.line_count),
            ",".join(ids) if ids else "-", ",".join(edges) if edges else "-",
        )))
    return ("\n".join(lines) + "\n").encode("utf-8")


def _changeset_bytes(
    *,
    group_count: int,
    section_count: int,
    patch_count: int,
    affected_count: int,
    batch_count: int,
    source_tree_digest: str,
    change_evidence_digest: str,
) -> bytes:
    return (
        f"FORMAT_VERSION={FORMAT_VERSION}\n"
        f"GROUP_COUNT={group_count}\n"
        f"DIFF_FILE_SECTION_COUNT={section_count}\n"
        f"PATCH_FILE_COUNT={patch_count}\n"
        f"AFFECTED_SOURCE_COUNT={affected_count}\n"
        f"BATCH_COUNT={batch_count}\n"
        f"SOURCE_TREE_DIGEST={source_tree_digest}\n"
        f"CHANGE_EVIDENCE_DIGEST={change_evidence_digest}\n"
    ).encode("ascii")


def _manifest_bytes(evidence_dir: Path) -> bytes:
    entries: list[tuple[str, bytes]] = []
    for path in evidence_dir.rglob("*"):
        if path.is_file() and not path.is_symlink() and path.name != "MANIFEST.sha256":
            entries.append((path.relative_to(evidence_dir).as_posix(), path.read_bytes()))
    return b"".join(
        f"{_sha256(data)}  {relative}\n".encode("utf-8")
        for relative, data in sorted(entries, key=lambda item: item[0].encode("utf-8"))
    )


def _change_evidence_records(evidence_dir: Path) -> list[tuple[str, bytes]]:
    names = {
        "CANDIDATE_STATE.json", "REQUIRED_SOURCE_BOUNDARY.json",
        "BATCH_RECEIPT.schema.json", "IMPACT_CLOSURE.tsv", "PATCH_INDEX.tsv",
    }
    records: list[tuple[str, bytes]] = []
    for path in evidence_dir.rglob("*"):
        relative = path.relative_to(evidence_dir).as_posix()
        if path.is_file() and not path.is_symlink() and (
            relative in names or relative.startswith("patches/") or relative.startswith("batches/")
        ):
            records.append((relative, path.read_bytes()))
    return records


def _canonical_output(review_root: Path, output_dir: Path, *, preparing: bool) -> tuple[Path, Path]:
    review_root = _require_canonical_existing_dir(review_root)
    expected = review_root / "change-evidence"
    if not output_dir.is_absolute() or output_dir.absolute() != expected:
        raise EvidenceError("invalid evidence path")
    if preparing:
        if os.path.lexists(output_dir):
            raise EvidenceError("evidence directory exists")
        if _is_symlink_component(output_dir, include_leaf=False):
            raise EvidenceError("invalid evidence path")
    else:
        output_dir = _require_canonical_existing_dir(output_dir)
        if output_dir != expected:
            raise EvidenceError("invalid evidence path")
    return review_root, output_dir


def prepare_review_evidence(
    review_root: Path,
    diff_file: Path,
    impact_input: Path,
    required_source_boundary: Path,
    receipt_contract: Path,
    output_dir: Path,
    *,
    base_commit: str,
    batch_byte_limit: int,
) -> EvidenceSummary:
    review_root, output_dir = _canonical_output(Path(review_root), Path(output_dir), preparing=True)
    repo_root = _resolve_candidate_worktree(review_root)
    for leader_path in (review_root, Path(diff_file), Path(impact_input), Path(required_source_boundary), Path(receipt_contract), output_dir):
        _require_ignored_candidate_path(repo_root, leader_path)
    state_before, canonical_diff = _capture_candidate_state(review_root, base_commit)
    supplied_diff = _require_absolute_file(Path(diff_file), "candidate diff mismatch")
    if supplied_diff != canonical_diff:
        raise EvidenceError("candidate diff mismatch")
    sections = _split_diff(canonical_diff)
    raw_rows = _parse_impact_input(Path(impact_input))
    boundary_bytes, boundary_paths, _ = _boundary_bytes_and_paths(Path(required_source_boundary), repo_root)
    receipt_bytes, _ = _canonical_json_object(Path(receipt_contract), "invalid receipt contract")
    _require_boundary_rows(raw_rows, boundary_paths, {section.path for section in sections})
    rows, _, batch_ids = _materialize_rows(raw_rows, review_root, sections, batch_byte_limit)
    _require_prepared_sources_match_candidate(repo_root, review_root, rows)
    declared = {row.path for row in rows if row.change_kind != "deleted"}
    source_tree_digest, _ = _source_tree(review_root, output_dir, declared)

    output_dir.mkdir(mode=0o700)
    _atomic_write(output_dir / "CANDIDATE_STATE.json", _candidate_state_bytes(state_before))
    _atomic_write(output_dir / "REQUIRED_SOURCE_BOUNDARY.json", boundary_bytes)
    _atomic_write(output_dir / "BATCH_RECEIPT.schema.json", receipt_bytes)
    shards, patch_ids = _write_patch_artifacts(output_dir, sections, rows)
    _atomic_write(output_dir / "PATCH_INDEX.tsv", _patch_index_bytes(shards))
    _atomic_write(output_dir / "IMPACT_CLOSURE.tsv", _impact_bytes(rows))
    batches_dir = output_dir / "batches"
    batches_dir.mkdir()
    for batch_id in batch_ids:
        _atomic_write(batches_dir / f"{batch_id}.tsv", _batch_bytes(rows, patch_ids, batch_id))
    change_evidence_digest = _record_digest(_change_evidence_records(output_dir))
    group_ids = tuple(dict.fromkeys(shard.group_id for shard in shards))
    changeset = _changeset_bytes(
        group_count=len(group_ids),
        section_count=len(sections),
        patch_count=len(shards),
        affected_count=len(rows),
        batch_count=len(batch_ids),
        source_tree_digest=source_tree_digest,
        change_evidence_digest=change_evidence_digest,
    )
    _atomic_write(output_dir / "CHANGESET.md", changeset)
    state_after, diff_after = _capture_candidate_state(review_root, base_commit)
    if state_after != state_before or diff_after != canonical_diff:
        raise EvidenceError("candidate state mismatch")
    _atomic_write(output_dir / "MANIFEST.sha256", _manifest_bytes(output_dir))
    return validate_review_evidence(review_root, output_dir)


def _changeset_headers(path: Path) -> dict[str, str]:
    data = _require_absolute_file(path, "missing CHANGESET header")
    try:
        lines = data.decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        raise EvidenceError("missing CHANGESET header") from exc
    result: dict[str, str] = {}
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = value
    required = {
        "FORMAT_VERSION", "GROUP_COUNT", "DIFF_FILE_SECTION_COUNT",
        "PATCH_FILE_COUNT", "AFFECTED_SOURCE_COUNT", "BATCH_COUNT",
        "SOURCE_TREE_DIGEST", "CHANGE_EVIDENCE_DIGEST",
    }
    if set(result) != required:
        raise EvidenceError("missing CHANGESET header")
    return result


def _parse_patch_index(path: Path, evidence_dir: Path) -> tuple[PatchShard, ...]:
    try:
        lines = _require_absolute_file(path, "invalid patch index").decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise EvidenceError("invalid patch index") from exc
    if not lines or lines[0] != PATCH_INDEX_HEADER:
        raise EvidenceError("invalid patch index")
    shards: list[PatchShard] = []
    for line in lines[1:]:
        fields = line.split("\t")
        if len(fields) != 9:
            raise EvidenceError("invalid patch index")
        try:
            shard = PatchShard(
                fields[0], fields[1], int(fields[2]), None if fields[3] == "-" else int(fields[3]),
                fields[4], fields[5], fields[6], fields[7], int(fields[8]),
            )
        except ValueError as exc:
            raise EvidenceError("invalid patch index") from exc
        artifact = evidence_dir / "patches" / shard.group_id / f"{shard.patch_id}.patch"
        data = _require_absolute_file(artifact, "invalid patch index")
        if _sha256(data) != shard.sha256 or len(data) != shard.byte_count:
            raise EvidenceError("invalid patch index")
        shards.append(shard)
    return tuple(shards)


def _evidence_files(evidence_dir: Path) -> set[str]:
    result: set[str] = set()
    for root, dirs, files in os.walk(evidence_dir, topdown=True, followlinks=False):
        root_path = Path(root)
        for name in dirs:
            if (root_path / name).is_symlink():
                raise EvidenceError("manifest mismatch")
        for name in files:
            path = root_path / name
            if path.is_symlink():
                raise EvidenceError("manifest mismatch")
            result.add(path.relative_to(evidence_dir).as_posix())
    return result


def validate_review_evidence(review_root: Path, evidence_dir: Path) -> EvidenceSummary:
    review_root, evidence_dir = _canonical_output(Path(review_root), Path(evidence_dir), preparing=False)
    headers = _changeset_headers(evidence_dir / "CHANGESET.md")
    rows = _parse_impact_output(evidence_dir / "IMPACT_CLOSURE.tsv")
    declared = {row.path for row in rows if row.change_kind != "deleted"}
    source_tree_digest, _ = _source_tree(review_root, evidence_dir, declared)
    if source_tree_digest != headers["SOURCE_TREE_DIGEST"]:
        raise EvidenceError("source digest mismatch")
    state_data = _require_absolute_file(evidence_dir / "CANDIDATE_STATE.json", "candidate state mismatch")
    persisted_state = _parse_candidate_state(state_data)
    repo_root = _resolve_candidate_worktree(review_root)
    _require_prepared_sources_match_candidate(repo_root, review_root, rows)
    try:
        current_state, canonical_diff = _capture_candidate_state(
            review_root, persisted_state.base_commit
        )
    except EvidenceError as exc:
        raise EvidenceError("candidate state mismatch") from exc
    if current_state != persisted_state or current_state.canonical_diff_sha256 != _sha256(canonical_diff):
        raise EvidenceError("candidate state mismatch")
    boundary_bytes, boundary_paths, _ = _boundary_bytes_and_paths(evidence_dir / "REQUIRED_SOURCE_BOUNDARY.json", repo_root)
    if boundary_bytes != (evidence_dir / "REQUIRED_SOURCE_BOUNDARY.json").read_bytes():
        raise EvidenceError("required source boundary mismatch")
    sections = _split_diff(canonical_diff)
    _validate_materialized_rows(rows, sections)
    _require_boundary_rows(rows, boundary_paths, {section.path for section in sections})
    _canonical_json_object(evidence_dir / "BATCH_RECEIPT.schema.json", "invalid receipt contract")
    change_digest = _record_digest(_change_evidence_records(evidence_dir))
    if change_digest != headers["CHANGE_EVIDENCE_DIGEST"]:
        raise EvidenceError("change evidence digest mismatch")
    expected_manifest = _manifest_bytes(evidence_dir)
    manifest = _require_absolute_file(evidence_dir / "MANIFEST.sha256", "manifest mismatch")
    if manifest != expected_manifest:
        raise EvidenceError("manifest mismatch")
    shards = _parse_patch_index(evidence_dir / "PATCH_INDEX.tsv", evidence_dir)
    sources = {
        row.path: b"" if row.change_kind == "deleted" else _source_bytes(review_root / row.path)[0]
        for row in rows
    }
    expected_records = _section_shard_records(sections, sources)
    expected_shards = tuple(shard for shard, _ in expected_records)
    if shards != expected_shards:
        raise EvidenceError("invalid patch index")
    patch_ids: dict[str, list[str]] = {row.path: [] for row in rows}
    for shard, expected_data in expected_records:
        artifact = evidence_dir / "patches" / shard.group_id / f"{shard.patch_id}.patch"
        if _require_absolute_file(artifact, "invalid patch index") != expected_data:
            raise EvidenceError("invalid patch index")
        patch_ids[shard.path].append(shard.patch_id)
    try:
        format_version = int(headers["FORMAT_VERSION"])
        section_count = int(headers["DIFF_FILE_SECTION_COUNT"])
        patch_count = int(headers["PATCH_FILE_COUNT"])
        affected_count = int(headers["AFFECTED_SOURCE_COUNT"])
        batch_count = int(headers["BATCH_COUNT"])
    except ValueError as exc:
        raise EvidenceError("missing CHANGESET header") from exc
    if format_version != FORMAT_VERSION or section_count != len(sections) or patch_count != len(shards) or affected_count != len(rows):
        raise EvidenceError("missing CHANGESET header")
    observed_batch_ids = sorted(
        {row.batch_id for row in rows}, key=lambda item: item.encode("utf-8")
    )
    batch_ids = tuple(f"batch-{index:04d}" for index in range(1, batch_count + 1))
    if observed_batch_ids != list(batch_ids):
        raise EvidenceError("invalid batch manifest")
    for batch_id in batch_ids:
        actual_batch = _require_absolute_file(
            evidence_dir / "batches" / f"{batch_id}.tsv",
            "invalid batch manifest",
        )
        if actual_batch != _batch_bytes(rows, patch_ids, batch_id):
            raise EvidenceError("invalid batch manifest")
    group_ids = tuple(dict.fromkeys(shard.group_id for shard in shards))
    if int(headers["GROUP_COUNT"]) != len(group_ids):
        raise EvidenceError("missing CHANGESET header")
    expected_changeset = _changeset_bytes(
        group_count=len(group_ids),
        section_count=len(sections),
        patch_count=len(shards),
        affected_count=len(rows),
        batch_count=len(batch_ids),
        source_tree_digest=source_tree_digest,
        change_evidence_digest=change_digest,
    )
    if _require_absolute_file(evidence_dir / "CHANGESET.md", "missing CHANGESET header") != expected_changeset:
        raise EvidenceError("missing CHANGESET header")
    expected_files = {
        "CANDIDATE_STATE.json",
        "REQUIRED_SOURCE_BOUNDARY.json",
        "BATCH_RECEIPT.schema.json",
        "CHANGESET.md",
        "IMPACT_CLOSURE.tsv",
        "PATCH_INDEX.tsv",
        "MANIFEST.sha256",
        *(f"batches/{batch_id}.tsv" for batch_id in batch_ids),
        *(f"patches/{shard.group_id}/{shard.patch_id}.patch" for shard in shards),
    }
    if _evidence_files(evidence_dir) != expected_files:
        raise EvidenceError("manifest mismatch")
    return EvidenceSummary(
        review_root=review_root,
        batch_receipt_contract_path=evidence_dir / "BATCH_RECEIPT.schema.json",
        format_version=format_version,
        candidate_state=persisted_state,
        source_tree_digest=source_tree_digest,
        change_evidence_digest=change_digest,
        affected_paths=rows,
        patch_shards=shards,
        group_ids=group_ids,
        diff_file_section_count=section_count,
        patch_file_count=patch_count,
        batch_ids=batch_ids,
    )


def _summary_json(summary: EvidenceSummary) -> bytes:
    state = summary.candidate_state
    value = {
        "affected_source_count": len(summary.affected_paths),
        "base_commit": state.base_commit,
        "batch_ids": list(summary.batch_ids),
        "batch_receipt_contract_path": str(summary.batch_receipt_contract_path),
        "canonical_diff_sha256": state.canonical_diff_sha256,
        "change_evidence_digest": summary.change_evidence_digest,
        "format_version": summary.format_version,
        "head_commit": state.head_commit,
        "patch_file_count": summary.patch_file_count,
        "source_tree_digest": summary.source_tree_digest,
        "worktree_fingerprint": state.worktree_fingerprint,
    }
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise EvidenceError(message)


def _absolute(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise argparse.ArgumentTypeError("path must be absolute")
    return path


def _argument_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="review-evidence", add_help=True)
    subcommands = parser.add_subparsers(
        dest="command", required=True, parser_class=_Parser
    )
    prepare = subcommands.add_parser("prepare")
    prepare.add_argument("--review-root", required=True, type=_absolute)
    prepare.add_argument("--base-commit", required=True)
    prepare.add_argument("--diff-file", required=True, type=_absolute)
    prepare.add_argument("--impact-input", required=True, type=_absolute)
    prepare.add_argument("--required-source-boundary", required=True, type=_absolute)
    prepare.add_argument("--receipt-contract", required=True, type=_absolute)
    prepare.add_argument("--output-dir", required=True, type=_absolute)
    prepare.add_argument("--batch-byte-limit", required=True, type=int)
    validate = subcommands.add_parser("validate")
    validate.add_argument("--review-root", required=True, type=_absolute)
    validate.add_argument("--evidence-dir", required=True, type=_absolute)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        arguments = _argument_parser().parse_args(argv)
        if arguments.command == "prepare":
            summary = prepare_review_evidence(
                arguments.review_root,
                arguments.diff_file,
                arguments.impact_input,
                arguments.required_source_boundary,
                arguments.receipt_contract,
                arguments.output_dir,
                base_commit=arguments.base_commit,
                batch_byte_limit=arguments.batch_byte_limit,
            )
        else:
            summary = validate_review_evidence(arguments.review_root, arguments.evidence_dir)
    except (EvidenceError, argparse.ArgumentTypeError) as exc:
        print(f"review-evidence: {exc}", file=sys.stderr)
        return 2
    sys.stdout.buffer.write(_summary_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
