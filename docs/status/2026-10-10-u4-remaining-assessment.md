# Remaining U4 assessment

Read-only reconciliation after U4d, 2026-10-10. B HEAD632f426 plus the preserved
candidate; shared branch c25da30, main3afc4d7; cached PR12 ref6a2883d. The PR12
ref is a local evidence revision, not a claim of the latest remote head.
Claude source reference remains a5afdd5a plus its concurrent dirty work. No A
runtime executed. No production changes or new test run in this assessment.

## DL-119 — Existing B correction; no duplicate implementation

PR12's row records missing authentication escalation and an applier that accepted
oauth-env. It is absent from this branch/main's historical row table, so inspect
the PR12 row rather than treating the missing row as a missing requirement.

Current B docs/references/repair-protocol.md opening assigns authentication
recovery to the user; Apply explicitly states that every oauth-env proposal is
refused. bin/_common.py:apply_classifier_patch refuses that class before storage
on either target path. tests/test_repair_proposals.py checks helper/owner CLI,
four CLIs and exit/banner targets, preserving the original extension and curated
entries. These tests are part of U4d's passing393 affected tests. The U4b1 repair
correction already supplies this implementation; do not create another applier.

The embedded child prompt instructs it to inspect the local classifier framework
and satisfy current validation rules; it does not repeat the authentication
sentence verbatim. This difference alone is not observed wrong behavior. No new
wording loop or phrase-pinning test is warranted. If a concrete child decision
violates escalation, use the owner's fresh scenario/control probe before revising.

Read-only A export_assets/distributed-repair-agent.md.tmpl explicitly escalates
authentication; its _common.py rejects oauth-env proposals too. A's export
renderer is host-specific and is not a B port. Full C37/C43 certification and
shared revision adoption are separate from this bounded B disposition.

## DL-91 — Confirmed remaining cleanup candidate

The shared row removes retired task/fanout tokens and exits, while retaining
task-blocked65 for Claude permission-denial envelopes. B still has exits68/69,
the fanout-spawn-error classifier/pattern/repair memberships, extract_codex_fanout,
and the optional codex answer-extraction branch in run_cli_with_retry. The
production callers found under bin/ are Claude and Gemini wrappers; stored replay
explicitly accepts only those plus the AGY interpreter. There is no Codex wrapper.

This is a concrete remaining source/spec mismatch, not a speculative vendor
failure. Some old fanout classification logic can still be reached through the
generic classifier, so do not describe every removal as unreachable. A bounded
next unit must inventory production, tests, shipped docs and dynamic references,
then remove retired engine support under DL-91 while preserving Claude
task-blocked65, native Codex dispatch, shared locking and active extraction paths.
Do not silently remove generic callable parameters or combine this with cleanup
entry-point design. Estimate the source delta and review that unit separately.

This assessment led to the completed U4e unit: shared a41769c preceded code,
389071a records final455affected/2152full passing tests (4skipped), four validators
and all-four SAFE/matching integrity. Production net-182; Claude task-blocked65,
native dispatch and locking preserved. No additional DL-119 implementation or
U4d rerun is queued. Current next action lives in spec-to-code-sot.md.
