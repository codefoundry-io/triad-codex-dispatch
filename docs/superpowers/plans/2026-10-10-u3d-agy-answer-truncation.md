# U3d — AGY selected-answer truncation

Goal: implement the settled R-CLASSIFY/C43/DL-102 own-line truncation marker
rule for the raw answer that B emits. Shared ca64d1d/e292e5c and A reply
6092564483 settle channel selection; no new design choice is needed.

Execute inline with executing-plans and TDD. Keep the existing dirty checkout.
Read-only A bc8a8a74 checks response before selecting structured_output; this is
a documented A choice, not a requirement to discard B's valid structured result.
The historical vendor captures establish marker syntax, not a current size cap.

Architecture: check only a nonempty string response in the existing raw branch
of bin/antigravity_wrapper.py. An own-line `<truncated N bytes>` or
`<truncated N lines>` returns existing truncated-answer/65 and no answer.
Preserve raw evidence, priority, schema/binding/original-JSON checks and replay.
No tool/web scan, recursive structured-field scan, fixed size cap or retry.

Estimated production +6-9/-1 (net +5-8), novel core 5-8 lines; tests about
100-150 lines; documentation about 50 lines. Files: wrapper, _common token
comment, a focused test module, README EN/KO, this plan and SoT.

Review focus: raw own-line vs inline marker; tool and web-result controls;
valid structured answer with incidental response marker; earlier failure
priority; existing schema/binding checks; stored-record parity. Tests are
constructed contract cases, not new vendor captures.

- [x] Preserve pre-unit bytes and add C43 tests; fresh dedicated RED verifies
  raw folded answers currently escape as success while controls pass.
- [x] Add the minimal raw-channel check and public documentation.
- [x] Fresh dedicated GREEN: affected suite, full suite, four skill validators;
  retain exact commands, runtime, source/log integrity and fixture cleanup.
- [x] Required independent four-family review, findings adjudication, integrity,
  exact review-stage cleanup and shared completion evidence.
- [x] Owner-authorized WIP checkpoint commit/push of current spec-to-code work;
  preserve unrelated files. Report remaining work; no install/merge/release.

All Python/tests/provider and Git mutations use literal /bin/zsh -lic,
require_escalated, workspace host cwd. The whole-task hook stays until final
completion. Review/adoption/release are separate from a checkpoint push.

RED: initial 5failed/513passed/4skipped included an erroneous auth control using
raw0/SUCCESS/nonempty response, which intentionally suppresses a sign-in banner.
Corrected that fixture to raw1; production auth behavior remains unchanged.
Fresh final RED:4failed/514passed/4skipped; three raw positives and stored replay
failed as intended, all controls passed. Source/log integrity and exact cleanup
passed. Minimal production delta +6/-1 (net+5), novel core5 lines.

First GREEN:518affected passed; full2259passed/4skipped/1failed. The remaining
failure was a stale distribution documentation assertion prohibiting the now
active truncated-answer token. Removed only that tuple entry, retaining the
permission-unavailable prohibition and the rest of the test. The affected suite
now includes tests/test_distribution_contract.py; this sixth unit file changes
one test line. Fresh GREEN follows; initial failure/evidence remain retained.

Final GREEN560affected/2260full passed,4skipped and all four validators passed.
R1 found a CRLF marker miss (Major, reproduced) and a known-shape tool control
fixture error (Minor, verified). Source integrity matched; all four results are
retained without admission, custody exported and exact stage/cwd removed.
Shared7902ffa/C43 and PR13comment6093171510 record both hosts' matcher gap.
Add four CRLF cases (bytes/lines on raw and replay), correct the tool fixture,
obtain fresh RED, accept only the line-ending CR, then fresh GREEN and full R2.

Fresh CRLF RED4failed/560passed/4skipped confirms raw and replay misses for both
units; controls pass, source/log hashes unchanged and exact fixture removed.
Use fullmatch on response.splitlines() to recognize logical lines including
CRLF while preserving the original response/stdout. This is a six-line inline
check, no new helper or returned-text normalization. Production +7/-1 (net+6)
against pre-unit bytes; one additional line over the first candidate.

## B candidate verification

Fresh final RED:4failed/514passed/4skipped; three raw positives and stored replay
exposed the missing check, all controls passed. The first RED also exposed a
test-only auth fixture error (raw0 rather than raw1); fixed before final RED.
R1 exposed the CRLF marker gap; fresh CRLF RED:4failed/560passed/4skipped.
The line-ending CR is accepted without changing original bytes. The tool/web
control now uses the existing step_type=tool/tool_name shape. R1 remains
NOT_APPROVED with matching integrity and exported evidence; no approval carries.
Fresh GREEN:564affected/2264full passed,4skipped; four source skill validators
passed. macOS26.6.2 arm64,Python3.12.13,pytest9.0.3; Ubuntu NOT RUN. Seven scoped
source/skill hashes,HEAD/full status and ten source run logs unchanged. Exact
private/tmp fixture removed. These are constructed contract cases, not a fresh
vendor capture or evidence of a current universal answer-size limit.

Review triad-agy-answer-truncation-20261010-r2: all four SAFE, 1 nonblocking
findings, ALL_SELECTED_APPROVED and ROUND_INTEGRITY_OK. Digest
084604730e1bb87524491df1daecc7a6c1cacce5acf5634703f7cf6a425bbb0e; fingerprint
2c9fd914497e4ca5089fd0f1db7ab4384d2fd7de18e3765411c1a365a0426efd.
Custody exported, exact stage/cwd removed. No install, merge, release or whole-C43
claim. DL-102 turn-timeout and truncation are now implemented B candidates;
DL-103 current-route schema assessment remains separate.

Actual delta: {"bin/_common.py": {"added": 1, "deleted": 1}, "bin/antigravity_wrapper.py": {"added": 6, "deleted": 0}, "README.md": {"added": 6, "deleted": 0}, "README.ko.md": {"added": 6, "deleted": 0}, "tests/test_agy_answer_truncation.py": {"added": 120, "deleted": 0}, "tests/test_distribution_contract.py": {"added": 1, "deleted": 1}}

Owner-authorized accumulated implementation checkpoint pushed: 060edf183cc2d400ade6c86ec386313ed7043e05.
