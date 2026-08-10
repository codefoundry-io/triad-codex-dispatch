# Formal reviewer routing

This is an owner routing policy, not a provider capability claim. The owner
authorizes the exact providers, objective, and external data boundary before a
round. Except for the documented packaged AGY child `always-proceed` selection,
native provider and project permissions remain in force.

## Required routes

- Claude: `opus`, `xhigh`, retained 1,800-second end-to-end wrapper deadline.
- Google: AGY 1.1.10 or newer, `gemini-3.1-pro-high`, `high`, 1,800-second
  end-to-end wrapper deadline.
- Fresh Codex: `gpt-5.6-terra`, `xhigh`, `fork_turns="none"`, no registered
  reviewer agent.

Use [leg contracts](leg-contracts.md) for invocation details. Record requested
route evidence and any runtime-exposed identity. Record an unexposed identity
as `unexposed`; do not infer it. A conflict with exposed identity invalidates
the leg.

AGY is the default Google route. If AGY is unavailable before provider
submission, the leader may select the separately authorized Gemini route
before starting a fresh round. A post-submission AGY failure invalidates the
Google leg and cannot be replaced inside that round.

## Admission and convergence

Every family reviews the same complete focused directory and returns one
validated `LegVerdict` for the same review ID and digest. No batch, shard, or
receipt compatibility mode is supported. Provider permissions do not prove a
no-edit boundary; prompt controls and integrity verification decide admission
within their stated scopes. Round integrity verification binds prepared-directory
and canonical worktree bytes only. External-state change through a configured
MCP tool is prompt-controlled and reviewer-disclosed; it is not mechanically
observed by round integrity.

Use [convergence](convergence.md) after all legs terminate. The leader may fix
only a reproduced bounded defect inside approved design. Design,
specification, capability, generalization, and scope changes require an owner
decision before editing. A correction creates a new digest and a fresh
complete three-family round.
