# Native Permissions and Full-Coverage Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make TRIAD inherit the developer's active provider permissions and require every model family to review every changed and affected production source with digest-bound per-path evidence.

**Architecture:** Add two focused Python modules: one prepares and validates immutable change evidence, and one validates per-family coverage receipts. Remove wrapper and bootstrap permission-controller behavior while retaining data authorization, executable/path validation, mutation detection, result custody, and explicit legacy packet compatibility.

**Tech Stack:** Python 3.12, Pydantic 2, pytest, Bash 3.2-compatible bootstrap, Markdown skills and public documentation, Codex plugin manifest.

## Global Constraints

- Work in `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`.
- Commit this plan on the current clean planning branch, then create
  `release/0.2.532` from that plan commit before production edits. Verify
  `1744c43c52b80cf2e28201a1c67d50611480f760` is an ancestor of the new branch.
- Preserve the pre-existing commits and unrelated user-owned files.
- Run every direct `python3` command from `/Users/chaniri/codex_workspace` through `/bin/zsh -lic`, after recording `command -v python3`, `python3 --version`, and `python3 -m pytest --version`.
- Use TDD for every behavior change: run the focused RED test, confirm the expected failure, implement the minimum change, then run focused and neighboring GREEN tests.
- Every formal-review family covers every deterministic batch. Family perspectives never partition source coverage.
- A manifest path alone is not coverage. Each affected path requires digest-bound symbol/positive-line evidence plus changed-hunk or impact-edge disposition.
- TRIAD never adds sandbox, permission-mode, yolo, bypass, accept-edits, auto-edit, dont-ask, or equivalent provider controls.
- Native AGY headless permission denial is terminal `permission-unavailable`; it is never retried with broader authority.
- Formal reviewers do not execute candidate code, tests, builds, hooks, or generated scripts.
- Exact owner-authored provider settings, Codex approval/reviewer settings, credentials, rules, and unrelated files remain unchanged.
- Plugin-owned legacy permission artifacts are removed only after exact marker/content ownership validation.
- Keep legacy packet validation reachable only from its existing explicit compatibility arguments.
- Use `0.2.532` for release metadata.

## Mandatory Review Gates and Scope Breaker

Before Task 1, run a `formal-gate` plan round with fresh independent Claude,
Google-family, and Codex legs over one leader-prepared immutable directory.
Include this executable plan, the approved design, every current production,
configuration, documentation, migration, skill, bootstrap, and wrapper file
named in the File Map, plus all repository test source. The exact test-source
boundary is `no test-source exclusions; all repository test source is
included`. Every leg receives the same directory, objective, digest, and
no-edit/no-execution contract. Implementation may begin only after all three
legs are valid and `SAFE`, with no open question and an unchanged digest.

After all implementation and local verification, but before installation,
push, PR creation, merge, tag, or release, run a fresh `formal-gate` pre-merge
round with the same three families and the same exact no-exclusion test-source
boundary. The candidate contains the complete branch diff, every changed
production file, every affected unchanged production file, relevant
configuration/build/documentation, and all repository test source. Every family
reviews every deterministic batch and every affected source. A candidate-byte,
closure, or digest change invalidates the round and requires all three fresh
legs again.

For findings from either formal round or any task review, the root leader first
reproduces the claim and classifies it:

1. A defect or underspecification inside the approved design permits only the
   smallest bounded correction and a fresh applicable review.
2. A design change, generalized abstraction, new validator/protocol/runtime
   capability, speculative edge-case handler, unrelated cleanup, or broader
   compatibility surface stops for owner approval before editing.

Reviewer confidence or a `NOT-SAFE` label never authorizes category 2. Do not
implement a universal impact analyzer, provider permission manager, speculative
framework, or cleanup outside the File Map merely to satisfy a reviewer. This
scope breaker governs every implementer, task reviewer, fix round, and final
review.

## File Map

### New focused modules

- Create `bin/review_evidence.py`: deterministic evidence preparation, parsing, hashing, batching, validation, and CLI.
- Create `bin/review_coverage.py`: Pydantic receipt models and full-family admission.
- Create `tests/test_review_evidence.py`: evidence-format, hostile-path, digest, and large-diff tests.
- Create `tests/test_review_coverage.py`: path-evidence and three-family coverage tests.

### Native provider transport

- Modify `bin/_common.py:55-87`: add the terminal `permission-unavailable` classification.
- Modify `bin/antigravity_wrapper.py:107-134,209-301,304-506,518-664`: remove sandbox/settings/bypass behavior and classify the observed native denial.
- Modify `bin/claude_wrapper.py:80-235`: remove wrapper permission arguments and generated Claude permission flags.
- Modify `bin/gemini_wrapper.py:50-182`: remove approval/sandbox policy arguments and generated Gemini permission flags.
- Delete `bin/_agy_settings.py`.
- Delete `bin/policies/gemini-readonly.toml`.
- Modify `tests/test_antigravity_packet_context.py`.
- Modify `tests/test_provider_packet_context.py`.
- Delete `tests/test_agy_settings.py`.
- Delete `tests/test_gemini_sandbox.py`.

### Plugin-owned permission-controller retirement

- Modify `bin/bootstrap_repair.py:16-50,97-123,1969-2245`: retain exact removal and generic transaction helpers; retire repair-agent installation/registration.
- Modify `scripts/bootstrap.sh:16-142,381-428,540-838,1086-1810,1834-2243`: install wrapper launchers only, clean exact legacy artifacts, and stop generating Codex permission state.
- Delete `agents/triad-repair-analyzer.toml`.
- Delete `migration/config-fragment.recommended.toml`.
- Delete `migration/requirements.recommended.toml`.
- Delete `migration/triad-codex-dispatch.rules`.
- Modify `migration/AGENTS.recommended.md`.
- Modify `tests/test_bootstrap.py`.
- Modify `tests/test_bootstrap_repair_transaction.py`.
- Modify `tests/test_migration_contract.py`.

### Review contract and distribution

- Modify `skills/triad-cross-family-review/SKILL.md`.
- Modify `skills/triad-cross-family-review/references/review-prompt-contract.md`.
- Modify `skills/triad-cross-family-review/references/reviewer-routing.md`.
- Modify `skills/triad-cross-family-review/references/fresh-codex-formal-review.md`.
- Modify `skills/triad-claude-dispatch/SKILL.md`.
- Modify `skills/triad-antigravity-dispatch/SKILL.md`.
- Modify `skills/triad-gemini-dispatch/SKILL.md`.
- Regenerate or update all four `skills/*/agents/openai.yaml` files only when their default prompts are stale.
- Modify `docs/references/repair-protocol.md`.
- Modify `tests/test_distribution_contract.py`.

