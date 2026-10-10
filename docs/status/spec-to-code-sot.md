# TRIAD Codex spec-to-code — execution SoT

Last updated: 2026-10-11 (Asia/Seoul).
Applies to the Codex host's shared-spec conformance work in this repository.
This is the single live progress record. The shared specification remains the
behavioral authority; this document does not override it or authorize publication.

## Core principle: develop the specification as well as the implementation

This work builds and validates the shared specification; it is not mechanical
translation of an assumed-correct document. If Codex code is deficient, fix it.
If the shared specification is ambiguous or deficient, clarify it before the
dependent implementation. Check Claude code as evidence without presuming it
correct. Never implement a guessed output location or other unobserved shape.

For every disputed item, identify which claims the evidence supports: a Codex
implementation defect, a Claude implementation defect, a shared-spec defect,
or an unmeasured fact (more than one may apply). Verify the instruction itself
against intended common behavior. Record the rule/case, both relevant code
paths, evidence and decision. An existing rule is not proof of its correctness;
an existing implementation is not authority to silently redefine that rule.
Resolve a spec defect through the shared authoring process before coding the
dependent behavior, so both hosts can implement the same clarified contract.

## Goal and boundaries

- Make common, non-native behavior follow the same shared specification on both
  hosts. Each host owns its native leg: spawning, presets, model/effort choices
  and internal implementation. Only the shared input/result boundary is common.
- Work one coherent specification item at a time. Check uncertain instructions
  against the rule, case, current code and evidence before implementing them.
- Read Claude source as evidence, not as the answer. If Claude's claim is weak,
  request exact commits, code and tests through the shared spec. If both hosts
  are deficient or the contract is ambiguous, resolve the shared spec first.
- Owner 2026-10-11: do not wait for Claude maintainer replies. Verify claims
  independently from the current shared specification, relevant source, primary
  documentation and bounded execution evidence; continue authorized work and
  share established differences asynchronously. A missing reply is not a gate
  or agreement. An actual unresolved design decision still goes to the owner.
  This does not waive required independent review or external setup approval.
- Both hosts are implementing concurrently. A spec-only or unimplemented item
  is pending work until evidence establishes a defect; pin each observation to
  current commits and relevant dirty files rather than treating old OPEN rows
  as current diagnoses.
- Prompt work targets contextual wrong decisions with minimal instructions.
  If discussion repeats over grammatical nuance, use fresh Luna/high scenario
  and contrasting-control probes, hiding expected answers and review history.
  Correct decisions end wording iteration. Owner 2026-10-09: keep prompt review
  to two or three passes focused on substantial defects and observed behavior;
  the owner will review wording later. Do not add phrase-pinning tests solely
  for wording review. Demonstrated functional failures still require correction
  or escalation. Record explicit owner dispositions separately from verdicts.
- Preserve intentional dirty work in place. No reset, clean, stash, discard or
  separating checkout. Existing authority and formal review gates still apply.
- Continue authorized bounded corrections autonomously. If a substantial design
  change is needed, or a necessary decision cannot be supported by the available
  evidence, stop that dependent work and ask the owner with the concrete choice,
  evidence and impact. Continue independent work that does not pre-decide it.
- Owner reaffirmed 2026-10-10: continue the authorized implementation through
  completion without routine stage-by-stage permission stops. When design or
  CLI usage is doubtful, check Tier 1 primary evidence and web sources as needed.
  Substantial design changes still require stopping and asking before edits.
  Keep review points/diff/related-code discovery central; prefer existing logic
  over new security, cwd or replay machinery without an evidenced need.
- Do not invent vendor output shapes or exhaust credits to manufacture evidence.
  Distinguish classifier tests, wrapper-path tests and observed vendor behavior.
- Product merge, installation and release require their applicable owner approval.
  Prior approval to publish spec draft PR #13 does not grant those permissions.

## Start or resume

1. Read this document and the repository's `AGENTS.md` and development contract.
2. Inspect the live branch, HEAD and dirty state. Compare with the recorded basis;
   retain previous evidence and explain any changed basis before reusing results.
3. Read the current stage's linked rules, cases and evidence only. Historical
   checkpoints are evidence, not a reason to restart completed work.
4. Brief the owner in Korean: current stage, confirmed issue, next action and
   intended impact. Continue already authorized work without repeat approval.
5. Update this document after a meaningful step, a stage transition, new evidence
   or before handing off. Record a concrete next action even when work is blocked.

## Current position

**Owner proceeded2026-10-11: bounded vendor-invocation simplification design;
U6b/U9 expansion drafts remain on hold and must not resume automatically.**
Read [the current audit](2026-10-11-vendor-responsibility-audit.md). The owner
states vendor CLIs manage their execution/handles. Reassess code and shared
rules from that boundary before adding wrapper mechanisms. A reproducible
failure in wrapper-added machinery is not proof that the machinery is needed.
Retain TRIAD's review inputs, result identity, agreement and exact own cleanup.

Runtime HEAD remainsb6868d8. All previously started U9 diagnoses and the single
RED ended; source fingerprint matcheda472f9172ced0ceca437398eb30398e35df12a2c69fca06300c0170b3e128238.
RED17failed/3passed includes two mixed Gemini fixture failures. No product edit,
GREEN or new formal review. Outside-source U6b/U9 drafts are evidence-only.
Current plan: [vendor invocation boundary](../superpowers/plans/2026-10-11-vendor-invocation-boundary.md).
Fresh main remains3afc4d7; PR13 has no newer A reply after6100596687; read-only
A remains1de943af. Google, fresh Astra/high and Claude/opus/xhigh diagnoses all
completed and recommend owned stream files. Google/Codex recommend direct-child
supervision; Claude's timeout-group-retention suggestion has no measured vendor
requirement and is not selected under the owner's descendant responsibility
direction. Invalid UTF-8 rejection remains; it needs no new owner choice.
Neither diagnosis nor a synthetic test is formal admission.

Standard-library spike:2MB exact input succeeds; inherited-output fixture takes
1.548s with communicate versus0.048s with files. Both accept early stdin close.
Actual installed Claude file-stdin marker probe returns exact marker/exit0;
no lifecycle, cancellation or effective model/effort identity claim. Evidence is
workspace `_runs/infra/20261011-vendor-boundary/`.

The owner was asked one concrete design choice: redefine stdin complete as
exact full input made available, dropping the existing large-prompt early-close
BrokenPipe detection, or preserve that monitoring. The overall reduction is
authorized, but this newly identified observable difference is pending. No
dependent normative or runtime edits before the answer. The shared decision is
`decisions/2026-10-11-vendor-invocation-boundary.md`, published as7d731ef and
shared in PR13comment6101372915 (read back); its authoring check passes1/1.
Only design/progress documents changed; every started provider/probe is terminal.
Settle the choice and amend shared rules/cases before RED/code. The diagnosis
fingerprint was after dispatch; subsequent leader changes were excluded design
documents only. No formal integrity or whole-worktree-equality claim is made.
Main merge needs scenario-based review and separate approval. The whole-task
hook remains while work is unfinished.

### Last completed implementation: U7

**U7 implementation and approved two-profile setup complete.
Final dedicated GREEN:304affected/2364full passed,4skipped. Fresh R3 all four
SAFE with ROUND_INTEGRITY_OK; custody exported and exact stages removed.
Source47a1503 and sharedc66e515 are pushed; PR13comment6100271567
shares completion. Shared authoring1/1 and182tests pass. Its former U6b/U9 next
steps are superseded by the owner-directed responsibility audit above.**

Owner2026-10-11 explicitly proceeded after the exclusion-profile live results and
the proposed global-settings removal. The current unit plan is
[U7 profile/settings](../superpowers/plans/2026-10-11-u7-profile-settings.md).
New shared R-CONTAIN/R-REVIEW-WEB and C6/C68/C72 are07ee684; authoring1/1 and182
tests pass, remote matched. PR13comment6099196142 requests A review; no newer A
reply at the start, and no reply is required to continue B verification. Main
remains3afc4d7; read-only A1de943af has no transaction.

Fresh dedicated RED-valid16failed/2passed reproduced settings mutation during
provider entry; later concurrent-writer checks were unreached. Initial RED was
confounded by a deliberately invalid legacy lock-timeout setting; preserved and
not treated as mutation proof. Candidate removes global transaction/lock/restore/
heal code, adds exclusion to existing profiles, applies them to raw read-only
without autoapproval, and requires CLI>=1.2.1 on read-only calls. Permissive raw
and optional project semantics remain separate. Requested web only checks known
existing denies/malformed settings; old residue stays. The two source profiles
are installed after explicit approval. Production shrinks by roughly500lines; no new hook/audit.
Leader diagnostics324passed/4skipped; documentation assertions corrected,
42distribution tests pass. First dedicated GREEN:366focused passed/4skipped;
full2354passed/4skipped and3failed. All three were stale test expectations of
removed guard data/restore guidance. Two test modules are corrected, runtime
unchanged. Final fresh dedicated GREEN:413focused and2357full passed,4skipped;
bootstrap syntax, all four skill validators and diff check passed. Source/log
integrity and exact temp cleanup passed. Host macOS26.6.2/arm64/Python3.12.13;
Ubuntu not run. Failed evidence is retained. No unit admission.
Owner2026-10-11 authorized the proposed two-file update. Both profiles now match
source bytes with `excludeDefaultComponents: true`; known permission-setting
hashes are unchanged. Receipt: `profile-install-receipt.json` in the evidence root.
R1 completed with valid four-leg results and matching integrity: Pro/Flash SAFE,
Opus/Astra NOT-SAFE. Current documents and rendered prompt overstated removed
global denies/MCP enforcement. These claims are corrected, the v2 receipt floor
is aligned to1.2.1, and timeout/profile-drift evidence coverage is restored.
Dedicated correction RED:5failed/3passed; both timeout controls already passed,
so no timeout runtime defect is claimed. Shared0d7073d clarifies MCP prohibition
versus an unproved mechanical guarantee; PR13comment6099813534 shares it.
R1 custody exported and exact stages removed. Fresh correction GREEN passed:
584focused/2362full,4skipped; bootstrap, four validators, diff check, source/log
integrity and exact cleanup passed. R2 then returned all four SAFE with integrity matched. Its fixture-isolation
Minor was reproduced: web tests read ambient settings and failed on a synthetic
URL deny or malformed JSON. The fixture now pins its invocation-owned settings
path; product code stays unchanged. Existing success/profile-drift coverage now
asserts stored classification and stdout. Fresh GREEN/R3 supersede R2 admission. The installed profiles need no further change.
Evidence: workspace `_runs/infra/20261010-spec-to-code/u7-current-research/`.
Final fixture GREEN:304affected/2364full passed,4skipped; bootstrap syntax/four
validators/diff check and source/log integrity pass. Fresh R3 all four SAFE,
ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK. Six nonblocking suggestions have
recorded dispositions; no further wording/import/helper cleanup backlog.
Runtime/tests/product docs remain the verified R3 bytes. No full plugin install,
revision adoption, merge or release. Profile setup was separately approved and
completed. U7 is complete; whole-task startup hook remains until U10 cleanup.


Source `a4fd93c6283349df67bdb5c4d718a52144ac4547` is pushed and remote-matched.
Shared completion `c55dca6` records C4/C5 fallback evidence separately from
U6b/DL-77/C69. Shared authoring1/1 and182tests passed. Remote main remains
`3afc4d7e931e55d601dd74877bdbe65e610a8e59`; PR12 inspected head is0ccc7c1.
At U6a publication, PR13 had no newer A reply through6096424215 and read-only A
was e9960053. Latest research refresh: PR13comment6097553901 answers U6b;
PR12 is d805b50, A404eb0ab is clean, and remote main remains3afc4d7. The U7
research source fingerprints matched; B runtime was not changed.

U6a now requires actual fallback allocation proof, preserves unmarked residue,
records deletion start before removing anything, resumes only an unchanged
remainder and removes proof last. Overlapping sweeps serialize on the existing
proof descriptor; busy allocations skip. Own-call failed writes remove only
their own empty new directory. Production+160/-19,net141,one file; no new public
cleanup service. [Unit plan](../superpowers/plans/2026-10-10-u6a-fallback-ownership.md).

Final dedicated GREEN-concurrent:340affected,29/29standalone,2347full passed,
4skipped and all four validators. Source/log integrity and exact fixture cleanup
passed. Fresh `triad-fallback-ownership-20261010-r3`: all four SAFE,
ALL_SELECTED_APPROVED / ROUND_INTEGRITY_OK; adjudication, custody export and
exact stages cleaned. Runtime/tests still match those verified bytes. macOS
Python3.12.13; Ubuntu NOT RUN. Earlier failed reviews and ineffective first
concurrency test remain evidence, not current approval. Optional detailed
residue diagnostics remain a disclosed nonblocking limit. The verification
guide now requires an invocation-owned TMPDIR before Python starts.

PR12 dispositions: DL-149 paid-tier advice is absent from searched shipped B
Markdown. DL-150's stale relative-prompt CHANGELOG sentence is removed; current
process-cwd behavior was already implemented/tested. DL-151's stream fold is
unmeasured; no length cap or output workaround is added. DL-123..126 introduces
no B port: current common behavior already agrees, while A's internal census,
stream and audit changes remain A-owned.

Earlier remaining actions (execution suspended by the current audit above):

1. U6b: PR13comment6097553901 answers the enclosing log-folder proof question;
   PR12 d805b50 adds DL-152 and its R-CLEANUP clarification. Compare that text
   and current source before declaration/migration code; it is no longer an
   unanswered A request. No per-file-marker or public deletion API is implied.
