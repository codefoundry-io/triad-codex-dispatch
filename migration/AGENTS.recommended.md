# Recommended AGENTS.md For Triad Codex Dispatch Consumers

Use this as a repo-local `AGENTS.md` starting point for teams that install the
Codex-led triad dispatch toolkit.

```md
# Triad Codex Dispatch Usage

Run Codex from the repository root. Installed plugin skills load from the plugin
cache in a new Codex thread. Do not add a repo-local `.agents/skills/` mirror for
this toolkit while the plugin is installed, or Codex will show duplicate triad
skills.

Use the installed triad dispatch skills instead of invoking wrapper scripts
directly:

- `$triad-claude-dispatch` for a single-shot Claude Code consult.
- `$triad-antigravity-dispatch` for the primary Google-family consult, including
  web-grounded research and live URL checks when a separate Google-family leg is
  useful.
- `$triad-gemini-dispatch` only for business, Vertex, or API-key Gemini tiers.
- `$triad-cross-family-review` before risky merges.

Do not use `danger-full-access`, `bypassPermissions`, or yolo-style permission
modes for this toolkit. Repair uses the exact registered
`triad-repair-analyzer` Custom Agent, which pins a read-only sandbox. The agent
reads an untrusted absolute run-log path and the local classifier framework as
needed, then returns a proposal or escalation. It makes no provider or network
calls and performs no edits.

The owner applies a validated proposal from a normal authenticated terminal with
`triad-apply-repair --cli <cli> --proposal-file <absolute-path>`. Run logs remain
available as untrusted evidence until the wrapper's age-floor cleanup; do not
manually remove them after analysis.

The plugin-add step prints a safely quoted absolute bootstrap command from its
returned `installedPath`. Run that printed absolute bootstrap command exactly
from a normal terminal outside the plugin cache or checkout. Do not carry a
temporary plugin-path variable across terminal or process boundaries.

Claude, agy, and business-tier Gemini auth are managed independently from Codex
auth. Auth failures should be surfaced to the user, not repaired by editing the
wrapper engine.
```
