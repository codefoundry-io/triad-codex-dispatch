# Worktree-First Review and Auto-Review Distribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:test-driven-development` and `superpowers:writing-skills`.
> Do not commit, push, install, dispatch providers, or release; those operations
> retain separate owner approval.

**Goal:** Replace packet-first triad review with direct existing-worktree review
and make the human-run distribution bootstrap route exact provider launchers to
Codex Auto-review.

**Architecture:** The leader sends every reviewer to one absolute Git worktree
with a shared scope and uses a pre/post Git state fingerprint as the consistency
guard. The installed triad profile selects `on-request + auto_review`; exact
managed launcher rules use `prompt`, so the Agent reviewer handles those calls
without a person approving each leg.

**Tech Stack:** Markdown skills and docs, POSIX shell bootstrap, embedded Python
payload renderers, Starlark exec-policy rules, pytest.

## Global Constraints

- Review the current worktree; create no source packet, snapshot, manifest,
  allowlist, or generated related-file list.
- Review scope extends from the diff to affected unchanged code, tests, config,
  build files, and governing docs.
- Credentials, authentication files, environment dumps, and provider logs are
  never review inputs.
- The user runs bootstrap from a normal terminal to modify `$CODEX_HOME`.
- The dedicated triad profile may select Auto-review; normal development
  configuration and model/reasoning settings remain unchanged.
- Commit, push, install/update, merge, provider dispatch, and release each remain
  separately authorized.

---

### Task 1: Direct-worktree skill contract

**Files:**

- Modify: `tests/test_distribution_contract.py`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `skills/triad-cross-family-review/references/fresh-codex-formal-review.md`
- Modify: `skills/triad-cross-family-review/references/reviewer-routing.md`
- Retain unused compatibility implementation for now:
  `skills/triad-cross-family-review/lib/review_snapshot.py`

**Interfaces:**

- Consumes: one absolute Git worktree and one scope selector.
- Produces: three no-edit reviews plus a stable pre/post source-state digest.

- [ ] **Step 1: Replace packet-positive contract tests with failing
      worktree-positive tests**

Add assertions equivalent to:

```python
def test_formal_review_uses_existing_worktree_without_source_packet() -> None:
    skill = _text(TRIAD_REVIEW_SKILL)
    assert "existing Git worktree" in skill
    assert "leader-generated Git status/diff" in skill
    assert "affected unchanged" in skill
    assert "pre/post" in skill and "fingerprint" in skill
    for forbidden in (
        "code-complete archived snapshot",
        "per-run external-input allowlist",
        "Mutable live-worktree source is outside formal evidence",
    ):
        assert forbidden not in skill


def test_formal_review_provider_calls_use_worktree_cwd() -> None:
    skill = _text(TRIAD_REVIEW_SKILL)
    assert '"--cwd", worktree_root' in skill
    assert '"--sandbox", "read-only"' in skill
    assert "--sealed-packet-root" not in skill
    assert "--expected-packet-sha256" not in skill
```

Delete or rewrite assertions whose desired behavior is the old mandatory packet
path. Leave wrapper compatibility tests intact because the wrapper flags remain
supported but unused by this skill.

- [ ] **Step 2: Run the focused tests and verify RED**

Run from `/Users/chaniri/codex_workspace` with the required outside-sandbox
login-shell Python:

```text
python3 -m pytest \
  workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py \
  -q
```

Expected: failures cite the old snapshot, packet, mutable-worktree prohibition,
or missing worktree-first wording.

- [ ] **Step 3: Rewrite the main skill with the smallest complete workflow**

The skill body must contain, in order:

1. owner authorization for the named review scope and provider families;
2. absolute existing-worktree resolution;
3. one scope selector: uncommitted, base/range, or commit;
4. read-only pre-review fingerprint;
5. concurrent independent Claude, Google-family, and fresh Codex dispatch;
6. one trusted leader-captured Git status/diff plus reviewer-owned direct file
   reads/searches and affected-unchanged-file tracing;
7. no-edit and no candidate execution contract;
8. post-review fingerprint equality check;
9. evidence-based consolidation and owner adjudication for surviving conflict.

