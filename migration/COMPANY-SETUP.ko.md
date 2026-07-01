# 회사 설치 가이드: Triad Codex Dispatch

이 저장소는 Codex 리더용 triad dispatch 툴킷을 Codex 플러그인과
bootstrap 점검 스크립트로 배포한다. 명령은 clone한 저장소 루트에서 실행한다.

## 검증된 배포 경로

- 플러그인 manifest: `.codex-plugin/plugin.json`. 최신 Codex 매뉴얼과
  `codex plugin --help`로 확인했다.
- 저장소 marketplace: `.agents/plugins/marketplace.json`.
- 플러그인 skills: 플러그인의 `skills/` 패키징 미러로 설치 가능함을 확인했다.
- repair agent: plugin cache 안의 TOML을 runtime spawn source로 쓰지 않는다.
  retained-evidence로 지원하는 경로는 personal-scope 설치다.
- fallback: `scripts/bootstrap.sh --check`가 `agents/*.toml`을
  `~/.codex/agents/`로 복사한다. 이 personal scope는 이미 spawn 가능으로
  검증된 경로다. 자세한 결정 경계는
  `docs/references/spike-d-plugin-agent-distribution-decision.md`를 본다.

## 설치

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

사내 Git marketplace를 쓸 때도 bootstrap용 local checkout은 필요하다. `.` 대신
owner가 확정한 내부 source를 넣는다.

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

plugin 설치는 marketplace snapshot을 쓰지만, bootstrap은 local checkout의
`scripts/`, `bin/`, `agents/`를 읽는다. bootstrap 실행 전 local checkout도 같은
`<release-ref>` snapshot에 detached 상태로 맞춘다. 설치 후에도 이 checkout을
유지한다. wrapper launcher는 이 absolute checkout path의 `bin/*.py`를 실행한다.
`<release-ref>`는 merge 후에는 `main`, 현재 branch를 직접 검증할 때는
`distribution-layer`로 둔다.

