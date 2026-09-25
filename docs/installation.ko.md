# 설치와 개인 설정

[English](installation.md) · [README](../README.ko.md)

**일반 마켓플레이스 설치** 또는 **Git 다운로드 후 로컬 설치** 중 하나를 선택합니다.
두 방식은 같은 플러그인과 공통 실행 환경 설정을 사용합니다. 같은 마켓플레이스 이름으로
두 경로를 중복 등록하지 마세요.

## 설치할 버전 선택

아래 명령은 최신 공개 버전 경로인 `main`을 선택합니다.
[v0.2.557 릴리스](https://github.com/codefoundry-io/triad-codex-dispatch/releases/tag/v0.2.557)에서
버전별 다운로드와 체크섬을 확인할 수 있습니다. 같은 버전을 재현하려면 B 경로에서
릴리스 노트에 기록된 전체 커밋 ID를 checkout합니다.

## 준비 사항

macOS, Linux 또는 WSL2의 평소 로그인 터미널을 사용합니다. Git, Bash,
Python 3.12 이상, Codex, 기본 Opus 5.5 경로용 Claude Code 2.1.280 이상과
Google CLI 하나 이상이 필요합니다.

- AGY를 우선 사용하며 개인 Google Sign-In에는 AGY가 필요합니다.
- **Gemini 구버전 CLI 사용**은 AGY와 구분되는 `gemini` 실행 파일 경로를 뜻합니다.
  다운그레이드를 권하는 표현이 아닙니다. 정식 리뷰에는 Gemini CLI `>=0.34.0`,
  version/help/policy preflight 통과와 기존 Gemini Enterprise OAuth 로그인이
  필요합니다. 기존 selector는 AGY가 없을 때만 이 경로를 선택합니다.
  v2 Pro 기본 모델에는 별도 버전 지원 검사가 있습니다.
  [리뷰 구성 안내](../README.ko.md#프로젝트-리뷰어-설정-확인)를 참고하세요.

[Claude Code 2.1.280에서 Opus 5.5가 추가됐습니다](https://github.com/anthropics/claude-code/releases/tag/v2.1.280).
이 릴리스는 2.1.282로 확인했습니다. v2 adapter의 기존 preflight 인터페이스
최소 버전은 이 모델 요구사항과 별개입니다. bootstrap은 실행 파일 존재를 확인하며
모델 사용 권한이나 실제 runtime effort를 확인하지는 않습니다. 새 기본 모델을
사용하기 전에 Claude Code를 업데이트하세요.

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

bootstrap은 `~/.local/bin`에 launcher 4개를, `~/.config/triad-codex-dispatch/`에
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
   없습니다. 기본 리뷰는 웹을 사용하지 않으며 필요한 해당 라운드에 직접 웹 검증을
   요청해야 합니다.

3. **선택 경로.** 기본 설치에는 추가 환경변수가 필요하지 않습니다.
   `TRIAD_BOOTSTRAP_BIN_DIR` 또는 `TRIAD_CLASSIFIER_EXTENSION`을 바꾼다면
   검토할 workspace 밖의 절대 경로를 사용하고 bootstrap을 다시 실행하세요.
   과거의 `triad-setup`, `triad-doctor`, repair-agent, `shell_environment_policy`
   설정 조각을 추가하지 마세요. 현재 설치 절차에 포함되지 않습니다.

설정 근거: [Codex 설정](https://learn.chatgpt.com/docs/config-file/config-basic),
[sandbox와 승인](https://learn.chatgpt.com/docs/sandboxing),
[permission profiles](https://learn.chatgpt.com/docs/permissions),
[로컬 플러그인 경로](https://developers.openai.com/plugins/build/plugins).

## 설치 확인

`codex plugin list --json`에서 TRIAD의 설치 버전을 확인하세요. 대상 프로젝트에서
`command -v review_round.py`가 설치된 launcher를 가리키는지 확인한 다음
**새 Codex 세션**을 열고 TRIAD 스킬 4개가 보이는지 확인합니다.
`.agents/skills/`에 같은 스킬을 별도로 복사하지 마세요.

선택한 provider의 설치된 스킬로 작은 읽기 전용 질문 하나를 요청합니다.
Gemini 구버전 CLI 사용은 `triad-gemini-dispatch`, AGY는
`triad-antigravity-dispatch`를 사용합니다. 설치와 스킬 인식만으로 실제 인증이나
정책 적용이 증명되지는 않습니다. 선택한 경로에서 기본 리뷰, 읽기 허용,
쓰기·셸 실행 차단, 직접 요청한 웹 허용을 각각 확인하세요.

## 업데이트

설치 캐시를 확실히 교체하려면 먼저 현재 설치된 bootstrap의 제거 명령을 출력합니다:

```bash
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","list","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); item=next(item for item in data["installed"] if item["pluginId"]=="triad-codex-dispatch@triad-codex-dispatch"); root=pathlib.Path(item["source"]["path"]); assert root.is_absolute(); print(shlex.join(["bash",str(root / "scripts" / "bootstrap.sh"),"--remove"]))'
```

캐시를 삭제하기 전에 출력된 명령을 실행하세요. 사용자 작성 설정과 학습된 classifier
patch는 보존됩니다. 제거가 실패하면 보고된 문제를 해결한 뒤 계속하세요.
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
