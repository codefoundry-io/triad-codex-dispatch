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
An explicit user request from the owner to call Claude, including an invocation
of this skill or `triad-cross-family-review`, supplies that authorization once
within the stated scope. A matching standing authorization also counts; record
its reference. Reuse it without asking again while the provider, destination,
worktree, task, and data boundary remain unchanged. For worktree review, that
scope is the repository data admitted by the shared review contract. Credentials,
tokens, cookies, authentication files, environment dumps, provider logs, and unrelated
paths remain excluded.

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

## Cross-family review invocation

Formal three-family preparation is defined by the
[triad-cross-family-review skill](../triad-cross-family-review/SKILL.md). Use
its leader-prepared shared review directory as Claude's `--cwd` and keep the
provider leg read-only.

```python
review_argv = [
    "/absolute/path/to/claude_wrapper.py",
    "--prompt-file", "/absolute/path/to/claude-review-prompt.txt",
    "--sandbox", "read-only",
    "--cwd", "/absolute/path/to/prepared-review-directory",
    "--model", "opus",
    "--effort", "xhigh",
]
```

Claude's formal review model is `opus` with `--effort xhigh`, as shown above.

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
