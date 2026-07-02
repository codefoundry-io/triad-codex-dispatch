# triad-codex-dispatch

**Status: distribution layer implemented on the review branch.** A
**Codex-led** counterpart to the Claude-Code-led `triad-dispatch` toolkit, for
internal company distribution — for teams who want **Codex** as the orchestrator
instead of Claude Code.

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

Spike D distribution decision: plugin-shipped skills install correctly, but
repair agents are not run from the plugin cache. Bootstrap copies
`agents/*.toml` into `$CODEX_HOME/agents/`, or `~/.codex/agents/` when
`CODEX_HOME` is unset, the retained-evidence verified personal-scope
named-agent path. See
`docs/references/spike-d-plugin-agent-distribution-decision.md`.

## Install / Update / Remove

### Install

Install assumes the three required CLIs are already installed and OAuth logged
in: `codex`, `claude`, and `agy`. This installer does not perform OAuth/login
setup. Business-tier `gemini` is optional unless the team enables
`TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1`.

Local clone:

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

Internal Git marketplace with a local checkout for bootstrap:

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
  unset. Bootstrap writes repair agents, the generated profile, and command
  rules under `~/.codex/`, classifier patches under
  `~/.config/triad-codex-dispatch/`, and launcher scripts in `~/.local/bin`
  unless `TRIAD_BOOTSTRAP_BIN_DIR` is set.
- **Workspace-contained install is advanced only.** Use it only if the team
  already manages a logged-in folder-scoped `CODEX_HOME`. Set `CODEX_HOME`,
  `XDG_CONFIG_HOME`, `TRIAD_BOOTSTRAP_BIN_DIR`, and `PATH` consistently before
  `codex plugin marketplace add`, `codex plugin add`, bootstrap, and every later
  `codex --profile triad-codex-dispatch` session. The repo ignores
  `.triad-codex-home/`, `.triad-config/`, and `.triad-bin/`.

The plugin install uses the marketplace snapshot; bootstrap still needs a local
checkout because it reads this repo's `scripts/`, `bin/`, and `agents/`. Keep
the local checkout detached at the fetched `<release-ref>` snapshot used by the
marketplace source before running bootstrap. Keep that checkout in place after
install: the wrapper launchers execute `bin/*.py` from this absolute checkout
path.
Use `main` as `<release-ref>` after this branch is merged; while validating this
branch directly, use `distribution-layer`.

Bootstrap probes the required auth states unless `TRIAD_BOOTSTRAP_SKIP_AUTH=1`
is set for CI or scheduled updater jobs.
Users must also keep wrapper prompt files and `--cwd` values inside the active
trusted workspace, or explicitly set `TRIAD_WRAPPER_ALLOWED_ROOTS` before
starting Codex for additional trusted roots.

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
shell functions during initial setup. The function pins the wrapper trusted
root to the directory where the user starts Codex:

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

Start a new Codex thread after install so plugin skills load from the refreshed
plugin cache. Trust the workspace only when developing from this repo or relying
on repo-local `.agents/skills/`; project-local skills are trust-gated.

### Update

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

Start a new Codex thread after updating so Codex loads the refreshed plugin
skills.

### Pre-Release Gate

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
directory instead of `~/.local/bin`. If bootstrap used `CODEX_HOME`, remove
repair agents from `$CODEX_HOME/agents` instead of `~/.codex/agents`.

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

설치는 필수 3개 CLI인 `codex`, `claude`, `agy`가 이미 설치되어 있고 OAuth login이
끝난 상태를 전제로 한다. 이 installer는 OAuth/login 설정을 대신하지 않는다.
business-tier `gemini`는 팀이 `TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1`을 켠 경우에만
필수다.

로컬 clone 기준:

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

bootstrap용 local checkout을 함께 두는 사내 Git marketplace 기준:

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

설치 대상:

- **사용자 홈 설치가 기본이자 권장 경로다.** `CODEX_HOME`을 지정하지 않는다.
  bootstrap은 repair agent, 생성 profile, command rules를 `~/.codex/` 아래에 쓰고,
  classifier patch는 `~/.config/triad-codex-dispatch/`에 쓴다. launcher는
  `TRIAD_BOOTSTRAP_BIN_DIR`가 없으면 `~/.local/bin`에 둔다.
- **workspace-contained 설치는 advanced 옵션이다.** 팀이 이미 로그인된
  folder-scoped `CODEX_HOME`을 관리할 때만 쓴다. bootstrap 전과 이후 모든
  `codex --profile triad-codex-dispatch` session 전뿐 아니라 `codex plugin marketplace add`,
  `codex plugin add`, bootstrap 전에도 `CODEX_HOME`, `XDG_CONFIG_HOME`,
  `TRIAD_BOOTSTRAP_BIN_DIR`, `PATH`를 일관되게 설정한다. 이 repo는 `.triad-codex-home/`,
  `.triad-config/`, `.triad-bin/`을 ignore한다.

