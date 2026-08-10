# TRIAD Skill SOT Behavioral Test Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans`, `superpowers:test-driven-development`, and
> `superpowers:writing-skills` to execute this plan task by task. Use the
> project-scoped `triad-skill-executor` only as a fresh behavior executor; it
> does not author changes or adjudicate reviews.

**Goal:** Prove `triad-cross-family-review` by executing it in a fresh,
skill-pinned Custom Agent, then make only the smallest SOT and distribution
corrections reproduced by that behavior test before the pending pre-merge gate.

**Architecture:** The workspace root owns one reusable Custom Agent definition
whose only stable job is to expose the exact source TRIAD skill to a fresh
behavior executor. Its `skills.config` entry enables the plugin worktree's exact
source `SKILL.md`; its developer instruction contains only the minimal no-edit
executor role. The leader puts the complete per-run scenario and receipt
contract in `spawn_agent.message`. Every test uses a new `fork_turns="none"`
instance. The plugin repository remains the SOT for the skill, its direct
references, and its deterministic runtime; the agent definition duplicates no
scenario or review procedure. Static pytest coverage handles deterministic
contracts, and the fresh agent supplies the missing behavior-level RED/GREEN
evidence.

**Tech Stack:** Codex project Custom Agents, TOML `skills.config`, Markdown
skills, Python 3.12 standard library, pytest, TRIAD packaged review tooling.

## Global Constraints

- Work only below `/Users/chaniri/codex_workspace`, except for the existing
  unique-ID system-temp review roots created and removed through
  `bin/review_round.py`.
- Before Task 5, do not edit user-global Codex configuration, plugin caches,
  provider settings, MCP settings, credentials, or another workspace. Task 5's
  supported plugin installation is the sole exception: first enumerate the
  exact external targets, delta, and impact and obtain the target-specific
  current-conversation approval required by the root `AGENTS.md`; then change
  only those approved installation artifacts. Never change provider, MCP,
  permission, model, or sandbox defaults.
- Do not restrict installed CLI, MCP, read, search, or web capabilities. The
  executor controls its instruction source and write scope, not tool
  availability.
- Do not duplicate packet, digest, dispatch, verdict, or cleanup rules in the
  Custom Agent TOML. Those rules remain in the plugin SOT.
- Do not put per-run commands, receipt fields, success criteria, or shell
  invocation corrections in the Custom Agent TOML. The leader supplies those
  test-harness requirements in the exact spawn message.
- The executor never edits the plugin SOT, commits, pushes, installs, publishes,
  or acts as a formal reviewer. It reports a workflow defect instead of working
  around it.
- Use a new executor thread for every RED or GREEN trial. Do not reuse its
  conversation after a skill edit.
- Use a fresh unique review ID for every TRIAD round. Never reuse packet bytes or
  verdicts from an earlier ID.
- Run a three-family formal-plan gate before plugin implementation and a fresh
  three-family pre-merge gate after implementation.
- Run every direct `python3` command through `/bin/zsh -lic` from
  `/Users/chaniri/codex_workspace`, after recording `command -v python3`,
  `python3 --version`, and `python3 -m pytest --version`.
- Make no new registry, daemon, lock, lifecycle protocol, tool restriction, or
  compatibility layer.
- The current owner-approved task or executable plan is the execution
  authority and must explicitly carry every retained or rejected decision that
  constrains its round. For this task, retain the packaged
  `_prepared_digest` algorithm, reject the reviewed `git hash-object`
  replacement, keep the lifecycle tool as the sole packet authority, and do
  not infer a version bump from the pre-install cache mismatch. A reviewer
  finding alone does not reopen any of those decisions.

## Recorded interruption point

- Workspace root:
  `/Users/chaniri/codex_workspace`, branch
  `codex/workspace-argus-agents`, HEAD
  `7554c18031ee51f6275ad4625a302971c1803c14`. It already contains unrelated
  owner changes; preserve them.
- Plugin repository:
  `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`,
  branch `release/0.2.532`, HEAD
  `8b2f66edae8af6fc9bd32cdf35cf4cbb3006879c`. Its 24 tracked modified paths and
  untracked status/plan files are the current candidate, not disposable output.
- The existing lifecycle plan's Tasks 0 through 9 are checked complete. Its
  recorded verification baseline is 501 passing tests; this session did not
  rerun that historical command.
- Formal-plan R30 used digest
  `58b02cf6eaedafebc37c90c7f19995504e1af53e6dfdb81ef27a759bedc45051`,
  returned admitted `SAFE` from Claude, Google, and fresh Codex, passed final
  integrity verification, and was cleaned exactly.
