# Triad R4 Bounded Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the six deterministically confirmed R3 defects and apply a simple one-hour best-effort cleanup policy without expanding the runtime.

**Architecture:** Reuse the existing wrapper, bootstrap, file-IPC, and Antigravity settings boundaries. Add validation or fail-stop behavior only at those boundaries, remove the inert setup runtime, and keep generic non-formal wrapper behavior unchanged.

**Tech Stack:** Python 3.12 standard library, Pydantic 2, POSIX shell, pytest 9, macOS, Ubuntu 24.04.

## Global Constraints

- Preserve every unrelated dirty-tree change.
- Do not stage, commit, push, or install until the fresh R4 review gate passes.
- Run direct `python3` and Python tests outside the Codex filesystem sandbox from `/Users/chaniri/codex_workspace`.
- Use no new Python dependency and no OS-specific cleanup tool.
- Cleanup is best-effort, uses the existing UUID IPC namespace, and deletes only managed entries older than 3,600 seconds.
- Claude tokens remain unavailable; the temporary formal gate is two Gemini 3.1 Pro (High) legs plus two fresh-context Codex legs.

---

### Task 1: Bind formal dispatch to actual sealed bytes

**Files:**
- Modify: `bin/_common.py`
- Modify: `bin/triad_formal_review_schema.py`
- Modify: `bin/antigravity_wrapper.py`
- Modify: `tests/test_provider_packet_context.py`
- Modify: `tests/test_antigravity_packet_context.py`
- Modify: `tests/test_formal_review_schema.py`

**Interfaces:**
- Consumes: `build_validation_context(pydantic_cls, sealed_packet_root, expected_packet_sha256)`.
- Produces: `FormalReview.verify_sealed_packet(context)`, called by `build_validation_context` before provider resolution and by schema validation; both generic and AGY drivers treat a non-empty sealed validation context as formal and disable their internal schema retry.

- [ ] Add packet-fixture helpers that write a real `INPUT_SHA256SUMS`, `SHA256SUMS`, and `PACKET_SHA256`.
- [ ] Add failing tests proving a valid packet reaches provider resolution while a tampered manifest, tampered input, or mismatched expected digest stops first.
- [ ] Run the focused tests and confirm the failures are caused by the missing byte verification.
- [ ] Implement `FormalReview.verify_sealed_packet(context)` by reusing the schema module's existing no-follow reader. Make `build_validation_context` require and call that verifier for a context-bearing schema; reject unsafe manifest paths, symlink/non-regular leaves, duplicates, missing files, and digest mismatches.
- [ ] Add a failing test proving sealed formal validation returns `schema-fail` after one provider response while a plain custom schema still receives its existing single repair retry.
- [ ] Add the minimal formal/no-repair branch and run the focused tests to green.

Run from the workspace root:

```sh
python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_provider_packet_context.py workspace/triad-codex-dispatch-reliability/tests/test_antigravity_packet_context.py workspace/triad-codex-dispatch-reliability/tests/test_formal_review_schema.py
```

Expected: new tests fail before production edits and all selected tests pass after the minimal implementation.

### Task 2: Keep IPC cleanup simple and restore failed AGY entry

**Files:**
- Modify: `bin/_common.py`
- Modify: `bin/_agy_settings.py`
- Modify: `bin/antigravity_wrapper.py`
- Modify: `tests/test_log_cleanup.py`
- Create: `tests/test_agy_settings.py`
- Modify: `tests/test_antigravity_packet_context.py`

**Interfaces:**
- Consumes: `prune_stale_run_logs(cli, age_floor_s=3600)` at the start of normal dispatch and `_shared_readonly_guard(...)`.
- Produces: best-effort one-hour managed cleanup before generic provider execution and before AGY preflight/settings/provider work, plus immediate restore when first-reader deny installation fails after mutation.

- [ ] Change cleanup tests first so a managed file older than 3,600 seconds is removed, a newer file and unrelated name remain, a symlinked managed root/leaf is skipped, and an unlink error does not block dispatch.
- [ ] Run the focused cleanup tests and confirm the default-floor assertion fails.
- [ ] Set `_STALE_IPC_AGE_FLOOR_S = 3600`, reuse the existing no-follow regular-file helpers for the time sweep, and update only the now-inaccurate comments; do not add another cleanup subsystem.
- [ ] Add a failing AGY ordering test, then move the existing AGY cleanup call from `_run_agy_with_retry` to `main` before preflight/settings/provider work. Keep generic wrapper cleanup in `run_cli_with_retry`.
- [ ] Add a failing AGY test whose fake `_merge_deny` writes changed settings and then raises; assert the original bytes are restored during the same call.
- [ ] Run it and confirm it exposes the current `mutated = False` gap.
- [ ] Mark restore responsibility immediately after the durable backup and before `_merge_deny`, then run both focused test files to green.

