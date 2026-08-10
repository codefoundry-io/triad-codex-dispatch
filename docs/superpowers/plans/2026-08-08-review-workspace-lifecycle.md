# Review Workspace Lifecycle Implementation Plan

> **For agentic workers:** Use `superpowers:executing-plans` and
> `superpowers:test-driven-development`. Task 0 is the owner-directed bootstrap repair required to
> create a valid gate packet. Do not implement later lifecycle integration before the formal-plan
> gate in Task 1.

**Goal:** Add deterministic, collision-safe review workspace allocation, bounded cleanup, and
unambiguous UTF-8 string transport without adding persistent coordination state or restricting
installed reviewer tools.

**Architecture:** Extend `bin/review_round.py` with `prepare`, `manifest`, and `cleanup`. `prepare`
validates a JSON string-array allow-list, sweeps exact-prefix roots older than 30 days, atomically creates one
system-temporary root from the leader-supplied review ID, and copies regular-file bytes into the
fixed shared-source layout. `manifest` directly hashes completed packet files into a deterministic
JSON manifest. `cleanup` derives that same exact root from the ID and removes it with
the standard symlink-resistant tree remover. A marker outside `shared/` records lifecycle activity;
successful CLI manifest/capture/render/verify touches it. The active plan or `TASK.md` carries the review ID
and returned root; the snapshot, JSON-escaped rendered metadata, and admitted results carry the captured digest.
There is no registry, daemon, database, heartbeat, or global pointer. A bounded `_common.py` change
prevents an explicitly configured round log root from falling back outside that root; ordinary
unconfigured wrapper behavior stays unchanged.

**Tech stack:** Python 3.12 standard library, argparse, pytest, Markdown skill contract.

## Owner-approved constraints

- System temp root with exact `triad-review-<review-id>` naming and exclusive creation.
- Same ID collides and fails; different IDs from the same current directory are isolated.
- Exact regular-file allow-list copy; no `.git`, symlink, unsupported entry, glob, or inferred
  closure.
- UTF-8 JSON strings with deterministic `ensure_ascii=True` serialization for member paths,
  manifest paths, and dynamic review metadata; no Base64/raw-byte path layer or legacy parser.
- Normal cleanup after all legs, final integrity, and adjudication are consumed.
- Interrupted residue is swept only by a later `prepare` after more than 30 days of inactivity.
- The canonical system-temp `triad-review-` namespace is lifecycle-owned; manual and durable roots
  do not use it.
- Durable handoffs are prepared directly at an owner-approved durable destination.
- No daemon, scheduler, DB, registry, heartbeat, source archive, closure limit, monitor, user-setting
  mutation, safe mode, or installed-tool suppression.
- Preserve the owner-approved `_prepared_digest` algorithm. The rejected standard-tool replacement
  is not part of this lifecycle plan or either formal review gate.
- Commit, push, and local installation are authorized only after the amended plan gate, implementation
  verification, fresh pre-merge gate, and regenerated distribution proof. Tagging, publishing, and
  release remain out of scope.
- Direct Python and pytest commands run through `/bin/zsh -lic` from
  `/Users/chaniri/codex_workspace` using literal `python3`.

## Frozen pre-bootstrap basis

These hashes are the historical lifecycle pre-implementation snapshots. Tracked files use their Git
basis as the review-diff origin. The untracked design spec was restored byte-for-byte at the listed
hash before editing, so its hash is provenance evidence while `REVIEW.diff` represents it as a new
working-tree file. The owner-directed Task 0 correction supersedes only the formal tool-selection
bytes and adds the packet-workflow bootstrap:

- `bin/review_round.py`: `0660d3f3b1f934937ea101635d33869e268196942e46416412e3c9f7ac7c3299`
- `tests/test_review_round.py`: `0aa007e0f8c4e8e312b8900de523a1cfeac972c94667e3a86480499c75b21101`
- `skills/triad-cross-family-review/SKILL.md`: `547f615f7946543e9e7b9480cfd03201c662ee55c7e07b545460810a9157cd7b`
- `tests/test_distribution_contract.py`: `36d7db49c46bfad383a7e58fa40f0b56328a296f1bcf25db4da59d2ce0116cbd`
- `CHANGELOG.md`: `57d838daa86e3c8461ad61b607e4d383a255d6dae642b204dff469fc29da0c58`
- `bin/_common.py`: `ff36f54e79a162e0478134d4f44ee2c95ad91ef2e6f3f86f266d02badf9d1c26`
- `tests/test_log_cleanup.py`: `baa1b2832321ae6bce138936f13eb1f252a55ee7e394bb4cd13011d1f3369933`
- design spec: `ebaa0e20f9c00ff825b788ff3b0cff399e4d98f1a5d7792785be8a160a739538`

Historical post-R30, pre-Task-2 admitted-plan candidate hashes. These values
record that completed gate only; they are not a current-candidate ledger and
must not be compared with later lifecycle or JSON-amendment bytes. Current
rounds bind current bytes through their generated packet manifest and capture
snapshot, and Tasks 9 and 11 regenerate final verification and clean-HEAD
distribution evidence. This plan is not self-hashed in this historical ledger
because that value would be recursive:

- `bin/review_round.py`: `22600b361e2fc0a7d05d4d710cbc7bd6af1fcf56e5ed837c9fdd4727b1c7cfd7`
- `tests/test_review_round.py`: `47d9b415f50e819f3145c53eb722d934dadee1acb5b5f47275d48ebe513de31d`
- `skills/triad-cross-family-review/SKILL.md`: `675d5e3182c9441c13b2eec8e198bf509b44dac7485cf661641dfb25599a41d4`
- `skills/triad-antigravity-dispatch/SKILL.md`: `3df652baed00ab30ee78a486019091c21bab8c726d70b50509e56d6130b33a2a`
- `skills/triad-cross-family-review/references/leg-contracts.md`: `b58c8bd54a6c1ace2a46df523f7050ebe577a6d0d983558709d13bfcba9e471b`
- `skills/triad-cross-family-review/references/review-prompt-contract.md`: `1aac8f6ed438c6590fce3fb9caa8c45239468b8f99889312de2ac25e9e60453d`
- `skills/triad-cross-family-review/references/reviewer-routing.md`: `704d4bc4d89978a754fabcb1d12148fb64b2bfa92270378b7944c513ea7414ae`
- `tests/test_distribution_contract.py`: `51db0f4cdf8df38371490dd15b7685b7083a1cf55007525d1b51154804bf66ff`
- `tests/test_provider_wrappers.py`: `29833ad2d2610ee902878795d26ebf8b093f0113d1896f09d18dfb2d02cecf38`
- `tests/test_review_policy_benchmark.py`: `57b9d7b2e3a69016dbc20e6e7fef219e42cf64243cade525d3876d6a3a32bfd2`
- `CHANGELOG.md`: `1dad157ad730a00d352596f39313ec509f8852f7b4e6129de33a7122db0f7bab`
- `bin/antigravity_wrapper.py`: `123c408e801037c179e61e6f6c121f6cfe3fce5c4342b64d558a310700f09758`
- `tests/test_antigravity_stream_json.py`: `ed42e9f2334a5a078e968f5b55d5f5666b1ed019700ec39715ad50284c0ada20`
- `bin/_common.py`: `ff36f54e79a162e0478134d4f44ee2c95ad91ef2e6f3f86f266d02badf9d1c26`
- `tests/test_log_cleanup.py`: `baa1b2832321ae6bce138936f13eb1f252a55ee7e394bb4cd13011d1f3369933`
- `docs/status/2026-08-05-next-session-handoff.md`: `5ab7aabe58c21ac9f53270c23a5e4e55c7d194b4f581db43fd1a6e6afb7bbad6`
- `docs/status/2026-08-08-triad-maintenance-decisions.md`: `ff11a382170684a88c16e571796af89bd22ac5cb482181073256ada3a963f70b`
- `docs/superpowers/plans/2026-08-05-triad-0.2.533-owner-decisions-and-release.md`: `c80489e3e594ba31dd15dc01126dba03f8acc4c6b44a6cd396a9e56b9e7395b6`
- `docs/superpowers/plans/2026-08-08-formal-review-contract-remediation.md`: `5618085e09cff1820090e504a746455e0165849271401aaea35bd8ab2025e67c`
- `docs/superpowers/plans/2026-08-08-triad-maintenance-decisions.md`: `653a77c6cf784fe8ba752231abb0872cb5c55e1c5eb4a37958ba9e61a59570af`
- design spec: `fd7c70155d46f05adee5a7ed2eb81e13f45f6f93ecc2dda842d0458d2083e9ea`

---

### Task 0: Repair the packet workflow before another dispatch

**Files:**
- Modify: `bin/review_round.py`
- Modify: `tests/test_review_round.py`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `bin/antigravity_wrapper.py`
- Modify: `tests/test_antigravity_stream_json.py`
- Modify: provider review contracts and their focused tests

- [x] **Step 1: Remove formal read/search tool suppression with RED/GREEN evidence**

The owner superseded `--formal-read-tools`. Preserve provider-native, installed CLI, configured MCP,
and approved web read/search tools. Keep only the prompt-controlled no-mutation, no-external-state,
and no-candidate-execution contract.

- [x] **Step 2: Make packet workflow defects fail closed in the skill**

A bad preparation/capture/dispatch path invalidates the round. Fix the skill/tool and a regression
test before another dispatch; never manually rebuild a packet as a bypass.

- [x] **Step 3: Implement only the bootstrap lifecycle core with TDD**

Implement exact-list `prepare`, exact-root `cleanup`, next-prepare 30-day stale cleanup, and
lifecycle packet source/artifact/manifest validation. Do not add activity propagation, log fallback
changes, output-path enforcement, a registry, state machine, artifact list, or provider changes in
this bootstrap step.

- [x] **Step 4: Restore AGY's native headless auto-approval route**

R12 proved that version/model catalog checks can pass while a headless call still exposes
`permission_mode: "request-review"` and auto-denies a harmless read command. A comparison with the
working Claude-led wrapper, official AGY examples, and a live A/B probe identified the missing
`--dangerously-skip-permissions` argv element. The wrapper inserts that fixed element internally;
callers do not pass a permission option. Remove the rejected init-preflight implementation. Do not
edit user settings, add a sandbox or command-specific allowlist, or suppress installed tools.
Retain the existing caller-facing `--preflight-only` version/route receipt. It does not inspect
permission state; only the rejected `--init-preflight` and `--expected-permission-mode` paths remain
removed.

- [x] **Step 5: Use the repaired CLI for the fresh Task 1 formal-plan round**

No hand-built or copied prior packet is admissible. Task 0 changes are part of the Task 1 reviewed
candidate and may be revised only from reproduced findings inside the approved design.

---

### Task 1: Pass the lifecycle formal-plan gate

**Files:**
- Review: `docs/superpowers/specs/2026-08-08-review-workspace-lifecycle-design.md`
- Review: `docs/superpowers/plans/2026-08-08-review-workspace-lifecycle.md`
- Review the complete changed closure: current `bin/review_round.py`,
  `bin/antigravity_wrapper.py`, `bin/_common.py`, `tests/test_review_round.py`,
  `tests/test_antigravity_stream_json.py`, `tests/test_log_cleanup.py`,
  `tests/test_distribution_contract.py`, `tests/test_provider_wrappers.py`,
  `tests/test_review_policy_benchmark.py`, `skills/triad-antigravity-dispatch/SKILL.md`,
  `skills/triad-cross-family-review/SKILL.md`, every cross-family reference, the current changed
  status/release-plan documents, `README.md`, `README.ko.md`, and every path in the candidate-hash
  ledger. Include the tracked benchmark fixture tree because its changed inventory test reads those
  files directly.
- Include every affected unchanged path directly opened by an in-closure distribution test:
  `.codex-plugin/plugin.json`, `SECURITY.md`, `skills/triad-claude-dispatch/SKILL.md`,
  `skills/triad-gemini-dispatch/SKILL.md`,
  `bin/claude_wrapper.py`, `bin/gemini_wrapper.py`, `bin/verdict_schema.py`,
  `bin/review_policy_benchmark.py`, `tests/test_verdict_schema.py`,
  `docs/superpowers/plans/2026-08-05-agy-1.1.10-formal-route.md`, and
  `docs/superpowers/specs/2026-08-05-agy-1.1.10-formal-route-design.md`.
- Include `scripts/bootstrap.sh` and `scripts/verify_distribution.py` as leader verification/release
  tooling, plus `docs/references/repair-protocol.md` as the governing document referenced by the
  current handoff. Together these categories form the same 62-member closure required by Tasks 5
  and 6.

- [x] **Step 1: Prepare one fresh-ID review directory**

Include the spec, plan, frozen hashes, current affected files/tests/contracts, `TASK.md`,
`SOURCE_SHA256SUMS`, and one content-only readable diff from the frozen lifecycle basis to the plan
candidate. Do not include any earlier round's task, diff, manifest, snapshot, prompt, status, or
verdict. The prior formal-contract R3 packet is contaminated by such historical inputs and is
advisory only, not an admitted basis. Exact test-source exclusion within the 62-member direct-reader
closure: none; full-suite totals also count unrelated test modules outside that review closure.

- [x] **Step 2: Dispatch all three legs before consuming results**

Use Claude `opus`/`xhigh`, Google
`gemini-3.1-pro-high`/`high`, and fresh Codex `gpt-5.6-terra`/`xhigh`/
`fork_turns=none`. Permit provider-native, installed CLI, and configured MCP read/search tools
under the approved boundary. Do not suppress installed tools. Set the existing
`TRIAD_DISPATCH_LOG_DIR` to the current review root's
`results/_logs` for provider wrappers. Mutation, external-state change, or candidate execution
invalidates a leg.

- [x] **Step 3: Admit the plan**

Require three schema-valid `SAFE` verdicts for one digest and `ROUND_INTEGRITY_OK`. Reproduce every
finding. Any proposed design expansion returns to the owner before implementation.

R8 was a valid but non-admitted round over digest
`e0ac0ca7440391f31fdb1a38f545ab5562fb7ceb31c244dab3545e6acd22c9d0`: Google returned
`SAFE`; Claude and fresh Codex returned `NOT-SAFE`; final integrity was `ROUND_INTEGRITY_OK`; exact
cleanup returned `removed: true`. Reproduced defects were source-copy check/use replacement,
dangling-symlink deletion false success, and lifecycle-shaped wrong-temp capture fail-open. The
bounded corrections and RED tests are part of the next fresh-ID candidate.

