# Native Permissions and Full-Coverage Review Design

Date: 2026-07-30

## Goal

Make TRIAD use the permission mode already selected by the developer's
authenticated terminal while preserving independent, complete review of every
production source file affected by a change.

Token reduction applies only to transport, deduplication, caching, and bounded
batching. It must not reduce review scope, substitute risk sampling for
coverage, divide the affected source set between model families, or admit a
partial result as `SAFE`.

## Owner decisions

- Claude, the Google-family provider, and fresh Codex use the developer's
  current terminal, project configuration, credentials, and permission mode.
- TRIAD does not select, synthesize, strengthen, weaken, or bypass a provider
  permission mode.
- Every required model family independently reviews the complete affected
  production-source closure.
- A diff is the navigation seed, not the review boundary.
- Final formal review keeps the full-quality owner-authorized routes. Cheaper
  models or lower effort may be used for transport smoke tests only.
- Native AGY headless permission denial fails closed. TRIAD does not retry with
  `--dangerously-skip-permissions`.

## Baseline failures

### Permission override

The current wrappers and distribution contain a second permission-control
layer on top of the developer's selected environment:

- provider-facing `--sandbox read-only|workspace-write` modes;
- Claude permission-mode and tool-list synthesis;
- AGY global-settings deny transactions and terminal sandbox selection;
- version-gated AGY insertion of `--dangerously-skip-permissions`;
- Gemini policy injection;
- a pinned read-only repair Custom Agent;
- plugin-owned permission profiles, sandbox escalation rules, migration
  fragments, and documentation that describe those controls as the supported
  route.

A live native-mode spike showed the practical conflict. Fresh Codex inherited
the active unrestricted filesystem permission and wrote a bounded marker
outside the workspace. Claude completed the path-navigation spike without a
permission override. The AGY wrapper completed only after inserting
`--dangerously-skip-permissions`; raw AGY headless execution, with the same
terminal settings and no override, failed because it could not prompt for the
required `command` permission.

The new design removes the hidden policy layer. It does not hide the resulting
native AGY availability constraint or Gemini's provider-owned workspace-trust
requirement. A trust denial is surfaced as the provider's native failure; no
speculative Gemini message detector or trust bypass is added.

### Missing large-diff evidence

The current shared-directory contract gives every family the same prepared
production tree and task, but it does not require a concrete diff path,
change-evidence digest, deterministic change index, or per-file coverage
ledger. A reviewer can therefore inspect the directory correctly while
missing a changed or affected file without producing machine-checkable
evidence of that omission.

### Ambiguous summaries

The first synthetic large-diff spike placed group counts only in a Markdown
table. Claude and AGY derived the number of groups, while fresh Codex returned
the per-group patch count. Adding explicit `GROUP_COUNT=12` and
`PATCH_FILE_COUNT=1200` headers made all three families return the same result.
Machine-consumed evidence therefore uses named fields rather than visual-table
inference.

## Selected architecture

### Native permission inheritance

TRIAD becomes permission-neutral:

| Runtime | Selected behavior |
|---|---|
| Fresh Codex | Native default child; inherits the parent session's sandbox and approval mode |
| Claude | Wrapper forwards prompt, cwd, model, effort, and result controls only |
| AGY | Wrapper forwards prompt, cwd, selector, and result controls only |
| Gemini fallback | Wrapper forwards prompt, cwd, selector, and result controls only |
| Repair analysis | Fresh default child with a proposal-only task contract; no pinned read-only Custom Agent |

The wrappers remove their public `--sandbox` modes and every internal
permission-mode synthesis path. They never add yolo, bypass, accept-edits,
dont-ask, or equivalent controls. The CLI's native user/project settings decide
whether a tool call is allowed, denied, or requires interaction.

This owner-approved boundary also removes wrapper-injected read-only tool
allowlists, strict MCP/settings-source overrides, AGY terminal sandbox
selection, Gemini policy injection, and the plugin-managed pre-spawn
`shell_environment_policy`. Those are permission/tool/environment policy
controllers, not retained integrity controls. Review no-edit behavior is
prompt-controlled and detected through immutable snapshots, digests, and
pre/post fingerprints; TRIAD does not claim provider-enforced mutation
prevention. Wrapper child-process environment scrubbing remains after the
trusted launcher/interpreter starts, but TRIAD does not rewrite the developer's
login environment before that point.

The empirically observed native AGY headless denial returns the distinct
`permission-unavailable` terminal result. It retains AGY's bounded diagnostic
and is not reinterpreted as authentication failure, retried with broader
authority, or admitted as a review verdict. This design does not add message
detectors for Claude or Gemini without current evidence.

### Boundaries retained

Permission neutrality does not remove unrelated integrity and data controls.
TRIAD retains:

- explicit authorization before an external provider receives approved data;
- credential, token, authentication-file, environment-dump, provider-log, and
  unrelated-path exclusions;
- argv-array construction, executable-path pinning, prompt-file validation,
  and wrapper child-process environment scrubbing after trusted startup;
- one immutable shared review root and its before/after digest;
- leader-only canonical-worktree fingerprints;
- the no-edit and no-execution review task contract;
- mutation and digest-mismatch invalidation;
- strict result extraction and semantic admission;
- legacy packet validation where an existing compatibility caller explicitly
  invokes it.

These controls validate data and result custody. They do not choose the
developer's permission mode.

The canonical-worktree fingerprint remains a leader-only operation and is
never a reviewer command. The evidence preparation and admission modules may
invoke the same bounded read-only capture routine so the submitted diff is
bound to the actual candidate state; this does not expose Git execution to
provider legs or restore a general worktree API. The fingerprint SHA-256 hashes
length-prefixed, tagged byte records in this order: current `HEAD`; full
`GIT_OPTIONAL_LOCKS=0 git status --porcelain=v1 -z --untracked-files=all`;
full staged and unstaged
`git diff --binary --full-index --no-ext-diff`; then the NUL-sorted output of
`git ls-files --others --exclude-standard -z` paired with each nonignored
untracked regular file's content digest or symlink's link-text digest. An
unreadable or unsupported untracked entry fails the fingerprint. The leader
compares the same record before and after a round. This design does not restore
the retired `canonical_git_visible_fingerprint` helper or expose Git execution
to provider legs.

Each fingerprint record is serialized as ASCII tag, NUL, decimal payload byte
length, NUL, then the exact payload bytes. The fixed tags are `HEAD`, `STATUS`,
`STAGED`, `UNSTAGED`, and one `UNTRACKED` record per sorted path. An
`UNTRACKED` payload is the ASCII kind `file` or `symlink`, NUL, the raw Git path
bytes, NUL, and the lowercase content or link-text SHA-256 hex digest. Command
failure or a non-regular/non-symlink untracked entry stops the round.