plugin 설치는 marketplace snapshot을 쓰지만, bootstrap은 이 repo의 `scripts/`,
`bin/`, `agents/`를 읽으므로 local checkout이 필요하다. bootstrap 실행 전
local checkout도 marketplace source와 같은 `<release-ref>` snapshot에 detached
상태로 맞춘다. 설치 후에도 이 checkout을 유지한다. wrapper launcher는 이 absolute
checkout path의 `bin/*.py`를 실행한다.
`<release-ref>`는 merge 후에는 `main`, 이 branch를 직접 검증할 때는
`distribution-layer`로 둔다.

Linux/WSL2 전제: OpenAI Codex sandbox 문서
(`https://developers.openai.com/codex/concepts/sandboxing`)는 Linux와 WSL2에서
안정적인 local sandboxing을 위해 `bubblewrap`(`bwrap`) 설치를 안내한다. Ubuntu
20.04에서는 `bubblewrap`, `git`, `jq`를 설치하거나 제공한다. Ubuntu 20.04 기본
Python은 오래됐으므로 bootstrap 전에 `python3 --version`이 `python3 >= 3.12`인지
확인한다. Ubuntu 20.04는 보통 bash로 시작하므로 아래 shell 설정은 기본으로
`~/.bashrc`에 쓰고, zsh 사용자일 때만 `~/.zshrc`로 전환한다. `~/.local/bin`이
`PATH`에 있어야 하며, 그렇지 않으면 `TRIAD_BOOTSTRAP_BIN_DIR`를 이미 `PATH`에
있는 launcher directory로 지정한다.
Bootstrap은 OS package를 설치하지 않으므로 fleet setup이 사용자가 Codex를
시작하기 전에 host package를 제공해야 한다.

위 설치 명령은 배포용 heavy-user 기본 자세다. 매칭되는 triad wrapper command는
매번 추가 prompt 없이 항상 sandbox 밖에서 실행된다. 이는 생성된 Codex profile과
user-layer `prefix_rule` allowlist로 구현하며, `danger-full-access`를 쓰는 방식이
아니다.

원본 toolkit 같은 day-to-day UX를 원하면 사용자가 실제로 시작하는 Codex command가
항상 triad profile을 쓰게 해야 한다. 그냥 `codex`로 들어오면 생성된
`approval_policy = "never"` profile을 쓰지 않을 수 있고, 그러면 계속 prompt가 뜬다.
초기 설정에서 아래 shell function 중 하나를 추가한다. function은 사용자가 Codex를
시작한 directory를 wrapper trusted root로 고정한다.

```bash
TRIAD_SHELL_RC="${HOME}/.bashrc"
case "${SHELL:-}" in
  */zsh) TRIAD_SHELL_RC="${HOME}/.zshrc" ;;
esac
cat >> "$TRIAD_SHELL_RC" <<'EOF'
# 권장: 명시적인 triad entrypoint.
codex-triad() {
  TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}" \
    command codex --profile triad-codex-dispatch --search "$@"
}

# triad 전용 머신에서는 plain `codex`도 triad profile로 열 수 있다.
# codex() {
#   TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}" \
#     command codex --profile triad-codex-dispatch --search "$@"
# }
EOF
. "$TRIAD_SHELL_RC"
codex-triad
```

plain `codex` function은 heavy-user external-CLI 자세가 그 머신의 기본값이어도 되는
환경에서만 켠다. profile이나 rules를 바꾼 뒤에는 기존 Codex session을 재시작해야
한다.
이 snippet은 현재 terminal에서 바로 쓰도록 선택한 RC 파일을 source한다. stock
Ubuntu에서는 login shell이 보통 `~/.profile`을 통해 `~/.bashrc`를 읽는다. minimal
image나 custom dotfile 환경에서 새 terminal에 `codex-triad`가 보이지 않으면 같은
source line을 login shell startup file에 추가한다.

설치 후 새 Codex thread를 시작해야 plugin cache의 skill이 로드된다. 이 repo에서
개발하거나 repo-local `.agents/skills/`를 직접 쓸 때만 workspace trust가 필요하다.
project-local skill은 trust gate를 통과해야 로드된다.

### 업데이트

로컬 clone 기준:

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

사내 Git marketplace 기준:

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

업데이트 후 새 Codex thread를 시작해야 갱신된 plugin skill이 로드된다.

### 배포 전 Gate

release ref를 공개하거나 `main`에 push하기 전에, 배포할 checkout에서 전체 gate를
실행한다.

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

