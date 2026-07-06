---
name: triad-claude-dispatch
description: Use when the Codex leader needs a single-shot Claude Code (claude -p) answer via the wrapper framework. Triggering signals — the leader is about to run claude_wrapper.py raw; the user said "claude 한 번 불러줘" / "claude 로 X 처리" / "클로드 단발 호출"; a higher-level orchestration (e.g. triad-cross-family-review) needs the claude leg of a fan-out; classification-aware routing with a self-improving repair named-subagent fallback is wanted instead of a raw subprocess. Do NOT use for gemini/agy (triad-antigravity-dispatch / triad-gemini-dispatch) or for the codex leader's own work.
---

# triad-claude-dispatch

Single-shot **Claude Code** (`claude -p`) dispatch for a **Codex leader**, with
classification-based routing and a self-improving repair loop. The Codex leader's
standard "call claude once" path — the mirror of the Claude-led toolkit's
`triad-codex-dispatch`, inverted (here Codex is the leader, claude is the leg).

## Use when

- The Codex leader has a discrete prompt and needs Claude's answer (or a
  structured failure signal) — e.g. a fresh-eyes second opinion, an
  Anthropic-ecosystem prompt, or the claude leg of a cross-family fan-out.
- Going through this SKILL (instead of raw `claude_wrapper.py`) is what makes the
  `unknown` / `extraction-error` / `timeout` path correctly route to the
  `claude-wrapper-repair` named subagent.

## Skip when

- Google-family calls → `triad-antigravity-dispatch` (agy, primary) or
  `triad-gemini-dispatch`. Codex's own work → do it directly, no leg.

## Hard rules

1. **Literal absolute-wrapper invocation.** Resolve `claude_wrapper.py` once,
   then run the absolute launcher path as the first argv token. Do
   not invoke through `bash -lc`, `zsh -lc`, `python3`, `/usr/bin/env`, command
   substitution, redirection, or inline env assignment; Codex command rules
   match argv prefixes and those shell forms miss the no-prompt allowlist.
   For `--sandbox workspace-write`, run the command with the tool/process
   working directory set to the same trusted workspace passed as `--cwd`. If
   `TRIAD_WRAPPER_ALLOWED_ROOTS` is unset, wrappers trust the process working
   directory by default; set the env var only for extra roots.
2. **Path-based repair input.** The repair analyzer reads the run-log *path*,
   never its content pasted inline (JSON-in-JSON / utf-8 / ANSI / large stdout
   corrupt on inline embedding). Step 5 surfaces a command that substitutes the
   path.
3. **Cleanup after dispatch.** `rm -f <run-log-path>` once the failure has been
   surfaced (the run-log is transient repair IPC). The wrapper failsafe is for
   orphans, not normal cleanup.
4. **Repair ONLY on `unknown` / `extraction-error` / `timeout`.** Other
   classifications carry actionable meaning at the wrapper layer — surfacing the
   repair command on them wastes the owner's time.
5. **Test isolation — production-shape prompt only.** No meta/test framing, no
   "this is a verification" / "treat as fake" disclaimers, even for a sample
   dispatch. The prompt the leg sees must look exactly like a real request.
6. **On a repair-routed classification, SURFACING the failure + the ready-to-paste
   top-level analyzer command is MANDATORY.** codex-host does NOT spawn an
   in-session repair worker — the write-capable subagent was the confused deputy
   (a subagent driven by an untrusted vendor run-log, inheriting the leader
   sandbox and a classifier/`bin/_logs` write grant). A hard-safe codex analyzer
   only runs top-level, in a FRESH terminal (a nested codex under the session
   sandbox cannot initialize; top-level is hard read-only + spike-verified
   2026-07-05). "I have other work", "the call already failed", "looks like a
   one-off" are NEVER valid reasons to skip the surface. The payoff is FUTURE
   routing (framework completeness): a surfaced-and-run analyzer grows the
   classifier so the same vendor error auto-routes next time. Skipping the surface
   is a silent regression.

## Flow

### Step 1 — Build the wrapper invocation

