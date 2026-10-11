# U1T — preserve model values across CLI parsers

## Outcome and authority

Implement the settled opaque-value requirement in shared56b5fc5,
R-MODEL/C18/C34 and DL-132. The owner authorized this bounded implementation.
Scenario: a pin shaped like `--help` must reach model validation rather than
trigger help; ordinary unknown pins and spaces must remain exact. No model-name
grammar, availability gate, permission change or native-leg change.

Basis: B5f5dda5b, main3afc4d7, PR12 11934f11; A transport9e16880d.
PR13 coordination: comment6095287430. AGY1.3.3 measured separate help versus
equals invalid-model/zero-turn rejection. Claude2.1.289 accepts both tested
spellings on its selection path. Retained Gemini0.63.0 actual parser and Python
wrapper measurements are reused. Evidence and limits:
`_runs/spec-plan-20261010/u1t/assessment.md`. These are not availability probes
to add to the product. Initial harness import failure remains retained.

## Smallest coherent change

- Emit one equals-form model token from v2 `_invocation`, Google adapter
  preflight and Gemini raw/v2 `build_cmd`. AGY uses equals form only for a pin
  starting with `-`; ordinary pins keep their measured existing spelling.
- Match both Google v2 receipt builders to those bytes. Legacy AGY's fixed
  ordinary pins, validator and project suffix remain unchanged. Existing
  receipts are not rewritten.
- Keep Claude native argv, native Codex invocation, legacy Gemini `-m auto`,
  user environment, null/default semantics, effort, identity checks, policy and
  one terminal rejection. Existing toolkit/receipt drift refuses old evidence.

Revised expected production: +10–20/-8–15 (net0–10), <=15 novel core lines,
five files: review_round_v2, review_adapters_v2, antigravity_wrapper,
gemini_wrapper, google_preflight_v2. Tests/fixtures: +120–180/-5–15;
documentation/status: +80–140. Receipt coupling belongs to the same
observable outcome; no new abstraction or transport layer.

## Steps and checks

- [x] Measure missing parser boundaries; preserve old evidence and limits.
- [x] Finalize shared rule/cases before product edits; shared authoring1/1 and
  182tests pass, shared56b5fc5 pushed and PR13 notified.
- [x] Collect independent Claude, Google and fresh Codex diagnosis; reproduce
  source findings. Only a substantial unresolved design choice returns to owner.
- [x] Fresh dedicated source executor RED: actual generated-wrapper parsers,
  Google adapter preflight, bound vendor dispatch/receipt and raw Gemini.
  Controls: ordinary/unknown/spaced pins and null where already supported.
- [x] Apply the minimal production correction and update only affected fixture
  assumptions. No fake parser success is described as vendor availability.
- [x] Fresh dedicated GREEN: affected adapters/wrappers/rounds plus complete
  repository regressions and all four source-skill validators; preserve logs,
  source fingerprint and exact temporary-fixture cleanup. macOS only; Ubuntu
  not run. Native parser measurements are separate from provider-free tests.
- [x] Fresh complete owner-selected review: opus/xhigh, AGY Pro/high,
  AGY Flash/high and fresh Astra/high on one guarded worktree basis. Read
  related source freely within the product boundary; no routine read audit.
- [x] Adjudicate, export/clean exact review stage/cwd, update shared evidence,
  publish source/checkpoint and report remaining work. Whole-task hook stays.

No installation, adopted-revision update, merge or release is authorized here.

## Diagnosis and RED checkpoint

All three independent diagnoses collected: Claude opus/xhigh, Google Pro/high,
fresh Codex Astra/high. No new common-model grammar is warranted. Raw reports
and adjudication are under workspace `_runs/infra/20261010-spec-to-code/u1t/`.
The proposed global AGY spelling change was narrowed after diagnosis: no
evidence certifies equals-form ordinary pins on every older supported release,
so keep existing ordinary/legacy transport. Only already-broken option-shaped
pins gain equals encoding. This removes the need to edit legacy receipt
validation or impose a higher CLI floor. It does not certify older parsers for
previously broken pins; vendor refusal remains one terminal result.

