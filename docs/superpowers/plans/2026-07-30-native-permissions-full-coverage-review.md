# Native Permissions and Full-Coverage Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Step checkboxes express the frozen execution order; record progress only in the plan-scoped ignored SDD ledger and do not edit these tracked plan bytes during implementation.

**Goal:** Make TRIAD inherit the developer's active provider permissions and require every model family to review every changed and affected production source with digest-bound per-path evidence.

**Architecture:** Add two focused Python modules: one binds an exact Git candidate state to immutable change evidence and validates it, and one validates per-family coverage receipts. Remove wrapper and bootstrap permission-controller behavior while retaining data authorization, executable/path validation, mutation detection, result custody, and explicit legacy packet compatibility.

**Tech Stack:** Python 3.12, Pydantic 2, pytest, Bash 3.2-compatible bootstrap, Markdown skills and public documentation, Codex plugin manifest.

## Global Constraints

- Work in `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`.
- The root leader commits the final approved plan correction on the current
  clean `release/0.2.530` planning branch and records that HEAD before Task 1.
  Create `release/0.2.532` from that exact commit before production edits and
  verify `1744c43c52b80cf2e28201a1c67d50611480f760` is its ancestor.
- Preserve the pre-existing commits and unrelated user-owned files.
- After the admitted planning commit, keep this tracked plan byte-for-byte
  frozen. Do not tick its checkboxes. Record every task, review, fix round, and
  completion only in the plan-scoped ignored SDD ledger so progress tracking
  cannot dirty or invalidate the release candidate.
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
push, PR creation, merge, tag, or release, run a fresh
`batched-full-coverage` pre-merge round with the same three families and the
same exact no-exclusion test-source
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

For each verified finding, record one leader triage:
`REPRODUCED`, `REACHABLE_UNPROVEN`, `OUT_OF_SCOPE_OR_SPECULATIVE`, or
`DESIGN_CHANGE`. A failed reproduction remains `REACHABLE_UNPROVEN` unless
direct evidence establishes another class. Severity controls blocking; triage
controls code authorization and never converts a blocking result into `SAFE`.
When explicit reviewed bytes prove that the claimed trigger is absent or
excluded by the approved boundary, classify it `OUT_OF_SCOPE_OR_SPECULATIVE`;
otherwise retain `REACHABLE_UNPROVEN`. A refuted disposition is not a fifth
triage label.

After each complete valid three-family round, record exactly one round state:
`CLEAN`, `CONVERGING`, `OSCILLATING`, or `OWNER_DECISION`. Use `CONFLICTED`
only as an item state for surviving incompatible claims. These records never
replace `coverage-admission.json`, release an old blocking verdict, or
authorize implementation, merge, or release. A new complete round requires
corrected candidate bytes or material new digest-bound evidence.
Apply the states in this order: `CLEAN`; `OWNER_DECISION` when any remaining
item requires the owner; `OSCILLATING` when no material new evidence remains;
otherwise `CONVERGING` when reproduced evidence remains.

Keep the leader residual ledger outside `prepared/` and the provider-response
custody tree at `_runs/reviews/<id>/residuals.md`. Identify claims by
review-relative path plus trigger. Record family, round, severity, triage,
reproduction evidence, disposition, and direct conflict without adding a
receipt field or machine-admission input.

Before implementing even a `REPRODUCED` claim, stop for owner approval if the
logical fix adds a runtime guard/fallback/retry/lock/validation layer, adds a
production dependency/configuration/environment/public protocol, changes
production paths outside the impact closure beyond mechanical caller/import
updates, or exceeds 30 added-plus-removed non-generated production lines.
Count the scoped logical-fix diff deterministically. Files already listed in
the approved File Map remain inside the approved correction boundary.

The pre-implementation native source-observation transport spike is complete
and recorded in
`docs/status/2026-07-30-native-source-observation-spike.md`. Claude, AGY, and
fresh Codex each returned the exact generated source observation without
mutation. The AGY negative control proved that provider-side command hashing is
not a viable common requirement.

## File Map

### New focused modules

- Inspect unchanged `.gitignore`: its tracked `_runs/` rule is the required
  review-artifact boundary. Task 1 Step 1 proves every exact planned artifact
  path is ignored before implementation; modify this file only if that live
  proof fails and the owner approves the resulting File Map change.
- Create `bin/review_evidence.py`: deterministic evidence preparation, parsing, hashing, batching, validation, and CLI.
- Create `bin/review_coverage.py`: Pydantic receipt models and full-family admission.
- Create `tests/test_review_evidence.py`: evidence-format, hostile-path, digest, and large-diff tests.
- Create `tests/test_review_coverage.py`: path-evidence and three-family coverage tests.

### Native provider transport

- Modify `bin/_common.py:55-87,211,269-270,296-297,398-406,428-430,1827,2486-2497,2623-2624,2637-2811,2935`: add the terminal `permission-unavailable` classification, keep custody/source and native repair comments current, remove the stale AGY-settings-transaction and legacy shell-entry activation descriptions, and let `apply_classifier_patch` receive the owner CLI's already validated explicit classifier extension path.
- Inspect unchanged `bin/_pty.py` to preserve the exact `PtyStartError` and
  `run_via_pty` contracts used by the AGY wrapper and PTY tests.
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

- Modify `bin/bootstrap_repair.py:16-50,97-123,652-772,1411-1704,1760-1857,1969-2320`: retain exact removal and generic transaction helpers; retire repair-agent, installed apply-launcher, profile/rule/config-fragment creation, and shell-entry installation/registration.
- Modify `scripts/bootstrap.sh:16-222,381-428,540-838,987-997,1086-2243`: install wrapper launchers only, clean exact legacy artifacts, delete the shell-entry preflight/install surface, and stop generating Codex permission state.
- Modify `bin/apply_patch.py:1-75`: describe the proposal-only native child,
  require `--classifier-file`, and reject a relative or symlinked classifier
  leaf or ancestor before delegating its validated absolute path.
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
- Inspect all four `skills/*/agents/openai.yaml` files unchanged. Their current
  provider-neutral prompts already delegate result-profile details to the
  skills and are not stale for this change; do not regenerate them.
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
- Modify only the active behavioral-contract rows `Impact`, `Default approval
  path`, and `Fail-closed posture`, plus the two active pre-R14
  statements beginning `Provider read-only policy remains intact` and `Test
  source is not sent` in
  `docs/status/2026-07-22-formal-review-routing-verification.md`. Label their
  former provider-read-only, plugin-owned launcher-rule, and
  test-source-exclusion claims as pre-0.2.532 history, and state that 0.2.532
  inherits provider permissions, generates no Codex permission state, and
  includes all repository test source in formal plan/pre-merge rounds. Preserve the
  file's `Updated: 2026-07-24` date and every dated R14-R17 ledger literal as
  historical evidence.
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
- Consumes: an immutable prepared review root inside its canonical Git
  worktree, an exact full base commit, a captured canonical unified diff file,
  one canonical required-source boundary JSON object, the canonical
  `BatchReceipt` JSON Schema emitted by Task 2, and a
  leader-authored UTF-8 TSV with exact header
  `path	reason	reached_from	change_kind	previous_path`.
- Produces: `EvidenceSummary`, `CANDIDATE_STATE.json`,
  `REQUIRED_SOURCE_BOUNDARY.json`, `CHANGESET.md`, `IMPACT_CLOSURE.tsv`,
  `PATCH_INDEX.tsv`, `BATCH_RECEIPT.schema.json`,
  `MANIFEST.sha256`, deterministic patch shards, and batch manifests.
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
) -> EvidenceSummary: ...

def validate_review_evidence(
    review_root: Path,
    evidence_dir: Path,
) -> EvidenceSummary: ...

def _resolve_candidate_worktree(review_root: Path) -> Path: ...

def _require_ignored_candidate_path(repo_root: Path, path: Path) -> None: ...

def _canonical_worktree_fingerprint(repo_root: Path) -> str: ...

def _capture_candidate_state(
    review_root: Path,
    base_commit: str,
) -> tuple[CandidateState, bytes]: ...

def _require_prepared_sources_match_candidate(
    repo_root: Path,
    review_root: Path,
    affected_paths: Sequence[ImpactRow],
) -> None: ...
```

For every callable and CLI path, the canonical non-symlink evidence directory
must equal `review_root / "change-evidence"`. Reject an external path, an
alternate in-root path, or any symlinked component. For preparation, require a
canonical review root and parent, create only that exact absent output leaf,
and reject any existing output leaf before writing, including an empty or
non-empty directory, symlink, or non-directory, with
`EvidenceError("evidence directory exists")`. Validation and admission recheck
the same canonical equality before reading evidence.

Preparation accepts only an exact full hexadecimal commit object ID through
`base_commit`. Resolve the enclosing canonical Git worktree from
`review_root`; do not accept a caller-selected alternate repository path. The
object ID must be lowercase ASCII with the repository's full 40- or 64-digit
hash width reported by `git rev-parse --show-object-format`, resolve as a
commit, and be an ancestor of current `HEAD`. The
review root, diff input, impact input, and output leaf must all be ignored by
that worktree so evidence creation cannot change the candidate state. Reject
any nonignored untracked entry rather than omitting it from the candidate diff.

Use one bounded read-only capture routine in this module to compute the
design-defined tagged-record worktree fingerprint and a canonical diff from
`base_commit` to the current tracked worktree. Run Git with
`GIT_OPTIONAL_LOCKS=0`, `LC_ALL=C`, `-c core.quotepath=true`,
`-c diff.noprefix=false`, `-c diff.mnemonicPrefix=false`,
`-c diff.srcPrefix=a/`, `-c diff.dstPrefix=b/`, full binary indexes,
`--no-color`, no external diff or text conversion, `--unified=3`,
`--diff-algorithm=myers`, `--no-indent-heuristic`, and
`--find-renames=50%`. The supplied `diff_file` must be byte-identical to this
capture. Write the resolved base commit, current `HEAD`, fingerprint, and diff
SHA-256 as one compact sorted-key `CANDIDATE_STATE.json`; include it in the
change-evidence digest and manifest. Recompute the same state after prepare,
during validate, and transitively during coverage admission. Any mismatch
fails closed. This is the only new Git-backed behavior; do not add a general
repository abstraction or expose Git to provider legs.

Before emitting evidence, and again during validation and admission, compare
every non-deleted closure path in the prepared review root with the same
review-relative path in the resolved canonical candidate worktree. Open both
without following symlinks, require regular UTF-8 files, and require exact
bytes, SHA-256, byte count, and `splitlines()` line count. A deleted closure
path must be absent from both locations. This comparison covers changed bytes
outside visible hunks and every affected-unchanged file; a copied or stale
prepared source fails with `prepared source differs from candidate`. The
prepared directory is still the only directory exposed to reviewers. Require
exact set equality between every regular file below `review_root` outside
`output_dir` and every non-deleted closure path; an unlisted prepared regular
file fails with `prepared file lacks closure row`. Thus no production,
configuration, documentation, build, or test source is exposed as unbound
context. During validation/admission, map a symlink encountered at a declared
closure path in the earlier source-tree walk to
`prepared source differs from candidate` so the documented precedence is
stable and the referent is never followed.

When validation could classify one mutation more than one way, run checks in
this exact order: (1) persisted evidence and source digests against prepared
bytes, (2) prepared closure bytes against the canonical candidate worktree,
and (3) the recomputed complete candidate state. The source-digest regression
mutates a prepared closure source while leaving the candidate unchanged; the
stale-copy regression changes a prepared closure copy before manifest
completion; and the candidate-state regression mutates a tracked non-closure
candidate file. Do not make a stable diagnostic depend on incidental mapping
or filesystem traversal order.

Require `receipt_contract` to be an absolute ignored, non-symlink regular
UTF-8 file containing one canonical compact sorted-key JSON object plus LF.
Copy its exact bytes to
`change-evidence/BATCH_RECEIPT.schema.json`, include that artifact in the
change-evidence digest and manifest, and expose that canonical prepared path as
`EvidenceSummary.batch_receipt_contract_path`. Task 2 admission compares those
bytes to its current `BatchReceipt.model_json_schema()` output, so a stale or
substitute contract cannot admit a round.

Require `required_source_boundary` to be an absolute ignored, non-symlink
regular UTF-8 file containing exactly one compact sorted-key JSON object plus
LF with shape `{"paths":[...],"roots":[...]}`. Roots and paths are canonical
review-relative UTF-8 strings, arrays are sorted by UTF-8 bytes with no
duplicate/overlapping roots or paths, and every path lies below exactly one
root. In the canonical candidate worktree and fixed Git environment, capture
the raw NUL inventories from `git ls-files -z --cached -- <roots...>` and
`git ls-files -z --deleted -- <roots...>`. Define the current tracked boundary
as the cached set minus the worktree-deleted set, sorted by UTF-8 path bytes,
and require exact equality with `paths`. This admits an unstaged tracked
deletion only as deleted diff evidence, never as a current boundary path.
Reject missing, extra, untracked, non-regular, symlinked, or non-UTF-8 current
entries as `required source boundary mismatch`. Copy the exact
bytes to `change-evidence/REQUIRED_SOURCE_BOUNDARY.json` and bind them into the
manifest and change-evidence digest. Every current boundary path must exist in
the prepared root and exactly one closure row; an unchanged path uses the
reserved `required-test-source` reason, while a changed path retains its one
canonical changed row. Validation and admission reopen the copied boundary,
rerun the same Git inventory, and recheck every row before reading receipts.

The persisted candidate-state bytes are exactly one sorted, separator-compact
JSON object plus one LF:

```json
{"base_commit":"<full-oid>","canonical_diff_sha256":"<sha256>","head_commit":"<full-oid>","worktree_fingerprint":"<sha256>"}
```

Use this candidate-binding and custody subset of the stable `EvidenceError`
messages: `invalid base commit`,
`leader path is not ignored`, `untracked candidate state`, `candidate diff
mismatch`, `candidate state mismatch`, `prepared source differs from
candidate`, `prepared file lacks closure row`, `invalid receipt contract`,
`required source boundary mismatch`, `non-UTF-8 source`, and `git candidate
capture failed`, plus `evidence directory exists` for any pre-existing prepare
output leaf. The named parsing and hostile-input tests below define their
inline diagnostics as equally stable; this subset is not an exhaustive list.
Every Git nonzero exit not already mapped to one of the narrower cases becomes
`git candidate capture failed`; never expose raw Git stderr in the stable CLI
diagnostic.

- CLI: resolve `toolkit_root` once as the canonical absolute root that owns the
  selected local or installed `triad-cross-family-review` skill, and replace
  `/absolute/toolkit-root` below with that exact value. Never resolve these
  modules relative to the developer worktree cwd.

```text
python3 /absolute/toolkit-root/bin/review_evidence.py prepare \
  --review-root /absolute/project/worktree/_runs/reviews/<id>/prepared \
  --base-commit <exact-full-commit-oid> \
  --diff-file /absolute/project/worktree/_runs/reviews/<id>/candidate.diff \
  --impact-input /absolute/project/worktree/_runs/reviews/<id>/impact-closure.tsv \
  --required-source-boundary /absolute/project/worktree/_runs/reviews/<id>/required-source-boundary.json \
  --receipt-contract /absolute/project/worktree/_runs/reviews/<id>/BATCH_RECEIPT.schema.json \
  --output-dir /absolute/project/worktree/_runs/reviews/<id>/prepared/change-evidence \
  --batch-byte-limit 262144

python3 /absolute/toolkit-root/bin/review_evidence.py validate \
  --review-root /absolute/project/worktree/_runs/reviews/<id>/prepared \
  --evidence-dir /absolute/project/worktree/_runs/reviews/<id>/prepared/change-evidence
