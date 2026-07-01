# Google-family leg: gemini CLI deprecated → agy; read-only VERIFIED (2026-07-01)

Live verification during the Codex-led-mirror work. Binding for the (future)
Codex Google-family dispatch skill.

## Finding 1 — gemini CLI individual tier is DEAD (live)

`gemini 0.46.0` with the individual Code Assist login now fails auth:

> `IneligibleTierError: This client is no longer supported for Gemini Code
> Assist for individuals. To continue using Gemini, please migrate to the
> Antigravity suite of products: https://antigravity.google`

Matches Google's "Transitioning Gemini CLI to Antigravity CLI" announcement and
the source repo's README note (gemini degrades after 2026-07-31). → For
individual-tier users the Google-family leg is **agy**, not gemini.

## Finding 2 — the "plan mode crashes on heavy files" bug (gemini)

Client-side Node/V8 **heap OOM**, independent of model — reproduced even with
`-m gemini-2.5-pro` (gemini-cli issue #11321; also #11285/#18331/#26588).
`--approval-mode plan` is literally "plan (read-only mode)" but plan-mode's extra
work triggers the OOM; a policy-based read-only avoids it. `NODE_OPTIONS=
--max-old-space-size=8192` mitigates. Moot for individual users now (auth dead).
agy is Go → no Node heap OOM.

## Finding 3 — agy works + carries the models

`agy models` → **Gemini 3.1 Pro (Low/High)**, Gemini 3.5 Flash (Low/Med/High),
Claude Sonnet 4.6 / Opus 4.6 (Thinking), GPT-OSS 120B. Pin the Pro model via
`--model "Gemini 3.1 Pro (High)"` (display names; confirm the exact accepted
string when wiring the wrapper). No dated model IDs pinned in code (per rule).

## Finding 4 — agy read-only is PER-CALL + preserves the code-agent role (VERIFIED)

The agy wrapper's `--sandbox read-only` applies
`_READ_ONLY_DENY = ["write_file(*)", "command(*)", "unsandboxed(*)",
"execute_url(*)", "mcp(*)"]` as a per-call `permissions.deny` transaction on
`~/.gemini/antigravity-cli/settings.json`, then restores byte-exactly
(flock-serialized, `.agybak` crash-recovery).

**E2E verification (2026-07-01):** a `--sandbox read-only` **write attempt was
BLOCKED** (no file created) and the agy settings md5 was **identical
before/after** (restored, no leak). So read-only is **per-call opt-in, NOT
global** — a `--sandbox workspace-write` call stays write-capable → the
code-agent role is preserved.

## Binding decision for the Codex-led repo

1. **Google-family dispatch leg = agy** (`triad-antigravity-dispatch`). The
   gemini CLI leg is deprecated for individual tier — keep it only if a
   business / Vertex / API-key path is ever needed (then it's a separate,
   non-default leg).
2. **Read-only / heavy-file / consult dispatches → agy `--sandbox read-only`**
   (NOT gemini plan mode). Go runtime avoids the Node heap OOM entirely.
3. **Never bake a global read-only policy** (it would kill the code-agent role).
   Read-only is ALWAYS per-call; the same leg does write/code work under
   `--sandbox workspace-write`. This mirrors codex's per-call `--sandbox`.
4. Cross-family review's Google leg = agy (already the spec's preferred choice);
   gemini is not a live fallback for individual tier.
