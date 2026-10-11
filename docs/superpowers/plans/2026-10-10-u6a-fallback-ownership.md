# U6a: prove ownership before fallback IPC cleanup

> **For agentic workers:** Use superpowers:executing-plans for this bounded
> correction. Dedicated fresh source-skill executors own RED/GREEN; the same
> four-family unit review follows before another implementation unit.

**Goal:** A next-run sweep deletes only fallback IPC directories allocated by
this host, preserves unproven residue, and retains proof through interruption.

**Architecture:** Keep `emit_run_log` and `prune_stale_tmp_dirs`. Add a private
sibling allocation record tied to the exact directory identity. The fallback writer records ownership after preserving the IPC file; a proof
write failure must not hide that file. The first eligible removal records its
checked flat contents; unexpected subdirectories are preserved, not recursively
claimed. Before any removal, resume accepts only the same
remaining subset and removes proof last. No new public cleanup command.

**Tech stack:** Python3.12+, stdlib/POSIX primitives already used by `_common`.
**Spec:** shared `reference/review-rules.md#R-CLEANUP`, C4/C5/C69, DL-77;
`decisions/2026-10-10-b-cleanup-entry-evidence.md`. U6b owns declared roots.

## Evidence and boundary

The isolated source spike deletes a synthetic old prefix-matching foreign
directory. Three independent diagnoses confirm the reachable fallback path.
Current B review-packet cleanup is already proven and remains unchanged.
Current A0be173bf has no corresponding new runtime change; A supplies evidence,
not an implementation to copy. No actual user-data loss is claimed.

Expected production delta +120-220/-15-35 (net+85-205), <=180 novel core lines,
mainly `bin/_common.py`; tests +150-240, documentation +15-35. Growth needed for
actual interruption/ownership checks stays in this outcome; no generic service.

## Constraints and review focus

- Preserve failure IPC, original provider output/status and configured-root
  no-fallback. No vendor invocation, environment edit or native-leg change.
- Default floor3600seconds; caller settings cannot lower the host minimum.
  Age comes from proof, not directory mtime after partial deletion.
- Preserve unmarked, malformed, mismatched or replaced allocations. Do not
  synthesize ownership for old residue or follow symlinks.
- A stopped removal retains proof and validates its remaining subset before
  retry; new/changed content or a git entry refuses without starting deletion.
- An own-call failure rolls back only resources allocated by that invocation;
  no scan of the real system temporary directory in any test.

## One implementation task

**Files:** `bin/_common.py`, `tests/test_log_cleanup.py`, new focused
`tests/test_fallback_cleanup_ownership.py`, affected README EN/KO.
**Interfaces retained:** `emit_run_log(...) -> Optional[Path]` and
`prune_stale_tmp_dirs(prefix, age_floor_s=3600, base=None) -> None`.
**Private record:** sibling `.<directory-name>.allocation.json`, version/role,
absolute root, directory uid/device/inode; deletion-start inventory only when
eligible. Canonical exclusive regular-file creation; no replacement of an
existing record. Exact internal fields are host-owned, not public spec fields.

- [x] Update shared cases with stale unproven fallback preservation and valid
  allocated positive control; record U6a/U6b separation and share the commit.
- [x] Add provider-free tests: unmarked prefix match preserved; real fallback
  writer creates proof; stale owned removal; fresh proof preserved despite old
  directory time; malformed/wrong-identity/symlink proof preserved; unknown
  git entry refuses; interrupted removal keeps proof; resumed subset succeeds
  while changed/new entries refuse; proof failure retains provider result.
- [x] Isolate both pytest and standalone cleanup-test runner temp bases. Existing
  cap, primary storage failure, explicit-root no-fallback and repair controls
  remain. Replace only the old unproven-deletion expectation.
- [x] Fresh dedicated RED for the actual ownership failure, with source/log
  fingerprints and exact fixture cleanup. No inferred bug from mocks alone.
- [x] Implement the private allocation/read/removal helpers using existing
  no-follow, canonical JSON, descriptor identity and advisory-error primitives.
  Keep proof last and preserve uncertain residue. Remove obsolete fan-out
  docstring; describe old residue as preserved, without hand-delete commands.
- [x] Fresh dedicated GREEN: focused ownership/log/review cleanup modules,
  standalone log harness, full repository suite and four source validators.
  Every execution uses `/bin/zsh -lic` with `require_escalated` and an exact
  invocation-owned TMPDIR/log directory.
