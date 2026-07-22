# Formal reviewer routing contract

## Scope

This review-only routing policy is an owner routing policy, not a vendor
capability claim. It does not set generic wrapper defaults. It applies only to
a cross-family review after the owner has authorized external dispatch.

## Bounded formal routes

Unless the review decision records a justified escalation, use these routes:

- Fresh Codex: `gpt-5.6-terra`, `xhigh`, `fork_turns="none"`.
- Claude: `opus`, `xhigh`.
- Primary Google: agy with `gemini-3.1-pro-high`.

Capture live proof of the selected route at the first possible proof point:

- accepted exact Codex spawn
- exact Claude argv/provider acceptance
- authenticated `agy models` evidence for the exact selector before formal dispatch, with the exact selector present

For every review ID, record the exact route and rationale/availability proof.
Archive it only when the owner explicitly requests a durable review archive.
Rejection or unavailability leaves the required leg missing under the gate
rules. Do not silently substitute a model, provider route, or effort.

For Google, authenticated `agy models` output proves selector availability; a
source packet or sealed-packet preflight is not required. Record actual provider
request acceptance and the effective model identity when exposed. If
effective-model telemetry is absent, record it as `unexposed` once without
claiming the hidden actual model. Any selector absence, rejection, or exposed
conflict leaves the Google leg missing/invalid; a missing telemetry field alone
may be unexposed rather than guessed. Existing fallback rules still apply.

## Conditional escalation

A Sol- or Fable-class model is a conditional escalation only for an ambiguous,
security-sensitive, deeply integrative, or adjudication-heavy review. Its
selection does not itself invalidate a review when the exact route, rationale,
and live proof of the selected route are recorded for that review ID.

## Convergence

Convergence remains based on the unchanged guarded worktree and reproducible
path:line evidence, not model labels or vote counts. An unresolved contradiction
is `CONFLICTED` and requires owner adjudication.
