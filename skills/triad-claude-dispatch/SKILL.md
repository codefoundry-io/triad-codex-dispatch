---
name: triad-claude-dispatch
description: Use when a bounded task needs one authorized Claude-family answer or when the cross-family review skill selects its Claude leg.
---

# Claude Dispatch

Use the packaged `bin/claude_wrapper.py`; do not call provider internals or
modify Claude authentication, permissions, or user configuration.

## Ordinary bounded dispatch

1. Confirm the exact objective, working directory, and authorized external
   data boundary.
2. Put long prompts in a leader-owned UTF-8 file outside reviewed evidence.
3. Invoke the wrapper with `--prompt-file`, `--cwd`, and the requested
   model/effort. Add `--pydantic module:Class` only when the caller supplies a
   real structured-output contract.
4. Treat nonzero exit, malformed result, refusal, timeout, or capacity failure
   as a failed dispatch. Do not reinterpret it as task evidence.

## Cross-family review leg

Use `triad-cross-family-review` and read its
`references/leg-contracts.md`. The formal Claude route is `--model opus
--effort xhigh --timeout 1800 --pydantic verdict_schema:LegVerdict
--expected-review-id "$review_id" --expected-family claude
--expected-content-digest "$review_digest"`. Claude reviews only; it does not
edit or execute candidate code. One validated result belongs to one review ID
and content digest.

## Result handling

Return the wrapper's terminal stdout to the leader. Keep run logs and result
files outside immutable reviewed evidence. Provider findings never authorize a
code or design change; the leader reproduces and classifies them.
