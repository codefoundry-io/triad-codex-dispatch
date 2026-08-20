# Formal Leg Fail-Fast and AGY Binding Design

> **Historical, superseded, and non-executable.** This design records the former
> native schema binding route. TRIAD 0.2.541 instead uses plan-mode terminal
> response admission and strict local validation. Current authority is
> `skills/triad-antigravity-dispatch/SKILL.md` plus the current cross-family leg
> and prompt contracts. The fail-fast round-control history below remains
> descriptive, not executable instructions.

**Owner decision:** A required-leg failure is an infrastructure failure for the
round. The leader stops every still-running leg immediately and repairs that
failure before any new review dispatch.

## Observed failure

Round `20260812-arg-s1-01-r9-persistent-authority-plan-r7-b5m8` sent the
packaged `LegVerdict` JSON Schema to AGY 1.1.12. AGY returned vendor exit 0,
but its structured object used absolute paths in
`affected_surfaces_inspected` and `family: "codex"`. Local validation rejected
the path and the wrapper exited 66. The native schema had only `type: string`
for paths and the three-value family enum because Pydantic field validators and
round-specific bindings were absent from `model_json_schema()`.

A minimal live spike proved AGY enforces supported JSON Schema `pattern` and
`const` constraints in `structured_output`: an intentionally requested
`/tmp/probe` and `codex` response was emitted as `tmp/probe` and `google` when
the supplied schema required those values.

Stopping the Python Claude wrapper exposed a second round-control defect: its
separate-session vendor child survived as an orphan. `_run_once()` terminates
the provider process group on timeout but not when the wrapper receives an
interrupt.

## Slice A: bind the formal AGY result before generation

**Behavioral claim:** A formal AGY invocation generates and locally enforces a
`LegVerdict` bound to the exact review ID, Google family, content digest, and a
review-relative path shape.

- Preserve `LegVerdict` as the semantic source of truth.
- Expose the existing review-relative path prefix/backslash restrictions in its
  JSON Schema while retaining the stricter local validator for dot segments and
  control characters.
- Add explicit formal binding arguments to `antigravity_wrapper.py`.
- When all bindings are supplied, add exact `const` values to the native schema
  and reject any locally validated payload whose three bound fields disagree.
- Keep unbound standalone AGY consults backward compatible.
- Do not normalize, rewrite, or repair a provider verdict after generation.
- Do not add a second provider call or substitute a provider.

Forecast: at most 120 production lines, at most 80 novel-core lines, one
behavioral claim.

## Slice B: cancel the complete invalid round

**Behavioral claim:** Interrupting a wrapper terminates and reaps its provider
process group, and the TRIAD leader cancels every sibling immediately after the
first required-leg failure.

- Factor the existing timeout termination sequence into one internal helper and
  invoke it for timeout and wrapper interruption.
- Re-raise the original interruption only after termination/reaping.
- On first required-leg failure, cancel all still-running legs started for that
  round, confirm their process trees terminated, discard every current-round
  verdict, perform the required post-termination integrity check, and clean the
  exact managed root.
- Diagnose and fix the infrastructure failure before preparing a fresh review
  ID. Never continue siblings merely to collect advisory evidence.
- Do not kill unrelated processes or use broad process-name matching.

Forecast: at most 90 production lines, at most 60 novel-core lines, one
behavioral claim.

## Verification and distribution

Each slice uses RED/GREEN pytest evidence and its own commit. The skill change
also uses fresh `triad-skill-executor` RED and GREEN behavior trials. Final
verification includes focused tests, the complete test suite, skill validation,
distribution verification, source/package byte comparison, supported
installation, and a fresh process exposure proof. Argus remains paused until
both slices are deployed; it then resumes with a fresh three-family review ID.
