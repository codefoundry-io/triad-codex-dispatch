from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))

import review_coverage
import review_evidence


FAMILIES = ("claude", "google", "codex")


def _git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        [
            "git",
            "-c", "diff.noprefix=false",
            "-c", "diff.mnemonicPrefix=false",
            "-c", "diff.srcPrefix=a/",
            "-c", "diff.dstPrefix=b/",
            "-C", str(repo),
            *args,
        ],
        check=True,
        capture_output=True,
    ).stdout


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8") + b"\n"


def _make_evidence(
    tmp_path: Path,
    *,
    changed_old: bytes | None = None,
    changed_new: bytes | None = None,
    include_deleted: bool = False,
    batch_byte_limit: int = 262144,
) -> review_evidence.EvidenceSummary:
    if changed_old is None:
        changed_old = b"".join(
            f"line {index:02d} original content\n".encode() for index in range(1, 16)
        )
    if changed_new is None:
        changed_new = changed_old.replace(
            b"line 02 original content", b"line 02 changed content"
        )
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    _git(repo, "config", "user.name", "TRIAD Test")
    _git(repo, "config", "user.email", "triad-test@example.invalid")
    (repo / ".gitignore").write_text("_runs/\n", encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src/main.py").write_bytes(changed_old)
    (repo / "tests").mkdir()
    (repo / "tests/contract.py").write_text(
        "def contract_value():\n    return 'stable contract value'\n",
        encoding="utf-8",
    )
    if include_deleted:
        (repo / "src/deleted.py").write_text(
            "def removed():\n    return 'gone'\n", encoding="utf-8"
        )
    _git(repo, "add", ".gitignore", "src", "tests")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD").decode().strip()
    (repo / "src/main.py").write_bytes(changed_new)
    if include_deleted:
        (repo / "src/deleted.py").unlink()

    run_root = repo / "_runs" / "reviews" / "round"
    review_root = run_root / "prepared"
    for relative in ("src/main.py", "tests/contract.py"):
        target = review_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((repo / relative).read_bytes())
    diff_file = run_root / "candidate.diff"
    diff_file.parent.mkdir(parents=True, exist_ok=True)
    diff_file.write_bytes(
        _git(
            repo, "diff", "--binary", "--full-index", "--no-color",
            "--no-ext-diff", "--no-textconv", "--unified=3",
            "--diff-algorithm=myers", "--no-indent-heuristic",
            "--find-renames=50%", base, "--",
        )
    )
    impact = run_root / "impact.tsv"
    rows = ["src/main.py\tchanged\t-\tmodified\t-"]
    if include_deleted:
        rows.append("src/deleted.py\tchanged\t-\tdeleted\tsrc/deleted.py")
    rows.append(
        "tests/contract.py\trequired-test-source\t"
        "owner-approved-no-exclusion-test-boundary\taffected-unchanged\t-"
    )
    impact.write_text(
        "path\treason\treached_from\tchange_kind\tprevious_path\n"
        + "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    boundary = run_root / "required-source-boundary.json"
    boundary.write_bytes(
        _canonical({"paths": ["tests/contract.py"], "roots": ["tests"]})
    )
    contract = run_root / "BATCH_RECEIPT.schema.json"
    contract.write_bytes(_canonical(review_coverage.BatchReceipt.model_json_schema()))
    return review_evidence.prepare_review_evidence(
        review_root=review_root,
        diff_file=diff_file,
        impact_input=impact,
        required_source_boundary=boundary,
        receipt_contract=contract,
        output_dir=review_root / "change-evidence",
        base_commit=base,
        batch_byte_limit=batch_byte_limit,
    )


def test_evidence_fixture_ignores_ambient_diff_prefix_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ambient = (
        ("diff.noprefix", "true"),
        ("diff.mnemonicPrefix", "true"),
        ("diff.srcPrefix", "evil/"),
        ("diff.dstPrefix", "hostile/"),
    )
    monkeypatch.setenv("GIT_CONFIG_COUNT", str(len(ambient)))
    for index, (key, value) in enumerate(ambient):
        monkeypatch.setenv(f"GIT_CONFIG_KEY_{index}", key)
        monkeypatch.setenv(f"GIT_CONFIG_VALUE_{index}", value)

    summary = _make_evidence(tmp_path)
    review_root = tmp_path / "repo" / "_runs" / "reviews" / "round" / "prepared"
    evidence_root = review_root / "change-evidence"
    shard = next((evidence_root / "patches").rglob("*.patch"))
    assert b"diff --git a/src/main.py b/src/main.py" in shard.read_bytes()
    assert review_evidence.validate_review_evidence(review_root, evidence_root) == summary


def _hunk_lines(evidence: review_evidence.EvidenceSummary, path: str) -> set[int]:
    import re

    covered: set[int] = set()
    for shard in evidence.patch_shards:
        if shard.path != path or shard.hunk_ordinal is None:
            continue
        artifact = (
            evidence.review_root / "change-evidence" / "patches"
            / shard.group_id / f"{shard.patch_id}.patch"
        )
        match = re.search(rb"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", artifact.read_bytes(), re.M)
        assert match
        start = int(match.group(1))
        count = 1 if match.group(2) is None else int(match.group(2))
        covered.update(range(start, start + count))
    return covered


def _valid_observation(
    evidence: review_evidence.EvidenceSummary,
    row: review_evidence.ImpactRow,
) -> tuple[int | None, str, int | None, int | None]:
    if row.change_kind == "deleted":
        return None, "", None, None
    data = (evidence.review_root / row.path).read_bytes()
    if data == b"":
        return None, "", None, None
    text = data.decode("utf-8")
    if not text.strip():
        return None, "", 1, row.line_count
    lines = text.splitlines()
    excluded = _hunk_lines(evidence, row.path) if row.change_kind != "affected-unchanged" else set()
    candidates = [
        (index, line) for index, line in enumerate(lines, 1)
        if line.strip() and index not in excluded
    ] or [(index, line) for index, line in enumerate(lines, 1) if line.strip()]
    line_number, line = candidates[0]
    observation = line[:160]
    if len(observation) < 8:
        observation = line
    return line_number, observation, 1, row.line_count


def _receipt_documents(
    evidence: review_evidence.EvidenceSummary, family: str
) -> dict[str, dict[str, object]]:
    documents: dict[str, dict[str, object]] = {}
    for batch_id in evidence.batch_ids:
        rows = [row for row in evidence.affected_paths if row.batch_id == batch_id]
        path_evidence = []
        for row in rows:
            observation_line, observation, line_start, line_end = _valid_observation(
                evidence, row
            )
            path_evidence.append({
                "path": row.path,
                "content_sha256": row.content_sha256,
                "observation_line": observation_line,
                "source_observation": observation,
                "line_start": line_start,
                "line_end": line_end,
                "symbols": [],
                "changed_hunks": sorted(
                    shard.patch_id for shard in evidence.patch_shards
                    if shard.path == row.path
                ),
                "verified_impact_edges": (
                    [] if row.impact_edge_id == "-" else [row.impact_edge_id]
                ),
                "disposition": "no-finding",
            })
        documents[batch_id] = {
            "family": family,
            "batch_id": batch_id,
            "source_tree_digest": evidence.source_tree_digest,
            "change_evidence_digest": evidence.change_evidence_digest,
            "verdict": "SAFE",
            "path_evidence": path_evidence,
            "findings": [],
            "affected_surfaces_inspected": [row.path for row in rows],
            "unresolved_paths": [],
            "open_questions": [],
        }
    return documents


def _write_documents(
    tmp_path: Path,
    family: str,
    documents: dict[str, dict[str, object]],
    *,
    envelope: bool = False,
) -> list[Path]:
    directory = tmp_path / "receipts" / family
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for batch_id, document in documents.items():
        path = directory / f"{batch_id}.json"
        data = _canonical(document)
        if envelope:
            data = b"```json\n" + data + b"```\n"
        path.write_bytes(data)
        paths.append(path)
    return paths


@pytest.fixture
def evidence_fixture(tmp_path: Path):
    evidence = _make_evidence(tmp_path)

    def factory(family: str, **changes: object) -> list[Path]:
        documents = _receipt_documents(evidence, family)
        first = documents[evidence.batch_ids[0]]["path_evidence"][0]
        assert isinstance(first, dict)
        extra_path = changes.pop("extra_path", None)
        if extra_path is not None:
            extra = deepcopy(first)
            extra["path"] = extra_path
            documents[evidence.batch_ids[0]]["path_evidence"].append(extra)
            documents[evidence.batch_ids[0]]["affected_surfaces_inspected"].append(extra_path)
        first.update(changes)
        return _write_documents(tmp_path, family, documents)

    return evidence, factory


def _all_coverages(evidence, tmp_path: Path, mutate=None):
    result = []
    for family in FAMILIES:
        documents = _receipt_documents(evidence, family)
        if mutate is not None:
            mutate(family, documents)
        result.append(review_coverage.validate_family_receipts(
            evidence, family, _write_documents(tmp_path, family, documents)
        ))
    return result


def _finding(location: str, severity: str = "Minor") -> dict[str, str]:
    return {
        "severity": severity,
        "location": location,
        "trigger": "A concrete trigger",
        "evidence": "Grounded evidence",
        "correction": "Bounded correction",
    }


def test_admission_requires_every_path_from_every_family(evidence_fixture) -> None:
    evidence, receipt_factory = evidence_fixture
    coverages = [
        review_coverage.validate_family_receipts(
            evidence, family, receipt_factory(family)
        )
        for family in FAMILIES
    ]
    admission = review_coverage.admit_full_coverage(evidence, coverages)
    assert admission.admitted is True


def test_manifest_path_echo_without_source_grounding_is_rejected(evidence_fixture) -> None:
    evidence, receipt_factory = evidence_fixture
    receipts = receipt_factory(
        "claude", observation_line=1, source_observation="forged observation",
        symbols=(), line_start=1, line_end=evidence.affected_paths[0].line_count,
    )
    with pytest.raises(review_coverage.CoverageError, match="source observation mismatch"):
        review_coverage.validate_family_receipts(evidence, "claude", receipts)


def test_new_affected_path_invalidates_the_round(evidence_fixture) -> None:
    evidence, receipt_factory = evidence_fixture
    receipts = receipt_factory("claude", extra_path="src/new_consumer.py")
    with pytest.raises(review_coverage.CoverageError, match="absent from closure"):
        review_coverage.validate_family_receipts(evidence, "claude", receipts)


def test_missing_batch_is_rejected(evidence_fixture) -> None:
    evidence, factory = evidence_fixture
    with pytest.raises(review_coverage.CoverageError, match="missing batch receipt"):
        review_coverage.validate_family_receipts(evidence, "claude", factory("claude")[:-1])


def test_duplicate_batch_receipt_is_rejected(evidence_fixture) -> None:
    evidence, factory = evidence_fixture
    paths = factory("claude")
    with pytest.raises(review_coverage.CoverageError, match="duplicate batch receipt"):
        review_coverage.validate_family_receipts(evidence, "claude", paths + paths[:1])


def test_receipt_digest_mismatch_is_rejected(evidence_fixture) -> None:
    evidence, _ = evidence_fixture
    documents = _receipt_documents(evidence, "claude")
    documents[evidence.batch_ids[0]]["source_tree_digest"] = "0" * 64
    with pytest.raises(review_coverage.CoverageError, match="evidence digest mismatch"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(
                evidence.review_root.parents[4], "claude", documents
            )
        )


def test_path_content_digest_must_match_closure(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    documents = _receipt_documents(evidence, "claude")
    documents[evidence.batch_ids[0]]["path_evidence"][0]["content_sha256"] = "0" * 64
    with pytest.raises(review_coverage.CoverageError, match="path content digest mismatch"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )
    documents = _receipt_documents(evidence, "claude")
    (evidence.review_root / "src/main.py").write_text("stale source\n")
    with pytest.raises(review_coverage.CoverageError, match="path content digest mismatch"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )

    deleted_root = tmp_path / "deleted-case"
    deleted_root.mkdir()
    deleted = _make_evidence(deleted_root, include_deleted=True)
    documents = _receipt_documents(deleted, "claude")
    for document in documents.values():
        for path_evidence in document["path_evidence"]:
            if path_evidence["path"] == "src/deleted.py":
                path_evidence["content_sha256"] = hashlib.sha256(b"not empty").hexdigest()
    with pytest.raises(review_coverage.CoverageError, match="path content digest mismatch"):
        review_coverage.validate_family_receipts(
            deleted, "claude", _write_documents(deleted_root, "claude", documents)
        )


def test_changed_path_without_hunk_evidence_is_rejected(evidence_fixture) -> None:
    evidence, factory = evidence_fixture
    with pytest.raises(review_coverage.CoverageError, match="changed path lacks hunk evidence"):
        review_coverage.validate_family_receipts(
            evidence, "claude", factory("claude", changed_hunks=[])
        )


def test_resolved_affected_unchanged_path_without_edge_is_rejected(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    documents = _receipt_documents(evidence, "claude")
    for document in documents.values():
        for item in document["path_evidence"]:
            if item["path"] == "tests/contract.py":
                item["verified_impact_edges"] = []
    with pytest.raises(review_coverage.CoverageError, match="affected path lacks impact-edge evidence"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


@pytest.mark.parametrize("bad", [[], ["extra"], ["duplicate", "duplicate"], ["forged"]])
def test_changed_hunk_ids_are_exact(tmp_path: Path, bad: list[str]) -> None:
    evidence = _make_evidence(tmp_path)
    expected = [s.patch_id for s in evidence.patch_shards if s.path == "src/main.py"]
    value = bad
    if bad == ["extra"]:
        value = expected + bad
    if bad == ["duplicate", "duplicate"]:
        value = expected + expected[:1]
    documents = _receipt_documents(evidence, "claude")
    documents[evidence.batch_ids[0]]["path_evidence"][0]["changed_hunks"] = value
    diagnostic = "changed path lacks hunk evidence" if not value else "changed hunk IDs do not match PATCH_INDEX"
    with pytest.raises(review_coverage.CoverageError, match=diagnostic):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


@pytest.mark.parametrize(
    ("mode", "unresolved"),
    [
        ("omitted", False), ("extra", False), ("duplicate", False),
        ("forged", False), ("extra", True), ("duplicate", True),
        ("forged", True),
    ],
)
def test_impact_edge_ids_are_exact(tmp_path: Path, mode: str, unresolved: bool) -> None:
    evidence = _make_evidence(tmp_path)
    documents = _receipt_documents(evidence, "claude")
    row = next(row for row in evidence.affected_paths if row.change_kind == "affected-unchanged")
    document = documents[row.batch_id]
    item = next(item for item in document["path_evidence"] if item["path"] == row.path)
    if unresolved:
        item["disposition"] = "unresolved"
        document["unresolved_paths"] = [row.path]
    if mode == "omitted":
        item["verified_impact_edges"] = []
    elif mode == "extra":
        item["verified_impact_edges"].append("impact-extra")
    elif mode == "duplicate":
        item["verified_impact_edges"].append(row.impact_edge_id)
    else:
        item["verified_impact_edges"] = ["impact-forged"]
    with pytest.raises(review_coverage.CoverageError, match="impact edge IDs do not match closure"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


def test_unresolved_edge_may_be_omitted_but_blocks_admission(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)

    def mutate(family, documents):
        if family != "claude":
            return
        row = next(row for row in evidence.affected_paths if row.change_kind == "affected-unchanged")
        document = documents[row.batch_id]
        item = next(item for item in document["path_evidence"] if item["path"] == row.path)
        item["verified_impact_edges"] = []
        item["disposition"] = "unresolved"
        document["unresolved_paths"] = [row.path]

    coverages = _all_coverages(evidence, tmp_path, mutate)
    assert coverages[0].unresolved_paths == ("tests/contract.py",)
    assert review_coverage.admit_full_coverage(evidence, coverages).admitted is False


def test_cross_kind_evidence_ids_must_be_empty(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    documents = _receipt_documents(evidence, "claude")
    first = documents[evidence.batch_ids[0]]["path_evidence"][0]
    first["verified_impact_edges"] = ["impact-forged"]
    with pytest.raises(review_coverage.CoverageError, match="unexpected cross-kind evidence"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )
    documents = _receipt_documents(evidence, "claude")
    item = next(
        item for item in documents[evidence.batch_ids[0]]["path_evidence"]
        if item["path"] == "tests/contract.py"
    )
    item["changed_hunks"] = ["patch-forged"]
    with pytest.raises(review_coverage.CoverageError, match="unexpected cross-kind evidence"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


@pytest.mark.parametrize("beyond", [False, True])
def test_partial_full_file_range_is_rejected(tmp_path: Path, beyond: bool) -> None:
    evidence = _make_evidence(tmp_path)
    documents = _receipt_documents(evidence, "claude")
    item = documents[evidence.batch_ids[0]]["path_evidence"][0]
    item["line_end"] = evidence.affected_paths[0].line_count + 1 if beyond else 1
    with pytest.raises(review_coverage.CoverageError, match="complete source range required"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


def test_line_range_beyond_current_source_is_rejected(tmp_path: Path) -> None:
    test_partial_full_file_range_is_rejected(tmp_path, True)


def test_manifest_only_observation_is_rejected(evidence_fixture) -> None:
    evidence, factory = evidence_fixture
    with pytest.raises(review_coverage.CoverageError, match="source observation mismatch"):
        review_coverage.validate_family_receipts(
            evidence, "claude", factory("claude", source_observation="src/main.py")
        )


@pytest.mark.parametrize("case", ["line", "absent", "long", "short", "whitespace"])
def test_source_observation_bounds_are_exact(tmp_path: Path, case: str) -> None:
    evidence = _make_evidence(tmp_path)
    documents = _receipt_documents(evidence, "claude")
    item = documents[evidence.batch_ids[0]]["path_evidence"][0]
    if case == "line":
        item["observation_line"] = evidence.affected_paths[0].line_count + 1
    elif case == "absent":
        item["source_observation"] = "not in the selected line"
    elif case == "long":
        item["source_observation"] = "x" * 161
    elif case == "short":
        item["source_observation"] = "line"
    else:
        item["observation_line"] = 3
        item["source_observation"] = "   "
    with pytest.raises(review_coverage.CoverageError, match="source observation mismatch"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


def test_empty_source_observation_exception_is_narrow(tmp_path: Path) -> None:
    zero = _make_evidence(tmp_path / "zero", changed_old=b"old\n", changed_new=b"")
    docs = _receipt_documents(zero, "claude")
    review_coverage.validate_family_receipts(
        zero, "claude", _write_documents(tmp_path / "zero", "claude", docs)
    )
    item = docs[zero.batch_ids[0]]["path_evidence"][0]
    item["line_start"] = 1
    item["line_end"] = 1
    with pytest.raises(review_coverage.CoverageError, match="complete source range required"):
        review_coverage.validate_family_receipts(
            zero, "claude", _write_documents(tmp_path / "zero", "claude", docs)
        )

    white_root = tmp_path / "white"
    white = _make_evidence(
        white_root,
        changed_old=b" \n \n \n \n \n \n \n",
        changed_new=b" \n\t\n \n \n \n \n \n",
    )
    docs = _receipt_documents(white, "claude")
    review_coverage.validate_family_receipts(
        white, "claude", _write_documents(white_root, "claude", docs)
    )
    item = docs[white.batch_ids[0]]["path_evidence"][0]
    item["line_start"] = None
    item["line_end"] = None
    with pytest.raises(review_coverage.CoverageError, match="complete source range required"):
        review_coverage.validate_family_receipts(
            white, "claude", _write_documents(white_root, "claude", docs)
        )


def test_changed_observation_outside_hunks_is_required(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    documents = _receipt_documents(evidence, "claude")
    item = documents[evidence.batch_ids[0]]["path_evidence"][0]
    inside = min(_hunk_lines(evidence, "src/main.py"))
    line = (evidence.review_root / "src/main.py").read_text().splitlines()[inside - 1]
    item["observation_line"] = inside
    item["source_observation"] = line
    with pytest.raises(review_coverage.CoverageError, match="observation outside changed hunks required"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


def test_empty_outside_hunk_lines_allow_patch_observation(tmp_path: Path) -> None:
    old = b"alpha original\nbeta original\ngamma original\n   \n\n   \n\n"
    new = old.replace(b"beta original", b"beta changed!")
    evidence = _make_evidence(tmp_path / "allowed", changed_old=old, changed_new=new)
    documents = _receipt_documents(evidence, "claude")
    item = documents[evidence.batch_ids[0]]["path_evidence"][0]
    item["observation_line"] = 2
    item["source_observation"] = "beta changed!"
    review_coverage.validate_family_receipts(
        evidence, "claude", _write_documents(tmp_path / "allowed", "claude", documents)
    )

    old = b"alpha original\nbeta original\ngamma original\n   \n\nnonwhite outside\n\n"
    new = old.replace(b"beta original", b"beta changed!")
    evidence = _make_evidence(tmp_path / "blocked", changed_old=old, changed_new=new)
    documents = _receipt_documents(evidence, "claude")
    item = documents[evidence.batch_ids[0]]["path_evidence"][0]
    item["observation_line"] = 2
    item["source_observation"] = "beta changed!"
    with pytest.raises(review_coverage.CoverageError, match="observation outside changed hunks required"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path / "blocked", "claude", documents)
        )


def test_full_file_hunks_allow_patch_derived_observation(tmp_path: Path) -> None:
    evidence = _make_evidence(
        tmp_path, changed_old=b"alpha old\nbeta stays\n",
        changed_new=b"alpha changed\nbeta stays\n",
    )
    documents = _receipt_documents(evidence, "claude")
    item = documents[evidence.batch_ids[0]]["path_evidence"][0]
    item["observation_line"] = 1
    item["source_observation"] = "alpha changed"
    review_coverage.validate_family_receipts(
        evidence, "claude", _write_documents(tmp_path, "claude", documents)
    )


@pytest.mark.parametrize("missing", ["severity", "location", "trigger", "evidence", "correction"])
def test_malformed_finding_is_rejected(tmp_path: Path, missing: str) -> None:
    evidence = _make_evidence(tmp_path)
    documents = _receipt_documents(evidence, "claude")
    finding = _finding("src/main.py:1")
    finding.pop(missing)
    documents[evidence.batch_ids[0]]["findings"] = [finding]
    documents[evidence.batch_ids[0]]["path_evidence"][0]["disposition"] = "finding"
    with pytest.raises(review_coverage.CoverageError, match="invalid batch receipt"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


def test_strict_json_receipt_accepts_json_arrays_for_tuple_fields(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    paths = _write_documents(tmp_path, "claude", _receipt_documents(evidence, "claude"))
    assert b'"path_evidence":[' in paths[0].read_bytes()
    coverage = review_coverage.validate_family_receipts(evidence, "claude", paths)
    assert coverage.covered_paths == tuple(row.path for row in evidence.affected_paths)


def test_single_outer_json_fence_preserves_raw_receipt_digest(tmp_path: Path) -> None:
    old = b"line 01 original\nline 02 original\nline 03 original\nline 04 original\nline 05 original\nline 06 ``` marker\n"
    new = old.replace(b"line 02 original", b"line 02 changed!")
    evidence = _make_evidence(tmp_path, changed_old=old, changed_new=new)
    documents = _receipt_documents(evidence, "claude")
    document = documents[evidence.batch_ids[0]]
    item = document["path_evidence"][0]
    item["observation_line"] = 6
    item["source_observation"] = "line 06 ``` marker"
    document["findings"] = [_finding("src/main.py:6") | {
        "trigger": "contains ``` marker", "evidence": "literal ``` is valid",
    }]
    item["disposition"] = "finding"
    paths = _write_documents(tmp_path, "claude", documents, envelope=True)
    raw = paths[0].read_bytes()
    coverage = review_coverage.validate_family_receipts(evidence, "claude", paths)
    assert coverage.receipt_digests[0] == hashlib.sha256(raw).hexdigest()

    for wrapper in (
        b"prose\n" + _canonical(document),
        b"```\n```json\n" + _canonical(document) + b"```\n```\n",
        b"```json\n" + _canonical(document) + b"```\n```json\n{}\n```\n",
    ):
        paths[0].write_bytes(wrapper)
        with pytest.raises(review_coverage.CoverageError, match="invalid receipt envelope"):
            review_coverage.validate_family_receipts(evidence, "claude", paths)


@pytest.mark.parametrize("target", ["verdict", "disposition", "severity"])
def test_receipt_rejects_duplicate_json_members_at_every_depth(tmp_path: Path, target: str) -> None:
    evidence = _make_evidence(tmp_path)
    documents = _receipt_documents(evidence, "claude")
    document = documents[evidence.batch_ids[0]]
    if target == "severity":
        document["findings"] = [_finding("src/main.py:1")]
        document["path_evidence"][0]["disposition"] = "finding"
    path = _write_documents(tmp_path, "claude", documents)[0]
    raw = path.read_bytes()
    if target == "verdict":
        raw = raw.replace(b'"verdict":"SAFE"', b'"verdict":"SAFE","verdict":"NOT-SAFE"')
    elif target == "disposition":
        raw = raw.replace(b'"disposition":"no-finding"', b'"disposition":"no-finding","disposition":"finding"', 1)
    else:
        raw = raw.replace(b'"severity":"Minor"', b'"severity":"Minor","severity":"Major"')
    path.write_bytes(raw)
    expected_digest = hashlib.sha256(raw).hexdigest()
    with pytest.raises(review_coverage.CoverageError, match="duplicate JSON member"):
        review_coverage.validate_family_receipts(evidence, "claude", [path])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_digest


def test_deleted_row_requires_patch_only_path_evidence(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path, include_deleted=True)
    documents = _receipt_documents(evidence, "claude")
    deleted = next(
        item for document in documents.values() for item in document["path_evidence"]
        if item["path"] == "src/deleted.py"
    )
    assert deleted["content_sha256"] == hashlib.sha256(b"").hexdigest()
    assert deleted["changed_hunks"]
    assert deleted["observation_line"] is deleted["line_start"] is deleted["line_end"] is None
    review_coverage.validate_family_receipts(
        evidence, "claude", _write_documents(tmp_path, "claude", documents)
    )
    deleted_source = evidence.review_root / "src/deleted.py"
    deleted_source.write_text("reappeared\n", encoding="utf-8")
    with pytest.raises(review_coverage.CoverageError, match="path content digest mismatch"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


def test_finding_location_is_source_grounded(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    for location in ("bad", "outside.py:1", "src/main.py:999"):
        documents = _receipt_documents(evidence, "claude")
        documents[evidence.batch_ids[0]]["findings"] = [_finding(location)]
        documents[evidence.batch_ids[0]]["path_evidence"][0]["disposition"] = "finding"
        with pytest.raises(review_coverage.CoverageError, match="finding location mismatch"):
            review_coverage.validate_family_receipts(
                evidence, "claude", _write_documents(tmp_path, "claude", documents)
            )

    documents = _receipt_documents(evidence, "claude")
    documents[evidence.batch_ids[0]]["findings"] = [_finding("src/main.py:1")]
    documents[evidence.batch_ids[0]]["path_evidence"][0]["disposition"] = "finding"
    source = evidence.review_root / "src/main.py"
    original = source.read_bytes()
    source.write_bytes(original + b"tampered\n")
    with pytest.raises(review_coverage.CoverageError, match="path content digest mismatch"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )
    source.write_bytes(original)

    shard = evidence.patch_shards[0]
    patch_relative = f"change-evidence/patches/{shard.group_id}/{shard.patch_id}.patch"
    documents[evidence.batch_ids[0]]["findings"] = [_finding(f"{patch_relative}:1")]
    patch = evidence.review_root / patch_relative
    original = patch.read_bytes()
    patch.write_bytes(original + b"tampered\n")
    with pytest.raises(review_coverage.CoverageError, match="finding artifact digest mismatch"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


def test_unresolved_disposition_is_rejected(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    receipts_root = tmp_path / "receipts"
    for family in FAMILIES:
        documents = _receipt_documents(evidence, family)
        if family == "claude":
            item = documents[evidence.batch_ids[0]]["path_evidence"][0]
            item["disposition"] = "unresolved"
            documents[evidence.batch_ids[0]]["unresolved_paths"] = [item["path"]]
        _write_documents(tmp_path, family, documents)
    output = evidence.review_root.parent / "coverage-admission.json"
    result = review_coverage.main(_admit_args(evidence, receipts_root, output))
    assert result != 0
    assert not output.exists()


def test_missing_path_evidence_is_rejected(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    documents = _receipt_documents(evidence, "claude")
    document = documents[evidence.batch_ids[0]]
    document["path_evidence"].pop()
    with pytest.raises(review_coverage.CoverageError, match="missing covered path"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


@pytest.mark.parametrize("mode", ["concentrated", "swapped", "extra", "reordered", "duplicate"])
def test_each_receipt_requires_exact_assigned_path_set(tmp_path: Path, mode: str) -> None:
    evidence = (
        _make_evidence(tmp_path)
        if mode == "reordered"
        else _make_evidence(tmp_path, batch_byte_limit=1)
    )
    documents = _receipt_documents(evidence, "claude")
    review_coverage.validate_family_receipts(
        evidence, "claude", _write_documents(tmp_path, "claude", deepcopy(documents))
    )
    first = evidence.batch_ids[0]
    second = evidence.batch_ids[1] if mode != "reordered" else None
    if mode == "concentrated":
        assert second is not None
        documents[first]["path_evidence"] += documents[second]["path_evidence"]
        documents[second]["path_evidence"] = []
    elif mode == "swapped":
        assert second is not None
        documents[first]["path_evidence"], documents[second]["path_evidence"] = (
            documents[second]["path_evidence"], documents[first]["path_evidence"]
        )
    elif mode == "extra":
        assert second is not None
        documents[first]["path_evidence"].append(deepcopy(documents[second]["path_evidence"][0]))
    elif mode == "reordered":
        assert len(documents[first]["path_evidence"]) >= 2
        documents[first]["path_evidence"].reverse()
    else:
        documents[first]["path_evidence"].append(deepcopy(documents[first]["path_evidence"][0]))
    with pytest.raises(review_coverage.CoverageError, match="assigned path set mismatch"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


@pytest.mark.parametrize("mode", ["missing", "extra", "swapped", "reordered", "duplicate"])
def test_each_receipt_requires_exact_assigned_inspected_surfaces(tmp_path: Path, mode: str) -> None:
    evidence = _make_evidence(tmp_path, batch_byte_limit=1)
    documents = _receipt_documents(evidence, "claude")
    first, second = evidence.batch_ids[:2]
    if mode == "missing":
        documents[first]["affected_surfaces_inspected"] = []
    elif mode == "extra":
        documents[first]["affected_surfaces_inspected"].append("outside.py")
    elif mode == "swapped":
        documents[first]["affected_surfaces_inspected"], documents[second]["affected_surfaces_inspected"] = (
            documents[second]["affected_surfaces_inspected"], documents[first]["affected_surfaces_inspected"]
        )
    elif mode == "reordered":
        documents[first]["affected_surfaces_inspected"] += documents[second]["affected_surfaces_inspected"]
        documents[first]["affected_surfaces_inspected"].reverse()
    else:
        documents[first]["affected_surfaces_inspected"] *= 2
    with pytest.raises(review_coverage.CoverageError, match="assigned inspected surfaces mismatch"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", documents)
        )


def test_not_safe_receipt_blocks_admission(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    coverages = _all_coverages(
        evidence, tmp_path,
        lambda family, docs: docs[evidence.batch_ids[0]].update(verdict="NOT-SAFE")
        if family == "claude" else None,
    )
    assert review_coverage.admit_full_coverage(evidence, coverages).admitted is False
    output = evidence.review_root.parent / "coverage-admission.json"
    assert review_coverage.main(
        _admit_args(evidence, tmp_path / "receipts", output)
    ) != 0
    assert not output.exists()


@pytest.mark.parametrize("severity", ["Critical", "Major"])
def test_critical_or_major_finding_blocks_admission(tmp_path: Path, severity: str) -> None:
    evidence = _make_evidence(tmp_path)

    def mutate(family, docs):
        if family == "claude":
            docs[evidence.batch_ids[0]]["findings"] = [_finding("src/main.py:1", severity)]
            docs[evidence.batch_ids[0]]["path_evidence"][0]["disposition"] = "finding"

    coverages = _all_coverages(evidence, tmp_path, mutate)
    assert review_coverage.admit_full_coverage(evidence, coverages).admitted is False
    output = evidence.review_root.parent / "coverage-admission.json"
    assert review_coverage.main(
        _admit_args(evidence, tmp_path / "receipts", output)
    ) != 0
    assert not output.exists()


def test_open_questions_block_admission(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    coverages = _all_coverages(
        evidence, tmp_path,
        lambda family, docs: docs[evidence.batch_ids[0]].update(open_questions=["question"])
        if family == "claude" else None,
    )
    assert review_coverage.admit_full_coverage(evidence, coverages).admitted is False
    output = evidence.review_root.parent / "coverage-admission.json"
    assert review_coverage.main(
        _admit_args(evidence, tmp_path / "receipts", output)
    ) != 0
    assert not output.exists()


@pytest.mark.parametrize("mode", ["finding-empty", "finding-hidden", "unresolved-no-finding", "unresolved-finding"])
def test_disposition_must_match_findings_and_unresolved_paths(tmp_path: Path, mode: str) -> None:
    evidence = _make_evidence(tmp_path)
    docs = _receipt_documents(evidence, "claude")
    document = docs[evidence.batch_ids[0]]
    item = document["path_evidence"][0]
    if mode == "finding-empty":
        item["disposition"] = "finding"
    elif mode == "finding-hidden":
        document["findings"] = [_finding("src/main.py:1")]
    else:
        document["unresolved_paths"] = ["src/main.py"]
        item["disposition"] = "finding" if mode.endswith("finding") else "no-finding"
        if item["disposition"] == "finding":
            document["findings"] = [_finding("src/main.py:1")]
    with pytest.raises(review_coverage.CoverageError, match="disposition mismatch"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", docs)
        )


@pytest.mark.parametrize("kind", ["source", "patch"])
def test_finding_must_belong_to_receipt_batch(tmp_path: Path, kind: str) -> None:
    evidence = _make_evidence(tmp_path, batch_byte_limit=1)
    docs = _receipt_documents(evidence, "claude")
    first, second = evidence.batch_ids[:2]
    other = docs[second]["path_evidence"][0]["path"]
    if kind == "source":
        location = f"{other}:1"
    else:
        shard = evidence.patch_shards[0]
        location = f"change-evidence/patches/{shard.group_id}/{shard.patch_id}.patch:1"
        first = second
    docs[first]["findings"] = [_finding(location)]
    with pytest.raises(review_coverage.CoverageError, match="finding belongs to another batch"):
        review_coverage.validate_family_receipts(
            evidence, "claude", _write_documents(tmp_path, "claude", docs)
        )


def test_admission_rejects_duplicate_family(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    coverages = _all_coverages(evidence, tmp_path)
    with pytest.raises(review_coverage.CoverageError, match="duplicate family coverage"):
        review_coverage.admit_full_coverage(evidence, coverages + coverages[:1])


def test_admission_rejects_missing_family(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    with pytest.raises(review_coverage.CoverageError, match="missing family coverage"):
        review_coverage.admit_full_coverage(evidence, _all_coverages(evidence, tmp_path)[:-1])


def _admit_args(evidence, receipts_root: Path, output: Path) -> list[str]:
    return [
        "admit", "--review-root", str(evidence.review_root),
        "--evidence-dir", str(evidence.review_root / "change-evidence"),
        "--receipts-root", str(receipts_root), "--output", str(output),
    ]


def _write_matrix(evidence, tmp_path: Path) -> Path:
    for family in FAMILIES:
        _write_documents(tmp_path, family, _receipt_documents(evidence, family))
    return tmp_path / "receipts"


def test_admit_cli_is_the_only_persisted_gate(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    receipts = _write_matrix(evidence, tmp_path)
    output = evidence.review_root.parent / "coverage-admission.json"
    assert review_coverage.main(_admit_args(evidence, receipts, output)) == 0
    original = output.read_bytes()
    wire = review_coverage.parse_canonical_owned_admission(original)
    assert wire.admitted is True
    assert review_coverage.canonical_admission_bytes(wire) == original

    extra = receipts / "claude" / "extra.json"
    extra.write_text("{}\n")
    assert review_coverage.main(_admit_args(evidence, receipts, output)) != 0
    assert not output.exists()
    extra.unlink()
    extra_directory = receipts / "unexpected"
    extra_directory.mkdir()
    assert review_coverage.main(_admit_args(evidence, receipts, output)) != 0
    assert not output.exists()
    extra_directory.rmdir()

    foreign = b"foreign\n"
    output.write_bytes(foreign)
    assert review_coverage.main(_admit_args(evidence, receipts, output)) != 0
    assert output.read_bytes() == foreign
    output.unlink()
    referent = tmp_path / "referent"
    referent.write_bytes(foreign)
    output.symlink_to(referent)
    assert review_coverage.main(_admit_args(evidence, receipts, output)) != 0
    assert output.is_symlink() and referent.read_bytes() == foreign
    output.unlink()

    value = json.loads(original)
    variants = [
        json.dumps(value, indent=2).encode() + b"\n",
        json.dumps(dict(reversed(list(value.items()))), separators=(",", ":")).encode() + b"\n",
        original.rstrip(b"\n"),
        _canonical(value | {"extra": True}),
    ]
    nested = deepcopy(value); nested["candidate_state"]["extra"] = True; variants.append(_canonical(nested))
    missing = deepcopy(value); missing.pop("admitted"); variants.append(_canonical(missing))
    variants.append(original.replace(b'"admitted":true', b'"admitted":true,"admitted":false'))
    for variant in variants:
        output.write_bytes(variant)
        assert review_coverage.main(_admit_args(evidence, receipts, output)) != 0
        assert output.read_bytes() == variant
        output.unlink()


def test_schema_cli_emits_canonical_batch_receipt_contract(tmp_path: Path, capsys) -> None:
    evidence = _make_evidence(tmp_path)
    output = evidence.review_root.parent / "BATCH_RECEIPT.schema.json"
    assert review_coverage.main(["schema", "--output", str(output)]) == 0
    expected = _canonical(review_coverage.BatchReceipt.model_json_schema())
    assert output.read_bytes() == expected
    stdout = json.loads(capsys.readouterr().out)
    assert stdout == {"output": str(output), "sha256": hashlib.sha256(expected).hexdigest()}


def test_schema_output_requires_absolute_ignored_nonsymlink_path(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    repo = evidence.review_root.parents[3]
    relative = Path("relative.json")
    assert review_coverage.main(["schema", "--output", str(relative)]) != 0
    visible = repo / "visible.json"
    assert review_coverage.main(["schema", "--output", str(visible)]) != 0
    referent = evidence.review_root.parent / "referent"
    referent.write_bytes(b"keep")
    linked = evidence.review_root.parent / "linked.json"
    linked.symlink_to(referent)
    assert review_coverage.main(["schema", "--output", str(linked)]) != 0
    assert referent.read_bytes() == b"keep"
    link_dir = evidence.review_root.parent / "linked-dir"
    link_dir.symlink_to(evidence.review_root.parent, target_is_directory=True)
    assert review_coverage.main(["schema", "--output", str(link_dir / "schema.json")]) != 0
    output = evidence.review_root.parent / "schema.json"
    assert review_coverage.main(["schema", "--output", str(output)]) == 0
    assert output.read_bytes() == _canonical(review_coverage.BatchReceipt.model_json_schema())


def test_admission_artifact_binds_candidate_state_and_evidence(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    receipts = _write_matrix(evidence, tmp_path)
    output = evidence.review_root.parent / "coverage-admission.json"
    assert review_coverage.main(_admit_args(evidence, receipts, output)) == 0
    value = json.loads(output.read_bytes())
    assert value["candidate_state"] == {
        "base_commit": evidence.candidate_state.base_commit,
        "head_commit": evidence.candidate_state.head_commit,
        "worktree_fingerprint": evidence.candidate_state.worktree_fingerprint,
        "canonical_diff_sha256": evidence.candidate_state.canonical_diff_sha256,
    }
    assert value["source_tree_digest"] == evidence.source_tree_digest
    assert value["change_evidence_digest"] == evidence.change_evidence_digest

    for artifact in ("CANDIDATE_STATE.json", "CHANGESET.md", "IMPACT_CLOSURE.tsv"):
        original = (evidence.review_root / "change-evidence" / artifact).read_bytes()
        (evidence.review_root / "change-evidence" / artifact).write_bytes(original + b"tamper")
        assert review_coverage.main(_admit_args(evidence, receipts, output)) != 0
        assert not output.exists()
        (evidence.review_root / "change-evidence" / artifact).write_bytes(original)
        assert review_coverage.main(_admit_args(evidence, receipts, output)) == 0


def test_admit_rejects_stale_receipt_contract(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    receipts = _write_matrix(evidence, tmp_path)
    evidence_dir = evidence.review_root / "change-evidence"
    (evidence_dir / "BATCH_RECEIPT.schema.json").write_bytes(_canonical({"type": "object"}))
    change_digest = review_evidence._record_digest(review_evidence._change_evidence_records(evidence_dir))
    changeset = (evidence_dir / "CHANGESET.md").read_text()
    changeset = __import__("re").sub(
        r"CHANGE_EVIDENCE_DIGEST=[0-9a-f]+", f"CHANGE_EVIDENCE_DIGEST={change_digest}", changeset
    )
    (evidence_dir / "CHANGESET.md").write_text(changeset)
    # CHANGESET is itself digest-bound; settle its self-excluding record digest.
    change_digest = review_evidence._record_digest(review_evidence._change_evidence_records(evidence_dir))
    changeset = __import__("re").sub(
        r"CHANGE_EVIDENCE_DIGEST=[0-9a-f]+", f"CHANGE_EVIDENCE_DIGEST={change_digest}", changeset
    )
    (evidence_dir / "CHANGESET.md").write_text(changeset)
    (evidence_dir / "MANIFEST.sha256").write_bytes(review_evidence._manifest_bytes(evidence_dir))
    for path in receipts.rglob("*.json"):
        document = json.loads(path.read_bytes())
        document["change_evidence_digest"] = change_digest
        path.write_bytes(_canonical(document))
    output = evidence.review_root.parent / "coverage-admission.json"
    assert review_coverage.main(_admit_args(evidence, receipts, output)) != 0
    assert not output.exists()


def test_admit_rejects_external_or_symlinked_evidence_dir(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    receipts = _write_matrix(evidence, tmp_path)
    output = evidence.review_root.parent / "coverage-admission.json"
    external = evidence.review_root.parent / "external-evidence"
    shutil.copytree(evidence.review_root / "change-evidence", external)
    args = _admit_args(evidence, receipts, output)
    args[args.index("--evidence-dir") + 1] = str(external)
    assert review_coverage.main(args) != 0 and not output.exists()
    original = evidence.review_root / "change-evidence"
    moved = evidence.review_root / "real-evidence"
    original.rename(moved)
    original.symlink_to(moved, target_is_directory=True)
    assert review_coverage.main(_admit_args(evidence, receipts, output)) != 0
    assert not output.exists()


def test_admit_output_requires_ignored_external_nonsymlink_path(tmp_path: Path) -> None:
    evidence = _make_evidence(tmp_path)
    receipts = _write_matrix(evidence, tmp_path)
    repo = evidence.review_root.parents[3]
    bad = [
        Path("relative.json"), repo / "visible.json",
        evidence.review_root / "inside.json",
    ]
    referent = evidence.review_root.parent / "referent"
    referent.write_bytes(b"keep")
    symlink = evidence.review_root.parent / "linked-admission.json"
    symlink.symlink_to(referent)
    bad.append(symlink)
    for output in bad:
        assert review_coverage.main(_admit_args(evidence, receipts, output)) != 0
        if output.is_absolute() and not output.is_symlink():
            assert not output.exists()
    assert referent.read_bytes() == b"keep"
    output = evidence.review_root.parent / "coverage-admission.json"
    assert review_coverage.main(_admit_args(evidence, receipts, output)) == 0
    assert output.exists()
