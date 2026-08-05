# Review leg contracts

Resolve one absolute toolkit root and one prepared directory. Render one shared
prompt from `review-prompt-contract.md`; only the reviewer perspective and
authorized provider route differ. Start every leg before collecting results.

## Claude

Use the packaged wrapper with the formal-quality route:

```text
python3 <toolkit>/bin/claude_wrapper.py
  --prompt-file <leader-owned-prompt>
  --cwd <prepared-directory>
  --model opus
  --effort xhigh
  --pydantic verdict_schema:LegVerdict
```

Claude receives no implementation task. Its terminal validated JSON is the
Claude leg result.

## Google family

Before the round, prove `agy --version` is at least 1.1.10 and `agy models`
advertises `gemini-3.1-pro-high`. Use:

```text
python3 <toolkit>/bin/antigravity_wrapper.py
  --prompt-file <leader-owned-prompt>
  --cwd <prepared-directory>
  --model gemini-3.1-pro-high
  --effort high
  --pydantic verdict_schema:LegVerdict
```

The wrapper uses AGY native `stream-json` plus `json-schema` and validates the
terminal result locally. Do not add sandbox, permission-bypass, or code-writing
flags. If AGY is unavailable before submission, the leader may select the
documented Gemini route before starting a fresh round. A failure after
submission invalidates the Google leg; do not substitute providers mid-round.

For a separately authorized pre-submission Gemini fallback, use the packaged
wrapper and the exact owner-authorized Gemini model:

```text
python3 <toolkit>/bin/gemini_wrapper.py
  --prompt-file <leader-owned-prompt>
  --cwd <prepared-directory>
  --model <owner-authorized-gemini-model>
  --pydantic verdict_schema:LegVerdict
```

This exact formal schema route makes one provider call. Capacity failure or
invalid structured output is terminal for that invocation; the wrapper makes
no capacity retry or schema-repair provider call.

## Fresh Codex

Spawn a fresh default child with:

```text
fork_turns = "none"
model = "gpt-5.6-terra"
reasoning_effort = "xhigh"
agent_type omitted
```

Give it the same absolute prepared directory, objective, criteria, digest,
read/search-only contract, and `LegVerdict` shape. The child must not edit or
execute candidate code. Save its terminal JSON outside the prepared directory
and validate it with:

```text
python3 <toolkit>/bin/verdict_schema.py validate
  --result-file <codex-result>
  --expected-review-id <review-id>
  --expected-family codex
  --expected-content-digest <digest>
```

The no-edit contract is prompt-controlled unless runtime metadata proves a
stronger boundary. Mutation detection, not a sandbox claim, decides admission.
