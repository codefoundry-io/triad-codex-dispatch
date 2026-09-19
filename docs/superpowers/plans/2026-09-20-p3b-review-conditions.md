# P3b: bind review conditions and toolkit bytes

P3a completed its full review and merged as `d15becea515635429d21533580e2816526884fb9`.
Close original `claude-01` and `codex-01` through a new full round. The leader
writes tests/source; fresh dedicated Terra/high executors observe RED and GREEN.
Shared remote main at planning: `2eb883fee59e66556ee7c7f87189b38231136622`.

## Existing requirement and smallest correction

Prepared rendering currently hashes prepared bytes and Google receipts, but not
the objective, criteria, boundary, kind or prepared path. Guarded rendering
already hashes those conditions. Both renderers omit the renderer's own static
clauses and the exact schema implementation. Gemini preflight identifies its
policy by path rather than bytes. R-PREPARE treats rule, schema, prompt and policy
changes as changes to the reviewed behavior; R-BIND retains the current wire.

Build the prepared common metadata before computing its digest; include every
current condition and receipt, excluding only the family and derived digest.
Add exact `review_round.py` and `verdict_schema.py` hashes to the common metadata
in both routes. Hashing whole files deliberately over-invalidates rather than
introducing a template-extraction layer. Preserve custody, snapshot verification,
paired Pro/Flash, route checks and the existing result schema.

Add `policy_sha256` to B's Gemini preflight record. Hash the same raw policy bytes
that the producer validates; require and recompute that hash in the existing
receipt validator used by rendering and dispatch. Older ephemeral receipts must
be regenerated. This does not choose new policy bytes, weaken guards, adopt a
shared revision, add roster fields or resolve D-B1. No AGY policy framework.

## TDD and verification

- Fresh dedicated RED: each changed prepared objective, criterion value/order,
  boundary value/order, kind, path and review ID changes its digest; family alone
  preserves equality. Mutating a copied toolkit renderer or schema changes both
  routes' digests without editing canonical files.
- A valid policy-byte change invalidates the old Gemini preflight before any
  provider call. Regenerating a receipt yields a different common basis. Assert
  the producer's actual hash, missing/wrong hashes, and unchanged compatibility.
- Preserve both route selection and paired-worktree tests, strict bindings,
  malformed receipt rejection, snapshot and canonical-file checks.
- Fresh GREEN, full macOS/Ubuntu 24.04 suites, source skill validator and fixed
  lifecycle. Complete a fresh full multi-family gate before merge/next plan.

Estimated production delta <= 100 additions, <= 30 deletions, novel core <= 70
lines, primarily `bin/review_round.py` and `bin/gemini_wrapper.py`; test fixtures
and relevant prompt/receipt documentation are counted separately.

A comparison at `92c8afd500499d8736afcc28b39a87a4f87fed50`: packet file-hash
folding in `.claude/skills/triad-cross-family-review/lib/review_scratch.py:1588`;
delivery brief/diff/history hashing at `4401`, then prompt rendering at `4423`.
Refresh these exact lines and record the A-specific gap in the shared spike.
A remains read-only. No shared design/wire change or deployment is implied.