2. U9: independent diagnosis and bounded correction planning for DL-88. Actual
   shared-driver fixture returns the answer in the control; a BrokenPipeError
   on its terminal diagnostic instead raises without a RunResult. No provider
   or real stderr was changed. Current A already drops failed diagnostic writes;
   it was read, not executed or copied. Shared `c55dca6` records the evidence.
   Other old lifecycle claims remain classified individually, not assumed bugs.
3. U2 evidence reconciliation and U10 final integration remain. U1T and U6a are
   complete; U8 and unused Claude-agent work remain withdrawn. Keep the task hook
   until whole-task completion and its explicit cleanup checklist.

No installation, adopted revision, merge, release or whole-task completion.

### Earlier U1T/U6a checkpoints (historical; current position above)

At B5f5dda5b plus the reviewed candidate, model values remain one opaque option
value through the Python-wrapper and affected Google parsers. AGY changes only
option-shaped pins; ordinary/legacy spelling remains. Both v2 receipt builders
match. Three wrappers refuse non-None non-string parsed models before I/O,
covering the reproduced old-CPython loss of literal `--`. Production delta:
+17/-9, net8, six files. Native model/effort/spawning and user settings unchanged.
Unit plan: ../superpowers/plans/2026-10-10-u1t-model-transport.md.

Final dedicated GREEN-compat:82 affected current-parser tests and46 official
CPython3.12.1 argparse-module tests passed onPython3.12.13; four validators pass.
The full2326passed/4skipped run is on identical production, before the final
test-only correction. Source/log fingerprints matched and exact fixture cleanup
completed. Do not call the module probe a full old-interpreter run. Ubuntu NOT
RUN; hidden runtime settings UNEXPOSED.

Fresh complete `triad-model-transport-20261010-r3`: all four SAFE,
ALL_SELECTED_APPROVED / ROUND_INTEGRITY_OK. One future encoder-drift suggestion
is nonblocking: current code and both-route transport tests agree, so no new
abstraction or required backlog. R1/R2 findings, failures and custody remain;
their approvals were not reused. R3 adjudication/export/exact stage cleanup
complete. Evidence: workspace `_runs/reviews/triad-model-transport-20261010-r3`.

Shared R-MODEL/C18/C34 clarification is d082a60. PR13 was refreshed through
6095707704, with no newer A reply. Remote main3afc4d7 and PR12 11934f11 were
fetched again; current read-only A0be173bf is clean and its intervening commits
change documentation/comments, not relevant model or cleanup runtime behavior.
A's old-parser handling remains its own follow-up, not a B blocker or native port.

U6 research is complete: the existing fallback sweep deletes an unproven old
prefix-matching directory in an isolated synthetic fixture. Three independent
diagnoses confirm the path. Shared ba04c60 adds the C4 boundary and aligns C69
and schema age descriptions with R-CLEANUP's existing named-close/resumption
exception; authoring1/1 and182tests passed, pushed and verified. PR13 comment
6095933437 shares exact evidence/sequence and was read back. No real system-temp
sweep or actual user-data-loss incident is claimed.

U1T sourceed8b76f and sharedd3a4412 are pushed and remote-matched; PR13
comment6095971207 reports completion. Next: U6a's existing fallback
allocation/sweep ownership correction. U6b separately owns declared roots/floors
and normal sweep/cap/archive migration. Use the bounded research/design record
at workspace `_runs/infra/20261010-spec-to-code/u6/disposition.md`; no new generic
deletion service/API or A-native port. Keep proven review export/identity/subset
cleanup. Source tests must isolate their temporary base. U6a plan:
../superpowers/plans/2026-10-10-u6a-fallback-ownership.md. Fresh dedicated RED
completed16failed/37passed without errors before product edits. Fresh GREEN
completed334affected,29/29standalone and2341full passed/4skipped, plus all four
validators. Scoped source and captured run logs matched; exact fixture removed.
Initial RED's fixture teardown errors remain recorded and were corrected before
product edits. Production+144/-17,net127,one file. Fresh review
`triad-fallback-ownership-20261010-r1` follows. No new public deletion API or
complete declaration-conformance claim. PR13 rechecked through6095971207;
no new A reply.

Independent U7 research: shared04cf1a7 records the provider-free two-folder
synthetic settings spike. The existing guard exposes its temporary settings to
the second folder and restores over that fixture writer's new value on exit.
No real user setting or provider was touched; no live incident is claimed.
Replacement selection still requires independent diagnosis and Tier1 evidence;
a substantial containment/design change returns to the owner before code.

U6a R1 all-four SAFE/matching integrity; Claude's four Minor findings were
adjudicated and exact stages cleaned. Add own-call empty-folder rollback when
the fallback leaf write fails; strengthen symlink/proof-failure tests and cover
partial start data. Clarify retained-residue docs. Refute the claimed real-temp
full-suite sweep: the actual runner sets an owned TMPDIR for every subprocess.
Fresh RED-rollback reproduced1failed/55passed; source/log integrity and cleanup
passed. The eight-net-line own-call rollback is implemented; fresh GREEN and
complete R2 follow. Final GREEN-rollback now completed337affected,
29/29standalone,2344full passed/4skipped and four validators. Source/log
integrity and exact fixture cleanup passed. R2 reviews current bytes; R1
approval does not cover them. Shared39e1fef and
PR13comment6096231782 record the bounded follow-up before product edits.
PR13 comment6096200341 shares U6/U7 evidence and U6b's sharedc5b8bfe ownership
mapping question. PR12 now0ccc7c1 adds DL-149/150/151; B's CHANGELOG has the
stale relative-prompt sentence, to remove after this unit. No paid-tier advice
found in searched shipped Markdown; no new AGY length workaround is selected.

U6a R2 completed with matching integrity, three SAFE and native NOT-SAFE.
Fresh dedicated RED-concurrent-valid1failed/18passed reproduced replacement of
a durable deletion-start inventory by an overlapping stale reader and deletion
of a changed repair remainder. Earlier RED-concurrent19passed missed the
interleaving because the proof age had refreshed; retained as invalid RED.
Shared dc48e3e adds the existing C5 boundary, authoring1/1 and182tests pass;
PR13comment6096424215 requests review before the correction. R2 adjudication,
export and exact stage cleanup completed. The bounded fix reuses the existing
nonblocking lock on the proof descriptor before reading, skips a busy allocation
and rechecks identity. Added leaf-symlink target-survival controls and corrected
the stale caller comment. Fresh GREEN-concurrent passed340affected,
29/29standalone,2347full/4skipped and all four validators. Source/log integrity
and exact fixture cleanup passed. Production+160/-19,net141,one file; complete
R3 completed all-four SAFE / ALL_SELECTED_APPROVED / ROUND_INTEGRITY_OK.
Adjudication/export/exact stage cleanup completed; runtime/tests stay unchanged.
Optional per-candidate diagnostic detail is retained as a nonblocking limit;
the generic verification guide's TMPDIR requirement will be clarified in a
documentation follow-up. These results cover the current concurrency correction.

U7 diagnosis is complete across Claude/Google/fresh Codex. One actual CLI probe
using the existing profile without B's settings transaction read/listed the
owned fixture and wrote nothing; no write call was attempted, so enforcement
remains UNVERIFIED. Settings/profile matched and exact fixture was removed.
Evidence: workspace `_runs/infra/20261010-spec-to-code/u7/disposition.md` and
`profile-probe/receipt.json`; shared dc48e3e records the same facts. The owner
has been asked to choose the simple existing-profile/plan/sandbox/integrity
posture with an explicit pre-execution-prevention limit, or a project-based
permission prerequisite. Raw migration and old-backup preservation are included.
Neither is selected; no U7 product edit while that design question is pending.
Initial U9 current-source mapping is read-only research, not completed checks:
workspace `_runs/infra/20261010-spec-to-code/u9-initial-mapping.md`.

Other remaining groups: U2 evidence reconciliation, U7 measured settings
isolation, U9 remaining-case mapping and U10 integration/final reconciliation.
U8 is withdrawn. Unused Claude agent research is removed, not deferred.
Completed U5a/U5b/U3e evidence remains in their linked plans and historical
checkpoints below. Whole-task hook stays until all work and its final cleanup
finish. No installation, adopted revision, merge, release or whole-task claim.

### Earlier U3d checkpoints (historical; current position above)

PR13 was checked again through comment6093171510; no new A reply. U3d completion
is published at shared73e6613 / PR13comment6093314527 after authoring1/1 and
182tests passed; A's CRLF correction remains open. Main
freshly fetched3afc4d7, PR12head8ec55d3, read-only A bc8a8a74. Owner explicitly
requests continued work and a push. After U3d verification/review, commit/push
the attributable accumulated candidate as a WIP checkpoint, preserving unrelated
Oct2 untracked records and .DS_Store. No install/merge/release or overall-complete
claim. Plan: ../superpowers/plans/2026-10-10-u3d-agy-answer-truncation.md.
Initial RED included a test-only auth-fixture error; corrected raw0 to raw1.
Fresh final RED4failed/514passed/4skipped, all controls passed. Logical-line raw
answer check implemented; valid schema and tool/web channels unchanged. Fresh
GREEN564affected/2264full passed,4skipped; four validators, source/log integrity
and exact fixture cleanup passed. Review triad-agy-answer-truncation-20261010-r2
all-four SAFE (1 nonblocking findings), matching integrity; custody exported,
exact stage/cwd removed. Owner-authorized accumulated WIP implementation checkpoint 060edf183cc2d400ade6c86ec386313ed7043e05
was pushed and matched origin/codex/opus-5-5-default. Shared completion is
published on PR13; see its latest comment. Whole-task hook stays. Remaining:
U1T, U2 evidence mapping, U3 schema assessment, U5, U6, U7 and U9; U10 is the
final reconciliation/integration gate. These are work groups, not seven
demonstrated bugs. U8 remains withdrawn. No install/merge/release.

U3d first GREEN:518affected pass; full2259passed/4skipped/1failed because a stale
distribution-doc assertion forbids truncated-answer, now an active shared token.
Removed only that prohibition; no runtime change. Fresh GREEN includes the
distribution test module. Initial failure and unchanged source/log receipts stay
retained; this is a test-contract update, not a new behavior or design decision.

U3d final GREEN560affected/2260full passed,4skipped and four validators passed.
R1 then returned NOT_APPROVED with matching integrity: native Codex found an
LF-only matcher that misses CRLF. Leader reproduced the exact source regex;
read-only A has the same gap. Shared7902ffa/PR13comment6093171510 adds C43 CRLF
controls and A follow-up. Claude's Minor identifies a tool-control fixture shape
error; corrected to the existing step_type=tool/tool_name shape in the required
test revision. All four results retained; custody exported and exact stage/cwd
removed. Fresh CRLF RED, minimal matcher correction and a complete R2 follow.

Fresh CRLF RED4failed/560passed/4skipped confirmed both marker units on raw and
stored replay. All controls pass; source/log integrity and exact cleanup pass.
Matcher now uses fullmatch on response.splitlines(), retaining original bytes.
Fresh GREEN and full R2 completed as recorded above; R1 admission was not reused.
R2's one nonblocking Unicode-line/digit suggestion was checked against source.
No observed AGY defect or exhaustive alphabet restriction was established; keep
the simple implementation without new spec restrictions or speculative backlog.

Earlier U3c checkpoint: sharede292e5c, PR13comment6092831650; main freshly
fetched3afc4d7, A read-only bc8a8a74. U3c plan:
../superpowers/plans/2026-10-10-u3c-agy-network-carrier.md. Shared C43 positive
and boundary cases precede code; authoring1/1 and182tests pass. Fresh dedicated
RED completed3failed/492passed/4skipped, source/logs unchanged, exact cleanup.
Minimal typed classifier forwarding/rung implemented. Fresh GREEN495affected/
2237full passed,4skipped; four validators; six hashes,HEAD/status and ten source
logs unchanged, exact fixture removed. R1 all-four SAFE/two nonblocking Minors; matching
integrity; custody exported and exact stage/cwd removed. Evidence:
_runs/spec-plan-20261010/u3c/green and workspace _runs/reviews/triad-agy-network-carrier-20261010-r1.
Shared completion published after authoring1/1 and182tests passed; checkout
clean. No pending required owner choice. The two Minors are retained: no
speculative defense for an unmeasured reflected-error combination; qualify the
pre-existing README retry wording in U5. Whole-task hook stays active.

A reply6092564483 agrees with the emitted-answer-channel interpretation and
DL-101 scope. Sharedca64d1d updates R-CLASSIFY/C43/DL-102; authoring1/1 and182
tests pass; PR13comment6092582472. A's current response-first refusal is an A
fact, not a B requirement. Owner says ignore an AGY web-search bug if implicated;
the actual reply concerns terminal answer selection, so no web-tool scan,
workaround or retry is introduced. Truncation code remains a subsequent unit.

Owner corrected passive waiting on A's truncation explanation. B independently
checked official AGY headless docs, A's actual channel selection and its retained
7.8KB structured /26–27KB plain-output reports. These support selected-answer
channel semantics, not discarding valid structured_output because incidental
response has a marker. Historical size observations do not establish a universal
current limit. Evidence/limits and proposed interpretation are shared in the
remaining-carriers note; A review is coordination, not a development prerequisite.
No fresh vendor truncation capture or recursive JSON-field scan is claimed.

Published completion: U3b sharedeb78ca9/PR13comment6092244826; U3a
sharedc495b1b/PR13comment6092450939. At that earlier handoff, shared was clean at65d2bd9 after
authoring1/1 and182tests passed. B HEAD632f426 and intentional dirty candidate
remain; diff check passes. Both review rounds completed/exported/cleaned.

