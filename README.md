# triad-codex-dispatch

[한국어 README](README.ko.md)

Codex-led triad dispatch for power users who already use the OpenAI Codex CLI,
Claude Code, and Antigravity (`agy`). Codex stays the leader and can dispatch
Claude, agy, and optional business-tier Gemini as single-shot workers through
packaged Codex skills and wrapper launchers.

This README is for the public GitHub distribution.

## What You Get

- Codex plugin skills under `skills/`.
- Wrapper launchers for Claude, agy, and Gemini.
- Codex custom repair agents installed under `$CODEX_HOME/agents` or
  `~/.codex/agents`.
- A generated Codex profile and command rules so approved wrapper calls run
  outside the sandbox without repeated prompts.

## Requirements

Install and log in before running bootstrap:

- `codex`
- `claude`
- `agy`

Optional:

- `gemini`, only for business, Vertex, or API-key Gemini accounts. Individual
  Google-family users should use `agy`.

Host tools:

- `git`, `jq`, and `python3 >= 3.12`
- Linux/WSL2: install `bubblewrap` (`bwrap`) for Codex sandbox support.
- Make sure `~/.local/bin` is on `PATH`, or set `TRIAD_BOOTSTRAP_BIN_DIR` to a
  directory already on `PATH`.

The installer does not perform OAuth login and does not install OS packages.

## Install

Install directly from the public GitHub repository. No local clone is required
for normal users.

Repository: https://github.com/codefoundry-io/triad-codex-dispatch

Choose one install scope before running install/update/remove commands:

- User scope: recommended default. Leave `CODEX_HOME`, `XDG_CONFIG_HOME`, and
  `TRIAD_BOOTSTRAP_BIN_DIR` unset.
- Workspace scope: use only when you want plugin cache, profile, rules,
  classifier patches, and launchers under the current workspace. Run from that
  workspace and keep the same environment when starting Codex.

```bash
# Workspace scope only. Skip this block for user scope.
mkdir -p .triad-codex-home .triad-config .triad-bin
export CODEX_HOME="$PWD/.triad-codex-home"
export XDG_CONFIG_HOME="$PWD/.triad-config"
export TRIAD_BOOTSTRAP_BIN_DIR="$PWD/.triad-bin"
export PATH="$TRIAD_BOOTSTRAP_BIN_DIR:$PATH"
```

```bash
codex plugin marketplace add codefoundry-io/triad-codex-dispatch --ref main

TRIAD_PLUGIN_DIR="$(
  codex plugin add triad-codex-dispatch@triad-codex-dispatch --json |
    jq -r '.installedPath'
)"

# No-prompt install for this plugin's target users.
# Conservative install: remove the three env lines below and run only bootstrap;
# Codex may ask for external-CLI approvals.
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --check
```

Then start a new Codex session:

```bash
codex --profile triad-codex-dispatch --search
```

Important install behavior:

- User scope writes repair agents, profile, and command rules under
  `~/.codex/`.
- User scope writes classifier patches under `~/.config/triad-codex-dispatch/`.
- User scope writes wrapper launchers under `~/.local/bin` unless
  `TRIAD_BOOTSTRAP_BIN_DIR` is set.
- Workspace scope writes those same artifacts under `.triad-codex-home/`,
  `.triad-config/`, and `.triad-bin/`.
- The generated wrapper launchers call files from the installed plugin cache.
  Rerun bootstrap after every plugin update so those paths stay current.
- The launchers pin resolved vendor CLI paths. Rerun bootstrap after upgrading
  or moving `claude`, `agy`, or optional `gemini`.
- Existing Codex sessions may not see newly installed plugin skills or custom
  agents. Start a new session after install or update.
- agy calls may transact against Antigravity CLI runtime settings under
  `~/.gemini/antigravity-cli/`; that is provider runtime state, not a bootstrap
  install target.
- `codex plugin add --json` reports marketplace `authPolicy`; this plugin still
  does not perform CLI OAuth/login.

## Recommended Shell Entry

Add a command that always starts Codex with the triad profile from the current
workspace. For workspace scope, export the same scope variables before using
this command.

```bash
TRIAD_SHELL_RC="${HOME}/.bashrc"
case "${SHELL:-}" in
  */zsh) TRIAD_SHELL_RC="${HOME}/.zshrc" ;;
esac

cat >> "$TRIAD_SHELL_RC" <<'EOF'
codex-triad() {
  TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}" \
    command codex --profile triad-codex-dispatch --search "$@"
}
EOF

. "$TRIAD_SHELL_RC"
codex-triad
```