### Public documentation and release

- Modify `README.md`.
- Modify `README.ko.md`.
- Modify `SECURITY.md`.
- Modify `CHANGELOG.md`.
- Modify `.codex-plugin/plugin.json`.
- Modify `docs/status/2026-07-22-current-state.md`.
- Modify `docs/status/2026-07-22-resume-prompt.md`.
- Create `docs/status/2026-07-30-v0.2.532-release-notes.md`.
- Preserve dated formal-round ledgers as historical records.

---

### Task 1: Deterministic Change-Evidence Preparation

**Files:**
- Create: `bin/review_evidence.py`
- Create: `tests/test_review_evidence.py`

**Interfaces:**
- Consumes: an immutable prepared review root, a captured unified diff file, and a leader-authored UTF-8 TSV with exact header `path	reason	reached_from`.
- Produces: `EvidenceSummary`, `CHANGESET.md`, `IMPACT_CLOSURE.tsv`, `PATCH_INDEX.tsv`, `MANIFEST.sha256`, deterministic patch shards, and batch manifests.
- Produces callable interfaces:

```python
@dataclass(frozen=True)
class ImpactRow:
    path: str
    reason: str
    reached_from: str
    content_sha256: str
    byte_count: int
    batch_id: str

@dataclass(frozen=True)
class PatchShard:
    patch_id: str
    group_id: str
    section_ordinal: int
    hunk_ordinal: int | None
    relative_path: str
    sha256: str
    byte_count: int

@dataclass(frozen=True)
class EvidenceSummary:
    format_version: int
    source_tree_digest: str
    change_evidence_digest: str
    affected_paths: tuple[ImpactRow, ...]
    patch_shards: tuple[PatchShard, ...]
    group_ids: tuple[str, ...]
    patch_file_count: int
    batch_ids: tuple[str, ...]

def prepare_review_evidence(
    review_root: Path,
    diff_file: Path,
    impact_input: Path,
    output_dir: Path,
    *,
    batch_byte_limit: int,
) -> EvidenceSummary: ...

def validate_review_evidence(
    review_root: Path,
    evidence_dir: Path,
) -> EvidenceSummary: ...
```

- CLI:

```text
python3 bin/review_evidence.py prepare \
  --review-root /private/tmp/triad-review-candidate \
  --diff-file /private/tmp/triad-review-input/candidate.diff \
  --impact-input /private/tmp/triad-review-input/impact-closure.tsv \
  --output-dir /private/tmp/triad-review-candidate/change-evidence \
  --batch-byte-limit 262144

python3 bin/review_evidence.py validate \
  --review-root /private/tmp/triad-review-candidate \
  --evidence-dir /private/tmp/triad-review-candidate/change-evidence
```

- The patch splitter treats `diff --git ` as a file-section boundary and `@@ ` as a hunk boundary. It carries the file header into each hunk shard and assigns ordinal IDs without interpreting shell syntax from path text.
- `PATCH_FILES_PER_GROUP = 100`. File sections 1-100 are `group-0001`,
  101-200 are `group-0002`, and so on; `GROUP_COUNT` is the exact number of
  non-empty groups. `PATCH_FILE_COUNT` counts file sections, while
  `patch_shards` may be larger when a section contains multiple hunks.
- Source files remain complete in the prepared root. An oversized file receives a single-path batch; provider file-read ranges may bound individual tool outputs, but every range remains required.

- [ ] **Step 1: Create the branch and record the Python boundary**

Run from `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`:

```bash
git switch -c release/0.2.532
git status -sb
```

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'command -v python3; python3 --version; python3 -m pytest --version'
```

Expected: branch `release/0.2.532`, clean worktree, literal `python3` resolves through the login shell, and pytest is available.

- [ ] **Step 2: Write the failing format and determinism tests**

Create `tests/test_review_evidence.py` with focused tests beginning with:

```python
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))

import review_evidence


def test_prepare_emits_named_headers_and_deterministic_batches(tmp_path: Path) -> None:
    review_root = tmp_path / "review root"
    source = review_root / "src" / "caller.py"
    source.parent.mkdir(parents=True)
    source.write_text("def caller():\n    return changed()\n", encoding="utf-8")
    diff_file = tmp_path / "change.diff"
    diff_file.write_text(
        "diff --git a/src/caller.py b/src/caller.py\n"
        "--- a/src/caller.py\n+++ b/src/caller.py\n"
        "@@ -1,2 +1,2 @@\n-def caller():\n+def caller():\n",
        encoding="utf-8",
    )
    impact = tmp_path / "impact.tsv"
    impact.write_text(
        "path\treason\treached_from\nsrc/caller.py\tchanged\t-\n",
        encoding="utf-8",
    )

    summary = review_evidence.prepare_review_evidence(
        review_root,
        diff_file,
        impact,
        review_root / "change-evidence",
        batch_byte_limit=262144,
    )

    changeset = (review_root / "change-evidence" / "CHANGESET.md").read_text()
    assert "FORMAT_VERSION=1\n" in changeset
    assert "GROUP_COUNT=1\n" in changeset
    assert "PATCH_FILE_COUNT=1\n" in changeset
    assert "AFFECTED_SOURCE_COUNT=1\n" in changeset
    assert "BATCH_COUNT=1\n" in changeset
    assert "SOURCE_TREE_DIGEST=" in changeset
    assert "CHANGE_EVIDENCE_DIGEST=" in changeset
    assert summary.group_ids == ("group-0001",)
    assert summary.patch_file_count == 1
    assert summary.batch_ids == ("batch-0001",)
    assert review_evidence.validate_review_evidence(
        review_root, review_root / "change-evidence"
    ) == summary


def test_prepare_rejects_symlinked_affected_source(tmp_path: Path) -> None:
    review_root = tmp_path / "review"
    review_root.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("secret = True\n", encoding="utf-8")
    (review_root / "linked.py").symlink_to(outside)
    diff_file = tmp_path / "change.diff"
    diff_file.write_bytes(b"")
    impact = tmp_path / "impact.tsv"
    impact.write_text(
        "path\treason\treached_from\nlinked.py\tchanged\t-\n",
        encoding="utf-8",
    )

    with pytest.raises(review_evidence.EvidenceError, match="regular file"):
        review_evidence.prepare_review_evidence(
            review_root,
            diff_file,
            impact,
            review_root / "change-evidence",
            batch_byte_limit=262144,
        )
