# Claude Leg (`claude_wrapper.py`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `claude` single-shot dispatch leg (`bin/claude_wrapper.py` around `claude -p --output-format json`) to the new Codex-led repo, reusing the leader-agnostic `_common.py` engine.

**Architecture:** The claude leg mirrors the existing thin `gemini_wrapper.py`: build a `claude -p` argv, delegate to `_common.run_cli_with_retry("claude", …)`, and let `_common` classify + emit the run-log. `_common.py` already ships claude scaffolding (`CLAUDE_VENDOR_EXIT_MAP`, a `classify()` claude arm, `extract_claude_answer`, a `run_cli_with_retry` claude branch); this plan copies that engine into the new repo, verifies the real-CLI envelope/exit-codes empirically (Spike E), extends the extractor for `--json-schema` structured output, and adds the wrapper + hermetic fake-CLI tests.

**Tech Stack:** Python ≥3.12 (stdlib only; `pydantic` optional, imported lazily), `claude` CLI v2.1.196, pytest.

## Global Constraints

- **Reuse, don't fork:** `bin/_common.py`, `_pty.py`, `_agy_settings.py`, `gemini_wrapper.py`, `antigravity_wrapper.py` are copied verbatim from `~/triad-dispatch/bin/`; only `_common.py` is edited (Tasks 2–3). Copy source of truth = `~/triad-dispatch/bin/`.
- **No-yolo invariant:** the wrapper rejects `--permission-mode bypassPermissions` and `--dangerously-skip-permissions` at argparse (mirror Codex `danger-full-access` ban).
- **No model IDs in code:** `--model` accepts an alias only (`opus`/`sonnet`/`haiku`/`fable`); default unset. Dated IDs appear in audit output only.
- **Read-only default:** `--sandbox read-only` ⇒ `--permission-mode dontAsk --allowedTools "Read,Glob,Grep"`. `--search` adds `WebSearch,WebFetch`.
- **Auth is user-managed:** the wrapper never touches login/keys.
- **Classify from the JSON envelope, not the exit code** (`claude -p` has no documented exit-code taxonomy).
- **Shared classification token set** (unchanged): `ok | server-capacity | cli-subscription-cap | token-limit | oauth-env | schema-rejected | timeout | extraction-error | unknown`.
- **Reasoning enum (owner default):** mirror codex `{low,medium,high,xhigh}` for `--reasoning`; claude's extra `max` is NOT exposed in v1.
- **Classifier path (owner default):** isolate to `~/.config/triad-codex-dispatch/classifier-patches.json` (+ import helper, out of scope for this plan).

---

## Interfaces reused from `_common.py` (read-only; defined by the copied engine)

- `run_cli_with_retry(cli: str, build_cmd: Callable[[str], list[str]], prompt: str, *, cwd, timeout, pydantic_cls, last_msg_path, repair_mode) -> RunResult`
- `RunResult(exit_code, stdout, stderr, elapsed_s, classification, mode, repair_attempt, final_answer, validated, schema_repair_attempt, extraction_error, validation_error, vendor_exit_code)`
- `extract_claude_answer(stdout: str, stderr: str) -> Tuple[str, Optional[str]]` — returns `(answer, extraction_error)`.
- `classify(...)` — has a `cli == "claude"` arm keyed on `CLAUDE_VENDOR_EXIT_MAP` + shared stderr/stdout pattern lists.
- `audit`, `debug_log`, `emit_run_log`, `load_pydantic_class`, `require_binary`, `log`, `EXIT_ARG_ERROR`.

---

## Task 0 (Spike E): Verify `claude -p` envelope + failure signals against the real CLI

**Files:**
- Create: `docs/references/spike-e-claude-findings.md`

**Why first:** the extractor (Task 3) and the classification map (Task 5) must key off *real* field values. `extract_claude_answer`'s envelope note is dated 2026-05-05; re-confirm on v2.1.196, and capture at least one real error envelope.

- [ ] **Step 1: Capture a success envelope**

Run: `claude -p 'Reply with the single word OK.' --output-format json --no-session-persistence --permission-mode dontAsk --allowedTools "Read,Glob,Grep"`
Record: top-level keys, `type`, `subtype`, `is_error`, `result`, and whether `structured_output` is absent.

- [ ] **Step 2: Capture a structured-output envelope**

Run: `claude -p 'Give one todo.' --output-format json --no-session-persistence --permission-mode dontAsk --allowedTools "Read,Grep,Glob" --json-schema '{"type":"object","properties":{"todos":{"type":"array","items":{"type":"string"}}},"required":["todos"]}'`
Record: exact location of the validated object (`structured_output`), and the `subtype` value on success.

