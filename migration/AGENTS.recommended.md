# Recommended AGENTS.md For Triad Codex Dispatch Consumers

Use this as a repo-local `AGENTS.md` starting point for teams that install the
Codex-led triad dispatch toolkit.

```md
# Triad Codex Dispatch Usage

Run TRIAD from the same authenticated login terminal and repository worktree
used for development. Installed plugin skills load from the plugin cache in a
new Codex thread. Do not add a repo-local `.agents/skills/` mirror for this
toolkit while the plugin is installed, or Codex will show duplicate triad
skills.

Use the installed triad dispatch skills instead of invoking wrapper scripts
directly:

- `$triad-claude-dispatch` for a single-shot Claude Code consult.
- `$triad-antigravity-dispatch` for the primary Google-family consult, including
  web-grounded research and live URL checks when a separate Google-family leg is
  useful.
- `$triad-gemini-dispatch` only for business, Vertex, or API-key Gemini tiers.
- `$triad-cross-family-review` before risky merges.

Select provider permissions and project trust in that authenticated developer
environment before dispatch. TRIAD inherits provider permissions without
changing them and does not install a separate Codex profile, rule, permission
mode, or pre-spawn `shell_environment_policy`. Trusted Python and `PATH` values
are prerequisites. After trusted launcher and interpreter startup, wrapper
descendants remain scrubbed of loader and interpreter injection variables.

Repair analysis uses a fresh native proposal-only child with prompt-controlled
no-edit behavior. The child reads an untrusted absolute run-log path and the
local classifier framework as needed, then returns a proposal or escalation.
The owner applies a validated proposal locally from the authenticated terminal
with the printed absolute bootstrap command for `bin/apply_patch.py`, including
the pinned absolute `--classifier-file`. Run logs remain available as untrusted
evidence until the wrapper's age-floor cleanup; do not manually remove them
after analysis.

The plugin-add step prints a safely quoted absolute bootstrap command from its
returned `installedPath`. Run that printed absolute bootstrap command exactly
from a normal terminal outside the plugin cache or checkout. Do not carry a
temporary plugin-path variable across terminal or process boundaries.

Claude, agy, and business-tier Gemini auth are managed independently from Codex
auth. Auth failures should be surfaced to the user, not repaired by editing the
wrapper engine.
```