R9 over digest `8447ece6823ea9d48ac0d142a9b5fca2d6e97d6f15ec9c4c8b9ce12eacfaab45` was
invalid because the Google leg was denied the manifest verification command and returned no schema
verdict. Claude and fresh Codex results are advisory only. The exact R9 root was removed. The AGY
route then relied on an ambient owner-selected setting; a same-route smoke exposed init
`permission_mode: "always-proceed"` and verified every manifest entry. R12 later proved that this
was not a durable headless route contract. The R9 advisory stale-delete/recreate finding assumes
concurrent reuse of one review ID. The owner rejected directory-wide locking as over-design: every
retry uses a new unique ID, earlier IDs are never reused, and exclusive root creation remains the
collision guard.

R10 (`20260809-review-workspace-lifecycle-plan-r10`) reviewed one 65-entry current packet over
digest `53e97699dc22c1b445ef609fd9b96d6863eee0435d0c2256e6a720c2b3545db2`.
Fresh Codex returned `SAFE`; Google and Claude returned `NOT-SAFE`; final integrity was
`ROUND_INTEGRITY_OK`; exact cleanup returned `removed: true` and the root was absent. The bounded
findings admitted for the next candidate are the renderer's review-ID/lifecycle-root mismatch and
missing exact commands/count expectations in Tasks 3 through 6. Provider capability gates,
permission changes, empty-directory digest records, and file-mode preservation are outside the
owner-approved byte-copy lifecycle and are not adopted.

R11 (`20260809-review-workspace-lifecycle-plan-r11`) reviewed 62 copied current sources plus three
current-round artifacts over digest
`1bf17ff99a4d40638b933d5d25539c460b3961b6a937f04805c2eace0f0b7fbd`. Google returned
schema-valid `SAFE`; fresh Codex and Claude returned schema-valid `NOT-SAFE`; final integrity was
`ROUND_INTEGRITY_OK`; exact cleanup returned `removed: true` and no managed review root remained.
The reproduced bounded corrections are: never sweep the currently requested ID; bind every planned
test addition to an exact collection ledger and final count; add explicit configured-log-root
RED/GREEN coverage; keep English/Korean local-data disclosures aligned; and state exact command
working directories. No provider, permission, MCP, digest, metadata-copy, or coordination change is
admitted.

R12 (`20260809-review-workspace-lifecycle-plan-r12`) prepared a mechanically valid 65-entry packet
at digest `61ac021699779f1078f39c313ded11dfa1324e0f4b9f71f5e9dc2b9bd7ad600a`, but the live AGY init
event exposed `permission_mode: "request-review"` and its `command` tool was auto-denied. The round
is invalid; the still-running Claude and fresh-Codex legs were stopped, exact cleanup returned
`removed: true`, and no managed review root remained. No R12 result may be reused. Before a fresh
round, the wrapper and skill now use AGY's documented headless auto-approval flag as an internal
fixed argv element. The rejected init-preflight and permission-mode caller arguments were removed.
This correction does not edit user settings or restrict CLI, MCP, read, or search tools; the review
prompt and integrity fingerprints enforce the no-mutation contract.

R13 (`20260809-review-workspace-lifecycle-plan-r13`) reviewed 62 current source members plus three
current-round artifacts at digest
`6b975105866dbb69b6ae7065125b54a44ddad53512f1b5edf9582ad267b4beb9`. Its bytes remained intact,
all three legs returned schema-valid `NOT-SAFE`, final verification printed
`ROUND_INTEGRITY_OK`, exact cleanup returned `removed: true`, and no managed root remained.
However, the leader-written `TASK.md` incorrectly called a standard-tool digest replacement
owner-approved even though the durable Decision 1 explicitly keeps `_prepared_digest` unchanged.
R13 is therefore formally invalid and every verdict is advisory. The Google digest claim is
refuted by the owner-approved basis and causes no runtime change. Independently reproduced bounded
plan corrections reconcile Task 4 skill wording, define the configured-log-root case as a
subprocess whose environment is set before `_common` import, and enumerate both README languages
plus every changed test/contract in Task 1 and Task 5 evidence. The existing library test remains
the single expected-root mismatch contract, so no duplicate CLI case is added. Claude's proposed
future AGY permission-state gate is not adopted: it is a hypothetical capability layer that
conflicts with the owner-approved internal flag, unrestricted-tool, no-preflight design, and the
R13 Google call completed through that route.

R14 (`20260809-review-workspace-lifecycle-plan-r14`) reviewed 62 freshly copied source members plus
three current-round artifacts at digest
`42cca50d2d6bfdea3e45902e2fed9e5ac561d1e908b7f52841921feea18b1095`. Fresh Codex returned
schema-valid `SAFE`; Google and Claude returned schema-valid `NOT-SAFE`. The leader reproduced
Google's and Claude's shared README-enumeration finding and changed the canonical plan before the
Claude leg terminated, so final verification correctly stopped with `worktree fingerprint
mismatch`. R14 is formally invalid for both the non-convergent verdicts and that leader sequencing
error. Exact cleanup returned `removed: true`, the root is absent, and no R14 result is reused.

The next candidate includes only reproduced bounded plan corrections: Task 1 names both README
languages; Task 3 adds one case that rejects a managed review-root descendant unless it is the exact
`shared/` child; all downstream count ledgers include that case; and Task 5 names its literal Git
working directory. Future round evidence describes the retained-decision guard precisely as a
documented skill rule pinned by a contract test, not as a semantic comparator that does not exist.

R15 (`20260809-review-workspace-lifecycle-plan-r15`) regenerated the 62-source direct-reader
closure, three current-round leader artifacts, and a 65-line manifest at digest
`cc8623c2bc2fb44ffdd655d598f7de1e4f1c17d497b26903224a12b6d4574364`. Fresh Codex and Google
returned schema-valid `SAFE`; Claude returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`, the root is absent, and no R15 result
is reused.

Canonical reproduction admitted only plan completeness corrections: four packet-validation RED
cases and their downstream counts, the full direct-reader closure in Tasks 1 and 5, the managed
descendant implementation rule, isolated `TMPDIR` for every new subprocess test, and inventory
assertion before the disposable smoke root is cleaned. R14's actual sequencing defect also required
the existing skill/test correction: the skill now forbids canonical worktree mutation until every
required leg terminates and verify prints `ROUND_INTEGRITY_OK`; the existing contract test was
observed RED then GREEN without changing collection counts. No provider, permission, MCP, digest,
benchmark, closure-ceiling, or coordination change is admitted.

R16 (`20260809-review-workspace-lifecycle-plan-r16`) regenerated the same 62-source direct-reader
closure plus three current-round leader artifacts and a 65-line manifest at digest
`1cdebe33ab207b67e79c221e71378910d8c5f0115f6fc71f4467d9ffbec2ce73`. Google returned
schema-valid `SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`; final verification
printed `ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`, the root is absent, and no R16
result is reused.

Reproduced bounded corrections update the restart handoff from the stale 454-case snapshot to the
current 457-case baseline; make one named managed-descendant case exercise capture, render, and
verify; preserve the existing direct-child rejection for lifecycle-shaped roots; distinguish
already-implemented regression coverage from genuinely RED behavior; mark the worktree-ordering
skill assertion already satisfied; and require sibling preservation in the planned CLI smoke.
Fresh Codex's proposed removal of `--preflight-only` is not admitted. That existing option emits a
version/route receipt without provider submission and is unrelated to the rejected permission
`--init-preflight`/`--expected-permission-mode` paths. The R16 `TASK.md` phrase "or preflight" was
overbroad; the current changelog and this plan now state the retained distinction explicitly.

R17 (`20260809-review-workspace-lifecycle-plan-r17`) regenerated the same 62-source closure plus
three current-round leader artifacts and validated its 65-line manifest at digest
`9f5da517d0b453cba98abb7a57989d2b837d382cbf84cb368653b1c72227a767`. Claude, Google, and fresh
Codex each returned schema-valid `NOT-SAFE`; final verification printed `ROUND_INTEGRITY_OK`.
Exact cleanup returned `removed: true`, the root is absent, and no R17 result is reused.

Canonical reproduction admitted only bounded plan/spec completeness corrections: direct cleanup
gets one foreign-UID rejection case and the count ledger increases by one; the durable design spec
and current changelog now state the approved Task 3 managed-descendant fail-closed target; Task 3 repeats
its isolated-`TMPDIR` constraint; and the 62-member closure distinguishes direct readers from
leader verification/release tooling and the governing repair protocol. Google's implementation-
stage observations are already assigned to Tasks 3 and 4, so they are not omissions in this
formal-plan gate. Its proposed `--formal-read-tools` addition directly conflicts with the owner-
approved unrestricted-tool decision and is rejected. No runtime, provider, permission, MCP,
digest, benchmark, closure-ceiling, or coordination behavior changes in this correction.

R18 (`20260809-review-workspace-lifecycle-plan-r18`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line manifest at digest
`e006e22e647727adf06869a8c1e8c0f3e13b8d9024573621d152a348dbe4c762`. Fresh Codex returned
schema-valid `SAFE`; Claude and Google returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`, the root is absent, and no R18 result
is reused.

Reproduction admitted only plan/release wording corrections. The R18 task incorrectly described
the explicit round log root as an absent-variable default and attributed sibling proof to the
skill; the next task states that the leader sets the variable and that the CLI smoke proves sibling
preservation. The current changelog no longer claims the planned managed-descendant rule is already
implemented. Task 3 identifies its one genuinely RED managed-descendant case, distinguishes three
RED activity-refresh parameters from six GREEN regression parameters, names deterministic
foreign-UID simulation, and Task 4 pins a failing `RunResult` for the explicit-log-root test. The
plan also makes existing Task 0 regression coverage explicit and adds the already-approved exact-
cleanup residue/sibling confirmation to the planned skill text.

Google's proposed new tests/count increases are not admitted: the current 35-case baseline already
covers duplicate members, `.git`, CR, same/different-ID isolation, concurrent leaf/parent symlink
replacement, invalid-ID/symlink/non-directory sweep skips, and both dangling-symlink removal races.
The plan now classifies those cases as retained baseline coverage rather than new Task 2/3 additions.
No runtime, provider, permission, MCP, digest, benchmark, closure-ceiling, or coordination behavior
changes in this correction.

