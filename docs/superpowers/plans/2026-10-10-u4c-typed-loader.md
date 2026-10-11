# U4c — Typed classifier-extension loader

> Use superpowers:executing-plans inline, with fresh dedicated source executors
> for RED/GREEN and the required owner-selected multi-family review.

Goal: enforce the existing DL-97 class restriction and DL-106 zero-key exclusion
when reading a hand-edited extension, preserving valid data and file bytes.
Spec: shared50845c5, R-CLASSIFY/R-TOKENS, C77 and
decisions/2026-10-10-b-typed-loader.md. PR13comment6084876199 shares the outcome
and A c890731 source evidence before implementation. Remote main3afc4d7.

Architecture: change only `_load_classifier_extension() -> dict` in
`bin/_common.py`, using the existing `VENDOR_EXIT_PROPOSAL_CLASSES` vocabulary.
No new class, schema, provider operation or native mechanism. Python3.12+.
Preserve source dirty work and actual AGY weak fallback. New-auth proposal
refusal is distinct from loading already-curated authentication entries.

Estimated delta: production+10-22/-3(net7-19), novel core<=19; tests80-110lines,
documentation15-25lines across current English/Korean/security/migration docs.
No function/module split, settings migration or new key-range policy.

## One bounded task

Files: existing bin/_common.py loader, new
tests/test_classifier_extension_contract.py; affected existing guidance.
Inputs: existing per-CLI vendor_exit_map JSON. Output: the same sanitized dict
with unsupported string classes and integer-zero keys excluded. Log each rejected
entry once per load; preserve current wrong-type handling and file immutability.

- [x] Add literal C77 fixtures: wrapper-only/unknown/ok classes become unknown
  on ordinary failure; supported six classes and valid siblings remain; numeric
  zero spellings are excluded; malformed values remain harmless; success stays
  ok; extension bytes remain unchanged. Tests call real loader/classifier, no
  provider and no copied implementation-set equality assertion.
- [x] Fresh dedicated RED observes unsupported-class/zero-key failures with
  passing valid-entry controls; record exact commands and state/cleanup.
- [x] Replace the string-only comprehension with the minimal filtering loop.
  Retain the existing proposal set including curated oauth-env and the separate
  applier authentication refusal. Keep parseable nonzero key policy unchanged.
- [x] Align affected guidance, fresh dedicated GREEN, complete affected modules,
  full suite once and four skill validators; exact fixtures and state proof.
- Verification: final child-isolated GREEN403focused/2143full passed,4skipped,
  four validators, seven hashes/HEAD/status and ten source log records unchanged.
  Exact neutral root removed. Earlier manifest failure and unisolated-log
  assertion failure remain evidence, with missing historical inventory disclosed;
  the owned stale-canary probe and runner-only isolation correction are recorded
  under _runs/spec-plan-20261010/u4c/. No product correction followed GREEN.
- [x] Fresh all-four review, integrity/export/cleanup, shared evidence and SoT.

R1 all-four SAFE, ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK; digest
5242550c0942c0bc56dd445c4c4c25597d69fea406dd2ad7c5e1bc32b1eae669.
All producers terminated and exact temporary stage/cwd removed after export.
One optional test-evidence note is retained: success assertion is a control;
the loader dictionary assertion is the zero-key RED evidence. No further edit.
Shared d1b9bcc, PR13comment6085594103; authoring1/1 and182tests passed.
This bounded unit is complete; other DL-106 removals and the overall task remain.

Review focus: actual unknown/contract token behavior, valid sibling preservation,
no success override, source-file immutability, no accidental authentication-policy
change. These boundaries are covered by the named tests, not hypothetical vendor
error messages. Related DL-106 deletion candidates remain separately assessed.

Commands: /bin/zsh -lic with sandbox_permissions=require_escalated from
/Users/chaniri/codex_workspace, absolute product paths. Keep product changes
local; no merge/install/release authority follows from this plan.
