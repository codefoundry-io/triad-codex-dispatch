# Codex Permission Profile Evidence

Date checked: 2026-07-01

Source route: OpenAI docs skill -> current Codex manual helper
(`developers.openai.com/codex/codex-manual.md`). The helper reported: "local
manual was already current."

## What The Official Codex Manual Establishes

- Codex supports named permission profiles for reusable filesystem and network
  policy. Built-ins are `:read-only`, `:workspace`, and
  `:danger-full-access`; custom profiles use `[permissions.<name>]` tables and a
  matching `default_permissions` value. Source pages:
  `config-basic.md`, `config-reference.md`, and `permissions.md`.
- Filesystem profile entries use `read`, `write`, and `deny`. `write` includes
  create, modify, rename, and delete under the granted path when the OS allows
  it. `read` is the intended grant for files and runtime paths that commands
  only need to inspect or execute through the active sandbox. Source page:
  `permissions.md`.
- Filesystem path forms include `:minimal`, which the manual describes as the
  platform and runtime paths needed by common tools. The repair profile uses it
  as a baseline and then adds explicit absolute grants for toolkit, classifier,
  runtime, and vendor executable paths. Source page: `permissions.md`.
- Network profiles use `[permissions.<name>.network] enabled = true` for network
  access. Source page: `permissions.md`.
- Codex rules control which commands Codex can run outside the sandbox.
  `prefix_rule(decision = "allow")` is documented as running the matching
  command outside the sandbox without prompting. Rules match argv prefixes and
  the `match` / `not_match` examples are validated when Codex loads the rules.
  Source page: `rules.md`.
- Custom agents live under `~/.codex/agents/` or `.codex/agents/` and load as
  configuration layers for spawned sessions. Custom agent files can include
  supported `config.toml` keys in addition to required `name`, `description`,
  and `developer_instructions`. Source page: `subagents.md`.
- Subagents inherit the parent sandbox policy and runtime overrides, while a
  custom agent file can override sandbox configuration. Permission profiles are
  the documented successor to the older `sandbox_mode` +
  `sandbox_workspace_write` combination for filesystem and network policy.
  Source pages: `subagents.md`, `config-advanced.md`, and `permissions.md`.

## Boundary

The retained spike evidence proves personal-scope custom agents are spawnable by
name from `~/.codex/agents/` and can inherit web search. It does **not** by
itself prove permission-profile behavior. The permission-profile schema comes
from the current official Codex manual above; bootstrap and docs tests then
verify that shipped repair-agent TOMLs use that schema and that bootstrap
injects absolute paths without stale placeholders.

## Profile-Bearing Spawn Proof

After running `TRIAD_BOOTSTRAP_SKIP_AUTH=1 scripts/bootstrap.sh --check` in this
checkout on 2026-07-02, the already installed personal-scope
`claude-wrapper-repair` custom agent was spawned by name from a fresh tool call.
The first attempted proof path under `_runs/` was corrected to the scoped repair
write area. The agent completed with `done` and wrote:

```json
{"ok":true,"agent":"claude-wrapper-repair","profile":"triad_repair","path":"bin/_logs"}
```

to `bin/_logs/profile-spawn-proof.json`. That file was validated with
`python3 -m json.tool`. The proof file is a runtime artifact and is not tracked.
