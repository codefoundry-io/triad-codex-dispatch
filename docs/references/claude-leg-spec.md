# Claude Leg Spec — `claude_wrapper.py` (Claude Code `claude -p` single-shot)

**Status:** reference spec for the new Codex-led toolkit. Target home in the new
repo: `skills/triad-claude-dispatch/references/claude-headless-spec.md`.
**Verified against:** Claude Code **v2.1.196** (`claude --help`) + official docs
`code.claude.com/docs/en/{headless,cli-reference,model-config,env-vars}.md` +
Agent SDK `structured-outputs`. Extraction date 2026-07-01.

> **ERRATA (2026-07-02):** no-prompt Codex rules require the wrapper command's
> first argv token to be an absolute launcher path. Dispatch skills
> must not wrap the wrapper in `bash -lc`, `zsh -lc`, `python3`, `/usr/bin/env`,
> heredoc command substitution, redirection, or inline env assignment. Long
> prompts use wrapper `--prompt-file /absolute/path`.

This spec defines how the new **claude leg** is driven as a single-shot worker,
mirroring the existing `gemini_wrapper.py` / `codex_wrapper.py` legs and reusing
the leg-agnostic `_common.py` (single-shot IPC → JSON envelope extraction →
fixed classification token set → run-log JSON → optional schema validation).

