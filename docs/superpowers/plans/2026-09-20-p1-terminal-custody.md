# P1 terminal completion and failure custody implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. The root leader owns skill source and tests; separate fresh `triad-skill-executor` instances execute RED and GREEN. Owner authorized implementation and merge without another confirmation on 2026-09-20. Existing plan reviews still apply.

**Goal:** A successful-looking provider answer cannot conceal incomplete/failed output collection or a failed AGY settings release; every partially started owned process is cleaned up.

**Architecture:** Extend the existing bounded process-group cleanup, reader threads and private `RunResult` transport state. Preserve the existing wrapper adapters and result vocabulary. Retain captured AGY bytes on settings-release failure through the existing artifact writer.

**Tech Stack:** Python 3.12+, subprocess/threading, pytest; macOS and Ubuntu 24.04.

**Spec:** Shared `triad-dispatch-spec` remote main `2eb883fee59e66556ee7c7f87189b38231136622`, C1/C2/C6 and R-TERMINAL; local authoring/audit `d7ef76304b2cfcdb4bdb9a0f7991e0cd77b19982`, `decisions/host-b-preimplementation-audit.md`. The confirmed P1 requirements do not depend on D-B1 policy, D-B2 privacy, roster schemas or revision adoption.

## Global constraints

- Start from B `ba6344be910307d9e05bad1396663f6227064467` in the existing `codex/host-parity-preflight` worktree. Preserve unrelated state; do not edit A or installed caches.
- No new dependency, public schema, exit token, retry policy, provider request, authentication change, dormant hook, or Codex subprocess.
- Preserve timeout precedence, genuine vendor errors, complete stdin delivery, exact interrupt propagation, raw/schema/binding routes and advisory audit behavior.
- Reader diagnostics contain stream/phase and exception class only; do not add captured private text to diagnostics.
- Retain bounded joins and the saved owned process group. Never signal the wrapper's own group or obtain a new post-reap group identity.
- Record A source/lines and the reproduction/fix/test procedure in the shared spike record after each completed change. Do not change A while B is in progress.
- Every completed functional plan receives required multi-family review; changed reviewed bytes require a fresh complete round. Track the original NOT-SAFE findings, including evidence-backed rejections. Merge is owner-authorized; deployment remains separate.

## Scope and budget

Production: `bin/_common.py`, `bin/claude_wrapper.py`, `bin/antigravity_wrapper.py`; estimate 180 additions, 65 deletions, +115 net, under 160 novel-core lines. Final production delta: 127 additions, 47 deletions, +80 net. Tests: new `tests/test_terminal_transport.py` plus existing process/AGY/stdin fixtures; 295 additions, 3 deletions. Docs: this plan, short README/README.ko/SECURITY explanations and shared spike/closure records, separately counted. Update estimates for coherent corrections; line growth is not an approval gate.

## Review focus

1. Complete terminal stdout alongside corrupt stderr must fail locally without retry or accepted verdict (Task 1).
2. A normal-exit child leaves a descendant with inherited pipes or closed output descriptors; cleanup must still reach that saved group (Task 1).
3. The first, second or third thread start fails after spawn; no child or already-started reader is abandoned (Task 1).
4. Output collection faults coexist with timeout, genuine vendor failure or an interrupt; local checks must not rewrite those primary causes (Task 1).
5. AGY returns valid bound output and then settings release fails; terminal failure and raw evidence both survive (Task 2).

### Task 1: Complete or fail local output transport

**Files:** modify `bin/_common.py`, `bin/claude_wrapper.py`, `bin/antigravity_wrapper.py`; create `tests/test_terminal_transport.py`; extend `tests/test_provider_wrappers.py` using its existing owned-process receipt cleanup.

**Interfaces:** retain `_run_once(...) -> RunResult`, `_terminate_provider_process_group(...)`, all public CLI/result fields and `_stdin_delivery_failed`. Add one defaulted private `_output_transport_failed: bool = False`, excluded from public/audit schemas. `_drain` receives an optional per-reader completion/error record. Ordinary retry, Claude native extraction and AGY interpretation return a failed local transport result before parsing or retrying it.

- [x] Write the new focused tests before changing source. Core end-to-end oracle (helpers in `tests/test_terminal_transport.py`):

```python
code = "import os; print(" + repr(_envelope("agy")) + ", flush=True); os.write(2, b'\\xff')"
result = _invoke("agy", code, tmp_path)
assert result.vendor_exit_code == 0
assert result.exit_code == _common.EXIT_CLI_FAIL
assert result.final_answer == "" and result.validated is None
assert len(owned_children) == 1
```

  Concrete tests in `tests/test_terminal_transport.py` cover raw, ordinary Claude, native Claude and AGY; capacity-shaped intact stdout; vendor nonzero; timeout; each `Thread.start` failure position. Process descendants use existing independent PID/group/session receipts in `test_provider_wrappers.py`; both inherited and closed-output cases are required. Synthetic children only; never launch real providers in these tests.
