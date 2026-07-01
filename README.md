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

Internal Git marketplace with a local checkout for bootstrap:

```bash
git clone <internal-git-url> triad-codex-dispatch
cd triad-codex-dispatch
codex plugin marketplace add <internal-git-url-or-owner/repo> --ref main
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

The plugin install uses the marketplace snapshot; bootstrap still needs a local
checkout because it reads this repo's `scripts/`, `bin/`, and `agents/`.

Start a new Codex thread after install so plugin skills load from the refreshed
plugin cache. Trust the workspace only when developing from this repo or relying
on repo-local `.agents/skills/`; project-local skills are trust-gated.

### Update

Local clone:

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

Internal Git marketplace:

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
rm -f ~/.local/bin/claude_wrapper.py
rm -f ~/.local/bin/gemini_wrapper.py
rm -f ~/.local/bin/antigravity_wrapper.py
```

If bootstrap used `TRIAD_BOOTSTRAP_BIN_DIR`, remove launcher files from that
directory instead of `~/.local/bin`.

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

bootstrap용 local checkout을 함께 두는 사내 Git marketplace 기준:

```bash
git clone <internal-git-url> triad-codex-dispatch
cd triad-codex-dispatch
codex plugin marketplace add <internal-git-url-or-owner/repo> --ref main
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

plugin 설치는 marketplace snapshot을 쓰지만, bootstrap은 이 repo의 `scripts/`,
`bin/`, `agents/`를 읽으므로 local checkout이 필요하다.

설치 후 새 Codex thread를 시작해야 plugin cache의 skill이 로드된다. 이 repo에서
개발하거나 repo-local `.agents/skills/`를 직접 쓸 때만 workspace trust가 필요하다.
project-local skill은 trust gate를 통과해야 로드된다.

### 업데이트

로컬 clone 기준:

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

사내 Git marketplace 기준:

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
rm -f ~/.local/bin/claude_wrapper.py
rm -f ~/.local/bin/gemini_wrapper.py
rm -f ~/.local/bin/antigravity_wrapper.py
```

bootstrap에서 `TRIAD_BOOTSTRAP_BIN_DIR`를 지정했다면 `~/.local/bin` 대신 그
디렉터리에서 launcher 파일을 지운다.

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

This profile is a convenience profile for trusted workspaces. In current Codex
configuration, `network_access = true` allows outbound network access for
commands in the session; it is not a domain allowlist scoped only to Claude,
Antigravity, Gemini, or Codex. If your fleet needs stricter egress, keep
`network_access = false` and rely on per-command approval or managed network
policy.

Do not use `sandbox_mode = "danger-full-access"` for this plugin. If a command
needs anything outside the workspace and the two roots above, Codex should still
ask.

## 편한 Codex 설정

OpenAI Codex 문서 기준으로 skill은 sandbox를 우회하지 않는다. skill 때문에
실행되는 command도 현재 Codex session의 sandbox와 approval policy를 그대로
상속한다. 이 plugin을 의도적으로 설치한 사용자가 반복 승인을 줄이고 싶다면 전용
profile을 쓴다.

`~/.codex/triad-dispatch.config.toml`:

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

macOS 사용자 이름으로 `YOUR_USER`를 바꾼 뒤 아래처럼 시작한다.

```bash
codex --profile triad-dispatch --search
```

이 설정은 `workspace-write` 안에 머물면서 bootstrap의 repair-agent 설치,
classifier patch, vendor CLI network 호출 때 반복 승인을 줄인다.
`network_access = true`는 해당 Codex session command의 outbound network를
허용한다는 뜻이지 Codex/Claude/agy/Gemini 도메인만 허용하는 allowlist가 아니다.
더 엄격한 egress가 필요하면 `network_access = false`로 두고 command approval이나
관리형 network policy를 사용한다. 이 plugin 때문에 `danger-full-access`를 쓰지
않는다.

## Automatic Updates

Codex documents `codex plugin marketplace upgrade` as the supported way to
refresh configured marketplace snapshots. It does not document a built-in
background auto-update switch for local/team plugins, so automate updates with
your OS scheduler.

For a local clone, use this command. Local clones update through Git plus
`codex plugin add`; `codex plugin marketplace upgrade` only refreshes configured
Git marketplace snapshots.

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
TRIAD_BOOTSTRAP_SKIP_AUTH=1 scripts/bootstrap.sh --check
```

For an internal Git marketplace source, use:

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin marketplace upgrade triad-codex-dispatch-local
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
TRIAD_BOOTSTRAP_SKIP_AUTH=1 scripts/bootstrap.sh --check
```

For macOS launchd with a local clone, create
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
    <string>cd /path/to/triad-codex-dispatch &amp;&amp; git pull --ff-only &amp;&amp; codex plugin add triad-codex-dispatch@triad-codex-dispatch-local &amp;&amp; TRIAD_BOOTSTRAP_SKIP_AUTH=1 scripts/bootstrap.sh --check</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>
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

## 자동 업데이트

현재 Codex 문서에는 local/team plugin용 background auto-update switch가 없다.
자동 업데이트가 필요하면 OS scheduler로 아래 명령을 주기 실행한다.

로컬 clone:

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
TRIAD_BOOTSTRAP_SKIP_AUTH=1 scripts/bootstrap.sh --check
```

사내 Git marketplace:

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin marketplace upgrade triad-codex-dispatch-local
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
TRIAD_BOOTSTRAP_SKIP_AUTH=1 scripts/bootstrap.sh --check
```

업데이트 후 새 Codex thread를 시작해야 plugin cache에서 갱신된 skill이 로드된다.
예약 job에는 vendor 호출을 아끼기 위해 `TRIAD_BOOTSTRAP_SKIP_AUTH=1`을 두고,
auth 재점검은 필요할 때 수동으로 `scripts/bootstrap.sh --check`를 실행한다.