- Existing lifecycle-plan Task 10 (fresh pre-merge) and Task 11
  (package/push/install/fresh-session proof) remain pending. Do not start them
  until this plan's skill behavior RED/GREEN and amended gates finish.
- The current session predates the new project agent catalog entry. Open a new
  Codex session at `/Users/chaniri/codex_workspace` before trying to select
  `triad-skill-executor`.

---

### Task 1: Prove the project-scoped executor loads and capture behavior

**Files:**
- Verify: `/Users/chaniri/codex_workspace/.codex/config.toml`
- Verify: `/Users/chaniri/codex_workspace/.codex/agents/triad-skill-executor.toml`
- Read as SOT: `skills/triad-cross-family-review/SKILL.md`
- Record in: `docs/status/2026-08-09-triad-skill-sot-behavior-test.md`

**Interfaces:**
- Consumes: one exact behavior scenario and the configured skill folder.
- Produces: a fresh-agent load receipt, pre/post plugin-worktree fingerprints,
  and an observed RED transcript without plugin edits.

- [ ] **Step 1: Start a new root session and verify the catalog entry**

Start Codex with `/Users/chaniri/codex_workspace` as the workspace root. Confirm
that `triad-skill-executor` is exposed as a registered project agent. If it is
not exposed, stop and diagnose the project catalog; do not fall back to a
default child and call that equivalent.

- [ ] **Step 2: Capture the no-edit basis**

From the plugin repository, record:

```bash
git status --short
git rev-parse HEAD
git status --porcelain=v1 -z | shasum -a 256
git diff --binary --no-ext-diff | shasum -a 256
```

- [ ] **Step 3: Spawn one fresh executor for the behavior scenario**

Select `agent_type="triad-skill-executor"`, set `fork_turns="none"`, and give
it the exact scenario below. Do not pass replacement workflow instructions.

```text
Execute one behavior characterization of the configured triad-cross-family-review skill as its leader. Use only the configured skill's leader workflow in observation mode: treat the skill, its source, and its tests as read-only, invoke no other skill, and stop before provider dispatch. First identify every non-system instruction source that the configured skill requires before packet preparation. Then exercise the deterministic current-packet lifecycle through prepare, manifest, capture, at least one render, verify, and exact cleanup using one new unique review ID and the canonical plugin worktree.

Create only the exact disposable fixture /Users/chaniri/codex_workspace/_runs/skill-executor/<same-review-id>/ and keep its parent and siblings unchanged. Under that leaf, create source/input.txt, source/payload.json, and members.json. Make members.json the sorted JSON array ["input.txt","payload.json"] and use the same array as the required-members JSON value. Make payload.json exactly {"quote":"a \"quote\"","backslash":"C:\\review\\packet","newline":"first\nsecond","tab":"left\tright","unicode":"한글 ✓"}. Use the fixture source directory as the prepare source root, the fixture members.json as the member list, and the canonical plugin worktree as the capture worktree. Before cleanup, compare the copied shared/source/product/payload.json with the fixture payload as decoded JSON. At the first lifecycle failure, use only supported exact cleanup when an exact managed root exists, emit WORKFLOW_DEFECT, remove the exact fixture leaf, and stop. A later trial uses a fresh child and review ID.

Return one JSON object. At every object level emit exactly the properties named here and no others. Top level: status, skill, instruction_sources, review_id, commands, artifacts, cleanup, worktree_changed, failures. status is "SUCCESS" or "WORKFLOW_DEFECT"; skill and review_id are strings; instruction_sources is an array of objects containing only string path and dependency; commands is an array of objects containing only string command and integer exit_state; worktree_changed is a boolean; failures is an array of objects containing only string stage, message, and classification. artifacts contains only fixture_leaf, fixture_payload, prepared_payload_path, payload_round_trip_verified, managed_review_root, prepared_directory, manifest, snapshot, and rendered_prompts. Its path fields are strings or null, fixture_payload is an object containing only the five string fields quote, backslash, newline, tab, and unicode, payload_round_trip_verified is a boolean, and rendered_prompts is a string array. cleanup contains only expected_root, removed, managed_review_root_absent, fixture_leaf_absent, residue, and swept_roots; expected_root is a string or null, removed is a boolean or null, the two absent fields are booleans, and residue and swept_roots are string arrays.

Encode every string as JSON and use JSON values for inter-process data. instruction_sources contains one canonical-realpath absolute {path, dependency} entry for every filesystem instruction source actually used through the complete scenario, including applicable AGENTS.md. commands contains only actual process invocations; run each packaged lifecycle subcommand as its own /bin/zsh -lic process and set exit_state to that process's exact observed status. Record non-process harness actions only in artifacts, cleanup, or failures. Run every direct python3 command through /bin/zsh -lic from /Users/chaniri/codex_workspace. Return "SUCCESS" with an empty failures array, non-null managed-review artifact paths, a non-empty rendered_prompts list, payload_round_trip_verified true, and cleanup removed true only when every requested stage succeeds. Otherwise return "WORKFLOW_DEFECT" with at least one failure. Set cleanup.expected_root equal to artifacts.managed_review_root.
```

