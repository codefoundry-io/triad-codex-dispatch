# U4d — Remove redundant classifier code

> Execute inline with superpowers:executing-plans; use fresh dedicated source
> executors for before/after verification and the required four-family review.

Goal: reduce internal maintenance code with identical classification outcomes.
Spec: DL-106, R-CLASSIFY/R-TOKENS and C77; shared decision
decisions/2026-10-10-b-classifier-removals.md. B632f426 plus preserved candidate;
main3afc4d7, read-only A a5afdd5a. Python3.12+, native legs host-owned.

Architecture: edit only bin/_common.py. Remove the unused private _json_len
and Gemini/Codex/Claude maps containing only0:ok. Select the retained AGY map
only for antigravity and use extension entries directly for other CLIs.
Keep the built-in-over-extension merge and weak-fallback priority for AGY.
Preserve classify's optional vendor_exit_code signature and fallback behavior.

Estimated production+3-8/-35-50(net-27..-47), novel core<=3; tests+1/-2, shipped docs0.
No public behavior/interface change, new class, provider operation or settings.

## One bounded task

- [x] Confirm no named repository source/test/script caller of _json_len or
  the removed maps outside their own definitions/classifier selection.
- [x] Publish shared host-specific disposition before dependent deletion.
  Shared4072d2c/be18058; authoring1/1 and182tests passed, normal push complete.
- [x] Save the pre-unit source and run complete existing affected modules with
  a fresh source executor; no manufactured failing name-absence test.
- [x] Remove the private helper, three no-op maps, redundant selection branches
  and stale internal explanation. Keep AGY and callable compatibility.
  Baseline393tests/four validators passed; state/logs unchanged, exact root removed.
  First post-removal run:392passed/1failed; an existing token-contract test
  constructs deleted map names dynamically, missed by named-reference search.
  Corrected its membership check to the retained AGY map. No behavior test or
  name-absence assertion added; no production correction. Fresh final run hashes
  this test too. Retain the failed run and its unchanged-source/log receipt.
- [x] Fresh executor repeats the same modules and four skill validators;
  record source state, child-only log/TMPDIR isolation and exact cleanup.
  Final393passed/four validators passed; three hashes/HEAD/status and ten logs
  unchanged. Exact root removed; green-final/report.md records terminal proof.
- [x] Fresh required four-family review; adjudicate, export and exact cleanup;
  update shared evidence, SoT and broad plan.
  R1 all-four SAFE/ROUND_INTEGRITY_OK; all producers terminal, custody exported,
  exact stage/cwd removed. Shared c25da30 pushed; PR13comment6089074042 published.
  Final production+3/-43(net-40), existing test+1/-2. No post-review product edit.

Verification modules: test_classifier_extension_contract.py,
test_exit_token_contract.py, test_auth_carriers.py, test_gemini_auth_exit.py,
test_vendor_quota_contract.py, test_antigravity_stream_json.py,
test_repair_replay.py, test_repair_proposals.py, test_provider_wrappers.py.
These cover success, ordinary/extension codes, retained auth41 and timeout
priority, AGY no-answer outcomes, wrappers and stored replay. Run all cases
in these modules, not a selection by test name. No provider CLI execution.

Review focus: success remains ok; ordinary unknown failures remain unknown;
curated valid entries remain effective; AGY weak fallback and stronger signals
retain priority; omitted raw exit remains compatible. Static reference closure
and passing before/after behavior justify removal, not a new failure scenario.

Ruling: this is a behavior-preserving removal, not a feature/bugfix; use baseline
and equivalence verification rather than fabricate RED or test private names.
Project dirty-state/custody rules take precedence over generic skill commit,
workspace deletion and whole-branch packaging steps. No source commit/install/
merge/release is implied. Runtime evidence2143full/4skipped from U4c remains the
previous candidate's full-suite result; this unit runs complete affected modules.
All Python/tests use /bin/zsh -lic, require_escalated, workspace host cwd.

## Final reachability and review qualification

The current AGY wrapper handles raw-zero missing/empty answers directly; its
stored replay reuses that interpreter. The retained map affects direct common
classify/classify_extraction calls, not the current wrapper route. Retain this
callable compatibility without claiming CLI dependence. The nine-module suite
does not directly exercise that raw-zero branch. A supplemental provider-free
before/after probe confirmed four identical outcomes (extraction-error, capacity
priority, success and omitted-raw-exit curated mapping), unchanged source hashes
and exact cleanup: _runs/spec-plan-20261010/u4d/callable-probe.json.

Three Minor findings were adjudicated: stale internal comments and an optional
redundant ok guard remain nonblocking; the reachability claim is corrected here
and in shared evidence. No fourth wording pass or additional implementation.
Review: workspace _runs/reviews/triad-classifier-removal-20261010-r1/;
digest7a9d4deec112a34efeb14196624ab35091813c6bab199325afbaf10d15f21a01,
fingerprint529c84290a1912e9a6abf8caaaea633a4b73ac9ea3440f7f58e30557bd7258cd.
