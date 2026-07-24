# AGY 0.2.528 Functional Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Port only the upstream AGY truncated-answer failure gate into the current worktree-first branch and include it in the branch's single local commit.

**Architecture:** Detect the vendor's own-line truncation marker in the AGY driver after the nonzero-exit gate and before any success or schema path. Quarantine the answer through the existing `finish()` result-custody helper, map the direct classification to terminal exit 65, and teach both Google dispatch and formal review contracts to invalidate the leg without provider fallback or file-writing workarounds.

**Tech Stack:** Python 3.12, pytest, Markdown skill contracts, existing AGY PTY/transcript wrapper.

## Global Constraints

- Source behavior comes from `94a24cb2e59972cd8fccefd06c05a6a7b77166b8`, but Git history is not merged.
- Match only an own-line `<truncated N bytes>` or `<truncated N lines>` marker, allowing surrounding horizontal whitespace and ASCII digits `[0-9]+`.
- Evaluate a nonzero vendor exit before truncation; `rc != 0` remains `vendor-error`.
- Evaluate truncation before plain success, Pydantic validation, and schema repair.
- A zero-exit truncated answer is `truncated-answer`, exits with `EXIT_TERMINAL` (`65`), has no `final_answer`, and retains a bounded diagnostic in `extraction_error`.
- `truncated-answer` is deterministic and non-repairable; a required formal Google leg is invalid and must not switch to Gemini after submission.
- Do not add generic `write_file`, shell, or sandbox bypass instructions.
- Do not change `.codex-plugin/plugin.json`, `CHANGELOG.md`, version, tag, release, installation, or remote state for this port.
- Keep the current dirty worktree intact and make one combined local commit only after all tests and reviews pass.

---

### Task 1: Add the fail-closed truncated-answer runtime and review contract

**Files:**
- Modify: `tests/test_antigravity_packet_context.py`
- Modify: `tests/test_distribution_contract.py`
- Modify: `bin/antigravity_wrapper.py`
- Modify: `bin/_common.py`
- Modify: `skills/triad-antigravity-dispatch/SKILL.md`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Verify: `docs/superpowers/specs/2026-07-22-agy-0528-functional-integration-design.md`

**Interfaces:**
- Consumes: `_run_agy_with_retry(...) -> AgyResult`, its nested `finish(...)`, `_common.EXIT_TERMINAL`, and `_common.map_classification_to_exit(cls)`.
- Produces: `_has_truncated_answer_marker(answer: str | None) -> bool` and the direct result classification literal `truncated-answer`.

- [ ] **Step 1: Write failing driver tests for marker grammar, gate ordering, schema suppression, quarantine, and exit mapping**

Add a small test helper that supplies either transcript extraction or PTY fallback without touching provider state, then add tests equivalent to:

```python
def _run_answer(monkeypatch, answer: str, *, rc: int = 0, transcript: bool = True,
                pydantic_cls=None):
    sentinel = "AGY_DONE_" + "9" * 32
    monkeypatch.setattr(wrapper._common, "snapshot_agy_transcripts", lambda: {})
    monkeypatch.setattr(
        wrapper._pty,
        "run_via_pty",
        lambda *_a, **_k: wrapper._pty.PtyResult(
            f"{answer}\n<<<{sentinel}>>>\n".encode(), rc, False
        ),
    )
    monkeypatch.setattr(
        wrapper._common,
        "extract_agy_answer_from_transcript",
        (lambda *_a, **_k: answer) if transcript else (lambda *_a, **_k: None),
    )
    if not transcript:
        monkeypatch.setattr(
            wrapper._common,
            "extract_antigravity_answer",
            lambda *_a, **_k: (answer, None),
        )
    return wrapper._run_agy_with_retry(
        ["agy", "-p", "review"], "review", 30,
        expected_sentinel=sentinel, pydantic_cls=pydantic_cls,
    )

@pytest.mark.parametrize(
    ("answer", "transcript"),
    [
        ("head\n<truncated 200 bytes>\ntail", True),
        ("head\n  <truncated 7 lines>\t\ntail", False),
    ],
)
def test_zero_exit_own_line_truncation_is_terminal_and_quarantined(
    answer, transcript, monkeypatch
):
    result = _run_answer(monkeypatch, answer, transcript=transcript)
    assert result.classification == "truncated-answer"
    assert result.exit_code == wrapper._common.EXIT_TERMINAL
    assert result.final_answer is None
    assert "quarantined" in result.extraction_error

def test_truncated_answer_never_reaches_schema_validation(monkeypatch):
    monkeypatch.setattr(
        wrapper, "validate_response",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("validated")),
    )
    result = _run_answer(
        monkeypatch, "head\n<truncated 1 bytes>\ntail", pydantic_cls=object
    )
    assert result.classification == "truncated-answer"
    assert result.schema_repair_attempt == 0

def test_nonzero_truncated_answer_remains_vendor_error(monkeypatch):
    result = _run_answer(
        monkeypatch, "head\n<truncated 2 lines>\ntail", rc=17
    )
    assert result.classification == "vendor-error"

def test_inline_truncation_text_is_not_a_marker(monkeypatch):
    answer = "The vendor printed <truncated 2 lines> inline."
    result = _run_answer(monkeypatch, answer)
    assert result.classification == "ok"
    assert result.final_answer == answer

def test_truncated_answer_maps_to_terminal_exit():
    assert (
        wrapper._common.map_classification_to_exit("truncated-answer")
        == wrapper._common.EXIT_TERMINAL
    )
```

