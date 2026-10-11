# Review read-boundary diagnosis

Date: 2026-10-09. Diagnostic record only; no correction or formal admission.
Product HEAD: `632f42633d3a92d6cb27168cd15c4d4debd8558c`; dirty work preserved.

## Independent investigation

Owner-requested fresh read-only children `read_boundary_policy_audit` and
`read_boundary_code_audit` used requested gpt-6.1-sol/high, fork_turns=none.
They separately investigated policy provenance and executable/test behavior,
without receiving each other's conclusions. Requested settings are not hidden
runtime attestation. No product edits, provider calls or test runs occurred.

## Findings

1. Canonical SKILL.md:39-44 accepts approved paths or categories.
   `bin/review_round.py:2250-2261` requires tracing affected unchanged consumers
   and permits declared categories/pathspecs. Exact-file-only is not mandatory.
2. Workspace `_runs/infra/20261009-spec-to-code/opus-default-r1/render-review.py:50-52`
   and its TASK add exact-file-only access and prohibit directories/wildcards.
   These restrictions are present in the actual R1 prompts. R1 lists 16 changed
   and 11 unchanged files, so it is not literally diff-only, but discovery is
   restricted to that inventory.
3. Concrete omitted dependency: approved `bin/review_adapters_v2.py:118` reads
   `bin/data/claude-capabilities.json` for minimum CLI version information;
   that JSON is outside the R1 inventory. Related installation/reference docs
   were also omitted. Not every additional file is therefore automatically relevant.
4. Exact lists already appeared in Google R1's model-review scripts. Google R3's
   reported directory-search violation led to stronger per-read validation and
   no-directory/wildcard wording for R4 (SoT:378-386). That wording recurs in
   Opus R1. Reuse is evidenced; the leader's motivation is inference.
5. R1 close-review.py:67-80 compares AGY paths against the exact inventory and
   treats the difference as violations, without semantic relevance assessment.
   Preserve its INCOMPLETE result and original evidence; do not retroactively
   rewrite the boundary or admit the round.
6. The canonical skill does not clearly distinguish a changed-file inventory
   from an inspection boundary. This is a recurrence-prevention gap, not proof
   that it required the leader's overly narrow choice.
7. Product development.md:23 broadly excludes governance. Workspace
   four-leg-formal-review.md:34-37 only prohibits exposing it merely to explain
   composition. The product wording does not clearly distinguish orchestration
   instructions from shipped skills/governing product documents under review.
   Local shared reference/review-rules.md:907-912 retains in-scope policy/prompt
   text as review material; remote adoption was not rechecked in this diagnosis.
8. The renderer checks nonempty boundary strings and hashes them; it does not
   validate their semantic adequacy. test_review_round.py around 3190, 3234 and
   3599 verifies prompt text, and test_review_conditions.py:39 verifies digest
   sensitivity. No related-file-discovery behavior proof was found by the audit.
9. antigravity_wrapper.py:156-189 explicitly disclaims read-coverage proof.
   Its limited DONE view_file telemetry does not cover every search/tool/family.
   A clean path comparison is not comprehensive access-compliance evidence.

## Correction candidates and meaningful verification

Treat diff/inventory as navigation. Approve relevant source, tests and product
documentation through bounded categories/pathspecs while retaining concrete
exclusions. Clarify the short canonical leader instruction and the ambiguous
product governance sentence. Keep historical failures, without promoting their
exact-list handling into a standing rule. Distinguish observed prohibited access,
semantic relevance, coverage gaps and source integrity during collection.

Behavior scenario: a changed file calls an unlisted helper in an approved source
category. The reviewer must discover and report a real helper defect. A correct
helper control must not produce a fabricated finding. Include excluded private
or peer-result references that must remain unread, an unavailable necessary
dependency requiring a coverage gap, and a shipped skill reviewed as data.
This tests decisions, not wording preferences. No such probe has run yet.

At the end of the diagnosis, R2 was not prepared/dispatched and its draft scripts
still contained the restrictions. The owner then authorized the correction below.

## Owner-authorized correction

The owner rejected leader enumeration/approval of related files and routine
post-review read-log auditing, then requested this correction before continuation.
The canonical skill's fresh baseline executor selected worktree discovery and
incident-driven log inspection correctly. That baseline is PASS, not a fabricated
RED; no canonical skill or product renderer modification is justified by it.

Changed the actual pending Opus R2 scripts: render/TASK now provide the product
worktree for related-source discovery with explicit private/runtime exclusions;
the collector no longer opens AGY read logs or compares paths with a file list.
The unused scope proposal was preserved as evidence and disabled so it cannot
restore the rejected mechanism. Historical rounds remain unchanged. Clarified
the project development instruction; no workspace policy/configuration changed.
Product runtime/skill delta: +0/-0; no new core mechanism or native-leg change.

Executed the collector with controlled producer/schema/render/fingerprint seams:
after correcting a fixture omission, all three cases failed at the unwanted
audit.jsonl read; after removal all three passed in 0.08s. Normal valid results
are admitted without a log, a negative verdict still blocks, and changed source
integrity still blocks. These tests do not claim live provider behavior.
Evidence: `_runs/spec-plan-20261009/read-boundary/collection-{red,green}.txt`;
the test is in workspace `_runs/infra/20261009-spec-to-code/`.

Claude source at clean `a91b436365385751beac674d21579ab91f4d8157` does not show
the same exact-file-only defect. Its AGY collector performs coded required
brief/patch-read and tool/hook checks, not approval of every source path. Those
controls remain unchanged. Shared R-PROMPT/C70/C71 clarify the common ambiguity
and request A's confirmation without claiming an unobserved A defect.
Shared main/PR12/PR13 refreshed at 3afc4d7/6a2883d/5c040ff before authoring.
Shared structural verification: 182 tests pass; one authoring map valid.
Fresh follow-up executor `read_boundary_green` selected worktree discovery and
normal collection without read logs. It found the unlisted pricing helper's
percent-scaling defect through the changed caller (10000 cents at 20 percent
produced -190000 rather than 8000). Its incident control selected targeted
diagnostic evidence only. Combined collector/review-round/review-condition
regressions: **191 passed in 23.74s**, exit 0; source skill validator valid.
All 16 under-test hashes were unchanged. Historical memory snippets concerned
generic executor lifecycle, not this scenario's expected decision or defect;
that exposure is disclosed rather than claiming an entirely history-free run.
Independent source review by `read_boundary_code_audit` found no concrete
regression. These are bounded behavior/source checks, not operational formal
admission. No provider review ran for this correction; U1b R2 remains pending.
Shared correction/handoff pushed to draft PR #13 at `cc10345`, confirmed remote
OPEN/draft with matching head. Final shared checks: 182 passed, one authoring map
valid. Full verification commands and limits are retained in
`_runs/spec-plan-20261009/read-boundary/verification.md`. No installation or merge.
