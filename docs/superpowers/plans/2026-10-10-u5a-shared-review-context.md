# U5a — shared review clauses and frozen preparation date

Approved roadmap U5, R-CONTEXT/R-PREPARE/R-AGREE, DL-45/46/56/61/93.
Current B emits the old pinned candidate clauses, has no review_date in its
bound basis, hard-codes no-web text and identifies A-only clauses by names.
Shared ca3d990a107b24644fddcf6978a9655f8e106d4f supplies the settled clauses.

Outcome: all v2 legs receive the same common context/date from one exact pinned
bundle. Preparation captures UTC YYYY-MM-DD once into the hashed basis; render
and retry consume it without a new clock read. Existing basis integrity detects
changed date inputs. Render no-web from its clause file and honor A-only header
markers; keep native dispatch, model/effort, web authorization and containment
unchanged. This is source candidate alignment, not installed revision adoption.

Files: review_prompts_v2.py, review_round_v2.py, the four prompt payloads and
manifest; focused renderer/custody tests; public-v2 review guidance, AGY skill
telemetry qualifier and EN/KO README exit64 clarification already queued by U3.
Estimated production +35-50/-5-15 (net +20-45), novel core <=35 lines;
tests +80-130, payload/docs +50-90. No new public CLI or result schema field.

- [x] Preserve pre-unit bytes; add date/leg-context and retry/integrity controls.
  Fresh dedicated executor verifies RED without providers or source edits.
- [x] Vendor exact four shared payloads and provenance; implement the bounded
  date/renderer changes and factual guidance. No hand-rewording shared clauses.
- [x] Fresh dedicated GREEN: focused renderer/round/wrapper tests, full suite,
  four validators, unchanged source/log hashes and exact temporary cleanup.
- [x] Complete independent Claude/AGY Pro/AGY Flash/fresh Codex review on one
  current basis, adjudicate real defects, verify integrity and exact cleanup.
- [ ] Record shared/SoT evidence and push the authorized candidate checkpoint.

Commands: /bin/zsh -lic, require_escalated, outer workspace cwd. Keep the
existing checkout and unrelated files. Owner reviews prompt wording later;
if review stalls on nuance, use the established bounded fresh scenario protocol.
U5 standing-web/default policy and remaining U2/U6/U7/U9 assessment remain separate.

Fresh dedicated RED:9failed/288passed/4skipped,124.30s. Missing prepared date,
six family/web context paths and renamed A-only clause reproduced; controls pass.
Fourteen source hashes,HEAD/status and source logs unchanged; exact fixture removed.
The common-clause expectation now reads the fenced payload independently of the
production parser; this preserves the same expected clause transport behavior.

Initial GREEN:6failed/291passed/4skipped. Six existing authorization cases pinned
the previous web-permission sentence; shared exact clause wording changed.
The legacy renderer also uses the common helper, so this wording reaches both
legacy and v2 authorized paths. Updated expectations independently extract the
shared fenced payload; all argv, authorization, digest and retry checks remain.
No production change for this failure. Fresh GREEN follows with fifteen hashes.

U5a R1 NOT_APPROVED, integrity matched: one verified stale no-web reference,
one unused constant and missing upstream-hash evidence in the review packet.
Updated reference, removed dead constant/test-only replacement, and computed
exact upstream git-show hashes for R2. Default authorization stays false; both
legacy and v2 use the shared no-web wording. R1 evidence exported/cleaned.
Fresh GREEN-r2 and complete R2 follow; no new shared design.

U5a R2 NOT_APPROVED, integrity matched: simulated UTC2026-10-11 reproduced
a wall-clock-dependent test (1failed). Fixed only the test using its existing
PreparationClock and a changed-value assertion; same probe now1passed.
Production/docs unchanged from full GREEN-r2(2273/4). Fresh dedicated affected
GREEN-r3 and four validators follow, then complete R3. R2 optional parser
refactor is nonblocking and not added; no new design or runtime change.

# B shared v2 review context — U5a

