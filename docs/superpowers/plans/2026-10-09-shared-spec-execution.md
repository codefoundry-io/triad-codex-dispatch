# Shared specification conformance implementation plan

**Owner steering2026-10-11:** implementation expansion is suspended for the
[vendor-responsibility audit](../../status/2026-10-11-vendor-responsibility-audit.md).
Do not execute U6b/U9 checklists automatically. Reassess whether each shared
requirement belongs to TRIAD or the vendor before proposing its implementation.
Completed work remains evidence; this does not authorize broad deletion or merge.

> **For agentic workers:** Use `superpowers:executing-plans` for leader-owned,
> sequential implementation. Independent research may use fresh read-only
> children. Each functional unit completes its required review before the next
> implementation unit starts. Live progress belongs only to
> `../../status/spec-to-code-sot.md`.

**Goal:** Make both hosts' common observable behavior follow a justified shared
specification while leaving each native leg to its own host.

**Architecture:** Reconcile shared main, PR #12 and PR #13 into a requirement
ledger, then implement one bounded outcome at a time in the existing Codex
checkout. A missing implementation on either concurrently developing host is
pending work, not evidence that the specification or implementation is wrong.
Resolve actual contract gaps before dependent code; use Claude code as evidence,
never as an implicit replacement contract.

**Tech stack:** Python 3.12+, pytest, JSON Schema, Markdown prompt clauses,
existing TRIAD wrappers and review lifecycle; zsh login-shell tooling.

**Spec inputs (checked 2026-10-09):**

- Shared main `3afc4d7e931e55d601dd74877bdbe65e610a8e59` (fresh remote fetch).
- PR #12 `6a2883dd163660b50833eb6ccd48ebd64de69825`, OPEN: records through
  DL-134, including A's Gemini floor, transport agreement and C34 clarification.
- PR #13 `5c040ff967064d8ee782fed1b6855846c4d322d5`, OPEN/Draft: B audit,
  Gemini 0.63 floor and completed bounded U1a verification evidence.
- Canonical rule/case sources: `reference/review-rules.md`,
  `reference/spec-authoring.md`, `cases/cases.json`,
  `contracts/vendor-failure-lines.json`, `authoring/shared-dev-log.md`.
- Shared checkout:
  `/Users/chaniri/codex_workspace/_runs/infra/20260919-host-parity-second-pass/spec-agreement-amendment`.
- B source baseline `632f42633d3a92d6cb27168cd15c4d4debd8558c` plus intentional
  dirty work. Completed quota/Google units are preserved, not restarted.
- Research: `../../status/2026-10-09-spec-investigations.md`.

## PR #13 follow-up disposition — 2026-10-09

