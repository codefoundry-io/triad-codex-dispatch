# Gemini FormalReview prompt review and verification

Date: 2026-07-22

## Final prompt review

Prompt changes were reviewed because authored prompt bytes changed. Four
independent fresh-context reviews drove or checked each material revision:

| Review | Result | Action |
|---|---|---|
| R1 | Failed C3, C5, C10, C14, G3 | Removed loader prose; reordered runtime input and contract; added closing anchor |
| R2 | Failed C4, C10, C16 | Added a runtime-data fence and positive output rules |
| R3 | Passed all 21 applicable criteria | No change |
| R4 | Passed all 21 applicable criteria on the final identity-bound assembled prompt | No change |

The final mechanical lint found no candidates. R4 classified eight criteria as
not applicable and reported no fixes or recommended additions. The prompt was
then frozen; no speculative text was added.

## TDD evidence

- Initial few-shot RED: `1 failed`; GREEN: `3 passed`.
- Ordering and schema-leanness RED: `2 failed`; GREEN: `5 passed`.
- Positive framing and runtime fence RED: `2 failed`; GREEN: `3 passed`.
- Trusted identity RED: `2 failed`; GREEN: `4 passed`.
- Final relevant files:
  `tests/test_formal_review_schema.py` and
  `tests/test_antigravity_packet_context.py`: `134 passed`.

## Deterministic verification

- macOS Python 3.12 full suite:
  `595 passed, 6 subtests passed in 121.95s`.
- Standalone log-cleanup suite: `28/28 passed`.
- macOS Bash syntax, Python compilation, plugin validation, skill lint, and
  `git diff --check`: passed.
- Ubuntu 24.04 pinned image
  `sha256:e9925f0b3f7832f47948760b8d05fec045469b3c00b3ddcb2500e9d30c28f09f`:
  `594 passed, 1 skipped, 6 subtests passed in 76.73s`.
- Ubuntu Bash syntax and Python compilation: passed.

The one Ubuntu skip is the existing case-insensitive APFS-only bootstrap case;
the path variant is a distinct directory on the container's case-sensitive
filesystem.

## Gate status

These calls demonstrate that the repaired Google route can return valid
no-issue, single-finding, multi-finding, and long-context `FormalReview`
envelopes. They do not constitute the required independent two-Google plus
two-Codex formal review round.

The authoritative R11 gate therefore remains
`REVIEW_UNAVAILABLE / INVALID / NOT-SAFE`. No plugin installation, commit,
push, or release is authorized by this advisory experiment alone.
