# Company Setup: Triad Codex Dispatch

This repo distributes the Codex-led triad dispatch toolkit as a Codex plugin plus
a bootstrap check. Run commands from the repo root after cloning or after adding
the internal marketplace source.

## Verified Distribution Path

- Plugin manifest: `.codex-plugin/plugin.json`, confirmed against the current
  Codex manual and `codex plugin --help`.
- Repo marketplace: `.agents/plugins/marketplace.json`.
- Plugin-shipped skills: confirmed installable through the plugin using the
  plugin `skills/` package mirror.
- Repair agents: **not** spawnable from the plugin cache as of Spike D on
  2026-07-01. The fresh Codex test returned
  `unknown agent_type 'claude-wrapper-repair'`.
- Fallback: `scripts/bootstrap.sh --check` copies `agents/*.toml` into
  `~/.codex/agents/`, the personal scope already verified spawnable.

## Install

For a local clone:

```bash
cd /path/to/triad-codex-dispatch
codex plugin marketplace add .
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

For an internal Git marketplace, replace `.` with the owner-approved internal
source:

```bash
codex plugin marketplace add <internal-git-url-or-owner/repo> --ref main
codex plugin marketplace upgrade
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

Open a new Codex thread after installation. Trust the workspace when Codex asks;
project-local `.agents/skills/` are trust-gated.

## Recommended Codex User Settings

Skills do not bypass the sandbox. Per the OpenAI Codex docs, a skill is loaded
as reusable instructions, and any local commands it causes Codex to run inherit
the active sandbox and approval policy. Keep the normal local-work posture:

```toml
# ~/.codex/config.toml
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = false
```

Do **not** set `sandbox_mode = "danger-full-access"` for this toolkit.

The only user-home writes this distribution layer needs are bootstrap targets:

- `~/.codex/agents/` for personal-scope repair agents.
- `~/.config/triad-codex-dispatch/` for classifier patches.

Default recommendation: leave those outside the sandbox and approve
`scripts/bootstrap.sh --check` when it requests the personal-scope write. If a
team wants bootstrap to run unattended, add only those exact writable roots:

```toml
# ~/.codex/config.toml
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
writable_roots = [
  "/Users/chaniri/.codex/agents",
  "/Users/chaniri/.config/triad-codex-dispatch",
]
network_access = false
```

Replace `/Users/chaniri` with the target user's home directory for managed
rollout templates.

## Update

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin marketplace upgrade triad-codex-dispatch-local
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

Start a new Codex thread after reinstalling so plugin skills are reloaded.

## What Bootstrap Checks

`scripts/bootstrap.sh --check` verifies or installs:

- `codex`, `claude`, `gemini`, `agy`, `python3 >= 3.12`, and `jq`.
- Auth probes for Codex, Claude, Gemini, and agy. Set
  `TRIAD_BOOTSTRAP_SKIP_AUTH=1` only for hermetic CI tests.
- Wrapper launchers for `claude_wrapper.py`, `gemini_wrapper.py`, and
  `antigravity_wrapper.py` when the repo `bin/` directory is not on `PATH`.
  Launchers are small executable scripts, not symlinks.
- Writable classifier extension JSON at
  `~/.config/triad-codex-dispatch/classifier-patches.json`, or
  `TRIAD_CLASSIFIER_EXTENSION` if set.
- Personal-scope repair agents under `~/.codex/agents/`.

If `~/.local/bin` is not on `PATH`, either add it before running bootstrap or set
`TRIAD_BOOTSTRAP_BIN_DIR` to a directory already on `PATH`.

## Auth And Egress

- `claude` must be independently authenticated in the shell. Parent Codex auth
  is not reused by Claude Code.
- Run leader sessions that may need repair as `codex --search ...`; repair
  agents inherit web search from the leader session.
- `agy` is the primary Google-family leg. It needs its own authenticated
  Antigravity setup.
- `gemini` is for business, Vertex, or API-key tiers only. Individual Gemini CLI
  auth is expected to fail with `IneligibleTierError`; use agy instead.
- Allow outbound access for Codex/OpenAI, Claude, Antigravity, and any internal
  Git marketplace source.

## Locked Fleets

Admins can publish this repo as the only allowed marketplace source and disable
public plugin sharing. Owner must provide the final internal source URL.

Example managed requirements shape:

```toml
features.plugins = true
features.plugin_sharing = false

[plugins.sources.triad-codex-dispatch-local]
source = "<internal-git-url>"
ref = "main"
```

Validate the exact managed config keys against the fleet's current Codex admin
policy before rollout.

## Owner Decisions Still Open

- Marketplace source: internal Git URL vs local-clone distribution.
- Classifier path policy: keep isolated `triad-codex-dispatch` path and import
  older `triad-dispatch` patches, or share the old path.
- Keep or drop any future `codex_wrapper.py` path for same-family fresh Codex
  reviewer work.
