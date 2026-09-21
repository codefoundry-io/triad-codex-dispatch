---
name: triad-antigravity-dispatch
description: Use when a bounded task needs one authorized AGY Google-family answer or when the cross-family review skill selects its Google leg.
---

# Antigravity Dispatch

Use the packaged `bin/antigravity_wrapper.py`.
Formal preflight and dispatch never use `--dangerously-skip-permissions`.
Raw investigations retain the version-gated headless compatibility unless
`AGY_NO_HEADLESS_AUTOAPPROVE=1` opts out. Callers do not pass the flag.
Formal calls use `--sandbox read-only`. Without an explicit project, the route uses
native `--mode plan` with a transient global-settings transaction
that unions the five raw read-only deny rules plus `read_url(*)` for default
no-web review, then restores the original bytes. Explicitly requested review web
uses the five raw denies and refuses an existing owner `read_url(*)` deny before
inference without removing it. Identical formal leases may overlap; different
raw/formal deny lists remain isolated. On AGY 1.1.20 or newer, the formal route passes a
review-bound native `--json-schema` in plan mode and consumes the terminal
`structured_output`. It then repeats strict local `LegVerdict` validation and
exact review-binding checks. Human-readable response text and diagnostic finish
messages are not verdict transport.
A missing, malformed, or schema-invalid structured output terminates the leg with no
schema-repair provider call. The formal Google prompt authorizes only
AGY native file-read/search tools for local inspection, forbids command and
other action tools plus experiments, and undecidable uncertainty goes to
`open_questions`. MCP calls are unavailable for the formal Google leg.
REVIEW defaults to no web; only a direct owner request enables
[the bound web option](../triad-cross-family-review/references/review-web.md).
Use `grep_search`
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
backstop. Local verdict and review-binding checks plus
round-integrity verification remain the admission gates. Round-integrity
mutation detection is separate. The wrapper does not suppress installed tools
before provider execution or reinterpret a completed review from the vendor's
evolving telemetry schema.
The route remains read-only by intent plus explicit deny, local result
admission, and separate round-integrity checks.

## Route proof

An owner-provisioned dedicated project may use `--project <canonical-lowercase-UUID>`
with an explicit `--cwd` and `--sandbox read-only`. The wrapper checks the project
record's ID, single cwd resource, and the same six formal deny entries by default without a
global settings lease or permission-file writes. Use the same UUID for preflight
and dispatch, and for both Pro/Flash preflights in a paired review. Keep the
project configuration stable during the call. Follow the exact
[project invocation contract](../triad-cross-family-review/references/leg-contracts.md#optional-dedicated-agy-project);
the wrapper does not create or modify projects.
The explicitly requested review-web option uses the five raw read-only denies;
an existing project `read_url(*)` deny causes refusal before inference and remains
unchanged. Other owner denies also remain authoritative.

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
authorizes only AGY native file-read/search tools for local inspection.
Web research is prohibited by default; MCP calls are always denied by the
formal read-only permission rules. It forbids command, shell, terminal,
file-write/edit, notebook-execution, subagent, browser-actuation, and
scratch-space tools plus experiments; undecidable uncertainty goes to
`open_questions`. AGY reviews only and makes no external-state changes or
candidate execution.

## Failure handling

A failure before provider submission stops the round with zero provider legs.
A failure after submission invalidates the Google leg and round. Do not switch
providers or authentication classes, drop `--sandbox read-only`, or substitute
a provider-side command-specific allowlist or tool suppression.
Keep formal permission checks enabled; if headless review is unavailable,
report the blocker and diagnose the same route without enabling autoapproval.
Clean the invalid round, correct the same route, and restart every required
family under a fresh review ID. Return one validated result bound to one review
ID and content digest.
