---
name: triad-claude-dispatch
description: Use when the Codex leader needs one Claude Code answer through the installed wrapper, including the Claude leg of a review or a classified repair handoff.
---

# triad-claude-dispatch

Dispatch one Claude Code request through the installed absolute
`claude_wrapper.py` launcher. Use `triad-cross-family-review` for a formal
cross-family gate.

## External dispatch authorization

Before sending any prompt or file to the external provider, confirm owner
authorization covers the provider, destination, task scope, and approved data.
An explicit user request to call Claude supplies authorization within that stated
scope. A matching standing authorization also counts; record its reference and
reuse it without asking again while its boundaries remain unchanged. For a
formal review, use `triad-cross-family-review` and require its recorded per-run
external-input allowlist; fail closed when that allowlist is absent or does not
cover every provider-visible input.

## Invocation

Resolve the launcher once, then invoke its absolute path directly. Pass a short
request with `--prompt`; write long or punctuation-rich requests to a UTF-8 file
and pass its absolute path with `--prompt-file`. Keep the launcher argv as data,
not a shell string.

```python
launcher_argv = [
    "/absolute/path/to/claude_wrapper.py",
    "--prompt-file", "/absolute/path/to/request.txt",
    "--sandbox", "read-only",
    "--cwd", "/absolute/path/to/workspace",
]
```

Use `--sandbox workspace-write` only for a code task in an isolated worktree.
The wrapper requires `--cwd` for that mode. Provider authentication and any
model selection happen in the owner's normal authenticated terminal; credentials
are never moved into a sandbox.

## Formal review invocation

Use the exact packaged canonical operand and paired packet identity flags:

```python
formal_review_schema = "triad_formal_review_schema:FormalReview"
review_argv = [
    "/absolute/path/to/claude_wrapper.py",
    "--prompt-file", "/absolute/immutable/reviews/<review-id>/claude-prompt.txt",
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

For a nonzero exit, scan captured stderr in memory. Select the last matching `[wrapper] claude ...` summary.
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
Set `cli` to `claude`. The protocol supplies the exact registered analyzer,
proposal-file lifecycle, and owner-run apply command.

## See also

- `triad-antigravity-dispatch` and `triad-gemini-dispatch` for Google-family calls.
- `triad-cross-family-review` for formal review gates.
