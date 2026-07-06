---
name: triad-gemini-dispatch
description: Use when the Codex leader needs a single-shot Gemini CLI (gemini -p) answer via the wrapper framework AND the company business/Vertex/API-key tier is specifically wanted. Triggering signals — the leader is about to run gemini_wrapper.py raw; the user said "gemini 한 번 불러줘" / "gemini 로 X 처리" / "gemini 단발 호출" with a business-tier account; a higher-level orchestration needs the gemini leg (not the agy leg) of a fan-out; classification-aware routing with a self-improving repair named-subagent fallback is wanted instead of a raw subprocess. Do NOT use for individual-tier Google accounts (use triad-antigravity-dispatch), for Claude (triad-claude-dispatch), or for the codex leader's own work.
---

# triad-gemini-dispatch

Single-shot **Gemini CLI** (`gemini -p`) dispatch for a **Codex leader**, with
classification-based routing and a self-improving repair loop. Used ONLY for
company business/Vertex/API-key tier Gemini — the individual-tier gemini CLI
is deprecated (IneligibleTierError → Antigravity).

## Use when

- The Codex leader has a discrete prompt and needs Gemini's answer via the
  **company business / Vertex / API-key tier** — e.g. a fresh-eyes second
  opinion with a Google-ecosystem model, or the gemini leg of a cross-family
  fan-out where the business tier is specifically required.
- Going through this SKILL (instead of raw `gemini_wrapper.py`) is what makes
  the `unknown` / `extraction-error` / `timeout` path correctly route to the
  `gemini-wrapper-repair` named subagent.

## Skip when

- **Default Google-family choice → `triad-antigravity-dispatch` (agy).** The
  gemini CLI individual tier is dead (IneligibleTierError — Google deprecated
  it; users on the individual tier see a hard auth failure and must migrate to
  Antigravity). Only come here when a business/Vertex/API-key gemini
  credential is explicitly in play.
- Anthropic Claude calls → `triad-claude-dispatch`.
- Codex's own work → do it directly, no leg.

## Hard rules

