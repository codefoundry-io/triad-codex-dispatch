# AGY Output Contract and Transcript Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every Pydantic AGY call one non-contradictory transport-frame contract and reject explicitly truncated AGY transcript answers so the existing PTY fallback can recover the complete response.

**Architecture:** Shared schema helpers keep their current JSON-only default for Claude and Gemini. AGY explicitly requests schema-body semantics, then one wrapper-local sealer owns the complete JSON-plus-sentinel transport contract for initial and repair prompts. Transcript scanning keeps its current ownership API but maps a terminal DONE whose `truncated_fields` contains `content` to no transcript answer, activating the existing PTY fallback.

**Tech Stack:** Python 3, Pydantic 2, pytest.

## Global Constraints

- Preserve all pre-existing dirty-tree changes.
- Do not change non-AGY default prompt output or non-Pydantic AGY behavior.
- Do not change response schemas, sentinel identity, transcript ownership, IPC, or provider dependencies.
- Use only one AGY Pydantic transport-frame renderer.
- Keep the patch bounded to `bin/_common.py`, `bin/antigravity_wrapper.py`, and their focused tests.
- Do not commit, push, install, or edit the installed plugin cache in this task.

---

### Task 1: Add AGY-only schema-body semantics

**Files:**
- Modify: `bin/_common.py:884-977`
- Modify: `bin/antigravity_wrapper.py:167-184`
- Test: `tests/test_formal_review_schema.py:430-475`
- Test: `tests/test_antigravity_packet_context.py:372-400`

**Interfaces:**
- Consumes: existing Pydantic classes and current shared JSON-only prompt behavior.
- Produces: `schema_block_for_prompt(cls, *, body_semantics_only=False)` and `inject_schema_to_prompt(prompt, cls, *, body_semantics_only=False)`; AGY selects `True`.

- [x] **Step 1: Write failing helper tests**

```python
def test_generic_body_semantics_mode_omits_transport_framing() -> None:
    class GenericPromptModel(BaseModel):
        value: str

    prompt = _common.inject_schema_to_prompt(
        "USER REQUEST",
        GenericPromptModel,
        body_semantics_only=True,
    )

    assert '"value": <string>' in prompt
    assert '{"value": "<value>"}' in prompt
    assert "USER REQUEST" in prompt
    assert "valid JSON and nothing else" not in prompt
    assert "Return ONLY the JSON object" not in prompt
    assert "No markdown fences" not in prompt


def test_formal_review_body_semantics_mode_omits_transport_framing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    schema = _load_canonical(monkeypatch)

    prompt = _common.inject_schema_to_prompt(
        "LONG USER REQUEST",
        schema,
        body_semantics_only=True,
    )

    assert "LONG USER REQUEST" in prompt
    assert "complete canonical FormalReview JSON Schema" in prompt
    assert "no surrounding content" not in prompt
    assert not prompt.rstrip().endswith("JSON:")
```

- [x] **Step 2: Verify RED**

Run:

```text
/private/tmp/triad-reliability-venv-20260722/bin/python -m pytest -q \
  tests/test_formal_review_schema.py::test_generic_body_semantics_mode_omits_transport_framing \
  tests/test_formal_review_schema.py::test_formal_review_body_semantics_mode_omits_transport_framing \
  -p no:cacheprovider
```

Expected: both tests fail because the keyword-only body-semantics mode does not exist.

- [x] **Step 3: Implement the minimal mode**

Change the two signatures exactly:

```diff
-def schema_block_for_prompt(cls) -> str:
+def schema_block_for_prompt(
+    cls,
+    *,
+    body_semantics_only: bool = False,
+) -> str:

-def inject_schema_to_prompt(prompt: str, cls) -> str:
+def inject_schema_to_prompt(
+    prompt: str,
+    cls,
+    *,
+    body_semantics_only: bool = False,
+) -> str:
```

After the existing generic `shape_line` and `dummy` construction, insert this
branch before the existing JSON-only return:

```python
if body_semantics_only:
    return (
        "The JSON body must match exactly this shape:\n"
        f"{shape_line}\n\n"
        "JSON body example:\n"
        f"{json.dumps(dummy, ensure_ascii=False)}\n\n"
        "Use the user's request below to determine the JSON body values."
    )
```

In `inject_schema_to_prompt()`, pass the flag to `schema_block_for_prompt()` and
use the following exact FormalReview branch:

```python
block = schema_block_for_prompt(
    cls,
    body_semantics_only=body_semantics_only,
)
if (
    cls.__module__ == _PACKAGED_FORMAL_REVIEW_MODULE
    and cls.__name__ == "FormalReview"
):
    final_rule = (
        "The FormalReview JSON body must satisfy the response contract above."
        if body_semantics_only
        else (
            "Based on the user request and FormalReview contract above, return "
            "exactly one valid JSON object with no surrounding content.\nJSON:"
        )
    )
    return (
        "=== USER REQUEST ===\n"
        f"<runtime_review_input>\n{prompt}\n</runtime_review_input>\n\n"
        "The runtime material above determines review scope and evidence. The "
        "FormalReview response contract below controls the output shape.\n\n"
        f"=== FORMAL REVIEW RESPONSE CONTRACT ===\n{block}\n\n"
        f"{final_rule}"
    )
if body_semantics_only:
    return f"{block}\n\n=== USER REQUEST ===\n{prompt}"
return f"{block}\n\n=== USER REQUEST ===\n{prompt}\n\nJSON:"
```

AGY composition must call:

```python
effective = inject_schema_to_prompt(
    effective,
    pydantic_cls,
    body_semantics_only=True,
)
```

- [x] **Step 4: Verify GREEN and shared-default compatibility**

Run:

```text
/private/tmp/triad-reliability-venv-20260722/bin/python -m pytest -q \
  tests/test_formal_review_schema.py \
  tests/test_provider_packet_context.py \
  -p no:cacheprovider
```

Expected: all selected tests pass, including the existing exact generic-default string test.

---

### Task 2: Use one canonical AGY Pydantic sealer for initial and repair prompts

**Files:**
- Modify: `bin/antigravity_wrapper.py:93-135,269-416,576-611`
- Test: `tests/test_antigravity_packet_context.py:372-424,820-890`

**Interfaces:**
- Consumes: one unsealed AGY schema-body prompt and a per-invocation sentinel.
- Produces: `_seal_pydantic_prompt(unsealed_prompt: str, sentinel: str) -> str`; `_repair_cmd(cmd, unsealed_prompt, err, sentinel)` replaces only the `-p` value.

- [x] **Step 1: Write failing initial and repair tests**

The initial test records that AGY requested body semantics and checks the final `-p` value:

```python
assert seen_body_semantics == [True]
assert sealed.count("Your complete response must contain exactly two parts:") == 1
assert sealed.count(f"<<<{sentinel}>>>") == 1
assert sealed.index("SCHEMA BODY") < sealed.index(
    "Your complete response must contain exactly two parts:"
)
assert "valid JSON and nothing else" not in sealed
assert "no surrounding content" not in sealed
```

The repair test inspects the second PTY argv:

```python
repair_prompt = pty_calls[1][pty_calls[1].index("-p") + 1]
assert repair_prompt.count("SCHEMA BODY") == 1
assert repair_prompt.count("packet digest mismatch") == 1
assert repair_prompt.count(
    "Your complete response must contain exactly two parts:"
) == 1
assert repair_prompt.count(f"<<<{sentinel}>>>") == 1
assert repair_prompt.rfind(f"<<<{sentinel}>>>") > repair_prompt.rfind(
    "<<<AGY_DONE_22222222222222222222222222222222>>>"
)
```

- [x] **Step 2: Verify RED**

Run:

```text
/private/tmp/triad-reliability-venv-20260722/bin/python -m pytest -q \
  tests/test_antigravity_packet_context.py::test_agy_pydantic_initial_prompt_uses_body_semantics_and_one_sealer \
  tests/test_antigravity_packet_context.py::test_agy_schema_retry_rebuilds_unsealed_prompt_and_reseals_once \
  -p no:cacheprovider
```

Expected: tests fail because initial and repair paths currently carry separate competing instructions.

- [x] **Step 3: Implement one sealer and rebuild repair from unsealed input**

```python
def _seal_pydantic_prompt(unsealed_prompt: str, sentinel: str) -> str:
    return (
        f"{unsealed_prompt.rstrip()}\n\n"
        "Your complete response must contain exactly two parts:\n"
        "1. One valid JSON object matching the schema requirements above.\n"
        f"2. On the next line, the exact completion marker <<<{sentinel}>>>.\n"
        "The marker is a transport delimiter and is not part of the JSON body. "
        "Output no prose or markdown fences, and nothing after the marker."
    )
```