```

Both subcommands are cwd-independent and accept only absolute input paths. On
success they exit 0, write nothing to stderr, and emit exactly one compact JSON
object to stdout with sorted keys `affected_source_count`, `base_commit`,
`batch_ids`, `batch_receipt_contract_path`, `canonical_diff_sha256`, `change_evidence_digest`,
`format_version`, `head_commit`, `patch_file_count`, `source_tree_digest`, and
`worktree_fingerprint`. `prepare` and the subsequent `validate` over the same
artifact emit byte-identical JSON. Argument errors and `EvidenceError` exit 2,
emit no success JSON or completed `MANIFEST.sha256`, and write one
`review-evidence: <reason>` diagnostic to stderr. Any partial output leaf is
invalid and must be discarded before retry rather than admitted or validated.

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
- Every `batches/<batch-id>.tsv` is normative and has this exact ordered
  header:
  `path\treason\tchange_kind\tcontent_sha256\tbyte_count\tline_count\tpatch_ids\timpact_edge_ids`.
  It contains exactly one row per source path assigned to that batch, with no
  duplicates, sorted by UTF-8 path bytes. `patch_ids` and `impact_edge_ids`
  are comma-separated canonical ID lists in sorted order; use `-` for an empty
  list, and canonical IDs never contain commas. Every row's assignment equals
  the same path's `batch_id` in `IMPACT_CLOSURE.tsv`.
- Enforce `reason == "changed"` if and only if `change_kind` is one of
  `modified`, `added`, `deleted`, or `renamed`; `affected-unchanged` requires a
  non-`changed` reason. Receipt hunk/edge rules key on `change_kind` only.
- `path` alone remains the coverage key. `change_kind` and `previous_path` are
  required deletion/rename provenance fields, not a composite
  `(path, change_kind)` key.
- For decoded UTF-8 current source, compute `line_count` exactly as
  `len(text.splitlines())`; test newline-terminated, unterminated, and
  newline-only files. Before computing it, reject the non-LF Unicode/Python
  line separators U+000B, U+000C, U+001C, U+001D, U+001E, U+0085, U+2028,
  and U+2029 with stable `unsupported source line separator`; this keeps the
  accepted `splitlines()` model aligned with unified-diff and provider line
  numbering without adding a second line codec.
- Each affected-unchanged path records one canonical, leader-selected
  reproducible proof edge. Do not duplicate path rows or add a multi-edge
  protocol; full source coverage, not exhaustive graph-edge enumeration, is
  the release requirement.
- `reason=required-test-source` is reserved for a current tracked regular file
  included solely by an exact owner/project no-exclusion test-source boundary.
  It uses `change_kind=affected-unchanged`, `previous_path=-`, and exact
  `reached_from=owner-approved-no-exclusion-test-boundary`; its deterministic
  impact-edge ID, batch assignment, full-file observation, and family receipt
  requirements are identical to every other affected-unchanged row. A changed
  or deleted test path remains `reason=changed` and is not duplicated.
- `DIFF_FILE_SECTIONS_PER_GROUP = 100`. File sections 1-100 are `group-0001`,
  101-200 are `group-0002`, and so on; `GROUP_COUNT` is the exact number of
  non-empty groups. `DIFF_FILE_SECTION_COUNT` counts canonical `diff --git`
  sections. `PATCH_FILE_COUNT` counts actual patch artifacts and equals
  `len(patch_shards)` / the `PATCH_INDEX.tsv` row count; the two counts differ
  when one section has multiple hunks.
- Source files remain complete in the prepared root. An oversized file receives a single-path batch; provider file-read ranges may bound individual tool outputs, but every range remains required.
- `EvidenceSummary.review_root` is the canonical prepared root used to
  revalidate source observations and finding locations. The coverage CLI
  receives `--review-root` once to call `validate_review_evidence`; downstream
  admission uses only the validated `EvidenceSummary.review_root`.

- [ ] **Step 1: Prove plan provenance, create the branch, and record the Python boundary**

Run from `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`:

```bash
set -eu
triad_planning_branch="$(git branch --show-current)"
triad_planning_head="$(git rev-parse HEAD)"
triad_repo_root="$(git rev-parse --show-toplevel)"
triad_ignore_root="$triad_repo_root/_runs/reviews/0.2.532-ignore-preflight"
test "$triad_planning_branch" = "release/0.2.530"
test "$triad_repo_root" = "/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability"
test -z "$(git status --short)"
git ls-files --error-unmatch .gitignore
for triad_ignored_path in \
  "$triad_ignore_root" \
  "$triad_ignore_root/candidate.diff" \
  "$triad_ignore_root/impact-closure.tsv" \
  "$triad_ignore_root/BATCH_RECEIPT.schema.json" \
  "$triad_ignore_root/required-source-boundary.json" \
  "$triad_ignore_root/coverage-admission.json" \
  "$triad_ignore_root/prepared" \
  "$triad_ignore_root/prepared/change-evidence"
do
  git check-ignore -q --no-index "$triad_ignored_path"
done
shasum -a 256 .gitignore
git merge-base --is-ancestor 1744c43c52b80cf2e28201a1c67d50611480f760 "$triad_planning_head"
git show --no-patch --format='%H %s' "$triad_planning_head"
git switch -c release/0.2.532 "$triad_planning_head"
git status -sb
```

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'command -v python3; python3 --version; python3 -m pytest --version'
```

Record `triad_planning_branch`, `triad_planning_head`, the ancestry result,
tracked `.gitignore` SHA-256, all eight successful ignore probes, and the new
branch HEAD in the SDD ledger. Expected: the final committed plan is the exact
branch point, branch `release/0.2.532` is clean, every review artifact path is
ignored by the tracked `_runs/` rule, literal `python3` resolves through the
login shell, and pytest is available. If any ignore probe fails, stop before
creating the implementation branch or Task 1 tests; do not weaken the evidence
requirement or edit `.gitignore` outside a newly reviewed File Map change.

- [ ] **Step 2: Write the failing format and determinism tests**

Create `tests/test_review_evidence.py` with focused tests beginning with:

```python
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))

import review_evidence


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


def _candidate_fixture(
    tmp_path: Path,
    relative_path: str,
    old: bytes,
    new: bytes,
) -> tuple[Path, Path, Path, Path, Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
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
    diff_file.write_bytes(
        _git(
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
    )
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


def test_prepare_emits_named_headers_and_deterministic_batches(tmp_path: Path) -> None:
    (
        review_root,
        diff_file,
        impact,
        required_source_boundary,
        receipt_contract,
        base_commit,
    ) = _candidate_fixture(
        tmp_path,
        "src/caller.py",
        b"def caller():\n    return old()\n",
        b"def caller():\n    return changed()\n",
    )

    summary = review_evidence.prepare_review_evidence(
        review_root,
        diff_file,
        impact,
        required_source_boundary,
        receipt_contract,
        review_root / "change-evidence",
        base_commit=base_commit,
        batch_byte_limit=262144,
    )

    changeset = (review_root / "change-evidence" / "CHANGESET.md").read_text()
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
        review_root, review_root / "change-evidence"
    ) == summary


def test_prepare_rejects_symlinked_affected_source(tmp_path: Path) -> None:
    (
        review_root,
        diff_file,
        impact,
        required_source_boundary,
        receipt_contract,
        base_commit,
    ) = _candidate_fixture(
        tmp_path, "linked.py", b"secret = False\n", b"secret = True\n"
    )
    outside = tmp_path / "outside.py"
    outside.write_text("secret = True\n", encoding="utf-8")
    (review_root / "linked.py").unlink()
    (review_root / "linked.py").symlink_to(outside)

    with pytest.raises(
        review_evidence.EvidenceError,
        match="prepared source differs from candidate",
    ):
        review_evidence.prepare_review_evidence(
            review_root,
            diff_file,
            impact,
            required_source_boundary,
            receipt_contract,
            review_root / "change-evidence",
            base_commit=base_commit,
            batch_byte_limit=262144,
        )
```

A non-regular or symlinked prepared closure source reaches the prepared-source
comparison before candidate-state recomputation and fails with the existing
stable `EvidenceError("prepared source differs from candidate")`; do not add a
second `regular file` diagnostic.

Implement the following additional named tests in the same file:

- `test_prepare_and_validate_cli_are_cwd_independent`: invoke the absolute
  `bin/review_evidence.py` path with `sys.executable` from an unrelated cwd,
  pass only absolute `prepare` arguments, require exit 0 and empty stderr, then
  invoke `validate` and require byte-identical compact JSON with exactly the
  eleven specified sorted keys and the expected commits, fingerprint, diff
  digest, receipt-contract path, counts, batch IDs, and evidence digests.
- `test_cli_rejects_noncanonical_paths_and_missing_artifacts`: invoke each
  subcommand as a real subprocess; require exit 2, empty stdout, one stable
  `review-evidence: <reason>` stderr line, no completed `MANIFEST.sha256`, and
  no validation admission for a relative argument, alternate or external
  output/evidence path, and validation before a successful preparation.
- `test_prepare_rejects_existing_evidence_leaf`: attempt preparation with an
  empty existing canonical output directory and then a non-empty one carrying
  a stale patch shard; require `EvidenceError("evidence directory exists")`,
  no success JSON, and no completed manifest. Retry succeeds only after the
  leader discards the entire partial leaf.

- `test_prepare_rejects_subset_of_canonical_candidate_diff`: modify two tracked
  production files after the exact base commit, supply a valid-looking diff and
  closure for only one, and require `EvidenceError("candidate diff mismatch")`
  before `MANIFEST.sha256` exists.
- `test_candidate_diff_prefixes_ignore_user_git_config`: set repository-local
  `diff.noprefix=true`, `diff.mnemonicPrefix=true`, and hostile
  `diff.srcPrefix`/`diff.dstPrefix` values, then require preparation and
  validation to retain canonical `diff --git a/... b/...` bytes and the same
  patch IDs as the default-config fixture.
- `test_candidate_state_rejects_symbolic_unknown_or_nonancestor_base`: pass
  `HEAD`, a short object ID, an unknown full object ID, and a full commit from a
  disconnected history; require `EvidenceError("invalid base commit")` and no
  completed evidence.
- `test_candidate_state_rejects_nonignored_untracked_entry`: add a nonignored
  untracked regular file and require `EvidenceError("untracked candidate state")`.
- `test_candidate_inputs_and_review_root_must_be_git_ignored`: move each input
  or the review root outside the committed ignore boundary and require failure
  before evidence creation.
- `test_validate_rejects_candidate_state_mutation`: prepare valid evidence,
  mutate one tracked non-closure worktree byte so the prepared-source check is
  unaffected, and require
  `EvidenceError("candidate state mismatch")`; restore the byte, tamper each
  `CANDIDATE_STATE.json` field in turn, and require the same failure class.
- `test_prepare_rejects_stale_or_miscopied_prepared_source`: first alter a
  changed file only on a line outside every canonical hunk in its prepared
  copy, then use an affected-unchanged prepared copy whose bytes differ from
  the same canonical candidate-worktree path; require
  `EvidenceError("prepared source differs from candidate")` before a completed
  manifest in both cases.
- `test_prepare_rejects_unlisted_prepared_regular_file`: add one regular file
  below `review_root` and outside `change-evidence` without an impact-closure
  row; require `EvidenceError("prepared file lacks closure row")` before any
  evidence output. The accepted case proves exact set equality between every
  prepared regular source file and every non-deleted closure path.
- `test_required_test_source_rows_cover_exact_current_test_inventory`: build a
  candidate with one changed, one unstaged worktree-deleted, and two unchanged
  tracked files below `tests/`; require the changed/deleted rows once as
  `reason=changed` and
  each current unchanged file once as `reason=required-test-source` with exact
  `reached_from=owner-approved-no-exclusion-test-boundary`. Prove every current
  test path receives a batch and later family receipt evidence; omitting one,
  duplicating one, or assigning the reserved reason outside the supplied
  `tests/` boundary fails before output.
- `test_required_source_boundary_is_canonical_git_bound_and_digest_bound`:
  reject a relative or symlinked input, malformed/noncanonical JSON,
  duplicate/overlapping roots, paths outside roots, and any missing/extra Git
  inventory entry with `EvidenceError("required source boundary mismatch")`;
  assert accepted exact bytes are copied to
  `REQUIRED_SOURCE_BOUNDARY.json` and covered by both the change-evidence
  digest and manifest, then prove validation rejects candidate inventory drift.
- `test_receipt_contract_is_canonical_and_digest_bound`: reject a symlink,
  non-object JSON, non-canonical serialization, and non-UTF-8 contract with
  `EvidenceError("invalid receipt contract")`; then assert the accepted exact
  bytes appear at `BATCH_RECEIPT.schema.json` and are covered by both the
  change-evidence digest and `MANIFEST.sha256`.

- `test_prepare_rejects_duplicate_impact_paths`: repeat `src/caller.py` in the
  TSV and require `EvidenceError("duplicate affected path")`.
- `test_prepare_rejects_unsupported_impact_reason`: use `reason=guessed` and
  require `EvidenceError("unsupported impact reason")`.
- `test_prepare_rejects_traversal_path`: use `../outside.py` and require
  `EvidenceError("invalid review-relative path")`.
- `test_prepare_rejects_control_characters_in_tsv_path_fields`: parameterize
  NUL, LF, CR, and TAB across `path`, `reached_from`, and the decoded old-side
  `previous_path` of a rename, requiring
  `EvidenceError("control character in TSV field")` and no completed output.
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
- `test_prepare_rejects_unsupported_source_line_separators`: parameterize
  U+000B, U+000C, U+001C, U+001D, U+001E, U+0085, U+2028, and U+2029 in a
  changed current source and then an affected-unchanged current source;
  require `EvidenceError("unsupported source line separator")` and no
  completed manifest in every case.
- `test_prepare_rejects_non_utf8_current_source`: use invalid UTF-8 bytes for
  a changed current source and then an affected-unchanged current source;
  require `EvidenceError("non-UTF-8 source")` and no completed manifest in
  both cases.
- `test_batch_manifest_has_exact_header_and_ordered_rows`: require the exact
  normative header, UTF-8 path-byte row order, sorted comma-separated ID
  encoding with `-` for empty lists, no duplicate paths, and exact agreement
  with each closure row's `batch_id`.
- `test_oversized_source_receives_complete_single_path_batch`: set the byte
  limit below one source file's size and assert one batch contains that
  complete path with the exact byte and line counts and no shard records.
- `test_validate_rejects_source_digest_mutation`: prepare valid evidence,
  change one affected source only in the prepared review root while leaving
  the canonical candidate unchanged, and require
  `EvidenceError("source digest mismatch")`.
- `test_validate_and_admit_reject_symlinked_prepared_closure_source`: after a
  valid prepare, replace one declared closure source with a symlink and require
  both direct validation and transitive admission to fail with
  `EvidenceError("prepared source differs from candidate")`; preserve the
  referent bytes and do not let the earlier source-tree digest walk emit a
  competing diagnostic.
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
- `test_unified_hunk_must_match_current_source`: independently reject a
  malformed header, old/new body-count mismatch, out-of-range new-side span,
  context/added body mismatch, and incorrect no-final-newline marker with
  stable `EvidenceError("invalid unified hunk")`; admit added
  `@@ -0,0 +1,N @@`, deleted `@@ -1,N +0,0 @@`, and nonzero-start
  zero-count insertion/deletion headers; admit and byte-preserve a standard
  optional section/function heading after the closing `@@`; include 99
  one-hunk sections followed by one two-hunk section and assert both hunks
  remain in `group-0001`, `DIFF_FILE_SECTION_COUNT=100`, and
  `PATCH_FILE_COUNT=101`.

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
    "required-test-source",
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

Add `main(argv: Sequence[str] | None = None) -> int` with `argparse` subcommands
`prepare` and `validate`, including the required absolute
`--required-source-boundary` and `--receipt-contract` preparation arguments,
plus the normal
`if __name__ == "__main__"` exit.
Render success JSON from the validated `EvidenceSummary` only after the
operation completes. Keep stdout empty on every error, map argument and
`EvidenceError` failures to exit 2 and the one-line stderr contract above, and
leave unexpected exceptions unclassified rather than printing success.

Import `field` from `dataclasses`; `EvidenceSummary.review_root` is
`field(compare=False)` so deterministic summaries prepared under separate
roots compare by their evidence content rather than their custody location.

Implement the candidate-state capture as private, focused helpers in this
module. Resolve `git rev-parse --show-toplevel` from `review_root`, verify that
the supplied full object ID is a commit without accepting a symbolic or short
ref, require `git check-ignore` success for every leader artifact path, reject
nonignored `git ls-files --others --exclude-standard -z` output, and run the
exact canonical diff argv specified above. Invoke Git through argv arrays with
the fixed environment; never a shell. The same helper produces the existing
length-prefixed tagged-record fingerprint. Capture before output, compare
again after output, and persist only the four path-independent fields in
`CANDIDATE_STATE.json`.

After closure parsing and before any output, compare each current closure
source against the same canonical worktree path through
`_require_prepared_sources_match_candidate`. Repeat that exact comparison in
validation after reopening the closure. Do not infer equivalence from a hunk,
manifest row, or digest generated from the prepared copy alone. Parse the
receipt contract once, require canonical compact sorted-key JSON-object bytes
plus LF, and copy those exact bytes into the evidence directory.

Open inputs with no symlink following, reject non-regular files and non-UTF-8
current production source, sort impact rows by UTF-8 path bytes, pack them
greedily into `batch-0001` onward, write all output through same-directory
temporary files plus `os.replace`, and derive `MANIFEST.sha256` from every
evidence file except itself. Validation reopens and rehashes the current source
and every evidence artifact. Reject NUL, LF, CR, and TAB in `path`,
`reached_from`, and every `previous_path` other than `-` before TSV emission;
decode both old- and new-side Git-quoted path fields only far enough to detect
and reject those controls. Spaces, quotes, backticks, and literal `$()` remain
data and execute nothing. This is an intentional
`0.2.532` input limit: do not silently omit a path or admit partial coverage.

For each supported textual hunk, parse the complete
`@@ -old_start,old_count +new_start,new_count @@` form (including the
single-line omitted-count shorthand). Accept the standard optional text after
the closing `@@` as an opaque section/function heading. Preserve its exact
bytes in the shard, but do not interpret it or include it in range/body
counts. Require header old/new counts to equal the respective
deletion/context and addition/context body counts. For a
positive new count, require `new_start >= 1` and
`new_start + new_count - 1 <= line_count`; compare the ordered context plus
added lines against that exact inclusive current-source range. For a zero new
count, require `0 <= new_start <= line_count` and compare the empty new-side
body against the empty boundary after `new_start` lines; do not require a zero
start because a zero-count deletion can occur within a current file. For a
deleted row only, use its already specified empty byte string as the new-side
comparison source while still requiring the current path to be absent. Require
`old_start >= 1` for a positive old count and `old_start >= 0` for a zero old
count; a zero-count insertion may have a nonzero old start. Include
`\ No newline at end of file` semantics in the exact comparison. Reject
malformed, count-mismatched, out-of-range, or content-mismatched hunks with
`EvidenceError("invalid unified hunk")`. Implement only this bounded
unified-text validator; do not add a general patch-application engine.

Before any output or evidence read, require the canonical non-symlink evidence
directory to equal `review_root / "change-evidence"` exactly. This containment
check is custody validation, not a generalized filesystem sandbox.