```

Implement the following additional named tests in the same file:

- `test_prepare_rejects_duplicate_impact_paths`: repeat `src/caller.py` in the
  TSV and require `EvidenceError("duplicate affected path")`.
- `test_prepare_rejects_unsupported_impact_reason`: use `reason=guessed` and
  require `EvidenceError("unsupported impact reason")`.
- `test_prepare_rejects_traversal_path`: use `../outside.py` and require
  `EvidenceError("invalid review-relative path")`.
- `test_validate_rejects_source_digest_mutation`: prepare valid evidence,
  change the affected source bytes, and require
  `EvidenceError("source digest mismatch")`.
- `test_validate_rejects_missing_named_header`: remove
  `AFFECTED_SOURCE_COUNT` from `CHANGESET.md` and require
  `EvidenceError("missing CHANGESET header")`.
- `test_prepare_large_diff_is_deterministic_and_preserves_hostile_paths`:
  synthesize 12 groups and 1,200 file sections padded past 10,000,000 bytes;
  include relative paths containing a space, a single quote, a backtick, and
  the literal characters `$()`; prepare twice into separate roots and assert
  equal summaries, equal manifests, `group-0001` through `group-0012`,
  exactly 1,200 patch IDs, and absence of any filesystem marker named by the
  hostile path text.

- [ ] **Step 3: Run the evidence tests to verify RED**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_review_evidence.py'
```

Expected: collection fails with `ModuleNotFoundError: No module named 'review_evidence'`.

- [ ] **Step 4: Implement evidence preparation and validation**

Create `bin/review_evidence.py` with the exact dataclasses and call signatures above. Use:

```python
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
})


class EvidenceError(ValueError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_relative_path(raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute() or not candidate.parts or ".." in candidate.parts:
        raise EvidenceError(f"invalid review-relative path: {raw!r}")
    return candidate
```

Open inputs with no symlink following, reject non-regular files, sort impact rows by UTF-8 path bytes, pack them greedily into `batch-0001` onward, write all output through same-directory temporary files plus `os.replace`, and derive `MANIFEST.sha256` from every evidence file except itself. Validation reopens and rehashes the current source and every evidence artifact.

Define `source_tree_digest` as SHA-256 over canonical
`relative-path NUL file-sha256 NUL byte-count LF` records for every regular file
below `review_root` except `output_dir`, sorted by UTF-8 path bytes. Reject every
symlink encountered during that walk. Define `change_evidence_digest` with the
same record encoding over generated patch, index, closure, and batch artifacts
before `CHANGESET.md` and `MANIFEST.sha256` are written. Then
`MANIFEST.sha256` hashes every evidence artifact except itself, including the
completed `CHANGESET.md`; this ordering avoids a self-referential digest.

- [ ] **Step 5: Run focused and neighboring GREEN tests**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_review_evidence.py workspace/triad-codex-dispatch-reliability/tests/test_formal_review_schema.py'
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit the evidence module**

```bash
git add bin/review_evidence.py tests/test_review_evidence.py
git commit -m "feat: prepare deterministic review evidence"
```

### Task 2: Full-Family Coverage Admission

**Files:**
- Create: `bin/review_coverage.py`
- Create: `tests/test_review_coverage.py`

**Interfaces:**
- Consumes: a validated `EvidenceSummary` and JSON batch receipts.
- Produces:

```python
class PathEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    path: str
    content_sha256: str
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
    path_evidence: tuple[PathEvidence, ...]
    findings: tuple[dict[str, object], ...]
    unresolved_paths: tuple[str, ...]

@dataclass(frozen=True)
class FamilyCoverage:
    family: str
    receipt_digests: tuple[str, ...]
    covered_paths: tuple[str, ...]

@dataclass(frozen=True)
class CoverageAdmission:
    admitted: bool
    family_coverages: tuple[FamilyCoverage, ...]

def validate_family_receipts(
    evidence: EvidenceSummary,
    family: str,
    receipt_paths: Sequence[Path],
) -> FamilyCoverage: ...

def admit_full_coverage(
    evidence: EvidenceSummary,
    family_coverages: Sequence[FamilyCoverage],
) -> CoverageAdmission: ...
```

- A `changed` row requires at least one `changed_hunks` entry.
- An unchanged affected row requires at least one `verified_impact_edges` entry.
- `line_start` and `line_end` are both absent or both present. Every path
  requires a non-empty symbol tuple or a present positive line range satisfying
  `line_start <= line_end <= actual_file_line_count`.
- `disposition="unresolved"` or a non-empty `unresolved_paths` list blocks admission.

- [ ] **Step 1: Write failing three-family and path-evidence tests**

Create `tests/test_review_coverage.py` with:

```python
def test_admission_requires_every_path_from_every_family(evidence_fixture) -> None:
    evidence, receipt_factory = evidence_fixture
    coverages = [
        review_coverage.validate_family_receipts(
            evidence, family, receipt_factory(family)
        )
        for family in ("claude", "google", "codex")
    ]
    admission = review_coverage.admit_full_coverage(evidence, coverages)
    assert admission.admitted is True


def test_manifest_path_echo_without_source_grounding_is_rejected(
    evidence_fixture,
) -> None:
    evidence, receipt_factory = evidence_fixture
    receipts = receipt_factory(
        "claude",
        symbols=(),
        line_start=None,
        line_end=None,
    )
    with pytest.raises(
        review_coverage.CoverageError,
        match="source-grounded path evidence",
    ):
        review_coverage.validate_family_receipts(
            evidence, "claude", receipts
        )


def test_new_affected_path_invalidates_the_round(evidence_fixture) -> None:
    evidence, receipt_factory = evidence_fixture
    receipts = receipt_factory("claude", extra_path="src/new_consumer.py")
    with pytest.raises(review_coverage.CoverageError, match="absent from closure"):
        review_coverage.validate_family_receipts(
            evidence, "claude", receipts
        )
```

Implement these named tests with `evidence_fixture` and require
`CoverageError` with the shown stable diagnostic:

- `test_missing_batch_is_rejected` -> `missing batch receipt`;
- `test_duplicate_batch_receipt_is_rejected` -> `duplicate batch receipt`;
- `test_receipt_digest_mismatch_is_rejected` -> `evidence digest mismatch`;
- `test_changed_path_without_hunk_evidence_is_rejected` ->
  `changed path lacks hunk evidence`;
- `test_affected_unchanged_path_without_edge_is_rejected` ->
  `affected path lacks impact-edge evidence`;
- `test_unresolved_disposition_is_rejected` -> `unresolved path`;
- `test_admission_rejects_duplicate_family` -> `duplicate family coverage`;
- `test_admission_rejects_missing_family` -> `missing family coverage`.

- [ ] **Step 2: Run the coverage tests to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py'
```

Expected: collection fails because `review_coverage` does not exist.

- [ ] **Step 3: Implement strict coverage models and admission**

Create `bin/review_coverage.py`. Validate JSON with Pydantic 2 strict models, compute receipt SHA-256 from the original bytes, require exact batch and path sets, and compare every receipt digest with `EvidenceSummary`. Raise `CoverageError` on the first deterministic mismatch and never coerce strings to numbers.

- [ ] **Step 4: Run focused GREEN tests**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py workspace/triad-codex-dispatch-reliability/tests/test_review_evidence.py'
```

Expected: all tests pass.

- [ ] **Step 5: Commit coverage admission**

```bash
git add bin/review_coverage.py tests/test_review_coverage.py
git commit -m "feat: require full-family source coverage"
```

### Task 3: Native AGY Permissions and Fail-Closed Denial

**Files:**
- Modify: `bin/_common.py:55-87`
- Modify: `bin/antigravity_wrapper.py:107-134,209-301,304-506,518-664`
- Modify: `tests/test_antigravity_packet_context.py`
- Delete: `bin/_agy_settings.py`
- Delete: `tests/test_agy_settings.py`

**Interfaces:**
- `_build_route_args(model: str | None, effort: str | None) -> list[str]`
- `_build_cmd(prompt, sentinel, model, timeout, *, effort=None, pydantic=False) -> list[str]`
- `_is_headless_softdeny(text: str) -> bool` remains the exact empirical detector.
- `map_classification_to_exit("permission-unavailable") == EXIT_TERMINAL`.

- [ ] **Step 1: Replace the auto-approve regression with failing native-mode tests**

Replace `test_formal_autoapprove_keeps_sandbox_and_readonly_deny_guard` with:

```python
def test_native_headless_permission_denial_is_terminal_without_retry(
    monkeypatch,
) -> None:
    calls: list[list[str]] = []
    sentinel = "AGY_DONE_" + "8" * 32

    def deny_once(cmd, **_kwargs):
        calls.append(list(cmd))
        return wrapper._pty.PtyResult(
            b'jetski: no output produced -- a tool required the "command" '
            b"permission that headless mode cannot prompt for, so it was auto-denied.\n",
            0,
            False,
        )

    monkeypatch.setattr(wrapper._common, "snapshot_agy_transcripts", lambda: {})
    monkeypatch.setattr(wrapper._pty, "run_via_pty", deny_once)
    result = wrapper._run_agy_with_retry(
        ["agy", "-p", "review"],
        "review",
        30,
        expected_sentinel=sentinel,
    )

    assert len(calls) == 1
    assert "--dangerously-skip-permissions" not in calls[0]
    assert "--sandbox" not in calls[0]
    assert result.classification == "permission-unavailable"
    assert result.exit_code == wrapper._common.EXIT_TERMINAL


def test_route_builder_contains_only_selector_and_effort() -> None:
    assert wrapper._build_route_args("Gemini 3.1 Pro (High)", None) == [
        "--model",
        "Gemini 3.1 Pro (High)",
    ]
```

Remove test fixtures and monkeypatches that reference `_agy_settings`, sandbox modes, `_agy_needs_skip_permissions`, or `AGY_NO_HEADLESS_AUTOAPPROVE`.

- [ ] **Step 2: Run the AGY tests to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_antigravity_packet_context.py -k "native_headless_permission_denial or route_builder_contains_only"'
```

Expected: the first test observes a second bypass retry or a non-terminal classification, and the route-builder signature does not match.

- [ ] **Step 3: Remove AGY permission control and add terminal classification**

Delete `_add_skip_permissions`, `_agy_needs_skip_permissions`, version-floor logic, `--sandbox`, settings-lock handling, `_agy_settings` imports/guards, and every `skip_permissions`/`agy_sandbox` parameter. In the no-answer path, add:

```python
if _is_headless_softdeny(scrubbed):
    return finish(
        None,
        "permission-unavailable",
        _common.EXIT_TERMINAL,
        result.rc,
        scrubbed_output=scrubbed,
        extraction_error="native headless permission unavailable",
    )
```

Add `"permission-unavailable": EXIT_TERMINAL` to `map_classification_to_exit`.

- [ ] **Step 4: Delete retired settings code and run GREEN tests**

Delete `bin/_agy_settings.py` and `tests/test_agy_settings.py`, then run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_antigravity_packet_context.py workspace/triad-codex-dispatch-reliability/tests/test_log_cleanup.py'
```

Expected: all selected tests pass and `rg "_agy_settings|dangerously-skip-permissions|AGY_NO_HEADLESS_AUTOAPPROVE" bin tests` returns no active-code hit.

- [ ] **Step 5: Commit native AGY behavior**

```bash
git add bin/_common.py bin/antigravity_wrapper.py tests/test_antigravity_packet_context.py
git add -u bin/_agy_settings.py tests/test_agy_settings.py
git commit -m "fix: inherit native agy permissions"
```

### Task 4: Native Claude and Gemini Permissions

**Files:**
- Modify: `bin/claude_wrapper.py:80-235`
- Modify: `bin/gemini_wrapper.py:50-182`
- Modify: `tests/test_provider_packet_context.py`
- Delete: `bin/policies/gemini-readonly.toml`
- Delete: `tests/test_gemini_sandbox.py`

**Interfaces:**
- Claude forwards only prompt, output format, optional model, optional effort, optional fallback model, cwd, timeout, schema, packet-compatibility, repair, and debug controls.
- Gemini forwards only prompt, output format, optional model, optional skip-trust, cwd, timeout, schema, packet-compatibility, repair, and debug controls.
- Removed wrapper arguments are rejected by `argparse` rather than translated.

