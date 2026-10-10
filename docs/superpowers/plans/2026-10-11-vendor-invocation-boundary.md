# Vendor invocation boundary implementation plan

> **For agentic workers:** Use `superpowers:executing-plans` for this one coherent unit. The input-delivery decision below is approved; proceed within this unit.

**Goal:** Collect a completed vendor CLI review without implementing its descendant lifecycle or custom pipe transport.

**Architecture:** Keep the current CLI arguments, cwd, environment policy and result parsers. Use invocation-owned temporary stream files and ordinary direct-child supervision; retain terminal result validation and review binding. Vendor descendants and remote execution remain vendor-owned.

**Spec:** Shared `reference/review-rules.md#R-TERMINAL`, C1/C2/C9 and `decisions/2026-10-11-vendor-invocation-boundary.md` at877621c; superseded DL-70/DL-87 queues retired atfb7c962. Both commits are pushed to PR13. Authoring1/1 and182tests pass.

**Status:** Implementation and required verification/review complete. Fresh R3 all four SAFE with matching integrity after the bounded R1 corrections. Publication of source and shared evidence follows; no merge/install/release or whole-task completion.

## Approved input-delivery decision

`stdin_delivery=complete` means exact full UTF-8 input prepared and made available to the launched CLI, not proof of consumption. File-backed stdin removes large-prompt BrokenPipe detection when a CLI closes stdin early. No file-offset consumption surveillance. Existing CLI failure, complete-result validation and authentication STOP remain.

## Global constraints

- Preserve review points, diff/worktree, related-code access, model/effort, auth STOP, schema validation and round binding.
- Preserve each host's native leg and user configuration. Claude source is read-only comparative evidence.
- Timeout/cancellation cannot admit an answer, even if the CLI exits zero while handling termination.
- Full input preparation failure prevents launch. Failed capture/invalid UTF-8 cannot become success.
- Snapshot each output stream after direct-child completion, using its observed byte length and offset-independent reads; do not wait for descendant EOF or follow output written later.
- Do not probe or kill process groups after normal exit. On interruption, terminate/wait/kill only the direct child with bounded waits; no no-orphan or remote-cancellation guarantee.
- No live provider-output mirror. Retain captured stderr for existing diagnosis; best-effort wrapper diagnostics must not replace the result or be replayed after a failed write.
- No retry-policy change, evidence consolidation, new cleanup service, SDK, shell rewrite, installation or merge in this unit.
- Python/tests/providers/Git mutations: `/bin/zsh -lic`, `sandbox_permissions=require_escalated`, host cwd `/Users/chaniri/codex_workspace`; allocate canonical owned TMPDIR before Python.

## Scope and size

Production: `bin/_common.py` transport and its existing `bin/google_diagnostics.py` termination-helper consumer. Expected +100–160/-280–380 lines, net reduction about 180; novel core below 120 lines. Tests: existing transport/stdin/provider/signal/receipt modules, approximately 150–250 edited lines, mainly replacing implementation-specific thread/group fixtures. Documentation: English/Korean/security guidance and this plan/SoT, counted separately.

The diagnostic helper is an existing consumer: adapt it to the same direct-child termination primitive; do not build another transport or retain a general group manager solely for offline probes. Record any additional necessary dependency before changing scope.

## Review focus

1. Large UTF-8 input with large simultaneous stdout/stderr: exact bytes without pipe deadlock.
2. Direct child exits but a descendant holds output descriptors: prompt return without descendant termination.
3. Timeout/SIGTERM/SIGHUP followed by child exit0: failure, answer withheld, direct child reaped.
4. Capture failure/invalid UTF-8 versus real nonzero/auth output: no false success or lost auth STOP.
5. Incomplete or wrong-round verdict with exit0: existing parser and binding rejection remain.

## Task 1: Replace the transport as one coherent unit

**Interfaces:** Preserve `_run_once(...) -> RunResult`, public exit vocabulary, wrapper options and receipt keys. The approved input-delivery meaning must be reflected in the shared rule and C9 before dependent tests/code.

