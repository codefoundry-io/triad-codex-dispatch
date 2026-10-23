# 공용 명령과 호스트 하위호환성

[English](shared-runtime.md) · [설치 안내](installation.ko.md)

0.2.564부터 `~/.local/bin`의 공용 명령 네 개로 명시적으로 등록한 여러 호스트를
사용할 수 있습니다. 공통 라이브러리는 binding 식별, 호환성, 선택과 보존을
판정하며 각 호스트는 native spawn, 모델, effort, 인증과 provider adapter를
관리합니다. Codex 설치로 기존 AGY 기본 호출이 Codex로 바뀌지 않습니다.

## 설치와 선택

설치 안내에 따라 작업할 project에서 설치된 `scripts/bootstrap.sh --install`을
실행합니다. 네 명령이 모두 없으면 첫 Codex 기본값을 만듭니다. 검증된 직접 Codex
또는 지원 AGY launcher가 있으면 원래 payload·대상·기본값을 보존하고 Codex
binding을 추가합니다. 이미 공용 generation이면 기존 binding과 기본값을 유지합니다.
일부만 존재하거나 서로 다른 출처, 수정된 파일, 알 수 없는 형식이면 교체를 거부합니다.

지원하는 직접 AGY 기준은 커밋 `00f255826e894b82105d2b32e68b209d761f964b`의
runtime 파일 80개입니다. canonical inventory SHA-256은
`1b40aaf00c786a4595333a0d389cb6fba5d51ee002dc04f8e1c2add7500a6d83`입니다.
marker만으로 인정하지 않으며 launcher 구조, 고정 context의 일관성, 전체 파일
목록과 바이트, 일반 파일 여부와 안전한 상위 경로를 검증합니다. 다른 AGY 버전은
독립적으로 검토한 기준 추가가 필요합니다.

불변 snapshot·binding·generation은 `~/.local/share/triad-dispatch-runtime`에,
Codex 설치 receipt는 `~/.local/share/triad-codex-dispatch/installations`에 둡니다.
공용 명령 네 개와 새 receipt를 하나의 rollback transaction으로 게시합니다.
네 파일이 동시에 원자적으로 교체된다는 뜻은 아니며 전환 중에도 기존 entry와
보존한 자산을 사용할 수 있습니다.

설치된 skill의 canonical plugin root를 확인한 뒤 resolver를 실행합니다.

```sh
python3 "$plugin_root/bin/shared_runtime.py" resolve --plugin-root "$plugin_root" --json
```

응답은 JSON 데이터로 읽고 shell 코드로 실행하지 않습니다. 검증된 `binding_id`,
`toolkit_root`, `launcher_dir`, 실행 context와 provenance를 사용합니다. 같은
plugin root에 서로 다른 context가 있으면 `--binding ID`로 명시해야 합니다.
최신 receipt나 PATH 순서로 고르지 않습니다. 잘못되거나 알 수 없거나 변경되거나
모호한 선택은 provider 실행 전에 거부합니다. 공용 명령의 무인자 기본 선택은
기존 legacy binding만 따릅니다.

공용 명령을 명시적으로 사용할 때만 해당 호출에 binding을 지정합니다.

```sh
TRIAD_RUNTIME_BINDING="$binding_id" review_round.py --help
```

전역 shell export는 추가하지 않습니다. 설치된 skill은 검증된 binding별 hardened
launcher로 interpreter, provider 경로, trusted PATH와 classifier 경로를 적용합니다.
classifier의 학습 내용은 기존 정책대로 변경할 수 있습니다. 인자·표준 입출력·종료
상태는 그대로 전달합니다.

## 라운드, 업데이트와 제거

라운드 준비 전에 한 번 선택하고 모든 helper·schema·reference·receipt에 같은
보존 toolkit을 사용합니다. Public v2는 `runtime_binding`과 실행 context를 봉인하고
불변 launcher allocation을 반환하며 retry와 collection에서도 같은 context를
검증합니다. 이후 공용 launcher 갱신, 설치 receipt 또는 원래 plugin cache 제거가
그 라운드의 실행 대상을 바꾸지 않습니다. Native Codex spawn 계약은 유지합니다.

plugin이나 provider 경로가 바뀌면 bootstrap을 다시 실행합니다. 같은 root·context는
binding을 재사용하고 새 root·context는 이전 binding을 보존합니다. `--remove`는
해당 설치 receipt만 등록 해제하며 공용 명령, 다른 consumer와 보존 자산을 유지합니다.
활성 의존성을 확정할 수 없으면 모두 보존하고 자동 GC하지 않습니다.

보장 범위에는 다음 제한이 있습니다.

- 이관 전에 직접 cache 경로로 시작한 라운드는 원래 cache가 필요합니다. 기존
  receipt를 새 toolkit 경로로 바꾸지 않습니다.
- 보존된 AGY legacy 대상은 원래 AGY 설치를 필요로 합니다. 독립적인 구버전 AGY
  installer/remover의 동작은 이 설치 프로그램이 관리하지 않습니다.
- 외부 Python 환경·user-site 의존성·provider 실행 파일·인증은 소유자가 관리합니다.
- Source-SOT 개발은 기존 격리 stage에서 직접 source를 사용하며 공용 binding을
  등록하거나 설치 receipt를 조회하지 않습니다.

Claude와 AGY는 각 호스트의 설치와 라운드 고정 경로를 별도로 적용한 뒤 독립적인
업데이트·제거 호환성을 검증해야 합니다. 실행 절차는
[설치된 skill 지침](../skills/triad-cross-family-review/references/shared-runtime.md)을
따릅니다. 소스 검사, 합성 dispatch, 실제 provider 동작, 공개 배포와 새 세션 skill
노출은 각각 별도 증거입니다.
