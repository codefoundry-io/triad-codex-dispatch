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
native AGY availability constraint.

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

If a non-interactive provider cannot obtain a native permission, the wrapper
returns a distinct permission-unavailable terminal result. It includes the
provider's bounded diagnostic and does not reinterpret the result as
authentication failure, retry it with broader authority, or admit it as a
review verdict.

### Boundaries retained

Permission neutrality does not remove unrelated integrity and data controls.
TRIAD retains:

- explicit authorization before an external provider receives approved data;
- credential, token, authentication-file, environment-dump, provider-log, and
  unrelated-path exclusions;
- argv-array construction, executable-path pinning, prompt-file validation,
  and environment scrubbing;
- one immutable shared review root and its before/after digest;
- canonical-worktree fingerprints;
- the no-edit and no-execution review task contract;
- mutation and digest-mismatch invalidation;
- strict result extraction and semantic admission;
- legacy packet validation where an existing compatibility caller explicitly
  invokes it.

These controls validate data and result custody. They do not choose the
developer's permission mode.

## Change-evidence format

The leader prepares one immutable review root:

```text
review-root/
├── <current approved production source, configuration, and documentation>
└── change-evidence/
    ├── CHANGESET.md
    ├── IMPACT_CLOSURE.tsv
    ├── MANIFEST.sha256
    ├── patches/
    │   └── <group>/<file-or-hunk>.patch
    └── batches/
        └── <batch-id>.tsv
```

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

`IMPACT_CLOSURE.tsv` contains one row per affected production source:

```text
path	reason	reached_from	content_sha256	batch_id
```

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

Each batch manifest lists the affected source paths, their complete patch-shard
set where applicable, content digests, and source byte counts. A large source
file may be split at deterministic symbol boundaries, but all of that file's
source shards remain in the batch set. Batching never samples lines or omits
low-risk files.

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

Each batch receipt contains:

```text
batch_id
source_tree_digest
change_evidence_digest
path_evidence
verified_impact_edges
findings
unresolved_paths
```

`path_evidence` is not a list of manifest paths. Every affected source path has
one compact record containing its content digest, inspected symbol or positive
line range, every changed hunk or recorded impact edge relevant to that path,
and the reviewer's disposition. A path echoed from the manifest without this
source-grounded evidence is uncovered.

The family-level result contains the ordered batch-receipt digests, complete
affected-path coverage, consolidated findings, unresolved questions, and the
normal result-profile fields.

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
- every covered path has non-empty, source-grounded `path_evidence`;
- every covered path has the expected content digest;
- every recorded impact edge is either verified or produces an unresolved
  question;
- no family reports a missing batch or unresolved path;
- the three families used the same source-tree and change-evidence digests;
- the review-root digest and canonical-worktree fingerprint remain unchanged;
- the leader independently reproduces material caller, consumer, schema,
  configuration, and build relationships; and
- the existing finding, severity, evidence, and verdict contract passes.

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
prerequisite and are not described as a permission boundary.

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

Permission denial, authentication failure, capacity failure, extraction
failure, and review finding remain distinct terminal classifications.

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
- GREEN: native permission denial returns the new terminal classification
  without a broader retry.
- GREEN: fresh Codex behavior proof observes parent-mode inheritance.

### Evidence RED/GREEN tests

- RED: a visual-only group summary permits divergent group-count
  interpretation.
- GREEN: named fields are required and validated.
- GREEN: 1,200 synthetic patch shards and a roughly ten-megabyte diff produce
  deterministic indexes, batches, and manifests.
- GREEN: paths containing spaces, quotes, newlines, and `$()` remain data and
  execute nothing.
- GREEN: every changed and affected path appears once in the closure and in
  every family coverage set.
- GREEN: an echoed path without source-grounded symbol/line and hunk/edge
  evidence is rejected as uncovered.
- GREEN: a missing path, missing batch, digest mismatch, or newly discovered
  affected path invalidates the round.
- GREEN: a large source split at symbol boundaries remains fully covered.

### Quality gates

- focused wrapper, distribution, bootstrap, skill, and evidence tests;
- the complete test suite through the workspace login-shell Python boundary;
- skill and prompt lint on every changed skill and authored prompt;
- hostile-input behavior probes;
- fresh Claude, Google-family, and Codex full-coverage review over one
  immutable candidate directory;
- source/cache hash comparison after installation; and
- fresh `codex exec --ephemeral` proof that the installed skill catalog exposes
  the new contract.

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