- [ ] **Step 1: Write failing argv tests**

Add to `tests/test_provider_packet_context.py`:

```python
@pytest.mark.parametrize(
    ("module", "forbidden"),
    [
        (
            claude_wrapper,
            {
                "--sandbox",
                "--permission-mode",
                "--tools",
                "--strict-mcp-config",
                "--setting-sources",
            },
        ),
        (
            gemini_wrapper,
            {"--sandbox", "--approval-mode", "--policy"},
        ),
    ],
)
def test_native_wrapper_argv_has_no_permission_override(
    module,
    forbidden,
    monkeypatch,
) -> None:
    captured: dict[str, list[str]] = {}

    def capture(_cli, build_cmd, prompt, **_kwargs):
        captured["argv"] = build_cmd(prompt)
        return _common.RunResult(
            _common.EXIT_OK,
            "ok",
            "",
            0.0,
            final_answer="ok",
        )

    monkeypatch.setattr(module, "require_binary", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(module, "run_cli_with_retry", capture)
    monkeypatch.setattr(module, "persist_result_artifacts", lambda *_a, **_k: None)
    monkeypatch.setattr(sys, "argv", [module.__file__, "--prompt", "review"])

    assert module.main() == 0
    assert forbidden.isdisjoint(captured["argv"])
```

- [ ] **Step 2: Run the wrapper argv test to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_provider_packet_context.py -k native_wrapper_argv'
```

Expected: Claude or Gemini argv contains a generated permission flag.

- [ ] **Step 3: Remove wrapper permission arguments and policy injection**

Delete Claude's `--sandbox`, `--permission-mode`, `TRIAD_CLAUDE_ENFORCE_SANDBOX`, and generated tool/config/permission flags. Delete Gemini's `--approval-mode`, `--sandbox`, policy constant, hardened default, and generated `--policy`/approval flags. Preserve `--skip-trust` because it controls workspace trust, not tool permission.

- [ ] **Step 4: Delete retired policy tests and run GREEN tests**

Delete `bin/policies/gemini-readonly.toml` and `tests/test_gemini_sandbox.py`. Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_provider_packet_context.py workspace/triad-codex-dispatch-reliability/tests/test_formal_review_schema.py'
```

Expected: all selected tests pass.

- [ ] **Step 5: Commit native Claude/Gemini behavior**

```bash
git add bin/claude_wrapper.py bin/gemini_wrapper.py tests/test_provider_packet_context.py
git add -u bin/policies/gemini-readonly.toml tests/test_gemini_sandbox.py
git commit -m "fix: inherit native provider permissions"
```

### Task 5: Retire the Read-Only Repair Custom Agent

**Files:**
- Modify: `docs/references/repair-protocol.md`
- Modify: `bin/bootstrap_repair.py:16-50,97-123,1969-2245`
- Modify: `scripts/bootstrap.sh:381-428,650-838,1908-2040,2180-2243`
- Modify: `tests/test_bootstrap.py`
- Modify: `tests/test_bootstrap_repair_transaction.py`
- Modify: `tests/test_distribution_contract.py`
- Delete: `agents/triad-repair-analyzer.toml`

**Interfaces:**
- Repair analysis uses native `spawn_agent` with `fork_turns="none"`, explicit current router model, medium effort, omitted `agent_type`, and the existing untrusted JSON envelope.
- Repair apply uses the plugin's `bin/apply_patch.py` through literal login-shell `python3`; no installed `triad-apply-repair` launcher is required.
- Upgrade cleanup removes only the exact managed analyzer registration, analyzer TOML, and apply launcher.

- [ ] **Step 1: Write failing distribution and cleanup tests**

In `tests/test_distribution_contract.py`, replace exact-agent assertions with:

```python
def test_repair_protocol_uses_fresh_native_child_without_custom_agent() -> None:
    protocol = _text(PROTOCOL)
    assert 'fork_turns="none"' in protocol
    assert "model=" in protocol
    assert "reasoning_effort=" in protocol
    assert "agent_type=" not in protocol
    assert "triad-repair-analyzer" not in protocol
    assert not REPAIR_AGENT.exists()
    assert "/bin/zsh" in protocol
    assert "python3" in protocol
    assert "bin/apply_patch.py" in protocol
```

In `tests/test_bootstrap.py`, add:

```python
def test_install_removes_only_exact_legacy_repair_agent_artifacts(
    tmp_path: Path,
) -> None:
    repo_root = _make_repo_root(tmp_path, real_agents=True)
    helper = _load_bootstrap_repair_module()
    codex_home = tmp_path / "home" / ".codex"
    agents = codex_home / "agents"
    agents.mkdir(parents=True)
    analyzer = agents / f"{REPAIR_ANALYZER}.toml"
    analyzer.write_text(
        f"{helper.ANALYZER_MARKER}\nname = \"{REPAIR_ANALYZER}\"\n",
        encoding="utf-8",
    )
    config = codex_home / "config.toml"
    config.write_text(helper.registration_block(analyzer, False), encoding="utf-8")
    launcher = tmp_path / "launchers" / "triad-apply-repair"
    launcher.parent.mkdir()
    launcher.write_text(
        "#!/usr/bin/python3 -E\n"
        f"{helper.LAUNCHER_MARKER}\n"
        "import os\n"
        "import sys\n"
        "os.execv('/usr/bin/python3', ['/usr/bin/python3', "
        "'/managed/apply_patch.py'] + sys.argv[1:])\n",
        encoding="utf-8",
    )
    launcher.chmod(0o755)
    foreign = agents / "foreign.toml"
    foreign.write_text('name = "foreign"\n', encoding="utf-8")

    result, _env, _launcher_dir = _run_bootstrap(
        tmp_path,
        repo_root=repo_root,
        env_overrides={"CODEX_HOME": str(codex_home)},
        arg="--install",
    )

    assert result.returncode == 0, result.stderr
    assert not config.exists()
    assert not analyzer.exists()
    assert not launcher.exists()
    assert foreign.read_text(encoding="utf-8") == 'name = "foreign"\n'
```

Use the production ownership parser for the registration block and the
production marker constants. The test's five-line launcher is the legacy
managed form already accepted by `launcher_is_managed`; do not add a second
removal predicate.

