---
name: triad-antigravity-dispatch
description: Use when an owner explicitly requests an Antigravity consult or an authorized cross-family workflow assigns the primary Google-family review leg.
---

# triad-antigravity-dispatch
Dispatch one Antigravity CLI (`agy`) request through the installed absolute
`antigravity_wrapper.py` launcher. This is the primary Google-family leg for
individual-tier calls.
When a Google-family leg is required, prefer agy when it is available.
Gemini Enterprise/Business, Vertex, or API-key is eligible only after a
pre-dispatch availability failure proves that agy cannot be started on the
configured route. An agy content, extraction, or schema failure after dispatch
does not make agy unavailable and must not trigger Gemini fallback. Handle that
result through the agy result or repair path; for a formal review, the agy leg
is invalid. If neither route is available, the required Google leg is
unavailable and a formal review round is invalid.
Fallback eligibility is limited to a no-final-summary numeric exit status `4`
(`EXIT_BINARY_MISSING`) paired with the wrapper-owned pre-submission diagnostic
`agy start failed before request submission: stage=exec errno=` for a supported
missing or unstartable executable. Any final summary proves post-dispatch
handling and is fallback-ineligible. Missing or invalid `TRIAD_AGY_BIN` and a
missing `agy` on `PATH` are fallback-ineligible route-setup errors under the
current wrapper contract; surface them so the owner can install or configure
AGY or explicitly authorize a separate Google route.
Bootstrap reports a discovered `gemini` executable as a binary candidate only;
it does not prove account tier, authentication, or model access. A successful
preflight or dispatch in the owner's authenticated terminal confirms configured
route availability and tier/model access only. If AGY is unavailable before
submission, ordinary/non-formal Gemini fallback remains available. Formal use
must pass the canonical formal proof gate in the
[formal reviewer routing contract](../triad-cross-family-review/references/reviewer-routing.md).
## External dispatch authorization
Before sending any prompt or file to the external provider, confirm owner
authorization covers the provider, destination, task scope, and approved data.
An explicit user request from the owner to call agy, including an invocation of
this skill or `triad-cross-family-review`, supplies that authorization once
within the stated scope. A matching standing authorization also counts; record
its reference. Reuse it without asking again while the provider, destination,
worktree, task, and data boundary remain unchanged. For worktree review, that
scope is the repository data admitted by the shared review contract. Credentials,
tokens, cookies, authentication files, environment dumps, provider logs, and unrelated
paths remain excluded.

## Review prompts

For a review request, read and render the
[shared review prompt contract](../triad-cross-family-review/references/review-prompt-contract.md).
Select `consult` or `advisory-review` for a standalone request and
`batched-full-coverage` for an operational formal cross-family leg with exact
batch metadata. Reserve `formal-gate` for the unbatched compatibility route.
Dispatch only after the objective, target, approved data, exclusions, and
selected result profile are determined.
For this skill, `provider` is Antigravity and `destination` is the installed
Antigravity wrapper route in the owner's authenticated terminal unless the
owner authorizes a narrower destination.
Route selection and prompt construction remain separate decisions.

## Cross-family review invocation
Formal three-family preparation is defined by the
[triad-cross-family-review skill](../triad-cross-family-review/SKILL.md). Use
its leader-prepared shared review directory as agy's `--cwd` and keep the
provider leg read-only.
Before a formal dispatch, require authenticated `agy --version` evidence that
reports `1.1.10` or newer and authenticated `agy models` evidence that the
exact `gemini-3.1-pro-high` selector is present. An older or unprobeable
version leaves the required Google leg unavailable. The current formal argv
uses the exact stable selector and omits `--effort`:
```python
review_argv = [
    "/absolute/path/to/antigravity_wrapper.py",
    "--prompt-file", "/absolute/path/to/agy-review-prompt.txt",
    "--cwd", "/absolute/path/to/prepared-review-directory",
    "--model", "gemini-3.1-pro-high",
]
```

Wrapper preflight reports the requested `model` and `effort` values and proves
argv construction only; it does not claim an `effective_model`. If provider
output exposes identity, it must agree with the requested route; absent
telemetry is recorded as `unexposed` once. After an AGY update, rerun these
three candidates as separate fresh runtime probes:

- `--model gemini-3.1-pro-high` with no `--effort`;
- `--model gemini-3.1-pro --effort high`; and
- `--model "Gemini 3.1 Pro (High)"` with no `--effort` as the historical
  AGY 1.1.7 control.

