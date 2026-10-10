# U4b2 — Stored-record repair verification

> Implement sequentially with superpowers:executing-plans. Preserve the current
> dirty source and native legs. Owner's latest direction is minimal reuse.

Goal: route actual unknown/extraction-error failures to the repair protocol,
exclude timeout/auth recovery, and verify applied classification against the
same stored run without another vendor call.

Spec: shared R-CLASSIFY, DL-104/C76 and
decisions/2026-10-10-repair-replay-inputs.md. PR13 reply6083248450 agrees and
schedules A's analogous work; completion is not claimed on A.

## Owner direction and bounded change

Keep the skill's core simple: pass review points and the diff/worktree, let
reviewers discover related code, then collect their results. Security and cwd
plumbing must justify their actual role rather than drive new architecture.
This unit does not redesign review execution or add routine log/read audits.

The provider-free AGY spike proves that classifying saved stdout/stderr wholesale
can report a successful repair while the actual interpreter remains unknown.
The diagnostic extraction_error also contains text not used by that classifier
call. No production defect or real provider incident is inferred from this fixture.

Owner steering supersedes the earlier architecture-choice question. Use the
existing failed record and the existing route's classification logic. Extract
only the small function needed to share that logic when necessary; no general
replay engine, new log schema or broad wrapper refactoring is planned. Preserve
the spike's wrong-channel control. If the actual record cannot support a sound
check, disclose that limit instead of guessing or building a new subsystem.
No source edits or RED/GREEN admission yet.

Implementation ruling: retain apply_patch.py and its --cli/--classifier-file/
--proposal-file arguments; add --verify-run-log PATH as a read-only alternative
to applying, after owner apply. Exit0 means the current extension produces the
proposal's class on the saved failure; exit3 reports mismatch or unsupported
evidence without mutation. Reuse AGY's existing _interpret_run, raw failure
classify, and the existing Claude/Gemini extraction classifiers. Never execute
recorded argv or infer extraction input from a diagnostic. This verifies failure
classification only, not full successful review admission or a new vendor run.
Native Codex has no wrapper on B and is not added. Ineligible, interrupted or
unusable records are reported rather than reconstructed by guesswork.

## Execution

- [x] Identify the smallest existing classification call reusable for the failed
  record and connect its check to the owner apply flow. Preserve the log format
  and existing command surface where possible. Initial bounded estimate:
  production+30-100/-0-40, novel core<=70; tests80-150, docs10-25. Re-estimate
  from actual code before edits; line count is not permission to add machinery.
- [x] Add meaningful RED against real stored-record producer and route consumer:
  matching learned phrase, wrong-channel control from the spike, raw vendor
  exit, authentication precedence, timeout exclusion, malformed/unsupported
  record, and zero provider calls. Do not assert document phrases.
- [x] Fresh dedicated source executor observes RED, including dispatch-skill
  routing decisions; leader implements only the evidenced bounded change.
- [x] Connect three dispatch skills to the protocol, remove timeout routing
  and vendor-rerun verification advice; preserve native analyzer spawning.
- [x] Fresh dedicated GREEN, relevant full modules/full suite/source validators;
  exact neutral fixtures, pre/post hashes/status and terminal handles recorded.
- [x] Fresh owner-selected four-family review and integrity/cleanup; update
  shared evidence and SoT. No install, merge or release claim.

Review focus: replay must use the runtime route's actual carrier/phase; no
wrapper diagnostic as evidence input; no repair of auth/timeout; no executing
recorded commands; never certify an unsupported record as repaired. C76 and
DL-104 remain open until implementation and verification complete.

Execution evidence: production+83/-1(net82), novel helper within70-line estimate;
tests+116/-0; skill bodies+21/-0; other guidance+43/-11 after TOC correction.
Scope remained the existing applier plus repair handoff. Valid dedicated
RED17failed; final dedicated GREEN329focused/2069full passed,4skipped, four
validators passed. HEAD/status/11hashes unchanged; exact fixture removed.
The separate initial wrong-shell RED is invalid and retained. Final GREEN
report: _runs/spec-plan-20261010/u4b2/green/report.md. Leader corrected only
the stale Rerun TOC link afterward; no executable or skill change followed.

R1 subsequently returned NOT_APPROVED with matching integrity: two Google SAFE,
Claude/Astra output-transport eligibility finding and Claude unchanged-class,
empty-path and lock-assertion findings. All are reproduced in dedicated RED:
9failed/19passed, including actual local output reader failure. Minimal guards
and corrected lock assertion pass28 focused cases in leader smoke. Common
R-CLASSIFY/C76 clarification92dc3e4 shared in PR13comment6084170769 before fixes.
Fresh GREEN and complete r2 review are required. No new log surface or design.

R1 corrections completed dedicated GREEN338focused/2078full passed,4skipped.
R2 is retained NOT_APPROVED with matching integrity; its native Major was
subsequently refuted against R-TERMINAL by the reviewer. Ordinary nonzero reader
failures retain vendor diagnosis in both runtime and verification. Corrected
the overbroad shared/product sentence, not the producer. Shared e6ea3ee and
PR13comment6084463664 preserve that rule. Added three actual local-reader
positive controls and one interruption control, without a provider invocation.

R2's fixture-location note was reproduced: import-time log globals defeated a
later environment override. Tests now bind those globals to tmp_path and assert
the emitted location. Exactly169 task-owned leaked records were archived and
removed; unrelated records preserved. No original log inventory exists to rule
out historical pruning, so prior neutral-root cleanup is not complete artifact
cleanup proof. See _runs/spec-plan-20261010/u4b2/fixture-log-recovery/.
Current32-case smoke passes with unchanged source run logs. Production code is
unchanged; fresh focused GREEN plus four validators precedes complete R3.

Complete: dedicated359-test GREEN and four validators passed. R3 all-four SAFE,
ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK, digest
1ea978486627066bed9f0f58a6851f15ea09eb79a1f347c80fb5b90aa5a7366a.
All sessions terminal; custody exported and exact stage/cwd removed. The two
optional Minor notes (unsupported-record wording and matching promotion tuple)
are verified nonblocking; no extra wording pass or speculative refactor.
Full C76 runtime limits, product integration and broader plan remain separate.

Commands use /bin/zsh -lic and sandbox_permissions=require_escalated from
/Users/chaniri/codex_workspace with absolute source paths. Providers excluded
from replay tests; formal review retains the previously selected roster.