- [ ] **Step 2: Run focused tests to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k repair_protocol_uses_fresh_native_child workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py -k removes_only_exact_legacy_repair_agent_artifacts'
```

Expected: the protocol still names the registered agent and bootstrap still installs it.

- [ ] **Step 3: Rewrite the repair protocol**

Keep the fenced JSON envelope and proposal schema. Replace the Custom Agent call with:

```python
spawn_agent(
    task_name=f"repair_analyzer_{token_hex(8)}",
    fork_turns="none",
    model="gpt-5.6-terra",
    reasoning_effort="medium",
    message=repair_message,
)
```

State that the child inherits the parent session's active permission mode, its proposal-only/no-edit behavior is prompt-controlled, and a mutation invalidates the analysis. Build the owner apply command from:

```python
owner_argv = [
    "/bin/zsh",
    "-lic",
    shlex.join([
        "python3",
        str(toolkit_root / "bin" / "apply_patch.py"),
        "--cli",
        cli,
        "--proposal-file",
        proposal_path,
    ]),
]
```

- [ ] **Step 4: Make bootstrap repair-agent support remove-only**

Remove `install`, `preflight-install`, analyzer source validation, analyzer registration creation, and installed apply-launcher creation from `bin/bootstrap_repair.py`. Retain the exact managed `remove` path and generic transaction helpers required to clean old installations.

Change `scripts/bootstrap.sh --install` to invoke exact repair cleanup before installing wrapper launchers. A foreign registration, analyzer, or launcher is reported and preserved. Delete the shipped analyzer TOML.

- [ ] **Step 5: Prune obsolete tests and run GREEN tests**

Remove tests whose only contract is installing, refreshing, or selecting the read-only analyzer. Retain and rename exact-removal, foreign-preservation, rollback, symlink-refusal, and transaction-integrity tests.

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py workspace/triad-codex-dispatch-reliability/tests/test_bootstrap_repair_transaction.py workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k "repair or analyzer or bootstrap_repair"'
```

Expected: selected tests pass and no shipped/installed read-only repair agent remains.

- [ ] **Step 6: Commit repair-agent retirement**

```bash
git add docs/references/repair-protocol.md bin/bootstrap_repair.py scripts/bootstrap.sh tests/test_bootstrap.py tests/test_bootstrap_repair_transaction.py tests/test_distribution_contract.py
git add -u agents/triad-repair-analyzer.toml
git commit -m "refactor: use native repair children"
```

### Task 6: Remove Plugin-Owned Permission Profiles, Rules, and Migration Templates

**Files:**
- Modify: `scripts/bootstrap.sh:16-142,540-650,1086-1810,1834-1935,2180-2243`
- Modify: `bin/bootstrap_repair.py:23-43,652-772,1411-1520,2163-2245`
- Modify: `migration/AGENTS.recommended.md`
- Modify: `tests/test_bootstrap.py`
- Modify: `tests/test_bootstrap_repair_transaction.py`
- Modify: `tests/test_migration_contract.py`
- Delete: `migration/config-fragment.recommended.toml`
- Delete: `migration/requirements.recommended.toml`
- Delete: `migration/triad-codex-dispatch.rules`

**Interfaces:**
- `scripts/bootstrap.sh --install` installs/refreshes only wrapper launchers and non-permission runtime support, after exact cleanup of prior plugin-owned policy artifacts.
- `scripts/bootstrap.sh --remove` removes exact managed launchers and exact legacy plugin-owned artifacts.
- No install option or environment variable can create a Codex profile, rule, shell entry, config fragment, or permission requirement.

- [ ] **Step 1: Write failing native-install and migration-absence tests**

Add or replace tests with:

```python
def test_native_install_does_not_create_codex_permission_state(tmp_path: Path) -> None:
    result, env, _launcher_dir = _run_bootstrap(tmp_path, arg="--install")
    codex_home = Path(env["HOME"]) / ".codex"

    assert result.returncode == 0, result.stderr
    assert not (codex_home / "triad-codex-dispatch.config.toml").exists()
    assert not (codex_home / "rules" / "triad-codex-dispatch.rules").exists()
    assert not (codex_home / "agents" / "triad-repair-analyzer.toml").exists()
    config = codex_home / "config.toml"
    assert not config.exists() or "triad-codex-dispatch managed" not in config.read_text()


def test_distribution_has_no_permission_migration_templates() -> None:
    migration = ROOT / "migration"
    assert not (migration / "config-fragment.recommended.toml").exists()
    assert not (migration / "requirements.recommended.toml").exists()
    assert not (migration / "triad-codex-dispatch.rules").exists()
```

- [ ] **Step 2: Run focused tests to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py -k native_install_does_not_create_codex_permission_state workspace/triad-codex-dispatch-reliability/tests/test_migration_contract.py'
```

Expected: default installation creates rules and the migration tests require the templates.

- [ ] **Step 3: Remove permission-generation paths**

Delete profile/rules selection, preflight, generation, config-fragment merge, requirements guidance, shell-entry installation, and Agent Review/sandbox messaging from `scripts/bootstrap.sh`. Keep exact ownership inspectors/removers in `bootstrap_repair.py` only as needed for upgrade cleanup.

On both `--install` and `--remove`, clean exact legacy artifacts in this order:

1. repair registration/analyzer/apply launcher;
2. plugin-owned rules;
3. plugin-owned profile;
4. exact managed config fragment;
5. exact managed shell entry.

A foreign or edited artifact is preserved and reported without broadening the removal predicate.

- [ ] **Step 4: Delete migration templates and update developer guidance**

Delete the three permission templates. Rewrite `migration/AGENTS.recommended.md` to recommend the same authenticated login terminal/worktree as development and state that TRIAD inherits provider permissions without changing them.

- [ ] **Step 5: Prune obsolete policy-install tests and run GREEN tests**

Remove tests for optional profile/rules/config/shell installation. Retain tests for exact cleanup, foreign preservation, symlink refusal, rollback, launcher installation, reinstall idempotence, Python boundary, and provider binaries not being invoked during install.

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py workspace/triad-codex-dispatch-reliability/tests/test_bootstrap_repair_transaction.py workspace/triad-codex-dispatch-reliability/tests/test_migration_contract.py'
```

Expected: all tests pass.

- [ ] **Step 6: Commit permission-controller removal**

