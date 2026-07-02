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
- Repair agents: not run from the plugin cache. The retained-evidence supported
  path is personal-scope installation.
- Fallback: `scripts/bootstrap.sh --check` copies `agents/*.toml` into
  `$CODEX_HOME/agents/`, or `~/.codex/agents/` when `CODEX_HOME` is unset, the
  personal scope already verified spawnable. See
  `docs/references/spike-d-plugin-agent-distribution-decision.md`.

## Install

Install assumes the three required CLIs are already installed and OAuth logged
in: `codex`, `claude`, and `agy`. This installer does not perform OAuth/login
setup. Business-tier `gemini` is optional unless the team enables
`TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1`.

For a local clone:

```bash
cd /path/to/triad-codex-dispatch
codex plugin marketplace add .
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
codex --profile triad-codex-dispatch --search
```

For an internal Git marketplace, keep a local checkout for bootstrap and replace
the source with the owner-approved internal source:

```bash
git clone <internal-git-url> triad-codex-dispatch
cd triad-codex-dispatch
git fetch --tags origin <release-ref>
git checkout --detach FETCH_HEAD
codex plugin marketplace add <internal-git-url-or-owner/repo> --ref <release-ref>
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
codex --profile triad-codex-dispatch --search
```

Install target:

- **User-home install is the default and recommended path.** Leave `CODEX_HOME`
  unset. Bootstrap writes repair agents, profile, and rules under `~/.codex/`;
  classifier patches under `~/.config/triad-codex-dispatch/`; and launchers
  under `~/.local/bin` unless `TRIAD_BOOTSTRAP_BIN_DIR` is set.
- **Workspace-contained install is advanced only.** Use it only if the team
  already manages a logged-in folder-scoped `CODEX_HOME`. Set `CODEX_HOME`,
  `XDG_CONFIG_HOME`, `TRIAD_BOOTSTRAP_BIN_DIR`, and `PATH` consistently before
  `codex plugin marketplace add`, `codex plugin add`, bootstrap, and every later
  `codex --profile triad-codex-dispatch` session. `.triad-codex-home/`,
  `.triad-config/`, and `.triad-bin/` are ignored local runtime folders.

The plugin install uses the marketplace snapshot. Bootstrap still reads
`scripts/`, `bin/`, and `agents/` from the local checkout. Keep that checkout
detached at the fetched `<release-ref>` snapshot before running bootstrap. Keep
that checkout in place after install: the wrapper launchers execute `bin/*.py`
from this absolute checkout path.
Use `main` as `<release-ref>` after this branch is merged; use
`distribution-layer` when validating the current branch directly.

Bootstrap probes the required auth states unless `TRIAD_BOOTSTRAP_SKIP_AUTH=1`
is set for CI or scheduled updater jobs.

Linux/WSL2 prerequisites: OpenAI Codex sandbox docs
(`https://developers.openai.com/codex/concepts/sandboxing`) say to install
`bubblewrap` (`bwrap`) on Linux and WSL2 for reliable local sandboxing. On
Ubuntu 20.04, install/provide `bubblewrap`, `git`, and `jq`; make sure
`python3 --version` is `python3 >= 3.12` before bootstrap because the stock
Ubuntu 20.04 Python is older. Ubuntu 20.04 usually starts users in bash, so the
shell setup below writes `~/.bashrc` by default and switches to `~/.zshrc` only
for zsh users. Ensure `~/.local/bin` is on `PATH`, or set
`TRIAD_BOOTSTRAP_BIN_DIR` to a launcher directory that is already on `PATH`.
Bootstrap does not install OS packages; fleet setup must provide the host
packages before users start Codex.

The install command above is the deployment/default heavy-user posture: matching
triad wrapper commands always run outside the sandbox without another prompt.
That is implemented by the generated Codex profile plus user-layer
`prefix_rule` allowlist, not by `danger-full-access`.

For original-toolkit-style day-to-day UX, make the triad profile the command the
user actually starts. Otherwise a plain `codex` session may not use the generated
`approval_policy = "never"` profile and will keep prompting. Add one of these
shell functions during initial setup. The function pins the wrapper trusted root
to the directory where the user starts Codex:

```bash
TRIAD_SHELL_RC="${HOME}/.bashrc"
case "${SHELL:-}" in
  */zsh) TRIAD_SHELL_RC="${HOME}/.zshrc" ;;
esac
cat >> "$TRIAD_SHELL_RC" <<'EOF'
# Recommended: explicit triad entrypoint.
codex-triad() {
  TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}" \
    command codex --profile triad-codex-dispatch --search "$@"
}

# Optional for dedicated triad machines: make plain `codex` use the triad profile.
# codex() {
#   TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}" \
#     command codex --profile triad-codex-dispatch --search "$@"
# }
EOF
. "$TRIAD_SHELL_RC"
codex-triad
```

