# Review Workspace Lifecycle Design

Date: 2026-08-08

Status: owner-approved design, including the 2026-08-09 JSON IPC amendment; implementation and
release state remain pending

## Goal

Prevent concurrent review rounds from overwriting one another, prevent abandoned review artifacts
from growing forever, and keep actual UTF-8 packet strings intact across process boundaries without
adding a daemon, registry, database, heartbeat, closure ceiling, permission profile, or
provider-tool monitor.

## Chosen approach

Extend `bin/review_round.py` with three small lifecycle commands:

- `prepare` allocates one system-temporary root named `triad-review-<review-id>`, creates the fixed
  review subdirectories, and byte-copies only the regular files named by an exact allow-list.
- `manifest` hashes the completed current packet and writes its manifest without parsing
  platform-specific hashing-tool output.
- `cleanup` removes only the system-temporary root derived from the same validated review ID.

The existing `capture`, `render`, and `verify` commands remain the digest, prompt, and integrity
authority. Lifecycle state is a `.last_activity` marker outside the prepared `shared/` directory,
so refreshing it after successful round operations never changes the reviewed digest.

## Alternatives rejected

### Leader-created ad hoc directories

This keeps code small but repeats the current failure mode: name collisions, stale copies, and
wrong diff or source bases depend on transient leader memory.

### Persistent registry or background cleaner

A registry, daemon, launch agent, heartbeat, or database could model active owners precisely, but
it creates more state and more failure modes than the local CLI workflow needs.

### Directory-wide lifecycle lock

Locking the system temporary directory could coordinate stale reclamation with same-ID recreation,
but the approved workflow never reuses a review ID. A fresh unique ID plus exclusive review-root
creation is sufficient, so `flock`, lock files, and broader coordination are intentionally omitted.

### Automatic context-managed deletion only

Deleting only on normal process exit cannot cover user interruption, process termination, or
automatic conversation compaction. A next-run stale sweep is the minimal recovery mechanism.

### Raw-byte or Base64 path protocol

The supported workflow exchanges UTF-8 strings. A byte-oriented filename protocol, Base64 layer,
protocol registry, or compatibility shim would add machinery for inputs outside that approved
domain. Deterministic JSON string escaping is sufficient for the actual values and preserves quote,
backslash, LF, CR, tab, other UTF-8 control characters, and U+2028 without record ambiguity.

## Interfaces

### `prepare`

```text
review_round.py prepare \
  --review-id <validated-id> \
  --source-root <canonical-absolute-directory> \
  --member-list <canonical-absolute-UTF-8-file> \
  --required-members-json <canonical-JSON-array>
```

The member list is a UTF-8 JSON array of non-empty strings without a BOM, sorted by decoded path.
The required-members argument appears exactly once and is a non-empty sorted JSON array of unique
paths. Every required path must occur in the member list; repeated arguments, duplicate paths, or a
missing member cause `prepare` to fail before creating the review root.
Each decoded string is one normalized POSIX relative regular-file path. Unsorted or duplicate paths,
NUL, non-UTF-8 values, absolute paths, `.` or `..` components, `.git` components, symlinked source
components, directories, devices, sockets, and missing entries fail closed. JSON string escapes
carry quote, backslash, LF, CR, tab, other UTF-8 control characters, and U+2028 without treating them
as record boundaries. No comments, glob syntax, Base64, raw non-UTF-8 filename bytes, or legacy
line-list compatibility are supported.

The supported domain is strings obtained through strict UTF-8 decoding. Escaped unpaired surrogate
code points are not members of that domain and cannot be produced by the exclusive supported
serializer from approved inputs. The workflow does not add surrogate scanning, raw-byte/Base64
fallback, or a second hand-written-input protocol. Manually injecting such a representation is
outside the input contract: no behavior, graceful-error classification, or regression test is
specified for it.

Every lifecycle operation uses the one canonical base
`Path(tempfile.gettempdir()).resolve(strict=True)`. The `triad-review-` direct-child namespace under
that base is reserved for this tool; manual packets and durable handoffs never use it. Before
allocation, `prepare` inspects only direct children with that exact prefix. A non-symlink directory
owned by the current UID with a valid, at-most-200-character review ID is sweep-eligible. It uses a
regular non-symlink `.last_activity` mtime when present and the root mtime when that marker is absent
or is successfully inspected as a symlink or unsupported type. If marker inspection itself fails
with an error other than absence, the root is skipped and reported. Other prefixed children are
skipped and reported without a deletion attempt. An eligible child
is deleted only when the selected time is strictly older than 30 days. `prepare` then creates
`triad-review-<review-id>` with
`exist_ok=False`, so two processes using the same ID cannot share or overwrite a directory.
Different IDs remain independent even when their source root and current working directory are
identical.