- [ ] **Step 3: Capture a failure envelope + exit code**

Force an auth/error case in a scratch shell, e.g. `ANTHROPIC_API_KEY=sk-invalid claude -p 'hi' --output-format json --no-session-persistence 2>&1; echo "exit=$?"` (or a deliberately-invalid `--json-schema`). Record `is_error`, `api_error_status`, the `result`/error text, the exit code, and (if reproducible) the `subtype: error_max_structured_output_retries` case.

- [ ] **Step 4: Write findings**

Record all three envelopes + the observed vendor exit codes in `docs/references/spike-e-claude-findings.md`. These values are the source of truth for Tasks 3 and 5. If the exit code for a failure is non-zero and stable, note it for `CLAUDE_VENDOR_EXIT_MAP`.

- [ ] **Step 5: Commit**

```bash
git add docs/references/spike-e-claude-findings.md
git commit -m "spike(claude-leg): verify claude -p envelope + failure signals (v2.1.196)"
```

---

## Task 1: Scaffold `bin/` — copy the reused engine

**Files:**
- Create: `bin/_common.py`, `bin/_pty.py`, `bin/_agy_settings.py`, `bin/gemini_wrapper.py`, `bin/antigravity_wrapper.py` (copies)

**Interfaces:**
- Produces: an importable `bin/` package so `python3 bin/gemini_wrapper.py --help` runs (sanity that the copied engine imports).

- [ ] **Step 1: Copy engine files verbatim from the source repo**

```bash
SRC=~/triad-dispatch/bin
cp "$SRC/_common.py" "$SRC/_pty.py" "$SRC/_agy_settings.py" \
   "$SRC/gemini_wrapper.py" "$SRC/antigravity_wrapper.py" bin/
```

- [ ] **Step 2: Verify imports resolve**

Run: `python3 bin/gemini_wrapper.py --help`
Expected: the gemini usage text prints (exit 0), proving sibling imports (`from _common import …`) resolve.

- [ ] **Step 3: Commit**

```bash
git add bin/
git commit -m "chore(claude-leg): vendor reused leg engine from source repo"
```

---

## Task 2: Namespace the classifier-extension path

**Files:**
- Modify: `bin/_common.py` (`_classifier_extension_path`, ~line 276–285)
- Test: `tests/test_classifier_path.py`

**Interfaces:**
- Consumes: `_classifier_extension_path() -> Path` and env `TRIAD_CLASSIFIER_EXTENSION`.
- Produces: default path rooted at `triad-codex-dispatch/classifier-patches.json`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_classifier_path.py
import importlib, os, sys
sys.path.insert(0, "bin")

