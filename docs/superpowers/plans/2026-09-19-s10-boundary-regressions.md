# S10: Reachable boundary regressions and operator guidance

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Root owns source/tests; a fresh dedicated executor verifies behavior and independent reviewers report findings.

**Goal:** Characterize two reachable adopted boundaries and clarify their actual operator limits.

**Architecture:** Extend existing synthetic Git and local-child NDJSON fixtures, with no production logic changes. Correct affected English/Korean/security guidance inside the same cohesive slice.

**Tech Stack:** Python 3.12+, pytest, real synthetic Git/local subprocess fixtures.

**Spec:** `../specs/2026-09-18-dispatch-adoption-design.md`, S10; selected cases recorded in the campaign.

## Entry and constraints

- Start implementation only after S9's gate, CI and authorized merge.
- Preserve dirty AGENTS.md and provider settings; no live provider inference, hook activation, wrapper redesign, copied upstream parser, or deployment.
- Expected production +0/-0, novel core 0; tests about +75; docs about +45/-5. S9's optional tuple-binding and version-boundary regressions belong to this adopted-boundary characterization scope.
- These characterize already selected behavior. An initially passing case is expected evidence, not an invented RED or reason to change correct production. A new real failure must first be classified against the approved design.

## Task 1: Existing behavior and matching guidance

**Files:** `tests/test_review_round.py`, `tests/test_antigravity_stream_json.py`, `tests/test_google_diagnostics.py`, `README.md`, `README.ko.md`, `SECURITY.md`, `docs/superpowers/plans/2026-09-18-s5-effective-cwd-receipt.md`, `docs/superpowers/specs/2026-09-18-codex-stdin-safety-design.md`.

- [ ] Add a real synthetic Git case: commit `.gitignore` with `build/`, create only an ignored file under `build`, assert ordinary porcelain status empty and `_committed_input_cli(worktree, HEAD)` returns the fingerprint successfully. This distinguishes ignored artifacts from disallowed untracked inputs.
- [ ] Add parameterized SUCCESS/ERROR NDJSON subprocess characterization using `_common._run_once(..., cwd=launch, classify_and_log=False)` and AGY `_interpret_run`. The real child prints canned stream bytes, and interpretation must preserve the captured launch cwd and expected result classification/exit. It must not execute a real provider.
- [ ] Replace the hardcoded S5 validator home path with a resolved `$TRIAD_SKILL_VALIDATOR`; correct the S3 spec's audit symbol to `emit_run_log`.
- [ ] Bind the diagnostic fake's environment-name fixture to the production removal tuple so future divergence fails. Add real-fake version outputs with no dotted numeric triple and an oversized component; both remain complete with no parsed version and retain exact raw stdout hash/count. These characterize the existing parser without changing it.
- [ ] Explain in both READMEs that the committed-input setup check uses `--ignore-submodules=none`, so configured ignore settings do not hide modified/untracked submodule content or a moved submodule HEAD. Keep the distinction between setup and later integrity.
- [ ] Add compact disabled-hook activation requirements to both READMEs and SECURITY: use/prove a trusted absolute Python interpreter; matcher `*` covers the entire enabled session; prove a complete review still finishes while off-list tools remain denied; verify oversized stdin/broken-pipe and process-failure outcomes before enabling. Do not assert undocumented internal tools, introduce unbounded stdin draining, or widen the allowlist.
- [ ] Fresh dedicated Terra/high executor verifies focused regressions, full suite, source skill validator and provider-free lifecycle, retaining complete terminal receipts and exact cleanup. Keep source fixed throughout.
- [ ] Independent static task review, leader adjudication, scoped commit, four-leg gate/integrity, CI and authorized merge before S11. The existing design-defect stop remains binding; no deployment in this slice.
