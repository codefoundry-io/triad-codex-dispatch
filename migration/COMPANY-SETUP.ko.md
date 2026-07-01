# 회사 설치 가이드: Triad Codex Dispatch

이 저장소는 Codex 리더용 triad dispatch 툴킷을 Codex 플러그인과
bootstrap 점검 스크립트로 배포한다. 명령은 clone한 저장소 루트에서 실행한다.

## 검증된 배포 경로

- 플러그인 manifest: `.codex-plugin/plugin.json`. 최신 Codex 매뉴얼과
  `codex plugin --help`로 확인했다.
- 저장소 marketplace: `.agents/plugins/marketplace.json`.
- 플러그인 skills: 플러그인의 `skills/` 패키징 미러로 설치 가능함을 확인했다.
- repair agent: 2026-07-01 Spike D 기준 플러그인 cache 안의 TOML은
  이름으로 spawn되지 않는다. fresh Codex 테스트 결과는
  `unknown agent_type 'claude-wrapper-repair'`였다.
- fallback: `scripts/bootstrap.sh --check`가 `agents/*.toml`을
  `~/.codex/agents/`로 복사한다. 이 personal scope는 이미 spawn 가능으로
  검증된 경로다.

## 설치

로컬 clone 기준:

```bash
cd /path/to/triad-codex-dispatch
codex plugin marketplace add .
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

사내 Git marketplace를 쓸 때는 `.` 대신 owner가 확정한 내부 source를 넣는다.

```bash
codex plugin marketplace add <internal-git-url-or-owner/repo> --ref main
codex plugin marketplace upgrade
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

설치 후 새 Codex thread를 시작한다. Codex가 workspace trust를 물으면 trust해야
project-local `.agents/skills/`가 로드된다.

## 권장 Codex 사용자 설정

Skill은 sandbox를 우회하지 않는다. OpenAI Codex 문서 기준으로 skill은 재사용
instruction으로 로드되고, skill 때문에 실행되는 로컬 명령/스크립트는 현재 Codex
세션의 sandbox와 approval policy를 그대로 상속한다. 기본 로컬 작업 자세는 아래를
권장한다.

```toml
# ~/.codex/config.toml
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = false
```

이 툴킷 때문에 `sandbox_mode = "danger-full-access"`를 설정하지 않는다.

이 distribution layer가 user home에 써야 하는 경로는 bootstrap 대상뿐이다.

- `~/.codex/agents/`: personal-scope repair agents.
- `~/.config/triad-codex-dispatch/`: classifier patches.

기본 권장: 이 두 경로는 sandbox 밖에 두고, `scripts/bootstrap.sh --check`가
personal-scope write 승인을 요청할 때 승인한다. 팀에서 bootstrap을 무인 실행해야
한다면 아래 두 writable root만 정확히 추가한다.

```toml
# ~/.codex/config.toml
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
writable_roots = [
  "/Users/chaniri/.codex/agents",
  "/Users/chaniri/.config/triad-codex-dispatch",
]
network_access = false
```

관리 배포 템플릿에서는 `/Users/chaniri`를 대상 사용자의 home directory로 바꾼다.

## 업데이트

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin marketplace upgrade triad-codex-dispatch-local
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
scripts/bootstrap.sh --check
```

재설치 후에는 새 Codex thread에서 플러그인 skill을 다시 로드한다.

## Bootstrap 점검 항목

`scripts/bootstrap.sh --check`는 다음을 확인하거나 설치한다.

- `codex`, `claude`, `gemini`, `agy`, `python3 >= 3.12`, `jq`.
- Codex, Claude, Gemini, agy auth probe. hermetic CI 테스트에서만
  `TRIAD_BOOTSTRAP_SKIP_AUTH=1`을 쓴다.
- repo `bin/`이 `PATH`에 없으면 `claude_wrapper.py`, `gemini_wrapper.py`,
  `antigravity_wrapper.py` launcher를 설치한다. symlink가 아니라 실행 가능한
  작은 스크립트다.
- classifier extension JSON:
  `~/.config/triad-codex-dispatch/classifier-patches.json`, 또는
  `TRIAD_CLASSIFIER_EXTENSION`이 지정한 경로.
- personal-scope repair agents: `~/.codex/agents/`.

`~/.local/bin`이 `PATH`에 없다면 bootstrap 전에 추가하거나,
`TRIAD_BOOTSTRAP_BIN_DIR`를 이미 `PATH`에 있는 디렉터리로 지정한다.

## Auth 와 Egress

- `claude`는 shell에서 독립적으로 인증되어 있어야 한다. Codex 부모 세션의
  인증 토큰을 재사용하지 않는다.
- repair가 필요한 leader session은 `codex --search ...`로 실행한다. repair
  subagent는 leader의 web search 권한을 상속한다.
- Google-family 기본 leg는 `agy`다. Antigravity 인증이 필요하다.
- `gemini`는 business, Vertex, API-key tier 전용이다. 개인 tier Gemini CLI는
  `IneligibleTierError`가 정상적인 실패 경로이며 이 경우 agy를 쓴다.
- Codex/OpenAI, Claude, Antigravity, 내부 Git marketplace source로 나가는
  egress를 허용한다.

## Locked Fleet

관리자는 이 저장소를 허용된 marketplace source로 제한하고 public plugin sharing을
끄는 방식으로 배포할 수 있다. 최종 internal source URL은 owner 결정이 필요하다.

예시 managed requirements 형태:

```toml
features.plugins = true
features.plugin_sharing = false

[plugins.sources.triad-codex-dispatch-local]
source = "<internal-git-url>"
ref = "main"
```

실제 rollout 전에는 현재 Codex admin policy의 정확한 managed config key를 다시
검증한다.

## 아직 필요한 Owner 결정

- Marketplace source: 내부 Git URL vs local clone 배포.
- Classifier path: `triad-codex-dispatch` isolated path 유지 후 기존
  `triad-dispatch` patch import vs old path 공유.
- 같은 Codex family fresh reviewer 용도의 `codex_wrapper.py` 경로를 유지할지.