1. **Literal absolute-wrapper invocation.** Resolve `gemini_wrapper.py` once,
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
7. **Read-only calls: use `--sandbox read-only`, never `--approval-mode plan`.**
   `plan` is not a wrapper option. It previously crashed the Node/V8 heap on
   heavy files (gemini-cli issues #11321 / #18331 / #26588), so read-only now
   routes through the per-call Policy Engine
   (`--policy bin/policies/gemini-readonly.toml`), which denies mutation + shell
   tools for that call only without the Node OOM. Business-tier Gemini
   read-only remains unverified until the owner runs a write-attempt check in
   that account; if the write-attempt has not been run, prefer agy for gated
   release review.
8. **No plan/yolo approval modes.** The wrapper argparse accepts only
   `--approval-mode default|auto_edit`. `plan` is replaced by the per-call
   read-only policy above, and `yolo` is not a permitted mode in this repo.

## Flow

### Step 1 — Build the wrapper invocation

Use an absolute wrapper path literally. Resolve it in a separate command if
needed; do not combine resolution and execution with `&&`, pipes, shell
substitution, or a shell wrapper. For short prompts, pass `--prompt` directly:

```bash
/Users/YOUR_USER/.local/bin/gemini_wrapper.py \
  --prompt "Read _runs/reviews/<id>/packet.md and review it." \
  [--sandbox read-only|workspace-write] \
  [--approval-mode default|auto_edit] \
  [--model <name>] \
  [--pydantic module:Class] \
  [--skip-trust] \
  [--cwd /absolute/path] \
  [--timeout <seconds>]
```

For a long prompt (≥50K chars, or any multi-KB packet), write a UTF-8 prompt
file first and pass its absolute path (when `TRIAD_WRAPPER_ALLOWED_ROOTS` is
set, the file must resolve inside an allowed root):

```bash
/Users/YOUR_USER/.local/bin/gemini_wrapper.py \
  --prompt-file /absolute/path/to/prompt.txt \
  [--sandbox read-only|workspace-write] \
  [--approval-mode default|auto_edit] \
  [--model <name>] \
  [--pydantic module:Class] \
  [--skip-trust] \
  [--cwd /absolute/path] \
  [--timeout <seconds>]
```

Defaults: `--sandbox read-only` attaches
`bin/policies/gemini-readonly.toml` via the Policy Engine for that call only
(`--policy` flag; see Hard rule 7 — `plan` is not a supported wrapper mode).
On hardened installs (`TRIAD_WRAPPER_HARDENED=1`, the public product's
bootstrap posture), a call that OMITS `--sandbox` defaults to `--sandbox
read-only` — a raw wrapper call is never write-capable by omission; write
access must be requested explicitly.
`--sandbox workspace-write` = write-enabled code-agent; run the wrapper from the
same directory passed as `--cwd` unless `TRIAD_WRAPPER_ALLOWED_ROOTS` declares
extra roots. `--approval-mode default` (read auto, write/shell prompt user) is
the argparse default;
`auto_edit` is write-enabled and therefore conflicts with `--sandbox read-only`.
`--approval-mode plan/yolo` is rejected by argparse.
`--model` is free-form — no dated IDs in code; verify the exact accepted string
against the business/Vertex tier; default = CLI Auto router. `--pydantic`
injects a JSON schema block into the prompt and pydantic-validates the reply
locally (one schema-repair retry, then exit 66); on hardened installs it
additionally requires `TRIAD_ALLOW_PYDANTIC_IMPORT=1` because it imports
Python code.

### Step 2 — Run the direct wrapper command; capture rc, stdout, stderr

Wrapper stderr contains a 1-line summary
`[wrapper] gemini <classification> exit=<int> vendor=<int> elapsed=<s>` and, on
failure, `run-log: <absolute-path>`. Stdout = the answer (or, with `--pydantic`,
the validated JSON object).

### Step 3 — Read the classification (use the LAST `[wrapper]` line)

The extraction-reclassify path emits an early `ok` line later corrected by a
second emission — always take the last:

```bash
SUMMARY=$(grep '^\[.*\] \[wrapper\] gemini ' <stderr-text> | tail -1)
CLS=$(printf '%s' "$SUMMARY" | sed -E 's/.*\[wrapper\] gemini ([a-z-]+) .*/\1/')
```

Token set: `ok | server-capacity | cli-subscription-cap | token-limit |
oauth-env | schema-fail | schema-rejected | timeout | extraction-error |
fanout-spawn-error | config-conflict | task-blocked | unknown`. Or branch on wrapper exit:
`0` ok / `1` cli-fail / `2` timeout / `3` arg / `4` binary-missing /
`64` server-cap-exhausted / `65` terminal / `66` schema fail /
`67` schema-rejected.

**Gemini envelope note:** `gemini -p … --output-format json` returns a single
JSON object `{response, stats, error}`. Classify from stderr AND the `error`
field — not the exit code alone. The wrapper does this internally; you read
the output classification from the `[wrapper]` summary line.

### Step 4 — Branch on classification

| classification (rc) | Leader action |
|---|---|
| `ok` (0) | Return wrapper stdout. With `--pydantic`, stdout is the validated JSON object. |
| terminal (65) — `cli-subscription-cap` / `token-limit` / `oauth-env` / `fanout-spawn-error` / `task-blocked` | Surface to user with cause (quota / prompt too large / re-login or business-tier auth expired / subagent spawn failure / tool permission denial). **NOT** repair territory. Auth is user-managed. |
| `config-conflict` (65) | Local config/settings conflict. Wait briefly and re-dispatch once if it is a lock contention; if repeated or parse/config shaped, surface the config cause. **NOT** repair territory. |
| `server-capacity` exhausted (64) | Wait + retry, or surface. Wrapper already retried per backoff. |
| `unknown` (1) | **Step 5 — surface the top-level read-only analyzer command (MANDATORY; Hard rule 6).** |
| `extraction-error` (1) | **Step 5 — surface the analyzer command.** rc=0 but the extractor found no answer (empty envelope / masked error). |
| `timeout` (2) | **Step 5 — surface the analyzer command** (route for uniformity; likely escalate). Wrapper fail-fasts (no retry on timeout). |
| `schema-fail` (66) / `schema-rejected` (67) | Surface, fix the class/schema, re-dispatch. **NOT** repair territory. `66` = post-hoc pydantic validation failed (gemini's `{response}` validated against the injected schema). `67` = a submit-time schema refusal (codex-style; not produced by gemini). |
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

#### 5b. Surface the command (substitute `$PLUGIN_ROOT_Q`, `$RUN_LOG_Q`; CLI = `gemini`)

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
  printf '%s' "$P" | jq -c '.proposal' | python3 $PLUGIN_ROOT_Q/bin/apply_patch.py --cli gemini
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

- `bin/gemini_wrapper.py` + `bin/policies/gemini-readonly.toml` — the leg
  contract and the per-call read-only policy (Policy Engine, not plan mode).
- `bin/apply_patch.py` — the deterministic, zero-LLM classifier-patch applier
  (the ONLY writer; re-validates every proposal).
- `docs/references/google-family-agy-readonly.md` — live verification:
  individual-tier is dead, plan-mode OOM reproduced, agy is the primary leg.
- `triad-antigravity-dispatch` — the primary Google-family leg (individual +
  business users without a direct gemini business credential).
- `triad-claude-dispatch` — the Anthropic Claude leg.
- `triad-cross-family-review` — composes claude + Google-family + codex
  reviewers.