Remaining U3 assessment shared65d2bd9, PR13comment6092478935:
`decisions/2026-10-10-u3-remaining-carriers.md`. A1ea9cb3e checks its response
truncation marker before consuming a separate structured_output; B's schema
path emits the latter. Initially requested A clarification of which answer channel
the common rule governs; direct B investigation above supersedes passive waiting. This is source analysis,
not a live failure; do not manufacture one or infer recursive JSON-field scans.
Independent next executable assessment: DL-101 measured typed network-error
carrier, preserving auth, exit-map and class priority without exposing unmeasured
quota placement. U3c now selects the bounded typed classifier argument/rung. Remaining U3
schema compatibility still needs current-route evidence, not A failure inference.
Whole-task hook stays active; U8 remains withdrawn; no install/merge/release.

U3a R1 has one nonblocking Minor: the shipped AGY skill could qualify its normal
telemetry description with the ERROR-only recovery exception. README EN/KO
already do. No leader-action defect; recorded in existing U5, no production fix.

U3b plan: ../superpowers/plans/2026-10-10-u3b-agy-turn-timeout.md. Shared9e03c6c
and PR13comment6092051096 recorded the settled DL-102 carrier before code.
Fresh RED4failed/412passed/4skipped. One 13-line AGY carrier branch and token
comment implement ERROR/empty response/raw1/typed error prefix -> vendor-timeout65.
First GREEN415passed/4skipped/1failed because the token-contract MAP_ONLY set
still prohibited emission; corrected that test, preserving exclusion from repair
vocabulary. Final fresh affected416passed/4skipped, full2171passed/4skipped and
four source validators passed on macOS26.6.2 arm64/Python3.12.13. Seven hashes,
HEAD/full status and ten source logs unchanged; exact temporary root removed.
Evidence: _runs/spec-plan-20261010/u3b/green-final/. No live vendor replay or
Ubuntu execution. Review triad-agy-turn-timeout-20261010-r1 is complete: all four SAFE,
ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK; fingerprint71d7f65c986ca4883344f02402bc7911a4a1366fd80ead9de72bfb2b66c0f2ab.
One optional Minor has no current defect; retained as advice. Custody exported,
exact stage/cwd removed. U3b sharedeb78ca9 and PR13comment6092244826 published the verified candidate.
U3a RED12failed/444passed/4skipped; minimal ERROR-only correction implemented.
First GREEN found two test expectation errors (schema-fail is66); corrected.
Final GREEN458affected/2213full passed,4skipped; four source validators passed,
source/logs unchanged and exact temporary tree removed. U3a R1 all-four SAFE, ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK;
digest350ee9e1da26abf02c9ce0d5d56bfe6667eac0e8c572e92b2d36857d881d8ee3,
fingerprint1698369b4d63888828a330d01fb4a2e6585f819d97062f51245875b7be7fe4ec.
Custody exported and exact temporary stage/cwd removed. Read-only A1ea9cb3e was checked: finish ordering,
integer-index terminal resolution and denial-head contract remain. DL-102 truncation remains open.

A reply6092107935 accepted U8 and U3b; its F3-c plan revision69fb82fd was checked
directly (implementation remains A Phase7 work). For U3a, A confirms measured
denial-head matching is separate from structured finish success/order, B retains
nonzero classification, and the September raw log expired. Sharedf332ab8 clarifies
R-CONTAIN/C23; authoring1/1 and182tests pass. Reply posted at
https://github.com/codefoundry-io/triad-dispatch-spec/pull/13#issuecomment-6092152745.
The two admission questions are resolved, not new owner decisions. No Claude
Code permission-rule port follows from A's host-specific observation.

Owner scope update, 2026-10-10: U8 installation coexistence is WITHDRAWN as an
operator-managed rare case (D-U8-WITHDRAWN-20261010). Its investigation, changes,
tests/review and dependencies are removed from the active plan, not transferred
to another unit. Existing installation behavior and tests remain. Remaining
roadmap: seven assessment/implementation units (U1T, U2, U3, U5, U6, U7, U9)
plus U10 final reconciliation. This is not a count of confirmed defects.
Shared48fba4b records the owner decision and changes B's DL-105/108/109 status
cells to WITHDRAWN. The first spec check caught stale status cells; after fixing
them, authoring1/1 and182tests passed. Normal push and PR13 handoff complete:
https://github.com/codefoundry-io/triad-dispatch-spec/pull/13#issuecomment-6092020274.

U3a evidence assessment before the reply (historical):
../superpowers/plans/2026-10-10-u3a-finish-resubmission.md.
PR13 rechecked through latest own6091822527: no new A reply beyond6088729953;
inline review comments empty. Shared main freshly fetched at3afc4d7; read-only A
now a5456b1324670117c445fef96d5b61f49c8955b6. B HEAD632f426 and intentional
dirty work preserved. U4e remains complete; no product edits in this assessment.

DL-113 core recovery decision is settled. B provider-free constructed contract
characterization confirms SUCCESS ok0 versus ERROR failed-then-successful finish
vendor-error65/withheld; missing success also refuses. Raw1 resubmission is
unknown1/withheld under the current early classifier. This is not a vendor replay
or formal dedicated RED. Source HEAD/status/two hashes unchanged and exact
temporary fixture removed. Evidence: _runs/spec-plan-20261010/u3/resubmit-characterization.json.

Actual A adddir capture confirms finish/DONE and a final structured_output;
Aprime/hookdeny captures expose generic TOOL_ERROR for permission denial.
A's _agy_step_denied reads error.message, while R-CONTAIN says structured-only
resubmission judgement. Clarify the scope of that wording and whether A's broader
nonzero admission is required on B before dependent implementation. The original
September failed/resubmitted run-log is absent at its recorded path; retained
stderr/recovered answer and A t15 axes30-37 were read. A runtime NOT RUN.

Shared8ea84eaf22d2613c9c1f8a7a3f42c5288f54d7e2 published the evidence/limits;
authoring1/1 and182tests passed, normal push complete, shared checkout clean.
Questions and the concrete B boundary proposal are posted at
https://github.com/codefoundry-io/triad-dispatch-spec/pull/13#issuecomment-6091931426.
Current next action: assess remaining U3 items (DL-101 network carrier, DL-102
truncation and current-route DL-103 schema compatibility) against spec/current A
and B before each dependent change. U3a and U3b are complete bounded candidates. No routine successful-run read audit, nonzero classifier override
or paid failure generation. Whole-task hook stays; installation/merge/release
remain separate.

### Previous completed unit: U4e

Completed bounded plan: ../superpowers/plans/2026-10-10-u4e-retired-task-code.md.
Shared main freshly fetched at3afc4d7; last A reply6088729953. Host-specific
DL-91 disposition published at a41769c, PR13comment6091668144; authoring1/1 and
182shared tests passed. Read-only A now3bb4f284 has no fanout helpers but retains
its active Codex CLI extractor. B has no such wrapper. Preserve task-blocked65,
native dispatch, callable retry parameters, locking and historical cleanup.
Fresh RED produced12failures/443passing controls, unchanged source/log receipts
and exact fixture cleanup. Failures establish retired phrase emissions, accepted
retired proposals/extension patterns and C8 membership drift. No new vendor case.
The exact C8 fixture is refreshed from main, not whole-revision adoption.
Evidence: _runs/spec-plan-20261010/u4e/red/. Removed only inventoried retired
engine pieces: production+7/-189(net-182), tests+42/-1, fixture/docs+9/-14.
Fresh affected GREEN455passed, full2152passed/4skipped and four validators passed
on macOS/Python3.12.13. Seven hashes/HEAD/status and ten source logs unchanged;
exact fixture root removed. Main3afc4d7 re-fetched before review. Other-platform
execution NOT RUN; no installation/merge/release or whole-revision adoption.

U4e R1 all-four SAFE, ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK; digest
25a3086321541c0271b967e5d6bd00178e40fbb4727f13aeead3a34ccf6bc486,
fingerprint293bf2e586dd096b7341af91c41681a70b5176cd2a04a1128547a07e945487aa.
All producers terminal, custody exported and exact stage/cwd removed. One Minor:
old JSONL/last-message and historical task-cleanup comments are stale; runtime
is correct and retry parameters stay by the explicit compatibility boundary.
Record comment debt without another wording-only implementation/review loop.
No post-review product edit. Evidence: workspace _runs/reviews/triad-retired-task-20261010-r1/.
Shared389071a updates DL-91/C8 evidence; authoring1/1 and182tests passed, push
complete. PR13 issue/inline/review comments checked again: no new A reply beyond
6088729953; no new design disagreement or unanswered question.
Completion reply: https://github.com/codefoundry-io/triad-dispatch-spec/pull/13#issuecomment-6091822527.

Next: resume U3 at DL-113's measured same-run finish resubmission. Read the
existing spec/capture and current A/B stream interpreters before choosing a
bounded change; use only demonstrated structured fields. Do not manufacture
vendor failures, expand an error catalog or infer AGY credit-message carriers.
U4's bounded removals are complete, but broader C43/C76/runtime and plan items
remain separate. Whole-task hook stays until the entire task is complete.

### Previous completed unit: U4d

Current bounded plan: ../superpowers/plans/2026-10-10-u4d-dead-classifier-code.md.
Shared4072d2c/be18058 clarifies DL-106 before dependent deletion: three zero:ok
maps and unused private _json_len may go; B's direct-call AGY fallback and callable
compatibility remain. Authoring1/1 and182shared tests passed; normal push complete.
Fresh baseline393affected tests/four validators passed, stable source/logs and
exact fixture cleanup. Removed only those definitions/selection and stale
docstring text in bin/_common.py. First GREEN392passed/1failed: the existing
token-contract test dynamically constructed the deleted map names. Corrected
that membership assertion to the retained AGY map; no production correction.
Fresh final GREEN393passed and four validators, three hashes/HEAD/status and
ten source logs unchanged, exact temporary root removed. Baseline measured two
hashes; final additionally hashes the updated test. No new test, vendor behavior,
public interface or host-native change. Prior full2143/4skipped remains U4c-byte
evidence; this unit did not rerun the full suite. Production+3/-43(net-40), test+1/-2.

U4d R1 all-four SAFE, ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK; digest
7a9d4deec112a34efeb14196624ab35091813c6bab199325afbaf10d15f21a01,
fingerprint529c84290a1912e9a6abf8caaaea633a4b73ac9ea3440f7f58e30557bd7258cd.
All producers terminal; custody exported and exact stage/cwd removed. Three
Minor findings adjudicated: stale comments and an optional redundant guard are
nonblocking; the AGY reachability/coverage claim is corrected below. No product
edit after review. Evidence: workspace _runs/reviews/triad-classifier-removal-20261010-r1/.
Shared completion c25da30 pushed after authoring1/1 and182tests; PR13 comment
https://github.com/codefoundry-io/triad-dispatch-spec/pull/13#issuecomment-6089074042.

Current reachability qualification supersedes earlier unqualified "live AGY"
statements in this record: the current AGY wrapper directly handles raw-zero
missing/empty answers, and stored replay uses that interpreter. The preserved
map affects direct common classify/classify_extraction calls, not the current
wrapper route. A separate provider-free before/after probe confirmed identical
extraction-error, capacity-priority, success and omitted-raw-exit curated-map
outcomes, unchanged source hashes and exact fixture cleanup. Evidence:
_runs/spec-plan-20261010/u4d/callable-probe.json. The nine-module suite does not
itself directly cover that raw-zero map branch. Retention is callable compatibility,
not evidence of current CLI dependence. No new compatibility backlog is created.

Remaining-item reconciliation is recorded in 2026-10-10-u4-remaining-assessment.md.
DL-119's applier refusal and owner escalation already exist in the candidate;
the embedded child's non-repetition of that sentence is not an observed wrong
decision. No duplicate applier or wording loop. DL-91 has actual retired task/
fanout remnants; current production retry callers are Claude/Gemini, with no
Codex wrapper. Next: inventory their full references, prepare one bounded DL-91
removal plan and publish the host-specific disposition before dependent edits.
Keep Claude task-blocked65, native dispatch and locking. Do not expand the error
catalog or port A internals. Whole-task completion, installation and hook
retirement remain open.

2026-10-10 PR13 reply6088729953 checked, including inline/review comment lists.
A agrees with C76 and names C77 tests (t21 axes10/12/14/17; t32 class controls).
Read-only A a5afdd5a plus unrelated concurrent dirty files confirms those test
sources and loader logic; A runtime NOT RUN. Its reported F3-c plan amendment
is not independently confirmed in the inspected local plan's old exit0 sentence.
No new B runtime correction or shared-rule disagreement follows from this reply.
The U4 section of the broad plan records these distinctions and the completed
DL-106 scenarios: remove demonstrated duplicate/dead private logic; preserve AGY
no-answer outcomes and current callable compatibility, qualified above.

U4c R1 all-four SAFE, ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK; digest
5242550c0942c0bc56dd445c4c4c25597d69fea406dd2ad7c5e1bc32b1eae669,
fingerprint309287f1b985e3ec6cddd4a751c06037166be2d98ae1d7d3c9cc618fbbd82cda.
All producers terminal; custody exported and exact stage/cwd removed. One Minor
only distinguishes the passing success control from the zero-key loader RED
assertion; retain that distinction, no further code or wording round.
Evidence: workspace _runs/reviews/triad-classifier-loader-20261010-r1/.
Shared d1b9bcc published with authoring1/1,182tests and clean shared tree;
PR13comment6085594103 requests A's own C77 evidence. Native legs untouched.
Its former next action, DL-106 assessment, is completed by U4d above. The broader
task/hook remains open; no speculative cleanup or automatic A port.

