# Formal reviewer routing

This owner routing policy chooses the review families and one Google
authentication class. It does not claim provider capability or authorize a
provider beyond the current task's objective and external-data boundary.

This table describes the legacy entry point. Explicit public v2 resolves its
named roster and per-CLI settings through [the v2 procedure](public-v2-review.md).

## Required routes

The table retains the standard legacy deadlines. Explicit `--timeout 2400` is
also supported for each provider wrapper; use it when the owner requests a
40-minute review. Previous 1200/600-second calls remain valid. Other legacy
deadline values are refused; ordinary/raw and public-v2 defaults are unchanged.

| Family | Formal route |
|---|---|
| Claude | `opus`, `xhigh`, 1,200-second wrapper deadline |
| Google with `personal-google` | AGY 1.2.1 or newer, `gemini-4-argon-high`, `high`, 600-second wrapper deadline |
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

### Explicit workspace paired worktree opt-in

Only when owner-governed workspace instructions require both Argon and Flash, use
the fixed paired `render-worktree` path. Keep one AGY selector and preflight
`gemini-4-argon-high` / `high` and `gemini-3.8-flash-high` / `high` separately.
Every family render receives the Argon receipt as `--google-preflight-receipt` and
the Flash receipt as `--google-flash-preflight-receipt`. For Flash only, add
`--google-review-model gemini-3.8-flash-high` to the Google-family render. The
renderer binds both receipts into the common digest and selects the correct
member for dispatch. Each Google wrapper invocation uses its own selected
preflight receipt and exact model/high arguments. Do not edit rendered metadata
or use the focus overlay to turn Argon into Flash. The public default remains
three-family; prepared rendering has no paired opt-in. Workspace instructions
own extra-leg admission and conditional native advice, not this public schema.

### Runtime identity

AGY preflight binds the requested model without a catalog probe. That request
does not prove runtime identity. A mismatched exposed model invalidates that leg.

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

Gemini preflight records `policy_sha256` from the exact packaged policy bytes
it validates. Rendering and dispatch verify that hash against the current
policy file. Regenerate preflight after a policy change or when an older receipt
lacks the hash. This binds bytes; it does not attest to merged runtime settings.

Gemini preflight first runs the selected executable's `--version` with a maximum
15-second timeout and the formal scrubbed environment. It requires SemVer
>=0.63.0 before the existing help probe and records the exact `gemini_version`.
Regenerate receipts missing this field. A prerelease of 0.63.0 is below the floor;
build metadata does not affect precedence. The receipt hash binds the observation,
which does not by itself prove authentication, runtime model or policy enforcement.

## Admission boundary

Public v2 binds standing authorization through [the v2 web procedure](review-web.md).

Legacy REVIEW defaults to no web; a direct owner request selects
[the common bound option](review-web.md). Legacy no-web AGY formal calls select the no-web
native-tool profile; authorized web selects its research twin. Both exclude
default components and omit headless autoapproval. No global settings writes,
locks or restoration occur. Explicit project validation retains its deny-rule
checks. Raw read-only uses the research profile; permissive raw remains separate.
Gemini's packaged no-web REVIEW policy explicitly denies its web read/search
tools and retains B's other deny rules. Byte/policy-engine checks remain distinct
from unrun authenticated effective-policy checks.

Provider permission modes are inputs to containment, not admission proof.
Packaged prompt controls, local receipt and `LegVerdict` validation, and the
post-review prepared-directory or worktree integrity check jointly determine
whether a result is admissible. Configured MCP side effects outside those
fingerprinted paths remain prompt-controlled and reviewer-disclosed rather than
mechanically observed.
