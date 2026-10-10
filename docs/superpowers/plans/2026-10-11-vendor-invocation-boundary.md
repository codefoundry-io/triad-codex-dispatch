# Vendor invocation boundary implementation plan

> **For agentic workers:** Use `superpowers:executing-plans` for this one coherent unit. Do not execute the implementation steps before the input-delivery decision below is settled.

**Goal:** Collect a completed vendor CLI review without implementing its descendant lifecycle or custom pipe transport.

**Architecture:** Keep the current CLI arguments, cwd, environment policy and result parsers. Use invocation-owned temporary stream files and ordinary direct-child supervision; retain terminal result validation and review binding. Vendor descendants and remote execution remain vendor-owned.

**Spec:** Shared `reference/review-rules.md#R-TERMINAL`, C1/C2/C9, and the pending shared decision `decisions/2026-10-11-vendor-invocation-boundary.md`. Current rules still describe the older mechanism until the decision is adopted into the draft.

**Status:** Approved simplification direction; implementation paused on the concrete input-delivery trade-off. This plan supersedes neither completed work nor the other responsibility-audit units.

## Decision before implementation

Recommend defining `stdin_delivery=complete` as exact UTF-8 input prepared and made available to the launched CLI, not proof that it consumed the input. File-backed stdin removes the existing large-prompt BrokenPipe detection when a CLI closes stdin early. Standard `communicate()` also suppresses BrokenPipe; it is not an equivalent drop-in replacement.

The owner approved proceeding with the audit's simplification direction, but did not explicitly select this observable behavior change. Present the real scenario and choices before changing the common rule or code. Do not add file-offset consumption surveillance merely to preserve the old mechanism.

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
- [ ] Settle the input-delivery decision and amend the shared rule/cases/unit/decision; validate and publish the same commit to PR13.
- [ ] Leader writes bounded behavior fixtures against canonical source. Fresh dedicated `triad-skill-executor` observes RED for descendant preservation/final capture and diagnostic independence; preserve success/timeout/auth/binding controls.
- [ ] Replace PIPE reader/writer threads, mirror and group sweep with owned stream files, final snapshot and ordinary direct-child supervision. Preserve public parsers/callers and failure precedence.
- [ ] Replace obsolete thread-phase/group-prescription tests with the five observable scenarios above; retain applicable current regressions.
- [ ] Fresh dedicated GREEN: affected tests, full tests, skill validators and applicable distribution checks. Record exact cleanup and unavailable OS coverage.
- [ ] Complete required independent multi-family unit review, reproduce substantive findings, and follow existing convergence rules. No admission from diagnosis or static checks.
- [ ] Commit/push, update shared evidence and SoT; only then start the retry/evidence reduction units.

## Remaining audit units

After this unit's gate, evaluate outer CLI capacity/schema restarts separately; then consolidate evidence/repeated validation according to actual consumers; finally simplify exact owned-artifact cleanup. U6b/U9's old expansion drafts do not resume automatically. Final integration review and whole-task hook removal remain at completion.