- [ ] **Step 4: Verify containment and record the observation**

Repeat the two worktree fingerprints. Any mismatch invalidates the trial. Record
the exact executor identity, requested model/effort from its registered profile,
whether runtime metadata exposed them, prompt, result JSON, created paths,
cleanup result, and reproduced skill defect. Do not fix anything in Task 1.

### Task 2: Pass the amended three-family formal-plan gate

**Files:**
- Review: this plan
- Review: the Task 1 RED record
- Review: the complete current affected-source and direct-reader closure already
  enumerated by the lifecycle plan

**Interfaces:**
- Consumes: reproduced RED behavior and the owner-approved minimal design.
- Produces: three admitted `SAFE` verdicts for one new digest before SOT edits.

- [ ] Prepare a new unique-ID directory with current source, this plan, the RED
  record, exact current diff, `TASK.md`, and generated `SOURCE_SHA256SUMS`. The
  lifecycle-plan direct-reader closure includes both unchanged governing files
  `docs/superpowers/plans/2026-08-05-agy-1.1.10-formal-route.md` and
  `docs/superpowers/specs/2026-08-05-agy-1.1.10-formal-route-design.md`; omitting
  either invalidates the packet.
- [ ] Dispatch Claude, Google, and fresh `fork_turns="none"` Codex legs over the
  same directory, objective, criteria, boundary, and digest.
- [ ] Reproduce every finding. Amend only a defect or underspecification inside
  this approved executor/SOT design. Ask the owner before any new capability or
  generalized mechanism.
- [ ] Include the live executor profile and the exact documented
  `skills.config` file-path contract in the reviewed evidence. Embed the complete
  credential-free executor TOML bytes, the complete credential-free workspace
  `.codex/config.toml` bytes, and the complete relevant official-manual passages
  without ellipses or paraphrase: the custom-agent schema passage that admits
  `skills.config`, the concrete custom-agent `/SKILL.md` example, the generated
  config-template `/SKILL.md` example, and the generic `skills.config..path`
  field-table passage that calls it a folder path. The workspace config capture
  must show the registered executor entry and the presence or absence of any
  parent-layer `skills.config` or plugin-enablement override. Record each source
  path and SHA-256, then mechanically compare every embedded capture with the
  named current files before manifesting. Require the plan to bind Task 4 to the source
  `SKILL.md` path and SHA-256 rather than to a skill name alone. Recompute each
  external-evidence SHA-256 directly from its named current file and require
  exactly 64 lowercase hexadecimal characters plus an exact value match before
  manifesting the packet.
- [ ] Keep earlier round packet/result artifacts out of each fresh review
  directory: prior `TASK.md`, `REVIEW.diff`, manifest, snapshot, rendered prompt,
  and result JSON files are prohibited. Current candidate source files that
  narrate historical rounds remain required closure members and are never
  treated as the current round's leg results. Preserve the leader adjudication
  during convergence and append the durable round ledger to the current status
  only after Task 2 receives final three-family admission.
- [ ] Require three admitted `SAFE` verdicts plus `ROUND_INTEGRITY_OK`, then
  clean the exact review root.

### Task 3: Apply the minimum skill-SOT correction with TDD

**Files:**
- Verify without adding scenario or workflow rules:
  `/Users/chaniri/codex_workspace/.codex/agents/triad-skill-executor.toml`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `tests/test_distribution_contract.py`
- Modify: `scripts/verify_distribution.py`
- Modify: `tests/test_distribution_verifier.py`
- Modify: `CHANGELOG.md`
- Record the superseding decision in:
  `docs/status/2026-08-09-triad-skill-sot-behavior-test.md`
- Preserve as historical evidence without rewriting:
  `docs/status/2026-08-08-triad-maintenance-decisions.md`

**Interfaces:**
- Consumes: the admitted Task 2 plan and Task 1 reproduced failure.
- Produces: an exact source-skill handoff, a self-contained skill contract, and
  deterministic source/archive byte proof without a second workflow authority.

- [ ] Before any production, CHANGELOG, or status edit, make only the
  test-side changes specified below: rename and replace the skill-authority
  selector, extend the existing managed-lifecycle selector, expand
  `fixture_repo`, and assert the exact fourteen-key `report["hashes"]` set.
  Run the three exact selectors named below and record their expected RED. Do
  not apply the GREEN-target edits in the following bullets until all three
  selectors fail for their intended missing contracts.