```bash
git add scripts/bootstrap.sh bin/bootstrap_repair.py migration/AGENTS.recommended.md tests/test_bootstrap.py tests/test_bootstrap_repair_transaction.py tests/test_migration_contract.py
git add -u migration/config-fragment.recommended.toml migration/requirements.recommended.toml migration/triad-codex-dispatch.rules
git commit -m "refactor: remove plugin permission policy"
```

### Task 7: Update the Skills for Native Permissions and Full Coverage

**Files:**
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `skills/triad-cross-family-review/references/review-prompt-contract.md`
- Modify: `skills/triad-cross-family-review/references/reviewer-routing.md`
- Modify: `skills/triad-cross-family-review/references/fresh-codex-formal-review.md`
- Modify: `skills/triad-claude-dispatch/SKILL.md`
- Modify: `skills/triad-antigravity-dispatch/SKILL.md`
- Modify: `skills/triad-gemini-dispatch/SKILL.md`
- Modify when stale: `skills/*/agents/openai.yaml`
- Modify: `tests/test_distribution_contract.py`

**Interfaces:**
- Formal prompt fields add `source_tree_digest`, `change_evidence_digest`, `batch_id`, `batch_manifest`, and the required `path_evidence` shape.
- Each family must cover the exact batch set.
- A new affected path invalidates the complete round.
- Provider examples omit every permission-control flag.

- [ ] **Step 1: Load the skill-writing contracts and write failing distribution tests**

Use `superpowers:writing-skills`, `superpowers:test-driven-development`, `skill-creator`, and `skill-prompt-review` before editing skill files.

Add tests:

```python
def test_formal_review_requires_full_family_batch_matrix_and_path_evidence() -> None:
    contract = "\n".join(
        _text(path)
        for path in (
            REVIEW_SKILL,
            REVIEW_PROMPT_REFERENCE,
            FRESH_CODEX_REVIEW_REFERENCE,
        )
    )
    for literal in (
        "source_tree_digest",
        "change_evidence_digest",
        "batch_id",
        "path_evidence",
        "Every required family reviews every batch",
        "A manifest path alone is not coverage",
    ):
        assert literal in contract


def test_provider_skill_examples_inherit_native_permissions() -> None:
    combined = "\n".join(_text(path) for path in PROVIDER_SKILLS)
    for forbidden in (
        "--sandbox",
        "--permission-mode",
        "--approval-mode",
        "--dangerously-skip-permissions",
        "triad-repair-analyzer",
    ):
        assert forbidden not in combined
    assert "same authenticated login terminal" in combined
```

- [ ] **Step 2: Run distribution tests to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k "full_family_batch_matrix or inherit_native_permissions"'
```

Expected: the full-coverage fields are missing and provider examples still contain `--sandbox`.

- [ ] **Step 3: Rewrite the cross-family and provider contracts**

Keep `SKILL.md` as the concise workflow entry point. Move format detail into the existing references. Require:

- leader preparation through `review_evidence.py`;
- validation before dispatch;
- all families over all batches;
- complete current source for changed and affected unchanged files;
- source-grounded `path_evidence`;
- invalidation on newly discovered paths;
- coverage admission through `review_coverage.py`;
- native permission inheritance;
- `permission-unavailable` as an invalid required leg; and
- fresh complete reruns after closure changes.

Provider argv examples contain only prompt-file, cwd, selector, effort where
applicable, and result controls. Keep stable instructions before batch-specific
paths and digests so provider caches can reuse the prefix. Permit separate fresh
contexts per batch, require each family to finish every batch, address repeated
content by the same digest, and retain only compact receipts between contexts.
Cheap transport probes may use cheap routes; formal gates keep the
owner-authorized full-quality route. No batching rule may sample or skip a
source path.

- [ ] **Step 4: Validate metadata and run skill/prompt lint**

Regenerate `agents/openai.yaml` only if the default prompt no longer matches the skill. Run the skill validator and prompt linter from the login-shell Python environment:

```bash
/bin/zsh -lic 'python3 /Users/chaniri/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review'
/bin/zsh -lic '
for target in \
  /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/SKILL.md \
  /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/review-prompt-contract.md \
  /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/reviewer-routing.md \
  /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/fresh-codex-formal-review.md \
  /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-claude-dispatch/SKILL.md \
  /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-antigravity-dispatch/SKILL.md \
  /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-gemini-dispatch/SKILL.md
do
  python3 /Users/chaniri/.codex/skills/skill-prompt-review/scripts/lint.py "$target" \
    /Users/chaniri/.codex/skills/skill-prompt-review/references/common.md \
    /Users/chaniri/.codex/skills/skill-prompt-review/references/openai.md \
    /Users/chaniri/.codex/skills/skill-prompt-review/references/anthropic.md \
    /Users/chaniri/.codex/skills/skill-prompt-review/references/google.md \
    /Users/chaniri/.codex/skills/skill-prompt-review/references/ai-authorship.md
done'
```

Expected: validation succeeds and every mechanical candidate is adjudicated or fixed.

- [ ] **Step 5: Run GREEN distribution tests**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py'
```

Expected: all distribution tests pass.

- [ ] **Step 6: Commit the skill contract**

```bash
git add \
  skills/triad-cross-family-review/SKILL.md \
  skills/triad-cross-family-review/references/review-prompt-contract.md \
  skills/triad-cross-family-review/references/reviewer-routing.md \
  skills/triad-cross-family-review/references/fresh-codex-formal-review.md \
  skills/triad-cross-family-review/agents/openai.yaml \
  skills/triad-claude-dispatch/SKILL.md \
  skills/triad-claude-dispatch/agents/openai.yaml \
  skills/triad-antigravity-dispatch/SKILL.md \
  skills/triad-antigravity-dispatch/agents/openai.yaml \
  skills/triad-gemini-dispatch/SKILL.md \
  skills/triad-gemini-dispatch/agents/openai.yaml \
  tests/test_distribution_contract.py
git commit -m "feat: require full-coverage triad review"
```

### Task 8: Public Documentation, Release Metadata, and Complete Verification

**Files:**
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `SECURITY.md`
- Modify: `CHANGELOG.md`
- Modify: `.codex-plugin/plugin.json`
- Modify: `docs/status/2026-07-22-current-state.md`
- Modify: `docs/status/2026-07-22-resume-prompt.md`
- Create: `docs/status/2026-07-30-v0.2.532-release-notes.md`

