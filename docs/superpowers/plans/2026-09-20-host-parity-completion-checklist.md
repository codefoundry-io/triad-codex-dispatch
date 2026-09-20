# Host B completion checklist

This is the local execution record for the remaining parity work. A schema file,
unit test or successful process exit alone does not close a runtime obligation.
Keep implementation, deterministic verification, live evidence, review, adoption
and release separate. Unchecked items are unfinished, not implicitly waived.

## Baseline and settled decisions

- [x] Confirm B checkout and common Git directory; preserve the dirty common checkout.
  B starts at `ce68780e8a29cb7455dbc94e660486fcea8c0679`, branch
  `codex/agy-web-evidence`; Claude A remains read-only at `92c8afd`.
- [x] Fetch shared remote main: `2eb883fee59e66556ee7c7f87189b38231136622`.
  Shared authoring candidate: `6bef14c0c42a13678594e8f2f039d1793b7cb127`.
  Candidate publication does not change an installed host's adopted revision.
- [x] Retain D-B1 host-specific Gemini profiles where usage differs.
- [x] Retain D-B2 masking/failure logs; no new permanent web evidence store.
- [x] Use D-5 project override path `.agents/triad-review-legs.json`.
- [x] Preserve the legacy development gate. Public v2 is explicit and cannot
  admit converted legacy results. Native Codex stays native; dormant hooks stay dormant.
- [ ] Re-fetch main before common changes and final review; record new SHAs here.

Current status refresh: B implementation HEAD `8f12bd58e401d061ba4a9bc889791e24718fb915`;
remote B main `56f0f6657084f81516217ee51698f9b18cfc71dc`. Shared main re-fetched
at `2eb883fee59e66556ee7c7f87189b38231136622`; authoring candidate before this
documentation refresh is `11582b0f6fe6cc6bd292cbb90dfd07dab452ed75`.
P1, P2 and P4 are implemented and reviewed on the B feature branch. P3 is local
work in progress; the producer adapter is not wired into operational review.
This refresh changes no production behavior, adoption or installation.

## Case coverage and completion evidence

`BASELINE` means existing source/test evidence; retain it in the final regression.
`OPEN` means runtime integration or verification is still missing. The detailed
baseline and source/test pointers are in shared
`spikes/2026-09-20-b-contract-implementation-audit.md` at the candidate above.

| Cases | Required outcome | Baseline | Closure evidence to add |
|---|---|---|---|
| C1 | Terminal child/readers/stdin, including catchable parent SIGTERM/SIGHUP | IMPLEMENTED: provider-collection signal omission repaired | `test_parent_signals.py`; macOS 1367 / Ubuntu 1365+2 skips; four-leg r2 SAFE |
| C2, C6 | Partial setup and guard-release failure custody | BASELINE: terminal/provider/stream tests | Full macOS and Ubuntu regressions |
| C3–C5, C7 | Age floor, proven ownership, export before cleanup, safe resume | BASELINE: log/cleanup custody tests | Full regressions; owned cleanup proof |
| C8 | Shared exit vocabulary and explicit exceptions | BASELINE: exit-token contract tests | No producer drift |
| C9, C10 | Actual native/CLI transport object in audit, failure IPC and v2 collection | PARTIAL: P1 CLI emission verified | P3 native receipt and per-entry/attempt collection; retain existing CLI tests |
| C11, C17 | Route-specific environment scrub | BASELINE: provider/diagnostic tests | Actual adapter env regression; no credential inspection |
| C12 | Three defaults, merge-by-name, discovery, validation and displayed enabled roster | PARTIAL: P2 resolver/display verified | P3 preparation and execution must consume resolved entries and capabilities |
| C13, C14, C30 | v2 producers, prompt, six bindings and admission switch together | PARTIAL: offline validator; local producer draft unwired | End-to-end v2 and legacy isolation; original duplicate rejection |
| C15 | REVIEW no-web on every route, preserving B policy protections | P4 IMPLEMENTED: exact separate B policy and route tests | Live B1–B3 and A V1–V5 remain NOT RUN; source equality is not live policy proof |
| C16 | Version/capability/auth boundary before dispatch | BASELINE partial | Preserve checks; actual principal/effective policy remains unverified unless observed |
| C18, C22 | Roster model/effort reaches native/CLI; Google Pro/high defaults | OPEN | Route catalog/argv/native matrix; unsupported values fail before inference |
| C19 | Same-basis failed-entry retry with immutable attempt custody | OPEN | Attempt 2 retains siblings; negative verdict is not retryable transport |
| C20 | Every changed condition forces full scope; previous findings fenced to all | PARTIAL: condition digest and capture/verify implemented | Full v2 roster/condition binding; complete residual delivery |
| C21, C23 | All N entries count, family coverage separate, same-family custody exclusive | OPEN | Informational blocker, missing result, swapped result/read audit tests |
| C24 | macOS and Ubuntu 24.04 outcomes recorded independently | BASELINE per prior slice | New complete suite on both; unrun service checks explicit |
| C25 | Raw custom prompt/schema/model/web/authorized roots survive | P4 VERIFIED: route preservation and extra roots | Retain route matrix through P3; no mandatory investigation envelope |
| C26, C27 | No-follow link text; selected route/binary/version frozen | BASELINE | Full regression and v2 consumer binding |
| C28 | Entry-cwd relative paths, checks and masked success path evidence | P4 VERIFIED: loader, evidence and masking | Retain success/refusal/vanished-cwd tests; accepted diagnostic limits below |
| C29 | Explicit Google investigation appends clause last; fetch evidence is qualified | P4 VERIFIED: both triggers; non-fatal AGY known issue | Incomplete source evidence remains incomplete/UNSURE where relevant; independent dispatch failures retain existing handling |

