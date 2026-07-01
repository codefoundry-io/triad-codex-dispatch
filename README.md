# triad-codex-dispatch

**Status: WIP / distribution layer added.** A **Codex-led** mirror of the Claude-Code-led
[`triad-dispatch`](../triad-dispatch) toolkit, for internal company
distribution — for teams who want **Codex** as the orchestrator instead of
Claude Code.

Codex is the leader; it dispatches **claude** (new `claude -p` single-shot leg),
**gemini**, and **antigravity (agy)** as single-shot workers, with
classification-aware routing, a self-improving classifier, Codex-native repair
subagents, and a cross-family pre-merge review.

## Where things are

- **Design spec:** [docs/specs/2026-07-01-codex-led-triad-dispatch-design.md](docs/specs/2026-07-01-codex-led-triad-dispatch-design.md)
- **References** (`docs/references/`):
  - `codex-draft-plan.md` — Codex's own xhigh + web-search draft plan (read the source repo, verified constraints).
  - `claude-leg-spec.md` — the `claude -p` single-shot leg spec (wrapper-oriented).
  - `claude-headless-reference.md` — full `claude -p` headless reference (682 lines).
  - `spike-evidence-*` — proof that Codex named-subagent repair works (see the design spec §Repair).

## Distribution

- Codex plugin manifest: `.codex-plugin/plugin.json`
- Repo marketplace: `.agents/plugins/marketplace.json`
- Plugin skill package mirror: `skills/`
- Bootstrap checks and repair-agent fallback install:
  `scripts/bootstrap.sh --check`
- Company migration docs: `migration/COMPANY-SETUP.md` and
  `migration/COMPANY-SETUP.ko.md`

Spike D result: plugin-shipped skills install correctly, but plugin-shipped
repair agents are not spawnable by name. Bootstrap copies `agents/*.toml` into
`~/.codex/agents/`, the verified personal-scope named-agent path.

## Install / Update / Remove

### Install

Local clone:

```bash
cd /path/to/triad-codex-dispatch
codex plugin marketplace add .
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

Internal Git marketplace:

```bash
codex plugin marketplace add <internal-git-url-or-owner/repo> --ref main
codex plugin marketplace upgrade triad-codex-dispatch-local
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

Start a new Codex thread after install. Trust the workspace when Codex asks so
repo-local `.agents/skills/` can load.

### Update

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin marketplace upgrade triad-codex-dispatch-local
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

Start a new Codex thread after updating so Codex loads the refreshed plugin
skills.

### Remove

Remove the installed plugin and marketplace source:

```bash
codex plugin remove triad-codex-dispatch@triad-codex-dispatch-local
codex plugin marketplace remove triad-codex-dispatch-local
```

Optional cleanup for files installed by bootstrap:

```bash
rm -f ~/.codex/agents/claude-wrapper-repair.toml
rm -f ~/.codex/agents/gemini-wrapper-repair.toml
rm -f ~/.codex/agents/agy-wrapper-repair.toml
```

Only remove classifier patches if you intentionally want to discard learned
local routing:

```bash
rm -rf ~/.config/triad-codex-dispatch
```

If you enabled the launchd updater from the automatic update section:

```bash
launchctl bootout gui/$(id -u)/com.company.triad-codex-dispatch-update
rm -f ~/Library/LaunchAgents/com.company.triad-codex-dispatch-update.plist
```

## 설치 / 업데이트 / 삭제

### 설치

로컬 clone 기준:

```bash
cd /path/to/triad-codex-dispatch
codex plugin marketplace add .
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

사내 Git marketplace 기준:

```bash
codex plugin marketplace add <internal-git-url-or-owner/repo> --ref main
codex plugin marketplace upgrade triad-codex-dispatch-local
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

설치 후 새 Codex thread를 시작한다. Codex가 workspace trust를 물으면 trust해야
repo-local `.agents/skills/`가 로드된다.

### 업데이트

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin marketplace upgrade triad-codex-dispatch-local
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

