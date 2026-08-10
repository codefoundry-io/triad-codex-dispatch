# Benchmark Provenance Caveat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Qualify the checked-in 4/4 benchmark aggregate with its post-hoc ground-truth amendment while preserving the independently valid 3/3 preregistered recall and runtime-efficiency evidence.

**Architecture:** Add one machine-readable provenance field to the captured runtime artifact, assert it in the existing benchmark behavior test, and repeat the same qualification in the two human-facing claims. Do not recompute or replace any captured metric.

**Tech Stack:** JSON evidence, Markdown, pytest 9, Python 3.12.

## Global Constraints

- Preserve `LegVerdict`, review routing, provider permissions, and runtime behavior.
- Do not change `cases.json`, rerun providers, or create replacement fixtures.
- Keep calls per round, artifact counts, and the checked-in aggregate values unchanged.
- Production net delta: 0 lines; novel algorithmic core: 0 lines; behavioral claims: 1; S-class.
- Work from `/Users/chaniri/codex_workspace`; run direct Python through `/bin/zsh -lic` with the nested test path.

---

### Task 1: Record the amended-ground-truth caveat

**Files:**
- Modify: `tests/test_review_policy_benchmark.py`
- Modify: `benchmarks/review-policy/focused-convergent-runtime.json`
- Modify: `CHANGELOG.md`
- Modify: `docs/status/2026-08-05-focused-convergent-runtime-benchmark.md`

**Interfaces:**
- Consumes: the captured `focused-convergent-runtime.json` object and existing benchmark aggregation.
- Produces: top-level string field `methodology_caveat`; no aggregate schema or calculation change.

- [ ] **Step 1: Write the failing machine-evidence assertion**

Add these assertions immediately after loading `focused` in
`test_checked_in_runtime_benchmark_proves_two_round_convergence`:

```python
    assert focused["methodology_caveat"] == (
        "LOCAL-2 was added to expected_finding_ids after reviewer output. "
        "The preregistered defect set was detected 3/3; the checked-in 4/4 "
        "and zero-false-finding aggregate uses amended ground truth. "
        "Calls-per-round and batch-artifact counts are unaffected."
    )
```

- [ ] **Step 2: Run the selector and verify RED**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_review_policy_benchmark.py::test_checked_in_runtime_benchmark_proves_two_round_convergence'
```

Expected: FAIL with `KeyError: 'methodology_caveat'`.

- [ ] **Step 3: Add the exact machine-readable caveat**

Add this top-level field after `batch_artifacts` in
`focused-convergent-runtime.json`:

```json
"methodology_caveat": "LOCAL-2 was added to expected_finding_ids after reviewer output. The preregistered defect set was detected 3/3; the checked-in 4/4 and zero-false-finding aggregate uses amended ground truth. Calls-per-round and batch-artifact counts are unaffected."
```

- [ ] **Step 4: Qualify both human-facing claims**

Change the 0.2.533 CHANGELOG benchmark bullet to state that the preregistered
set was detected 3/3, `LOCAL-2` was added to expected IDs after reviewer output,
and therefore the checked-in 4/4 and zero-false-finding aggregate is post-hoc.
Retain the six calls, 3/3 confirmation `SAFE`, zero admitted mutations, and
87.5% call-reduction claims.

In the benchmark status document, keep the comparison table values but add a
paragraph directly below the table with the same distinction and explicitly
state that the call and artifact measurements are unaffected.

- [ ] **Step 5: Run focused verification and verify GREEN**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_review_policy_benchmark.py'
```

Expected: all benchmark-policy tests PASS.

- [ ] **Step 6: Check patch hygiene and commit only this slice**

Run from the repository worktree:

```bash
git diff --check
git status --short
```

Stage the four listed files and commit:

```bash
git add tests/test_review_policy_benchmark.py benchmarks/review-policy/focused-convergent-runtime.json CHANGELOG.md docs/status/2026-08-05-focused-convergent-runtime-benchmark.md
git commit -m "docs: qualify review benchmark ground truth"
```
