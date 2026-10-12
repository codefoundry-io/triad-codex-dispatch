# Codex Shared Library Adoption Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Use the shared library in Codex's existing v2 runtime and provide Claude port instructions.

**Architecture:** Generate the exact library package from a pinned wheel into the
existing plugin distribution. Thin host facades preserve native mechanisms and
delegate deterministic roster, prompt and verdict logic to it.

**Tech Stack:** Python 3.12+, triad-dispatch-lib 0.1.0.dev3, existing Pydantic/jsonschema.

**Spec:** `docs/design/2026-10-13-library-adoption.md`; library `spec/` and `docs/host-adoption.md` at commit `81748d721e56dfc3463888f02328902e18398600`.

## Global Constraints

- Work in the existing `triad-codex-dispatch-reliability` worktree on `codex/shared-library-adoption`; preserve unrelated untracked files.
- Common sources are library-owned; generated package bytes cannot be hand-edited.
- Preserve four configurable routes, host-native controls, exact bindings, workarounds and explicit v2 selection.
- No global install, dependency auto-install, Claude source edits or final merge.
- Python/tests/builds/Git mutations use `/bin/zsh -lic` with `sandbox_permissions="require_escalated"` on the first call; set an owned canonical TMPDIR before Python tests.
- Root owns instruction/prompt source edits; workers may edit runtime code and regression tests assigned below. No recursive delegation.

## Review Focus

- Modified or unexpected generated files survive a refused refresh (Task 1).
- An ambient library cannot replace the bundled implementation on executable paths (Task 1).
- Library resource/code changes invalidate prepared review custody (Task 2).
- Original duplicate/overflow JSON and all six binding swaps remain rejected (Task 2).
- Installed archive behavior does not depend on sibling library checkout or editable installs (Task 3).

### Task 1: Reproducible bundled dependency

**Files:** `scripts/vendor_library.py`, `bin/library_adoption.py`, `bin/triad_dispatch_lib/**`, `contracts/library-adoption.json`, `vendor/triad-dispatch-lib.LICENSE`, `requirements.txt`, `tests/test_library_adoption.py`.

**Interfaces:** `library_adoption.verify_library() -> dict` verifies the exact generated path inventory/hashes and returns adoption metadata. `vendor_library.py --check` performs nonwriting verification; `--wheel PATH --source-commit SHA --write` refreshes only unchanged managed files after complete validation.

- [x] Add failing integrity/refresh preservation tests: changed/missing/extra/symlink files, wrong wheel metadata, complete package resources, normal script import location.
- [x] Build from the exact clean library commit, record wheel hash and source identity, copy wheel package bytes and license unchanged; implement verify/refresh without runtime installation or global writes.
- [x] Verify generated content and focused tests; record RED/GREEN and commit only assigned files. Commits `5852787`, `e1dae12`; 26 passed; independent review and scoped fix review cleared.

### Task 2: Thin deterministic facades

**Files:** `bin/validate_v2.py`, `bin/verdict_v2.py`, `bin/review_roster.py`, `bin/review_prompts_v2.py`; corresponding existing tests plus `tests/test_library_host_integration.py` and `tests/test_v2_toolkit_inputs.py`.

**Interfaces:** Consume Task 1's verified package. Preserve existing host public signatures and result shapes. Use library `parse_json`, `validate_verdict`, `validate_binding`, `resolve_roster`, `render_review_clauses`, `render_data`; call with host B and exact per-family replacements.

- [x] Add failing host integration cases for delegation, four routes, repeated family entries, all bindings, overflow JSON and custody changes.
- [x] Replace deterministic implementations while retaining canonical file, legacy asset, packet, preflight and wrapper guards. Contract faults fail closed rather than counting as ballots.
- [x] Run focused roster/validator/producer/prompt/round/custody suites and commit scoped files with evidence. Commit `317f14f`; 503 passed, 4 existing route skips; independent review cleared.

### Task 3: Distribution proof and independent host handoff

**Files:** `bin/bootstrap_repair.py` only if dependency readiness needs the bundled import; `scripts/verify_distribution.py`, `tests/test_distribution_verifier.py`, `.github/workflows/test.yml`, `scripts/verify_library_runtime.py`; `README.md`, `README.ko.md`, `docs/installation.md`, `docs/verification/2026-10-13-library-adoption.md`, `docs/handoffs/claude-library-adoption.md`.

**Interfaces:** Archive verification includes all generated files and metadata. A neutral-directory isolated environment installs only existing host requirements and loads the archived bundled package through the host bin path, never a sibling checkout.

- [x] Add distribution/dependency readiness checks and native macOS/Ubuntu CI using owned TMPDIR. Preserve the existing clean-source verifier gate.
- [x] Run full host regression plus isolated archive smoke; update documentation with exact evidence and limits. Full source 2515 passed before readiness correction; corrected complete bootstrap/transaction suites 338 passed. Native CI reruns both full source and archive at the frozen final candidate.
- [x] Write concrete Claude instructions: pin identity, use host A clauses, keep native mechanisms and AGY hook profile, shared verdict binding, four-route/cancellation/conformance tests, managed-file conflict preservation and independent release.
- [ ] Complete independent task/whole-branch review and the project's available required multi-family gate; report unavailable required routes explicitly without substitution. Push candidate and attach draft PR; no merge or global installation.

This checklist is captured with the source review basis. Later whole-branch,
formal review and native CI outcomes are recorded in
[PR #44](https://github.com/codefoundry-io/triad-codex-dispatch/pull/44) and the
leader's per-round ledger, without rewriting the frozen review inputs. The
owner authorized Sol/xhigh in place of the unavailable Terra slot for this round.