Owner reaffirmed: stop and ask before a substantial design or scope change.
Current correction remains the existing loader contract, with no new mechanism.
The first GREEN invocation had a comma-joined test-path typo and ran no tests.
The next run passed403focused/2143full (4skipped) and four validators, but its
source-log equality assertion failed. Product hashes/HEAD/status were unchanged.
Its missing pre-run log inventory prevents attribution or recovery of exact
historical record changes; do not claim that run preserved logs.

Source inspection found test_preflight_accepts_without_any_agy_catalog reaches
actual stale cleanup without a test override. A neutral provider-free canary
confirmed the path while preserving existing logs. The ignored execution runner
now establishes child-only log/TMPDIR roots before imports and saves before/after
log inventories. Parent/user settings and product code are unchanged. Fresh
green-isolated finished once with exit0: focused403/full2143passed,4skipped;
four validators passed. Seven hashes/HEAD/fullstatus and ten source run-log
records were unchanged; exact temporary root removed. This is the final U4c R1
verification basis. Actual production+15/-3(net12), tests+59,
guidance+14/-1. No installation, merge or release.
Evidence: _runs/spec-plan-20261010/u4c/{green,green-valid,log-isolation-probe,green-isolated}/.
At that review's capture, PR13 latest comment6084876199 and remote main3afc4d7
were rechecked with no new A reply; the newer reply is reconciled above.

Fresh dedicated RED reproduced36failures/25passing controls, unchanged source
and exact fixture cleanup. Minimal loader correction now filters the existing
supported class set and integer-zero keys; leader smoke61passed. Four guidance
surfaces aligned. No new classifier vocabulary or authentication-proposal policy.
Final verification and review are recorded above. Shared revision adoption and
whole-task completion remain separate.

U4b2 evidence and existing-loader C77 case published at shared50845c5,
PR13comment6084876199. Authoring1/1 and182shared tests passed. Current bounded
plan: ../superpowers/plans/2026-10-10-u4c-typed-loader.md. Tests use real temporary
extension files and actual loader/classifier:36 expected RED cases,25 passing
controls. No new class, provider call, native mechanism or key-range policy.
Preserve curated oauth-env separately from new-auth proposal refusal and keep
B's reachable AGY fallback. That publication preceded the RED and correction.

U4b2 final R3: all four SAFE, ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK.
Digest1ea978486627066bed9f0f58a6851f15ea09eb79a1f347c80fb5b90aa5a7366a;
fingerprint13fde2646aed63e7618458298bcf88da0d4628fd7c311a4aa9c1b15e3c147e3a.
All producers terminated, custody exported, exact temporary stage/cwd removed.
Evidence: workspace _runs/reviews/triad-repair-replay-20261010-r3/.
Verified two optional Minor notes: docs can later qualify failed-delivery and
negative-exit refusal; the matching extraction-promotion tuple could later be
shared. Neither demonstrates a current false pass or warrants a fourth wording
round/refactor. No post-review product change. Production delta+89/-1(net88);
tests194lines; skills+21; other guidance+54/-11. Full C76 runtime limits remain.
Next: publish measured C76/B evidence, then separately plan/test DL-97 and
DL-106's zero extension entry under existing contracts. Rechecked A c890731
plus concurrent dirty work already filters proposal classes and nonpositive keys;
do not copy A-only internals or delete B's reachable AGY weak fallback.

Historical R2 is retained NOT_APPROVED/ROUND_INTEGRITY_OK. Claude and both Google legs
returned SAFE. The native reviewer's original Major assumed every nonzero
reader failure must invalidate verification. Current R-TERMINAL explicitly
retains the vendor diagnosis in that case; the reviewer subsequently confirmed
there was no runtime/verifier mismatch and withdrew the implementation claim
in a separate clarification, without replacing the original verdict. Narrowed
the overbroad shared sentence and product guidance to transport failures that
override runtime vendor classification. Shared e6ea3ee / PR13comment6084463664;
182 shared tests and authoring validation passed. No producer/log-schema change.

R2 also exposed a real test-fixture defect: setting the log environment after
module import did not redirect emit_run_log. Fixed the two captured log globals,
asserted the actual output location, added nonzero-reader and interruption
controls. Exactly169 prior U4b2 fixture logs were identified by recorded neutral
roots and the saved sentinel command, archived, hash-verified and removed from
bin/_logs. Other records were preserved. Earlier cleanup receipts establish
only removal of their stated neutral roots; no pre-run log inventory exists to
exclude historical pruning. Evidence: _runs/spec-plan-20261010/u4b2/fixture-log-recovery/.
Leader smoke32passed and source run logs unchanged. Fresh dedicated affected-
module GREEN359passed and four validators passed, HEAD/status/11hashes and
source run logs unchanged; exact neutral root removed. Evidence:
_runs/spec-plan-20261010/u4b2/focused-fix-r2-green/report.md.
Production apply_patch.py remains at the SHA tested by
green-fix-r1 (338focused/2078full passed,4skipped). Fresh complete R3 follows.
All R2 producers are terminal and exact temporary stage/cwd cleanup is complete.
No full C76, installation, merge or release claim; broader work/hook remain open.

Historical R1: triad-repair-replay-20261010-r1 is NOT_APPROVED/ROUND_INTEGRITY_OK:
both Google legs SAFE; Claude/Astra identify lost transport-failure eligibility;
Claude also identifies unchanged-class false pass, empty verify-path mutation
and the wrong test lock sibling. All producers terminated, evidence exported,
exact temporary stage/cwd removed. Valid dedicated correction RED9failed/19passed,
state unchanged, fixture removed. Small corrections refuse existing host-generated
transport diagnostics and unchanged class, preserve verify mode for empty values,
and test the actual lock sibling. No new log schema or native/provider execution.
Shared clarification92dc3e4, PR13comment6084170769; authoring1/1 and182tests pass.
Next: fresh dedicated GREEN, then complete fresh round r2. Prior GREEN remains
evidence for its earlier bytes only; no full C76/admission claim.

U4b2 update,2026-10-10: existing apply_patch.py now supports read-only
--verify-run-log using the actual route classification path. Dedicated valid
RED17failed; GREEN329focused/2069full passed,4skipped; four skill validators
passed, HEAD/status/11hashes unchanged, exact fixture removed. Scenario choices
route unknown through the proposal child then stored verification; timeout and
authentication stay outside phrase repair. A stale protocol TOC link was corrected
after GREEN; executable/skill bytes are unchanged. Evidence:
_runs/spec-plan-20261010/u4b2/green/report.md. Production delta+83/-1; no new log
schema, vendor calls, native mechanism or global configuration changes.
PR13 reply6083800391 agrees with minimal route-specific reuse; A's reported
234-record spike is not rerun here. A livecc6fc3a plus concurrent dirty work still
has no verify-run-log option; its Phase7 work is pending. Shared main freshly
fetched at3afc4d7. Next: triad-repair-replay-20261010-r1 on the final bounded delta,
then publish measured evidence and proceed to the separate DL-97 loader item.
No full C76, installation, merge or release claim.

2026-10-10 U4b2 entry: PR13 A reply6083248450 agrees; E-ENV/E-AUTH74 and F3-a..d
are scheduled, not completed. Read-only clean A92b7fee still has caps, selector
omissions and no-web repair instructions. New bounded plan:
../superpowers/plans/2026-10-10-u4b2-stored-record.md.
Provider-free spike proves naive stored-stream replay can yield server-capacity
while actual AGY interpretation remains unknown; stderr positive control works.
Evidence: workspace _runs/infra/20261009-spec-to-code/u4b2-replay-spike.json.
No provider calls, exact fixture removed. Owner's subsequent simplicity direction
supersedes the architecture-choice question: reuse the existing failed record
and actual classification path with only a minimal helper if needed. No general
replay engine, new log schema or broad wrapper refactor is planned. Preserve
review points, diff and related-code discovery; avoid additional cwd/security
machinery without a concrete need. Do not claim full C76/DL-104.
Shared investigation published at cbb4ac2; PR13 comment6083528392 requests
A's F3-c replay-boundary evidence. Authoring1/1 and182shared tests passed,
both diff checks clean. No design answer remains pending for those withdrawn
alternatives; no source behavior has changed in this U4b2 investigation.
Minimal-reuse direction published at5985fc9, PR13 comment6083611215;
shared authoring1/1 and182tests passed. The next step is the bounded existing-path
implementation in the revised plan, not another architecture approval request.

Owner follow-up: D-BACKLOG-DISPOSITIONS-20261009 distinguishes deferred,
unmeasured, withdrawn/unadopted, no-port and bounded-method items in the shared
spec. The broad plan adds an explicit U10 remnant-removal sweep. Deferred features keep their contract/re-entry condition;
withdrawn proposals and cross-host copying are not active prerequisites. Preserve
historical evidence and working features. This documentation cleanup does not
change the next implementation unit, U4b2, or complete the whole task.
Scope cleanup published at142904d (PR13 comment6083342471): unnecessary
research/resumption tasks removed from the plan and maintainer handoff;
explicit memory correction recorded. Shared authoring1/1 and182tests passed,
both diff checks clean. No executable code or host-native behavior changed.

[U4b1 bounded plan](../superpowers/plans/2026-10-09-u4b1-applier.md):
shared b24f858 clarifies all-oauth proposal refusal before dependent B edits;
182shared tests passed, PR13 comment6082468957. PR13 had no new issue/inline/review
reply; A shared branch cdf5858 records DL-131..135 separately. A clean6e555144
still lacks repair web/timeout/replay updates; its all-oauth refusal is confirmed.
Fresh dedicated RED18failed/3passed, stable hashes/status and exact cleanup.
B now refuses every auth proposal and removes entry/reason caps while preserving
semantic checks, curated entries, locking/atomic writes. Actual repair_message
is unchanged. Fresh dedicated GREEN: focused229/full2050 passed,4skipped;
both validators passed, source hashes/HEAD/status stable, exact test root removed.
Round triad-repair-applier-20261009-r1: all four SAFE, ALL_SELECTED_APPROVED,
ROUND_INTEGRITY_OK. Digest fd55e0315b468b1aa164c734905de76e9e8619124d20f772b99f3c70deb15b5f;
fingerprint84fd4f1b7aa8e8fc2900189f594fec510fc329d679b06895e56407033d6bebc3.
All producers terminal; custody exported, exact review stage/cwd removed.
One nonblocking comment-only note at _common.py2618/2687 is retained: old
proposal-set comments still include oauth-env, but the early refusal is correct;
sets remain unchanged to preserve curated-entry behavior. No post-review product
edit or wording-only redispatch. Delta: production+8/-42, docs+18, tests+88.
Next: U4b2 stored-record replay/timeout/handoff plan under settled DL-104.
Shared evidence published at0246311 to PR13; authoring1/1,182shared tests and
diff check passed, shared tree clean. Claude handoff comment6082819262 records
implemented Gemini floor/model transport and remaining repair/environment work
at A6e555144. No product commit/install/merge/release; task hook stays active.
Full C76, stored-record verifier/handoff U4b2 and typed-loader DL-97 remain pending.

Impact split: [U4a plan](../superpowers/plans/2026-10-09-u4a-repair-web.md) covers
repair web permission; U4b retains timeout routing, stored-record verification,
applier work and the verified existing dispatch-skill-to-protocol handoff gap.
Owner accepted the two residual demands as nonblocking and authorized U4b.
Full C76 remains pending; R3 NOT_APPROVED stays as historical reviewer evidence.
Decision: shared D-PROMPT-REVIEW-BOUNDED-20261009. No fourth unchanged round.
Published to PR13 at f8ae9ba; authoring1/1 and182shared tests passed, worktree
clean. Claude handoff: comment6082308225. Native leg mechanisms remain untouched.

U4a changes five text files (+47/-5): actual repair_message, README EN/KO,
SECURITY and migration guidance. No Python module/classifier/schema/native
model/effort/settings change. Dedicated RED refused web; GREEN performed official
search/fetch with attribution; local control skipped unnecessary search/entries.
Capability fixtures are not vendor incidents. Focused106/full2029 passed (4 skips),
both validators; migration correction passed fresh106/validators plus4 dedicated
migration-contract tests. Prompt/Python bytes unchanged since GREEN. Production
Terra preset and unavailable-tool branch were not separately certified. The local
control did not capture the four-file prehash; other verification did.

R1/R2/R3 retained NOT_APPROVED with ROUND_INTEGRITY_OK. R1 omitted R-THREAT;
its malicious-URL suggestion was speculative under the settled context. R2 found
missing migration guidance, now corrected. R3 digest
e82260abc580d0fd8124a22460cdab81ea7cffba809b9e735a34bbdf7113b54b;
fingerprint4be5cd186eccb81541c3daee835869ef4c248b1d7a22843e3c9292e9d92b35f5.
Pro/Flash/Astra SAFE; Claude NOT-SAFE. All producers terminal, custody exported,
exact temporary stage/cwd removed. No majority approval.

Accepted nonblocking residuals: README unrelated-public-errors wording became Major in R3
after Minor in R1/R2 on unchanged bytes; a new Major demands phrase-pinning tests.
Fresh Luna/high URL and README-owner scenario/control choices all met the
preregistered expectations. Independent Sol/high consolidation confirms a real
README wording ambiguity but no demonstrated wrong behavior, and distinguishes
literal-pinning coverage from functional proof. The higher-priority testing rule
excludes tests merely mirroring implementation; owner direction ends wording
iteration on correct choices. Owner adjudication is now received: accept the
two demands as nonblocking and continue U4b. No unchanged redispatch. No further prompt rewrite or
speculative classifier is authorized by a review label. Citation-field and
untrusted-page notes stay nonblocking; do not add the retiring 500-character cap
to instructions. Evidence: _runs/spec-plan-20261009/u4a/ and workspace R1/R2/R3
review records. Preserve the source candidate and task hook.