The command creates:

```text
triad-review-<review-id>/
  .last_activity
  member-list.txt
  shared/
    source/product/
  prompts/
  results/
```

`member-list.txt` is the normalized exact source list serialized as deterministic compact JSON and stays
outside the prepared `shared/` directory but inside the review root. Immediately after exclusive
root creation, `prepare` creates the fixed layout and writes the normalized member list. It creates
`.last_activity` only after every exact source copy succeeds. A process killed during copying leaves
a partial root without that marker, so the reserved-namespace sweep uses the root mtime after 30
days. The file provides per-round IPC for deterministic enumeration and is deleted with the root.
`prepare` prints one deterministic compact JSON object containing the review ID, canonical root paths, copied
member count, and stale roots removed or skipped. The active implementation plan or `TASK.md`
records the ID and paths; capture later supplies the reviewed digest. There is no global pointer or
registry.

All `bin/review_round.py`-owned JSON in this workflow uses UTF-8,
`json.dumps(..., ensure_ascii=True, sort_keys=True, separators=(",", ":"))`, and one final LF when
written as a file or CLI record. This covers the member list, manifest, prepare/cleanup results,
capture snapshot, and rendered metadata; it does not change wrapper or benchmark output formats.
`ensure_ascii=True` makes every non-ASCII code point and JSON-significant control character explicit
on the wire; JSON decoding recovers the original UTF-8 string before existing path validation runs.
This local deterministic encoding is the canonical JSON form for this workflow; it does not claim an
additional general-purpose canonicalization standard.

Provider wrapper calls for the round set the existing `TRIAD_DISPATCH_LOG_DIR` to
the canonical `<review-root>/results/_logs` and do not pass `--debug`. Their audit and failure-run
logs therefore share the round lifecycle instead of growing repository-local `bin/_logs` state. A
bounded `_common.py` correction disables its external system-temp run-log fallback only when an
explicit log root is configured; a configured-root storage failure is reported as unavailable.
Unconfigured wrapper behavior stays unchanged. This is routing of generated evidence, not a
provider tool, permission, or MCP restriction.

### `manifest`

```text
review_round.py manifest \
  --prepared-dir <returned-shared-directory>
```

The command requires the exact `shared/` child of a managed current review root and requires
`SOURCE_SHA256SUMS` to be absent. This absence precondition is evaluated before packet-inventory
verification so a second invocation deterministically reports the exclusive-create error without
rewriting existing bytes. Before writing, it decodes the stored member list and verifies that
the packet inventory is exactly every `source/product/<member>`, `TASK.md`, `REVIEW.diff`, and
optional `EVIDENCE.md`; a wrong packet is rejected rather than merely hashed. It enumerates every
other regular file directly, retains the existing symlink and unsupported-entry rejection, hashes
file bytes with Python's SHA-256, sorts by the decoded relative POSIX path, and creates
`SOURCE_SHA256SUMS` exclusively. Only the root-relative manifest path is excluded, so an allowlisted
`source/product/SOURCE_SHA256SUMS` or nested file with that basename remains a normal manifested
source member. The file is a
deterministic JSON array of objects with exactly `path` and `sha256` string keys. It never parses
`shasum`, `sha256sum`, `tar`, shell escaping, or newline-delimited filenames. Capture and verify
decode the same JSON shape, require exact sorted inventory with no duplicates, and recompute every
digest. `manifest` prints one deterministic compact JSON result with the canonical manifest path and
file count, then refreshes lifecycle activity under the existing best-effort rule. There is no
legacy line-manifest compatibility path.

`manifest` is the exclusive supported producer, and its dictionary serializer cannot emit repeated
lexical object member names. Validation therefore uses standard JSON decoding followed by an exact
decoded key-set check; it does not add an object-pair scanner for hand-written duplicate keys. Manual
packet rewriting is already outside the workflow and invalidates the round.

### Rendered review metadata

`render` keeps the fixed inspection and result instructions as prose. It serializes every dynamic
value—review ID, kind, family, objective, prepared directory, content digest, criteria, and approved
boundary—inside one deterministic compact JSON object on the single line introduced by the literal
fixed prefix `Review metadata: `. JSON escaping
therefore prevents a quote, backslash, newline, carriage return, tab, control character, or U+2028
inside a value from changing prompt framing. The existing CLI arguments and `LegVerdict` schema stay
unchanged; no second brief-file protocol is added. The fixed result instruction binds the returned
`review_id`, `family`, and `content_digest` to the same-named values in that metadata object instead
of interpolating any value a second time. Separate fixed inspection prose directs the reviewer to
perform `metadata.objective` for `metadata.review_kind` and `metadata.family`, inspect
`metadata.prepared_directory`, and evaluate every `metadata.criteria` item across
`metadata.approved_boundary`; it does not interpolate those values again.