## Change-evidence format

The leader prepares one immutable review root:

```text
review-root/
├── <current approved production source, configuration, and documentation>
└── change-evidence/
    ├── CANDIDATE_STATE.json
    ├── REQUIRED_SOURCE_BOUNDARY.json
    ├── BATCH_RECEIPT.schema.json
    ├── CHANGESET.md
    ├── IMPACT_CLOSURE.tsv
    ├── PATCH_INDEX.tsv
    ├── MANIFEST.sha256
    ├── patches/
    │   └── <group-id>/<patch-id>.patch
    └── batches/
        └── <batch-id>.tsv
```

The canonical non-symlink evidence directory is exactly
`review-root/change-evidence`. Preparation, validation, and admission reject
an external path, an alternate in-root path, or any symlinked component rather
than excluding evidence from the immutable shared root. Preparation also
requires that exact output leaf to be absent and rejects any pre-existing
empty or non-empty directory, symlink, or non-directory with `evidence
directory exists`. A failed partial preparation is never reused: the leader
discards the entire leaf before retry. Validation and admission require the
successfully prepared existing directory.

The tracked repository `.gitignore` is an unchanged prerequisite input. Before
creating the implementation branch, the leader runs `git check-ignore
--no-index` over one exact `_runs/reviews/...` probe root and its candidate
diff, closure TSV, receipt schema, required-source-boundary JSON, admission
JSON, prepared root, and `prepared/change-evidence` leaf. All eight probes must
resolve through the tracked `_runs/` rule. Failure stops implementation and
requires a newly reviewed File Map change; success does not authorize or
require an ignore-rule edit.

`CANDIDATE_STATE.json` binds the evidence to one repository state. It is one
compact sorted-key JSON object containing the exact full base commit, current
`HEAD` commit, canonical-worktree fingerprint, and canonical full-diff
SHA-256. Preparation accepts only a lowercase, repository-width full
hexadecimal commit object ID that resolves as a commit and is an ancestor of
current `HEAD`, resolves the enclosing canonical Git worktree from
`review_root`, and requires the
review root plus all leader inputs and outputs to be ignored by that worktree.
It rejects every nonignored untracked entry so an added candidate path cannot
fall outside the canonical diff silently.

The canonical full diff is captured with `GIT_OPTIONAL_LOCKS=0`, a fixed C
locale, `core.quotepath=true`, `diff.noprefix=false`,
`diff.mnemonicPrefix=false`, exact `a/` and `b/` source/destination prefixes,
disabled color, external diff, and text conversion, full binary indexes, fixed
three-line context, the Myers algorithm with the indent heuristic disabled,
and explicit 50-percent rename detection, from the exact base commit to the
current tracked worktree state. These command-local settings override
prefix-affecting user Git configuration. The caller-supplied diff must be byte-identical
to that capture. Preparation rechecks the candidate fingerprint after writing
the evidence leaf. Validation and final admission resolve the same enclosing
worktree, recompute the candidate state and canonical diff, and reject any
field, digest, byte, or fingerprint mismatch. The candidate-state artifact is
included in the change-evidence digest and `MANIFEST.sha256`.

Candidate-state equality does not by itself prove that a copied prepared
source file equals its canonical-worktree counterpart. Preparation,
validation, and admission therefore open every non-deleted closure path in
both roots without following symlinks and require exact bytes, SHA-256, byte
count, and `splitlines()` line count. Deleted closure paths are absent in both
roots. This binds changed bytes outside visible hunks and all
affected-unchanged sources to the reviewed candidate. A stale or miscopied
prepared source invalidates the round before dispatch or admission. Every
regular file below the review root outside `change-evidence` must be exactly
one non-deleted closure path; an extra prepared regular file fails before
output. Consequently all exposed production, configuration, documentation,
build, and test context is candidate-bound rather than merely digest-stable.

`BATCH_RECEIPT.schema.json` contains the exact canonical compact sorted-key
JSON Schema emitted from the implementation's strict `BatchReceipt` model,
plus one LF. The leader generates it before evidence preparation; preparation
copies the exact ignored input bytes and binds the artifact into the
change-evidence digest and manifest. Every batch prompt receives its prepared
path as `batch_receipt_contract_path`. Admission regenerates the model schema
and requires byte equality, so neither documentation prose nor a stale schema
can substitute for the operational receipt contract. The schema CLI and final
admission CLI publish only to canonical absolute Git-ignored output paths with
no symlink leaf or ancestor. They validate custody before generation or
evidence parsing. Schema preserves every existing target/referent on refusal
and uses atomic replacement only after validation. Admission treats an
existing leaf as owned only when it is exact canonical JSON for the strict
prior admitted artifact. It removes only that verified prior leaf before
current validation, preserves and rejects every foreign or symlinked target,
leaves the canonical path absent on a later failure, and atomically publishes
a fresh artifact only after admission.

`REQUIRED_SOURCE_BOUNDARY.json` is the exact canonical compact sorted-key
object `{"paths":[...],"roots":[...]}` plus LF. For this release its exact
root is `tests/`, supplied by the approved no-exclusion project boundary. The
leader builds its UTF-8-byte-sorted path list from the current candidate's raw
NUL cached and worktree-deleted Git inventories: current paths are
`git ls-files -z --cached -- <roots...>` minus
`git ls-files -z --deleted -- <roots...>`. The leader records both inventory
digests. Preparation, validation, and admission independently recompute the
same deletion-aware current inventory, require every current tracked regular
path once in both the prepared root and closure, and bind the copied contract
into the manifest and change-evidence digest. Current unchanged tests use
reserved reason `required-test-source` with
`reached_from=owner-approved-no-exclusion-test-boundary`; changed tests retain
their canonical changed row and staged or unstaged deleted tests remain diff
evidence only.

`CHANGESET.md` contains named machine-readable headers followed by a compact
human summary:

```text
FORMAT_VERSION=1
GROUP_COUNT=<integer>
DIFF_FILE_SECTION_COUNT=<integer>
PATCH_FILE_COUNT=<integer>
AFFECTED_SOURCE_COUNT=<integer>
BATCH_COUNT=<integer>
SOURCE_TREE_DIGEST=<sha256>
CHANGE_EVIDENCE_DIGEST=<sha256>
```