Use an alias/function for plain `codex` only on machines where this no-prompt
external-CLI posture should be the default.

## Use

Ask Codex to use these installed skills:

- `triad-claude-dispatch`: single-shot Claude Code consult.
- `triad-antigravity-dispatch`: primary Google-family consult through `agy`.
- `triad-gemini-dispatch`: Gemini business/Vertex/API-key accounts only.
- `triad-cross-family-review`: pre-merge review across Claude, Google-family,
  and a fresh Codex subagent.

Normal code-write dispatch should run from the target workspace. Wrappers trust
their process working directory by default. Set `TRIAD_WRAPPER_ALLOWED_ROOTS`
only when you need additional trusted roots.

## Update

For workspace scope, export the same scope variables from install first.

```bash
codex plugin marketplace upgrade triad-codex-dispatch

TRIAD_PLUGIN_DIR="$(
  codex plugin add triad-codex-dispatch@triad-codex-dispatch --json |
    jq -r '.installedPath'
)"

TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --check
```

Start a new Codex session after updating.

## Remove

Default user-home removal:

```bash
codex plugin remove triad-codex-dispatch@triad-codex-dispatch
codex plugin marketplace remove triad-codex-dispatch

rm -f ~/.codex/agents/claude-wrapper-repair.toml
rm -f ~/.codex/agents/gemini-wrapper-repair.toml
rm -f ~/.codex/agents/agy-wrapper-repair.toml
rm -f ~/.codex/triad-codex-dispatch.config.toml
rm -f ~/.codex/rules/triad-codex-dispatch.rules

rm -f ~/.local/bin/claude_wrapper.py
rm -f ~/.local/bin/gemini_wrapper.py
rm -f ~/.local/bin/antigravity_wrapper.py
rm -rf ~/.config/triad-codex-dispatch
```

If you installed with a custom `CODEX_HOME`, remove the agent/profile/rules
files from that directory instead of `~/.codex`.
If you used a custom `TRIAD_BOOTSTRAP_BIN_DIR`, remove the three wrapper
launchers from that directory instead of `~/.local/bin`. For custom `XDG_CONFIG_HOME`,
remove `triad-codex-dispatch/` under that config directory instead of
`~/.config/triad-codex-dispatch`.

Workspace scope removal:

```bash
export CODEX_HOME="$PWD/.triad-codex-home"
export XDG_CONFIG_HOME="$PWD/.triad-config"
export TRIAD_BOOTSTRAP_BIN_DIR="$PWD/.triad-bin"
export PATH="$TRIAD_BOOTSTRAP_BIN_DIR:$PATH"

codex plugin remove triad-codex-dispatch@triad-codex-dispatch
codex plugin marketplace remove triad-codex-dispatch

rm -rf .triad-codex-home .triad-config .triad-bin
```

## Custom Subagents

The shipped repair agents are repair-only and must not recursively dispatch.
Do not add triad dispatch skills to those repair agents.

If you create your own Codex custom subagent that should call triad dispatch
skills, opt in explicitly with Codex `skills.config` entries pointing at the
needed `SKILL.md` files under the `TRIAD_PLUGIN_DIR` value from install/update.

After editing custom-agent TOML files, start a new Codex session.

## Runtime Logs And Local Data

Runtime telemetry is local under the installed plugin's `bin/_logs/<cli>/`.
`audit.jsonl` keeps redacted argv, prompt length, status, 500-character
stdout/stderr heads, and structured-output presence/length only. Failure run
logs keep full prompts and vendor transcripts for repair replay, then skills
delete them after repair; a failsafe caps stale run logs. Treat these files as
sensitive and remove `bin/_logs/` when needed.

`approval_policy=never` applies to the whole triad Codex session, not only this
plugin. Do not run unrelated work in that session. Antigravity settings under
`~/.gemini/antigravity-cli/` are transacted during agy calls. Avoid editing agy permissions during triad calls or running another Antigravity settings change at the same time.

## Notes

- This plugin avoids `danger-full-access`.
- Generated command rules allow only launcher files installed under
  `~/.local/bin` or `TRIAD_BOOTSTRAP_BIN_DIR`; those launchers call the installed
  plugin cache.
- Repair-agent permissions are declared TOML grants, not a proof that a broader
  parent session or managed runtime override cannot allow more.
- Detailed design and evidence live under `docs/`.