Define `source_tree_digest` as SHA-256 over canonical
`relative-path NUL file-sha256 NUL byte-count LF` records for every regular file
below `review_root` except `output_dir`, sorted by UTF-8 path bytes. Reject every
symlink encountered during that walk. Define `change_evidence_digest` with the
same record encoding over `CANDIDATE_STATE.json`,
`REQUIRED_SOURCE_BOUNDARY.json`, `BATCH_RECEIPT.schema.json`, plus generated
patch, index, closure, and batch artifacts before `CHANGESET.md` and
`MANIFEST.sha256` are
written. Then
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

def validate_family_receipts(
    evidence: EvidenceSummary,
    family: str,
    receipt_paths: Sequence[Path],
) -> FamilyCoverage: ...

def admit_full_coverage(
    evidence: EvidenceSummary,
    family_coverages: Sequence[FamilyCoverage],
) -> CoverageAdmission: ...

def reject_duplicate_json_members(json_bytes: bytes) -> None: ...

def canonical_admission_bytes(
    admission: CoverageAdmission | CoverageAdmissionWire,
) -> bytes: ...

def parse_canonical_owned_admission(
    json_bytes: bytes,
) -> CoverageAdmissionWire: ...
```

- Operational CLI:

```text
python3 /absolute/toolkit-root/bin/review_coverage.py schema \
  --output /absolute/project/worktree/_runs/reviews/<id>/BATCH_RECEIPT.schema.json

python3 /absolute/toolkit-root/bin/review_coverage.py admit \
  --review-root /absolute/project/worktree/_runs/reviews/<id>/prepared \
  --evidence-dir /absolute/project/worktree/_runs/reviews/<id>/prepared/change-evidence \
  --receipts-root /absolute/project/worktree/_runs/reviews/<id>/results \
  --output /absolute/project/worktree/_runs/reviews/<id>/coverage-admission.json
```

The `schema` subcommand writes exactly the canonical compact sorted-key JSON
from `BatchReceipt.model_json_schema()` plus one LF through an atomic replace.
It accepts one absolute, ignored, non-symlink output path, emits a compact
sorted-key stdout receipt containing that path and its SHA-256, and writes
nothing to stderr on success. Evidence preparation copies those exact bytes.
The `admit --output` path has the same absolute, ignored, non-symlink custody
requirements and must also be outside `review-root`; reject relative,
nonignored, symlinked, or prepared-root output targets before evidence
validation or any write. After that custody check and before validating the
current evidence or receipts, an existing regular output leaf is owned only
when its bytes are exact canonical JSON for the recursive
`CoverageAdmissionWire` shape, `admitted` is `true`, and no top-level or nested
field is missing, extra, or duplicated. Build the wire value with
`CoverageAdmissionWire.model_validate(admission, from_attributes=True)`.
Serialize only `wire.model_dump(mode="json")` with
`json.dumps(..., ensure_ascii=False, allow_nan=False, sort_keys=True,
separators=(",", ":"))`, UTF-8 encode it, and append exactly one LF. This is
the sole admission serializer. Parse an existing leaf with the duplicate-key
pass and `CoverageAdmissionWire.model_validate_json(..., strict=True)`, then
require reserialization through that exact function to equal every original
byte before treating it as owned. Unlink only that
exact verified prior leaf; never follow or remove a symlink, referent,
directory, noncanonical file, or foreign regular file. Refuse an unowned
existing leaf with `CoverageError("existing admission output is not owned")`
and preserve its bytes. A later validation failure therefore leaves the
canonical output absent instead of exposing a stale success. A successful
command publishes a fresh validated leaf through same-directory temporary
bytes plus atomic replace.
Before parsing receipts, `admit` compares the digest-bound prepared contract
with the current canonical model schema and fails with `receipt contract
mismatch` on any difference.

`receipts-root` contains exactly
`<family>/<batch-id>.json` for every combination of `claude`, `google`,
`codex`, and the validated batch IDs. Missing files, extra JSON files,
symlinks, and non-regular files are invalid. The `admit` command validates evidence,
each exact response byte stream, every family, and final admission, then
atomically writes canonical UTF-8 JSON. It exits nonzero and writes no admitted
artifact on any invalid or non-admitted result. This output is the sole
machine-admissible gate result; prose summaries cannot replace it. Its exact
top-level fields are `format_version`, `candidate_state`,
`source_tree_digest`, `change_evidence_digest`, `admitted`, and
`family_coverages`; the first four values are copied from the revalidated
`EvidenceSummary`, never from caller input or receipts.
The CLI first requires canonical `evidence-dir` equality with
`review-root/change-evidence`; an external, alternate, or symlinked evidence
path is invalid.

For every parsed receipt, require both its ordered `path_evidence.path` tuple
and its ordered `affected_surfaces_inspected` tuple to equal exactly the
ordered source paths assigned to `receipt.batch_id` in the validated closure.
Reject missing, extra, reordered, out-of-batch, or duplicate entries before
family aggregation. Patch artifact paths are evidence for their owning source
row and never appear as additional inspected surfaces. A global family union
cannot compensate for an invalid per-batch assignment.

- A `changed` row's `changed_hunks` set exactly equals its canonical
  `PATCH_INDEX.tsv` `patch_id` set. An omitted, extra, duplicated, or forged
  ID is rejected.
- A resolved affected-unchanged row's `verified_impact_edges` set exactly
  equals its expected `impact_edge_id` set. An unresolved affected-unchanged
  row may contain any subset of its expected IDs because an unverified edge is
  the reason the path remains unresolved. Extra, duplicated, or forged IDs
  are always rejected, and an unresolved disposition/path always blocks
  admission.
- Changed, added, deleted, and renamed rows have an empty
  `verified_impact_edges`; affected-unchanged rows have an empty
  `changed_hunks`.
- Every `PathEvidence.content_sha256` must equal its exact
  `ImpactRow.content_sha256`. Preparation computes that closure digest from the
  current source and validation reopens and rehashes it; a deleted row uses the
  SHA-256 of the empty byte string and accepts no other receipt digest.
- Every non-empty non-deleted path requires `line_start == 1` and
  `line_end == ImpactRow.line_count`; `symbols` are optional annotations and
  never replace full-file evidence. For UTF-8 source with non-whitespace
  content, `observation_line` names a line within the file and
  `source_observation` is a 1-160 character exact substring of that line; when
  the line has at least eight characters the observation has at least eight,
  and the observation contains at least one non-whitespace character. A
  whitespace-only observation is valid only under the validator-proven
  whitespace-only source exception below.
  Observation text is absent from reviewer-visible manifests and is
  revalidated from `EvidenceSummary.review_root`. A validator-proven zero-byte
  current source uses `line_start=line_end=None`,
  `observation_line=None`, and empty observation text. A non-empty
  whitespace-only source keeps its exact full-file line range and uses
  `observation_line=None` plus empty observation text only when the validator
  proves that condition. Deleted paths encode `source_observation=""`,
  `observation_line=None`, `line_start=None`, `line_end=None`, and empty
  `symbols`; they require no current-source observation, symbol, or line
  evidence.
- For a changed current source with at least one non-whitespace character and
  at least one line containing a non-whitespace character outside the
  validated new-side ranges of its canonical patch hunks, require
  `observation_line` to name such a non-whitespace outside-hunk line. The
  validator-proven whitespace-only exception takes precedence and retains
  `observation_line=None`. Parse ranges from the digest-bound patch artifacts;
  do not add another index field. If no line outside the validated hunk ranges
  contains a non-whitespace character, admit a patch-derived observation
  because the patch already contains every current line that can supply a
  valid non-whitespace observation and no valid outside-hunk substring exists.
  This is the only changed-path anti-echo exception; a whitespace-only but non-empty
  outside-hunk line does not block it.
- Every finding location is an exact review-relative `path:positive-line`.
  Admit only a current closure path or
  `change-evidence/patches/<group-id>/<patch-id>.patch`, re-open it without
  symlink following, and validate its expected digest, UTF-8 decoding, and line
  bound.
- `disposition="unresolved"`, a non-empty `unresolved_paths`, an
  `open_questions` entry, Critical/Major finding, or any `NOT-SAFE` receipt
  blocks admission.
- Cross-check each `PathEvidence.disposition` within its receipt/batch. A
  receipt finding location must map to a current path or canonical patch ID
  owned by that same batch. The disposition is `unresolved` exactly for a path
  in that receipt's `unresolved_paths`; otherwise it is `finding` exactly when
  one of that receipt's admitted findings maps to the path, and `no-finding`
  only when neither condition holds. Reject every cross-batch finding or
  contradictory disposition; a finding belongs in the receipt that owns the
  referenced path.
- Each provider returns exactly one strict `BatchReceipt` JSON document per
  batch. The leader saves the exact UTF-8 response bytes under a
  family/batch-specific result path and gives those paths to
  `validate_family_receipts`. Hash the original response bytes for custody.
  Deterministically accept either raw JSON or exactly one outer Markdown fence
  with an optional `json` info string, then pass only its inner bytes to strict
  JSON validation. Trim only outer ASCII whitespace for envelope detection.
  The opening line is exactly three backticks or three backticks plus `json`,
  and the final non-whitespace line is exactly three backticks. Slice only the
  bytes between those two complete outer lines. Do not scan for or reject a
  triple-backtick sequence inside those bytes: valid JSON strings may contain
  it. Strict JSON parsing still rejects nested or multiple top-level fence
  envelopes, leading/trailing prose, missing fields, and family/batch
  mismatch. Fresh Codex terminal text is persisted under the same rule; no
  wrapper responsibility is added.
  Before Pydantic validation, make one validation-only standard-library JSON
  pass over the raw-or-unfenced bytes with an `object_pairs_hook` that rejects
  a repeated member name in every object depth with
  `CoverageError("duplicate JSON member")`; discard the decoded result. This
  pass exists only to detect duplicate members and must not feed Python values
  to Pydantic. Then parse the same original raw-or-unfenced JSON bytes with
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
- `test_path_content_digest_must_match_closure`: forge and then stale a
  non-deleted `PathEvidence.content_sha256`, and give a deleted row a non-empty
  digest; require `path content digest mismatch` for each case;
- `test_changed_path_without_hunk_evidence_is_rejected` ->
  `changed path lacks hunk evidence`;
- `test_resolved_affected_unchanged_path_without_edge_is_rejected` ->
  `affected path lacks impact-edge evidence`;
- `test_changed_hunk_ids_are_exact`: use omitted, extra, duplicated, and forged
  IDs and require `changed hunk IDs do not match PATCH_INDEX`;
- `test_impact_edge_ids_are_exact`: for a resolved row use an omitted ID, and
  for either disposition use extra, duplicated, and forged IDs; require
  `impact edge IDs do not match closure`;
- `test_unresolved_edge_may_be_omitted_but_blocks_admission`: omit the expected
  edge only with `disposition="unresolved"` and the matching
  `unresolved_paths` entry, prove receipt validation succeeds, and prove final
  admission remains false;
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
  least eight characters; also reject an all-whitespace substring selected
  from a source that contains any non-whitespace character;
- `test_empty_source_observation_exception_is_narrow`: admit empty observation
  only for validator-proven empty or whitespace-only current source; require
  `line_start=line_end=None` for a zero-byte source but the exact full-file
  line range for a non-empty whitespace-only source, including a modified
  whitespace-only source with a line outside the validated hunk ranges;
- `test_changed_observation_outside_hunks_is_required`: reject a partial-file
  changed path whose observation line is inside a visible patch hunk when a
  non-whitespace outside-hunk line exists;
- `test_empty_outside_hunk_lines_allow_patch_observation`: construct a changed
  source whose only outside-hunk lines are empty or whitespace-only and admit
  a valid observation from a hunk; then give one outside line a
  non-whitespace character and require the observation to move outside the
  hunk;
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
  accept triple backticks inside `source_observation` and finding strings, and
  reject prose wrappers plus nested or multiple top-level fence envelopes;
- `test_receipt_rejects_duplicate_json_members_at_every_depth`: construct raw
  receipt bytes with conflicting duplicate `verdict` members, then separately
  with duplicate nested `path_evidence.disposition` and finding `severity`
  members; require exact `duplicate JSON member` before Pydantic admission,
  while keeping the original response bytes as the custody digest source;
- `test_deleted_row_requires_patch_only_path_evidence`: include a deleted row
  in the exact receipt path set with patch IDs and no current-source fields;
- `test_finding_location_is_source_grounded`: reject malformed, out-of-closure,
  out-of-range, and digest-mismatched source or canonical patch locations;
- `test_unresolved_disposition_is_rejected`: prove receipt validation produces
  unresolved family coverage, then require the `admit` CLI to fail with
  `unresolved path` and leave no output artifact;
- `test_missing_path_evidence_is_rejected`: omit one assigned closure path
  while preserving every other receipt field and require
  `missing covered path`;
- `test_each_receipt_requires_exact_assigned_path_set`: create two batches and
  first admit the exact ordered assignment; then reject concentrated evidence
  in one receipt with an empty second receipt, swapped batch evidence,
  out-of-batch paths, reordered paths, and duplicate paths before family
  aggregation;
- `test_each_receipt_requires_exact_assigned_inspected_surfaces`: over the same
  two batches require `affected_surfaces_inspected` to equal the exact ordered
  assigned source tuple and reject missing, extra, swapped, reordered, and
  duplicate entries;
- `test_not_safe_receipt_blocks_admission`: use a complete receipt matrix with
  one `NOT-SAFE` receipt and require non-admission plus no CLI output artifact;
- `test_critical_or_major_finding_blocks_admission`: parameterize Critical and
  Major source-grounded findings over otherwise complete receipts and require
  non-admission plus no CLI output artifact;
- `test_open_questions_block_admission`: add one non-empty open question to an
  otherwise complete receipt and require non-admission plus no CLI output
  artifact;
- `test_disposition_must_match_findings_and_unresolved_paths`: reject
  `finding` with no path-mapped finding, `no-finding` with a path-mapped
  finding, and either resolved disposition for a path in `unresolved_paths`;
- `test_finding_must_belong_to_receipt_batch`: reject a receipt whose finding
  location maps only to a path or canonical patch ID owned by another batch,
  even when that other receipt reports a compatible disposition;
- `test_admission_rejects_duplicate_family` -> `duplicate family coverage`;
- `test_admission_rejects_missing_family` -> `missing family coverage`.
- `test_admit_cli_is_the_only_persisted_gate`: build the exact three-family
  receipt tree, run `main(["admit", ...])`, assert exact canonical admitted
  UTF-8 bytes with compact sorted keys and one LF, reparse them through
  `CoverageAdmissionWire`, and require exact reserialization equality,
  then add one extra receipt and rerun against the same output path. Require
  the verified prior admission leaf to be removed before current validation,
  nonzero exit, and no stale canonical output. Separately place a foreign
  regular file and a symlink at the output leaf and require refusal without
  changing the file or referent. Also place semantically valid but pretty,
  reordered, no-final-LF, top-level-extra, nested-extra, missing-field, and
  duplicate-member admission variants at the leaf; require every variant to be
  preserved byte-for-byte as unowned.
- `test_schema_cli_emits_canonical_batch_receipt_contract`: run
  `main(["schema", ...])`, compare the exact file bytes with canonical
  `BatchReceipt.model_json_schema()` bytes, and assert the stdout path/digest
  receipt.
- `test_schema_output_requires_absolute_ignored_nonsymlink_path`: reject a
  relative output, a nonignored target, a symlink leaf, and a path with a
  symlinked ancestor before any write; require the original target/referent to
  remain byte-identical, then admit the exact absolute ignored round-root
  schema path and prove atomic publication.
- `test_admission_artifact_binds_candidate_state_and_evidence`: assert the
  emitted JSON contains the revalidated exact CandidateState, source-tree
  digest, and change-evidence digest; tamper each evidence-side binding and
  require nonzero exit with no admitted artifact.
- `test_admit_rejects_stale_receipt_contract`: replace the prepared schema with
  a valid but different JSON Schema; recompute the persisted
  `CHANGE_EVIDENCE_DIGEST`, update every receipt-declared
  `change_evidence_digest`, and repair the completed manifest so the round is
  otherwise self-consistent before requiring `receipt contract mismatch` with
  no admitted artifact.
- `test_admit_rejects_external_or_symlinked_evidence_dir`: point the CLI at an
  otherwise valid copied external evidence tree and then a symlinked
  `change-evidence` path; require nonzero exit and no admitted output.
- `test_admit_output_requires_ignored_external_nonsymlink_path`: reject a
  relative output, a nonignored path, a symlink, and any output under the
  immutable prepared review root before validation or writing; admit the exact
  ignored round-root `coverage-admission.json` sibling and prove atomic output.

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
and never coerce strings to numbers. Before any range or observation rule,
require each `PathEvidence.content_sha256` to equal its matched
`ImpactRow.content_sha256`, including the deleted-row empty digest; raise
`CoverageError("path content digest mismatch")` otherwise. Require
`1..ImpactRow.line_count` for
every non-empty non-deleted row, validate its bounded exact source observation
from `EvidenceSummary.review_root`, and keep symbols optional. Require a
changed-path observation outside validated current-side hunk ranges whenever
such an outside-hunk line contains a non-whitespace character; allow a
hunk-derived observation when no outside-hunk line contains a non-whitespace
character, including when outside-hunk lines are non-empty but whitespace-only.
Exempt validator-proven zero-byte current sources
and deleted rows from current observation/symbol/line requirements. Validate
finding locations against digest-bound current closure paths or canonical
patch artifacts, require each location to be owned by the same receipt batch,
and use only that receipt's findings and `unresolved_paths` to enforce exact
disposition consistency.
Require `evidence_dir` to be the canonical non-symlink
`review_root / "change-evidence"` before parsing receipts.
Implement only the exact `schema` and `admit` CLI subcommands and receipt
layout above; do not add a general orchestration framework or source sharding.
Before either CLI publishes output, apply the same canonical absolute,
Git-ignored, non-symlink leaf-and-ancestor validation. Perform this validation
before schema generation or evidence/receipt validation. The schema command
preserves every existing target or referent on refusal and atomically replaces
only its validated leaf. For `admit`, implement only the verified-prior-leaf
retirement lifecycle above: remove an exact canonical prior admitted artifact
before current validation, preserve and reject every foreign or symlinked
target, leave no canonical output on failure, and atomically publish the fresh
leaf only after successful admission.

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
- Modify: `bin/_common.py:55-87,296-297,2492-2497,2623-2624`
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
- The exact post-change preflight receipt keys are `provider_started`,
  `dispatch_phase`, `model`, `effort`, `pydantic`, `sealed_packet_root`,
  `expected_packet_sha256`, `route_args`, and `timeout`. Permission inheritance
  is the absence of permission-control fields, not a new receipt key.

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
    monkeypatch.setattr(
        wrapper._common,
        "extract_agy_answer_from_transcript",
        lambda *_args, **_kwargs: None,
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
    assert "permission-unavailable" not in wrapper._common.CLASSIFICATION_TOKENS
    assert "permission-unavailable" not in wrapper._common.REPAIR_CLASSIFICATION_TOKENS


def test_route_builder_contains_only_selector_and_effort() -> None:
    assert wrapper._build_route_args("Gemini 3.1 Pro (High)", None) == [
        "--model",
        "Gemini 3.1 Pro (High)",
    ]
```