Catalog presence or provider acceptance alone does not authorize a route
change. Keep the stable slug route unless another candidate is accepted and its
runtime-exposed identity agrees with the requested Pro High route. Any
alternative remains unselected until its fresh successful runtime probe
confirms both conditions. The display-label compatibility route is historical.

For unbatched `formal-gate` compatibility only, return the semantic fields
required by the shared contract: `verdict`, `findings`,
`affected_surfaces_inspected`, and `open_questions`.
Markdown fences do not invalidate this non-Pydantic compatibility route.

For operational formal review, return one strict `BatchReceipt` per
provider/batch under exact custody: persist and hash the exact original UTF-8
response bytes at `<family>/<batch-id>.json`, then validate and admit them under
the shared batched contract.

Archive actual provider request acceptance for the exact outbound stable selector
and archive provider identity when exposed. If identity telemetry is absent,
record it as `unexposed` once without claiming a hidden actual model. Any
selector absence, rejection, or exposed conflict leaves the Google leg
missing/invalid. Do not silently substitute; keep the fallback rules above.

## Invocation

Resolve the launcher once, then invoke its absolute path directly. Pass a short
request with `--prompt`; write long or punctuation-rich requests to a UTF-8 file
and pass its absolute path with `--prompt-file`. Keep the launcher argv as data,
not a shell string.

```python
launcher_argv = [
    "/absolute/path/to/antigravity_wrapper.py",
    "--prompt-file", "/absolute/path/to/request.txt",
    "--cwd", "/absolute/path/to/workspace",
]
```

Run the wrapper from the same authenticated login terminal used for
development. TRIAD inherits AGY permissions from that launch context and does
not select or override them. For ordinary non-formal use, discover an accepted
Google model from current `agy models` output in that terminal and keep the
wrapper's free-form passthrough. Formal use follows the versioned route above.
Antigravity's web tools are native to the provider route, so do not invent a
wrapper `--search` flag. Credentials stay outside approved review data.

## Result handling
An initial tool response with a running session or cell handle is pending, not unavailable,
invalid, or failed. Keep it running and use event-driven status checks until a terminal process
exit arrives; report a concise heartbeat when useful. A poll timeout is only a wake-up boundary,
never a provider verdict or process failure.

The wrapper tool yields captured stdout, stderr, and process exit status. It is
not a structured result object. The exit status and final emitted state are
authoritative. When the exit status is zero, stdout is the answer.

For a nonzero exit, scan captured stderr in memory. Select the last matching `[wrapper] antigravity ...` summary.
Use that final summary as the classification source. Select the last `run-log:` path
without a shell pipeline, keep it as opaque data, and pass it only to the
fresh native proposal-only child defined by the repair protocol; the leader
does not open the raw log.
If no matching final summary exists, do not invent one: preserve the exact exit
status and stderr and classify the invocation as an early wrapper failure. It is
eligible for Gemini fallback only when numeric exit status `4`
(`EXIT_BINARY_MISSING`) is paired with the wrapper-owned pre-submission
diagnostic `agy start failed before request submission: stage=exec errno=` for
a supported missing or unstartable executable. Every other no-summary failure
is fallback-ineligible. Missing or invalid `TRIAD_AGY_BIN` and missing `agy` on
`PATH` remain fallback-ineligible route-setup errors under the current wrapper
contract. Without a `run-log:` path, surface the early failure directly instead
of fabricating a repair handoff.
An early `ok` followed by a corrected `extraction-error` is a failure:
route the final `extraction-error` to repair. Surface terminal, schema,
configuration, and capacity outcomes with their reported reason. Route only
`unknown`, `extraction-error`, and `timeout` to the repair protocol; preserve
the run log for its age-floor cleanup. Treat `permission-unavailable` as an
invalid required leg and a post-dispatch result that cannot activate Gemini
fallback. Treat `truncated-answer` (exit 65) as a deterministic terminal
result: the answer is quarantined, it is not repair-routed, and a new
invocation must ask for a bounded, compact result. Use the documented compact
complete-family retry rule for formal receipt recovery.

## Repair handoff

Follow [the shared repair protocol](../../docs/references/repair-protocol.md).
Set `cli` to `antigravity`. The protocol supplies the fresh native
proposal-only child, proposal-file lifecycle, and owner-controlled local apply
command. No provider invocation occurs during apply.

## See also

- `triad-claude-dispatch` for Claude Code.
- `triad-cross-family-review` for formal review gates.
