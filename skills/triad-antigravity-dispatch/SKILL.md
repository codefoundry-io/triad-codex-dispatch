---
name: triad-antigravity-dispatch
description: Use when a bounded task needs one authorized AGY Google-family answer or when the cross-family review skill selects its Google leg.
---

# Antigravity Dispatch

Use the packaged `bin/antigravity_wrapper.py`. The wrapper internally inserts
`--dangerously-skip-permissions` for AGY headless calls unless the operator
sets `AGY_NO_HEADLESS_AUTOAPPROVE=1`. Callers do not pass this flag. Formal
calls use `--sandbox read-only` and a transient global-settings transaction
that unions the five write/command/unsandboxed/URL/MCP deny rules, then
restores the original bytes. The headless flag voids both deny and sandbox
enforcement, so that path is read-only by intent plus round-integrity checks,
not enforced containment. The wrapper does not suppress installed tools.

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
  --sandbox read-only
  --model gemini-3.1-pro-high
  --effort high
  --timeout 1800
  --pydantic verdict_schema:LegVerdict
  --expected-review-id "$review_id"
  --expected-family google
  --expected-content-digest "$review_digest"
```

The wrapper calls AGY print mode with native `--output-format stream-json` and
`--json-schema`, admits only the terminal result event, and validates it
locally. The formal route binds the exact review ID, Google family, content
digest, and review-relative path shape in the native schema and repeats those
binding checks locally. The formal leg uses this explicit 1,800-second end-to-end deadline;
shorter leader polling waits do not terminate it. Installed CLI commands, configured MCP tools, and provider-native
read/search tools stay available. AGY reviews only; the review prompt forbids
editing, external-state changes, and candidate execution.

## Failure handling

A failure before provider submission stops the round with zero provider legs.
A failure after submission invalidates the Google leg and round. Do not switch
providers or authentication classes, drop `--sandbox read-only`, or substitute
a command-specific allowlist or tool suppression. If the operator opt-out makes
headless review unavailable, preserve that opt-out and report the blocker.
Clean the invalid round, correct the same route, and restart every required
family under a fresh review ID. Return one validated result bound to one review
ID and content digest.