Also create the RED
`test_antigravity_wrapper_source_contains_no_retired_settings_control` in this
step. Read `Path(wrapper.__file__)` and `Path(wrapper._common.__file__)`;
require `AGY_SETTINGS_LOCK_TIMEOUT`, `_agy_settings`, `--sandbox`,
`agy_sandbox`, and `skip_permissions` to be absent from the wrapper, require
the stale phrase `without settings mutation` to be absent from the wrapper,
and require `agy settings txn` to be absent from `_common.py`.
It initially fails against both current sources; Task 3 Step 3 makes this
already-existing RED guard pass.

Remove test fixtures and monkeypatches that reference `_agy_settings`, sandbox modes, `_agy_needs_skip_permissions`, or `AGY_NO_HEADLESS_AUTOAPPROVE`.
Remove every remaining `skip_permissions` argument/signature dependency,
including the non-preflight `_build_cmd(..., skip_permissions=True)` call sites
and the positional-arity assumption in
`test_build_cmd_passes_model_and_optional_effort_unchanged`; preserve that
test's selector/model/effort assertions.
In
`test_agy_pydantic_initial_prompt_uses_body_semantics_and_one_sealer`, drop the
removed positional `agy_sandbox` argument from both direct `_build_cmd` calls
while preserving its body-semantics, one-sealer, and plain-marker assertions.
Also drop that removed positional argument from the direct `_build_cmd` calls
in `test_schema_repair_retains_trusted_packet_footer` and
`test_agy_schema_retry_rebuilds_unsealed_prompt_and_reseals_once`, while
preserving their trusted-packet footer, schema-repair, one-sealer, and argv
prefix assertions.

Delete
`test_settings_guard_phase_is_preserved_in_custody_and_summary` and
`test_settings_restore_failure_suppresses_validated_provider_answer`; their
only contract is the retired settings transaction. Rewrite
`test_sealed_schema_failure_persists_one_provider_response_without_retry` and
`test_audit_and_run_log_preserve_phase_and_exact_validated_object` to preserve
their schema/custody assertions while using `post-dispatch-result`.

Update all three existing preflight tests that assert sandbox,
`skip_permissions`, or the old `_build_route_args` arity so their expected
preflight receipt has exactly the nine keys listed in the Task 3 interface,
with selector/model and optional effort carried by `route_args` and no
`sandbox`, `skip_permissions`, or invented permission/classification key.
Patch the transcript extractor mock with the current helper signature exactly
as the surrounding tests do. Update the `_common.py` classification-source
comment when adding `permission-unavailable`, removing the retired `+ agy
settings txn` source claim while retaining `CONFIG_CONFLICT_PATTERNS`. Rewrite
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

Delete `_add_skip_permissions`, `_agy_needs_skip_permissions`, version-floor
logic, `--sandbox`, settings-lock handling, `_agy_settings` imports/guards, and
every `skip_permissions`, `agy_sandbox`, and `_run_agy_with_retry(...,
sandbox=...)` parameter. In the no-answer path, add the observed native AGY
detector only; do not add Claude or Gemini message detectors. Add:

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
Do not add it to `CLASSIFICATION_TOKENS` or
`REPAIR_CLASSIFICATION_TOKENS`: like `vendor-error` and
`truncated-answer`, it is emitted directly by the AGY driver and is never a
classifier-repair target. Extend the nearby exception comment and retain the
focused non-membership assertions from Step 1. Remove the now-unused
`subprocess` import together with `_agy_needs_skip_permissions`.
Remove only the `_agy_settings.agy_settings_guard(...)` lease, the
`pre-dispatch-settings` / `dispatch-uncertain` / `post-dispatch-cleanup` phase
assignments, and the settings-release suppression clause. Call
`_run_agy_with_retry` directly and retain `post-dispatch-result` through result
custody. Preserve the surrounding driver `try/except`, the pre-submission
`EXIT_BINARY_MISSING` branch, and the custody-preserving terminal
`config-conflict` result for `_pty.PtyStartError`, `TimeoutError`,
`json.JSONDecodeError`, `ValueError`, and `OSError`. Update the
`RunResult.dispatch_phase` comment plus retired sandbox/settings module
docstrings. Delete the orphaned `AGY_SETTINGS_LOCK_TIMEOUT` environment parse
and its wrapper-owned invalid-number `EXIT_ARG_ERROR` branch together with the
settings guard, making the Step 1 wrapper-source guard pass. Task 5 separately
updates the analyzer wording.
Rewrite `--preflight-only` help to promise only exact route-argument validation
without provider inference; it must not claim an absent settings-mutation
boundary.

The retained ordinary/non-formal Gemini fallback proof no longer uses a
settings phase. It is exactly the no-final-summary
`EXIT_BINARY_MISSING` return paired with the wrapper-owned
`agy start failed before request submission: stage=exec errno=<supported>`
diagnostic from `PtyStartError(stage="exec", errno in
_PRE_SUBMISSION_EXEC_ERRNOS)`. Any invocation that emits a final wrapper
summary reached post-dispatch handling and is fallback-ineligible. Do not add a
new detector or restore `pre-dispatch-settings`. A missing or invalid
`TRIAD_AGY_BIN` and a missing `agy` on `PATH` remain direct early route-setup
errors but are intentionally fallback-ineligible in `0.2.532`; the owner must
install/configure AGY or explicitly authorize a separate Google route.

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
  the now-unused `os` import from Claude, and orphaned `APPROVAL_CHOICES`,
  `SANDBOX_CHOICES`, `_wrapper_hardened`, and `Path` names from Gemini with
  their consumers.

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

Also create the RED
`test_provider_wrapper_sources_contain_no_retired_permission_controls` in this
step. Read `Path(claude_wrapper.__file__)` and
`Path(gemini_wrapper.__file__)`; require `--permission-mode`, `--sandbox`,
`--tools`, `--strict-mcp-config`, and `--setting-sources` to be absent from the
Claude module, and `--approval-mode`, `APPROVAL_CHOICES`, and
`SANDBOX_CHOICES` to be absent from the Gemini module. The
assertions initially fail against the current parser/docstring/argv source and
Task 4 Step 3 makes this already-existing RED guard pass.

- [ ] **Step 2: Run the wrapper argv test to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_provider_packet_context.py -k "removed_permission_options or native_wrapper_default_argv"'
```

Expected: removed-option cases fail because the current parser accepts them;
the hardened Gemini default emits `--policy`.

- [ ] **Step 3: Remove wrapper permission arguments and policy injection**

Delete Claude's `--sandbox`, `--permission-mode`, `TRIAD_CLAUDE_ENFORCE_SANDBOX`, and generated tool/config/permission flags. Rewrite `bin/claude_wrapper.py`'s module docstring to describe only transport forwarding and native provider settings; remove its stale permission-mode and wrapper isolation-flag paragraphs, making the Step 1 source guard pass. Delete Gemini's `--approval-mode`, `--sandbox`, `--skip-trust`, policy constant, hardened default, and generated `--policy`/approval flags. Rewrite `bin/gemini_wrapper.py`'s module docstring so its generated-argv example contains only provider-native forwarded arguments and no `--approval-mode`, making the Step 1 Gemini source guard pass. Neither the public nor generated Gemini argv may skip a provider-owned trust decision.
Delete the now-orphaned Gemini `APPROVAL_CHOICES` and `SANDBOX_CHOICES`
constants in the same edit; the source guard must prove both names are absent.

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
- Modify: `bin/apply_patch.py:1-75`
- Modify: `bin/_common.py:211,269-270,1827,2486-2491,2637-2811,2935`
- Modify: `bin/antigravity_wrapper.py:347,746`
- Modify: `bin/claude_wrapper.py:44-46`
- Modify: `bin/gemini_wrapper.py:25-27`
- Modify: `bin/bootstrap_repair.py:16-50,97-123,1838-1857,1969-2245`
- Modify: `scripts/bootstrap.sh:381-428,650-838,1908-2150,2180-2243`
- Modify: `tests/test_bootstrap.py`
- Modify: `tests/test_bootstrap_repair_transaction.py`
- Modify: `tests/test_distribution_contract.py`
- Delete: `agents/triad-repair-analyzer.toml`

**Interfaces:**
- Repair analysis uses native `spawn_agent` with `fork_turns="none"`, explicit current router model, medium effort, omitted `agent_type`, and the existing untrusted JSON envelope.
- Repair apply uses the plugin's `bin/apply_patch.py` through literal
  login-shell `python3` with required
  `--classifier-file <install-resolved-absolute-path>`; no installed
  `triad-apply-repair` launcher is required. Bootstrap prints the exact
  owner-apply argv with the same classifier path pinned into provider
  launchers, so a fresh login shell cannot silently write another default.
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
    assert "--classifier-file" in protocol
```

In `tests/test_bootstrap.py`, add
`test_apply_patch_requires_explicit_absolute_classifier_file`: invoke
`bin/apply_patch.py` without the option, with a relative path, and with a
symlinked leaf/ancestor and require refusal before any classifier write; then
invoke it from a fresh `HOME`/`XDG_CONFIG_HOME` with an absolute custom path
and require only that exact file to change. Also add
`test_bootstrap_prints_owner_apply_argv_with_pinned_classifier`: install with a
custom `TRIAD_CLASSIFIER_EXTENSION`, parse the printed argv, and require its
`--classifier-file` value to equal the path embedded in every provider
launcher.

In the same module, add:

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
    config.write_text(
        "# >>> triad-codex-dispatch managed repair analyzer registration >>>\n"
        "# original config existed = false\n"
        "[agents.triad-repair-analyzer]\n"
        'description = "Read-only triad repair analyzer for untrusted vendor run logs."\n'
        f"config_file = {json.dumps(str(analyzer), ensure_ascii=False)}\n"
        "# <<< triad-codex-dispatch managed repair analyzer registration <<<\n",
        encoding="utf-8",
    )
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
    config_text = config.read_text(encoding="utf-8") if config.exists() else ""
    _before, _after, had_registration, _original_existed = (
        helper.split_registration(config_text, config, analyzer)
    )
    assert not had_registration
    assert not analyzer.exists()
    assert not launcher.exists()
    assert foreign.read_text(encoding="utf-8") == 'name = "foreign"\n'
```

Use the production ownership parser for the registration block and the
production marker constants. The test's five-line launcher is the legacy
managed form already accepted by `launcher_is_managed`. Parameterize the test
over that five-line legacy form and a frozen exact fixture of the current
seven-line pinned form before deleting `bootstrap_repair.launcher_text`, so
the actual `0.2.531 -> 0.2.532` upgrade is covered without retaining a
production launcher generator solely for a test. Do not add a second removal
predicate.

Rename/rewrite the existing
`test_repair_protocol_uses_the_exact_installed_agent_and_apply_contract` as
`test_repair_protocol_uses_fresh_native_child_without_custom_agent`, using the
exact assertions introduced in Step 1. Do not leave the old test or add a
parallel duplicate.

Split the protocol-only assertions out of
`test_provider_skills_use_final_process_state_for_corrected_extraction_failure`
into the new Task-5-owned
`test_repair_protocol_keeps_run_log_opaque_for_native_child`. Read only
`docs/references/repair-protocol.md`; require the leader never to open the run
log, require its absolute path to be passed only to the fresh native proposal
child, and require no registered repair analyzer. Leave the provider-skill,
final-process-state, and AGY fallback assertions in the original test for Task
7. Do not duplicate either assertion group between the two tests.

Rewrite the existing
`test_repair_handoff_uses_one_json_input_envelope_and_valid_output_examples`
to read `docs/references/repair-protocol.md` alone after the agent TOML is
deleted. Preserve its one-envelope assertion and validate both `propose` and
`escalate` examples against `_common.PATTERN_LIST_CLASS`,
`_MIN_SUBSTRING_LEN`, and `_MAX_SUBSTRING_LEN`; remove only the
`REPAIR_AGENT`, `developer_instructions`, and `agent_type` assertions. Add new
literal `/bin/zsh`, `-lic`, `python3`, and `bin/apply_patch.py` assertions to
`test_repair_protocol_uses_fresh_native_child_without_custom_agent`; they are
not present in the old test. Replace the old `--cli`, `--proposal-file`, and
`shlex.join` assertions with exact checks over the documented `owner_argv`,
then remove the retired exact-installed-agent half.

- [ ] **Step 2: Run focused tests to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k repair_protocol_uses_fresh_native_child'
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k repair_protocol_keeps_run_log_opaque_for_native_child'
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py -k removes_only_exact_legacy_repair_agent_artifacts'
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py -k "apply_patch_requires_explicit_absolute_classifier_file or bootstrap_prints_owner_apply_argv_with_pinned_classifier or provider_launchers_and_owner_apply_share_custom_classifier_in_a_fresh_environment"'
```

