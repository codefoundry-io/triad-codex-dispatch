# Non-authentication classification: scope adjudication

Date: 2026-10-09. Read-only source/spec comparison; no provider calls or tests
were run for this adjudication. No production or shared-spec change is claimed.

## Current evidence

- B: `632f42633d3a92d6cb27168cd15c4d4debd8558c` plus the preserved dirty
  candidate. `bin/_common.py:1376-1381` promotes empty-result permission denials
  to an extraction error containing the denial JSON. `classify_extraction`
  at line 774 passes that extracted text to the classifier. The existing shared
  lists at lines 97-168 still include `too many requests`, `400 bad request`
  and `schema validation failed`; `_p` at line 828 includes shared lists on
  every CLI. The earlier R3 diagnostic demonstrates this constructed input's
  classification, not occurrence of that combination in a vendor run.
- A: clean checkout at `5473933a8be8ecf08855ed35294f926a5504b7a7`.
  No `3rd-Agent/wrappers/claude_wrapper.py` is shipped. Its review leg contract
  says the native Claude spawn has no wrapper. Do not transpose B's Claude CLI
  extraction path into A's native leg.
- A `3rd-Agent/wrappers/_common.py:134-204` empties shared phrase lists and
  retains per-CLI measured phrases with evidence comments. The three example
  fragments above are explicitly removed. `classify` at lines 2020-2023 reads
  each CLI's own entries. `tests/unit/wrappers/t1-classify-timeout.sh:160-204`
  covers generic-fragment and cross-CLI controls. These are source observations;
  A's tests/runtime were not executed here.
- Shared spec: clean checkout at `75dc801923cd69b875c132c61d492489a0249729`.
  `reference/review-rules.md:723-732` requires vendor-owned, per-CLI sentences.
  Lines 797-828 record constructed unobserved shapes as limits and require
  measured evidence for retained phrases. `authoring/shared-dev-log.md` DL-86
  and DL-92 already request removal of unmeasured shared phrases and per-CLI
  non-auth lists on B. No new rule is needed for that existing difference.

## Distinguish the two findings

C74's Claude regression is an `is_error` envelope with an ordinary API failure
in `result`, plus unrelated text in `permission_denials.tool_input`. The U2b
correction preserves the original restricted non-auth input when authentication
needs original streams. That completed regression must not be relabelled as the
separate, pre-existing empty-answer denial-summary case.

The latter is recorded in workspace
`_runs/reviews/triad-auth-carriers-20261009-r3/minor-reproduction.json` and
`adjudication.md`. No supplied capture or cited vendor source establishes that
particular failure combination. It does not justify a new denial-specific parser,
classification rung, runtime audit or dedicated implementation unit.

## Disposition and next action (superseded by owner clarification below)

Defer the constructed empty-answer denial case as a recorded limit. Do not claim
it cannot occur, or that the synthetic reproduction proves an actual incident.
The leader's earlier assertion that this special-case implementation was necessary
was unsupported; treating all non-auth classification work as unnecessary would
also miss the independently confirmed DL-86/DL-92 source/spec difference.

The next bounded mapping is retained non-auth phrases against the existing
vendor contract, source/capture evidence and emitting CLI. Preserve measured
sentences; remove unsupported generic seeds or correct their CLI scope only after
that mapping. Do not guess AGY credit carriers, repeat completed authentication
work, reopen withdrawn model/effort research, or change host-native mechanisms.
This review records the scope decision; implementation and its verification have
not started. No shared-spec amendment or Claude implementation request is needed
for the constructed Claude-only case.

## Owner clarification: execution evidence precedes repair work

The owner rejected treating an in-progress spec difference as an urgent defect
and expanding implementation through imagined failures. This supersedes the
automatic-next mapping priority above, without deleting the historical comparison
or changing the existing shared rules. A listed difference is pending conformance
work, not proof of an incident or an instruction to add speculative classifiers.

The existing shared decision D-REPAIR-LOOP-KEEP-20261008 already defines the flow:
an actual failed run ending unknown/extraction-error supplies its own record to
the read-only repair analyzer; it proposes one supported phrase or exit-code
entry; deterministic code applies the proposal and reclassifies the stored record
to verify it, without another vendor call. Learned evidence can then enter the
common contract. Do not inspect successful-run logs routinely or manufacture
failures to populate an exhaustive classification table. Preserve established
measured classifications and separately authorized conformance work.

Official references checked on 2026-10-09:
- Gemini CLI troubleshooting: https://geminicli.com/docs/resources/troubleshooting/
  includes a CLI exit-code table and common messages.
- Claude API errors: https://platform.claude.com/docs/en/api/errors
  describes API status/type/message semantics, not every Claude Code CLI exit
  or emitted envelope.
- AGY headless mode: https://antigravity.google/docs/cli/headless/
  describes error output and an example; it is not an exhaustive message table.

No complete cross-CLI message/carrier catalog was established. The local
vendor-failure-lines contract combines observed runs and vendor-source evidence;
it is not a universal error dictionary. These references authorize no automatic
code changes, guessed carrier mapping, or fresh provider probes. This correction
changes local planning records only; no shared-spec or production edit was made.
