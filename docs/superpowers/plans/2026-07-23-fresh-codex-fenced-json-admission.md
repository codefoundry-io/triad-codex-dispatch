# Fresh Codex Native Semantic Result Admission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` and
> `superpowers:test-driven-development`. This bounded review-fix is Lunar-only;
> the root leader owns orchestration and verification.

**Goal:** Admit one native fresh-Codex terminal review result by semantic
content, without imposing an external CLI JSON transport contract.

**Architecture:** Keep the existing semantic review checks and four required
elements. Document that native `spawn_agent` messages may be ordinary Markdown,
labeled prose, or JSON. Keep Claude CLI extraction distinct from native Codex
admission. Separately record that a formal non-Pydantic AGY review is admitted
semantically: required semantic fields remain admissible despite Markdown
fences. AGY transport, completion sentinel, extraction, routing, and fallback
remain unchanged; no AGY wrapper transport behavior changes.

## Global constraints

- Apply the semantic admission contract only to the native fresh-Codex leg.
- Require `verdict`, `findings`, `affected_surfaces_inspected`, and
  `open_questions`; do not infer missing meaning.
- Presentation fences and non-JSON rendering alone are not invalid, findings, or
  candidate defects. JSON serialization/parsing is not required.
- Retain citation validity, SAFE contradiction, mutation/prohibited-execution,
  fingerprint, and exposed-route checks.
- Do not modify Claude, AGY, Gemini, wrappers, parsers, fallback, route behavior,
  README, SECURITY, CHANGELOG, bootstrap, or the AGY workaround.
- R16 was owner-paused during that implementation; no provider dispatch belonged
  to that change. The owner later resumed R16 explicitly, and the resulting round
  is recorded in the handoff ledgers.
- Do not commit, push, install, merge, release, or create a PR.

---

### Task 1: Replace the incorrect fresh-Codex JSON transport contract

**Files:**

- Modify: `tests/test_distribution_contract.py`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `skills/triad-cross-family-review/references/fresh-codex-formal-review.md`
- Modify: `docs/superpowers/plans/2026-07-23-r11-minor-hardening.md`
- Modify: `docs/superpowers/specs/2026-07-23-fresh-codex-fenced-json-admission-design.md`
- Modify: `docs/superpowers/plans/2026-07-23-fresh-codex-fenced-json-admission.md`

**Interface:** A native `spawn_agent` terminal message is admitted by its
semantic review elements and existing evidence gates, not by JSON parsing.

- [x] **Step 1: Replace the fenced-JSON regression with semantic RED assertions**

Require the fresh-Codex prompt and Result admission section to identify the
native agent message rather than CLI stdout, require the four semantic elements,
allow Markdown/labeled prose/JSON without requiring JSON parsing, and state that
presentation fences alone are not invalid. Pin missing/ambiguous content and
all citation, verdict, mutation, fingerprint, and route checks. Keep the R16
historical R16 owner-paused/no-provider-dispatch assertion in both task docs.

- [x] **Step 2: Run RED**

Run the focused distribution-contract selector from the workspace-root login
shell. The expected failures identify the stale fenced-JSON wording and missing
semantic/R16 contract markers.

- [x] **Step 3: Apply the minimum semantic-contract documentation fix**

Qualify the cross-family JSON example as wrapper-backed material. State the
native semantic result contract in the cross-family skill and fresh-Codex
reference, remove `Return one JSON object only`, outer-fence normalization, and
malformed-JSON admission rules, and preserve the existing evidence checks.
Rewrite this design and plan to explain the corrected root cause: native
`spawn_agent` is not an external CLI envelope. The historical implementation
pause is recorded in the handoff ledgers; the owner later resumed R16 explicitly.

- [x] **Step 4: Run GREEN and nearby distribution coverage**

Run the focused selector, then the complete
`tests/test_distribution_contract.py` file. Require zero failures.

- [x] **Step 5: Verify text integrity**

Run `git diff --check` and `git diff --cached --check`. Do not dispatch
providers or perform external mutation.