Expected: the protocol still names the registered agent, bootstrap still
installs it, and the explicit classifier-file and owner-argv behavior is not
implemented yet.

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
        "--classifier-file",
        classifier_path,
        "--proposal-file",
        proposal_path,
    ]),
]
```

`classifier_path` is the install-resolved absolute path from the exact
bootstrap-printed owner argv, not a value recomputed from the current shell.
Make `--classifier-file` required in `bin/apply_patch.py`; reject a relative or
symlinked leaf/ancestor before reading the proposal. Extend
`_common.apply_classifier_patch` with one optional explicit `extension_path`
parameter and have this CLI always pass the validated absolute path. Retain the
ambient fallback only for existing direct compatibility callers that omit that
internal parameter; the documented owner CLI never uses it. Update the module
usage docstring and the repair-protocol tests with this exact argument.

Preserve the existing collision-resistant task-label contract asserted by
`test_documented_native_task_names_match_the_callable_schema`: keep
`from secrets import token_hex`,
`task_name=f"repair_analyzer_{token_hex(8)}"`, and the retry-with-new-suffix
wording while removing only the retired `agent_type` and pinned read-only
agent claims.

Update `bin/apply_patch.py`'s module docstring to describe the proposal-only
native child, and update both AGY runtime comments at the retry driver and
result-custody path so neither claims a shipped read-only analyzer exists.
These are wording-only changes; retain the validated apply path and retry
behavior.

- [ ] **Step 4: Make bootstrap repair-agent support remove-only**

Remove `install`, `preflight-install`, analyzer source validation, analyzer
registration creation, `launcher_text`, and installed apply-launcher creation
from `bin/bootstrap_repair.py`. Retain the exact managed `remove` path,
`launcher_is_managed`, and generic transaction helpers required to clean old
installations.

Delete the corresponding `run_repair_lifecycle preflight-install` invocation
and its now-stale repair-target preflight comment at baseline
`scripts/bootstrap.sh:2144-2150`; the removed subcommand and its only bootstrap
caller belong to this same Task 5 change.

Change `scripts/bootstrap.sh --install` to invoke exact repair cleanup before installing wrapper launchers. A foreign registration, analyzer, or launcher is reported and preserved. Delete the shipped analyzer TOML.
After successful wrapper publication, print the exact shlex-safe owner apply
argv containing the trusted literal login shell, absolute toolkit
`bin/apply_patch.py`, placeholder `--cli`/proposal values, and the same resolved
absolute canonicalized `CLASSIFIER_PATH` pinned into the wrapper launchers. Printing is
transaction output only; do not reinstall an apply launcher or create another
state file.

- [ ] **Step 5: Prune obsolete tests and run GREEN tests**

Remove tests whose only contract is installing, refreshing, or selecting the read-only analyzer. Retain and rename exact-removal, foreign-preservation, rollback, symlink-refusal, and transaction-integrity tests.

Apply these exact `tests/test_bootstrap.py` dispositions so the retained
upgrade-cleanup path is not confused with the deleted repair-agent creation
path:

- rename
  `test_install_refuses_unsafe_repair_launcher_before_any_mutation` as
  `test_install_cleanup_refuses_unsafe_legacy_repair_launcher_before_wrapper_publication`.
  Keep its FIFO, symlink, and foreign-file cases against the exact legacy
  launcher cleanup performed by `scripts/bootstrap.sh --install`; remove its
  retired profile/shell-install options and assertions;
- rename
  `test_install_refuses_symlinked_repair_analyzer_parent_before_any_mutation`
  as
  `test_install_cleanup_refuses_symlinked_legacy_analyzer_parent_before_wrapper_publication`.
  Seed only the frozen legacy-owned analyzer target, require the symlinked
  parent and foreign target to remain untouched, and remove assertions about
  creating a new analyzer, profile, rule, or shell entry; and
- retain
  `test_remove_refuses_unsafe_repair_target_before_any_mutation` and
  `test_remove_refuses_symlinked_repair_analyzer_parent_before_any_mutation`
  as remove-path guards, but seed their exact legacy-owned artifacts from the
  frozen fixtures instead of calling the deleted install/registration path.

Remove the current `_repair_install_args` helper completely; no test may keep
the deleted production `install` parser or function as a state factory. Add
one test-only `_seed_frozen_legacy_repair_state` fixture that writes the exact
0.2.531 managed analyzer, registration, and launcher bytes already frozen in
Step 1, without calling production creation code.

Delete these creation-only `tests/test_bootstrap.py` tests with the production
creation surface they exercise:

- `test_bootstrap_repair_revalidates_target_before_replacement`;
- `test_bootstrap_repair_preserves_foreign_swap_between_check_and_publish`;
- `test_bootstrap_repair_never_clobbers_foreign_create_during_publication`;
- `test_bootstrap_repair_non_bmp_config_path_is_valid_toml`;
- `test_bootstrap_repair_apply_launcher_pins_classifier_path`;
- `test_bootstrap_repair_preflight_install_is_read_only`;
- `test_bootstrap_repair_rolls_back_replace_when_parent_fsync_fails`;
- `test_bootstrap_repair_rollback_preserves_foreign_replace_after_publication`;
- `test_bootstrap_repair_rejects_apply_or_runtime_identity_swap`;
- `test_bootstrap_repair_cleans_staged_files_when_later_stage_fails`;
- `test_bootstrap_repair_outer_cleanup_retries_one_shot_unlink_failure`;
- `test_bootstrap_repair_outer_cleanup_reports_persistent_unlink_failure`;
- `test_bootstrap_repair_cleans_temps_after_publish_or_readback_failure`;
- `test_bootstrap_repair_rolls_back_post_replace_readback_failure`; and
- `test_bootstrap_repair_rollback_continues_after_refusal`.

Rename/rewrite
`test_installed_launchers_keep_custom_classifier_in_a_fresh_environment` as
`test_provider_launchers_and_owner_apply_share_custom_classifier_in_a_fresh_environment`.
Keep the provider-launcher execution and custom classifier assertion. Remove
the retired `triad-apply-repair` execution; instead parse the exact
bootstrap-printed owner argv, substitute a valid CLI and proposal file, run it
under the same fresh `HOME`/`XDG_CONFIG_HOME`, and require the explicit
`--classifier-file` target to be the same custom path printed and pinned into
the provider launcher. Require no classifier file below the fresh ambient
config directory.

Retain the following removal-ownership and removal-transaction tests, but
rewrite each to use the frozen test-only seed or the retained ownership helper
directly, never `_repair_install_args`, `helper.install`, the `install`
subcommand, or `launcher_text`:

- `test_bootstrap_repair_refuses_exact_analyzer_marker_inside_multiline_string`;
- `test_bootstrap_repair_refuses_exact_launcher_marker_inside_python_multiline_string`;
- `test_bootstrap_repair_preserves_exact_registration_block_inside_multiline_string`;
- `test_bootstrap_repair_refuses_noncanonical_marker_wrapped_registration`;
- `test_bootstrap_repair_rolls_back_unlink_when_parent_fsync_fails`;
- `test_bootstrap_repair_rollback_preserves_foreign_create_after_unlink`;
- `test_bootstrap_repair_restores_registration_when_analyzer_removal_fails`;
- `test_bootstrap_repair_remove_refuses_unsafe_artifact_before_config_mutation`;
- `test_bootstrap_repair_refuses_malformed_toml_inside_managed_markers`;
- `test_bootstrap_repair_embedded_launcher_and_config_markers_are_foreign`;
- `test_bootstrap_repair_config_round_trips_existing_bytes_exactly`;
- `test_bootstrap_repair_refuses_reversed_reserved_marker_comments`; and
- `test_bootstrap_repair_refuses_orphan_or_duplicate_reserved_marker_comments`.

Rewrite `test_bootstrap_repair_reports_explicit_refusal_and_success_statuses`
as `test_bootstrap_repair_reports_remove_only_success_status`: require the
exact successful remove status and no creation-path invocation. Rename/rewrite
`test_bootstrap_repair_help_exposes_explicit_install_and_remove` as
`test_bootstrap_repair_help_exposes_remove_only_repair_lifecycle`. Inspect the
parser's subparser choice set, not a whole-help substring: require `install`
and `preflight-install` to be absent while `remove`, `preflight-remove`,
`commands-install`, and `commands-remove` remain present. The literal token
`install` may still occur inside the retained `commands-install` choice; do not
treat that as the deleted standalone subcommand. Retain
`test_bootstrap_repair_restores_pair_when_launcher_removal_fails`, but seed its
initial pair from the frozen fixture. In
`tests/test_bootstrap_repair_transaction.py`, delete
`test_repair_install_rolls_back_when_staged_cleanup_fails_after_publication`
and replace its `_repair_args` install-state builder with the same frozen
test-only seed for
`test_repair_remove_rolls_back_when_staged_cleanup_fails_after_publication`.
All unrelated generic command-group and transaction-helper tests in that
module remain unchanged.

Apply these additional exact `tests/test_bootstrap.py` dispositions rather
than leaving current repair-agent tests to inference:

- delete `test_reinstall_refreshes_the_managed_repair_analyzer`,
  `test_apply_repair_launcher_forwards_argv_unchanged`, and
  `test_install_registers_repair_analyzer_without_replacing_agents_settings`;
  each exists only for the retired creation path; and
- rename/rewrite `test_install_refuses_nonmanaged_repair_analyzer_target` and
  `test_install_refuses_nonregular_repair_analyzer_target` as install-time
  legacy-cleanup guards. Preserve and report a safe foreign analyzer, refuse a
  non-regular target without following or mutating it, and require no partial
  wrapper publication.

Rename and rewrite the named current test
`test_runtime_comments_describe_the_current_read_only_analyzer_flow` as
`test_runtime_comments_describe_native_proposal_only_repair_flow`. Scan the
current runtime and require `read-only analyzer` and `ZERO write authority` to
be absent. Require the replacement comments to retain the native fresh-child,
proposal-only, owner-controlled local apply, no-provider-invocation, and
age-floor semantics. Rewrite the matching current comments in
`bin/_common.py` plus the Claude and Gemini `--repair-mode` docstrings;
historical frozen test fixtures may retain their literal old text. Update
`_make_repo_root` and related bootstrap fixtures
so deleting the shipped analyzer and the migration requirements template does
not leave a fixture-generated stale file.
For the two current `tests/test_bootstrap.py` users of
`bootstrap_repair.launcher_text`, retarget
`test_bootstrap_repair_rejects_whitespace_python_shebang` directly to
`portable_python_shebang(Path("/tmp/python runtime/bin/python3"))` and preserve
its exact refusal assertion. Rewrite only
`test_bootstrap_repair_keeps_foreign_registration_but_removes_managed_launcher`
to construct its legacy launcher from the frozen managed-launcher fixture
above. Preserve
`test_documented_native_task_names_match_the_callable_schema` as specified in
Step 3.

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py workspace/triad-codex-dispatch-reliability/tests/test_bootstrap_repair_transaction.py workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k "repair or analyzer or bootstrap_repair or documented_native_task_names or apply_patch_requires_explicit_absolute_classifier_file or bootstrap_prints_owner_apply_argv_with_pinned_classifier or provider_launchers_and_owner_apply_share_custom_classifier_in_a_fresh_environment"'
```

Expected: selected tests pass and no shipped/installed read-only repair agent remains.

- [ ] **Step 6: Commit repair-agent retirement**

```bash
git add docs/references/repair-protocol.md bin/apply_patch.py bin/_common.py bin/antigravity_wrapper.py bin/claude_wrapper.py bin/gemini_wrapper.py bin/bootstrap_repair.py scripts/bootstrap.sh tests/test_bootstrap.py tests/test_bootstrap_repair_transaction.py tests/test_distribution_contract.py
git add -u agents/triad-repair-analyzer.toml
git commit -m "refactor: use native repair children"
```

### Task 6: Remove Plugin-Owned Permission Profiles, Rules, and Migration Templates

**Files:**
- Modify: `bin/_common.py:398-406,428-430`
- Modify: `scripts/bootstrap.sh:16-222,540-650,987-997,1086-1935,2138-2243`
- Inspect unchanged: `scripts/bootstrap.sh:2005-2026` legacy remove-only
  `/etc/codex/requirements.toml` warning
- Modify: `bin/bootstrap_repair.py:23-43,652-772,1411-1704,1760-1835,2163-2320`
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
- `TRIAD_CODEX_PROFILE_APPROVAL_POLICY`, its parsed state, validation, and
  warning are retired with profile/rule creation; they cannot reject install or
  remove after their consumers disappear.
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

Add `test_native_install_emits_no_permission_environment_controls` as the
runtime postcondition and assert that no bootstrap-produced wrapper launcher,
file below the temporary `CODEX_HOME`, or managed shell-rc output contains
`TRIAD_CLAUDE_ENFORCE_SANDBOX` or `TRIAD_WRAPPER_HARDENED`. This assertion does
not scan repository source: `bin/_common.py` intentionally retains explicit
environment-variable activation for compatibility callers. Also add
the independently RED
`test_permission_environment_control_producers_are_removed`: read
`bin/bootstrap_repair.py` and require both environment names plus
`def _shell_entry_block(` to be absent. This static guard binds the RED/GREEN
cycle to the current producer even though the legacy shell-entry install is
opt-in and a default install does not exercise it.
Also add `test_bootstrap_source_contains_no_retired_permission_controller_names`:
read `scripts/bootstrap.sh` and require `install_codex_rules` to be absent.
This initially fails against both the function and the launcher-policy comment,
so the production comment cannot outlive its retired controller.

