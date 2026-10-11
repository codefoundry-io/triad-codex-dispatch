# U3a — Same-run AGY finish recovery implementation plan

> Execute inline using superpowers:executing-plans and test-driven-development.
> Fresh dedicated source executors verify RED/GREEN; required four-family review
> follows. Preserve the existing worktree and intentional dirty changes.

**Goal:** Keep a valid corrected submission from the same AGY run under DL-113.
**Architecture:** Add a bounded ERROR-admission predicate to the existing stream
interpreter, then use its existing verdict/schema/binding path. No normal-run
read audit or new retry/dispatch mechanism. Boundary questions below must be
resolved before dependent code; do not silently expand this into A's full census.
**Tech stack:** Python3.12+, pytest, existing AGY stream-json interpreter.
**Spec:** R-CONTAIN/R-CLASSIFY, C23, DL-113 and shared
`decisions/2026-10-10-agy-resubmission-evidence.md`.

## Basis and scope

Main3afc4d7 freshly fetched; B632f426 plus current candidate; read-only A
1ea9cb3e343dd8b492911e247219d169ec33c84b. A reply6092107935 resolved the
boundaries; sharedf332ab8 is the normative clarification. No current native leg changes.

Files: bin/antigravity_wrapper.py, tests/test_agy_finish_resubmission.py,
README.md and README.ko.md. Existing v2 wrapper/producer tests are regressions.
Provisional estimate: production+60-110/-0-5(net+55-110), novel core60-100;
tests+180-280, docs+10-20. Two bounded helpers: measured denial-head recognition
and ERROR-only finish recovery; a web flag carries the already bound profile.
One result event and stream ordering keep recovery within one submitted stream;
terminal tool updates resolve ACTIVE only with the same integer index/name.
No normal SUCCESS census, source-path accounting or full A admission port.

Preserve auth, timeout, input/output transport, current nonzero-exit classification
unless a shared rule explicitly resolves otherwise, route checks, schema/full
verdict binding, ordinary success and existing post-completion denial admission.
Use the final result carrier already handled by B. Do not reconstruct an answer
from guessed finish fields or replay a different provider conversation.

## Review focus

- A later valid finish rescues an earlier failed finish; reversed/missing success
  and a tool-typed finish/DONE alone do not count.
- Read-blind or other executed/errored non-read work is not hidden by recovery.
- Web permission comes from the bound profile; a diagnostic path list is not a
  new per-file review boundary or a full proof of read coverage.
- Denied-before-execution versus executed tools must use an evidenced contract;
  generic TOOL_ERROR is not a denial discriminator.
- Recovery must still reach existing auth/transport/model/schema/binding guards.

## Steps

- [x] Check PR13, current A/B source and the existing measured evidence.
  No new A reply; no inline review comments. Original September raw log absent;
  successful finish shape and generic denial error type directly inspected.
- [x] Characterize current B with constructed provider-free inputs and a success
  control. ERROR recovery refuses vendor-error65; raw1 refuses unknown1;
  success passes. Source unchanged; exact temporary fixture removed.
  `_runs/spec-plan-20261010/u3/resubmit-characterization.json`.
- [x] Publish shared evidence and request A clarification of structured-only
  recovery versus message-based denial, and nonzero admission scope. Request a
  retained sanitized September capture if available; no paid failure generation.
  Shared8ea84ea; authoring1/1 and182tests pass, clean after push.
  PR13 comment6091931426 records the same revision and questions.
- [x] Resolve scope and record explicit success/negative axes in existing C23,
  updating normative wording only where necessary. Ask the owner only if a
  substantive design choice remains; missing raw evidence alone is not a choice.
  A reply6092107935 agrees: measured denial-head predicate is separate from
  structured finish success/order; B keeps its nonzero classifier path. Raw
  September capture expired. Sharedf332ab8 clarifies R-CONTAIN/C23 and passes
  authoring1/1 +182tests; PR13reply6092152745. No owner design question remains.
  U3b all-four SAFE/integrity/cleanup completed; sharedeb78ca9 and PR13comment6092244826.
