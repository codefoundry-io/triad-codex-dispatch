# P3a: preserve original JSON integrity before review admission

Implement the already identified C14 lexical/binding portion after P2 merges.
Do not add C19 attempt semantics, schema v2 fields, a new retry loop or routes.
The leader writes all tests/source; separate fresh Terra/high skill executors
observe RED and GREEN on the canonical checkout.

## Current evidence and bounded correction

Direct `validate_verdict_file` rejects duplicate members in original JSON before
strict Pydantic validation. Wrapper admission currently normalizes the Claude,
Gemini and AGY envelope/structured object before semantic validation, losing
duplicate fields. AGY also accepts the canonical LegVerdict schema without any
of the three expected bindings; peer wrappers reject that invocation.

Reuse the existing duplicate-members scanner for canonical verdict admission
before original envelope/event bytes are discarded and before final answer
validation. Keep arbitrary raw replies and custom schemas on their existing
paths. Preserve malformed/noise NDJSON handling and timeout/vendor/transport
failure precedence. Fail canonical ambiguous JSON without reflecting member
names or untrusted contents into diagnostics. Do not start a second provider
attempt on this formal admission failure.

Reject zero and partial binding triples for the reserved AGY schema before
binary resolution. Keep preflight and ordinary invocation semantics intact.

## TDD verification

- Literal JSON with duplicate review_id/family/content_digest, including an
  escaped spelling whose first value disagrees but last value matches.
- Claude native structured envelope, Gemini object response and AGY terminal
  structured output duplicates; do not create these fixtures through dicts.
- Canonical direct answer and envelope paths both refuse; no final answer or
  SUCCESS emission. Exactly one synthetic provider call on wrapper tests.
- Custom schema/no-schema compatibility controls, valid existing envelopes,
  malformed stream noise, strict schema semantics and all existing bindings.
- AGY reserved schema with zero/partial bindings refuses before provider probe.
- Fresh RED/GREEN, full macOS/Ubuntu 24.04 suites, validator, applicable fixed
  lifecycle, full multi-family gate on the entire change and affected consumers.

Expected production delta approximately 65 additions/15 deletions; measure
actual coherent scope. Tests and narrative documentation are separate.

A is read-only at `92c8afd500499d8736afcc28b39a87a4f87fed50`: `_common.py:1590`
does semantic validation before its failure-only duplicate probe; Claude
normalizes at `1874`, AGY events at `409` and its wrapper structured output at
`748`. Verify those exact current lines before recording the final shared spike.
A's external binding boundary differs; do not port B's CLI argument check
mechanically. No installed/shared runtime revision adoption is implied.
