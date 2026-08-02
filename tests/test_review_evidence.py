from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))

import review_evidence
import review_coverage


def _git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        [
            "git",
            "-c", "core.quotepath=true",
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


def _canonical_diff(repo: Path, base_commit: str) -> bytes:
    return _git(
        repo,
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


def _candidate_fixture(
    tmp_path: Path,
    relative_path: str,
    old: bytes,
    new: bytes,
) -> tuple[Path, Path, Path, Path, Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    _git(repo, "config", "user.name", "TRIAD Test")
    _git(repo, "config", "user.email", "triad-test@example.invalid")
    (repo / ".gitignore").write_text("_runs/\n", encoding="utf-8")
    source = repo / relative_path
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(old)
    required_test = repo / "tests" / "test_contract.py"
    required_test.parent.mkdir(parents=True, exist_ok=True)
    required_test.write_text("def test_contract():\n    assert True\n", encoding="utf-8")
    _git(repo, "add", ".gitignore", relative_path, "tests/test_contract.py")
    _git(repo, "commit", "-q", "-m", "base")
    base_commit = _git(repo, "rev-parse", "HEAD").decode("ascii").strip()
    source.write_bytes(new)

    runs = repo / "_runs"
    review_root = runs / "review root"
    prepared_source = review_root / relative_path
    prepared_source.parent.mkdir(parents=True)
    prepared_source.write_bytes(new)
    prepared_test = review_root / "tests" / "test_contract.py"
    prepared_test.parent.mkdir(parents=True, exist_ok=True)
    prepared_test.write_bytes(required_test.read_bytes())
    diff_file = runs / "candidate.diff"
    diff_file.write_bytes(_canonical_diff(repo, base_commit))
    impact = runs / "impact.tsv"
    impact.write_text(
        "path\treason\treached_from\tchange_kind\tprevious_path\n"
        f"{relative_path}\tchanged\t-\tmodified\t-\n"
        "tests/test_contract.py\trequired-test-source\t"
        "owner-approved-no-exclusion-test-boundary\taffected-unchanged\t-\n",
        encoding="utf-8",
    )
    required_source_boundary = runs / "required-source-boundary.json"
    required_source_boundary.write_text(
        '{"paths":["tests/test_contract.py"],"roots":["tests"]}\n',
        encoding="utf-8",
    )
    receipt_contract = runs / "BATCH_RECEIPT.schema.json"
    receipt_contract.write_text(
        '{"title":"BatchReceipt","type":"object"}\n', encoding="utf-8"
    )
    return (
        review_root,
        diff_file,
        impact,
        required_source_boundary,
        receipt_contract,
        base_commit,
    )


def _prepare_args(fixture: tuple[Path, Path, Path, Path, Path, str], **kwargs):
    review_root, diff_file, impact, boundary, receipt, base = fixture
    return dict(
        review_root=review_root,
        diff_file=diff_file,
        impact_input=impact,
        required_source_boundary=boundary,
        receipt_contract=receipt,
        output_dir=review_root / "change-evidence",
        base_commit=base,
        batch_byte_limit=kwargs.pop("batch_byte_limit", 262144),
        **kwargs,
    )


def _prepare(fixture, **kwargs):
    return review_evidence.prepare_review_evidence(**_prepare_args(fixture, **kwargs))


def _rewrite_impact(fixture, rows: list[tuple[str, str, str, str, str]]) -> None:
    fixture[2].write_text(
        "path\treason\treached_from\tchange_kind\tprevious_path\n"
        + "".join("\t".join(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def _discard(fixture) -> None:
    evidence = fixture[0] / "change-evidence"
    if evidence.exists() and not evidence.is_symlink():
        shutil.rmtree(evidence)
    elif evidence.is_symlink():
        evidence.unlink()


def test_prepare_emits_named_headers_and_deterministic_batches(tmp_path: Path) -> None:
    fixture = _candidate_fixture(
        tmp_path,
        "src/caller.py",
        b"def caller():\n    return old()\n",
        b"def caller():\n    return changed()\n",
    )

    summary = _prepare(fixture)

    changeset = (fixture[0] / "change-evidence" / "CHANGESET.md").read_text()
    assert "FORMAT_VERSION=1\n" in changeset
    assert "GROUP_COUNT=1\n" in changeset
    assert "DIFF_FILE_SECTION_COUNT=1\n" in changeset
    assert "PATCH_FILE_COUNT=1\n" in changeset
    assert "AFFECTED_SOURCE_COUNT=2\n" in changeset
    assert "BATCH_COUNT=1\n" in changeset
    assert "SOURCE_TREE_DIGEST=" in changeset
    assert "CHANGE_EVIDENCE_DIGEST=" in changeset
    assert summary.group_ids == ("group-0001",)
    assert summary.diff_file_section_count == 1
    assert summary.patch_file_count == 1
    assert summary.batch_ids == ("batch-0001",)
    assert review_evidence.validate_review_evidence(
        fixture[0], fixture[0] / "change-evidence"
    ) == summary


def test_prepare_rejects_symlinked_affected_source(tmp_path: Path) -> None:
    fixture = _candidate_fixture(
        tmp_path, "linked.py", b"secret = False\n", b"secret = True\n"
    )
    outside = tmp_path / "outside.py"
    outside.write_text("secret = True\n", encoding="utf-8")
    (fixture[0] / "linked.py").unlink()
    (fixture[0] / "linked.py").symlink_to(outside)

    with pytest.raises(
        review_evidence.EvidenceError,
        match="prepared source differs from candidate",
    ):
        _prepare(fixture)


def test_prepare_and_validate_cli_are_cwd_independent(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "src/a.py", b"a=1\n", b"a=2\n")
    review_root, diff_file, impact, boundary, receipt, base = fixture
    unrelated = tmp_path / "elsewhere"
    unrelated.mkdir()
    prepare = subprocess.run(
        [
            sys.executable,
            str((BIN / "review_evidence.py").resolve()),
            "prepare",
            "--review-root", str(review_root.resolve()),
            "--base-commit", base,
            "--diff-file", str(diff_file.resolve()),
            "--impact-input", str(impact.resolve()),
            "--required-source-boundary", str(boundary.resolve()),
            "--receipt-contract", str(receipt.resolve()),
            "--output-dir", str((review_root / "change-evidence").absolute()),
            "--batch-byte-limit", "262144",
        ],
        cwd=unrelated,
        capture_output=True,
    )
    assert prepare.returncode == 0, prepare.stderr.decode()
    assert prepare.stderr == b""
    validate = subprocess.run(
        [
            sys.executable,
            str((BIN / "review_evidence.py").resolve()),
            "validate",
            "--review-root", str(review_root.resolve()),
            "--evidence-dir", str((review_root / "change-evidence").resolve()),
        ],
        cwd=unrelated,
        capture_output=True,
    )
    assert validate.returncode == 0, validate.stderr.decode()
    assert validate.stderr == b""
    assert validate.stdout == prepare.stdout
    data = json.loads(prepare.stdout)
    assert list(data) == sorted(data)
    assert set(data) == {
        "affected_source_count", "base_commit", "batch_ids",
        "batch_receipt_contract_path", "canonical_diff_sha256",
        "change_evidence_digest", "format_version", "head_commit",
        "patch_file_count", "source_tree_digest", "worktree_fingerprint",
    }
    assert data["base_commit"] == base
    assert data["canonical_diff_sha256"] == hashlib.sha256(diff_file.read_bytes()).hexdigest()


def test_cli_rejects_noncanonical_paths_and_missing_artifacts(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    script = str((BIN / "review_evidence.py").resolve())
    result = subprocess.run(
        [sys.executable, script, "validate", "--review-root", "relative", "--evidence-dir", "relative/change-evidence"],
        capture_output=True,
    )
    assert result.returncode == 2
    assert result.stdout == b""
    assert result.stderr.startswith(b"review-evidence: ") and result.stderr.count(b"\n") == 1
    result = subprocess.run(
        [sys.executable, script, "validate", "--review-root", str(fixture[0].resolve()), "--evidence-dir", str((tmp_path / "external").resolve())],
        capture_output=True,
    )
    assert result.returncode == 2 and result.stdout == b""
    assert not (fixture[0] / "change-evidence" / "MANIFEST.sha256").exists()


def test_prepare_rejects_existing_evidence_leaf(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    output = fixture[0] / "change-evidence"
    output.mkdir()
    with pytest.raises(review_evidence.EvidenceError, match="evidence directory exists"):
        _prepare(fixture)
    (output / "stale.patch").write_text("stale")
    with pytest.raises(review_evidence.EvidenceError, match="evidence directory exists"):
        _prepare(fixture)
    shutil.rmtree(output)
    assert _prepare(fixture).format_version == 1


def test_prepare_rejects_subset_of_canonical_candidate_diff(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    repo = fixture[0].parents[1]
    (repo / "b.py").write_text("b=1\n")
    _git(repo, "add", "b.py")
    _git(repo, "commit", "-q", "-m", "add b")
    (repo / "b.py").write_text("b=2\n")
    with pytest.raises(review_evidence.EvidenceError, match="candidate diff mismatch"):
        _prepare(fixture)


def test_candidate_diff_prefixes_ignore_user_git_config(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "src/a.py", b"a=1\n", b"a=2\n")
    repo = fixture[0].parents[1]
    for key, value in (("diff.noprefix", "true"), ("diff.mnemonicPrefix", "true"), ("diff.srcPrefix", "evil/"), ("diff.dstPrefix", "hostile/")):
        _git(repo, "config", key, value)
    fixture[1].write_bytes(_canonical_diff(repo, fixture[5]))
    summary = _prepare(fixture)
    shard = next((fixture[0] / "change-evidence" / "patches").rglob("*.patch"))
    assert b"diff --git a/src/a.py b/src/a.py" in shard.read_bytes()
    assert review_evidence.validate_review_evidence(fixture[0], fixture[0] / "change-evidence") == summary


def test_candidate_fingerprint_and_validation_ignore_local_diff_config(
    tmp_path: Path,
) -> None:
    fixture = _candidate_fixture(
        tmp_path,
        "src/a.py",
        b"one\ntwo\nthree\nold\nfive\nsix\nseven\neight\n",
        b"one\ntwo\nthree\nnew\nfive\nsix\nseven\neight\n",
    )
    repo = fixture[0].parents[1]
    rename_old = repo / "rename-old.py"
    rename_old.write_text("same=True\n")
    _git(repo, "add", "rename-old.py")
    _git(repo, "commit", "-q", "-m", "add rename source")
    fixture = (*fixture[:5], _git(repo, "rev-parse", "HEAD").decode().strip())
    rename_old.rename(repo / "rename-new.py")
    _git(repo, "add", "-A", "rename-old.py", "rename-new.py")
    (fixture[0] / "rename-new.py").write_text("same=True\n")
    _rewrite_impact(fixture, [
        ("rename-new.py", "changed", "-", "renamed", "rename-old.py"),
        ("src/a.py", "changed", "-", "modified", "-"),
        ("tests/test_contract.py", "required-test-source", "owner-approved-no-exclusion-test-boundary", "affected-unchanged", "-"),
    ])
    fixture[1].write_bytes(_canonical_diff(repo, fixture[5]))
    for key, value in (
        ("diff.context", "3"),
        ("diff.algorithm", "myers"),
        ("diff.indentHeuristic", "false"),
        ("diff.renames", "true"),
    ):
        _git(repo, "config", key, value)

    summary = _prepare(fixture)
    fingerprint = summary.candidate_state.worktree_fingerprint

    for key, value in (
        ("diff.context", "0"),
        ("diff.algorithm", "histogram"),
        ("diff.indentHeuristic", "true"),
        ("diff.renames", "copies"),
    ):
        _git(repo, "config", key, value)

    assert review_evidence._canonical_worktree_fingerprint(repo) == fingerprint
    assert review_evidence.validate_review_evidence(
        fixture[0], fixture[0] / "change-evidence"
    ) == summary


def test_candidate_state_rejects_symbolic_unknown_or_nonancestor_base(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    repo = fixture[0].parents[1]
    head = _git(repo, "rev-parse", "HEAD").decode().strip()
    other = "0" * len(head)
    for base in ("HEAD", head[:12], other):
        with pytest.raises(review_evidence.EvidenceError, match="invalid base commit"):
            review_evidence.prepare_review_evidence(**{**_prepare_args(fixture), "base_commit": base})
        _discard(fixture)
    disconnected = _git(repo, "commit-tree", f"{head}^{{tree}}", "-m", "disconnected").decode().strip()
    with pytest.raises(review_evidence.EvidenceError, match="invalid base commit"):
        review_evidence.prepare_review_evidence(**{**_prepare_args(fixture), "base_commit": disconnected})


def test_candidate_state_rejects_nonignored_untracked_entry(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    (fixture[0].parents[1] / "untracked.txt").write_text("x")
    with pytest.raises(review_evidence.EvidenceError, match="untracked candidate state"):
        _prepare(fixture)


def test_candidate_inputs_and_review_root_must_be_git_ignored(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    repo = fixture[0].parents[1]
    for key in ("diff_file", "impact_input", "required_source_boundary", "receipt_contract"):
        args = _prepare_args(fixture)
        copied = repo / f"leader-{key}"
        copied.write_bytes(Path(args[key]).read_bytes())
        args[key] = copied
        with pytest.raises(review_evidence.EvidenceError, match="leader path is not ignored"):
            review_evidence.prepare_review_evidence(**args)
        copied.unlink()


def test_validate_rejects_candidate_state_mutation(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    repo = fixture[0].parents[1]
    extra = repo / "extra.py"
    extra.write_text("x=1\n")
    _git(repo, "add", "extra.py")
    _git(repo, "commit", "-q", "-m", "extra")
    fixture = (*fixture[:5], _git(repo, "rev-parse", "HEAD").decode().strip())
    fixture[1].write_bytes(_canonical_diff(repo, fixture[5]))
    _prepare(fixture)
    extra.write_text("x=2\n")
    with pytest.raises(review_evidence.EvidenceError, match="candidate state mismatch"):
        review_evidence.validate_review_evidence(fixture[0], fixture[0] / "change-evidence")
    extra.write_text("x=1\n")
    state_path = fixture[0] / "change-evidence" / "CANDIDATE_STATE.json"
    original = json.loads(state_path.read_text())
    for field in original:
        state = dict(original)
        state[field] = "0" * len(str(state[field]))
        state_path.write_text(json.dumps(state, sort_keys=True, separators=(",", ":")) + "\n")
        with pytest.raises(review_evidence.EvidenceError, match="candidate state mismatch"):
            review_evidence.validate_review_evidence(fixture[0], fixture[0] / "change-evidence")
    state_path.write_text(json.dumps(original, sort_keys=True, separators=(",", ":")) + "\n")


def test_prepare_rejects_stale_or_miscopied_prepared_source(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\nb=1\n", b"a=2\nb=1\n")
    (fixture[0] / "a.py").write_text("a=2\nb=stale\n")
    with pytest.raises(review_evidence.EvidenceError, match="prepared source differs from candidate"):
        _prepare(fixture)
    (fixture[0] / "a.py").write_bytes((fixture[0].parents[1] / "a.py").read_bytes())
    (fixture[0] / "tests/test_contract.py").write_text("stale\n")
    with pytest.raises(review_evidence.EvidenceError, match="prepared source differs from candidate"):
        _prepare(fixture)


def test_prepare_rejects_unlisted_prepared_regular_file(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    (fixture[0] / "extra.txt").write_text("x")
    with pytest.raises(review_evidence.EvidenceError, match="prepared file lacks closure row"):
        _prepare(fixture)
    (fixture[0] / "extra.txt").unlink()
    assert len(_prepare(fixture).affected_paths) == 2


def test_required_test_source_rows_cover_exact_current_test_inventory(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "src/a.py", b"a=1\n", b"a=2\n")
    repo = fixture[0].parents[1]
    (repo / "tests/second.py").write_text("second=True\n")
    _git(repo, "add", "tests/second.py")
    _git(repo, "commit", "-q", "-m", "second")
    fixture = (*fixture[:5], _git(repo, "rev-parse", "HEAD").decode().strip())
    (fixture[0] / "tests/second.py").write_text("second=True\n")
    fixture[3].write_text('{"paths":["tests/second.py","tests/test_contract.py"],"roots":["tests"]}\n')
    fixture[1].write_bytes(_canonical_diff(repo, fixture[5]))
    _rewrite_impact(fixture, [
        ("src/a.py", "changed", "-", "modified", "-"),
        ("tests/second.py", "required-test-source", "owner-approved-no-exclusion-test-boundary", "affected-unchanged", "-"),
        ("tests/test_contract.py", "required-test-source", "owner-approved-no-exclusion-test-boundary", "affected-unchanged", "-"),
    ])
    assert len(_prepare(fixture).affected_paths) == 3
    _discard(fixture)
    _rewrite_impact(fixture, [("src/a.py", "changed", "-", "modified", "-"), ("tests/test_contract.py", "required-test-source", "owner-approved-no-exclusion-test-boundary", "affected-unchanged", "-")])
    with pytest.raises(review_evidence.EvidenceError, match="required source boundary mismatch"):
        _prepare(fixture)


def test_required_source_boundary_is_canonical_git_bound_and_digest_bound(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    accepted = fixture[3].read_bytes()
    summary = _prepare(fixture)
    evidence = fixture[0] / "change-evidence"
    assert (evidence / "REQUIRED_SOURCE_BOUNDARY.json").read_bytes() == accepted
    assert "REQUIRED_SOURCE_BOUNDARY.json" in (evidence / "MANIFEST.sha256").read_text()
    assert summary.change_evidence_digest
    _discard(fixture)
    for bad in (b'{}\n', b'{"paths":[], "roots":[]}\n', b'{"paths":["outside"],"roots":["tests"]}\n'):
        fixture[3].write_bytes(bad)
        with pytest.raises(review_evidence.EvidenceError, match="required source boundary mismatch"):
            _prepare(fixture)
        _discard(fixture)


def test_receipt_contract_is_canonical_and_digest_bound(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    accepted = fixture[4].read_bytes()
    summary = _prepare(fixture)
    evidence = fixture[0] / "change-evidence"
    assert (evidence / "BATCH_RECEIPT.schema.json").read_bytes() == accepted
    assert "BATCH_RECEIPT.schema.json" in (evidence / "MANIFEST.sha256").read_text()
    assert summary.change_evidence_digest
    _discard(fixture)
    for bad in (b'[]\n', b'{"type": "object"}\n', b'\xff'):
        fixture[4].write_bytes(bad)
        with pytest.raises(review_evidence.EvidenceError, match="invalid receipt contract"):
            _prepare(fixture)
        _discard(fixture)


def test_prepare_rejects_duplicate_impact_paths(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    with fixture[2].open("a") as stream:
        stream.write("a.py\tchanged\t-\tmodified\t-\n")
    with pytest.raises(review_evidence.EvidenceError, match="duplicate affected path"):
        _prepare(fixture)


def test_prepare_rejects_unsupported_impact_reason(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    text = fixture[2].read_text().replace("\tchanged\t", "\tguessed\t", 1)
    fixture[2].write_text(text)
    with pytest.raises(review_evidence.EvidenceError, match="unsupported impact reason"):
        _prepare(fixture)


def test_prepare_rejects_traversal_path(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    fixture[2].write_text(fixture[2].read_text().replace("a.py", "../outside.py", 1))
    with pytest.raises(review_evidence.EvidenceError, match="invalid review-relative path"):
        _prepare(fixture)


@pytest.mark.parametrize("field", ["path", "reached_from", "previous_path"])
@pytest.mark.parametrize("control", ["\x00", "\n", "\r", "\t"])
def test_prepare_rejects_control_characters_in_tsv_path_fields(
    tmp_path: Path, field: str, control: str
) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    values = {
        "path": "a.py",
        "reached_from": "-",
        "previous_path": "-",
    }
    values[field] = f"bad{control}value"
    fixture[2].write_text(
        "path\treason\treached_from\tchange_kind\tprevious_path\n"
        f"{values['path']}\tchanged\t{values['reached_from']}\tmodified\t"
        f"{values['previous_path']}\n",
        encoding="utf-8",
    )
    with pytest.raises(review_evidence.EvidenceError, match="control character in TSV field"):
        _prepare(fixture)


def test_prepare_rejects_missing_diff_row_for_changed_closure(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    (fixture[0] / "missing.py").write_text("x=1\n")
    repo = fixture[0].parents[1]
    (repo / "missing.py").write_text("x=1\n")
    _git(repo, "add", "missing.py")
    _git(repo, "commit", "-q", "-m", "tracked missing")
    fixture = (*fixture[:5], _git(repo, "rev-parse", "HEAD").decode().strip())
    fixture[1].write_bytes(_canonical_diff(repo, fixture[5]))
    _rewrite_impact(fixture, [("a.py", "changed", "-", "modified", "-"), ("missing.py", "changed", "-", "added", "-"), ("tests/test_contract.py", "required-test-source", "owner-approved-no-exclusion-test-boundary", "affected-unchanged", "-")])
    with pytest.raises(review_evidence.EvidenceError, match="changed closure row lacks diff section"):
        _prepare(fixture)


def test_prepare_rejects_missing_changed_row_for_diff_target(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    _rewrite_impact(fixture, [("a.py", "caller", "tests/test_contract.py", "affected-unchanged", "-"), ("tests/test_contract.py", "required-test-source", "owner-approved-no-exclusion-test-boundary", "affected-unchanged", "-")])
    with pytest.raises(review_evidence.EvidenceError, match="diff target lacks changed closure row"):
        _prepare(fixture)


def test_prepare_rejects_reason_change_kind_mismatch(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    for row in (("a.py", "changed", "-", "affected-unchanged", "-"), ("a.py", "caller", "x", "modified", "-")):
        _rewrite_impact(fixture, [row, ("tests/test_contract.py", "required-test-source", "owner-approved-no-exclusion-test-boundary", "affected-unchanged", "-")])
        with pytest.raises(review_evidence.EvidenceError, match="reason/change_kind mismatch"):
            _prepare(fixture)
        _discard(fixture)


def test_prepare_handles_deletion_and_rename(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "old.py", b"old=True\n", b"new=True\n")
    repo = fixture[0].parents[1]
    (repo / "old.py").unlink()
    (fixture[0] / "old.py").unlink()
    fixture[1].write_bytes(_canonical_diff(repo, fixture[5]))
    _rewrite_impact(fixture, [("old.py", "changed", "-", "deleted", "old.py"), ("tests/test_contract.py", "required-test-source", "owner-approved-no-exclusion-test-boundary", "affected-unchanged", "-")])
    summary = _prepare(fixture)
    deleted = next(row for row in summary.affected_paths if row.path == "old.py")
    assert deleted.content_sha256 == hashlib.sha256(b"").hexdigest()
    assert (deleted.byte_count, deleted.line_count, deleted.previous_path) == (0, 0, "old.py")

    rename_fixture = _candidate_fixture(
        tmp_path / "rename", "before.py", b"same=True\n", b"same=True\n"
    )
    rename_repo = rename_fixture[0].parents[1]
    (rename_repo / "before.py").rename(rename_repo / "after.py")
    _git(rename_repo, "add", "-A", "before.py", "after.py")
    (rename_fixture[0] / "before.py").rename(rename_fixture[0] / "after.py")
    rename_fixture[1].write_bytes(_canonical_diff(rename_repo, rename_fixture[5]))
    _rewrite_impact(rename_fixture, [
        ("after.py", "changed", "-", "renamed", "before.py"),
        ("tests/test_contract.py", "required-test-source", "owner-approved-no-exclusion-test-boundary", "affected-unchanged", "-"),
    ])
    renamed_summary = _prepare(rename_fixture)
    renamed = next(row for row in renamed_summary.affected_paths if row.path == "after.py")
    assert renamed.previous_path == "before.py"
    assert renamed.change_kind == "renamed"
    assert not (rename_fixture[0] / "before.py").exists()
    assert next(shard for shard in renamed_summary.patch_shards if shard.path == "after.py").hunk_ordinal is None


def test_prepare_rejects_deleted_path_with_current_prepared_source(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "old.py", b"old=True\n", b"new=True\n")
    repo = fixture[0].parents[1]
    (repo / "old.py").unlink()
    fixture[1].write_bytes(_canonical_diff(repo, fixture[5]))
    _rewrite_impact(fixture, [
        ("old.py", "changed", "-", "deleted", "old.py"),
        (
            "tests/test_contract.py",
            "required-test-source",
            "owner-approved-no-exclusion-test-boundary",
            "affected-unchanged",
            "-",
        ),
    ])

    with pytest.raises(
        review_evidence.EvidenceError, match="deleted path has current source"
    ):
        _prepare(fixture)


def test_prepare_rejects_deleted_row_without_deletion_diff(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "old.py", b"old=True\n", b"new=True\n")
    _rewrite_impact(fixture, [
        ("old.py", "changed", "-", "deleted", "old.py"),
        (
            "tests/test_contract.py",
            "required-test-source",
            "owner-approved-no-exclusion-test-boundary",
            "affected-unchanged",
            "-",
        ),
    ])

    with pytest.raises(
        review_evidence.EvidenceError, match="deleted row lacks deletion diff"
    ):
        _prepare(fixture)


def test_evidence_directory_must_be_canonical_child(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    for output in (tmp_path / "external", fixture[0] / "alternate"):
        with pytest.raises(review_evidence.EvidenceError):
            review_evidence.prepare_review_evidence(**{**_prepare_args(fixture), "output_dir": output.absolute()})
    target = tmp_path / "target"
    target.mkdir()
    (fixture[0] / "change-evidence").symlink_to(target, target_is_directory=True)
    with pytest.raises(review_evidence.EvidenceError):
        _prepare(fixture)


@pytest.mark.parametrize("data,count", [(b"a\n", 1), (b"a", 1), (b"\n", 1), (b"", 0)])
def test_line_count_matches_splitlines_convention(tmp_path: Path, data: bytes, count: int) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"old\n", data)
    summary = _prepare(fixture)
    assert next(row.line_count for row in summary.affected_paths if row.path == "a.py") == count


@pytest.mark.parametrize("separator", ["\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"])
def test_prepare_rejects_unsupported_source_line_separators(tmp_path: Path, separator: str) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"old\n", f"a{separator}b\n".encode())
    with pytest.raises(review_evidence.EvidenceError, match="unsupported source line separator"):
        _prepare(fixture)
    affected = _candidate_fixture(tmp_path / "affected", "a.py", b"old\n", b"new\n")
    repo = affected[0].parents[1]
    helper = repo / "helper.py"
    helper.write_text(f"a{separator}b\n")
    _git(repo, "add", "helper.py")
    _git(repo, "commit", "-q", "-m", "add affected helper")
    affected = (*affected[:5], _git(repo, "rev-parse", "HEAD").decode().strip())
    (affected[0] / "helper.py").write_bytes(helper.read_bytes())
    affected[1].write_bytes(_canonical_diff(repo, affected[5]))
    _rewrite_impact(affected, [
        ("a.py", "changed", "-", "modified", "-"),
        ("helper.py", "caller", "a.py", "affected-unchanged", "-"),
        ("tests/test_contract.py", "required-test-source", "owner-approved-no-exclusion-test-boundary", "affected-unchanged", "-"),
    ])
    with pytest.raises(review_evidence.EvidenceError, match="unsupported source line separator"):
        _prepare(affected)


def test_prepare_rejects_non_utf8_current_source(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"old\n", b"\xff\n")
    with pytest.raises(review_evidence.EvidenceError, match="non-UTF-8 source"):
        _prepare(fixture)
    affected = _candidate_fixture(tmp_path / "affected", "a.py", b"old\n", b"new\n")
    repo = affected[0].parents[1]
    helper = repo / "helper.py"
    helper.write_bytes(b"\xff\n")
    _git(repo, "add", "helper.py")
    _git(repo, "commit", "-q", "-m", "add affected helper")
    affected = (*affected[:5], _git(repo, "rev-parse", "HEAD").decode().strip())
    (affected[0] / "helper.py").write_bytes(helper.read_bytes())
    affected[1].write_bytes(_canonical_diff(repo, affected[5]))
    _rewrite_impact(affected, [
        ("a.py", "changed", "-", "modified", "-"),
        ("helper.py", "caller", "a.py", "affected-unchanged", "-"),
        ("tests/test_contract.py", "required-test-source", "owner-approved-no-exclusion-test-boundary", "affected-unchanged", "-"),
    ])
    with pytest.raises(review_evidence.EvidenceError, match="non-UTF-8 source"):
        _prepare(affected)


def test_batch_manifest_has_exact_header_and_ordered_rows(tmp_path: Path) -> None:
    old = b"z=1\n" + b"".join(
        f"stable_{index}=True\n".encode() for index in range(2, 12)
    ) + b"tail=1\n"
    new = old.replace(b"z=1\n", b"z=2\n").replace(b"tail=1\n", b"tail=2\n")
    fixture = _candidate_fixture(tmp_path, "z.py", old, new)
    summary = _prepare(fixture)
    batches = fixture[0] / "change-evidence" / "batches"
    observed_paths: list[str] = []
    closure_batches = {row.path: row.batch_id for row in summary.affected_paths}
    for batch_id in summary.batch_ids:
        lines = (batches / f"{batch_id}.tsv").read_text().splitlines()
        assert lines[0] == "path\treason\tchange_kind\tcontent_sha256\tbyte_count\tline_count\tpatch_ids\timpact_edge_ids"
        for line in lines[1:]:
            fields = line.split("\t")
            assert len(fields) == 8
            observed_paths.append(fields[0])
            assert closure_batches[fields[0]] == batch_id
            if fields[0] == "z.py":
                assert fields[6] == (
                    "patch-000001-hunk-0001,patch-000001-hunk-0002"
                )
                assert fields[7] == "-"
            else:
                assert fields[6] == "-"
                assert fields[7].startswith("edge-")
    assert observed_paths == ["tests/test_contract.py", "z.py"]


def test_oversized_source_receives_complete_single_path_batch(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "large.py", b"old\n", b"x" * 100 + b"\n")
    summary = _prepare(fixture, batch_byte_limit=10)
    row = next(row for row in summary.affected_paths if row.path == "large.py")
    assert row.byte_count == 101
    batch_lines = (fixture[0] / "change-evidence" / "batches" / f"{row.batch_id}.tsv").read_text().splitlines()
    assert len(batch_lines) == 2


def test_validate_rejects_source_digest_mutation(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    _prepare(fixture)
    (fixture[0] / "a.py").write_text("a=3\n")
    with pytest.raises(review_evidence.EvidenceError, match="source digest mismatch"):
        review_evidence.validate_review_evidence(fixture[0], fixture[0] / "change-evidence")


def test_validate_and_admit_reject_symlinked_prepared_closure_source(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    _prepare(fixture)
    referent = tmp_path / "same.py"
    referent_bytes = b"a=2\n"
    referent.write_bytes(referent_bytes)
    (fixture[0] / "a.py").unlink()
    (fixture[0] / "a.py").symlink_to(referent)
    with pytest.raises(review_evidence.EvidenceError, match="prepared source differs from candidate"):
        review_evidence.validate_review_evidence(fixture[0], fixture[0] / "change-evidence")
    admission = fixture[0].parent / "coverage-admission.json"
    assert review_coverage.main([
        "admit",
        "--review-root", str(fixture[0]),
        "--evidence-dir", str(fixture[0] / "change-evidence"),
        "--receipts-root", str(fixture[0].parent / "receipts"),
        "--output", str(admission),
    ]) != 0
    assert not admission.exists()
    assert referent.read_bytes() == referent_bytes


def test_validate_rejects_missing_named_header(tmp_path: Path) -> None:
    fixture = _candidate_fixture(tmp_path, "a.py", b"a=1\n", b"a=2\n")
    _prepare(fixture)
    path = fixture[0] / "change-evidence" / "CHANGESET.md"
    path.write_text(path.read_text().replace("AFFECTED_SOURCE_COUNT=2\n", ""))
    with pytest.raises(review_evidence.EvidenceError, match="missing CHANGESET header"):
        review_evidence.validate_review_evidence(fixture[0], fixture[0] / "change-evidence")


def test_prepare_large_diff_is_deterministic_and_preserves_hostile_paths(tmp_path: Path) -> None:
    hostile_path = "file ' ` $(touch hostile-marker).py"
    padding = b"x" * 8500
    fixture = _candidate_fixture(
        tmp_path, hostile_path, b"old-" + padding + b"\n", b"new-" + padding + b"\n"
    )
    repo = fixture[0].parents[1]
    rows = [(hostile_path, "changed", "-", "modified", "-")]
    for index in range(1, 1200):
        rel = f"bulk/f{index:04d}.txt"
        candidate = repo / rel
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_bytes(b"old-" + padding + b"\n")
        _git(repo, "add", rel)
    _git(repo, "commit", "-q", "-m", "bulk")
    fixture = (*fixture[:5], _git(repo, "rev-parse", "HEAD").decode().strip())
    for index in range(1, 1200):
        rel = f"bulk/f{index:04d}.txt"
        (repo / rel).write_bytes(b"new-" + padding + b"\n")
        prepared = fixture[0] / rel
        prepared.parent.mkdir(parents=True, exist_ok=True)
        prepared.write_bytes(b"new-" + padding + b"\n")
        rows.append((rel, "changed", "-", "modified", "-"))
    rows.append(("tests/test_contract.py", "required-test-source", "owner-approved-no-exclusion-test-boundary", "affected-unchanged", "-"))
    fixture[1].write_bytes(_canonical_diff(repo, fixture[5]))
    assert len(fixture[1].read_bytes()) > 10_000_000
    _rewrite_impact(fixture, rows)
    summary = _prepare(fixture)
    second_root = repo / "_runs" / "second review root"
    shutil.copytree(
        fixture[0],
        second_root,
        ignore=shutil.ignore_patterns("change-evidence"),
    )
    second_summary = review_evidence.prepare_review_evidence(
        second_root,
        fixture[1],
        fixture[2],
        fixture[3],
        fixture[4],
        second_root / "change-evidence",
        base_commit=fixture[5],
        batch_byte_limit=262144,
    )
    assert summary.group_ids == tuple(f"group-{n:04d}" for n in range(1, 13))
    assert summary.patch_file_count == 1200
    assert summary == second_summary
    assert (fixture[0] / "change-evidence" / "MANIFEST.sha256").read_bytes() == (
        second_root / "change-evidence" / "MANIFEST.sha256"
    ).read_bytes()
    assert not (repo / "hostile-marker").exists()


def test_unified_hunk_must_match_current_source(tmp_path: Path) -> None:
    invalid = (
        (b"@@ malformed @@\n+a\n", b"a\n"),
        (b"@@ -1 +1,2 @@\n-a\n+a\n", b"a\n"),
        (b"@@ -1 +2 @@\n-a\n+a\n", b"a\n"),
        (b"@@ -1 +1 @@\n-a\n+wrong\n", b"a\n"),
        (b"@@ -1 +1 @@\n-a\n+a\n\\ No newline at end of file\n", b"a\n"),
    )
    for hunk, source in invalid:
        with pytest.raises(review_evidence.EvidenceError, match="invalid unified hunk"):
            review_evidence._validate_hunk(hunk, source)

    accepted = (
        (b"@@ -0,0 +1 @@\n+a\n", b"a\n"),
        (b"@@ -1 +0,0 @@\n-a\n", b""),
        (b"@@ -1,0 +2 @@ function heading\n+b\n", b"a\nb\n"),
        (b"@@ -2 +1,0 @@\n-b\n", b"a\n"),
    )
    for hunk, source in accepted:
        review_evidence._validate_hunk(hunk, source)

    sections = []
    for index in range(1, 101):
        hunks = b"@@ -1 +1 @@ heading\n-old\n+new\n"
        if index == 100:
            hunks += b"@@ -3 +3 @@\n-old\n+new\n"
        sections.append(
            (
                f"diff --git a/f{index}.txt b/f{index}.txt\n"
                "index 0000000..1111111 100644\n"
                f"--- a/f{index}.txt\n+++ b/f{index}.txt\n"
            ).encode()
            + hunks
        )
    parsed = review_evidence._split_diff(b"".join(sections))
    sources = {section.path: b"new\nkeep\nnew\n" for section in parsed}
    shards = review_evidence._section_shard_records(parsed, sources)
    assert len(parsed) == 100
    assert len(shards) == 101
    assert {shard.group_id for shard, _ in shards} == {"group-0001"}
    assert b"@@ -1 +1 @@ heading\n" in shards[0][1]