`DIFF_FILE_SECTION_COUNT` is the number of canonical `diff --git` file
sections. `PATCH_FILE_COUNT` is the number of actual
`patches/<group-id>/<patch-id>.patch` artifacts and therefore equals the
`PATCH_INDEX.tsv` row count. They differ when a file section has multiple
hunks.

`PATCH_INDEX.tsv` is normative. It contains one row for each canonical patch
receipt, with this exact header and column order:

```text
patch_id	group_id	section_ordinal	hunk_ordinal	change_kind	previous_path	path	sha256	byte_count
```

`patch_id` is the canonical receipt identifier. A file section without a
textual hunk has one file-level `patch_id`; use `-` for its `hunk_ordinal`.
Use `-` for an absent `previous_path`. The allowed `change_kind` values are
exactly `modified`, `added`, `deleted`, and `renamed`.
The canonical artifact for each row is
`patches/<group_id>/<patch_id>.patch`; this exact path is also an allowed
finding-location surface.

For every textual hunk, preparation and validation parse the complete unified
hunk header and body. The standard optional text after the closing `@@` is an
opaque section/function heading: accept and preserve its exact bytes in the
patch shard, but do not interpret it or include it in range/body counts. Header
old/new counts must equal the respective body line counts. A positive new count
uses the inclusive current-source range
`new_start..new_start + new_count - 1`; it must start at one or later and end
within `line_count`. A zero new count uses a valid empty boundary
`0 <= new_start <= line_count`; it does not require `new_start == 0`. The
ordered context plus added lines, including the no-final-newline marker
semantics, must equal that exact current-source slice. For a deleted row only,
the new-side comparison source is the already specified empty byte string
while the current path must remain absent. Old-side starts are positive for a
positive count and non-negative for a zero count, because a zero-count
insertion may occur after any old-side line. A malformed, count-mismatched,
out-of-range, or content-mismatched hunk is invalid. This is the bounded
supported unified-text format, not a general patch engine.

`IMPACT_CLOSURE.tsv` is also normative. It contains one row per affected
production source, with this exact header and column order:

```text
path	reason	reached_from	change_kind	previous_path	content_sha256	byte_count	line_count	impact_edge_id	batch_id
```

`ImpactRow` therefore includes `change_kind`, `previous_path`, `line_count`,
and `impact_edge_id` in addition to the existing path, reason, reachability,
digest, byte-count, and batch fields. Changed rows use `impact_edge_id=-`.
The allowed closure `change_kind` values are exactly `modified`, `added`,
`deleted`, `renamed`, and `affected-unchanged`.
For an `affected-unchanged` row, derive `impact_edge_id` deterministically from
the exact UTF-8 bytes of `path`, `reason`, and `reached_from`.
The format records one canonical, leader-selected proof edge per affected
path. Multiple discovery paths do not duplicate the source row or introduce an
edge-list protocol; the leader selects the strongest reproducible edge and
still reviews the complete source. This is provenance for path inclusion, not
a claim that every possible graph edge is enumerated.

For a deleted path, no current source file is permitted: `path` and
`previous_path` both contain the canonical old path, record the SHA-256 of
empty bytes, `byte_count=0`, `line_count=0`, and retain its exact patch IDs.
The duplication is intentional: `path` remains the coverage key and
`previous_path` records change provenance. It needs exact patch evidence but no
current source evidence. For a renamed path, `previous_path` is the old path,
the new current source is required, and the rename/file-level patch ID is
bound. Modified, added, and affected-unchanged rows use `previous_path=-`.
`path` alone remains the coverage key. `change_kind` and `previous_path` are
required provenance fields, not a composite `(path, change_kind)` key.

For decoded UTF-8 current source, `line_count` is exactly
`len(text.splitlines())`. This gives zero for a zero-byte file and counts the
last logical line consistently whether or not the file ends in a newline.
Before computing it, preparation and validation reject U+000B, U+000C,
U+001C, U+001D, U+001E, U+0085, U+2028, and U+2029 with stable
`unsupported source line separator`. The accepted source model therefore has
the same line boundaries as unified diffs and provider line references without
adding a second line codec.

Reasons use a small stable vocabulary:

- `changed`;
- `import`;
- `caller`;
- `implementation`;
- `inheritance`;
- `registration`;
- `schema-consumer`;
- `configuration-consumer`;
- `build-consumer`;
- `runtime-entrypoint`;
- `lifecycle`;
- `error-path`;
- `owner-approved-project-edge`; or
- `required-test-source` (reserved for the owner-approved no-exclusion test
  boundary defined above).

The vocabulary records why a path is present. It does not attempt to implement
a universal static analyzer.

Each `batches/<batch-id>.tsv` manifest has the exact ordered header
`path\treason\tchange_kind\tcontent_sha256\tbyte_count\tline_count\tpatch_ids\timpact_edge_ids`.
It contains exactly one row per source path assigned to that batch, with no
duplicates, sorted by UTF-8 path bytes. `patch_ids` and `impact_edge_ids` are
comma-separated canonical ID lists in sorted order, use `-` for an empty list,
and canonical IDs never contain commas. Every row's assignment equals the same
path's `batch_id` in `IMPACT_CLOSURE.tsv`.

The manifest therefore lists the affected source paths, their complete
canonical `patch_id` set where applicable, content digests, byte counts, line
counts, and impact-edge IDs.
An oversized source receives one single-path batch and remains a complete file;
there is no source-shard or symbol-boundary protocol. Provider file-read ranges
may bound individual tool outputs, but all ranges remain required. Batching
never samples lines or omits low-risk files.

## Impact-closure preparation

The leader performs these bounded preparation actions:

1. Resolve the exact base commit, capture the canonical candidate state and
   full diff once, and prove the supplied diff is byte-identical.
2. Generate the canonical strict `BatchReceipt` schema and bind its exact
   bytes into the evidence directory.
3. Add every changed file and hunk as a seed.
4. Trace the seed through affected unchanged production code using the
   project's instructions, language-aware read-only tools, source search,
   build metadata, schemas, registrations, and runtime configuration.
5. Record each reached path and edge in `IMPACT_CLOSURE.tsv`, then prove every
   non-deleted prepared closure byte equals the canonical-worktree path.
6. Expand uncertain dynamic edges conservatively to the containing module or
   production root.
7. Stop with an open question when reflection, generated registration,
   runtime discovery, or a missing project boundary prevents a defensible
   closure.
8. Partition the complete closure deterministically by size and semantic
   boundaries.
9. Record the source-tree and change-evidence digests before dispatch.