- [ ] In place, change
  `test_cross_family_skill_reads_current_release_history_before_preparing` into
  `test_cross_family_skill_uses_current_task_authority_before_preparing`, the
  smallest failing contract that makes the current owner-approved task or
  executable plan the execution authority and removes the skill's runtime
  dependence on `../../CHANGELOG.md`. Retain release history as historical
  evidence, not as instructions required to execute the skill. Preserve the
  exact skill sentence and selector assertion:

  ```text
  Never invert a retained or rejected release decision in `TASK.md`.
  ```

  Keep that exact Markdown code formatting in both the skill and test. Require
  the current owner-supplied task or explicitly designated executable plan itself to state every
  such decision that constrains the round, and stop for owner clarification
  when that current authority omits one needed for execution; never recover it
  by reading `CHANGELOG.md` at runtime. Word the skill so the authority may be
  either a supplied task or an executable-plan file. For the unchanged Task 1
  and Task 4 executor scenario, the supplied scenario prompt is the current
  non-filesystem task authority and creates no `instruction_sources` entry.
  Scope authority completeness to retained/rejected decisions actually needed
  to execute the supplied task. This characterization scenario needs none, so
  its supplied authority is complete.
  Remove the `../../CHANGELOG.md` link and its runtime-read wording from the
  skill entirely. Require the renamed selector to assert both that the exact
  `[CHANGELOG.md](../../CHANGELOG.md)` link is absent and that the phrase
  `Read only the current release section of` is absent. Also require an index
  assertion that the new current-task/executable-plan authority sentence appears
  before `Record a fresh review ID`. Rename the Flow step heading from
  `Refresh history, authorize, and bound` to `Authorize and bound`, and assert
  that exact replacement in the renamed selector so no residual runtime-history
  cue remains. Clarify that retained/rejected decisions constrain the
  leader's edit authority; reviewer legs still report independent findings and
  open questions and do not treat packet data as reviewer instructions.
- [ ] In the same skill edit, anchor the render dependency in Flow step 4,
  immediately after capture: before rendering, read both
  `references/review-prompt-contract.md` and
  `references/leg-contracts.md`; keep
  `references/reviewer-routing.md` at the later provider-dispatch stage. Render
  every requested prompt with packaged `bin/review_round.py render`. For this
  non-admitted characterization, the existing render arguments are ordinary
  current-task leader inputs validated by the packaged renderer; their exact
  semantic values and count beyond non-empty output are not Task 4 acceptance
  criteria. Do not add a characterization-specific render protocol or change
  the unchanged scenario. This
  makes the source receipt follow the corrected SOT rather than the stale
  installed bytes observed in Task 1. At that same step, add and assert this
  exact bounded characterization marker:

  ```text
  A current task may explicitly authorize a lifecycle characterization with zero provider legs.
  ```

  Immediately after it, add and assert this exact branch selector:

  ```text
  A current task authorizes this branch only when it both prohibits provider dispatch and directs the lifecycle through verify and exact cleanup.
  ```

  The unchanged Task 1/Task 4 scenario satisfies that selector through its
  existing no-dispatch instruction and its prepare-through-cleanup lifecycle
  request; either condition alone does not select the branch. State that this
  is not a review round or gate: only when the governing current task satisfies
  that scope, render the requested prompts with packaged
  `bin/review_round.py render`, run `bin/review_round.py verify`, make no review-admission,
  convergence, adjudication, or gate-passage claim, use supported exact cleanup,
  and return without entering provider dispatch. Otherwise continue the normal
  three-family flow unchanged. This is the SOT behavior that makes the
  owner-supplied Task 1/Task 4 scenario executable; do not duplicate it in the
  workspace profile.
  In Flow step 8, qualify only the existing leg-termination precondition: it
  applies to review rounds, while the task-authorized zero-provider
  characterization runs `bin/review_round.py verify` through the Flow step 4
  branch. Preserve the existing canonical-worktree mutation prohibition. In
  Flow step 11, qualify only the existing gate-passage and post-adjudication
  normal-cleanup sentences with an explicit back-reference: they apply to review
  rounds, while the task-authorized zero-provider characterization uses the Flow
  step 4 verify-and-exact-cleanup branch. Assert that qualification in the same
  managed-lifecycle selector; add no mechanism or collected case.
