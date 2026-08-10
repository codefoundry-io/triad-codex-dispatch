# Review Suggestion and Context Convention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let reviewers carry genuinely non-blocking hardening suggestions as `Minor` findings while ensuring missing context needed for current correctness remains an explicit `NOT-SAFE` question.

**Architecture:** Preserve the current strict binary schema and add one meaning convention to both the reference contract and the actual rendered provider prompt. Protect the emitted prompt with one behavior-level regression test.

**Tech Stack:** Python prompt renderer, Markdown skill contract, pytest 9, Python 3.12.

## Global Constraints

- Do not add `context_known`, `Suggestion`, `HARDENING-SUGGESTION`, or another verdict.
- Do not change schema validation, provider routing, permissions, or tool availability.
- Missing context needed to decide current correctness must remain blocking.
- Production net delta: approximately 8-15 prompt lines; novel algorithmic core: 0 lines; behavioral claims: 1; S-class.
- Work from `/Users/chaniri/codex_workspace`; run direct Python through `/bin/zsh -lic` with the nested test path.

---

### Task 1: Emit the suggestion-versus-uncertainty convention

**Files:**
- Modify: `tests/test_review_round.py`
- Modify: `bin/review_round.py`
- Modify: `skills/triad-cross-family-review/references/review-prompt-contract.md`

**Interfaces:**
- Consumes: `render_review_prompt(ReviewBrief) -> str` and the unchanged `LegVerdict` schema.
- Produces: a rendered instruction that distinguishes non-blocking `Minor` suggestions from blocking `open_questions`.

- [ ] **Step 1: Write the failing rendered-prompt test**

Add this test after `test_rendered_prompt_binds_focused_round_once`:

```python
def test_rendered_prompt_distinguishes_suggestions_from_unknown_context(prepared):
    brief = ReviewBrief(
        review_id="suggestion-r1",
        review_kind="pre-merge",
        family="claude",
        objective="Check current deployment correctness.",
        prepared_dir=prepared,
        content_digest=_prepared_digest(prepared),
        criteria=("correctness",),
        approved_boundary=("src/source.py",),
    )

    prompt = render_review_prompt(brief)

    assert "A Minor finding may carry a non-blocking hardening suggestion only when" in prompt
    assert "packet evidence establishes current correctness and rules out its scenario" in prompt
    assert "Missing deployment or operational context needed to decide current correctness" in prompt
    assert "Never suppress genuine uncertainty to produce SAFE" in prompt
```

The production change that makes this test pass is emission of the approved
reviewer convention; deleting any operative clause makes the provider prompt
ambiguous again.

- [ ] **Step 2: Run the selector and verify RED**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_rendered_prompt_distinguishes_suggestions_from_unknown_context'
```

Expected: FAIL on the first missing prompt clause.

- [ ] **Step 3: Add the minimal rendered instruction**

After the existing SAFE/NOT-SAFE sentences in `render_review_prompt`, append:

```python
        "A Minor finding may carry a non-blocking hardening suggestion only when packet evidence "
        "establishes current correctness and rules out its scenario for this decision; state why it "
        "is non-blocking in trigger and evidence. Missing deployment or operational context needed "
        "to decide current correctness belongs in open_questions and therefore requires NOT-SAFE. "
        "Never suppress genuine uncertainty to produce SAFE. "
```

Keep the existing final design-change instruction after these sentences.

- [ ] **Step 4: Add the matching reference convention**

After the SAFE/NOT-SAFE rules in `review-prompt-contract.md`, add one paragraph
with the same four requirements: current correctness established, scenario
ruled out, non-blocking reason stated in trigger/evidence, and missing required
context carried in `open_questions` as `NOT-SAFE` without suppression.

- [ ] **Step 5: Run focused verification and verify GREEN**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_rendered_prompt_distinguishes_suggestions_from_unknown_context workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_rendered_prompt_binds_focused_round_once'
```

Expected: both tests PASS.

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
git commit -m "fix: define nonblocking review suggestions"
```
