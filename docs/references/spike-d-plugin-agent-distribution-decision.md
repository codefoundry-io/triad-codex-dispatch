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

## Custom-Agent Skill Enablement Follow-Up

On 2026-07-02, the formal Codex custom-agent path was checked against the current
OpenAI Codex docs: custom agents are TOML files under `$CODEX_HOME/agents/` or
`.codex/agents/`, and `skills.config` is the documented per-agent skill
enablement schema. The retained summary is
`docs/references/custom-agent-skills-config-evidence.md`.

The retained behavior boundary for this repo is:

- A fresh Codex process loaded custom agents installed under
  `$CODEX_HOME/agents/` and honored `[[skills.config]]`.
- A disabled negative-control agent (`enabled = false`) could not use the triad
  dispatch skill.
- An enabled positive-control agent (`enabled = true`) used the configured triad
  dispatch skill and completed a code-write smoke in `/private/tmp`.
- The already running Codex session did not hot-reload newly created custom
  agent TOMLs; a fresh session/process was required before the new agent type
  became available.

Distribution consequence: bootstrap must install repair agents into the
personal custom-agent scope, and docs must tell users to start a new Codex
session/thread after install or update. `skills.config` is documented for user
custom subagents that intentionally call triad dispatch skills; shipped repair
agents do not enable dispatch skills because recursive dispatch is forbidden.

## Evidence Boundary

A throwaway Spike D run was cleaned up as required by the handoff guardrails, so
the repo should not cite an uncommitted raw transcript or a specific observed
error string as durable evidence. Until a retained transcript proves otherwise,
documentation should say "plugin-shipped repair agents are not relied on" rather
than cite an unretained negative spawnability claim.
