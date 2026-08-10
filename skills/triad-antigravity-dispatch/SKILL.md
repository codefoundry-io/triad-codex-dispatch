---
name: triad-antigravity-dispatch
description: Use when a bounded task needs one authorized AGY Google-family answer or when the cross-family review skill selects its Google leg.
---

# Antigravity Dispatch

Use the packaged `bin/antigravity_wrapper.py`. The wrapper internally inserts
`--dangerously-skip-permissions` for AGY headless calls. Callers do not pass
this flag. The wrapper does not edit user settings, add a sandbox or a
command-specific allowlist, or suppress installed tools.

## Route proof

Before formal review, require authenticated output proving:

```text
agy --version  -> 1.1.10 or newer
agy models     -> gemini-3.1-pro-high present
```

Catalog and argv evidence prove the requested route, not hidden backend
identity. Record runtime identity as `unexposed` when the provider does not
expose it; an exposed conflict invalidates the leg.

## Formal Google leg

Use `triad-cross-family-review` and its `references/leg-contracts.md`. The
formal wrapper arguments are:

```text
  --model gemini-3.1-pro-high
  --effort high
  --timeout 1800
  --pydantic verdict_schema:LegVerdict
```

The wrapper calls AGY print mode with native `--output-format stream-json` and
`--json-schema`, admits only the terminal result event, and validates it
locally. The formal leg uses this explicit 1,800-second end-to-end deadline;
shorter leader polling waits do not terminate it. Installed CLI commands, configured MCP tools, and provider-native
read/search tools stay available. AGY reviews only; the review prompt forbids
editing, external-state changes, and candidate execution.

## Failure handling

A failure before provider submission may permit the leader to select the
documented Gemini route before starting the round. A failure after submission
invalidates the Google leg and round. Do not switch providers mid-round or
substitute a command-specific allowlist, sandbox, or tool suppression. Clean
the invalid round, correct the route, and restart every required family under
a fresh review ID. Return one validated result bound to one review ID and
content digest.