### `cleanup`

```text
review_round.py cleanup \
  --review-id <validated-id> \
  --expected-root <root-returned-by-prepare>
```

The command derives the exact root from the canonical system temp base and the validated ID,
then requires byte-for-byte path equality with `--expected-root` before inspecting or deleting
anything. This parameter is a mismatch guard, not an arbitrary deletion target. A changed temp base
therefore fails loudly instead of treating the real root as absent. The command prints compact JSON
with the review ID, derived root, and `removed` boolean. A missing matched root is an idempotent
`removed: false`; normal leader cleanup requires the first result to be `removed: true`. A root
symlink, unexpected file type, path mismatch, permission failure, or deletion error fails without
retrying a broader or stronger operation. The exact recorded root may be incomplete, but it must
still be a current-UID non-symlink directory with the exact ID-derived name. Successful deletion is
permanent.

## Activity and stale cleanup

`prepare` creates `.last_activity` only after every exact source copy succeeds. Successful CLI
`manifest`, `capture`, `render`, and `verify` operations make a best-effort refresh after their action
and output succeed when the prepared directory is the exact `shared/` child of a valid ID-derived
lifecycle root. Refresh opens only an existing regular, non-symlink marker with write intent through
`O_WRONLY | O_NOFOLLOW`, then updates that opened descriptor. If the
marker is missing or successfully inspected as unsafe, the operation does not follow or recreate it
and instead makes one best-effort refresh of the exact managed root mtime without following links.
If an existing regular marker cannot be updated, or marker inspection itself fails, no second
fallback is attempted. Any activity-
refresh failure preserves the completed operation's output and exit status. The managed
root itself, or a path under it but outside
its exact `shared/` child, is a lifecycle error rather than a non-lifecycle directory. Failed
operations and directories outside managed lifecycle roots do not create or touch a marker. The
skill routes snapshots, prompts, results, and wrapper logs under
the review root so normal cleanup removes them together; the CLI does not add a separate output-path
policy.

Exactly 30 days is the owner-approved age floor. Cleanup runs only at the start of a later `prepare`;
there is no periodic process. On macOS the standard temp root is normally per-user; on Linux it may
be a shared sticky `/tmp`. Canonical-base, current-UID, valid-ID, and non-symlink-root checks prevent
a foreign prefix match from becoming a deletion candidate on either platform. CLI tests set
`TMPDIR` to an isolated canonical test directory so they never sweep the developer's real temp
base.

## Copy and containment behavior

`prepare` copies file bytes, not Git history or metadata. It never copies `.git`, follows no source
symlink, and normalizes destination files through a newly allocated root. Each validated source
component is reopened relative to a verified directory descriptor with `O_NOFOLLOW`; device/inode
identity is compared before copying, and file size/mtime are checked before and after the descriptor
read. A concurrent pathname replacement therefore fails and removes the partial review root instead
of redirecting copied bytes. `shared/`, `prompts/`, and `results/` remain separated as required by
the review contract. Snapshots, leg verdicts, and wrapper logs are written under `results/`;
rendered prompts are written under `prompts/`.

The prepared packet contains only the current candidate closure and artifacts created for the
current round. Never copy an earlier round's `TASK.md`, diff, manifest, snapshot, prompts, status,
or verdicts into a later prepared directory. Historical round records remain leader evidence
outside the prepared `shared/` directory and are not reviewer input. Each decoded source member `m` maps
exactly to `shared/source/product/<m>`. The only current-round files outside that source tree are
`TASK.md`, `REVIEW.diff`, `SOURCE_SHA256SUMS`, and optional `EVIDENCE.md`. Capture and verification
verify that mapping and that the JSON manifest names every other regular file exactly once. The tracked benchmark
fixtures are allow-list source members, not prior-round evidence. This slice does not invent a diff
algorithm, closure ceiling, or evidence registry.

## Durable handoff rule

If the owner asks for a durable handoff, the leader prepares it directly at the explicitly approved
durable destination. A temporary lifecycle root is never promoted or exempted from cleanup.

## Normal and interrupted flows

Normal flow:

1. The leader chooses and records a fresh review ID.
2. `prepare` sweeps stale roots, allocates the exact root, and copies the allow-list.
3. The leader adds only current-round artifacts, runs `manifest` to generate and verify the final
   JSON `SOURCE_SHA256SUMS`, enumerates the packet, captures to `results/snapshot.json`, renders under
   `prompts/`, routes wrapper logs and verdicts under `results/`, dispatches, verifies, and
   adjudicates.
