# Gemini FormalReview Few-Shot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add compact schema-conformant few-shot guidance and validate it through bounded Gemini calls and fresh-eye review.

**Architecture:** Keep the existing packaged Pydantic schema and validation path unchanged. Strengthen only the canonical prompt text, then treat every real provider response as data for the next bounded iteration.

**Tech Stack:** Python 3.12, Pydantic 2, pytest, `antigravity_wrapper.py`, exact `Gemini 3.1 Pro (High)`.

## Global Constraints

- Do not normalize or accept schema-invalid formal results.
- Do not add a provider retry inside one sealed formal invocation.
- Do not run a full four-leg formal review in this task.
- Make no speculative delta after the final assembled prompt produces a valid result.
- Do not commit, push, or install while the existing formal gate remains unavailable.

---

### Task 1: Prompt contract regression

**Files:**
- Modify: `tests/test_formal_review_schema.py`
- Modify: `bin/_common.py`

**Interfaces:**
- Consumes: `_common.schema_block_for_prompt(cls) -> str`
- Produces: the existing complete `FormalReview` schema block plus two examples and explicit no-issue/location rules

- [x] Add a focused test asserting the no-issue full envelope, finding full envelope, positive location rules, non-empty required strings, and final `JSON:` cue.
- [x] Run the focused test and confirm RED because the examples are absent.
- [x] Add the minimum prompt text to `schema_block_for_prompt`.
- [x] Run the focused tests and confirm GREEN.

### Task 2: Bounded Gemini iterations

**Files:**
- Modify when evidence requires it: `bin/_common.py`
- Modify first when evidence requires a prompt delta: `tests/test_formal_review_schema.py`
- Create: `docs/status/2026-07-22-gemini-formal-review-few-shot-spikes.md`

**Interfaces:**
- Consumes: immutable packet root, packet digest, packaged `FormalReview` validator
- Produces: bounded terminal attempt records with raw result classification and prompt delta

- [x] Run exact Gemini attempt 1 against the no-issue case and validate the full envelope.
- [x] Exercise finding, multi-finding, and original long-scope prompts; add a new failing regression before every evidence-backed prompt delta.
- [x] Stop after the final identity-bound prompt produces a schema-valid result.
- [x] Record every attempt and whether it changed the prompt.

Execution note: the original draft capped provider calls at five. Four prompt
revisions required eight explicit terminal advisory calls because the final
fresh-eye revisions each needed a replay and one replay exposed an exact review
identity defect. No provider call was retried inside a sealed invocation.

### Task 3: Final prompt review and verification

**Files:**
- Create: `docs/status/2026-07-22-gemini-formal-review-few-shot-review.md`

**Interfaces:**
- Consumes: final authored prompt, common/Google/AI-authorship review criteria, mechanical lint output
- Produces: fresh-eye criterion report and deterministic verification evidence

- [x] Run focused prompt tests and the complete test suite on macOS Python 3.12.
- [x] Run the same complete suite in the pinned Ubuntu 24.04 image.
- [x] Run a fresh-context prompt reviewer read-only against the final prompt and criteria.
- [x] Record the result without changing the existing R11 formal-gate verdict.
