# Formal reviewer routing

This is an owner routing policy, not a provider capability claim. The owner
authorizes the exact providers, objective, and external data boundary before a
round. Native provider authentication remains in force. The formal Google leg
uses one pre-dispatch, owner-selected authentication class and one frozen route.

## Required routes

- Claude: `opus`, `xhigh`, retained 1,800-second end-to-end wrapper deadline.
- Google authentication class `personal-google`: personal Google Sign-In requires AGY
  1.1.20 or newer, `gemini-3.1-pro-high`, `high`, and the retained 1,800-second deadline.
- Google authentication class `gemini-enterprise`: AGY is preferred with the same
  contract. Gemini Enterprise OAuth may select Gemini only when AGY is absent. That route uses
  the already authenticated organization account, Gemini CLI Auto router forced by
  `-m auto`, requested native Plan Mode, a mode-independent packaged read/search-only
  policy as the enforcement boundary, and the retained 1,800-second deadline.
- Fresh Codex: `gpt-5.6-terra`, `xhigh`, `fork_turns="none"`, no registered
  reviewer agent.

Use [leg contracts](leg-contracts.md) for invocation details. Record the
owner-selected authentication class, selector receipt, and any runtime-exposed identity.
The current Gemini CLI Auto JSON envelope exposes no authoritative single runtime-model identity;
its `stats.models` value is multi-model usage telemetry. Record exactly `unexposed` and do not infer
identity from telemetry, Plan Mode, authentication class, or route. AGY retains its exposed-model
comparison and invalidates a conflicting leg.

Gemini reports requested approval mode `plan` and effective approval mode
`unexposed`. Do not infer trust or merged settings from help output. The exact
mode-independent policy remains active if Gemini resolves a different approval
mode; TRIAD never adds `--skip-trust` or reads user settings to speculate about it.

Before starting any family, run the bootstrap-managed `review_round.py select-google-route`
launcher for the packaged script with
`--review-id`, `--authentication-class personal-google|gemini-enterprise`, and a new round-owned
`--output`. The exact canonical receipt must report `provider_started:false` plus the review ID,
selected executable, wrapper, route, and authentication class. Preflight only the recorded wrapper
with the current task file before rendering any family prompt. Its canonical output must repeat the
review ID, route, executable, and selector SHA. After it succeeds, pass both receipts
to every family render and the selected wrapper's dispatch; render rejects a mismatched pair and derives the common admission digest
and Google tool contract from it, while the wrapper executes its recorded executable directly.
Never rerun or replace the receipt in that round. Never switch
routes after the selected provider starts. An AGY version,
model, settings, auth, entitlement, capacity, schema, or provider failure does not select Gemini;
a Gemini failure does not select AGY. TRIAD never signs in, changes accounts, or switches
authentication classes. Unavailable selected authentication, model, policy, or containment
invalidates the round.

The Gemini Enterprise OAuth route preserves cached Sign in with Google and organization Cloud-project
selection. It removes competing API-key, ADC, and Vertex selectors from the formal child without
reading their values. It is not an API-key or Vertex fallback. The packaged user-tier policy
replaces configured user policy paths for that invocation; enterprise admin policy remains higher
priority, while prompt controls and final integrity verification still decide review admission.

## Admission and convergence

Every family reviews the same complete focused source view and returns one
validated `LegVerdict` for the same review ID and digest. No batch, shard, or
receipt compatibility mode is supported. Provider permissions do not prove a
no-edit boundary; prompt controls and integrity verification decide admission
within their stated scopes. Round integrity verification binds the selected
prepared-directory bytes or worktree review digest plus canonical worktree fingerprint.
At the first required-leg failure, terminate every still-running leg and its
exact provider process group, discard every current-round verdict, and never
continue a sibling merely to collect advisory evidence. Confirm termination,
verify integrity, clean the exact round, and repair the defect before a fresh ID.
External-state change through a configured
MCP tool is prompt-controlled and reviewer-disclosed; it is not mechanically
observed by round integrity.

Use [convergence](convergence.md) after all legs terminate. The leader may fix
only a reproduced bounded defect inside approved design. Design,
specification, capability, generalization, and scope changes require an owner
decision before editing. A correction creates a new digest and a fresh
complete three-family round.