Shared R-CLASSIFY/C76/D-REPAIR-WEB-20261009 is published at310de79. Refreshed
remote main3afc4d7; A clean a6f3c175 still prohibits web in three source agents
and distributed template. Shared partial evidence published at8d0dcb2; authoring1/1,
182shared tests and whitespace check passed. PR13 handoff comment6081735013.
A runtime NOT RUN; no A edit. No product commit/install/merge/release.

U4b current-source check: B632f426 + preserved candidate still includes timeout
at repair-protocol.md:3; bin/apply_patch.py accepts cli/classifier/proposal only,
with no stored-run verification option; shipped dispatch skills have no repair
protocol pointer. A d075a879 has unrelated concurrent dirty work preserved;
triad-codex-dispatch/SKILL.md:90/230 routes timeout, and239/317-320/343 calls the
vendor again using --repair-mode to verify. A runtime NOT RUN; no A edits.
These are pending implementations of settled DL-104, not invented incidents.
Next: bounded U4b plan and provider-free stored-record/handoff RED, preserving
auth STOP, locking and native leg ownership; separate any DL-97/parser dependency.



U2c completed in the local candidate: model/effort settings preserved; agreed
auth/endpoint/loader omissions filter names before values; Gemini project
variables survive direct and v2 adapter -> wrapper -> vendor probe paths.
Fresh final dedicated focused370/full2029 passed with4skips, both validators;
stable hashes and exact test cleanup. Fresh round triad-child-env-20261009-r2:
all four SAFE, ALL_SELECTED_APPROVED, ROUND_INTEGRITY_OK. Digest
3eb16d60e4f1a5fe6ae7d7ca3cce0bbd779778b01ffa0dd6fa3238aa06599aad;
fingerprint6d57005c718598c64f6cbea511545d5f9bddcf62d739e5f569b10bcfd2fd6a87.
Every producer terminated; custody exported and exact temporary stage/cwd removed.
Retain one nonblocking internal-comment note (_common.py1396-1398/1637-1640:
old loader-only/same-environment/pty description). The helper docstring and public
docs state the correct rule; no product bytes changed after R2 approval.

Shared evidence/case/dev-log update published to PR13 at **75dc801**; authoring1/1,
182 shared tests and whitespace checks passed, shared worktree clean. Maintainer
handoff: PR13 comment6080219137. A dd790cc3 still has the three obsolete model
omissions and items-before-filter helper; read-only source evidence, runtime
NOT RUN. Each host's native leg remains untouched. The cancelled selector
warning/research/attestation remains cancelled.

Owner clarification: do not make speculative classifier expansion or an exhaustive
phrase audit the automatic next implementation unit. An in-progress spec difference
is pending work, not evidence of an incident. Use the existing repair flow: actual
unknown/extraction-error -> that run's record -> read-only analyzer proposal ->
deterministic apply and stored-record verification -> shared evidence when warranted.
Resume the agreed implementation sequence without the constructed denial-case task;
retain DL-86/DL-92 as pending conformance items, not newly diagnosed incidents.
The owner's challenge prompted a source/spec review:
A 5473933 has no Claude CLI wrapper and already uses per-CLI measured lists;
B still retains generic shared phrases. The constructed formal-Claude empty-answer
denial/tool_input case is a recorded limit, not a dedicated implementation target.
It is distinct from the completed C74 is_error-envelope regression. See
[scope adjudication](2026-10-09-non-auth-classification-review.md). No production
change or provider/test execution occurred for that review; shared75dc801 already
states the relevant rule. Keep typed-extension DL-97 separate. Do not invent
unmeasured AGY credit carriers Full C37
and the broader spec-to-code task remain open; retain the startup hook. No product
commit, adoption, merge, installation or release is claimed.

U2c final-verification history:

Fresh R2 dedicated verification: focused370passed/4skipped; full2029passed/
4skipped in408.65s; both validators passed. HEAD/full status/all15 SHA256 targets
and inherited runner environment unchanged. Session40459 terminated; exact
neutral pytest root removed. Evidence: `_runs/spec-plan-20261009/u2c/r2-green/`.
Remote shared main freshly checked again at3afc4d7. Source is ready for the full
R2 review; no approval or whole-task completion claimed yet.

R1 is NOT_APPROVED with ROUND_INTEGRITY_OK: Claude and native Astra both found
that the v2 adapter labels its outer wrapper child `preflight`, losing Gemini
project variables before version/help children. Pro/Flash were SAFE. All producers
terminated, custody exported and exact stage/cwd removed. Digest1ff975118211d7f3ff54a6e9e16cfd56d8addcde09f2a5a9fa7b4fb81d7a3607;
fingerprint436d4e8a023b6672df478c76d58ace08f3109de62ea8050a4787bbf0c0e810da.
Shared a2149f9 names the intermediate chain in C75 before the correction;182
spec tests and authoring1/1 passed. PR13 comment6079842522 requests equivalent
A outcome checks; A c57d6b60 remains read-only and runtime NOT RUN.

Fresh valid dedicated RED:1failed/1passed; actual adapter -> wrapper -> synthetic
vendor version/help lost all four project variables. Earlier `adapter-red/`
stopped at missing user-site pydantic under synthetic HOME and is fixture-failure
evidence only. Corrected fixture preserves login HOME for Python dependencies;
the vendor remains a local fake executable, never authenticated inference.
`adapter-red-valid/` retains the intended RED with stable source and exact cleanup.
Route now propagates through the outer Google probe; default/non-Gemini behavior
remains, and compatibility-subset comments resolve the two Minor notes without
removing established arguments. Leader focused smoke58passed. Production
+58/-16 (net42), tests +201/-9, docs +20/-3. Fresh dedicated focused/full
GREEN and validators are complete; next round triad-child-env-20261009-r2.
No R1 approval is carried forward and no new selector investigation is added.

Pre-correction verification (historical):

Fresh verification: focused335passed/4skipped; neutral full2027passed/4skipped
(445.76s), both validators passed, HEAD/full status/12 hashes unchanged, exact
temporary root removed and sessions reaped. Evidence: U2c `neutral-green/`.
The first full attempt under `green/` failed104 tests because its runner placed
temporary bootstrap/lifecycle roots inside the source checkout; representative
guard refusals and all failure output are retained. Two representatives and the
entire suite passed with neutral paths and unchanged product source. This was
a test orchestration correction, not a source fix or permission bypass.
Actual bounded production delta +52/-13 (net39), tests +141/-7, docs +20/-3.
R1 subsequently found the intermediate-probe defect recorded above.

Shared74d259c reconciles R-NOCOST/C11/C17/C37 with the owner's withdrawal:
GEMINI_MODEL, ANTHROPIC_MODEL and ANTHROPIC_SMALL_FAST_MODEL are preserved,
alongside effort settings. Shared authoring1/1 and182 tests passed; PR13 comment
6079317869 asks Claude to apply the same contract and independent C75 filtering.
A source5531a663 was inspected read-only; A runtime NOT RUN.
Fresh dedicated preservation RED:22failed/37passed, seven hashes/HEAD/status
stable. The candidate now removes the obsolete three-name omissions and formal
Gemini override, with paired documentation and fixtures aligned. Dedicated
GREEN/full suite/validators are complete; the four-family review remains.
No additional selector investigation, warnings or attestation is pending.

Latest owner decision: discard the new model/effort environment inspection,
warning, modification and effective-effort verification proposal. The previous
preserve-and-warn direction is superseded. Preserve user settings and existing
effort forwarding. No warning implementation exists; no new selector probe,
per-dispatch hook, capability matrix or attestation gate is required. Historical
research remains in `2026-10-09-cli-selector-precedence.md`, clearly withdrawn as
an implementation proposal. Shared decision:
D-SELECTOR-PROPOSAL-WITHDRAWN-20261009.
Published to PR13 at8763d54; shared authoring validation passed (1/1), diff check
passed. Remote main was re-fetched at3afc4d7. Claude maintainer notified by PR
comment; this is proposal withdrawal, not product implementation or release.

At withdrawal, the earlier U2c candidate remained unadmitted with its baseline;
withdrawal itself was not GREEN/review or completion. The completed U2c proof
above supersedes that pending state. Independent credential/loader
hygiene, C75 name-before-value filtering and Gemini project handling remain
separate from the cancelled selector extension. Next: resume the existing
conformance backlog with that extension removed; reconcile the remaining U2c
scope against its pre-edit baseline before any further code admission (now mapped
in the revised U2c plan; verification/review still pending). No native
leg changes, installation, release or whole-task completion is claimed. Keep
the task startup hook until the entire spec-to-code task is complete.

Previous completed unit:

U2b final candidate: measured vendor authentication carriers STOP before
capacity/timeout, captured authentication survives signals, usable answers and
reflected command/tool text retain their proper treatment. C74 was clarified
in shared dd85b52/d5c5756 BEFORE the corresponding corrections. Each host's
native leg remains untouched.

Fresh final dedicated deterministic verification: focused437/full2005 passed,
4 skipped each; both skill validators passed; hashes, HEAD and Git status stable.
The executor disclosed reading required instruction/memory context before the
fixed manifest; this is not a blinded prompt-choice probe. Fresh review
`triad-auth-carriers-20261009-r3`: all four SAFE, matching integrity,
ALL_SELECTED_APPROVED. Digest
`133cb3e3da1671ac54d0eca03df6ba77e4d60dbe3daa4bdd4e6fb198d654d3fc`;
fingerprint `9cf5da5e0d91e5cc07086e932b8446e777ad12869db64a0acdcc5619c60b8e33`.
All processes terminated, custody exported, exact stage/cwd removed. Local
evidence: `_runs/spec-plan-20261009/u2b/r3-green/` and workspace
`_runs/reviews/triad-auth-carriers-20261009-r3/`.

Bounded evidence published to draft PR13 at `b8512b6`; shared authoring map
valid, 182 tests passed, whitespace check clean. DL-75/95 implemented in B's
candidate; DL-92 raw-auth part complete, non-auth per-CLI lists still OPEN.
A source2f91e8c C74 verification requested; runtime NOT RUN, reply pending.
Full multiline denied-command vendor output is unmeasured; synthetic controls
do not establish a new carrier. The non-blocking Gemini derived-error fallback
limit stays recorded for measured follow-up or later classifier cleanup.
R3 also reproduced baseline formal-Claude denial-summary/non-auth matching and
typed extension auth-code timeout/signal precedence gaps. Both are nonblocking
for this measured-auth unit; track them with non-auth cleanup and DL-97.

U2c implementation and bounded completion now appear above.
Do not read environment values, manufacture auth failures, guess AGY credit
location/exit, Full C37/C43 and broader
spec-to-code work remain incomplete, so the task startup hook remains enabled.
No product commit, install, merge, revision adoption or release is claimed.

Historical R2: focused435/full2003 passed with4skips; review NOT_APPROVED despite
matching integrity. Fresh RED2failed/4passed reproduced the denied-command
banner scan. Shared clarification d5c5756 preceded correction; R3 supersedes
that failed round without erasing its evidence.

R1 verified 423 focused passes/4 skips and 1991 full passes/4 skips, both
validators, stable hashes; review integrity matched but outcome NOT_APPROVED.
Claude found reflected AGY command text falsely classified as authentication
and full Claude envelopes widening non-auth classification; native found a
redundant AGY SUCCESS guard hiding the auth banner on no-answer failure. Fresh
combined correction RED: 11 failed/1 passed, source stable. Shared C74 was written
and pushed BEFORE dependent correction at dd85b52 (182 shared checks passed),
with an A verification request on PR13 comment 6077472952. Current A 2f91e8c
has the corresponding helper risk by source; no A runtime verification/edit.
The three bounded corrections and two associated documentation/comment fixes
pass leader focused verification (293 cases). That basis was superseded by the R2/R3 verification above. R1 producers terminated, custody exported, exact
stage/cwd removed. Retain R1 evidence and adjudication, including its copied
receipt-limit description correction; no R1 admission is claimed.

U2b follows `docs/superpowers/plans/2026-10-09-u2b-auth-carriers.md` against shared
PR13 b085a6e and freshly fetched main 3afc4d7. Dedicated RED observed 39 failures
and 34 passing controls with stable source hashes. Carrier parsing now retains
original error fields across classification, extraction, timeout and signals;
raw authentication phrases/extensions cannot stop quoted answers. AGY non-auth
diagnostic text retains its existing treatment. Initial leader focused suite:
281 passed. Three initial test expectations were corrected to retain the existing
non-auth schema classification; generic phrase cleanup remains a separate unit.
The final GREEN and current-unit review are recorded above.
No new vendor shape, native-leg behavior or global setup is introduced.

