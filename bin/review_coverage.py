#!/usr/bin/env python3
"""Validate provider batch receipts and publish full-family admission."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from review_evidence import (
    CHANGED_KINDS,
    CandidateState,
    EvidenceError,
    EvidenceSummary,
    ImpactRow,
    PatchShard,
    validate_review_evidence,
)
from triad_formal_review_schema import FormalFinding


FAMILIES = ("claude", "google", "codex")
ASCII_WHITESPACE = b" \t\r\n\f\v"
_HUNK_HEADER = re.compile(
    rb"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@(?:[^\r\n]*)$", re.M
)
_LOCATION = re.compile(r"^(.+):([1-9][0-9]*)$")


class CoverageError(ValueError):
    pass


class PathEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    path: str
    content_sha256: str
    observation_line: int | None = Field(default=None, ge=1)
    source_observation: str = ""
    line_start: int | None = Field(default=None, ge=1)
    line_end: int | None = Field(default=None, ge=1)
    symbols: tuple[str, ...]
    changed_hunks: tuple[str, ...]
    verified_impact_edges: tuple[str, ...]
    disposition: Literal["no-finding", "finding", "unresolved"]


class BatchReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    family: Literal["claude", "google", "codex"]
    batch_id: str
    source_tree_digest: str
    change_evidence_digest: str
    verdict: Literal["SAFE", "NOT-SAFE"]
    path_evidence: tuple[PathEvidence, ...]
    findings: tuple[FormalFinding, ...]
    affected_surfaces_inspected: tuple[str, ...]
    unresolved_paths: tuple[str, ...]
    open_questions: tuple[str, ...]


@dataclass(frozen=True)
class FamilyCoverage:
    family: str
    receipt_digests: tuple[str, ...]
    covered_paths: tuple[str, ...]
    consolidated_findings: tuple[FormalFinding, ...]
    unresolved_paths: tuple[str, ...]
    open_questions: tuple[str, ...]
    affected_surfaces_inspected: tuple[str, ...]
    verdict: Literal["SAFE", "NOT-SAFE"]


@dataclass(frozen=True)
class CoverageAdmission:
    format_version: int
    candidate_state: CandidateState
    source_tree_digest: str
    change_evidence_digest: str
    admitted: bool
    family_coverages: tuple[FamilyCoverage, ...]


class CandidateStateWire(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, from_attributes=True)

    base_commit: str
    head_commit: str
    worktree_fingerprint: str
    canonical_diff_sha256: str


class FamilyCoverageWire(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, from_attributes=True)

    family: Literal["claude", "google", "codex"]
    receipt_digests: tuple[str, ...]
    covered_paths: tuple[str, ...]
    consolidated_findings: tuple[FormalFinding, ...]
    unresolved_paths: tuple[str, ...]
    open_questions: tuple[str, ...]
    affected_surfaces_inspected: tuple[str, ...]
    verdict: Literal["SAFE", "NOT-SAFE"]


class CoverageAdmissionWire(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, from_attributes=True)

    format_version: int = Field(ge=1)
    candidate_state: CandidateStateWire
    source_tree_digest: str
    change_evidence_digest: str
    admitted: bool
    family_coverages: tuple[FamilyCoverageWire, ...]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _duplicate_rejector(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise CoverageError("duplicate JSON member")
        result[key] = value
    return result


def reject_duplicate_json_members(json_bytes: bytes) -> None:
    try:
        json.loads(json_bytes.decode("utf-8"), object_pairs_hook=_duplicate_rejector)
    except CoverageError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CoverageError("invalid JSON document") from exc


def _receipt_json_bytes(raw: bytes) -> bytes:
    trimmed = raw.strip(ASCII_WHITESPACE)
    if not trimmed.startswith(b"```"):
        if not trimmed.startswith(b"{"):
            raise CoverageError("invalid receipt envelope")
        return raw
    lines = trimmed.splitlines(keepends=True)
    if len(lines) < 3:
        raise CoverageError("invalid receipt envelope")
    opening = lines[0].rstrip(b"\r\n")
    closing = lines[-1].rstrip(b"\r\n")
    if opening not in {b"```", b"```json"} or closing != b"```":
        raise CoverageError("invalid receipt envelope")
    inner = b"".join(lines[1:-1])
    if inner.strip(ASCII_WHITESPACE).startswith(b"```"):
        raise CoverageError("invalid receipt envelope")
    return inner


def _safe_read(path: Path, diagnostic: str) -> bytes:
    if not path.is_absolute() or _has_symlink_component(path):
        raise CoverageError(diagnostic)
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            metadata = os.fstat(fd)
            if not stat.S_ISREG(metadata.st_mode):
                raise CoverageError(diagnostic)
            chunks: list[bytes] = []
            while True:
                chunk = os.read(fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            os.close(fd)
    except CoverageError:
        raise
    except OSError as exc:
        raise CoverageError(diagnostic) from exc


def _parse_receipt(path: Path) -> tuple[BatchReceipt, str]:
    raw = _safe_read(path, "invalid batch receipt")
    fenced = raw.strip(ASCII_WHITESPACE).startswith(b"```")
    json_bytes = _receipt_json_bytes(raw)
    try:
        reject_duplicate_json_members(json_bytes)
    except CoverageError as exc:
        if fenced and str(exc) != "duplicate JSON member":
            raise CoverageError("invalid receipt envelope") from exc
        raise
    try:
        receipt = BatchReceipt.model_validate_json(json_bytes, strict=True)
    except ValidationError as exc:
        raise CoverageError("invalid batch receipt") from exc
    return receipt, _sha256(raw)


def _source_data(evidence: EvidenceSummary, row: ImpactRow) -> tuple[bytes, str]:
    if row.change_kind == "deleted":
        if os.path.lexists(evidence.review_root / row.path):
            raise CoverageError("path content digest mismatch")
        return b"", ""
    data = _safe_read(evidence.review_root / row.path, "path content digest mismatch")
    if _sha256(data) != row.content_sha256:
        raise CoverageError("path content digest mismatch")
    try:
        return data, data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CoverageError("source observation mismatch") from exc


def _patch_ids(evidence: EvidenceSummary, path: str) -> tuple[str, ...]:
    return tuple(sorted(shard.patch_id for shard in evidence.patch_shards if shard.path == path))


def _new_hunk_lines(evidence: EvidenceSummary, path: str) -> set[int]:
    result: set[int] = set()
    for shard in evidence.patch_shards:
        if shard.path != path or shard.hunk_ordinal is None:
            continue
        artifact = (
            evidence.review_root / "change-evidence" / "patches"
            / shard.group_id / f"{shard.patch_id}.patch"
        )
        data = _safe_read(artifact, "finding artifact digest mismatch")
        if _sha256(data) != shard.sha256:
            raise CoverageError("finding artifact digest mismatch")
        matches = tuple(_HUNK_HEADER.finditer(data))
        if len(matches) != 1:
            raise CoverageError("invalid changed hunk evidence")
        start = int(matches[0].group(1))
        count = 1 if matches[0].group(2) is None else int(matches[0].group(2))
        result.update(range(start, start + count))
    return result


def _validate_path_evidence(
    evidence: EvidenceSummary,
    row: ImpactRow,
    item: PathEvidence,
) -> None:
    if item.content_sha256 != row.content_sha256:
        raise CoverageError("path content digest mismatch")
    if row.change_kind == "deleted" and item.content_sha256 != _sha256(b""):
        raise CoverageError("path content digest mismatch")
    data, text = _source_data(evidence, row)

    if row.change_kind in CHANGED_KINDS:
        if item.verified_impact_edges:
            raise CoverageError("unexpected cross-kind evidence")
        expected_hunks = _patch_ids(evidence, row.path)
        if not item.changed_hunks:
            raise CoverageError("changed path lacks hunk evidence")
        if len(set(item.changed_hunks)) != len(item.changed_hunks) or set(item.changed_hunks) != set(expected_hunks):
            raise CoverageError("changed hunk IDs do not match PATCH_INDEX")
    else:
        if item.changed_hunks:
            raise CoverageError("unexpected cross-kind evidence")
        expected_edges = () if row.impact_edge_id == "-" else (row.impact_edge_id,)
        actual = item.verified_impact_edges
        if item.disposition == "unresolved":
            if len(set(actual)) != len(actual) or not set(actual).issubset(expected_edges):
                raise CoverageError("impact edge IDs do not match closure")
        else:
            if not actual and expected_edges:
                raise CoverageError(
                    "affected path lacks impact-edge evidence; "
                    "impact edge IDs do not match closure"
                )
            if len(set(actual)) != len(actual) or set(actual) != set(expected_edges):
                raise CoverageError("impact edge IDs do not match closure")

    if row.change_kind == "deleted":
        if (
            item.observation_line is not None or item.source_observation != ""
            or item.line_start is not None or item.line_end is not None
            or item.symbols
        ):
            raise CoverageError("complete source range required")
        return
    if data == b"":
        if (
            item.line_start is not None or item.line_end is not None
            or item.observation_line is not None or item.source_observation != ""
        ):
            raise CoverageError("complete source range required")
        return
    if item.line_start != 1 or item.line_end != row.line_count:
        raise CoverageError("complete source range required")
    if not text.strip():
        if item.observation_line is not None or item.source_observation != "":
            raise CoverageError("source observation mismatch")
        return

    lines = text.splitlines()
    if item.observation_line is None or not (1 <= item.observation_line <= len(lines)):
        raise CoverageError("source observation mismatch")
    observation = item.source_observation
    line = lines[item.observation_line - 1]
    if (
        not (1 <= len(observation) <= 160)
        or observation not in line
        or not observation.strip()
        or (len(line) >= 8 and len(observation) < 8)
    ):
        raise CoverageError("source observation mismatch")
    if row.change_kind in CHANGED_KINDS:
        hunk_lines = _new_hunk_lines(evidence, row.path)
        outside_nonempty = any(
            line_value.strip() and index not in hunk_lines
            for index, line_value in enumerate(lines, 1)
        )
        if outside_nonempty and item.observation_line in hunk_lines:
            raise CoverageError("observation outside changed hunks required")


def _finding_owner(
    evidence: EvidenceSummary,
    finding: FormalFinding,
) -> str:
    match = _LOCATION.fullmatch(finding.location)
    if match is None:
        raise CoverageError("finding location mismatch")
    relative, raw_line = match.groups()
    line_number = int(raw_line)
    rows = {row.path: row for row in evidence.affected_paths}
    if relative in rows and rows[relative].change_kind != "deleted":
        row = rows[relative]
        data = _safe_read(evidence.review_root / relative, "finding location mismatch")
        if _sha256(data) != row.content_sha256:
            raise CoverageError("finding artifact digest mismatch")
        owner = relative
    else:
        shards = {
            f"change-evidence/patches/{shard.group_id}/{shard.patch_id}.patch": shard
            for shard in evidence.patch_shards
        }
        shard = shards.get(relative)
        if shard is None:
            raise CoverageError("finding location mismatch")
        data = _safe_read(evidence.review_root / relative, "finding location mismatch")
        if _sha256(data) != shard.sha256:
            raise CoverageError("finding artifact digest mismatch")
        owner = shard.path
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise CoverageError("finding location mismatch") from exc
    if line_number > len(lines):
        raise CoverageError("finding location mismatch")
    return owner


def _validate_receipt(
    evidence: EvidenceSummary,
    family: str,
    receipt: BatchReceipt,
) -> None:
    if receipt.family != family:
        raise CoverageError("receipt family mismatch")
    if (
        receipt.source_tree_digest != evidence.source_tree_digest
        or receipt.change_evidence_digest != evidence.change_evidence_digest
    ):
        raise CoverageError("evidence digest mismatch")
    expected_rows = tuple(row for row in evidence.affected_paths if row.batch_id == receipt.batch_id)
    expected_paths = tuple(row.path for row in expected_rows)
    actual_paths = tuple(item.path for item in receipt.path_evidence)
    closure_paths = {row.path for row in evidence.affected_paths}
    if any(path not in closure_paths for path in actual_paths):
        raise CoverageError("absent from closure")
    if actual_paths != expected_paths:
        if len(actual_paths) < len(expected_paths) and set(actual_paths).issubset(expected_paths):
            raise CoverageError("missing covered path")
        raise CoverageError("assigned path set mismatch")
    if receipt.affected_surfaces_inspected != expected_paths:
        raise CoverageError("assigned inspected surfaces mismatch")

    rows = {row.path: row for row in expected_rows}
    for item in receipt.path_evidence:
        _validate_path_evidence(evidence, rows[item.path], item)

    if len(set(receipt.unresolved_paths)) != len(receipt.unresolved_paths):
        raise CoverageError("disposition mismatch")
    if any(path not in rows for path in receipt.unresolved_paths):
        raise CoverageError("disposition mismatch")
    finding_paths: set[str] = set()
    for finding in receipt.findings:
        owner = _finding_owner(evidence, finding)
        if owner not in rows:
            raise CoverageError("finding belongs to another batch")
        finding_paths.add(owner)
    unresolved = set(receipt.unresolved_paths)
    for item in receipt.path_evidence:
        expected = (
            "unresolved" if item.path in unresolved
            else "finding" if item.path in finding_paths
            else "no-finding"
        )
        if item.disposition != expected:
            raise CoverageError("disposition mismatch")


def validate_family_receipts(
    evidence: EvidenceSummary,
    family: str,
    receipt_paths: Sequence[Path],
) -> FamilyCoverage:
    if family not in FAMILIES:
        raise CoverageError("receipt family mismatch")
    parsed: dict[str, tuple[BatchReceipt, str]] = {}
    for raw_path in receipt_paths:
        receipt, digest = _parse_receipt(Path(raw_path))
        if receipt.batch_id in parsed:
            raise CoverageError("duplicate batch receipt")
        parsed[receipt.batch_id] = (receipt, digest)
    missing = [batch_id for batch_id in evidence.batch_ids if batch_id not in parsed]
    if missing:
        raise CoverageError("missing batch receipt")
    if set(parsed) != set(evidence.batch_ids):
        raise CoverageError("extra batch receipt")

    receipts: list[BatchReceipt] = []
    digests: list[str] = []
    for batch_id in evidence.batch_ids:
        receipt, digest = parsed[batch_id]
        _validate_receipt(evidence, family, receipt)
        receipts.append(receipt)
        digests.append(digest)
    findings = tuple(finding for receipt in receipts for finding in receipt.findings)
    unresolved = tuple(path for receipt in receipts for path in receipt.unresolved_paths)
    questions = tuple(question for receipt in receipts for question in receipt.open_questions)
    surfaces = tuple(path for receipt in receipts for path in receipt.affected_surfaces_inspected)
    return FamilyCoverage(
        family=family,
        receipt_digests=tuple(digests),
        covered_paths=tuple(row.path for row in evidence.affected_paths),
        consolidated_findings=findings,
        unresolved_paths=unresolved,
        open_questions=questions,
        affected_surfaces_inspected=surfaces,
        verdict="NOT-SAFE" if any(receipt.verdict == "NOT-SAFE" for receipt in receipts) else "SAFE",
    )


def admit_full_coverage(
    evidence: EvidenceSummary,
    family_coverages: Sequence[FamilyCoverage],
) -> CoverageAdmission:
    by_family: dict[str, FamilyCoverage] = {}
    for coverage in family_coverages:
        if coverage.family in by_family:
            raise CoverageError("duplicate family coverage")
        by_family[coverage.family] = coverage
    if set(by_family) != set(FAMILIES):
        raise CoverageError("missing family coverage")
    expected_paths = tuple(row.path for row in evidence.affected_paths)
    ordered = tuple(by_family[family] for family in FAMILIES)
    if any(coverage.covered_paths != expected_paths for coverage in ordered):
        raise CoverageError("missing covered path")
    admitted = all(
        coverage.verdict == "SAFE"
        and not coverage.unresolved_paths
        and not coverage.open_questions
        and not any(
            finding.severity in {"Critical", "Major"}
            for finding in coverage.consolidated_findings
        )
        for coverage in ordered
    )
    return CoverageAdmission(
        format_version=evidence.format_version,
        candidate_state=evidence.candidate_state,
        source_tree_digest=evidence.source_tree_digest,
        change_evidence_digest=evidence.change_evidence_digest,
        admitted=admitted,
        family_coverages=ordered,
    )


def canonical_admission_bytes(
    admission: CoverageAdmission | CoverageAdmissionWire,
) -> bytes:
    wire = CoverageAdmissionWire.model_validate(admission, from_attributes=True)
    return json.dumps(
        wire.model_dump(mode="json"), ensure_ascii=False, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8") + b"\n"


def parse_canonical_owned_admission(json_bytes: bytes) -> CoverageAdmissionWire:
    reject_duplicate_json_members(json_bytes)
    try:
        wire = CoverageAdmissionWire.model_validate_json(json_bytes, strict=True)
    except ValidationError as exc:
        raise CoverageError("existing admission output is not owned") from exc
    if not wire.admitted or canonical_admission_bytes(wire) != json_bytes:
        raise CoverageError("existing admission output is not owned")
    return wire


def _has_symlink_component(path: Path, *, include_leaf: bool = True) -> bool:
    absolute = path.absolute()
    current = Path(absolute.parts[0])
    end = len(absolute.parts) if include_leaf else len(absolute.parts) - 1
    for part in absolute.parts[1:end]:
        current /= part
        try:
            if stat.S_ISLNK(current.lstat().st_mode):
                return True
        except FileNotFoundError:
            return False
    return False


def _repo_root(path: Path) -> Path:
    try:
        raw = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            check=True, capture_output=True,
        ).stdout.decode("utf-8").strip()
        return Path(raw)
    except (OSError, UnicodeDecodeError, subprocess.CalledProcessError) as exc:
        raise CoverageError("output path is not ignored") from exc


def _validate_output_path(output: Path, review_root: Path | None = None) -> None:
    if not output.is_absolute() or _has_symlink_component(output):
        raise CoverageError("invalid output path")
    parent = output.parent
    try:
        if not stat.S_ISDIR(parent.lstat().st_mode) or parent.resolve(strict=True) != parent:
            raise CoverageError("invalid output path")
    except OSError as exc:
        raise CoverageError("invalid output path") from exc
    if review_root is not None and (output == review_root or review_root in output.parents):
        raise CoverageError("admission output must be outside review root")
    repo = _repo_root(parent)
    try:
        subprocess.run(
            ["git", "-C", str(repo), "check-ignore", "-q", "--no-index", str(output)],
            check=True, capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CoverageError("output path is not ignored") from exc
    if output.exists():
        try:
            if not stat.S_ISREG(output.lstat().st_mode):
                raise CoverageError("invalid output path")
        except OSError as exc:
            raise CoverageError("invalid output path") from exc


def _retire_owned_output(output: Path) -> None:
    if not output.exists():
        return
    data = _safe_read(output, "existing admission output is not owned")
    try:
        parse_canonical_owned_admission(data)
    except CoverageError as exc:
        raise CoverageError("existing admission output is not owned") from exc
    os.unlink(output)


def _atomic_write(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        view = memoryview(data)
        while view:
            view = view[os.write(fd, view):]
        os.fsync(fd)
    finally:
        os.close(fd)
    try:
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _schema_bytes() -> bytes:
    return json.dumps(
        BatchReceipt.model_json_schema(), ensure_ascii=False, allow_nan=False,
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8") + b"\n"


def _receipt_paths(receipts_root: Path, evidence: EvidenceSummary) -> dict[str, list[Path]]:
    if not receipts_root.is_absolute() or _has_symlink_component(receipts_root):
        raise CoverageError("invalid receipts root")
    try:
        if not stat.S_ISDIR(receipts_root.lstat().st_mode):
            raise CoverageError("invalid receipts root")
    except OSError as exc:
        raise CoverageError("invalid receipts root") from exc
    expected = {
        f"{family}/{batch_id}.json"
        for family in FAMILIES for batch_id in evidence.batch_ids
    }
    observed: set[str] = set()
    for root, dirs, files in os.walk(receipts_root, topdown=True, followlinks=False):
        root_path = Path(root)
        for name in dirs:
            child = root_path / name
            relative = child.relative_to(receipts_root).as_posix()
            if child.is_symlink() or relative not in FAMILIES:
                raise CoverageError("invalid receipts root")
        for name in files:
            path = root_path / name
            if path.is_symlink() or not path.is_file():
                raise CoverageError("invalid receipts root")
            observed.add(path.relative_to(receipts_root).as_posix())
    if expected - observed:
        raise CoverageError("missing batch receipt")
    if observed - expected:
        raise CoverageError("extra batch receipt")
    return {
        family: [receipts_root / family / f"{batch_id}.json" for batch_id in evidence.batch_ids]
        for family in FAMILIES
    }


def _require_evidence_path(review_root: Path, evidence_dir: Path) -> None:
    expected = review_root / "change-evidence"
    if (
        not review_root.is_absolute() or not evidence_dir.is_absolute()
        or evidence_dir != expected
        or _has_symlink_component(review_root)
        or _has_symlink_component(evidence_dir)
    ):
        raise CoverageError("invalid evidence path")


def _non_admission_diagnostic(admission: CoverageAdmission) -> str:
    if any(coverage.unresolved_paths for coverage in admission.family_coverages):
        return "unresolved path"
    if any(coverage.open_questions for coverage in admission.family_coverages):
        return "open question"
    if any(coverage.verdict == "NOT-SAFE" for coverage in admission.family_coverages):
        return "NOT-SAFE receipt"
    return "blocking finding"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="review_coverage.py")
    commands = parser.add_subparsers(dest="command", required=True)
    schema = commands.add_parser("schema")
    schema.add_argument("--output", type=Path, required=True)
    admit = commands.add_parser("admit")
    admit.add_argument("--review-root", type=Path, required=True)
    admit.add_argument("--evidence-dir", type=Path, required=True)
    admit.add_argument("--receipts-root", type=Path, required=True)
    admit.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        arguments = _parser().parse_args(argv)
        output = arguments.output
        if arguments.command == "schema":
            _validate_output_path(output)
            data = _schema_bytes()
            _atomic_write(output, data)
            receipt = {"output": str(output), "sha256": _sha256(data)}
            sys.stdout.write(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n")
            return 0

        review_root = arguments.review_root
        evidence_dir = arguments.evidence_dir
        _validate_output_path(output, review_root)
        _retire_owned_output(output)
        _require_evidence_path(review_root, evidence_dir)
        evidence = validate_review_evidence(review_root, evidence_dir)
        if _safe_read(evidence.batch_receipt_contract_path, "receipt contract mismatch") != _schema_bytes():
            raise CoverageError("receipt contract mismatch")
        receipt_paths = _receipt_paths(arguments.receipts_root, evidence)
        coverages = tuple(
            validate_family_receipts(evidence, family, receipt_paths[family])
            for family in FAMILIES
        )
        admission = admit_full_coverage(evidence, coverages)
        if not admission.admitted:
            raise CoverageError(_non_admission_diagnostic(admission))
        data = canonical_admission_bytes(admission)
        _atomic_write(output, data)
        return 0
    except (CoverageError, EvidenceError, ValidationError, OSError) as exc:
        sys.stderr.write(f"review-coverage: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