업데이트 후 새 Codex thread를 시작해야 갱신된 plugin skill이 로드된다.

### 삭제

설치된 plugin과 marketplace source를 제거한다.

```bash
codex plugin remove triad-codex-dispatch@triad-codex-dispatch-local
codex plugin marketplace remove triad-codex-dispatch-local
```

bootstrap이 설치한 repair agent 파일은 선택적으로 지운다.

```bash
rm -f ~/.codex/agents/claude-wrapper-repair.toml
rm -f ~/.codex/agents/gemini-wrapper-repair.toml
rm -f ~/.codex/agents/agy-wrapper-repair.toml
```

classifier patch는 로컬에서 학습된 routing 정보다. 버리려는 게 확실할 때만 지운다.

```bash
rm -rf ~/.config/triad-codex-dispatch
```

자동 업데이트용 launchd를 등록했다면 같이 내린다.

```bash
launchctl bootout gui/$(id -u)/com.company.triad-codex-dispatch-update
rm -f ~/Library/LaunchAgents/com.company.triad-codex-dispatch-update.plist
```

## Comfortable Codex Settings

OpenAI's Codex docs separate **sandbox boundaries** from **approval policy**:
skills do not bypass the sandbox, and commands launched because of a skill still
run inside the active Codex sandbox. For people who intentionally install this
plugin, use a dedicated profile so normal triad dispatch does not ask for the
same approvals every time.

Create `~/.codex/triad-dispatch.config.toml`:

```toml
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
writable_roots = [
  "/Users/YOUR_USER/.codex/agents",
  "/Users/YOUR_USER/.config/triad-codex-dispatch",
]
```

Replace `YOUR_USER` with your macOS username. Then start Codex with the profile:

```bash
codex --profile triad-dispatch --search
```

This keeps Codex inside `workspace-write`, but avoids repeated prompts for the
normal toolkit path:

- vendor CLI network calls from `claude`, `agy`, and business-tier `gemini`;
- repair-agent installation under `~/.codex/agents/`;
- classifier patches under `~/.config/triad-codex-dispatch/`.

Do not use `sandbox_mode = "danger-full-access"` for this plugin. If a command
needs anything outside the workspace and the two roots above, Codex should still
ask.

## Automatic Updates

Codex documents `codex plugin marketplace upgrade` as the supported way to
refresh configured marketplace snapshots. It does not document a built-in
background auto-update switch for local/team plugins, so automate updates with
your OS scheduler.

For a local clone, use this command:

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin marketplace upgrade triad-codex-dispatch-local
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
TRIAD_BOOTSTRAP_SKIP_AUTH=1 scripts/bootstrap.sh --check
```

For macOS launchd, create
`~/Library/LaunchAgents/com.company.triad-codex-dispatch-update.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.company.triad-codex-dispatch-update</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>-lc</string>
    <string>cd /path/to/triad-codex-dispatch &amp;&amp; git pull --ff-only &amp;&amp; codex plugin marketplace upgrade triad-codex-dispatch-local &amp;&amp; codex plugin add triad-codex-dispatch@triad-codex-dispatch-local &amp;&amp; TRIAD_BOOTSTRAP_SKIP_AUTH=1 scripts/bootstrap.sh --check</string>
  </array>
  <key>StartInterval</key>
  <integer>86400</integer>
  <key>StandardOutPath</key>
  <string>/tmp/triad-codex-dispatch-update.out</string>
  <key>StandardErrorPath</key>
  <string>/tmp/triad-codex-dispatch-update.err</string>
</dict>
</plist>
```

Load it:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.company.triad-codex-dispatch-update.plist
launchctl enable gui/$(id -u)/com.company.triad-codex-dispatch-update
```

After an update, start a new Codex thread so installed plugin skills are loaded
from the refreshed plugin cache. Keep `TRIAD_BOOTSTRAP_SKIP_AUTH=1` for the
scheduled job so it does not spend vendor calls; run `scripts/bootstrap.sh
--check` manually when you want to re-check auth.