기본 사용자 조건: 이 배포판은 triad CLI family를 이미 쓰는 heavy user용이다.
`codex`, `claude`, `agy`는 설치와 인증이 끝나 있어야 한다. business-tier `gemini`는
팀이 `TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1`을 켠 경우에만 필수다. bootstrap은 CI나 예약
updater job에서 `TRIAD_BOOTSTRAP_SKIP_AUTH=1`을 둔 경우를 제외하고 이 auth 상태를
점검한다.

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
cat >> ~/.zshrc <<'EOF'
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
source ~/.zshrc
codex-triad
```

plain `codex` function은 heavy-user external-CLI 자세가 그 머신의 기본값이어도 되는
환경에서만 켠다. profile이나 rules를 바꾼 뒤에는 기존 Codex session을 재시작해야
한다.

설치 후 새 Codex thread를 시작해야 plugin cache의 skill이 로드된다. 이 repo에서
개발하거나 repo-local `.agents/skills/`를 직접 쓸 때만 workspace trust가 필요하다.
project-local skill은 trust gate를 통과해야 로드된다.

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

이 distribution layer가 user home에 쓸 수 있는 경로는 bootstrap 대상뿐이다.

- `~/.codex/agents/`: personal-scope repair agents.
- `~/.config/triad-codex-dispatch/`: classifier patches.
- `~/.local/bin/`: wrapper launcher. 단 `TRIAD_BOOTSTRAP_BIN_DIR`가 다른
  `PATH` 디렉터리를 가리키면 그 경로를 쓴다.

기본 권장: 이 bootstrap 대상 경로들은 sandbox 밖에 두고, `scripts/bootstrap.sh --check`가
personal-scope write 승인을 요청할 때 승인한다. 이 경우 network access는 계속
승인 기반이다.

```toml
# ~/.codex/config.toml
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = false
```

팀에서 bootstrap을 무인 실행해야 한다면 아래 bootstrap writable root만 정확히 추가한다.

```toml
# ~/.codex/triad-codex-dispatch-install.config.toml
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
writable_roots = [
  "/Users/YOUR_USER/.codex/agents",
  "/Users/YOUR_USER/.config/triad-codex-dispatch",
  "/Users/YOUR_USER/.local/bin",
]
network_access = false
```

bootstrap은 `codex --profile triad-codex-dispatch-install --search`에서 돌리거나,
normal session에서 `scripts/bootstrap.sh --check`를 1회 승인한다. `~/.local/bin`은
launcher script 설치/갱신 때만 필요하므로 평소 runtime profile에 계속 writable로
두지 않는다.

vendor CLI 호출 때 반복 승인을 줄이는 것이 목표라면 trusted workspace 전용
편의 profile을 따로 만들고 egress tradeoff를 명시한다.

배포용 heavy triad user에게는 no-prompt wrapper setup을 생성한다.

```bash
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
scripts/bootstrap.sh --check
```

이 명령은 `$CODEX_HOME/triad-codex-dispatch.config.toml`을 쓴다. `CODEX_HOME`이
없으면 `~/.codex/triad-codex-dispatch.config.toml`을 쓴다. bootstrap이 만든 marker가
있는 profile만 갱신하며, 사용자가 직접 만든 unmanaged profile이 이미 있으면
`refusing to overwrite unmanaged Codex profile`로 실패하고 덮어쓰지 않는다. 또한
사용자의 실제 launcher/check-out 경로가 들어간
`$CODEX_HOME/rules/triad-codex-dispatch.rules`를 쓴다. `CODEX_HOME`이 없으면
`~/.codex/rules/triad-codex-dispatch.rules`를 쓴다.

이 profile은 heavy triad user의 명시적 external-CLI 동의 경계다. 이 profile로
Codex를 시작하면 일반 dispatch가 관련 prompt, repo snippet, review packet,
failure log를 이미 인증된 `claude`, `agy`, 선택적 `gemini` CLI로 보낼 수 있음을
승인한다. `--sandbox workspace-write`에서는 선택된 external CLI가 wrapper의 trusted
runtime root 안에서 edit/write를 수행할 수도 있다. wrapper는 `--cwd`와
`--prompt-file`이 이 root 밖이면 거부하며, 추가 root는 Codex 시작 전에
`TRIAD_WRAPPER_ALLOWED_ROOTS`로 명시해야 한다.
`TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never`와 생성된 rules를 같이 쓰면 매칭되는
wrapper command는 추가 approval prompt 없이 항상 sandbox 밖에서 실행된다.
이것이 배포용 기본 경로다.

원본 toolkit과 같은 평소 사용성을 내려면 매번 이 profile로 Codex를 시작해야 한다.
권장 shell 설정은 아래와 같다.

```bash
cat >> ~/.zshrc <<'EOF'
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
source ~/.zshrc
```

triad 작업에는 `codex-triad`를 쓰고, 이 자세가 머신 기본값이어도 되는 경우에만
optional plain `codex` function을 켠다.

per-call approval prompt를 유지하는 보수적 설치가 필요하면 approval override를 뺀다.

```bash
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
scripts/bootstrap.sh --check
```

배포용 no-prompt 경로도 `danger-full-access`는 쓰지 않는다.

수동 동등 설정은 아래와 같다.

```toml
# ~/.codex/triad-codex-dispatch.config.toml
# Heavy triad user를 위한 external-CLI consent profile.
approval_policy = "on-request"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
writable_roots = [
  "/Users/YOUR_USER/.config/triad-codex-dispatch",
  "/path/to/triad-codex-dispatch/bin/_logs",
]
network_access = true
```

이 profile은 아래처럼 시작한다.

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

rules를 직접 검토하거나 fleet packaging에 넣으려면 placeholder path를 바꾼 뒤
template을 복사한다.

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

rules 변경 후 Codex를 재시작한다. 생성된 rules는 wrapper 전용 prefix만 허용한다:
absolute bootstrap launcher path만 허용한다. bare wrapper name, checkout
`bin/*.py` path, `python3 <wrapper>`, `/usr/bin/env python3`, `bash -lc`나
`zsh -lc` 같은 넓은 shell entrypoint는 허용하지 않는다. Codex rules는 argv
prefix를 매칭하며, redirection/command substitution/env/wildcard가 들어간 shell
script는 안전하게 split하지 않는다. no-prompt 경로에서는 literal absolute-wrapper
command를 사용한다. 긴 prompt는 active workspace 아래 absolute prompt file, 예를
들면 `$PWD/_runs/prompts/<id>.txt`에 쓰고 `--prompt-file /absolute/path/to/prompt.txt`로
넘긴다. wrapper command에서 heredoc command substitution을 쓰지 않는다. wrapper는
`TRIAD_WRAPPER_ALLOWED_ROOTS` 밖의 `--prompt-file`과 `--cwd`를 거부한다.
`codex-triad` shell function은 Codex를 시작한 directory를 이 root로 설정한다. 추가
trusted workspace root가 필요하면 Codex 시작 전에 `TRIAD_WRAPPER_ALLOWED_ROOTS`를
설정한다.
structured-output `--pydantic module:Class` 기능은 남아 있지만, class 로딩이 Codex
sandbox 밖 Python import가 되므로 `TRIAD_ALLOW_PYDANTIC_IMPORT=1`을 명시한 경우에만
허용한다.

Codex 문서는 `--profile profile-name`이
`~/.codex/profile-name.config.toml`을 로드한다고 설명하고, 현재 CLI help도 같은
`$CODEX_HOME/<name>.config.toml` layering 동작을 표시한다. profile 파일의 key는
`[profiles.<name>]` 아래가 아니라 top-level에 둔다.

`network_access = true`는 해당 Codex session의 command에 outbound network를
허용한다. Codex, Claude, agy, Gemini 도메인만 허용하는 domain allowlist가 아니다.
도메인 단위 egress 제한이 필요하면 managed network policy나 command approval을
사용한다.

Rules는 matching command를 sandbox 밖에서 prompt 없이 실행할 수 있는지만 결정한다.
enterprise managed requirements, tenant guardian policy, data-export deny를
override하지 않는다. managed policy가 private workspace material을 external CLI로
보내는 것을 금지하면 local rules로는 우회할 수 없다.

### Provider별 Sandbox 차이

provider sandbox는 서로 호환되는 하나의 모델이 아니다. Codex는 생성된
`workspace-write` profile과 launcher-only `prefix_rule`로 no-prompt dispatch를
처리한다. Claude read-only dispatch는 `--permission-mode dontAsk`와
`Read,Glob,Grep`, 선택적 `WebSearch,WebFetch`로 매핑된다. Antigravity는 settings
transaction과 `agy --sandbox`를 함께 쓴다. Gemini business-tier dispatch는
read-only에서 Gemini Policy Engine 파일을 붙이고 read-only `auto_edit`를 거부한다.
다만 Gemini read-only enforcement를 신뢰하기 전에는 회사 business-tier 계정에서
write-attempt 검증을 통과해야 한다. 개인 Gemini CLI 사용자는 Gemini leg가 아니라
agy를 써야 한다.

`~/.codex/agents`와 `~/.local/bin`은 day-to-day runtime profile에 계속 writable로
두지 않는다. repair-agent TOML과 wrapper launcher는 bootstrap/update 때 설치되고,
일반 dispatch 중에는 읽기만 한다.

`/path/to/triad-codex-dispatch`는 bootstrap launcher가 가리키는 local checkout
경로로 바꾼다. 전체 checkout이 아니라 runtime artifact 디렉터리인 `bin/_logs`만
writable로 둔다. bootstrap은 repair-agent TOML마다 `triad_repair` Codex
permission profile(`default_permissions = "triad_repair"`)을 설치한다. 이 agent는
toolkit checkout을 읽고, `~/.config/triad-codex-dispatch`와 해당 checkout의
`bin/_logs`만 쓰며, repair verification call을 위해 network를 켠다. 호출 대상
source tree write 권한은 받지 않는다. bootstrap은 toolkit checkout, classifier
directory, Python runtime에 대한 absolute filesystem grant를 주입하며, resolved
vendor CLI executable directory도 read-only로 주입한다. repair profile은
`:workspace_roots`를 쓰지 않는다. named-agent spawnability 증거와 Codex
permission-profile 공식 문서 근거는
`docs/references/spike-d-plugin-agent-distribution-decision.md`와
`docs/references/codex-permission-profile-evidence.md`에 분리해 기록한다.
repair verification은 원래 wrapper의 `--cwd`를 제거하고 toolkit checkout에서
실행한다. 호출 대상 source tree read/write 권한 없이 classifier routing만 검증한다.
`TRIAD_CLASSIFIER_EXTENSION`을 다른 경로로 바꿔야 하면 bootstrap 전에 설정하고
`scripts/bootstrap.sh --check`를 다시 실행한다. repair-agent permission은 bootstrap
설치 시점의 경로로 고정된다.

## 업데이트

로컬 clone:

```bash
cd /path/to/triad-codex-dispatch
git pull --ff-only
codex plugin add triad-codex-dispatch@triad-codex-dispatch-local
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
scripts/bootstrap.sh --check
```

`codex plugin marketplace upgrade`는 설정된 source를 새로고침할 뿐 기존 pinned
`--ref`를 다른 값으로 바꾸지 않는다. `<release-ref>`를 바꿀 때는 marketplace
source를 다시 add한다. 같은 moving branch ref를 계속 쓰더라도 bootstrap 실행 전
local checkout을 최신 snapshot으로 이동시키는 단계는 위의 `git fetch ...
<release-ref>`와 detached `FETCH_HEAD` checkout이다.

재설치 후에는 새 Codex thread에서 플러그인 skill을 다시 로드한다.

## 삭제

설치된 plugin과 marketplace source를 제거한다.

```bash
codex plugin remove triad-codex-dispatch@triad-codex-dispatch-local
codex plugin marketplace remove triad-codex-dispatch-local
```

bootstrap이 설치한 파일은 필요하면 지운다.

```bash
rm -f ~/.codex/agents/claude-wrapper-repair.toml
rm -f ~/.codex/agents/gemini-wrapper-repair.toml
rm -f ~/.codex/agents/agy-wrapper-repair.toml
rm -f ~/.local/bin/claude_wrapper.py
rm -f ~/.local/bin/gemini_wrapper.py
rm -f ~/.local/bin/antigravity_wrapper.py
```

bootstrap에서 `TRIAD_BOOTSTRAP_BIN_DIR`를 지정했다면 `~/.local/bin` 대신 그
디렉터리에서 launcher를 지운다. classifier directory는 로컬에서 학습된 routing을
버리려는 게 확실할 때만 지운다.

```bash
rm -rf ~/.config/triad-codex-dispatch
```

runtime log는 local artifact다. dispatch가 돌고 있지 않을 때 source checkout이나
설치된 plugin cache의 `bin/_logs/`를 선택적으로 지운다.

## Bootstrap 점검 항목

`scripts/bootstrap.sh --check`는 다음을 확인하거나 설치한다.

- 필수 binary: `codex`, `claude`, `agy`, `python3 >= 3.12`, `jq`.
- 선택 binary: `gemini`. 단 `TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1`이면 필수다.
- Codex, Claude, agy auth probe. Gemini auth는
  `TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1`일 때만 필수다.
  `TRIAD_BOOTSTRAP_SKIP_AUTH=1`은 hermetic CI 테스트나 예약 updater job에서만
  쓴다.
- wrapper command가 이 checkout으로 resolve되지 않으면 `claude_wrapper.py`,
  `gemini_wrapper.py`, `antigravity_wrapper.py` launcher를 설치한다. symlink가
  아니라 실행 가능한 작은 스크립트이며, update 때 다시 쓴다. 더 앞선 `PATH`
  항목이 옛 wrapper로 shadowing하면 bootstrap은 실패한다.
- classifier extension JSON:
  `~/.config/triad-codex-dispatch/classifier-patches.json`, 또는
  `TRIAD_CLASSIFIER_EXTENSION`이 지정한 경로.
- personal-scope repair agents: `~/.codex/agents/`.

`~/.local/bin`이 `PATH`에 없다면 bootstrap 전에 추가하거나,
`TRIAD_BOOTSTRAP_BIN_DIR`를 이미 `PATH`에 있는 디렉터리로 지정한다.

## 런타임 산출물과 정리

Runtime telemetry는 wrapper family별 `bin/_logs/<cli>/` 아래에 생긴다.

- `audit.jsonl`은 active file이 10 MB를 넘으면 rotate하고, CLI당 archive는
  최대 5개 / 50 MB까지만 유지한다.
- 실패 IPC run log는 `bin/_logs/<cli>/runs/*.json`에 생긴다. 파일명에는 UTC
  timestamp, process id, 8자 random UUID suffix가 들어가 병렬 실행에서도
  유니크하다.
- dispatch skill은 repair agent가 끝난 뒤 run log와 대응되는 `.repair.json`을
  지운다.
- wrapper failsafe는 run log를 CLI당 100개 / 20 MB로 제한하고, 다음 normal
  dispatch 시작 시 7200초보다 오래된 run log와 `.repair.json`을 sweep한다.

repair agent가 `~/.config/triad-codex-dispatch/classifier-patches.json`을 수정할
때는 classifier JSON 옆 advisory lock file을 사용하도록 지시되어 있어 병렬 repair
간 덮어쓰기를 피한다.

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

현재 Codex fleet-management key를 admin이 재검증하기 전에는 아래를 copy-paste
최종 policy가 아니라 예시 형태로만 취급한다.

```toml
features.plugins = true
features.plugin_sharing = false

[plugins.sources.triad-codex-dispatch-local]
source = "<internal-git-url>"
ref = "<release-ref>"
```

실제 rollout 전에는 현재 Codex admin policy의 정확한 managed config key를 다시
검증한다.

## 아직 필요한 Owner 결정

- Marketplace source: 내부 Git URL vs local clone 배포.
- Classifier path: `triad-codex-dispatch` isolated path 유지 후 기존
  `triad-dispatch` patch import vs old path 공유.

## 확정된 리더 전환 결정

- 같은 family Codex 작업용 `codex_wrapper.py` dispatch leg는 배포하지 않는다.
  이 배포판에서는 Codex가 리더이며, cross-family review의 fresh Codex 관점은
  `spawn_agent(fork_context=false)`로 확보한다.
