# triad-codex-dispatch

[설치와 개인 설정](docs/installation.ko.md): 일반 마켓플레이스 또는 Git 다운로드 후
로컬 설치를 선택합니다. 최신 공개 버전은 `main`을 사용하며,
[v0.2.556](https://github.com/codefoundry-io/triad-codex-dispatch/releases/tag/v0.2.556)에서
버전별 릴리스와 다운로드 체크섬을 확인할 수 있습니다.

[English README](README.md)

**AI 코딩 어시스턴트는 자기 리뷰어와 blind spot 을 공유합니다.** codex 에게 codex 의
결과물을 검토시키면 같은 framing 을 물려받습니다 — 버그를 만든 추론이 곧 그 버그를
리뷰하는 추론입니다. triad-codex-dispatch 는 **다른 모델 패밀리** 로부터 두 번째, 세
번째 의견을 받아줍니다: codex 가 리더로 남아 **Claude Code**(Anthropic)와
**AGY 또는 Gemini CLI**(Google)를 단발(single-shot) 워커로 디스패치하고, 위험한
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
- bootstrap은 Claude, agy, Gemini 세 provider wrapper와 `review_round.py`
  selector launcher를 publish합니다.
  `triad-setup` 및 `triad-doctor`는 remove-only legacy cleanup 이름입니다.
- 정식 Google review는 어떤 family도 시작하기 전에 route를 선택해 고정합니다.
  AGY를 우선하며 개인 Google Sign-In에는 AGY가 필요합니다. owner가 Gemini
  Enterprise OAuth를 선택했고 AGY 실행 파일이 없을 때만 기존 Gemini CLI wrapper로
  즉시 넘어갑니다. AGY를 선택하거나 시작한 뒤의 실패는 Gemini fallback을 일으키지
  않습니다. 명시적 `--project`가 없는 AGY route는 `--sandbox read-only`
  호출 동안 일시적 global-settings transaction으로
  원래 바이트를 복원합니다. 기본 Formal AGY는 기존 다섯 deny에 `read_url(*)`를
  추가하고 headless 자동 승인 flag를 사용하지 않습니다. 동일한 formal deny
  lease는 동시 실행할 수 있고 raw/formal 목록은 격리됩니다. Raw 조사는 기존 웹
  기능과 버전별 headless 호환 처리를 유지하며 `AGY_NO_HEADLESS_AUTOAPPROVE=1`로
  해당 처리를 끌 수 있습니다. REVIEW는 기본적으로 웹을 금지합니다. 사용자가 해당 리뷰에 직접 요청하면
  [모든 leg에 웹 검증을 허용](skills/triad-cross-family-review/references/review-web.md)합니다. AGY의 MCP 호출도 차단합니다. Gemini 구버전 CLI
  경로는 explicit CLI Auto와 native Plan Mode를 요청하고,
  mode-independent packaged read/search-only user policy를 fail-closed enforcement
  boundary로 사용합니다. 기존 조직 OAuth cache를 사용하며 경쟁
  API-key/ADC/Vertex/model selector는 값을 읽지 않고 제거합니다. effective mode와
  runtime model은 `unexposed`입니다. 이는 OS 수준 confinement가 아니며
  round-integrity mutation detection은 별도 검사입니다. B 전용 기본 Gemini policy는 두 웹
  도구를 명시적으로 거부합니다. 조직 정책의 우선순위를 포함한 실제 적용 여부는
  별도 라이브 검증 항목으로 유지합니다.
- classifier gap에는 fresh native proposal-only child를 사용합니다. owner는 동일한
  인증된 로그인 터미널에서 bootstrap이 출력한
  `python3 bin/apply_patch.py ... --classifier-file ...` 명령으로 검증된 proposal을
  적용합니다. repair Custom Agent나 apply launcher는 설치하지 않습니다.

## 필수 설정 (~2분)

세 단계면 일반 Codex에서 사용할 수 있는 설치를 마칩니다. 이 섹션 아래는 모두
선택입니다.

1. **native vendor 로그인.** 개발에 사용한 동일한 인증된 로그인 터미널과 project
   worktree를 사용합니다. leader `codex`와 사용할 worker 를 설치하고
   로그인합니다 — toolkit 은 credential 을 발급/refresh 하지 않습니다:
   - `codex` — 설치 후 `codex login`.
   - `agy` — 우선 Google-family worker이며 개인 Google Sign-In에는 필수.
   - `gemini` — AGY가 없는 Gemini 구버전 CLI 경로에서만 필수. 기존 Gemini Enterprise OAuth 인증을 사용합니다.
   - `claude` — Claude Code `>= 2.1.170`; bootstrap 은 binary 존재만 확인하며
     version probe 를 실행하지 않습니다.

   `git`, `python3 >= 3.12`, 그리고 그 동일 Python runtime의 Pydantic 2와 `jsonschema>=4.26,<5`도
   필요합니다. runtime 의존성은 배포되는 `requirements.txt`에 선언됩니다.
   `~/.local/bin` 이 `PATH`
   에 있어야 합니다(아니면 이미 `PATH` 에 있는 디렉터리를 `TRIAD_BOOTSTRAP_BIN_DIR`
   로 지정). `agy` 또는 `gemini` 중 하나 이상은 설치되어야 합니다.

   Bootstrap은 installer-selected Python을 생성된 launcher에 고정합니다.
   credential-compatible/user-site mode에서는 Codex와 launcher를 trusted HOME에서
   시작해야 합니다. HOME이 선택한 user site의
   sitecustomize.py/usercustomize.py는 launcher scrub 전에 실행될 수 있습니다.
   Installer는 provider login workflow를 보존하는 경우에만 trusted isolated Python
   environment를 대신 선택할 수 있습니다.

2. **설치 경로 선택.** 아래 명령은 일반 마켓플레이스의 공개 버전을 설치합니다.
   Git 로컬 설치나 특정 커밋 고정은 [설치와 개인 설정](docs/installation.ko.md)을
   따르세요. 현재 approval 경계가 허용하면 Codex가 이 명령을 실행할 수 있습니다.

   ```bash
   codex plugin marketplace add codefoundry-io/triad-codex-dispatch --ref main
   python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","add","triad-codex-dispatch@triad-codex-dispatch","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); root=pathlib.Path(data["installedPath"]); assert root.is_absolute(); print(shlex.join(["bash",str(root / "scripts" / "bootstrap.sh"),"--install"]))'
   ```

3. **사용자가 실행하는 runtime setup.** 플러그인 installer는 임의의
   post-install 코드를 실행하지 않습니다. 2단계의 마지막 명령은 반환된
   `installedPath`로부터 Python `shlex.join`을 사용해 안전하게 인용된 절대 bootstrap
   명령을 출력합니다. 그 출력 명령을 일반 로그인 terminal에서 그대로 실행하세요.
   실행 권한 비트에 의존하지 않도록 출력된 `bash` 명령을 사용합니다.

   첫 mutation 전에 스크립트는 선택된 Python이 toolkit에서 사용하는 Pydantic 2 및 jsonschema Draft 2020-12
   API를 import할 수 있는지 검사합니다. 불가능하면 멈추고
   `python3 -m pip install -r <absolute-plugin-path>/requirements.txt`와 동등한
   argv-safe 명령을 출력합니다. 소유한 Python 환경에서 그 명령을 실행한 뒤 bootstrap을
   다시 실행하세요. Bootstrap은 Python package를 설치하지 않습니다.

   이 스크립트는 three provider wrapper launchers와 packaged script를 재사용하는
   review-round selector launcher를 하나의 staged all-or-nothing
   command group으로 설치합니다. Codex permission profile, command rule,
   repair-agent registration, pre-spawn `[shell_environment_policy]`는 설치하지
   않습니다. owner-authored `config.toml`, rule, permission setting, credential,
   관련 없는 파일을 보존합니다.

   Bootstrap은 install-resolved classifier path를 provider launcher에 고정하고,
   동일한 explicit `--classifier-file`을 포함한 login-shell
   `python3 bin/apply_patch.py` owner argv를 Python `shlex.join`으로 출력합니다.
   설치된 apply launcher는 없고 ambient default를 다시 계산하지 않습니다.

   **TRIAD를 사용하기 전에 Codex host 권한 모드를 선택하세요.** Codex가 실행하는
   모든 TRIAD lifecycle/provider 명령과 TRIAD test/development 명령은 Codex workspace
   sandbox 밖에서 실행합니다. 이 바깥쪽 host 경계는 AGY의 provider-native read-only
   sandbox 및 Gemini의 native Plan Mode + packaged read/search-only policy와 별개입니다.

   대화형 workspace 정책을 사용하세요. 해당
   profile이 제공되면 Desktop 또는 CLI `/permissions`에서 Workspace Write / on-request를
   선택합니다. 같은 설정을 지속하려면 user 범위 `~/.codex/config.toml` 또는 신뢰한
   프로젝트의 `.codex/config.toml`에 둡니다.

   ```toml
   sandbox_mode = "workspace-write"
   approval_policy = "on-request"
   approvals_reviewer = "user"
   ```

   기존 설정을 보존하고 같은 키를 중복 추가하지 말고 해당 값만 수정하세요.
   위 최상위 키는 `[table]` 헤더보다 앞에 둡니다. 이미 permission profile을
   사용한다면 해당 설정 방식을 유지하세요.

   `approvals_reviewer = "user"`는 outside-sandbox 요청마다 사람의 Yes/No 결정을
   유지합니다. 조직 정책이 agent reviewer를 허용하는 경우에만 이 필드만 바꿉니다.

   ```toml
   approvals_reviewer = "auto_review"
   ```

   leader는 처음부터 outside-sandbox 실행 승인을 요청하며, 실패가 확실한
   workspace-sandbox 시험 명령으로 한 번 낭비하지 않습니다. `auto_review`는 요청을
   검토하는 주체만 바꾸며 권한을 부여하지 않습니다. Project config는 신뢰한
   프로젝트에서만 로드됩니다. 새 permission-profile 시스템을 사용한다면
   `/permissions`에서 interactive workspace profile을 선택하고 legacy `sandbox_mode`
   키와 섞지 마세요. OpenAI 공식 [sandbox](https://learn.chatgpt.com/docs/sandboxing),
   [configuration](https://learn.chatgpt.com/docs/config-file/config-basic),
   [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference),
   [plugin](https://learn.chatgpt.com/docs/plugins) 문서를 따릅니다.

   OpenAI 문서상 plugin capability에는 Codex host의 sandbox와 approval policy가
   적용되며, plugin-level install-time sandbox Yes/No grant는 문서화되어 있지 않습니다.
   Connector 인증 prompt는 별개입니다. 따라서 이 plugin은 host permission mode를
   선택하거나 설치하지 않습니다. Native permission 처리는 실행 시점 경계이지 owner
   workflow authorization이 아닙니다. Commit, push, plugin/dependency 설치, release,
   publication은 각각 별도 owner 결정이며, leader는
   `approvals_reviewer = "auto_review"`가 활성화되어 있다는 이유만으로 이를 시작하면
   안 됩니다.

   > **배치 불변식 (hard).** bootstrap 은 설치 대상이 들어 있는 디렉터리가 아니라
   > 작업할 project workspace 에서 실행하세요. bootstrap 은 classifier patch 를
   > `~/.config/triad-codex-dispatch/`, launcher 를 `~/.local/bin`(또는
   > `TRIAD_BOOTSTRAP_BIN_DIR`)에 설치합니다. 이 대상과 그것이 실행하는 모든 것
   > (plugin cache, `python3` runtime)은 sandbox-writable root 밖에 있어야 하며,
   > 어느 하나라도 실행 디렉터리(예: `$HOME`) 안으로 resolve 되면 hard-fail 합니다.

   일반 `codex`는 동일한 인증된 로그인 터미널의 실제 project/worktree root에서
   시작하세요. 기존 AGY 로그인 또는 AGY가 없을 때 기존 Gemini Enterprise OAuth
   로그인을 사용합니다. 정식 AGY review는 기본적으로 일시적 settings lease 아래
   `--sandbox read-only`로 실행합니다. 전용 프로젝트를 명시하면 미리 설정된 프로젝트
   권한을 사용해 이 lease를 생략합니다. 정식 Gemini review는 native Plan Mode를 요청하며
   mode-independent packaged per-call policy가 read/search-only behavior를 enforce합니다. Trusted
   Python과 `PATH`가 prerequisite이며 trusted launcher와 interpreter가 시작된 뒤
   wrapper child-process scrubbing은 유지됩니다.

   설치 후 대상 workspace 에서 일반 Codex session 을 새로 시작합니다:

   ```bash
   codex
   ```

   `/status`로 활성 approval policy를 확인하세요. 사용하는 Codex 빌드가
   `/debug-config`를 제공하면 다른 설정 계층이 예상 reviewer를 바꾼 원인도 확인할 수 있습니다.

이게 필수 경로의 전부입니다. repair 는 필요할 때만 surface 되는 proposal-only native-child
단계입니다([Custom Subagent](#custom-subagent) 와 [보안](#보안-security) 참고).

## 선택 / 고급

이 섹션의 어떤 것도 일반 개인 설치에는 필요 없습니다. 각 하위 섹션의 "다음 경우에만
하세요…" 조건이 해당될 때만 보세요.

### Gemini 구버전 CLI 사용

이 명칭은 AGY와 구분되는 `gemini` 실행 파일 경로를 뜻하며 다운그레이드를 권하지
않습니다. 정식 리뷰에는 CLI `>=0.34.0`과 version/help/policy preflight 통과가
필요합니다. v2 Pro 기본 모델에는 별도 버전 지원 검사가 적용됩니다.
인증 구분의 실제 식별자는 기존 `gemini-enterprise`를 유지합니다.

*조직 계정으로 Gemini CLI Sign in with Google이 이미 완료된 경우에만.* AGY가
설치되어 있으면 selector는 계속 AGY를 우선합니다. AGY가 없으면 어떤 family도
시작하기 전에 `gemini-enterprise`가 packaged Gemini wrapper를 선택합니다. 조직
Cloud-project 변수는 보존하고, explicit `-m auto`와 native `--approval-mode plan`을
요청하며 mode-independent packaged read/search-only policy를 enforcement boundary로
사용합니다. effective approval mode는 `unexposed`입니다. 모든 formal binding을
요구하고 provider call은 한 번만 합니다. API-key, ADC, Vertex, ambient-model
fallback을 사용하지 않고 선택한 provider가
시작된 뒤에는 route를 바꾸지 않습니다. `triad-gemini-dispatch`는 standalone consult로
남으며 formal route 선택은 `triad-cross-family-review`만 소유합니다.
현재 Gemini JSON envelope에는 신뢰할 수 있는 단일 runtime-model identity가 없으므로
formal audit는 정확히 `runtime_identity: "unexposed"`를 기록하고 `stats.models`, account
class, route에서 identity를 추론하지 않습니다.

### Linux / WSL2 sandbox 지원

*Linux 또는 WSL2 에서만.* Codex sandbox 지원을 위해 `bubblewrap`(`bwrap`)을
설치하세요. installer 는 OS package 를 설치하지 않습니다.

### 보안 모델 읽기

*툴킷에 의존하기 전에 전체 threat model 을 보고 싶을 때만.*
[SECURITY.md](SECURITY.md)의 전체 threat model과 아래
[보안](#보안-security) 요약을 참고하세요.

### bootstrap 재실행 참고

- 생성된 wrapper launcher 는 설치된 plugin cache 의 파일을 호출하므로, plugin
  업데이트 뒤에는 bootstrap 을 다시 실행해 launcher 경로를 최신으로 맞추세요.
- launcher 는 확인된 vendor CLI 경로를 고정하므로, `claude`, `agy`, 선택적
  `gemini` 를 업그레이드/이동한 뒤에도 다시 실행하세요.
- 기존 Codex session 은 새 plugin skill 을 못 볼 수 있으니 설치/업데이트 후 새
  session 을 시작하세요.
- `codex plugin add --json`은 marketplace `authPolicy`를 표시할 수 있지만, 이
  플러그인은 CLI OAuth/login을 수행하지 않습니다.

### 0.2.556 업그레이드

0.2.556은 명시적으로 선택하는 public v2 리뷰와 사용자가 직접 요청한 모든 leg의
웹 검증을 포함합니다. 기본 리뷰는 계속 no-web이며 기존 legacy 절차, 인증 경계와
공유 revision 선택을 유지합니다.

설치 방식에 맞는 [마켓플레이스 또는 로컬 Git 업데이트](docs/installation.ko.md#업데이트)를
따르고 bootstrap을 다시 실행한 뒤 새 Codex 세션을 시작하세요. Gemini 실제 정책
검증과 웹 허용 검증은 배포 패키지 검증과 별도로 수행합니다.

### 0.2.555 업그레이드

0.2.555는 provider 전송, 리뷰 root 정리 전 증거 보존, canonical verdict 파싱,
리뷰 조건·policy bytes 결합, Gemini CLI 버전 preflight를 강화합니다. Guarded
review는 링크 대상을 따라가지 않고 범위 내 symlink text와 누락된 검토 범위를
명시적으로 기록합니다.

0.2.555 릴리스의 기본 Formal REVIEW는 웹 조사를 금지합니다. AGY formal 호출은 URL-read deny를 추가하고
headless autoapproval을 생략하며, raw INVESTIGATION 기능은 유지합니다. Gemini
REVIEW는 B 전용 policy의 명시적 웹 deny를 사용하며 실제 적용 검증은 별도입니다.
기존 인증 경로, 공개 verdict schema, 비활성 AGY hook을 유지합니다. 이번 릴리스는
공유 스펙 revision 채택이나 cross-host 정합성 인증을 의미하지 않습니다.

아래 절차대로 marketplace를 갱신하고 플러그인을 재설치한 뒤, 설치된 bootstrap을
실행하고 새 Codex 세션을 시작하세요.

### 0.2.554 업그레이드

0.2.554는 제한된 process-group cleanup, Claude stdin 전달과 정제된 audit receipt,
AGY 오류·읽기 진단, opt-in committed-input 검사, 읽기 전용 Google CLI 진단,
raw verdict-file의 중복 member 거부를 추가합니다. review 구성, 공개 verdict schema와
`--project`를 생략한 기본 AGY 권한 경로는 유지하며, 진단 결과에 admission·coverage
효력을 부여하지 않습니다.

선택적이며 receipt에 바인딩되는 AGY `--project` 모드는 소유자가 미리 준비한 project의
정확한 `--cwd`와 필수 읽기 전용 deny 규칙을 `--sandbox read-only`와 함께 검증합니다.
이 모드에서는 global settings transaction 대신 해당 project를 검증하며 project나
권한을 생성·수정하지 않습니다. provider-free 스킬 동작 검증은 패키지의 고정 lifecycle
verifier를 사용하며, 이는 리뷰 라운드나 admission 결과가 아닙니다.

패키지의 AGY hook은 비활성 상태이며 bootstrap이 활성화하지 않습니다. 별도 승인을
받아 활성화하기 전에 문서의 live 검증 요건을 충족해야 합니다. raw-file 중복 검사는
provider wrapper가 이미 병합한 member를 복구할 수 없습니다. 플러그인을 재설치하고
설치된 bootstrap으로 launcher를 갱신한 뒤 새 Codex 세션에서 새 바이트를 불러오세요.

### 0.2.553 업그레이드

0.2.553은 아래에 설명한 guarded-worktree Pro/Flash preflight pair를 명시적으로
지원합니다. 두 receipt를 공통 digest에 포함하고, 각 Google dispatch는 선택한
model 자신의 receipt와 high effort를 사용합니다. AGY preflight는 요청한 model을
검사하며 native verdict validation은 공백만 있는 path를 거부합니다. 공개
three-family 기본값, prepared-directory route, `LegVerdict` schema는 유지하고,
four-leg admission gate는 workspace policy가 정합니다.

### 0.2.552 업그레이드

source-SOT staging은 이제 `TRIAD_BOOTSTRAP_CODEX_ROOT`로 bootstrap의 Codex directory를
선택하고 login `HOME`과 `CODEX_HOME`은 보존합니다. 명시한 root가 우선하며, 미설정 또는
빈 값이면 기존 `CODEX_HOME`, 이후 `$HOME/.codex` 기본값을 사용합니다. 동일한 absolute-path,
containment, provenance 검사를 적용하며 provider authentication은 변경하지 않습니다.

0.2.552는 formal review route별 의도된 시간을 고정합니다. Claude wrapper deadline
1,200초, AGY 또는 Gemini wrapper deadline 600초, fresh Codex의 반복 가능한 1,200초
observation wait를 사용합니다. poll, snapshot, wait wake-up은 nonterminal이며 terminal
outcome 해석은 cross-family `references/convergence.md` 계약이 전담합니다. provider
prompt framing, renderer metadata, three-family 구성, verdict schema, `_common.py`의
process termination 동작은 변경하지 않습니다.

### 0.2.551 업그레이드

0.2.551은 cross-family skill을 축소하고 기계적으로 검사할 수 있는 안전 규칙을 wrapper,
bootstrap, contract test로 이동합니다. 완전히 binding된 formal Claude `LegVerdict` route는
provider resolution 전에 `opus`, `xhigh`, 1,800초 timeout, fallback 없음 조건을 모두
충족해야 합니다. source-SOT staging은 review basis capture보다 먼저 실행되고, basis
route마다 하나의 명시적 provider cwd를 사용하며, Python 3.12로 임시 root를 정규화합니다.
또한 설치 시작 전에 toolkit 또는 review worktree 안의 모든 staged write target을 거부합니다.

### 0.2.550 업그레이드

0.2.550은 provider가 하나도 시작되기 전에 반복되는 실패의 복구 절차를 강화합니다.
같은 workflow에서 두 번째 zero-provider 실패가 발생하면 새 review ID 할당을 멈추고,
모든 failure receipt를 보존·비교해 공통 원인을 검증한 뒤 provider-free setup-only probe
하나를 통과해야 다음 formal round를 준비할 수 있습니다. source-SOT bootstrap에서는 host
command의 outer workdir를 환경 요구대로 유지하고, 문서화된 subshell만 별도의 neutral child
cwd로 들어갑니다. 현재 bootstrap에서는 `HOME`과 `CODEX_HOME`을 보존하고
`TRIAD_BOOTSTRAP_CODEX_ROOT`로 bootstrap의 Codex directory를 격리합니다. repository
검증 명령도 의도한 checkout을 명시적으로 binding하므로 workspace root의 다른 `tests/`
directory를 실수로 선택하지 않습니다. provider 구성, routing, strict `LegVerdict` schema는
바뀌지 않습니다.

### 0.2.549 업그레이드

0.2.549는 review family 하나라도 시작된 뒤 required leg의 시작이나 결과가 실패할 때의
처리를 바꿉니다. 실패한 leg는 계속 admission을 무효화하지만 이미 시작된 sibling을
취소하지 않습니다. 리더는 이미 시작된 모든 sibling을 기다리고, 구조적으로 사용 가능한 결과를
엄격히 검증한 뒤 post-review integrity를 확인합니다. 유효한 sibling finding은 advisory로만 유지하며,
모두 재현하고 확인된 범위 내 결함과 workflow, skill, tool, instruction, operator 또는
vendor로 분류한 실패 원인을 함께 수정하거나 transient vendor incident의 복구를 검증한 뒤 fresh complete three-family round를
실행합니다. 이 finding은 실패한 round를 admit하거나 다음 round에 admission credit을
제공하지 않습니다. provider 구성, routing, strict `LegVerdict` schema는 바뀌지 않습니다.

### 0.2.548 업그레이드

0.2.548은 Gemini를 사후 재시도로 만들지 않으면서 Gemini 구버전 CLI 정식 Google route를
복원합니다. 어떤 family도 시작하기 전에 packaged selector가 owner-selected 인증
class를 기록하고 AGY를 우선하며, AGY가 없을 때만 Gemini Enterprise OAuth용 Gemini
CLI를 선택합니다. selector는 review ID용 receipt 하나를 exclusive-create하고 preflight는
그 review ID, route, executable, selector SHA를 담은 canonical receipt를 만듭니다. 이
receipt 자체의 SHA, 정확한 model, nullable effort도 공통 review basis에 binding되며,
AGY는 tab-separated model catalog에서 필요한 정확한 slug를 증명합니다. 모든 family
render와 선택된 wrapper dispatch는 두 receipt가 다르면 거부합니다.
provider-free model/Plan/policy help preflight, explicit `-m auto`, native Plan Mode
요청, effective mode `unexposed` 기록, enforcement boundary인 mode-independent
packaged read/search-only policy의 exact fail-closed shape 검사,
경쟁 auth-selector scrub, 한 번의 provider call, exact local review-binding 검증과
literal `runtime_identity: "unexposed"` 기록을 수행합니다. 개인 Google Sign-In에는 계속
AGY가 필요합니다.

### 0.2.547 업그레이드

0.2.547은 reviewed data 안에 적힌 path, command, instruction이 approved review
input으로 승격되지 않게 합니다. plan, diff, source file, test, document가 참조한다는
이유만으로 reviewer가 excluded 또는 unrelated path를 열거나 따라가면 안 됩니다.
provider routing, verdict schema, review scope, approved evidence는 변경하지 않습니다.
또한 local validation을 통과한 leg result는 final packet 또는 worktree integrity가
성공할 때까지 provisional이며, 그 뒤에만 formal review evidence로 admit됩니다.

0.2.546은 worktree-first reviewer가 excluded path 이름을 노출하는 저장소 전체
path enumeration, status, search 명령을 실행해 자기 leg를 무효화하지 않도록 합니다.
review는 인증된 current-round diff에서 시작하고 이후에는 명시적인 approved path 또는
pathspec만 사용합니다. provider routing, verdict schema, review scope는 변경하지 않습니다.

0.2.545는 provider-native JSON Schema, strict local `LegVerdict` validator,
두 review prompt의 clean POSIX result path 계약을 일치시킵니다. leading/trailing
slash, backslash, empty 또는 exact dot/dotdot component, ASCII control, DEL을
거부하면서 일반 path, space, `.gitignore`, `..hidden`은 유지합니다. provider
선택, retry 동작, 정적 리뷰 capability는 변경하지 않습니다.

0.2.544는 완료 후 AGY `step_update` telemetry를 diagnostic으로 유지하고
verdict-admission schema로 취급하지 않습니다. 새 metadata field, 변경된 optional tool argument, 차단된 시도, 상충하는
duplicate progress event가 유효한 terminal review를 사후에 무효화하지 않습니다.
정적 리뷰 containment는 prompt, native `--mode plan`, 명시적 deny transaction이
계속 담당하며, strict local `LegVerdict`와 review-binding 검증 및 round-integrity
검증이 admission gate로 유지됩니다.

formal AGY 프롬프트는 계속 명시적인 정적 전용 계약입니다.
로컬 검사는 native file read/search만 허용하고, 웹은 기본적으로 차단하며 MCP 호출은 항상 차단하고 command, write, experiment, notebook, subagent, browser
actuation, scratch 도구를 금지합니다. 정적 검사로 결정할 수 없는 불확실성은
`open_questions`에 기록합니다. prepared directory 안에서는 native `list_dir`,
`find_by_name`, `view_file`을 필요에 따라 사용하고, 필수 `SearchPath`와 `Query` 인자를
전달하는 native `grep_search`를 사용합니다. 모든 view는 필수 `AbsolutePath` 인자를 전달하고, 큰 파일은 양의 정수 `StartLine`과
`EndLine` 범위를 명시해 읽습니다.
`ContentOffset`, `IsSkillFile`, 묵시적 `another page` 연속 읽기는 금지합니다.
AGY 1.1.20 이상의 formal plan-mode route는 native `--json-schema`를 전달하고
terminal `structured_output`을 소비한 뒤 strict local `LegVerdict` 및 exact
review-binding 검증을 반복합니다. 사람이 읽는 response text와 finish diagnostics는
verdict transport가 아니며,
개인 또는 Gemini Enterprise Business Sign-In,
일시적 global-settings transaction, `--sandbox read-only`, operator opt-out, 유료
API/ADC/Vertex route-selector 제거, local 결과 binding, failed-round 진단 전에 이미
시작된 sibling을 모두 완료하는 계약을 유지합니다.

일반 `--install`과 `--remove`는 marker 및 expected byte가 일치하는 정확한
plugin-owned legacy profile, launcher rule, repair-agent registration, pre-spawn
`[shell_environment_policy]`, retired apply/repair launcher만 정리합니다. Foreign,
edited, linked, non-regular target은 보존하고 보고합니다. owner-authored 설정을 보존하며
rule, permission profile, credential, 관련 없는 파일을 건드리지 않습니다.

review runtime은 하나의 complete focused directory, required family별 하나의
`LegVerdict`, bounded fix 이후 fresh complete round를 사용합니다. Batch, packet,
receipt, PTY, sentinel review transport는 제거되었습니다. AGY는 1.1.20 이상을
요구하고 native `stream-json`을 사용합니다. formal plan-mode route는 native
`--json-schema`를 전달하고 `structured_output`을 소비하여 로컬에서 검증하며,
`gemini-3.1-pro-high`와 `high` effort를 전달합니다. formal binding이 완료된 Claude
leg는 native `--permission-mode plan`을 추가하며, 세 review binding이 모두 없는
정확한 formal `LegVerdict` schema는 provider를 resolve하기 전에 실패합니다.
완전히 바인딩된 formal Claude route는 `--model opus --effort xhigh --timeout 1200`을
사용하고 `--fallback-model`을 지정하지 않은 경우에만 provider resolution 전에 통과합니다.
현재 route timing은 Claude wrapper deadline 1,200초, AGY 또는 Gemini wrapper deadline
600초, fresh Codex의 반복 가능한 1,200초 observation wait입니다. terminal outcome 해석은
cross-family `references/convergence.md` 계약이 전담합니다.
non-formal Claude permission 선택과 모든 project-trust policy는 native 설정을
유지합니다. 일반 `codex`가 정상 경로입니다.

명시적인 workspace four-leg gate는 guarded-worktree renderer에서 AGY
`gemini-3.8-flash-high`, `high`를 추가로 사용할 수 있습니다. AGY route 하나를
선택하고 Pro와 Flash를 별도로 preflight한 뒤, **모든** `render-worktree` 호출에
Pro receipt를 `--google-preflight-receipt`, Flash receipt를
`--google-flash-preflight-receipt`로 전달합니다. 두 receipt가 공통 digest에
포함됩니다. Flash prompt에는
`--family google --google-review-model gemini-3.8-flash-high`를 추가하고,
dispatch 시 Flash 자신의 receipt와 일치하는 model/high 인자를 사용합니다.
수정한 Pro prompt나 Pro receipt로 Flash custody를 대체할 수 없습니다. 이 고정
opt-in은 공개 three-family 기본값, prepared-directory renderer, `LegVerdict`
필드를 바꾸지 않으며 workspace admission 구성을 자동 설정하지 않습니다.

maintainer는 설치 전에 clean `HEAD`의 exact archive byte를 검증할 수 있습니다:

```bash
/bin/zsh -lic 'python3 scripts/verify_distribution.py --source-root . --output-dir _runs/distribution/0.2.556-final-r1'
```

시도마다 새 output label을 사용해야 하며 verifier는 기존 directory를 거부합니다.
dirty source tree를 거부하고 `HEAD`를 archive한 뒤 안전하게 추출하며 manifest와 core
review-skill hash를 비교하고 extracted byte에서 전체 test suite를 실행한 다음
`verification.json`을 기록합니다. authenticated fresh-process skill exposure는 별도 release
procedure로 유지합니다.

## 사용

Codex에게 다음 skill을 사용하도록 요청합니다.

- `triad-claude-dispatch`: Claude Code 단발 consult.
- `triad-antigravity-dispatch`: `agy` 기반 기본 Google-family consult.
- `triad-gemini-dispatch`: 별도 설치된 `gemini` CLI를 통한 standalone 호환
  consult입니다. formal review를 이끌지는 않지만, cross-family skill이 AGY가 없는
  Enterprise route에서 그 wrapper를 선택할 수 있습니다.
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
documentation을 둡니다. 이 release의 no-exclusion boundary는 모든 repository test
source를 포함합니다. 일반 SDD 구현 리뷰는 관련 test source를 포함하고, 다른
advisory review는 별도로 owner가 승인한 data scope를 따릅니다.
Normal SDD implementation review includes relevant test source.

Every leg receives the same directory and task. No prompt inlines a diff or file body.
Leader는 dispatch 전에 prepared-directory integrity digest를 기록하고 시작된 모든 leg이 끝난 뒤
다시 비교합니다. partial-start round에서는 실제 start failure와 나머지 required leg를
launch가 닫혀 시작하지 않은 상태로 기록한 뒤 비교합니다. 달라지면 round를 무효화합니다. 정식 gate 전에 모든 test failure를
production defect, test-case defect, intentional specification change 중 하나로
분류하고 해결하거나 승인합니다. Reviewer는 candidate code, test, build, hook,
generated script를 실행하지 않습니다.
Before a formal gate, classify every test failure as production defect, test-case defect,
or intentional specification change and resolve or approve it.

full diff는 navigation evidence이지 review boundary가 아닙니다. Leader는 현재 결정에
관련된 complete current file, configuration, governing documentation을 하나의 focused
directory에 준비합니다. 모든 required family는 그 동일한 complete directory를 한 번씩
검토하고 family, review ID, route-bound `metadata.content_digest`에 bind된 strict `LegVerdict` 하나를
반환합니다. 두 review 경로 모두 admission digest에 공통 검토 조건과 renderer/schema의
정확한 파일 bytes를 포함합니다. 조건·toolkit·receipt가 바뀌면 새 검토 기준을 만들며,
family만 바꾸면 공통 digest를 유지합니다. Gemini preflight는 policy bytes도 고정합니다.
`policy_sha256` 또는 `gemini_version`이 없는 receipt나 policy 파일이 바뀐 receipt는 다시 생성해야 합니다.
Formal Gemini preflight는 최대 15초의 `--version` 검사로 SemVer >=0.34.0을 먼저
확인한 뒤 기존 help 기능을 검사합니다. 실제 버전 문자열을 기록하며 receipt hash가
그 버전을 검토 기준에 포함합니다.
Leader는 dispatch 전에 prepared-directory integrity digest와 canonical-worktree fingerprint를
capture하고 시작된 모든 leg이 끝난 뒤 둘 다 verify하며, 모든 finding을 canonical worktree에서
재현합니다. Provider가 더 강한 boundary를 노출하지 않는 한 reviewer coverage는
prompt-controlled이며, manifest path나 provider confidence만으로 승격하지 않습니다.

Finding path와 inspected surface는 공백만으로 이루어지지 않은 canonical POSIX
review-relative path여야 합니다. Native schema와 local validation은 공백뿐인 전체
경로를 거부하되, 정상 파일명의 공백을 잘라내거나 공백이 포함된 component를 거부하지 않습니다.

이 계약은 credential, token, cookie, authentication file, environment dump, provider
log, 관련 없는 path를 provider-visible input에서 제외한다는 보안 경계를 바꾸지
않습니다. Commit, push, install/update, merge, release, publication은 계속 각각 별도의
owner authorization이 필요합니다.

일반 code-write dispatch는 대상 workspace에서 실행하세요. 경로 containment는
opt-in입니다: `TRIAD_WRAPPER_ALLOWED_ROOTS`가 설정된 경우에만 wrapper가 trusted root
밖의 `--cwd` / `--prompt-file`을 거부합니다. 기본은 경로를 제약하지 않으므로
approved-path containment는 provider가 실제로 enforce하지 않는 한 prompt-controlled입니다.
그 외 경계는 선택한 `--cwd` worktree, native provider permission,
immutable-directory digest, leader mutation check에 의존합니다.

`--prompt-file`과 `--cwd`는 절대 경로와 상대 경로를 받습니다. 두 상대 경로는
wrapper 시작 시 기록한 프로세스 작업 디렉터리를 각각 기준으로 사용합니다.
provider의 `--cwd`를 prompt 파일의 기준 경로로 사용하지 않습니다. 기존 경로 존재,
파일·디렉터리 종류, UTF-8, 빈 prompt 및 선택적 runtime-root 검사는 provider 실행
파일을 찾기 전에 적용됩니다. 정식 리뷰 산출물 경로는 계속 절대 경로이며 audit
마스킹도 유지됩니다.

로컬 Claude wrapper는 실제 전달할 prompt를 UTF-8 text stdin으로 provider에 보내며 JSON 및 native-schema 출력을 유지합니다. 바깥쪽 wrapper 명령줄에서도 prompt를 제외하려면 `--prompt-file`을 사용하세요. Claude 문서는 stdin의 [10MB 한도](https://code.claude.com/docs/en/headless#pipe-data-through-claude)를 명시하며 이 한도는 vendor가 적용합니다. 모델의 context/token 한도도 그대로 적용됩니다. Wrapper는 한도를 피하려고 prompt를 자르거나 나누거나 요청을 추가하지 않습니다. Stdin 전달 실패를 성공으로 받아들이지 않습니다. Stdin은 안쪽 provider argv에서 prompt를 제외합니다. 기존 argv 배열도 shell expansion을 방지합니다. 민감한 prompt/transcript 로그는 그대로 남으며 stdin이 입력 암호화, prompt injection 방지, token 사용량 감소를 제공하지는 않습니다.

Provider 성공에는 오류 없는 UTF-8 출력 수집 완료도 필요합니다. Wrapper는 정상
종료 후에도 저장된 process group을 정리하며 reader/writer 시작 도중 실패해도
정리합니다. AGY 설정 복구가 실패하면 답변을 출력하지 않고 수집한 원본을 기존
실패 기록에 보존합니다. 먼저 발생한 시간 초과나 provider 오류는 주된 실패
원인으로 유지합니다.

## 문제 해결 (Troubleshooting)

| 증상 | 원인 | 해결 |
|---|---|---|
| Gemini가 project worktree를 untrusted로 거부 | `--skip-trust` 제거 후 Gemini가 workspace trust를 소유 | 해당 worktree에 provider-native trust 결정을 하거나 중단하세요. TRIAD에는 trust bypass나 speculative detector가 없습니다. |
| 디스패치가 `oauth-env`로 실패 | 워커 CLI 로그인이 만료됐거나 없음 | 해당 vendor의 native login 재실행(`claude`, native AGY CLI 로그인, Gemini CLI Sign in with Google, 또는 `codex login`). toolkit은 대신 재인증하지 않습니다 — 신호만 surface 하니 직접 로그인하세요. |
| gemini leg이 `IneligibleTier`로 실패 | 선택한 조직 계정에 적합한 Gemini CLI entitlement가 없음 | 동일 Enterprise OAuth route를 고치세요. 개인 Google review는 AGY를 사용하며 dispatch 뒤 계정이나 route를 바꾸지 않습니다. |
| 설치/업데이트 후 새 skill이 안 보임 | 기존 Codex 세션은 새로 설치된 skill을 못 봄 | 새 Codex 세션을 시작하세요(플러그인 업데이트 뒤에는 launcher 경로 최신화를 위해 `bootstrap.sh --install` 재실행). |
| 디스패치가 non-zero로 끝났고 원인을 알고 싶음 | 숫자 exit code가 항상 권위가 있으며, 완료된 wrapper 실패는 보통 최종 분류도 출력함 | 아래 exit-code 범례를 보세요. 최종 `[wrapper] …` stderr 줄이 있으면 그 분류를 쓰고, summary 없는 초기 실패는 그대로 보존하세요. |

**Exit-code 범례**(wrapper 프로세스 exit code; 최종 wrapper summary가 있으면 그 class가
`[wrapper] <cli> <class> …` stderr 줄의 단어로 나타납니다):

| Exit | 의미 | 조치 |
|---|---|---|
| `0` | 성공 — 이어서 답변 | 없음. |
| `4` | 설정된 provider 실행 파일이 제출 전에 없거나 실행할 수 없음 | dispatch 전에는 개인 Google용 AGY 또는 Enterprise OAuth용 AGY/Gemini를 설치하세요. route 선택 뒤에는 같은 실행 파일을 고치고 사후 fallback하지 않습니다. |
| `64` | 재시도 후에도 server capacity 소진 | 일시적 vendor 과부하; 기다렸다 재시도. |
| `65` | 인증, config, quota 또는 다른 terminal provider failure(예: `oauth-env`, `cli-subscription-cap`, `token-limit`) | 표시된 provider state를 해결한 뒤 explicit new invocation을 만드세요. |
| `66` | 구조화 출력(`--pydantic`) 스키마 검증 실패 | `schema-fail is terminal for that invocation`; leader가 판단한 뒤 explicit new invocation을 만들 수 있습니다. shared-directory formal path는 legacy packet-bound schema를 요구하지 않습니다. |
| `67` | Codex가 제출된 output schema를 거부함(`schema-rejected`) | schema/configuration 불일치를 확인하고 explicit new invocation을 만드세요. |
| `1` | Wrapper가 답변을 추출하지 못했거나(`extraction-error`) 분류가 `unknown`임 | 최종 wrapper 분류와 provider 진단을 확인한 뒤 적절히 재시도하거나 escalation하세요. |

## 범위와 한계 — 이 도구가 하지 않는 것

toolkit이 어디서 멈추는지 알 수 있도록, 정직한 경계:

- **vendor 인증이나 token을 관리하지 않습니다.** token 발급/refresh, API-key
  주입, install-time provider probe가 없습니다. 각 vendor CLI의 native
  login으로 직접 로그인하며, runtime 인증 에러는 재로그인하라고 surface 됩니다.
  credential 복사, sandbox login 시도, 계정 프로비저닝 절차, authorization store는 없습니다.
- **OS 또는 Python package를 설치하지 않습니다.** vendor CLI, `python3`, 배포된
  Python requirements, (Linux/WSL2에서) `bubblewrap`은 직접 설치하며, installer는
  three provider wrapper launchers와 review-round selector launcher만 쓰고
  owner-authored config를 보존합니다. 선택된
  Python에 Pydantic 2 또는 필요한 jsonschema API가 없으면 bootstrap은
  mutation 전에 멈추고 그 interpreter를 위한 정확한
  `python3 -m pip install -r .../requirements.txt` 명령을 출력합니다.
- **자기개선 분류기는 heuristic이지 oracle이 아닙니다.** 진짜 실패를 그럴듯하지만
  틀린 class로 라우팅할 수 있습니다. worst case는 *integrity* 이슈 — 지속적 라우팅
  오분류이지 코드 실행이 **아닙니다**([보안](#보안-security) 참고) — 이지만,
  `~/.config/triad-codex-dispatch/classifier-patches.json`에 적용된 delta를
  주기적으로 검토하세요. Bootstrap은 확정된 절대 경로를 provider launcher와 출력된 owner apply argv에 고정하므로
  `TRIAD_CLASSIFIER_EXTENSION`을 바꾸면 bootstrap을 다시 실행해야 합니다.
- **wrapper containment은 프로세스 수준이지 OS 수준 confinement이 아닙니다.**
  wrapper-containment env는 wrapper 프로세스의 path/pydantic 처리를 gate할 뿐, OS
  수준 격리 주장이 아닙니다. 정식 AGY는 `--sandbox`, 선택한 `--cwd` review root,
  digest/mutation check, 커밋 전 사용자 검토를 결합합니다. `--project`가 없으면
  일시적 deny lease를 사용하고, 지정하면 사용자가 준비한 프로젝트 권한 레코드를 검증합니다.
  기본 웹 비활성 Formal preflight와 dispatch는 여섯 review deny를 요구합니다.
  웹 검증을 직접 요청한 review는 기존 다섯 raw deny를 유지하며, owner의
  `read_url(*)` 차단이 있으면 이를 제거하지 않고 실행 전에 거절합니다. 두 Formal
  모드 모두 `--dangerously-skip-permissions`를 전달하지 않습니다. Raw 호출은 기존 버전별
  headless 호환 처리를 유지합니다.
  sandbox는 OS 수준 confinement가 아닌 provider 관리 경계이며, round-integrity
  mutation detection은 별도의 fail-closed 검사입니다.
  Prepared-directory review의 wrapper `--cwd`와 `--prompt-file`은 예약된 `triad-review-`
  system-temp root 아래에 있습니다. `TRIAD_WRAPPER_ALLOWED_ROOTS`를 설정했다면 hardened
  mode를 포함해 canonical system temp base를 포함해야 합니다.

## 업데이트

[마켓플레이스 또는 로컬 Git 업데이트 절차](docs/installation.ko.md#업데이트)를
따라 개인 설정을 보존하면서 설치 캐시를 교체하세요.

새로 출력된 절대 명령을 실행하세요. 기본 `--install`은 permission state를 만들지 않고
three provider wrapper launchers와 review-round selector launcher를 다시 publish하며 exact plugin-owned legacy cleanup을
수행합니다. 업데이트 후 일반 Codex session을 새로 시작하세요.

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

이 `[wrapper] antigravity ok …` 줄이 디스패치가 동작했다는 신호입니다 — 플러그인과 launcher가
native provider environment에 연결된 것입니다. `ok` 는 분류이며, 다른 값(예: `oauth-env`,
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

provider-free 합성 lifecycle 검증을 명시적으로 요청한 경우 checkout에서
`python3 skills/triad-cross-family-review/scripts/verify_lifecycle.py`를 실행합니다.
기존 CLI와 격리 bootstrap을 재사용하며, 추론 없이 AGY 버전·모델 목록만 조회합니다.
실제 명령 결과, 패키지 소스 해시, export manifest, 합성 artifact의 실제 bytes(base64),
링크 문자열과 정리 증거를 JSON으로 출력합니다. Export 실패 시에도 합성 bytes를 보고서에
보관한 뒤 자체 fixture를 정리하며, 보관에 실패하면 fixture를 남깁니다.
PATH에 Git과 Codex, Claude, AGY CLI가, Python 3.12+ 환경에 배포된 requirements의 Pydantic 2와 jsonschema가 필요합니다.
임시 `AGY_SETTINGS_PATH`는 wrapper
트랜잭션만 격리하며 vendor 설정 격리를 증명하지 않습니다. 성공은 리뷰 판정이나
릴리스 인증이 아닙니다.

## 삭제

fresh shell에서 현재 설치된 plugin 경로를 다시 확인해 managed uninstall 명령을
출력한 뒤 plugin cache를 지우세요(script가 그 cache 안에 있습니다).

```bash
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","list","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); item=next(item for item in data["installed"] if item["pluginId"]=="triad-codex-dispatch@triad-codex-dispatch"); root=pathlib.Path(item["source"]["path"]); assert root.is_absolute(); print(shlex.join(["bash",str(root / "scripts" / "bootstrap.sh"),"--remove"]))'
```

출력된 절대 removal 명령을 실행한 다음 plugin registration을 제거합니다.

```bash
codex plugin remove triad-codex-dispatch@triad-codex-dispatch
codex plugin marketplace remove triad-codex-dispatch
```

`--remove`는 three provider wrapper launchers, review-round selector launcher와 exact plugin-owned legacy launcher,
profile, command rule, repair-agent registration, `[shell_environment_policy]` fragment를
marker와 expected byte가 정확히 일치할 때만 삭제합니다. exact legacy three-agent TOML도
제거합니다. Foreign, edited, linked, non-regular target은 보존하고 보고합니다.
owner-authored 설정을 보존하며 `config.toml`, rule, permission profile, credential,
관련 없는 파일을 건드리지 않습니다.
학습된 classifier patch는 의도적으로 보존됩니다. 이는 managed
uninstall 범위 밖이며, owner가 학습된 routing을 폐기하려는 경우에만 별도로
삭제해야 합니다.

## Custom Subagent

classifier repair는 prompt-controlled no-edit 동작을 가진 fresh native proposal-only
child를 사용합니다. Child는 proposal 또는 escalation만 반환하고 patch를 적용하지
않습니다. leader는 proposal만 고유 UTF-8 JSON에 저장하며 bootstrap은 Python
`shlex.join`으로 direct owner command를 출력합니다:

`python3 bin/apply_patch.py --cli <cli> --proposal-file <absolute-path> --classifier-file <pinned-absolute-path>`.

동일한 인증된 로그인 터미널에서 출력된 절대 명령을 실행합니다. run log는 age-floor
cleanup까지 남아 있습니다.

직접 만든 Codex custom subagent가 triad dispatch skill을 호출해야 한다면 Codex
`skills.config`에 필요한 `SKILL.md` 경로를 명시하세요. 경로는 live
`codex plugin list --json` 출력의 현재 설치 plugin `source.path` 아래 skill 파일을
가리키면 됩니다.

custom-agent TOML을 바꾼 뒤에는 새 Codex session을 시작하세요.

## 선택: 커밋 전용 입력의 사전 확인

특정 커밋만 리뷰하기로 명시한 경우, 사용자가 제공한 기존 review worktree를
custody 파일 생성 전에 확인할 수 있습니다.

```bash
python3 "$TRIAD_TOOLKIT/bin/review_round.py" fingerprint-worktree \
  --worktree "$REVIEW_WORKTREE" --require-clean-head "$REVIEW_COMMIT"
```

`TRIAD_TOOLKIT`과 `REVIEW_WORKTREE`는 canonical absolute root,
`REVIEW_COMMIT`은 승인된 전체 소문자 commit ID로 지정합니다. 검사 전후 HEAD가
정확히 일치하고 Git status가 깨끗해야 하며, 기존 hidden index flag와 sparse
checkout 거부도 유지합니다. Worktree나 provider project를 생성하지 않습니다.
옵션을 생략하면 기존 dirty-worktree 리뷰 방식을 그대로 사용합니다.

검사는 `--ignore-submodules=none`을 사용하므로 설정된 ignore 옵션이 submodule의
수정·untracked 내용이나 이동한 HEAD를 숨길 수 없습니다.

Custody 준비 후에는 정상 리뷰 fingerprint를 다시 계산하고 기존 render 및
post-review integrity 절차를 따릅니다. 이 사전 검사는 admission을 부여하거나
해당 절차를 대체하지 않습니다. Git-ignored 파일은 clean-state 주장에 포함되지
않으며 리뷰 입력에서 제외해야 합니다. 공유 Git metadata나 이후 변경을 격리하지
않습니다. AGY에는 이 cwd에 정확히 연결된 기존 UUID와 read-only guard가 필요합니다.
다른 프로젝트 UUID를 재연결하거나 global-settings fallback을 사용하지 마세요.
저장소 지침이 기존 guarded worktree를 요구한다면 의도된 dirty 변경도 보존합니다.

Guarded 리뷰에서는 리더가 승인된 심링크의 정확한 문자열과 HEAD/index/working-tree
기준을 capture 전에 TASK에 기록합니다. 리뷰어는 링크 대상이나 심링크 부모 경로를
따라 읽지 않고 이 증거를 검토합니다. 대상 내용은 별도로 승인하고 결합한 입력이어야
하며, 판정에 필요한 증거가 없으면 open question으로 보고합니다.
자세한 절차는 [scoped symlink evidence](skills/triad-cross-family-review/references/leg-contracts.md#scoped-symlink-evidence)를 따릅니다.

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

### 로그 보관과 수명주기

[공통 정리 계약](https://github.com/codefoundry-io/triad-dispatch-spec/blob/main/reference/review-rules.md#R-CLEANUP)은
소유권 확인, 증거 export, 최근 sibling IPC 보호를 규정합니다. 아래 수치는 이 host의
현재 구현값이며 양쪽 host의 공통 기본값은 아닙니다. 예약된 백그라운드 청소는 없습니다.

| 자료 | 청소 시점과 현재 한도 |
|---|---|
| Audit, `bin/_logs/<cli>/audit.jsonl` | 기록 성공 후 활성 파일이 10 MiB를 넘으면 회전합니다. 회전 시 CLI별 오래된 적격 보관본부터 정리하여 최대 5개·50 MiB로 제한합니다. 활성 파일은 별도이며 기간 기준 삭제는 없습니다. |
| 실패 IPC, `bin/_logs/<cli>/runs/` | 다음 일반 호출에서 3,600초 지난 적격 파일을 정리합니다. 실패 기록 후 100개·20 MiB를 넘으면 오래된 적격 파일부터 정리하지만 최근 sibling과 방금 쓴 기록은 보존합니다. 성공 호출은 실패 run-log를 만들지 않습니다. |
| 명시적 v2 리뷰 기록, `results/<name>/attempt-N/logs/<cli>/runs/` | 성공·실패 모두 기존 형식으로 원본 provider 증거를 보관합니다. attempt별 root를 사용하고 관리형 cleanup 전에 export합니다. 성공 기록은 실패 IPC나 수리 요청이 아닙니다. |
| 선택적 debug, `bin/_debug/<UTC-date>/<cli>.md` | `--debug`일 때만 기록하며 redacted mode에서는 생략합니다. 자동 보관 한도나 삭제는 없습니다. |
| 임시 `triad-review-*` 할당 | 모든 writer 종료 후 검증된 `export`를 먼저 수행하고 명시적으로 `cleanup`합니다. 이후 `prepare`는 소유권과 export가 확인된 30일 초과 비활성 할당만 회수할 수 있습니다. [리뷰 증거 정리](#리뷰-증거-정리)를 참고하세요. |
| Export한 리뷰 증거와 작업별 `_runs` 조사·스파이크 자료 | 자동 삭제하지 않습니다. 임시 리뷰 root를 정리해도 지정한 보관 목적지에는 남습니다. |
| AGY 자체 `~/.gemini/antigravity-cli/brain` | TRIAD 청소 소유 범위 밖입니다. 이 표는 AGY 자체 보관 정책을 보증하지 않습니다. |

`TRIAD_DISPATCH_LOG_DIR`는 audit·실패 로그 위치만 바꾸며 debug 위치는 바꾸지 않습니다.
기본 위치에 실패 IPC를 쓰지 못하면 소유한 임시 fallback을 사용할 수 있고, 이후 적격
호출에서 같은 기간 기준으로 정리합니다. 명시적으로 지정한 위치는 fallback하지 않습니다.
파일 identity·링크 검사·I/O 문제로 정리를 거부하면 자료가 남을 수 있습니다.
다음 호출이 없으면 다음 호출 시 청소도 실행되지 않습니다.
근거: [로그 구현](bin/_common.py), [로그 정리 테스트](tests/test_log_cleanup.py),
[리뷰 custody 테스트](tests/test_review_cleanup_custody.py).

### 전송과 진단 기록

Audit와 실패 run-log에는 같은 `transport` 객체가 기록됩니다. 실제 실행 route,
시도한 실행 파일, 관측한 CLI 버전(미관측 시 `null`), attempt와 stdin 전달 상태를
[공통 후보 계약](contracts/receipt-fields.json)에 맞춰 보존합니다. 인코딩·spawn
실패는 `not-started`, 불완전한 전달은 `failed`이며 기존 timeout·vendor 오류를
덮어쓰지 않습니다. 관측하지 못한 별도 transport는 `unexposed`입니다. AGY의 기존
버전 검사와 검증된 Gemini preflight 버전을 재사용하며 추가 provider 호출은 없습니다.
현재 legacy 호출은 `attempt=1`을 기록하며 capacity/schema-repair 횟수는 기존
별도 필드 의미를 유지합니다. 명시적 v2 경로는 할당한 leg·attempt에 실제 native
호스트 또는 CLI 관측을 결합합니다. preflight 버전으로 미노출 실행 버전을 채우지 않습니다.

Wrapper main thread가 provider 결과를 수집하는 동안 SIGTERM/SIGHUP을 받으면
소유한 프로세스 그룹과 reader/writer를 수거하고 기존 audit/run-log에 실패를
기록합니다. 이미 출력한 성공 응답은 취소를 덮어쓰거나 재호출을 유발하지 못합니다.
이전 signal handler는 복원하며 KeyboardInterrupt의 기존 수거 후 재발생 동작은
유지합니다. SIGKILL이나 호스트 장애까지 수거한다고 보장하지 않습니다.

Provider child가 시작된 경우 audit에 `effective_cwd`가 남을 수 있습니다.
Dispatch 전에 host가 해석한 실행 디렉터리이며 redacted/hardened mode에서는
경로 전체를 `<redacted:cwd-path>`로 가립니다. 실행 전 실패에는 생략합니다.
이는 실행 위치의 기록이며 provider의 이후 디렉터리 변경이나 리뷰 범위를
증명하지 않습니다. 환경 덤프나 failure/repair IPC field를 추가하지 않으며
dispatch와 admission을 변경하지 않습니다.

Formal AGY plan-mode audit에는 `agy_read_telemetry`가 포함될 수 있습니다.
관측한 `done_view_file_event_count`와 host 실행 cwd 안에서 해석한 고유
`relative_paths`를 최초 등장 순서대로 남깁니다(최대 128개, 경로당 유효한
UTF-8 문자 최대 1024개). `view_file`인 DONE tool event만 세며 반복·실패도
포함합니다. 잘못된 경로, 상대경로, `..` 구성요소가 있는 경로, cwd 밖 또는
symlink로 이탈하는 경로는 제외하고 경로 해석 실패는 판정에 영향을 주지 않습니다. Redacted/hardened
audit에는 개수만 남습니다. 유효한 cwd 또는 해당 event가 없으면 생략합니다.
읽기 성공, 고유 실행, 리뷰 범위, 권한 또는 과거 파일시스템 상태를 증명하지
않는 진단 정보입니다. 결과·failure/repair IPC field와 기존 raw-stream 보관
정책은 바꾸지 않습니다. Event 형식은 [AGY headless mode](https://antigravity.google/docs/cli/headless/)를 따릅니다.

Claude audit에는 stdout preview와 별도로 `claude_receipt`가 남을 수 있습니다.
검증된 session UUID, 전체 token 수, 최대 16개 model의 사용량(식별자는 최대
128 ASCII 문자), 추정 USD 비용, permission denial 개수만 보존합니다.
Token 수는 `2**53 - 1` 이하의 음이 아닌 정수, 비용은 USD 1,000,000 이하의
유한한 값만 허용하고 잘못된 field는 생략합니다. Redacted mode에서는 session과
전체 per-model map을 제외하고 aggregate 숫자만 보존합니다. 마지막 envelope를
사용하며 tool 이름·인자와 denial 상세는 receipt에 넣지 않습니다. 기존 audit의
권한과 보관 정책을 따릅니다. 보고된 model 목록은 실제 reviewer model의 증명이
아니며 비용은 청구액이 아닌 [provider 추정치](https://code.claude.com/docs/en/headless)입니다.
Receipt는 응답·재시도·종료 상태·admission에 영향을 주지 않습니다.

AGY terminal failure는 `extraction_error`에 `terminal_error`를 덧붙일 수 있습니다.
문자열 오류 또는 `message`, `error`, `detail`, `code` 순서에서 처음 찾은 유효한
문자열의 첫 비어 있지 않은 줄을 최대 512자로 보존합니다. 진단 데이터이며
분류·재시도·admission은 바뀌지 않습니다. 합쳐진 필드에는 기존 audit redaction과
길이 제한이 적용되고, failure run log는 계속 민감한 untrusted data입니다.

Cross-family review는 focused prepared-directory digest, canonical worktree
fingerprint, family별 하나의 strict `LegVerdict`를 사용합니다. 리더는 result와
snapshot을 reviewed evidence 밖에 두며 bounded correction 뒤에는 fresh complete
round를 시작합니다.

### 리뷰 증거 정리

`prepare`는 system temp의 `triad-review-` namespace에 mode-0700 root를 만들고,
root 밖에 독점 생성한 allocation 기록으로 실제 디렉터리 identity를 연결합니다.
`results/_logs`도 다른 round 증거와 함께 export 대상에 포함합니다.
모든 writer가 종료된 뒤 `review_round.py export --review-id ID --expected-root ROOT
--output DESTINATION`을 실행하고 같은 ID/root로 `cleanup`합니다. 목적지는 모든
managed root·cleanup claim 밖의 새 절대 경로여야 합니다. Export는 파일 bytes,
빈 디렉터리를 포함한 목록, 링크 문자열을 보관하며 링크 대상을 따라가지 않습니다.
Cleanup은 원본과 보관된 증거를 재검증하고, 뒤늦게 추가·수정된 자료가 있으면 거부합니다.
최종 결과 수거 후 한 번 export합니다.

하나의 allocation은 리더 한 명만 정리합니다. 확인된 partial claim은 재개하고,
완료 후 재호출은 no-op입니다. 다음 `prepare`는 출처와 export가 검증된 allocation 중
activity가 strictly more than 30 days 없는 것만 정리하며 partial claim도 포함합니다.
이름·UID·나이·그럴듯한 marker만으로는 삭제하지 않습니다. 다른 root와 링크 대상은 보존합니다.

거부된 잔여물은 경로·진단을 남기고 소유자 권한으로 증거를 확인·보관한 뒤 정확히 확인한
대상만 정리합니다. 알 수 없는 폴더를 채택하려고 allocation/export 기록을 만들지 마세요.
`triad-review-ID` root의 형제 기록은 `.triad-review-ID.{allocation,export,claim}.json`,
claim 폴더는 `.triad-review-ID.cleanup`입니다. 정리 중단 후 검증된 기록만 남았다면
원래 review ID와 expected root로 `cleanup`을 다시 실행하세요. Root와 claim 폴더가
모두 사라진 뒤 기록만 남은 경우 stale sweep은 이를 수거하지 않습니다.
악의적인 동일 UID의 기록 위조나 열린 FD를 유지하는 동시 writer 방어를 보장하지 않습니다.

Dispatch driver에 도달한 모든 일반 non-`--repair-mode` wrapper invocation은 provider
실행 전에 3,600 seconds보다 오래된 managed UUID/file-IPC entry를 best-effort
cleanup합니다. Antigravity는 `--preflight-only` 전에도 cleanup합니다. Cleanup error는
dispatch를 막지 않으며 perfect garbage collector를 주장하지 않습니다.

- **Timeout cleanup은 best effort이며 containment가 아닙니다.** POSIX에서 wrapper는
  새 child의 group이고 wrapper group과 다른 경우에만 provider group을 기록합니다.
  Timeout 또는 interruption은 TERM을 보내고 direct child를 reap한 뒤, 저장한 group을
  probe하여 살아 있는 member에게 KILL을 보냅니다. 지원하지 않거나 안전하지 않은 group
  identity에서는 direct-process cleanup을 사용합니다. captured group을 벗어난 child
  (새 session 시작 포함)는 이 보장의 범위 밖이며 OS identifier reuse race도 남습니다.
  이것은 OS sandbox가 아닙니다.

## 보안 (Security)

지속적인 control은 explicit data authorization, pinned executable,
digest/mutation check, strict result custody, native proposal-only repair child와
deterministic owner apply입니다. 문서화된 formal Claude, packaged AGY, formal Gemini route 밖의
permission 선택은 provider/user/project setting에 남습니다. 전체 threat model:
[SECURITY.md](SECURITY.md).

## Support

- 버그 신고와 질문: https://github.com/codefoundry-io/triad-codex-dispatch/issues
- 보안에 민감한 신고: 같은 tracker에 제목 앞에 `[security]`를 붙여 올리세요.
  신고 본문에 secret이나 token은 넣지 마세요.

## 선택: 전용 AGY 프로젝트

owner가 준비한 AGY 프로젝트를 사용하려면 `--project <canonical-lowercase-UUID>`와
명시적 `--cwd`, `--sandbox read-only`를 함께 전달합니다. wrapper는
`~/.gemini/config/projects/<UUID>.json`에서 일치하는 `id`, canonical cwd URI와
같은 `folderUri`를 가진 단일 resource, 다음 다섯 deny rule을 확인합니다:
`write_file(*)`, `command(*)`, `unsandboxed(*)`, `execute_url(*)`, `mcp(*)`.
추가 owner deny rule은 보존하며, 이 모드에서는 프로젝트·전역 설정·전역 lease 파일을
생성하거나 수정하지 않습니다.

기본 웹 비활성 정식 review의 preflight와 dispatch에는 같은 UUID를 사용합니다.
프로젝트 설정에 `read_url(*)`도 있어야 하며 누락되면 owner 설정을 바꾸지 않고
거절합니다. 웹 검증을 직접 요청한 review는 이 전체 URL 차단이 남아 있으면 실행 전에
거절하고 원래 규칙을 보존합니다. 기존 preflight의
`route_args`와 receipt hash가 프로젝트를 review에 연결합니다. Pro/Flash pair도 같은
프로젝트를 선택해야 하며, 호출 동안 프로젝트 설정을 유지해야 합니다. 이는 설정된
native permission 경계이며 OS 격리나 실행 중 정책 증명은 아닙니다. `--project`를
생략하면 기존 전역 transaction을 사용합니다. 정확한 명령은
[호출 계약](skills/triad-cross-family-review/references/leg-contracts.md#optional-dedicated-agy-project)을 따릅니다.

## 선택적 AGY 훅 도구 (비활성)

`bin/agy_hook.py`는 패키지에 포함된 PreToolUse 도구 이름 필터입니다.
신뢰하는 toolkit 루트에서 다음 명령으로 비활성 설정을 출력할 수 있습니다.

```sh
python3 bin/agy_hook.py --render-config
```

항상 `enabled:false`와 shell quoting된 helper 절대 경로를 출력합니다.
설정 파일 생성·설치·활성화나 wrapper/project 권한 변경은 하지 않으며,
bootstrap도 이 훅을 활성화하지 않습니다. 기본 stdin 인터페이스는 정확한
이름 `view_file`, `grep_search`, `list_dir`, `find_by_name`, `search_web`,
`read_url_content`에만 JSON `allow`를 반환합니다. 나머지 이름은 거부합니다.
`toolCall.name` 문자열과 `toolCall.args` 객체가 필요합니다. 잘못된 UTF-8/JSON,
중복 키, 객체·배열 64단계 초과 중첩(루트가 1단계), 1 MiB 초과 입력은
원문을 반영하지 않는 짧은 deny JSON을
반환합니다. 처리된 allow/deny 응답의 종료 코드는 0입니다.

이름 필터는 경로·내용·네트워크 목적지 격리가 아닙니다. `allow`는 명시적 권한
결정이며 중립적 통과가 아닙니다. 실제 훅 로딩, 정상 읽기, off-list 거부와 효과
부재, 기존 deny 규칙 보존은 offline 테스트로 입증되지 않았습니다. 활성화 전에
정확한 훅 경로·설정과 기존 대상 UUID/cwd의 사용 승인을 받고 해당 환경에서 각각
검증해야 합니다. 증거가 없으면 비활성 상태를 유지합니다. helper crash/timeout에
대한 provider의 권한 처리는 미검증이며, 종료 코드만으로 차단을 입증할 수 없습니다.
이 도구는 리뷰 승인이나 읽기 coverage 증거를 제공하지 않습니다.
[공식 훅 계약](https://antigravity.google/docs/hooks)을 참고하세요.

비활성 renderer는 현재 bare `python3`를 호출합니다. 승인된 활성화 전에는 이를
검증된 신뢰 가능한 인터프리터 절대 경로로 바꿔야 합니다. `*` matcher는 활성 세션의
모든 도구 호출에 allowlist를 적용하므로, off-list 도구를 계속 거부하면서 전체 리뷰가
완료되는지 입증해야 합니다. 초과 입력의 stdin 쓰기·broken pipe 및 helper 프로세스
실패 결과도 확인해야 하며, deny JSON 출력만으로 provider의 차단을 증명하지 않습니다.

## 원본 판정 파일 검증

`bin/verdict_schema.py validate --result-file`과 `validate_verdict_file()`은
값이 같거나 중첩된 중복 JSON 키와, 이스케이프 표기만 다른 동일 키도 거부합니다.
검증된 파일을 한 번 읽고 같은 원본 바이트에 중복 검사와 기존 strict semantic 및
review/family/digest 검증을 적용합니다. 중복 입력은 키·값을 반영하지 않는 고정 오류
`duplicate JSON member`와 종료 코드 2를 반환합니다. 정상 판정의 출력은 유지합니다.

Canonical wrapper도 성공 결과를 내보내기 전에 원본 답변과 native envelope/event의
JSON 중복을 검사하며, 중복 판정은 추가 formal provider 호출 없이 schema failure로
반환합니다. 예약 표기 `verdict_schema:LegVerdict`와 `verdict_schema.LegVerdict`는
모두 패키지의 스키마 파일을 읽고 dispatch 전에 세 expected review binding을
요구합니다. 사용자 정의 스키마, raw 조사, 깨진 AGY 로그 행 처리와 기존 provider
실패 우선순위는 유지합니다. schema field나 리뷰 구성은 추가하지 않습니다.
result-file reader만으로는 다른 호출자가 이미 없앤 중복을 복원할 수 없습니다.

## Google CLI 메타데이터 스냅샷

`python3 bin/google_diagnostics.py --cli agy` 또는 `--cli gemini`를 실행하면
JSON 스냅샷 하나를 출력합니다. 프롬프트나 추론 호출 없이 `--version`, `--help`
순서로 조회합니다. 실행한 조회가 모두 끝나면 종료 코드 0, 처리된 선택·호스트·조회
실패는 1입니다. 지원하지 않는 기능은 관찰 결과이며 실패가 아닙니다. 이 독립 도구는
wrapper나 리뷰 승인에 영향을 주지 않습니다.

`--inventory`를 추가하면 루트와 하위 명령 도움말을 확인한 뒤 지원되는
`agy models`, `agy plugin list`, `gemini extensions list`만 조회합니다.
별칭을 추측하거나 설치·업데이트·인증 명령을 실행하지 않습니다. 고정된 조회 인수,
상태, 종료 코드, stdout 바이트 수·SHA-256, 제한된 버전·지원 여부만 기록합니다.
인식한 탭 구분 AGY 목록은 중복 없는 모델 slug 최대 128개, 각 ASCII 128자까지
반영합니다. 비어 있거나 형식을 알 수 없거나 상한을 넘으면 해시를 보존하고
`model_format: unrecognized`, 빈 slug 목록을 반환합니다. 플러그인·확장 출력은
해시로만 표현하며 비공개 이름·경로, stdout/stderr 원문, 환경 덤프를 출력하지 않습니다.

기존 실행 파일 선택 규칙을 유지합니다. 유효한 고정 경로를 우선하며, 엄격 모드가
아니면 누락·무효 고정 경로에서 PATH로 대체할 수 있습니다. 엄격 모드는 대체를
거부합니다. 상대 PATH의 선택 결과는 선택 시점 cwd를 기준으로 고정해 중립 디렉터리에서도
같은 실행 파일을 사용합니다. stdin을 닫고 도구 소유의 중립 임시 cwd 및 기존 주입·Google 환경 선택자
제거 함수를 사용합니다. 각 조회는 5초 기한과 제한된 프로세스 정리 유예를 가지므로
전체 실행이 정확히 5초 안에 끝난다는 보장은 아닙니다. 실패하면 후속 조회를 멈춥니다.
기준선·이력을 저장하지 않아 자동 변경 판정을 제공하지 않습니다. Vendor CLI 자체의
캐시·텔레메트리는 발생할 수 있으며, OS 격리나 실제 설치 환경의 부작용 검증은 아닙니다.

공식 명령 근거: [AGY 모델](https://antigravity.google/docs/cli/headless/),
[AGY 플러그인](https://antigravity.google/docs/plugins?tab=cli),
[Gemini 확장](https://geminicli.com/docs/extensions/). 실제 도움말로 지원 여부를
판단하며, 가짜 CLI 테스트는 실제 추론 없이 이 도구의 동작을 검증합니다.

## 참고

- 위에서 공개한 승인된 내부 AGY flag, 일시적 AGY global-settings transaction,
  사용자가 준비한 프로젝트를 선택하는 `--project`, wrapper 내부 formal Gemini
  model/Plan 요청 및 policy flag 외에는
  TRIAD가 caller-supplied yolo, bypass, skip-trust, accept-edits 또는 동등한 permission
  control을 받지 않습니다. transaction은 lease 동안만 AGY setting을 변경하고 원래
  바이트를 복원하며, hard crash가 남긴 deny residue는 다음 guarded call이 복구합니다.
- Native permission decision은 commit, push, install, release, publication에 대한 owner workflow
  authorization을 제공하지 않습니다.
- Fresh repair child는 proposal 또는 escalation만 반환하고 classifier change를
  적용하지 않습니다.

## 프로젝트 리뷰어 설정 확인

provider를 실행하지 않고 v2 설정의 해석 결과를 확인합니다.

```bash
python3 /absolute/plugin/bin/review_round.py resolve-roster --project-root /absolute/project
```

해당 프로젝트의 `.agents/triad-review-legs.json`만 읽으며, 파일이 없으면
[호스트 기본값](contracts/review-legs.default.json)의 Claude·native Codex·Google
3개를 사용합니다. `name`별로 병합하고 중첩 필드는 병합하며 스칼라·배열은
교체합니다. 새 이름은 완전한 항목이어야 합니다. 이름·원본 JSON 키 중복,
알 수 없는 필드, 잘못된 vendor 블록, 미해결 템플릿, 링크·잘못된 파일은
기본값으로 대체하지 않고 종료 코드 2로 거부합니다.

출력에는 전체 설정, 활성 이름, 서로 다른 family와 설정 경로가 포함됩니다.
`acceptance`는 데이터이며 informational 항목도 참여자입니다. model/effort의
null은 dispatch 시 기본값을 적용하도록 그대로 보존합니다.
`capabilities_checked=false`는 설정 검증만 했다는 의미입니다. 모델 가용성,
dispatch·round 승인이나 기존 legacy gate 변경을 뜻하지 않습니다. 실행·수집은
아래 명시적 v2 절차를 따릅니다. Gemini 기본 요청은 `gemini-3.1-pro-preview`이며
HIGH는 CLI v0.60.0의
[소스 기본값](https://github.com/google-gemini/gemini-cli/blob/v0.60.0/packages/core/src/config/defaultModelConfigs.ts#L45-L77)입니다.
Gemini effort 플래그나 실제 계정 접근·실행 모델을 증명하는 값은 아닙니다.

## 오프라인 v2 후보 검증

[공통 계약 후보](contracts/README.md)는 공유 커밋
055204c83e57bf87eeac5b2422f2b17340f7c53b의 원문입니다.
절대 정규 경로의 일반 결과 파일과 예상 결합값 6개를 지정합니다.

    python3 /absolute/plugin/bin/validate_v2.py validate --result-file /absolute/result.json --expected-review-id round-1 --expected-family codex --expected-content-digest <64-lowercase-hex> --expected-leg-name codex-main --expected-attempt 1 --expected-route null

실제 인자로 치환하세요. Google의 예상 route는 agy 또는 gemini입니다.
성공하면 검증된 v2 객체와 종료 코드 0을 반환하며, 입력·결합값·계약 무결성
오류는 종료 코드 2로 거부합니다. jsonschema로 오프라인 검증하고 원본 JSON의
중복 키와 배포된 SHA-256을 검사합니다. 해시는 서명이 아닌 로컬 무결성 확인입니다.
이 명령은 provider를 호출하거나 round를 승인하지 않습니다. v2 wrapper·renderer·수집기
활성화 및 revision 채택도 별도 단계입니다. 기존 legacy 경로와 custom-schema 조사는 유지됩니다.

## 명시적 public v2 리뷰

현재 사용자·프로젝트 지침에서 v2를 명시적으로 선택하면
[스킬의 v2 절차](skills/triad-cross-family-review/references/public-v2-review.md)를 따릅니다.
`bin/review_round.py`의 `v2-create`, `v2-allocate`, `v2-record-cli`,
`v2-record-native`, `v2-record-start-failure`, `v2-collect`가 프로젝트 roster,
공통 프롬프트, native·wrapper 호출과 결합값 6개의 판정을 연결합니다.
기존 legacy 개발 게이트와 wire 형식은 유지하며 결과를 상호 변환하지 않습니다.

informational을 포함한 모든 활성 이름이 참여합니다. 원본 결과·run-log·호스트
관측·읽기 증거와 준비 실패 기록을 attempt별로 보존합니다. 누락·무효 결과는
합의를 막습니다. 원인 확인 후 변경 없는 실행 실패 항목만 재시도할 수 있고,
소스나 리뷰 조건이 바뀌면 모든 항목이 새 기준으로 전체 범위를 검토합니다.
Minor만 있는 부정 판정도 원래 선택을 보존합니다. 수집 명령 종료 0은 승인과
다르며 JSON의 `INCOMPLETE`, `BLOCKED`, `OWNER_DECISION_REQUIRED`, `AGREED`를 확인합니다.

Codex는 native로 실행합니다. 설치된 CLI·catalog 검사는 요청 설정 지원 여부이며
계정 접근권이나 실제 실행 모델의 증명이 아닙니다. 노출되지 않은 값은 null/unexposed로
남깁니다. 기존 export·cleanup을 사용하며 별도 스케줄러·주기적 정리기·영구 웹 로그나
설치 revision 변경을 추가하지 않습니다.

## 직접 요청한 웹 검증

사용자가 해당 리뷰에 직접 요청할 때만 모든 leg에 웹 검증을 허용합니다.
신기술 여부로 자동 허용하지 않습니다. [호출 절차](skills/triad-cross-family-review/references/review-web.md)를 따릅니다.
Raw Claude `--web`은 `WebSearch`/`WebFetch`를 허용하고 호출자 프롬프트를 보존합니다.
0.2.556 릴리스에 포함되며, 실계정 웹 실행 검증과 공유 revision 채택은 별도 단계입니다.

## 승인된 AGY 웹 조사

사용자가 독립적인 웹 조사를 직접 요청하면
`antigravity_wrapper.py --web --sandbox read-only`를 사용합니다. 사용자 프롬프트나
프롬프트 파일과 선택적 custom schema를 받습니다. 리뷰에서 사용하려면 모든 leg의
현재 허용 조건과 preflight·호출 옵션을 일치시켜야 합니다.
Gemini raw wrapper도 `--web`을 받고 같은 지침의 도구 이름만 치환합니다. 기존
Gemini 권한과 인증은 유지되며, 이 옵션이 권한 우회나 formal policy를 선택하지 않습니다.
[호출과 증거 계약](skills/triad-cross-family-review/references/leg-contracts.md#authorized-agy-web-investigation)을 따릅니다.

wrapper는 공통 근거 확인 지침을 프롬프트 맨 끝에 붙입니다. 검색 요약은 원문을 찾는
단서이며, 인용한 페이지를 실제로 읽고 날짜·버전을 확인해야 합니다. 지침 추가만으로
페이지 읽기나 해석의 정확성이 증명되지는 않습니다. 기존 로그 마스킹과 실패 시에만
생기는 run-log는 유지되며, 일반 성공 로그에는 전체 웹 도구 호출 기록이 남지 않습니다.

Known issue `KI-AGY-URL-BODY-PREFIX`: AGY 1.2.7은 일부 페이지의 원문을 앞부분만
저장할 수 있습니다. 이 현상만으로 TRIAD 호출 실패로 판정하거나 자동 복구·재시도를
시작하지 않습니다. 실제 호출 결과를 유지하고, 결론에 영향을 주는 불완전한 근거는
불완전 또는 UNSURE로 표시합니다. 별개의 전송·스키마·모델 식별·무결성 실패 처리는
유지합니다. [사용자 결정과 재현 근거](https://github.com/codefoundry-io/triad-dispatch-spec/blob/11582b0f6fe6cc6bd292cbb90dfd07dab452ed75/decisions/2026-09-20-owner-follow-up.md#ki-agy-url-body-prefix-non-fatal-known-issue)를 참고하세요.

세 wrapper의 raw 호출은 승인된 추가 입력 폴더를 `--add-dir`로 반복 지정할 수
있습니다. 호출 시작 cwd 기준으로 해석하고 기존 runtime-root 검사를 유지합니다.
Claude·AGY는 native `--add-dir`, Gemini는 `--include-directories`로 전달합니다.
Gemini는 쉼표가 포함된 단일 경로를 거부합니다. 기존 native 권한을 유지하며
OS 읽기 전용 격리를 뜻하지 않습니다. REVIEW에서는 범위 밖 입력 추가를 거부합니다.
성공 요약과 기존 audit에는 해석된 prompt-file·cwd가 기존 마스킹 정책에 따라
기록됩니다. inline prompt의 파일 경로는 null이며, 거부 시 후보 경로도 마스킹합니다.
