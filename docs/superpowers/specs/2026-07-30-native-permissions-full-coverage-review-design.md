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

The canonical-worktree fingerprint is an operational leader record, not a
skill API or reviewer command. It SHA-256 hashes length-prefixed, tagged byte
records in this order: current `HEAD`; full
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
than excluding evidence from the immutable shared root.

`CHANGESET.md` contains named machine-readable headers followed by a compact
human summary:

```text
FORMAT_VERSION=1
GROUP_COUNT=<integer>
PATCH_FILE_COUNT=<integer>
AFFECTED_SOURCE_COUNT=<integer>
BATCH_COUNT=<integer>
SOURCE_TREE_DIGEST=<sha256>
CHANGE_EVIDENCE_DIGEST=<sha256>
```

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
- `error-path`; or
- `owner-approved-project-edge`.

The vocabulary records why a path is present. It does not attempt to implement
a universal static analyzer.

Each batch manifest lists the affected source paths, their complete canonical
`patch_id` set where applicable, content digests, byte counts, and line counts.
An oversized source receives one single-path batch and remains a complete file;
there is no source-shard or symbol-boundary protocol. Provider file-read ranges
may bound individual tool outputs, but all ranges remain required. Batching
never samples lines or omits low-risk files.

## Impact-closure preparation

The leader performs these bounded preparation actions:

1. Capture the canonical status and diff once.
2. Add every changed file and hunk as a seed.
3. Trace the seed through affected unchanged production code using the
   project's instructions, language-aware read-only tools, source search,
   build metadata, schemas, registrations, and runtime configuration.
4. Record each reached path and edge in `IMPACT_CLOSURE.tsv`.
5. Expand uncertain dynamic edges conservatively to the containing module or
   production root.
6. Stop with an open question when reflection, generated registration,
   runtime discovery, or a missing project boundary prevents a defensible
   closure.
7. Partition the complete closure deterministically by size and semantic
   boundaries.
8. Record the source-tree and change-evidence digests before dispatch.

`prepare_review_evidence` and `validate_review_evidence` fail when a parsed
diff target lacks a `reason=changed` closure row or when a changed closure row
lacks a diff section. They also reject NUL, LF, CR, and TAB in `path` and
`reached_from` before TSV emission. Git-quoted diff fields are decoded only far
enough to detect and reject those controls; no reversible generic field codec
is introduced. Spaces, quotes, backticks, and literal `$()` remain inert data
and execute nothing. This intentional `0.2.532` input limit never silently
omits a path or admits partial coverage.

The implementation supplies deterministic inventory, manifest, digest, and
batching utilities. It does not claim language-independent impact discovery.
The leader remains responsible for project-specific caller and consumer
tracing.

## Full-coverage review matrix

