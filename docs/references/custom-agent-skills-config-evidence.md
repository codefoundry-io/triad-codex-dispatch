# Custom-Agent `skills.config` Evidence

**Date checked:** 2026-07-02

**Source route:** OpenAI docs skill and current Codex manual helper. The helper
reported that the local manual was already current. Official docs establish that
custom agents are TOML files under `$CODEX_HOME/agents/` or `.codex/agents/` and
that `skills.config` is the per-agent skill enablement override schema.

Official anchors used:

- `https://developers.openai.com/codex/subagents#custom-agent-file-schema`
  lists `skills.config` as a supported custom-agent field and shows a
  `[[skills.config]]` example whose `path` value points directly at a
  `SKILL.md` file.
- `https://developers.openai.com/codex/config-reference#skillsconfig` documents
  `skills.config` as an array of per-skill enablement overrides with `enabled`
  and `path`.

## Formal Behavior Check

The check used two fresh non-repair custom agents under a temporary personal
Codex scope:

- disabled negative control: `[[skills.config]] enabled = false`
- enabled positive control: `[[skills.config]] enabled = true`

Observed result:

- The disabled agent spawned in a fresh Codex process and reported the triad
  dispatch skill unavailable. It did not run the wrapper and did not create the
  smoke output file.
- The enabled agent spawned in a fresh Codex process, used the configured triad
  dispatch skill, and completed a bounded code-write smoke in `/private/tmp`.
- The smoke confirmed the output stayed in the requested temporary workspace,
  not in an unrelated caller directory.

## Hot-Reload Boundary

The already running Codex session did not hot-reload newly created custom-agent
TOMLs; direct spawn reported the newly added agent type as unavailable. A fresh
Codex process did load the custom agents and their `skills.config` values.

Distribution consequence: after bootstrap installs or updates files under
`$CODEX_HOME/agents`, users must start a new Codex session/thread before relying
on the newly installed `agent_type` or `skills.config` entries.

## Distribution Rationale

Use `skills.config` for custom subagents that intentionally call triad dispatch
skills. Do **not** add triad dispatch skills to the shipped repair agents:
their `developer_instructions` explicitly forbid invoking triad dispatch skills
or spawning another repair agent recursively.

## Installer Smoke

After this distribution update, a temp `CODEX_HOME` bootstrap smoke ran:

```text
TRIAD_BOOTSTRAP_SKIP_AUTH=1
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never
scripts/bootstrap.sh --check
```

Observed result:

- bootstrap installed repair agents to the temp personal Codex scope
- bootstrap printed the new-session warning for custom agents and
  `skills.config`
- parsing each installed repair-agent TOML confirmed it remains a repair-only
  custom agent without triad dispatch `skills.config`
- plugin validation passed
- full tests passed: `74 passed`