`prepare_review_evidence` and `validate_review_evidence` fail when candidate
state cannot be reproduced, the supplied diff is a subset or other mismatch,
a parsed diff target lacks a `reason=changed` closure row, or a changed closure
row lacks a diff section. They also reject NUL, LF, CR, and TAB in `path`,
`reached_from`, and every `previous_path` other than `-` before TSV emission.
Both old- and new-side Git-quoted diff fields are decoded only far enough to
detect and reject those controls; no reversible generic field codec is
introduced. Spaces, quotes, backticks, and literal `$()` remain inert data and
execute nothing. The hostile-path test matrix includes renamed old-side paths
containing each of NUL, LF, CR, and TAB and requires the stable rejection
before any TSV output. This intentional `0.2.532` input limit fails with the
stable `non-UTF-8 source` diagnostic for any non-deleted current source and
with stable `unsupported source line separator` for the explicitly unsupported
decoded separators above; it never silently omits a path or admits partial
coverage.

A non-regular or symlinked prepared closure source fails during the prepared-
source comparison with `prepared source differs from candidate`, before
candidate-state recomputation. During validation and admission, the earlier
source-tree digest walk maps a symlink at a declared closure path to that same
diagnostic without following the referent. There is no competing `regular
file` diagnostic for this case. An unlisted prepared regular source fails with
the distinct stable `prepared file lacks closure row` diagnostic.

Validation uses one stable precedence for overlapping mutations: first verify
the persisted evidence and source digests against the prepared bytes, then
compare every prepared closure byte with the canonical candidate worktree,
then recompute and compare the complete candidate state. Tests for those three
diagnostics mutate, respectively, a prepared closure source, a stale prepared
copy before manifest completion, and a tracked non-closure candidate file.
This ordering makes `source digest mismatch`, `prepared source differs from
candidate`, and `candidate state mismatch` independently reachable without
weakening any later check.

The operational evidence CLI invokes these same preparation and validation
interfaces by absolute script and input paths, independent of cwd. Successful
`prepare` and subsequent `validate` calls emit the same deterministic compact
JSON summary only after the artifact validates. Argument, canonical-path, or
`EvidenceError` failures emit no success JSON or completed manifest and
terminate with the documented stable diagnostic contract. Any partial output
leaf is invalid and discarded before retry.

The implementation supplies deterministic inventory, manifest, digest, and
batching utilities. It does not claim language-independent impact discovery.
The leader remains responsible for project-specific caller and consumer
tracing.

## Full-coverage review matrix

Every family receives the same review root, objective, complete batch list, and
evidence digests.

The shared prompt also retains its simple `content_digest` for whole
review-directory custody and pre/post mutation comparison. The batched route
adds `source_tree_digest`, `change_evidence_digest`, batch metadata, and the
strict receipt contract; the simple digest never substitutes for those
machine-admitted evidence bindings.

| Required family | Batch 1 | Batch 2 | Batch 3 | All later batches |
|---|---:|---:|---:|---:|
| Claude family | required | required | required | required |
| Google family | required | required | required | required |
| Fresh Codex | required | required | required | required |

Perspective assignments change emphasis only. They never assign disjoint
source subsets.

For each changed file, a family reviews the complete current production file
and every changed hunk. For each affected unchanged file, it reviews the
complete current production file and verifies the recorded impact edge. A
family may process deterministic batches in separate fresh contexts, but its
family result is incomplete until every batch has a valid receipt.

The following is the one normative receipt schema in both the design and the
implementation plan. Each provider prompt returns exactly one strict
`BatchReceipt` JSON document per batch:

```text
PathEvidence:
  path
  content_sha256
  observation_line
  source_observation
  line_start
  line_end
  symbols
  changed_hunks
  verified_impact_edges
  disposition

BatchReceipt:
family
batch_id
source_tree_digest
change_evidence_digest
verdict
path_evidence
findings
affected_surfaces_inspected
unresolved_paths
open_questions
```

`path_evidence` is not a list of manifest paths. Every affected source path has
one compact record. A current non-empty source record contains its content
digest, the exact full-file line range `1..line_count`, one bounded exact
source observation and its line number, optional symbol annotations, every
changed hunk or recorded impact edge relevant to that path, and the reviewer's
disposition.
`source_observation` is a 1-160 character exact substring of the UTF-8 logical
line named by `observation_line`; when that line has at least eight characters,
the observation has at least eight, and it contains at least one
non-whitespace character whenever the source contains any non-whitespace
character. It is never written into
reviewer-visible manifests. A non-empty whitespace-only source retains its
full line range but uses empty observation text only when validation proves it
has no non-whitespace character. A zero-byte current source uses
`observation_line=None`, empty observation text, and
`line_start=line_end=None`. Deleted paths retain patch evidence but require no
current-source observation or line range: they encode
`source_observation=""`, `observation_line=None`, `line_start=None`,
`line_end=None`, and empty `symbols`.

For each receipt, the ordered `path_evidence.path` tuple and the ordered
`affected_surfaces_inspected` tuple each equal exactly the source-path tuple
assigned by that receipt's `batch_id`. Missing, extra, out-of-batch, reordered,
or duplicated paths invalidate the receipt. Canonical patch artifacts are
evidence for their assigned source path, not additional inspected-surface
entries. Consequently one batch cannot carry another batch's evidence while
an empty receipt satisfies the required file matrix.

For a changed current source containing at least one non-whitespace character
and at least one current line with a non-whitespace character outside all
validated new-side hunk ranges, `observation_line` must name one of those
non-whitespace outside-hunk lines. The
validator-proven whitespace-only exception takes precedence and keeps
`observation_line=None`. If no line outside the canonical patch hunk ranges
contains a non-whitespace character, including when outside lines are
whitespace-only but non-empty, the patch artifacts contain every current line
that can supply a valid non-whitespace observation and a patch-derivable
observation is allowed because no valid outside-hunk substring exists. This
exception is explicit evidence for the only observable source content that
can satisfy the observation contract, not a claim that patch-only inspection
generally proves full-file review. A receipt built only by echoing manifest
and index fields is otherwise uncovered.

The `batched-full-coverage` prompt repeats these exact observation length,
non-whitespace, outside-hunk, zero-byte, whitespace-only, and patch-derived
exception rules. The JSON Schema's structural bounds alone are not sufficient
provider instructions; prompt generation and receipt validation must share the
same semantic contract.