Use the plain `codex` function only on machines where the heavy-user external-CLI
posture is the desired default. Existing Codex sessions must be restarted after
profile or rules changes.
The snippet sources the chosen RC file for the current terminal. On stock
Ubuntu, login shells normally source `~/.bashrc` through `~/.profile`; on
minimal or custom images, add the same source line to the login shell startup
file if a new terminal does not expose `codex-triad`.

Open a new Codex thread after installation so plugin skills load from the plugin
cache. Trust the workspace only when developing from this repo or relying on
repo-local `.agents/skills/`; project-local skills are trust-gated.

## Pre-Release Gate

Before publishing a release ref or pushing `main`, run the full local gate from
the checkout that will be distributed:

```bash
bash <<'TRIAD_RELEASE_GATE'
set -euo pipefail

release_base="${RELEASE_BASE:-origin/main}"
tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/triad-codex-dispatch-release-check.XXXXXX")"
trap 'rm -rf "$tmp_root"' EXIT
tmp_root="$(cd "$tmp_root" && pwd -P)"
mkdir -p "$tmp_root/bin"

case "$release_base" in
  origin/*) git fetch --prune origin ;;
esac

if ! git rev-parse --verify -q "$release_base^{commit}" >/dev/null; then
  printf '%s\n' "release base not found: $release_base; run git fetch or set RELEASE_BASE" >&2
  exit 1
fi

git diff --check
git diff --cached --check
git diff --check "$release_base"...HEAD
git status --short > "$tmp_root/git-status.txt"
if test -s "$tmp_root/git-status.txt"; then
  cat "$tmp_root/git-status.txt" >&2
  printf '%s\n' "release gate requires a clean worktree, including untracked files" >&2
  exit 1
fi

python3 -m pytest -q tests/ -p no:cacheprovider
bash -n scripts/bootstrap.sh
TRIAD_BOOTSTRAP_SKIP_AUTH=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
TRIAD_BOOTSTRAP_BIN_DIR="$tmp_root/bin" \
CODEX_HOME="$tmp_root/codex" \
HOME="$tmp_root/home" \
XDG_CONFIG_HOME="$tmp_root/config" \
PATH="$tmp_root/bin:$PATH" \
scripts/bootstrap.sh --check
TRIAD_RELEASE_GATE
```

Then run `triad-cross-family-review` on the exact diff or release candidate.
Refresh your chosen base first, for example with `git fetch --prune origin`, or
set `RELEASE_BASE` when the release branch should be compared against a base
other than `origin/main`.
Do not push the release until the independent reviewers are unanimous:
`Claude SAFE`, `agy SAFE`, and `fresh Codex SAFE`. If any reviewer returns a
blocking question, update the implementation or docs, rerun the gate above, and
rerun the 3-way review.

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

The user-home writes this distribution layer may need are bootstrap targets:

- `$CODEX_HOME/agents/`, or `~/.codex/agents/` when `CODEX_HOME` is unset, for
  personal-scope repair agents.
- `~/.config/triad-codex-dispatch/` for classifier patches.
- `~/.local/bin/` for wrapper launchers, unless
  `TRIAD_BOOTSTRAP_BIN_DIR` points somewhere else on `PATH`.

Default recommendation: leave those outside the sandbox and approve
`scripts/bootstrap.sh --check` when it requests the personal-scope write. This
keeps network access approval-based:

```toml
# ~/.codex/config.toml
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = false
```

If a team wants bootstrap to run unattended, add only those exact writable roots:

```toml
# ~/.codex/triad-codex-dispatch-install.config.toml
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
writable_roots = [
  "/absolute/home/path/.codex/agents",
  "/absolute/home/path/.config/triad-codex-dispatch",
  "/absolute/home/path/.local/bin",
]
network_access = false
```

Use absolute paths in manual TOML; do not rely on shell expansion inside TOML.
Replace `/absolute/home/path` with the value of `printf '%s\n' "$HOME"`, or use
the absolute `CODEX_HOME` path when the team sets `CODEX_HOME`.

Run bootstrap with `codex --profile triad-codex-dispatch-install --search` or
approve `scripts/bootstrap.sh --check` once from a normal session. Do not keep
`~/.local/bin` writable in the day-to-day runtime profile; it is only needed
while installing or refreshing launcher scripts.

