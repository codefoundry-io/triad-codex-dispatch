# triad-codex-dispatch

[English README](README.md)

Codex를 리더로 두고 Claude Code, Antigravity(`agy`), 선택적 business-tier Gemini를
단발 worker로 호출하는 triad dispatch 플러그인입니다. 이 문서는 public GitHub 배포
사용자를 위한 설치/업데이트/삭제 가이드입니다.

## 제공 기능

- `skills/` 아래의 Codex 플러그인 skill.
- Claude, agy, Gemini wrapper launcher.
- `$CODEX_HOME/agents` 또는 `~/.codex/agents`에 설치되는 Codex custom repair agent.
- 승인된 wrapper 호출이 반복 prompt 없이 sandbox 밖에서 실행되도록 하는 Codex profile
  및 command rules.

## 전제 조건

bootstrap 전에 설치와 로그인이 끝나 있어야 합니다.

- `codex`
- `claude`
- `agy`

선택 사항:

- `gemini`: business, Vertex, API-key Gemini 계정 전용입니다. 개인 Google-family
  사용자는 `agy`를 쓰세요.

host 도구:

- `git`, `jq`, `python3 >= 3.12`
- Linux/WSL2: Codex sandbox 지원을 위해 `bubblewrap`(`bwrap`) 설치.
- `~/.local/bin`이 `PATH`에 있어야 합니다. 아니면 이미 `PATH`에 있는 디렉터리를
  `TRIAD_BOOTSTRAP_BIN_DIR`로 지정하세요.

installer는 OAuth login이나 OS package 설치를 대신하지 않습니다.

## 설치

public GitHub repository에서 바로 설치합니다. 일반 사용자는 local clone이 필요 없습니다.

Repository: https://github.com/codefoundry-io/triad-codex-dispatch

설치/업데이트/삭제 명령을 실행하기 전에 설치 scope를 하나 고르세요.

- User scope: 권장 기본값입니다. `CODEX_HOME`, `XDG_CONFIG_HOME`,
  `TRIAD_BOOTSTRAP_BIN_DIR`를 지정하지 않습니다.
- Workspace scope: plugin cache, profile, rules, classifier patch, launcher를
  현재 workspace 아래에 두고 싶을 때만 씁니다. 해당 workspace에서 실행하고, Codex를
  시작할 때도 같은 환경변수를 유지하세요.

```bash
# Workspace scope 전용입니다. User scope면 이 블록을 건너뜁니다.
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

# 이 플러그인의 기본 대상 사용자를 위한 no-prompt 설치입니다.
# 보수적 설치: 아래 env 세 줄을 빼고 bootstrap만 실행하세요.
# 그러면 Codex가 external-CLI 승인 질문을 할 수 있습니다.
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --check
```

설치 후 새 Codex session을 시작합니다.

```bash
codex --profile triad-codex-dispatch --search
```

설치 시 중요한 점:

- User scope는 repair agent, profile, command rules를 `~/.codex/` 아래에
  설치합니다.
- User scope는 classifier patch를 `~/.config/triad-codex-dispatch/` 아래에 저장합니다.
- User scope는 wrapper launcher를 기본적으로 `~/.local/bin`에 설치합니다.
- Workspace scope는 같은 산출물을 `.triad-codex-home/`, `.triad-config/`,
  `.triad-bin/` 아래에 둡니다.
- 생성된 wrapper launcher는 설치된 plugin cache의 파일을 호출합니다. plugin을 업데이트한
  뒤에는 bootstrap을 다시 실행해서 launcher 경로를 최신 상태로 맞추세요.
- launcher는 확인된 vendor CLI 경로를 고정합니다. `claude`, `agy`, 선택적 `gemini`를
  업그레이드하거나 이동한 뒤에도 bootstrap을 다시 실행하세요.
- 기존 Codex session은 새 plugin skill이나 custom agent를 못 볼 수 있습니다. 설치나
  업데이트 후 새 session을 시작하세요.
- agy 호출은 `~/.gemini/antigravity-cli/` 아래 Antigravity CLI runtime 설정을
  transaction으로 다룰 수 있습니다. 이것은 bootstrap 설치 대상이 아니라 provider
  runtime 상태입니다.
- `codex plugin add --json`은 marketplace `authPolicy`를 표시할 수 있지만, 이
  플러그인은 CLI OAuth/login을 수행하지 않습니다.

## 권장 실행 명령

현재 workspace에서 항상 triad profile로 Codex를 시작하는 명령을 추가합니다.
Workspace scope라면 이 명령을 쓰기 전에 같은 scope 환경변수를 먼저 export하세요.

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

