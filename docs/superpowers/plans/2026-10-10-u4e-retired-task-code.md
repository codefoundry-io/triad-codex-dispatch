# U4e — Retired task engine removal

> Execute inline using superpowers:executing-plans and test-driven-development;
> dedicated fresh source executors verify RED/GREEN; four-family review follows.

Goal: implement settled DL-91 without changing host-native dispatch.
Spec: shared main3afc4d7, DL-91/D-TASK-MODE-REMOVED-20261005, C8/R-TOKENS;
decisions/2026-10-10-b-retired-task-code.md. B632f426 plus preserved candidate;
read-only A3bb4f284 has removed fanout support but retains its active Codex CLI
answer extractor. B has no such wrapper; do not copy A's host internals.

Architecture: remove retired tokens/patterns and their engine memberships, unused
Codex/fanout/implementer-status extractors and the unused Codex extraction arm.
Keep run_cli_with_retry's parameter signature, Claude/Gemini callers, locking,
task-blocked65, native dispatch and historical report-directory cleanup.
Refresh only the C8 token fixture from exact verified shared-main bytes; this
is a fixture update, not whole-revision adoption. Preserve the pre-unit bytes.

Estimated production+2-6/-195-235(net-189..-233), novel core0; tests+35-55;
fixture/docs+10-20/-20-35. Python3.12+; no provider calls in tests.
Files: bin/_common.py, bin/apply_patch.py, tests/test_exit_token_contract.py,
tests/test_retired_task_contract.py, tests/fixtures/shared-spec/{exit-tokens.json,README.md}.

Review focus: retired fanout phrases no longer emit a retired terminal token;
extension loading/proposals cannot restore that token; valid classes still work;
Claude permission-denial stays task-blocked65; existing extraction/replay/locking
and native dispatch remain unchanged. Related-code discovery stays available.

- [x] Inventory source/test/doc callers; fetch shared main and check PR13.
  Main3afc4d7, latest reply6088729953/own6089074042; no new A disagreement.
- [x] Publish shared host-specific disposition before dependent edits.
  Shared a41769c/PR13comment6091668144; authoring1/1 and182tests pass.
- [x] Preserve pre-unit source/fixture and prepare exact new fixture plus behavior
  tests. Fresh executor RED: retired phrase -> unknown rather than terminal;
  retired pattern proposal refused without write; C8 table rejects old emission.
  No private-name absence tests. Existing Claude receipt tests are the positive control.
  Fresh RED12failed/443passed; unchanged source/logs and exact cleanup confirmed.
- [x] Remove only inventoried retired code; keep generic callable parameters and
  historical cleanup out of this unit. No new abstractions or CLI route.
  Actual production+7/-189(net-182); tests+42/-1; fixture/docs+9/-14.
- [x] Fresh executor GREEN: complete affected classifier, wrapper, repair, Claude
  receipt and transport modules, then full suite and four skill validators.
  Child-only log/TMPDIR roots before imports; preserve source/log state and exact cleanup.
  Affected455/full2152passed,4skipped; four validators passed. Seven hashes/HEAD/
  status and ten source logs unchanged; exact root removed.
- [x] Fresh required four-family review, adjudication, custody export and exact
  temporary-root cleanup; publish evidence and update SoT/broad plan.
  R1 all-four SAFE/ROUND_INTEGRITY_OK, terminal producers, exact cleanup.
  Shared389071a published with authoring1/1 and182tests passing. One verified
  nonblocking stale-comment finding deferred; no post-review product edit.
  PR13 completion reply6091822527 records the same evidence and limits.
  Digest25a3086321541c0271b967e5d6bd00178e40fbb4727f13aeead3a34ccf6bc486;
  fingerprint293bf2e586dd096b7341af91c41681a70b5176cd2a04a1128547a07e945487aa.

Ruling: settled removal and inline execution are already authorized; no repeated
plan approval. Project custody/dirty-state rules replace generic commit/worktree
deletion steps. Substantial new interface/design choices still stop for the owner.
Every Python/test/Git-GH mutation uses /bin/zsh -lic with require_escalated from
the workspace host cwd. No installation, merge, release or hook retirement.
