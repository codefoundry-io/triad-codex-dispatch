# 설치와 개인 설정

[English](installation.md) · [README](../README.ko.md)

**일반 마켓플레이스 설치** 또는 **Git 다운로드 후 로컬 설치** 중 하나를 선택합니다.
두 방식은 같은 플러그인과 공통 실행 환경 설정을 사용합니다. 같은 마켓플레이스 이름으로
두 경로를 중복 등록하지 마세요.

## 포함된 공통 라이브러리

이 소스는 공개된 `triad-dispatch-lib 0.1.0.dev6` 사전 릴리스를
커밋 `1872227abd42553635c733e0aa228548a577a732`에서 가져와
`bin/triad_dispatch_lib/`에 포함합니다. 별도 라이브러리 checkout이나 editable
설치는 필요 없습니다. 선택한 Python 3.12+ 환경에 배포본의 `requirements.txt`를
설치하며 `referencing>=0.37,<1`을 사용합니다. 리뷰 실행 중 의존성을 설치하지
않습니다. [공용 runtime](shared-runtime.ko.md)은 기존 legacy consumer를
기본값으로 보존하며 설치된 Codex skill은 검증된 보존 binding을 선택합니다.

유지보수자는 `python3 scripts/vendor_library.py --check`로 생성 파일을 확인합니다.
현재 고정된 릴리스를 갱신할 때에는 생성 파일을 직접 수정하지 말고 toolkit 루트에서 실행합니다.

```bash
python3 scripts/vendor_library.py --wheel /absolute/path/to/wheel \
  --source-commit 1872227abd42553635c733e0aa228548a577a732 --write
```

검토한 아티팩트 해시와 라이브러리 변경을 먼저 확인합니다. 변경되거나 예상하지
못한 관리 파일이 있으면 갱신을 거부하고 보존합니다. 이 검사는 Codex 자체의
플러그인 캐시 교체 동작을 변경하지 않으므로 기존 업데이트·제거 절차를 따릅니다.

