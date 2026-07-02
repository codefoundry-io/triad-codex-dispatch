---
name: triad-antigravity-dispatch
description: Use when the Codex leader needs a single-shot Antigravity (agy) answer via the wrapper framework. agy is the PRIMARY Google-family leg — the gemini CLI individual tier is deprecated (IneligibleTierError) and agy is its successor. Triggering signals — the leader is about to run antigravity_wrapper.py raw; the user said "agy 한 번 불러줘" / "agy 로 X 처리" / "구글 AI 단발 호출"; a higher-level orchestration (e.g. triad-cross-family-review) needs the Google-family leg of a fan-out; a separate Google-family leg needs web-grounded research or live-URL lookup (agy's read_url/search_web is native and always allowed); classification-aware routing with a self-improving repair named-subagent fallback is wanted instead of a raw subprocess. Do NOT use for claude (triad-claude-dispatch) or for the codex leader's own direct work.
---

# triad-antigravity-dispatch

Single-shot **Antigravity CLI** (`agy -p`) dispatch for a **Codex leader**, with
classification-based routing and a self-improving repair loop. The Codex leader's
standard "call agy once" path — the Google-family mirror of `triad-claude-dispatch`.

**agy is the PRIMARY Google-family leg.** The gemini CLI individual tier has been
deprecated (`IneligibleTierError` → "migrate to the Antigravity suite"); agy is its
successor. Use agy for all individual-tier Google-family calls.

**agy is the Google-family search/research specialist.** Its `read_url` and
`search_web` tools are native and always allowed (even under `--sandbox
read-only`). Include agy when the dispatch needs a separate Google-family
web-grounded leg; the Codex leader uses `codex --search` for its own direct web
needs.

## Use when

- The Codex leader has a discrete prompt and needs agy's answer (or a structured
  failure signal) — e.g. a Google-ecosystem second opinion, a separate
  Google-family web-grounded research leg, live-URL lookup, or the Google-family
  leg of a cross-family fan-out.
