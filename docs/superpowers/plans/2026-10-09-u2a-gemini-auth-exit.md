# U2a — Preserve Gemini authentication exit 41

Authority: owner continuation of shared-spec implementation. Existing C37,
R-AUTH/R-CLASSIFY and DL-99 decide this behavior; no new design is proposed.
U2 is split by observable carrier to keep implementation and evidence bounded.

Confirmed source: Gemini v0.63.0 `packages/core/src/utils/exitCodes.ts` assigns
FATAL_AUTHENTICATION_ERROR=41 (official raw source fetched 2026-10-09).
A `_auth_carrier_stop` checks it at 0e04d2a. B 632f426 plus dirty source still
treats it as docs-only; classify and late signal handling lose the auth STOP.

Expected production delta: about +20/-8, net +12, novel core under 20 lines in
`bin/_common.py`. Tests about 75 added lines in `tests/test_gemini_auth_exit.py`;
plan/status evidence separate. No native-leg, global configuration or prompt edit.

1. Fresh dedicated source executor runs the new provider-free cases against
   current bytes and records RED plus controls. No real authentication failure,
   credential inspection or provider inference is needed.
2. Recognize the raw Gemini code before timeout/other failed-run classes;
   preserve terminal token/65 through capture and late SIGTERM/SIGHUP without
   altering cleanup or allowing a cancelled answer. Other CLI exit 41 stays unknown.
3. Fresh executor runs GREEN, complete affected provider/signal modules and
   validators. Run full suite once after the final correction.
4. Required fresh full-scope Claude/Google Pro/Google Flash/native Astra review,
   exact custody and cleanup; record shared implementation evidence after admission.

Do not broaden this unit to authentication phrase parsing, environment-variable
scrubbing, extension validation or AGY credits carriers. Those remain U2 follow-ups
with their own evidence. Tests must fail if Gemini 41 becomes unknown/retryable,
if a signal erases it, or if another CLI inherits the code. Existing cancelled
success tests must remain passing. No conformance claim for the whole C37 follows.

Execution ledger: dedicated RED 7 failed / 3 passed; log-isolation correction
reproduced the same RED before implementation. Actual production delta +26/-13,
net +13. New tests and existing signal module passed 18 cases. Dedicated GREEN
focused scope passed 179 / skipped 4; full suite and formal review pending.
The first RED's stale-log cleanup had an unisolated import-time root; historical
deletion effects cannot be reconstructed without a prior inventory. Corrected
test fixtures isolate the log root and disable unrelated global cleanup.

Ruling: after focused GREEN, overlap read-only review with the full suite on
fixed source bytes. Admission waits for both; a test-triggered source correction
requires a new complete round. This saves idle time without transferring approval.

Completed: full suite 1925 passed / 4 skipped, both skill validators passed,
same tested-source hashes. Fresh triad-gemini-auth41-20261009-r1 all four SAFE,
ROUND_INTEGRITY_OK, ALL_SELECTED_APPROVED; all terminal, custody exported and
exact stage/cwd removed. Three nonblocking findings have dispositions in the
round adjudication. The two further engine-level coverage cases and old classifier
header are explicitly retained for the broader carrier unit; no whole-C37 claim.