- [ ] **Step 2: Run the focused runtime tests and verify RED**

Run from `/Users/chaniri/codex_workspace` in the user's login-shell Python environment:

```bash
python3 -m pytest \
  workspace/triad-codex-dispatch-reliability/tests/test_antigravity_packet_context.py \
  -k 'truncat and not truncated_done_content' -q
```

Expected: the new zero-exit and mapping assertions fail because `truncated-answer` detection and mapping do not exist; the inline and nonzero controls may already pass.

- [ ] **Step 3: Implement the minimal runtime gate**

Add the compiled marker and helper after `_is_headless_softdeny()`:

```python
_TRUNCATED_ANSWER_RE = re.compile(
    r"^[ \t]*<truncated [0-9]+ (?:bytes|lines)>[ \t]*$",
    re.MULTILINE,
)


def _has_truncated_answer_marker(answer) -> bool:
    """True only for agy's own-line lossy-output marker."""
    return bool(_TRUNCATED_ANSWER_RE.search(answer or ""))
```

After the existing `result.rc != 0` return and before `if pydantic_cls is None`, add:

```python
if _has_truncated_answer_marker(answer):
    snippet = answer if len(answer) <= 2000 else answer[:2000] + " …[truncated]"
    return finish(
        None,
        "truncated-answer",
        _common.EXIT_TERMINAL,
        result.rc,
        scrubbed_output=scrubbed,
        extraction_error=(
            "vendor rc=0 returned an answer containing an own-line "
            "truncation marker; surfaced as truncated-answer (not ok, "
            f"not repair). quarantined answer: {snippet}"
        ),
    )
```

Add the shared mapping beside the other direct AGY terminal result:

```python
"truncated-answer": EXIT_TERMINAL,
```

Update the nearby direct-classification comment to state that both `vendor-error` and `truncated-answer` are driver-emitted and are not classifier-patch targets.

- [ ] **Step 4: Run the focused runtime tests and verify GREEN**

Run:

```bash
python3 -m pytest \
  workspace/triad-codex-dispatch-reliability/tests/test_antigravity_packet_context.py \
  -k 'truncat and not truncated_done_content' -q
```

Expected: all selected tests pass, with no schema validation or retry on the marker path.

- [ ] **Step 5: Write failing static contract tests for non-repair and no fallback/write workaround**

Add a focused distribution test equivalent to:

```python
def test_agy_truncated_answer_is_terminal_without_repair_or_provider_switch():
    agy = " ".join(_text(AGY_SKILL).split())
    review = " ".join(_text(REVIEW_SKILL).split())
    combined = f"{agy} {review}"

    assert "`truncated-answer`" in combined
    assert "exit 65" in combined
    assert "deterministic" in combined
    assert "not repair" in combined
    assert "invalid" in review
    assert "does not make Gemini fallback-eligible" in review
    assert "bounded, compact" in combined
    assert "generic `write_file`" in combined
    assert "Do not omit `--sandbox read-only`" in combined
```

- [ ] **Step 6: Run the static contract test and verify RED**

Run:

```bash
python3 -m pytest \
  workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py \
  -k truncated_answer -q
```

Expected: FAIL because the two skills do not yet name the new classification and policy.

- [ ] **Step 7: Add the minimal skill wording without exceeding the 200-line skill-body limit**

In `triad-antigravity-dispatch/SKILL.md`, extend result handling with this contract:

```markdown
Treat `truncated-answer` (exit 65) as a deterministic terminal result: the
answer is quarantined, it is not repair-routed, and a new invocation must ask
for a bounded, compact result. Do not use a generic `write_file` workaround or
omit `--sandbox read-only` to recover a long answer.
```

In `triad-cross-family-review/SKILL.md`, add or replace one Common failures row without increasing the body beyond 200 lines:

```markdown
| Required agy leg returns `truncated-answer` | Invalidate the leg; request a new bounded, compact result. Post-dispatch truncation does not make Gemini fallback-eligible |
```

- [ ] **Step 8: Run the static contract and line-limit tests and verify GREEN**

Run:

```bash
python3 -m pytest \
  workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py \
  -k 'truncated_answer or progressive_disclosure_limit' -q
```

Expected: all selected tests pass and `triad-cross-family-review/SKILL.md` remains within its 200-line body limit.

- [ ] **Step 9: Run regression verification**

Run the Python preflight once, then focused and partitioned suites from `/Users/chaniri/codex_workspace`:

```bash
command -v python3
python3 --version
python3 -m pytest --version
python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_antigravity_packet_context.py -q
python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -q
python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py -q
python3 -m pytest workspace/triad-codex-dispatch-reliability/tests --ignore=workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py -q
```

Expected: every partition passes. If the known monolithic macOS temporary-Python SIGKILL reproduces, preserve its exact evidence and require the isolated/partitioned affected tests to pass before completion.

- [ ] **Step 10: Review and create the single authorized local commit**

Review the complete worktree diff, confirm no `.codex-plugin/plugin.json` or `CHANGELOG.md` change entered this functional port, run the final reviewer gate, then stage the intended current-branch files and create one local commit. Do not push, install, tag, or release.
