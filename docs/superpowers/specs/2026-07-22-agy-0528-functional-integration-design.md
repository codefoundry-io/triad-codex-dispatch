# AGY 0.2.528 functional integration design

Date: 2026-07-22
Source commit: `94a24cb2e59972cd8fccefd06c05a6a7b77166b8`
Target: `codex/triad-reliability-redesign`

## Goal

Integrate only the upstream behavior that prevents a lossy AGY answer from
being admitted as success. Preserve the target branch's worktree-first review,
read-only formal-review posture, result custody, and existing unreleased version.

## Accepted behavior

- Detect an own-line `<truncated N bytes>` or `<truncated N lines>` marker in a
  non-empty AGY answer with vendor exit zero.
- Check for the marker after the nonzero vendor-exit gate and before plain or
  Pydantic success. A nonzero vendor exit remains `vendor-error`; a truncated
  zero-exit answer never reaches schema validation or schema repair.
- Return `truncated-answer` with terminal exit 65 through the target branch's
  `finish()` helper, keep stdout empty, and retain a bounded diagnostic in the
  normal failure run log.
- Add the classification to the shared exit mapping defensively.
- Document `truncated-answer` as a deterministic, non-repair failure. Formal
  review treats the required Google leg as invalid and requests a new bounded,
  compact result; it does not switch providers after post-dispatch truncation.

## Rejected upstream behavior

- Do not copy the generic long-answer `write_file` workaround. AGY read-only
  mode denies `write_file(*)`, and allowing an arbitrary absolute output path
  contradicts the formal no-edit contract and pre/post worktree fingerprint.
- Do not omit `--sandbox read-only`, grant shell access, or change candidate
  source so a reviewer can emit a long answer.
- Do not merge upstream history, bump the plugin version, rewrite the changelog,
  tag, release, install, or push as part of this functional port.

## Tests

- Zero-exit transcript and PTY-fallback answers containing bytes/lines markers
  are terminal and quarantined.
- Pydantic validation and schema retry are not reached for truncated answers.
- A nonzero-exit marker remains `vendor-error`.
- Indented own-line markers match; inline prose does not.
- Result persistence emits no answer on stdout and keeps the diagnostic.
- Static skill contracts name the new terminal classification and forbid the
  output-file workaround in formal review.

## Commit boundary

The functional port, its tests, and this design join the current worktree-first
and Agent-review changes in one local commit. Push, release, installation, and
provider execution remain separate actions.
