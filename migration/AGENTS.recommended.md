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

For sessions that may trigger wrapper repair, start Codex with web search:

```bash
codex --search
```

Do not use `danger-full-access`, `bypassPermissions`, or yolo-style permission
modes for this toolkit. Bootstrap installs shipped repair agents with
`default_permissions = "triad_repair"` so the generated TOML grants read access
to the toolkit checkout, write access only to the classifier config and bounded
run-log IPC area, and network for repair verification. This is the declared
profile grant boundary, not proof that a broader parent session or managed
runtime override cannot allow more. The profile uses bootstrap-injected absolute
filesystem grants for the toolkit checkout, classifier config, bounded run-log
IPC area, Python runtime, and resolved vendor CLI executable directories, not
`:workspace_roots`, so the profile itself does not expand into the caller
workspace. Repair verification strips the original wrapper `--cwd` and runs
from the toolkit checkout; it checks classifier routing, not caller-repo
behavior.
The generated profile grants write access to the classifier config directory and
the bounded `bin/_logs/<cli>/` IPC area. That log area contains run logs,
requested `<run_log>.repair.json` response files, and temporary `.prompt.tmp`
files used for repair verification.

Classifier patch edits must use the adjacent advisory lock file. Runtime
artifacts under `bin/_logs/<cli>/` are bounded by the wrapper, but normal
dispatch should still remove the run log and matching `.repair.json` after the
repair branch is handled.

Run before relying on the toolkit on a new machine:

```bash
scripts/bootstrap.sh --check
```

Claude, agy, and business-tier Gemini auth are managed independently from Codex
auth. Auth failures should be surfaced to the user, not repaired by editing the
wrapper engine.
```