## Dependency-ordered functional plans

### P1 — CLI transport evidence

- [x] Inspect A counterparts: A `_common.py:925-978` has separate version/stdin
  fields, not the common object. Preserve current masking/retry/error contracts.
- [x] Write focused C9/C10 failing tests; fresh dedicated Terra/high RED: 10
  intended failures. Added Gemini version consumer RED: 1 intended failure.
- [x] Implement common CLI transport observations using
  existing result/audit/run-log surfaces. No second logging subsystem.
- [x] Initial dedicated GREEN: macOS 1359 passed; Ubuntu 1357 passed, 2 existing
  filesystem skips. Validator/lifecycle passed with unchanged source.
- [x] Initial four-leg review `triad-b-transport-r1`: all four valid NOT-SAFE,
  matching integrity. All identify the pre-existing C1 signal omission.
- [x] Add actual parent-signal and ownership-boundary tests. Dedicated RED:
  7 failed/1 passed; the leader found the last test could accidentally pass on
  its own caught assertion, corrected it, and observed all 8 fail before repair.
- [x] Add scoped signal capture, existing group/reader cleanup, restored handlers
  and cancellation rejection. Preserve KeyboardInterrupt and timeout behavior.
- [x] Fresh dedicated GREEN: 60 focused / 1367 full macOS tests; validator and
  lifecycle pass, exact source/status unchanged. Ubuntu 24.04: 1365 passed,
  two existing filesystem skips. Evidence: workspace
  `_runs/infra/20260920-transport-contract/green-c1` and `ubuntu-c1.log`.
- [x] Fresh complete four-leg `triad-b-transport-r2`: all SAFE,
  `ADMITTED_SAFE`, matching integrity. Digest
  `043ca1eea255d29245485225b73f55f9f5986451efef8a5425fd4da1b1ccaeca`.
  Evidence retained and owned staging/custody cleaned. Claude's Minor signal
  checkpoint window is after provider collection (no orphan); recorded without
  broadening the guarantee. Internal capacity/schema retries are not the
  contract's per-leg invocation counter; actual v2 attempt binding remains P3.

Verification history: focused 11 passed. Initial Ubuntu run: 1356 passed,
2 filesystem skips, 1 documentation guard failure because a new link label
contained a retired generic phrase. Changed only that label to "receipt schema".
The first macOS full run lost its terminal tool result: count/exit UNEXPOSED,
not a pass; its process terminated. Skill validator and provider-free lifecycle
passed with unchanged source. A fresh executor will use task-local command logs
and durable terminal receipts for the corrected bytes (results above). One earlier Ubuntu shell
failed before Docker started because its output directory did not yet exist;
that is a preparation error, not a test or provider result.