`PathEvidence` retains per-path `changed_hunks` and
`verified_impact_edges`; there is no redundant top-level
`verified_impact_edges` promise. Each receipt's `changed_hunks` set must
exactly equal the canonical `patch_id` set for its path. A resolved
affected-unchanged receipt's `verified_impact_edges` set must exactly equal the
expected `impact_edge_id` set. An unresolved affected-unchanged receipt may
contain any subset of expected IDs; the absent verification is represented by
its unresolved disposition and matching `unresolved_paths` entry, both of
which block admission. Extra, duplicated, and forged IDs are always invalid.
Changed rows must have an empty `verified_impact_edges`; affected-unchanged
rows must have an empty `changed_hunks`. Deleted and renamed rows follow their
canonical patch-ID sets rather than admitting arbitrary IDs.

`disposition` is also source-grounded within one receipt/batch. A receipt
finding location must map to a current path or canonical patch ID owned by that
same batch. For each path record, disposition is `unresolved` exactly when the
path appears in that receipt's `unresolved_paths`; otherwise it is `finding`
exactly when one of that receipt's admitted findings maps to the path, and
`no-finding` only when neither condition holds. A cross-batch finding location
or contradictory disposition invalidates the receipt; the finding must be
reported in the receipt that owns the path.

`BatchReceipt.findings` and `FamilyCoverage.consolidated_findings` use the
existing strict `FormalFinding` contract; free-form finding dictionaries are
not admitted. `FamilyCoverage` retains ordered receipt digests, covered paths,
consolidated findings, unresolved paths/questions, affected surfaces, and a
verdict. The leader persists the exact UTF-8 response bytes under a
family/batch-specific result path and passes those paths to
`validate_family_receipts`. Admission hashes those original bytes, then accepts
either raw JSON or exactly one outer Markdown fence whose optional info string
is `json`. For envelope detection it trims only outer ASCII whitespace; the
opening line is exactly three backticks or three backticks plus `json`, the
final non-whitespace line is exactly three backticks, and only the bytes
between those complete outer lines are extracted. Triple backticks inside the
inner JSON bytes are allowed because they may be ordinary string content; the
parser does not scan for them as fence tokens. Before strict Pydantic
validation, the extracted inner bytes receive one validation-only
standard-library JSON pass whose `object_pairs_hook` rejects a duplicate member
name at every object depth. The decoded value is discarded; the same original
inner bytes are then passed to strict Pydantic JSON validation so JSON tuple
fields retain strict JSON-mode semantics. Leading or trailing prose, nested or
multiple top-level fence
envelopes, a missing
field, or a family/batch mismatch is invalid. This deterministic outer-fence
step preserves the repository's observed AGY fence tolerance without adding
wrapper repair or changing response custody. Fresh Codex terminal text follows
the same custody rule; this is operational custody, not a new wrapper
responsibility.

The operational admission command consumes the validated evidence directory
and an exact receipt tree of `<family>/<batch-id>.json`, rejects missing and
extra receipt files, and atomically emits the sole machine-admissible
`coverage-admission.json`. A prose summary or manually assembled family result
cannot replace this command. Its output path is absolute, Git-ignored,
non-symlinked, and outside the immutable prepared review root; violating that
custody boundary fails before validation or writing. The artifact uses one
recursive strict wire schema: the exact four CandidateState fields; each exact
FamilyCoverage field (`family`, receipt digests, covered paths, consolidated
findings, unresolved paths, open questions, inspected surfaces, and verdict);
and the exact CoverageAdmission fields (format version, candidate state,
source-tree digest, change-evidence digest, admission boolean, and family
coverages). Every wire model forbids extra fields and uses strict validation.
The sole serializer dumps that validated wire value with UTF-8, non-ASCII
preservation, non-finite-number rejection, sorted keys, compact separators,
and exactly one final LF. An existing leaf is owned only after duplicate-key
rejection, strict recursive wire parsing, `admitted=true`, and byte-identical
reserialization through that sole serializer; pretty, reordered, missing,
extra, duplicate-member, or otherwise noncanonical regular files are foreign
and preserved. The artifact contains the revalidated format version, complete
CandidateState, source-tree digest, change-evidence digest, admission boolean,
and family coverages. The command exits nonzero and leaves
no artifact for a non-admitted result. Release gating requires the artifact's
bindings to match the immediately revalidated evidence and all three family
coverages to be `SAFE` with no unresolved path or question.
Receipt schema enforcement is offline. Original response bytes are the custody
and receipt-digest source; only the deterministic optional outer-fence removal
precedes strict JSON parsing. Wrappers do not add an in-band Pydantic repair
route. A malformed receipt makes that family leg invalid and requires its
complete fresh re-dispatch under the round contract.

Provider-native file-read telemetry is retained and digest-bound when the
provider exposes it. When a provider does not expose such telemetry, coverage
remains prompt-controlled and is admitted only through `path_evidence`, valid
source citations, cross-family independence, and leader verification. The
release documentation states this limitation; TRIAD does not claim
provider-enforced proof of every read.

## Coverage admission

A formal result is admissible only when:

- every changed file and hunk is covered by every required family;
- every row in `IMPACT_CLOSURE.tsv` is covered by every required family;
- every non-deleted covered path has the exact `1..line_count` range and a
  validated source observation absent from reviewer-visible manifests, except
  that a validator-proven non-empty whitespace-only source keeps its full
  range with no observation and a zero-byte current source has neither;
- every covered path's receipt `content_sha256` exactly equals its closure
  `content_sha256`; a deleted row's expected value is the SHA-256 of empty
  bytes;
- every recorded impact edge is either verified or produces an unresolved
  question;
- no family reports a missing batch or unresolved path;
- the three families used the same source-tree and change-evidence digests;
- the prepared receipt contract exactly equals the current canonical strict
  `BatchReceipt` model schema and is included in the evidence digest;
- validation at admission reproduces the exact base commit, `HEAD`, canonical
  diff, and candidate-state fingerprint recorded by preparation;
- every non-deleted prepared closure source still exactly equals the same
  canonical candidate-worktree path;
- the review-root digest and canonical-worktree fingerprint remain unchanged;
- the leader independently reproduces material caller, consumer, schema,
  configuration, and build relationships; and
- the existing finding, severity, evidence, and verdict contract passes.

The release consumes only the successful machine-emitted
`coverage-admission.json` carrying those exact candidate and evidence
bindings. Receipt prose or a manually reconstructed summary cannot satisfy
this condition.

`SAFE` is impossible when findings include Critical or Major, any receipt is
`NOT-SAFE`, or any unresolved path or open question exists. For current source,
optional symbols are annotations only; `line_start` and `line_end` are
mandatory and must equal `1` and `ImpactRow.line_count` for every non-empty
current source. A validator-proven non-empty whitespace-only source keeps that
range but requires no observation. A validator-proven zero-byte current source
and a deleted row require no observation, symbol, or line evidence. Current
non-deleted source must be UTF-8 for exact observation and finding-location
validation; invalid UTF-8 stops evidence preparation rather than reducing
coverage.