- [x] Complete fresh opus/xhigh, AGY Pro/high, AGY Flash/high, Astra/high unit
  review; adjudicate findings, export custody and clean exact current stages.
- [x] Publish the reviewed source checkpoint and accurate shared case evidence.
  Update SoT; U6b/DL-77 remains open and whole-task hook remains installed.

No install, merge, adopted revision, release or whole-task completion is implied.

Shared ba04c60 was pushed and shared in PR13 comment6095933437 before code.
U1T completed at Bed8b76f / sharedd3a4412 and PR13 comment6095971207.

First dedicated RED:16failed/37passed/2teardown errors. Actual missing-proof
assertions fail as intended; fixture teardown collided with os.close failure
injection. Keep that evidence. Pytest isolation now uses its owned tmp_path and
monkeypatch lifetime, rather than immediate teardown cleanup. No product edit.
Fresh RED-valid is required before implementation.

Fresh RED-valid:16failed/37passed, no errors; source/log fingerprints unchanged,
exact fixture cleanup. Two unproven deletion cases and the failure-IPC retention
case reproduce actual deletion;13 cases stop at missing allocation proof, so
their later assertions were not reached. Candidate keeps existing entry points,
uses a sibling allocation line and appended deletion-start inventory, and only
cleans the writer's flat run-log/repair pair. Unknown entries/subdirectories are
preserved. A partial start line is not started; deletion waits for a complete
flushed line. No recursive cleanup engine or new public command.
Fresh dedicated GREEN completed:334affected,29/29standalone,2341full passed and
4skipped; all four validators passed. Source/log integrity and exact fixture
cleanup passed. Production+144/-17,net127,one file. Fresh complete unit review
`triad-fallback-ownership-20261010-r1` is next; no prior unit approval is reused.

R1 completed all-four SAFE/matching integrity; four Minor findings are preserved
with adjudication. Its own-call fallback-write rollback omission was reproduced
by fresh RED-rollback:1failed/55passed, source/log integrity and exact cleanup
passed. The correction attempts only rmdir of that call's newly-created empty
folder; nonempty/refused residue and the original failure survive. Strengthened
symlink/proof-failure/partial-start controls passed RED's controls. README now
names retained residue and operator responsibility without a deletion command.
Production+153/-18,net135,one file. Fresh GREEN-rollback and complete R2 follow.
GREEN-rollback completed337affected,29/29standalone,2344full passed/4skipped and
four validators; source/log integrity and exact fixture cleanup passed. R2 is
the current complete unit review; no previous approval is carried forward.
The allegation of a real-temp full-suite sweep was refuted against the actual
runner, which sets an owned TMPDIR before every fresh subprocess.

R2 NOT_APPROVED with matching integrity: three SAFE, native Major. Fresh
RED-concurrent-valid1failed/18passed reproduced overlapping starts replacing
the durable inventory and deleting a changed remainder. The first19passed
probe paused after ftruncate refreshed proof age and missed the race; retained
as invalid RED. No source changed during either isolated probe or R2.
Shared dc48e3e/C5 and PR13comment6096424215 precede dependent implementation.
The bounded correction holds the existing proof descriptor's nonblocking lock
before reading; busy allocations skip and identity is checked under lock.
No new lock file/service. Add two leaf-symlink target-survival controls and
correct the caller's proof-age comment. Fresh GREEN-concurrent/full suite and
complete R3 follow; R2 adjudication/export/exact cleanup are complete.

Final GREEN-concurrent:340affected,29/29standalone,2347full passed/4skipped
in410.97seconds, all four validators, matching source/log fingerprints and exact
fixture cleanup. Production+160/-19,net141,one file. The new focused test file
is304lines; growth beyond the initial test estimate is the deterministic
two-sweeper schedule plus rollback/leaf-link controls for reproduced findings,
not a new feature or public surface. Current R3 reviews these exact bytes.

R3 completed all-four SAFE with matching integrity, adjudication, custody export
and exact stage cleanup. Optional per-candidate diagnostic detail remains a
nonblocking limit; no new runtime logger surface is required. The actual full
suite was isolated; clarify the general verification command's TMPDIR requirement
as a documentation follow-up. Reviewed runtime/tests remain unchanged.

Published: B `a4fd93c6283349df67bdb5c4d718a52144ac4547` and shared `c55dca6`
are pushed and remote-matched. C4/C5 reference this verified fallback behavior;
U6b/DL-77/C69 remain pending. Shared authoring1/1 and182tests pass. The local
verification guide now requires invocation-owned TMPDIR before Python starts.
