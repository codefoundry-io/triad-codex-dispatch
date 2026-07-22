# Approval Setting Inheritance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the generated triad runtime profile inherit the owner's `approval_policy` and `approvals_reviewer` by default while preserving the explicit `TRIAD_CODEX_PROFILE_APPROVAL_POLICY` advanced override.

**Architecture:** Keep `default_permissions = "triad_leader"` and the existing permission profile unchanged. Track whether the approval-policy environment variable was explicitly supplied, omit both approval keys from the default overlay, and emit only `approval_policy` for an explicit supported override.

**Tech Stack:** Bash, embedded Python 3, pytest, TOML, Markdown.

## Global Constraints

- Never generate `approval_policy = "never"` unless `TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never` was explicitly supplied.
- Never generate `approvals_reviewer`; inherit the owner's base/workspace value.
- Do not add a launcher, permission system, or new runtime profile.
- Preserve `default_permissions = "triad_leader"` and all existing filesystem/network restrictions.
- Do not modify `/Users/chaniri/triad-codex-dispatch`.

---

### Task 1: Implement the inherited approval overlay with TDD

**Files:**
- Modify: `scripts/bootstrap.sh`
- Modify: `tests/test_bootstrap.py`
- Modify: `tests/test_distribution_contract.py`

**Interfaces:**
- Consumes: `_run_bootstrap(tmp_path, env_overrides=...)` and generated `$CODEX_HOME/triad-codex-dispatch.config.toml`.
- Produces: regression coverage and a generator that inherits approval settings by default while preserving explicit policy overrides.

- [x] **Step 1: Change the default assertions and add an owner-config regression**

```python
data = tomllib.loads(profile.read_text(encoding="utf-8"))
assert "approval_policy" not in data
assert "approvals_reviewer" not in data
assert data["default_permissions"] == "triad_leader"
```

```python
def test_default_runtime_profile_inherits_owner_approval_settings(tmp_path):
    codex_home = tmp_path / "owner-codex-home"
    codex_home.mkdir()
    base_config = codex_home / "config.toml"
    base_config.write_text(
        'approval_policy = "on-request"\n'
        'approvals_reviewer = "auto_review"\n',
        encoding="utf-8",
    )

    result, env, _launcher_bin = _run_bootstrap(
        tmp_path,
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert result.returncode == 0, result.stderr + result.stdout
    base_data = tomllib.loads(base_config.read_text(encoding="utf-8"))
    assert base_data["approval_policy"] == "on-request"
    assert base_data["approvals_reviewer"] == "auto_review"
    profile = Path(env["CODEX_HOME"]) / "triad-codex-dispatch.config.toml"
    profile_data = tomllib.loads(profile.read_text(encoding="utf-8"))
    assert "approval_policy" not in profile_data
    assert "approvals_reviewer" not in profile_data
    assert profile_data["default_permissions"] == "triad_leader"
```

- [x] **Step 2: Cover every explicit override and the empty-string boundary**

```python
@pytest.mark.parametrize("approval_policy", ["on-request", "never", "untrusted"])
def test_check_can_install_runtime_profile_with_explicit_approval_policy(...):
    ...
    assert data["approval_policy"] == approval_policy
    assert data.keys() & {"approval_policy", "approvals_reviewer"} == {
        "approval_policy"
    }

def test_empty_runtime_profile_approval_policy_inherits_owner_settings(...):
    ...
    assert "approval_policy" not in data
    assert "approvals_reviewer" not in data
    assert data["default_permissions"] == "triad_leader"
```

- [x] **Step 3: Run the initial focused tests and verify RED**

Completed before implementation: the focused owner-inheritance, default
profile, and explicit-override tests failed because the overlay still emitted
`on-request` and `user`.

- [x] **Step 4: Record explicit override presence**

```bash
CODEX_PROFILE_APPROVAL_POLICY="${TRIAD_CODEX_PROFILE_APPROVAL_POLICY:-on-request}"
CODEX_PROFILE_APPROVAL_POLICY_EXPLICIT=0
if [ -n "${TRIAD_CODEX_PROFILE_APPROVAL_POLICY:-}" ]; then
  CODEX_PROFILE_APPROVAL_POLICY_EXPLICIT=1
fi
```