Every `FormalFinding.location` is an exact review-relative `path:positive-line`
reference. The validator admits only a digest-bound current closure path or
canonical patch artifact, reopens it without following symlinks, and rejects
an absent, out-of-range, or digest-mismatched location. A finding can never be
grounded only by a non-empty location string.

If any family discovers an affected source path that is absent from
`IMPACT_CLOSURE.tsv`, the leader expands the closure and invalidates the round.
The new path is not appended to only the other two families. All three families
start a fresh complete round over the corrected identical evidence.

`SAFE` is unavailable for sampled, partial, unresolved, digest-mismatched, or
family-partitioned coverage.

## Round convergence, triage, and correction scope

The leader classifies claims only after non-mutating verification against the
canonical worktree:

- `REPRODUCED`: direct source contradiction or deterministic evidence inside
  the approved design;
- `REACHABLE_UNPROVEN`: a reachable mechanism whose claimed failure has not
  been reproduced;
- `OUT_OF_SCOPE_OR_SPECULATIVE`: excluded by the approved design or deployment
  boundary; and
- `DESIGN_CHANGE`: a new capability, generalized abstraction, protocol,
  policy, or deployment assumption.

A failed reproduction remains `REACHABLE_UNPROVEN` unless direct evidence
establishes another class. Reviewer severity controls blocking; leader triage
controls whether code is authorized. Triage never converts a blocking result
into `SAFE`.
When explicit reviewed bytes prove that the claimed trigger is absent or
excluded by the approved boundary, the claim is
`OUT_OF_SCOPE_OR_SPECULATIVE`; otherwise a failed reproduction remains
`REACHABLE_UNPROVEN`. A refuted disposition is not a fifth triage class.

After a complete valid three-family round, the leader records exactly one
round state:

- `CLEAN`: every required result is `SAFE` and no unresolved claim remains;
- `CONVERGING`: the round adds or independently confirms a reproduced defect;
- `OSCILLATING`: a resolved claim returns without material new evidence; or
- `OWNER_DECISION`: the remaining evidence gap or blocking residual needs
  owner adjudication.

Apply the states in this order: `CLEAN`; `OWNER_DECISION` when any remaining
item requires the owner; `OSCILLATING` when no material new evidence remains;
otherwise `CONVERGING` when reproduced evidence remains.
`CONFLICTED` is an item state for surviving incompatible claims rather than a
competing round label. Round and item states are leader records only. They do
not admit coverage, release a blocking verdict, or authorize implementation,
merge, or release. A refutation or owner decision never rewrites an old receipt
as `SAFE`. A fresh complete round may follow corrected candidate bytes or
material new digest-bound evidence.

The residual ledger is leader-owned and stays outside the immutable
`review-root` and provider-response custody tree. The default location is
`_runs/reviews/<id>/residuals.md`. Its stable claim identifier is the pair of
review-relative finding path and trigger. Each entry records the originating
family and round, severity, leader triage, reproduction evidence, disposition,
and direct conflict. The ledger adds no receipt field, database, service, or
machine-admission input.

Even for a `REPRODUCED` claim, the leader stops for owner approval when the
proposed correction:

- adds a runtime guard, fallback, retry, lock, or validation layer;
- adds a production dependency, configuration, environment, or public-protocol
  surface;
- changes production paths outside the claim's impact closure except
  mechanically required caller or import updates; or
- exceeds 30 added-plus-removed non-generated production lines for one logical
  fix.

The leader measures the logical-fix production diff deterministically rather
than asking a reviewer to count it. Files already present in the approved File
Map remain inside the approved correction boundary. These conditions request
owner review; they are not automatic rejection rules.

## Token and context policy

The design reduces waste without reducing coverage:

- prompts carry paths, objectives, digests, and result profiles rather than
  source or diff bodies;
- every content object is addressed by digest and read once per required
  family context;
- stable provider instructions remain a stable prefix for provider caching;
- batches are sized to prevent one large tool output from forcing context
  compaction;
- batch receipts retain only coverage, evidence, findings, and unresolved
  paths;
- a manifest path by itself never counts as coverage;
- repeated source references reuse the same indexed artifact;
- transport probes use a cheap route, while formal gates retain the
  owner-authorized full-quality route; and
- no risk score, byte threshold, early positive summary, or low-severity label
  permits a source file to be skipped.

## Distribution and developer guidance

The English and Korean READMEs state:

> Run TRIAD from the same authenticated login terminal and project worktree
> used for development. Select provider permissions in that environment before
> dispatch. TRIAD inherits those permissions and does not install or inject a
> separate permission mode.

Prepared review directories stay under that canonical project worktree so
provider project/trust settings have the same scope. If a provider still
requires a native workspace-trust decision, the owner makes it in that
environment before dispatch; TRIAD neither skips nor synthesizes trust.

Bootstrap stops installing permission profiles, sandbox-specific wrapper
rules, read-only Custom Agents, or migration fragments that make TRIAD a
permission controller. Upgrade cleanup removes only exact plugin-owned
artifacts whose marker and expected content identify them. It preserves
owner-authored settings, rules, permission profiles, credentials, and unrelated
files. The same exact cleanup runs on install and remove through the retained
remove-only repair routes; no inspection/preflight policy surface is added.
Exact 0.2.531 managed profile and shell-entry bytes are removed, foreign or
edited legacy artifacts are preserved and reported, and unsafe non-regular or
linked targets are refused without following or mutation. Legacy cleanup tests
use frozen prior-version fixtures rather than retained production generators.
Provider launchers keep the install-resolved classifier path. The retired
apply launcher is replaced by a bootstrap-printed, shlex-safe owner argv that
invokes `bin/apply_patch.py` with required explicit
`--classifier-file <same-absolute-path>` through the trusted login-shell
Python boundary. The owner apply path never recomputes a classifier default
from a fresh shell, and public guidance no longer claims an installed apply
launcher.
The shipped plugin prompt selects `batched-full-coverage` for the operational
pre-merge gate and reserves `formal-gate` for the unbatched compatibility
formal-plan route; the prompt cannot describe the compatibility profile as the
0.2.532 coverage-admissible gate.

The security guide describes the remaining authorization, data, executable,
digest, mutation, and result-custody boundaries without claiming provider or OS
sandbox enforcement.

