---
name: triad-gemini-dispatch
description: Use when a bounded task needs one authorized standalone Gemini CLI compatibility answer. Do not use it as the formal Google-family review leg.
---

# Gemini Dispatch

Use the packaged `bin/gemini_wrapper.py`; preserve native authentication,
workspace trust, and permissions.

## Ordinary bounded dispatch

Confirm objective, cwd, model, and external data boundary. Invoke the wrapper
with `--prompt-file` for long input, `--cwd`, optional `--model`, and optional
`--pydantic module:Class`. A nonzero exit or malformed result is a failed
dispatch, not substantive evidence.

## No formal Google-leg substitution

This skill is a standalone compatibility consult only. Formal Google review
uses the packaged AGY route for both personal Google Sign-In and Gemini
Enterprise Business Sign-In. If AGY is unavailable, invalidate the round and
repair the same selected AGY authentication class; never substitute this
Gemini wrapper in the current or a fresh formal round.

The exact formal `verdict_schema:LegVerdict` route makes one provider call.
Capacity failure or invalid structured output is terminal for that invocation;
the wrapper makes no hidden capacity retry or schema-repair provider call.

Gemini reviews only; it does not edit or execute candidate code. The leader
reproduces every finding and asks the owner before any proposed design,
specification, capability, or scope change.