R19 (`20260809-review-workspace-lifecycle-plan-r19`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line manifest at digest
`57edbe395adf87c3573d8e51df1b1811954a8f64874fe15928efd802f29c5f89`. Google and fresh Codex
returned schema-valid `SAFE`; Claude returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`, the root is absent, and no R19 result
is reused.

Both Claude findings reproduce as bounded plan wording gaps. Task 2 now preserves and names every
existing `PreparedWorkspace` receipt field, including `prompts_dir` and `results_dir`. Task 4 now
states that only the explicit-log-root case is expected RED before its `_common.py` correction;
the collision case, two invalid-argument parameters, and lifecycle-sequence case are Task 0
regression coverage that may start GREEN, with pre-implementation state recorded per case. Counts
and all runtime/provider/permission/MCP/digest/benchmark/closure/coordination behavior remain
unchanged.

R20 (`20260809-review-workspace-lifecycle-plan-r20`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line manifest at digest
`9145e98d097d78217a51355869427c31d7803458d306408f5d616e5d3931daeb`. Google returned
schema-valid `SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`; final verification
printed `ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`, the root is absent, and no
R20 result is reused.

Reproduced corrections remain inside the approved lifecycle design. Task 2 now classifies all ten
new cases as Task 0 regression coverage that may start GREEN. The existing specification word
"may" is pinned to best-effort activity refresh: refresh only an existing regular non-symlink
marker without following links; a missing/unsafe marker or refresh error preserves the successful
operation, output, and exit status. The existing three success-path cases also exercise an unsafe-
marker subcase, so collection counts do not change. Task 4 binds every Claude/Google wrapper call
to `TRIAD_DISPATCH_LOG_DIR=<returned-root>/results/_logs` with an existing distribution-contract
assertion, and the pending release-plan round now uses the returned lifecycle root rather than a
repository `_runs/reviews` directory. No provider, permission, MCP, digest, benchmark, closure-
ceiling, registry, lock, or coordination behavior changes.

R21 (`20260809-review-workspace-lifecycle-plan-r21`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line manifest at digest
`8d17f52dd1c5e2d41a4c27c0873d43f419941e683e5611c8578d5570e16b4333`. Google returned
schema-valid `SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`; final verification
printed `ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`, the root is absent, and no
R21 result is reused.

Reproduced corrections are declarative only. Task 3's file surface now includes the stage-accurate
`CHANGELOG.md` update; its unsafe-marker subcase asserts that the marker stays a symlink and both
external-target bytes and mtime remain unchanged. Task 2's invalid-UTF-8 parameter uses raw bytes.
Task 4 includes `references/leg-contracts.md`, adds the exact log environment assignment to every
Claude, AGY, and Gemini formal template, and extends an existing distribution assertion across the
skill and templates without a new collected case. The release plan labels its completed Task 4
`_runs/reviews` path as historical only and routes every rerun through the lifecycle CLI. Counts and
runtime/provider/permission/MCP/digest/benchmark/closure/coordination behavior remain unchanged.

R22 (`20260809-review-workspace-lifecycle-plan-r22`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line manifest at digest
`b7f21d976406e0ecd3cf2fc3e6767c3d4de5eafade951a3bc71dd9a7160ea6e9`. Google returned
schema-valid `SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`; final verification
printed `ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`, the root is absent, and no
R22 result is reused.

Bounded corrections require no new cases: the managed-root itself and a non-`shared/` descendant
become subcases of the existing lifecycle-operation case; missing-marker success becomes a subcase
of each existing activity success parameter; Task 2 removes two undeclared documentation surfaces;
and retained fallback tests explicitly remove the import-time log environment. Counts stay fixed.

The owner approved the recommended minimal resolution of R22's remaining ambiguity. `prepare`
creates the existing `.last_activity` only after every exact source copy succeeds. Sweep uses marker
mtime only for a regular non-symlink marker and root mtime when the marker is absent or unsafe.
Successful lifecycle operations refresh that exact managed root mtime as a best-effort fallback
when the marker is missing or unsafe, without following or recreating the marker. Failure to update
an existing regular marker triggers no second fallback and does not change the completed operation
result. This reuses existing state and adds no sentinel, registry, lock, or collected case.

R23 (`20260809-review-workspace-lifecycle-plan-r23`) failed pre-dispatch capture because the
leader-generated `SOURCE_SHA256SUMS` used `./`-prefixed paths instead of the canonical paths expected
by the existing validator. The exact root was cleaned with `removed: true`, and no R23 input or
result is reused. The existing distribution case observed RED, the skill now states that each
manifest path is POSIX-relative to `shared/` with no leading `./`, and the same case plus the full
16-case module and skill validation pass. This workflow correction adds no command, mechanism, or
collected case; the next round starts from preparation under a fresh ID.

R24 (`20260809-review-workspace-lifecycle-plan-r24`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`550c13e3bfa057b6da5e9a0c56b3f58c37e4a833fdcaffc3eaf2c70c84706176`. Google returned
schema-valid `SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`; final verification
printed `ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; no managed root remained and
no R24 input or result is reused.

The reproduced corrections remain inside the approved design and add no collected case. The
existing complete-layout case observes marker absence from inside the copy helper, then post-copy
presence. Root fallback applies only to a missing or structurally unsafe marker; an existing regular
marker update failure has no second fallback, and a marker-inspection error is skipped and reported.
Task 4 adds accurate internal-AGY-flag wording to its existing public-doc and distribution-test work,
transitions the lifecycle changelog claim only after GREEN, and marks the already-landed release-plan
reconciliation satisfied. Counts and lifecycle mechanisms remain unchanged.

R25 (`20260809-review-workspace-lifecycle-plan-r25`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`d3ded087d74eb35f134cade57f2e62d91aba22553d8d33419c9060d2fac4bc77`. Google and fresh Codex
returned schema-valid `SAFE`; Claude returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; no managed root remained and no R25
input or result is reused.

The reproduced corrections add no mechanism or collected case. Existing activity-success parameters
reset root mtime after marker mutation, distinguish regular-marker root non-refresh from missing or
unsafe fallback refresh, and include regular-marker update failure as another subcase. The existing
managed-prefix baseline case includes marker-inspection failure as a skipped/preserved subcase. The
complete-layout test is labeled as a new Task 2 case, and explicit log-root configuration requires a
present non-empty value. All ledger totals remain unchanged.

R26 (`20260809-review-workspace-lifecycle-plan-r26`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`da39777700c1f21d8935c714c9066ae345b718fedab9e56b6a5c32975fd26ec5`. Claude, Google, and fresh
Codex returned schema-valid `NOT-SAFE`; final verification printed `ROUND_INTEGRITY_OK`. Exact
cleanup returned `removed: true`; no managed root remained and no R26 input or result is reused.

Accepted corrections add no collected case: pin marker mtime and write-intent opening in the existing
update-failure subcase; extend the existing root-mtime sweep case across absent, symlink, and
unsupported markers; fold source-parent and malformed-manifest branches into existing planned cases;
and align Task 4 wording with its one module command. Google's unexpected-member claim is contradicted
by the existing prior-round-artifact regression. The hard-link marker proposal would add a new
`st_nlink` validator beyond the owner-approved leader-owned-root and regular-non-symlink marker
boundary, so it is rejected rather than expanding the design. Counts and mechanisms remain fixed.

R27 (`20260809-review-workspace-lifecycle-plan-r27`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`dde39feb860b58a9b1c53416ddc93d5152c7cbd9aa07128437367ab80cee07af`. Claude and Google returned
schema-valid `SAFE`; fresh Codex returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; no managed root remained and no R27
input or result is reused.

The reproduced R27 correction reuses `_validate_lifecycle_packet` before `verify_round` can succeed
and extends the one planned manifest inventory/syntax case with a digest-matching verification
subcase. Claude's three Minor clarifications pin the existing blank-line normalization, ordinary
non-root permission-failure test premise, and no-fallback refresh-inspection-error branch. No test
count, lifecycle mechanism, tool restriction, or owner boundary changes.

R28 (`20260809-review-workspace-lifecycle-plan-r28`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`2123e0b1c9214b4bef76be079a7c15aaa5f89904650f25f8bbcd923d5396eb83`. Google and fresh Codex
returned schema-valid `SAFE`; Claude returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; no managed root remained and no R28
input or result is reused.

The R28 correction only classifies the existing digest-matching verification subcase as mandatory
RED and records the already approved verify-side validator reuse as a pending target in the current
changelog. Both entries transition only after GREEN. Counts, mechanisms, and boundaries remain fixed.

R29 (`20260809-review-workspace-lifecycle-plan-r29`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`b66260299989b97dfe913070d45520be57ab6fafe0918612f5939936fc512467`. Google returned schema-valid
`SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; no managed root remained and no R29
input or result is reused.

The R29 corrections add no case or mechanism: Task 0-supplied lifecycle cases are explicitly GREEN-
eligible regression coverage; the existing three activity-success parameters include a deterministic
marker-inspection-error subcase; and the planned import-time configured-log-root boolean joins the
existing `_PATCHED_ATTRS` test snapshot/restore contract. Google's packet wording Minor is corrected
only in later packet descriptions from identity-checked deletion to identity-checked copying.

R30 (`20260809-review-workspace-lifecycle-plan-r30`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`58b02cf6eaedafebc37c90c7f19995504e1af53e6dfdb81ef27a759bedc45051`. Claude, Google, and fresh
Codex returned schema-valid `SAFE`; final verification printed `ROUND_INTEGRITY_OK`. Exact cleanup
returned `removed: true`; no managed root remained. The formal plan gate is admitted and no R30
packet or result is reused.

Claude's SAFE Minor clarifications add no case or mechanism: the packet/full-suite evidence scope,
in-process temp-base monkeypatch, post-marker-mutation root-mtime reset, Task 2 per-case state record,
macOS execution versus Linux API/gate analysis, and one grammar correction are folded into execution.

---

## Exact test collection ledger

The post-R22-bounded-correction, pre-Task-2 baseline is exactly `35` cases in
`tests/test_review_round.py`, `88` cases in the focused three-module command, `15` cases in
`tests/test_antigravity_stream_json.py`, and `457` cases in the full suite. The remaining tasks add
only the cases listed below:

The 35, 88, and 15 baselines are reproducible from the 62-member direct-reader review closure. The
full-suite column additionally counts unrelated test modules outside that closure.

| Gate | New collected cases | `test_review_round.py` | Focused total | Full total |
|---|---:|---:|---:|---:|
| Task 2 complete | 13 review-round cases | 48 | 101 | 470 |
| Task 3 complete | 23 review-round cases | 71 | 124 | 493 |
| Task 4 complete | 4 review-round + 1 log-cleanup case | 75 | 129 | 498 |
| Task 8 complete | 3 review-round cases | 78 | 132 | 501 |

`tests/test_distribution_contract.py` remains exactly 16 collected cases at every gate in this
ledger; Task 8 extends an existing assertion and adds no collected distribution case.

Every row requires the exact collected count and the same passed count, with zero failed, skipped,
or xfailed. If a newly reproduced gap needs another case, amend this ledger and every downstream
expected total before adding that case; never accept an observed count after the fact.

---

### Task 2: Complete exact workspace preparation coverage with TDD

**Files:**
- Modify: `bin/review_round.py`
- Modify: `tests/test_review_round.py`

**Bootstrap state:** Task 0 already supplies the interfaces and the core exact-copy, isolation,
symlink-rejection, stale-sweep, and partial-cleanup behavior needed to construct the formal-plan
packet. This task keeps that work and adds only missing boundary coverage or the smallest correction
needed by a reproduced RED case.

**Interfaces:**
- `prepare_review_workspace(review_id, source_root, member_list, *, temp_root=None, now=None)`
- preserve the Task 0 result fields verbatim and add none: `review_id`, `root`, `shared_dir`,
  `source_dir`, `prompts_dir`, `results_dir`, `member_list`, `copied_count`, `swept_roots`, and
  `skipped_roots`; the CLI emits that complete result as compact JSON

- [x] **Step 1: Add the remaining layout and exact-copy regression coverage**

Add tests proving the preparation behaviors listed below. These cases pin Task 0 behavior already present except for the
owner-approved post-copy marker ordering, which the new
`test_prepare_creates_complete_layout_and_metadata` case added in this step must observe RED before
its smallest correction:

- creates `<temp>/triad-review-<id>` exclusively with `.last_activity`, normalized
  `member-list.txt`, `shared/source/product`, `prompts`, and `results`;
- uses one canonical `Path(tempfile.gettempdir()).resolve(strict=True)` base and creates the fixed
  layout and member list immediately after the exclusive root, then creates the marker only after
  every exact member copy succeeds; a copy-interrupted partial root has no marker;
- copies only the normalized member-list files with byte-identical content and no `.git`;
- returns deterministic paths/counts; and
- removes its own partial root if copying fails.

Add exactly three collected cases in this step:

- `test_prepare_creates_complete_layout_and_metadata` (1);
- `test_prepare_preserves_blank_lines_and_path_whitespace` (1); and
- `test_prepare_accepts_200_character_review_id` (1).

The blank-line/whitespace case proves that truly empty input lines are ignored without error while
non-empty path whitespace is preserved byte-for-byte in both the accepted member set and the
normalized `member-list.txt`.

In the newly added `test_prepare_creates_complete_layout_and_metadata` case, wrap the existing `_copy_source_member`
helper with a monkeypatched observer that asserts `.last_activity` is absent at each copy call and
then delegates to the original helper. After `prepare` returns, assert that the marker exists. This
one Task 2 case is expected RED against Task 0's pre-copy marker creation; marker ordering does not
add a fourth Step 1 case or a cleanup bypass.
Record the pre-implementation state per case instead of claiming all three additions were RED.

Run:

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py -k "test_prepare_" -q'
```

Expected before adding Task 2 cases: exactly 14 selected tests pass. Record the selected and passed
counts on every run.

- [x] **Step 2: Add containment/concurrency regression coverage and RED tests**

Retain the Task 0 baseline cases for duplicate members, absolute/traversing paths, `.git`, an
initial leaf symlink, same-ID collision, different-ID isolation, CR rejection, and deterministic
post-validation leaf/parent replacement with a symlink. Add only the remaining cases for
non-normalized paths, UTF-8 BOM, NUL, invalid UTF-8, a missing file, an initial parent symlink,
unsupported entries, and invalid review IDs. Every rejected case must leave canonical source bytes
unchanged and every post-validation replacement must retain fail-closed partial cleanup.

Add exactly ten new collected cases in this step; the retained Task 0 cases above are already part
of the 35-case baseline and are not counted again:

- extend `test_prepare_rejects_unsafe_member_lists` with non-normalized path, UTF-8 BOM, NUL, and
  invalid-UTF-8 parameters (4); carry raw bytes in the parametrization so the invalid-UTF-8 case
  reaches the decoder instead of attempting to encode an invalid value from `str`;
- `test_prepare_rejects_missing_or_non_directory_parent_source_member`, exercising both a missing
  leaf and an intermediate regular-file component in one collected case (1);
- `test_prepare_rejects_initial_parent_symlink` (1);
- `test_prepare_rejects_unsupported_source_entry` with directory and FIFO parameters (2); and
- `test_prepare_rejects_invalid_review_id` with 201-character and invalid-leading-character
  parameters (2).

All ten additions exercise Task 0 behavior and may start GREEN. Record the pre-implementation
state per case; require RED evidence only if one of them proves a boundary is actually missing.

- [x] **Step 3: Harden the existing preparation helpers only for reproduced gaps**

Preserve the Task 0 helpers and add or change only what a Step 1 or Step 2 RED case proves missing:

- constants for prefix, activity marker, and 30-day age;
- a frozen result dataclass;
- one resolved canonical system-temp and review-root derivation;
- strict UTF-8 member-list parsing and POSIX-relative normalization;
- source-component symlink/regular-file checks;
- descriptor-relative `O_NOFOLLOW` reopening with expected device/inode identity, regular-file
  size/mtime checks, and byte copying into a newly allocated root;
- `.last_activity` creation only after every exact source copy succeeds;
- explicit `skipped_roots` reporting for every ineligible prefixed direct child; and
- partial-root cleanup limited to the root created by this call.

Use `Path.mkdir(mode=0o700, exist_ok=False)` for the review root. Do not add a random fallback,
lockfile, registry, retry, batch, or archive.

- [x] **Step 4: Run GREEN preparation tests**

Run:

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py -k "test_prepare_" --collect-only -q'
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py -q'
```

Expected: exactly `27` prepare cases collected and exactly `48 passed` for the module, with zero
failed, skipped, or xfailed. Any other count stops Task 2 and requires the ledger to be reconciled
before implementation continues.

---

### Task 3: Complete cleanup, stale-sweep, and activity coverage with TDD

**Files:**
- Modify: `bin/review_round.py`
- Modify: `tests/test_review_round.py`
- Modify: `CHANGELOG.md`

**Interfaces:**
- `cleanup_review_workspace(review_id, expected_root, *, temp_root=None) -> CleanupResult`
- stale sweep invoked only by `prepare_review_workspace`
- lifecycle activity touch invoked after successful CLI manifest/capture/render/verify

**Bootstrap state:** Task 0 already supplies exact-root cleanup, idempotent missing-root handling,
same-namespace stale sweeping, and symlink-target preservation. Keep those bytes, add the listed
regression coverage, and implement only the explicitly RED boundaries and activity refresh.

- [x] **Step 1: Add regression coverage and RED tests for remaining lifecycle boundaries**

Cover:

- exact-root deletion with `removed=True`, matched missing-root idempotence with `removed=False`,
  and expected-root/temp-base mismatch failure;
- sibling review root and external symlink target preservation;
- root-symlink and unexpected-type rejection;
- recent complete-root retention and strictly older-than-30-day complete-root removal by marker;
- reserved-namespace current-UID valid-ID marker-absent partial-root retention/removal by root mtime;
- foreign-UID, invalid-ID, root-symlink, and non-directory prefix entries skipped and reported;
- a validated cleanup or sweep root replaced by a dangling symlink before removal completion must
  remain an error, never `removed: true`;
- a lifecycle-shaped `triad-review-<id>/shared` path outside the current canonical temp base must
  fail packet capture rather than bypass lifecycle validation;
- a canonical managed review root itself, or any path beneath it that is not its exact `shared/`
  child, must fail lifecycle capture/render/verify instead of being treated as an unmanaged packet;
- direct cleanup must reject a foreign-UID derived root and leave it present;
- lifecycle packet capture and verification must reject a missing copied source member, manifest path-set omission
  or addition, malformed separator/digest or invalid UTF-8, unsorted manifest paths, and a content-
  digest mismatch;
- a target absent before deletion or absent after a top-level race reported as already removed,
  while an error that leaves the root present stops; and
- eligible-root deletion failure propagation without ignoring it or using a stronger retry.

The 35-case baseline already covers invalid-ID, symlink, and non-directory managed-prefix skips in
`test_prepare_reports_ineligible_managed_prefix_entries`, plus both cleanup and sweep dangling-
symlink replacement races. Extend that existing managed-prefix case with a marker whose `lstat`
raises a non-`FileNotFoundError` `OSError`, using a path-specific monkeypatch, and assert the eligible
root is reported in `skipped_roots` and remains present. Retain these cases without counting them
again below. The baseline
`test_capture_rejects_extra_prior_round_artifact_in_lifecycle_packet` already proves that an
unexpected lifecycle packet member is rejected.

Add exactly fourteen new collected cases in this step:

- `test_cleanup_rejects_unsafe_root_type` with symlink and non-directory parameters (2);
- `test_prepare_sweeps_partial_roots_by_root_mtime`, covering marker absence plus symlink and
  unsupported-type marker subcases in the same collected case; each proves retention at or below and
  removal strictly above the 30-day floor by root mtime, pinning root mtime after each marker mutation
  and immediately before `prepare` (1);
- `test_prepare_skips_foreign_uid_managed_root` (1);
- `test_cleanup_rejects_foreign_uid_managed_root` and proves the root remains (1);
- `test_cleanup_accepts_top_level_disappearance` (1);
- `test_stale_sweep_accepts_top_level_disappearance` (1);
- `test_cleanup_propagates_persistent_removal_error` (1);
- `test_stale_sweep_propagates_persistent_removal_error` (1);
- `test_lifecycle_operations_reject_non_shared_path_under_lifecycle_root`, exercising capture,
  render, and verify against both the managed root itself and a non-`shared/` descendant in one
  collected case (1);
- `test_capture_rejects_missing_lifecycle_source_member` (1);
- `test_capture_and_verify_reject_lifecycle_manifest_inventory_or_syntax_error`, covering an omitted
  path, an added path, malformed separator/digest input, and invalid UTF-8 in one collected case (1);
- `test_capture_rejects_unsorted_lifecycle_manifest` (1); and
- `test_capture_rejects_lifecycle_manifest_digest_mismatch` (1).

The capture-side packet-manifest branches already supplied by Task 0 are regression coverage and may
start GREEN. The verification subcase of
`test_capture_and_verify_reject_lifecycle_manifest_inventory_or_syntax_error` and
`test_lifecycle_operations_reject_non_shared_path_under_lifecycle_root` must each be observed RED
before their smallest implementation correction. The inventory/syntax verification subcase creates
a snapshot whose prepared digest matches the malformed packet and proves `verify_round` still rejects
it semantically; that subcase does not add a collected case.

The first nine collected cases in the list above, through
`test_stale_sweep_propagates_persistent_removal_error`, plus the managed-prefix marker-inspection
extension are Task 0 regression coverage that may start GREEN. Record the pre-implementation state
per case instead of claiming all fourteen additions were RED.

Create the two foreign-UID conditions deterministically by creating each root under the real UID,
then monkeypatching `review_round.os.getuid` to a different value for the operation under test. Do
not use `chown`, privilege escalation, `skip`, or `xfail`.

- [x] **Step 2: Write RED activity tests**

Prove successful lifecycle CLI `capture`, `render`, and `verify` update `.last_activity` only after
the action and its output succeed for the exact `shared/` child of a valid lifecycle root. Failed
operations and non-lifecycle prepared directories must not create or touch a marker.

Add exactly nine collected cases in this step:

- `test_cli_lifecycle_activity_success_paths` parameterized for capture, render, and verify (3).
  Each parameter first pins the managed root to a fixed old mtime, proves a regular marker refresh,
  and proves the root `st_mtime_ns` remains byte-identical. It then replaces the marker with a
  symlink to an external target, resets the root to the fixed old mtime after that mutation, and
  proves a second successful operation preserves its output/exit status and the link while the
  external target's bytes and mtime remain unchanged and the root `st_mtime_ns` strictly increases.
  It removes `.last_activity`, again resets root mtime after the mutation, and proves a third
  successful operation does not recreate the marker while strictly increasing root `st_mtime_ns`.
  Finally, on the ordinary non-root developer/test process used by this macOS/Linux workflow, it
  creates a regular non-symlink marker, sets its mode to `0o400` so the subprocess cannot open it for
  update, resets the root to the fixed old mtime,
  runs a fourth successful operation, and proves output/exit status remain successful, the marker
  remains, and both marker and root `st_mtime_ns` are unchanged. Restore marker mode to `0o600`
  before cleanup. In the same parameter, invoke the command's `main()` path in-process under a
  path-specific `Path.lstat` monkeypatch that raises an `OSError` only for `.last_activity`; restore
  the patch before inspection, monkeypatch `review_round.tempfile.gettempdir` to the same isolated
  canonical `tmp_path` used by the subprocess subcases, and prove successful output plus unchanged marker and root mtimes,
  so an inspection error cannot silently take the root fallback. These are subcases of the same
  three parameters and add no collected case;
- `test_cli_lifecycle_activity_does_not_refresh_after_failure` parameterized for capture, render,
  and verify (3); and
- `test_cli_non_lifecycle_operation_does_not_create_activity` parameterized for capture, render,
  and verify (3).

Only the three success-path parameters are expected RED before activity refresh is
implemented. The six failure/non-lifecycle parameters are regression coverage that may start GREEN;
record the pre-implementation state per case instead of claiming all nine were RED.

Every Task 3 CLI subprocess case sets `TMPDIR` to its isolated canonical `tmp_path`; no Task 3 test
enumerates or deletes children of the developer's real system temp.

- [x] **Step 3: Harden bounded cleanup and add activity refresh**

Before a successful verification result, call the existing `_validate_lifecycle_packet(prepared)`;
digest equality does not replace semantic packet and manifest validation.

Use the validated ID to derive the only deletion target and compare it with the caller's recorded
expected root before inspection. Return a frozen cleanup result containing the derived root and
`removed` boolean. Activity refresh requires the canonical system-temp parent, exact valid-ID name,
current UID, non-symlink root, and exact `shared/` child. Refresh is best-effort after the action and
its output succeed: open an existing regular non-symlink `.last_activity` with
`os.O_WRONLY | os.O_NOFOLLOW`, then update the opened descriptor;
when the marker is missing or successfully inspected as unsafe, do not follow or recreate it and
instead make one best-effort refresh of the exact managed root mtime without following links. If an
existing regular marker cannot be updated, attempt no second fallback. A marker-inspection error
during refresh likewise attempts no fallback. Any refresh failure must
preserve the completed action's output and exit status. Direct cleanup of the exact recorded root
needs the ID-derived name, current UID, and non-symlink directory but may remove an interrupted
partial root.
Sweep only direct reserved-prefix children. Use marker mtime only for a regular non-symlink marker;
use root mtime when the marker is absent or successfully inspected as a symlink or unsupported type.
Skip and report a marker inspection error, foreign entry, or malformed entry. Treat only a post-race `lstat`
`FileNotFoundError` as absence; a dangling symlink is a remaining entry. Preserve the existing rule
that every lifecycle-shaped `triad-review-<id>/shared` root must be a direct child of the canonical
temp base, so a look-alike nested deeper inside that base still fails. Resolve `prepared` relative
to the base; when it is a valid direct managed root or its first component is one, accept only that
root's exact `shared/` child and fail closed for the root itself and every other managed descendant
in capture, render, and verify.
Preserve the packet source/member mapping and sorted complete manifest validation. Stop on any
deletion error while an entry remains. The design spec already states both targets. After each
required RED case turns GREEN, update its current changelog entry from a planned target to an
implemented guarantee; do not claim implementation before that point. Wrap lifecycle filesystem errors as
`RoundIntegrityError`.

- [x] **Step 4: Run GREEN lifecycle tests**

Run all lifecycle tests by running the module in full:

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py -q'
```

Expected: exactly `71` cases collected and exactly `71 passed`, with zero failed, skipped, or
xfailed. Any other count stops Task 3.

---

### Task 4: Finish CLI, log routing, and leader-skill integration

**Files:**
- Modify: `bin/review_round.py`
- Modify: `bin/_common.py`
- Modify: `tests/test_review_round.py`
- Modify: `tests/test_log_cleanup.py`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `skills/triad-cross-family-review/references/leg-contracts.md`
- Modify: `tests/test_distribution_contract.py`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `SECURITY.md`
- Modify: `CHANGELOG.md`

- [x] **Step 1: Add the remaining RED CLI and log-routing tests**

Keep the Task 0 prepare/cleanup round-trip test and add subprocess tests for:

- `prepare --review-id --source-root --member-list` compact JSON and collision failure;
- `cleanup --review-id --expected-root` removal plus explicit `removed: false` idempotent second
  success; preserve the existing library-level expected-root mismatch test instead of adding a
  duplicate CLI case; and
- invalid IDs/paths returning exit 2 with no unrelated mutation; and
- one isolated `test_cli_lifecycle_sequence` covering prepare → capture → render → verify → cleanup
  on one lifecycle root, including exact packet inventory, sibling-root preservation, and
  first/second cleanup results.

Add exactly five collected cases in this step:

- `test_cli_prepare_reports_collision` (1);
- `test_cli_invalid_lifecycle_arguments_fail_without_mutation` with invalid-ID and invalid-path
  parameters (2);
- `test_cli_lifecycle_sequence` (1); and
- `test_configured_log_root_failure_does_not_fallback` in `tests/test_log_cleanup.py` (1).

Only `test_configured_log_root_failure_does_not_fallback` is expected RED before the Step 2
`_common.py` correction. `test_cli_prepare_reports_collision`, both invalid-argument parameters,
and `test_cli_lifecycle_sequence` are Task 0 regression coverage that may start GREEN. Record the
pre-implementation state per case instead of claiming all five additions were RED.

The configured-log-root test starts a subprocess with `TRIAD_DISPATCH_LOG_DIR` set to an unusable
explicit root before `_common` is imported and uses both a failing `RunResult` with
`exit_code != EXIT_OK`, matching the existing `_result()` helper, and a successful result. It
requires `emit_run_log`/`persist_result_artifacts` to return `None`, emit
`run-log-unavailable` for both real configured-root failures, preserve each provider result and exit
code, and create no `triad-<cli>-run-log-*` directory in system temp. The same selector then points
the imported module at a writable configured root and requires successful audit persistence without
a false run-log-unavailable diagnostic. Keep the existing import-time `_LOG_DIR` global, its test
monkeypatch contract, and the existing unconfigured fallback behavior.
Treat explicit configuration as an import-time `TRIAD_DISPATCH_LOG_DIR` value that is present and
non-empty; an absent or empty value retains the unconfigured fallback contract. Record that state in
one module boolean beside `_LOG_DIR`, add that boolean to the existing `_PATCHED_ATTRS` snapshot/
restore contract, and set it false in retained in-process tests that monkeypatch `_LOG_DIR` to exercise
unconfigured fallback. Do not depend on clearing the environment after `_common` was already imported.

Every new subprocess test added by Tasks 3 and 4 sets `TMPDIR` to an isolated canonical `tmp_path`,
including `test_configured_log_root_failure_does_not_fallback`; no test may enumerate or delete
children of the developer's real system temp.

- [x] **Step 2: Preserve parser branches and add bounded explicit-log-root behavior**

The two documented lifecycle subcommands already exist from Task 0. Preserve them and all
non-lifecycle capture/verify/render behavior. When
`TRIAD_DISPATCH_LOG_DIR` has a present non-empty import-time value, make `_common.py` report an
unavailable run-log for an actual configured-root storage failure, including a successful provider
result whose audit record could not be persisted, instead of creating its private system-temp
fallback outside that configured root. A healthy successful result needs no repair run-log and emits
no unavailable diagnostic. An audit append is successful even when its later best-effort rotation
fails; bounded lock contention or lock-name attestation skips are advisory rather than storage
errors. Preserve the existing fallback for absent or empty values and other unconfigured wrapper
calls. The boolean that records this import-time state is internal and follows the existing test
snapshot/restore contract; it is not a new user-facing setting. Formal round dispatch never passes
`--debug`.

- [x] **Step 3: Add RED assertions for any remaining distributed-contract gaps**

Require the public skill to state:

- fresh review ID recorded before preparation;
- system-temp exclusive `prepare` and exact allow-list copy;
- review ID and returned root in active `TASK.md` or plan, with the digest carried mechanically by
  the snapshot, rendered prompts, and admitted results;
- normal `cleanup` only after final integrity and adjudication;
- next-run 30-day sweep for interruptions;
- same-ID collision and different-ID isolation; and
- current-round-only prepared bytes with no prior-round task, diff, manifest, snapshot, prompt,
  status, or verdict; and
- member-list IPC, every source member mapped to `shared/source/product/<member>`, and only
  `TASK.md`, `REVIEW.diff`, `SOURCE_SHA256SUMS`, and optional `EVIDENCE.md` outside that tree;
- packet-workflow failure invalidates the round and requires the skill/tool plus a regression test
  to be fixed before a fresh-ID restart, with no manual packet rebuild;
- snapshots and verdicts routed under the current review root, with every Claude and Google wrapper
  invocation setting `TRIAD_DISPATCH_LOG_DIR=<returned-root>/results/_logs` exactly;
- every applicable Claude, AGY, and authorized Gemini fallback command template in
  `references/leg-contracts.md` carrying that same exact environment assignment;
- expected-root comparison and explicit first-cleanup `removed: true`; and
- after successful cleanup, confirmation that the exact root is absent and other managed sibling
  roots remain untouched; and
- durable handoff prepared directly at the durable destination; and
- the formal routing reference linked from the public skill so its load-bearing rules are reachable;
  and
- matching lifecycle local-data disclosures in both `README.md` and `README.ko.md`; and
- matching public permission wording in `README.md`, `README.ko.md`, and `SECURITY.md` that
  distinguishes the wrapper's approved internal `--dangerously-skip-permissions` insertion from
  caller-supplied flags, user-setting changes, permission profiles, sandboxes, trust bypasses, and
  tool restrictions; and
- already satisfied in the current candidate: no canonical worktree modification until every
  required leg terminates and final verification prints `ROUND_INTEGRITY_OK`, pinned in the
  existing lifecycle distribution-contract test without adding a collected case.

- [x] **Step 4: Finish the skill and changelog minimally**

Keep the Task 0 lifecycle paragraph, changelog entries, and already-satisfied worktree-ordering
assertion. Add the remaining public-skill statements listed in Step 3, including review-ID/root
custody, collision/isolation, member-list IPC and
`shared/source/product/<member>` mapping, the exact per-invocation
`TRIAD_DISPATCH_LOG_DIR=<returned-root>/results/_logs` assignment, and first-cleanup `removed: true`.
Update every applicable formal provider template in `references/leg-contracts.md` with the same
assignment. Extend an existing distribution-contract assertion to pin that exact variable/path
relationship in both the public skill and the executable templates; do not add a collected test case.
Also add only the missing log/result routing or activity wording needed by those assertions; do not
further change the approved provider route, tool availability, packet manifest, closure policy,
digest, verdict schema, or convergence rules. Keep the skill below its existing 200-line contract.
Document the reserved `triad-review-` system-temp namespace, next-prepare cleanup after strictly
more than 30 days, and round-owned `results/_logs` in the existing local-data sections of both
`README.md` and `README.ko.md`. Correct the existing permission and troubleshooting statements in
both README languages and `SECURITY.md` so they disclose the approved internal AGY flag while
preserving the exact distinctions in Step 3. Extend an existing distribution assertion across those
three public documents without adding a collected case. After the Task 2 marker-ordering case and
Task 3 activity-success parameters are GREEN, change the current lifecycle changelog bullet from a
pending target to an implemented guarantee. Do not bump the version.

Already satisfied in the current candidate: the pending `final-0.2.533-r9` release-plan round uses
the lifecycle CLI's returned root for its snapshot, prompts, verdicts, and wrapper logs and does not
recreate a repository `_runs/reviews/<id>` review root. Task 4 does not reopen that release plan.

- [x] **Step 5: Run GREEN CLI and distribution tests**

Run the full affected modules:

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py workspace/triad-codex-dispatch-reliability/tests/test_log_cleanup.py workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -q'
```

Expected: exactly `129` cases collected and exactly `129 passed`, with zero failed, skipped, or
xfailed. Any other count stops Task 4.

---

### Task 5: Verify the complete lifecycle candidate

**Files:**
- Verify all changed files and preserve the frozen formal-contract basis.
- Verify the same 62-member Task 1/Task 6 closure. Its direct readers include `.codex-plugin/plugin.json`, all
  four public skills, every cross-family reference, `SECURITY.md`, both provider wrappers,
  `bin/verdict_schema.py`, `bin/review_policy_benchmark.py`, `tests/test_verdict_schema.py`, both
  2026-08-05 AGY route documents, both README languages, and the 23 benchmark members. Its leader
  verification/governing inputs are `scripts/bootstrap.sh`, `scripts/verify_distribution.py`, and
  `docs/references/repair-protocol.md`.

- [x] **Step 1: Focused tests**

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py workspace/triad-codex-dispatch-reliability/tests/test_log_cleanup.py workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -q'
```

Historical pre-Task-2 baseline: `88 passed`. Acceptance requires exactly `129` collected and
`129 passed`, matching Task 4 Step 5, with zero failed, skipped, or xfailed. Any deviation stops
Task 5 and returns to the task whose collection changed.

- [x] **Step 2: Full suite**

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests -q'
```

Historical pre-Task-2 baseline: `457 passed`. Acceptance requires exactly `498` collected and
`498 passed`, with zero failed, skipped, or xfailed. Any deviation stops Task 5 and returns to the
task whose collection changed.

- [x] **Step 3: Static and live smoke checks**

From `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`, run:

```zsh
bash -n scripts/bootstrap.sh
git diff --check
```

From `/Users/chaniri/codex_workspace`, run:

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_cli_lifecycle_sequence -q'
```

Expected: shell and diff checks exit `0`; the exact smoke selector reports `1 passed`. That test
must prove prepare → capture → render → verify → cleanup on one disposable root, exact packet
inventory, first cleanup `removed: true`, second cleanup `removed: false`, sibling preservation,
and final root absence. Do not use a real provider call for this smoke check.

- [x] **Step 4: Boundary verification**

Confirm no provider route, digest framing, verdict schema, benchmark evidence, closure policy,
permission setting, or MCP setting changed outside the owner-directed removal of tool suppression,
the exact lifecycle/skill additions, and the bounded explicit-log-root fallback correction. Record
the then-current, now historical candidate hashes as the pre-lifecycle basis. Enumerate every regular file under the
smoke packet inside `test_cli_lifecycle_sequence`, before that test performs cleanup, and assert
that each path is either `source/product/<member-list entry>` or one of the fixed current-round
artifacts. Treat that test assertion as the reproducible inventory evidence after the disposable
root is gone; record tracked benchmark fixtures as source membership, not review history.

Run the Git boundary evidence commands from
`/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`:

```zsh
git status --short
git diff --name-only
git diff -- CHANGELOG.md README.md README.ko.md SECURITY.md bin/review_round.py bin/antigravity_wrapper.py bin/_common.py docs/status/2026-08-05-next-session-handoff.md docs/status/2026-08-08-triad-maintenance-decisions.md docs/superpowers/plans/2026-08-05-triad-0.2.533-owner-decisions-and-release.md docs/superpowers/plans/2026-08-08-formal-review-contract-remediation.md docs/superpowers/plans/2026-08-08-review-workspace-lifecycle.md docs/superpowers/plans/2026-08-08-triad-maintenance-decisions.md docs/superpowers/specs/2026-08-08-review-workspace-lifecycle-design.md skills/triad-antigravity-dispatch/SKILL.md skills/triad-cross-family-review/SKILL.md skills/triad-cross-family-review/references tests/test_review_round.py tests/test_antigravity_stream_json.py tests/test_log_cleanup.py tests/test_distribution_contract.py tests/test_provider_wrappers.py tests/test_review_policy_benchmark.py
```

Run the portable SHA-256 evidence command from `/Users/chaniri/codex_workspace`:

```zsh
/bin/zsh -lic 'python3 -c "import hashlib, pathlib, sys; [print(hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest(), name) for name in sys.argv[1:]]" workspace/triad-codex-dispatch-reliability/CHANGELOG.md workspace/triad-codex-dispatch-reliability/README.md workspace/triad-codex-dispatch-reliability/README.ko.md workspace/triad-codex-dispatch-reliability/SECURITY.md workspace/triad-codex-dispatch-reliability/bin/review_round.py workspace/triad-codex-dispatch-reliability/bin/antigravity_wrapper.py workspace/triad-codex-dispatch-reliability/bin/_common.py workspace/triad-codex-dispatch-reliability/docs/status/2026-08-05-next-session-handoff.md workspace/triad-codex-dispatch-reliability/docs/status/2026-08-08-triad-maintenance-decisions.md workspace/triad-codex-dispatch-reliability/docs/superpowers/plans/2026-08-05-triad-0.2.533-owner-decisions-and-release.md workspace/triad-codex-dispatch-reliability/docs/superpowers/plans/2026-08-08-formal-review-contract-remediation.md workspace/triad-codex-dispatch-reliability/docs/superpowers/plans/2026-08-08-review-workspace-lifecycle.md workspace/triad-codex-dispatch-reliability/docs/superpowers/plans/2026-08-08-triad-maintenance-decisions.md workspace/triad-codex-dispatch-reliability/docs/superpowers/specs/2026-08-08-review-workspace-lifecycle-design.md workspace/triad-codex-dispatch-reliability/skills/triad-antigravity-dispatch/SKILL.md workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/SKILL.md workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/leg-contracts.md workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/review-prompt-contract.md workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/reviewer-routing.md workspace/triad-codex-dispatch-reliability/tests/test_review_round.py workspace/triad-codex-dispatch-reliability/tests/test_antigravity_stream_json.py workspace/triad-codex-dispatch-reliability/tests/test_log_cleanup.py workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py workspace/triad-codex-dispatch-reliability/tests/test_provider_wrappers.py workspace/triad-codex-dispatch-reliability/tests/test_review_policy_benchmark.py'
```

---

### Task 6: Pass a fresh mandatory three-family pre-merge gate

Historical result: R3 completed this task with three admitted `SAFE` verdicts and
`ROUND_INTEGRITY_OK` for digest
`8039f18ab617f687f0ee4ddfc8642be2c45322d6912dc8e1561c62ddcfae9647`. Later bounded Minor fixes
and the owner-approved JSON IPC amendment changed source bytes, so R3 is historical evidence only.

**Files:**
- Review only: current lifecycle candidate, complete affected unchanged closure, tests, spec, plan,
  and current lifecycle RED/GREEN and verification evidence.

- [x] **Step 1: Prepare a new unique-ID directory with the implemented CLI**

Use `prepare` itself with an exact allow-list. Add current `TASK.md`, `REVIEW.diff`, and optional
`EVIDENCE.md`; exclude every prior round's task, diff, manifest, snapshot, prompt,
status, and verdict. The following line-manifest sentence records the historical R3 recipe and is
superseded for Task 10 by the implemented `manifest` command: generate `SOURCE_SHA256SUMS` last with
one sorted SHA-256 line for each other regular file.
Mechanically verify the manifest path set, order, count, and every hash, then enumerate the packet
as exactly `source/product/<member-list entry>` plus the fixed current-round artifacts before
capture. Include every governing document directly read by an in-closure distribution test,
including `README.ko.md`, `SECURITY.md`, the current handoff/release plan, and the superseded AGY
design/plan named by that test. Exact test-source exclusion within the 62-member direct-reader
closure: none; full-suite totals also count unrelated test modules outside that closure. Write the snapshot to
`results/snapshot.json` and rendered prompts directly under `prompts/`.

After replacing each angle-bracket token with the recorded literal value, run:

```zsh
/bin/zsh -lic 'python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py prepare --review-id <fresh-review-id> --source-root /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability --member-list <absolute-current-member-list> --required-members-json <one-shell-quoted-canonical-json-array>'
/bin/zsh -lic 'python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py capture --prepared-dir <returned-shared-dir> --worktree /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability --output <returned-root>/results/snapshot.json'
/bin/zsh -lic 'python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py render --review-id <fresh-review-id> --review-kind pre-merge --family claude --objective "Review the complete lifecycle candidate for correctness, completeness, compatibility, bounded risk, and false-pass paths." --prepared-dir <returned-shared-dir> --content-digest <captured-digest> --criterion correctness --criterion completeness --criterion compatibility --criterion bounded-risk --criterion false-pass --approved-boundary "Every regular file in the prepared directory; exact test-source exclusion: none" --output <returned-root>/prompts/claude.txt'
/bin/zsh -lic 'python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py render --review-id <fresh-review-id> --review-kind pre-merge --family google --objective "Review the complete lifecycle candidate for correctness, completeness, compatibility, bounded risk, and false-pass paths." --prepared-dir <returned-shared-dir> --content-digest <captured-digest> --criterion correctness --criterion completeness --criterion compatibility --criterion bounded-risk --criterion false-pass --approved-boundary "Every regular file in the prepared directory; exact test-source exclusion: none" --output <returned-root>/prompts/google.txt'
/bin/zsh -lic 'python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py render --review-id <fresh-review-id> --review-kind pre-merge --family codex --objective "Review the complete lifecycle candidate for correctness, completeness, compatibility, bounded risk, and false-pass paths." --prepared-dir <returned-shared-dir> --content-digest <captured-digest> --criterion correctness --criterion completeness --criterion compatibility --criterion bounded-risk --criterion false-pass --approved-boundary "Every regular file in the prepared directory; exact test-source exclusion: none" --output <returned-root>/prompts/codex.txt'
```

- [x] **Step 2: Dispatch Claude, Google, and fresh Codex before consuming results**

Use the same approved routes and one digest. Provider legs may read/search only and must not execute
candidate code or mutate state. Set `TRIAD_DISPATCH_LOG_DIR` to this round's `results/_logs` for
both provider wrappers and write all three verdicts under `results/`.

Start these provider commands plus the documented fresh Codex native spawn before reading any
result:

```zsh
/bin/zsh -lic 'TRIAD_DISPATCH_LOG_DIR=<returned-root>/results/_logs python3 workspace/triad-codex-dispatch-reliability/bin/claude_wrapper.py --prompt-file <returned-root>/prompts/claude.txt --cwd <returned-shared-dir> --model opus --effort xhigh --timeout 1800 --pydantic verdict_schema:LegVerdict > <returned-root>/results/claude.json'
/bin/zsh -lic 'TRIAD_DISPATCH_LOG_DIR=<returned-root>/results/_logs python3 workspace/triad-codex-dispatch-reliability/bin/antigravity_wrapper.py --prompt-file <returned-root>/prompts/google.txt --cwd <returned-shared-dir> --model gemini-3.1-pro-high --effort high --timeout 1800 --pydantic verdict_schema:LegVerdict > <returned-root>/results/google.json'
```

Fresh Codex uses `fork_turns="none"`, `model="gpt-5.6-terra"`,
`reasoning_effort="xhigh"`, and no `agent_type`; save its terminal JSON as
`<returned-root>/results/codex.json`.

- [x] **Step 3: Admit and clean up**

Require three schema-valid `SAFE` verdicts and final `ROUND_INTEGRITY_OK`. Independently reproduce
all findings. After adjudication evidence is consumed, call `cleanup` with the exact review ID and
root returned by `prepare`; require that same root with `removed: true`, then confirm it is absent.
Preserve a durable handoff only if separately requested by the owner.

Validate each result, verify integrity, and then substitute the literal recorded ID/root in the
cleanup command:

```zsh
/bin/zsh -lic 'python3 workspace/triad-codex-dispatch-reliability/bin/verdict_schema.py validate --result-file <returned-root>/results/claude.json --expected-review-id <fresh-review-id> --expected-family claude --expected-content-digest <captured-digest>'
/bin/zsh -lic 'python3 workspace/triad-codex-dispatch-reliability/bin/verdict_schema.py validate --result-file <returned-root>/results/google.json --expected-review-id <fresh-review-id> --expected-family google --expected-content-digest <captured-digest>'
/bin/zsh -lic 'python3 workspace/triad-codex-dispatch-reliability/bin/verdict_schema.py validate --result-file <returned-root>/results/codex.json --expected-review-id <fresh-review-id> --expected-family codex --expected-content-digest <captured-digest>'
/bin/zsh -lic 'python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py verify --prepared-dir <returned-shared-dir> --worktree /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability --snapshot <returned-root>/results/snapshot.json'
/bin/zsh -lic 'python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py cleanup --review-id <fresh-review-id> --expected-root <returned-root>'
```

- [x] **Step 4: Stop before external release state**

Report changed paths, verification, cleanup, and remaining risks. Do not commit, push, merge,
install, tag, publish, or release.

---

## 2026-08-09 canonical JSON IPC amendment

This amendment supersedes only the newline member-list, line manifest, and interpolated dynamic
prompt metadata described above. It retains the approved unique-ID lifecycle, exact source closure,
prepared-directory digest, symlink/unsupported-entry rejection, provider routes, tool availability,
30-day cleanup, verdict schema, and convergence rules. It supports actual UTF-8 strings through
deterministic JSON escaping and deliberately adds no Base64/raw-byte layer, protocol negotiation,
registry, or legacy compatibility parser.

In Task 8 code literals, `b"\n"` means the single LF terminator. Doubled backslashes shown in the
metadata raw-wire list denote the two-character JSON escape sequences that must appear on the wire.

### Task 7: Pass the amended formal-plan gate

**Files:** Review the current design, this plan, `bin/review_round.py`, `tests/test_review_round.py`,
the cross-family skill and references, the current changelog, and the unchanged direct-reader
closure already fixed by Tasks 1, 5, and 6. Exact test-source exclusion: none.

- [x] Prepare a fresh unique-ID packet from the canonical worktree. The packet itself uses only
  current safe path names and the last admitted lifecycle CLI; do not copy or reuse an earlier
  packet, task, diff, manifest, snapshot, prompt, or verdict.
- [x] Render the same objective, criteria, boundary, directory, and digest for Claude, Google, and a
  fresh Codex child. Start all three before consuming a verdict.
- [x] This is a pre-implementation formal-plan gate. Review the executable Task 8 plan against the
  current implementation; the absence of a Task 8 implementation is expected and is not a finding.
- [x] Require three admitted `SAFE` verdicts, run final integrity verification, reproduce every
  finding, and clean the exact root. Any packet/tool/schema failure invalidates the whole round and
  requires a repaired workflow plus a fresh ID.

R1 (`20260809-json-ipc-plan-r1`) reviewed the fresh 62-source closure at digest
`c5ab7796a7bd5e93f2c3daf1f853436d907bee95e557acd51c8dd25a2e35f0b0`. Google exposed
`gemini-3.1-pro-high` and returned `SAFE`; Claude requested `opus`/`xhigh` with runtime identity
unexposed and returned `NOT-SAFE`; fresh Codex requested `gpt-5.6-terra`/`xhigh` with runtime
model/effort unexposed and returned `NOT-SAFE`. Final verification printed `ROUND_INTEGRITY_OK`,
cleanup returned `removed: true`, and no managed root remained.

Reproduced plan defects: name every active line-manifest consumer; preserve each decoded path guard
with well-formed JSON inputs; reject non-managed targets and wrong inventory before manifest write;
include source members whose basename is `SOURCE_SHA256SUMS`; keep family binding through the
metadata key; define manifest activity; and keep the existing exact collection totals by extending
existing tests rather than adding collected cases. A lexical duplicate-key scanner is not adopted:
the exclusive dictionary serializer cannot emit that representation, manual packet rewriting is
outside the workflow, and the owner explicitly rejected defenses for inputs the supported producer
cannot create.

R2 (`20260809-json-ipc-plan-r2`) reviewed a new 62-source copy at digest
`44e132c761db47a6de51a0bd544ca4abbfaeb5778c383e894d0633593c054f5a`. Claude, Google, and fresh
Codex all returned `NOT-SAFE`; Google exposed `gemini-3.1-pro-high`, while Claude runtime identity
and fresh Codex model/effort remained unexposed. Final verification printed `ROUND_INTEGRITY_OK`,
cleanup returned `removed: true`, and no managed root remained.

The reproduced R2 plan gaps were narrower than the design: make CR acceptance explicitly supersede
the old CR-rejection case; classify sorted member-list enforcement as a new guard and publish that
precondition in the skill; give every new behavior its own RED selector and predeclare the resulting
counts; enumerate the existing member-list/manifest/render test edit surfaces; prove no dynamic
marker survives outside the metadata line; and list exact focused/full commands. Google findings
that merely restated current pre-implementation code were refuted by the explicit Task 8 corrections;
the suggestion to canonicalize a loader fixture with the production serializer was outside the
tool-owned-output contract.

R3 (`20260809-json-ipc-plan-r3`) reviewed a new 62-source copy at digest
`70171667d015eed01efb7c4506f2ac3f57aa6b554de2c83c39e77d51483651a4`. Fresh Codex returned
`SAFE`; Claude returned `NOT-SAFE`; the Google provider was submitted as exposed runtime
`gemini-3.1-pro-high` but returned `status=ERROR` after 597.37 seconds without a terminal verdict.
The Google leg and therefore the formal round were invalid. Final verification nevertheless printed
`ROUND_INTEGRITY_OK`, exact cleanup returned `removed: true`, and the root is absent. No R3 input or
result is reused.

The owner increased the selected formal AGY end-to-end wrapper deadline from the wrapper's 600-second
default to an explicit 1,800 seconds. The existing `--timeout` interface already implements this;
the formal leg contract, Antigravity skill, routing evidence, active release plan, changelog, and
existing distribution assertion pin the invocation. No wrapper default, provider route, permission,
tool availability, or retry behavior changes. Reproduced Claude plan gaps only tighten the approved
design: bind returned review ID and digest to metadata alongside family; isolate every new CLI test
from the real system temp; extend the predeclared count ledger; pin compact stored-list bytes; and
sort ordinary helper output while constructing the one unsorted rejection payload directly.
The formal Claude leg already had its separately reviewed 1,800-second deadline before this owner
decision and retains it unchanged; “selected AGY only” describes this new delta, not removal of the
existing Claude contract.

R4 (`20260809-json-ipc-plan-r4`) reviewed a new 62-source copy at digest
`4d28c01572c9565b41eaf34f79d82f26bdee35298ef342dc5e24f2f7eba2ac40`. The selected AGY route
received wrapper timeout 1,800 and native print timeout 1,790 seconds and returned a terminal result
successfully after 485.4 seconds; Claude ended successfully after 695.5 seconds. All three admitted
verdicts were `NOT-SAFE`, final verification printed `ROUND_INTEGRITY_OK`, exact cleanup returned
`removed: true`, and the root is absent. No R4 input or result is reused.

Reproduced R4 plan defects: add the explicit timeout to the plan's remaining literal AGY command;
rewrite the three existing capture-side manifest-malformation tests over decoded JSON entries with
branch-specific expectations; relabel the embedded post-R30 hash ledger as historical; pin canonical
raw bytes for the manifest, metadata line, representative lifecycle stdout records, and snapshot;
and exercise manifest activity inside existing collected cases. Two proposed expansions are rejected.
Escaped unpaired surrogate code points are not strict UTF-8-decoded workflow strings and the supported
exclusive producer cannot emit them from the approved domain, so no surrogate scanner or test is
added. The 1,800-second owner decision applies to the selected AGY route that actually timed out; the
separately authorized pre-submission Gemini fallback retains its own invocation contract.

R5 (`20260809-json-ipc-plan-r5`) reviewed a new 62-source copy at digest
`36421fad6385e7628a5b194f20b2ae2eef673cda3af38be35a91e88a2c7f5a55`. Google and fresh Codex
returned `SAFE`; Claude returned `NOT-SAFE`. Google completed successfully after 88.5 seconds and
Claude after 686.3 seconds. Final verification printed `ROUND_INTEGRITY_OK`, exact cleanup returned
`removed: true`, and the root is absent. No R5 input or result is reused. The reproduced corrections
add no collected case or capability: capture/verify malformed-manifest subcases explicitly cover
wrong decoded types and duplicate decoded paths with controlled `RoundIntegrityError`/CLI exit 2;
the two existing rendered-family assertions move to metadata-key binding; and a second `manifest`
invocation proves exclusive creation preserves the first manifest bytes.

R6 (`20260809-json-ipc-plan-r6`) reviewed a new 62-source copy at digest
`106a30d859ca6b09df9b15ed9e65eecf9b2a563942ef43baea11c51c608a7a40`. Claude and fresh Codex
returned `SAFE`; Google returned `NOT-SAFE`. Claude completed after 610.6 seconds and Google after
940.2 seconds, directly confirming that the selected AGY 1,800-second correction is effective. Final
verification printed `ROUND_INTEGRITY_OK`, exact cleanup returned `removed: true`, and the root is
absent. No R6 input or result is reused. Google's proposed removal of the pre-existing Claude
1,800-second contract is refuted: the current owner delta only adds the same deadline to selected
AGY. The reproduced Claude Minor corrections name two remaining legacy-heading assertion sites,
choose one literal metadata-line label, and identify the exact existing activity subcase to extend.

R7 (`20260809-json-ipc-plan-r7`) allocated a fresh 62-source root but was abandoned before capture or
provider dispatch. The first auxiliary diff/manifest generator invocation failed at Python parse time
and wrote neither artifact; after confirming their absence, the leader generated them with the known
routine but still invalidated the ID rather than reusing the root. Exact cleanup returned
`removed: true`, the root is absent, and no R7 input or result is reused.

R8 (`20260809-json-ipc-plan-r8`) reviewed a new 62-source copy at digest
`1344597dcabf8ce9f78888955f27f939ef68ff50877ef84ce50c169f6852c483`. Google and fresh Codex
returned `SAFE`; Claude returned `NOT-SAFE`. Google completed after 530.3 seconds and Claude after
677.6 seconds. Final verification printed `ROUND_INTEGRITY_OK`, exact cleanup returned
`removed: true`, and the root is absent. No R8 input or result is reused. Reproduced corrections add
no mechanism or collected case: record R7, refresh the live handoff from 457 to the already verified
498 baseline and require 501 after Task 9, state the retained Claude deadline in routing, disambiguate
the LF literal, make the test manifest helper emit canonical JSON, and fix manifest absence ordering.

R9 (`20260809-json-ipc-plan-r9`) reviewed a new 62-source copy at digest
`a933dd2853314dcf359e8d79ce071b3009ecae6b0198c1285cfeb4c7fce08439`. Claude and fresh Codex
returned `SAFE`; Google returned `NOT-SAFE`. Google completed after 139.4 seconds and Claude after
965.8 seconds, further proving that the selected 1,800-second provider deadlines must not be replaced
by short leader polling waits. Final verification printed `ROUND_INTEGRITY_OK`, exact cleanup returned
`removed: true`, and the root is absent. No R9 input or result is reused. Google's three findings only
reported that the explicitly pre-implementation Task 8 code did not yet exist, so they are refuted as
phase errors and do not authorize implementation before convergence. Reproduced Claude Minor
corrections narrow the serializer wording to `review_round.py`, add `manifest` to activity lists,
supersede the historical blank-line case, exercise retained symlink rejection inside RED 2, retain a
distinct sorted-manifest error, and require the skill to call `manifest` instead of hand-building it.

R10 (`20260809-json-ipc-plan-r10`) reviewed a new 62-source copy at digest
`0592edb9ec9c4279007ccaead1313fc076136679edc69d603392b8b32e69f1d8`. Claude returned `SAFE`;
Google and fresh Codex returned `NOT-SAFE`. Google completed after 253.3 seconds and Claude after
651.7 seconds. Final verification printed `ROUND_INTEGRITY_OK`, exact cleanup returned
`removed: true`, and the root is absent. No R10 input or result is reused. The reproduced bounded
gaps require failed managed-root `manifest` calls not to refresh activity and require fixed prose to
apply metadata criteria over the approved boundary. Google's `shasum -c` claim misread a historical
provider-denial record as a current command, and its validator claim is contradicted by GREEN 2's
capture/verify decoder update. Its packet-only tab/double-space wording correction is carried into the
next current-round task. Codex's manual escaped-surrogate proposal remains outside the owner-approved
strict-UTF-8 producer domain and is not implemented.

R11 (`20260809-json-ipc-plan-r11`) prepared and captured a fresh 62-source packet but was invalidated
before any provider dispatch because one manually repeated render command supplied a different
approved-boundary string to the Codex prompt. Exact cleanup returned `removed: true`, the root is
absent, and no R11 input, prompt, snapshot, or result is reused. The next round renders all three
families through one mechanical loop over a single objective, criteria list, boundary, and digest.

R12 (`20260809-json-ipc-plan-r12`) failed at shell parse time before `prepare`; R13
(`20260809-json-ipc-plan-r13`) was rejected by `prepare` because process substitution is not a
canonical regular member-list file. Neither ID created a review root or dispatched a provider, and
neither is reused. R14 generated a unique regular member-list file with `mktemp` plus deterministic
`sort -u -o`, verified exactly 62 entries, prepared successfully, and deleted that exact temporary
file immediately.

R14 (`20260809-json-ipc-plan-r14`) captured digest
`be7bde6c520ad6be516e29deda727b0b5cac3ef476bd802aebb4d8dad3b0e456`. Fresh Codex returned
`SAFE`; Google returned `NOT-SAFE`; Claude completed after 772.1 seconds but its result file was
schema-invalid because login-shell startup stdout preceded the JSON. Final packet verification still
printed `ROUND_INTEGRITY_OK`, exact cleanup returned `removed: true`, and the root is absent. No R14
input or result is reused. Google repeated refuted standard-checksum compatibility and omitted-skill
claims and mistook metadata-key references for duplicated dynamic values. The real workflow defect is
fixed at the invocation boundary: each wrapper redirects stdout to its result path inside the provider
command, and the distribution contract pins that placement. A contaminated result is never filtered
or salvaged.

R15 (`20260809-json-ipc-plan-r15`) reviewed a fresh 62-source copy at digest
`b414168344f208c67468c2fadf39bcdc7a5ea2003edc17b6a56a06d7ca71b987`. Claude, Google, and fresh
Codex all returned schema-valid `SAFE` verdicts with no open questions; Google completed after 161.8
seconds and Claude after 666.6 seconds. Every result began directly with JSON, final verification
printed `ROUND_INTEGRITY_OK`, exact cleanup returned `removed: true`, and the root is absent. No R15
input or result is reused. Task 7 is admitted. Claude's three Minor findings add no mechanism or
collected case: producer-side `manifest` failures receive branch-distinct stderr assertions, decoded
manifest failures remain capture/verify responsibilities, and the renamed whitespace case gets one
literal name and selector.

### Task 8: Implement the amendment with TDD

**Files:**

- Modify: `bin/review_round.py`
- Modify: `tests/test_review_round.py`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `skills/triad-cross-family-review/references/review-prompt-contract.md`
- Modify: `tests/test_distribution_contract.py`
- Modify: `docs/superpowers/plans/2026-08-05-triad-0.2.533-owner-decisions-and-release.md`
- Modify: `docs/superpowers/plans/2026-08-08-review-workspace-lifecycle.md` only to record the
  required RED/GREEN evidence, pre-implementation review corrections, and completion state
- Modify: `CHANGELOG.md`
- Add no new protocol file and do not rewrite historical round records.

- [x] **RED 1 — member-list JSON:** Add exactly one collected test named
  `test_prepare_json_member_list_round_trips_special_characters_and_rejects_invalid_shapes`. It uses
  a sorted JSON array containing actual paths with quote, backslash, LF, CR, tab, `\u0001`, and
  U+2028, requires byte-identical copies and stored `member-list.txt` bytes exactly equal to
  `json.dumps(members, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8") +
  b"\n"`, and loops over
  malformed JSON, non-array top level, non-string element, empty array, empty-string member, and
  unsorted array. CR is now accepted through JSON escaping and explicitly supersedes Task 2 Step 2's
  historical CR-rejection requirement. Run this selector before implementation and record its
  expected failure.
- [x] Keep the existing nine collected unsafe-member parameters but re-express their semantics as:
  JSON absolute path, traversal, `.git`, duplicate decoded path, raw unescaped JSON control
  character (the former CR slot), normalized `nested/..`, BOM, escaped NUL, and invalid UTF-8. Rename
  the blank-line/whitespace test to
  `test_prepare_preserves_path_whitespace_and_rejects_empty_string_member`; it preserves path
  whitespace and rejects an empty-string element because JSON has no ignored blank-line record. This
  explicitly supersedes Task 2 Step 1's historical test name and ignored-empty-line description.
  Preserve each specific boundary error and run the existing unsafe-member selector before the parser
  edit.
- [x] **GREEN 1:** Add one deterministic JSON serializer, decode a sorted UTF-8 JSON string array, retain
  the existing duplicate, normalized-relative-path, and source-entry checks, add sorted-order
  rejection as a new guard, and write the normalized stored member list with a final LF. Reject NUL
  and non-UTF-8 strings; add no byte/Base64 fallback. Route existing prepare/cleanup/snapshot JSON
  and the new manifest result and metadata through that one serializer; test-only loader fixtures do
  not become tool-owned output.
- [x] The supported string domain means values produced by strict UTF-8 decoding. Do not add a
  raw-byte, surrogate-code-point, or Base64 compatibility layer: an escaped unpaired surrogate is
  outside that domain and cannot be emitted by the supported producer. Manual injection is outside
  the input contract; specify no behavior, graceful-error classification, or regression test for it.
- [x] **RED 2 — manifest JSON:** Add exactly one collected test named
  `test_manifest_cli_json_round_trips_special_paths_and_rejects_invalid_packet`. It calls a
  not-yet-existing `manifest` command and requires a sorted JSON array of
  exact decoded `{path, sha256}` objects. Prove the same special-character paths round-trip;
  `source/product/SOURCE_SHA256SUMS` and a nested source file with that basename are included; only
  the root manifest is excluded. Producer-side failure subcases cover a malformed stored member list,
  packet-inventory mismatch, symlink/unsupported entry, non-managed or non-`shared/` target, and
  exclusive creation; no failure creates or rewrites a manifest. Do not add lexical duplicate-object-
  key cases, which the exclusive serializer cannot produce. Run this selector before implementation
  and record its expected failure.
- [x] In that same RED 2 selector, replace one inventory-matching packet member with a symlink and
  require CLI exit 2 with no manifest created. This preserves the existing packet-escape guard and
  adds no collected case.
- [x] In that same RED 2 selector, invoke `manifest` a second time after successful creation and
  require CLI exit 2, the exclusive-create error, and byte-identical existing manifest bytes. No
  overwrite, replacement, or compatibility behavior is added. Evaluate the root-manifest-absence
  precondition before packet-inventory verification so this branch is deterministic.
- [x] Every `manifest` CLI failure subcase requires its branch-distinct `review_round: <error>` stderr
  text and asserts that neither argparse `usage:` nor a traceback appears. A missing subcommand or a
  rejection by the wrong branch must not satisfy RED 2.
- [x] For every RED 2 `manifest` CLI failure subcase under a managed current root, pin the root and
  regular `.last_activity` marker to fixed `st_mtime_ns` values before invocation and require both
  values to remain identical afterward. This includes inventory, symlink, and exclusive-create
  failures and remains inside the one existing RED 2 collected test.
- [x] Prove malformed JSON, wrong decoded types, duplicate decoded paths, unsorted paths, inventory,
  and digest failures through capture/verify after editing a valid `manifest`-produced JSON file. The
  producer never decodes an existing root manifest; keep those decoder branches in the three existing
  capture/verify tests named below.
- [x] In RED 2, assert the manifest file bytes equal the one canonical serializer output plus one LF,
  and assert the `manifest` stdout record is the same compact sorted-key form plus one LF. Include
  regular-marker and missing/unsafe-marker activity subcases in this same collected selector. Extend
  the in-process marker-inspection-error subcase of `test_cli_lifecycle_activity_success_paths` with
  a manifest operation inside its current collected case, using a packet whose root
  `SOURCE_SHA256SUMS` is absent so exclusive creation succeeds. The activity inspection failure must
  preserve the completed output and exit status.
- [x] Every new or edited Task 8 test that invokes the CLI, including the manifest selector and the
  manifest-updated lifecycle smoke, sets `TMPDIR` to an isolated canonical `tmp_path`; an in-process
  variant monkeypatches `review_round.tempfile.gettempdir` to that same isolated path. No Task 8 test
  enumerates or deletes children of the developer's real system temp.
- [x] **GREEN 2:** Add `review_round.py manifest --prepared-dir <shared>`. Enumerate and hash files in
  Python only after requiring the exact canonical-temp managed `shared/` target and verifying the
  stored-member/fixed-artifact inventory. Retain symlink/unsupported-entry rejection, exclude only
  the root-relative manifest, create it exclusively, print a deterministic JSON result, refresh
  lifecycle activity after successful output, and make capture/verify parse only the new JSON shape.
  The shared manifest decoder rejects non-array top levels, non-object entries, missing or extra
  object keys, non-string `path`/`sha256` values, and duplicate decoded paths as
  `RoundIntegrityError`. It retains sorted decoded-path validation with a distinct error from packet
  inventory mismatch; the CLI maps those failures to exit 2 without a traceback.
- [x] **RED 3 — prompt metadata:** Add exactly one collected test named
  `test_rendered_metadata_json_escapes_every_free_form_value_without_legacy_interpolation`. Give each
  free-form field a distinct marker, including quote, backslash, LF, CR, tab, `\u0001`, and U+2028.
  Require exactly one line with the literal fixed prefix `Review metadata: ` followed immediately by
  the metadata JSON object whose decoded value contains every dynamic field; remove
  that line from the prompt and assert every free-form marker occurs zero times and every legacy
  dynamic heading is absent from the remaining fixed prose. Static schema enum examples may remain.
  Require fixed inspection prose to direct the reviewer to perform `metadata.objective` for
  `metadata.review_kind` and `metadata.family`, inspect `metadata.prepared_directory`, and evaluate
  every `metadata.criteria` item across `metadata.approved_boundary`, without interpolating those
  values again.
  Require the result instruction to bind returned review ID, family, and content digest to
  `metadata.review_id`, `metadata.family`, and `metadata.content_digest` without a second interpolated
  instruction for any of those values. Run this selector before implementation and record its
  expected failure.
- [x] In RED 3, assert the bytes after the literal `Review metadata: ` prefix equal the canonical
  serializer output exactly and
  contain the required `\\\"`, `\\\\`, `\\n`, `\\r`, `\\t`, `\\u0001`, and `\\u2028` wire escapes
  with compact separators and sorted keys. Extend existing prepare/cleanup CLI assertions and the
  snapshot assertion to require their exact canonical bytes plus one LF; do not add a collected case.
- [x] **GREEN 3:** Keep fixed reviewer instructions as prose and serialize the dynamic metadata with
  the same deterministic serializer; use the fixed inspection binding for all metadata fields and
  refer to its `review_id`, `family`, and `content_digest` keys in the result binding instruction. Do
  not add a brief file, schema version, or new CLI option. Remove the legacy Review ID/kind/family/
  objective/path/digest headings and criteria/boundary list interpolation rather than leaving both
  representations in the prompt.
- [x] **Skill RED/GREEN:** Use the already reproduced line-framing failure plus a focused
  distribution-contract RED that requires JSON member/manifest generation and JSON metadata. Then
  update the skill, prompt contract, active 0.2.533 release plan, and current changelog together, and
  make the existing distribution assertion pin the same JSON contract across those active consumers.
  Require the skill to call the member list a sorted JSON array of non-empty normalized POSIX
  relative paths. Replace its manual manifest-generation instructions with
  `bin/review_round.py manifest --prepared-dir <shared>` and make the existing distribution assertion
  pin that command string. Do not alter provider permissions, tools, closure policy, or review routes.
- [x] **Existing test edit surface:** Add one test-only JSON member-list writer and mechanically
  replace every line-framed member-list write and stored-list byte assertion. The helper sorts by
  decoded path; reorder the currently unsorted nested-artifact call site, while the unsorted-array
  rejection case writes its JSON payload directly without the helper. Update
  `_write_source_manifest` to emit the canonical sorted JSON `{path, sha256}` array plus one LF and
  exclude only the root manifest until production `manifest` replaces it. Rewrite
  `test_capture_and_verify_reject_lifecycle_manifest_inventory_or_syntax_error`,
  `test_capture_rejects_unsorted_lifecycle_manifest`, and
  `test_capture_rejects_lifecycle_manifest_digest_mismatch` to decode the JSON array, respectively
  drop/append/reorder an entry or corrupt one `sha256`; add wrong-typed decoded values and a duplicate
  decoded path inside the first existing test. Assert `RoundIntegrityError` from capture/verify and
  CLI exit 2 without traceback, with distinct syntax, type, duplicate, inventory, sort, and digest
  expectations instead of a shared broad match. Update the lifecycle smoke to call `manifest`.
  Replace existing `Review ID:`/`Reviewer family:` assertions and the legacy interpolated-family
  assertions in `test_rendered_prompt_binds_focused_round_once` and
  `test_cli_renders_family_bound_prompt` with parsed metadata and metadata-key binding assertions.
  Also migrate the render branch in `_assert_cli_operation_success` and the prompt assertion in
  `test_cli_lifecycle_sequence` from the removed `Review ID:` heading to parsed metadata.
- [x] Retain and verify the three bounded R3 Minor corrections: boundary error ordering, exact
  affected-consumer tracing in rendered instructions, and the manifest framing defect now
  superseded by the JSON parser.

Run every direct Python command from `/Users/chaniri/codex_workspace`:

```zsh
/bin/zsh -lic 'command -v python3 && python3 --version && python3 -m pytest --version'
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_prepare_json_member_list_round_trips_special_characters_and_rejects_invalid_shapes -q'
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_prepare_rejects_unsafe_member_lists -q'
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_prepare_preserves_path_whitespace_and_rejects_empty_string_member -q'
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_manifest_cli_json_round_trips_special_paths_and_rejects_invalid_packet -q'
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_rendered_metadata_json_escapes_every_free_form_value_without_legacy_interpolation -q'
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py -q'
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -q'
```

The amendment adds exactly the three named `tests/test_review_round.py` cases above. Required totals
become exactly: `tests/test_review_round.py` 78, `tests/test_distribution_contract.py` 16, the
established focused set 132, and the full suite 501. The existing nine unsafe-member parameters keep
their nine slots; extra invalid-shape checks are looped inside the new member-list test. Before each
GREEN edit, record the failing selector and expected unmet contract in this plan; after the edit,
record the same selector passing. Any collection drift stops implementation and requires this plan
to be amended before continuing.

Task 8 TDD evidence: RED 1 failed because the prior line parser treated the complete JSON array as
one source path; after the bounded parser/serializer edit, the named selector passed, the nine unsafe
parameters plus renamed whitespace selector passed 10 cases, and the then-current module passed 76
cases. RED 2 failed with argparse's invalid `manifest` choice; after adding the managed exclusive
producer and JSON decoder, its named selector passed. RED 3 failed because zero `Review metadata: `
records existed; after removing legacy interpolation and binding fixed prose to `metadata.*`, its
named selector passed. The focused distribution RED failed on the absent sorted-JSON member rule;
after the active skill/contract/plan/changelog update, the exact distribution module passed 16 cases.
Final collection and GREEN totals are exactly 78 review-round, 16 distribution, 132 focused, and 501
full-suite cases.

### Task 9: Verify the complete amended candidate

- [x] From `/Users/chaniri/codex_workspace`, run the exact commands below. The py_compile target is
  separate from the focused and full pytest sets:

```zsh
/bin/zsh -lic 'python3 -m py_compile workspace/triad-codex-dispatch-reliability/bin/review_round.py'
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py -q'
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -q'
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py workspace/triad-codex-dispatch-reliability/tests/test_log_cleanup.py workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -q'
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests -q'
```
- [x] Run `git diff --check`, review the full changed-path inventory, and prove no path outside the
  workspace was changed. Do not mutate user settings, MCP state, permission profiles, or unrelated
  worktrees. Run from `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`:

```zsh
git diff --check
git status --short
```
- [x] Require the predeclared 78/16/132/501 collection and pass totals. A differing observed count
  stops the task; never rewrite the ledger after the fact to accept drift. Update release/handoff
  claims only when the expected totals pass.
- [x] After the exact 501-test full suite passes, update
  `docs/status/2026-08-05-next-session-handoff.md` from the current pre-JSON 498 baseline to
  `501 passed` and add 498 to its do-not-reuse list. Do not make that handoff claim before the pass.

Task 9 evidence: login-shell preflight resolved Python 3.12.13 and pytest 9.0.3; `py_compile` exited
0. The exact modules passed 78 and 16 cases, the focused set passed 132, and the full suite passed
501 in 131.05 seconds. `git diff --check` exited 0. The reviewed status inventory contains only this
canonical worktree's declared candidate paths; no command edited user settings, MCP state,
permission profiles, or another worktree. The live handoff now records 501 and rejects reuse of 498.

### Task 10: Pass a fresh mandatory three-family pre-merge gate

Pre-merge R1 (`20260809-json-ipc-premerge-r1`) failed before root creation because the leader passed
the non-canonical `/var/...` alias returned by macOS `mktemp` instead of its `/private/var/...`
realpath. `prepare` correctly rejected the member list as non-canonical. No review root or provider
leg existed, and the ID was not reused.

Pre-merge R2 (`20260809-json-ipc-premerge-r2`) copied 75 current source members, generated a
78-entry JSON manifest, and captured digest
`2f2046855361fd4d75b3a4a922726a2cb89809eda47b8e04ce78a95282892007`. Google returned
schema-valid `SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`. Google completed in
87.0 seconds and Claude in 710.7 seconds under their explicit 1,800-second deadlines. Final
verification printed `ROUND_INTEGRITY_OK`; exact cleanup returned `removed: true`; no managed
review root remains.

R2 is not admissible because the leader's mechanical closure omitted three paths explicitly named
by this plan's direct-reader rule: the historical/superseded AGY 1.1.10 plan and design plus
`docs/references/repair-protocol.md`. The next packet adds those paths under a fresh ID. Independent
reproduction also accepted five bounded candidate corrections inside the approved design: bracket
verify-time worktree fingerprinting with a second packet digest; disclose the internal AGY
child-only `always-proceed` selection in migration/bootstrap text without implying stored-setting
mutation; report configured-root run-log storage failure for successful results too; align current
and historical changelog wording; and remove one dead packet-file constant. Existing collected tests
were extended in place: the five focused selectors were RED for these exact gaps and then GREEN, the
132-case focused set passed, and bootstrap plus migration passed 256 cases. Claude's question about
the omitted AGY documents is resolved by their explicit `Historical, superseded, and non-executable`
headers; no legacy permission rule is revived.

Pre-merge R3 (`20260809-json-ipc-premerge-r3`) copied 78 current source members, generated an
81-entry JSON manifest, and captured digest
`9f8369204846956a7f2c7a2e8d8183ba869acf3e14527ce48480c86017710019`. Google returned
schema-valid `SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`. Google completed in
202.3 seconds and Claude in 615.1 seconds under their explicit 1,800-second deadlines. Final
verification printed `ROUND_INTEGRITY_OK`; exact cleanup returned `removed: true`; no managed
review root remains.

Both `NOT-SAFE` legs independently reproduced one bounded candidate defect: a successful provider
intentionally receives no repair run-log, so `emit_run_log` returns `None`, but
`persist_result_artifacts` treated every `None` as storage failure and printed
`run-log-unavailable: storage-failure` even after a healthy audit write. The actual Google and
Claude wrapper completions reproduced that false diagnostic. The existing configured-root selector
was extended in place with a writable-root success observation and failed RED with three diagnostics
instead of two. The minimal GREEN carries the actual audit append outcome through the existing
helpers and emits the success-path run-log diagnostic only for a real explicitly configured-root
storage failure. The existing provider-wrapper rejection selector now exercises caller-supplied
permission flags against AGY as well as Claude and Gemini without adding a collected case. The 84
directly affected tests pass. The fixed candidate also passed the predeclared 78 review-round tests,
16 distribution tests, 132 focused tests, and the complete 501-test suite in 127.52 seconds;
`git diff --check` and `bash -n scripts/bootstrap.sh` exited 0. Because source and tests changed, R3
is not admissible and the next round uses a fresh ID and fresh copies.

Pre-merge R4 (`20260809-json-ipc-premerge-r4`) prepared the expected 78-source copy but was
invalidated before current-round artifacts, manifest, snapshot, prompts, or provider dispatch. The
leader ran the changed-path membership check from the nested checkout's login-shell environment,
where `jq` was not on `PATH`, instead of the required `/Users/chaniri/codex_workspace` workdir. The
resulting missing-path messages were a failed checker, not packet evidence. Exact cleanup returned
`removed: true`; the review root and external member-list input are absent, and the ID is not reused.
The corrected preparation runs environment-resolved commands from the workspace root.

Pre-merge R5 (`20260809-json-ipc-premerge-r5`) was invalidated before `prepare`: the leader used
`path` as a zsh loop variable, overwriting zsh's special `path` array and therefore `PATH`; the
subsequent `git` and `sort` membership commands were not resolved, and the command lacked fail-fast
handling before printing a false OK marker. No review root, current-round artifact, prompt, or
provider leg existed. The external member-list input is deleted and the ID is not reused. The
corrected check uses `set -euo pipefail`, no zsh special variable, and a single JSON set comparison.

Pre-merge R6 (`20260809-json-ipc-premerge-r6`) copied 78 current source members, generated an
81-entry JSON manifest, and captured digest
`d9f1f1a1ad7465852f31cdc0f5551263de369c8d4c3a84e989f5bcc3578d99d5`. Google returned
schema-valid `SAFE`; Claude returned schema-valid `SAFE` with four Minor findings; fresh Codex
returned schema-valid `NOT-SAFE` with three Major findings. Google completed in 477.4 seconds and
Claude in 796.1 seconds under their explicit 1,800-second deadlines. Both successful wrapper exits
omitted the former false run-log-unavailable diagnostic. Final verification printed
`ROUND_INTEGRITY_OK`; exact cleanup returned `removed: true`; no managed review root remains.

Independent reproduction accepted the bounded defects and documentation mismatches within the
approved design. The existing unsafe-member selector now rejects the componentless `.` path before
root creation and maps filesystem rejection of an unrepresentable decoded string to the controlled
error contract without adding a surrogate scanner. The existing manifest-error selector now rejects
semantically equivalent noncanonical `SOURCE_SHA256SUMS` bytes. The existing configured-root
selector distinguishes appended audit evidence, advisory contention/attestation skips, and actual
storage exceptions; post-append rotation stays best-effort and only an actual configured-root
storage exception produces the success-path unavailable diagnostic. CHANGELOG now scopes manifest
enforcement to managed lifecycle `shared/`, and the handoff no longer revives its stale 80-file
count. All subcases extend existing collected selectors; the 78/16/132/501 ledger is unchanged.
The corrected candidate passed the three expanded selectors (11 cases), the exact 78 review-round
tests, 16 distribution tests, 132 focused tests, and the complete 501-test suite in 128.28 seconds;
`git diff --check` and `bash -n scripts/bootstrap.sh` exited 0. Because source, tests, and
direct-reader documents changed, R6 is not admissible and the next round uses a fresh ID and fresh
copies.

Pre-merge R7 (`20260809-json-ipc-premerge-r7`) copied 78 current source members, generated an
81-entry JSON manifest, and captured digest
`96f20a14a239bff1dbd4e6c6604f61153cb5a24ac3c71e17f40a658a02643262`. Google and fresh Codex
returned schema-valid `SAFE` without findings. Claude returned schema-valid `SAFE` with three Minor
findings. Google completed in 224.7 seconds and Claude in 787.7 seconds under their explicit
1,800-second deadlines; both wrappers exited 0 without the former false run-log diagnostic. Final
verification printed `ROUND_INTEGRITY_OK`; exact cleanup returned `removed: true`; no managed review
root remains.

Independent reproduction accepted two current-document clarity corrections: mark the 0.2.532
permission statement as superseded by the disclosed 0.2.533 wrapper-internal AGY flag, and disclose
the mode-0700 review root, round-owned logs, and interrupted-root retention in the public threat
model. The proposed success-path diagnostic rename is not accepted: this plan explicitly requires
`run-log-unavailable` for an actual configured-root storage failure even after a successful provider
result, and the repair protocol already limits analyzer handoff to failed wrapper classifications.
These documentation corrections change reviewed bytes, so R7 does not authorize integration and a
fresh complete round uses a new ID and fresh copies.

Pre-merge R8 (`20260809-json-ipc-premerge-r8`) was invalidated before `prepare`: the leader's
mechanical changed-path subset check invoked `jq` without `-n`, so the filter received no input and
exited 4 without a result. Separate checks proved that the generated member list contained the
expected 78 paths and the changed set contained 29 paths, but no review root was created. The
external member-list file was removed and the ID is not reused. The owner superseded a local shell
comparison fix with one mechanical boundary: `prepare` must receive a non-empty
`--required-members-json` array and reject any required path absent from the member list before
creating a review root. The skill retains only the judgment of which owner-approved paths are
required; it adds no subcommand, Git inference, state file, lock, or registry.

The focused RED proved that the old CLI rejected `--required-members-json` and the distributed skill
did not carry that interface. The first behavior GREEN proves controlled rejection for malformed,
empty, and missing-member JSON before root creation and successful argv transport for quote, LF,
backslash, and U+2028 path values.

The completed amendment verification resolved Python 3.12.13 and pytest 9.0.3 from the required
login shell; `py_compile` exited 0; the exact modules passed 78 and 16 cases; the focused set passed
132; and the full suite passed 501 in 128.18 seconds.

Pre-merge R9 (`20260809-json-ipc-premerge-r9`) copied 78 current source members after `prepare`
mechanically admitted the non-empty 29-path required JSON, generated an 81-entry manifest, and
captured digest `969f4612d1dc2350db5be93f6a6e48352cd083146ee65fd14575d1c3ef646448`.
Google and fresh Codex returned schema-valid `SAFE` without findings; Claude returned schema-valid
`SAFE` with three Minor findings. Google completed in 181.7 seconds and Claude in 795.1 seconds.
Final verification printed `ROUND_INTEGRITY_OK`; exact cleanup returned `removed: true`; the root is
absent and managed siblings are unchanged. One reproduced bounded correction adds unsorted and
duplicate required-array tuples to the existing CLI rejection loop without adding a collected case.
The two other Minor proposals are not adopted: no current member needs a verdict path containing a
backslash or control character and narrowing that supported domain would change the approved scope;
the mandatory formal CLI already enforces the required argument while the internal function default
preserves the owner-approved minimal implementation.

Post-R9 verification kept the collection ledger unchanged: 78 review-round, 16 distribution, 132
focused, and 501 full-suite cases passed; the full suite completed in 128.68 seconds.

Pre-merge R10 (`20260809-json-ipc-premerge-r10`) was invalidated before provider dispatch. The
packet and `capture` succeeded, but an unsupported leader-side assertion queried the snapshot's
nonexistent `.content_digest` field instead of its actual `.prepared_digest` field and exited 1.
The packaged lifecycle contract was not defective: `capture` returned the prepared digest and
`verify` is the supported final snapshot check. Exact cleanup returned `removed: true`, the root is
absent, no managed sibling changed, and the ID is not reused. The next round carries the digest from
`capture` output and uses packaged `verify`; it does not repeat the redundant snapshot-field query.

The owner correctly reclassified R10 as a distributed-skill workflow defect rather than a merely
local leader mistake. The focused distribution RED failed because the skill did not require exact
`capture` stdout handoff or forbid snapshot-field reparsing. The bounded repair assigns prompt and
verdict digest input to exact `capture` stdout and leaves final snapshot validation to packaged
`verify`; it adds no command, field, protocol, or state.

The same focused distribution selector passed after the skill and current changelog were updated;
the superseded capture-snapshot prose assertion was replaced by the exact printed-digest contract.
Final post-repair totals remained 78, 16, 132, and 501; the full suite completed in 128.69 seconds.

Pre-merge R11 (`20260809-json-ipc-premerge-r11`) copied 78 current members, generated an 81-entry
manifest, and carried exact `capture` stdout digest
`a50b04b0e9670954a27fafa61d0f26f5c27f73feceb4bd7fa97590c2ae32d864` into every prompt and
validator without parsing the snapshot. Google returned schema-valid `SAFE` in 111.7 seconds;
Claude returned schema-valid `SAFE` with two Minor findings in 976.2 seconds; fresh Codex returned
schema-valid `NOT-SAFE` with one Major finding. Packaged `verify` printed `ROUND_INTEGRITY_OK`;
exact cleanup returned `removed: true`; the root is absent and no managed sibling changed. The
reproduced Major showed that repeated `--required-members-json` arguments silently kept only the
last value, so the bounded correction enforces exactly one occurrence before root creation in the
existing CLI test. The two Minor corrections bind the new changelog control in the existing
distribution test and document the already-enforced unique required-path rule. No new collected
case, command, field, protocol, state, or lifecycle layer is added.
Post-R11 totals remained 78, 16, 132, and 501; the full suite completed in 128.76 seconds.

Pre-merge R12 (`20260809-json-ipc-premerge-r12`) copied 78 current members, generated an 81-entry
manifest, and carried exact `capture` stdout digest
`711e0780f4516cb792a11fddc1601f6f3a3728919747e3f42f21de08a27c05b3` into every prompt and
validator. Google returned schema-valid `SAFE` without findings in 156.5 seconds; fresh Codex
returned schema-valid `SAFE` without findings; Claude returned schema-valid `SAFE` with two Minor
findings in 611.7 seconds. Packaged `verify` printed `ROUND_INTEGRITY_OK`; exact cleanup returned
`removed: true`; the root is absent and no managed sibling changed. The reproduced documentation
corrections qualify the packaged AGY child permission selection in formal routing and disclose that
configured wrapper allowed roots must include the canonical system temp base used by formal review
paths. Existing distribution coverage is extended in place; no collected case or runtime mechanism
is added.
The focused public-document RED failed on the unqualified routing claim; the same selector passed
after the routing and wrapper-root disclosures were aligned across English, Korean, and security
surfaces.
Post-R12 totals remained 78, 16, 132, and 501; the full suite completed in 128.89 seconds.

- [ ] Prepare a new unique-ID packet with the implemented JSON member list and `manifest` command.
  Include the same complete current closure and exact test-source exclusion `none`; include current
  RED/GREEN and verification evidence only.
- [ ] Start independent Claude, Google, and `fork_turns="none"` Codex legs on the same exact
  directory and digest before consuming results. Require structured verdict admission and final
  `ROUND_INTEGRITY_OK`.
- [ ] Reproduce and classify every finding. Apply only the smallest defect correction inside this
  approved design; any design delta returns to the owner. Every changed candidate requires a fresh
  complete round and a new ID. Clean each completed or invalid root exactly.

### Task 11: Package, push, install, and prove fresh-session readiness

- [ ] After Task 10 passes, create one intentional candidate commit, then run
  `scripts/verify_distribution.py` from clean `HEAD` and compare source/archive/extracted bytes and
  tests. A source change after review restarts Task 10.
- [ ] Push the reviewed commit to `origin/release/0.2.532`. Do not tag, publish, merge, or create a
  release.
- [ ] Install those exact plugin bytes through the supported `codex plugin add ... --json` path,
  run installed-cache `scripts/bootstrap.sh --install`, compare source/cache hashes, and use a fresh
  `codex exec --ephemeral` process to prove the current cross-family skill exposes the JSON member
  list, `manifest` command, JSON metadata, unique-ID cleanup, and exact current marker.
- [ ] From `/Users/chaniri/codex_workspace`, inspect the live Argus root/project instructions and
  current status/restart documents. Record the actual checkpoint and dirty-tree boundary for the
  next fresh session; do not reconstruct missing sealed inputs or start product work in this release
  task.
