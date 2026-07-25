# Shared Review Prompt Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:test-driven-development` and `superpowers:writing-skills`.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one provider-neutral review prompt contract with explicit
external-send gating and mode-specific output profiles.

**Architecture:** Provider skills remain transport adapters. The
cross-family skill owns a shared review-prompt reference consumed by Claude,
Google-family, and fresh Codex legs. Provider metadata requires explicit
invocation, while implicit cross-family activation may prepare but not send a
review without matching owner authorization.

**Tech Stack:** Markdown Agent Skills, Codex plugin metadata, pytest
distribution-contract tests.

## Global Constraints

- Do not change wrapper, selector, fallback, extraction, repair, or runtime
  identity behavior.
- Keep formal review evidence, citation, verdict, digest, and invalidation
  semantics unchanged.
- Keep source bytes out of review prompts.
- Keep documentation in English.
- Run direct `python3` and pytest commands from the workspace-root login shell.
- Complete the owner-requested Google-family and fresh-Codex review gate before
  commit, push, install, or release.

---

### Task 1: Pin the missing prompt and invocation contracts

**Files:**

- Modify: `tests/test_distribution_contract.py`

**Interfaces:**

- Consumes: shipped skill and plugin metadata.
- Produces: regressions for explicit provider invocation, shared prompt fields,
  result profiles, and formal fresh-Codex rendering.

- [ ] **Step 1: Add failing distribution-contract tests**

Add tests requiring provider `allow_implicit_invocation: false`, a
`review-prompt-contract.md` reference, the `consult`, `advisory-review`, and
`formal-gate` profiles, provider links to that contract, preparation-only
implicit cross-family activation, and formal-only fresh-Codex rendering.

- [ ] **Step 2: Run the focused tests and verify RED**

Run the new tests from the workspace-root login shell. Expected failures are
missing shared reference, implicit provider activation, broad default prompts,
and the mixed-mode fresh-Codex template.

### Task 2: Implement the shared review prompt contract

**Files:**

- Create:
  `skills/triad-cross-family-review/references/review-prompt-contract.md`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify:
  `skills/triad-cross-family-review/references/fresh-codex-formal-review.md`
- Modify: `skills/triad-claude-dispatch/SKILL.md`
- Modify: `skills/triad-antigravity-dispatch/SKILL.md`
- Modify: `skills/triad-gemini-dispatch/SKILL.md`
- Modify: `skills/*/agents/openai.yaml`
- Modify: `.codex-plugin/plugin.json`

**Interfaces:**

- Consumes: leader-controlled authorization, scope, objective, perspective,
  review mode, boundary, and digest values.
- Produces: one ordered review envelope and one exact result profile.

- [ ] **Step 1: Add the minimum shared reference**

Document the envelope fields, inspection/evidence contract, three result
profiles, and final anchored request. Keep the reference one level below the
owning skill and below 100 lines when practical.

- [ ] **Step 2: Link every review route**

Require Claude, Antigravity, Gemini, and fresh Codex review prompts to render
the shared contract. Preserve every existing transport and route rule.

- [ ] **Step 3: Tighten invocation metadata**

Set provider dispatch skills to explicit invocation. Retain implicit
cross-family discovery with a preparation-only authorization gate. Replace
broad opinion prompts with prompts that name objective, approved data,
exclusions, and result profile.

- [ ] **Step 4: Run focused GREEN**

Run the Task 1 tests and require zero failures.

### Task 3: Package and verify the release candidate

**Files:**

- Modify: `.codex-plugin/plugin.json`
- Modify: `CHANGELOG.md`
- Modify: version-sensitive tests when required.

**Interfaces:**

- Consumes: verified final skill and prompt bytes.
- Produces: the next patch release candidate and reviewable release notes.

- [ ] **Step 1: Bump the patch release**

Advance the plugin version from `0.2.530` to `0.2.531` and add a concise
changelog entry limited to the shared prompt contract and explicit dispatch
activation.

- [ ] **Step 2: Run focused and full verification**

Run prompt lint, the focused distribution tests, the complete pytest suite,
`bash -n scripts/bootstrap.sh`, and Git diff checks.

- [ ] **Step 3: Run behavior and independent review gates**

Re-run the RED scenario with the finished skill and require determinate prompt
and result fields. Run two independent owner-authorized Google-family deep
reviews and one fresh-Codex review over the approved review directory. Verify
the pre/post digest and adjudicate every finding against the canonical
worktree.

- [ ] **Step 4: Publish only on a clean pass**

After all required temporary review legs pass, commit, push, publish the release
using the repository's established release path, install it, and prove
fresh-session skill exposure.