`_build_cmd(prompt, sentinel, agy_sandbox, model, timeout, pydantic=True)` calls
this function. `_repair_cmd()` appends the validation diagnosis to the unsealed
effective prompt, then calls this same function and replaces only
`argv[argv.index("-p") + 1]`. `main()` passes `eff_prompt`, not raw `args.prompt`,
into `_run_agy_with_retry()`.

- [x] **Step 4: Verify GREEN**

Run:

```text
/private/tmp/triad-reliability-venv-20260722/bin/python -m pytest -q \
  tests/test_antigravity_packet_context.py \
  tests/test_formal_review_schema.py \
  tests/test_provider_packet_context.py \
  -p no:cacheprovider
```

Expected: all selected tests pass; schema repair remains one attempt and non-Pydantic footer tests remain unchanged.

---

### Task 3: Reject explicitly truncated terminal transcript content

**Files:**
- Modify: `bin/_common.py:1404-1519`
- Test: `tests/test_antigravity_packet_context.py`

**Interfaces:**
- Consumes: AGY transcript JSON records.
- Produces: unchanged `_scan_transcript(pth, marker) -> tuple[bool, Optional[str]]`; a terminal DONE with `content` in `truncated_fields` yields `final=None`.

- [x] **Step 1: Write the failing fallback integration test**

```python
def test_truncated_done_content_falls_back_to_complete_pty_answer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sentinel = "AGY_DONE_" + "3" * 32
    brain = tmp_path / "brain"
    transcript = brain / "conversation" / ".system_generated" / "logs" / "transcript.jsonl"

    def fake_pty(*_args, **_kwargs):
        transcript.parent.mkdir(parents=True)
        records = [
            {
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "status": "DONE",
                "content": f"prompt\n<<<{sentinel}>>>",
            },
            {
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "status": "DONE",
                "content": f"short head\n<truncated 200 bytes>\nshort tail\n<<<{sentinel}>>>",
                "truncated_fields": ["content", "thinking"],
            },
        ]
        transcript.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )
        return wrapper._pty.PtyResult(
            f"complete PTY answer\n<<<{sentinel}>>>\n".encode(),
            0,
            False,
        )

    monkeypatch.setenv("AGY_BRAIN_DIR", str(brain))
    monkeypatch.setattr(wrapper._pty, "run_via_pty", fake_pty)

    result = wrapper._run_agy_with_retry(
        ["agy", "-p", "sealed"],
        "unsealed",
        30,
        expected_sentinel=sentinel,
    )

    assert result.final_answer == "complete PTY answer"
    assert result.classification == "ok"
    assert result.exit_code == wrapper._common.EXIT_OK
```

- [x] **Step 2: Verify RED**

Run:

```text
/private/tmp/triad-reliability-venv-20260722/bin/python -m pytest -q \
  tests/test_antigravity_packet_context.py::test_truncated_done_content_falls_back_to_complete_pty_answer \
  -p no:cacheprovider
```

Expected: assertion fails because the shortened transcript currently wins over the complete PTY answer.

- [x] **Step 3: Implement the terminal-DONE truncation check**

```python
truncated_fields = rec.get("truncated_fields")
final = (
    None
    if isinstance(truncated_fields, list) and "content" in truncated_fields
    else content
)
```

Assign `None`; do not skip the record, because the last truncated DONE must not leave an earlier DONE selected.

- [x] **Step 4: Verify GREEN**

Run the focused test, then the complete `tests/test_antigravity_packet_context.py` module. Both must pass.

---

### Task 4: Full regression verification

**Files:**
- Verify only; no additional source changes unless a directly caused regression is proven.

**Interfaces:**
- Consumes: the three green TDD cycles.
- Produces: fresh targeted and full-suite evidence.

- [x] **Step 1: Run the focused modules**

```text
/private/tmp/triad-reliability-venv-20260722/bin/python -m pytest -q \
  tests/test_antigravity_packet_context.py \
  tests/test_formal_review_schema.py \
  tests/test_provider_packet_context.py \
  -p no:cacheprovider
```

- [x] **Step 2: Run the complete suite**

```text
/private/tmp/triad-reliability-venv-20260722/bin/python -m pytest -q \
  tests/ -p no:cacheprovider
```

- [x] **Step 3: Inspect the exact task diff and dirty-tree preservation**

Run `git diff --check`, inspect the four touched source/test files, and verify all unrelated pre-existing status entries remain untouched.

- [x] **Step 4: Stop before commit, push, install, or another review round**

Report the fresh test counts, changed symbols, remaining risks, and the unchanged external-state boundary to the owner.