def test_default_path_is_namespaced(monkeypatch):
    monkeypatch.delenv("TRIAD_CLASSIFIER_EXTENSION", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    c = importlib.reload(importlib.import_module("_common"))
    p = c._classifier_extension_path()
    assert p.parts[-2:] == ("triad-codex-dispatch", "classifier-patches.json")

def test_env_override_wins(monkeypatch, tmp_path):
    target = tmp_path / "x.json"
    monkeypatch.setenv("TRIAD_CLASSIFIER_EXTENSION", str(target))
    c = importlib.reload(importlib.import_module("_common"))
    assert c._classifier_extension_path() == target
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_classifier_path.py -v`
Expected: FAIL — default path still ends with `triad-dispatch/classifier-patches.json`.

- [ ] **Step 3: Change the default directory name**

In `bin/_common.py`, in `_classifier_extension_path()`, change the returned path's directory from `"triad-dispatch"` to `"triad-codex-dispatch"` (the `TRIAD_CLASSIFIER_EXTENSION` and `XDG_CONFIG_HOME` branches are unchanged).

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_classifier_path.py -v`
Expected: PASS (both tests).

- [ ] **Step 5: Commit**

```bash
git add bin/_common.py tests/test_classifier_path.py
git commit -m "feat(claude-leg): namespace classifier extension path to triad-codex-dispatch"
```

---

## Task 3: Extend `extract_claude_answer` for `--json-schema` structured output

**Files:**
- Modify: `bin/_common.py` (`extract_claude_answer`, ~line 755–818)
- Test: `tests/test_extract_claude.py`

**Interfaces:**
- Consumes: `extract_claude_answer(stdout, stderr) -> (answer, extraction_error)`.
- Produces: when the envelope carries `structured_output`, the answer is its compact JSON string; when `subtype == "error_max_structured_output_retries"`, returns `("", "schema-retries-exhausted: …")`. Existing success/`is_error`/empty behavior is preserved.

> Use the real field names captured in Task 0. The snippet below assumes Task 0 confirmed `structured_output` and the `error_max_structured_output_retries` subtype; adjust to the recorded values if they differ.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_extract_claude.py
import json, sys
sys.path.insert(0, "bin")
from _common import extract_claude_answer

def test_plain_result():
    env = {"type":"result","subtype":"success","is_error":False,"result":"hello"}
    ans, err = extract_claude_answer(json.dumps(env), "")
    assert (ans, err) == ("hello", None)

def test_structured_output_returned_as_json():
    env = {"type":"result","subtype":"success","is_error":False,"result":"",
           "structured_output":{"todos":["a","b"]}}
    ans, err = extract_claude_answer(json.dumps(env), "")
    assert err is None
    assert json.loads(ans) == {"todos":["a","b"]}

def test_schema_retries_exhausted_is_extraction_error():
    env = {"type":"result","subtype":"error_max_structured_output_retries",
           "is_error":False,"result":""}
    ans, err = extract_claude_answer(json.dumps(env), "")
    assert ans == ""
    assert "schema-retries-exhausted" in err

def test_is_error_still_surfaces():
    env = {"type":"result","is_error":True,"api_error_status":401,"result":"Not logged in"}
    ans, err = extract_claude_answer(json.dumps(env), "")
    assert ans == ""
    assert "is_error=true" in err and "401" in err
```

- [ ] **Step 2: Run tests to verify the new ones fail**

Run: `python3 -m pytest tests/test_extract_claude.py -v`
Expected: `test_plain_result` and `test_is_error_still_surfaces` PASS; `test_structured_output_returned_as_json` and `test_schema_retries_exhausted_is_extraction_error` FAIL.

- [ ] **Step 3: Extend the extractor**

In `extract_claude_answer`, after `obj = json.loads(s)` and before the `is_error` check, add:

```python
    subtype = obj.get("subtype", "")
    if subtype == "error_max_structured_output_retries":
        return "", "schema-retries-exhausted: structured output failed validation"
    structured = obj.get("structured_output")
    if structured is not None:
        return json.dumps(structured, ensure_ascii=False), None
```

(Leave the existing `is_error` / `permission_denials` / empty-`result` logic below unchanged.)

- [ ] **Step 4: Run tests to verify all pass**

Run: `python3 -m pytest tests/test_extract_claude.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add bin/_common.py tests/test_extract_claude.py
git commit -m "feat(claude-leg): extract_claude_answer handles structured_output + schema-retry failure"
```

---

## Task 4: `claude_wrapper.py` + fake-CLI fixture (end-to-end thin leg)

**Files:**
- Create: `bin/claude_wrapper.py`
- Create: `tests/fixtures/fake_claude.py`
- Test: `tests/test_claude_wrapper.py`

**Interfaces:**
- Consumes: `run_cli_with_retry`, `require_binary`, `emit_run_log`, `audit`, `load_pydantic_class`, `EXIT_ARG_ERROR`.
- Produces: CLI `claude_wrapper.py --prompt <p> [--sandbox read-only|workspace-write] [--search] [--model <alias>] [--reasoning low|medium|high|xhigh] [--pydantic m:C] [--cwd] [--timeout] [--repair-mode]`; stdout = answer (or validated JSON); stderr = wrapper log + `[wrapper] claude <class> …`.

- [ ] **Step 1: Write the fake claude CLI fixture**

```python
# tests/fixtures/fake_claude.py  — emulates `claude -p --output-format json`
# Mode is read from the FAKE_MODE env var so the wrapper (which owns the argv) needn't pass it.
import json, os, sys
def main():
    mode = os.environ.get("FAKE_MODE", "success")   # success|is_error|structured|empty
    if mode == "success":
        print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"FAKE-OK"}))
    elif mode == "structured":
        print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"",
                          "structured_output":{"todos":["x"]}}))
    elif mode == "is_error":
        print(json.dumps({"type":"result","is_error":True,"api_error_status":401,
                          "result":"Not logged in"}))
    elif mode == "empty":
        pass  # no stdout → extraction-error
    return 0
if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Write `claude_wrapper.py`**

