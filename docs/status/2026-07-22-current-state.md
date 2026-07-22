# Triad Codex Dispatch 0.2.527 current state

Date: 2026-07-22

## Authoritative checkout

- Development root:
  `/Users/chaniri/codex_workspace`
- Product repository:
  `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`
- Branch: `codex/triad-reliability-redesign`
- Repair base: `09b4c59f43d76d2b9c47b13e58bff970b9b7d819`
- This document is part of the owner-authorized commit/push publication of the
  approval-inheritance repair. Verify the current `HEAD`, worktree, and remote
  branch before continuing; do not assume the original uncommitted state.

Preserve the unrelated dirty checkout at
`/Users/chaniri/triad-codex-dispatch`. Do not reset, clean, copy over, merge
into, or otherwise modify that checkout.

## Completed implementation gate

- The R13 formal round found one reproducible Major: a reviewer-visible copy of
  a sealed snapshot could not verify because the receipt required its original
  absolute parent path.
- The bounded correction keeps the generated snapshot directory name as its
  logical identity, permits a byte-identical parent relocation, and rejects a
  rename.
- macOS Python 3.12: `603 passed, 6 subtests passed`.
- Ubuntu 24.04 Python 3.12: `602 passed, 1 skipped, 6 subtests passed`.
- R14 used two independent Gemini 3.1 Pro (High) legs and two independent fresh
  Codex legs. All four returned `SAFE`; open questions were empty.
- R14 packet SHA-256:
  `8946f4317acdcd047d19520ca9527382c177053f587092b51c6cf273847b9acd`.
- Immutable records:
  `_runs/reviews/20260722-triad-reliability-formal-r14`.

Two nonblocking follow-ups remain recorded from R14:

1. Claude/Gemini persisted audit argv is stale for a schema-injected or repaired
   Pydantic call, although provider execution and returned results are correct.
2. The English and Korean README audit-redaction descriptions do not match the
   more restrictive runtime behavior.

## Installed state

- `triad-codex-dispatch@triad-codex-dispatch` version `0.2.527` is installed and
  enabled from the Git marketplace branch.
- Installed executable payload:
  `/Users/chaniri/.codex/plugins/cache/triad-codex-dispatch/triad-codex-dispatch/0.2.527`.
- Bootstrap passed twice from that installed path and installed the provider
  launchers, command rules, repair analyzer registration, runtime profile, and
  classifier storage without running provider login or model probes.
- A fresh ordinary Codex session exposed all four triad skills. An actual native
  spawn using exact `agent_type=triad-repair-analyzer` succeeded and returned a
  bounded `escalate` result for a nonexistent proof log.
- The owner then ran the shell-entry installation guide. `~/.zshrc` now contains
  the managed `codex-triad()` function.

## Approval-inheritance repair complete; commit/push authorized

The owner's existing settings are:

```toml
approval_policy = "on-request"
approvals_reviewer = "auto_review"
```

They remain unchanged in both `~/.codex/config.toml` and the workspace
`.codex/config.toml`. The previously generated separate runtime profile instead
contained:

```toml
approval_policy = "on-request"
approvals_reviewer = "user"
default_permissions = "triad_leader"
```

That override violated the owner's requirement to use existing user authority
and approval configuration unchanged. The installed local profile has now been
hotfixed by omitting both approval keys.

Local proof is recorded exactly as:

```text
TRIAD_LOCAL_CLEAN effective_approval=on-request/auto_review pins=3/3 skills=4/4 catalog_version=0.2.527 profile_permission=triad_leader
```

The bounded source repair makes the generated profile omit both
`approval_policy` and `approvals_reviewer` by default, while retaining
`default_permissions = "triad_leader"`. A nonempty
`TRIAD_CODEX_PROFILE_APPROVAL_POLICY` in `on-request`, `never`, or `untrusted`
emits only `approval_policy`; it never emits `approvals_reviewer`. In particular,
`never` remains an advanced opt-in mode.

Completed verification evidence from the workspace-root login-shell boundary:

- Literal `python3`: Python `3.12.13`; pytest `9.0.3`.
- Focused bootstrap tests: `4 passed`.
- Distribution contract: `52 passed`.
- Final tests-directory run: `608 passed, 6 subtests passed in 125.65s` from
  `python3 -m pytest /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/tests -q`.
- Task reviews: approved.
- Initial whole-diff review: `With fixes` only for the handoff/test-plan items
  now addressed by the final-review fix wave.
- Final frozen-artifact re-review: `APPROVED`; no Critical, Important, or Minor
  findings remained, and all three supplied SHA-256 hashes matched.

This evidence does not rewrite or supersede immutable R14 history. The owner
authorized commit and push for this bounded repair. Git history and remote-state
changes go through the workspace's automatic security review and may present an
approval request. Version/changelog changes, reinstall, release, and
pull-request creation remain separate and pending.

## Next handoff boundary

Preserve `_runs/reviews/20260722-triad-reliability-formal-r14` as immutable
history. Do not reinstall, invoke providers, open a pull request, release, bump
the version or changelog, or modify `/Users/chaniri/triad-codex-dispatch`.
Commit and push are authorized only for this reviewed bounded repair; if the
workspace security boundary requests approval, wait for that approval before
continuing. Verify the resulting local and remote branch state.
