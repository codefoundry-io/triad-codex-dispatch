# Recommended AGENTS.md For Triad Codex Dispatch Consumers

Use this as a repo-local `AGENTS.md` starting point for teams that install the
Codex-led triad dispatch toolkit.

```md
# Triad Codex Dispatch Usage

Run Codex from the repository root. Installed plugin skills load from the plugin
cache in a new Codex thread; trust the workspace when using repo-local
`.agents/skills/` during development.

Use the installed triad dispatch skills instead of invoking wrapper scripts
directly:

- `$triad-claude-dispatch` for a single-shot Claude Code consult.
- `$triad-antigravity-dispatch` for the primary Google-family consult, including
  web-grounded research and live URL checks when a separate Google-family leg is
  useful.
- `$triad-gemini-dispatch` only for business, Vertex, or API-key Gemini tiers.
- `$triad-cross-family-review` before risky merges.

For sessions that may trigger wrapper repair, start Codex with web search:

```bash
codex --search
```

Do not use `danger-full-access`, `bypassPermissions`, or yolo-style permission
modes for this toolkit. Repair agents may only write:

- `~/.config/triad-codex-dispatch/classifier-patches.json`
- the requested `<run_log>.repair.json` response file

Run before relying on the toolkit on a new machine:

```bash
scripts/bootstrap.sh --check
```

Claude, agy, and business-tier Gemini auth are managed independently from Codex
auth. Auth failures should be surfaced to the user, not repaired by editing the
wrapper engine.
```
