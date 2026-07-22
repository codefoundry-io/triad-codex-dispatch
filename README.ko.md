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
- bootstrap은 새로 Claude, agy, Gemini 세 provider wrapper command만 publish합니다.
  `triad-setup` 및 `triad-doctor`는 remove-only legacy cleanup 이름입니다.
- Codex permission-profile 시스템 기반 생성 profile
  (`default_permissions = "triad_leader"`, `:workspace` 확장; legacy
  `sandbox_mode` key는 쓰지 않습니다)과 wrapper launcher용 command rules — 둘 다
  기본 설치됩니다. 기본적으로 생성된 triad profile은 `approval_policy`와
  `approvals_reviewer`를 생략하므로, Codex는 owner의 기존 layered approval
  configuration을 변경 없이 상속합니다.
- classifier gap에는 설치된 read-only `triad-repair-analyzer` Custom Agent를
  사용합니다. analyzer는 proposal을 반환하고, leader는 그 proposal만 고유한 UTF-8
  JSON 파일에 기록합니다. owner가 일반 인증 terminal에서 설치된
  `triad-apply-repair` 실행 파일로 적용합니다. legacy three-agent file은 active
  repair route가 아니라 migration quarantine 또는 removal 대상입니다.
- 선택적 managed `codex-triad` shell entry
  (`TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1`) — no-prompt 자세에서는 필수 시작
  명령입니다.

## 필수 설정 (~2분)

세 단계면 기존 approval configuration을 보존하는 설치를 마칠 수 있습니다. 이 섹션 아래는
모두 선택입니다.

