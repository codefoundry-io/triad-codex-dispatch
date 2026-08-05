---
name: triad-gemini-dispatch
description: Use when a bounded task needs one authorized Gemini CLI answer or when AGY is proven unavailable before a cross-family review round starts.
---

# Gemini Dispatch

Use the packaged `bin/gemini_wrapper.py`; preserve native authentication,
workspace trust, and permissions.

## Ordinary bounded dispatch

Confirm objective, cwd, model, and external data boundary. Invoke the wrapper
with `--prompt-file` for long input, `--cwd`, optional `--model`, and optional
`--pydantic module:Class`. A nonzero exit or malformed result is a failed
dispatch, not substantive evidence.

## Cross-family Google leg

AGY is the formal default. Gemini is eligible only when AGY is proven
unavailable before submission and the leader selects Gemini before starting a
fresh complete round. Give it the same prepared directory, prompt, digest,
read/search-only contract, and `verdict_schema:LegVerdict`. Never replace a
failed in-flight AGY leg with Gemini inside the same round.

Gemini reviews only; it does not edit or execute candidate code. The leader
reproduces every finding and asks the owner before any proposed design,
specification, capability, or scope change.