2026-10-10, B179c7af plus bounded candidate; exact shared payloads copied from
ca3d990a107b24644fddcf6978a9655f8e106d4f, source manifest/hash checks retained.

DL-45: both web/no-web clauses are rendered from the common clause file. A-only
clauses are excluded through their header marker, not a historical name list.
The legacy renderer also consumes this shared helper for both web policies; permission
flags and authorization/digest controls retain their existing behavior.
DL-46: UTC preparation date is captured once inside the existing hashed basis;
all render/retry paths use that date. Date changes fail existing custody checks.
DL-56/93: all v2 legs receive the exact shared deployment/measured-shape context.
DL-61: public v2 guidance says to collect again before relying on AGREED when an
earlier retried leg may still be running. No new synchronization is claimed.

Native spawn/model/effort, explicit web authorization, wrapper containment and
public result schema remain unchanged. This is candidate prompt integration,
not adopted SPEC_REVISION, installation, merge or release. U5's standing-web
policy assessment (DL-39) stays separate; no native-leg port follows.

Read-only A7dbba148b75cda907f2609731c8b68d2936595ca corroborates date capture at
.claude/skills/triad-cross-family-review/lib/review_scratch.py:1952 and reuse
at:2739; lib/prompts_v2.py:399-427 validates date, resolves common web clauses
and applies host markers. A tests were not rerun. A's hook/raw-reply behavior
remains its own implementation; this unit requests no A code change.

Fresh dedicated RED9failed/288passed/4skipped. Fresh GREEN-r3 297 affected
passed,4skipped; four source skill validators passed. Full GREEN-r2 previously
passed 2273 tests,4 skipped on identical production/docs. Only the
clock fixture test differs afterward; source hashes confirm this boundary.
Initial GREEN retained six stale literal assertions (291passed/4skipped); their
expectations now independently extract the pinned shared clause. No production
change was made for that test-only correction.
macOS26.6.2 arm64/Python3.12.13/pytest9.0.3; Ubuntu NOT RUN. Seventeen source/skill
hashes,HEAD/full status and preexisting source logs unchanged; exact fixture
removed. Tests exercise real renderer/basis/retry/collector behavior with vendor
execution replaced, not live model-choice claims or a wording-quality benchmark.

Review triad-shared-review-context-20261010-r3: all four selected independent
reviewers SAFE, matching ROUND_INTEGRITY_OK. Digest 67725e8bd8b65a2c65af526dc40bcadd47391aa72b7aeb5cea632360b598a158.
R1 was NOT_APPROVED: a stale review-web reference, dead no-web constant and
missing upstream-byte evidence were verified. The reference now describes both
legacy/v2 shared policies and existing uncertainty routing; the unused constant
was removed. R2 binds git-show hashes and byte equality of all four payloads at
the upstream commit. No R1 approval is reused. Default web authorization is still
false; the legacy default clause wording/hash changes with the shared payload.
R2 then found the clock-dependent test: UTC2026-10-11 made the replacement equal
to the original. An actual injected-clock probe reproduced one failure; setting
the existing PreparationClock and asserting changed value fixes it (same probe
one pass). Production/docs were unchanged. R3 is a complete fresh review; no
R2 approval is reused. Its optional parser refactor is not a required change.
Findings and dispositions retained in the round adjudication. Custody exported
and exact temporary launcher stage/cwd removed. Earlier U3 tests/reviews remain
their own evidence; the new result does not certify all C19/C32/C60/C67/C68 axes.

R3 retained two nonblocking source-supported observations: a damaged prompt
bundle on legacy default rendering may fail closed with traceback/exit1 instead
of the handled exit2 diagnostic (no damaged-install runtime probe); the public
mechanical-fields table omits the prepared-date explanation, while runtime/retry
behavior is correct. Both reviewers and leader keep them nonblocking under the
owner three-pass bound. No fourth prompt round or new required backlog is added.

Shared evidence published at885e52e019bad28abef9edcaea1bce4d00f9dbab;
authoring1/1 and182tests pass. Final production +17/-14 (net+3).
Authorized source checkpoint push is next. No install/merge/release.
