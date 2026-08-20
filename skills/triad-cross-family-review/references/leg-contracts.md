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
At the first required-leg failure, terminate every still-running leg and its
exact provider process group, discard every current-round verdict, and never
continue a sibling merely to collect advisory evidence. Confirm termination,
verify integrity, clean the exact round, and repair the defect before a fresh ID.

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
  --expected-review-id "$review_id" \
  --expected-family claude \
  --expected-content-digest "$review_digest" \
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

Before the round, prove `agy --version` is at least 1.1.17 and `agy models`
advertises `gemini-3.1-pro-high`. Before starting any family, run this
non-model wrapper preflight to validate the same binary/version and route:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/antigravity_wrapper.py" \
  --prompt-file "$review_prompt_file" \
  --cwd "$review_shared" \
  --sandbox read-only \
  --model gemini-3.1-pro-high \
  --effort high \
  --preflight-only \
  > "$google_preflight_file"
```

The receipt must report `"provider_started": false`. A preflight failure stops
the round before Claude, Google, or Codex starts. After successful preflight,
use:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/antigravity_wrapper.py" \
  --prompt-file "$review_prompt_file" \
  --cwd "$review_shared" \
  --sandbox read-only \
  --model gemini-3.1-pro-high \
  --effort high \
  --timeout 1800 \
  --pydantic verdict_schema:LegVerdict \
  --expected-review-id "$review_id" \
  --expected-family google \
  --expected-content-digest "$review_digest" \
  > "$google_result_file"
```

The same packaged AGY wrapper supports either personal Google Sign-In or
Business Sign-In for Gemini Enterprise with an owner-provisioned GE Standard
or GE Plus seat. It uses `stream-json`, then validates the terminal result
locally. Matching the deployed Claude-led TRIAD,
formal AGY passes `--sandbox`, uses native `--mode plan`, and brackets the call in a transient global-settings
transaction that unions `write_file(*)`, `command(*)`, `unsandboxed(*)`,
`execute_url(*)`, and `mcp(*)`, and restores the original bytes. AGY 1.1.3+
also receives the wrapper-owned `--dangerously-skip-permissions` adaptation so
headless read tools work, unless the operator sets
`AGY_NO_HEADLESS_AUTOAPPROVE=1`. The formal route omits native `--json-schema` in plan mode because the
selected Business Sign-In backend rejects a custom finish schema before model
execution. It requires the terminal `response` to be one JSON object, then
uses the shared local validator to remove AGY's optional single Markdown fence
around that sole object. It then performs strict local `LegVerdict` validation
and exact review-binding checks. Unmatched, nested, repeated, prose-bearing,
and multiple-object responses are rejected locally.
A missing, malformed, or schema-invalid response terminates the leg with no
schema-repair provider call. The formal Google prompt authorizes only
AGY native file-read/search tools for local inspection, and undecidable
uncertainty goes to `open_questions`. The explicit deny rules remain the
action-namespace enforcement backstop, and a denied call invalidates the leg.
The formal Google settings transaction denies all MCP calls. Approved AGY
native official-web reads remain available only when the review objective and
authorized external data boundary expressly permit them.
Headless auto-approve removes interactive approval prompts but does not remove
those explicit deny entries. Round-integrity mutation detection is separate.
The formal Google leg remains read-only by intent plus explicit deny and
separate round-integrity checks. Callers never pass the flag. The
formal child environment removes known API-key, ADC, Vertex, SDK-enterprise,
cloud project/location/quota, and `AGY_ADC_AUTH` route selectors without reading
their values. Native sign-in state remains provider-owned; TRIAD does not log
in, switch accounts, or choose a billed API route.

The selected formal AGY leg uses the explicit 1,800-second end-to-end wrapper
deadline; shorter polling waits are wake-up boundaries, not provider failures.
Its rendered prompt permits AGY native file-read and search tools for local
inspection but explicitly forbids `run_command`, terminal and shell tools,
file-write/edit tools, notebook execution, subagents, browser actuation, and
scratch-space tools. It also forbids creating or executing experiments; a fact
that static inspection and expressly authorized read-only external evidence
cannot decide belongs in `open_questions`. This prompt contract complements the
deny transaction. Use `grep_search` with the required `SearchPath` and `Query`
arguments to search inside the review target identified by Review metadata, and use `list_dir`,
`find_by_name`, and `view_file` as needed. For every `view_file` call, provide the required
`AbsolutePath` argument. For files larger than one native view, request explicit
positive-integer `StartLine` and `EndLine` ranges. Never request `ContentOffset`
or `IsSkillFile`, and do not rely on implicit another-page continuation. If
native reads and searches are insufficient, report the limit in
`open_questions`. The wrapper scans formal `step_update` telemetry, admits only
the fixed native read/search tool set, and terminates the leg as
`tool-contract-violation` for any other tool, non-object parameters, a missing
or non-integer step index, or conflicting duplicate step telemetry. A tool
attempt in a named denied namespace is also blocked by its matching deny entry;
round-integrity mutation detection remains separate.
Do not edit files, change external state, or execute candidate code, tests,
builds, hooks, or scripts. If AGY, the model, or the settings transaction is
unavailable, invalidate the round. Clean it and repair the same selected AGY
authentication class before restarting every required family under a fresh
review ID. Do not change from personal Google Sign-In to Business Sign-In for
Gemini Enterprise, or the reverse, as recovery.
If the operator opt-out makes headless review unavailable, preserve the opt-out
and report that same-route blocker rather than overriding it.

This exact formal local-validation route makes one provider call. Capacity
failure or invalid output is terminal for that invocation; the wrapper makes no
capacity retry or schema-repair provider call.

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
directory. Construct review_id, family, and content_digest by copying their complete string values directly from the single Review metadata JSON record. Before returning, compare each copied value character-for-character with that record; the three pairs must be identical. Validate it with:

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
