# Native source-observation transport spike

Date: 2026-07-30  
Scope: one generated three-line non-sensitive text file  
Mutation: none

## Objective

Verify that Claude, the Google family through AGY, and a fresh Codex child can
return one exact source-derived observation without candidate execution,
provider-side hashing, permission overrides, or file mutation.

The expected observation was:

```json
{"observation_line":2,"source_observation":"OBSERVATION_ANCHOR_7f31c9a2 exact-source-read"}
```

## Routes and results

- Claude Sonnet, low effort, authenticated native wrapper route: exact JSON
  returned using provider-native file read.
- AGY `1.1.8`, Gemini 3.6 Flash Low, authenticated native route with dangerous
  auto-approval disabled: exact JSON returned when command execution was
  prohibited and provider-native file read was used.
- Fresh Codex `gpt-5.6-terra`, low reasoning, `fork_turns="none"`: exact JSON
  returned using a bounded non-mutating file-read operation.

A second AGY wording trial explicitly mentioned non-mutating commands. AGY
selected its `command` tool and the native headless permission denied it. This
negative control confirms that the common receipt must use an exact source
observation obtainable through native file-read capability; it must not
require provider-side SHA-256 or command execution.

Provider-specific routing guidance may identify the available native read
mechanism. It does not change the common reviewed bytes, objective, evidence
schema, or no-mutation contract.