Remove every instruction that makes a packet, snapshot, manifest, packet hash,
or packet-local citation a prerequisite.

- [ ] **Step 4: Rewrite the fresh Codex reference**

Use an absolute worktree prompt with this result shape:

```json
{
  "verdict": "SAFE",
  "findings": [],
  "affected_surfaces_inspected": ["path/to/consumer.py"],
  "open_questions": []
}
```

The native spawn remains fresh-context `gpt-5.6-terra` / `xhigh` with
`fork_turns="none"`, omitted `agent_type`, and a no-edit prompt. It may read Git
state and source files inside the named worktree.

- [ ] **Step 5: Simplify routing reference**

Keep model availability and leader-versus-reviewer guidance. Remove sealed
packet preflight as a formal prerequisite. Provider availability proof must not
create source packaging.

- [ ] **Step 6: Run focused tests and verify GREEN**

Expected: all direct-worktree distribution-contract tests pass; packet-context
wrapper compatibility tests remain unchanged.

---

### Task 2: Auto-review distribution profile and exact prompt rules

**Files:**

- Modify: `tests/test_bootstrap.py`
- Modify: `tests/test_distribution_contract.py`
- Modify: `scripts/bootstrap.sh`

**Interfaces:**

- Consumes: human-run `scripts/bootstrap.sh --install`.
- Produces: managed triad profile and exact absolute-launcher rules under the
  selected `$CODEX_HOME`.

- [ ] **Step 1: Write failing bootstrap expectations**

Update the default-install test to require:

```python
profile_data = tomllib.loads(profile.read_text(encoding="utf-8"))
assert profile_data["approval_policy"] == "on-request"
assert profile_data["approvals_reviewer"] == "auto_review"

rules_text = rules.read_text(encoding="utf-8")
assert 'decision = "prompt"' in rules_text
assert 'decision = "allow"' not in rules_text
assert "owner-authorized triad review" in rules_text
```

Keep negative match assertions for repository wrapper paths, `python3`,
`/usr/bin/env python3`, `bash -lc`, and `zsh -lc`.

- [ ] **Step 2: Run focused bootstrap tests and verify RED**

Expected: the current generated profile omits both approval keys and the current
rules use `allow`.

- [ ] **Step 3: Emit the dedicated Auto-review profile**

Default profile payload:

```toml
approval_policy = "on-request"
approvals_reviewer = "auto_review"
default_permissions = "triad_leader"
```

Keep `TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never` only as the existing explicit
advanced override. It changes `approval_policy` only; the generated profile still
names `approvals_reviewer = "auto_review"`, which has no work to do under
`never`.

- [ ] **Step 4: Change only the exact managed launcher rules to prompt**

Generate:

```python
prefix_rule(
    pattern = ["/absolute/managed/claude_wrapper.py"],
    decision = "prompt",
    justification = "Route this exact owner-authorized triad review through automatic approval review; review source may go only to the authenticated named provider, with credentials, authentication files, environment dumps, and unrelated paths excluded.",
)
```

Generate equivalent exact rules for Antigravity and Gemini. Do not add generic
provider, Python, shell, or directory prefixes.

- [ ] **Step 5: Verify generated rules deterministically**

Use `codex execpolicy check` in tests or focused verification to prove managed
launcher examples return `prompt` and negative forms do not match.

- [ ] **Step 6: Run focused bootstrap tests and verify GREEN**

Expected: profile, rule generation, reinstall, provenance, no-clobber, and
negative-match tests pass.

---

### Task 3: Distribution and workspace documentation

**Files:**

- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `SECURITY.md` if it currently claims promptless wrapper bypass
- Modify: `docs/status/2026-07-22-current-state.md`
- Modify: `docs/status/2026-07-22-resume-prompt.md`
- Modify: `/Users/chaniri/codex_workspace/AGENTS.md`

**Interfaces:**

- Produces: one consistent operator contract across source, installed plugin,
  and root leadership policy.

- [ ] **Step 1: Add failing documentation-contract assertions**

