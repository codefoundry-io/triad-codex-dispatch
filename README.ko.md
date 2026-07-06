# triad-codex-dispatch

[English README](README.md)

**AI 코딩 어시스턴트는 자기 리뷰어와 blind spot 을 공유합니다.** codex 에게 codex 의
결과물을 검토시키면 같은 framing 을 물려받습니다 — 버그를 만든 추론이 곧 그 버그를
리뷰하는 추론입니다. triad-codex-dispatch 는 **다른 모델 패밀리** 로부터 두 번째, 세
번째 의견을 받아줍니다: codex 가 리더로 남아 **Claude Code**(Anthropic)와
**antigravity / `agy`**(Google)를 단발(single-shot) 워커로 디스패치하고, 위험한
변경을 머지하기 전에는 각 패밀리가 그 결정을 **독립적으로** 반박하는 리뷰를
돌립니다 — 그래서 내 주 모델이 스스로 합리화해 넘긴 버그를, 그 blind spot 이 애초에
없던 모델이 잡아냅니다.

codex 플러그인으로 설치하고 계속 codex 에서 작업하되, 외부 의견이 필요하거나 변경이
머지를 막을 만큼 위험할 때 리더가 대신 다른 패밀리에 물어봅니다.

> **자매 제품:** 팀이 codex CLI 대신 **Claude Code** 를 리더로 쓴다면
> **[triad-dispatch](https://github.com/codefoundry-io/triad-dispatch)** 를 보세요
> — Claude Code 가 드라이버인 동일한 3-패밀리 모델입니다. 이 제품은 codex 드라이버용입니다.

## 제공 기능

- `skills/` 아래의 Codex 플러그인 skill.
- Claude, agy, Gemini wrapper launcher.
- Codex permission-profile 시스템 기반 생성 profile
  (`default_permissions = "triad_leader"`, `:workspace` 확장; legacy
  `sandbox_mode` key는 쓰지 않습니다)과 wrapper launcher용 command rules — 둘 다
  기본 설치됩니다.
- in-session repair agent는 설치하지 않습니다. dispatch가 classifier gap을 만나면
  SKILL이 top-level `codex exec -s read-only` analyzer 명령을 surface하며, 그
  명령을 fresh terminal에 붙여넣어 실행합니다. analyzer는 classifier entry ONE개를
  제안하고, 결정적 `bin/apply_patch.py`가 이를 검증 후 적용합니다. write 권한을 가진
  in-session repair worker는 없습니다.
- 선택적 managed `codex-triad` shell entry
  (`TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1`) — no-prompt 자세에서는 필수 시작
  명령입니다.

## 필수 설정 (~2분)

세 단계면 안전한(프롬프트하는) 기본값으로 동작하는 설치가 됩니다. 이 섹션 아래는
모두 선택입니다.

1. **native vendor 로그인.** leader `codex`와 사용할 worker 를 설치하고
   로그인합니다 — toolkit 은 credential 을 발급/refresh 하지 않습니다:
   - `codex` — 설치 후 `codex login`.
   - `agy` — 설치 + OAuth 로그인 (개인 사용자의 Google-family worker).
   - `claude` — Claude Code `>= 2.1.170`; 더 낮은 버전이면 bootstrap 이 경고합니다.

   host 도구 `git`, `jq`, `python3 >= 3.12` 도 필요하고, `~/.local/bin` 이 `PATH`
   에 있어야 합니다(아니면 이미 `PATH` 에 있는 디렉터리를 `TRIAD_BOOTSTRAP_BIN_DIR`
   로 지정). `gemini` 는 선택입니다 — [선택 / 고급](#선택--고급) 참고.

2. **플러그인 추가.** 일반 사용자는 local clone 이 필요 없습니다.

   ```bash
   codex plugin marketplace add codefoundry-io/triad-codex-dispatch --ref main

   TRIAD_PLUGIN_DIR="$(
     codex plugin add triad-codex-dispatch@triad-codex-dispatch --json |
       jq -r '.installedPath'
   )"
   ```

3. **bootstrap 실행 (env var 0개).** 그냥 `--install` 하면 runtime profile +
   command rules + wrapper launcher 가 설치됩니다 — 권장 setup:

   ```bash
   "$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --install
   ```

   생성 profile 은 `approval_policy=on-request` 를 유지하므로 Codex 가
   **external-CLI wrapper 호출마다 승인을 물어봅니다** — 안전한 기본값입니다.
   `--install` 은 LIVE vendor auth probe 도 실행합니다 (`codex login status` 와,
   `claude`·`agy`(설치된 경우 `gemini`)에 대한 "Return exactly OK." 한 줄 호출 각
   1회); CI / 예약 job 에서만 `TRIAD_BOOTSTRAP_SKIP_AUTH=1` 로 건너뜁니다.

   > **배치 불변식 (hard).** bootstrap 은 설치 대상이 들어 있는 디렉터리가 아니라
   > 작업할 project workspace 에서 실행하세요. bootstrap 은 profile + command rules
   > 를 `$CODEX_HOME`(기본 `~/.codex/`), classifier patch 를
   > `~/.config/triad-codex-dispatch/`, launcher 를 `~/.local/bin`(또는
   > `TRIAD_BOOTSTRAP_BIN_DIR`)에 설치합니다. 이 대상과 그것이 실행하는 모든 것
   > (plugin cache, `python3` runtime)은 sandbox-writable root 밖에 있어야 하며,
   > 어느 하나라도 실행 디렉터리(예: `$HOME`) 안으로 resolve 되면 hard-fail 합니다.

   설치 후 대상 workspace 에서 새 Codex session 을 시작합니다:

   ```bash
   codex --profile triad-codex-dispatch --search
   ```

이게 필수 경로의 전부입니다. repair 는 필요할 때만 surface 되는 수동 read-only
단계입니다([Custom Subagent](#custom-subagent) 와 [보안](#보안-security) 참고).

## 선택 / 고급

이 섹션의 어떤 것도 일반 개인 설치에는 필요 없습니다. 각 하위 섹션의 "다음 경우에만
하세요…" 조건이 해당될 때만 보세요.

### no-prompt 자세 (heavy user)

*Codex 가 wrapper 호출마다 묻지 않게 하고 싶을 때만.* 이것이 safety 프롬프트를
포기하는 유일한 설정이라 opt-in 으로 유지됩니다:
`TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never` 와 managed shell entry 를 bootstrap
명령에 추가합니다.

> **경고 — session 전체 적용.**
> `approval_policy=never`는 이 plugin만이 아니라 triad Codex session 전체에
> 적용됩니다. 그 session에서는 관련 없는 작업을 하지 마세요.

```bash
TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --install
```

no-prompt 자세에서 지원되는 유일한 시작 명령은
`TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1`이 shell RC(기본 `~/.bashrc`, zsh는
`~/.zshrc`, `TRIAD_BOOTSTRAP_SHELL_RC`로 override)에 추가하는 managed
`codex-triad` function입니다. 이 function은 wrapper-containment env를 고정합니다
(wrapper 프로세스의 path/pydantic 처리를 gate할 뿐, OS 수준 confinement 주장이
아닙니다 — [SECURITY.md](SECURITY.md) 참고):

```bash
codex-triad() {
  TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}" \
  TRIAD_WRAPPER_HARDENED=1 \
  TRIAD_CLAUDE_ENFORCE_SANDBOX=1 \
    command codex --profile triad-codex-dispatch --search "$@"
}
```

새 terminal을 열거나 shell RC를 source한 뒤, 대상 workspace에서 `codex-triad`로
시작하세요. no-prompt profile을 bare `codex --profile ...` 호출로 시작하지
마세요. 고정된 wrapper containment env 없이 실행됩니다.

### enterprise Gemini worker

*business / Vertex / API-key Gemini 계정이 있을 때만.* `gemini` 를 설치하고
로그인하세요; 개인 Google-family 사용자는 `agy` 를 쓰세요. 팀이 bootstrap 에서
필수로 요구하려면 `TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1` 을 설정합니다.

### 기본 profile / rules opt-out

*profile 및/또는 command rules 를 설치하고 싶지 않을 때만.* profile 과 rules 는
기본 설치됩니다. 각각 명시적 `=0` 또는 `SKIP` 로 억제합니다:

```bash
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=0 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=0 \
"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --install
# 동등: TRIAD_BOOTSTRAP_SKIP_CODEX_PROFILE=1 / _SKIP_CODEX_RULES=1
```

### Linux / WSL2 sandbox 지원

*Linux 또는 WSL2 에서만.* Codex sandbox 지원을 위해 `bubblewrap`(`bwrap`)을
설치하세요. installer 는 OS package 를 설치하지 않습니다.

### 보안 모델 읽기

*툴킷에 의존하기 전에 전체 threat model 을 보고 싶을 때만.*
[SECURITY.md](SECURITY.md) 참고 — 지속적인 control 은 model trust 가 아니라
privilege separation 입니다(아래 [보안](#보안-security) 에 요약).

### 회사 / fleet 설정

*개인 설치가 아니라 managed fleet 을 구성할 때만.* `migration/COMPANY-SETUP.md`
참고.

### bootstrap 재실행 참고

- `--check`는 `--install`의 deprecated alias이며 한 release 동안만 유지됩니다.
- 생성된 wrapper launcher 는 설치된 plugin cache 의 파일을 호출하므로, plugin
  업데이트 뒤에는 bootstrap 을 다시 실행해 launcher 경로를 최신으로 맞추세요.
- launcher 는 확인된 vendor CLI 경로를 고정하므로, `claude`, `agy`, 선택적
  `gemini` 를 업그레이드/이동한 뒤에도 다시 실행하세요.
- 기존 Codex session 은 새 plugin skill 을 못 볼 수 있으니 설치/업데이트 후 새
  session 을 시작하세요.
- agy 호출은 `~/.gemini/antigravity-cli/` 아래 Antigravity CLI runtime 설정을
  transaction 으로 다룰 수 있습니다 — bootstrap 설치 대상이 아니라 provider
  runtime 상태입니다.
- `codex plugin add --json`은 marketplace `authPolicy`를 표시할 수 있지만, 이
  플러그인은 CLI OAuth/login을 수행하지 않습니다.

## 사용

Codex에게 다음 skill을 사용하도록 요청합니다.

- `triad-claude-dispatch`: Claude Code 단발 consult.
- `triad-antigravity-dispatch`: `agy` 기반 기본 Google-family consult.
- `triad-gemini-dispatch`: Gemini business/Vertex/API-key 계정 전용.
- `triad-cross-family-review`: Claude, Google-family, fresh Codex subagent 기반
  pre-merge review.

### 첫 디스패치

대상 workspace에서 리더를 시작하고 단발 consult를 요청합니다:

```bash
codex --profile triad-codex-dispatch --search
```

그 세션에서:

> triad-claude-dispatch 로 Claude 에게 물어봐: `git rebase --onto` 는 무슨 일을 해? 한 문단으로.

Codex가 `triad-claude-dispatch` skill을 실행하고, Claude launcher를 호출해 Claude의
답을 돌려줍니다. stderr에 한 줄 성공 요약이 뜹니다:

```
[wrapper] claude ok exit=0 vendor=0 elapsed=6.4s
```

`[wrapper] claude`는 실행된 워커, `ok`는 분류(깨끗한 답변), `exit=0`은 성공입니다.
`triad-claude-dispatch`를 `triad-antigravity-dispatch`로 바꾸면 Google-family(`agy`)
leg을 같은 방식으로 consult할 수 있습니다.

일반 code-write dispatch는 대상 workspace에서 실행하세요. 경로 containment는
opt-in입니다: `TRIAD_WRAPPER_ALLOWED_ROOTS`가 설정된 경우에만 wrapper가 trusted root
밖의 `--cwd` / `--prompt-file`을 거부합니다(managed `codex-triad` shell entry가
`TRIAD_WRAPPER_HARDENED=1`과 함께 고정하는 hardened path). 기본은 경로를 제약하지
않으므로 경계는 격리된 `--cwd` worktree + Codex profile/rules에 의존합니다.

## 문제 해결 (Troubleshooting)

| 증상 | 원인 | 해결 |
|---|---|---|
| Codex가 wrapper 호출마다 승인을 물어봄 | 기본 자세가 `approval_policy=on-request` 유지 | 정상입니다. no-prompt 세션이 필요하면 [No-Prompt Opt-In](#no-prompt-opt-in-heavy-user-전용)을 쓰고 managed `codex-triad` function으로 시작하세요. |
| 디스패치가 `oauth-env`로 실패 | 워커 CLI 로그인이 만료됐거나 없음 | 해당 vendor의 native login 재실행(`claude` / `agy` OAuth, 또는 `codex login`). toolkit은 대신 재인증하지 않습니다 — 신호만 surface 하니 직접 로그인하세요. |
| gemini leg이 `IneligibleTier`로 실패 | Gemini CLI *개인* tier 폐지 | `agy`(Antigravity) leg을 쓰세요 — 개인 사용자의 Google-family leg입니다. `gemini`는 business / Vertex / API-key 계정 전용. |
| 설치/업데이트 후 새 skill이 안 보임 | 기존 Codex 세션은 새로 설치된 skill을 못 봄 | 새 Codex 세션을 시작하세요(플러그인 업데이트 뒤에는 launcher 경로 최신화를 위해 `bootstrap.sh --install` 재실행). |
| 디스패치가 non-zero로 끝났고 원인을 알고 싶음 | 각 실패에는 분류 + exit code가 있음 | 아래 exit-code 범례 + `[wrapper] …` stderr 줄의 분류를 보세요. |

**Exit-code 범례**(wrapper 프로세스 exit code; 같은 실패 class가
`[wrapper] <cli> <class> …` stderr 줄의 단어로도 나타납니다):

| Exit | 의미 | 조치 |
|---|---|---|
| `0` | 성공 — 이어서 답변 | 없음. |
| `64` | 재시도 후에도 server capacity 소진 | 일시적 vendor 과부하; 기다렸다 재시도. |
| `65` | 인증 / config / quota(예: `oauth-env`, `cli-subscription-cap`) | 재로그인하거나 quota reset 대기 — 분류 단어 참고. |
| `66` | 구조화 출력(`--pydantic`) 스키마 검증 실패 | 1회 repair 재시도 후에도 모델 JSON이 스키마 불일치. |
| `69` | code task가 blocked / 컨텍스트 부족(codex `--task code`) | 부족한 컨텍스트를 채워 재디스패치. |

## 범위와 한계 — 이 도구가 하지 않는 것

toolkit이 어디서 멈추는지 알 수 있도록, 정직한 경계:

- **vendor 인증이나 token을 관리하지 않습니다.** token 발급/refresh 없음, API-key
  주입 없음. 각 vendor CLI의 native login으로 직접 로그인하며, 인증성 에러는
  재로그인하라고 surface 됩니다. `bootstrap.sh --install`은 live auth probe를 돌리지만
  로그인 자체는 하지 않습니다.
- **OS 패키지를 설치하지 않습니다.** vendor CLI, `python3`, (Linux/WSL2에서)
  `bubblewrap`은 직접 설치하며, installer는 profile, rules, launcher만 씁니다.
- **자기개선 분류기는 heuristic이지 oracle이 아닙니다.** 진짜 실패를 그럴듯하지만
  틀린 class로 라우팅할 수 있습니다. worst case는 *integrity* 이슈 — 지속적 라우팅
  오분류이지 코드 실행이 **아닙니다**([보안](#보안-security) 참고) — 이지만,
  `~/.config/triad-codex-dispatch/classifier-patches.json`에 적용된 delta를
  주기적으로 검토하세요.
- **wrapper containment은 프로세스/권한 수준이지 OS 수준 confinement이 아닙니다.**
  wrapper-containment env는 wrapper 프로세스의 path/pydantic 처리를 gate할 뿐, OS
  수준 격리 주장이 아닙니다. 경계는 격리된 `--cwd` worktree + Codex profile/rules +
  커밋 전 사용자 검토에 의존합니다.

## 업데이트

```bash
codex plugin marketplace upgrade triad-codex-dispatch

TRIAD_PLUGIN_DIR="$(
  codex plugin add triad-codex-dispatch@triad-codex-dispatch --json |
    jq -r '.installedPath'
)"

# 그냥 --install 하면 기본 profile + rules 가 다시 적용됩니다; 설치 때 쓴
# opt-in env flag(예: no-prompt 자세)가 있으면 그것만 다시 추가하세요.
"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --install
```

업데이트 후 새 Codex session을 시작하세요.

## 설치 검증

### 플러그인 전용 smoke test (clone 불필요)

일반 경로입니다 — 아무것도 clone 하지 않고 toolkit 이 살아 있는지 확인합니다. 대상
workspace 에서 리더를 시작하고 codex 에게 사소한 Google-family dispatch 를 시킵니다:

```bash
codex --profile triad-codex-dispatch --search
```

그 세션에서:

> triad-antigravity-dispatch 로 agy 에게 물어봐: `git rebase --onto` 는 무슨 일을 해? 한 문단으로.

agy 의 답과 함께 stderr 에 한 줄 성공 요약이 뜹니다:

```
[wrapper] agy ok exit=0 vendor=0 elapsed=6.4s
```

이 `[wrapper] agy ok …` 줄이 디스패치가 동작했다는 신호입니다 — 플러그인, launcher,
profile 이 모두 연결된 것입니다. `ok` 는 분류이며, 다른 값(예: `oauth-env`,
`server-capacity`)은 특정 실패를 뜻합니다 — [문제 해결](#문제-해결-troubleshooting) 참고.

### 개발자 경로 (선택 — clone + pytest)

번들 unit 테스트를 돌리려면 repository 를 clone 해 실행하세요. `pytest`
(`python3 -m pip install pytest`)가 필요하며, 이는 테스트 전용 의존성으로 dispatch
도구 실행 자체에는 필요하지 않습니다:

```bash
git clone https://github.com/codefoundry-io/triad-codex-dispatch
cd triad-codex-dispatch
python3 -m pytest -q tests/ -p no:cacheprovider   # 모든 테스트 PASS 기대
```

## 삭제

plugin cache를 지우기 전에 managed uninstall을 먼저 실행하세요 (script가 그
cache 안에 있습니다).

```bash
"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --remove

codex plugin remove triad-codex-dispatch@triad-codex-dispatch
codex plugin marketplace remove triad-codex-dispatch
```

`--remove`(alias `--uninstall`)는 wrapper launcher, managed profile과 command
rules, managed `codex-triad` shell entry를 삭제합니다. 예전 설치가 남긴 legacy
personal-scope repair-agent TOML도 함께 삭제합니다(현재 설치는 하나도 쓰지
않습니다). 학습된 classifier patch는 보존됩니다. 학습된 routing까지 버리려면
`rm -rf ~/.config/triad-codex-dispatch`를 직접 실행하세요.

기본 user-home 설치 삭제의 수동 동등 명령(repair-agent 줄은 예전 설치를 정리할
때만 해당):

```bash
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

## Custom Subagent

이 배포는 repair subagent를 하나도 포함하지 않습니다. classifier repair는 SKILL이
surface하는 top-level `codex exec -s read-only` analyzer로 실행하며, 그 명령을 fresh
terminal에 붙여넣습니다 — analyzer는 읽기만 하고(session sandbox 아래 중첩된 codex는
init되지 않으며, top-level에서는 hard read-only), 유일한 writer는 결정적
`bin/apply_patch.py`입니다. run-log를 읽는 쪽에 write 권한이 없다는 privilege
separation이 confused-deputy 경로를 닫습니다; `triad-cross-family-review`의
fresh-codex reviewer leg는 계속 사용할 수 있습니다.

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

Antigravity settings는 agy 호출 중 `~/.gemini/antigravity-cli/` 아래에서
transaction으로 다룹니다. 같은 시간에 agy permission을 편집하거나 다른
Antigravity settings 변경을 실행하지 마세요.

## 보안 (Security)

지속적인 control은 model trust가 아니라 **privilege separation**입니다: untrusted
run-log를 읽는 컴포넌트는 write 권한이 0입니다. 이 제품은 in-session repair worker를
싣지 않습니다 — repair는 top-level `codex exec -s read-only` analyzer(write 불가)로,
그 proposal은 결정적 zero-LLM `bin/apply_patch.py`로만 적용됩니다. "model이 injection에
저항한다"는 경계가 **아닙니다**. 전체 threat model: [SECURITY.md](SECURITY.md).

## Support

- 버그 신고와 질문: https://github.com/codefoundry-io/triad-codex-dispatch/issues
- 보안에 민감한 신고: 같은 tracker에 제목 앞에 `[security]`를 붙여 올리세요.
  신고 본문에 secret이나 token은 넣지 마세요.

## 참고

- 이 플러그인은 `danger-full-access`를 쓰지 않습니다.
- 생성된 command rules는 `~/.local/bin` 또는 `TRIAD_BOOTSTRAP_BIN_DIR` 아래에
  설치된 launcher 파일만 허용합니다. 그 launcher가 설치된 plugin cache를 호출합니다.
- repair-agent permission은 선언된 TOML grant입니다. 더 넓은 parent session이나
  managed runtime override가 더 많은 권한을 허용하지 못한다는 hard isolation 증명은
  아닙니다.
- 회사/fleet 상세 설치 가이드는 `migration/` 아래에 있습니다.
