# Formal reviewer routing contract

## Contents

- [Scope](#scope)
- [Bounded formal routes](#bounded-formal-routes)
- [Approval behavior](#approval-behavior)
- [Google route and fallback](#google-route-and-fallback)
- [Conditional escalation and convergence](#conditional-escalation-and-convergence)
- [Failure handling](#failure-handling)

## Scope

This review-only routing policy is an owner routing policy, not a vendor
capability claim. It does not set generic wrapper defaults. It applies only to
a cross-family review after the owner has authorized external dispatch.
Run every provider route from the same authenticated login terminal and
project worktree used for development. TRIAD inherits provider permissions and
provider-owned project/trust decisions from that launch context; it does not
install, inject, strengthen, weaken, or bypass a permission mode.

## Bounded formal routes

Unless the review decision records a justified escalation, use these routes:

- Fresh Codex: `gpt-5.6-terra`, `xhigh`, `fork_turns="none"`.
- Claude: `opus`, `xhigh`.
- Primary Google: agy with the exact display label `Gemini 3.1 Pro (High)`;
  catalog evidence uses `gemini-3.1-pro-high`.

Capture live proof of the selected route at the first possible proof point:

- accepted exact Codex spawn
- exact Claude argv/provider acceptance
- authenticated `agy models` evidence for the exact selector before formal dispatch, with the exact selector present

For every review ID, record the exact route and rationale/availability proof.
Rejection or unavailability leaves the required leg missing under the gate
rules. Do not silently substitute a model, provider route, or effort.

## Approval behavior

The explicit owner request, exact provider/data boundary, and sanitized argv
are the authorization evidence. Native user/project settings decide whether a
provider operation is allowed, denied, or interactive. A native permission
denial leaves the required leg invalid. Keep prompt-controlled no-edit and
no-execution behavior distinct from provider-enforced containment, and use
immutable-directory digests plus canonical-worktree fingerprints to detect a
violation.

## Google route and fallback

AGY is the primary Google-family route. A configured Gemini
Enterprise/Business, Vertex, or API-key route is eligible only when the AGY
wrapper emits no final summary, exits with `EXIT_BINARY_MISSING`, and records
the wrapper-owned pre-submission
`PtyStartError(stage="exec", errno in the supported missing/unstartable set)`
diagnostic. A content, extraction, schema, validation, timeout, capacity,
permission, or other post-dispatch failure does not permit Gemini fallback. A
running tool handle is pending; wait for its terminal result. Any final summary
is post-dispatch and fallback-ineligible.

Missing or invalid `TRIAD_AGY_BIN` and missing `agy` on `PATH` are surfaced as
fallback-ineligible route-setup errors under the current wrapper contract. The
owner installs or configures AGY, or explicitly authorizes a separate Google
route. A
`permission-unavailable` required leg is invalid and post-dispatch, so it
cannot activate Gemini in the same round. If neither authorized route is
available, the required Google leg is unavailable and the formal round is
invalid.
A missing selector, request rejection, or exposed identity conflict also
leaves the Google leg missing/invalid.

For Google, authenticated `agy models` output proves that the stable selector is
advertised before formal dispatch. The current formal argv uses the exact display label `Gemini 3.1 Pro (High)` and
omits `--effort`; the catalog selector remains evidence only. Wrapper preflight
reports the requested `model` and `effort` and proves argv construction, never a
locally invented `effective_model`. Record actual provider request acceptance
and require any runtime-exposed identity to agree with the requested label. If
runtime telemetry is absent after the successful preflight, record it as
`unexposed` once without guessing the hidden actual model. After an AGY update,
rerun these three candidates as separate fresh runtime probes:

- `--model gemini-3.1-pro-high` with no `--effort`;
- `--model gemini-3.1-pro --effort high`; and
- `--model "Gemini 3.1 Pro (High)"` with no `--effort` as the control.

Catalog presence or provider acceptance alone does not authorize a route
change. Keep the control route unless another candidate is accepted and its
runtime-exposed identity agrees with the requested Pro High route. Any
alternative remains unselected until its fresh successful runtime probe
confirms both conditions.

A Gemini preflight/dispatch proves route availability only. For a formal
round, separately record owner authorization for the exact Gemini route,
provider, data boundary, and objective. Use the same immutable prepared
directory, prompt-controlled no-edit/no-execution contract, digest and
mutation invalidation, full batch matrix, and strict receipt admission. Native
owner/project permissions govern the route; TRIAD does not add an enforcement
probe or substitute one provider for another after dispatch.

## Conditional escalation and convergence

An escalated reviewer route is conditional and reserved for an ambiguous,
security-sensitive, deeply integrative, or adjudication-heavy review. Its
selection does not itself invalidate a review when the exact route, rationale,
and live proof are recorded for that review ID.

Convergence remains based on reproducible path:line evidence and the unchanged
shared review directory, not model labels or vote counts. An unresolved
contradiction is `CONFLICTED` and requires owner adjudication. A reviewer that
modifies or executes candidate code invalidates that leg; a changed shared
directory invalidates the round and requires a fresh complete review.

Classify each verified claim before editing:

- `REPRODUCED`: direct source contradiction or deterministic evidence inside
  the approved design; the smallest bounded correction may proceed.
- `REACHABLE_UNPROVEN`: the mechanism is reachable but the claimed failure is
  not reproduced; gather evidence before code.
- `OUT_OF_SCOPE_OR_SPECULATIVE`: the approved design or deployment boundary
  excludes the claim; record it for the owner without implementation.
- `DESIGN_CHANGE`: the claim requires a new capability, abstraction, protocol,
  policy, or deployment assumption; stop for owner approval.

A failed reproduction remains `REACHABLE_UNPROVEN` unless direct evidence
establishes another class. Reviewer severity decides whether a claim blocks;
leader triage decides whether code is authorized. Triage never converts a
blocking result into a pass.
When explicit reviewed bytes prove that the claimed trigger is absent or
excluded by the approved boundary, classify it `OUT_OF_SCOPE_OR_SPECULATIVE`;
otherwise retain `REACHABLE_UNPROVEN`. A refuted disposition is not a fifth
triage label.

After each complete valid three-family round, record one round state:

- `CLEAN`: every required result is `SAFE` and no unresolved claim remains.
- `CONVERGING`: the round adds a reproduced defect or independently confirms
  one.
- `OSCILLATING`: a resolved claim returns without material new evidence.
- `OWNER_DECISION`: the remaining evidence gap or blocking residual requires
  owner adjudication.

Apply the states in this order: `CLEAN`; `OWNER_DECISION` when any remaining
item requires the owner; `OSCILLATING` when no material new evidence remains;
otherwise `CONVERGING` when reproduced evidence remains.
Use these four labels only for the complete round; each claim retains its own
triage and disposition label in the residual ledger.
`CONFLICTED` is an item state for surviving incompatible claims. Route that
item to the owner before continuing it; other verified items remain governed by
their own triage. A round state records progress and never admits a result,
releases a blocking verdict, or authorizes release.

Keep the leader's residual ledger outside the immutable prepared directory and
provider-response custody tree. When the standard run layout is present, use
`_runs/reviews/<id>/residuals.md`. Identify a claim by its
prepared-directory-relative path and trigger, and record its family, round,
severity, triage, reproduction evidence, disposition, and direct conflict.
Use this ledger rather than adding another receipt field, database, or service.

Before implementing a `REPRODUCED` claim, stop for owner approval when the fix
adds a runtime guard, fallback, retry, lock, validation layer, production
dependency/configuration/public protocol, changes production paths outside the
claim's impact closure, or exceeds 30 added-plus-removed non-generated
production lines. The leader counts the logical-fix diff deterministically.
Mechanically required callers/imports and files already listed in the approved
implementation map remain inside the approved correction boundary.

A malformed or truncated required result permits exactly one compact
re-dispatch of that complete family across every batch, using the same evidence,
route, objective, boundaries, and result profile in fresh contexts. Retain the
original response bytes for custody, but do not combine old and replacement
receipts for admission. A second malformed or truncated result leaves the
required family invalid and the round invalid. Provider substitution and a
two-family formal pass remain unavailable.

## Failure handling

| Failure | Response |
|---|---|
| Reviewer asks for a packet | Point it to the shared review directory and scope |
| Provider unavailable before submission | Preserve evidence and apply the Google fallback rules |
| Required family result is malformed or truncated | Re-dispatch that complete family across every batch once with the same evidence and a compact-format reminder; a second failure invalidates the family and round |
| Required agy leg returns `truncated-answer` | Apply the complete-family rule above; post-dispatch truncation does not permit Gemini fallback |
| Commit, push, install, merge, or release is needed | Stop for separate owner authorization |