Use an absolute wrapper path literally. Resolve it in a separate command if
needed; do not combine resolution and execution with `&&`, pipes, shell
substitution, or a shell wrapper. For short prompts, pass `--prompt` directly:

```bash
/Users/YOUR_USER/.local/bin/claude_wrapper.py \
  --prompt "Read _runs/reviews/<id>/packet.md and review it." \
  --sandbox read-only \
  [--effort low|medium|high|xhigh|max] \
  [--fallback-model <alias>] \
  [--pydantic module:Class] \
  [--cwd /absolute/path] \
  [--timeout <seconds>]
```

For a long prompt (≥50K chars, or any multi-KB packet), write a UTF-8 prompt
file first and pass its absolute path (when `TRIAD_WRAPPER_ALLOWED_ROOTS` is
set, the file must resolve inside an allowed root):

```bash
/Users/YOUR_USER/.local/bin/claude_wrapper.py \
  --prompt-file /absolute/path/to/prompt.txt \
  --sandbox read-only \
  [--effort low|medium|high|xhigh|max] \
  [--fallback-model <alias>] \
  [--pydantic module:Class] \
  [--cwd /absolute/path] \
  [--timeout <seconds>]
```

Write-capable variant (code tasks only) — `--cwd` is MANDATORY and must be an
isolated directory (a dedicated worktree, never a shared checkout):

```bash
/Users/YOUR_USER/.local/bin/claude_wrapper.py \
  --prompt "Apply the fix described in task.md." \
  --sandbox workspace-write \
  --cwd /absolute/isolated/worktree \
  [--timeout <seconds>]
```

**Sandbox contract (wrapper-ENFORCED — pass `--sandbox` on every call).** On
installs where the bootstrap pins `TRIAD_CLAUDE_ENFORCE_SANDBOX=1`, omitting
`--sandbox` is an argument error (raw transport-only dispatch is disabled).

- `--sandbox read-only` — the wrapper synthesizes `--tools "Read,Glob,Grep"`
  + `--strict-mcp-config` + `--setting-sources user` + `--permission-mode
  dontAsk`. `--tools` is a real RESTRICTION of the worker's tool surface.
  (Do NOT substitute the older `--permission-mode dontAsk --allowedTools
  "Read,Glob,Grep"` recipe: `--allowedTools` only PRE-APPROVES the listed
  tools — it never denies unlisted ones, so it restricts nothing.)
  Isolation rationale: `--setting-sources user` means the dispatched-into
  repo's project settings, hooks, and CLAUDE.md are NOT loaded — a read leg
  must not execute a target repo's hooks or inherit its framing — and
  `--strict-mcp-config` blocks settings-inherited MCP servers. No web tools
  are available in read-only (the claude wrapper has no `--search` flag;
  route web-grounded research to the agy leg).
- `--sandbox workspace-write` — synthesizes `--permission-mode acceptEdits` +
  `--strict-mcp-config` and REQUIRES `--cwd`. Blast radius: `acceptEdits`
  auto-approves file-mutating commands including `rm`, `rmdir`, and in-place
  `sed`, so the worker can delete or rewrite anything under its working
  directory without a prompt — the only containment is WHERE it runs, which
  is why the wrapper hard-fails (arg error) when `--cwd` is missing. Point
  `--cwd` at an isolated worktree.
- `--sandbox` and `--permission-mode` are mutually exclusive (`--sandbox`
  synthesizes the permission posture); `--permission-mode bypassPermissions`
  is banned at argparse.

Other flags: `--effort` = claude's reasoning effort (`max` = deepest — use it
for review legs). `--fallback-model <alias>` = auto-fallback when the default
model is overloaded (alias only — no dated IDs). `--pydantic` injects a JSON
schema block into the prompt and pydantic-validates the reply locally (one
schema-repair retry, then exit 66); on hardened installs it additionally
requires `TRIAD_ALLOW_PYDANTIC_IMPORT=1` because it imports Python code.

### Step 2 — Run the direct wrapper command; capture rc, stdout, stderr

Wrapper stderr contains a 1-line summary
`[wrapper] claude <classification> exit=<int> vendor=<int> elapsed=<s>` and, on
failure, `run-log: <absolute-path>`. Stdout = the answer (or, with `--pydantic`,
the validated JSON object).

