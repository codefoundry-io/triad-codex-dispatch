---
name: triad-antigravity-dispatch
description: Use when a bounded task needs one authorized AGY Google-family answer or when the cross-family review skill selects its Google leg.
---

# Antigravity Dispatch

Use the packaged `bin/antigravity_wrapper.py`. The wrapper internally inserts
`--dangerously-skip-permissions` for AGY headless calls unless the operator
sets `AGY_NO_HEADLESS_AUTOAPPROVE=1`. Callers do not pass this flag. Formal
calls use `--sandbox read-only`. The route uses native `--mode plan` with a transient global-settings transaction
that unions the five write/command/unsandboxed/URL/MCP deny rules, then
restores the original bytes. On AGY 1.1.20 or newer, the formal route passes a
review-bound native `--json-schema` in plan mode and consumes the terminal
`structured_output`. It then repeats strict local `LegVerdict` validation and
exact review-binding checks. Human-readable response text and diagnostic finish
messages are not verdict transport.
A missing, malformed, or schema-invalid structured output terminates the leg with no
schema-repair provider call. The formal Google prompt authorizes only
AGY native file-read/search tools for local inspection, forbids command and
other action tools plus experiments, and undecidable uncertainty goes to
`open_questions`. MCP calls are unavailable for the formal Google leg. Approved
AGY native official-web reads remain available only when the review objective
and authorized external data boundary expressly permit them. Use `grep_search`
with the required `SearchPath` and `Query` arguments to search inside the review
target identified by Review metadata, and use `list_dir`, `find_by_name`, and `view_file` as
needed. For every `view_file` call, provide the required `AbsolutePath` argument. For files
larger than one native view, request explicit positive-integer `StartLine` and
`EndLine` ranges.
Never request `ContentOffset` or `IsSkillFile`, and do not rely on implicit
another-page continuation. If native reads and searches are insufficient, report the limit in
`open_questions`. Formal `step_update` telemetry is diagnostic vendor output,
not an admission schema: added fields, changed optional tool arguments, denied
attempts, and duplicate progress events do not invalidate an otherwise valid
terminal verdict. The prompt and native `--mode plan` define the static-review
behavior. The explicit deny rules remain the action-namespace enforcement
backstop. Headless auto-approve removes interactive approval prompts but does
not remove those explicit deny entries. Local verdict and review-binding checks plus
round-integrity verification remain the admission gates. Round-integrity
mutation detection is separate. The wrapper does not suppress installed tools
before provider execution or reinterpret a completed review from the vendor's
evolving telemetry schema.
The route remains read-only by intent plus explicit deny, local result
admission, and separate round-integrity checks.

## Route proof

Before formal review, require authenticated output proving:

```text
agy --version  -> 1.1.20 or newer
agy models     -> gemini-3.1-pro-high present
```

Catalog and argv evidence prove the requested route, not hidden backend
identity. Record runtime identity as `unexposed` when the provider does not
expose it; an exposed conflict invalidates the leg.

## Formal Google leg

Use `triad-cross-family-review` and its `references/leg-contracts.md`. The
formal wrapper arguments are:

```text
  --sandbox read-only
  --model gemini-3.1-pro-high
  --effort high
  --timeout 600
  --pydantic verdict_schema:LegVerdict
  --expected-review-id "$review_id"
  --expected-family google
  --expected-content-digest "$review_digest"
```

The wrapper calls AGY print mode with native `--output-format stream-json`.
The formal plan-mode route passes native `--json-schema`, admits only the
terminal result event's `structured_output`, and repeats strict local
`LegVerdict` validation. It checks the exact review ID,
Google family, content digest, and review-relative path shape locally. Invalid
output is terminal and causes no schema-repair provider call. The formal leg uses
an explicit 600-second wrapper provider-process deadline, and the AGY child gets
`--print-timeout 590s`. Apply [convergence](../triad-cross-family-review/references/convergence.md)
to observation waits and terminal outcomes. The formal Google prompt
authorizes only AGY native file-read/search tools for local inspection plus
expressly authorized AGY native official-web reads. MCP calls are denied by the
formal settings transaction. It forbids command, shell, terminal,
file-write/edit, notebook-execution, subagent, browser-actuation, and
scratch-space tools plus experiments; undecidable uncertainty goes to
`open_questions`. AGY reviews only and makes no external-state changes or
candidate execution.

## Failure handling

A failure before provider submission stops the round with zero provider legs.
A failure after submission invalidates the Google leg and round. Do not switch
providers or authentication classes, drop `--sandbox read-only`, or substitute
a provider-side command-specific allowlist or tool suppression. If the operator
opt-out makes headless review unavailable, preserve that opt-out and report the blocker.
Clean the invalid round, correct the same route, and restart every required
family under a fresh review ID. Return one validated result bound to one review
ID and content digest.