## Compatibility

Removing the wrapper `--sandbox` interface is an intentional breaking change.
The release notes map old invocations to native-mode invocations and explain
that permission selection now belongs to the provider's user/project settings.

Narrowing ordinary Gemini fallback is also an intentional breaking change.
A missing or invalid `TRIAD_AGY_BIN` and a missing `agy` on `PATH` remain
early route-setup failures but no longer authorize fallback. They are surfaced
directly so the owner can install/configure AGY or explicitly authorize a
separate Google route. Only the no-final-summary `EXIT_BINARY_MISSING` plus
wrapper-owned pre-submission `PtyStartError(stage="exec", errno in the
supported missing/unstartable set)` proof remains fallback-eligible. The
release notes and migration guidance name this removed ordinary-path behavior.

Legacy sealed-packet arguments remain available only to their existing explicit
compatibility callers. They do not become an active worktree-review
prerequisite and are not described as a permission boundary. The existing
`FormalReview` model remains normative only for those legacy sealed-packet
callers. `BatchReceipt` is normative only for the new batched full-coverage
route; the two schemas are not interchangeable or competing admission paths.
The existing four-labeled-element semantic `formal-gate` result remains an
unbatched compatibility profile and is not machine-admissible as a batched
coverage receipt. The operational `0.2.532` full-coverage workflow selects the
separately named batched profile.

## Error handling

The round stops or becomes invalid on:

- missing or ambiguous named change-evidence fields;
- an unavailable exact test-source or approved-data boundary;
- an incomplete or uncertain impact closure;
- native provider permission denial;
- unavailable required family;
- missing batch receipt;
- affected-path or impact-edge coverage gaps;
- candidate base, diff, fingerprint, or untracked-state mismatch;
- source or evidence digest mismatch;
- review-root or canonical-worktree mutation;
- provider route or result-profile mismatch; or
- semantically incomplete findings or verdicts.

The observed native AGY headless permission denial, authentication failure,
capacity failure, extraction failure, and review finding remain distinct
terminal classifications. A required leg denied by native permissions is
invalid. Because `permission-unavailable` is a post-dispatch failure, it cannot
trigger Gemini fallback in the same round. A separately authorized Google
fallback remains eligible only when the wrapper exits without a final summary
using `EXIT_BINARY_MISSING` and emits its exact pre-submission
`PtyStartError(stage=exec, errno in the supported missing/unstartable set)`
diagnostic. Any emitted final summary is post-dispatch and
fallback-ineligible. For a formal round, that same proof permits Gemini only
when the owner separately authorizes the exact Gemini route, provider, data
boundary, and objective for the new round. The immutable prepared directory,
prompt-controlled no-edit contract, digest/mutation invalidation, and strict
result admission remain mandatory; retired read-only-policy denial evidence is
not replaced by a new enforcement probe. Native owner/project permissions
govern both routes, not a TRIAD-installed read-only policy.

## Verification strategy

Implementation follows test-driven development.

### Permission RED/GREEN tests

- RED: current AGY version routing inserts
  `--dangerously-skip-permissions`.
- GREEN: no wrapper argv contains a sandbox, permission-mode, yolo, bypass,
  auto-edit, or dont-ask override.
- RED: current bootstrap and migration artifacts install or document a
  plugin-owned sandbox policy.
- GREEN: install and cleanup preserve owner settings while eliminating exact
  plugin-owned permission-controller artifacts.
- GREEN: the observed native AGY headless denial returns the new terminal
  classification without a broader retry; `_common.py` documents
  `permission-unavailable` as its classification source.
- GREEN: fresh Codex behavior proof observes parent-mode inheritance.

### Evidence RED/GREEN tests

- GREEN prerequisite: the tracked `.gitignore` and eight exact nonexistent-path
  `git check-ignore --no-index` probes prove all planned review artifacts are
  ignored before implementation begins.
- RED/GREEN: real subprocess calls to the absolute evidence CLI prove both
  `prepare` and `validate`, cwd independence, deterministic success JSON and
  exit behavior, canonical evidence-child enforcement, and failure before a
  successful artifact exists.
- RED: a visual-only group summary permits divergent group-count
  interpretation.
- RED: a caller-supplied diff that omits one real changed source from the
  canonical base-to-worktree diff is rejected before evidence completion.
- GREEN: hostile user `diff.noprefix`, mnemonic-prefix, source-prefix, and
  destination-prefix configuration cannot change canonical `a/` and `b/`
  diff headers or patch IDs.
- RED: a symbolic/unknown base, nonignored untracked entry, nonignored review
  root, or post-prepare candidate mutation invalidates preparation or
  admission.
- RED: a changed prepared source with a stale outside-hunk byte and an
  affected-unchanged prepared source copied from stale bytes are both rejected
  against the canonical candidate worktree.
- RED/GREEN: the receipt schema CLI emits one canonical model-derived
  contract; a symlinked, malformed, noncanonical, stale, or substituted
  contract fails preparation or admission, while the accepted bytes are
  digest- and manifest-bound.
- GREEN: named fields are required and validated.
- GREEN: 1,200 synthetic patch shards and a roughly ten-megabyte diff produce
  deterministic indexes, batches, and manifests.
- GREEN: every batch manifest has the exact normative header, one UTF-8
  path-byte-sorted row per assigned source, sorted comma-separated canonical
  ID lists or `-`, and no duplicate or cross-batch path.
- RED: invalid UTF-8 in a changed or affected-unchanged current source fails
  with `non-UTF-8 source` before a completed manifest exists.
- RED: every unsupported non-LF source line separator fails with
  `unsupported source line separator` before a completed manifest exists.
- GREEN: paths containing spaces, quotes, backticks, and literal `$()` remain
  data and execute nothing; newline and tab pathnames fail closed.
- GREEN: every changed and affected path appears once in the closure and in
  every family coverage set.
- RED: a missing diff row, a missing changed closure row, or deletion/rename
  evidence mismatch is rejected.
- RED: a deleted closure row whose current path still exists, or whose
  canonical diff section is not a deletion, is rejected.
- RED: malformed, count-mismatched, out-of-range, or current-source-mismatched
  unified-text hunks are rejected before their ranges can enable the
  full-file-hunk observation exception.
- GREEN: added/deleted file headers and zero-count insertion/deletion headers
  use valid empty-boundary semantics without requiring a zero start for every
  zero count.
- GREEN: a standard optional section/function heading after the closing `@@`
  is accepted and preserved as opaque patch text without changing range/body
  validation.
- RED: an external, alternate, or symlinked evidence directory is rejected by
  preparation, validation, and admission.
