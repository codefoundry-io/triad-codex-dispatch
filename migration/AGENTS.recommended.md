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
- `$triad-gemini-dispatch` for a standalone authorized Gemini CLI compatibility
  consult; it does not choose or lead a formal Google-family review.
- `$triad-cross-family-review` before risky merges.

For formal review, record `personal-google` or `gemini-enterprise` before any
family starts. Personal Google Sign-In requires AGY. Gemini Enterprise OAuth
prefers AGY and selects Gemini CLI only when AGY is absent. Freeze the selected
route by exclusive-creating one review-ID selector receipt, preflight it once,
then pass that selector and canonical preflight receipt through every render and
Google dispatch; bind both receipt SHA values plus the selected model and effort into
the common review digest. Never
switch after the selected provider starts or fails.

Once any provider leg has started, a later required-leg start or result failure invalidates
admission but already-started sibling families finish. Strictly validate their
available terminal results and run post-review integrity verification. Preserve
valid sibling findings as advisory only, reproduce and correct every in-scope
defect, then classify and correct the failed leg or verify recovery from a transient vendor incident before a fresh complete
three-family round. No sibling result admits the failed round or supplies later
admission credit.

Select provider permissions and project trust in that authenticated developer
environment before dispatch. TRIAD does not install a separate Codex profile,
rule, permission mode, or pre-spawn `shell_environment_policy`. The Codex-led
AGY wrapper deliberately selects AGY native headless `always-proceed` for that
child through its internal `--dangerously-skip-permissions` flag; callers do not
pass the flag, and this does not change stored or global user/project settings.
Trusted Python and `PATH` values are prerequisites. After trusted launcher and
interpreter startup, wrapper descendants remain scrubbed of loader and
interpreter injection variables.

Launch all TRIAD lifecycle, provider, test, and development commands outside the
Codex workspace sandbox under the user-selected Codex host policy. Use an
interactive company-compatible policy: `sandbox_mode = "workspace-write"`,
`approval_policy = "on-request"`, and `approvals_reviewer = "user"` for a human
Yes/No decision. Where organization policy permits an agent reviewer, change
only that last field to `approvals_reviewer = "auto_review"`; this changes the
reviewer, not the permission grant. Ask for the outside-sandbox launch directly
instead of first running a command that is known to fail in the workspace
sandbox. The OpenAI plugin model applies the host sandbox and approval policy to
plugin capabilities and documents no plugin-level install-time sandbox grant.
TRIAD does not install or mutate that host policy. Do not mix permission profiles
with legacy `sandbox_mode` settings.

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

For source-SOT pre-deployment staging, follow the canonical leg-contract recipe:
preserve login `HOME` and `CODEX_HOME`, and scope bootstrap's Codex directory with
`TRIAD_BOOTSTRAP_CODEX_ROOT`. This does not change provider authentication or grant
authority over other user-global paths.

Claude, AGY, and organization Gemini Enterprise OAuth are managed independently
from Codex auth. Auth failures should be surfaced to the user, not repaired by
editing the wrapper engine.
```