Every family receives the same review root, objective, complete batch list, and
evidence digests.

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
path_evidence
findings
affected_surfaces_inspected
unresolved_paths
open_questions
verdict
```

`path_evidence` is not a list of manifest paths. Every affected source path has
one compact record. A current non-empty source record contains its content
digest, the exact full-file line range `1..line_count`, one bounded exact
source observation and its line number, optional symbol annotations, every
changed hunk or recorded impact edge relevant to that path, and the reviewer's
disposition.
`source_observation` is a 1-160 character exact substring of the UTF-8 logical
line named by `observation_line`; when that line has at least eight characters,
the observation has at least eight. It is never written into
reviewer-visible manifests. A non-empty whitespace-only source retains its
full line range but uses empty observation text only when validation proves it
has no non-whitespace character. A zero-byte current source uses
`observation_line=None`, empty observation text, and
`line_start=line_end=None`. Deleted paths retain patch evidence but require no
current-source observation or line range.

For a changed current source with at least one current line outside all
validated new-side hunk ranges, `observation_line` must name one of those
outside-hunk lines. If the canonical patch hunks cover every current line, the
patch artifact already contains the complete current source and a
patch-derivable observation is allowed. This exception is explicit evidence
that the whole source was present in the patch, not a claim that patch-only
inspection generally proves full-file review. A receipt built only by echoing
manifest and index fields is otherwise uncovered.

`PathEvidence` retains per-path `changed_hunks` and
`verified_impact_edges`; there is no redundant top-level
`verified_impact_edges` promise. Each receipt's `changed_hunks` set must
exactly equal the canonical `patch_id` set for its path. Each receipt's
`verified_impact_edges` set must exactly equal the expected `impact_edge_id`
set. Omitted, extra, duplicated, and forged IDs are invalid.
Changed rows must have an empty `verified_impact_edges`; affected-unchanged
rows must have an empty `changed_hunks`. Deleted and renamed rows follow their
canonical patch-ID sets rather than admitting arbitrary IDs.

`disposition` is also source-grounded. It is `unresolved` exactly when the
path appears in `unresolved_paths`; otherwise it is `finding` exactly when at
least one admitted finding location maps to that current path or one of its
canonical patch IDs, and `no-finding` only when neither condition holds. A
contradictory disposition invalidates the receipt.

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
closing line is exactly three backticks, and the inner payload contains no
fence token. Only the extracted inner bytes are passed to strict JSON
validation. Leading or trailing prose, nested or multiple fences, a missing
field, or a family/batch mismatch is invalid. This deterministic outer-fence
step preserves the repository's observed AGY fence tolerance without adding
wrapper repair or changing response custody. Fresh Codex terminal text follows
the same custody rule; this is operational custody, not a new wrapper
responsibility.

The operational admission command consumes the validated evidence directory
and an exact receipt tree of `<family>/<batch-id>.json`, rejects missing and
extra receipt files, and atomically emits the sole machine-admissible
`coverage-admission.json`. A prose summary or manually assembled family result
cannot replace this command.
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
  that a validator-proven zero-byte current source has no line range or
  observation;
- every covered path has the expected content digest;
- every recorded impact edge is either verified or produces an unresolved
  question;
- no family reports a missing batch or unresolved path;
- the three families used the same source-tree and change-evidence digests;
- the review-root digest and canonical-worktree fingerprint remain unchanged;
- the leader independently reproduces material caller, consumer, schema,
  configuration, and build relationships; and
- the existing finding, severity, evidence, and verdict contract passes.

`SAFE` is impossible when findings include Critical or Major, any receipt is
`NOT-SAFE`, or any unresolved path or open question exists. For current source,
optional symbols are annotations only; `line_start` and `line_end` are
mandatory and must equal `1` and `ImpactRow.line_count` for every non-empty
current source. A validator-proven zero-byte current source and a deleted row
require no observation, symbol, or line evidence. Current non-deleted source
must be UTF-8 for exact observation and finding-location validation; invalid
UTF-8 stops evidence preparation rather than reducing coverage.

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
files.

The security guide describes the remaining authorization, data, executable,
digest, mutation, and result-custody boundaries without claiming provider or OS
sandbox enforcement.

## Compatibility

Removing the wrapper `--sandbox` interface is an intentional breaking change.
The release notes map old invocations to native-mode invocations and explain
that permission selection now belongs to the provider's user/project settings.

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
- source or evidence digest mismatch;
- review-root or canonical-worktree mutation;
- provider route or result-profile mismatch; or
- semantically incomplete findings or verdicts.

The observed native AGY headless permission denial, authentication failure,
capacity failure, extraction failure, and review finding remain distinct
terminal classifications. A required leg denied by native permissions is
invalid. Because `permission-unavailable` is a post-dispatch failure, it cannot
trigger Gemini fallback in the same round. A separately authorized Google
fallback remains eligible only for the existing proven pre-dispatch AGY
unavailability route. Native owner/project permissions govern both routes, not
a TRIAD-installed read-only policy.

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

- RED: a visual-only group summary permits divergent group-count
  interpretation.
- GREEN: named fields are required and validated.
- GREEN: 1,200 synthetic patch shards and a roughly ten-megabyte diff produce
  deterministic indexes, batches, and manifests.
- GREEN: paths containing spaces, quotes, backticks, and literal `$()` remain
  data and execute nothing; newline and tab pathnames fail closed.
- GREEN: every changed and affected path appears once in the closure and in
  every family coverage set.
- RED: a missing diff row, a missing changed closure row, or deletion/rename
  evidence mismatch is rejected.
- RED: a deleted closure row whose current path still exists, or whose
  canonical diff section is not a deletion, is rejected.
- RED: an external, alternate, or symlinked evidence directory is rejected by
  preparation, validation, and admission.
- RED: omitted, extra, duplicated, and forged changed-hunk and impact-edge IDs
  are rejected.
- GREEN: an echoed path without a valid source observation, exact full-file range,
  and hunk/edge evidence is rejected as uncovered.
- RED: a partial-file changed path whose observation is derived from a visible
  hunk is rejected; when validated hunks cover every current line, the
  patch-derived observation exception is admitted.
- GREEN: a validator-proven zero-byte current source uses no line range or
  observation, while a non-empty whitespace-only source still carries its
  complete line range.
- GREEN: terminated, unterminated, newline-only, and zero-byte UTF-8 sources
  share the exact `len(text.splitlines())` line-count convention.
- RED: `finding`, `no-finding`, and `unresolved` dispositions that contradict
  path-mapped findings or unresolved paths are rejected.
- GREEN: raw and single-outer-fenced JSON receipts share strict schema
  validation while prose-wrapped and multiple-fence responses remain invalid;
  receipt digests always use the original bytes.
- GREEN: a missing path, missing batch, digest mismatch, or newly discovered
  affected path invalidates the round.
- GREEN: an oversized source receives one complete single-path batch.
- RED: malformed, out-of-closure, out-of-range, and digest-mismatched finding
  locations are rejected.
- GREEN: the receipt-tree CLI is the only path that emits an admitted result.
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

## Release boundary

The intended package version is `0.2.532`.

A local commit, remote push, tag, release publication, plugin reinstall, or
fresh-session success claim occurs only after its corresponding verification
gate passes. A native AGY permission denial keeps the three-family formal gate
incomplete; the release does not silently fall back to the old dangerous
bypass.

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
