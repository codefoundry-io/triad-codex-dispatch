# Review leg contracts

## Contents

- [Claude](#claude)
- [Google family](#google-family)
- [Fresh Codex](#fresh-codex)
- [Shared containment boundary](#shared-containment-boundary)

Resolve one absolute toolkit root and one prepared directory. Render one shared
prompt from `review-prompt-contract.md`; only the reviewer perspective and
authorized provider route differ. Start every leg before collecting results.
Bind each dynamic path, review ID, digest, and fallback model to the task-specific
shell variables shown below, then use only double-quoted expansions.
Each provider command writes wrapper stdout to its result path inside the command
itself. If a workspace requires a launcher shell, keep that redirection inside
that launcher command so launcher-startup stdout cannot contaminate the result
JSON. Never strip or filter a contaminated result; invalidate the round, fix the
invocation contract, and restart every required family under a fresh ID.

## Claude

Use the packaged wrapper with the formal-quality route:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/claude_wrapper.py" \
  --prompt-file "$review_prompt_file" \
  --cwd "$review_shared" \
  --model opus \
  --effort xhigh \
  --timeout 1800 \
  --pydantic verdict_schema:LegVerdict \
  > "$claude_result_file"
```

Claude receives no implementation task. Its terminal validated JSON is the
Claude leg result. The formal Claude leg uses the explicit 1,800-second
end-to-end wrapper deadline; shorter polling waits are wake-up boundaries, not
provider failures. Provider-native tools, installed CLI tools, and configured
MCP tools remain available for reads and searches inside the authorized review
boundary. Configured MCP servers remain available. Existing user permission
settings continue to govern MCP calls. Approved official-web reads through
read-only MCP tools remain available when the review objective and authorized
external data boundary permit them. Do not edit files, change external state,
or execute candidate code, tests, builds, hooks, or scripts.

Validate the Claude result with:

```text
python3 "$toolkit_root/bin/verdict_schema.py" validate \
  --result-file "$claude_result_file" \
  --expected-review-id "$review_id" \
  --expected-family claude \
  --expected-content-digest "$review_digest"
```

## Google family

Before the round, prove `agy --version` is at least 1.1.10 and `agy models`
advertises `gemini-3.1-pro-high`. Use:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/antigravity_wrapper.py" \
  --prompt-file "$review_prompt_file" \
  --cwd "$review_shared" \
  --model gemini-3.1-pro-high \
  --effort high \
  --timeout 1800 \
  --pydantic verdict_schema:LegVerdict \
  --expected-review-id "$review_id" \
  --expected-family google \
  --expected-content-digest "$review_digest" \
  > "$google_result_file"
```

The wrapper uses AGY native `stream-json` plus `json-schema` and validates the
terminal result locally. Its native schema and local admission bind the exact
review ID, Google family, content digest, and review-relative path shape before
the result file is written. The selected formal AGY leg uses the explicit 1,800-second
end-to-end wrapper deadline; shorter polling waits are wake-up boundaries, not
provider failures. The wrapper internally inserts
`--dangerously-skip-permissions`. Callers do not pass this flag. The wrapper
does not edit user settings, add a command-specific allowlist or sandbox, or
suppress tools. Provider-native tools, installed CLI tools, and configured MCP
tools remain available for reads and searches inside the authorized review
boundary.
Do not edit files, change external state, or execute candidate code, tests,
builds, hooks, or scripts. If AGY is unavailable before submission, the leader
may select the documented Gemini route before starting a fresh round. A
failure after submission invalidates the Google leg; clean it, correct the
route, and restart every required family under a fresh review ID instead of
substituting providers mid-round.

For a separately authorized pre-submission Gemini fallback, use the packaged
wrapper and the exact owner-authorized Gemini model:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/gemini_wrapper.py" \
  --prompt-file "$review_prompt_file" \
  --cwd "$review_shared" \
  --model "$review_gemini_model" \
  --pydantic verdict_schema:LegVerdict \
  > "$google_result_file"
```

The owner-approved 1,800-second correction applies to the selected AGY route
that produced the observed post-submission timeout. It does not silently change
this separately authorized fallback's deadline; any such change requires its
own owner decision.

This exact formal schema route makes one provider call. Capacity failure or
invalid structured output is terminal for that invocation; the wrapper makes
no capacity retry or schema-repair provider call.

Validate the Google result with:

```text
python3 "$toolkit_root/bin/verdict_schema.py" validate \
  --result-file "$google_result_file" \
  --expected-review-id "$review_id" \
  --expected-family google \
  --expected-content-digest "$review_digest"
```

## Fresh Codex

Spawn a fresh default child with:

```text
fork_turns = "none"
model = "gpt-5.6-terra"
reasoning_effort = "xhigh"
agent_type omitted
```

Give it the same absolute prepared directory, objective, criteria, digest, and
`LegVerdict` shape. Provider-native tools, installed CLI tools, and configured
MCP tools remain available for reads and searches inside the authorized review
boundary. Do not edit files, change external state, or execute candidate code,
tests, builds, hooks, or scripts. Save its terminal JSON outside the prepared
directory and validate it with:

```text
python3 "$toolkit_root/bin/verdict_schema.py" validate \
  --result-file "$codex_result_file" \
  --expected-review-id "$review_id" \
  --expected-family codex \
  --expected-content-digest "$review_digest"
```

## Shared containment boundary

The no-edit contract is prompt-controlled unless runtime metadata proves a
stronger boundary. Mutation detection, not a sandbox claim, decides admission.
The prepared-directory digest monitors every prepared regular file; the
canonical-worktree fingerprint monitors Git HEAD, staged and unstaged tracked
changes, and non-ignored untracked entries. Because legs retain native tools,
separate selected-member comparisons cover listed source members even when
Git-ignored. Mutations in other Git-ignored worktree paths, paths outside both
directories, and network egress of packet content are neither prevented nor
detected. Legs run in parallel against the same prepared directory,
so a mid-round mutation may affect another leg's reads before final verification.
A mismatch invalidates the complete round and discards every verdict; verification
does not retroactively prevent the mutation.