Budget: approximately +130/-15 production lines, 110 novel core; about 310 test
lines. Surfaces: `_common.py`, Google wrappers/preflight receipt, transport tests
and affected public documentation. Growth closes the already required C1
catchable-signal gap and adds actual signal/ownership tests; no new supervisor
or logging system is introduced. Native receipt collection is completed with
P3's consumer; C28 masked-path wording and implementation belong to P4 with D-B2.

### P2 — Resolved roster and provider-free display

- [x] Read actual catalogs/help and A roster handling; ship three concrete default
  entries in `contracts/review-legs.default.json`. AGY 1.2.7's catalog confirms
  Pro-high; Gemini 0.60.0 source confirms the requested Pro HIGH default, not
  effective account identity. Claude 2.1.271's documented session-only `/model`
  route distinguishes a valid selection from not-found despite both exiting 0.
- [x] Test discovery, merge, strict shape, placeholders, disabled entries and
  displayed enabled roster. Invalid or unreadable configured data must refuse.
- [x] Implement `review_round.py resolve-roster --project-root PATH` using the
  canonical schema and a host data file. This command never starts a provider;
  its output is resolved configuration, not a capability or admission receipt.
- [x] Fresh RED/GREEN and complete plan review before the next implementation plan.
  Dedicated GREEN: 96 focused / 1393 full macOS tests; Ubuntu 24.04:
  1391 passed and two existing filesystem skips. `triad-b-roster-r1`: all four
  SAFE, `ADMITTED_SAFE`; integrity verified and owned custody cleaned.
  Published B commit: `7cc70a73c72ef9106e7c963bafed24cbbf623a5a`.

Dedicated RED: 26 failures at the missing resolver command; root GREEN: all 26
pass. A separate dedicated distribution RED confirms the two new payloads were
missing from archive hash coverage; the bounded hash-list correction adds them.
No provider inference is performed by the resolver. The actual adapter and full
v2 consumer remain open, so this does not close C12 end-to-end.

Budget: approximately +150/-0 production lines, 120 novel core; about 220 test
lines. Reuse canonical schemas and strict file/JSON loading. A's v1 additional-leg
loader is at `.claude/skills/triad-cross-family-review/lib/review_scratch.py:2618`;
B's v2 includes the default entries and uses the owner-selected project path.
The executable adapter boundary moves with the complete P3 wire/consumer switch:
P2 is an independently useful configuration check, never partial v2 dispatch.

### P3 — Operational public v2 collection and retry

- [ ] Switch v2 renderer, wrapper producer boundary and validator together;
  preserve an explicit legacy entry point.
- [ ] Consume the P2 roster in preparation/dispatch; show exact native/wrapper
  arguments, verify supported route/model/effort before inference, and preserve
  the authentication selector and independent AGY/Gemini model blocks.
- [ ] Bind named entries/attempt/route, immutable result/read-evidence locations,
  actual transport, complete roster and source/toolkit integrity.
- [ ] Implement same-basis failed-entry retry and full changed-basis re-review
  with previous findings/rebuttals fenced as data for every entry.
- [ ] Test all N-entry agreement outcomes and legacy/v2 isolation; fresh RED/GREEN,
  full suites and complete plan review.

Budget: approximately +1000/-60 production lines, 500 novel core; about 600 test
lines. The refined estimate includes the actual producer/consumer and exclusive
attempt custody, not only schemas. This is one cohesive wire/consumer transition;
size is a planning guide. Execute P4 first because these consumers reuse the
completed policy and investigation boundaries.

### P4 — Google policy and investigation completion

- [x] Isolate AGY page truncation with primary sources and controlled usage spikes:
  a 158-byte official file is persisted as a 148-byte strict prefix with and
  without plan mode. The provider artifact is already short before B collection.
  No verified AGY CLI truncation control was found; exact internal cause remains
  unexposed. Retain the external limitation, not a false fixed claim.
- [x] Publish the D-B1/D-B2 contract wording and same-commit Claude review request
  before implementing any changed common behavior.
  Shared commit `6f0f2746f0bd74e16cf6df7c9ee5e0750d42d7d5`, PR 1 comment
  `5748274863`. `triad-shared-v2-policy-r2`: all four SAFE, `ADMITTED_SAFE`;
  80 contract checks passed on macOS and Ubuntu. Remote main remained
  `2eb883fee59e66556ee7c7f87189b38231136622`. Candidate publication is not adoption.
