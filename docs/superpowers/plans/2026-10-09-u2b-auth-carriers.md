# U2b — Authentication error carriers

> Use superpowers:executing-plans and the dedicated source executor for RED/GREEN.

**Goal:** Preserve the authentication STOP from measured vendor error carriers,
without interpreting quoted answer/tool text as an authentication failure.

**Architecture:** One carrier predicate in `_common.py`, used before failed-run
classification and at transport/signal boundaries. Extractor promotions retain
the original stdout/stderr. The AGY interpreter checks authentication separately
from diagnostic text, retaining its existing non-authentication classifications.

**Tech Stack:** Python 3.12+, pytest, existing wrapper subprocess engine.

**Spec:** Shared PR13 b085a6e `reference/review-rules.md#R-CLASSIFY`, R-AUTH,
C37/C43 and `contracts/vendor-failure-lines.json`; main 3afc4d7 unchanged.

## Constraints and measured basis

- Preserve the dirty existing worktree, host-native legs, CLI versions and settings.
- Codex: JSONL error.message / turn.failed.error.message; own configuration-error
  stderr prefix. Shared rows cite Codex source and observed 401/refresh failures.
- Claude: is_error envelope status 401 or result text; non-null structured_output
  remains the answer. Shared rows cite captured login/API-key failures. A has no
  Claude CLI route and cannot certify B's extractor integration.
- Gemini: stdout error object / trailing stderr error envelope, codes 41/401,
  cached-credentials prefix. Tool-error message excluded; code still authoritative.
  Shared source evidence is v0.60.0; raw code 41 also verified in v0.63.0 in U2a.
- AGY: terminal result.error and own stderr banner, signed-out 1.3.1 capture.
  Schema-validation reports may reflect model text: only a banner line counts.
- A `_auth_carrier_stop` at 0e04d2a is implementation evidence, not authority.
- No unmeasured AGY credit carrier, nested-field expansion, global installs or
  live logout/credit-exhaustion tests. Fixtures are contract cases, not captures.
- Remove raw authentication matching, ignore obsolete raw-auth extensions with
  a diagnostic and refuse new raw-auth patch proposals. General extension
  validation, other phrase lists, environment scrub and general exception guards
  remain later units; this unit does not claim whole-C37 conformance.

## Scope and size

Production: `_common.py`, `claude_wrapper.py`, `antigravity_wrapper.py`;
estimate +220/-80, net +140, novel core below 200 lines. Tests about +280/-5:
new `test_auth_carriers.py`, retained U2a real-child cases and the conflicting
AGY diagnostic control. Paired README/security notes and plan/SoT are separate.

## Task 1: Preserve carrier provenance through failed-call handling

Interface: `_auth_carrier_stop(cli, stderr, stdout, vendor_exit_code=None) -> bool`.
Consumes actual captured streams; never a synthesized extraction-error string.
Callers establish failed/no-answer context, preserving completed usable answers.

- [x] Author classifier positive/negative controls, real-child wrapper tests,
  timeout/late-signal cases and raw-auth-extension refusal; fresh executor RED.
- [x] Implement carrier predicate, precedence and raw input preservation. Fix the
  retained outdated exit-map/layer comments. Keep capacity retry behavior intact.
- [x] Fresh executor GREEN: new cases, complete provider/Claude/AGY/signal/patch
  modules, both validators, full suite once. Isolate actual log globals and disable
  unrelated stale temporary cleanup in every new subprocess test fixture.
- [x] Fresh full-scope Claude/AGY Pro/AGY Flash/native Astra formal review;
  collect all terminal results, integrity, adjudication, exact-stage cleanup.
- [x] Publish bounded evidence to shared PR13 and update SoT. Do not mark C37
  complete while environment and other open requirements remain.

## Review focus / tests

Authentication plus capacity/timeout must STOP without retry; usable success must
survive authentication quotations; carrier fields must not expand to tool output;
malformed ordinary JSON types must not crash classification; late signal and
transport failure must withhold answers without erasing observed authentication.
Include the two U2a retained engine cases: capacity stderr + raw 41, and a child
that exits 41 from SIGTERM after the actual timeout boundary.

## Ledger

Pre-flight: shared predicate feeds engine, signal boundary and wrapper extraction;
all must use original streams. AGY non-auth error text stays diagnostic-only.
Ruling: use the existing project evidence/SoT lifecycle and guarded dirty checkout;
do not create a separating worktree or commit unrelated pending work.

Dedicated RED: 39 failed, 34 passed; seven hashes, HEAD and status unchanged.
Leader initial smoke after implementation: 70 passed, three control expectations
were too broad. Ruling: schema-report controls assert the existing schema-rejected
classification rather than unknown, because this unit removes raw authentication
matching only; the separate generic non-auth phrase cleanup remains pending.
Strengthened precedence fixtures to use actual recognized capacity tokens.
Leader focused verification then passed 281 cases. Dedicated GREEN follows final
comment cleanup and the stronger Claude capacity fixture, on frozen bytes.

R1: dedicated focused 423 passed/4 skipped, full 1991 passed/4 skipped, both
validators and stable hashes. Formal review NOT_APPROVED with matching integrity:
three reproduced regressions (AGY no-answer guard, reflected denied command,
Claude non-auth input widening). Fresh correction RED 11 failed/1 passed. C74
clarification published before correction (shared dd85b52), A review requested.
Corrected source passes leader focused 293 cases; fresh GREEN and R2 follow.
Ruling: these corrections preserve the settled tool-text exclusion and existing
admission, not a new vendor shape or native mechanism. General typed exit-code
extension validation remains separate from removal of raw-auth phrase extensions.

R2: focused435/full2003passed with4skips, validators and stable hashes; three SAFE,
Claude NOT-SAFE. Fresh RED2failed/4passed confirmed denied-command text was still
scanned for a banner. C74 clarified at shared d5c5756 before correction: skip the
entire denied-command error; retain only the separately measured own-stderr and
schema-report banner carriers. No full-command vendor capture is claimed.
Deferred Minor: Gemini's derived-error fallback can re-enter auth parsing only
on an unmeasured exit-zero error envelope. Record the limit; revisit with measured
evidence or planned classifier cleanup. No speculative parser expansion.

Final R3: focused437/full2005 passed with4skips, both validators and stable
hashes/HEAD/status. Four SAFE, ROUND_INTEGRITY_OK, ALL_SELECTED_APPROVED;
all terminal results collected, custody exported, exact stage/cwd cleanup done.
Shared evidence published at b8512b6 in draft PR13, 182 shared tests and
authoring check passed. No full C37/C43, A runtime result or release claim.
Final executor's instruction/memory-read disclosure limits blinded behavior
claims, not the recorded deterministic test outcomes. Next unit: U2c environment
name-set parity mapping, before any new implementation. See live SoT.
