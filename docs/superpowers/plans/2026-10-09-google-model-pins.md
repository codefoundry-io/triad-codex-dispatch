# Google model pins without catalog gates

Status: COMPLETE (bounded Google unit). The owner chose one Gemini CLI floor of 0.63.0, recorded
before implementation as D-GEMINI-FLOOR-20261009 in shared rules and cases.
Raw, legacy and v2 use this floor; 0.63.0 prereleases are below it. The earlier
held draft is retained as history. No model-specific or catalog gate survives.

> Execute inline with `superpowers:executing-plans` and TDD. The owner already
> authorized spec-to-code work and asks for a stop only for substantial design
> changes or necessary unsupported decisions. Live progress remains in
> `docs/status/spec-to-code-sot.md`; no duplicate progress authority.

**Goal:** Pass a user's Google model pin unchanged without a catalog probe or
packaged-list rejection, retaining required interface and containment checks.

**Spec:** Shared `reference/review-rules.md#R-MODEL`, C18, DL-116 at `3afc4d7`.
Claude source gate removal `86cffe93` corroborates this rule but is not its authority.
This is a bounded correction to existing Google preflight/dispatch, not a new
route or model default. No native-leg or Claude-selection changes.

**Architecture:** Remove AGY's catalog call and Gemini's model-dependent support
lookup. Continue validating Gemini's required CLI version, policy and receipt
at both creation and consumption. Leave shipped model data informational and
bound source manifests intact. Existing legacy fixed roster remains separate
from v2 user pins. Record terminal vendor rejection once without fallback.

**Estimate (updated for owner floor):** Production +25/-80 (net -55), novel core
<=20 lines across `bin/antigravity_wrapper.py`, `bin/google_preflight_v2.py`,
`bin/gemini_wrapper.py`, `bin/review_round.py`. Tests +100/-100 plus version
fixture changes; documentation about 60 changed lines. Adjust the estimate with
evidence if terminal refusal behavior needs a separately bounded correction.

## One functional unit

- [x] Fresh dedicated source-skill executor RED on a valid route with a missing
  catalog entry. Scenario and expectation recorded outside the guarded source.
- [x] RED regression: unknown Google pin survives preflight, receipt loading
  and actual wrapper command; no `agy models` call. Test both routes, including
  Gemini 0.63.0 with a later/future model pin. Versions below 0.63.0 fail before
  inference on raw and review paths; policy and interface controls still apply.
- [x] Preserve negatives: version below capability floor, invalid effort,
  changed model/receipt, altered binding, policy failure, no provider on preflight.
- [x] Minimal production removals, then affected suite GREEN. Update obsolete
  tests that explicitly required catalog calls; preserve unrelated dirty tests.
- [x] Keep CLI diagnostic catalog display unchanged: only review/dispatch gates
  are in scope. Update README English/Korean, SECURITY and source leg contracts
  that currently instruct a catalog check. No release version change.
- [x] Fresh dedicated executor GREEN; full repository tests and applicable
  source skill/distribution contract checks. No clean release archive claim
  from this intentionally dirty worktree.
- [x] Fresh complete four-leg formal review, integrity and exact stage cleanup.
  Update SoT and shared audit evidence; no merge/install/release.

Final evidence: `triad-google-pins-20261009-r4`, all four SAFE,
ALL_SELECTED_APPROVED / ROUND_INTEGRITY_OK; exact temporary cleanup complete.
Actual four runtime-file delta: +21/-65 (net -44); one adapter comment +1/-1
and two historical-data annotation lines are separate. Full suite 1,856 passed,
4 skipped before documentation/test-only corrections; final affected modules
185 passed, 4 skipped. Canonical dedicated GREEN and validator passed.
Three optional nonblocking notes are dispositioned in the final review evidence
and SoT. Product code remains uncommitted with intentional prior work preserved.

**Review focus:** catalog absence must not stop a valid pin; version floors and
containment must remain; pins cannot change between preflight and dispatch;
vendor failure must not trigger model substitution or repeated inference; source
skill must no longer request catalog availability checks. Synthetic vendor
responses prove control flow only, never new vendor output shapes.

**Commands:** Use `/bin/zsh -lic` with `sandbox_permissions=require_escalated`
from workspace host cwd. Focused tests: `test_v2_google_wrappers.py`,
`test_antigravity_stream_json.py`, `test_provider_wrappers.py`,
`test_verify_lifecycle.py`, `test_v2_adapters.py`, `test_distribution_contract.py`.
Then the project's full `python3 -m pytest -q "$1/tests" --rootdir "$1"
-p no:cacheprovider` command. Expected: all pass; skips and runtime limits recorded.