Require both READMEs to state:

- the installed triad profile uses Auto-review;
- exact wrapper calls go to Agent review rather than bypassing review;
- the owner runs the printed bootstrap command in a normal terminal;
- one triad-skill invocation authorizes its named provider legs;
- commit, push, install/update, merge, and release remain separate.

- [ ] **Step 2: Run documentation-contract tests and verify RED**

Expected: old “automatically allow” and inheritance wording fails.

- [ ] **Step 3: Update English and Korean operator documentation**

Remove the old claim that exact launcher rules use `allow`. Explain that no
human prompt appears because `prompt` routes to Auto-review in the dedicated
profile. Keep the human-run bootstrap boundary prominent.

- [ ] **Step 4: Update root leadership policy**

Replace the root `AGENTS.md` formal-gate packet rule with direct-worktree review,
affected-unchanged-file inspection, pre/post state fingerprinting, and an
explicit opt-in-only archive statement.

- [ ] **Step 5: Replace the paused R15 packet handoff**

State that R15 packet dispatch was cancelled before provider execution and that
the next validation target is the worktree-first implementation. Do not claim a
formal three-family result, install, commit, push, or release.

- [ ] **Step 6: Run documentation-contract tests and verify GREEN**

Expected: English, Korean, status, and policy contracts agree.

---

### Task 4: Skill pressure verification and regression suite

**Files:**

- Modify only if a pressure test finds a concrete loophole:
  `skills/triad-cross-family-review/SKILL.md`
- Record evidence in the current status document, not a source packet.

- [ ] **Step 1: Run fresh-context GREEN pressure scenarios**

Give fresh agents the owner scenario from the RED test. Success requires each
agent to choose the existing worktree, avoid packet/snapshot creation, attach one
trusted Git diff as the entry point, inspect affected unchanged files, and route exact
provider calls through Auto-review.

- [ ] **Step 2: Inspect rationalizations and close only observed loopholes**

Do not add speculative security machinery. Prefer a positive execution recipe
over a growing prohibition list.

- [ ] **Step 3: Re-run the pressure scenario**

Expected: stable worktree-first behavior with no packaging suggestion.

- [ ] **Step 4: Run required Python environment preflight**

From `/Users/chaniri/codex_workspace` outside the filesystem sandbox, record:

```text
command -v python3
python3 --version
python3 -m pytest --version
```

- [ ] **Step 5: Run focused and full tests**

```text
python3 -m pytest \
  workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py \
  workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py \
  -q

python3 -m pytest \
  workspace/triad-codex-dispatch-reliability/tests \
  -q
```

- [ ] **Step 6: Verify the diff and stop at the authorization boundary**

Run `git diff --check`, inspect both repository statuses, and report changed
files and test evidence. Do not commit, push, install/reinstall, invoke Claude
or Google providers, merge, or release.

## Skill-authoring checklist

- [x] RED pressure scenario created.
- [x] RED scenario run against the old skill.
- [x] Failure and rationalization identified.
- [ ] Existing valid skill name retained.
- [ ] YAML frontmatter remains valid and concise.
- [ ] Description remains third-person and trigger-only.
- [ ] Worktree/diff/affected-file keywords are discoverable.
- [ ] Overview states the worktree-first core principle.
- [ ] Updated guidance directly fixes the observed packet-first failure.
- [ ] Guidance uses a positive execution contract.
- [ ] Fresh-context wording checks include a no-change baseline comparison.
- [ ] One complete worktree-review example is provided.
- [ ] GREEN pressure scenario passes.
- [ ] New rationalizations are recorded if observed.
- [ ] Only observed loopholes are closed.
- [ ] Re-test converges on the intended behavior.
- [ ] A decision table is used only where reviewer routing is non-obvious.
- [ ] Quick-reference review contract is present.
- [ ] Common failure behavior is explicit.
- [ ] No narrative history is added to the skill body.
- [ ] Supporting files remain limited to reusable contracts/tools.
- [ ] Commit and push remain pending explicit owner authorization.
- [ ] Upstream contribution is not attempted in this task.