1. **native vendor 로그인.** leader `codex`와 사용할 worker 를 설치하고
   로그인합니다 — toolkit 은 credential 을 발급/refresh 하지 않습니다:
   - `codex` — 설치 후 `codex login`.
   - `agy` — 설치 + OAuth 로그인 (개인 사용자의 Google-family worker).
   - `claude` — Claude Code `>= 2.1.170`; bootstrap 은 binary 존재만 확인하며
     version probe 를 실행하지 않습니다.

   `git`, `python3 >= 3.12`, 그리고 그 동일 Python runtime의 Pydantic 2도
   필요합니다. runtime 의존성은 배포되는 `requirements.txt`에 선언됩니다.
   `~/.local/bin` 이 `PATH`
   에 있어야 합니다(아니면 이미 `PATH` 에 있는 디렉터리를 `TRIAD_BOOTSTRAP_BIN_DIR`
   로 지정). `gemini` 는 선택입니다 — [선택 / 고급](#선택--고급) 참고.

2. **플러그인 설치(Codex가 수행 가능).** 일반 사용자는 local clone 이 필요
   없습니다. 현재 approval 경계가 허용하면 Codex가 이 명령을 실행할 수 있습니다.

   ```bash
   codex plugin marketplace add codefoundry-io/triad-codex-dispatch --ref main
   python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","add","triad-codex-dispatch@triad-codex-dispatch","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); root=pathlib.Path(data["installedPath"]); assert root.is_absolute(); print(shlex.join([str(root / "scripts" / "bootstrap.sh"),"--install"]))'
   ```

3. **사용자가 실행하는 runtime setup.** 플러그인 installer는 임의의
   post-install 코드를 실행하지 않습니다. 2단계의 마지막 명령은 반환된
   `installedPath`로부터 Python `shlex.join`을 사용해 안전하게 인용된 절대 bootstrap
   명령을 출력합니다. 그 출력 명령을 일반 로그인 terminal에서 그대로 실행하세요.
   shebang이 포함된 shipped script라 직접 실행할 수 있습니다.

   첫 mutation 전에 스크립트는 선택된 Python이 formal review에 필요한 Pydantic 2
   API를 import할 수 있는지 검사합니다. 불가능하면 멈추고
   `python3 -m pip install -r <absolute-plugin-path>/requirements.txt`와 동등한
   argv-safe 명령을 출력합니다. 소유한 Python 환경에서 그 명령을 실행한 뒤 bootstrap을
   다시 실행하세요. Bootstrap은 Python package를 설치하지 않습니다.

   이 스크립트는 runtime profile, command rules, 세 provider wrapper command를 설치하지만
   provider 로그인이나 model probe를 실행하지 않습니다. 설치된 절대 launcher rule이 자동 승인
   하므로 세 wrapper는 반복 승인 prompt 없이 sandbox 밖에서 실행됩니다. 다른 command에는
   상속된 approval configuration이 계속 적용됩니다.

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

설치된 절대 launcher rule이 세 provider launcher를 자동 승인하며, 다른 command에는
상속된 approval configuration이 적용됩니다.
*전용 triad session 전체에서 interactive 승인 요청을 없애고 hardened wrapper 환경을
고정해 시작하려는 경우에만* 이 설정을 사용하세요.
`TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never`와 managed shell entry를 bootstrap
명령에 추가합니다.

`TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never`를 설정하면
`approval_policy = "never"`만 명시적으로 생성합니다. 이는 opt-in advanced mode로
유지되며 `approvals_reviewer`는 절대 변경하지 않습니다.

> **경고 — session 전체 적용.**
> `approval_policy=never`는 이 plugin만이 아니라 triad Codex session 전체에
> 적용됩니다. 그 session에서는 관련 없는 작업을 하지 마세요.

일반 terminal에서 두 option을 설정합니다:

```bash
export TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1
export TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never
```

그다음 새로 출력한 절대 bootstrap 명령을 다시 실행합니다. plugin을 update 또는
reinstall했다면 먼저 2단계의 출력 명령을 다시 실행하세요.

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
bootstrap 은 실행 파일 존재를 Gemini fallback candidate 로만 표시하며
인증·model·version probe를 실행하지 않습니다. 정식 review에서 이 fallback을
계산하기 전에 owner의 일반 인증 terminal에서 성공한 preflight 또는 dispatch로
실제 route를 입증해야 합니다. Gemini fallback은 request 제출 전에 agy route가
명시적으로 없거나 시작 불가능한 경우에만 사용할 수 있습니다.
`phase=pre-dispatch-settings`는 필요조건일 뿐 충분조건이 아니며, 불확실한 phase와
post-dispatch phase는 fallback 대상이 아닙니다. 직접 Gemini 요청으로 agy-first
규칙을 우회할 수 없습니다. content, schema, timeout, capacity, post-dispatch 실패는
agy 실패 경로에 남습니다.

### 기본 profile / rules opt-out

*profile 및/또는 command rules 를 설치하고 싶지 않을 때만.* profile 과 rules 는
기본 설치됩니다. 각각 명시적 `=0` 또는 `SKIP` 로 억제합니다:

일반 terminal에서 `TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=0` 및/또는
`TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=0`을 export한 뒤, 새로 출력한 절대 bootstrap
명령을 실행합니다. 동등한 skip flag는
`TRIAD_BOOTSTRAP_SKIP_CODEX_PROFILE=1`과
`TRIAD_BOOTSTRAP_SKIP_CODEX_RULES=1`입니다.

### Linux / WSL2 sandbox 지원

*Linux 또는 WSL2 에서만.* Codex sandbox 지원을 위해 `bubblewrap`(`bwrap`)을
설치하세요. installer 는 OS package 를 설치하지 않습니다.

### 보안 모델 읽기

*툴킷에 의존하기 전에 전체 threat model 을 보고 싶을 때만.*
[SECURITY.md](SECURITY.md) 참고 — 지속적인 control 은 model trust 가 아니라
privilege separation 입니다(아래 [보안](#보안-security) 에 요약).

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
- `triad-gemini-dispatch`: 제출 전 agy route unavailable이 입증된 뒤에만 쓰는
  fallback이며 Gemini business/Vertex/API-key 계정 전용.
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
| 설치된 wrapper 호출에서 Codex가 승인을 물어봄 | 생성된 절대 launcher rule이 없거나 disabled/stale 상태 | rules를 켠 상태로 새로 출력된 bootstrap 명령을 다시 실행하세요. rules를 의도적으로 opt out했다면 prompt가 정상입니다. 관련 없는 command에는 상속된 approval configuration이 계속 적용됩니다. [no-prompt 자세](#no-prompt-자세-heavy-user)도 참고하세요. |
| 디스패치가 `oauth-env`로 실패 | 워커 CLI 로그인이 만료됐거나 없음 | 해당 vendor의 native login 재실행(`claude` / `agy` OAuth, 또는 `codex login`). toolkit은 대신 재인증하지 않습니다 — 신호만 surface 하니 직접 로그인하세요. |
| gemini leg이 `IneligibleTier`로 실패 | Gemini CLI *개인* tier 폐지 | `agy`(Antigravity) leg을 쓰세요 — 개인 사용자의 Google-family leg입니다. `gemini`는 business / Vertex / API-key 계정 전용. |
| 설치/업데이트 후 새 skill이 안 보임 | 기존 Codex 세션은 새로 설치된 skill을 못 봄 | 새 Codex 세션을 시작하세요(플러그인 업데이트 뒤에는 launcher 경로 최신화를 위해 `bootstrap.sh --install` 재실행). |
| 디스패치가 non-zero로 끝났고 원인을 알고 싶음 | 숫자 exit code가 항상 권위가 있으며, 완료된 wrapper 실패는 보통 최종 분류도 출력함 | 아래 exit-code 범례를 보세요. 최종 `[wrapper] …` stderr 줄이 있으면 그 분류를 쓰고, summary 없는 초기 실패는 그대로 보존하세요. |

**Exit-code 범례**(wrapper 프로세스 exit code; 최종 wrapper summary가 있으면 그 class가
`[wrapper] <cli> <class> …` stderr 줄의 단어로 나타납니다):

| Exit | 의미 | 조치 |
|---|---|---|
| `0` | 성공 — 이어서 답변 | 없음. |
| `4` | 설정된 provider 실행 파일이 제출 전에 없거나 실행할 수 없음 | 해당 binary를 고치세요. AGY route에 한해서만 wrapper 소유 진단이 이 제출 전 실패를 함께 입증할 때 Gemini Enterprise fallback 대상입니다. |
| `64` | 재시도 후에도 server capacity 소진 | 일시적 vendor 과부하; 기다렸다 재시도. |
| `65` | 인증 / config / quota(예: `oauth-env`, `cli-subscription-cap`) | 재로그인하거나 quota reset 대기 — 분류 단어 참고. |
| `66` | 구조화 출력(`--pydantic`) 스키마 검증 실패 | sealed formal call에서는 `schema-fail is terminal for that invocation`; leader가 판단한 뒤 explicit new invocation을 만들 수 있습니다. |
| `69` | code task가 blocked / 컨텍스트 부족(codex `--task code`) | 부족한 컨텍스트를 채워 재디스패치. |

## 범위와 한계 — 이 도구가 하지 않는 것

toolkit이 어디서 멈추는지 알 수 있도록, 정직한 경계:

- **vendor 인증이나 token을 관리하지 않습니다.** token 발급/refresh, API-key
  주입, install-time provider probe가 없습니다. 각 vendor CLI의 native
  login으로 직접 로그인하며, runtime 인증 에러는 재로그인하라고 surface 됩니다.
  credential 복사, sandbox login 시도, company setup flow, authorization store는 없습니다.
- **OS 또는 Python package를 설치하지 않습니다.** vendor CLI, `python3`, 배포된
  Python requirements, (Linux/WSL2에서) `bubblewrap`은 직접 설치하며, installer는
  profile, rules, launcher만 씁니다. 선택된 Python에 Pydantic 2가 없으면 bootstrap은
  mutation 전에 멈추고 그 interpreter를 위한 정확한
  `python3 -m pip install -r .../requirements.txt` 명령을 출력합니다.
- **자기개선 분류기는 heuristic이지 oracle이 아닙니다.** 진짜 실패를 그럴듯하지만
  틀린 class로 라우팅할 수 있습니다. worst case는 *integrity* 이슈 — 지속적 라우팅
  오분류이지 코드 실행이 **아닙니다**([보안](#보안-security) 참고) — 이지만,
  `~/.config/triad-codex-dispatch/classifier-patches.json`에 적용된 delta를
  사용합니다. Bootstrap은 확정된 절대 경로를 provider/apply launcher에 고정하므로
  `TRIAD_CLASSIFIER_EXTENSION`을 바꾸면 bootstrap을 다시 실행해야 합니다.
  주기적으로 검토하세요.
- **wrapper containment은 프로세스/권한 수준이지 OS 수준 confinement이 아닙니다.**
  wrapper-containment env는 wrapper 프로세스의 path/pydantic 처리를 gate할 뿐, OS
  수준 격리 주장이 아닙니다. 경계는 격리된 `--cwd` worktree + Codex profile/rules +
  커밋 전 사용자 검토에 의존합니다.

## 업데이트

```bash
codex plugin marketplace upgrade triad-codex-dispatch
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","add","triad-codex-dispatch@triad-codex-dispatch","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); root=pathlib.Path(data["installedPath"]); assert root.is_absolute(); print(shlex.join([str(root / "scripts" / "bootstrap.sh"),"--install"]))'
```

새로 출력된 절대 명령을 실행하세요. 기본 `--install`은 default profile과 rules를
재적용하므로 opt-in flag가 있으면 실행 전에 다시 설정합니다. 업데이트 후 새 Codex
session을 시작하세요.

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
[wrapper] antigravity ok exit=0 vendor=0 elapsed=6.4s
```

이 `[wrapper] antigravity ok …` 줄이 디스패치가 동작했다는 신호입니다 — 플러그인, launcher,
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

fresh shell에서 현재 설치된 plugin 경로를 다시 확인해 managed uninstall 명령을
출력한 뒤 plugin cache를 지우세요(script가 그 cache 안에 있습니다).

```bash
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","list","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); item=next(item for item in data["installed"] if item["pluginId"]=="triad-codex-dispatch@triad-codex-dispatch"); root=pathlib.Path(item["source"]["path"]); assert root.is_absolute(); print(shlex.join([str(root / "scripts" / "bootstrap.sh"),"--remove"]))'
```

출력된 절대 removal 명령을 실행한 다음 plugin registration을 제거합니다.

```bash
codex plugin remove triad-codex-dispatch@triad-codex-dispatch
codex plugin marketplace remove triad-codex-dispatch
```

`--remove`(alias `--uninstall`)는 wrapper launcher, 설치된
`triad-repair-analyzer`, managed profile과 command rules, managed `codex-triad`
shell entry를 삭제합니다. 예전 설치가 남긴 legacy three-agent TOML도 함께
삭제합니다. 학습된 classifier patch는 의도적으로 보존됩니다. 이는 managed
uninstall 범위 밖이며, owner가 학습된 routing을 폐기하려는 경우에만 별도로
삭제해야 합니다.

## Custom Subagent

classifier repair는 설치된 read-only `agent_type="triad-repair-analyzer"`와
`fork_turns="none"`을 사용합니다. `task_name`은 label일 뿐이며, model, effort,
sandbox는 설치된 agent가 소유합니다. agent는 proposal 또는 escalation만 반환하고
patch를 적용하지 않습니다. leader는 proposal만 고유한 UTF-8 JSON 파일로 저장한 뒤
Python `shlex.join`으로 argv list에서 owner command를 만듭니다:

`triad-apply-repair --cli <cli> --proposal-file <absolute-path>`.

이 설치된 실행 파일은 owner의 일반 인증 terminal에서 실행합니다. selector가 없으면
그 terminal에서 bootstrap을 실행하고 Codex를 재시작하며, generic agent로 낮추지
않습니다. run log는 age-floor cleanup까지 남아 있습니다.

직접 만든 Codex custom subagent가 triad dispatch skill을 호출해야 한다면 Codex
`skills.config`에 필요한 `SKILL.md` 경로를 명시하세요. 경로는 live
`codex plugin list --json` 출력의 현재 설치 plugin `source.path` 아래 skill 파일을
가리키면 됩니다.

custom-agent TOML을 바꾼 뒤에는 새 Codex session을 시작하세요.

## Runtime Log 및 Local Data

Runtime telemetry는 설치된 plugin의 `bin/_logs/<cli>/` 아래에 local artifact로
남습니다. `audit.jsonl`은 redacted argv, prompt length, status, stdout/stderr
앞 500자, structured-output 존재 여부와 길이만 저장합니다. failure run log는 repair
untrusted repair evidence를 위해 전체 prompt와 vendor transcript를 저장하고 age-floor cleanup까지
남습니다. 이 파일들은 민감한 데이터로 보고 필요하면 `bin/_logs/`를 지우세요.

formal sealed call에서는 provider resolution 전에 `PACKET_SHA256, SHA256SUMS,
and INPUT_SHA256SUMS`를 검증합니다. dispatch driver에 도달한 모든 일반
non-`--repair-mode` wrapper invocation은 provider 실행 전에 3,600 seconds보다 오래된
managed UUID/file-IPC entry를 best-effort cleanup합니다. Antigravity는
`--preflight-only` 전에도 cleanup합니다. cleanup errors never block dispatch이고 perfect
garbage collector를 주장하지 않습니다. sealed formal schema
failure는 terminal입니다: `schema-fail is terminal for that invocation`; leader는
판단 뒤 explicit new invocation을 만들 수 있습니다. 이 schema rule은 documented
same-prompt capacity/transport recovery 또는 Antigravity headless soft-deny
adaptation을 비활성화하지 않습니다. 이 경로들은 review prompt와 packet identity를
유지하며 replacement formal leg를 만들지 않습니다.

Antigravity settings는 agy 호출 중 `~/.gemini/antigravity-cli/` 아래에서
transaction으로 다룹니다. 같은 시간에 agy permission을 편집하거나 다른
Antigravity settings 변경을 실행하지 마세요.

## 보안 (Security)

지속적인 control은 model trust가 아니라 **privilege separation**입니다: 설치된
read-only analyzer가 untrusted run log를 읽고 proposal만 반환하며, owner-run
결정적 `triad-apply-repair`가 그 proposal을 검증하고 적용합니다. 전체 threat model:
[SECURITY.md](SECURITY.md).

## Support

- 버그 신고와 질문: https://github.com/codefoundry-io/triad-codex-dispatch/issues
- 보안에 민감한 신고: 같은 tracker에 제목 앞에 `[security]`를 붙여 올리세요.
  신고 본문에 secret이나 token은 넣지 마세요.

## 참고

- 이 플러그인은 `danger-full-access`를 쓰지 않습니다.
- 생성된 command rules는 `~/.local/bin` 또는 `TRIAD_BOOTSTRAP_BIN_DIR` 아래의 정확한
  절대 launcher 파일만 자동 허용합니다. launcher가 argv를 검증하고 설치된 plugin cache를
  호출하며, 다른 command에는 profile의 일반 approval policy가 적용됩니다.
- 정확히 설치된 `triad-repair-analyzer`는 pinned read-only sandbox를 사용하며,
  proposal 또는 escalation만 반환하고 classifier change를 적용하지 않습니다.
