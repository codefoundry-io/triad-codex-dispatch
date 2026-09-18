# AGY Terminal Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Preserve bounded terminal AGY error detail without changing failure behavior.

**Architecture:** A pure helper selects a bounded string from the last terminal
result. Existing failure branches append its suffix after classification. No
provider, logger, or shared result-schema interface changes.

**Tech Stack:** Python 3.12+, stdlib JSON, existing pytest/Pydantic test fixtures.

**Spec:** `docs/superpowers/specs/2026-09-18-dispatch-adoption-design.md`, S2.

## Global Constraints

- One behavioral claim: failure diagnostic preservation only; production/core
  net delta <50 lines. No new dependencies or abstraction layer.
- Codex remains native. Preserve AGY project guard, selector receipts, native
  plan/schema validation, formal single-provider-call and existing success exceptions.
- Preserve timeout, missing-result, success and classification behavior. The
  nonzero-vendor path must classify original stderr/status before adding detail.
- Retain existing audit redaction/caps and sensitive failure-log handling.
- Work in the existing checkout on `codex/triad-adoption-agy-diagnostics`, based
  on `46dab9f388ff0a3992a2889061aa2563b74d11c0`. Preserve dirty `AGENTS.md` and S1.
- No live providers, global settings, bundled-skill edits, installation, release,
  formal admission, or merge. Stage only task-owned files.

### Task 1: preserve terminal error detail at the existing failure boundary

**Files:**

- Modify `bin/antigravity_wrapper.py`: pure suffix helper and two failure details.
- Modify `tests/test_antigravity_stream_json.py`: interpreter regression cases.
- Modify `README.md` and `README.ko.md`: runtime-log paragraph.
- Modify `SECURITY.md`: diagnostic-data limit in the repair-boundary section.

**Interfaces:**

- Consume existing `parse_agy_stream` last-result dictionary, `_interpret_run`,
  `_run_result`, `_stream`, and current `_fail`/`RunResult` interfaces.
- Produce `_terminal_error_suffix(result: dict[str, Any] | None) -> str`.
- Emit no diagnostic suffix unless a permitted nonempty string is found.

- [ ] **Step 1: add causal regression tests, then run RED.**

Use existing helpers; insert tests near the current non-success result tests.
The primary test should preserve classification by comparing the same failing
invocation with and without terminal diagnostic data, rather than assuming all
nonzero provider exits have the same classification.

```python
@pytest.mark.parametrize("rc", [0, 1])
@pytest.mark.parametrize("error,summary", [
    ("backend failed", "backend failed"),
    ({"code": "RESOURCE_EXHAUSTED", "message": "backend failed"}, "backend failed"),
    ({"message": "", "error": "denied", "detail": "later"}, "denied"),
    ({"message": {"private": "hidden"}, "code": "UNAVAILABLE"}, "UNAVAILABLE"),
])
def test_terminal_diagnostic_retains_typed_error_without_reclassification(rc, error, summary):
    payload = {"status": "ERROR", "response": "never admit this"}
    baseline = wrapper._interpret_run(_run_result(_stream(payload), rc=rc), None)
    result = wrapper._interpret_run(_run_result(_stream({**payload, "error": error}), rc=rc), None)
    assert (result.classification, result.exit_code) == (baseline.classification, baseline.exit_code)
    assert result.final_answer == ""
    assert result.extraction_error == baseline.extraction_error + "; terminal_error=" + summary


@pytest.mark.parametrize("error", [None, 42, [], {"nested": {"message": "hidden"}}, {"code": False}, " \n\t "])
def test_terminal_diagnostic_ignores_unsupported_or_empty_values(error):
    result = wrapper._interpret_run(_run_result(_stream({"status": "ERROR", "error": error})), None)
    assert result.extraction_error == "terminal result status is 'ERROR'"
    assert result.classification == "vendor-error"
    assert result.exit_code == _common.EXIT_TERMINAL


def test_terminal_diagnostic_is_one_bounded_nonempty_line():
    error = {"message": " \n  " + "x" * 700 + "\nprivate second line", "code": "later"}
    result = wrapper._interpret_run(_run_result(_stream({"status": "ERROR", "error": error})), None)
    assert result.extraction_error == "terminal result status is 'ERROR'; terminal_error=" + "x" * 512


@pytest.mark.parametrize("error", ["rate limit exceeded", "invalid authentication credentials"])
def test_terminal_diagnostic_does_not_feed_nonzero_exit_classifier(error):
    payload = {"status": "ERROR"}
    baseline = wrapper._interpret_run(_run_result(_stream(payload), rc=1), None)
    result = wrapper._interpret_run(_run_result(_stream({**payload, "error": error}), rc=1), None)
    assert (result.classification, result.exit_code) == (baseline.classification, baseline.exit_code)
    assert result.extraction_error.endswith("; terminal_error=" + error)


def test_terminal_diagnostic_does_not_annotate_success():
    result = wrapper._interpret_run(_run_result(_stream({"status": "SUCCESS", "response": "done", "error": "ignored"})), None)
    assert result.exit_code == _common.EXIT_OK
    assert result.final_answer == "done"
    assert result.extraction_error is None
```

