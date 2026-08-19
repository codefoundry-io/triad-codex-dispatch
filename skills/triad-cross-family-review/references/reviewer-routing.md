# Formal reviewer routing

This is an owner routing policy, not a provider capability claim. The owner
authorizes the exact providers, objective, and external data boundary before a
round. Native provider authentication remains in force. The formal Google leg
uses native AGY CLI sign-in and the deployed Claude-led TRIAD settings
transaction lifecycle.

## Required routes

- Claude: `opus`, `xhigh`, retained 1,800-second end-to-end wrapper deadline.
- Google: AGY 1.1.12 or newer, `gemini-3.1-pro-high`, `high`, retained
  1,800-second end-to-end wrapper deadline, and one owner-selected native
  authentication class: personal Google Sign-In or Business Sign-In for
  Gemini Enterprise with a GE Standard or GE Plus seat.
- Fresh Codex: `gpt-5.6-terra`, `xhigh`, `fork_turns="none"`, no registered
  reviewer agent.

Use [leg contracts](leg-contracts.md) for invocation details. Record the
owner-selected authentication class and any runtime-exposed identity. Record an unexposed identity
as `unexposed`; do not infer it. A conflict with exposed identity invalidates
the leg.

Both authentication classes use the same AGY executable, packaged wrapper,
model, settings transaction, and containment contract. TRIAD never signs in, changes the
active account, or falls back between authentication classes. If the selected
authentication, entitlement, model, or containment contract is unavailable,
the formal round is invalid.

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