- [ ] **Step 2: Run focused tests to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py -k "native_install_does_not_create_codex_permission_state or permission_environment_control_producers_are_removed or bootstrap_source_contains_no_retired_permission_controller_names"'
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_migration_contract.py'
```

Expected: default installation creates rules, the repair helper still contains
the legacy permission-environment producer, and the migration tests require
the templates.

- [ ] **Step 3: Remove permission-generation paths**

Delete profile/rules selection, preflight, generation, config-fragment merge,
requirements guidance, shell-entry installation, and Agent Review/sandbox
messaging from `scripts/bootstrap.sh`. In `bootstrap_repair.py`, delete
`preflight_managed_artifact`, `install_managed_artifact`, the
`managed-artifact` CLI subcommand, `merge_config_fragment`,
`_publish_config_backup`, the `config-fragment --action merge` choice,
`preflight_shell_entry`, `_shell_entry_block`, and the install branch of
`update_shell_entry`. Retain `remove_managed_artifact`,
`remove_config_fragment`, their exact marker/text ownership helpers, and only
the remove action of the config-fragment/shell-entry CLI surfaces needed for
upgrade cleanup. Keep exact ownership inspectors/removers in
`bootstrap_repair.py` only as needed for upgrade cleanup. Preserve the
existing all-or-nothing command-group staged publication for wrapper
launchers; repair-agent retirement cannot weaken that transaction boundary.
Rewrite the launcher construction comment at baseline
`scripts/bootstrap.sh:987-997` to describe only the retained constructed-env
trust boundary and remove its `install_codex_rules` policy-matching claim. Do
not replace that function name with another permission-controller claim.

Delete `CODEX_PROFILE_APPROVAL_POLICY`,
`CODEX_PROFILE_APPROVAL_POLICY_EXPLICIT`,
`validate_codex_profile_approval_policy`, its call from
`validate_bootstrap_inputs`, and the retired Agent Review warning. Delete both
`test_check_rejects_invalid_runtime_profile_approval_policy` and
`test_remove_rejects_invalid_runtime_profile_approval_policy_before_any_mutation`;
no install or remove path may reject an orphaned permission-policy input.

Delete `warn_legacy_opt_out_artifacts` and its preserve-only messaging from
`scripts/bootstrap.sh`; it calls the deleted `managed-artifact --action
inspect` surface and conflicts with install-time exact cleanup. Replace its
call sites with the retained exact remove routes only: rules and profile use
`remove_owned_artifact`/`managed-remove`, the config fragment uses the retained
`config-fragment --action remove`, and the shell entry uses the retained
`shell-entry --action remove`. Do not introduce a replacement inspection or
policy surface. Both `--install` and `--remove` execute this same exact cleanup:
exact managed legacy bytes are removed, safe unmanaged or edited artifacts are
preserved and reported, and unsafe symlink/FIFO/non-regular targets are refused
without following or mutating them.

Delete or rewrite only the
`tests/test_bootstrap_repair_transaction.py` cases whose contract is
managed-artifact preflight/install/CLI access or config-fragment merge,
including the current merge group around lines 1220-1295 and the CLI/rollback
merge cases around lines 1399-1430 and 1550. Retain direct exact-ownership,
foreign-preservation, config-fragment removal, rollback, and transaction
tests. Rewrite current `tests/test_bootstrap.py` merge assertions to exercise
remove-only upgrade cleanup; no test may retain a production creation helper
solely to synthesize legacy state.

Delete `inspect_managed_artifact` together with the deleted
`managed-artifact` CLI, and delete the five
`tests/test_bootstrap_repair_transaction.py` tests from
`test_managed_artifact_inspect_returns_safe_tri_state` through
`test_managed_artifact_inspect_refuses_injected_read_failure`. Their only
entry point is the retired inspect action; retained `managed-remove` ownership,
foreign-preservation, unsafe-path, rollback, and transaction tests cover the
upgrade-cleanup contract. The named dispositions in Tasks 5 and 6 resolve
ambiguous current tests; every remaining test follows the general retain/delete
rule stated by its task and does not keep a retired creation/inspection surface.
Task 8 Step 6's complete-suite run is the authoritative catch for any unnamed
retired-surface test.

Apply these additional exact `tests/test_bootstrap.py` dispositions for the
current profile, rule, and shell-entry cases:

- delete `test_profile_and_rules_can_be_explicitly_disabled`,
  `test_profile_and_rules_skip_flags_disable_both`,
  `test_check_can_install_optional_codex_runtime_profile`,
  `test_opt_in_runtime_profile_preserves_base_approval_settings`,
  `test_check_can_install_runtime_profile_with_explicit_approval_policy`,
  `test_explicit_never_profile_keeps_global_rules_on_agent_review_prompt`,
  `test_never_policy_without_profile_cannot_bypass_agent_review`,
  `test_empty_runtime_profile_approval_policy_uses_auto_review_default`,
  `test_check_rejects_invalid_runtime_profile_approval_policy`,
  `test_shell_entry_opt_in_requires_legacy_profile_before_any_mutation`,
  `test_shell_entry_installs_pinned_codex_triad_function`, and
  `test_shell_entry_missing_final_newline_refuses_before_any_install_mutation`;
  each requires a retired creation or opt-in interface; and
- retain and rewrite
  `test_install_rejects_unsafe_selected_profile_or_rules_target_before_commands`,
  `test_check_refuses_to_overwrite_unmanaged_codex_runtime_profile`,
  `test_shell_entry_refuses_unmanaged_codex_triad_function`,
  `test_shell_entry_transaction_preserves_foreign_replacement_after_capture`,
  `test_install_legacy_quarantine_preserves_foreign_replacement_after_capture`,
  `test_bootstrap_rejects_malformed_shell_markers_without_changing_bytes`, and
  `test_remove_uninstalls_managed_artifacts_and_shell_entry` as exact
  cleanup/refusal/foreign-preservation/transaction tests. Remove retired
  selector and creation assertions, seed frozen managed bytes directly, and
  preserve the existing no-follow/no-partial-mutation guarantees.

Remove all `scripts/bootstrap.sh` calls to the deleted
`preflight_shell_entry` and delete that Bash wrapper function itself
(`scripts/bootstrap.sh:1815-1832`). The retained
`update_shell_entry --action remove` operation performs the exact
marker/content ownership check and removal as one guarded upgrade-cleanup
action; a foreign or edited block is preserved and reported. Do not replace
the retired preflight with a new policy layer.

Rewrite the `bin/_common.py` hardening comment so it no longer claims that the
retired shell entry activates `TRIAD_WRAPPER_HARDENED`. Describe only the
remaining explicit environment-variable activation used by compatibility
callers; do not add a new installer path. This includes both the helper comment
near `_wrapper_hardened` and the `runtime_allowed_roots` docstring's explicit
`opted-in legacy codex-triad shell entry` claim.

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
Preserve the still-valid native repair envelope, `age-floor cleanup`, and
`printed absolute bootstrap command` wording needed by the retained migration
guidance test; remove only its retired read-only repair-agent and installed
apply-launcher claims.

- [ ] **Step 5: Prune obsolete policy-install tests and run GREEN tests**

Remove tests for optional profile/rules/config/shell installation. Retain tests for exact cleanup, foreign preservation, symlink refusal, rollback, launcher installation, reinstall idempotence, Python boundary, provider binaries not being invoked during install, and all-or-nothing command-group staged publication. Update `_make_repo_root` and related bootstrap fixtures for the deleted repair analyzer and `migration/requirements.recommended.toml` rather than masking their absence.

Apply these exact `tests/test_bootstrap.py` dispositions in this task:

- rename/rewrite
  `test_default_install_keeps_ordinary_codex_and_installs_prompt_rules` as
  `test_default_install_keeps_ordinary_codex_and_installs_wrapper_launchers`.
  Preserve classifier initialization, log-directory setup, trusted-Python
  diagnostics, and transactional wrapper-launcher publication; replace its
  analyzer, analyzer-registration, prompt-rule, granular-permission, and
  `triad-apply-repair` assertions with exact absence assertions for those
  retired artifacts and messages;
- delete
  `test_default_install_routes_exact_wrapper_calls_to_active_reviewer`
  because its only production input is the deleted plugin-owned rules file;
- rename/rewrite
  `test_default_install_preserves_owner_approval_keys_and_adds_env_guard` as
  `test_default_install_preserves_owner_codex_config_bytes`. Seed the existing
  approval keys, require the complete `config.toml` bytes to remain unchanged,
  and require no plugin-owned shell-environment guard, profile, rule, or
  repair-agent state to be created;

- delete `test_migration_rules_claude_examples_use_effort_not_reasoning`
  because its only production input is the deleted
  `migration/triad-codex-dispatch.rules` template;
- delete `test_bootstrap_requirements_warning_uses_python_argv_safe_guidance`
  because it invokes the retired profile-install option and requires the
  deleted requirements-template path and command printer; the absence
  contract is covered by the new migration/bootstrap assertions below;
- rename/rewrite
  `test_bootstrap_usage_documents_paired_legacy_shell_entry_flags` as
  `test_bootstrap_usage_omits_retired_permission_install_flags`. Require the
  paired legacy environment names and normal-start activation clause to be
  absent while preserving wrapper-launcher and native-terminal guidance;
- rewrite `test_bootstrap_help_describes_google_route_fallback` to preserve the
  AGY/Gemini fallback and ordinary-Codex/no-dedicated-profile guidance, remove
  its `approvals_reviewer=auto_review`, `granular.rules=true`, and
  `granular.sandbox_approval=true` expectations, and require retired
  plugin-owned permission messaging to be absent; and
- delete `test_install_warns_when_base_config_has_legacy_sandbox_mode`
  because the warning is plugin-owned sandbox-selection messaging removed by
  this task and the owner configuration remains unchanged.

Apply these additional exact dispositions to the current legacy opt-out tests:

- rename/rewrite
  `test_plain_install_warns_for_managed_legacy_profile_without_deleting_it` as
  `test_plain_install_removes_exact_managed_legacy_profile`; seed the frozen
  exact 0.2.531 managed profile bytes and require removal on `--install`;
- rename/rewrite
  `test_plain_install_warns_for_managed_legacy_shell_entry_without_deleting_it`
  as `test_plain_install_removes_exact_managed_legacy_shell_entry`; seed a
  frozen exact 0.2.531 shell-entry fixture rather than calling the retired
  `_shell_entry_block` producer, and require removal on `--install`;
- rename/rewrite
  `test_plain_install_ignores_safe_unmanaged_legacy_opt_out_artifacts` as
  `test_plain_install_preserves_and_reports_safe_unmanaged_legacy_artifacts`;
- rename/rewrite
  `test_plain_install_has_no_managed_legacy_warning_when_opt_out_artifacts_absent`
  as `test_plain_install_cleanup_is_quiet_when_legacy_artifacts_are_absent`,
  without retaining the retired warning text;
- rename/rewrite
  `test_plain_install_warns_and_continues_for_unsafe_opt_out_profile` and
  `test_plain_install_warns_and_continues_for_unsafe_opt_out_shell` as exact
  fail-closed cleanup tests that require refusal, no target following, and no
  mutation of unsafe symlink/FIFO/non-regular targets; and
- delete `test_legacy_profile_opt_in_suppresses_retained_artifact_warning` and
  `test_paired_legacy_opt_in_suppresses_warning_and_updates_managed_shell_entry`
  because the opt-in variables, preserve-only warning path, and shell-entry
  install/update path are all removed.

Apply this exact `tests/test_distribution_contract.py` disposition in this
task:

- rewrite
  `test_recommended_agent_template_uses_current_read_only_repair_contract` as
  `test_recommended_agent_template_uses_native_permissions_and_repair_contract`.
  Keep its native repair-envelope, `age-floor cleanup`, printed absolute
  bootstrap-command, and stale-path absence assertions; replace only the
  retired analyzer, read-only sandbox, and installed apply-launcher assertions
  with provider-native permission inheritance and proposal-only local apply.

Apply these exact dispositions in `tests/test_migration_contract.py`:

- delete
  `test_shipped_environment_policy_uses_all_with_exact_case_insensitive_excludes`,
  `test_migration_rules_follow_the_current_bootstrap_generated_shape`, and
  `test_requirements_template_is_explicit_legacy_profile_material` because
  their only production inputs are deleted;
- rename/rewrite
  `test_current_migration_guidance_never_describes_wrapper_rules_as_allow` as
  `test_current_migration_guidance_is_permission_neutral`, reading only the
  retained `migration/AGENTS.recommended.md` and requiring the authenticated
  login-terminal inheritance wording plus absence of plugin-selected profiles,
  rules, and permission modes;
- replace
  `test_requirements_admin_copy_is_absolute_argv_safe_and_cwd_independent`
  with `test_bootstrap_install_has_no_admin_permission_copy_path`, preserving
  the still-valid global `sudo cp` and `cp -n` absence assertions while
  requiring no `/etc/codex/requirements.toml`, requirements-template path, or
  admin command printer in the install/creation portion of
  `scripts/bootstrap.sh`; delete its execution fixture and imports. Preserve
  the unchanged `run_remove` read-only warning for a root-owned legacy file,
  and assert that the remaining exact path occurs only in that remove-time
  warning and is never written or removed by bootstrap;
  and
- keep `test_release_headers_are_in_descending_order`, with its new 0.2.532
  ordering assertion assigned explicitly to Task 8 Step 3.

Delete
`tests/test_bootstrap_repair_transaction.py::test_shell_entry_transaction_preserves_existing_mode_and_owner_bytes`:
its first assertion invokes the retired `shell-entry --action install` branch.
Keep the existing removal-only shell-entry ownership, foreign-preservation,
mode, rollback, and symlink-refusal tests; do not retain an install path solely
for this transaction test.

Rewrite
`tests/test_bootstrap.py::test_bootstrap_routes_classifier_artifacts_and_config_mutations_through_helper`
to remove only its retired `managed-artifact` routing assertion. Preserve its
`classifier` and retained remove-only `config-fragment` helper-routing
assertions plus all five no-direct-profile/rules/config-write assertions. Do
not delete this no-direct-write invariant with the optional installation
tests.

In `tests/test_distribution_contract.py`, delete
`test_task2_config_backup_guidance_qualifies_registration_only_fresh_config`,
rewrite
`test_task2_hardened_comments_name_opted_in_legacy_shell_entry` to assert the
post-retirement environment-only compatibility wording and require the exact
stale `opted-in legacy codex-triad shell entry` phrase to be absent,
rewrite
`test_company_fleet_guides_and_terms_are_removed_but_personal_templates_remain`
as `test_distribution_has_only_retained_non_permission_migration_guidance`.
At this Task 6 boundary it inspects only Task-owned `migration/`,
`scripts/bootstrap.sh`, and the already-corrected repair protocol: require only
`migration/AGENTS.recommended.md`, absence of the three deleted templates and
company/fleet material, and native permission neutrality. Do not inspect
README, SECURITY, or status bytes that Task 8 owns, or provider-skill bytes
that Task 7 owns. Rewrite
the former combined test by splitting, not dropping, its remaining guards:
Task 7 owns the provider-skill/company-fleet and Gemini-route assertions, and
Task 8 owns the README/README.ko/SECURITY company-fleet assertions. Rewrite
`test_bootstrap_usage_describes_ordinary_codex_agent_review_requirements` to
assert native permission neutrality and exact legacy cleanup without requiring
profile/rule/repair-agent installation messaging.

Do not rewrite
`test_readmes_use_ordinary_codex_without_profile_or_alias` or
`test_r14_corrected_round_ledger_and_upgrade_containment_contract_is_present`
in Task 6. They read Task 8-owned README/SECURITY/status bytes. Task 8 Step 3
owns both exact dispositions after those documents change; the unchanged
formal-routing verification ledger remains historical input only.

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py workspace/triad-codex-dispatch-reliability/tests/test_bootstrap_repair_transaction.py workspace/triad-codex-dispatch-reliability/tests/test_migration_contract.py'
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k "distribution_has_only_retained_non_permission_migration_guidance or bootstrap_usage_describes_ordinary_codex_agent_review_requirements or task2_hardened_comments_name_opted_in_legacy_shell_entry or recommended_agent_template_uses_native_permissions_and_repair_contract"'
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
- Inspect unchanged: `skills/*/agents/openai.yaml`
- Modify: `tests/test_distribution_contract.py`

**Interfaces:**
- The shared prompt retains `content_digest` as the simple immutable
  review-directory custody digest. The batched profile additionally supplies
  `source_tree_digest`, `change_evidence_digest`,
  `batch_receipt_contract_path`, `batch_id`, `batch_manifest`, and the required
  `path_evidence` shape; `content_digest` is never the sole batched evidence
  binding.
- `path_evidence` includes a validated `observation_line` and bounded exact
  `source_observation` absent from visible manifests plus the exact full-file
  line range.
- Each family must cover the exact batch set.
- Each receipt's `path_evidence` and `affected_surfaces_inspected` must each
  equal its own batch's exact ordered source-path assignment; no global union
  can repair concentrated, swapped, reordered, or duplicate batch evidence.
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
  profile. Revise the already-present separately named
  `batched-full-coverage` profile so it is selected only when the exact batch
  metadata is present and requires the new strict `BatchReceipt`. The
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
        "batch_receipt_contract_path",
        "batch_id",
        "path_evidence",
        "source_observation",
        "observation_line",
        "1-160 character exact substring",
        "at least eight characters",
        "contains at least one non-whitespace character",
        "outside validated new-side hunk ranges",
        "outside-hunk lines are whitespace-only",
        "patch hunks cover every current line that can supply a valid non-whitespace observation",
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
        "exact registered analyzer",
        "read-only analyzer",
    ):
        assert forbidden not in combined
    assert "sandbox escalation to reach Agent Review" not in combined
    assert "read-only policy denies write" not in combined
    for path in (*PROVIDER_SKILLS, REVIEW_ROUTING_REFERENCE):
        assert "same authenticated login terminal" in _text(path)
```

- [ ] **Step 2: Run distribution tests to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k "full_family_batch_matrix or inherit_native_permissions"'
```

Expected: the new source-observation, complete-range, and coverage-admission
literals are missing, and provider examples still contain `--sandbox`.
`batch_receipt_contract_path` and the existing `batched-full-coverage` profile
name are already present. The existing `batched-full-coverage` profile name
alone is not a RED result; the RED test must fail only on the newly required
exact receipt and coverage semantics.

- [ ] **Step 3: Rewrite the cross-family and provider contracts**

Keep `SKILL.md` as the concise workflow entry point. Move format detail into the existing references. Require:

- leader preparation through the exact absolute
  `toolkit_root / "bin" / "review_evidence.py"` path;
- receipt-contract generation through exact absolute
  `toolkit_root / "bin" / "review_coverage.py" schema`, followed by preparation
  of the resulting exact bytes as
  `change-evidence/BATCH_RECEIPT.schema.json` and prompt delivery through
  `batch_receipt_contract_path`;
- validation before dispatch;
- all families over all batches;
- complete current source for changed and affected unchanged files;
- source-grounded `path_evidence`;
- exact `1..line_count` source coverage and a validated bounded exact source
  observation for every non-empty non-deleted path. The batched prompt must
  state the same admissibility rules enforced by Task 2: the observation is a
  `1-160 character exact substring` of its named line; when that line has at
  least eight characters the observation has at least eight; and it contains
  at least one non-whitespace character whenever the source does. For a changed
  non-whitespace source with a non-whitespace line outside validated new-side
  hunk ranges, `observation_line` must name such an outside-hunk line. State the
  validator-proven zero-byte and whitespace-only exceptions explicitly. Also
  state the sole patch-derived exception: when no outside-hunk line contains a
  non-whitespace character, including when outside-hunk lines are
  whitespace-only or the canonical patch hunks cover every current line that
  can supply a valid non-whitespace observation, a hunk-line observation is
  admissible. Task 7's RED literals and the rewritten
  `review-prompt-contract.md` batched block must use the exact phrases asserted
  above so prompt generation and receipt validation remain one TDD contract;
- invalidation on newly discovered paths;
- coverage admission through the exact absolute
  `toolkit_root / "bin" / "review_coverage.py"` path;
- native permission inheritance. Require each provider skill and the
  reviewer-routing scope section to state the exact phrase `same authenticated
  login terminal` and explain that TRIAD inherits provider permissions from
  that launch context; this is the exact Task 7 RED/GREEN literal, not public
  README-only wording;
- `permission-unavailable` as an invalid required leg; and
- fresh complete reruns after closure changes.

Require exactly one strict `BatchReceipt` JSON document per provider/batch.
Persist and hash the exact original UTF-8 response bytes. Accept raw JSON or
exactly one outer Markdown fence with optional `json` info, then strictly
validate only the inner JSON bytes. Use the exact outer-fence grammar and
ASCII-whitespace handling from Task 2. Accept triple backticks inside JSON
string values; reject prose wrappers, nested or multiple top-level fence
envelopes, missing fields, and family/batch mismatches. Fresh Codex
terminal text is persisted under the same custody rule. Require
`changed_hunks` to exactly equal each path's canonical `PATCH_INDEX.tsv` IDs.
For a resolved affected-unchanged path, `verified_impact_edges` exactly equals
its expected closure IDs; an unresolved path may omit only expected IDs, but
the unresolved disposition and path still block admission. `SAFE` is
impossible for Critical/Major findings,
any `NOT-SAFE` receipt, unresolved paths, or open questions.
Require the exact `<family>/<batch-id>.json` receipt tree and admit a formal
round only through the deterministic absolute-toolkit-path
`review_coverage.py admit` output. Resolve `toolkit_root` from the selected
local checkout or installed skill package once; do not rely on the caller's
cwd and do not add a helper or environment policy.

The common batched prompt treats false-pass risk as a hypothesis, accepts zero
findings only with complete receipt evidence, and requires inspection of every
assigned path, complete current source, changed hunk, and impact edge. It asks
each family to check source-to-diff consistency; caller, consumer, schema,
configuration, build, and documentation impact; in-scope failure and cleanup
behavior; review-kind-specific migration and compatibility semantics;
removed-surface cleanup; and false-pass paths in admission. This permission
migration review names permission-neutral migration in its objective. Every
material finding uses an exact prepared-directory-relative
`path:positive-line` and concrete trigger. A missing fact
enters `open_questions` only when it prevents disposition, and every formal
entry blocks admission. A `SAFE` receipt is admissible only when digest-bound
evidence covers every assigned path, hunk, and impact edge; the receipt does
not claim provider-enforced proof of private read activity.

For any family, one malformed or truncated result permits exactly one compact
fresh re-dispatch of that complete family across every batch with the same
evidence, route, objective, boundaries, and profile. Retain original response
bytes for custody without mixing old and replacement receipts for admission.
A second malformed or truncated result leaves the family and round invalid.
Provider substitution and two-family formal admission remain unavailable.

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
in the same round. Keep Gemini fallback eligible only for the exact
no-final-summary `EXIT_BINARY_MISSING` plus wrapper-owned pre-submission
`PtyStartError` diagnostic defined in Task 3. Any final summary is
post-dispatch and fallback-ineligible. For a formal round, require separate
owner authorization for the exact Gemini route, provider, data boundary, and
objective, then retain the same immutable prepared directory,
prompt-controlled no-edit contract, digest/mutation invalidation, and strict
result admission. Remove the retired exact-route read-only-denial proof as an
owner-visible native-permission relaxation; do not replace it with a new
enforcement probe. Remove stale
`phase=pre-dispatch-settings`, `dispatch-uncertain`, and
`post-dispatch-cleanup` eligibility language without adding a detector or
restoring a TRIAD-installed read-only policy, bypass, or provider substitution.
State explicitly that missing/invalid `TRIAD_AGY_BIN` and missing `agy` on
`PATH` are surfaced as fallback-ineligible route-setup errors in `0.2.532`,
not silently translated into Gemini dispatch.
In all three provider skills, replace the stale `exact registered analyzer`
and `read-only analyzer` wording with the Task 5 fresh native
proposal-only-child contract. Preserve the repair-protocol link, local
owner-controlled apply boundary, and no-provider-invocation statement; do not
introduce a new registered agent or permission controller.

- [ ] **Step 4: Validate metadata and run skill/prompt lint**

Verify that the four current provider-neutral `agents/openai.yaml` prompts
still delegate result-profile details to their skills and leave their bytes
unchanged. Run the skill validator and prompt linter from the login-shell
Python environment:

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

At this boundary rewrite only tests whose production assertions are wholly
owned by Task 7 skill/reference files:

- rewrite
  `test_fresh_codex_template_renders_formal_kind_and_approved_data_boundary`
  to retain the simple `content_digest` assignment for the shared envelope,
  require additional `source_tree_digest`, `change_evidence_digest`,
  `batch_receipt_contract_path`, `batch_id`, and `batch_manifest` assignments,
  and reject treating `content_digest` as the sole batched binding;
- rewrite `test_r17_fresh_template_is_renderable_and_scope_mapped` so its exact
  `shared_prompt_values` equality retains all existing keys, including
  `content_digest`, and adds the five exact batched metadata keys above;
- rewrite `test_fresh_codex_example_has_complete_no_edit_worktree_contract` to
  retain the simple `content_digest` custody assignment and require the five
  batched metadata assignments without weakening the no-edit/native-child
  contract;
- rewrite `test_r17_template_scope_execution_is_conditional_and_deletion_safe`
  and `test_r17_fresh_helpers_execute_against_hermetic_filesystem` to retain
  `content_digest`, execute the expanded metadata dictionary, and require all
  five batched values while preserving their conditional/deletion-safe and
  hermetic-execution assertions;
- rename/rewrite
  `test_fresh_codex_formal_template_uses_only_the_formal_profile` as
  `test_fresh_codex_template_preserves_unbatched_and_selects_batched_profile`:
  preserve the byte-identical four-element `formal-gate` compatibility
  profile while requiring the operational template to select
  `batched-full-coverage` only with complete batch metadata;
- rename/rewrite
  `test_task_1a_uses_one_prepared_review_directory_and_simple_digest` as
  `test_formal_review_uses_one_prepared_directory_and_bound_evidence_digests`:
  preserve its shared-directory, exact test-boundary, and no-inline-source
  assertions and preserve the simple `content_digest` custody assertions
  byte-wise; replace only any claim that the simple digest is sufficient for
  batched admission with the two evidence digests, candidate-state binding,
  and post-leg revalidation;
- rename/rewrite
  `test_task_1a_fresh_codex_uses_native_semantics_without_fence_or_json_gate`
  as `test_fresh_codex_profiles_separate_semantic_compatibility_from_batched_receipts`:
  preserve native spawn semantics and the unbatched no-JSON compatibility
  statement while requiring the separately selected batched route's strict
  receipt and exact outer-fence custody rule;
- preserve `test_every_review_leg_uses_the_shared_prompt_contract` and
  `test_formal_review_physically_excludes_only_exact_test_roots_and_uses_prepared_paths`
  unchanged. The exact physical test-source boundary remains an approved
  contract and is not removed by batched evidence;

- rewrite `test_task_2a_provider_guides_delegate_shared_formal_preparation` and
  `test_task_2b_gemini_guide_keeps_fallback_contract_without_shared_protocol`
  to retain route/cwd/shared-directory assertions while requiring absence of
  provider permission flags; for the latter test, also remove its exact
  `phase=pre-dispatch-settings` assertion with the retired phase taxonomy;
- rewrite `test_google_fallback_requires_pre_dispatch_agy_unavailability` to
  require the exact no-summary exit-4/diagnostic proof, reject every
  final-summary result, explicitly reject missing/invalid `TRIAD_AGY_BIN` and
  missing-`agy`-on-`PATH` diagnostics as fallback triggers, and remove the
  retired phase taxonomy from provider skills and reviewer routing;
- rewrite
  `test_provider_skills_use_final_process_state_for_corrected_extraction_failure`
  to preserve its final status, final run-log, and opaque-data assertions;
  remove the protocol-only assertions moved to Task 5; replace the old
  missing/invalid `TRIAD_AGY_BIN` and missing-`agy`-on-`PATH` fallback-trigger
  assertions with direct fallback-ineligible route-setup behavior and exact
  retained `PtyStartError` eligibility proof;
- preserve and rerun
  `test_formal_review_uses_owner_routing_baseline_and_bounded_escalation`
  because Task 7 modifies its reviewer-routing input, while retaining the
  Task 3 wrapper-source rewrite already made to that test;
- rewrite
  `test_task_2b_routing_reference_keeps_routes_and_outcomes_without_git_protocol`
  to preserve route, availability, no-substitution, `CONFLICTED`, and owner
  adjudication assertions while removing only the retired Codex
  approval/profile configuration assertions;
- rewrite `test_agy_truncated_answer_is_terminal_without_repair_or_provider_switch`
  to retain every truncated-answer terminality assertion while removing only
  the retired `--sandbox read-only` requirement; and
- preserve `test_fresh_codex_native_result_admission_is_semantic_not_json` and
  the historical
  `test_fresh_codex_admission_docs_record_agy_fence_tolerance` unchanged. Add a
  new `test_batched_receipt_fence_custody_is_strict` over only the active
  Task 7 skill/reference files, requiring one outer fence, inner backticks as
  data, and original-byte receipt hashing; and
- update
  `test_shared_review_prompt_contract_defines_envelope_and_mode_specific_results`
  to preserve the byte-identical unbatched profile and assert the separately
  selected `batched-full-coverage` profile; and
- split the provider-skill portion retired from
  `test_company_fleet_guides_and_terms_are_removed_but_personal_templates_remain`
  into
  `test_provider_skills_retain_personal_routes_without_company_fleet_guidance`:
  scan `PROVIDER_SKILLS` plus `REVIEW_SKILL` for the existing company/fleet
  stale-term set and preserve the Gemini skill's
  `business, Vertex, or API-key` route assertion. Task 6 keeps only its
  migration/bootstrap/protocol-owned portion, and Task 8 owns the public-doc
  portion below.
- preserve and run
  `test_formal_review_guards_one_worktree_and_reruns_the_whole_round` and
  `test_formal_review_uses_wrapper_serialization_and_native_semantics` because
  their production inputs are wholly Task-7-owned review skill/reference
  files; retain their simple-digest compatibility and semantic-admission
  assertions; and
- preserve and run
  `test_provider_invocation_examples_are_explicit_argv_arrays` and
  `test_cross_family_skill_requires_complete_fresh_codex_reference`; their
  wrapper argv, reference completeness, no-edit, same-directory, and
  no-inline-source inputs are wholly Task-7-owned; and
- preserve and run
  `test_cross_family_skill_body_stays_within_progressive_disclosure_limit`,
  `test_provider_skills_share_the_repair_protocol_without_legacy_repair_shell`,
  and `test_active_long_references_have_resolving_contents_links` in this Task
  7 GREEN gate because their skill-size, repair-link, and contents-anchor
  inputs are wholly Task-7-owned.
- preserve and run the remaining wholly Task-7-owned contracts unchanged:
  `test_provider_dispatch_activation_is_explicit_and_cross_family_implicit_is_prepare_only`,
  `test_agy_formal_prompt_contract_does_not_require_unfenced_json`,
  `test_task_2a_provider_guides_keep_routes_and_do_not_impose_agy_fence_gate`,
  `test_formal_review_consolidation_requires_all_safe_and_adjudicates_conflict`,
  `test_formal_review_prompts_are_leader_controlled_and_trace_affected_surfaces`,
  `test_every_formal_review_mutation_or_route_mismatch_is_invalid`,
  `test_formal_review_reads_the_guarded_worktree_beyond_the_diff`,
  `test_formal_review_uses_existing_worktree_without_source_packet`,
  `test_formal_review_provider_calls_use_worktree_cwd`,
  `test_obsolete_review_snapshot_source_and_reference_are_absent`,
  `test_formal_review_inspects_governing_documentation_in_the_worktree`,
  `test_docs_use_current_google_preflight_instead_of_a_version_threshold`,
  `test_dispatch_skills_keep_nonterminal_tool_handles_pending`,
  `test_formal_review_records_authorization_once_and_uses_agent_review`,
  `test_standalone_google_dispatch_requires_authorized_approved_data`,
  `test_standalone_claude_dispatch_requires_authorized_approved_data`,
  `test_gemini_skill_omits_legacy_packet_compatibility_and_cleanup_details`,
  `test_external_formal_prompts_treat_worktree_source_as_untrusted_data`,
  `test_external_formal_prompts_require_prepared_directory_relative_citations`,
  `test_r17_scope_specific_reviewer_commands_are_fail_closed_and_literal_safe`,
  `test_r17_capability_and_fingerprint_contract_is_canonical`,
  `test_fresh_codex_prompt_requires_semantic_labels_without_json_priming`,
  `test_fresh_codex_citations_are_fenced_to_worktree_paths`,
  `test_formal_agy_leg_uses_the_existing_worktree_without_packet_preflight`,
  `test_formal_review_prompts_require_absolute_worktree_identity`, and
  `test_task4_cross_family_skill_names_catalog_selector_inline`. These tests
  read only Task-7-owned skill/reference paths plus the four explicitly
  unchanged provider-neutral `agents/openai.yaml` files where named.

Explicitly defer these public/status-dependent rewrites to Task 8 Step 3,
where their asserted files change:

- `test_distribution_docs_describe_one_installed_analyzer_and_launcher`;
- `test_package_version_and_removed_release_aliases_are_current`;
- `test_public_docs_state_formal_schema_and_phase_based_fallback`;
- `test_gemini_formal_fallback_requires_separate_exact_route_enforcement_proof`;
  and
- `test_google_leg_prefers_agy_then_uses_configured_gemini_fallback`.

Task 7 must not edit README, SECURITY, CHANGELOG, or status bytes to force an
early full-suite pass. Its GREEN gate is the exact focused skill-owned set
below; Task 8 runs the complete distribution file after resolving every named
public/status disposition.

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k "formal_review_requires_full_family_batch_matrix or provider_skill_examples_inherit_native_permissions or fresh_codex_template_renders_formal_kind_and_approved_data_boundary or r17_fresh_template_is_renderable_and_scope_mapped or fresh_codex_example_has_complete_no_edit_worktree_contract or r17_template_scope_execution_is_conditional_and_deletion_safe or r17_fresh_helpers_execute_against_hermetic_filesystem or fresh_codex_template_preserves_unbatched_and_selects_batched_profile or formal_review_uses_one_prepared_directory_and_bound_evidence_digests or fresh_codex_profiles_separate_semantic_compatibility_from_batched_receipts or every_review_leg_uses_the_shared_prompt_contract or formal_review_physically_excludes_only_exact_test_roots_and_uses_prepared_paths or task_2a_provider_guides_delegate_shared_formal_preparation or task_2b_gemini_guide_keeps_fallback_contract_without_shared_protocol or google_fallback_requires_pre_dispatch_agy_unavailability or task_2b_routing_reference_keeps_routes_and_outcomes_without_git_protocol or agy_truncated_answer_is_terminal_without_repair_or_provider_switch or fresh_codex_native_result_admission_is_semantic_not_json or batched_receipt_fence_custody_is_strict or shared_review_prompt_contract_defines_envelope_and_mode_specific_results or provider_skills_retain_personal_routes_without_company_fleet_guidance or cross_family_skill_body_stays_within_progressive_disclosure_limit or provider_skills_share_the_repair_protocol_without_legacy_repair_shell or active_long_references_have_resolving_contents_links or provider_skills_use_final_process_state_for_corrected_extraction_failure or formal_review_uses_owner_routing_baseline_and_bounded_escalation or formal_review_guards_one_worktree_and_reruns_the_whole_round or formal_review_uses_wrapper_serialization_and_native_semantics or provider_invocation_examples_are_explicit_argv_arrays or cross_family_skill_requires_complete_fresh_codex_reference"'
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k "provider_dispatch_activation_is_explicit_and_cross_family_implicit_is_prepare_only or agy_formal_prompt_contract_does_not_require_unfenced_json or task_2a_provider_guides_keep_routes_and_do_not_impose_agy_fence_gate or formal_review_consolidation_requires_all_safe_and_adjudicates_conflict or formal_review_prompts_are_leader_controlled_and_trace_affected_surfaces or every_formal_review_mutation_or_route_mismatch_is_invalid or formal_review_reads_the_guarded_worktree_beyond_the_diff or formal_review_uses_existing_worktree_without_source_packet or formal_review_provider_calls_use_worktree_cwd or obsolete_review_snapshot_source_and_reference_are_absent or formal_review_inspects_governing_documentation_in_the_worktree or docs_use_current_google_preflight_instead_of_a_version_threshold or dispatch_skills_keep_nonterminal_tool_handles_pending or formal_review_records_authorization_once_and_uses_agent_review or standalone_google_dispatch_requires_authorized_approved_data or standalone_claude_dispatch_requires_authorized_approved_data or gemini_skill_omits_legacy_packet_compatibility_and_cleanup_details or external_formal_prompts_treat_worktree_source_as_untrusted_data or external_formal_prompts_require_prepared_directory_relative_citations or r17_scope_specific_reviewer_commands_are_fail_closed_and_literal_safe or r17_capability_and_fingerprint_contract_is_canonical or fresh_codex_prompt_requires_semantic_labels_without_json_priming or fresh_codex_citations_are_fenced_to_worktree_paths or formal_agy_leg_uses_the_existing_worktree_without_packet_preflight or formal_review_prompts_require_absolute_worktree_identity or task4_cross_family_skill_names_catalog_selector_inline"'
```

Expected: every selected Task 7-owned distribution contract passes. No
public/status-dependent test is weakened or claimed GREEN before Task 8.

- [ ] **Step 6: Commit the skill contract**

```bash
git add \
  skills/triad-cross-family-review/SKILL.md \
  skills/triad-cross-family-review/references/review-prompt-contract.md \
  skills/triad-cross-family-review/references/reviewer-routing.md \
  skills/triad-cross-family-review/references/fresh-codex-formal-review.md \
  skills/triad-claude-dispatch/SKILL.md \
  skills/triad-antigravity-dispatch/SKILL.md \
  skills/triad-gemini-dispatch/SKILL.md \
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
- Modify only the active behavioral-contract rows `Impact`, `Default approval
  path`, and `Fail-closed posture`, plus the two active pre-R14
  statements beginning `Provider read-only policy remains intact` and `Test
  source is not sent` in:
  `docs/status/2026-07-22-formal-review-routing-verification.md`
- Create: `docs/status/2026-07-30-v0.2.532-release-notes.md`
- Modify: `tests/test_distribution_contract.py`
- Modify: `tests/test_migration_contract.py`

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
    assert "agy calls may transact against Antigravity CLI runtime settings" not in english
    assert "Antigravity settings under `~/.gemini/antigravity-cli/` are transacted" not in english
    assert "agy 호출은 `~/.gemini/antigravity-cli/` 아래" not in korean
    assert "Antigravity settings는 agy 호출 중" not in korean
```

- [ ] **Step 2: Run the release-contract test to verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k 02532_public_contract'
```

Expected: manifest remains `0.2.531` and the public native/full-coverage language is absent.

- [ ] **Step 3: Update English, Korean, security, status, and release metadata**

At the start of this step, obtain the actual current calendar date in the
workspace timezone (`Asia/Seoul`) and record `Task 8 candidate_date:
YYYY-MM-DD` in this plan's ignored SDD progress ledger. Use that exact recorded
date in the modified current-state handoff and in a `Candidate date:
YYYY-MM-DD` field in the new 0.2.532 release notes. Do not freeze a future
execution date into this admitted plan. In the dated historical routing
ledger, modify only the three named active behavioral-contract rows and the two
named active pre-R14 statements required by this task; preserve its date and every
formal-round ledger byte.

Document:

- native permission inheritance and no hidden override;
- the owner-approved distinction between retained wrapper child-process
  scrubbing after trusted startup and removed pre-spawn
  `shell_environment_policy`, including the trusted terminal/Python/PATH
  prerequisite;
- native AGY headless fail-closed behavior and narrow user/project remediation;
- ordinary/non-formal Gemini fallback only for the exact no-final-summary
  `EXIT_BINARY_MISSING` plus wrapper-owned pre-submission `PtyStartError`
  diagnostic; every final-summary result is post-dispatch and
  fallback-ineligible;
- the intentional `0.2.532` breaking fallback migration: missing/invalid
  `TRIAD_AGY_BIN` and missing `agy` on `PATH` are direct fallback-ineligible
  route-setup errors, with install/configure-AGY or explicitly authorize a
  separate Google route as the migration paths;
- `permission-unavailable` in both README exit-65 legends and the matching
  `test_task2_readme_exit_code_legends_match_reachable_classes` assertion,
  distinct from authentication, quota, and truncated-answer classifications;
- Gemini's provider-owned workspace-trust requirement after `--skip-trust`
  removal, with no TRIAD bypass or speculative detector;
- removal of both English statements and both Korean mirrors claiming that agy
  calls transact `~/.gemini/antigravity-cli/` settings or advising the owner
  not to edit agy permissions concurrently. That operating advice belonged to
  the retired `_agy_settings` transaction and is not current provider-runtime
  guidance;
- full diff plus complete affected-source closure;
- all-family/all-batch coverage;
- source-grounded observations, exact full-file ranges, and deterministic
  coverage admission;
- exact plugin-owned legacy cleanup and owner-setting preservation;
- provider launchers pin the install-resolved classifier path, while bootstrap
  prints the direct owner apply argv with the same required explicit
  `--classifier-file`; no current documentation claims an installed apply
  launcher or lets the owner apply path recompute an ambient default;
- the intentional UTF-8 evidence boundary: a non-UTF-8 current source fails
  closed with `non-UTF-8 source`; the leader must not omit it from closure and
  must instead defer the candidate or obtain owner approval for a separately
  reviewed design that adds support;
- the `0.2.532` migration from removed wrapper flags and removed
  missing-binary Gemini-fallback triggers; and
- fresh-session verification requirements.

State the evidence limit precisely: provider-native file-read telemetry is
retained and digest-bound when exposed; otherwise coverage is prompt-controlled
and admitted through source-grounded receipts, independent family review, and
leader reproduction, not claimed as provider-enforced proof.

Mark prior `0.2.529`/`0.2.531` status facts as historical where they remain in
current handoff documents. Apart from the three active pre-R14 surfaces owned
above, do not rewrite dated formal-round ledger content.
In `docs/status/2026-07-22-resume-prompt.md`, remove from active guidance the
exact sentences `Formal plan/pre-merge legs do not receive test source` and
`Reviewers must not receive, open, or review test source`. In
`docs/status/2026-07-22-current-state.md`, likewise remove the active pre-R14
sentence `Test source stays out of reviewer scope`; retain any of these claims
only if the containing old round is explicitly labeled pre-0.2.532 history.
Extend `test_task2_active_handoffs_use_complete_shared_directory_input` to
require all three sentences absent from their active pre-R14 guidance,
alongside its routing-ledger assertions.
Write only candidate-scoped behavior, migration, known pre-candidate evidence,
and the still-pending release checklist to
`docs/status/2026-07-30-v0.2.532-release-notes.md`. Do not prestate post-commit
verification, formal-gate, install, merge, tag, or release facts in tracked
documentation. Those later facts belong to the ignored external release
ledger defined below.

In this step, also update the existing
`test_package_version_and_removed_release_aliases_are_current` assertions from
0.2.531 to exact 0.2.532 manifest and changelog-header expectations, and update
`tests/test_migration_contract.py::test_release_headers_are_in_descending_order`
to assert `0.2.532 < 0.2.531 < 0.2.530 < 0.2.529 < 0.2.528 < 0.2.527` by changelog
position. These existing assertions are part of the Task 8 RED/GREEN cycle,
not deferred documentation cleanup.

Rewrite the cross-family `.codex-plugin/plugin.json` `defaultPrompt` to name
`batched-full-coverage` as the operational pre-merge gate profile and
`formal-gate` as the unbatched compatibility formal-plan profile only. Extend
`test_plugin_default_prompts_require_bounded_review_inputs` to require those
two exact profile literals and their distinction, so the shipped prompt cannot
direct the 0.2.532 full-coverage gate to a non-admissible result shape.

Resolve every public/status-dependent disposition deferred by Tasks 6 and 7
in this same RED/GREEN cycle:

- add `test_public_docs_remain_personal_without_company_fleet_guidance` over
  README.md, README.ko.md, and SECURITY.md, preserving the public-document
  stale company/fleet-term assertions split from the former combined test;
- retain
  `test_review_docs_distinguish_formal_advisory_and_sdd_test_boundaries` and
  update only its Task-8-owned README/SECURITY/CHANGELOG expectations to the
  no-exclusion formal-plan/pre-merge boundary while preserving its provider
  shared-contract and normal-SDD test-source assertions;
- retain
  `test_r17_leader_fingerprint_is_unscoped_and_current_surfaces_ban_only_separate_artifacts`:
  preserve its review-skill shared-directory, simple `content_digest`,
  no-inline-source, and obsolete-fingerprint assertions while updating its
  Task-8-owned public/status surfaces to the 0.2.532 contract;
- rewrite `test_distribution_docs_describe_one_installed_analyzer_and_launcher`
  as `test_distribution_docs_describe_native_repair_and_local_apply`: require
  the fresh native proposal-only child and login-shell
  `python3 bin/apply_patch.py` owner path, and require the retired
  `triad-repair-analyzer` and `triad-apply-repair` names to be absent from
  README/README.ko/SECURITY current guidance;
- rewrite `test_google_leg_prefers_agy_then_uses_configured_gemini_fallback`:
  preserve AGY primary-route, configured Gemini route, and invalid-family-round
  assertions; replace generic fallback-when-AGY-is-unavailable language with
  the exact eligible owned-`PtyStartError` proof; and require README/README.ko
  to document the breaking migration that missing/invalid `TRIAD_AGY_BIN` and
  missing `agy` on `PATH` are route-setup errors rather than fallback triggers;
- rewrite `test_readmes_use_ordinary_codex_without_profile_or_alias` to retain
  ordinary-Codex and no-profile/no-alias assertions while requiring the same
  authenticated login terminal and absence of rules-wired, repair-agent,
  permission-profile, and permission-opt-out claims;
- move the current-surface part of
  `test_r14_corrected_round_ledger_and_upgrade_containment_contract_is_present`
  here: preserve its exact R14 literals in all three historical handoffs,
  including
  `docs/status/2026-07-22-formal-review-routing-verification.md`, preserve the
  launcher child-scrub assertion, and replace only README/SECURITY current
  rules/profile/shell-entry assertions with the native-permission and exact
  legacy-cleanup contract;
- rewrite `test_public_docs_state_formal_schema_and_phase_based_fallback` to
  require the exact no-final-summary exit-4/owned-`PtyStartError` eligibility,
  reject every final-summary result, and require the retired phase taxonomy to
  be absent from README/README.ko while preserving current full-coverage and
  legacy `FormalReview` compatibility language;
- rewrite
  `test_gemini_formal_fallback_requires_separate_exact_route_enforcement_proof`
  across the now-current provider/public/status surfaces: preserve separate
  owner authorization, exact route/data boundary, unavailable-leg, and
  invalid-round assertions; replace only retired enforcement-policy language
  with immutable-directory, prompt/no-edit, digest/mutation, and strict
  admission requirements;
- rewrite
  `test_task_3c_current_handoffs_use_shared_directory_and_label_history` so
  README/README.ko must omit
  `TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1` and
  `TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1`, while the 0.2.529 historical
  CHANGELOG section retains those exact migration-history names and the new
  0.2.532 section does not advertise them as current controls;
- retain `test_task2_active_handoffs_use_complete_shared_directory_input`
  while adding exact assertions that the routing-verification ledger labels
  its former provider-read-only, plugin-owned launcher-rule, and formal
  test-source-exclusion claims as pre-0.2.532 history, states that 0.2.532
  inherits provider permissions and generates no Codex permission state, and
  states that 0.2.532 formal plan/pre-merge rounds include all repository test
  source. Require the three exact former active sentences named above to be
  absent from the active pre-R14 sections of their owning handoffs.
  Task 8 must preserve the test's six active shared-directory literals in all
  three modified handoffs; and
- rewrite
  `test_status_handoff_records_current_release_branch_without_future_git_authority`
  as `test_status_handoff_records_frozen_02532_candidate_without_future_publication_claims`:
  require branch `release/0.2.532`, pending external verification/publication,
  and no premature upstream, merge, tag, release URL, or completed-release
  claim in the frozen tracked handoffs.
- rewrite `test_r21_handoffs_date_current_result_and_mark_687_historical` so
  it parses the modified current-state handoff's ISO-8601 `Updated:` value and
  the new release notes' ISO-8601 `Candidate date:` value, requires them to be
  equal and not earlier than the 2026-08-02 plan-approval date, and keeps the
  routing ledger at exact `Updated: 2026-07-24`. Retain
  all existing historical/current result-label assertions. The implementer
  must compare the tested value with the exact Task 8 candidate date recorded
  in the ignored SDD ledger before committing.

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
  docs/status/2026-07-22-formal-review-routing-verification.md \
  docs/status/2026-07-22-resume-prompt.md \
  docs/status/2026-07-30-v0.2.532-release-notes.md \
  tests/test_distribution_contract.py \
  tests/test_migration_contract.py
git commit -m "release: 0.2.532"
```

This commit freezes the release-candidate tracked bytes. After it, Steps 6-11
write verification, review, installation, publication, and handoff evidence
only below ignored `_runs/releases/0.2.532/` or the ignored review-round path.
Any later tracked edit, including a release-note or current-state edit, must be
committed as a new candidate and forces complete repetition of Steps 6-8.

- [ ] **Step 6: Run the complete local verification suite**

From `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests'
```

From the repository:

```bash
bash -n scripts/bootstrap.sh
triad_release_base="$(git rev-parse release/0.2.530^{commit})"
git merge-base --is-ancestor "$triad_release_base" HEAD
git diff --check "$triad_release_base"..HEAD
git diff --check
git diff --cached --check
```

Expected: complete pytest suite passes, Bash syntax passes, the entire
committed release range is whitespace-clean, and both worktree/index diff
checks are clean.

Record the exact commands, exit status, test count, commit, release-base OID,
and diff-check results in ignored
`_runs/releases/0.2.532/local-verification.md`; do not edit tracked release
notes or handoff files after the candidate commit.

- [ ] **Step 7: Run the hostile-path and large-diff behavior proof**

Run the deterministic fixtures that construct the 12-group, 1,200-section,
10,000,000-byte diff, hostile paths, non-routine impact edge, oversized source,
complete three-family receipts, and one deliberately incomplete receipt:

```bash
/bin/zsh -lic 'python3 -m pytest -q \
  workspace/triad-codex-dispatch-reliability/tests/test_review_evidence.py::test_prepare_and_validate_cli_are_cwd_independent \
  workspace/triad-codex-dispatch-reliability/tests/test_review_evidence.py::test_prepare_large_diff_is_deterministic_and_preserves_hostile_paths \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_admission_requires_every_path_from_every_family \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_schema_cli_emits_canonical_batch_receipt_contract \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_admission_artifact_binds_candidate_state_and_evidence \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_manifest_path_echo_without_source_grounding_is_rejected \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_missing_path_evidence_is_rejected \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_not_safe_receipt_blocks_admission \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_critical_or_major_finding_blocks_admission \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_open_questions_block_admission \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_unresolved_edge_may_be_omitted_but_blocks_admission \
  workspace/triad-codex-dispatch-reliability/tests/test_review_coverage.py::test_admission_rejects_missing_family'
```

Record the fixture's pre/post source-tree digest and evidence digest in
ignored `_runs/releases/0.2.532/hostile-proof.md`.

Expected: complete evidence admits, missing evidence fails, no hostile path executes, and the pre/post review-root digest is unchanged.

- [ ] **Step 8: Run the mandatory pre-merge three-family full-coverage candidate review**

Prepare one immutable candidate directory containing current approved
production source, configuration, documentation, `change-evidence`, and the
exact owner/project test-source boundary. Use the Task 1 CLI with the recorded
full `triad_planning_head` as `--base-commit`; the supplied `candidate.diff`
must be the exact canonical diff produced by the documented argv. Require no
nonignored untracked entry, then run `validate` and record its byte-identical
candidate-state summary before dispatch. Record the immutable directory digest
and the same canonical worktree fingerprint independently in the round ledger.
The bounded evidence helper and the leader record use the design's exact
length-prefixed tagged-record algorithm over current `HEAD`, full
`GIT_OPTIONAL_LOCKS=0` porcelain status, binary/full-index staged and unstaged
diffs, and NUL-sorted nonignored untracked path plus content/link-text digests.
An unreadable, unsupported, or nonignored untracked entry stops the gate. Do
not expose Git execution to provider legs.

Before `prepare`, generate the one receipt contract, then copy and bind those
exact bytes through the evidence command. Execute every literal `python3`
command in this step through the workspace-required `/bin/zsh -lic`
login-shell boundary from `/Users/chaniri/codex_workspace`; each displayed
argv is the inner command and remains cwd-independent:

For this repository the exact no-exclusion test-source root is `tests/`.
Generate canonical `required-source-boundary.json` with roots exactly
`["tests"]`. Capture the current candidate's raw NUL inventories with
`GIT_OPTIONAL_LOCKS=0 git ls-files -z --cached -- tests/` and
`GIT_OPTIONAL_LOCKS=0 git ls-files -z --deleted -- tests/`; set `paths` to the
cached set minus the worktree-deleted set, sorted by UTF-8 path bytes. Record
both raw inventories' SHA-256 values and the resulting current path count in
the ignored round ledger. Add every changed current test path once through its canonical
diff row and every other current test path once as
`reason=required-test-source`, `change_kind=affected-unchanged`,
`previous_path=-`, and exact
`reached_from=owner-approved-no-exclusion-test-boundary`; staged or unstaged
deleted test paths remain one canonical deleted changed row but are absent
from the current boundary JSON. Copy every current boundary path byte-for-byte into the same
review-relative prepared path. The evidence CLI independently recomputes the
Git inventory and stops on any missing, extra, duplicate, non-regular,
symlinked, or non-UTF-8 test entry before output.

```bash
python3 /absolute/toolkit-root/bin/review_coverage.py schema \
  --output /absolute/project/worktree/_runs/reviews/<id>/BATCH_RECEIPT.schema.json
python3 /absolute/toolkit-root/bin/review_evidence.py prepare \
  --review-root /absolute/project/worktree/_runs/reviews/<id>/prepared \
  --base-commit <exact-triad-planning-head-full-oid> \
  --diff-file /absolute/project/worktree/_runs/reviews/<id>/candidate.diff \
  --impact-input /absolute/project/worktree/_runs/reviews/<id>/impact-closure.tsv \
  --required-source-boundary /absolute/project/worktree/_runs/reviews/<id>/required-source-boundary.json \
  --receipt-contract /absolute/project/worktree/_runs/reviews/<id>/BATCH_RECEIPT.schema.json \
  --output-dir /absolute/project/worktree/_runs/reviews/<id>/prepared/change-evidence \
  --batch-byte-limit 262144
python3 /absolute/toolkit-root/bin/review_evidence.py validate \
  --review-root /absolute/project/worktree/_runs/reviews/<id>/prepared \
  --evidence-dir /absolute/project/worktree/_runs/reviews/<id>/prepared/change-evidence
```

Require the schema stdout digest to match
`change-evidence/BATCH_RECEIPT.schema.json`, and pass the exact prepared
`batch_receipt_contract_path` to every batch prompt.

Select the `batched-full-coverage` result profile for every family/batch
dispatch in this step; do not use the unbatched `formal-gate` compatibility
profile. Render every prompt with the exact source-tree digest,
change-evidence digest, batch ID, batch manifest, and prepared strict
`BatchReceipt` contract path. A response in the four-element unbatched profile
is invalid and cannot be converted into a receipt.

Dispatch:

- current owner-authorized Claude Opus route;
- current accepted Google-family Pro High route without a TRIAD permission override; and
- fresh Codex default child with `fork_turns="none"` and the current approved formal-review model/effort.

Every family reviews every batch and returns valid receipts. If native AGY
reports `permission-unavailable`, stop the formal gate and report the required
user/project permission decision. This is post-dispatch and cannot activate
Gemini fallback in the same round; do not insert a bypass or count a different
family twice. A separately authorized Gemini formal fallback remains limited
to the exact proven pre-dispatch AGY-unavailability signal and must retain the
same prepared-directory, prompt/no-edit, digest/mutation, and admission
contracts.

After every exact provider response byte stream is saved, run the sole machine
gate explicitly:

```bash
python3 /absolute/toolkit-root/bin/review_coverage.py admit \
  --review-root /absolute/project/worktree/_runs/reviews/<id>/prepared \
  --evidence-dir /absolute/project/worktree/_runs/reviews/<id>/prepared/change-evidence \
  --receipts-root /absolute/project/worktree/_runs/reviews/<id>/results \
  --output /absolute/project/worktree/_runs/reviews/<id>/coverage-admission.json
```

Pass only if the command exits 0, the artifact exists, its CandidateState and
source/change digests exactly equal the immediately revalidated evidence
summary, `admitted` is true, all three required family coverages are `SAFE`,
and all unresolved/open-question lists are empty. Preserve that artifact,
provider receipts, pre/post review-root digest, and pre/post canonical
fingerprint in the ignored round ledger. Provider prose or a hand-written
summary is never a substitute.

Expected: three valid family coverages, no unresolved path, identical pre/post
candidate digest, identical pre/post canonical-worktree fingerprint, and an
exact digest-bound `coverage-admission.json` with three `SAFE` verdicts, or a
stopped release with evidence-backed findings.

- [ ] **Step 9: Correct accepted findings through new RED/GREEN cycles**

For each reproduced defect or approved underspecification, add one focused failing test, implement the minimum correction, run neighboring tests, and commit. If candidate bytes change, rebuild evidence and run a fresh complete three-family round.

Expected: no finding is applied solely because a provider requested it, and no changed candidate reuses a prior verdict.

If any accepted correction changes tracked bytes, commit it, discard the old
candidate admission for release purposes, and repeat the full local suite,
hostile proof, evidence preparation, three-family dispatch, and machine
admission over the new commit. Never append a tracked “correction result” after
the final rerun.

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
cache path, child proof, and ephemeral output in ignored
`_runs/releases/0.2.532/install-proof.md`; do not modify the admitted tracked
candidate.

- [ ] **Step 11: Publish the verified release**

After all gates pass, stop unless the current owner task explicitly authorizes
the exact external repository, `release/0.2.532` push, and PR creation. Local
workspace autonomy or approval to implement/install is not remote-publication
authority. With that authorization present, first run these read-only checks:

```bash
git remote get-url origin
git branch --show-current
gh repo view --json nameWithOwner,url
```

Require `origin`, the GitHub repository identity, and the current branch to
equal the owner-authorized target and `release/0.2.532`. Any mismatch or absent
authorization stops before external mutation. Then:

```bash
git status -sb
git push -u origin release/0.2.532
gh pr create --base main --head release/0.2.532 --title "Release 0.2.532" --body-file _runs/releases/0.2.532/pr-body.md
gh pr checks --watch
```

Before `gh pr create`, generate ignored
`_runs/releases/0.2.532/pr-body.md` from the frozen tracked release notes plus
the exact local-verification, hostile-proof, formal-admission, and install-proof
ledger results. Confirm `git status --short` has no tracked change and rerun
the committed-range `git diff --check` immediately before push.

Merge only after required checks succeed and after obtaining separate explicit
owner authorization for the exact merge, tag, and release publication. Then
create/publish `v0.2.532` through the repository's existing release workflow.
Record the merge commit, tag/release URL, installed source/cache hashes, and fresh-session proof in
ignored `_runs/releases/0.2.532/published-handoff.md`. A later tracked status
update is a separate documentation change with its own review; it is not
silently added to the admitted release candidate.

Expected when each external action is authorized: remote branch, passing PR
checks, merged release, published `v0.2.532`, and matching
installed/fresh-session evidence. Otherwise stop with the verified local
candidate and exact pending authorization recorded.
