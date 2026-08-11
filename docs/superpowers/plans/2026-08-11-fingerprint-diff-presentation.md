# Fingerprint Diff Presentation Pinning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pin the tested staged and unstaged Git diff presentation axes and prevent textconv execution during worktree fingerprinting.

**Architecture:** Keep the existing four fingerprint records. Add one immutable argument tuple for both `git diff` arms so the tested presentation choices are selected by product code rather than the corresponding repository configuration. The root leader authors tests and production edits; fresh `triad-skill-executor` instances exclusively execute RED and GREEN.

**Tech Stack:** Python 3.12 standard library, Git CLI, pytest 9.

## Global constraints

- S-class: 15-30 production lines, zero novel-core lines, one behavioral claim.
- Canonical SOT: `workspace/triad-codex-dispatch-reliability`; do not test a copy or installed cache.
- The root leader must not execute Python tests or behavior fixtures.
- No `skill-prompt-review` and no provider dispatch by the test agent.

## Known residuals and disposition

This slice does not claim independence from every Git diff configuration key.
The [dedicated residual probe](../../status/2026-08-11-fingerprint-diff-residuals.md)
reproduced `diff.orderFile`, `diff.suppressBlankEmpty`, and a `.gitattributes`
`diff=<driver>` selection combined with `diff.<driver>.xfuncname` changing patch
bytes. They change ordering or presentation, not whether a tracked mutation is
represented. When one of these settings affects rendered bytes and changes
between capture and verification, the fingerprint fails closed with a mismatch;
an invalid setting that makes `git diff` fail stops fingerprinting instead. The
owner selected the same bounded patch-diff model used by the vetted
Claude-hosted TRIAD skill and rejected a canonical-index/full-file hash redesign
as over-engineering. These residual false-mismatch paths remain disclosed rather
than expanding this slice.

---

### Task 1: Author a configuration-sensitive RED test

**Files:**
- Modify: `tests/test_review_round.py`

- [ ] Add a parametrized staged/unstaged fixture that commits a multi-line file, changes two separated lines, and proves its raw `git diff` bytes change when `diff.context` and `diff.noprefix` are changed.
- [ ] In the same test, assert `_worktree_fingerprint()` stays equal across the two configurations. This assertion must fail on the pre-change source while the raw-diff precondition passes.
- [ ] Add an executable Python textconv fixture selected through `.gitattributes`; it writes a sentinel before echoing the candidate file. Assert fingerprinting does not create the sentinel.
- [ ] Include an argument-contract assertion for both diff arms covering exactly:

```python
(
    "--binary",
    "--full-index",
    "--no-color",
    "--no-ext-diff",
    "--unified=3",
    "--inter-hunk-context=0",
    "--diff-algorithm=myers",
    "--no-indent-heuristic",
    "--no-renames",
    "--no-textconv",
    "--src-prefix=a/",
    "--dst-prefix=b/",
)
```

### Task 2: Obtain RED from a fresh dedicated executor

- [ ] Spawn `agent_type="triad-skill-executor"`, `fork_turns="none"` with a behavior-only, no-edit brief.
- [ ] Require the agent to record the resolved SOT realpath, `HEAD`, `git status --short`, and a source fingerprint before and after.
- [ ] From `/Users/chaniri/codex_workspace` through `/bin/zsh -lic`, require it to record `command -v python3`, `python3 --version`, and `python3 -m pytest --version`, then run only the new focused tests.
- [ ] Admit RED only if the raw-diff sensitivity precondition passes and the expected fingerprint/textconv assertion fails. Otherwise repair the test source before any production edit.

### Task 3: Pin both diff arms

**Files:**
- Modify: `bin/review_round.py`

- [ ] Add `_FINGERPRINT_DIFF_ARGS` with the exact tuple above.
- [ ] Render the staged arm as `_git(root, "diff", "--cached", *_FINGERPRINT_DIFF_ARGS)` and the unstaged arm as `_git(root, "diff", *_FINGERPRINT_DIFF_ARGS)`.
- [ ] Do not change status, untracked, index-flag, prompt, or provider behavior in this slice.

### Task 4: Obtain GREEN and regression evidence

- [ ] Spawn a separate fresh `triad-skill-executor` with the same provenance/no-edit contract.
- [ ] Require the focused tests, then `tests/test_review_round.py`, then the complete `tests/` suite and `git diff --check`.
- [ ] Require an unchanged post-run source fingerprint and exact disposable-fixture cleanup evidence. Any missing element leaves the slice `UNTESTED`.

### Task 5: Commit and run the operational gate

- [ ] Stage only `bin/review_round.py` and `tests/test_review_round.py`; commit as `fix: pin review fingerprint diff presentation`.
- [ ] The root leader runs a fresh-ID Claude/Google/fresh-Codex implementation review over this slice only, with review points selected for the explicitly pinned Git presentation axes, executable textconv prevention, disclosed residuals, and cross-platform Git flag compatibility.
- [ ] Reproduce every finding against the canonical worktree. A bounded defect restarts RED/GREEN and all three review legs; an out-of-scope proposal returns to the owner.
