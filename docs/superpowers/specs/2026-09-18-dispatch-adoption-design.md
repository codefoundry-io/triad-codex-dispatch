# Dispatch adoption: spike findings and bounded slices

## Goal and authority

Adopt useful transport and review infrastructure from the Claude-led
`codefoundry-io/triad-dispatch` into this Codex-led project. Codex remains the
native leader and native reviewer. The upstream `codex exec` worker corresponds
to this project's external `claude -p` worker; it is not a reason to introduce
an external Codex worker here.

The owner authorized spikes, planning, and implementation. This document makes
the first implementation unit concrete. Later rows are separate candidate
slices, not permission to change provider settings, governance, or admission.
Final merge and deployment are separate boundaries.

## Source and experiment custody

- Current product base: `2abfc071390e7c7aae06f0ab8af905a382b87a80` (0.2.553).
- Upstream snapshot: `b2cab9c43495f42913aef740cded59735d701086` (0.2.828).
- Implementation branch: `codex/triad-adoption-process-cleanup`, using the
  existing `triad-codex-dispatch-reliability` checkout. Its unrelated dirty
  `AGENTS.md` is preserved and excluded from task commits.
- Local experiment root, relative to the host workspace:
  `_runs/infra/20260918-triad-adoption-spike-Tcszot/`.
- Baseline: **805 tests passed in 169.91s** under Python 3.12.13 / pytest 9.0.3.
  No provider call is required by the repository suite.

| Spike | Observed result | What it establishes |
|---|---|---|
| Process cleanup | Unchanged `_run_once` timed out; direct child exited on TERM; same-group descendant ignoring TERM survived. Fixture cleanup verified no survivors. | A current lifecycle defect, not speculative hardening. `process/evidence.json` and `process/report.md`. |
| Claude stdin and native schema | One synthetic `claude -p` call with stdin and `--json-schema` returned the exact structured marker; exit 0; 7.089s. | Compatible transport on Claude Code 2.1.271. Session/usage/model/denial metadata exists. `claude/result.json`; no review-quality claim. |
| Committed review worktree | A synthetic detached checkout retained committed bytes while the developer tree changed; dirty/untracked bytes were absent; common Git metadata was shared. | Useful for committed review with concurrent writers, not dirty-input review or OS isolation. `worktree/result.json`. |
| AGY hook | Offline helper allowed `view_file`, denied `write_to_file`; synthetic load checks produced PASS with rows and VOID without rows. AGY 1.2.5 help inspected. | Handler compatibility only; actual AGY discovery and enforcement are unproven. `google/fixture-results.json`. |
| AGY terminal error | A canned nested `result.error` lost its message/code in current failure diagnostics; classification remained `vendor-error` / 65. | Diagnostic loss for that fixture. Nested shape is defensive compatibility input, not a claim about Google's documented schema. `google/spike-report.md`. |
| Gemini | Local CLI 0.46.0 help inspected; no provider call. | No reason found to replace the existing pinned formal policy/selector/single-call route. |

The Claude envelope estimated USD 0.199142 and reported 49,378 cache-creation
input tokens. These are provider estimates for one probe, not subscription
billing, review cost, or a performance benchmark.

## Ordered adoption roadmap

| Slice | Priority and decision | Benefit | Cost / prerequisite |
|---|---|---|---|
| S1: shared process cleanup | High; implement now | Terminates surviving same-group descendants after timeout/interruption. | POSIX lifecycle regression, safe fallback, bounded escalation. |
| S2: AGY terminal diagnostics | Medium; implementation-ready after its own TDD plan | Keeps bounded typed failure detail for triage. | Accept only documented/defensive scalar shapes; no retry or answer-text classification. |
| S3: Claude stdin | Medium; live compatibility confirmed | Keeps task prompt out of argv; uses existing shared stdin writer. | Prove structured binding, interruption, and one-call behavior unchanged. |
| S4: Claude provenance receipt | Medium; separate evidence-only design | Preserves session/model/usage/denial metadata beyond the capped stdout head. | Bounded sanitized sidecar outside verdict; denials are not automatic invalidation; estimates are not billing. |
| S5: effective cwd receipt | Medium; source gap confirmed | Makes wrong-root failures diagnosable. | Apply current path redaction and audit policy; no raw environment capture. |
| S6: committed review checkout | High, conditional; synthetic semantics verified | Prevents developer-tree edits from disturbing committed review bytes. | Explicit existing-worktree policy decision and compatible AGY UUID/cwd route; preserve dirty-review mode; lifecycle costs and shared Git metadata remain. |
| S7: AGY allowlist hook | High, conditional; offline only | Can deny off-list tools before execution. | Disposable local hook and live discovery/deny proof; preserve UUID/cwd/deny guard. Do not alter global or project records as an inferred prerequisite. |
| S8: AGY read telemetry | Medium; diagnostics only | Records observed packet reads for triage. | No coverage/admission credit or automatic VOID policy. |
| S9: read-only drift diagnostics | Medium; bounded follow-up | Reports CLI/model/extension compatibility drift. | Version/help probes first; no auto-update or global settings changes. |
| S10: adversarial path/origin tests | Low; select only reachable cases | Protects adopted boundaries. | Do not import the unrelated Claude hook parser wholesale. |
| S11: duplicate JSON member handling | Low; needs a reachable transport case | Can reject ambiguous raw JSON before model validation. | Current native structured output already reduces this risk; no repair/re-ask loop. |

