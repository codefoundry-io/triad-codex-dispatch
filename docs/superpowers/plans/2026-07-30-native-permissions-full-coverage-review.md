# Native Permissions and Full-Coverage Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make TRIAD inherit the developer's active provider permissions and require every model family to review every changed and affected production source with digest-bound per-path evidence.

**Architecture:** Add two focused Python modules: one prepares and validates immutable change evidence, and one validates per-family coverage receipts. Remove wrapper and bootstrap permission-controller behavior while retaining data authorization, executable/path validation, mutation detection, result custody, and explicit legacy packet compatibility.

**Tech Stack:** Python 3.12, Pydantic 2, pytest, Bash 3.2-compatible bootstrap, Markdown skills and public documentation, Codex plugin manifest.

## Global Constraints

- Work in `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`.
- The root leader commits the final approved plan correction on the current
  clean `release/0.2.530` planning branch and records that HEAD before Task 1.
  Create `release/0.2.532` from that exact commit before production edits and
  verify `1744c43c52b80cf2e28201a1c67d50611480f760` is its ancestor.
- Preserve the pre-existing commits and unrelated user-owned files.
- Run every direct `python3` command from `/Users/chaniri/codex_workspace` through `/bin/zsh -lic`, after recording `command -v python3`, `python3 --version`, and `python3 -m pytest --version`.
- Use TDD for every behavior change: run the focused RED test, confirm the expected failure, implement the minimum change, then run focused and neighboring GREEN tests.
- Every formal-review family covers every deterministic batch. Family perspectives never partition source coverage.
- A manifest path alone is not coverage. Each non-empty non-deleted path
  requires the exact full-file line range and changed-hunk or impact-edge
  disposition. It also requires a validated source observation absent from
  visible manifests unless the validator proves the complete source is
  whitespace-only. A validator-proven zero-byte current source has neither
  range nor observation.
- TRIAD never adds sandbox, permission-mode, yolo, bypass, accept-edits, auto-edit, dont-ask, or equivalent provider controls.
- The owner-approved native boundary also removes wrapper-injected Claude tool
  allowlists/settings-source/MCP policy, AGY sandbox selection, Gemini policy,
  and the plugin-managed pre-spawn shell environment policy. Retained mutation
  control means immutable snapshot plus digest/fingerprint detection and
  invalidation, not provider-enforced read-only containment.
- Native AGY headless permission denial is terminal `permission-unavailable`; it is never retried with broader authority.
- The only permission-denial detector added in this release is the empirically
  observed native AGY headless denial; Claude and Gemini receive no speculative
  message detector.
- Formal reviewers do not execute candidate code, tests, builds, hooks, or generated scripts.
- Exact owner-authored provider settings, Codex approval/reviewer settings, credentials, rules, and unrelated files remain unchanged.
- Plugin-owned legacy permission artifacts are removed only after exact marker/content ownership validation.
- Keep legacy packet validation reachable only from its existing explicit compatibility arguments.
- Keep `FormalReview` normative only for those legacy sealed-packet callers.
  `BatchReceipt` is normative only for the new batched full-coverage route;
  neither schema is an alternate admission path for the other.
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

The pre-implementation native source-observation transport spike is complete
and recorded in
`docs/status/2026-07-30-native-source-observation-spike.md`. Claude, AGY, and
fresh Codex each returned the exact generated source observation without
mutation. The AGY negative control proved that provider-side command hashing is
not a viable common requirement.

## File Map

### New focused modules

- Create `bin/review_evidence.py`: deterministic evidence preparation, parsing, hashing, batching, validation, and CLI.
- Create `bin/review_coverage.py`: Pydantic receipt models and full-family admission.
- Create `tests/test_review_evidence.py`: evidence-format, hostile-path, digest, and large-diff tests.
- Create `tests/test_review_coverage.py`: path-evidence and three-family coverage tests.

### Native provider transport

- Modify `bin/_common.py:55-87,296-297,398-406,2492-2497`: add the terminal `permission-unavailable` classification, keep custody/source comments current, and remove the stale legacy shell-entry activation description.
- Modify `bin/antigravity_wrapper.py:1-60,107-134,209-301,304-506,518-790`: remove sandbox/settings/bypass behavior and classify the observed native denial.
- Modify `bin/claude_wrapper.py:1-235`: remove wrapper permission arguments, their orphaned constants, and generated Claude permission flags.
- Modify `bin/gemini_wrapper.py:1-182`: remove approval/sandbox policy arguments, orphaned imports, and generated Gemini permission flags.
- Delete `bin/_agy_settings.py`.
- Delete `bin/policies/gemini-readonly.toml`.
- Modify `tests/test_antigravity_packet_context.py`.
- Modify `tests/test_provider_packet_context.py`.
- Delete `tests/test_agy_settings.py`.
- Delete `tests/test_gemini_sandbox.py`.

### Plugin-owned permission-controller retirement

- Modify `bin/bootstrap_repair.py:16-50,97-123,1760-1835,1969-2245`: retain exact removal and generic transaction helpers; retire repair-agent and shell-entry installation/registration.
- Modify `scripts/bootstrap.sh:16-142,381-428,540-838,1086-1810,1834-2243`: install wrapper launchers only, clean exact legacy artifacts, and stop generating Codex permission state.
- Modify `bin/apply_patch.py:1-9`: describe the proposal-only native child rather than the retired Custom Agent.
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
- Inspect unchanged `bin/triad_formal_review_schema.py` and
  `tests/test_formal_review_schema.py` to preserve the legacy sealed-packet
  `FormalReview` boundary while the new route reuses only `FormalFinding`.

### Public documentation and release

- Modify `README.md`.
- Modify `README.ko.md`.
- Modify `SECURITY.md`.
- Modify `CHANGELOG.md`.
- Modify `.codex-plugin/plugin.json`.
- Modify `docs/status/2026-07-22-current-state.md`.
- Modify `docs/status/2026-07-22-resume-prompt.md`.
- Preserve the already committed
  `docs/status/2026-07-30-native-source-observation-spike.md` proof; Task 8
  updates no historical spike bytes.
- Create `docs/status/2026-07-30-v0.2.532-release-notes.md`.
- Preserve dated formal-round ledgers as historical records.

---

### Task 1: Deterministic Change-Evidence Preparation

**Files:**
- Create: `bin/review_evidence.py`
- Create: `tests/test_review_evidence.py`

**Interfaces:**
- Consumes: an immutable prepared review root, a captured unified diff file,
  and a leader-authored UTF-8 TSV with exact header
  `path	reason	reached_from	change_kind	previous_path`.
- Produces: `EvidenceSummary`, `CHANGESET.md`, `IMPACT_CLOSURE.tsv`, `PATCH_INDEX.tsv`, `MANIFEST.sha256`, deterministic patch shards, and batch manifests.
- Produces callable interfaces:

```python
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
class EvidenceSummary:
    review_root: Path = field(compare=False)
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

For every callable and CLI path, the canonical non-symlink evidence directory
must equal `review_root / "change-evidence"`. Reject an external path, an
alternate in-root path, or any symlinked component. For preparation, require a
canonical review root and parent, create only that exact absent output leaf,
and reject an existing symlink or non-directory. Validation and admission
recheck the same equality before reading evidence.

- CLI:

```text
python3 bin/review_evidence.py prepare \
  --review-root /absolute/project/worktree/_runs/reviews/<id>/prepared \
  --diff-file /absolute/project/worktree/_runs/reviews/<id>/candidate.diff \
  --impact-input /absolute/project/worktree/_runs/reviews/<id>/impact-closure.tsv \
  --output-dir /absolute/project/worktree/_runs/reviews/<id>/prepared/change-evidence \
  --batch-byte-limit 262144

python3 bin/review_evidence.py validate \
  --review-root /absolute/project/worktree/_runs/reviews/<id>/prepared \
  --evidence-dir /absolute/project/worktree/_runs/reviews/<id>/prepared/change-evidence
```

- The patch splitter treats `diff --git ` as a file-section boundary and `@@ ` as a hunk boundary. It carries the file header into each hunk shard and assigns ordinal IDs without interpreting shell syntax from path text.
- `PATCH_INDEX.tsv` is normative and has this exact ordered header:
  `patch_id	group_id	section_ordinal	hunk_ordinal	change_kind	previous_path	path	sha256	byte_count`.
  `patch_id` is the canonical receipt identifier; a file section without a
  textual hunk gets one file-level ID. Use `-` for an absent `hunk_ordinal` or
  `previous_path`. Each patch artifact has the exact relative path
  `patches/<group_id>/<patch_id>.patch`. Its `change_kind` is exactly one of
  `modified`, `added`, `deleted`, or `renamed`; `affected-unchanged` never has a
  patch row.
- `IMPACT_CLOSURE.tsv` is normative and has this exact ordered header:
  `path	reason	reached_from	change_kind	previous_path	content_sha256	byte_count	line_count	impact_edge_id	batch_id`.
  Allowed `change_kind` values are exactly `modified`, `added`, `deleted`,
  `renamed`, and `affected-unchanged`. Changed rows use
  `impact_edge_id=-`; affected unchanged rows derive it deterministically from
  the exact UTF-8 bytes of `path`, `reason`, and `reached_from`. For a deleted
  row, `path` and `previous_path` both contain the canonical old path. Modified,
  added, and affected-unchanged rows use `previous_path=-`; renamed rows use
  the old path there.
- Enforce `reason == "changed"` if and only if `change_kind` is one of
  `modified`, `added`, `deleted`, or `renamed`; `affected-unchanged` requires a
  non-`changed` reason. Receipt hunk/edge rules key on `change_kind` only.
- `path` alone remains the coverage key. `change_kind` and `previous_path` are
  required deletion/rename provenance fields, not a composite
  `(path, change_kind)` key.
- For decoded UTF-8 current source, compute `line_count` exactly as
  `len(text.splitlines())`; test newline-terminated, unterminated, and
  newline-only files.
- Each affected-unchanged path records one canonical, leader-selected
  reproducible proof edge. Do not duplicate path rows or add a multi-edge
  protocol; full source coverage, not exhaustive graph-edge enumeration, is
  the release requirement.
- `PATCH_FILES_PER_GROUP = 100`. File sections 1-100 are `group-0001`,
  101-200 are `group-0002`, and so on; `GROUP_COUNT` is the exact number of
  non-empty groups. `PATCH_FILE_COUNT` counts file sections, while
  `patch_shards` may be larger when a section contains multiple hunks.
- Source files remain complete in the prepared root. An oversized file receives a single-path batch; provider file-read ranges may bound individual tool outputs, but every range remains required.
- `EvidenceSummary.review_root` is the canonical prepared root used to
  revalidate source observations and finding locations. The coverage CLI
  receives `--review-root` once to call `validate_review_evidence`; downstream
  admission uses only the validated `EvidenceSummary.review_root`.

- [ ] **Step 1: Prove plan provenance, create the branch, and record the Python boundary**

Run from `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`:

```bash
triad_planning_branch="$(git branch --show-current)"
triad_planning_head="$(git rev-parse HEAD)"
test "$triad_planning_branch" = "release/0.2.530"
test -z "$(git status --short)"
git merge-base --is-ancestor 1744c43c52b80cf2e28201a1c67d50611480f760 "$triad_planning_head"
git show --no-patch --format='%H %s' "$triad_planning_head"
git switch -c release/0.2.532 "$triad_planning_head"
git status -sb
```

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'command -v python3; python3 --version; python3 -m pytest --version'
```

