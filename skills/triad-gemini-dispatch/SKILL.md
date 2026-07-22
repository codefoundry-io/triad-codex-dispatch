---
name: triad-gemini-dispatch
description: Use when the Codex leader needs one business, Vertex, or API-key Gemini answer after the agy route is unavailable before dispatch, including a classified repair handoff.
---

# triad-gemini-dispatch

Dispatch one Gemini CLI request through the installed absolute
`gemini_wrapper.py` launcher. Prefer `triad-antigravity-dispatch` for the
individual-tier Google-family route.

This is the Google-family fallback when agy is unavailable. Unavailable means a
pre-dispatch availability failure proves that agy cannot be started on the
configured route, and a configured Gemini Enterprise/Business, Vertex, or
API-key route is available. An agy content, extraction, or schema failure does
not make agy unavailable and must not trigger Gemini fallback. Handle that
result on the agy path; for a formal review, preserve the invalid agy leg rather
than substituting Gemini. If neither Google route is available, report the
required Google leg as unavailable; a formal review round is invalid.

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

Bootstrap can report only a `gemini` binary candidate. A preflight or dispatch
in the owner's authenticated terminal must succeed before the route counts as
a configured formal Google leg; never infer tier or model access from executable
presence.

## External dispatch authorization

Before sending any prompt or file to the external provider, confirm owner
authorization covers the provider, destination, task scope, and approved data.
An explicit user request to call Gemini supplies authorization within that
stated scope, but it does not establish fallback eligibility or bypass the
agy-first rule. A matching standing authorization also counts; record its
reference and reuse it without asking again while its boundaries remain
unchanged. For a formal review, use `triad-cross-family-review` and require its
recorded per-run external-input allowlist; fail closed when that allowlist is
absent or does not cover every provider-visible input.

## Invocation

Resolve the launcher once, then invoke its absolute path directly. Pass a short
request with `--prompt`; write long or punctuation-rich requests to a UTF-8 file
and pass its absolute path with `--prompt-file`. Keep the launcher argv as data,
not a shell string.

```python
launcher_argv = [
    "/absolute/path/to/gemini_wrapper.py",
    "--prompt-file", "/absolute/path/to/request.txt",
    "--sandbox", "read-only",
    "--cwd", "/absolute/path/to/workspace",
]
```

Use `--sandbox workspace-write` only for a code task in an isolated worktree.
Provider authentication and model selection occur only in the owner's normal
authenticated terminal; credentials are never moved into a sandbox.

## Formal review invocation

This invocation is eligible only after proven pre-submission agy route
unavailability. Use the exact packaged canonical operand and paired packet
identity flags:

```python
formal_review_schema = "triad_formal_review_schema:FormalReview"
review_argv = [
    "/absolute/path/to/gemini_wrapper.py",
    "--prompt-file", "/absolute/immutable/reviews/<review-id>/gemini-prompt.txt",
    "--sandbox", "read-only",
    "--cwd", "/absolute/immutable/reviews/<review-id>/packet",
    "--pydantic", formal_review_schema,
    "--sealed-packet-root", "/absolute/immutable/reviews/<review-id>/packet",
    "--expected-packet-sha256", "<exact 64-lowercase-hex digest>",
]
```

The formal prompt names the exact packet root, digest, and packet-local
`INPUT_SHA256SUMS`. Before provider resolution, a sealed formal invocation
verifies `PACKET_SHA256, SHA256SUMS, and INPUT_SHA256SUMS`. Every finding location uses an exact manifest-listed
packet-relative path plus a positive line number. Put an unverifiable citation
in `open_questions` and return `NOT-SAFE`. The wrapper rejects missing, partial,
or unsupported validation context before provider startup. It performs no hidden
automatic schema-repair retry: `schema-fail is terminal for that invocation`.
The leader may make an explicit new invocation after deciding what to do.

Every normal non-`--repair-mode` wrapper invocation that reaches the provider driver performs
best-effort cleanup of managed UUID/file-IPC entries older than 3,600 seconds;
cleanup errors never block dispatch, and no perfect garbage collector is
claimed.

## Result handling

An initial tool response with a running session or cell handle is pending, not unavailable,
invalid, or failed. Keep it running and use event-driven status checks until a terminal process
exit arrives; report a concise heartbeat when useful. A poll timeout is only a wake-up boundary,
never a provider verdict or process failure.

The wrapper tool yields captured stdout, stderr, and process exit status. It is
not a structured result object. The exit status and final emitted state are
authoritative. When the exit status is zero, stdout is the answer.

For a nonzero exit, scan captured stderr in memory. Select the last matching `[wrapper] gemini ...` summary.
Use that final summary as the classification source. Select the last `run-log:` path
without a shell pipeline, keep it as opaque data, and pass it only to the
read-only analyzer for repair-routed classifications; the leader does not open
the raw log.
If no matching final summary exists, do not invent one: preserve the exact exit
status and stderr and surface the invocation as an early wrapper failure. Without a `run-log:` path,
report that failure directly instead of fabricating a repair handoff.
An early `ok` followed by a corrected `extraction-error` is a failure:
route the final `extraction-error` to repair. Surface terminal, schema,
configuration, and capacity outcomes with their reported reason. Route only
`unknown`, `extraction-error`, and `timeout` to the repair protocol; preserve
the run log for its age-floor cleanup.

## Repair handoff

Follow [the shared repair protocol](../../docs/references/repair-protocol.md).
Set `cli` to `gemini`. The protocol supplies the exact registered analyzer,
proposal-file lifecycle, and owner-run apply command.

## See also

- `triad-antigravity-dispatch` for the primary individual-tier Google route.
- `triad-cross-family-review` for formal review gates.