If the team intentionally wants fewer prompts for vendor CLI calls, use a
separate trusted-workspace convenience profile and make the egress tradeoff
explicit:

For deployment to heavy triad users, generate the no-prompt wrapper setup:

```bash
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

That writes `$CODEX_HOME/triad-codex-dispatch.config.toml`, or
`~/.codex/triad-codex-dispatch.config.toml` when `CODEX_HOME` is unset. It
refreshes only a bootstrap-managed profile and fails with
`refusing to overwrite unmanaged Codex profile` if that file already exists
without the triad marker. It also writes
`$CODEX_HOME/rules/triad-codex-dispatch.rules`, or
`~/.codex/rules/triad-codex-dispatch.rules` when `CODEX_HOME` is unset, with the
user's actual launcher and checkout paths.

This profile is the explicit external-CLI consent boundary for heavy triad
users. Starting Codex with it means normal dispatch may send relevant prompts,
repo snippets, review packets, and failure logs to the already-authenticated
`claude`, `agy`, and optional `gemini` CLIs. With
`--sandbox workspace-write`, the selected external CLI may also edit/write
inside the wrapper's trusted runtime root. Wrappers reject `--cwd` and
`--prompt-file` outside that root unless the user predeclares another trusted
root with `TRIAD_WRAPPER_ALLOWED_ROOTS`. With
`TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never` plus the generated rules, matching
wrapper commands always run outside the sandbox without another approval prompt.
This is the packaged deployment path.

To get the same day-to-day UX as the source toolkit, start Codex through the
profile every time. The recommended shell setup is:

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
# Optional on dedicated triad machines:
# codex() {
#   TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}" \
#     command codex --profile triad-codex-dispatch --search "$@"
# }
EOF
. "$TRIAD_SHELL_RC"
```

Then use `codex-triad` for triad work, or enable the optional plain `codex` function
when this posture should be the machine default.

For a conservative install that keeps per-call approval prompts, omit the
approval override:

```bash
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
scripts/bootstrap.sh --check
```

The no-prompt deployment path still does not use `danger-full-access`.

The manual equivalent is:

```toml
# ~/.codex/triad-codex-dispatch.config.toml
# Explicit external-CLI consent profile for heavy triad users.
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
writable_roots = [
  "/absolute/home/path/.config/triad-codex-dispatch",
  "/path/to/triad-codex-dispatch/bin/_logs",
]
network_access = true
```

Use absolute paths in manual TOML; do not rely on shell expansion inside TOML.
Replace `/absolute/home/path` with the value of `printf '%s\n' "$HOME"`, and
replace `/path/to/triad-codex-dispatch` with the local checkout used by
bootstrap launchers.

Start that profile with:

```bash
codex --profile triad-codex-dispatch --search
```

If the profile is already installed and only the no-prompt rules need refresh,
run:

```bash
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
scripts/bootstrap.sh --check
```

Bootstrap refreshes only a bootstrap-managed rules file and refuses to overwrite
an unmanaged file.

For manual review or custom fleet packaging, copy the template after replacing
the placeholder paths:

```bash
mkdir -p ~/.codex/rules
cp migration/triad-codex-dispatch.rules ~/.codex/rules/triad-codex-dispatch.rules
# Expected: matchedRules contains triad-codex-dispatch allow rule.
codex execpolicy check --pretty --rules ~/.codex/rules/triad-codex-dispatch.rules -- /path/to/launcher-dir/claude_wrapper.py --prompt hi --sandbox read-only
codex execpolicy check --pretty --rules ~/.codex/rules/triad-codex-dispatch.rules -- /path/to/launcher-dir/claude_wrapper.py --prompt-file /path/to/workspace/_runs/prompts/triad-prompt.txt --sandbox read-only
# Expected: matchedRules is empty.
codex execpolicy check --pretty --rules ~/.codex/rules/triad-codex-dispatch.rules -- claude_wrapper.py --prompt hi --sandbox read-only
codex execpolicy check --pretty --rules ~/.codex/rules/triad-codex-dispatch.rules -- /path/to/triad-codex-dispatch/bin/claude_wrapper.py --prompt hi --sandbox read-only
codex execpolicy check --pretty --rules ~/.codex/rules/triad-codex-dispatch.rules -- python3 /path/to/triad-codex-dispatch/bin/gemini_wrapper.py --prompt hi --sandbox read-only
```