Read A's replies at [04:00 UTC](https://github.com/codefoundry-io/triad-dispatch-spec/pull/13#issuecomment-6073991579)
and [04:20 UTC](https://github.com/codefoundry-io/triad-dispatch-spec/pull/13#issuecomment-6074188589),
then inspected PR #12 commits `65fc442`, `e6a71e4`, `6936bd6`, `6a2883d`
and A source at `49910604792e251d5f251da36df5ea0d8079392f`. A has concurrent
dirty review-library/test work; none was changed. Main remains `3afc4d7`.
These are unmerged draft inputs, not an adopted common revision.

| Update | Verified scope and effect on this plan |
|---|---|
| DL-134 / Gemini >=0.63.0 | IMPLEMENTED-OBSERVED in A source: `_version_floor` runs through review preflight or directly on other routes before dispatch; t57 axes 17/18 cover build metadata and raw/write/web routes. A reports Gate 31 green; B did not rerun A's tests. Do not redo completed B floor work. C16/C18/C65 `tests.A` re-pins remain owed after PR #13 merges. |
| DL-132 / opaque model values | A agrees with the observable requirement; its implementation remains scheduled. Move U1T from awaiting A's initial response to shared-rule/case finalization. Preserve per-parser evidence and one terminal vendor refusal, without a new name grammar. |
| AGY 1.3.2 equals form | MEASURED-REPORTED: A reports one successful `--model=gemini-3.1-pro-high` dispatch, matching `init.model` and `result.status: SUCCESS`. Raw capture path/hash was not supplied or independently inspected. This supports ordinary-pin equals compatibility; it does not demonstrate an option-shaped model value or Claude's parser. Reuse the existing capture if available; do not repeat paid inference for this plan update. |
| DL-133 / C34 | Accept requested/exposed identity separation, no catalog admission and no invented runtime attestation. New wording combines "before review inference" refusal with "after the call" observation. Clarify selection-call versus review-runtime receipts before any phase change; do not infer removal of B's existing selection check. Distinguish absent runtime fields from preserved raw unknown labels. U1a's three RED defects are already fixed (`5c040ff` records evidence); reconcile the stale OPEN-B cell rather than reimplementing them. |
| DL-131 / obsolete A descriptions | Confirmed draft edits in `65fc442`: A no longer attributed a Claude CLI producer, extractor or removed test arms; per-attempt hooks and one audit custody line described. No new B port. Remaining DL-6/10/11/12/13 historical annotations and explicitly un-rechecked C14/f13 pointers retain their limits. |
| Credits carrier / DL-103 | No new carrier or schema acceptance evidence. Keep both limits; AGY model-argv success is unrelated evidence. |

U1T must carry the agreed observable rule into R-MODEL and C18/C34 boundary
cases before dependent edits. AGY capture and Claude parser gaps are separate:
do not silently mark them proven or block independently supported corrections.
Do not copy A's Codex CLI TOML encoding into B's host-owned native leg.

## Global constraints and development method

### Non-active work and removal — owner 2026-10-09

Shared authority: D-BACKLOG-DISPOSITIONS-20261009 and
`decisions/2026-10-09-backlog-dispositions.md` in the shared spec. This disposition
overrides historical unchecked tasks and OPEN cells; those are not scheduling authority.

| Item | Disposition / active-plan effect |
|---|---|
| Model/effort environment warning, inspection, normalization, attestation | Withdrawn; remove prerequisites and confirmed remnants. Preserve user settings, existing forwarding and independent auth/loader hygiene. |
| Unmeasured AGY credit carrier | Evidence limit, not a parsing task. Re-enter with actual carrier evidence; preserve the implemented phrase. |
| Option-shaped model-name ban | Not adopted; no grammar restriction. U1T value-preserving transport remains active. |
| Other host's native spawning/presets/logging | No port; common input/result contracts remain. |
| A hook/stream/audit simplification DL-124..126 | No automatic port; compare common outcomes only and fix demonstrated B differences. |
| A Claude CLI removal DL-110/121/131 | No B removal; keep shared documentation/test-pointer corrections. |
| Repeated prompt nuance/phrase-pinning work | Remove open-ended iteration; retain bounded contextual behavior verification. |

Remaining removal work is explicit in U10 below and is performed alongside each
owning unit when a confirmed remnant is found. Do not delete historical evidence,
functioning optional features or common contracts under the word "cleanup".

### Implementation constraints

1. Refresh main and both PR heads at unit entry, before a shared design change,
   and before final review. Record each host's commit and relevant dirty files.
   Do not mistake old status cells, concurrent edits or an unmerged PR for a
   current implementation result or an adopted release.
2. For each requirement record: rule/case, intended result, why it is useful,
   evidence/source/version, A state, B state, uncertainty and owning unit.
   Use states `IMPLEMENTED-OBSERVED`, `IMPLEMENTED-REPORTED`, `PENDING`,
   `SPEC-GAP`, `UNMEASURED`, `NOT-APPLICABLE`; test execution is a separate field.
3. Decision order: existing spec -> corresponding Claude code if the spec is
   silent -> primary vendor evidence or a bounded spike -> shared fact/limit
   or clarified rule/case -> dependent Codex implementation. Question the rule
   itself when evidence contradicts it. Do not blindly copy A's mechanism.
4. A new common behavior needs its evidence, current/proposed behavior, both
   hosts' effects, preserved features and verification written into the shared
   spec before code. Request the other maintainer's review of the same revision.
   Settled implementation work does not wait merely for A to finish its own work.
5. Stop only the affected work for a substantial design change, conflicting
   supported requirements or a necessary owner choice. Present concrete options
   and impacts. A fact neither host knows is recorded as unknown; do not ask the
   same unanswered factual question repeatedly or invent output locations.
6. Each unit: bounded plan -> meaningful RED -> minimal fix -> affected GREEN ->
   relevant regression -> required independent multi-family review -> evidence
   and shared handoff. Preserve negative rounds; changed bytes/basis need a new
   complete round. No automatic composition change based on a historical round.
7. Keep production/test/doc changes separate in estimates. No worktree reset,
   clean, stash or separating checkout. One production writer, since several
   units share `bin/_common.py`. Commit only attributable hunks after the unit
   gate; never stage unrelated existing changes.
8. Gemini minimum is `0.63.0` on raw/legacy/v2, prereleases below that floor;
   no catalog gate or model substitution. Browser-auth and containment remain.
   No native spawning/preset/default redesign, credential manipulation or
   quota-exhaustion experiment. A planned live probe is not a completed check.
9. Product merge, adoption, installation and release remain distinct approvals.
   The temporary SoT hook stays through unfinished work and is removed with its
   temporary startup instructions only at whole-task completion.

## Prompt method: contextual decisions, minimal wording

- A prompt finding must name a realistic context, the wrong action it causes,
  the expected action and the shortest correction. Grammar, tone and equivalent
  wording are not defects without an action difference.
- If a discussion repeats over nuance, freeze the candidate and record expected
  choices plus a contrasting control before dispatch. Give a fresh
  `gpt-6-luna` / `high`, `fork_turns="none"` child only the prompt, necessary
  context and scenario. Ask for its chosen action and a short reason; hide the
  expected answer and prior review history.
- Use three scenario/control pairs covering the disputed boundary, not three
  paraphrases of one obvious instruction. Retain prompt hash, model requested,
  scenario, response and outcome. Runtime model details not exposed by the tool
  remain `UNEXPOSED`.
- If Luna/high makes the intended choices and controls distinguish the boundary,
  stop stylistic revision. This is scoped comprehension evidence, not universal
  proof. Revise minimally and repeat only a failing boundary or new evidence.
- The owner's Luna/high choice overrides the older generic Sol/medium prompt
  simulation default for this task. These simulations do not replace this
  repository's dedicated skill-executor RED/GREEN or formal review requirements.

## Review focus

- A transcript quoting an authentication error must not cause a false STOP;
  an actual authentication carrier must stop even beside capacity or interruption.
  U2 tests own both sides.
- A legitimate model absent from a shipped list must pass unchanged, while
  observed family/tier substitution must refuse. U1 owns these tests.
- A later valid AGY finish must preserve the answer without admitting another
  executed forbidden step. U3 owns stream-order tests from measured evidence.
- Two hosts in different folders must not change each other's global settings.
  U7 owns the concurrency spike and chosen isolation tests.
- Interrupted cleanup must keep ownership evidence and never remove an
  undeclared/live root. U6 owns the interruption and configuration tests.

## Execution sequence and estimates

Production estimates are planning ranges, not authorization to add mechanisms.
`+/-/net` counts runtime lines; novel core is a separate upper estimate. Tests
and documentation are additional. Re-estimate from the actual scoped diff at
unit entry; growth alone does not require an owner question.

| Unit | Outcome / dependencies | Production + / - / net; novel core | Tests / docs estimate |
|---|---|---|---|
| U0 | Reconcile evidence and five investigations; current planning work | 0 / 0 / 0; 0 | no new product tests; 600-850 doc lines across plan/evidence/shared note |
| U1T | Preserve opaque model values through parsers, after U0 and shared disposition | +15-40 / -10-30 / -15 to +30; <=25 | 60-110 / 15-30 |
| U1 | Claude pin/alias identity, after U1T or independently if its decision is pending | +80-140 / -40-90 / -10 to +100; <=100 | 120-200 / 20-50 |
| U2 | Authentication and measured carrier classifier, after U1 | +100-180 / -80-150 / -50 to +100; <=130 | 180-300 / 30-60 |
| U3 | AGY terminal semantics and schema evidence, after U2 | +70-140 / -30-70 / 0 to +110; <=110 | 130-220 / 20-40 |
| U4 | Repair semantics and retired helper paths, after U2/U3 | +30-80 / -100-220 / -190 to -20; <=60 | 100-180 / 30-60 |
| U5 | Shared prompt and review basis synchronization, after U1-U4 | +60-120 / -30-70 / -10 to +90; <=80 | 120-220 / 50-100 |
| U6 | Declared cleanup roots and deletion ownership | +220-400 / -140-260 / -40 to +260; <=280 | 220-350 / 40-80 |
| U7 | AGY shared-state isolation and read-only web prerequisite | +100-200 / -180-350 / -250 to +20; <=150 | 160-250 / 40-80 |
| U9 | Remaining lifecycle/custody/OS evidence | +60-120 / -30-80 / -20 to +90; <=90 | 120-200 / 30-60 |
| U10 | Combined conformance and integration handoff | corrections only, separately bounded | full manifest and handoff |

U6, U7 and U9 research may run independently. Their product changes remain sequential
and start only after the preceding implemented unit's gate. A concrete design
choice uncovered by U6/U7 is returned to the owner before dependent code.

## U0 — Consolidate the baseline and research

**Files:** this plan, `docs/status/spec-to-code-sot.md`, research note; shared
`decisions/2026-10-09-execution-planning.md` and its development-log link.
**Output:** each investigation has a supported conclusion or a precise limit,
not an unbounded research task. No new runtime API.

- [x] Reconcile main and PR changes, retaining both pending host implementations.
- [x] Investigate credits carrier using primary docs/captures without consuming quota.
- [x] Extract the schema actually emitted by B, run route-specific offline tests,
  and write the smallest authenticated manifest only if live proof is missing.
- [x] Compare DL-124..126 observable contracts and DL-110/121 documentation to
  current source; do not copy A-only internal simplifications.
- [x] Investigate model argv interpretation with an actual parser or primary
  implementation source; do not infer a vendor failure from a mock parser.
- [x] Save shared facts/requests and self-check this plan's coverage and links.

## U1T — Lossless model argument transport

**Rules:** R-MODEL/C18 (existing pass-as-written requirement); proposed shared
clarification in `decisions/2026-10-09-execution-planning.md`.
**Files:** `bin/review_adapters_v2.py`, model argv construction in
`bin/gemini_wrapper.py`, `bin/antigravity_wrapper.py`, `bin/claude_wrapper.py`;
`tests/test_v2_adapter_wrapper_bridge.py`, `tests/test_provider_wrappers.py`.
**Interface:** a model is one opaque option value at every parser boundary.
Do not create a shared model-name grammar or claim a shell-injection defect.

- [x] Review the existing Gemini 0.63.0 and 24-case B Python-wrapper evidence;
  reproduce only missing cases. Use A's DL-132 agreement and census to finalize
  R-MODEL/C18/C34 before dependent code.
- [x] Obtain independent Claude, Google and fresh Codex diagnosis for any
  confirmed existing-design omission before implementing its remedy. Return a
  substantial design choice to the owner; do not treat a routine argv encoding
  correction as permission for a new model grammar or containment change.
- [x] RED: `--help` as a model value does not activate help, `--yolo` does not
  activate a permission flag, ordinary unknown pins and spaces remain exact.
  Label these parser/transport tests, not vendor model availability fixtures.
- [x] Test candidate equals-form encoding on each affected real parser before
  adopting it. A help-only result from AGY/Claude is insufficient proof of value
  interpretation; retain the gap or find stronger parser evidence.
- [x] Apply only compatible value-preserving transport, keep required runtime
  controls and one terminal vendor rejection, run affected bridges and wrappers,
  and obtain a fresh bounded formal gate. The completed Google unit's earlier
  approval is not approval for these new bytes.

Completed 2026-10-10; exact scope, parser limits, RED/GREEN and fresh R3
evidence: [U1T unit plan](2026-10-10-u1t-model-transport.md). Final production
+17/-9 across six files; no native or model-grammar change. Shared d082a60.

## U1 — Claude selection without a catalog gate

Execution boundary (2026-10-09): first complete **U1a**, the reproduced adapter
catalog/selection defect, independently of **U1b** alias-default migration.
These outcomes have different consumers. U1a changes only `_claude` and its private comparison helper, tests,
and explanatory documentation; defaults, native legs and agent custody remain
unchanged. Estimated production +55/-20/net +35, novel core <=45 lines. Its
formal gate precedes U1b or another implementation unit. The owner explicitly
requested implementation after the three diagnostic RED cases were reported;
this is a bounded correction to the existing C34/R-MODEL implementation.

U1a completion (2026-10-09): actual production +60/-19/net +41, novel core
within the 45-line estimate. No default/native/agent-custody change.

- [x] Remove catalog admission; preserve request and unknown observed labels.
- [x] Refuse exposed alias/full-ID and effort contradictions; keep the wrapper
  effort vocabulary and required CLI controls as interface checks.
- [x] Reproduce and fix both round-1 header parsing findings. Final affected
  suite: 99 passed (32 selection cases); earlier full suite: 1,881 passed,
  4 skipped. The full result predates the bounded parser corrections.
- [x] Fresh round `triad-claude-selection-20261009-r2`: all four selected
  reviewers SAFE, matching integrity, exact temporary stage/cwd cleanup complete.

### U1b — Claude alias default

U1b execution scope (2026-10-09): R-ROSTER/DL-114 explicitly supersedes the
fixed-ID default on both B v2 and the legacy formal CLI route. Change only
`contracts/review-legs.default.json` and `bin/claude_wrapper.py` route constant/
diagnostic, plus their current skill/reference/documentation consumers. Keep
xhigh, 1200 seconds, no fallback, plan-mode containment, explicit raw/v2 model
overrides, explicit v2 null and `agent: null`. No native control or agent resolver
change. Estimated production/data +4/-4/net 0; novel core 0. Tests 20-45 added/
updated lines; docs 20-35 lines. The existing SoT remains the execution ledger
instead of a second skill-generated progress ledger; preserve existing worktree.

- [x] RED: real roster resolves opus; legacy wrapper sends opus and retains
  binding/effort/timeout/fallback refusal tests; raw/v2 explicit IDs/null survive.
- [x] Dedicated source-skill executor records the current Claude command;
  after minimal route edits a fresh executor verifies the revised selection.
- [x] GREEN: affected roster/adapter/wrapper/distribution tests, full suite,
  skill validation and fresh four-family-entry review with integrity.
- [x] Update SoT and shared implementation evidence without claiming install,
  release, adoption or changing native legs. Source review uses the owner-decided
  opus alias and preserved Astra/high selection, with deviations from the old
  fixed workspace ledger explicit; no fabricated fixed-ledger admission token.

Owner-authorized review-workflow correction, 2026-10-09: the objective, diff and
worktree go to reviewers; they discover related unchanged files. Remove the
operational exact-file-only boundary and normal-close read-log comparison.
Product runtime/skill delta is +0/-0, novel core 0; round scaffolding is simplified
and project guidance clarified. Canonical-skill baseline chose correctly, so no
unnecessary skill rewrite follows. Collector RED/GREEN: 3 failing log-dependency
cases, then 3 passing; fresh executor discovers an unlisted helper defect and
selects incident-driven log inspection. Combined relevant checks: 191 passed;
skill validator valid. Shared C70/C71 preserve A's coded route controls and
record that the same exact-list defect was not found in A at a91b436. This is
workflow correction evidence, not U1b formal admission. R2 was NOT_APPROVED
for AGY missing search; approved C72 profile recovery subsequently passed source
verification and a real native search/read control. Fresh R3 is all four SAFE,
ROUND_INTEGRITY_OK, with six nonblocking Minor findings. The SoT records one
bounded documentation follow-up; its changed bytes passed their own review
`triad-agy-docs-20261009-r1` (all four SAFE, matching integrity). Dedicated clean
RED exposed a contradictory catalog requirement that withheld launch; fresh GREEN
selected the intended action, passed 159 affected tests and both validators with
stable hashes/status. A fresh Luna/high probe resolved further wording suggestions
by correct update/removal/missing-profile choices; stop wording iteration. Runtime
delta +0/-0; six documentation files only, no additional prose-pinning tests.

U1a/U1b are complete with the evidence above. Remaining model-value transport
and selection/runtime wording belong to U1T and DL-133; do not repeat the
completed catalog/default work.

## U2 — Authentication and measured error carriers

Owner withdrawal2026-10-09: discard the later model/effort environment
inspection/warning/attestation extension and remove its research prerequisites.
Existing effort forwarding and user settings remain. Do not restart those
spikes or implement the withdrawn warning. Shared decision
D-SELECTOR-PROPOSAL-WITHDRAWN-20261009 governs; independent auth/loader parity
was completed as the bounded U2c candidate below.

Progress 2026-10-09: U2a Gemini exit41 and U2b measured auth carriers are complete
in the local candidate with dedicated verification and fresh all-four SAFE
reviews. U2b also closes the auth portion of DL-92 and implements DL-75/95;
it does not complete this whole U2 checklist. U2c is now complete: agreed child
environment parity, name-before-value filtering, preserved model/effort settings
and Gemini project passthrough including v2 intermediate preflight. Final
focused370/full2029 passed with4skips, both validators; complete fresh R2 all-four
SAFE/matching integrity, exact cleanup. Shared evidence75dc801 and SoT retain
the failed runner/fixture attempts and R1 correction. Non-auth per-CLI classification,
general guards and unmeasured vendor carriers remain separate pending work.
Detailed current evidence and remaining limits are in the execution SoT.
R3 observations: preserve original-stream-only auth when later refactoring Gemini
extraction; record the constructed formal Claude empty-answer denial/tool_input
case as a limit, not a dedicated implementation target; keep typed extension
oauth-env codes under separate DL-97 review. These observations have provider-free
diagnostic reproduction, not new vendor captures. The owner's challenge and
current A/B/spec comparison are recorded in
`docs/status/2026-10-09-non-auth-classification-review.md`. A has no Claude CLI
wrapper; its generic shared lists are empty and its measured phrases are per CLI.
B's remaining shared generic phrases are pending R-CLASSIFY/DL-86/DL-92
conformance work, not proof of an actual incident. The owner subsequently rejected
promoting this comparison into an automatic classifier-cleanup priority. Preserve
the actual-failure-driven repair loop (D-REPAIR-LOOP-KEEP-20261008): inspect the
failed run's own record, propose a supported entry, verify against the stored record,
and promote learned evidence to the shared contract. No exhaustive error dictionary,
manufactured failure campaign or routine successful-run log audit is planned.
Do not add a special denial parser or widen
C74's completed is_error-envelope regression into the constructed empty-answer case.

Status: remaining evidence mapping. First
reuse existing C43 tests and investigation notes, then identify a demonstrated
gap; this checklist does not assume every listed correction is still needed.

**Rules:** R-AUTH/R-CLASSIFY/R-NOCOST; C11/C16/C17/C37/C43;
DL-16/62/65/71/75/76/80/81/82/86/90/92/95/99/117.
**Files:** `bin/_common.py` (`classify`, child-environment construction,
`_mark_signal_failure`), `bin/antigravity_wrapper.py`, `bin/gemini_wrapper.py`,
`bin/claude_wrapper.py`; existing provider/wrapper/parent-signal tests and
new `tests/test_measured_auth_contract.py` if a single focused module is clearer.
**Interface:** preserve `RunResult`, common token vocabulary and exit mapping;
carry source CLI/channel explicitly into the internal classification decision.

- [ ] Map every retained phrase to a contract/source/capture and its carrier.
  A shared phrase table is not permission to guess AGY quota event placement.
- [ ] RED: measured structured authentication beats capacity; quoted auth text
  in an answer does not STOP; Gemini authentication exit 41 stops; a signalled
  run retains an already captured authentication result; each forbidden env
  variable is set synthetically before checking that the child lacks it.
- [ ] Implement the minimal carrier-first decision and per-CLI matching;
  retain the already-corrected quota rows and generic never-raise/record guarantee.
- [ ] Run the changed wrapper/classifier/signal modules, check no usable answer
  is discarded solely for its prose, then complete review and shared evidence.

## U3 — Measured AGY results and schema compatibility

Current remaining assessment: sharedca64d1d and PR13comment6092582472,
`decisions/2026-10-10-u3-remaining-carriers.md`. Direct B investigation and A
reply6092564483 settle the marker rule on the actually emitted answer channel;
valid structured_output survives a marker in incidental response. A bc8a8a74
checks response first as a host choice, not a common rule or measured mixed pair. DL-101
typed network-error handling is independent, but must preserve classifier
priority without guessing a credits carrier. U3c now implements the exact typed
network row through the existing capacity rung; see its bounded plan. Owner
correction: investigate truncation directly, not passively await A's explanation.
Official headless docs and A's historical structured/long-output reports support
the actually emitted answer channel; a response-only marker is not proof of
lost structured output. The distinction is now recorded in R-CLASSIFY/C43/DL-102
before dependent code. Preserve schema/binding checks; no recursive scans,
byte-size gate or tool/web-search-output workaround follows from this rule.

U3c measured network carrier is implemented and verified:495affected/2237full
passed,4skipped, four validators, all-four SAFE/two nonblocking Minors, matching integrity
and exact cleanup. U3d raw-answer truncation is now verified:564affected/2264full
passed,4skipped, four validators, all-four SAFE with matching integrity and exact
cleanup. Next: DL-103 current-route schema evidence. No web-tool workaround.

First bounded item: [U3a finish resubmission](2026-10-10-u3a-finish-resubmission.md).
Execution update: [U3b turn-timeout](2026-10-10-u3b-agy-turn-timeout.md) proceeded
independently while U3a awaited clarification; GREEN and all-four SAFE review complete.
A reply6092107935 and sharedf332ab8 now resolve U3a's two boundaries. Finish
U3a is implemented and verified:458affected/2213full passed,4skipped, four validators, all-four SAFE/matching integrity and exact cleanup. U3b is also complete. The following paragraph records the initial assessment.
2026-10-10 evidence assessment confirms the B ERROR-result recovery gap with a
provider-free characterization, not a live provider replay or dedicated RED.
Before dependent edits, clarify the existing structured-only finish judgement
versus A's message-based denial predicate, and the shared scope of nonzero exits.
The shared evidence note records both questions and the missing original raw
capture. Do not port A's full census or add a routine successful-run read audit.

**Rules:** R-CONTAIN/R-CLASSIFY; C23/C30/C43; DL-101/102/103/113/125.
**Files:** `bin/antigravity_wrapper.py` (`_interpret_run`, `parse_agy_stream`),
`bin/verdict_v2.py`;
`tests/test_antigravity_stream_json.py`, `tests/test_v2_google_wrappers.py`,
`tests/test_v2_producer_adapter.py`.
**Interface:** terminal result admission yields the existing answer/token/exit;
canonical full verdict validation remains mandatory after any producer projection.

- [x] Reuse measured network-error, turn-timeout, truncation and finish-resubmit
  evidence; record source/version and actual structured fields first.
- [x] RED: own-line truncation withholds answer; terminal timeout uses the
  specified token/65; later successful finish rescues only the earlier failed
  finish, not another executed forbidden/errored step or a read-blind run.
- [x] Verify actual AGY schema: current route enum is already `['agy']`; do not
  reimplement a null-enum fix. Execute a bounded live manifest when needed to
  decide remaining keyword compatibility. Auth/capacity failure is inconclusive.
- [x] Add projection only if current-route vendor evidence requires it; keep
  post-output full-contract validation. Complete relevant modules and review.

U3e assessment complete: actual AGY1.3.3 Pro/high normal v2 wrapper exit0,
full local binding/schema validation passed; no new projection justified.
Production/test delta zero. Evidence: ../../status/2026-10-10-agy-v2-schema.md.
Next: U5 shared-clause/current-context assessment; U2 retains evidence mapping.

## U4 — Repair boundary and obsolete helpers

U4a is accepted by the owner after passing behavior/regression checks; original
R3 NOT_APPROVED is retained. D-PROMPT-REVIEW-BOUNDED-20261009 accepts the two
wording/test demands as nonblocking and authorizes U4b. No unchanged redispatch.

U4b1 [applier plan](2026-10-09-u4b1-applier.md) is complete in the local candidate:
all-auth proposal refusal and reason/entry cap removal; focused229/full2050 passed
with4skips, two validators, all-four SAFE and matching source integrity.
U4b2 [stored-record plan](2026-10-10-u4b2-stored-record.md) is complete:359focused
passed on final guidance/tests, unchanged production previously2078full passed
with4skips; R3 all-four SAFE/matching integrity. Full C76 runtime remains partial.
U4c [typed-loader plan](2026-10-10-u4c-typed-loader.md) is complete:403focused/
2143full passed,4skipped, four validators and R1 all-four SAFE/matching integrity.
DL-97 and DL-106 zero-key loading are implemented. U4d below completes the
remaining DL-106 disposition, preserving direct-call AGY compatibility.
Shared d1b9bcc/PR13comment6085594103 records completion and verification limits.

### PR13 follow-up6093708612 — 2026-10-10

A agrees with the DL-101/102/103 dispositions and confirms CRLF fix4b07949a.
A C43 tests.A evidence refresh remains A-owned. A reports DL-104 timeout
exclusion and applier-cap removal implemented; read-only A7dbba148 _common.py
confirms timeout exclusion. Its analyzer consolidation/stored-record verifier
work is ongoing, not a new B backlog. Preserve B U4b1/U4b2 completed evidence.
No U5 change or A-native port follows.

### Earlier PR13 follow-up6088729953 — 2026-10-10

A agrees with the C76 clarification and reports a revised F3-c plan; Phase7
implementation remains pending. Preserve B's completed stored-record verifier;
A's combined apply/verify command is not an instruction to port its mechanism.
The local A plan inspected at a5afdd5a still contains the old exit0 sentence in
F3-c, so the reported plan amendment is not independently verified here. Record
the next published revision before marking that amendment confirmed; concurrent
work is not a new implementation defect. No new common rule is requested.

C77 source evidence is now identified: A's t21 axes10/12/14/17 and t32 proposal
class assertions, inspected read-only at a5afdd5a. No A tests were executed.
Axis17 directly tests key0 plus a valid7 sibling; the loader's int(k)<=0 branch
also explains its broader exclusion. B keeps its agreed zero-only rule. A keeps
noninteger keys but they never match; do not add a new key-range restriction.
A will synchronize its tests.A cell after the shared case reaches main.

Completed [U4d maintenance simplification](2026-10-10-u4d-dead-classifier-code.md)
removes _json_len and the Gemini/Codex/Claude maps containing only zero:ok.
The AGY zero:extraction-error fallback is preserved for direct common callable
compatibility. The current wrapper handles raw-zero missing/empty answers itself,
and stored replay uses its interpreter; do not claim wrapper dependence on the
map. Normal success, valid extension entries, Gemini auth41, timeout precedence
and AGY no-answer outcomes remain identical in affected verification.
Removing the optional vendor_exit_code argument changes a callable interface;
it is not automatically bundled with private dead-code deletion.

- [x] Read issue, inline and review comments; verify new claims against A source.
- [x] Identify the candidate definitions and B's production classify call sites.
- [x] Complete caller/reachability assessment and record delete/keep/defer for
  each DL-106 item; clarify stale shared claims before dependent deletion.
- [x] If behavior-preserving removal is established, create one bounded plan
  and use existing classifier/wrapper controls plus any necessary missing
  behavior case. Do not add tests whose sole assertion is that a private name
  disappeared. Keep child log/TMPDIR isolation before imports.
- Standing gate: stop and ask before a substantial design/scope or callable-interface change.

U4d actual production+3/-43(net-40), existing test+1/-2. Dedicated baseline/final
393tests and four validators passed; first392/1failure retained and corrected in
the existing dynamic-name test. Four-family R1 SAFE/matching integrity, terminal
producers, exact cleanup. Shared c25da30/PR13comment6089074042 records completion
and narrowed callable coverage. Supplemental before/after callable probe has
four matching outcomes; no current full-suite claim. Optional comment/guard
cleanup is nonblocking, not an automatic new unit. DL-91/DL-119 reconciliation
against current rules, B callers and read-only A source is recorded below.

That reconciliation is now recorded in
[remaining assessment](../../status/2026-10-10-u4-remaining-assessment.md).
DL-119's B applier/escalation correction already exists; no observed child wrong
decision justifies another wording cycle. DL-91's bounded removal is complete in
[U4e](2026-10-10-u4e-retired-task-code.md), under shared a41769c and
PR13comment6091668144. RED12failed/443passed; removed production+7/-189(net-182),
preserving Claude task-blocked65, retry parameters, locking and native dispatch.
Affected GREEN455/full2152passed,4skipped; four validators and all-four SAFE with
matching integrity. Exact fixtures and review stage/cwd removed; shared389071a
updates DL-91/C8 evidence. One Minor stale-comment note retained, no wording loop.
Next: U3 DL-113 measured finish-resubmission evidence/source assessment before code.

Execution split: [U4a repair-web plan](2026-10-09-u4a-repair-web.md) implements
the owner-requested research capability first. U4b retains the timeout-routing,
stored-record replay and applier checks below. Web permission alone does not
close C76 or DL-104; no U2 phrase cleanup or U3 parser work is pulled into U4a.

Historical pre-U4a steering (owner 2026-10-09): shared PR13 commit310de79 adds
R-CLASSIFY/C76 failure-driven repair web research for both hosts. A c50b1c8's
three repair agents and distributed template forbid web; B's actual native
analyzer prompt in docs/references/repair-protocol.md:51-55 does too. Align B's
research prompt and effective web capability within this unit; keep the analyzer
read-only, sources attributed, and vendor reruns separate. No new error dictionary
or speculative carrier parsing. C76 host implementation and runtime validation
remain pending. Shared authoring1/1 and182tests passed; see
decisions/2026-10-09-repair-web-research.md in the shared spec for A handoff.

**Rules:** R-CLASSIFY/R-AUTH/R-TOKENS; C8/C37/C43;
DL-91/97/104/106/119. Existing DL-105 preflight binding remains; the separate
U8 installation investigation was withdrawn by the owner on 2026-10-10.
**Files:** `bin/_common.py` (`_load_classifier_extension`,
`apply_classifier_patch`, repair token sets), `docs/references/repair-protocol.md`,
dispatch skill repair references and existing classifier/repair tests.
**Interface:** proposal-only child -> existing proposal schema -> host applier;
verification consumes the stored run record, not another vendor invocation.

- [x] Historical pre-implementation assessment: B lacked stored-record verification
  and the handoff; A d075a879 then routed timeout and used vendor reruns.
  Superseded by completed B U4b and the A follow-up6093708612 above.
- [x] Restore the existing missing dispatch-skill-to-protocol pointer for
  unknown/extraction-error; verify handoff without vendor replay.
- [x] RED: timeout is not sent for phrase repair; an `oauth-env` proposal is
  refused on every proposal path; extension exit 0 and out-of-class tokens do
  not override the contract; replay verification makes zero provider calls.
- [x] Keep locking for concurrent leg results. Remove retired
  fanout/task helpers and owner-rejected limits, preserving `task-blocked` where
  it still describes the Codex host's external Claude route.
- [x] Render minimal auth-escalation guidance; apply the Luna protocol only if
  contextual wording is disputed. Promote newly learned measured phrases to
  shared contract evidence rather than a private permanent fork.
  Existing protocol opening/Apply guidance and U4b1 applier refusal satisfy the
  current bounded correction. Ongoing new-error evidence is not a pending rewrite.
- [x] Run repair/classifier/distribution tests and required skill behavior
  validation, then formal review.
  U4a..U4e evidence is recorded per bounded unit. U4e's current full suite covers
  source distribution-contract tests; release archive/install verification and
  broader measured-runtime C43/C76 certification remain separate.

## U5 — Shared prompts and bound review context

U5a candidate complete: exact sharedca3d990 clauses, bound preparation date,
A-only header selection and late-answer recollection guidance. Fresh GREEN
297 affected fresh; 2273 full prior R2 passed, 4 skipped, four validators; all-four SAFE
with matching integrity and cleanup. DL-39 v2 standing-web binding completed in U5b below.
See [U5a plan](2026-10-10-u5a-shared-review-context.md).

U5a resolves the U3c/U3a documentation notes: README EN/KO now distinguish
AGY single-shot capacity behavior, and the AGY skill names the measured
ERROR-only finish recovery. No runtime retry change or repeated U3 review.
The unmeasured reflected-command suggestion remains nonblocking.

**Rules:** R-CONTEXT/R-PREPARE/R-REVIEW-WEB/R-AGREE; C19/C32/C60/C67/C68;
DL-39/45/46/49/56/61/93. Native model choice remains host-owned.
**Files:** `prompts/review-v2/`, `bin/review_prompts_v2.py`
(`review_web_clause`, `render_prompt`), `bin/review_round_v2.py`,
`tests/test_v2_review_prompts.py`, `tests/test_v2_round_custody.py` and source
skill references. Adopt payload bytes/digests consistently with the chosen revision.

- [x] Identify the exact shared clauses to adopt; do not mix unmerged PR prose
  into a claimed frozen revision. Record latest concurrency and measured-shape
  wording plus the bound preparation-date rule.
- [x] RED: rendered date comes from the frozen basis, not render time; all
  applicable legs receive the same common clause; web authorization matches
  execution; changed bound inputs fail integrity; no host-native clause leaks.
- [x] Reuse clause files instead of duplicate constants. Add only needed
  invocation/pointer guidance and the late-answer recollection instruction.
- [x] If nuance repeats, run fresh Luna/high decision/control scenarios; stop
  wordsmithing when behavior is correct. Complete dedicated executor and formal
  gates required for source skill changes.

U5b v2 standing-web candidate is now complete: 371 affected/2280 full passed,
4 skipped, four validators and complete all-four SAFE review with matching
integrity and cleanup. See [U5b plan](2026-10-10-u5b-standing-review-web.md).
Legacy per-request authorization remains the recorded DL-59 difference, to be
accounted for in U10; no legacy retirement decision is implied. Native model
and effort remain host-owned. No wording scenario probe was needed.

## U6 — Cleanup as declared host code

**Rules:** R-CLEANUP; C3/C4/C5/C7/C69; DL-19/22/54/77/79/85.
**Files:** existing `bin/review_round.py` cleanup, `bin/_common.py`
(`prune_stale_run_logs`, `prune_stale_tmp_dirs`), proposed
`bin/cleanup.py` and `bin/data/cleanup-roots.json`, README EN/KO;
`tests/test_review_cleanup_custody.py`, `tests/test_log_cleanup.py`.
**Interface decision before code:** choose the concrete deletion entry point
and config lookup against the shared schema; record ownership, age and resume
semantics. No command name is silently invented by this roadmap.

- [x] Inventory current roots/proofs/floors and compare A's implementation to
  the contract. Confirm invocation-time owned temporary cleanup exceptions.
- [ ] Resolve entry-point/migration design before RED; ask the owner only if
  it changes shared surfaces or requires an unresolved trade-off.
- [ ] RED: missing/invalid config deletes nothing; undeclared path is refused;
  proof is removed last; interruption can resume; linked worktree ownership,
  live age floors and exports survive; name-shaped unowned temp dirs remain.
- [ ] Route owning deletions through the agreed code and replace manual-delete
  advice. Run cleanup/bootstrap contract tests and complete formal review.

Execution split (2026-10-10): U6a corrects the demonstrated fallback-folder
ownership omission with existing entry points; [bounded plan](2026-10-10-u6a-fallback-ownership.md).
U6b retains declared-root/floor migration and normal sweep/cap/archive checks.
The proposed generic cleanup.py above is not a selected interface or dependency.
Independent diagnosis and shared ba04c60/C4 boundaries precede U6a code.

U6a completed: B `a4fd93c` / shared `c55dca6`, pushed and remote-matched.
Final340affected/29standalone/2347full passed,4skipped; four validators and fresh
R3 all-four SAFE/matching integrity. Custody export/exact cleanup are complete.
U6b's enclosing normal-log-folder proof mapping received A's answer in
PR13comment6097553901 and PR12 d805b50/DL-152. Current source/spec comparison is
next; receipt of a reply does not close declaration/migration or C69 conformance.

## U7 — AGY isolation without shared settings writes

**Rules:** R-CONTAIN/R-REVIEW-WEB; C6/C68/C72, shared0d7073d.
Owner selected the exclusion-profile approach on2026-10-11 after live native
read/search/web probes. The bounded execution plan and evidence ledger are
[U7 profile/settings](2026-10-11-u7-profile-settings.md).

- [x] Diagnose shared settings mutation and compare current A behavior.
- [x] Publish the selected contract and request A review on PR13.
- [x] Obtain dedicated RED, remove global settings transactions, add exclusion
  to the existing explicit-tool profiles, and migrate raw read-only routing.
- [x] Align affected current documentation and retain historical release facts.
- [x] Final dedicated GREEN2364passed/4skipped and fresh R3 all four SAFE, integrity matched.
- [x] Record verified implementation evidence for publication and shared C6/C68/C72 update.

No new project prerequisite, hook, cwd machinery or routine read audit. Existing
optional project validation remains. Requested web rejects a known URL-wide deny
or malformed existing settings without adding an allow-list prerequisite. Old
settings residue is preserved. Permissive raw keeps its existing behavior except
for removal of global mutations. Read-only requires CLI>=1.2.1 and no autoapproval.
The live no-write result is not proof of a denied attempt or universal prevention.
Both profiles were updated after exact-path owner approval; known permission settings
hashes stayed unchanged. Evidence is in the U7 unit plan; no full plugin installation
or release. U7 is complete; remaining roadmap is U6b, U9, U2 and U10.

## U8 — Withdrawn by owner, 2026-10-10

Installation coexistence is treated as an operator-managed rare case. Remove
this unit's investigations, implementation, test/review work and dependencies;
do not move them to U7, U9 or final completion prerequisites. This is WITHDRAWN,
not implemented or verified. Shared decision D-U8-WITHDRAWN-20261010 records the
owner's wording. Existing installation code, tests, preflight binding and common
authentication requirements remain; no removal or new work follows from them.
Reopen only by a new explicit owner scope decision.

## U9 — Remaining lifecycle and evidence checks

**Rules:** R-TERMINAL/R-TOKENS/R-BIND/R-PREPARE;
DL-13/14/42/43/67/70/72/84/87/88/90/123/125/126.
**Files:** `bin/_common.py`, `bin/review_round.py`, `bin/review_round_v2.py`;
`tests/test_parent_signals.py`, `tests/test_v2_evidence_custody.py`,
`tests/test_v2_round_custody.py`, existing symlink/cleanup tests.
**Interface:** preserve answer, terminal record and canonical token/exit through
ordinary operator signals and I/O failures; no new vendor event speculation.

- [ ] Classify each old CHECK-B as present, genuinely failing, unmeasured or
  optional hardening. DL-124..126 A-only simplifications are not automatic B work.
- [ ] RED for reproduced gaps: signal between attempts leaves a terminal
  record; a second signal does not orphan a child; failed stderr write does not
  lose answer/exit; symlink-listing failure cannot be certified as full coverage;
  each emitted summary pair is a contract pair.
- [ ] Implement only supported gaps, run complete affected modules, and review
  the smallest coherent lifecycle outcome. Split unrelated findings if review
  could accept one independently; update estimates accordingly.

Measured DL-88 evidence is shared at `c55dca6` /
`decisions/2026-10-10-b-terminal-evidence.md`: the actual B shared driver returns
a valid synthetic answer in the control, but raises and returns no RunResult
when its terminal diagnostic sink raises BrokenPipeError. No live provider,
real stderr or product edit. A e9960053 already drops failed diagnostic writes;
its source was read, not executed. Independent diagnosis and the smallest
existing-contract correction remain next; do not expand this to speculative
vendor error classes. DL-123..126 needs no B port; other old rows remain
individual evidence checks, not confirmed defects.

## U10 — Reconcile and hand off

- [ ] Remove confirmed remnants of withdrawn proposals and no-port requirements
  from active guidance, hooks and relevant code/tests in this host's scope.
  Use D-BACKLOG-DISPOSITIONS-20261009's item table; record each as removed,
  absent, deferred with re-entry condition, or common behavior preserved.
  A live common contract or functioning optional feature is not a deletion target.
- [ ] Remove superseded executable checklists and stale completion prerequisites;
  reconcile old OPEN cells with current evidence. Retain labelled historical
  research, failed reviews and original observations; no blanket text deletion.
- [ ] Verify changed links and affected behavior only where actual changes occur;
  send the shared disposition to A without changing A-owned implementation.

- [ ] Account for every current main/PR row, including newly added A rows:
  completed, pending by owner, limit, not applicable, or explicitly deferred.
  No `OPEN` -> `FIXED` transition without current evidence.
- [ ] Reconcile rule text, cases/tests pointers, implementation-map coverage,
  shared log and both PR descriptions. Evidence documents do not silently
  override contradictory normative text.
- [ ] Run the final affected/full checks and required combined review on the
  resulting bytes. Preserve OS/service NOT RUN and runtime UNEXPOSED limits.
- [ ] Present source commits/diffs, test results, review receipts, A follow-up
  and revision/adoption status. Merge/install/release only under their own gates.
- [ ] At whole-task completion, retire the temporary hook and AGENTS routing
  using the existing SoT checklist; retain evidence and the completed plan.

## Commands and acceptance

Run Python/tests/builds/Git mutations/provider CLIs through `/bin/zsh -lic`
with `sandbox_permissions="require_escalated"` on the first call, outer cwd
`/Users/chaniri/codex_workspace`. Read-only file/Git inspection may use the
default sandbox. Include this exact requirement in every delegated task.

Before Python checks: `command -v python3`, `python3 --version`,
`python3 -m pytest --version` in that environment.

For each unit, use its named complete test modules with:
`python3 -m pytest -q <absolute-test-paths> --rootdir <H> -p no:cacheprovider`.
Expected: all affected tests pass; record exact counts/skips and failure cause.
The final full suite uses the same command with `<H>/tests`.

Shared changes: run `python3 tools/check_authoring.py` and
`python3 -m pytest -q tests -p no:cacheprovider` from S, plus `git diff --check`.
These establish structure/regression only, not semantic approval or adoption.

## Plan self-review

- Coverage: old OPEN-B and CHECK-B clusters are assigned above; the ledger is
  reconciled again at U10 because A and shared source continue to move.
- Types: existing public result/receipt contracts remain stable unless a shared
  design change is explicitly resolved. Unsettled interfaces in U6/U7 have
  investigation/decision steps before implementation, not fabricated signatures.
- Scope: the five review-focus boundaries have owning tests. Optional parser
  restrictions and uncaptured quota carriers are evidence tasks, not guards.
- Method: sequential product ownership, parallel bounded research, minimal
  prompt changes and Luna/high contextual probes implement the owner's request.