4. After all required evidence is consumed, `cleanup` compares the recorded expected root, returns
   `removed: true`, and removes the exact root.

Interrupted flow:

1. The process may stop with the root intact.
2. No background component acts on it.
3. A later `prepare` deletes it only after 30 days without recorded lifecycle activity. The root
   derived from that later call's requested ID is excluded from sweeping and must collide instead.

## Error handling

- Same review ID still present after the bounded sweep: fail; never reuse or overwrite.
- Invalid or escaping member: fail before copying that member.
- Malformed member-list JSON, manifest JSON, wrong JSON value type, duplicate decoded path, or
  non-UTF-8 string: fail without falling back to line parsing.
- Partial `prepare` failure: remove only the root allocated by that invocation; propagate failure.
- Ineligible prefixed root: skip and report it without attempting deletion.
- A lifecycle-shaped `triad-review-<id>/shared` directory outside the current canonical system-temp
  base: fail instead of silently treating it as an unmanaged packet.
- A valid direct managed `triad-review-<id>` root itself, or a prepared path under it: fail capture,
  render, and verify unless the prepared path is that root's exact `shared/` child.
- Eligible stale-root deletion failure: stop the new prepare and report the exact root; do not
  ignore, retry more strongly, or widen cleanup.
- Eligible target absent before deletion, or absent after a top-level race: report it as already
  removed. Test absence with `lstat`; a remaining dangling symlink is not absence. If any deletion
  error returns while an entry remains, stop. Never blanket-swallow `OSError` from the sweep.
- Expected cleanup root mismatch: fail before inspecting or deleting either path.
- Normal cleanup failure: leave the remaining root and report it for owner action.
- A post-success best-effort activity-marker refresh failure is the explicit exception: preserve
  the completed action, output, and exit status without following or creating another path.
- Lifecycle filesystem failures are wrapped as `RoundIntegrityError`, so the CLI returns 2 without
  a traceback. The 200-character ID bound keeps the prefixed leaf within common `NAME_MAX`.

## Verification

Tests cover:

- byte-exact allow-list copy and fixed directory layout;
- same-ID collision and different-ID isolation from one working directory;
- traversal, `.git`, missing entry, symlink, and unsupported-entry rejection;
- complete-root marker timing; absent, symlink, and unsupported-marker root-mtime fallback;
  UID/ID/root-type gating; and older-than-30-day next-run sweep;
- idempotent exact cleanup, expected-root mismatch detection, and non-traversal of an internal
  symlink target, including foreign-UID cleanup rejection;
- activity touches for exact lifecycle roots without touching non-lifecycle or failed-command
  paths; tests reset root mtime after marker mutation, prove a regular-marker refresh leaves root
  mtime unchanged, prove unsafe/missing-marker fallback advances root mtime, and prove a regular-
  marker update failure preserves success with both marker and root mtimes unchanged; a refresh-side
  marker-inspection error attempts no fallback, while a sweep-side inspection error is skipped and
  reported; managed roots themselves and non-`shared/` descendants are rejected by
  capture, render, and verify;
- per-round JSON member-list, exact source mapping, fixed current artifacts, JSON manifest coverage,
  snapshot/verdict/log placement, and cleanup;
- manifest rejection before write for a non-managed target or wrong packet inventory, plus inclusion
  of allowlisted root and nested source members whose basename is `SOURCE_SHA256SUMS`;
- round-trip and raw-wire assertions for quote, backslash, LF, CR, tab, a control character, and
  U+2028 in actual UTF-8 member paths and rendered metadata;
- unchanged digest and non-lifecycle capture/render/verify behavior, plus explicitly configured
  log-root failure behavior;
- macOS execution evidence plus Linux behavior supported analytically by Python 3.12 standard-library
  API selection and the canonical-base, UID, valid-ID, and non-symlink-root gates above.

## Explicit non-goals

- No daemon, launch agent, cron job, database, registry, or heartbeat.
- No process monitoring, MCP monitoring, permission override, safe mode, or tool suppression.
- No source archive, Git repository copy, closure limit, automatic decision splitting, or provider
  execution change.
- No Base64/raw-byte filename layer, protocol registry/version negotiation, or compatibility parser
  for the superseded newline member-list and manifest formats.
- Commit, push, and local installation occur only after the amended plan gate, implementation
  verification, fresh pre-merge gate, and regenerated distribution proof. No tag, publish, or
  release action is included.