- [x] Fresh dedicated RED executor runs the focused file and new descendant cases against the canonical source. Observed 13 causal failures and 7 passes; source/test fingerprint unchanged.
- [x] Root implements reader completion/error records, protected thread startup, normal-exit owned-group reconciliation and adapter gates using the existing terminator.
- [x] Root focused GREEN: 187 passed, including existing stdin/process/AGY regressions. The synchronous `InterruptingWriter` test double now exposes `is_alive() == False` for cleanup verification; its interrupt and two bounded joins remain asserted.

### Task 2: Preserve AGY captured output when guard release fails

**Files:** `bin/antigravity_wrapper.py`, `tests/test_antigravity_stream_json.py`.

**Interfaces:** consume unchanged `RunResult` and `persist_result_artifacts`. A settings error before the provider starts retains its existing no-output behavior. An error after a completed call suppresses final answer/validated output, preserves raw stdout/stderr/vendor rc, and passes the terminal failed result through the ordinary persistence path.

- [x] Add post-call guard failure fixture and keep the entry-failure regression.
- [x] Include the regression in fresh RED; observed return-before-persistence failure.
- [x] Preserve captured raw output through the existing persistence tail. Interpret the captured result, retain any primary provider/transport failure, and convert only successful output to `config-conflict`; suppress accepted output after every release failure.
- [x] Fresh GREEN executor: 189 focused and 1042 full-suite passes; canonical skill validator passed; provider-free lifecycle SUCCESS and ROUND_INTEGRITY_OK with all exact fixtures cleaned. Full suite includes applicable distribution-contract checks; clean-HEAD release archive verification is separate.

## Verification and closure

Host command cwd is `/Users/chaniri/codex_workspace`; literal `python3` runs in `/bin/zsh -lic`. The checkout is passed as `$1`:

```sh
/bin/zsh -lic 'command -v python3; python3 --version; python3 -m pytest --version'
/bin/zsh -lic 'python3 -m pytest -q "$1/tests/test_terminal_transport.py" "$1/tests/test_stdin_transport.py" "$1/tests/test_provider_wrappers.py" "$1/tests/test_antigravity_stream_json.py" --rootdir "$1" -p no:cacheprovider' triad-p1 /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
/bin/zsh -lic 'python3 -m pytest -q "$1/tests" --rootdir "$1" -p no:cacheprovider' triad-p1-full /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
```

- [x] macOS: 1042 passed. Ubuntu 24.04.4, Python 3.12.3, nonroot container: 1040 passed, 2 case-insensitive-filesystem tests skipped. This is automated platform evidence, not authenticated cross-platform dispatch conformance.
- [x] Refresh shared remote main and A commit/lines; update shared spike with evidence/version → current/fixed behavior → A/B impact → preserved functionality → exact checks.
- [x] Complete the required full-scope multi-family round and resolve every reproduced blocker. Round `triad-b-p1-r2`: all four SAFE, matching final integrity, ADMITTED_SAFE; the original P1 findings close. Non-P1 findings remain in the shared register. The remaining Google Minor about simultaneous read/close errors is recorded without changing reviewed source.

Commit only this plan's files. Recheck actual main/worktree/remote state before an authorized merge; do not deploy or change the adopted specification revision as a side effect. This narrative completion record is outside the formal source scope; the twelve reviewed source/document files remain byte-identical to the admitted basis.

## Progress and rulings

- Planning basis verified: latest shared remote main remains `2eb883f`; B functional source still `520caa9` plus one instruction pointer.
- Ruling: owner explicitly waived repeat implementation/merge confirmation; preserve formal verification and design-expansion boundaries. Shared remote publication is separate from authoring a locally reviewable spike.
- Ruling: root writes source/tests under the repository's skill ownership contract; fresh children perform dedicated execution, bounded investigation and independent review.
- Ruling: retain the existing terminator name; renaming it to match A adds no behavior. Reconcile normal-exit descendants even when their output descriptors are closed. Preserve genuine vendor capacity retry; a successful-looking capacity envelope with corrupt transport gets no retry.
- Evidence: `_runs/infra/20260920-triad-p1/red-executor/` and `root-focused-green.txt` under the owner workspace. Shared original-finding register and A-line spike are local authoring records; they do not constitute admission or publication.
- Review correction: a fresh C6 scenario reproduced timeout/vendor failure being overwritten by settings-release failure (2 failed, 1 passed). The correction preserves the primary result and adds a content-free secondary release diagnostic; final GREEN above includes it.
- Full review r1: all four valid results and matching final integrity produced ADMITTED_NOT_SAFE. Claude's reproduced Major finding exposed a missing secondary reader diagnostic on nonzero-vendor/timeout outcomes. Fresh dedicated RED: 3 failed, 14 deselected; primary exit/classification/retry assertions passed. Log the existing class-only transport diagnostic before result selection, preserving precedence. The helper comment now distinguishes signaling/reaping from descendant zombie removal. A full fresh round follows the next GREEN; no prior SAFE result carries forward.
- Ubuntu harness correction: Docker's default tmpfs `noexec` prevented executable fixtures; use a disposable `exec` tmpfs. The process-observation fixture now treats Linux `/proc/<pid>/stat` ESRCH, like ENOENT, as a process that exited during observation. No production behavior was changed for either harness issue.