### Step 3 — Read the classification (use the LAST `[wrapper]` line)

The extraction-reclassify path emits an early `ok` line later corrected by a
second emission — always take the last:

```bash
SUMMARY=$(grep '^\[.*\] \[wrapper\] claude ' <stderr-text> | tail -1)
CLS=$(printf '%s' "$SUMMARY" | sed -E 's/.*\[wrapper\] claude ([a-z-]+) .*/\1/')
```

Token set: `ok | server-capacity | cli-subscription-cap | token-limit | oauth-env
| schema-fail | schema-rejected | timeout | extraction-error | fanout-spawn-error
| config-conflict | task-blocked | unknown`. Or branch on wrapper exit: `0` ok / `1` cli-fail /
`2` timeout / `3` arg / `4` binary-missing / `64` server-cap-exhausted /
`65` terminal / `66` schema fail / `67` schema-rejected.

### Step 4 — Branch on classification

| classification (rc) | Leader action |
|---|---|
| `ok` (0) | Return wrapper stdout. With `--pydantic`, stdout is the validated JSON object. |
| terminal (65) — `cli-subscription-cap` / `token-limit` / `oauth-env` / `fanout-spawn-error` / `task-blocked` | Surface to user with cause (quota / prompt too large / re-login / subagent spawn failure / tool permission denial). **NOT** repair territory. Auth is user-managed. |
| `config-conflict` (65) | Local config/settings conflict. Wait briefly and re-dispatch once if it is a lock contention; if repeated or parse/config shaped, surface the config cause. **NOT** repair territory. |
| `server-capacity` exhausted (64) | Wait + retry, or surface. Wrapper already retried per backoff. |
| `unknown` (1) | **Step 5 — surface the top-level read-only analyzer command (MANDATORY; Hard rule 6).** |
| `extraction-error` (1) | **Step 5 — surface the analyzer command.** rc=0 but the extractor found no answer (empty envelope / masked error). |
| `timeout` (2) | **Step 5 — surface the analyzer command** (route for uniformity; likely escalate). Wrapper fail-fasts (no retry on timeout). |
| `schema-fail` (66) / `schema-rejected` (67) | Surface, fix the class/schema, re-dispatch. **NOT** repair territory. `66` = the `--pydantic` path failed: the prompt-injected schema reply did not validate locally after the one schema-repair retry (a vendor `error_max_structured_output_retries` envelope also promotes to `schema-fail`). `67` = a submit-time schema refusal (codex-style; not normally produced by claude). |
| arg (3) / binary missing (4) | Surface to user with cause. |

### Step 5 — Surface the top-level read-only analyzer command (do NOT spawn)

On `unknown` / `extraction-error` / `timeout` the leader spawns NOTHING and
writes nothing. It extracts the run-log path and REPORTS to the user: the
classification, the run-log path, and a **ready-to-paste command to run in a
FRESH terminal** (NOT this codex session — a nested codex cannot initialize under
the session sandbox, so the analyzer only inits when launched top-level; top-level
it is hard read-only and a write is DENIED — spike-verified 2026-07-05).

The analyzer is READ-ONLY: it reads the run-log and the local classification
framework, then returns ONE inline JSON proposal. It has NO write authority; the
deterministic `bin/apply_patch.py` (which re-validates the proposal — exit 3 if
invalid) is the ONLY writer. The `< /dev/null` is MANDATORY (else codex blocks on
stdin and hangs).

#### 5a. Extract the run-log path + shell-quote the substituted paths

```bash
RUN_LOG_PATH=$(grep -oE 'run-log: [^[:space:]]+' <stderr-text> | tail -1 | awk '{print $2}')
[ -f "$RUN_LOG_PATH" ] || { echo "run-log path missing"; exit 1; }
# Shell-quote BOTH values the surfaced command interpolates. The owner's install
# path can legitimately contain a single quote (e.g. /Users/O'Brien/…); pasted raw
# into the single-quoted prompt string below it would terminate the quote and the
# path remainder would run as a shell command. printf %q makes each value a safe,
# paste-proof shell token. (The run-log basename is wrapper-generated + metacharacter
# -free — this guards the OWNER-PATH quote, which is real code-exec-on-paste.)
RUN_LOG_Q=$(printf '%q' "$RUN_LOG_PATH")
PLUGIN_ROOT_Q=$(printf '%q' "<PLUGIN_ROOT>")
```