Restart Codex after changing rules. The generated rules allow wrapper-specific
prefixes only: absolute bootstrap launcher paths. Do not allow bare wrapper
names, checkout `bin/*.py` paths, `python3 <wrapper>`, `/usr/bin/env python3`,
or broad shell entrypoints such as `bash -lc` or `zsh -lc`: Codex rules match
argv prefixes, and shell redirection/command substitution/env/wildcards prevent
safe command splitting. Use literal absolute-wrapper commands for the no-prompt
path.
For long prompts, write an absolute prompt file under the active workspace, for
example `$PWD/_runs/prompts/<id>.txt`, and pass
`--prompt-file /absolute/path/to/prompt.txt`; do not use heredoc command
substitution in the wrapper command. Wrappers reject `--prompt-file` and `--cwd`
outside `TRIAD_WRAPPER_ALLOWED_ROOTS`. The `codex-triad` shell function sets
that root to the directory where Codex was started; set
`TRIAD_WRAPPER_ALLOWED_ROOTS` before starting Codex only when additional trusted
workspace roots are required.
Structured-output `--pydantic module:Class` remains available, but wrappers
reject it unless `TRIAD_ALLOW_PYDANTIC_IMPORT=1` is set because loading the class
imports Python code outside the Codex sandbox.

Codex documents `--profile profile-name` as loading
`~/.codex/profile-name.config.toml` and the installed CLI help describes the
same `$CODEX_HOME/<name>.config.toml` layering behavior. Keep profile file keys
top-level, not under `[profiles.<name>]`.

`network_access = true` enables outbound network for commands in that Codex
session; it is not a domain allowlist scoped only to Codex, Claude, agy, or
Gemini. Use managed network policy or approval prompts if the fleet needs
domain-scoped egress.

Rules only decide whether matching commands may run outside the sandbox without
a prompt. They do not override enterprise managed requirements, tenant guardian
policy, or data-export denials. If a managed policy forbids sending private
workspace material to external CLIs, local rules cannot bypass it.

### Provider Sandbox Differences

The provider sandboxes are not interchangeable. Codex uses the generated
`workspace-write` profile plus launcher-only `prefix_rule`s for no-prompt
dispatch. Claude read-only dispatch maps to `--permission-mode dontAsk` with
`Read,Glob,Grep` and optional `WebSearch,WebFetch`. Antigravity uses a
settings transaction plus `agy --sandbox`. Gemini business-tier dispatch uses
the Gemini Policy Engine file for read-only mode, rejects read-only
`auto_edit`, and requires a company business-tier write-attempt verification
before relying on Gemini read-only enforcement. Individual Gemini CLI users
should use agy.

Do not keep install/update targets such as `$CODEX_HOME/agents` (default
`~/.codex/agents`) or `~/.local/bin` writable in the day-to-day runtime profile.
Repair-agent TOMLs and wrapper launchers are installed by bootstrap/update, then
only read during normal dispatch.

Replace `/path/to/triad-codex-dispatch` with the local checkout used by bootstrap
launchers. Keep only that `bin/_logs` runtime artifact directory writable, not
the whole checkout. Bootstrap also installs each repair-agent TOML with a Codex
permission profile named `triad_repair` (`default_permissions = "triad_repair"`):
the agent can read the toolkit checkout, write only
`~/.config/triad-codex-dispatch` and the checkout's `bin/_logs`, and use network
for the repair verification call. It does not receive write access to the
caller's source tree. Bootstrap injects absolute filesystem grants for the
toolkit checkout, classifier directory, Python runtime, and resolved vendor CLI
executable directories; the repair profile does not use `:workspace_roots`. The
repo keeps named-agent spawnability evidence separate from official Codex
permission-profile evidence in
`docs/references/spike-d-plugin-agent-distribution-decision.md` and
`docs/references/codex-permission-profile-evidence.md`.
Repair verification strips the original wrapper `--cwd` and runs from the
toolkit checkout; it verifies classifier routing without granting write or read
access to the caller's source tree.
If `TRIAD_CLASSIFIER_EXTENSION` should point somewhere else, set it before
running bootstrap and re-run `scripts/bootstrap.sh --check`; the repair-agent
permissions are pinned at bootstrap install time.

## Update

Local clone:

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

Internal Git marketplace:

