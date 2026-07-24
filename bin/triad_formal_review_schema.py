"""Canonical structured result contract for sealed formal reviews."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import sys
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import ClassVar, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationInfo,
    field_validator,
    model_validator,
)


_SHA256 = re.compile(r"[0-9a-f]{64}")
_MANIFEST_ENTRY = re.compile(r"([0-9a-f]{64})  (.+)")


class FormalFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    severity: Literal["Critical", "Major", "Minor"]
    location: str
    trigger: str
    evidence: str
    correction: str

    @field_validator("location", "trigger", "evidence", "correction")
    @classmethod
    def require_nonempty_string(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("finding strings must be non-empty")
        return value


def _canonical_packet_root(value: object) -> Path:
    try:
        raw = Path(os.fspath(value))
        resolved = raw.resolve(strict=True)
        mode = raw.lstat().st_mode
    except (OSError, RuntimeError, TypeError, ValueError):
        raise ValueError(
            "sealed_packet_root must be a canonical existing directory"
        ) from None
    if (
        not raw.is_absolute()
        or raw != resolved
        or not stat.S_ISDIR(mode)
        or raw.name != "packet"
        or not raw.parent.name.strip()
    ):
        raise ValueError(
            "sealed_packet_root must be a canonical <nonempty-review-id>/packet "
            "directory"
        )
    return resolved


def _exact_packet_relative_path(value: str) -> tuple[str, ...]:
    if not value or value.startswith("/") or "\\" in value:
        raise ValueError("finding location must use an exact packet-relative path")
    parts = tuple(value.split("/"))
    if (
        any(not part or part in {".", ".."} for part in parts)
        or "/".join(parts) != value
    ):
        raise ValueError("finding location must use an exact packet-relative path")
    return parts


def _required_open_flags(*names: str) -> int:
    flags = 0
    for name in names:
        value = getattr(os, name, None)
        if value is None:
            raise ValueError(f"packet validation requires os.{name}")
        flags |= value
    return flags


@contextmanager
def _open_regular_packet_file(
    root: Path, relative_path: str, *, label: str
) -> Iterator[tuple[int, os.stat_result]]:
    parts = _exact_packet_relative_path(relative_path)
    directory_flags = _required_open_flags(
        "O_RDONLY", "O_DIRECTORY", "O_CLOEXEC", "O_NOFOLLOW"
    )
    file_flags = _required_open_flags(
        "O_RDONLY", "O_CLOEXEC", "O_NOFOLLOW", "O_NONBLOCK"
    )
    held: list[int] = []
    try:
        root_identity = root.lstat()
        root_fd = os.open(root, directory_flags)
        held.append(root_fd)
        opened_root = os.fstat(root_fd)
        if (
            not stat.S_ISDIR(opened_root.st_mode)
            or opened_root.st_dev != root_identity.st_dev
            or opened_root.st_ino != root_identity.st_ino
        ):
            raise ValueError(f"{label} escaped the canonical packet root")

        parent_fd = root_fd
        for component in parts[:-1]:
            next_fd = os.open(component, directory_flags, dir_fd=parent_fd)
            held.append(next_fd)
            if not stat.S_ISDIR(os.fstat(next_fd).st_mode):
                raise ValueError(f"{label} must resolve to a regular packet file")
            parent_fd = next_fd

        before = os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
        leaf_fd = os.open(parts[-1], file_flags, dir_fd=parent_fd)
        held.append(leaf_fd)
        opened = os.fstat(leaf_fd)
        if (
            not stat.S_ISREG(opened.st_mode)
            or before.st_dev != opened.st_dev
            or before.st_ino != opened.st_ino
        ):
            raise ValueError(f"{label} must resolve to a regular packet file")
        yield leaf_fd, opened
    except ValueError:
        raise
    except (OSError, RuntimeError, TypeError):
        raise ValueError(f"{label} must resolve to a regular packet file") from None
    finally:
        for fd in reversed(held):
            try:
                os.close(fd)
            except OSError:
                pass


def _read_regular_packet_file(
    root: Path, relative_path: str, *, label: str
) -> bytes:
    with _open_regular_packet_file(
        root, relative_path, label=label
    ) as (leaf_fd, before):
        chunks: list[bytes] = []
        while True:
            chunk = os.read(leaf_fd, 64 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(leaf_fd)
        if _packet_file_changed(before, after):
            raise ValueError(f"{label} changed while reading")
        return b"".join(chunks)


def _packet_file_changed(
    before: os.stat_result, after: os.stat_result
) -> bool:
    stable = (
        "st_dev",
        "st_ino",
        "st_mode",
        "st_size",
        "st_mtime_ns",
        "st_ctime_ns",
    )
    return any(getattr(before, field) != getattr(after, field) for field in stable)


def _hash_regular_packet_file(
    root: Path, relative_path: str, *, label: str
) -> str:
    digest = hashlib.sha256()
    with _open_regular_packet_file(
        root, relative_path, label=label
    ) as (leaf_fd, before):
        while True:
            chunk = os.read(leaf_fd, 64 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        after = os.fstat(leaf_fd)
        if _packet_file_changed(before, after):
            raise ValueError(f"{label} changed while hashing")
    return digest.hexdigest()


def _load_input_manifest(root: Path) -> dict[str, str]:
    return _load_manifest(root, "INPUT_SHA256SUMS")


def _load_manifest(root: Path, label: str) -> dict[str, str]:
    raw = _read_regular_packet_file(root, label, label=label)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"{label} must be valid UTF-8") from None
    lines = text.splitlines()
    if not lines:
        raise ValueError(f"{label} must contain manifest entries")
    entries: dict[str, str] = {}
    for line in lines:
        match = _MANIFEST_ENTRY.fullmatch(line)
        if match is None:
            raise ValueError(f"{label} contains a malformed entry")
        digest, relative_path = match.groups()
        try:
            _exact_packet_relative_path(relative_path)
        except ValueError:
            raise ValueError(f"{label} contains an unsafe path") from None
        if relative_path in entries:
            raise ValueError(f"{label} contains a duplicate entry")
        entries[relative_path] = digest
    return entries


def _verify_manifest_entries(
    root: Path, manifest: Mapping[str, str], *, label: str
) -> None:
    for relative_path, expected_digest in manifest.items():
        digest = _hash_regular_packet_file(root, relative_path, label=label)
        if digest != expected_digest:
            raise ValueError(f"{label} digest mismatch for {relative_path!r}")


def _packet_tree_regular_files(root: Path) -> set[str]:
    directory_flags = _required_open_flags(
        "O_RDONLY", "O_DIRECTORY", "O_CLOEXEC", "O_NOFOLLOW"
    )
    file_flags = _required_open_flags(
        "O_RDONLY", "O_CLOEXEC", "O_NOFOLLOW", "O_NONBLOCK"
    )

    def same_identity(first: os.stat_result, second: os.stat_result) -> bool:
        return first.st_dev == second.st_dev and first.st_ino == second.st_ino

    def walk(directory_fd: int, parts: tuple[str, ...]) -> set[str]:
        names = sorted(os.listdir(directory_fd))
        if parts and not names:
            raise ValueError(
                "packet tree contains an unbound empty directory at "
                f"{'/'.join(parts)!r}"
            )
        files: set[str] = set()
        for name in names:
            relative_path = "/".join((*parts, name))
            try:
                _exact_packet_relative_path(relative_path)
                before = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except (OSError, RuntimeError, TypeError, ValueError):
                raise ValueError(
                    "packet tree contains an unsafe or unstable entry"
                ) from None

            if stat.S_ISDIR(before.st_mode):
                child_fd = -1
                try:
                    child_fd = os.open(name, directory_flags, dir_fd=directory_fd)
                    opened = os.fstat(child_fd)
                    if not stat.S_ISDIR(opened.st_mode) or not same_identity(
                        before, opened
                    ):
                        raise ValueError("packet tree directory identity changed")
                    files.update(walk(child_fd, (*parts, name)))
                except ValueError:
                    raise
                except (OSError, RuntimeError, TypeError):
                    raise ValueError(
                        "packet tree directory could not be opened without following links"
                    ) from None
                finally:
                    if child_fd >= 0:
                        try:
                            os.close(child_fd)
                        except OSError:
                            pass
            elif stat.S_ISREG(before.st_mode):
                child_fd = -1
                try:
                    child_fd = os.open(name, file_flags, dir_fd=directory_fd)
                    opened = os.fstat(child_fd)
                    if not stat.S_ISREG(opened.st_mode) or not same_identity(
                        before, opened
                    ):
                        raise ValueError("packet tree file identity changed")
                    files.add(relative_path)
                except ValueError:
                    raise
                except (OSError, RuntimeError, TypeError):
                    raise ValueError(
                        "packet tree file could not be opened without following links"
                    ) from None
                finally:
                    if child_fd >= 0:
                        try:
                            os.close(child_fd)
                        except OSError:
                            pass
            else:
                raise ValueError(
                    "packet tree contains a symlink or non-regular entry at "
                    f"{relative_path!r}"
                )
        return files

    root_fd = -1
    try:
        root_identity = root.lstat()
        root_fd = os.open(root, directory_flags)
        opened_root = os.fstat(root_fd)
        if (
            not stat.S_ISDIR(opened_root.st_mode)
            or not same_identity(root_identity, opened_root)
        ):
            raise ValueError("packet tree escaped the canonical packet root")
        return walk(root_fd, ())
    except ValueError:
        raise
    except (OSError, RuntimeError, TypeError):
        raise ValueError(
            "packet tree could not be inspected without following links"
        ) from None
    finally:
        if root_fd >= 0:
            try:
                os.close(root_fd)
            except OSError:
                pass


def _validate_finding_locations(
    root: Path, findings: list[FormalFinding]
) -> None:
    manifest = _load_input_manifest(root)
    held_text: dict[str, str] = {}
    for finding in findings:
        try:
            relative_path, line_text = finding.location.rsplit(":", 1)
            _exact_packet_relative_path(relative_path)
        except (ValueError, AttributeError):
            raise ValueError(
                "finding location must be an exact packet-relative path and "
                "positive line number"
            ) from None
        if not line_text.isascii() or not line_text.isdigit():
            raise ValueError("finding location must end in a positive line number")
        line_number = int(line_text)
        if line_number <= 0:
            raise ValueError("finding location must end in a positive line number")
        expected_digest = manifest.get(relative_path)
        if expected_digest is None:
            raise ValueError("finding location path is not listed in INPUT_SHA256SUMS")
        if relative_path not in held_text:
            data = _read_regular_packet_file(
                root,
                relative_path,
                label=f"finding location {relative_path!r}",
            )
            if hashlib.sha256(data).hexdigest() != expected_digest:
                raise ValueError("finding location manifest digest mismatch")
            try:
                held_text[relative_path] = data.decode("utf-8")
            except UnicodeDecodeError:
                raise ValueError("finding location packet file must be UTF-8") from None
        if line_number > len(held_text[relative_path].splitlines()):
            raise ValueError("finding location line number is out of range")


class FormalReview(BaseModel):
    """JSON-only validation and dump contract for one sealed formal review.

    Supported interchange is ``model_validate_json`` followed by
    ``model_dump(mode="json")``. The loader assigns a private module identity;
    cross-process pickling and name-based re-import are intentionally
    unsupported.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    required_validation_context: ClassVar[frozenset[str]] = frozenset(
        {"sealed_packet_root", "expected_packet_sha256"}
    )

    review_id: str
    packet_sha256: str
    verdict: Literal["SAFE", "NOT-SAFE"]
    findings: list[FormalFinding]
    open_questions: list[str]

    @classmethod
    def verify_sealed_packet(cls, context: Mapping[str, object]) -> None:
        """Verify the sealed packet bytes named by a formal validation context."""
        if frozenset(context) != cls.required_validation_context:
            raise ValueError(
                "validation context must contain exactly sealed_packet_root and "
                "expected_packet_sha256"
            )
        root = _canonical_packet_root(context["sealed_packet_root"])
        expected_hash = context["expected_packet_sha256"]
        if (
            not isinstance(expected_hash, str)
            or _SHA256.fullmatch(expected_hash) is None
        ):
            raise ValueError("expected packet SHA-256 must be 64 lowercase hex characters")

        packet_hash = _read_regular_packet_file(
            root, "PACKET_SHA256", label="PACKET_SHA256"
        )
        if packet_hash not in {expected_hash.encode("ascii"), f"{expected_hash}\n".encode("ascii")}:
            raise ValueError("PACKET_SHA256 content mismatch")

        sums_bytes = _read_regular_packet_file(root, "SHA256SUMS", label="SHA256SUMS")
        if hashlib.sha256(sums_bytes).hexdigest() != expected_hash:
            raise ValueError("SHA256SUMS digest mismatch")
        input_manifest_bytes = _read_regular_packet_file(
            root, "INPUT_SHA256SUMS", label="INPUT_SHA256SUMS"
        )
        sums_manifest = _load_manifest(root, "SHA256SUMS")
        if sums_manifest.get("INPUT_SHA256SUMS") != hashlib.sha256(
            input_manifest_bytes
        ).hexdigest():
            raise ValueError("SHA256SUMS must bind INPUT_SHA256SUMS exactly once")
        _verify_manifest_entries(
            root, sums_manifest, label="SHA256SUMS"
        )
        input_manifest = _load_input_manifest(root)
        _verify_manifest_entries(root, input_manifest, label="INPUT_SHA256SUMS")
        expected_input_manifest = {
            relative_path: digest
            for relative_path, digest in sums_manifest.items()
            if relative_path != "INPUT_SHA256SUMS"
        }
        if input_manifest != expected_input_manifest:
            raise ValueError(
                "INPUT_SHA256SUMS entries must equal SHA256SUMS payload entries"
            )
        expected_files = set(sums_manifest) | {"SHA256SUMS", "PACKET_SHA256"}
        if _packet_tree_regular_files(root) != expected_files:
            raise ValueError(
                "sealed packet tree does not exactly match SHA256SUMS"
            )

    @model_validator(mode="before")
    @classmethod
    def validate_packet_identity(
        cls, value: object, info: ValidationInfo
    ) -> object:
        if not isinstance(value, Mapping):
            return value
        context = info.context
        if (
            not isinstance(context, Mapping)
            or frozenset(context) != cls.required_validation_context
        ):
            raise ValueError(
                "validation context must contain exactly sealed_packet_root and "
                "expected_packet_sha256"
            )

        cls.verify_sealed_packet(context)
        root = _canonical_packet_root(context["sealed_packet_root"])
        expected_hash = context["expected_packet_sha256"]
        if (
            not isinstance(expected_hash, str)
            or _SHA256.fullmatch(expected_hash) is None
        ):
            raise ValueError("expected packet SHA-256 must be 64 lowercase hex characters")

        expected_review_id = root.parent.name
        if (
            value.get("packet_sha256") != expected_hash
            or value.get("review_id") != expected_review_id
        ):
            raise ValueError("formal review identity mismatch")
        return value

    @field_validator("open_questions")
    @classmethod
    def require_nonempty_questions(cls, values: list[str]) -> list[str]:
        if any(not value.strip() for value in values):
            raise ValueError("open questions must be non-empty")
        return values

    @model_validator(mode="after")
    def validate_verdict(
        self, info: ValidationInfo
    ) -> "FormalReview":
        context = info.context
        if (
            not isinstance(context, Mapping)
            or frozenset(context) != self.required_validation_context
        ):
            raise ValueError(
                "validation context must contain exactly sealed_packet_root and "
                "expected_packet_sha256"
            )
        root = _canonical_packet_root(context["sealed_packet_root"])
        _validate_finding_locations(root, self.findings)
        blocking = any(
            finding.severity in {"Critical", "Major"}
            for finding in self.findings
        )
        expected_verdict = (
            "NOT-SAFE" if blocking or self.open_questions else "SAFE"
        )
        if self.verdict != expected_verdict:
            raise ValueError(f"verdict must be {expected_verdict}")
        return self


