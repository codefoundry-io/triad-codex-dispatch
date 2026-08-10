# Out-of-Packet Surface Convention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve coverage when a reviewer suspects a relevant surface omitted from the prepared directory without allowing uninspected evidence to masquerade as a finding.

**Architecture:** Keep one prepared-directory root and the existing schema. Teach each rendered reviewer to place the suspected normalized worktree-relative path and required check in a blocking open question, then document the leader's existing reproduce-expand-rerun response.

**Tech Stack:** Python prompt renderer, Markdown skill contract, pytest 9, Python 3.12.

## Global Constraints

- Preserve the prepared directory as the only reviewer filesystem input.
- Do not add a second root, prefix protocol, path membership validator, or canonical-worktree access for reviewer legs.
- Do not claim that an omitted surface was inspected.
- Production net delta: approximately 5-10 prompt lines; novel algorithmic core: 0 lines; behavioral claims: 1; S-class.
- Work from `/Users/chaniri/codex_workspace`; run direct Python through `/bin/zsh -lic` with the nested test path.

---

### Task 1: Emit the omitted-surface reporting convention

**Files:**
- Modify: `tests/test_review_round.py`
- Modify: `bin/review_round.py`
- Modify: `skills/triad-cross-family-review/references/review-prompt-contract.md`

**Interfaces:**
- Consumes: `render_review_prompt(ReviewBrief) -> str`, `open_questions`, and the existing fresh-round convergence flow.
- Produces: a rendered instruction that routes a suspected omitted surface to `open_questions` and `NOT-SAFE` without a false citation.

- [ ] **Step 1: Write the failing rendered-prompt test**

Add this test after the suggestion/context test:

```python
def test_rendered_prompt_reports_omitted_surfaces_as_open_questions(prepared):
    brief = ReviewBrief(
        review_id="omitted-surface-r1",
        review_kind="pre-merge",
        family="codex",
        objective="Trace affected callers.",
        prepared_dir=prepared,
        content_digest=_prepared_digest(prepared),
        criteria=("correctness",),
        approved_boundary=("src/source.py",),
    )

    prompt = render_review_prompt(brief)

    assert "If a potentially relevant surface is absent from the prepared directory" in prompt
    assert "do not cite it as a finding or list it in affected_surfaces_inspected" in prompt
    assert "suspected normalized worktree-relative path and required check in open_questions" in prompt
    assert "which requires NOT-SAFE" in prompt
```

The production change that makes this test pass is the emitted fallback path for
coverage gaps; removing it recreates the silent-drop-or-false-citation choice.

- [ ] **Step 2: Run the selector and verify RED**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_rendered_prompt_reports_omitted_surfaces_as_open_questions'
```

Expected: FAIL on the first missing prompt clause.

- [ ] **Step 3: Add the minimal rendered instruction**

After the suggestion/context convention in `render_review_prompt`, append:

```python
        "If a potentially relevant surface is absent from the prepared directory, do not cite it "
        "as a finding or list it in affected_surfaces_inspected. Put its suspected normalized "
        "worktree-relative path and required check in open_questions, which requires NOT-SAFE. "
```

- [ ] **Step 4: Add the matching reference and leader response**

Add a paragraph to `review-prompt-contract.md` that repeats the leg instruction
and states that the leader reproduces the suspicion against the canonical
worktree; if relevant, the leader prepares a new complete directory containing
the surface and restarts every required family under a fresh review ID.

- [ ] **Step 5: Run focused verification and verify GREEN**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_rendered_prompt_reports_omitted_surfaces_as_open_questions workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_rendered_prompt_distinguishes_suggestions_from_unknown_context workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_rendered_prompt_binds_focused_round_once'
```

Expected: all three tests PASS.

- [ ] **Step 6: Run the reference/distribution regression set**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py workspace/triad-codex-dispatch-reliability/tests/test_review_round.py'
```

Expected: both modules PASS.

- [ ] **Step 7: Check patch hygiene and commit only this slice**

Run `git diff --check`, stage the three listed files, and commit:

```bash
git add tests/test_review_round.py bin/review_round.py skills/triad-cross-family-review/references/review-prompt-contract.md
git commit -m "fix: preserve omitted review surfaces"
```