- [ ] Set `HASH_TARGETS` in `scripts/verify_distribution.py` to exactly the
  load-bearing target set below. Make the existing `fixture_repo` create and
  commit every listed file, and extend its existing success selector to require
  `sorted(report["hashes"])` to equal the sorted fourteen-target list as well as
  every source/archive hash pair to match. Add no collected test or parameter
  case:

  ```text
  .codex-plugin/plugin.json
  skills/triad-cross-family-review/SKILL.md
  skills/triad-cross-family-review/agents/openai.yaml
  skills/triad-cross-family-review/references/convergence.md
  skills/triad-cross-family-review/references/leg-contracts.md
  skills/triad-cross-family-review/references/review-prompt-contract.md
  skills/triad-cross-family-review/references/reviewer-routing.md
  bin/_common.py
  bin/antigravity_wrapper.py
  bin/claude_wrapper.py
  bin/gemini_wrapper.py
  bin/review_round.py
  bin/verdict_schema.py
  requirements.txt
  ```

- [ ] Keep the executor profile as a stable clean-context harness. Its
  `skills.config.path` is the exact absolute source
  `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/SKILL.md`.
  The official contract attests both concrete `/SKILL.md` examples and generic
  folder wording, so treat this file pin as the current bounded source-selection
  hypothesis rather than proof of runtime behavior. If the reloaded Task 4
  executor still resolves the plugin-namespaced installed copy or omits the
  exact source skill from its receipt, preserve and clean its evidence, classify
  `WORKFLOW_DEFECT`, and diagnose name-based plugin resolution versus
  enablement-only `skills.config` using only the workspace catalog and source
  discovery pointer. The profile contains only the model, effort, minimal
  no-edit executor role, and skill enablement; do not add per-run receipt,
  command, cleanup, shell, or lifecycle rules. Those test-harness details live
  in the exact Task 1/Task 4 spawn message above, while workflow behavior lives
  in the source skill or its scripts. Make no user-global change,
  alternate-skill invocation, or tool
  restriction. Apply only a reproduced smallest workspace catalog/profile fix
  and restart all of Task 4 with a new ID; stop for owner approval if resolution
  would require a new mechanism or design expansion.
- [ ] Record the Task 1 `prepare` failure's exact disposition. The stale
  installed skill omitted the source skill's sorted-JSON member-list contract;
  current `bin/review_round.py` correctly rejected that input and the existing
  `test_prepare_json_member_list_round_trips_special_characters_and_rejects_invalid_shapes`
  selector already proves the tool contract. Repair the source selection and
  record that no `review_round.py` change or new regression case is warranted.
- [ ] In the current `0.2.533` CHANGELOG section, supersede the exact bullet
  saying the skill reads the current release entry before packet preparation.
  Replace it in place with the current task/plan authority rule and retained-
  decision requirement; do not append a contradictory second current-release
  behavior claim or rewrite historical status evidence.
- [ ] In the current 2026-08-09 status, explicitly mark the 2026-08-08
  maintenance-status statement that the skill reads CHANGELOG before prepare
  as historical and superseded. Do not rewrite the historical status file.
- [ ] Extend the already-collected
  `test_cross_family_skill_uses_managed_review_workspace_lifecycle` selector to
  assert that Flow step 4 links both render references before the first
  `reviewer-routing.md` dispatch link. In that same selector, assert the exact
  zero-provider characterization marker and exact branch selector, require them
  to occur before the first `reviewer-routing.md` dispatch link, and assert the
  adjacent no-admission,
  no-convergence/adjudication, packaged-render, packaged-verify, exact-cleanup
  limitation, and Flow step 8 and Flow step 11 back-references.
  Together with
  `test_cross_family_skill_uses_current_task_authority_before_preparing` and
  `test_verifier_archives_head_compares_hashes_and_runs_package_tests`, these
  are the three exact RED selectors above. Make the minimum SKILL,
  verifier, CHANGELOG, and current-status correction, then rerun the same three
  selectors to GREEN.
- [ ] Keep the predeclared collection ledger unchanged: these changes replace
  or extend existing selectors and add no collected case. Because the edited
  `fixture_repo` is shared across `tests/test_distribution_verifier.py`, run that
  exact module after the test-only RED edit and require 8 collected cases with
  exactly the intended
  `test_verifier_archives_head_compares_hashes_and_runs_package_tests` failure
  and the other 7 passing; after the `HASH_TARGETS` implementation, rerun it and
  require exactly 8 passing cases. Also run
  `tests/test_distribution_contract.py` after the test-only RED edit and require
  16 collected cases with exactly the renamed authority selector and extended
  managed-lifecycle selector failing and the other 14 passing; after the
  SKILL/CHANGELOG correction, require exactly 16 passing cases. The remaining expected totals stay 78
  review-round, 16 distribution-contract, 132 focused, and 501 full-suite cases.

### Task 4: Prove GREEN with a new executor and verify the candidate

