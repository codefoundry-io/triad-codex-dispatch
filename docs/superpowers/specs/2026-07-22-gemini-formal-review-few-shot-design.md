# Gemini FormalReview Few-Shot Design

## Goal

Reduce avoidable Gemini `FormalReview` schema failures without changing the
schema, accepting malformed results, or adding an automatic normalizer.

## Design

The canonical `FormalReview` prompt will retain its complete JSON Schema and add
two compact examples:

1. A no-issue result that still emits the complete envelope with `verdict` set
   to `SAFE` and both `findings` and `open_questions` set to empty arrays.
2. A finding result that emits the complete envelope and one finding with all
   five required fields.

The prompt will state the valid shape positively: one complete envelope, one
manifest-listed path plus a positive decimal line per location, separate
findings for separate paths, and line numbers rather than symbols. Required
strings must be non-empty; absence is represented by empty arrays in the two
list fields.

## Bounded experiment

Run roughly five evidence-driven iterations with exact `Gemini 3.1 Pro (High)`.
Each terminal call must be locally validated by the packaged `FormalReview`
model. Change the prompt only when a raw result or independent prompt review
exposes a reproducible defect; allow a separate replay after each such change.
Stop after the final changed prompt produces a valid result. Do not launch a
full four-leg formal review as part of this experiment.

## Verification

- TDD regression for the complete envelope, empty-array no-issue result,
  finding example, observed-invalid-shape warnings, and final `JSON:` cue.
- Focused and full deterministic tests.
- Fresh-eye prompt review after each material prompt revision, including the
  final fully assembled prompt, because prompt bytes change.
- An experiment record containing each attempt, outcome, and any resulting
  prompt delta.