**Interfaces:**
- Public recommendation: run TRIAD from the same authenticated login terminal and worktree used for development.
- Security statement: permission selection belongs to the provider/user/project; TRIAD retains data, executable, digest, mutation, and result-custody boundaries.
- Version: `0.2.532`.

- [ ] **Step 1: Write failing release-contract tests**

Update `tests/test_distribution_contract.py`:

```python
def test_02532_public_contract_is_native_and_full_coverage() -> None:
    manifest = json.loads(_text(PLUGIN_MANIFEST))
    english = " ".join(_text(ROOT / "README.md").split())
    korean = " ".join(_text(ROOT / "README.ko.md").split())
    security = " ".join(_text(SECURITY).split())
    changelog = _text(CHANGELOG)

    assert manifest["version"] == "0.2.532"
    assert changelog.startswith("# Changelog\n\n## 0.2.532")
    assert "same authenticated login terminal" in english
    assert "동일한 인증된 로그인 터미널" in korean
    assert "does not select or override a permission mode" in security
    assert "every required family reviews every affected production source" in english
```

- [ ] **Step 2: Run the release-contract test to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k 02532_public_contract'
```

Expected: manifest remains `0.2.531` and the public native/full-coverage language is absent.

- [ ] **Step 3: Update English, Korean, security, status, and release metadata**

Document:

- native permission inheritance and no hidden override;
- native AGY headless fail-closed behavior and narrow user/project remediation;
- full diff plus complete affected-source closure;
- all-family/all-batch coverage;
- source-grounded path evidence;
- exact plugin-owned legacy cleanup and owner-setting preservation;
- the `0.2.532` migration from removed wrapper flags; and
- fresh-session verification requirements.

State the evidence limit precisely: provider-native file-read telemetry is
retained and digest-bound when exposed; otherwise coverage is prompt-controlled
and admitted through source-grounded receipts, independent family review, and
leader reproduction, not claimed as provider-enforced proof.

Mark prior `0.2.529`/`0.2.531` status facts as historical where they remain in current handoff documents. Do not rewrite dated formal-round ledgers.
Write the exact verified release summary and gate evidence to
`docs/status/2026-07-30-v0.2.532-release-notes.md`; this file is also the PR
body.

- [ ] **Step 4: Run documentation and release GREEN tests**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py workspace/triad-codex-dispatch-reliability/tests/test_migration_contract.py'
```

Expected: all selected tests pass.

- [ ] **Step 5: Commit the release candidate**

```bash
git add \
  README.md \
  README.ko.md \
  SECURITY.md \
  CHANGELOG.md \
  .codex-plugin/plugin.json \
  docs/status/2026-07-22-current-state.md \
  docs/status/2026-07-22-resume-prompt.md \
  docs/status/2026-07-30-v0.2.532-release-notes.md \
  tests/test_distribution_contract.py
git commit -m "release: 0.2.532"
```

- [ ] **Step 6: Run the complete local verification suite**

From `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests'
```

From the repository:

```bash
bash -n scripts/bootstrap.sh
git diff --check
git diff --cached --check
```

Expected: complete pytest suite passes, Bash syntax passes, and both diff checks are clean.

- [ ] **Step 7: Run the hostile-path and large-diff behavior proof**

Run the deterministic fixtures that construct the 12-group, 1,200-section,
10,000,000-byte diff, hostile paths, non-routine impact edge, oversized source,
complete three-family receipts, and one deliberately incomplete receipt:

```bash
/bin/zsh -lic 'python3 -m pytest -q \
  workspace/triad-codex-dispatch-reliability/tests/test_review_evidence.py::test_prepare_large_diff_is_deterministic_and_preserves_hostile_paths \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_admission_requires_every_path_from_every_family \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_manifest_path_echo_without_source_grounding_is_rejected \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_admission_rejects_missing_family'
```

Record the fixture's pre/post source-tree digest and evidence digest in the
release notes.

Expected: complete evidence admits, missing evidence fails, no hostile path executes, and the pre/post review-root digest is unchanged.

- [ ] **Step 8: Run the mandatory pre-merge three-family candidate review**

Prepare one immutable candidate directory containing current approved
production source, configuration, documentation, `change-evidence`, and the
exact owner/project test-source boundary. Record its digest and the canonical
worktree fingerprint before dispatch.

Dispatch:

- current owner-authorized Claude Opus route;
- current accepted Google-family Pro High route without a TRIAD permission override; and
- fresh Codex default child with `fork_turns="none"` and the current approved formal-review model/effort.

Every family reviews every batch and returns valid receipts. If native AGY reports `permission-unavailable`, stop the formal gate and report the required user/project permission decision; do not insert a bypass or count a different family twice.

Expected: three valid family coverages, no unresolved path, identical pre/post
candidate digest, identical pre/post canonical-worktree fingerprint, and either
three `SAFE` verdicts or a stopped release with evidence-backed findings.

- [ ] **Step 9: Correct accepted findings through new RED/GREEN cycles**

For each reproduced defect or approved underspecification, add one focused failing test, implement the minimum correction, run neighboring tests, and commit. If candidate bytes change, rebuild evidence and run a fresh complete three-family round.

Expected: no finding is applied solely because a provider requested it, and no changed candidate reuses a prior verdict.

- [ ] **Step 10: Install and prove the fresh plugin catalog**

Run the installed bootstrap through the authenticated login environment, compare source/cache hashes, and start a fresh ephemeral Codex session:

```bash
codex plugin list --json
scripts/bootstrap.sh --install
codex exec --ephemeral 'Return exactly TRIAD_02532_NATIVE_FULL_COVERAGE if the installed triad-cross-family-review skill requires native permission inheritance and all-family full affected-source coverage.'
```

Expected: source/cache hashes match and fresh output is exactly `TRIAD_02532_NATIVE_FULL_COVERAGE`.

- [ ] **Step 11: Publish the verified release**

After all gates pass:

```bash
git status -sb
git push -u origin release/0.2.532
gh pr create --base main --head release/0.2.532 --title "Release 0.2.532" --body-file docs/status/2026-07-30-v0.2.532-release-notes.md
gh pr checks --watch
```

Merge only after required checks succeed, then create/publish `v0.2.532` through the repository's existing release workflow. Record the merge commit, tag/release URL, installed source/cache hashes, and fresh-session proof in the current-state handoff.

Expected: remote branch, passing PR checks, merged release, published `v0.2.532`, and matching installed/fresh-session evidence.
