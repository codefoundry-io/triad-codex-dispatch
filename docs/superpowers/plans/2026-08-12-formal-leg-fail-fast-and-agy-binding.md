# Formal Leg Fail-Fast and AGY Binding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` or `superpowers:executing-plans` to
> implement this plan task-by-task. Use `superpowers:test-driven-development`
> for code and `superpowers:writing-skills` with the project-scoped
> `triad-skill-executor` for skill behavior.

**Goal:** Prevent under-bound native AGY verdicts and make the first required-leg
failure cancel the complete TRIAD round without leaving provider descendants.

**Architecture:** Keep `LegVerdict` and local validation authoritative. Add
round-specific constants only to the AGY native schema, then share one provider
process-group teardown path between timeout and interruption. The skill remains
the operational SOT and specifies fail-fast sibling cancellation.

**Tech Stack:** Python 3.12, Pydantic 2, pytest, AGY 1.1.12 native
`stream-json`/`json-schema`, Markdown skill contracts.

## Global Constraints

- No provider retry, fallback, substitution, or result normalization.
- No user-global configuration edits; deploy only through the supported plugin
  build/install path after source verification.
- Preserve standalone unbound AGY consult behavior.
- Every required-leg failure invalidates and discards the complete round.
- Slice A and Slice B are separate one-claim S/M merge-gate units.
- Run every direct `python3` command through `/bin/zsh -lic` from
  `/Users/chaniri/codex_workspace` after recording Python and pytest versions.

---

### Task 1: Slice A — bind native AGY LegVerdict generation

**Files:**
- Modify: `bin/verdict_schema.py`
- Modify: `bin/antigravity_wrapper.py`
- Modify: `tests/test_verdict_schema.py`
- Modify: `tests/test_antigravity_stream_json.py`
- Modify: `skills/triad-cross-family-review/references/leg-contracts.md`
- Modify: `tests/test_distribution_contract.py`

**Interfaces:**
- Consumes: exact `review_id`, `family=google`, and `content_digest` already
  carried by the rendered prompt and final validator.
- Produces: one native JSON Schema with path constraints and three exact
  constants; one locally bound admitted object.

- [ ] **Step 1: Add RED schema tests.** Assert the emitted path item schemas
  reject a leading slash/backslash shape and that a requested formal schema
  contains exact constants for review ID, family, and digest.
- [ ] **Step 2: Run the focused tests and require the expected RED.**

  ```bash
  /bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_verdict_schema.py workspace/triad-codex-dispatch-reliability/tests/test_antigravity_stream_json.py -q'
  ```

  Expected: failures because the native schema is unbound and the formal
  wrapper arguments do not exist.

- [ ] **Step 3: Implement the minimum schema/binding path.** Add JSON-Schema-
  visible relative-path constraints to the existing string fields. Add three
  optional formal binding CLI arguments that must appear together; use them to
  set native schema constants and locally compare the admitted payload.
- [ ] **Step 4: Update the formal Google command.** Pass
  `--expected-review-id "$review_id"`, `--expected-family google`, and
  `--expected-content-digest "$review_digest"`; pin this command in the
  distribution contract test.
- [ ] **Step 5: Run focused and full wrapper/schema tests GREEN.**
- [ ] **Step 6: Commit Slice A.**

  ```bash
  git add bin/verdict_schema.py bin/antigravity_wrapper.py tests/test_verdict_schema.py tests/test_antigravity_stream_json.py skills/triad-cross-family-review/references/leg-contracts.md tests/test_distribution_contract.py
  git commit -m "fix: bind formal AGY verdict generation"
  ```

### Task 2: Slice B — reap interrupted providers and fail fast

**Files:**
- Modify: `bin/_common.py`
- Modify: `tests/test_provider_wrappers.py`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `skills/triad-cross-family-review/references/leg-contracts.md`
- Modify: `skills/triad-cross-family-review/references/reviewer-routing.md`
- Modify: `skills/triad-cross-family-review/references/convergence.md`
- Modify: `tests/test_distribution_contract.py`

