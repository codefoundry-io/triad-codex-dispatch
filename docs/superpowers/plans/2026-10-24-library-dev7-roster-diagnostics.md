# Library dev7 roster diagnostics implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Adopt published library dev7, preserve typed roster locations through the Codex facade, and publish/install verified Codex 0.2.565 after the required formal review.

**Architecture:** Keep shared validation in the vendored library. A small host `ValueError` subclass retains the library diagnostic fields and renders canonical schema locations through the existing CLI error path. Existing runtime selection and retained bindings remain unchanged.

**Tech Stack:** Python 3.12+, existing pytest suite, pinned wheel vendoring, native macOS/Ubuntu CI and the current four-leg guarded-worktree review.

**Spec:** Published [library dev7 API](https://github.com/codefoundry-io/triad-dispatch-lib/blob/62c3a741b729c6359cc5079a0306fad1fdd1fac8/spec/reference/library-api.md), [dev7 host handoff](https://github.com/codefoundry-io/triad-codex-dispatch/pull/46#issuecomment-6373568489), and the owner's current instruction to implement, verify, formally re-review, merge and deploy. The existing handoff plus this bounded implementation choice supplies the scope; no new shared contract is proposed.

## Global Constraints

- Start from main `2eec0bb62e0de027332b45c12e59fab94cf2bbc8` in the selected existing checkout. Preserve its intentional untracked files in place; do not read protected owner review artifacts, reset, clean, stash or create a separating checkout.
- Adopt library `0.1.0.dev7`, source `62c3a741b729c6359cc5079a0306fad1fdd1fac8`, published wheel SHA256 `cc24c8d285927c9a874a54c0b72a01668eaf77abbf183e6cf3abb8771ea9b480`. Use the complete verified package/license inventory and unchanged resource bundle identities.
- Verify the old package under its old pin; generate and verify dev7 in an owned empty staging directory; recheck old managed bytes before replacement; verify the complete new tree. Do not weaken the same-pin refresh guard or hand-edit generated modules.
- Preserve library error selection, `.code`, `.path`, `.missing`, `.document`, schema/prompt bytes and host-native behavior. `instance_path` is a tuple of canonical property names/indices, `()` is root and `None` is unavailable. Resolved indices describe final merged order.
- Keep existing `invalid roster: ...` text unchanged for non-schema failures and preserve refusal exit 2, contract faults, no invalid-input dispatch and all-selected agreement. Never render validator messages, input values or arbitrary unknown-key spelling.
- Python/tests/builds/Git mutations/provider CLIs use literal `/bin/zsh -lic` and `sandbox_permissions="require_escalated"` on the first call, outer cwd `/Users/chaniri/codex_workspace`. All test/tool invocations use this task's canonical owned TMPDIR from `_runs/20261024-codex-dev7/environment.json` in the workspace.
- Do not change source skills, model/effort defaults, global settings, shared-runtime algorithms, unrelated existing follow-ups or other hosts. Public release, installation, fresh skill exposure and live provider behavior remain distinct evidence.
- Preserve shared launcher default/bindings/retained snapshots and original caches needed by older direct consumers during the supported update. No lifecycle deletion is authorized merely by a newer version becoming available.

## Review Focus

- Later-entry failures must report the library's document and index, not an index inferred from host names: cover override timeout and resolved Google configuration errors.
- Root and unavailable locations are distinct: test `()` explicitly and preserve non-schema text for `None`.
- Unknown properties and sensitive values must not leak into diagnostics: use sentinel key/value assertions.
- Malformed roster input must stop before adapter preparation/provider calls and retain CLI exit 2/stdout-empty behavior.
- Pin migration must preserve old-tree verification and canonical resource identities; verify the new full inventory and unchanged non-roster library bytes.

## Task 1: Adopt dev7 and expose typed roster diagnostics

**Files:**
- Modify `bin/library_adoption.py`, generated `bin/triad_dispatch_lib/` and `contracts/library-adoption.json` through verified staging.
- Modify `bin/review_roster.py`.
- Test `tests/test_review_roster.py`, `tests/test_library_host_integration.py`, `tests/test_library_adoption.py`; use existing `tests/test_v2_rounds.py` seams if necessary for no-preparation coverage.
- Synchronize `.codex-plugin/plugin.json`, `CHANGELOG.md`, `README.md`, `README.ko.md`, current library sections in `docs/installation.md` and `docs/installation.ko.md`, and affected existing security/migration guidance only where the new diagnostic behavior needs explanation.

**Interfaces:**
- Consume shared `RosterError` and `instance_path` from the exact dev7 package.
- Produce host `RosterValidationError(ValueError)` with `code`, `path`, `missing`, `document`, `instance_path` copied without reinterpretation. The constructor takes the shared error. Existing callers continue catching `ValueError`.
- For schema errors with a non-None location, append ` [document=<JSON string>, instance_path=<JSON array>]` to the existing fixed-message prefix, using `json.dumps(..., ensure_ascii=True)`. Root renders an empty array. Non-schema text stays unchanged. Catch shared `RosterError` before the existing generic `ValueError` branch; keep `ContractError` propagation unchanged.

- [ ] Record baseline focused roster/adoption/integration checks and old dev6 inventory verification.
- [ ] Add failing tests for typed fields, later-entry attribution, root versus unavailable, sentinel privacy, CLI status and no adapter preparation. Observe intended RED before production changes.
- [ ] Perform the verified dev7 pin transition, including hardcoded adoption test fixtures, preserving all four resource bundle identities.
- [ ] Implement the small facade adaptation and observe focused GREEN. No caller changes unless a concrete existing boundary requires them.
- [ ] Update 0.2.565 metadata/current upgrade notes and diagnostic documentation in English/Korean. Keep historical release headings and unrelated owner files intact.
- [ ] Run the full isolated host suite, vendoring check and affected distribution-contract checks. Record exact results, skips, environment and production/test/doc deltas; commit only this task's files.
- [ ] Obtain independent task review and final whole-branch review; reproduce and fix in-scope findings, preserving the review lifecycle.

Expected handwritten production delta: 20-40 additions, 1-5 deletions, net 15-39; novel core under 40 lines. Vendor changes, tests and documentation are counted separately. A shared-runtime pin integration correction may be included only if required to preserve existing supported compatibility, with its regression and recorded scope.

## Verification, formal review and delivery

- Use the current workspace Opus/Argon/Flash/fresh Sol composition over one current guarded source basis, with all required results and matching final integrity. Required provider calls may use the previously authorized 2400-second deadline. A failed or changed round gets no admission reuse.
- Source/archive distribution verification requires a clean checkout. Preserve owner untracked files and use native clean-checkout CI for that evidence rather than removing or relocating them.
- Create and attach the implementation PR; verify exact reviewed tree and native CI. Merge under the current explicit owner authorization, verify merged tree equality and post-merge checks, then publish 0.2.565 from the actual merged SHA with archive/checksums/manifest.
- Download and verify published assets. Follow the existing already-shared plugin update procedure; verify installed source and retained toolkit identities, old-consumer preservation, explicit new Codex selection, and fresh plugin-qualified skill exposure. Preserve 0.2.563 and existing shared assets throughout.
- Update Codex #46 and library issue #9 with actual results. Issue #9 remains partial/open beyond the bounded location property. Report only observed outcomes and real remaining limits.
