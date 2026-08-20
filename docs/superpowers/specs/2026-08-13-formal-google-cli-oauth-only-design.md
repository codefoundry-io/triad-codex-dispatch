# Formal AGY Native-Sign-In Design

> **Historical, superseded, and non-executable.** TRIAD 0.2.541 supersedes this
> design. A bounded AGY 1.1.16 Business Sign-In runtime probe on 2026-08-20 ran
> with `--dangerously-skip-permissions`, attempted `write_to_file`, and returned
> `Matches user-configured deny rule`; the target remained absent. The current
> authority is `skills/triad-antigravity-dispatch/SKILL.md` plus the current
> cross-family leg and prompt contracts. The contrary historical claim below
> that the flag voids the deny transaction is non-executable.

**Owner decision:** Formal three-family review keeps both owner environments
through AGY 1.1.10 or newer: personal Google Sign-In and Business Sign-In for
Gemini Enterprise with a GE Standard or GE Plus seat. TRIAD records the active
class before a round and never changes the provider account or billing route.

## Behavioral claim

A formal Google-family review leg uses the deployed Claude-led TRIAD AGY
settings-transaction lifecycle while preserving the owner-selected personal or
Gemini Enterprise native sign-in.

## Proven source contract

- Source: `/Users/chaniri/triad` at local `main` containing remote `origin/main`.
- Deployment: `/Users/chaniri/triad-dispatch` at remote `origin/main`.
- The source and deployment `antigravity_wrapper.py` and `_agy_settings.py`
  SHA-256 values agree.
- AGY exposes no consumed per-call, per-workspace, or project permission file
  for headless review. Its effective permission source is the global
  `~/.gemini/antigravity-cli/settings.json`.
- The wrapper holds an `flock`, snapshots the original settings, unions
  `write_file(*)`, `command(*)`, `unsandboxed(*)`, `execute_url(*)`, and
  `mcp(*)`, runs AGY, and restores the original bytes. A crash sentinel supports
  recovery.
- Formal calls pass `--sandbox read-only`. Unless the operator sets
  `AGY_NO_HEADLESS_AUTOAPPROVE=1`, AGY 1.1.3+ also receives the wrapper-owned
  `--dangerously-skip-permissions` headless adaptation. That flag
  voids both the deny transaction and AGY OS-ring enforcement, so the admitted
  boundary is read-only intent plus disposable review-directory and worktree
  fingerprint verification.

## Authentication and billing boundary

- AGY owns personal Google Sign-In and Gemini Enterprise Business Sign-In.
- The formal child removes known API-key, ADC, Vertex, SDK-enterprise, and cloud
  billing-route selector names without reading their values.
- TRIAD does not sign in, refresh credentials, switch accounts, or fall back to
  API-key, Vertex, ADC, service-account, or another authentication class.
- `gemini_wrapper.py` remains a standalone compatibility consult and is not the
  Enterprise formal leg.

## Rejected Project-permission design

The superseded design required `--project` and a project JSON deny list. It was
rejected by runtime evidence on AGY 1.1.12:

1. The provider-generated project record could contain all five deny entries,
   yet a token-zero `/permissions` run reported an empty project scope.
2. Adding the documented centralized workspace-to-project mapping did not make
   the project deny entries effective.
3. The interactive project permission editor wrote the deny entries to global
   `settings.json`, not to an effective project-scoped headless policy.
4. After removing that accidental global delta, the same token-zero probe again
   showed no project denies.

No future divergence from Claude parity is allowed without a disposable runtime
spike that demonstrates stronger containment while preserving native personal
and Gemini Enterprise authentication and formal review executability.

## Acceptance

1. Unit tests prove the deny lease is live during the call and the original
   settings bytes return after normal exit, provider failure, and body exception.
2. Formal wrapper tests require `--sandbox read-only`, version-gated
   auto-approve, native schema binding, and billed-route environment scrubbing.
3. Skill-executor tests retain both authentication classes and stop before all
   families when the settings transaction cannot be established.
4. Formal three-family review runs only after all static and runtime gates pass.
