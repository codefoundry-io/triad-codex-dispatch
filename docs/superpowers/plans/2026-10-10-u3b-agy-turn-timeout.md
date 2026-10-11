# U3b — AGY terminal turn-timeout classification

> Execute inline with superpowers:executing-plans and test-driven-development;
> fresh dedicated executors verify RED/GREEN; required four-family review follows.

Goal: implement the settled DL-102/C43 turn-timeout row. AGY's typed terminal
result.error starts with `timeout waiting for response`, status ERROR, response
empty and vendor exit1: return vendor-timeout/65, with no answer. Current B sends
only stderr/status to classification and returns unknown/1 for that carrier.

Spec: contracts/vendor-failure-lines.json, R-CLASSIFY, C43, DL-102. Shared main
3afc4d7; B632f426 plus preserved work; read-only A a5456b13 has the anchored
_is_vendor_turn_timeout predicate. A's broader whitespace/case/route handling
does not expand the exact measured row implemented here. No A runtime run.

Architecture: one carrier-specific check inside _interpret_run after the existing
auth/host-timeout/transport priorities and before the nonzero fallback. Reuse the
existing vendor-timeout token/65 and bounded diagnostic suffix. Do not scan raw
stdout, stderr, tool output or answer prose for this phrase. Existing classifications
outside the row remain. No new helper, retry policy, environment or native change.

Estimated production+12-18/-1(net+11-17), novel core12-17; tests+80-130;
docs+40-70. Files: bin/antigravity_wrapper.py, bin/_common.py (one stale comment),
tests/test_agy_turn_timeout.py, tests/test_exit_token_contract.py, README.md and
README.ko.md for the reported outcome.
Tests are constructed contract inputs, not captures.

Review focus: strict terminal carrier and prefix, exact status/exit/empty-response
boundary, auth/timeout/transport precedence, no inferred fields, preserved answer
prose and diagnostic custody. Normal success and nonmatching error controls remain.

- [x] Publish shared scope/C43 test pointer before dependent implementation.
  Shared9e03c6c, authoring1/1 and182tests pass; PR13comment6092051096.
- [x] Preserve pre-unit bytes and write the contract cases; fresh dedicated RED.
  Four expected failures,412passed/4skipped; source/logs unchanged, exact cleanup.
- [x] Minimal implementation and current token comment correction.
  One 13-line carrier branch plus the token comment; EN/KO outcome documented.
- [x] Fresh dedicated GREEN: complete affected wrapper/auth/replay/transport/token
  tests, full suite and four source validators; child log/TMPDIR before imports.
  First GREEN415passed/4skipped/1failed: the old token-contract MAP_ONLY set still
  prohibited vendor-timeout emission. Move it out of that set while preserving
  its exclusion from phrase-repair vocabulary. No production correction.
  Final fresh affected416passed/4skipped, full2171passed/4skipped, four validators
  passed; seven hashes/HEAD/status and ten source logs unchanged, exact cleanup.
- [x] Fresh complete review, adjudication, integrity, custody and exact cleanup;
  publish evidence and update SoT. Do not mark all DL-102 complete: truncation remains.

Ruling: U3a's unanswered admission questions affect only that dependent change;
this existing, independently testable row can proceed. U8 remains withdrawn.
No product install/merge/release. Commands use /bin/zsh -lic with require_escalated
from workspace host cwd; preserve dirty work. Substantial design changes stop.

R1 all four SAFE, ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK; one optional Minor recorded, no correction needed. Custody exported and exact stage/cwd removed. Evidence in workspace _runs/reviews/triad-agy-turn-timeout-20261010-r1/.
