# Single CLI invocation implementation plan

> **For agentic workers:** Use `superpowers:executing-plans` inline. The owner approved the bounded proposal with "진행"; no repeated approval handoff.

**Goal:** One wrapper call returns the observed outcome without automatically replaying the whole CLI for capacity or local schema errors.
**Architecture:** Remove the two loops from the existing common driver. Keep extraction, classification, validation, input and evidence interfaces. Preserve the helper signature and compatibility record fields; no replacement scheduler.
**Tech Stack:** Python3.12+, pytest; existing provider wrappers.
**Spec:** Shared R-TERMINAL/C78 and `decisions/2026-10-11-single-cli-invocation.md` in the current shared draft.

## Constraints and scope

Preserve64/server-capacity,66/schema-fail, authentication STOP, transport precedence,
original streams/vendor exit, schema/web prompt injection, result completeness and
round bindings. Vendor-internal retries, explicit review-level retry, native legs,
model/effort, settings and cleanup stay separate. Never manufacture a vendor error.
Owner2026-10-11: if Claude actually reaches its usage limit, close that round's
started producers and use a fresh Sol/xhigh + Astra/high + Google Pro/high three-leg
round, with one common basis. No quota inference from authentication/tool failures.

Production estimate +10–30/-70–110, net reduction40–100, novel core below20lines.
Actual driver delta is +91/-184 (net -93); moving the retained extraction block
out of the removed loop increases diff churn without adding a new responsibility.
Main file `bin/_common.py`; callers preserve compatibility. Tests: new local
subprocess counting/prompt fixtures plus affected existing expectations. Public
English/Korean/security docs and relevant source skill instructions updated only
where they describe the removed policy. No per-file read allowlist or routine log audit.
All Python/tests/provider/Git mutations use `/bin/zsh -lic`, require_escalated first,
host cwd workspace, canonical invocation-owned TMPDIR set before Python.

## Review focus

1. Claude rc0 error-envelope capacity remains64, not extraction-error or success.
2. Nonzero capacity retains vendor evidence and launches once.
3. Schema-invalid answer fails66 without prompt mutation/relaunch; valid answer stays valid.
4. Auth STOP, transport failure and formal binding rejection precede any accepted answer.
5. Initial schema and authorized web clause remain exact; explicit later review retry stays available.

## Task 1: Remove wrapper replay

- [x] Publish shared replacement before dependent implementation; record A/B source and main.
- [x] Write `tests/test_single_cli_call.py` using real local processes and a launch journal. A second launch must make capacity/schema cases fail; success/auth controls pass. Fresh dedicated executor observes RED.
- [x] Remove capacity/backoff and schema-correction loops/constants in `bin/_common.py::run_cli_with_retry`; preserve signature/record compatibility and classification/extraction branches.
- [x] Update affected existing retry-count expectations, initial-clause tests and public guidance. No unrelated parser or logging fix.
- [x] Fresh dedicated GREEN: affected tests, complete suite, four skill validators, diff check and source integrity. No live vendor required for local policy.
- [x] Complete required independent unit review; apply only verified bounded corrections.
- [x] Commit/push source and shared C78 evidence; update SoT and PR13. Final merge remains separate.

## Status

Baseline25372be. Shared7c4946f is pushed, authoring1/1 and182tests passed;
PR13comment6104736069 shares the replacement. First dedicated RED7failed/2passed:
five expected launch-count failures, two test-control mistakes expecting a model
instead of validate_response's documented dictionary. Correct the control to the
literal dictionary. Fresh dedicated RED then observed5failed/4passed; all325
tracked/nonignored fingerprints and HEAD/status matched, exact temp cleanup passed.
The five failures measured3capacity calls and2schema-invalid calls. Implementation
now removes both loops. Leader focused397passed; fresh dedicated GREEN397focused/
2369full passed,4skipped, four validators and diff check passed. Source fingerprints
matched and exact temp cleanup passed. Two exit-code comments were then aligned;
executable AST equality confirms no runtime change after GREEN.
R1 INCOMPLETE after actual Claude monthly spend limit; Pro/Flash/Astra SAFE,
integrity matched, all producers ended and exact stages cleaned. Owner fallback
activated. Fresh R2 Sol/xhigh+Astra/high+Google Pro/high all SAFE, integrity matched,
all terminal handles consumed, custody exported and exact stages cleaned.
Two verified nonblocking Minors: pre-existing duplicate Claude extraction;
authentication troubleshooting still uses "capacity retry" in three public docs,
while the explicit one-call sections and executable behavior are correct. Preserve
these notes without another wording round or automatic parser-refactor backlog.
Evidence: workspace `_runs/infra/20261011-single-cli-call/` and
`_runs/reviews/triad-single-cli-20261011-r2/`. No merge/install/release claim.

This bounded unit is complete: sourcef4d6331 and shared69983bb pushed;
shared authoring1/1 and182tests passed. PR13comment6104953702 records completion,
the active quota fallback, both residuals and A's pending adoption.
