# AGY print-timeout admission correction

> Use `superpowers:executing-plans` inline. Owner approved the audit corrections
> with "진행"; continue within this bounded design without another approval handoff.

**Goal:** The measured AGY print-timeout stderr line never admits a partial answer.
**Spec:** Existing R-CLASSIFY, R-AUTH, C43, vendor-failure-lines and DL-62 in the
shared PR13 draft. C43's carrier/exit clarification precedes implementation.
**Architecture:** One shared line predicate used by the existing AGY admission
and authentication completed-answer exemption. No new taxonomy, retry or process.
**Tech stack:** Python3.12+, pytest and the existing source TRIAD review toolkit.

Baseline B e3a35a3, S20c5e64, remote main3afc4d7 and read-only A1de943af.
Expected production +15–25/-0, net +15–25; novel core below25 lines, two files
(`bin/_common.py`, `bin/antigravity_wrapper.py`). Separate tests about150 lines;
English/Korean/security guidance about12 lines. Keep native legs and user settings.
All Python/tests/provider/Git mutations use `/bin/zsh -lic`, require_escalated
first, host cwd workspace and canonical invocation-owned TMPDIR before Python.

## Review focus

- Full own stderr line only; raw/schema partial answers and absent result, any exit.
- Authentication STOP precedes timeout even for SUCCESS/exit0 with usable-looking output.
- Preserve wrapper-timeout/transport priority, quoted/wrong-carrier controls, original
  streams/vendor exit, one CLI call and stored failure interpretation through the same code.
- Keep existing typed turn-timeout65 distinct from print-timeout2. No live error induction.

## Task 1: Correct AGY print-timeout admission

- [x] Clarify C43 input, validate shared authoring/tests, push and request PR13 review.
- [x] Write `tests/test_agy_print_timeout.py`; fresh dedicated executor observes RED.
  Expected: own-line partial-result and authentication-priority regressions fail;
  negative carrier and existing transport controls pass.
- [x] Add the shared predicate and two call sites; update affected public guidance.
- [x] Fresh dedicated GREEN: focused tests, full suite, four skill validators,
  diff check and matching source fingerprints. Expected: all applicable checks pass.
- [x] Fresh Sol/xhigh + Astra/high + Google Pro/high same-basis review. Expected:
  all selected results admitted, matching integrity and exact owned cleanup.
- [ ] Commit/push, record bounded C43 evidence and update SoT/PR13. No merge/install/release.

Evidence lives in workspace `_runs/infra/20261011-agy-print-timeout/` and the fresh
unit review directory. Existing untracked owner documents remain untouched.

Shared3495262 is pushed, authoring1/1 and182tests passed; PR13comment6105233291.
Fresh dedicated RED:27failed/15passed, matching source fingerprints and exact
cleanup. Failures cover partial raw/schema answers, empty/missing result,
authentication priority and stored replay; all carrier/transport controls pass.
Actual production delta +12/-0; tests120lines, public guidance11lines.
Fresh dedicated GREEN:320focused/2411full passed,4skipped; all four validators
and diff check passed with matching source fingerprints and exact temp cleanup.
Round `triad-agy-print-timeout-20261011-r1`: all three SAFE, no findings or open
questions; ALL_SELECTED_APPROVED with matching final integrity. Every producer's
actual terminal outcome was consumed; custody exported and exact stages cleaned.
No new live vendor timeout was induced; other C43 rows retain their own limits.
