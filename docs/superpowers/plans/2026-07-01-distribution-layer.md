# Distribution Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the Codex-led triad dispatch repo for team install/update with a Codex plugin, repo marketplace, bootstrap checks, and migration docs.

**Architecture:** The repo root is the plugin source and contains `.codex-plugin/plugin.json`; its manifest points at the existing `.agents/skills/` tree and leaves named repair agents out of manifest fields unless Spike D proves Codex supports them. The bootstrap script owns environment checks and the fallback personal-scope repair-agent install path.

**Tech Stack:** Codex CLI plugin marketplace, POSIX shell, Python pytest for hermetic bootstrap checks, Markdown docs.

---

### Task 1: Spike D

**Files:**
- Create: `.codex-plugin/plugin.json`
- Create: `.agents/plugins/marketplace.json`
- Modify: `docs/specs/2026-07-01-codex-led-triad-dispatch-design.md`

- [ ] Create the root plugin manifest with `skills: "./.agents/skills/"`.
- [ ] Create a repo marketplace entry pointing `source.path` at `"."`.
- [ ] Run `codex plugin marketplace add . --json` and `codex plugin add triad-codex-dispatch@<marketplace> --json`.
- [ ] Attempt a real fresh Codex named-agent spawn for `claude-wrapper-repair`; if unavailable, record the fallback decision.
- [ ] Confirm plugin-shipped skills install by inspecting `codex plugin list --available --json` and installed cache contents.

### Task 2: Bootstrap

**Files:**
- Create: `scripts/bootstrap.sh`
- Create: `tests/test_bootstrap.py`

- [ ] Write failing tests for `--check` success, missing binaries, launcher install, and personal repair-agent install.
- [ ] Implement `scripts/bootstrap.sh --check` with override env vars for hermetic tests.
- [ ] Run the bootstrap tests and then the full pytest suite.

### Task 3: Migration Docs

**Files:**
- Create: `migration/COMPANY-SETUP.md`
- Create: `migration/COMPANY-SETUP.ko.md`
- Create: `migration/AGENTS.recommended.md`

- [ ] Document marketplace install/update, bootstrap check, trust, auth, egress, and locked-fleet `requirements.toml`.
- [ ] Flag owner decisions instead of choosing internal git URL, classifier import policy, or codex wrapper retention.
- [ ] Keep Korean and English setup docs behaviorally aligned.

### Task 4: Verification

**Files:**
- Modify: no production files unless failures reveal a distribution bug.

- [ ] Validate plugin manifest shape against official Codex manual and CLI help.
- [ ] Run `scripts/bootstrap.sh --check` where local auth/tooling permits.
- [ ] Run `python3 -m pytest tests/`.
- [ ] Commit the branch if verification is clean enough for review.