**Interfaces:**
- Consumes: the provider process/session created by `_run_once()` and the first
  observed required-leg failure.
- Produces: terminated/reaped provider process group and a discarded, verified,
  exactly cleaned invalid round.

- [ ] **Step 1: Capture the skill RED behavior.** Run a fresh
  `triad-skill-executor` over the current SOT with the pressure scenario where
  AGY fails early and expensive siblings remain healthy. Record whether it
  chooses advisory continuation.
- [ ] **Step 2: Add RED process teardown test.** Inject an interruption while
  `_run_once()` waits; require termination of the created process group,
  bounded wait/reap, and re-raising the identical interruption.
- [ ] **Step 3: Run the focused test and require the expected RED.**
- [ ] **Step 4: Implement one teardown helper.** Reuse it from timeout and the
  interruption path; do not add a daemon or external process registry.
- [ ] **Step 5: Make the skill fail-fast.** State the positive action sequence:
  first invalid leg → cancel exact sibling process trees → wait for termination
  → discard all verdicts → integrity verification → exact cleanup → repair
  infrastructure. Remove any wording that drives advisory continuation.
- [ ] **Step 6: Run a fresh `triad-skill-executor` GREEN trial.** Require choice
  B and the exact ordered action sequence without edits or provider dispatch.
- [ ] **Step 7: Run focused tests GREEN and commit Slice B.**

  ```bash
  git add bin/_common.py tests/test_provider_wrappers.py skills/triad-cross-family-review/SKILL.md skills/triad-cross-family-review/references/leg-contracts.md skills/triad-cross-family-review/references/reviewer-routing.md skills/triad-cross-family-review/references/convergence.md tests/test_distribution_contract.py
  git commit -m "fix: cancel invalid TRIAD rounds fail fast"
  ```

### Task 3: Verify, package, and deploy the same bytes

**Files:**
- Modify only if required by the existing release workflow: `CHANGELOG.md`,
  `.codex-plugin/plugin.json`, and matching distribution assertions.
- Verify: `scripts/verify_distribution.py`, `scripts/bootstrap.sh`, complete
  `tests/`.

**Interfaces:**
- Consumes: committed Slice A and Slice B bytes.
- Produces: full regression evidence, validated skill behavior, distributable
  package, installed current marker, and fresh-process exposure.

- [ ] **Step 1: Run Python preflight and all focused tests.**
- [ ] **Step 2: Run `tests/test_review_round.py`, then the complete `tests/`
  suite with an exact workspace-owned test root and cleanup.**
- [ ] **Step 3: Run the official skill validator, `git diff --check`, and
  distribution verifier.**
- [ ] **Step 4: Build the supported distribution and compare required source
  files byte-for-byte with the package.**
- [ ] **Step 5: Install through the supported bootstrap/plugin path and run a
  fresh Codex skill-exposure proof.**
- [ ] **Step 6: Commit/push/release only as prescribed by the current release
  workflow. Do not merge without separate owner approval.**

### Task 4: Resume Argus with a fresh complete round

**Files:**
- Do not change Argus candidate bytes until the infrastructure deployment is
  proven.
- Create only a new unique current-round review root and result set.

**Interfaces:**
- Consumes: deployed fail-fast TRIAD skill and the unchanged current Argus
  worktree basis.
- Produces: one fresh Claude/Google/Codex round or an immediate fail-fast
  infrastructure stop.

- [ ] **Step 1: Verify the Argus worktree fingerprint and current plan digest.**
- [ ] **Step 2: Prepare/render a fresh review ID; never reuse R7 artifacts.**
- [ ] **Step 3: Start all three legs. On the first required-leg failure, apply
  the new fail-fast cancellation contract.**
- [ ] **Step 4: Admit results only after all three succeed and final integrity
  verification passes.**

