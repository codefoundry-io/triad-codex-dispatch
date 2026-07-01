# Spike D Plugin Agent Distribution Decision

**Date:** 2026-07-01
**Scope:** Codex plugin distribution for repair named subagents.

## Retained Evidence

- Personal-scope Codex named subagents under `~/.codex/agents/*.toml` are
  retained-evidence verified spawnable by name. See
  `docs/references/spike-evidence-leader.log` and
  `docs/references/spike-evidence-result.json`.
- Codex plugin packaging, marketplace install, plugin cache install, and
  plugin-shipped skills were verified during the distribution work. The
  install/update flow is implemented through `.codex-plugin/plugin.json`,
  `.agents/plugins/marketplace.json`, and `skills/`.

## Distribution Decision

The distribution layer does **not** rely on plugin-shipped repair agent TOMLs as
a spawn-by-name source. The bootstrap installs `agents/*.toml` into the retained
evidence path, `~/.codex/agents/`, because that personal scope is proven
spawnable.

This is a conservative support decision: plugin-shipped repair agents remain
packaged as source material, but the supported runtime path is personal-scope
installation by `scripts/bootstrap.sh --check`.

## Evidence Boundary

A throwaway Spike D run was cleaned up as required by the handoff guardrails, so
the repo should not cite an uncommitted raw transcript or a specific observed
error string as durable evidence. Until a retained transcript proves otherwise,
documentation should say "plugin-shipped repair agents are not relied on" rather
than cite an unretained negative spawnability claim.
