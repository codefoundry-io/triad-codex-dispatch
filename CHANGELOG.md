# Changelog

## 0.2.480 — 2026-07-12

**Hardened-audit custody + agy extraction strictness + review-packet
lifecycle.**

- Redact mode (hardened default via bootstrap): the durable audit now
  stores `stdout`/`stdout_head`/`stderr` as `"<redacted>"` plus
  lengths on every record and caps `extraction_error` at 500 chars;
  the transient failure run-log keeps full copies. NOTE: audit files
  written by earlier hardened installs may contain full non-ok
  streams — rotate/purge them once.
- The antigravity pty-fallback extractor accepts its completion marker
  only when TERMINAL (whitespace-only tail AND newline-preceded, per the
  sealed prompt's own-line instruction); a truncated run whose only
  marker is an early echo fails closed instead of returning a partial
  answer as ok.
- The cross-family-review skill ships a deterministic packet-lifecycle
  helper (`skills/triad-cross-family-review/lib/review_scratch.py`);
  packets stranded by a crashed review are swept at the next `open`.
- Relative `--prompt-file` stays fail-loud; the error now shows the
  caller cwd and a cwd-derived absolute candidate.

Built from the Triad source of truth. Full history: https://github.com/codefoundry-io/triad-codex-dispatch/commits/main (each release commit summarizes its delta).