## S1 behavior and implementation boundary

**One behavioral claim:** on timeout or interruption, the wrapper attempts to
terminate surviving members of its verified child-owned process group even if
the direct child exits first, without signaling the wrapper's own group.

Capture the provider PGID immediately after successful `Popen`. Only a group
equal to the new child's PID and distinct from the wrapper group qualifies.
Use that saved identity for cleanup; never resolve the already-exited leader's
PID again. If group identity is unavailable or unsafe, retain direct-child
termination as the fallback.

Send TERM, wait for the direct child within the existing bound, and then check
the saved group independently of the child's wait result. A surviving group
receives KILL. Reap the direct child with bounded waits. Timeout classification
and interruption propagation remain unchanged. A missing group is already
clean; permission failure must not redirect a signal to another group.

This does not promise control over descendants that leave the captured group
(including by creating another session), OS-enforced containment, or elimination of the residual OS identifier-reuse
race. No new process registry, daemon, provider retry, or runtime dependency is
needed. Planned net production delta is below 100 lines, novel core below 100,
and one behavioral claim, within the S/M slice budget.

## S2 behavior and implementation boundary

**One behavioral claim:** an existing AGY terminal failure retains a bounded
provider error summary in `extraction_error` without changing its classification,
exit code, admission, or number of provider calls.

Start S2 from S1 commit `46dab9f388ff0a3992a2889061aa2563b74d11c0` on the stacked
branch `codex/triad-adoption-agy-diagnostics`. Preserve the unrelated dirty
`AGENTS.md` and S1 bytes. The owner requested the next planned slice.

The source already retains the last terminal result but constructs failure
detail from stderr/status only. Accept `result.error` as a string or a JSON
object containing string fields in priority order `message`, `error`, `detail`,
`code`. Select the first field with a nonempty line; strip that line and retain
at most 512 characters. Ignore unsupported types, nested values, and empty
strings. Do not serialize arbitrary objects or copy response text.

Append `; terminal_error=<summary>` only to the existing nonzero-vendor-exit or
non-success-status failure detail. In the nonzero-exit path, classify the
original stderr/status first, then append the summary. Existing classification
may vary with stderr; S2 must not change it. Preserve timeout/missing-result
handling and the formal post-completion permission-denial success exception.

This is diagnostic data, not a new routing, retry, or admission signal. Existing
audit redaction/capping and sensitive failure-run-log handling remain unchanged;
the audit may truncate the combined field further. The 512-character bound
applies to the newly selected provider text, not to existing stderr or the whole
run log. Historical changelog entries and shared logging behavior are outside
this slice. Nested error objects are defensive fixture compatibility, not a
claim about Google's documented payload schema.

Expected production net delta <50 lines, novel core <50, one behavioral claim.
Use offline interpreter regressions and the existing formal/main integration
tests; no provider call, settings change, new dependency, install, or merge.

## Retained contracts and excluded imports

Keep Claude's native schema constants and local binding validation, AGY's exact
project boundary and selector receipt, Gemini's pinned plan policy and selector,
formal one-provider-call behavior, fresh round identities, and current verdict
schema. Keep Codex native. Do not import upstream provider retry/schema repair,
degraded admission, coverage admission, permission installation ownership, or
whole review-worktree lifecycle machinery.

## Sources

- [Current transport and cleanup](https://github.com/codefoundry-io/triad-codex-dispatch/blob/2abfc071390e7c7aae06f0ab8af905a382b87a80/bin/_common.py#L1227).
- [Upstream saved-group cleanup pattern](https://github.com/codefoundry-io/triad-dispatch/blob/b2cab9c43495f42913aef740cded59735d701086/bin/_common.py#L1959).
- [Current Claude wrapper](https://github.com/codefoundry-io/triad-codex-dispatch/blob/2abfc071390e7c7aae06f0ab8af905a382b87a80/bin/claude_wrapper.py#L42) and [official headless interface](https://code.claude.com/docs/en/headless).
- [Current AGY parser](https://github.com/codefoundry-io/triad-codex-dispatch/blob/2abfc071390e7c7aae06f0ab8af905a382b87a80/bin/antigravity_wrapper.py#L212), [official headless mode](https://antigravity.google/docs/cli/headless/), and [hooks](https://antigravity.google/docs/hooks).
- [Upstream hook](https://github.com/codefoundry-io/triad-dispatch/blob/b2cab9c43495f42913aef740cded59735d701086/skills/triad-cross-family-review/lib/agy_hook.py#L66) and [review-worktree creation](https://github.com/codefoundry-io/triad-dispatch/blob/b2cab9c43495f42913aef740cded59735d701086/skills/triad-cross-family-review/lib/review_scratch.py#L3445).