**Files:**
- Record in: `docs/status/2026-08-09-triad-skill-sot-behavior-test.md`
- Update after current verification:
  `docs/status/2026-08-05-next-session-handoff.md`
- Verify the complete current plugin candidate

**Interfaces:**
- Consumes: Task 3 GREEN bytes and the unchanged Task 1 scenario.
- Produces: fresh behavior evidence, deterministic test evidence, and a clean
  handoff to the existing pre-merge task.

- [ ] After Task 3 edits and focused GREEN complete, record the post-edit root
  and plugin fingerprints plus the executor-profile hash and the exact SHA-256
  values of the source `SKILL.md`, `review-prompt-contract.md`, and
  `leg-contracts.md` in the handoff, then
  end the current root session only when the executor TOML or catalog changed.
  The current owner correction removes the prior profile-level workflow and
  receipt rules, so one final reload is required for that correction. Later
  source `SKILL.md` or script edits require a new child thread, not another root
  restart, while the profile remains byte-identical. Those two repository fingerprints are snapshots
  immediately before the handoff documentation edit; that edit necessarily
  changes the plugin fingerprint, so the next session records a new
  post-handoff baseline rather than comparing it to the stored plugin value.
  The executor-profile hash remains exact and must match. Start a new Codex root session at
  `/Users/chaniri/codex_workspace` so the corrected minimal Custom Agent TOML is reloaded;
  do not attempt Task 4 from the session that edited the profile. In the new
  session, apply the required skills, reread the root instructions, plan, and
  handoff, re-record both repositories' fingerprints, confirm the live catalog
  exposes `triad-skill-executor`, and require its loaded profile to contain the
  exact absolute source `SKILL.md` pin and the Task 3 profile SHA-256. Before
  spawn, require the three current source/reference hashes to equal the exact
  Task 3 handoff values. Diagnose
  a catalog-loading mismatch instead of spawning a default agent.
- [ ] Spawn a new `triad-skill-executor` instance with `fork_turns="none"` and
  the exact Task 1 scenario only after that reload proof. Do not reuse the RED
  thread. Keep the scenario text unchanged and do not inline a replacement path
  or SHA-256: the reloaded registered profile's exact source path plus the
  pre-spawn hash and post-run receipt provide the Task 4 source binding.
- [ ] Before spawning, hash the expected non-system instruction-source set:
  `/Users/chaniri/codex_workspace/AGENTS.md`,
  `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/SKILL.md`,
  and
  `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/review-prompt-contract.md`,
  and
  `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/leg-contracts.md`.
  Require the returned absolute-path receipt to contain exactly those four
  `{path, dependency}` entries. Hash every returned path immediately after the
  executor terminates and require equality with the pre-spawn hashes; unchanged
  root/plugin fingerprints close the interval. The receipt does not invent a
  `sha256` field absent from the unchanged scenario. Its instruction to first
  identify sources needed before preparation orders the initial reads; it does
  not cap the final `instruction_sources` receipt. The supplied scenario requires
  that final receipt to cover every filesystem instruction source actually used
  through the complete exercised scenario. The unchanged scenario
  stops after render, verify, and cleanup without entering the skill's provider
  dispatch step, so it reads the render-stage `leg-contracts.md` but not the
  dispatch-stage `reviewer-routing.md`. It also produces no legs or findings, so
  it does not enter the convergence-reconciliation stage and must not read or
  report `convergence.md`. Any missing or extra receipt entry is a new behavior RED:
  keep the evidence, clean the exact roots, make no further edit, and diagnose
  the source-selection/reporting defect instead of relaxing the expected set.
  Before spawn, verify that the supplied non-filesystem scenario is the current
  task authority and that the workspace-root `AGENTS.md` is the only applicable
  filesystem AGENTS file in the root-to-plugin ancestry; a newly present
  project-level AGENTS file must be added to the hashed expected set rather than
  ignored.
