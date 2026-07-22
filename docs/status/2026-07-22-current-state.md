# Triad Codex Dispatch 0.2.527 current state

Date: 2026-07-22

## Authoritative checkout

- Development root:
  `/Users/chaniri/codex_workspace`
- Product repository:
  `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`
- Branch: `codex/triad-reliability-redesign`
- Commit: `177c9901d3e43b10f3736742455ad8da70068bed`
- The local branch and `origin/codex/triad-reliability-redesign` match and the
  product worktree was clean before this handoff document was added.

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

## Newly discovered distribution defect

The owner's existing settings are:

```toml
approval_policy = "on-request"
approvals_reviewer = "auto_review"
```

They remain unchanged in both `~/.codex/config.toml` and the workspace
`.codex/config.toml`. However, the generated separate runtime profile currently
contains:

```toml
approval_policy = "on-request"
approvals_reviewer = "user"
default_permissions = "triad_leader"
```

Therefore a session started through the installed `codex-triad` function uses
`approvals_reviewer="user"` instead of inheriting the owner's Agent review
setting. `approval_policy=never` was not installed, but this reviewer override
still violates the owner's requirement to use existing user authority and
approval configuration unchanged.

This defect was discovered after the R14 reviewed commit. It is recorded but
not fixed. The current general first-install guidance is not ready for release
until the runtime profile inherits `approval_policy` and `approvals_reviewer`
by default. `codex-triad` must remain optional, and any explicit session-wide
`approval_policy=never` mode must remain a separately requested advanced mode.

## Fresh-session boundary

The next session begins with evidence-only skill testing. Do not edit source,
user config, shell RC files, plugin installation, or Git history before the
owner sees the test results. In particular, do not silently replace Agent
review, do not set `approval_policy=never`, and do not treat a prompt-only role
claim as proof of a custom-agent selector.

After the test report, ask the owner whether to implement the bounded profile
inheritance repair. If approved, keep it small: profile generation and directly
affected bootstrap tests/docs only, with no new launcher or permission system.