U2a terminal evidence: dedicated focused 179 passed / 4 skipped; full suite
1925 passed / 4 skipped (411.41s), both validators passed; measured hashes,
HEAD/status stable. Fresh review `triad-gemini-auth41-20261009-r1`: all four SAFE,
ROUND_INTEGRITY_OK, ALL_SELECTED_APPROVED under the owner-selected roster.
Digest e54c33c00da4c621a0d27950f8f924859c9c7c3b10694162412503e4b1efe013;
fingerprint b1357b8bac1bf165af2308e11d19b7fc313934adde76adf950c96b8f2dc4b2eb.
All producers terminated; exact stage/cwd cleanup and custody export complete.
Three Minor findings adjudicated: no benefit established for moving the signal
invariant into callers; stale header/layer docs and two real-child integration
coverage suggestions are retained for the remaining carrier unit. Its cases
must include capacity stderr plus exit 41 and timeout-triggered TERM exit 41.
No whole-C37 conformance, product installation/merge/release is claimed.
Shared implementation evidence and bounded DL-99 status are pushed to PR13 at
**b085a6e**. Shared authoring map valid; 182 checks passed after synchronizing
the dev-log OPEN footer with DL-99's implemented-candidate status. Task startup
hooks remain active because the broader spec-to-code work is incomplete.

U2a is the first bounded authentication carrier unit, following
`docs/superpowers/plans/2026-10-09-u2a-gemini-auth-exit.md`. Gemini v0.63.0's
official exitCodes.ts confirms authentication code 41. Dedicated RED: 7 failed,
3 other-CLI controls passed. Leader corrected test log isolation and reproduced
the same failures before implementation. First RED called stale-log cleanup at
the import-time default log root; no prior file inventory exists, so whether
and which historical logs were removed is unknown. This is a verification limit,
not evidence of no side effect. Subsequent fixture uses its temporary log root
and disables global stale-temp sweeping. Source delta +26/-13 (net +13) recognizes
only Gemini's raw exit code, returns oauth-env/65 even at timeout or late signal,
and preserves transport failure flags and answer withholding. Leader smoke:
18 passed (new cases and complete parent-signal module). Final dedicated verification
and review are recorded above. Text carriers, environment scrub
and extension work remain separate U2 follow-ups.

Official docs plus a one-off real CLI diagnostic confirmed current read/search:
Claude 2.1.289 opus/xhigh plan used Bash rg then Read; Codex 0.160.0 with
gpt-6.1-sol/medium read-only used native rg then cat. No agent or tool-enabling
override, both exit 0, random marker recovered, fixture unchanged and removed.
This proves that bounded capability, not universal settings or formal conformance.
Evidence: workspace `_runs/infra/20261009-spec-to-code/leg-tool-probe/` and shared
`decisions/2026-10-09-leg-agent-scope.md`. Runtime delta +0/-0; no new audit gate.
Clarification and capability evidence pushed to draft PR13 at **11c6b46**;
fresh shared checks: 182 passed, one valid authoring map, diff whitespace clean.
Initial [U2 source mapping](2026-10-09-u2-auth-mapping.md) identifies carrier,
exit-41 and signal-handling gaps. The exit-41 correction now has the bounded
U2a evidence above; remaining carrier conformance is still open.

2026-10-09 continuation: main fetched again at 3afc4d7; B remains on
codex/opus-5-5-default at 632f426 with its intentional dirty work preserved.
Current A source is 6878cc4a6913e7ef1d61487757276b3d105703a2, with an unrelated
dirty lib/review_scratch.py. Read-only comparison of its leg-contracts lines
345–347 and 357–377 confirms no catalog gate and explicit setup-once profiles;
no A correction or native-leg change is needed for this documentation unit.
Plan/scenario: workspace `_runs/infra/20261009-spec-to-code/agy-docs/`.
Expected production delta +0/-0, novel core 0; about +20/-15 documentation lines
in six shipped files. Pre-change bytes are retained for the bounded diff in
`_runs/spec-plan-20261009/agy-docs/before/`. First executor read historical memory,
so its sample is retained but excluded from independent behavior proof. A new
history-free executor (`agy_docs_baseline_clean`) observed the intended RED:
normal provider launch withheld because the AGY catalog requirement conflicted
with the canonical no-catalog rule; drift/permission controls were correct.
Its 13 measured hashes and HEAD/status matched. The six document edits remove
that obsolete instruction, link explicit setup, clarify profile versus permission
controls, and align paired installation/removal guidance. Runtime/profile bytes
and tests are unchanged. Fresh GREEN selected catalog-free normal preparation,
retained mismatch refusal, and distinguished profile selection from enforcement.
All six complete affected modules passed (159 tests, 5.62s); both cross-family
and AGY validators passed. All 16 hashes, HEAD and Git status stayed unchanged.
No full-suite or release archive rerun is claimed for this documentation-only
unit. Evidence: `_runs/spec-plan-20261009/agy-docs/green/`.
Fresh full-scope review `triad-agy-docs-20261009-r1` completed: all four SAFE,
ROUND_INTEGRITY_OK, ALL_SELECTED_APPROVED under the owner-selected roster.
Digest ebd0c40d3133a5e138d22ec87ecf0c475c596da3d29aa19b1a9f11645cc8a7db;
fingerprint 8ccf4fa968988ae546449fa1deeaf417566913d69a1449fedd6c324d36bfa45d.
Claude's four further nonblocking documentation/test-pin suggestions were checked.
One fresh Luna/high simulation, without review history or expected answers,
selected correct changed/equal-byte update, exact removal ownership, and
missing/matching-profile actions. Per owner direction, stop wording iteration;
retain suggestions rather than add duplicative instructions or exact-prose tests.
Source fingerprint still matched after the probe. All formal producers terminated;
custody export and exact temporary stage/cwd cleanup completed. Evidence and
dispositions: workspace `_runs/reviews/triad-agy-docs-20261009-r1/`.
Shared evidence is pushed to PR13 at e90305a. Shared checks: 182 tests passed,
one authoring map valid; the spec worktree is clean. Broader SoT/task hooks remain
until the complete spec-to-code checklist is finished; no premature cleanup.

Current correction: shared C72/R-CONTAIN published on PR13 at 9bd9d58, A's
latest reply and its evidence limits recorded at 9763373. Local code now ships
B-owned review/research profiles and explicit setup, validates installed bytes,
binds name/path/hash into legacy/v2 preflight and checks before/after dispatch.
Raw routes and native legs are unchanged. Dedicated RED reproduced two missing
checks. Independent code review's Unicode-path defect was reproduced and fixed;
C72 has 12 passing tests. Dedicated final full suite: 1915 passed, 4 skipped in
404.91s, exit 0; both skill validators pass. All 55 measured source hashes remain
identical. Git status alone gained the leader-authored installation approval doc
during verification; this attributed documentation delta is retained explicitly.
Shared PR13 is OPEN/draft; verified evidence is pushed at fd7d370. Its rule distinguishes tool declarations
from permission evidence, incorporating A's latest comment. The owner subsequently
approved the exact two global profiles: installed bytes match source and A-owned
profiles are unchanged. One AGY 1.3.2 Pro/high formal-v2 capability call completed
native grep_search then view_file, wrapper/vendor exit 0. Evidence and limits are
in the installation record. This is capability proof, not formal admission.

**Next action:** continue U2 carrier/environment mapping after completed U2a.
For the text-carrier unit, include the retained header and integration-test items. Reuse
existing quota/source research; do not guess the unmeasured AGY credits carrier.
The documentation unit above is complete. Optional C72
test expansion and receipt-parser refactoring remain deferred absent a demonstrated
behavior defect; do not reopen settled wording without new failure evidence.

R3 (`triad-opus-default-20261009-r3`) completed: all four SAFE, all bindings and
canonical re-render checks valid, ROUND_INTEGRITY_OK. Owner-selected outcome is
ALL_SELECTED_APPROVED, not the fixed Terra ledger token. Claude supplied six
nonblocking Minor findings; the other legs had no findings. Reproduction and
dispositions are in workspace `_runs/reviews/triad-opus-default-20261009-r3/adjudication.md`.
Digest f69e626dc82f26ebff64d7589dade725ea8f96868ef219147ca348d7a9ec9e22;
fingerprint 44d877097ee366236be908a666d71ae616f5d544ca57701787be115db61ee914.
All producers terminated, custody exported and exact temporary stage/cwd removed.
The installed profile delta remains the [exact installation record](2026-10-09-agy-profile-installation.md).
The [approved implementation](2026-10-09-agy-search-profile-decision.md) is tested.
Capability evidence is published in PR13 at fc9e497, followed by R3 results and
bounded follow-ups at 2996cda; spec checks pass (182 tests, one authoring map).
Freshly fetched main remains 3afc4d7. R3 covers U1b plus the
approved AGY profile recovery and related consumers, with the existing owner
roster (opus/xhigh, AGY Pro/high, AGY Flash/high, fresh Astra/high). No prior
review result was carried forward; no routine source-read audit was performed.
Separate Gemini CLI remains 0.60.0, below the owner-required 0.63.0; its official
0.63.0 source retains default native search, but no supported-version live probe
or global upgrade has occurred. R2 remains NOT_APPROVED with
ROUND_INTEGRITY_OK: three SAFE; Pro reports missing native search tools. All
producers terminated; results/adjudication/export and exact cleanup are complete.
A bounded Pro diagnostic reproduced the missing-search report with a successful
file-read control. Installed AGY is 1.3.2; its official CLI changelog says 1.2.7
removed grep_search/list_dir/find_by_name from the default toolset, retaining them
for explicit custom-agent tools. A source already ships such an AGY profile;
no A runtime capability is claimed. The new B capability result is independent.
The two nonblocking Claude documentation notes were verified and corrected:
state the existing v2-only 2.1.205 floor and disclose the formal alias migration
in pending compatibility notes. Documentation checks: 42 passed in 0.15s.
Do not rerun the full review without capability evidence, bypass the missing leg,
restore exact-file allowlists or add a routine read-log audit.
Round: `triad-opus-default-20261009-r2`.
Main was freshly fetched at `3afc4d7`; draft spec HEAD is `cc10345`. The
owner-requested
[`review-boundary diagnosis`](2026-10-09-review-read-boundary-diagnosis.md)
is implemented and verified. The owner rejected leader enumeration/approval of
related files and routine read-log auditing. R2's render/TASK now allow related
discovery across the product worktree; its collector no longer scans read logs.
Three collector regression cases pass after the unwanted log read was reproduced.
Project instructions are clarified. A fresh canonical-skill baseline already
selected the correct behavior, so the product skill/renderer are unchanged.
Shared C70/C71 record the clarified contract and the A comparison: no equivalent
file-list defect found; existing coded AGY required-read/tool checks preserved.
Fresh behavior verification discovered the unlisted helper defect and selected
incident-driven log inspection. Combined relevant regressions: 191 passed;
source validator valid, under-test hashes unchanged. Independent source review
found no concrete regression. These were not formal admission. R2 subsequently
completed under the corrected workflow and is NOT_APPROVED for the separate
AGY tool-exposure gap above. Diagnostic logs were inspected only for that incident.
Shared clarification and A handoff are published to draft PR #13 at `cc10345`:
R-PROMPT, C70/C71 and the common code-purpose clause. Shared suite 182 passed,
one authoring map valid; remote OPEN/draft/head verified. No adoption or merge.
Detailed execution evidence is `_runs/spec-plan-20261009/read-boundary/verification.md`.
The broader
[`execution plan`](../superpowers/plans/2026-10-09-shared-spec-execution.md)
remains active.
Production/data delta is +4/-4/net 0: v2 default and legacy formal route now
use `opus`, retaining xhigh/1200/no-fallback and no default agent. Raw/v2 explicit
model IDs and v2 null remain supported. RED: 16 failures/159 passing controls;
dedicated fresh executor selected the old fixed-ID command before the edit.
Evidence: `_runs/spec-plan-20261009/u1b/`; no admission, install or release yet.
Dedicated fresh GREEN chose opus/xhigh/1200 with no agent; 398 affected tests
and both skill validators passed. Under-test source hashes stayed identical;
only this progress document changed during that executor's run. Initial full
suite: 1,902 passed/4 skipped/one stale C65 request assertion (the test was
collected before its final expectation edit). Final full suite passed **1,903
tests, 4 skipped** in 416.69s (exit 0). Review
`triad-opus-default-20261009-r1` remains INCOMPLETE with matching source integrity:
its exact-file boundary was violated and Claude found stale current installation
prerequisite wording. That finding was verified and corrected in both README
and installation languages; subsequent documentation checks passed **42 tests**.
Round 1 evidence and exact temporary cleanup are retained. No admission is
claimed. Earlier R4 exact-list wording below is historical round handling,
not a current general requirement for related-code inspection.
U1T now has A's
agreement and awaits rule/case finalization and per-parser evidence, not another
initial maintainer response. Each host's native leg remains excluded. U1a removes the
Claude adapter's model/effort catalog gate, checks exposed identity/effort
contradictions independently, and retains unknown labels without fabricated IDs.
Final affected suite: **99 passed** in 26.17s, including 32 selection cases.
Earlier full suite: 1,881 passed, 4 skipped, exit 0 in 407.57s (Python 3.12.13 /
pytest 9.0.3); this precedes the bounded review corrections. The earlier five-case
diagnostic also passed. Final production delta is +60/-19/net +41. Shared draft
interpretation is published
on PR #13 at `32d7897`, with completion evidence pushed at `5c040ff`; it is not
a common adoption or full C34 claim. The reviewed adapter SHA-256 is
`aa7444dcbf5ca1c7ecd4c3c2339b55363be06e1c1cf8a4790ab23a8427376747`.
Initial RED was 12 failures; two further boundary defects were reproduced and
fixed. Full-suite evidence is `_runs/spec-plan-20261009/u1/full-suite.txt`.
Round `triad-claude-selection-20261009-r1` is NOT_APPROVED with matching
integrity: Claude and Codex identified two selection-header parsing defects.
Both were reproduced (10 failing boundary cases before fixes); wrapper effort
vocabulary validation was also restored independently of the model catalog.
The corrected six-module suite passes 99 tests (26.17s); 32 selection cases.
The 1,881-test full result precedes these bounded parser corrections.
Fresh review `triad-claude-selection-20261009-r2` is **ALL_SELECTED_APPROVED /
ROUND_INTEGRITY_OK**: Claude, Google Pro, Google Flash and fresh Codex Astra each
returned SAFE. Its digest is
`8ebf2c475aa49fd9c32606a1f0763c839dbb7de4c5f52d58fdcaa345455895db`.
The preserved owner-selected Astra/high override means this is not the fixed
Terra-ledger ADMITTED_SAFE token. Evidence is at workspace
`_runs/reviews/triad-claude-selection-20261009-r2/`; exact stage/cwd cleanup is
complete. Round 1 and its findings remain retained without carried approval.
The final optional suggestion for version-less/novel vendor labels is deferred
until there is observed output evidence; no additional parser shape is guessed.
The historical 2.1.282 selection capture and official `[1m]` alias documentation
are materialized in its task. Current-version format coverage remains bounded.
Three earlier expected failures and two passing controls remain in
`_runs/spec-plan-20261009/u1/test_selection_red.py`. U1T's actual wrapper parser
observations (24 combinations) remain separate pending shared disposition.
The Claude maintainer prompt is
[`2026-10-09-claude-maintainer-prompt.md`](2026-10-09-claude-maintainer-prompt.md).
Share the transport clarification through the spec
before dependent implementation; current code must not infer an unknown model
label. Evidence and unresolved live checks are in
[`2026-10-09-spec-investigations.md`](2026-10-09-spec-investigations.md).
U1a changes are local and uncommitted. Native legs remain host-owned.
Do not rerun completed units without new evidence or changed product bytes.
The completed Google unit's final round
`triad-google-pins-20261009-r4` is ALL_SELECTED_APPROVED / ROUND_INTEGRITY_OK.
The prior C43 correction remains admitted by `triad-c43-quota-20261009-r2`.