def _read_result_file(path: Path) -> bytes:
    """Read one canonical, no-follow, single-link native-review result file."""
    try:
        resolved = path.resolve(strict=True)
        before = path.lstat()
    except (OSError, RuntimeError):
        raise ValueError("result file must be a canonical existing regular file") from None
    if (
        not path.is_absolute()
        or path != resolved
        or not stat.S_ISREG(before.st_mode)
        or before.st_nlink != 1
    ):
        raise ValueError("result file must be a canonical existing regular file")
    flags = os.O_RDONLY | _required_open_flags("O_NOFOLLOW", "O_CLOEXEC", "O_NONBLOCK")
    try:
        fd = os.open(path, flags)
    except OSError:
        raise ValueError("result file could not be opened safely") from None
    try:
        opened = os.fstat(fd)
        if not os.path.samestat(opened, before):
            raise ValueError("result file changed while opening")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after_fd = os.fstat(fd)
        after_path = path.lstat()
        identity = lambda value: (
            value.st_dev,
            value.st_ino,
            value.st_size,
            value.st_mtime_ns,
            stat.S_IMODE(value.st_mode),
        )
        if identity(opened) != identity(after_fd) or identity(opened) != identity(after_path):
            raise ValueError("result file changed while reading")
        return b"".join(chunks)
    finally:
        os.close(fd)


def validate_formal_review_file(
    result_file: Path,
    sealed_packet_root: Path,
    expected_packet_sha256: str,
) -> FormalReview:
    """Validate a native-review file with the same sealed-packet contract."""
    payload = _read_result_file(result_file)
    return FormalReview.model_validate_json(
        payload,
        context={
            "sealed_packet_root": str(sealed_packet_root),
            "expected_packet_sha256": expected_packet_sha256,
        },
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-file", type=Path, required=True)
    parser.add_argument("--sealed-packet-root", type=Path, required=True)
    parser.add_argument("--expected-packet-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        review = validate_formal_review_file(
            args.result_file,
            args.sealed_packet_root,
            args.expected_packet_sha256,
        )
    except (OSError, ValueError) as error:
        print(f"invalid FormalReview: {error}", file=sys.stderr)
        return 2
    print(review.model_dump_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
