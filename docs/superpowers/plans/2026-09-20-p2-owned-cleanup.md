# P2: owned cleanup after verified evidence export

> Required execution skill: superpowers:executing-plans. The root leader writes
> source/tests; separate fresh triad-skill-executor instances perform RED/GREEN.

Start from merged P1 `a9e5b84b53f6b5db841b3b9fe81591dc2d1fd0a7` in the existing
checkout, branch `codex/host-parity-p2-cleanup`. P1 passed complete round
`triad-b-p1-r2` and PR 27. Shared remote main remains `2eb883fee59e66556ee7c7f87189b38231136622`.
No D-B1/D-B2 policy/custody decision is needed for this existing cleanup contract.

Goal: implement existing C4/C5/C7 and R-CLEANUP without deleting foreign or
unexported review material. Preserve current cleanup CLI, prepared/worktree
selection, no-follow source copy, idempotence and eligible 30-day stale sweeping.

The [Python 3.12 rmtree contract](https://docs.python.org/3.12/library/shutil.html#shutil.rmtree)
provides fd-based symlink resistance on supporting platforms and propagates
removal errors; it is not allocation proof or an evidence export protocol.
The [rename contract](https://docs.python.org/3.12/library/os.html#os.rename)
permits replacing an empty destination directory on Unix, so a check followed
by ordinary rename is not an exclusive destination claim.

## Minimal host-local mechanism

- `prepare` exclusively records allocation identity beside its new managed root.
  Bind review ID, canonical root, UID/device/inode and a generated allocation
  identifier. Reject colliding metadata; never adopt a plausible foreign marker.
  A preparation failure may remove only the allocation made by that invocation.
- Add `export --review-id --expected-root --output` to the existing lifecycle
  CLI. Use a new caller-selected canonical absolute output directory, census all
  deletable artifacts without following links, copy regular files using the
  existing guarded source-copy helpers, and retain link kind/text as evidence.
  Keep exported files outside this and every other managed review root/claim.
  Inventory includes empty directories, regular-file hashes and exact link
  text; unsupported special entries preserve/refuse. Verify the copy and manifest
  before writing an exclusive external export
  receipt bound to the allocation and destination. No receipt inside a tree
  that cleanup itself will progressively remove.
- Cleanup requires allocation proof plus a reverified external export. New or
  changed artifacts after export must stop deletion. Partial cleanup permits
  only a same-content subset of the original verified inventory.
- Use one exclusively created private claim sibling directory for bounded resume.
  Its exclusive identity marker binds the allocation and original last-activity
  time; move the root into its reserved child path, so rename cannot overwrite
  an existing foreign sibling. Existing claims require that same proof before
  resume. Recheck the moved inode and inventory against the verified export
  before deletion. If replacement is detected, retain and report both paths;
  never overwrite a replacement to restore the old name. Keep allocation/export
  metadata until deletion completes. Do not
  claim resistance to a malicious same-UID actor rewriting all evidence or
  introduce a secret capability, global registry or custom deletion framework.
- Cleanup begins only after all round writers/providers are terminal; one leader
  cleans an allocation at a time. Rename separates the old namespace and detects
  a pre-rename root replacement; it does not freeze open FDs or make concurrent
  content writers safe. Refuse observed drift rather than promise race immunity.
- Root absent plus a proven claim resumes; root and claim both absent is a no-op
  with only proven metadata residue removed; collisions/identity mismatches are
  preserved. `prepare` refuses a reused ID while any allocation/claim remains.
- Stale sweep calls the same ownership/export/cleanup rules. It reports and
  retains uncertain legacy roots; it does not turn off cleanup for proven,
  exported stale allocations. Preserve strict 30-day behavior and the requested
  review ID collision refusal. Enumerate claim-only allocations too. Use the
  captured pre-claim activity when a partial deletion removed the original
  marker; do not interpret claim-rename mtime as review activity. Proven deletion
  failures still propagate, rather than being swallowed as uncertain legacy.
- Document one recovery: preserve an unproven root and its observed diagnostics;
  manually inspect/retain evidence under owner authority before exact removal.
  Never manufacture a new allocation record to adopt unknown residue.

## Files, budget and meaningful verification

Production: `bin/review_round.py`; provider-free verifier consumes the added
export phase. Reuse existing file identity, canonical serialization, exclusive
write and guarded copy/hash functions, with nonblocking file opens before fstat
to avoid a replaced FIFO blocking the export. Initial estimate 240 additions/45
deletions; measure actual coherent scope instead of adding line-count gates.
Tests and narrative documentation are counted separately.

Fresh dedicated RED first: same-UID foreign root with a plausible marker must
survive explicit cleanup and stale sweep; allocated but unexported root must
survive; changed/late artifacts invalidate export; original root replacement at
claim transition must preserve the foreign tree. Then validate verified-export
cleanup, partial-delete resume, corrupt/missing/linked receipts, export failure,
links without target reads/deletion, eligible stale sweep and repeated no-op.

Update existing tests that explicitly expect deletion without provenance, while
retaining their root/type/UID/symlink/permission/race assertions with real
prepare/export setup. Adapt CLI lifecycle and synthetic verifier to export before
cleanup; retain the actual small synthetic artifact bytes/link records and
manifest in its report before exact fixture cleanup, including failure paths.
Prepare rollback verifies the just-created root identity and remains a private
preparation-only path, never a generic export bypass.
Run fresh Terra/high GREEN, full macOS and Ubuntu 24.04 suites, validator,
provider-free lifecycle and the complete independent multi-family review.

A remains read-only. Record its magic-marker validation at
`.claude/skills/triad-cross-family-review/lib/review_scratch.py:668-705`,
name-only claim reclamation at `720-732`, deletion at `849-864`, and close path
`936-1082` at `92c8afd`. Preserve A's registered-worktree protections; do not port
its unproven `.pruning` deletion to B. Publish no common revision or deployment as
a side effect of this host-local implementation.

## Execution sequence

1. Add `tests/test_review_cleanup_custody.py` against the existing functions.
   Fresh RED must reproduce cleanup/sweep deleting same-UID unproven roots and
   allocated but unexported evidence. The test owns its private temp base.
2. Implement allocation records, `export_review_workspace(...)`, and
   `export --review-id --expected-root --output` in the existing helper. Preserve
   `prepare` and `cleanup` result fields and expected-root checks. Add focused
   export/collision/drift/link/resume regressions before production changes.
3. Update the existing lifecycle tests and provider-free verifier to use the
   explicit export phase. Keep original safety/error assertions. Document the
   deletion preconditions and one uncertain-residue recovery in the skill and
   user-facing English/Korean/security surfaces.
4. Fresh GREEN: focused cleanup/lifecycle tests, full repository suite, canonical
   skill validator and fixed provider-free lifecycle verifier. Run Ubuntu 24.04
   independently. Record exact source stability and owned fixture cleanup.
5. Refresh latest spec and A comparisons; full required multi-family review over
   P2 and affected consumers. Apply only reproduced in-scope corrections and
   repeat every leg on a fresh basis. Commit/merge under standing authorization;
   installation, publication of the shared authoring branch and adoption stay
   separate.

## Implementation checkpoint

The initial fresh dedicated RED reproduced four unsafe deletion cases. A second
fresh dedicated RED reproduced five filesystem-error reporting gaps and missing
generated snapshot/prompt custody (six failures). The leader corrected those
bounded findings and retained terminal-writer/single-cleaner assumptions.
The helper uses three external records (allocation, export and claim identity)
and one private claim container; there is no global registry or new provider route.

Current production estimate: approximately 340 additions / 51 deletions across
the lifecycle helper and synthetic verifier; about 285 novel helper lines.
The increase over the initial estimate covers resumable claim ownership,
verified external byte custody and the verifier's failure retention. Tests,
fixtures and docs are separate. Fresh GREEN and formal review remain pending.