The expanded plan owns the dependency order and functional-unit checklists;
the earlier stage-4 table below is a coarse queue, not an exhaustive ledger.
New parser evidence justifies a separate transport unit, without retroactively
approving that unit under the earlier Google review.

**Known limitation:** neither host has captured the AGY credits sentence's
channel, event field or exit status. Claude's reply confirms this; repeatedly
asking the same question without new evidence is not progress. This unknown
does not by itself decide the admissibility of every unrelated change.

## Stage checklist and exit conditions

### 1. Establish the current correction's required evidence

- [x] Read Claude's full [PR #13 reply](https://github.com/codefoundry-io/triad-dispatch-spec/pull/13#issuecomment-6071390137).
- [x] Verify A's classifier and model-gate changes against source and test assertions.
- [x] Map the negative review finding to an exact shared requirement and case.
- [x] Separate required evidence for this correction from unmeasured runtime facts.
- [x] Record the disposition and any actual missing prerequisite below.

Exit: an evidence-backed decision on the correction's scope and required proof.
A leader's disposition does not retroactively change a reviewer's verdict.

### 2. Resolve the bounded spec or implementation gap

- [x] State the confirmed defect or contract ambiguity and the minimal delta.
- [x] Classify the gap as Codex, Claude, shared-spec or unmeasured, with supporting
  evidence; challenge questionable instructions as well as questionable code.
- [x] If the shared contract is ambiguous or both hosts are deficient, follow
  R-DECISION-ORDER / R-AUTHORING-SYNC and author the clarification first.
- [x] If implementation must change, update the unit plan with affected files,
  production additions/deletions/net, novel-core size and verification scope.
- [x] Implement the necessary correction with meaningful regression coverage,
  or document with evidence why no source change is needed.
- [x] Record any Claude follow-up in the shared spec with precise evidence.

Exit: a concrete candidate tied to the governing rules and cases, with explicit
limitations. No speculative carrier handling and no native-leg changes.

### 3. Verify and obtain a fresh required review

- [x] Run checks appropriate to changed bytes and evidence; record command,
  environment, result and candidate identity. Reuse history only as history.
- [x] If the candidate or review basis changes, run a complete fresh round under
  the applicable project profile with a new ID and immutable evidence packet.
- [x] Resolve negative findings by source evidence or correction; preserve the
  original NOT_APPROVED round. A majority of SAFE results is not admission.
- [x] Record final admission and integrity evidence for the current unit.

Exit: the current unit satisfies its required review. If it cannot yet do so,
record the precise dependency and useful next action, without endless unchanged
review reruns. The next implementation unit starts after this gate.

### PR #13 reply reconciliation — 2026-10-09

Read replies `6073991579` and `6074188589`; verified main `3afc4d7`, PR #12
`6a2883d`, PR #13 `5c040ff`, A source `49910604` with concurrent dirty work.
Detailed dispositions and comment links are in the execution plan.

- A's Gemini >=0.63.0 implementation and boundary test source were inspected;
  A's test run is reported, not rerun here. `tests.A` re-pins remain after PR #13.
- A agreed to opaque model transport. AGY equals-form success is reported for
  one ordinary pin; raw capture and option-shaped/Claude parser proof stay limited.
- DL-133's C34 sentence needs selection-call/runtime phase clarity before any
  phase change; its OPEN-B diagnostic row predates completed U1a.
- DL-131 contains the requested present-form A documentation corrections;
  historical annotations remain. No new B hook/stream/audit port was identified.
- AGY credits carrier and live schema acceptance remain unmeasured.


This follow-up changes planning documents only. No implementation admission,
shared-rule adoption, vendor dispatch, hook removal or host-native change.

### 4. Implement the remaining shared items, one unit at a time

Each row needs its own bounded plan, rule-to-code-to-test mapping and required
review before the next unit starts. Confirm current spec and source before
expanding the row into a plan; this queue is not a claim of exhaustive coverage.

| Order | Shared outcome | State | Evidence / completion condition |
|---|---|---|---|
| 1a | R-MODEL / DL-116 / C18: Google catalog gates | COMPLETE (bounded unit) | Common Gemini >=0.63.0 on raw/legacy/v2. Full suite 1,856 passed/4 skipped; final affected modules 185 passed/4 skipped; dedicated GREEN and validator passed. Round 4 all four SAFE with matching integrity; exact temporary cleanup complete. Remaining optional notes and full-C18 limits below. |
| 1b | R-MODEL / DL-116 / C34: Claude catalog and identity | U1a/U1b COMPLETE | Catalog and default units passed their recorded gates. Native Claude is excluded. |
| 2 | R-CLASSIFY / R-AUTH: remaining measured errors and carriers | EVIDENCE MAPPING | Map remaining shared cases to B code and tests; measured carrier scope remains explicit. |
| 3 | R-CLEANUP / DL-77: declarative roots and deletion ownership | HOLD: RESPONSIBILITY AUDIT | Decide minimum remaining artifacts/cleanup before adding declarations; see current position. |
| 4 | DL-107: AGY shared settings interaction (U7) | COMPLETE (bounded unit) | Transaction removed; approved profiles installed; final2364passed/4skipped and all-four SAFE R3, integrity matched. Live probe does not prove universal write prevention. U8 installation coexistence, including B's DL-108/109 investigations, is WITHDRAWN by D-U8-WITHDRAWN-20261010; do not reinstate it here. |

- [ ] Complete the queued shared units with linked proof for each.
- [ ] Reconcile remaining shared-log B rows and disclose any unassessed scope.

### 5. Handoff and integration decision

- [ ] Present completed rules, code, tests, review receipts and remaining limits.
- [ ] Complete any required combined pre-merge review.
- [ ] Obtain applicable owner approval before merge, installation or release;
  record each separately, without treating one as proof of another.
- [ ] After the authorized work is complete, retire this task's session hook
  and temporary startup instructions using the cleanup checklist below.

## Completion cleanup — owner instruction, 2026-10-09

This hook and its task-specific startup instructions are temporary. Once the
authorized work is complete and its required verification/review is recorded,
perform this cleanup without asking again. A single finished stage, a blocked
review or an interrupted session is not completion of the whole task.

- [ ] Record the final outcome, evidence and any explicitly deferred work here;
  mark this document COMPLETE and historical, with no active next action.
- [ ] Remove only the SessionStart handler in the original checkout's
  `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch/.codex/hooks.json`
  whose command reads this SoT. Preserve unrelated handlers. Remove
  the file only if this task still owns its entire remaining configuration.
- [ ] Remove the temporary `Spec-to-code continuation` section from project
  `AGENTS.md` and the TRIAD spec-to-code routing row from workspace `AGENTS.md`.
  Preserve unrelated changes and standing development policies.
- [ ] Verify that no active hook or startup instruction still loads this completed
  task. Record the cleanup result here and report it to the owner.

Retain the SoT, historical checkpoints and review receipts as evidence. Finished
steps belong to completion history, not continuing instructions. Do not replace
the retired hook with another recurring reminder or alter global trust settings
as part of this cleanup. The completion trigger does not authorize merge,
installation or release beyond the separately approved scope.

## Evidence register

Stage 1/2 disposition (2026-10-09): latest remote main remains `3afc4d7`.
C43 explicitly supplies a failed run with vendor exit 1 and a contract sentence
as its test input; R-CLASSIFY requires the sentence/token mapping on its own CLI.
R-CLASSIFY Recorded limits and D-MEASURED-SHAPES accept a contract row or vendor
source as phrase evidence and forbid coding unmeasured channel shapes. The
quota phrase is documented, its AGY carrier is not. Gap disposition: B's missing
phrase is a code defect already corrected; the unknown AGY carrier is a recorded
runtime limit, not evidence for a speculative wrapper change. No normative rule
change is needed for this bounded unit. Prior review lacked these complete rule
excerpts and the maintainer's confirmed reply. A new review must assess this
evidence basis independently; the leader cannot retroactively admit round 1.
The local shared audit records this follow-up for both hosts. Only comment/test
documentation changes were needed now; classifier logic is unchanged from GREEN.

| Evidence | Verified basis / result |
|---|---|
| B candidate | Baseline `632f42633d3a92d6cb27168cd15c4d4debd8558c`; quota change in `bin/_common.py` and `tests/test_vendor_quota_contract.py`, still uncommitted. Other dirty work is separate and preserved. |
| Shared spec | Main read at `3afc4d7`; [PR #12](https://github.com/codefoundry-io/triad-dispatch-spec/pull/12) checked at `1a5ab9a68bce42101b150a972d80adfae1788fd7`; B audit [draft PR #13](https://github.com/codefoundry-io/triad-dispatch-spec/pull/13) at `7cb188a8`. Drafts are not merged/adopted rules. |
| C43 checks | Historical RED: two quota positives failed. Focused GREEN: 40 passed. Full B suite: 1,846 passed, 4 skipped. These prove the recorded candidate, not later edits or live AGY delivery. |
| Formal round | `triad-c43-quota-20261008-r1`: Claude, Flash and Astra SAFE; Google Pro NOT-SAFE with carrier question. Overall NOT_APPROVED, ROUND_INTEGRITY_OK. Durable root named above. |
| Fresh formal round | `triad-c43-quota-20261009-r2`: all four SAFE, ALL_SELECTED_APPROVED, ROUND_INTEGRITY_OK. Digest `276c8d2211934b3dcb09ae62deb0eedac31d7ab75236a63091bdff181d7fcd99`. Receipt: workspace `_runs/reviews/triad-c43-quota-20261009-r2/owner-selected-review-receipt.json`. Exact temporary stage/cwd removed after export; custody and results retained. No fixed Terra-ledger admission claimed. |
| Claude source | Clean source inspected at `3b79a8e54c34f0baa86f96ae27cf2f801f127c1e`: quota `af50c468`, gates `86cffe93`, result-error signals `3626aab7`. Source/test assertions inspected; A's suite was not rerun here. |
| Historical detail | [2026-10-08 checkpoint](2026-10-08-spec-to-code.md). Its October 2 predecessor predates already shipped v0.2.558; do not repeat that implementation. |

## Progress update discipline

Check a box only with evidence. For each completed step, append a brief entry:
`date | stage/unit | gap disposition | rule/case | files + commit or dirty fingerprint | command/result
or source evidence | review/limits | next action`.
If work is blocked, identify the missing fact and why that exact requirement
needs it; distinguish it from a limitation that can remain open. Keep the active
stage and next action above current. Never erase failed-round evidence.

- 2026-10-09 | Resume setup | Owner-requested staged workflow recorded here;
  project SessionStart hook and AGENTS routing added. Product implementation
  stages remain unchecked beyond the already verified evidence.
- 2026-10-09 | Resume verification | Python 3.12.13: hook JSON parsed, matcher
  accepts startup/resume/clear/compact, command emits exactly the SoT bytes from
  both repository root and a nested directory. Five stages and the core
  spec-development principle checked; `git diff --check` passed. No product
  behavior changed or product test suite rerun for this documentation setup.
- 2026-10-09 | Completion lifecycle | Owner requests removal of the task hook
  and completed startup instructions after completion. Cleanup is now a required
  final checklist; the current unfinished task's hook is retained.
- 2026-10-09 | Stage 3 complete | Focused current checks: 40 passed. Fresh
  four-leg review admitted the unchanged classifier logic and clarified evidence
  scope. Claude's two Minor notes: record AGY reachability (accepted below), and
  optionally add C43's plain-capacity sentence (deferred to remaining classifier
  coverage; no current behavior defect). Exact phrase is absent from current
  tests. No product change follows these nonblocking suggestions in this unit.
