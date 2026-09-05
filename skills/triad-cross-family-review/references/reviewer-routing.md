# Formal reviewer routing

This owner routing policy chooses the review families and one Google
authentication class. It does not claim provider capability or authorize a
provider beyond the current task's objective and external-data boundary.

## Required routes

| Family | Formal route |
|---|---|
| Claude | `opus`, `xhigh`, 1,200-second wrapper deadline |
| Google with `personal-google` | AGY 1.1.20 or newer, `gemini-3.1-pro-high`, `high`, 600-second wrapper deadline |
| Google with `gemini-enterprise` | Prefer the same AGY route; when AGY is absent, use Gemini Enterprise OAuth with CLI Auto, requested Plan Mode, packaged read/search-only policy, and a 600-second wrapper deadline |
| Fresh Codex | `gpt-5.6-terra`, `xhigh`, `fork_turns="none"`, default child rather than a registered reviewer agent, repeatable 1,200-second native observation waits |

Use [leg contracts](leg-contracts.md) for exact invocation and containment
details. Use [convergence](convergence.md) for every setup failure, started-leg
failure, result failure, finding, rerun, and owner-decision outcome.

## Google route selection

The leader records `personal-google` or `gemini-enterprise` before dispatch.
Personal Google Sign-In requires AGY. Gemini Enterprise OAuth may select Gemini
only when AGY is absent; that route uses CLI Auto with `-m auto`.
Before any family starts, the bootstrap-managed
`review_round.py select-google-route` launcher for the canonical toolkit
exclusive-creates one current-round receipt. An installed operation uses its
matching installed launcher. A source-SOT pre-deployment round uses the isolated
same-root launcher group defined in [leg contracts](leg-contracts.md).

The selector receipt binds the review ID, authentication class, route,
executable, wrapper, and `provider_started:false`. Preflight only that recorded
wrapper with the current task file. Its canonical receipt repeats the route
identity and selector SHA, and adds the exact model, effort, executable, and
preflight SHA. Pass the unchanged receipt pair to every family render and to the
selected Google dispatch. The renderer derives the shared admission digest and
route-specific Google tool contract from those receipts.

The receipt establishes one frozen route for the round. The selected
authentication class and route stay fixed. Provider,
auth, entitlement, model, policy, capacity, schema, or output failure follows
the recovery contract; it does not select the other route. TRIAD uses existing
provider authentication and does not sign in, change accounts, or choose a
different billing route.

## Route-specific identity

AGY preflight proves the exact model from the selected executable's literal
tabular catalog. A mismatched exposed model invalidates that leg.

Gemini Enterprise OAuth preserves the authenticated organization account and
Cloud-project selection while removing competing API-key, ADC, Vertex, and
base-URL selectors from the formal child without reading their values. Its CLI
Auto JSON envelope exposes no authoritative single runtime-model identity;
record `runtime_identity: "unexposed"` rather than inferring identity from
`stats.models`, authentication class, Plan Mode, or route.

Gemini records requested approval mode `plan` and effective approval mode
`unexposed`. The packaged mode-independent read/search-only policy is the
user-tier enforcement boundary, with enterprise admin policy above it. Help
surface evidence proves required CLI support, not merged settings or workspace
trust.

## Admission boundary

Provider permission modes are inputs to containment, not admission proof.
Packaged prompt controls, local receipt and `LegVerdict` validation, and the
post-review prepared-directory or worktree integrity check jointly determine
whether a result is admissible. Configured MCP side effects outside those
fingerprinted paths remain prompt-controlled and reviewer-disclosed rather than
mechanically observed.