#### 5b. Surface the command (substitute `$PLUGIN_ROOT_Q`, `$RUN_LOG_Q`; CLI = `claude`)

Report the classification + run-log path to the user, then give them this
ready-to-paste command. Substitute the `%q`-quoted values from 5a (NOT the raw
paths). Run it in a FRESH terminal, NOT this codex session:

The prompt body stays a SINGLE-quoted literal (it contains JSON `"…"`); the
`%q` values expand UNQUOTED — `-C $PLUGIN_ROOT_Q` and, in the prompt, spliced
via close/reopen `'…at '$RUN_LOG_Q' (use…'`. `printf %q` output is built for an
unquoted context (a surrounding `"…"` would keep its escape backslashes literal),
so do NOT wrap `$PLUGIN_ROOT_Q` / `$RUN_LOG_Q` in double quotes. This makes a
quote in the owner path (e.g. `/Users/O'Brien/…`) unable to break out of the literal.

```bash
# Run in a FRESH terminal — grows the classifier for this error. Read-only analyzer; it cannot write.
# $PLUGIN_ROOT_Q / $RUN_LOG_Q are the printf %q results from 5a (paste-proof against a quote in the owner path).
# NOTE: %q values expand UNQUOTED (no surrounding double quotes) — that is how %q escaping is meant to be used.
P=$(codex exec -s read-only --skip-git-repo-check --ephemeral -c approval_policy=never \
      -C $PLUGIN_ROOT_Q \
      'You are a READ-ONLY repair analyzer. Read the run-log at '$RUN_LOG_Q' (use your read tools).
You may read the engine module in bin/ to see the classification framework: the valid classification tokens are
the keys of map_classification_to_exit(); the pattern-list names are the *_PATTERNS constants.
Decide the classification from the run-log + that local framework. Network is OFF — do not web-search;
if you cannot classify from local evidence, escalate. Return ONLY one inline JSON object as your
entire final message (no prose, no code fence):
{"outcome":"propose"|"escalate","reason":"<one line>","proposal":<object|null>}
where proposal (present iff propose) = {"classification":"<token>","reason":"<one line>", and EITHER
"vendor_exit_code":<int> XOR ("pattern_list":"<NAME>","substring":"<literal>")}. You do NOT apply —
the caller does.' < /dev/null)
if printf '%s' "$P" | jq -e '.outcome=="propose"' >/dev/null 2>&1; then
  printf '%s' "$P" | jq -c '.proposal' | python3 $PLUGIN_ROOT_Q/bin/apply_patch.py --cli claude
else
  printf 'escalated: %s\n' "$(printf '%s' "$P" | jq -r '.reason')"
fi
```

- `propose` → the piped `apply_patch.py` validates + applies ONE classifier entry
  (exit 0 applied, exit 3 rejected as invalid). Future calls auto-route.
- `escalate` → the analyzer could not classify from local evidence; surface the
  reason for manual diagnosis.

#### 5c. Cleanup

```bash
rm -f "$RUN_LOG_PATH"
```

## Outputs

- `ok`: wrapper stdout (raw answer or pydantic-validated JSON).
- terminal: `{ class, reason, action_required }`.
- server-cap-exhausted: transient overload — leader-policy retry or surface.
- repair-cycle: surfaced top-level analyzer proposes → `apply_patch.py` applies
  the classifier entry (future auto-routing), OR escalate (surface reason).

## See also

- `bin/claude_wrapper.py` + `docs/references/claude-leg-spec.md` — the leg contract.
- `bin/apply_patch.py` — the deterministic, zero-LLM classifier-patch applier
  (the ONLY writer; re-validates every proposal).
- `triad-antigravity-dispatch` / `triad-gemini-dispatch` — the Google-family legs.
- `triad-cross-family-review` — composes claude + Google-family + codex reviewers.