- [x] Preserve separate Gemini policy profiles, enforce REVIEW no-web, implement
  explicit Gemini investigation clause and authorized read-root propagation.
- [x] Fresh RED/GREEN, complete review and platform checks. Leave unavailable
  authenticated Gemini V1–V5 evidence NOT RUN; do not relabel a stub as a service run.
  B commit `8f12bd58e401d061ba4a9bc889791e24718fb915`; dedicated final GREEN:
  108 focused and 1429 full macOS tests. Ubuntu 24.04, unprivileged uid 65534:
  1427 passed, two existing filesystem skips. `triad-b-p4-r1`: four SAFE,
  `ADMITTED_SAFE`, matching integrity, exact owned cleanup. Digest
  `3b3f3414f05714417dd73d6d2ea600eabd19bfec12a06c305441e138fdcc3209`.
  Minor diagnostic limitations on the unchanged reviewed bytes: invalid extra
  directory refusal may display entry cwd as its candidate; a missing required
  jsonschema dependency in Gemini provenance parsing exits 1 rather than 3.
  Both refuse before inference and preserve masking. No unnecessary reader/path
  abstraction was added. Leader disposition is retained in workspace
  `_runs/infra/20260920-transport-contract/p4-review-adjudication.md`.
- [ ] Resolve the AGY 1.2.7 changelog/runtime discrepancy before claiming search
  compatibility. The release note says default legacy search tools were retired;
  diagnostic init events still advertise them. An exact fixture view succeeded,
  but the model skipped the requested grep call: its unsupported-tool prose is
  not a tool failure. Current evidence does not establish a functional defect.
  A explicitly lists these tools in a custom agent. Preserve current routing;
  any shared Google-clause change needs publication and same-commit Claude review.

Dedicated P4 RED: 17 failures / 4 passes across missing success-path evidence,
masked refusal paths, extra-root forwarding, Gemini web trigger and B policy.
Leader checks additionally exposed a schema-output suffix after the required
Gemini web clause; the final-clause fix must cover the first and schema-repair
attempt. The GitHub blob representation also produced the same 148-byte prefix
as raw (29.4 s, provider/wrapper 0/0); this remains an external incomplete-body
observation, not a repaired provider behavior.

Cross-site evidence: Python.org robots.txt also yielded a strict prefix,
297/536 normalized characters (239 trailing characters omitted); IANA robots.txt
23/23 and RFC 20 18497/18497 were complete. Direct bytes before/after matched
for every URL. A fresh native independent audit confirmed the comparisons.
This excludes a GitHub-only explanation and a universal small fixed cutoff;
it does not identify the provider's internal component. Task-scoped artifacts
are retained in workspace `_runs/infra/20260920-agy-web-evidence/`.

- [x] Record `KI-AGY-URL-BODY-PREFIX` as a non-fatal external known issue under
  the owner's instruction. Shared disposition commit
  `11582b0f6fe6cc6bd292cbb90dfd07dab452ed75`, PR 1 comment `5748658935`.
  The observed body loss alone is neither an implementation failure nor an
  automatic repair/retry trigger. Existing successful exits are unchanged;
  incomplete evidence and independent dispatch failures retain their meaning.
  No new log, retention policy, provider workaround or vendor-fix claim is added.

Budget: approximately +210/-60 production lines, 150 novel core; about 220 test
lines. A vendor defect or a design change is a diagnosis/owner boundary, not a
reason to invent a fetch service, SDK migration or global setting.

## Final anti-omission gate

- [ ] For every C1–C30 row, record actual production consumer and named tests.
- [ ] Reconcile rules, prompts, contracts and units beyond the numbered cases.
- [ ] Sequential independent native audits; leader verifies findings in source.
- [ ] Complete combined integration review on identical final bytes.
- [ ] Record platform outcomes, source/archive equality and exact remaining limits.
- [ ] Update Claude handoff with A/B source lines, preserved behavior, changed
  contract commit, migration steps and unrun checks. Do not edit Claude host.
- [ ] Do not claim merge, tag, installation or deployment without those distinct
  authorized operations and their evidence.