- [ ] Require valid JSON with `status: "SUCCESS"`, an empty `failures` array,
  non-null `managed_review_root`, `prepared_directory`, `manifest`, `snapshot`,
  and a non-empty `rendered_prompts` list, lifecycle cleanup reporting
  `removed: true`, and unchanged pre/post root and plugin fingerprints. After
  the executor terminates, independently require the returned exact
  `managed_review_root` and `_runs/skill-executor/<review-id>/` fixture leaf to be
  absent. Require that no sibling or other managed `triad-review-*` root was
  touched except an older-than-30-days managed root explicitly returned by
  `prepare` in `swept_roots`; record every such supported sweep in the current
  status. Require
  every returned direct `python3`/pytest command to have run through
  `/bin/zsh -lic`. Require one packaged `render` entry in `commands` with exact
  self-reported exit state `0` for every returned `rendered_prompts` path, with
  that path used as the process's `--output` value. Also require a `verify`
  entry in `commands` with exact self-reported exit state `0`. Require that no
  `commands` entry invokes `bin/claude_wrapper.py`,
  `bin/antigravity_wrapper.py`, or `bin/gemini_wrapper.py`; any such entry is a
  scenario/SOT mismatch to preserve and diagnose under the same bounded exit
  below. The unchanged receipt contract has no stdout
  field, so do not require or invent a `ROUND_INTEGRITY_OK` receipt marker and do
  not mislabel the self-reported exit as an independently observed process
  channel. For this characterization only, the supplied current-task authority
  satisfies the Task 3 branch selector because it prohibits provider dispatch
  and directs the lifecycle through `verify` and exact cleanup, with no
  convergence/adjudication read. `SUCCESS` describes completion of that characterization only
  and is never review admission or gate passage; this deterministic lifecycle
  branch does not change the skill's general three-leg flow. A `WORKFLOW_DEFECT` or extra
  `convergence.md` receipt entry citing only missing provider legs or absent
  adjudication is a scenario/SOT ordering mismatch to preserve and diagnose
  before any further edit, not a source-selection RED. Use the same bounded
  no-global-change diagnosis and owner-escalation exit defined for the source
  selection hypothesis if the mismatch cannot be resolved without changing the
  approved scenario.
- [ ] After the executor's exact cleanup, use a second new unique review ID and
  the exact disposable fixture
  `/Users/chaniri/codex_workspace/_runs/skill-executor-leader/<same-second-id>/`
  to repeat the same post-Task-3 prepare, manifest, capture, render, verify, and
  cleanup lifecycle without provider dispatch. The leader owns these commands
  and must independently observe the verify process exit `0` and stdout
  `ROUND_INTEGRITY_OK` marker. Use the same special JSON string classes, do not
  salvage any failure, clean only the supported exact managed root, then remove
  only that exact leader fixture leaf and confirm both are absent. This
  reproduction is the authoritative process-exit/stdout proof; it complements
  but does not replace the required fresh executor or relax its acceptance
  fields.
- [ ] Record the post-edit executor-profile SHA-256, executor identity,
  requested model/effort, and any runtime-exposed model/effort in the current
  status before accepting the GREEN receipt. The profile is workspace-owned
  external evidence and is not a plugin archive/cache target.
- [ ] Run the focused tests, full suite, skill validation, `bash -n`,
  `git diff --check`, and the existing lifecycle smoke using the exact commands
  and count policy in the lifecycle plan. Skill validation means exactly:

  ```zsh
  /bin/zsh -lic 'python3 /Users/chaniri/.codex/skills/.system/skill-creator/scripts/quick_validate.py workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review'
  ```
- [ ] Update the current handoff with observed commands and results only after
  they run; never copy a historical pass count as current proof. At that point,
  replace its stale statement that `skills.config` enables a skill folder with
  the observed exact source `SKILL.md` file pin. After this final documentation
  edit, rerun `tests/test_distribution_contract.py` and require exactly 16
  passing cases before Task 5.

### Task 5: Complete the existing pre-merge and distribution pipeline

**Files:**
- Resume: `docs/superpowers/plans/2026-08-08-review-workspace-lifecycle.md`
  Task 10 and Task 11

**Interfaces:**
- Consumes: the combined verified lifecycle/JSON/skill-SOT candidate.
- Produces: final three-family admission, exact package bytes, push, local
  installation, and fresh-session exposure proof.

- [ ] Run one new mandatory three-family pre-merge round over the combined
  candidate. Do not reuse R30 or any earlier verdict.
- [ ] After all three pre-merge legs terminate and final integrity verification
  passes, keep the exact review root only long enough to bind the reviewed bytes.
  Require the pre-merge member list to contain every current plugin candidate
  path plus all fourteen load-bearing distribution targets listed in Task 3.
  Without changing a worktree file, compare every listed plugin member to its
  exact `source/product/<member>` entry in the current `SOURCE_SHA256SUMS`,
  create the intentional plugin candidate commit with the review ID and content
  digest in its commit message, and compare every committed `HEAD:<member>`
  byte to that same manifest entry. An absent entry, mismatch, or any worktree
  change restarts pre-merge. The workspace-owned executor profile is not a
  `source/product` member; recheck it against the Task 4 post-edit hash and
  fingerprint instead. Clean the exact review root only after the commit tree
  and external-profile check are bound, then run distribution verification from
  clean HEAD.
