# Legacy agent exact-content cleanup

> Use `superpowers:executing-plans` inline. Owner approved bounded audit corrections.

**Goal:** Preserve edited/unknown retired agent files during bootstrap removal and quarantine.
**Architecture:** Replace the first-five-lines header predicate with six complete-file
hashes from historical unchanged-copy installs. Preserve existing capture/claim/race
handling. Unknown machine-rendered content stays unmanaged; no template matcher,
installed-state database, global settings change or U8 coexistence work.
**Contract:** B README/SECURITY exact-content preservation; shared audit record only.
This is host-owned bootstrap behavior, not a new common case or an A/native-leg change.
**Tech stack:** Python3.12+, pytest, existing bootstrap helper.

Baseline B e439fdf. Historical307745f/dca0cd4 copied three full TOMLs each.
Later fee6f6f/50e6faa/ebdc0c9 templates rendered machine paths/read grants without
an immutable installed-byte receipt; preserve those uncertain files with the existing
unmanaged warning. Source history proves templates/install behavior, not any actual
user installation. Evidence: whole-system audit `repair-install.md` addendum.

Expected production +12–18/-9–12, net0–9, novel core below5 lines in
`bin/bootstrap_repair.py`. Separate tests about100lines plus six full historical
fixtures; replace abbreviated ownership fixtures in two existing test files.
Update English/Korean/security guidance only for this preservation boundary.
All Python/tests/Git mutations use `/bin/zsh -lic`, require_escalated first,
host cwd workspace, canonical invocation-owned TMPDIR before Python.

## Review focus

- Only complete known payloads qualify; retained headers alone are insufficient.
- Appended/body/encoding/line-ending edits, foreign snippets and rendered variants survive.
- Removal and quarantine share the predicate; captured inode/race/no-clobber checks remain.
- Existing installer warnings communicate preserved files; no scan of user-global state.

## Task 1: Narrow legacy ownership

- [x] Record bounded B-only evidence in the shared log; no new common constraint.
- [x] Add full historical fixtures and behavioral tests; fresh dedicated RED.
  Expected: edited/header-only files fail preservation, complete originals still qualify.
- [x] Replace the header predicate with exact historical content hashes; align docs
  and existing race-test inputs with complete owned payloads.
- [x] Fresh dedicated GREEN: focused/full suite, four validators, diff check,
  source integrity and exact cleanup. Expected: all applicable checks pass.
- [x] Fresh Sol/xhigh+Astra/high+Google Pro/high same-basis review before another unit.
  Expected: all selected verdicts admitted, matching final integrity and exact cleanup.
- [x] Commit/push, update this plan/SoT and share the bounded result on PR13.

Evidence: workspace `_runs/infra/20261011-legacy-agent-ownership/`.
No actual owner artifact is removed in verification. No install/merge/release claim.

Shared8c1f6c0 is pushed; authoring1/1 and182tests passed, PR13comment6105413082.
First dedicated RED22failed/14passed:20 ownership-preservation failures and two
rendered-fixture preparation errors. Source integrity and exact cleanup passed.
The fixture must replace PYTHON3 and whole grant lines exactly as historical
fee6f6f bootstrap did; correct only that input before a new fresh RED executor.

Corrected fresh RED:22failed/14passed, all22 failures reached the ownership
entry points; no setup errors. All12 complete-original controls and two invalid
UTF8 preservation controls passed. Terminal exit1, source integrity matched and
exact temporary cleanup completed. Production now changes only the ownership
predicate/constants; full GREEN is next. Fixtures are inert historical evidence.

Final production delta:13 added/9 removed, net4, one-line predicate plus constants.
Dedicated GREEN:411focused/2447full passed,4skipped; four validators and diff check
passed. Python3.12.13/pytest9.0.3, macOS26.6.2 arm64. Pre/post source fingerprints
matched and exact owned temp cleanup completed. Ubuntu was not run.

Fresh `triad-legacy-ownership-20261011-r1`: Sol/xhigh, Astra/high and Google
Pro/high all SAFE; schema/bindings valid, no open questions, ROUND_INTEGRITY_OK.
Digest04c75f77169f8d2e31f727770d5bb2a6fd6463755dec88155ee951002c04cd57.
All actual handles terminated; exact stages/cwd were cleaned after evidence export.
Receipt: workspace `_runs/reviews/triad-legacy-ownership-20261011-r1/`.

Deferred minor: Google suggested inlining the existing profile/rules dispatcher
`_managed_artifact_data_is_owned`. Its single caller was confirmed, but no current
correctness defect was shown and that unchanged dispatch is outside the legacy
ownership correction. It creates no automatic follow-up implementation.

Committed/pushed B8efa45e, sharedb6c5b76; authoring1/1 and182tests pass.
PR13comment6105598443 shares the result. Exact execution scratch was exported
under the evidence root and removed after task completion; no active next action.