- RED: omitted changed-hunk IDs and omitted resolved impact-edge IDs are
  rejected; extra, duplicated, and forged IDs are rejected for every
  disposition.
- GREEN: an unresolved affected path may omit only its expected unverified
  edge, but its unresolved disposition and path still make admission false.
- GREEN: an echoed path without a valid source observation, exact full-file range,
  and hunk/edge evidence is rejected as uncovered.
- RED: an all-whitespace observation from a source containing non-whitespace
  content is rejected; only a validator-proven whitespace-only source uses the
  empty/content-free exception.
- RED: a partial-file changed path whose observation is derived from a visible
  hunk is rejected when a non-whitespace outside-hunk line exists; when every
  outside-hunk line is empty or whitespace-only, the patch-derived observation
  exception is admitted.
- GREEN: a validator-proven zero-byte current source uses no line range or
  observation, while a non-empty whitespace-only source still carries its
  complete line range and remains exempt from the outside-hunk observation.
- GREEN: terminated, unterminated, newline-only, and zero-byte UTF-8 sources
  share the exact `len(text.splitlines())` line-count convention.
- RED: `finding`, `no-finding`, and `unresolved` dispositions that contradict
  receipt-local path-mapped findings or unresolved paths are rejected; a
  finding that maps only to another batch is also rejected.
- GREEN: raw and single-outer-fenced JSON receipts share strict schema
  validation, triple backticks inside JSON string values remain data, and
  prose-wrapped or multiple-top-level-fence responses remain invalid; receipt
  digests always use the original bytes.
- RED: conflicting duplicate JSON members at the receipt top level or inside
  path evidence or findings are rejected before Pydantic admission without
  replacing the original-byte custody digest.
- GREEN: a missing path, missing batch, digest mismatch, or newly discovered
  affected path invalidates the round.
- RED: otherwise complete receipt matrices with a `NOT-SAFE` verdict,
  Critical/Major finding, or open question do not admit and emit no gate
  artifact.
- RED: a forged or stale per-path receipt digest, including a non-empty digest
  for a deleted row, is rejected against the validated closure digest.
- GREEN: an oversized source receives one complete single-path batch.
- RED: malformed, out-of-closure, out-of-range, and digest-mismatched finding
  locations are rejected.
- GREEN: the receipt-tree CLI is the only path that emits an admitted result.
- GREEN: admission output reparses through the exact recursive wire schema and
  reserializes byte-for-byte as compact sorted-key UTF-8 plus one LF; valid but
  noncanonical, nested-extra, missing, and duplicate-member existing files are
  preserved as foreign.
- GREEN: the emitted admission artifact carries the exact revalidated
  CandidateState plus source/change digests; tampering any binding or omitting
  any `path_evidence` entry fails closed.
- GREEN: cheap native transport spikes prove Claude, Google, and fresh Codex
  can return the same exact source observation without candidate execution or
  mutation; provider-specific read mechanics do not change the common task.
  The completed proof is recorded in
  `docs/status/2026-07-30-native-source-observation-spike.md`.

### Quality gates

- a mandatory fresh Claude, Google-family, and Codex formal plan review before
  implementation begins, over one immutable directory containing the approved
  design, executable plan, every current production/configuration/documentation
  file named by that plan, and all repository test source;
- focused wrapper, distribution, bootstrap, skill, and evidence tests;
- the complete test suite through the workspace login-shell Python boundary;
- skill and prompt lint on every changed skill and authored prompt;
- hostile-input behavior probes;
- a mandatory fresh Claude, Google-family, and Codex pre-merge full-coverage
  review over one immutable candidate directory;
- source/cache hash comparison after installation; and
- an owner-authorized disposable fresh-child probe that records the active
  parent permission mode and the observed inherited child capability; and
- fresh `codex exec --ephemeral` proof that the installed skill catalog exposes
  the new contract.

Both formal rounds use the exact test-source boundary `no test-source
exclusions; all repository test source is included`. All three legs must be
valid and `SAFE`, and a changed reviewed byte invalidates the round. The leader
reproduces every finding and classifies it before any edit:

- a defect or underspecification inside this approved design permits only the
  smallest bounded correction; or
- a design change, generalized abstraction, new validator/protocol/runtime
  capability, speculative edge-case handler, or unrelated cleanup stops for
  owner approval.

A reviewer finding never authorizes the second category. This classification,
plus the non-goals below, is the overimplementation breaker for both rounds and
for every task review between them.

Intermediate GREEN gates respect file ownership and sequencing. Permission
controller retirement and skill-contract tasks run focused tests over only the
production files they own. Tests whose assertions span README, SECURITY,
CHANGELOG, or current status documents are rewritten only in the public
documentation task after those bytes change, followed by the complete
distribution suite. The unchanged formal-routing verification ledger remains
included as historical review input because shared-directory and R14
preservation tests read it; no earlier task edits public/status bytes merely to
force a premature full-suite pass.

## Release boundary

The intended package version is `0.2.532`.

A local commit, remote push, tag, release publication, plugin reinstall, or
fresh-session success claim occurs only after its corresponding verification
gate passes. A native AGY permission denial keeps the three-family formal gate
incomplete; the release does not silently fall back to the old dangerous
bypass.

Local workspace autonomy and implementation/install approval do not authorize
external publication. Before push or PR creation, the leader requires explicit
owner authorization for the exact repository and branch and read-only verifies
the `origin` URL, GitHub repository identity, and current branch. Merge, tag,
and release publication require their own explicit authorization after checks
pass. A missing authorization stops with a verified local candidate rather
than mutating remote state.

The release-candidate commit freezes every tracked byte before the complete
local suite, hostile proof, pre-merge batched full-coverage review, machine
admission, and install proof. Those post-commit facts are recorded below ignored
`_runs/releases/0.2.532/`, including the generated PR body, rather than being
appended to tracked release notes or current-state documents. Any tracked edit
after the freeze creates a new candidate commit and requires the complete
verification and three-family admission again. Merge/tag/release URLs remain
external handoff evidence unless a later documentation-only change receives
its own review.

## Non-goals

- Implement a universal cross-language static impact analyzer.
- Certify that an unrestricted provider runtime is safe.
- Modify owner-authored provider permission settings.
- Copy credentials or authentication state into another environment.
- Reduce formal review to risk sampling.
- Divide affected production source between model families.
- Treat tests, builds, or provider verdicts as substitutes for leader
  adjudication.
- Remove legacy packet validation without evidence that its explicit
  compatibility callers are retired.
