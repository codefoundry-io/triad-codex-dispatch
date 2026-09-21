# Host B completion checklist

This is the local execution record frozen as input to the corrected P3 review.
Final review, publication and distribution outcomes are maintained in the
[current verification record](https://github.com/codefoundry-io/triad-dispatch-spec/blob/codex/host-b-preimplementation-audit/decisions/host-b-p3-verification.md).
Pending integration items below describe this review-start snapshot. A schema file,
unit test or successful process exit alone does not close a runtime obligation.
Keep implementation, deterministic verification, live evidence, review, adoption
and release separate. Unchecked items are unfinished, not implicitly waived.

## Internal tracking and final delivery

This Markdown checklist is the internal execution record. Close each feature
only after its production consumer and verification evidence are recorded. Keep
historical findings and run receipts here or in linked evidence; do not delete
them to make the final deliverable appear complete.

The final Claude implementation handoff is a PRD-style specification, without
checkboxes or progress history. It describes the finished functions, interfaces,
input/output contracts, constraints, exceptional behavior, migration requirements
and acceptance criteria. Reconcile every internal obligation against that final
specification before delivery. Explicit external verification limits remain
limits; they are not missing functionality or fabricated passes. Claude-host
source remains read-only while B completes implementation and validation.

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
- [x] Re-fetch main before common changes and final review: `2eb883fee59e66556ee7c7f87189b38231136622`, unchanged.

Corrected review-start snapshot: B baseline HEAD
`3d62b7cc370d2c72fc439a431d5f78ab76875b98`; remote B main
`56f0f6657084f81516217ee51698f9b18cfc71dc`. Shared main was re-fetched
at `2eb883fee59e66556ee7c7f87189b38231136622`; authoring baseline is
`aef3adee863fd90fdfab60ae2253717cf1b4d303`. P1/P2/P4 are published.
P3-F1/F2/F3 are corrected, with new real-wrapper/adapter regressions and clean
dedicated GREEN, now including reserved-input/type refusals: macOS 1631
tests, Ubuntu 1629 plus 2 existing skips.
Native spawn now succeeds. The earlier incomplete formal round remains FAILED;
the new round and final publication are recorded separately after they finish.

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
| C9, C10 | Actual native/CLI transport object in audit, failure IPC and v2 collection | IMPLEMENTED: actual route-specific delivery and runtime observations | `test_v2_round_cli.py`, `test_v2_evidence_custody.py`, `test_v2_review_findings.py`; real Google wrapper-log path passes |
| C11, C17 | Route-specific environment scrub | BASELINE: provider/diagnostic tests | Actual adapter env regression; no credential inspection |
| C12 | Three defaults, merge-by-name, discovery, validation and displayed enabled roster | IMPLEMENTED: schema-valid omitted fields preserve defaults or controlled preparation refusal | `test_v2_adapters.py`, `test_v2_adapter_wrapper_bridge.py`, `test_v2_review_findings.py`; omitted-key/refusal paths pass |
| C13, C14, C30 | v2 producers, prompt, six bindings and admission switch together | LOCAL IMPLEMENTATION: opt-in runtime path connected | `test_v2_producer_adapter.py`, wrapper/round/prompt tests; formal P3 admission pending |
| C15 | REVIEW no-web on every route, preserving B policy protections | P4 IMPLEMENTED: exact separate B policy and route tests | Live B1–B3 and A V1–V5 remain NOT RUN; source equality is not live policy proof |
| C16 | Version/capability/auth boundary before dispatch | BASELINE partial | Preserve checks; actual principal/effective policy remains unverified unless observed |
| C18, C22 | Roster model/effort reaches native/CLI; Google Pro/high defaults | LOCAL IMPLEMENTATION: actual argument/capability adapters | `test_v2_adapters.py`, `test_v2_runtime_boundaries.py`; formal P3 admission pending |
| C19 | Same-basis failed-entry retry with immutable attempt custody | LOCAL IMPLEMENTATION: retry/attempt custody | `test_v2_rounds.py`, `test_v2_round_custody.py`; formal P3 admission pending |
| C20 | Every changed condition forces full scope; previous findings fenced to all | LOCAL IMPLEMENTATION: source/toolkit/roster/conditions and residual bound | `test_v2_review_prompts.py`, `test_v2_toolkit_inputs.py`, round integrity tests; formal P3 admission pending |
| C21, C23 | All N entries count, family coverage separate, same-family custody exclusive | LOCAL IMPLEMENTATION: all-entry collector | Informational blocker, missing/swap tests in `test_v2_rounds.py`; formal P3 admission pending |
| C24 | macOS and Ubuntu 24.04 outcomes recorded independently | VERIFIED: corrected-byte full suites | macOS 1631; Ubuntu 1629 + 2 existing skips; unrun service checks explicit |
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

Current implementation and verification checklist:

- [x] P3-F1: actual AGY/Gemini argv delivery is accepted as `not-used`;
  Claude still requires complete stdin. Real process/wrapper/run-log/collector
  regressions and incomplete-Claude controls cover the boundary.
- [x] P3-F2: schema-valid omitted adapter keys use documented defaults or
  controlled capability refusal with preparation-failure custody. Empty Claude
  selection and absent selected Google blocks refuse before inference.
- [x] P3-F3: v2 Gemini keeps unexposed runtime version null while preserving
  its preflight version separately; legacy semantics remain unchanged.
- [x] Dedicated fresh RED observed 10 failures and five controls before edits.
  A distinct clean-input dedicated GREEN passed 15 focused and 1619 full macOS
  tests, skill validation and provider-free lifecycle, with source unchanged.
  A prior history-bearing executor run is retained only as regression evidence.
- [x] Refuse collector-owned output/metadata/sidecar input names before writes,
  and route malformed v2-create identifier/path types through controlled errors.
  Dedicated fresh RED: 12 intended failures; leader related suite: 56 passed.
  Current clean-input dedicated GREEN: 27 focused / 1631 full macOS,
  validator/lifecycle passed, unchanged source and exact cleanup.
  `test_v2_input_refusals.py` also proves correction within the same attempt.
- [x] Complete r2 with four SAFE results, matching integrity and exact cleanup.
  Two accepted input-handling findings changed the bytes afterwards; r2 is
  historical evidence and cannot admit the current candidate.
- [ ] Complete the new required formal round on these corrected bytes.

Connected feature surfaces:

- [x] Connect canonical schema-backed generation and strict original-JSON validation.
- [x] Connect all three wrapper producer boundaries and native host receipt ingestion.
- [x] Vendor and hash the four shared prompts; consume them in the v2 renderer.
- [x] Consume the named roster in installed-interface capability checks and actual
  native/wrapper invocation allocation, preserving authentication and legacy routes.
- [x] Bind all six verdict fields, original replies, transport and read observations
  to exclusive named-entry/attempt custody; retain failed preparation generations.
- [x] Implement diagnosed unchanged-basis failed-entry retry and changed-basis
  full review with bound prior findings/rebuttals delivered to every enabled entry.
- [x] Count all N entries, including informational entries; preserve legacy/v2
  isolation, independent family coverage, integrity and existing export/cleanup.
- [x] Document the explicit v2 skill procedure within the original instruction budget.
- [x] Obtain clean-input fresh dedicated Terra/high GREEN: 27 focused, 1631 full macOS,
  valid skill and successful provider-free lifecycle; exact source unchanged.
- [x] Verify corrected bytes on Ubuntu 24.04 independently: 1629 passed, 2 existing filesystem
  skips, terminal exit 0 and source unchanged.
- [x] Collect every started CLI in `triad-b-transport-p3-r1`: Claude Opus/xhigh,
  AGY Pro/high and Flash/high all valid terminal results. Claude is NOT-SAFE;
  Pro and Flash are SAFE. Record matching final integrity,
  export evidence and remove only recorded disposable staging/custody.
- [ ] Run a fresh complete formal round with a fresh native reviewer. The P3 r1
  native spawn returned `agent thread limit reached` before creating a handle.
  Its gate is FAILED; no admission carries forward.
- [ ] Commit admitted bytes and verify the clean committed distribution.

Current evidence: workspace `_runs/infra/20260920-transport-contract/p3-input-refusals-green/`,
`p3-input-refusals-red/`, `ubuntu-p3-input-refusals/`. Earlier evidence: `p3-clean-green/`,
`p3-findings-red-r2/`, `ubuntu-p3-findings-r2/`, `p3-implementation-notes.md`, `p3-source-consumer-map.md`
and `p3-case-evidence-map.json`; formal ledger and exported packet are under
`_runs/reviews/triad-b-transport-p3-r1/`. The JSON index covers C1-C30 and every
named test path exists. Neither this index nor deterministic tests claim
authenticated policy enforcement or installed runtime identity.

The leader reproduced P3-F1 on both argv routes using the actual process engine,
and P3-F2 with a schema-valid additional Claude entry plus omitted native fields.
`p3-review-findings-reproduction.json` preserves those results with unchanged
source and fixture cleanup. This diagnosis is not the dedicated RED requirement.
`p3-review-adjudication.md` records the verified scope and A source comparison.

Earlier sequential independent audits were adjudicated against current source. Changed
policy bytes already invalidate retry; failed preparation is not an allocated
provider attempt; native custody uses trusted host observations, not an unavailable
signed host API. Optional AGY project UUID stays on existing legacy/raw paths.
The reproduced runtime-log hash omission was corrected after two dedicated RED
failures: only `bin/_logs` and `bin/_debug` are excluded, while code, policy and
allocated evidence remain bound. Focused toolkit/distribution/instruction checks:
52 passed. The original 125-line / 1600-word skill limits remain intact.

<details>
<summary>Intermediate P3 implementation evidence; the checklist above is current</summary>

- Observe dedicated producer-adapter RED (33 intended failures); implement
  the canonical-backed adapter and verify 33 focused tests locally. This is
  partial work, not the final fresh GREEN or an operational v2 switch.
- Observe fresh wrapper integration RED, then wire complete binding and
  generation-schema handling at actual wrapper boundaries.
  Claude boundary: fresh canonical RED 22 failed; leader implementation passes
  91 focused adapter/wrapper/receipt tests. Evidence is retained under workspace
  `_runs/infra/20260920-transport-contract/claude-v2-red-canonical/`.
  Google, native and round collection remain open; final dedicated GREEN has
  not run for P3.
  Google boundary subsequently observed fresh RED: 24 failed / 2 early-parser
  negative controls passed. After connecting v2 preflight and both wrappers,
  all 81 producer/v2-wrapper tests and 282 affected legacy/investigation tests
  pass in leader runs. The AGY synthetic success fixture was corrected to
  include its existing required structured_output field before implementation;
  no production extractor fallback was introduced. Native and round collection
  remain open. No live service or final dedicated GREEN claim follows.
  Per-attempt evidence: dedicated custody RED observed 10 intended failures and
  one legacy control pass. The bounded wrapper/run-log change passes 92 focused
  v2 tests in the leader run. Raw original replies and all six bindings now
  survive v2 success/failure; ordinary legacy/investigation success logging is
  unchanged. Operational collection and final dedicated GREEN remain open.
- Vendor the four shared v2 prompt payloads from their published commit,
  record exact hashes and exercise their production renderer consumers.
  Exact bytes from `6bef14c0c42a13678594e8f2f039d1793b7cb127` are now staged in
  `prompts/review-v2/` with an adjacent manifest. Fresh prompt RED: 15 intended
  failures. The v2 clause renderer and distribution hash coverage are implemented;
  operational round integration and final certification remain open.
- Switch v2 renderer, wrapper producer boundary and validator together;
  preserve an explicit legacy entry point.
  Operational CLI RED: 12 intended failures, canonical source unchanged.
  The leader connected create/allocate/record/collect commands to native host
  receipts and actual wrapper run logs; original evidence is bound and retained.
  Preparation failures keep their partial receipts in separate generations.
  Combined core/custody/CLI checks: 35 passed in 49.05 s, terminal exit 0.
  These are deterministic tests; source-skill guidance, fresh final GREEN and
  complete formal review are still required before closing P3.
  Independent adapter review found invalid agent-name timing, invalid catalog
  failure custody and pre-validation mkdir side effects. Fresh runtime RED:
  10 intended failures, exact source unchanged. The leader corrected those
  boundaries plus retry-preparation retention, prepared-directory cwd selection
  and unexposed Claude runtime-version collection. An actual fake-vendor
  subprocess exercises the real wrapper/stdin/run-log/collector. Focused checks:
  38 passed in 16.06 s, terminal exit 0. This is not a paid service attestation.
  The source-reference RED independently found that the skill still documented
  only legacy flow. An explicit v2 procedure now supplies generated invocations,
  host receipt shapes, outcome/retry handling and lifecycle reuse; final fresh
  behavior and complete regression verification remain open.
- Consume the P2 roster in preparation/dispatch; show exact native/wrapper
  arguments, verify supported route/model/effort before inference, and preserve
  the authentication selector and independent AGY/Gemini model blocks.
  Fresh adapter RED: 19 failures. The leader implemented native capability
  validation, Claude session-only selection and documented effort checks,
  optional agent forwarding, and Google pinned/unpinned wrapper preflight.
  An actual-wrapper bridge test then exposed two preflight argv errors (family
  belongs to runtime result binding, not preparation); the adapter was corrected
  without weakening either parser. Related tests: 69 passed in 2.97 s.
  Native runtime defaults must be host-observed before freezing a null selection;
  Claude null selection is inspected with `/model`, never reset to `default`.
  This is interface/capability evidence, not account or inference attestation.
  Operational CLI ingestion and final dedicated GREEN remain open.
- Bind named entries/attempt/route, immutable result/read-evidence locations,
  actual transport, complete roster and source/toolkit integrity.
  Round-core RED: the fresh canonical executor observed 17 intended failures
  with unchanged input/source hashes. The leader's additive lifecycle accounting
  implementation passes all 17 tests (30.10 s). Native and CLI allocations,
  all-entry collection, same-basis retry and evidence mutation refusal are
  exercised with an isolated capability-adapter fixture. Actual adapter discovery,
  CLI command integration and final dedicated GREEN remain open; this is not
  operational completion. Evidence: workspace
  `_runs/infra/20260920-transport-contract/round-core-red-canonical/`.
  Follow-up custody RED: 6 intended failures. The leader now retains invalid
  original answers as INVALID evidence, rejects lost prior retry terminals and
  preserves allowed native unexposed stdin observations. Combined round/custody
  suite: 23 passed in 36.12 s, terminal exit 0. This remains partial P3 work.
- Implement same-basis failed-entry retry and full changed-basis re-review
  with previous findings/rebuttals fenced as data for every entry.
- Test all N-entry agreement outcomes and legacy/v2 isolation; fresh RED/GREEN,
  full suites and complete plan review.

</details>

Budget: approximately +1300/-40 production lines, 650 novel core; about 1600 test
lines. Latest measured intermediate delta was +1244/-32 production, +1504/-0
tests and +307/-1 documentation before final procedure text. Growth covers
actual adapter/wrapper/collector boundaries and preparation/receipt regressions,
not an additional scheduler, provider engine or logging subsystem.
The refined estimate includes the actual producer/consumer and exclusive
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

- [x] For every C1–C30 row, record actual production consumer and named tests.
  Internal source/test maps are retained with the task evidence; P3-F1/F2 expose
  previously missing regression scenarios, now covered by the corrected-byte tests above.
- [x] Reconcile rules, prompts, contracts and units beyond the numbered cases.
  Shared mappings now describe actual opt-in v2 consumers and preserve legacy
  boundaries, historical audits and unrun service checks. Existing shared
  contract/policy suite: 80 passed; normative payloads are unchanged.
- [x] Sequential independent native audits; leader verified findings in source.
  The mandatory fresh formal reviewer is a separate outstanding item above.
- [ ] Complete combined integration review on identical final bytes.
- [ ] Record platform outcomes, source/archive equality and exact remaining limits.
- [ ] Update Claude handoff with A/B source lines, preserved behavior, changed
  contract commit, migration steps and unrun checks. Do not edit Claude host.
- [ ] Do not claim merge, tag, installation or deployment without those distinct
  authorized operations and their evidence.