[dev6 릴리스](https://github.com/codefoundry-io/triad-dispatch-lib/releases/tag/v0.1.0.dev6)에
wheel과 `triad-release.json`이 공개되었습니다. 이 번들에 사용한 릴리스 wheel은 [`contracts/library-adoption.json`](../contracts/library-adoption.json)에
기록되어 있으며, `wheel_sha256`은
`5baf86483fe04935b2e21654508678eb21f7003a0038fb3875355a2e2967bfdc`입니다.
갱신 전에 릴리스 manifest, 원본 커밋과 wheel SHA-256을 확인합니다.
전체 패키지에는 네 리소스 번들이 포함되며 일부 모듈만 복사하는 방식은 지원하지 않습니다.

다른 소스·콘텐츠 pin으로 전환할 때는 유지보수자가 기존 pin으로 기존 파일을
검증하고, 소유한 빈 staging 디렉터리에서 새 패키지를 생성·검증한 다음,
교체 직전 기존 관리 파일을 다시 확인하고 교체 후 전체를 검증합니다. 위의
동일 pin 갱신 명령은 pin 이관 명령이 아닙니다. 기존 관리 파일을 삭제하거나
검증을 건너뛰어 이관하지 마세요.

원본·아티팩트·파일 해시는 `contracts/library-adoption.json`에 기록합니다.
소스 반영, 공개 릴리스, 전역 설치, 새 세션 노출은 별도의 검증 결과입니다.
Claude와 AGY는 독립적으로 적용합니다. 공통 변경과 호스트 경계는 라이브러리의
[dev5 AGY 메타데이터 결정](https://github.com/codefoundry-io/triad-dispatch-lib/blob/859f27c07c1123e87b50344f587999a0cbc172a6/spec/decisions/2026-10-22-agy-result-metadata.md)을 참고하세요.

<a id="agy-리뷰-프로필-설정--반영-대기-후보"></a>

## AGY 리뷰 프로필 설정

0.2.559는 legacy/v2 정식 리뷰에 AGY 프로필 두 개를 요구합니다.
선택한 toolkit의 `bin/agents/` 파일을 검토한 뒤 루트에서 실행합니다.


두 프로필은 `excludeDefaultComponents: true`를 사용합니다. Raw 읽기 전용
조사를 포함한 읽기 전용 호출은 AGY 1.2.1 이상이 필요하며 raw는 research 프로필을
사용합니다. 이전 프로필 갱신은 두 파일의 변경을 검토한 뒤 같은 설치 명령에
`--replace`를 명시해야 합니다. 실행 중 자동 갱신하지 않습니다.
전역 설정과 이전 `.agybak`, lock, lease 파일은 자동 복원·삭제하지 않습니다.
요청한 웹 사용과 충돌하는 기존 URL 금지나 잘못된 설정은 수정 없이 거부합니다.
1.3.3 실측에서는 읽기·검색·웹과 쓰기 요청 시 파일 미생성을 확인했습니다.
쓰기 호출을 실행 단계에서 차단했다는 증거는 아닙니다.
0.2.559 업데이트 이전 비정상 종료로 `settings.json` 자체에 TRIAD deny가 남았을 수 있습니다.
남은 `.agybak`과 현재 설정을 비교해 확인된 TRIAD 잔여 항목만 직접 정리하고,
이후 사용자 변경은 보존하세요. 전체 백업을 무조건 덮어쓰지 않으며 TRIAD는 자동 복구하지 않습니다.

```sh
python3 bin/_agy_agent.py --install
```

쓰기 대상은 `~/.gemini/config/agents/triad-codex-readonly-review.md`와
`triad-codex-readonly-research.md`입니다. 권한 설정이나 Claude 호스트의
프로필은 변경하지 않습니다. 같은 파일은 유지하고, 내용이 다르면 검토 후
명시적 `--replace`가 필요합니다. 리뷰 실행 중 자동 설치하지 않습니다.
업데이트로 프로필 내용이 바뀌면 다시 설정해야 합니다. 제거할 때는 더 이상
사용하지 않는지 확인한 뒤 이 두 Codex 소유 파일만 직접 제거합니다.
bootstrap은 이 파일들의 설치·제거를 관리하지 않습니다.

preflight는 이름·경로·SHA-256을 결합하고 누락·변경 시 추론 전에 거부합니다.
일반 리뷰에는 읽기·검색 프로필, 승인된 `--web`에는 웹 도구가 추가된 프로필을
선택합니다. 모델·effort는 CLI로 전달합니다. 프로필만으로 권한 제한을 보장하지
않으며 기존 plan/sandbox와 결과 검증을 유지합니다. 버전·preflight 통과만으로
검색 성공을 보장하지 않습니다. 선택한 프로필에서 실제 네이티브 검색과 읽기가
성공해야 검색 기능을 확인할 수 있습니다.

## 설치할 버전 선택

아래 명령은 최신 공개 버전 경로인 `main`을 선택합니다.
[공개 릴리스](https://github.com/codefoundry-io/triad-codex-dispatch/releases)에서
버전별 다운로드와 체크섬을 확인할 수 있습니다. 같은 버전을 재현하려면 B 경로에서
릴리스 노트에 기록된 전체 커밋 ID를 checkout합니다.

## 준비 사항

macOS, Linux 또는 WSL2의 평소 로그인 터미널을 사용합니다. Git, Bash,
Python 3.12 이상, Codex, CLI가 해석하는 `opus` 리뷰 기본값용 Claude Code와
Google CLI 하나 이상이 필요합니다.

- AGY를 우선 사용하며 개인 Google Sign-In에는 AGY가 필요합니다.
- **Gemini 구버전 CLI 사용**은 AGY와 구분되는 `gemini` 실행 파일 경로를 뜻합니다.
  다운그레이드를 권하는 표현이 아닙니다. Gemini CLI는 `>=0.63.0`부터 지원하며, 정식 리뷰에는
  version/help/policy preflight 통과와 기존 Gemini Enterprise OAuth 로그인이
  필요합니다. 기존 selector는 AGY가 없을 때만 이 경로를 선택합니다.
  모든 모델과 raw·legacy·v2 경로에 같은 버전 하한을 적용합니다.
  [리뷰 구성 안내](../README.ko.md#프로젝트-리뷰어-설정-확인)를 참고하세요.

v2 Claude 경로는 Claude Code >=2.1.205를 요구하고 선택 전에 필요한 옵션을
확인합니다. 이는 v2 preflight 하한이며 raw·legacy에 새 버전 검사를 추가하지 않습니다.

[Claude Code 2.1.280에서 Opus 5.5가 추가됐습니다](https://github.com/anthropics/claude-code/releases/tag/v2.1.280).
이 특정 모델의 버전 요구사항은 현재 `opus` 별칭 기본값과 별개이며, 별칭은 실제
실행 모델의 고정 버전을 보증하지 않습니다. v2 adapter는 선택 전에 필요한 CLI
버전과 옵션을 확인합니다. raw/v2 경로에서는 명시적 모델 ID 선택을 유지합니다.
bootstrap은 실행 파일 존재를 확인하며 모델 사용 권한이나 실제 runtime effort를
확인하지는 않습니다.

각 CLI의 기본 로그인 절차로 인증합니다(Codex는 `codex login`). TRIAD는 계정을
설정하거나 인증 정보를 복사하지 않습니다. Linux/WSL2에서 Codex sandbox가 요구하면
`bubblewrap`도 설치하세요. Python 실행 의존성은 플러그인의 `requirements.txt`에
있습니다. bootstrap은 변경 전에 의존성을 확인하고, 없으면 정확한 설치 명령을 출력합니다.

bootstrap 실행 전에 `~/.local/bin`이 `PATH`에 있어야 합니다. 없다면 평소 사용하는
셸 시작 파일의 기존 내용을 보존하면서 다음 줄을 한 번만 추가하고, 새 로그인 터미널을
연 뒤 다음 단계로 진행하세요:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## A. 일반 마켓플레이스 설치

Git 저장소를 직접 다운로드하지 않아도 됩니다:

```bash
codex plugin marketplace add codefoundry-io/triad-codex-dispatch --ref main
```

이미 등록했다면 [업데이트](#업데이트)는 기존 경로와 추적 ref를 유지합니다.
경로나 ref를 바꿀 때(후보 브랜치에서 `main`으로 전환하는 경우 포함)는
[제거 절차](../README.ko.md#삭제)를 따라 설치된 bootstrap 제거, 플러그인 제거,
마켓플레이스 제거 순서로 진행합니다. 위 또는 아래의 선택한 경로를 등록한 뒤
다시 설치하세요. 다른 마켓플레이스와 개인 설정은 보존합니다.

## B. Git 다운로드 후 로컬 설치

검토할 프로젝트 밖에 저장소를 다운로드합니다. 이후 업데이트에 사용할 수 있도록
다운로드한 저장소를 유지하세요. 아래 대상 디렉터리는 아직 존재하지 않아야 합니다:

```bash
mkdir -p "$HOME/.local/share"
git clone --branch main --single-branch https://github.com/codefoundry-io/triad-codex-dispatch.git "$HOME/.local/share/triad-codex-dispatch"
git -C "$HOME/.local/share/triad-codex-dispatch" rev-parse HEAD
codex plugin marketplace add "$HOME/.local/share/triad-codex-dispatch"
```

검증된 특정 커밋을 사용하려면 브랜치를 다운로드한 다음, 마켓플레이스를 등록하기 전에
`git -C "$HOME/.local/share/triad-codex-dispatch" checkout --detach <전체-커밋-ID>`를
실행하세요. 자리표시자는 실제 전달받은 커밋으로 바꿉니다. Codex는 설치 캐시의 복사본을
사용하므로 다운로드한 소스만 수정해서는 설치본이 업데이트되지 않습니다.
`codex plugin add --path`는 지원되는 설치 명령이 아닙니다.

## 플러그인과 실행 환경 설치

A 또는 B를 선택한 뒤 같은 로그인 터미널에서 한 번 실행합니다:

```bash
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","add","triad-codex-dispatch@triad-codex-dispatch","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); root=pathlib.Path(data["installedPath"]); assert root.is_absolute(); print(shlex.join(["bash",str(root / "scripts" / "bootstrap.sh"),"--install"]))'
```

TRIAD를 사용할 프로젝트 workspace로 이동한 뒤 출력된 절대 경로의
`bash .../bootstrap.sh --install` 명령을 실행하세요. 홈 디렉터리, 플러그인 캐시나
다운로드한 플러그인 저장소에서 bootstrap을 실행하지 마세요. launcher, classifier,
Python, 플러그인 경로는 해당 workspace의 쓰기 허용 경로 밖에 있어야 합니다.
Python 의존성이 없다면 출력된 requirements 설치 명령을 사용할 Python 환경에서
실행한 뒤 같은 bootstrap 명령을 다시 실행합니다.

bootstrap은 공용 launcher 4개를 검증하여 `~/.local/bin`에 설치하고 보존 Codex
binding을 등록합니다. 지원하는 이관은 [공용 runtime 안내](shared-runtime.ko.md)를
따릅니다. `~/.config/triad-codex-dispatch/`에
classifier 파일을 설치합니다. 기존 Codex 설정, 권한 규칙과 인증 정보는 보존합니다.
로그인이나 의존성 설치를 자동으로 수행하지 않습니다.

## 개인 설정

1. **Codex 권한.** Codex에 TRIAD 실행을 요청하기 전에 `/permissions`에서 대화형
   workspace 정책을 선택합니다. 기존 설정 키를 사용하는 설치에서는
   `~/.codex/config.toml` 또는 신뢰한 프로젝트의 `.codex/config.toml` 중 하나에서
   다음 항목만 설정합니다:

   ```toml
   sandbox_mode = "workspace-write"
   approval_policy = "on-request"
   approvals_reviewer = "user"
   ```

   파일 전체를 덮어쓰거나 이미 있는 키를 중복 추가하지 말고 다른 항목과 테이블을
   보존하세요. 위 항목은 최상위 키이므로 `[table]` 헤더보다 앞에 둡니다. 우선순위가 높은
   설정은 사용자 값을 덮어쓸 수 있고 관리형 요구사항은 선택 가능한 값을 제한할 수 있습니다.
   현재 정책이 자동 검토를
   허용하면 `approvals_reviewer`만 `"auto_review"`로 바꿀 수 있습니다. 승인 검토자를
   바꾸는 설정이며 sandbox나 작업 권한을 확대하지 않습니다.
   새 permission-profile 시스템을 이미 사용한다면 해당 workspace profile을
   선택하고 위의 기존 키를 추가하지 마세요. `/status`로 적용 결과를 확인합니다.
   사용하는 Codex 빌드가 `/debug-config`를 제공하면 설정 우선순위도 확인할 수 있습니다.

2. **모델과 리뷰 설정.** 리더 모델은 Codex에서 선택합니다. v2 절차를 명시적으로
   사용한다면 [기본 리뷰 구성](../contracts/review-legs.default.json)을 확인하고
   대상 프로젝트의 `.agents/triad-review-legs.json`에 지원되는 override를 둡니다.
   기존 항목은 유지하세요. 인증은 리뷰 실행 시 별도로 선택하며, Gemini 구버전 CLI
   사용에 필요한 실제 인증 식별자는 `gemini-enterprise`입니다.
   실행 전에 [구성 확인](../README.ko.md#프로젝트-리뷰어-설정-확인)을 수행합니다.
   구성 확인 성공은 provider 접근권 증명이 아닙니다. Gemini에는 effort flag가
   없습니다. 0.2.559의 Public v2는 사용자의 상시 웹 허용을 새 라운드에 고정하며,
   요청값 생략·false로 이를 철회하지 않습니다. 활성 native Codex leg는
   `web_available: true`를 보고해야 합니다. Legacy는 해당 라운드에 직접 요청한
   경우에만 웹을 허용합니다. 기존 설치에 적용하려면 플러그인을 업데이트하세요.

3. **선택 경로.** 기본 설치에는 추가 환경변수가 필요하지 않습니다.
   `TRIAD_BOOTSTRAP_BIN_DIR` 또는 `TRIAD_CLASSIFIER_EXTENSION`을 바꾼다면
   검토할 workspace 밖의 절대 경로를 사용하고 bootstrap을 다시 실행하세요.
   과거의 `triad-setup`, `triad-doctor`, repair-agent, `shell_environment_policy`
   설정 조각을 추가하지 마세요. 현재 설치 절차에 포함되지 않습니다.

설정 근거: [Codex 설정](https://learn.chatgpt.com/docs/config-file/config-basic),
[sandbox와 승인](https://learn.chatgpt.com/docs/sandboxing),
[permission profiles](https://learn.chatgpt.com/docs/permissions),
[로컬 플러그인 경로](https://developers.openai.com/plugins/build/plugins).

<a id="gemini-cli-38-high"></a>

### Gemini CLI 3.8 Flash 설정

확인일: **2026-10-02**. Native Gemini CLI에서는 `gemini-3.8-flash`를 요청합니다.
AGY의 `gemini-3.8-flash-high`는 별도 선택 slug입니다. 2026-10-09 사용자 결정에
따라 TRIAD의 모든 Gemini 모델과 raw·legacy·v2 경로는 **CLI 0.63.0부터**
지원합니다. 필요하면 기존 CLI 설치 방식으로 업데이트하세요. 모델 목록 조회나
모델별 허용 목록은 사용하지 않습니다. preview/nightly 실행 호환성은 미검증이며,
0.63.0 prerelease는 지원 하한보다 낮습니다. 이전 모델별 하한은 이 결정으로
대체됐습니다. 0.60.0에는 3.8 alias가 없고 `flash`로 끝나는
문자열을 이전 모델로 바꿀 수 있습니다
([태그가 고정된 routing 소스](https://github.com/google-gemini/gemini-cli/blob/v0.60.0/packages/core/src/config/models.ts#L230-L270)).

아래 native 설정 안내는 2026-10-02에 v0.61.0 소스로 확인한 내용입니다.
설정과 alias 동작은 v0.63.0에서 재검증이 필요하며, 과거 설정 근거가 현재
런타임 동작을 증명하지는 않습니다.

Native 대화형 세션에서는 `gemini --model gemini-3.8-flash`로 정확한 ID를 요청합니다.
v0.61.0 기본 alias는 **HIGH** generation 설정을 상속합니다
([태그가 고정된 기본값](https://github.com/google-gemini/gemini-cli/blob/v0.61.0/packages/core/src/config/defaultModelConfigs.ts#L31-L140)).
HIGH는 CLI effort flag가 아니며 provider 내부 추론 동작의 증명도 아닙니다.

선택을 저장하려면 기존 `~/.gemini/settings.json` 또는
`<project-root>/.gemini/settings.json`에 아래 항목을 병합하세요. 프로젝트 설정이
사용자 설정보다 우선합니다
([태그가 고정된 설정 문서](https://github.com/google-gemini/gemini-cli/blob/v0.61.0/docs/reference/configuration.md#L44-L60)).
다른 필드는 보존하세요. CLI `--model`이나 `GEMINI_MODEL` 값이 이를 덮어쓸 수 있습니다.

```json
{"model": {"name": "gemini-3.8-flash"}}
```

명시적 HIGH 설정은 선택 사항이며 기존의 낮은 설정을 덮어쓸 때 사용할 수 있습니다.
아래 필드를 병합하고 기존 `customOverrides` 배열에 규칙을 **추가**하세요.
기존 배열이나 파일 전체를 교체하지 마세요. 지원되는 구조는
[태그가 고정된 설정 schema](https://github.com/google-gemini/gemini-cli/blob/v0.61.0/packages/cli/src/config/settingsSchema.ts#L1144-L1192)에 정의되어 있습니다.

```json
{
  "model": {"name": "gemini-3.8-flash"},
  "modelConfigs": {
    "customOverrides": [{
      "match": {"model": "gemini-3.8-flash"},
      "modelConfig": {
        "generateContentConfig": {
          "thinkingConfig": {"thinkingLevel": "HIGH"}
        }
      }
    }]
  }
}
```

`previewFeatures`나 `experimental.dynamicModelConfiguration` 활성화는 필요 없습니다.
Dynamic 설정, alias, rollout은 실제 적용 ID를 바꿀 수 있으며 더 구체적인 규칙이나
runtime override도 우선할 수 있습니다.
[태그가 고정된 ID resolver](https://github.com/google-gemini/gemini-cli/blob/v0.61.0/packages/core/src/config/models.ts#L234-L363)를 참고하세요.

TRIAD v2에서는 `.agents/triad-review-legs.json`의 **기존 선택된 Google entry**에
`"gemini": {"model": "gemini-3.8-flash", "effort": null}`을 병합합니다.
entry 이름, 다른 entry와 route/authentication 선택은 보존하며 배포 기본 roster는
변경하지 않습니다. 위 CLI 설정은 Gemini JSON 파일에 두고 TRIAD roster에 새로운
키로 넣지 마세요. 필수 인증 경로를 유지해야 하며 API key는 TRIAD의 Enterprise
OAuth 경계를 우회하는 수단이 아닙니다.

새 provider 요청 없이 `gemini --version`을 실행하고 적용되는 설정 및
`--model`/`GEMINI_MODEL` override를 확인하세요. **이미 열린** Gemini 세션에서는
prompt를 보내지 않고 `/model` 화면을 확인할 수 있습니다. 이는 binary 버전과
선택·요청 모델을 보여주며 backend 접근권이나 실제 runtime 모델을 증명하지 않습니다.
모델을 명시한 subagent는 해당 선택을 유지합니다. Custom subagent의 기본값은
`inherit`이며 main session 모델을 사용합니다
([v0.61.0 subagent schema](https://github.com/google-gemini/gemini-cli/blob/v0.61.0/docs/core/subagents.md#configuration-schema)).

## 설치 확인

`codex plugin list --json`에서 TRIAD의 설치 버전을 확인하세요. 대상 프로젝트에서
`command -v review_round.py`가 공용 launcher를 가리키는지 확인하고 canonical plugin
root로 `python3 "$plugin_root/bin/shared_runtime.py" resolve --plugin-root "$plugin_root" --json`을
실행해 보존 toolkit과 binding을 검증합니다. 명령 이름만으로 Codex를 식별하지 않습니다.
**새 Codex 세션**을 열고 TRIAD 스킬 4개가 보이는지 확인합니다.
`.agents/skills/`에 같은 스킬을 별도로 복사하지 마세요.

선택한 provider의 설치된 스킬로 작은 읽기 전용 질문 하나를 요청합니다.
Gemini 구버전 CLI 사용은 `triad-gemini-dispatch`, AGY는
`triad-antigravity-dispatch`를 사용합니다. 설치와 스킬 인식만으로 실제 인증이나
정책 적용이 증명되지는 않습니다. 선택한 경로에서 기본 리뷰, 읽기 허용,
쓰기·셸 실행 차단, 직접 요청한 웹 허용을 각각 확인하세요.

## 업데이트

직접 launcher를 처음 공용으로 이관할 때는 새로 검증한 bootstrap이 기존 legacy
binding을 검증·보존할 때까지 원래 launcher 네 개와 toolkit을 유지합니다. 기존
제거 스크립트를 먼저 실행하지 마세요. Plugin manager가 이전 cache를 유지할 수
없으면 검증한 릴리스를 안정된 로컬 Git 경로(경로 B)에 두고 새 bootstrap을 먼저
실행한 뒤 cache를 교체합니다. 직접 라운드나 보존 legacy 대상이 사용하는 원래
cache는 유지하며 최종 설치 root에서도 bootstrap을 실행해 등록합니다.
[보장 범위](shared-runtime.ko.md#라운드-업데이트와-제거)를 확인하세요.

이미 공용으로 설치된 cache를 교체하려면 먼저 해당 bootstrap의 제거 명령을 출력합니다:

```bash
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","list","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); item=next(item for item in data["installed"] if item["pluginId"]=="triad-codex-dispatch@triad-codex-dispatch"); root=pathlib.Path(item["source"]["path"]); assert root.is_absolute(); print(shlex.join(["bash",str(root / "scripts" / "bootstrap.sh"),"--remove"]))'
```

캐시를 삭제하기 전에 출력된 명령을 실행하세요. 해당 설치 receipt만 등록 해제하고
공용 명령·binding·자산, 사용자 작성 설정과 학습된 classifier patch를 보존합니다.
제거가 실패하면 보고된 문제를 해결한 뒤 계속하세요.
마켓플레이스 등록을 유지하면서 해당 플러그인만 제거합니다:

```bash
codex plugin remove triad-codex-dispatch@triad-codex-dispatch
```

등록된 소스를 갱신합니다:

- **Git 원격 마켓플레이스:**
  `codex plugin marketplace upgrade triad-codex-dispatch`를 실행합니다.
- **로컬 Git 다운로드:**
  `git -C "$HOME/.local/share/triad-codex-dispatch" pull --ff-only`로 소스를 받습니다.
  Marketplace upgrade는 Git 원격 등록을 갱신하며 로컬 디렉터리에는 사용하지 않습니다.
  특정 커밋에 detached 상태로
  고정했다면 pull 대신 fetch 후 다음 검증된 전체 커밋을 선택합니다. 로컬 수정은 보존하세요.

두 경로 모두 위의 플러그인 설치 명령을 다시 실행하고, 새로 출력된 bootstrap 명령을
대상 프로젝트에서 실행한 뒤 새 Codex 세션을 시작합니다. Provider CLI 실행 파일을
이동하거나 업그레이드한 뒤에도 bootstrap을 다시 실행하세요.