- Live web search / `read_url` / `search_web` is needed (agy's native tools;
  always allowed — no flag required, unlike the codex leader's `--search`).
- Going through this SKILL (instead of raw `antigravity_wrapper.py`) is what makes
  the `unknown` / `extraction-error` / `timeout` path correctly route to the
  `agy-wrapper-repair` named subagent.

## Skip when

- Anthropic-family calls → `triad-claude-dispatch`. Codex's own work → do it
  directly, no leg. gemini CLI (non-individual / Vertex / API-key paths) →
  `triad-gemini-dispatch` if that leg is alive; otherwise agy is the default.

## Hard rules

1. **Literal absolute-wrapper invocation.** Resolve `antigravity_wrapper.py`
   once, then run the absolute launcher/check-out path as the first argv token.
   Do not invoke through `bash -lc`, `zsh -lc`, `python3`, `/usr/bin/env`,
   command substitution, redirection, or inline env assignment; Codex command
   rules match argv prefixes and those shell forms miss the no-prompt allowlist.
   For `--sandbox workspace-write`, run the command with the tool/process
   working directory set to the same trusted workspace passed as `--cwd`. If
   `TRIAD_WRAPPER_ALLOWED_ROOTS` is unset, wrappers trust the process working
   directory by default; set the env var only for extra roots.
2. **Path-based repair input.** Pass the run-log file *path* to the repair
   subagent, never its content (JSON-in-JSON / utf-8 / ANSI / large pty transcript
   corrupt on inline embedding).
3. **Cleanup after dispatch.** `rm -f <run-log-path> <run-log-path>.repair.json`
   once the repair subagent returns (REPAIRED or ESCALATE). The wrapper failsafe
   is for orphans, not normal cleanup.
4. **Repair ONLY on `unknown` / `extraction-error` / `timeout`.** Other
   classifications carry actionable meaning at the wrapper layer — spawning the
   repair agent on them wastes its 3-attempt budget.
5. **Test isolation — production-shape prompt only.** No meta/test framing, no
   "this is a verification" / "treat as fake" disclaimers, even for a sample
   dispatch. The prompt the leg sees must look exactly like a real request.
6. **Repair dispatch is MANDATORY + non-deferrable — spawn it, never skip.** When
   Step 4 routes a failure to repair, you MUST spawn the `agy-wrapper-repair`
   named subagent. Surfacing the failure to the user does NOT discharge this —
   surfacing and repairing are SEPARATE obligations. "I have other work", "the
   call already failed", "looks like a one-off" are NEVER valid reasons to skip.
   The payoff is FUTURE routing (framework completeness), so spawn it CONCURRENTLY
   with your foreground work (`spawn_agent` then continue; `wait_agent` + read the
   response file when you need the outcome). Skipping it is a silent regression
   that lets the same vendor error keep failing un-routed on every later call.
7. **No `--search` flag.** Unlike the claude leg, agy has NO `--search` flag —
   its web tools (`read_url`, `search_web`) are native and always active. Do not
   fabricate a `--search` argument; argparse will reject it.

## Flow

### Step 1 — Build the wrapper invocation

Use an absolute wrapper path literally. Resolve it in a separate command if
needed; do not combine resolution and execution with `&&`, pipes, shell
substitution, or a shell wrapper. For short prompts, pass `--prompt` directly:

```bash
/Users/YOUR_USER/.local/bin/antigravity_wrapper.py \
  --prompt "Read _runs/reviews/<id>/packet.md and review it." \
  [--sandbox read-only|workspace-write] \
  [--model "Gemini 3.1 Pro (High)"] \
  [--pydantic module:Class] \
  [--cwd /absolute/path] \
  [--timeout <seconds>]
```

For a long prompt, write a UTF-8 prompt file first and pass its absolute path:

```bash
/Users/YOUR_USER/.local/bin/antigravity_wrapper.py \
  --prompt-file /absolute/path/to/prompt.txt \
  [--sandbox read-only|workspace-write] \
  [--model "Gemini 3.1 Pro (High)"] \
  [--pydantic module:Class] \
  [--cwd /absolute/path] \
  [--timeout <seconds>]
```

Flags:
- `--sandbox read-only` — per-call `permissions.deny` transaction (global
  `~/.gemini/antigravity-cli/settings.json` mutate+restore, flock-serialized,
  `.agybak` crash-recovery). Blocks `write_file(*)`, `command(*)`,
  `unsandboxed(*)`, `execute_url(*)`, `mcp(*)`. `read_url`/`search_web` remain
  allowed. Pass `--sandbox` flag to agy (OS-ring sandbox) as well.
- `--sandbox workspace-write` — write-capable in the worktree `--cwd`; dangerous
  paths and destructive commands denied. Requires `--cwd`; run the wrapper from
  that same directory unless `TRIAD_WRAPPER_ALLOWED_ROOTS` declares extra roots.
- `--model` — agy display-name string (e.g. `"Gemini 3.1 Pro (High)"`,
  `"Gemini 3.5 Flash (High)"`). Run `agy models` to list accepted strings. No
  dated model IDs in code.
- `--pydantic` — `module:Class` spec; the wrapper appends a JSON-output
  instruction to the prompt and validates the response (agy has no native schema
  mode). Requires `TRIAD_ALLOW_PYDANTIC_IMPORT=1` because it imports Python code.
- `--cwd` — absolute path; required with `--sandbox workspace-write`.
- `--timeout` — seconds (default 600); the wrapper sets `--print-timeout` offset
  internally (`max(timeout - 10, 5)s`).

### Step 2 — Run via Bash; capture rc, stdout, stderr

The wrapper drives agy through a PTY (agy drops stdout on a non-TTY; no
`--output-format json`). Stderr contains a 1-line summary:
`[wrapper] antigravity <classification> exit=<int> vendor=<int> elapsed=<s>`
and, on failure, `run-log: <absolute-path>`. Stdout = the extracted answer (or,
with `--pydantic`, the validated JSON object).

### Step 3 — Read the classification (use the LAST `[wrapper]` line)

The extraction-reclassify path may emit an early line corrected by a later
emission — always take the last:

```bash
SUMMARY=$(grep '^\[.*\] \[wrapper\] antigravity ' <stderr-text> | tail -1)
CLS=$(printf '%s' "$SUMMARY" | sed -E 's/.*\[wrapper\] antigravity ([a-z-]+) .*/\1/')
```

Token set: `ok | server-capacity | cli-subscription-cap | token-limit | oauth-env
| schema-rejected | timeout | extraction-error | unknown`. Exit codes: `0` ok /
`1` cli-fail / `2` timeout / `3` arg / `4` binary-missing / `64`
server-cap-exhausted / `65` terminal / `66` schema fail / `67` schema-rejected.

**agy-specific exit note:** `ANTIGRAVITY_VENDOR_EXIT_MAP[0] = extraction-error`
fires ONLY on the **no-answer path**. A rc=0 agy call with a non-empty extracted
answer returns `ok` and never reaches this mapping. Only when the extractor finds
no usable answer (rc=0 but the completion sentinel was not written) does the `[0]`
entry classify it `extraction-error` (not `ok`) → repair. So do not expect
`extraction-error` on ordinary successful rc=0 calls.

### Step 4 — Branch on classification

| classification (rc) | Leader action |
|---|---|
| `ok` (0) | Return wrapper stdout. With `--pydantic`, stdout is the validated JSON object. |
| terminal (65) — `cli-subscription-cap` / `token-limit` / `oauth-env` | Surface to user with cause (quota / prompt too large / re-login). **NOT** repair territory. Auth is user-managed. |
| `server-capacity` exhausted (64) | Wait + retry, or surface. Wrapper already retried per backoff. |
| `unknown` (1) | **Step 5 — repair subagent (MANDATORY + concurrent; Hard rule 6).** |
| `extraction-error` (1) | **Step 5 — repair subagent.** rc=0 but the extractor found no sentinel / empty answer body. |
| `timeout` (2) | **Step 5 — repair subagent** (route for uniformity; likely ESCALATE). Wrapper fail-fasts (no retry on timeout). |
| schema fail (66) / schema-rejected (67) | Surface, fix the class/schema, re-dispatch. **NOT** repair territory. `66` = post-hoc pydantic validation failed (agy has no native schema mode — the wrapper injects the schema into the prompt and validates the reply). `67` = a submit-time schema refusal (codex-style; not produced by agy). |
| arg (3) / binary missing (4) | Surface to user with cause. |

### Step 5 — Repair via the `agy-wrapper-repair` named subagent

Verified mechanism (personal-scope named agent, spawnable by name): the leader
spawns the agent, continues foreground work, then waits.
The bootstrap-installed repair agent carries `default_permissions =
"triad_repair"`: read the toolkit checkout, write only the classifier config and
bounded `bin/_logs` IPC area, read Python/vendor executable paths needed for
verification, and use network for verification.

#### 5a. Extract the run-log path + derive the output path

```bash
RUN_LOG_PATH=$(grep -oE 'run-log: [^[:space:]]+' <stderr-text> | tail -1 | awk '{print $2}')
[ -f "$RUN_LOG_PATH" ] || { echo "run-log path missing"; exit 1; }
OUTPUT_PATH="${RUN_LOG_PATH}.repair.json"
```

#### 5b. Spawn the named subagent (concurrent), then wait

Use Codex multi-agent: `spawn_agent` the role **`agy-wrapper-repair`**, then
continue any foreground work, then `wait_agent` and read `OUTPUT_PATH`. Give it a
JSON-shaped task with `run_log_path` + `output_path` + the output contract:

```
You are a repair agent with a file-based response contract. Read the run-log, run the repair workflow, then write your JSON response to output_path. Return ONLY a single token: `done` (file written) or `error: <one-line reason>`. Do NOT include the JSON in your reply.

Input:
{
  "run_log_path": "<RUN_LOG_PATH>",
  "output_path": "<OUTPUT_PATH>",
  "output_schema": {
    "outcome":   "<'REPAIRED' if the framework now classifies the error, else 'ESCALATE'>",
    "downstream":"<'ok' | 'terminal:<class>' | 'retry-exhausted' | 'timeout' | null>",
    "patch":     "<'<file:line> — entry added', or null when ESCALATE>",
    "reason":    "<one-line semantic summary>",
    "attempts":  "<int 1-3>",
    "per_attempt_log": "<array of {n, hypothesis, source, patch, py_compile, rerun}>"
  },
  "task": "Extract the literal error from the PTY transcript -> date-anchored web search -> add ONE entry to the bootstrap-configured classifier extension JSON (antigravity envelope) -> re-run with --repair-mode. 3-attempt ceiling, then escalate."
}
```

#### 5c. Read the file-based output + branch

```bash
[ -f "$OUTPUT_PATH" ] || { echo "agent did not write output_path"; exit 1; }
OUTCOME=$(jq -r '.outcome' "$OUTPUT_PATH"); DOWNSTREAM=$(jq -r '.downstream // empty' "$OUTPUT_PATH"); REASON=$(jq -r '.reason' "$OUTPUT_PATH")
```

| OUTCOME | DOWNSTREAM | Next action |
|---|---|---|
| REPAIRED | ok | Re-run the original wrapper call. |
| REPAIRED | terminal:`<class>` | Surface to user with REASON; framework now catches future calls. |
| REPAIRED | retry-exhausted / timeout | Wait+retry or surface; patch is in place. |
| ESCALATE | (omit) | Surface the per-attempt log + REASON; manual diagnosis. |

#### 5d. Cleanup

```bash
rm -f "$RUN_LOG_PATH" "$OUTPUT_PATH"
```

## Outputs

- `ok`: wrapper stdout (raw answer or pydantic-validated JSON).
- terminal: `{ class, reason, action_required }`.
- server-cap-exhausted: transient overload — leader-policy retry or surface.
- repair-cycle: ok-path after re-run, OR ESCALATE per-attempt log.

## See also

- `bin/antigravity_wrapper.py` + `bin/_agy_settings.py` — the leg contract, PTY
  transport, and per-call deny transaction.
- `docs/references/google-family-agy-readonly.md` — live verification: gemini
  individual tier deprecated, agy read-only e2e verified.
- `agents/agy-wrapper-repair.toml` — the named repair subagent (developer_instructions).
- `triad-claude-dispatch` — the Anthropic-family leg.
- `triad-cross-family-review` — composes agy + claude + codex reviewers.