Run:

```sh
python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_log_cleanup.py workspace/triad-codex-dispatch-reliability/tests/test_agy_settings.py workspace/triad-codex-dispatch-reliability/tests/test_antigravity_packet_context.py
```

Expected: all selected tests pass; cleanup exceptions remain non-fatal.

### Task 3: Repair bootstrap publication and removal boundaries

**Files:**
- Modify: `scripts/bootstrap.sh`
- Modify: `tests/test_bootstrap.py`
- Delete: `bin/triad_runtime.py`
- Delete: `tests/test_triad_runtime.py`

**Interfaces:**
- Consumes: existing `preflight_install_command_targets`, command-group transaction helpers, profile/rules environment options, and `run_remove`.
- Produces: a pre-publication profile/rules target check, three public wrapper commands only, and a removal fail-stop before any later state mutation.

- [ ] Add failing install tests for live and dangling profile/rules symlink leaves and a symlinked `rules` ancestor; assert no wrapper command is published and external targets are unchanged.
- [ ] Add the smallest Python-backed bootstrap preflight before `begin_command_group`, gated by the existing profile/rules install choices, and repeat the leaf check immediately before each write.
- [ ] Replace five-command expectations with the three wrapper commands and add a failing distribution test proving `triad-setup`, `triad-doctor`, and `triad_runtime.py` are absent.
- [ ] Remove runtime command installation/staging/preflight/verification code and delete the inert runtime module and its dedicated test. Retain only the managed-name recognition and `--remove` queue entries needed to clean `triad-setup` and `triad-doctor` from an older installation.
- [ ] Add a failing removal test that injects command-group removal failure and asserts shell entry, repair registration, profile, config fragment, rules, and classifier state remain unchanged.
- [ ] Move shell-entry removal after successful command-group removal and return immediately if that group adds an error.
- [ ] Run the complete bootstrap and distribution tests to green.

Run:

```sh
python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py workspace/triad-codex-dispatch-reliability/tests/test_bootstrap_repair_transaction.py workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py
```

Expected: all selected tests pass with only the three provider wrapper commands installed.

### Task 4: Align public documentation and skill prompts

**Files:**
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `SECURITY.md`
- Modify: `CHANGELOG.md`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `skills/triad-antigravity-dispatch/SKILL.md`
- Modify: `skills/triad-claude-dispatch/SKILL.md`
- Modify: `skills/triad-gemini-dispatch/SKILL.md`
- Modify: `tests/test_distribution_contract.py`

**Interfaces:**
- Consumes: behavior completed by Tasks 1-3.
- Produces: concise public claims for verified packet preflight, leader-owned formal retries, one-hour best-effort IPC cleanup, three installed commands, and user-owned provider login.

- [ ] Add or update distribution assertions first so stale runtime-command and hidden formal-retry claims fail.
- [ ] Update documentation and skills with the implemented behavior; do not add a company setup flow or a new authorization store.
- [ ] Run distribution tests to green.
- [ ] Run `skill-prompt-review` against the four shipped dispatch/review skills, fix only concrete contradictions or ambiguity, and record the review result in the R4 evidence directory.

Run:

```sh
python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py workspace/triad-codex-dispatch-reliability/tests/test_migration_contract.py
```

Expected: all selected tests pass and the skill review reports no unresolved blocking prompt defect.

### Task 5: Verify once, freeze R4, and run the formal gate

**Files:**
- Create under ignored evidence only: `_runs/sdd/*` and `_runs/reviews/<fresh-r4-id>/*`
- Modify tracked status/changelog only if required by the established distribution contract.

**Interfaces:**
- Consumes: completed R4 candidate and existing deterministic R3 verification tooling.
- Produces: macOS and Ubuntu verification evidence, a fresh immutable packet, four terminal review legs, and a reconciled gate decision.

- [ ] Run `git diff --check`, shell syntax, Python compile, plugin validation, skill lint, and the complete macOS pytest suite.
- [ ] Run the existing Ubuntu 24.04 verification path once; do not build unrelated artifacts.
- [ ] Freeze all affected and impact-related code, tests, docs, manifests, and verification evidence under one new review ID; verify all hashes before dispatch.
- [ ] Preflight and queue two exact Gemini 3.1 Pro (High) legs, then launch two `fork_turns="none"` fresh Codex legs with frozen complementary perspectives before reading any verdict.
- [ ] Reconcile evidence rather than votes. If clean, stage and commit only this product worktree, push its branch, install with the documented bootstrap, and verify the installed plugin in a fresh session.

Expected: one valid R4 gate, or a precise fail-closed record if a required route changes or becomes unavailable.
