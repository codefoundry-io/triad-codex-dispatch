# Published dev4 library update

**Goal:** Ship the published `triad-dispatch-lib 0.1.0.dev4` in Codex host 0.2.562 using the existing approved bundling design.

**Source:** Release `v0.1.0.dev4`, commit `087af94a7078de0ae9701fb057840b5492f51f66`, wheel SHA-256 `c5bfdf10c4ce81f431ec7f77106e4d77b1556ac9c7b6b01bdb6616f988e8b2cc`. The library's later API compatibility CI does not change this released runtime.

## Boundary

Preserve the current facade calls, native adapters, scheduler, model/effort defaults and Python 3.12+ requirement. New library APIs are available in the complete bundle; adopting them into host orchestration is outside this update. Claude remains host-owned. Preserve intentional untracked documents in the selected worktree.

One coherent unit: verified package refresh, complete distribution inventory, regression coverage and current release/install documentation. Estimated upstream generated delta: up to 600 additions/150 deletions; host production delta under 20 additions/10 deletions, no new algorithm. Tests: approximately 60 additions/15 deletions. Documentation is counted separately. These are planning estimates, not gates.

## Execution

All Python, tests, builds, Git/GitHub mutations and provider commands use literal `/bin/zsh -lic` with `sandbox_permissions="require_escalated"` from `/Users/chaniri/codex_workspace`. Test runs allocate their own canonical TMPDIR before Python starts.

1. Verify old managed files under the old pin. Verify the published wheel against the release manifest and exact tagged source. Generate and verify the new bundle in an owned empty stage; recheck the old tree immediately before replacing only managed files. Update independent content pin and inventory for the receipt module/bundle.
2. Add meaningful inventory regressions for new module/resources, including missing/tampered files and allowed runtime cache. Update distribution requirements and existing package identity assertions. Keep host facade behavior unchanged.
3. Align plugin version, changelog, English/Korean current upgrade and installation guidance. Link the library release and adoption guide; do not prescribe another host's deployment commands.
4. Run focused/full host tests, isolated library runtime and committed archive verification. Obtain native macOS/Ubuntu CI. Preserve exact commands, terminal results, counts and limitations in task evidence.
5. Perform the required full-scope independent host review with 2400-second limits and official web research allowed. Concrete reproduced failures and contract violations govern corrections; optional style or speculative hardening does not block merge.
6. Prepare the PR and release notes. Final merge requires explicit approval for this PR. After approval and verified publication, perform the supported marketplace/plugin/bootstrap update and fresh installed-session check. Keep source, release, install and runtime proof separate.

## Ownership

The bundle implementer owns `bin/library_adoption.py`, generated `bin/triad_dispatch_lib/**`, `contracts/library-adoption.json`, `vendor/triad-dispatch-lib.LICENSE`, `scripts/verify_distribution.py`, `tests/test_library_adoption.py`, and `tests/test_distribution_verifier.py`. The root owns release/docs, integration, review and installation. No recursive delegation or edits to other workers' files.

## Evidence

Task evidence: workspace `_runs/20261017-codex-dev4-update/`. Source baseline: `2fb1cef8b8dc9d560a6eaa569b1e614281eed569`. Local installed plugin before work: 0.2.561, bundling dev3.