```bash
cd /path/to/triad-codex-dispatch
git fetch --tags origin <release-ref>
git checkout --detach FETCH_HEAD
codex plugin marketplace remove triad-codex-dispatch-local
codex plugin marketplace add <internal-git-url-or-owner/repo> --ref <release-ref>
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

`codex plugin marketplace upgrade` refreshes the configured source; it does not
change an existing pinned `--ref`. Re-add the marketplace source when changing
`<release-ref>`. Even for an unchanged moving branch ref, the `git fetch ...
<release-ref>` plus detached `FETCH_HEAD` step above is what advances the local
bootstrap checkout before bootstrap runs.

Start a new Codex thread after reinstalling so plugin skills are reloaded.

## Remove

Remove the installed plugin and marketplace source:

```bash
codex plugin remove triad-codex-dispatch@triad-codex-dispatch-local
codex plugin marketplace remove triad-codex-dispatch-local
```

Optional cleanup for bootstrap-installed files:

```bash
rm -f ~/.codex/agents/claude-wrapper-repair.toml
rm -f ~/.codex/agents/gemini-wrapper-repair.toml
rm -f ~/.codex/agents/agy-wrapper-repair.toml
rm -f ~/.local/bin/claude_wrapper.py
rm -f ~/.local/bin/gemini_wrapper.py
rm -f ~/.local/bin/antigravity_wrapper.py
```

If bootstrap used `TRIAD_BOOTSTRAP_BIN_DIR`, remove launchers from that
directory instead of `~/.local/bin`. Only delete the classifier directory if the
team intentionally wants to discard learned local routing:

```bash
rm -rf ~/.config/triad-codex-dispatch
```

Runtime logs are local artifacts. Remove `bin/_logs/` from a source checkout or
installed plugin cache only after no dispatch is running.

## What Bootstrap Checks

`scripts/bootstrap.sh --check` verifies or installs toolkit-managed items only.
Bootstrap does not install OS packages; on Ubuntu 20.04 or WSL2 hosts, fleet
setup must provide the Codex Linux/WSL2 sandbox prerequisite `bubblewrap` /
`bwrap` before users start Codex.

- Required binaries: `codex`, `claude`, `agy`, `python3 >= 3.12`, and `jq`.
- Optional binary: `gemini`, unless `TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1`.
- Auth probes for Codex, Claude, and agy. Gemini auth is optional unless
  `TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1`. Set `TRIAD_BOOTSTRAP_SKIP_AUTH=1` only
  for hermetic CI tests or scheduled updater jobs.
- Wrapper launchers for `claude_wrapper.py`, `gemini_wrapper.py`, and
  `antigravity_wrapper.py` when the wrapper commands do not resolve to this
  checkout. Launchers are small executable scripts, not symlinks; bootstrap
  rewrites them on update and fails if an older PATH entry shadows them.
- Writable classifier extension JSON at
  `~/.config/triad-codex-dispatch/classifier-patches.json`, or
  `TRIAD_CLASSIFIER_EXTENSION` if set.
- Personal-scope repair agents under `$CODEX_HOME/agents/`, or
  `~/.codex/agents/` when `CODEX_HOME` is unset.

If `~/.local/bin` is not on `PATH`, either add it before running bootstrap or set
`TRIAD_BOOTSTRAP_BIN_DIR` to a directory already on `PATH`.

## Runtime Artifacts And Cleanup

Runtime telemetry lives under `bin/_logs/<cli>/` for each wrapper family:

- `audit.jsonl` rotates after the active file exceeds 10 MB and keeps at most
  five archives / 50 MB per CLI.
- Failure IPC run logs live in `bin/_logs/<cli>/runs/*.json`. Names include UTC
  timestamp, process id, and an 8-character random UUID suffix for parallel
  uniqueness.
- The dispatch skills delete the run log and matching `.repair.json` after the
  repair agent returns.
- Wrapper failsafes cap run logs at 100 files / 20 MB per CLI and sweep stale
  run logs plus `.repair.json` files older than 7200 seconds on the next normal
  dispatch.

Repair agents that patch
`~/.config/triad-codex-dispatch/classifier-patches.json` are instructed to use
an advisory lock file next to the classifier JSON, so concurrent repairs do not
silently overwrite each other.

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

Illustrative managed requirements shape, not a copy-paste final policy until an
admin verifies the current Codex fleet-management keys:

```toml
features.plugins = true
features.plugin_sharing = false

[plugins.sources.triad-codex-dispatch-local]
source = "<internal-git-url>"
ref = "<release-ref>"
```

Validate the exact managed config keys against the fleet's current Codex admin
policy before rollout.

## Owner Decisions Still Open

- Marketplace source: internal Git URL vs local-clone distribution.
- Classifier path policy: keep isolated `triad-codex-dispatch` path and import
  older `triad-dispatch` patches, or share the old path.

## Resolved Leader-Inversion Decisions

- No `codex_wrapper.py` dispatch leg is shipped for same-family Codex work.
  Codex is the leader in this distribution; cross-family review gets a fresh
  Codex perspective through `spawn_agent(fork_context=false)`.