The transport is `claude -p ... --output-format json`. Claude's `json` envelope
is a single object (like Gemini's `{response, stats, error}`), so extraction and
classification follow the Gemini leg pattern, NOT the Codex JSONL-events pattern.

---

## 0. Framework invariants (carried over from the existing legs)

- **Wrapper never manages auth.** User runs Claude's own login. `oauth-env` is a
  terminal, surface-to-user class; the repair agent must never touch auth.
- **No-yolo.** `--permission-mode bypassPermissions` and
  `--dangerously-skip-permissions` are **banned at argparse** (mirror Codex
  banning `danger-full-access`).
- **No model IDs pinned in code.** `--model` accepts an alias
  (`opus`/`sonnet`/`haiku`/`fable`); the subscription auto-routes. Dated full IDs
  appear in **audit logs only**, never in wrapper defaults (global user rule).
- **Single-shot, ephemeral.** `--no-session-persistence` = Codex `--ephemeral`.
- **Classification token set is shared** across all legs; the claude leg maps
  Claude's signals onto it (see §6). Exit codes reuse `_common`'s codes.

---

## 1. Canonical invocation (default command shape)

```bash
claude -p '<INSTRUCTION>' \
  --output-format json \
  --no-session-persistence \
  --permission-mode dontAsk \
  --allowedTools "Read,Glob,Grep" \
  [--model <alias>] \
  [--effort <low|medium|high|xhigh|max>] \
  [--json-schema '<schema>'] \
  [--append-system-prompt '<...>'] \
  [--fallback-model <alias,alias>] \
  [--bare]
```

- Deliver short instructions via wrapper `--prompt`; deliver long instructions
  via wrapper `--prompt-file /absolute/path`. Do not use heredoc command
  substitution in no-prompt dispatch commands because Codex command rules will
  not match the wrapper prefix.
- **Do NOT rely on pure piped stdin for the instruction.** Docs are ambiguous:
  piped stdin is treated as *additional context* when an argv prompt is present,
  and as the sole instruction only when used alone. For deterministic behavior
  the wrapper passes the instruction on argv. Piped stdin cap = **10 MB**
  (v2.1.128+); exceeding it errors. → For large inputs use the file-IPC rule
  (§9), not giant stdin.

---

## 2. Read-only vs workspace-write (the `--sandbox` equivalent)

**Claude has no `--sandbox` flag.** The equivalent is `--permission-mode` +
`--allowedTools`. In headless (`-p`, non-TTY) interactive prompts cannot be
answered, so `default` mode would hang/deny — the wrapper must pick a
non-prompting mode.

| Leg intent | Wrapper `--sandbox` | Claude flags |
|---|---|---|
| **read-only (default)** | `read-only` | `--permission-mode dontAsk --allowedTools "Read,Glob,Grep[,WebSearch,WebFetch]"` — no prompts, denies all writes/unlisted tools |
| **workspace-write** (future claude `--task code`) | `workspace-write` | `--permission-mode acceptEdits` (auto-approves file writes + `mkdir/touch/mv/cp`); requires an isolated `--cwd`/worktree, leader-managed |
| **banned** | `danger-full-access` | `bypassPermissions` / `--dangerously-skip-permissions` — argparse-rejected |

- `dontAsk` = "deny anything not in `permissions.allow` or the read-only set" —
  the deterministic non-interactive read-only mode. `--allowedTools` feeds the
  allow-set. (`auto` is a looser alternative; `dontAsk` + explicit allowlist is
  more predictable → chosen default.)
- The wrapper uses `--cwd <repo-root>` for repository context. Large review
  packets are passed as absolute or repo-relative paths inside the prompt; the
  read-only leg opens them with the allowed `Read` tool.

---

## 3. Web search (opt-in — mirror Codex `--search`)

- **OFF by default in print mode.** No env toggle.
- Enable by adding tools to the allowlist:
  `--allowedTools "Read,Glob,Grep,WebSearch,WebFetch"`.
- Wrapper `--search` flag → injects `WebSearch,WebFetch` into `--allowedTools`.
  Same opt-in semantics as the Codex leg's `--search`; leave OFF for routine
  calls, ON for research/consult/review.
- Web-tool usage is visible in the envelope:
  `usage.server_tool_use.{web_search_requests,web_fetch_requests}`.

---

## 4. Model / tier selection

- `--model <alias|full-id>`. Aliases: `default`, `best`, `fable`, `opus`,
  `sonnet`, `haiku`, `opusplan`, `sonnet[1m]`, `opus[1m]`.
- **Wrapper policy:** accept `--model <alias>`, default **unset** (inherit the
  account default). Never pin a dated full ID in the wrapper. The resolved exact
  ID is available in the envelope `modelUsage.model` → record in audit only.
- `--fallback-model <alias,alias>` — comma chain, max 3, tries each on
  overloaded/unavailable, skips retired. Optional wrapper passthrough.

---

## 5. Reasoning / effort (mirror Codex `--reasoning`)

- `--effort {low,medium,high,xhigh,max}`. Default **high** (xhigh on Opus 4.7).
  Unsupported levels fall back to the highest supported ≤ requested.
- **`max`** = deepest, no token cap, **session-only** (or via
  `CLAUDE_CODE_EFFORT_LEVEL`). Codex tops out at `xhigh`.
- **Wrapper policy:** map wrapper `--reasoning` → claude `--effort`. Set by
  intent (high for review/planning, low for mechanical). Leave unset for routine.
- ⚠️ **Owner decision (§11):** mirror the Codex enum `{low,medium,high,xhigh}`
  exactly, or expose claude's extra `max` for deep review on the claude leg only.

---

## 6. Output envelope → extraction + classification

Run with `--output-format json`. Single top-level result object. Extractor reads
`.result` (answer text), or `.structured_output` when `--json-schema` is set.

**Envelope fields the wrapper reads:** `type`, `subtype`, `is_error`,
`api_error_status`, `result`, `stop_reason`, `structured_output`,
`terminal_reason`, `permission_denials`, `modelUsage.model`, `total_cost_usd`,
`usage`, `session_id`, `duration_ms`.

**Claude has NO documented exit-code taxonomy** (only 0=success / 1=generic /
126 / 127 observed). → **Classify from the JSON envelope, not the exit code.**

| Shared class (rc) | Claude signal to detect |
|---|---|
| `ok` (0) | exit 0, `is_error=false`, `.result` present (or `.structured_output` when schema) |
| `extraction-error` (1) | exit 0 / `is_error=false` but no `.result` and no `.structured_output` (empty answer) → repair |
| `schema-fail` (66) | `subtype == "error_max_structured_output_retries"` (structured-output retries exhausted). NB: Claude has no submit-time schema *rejection*, so class `schema-rejected`(67) is **N/A** for this leg |
| `oauth-env` (65, terminal) | `is_error=true` + `api_error_status ∈ {401,403}`, or stream error category `authentication_failed` / `oauth_org_not_allowed`. **Surface for re-login; never repair.** |
| `cli-subscription-cap` (65, terminal) | error category `billing_error`, or 429 tied to quota/subscription |
| `server-capacity` (64, retryable) | error category `overloaded` / `server_error`, or `api_error_status ∈ {500,503,529}`. Framework backoff applies |
| `token-limit` (65, terminal) | error category `max_output_tokens`, context/input-too-large, or the 10 MB stdin-cap error |
| `timeout` (2) | wrapper outer-timeout kill (no built-in claude timeout) → repair-route for uniformity |
| `unknown` (1) | nonzero exit with no recognized envelope/stderr pattern → repair agent |

- The **fine-grained error category enum** lives in `stream-json`
  `api_retry`/error events:
  `authentication_failed | oauth_org_not_allowed | billing_error | rate_limit |
  overloaded | invalid_request | model_not_found | server_error |
  max_output_tokens | unknown`. `json` mode exposes `is_error` +
  `api_error_status` + `subtype` + `terminal_reason`, which is sufficient for the
  table above. **Owner decision (§11):** if finer classification is needed, the
  wrapper can add a `stream-json` pass; default is `json` (simpler, one object).
- `permission_denials[]` non-empty with an otherwise-empty result ⇒ a
  `task-blocked`-style signal (leg lacked a needed tool) — surface, not repair.

---

## 7. Structured output (`--pydantic` support)

- Wrapper `--pydantic module:Class` → generate JSON Schema → pass via
  `--json-schema '<schema>'` → read `.structured_output` → then **still
  Pydantic-validate locally** (defense in depth; mirrors the Codex/Gemini path).
- The implemented wrapper rejects `--pydantic` unless
  `TRIAD_ALLOW_PYDANTIC_IMPORT=1` is set, because loading a schema module imports
  Python code and no-prompt dispatch may run the wrapper outside the Codex
  sandbox.
- Failure: `subtype == error_max_structured_output_retries` → `schema-fail` (rc 66).
- Supported schema features: `object/array/string/number/boolean/null`, `enum`,
  `const`, `required`, nested objects, `$ref`.

---

## 8. Timeout, lifecycle, auth

- **No built-in print timeout** → the wrapper enforces its own (existing
  `_common` timeout). Related env: `API_TIMEOUT_MS` (default 600000),
  `BASH_DEFAULT_TIMEOUT_MS` (120000).
- `--no-session-persistence` = ephemeral single-shot (no resumable session).
- **Auth (user-managed, wrapper never touches):** priority
  `ANTHROPIC_API_KEY` → `apiKeyHelper` (via `--settings`) → OAuth/keychain
  (skipped in `-p`). 3P: `CLAUDE_CODE_USE_BEDROCK` / `_VERTEX` / `_FOUNDRY` /
  `_ANTHROPIC_AWS` with their own creds.
- `--bare` (CI-only, opt-in, default OFF): skips hooks/skills/plugins/MCP/CLAUDE.md
  and forces `ANTHROPIC_API_KEY`/`apiKeyHelper` auth. **Off by default** because a
  claude review leg may legitimately want skills/MCP; enable only for locked CI.

---

## 9. Large packets (file-IPC — mirror v0.9.0 rule)

Because piped stdin is capped at 10 MB and is treated as *context* (not the sole
instruction), large review/consult packets must NOT go through giant stdin:

1. Leader/wrapper writes the packet to a file under the repo/run dir.
2. Invoke the wrapper with `--cwd <repo-root>` and reference the packet path
   inside the argv prompt (e.g. "Read `<path>` and review it").
3. Claude reads the file with its `Read` tool (allowed in the read-only policy).

This is the same file-IPC-for-LARGE-packets contract the framework already uses.

---

## 10. Worked examples

```bash
# Read-only single-shot Q&A (no web)
claude -p 'Explain the tradeoff between X and Y in one paragraph.' \
  --output-format json --no-session-persistence \
  --permission-mode dontAsk --allowedTools "Read,Glob,Grep"

# Research dispatch (web search ON, high effort)
claude -p 'What changed in <lib> in the last month? Cite sources.' \
  --output-format json --no-session-persistence --effort high \
  --permission-mode dontAsk --allowedTools "Read,Grep,WebSearch,WebFetch"

# Structured output (--pydantic → --json-schema)
claude -p 'Extract all TODOs.' --output-format json --no-session-persistence \
  --permission-mode dontAsk --allowedTools "Read,Grep,Glob" \
  --json-schema '{"type":"object","properties":{"todos":{"type":"array","items":{"type":"string"}}},"required":["todos"]}'

# Cross-family review leg (large packet via file-IPC)
claude -p 'Read _runs/reviews/<id>/packet.md and review it; frame suspect decisions as questions.' \
  --output-format json --no-session-persistence --effort high \
  --permission-mode dontAsk --allowedTools "Read,Grep"
```

---

## 11. Open decisions (owner call before implementation)

1. **Reasoning enum**: mirror Codex `{low,medium,high,xhigh}` exactly, or allow
   claude's extra `max` on the claude leg?
2. **Read-only allowlist**: minimal Q&A (`Read,Glob,Grep`) vs review-oriented
   (add `WebSearch,WebFetch` only under `--search`). Confirm the default set.
3. **Default model**: leave unset (account default) vs pin alias `sonnet` for
   cheap legs / `opus` for review legs.
4. **Classification granularity**: `json`-only (simpler) vs an added `stream-json`
   pass for the fine error-category enum. Default `json`.
5. **`--bare` default**: keep OFF (skills/MCP available) — confirm for the
   company's locked-CI posture.

---

## 12. Sources

- Official: `code.claude.com/docs/en/headless.md`, `.../cli-reference.md`,
  `.../model-config.md`, `.../env-vars.md`, `.../agent-sdk/structured-outputs.md`.
- Tier-2: installed `claude --help` (v2.1.196), live `--output-format json` sample.
- Full raw extraction (682-line reference) retained alongside this spec.
