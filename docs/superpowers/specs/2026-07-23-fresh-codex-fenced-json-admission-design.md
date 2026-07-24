# Fresh Codex Native Semantic Result Admission Design

Date: 2026-07-23

## Goal

Admit the native fresh-Codex terminal result by its review meaning rather than
by an external CLI serialization format. Markdown, labeled prose, and JSON are
presentation choices; none changes the semantic contract.

## Corrected root cause

The native fresh-Codex leg is created with `spawn_agent` and returns a native
agent message and terminal state. Treating that message as if it were stdout
from a wrapper-backed CLI incorrectly imposed JSON serialization and parsing.
Comparing Codex to Claude's CLI envelope was therefore the wrong abstraction.
Claude's wrapper extraction and the AGY/Gemini result contracts remain separate.

## Approved AGY presentation decision

Claude CLI extraction is a wrapper transport concern and remains distinct from
native Codex admission. Separately, a formal non-Pydantic AGY review is
admitted semantically: required semantic fields remain admissible despite
Markdown fences. This is only a presentation tolerance. AGY transport,
completion sentinel, extraction, routing, and fallback remain unchanged, and
no AGY wrapper transport behavior changes.

## Selected behavior

For the native fresh-Codex leg only, require these four semantic elements:

1. an unambiguous `verdict`;
2. `findings` with supported evidence;
3. `affected_surfaces_inspected`; and
4. `open_questions`.

The elements may be rendered as ordinary Markdown, labeled prose, or JSON.
JSON parsing is not required. Presentation fences or other non-JSON framing
alone are not invalid and are never a finding or candidate defect. Do not infer
missing meaning: a terminal response is invalid/missing when an element or
unambiguous verdict is absent, evidence is unsupported, citations are invalid,
`SAFE` contradicts Critical/Major findings or open questions, the agent mutated
or executed prohibited work, the fingerprint changed, or exposed route metadata
conflicts.

The four semantic elements and all existing citation, verdict, mutation,
fingerprint, and route checks remain required. Wrapper-backed JSON examples in
the cross-family skill are qualified as wrapper material and do not govern this
native leg.

## Scope and non-goals

This applies only to the native fresh-Codex leg documented by
`triad-cross-family-review`, with the separately recorded AGY presentation
tolerance above. Do not alter Claude, AGY, Gemini, any wrapper or parser,
fallback, route behavior, or the AGY display-label workaround; the AGY
decision changes no runtime behavior.

R16 was owner-paused during that implementation. No provider dispatch belonged
to that change. The owner later resumed R16 explicitly, and the resulting round
is recorded in the handoff ledgers.

## Verification

Distribution-contract tests pin the native semantic contract, the absence of a
fresh-Codex JSON-parser requirement, the retained admission checks, and the
historical R16/no-dispatch boundary. No provider call is part of this change.