- 2026-10-09 | Runtime limits | AGY credits classification is currently reachable
  only from stderr at nonzero vendor exit. A stdout/result.error carrier would
  currently yield unknown/1, or vendor-error/65 for an exit-zero error result.
  Neither carrier is claimed observed. The codex quota row has no Codex wrapper
  consumer on this host; it is classifier data only. Add measured carrier tests
  when evidence exists, without changing either host's native leg.
- 2026-10-09 | Hook delivery | Fresh session
  `01a11e0b-f50f-7123-a0ed-b12d3b1fe277` received the SoT in developer hook context;
  no file tools or project work ran. Exact rollout inspection confirms the core
  principle and current stage. Receipt: workspace
  `_runs/infra/20261009-spec-to-code/hook-delivery-receipt.json`.
- 2026-10-09 | Stage 4 / Google model pins | Dedicated fresh source executor
  `google_pin_skill_red` required catalog refusal from the current skill. Code
  RED: 7 failed, 1 skipped, 58 deselected (expected gates). While separating
  those gates from version checks, confirmed the existing Gemini 3.8/0.61.0
  floor guards a vendor-source-backed remapping condition. R-GOOGLE's only-0.34.0
  sentence conflicts with R-CLI-VERSION's known-defect exception. Wrote the
  shared decision proposal and maintainer request; asked the owner before
  changing that policy. No GREEN, formal admission or completion claimed.
  The unfinished candidate and RED evidence are retained outside source; product
  files were returned to their exact pre-unit state without touching other work.
  Restoration verification: quota/exit-token/v2-Google-wrapper tests returned
  **96 passed, 4 skipped in 5.30s**; both repository diff-whitespace checks pass.
  Existing `test_v2_google_wrappers.py` +20-line dirty change remains intact.

## Session loading

Owner resolution, 2026-10-09: "Gemini믄 63부터 지원하는걸로해".
Latest stable release v0.63.0 was verified from official GitHub. Shared main
was fetched again at `3afc4d7`; A source now at `e275ee8638c1b3edf8936aef3fbd8e1504abad33`
still uses `_GEMINI_VERSION_FLOOR = (0, 34, 0)` in its Gemini wrapper. The shared
handoff requests A's equivalent update; A source is untouched. New code RED:
9 failed/3 passed, then boundary GREEN 46 passed. Prior catalog RED is retained.
An unsafe bulk-test rewrite was rejected by automatic approval and never ran;
explicit individual patches were used, preserving existing dirty changes.
Full source executor run: 1,856 passed, 4 skipped in 391.28s on macOS 26.6.2
arm64 / Python 3.12.13 / pytest 9.0.3; source fingerprint unchanged throughout.
The source validator passed and selected behavior matched the shared rule.
Stale explanatory wording was corrected afterward (routing catalog text,
prerelease example, Korean lifecycle text, plus verifier docstring); no executable
logic changed. Shared owner decision and A request are pushed to draft PR #13
at `2918ed5`; shared checks 182 passed and one authoring map valid. No tag/adoption.
Final fresh source executor confirmed correct behavior after those corrections:
152 passed, 4 skipped; validator passed; HEAD/status/hashes/fingerprint unchanged.
Evidence: workspace `_runs/infra/20261009-spec-to-code/final-green-executor/`.
Shared main fetched again before review remains `3afc4d7`.
Google unit round `triad-google-pins-20261009-r1` returned three SAFE results
and Claude NOT-SAFE for stale prerequisite descriptions. Integrity matched;
NOT_APPROVED is retained and exact temporary stage/cwd were removed after export.
The three contradictory statements were corrected. Five Minor notes were
verified: moved malformed-version fixtures above the support floor, documented
existing local exit 3, scoped SECURITY's catalog claim to admission/dispatch,
fixed one adapter comment and marked the retained model data historical.
No executable logic changed. A fresh complete review follows affected checks.
Google round `triad-google-pins-20261009-r2` also remains NOT_APPROVED with valid
integrity: Claude requested the missing roster/schema evidence; three siblings
returned SAFE. The schema has no Google model enum, only nullable nonblank text;
the resolver retains placeholder validation. Expanded the next packet to those
consumers and added resolver-to-adapter pin tests on both routes, plus explicit
legacy/v2 stale-version receipt negatives. Restored historical 0.2.548 notes and
added a clearly unreleased compatibility note. Affected checks: 182 passed,
4 skipped in 6.70s. Source-skill instructions and executable logic are unchanged.
Round 2 evidence is retained and exact stage/cwd cleanup is complete. Fresh
round `triad-google-pins-20261009-r3` is next; no prior approval is carried over.
Round 3 remains NOT_APPROVED despite no Critical/Major code finding: Claude
disclosed an out-of-boundary bin-directory search. This is a reviewer/workflow
failure, not implementation evidence for a code change; valid source integrity
does not excuse it. All producers terminated; exact stage/cwd cleanup is complete.
Accepted three Minor notes: exact raw exit-3/failure coverage, explicitly scoped
Gemini exit wording, and historical v0.61.0 settings-guide basis. Affected tests:
185 passed, 4 skipped in 6.64s. For fresh round 4, each reviewer must validate
every read/search file against the exact allowlist and must not search directories,
wildcards or the repository. Same authorized scope; no permission expansion.

Final Google unit: `triad-google-pins-20261009-r4`, all four SAFE,
ALL_SELECTED_APPROVED / ROUND_INTEGRITY_OK. Digest
`a5b3a6ae8ead7a7eab68f192d41835fbc8f6e536f102c8a8c922b37708ddb686`;
reviewed fingerprint `840f0e26340a583e60aa7db366a726afd8b6b7aa6f5291beeb4bea29659cb6ef`.
Receipt/adjudication/export and exact cleanup evidence are retained at workspace
`_runs/reviews/triad-google-pins-20261009-r4/`. Prior failed rounds remain retained.
No product behavior changed after final review. Product changes remain local
and uncommitted; shared normative decision was pushed at `2918ed5` to PR #13.

Three optional Minor notes remain documented, not blockers: (1) dash-led model
syntax may warrant a shared policy only after vendor-parser evidence; no flag
reinterpretation is currently established, so do not guess it; (2) the raw
test's environment-absence assertion is weak without setting a synthetic key,
so do not treat it as independent scrub proof (formal shared-probe coverage does
set the key); (3) the new roster test uses a synthetic preflight receipt, while
separate actual-wrapper tests cover unknown-pin acceptance and dispatch. A
combined unknown-pin bridge is optional coverage, not live-service proof.
The broader spec-to-code task remains open; retain the SoT hook until its whole
completion checklist is satisfied. Next unit is the separate Claude catalog/
identity correction, with native legs excluded.
Shared audit and development-log evidence were published to draft PR #13 at
`cff8a20` after one valid authoring map and 182 passing shared tests. The support
decision itself remains at `2918ed5`. Both repository whitespace checks passed;
the shared-spec tree is clean, and the product tree retains its intentional
uncommitted work. This publication is not merge, adoption, installation or release.


## Integrated planning handoff — 2026-10-09

Execution follow-up: user authorized proceeding. U1T's actual wrapper parser
spike checked 24 combinations without dispatch; equals values were retained and
separate option-shaped values refused at argparse. U1's existing adapter tests
were reused in a diagnostic-only module: 3 expected RED failures, 2 passing
controls (0.36s); root causes are alias mismatch omission and table/shorter-ID
coupling. Shared evidence was pushed to PR #13 at `6e86626`; authoring map valid,
182 spec tests passed (0.67s). Copyable Claude handoff is linked above. No U1/U1T
production fix or admission is claimed; the next action remains independent
diagnosis and shared disposition of unexposed selection/effort behavior before
the complete catalog-removal correction.

The owner clarified that both hosts are implementing the same spec concurrently,
requested an execution/development plan and five bounded investigations, and
selected Luna/high for contextual prompt-choice probes when nuance repeats.
The linked plan and research note record these instructions and findings.
No production code changed in this planning turn.

New evidence: Gemini 0.63.0's isolated real parser reinterprets separate-token
`--help` model values; equals encoding preserved tested values. U1T is a new
bounded transport investigation/change candidate, not a model grammar ban.
Current B's actual AGY v2 schema already excludes null from its route enum;
95 provider-free tests passed with 4 skips. Remaining live schema acceptance and
the exact AGY credits carrier remain unverified. The first raw probe runner
omitted normal environment/preflight/containment boundaries; it was disabled
before any provider call, with required prerequisites recorded. DL-124..126
requires no newly identified B port; DL-110/121 needs shared documentation work.

Shared evidence and maintainer requests were published in draft PR #13 at
`c1c7f13c792ce2e39f1e5317779f068401c4c307`; the title/body now describe the actual
floor change, investigations and final bounded review evidence. Shared checks:
one authoring map valid, 182 tests passed (0.71s), whitespace check clean. Remote
head and draft/open state confirmed; shared working tree clean. Product plan,
SoT and research remain local alongside intentional dirty work. No adoption,
merge, installation, release or whole-task completion is claimed. Next action:
the linked plan's U1T shared disposition and U1 code-to-case mapping.

The original checkout's `.codex/hooks.json` prints this file on startup, resume,
clear and compaction only when cwd is this reliability worktree or a descendant.
Codex 0.160.0 loads linked-worktree hook declarations from the original checkout
(official `codex-rs/config/src/state.rs` and `loader/local.rs` at rust-v0.160.0).
The hook is read-only; it does not change checkboxes or run work.
The exact hook definition must be trusted through Codex `/hooks` before it runs.
Project `AGENTS.md` also points here. A workspace-root session uses its
TRIAD-specific AGENTS routing; a child project's hook is not assumed to load
upward into the workspace root. Verify fresh-session delivery separately from
the hook command's output.

Activation status: **TRUSTED AND ENABLED**. On 2026-10-09 the owner explicitly
approved the original repository's folder trust and this SoT hook's permanent
trust. Applied through Codex CLI 0.160.0's normal folder-trust and `/hooks`
screens; the exact handler displays `Trusted` and enabled. No trust bypass or
permission weakening was used. Worktree-local hook declarations were not loaded:
the version's official loader redirects them to the original checkout. Moved
the single task handler there and removed the unsuccessful worktree-local hook
and temporary config layer. Direct checks prove exact SoT output from this
worktree and a nested directory, and zero output from the original checkout
or workspace root. Fresh-session delivery is verified by the receipt above.
The injected context is truncated at the configured 3,500-token allowance;
the AGENTS entry requires reading this full file before work.

PR12head8ec55d3 was inspected in this continuation: R-PREPARE/DL-53 now
describe A current link disclosure rather than its stale lexical-walk work.
This is an A factual correction; no U3d runtime change or automatic B port.

Initial GREEN:6failed/291passed/4skipped. Six existing authorization cases pinned
the previous web-permission sentence; shared exact clause wording changed.
The legacy renderer also uses the common helper, so this wording reaches both
legacy and v2 authorized paths. Updated expectations independently extract the
shared fenced payload; all argv, authorization, digest and retry checks remain.
No production change for this failure. Fresh GREEN follows with fifteen hashes.

U5a R1 NOT_APPROVED, integrity matched: one verified stale no-web reference,
one unused constant and missing upstream-hash evidence in the review packet.
Updated reference, removed dead constant/test-only replacement, and computed
exact upstream git-show hashes for R2. Default authorization stays false; both
legacy and v2 use the shared no-web wording. R1 evidence exported/cleaned.
Fresh GREEN-r2 and complete R2 follow; no new shared design.

U5a R2 NOT_APPROVED, integrity matched: simulated UTC2026-10-11 reproduced
a wall-clock-dependent test (1failed). Fixed only the test using its existing
PreparationClock and a changed-value assertion; same probe now1passed.
Production/docs unchanged from full GREEN-r2(2273/4). Fresh dedicated affected
GREEN-r3 and four validators follow, then complete R3. R2 optional parser
refactor is nonblocking and not added; no new design or runtime change.

R3 retained two nonblocking source-supported observations: a damaged prompt
bundle on legacy default rendering may fail closed with traceback/exit1 instead
of the handled exit2 diagnostic (no damaged-install runtime probe); the public
mechanical-fields table omits the prepared-date explanation, while runtime/retry
behavior is correct. Both reviewers and leader keep them nonblocking under the
owner three-pass bound. No fourth prompt round or new required backlog is added.

U5b R1: all-four SAFE, matching integrity; Claude identified stale legacy-only
web-request wording and an ambiguous release attribution. Corrected three
documentation files only. Production/tests remain identical to full GREEN2280/4.
R1 adjudication/export/exact cleanup completed; fresh affected verification and
complete R2 follow. Three equivalent code-refactor suggestions are nonblocking
and add no required backlog.

U5b R2 NOT_APPROVED with matching integrity: installation EN/KO still described
v2 as no-web by default. Corrected that material omission and the same stale
default in current AGY/project guidance. Historical release notes retained.
No production/test edits; R2 adjudicated/exported/cleaned. Focused documentation
and skill checks, then a complete fresh R3 follow; prior approval is not reused.

2026-10-10 | U5b publication | Source b6680818ac562815c6e2280e1f2b122c1ae6cd0d and shared 7fb5bb2fc1a663d7822e72f17c3c49518016391a pushed and verified against their remote branches. Shared authoring1/1 and182tests passed. PR13 reply https://github.com/codefoundry-io/triad-dispatch-spec/pull/13#issuecomment-6094950337 read back exactly. All-three review stages/cwds cleaned; R1/R2 evidence retained. Next U1T uses existing Gemini/parser evidence and A agreement; Claude/AGY parser gaps remain separate. Whole-task hook retained.