```python
#!/usr/bin/env python3
"""Single-shot Claude Code (`claude -p`) subprocess wrapper. Mirrors gemini_wrapper.py."""
from __future__ import annotations
import argparse, json, sys
from _common import (EXIT_ARG_ERROR, audit, debug_log, emit_run_log,
                     load_pydantic_class, log, require_binary, run_cli_with_retry)

SANDBOX_CHOICES = ("read-only", "workspace-write")   # bypassPermissions banned (no-yolo)
REASONING_CHOICES = ("low", "medium", "high", "xhigh")
READONLY_TOOLS = "Read,Glob,Grep"

def main() -> int:
    p = argparse.ArgumentParser(description="Claude Code single-shot wrapper")
    p.add_argument("--prompt", required=True)
    p.add_argument("--sandbox", default="read-only", choices=SANDBOX_CHOICES)
    p.add_argument("--search", action="store_true", help="Enable WebSearch/WebFetch")
    p.add_argument("--model", default=None, help="Model alias (opus/sonnet/haiku/fable)")
    p.add_argument("--reasoning", default=None, choices=REASONING_CHOICES)
    p.add_argument("--pydantic", default=None)
    p.add_argument("--cwd", default=None)
    p.add_argument("--timeout", type=int, default=600)
    p.add_argument("--repair-mode", action="store_true")
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    if not args.prompt.strip():
        log("empty prompt"); return EXIT_ARG_ERROR

    require_binary("claude")

    pydantic_cls = None
    if args.pydantic:
        try:
            pydantic_cls = load_pydantic_class(args.pydantic)
        except Exception as e:
            log(f"--pydantic load failed: {e}"); return EXIT_ARG_ERROR

    def build_cmd(effective_prompt: str) -> list[str]:
        tools = READONLY_TOOLS + (",WebSearch,WebFetch" if args.search else "")
        perm = "dontAsk" if args.sandbox == "read-only" else "acceptEdits"
        cmd = ["claude", "-p", effective_prompt,
               "--output-format", "json", "--no-session-persistence",
               "--permission-mode", perm, "--allowedTools", tools]
        if args.model:
            cmd += ["--model", args.model]
        if args.reasoning:
            cmd += ["--effort", args.reasoning]
        if pydantic_cls is not None:
            from _common import pydantic_to_codex_schema
            cmd += ["--json-schema", json.dumps(pydantic_to_codex_schema(pydantic_cls))]
        return cmd

    result = run_cli_with_retry("claude", build_cmd, args.prompt,
                                cwd=args.cwd, timeout=args.timeout,
                                pydantic_cls=pydantic_cls, last_msg_path=None,
                                repair_mode=args.repair_mode)

    audit_cmd = build_cmd(args.prompt)
    audit("claude", audit_cmd, args.prompt, result)
    if args.debug:
        debug_log("claude", args.prompt, result)
    run_log_path = emit_run_log("claude", sys.argv, audit_cmd, args.prompt, result)
    if run_log_path is not None:
        log(f"run-log: {run_log_path}")

    if pydantic_cls and result.validated is not None:
        sys.stdout.write(json.dumps(result.validated, ensure_ascii=False) + "\n")
    else:
        ans = result.final_answer or ""
        sys.stdout.write(ans + ("\n" if ans and not ans.endswith("\n") else ""))
    sys.stdout.flush()
    return result.exit_code

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Write the wrapper test (fake CLI on PATH)**

```python
# tests/test_claude_wrapper.py
import os, subprocess, sys, shutil, stat, textwrap
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def _fake_claude_on_path(tmp_path):
    # a shim named `claude` that execs the fake fixture
    shim = tmp_path / "claude"
    shim.write_text(f'#!/usr/bin/env bash\nexec python3 {ROOT}/tests/fixtures/fake_claude.py "$@"\n')
    shim.chmod(shim.stat().st_mode | stat.S_IEXEC)
    return str(tmp_path)

def _run(tmp_path, *extra, fake_mode="success"):
    env = dict(os.environ, PATH=_fake_claude_on_path(tmp_path) + os.pathsep + os.environ["PATH"])
    # inject --fake-mode by appending to the prompt path is not possible; pass via env the fixture reads:
    env["FAKE_MODE"] = fake_mode
    return subprocess.run([sys.executable, str(ROOT / "bin/claude_wrapper.py"),
                           "--prompt", "hi", *extra],
                          capture_output=True, text=True, env=env)

def test_success_returns_answer(tmp_path):
    r = _run(tmp_path)
    assert r.returncode == 0
    assert "FAKE-OK" in r.stdout
    assert "[wrapper] claude ok" in r.stderr

def test_bypass_permissions_rejected():
    r = subprocess.run([sys.executable, str(ROOT / "bin/claude_wrapper.py"),
                        "--prompt", "hi", "--sandbox", "bypassPermissions"],
                       capture_output=True, text=True)
    assert r.returncode != 0
    assert "invalid choice" in r.stderr
