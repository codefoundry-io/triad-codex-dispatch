# TRIAD Maintenance Decisions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the current digest, benchmark evidence, and focused-review skill while making the retained evidence inventory and maintenance rationale exact and reproducible.

**Architecture:** Add one test-owned literal inventory for the 23 tracked benchmark evidence files and one English status record for the three owner decisions. Do not change runtime code, wrappers, the skill, digest values, benchmark bytes, packaging behavior, or the six pre-existing dirty files.

**Tech Stack:** Python 3.12, pytest, Git archive verification, Markdown.

## Global Constraints

- Do not modify `bin/review_round.py`, any wrapper, `skills/**`, or `benchmarks/review-policy/**`.
- Preserve the six pre-existing dirty-worktree files byte-for-byte.
- Do not commit, push, merge, install, or publish without separate owner approval.
- Run direct Python and pytest commands through `/bin/zsh -lic` from `/Users/chaniri/codex_workspace`.
- The formal-plan evidence is review ID `20260808-triad-maintenance-items-formal-plan-r1`, digest `667582cc4c7a77d0f30ff98abed7376cbc9c0fc4417319137f76427ac87e8c7c`, status `VALID / SAFE`.

---

### Task 1: Exact benchmark evidence inventory

**Files:**
- Modify: `tests/test_review_policy_benchmark.py`

**Interfaces:**
- Consumes: the tracked files below `benchmarks/review-policy`.
- Produces: a package-test assertion that rejects any missing or unexpected benchmark evidence member.

- [ ] **Step 1: Add the literal inventory test**

Add an `EXPECTED_BENCHMARK_FILES` literal containing the exact 23 paths relative to
`benchmarks/review-policy`, and add:

```python
def test_benchmark_evidence_filesystem_inventory_is_exact() -> None:
    actual = {
        path.relative_to(FIXTURES).as_posix()
        for path in FIXTURES.rglob("*")
        if path.is_file()
    }
    assert actual == EXPECTED_BENCHMARK_FILES
```

- [ ] **Step 2: Prove the test detects an omitted evidence member**

Create a disposable copy of the repository that excludes
`benchmarks/review-policy/focused-convergent-skill.json`, then run only the new test against that
copy.

Run from the workspace root through `/bin/zsh -lic`.

Expected: FAIL showing `focused-convergent-skill.json` missing from the actual inventory.

- [ ] **Step 3: Verify the canonical inventory passes**

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_policy_benchmark.py::test_benchmark_evidence_filesystem_inventory_is_exact -q'
```

Expected: `1 passed`.

- [ ] **Step 4: Verify the complete benchmark test module**

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_policy_benchmark.py -q'
```

Expected: all tests pass.

### Task 2: Durable maintenance decision record

**Files:**
- Create: `docs/status/2026-08-08-triad-maintenance-decisions.md`

**Interfaces:**
- Consumes: formal-plan R1 adjudication and checked-in benchmark evidence.
- Produces: the durable human-readable decision and measurement provenance; no runtime consumer.

- [ ] **Step 1: Record Item 1 exactly**

State that `_prepared_digest` remains unchanged because Git blob hashing still needs path/tree
framing and macOS bsdtar 3.5.3 rejects `--sort=name`. State that the digest binds regular-file
relative paths and contents only; mode bits and empty directories are out of scope within the
leader-owned capture/verify bracket.

- [ ] **Step 2: Record Item 2 and measurement provenance**

State that five files are direct pytest inputs and the remaining 18 retain planted-defect,
correction, runtime, and pressure-test evidence. Record:

```text
commit: 8b2f66edae8af6fc9bd32cdf35cf4cbb3006879c
git ls-files benchmarks/review-policy | wc -l -> 23
git ls-files benchmarks/review-policy | xargs wc -c | tail -1 -> 10991 total
git archive --format=tar HEAD | wc -c -> 1515520
```

Explain that clean-HEAD distribution verification runs the complete extracted `tests` tree, which
loads the retained benchmark inputs.

- [ ] **Step 3: Record Item 3 without changing the skill**

Record the R46 values `24 planned calls`, `465 patch artifacts`, `93 impact paths`, and `186,634
prompt bytes`; contrast them with focused-round prompt sizes `4,665` and `4,743`. State that these
measurements establish no universal safe file-count or byte ceiling. A concrete oversized closure
returns to the owner through the skill's existing authorize-and-bound step; no ceiling or skill edit
is added.

- [ ] **Step 4: Self-review the decision record**

Check that it contains no placeholder markers, unsupported claim that all 23 files are direct test
inputs, or wording that modifies the skill/runtime contract.

### Task 3: Regression verification

**Files:**
- Verify only; no additional source changes.

**Interfaces:**
- Consumes: Tasks 1 and 2.
- Produces: current-source and dirty-boundary evidence before the pre-merge review.

- [ ] **Step 1: Run the focused tests**

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_policy_benchmark.py workspace/triad-codex-dispatch-reliability/tests/test_review_round.py -q'
```

- [ ] **Step 2: Run the full suite**

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests -q'
```

- [ ] **Step 3: Verify scope**

Confirm that the only new task changes are this plan, the benchmark inventory test, and the status
record, while the six pre-existing dirty files retain their pre-task bytes.

- [ ] **Step 4: Run the unchanged skill's three-family pre-merge gate**

Prepare a fresh complete focused directory, use the installed `triad-cross-family-review` skill as
written, and require admitted Claude, Google, and fresh Codex `SAFE` verdicts for one digest.