- [x] Write bounded tests and preserve pre-unit bytes; fresh dedicated executor
  observes RED against the canonical source. Characterization is not formal RED.
  Fresh RED12failed/444passed/4skipped: missing recovery and downstream validation.
  Source/status/logs unchanged; exact temporary tree removed. Constructed inputs.
- [x] Implement the smallest admission correction under the settled boundary.
  ERROR-only predicate, measured denial-head helper, existing terminal validation
  reused and bound web flag forwarded by main. EN/KO behavior documented.
- [x] Fresh dedicated GREEN: complete affected AGY/wrapper/producer/replay suites,
  applicable source validators and relevant regression. Use child-only log/TMPDIR
  roots before imports and exact cleanup. No provider inference in those tests.
- [x] Complete required independent review, adjudicate concrete findings, export
  custody and clean exact temporary review roots; publish verified shared evidence.

Every Python/test/Git-GH mutation uses /bin/zsh -lic with require_escalated from
the workspace host cwd. No installation, merge, release or whole-task hook removal.

First GREEN:456passed/4skipped/2failed from incorrect schema-fail4 test expectations; existing B contract is66. Tests corrected, production unchanged.


Final fresh dedicated GREEN: affected458passed/4skipped; full2213passed/4skipped;
four source validators passed on macOS26.6.2 arm64/Python3.12.13/pytest9.0.3.
Five source/skill hashes, HEAD/full status and ten preexisting source logs were
unchanged. Exact temporary root removed. No live vendor failure recreation or
Ubuntu run. U3b all-four review remains separate prior-unit evidence.

Actual bounded delta: {"bin/antigravity_wrapper.py": {"added": 75, "removed": 1}, "tests/test_agy_finish_resubmission.py": {"added": 194, "removed": 0}, "README.md": {"added": 8, "removed": 0}, "README.ko.md": {"added": 7, "removed": 0}}.


## B candidate implementation and verification

B632f426 plus its preserved candidate implements the resolved DL-113 boundary.
bin/antigravity_wrapper.py adds an ERROR-only recovery predicate and the measured
denial-head helper; main forwards its already bound web flag. Existing final
structured_output validation, original JSON checks, model/review binding,
auth/host-timeout/transport priority and nonzero classification remain. No normal
SUCCESS census, per-file read audit, new retry or A's broader admission port.
Production delta75added/1removed; tests194added; EN/KO docs15added.

Fresh dedicated RED12failed/444passed/4skipped. First GREEN456passed/4skipped/2failed
found incorrect test expectations for schema-fail (B's established exit is66,
not4); those expectations alone were corrected. Final fresh GREEN458affected
and2213full tests passed/4skipped, four source validators passed. Five measured
hashes, HEAD/status and ten existing logs unchanged; exact fixture removed.
Platform macOS26.6.2 arm64/Python3.12.13/pytest9.0.3. Ubuntu NOT RUN; constructed
contract cases, not a fresh AGY failure capture. Main's bound web-profile
positive/negative behavior is covered by the real wrapper path with fake provider.

Independent review triad-agy-finish-resubmission-20261010-r1: all selected legs
SAFE (Claude opus/xhigh, AGY Pro/high, AGY Flash/high, fresh Codex Astra/high),
ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK. Digest
350ee9e1da26abf02c9ce0d5d56bfe6667eac0e8c572e92b2d36857d881d8ee3;
fingerprint1698369b4d63888828a330d01fb4a2e6585f819d97062f51245875b7be7fe4ec.
Custody exported, exact stage/cwd removed. Current A1ea9cb3e source was read;
A's native leg, implementation and tests remain A-owned. No installation,
merge, release, full C23 conformance or whole-revision adoption is claimed.
