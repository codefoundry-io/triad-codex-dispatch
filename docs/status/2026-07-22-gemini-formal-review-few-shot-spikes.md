# Gemini FormalReview few-shot spikes

Date: 2026-07-22

## Scope

This was an advisory route-repair experiment, not a new formal review round.
Every provider call used:

- `Gemini 3.1 Pro (High)` through the Antigravity wrapper;
- the packaged `triad_formal_review_schema:FormalReview` validator;
- read-only provider sandboxing;
- immutable packet
  `_runs/reviews/20260721-triad-reliability-final-r11/packet`;
- expected packet digest
  `2c5c6cf56ed2bda30c72bfd98e4df13df7f336468a07bfc44f7fd3aa573d7304`.

The direct checkout shebang selected Python 3.14 without Pydantic 2 and failed
preflight before provider launch. The same candidate was therefore executed
with the already-proven Python 3.12 interpreter. This was an interpreter
selection issue, not an authentication or provider-sandbox failure.

## Terminal provider calls

| Call | Input focus | Seconds | Result | Prompt consequence |
|---:|---|---:|---|---|
| 1 | Manifest chain, no issue | 93.9 | Valid `SAFE`; both lists `[]` | None |
| 2 | Antigravity settings symlink defect | 35.3 | Valid `NOT-SAFE`; Major at `inputs/candidate/bin/_agy_settings.py:211` | None |
| 3 | Bootstrap usage wording | 63.1 | Valid `SAFE`; Minor at `inputs/candidate/scripts/bootstrap.sh:53` | None |
| 4 | Both independent defects | 44.9 | Valid `NOT-SAFE`; two separate findings | None |
| 5 | Original long R11 Scope A | 201.6 | Valid `NOT-SAFE`; numeric location at `inputs/candidate/bin/_pty.py:227` | None |
| 6 | Same long Scope A after ordering revision | 134.6 | Valid `SAFE`; empty envelope | None |
| 7 | Multi-finding after positive-rule revision | 56.3 | Wrapper `66`; structurally valid but hallucinated review ID | Add trusted review ID and exact-copy rule |
| 8 | Same multi-finding after identity revision | 58.9 | Valid `NOT-SAFE`; exact identity and two separate findings | Stop |

All eight vendor processes exited zero. Call 7 was correctly rejected by local
schema validation and its raw result was preserved in
`bin/_logs/antigravity/runs/20260722T005406Z-62021-7f1a6914.json` for the normal
age-floor cleanup path.

## Evidence-driven prompt revisions

1. Add complete SAFE and NOT-SAFE envelopes, including empty arrays for a
   no-issue result.
2. Remove an implementation-only Pydantic description, put runtime input
   before the contract, and add a final JSON anchor.
3. Fence runtime input and express the valid location and envelope shapes as
   positive rules.
4. Inject the exact trusted review ID beside the packet root and digest, then
   require both identity values to be copied exactly.

The initial plan interpreted “about five” as a five-call cap. Execution used
eight explicit terminal calls because independent reviews triggered two
revisions and call 7 exposed the final identity defect. There were four prompt
revisions, no hidden retry within an invocation, and no further change after
call 8 passed.

## Artifacts

The ignored spike directory is
`_runs/spikes/20260722-gemini-formal-fewshot/`. The final assembled prompt is
4,334 bytes with SHA-256
`df63f8e53cd20bd966e5e84e052a287877e0a17d894c15bd01bee82b19480405`.