- [x] Refresh main/PR13 and compare A/B source; independently diagnose with Claude, Google and fresh Codex. All three completed. They recommend file capture; Claude additionally proposes retaining timeout group kill, which lacks a measured vendor requirement and is not selected under the approved vendor-owned descendant boundary. Invalid UTF-8 rejection stays, so it needs no new decision.
- [x] Compare standard-library transports in an isolated, provider-free spike. Do not treat it as vendor lifecycle conformance.
- [x] Settle the input-delivery decision and amend the shared rule/cases/unit/decision; validate and publish the same commit to PR13.
- [x] Leader writes bounded behavior fixtures against canonical source. Fresh dedicated `triad-skill-executor` observes RED for descendant preservation/final capture and diagnostic independence; preserve success/timeout/auth/binding controls.
- [x] Replace PIPE reader/writer threads, mirror and group sweep with owned stream files, final snapshot and ordinary direct-child supervision. Preserve public parsers/callers and failure precedence.
- [x] Replace obsolete thread-phase/group-prescription tests with the five observable scenarios above; retain applicable current regressions.
- [x] Fresh dedicated GREEN:238affected/2362full passed,4skipped; four validators and diff check passed. Exact cleanup/source integrity passed; Ubuntu not run. Full suite includes distribution contracts; no release archive requested.
- [x] Complete required independent multi-family unit review: R3 all four SAFE/ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK; exact cleanup complete. R2 failed before start due to a leader script quoting error, not source behavior.
- [ ] Commit/push, update shared evidence and SoT. The next retry-policy unit additionally requires the pending owner choice.

## Remaining audit units

After this unit's gate, evaluate outer CLI capacity/schema restarts separately; then consolidate evidence/repeated validation according to actual consumers; finally simplify exact owned-artifact cleanup. U6b/U9's old expansion drafts do not resume automatically. Final integration review and whole-task hook removal remain at completion.

## Current verification evidence

Fresh dedicated RED:4failed/6passed; corrected standalone stderr-line assertion then reproduced independently (1failed). Source hashes/status stayed unchanged during each run; owned fixture cleanup complete. Evidence: workspace `_runs/infra/20261011-vendor-boundary/{red,mirror-red}/report.md`. The first substring assertion was contaminated by logged argv; the second removes that ambiguity. Broken-display RED occurred on initial logging, not after a completed result.

Candidate removes custom PIPE threads/mirror/group sweep, shares direct-child termination and finite byte snapshot with diagnostics, and drops failed diagnostic lines without buffering them. Initial leader check19passed/4obsolete thread tests failed; those fixtures were replaced with partial file-preparation and actual wait-interrupt behavior. Broader check168passed/1failed: a test incorrectly expected retries from the existing single-call native parser; corrected to one invocation without changing parser/retry behavior.

Current production delta: approximately+140/-281 (net-141), novel core below120lines; tests approximately+180/-344 including new scenarios. English/Korean/security/candidate receipt docs updated. No release, install, adoption or admission claim. Next: correction GREEN and complete fresh four-entry R2.

R1 returned Claude NOT-SAFE and three SAFE with ROUND_INTEGRITY_OK. Its source
instructions retained process-group cleanup and unqualified writer termination.
A fresh dedicated instruction RED selected unnecessary waiting for a vendor-only
stream holder; the TRIAD-owned result-writer control correctly waited. Shared
c8812a5 now clarifies the replacement completion guidance. The correction aligns
the skill/public-v2/convergence references and adapter comment, documents anonymous
file lifetime, fixes a typo, and consolidates duplicate descendant tests. No new
runtime algorithm or lifecycle manager is added. Prior R1 evidence is retained;
its exact stage/cwd cleanup is complete. Fresh instruction GREEN selected both
expected actions;236focused passed. Full2359passed/4skipped and one obsolete
distribution assertion failed on the former completion sentence. Only that
expectation is updated; runtime and skill bytes are unchanged. A fresh executor
will run the full distribution module and four validators. The completed full
run supplies the unchanged remainder's evidence; do not rerun it solely for an
assertion text update.

Final complete distribution module42passed, all four validators and diff check
passed. R3 all four SAFE with matching integrity and exact cleanup. Two verified
nonblocking Minors are deferred: missing sys.stderr at interpreter startup fails
before provider launch; README cleanup prose retains generic writer wording while
the operational instructions explicitly name TRIAD-owned writers. Source/runtime
and skill bytes remain the reviewed bytes. No further prompt iteration or automatic
backlog; see workspace investigation `r3-adjudication.md` for evidence and impact.

Necessary dependency discovered before dedicated GREEN: the candidate receipt description is hash-pinned. Synchronize its exact shared bytes, source manifest, `validate_v2.py` commit constant and existing provenance test/README to sharedfb7c962. The other three schema payloads are byte-identical; no wire constraint, validation algorithm or deployed revision changes. This adds one production constant line to the coherent unit. GREEN had not begun snapshots/tests when this was corrected.