그 다음 정확한 diff 또는 release candidate에 대해 `triad-cross-family-review`를
돌린다. 먼저 `git fetch --prune origin` 등으로 비교 base를 갱신하거나, release
branch를 `origin/main`이 아닌 다른 base와 비교해야 하면 `RELEASE_BASE`를 지정한다.
`Claude가 SAFE`, `agy가 SAFE`, `fresh Codex가 SAFE`로 만장일치가 되기
전에는 release를 push하지 않는다. blocker 질문이 하나라도 나오면 구현이나 문서를
수정하고 위 gate와 3자 review를 다시 실행한다.

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
디렉터리에서 launcher 파일을 지운다. bootstrap에 `CODEX_HOME`을 지정했다면
repair agent는 `~/.codex/agents`가 아니라 `$CODEX_HOME/agents`에서 지운다.

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

Codex documents `--profile <name>` as layering
`$CODEX_HOME/<name>.config.toml` on top of the base user config; the installed
CLI help says the same. Use top-level config keys in the profile file.

For deployment to heavy triad users, use the no-prompt wrapper setup:

```bash
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

That writes `$CODEX_HOME/triad-codex-dispatch.config.toml` (or
`~/.codex/triad-codex-dispatch.config.toml` when `CODEX_HOME` is unset). It
refreshes only a bootstrap-managed profile and fails with
`refusing to overwrite unmanaged Codex profile` if the file already exists
without the triad marker. It also writes
`$CODEX_HOME/rules/triad-codex-dispatch.rules` (or
`~/.codex/rules/triad-codex-dispatch.rules` when `CODEX_HOME` is unset) with the
user's actual launcher and checkout paths.

This profile is the explicit consent boundary for heavy triad users: starting
Codex with it means normal dispatch may send relevant prompts, repo snippets,
review packets, and failure logs to the already-authenticated `claude`, `agy`,
and optional `gemini` CLIs. `--sandbox workspace-write` dispatch also allows
the selected external CLI to edit/write inside the wrapper's trusted runtime
root; wrappers reject `--cwd` and `--prompt-file` outside that root unless the
user predeclares another root with `TRIAD_WRAPPER_ALLOWED_ROOTS`. With
`TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never` plus the generated rules, matching
wrapper commands always run outside the sandbox without another approval prompt.
This is the packaged deployment path; it still does **not** use
`danger-full-access`.

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

Manual equivalent:

```toml
# Explicit external-CLI consent profile for heavy triad users.
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
writable_roots = [
  "/absolute/home/path/.config/triad-codex-dispatch",
  "/path/to/triad-codex-dispatch/bin/_logs",
]
```

Use absolute paths in manual TOML; do not rely on shell expansion inside TOML.
Replace `/absolute/home/path` with the value of `printf '%s\n' "$HOME"`, and
replace `/path/to/triad-codex-dispatch` with the local checkout used by
bootstrap launchers. Bootstrap creates `bin/_logs` during
`scripts/bootstrap.sh --check`. Then start Codex with the profile:

```bash
codex --profile triad-codex-dispatch --search
```

If you already installed the profile and only need to refresh the no-prompt
rules, run:

```bash
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
scripts/bootstrap.sh --check
```

Bootstrap refreshes only a bootstrap-managed rules file and refuses to overwrite
an unmanaged file.

Users who want to review or install rules manually can copy the template:

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

Replace the placeholder paths before using the template manually. Restart Codex
after changing rules. These rules intentionally allow wrapper-specific prefixes
only: absolute bootstrap launcher paths. They do not allow bare wrapper names,
checkout `bin/*.py` paths, `python3 <wrapper>`, `/usr/bin/env python3`, or broad
shell entrypoints such as `bash -lc` or `zsh -lc`: Codex rules match argv
prefixes, and official docs note that shell redirection, command substitution,
variables, or wildcards prevent safe command splitting. If a command is wrapped as
`zsh -lc "claude_wrapper.py ... > out 2> err"`, the wrapper prefix rule will not
match. Use literal absolute-wrapper commands for the no-prompt path.

Dispatch skills must follow the same shape. For short prompts, pass
`--prompt "Read _runs/.../packet.md and review it"`. For long prompts, write an
absolute prompt file under the active workspace, for example
`$PWD/_runs/prompts/<id>.txt`, and pass `--prompt-file /absolute/path/to/prompt.txt`.
Never use `--prompt "$(cat <<'PROMPT' ...)"`, shell redirection, or shell
substitution in the wrapper command when relying on no-prompt rules.
Structured-output `--pydantic module:Class` remains available, but wrappers
reject it unless `TRIAD_ALLOW_PYDANTIC_IMPORT=1` is set because loading the class
imports Python code outside the Codex sandbox.
Wrappers also reject `--prompt-file` and `--cwd` paths outside
`TRIAD_WRAPPER_ALLOWED_ROOTS`. The `codex-triad` shell function sets that root
to the directory where Codex was started; users can pre-set
`TRIAD_WRAPPER_ALLOWED_ROOTS` to a colon-separated absolute list when they need
additional trusted workspace roots.

### Provider Sandbox Differences

The three external CLIs do not share one sandbox model. This plugin normalizes
the user-facing wrapper flags, but the underlying enforcement is different:

| Layer | What the user must set up | What `--sandbox read-only` means |
|---|---|---|
| Codex leader | Start Codex with `codex --profile triad-codex-dispatch --search` after bootstrap installs the profile and rules. | Codex remains `sandbox_mode = "workspace-write"`. User-layer `prefix_rule`s allow only absolute triad wrapper commands to run outside the Codex sandbox without another approval prompt. |
| Claude leg | Install and authenticate `claude`. Use the absolute wrapper path generated by bootstrap. | The wrapper calls Claude with `--permission-mode dontAsk --allowedTools Read,Glob,Grep`; `--search` adds `WebSearch,WebFetch`. Writes are not allowed in read-only mode. |
| Antigravity / agy leg | Install and authenticate `agy`. Use agy as the default Google-family leg. No `--search` flag is needed or accepted. | The wrapper takes a flock-serialized settings transaction: it adds deny rules to Antigravity settings, runs `agy --sandbox`, then restores settings. `read_url` and `search_web` remain available. |
| Gemini CLI leg | Use only for business, Vertex, or API-key Gemini accounts. Individual Gemini CLI users should use agy. Set `TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1` only when Gemini must be required at install time. | The wrapper does not use Gemini `plan` or `yolo`. `--sandbox read-only` attaches `bin/policies/gemini-readonly.toml` with Gemini's Policy Engine, but the policy file must pass a company business-tier write-attempt verification before relying on Gemini read-only enforcement. `--approval-mode auto_edit` is rejected with read-only. |

For the packaged no-prompt UX, users do these once:

```bash
cd /path/to/triad-codex-dispatch
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check

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

If a team keeps prompt packets outside the checkout, start Codex with an
explicit trusted-root list:

```bash
TRIAD_WRAPPER_ALLOWED_ROOTS="/path/to/workspace:/path/to/triad-review-packets" codex-triad
```

If the team requires Gemini business-tier dispatch during bootstrap, add
`TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1` to the bootstrap command after configuring
Gemini's own business/Vertex/API-key authentication. Otherwise Gemini remains
optional and agy is the default Google-family leg.

This keeps Codex inside `workspace-write`, but avoids repeated prompts for the
normal toolkit path:

- vendor CLI network calls from `claude`, `agy`, and business-tier `gemini`;
- classifier patches under `~/.config/triad-codex-dispatch/`;
- bounded wrapper run logs and repair response files under
  `/path/to/triad-codex-dispatch/bin/_logs`.

Do not keep install/update targets such as `$CODEX_HOME/agents` (default
`~/.codex/agents`) or `~/.local/bin` writable in the normal runtime profile.
Repair-agent TOMLs and wrapper launchers are installed by bootstrap/update;
approve `scripts/bootstrap.sh --check` once, or use a short-lived install-only
profile / `--add-dir` for those directories.
Bootstrap installs repair-agent TOMLs with a Codex permission profile named
`triad_repair` (`default_permissions = "triad_repair"`): it reads the toolkit
checkout, writes only `~/.config/triad-codex-dispatch` and that checkout's
`bin/_logs`, and enables network for the repair verification call. It does not
grant write access to the caller's source tree. Bootstrap injects absolute
filesystem grants for the toolkit checkout, classifier directory, and Python
runtime plus resolved vendor CLI executable directories; the repair profile does
not use `:workspace_roots`. The named-agent spawnability evidence and the
official Codex permission-profile evidence are tracked separately in
`docs/references/spike-d-plugin-agent-distribution-decision.md` and
`docs/references/codex-permission-profile-evidence.md`.
Rules only decide whether matching commands may run outside the sandbox without
a prompt; they do not override enterprise managed requirements, tenant guardian
policy, or data-export denials. If those layers forbid sending private workspace
material to external CLIs, local rules cannot bypass that policy.
Repair verification strips the original wrapper `--cwd` and runs from the
toolkit checkout; it verifies classifier routing without granting write or read
access to the caller's source tree.
If `TRIAD_CLASSIFIER_EXTENSION` should point somewhere else, set it before
running bootstrap and re-run `scripts/bootstrap.sh --check`; the repair-agent
permissions are pinned at bootstrap install time.

This profile is a convenience profile for trusted workspaces. In current Codex
configuration, `network_access = true` allows outbound network access for
commands in the session; it is not a domain allowlist scoped only to Claude,
Antigravity, Gemini, or Codex. If your fleet needs stricter egress, keep
`network_access = false` and rely on per-command approval or managed network
policy.

Do not use `sandbox_mode = "danger-full-access"` for this plugin. If a command
needs anything outside the workspace and the roots above, Codex should still
ask.

## Runtime Artifacts And Cleanup

Wrapper telemetry is bounded and local. Runtime files live under
`bin/_logs/<cli>/` for each wrapper family (`claude`, `gemini`,
`antigravity`):

- `audit.jsonl` is append-only operational telemetry. It rotates when the active
  file exceeds 10 MB and keeps at most five archives / 50 MB per CLI.
- Failure IPC run logs live under `bin/_logs/<cli>/runs/*.json`. File names
  include UTC timestamp, process id, and an 8-char random UUID suffix, so
  parallel dispatches do not collide.
- Normal dispatch cleanup deletes the run log and matching `.repair.json` after
  the repair agent returns.
- Wrapper failsafes cap run logs at 100 files / 20 MB per CLI and sweep stale
  run logs plus `.repair.json` files older than 7200 seconds on the next normal
  dispatch. The age floor protects live parallel repairs.

On uninstall, optionally remove `bin/_logs/` from a source checkout or from an
installed plugin cache only after no dispatch is running.

## 편한 Codex 설정

OpenAI Codex 문서 기준으로 skill은 sandbox를 우회하지 않는다. skill 때문에
실행되는 command도 현재 Codex session의 sandbox와 approval policy를 그대로
상속한다. Codex 문서와 현재 CLI help 모두 `--profile <name>`이
`$CODEX_HOME/<name>.config.toml`을 base user config 위에 layer한다고 설명한다.
profile 파일에는 top-level config key를 둔다. 이 plugin을 의도적으로 설치한
사용자가 반복 승인을 줄이고 싶다면 전용 profile을 쓴다.

배포용 heavy triad user에게는 no-prompt wrapper setup을 쓴다.

```bash
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

이 명령은 `$CODEX_HOME/triad-codex-dispatch.config.toml`을 쓴다(`CODEX_HOME`이
없으면 `~/.codex/triad-codex-dispatch.config.toml`). bootstrap이 만든 marker가
있는 profile만 갱신하며, 사용자가 직접 만든 unmanaged profile이 이미 있으면
`refusing to overwrite unmanaged Codex profile`로 실패하고 덮어쓰지 않는다. 또한
사용자의 실제 launcher/check-out 경로가 들어간
`$CODEX_HOME/rules/triad-codex-dispatch.rules`를 쓴다. `CODEX_HOME`이 없으면
`~/.codex/rules/triad-codex-dispatch.rules`를 쓴다.

이 profile은 heavy triad user의 명시적 동의 경계다. 이 profile로 Codex를 시작한다는
것은 일반 dispatch가 관련 prompt, repo snippet, review packet, failure log를 이미
인증된 `claude`, `agy`, 선택적 `gemini` CLI로 보낼 수 있음을 승인한다는 뜻이다.
`--sandbox workspace-write` dispatch는 선택된 external CLI가 wrapper의 trusted
runtime root 안에서 edit/write를 수행할 수도 있음을 의미한다. wrapper는 `--cwd`와
`--prompt-file`이 이 root 밖이면 거부하며, 추가 root는 Codex 시작 전에
`TRIAD_WRAPPER_ALLOWED_ROOTS`로 명시해야 한다.
`TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never`와 생성된 rules를 같이 쓰면 매칭되는
wrapper command는 추가 approval prompt 없이 항상 sandbox 밖에서 실행된다. 이것이
배포용 기본 경로다. 그래도 `danger-full-access`는 쓰지 않는다.

원본 toolkit과 같은 평소 사용성을 내려면 매번 이 profile로 Codex를 시작해야 한다.
권장 shell 설정은 아래와 같다.

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
# triad 전용 머신에서는 아래를 켜서 plain `codex`도 triad profile로 열 수 있다.
# codex() {
#   TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}" \
#     command codex --profile triad-codex-dispatch --search "$@"
# }
EOF
. "$TRIAD_SHELL_RC"
```

triad 작업에는 `codex-triad`를 쓰고, 이 자세가 머신 기본값이어도 되는 경우에만
optional plain `codex` function을 켠다.

per-call approval prompt를 유지하는 보수적 설치가 필요하면 approval override를 뺀다.

```bash
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
scripts/bootstrap.sh --check
```

수동으로 만들 때의 동등한 내용:

```toml
# Heavy triad user를 위한 external-CLI consent profile.
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
writable_roots = [
  "/absolute/home/path/.config/triad-codex-dispatch",
  "/path/to/triad-codex-dispatch/bin/_logs",
]
```

수동 TOML에는 절대 경로를 쓴다. TOML 안의 shell expansion에 의존하지 않는다.
`/absolute/home/path`는 `printf '%s\n' "$HOME"` 결과로 바꾸고,
`/path/to/triad-codex-dispatch`는 bootstrap launcher가 가리키는 local checkout
경로로 바꾼다. bootstrap이 `scripts/bootstrap.sh --check` 중 `bin/_logs`를
만든다. 그 뒤 아래처럼 시작한다.

```bash
codex --profile triad-codex-dispatch --search
```

profile은 이미 설치했고 no-prompt rules만 갱신해야 하면 아래만 실행한다.

```bash
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
scripts/bootstrap.sh --check
```

bootstrap은 관리 중인 rules 파일만 갱신하며, 사용자가 만든 unmanaged 파일은
덮어쓰지 않는다.

rules를 직접 검토하거나 수동 설치하려면 template을 복사한다.

```bash
mkdir -p ~/.codex/rules
cp migration/triad-codex-dispatch.rules ~/.codex/rules/triad-codex-dispatch.rules
# 예상: matchedRules에 triad-codex-dispatch allow rule이 나온다.
codex execpolicy check --pretty --rules ~/.codex/rules/triad-codex-dispatch.rules -- /path/to/launcher-dir/claude_wrapper.py --prompt hi --sandbox read-only
codex execpolicy check --pretty --rules ~/.codex/rules/triad-codex-dispatch.rules -- /path/to/launcher-dir/claude_wrapper.py --prompt-file /path/to/workspace/_runs/prompts/triad-prompt.txt --sandbox read-only
# 예상: matchedRules가 비어 있다.
codex execpolicy check --pretty --rules ~/.codex/rules/triad-codex-dispatch.rules -- claude_wrapper.py --prompt hi --sandbox read-only
codex execpolicy check --pretty --rules ~/.codex/rules/triad-codex-dispatch.rules -- /path/to/triad-codex-dispatch/bin/claude_wrapper.py --prompt hi --sandbox read-only
codex execpolicy check --pretty --rules ~/.codex/rules/triad-codex-dispatch.rules -- python3 /path/to/triad-codex-dispatch/bin/gemini_wrapper.py --prompt hi --sandbox read-only
```

template을 수동으로 쓸 때는 placeholder path를 먼저 바꾼다. rules 변경 후 Codex를
재시작한다. 이 rules는 wrapper 전용 prefix만 허용한다: absolute bootstrap launcher
path만 허용한다. bare wrapper name, checkout `bin/*.py` path,
`python3 <wrapper>`, `/usr/bin/env python3`, `bash -lc`나 `zsh -lc` 같은 넓은
shell entrypoint는 허용하지 않는다. Codex rules는 argv prefix를 매칭하며, 공식
문서 기준으로 redirection, command substitution, env var, wildcard가 들어간 shell
script는 안전하게 split하지 않는다. 따라서
`zsh -lc "claude_wrapper.py ... > out 2> err"`처럼 감싸면 wrapper prefix rule이
매칭되지 않는다. no-prompt 경로에서는 literal absolute-wrapper command를 사용한다.

dispatch skill도 같은 형태를 따라야 한다. 짧은 prompt는
`--prompt "Read _runs/.../packet.md and review it"`로 넘긴다. 긴 prompt는 active
workspace 아래 absolute prompt file, 예를 들면 `$PWD/_runs/prompts/<id>.txt`에
쓰고 `--prompt-file /absolute/path/to/prompt.txt`로 넘긴다.
no-prompt rules에 의존할 때 wrapper command 안에서
`--prompt "$(cat <<'PROMPT' ...)"`, redirection, shell substitution을 쓰지 않는다.
structured-output `--pydantic module:Class` 기능은 남아 있지만, class 로딩이 Codex
sandbox 밖 Python import가 되므로 `TRIAD_ALLOW_PYDANTIC_IMPORT=1`을 명시한 경우에만
허용한다.
wrapper는 `TRIAD_WRAPPER_ALLOWED_ROOTS` 밖의 `--prompt-file`과 `--cwd`를 거부한다.
`codex-triad` shell function은 Codex를 시작한 directory를 이 root로 설정한다. 추가
trusted workspace root가 필요하면 Codex 시작 전에 colon-separated absolute list로
`TRIAD_WRAPPER_ALLOWED_ROOTS`를 설정한다.

### Provider별 Sandbox 차이

세 external CLI의 sandbox 모델은 서로 다르다. 이 plugin은 wrapper flag를 비슷하게
보이게 만들지만, 실제 enforcement는 provider마다 다르다.

| Layer | 사용자가 해야 할 설정 | `--sandbox read-only`의 실제 의미 |
|---|---|---|
| Codex leader | bootstrap으로 profile/rules를 설치한 뒤 `codex --profile triad-codex-dispatch --search`로 시작한다. | Codex는 `sandbox_mode = "workspace-write"`에 머문다. user-layer `prefix_rule`이 absolute triad wrapper command만 추가 approval prompt 없이 Codex sandbox 밖에서 실행하게 한다. |
| Claude leg | `claude`를 설치하고 인증한다. bootstrap이 만든 absolute wrapper path를 쓴다. | wrapper가 Claude를 `--permission-mode dontAsk --allowedTools Read,Glob,Grep`로 호출한다. `--search`를 주면 `WebSearch,WebFetch`만 추가된다. read-only에서는 write를 허용하지 않는다. |
| Antigravity / agy leg | `agy`를 설치하고 인증한다. Google-family 기본 leg는 agy다. `--search` flag는 필요 없고 넣으면 안 된다. | wrapper가 flock으로 보호된 settings transaction을 수행한다. Antigravity settings에 deny rule을 추가하고 `agy --sandbox`를 실행한 뒤 settings를 복구한다. `read_url`과 `search_web`은 계속 가능하다. |
| Gemini CLI leg | business, Vertex, API-key Gemini account 전용이다. 개인 Gemini CLI 사용자는 agy를 쓴다. 설치 때 Gemini를 필수로 요구하려면 `TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1`을 켠다. | Gemini `plan`/`yolo`를 쓰지 않는다. `--sandbox read-only`는 Gemini Policy Engine의 `bin/policies/gemini-readonly.toml`을 붙이지만, Gemini read-only enforcement를 신뢰하기 전에 회사 business-tier 계정에서 write-attempt 검증을 통과해야 한다. `read-only + --approval-mode auto_edit`는 wrapper가 거부한다. |

배포용 no-prompt UX를 위해 사용자는 아래를 한 번 실행한다.

```bash
cd /path/to/triad-codex-dispatch
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check

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

prompt packet을 checkout 밖에 두는 팀은 trusted root를 명시해서 Codex를 시작한다.

```bash
TRIAD_WRAPPER_ALLOWED_ROOTS="/path/to/workspace:/path/to/triad-review-packets" codex-triad
```

팀이 Gemini business-tier dispatch를 bootstrap 단계에서 필수로 검증해야 하면,
Gemini 자체 business/Vertex/API-key 인증을 끝낸 뒤 bootstrap 명령에
`TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1`을 추가한다. 그렇지 않으면 Gemini는 optional이고
Google-family 기본 leg는 agy다.

이 설정은 `workspace-write` 안에 머물면서 classifier patch, bounded wrapper
run log / `.repair.json`, vendor CLI network 호출 때 반복 승인을 줄인다.
`$CODEX_HOME/agents`(`CODEX_HOME`이 없으면 `~/.codex/agents`)와 `~/.local/bin`은
일반 runtime profile에 계속 writable로 두지 않는다. repair-agent TOML과 wrapper
launcher 설치는 bootstrap/update 작업이므로 `scripts/bootstrap.sh --check`를 1회
승인하거나, 해당 디렉터리에 대한 짧은 install-only profile / `--add-dir`를 사용한다.
bootstrap은 repair-agent TOML에
`triad_repair` Codex permission profile(`default_permissions = "triad_repair"`)을
설치한다. 이 profile은 toolkit checkout을 읽고, `~/.config/triad-codex-dispatch`와
그 checkout의 `bin/_logs`만 쓰며, repair verification call을 위해 network를 켠다.
호출 대상 source tree write 권한은 주지 않는다. bootstrap은 toolkit checkout,
classifier directory, Python runtime에 대한 absolute filesystem grant를 주입하며,
resolved vendor CLI executable directory도 read-only로 주입한다. repair profile은
`:workspace_roots`를 쓰지 않는다. named-agent spawnability 증거와 Codex
permission-profile 공식 문서 근거는
`docs/references/spike-d-plugin-agent-distribution-decision.md`와
`docs/references/codex-permission-profile-evidence.md`에 분리해 기록한다.
rules는 매칭된 command를 sandbox 밖에서 prompt 없이 실행할지 결정할 뿐이다.
enterprise managed requirements, tenant guardian policy, data-export deny를
우회하지 않는다. 그런 상위 정책이 private workspace 내용을 외부 CLI로 보내는 것을
금지하면 local rules로는 해결할 수 없다.
repair verification은 원래 wrapper의 `--cwd`를 제거하고 toolkit checkout에서
실행한다. 호출 대상 source tree read/write 권한 없이 classifier routing만 검증한다.
`TRIAD_CLASSIFIER_EXTENSION`을 다른 경로로 바꿔야 하면 bootstrap 전에 설정하고
`scripts/bootstrap.sh --check`를 다시 실행한다. repair-agent permission은 bootstrap
설치 시점의 경로로 고정된다.
`network_access = true`는 해당 Codex session command의 outbound network를
허용한다는 뜻이지 Codex/Claude/agy/Gemini 도메인만 허용하는 allowlist가 아니다.
더 엄격한 egress가 필요하면 `network_access = false`로 두고 command approval이나
관리형 network policy를 사용한다. 이 plugin 때문에 `danger-full-access`를 쓰지
않는다.

## 런타임 산출물과 정리

Wrapper telemetry는 로컬에 남지만 크기가 제한된다. 파일은 wrapper family별로
`bin/_logs/<cli>/` 아래에 생긴다(`claude`, `gemini`, `antigravity`).

- `audit.jsonl`은 운영 telemetry다. active file이 10 MB를 넘으면 rotate하고,
  CLI당 archive는 최대 5개 / 50 MB까지만 유지한다.
- 실패 IPC run log는 `bin/_logs/<cli>/runs/*.json`에 생긴다. 파일명에는 UTC
  timestamp, process id, 8자 random UUID suffix가 들어가므로 병렬 dispatch끼리
  충돌하지 않는다.
- 정상 dispatch cleanup은 repair agent가 끝난 뒤 run log와 대응되는
  `.repair.json`을 지운다.
- wrapper failsafe는 run log를 CLI당 100개 / 20 MB로 제한하고, 다음 normal
  dispatch 시작 시 7200초보다 오래된 run log와 `.repair.json`을 sweep한다. 이
  age floor는 실행 중인 병렬 repair를 지우지 않기 위한 안전 여유다.

삭제 시에는 dispatch가 돌고 있지 않음을 확인한 뒤 source checkout이나 설치된
plugin cache의 `bin/_logs/`를 선택적으로 지운다.

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
TRIAD_BOOTSTRAP_SKIP_AUTH=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

For an internal Git marketplace source, use:

```bash
cd /path/to/triad-codex-dispatch
git fetch --tags origin <release-ref>
git checkout --detach FETCH_HEAD
codex plugin marketplace remove triad-codex-dispatch-local
codex plugin marketplace add <internal-git-url-or-owner/repo> --ref <release-ref>
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
TRIAD_BOOTSTRAP_SKIP_AUTH=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

`marketplace upgrade` refreshes the currently configured source; it does not
change a previously configured `--ref`. Re-add the marketplace source when
moving a fleet from one pinned release ref to another. Even for an unchanged
moving branch ref, the `git fetch ... <release-ref>` plus detached `FETCH_HEAD`
step above is what advances the local bootstrap checkout before bootstrap runs.

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
    <string>cd /path/to/triad-codex-dispatch &amp;&amp; git pull --ff-only &amp;&amp; codex plugin add triad-codex-dispatch@triad-codex-dispatch-local &amp;&amp; TRIAD_BOOTSTRAP_SKIP_AUTH=1 TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never scripts/bootstrap.sh --check</string>
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
TRIAD_BOOTSTRAP_SKIP_AUTH=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

사내 Git marketplace:

```bash
cd /path/to/triad-codex-dispatch
git fetch --tags origin <release-ref>
git checkout --detach FETCH_HEAD
codex plugin marketplace remove triad-codex-dispatch-local
codex plugin marketplace add <internal-git-url-or-owner/repo> --ref <release-ref>
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
TRIAD_BOOTSTRAP_SKIP_AUTH=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

`marketplace upgrade`는 이미 설정된 source를 새로고침할 뿐, 기존 `--ref`를 다른
값으로 바꾸지 않는다. fleet를 새 pinned release ref로 옮길 때는 marketplace
source를 다시 add한다. 같은 moving branch ref를 계속 쓰더라도, bootstrap 실행 전
local checkout을 최신 snapshot으로 이동시키는 단계는 위의 `git fetch ...
<release-ref>`와 detached `FETCH_HEAD` checkout이다.

macOS launchd를 쓰려면 위 English section의
`com.company.triad-codex-dispatch-update.plist` 예시를
`~/Library/LaunchAgents/`에 만들고 `/path/to/triad-codex-dispatch`만 실제
checkout 경로로 바꾼다. 등록 명령:

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.company.triad-codex-dispatch-update.plist
launchctl enable gui/$(id -u)/com.company.triad-codex-dispatch-update
```

업데이트 후 새 Codex thread를 시작해야 plugin cache에서 갱신된 skill이 로드된다.
예약 job에는 vendor 호출을 아끼기 위해 `TRIAD_BOOTSTRAP_SKIP_AUTH=1`을 두고,
auth 재점검은 필요할 때 수동으로 `scripts/bootstrap.sh --check`를 실행한다.