Add `assert admitted.extraction_error is None` to the existing formal
post-completion permission-denial success test. Adapt wrapping/type annotations
to the file's style without changing these behavioral assertions.

Run from `/Users/chaniri/codex_workspace`:

```sh
/bin/zsh -lic 'python3 -m pytest -q "$1/tests/test_antigravity_stream_json.py" -k terminal_diagnostic --rootdir "$1" -p no:cacheprovider' triad-tests /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
```

Expected RED: missing `terminal_error` suffix on supported error cases; no
fixture, import, or provider failure counts as the intended RED.

- [ ] **Step 2: implement the pure selection helper.**

Place beside `parse_agy_stream`, using the existing `Any` import:

```python
def _terminal_error_suffix(result: dict[str, Any] | None) -> str:
    error = result.get("error") if result is not None else None
    if isinstance(error, str):
        candidates = (error,)
    elif isinstance(error, dict):
        candidates = tuple(error.get(key) for key in ("message", "error", "detail", "code"))
    else:
        return ""
    for value in candidates:
        if not isinstance(value, str):
            continue
        for raw_line in value.splitlines():
            line = raw_line.strip()
            if line:
                return f"; terminal_error={line[:512]}"
    return ""
```

In the nonzero-vendor branch, leave `detail` construction and `classify` inputs
unchanged. Replace only the final `_fail` detail argument with:

```python
(detail or "AGY exited without an admissible result") + _terminal_error_suffix(result)
```

In the non-success branch after `denied_post_completion` handling, replace only
the `_fail` detail argument with:

```python
f"terminal result status is {status!r}" + _terminal_error_suffix(result)
```

- [ ] **Step 3: run GREEN and affected integration tests.**

Run the focused command again, then the whole affected module and distribution
contracts after the docs step. Existing main/formal tests cover unchanged
single-call dispatch, schema bindings, timeout and permission-denial admission.

- [ ] **Step 4: document the exact diagnostic contract.**

Add under Runtime Logs And Local Data in `README.md`:

> AGY terminal failures may add `terminal_error` to `extraction_error`: the first nonempty line from a string error or the first usable string field among `message`, `error`, `detail`, and `code`, capped at 512 characters. This is diagnostic data; classification, retries, and admission are unchanged. Existing audit redaction/capping still applies to the combined field, and failure run logs remain sensitive untrusted data.

Add the equivalent under Runtime Log 및 Local Data in `README.ko.md`:

> AGY terminal failure는 `extraction_error`에 `terminal_error`를 덧붙일 수 있습니다. 문자열 오류 또는 `message`, `error`, `detail`, `code` 순서에서 처음 찾은 유효한 문자열의 첫 비어 있지 않은 줄을 최대 512자로 보존합니다. 진단 데이터이며 분류·재시도·admission은 바뀌지 않습니다. 합쳐진 필드에는 기존 audit redaction과 길이 제한이 적용되고, failure run log는 계속 민감한 untrusted data입니다.

Add one sentence in `SECURITY.md` Repair boundary:

> Bounded AGY terminal-error summaries remain untrusted diagnostic data under the existing audit redaction and failure-log retention rules; they do not drive classification, retries, or admission.

Wrap prose to surrounding style. Do not revise historical changelogs or logger
code. No migration is required because no option, schema, or settings change.

```sh
/bin/zsh -lic 'python3 -m pytest -q "$1/tests/test_antigravity_stream_json.py" "$1/tests/test_distribution_contract.py" --rootdir "$1" -p no:cacheprovider' triad-tests /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
```

- [ ] **Step 5: full verification once, self-review, and exact-file commit.**

```sh
/bin/zsh -lic 'python3 -m pytest -q "$1/tests" --rootdir "$1" -p no:cacheprovider' triad-tests /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
```

Do not rerun the already-proven 810-test S1 baseline. Run the full suite once
after final S2 changes. Inspect the diff, then commit only the five owned files
with subject `fix: retain bounded AGY terminal error diagnostics`.

Write the requested SDD report with exact RED/GREEN/full-suite commands and
terminal results, commit, net production delta, owned files, and any concerns.
The leader supplies fresh task and final reviewers; do not spawn reviewers.
