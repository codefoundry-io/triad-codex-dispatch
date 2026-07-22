# Triad reliability post-R11 gate status

Date: 2026-07-21

## Outcome

The two accepted R11 findings are repaired:

- `agy_settings_guard` rejects an existing or dangling symlink at the configured
  Antigravity `settings.json` path before creating transaction artifacts or
  changing the link target.
- Bootstrap usage now states the actual default: installed absolute-launcher
  rules automatically allow the managed wrappers, while `on-request` remains in
  force for other commands.

No LLM prompt or `SKILL.md` byte changed in this post-R11 repair, so no additional
prompt-skill review was run.

## Deterministic verification

- Focused RED: both symlink cases and the bootstrap wording contract failed
  before implementation (`3 failed`).
- Focused GREEN: `3 passed`.
- macOS, Python 3.12: `593 passed, 6 subtests passed`.
- Standalone log-cleanup suite: `28/28 passed`.
- macOS Bash syntax, Python compilation, plugin validation, and skill lint:
  passed.
- Ubuntu 24.04 pinned image
  `sha256:e9925f0b3f7832f47948760b8d05fec045469b3c00b3ddcb2500e9d30c28f09f`:
  `592 passed, 1 platform-specific skipped, 6 subtests passed`.
- Ubuntu Bash syntax and Python compilation: passed.
- `git diff --check`: passed.

## Review gate

The immutable R11 reconciliation remains authoritative at
`_runs/reviews/20260721-triad-reliability-final-r11-record/reconciliation.md`.
The formal gate is `REVIEW_UNAVAILABLE / INVALID / NOT-SAFE` because a required
Google leg produced schema-invalid output in three consecutive rounds. The
post-R11 code repairs do not change that reviewer-route result.

Do not start another full formal review round or deploy the plugin until the
owner chooses whether to deploy with this unavailable Google gate or wait for a
review-route repair.
