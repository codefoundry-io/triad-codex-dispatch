---
name: triad-antigravity-dispatch
description: Use when the Codex leader needs one Antigravity (agy) answer through the installed wrapper, including the primary Google-family leg of a review or a classified repair handoff.
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
Availability failure is limited to a missing or unstartable agy executable or
configured route before request submission. A prompt, packet-identity, Pydantic
import or review-schema, validation, timeout, or capacity failure remains an agy
failure.
Fallback eligibility also uses the authoritative final summary phase when one
is emitted. `phase=pre-dispatch-settings` is necessary, but phase alone does not
prove route unavailability: the reported reason must explicitly prove a missing
or unstartable agy executable or configured route. `phase=dispatch-uncertain`,
`phase=post-dispatch-result`, and `phase=post-dispatch-cleanup` are ineligible
for Gemini fallback.
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
## Cross-family review invocation
Formal three-family preparation is defined by the
[triad-cross-family-review skill](../triad-cross-family-review/SKILL.md). Use
its leader-prepared shared review directory as agy's `--cwd` and keep the
provider leg read-only.
Before a formal dispatch, require authenticated `agy models` evidence that the
exact `gemini-3.1-pro-high` selector is present.
That catalog selector is policy/evidence only. The current formal argv uses the
exact display label `Gemini 3.1 Pro (High)` and omits `--effort`:
```python
review_argv = [
    "/absolute/path/to/antigravity_wrapper.py",
    "--prompt-file", "/absolute/path/to/agy-review-prompt.txt",
    "--sandbox", "read-only",
    "--cwd", "/absolute/path/to/prepared-review-directory",
    "--model", "Gemini 3.1 Pro (High)",
]
```

Wrapper preflight reports the requested `model` and `effort` values and proves
argv construction only; it does not claim an `effective_model`. If provider
output exposes identity, it must agree with the requested route; absent
telemetry is recorded as `unexposed` once. After an AGY update, adopt the base
slug plus `--effort high` only after a fresh successful runtime probe confirms
provider acceptance and identity agreement.

For formal review, return the semantic fields required by the shared contract:
`verdict`, `findings`, `affected_surfaces_inspected`, and `open_questions`.
Markdown fences do not invalidate this non-Pydantic review route.

Archive actual provider request acceptance for the exact outbound display label
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
    "--sandbox", "read-only",
    "--cwd", "/absolute/path/to/workspace",
]
```

Use `--sandbox workspace-write` only for a code task in an isolated worktree.
Discover an accepted Google model from the current `agy models` output in the
owner's normal authenticated terminal; do not apply a version threshold or a
baked model name. Antigravity's web tools are native to the provider route, so
do not invent a wrapper `--search` flag. Credentials stay outside sandboxes.

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
read-only analyzer for repair-routed classifications; the leader does not open
the raw log.
If no matching final summary exists, do not invent one: preserve the exact exit
status and stderr and classify the invocation as an early wrapper failure. It is
eligible for Gemini fallback only when numeric exit status `4`
(`EXIT_BINARY_MISSING`) is paired with a
wrapper-owned diagnostic proving missing/invalid `TRIAD_AGY_BIN`, missing `agy`
on `PATH`, or `agy start failed before request submission: stage=exec errno=`.
Every other no-summary failure is fallback-ineligible. Without a `run-log:` path, surface
the early failure directly instead of fabricating a repair handoff.
An early `ok` followed by a corrected `extraction-error` is a failure:
route the final `extraction-error` to repair. Surface terminal, schema,
configuration, and capacity outcomes with their reported reason. Route only
`unknown`, `extraction-error`, and `timeout` to the repair protocol; preserve
the run log for its age-floor cleanup. Treat `truncated-answer` (exit 65) as a deterministic terminal result: the answer is quarantined, it is not repair-routed, and a new invocation must ask for a bounded, compact result. Do not use a generic `write_file` workaround. Do not omit `--sandbox read-only` to recover a long answer.

## Repair handoff

Follow [the shared repair protocol](../../docs/references/repair-protocol.md).
Set `cli` to `antigravity`. The protocol supplies the exact registered analyzer,
proposal-file lifecycle, and owner-run apply command.

## See also

- `triad-claude-dispatch` for Claude Code.
- `triad-cross-family-review` for formal review gates.
