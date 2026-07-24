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
- 세 managed wrapper launcher의 정확한 command rules. `decision = "prompt"`를
  사용하고 일반 `codex` session에서 동작합니다. Bootstrap은 전용 profile을
  설치하거나 owner의 approval, reviewer, model, reasoning, sandbox 설정을 교체하지
  않습니다.
- classifier gap에는 설치된 read-only `triad-repair-analyzer` Custom Agent를
  사용합니다. analyzer는 proposal을 반환하고, leader는 그 proposal만 고유한 UTF-8
  JSON 파일에 기록합니다. owner가 일반 인증 terminal에서 설치된
  `triad-apply-repair` 실행 파일로 적용합니다. legacy three-agent file은 active
  repair route가 아니라 migration quarantine 또는 removal 대상입니다.

## 필수 설정 (~2분)

세 단계면 일반 Codex에서 사용할 수 있는 설치를 마칩니다. 이 섹션 아래는 모두
선택입니다.

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

   Bootstrap은 installer-selected Python을 생성된 launcher에 고정합니다.
   credential-compatible/user-site mode에서는 Codex와 launcher를 trusted HOME에서
   시작해야 합니다. HOME이 선택한 user site의
   sitecustomize.py/usercustomize.py는 launcher scrub 전에 실행될 수 있습니다.
   Installer는 provider login workflow를 보존하는 경우에만 trusted isolated Python
   environment를 대신 선택할 수 있습니다.

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

   첫 mutation 전에 스크립트는 선택된 Python이 toolkit에서 사용하는 Pydantic 2
   API를 import할 수 있는지 검사합니다. 불가능하면 멈추고
   `python3 -m pip install -r <absolute-plugin-path>/requirements.txt`와 동등한
   argv-safe 명령을 출력합니다. 소유한 Python 환경에서 그 명령을 실행한 뒤 bootstrap을
   다시 실행하세요. Bootstrap은 Python package를 설치하지 않습니다.

   이 스크립트는 정확한 command rules와 세 provider wrapper command를 설치합니다.
   또한 `$CODEX_HOME/config.toml`에 provenance-marked repair-analyzer 등록을 추가하고,
   owner-authored policy가 없을 때 provenance-marked loader-environment guard를
   추가합니다. 다른 config key는 모두 보존하며, owner가 작성하거나 편집한 environment
   policy는 warning과 함께 그대로 두고 `--remove`는 정확한 managed block만 제거합니다.
   전용 profile을 설치하거나 owner의 Codex approval/reviewer/sandbox key를 변경하지
   않으며, provider 로그인이나 model probe도 실행하지 않습니다. 정확한 절대 launcher
   rule은 `prompt`를 사용합니다.

   Bootstrap은 repair lifecycle의 analyzer, registration,
   `triad-apply-repair` transaction이 성공한 뒤에만 provider wrapper command를
   publish합니다. 늦은 repair-registration 실패가 발생하면 provider launcher,
   `triad-apply-repair`, analyzer/registration, command rules, legacy shell entry는
   publish되지 않습니다.

   Agent Review를 자동으로 사용하려면 다음 단순 설정을 사용합니다:

   ```toml
   approval_policy = "on-request"
   approvals_reviewer = "auto_review"
   ```

   기존 granular policy를 유지한다면 다른 category 선택은 그대로 두고
   `granular.rules = true`와 `granular.sandbox_approval = true`인지 확인해야 합니다.
   그래야 정확한 rule prompt와 sandbox escalation이 Agent Review에 도달하기 전에
   자동 거절되지 않습니다. `approvals_reviewer = "user"`이면 wrapper는 동작하지만
   사람이 승인합니다. `approval_policy = "never"`이면 Agent Review는 실행되지 않습니다.

   이 설정은 OpenAI의 [Auto-review](https://learn.chatgpt.com/docs/sandboxing/auto-review),
   [rules](https://learn.chatgpt.com/docs/agent-configuration/rules),
   [approval policy](https://learn.chatgpt.com/docs/config-file/config-advanced#approval-policies-and-sandbox-modes)
   문서를 따릅니다.

   플러그인은 `[auto_review].policy`를 설치하지 않습니다. 그러면 owner의 reviewer
   지시를 교체할 수 있고 managed policy가 더 높은 precedence를 갖기 때문입니다.
   명시적 owner 요청과 정확한 rule justification이 기본 reviewer policy에 필요한
   authorization context를 제공합니다. 정확한 동작 하나가 거절되면 owner는 `/approve`로
   그 기록 한 건만 선택할 수 있으며 broad allow rule로 바꾸면 안 됩니다.

   Automatic review는 실행 시점 security check이지 owner workflow authorization이
   아닙니다. Commit, push, plugin 또는 dependency 설치, release, publication은 각각 별도의
   owner 결정이며, leader는 `approvals_reviewer = "auto_review"`가 활성화되어 있다는 이유만으로
   이를 시작하면 안 됩니다.

   > **배치 불변식 (hard).** bootstrap 은 설치 대상이 들어 있는 디렉터리가 아니라
   > 작업할 project workspace 에서 실행하세요. bootstrap 은 command rules와
   > provenance-marked config registration을 `$CODEX_HOME`(기본 `~/.codex/`), classifier patch 를
   > `~/.config/triad-codex-dispatch/`, launcher 를 `~/.local/bin`(또는
   > `TRIAD_BOOTSTRAP_BIN_DIR`)에 설치합니다. 이 대상과 그것이 실행하는 모든 것
   > (plugin cache, `python3` runtime)은 sandbox-writable root 밖에 있어야 하며,
   > 어느 하나라도 실행 디렉터리(예: `$HOME`) 안으로 resolve 되면 hard-fail 합니다.

   일반 경로에는 의도적으로 전용 permission profile이 없습니다. 일반 `codex`는
   `$HOME`이나 `~/.local/bin`, `$CODEX_HOME`, plugin cache의 상위 디렉터리가 아니라
   실제 project/workspace root에서 시작하세요. 이후 workspace-write session의 root가
   managed executable 위에 잡히면 그것을 다시 쓸 수 있으며, 설치 시 placement 검사는
   미래 session root까지 강제하지 못합니다. 매 session의 exec-target deny가 필요한
   owner에게만 legacy profile이 명시적 migration option으로 남습니다.

   설치 후 대상 workspace 에서 일반 Codex session 을 새로 시작합니다:

   ```bash
   codex
   ```

   `/status`로 활성 approval policy를 확인하고, project/profile/managed layer가 예상
   reviewer를 바꾼 경우 `/debug-config`로 precedence를 확인하세요.

이게 필수 경로의 전부입니다. repair 는 필요할 때만 surface 되는 수동 read-only
단계입니다([Custom Subagent](#custom-subagent) 와 [보안](#보안-security) 참고).

## 선택 / 고급

이 섹션의 어떤 것도 일반 개인 설치에는 필요 없습니다. 각 하위 섹션의 "다음 경우에만
하세요…" 조건이 해당될 때만 보세요.

### enterprise Gemini worker

*business / Vertex / API-key Gemini 계정이 있을 때만.* `gemini` 를 설치하고
로그인하세요; 개인 Google-family 사용자는 `agy` 를 쓰세요. 팀이 bootstrap 에서
필수로 요구하려면 `TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1` 을 설정합니다.
bootstrap 은 실행 파일 존재를 Gemini fallback candidate 로만 표시하며
인증·model·version probe를 실행하지 않습니다. 일반/비정식 Gemini fallback은
request 제출 전에 agy route가 명시적으로 없거나 시작 불가능한 경우에만 사용할
수 있습니다.
`phase=pre-dispatch-settings`는 필요조건일 뿐 충분조건이 아니며, 불확실한 phase와
post-dispatch phase는 fallback 대상이 아닙니다. 직접 Gemini 요청으로 agy-first
규칙을 우회할 수 없습니다. content, schema, timeout, capacity, post-dispatch 실패는
agy 실패 경로에 남습니다. 정식 Gemini fallback은 별도 gate이며, 배포본에는 이를
허용할 enforcement proof가 없고 automatic probe도 실행하지 않습니다. 정식 admission에
필요한 owner-recorded proof는
[formal reviewer routing contract](skills/triad-cross-family-review/references/reviewer-routing.md)를
따릅니다.

### 기본 rules opt-out

*command rules 를 설치하고 싶지 않을 때만.*

일반 terminal에서 `TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=0`을 export한 뒤, 새로
출력한 절대 bootstrap 명령을 실행합니다. 동등한 skip flag는
`TRIAD_BOOTSTRAP_SKIP_CODEX_RULES=1`입니다. 이 opt-out은 policy-matched launcher도
활성화할 configured rules path가 없을 때만 managed loader-environment guard를
함께 건너뜁니다. 그 path에 owner-maintained rules가 이미 있으면 bootstrap은
rules를 보존하고, launcher를 계속 활성화할 수 있으므로 guard도 유지합니다.
repair-analyzer 등록은 별도입니다.

### Linux / WSL2 sandbox 지원

*Linux 또는 WSL2 에서만.* Codex sandbox 지원을 위해 `bubblewrap`(`bwrap`)을
설치하세요. installer 는 OS package 를 설치하지 않습니다.

### 보안 모델 읽기

*툴킷에 의존하기 전에 전체 threat model 을 보고 싶을 때만.*
[SECURITY.md](SECURITY.md) 참고 — 지속적인 control 은 model trust 가 아니라
privilege separation 입니다(아래 [보안](#보안-security) 에 요약).

### bootstrap 재실행 참고

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

### pre-0.2.529 업그레이드

이전 설치가 남긴 남아 있는 managed legacy profile 또는 shell artifact가
있으면 일반 `--install`은 정확한 경로를 경고하고 자동 삭제를 하지 않습니다.
선택하지 않은 legacy path가 unsafe 또는 unreadable이면 bootstrap은 거부 상세와
경로를 warning으로 표시하고, 그 path를 따라가거나 변경하지 않은 채 선택된 일반
artifact 설치를 계속합니다. 선택된 profile, rules, shell entry의 unsafe preflight는
계속 fatal입니다.

Legacy profile이 필요하면 `TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1`을 설정하세요.
Legacy shell entry에는 `TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1`과
`TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1`이 모두 필요하며 shell flag만 설정하면
거부됩니다. 이 compatibility path는 명시적 legacy opt-in입니다. 또는 의도적으로
`--remove` 후 일반 재설치를 실행하세요. 일반 `codex`가 정상 시작 경로이며, 폐기된
no-prompt `allow` posture는 복원되지 않습니다.
pre-0.2.529에서 처음에는 없었던 config에 stale original config existed = true
provenance가 남아 있으면, 진짜로 미리 존재하던 빈 파일과 구분할 수 없으므로 안전한
zero-byte 파일로 남겨 둡니다.

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
codex
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

### Shared-directory cross-family review

Owner가 `triad-cross-family-review`를 명시적으로 호출하면 그 한 번의 요청이 명시된
source scope에 대한 Claude, Google-family, fresh Codex review leg을 authorize합니다.
Leader는 이 authorization을 한 번 기록하고 leg마다 다시 묻지 않습니다. 그래도
provider-visible input에서는 credential, token, cookie, authentication file,
environment dump, provider log, 관련 없는 path를 제외해야 합니다.

정식 plan 및 pre-merge 3-패밀리 gate는 one leader-prepared shared review directory를
사용합니다. 이 directory에는 current approved production source, configuration, and
documentation만 둡니다. Project instruction 또는 owner가 exact test-source exclusions를
제공해야 하며 이를 추론하지 않습니다. 경계가 없으면 stop and ask the owner를
수행합니다. 일반 SDD 구현 리뷰는 관련 test source를 포함하고, 다른 advisory review는
별도로 owner가 승인한 data scope를 따릅니다.
Normal SDD implementation review includes relevant test source.

Every leg receives the same directory and task. No prompt inlines a diff or file body.
Leader는 dispatch 전에 one simple content digest를 기록하고 모든 required leg이 끝난
뒤 다시 비교합니다. 달라지면 round를 무효화합니다. 정식 gate 전에 모든 test failure를
production defect, test-case defect, intentional specification change 중 하나로
분류하고 해결하거나 승인합니다. Reviewer는 candidate code, test, build, hook,
generated script를 실행하지 않습니다.
Before a formal gate, classify every test failure as production defect, test-case defect,
or intentional specification change and resolve or approve it.

이 계약은 credential, token, cookie, authentication file, environment dump, provider
log, 관련 없는 path를 provider-visible input에서 제외한다는 보안 경계를 바꾸지
않습니다. Commit, push, install/update, merge, release, publication은 계속 각각 별도의
owner authorization이 필요합니다.

일반 code-write dispatch는 대상 workspace에서 실행하세요. 경로 containment는
opt-in입니다: `TRIAD_WRAPPER_ALLOWED_ROOTS`가 설정된 경우에만 wrapper가 trusted root
밖의 `--cwd` / `--prompt-file`을 거부합니다. 기본은 경로를 제약하지 않으므로
approved-path containment는 provider가 실제로 enforce하지 않는 한 prompt-controlled입니다.
그 외 경계는 선택한 `--cwd` worktree, 요청한 wrapper sandbox, 일반 Codex sandbox,
정확한 rules에 의존합니다.

## 문제 해결 (Troubleshooting)

| 증상 | 원인 | 해결 |
|---|---|---|
| Wrapper 호출이 automatic review 대신 수동 승인을 기다림 | 활성 reviewer가 `user`이거나 더 높은 precedence layer가 reviewer를 바꿨거나 생성 rule이 없거나 stale함 | `/status`와 `/debug-config`를 확인하고, 원한다면 적용 layer에서 `approvals_reviewer = "auto_review"`를 복구하고, stale rule이면 bootstrap을 다시 실행한 뒤 일반 `codex`를 재시작하세요. |
| Wrapper rule이 Agent Review 전에 자동 거절됨 | 활성 granular policy의 `rules = false` 또는 `sandbox_approval = false`, 혹은 approval이 `never`임 | 다른 granular 선택은 보존하면서 두 category를 활성화하고 재시작하거나 `approval_policy = "on-request"`를 사용하세요. |
| Automatic review가 wrapper 호출을 거부함 | Authorization이 없거나 범위를 벗어났거나, provider-visible input에 제외 대상 credential material이 있거나, reviewer가 다른 unsafe 조건을 찾음 | Input 범위를 줄이거나 필요한 owner authorization을 받으세요. Owner는 정확한 기록 한 건을 `/approve`로 선택할 수 있지만 broad allow rule을 설치하면 안 됩니다. |
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
| `65` | 인증 / config / quota 또는 손실된 AGY 응답(예: `oauth-env`, `cli-subscription-cap`, `truncated-answer`) | `truncated-answer`이면 repair하거나 Gemini fallback으로 전환하지 말고 bounded, compact result를 요청하는 새 호출을 만드세요. 다른 분류는 재로그인하거나 quota reset을 기다리세요. |
| `66` | 구조화 출력(`--pydantic`) 스키마 검증 실패 | `schema-fail is terminal for that invocation`; leader가 판단한 뒤 explicit new invocation을 만들 수 있습니다. shared-directory formal path는 legacy packet-bound schema를 요구하지 않습니다. |
| `67` | Codex가 제출된 output schema를 거부함(`schema-rejected`) | schema/configuration 불일치를 확인하고 explicit new invocation을 만드세요. |
| `1` | Wrapper가 답변을 추출하지 못했거나(`extraction-error`) 분류가 `unknown`임 | 최종 wrapper 분류와 provider 진단을 확인한 뒤 적절히 재시도하거나 escalation하세요. |

## 범위와 한계 — 이 도구가 하지 않는 것

toolkit이 어디서 멈추는지 알 수 있도록, 정직한 경계:

- **vendor 인증이나 token을 관리하지 않습니다.** token 발급/refresh, API-key
  주입, install-time provider probe가 없습니다. 각 vendor CLI의 native
  login으로 직접 로그인하며, runtime 인증 에러는 재로그인하라고 surface 됩니다.
  credential 복사, sandbox login 시도, company setup flow, authorization store는 없습니다.
- **OS 또는 Python package를 설치하지 않습니다.** vendor CLI, `python3`, 배포된
  Python requirements, (Linux/WSL2에서) `bubblewrap`은 직접 설치하며, installer는
  정확한 rules, launcher, provenance-marked loader 환경 방어를 쓰되 다른 owner config
  key는 보존합니다. 선택된 Python에 Pydantic 2가 없으면 bootstrap은
  mutation 전에 멈추고 그 interpreter를 위한 정확한
  `python3 -m pip install -r .../requirements.txt` 명령을 출력합니다.
- **자기개선 분류기는 heuristic이지 oracle이 아닙니다.** 진짜 실패를 그럴듯하지만
  틀린 class로 라우팅할 수 있습니다. worst case는 *integrity* 이슈 — 지속적 라우팅
  오분류이지 코드 실행이 **아닙니다**([보안](#보안-security) 참고) — 이지만,
  `~/.config/triad-codex-dispatch/classifier-patches.json`에 적용된 delta를
  주기적으로 검토하세요. Bootstrap은 확정된 절대 경로를 provider/apply launcher에 고정하므로
  `TRIAD_CLASSIFIER_EXTENSION`을 바꾸면 bootstrap을 다시 실행해야 합니다.
- **wrapper containment은 프로세스/권한 수준이지 OS 수준 confinement이 아닙니다.**
  wrapper-containment env는 wrapper 프로세스의 path/pydantic 처리를 gate할 뿐, OS
  수준 격리 주장이 아닙니다. 경계는 process permission, 선택한 `--cwd` worktree,
  Codex rules, 커밋 전 사용자 검토에 의존합니다.

## 업데이트

```bash
codex plugin marketplace upgrade triad-codex-dispatch
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","add","triad-codex-dispatch@triad-codex-dispatch","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); root=pathlib.Path(data["installedPath"]); assert root.is_absolute(); print(shlex.join([str(root / "scripts" / "bootstrap.sh"),"--install"]))'
```

새로 출력된 절대 명령을 실행하세요. 기본 `--install`은 전용 profile 없이 정확한
rules, launcher, managed loader 환경 방어를 재적용합니다. legacy opt-in flag가 있으면
실행 전에 다시 설정합니다. 업데이트 후 일반 Codex session을 새로 시작하세요.

## 설치 검증

### 플러그인 전용 smoke test (clone 불필요)

일반 경로입니다 — 아무것도 clone 하지 않고 toolkit 이 살아 있는지 확인합니다. 대상
workspace 에서 리더를 시작하고 codex 에게 사소한 Google-family dispatch 를 시킵니다:

```bash
codex
```

그 세션에서:

> triad-antigravity-dispatch 로 agy 에게 물어봐: `git rebase --onto` 는 무슨 일을 해? 한 문단으로.

agy 의 답과 함께 stderr 에 한 줄 성공 요약이 뜹니다:

```
[wrapper] antigravity ok exit=0 vendor=0 elapsed=6.4s
```

이 `[wrapper] antigravity ok …` 줄이 디스패치가 동작했다는 신호입니다 — 플러그인, launcher,
rules 가 모두 연결된 것입니다. `ok` 는 분류이며, 다른 값(예: `oauth-env`,
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

`--remove`는 wrapper launcher, 설치된
`triad-repair-analyzer`, `triad-apply-repair`, 정확한 command rules, 예전 release가 만든 provenance-matched
legacy profile/shell entry를 삭제합니다. 예전 설치가 남긴 legacy three-agent TOML도 함께
삭제합니다. `$CODEX_HOME/config.toml`에서는 managed repair-analyzer registration과
정확한 managed `[shell_environment_policy]` block을 제거합니다. 이 둘이 유일한
managed content이고 owner content가 남지 않으면, `config.toml`은 설치 전에
존재하지 않았던 경우에만 삭제합니다. 설치 전에 존재했던 파일과 owner content는
보존합니다. 즉 absent-file restoration은 provenance-marked managed registration과
environment-policy block이 둘 다 그대로 남아 있는 경우에만 적용됩니다.
학습된 classifier patch는 의도적으로 보존됩니다. 이는 managed
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
남습니다. `audit.jsonl`은 redacted argv, prompt length, status,
structured-output 존재 여부와 길이를 저장합니다. Audit retention 기준으로
generated-launcher/redacted mode는 redacted stdout/stderr와 원래 길이를 저장합니다.
500자 cap은 model-output field에 적용되며 이 stream field에는 적용되지 않습니다.
unredacted non-launcher path는 전체 stdout/stderr stream을 보존할 수 있습니다.
failure run log는 untrusted repair evidence를 위해 전체 prompt와 vendor transcript를
저장하고 age-floor cleanup까지 남습니다. 이 파일들은 민감한 데이터로 보고 필요하면
`bin/_logs/`를 지우세요.

Worktree-first review는 packet-bound `FormalReview` schema, sealed-packet flag,
source snapshot을 사용하지 않습니다. 이 option의 legacy wrapper support는 명시적
compatibility 용도로 남을 수 있지만 일반 또는 formal worktree review의 일부가 아니며
gate prerequisite도 아닙니다.

Dispatch driver에 도달한 모든 일반 non-`--repair-mode` wrapper invocation은 provider
실행 전에 3,600 seconds보다 오래된 managed UUID/file-IPC entry를 best-effort
cleanup합니다. Antigravity는 `--preflight-only` 전에도 cleanup합니다. Cleanup error는
dispatch를 막지 않으며 perfect garbage collector를 주장하지 않습니다.

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
  절대 launcher 파일만 match합니다. Launcher가 argv를 검증하고 설치된 plugin cache를
  호출합니다. Rules는 항상 `prompt`를 사용합니다. `approval_policy=never`이면
  Agent Review가 비활성화되어 fail-closed 합니다.
- Automatic review는 commit, push, install, release, publication에 대한 owner workflow
  authorization을 제공하지 않습니다.
- 정확히 설치된 `triad-repair-analyzer`는 pinned read-only sandbox를 사용하며,
  proposal 또는 escalation만 반환하고 classifier change를 적용하지 않습니다.