```

- [ ] **Step 4: Run the tests**

Run: `python3 -m pytest tests/test_claude_wrapper.py -v`
Expected: PASS (`test_success_returns_answer`, `test_bypass_permissions_rejected`).

- [ ] **Step 5: Commit**

```bash
git add bin/claude_wrapper.py tests/fixtures/fake_claude.py tests/test_claude_wrapper.py
git commit -m "feat(claude-leg): claude_wrapper.py single-shot leg + fake-CLI tests"
```

---

## Task 5: Classification-mapping tests (fake CLI → shared token set)

**Files:**
- Test: `tests/test_claude_classification.py`

**Interfaces:**
- Consumes: the fake CLI (`FAKE_MODE`) + `claude_wrapper.py` end-to-end; the `[wrapper] claude <class>` stderr summary.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_claude_classification.py  — reuses helpers from test_claude_wrapper
from test_claude_wrapper import _run
import re
def _cls(stderr):
    m = re.search(r"\[wrapper\] claude (\S+) ", stderr)
    return m.group(1) if m else None

def test_is_error_maps_to_failure(tmp_path):
    r = _run(tmp_path, fake_mode="is_error")
    assert r.returncode != 0
    assert _cls(r.stderr) in {"oauth-env", "unknown", "extraction-error"}

def test_empty_stdout_is_extraction_error(tmp_path):
    r = _run(tmp_path, fake_mode="empty")
    assert _cls(r.stderr) == "extraction-error"

def test_structured_output_ok(tmp_path):
    r = _run(tmp_path, fake_mode="structured")
    assert r.returncode == 0
    assert '"todos"' in r.stdout
```

- [ ] **Step 2: Run tests to verify failures**

Run: `python3 -m pytest tests/test_claude_classification.py -v`
Expected: FAIL where the classifier arm doesn't yet map the real `is_error`/`api_error_status` phrases (e.g. `oauth-env` for 401 "Not logged in").

- [ ] **Step 3: Extend the claude classify arm**

Using Task 0's real error text, add the auth/quota/overload phrase(s) to the shared pattern lists (`OAUTH_ENV_PATTERNS`, `CLI_SUB_CAP_PATTERNS`, `SERVER_CAPACITY_PATTERNS`) and/or `CLAUDE_VENDOR_EXIT_MAP`, following the false-positive guard rules (phrase form, never bare `401`/`oauth`). Add only what a captured envelope proves.

- [ ] **Step 4: Run tests to verify pass**

Run: `python3 -m pytest tests/ -v`
Expected: PASS (all tests across the suite).

- [ ] **Step 5: Commit**

```bash
git add bin/_common.py tests/test_claude_classification.py
git commit -m "feat(claude-leg): map claude envelope error signals onto shared classification set"
```

---

## Task 6: Real-vendor smoke test

**Files:** none (manual verification gate)

- [ ] **Step 1: Read-only single-shot**

Run: `python3 bin/claude_wrapper.py --prompt 'Reply with the single word OK.'`
Expected: stdout contains `OK`; stderr has `[wrapper] claude ok exit=0 …`.

- [ ] **Step 2: Web-search dispatch**

Run: `python3 bin/claude_wrapper.py --prompt 'What is the latest codex-cli version? Cite a source.' --search --reasoning high`
Expected: an answer citing a source; classification `ok`.

- [ ] **Step 3: Structured output**

Run: `python3 bin/claude_wrapper.py --prompt 'List two todos.' --pydantic <a test module:Class>` (define a tiny local pydantic class first).
Expected: stdout is a validated JSON object.

- [ ] **Step 4: Confirm clean + no leaked logs in git**

Run: `git status --short` — expected: no `_logs/` / `_debug/` tracked (they are gitignored).

---

## Self-Review

- **Spec coverage:** claude leg §5 + claude-leg-spec.md → Tasks 3–5 (extractor, wrapper, classification); read-only/web/model/effort → Task 4 `build_cmd`; classifier path §8 → Task 2. Distribution/skills/repair are OTHER plans (out of scope, by design).
- **Placeholder scan:** the only deferred values are Task 0's real envelope fields, explicitly gated behind the spike and flagged where used (Tasks 3, 5). No silent TODOs.
- **Type consistency:** `extract_claude_answer -> (answer, err)`, `run_cli_with_retry(...) -> RunResult`, and `RunResult.final_answer/.validated/.exit_code` are used consistently and match the copied engine.

---

## Follow-on plans (not in this plan)

1. **Codex leader skills** — `triad-{claude,gemini,antigravity}-dispatch` + cross-family review as Codex `SKILL.md`.
2. **Repair named subagents** — `.codex/agents/*.toml` (+ new `claude-wrapper-repair`), per the verified spike.
3. **Distribution** — Codex plugin/marketplace + bootstrap; gated by **Spike D** (plugin-shipped named agent spawnability).
