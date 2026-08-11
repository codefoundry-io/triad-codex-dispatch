# Reviewer Context Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make both review prompt renderers apply the same explicit rule for ruled-out internal scenarios, declared untrusted boundaries, evidence-backed context challenges, and unknown context.

**Architecture:** Define one fixed renderer constant, include it once in each prompt, duplicate its prose in the skill's prompt-contract reference, and pin normalized equality with a drift test. Situation-specific review points remain leader-authored.

**Tech Stack:** Python 3.12, pytest 9, Markdown Agent Skill reference.

## Global constraints

- S-class: 20-50 production lines, zero novel-core lines, one behavioral claim.
- Do not generate review points or invoke `skill-prompt-review` in operational rounds.
- Root authors tests/SOT edits; dedicated fresh executors alone run RED and GREEN.

---

### Task 1: Author an exact normalized-contract RED test

**Files:**
- Modify: `tests/test_review_round.py`

- [ ] Define the expected normalized contract in the test:

```text
Apply the governing deployment context when judging required defenses. Do not demand validation, fallback behavior, or error handling for scenarios that the governing deployment context expressly rules out or that an evidenced framework guarantee makes impossible; trust internal code and evidenced framework guarantees, and require validation at system boundaries only. Declared untrusted inputs, including vendor stdout, run logs, and review packets, are system boundaries where validation remains in scope. Challenge a deployment-context or framework-guarantee claim when concrete review evidence contradicts it. If context required to decide current correctness is unknown, state the affected impact and required evidence in open_questions rather than guessing; any open question requires NOT-SAFE.
```

- [ ] Render one prepared-directory and one worktree prompt; assert each contains the normalized contract exactly once.
- [ ] Extract the marked context-contract section from `references/review-prompt-contract.md`, normalize whitespace, and assert exact equality with the same expected text so wrapping cannot hide drift.
- [ ] Assert the prompt still preserves leader-authored `review_points` and contains no `skill-prompt-review` instruction.

### Task 2: Obtain RED from a fresh dedicated executor

- [ ] Spawn `agent_type="triad-skill-executor"`, `fork_turns="none"`; prohibit SOT edits and providers.
- [ ] Require exact SOT provenance, login-shell Python provenance, focused failure output, unchanged source fingerprint, and cleanup.
- [ ] Admit RED only when the missing fixed contract is the failure.

### Task 3: Add the shared contract to both SOT surfaces

**Files:**
- Modify: `bin/review_round.py`
- Modify: `skills/triad-cross-family-review/references/review-prompt-contract.md`

- [ ] Add `_REVIEWER_CONTEXT_CONTRACT` with exactly the text pinned by the test.
- [ ] Include it once in `render_review_prompt()` and once in `render_worktree_review_prompt()` adjacent to the verdict/context rules.
- [ ] Remove only redundant older unknown-context sentences whose meaning is fully subsumed; preserve Minor-finding, omitted-surface, verdict-schema, and no-edit/no-execute rules.
- [ ] Add `REVIEWER_CONTEXT_CONTRACT_START` and `REVIEWER_CONTEXT_CONTRACT_END` markers around the exact prose in the reference.

### Task 4: Obtain GREEN and regression evidence

- [ ] A separate fresh executor runs the focused prompt tests, `tests/test_review_round.py`, `tests/test_distribution_contract.py`, all `tests/`, the skill validator, and `git diff --check`.
- [ ] Require exact SOT realpath and unchanged source fingerprint. Any missing proof leaves the skill `UNTESTED`.

### Task 5: Commit and run the operational gate

- [ ] Stage only renderer, reference, and tests; commit as `fix: define reviewer context boundary contract`.
- [ ] The root leader runs a fresh-ID three-family implementation review with points selected for anti-over-hardening bias, untrusted-boundary preservation, unknown-context verdict semantics, and doc/renderer drift.
- [ ] Do not attach a skill-prompt review. Reproduce every finding and restart the complete slice gate for any bounded fix.
