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

Use the public repository clone as the stable checkout. Keep it after install;
the generated launchers call wrapper files from this checkout.

```bash
git clone https://github.com/codefoundry-io/triad-codex-dispatch.git
cd triad-codex-dispatch

codex plugin marketplace add .
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local

TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

Then start a new Codex session:

```bash
codex --profile triad-codex-dispatch --search
```

Important install behavior:

- Default install target is your user home. Leave `CODEX_HOME` unset unless you
  intentionally manage a separate Codex home.
- Bootstrap writes repair agents, profile, and command rules under `~/.codex/`.
- Bootstrap writes classifier patches under `~/.config/triad-codex-dispatch/`.
- Bootstrap writes wrapper launchers under `~/.local/bin` unless
  `TRIAD_BOOTSTRAP_BIN_DIR` is set.
- Existing Codex sessions may not see newly installed plugin skills or custom
  agents. Start a new session after install or update.

## Recommended Shell Entry

Add a command that always starts Codex with the triad profile from the current
workspace:

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

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local

TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

Start a new Codex session after updating.

## Remove

Default user-home removal:

```bash
codex plugin remove triad-codex-dispatch@triad-codex-dispatch-local
codex plugin marketplace remove triad-codex-dispatch-local

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

## Custom Subagents

The shipped repair agents are repair-only and must not recursively dispatch.
Do not add triad dispatch skills to those repair agents.

If you create your own Codex custom subagent that should call triad dispatch
skills, opt in explicitly with Codex `skills.config`:

```toml
[[skills.config]]
path = "/path/to/triad-codex-dispatch/skills/triad-claude-dispatch/SKILL.md"
enabled = true

[[skills.config]]
path = "/path/to/triad-codex-dispatch/skills/triad-antigravity-dispatch/SKILL.md"
enabled = true

[[skills.config]]
path = "/path/to/triad-codex-dispatch/skills/triad-gemini-dispatch/SKILL.md"
enabled = true

[[skills.config]]
path = "/path/to/triad-codex-dispatch/skills/triad-cross-family-review/SKILL.md"
enabled = true
```

After editing custom-agent TOML files, start a new Codex session.

## Notes

- This plugin avoids `danger-full-access`.
- Generated command rules allow only this checkout's wrapper launchers.
- Repair-agent permissions are declared TOML grants, not a proof that a broader
  parent session or managed runtime override cannot allow more.
- Detailed design and evidence live under `docs/`.
