# Spike E — `claude -p` envelope + failure signals (real CLI)

**Date:** 2026-07-01 · **CLI:** claude 2.1.196 · **Task:** plan Task 0.

## Environment caveat (READ FIRST)

This spike ran inside a **Claude Desktop child session**
(`CLAUDE_CODE_CHILD_SESSION=1`, `CLAUDE_CODE_ENTRYPOINT=claude-desktop`), where
auth is host-injected via OAuth refresh into the SDK
(`CLAUDE_CODE_SDK_HAS_OAUTH_REFRESH=1`) rather than a keychain/API-key a fresh
subprocess can read. A freshly-spawned `claude -p` therefore gets **HTTP 401**.

- **This is not a leg-design defect.** In production the Codex leader runs in a
  normal shell where `claude` is independently authenticated (its own
  `claude` login / keychain), so `claude -p` authenticates normally.
- **Consequence:** the live **success** and **structured_output** envelopes could
  NOT be captured here, and plan **Task 6 (real-vendor smoke) must run in a
  standalone shell** where `claude` is logged in (not this nested session). The
  hermetic fake-CLI tests (Tasks 4–5) fully exercise wrapper logic without auth.
- **Production requirement (record in migration docs):** the claude leg needs
  `claude` independently authenticated in the shell where the wrapper runs.

## 1. Envelope shape — CONFIRMED (superset of the 2026-05-05 note)

`--output-format json` returns one object with these top-level keys (observed):

```
type, subtype, is_error, api_error_status, duration_ms, duration_api_ms,
num_turns, result, stop_reason, session_id, total_cost_usd,
usage{input_tokens, output_tokens, cache_creation_input_tokens,
      cache_read_input_tokens, server_tool_use{web_search_requests,
      web_fetch_requests}, service_tier, cache_creation{...}, inference_geo,
      iterations, speed},
modelUsage, permission_denials, terminal_reason, fast_mode_state, uuid
```

`extract_claude_answer` reads `result` (+ `structured_output` after Task 3);
`structured_output` was NOT observable live (auth blocked) but is documented in
`claude-leg-spec.md` / the headless reference and is covered by fake-CLI tests.

## 2. Error envelope (auth 401) — REAL CAPTURE → `oauth-env`

```json
{"type":"result","subtype":"success","is_error":true,"api_error_status":401,
 "result":"Failed to authenticate. API Error: 401 Invalid authentication credentials",
 "stop_reason":"stop_sequence","permission_denials":[],"terminal_reason":"completed", ...}
```

- **Exit code: 1** (generic — even with a well-formed envelope).
- **Note:** `subtype` was `"success"` even though `is_error:true` — so
  `is_error` (not `subtype`) is authoritative for the failure decision. The
  existing `extract_claude_answer` already keys on `is_error` → correct.
- **Task 5 classification mapping:** `api_error_status == 401` and/or the phrase
  **`"invalid authentication credentials"`** (lowercased, distinctive, FP-safe)
  → `oauth-env` (terminal; user re-login; never repair). Add the phrase to
  `OAUTH_ENV_PATTERNS`; do NOT add bare `401`.

## 3. Invalid `--json-schema` — CLI arg-level error (not an envelope)

`claude -p 'hi' --output-format json --json-schema 'THIS-IS-NOT-JSON'`:

```
stderr: Error: --json-schema is not valid JSON: JSON Parse error: Unexpected identifier "THIS"
stdout: (empty)   exit: 1
```

- A malformed schema is rejected **before** any envelope is produced → surfaces
  as empty stdout + stderr `Error:`. The wrapper builds the schema from a
  validated pydantic class, so this is a defensive edge; if it occurs, it lands
  as `extraction-error` (empty stdout) — acceptable. Distinct from the
  `subtype: error_max_structured_output_retries` runtime case (Task 3), which was
  not reproducible without auth.

## 4. Exit codes observed

| Case | exit | classify from |
|---|---|---|
| is_error=true (401) | 1 | envelope (`is_error`/`api_error_status`) |
| invalid `--json-schema` | 1 | stderr `Error:` + empty stdout |

Exit `1` is generic → **classify from the JSON envelope, not the exit code**
(confirms the plan's Global Constraint). `CLAUDE_VENDOR_EXIT_MAP` stays
`{0: "ok"}`; no stable non-zero vendor code proven to add.

## 5. Impact on the plan

- **Task 3** (structured_output extraction): proceed per spec; the `structured_output`
  field + `error_max_structured_output_retries` subtype are covered by fake-CLI
  tests (live capture blocked by auth). No change to the plan.
- **Task 5** (classification): add `"invalid authentication credentials"` →
  `OAUTH_ENV_PATTERNS` (real evidence above). More phrases (quota/overload) need a
  live-auth capture — defer to the standalone-shell smoke.
- **Task 6** (real smoke): must run in a standalone, `claude`-authenticated shell.
- **Migration docs:** add the "claude independently authenticated" requirement.
