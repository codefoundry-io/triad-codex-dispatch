# Formal AGY Claude-Parity Native-Sign-In Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development or superpowers:executing-plans.

**Goal:** Preserve personal Google Sign-In and company Gemini Enterprise
Business Sign-In through the same executable AGY review route used by the
deployed Claude-led TRIAD.

**Architecture:** Copy the current deployed `_agy_settings.py` byte-for-byte,
connect the Codex wrapper's existing stream/schema/verdict path to that
transaction, retain child environment billing-route scrubbing, and keep the
existing prepared-directory/worktree integrity gate.

## Slice budget

- One behavioral claim: formal AGY follows the Claude settings-transaction,
  sandbox, headless-adaptation, and restoration lifecycle.
- Forecast production net delta: about 610 lines, above the approximate S/M
  target but below the 800-line ceiling. Of that, 544 lines are the byte-identical
  proven helper; the independently reviewable novel integration remains thin.
- Novel core: at most 30 lines of Codex wrapper integration; the 544-line
  transaction is an exact proven copy, not a new semantic model.
- Tests and documentation are unbounded.

## Execution

- [x] Verify source and deployed Claude repositories against their remote heads.
- [x] Prove the wrapper and settings helper hashes agree across source and
  deployment.
- [x] Run a dedicated skill-executor RED showing the Project contract blocks the
  otherwise working Claude path.
- [x] Run code RED showing missing settings guard, sandbox, auto-approve, and
  formal lease behavior.
- [x] Copy the deployed `_agy_settings.py` with identical SHA-256.
- [x] Connect the Codex wrapper to `--sandbox read-only`, version-gated
  `--dangerously-skip-permissions`, environment scrubbing, and the settings
  guard without changing its one-call stream/schema/verdict admission.
- [x] Update bootstrap, distribution manifests, public docs, and skill SOT.
- [x] Run focused and full tests, Ruff, formatter checks, and `git diff --check`.
- [x] Run dedicated skill-executor GREEN against current bytes.
- [ ] Run a fresh operational three-family review. Any infrastructure failure
  stops the full round before code adjudication.
- [ ] Build, verify, publish, install, then resume Argus.

## Stop rules

- Do not introduce API-key, Vertex, ADC, service-account, or account fallback.
- Do not add a new permission abstraction or improve the copied transaction
  without a failing test and runtime evidence that it is better than Claude.
- Do not count prompt-controlled read-only as OS containment. The headless
  auto-approve residual must remain explicit.
- Do not run `skill-prompt-review`; use only the dedicated skill executor for
  skill behavior tests.
