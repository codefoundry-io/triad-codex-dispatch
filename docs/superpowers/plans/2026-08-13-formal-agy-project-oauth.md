# Formal AGY Project OAuth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the formal Google review leg use only native AGY OAuth inside an explicitly verified read-only AGY Project, with no Gemini fallback or permission bypass.

**Architecture:** Add one read-only AGY Project contract parser beside the provider wrapper. The formal wrapper validates the selected Project before provider submission, strips separately billed route selectors from only the child environment, invokes AGY with `--project` and `--sandbox`, and never emits `--dangerously-skip-permissions`. The formal skill and bootstrap use that single route and fail closed.

**Tech Stack:** Python 3.12, Bash, pytest, the existing distribution builder/verifier, and the `triad-cross-family-review` skill.

## Global Constraints

- One S/M behavioral claim: a formal Google review call uses only native OAuth AGY in a verified read-only AGY Project.
- Production/script net delta at most 260 lines; novel project-binding/validation core at most 140 lines.
- Do not read, copy, log, inject, refresh, or mutate authentication credentials.
- Do not modify global `~/.gemini/antigravity-cli/settings.json`.
- Do not invoke Gemini CLI, API-key, Vertex, service-account, or other separately billed routes.
- Do not use `skill-prompt-review` for the three-family review.
- Skill behavior verification runs through the dedicated `triad-skill-executor` subagent.

---

### Task 1: Enforce the formal AGY Project OAuth route

**Files:**
- Create: `bin/agy_project.py`
- Modify: `bin/_common.py`
- Modify: `bin/antigravity_wrapper.py`
- Modify: `scripts/bootstrap.sh`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `skills/triad-cross-family-review/references/reviewer-routing.md`
- Modify: `skills/triad-cross-family-review/references/leg-contracts.md`
- Modify: `README.md`
- Test: `tests/test_agy_project.py`
- Test: `tests/test_antigravity_stream_json.py`
- Test: `tests/test_bootstrap.py`
- Test: `tests/test_distribution_contract.py`

**Interfaces:**
- Consumes: AGY project mapping at `~/.gemini/antigravity-cli/cache/projects.json`, project record at `~/.gemini/config/projects/<project-id>.json`, and the existing AGY native stream contract.
- Produces: `agy_project.verify_project_binding(project_id, workspace) -> str`, returning the verified project ID; `_common._run_once(..., remove_env=())`; and formal wrapper arguments `--project` plus `--project-workspace`.

- [ ] **Step 1: Write static and unit RED tests**

  Require all of the following before changing production bytes:

  - the formal command contains `--project <id>` and `--sandbox`;
  - no formal command contains `--dangerously-skip-permissions`;
  - missing project arguments, resource disagreement, symlinked/malformed project files, and any missing exact deny rule stop before `_run_once`;
  - the AGY child lacks `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_GENAI_USE_ENTERPRISE`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GOOGLE_CLOUD_REGION`, `GOOGLE_CLOUD_QUOTA_PROJECT`, and `AGY_ADC_AUTH`, while the parent environment remains unchanged;
  - bootstrap requires AGY and never accepts Gemini as the formal Google route;
  - active formal skill text contains no Gemini fallback and requires the verified Project route.

- [ ] **Step 2: Run RED and record the causal failures**

  Run the focused pytest selectors from the login-shell Python environment. Expected: failures show the current danger flag, missing Project verifier/arguments, ambient billed-route variables reaching the child, and active Gemini fallback text.

- [ ] **Step 3: Implement the minimal Project verifier and wrapper route**

  `agy_project.py` must read only regular non-symlink JSON files, validate one exact selected project ID, require the reviewed workspace as the Project's sole `file://` resource, and require the five deny rules. It must not write either AGY registry file. Extend `_run_once` only with an optional set of environment variable names to omit. The wrapper performs this check before provider submission and uses `--project`, `--sandbox`, and the existing stream/schema/model arguments.

- [ ] **Step 4: Remove the formal fallback and update bootstrap/docs**

  Keep standalone Gemini tooling packaged for explicitly requested non-formal enterprise work. Make the cross-family skill AGY-only, make any AGY/preflight failure invalidate the whole round, and update bootstrap/readme language to native OAuth plus project-scoped permission prerequisites.

- [ ] **Step 5: Run focused and full GREEN verification**

  Run the affected wrapper, bootstrap, distribution-contract, full test suite, format/lint, `git diff --check`, and production-delta checks. No provider model call is part of this step.

- [ ] **Step 6: Run dedicated skill GREEN behavior testing**

  Dispatch `triad-skill-executor` against the canonical current SOT with an unavailable-AGY/API-key-present pressure scenario. It must make no provider call, must invalidate the round, must not select Gemini, and must report the exact Project/OAuth repair boundary.

- [ ] **Step 7: Prove installed AGY behavior with one disposable-project spike**

  After obtaining the required exact external-path authorization for the disposable AGY Project registry records, bind a workspace-managed disposable review directory, use native OAuth only, and prove one file-view read succeeds while write and command attempts are denied without a danger flag. Remove only the exact disposable Project records and workspace mapping afterward; preserve the spike evidence under the repository `_runs/` directory.

- [ ] **Step 8: Build, verify, release, and install**

  Build the distribution from current committed bytes, run the unpacked-distribution verifier, commit/push/release under standing authorization, install the updated plugin, and perform a fresh-session exposure check. Stop before final merge for owner approval.