Record `triad_planning_branch`, `triad_planning_head`, the ancestry result, and
the new branch HEAD in the SDD ledger. Expected: the final committed plan is
the exact branch point, branch `release/0.2.532` is clean, literal `python3`
resolves through the login shell, and pytest is available.

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
        "path\treason\treached_from\tchange_kind\tprevious_path\n"
        "src/caller.py\tchanged\t-\tmodified\t-\n",
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
    diff_file.write_text(
        "diff --git a/linked.py b/linked.py\n"
        "--- a/linked.py\n+++ b/linked.py\n"
        "@@ -1 +1 @@\n-secret = False\n+secret = True\n",
        encoding="utf-8",
    )
    impact = tmp_path / "impact.tsv"
    impact.write_text(
        "path\treason\treached_from\tchange_kind\tprevious_path\n"
        "linked.py\tchanged\t-\tmodified\t-\n",
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
- `test_prepare_rejects_newline_or_tab_path`: use a Git-quoted pathname with
  LF and then TAB, requiring `EvidenceError("control character in TSV field")`.
- `test_prepare_rejects_missing_diff_row_for_changed_closure`: declare a
  `reason=changed` row absent from the parsed diff and require
  `EvidenceError("changed closure row lacks diff section")`.
- `test_prepare_rejects_missing_changed_row_for_diff_target`: omit the
  `reason=changed` closure row for a parsed diff target and require
  `EvidenceError("diff target lacks changed closure row")`.
- `test_prepare_rejects_reason_change_kind_mismatch`: cover both directions of
  the `reason=changed` equivalence and require
  `EvidenceError("reason/change_kind mismatch")`.
- `test_prepare_handles_deletion_and_rename`: assert a deletion records empty
  SHA-256, byte count and line count zero, identical canonical old `path` and
  `previous_path`, exact patch IDs, no current source, and a canonical deletion
  diff section; require `EvidenceError("deleted path has current source")` when
  that path still exists and `EvidenceError("deleted row lacks deletion diff")`
  when the diff kind disagrees. Assert a rename records old `previous_path`,
  the new source, and its file-level rename ID.
- `test_evidence_directory_must_be_canonical_child`: reject an external
  `output_dir`/`evidence_dir`, an alternate in-root directory, and a symlinked
  `change-evidence` path; accept only the exact canonical child.
- `test_line_count_matches_splitlines_convention`: assert exact counts for
  newline-terminated, unterminated, newline-only, and zero-byte UTF-8 sources.
- `test_oversized_source_receives_complete_single_path_batch`: set the byte
  limit below one source file's size and assert one batch contains that
  complete path with the exact byte and line counts and no shard records.
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
  equal summaries (with `review_root` excluded from dataclass equality), equal
  manifests, `group-0001` through `group-0012`,
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

Import `field` from `dataclasses`; `EvidenceSummary.review_root` is
`field(compare=False)` so deterministic summaries prepared under separate
roots compare by their evidence content rather than their custody location.

Open inputs with no symlink following, reject non-regular files and non-UTF-8
current production source, sort impact rows by UTF-8 path bytes, pack them
greedily into `batch-0001` onward, write all output through same-directory
temporary files plus `os.replace`, and derive `MANIFEST.sha256` from every
evidence file except itself. Validation reopens and rehashes the current source
and every evidence artifact. Reject NUL, LF, CR, and TAB in `path` and
`reached_from` before TSV emission; decode Git-quoted path fields only far
enough to detect and reject those controls. Spaces, quotes, backticks, and
literal `$()` remain data and execute nothing. This is an intentional
`0.2.532` input limit: do not silently omit a path or admit partial coverage.

Before any output or evidence read, require the canonical non-symlink evidence
directory to equal `review_root / "change-evidence"` exactly. This containment
check is custody validation, not a generalized filesystem sandbox.

Define `source_tree_digest` as SHA-256 over canonical
`relative-path NUL file-sha256 NUL byte-count LF` records for every regular file
below `review_root` except `output_dir`, sorted by UTF-8 path bytes. Reject every
symlink encountered during that walk. Define `change_evidence_digest` with the
same record encoding over generated patch, index, closure, and batch artifacts
before `CHANGESET.md` and `MANIFEST.sha256` are written. Then
`MANIFEST.sha256` hashes every evidence artifact except itself, including the
completed `CHANGESET.md`; this ordering avoids a self-referential digest.

`prepare_review_evidence` and `validate_review_evidence` reject every parsed
diff target missing a `reason=changed` closure row and every changed closure
row missing a diff section. They enforce the exact `reason`/`change_kind`
equivalence above. For a deleted row, both preparation and validation reject
any existing current path and any canonical diff section that is not a
deletion; valid deletion evidence has the empty digest/counts and exact patch
IDs but no current observation or line evidence. A renamed path requires the
new current source and its old path in `previous_path`. Compute every current
source `line_count` with `len(decoded_text.splitlines())`.

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
- Reuses: `FormalFinding` from `bin/triad_formal_review_schema.py`.
- Produces:

```python
class PathEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    path: str
    content_sha256: str
    observation_line: int | None = Field(default=None, ge=1)
    source_observation: str
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

- Operational CLI:

```text
python3 bin/review_coverage.py admit \
  --review-root /absolute/project/worktree/_runs/reviews/<id>/prepared \
  --evidence-dir /absolute/project/worktree/_runs/reviews/<id>/prepared/change-evidence \
  --receipts-root /absolute/project/worktree/_runs/reviews/<id>/results \
  --output /absolute/project/worktree/_runs/reviews/<id>/coverage-admission.json
```

`receipts-root` contains exactly
`<family>/<batch-id>.json` for every combination of `claude`, `google`,
`codex`, and the validated batch IDs. Missing files, extra JSON files,
symlinks, and non-regular files are invalid. The command validates evidence,
each exact response byte stream, every family, and final admission, then
atomically writes canonical UTF-8 JSON. It exits nonzero and writes no admitted
artifact on any invalid or non-admitted result. This output is the sole
machine-admissible gate result; prose summaries cannot replace it.
The CLI first requires canonical `evidence-dir` equality with
`review-root/change-evidence`; an external, alternate, or symlinked evidence
path is invalid.

- A `changed` row's `changed_hunks` set exactly equals its canonical
  `PATCH_INDEX.tsv` `patch_id` set. An omitted, extra, duplicated, or forged
  ID is rejected.
- An affected unchanged row's `verified_impact_edges` set exactly equals its
  expected `impact_edge_id` set. An omitted, extra, duplicated, or forged ID
  is rejected.
- Changed, added, deleted, and renamed rows have an empty
  `verified_impact_edges`; affected-unchanged rows have an empty
  `changed_hunks`.
- Every non-empty non-deleted path requires `line_start == 1` and
  `line_end == ImpactRow.line_count`; `symbols` are optional annotations and
  never replace full-file evidence. For UTF-8 source with non-whitespace
  content, `observation_line` names a line within the file and
  `source_observation` is a 1-160 character exact substring of that line; when
  the line has at least eight characters the observation has at least eight.
  Observation text is absent from reviewer-visible manifests and is
  revalidated from `EvidenceSummary.review_root`. A validator-proven zero-byte
  current source uses `line_start=line_end=None`,
  `observation_line=None`, and empty observation text. A non-empty
  whitespace-only source keeps its exact full-file line range and uses
  `observation_line=None` plus empty observation text only when the validator
  proves that condition. Deleted paths require no current-source observation,
  symbol, or line evidence.
- For a changed current source with at least one line outside the validated
  new-side ranges of its canonical patch hunks, require `observation_line` to
  name an outside-hunk line. Parse those ranges from the digest-bound patch
  artifacts; do not add another index field. If the validated hunks cover
  every current line, admit a patch-derived observation because the patch
  already contains the complete current source. This is the only changed-path
  anti-echo exception.
- Every finding location is an exact review-relative `path:positive-line`.
  Admit only a current closure path or
  `change-evidence/patches/<group-id>/<patch-id>.patch`, re-open it without
  symlink following, and validate its expected digest, UTF-8 decoding, and line
  bound.
- `disposition="unresolved"`, a non-empty `unresolved_paths`, an
  `open_questions` entry, Critical/Major finding, or any `NOT-SAFE` receipt
  blocks admission.
- Cross-check each `PathEvidence.disposition`. It is `unresolved` exactly for a
  path in `unresolved_paths`; otherwise it is `finding` exactly when an
  admitted finding location maps to that current path or one of its canonical
  patch IDs, and `no-finding` only when neither condition holds. Reject every
  contradictory disposition.
- Each provider returns exactly one strict `BatchReceipt` JSON document per
  batch. The leader saves the exact UTF-8 response bytes under a
  family/batch-specific result path and gives those paths to
  `validate_family_receipts`. Hash the original response bytes for custody.
  Deterministically accept either raw JSON or exactly one outer Markdown fence
  with an optional `json` info string, then pass only its inner bytes to strict
  JSON validation. Trim only outer ASCII whitespace for envelope detection.
  The opening line is exactly three backticks or three backticks plus `json`,
  the closing line is exactly three backticks, and the inner payload contains
  no fence token. Reject leading/trailing prose, nested or multiple fences,
  missing fields, or family/batch mismatch. Fresh Codex terminal text is
  persisted under the same rule; no wrapper responsibility is added.
  Parse the raw-or-unfenced JSON bytes with
  `BatchReceipt.model_validate_json(json_bytes, strict=True)` so JSON arrays
  use Pydantic's strict JSON path for tuple fields; do not pre-decode into
  strict Python-mode tuple validation. Schema enforcement is offline. A
  malformed receipt invalidates that family and requires its complete fresh
  re-dispatch; wrappers add no schema-repair retry.

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
        observation_line=1,
        source_observation="forged observation",
        symbols=(),
        line_start=1,
        line_end=evidence.affected_paths[0].line_count,
    )
    with pytest.raises(
        review_coverage.CoverageError,
        match="source observation mismatch",
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
- `test_changed_hunk_ids_are_exact`: use omitted, extra, duplicated, and forged
  IDs and require `changed hunk IDs do not match PATCH_INDEX`;
- `test_impact_edge_ids_are_exact`: use omitted, extra, duplicated, and forged
  IDs and require `impact edge IDs do not match closure`;
- `test_cross_kind_evidence_ids_must_be_empty`: add an impact-edge ID to a
  changed row and a hunk ID to an affected-unchanged row, requiring
  `unexpected cross-kind evidence`;
- `test_partial_full_file_range_is_rejected`: use `1..1` for a multi-line
  source and require `complete source range required`;
- `test_line_range_beyond_current_source_is_rejected`: set `line_end` above
  `ImpactRow.line_count` and require `complete source range required`;
- `test_manifest_only_observation_is_rejected`: populate every visible
  manifest and index field correctly but forge `source_observation`, requiring
  `source observation mismatch`;
- `test_source_observation_bounds_are_exact`: reject an out-of-range
  `observation_line`, a substring absent from that line, an observation over
  160 characters, and an under-eight observation when the selected line is at
  least eight characters;
- `test_empty_source_observation_exception_is_narrow`: admit empty observation
  only for validator-proven empty or whitespace-only current source; require
  `line_start=line_end=None` for a zero-byte source but the exact full-file
  line range for a non-empty whitespace-only source;
- `test_changed_observation_outside_hunks_is_required`: reject a partial-file
  changed path whose observation line is inside a visible patch hunk;
- `test_full_file_hunks_allow_patch_derived_observation`: admit an observation
  inside a hunk only when validated new-side hunk ranges cover every current
  source line;
- `test_malformed_finding_is_rejected`: omit each required `FormalFinding`
  field in turn and require strict receipt validation failure;
- `test_strict_json_receipt_accepts_json_arrays_for_tuple_fields`: persist an
  otherwise valid raw JSON receipt and prove `model_validate_json` is the
  parsing path; the validator must not pre-decode it into strict Python mode;
- `test_single_outer_json_fence_preserves_raw_receipt_digest`: admit one exact
  outer JSON fence, assert the receipt digest hashes the original fenced bytes,
  and reject prose wrappers plus nested or multiple fences;
- `test_deleted_row_requires_patch_only_path_evidence`: include a deleted row
  in the exact receipt path set with patch IDs and no current-source fields;
- `test_finding_location_is_source_grounded`: reject malformed, out-of-closure,
  out-of-range, and digest-mismatched source or canonical patch locations;
- `test_unresolved_disposition_is_rejected` -> `unresolved path`;
- `test_disposition_must_match_findings_and_unresolved_paths`: reject
  `finding` with no path-mapped finding, `no-finding` with a path-mapped
  finding, and either resolved disposition for a path in `unresolved_paths`;
- `test_admission_rejects_duplicate_family` -> `duplicate family coverage`;
- `test_admission_rejects_missing_family` -> `missing family coverage`.
- `test_admit_cli_is_the_only_persisted_gate`: build the exact three-family
  receipt tree, run `main(["admit", ...])`, assert canonical admitted JSON,
  then add one extra receipt and assert nonzero exit with no output.
- `test_admit_rejects_external_or_symlinked_evidence_dir`: point the CLI at an
  otherwise valid copied external evidence tree and then a symlinked
  `change-evidence` path; require nonzero exit and no admitted output.

- [ ] **Step 2: Run the coverage tests to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py'
```

Expected: collection fails because `review_coverage` does not exist.

- [ ] **Step 3: Implement strict coverage models and admission**

Create `bin/review_coverage.py`. Validate JSON with Pydantic 2 strict models,
reuse `FormalFinding` from `triad_formal_review_schema`,
hash the original response bytes, deterministically remove at most one exact
outer JSON Markdown fence, parse the raw-or-unfenced JSON bytes through
`BatchReceipt.model_validate_json(json_bytes, strict=True)`, compute receipt
SHA-256 from the original bytes, require exact batch and path
sets, exact per-path patch and edge sets, and compare every receipt digest with
`EvidenceSummary`. Raise `CoverageError` on the first deterministic mismatch
and never coerce strings to numbers. Require `1..ImpactRow.line_count` for
every non-empty non-deleted row, validate its bounded exact source observation
from `EvidenceSummary.review_root`, and keep symbols optional. Require a
changed-path observation outside validated current-side hunk ranges whenever
such a line exists; allow a hunk-derived observation only when those ranges
cover every current line. Exempt validator-proven zero-byte current sources
and deleted rows from current observation/symbol/line requirements. Validate
finding locations against digest-bound current closure paths or canonical
patch artifacts and use that mapping to enforce exact disposition consistency.
Require `evidence_dir` to be the canonical non-symlink
`review_root / "change-evidence"` before parsing receipts.
Implement only the exact `admit` CLI and receipt layout above; do not add a
general orchestration framework or source sharding.

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
- Modify: `bin/_common.py:55-87,296-297,2492-2497`
- Modify: `bin/antigravity_wrapper.py:1-60,107-134,209-301,304-506,518-790`
- Modify: `tests/test_antigravity_packet_context.py`
- Modify: `tests/test_distribution_contract.py`
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

    monkeypatch.setattr(
        wrapper._common,
        "snapshot_agy_transcripts",
        lambda *args, **kwargs: {},
    )
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
Remove every remaining `skip_permissions` argument/signature dependency,
including the non-preflight `_build_cmd(..., skip_permissions=True)` call sites
and the positional-arity assumption in
`test_build_cmd_passes_model_and_optional_effort_unchanged`; preserve that
test's selector/model/effort assertions.

Delete
`test_settings_guard_phase_is_preserved_in_custody_and_summary` and
`test_settings_restore_failure_suppresses_validated_provider_answer`; their
only contract is the retired settings transaction. Rewrite
`test_sealed_schema_failure_persists_one_provider_response_without_retry` and
`test_audit_and_run_log_preserve_phase_and_exact_validated_object` to preserve
their schema/custody assertions while using `post-dispatch-result`.

Update all three existing preflight tests that assert sandbox,
`skip_permissions`, or the old `_build_route_args` arity so their expected
preflight receipt has only the post-change fields: selector/model, optional
effort, native permission inheritance, and `permission-unavailable` terminal
classification. Patch the transcript extractor mock with the current helper
signature exactly as the surrounding tests do. Update the `_common.py`
classification-source comment when adding `permission-unavailable`. Rewrite
`test_formal_review_uses_owner_routing_baseline_and_bounded_escalation` so its
wrapper-source assertion expects `_build_route_args(model, effort)` and retains
all unrelated routing assertions.
Rewrite
`test_nonroute_first_start_error_remains_ineligible_config_conflict`,
`test_retry_pty_start_failure_remains_post_dispatch_and_ineligible`, and
`test_schema_retry_transport_error_persists_attempt_state` to retain their
driver exception containment, result custody, and fallback-ineligibility
assertions while replacing the retired `dispatch-uncertain` phase with
`post-dispatch-result`.

- [ ] **Step 2: Run the AGY tests to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_antigravity_packet_context.py -k "native_headless_permission_denial or route_builder_contains_only"'
```

Expected: the first test observes a second bypass retry or a non-terminal classification, and the route-builder signature does not match.

- [ ] **Step 3: Remove AGY permission control and add terminal classification**

Delete `_add_skip_permissions`, `_agy_needs_skip_permissions`, version-floor logic, `--sandbox`, settings-lock handling, `_agy_settings` imports/guards, and every `skip_permissions`/`agy_sandbox` parameter. In the no-answer path, add the observed native AGY detector only; do not add Claude or Gemini message detectors. Add:

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
Remove only the `_agy_settings.agy_settings_guard(...)` lease, the
`pre-dispatch-settings` / `dispatch-uncertain` / `post-dispatch-cleanup` phase
assignments, and the settings-release suppression clause. Call
`_run_agy_with_retry` directly and retain `post-dispatch-result` through result
custody. Preserve the surrounding driver `try/except`, the pre-submission
`EXIT_BINARY_MISSING` branch, and the custody-preserving terminal
`config-conflict` result for `_pty.PtyStartError`, `TimeoutError`,
`json.JSONDecodeError`, `ValueError`, and `OSError`. Update the
`RunResult.dispatch_phase` comment plus retired sandbox/settings module
docstrings. Task 5 separately updates the analyzer wording.

- [ ] **Step 4: Delete retired settings code and run GREEN tests**

Delete `bin/_agy_settings.py` and `tests/test_agy_settings.py`, then run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_antigravity_packet_context.py workspace/triad-codex-dispatch-reliability/tests/test_log_cleanup.py'
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k formal_review_uses_owner_routing_baseline_and_bounded_escalation'
```

Expected: all selected tests pass and `rg "_agy_settings|dangerously-skip-permissions|AGY_NO_HEADLESS_AUTOAPPROVE" bin tests` returns no active-code hit.

- [ ] **Step 5: Commit native AGY behavior**

```bash
git add bin/_common.py bin/antigravity_wrapper.py tests/test_antigravity_packet_context.py tests/test_distribution_contract.py
git add -u bin/_agy_settings.py tests/test_agy_settings.py
git commit -m "fix: inherit native agy permissions"
```

### Task 4: Native Claude and Gemini Permissions

**Files:**
- Modify: `bin/claude_wrapper.py:1-235`
- Modify: `bin/gemini_wrapper.py:1-182`
- Modify: `tests/test_provider_packet_context.py`
- Delete: `bin/policies/gemini-readonly.toml`
- Delete: `tests/test_gemini_sandbox.py`

**Interfaces:**
- Claude forwards only prompt, output format, optional model, optional effort, optional fallback model, cwd, timeout, schema, packet-compatibility, repair, and debug controls.
- Gemini forwards only prompt, output format, optional model, cwd, timeout,
  schema, packet-compatibility, repair, and debug controls. `--skip-trust` is
  removed from public and generated argv because it bypasses a provider-owned
  trust decision.
- An untrusted prepared directory can therefore fail under Gemini's native
  workspace-trust policy. TRIAD reports the native failure and adds neither a
  trust bypass nor a speculative denial detector.
- Removed wrapper arguments are rejected by `argparse` rather than translated.
- Remove orphaned `PERMISSION_CHOICES` / `PERMISSION_FORBIDDEN` constants and
  the now-unused `os` import from Claude, and orphaned `_wrapper_hardened` /
  `Path` imports from Gemini with their consumers.

- [ ] **Step 1: Write failing argv tests**

Add to `tests/test_provider_packet_context.py`:

```python
@pytest.mark.parametrize(
    ("module", "removed_argv"),
    [
        (claude_wrapper, ["--sandbox", "read-only"]),
        (claude_wrapper, ["--permission-mode", "default"]),
        (gemini_wrapper, ["--sandbox", "read-only"]),
        (gemini_wrapper, ["--approval-mode", "default"]),
        (gemini_wrapper, ["--skip-trust"]),
    ],
)
def test_removed_permission_options_are_rejected(
    module,
    removed_argv,
    monkeypatch,
) -> None:
    monkeypatch.delenv("TRIAD_CLAUDE_ENFORCE_SANDBOX", raising=False)
    monkeypatch.setattr(
        module,
        "_wrapper_hardened",
        lambda: False,
        raising=False,
    )
    monkeypatch.setattr(module, "require_binary", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        module,
        "run_cli_with_retry",
        lambda *_a, **_k: _common.RunResult(
            _common.EXIT_OK,
            "ok",
            "",
            0.0,
            final_answer="ok",
        ),
    )
    monkeypatch.setattr(module, "persist_result_artifacts", lambda *_a, **_k: None)
    monkeypatch.setattr(
        sys,
        "argv",
        [module.__file__, "--prompt", "review", *removed_argv],
    )

    with pytest.raises(SystemExit) as exc_info:
        module.main()
    assert exc_info.value.code == 2


@pytest.mark.parametrize(
    ("module", "forbidden", "hardened"),
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
            False,
        ),
        (
            gemini_wrapper,
            {"--sandbox", "--approval-mode", "--policy", "--skip-trust"},
            True,
        ),
    ],
)
def test_native_wrapper_default_argv_has_no_permission_override(
    module,
    forbidden,
    hardened,
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

    monkeypatch.delenv("TRIAD_CLAUDE_ENFORCE_SANDBOX", raising=False)
    monkeypatch.setattr(
        module,
        "_wrapper_hardened",
        lambda: hardened,
        raising=False,
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
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_provider_packet_context.py -k "removed_permission_options or native_wrapper_default_argv"'
```

Expected: removed-option cases fail because the current parser accepts them;
the hardened Gemini default emits `--policy`.

- [ ] **Step 3: Remove wrapper permission arguments and policy injection**

Delete Claude's `--sandbox`, `--permission-mode`, `TRIAD_CLAUDE_ENFORCE_SANDBOX`, and generated tool/config/permission flags. Delete Gemini's `--approval-mode`, `--sandbox`, `--skip-trust`, policy constant, hardened default, and generated `--policy`/approval flags. Neither the public nor generated Gemini argv may skip a provider-owned trust decision.

- [ ] **Step 4: Delete retired policy tests and run GREEN tests**

Delete `bin/policies/gemini-readonly.toml` and `tests/test_gemini_sandbox.py`.
`bin/policies/` has no remaining tracked artifact and disappears naturally;
do not add an empty-directory placeholder. Run:

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
- Modify: `bin/apply_patch.py:1-9`
- Modify: `bin/antigravity_wrapper.py:347,746`
- Modify: `bin/bootstrap_repair.py:16-50,97-123,1969-2245`
- Modify: `scripts/bootstrap.sh:381-428,650-838,1908-2145,2180-2243`
- Modify: `tests/test_bootstrap.py`
- Modify: `tests/test_bootstrap_repair_transaction.py`
- Modify: `tests/test_distribution_contract.py`
- Delete: `agents/triad-repair-analyzer.toml`

**Interfaces:**
- Repair analysis uses native `spawn_agent` with `fork_turns="none"`, explicit current router model, medium effort, omitted `agent_type`, and the existing untrusted JSON envelope.
- Repair apply uses the plugin's `bin/apply_patch.py` through literal login-shell `python3`; no installed `triad-apply-repair` launcher is required.
- Upgrade cleanup removes only the exact managed analyzer registration, analyzer TOML, and apply launcher.
- Wrapper launchers retain their existing all-or-nothing command-group staged
  publication independently of the retired repair-agent lifecycle; cleanup
  must not publish a partial launcher group.

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
managed form already accepted by `launcher_is_managed`. Parameterize the test
over that five-line legacy form and the current seven-line pinned form emitted
by `bootstrap_repair.launcher_text`, so the actual `0.2.531 -> 0.2.532`
upgrade is covered. Do not add a second removal predicate.

Rewrite the existing
`test_repair_handoff_uses_one_json_input_envelope_and_valid_output_examples`
to read `docs/references/repair-protocol.md` alone after the agent TOML is
deleted. Preserve its one-envelope assertion and validate both `propose` and
`escalate` examples against `_common.PATTERN_LIST_CLASS`,
`_MIN_SUBSTRING_LEN`, and `_MAX_SUBSTRING_LEN`; remove only the
`REPAIR_AGENT`, `developer_instructions`, and `agent_type` assertions. Fold the
still-valid literal login-shell `bin/apply_patch.py` assertions from
`test_repair_protocol_uses_the_exact_installed_agent_and_apply_contract` into
`test_repair_protocol_uses_fresh_native_child_without_custom_agent`, then
remove the retired exact-installed-agent half.

- [ ] **Step 2: Run focused tests to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k repair_protocol_uses_fresh_native_child'
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py -k removes_only_exact_legacy_repair_agent_artifacts'
```

Expected: the protocol still names the registered agent and bootstrap still installs it.

- [ ] **Step 3: Rewrite the repair protocol**

Keep the fenced JSON envelope and proposal schema, including both bounded
example payloads validated by the rewritten distribution test. Replace the
Custom Agent call with:

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

Update `bin/apply_patch.py`'s module docstring to describe the proposal-only
native child, and update both AGY runtime comments at the retry driver and
result-custody path so neither claims a shipped read-only analyzer exists.
These are wording-only changes; retain the validated apply path and retry
behavior.

- [ ] **Step 4: Make bootstrap repair-agent support remove-only**

Remove `install`, `preflight-install`, analyzer source validation, analyzer registration creation, and installed apply-launcher creation from `bin/bootstrap_repair.py`. Retain the exact managed `remove` path and generic transaction helpers required to clean old installations.

Change `scripts/bootstrap.sh --install` to invoke exact repair cleanup before installing wrapper launchers. A foreign registration, analyzer, or launcher is reported and preserved. Delete the shipped analyzer TOML.

- [ ] **Step 5: Prune obsolete tests and run GREEN tests**

Remove tests whose only contract is installing, refreshing, or selecting the read-only analyzer. Retain and rename exact-removal, foreign-preservation, rollback, symlink-refusal, and transaction-integrity tests.

Rewrite the named current test
`test_recommended_agent_template_uses_current_read_only_repair_contract` to
retain its still-valid native repair-envelope assertions while replacing only
the retired read-only repair-agent expectation. Rewrite
`test_runtime_comments_describe_the_current_read_only_analyzer_flow` to retain
the owner-controlled proposal/no-provider-invocation assertions without the
retired agent phrase. Update `_make_repo_root` and related bootstrap fixtures
so deleting the shipped analyzer and the migration requirements template does
not leave a fixture-generated stale file.

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py workspace/triad-codex-dispatch-reliability/tests/test_bootstrap_repair_transaction.py workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k "repair or analyzer or bootstrap_repair"'
```

Expected: selected tests pass and no shipped/installed read-only repair agent remains.

- [ ] **Step 6: Commit repair-agent retirement**

```bash
git add docs/references/repair-protocol.md bin/apply_patch.py bin/antigravity_wrapper.py bin/bootstrap_repair.py scripts/bootstrap.sh tests/test_bootstrap.py tests/test_bootstrap_repair_transaction.py tests/test_distribution_contract.py
git add -u agents/triad-repair-analyzer.toml
git commit -m "refactor: use native repair children"
```

### Task 6: Remove Plugin-Owned Permission Profiles, Rules, and Migration Templates

**Files:**
- Modify: `bin/_common.py:398-406`
- Modify: `scripts/bootstrap.sh:16-142,540-650,1086-1810,1834-1935,2180-2243`
- Modify: `bin/bootstrap_repair.py:23-43,652-772,1411-1520,1760-1835,2163-2245`
- Modify: `migration/AGENTS.recommended.md`
- Modify: `tests/test_bootstrap.py`
- Modify: `tests/test_bootstrap_repair_transaction.py`
- Modify: `tests/test_migration_contract.py`
- Modify: `tests/test_distribution_contract.py`
- Delete: `migration/config-fragment.recommended.toml`
- Delete: `migration/requirements.recommended.toml`
- Delete: `migration/triad-codex-dispatch.rules`

**Interfaces:**
- `scripts/bootstrap.sh --install` installs/refreshes only wrapper launchers and non-permission runtime support, after exact cleanup of prior plugin-owned policy artifacts.
- `scripts/bootstrap.sh --remove` removes exact managed launchers and exact legacy plugin-owned artifacts.
- No install option or environment variable can create a Codex profile, rule, shell entry, config fragment, or permission requirement.
- The `shell-entry --action install` path and generated
  `TRIAD_WRAPPER_HARDENED` / `TRIAD_CLAUDE_ENFORCE_SANDBOX` exports are
  retired. Exact managed shell-entry removal remains for upgrades.
- Existing all-or-nothing command-group staged publication for wrapper launchers
  remains intact and independent of retired repair-agent cleanup.

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

Add `test_native_install_emits_no_permission_environment_controls` and assert
that no generated or installed artifact contains
`TRIAD_CLAUDE_ENFORCE_SANDBOX` or `TRIAD_WRAPPER_HARDENED`.

- [ ] **Step 2: Run focused tests to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py -k native_install_does_not_create_codex_permission_state'
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_migration_contract.py'
```

Expected: default installation creates rules and the migration tests require the templates.

- [ ] **Step 3: Remove permission-generation paths**

Delete profile/rules selection, preflight, generation, config-fragment merge,
requirements guidance, shell-entry installation, and Agent Review/sandbox
messaging from `scripts/bootstrap.sh`. In `bootstrap_repair.py`, delete
`preflight_shell_entry`, `_shell_entry_block`, and the install branch of
`update_shell_entry`; retain only exact ownership inspection/removal needed for
upgrade cleanup. Keep exact ownership inspectors/removers in
`bootstrap_repair.py` only as needed for upgrade cleanup. Preserve the existing
all-or-nothing command-group staged publication for wrapper launchers;
repair-agent retirement cannot weaken that transaction boundary.

Remove all `scripts/bootstrap.sh` calls to the deleted
`preflight_shell_entry`. The retained `update_shell_entry --action remove`
operation performs the exact marker/content ownership check and removal as one
guarded upgrade-cleanup action; a foreign or edited block is preserved and
reported. Do not replace the retired preflight with a new policy layer.

Rewrite the `bin/_common.py` hardening comment so it no longer claims that the
retired shell entry activates `TRIAD_WRAPPER_HARDENED`. Describe only the
remaining explicit environment-variable activation used by compatibility
callers; do not add a new installer path.

On both `--install` and `--remove`, clean exact legacy artifacts in this order:

1. repair registration/analyzer/apply launcher;
2. plugin-owned rules;
3. plugin-owned profile;
4. exact managed config fragment;
5. exact managed shell entry.

A foreign or edited artifact is preserved and reported without broadening the removal predicate.

- [ ] **Step 4: Delete migration templates and update developer guidance**

Delete the three permission templates. Rewrite `migration/AGENTS.recommended.md` to recommend the same authenticated login terminal/worktree as development and state that TRIAD inherits provider permissions without changing them.
State the selected environment boundary exactly: wrapper descendants remain
scrubbed after trusted launcher/interpreter startup, but TRIAD no longer
injects a pre-spawn `shell_environment_policy`; the authenticated developer
terminal, trusted Python/PATH, and provider project settings are prerequisites.

- [ ] **Step 5: Prune obsolete policy-install tests and run GREEN tests**

Remove tests for optional profile/rules/config/shell installation. Retain tests for exact cleanup, foreign preservation, symlink refusal, rollback, launcher installation, reinstall idempotence, Python boundary, provider binaries not being invoked during install, and all-or-nothing command-group staged publication. Update `_make_repo_root` and related bootstrap fixtures for the deleted repair analyzer and `migration/requirements.recommended.toml` rather than masking their absence.

In `tests/test_distribution_contract.py`, delete
`test_task2_config_backup_guidance_qualifies_registration_only_fresh_config`,
rewrite
`test_task2_hardened_comments_name_opted_in_legacy_shell_entry` to assert the
post-retirement environment-only compatibility wording,
rewrite
`test_company_fleet_guides_and_terms_are_removed_but_personal_templates_remain`
to require only the retained non-permission migration guidance, and rewrite
`test_bootstrap_usage_describes_ordinary_codex_agent_review_requirements` to
assert native permission neutrality and exact legacy cleanup without requiring
profile/rule/repair-agent installation messaging.

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py workspace/triad-codex-dispatch-reliability/tests/test_bootstrap_repair_transaction.py workspace/triad-codex-dispatch-reliability/tests/test_migration_contract.py'
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k "task2_config_backup_guidance or company_fleet_guides_and_terms_are_removed_but_personal_templates_remain or bootstrap_usage_describes_ordinary_codex_agent_review_requirements"'
```

Expected: all tests pass.

- [ ] **Step 6: Commit permission-controller removal**

```bash
git add scripts/bootstrap.sh bin/bootstrap_repair.py migration/AGENTS.recommended.md tests/test_bootstrap.py tests/test_bootstrap_repair_transaction.py tests/test_migration_contract.py tests/test_distribution_contract.py
git add bin/_common.py
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
- `path_evidence` includes a validated `observation_line` and bounded exact
  `source_observation` absent from visible manifests plus the exact full-file
  line range.
- Each family must cover the exact batch set.
- A new affected path invalidates the complete round.
- Provider examples omit every permission-control flag.
- The one normative `BatchReceipt` schema includes `family`, `batch_id`, both
  digests, `verdict`, `path_evidence`, `findings`,
  `affected_surfaces_inspected`, `unresolved_paths`, and `open_questions`.
  `PathEvidence` alone retains per-path `changed_hunks` and
  `verified_impact_edges`; no redundant top-level edge promise exists.
- `FamilyCoverage` retains ordered receipt digests, covered paths,
  consolidated findings, unresolved paths/questions, affected surfaces, and a
  verdict. The leader retains exact UTF-8 response bytes at a
  family/batch-specific result path for `validate_family_receipts`.
- `BatchReceipt` is normative only for this batched route. The unchanged
  `FormalReview` model remains normative only for explicit legacy sealed-packet
  compatibility callers.
- Keep the existing shared prompt contract's unbatched `formal-gate` line and
  its four labeled semantic elements byte-identical as a compatibility
  profile. Add a separately named `batched-full-coverage` profile selected only
  when the exact batch metadata is present; it requires `BatchReceipt`. The
  operational `0.2.532` skill selects the batched profile, and an unbatched
  four-element answer is not coverage-admissible.

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
            REVIEW_ROUTING_REFERENCE,
            FRESH_CODEX_REVIEW_REFERENCE,
        )
    )
    for literal in (
        "source_tree_digest",
        "change_evidence_digest",
        "batch_id",
        "path_evidence",
        "source_observation",
        "observation_line",
        "complete source range",
        "coverage-admission.json",
        "Every required family reviews every batch",
        "A manifest path alone is not coverage",
    ):
        assert literal in contract


def test_provider_skill_examples_inherit_native_permissions() -> None:
    combined = "\n".join(
        [_text(path) for path in PROVIDER_SKILLS]
        + [_text(REVIEW_ROUTING_REFERENCE)]
    )
    for forbidden in (
        "--sandbox",
        "--permission-mode",
        "--approval-mode",
        "--skip-trust",
        "--dangerously-skip-permissions",
        "triad-repair-analyzer",
    ):
        assert forbidden not in combined
    assert "sandbox escalation to reach Agent Review" not in combined
    assert "read-only policy denies write" not in combined
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
- exact `1..line_count` source coverage and a validated bounded exact source
  observation for every non-empty non-deleted path, with the validator-proven
  zero-byte exception stated explicitly;
- invalidation on newly discovered paths;
- coverage admission through `review_coverage.py`;
- native permission inheritance;
- `permission-unavailable` as an invalid required leg; and
- fresh complete reruns after closure changes.

Require exactly one strict `BatchReceipt` JSON document per provider/batch.
Persist and hash the exact original UTF-8 response bytes. Accept raw JSON or
exactly one outer Markdown fence with optional `json` info, then strictly
validate only the inner JSON bytes. Use the exact outer-fence grammar and
ASCII-whitespace handling from Task 2. Reject prose wrappers, nested or
multiple fences, missing fields, and family/batch mismatches. Fresh Codex
terminal text is persisted under the same custody rule. Require
`changed_hunks` to exactly equal each path's
canonical `PATCH_INDEX.tsv` IDs and `verified_impact_edges` to exactly equal
its expected closure IDs. `SAFE` is impossible for Critical/Major findings,
any `NOT-SAFE` receipt, unresolved paths, or open questions.
Require the exact `<family>/<batch-id>.json` receipt tree and admit a formal
round only through the deterministic `review_coverage.py admit` output.
In `review-prompt-contract.md`, preserve the existing unbatched
`formal-gate -> verdict, findings, affected_surfaces_inspected, open_questions`
profile verbatim and add the separately selected batched profile. Do not
describe the legacy four-element semantic result or packet-bound
`FormalReview` as an alternate receipt schema.

Provider argv examples contain only prompt-file, cwd, selector, effort where
applicable, and result controls. Keep stable instructions before batch-specific
paths and digests so provider caches can reuse the prefix. Permit separate fresh
contexts per batch, require each family to finish every batch, address repeated
content by the same digest, and retain only compact receipts between contexts.
Cheap transport probes may use cheap routes; formal gates keep the
owner-authorized full-quality route. No batching rule may sample or skip a
source path.

Route-specific guidance may name the provider's native file-read/search
mechanism without changing the shared directory, objective, or receipt schema.
AGY source observation must not require its denied `command` tool or
provider-side hashing; fresh Codex may use bounded non-mutating read/search
operations. Candidate code, scripts, tests, builds, hooks, and mutation remain
prohibited for every formal leg.

Rewrite reviewer routing so native owner/project permissions govern AGY and
any separately authorized Google fallback. A native-permission-denied required
leg is invalid and, because it is post-dispatch, cannot trigger Gemini fallback
in the same round. Keep Gemini fallback eligible only for the existing proven
pre-dispatch AGY-unavailability route. Do not restore a TRIAD-installed
read-only policy, bypass, or provider substitution.

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

Rewrite the named current test
`test_distribution_docs_describe_one_installed_analyzer_and_launcher` to retain
still-valid distribution assertions and replace only retired
permission-controller/repair-agent expectations. Also update
`test_package_version_and_removed_release_aliases_are_current` only where its
retired controller expectation conflicts with the `0.2.532` contract.
Additionally:

- rewrite `test_task_2a_provider_guides_delegate_shared_formal_preparation` and
  `test_task_2b_gemini_guide_keeps_fallback_contract_without_shared_protocol`
  to retain route/cwd/shared-directory assertions while requiring absence of
  provider permission flags;
- rewrite `test_agy_truncated_answer_is_terminal_without_repair_or_provider_switch`
  to retain every truncated-answer terminality assertion while removing only
  the retired `--sandbox read-only` requirement; and
- preserve `test_fresh_codex_native_result_admission_is_semantic_not_json` and
  `test_fresh_codex_admission_docs_record_agy_fence_tolerance`, while adding
  route-specific assertions that the new `BatchReceipt` admission accepts only
  one outer fence and hashes the original bytes; and
- update
  `test_shared_review_prompt_contract_defines_envelope_and_mode_specific_results`
  to preserve the byte-identical unbatched profile and assert the separately
  selected `batched-full-coverage` profile; and
- preserve the complete distribution test as the Task 7 GREEN gate so no
  stale assertion is deferred to release documentation.

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
- Security documentation states that wrapper-launcher command groups continue
  to publish all-or-nothing through the existing staged transaction, separately
  from retired repair-agent cleanup.
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
- the owner-approved distinction between retained wrapper child-process
  scrubbing after trusted startup and removed pre-spawn
  `shell_environment_policy`, including the trusted terminal/Python/PATH
  prerequisite;
- native AGY headless fail-closed behavior and narrow user/project remediation;
- `permission-unavailable` in both README exit-65 legends and the matching
  `test_task2_readme_exit_code_legends_match_reachable_classes` assertion,
  distinct from authentication, quota, and truncated-answer classifications;
- Gemini's provider-owned workspace-trust requirement after `--skip-trust`
  removal, with no TRIAD bypass or speculative detector;
- full diff plus complete affected-source closure;
- all-family/all-batch coverage;
- source-grounded observations, exact full-file ranges, and deterministic
  coverage admission;
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

Rewrite the named current test
`test_public_remove_docs_cover_every_managed_config_surface` to retain
still-valid public removal coverage and replace only retired
permission-controller/repair-agent expectations. The Task 7 rewrite similarly
updates the named current package/distribution assertions without broadening
the public compatibility surface. Rewrite
`test_readmes_describe_agent_review_eligibility_truthfully` to require native
provider/user/project permission ownership while retaining credential and
provider-log boundaries; do not keep granular sandbox-approval requirements.

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
worktree fingerprint before dispatch. The leader-only fingerprint uses the
design's exact length-prefixed tagged-record algorithm over current `HEAD`,
full `GIT_OPTIONAL_LOCKS=0` porcelain status, binary/full-index staged and
unstaged diffs, and NUL-sorted nonignored untracked path plus content/link-text
digests. An unreadable or unsupported untracked entry stops the gate. It is an
operational record only: do not restore the retired
`canonical_git_visible_fingerprint` helper or ask provider legs to execute Git.

Dispatch:

- current owner-authorized Claude Opus route;
- current accepted Google-family Pro High route without a TRIAD permission override; and
- fresh Codex default child with `fork_turns="none"` and the current approved formal-review model/effort.

Every family reviews every batch and returns valid receipts. If native AGY
reports `permission-unavailable`, stop the formal gate and report the required
user/project permission decision. This is post-dispatch and cannot activate
Gemini fallback in the same round; do not insert a bypass or count a different
family twice. A separately authorized Gemini formal fallback remains limited
to proven pre-dispatch AGY unavailability.

Expected: three valid family coverages, no unresolved path, identical pre/post
candidate digest, identical pre/post canonical-worktree fingerprint, and either
three `SAFE` verdicts or a stopped release with evidence-backed findings.

- [ ] **Step 9: Correct accepted findings through new RED/GREEN cycles**

For each reproduced defect or approved underspecification, add one focused failing test, implement the minimum correction, run neighboring tests, and commit. If candidate bytes change, rebuild evidence and run a fresh complete three-family round.

Expected: no finding is applied solely because a provider requested it, and no changed candidate reuses a prior verdict.

- [ ] **Step 10: Install, compare cache bytes, and prove native inheritance**

Record the root session's current effective permission profile and canonical
worktree fingerprint using the same leader-only algorithm from Step 8. Create
one owner-authorized disposable directory with
`mktemp -d` outside the worktree. Spawn a fresh default child with
`fork_turns="none"`, the current approved model, and low effort; ask it to
write one exact marker only in that directory. Record requested model/effort,
child identity, runtime-exposed actual values or `unexposed`, the marker result,
and the unchanged worktree fingerprint. This is a capability probe for the
current parent mode, not a request to broaden it. Remove only that exact marker
and disposable directory after recording the result.

Install the local marketplace snapshot, run bootstrap through the authenticated
login environment, and compare every Git-tracked source path with the exact
`0.2.532` cache path:

```bash
codex plugin add triad-codex-dispatch@triad-codex-dispatch --json
codex plugin list --json
scripts/bootstrap.sh --install

set -eu
triad_source_root="$(pwd -P)"
triad_cache_root="/Users/chaniri/.codex/plugins/cache/triad-codex-dispatch/triad-codex-dispatch/0.2.532"
triad_hash_dir="$(mktemp -d /private/tmp/triad-02532-cache-proof.XXXXXX)"
git ls-files -z > "$triad_hash_dir/paths.z"
(cd "$triad_source_root" && xargs -0 shasum -a 256 < "$triad_hash_dir/paths.z") > "$triad_hash_dir/source.manifest"
(cd "$triad_cache_root" && xargs -0 shasum -a 256 < "$triad_hash_dir/paths.z") > "$triad_hash_dir/cache.manifest"
cmp -s "$triad_hash_dir/source.manifest" "$triad_hash_dir/cache.manifest"
shasum -a 256 "$triad_hash_dir/source.manifest" "$triad_hash_dir/cache.manifest"

codex exec --ephemeral 'Return exactly TRIAD_02532_NATIVE_FULL_COVERAGE if the installed triad-cross-family-review skill requires native permission inheritance and all-family full affected-source coverage.'
```

Expected: the plugin reports installed/enabled `0.2.532`, every tracked source
path exists in cache, source/cache manifests and their SHA-256 values match,
the bounded child behavior matches the recorded parent mode, and fresh output
is exactly `TRIAD_02532_NATIVE_FULL_COVERAGE`. Record both manifest hashes,
cache path, child proof, and ephemeral output in the release notes and
current-state handoff.

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