- [ ] Compare source, archive, and installed-cache hashes for only the exact
  fourteen load-bearing distribution targets listed in Task 3 against the
  reviewed commit tree. This is a bounded load-bearing subset, not a hash proof
  of every distributed file: non-target files such as
  `skills/triad-antigravity-dispatch/SKILL.md` are bound to the reviewed commit
  and archive construction but are not independently hash-compared in the
  installed cache, so same-version cache staleness for them remains a recorded
  residual. The installed-cache files executed by the approved bootstrap step
  but outside that subset are exactly `scripts/bootstrap.sh` and
  `bin/bootstrap_repair.py`: after the supported plugin install and before
  executing bootstrap, compare both files byte-for-byte to their reviewed
  `HEAD:<path>` values and stop on any absence or mismatch. These
  execution-provenance checks do not
  enlarge the fourteen-target distribution subset. Task 1 did not run an install, so its
  pre-install cache mismatch is not evidence that the supported same-version
  update cannot replace bytes and does not authorize a version bump. Accept the
  owner-approved `0.2.533` cache only when every installed target hash equals the
  reviewed commit/source/archive hash after the supported install command; never
  overwrite or salvage cache files manually.
- [ ] Before external installation, state the exact plugin/cache/bootstrap
  targets, including the separately checked installed-cache
  `scripts/bootstrap.sh` and `bin/bootstrap_repair.py`, delta, and impact and obtain the target-specific current-conversation
  approval required by the root `AGENTS.md`. Then push and install only the
  reviewed bytes. If the supported same-version install cannot replace the stale
  cache without an unapproved user-global setting change, stop and report the
  workflow defect instead of bypassing it.
- [ ] Retain the lifecycle-plan Task 11 installed-exposure contract in full. Run
  a fresh `codex exec --ephemeral` probe that proves the installed skill exposes
  the JSON member list, `manifest` command, JSON metadata, unique-ID cleanup,
  and this exact current marker:

  ```text
  A current task may explicitly authorize a lifecycle characterization with zero provider legs.
  ```

  Before install, prove the stale same-version installed skill does not contain
  that literal; after install, require the fresh ephemeral process to return it
  exactly from the loaded installed skill. The fourteen-target hashes do not
  supersede any of these behavior proofs. Do not tag, publish, merge, or release.

## New-session continuation prompt

```text
/Users/chaniri/codex_workspace 에서 TRIAD 작업을 계속 진행해. 먼저 $superpowers:using-superpowers, $superpowers:executing-plans, $superpowers:test-driven-development, $superpowers:writing-skills 를 적용하고, root AGENTS.md와 현재 live agent catalog를 확인해. 다음 두 파일을 작업 기준으로 읽어:

- /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-08-05-next-session-handoff.md
- /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/superpowers/plans/2026-08-09-triad-skill-sot-behavior-test.md

루트와 plugin 저장소의 git status, HEAD, status fingerprint, diff fingerprint를 먼저 기록하고 기존 dirty tree를 보존해. 현재 중단점은 lifecycle plan Task 0-9 완료, formal-plan R30 admitted SAFE, Task 10 pre-merge와 Task 11 package/push/install 미시작 상태야. 기존 lifecycle Task 10부터 실행하지 말고 새 skill-SOT plan을 순서대로 진행해.

먼저 새 세션의 catalog에 triad-skill-executor가 실제 노출되는지 확인해. 노출되지 않으면 default agent로 우회하지 말고 catalog loading 문제를 진단해서 고쳐. 노출되면 agent_type="triad-skill-executor", fork_turns="none"인 새 인스턴스로 plan Task 1의 정확한 RED 시나리오를 실행해. executor는 지정된 triad-cross-family-review만 사용하고 SOT를 수정하거나 다른 skill을 호출하면 안 돼. 결과와 cleanup, pre/post fingerprint를 새 status record에 남겨. Task 1에서는 plugin을 고치지 마.

그 다음 Task 2의 fresh-ID Claude/Google/fresh-Codex 3가족 formal-plan review를 완료한 뒤에만 Task 3 최소 TDD 수정을 해. 도구, CLI, MCP, read, search, web 기능을 제한하거나 user-global 설정을 바꾸지 마. workflow defect는 우회하지 말고 skill/tool과 regression을 고친 뒤 새 ID로 전체 절차를 다시 시작해. 설계 확장이 필요할 때만 concrete delta/evidence/impact를 나에게 알리고 멈춰.

Task 4는 RED thread를 재사용하지 말고 새 triad-skill-executor로 동일 시나리오를 GREEN 검증해. 이후 전체 검증과 fresh 3가족 pre-merge를 통과한 같은 bytes만 package, push, install하고 fresh ephemeral installed-skill proof를 수행해. tag/publish/merge/release는 하지 마. 생성한 review root와 fixture는 정확한 unique root만 cleanup하고 sibling이나 다른 프로세스의 파일은 건드리지 마.
```