- [x] **Step 5: Pass and validate the explicitness flag in the embedded generator**

Pass `CODEX_PROFILE_APPROVAL_POLICY_EXPLICIT` immediately after the policy value. Accept only `"0"` or `"1"`, then construct:

```python
approval_policy_line = (
    f'approval_policy = {toml_string(approval_policy)}\n'
    if approval_policy_explicit == "1"
    else ""
)
```

- [x] **Step 6: Render the bounded overlay**

```python
{approval_policy_line}default_permissions = "triad_leader"
```

Remove the generated `approvals_reviewer` line completely.

- [x] **Step 7: Run focused tests and verify GREEN**

Run the explicit override matrix plus empty-string regression:

```bash
python3 -m pytest \
  tests/test_bootstrap.py::test_check_can_install_runtime_profile_with_explicit_approval_policy \
  tests/test_bootstrap.py::test_empty_runtime_profile_approval_policy_inherits_owner_settings -q
```

Completed result: `4 passed`.

- [x] **Step 8: Align the distribution wording contract**

Replace assertions that force `on-request` for unrelated commands with assertions that the owner's inherited approval configuration remains in force, while retaining the absolute-launcher auto-allow and no-false-per-wrapper-prompt checks. Run the two focused contract tests and `tests/test_distribution_contract.py` in full.

Completed result: `52 passed` for `tests/test_distribution_contract.py` after
adding the Git security-review publication contract.

### Task 2: Align operator documentation and handoff state

**Files:**
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `docs/status/2026-07-22-current-state.md`
- Modify: `docs/status/2026-07-22-resume-prompt.md`

**Interfaces:**
- Consumes: the Task 1 generation contract.
- Produces: installation guidance that distinguishes inherited defaults from the explicit advanced override.

- [x] **Step 1: Document default inheritance**

Use this contract in both READMEs: "By default, the generated triad profile omits `approval_policy` and `approvals_reviewer`, so Codex inherits the owner's existing layered approval configuration unchanged."

- [x] **Step 2: Preserve the advanced-mode warning**

Use this contract in both READMEs: "Setting `TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never` explicitly emits only `approval_policy = \"never\"`; it remains an opt-in advanced mode and never changes `approvals_reviewer`."

- [x] **Step 3: Supersede the known-defect handoff**

Record the local proof and bounded source repair without rewriting the immutable R14 review history. Replace the obsolete restart instruction that says the defect remains unfixed.

### Task 3: Verify the bounded repair

**Files:**
- Verify only; no additional implementation files.

**Interfaces:**
- Consumes: Tasks 1-2.
- Produces: fresh macOS test evidence and a review-ready diff.

- [x] **Step 1: Run direct Python preflight from the workspace root**

Record `command -v python3`, `python3 --version`, and `python3 -m pytest --version` outside the filesystem sandbox as required by the workspace instructions.

Completed result: literal `python3` resolved to Python `3.12.13`; pytest was
`9.0.3`.

- [x] **Step 2: Run focused bootstrap tests**

Run the changed profile tests first.

Completed result: `4 passed`.

- [x] **Step 3: Run the complete suite**

Run exactly:

```bash
python3 -m pytest /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/tests -q
```

Completed result: `608 passed, 6 subtests passed in 125.65s` after the final
Git security-review handoff regression was added.

- [x] **Step 4: Review the final diff and address its bounded findings**

Confirm that changes are limited to profile generation, directly affected tests/docs, and this plan. Do not commit, push, reinstall, or bump a release version until the review gate is chosen.

Completed result: task reviews approved. The initial whole-diff review returned
`With fixes` only for the handoff/test-plan items addressed by the final-review
fix wave.

### Task 4: Close the final gate

- [x] **Step 1: Complete final re-review of the intentional uncommitted diff**

Completed result: `APPROVED` with no Critical, Important, or Minor findings;
all supplied frozen-artifact SHA-256 hashes matched.

- [x] **Step 2: Ask the owner for the distribution decision**

The owner authorized commit and push for this bounded repair, acknowledging
that Git history and remote-state changes may trigger the workspace's automatic
security approval flow. Version/changelog changes, reinstall, release, and
pull-request creation remain separate and pending. Preserve the immutable R14
review history.