plain `codex`까지 triad profile로 바꾸는 alias/function은 이 no-prompt external-CLI
자세가 해당 머신의 기본값이어도 될 때만 사용하세요.

## 사용

Codex에게 다음 skill을 사용하도록 요청합니다.

- `triad-claude-dispatch`: Claude Code 단발 consult.
- `triad-antigravity-dispatch`: `agy` 기반 기본 Google-family consult.
- `triad-gemini-dispatch`: Gemini business/Vertex/API-key 계정 전용.
- `triad-cross-family-review`: Claude, Google-family, fresh Codex subagent 기반
  pre-merge review.

일반 code-write dispatch는 대상 workspace에서 실행하세요. wrapper는 process working
directory를 기본 trusted root로 봅니다. 추가 trusted root가 필요할 때만
`TRIAD_WRAPPER_ALLOWED_ROOTS`를 설정하세요.

## 업데이트

Workspace scope로 설치했다면 설치 때 쓴 scope 환경변수를 먼저 다시 export하세요.

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

업데이트 후 새 Codex session을 시작하세요.

## 삭제

기본 user-home 설치 삭제:

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

custom `CODEX_HOME`으로 설치했다면 agent/profile/rules 파일은 `~/.codex`가 아니라
그 `CODEX_HOME`에서 지우세요.
custom `TRIAD_BOOTSTRAP_BIN_DIR`를 썼다면 세 wrapper launcher는 `~/.local/bin`이
아니라 그 디렉터리에서 지우세요. custom `XDG_CONFIG_HOME`을 썼다면
`~/.config/triad-codex-dispatch` 대신 그 config 디렉터리 아래
`triad-codex-dispatch/`를 지우세요.

Workspace scope 삭제:

```bash
export CODEX_HOME="$PWD/.triad-codex-home"
export XDG_CONFIG_HOME="$PWD/.triad-config"
export TRIAD_BOOTSTRAP_BIN_DIR="$PWD/.triad-bin"
export PATH="$TRIAD_BOOTSTRAP_BIN_DIR:$PATH"

codex plugin remove triad-codex-dispatch@triad-codex-dispatch
codex plugin marketplace remove triad-codex-dispatch

rm -rf .triad-codex-home .triad-config .triad-bin
```

## Custom Subagent

배포된 repair agent는 repair 전용이며 재귀 dispatch를 하면 안 됩니다. repair agent에
triad dispatch skill을 추가하지 마세요.

직접 만든 Codex custom subagent가 triad dispatch skill을 호출해야 한다면 Codex
`skills.config`에 필요한 `SKILL.md` 경로를 명시하세요. 경로는 설치/업데이트 때 얻은
`TRIAD_PLUGIN_DIR` 아래의 skill 파일을 가리키면 됩니다.

custom-agent TOML을 바꾼 뒤에는 새 Codex session을 시작하세요.

## Runtime Log 및 Local Data

Runtime telemetry는 설치된 plugin의 `bin/_logs/<cli>/` 아래에 local artifact로
남습니다. `audit.jsonl`은 redacted argv, prompt length, status, stdout/stderr
앞 500자, structured-output 존재 여부와 길이만 저장합니다. failure run log는 repair
replay를 위해 전체 prompt와 vendor transcript를 저장하고, repair 뒤 skill이
삭제합니다. failsafe는 오래된 run log를 cap으로 정리합니다. 이 파일들은 민감한
데이터로 보고 필요하면 `bin/_logs/`를 지우세요.

`approval_policy=never`는 이 plugin만이 아니라 triad Codex session 전체에 적용됩니다.
그 session에서는 관련 없는 작업을 하지 마세요. Antigravity settings는 agy 호출 중
`~/.gemini/antigravity-cli/` 아래에서 transaction으로 다룹니다. 같은 시간에 agy permission을 편집하거나 다른 Antigravity settings 변경을 실행하지 마세요.

## 참고

- 이 플러그인은 `danger-full-access`를 쓰지 않습니다.
- 생성된 command rules는 `~/.local/bin` 또는 `TRIAD_BOOTSTRAP_BIN_DIR` 아래에
  설치된 launcher 파일만 허용합니다. 그 launcher가 설치된 plugin cache를 호출합니다.
- repair-agent permission은 선언된 TOML grant입니다. 더 넓은 parent session이나
  managed runtime override가 더 많은 권한을 허용하지 못한다는 hard isolation 증명은
  아닙니다.
- 상세 설계와 검증 근거는 `docs/` 아래에 있습니다.