Initial dedicated RED:22failed/74passed/4skipped, source/log integrity and exact
cleanup passed. Revised test no longer demands equals spelling for already
working ordinary AGY pins; a fresh bounded RED follows before product edits.
Google's speculative null-default omission and other-option expansion were
rejected against current defaults and scope. String concatenation preserves
existing type failures without new model validation.

Revised fresh RED20failed/76passed/4skipped; no harness error, unchanged source
and logs, exact cleanup. Candidate production +8/-9 (net-1), five files; existing
receipt format changes only where argv changes. No legacy validator change.

Initial GREEN affected634/4 passed; full2313/4 passed with two failures in the
same custom-schema investigation test (repair false/true), which still looked
for separate `-m`. The emitted command and answer were correct. Updated that
test to check the model on each actual command, retaining its web-clause/output
checks. No production change. Fresh corrected GREEN checks the changed module
and model transport, then the complete repository and all four validators;
the already-passed unchanged affected suite is not duplicated separately.

Corrected fresh GREEN:71 affected passed; full2315 passed/4 skipped; four skill
validators pass. Source/logs unchanged and exact fixture cleanup confirmed.
Evidence: `_runs/spec-plan-20261010/u1t/green-corrected/receipt.json`.
Next: prepared fresh review `triad-model-transport-20261010-r1`.

R1 finished all-four SAFE with matching integrity and exact cleanup. Its Minor
old-argparse finding was reproduced from official CPython v3.12.1/v3.12.2
modules: the former turns `--model=--` into an empty list. Current wrapper
truthiness can omit that value. Shared d082a60 records the parser evidence,
no-omission clarification and A follow-up before this correction.
Fresh dedicated RED-parser:3failed/43passed, unchanged source/logs and exact
cleanup. Add three lines per wrapper to refuse non-None non-string parsed
models before I/O. No Python floor change, guessed value recovery or name
grammar. Revised production +17/-9 (net8), six files, <=20 novel core lines.
Fresh GREEN-parser/full/validators and complete R2 are required for these bytes;
R1 approval is not carried forward. The earlier GREEN remains historical.

Final fresh GREEN-parser:82 affected passed; full2326 passed/4skipped; four
validators pass. Source/logs unchanged, exact temporary fixture removed.
Next: complete fresh `triad-model-transport-20261010-r2` over these final bytes.

R2: three SAFE, Astra NOT-SAFE, matching integrity; exported and cleaned.
The only finding is test compatibility: the new literal '--' cases wrongly
require parsing success even on the older parser where refusal is correct.
Fresh RED-compat with the SHA256-checked official3.12.1 argparse module on
3.12.13:11failed/35passed, unchanged source/logs and exact cleanup.
Corrected only tests/test_model_value_transport.py: ordinary injection control,
actual parser capability check, exact transport or pre-I/O argument refusal.
No tests are skipped and no production changes follow. Fresh GREEN-compat runs
the changed/related modules on the current parser and all46 transport tests on
the retained old parser, then four validators. Full2326/4 remains evidence for
identical production/other tests, predating only this test correction. A fresh
complete R3 is required; no R2 majority approval or old-round credit.


Final GREEN-compat:82 current affected/46 official old-parser module tests,
four validators passed. Source/status and existing run logs unchanged; exact
fixture removed. Full2326/4 remains the identical-production evidence before
the final test-only correction. R3 all-four SAFE, ALL_SELECTED_APPROVED and
ROUND_INTEGRITY_OK; one optional future-drift suggestion does not identify a
current defect, so no new helper/assertion or required backlog. All producers
terminal; result bindings/integrity/adjudication/export/exact cleanup complete.
Current shared main3afc4d7, PR12 11934f11, A0be173bf clean; later A work is
documentation/comments only. Source/shared publication follows this checkpoint.

Published sourceed8b76f / sharedd3a4412, remote equality verified; PR13
comment6095971207. Whole-task hook retained; next U6a.
