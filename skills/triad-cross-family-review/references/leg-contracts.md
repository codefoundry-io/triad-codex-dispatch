# Review leg contracts

## Contents

- [Claude](#claude)
- [Google family](#google-family)
- [Fresh Codex](#fresh-codex)
- [Shared containment boundary](#shared-containment-boundary)

Resolve one absolute toolkit root and one prepared directory. Render one shared
prompt from `review-prompt-contract.md`; only the reviewer perspective and
family-specific tool contract differ. Start every leg before collecting results.
Bind each dynamic path, review ID, and digest to the task-specific
shell variables shown below, then use only double-quoted expansions.
Each provider command writes wrapper stdout to its result path inside the command
itself. If a workspace requires a launcher shell, keep that redirection inside
that launcher command so launcher-startup stdout cannot contaminate the result
JSON. Never strip or filter a contaminated result; invalidate the round, fix the
invocation contract, and restart every required family under a fresh ID.
A preflight or launch-setup failure before any provider leg starts uses cleanup and fresh-ID restart;
classify and correct the zero-provider failure or verify recovery from a transient vendor incident first.
After a second zero-provider failure in the same attempted workflow, stop allocating fresh review IDs.
Retain and compare every failure receipt. For each attempt, record the exact non-secret command, the
outer host-command working directory, the inner bootstrap child working directory, environment
override names without secret values, exit status and error, and provider-start evidence. Compare
those fields with the canonical instruction block, investigate and verify the shared root cause, and
resume only after one controlled setup-only probe demonstrates the corrected path. A changed command
alone is not a correction, and the probe is not a formal review round.
But once any provider leg has started, a later leg start or result failure invalidates admission but
does not cancel sibling execution; do not launch a not-yet-started leg after the failure; wait for every already-started sibling to terminate,
strictly validate every terminal result that is structurally available, and confirm that every exact
provider process tree is gone before integrity verification; run it only after every started leg terminates. Structurally valid results remain
provisional until post-review integrity succeeds. After a matching integrity check, preserve and
reproduce every valid sibling finding as advisory only while classifying the failure as a workflow,
skill, tool, instruction, operator, or vendor problem. A valid `NOT-SAFE` result is not a failed leg
and receives the same complete sibling collection. Valid sibling results never admit the failed
round or supply admission credit to a later round. If integrity fails, treat outputs only as
untrusted leads and independently reproduce any claim before use; diagnose and correct the integrity mismatch before a fresh round. Before preparing a fresh round,
reproduce every collected finding before the next round; correct and verify every reproduced
in-scope defect, and correct the classified leg failure or verify recovery from a transient vendor
incident. A finding that requires a design expansion still stops for owner approval. Clean the exact
round, prepare a fresh ID, and rerun a complete three-family round.

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
provisional Claude leg result until shared final integrity verification succeeds.
The formal Claude leg uses the explicit 1,800-second
end-to-end wrapper deadline. Its exact formally bound `LegVerdict` route adds native
`--permission-mode plan`; the wrapper rejects that formal schema before
provider resolution when any required binding is absent. Provider-native tools,
installed CLI tools, and configured
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

For a prepared-directory round, bind the exact current-round task before selection:

```text
review_task_file="$review_shared/TASK.md"
```

For worktree-first review, bind `review_task_file` to the exact canonical current-round path also
passed to `render-worktree --task-file`. That file must exist before selection and is the selected
wrapper preflight's sole prompt input.

Before starting any family, bind `google_authentication_class` to exactly
`personal-google` or `gemini-enterprise`. The selector launcher must target the same canonical
toolkit root used by every lifecycle renderer and provider wrapper. A wrapper from another
checkout or installed cache remains foreign even when that one file is byte-identical: sibling
modules and the Gemini policy are part of its runtime behavior.

For an installed operational skill whose bootstrap-managed launcher targets that installed
toolkit root, bind it normally:

```text
google_selector_launcher="$(command -v review_round.py)"
```

For a source-SOT pre-deployment round, do not use an older installed launcher. Before preparing
the review packet, create two unique sibling system-temporary directories: one neutral bootstrap
working directory and one task-scoped stage. Bind every path first, keep the launcher directory on
the bootstrap `PATH`, and isolate bootstrap's launcher, Codex-home, configuration, classifier, and
shell-rc targets inside the stage. Run this before packet capture; bootstrap may also create its
ordinary ignored runtime-log directory under the canonical toolkit root:

Keep any project root required by the host executor as the outer host-command working directory.
Inside that login-shell invocation, the shown subshell `cd` sets the inner bootstrap child working
directory; the bootstrap guard evaluates the child process's `PWD`. Do not substitute the toolkit
root or stage root for that child directory. Preserve the login user's `HOME`; isolate Codex with
`CODEX_HOME`, not `HOME`, exactly as shown.

```text
selector_bootstrap_cwd_raw="$(mktemp -d "${TMPDIR:-/tmp}/triad-selector-cwd.${review_id}.XXXXXX")"
selector_stage_root_raw="$(mktemp -d "${TMPDIR:-/tmp}/triad-selector-stage.${review_id}.XXXXXX")"
selector_bootstrap_cwd="$(realpath "$selector_bootstrap_cwd_raw")"
selector_stage_root="$(realpath "$selector_stage_root_raw")"
selector_launcher_dir="$selector_stage_root/bin"
selector_stage_codex_home="$selector_stage_root/codex-home"
selector_stage_config_home="$selector_stage_root/config-home"
selector_stage_classifier="$selector_stage_config_home/triad-codex-dispatch/classifier-patches.json"
selector_stage_shell_rc="$selector_stage_root/shellrc"
(
  cd "$selector_bootstrap_cwd" &&
  CODEX_HOME="$selector_stage_codex_home" \
  XDG_CONFIG_HOME="$selector_stage_config_home" \
  TRIAD_CLASSIFIER_EXTENSION="$selector_stage_classifier" \
  TRIAD_BOOTSTRAP_SHELL_RC="$selector_stage_shell_rc" \
  TRIAD_BOOTSTRAP_REPO_ROOT="$toolkit_root" \
  TRIAD_BOOTSTRAP_BIN_DIR="$selector_launcher_dir" \
  PATH="$selector_launcher_dir:$PATH" \
    "$toolkit_root/scripts/bootstrap.sh" --install
)
google_selector_launcher="$selector_launcher_dir/review_round.py"
```

The two `mktemp` results must be distinct canonical directories, and neither may contain the
other, the toolkit root, or the review worktree. Record both as current-round temporary handles.
If staging fails or the launcher does not exist as a canonical executable, no review root or
provider may start. Remove only those two exact directories after the round terminates or after a
pre-provider failure, and confirm both are absent.

Then exclusive-create one round-owned selector receipt:

```text
"$google_selector_launcher" select-google-route \
  --review-id "$review_id" \
  --authentication-class "$google_authentication_class" \
  --output "$google_selector_receipt"
```

The command must resolve to the bootstrap-managed launcher for the canonical toolkit root's
packaged `review_round.py`.
Do not prefix it with `python3`: that launcher supplies the install-resolved AGY and Gemini pins,
explicitly records either absence, and requires pinned-vendor selection without exporting pin
variables into the shell. A missing or shadowed selector launcher is a route-setup failure.

The exclusive-created canonical receipt reports the review ID, `"provider_started": false`,
its executable and wrapper,
and one of these bindings: `{"authentication_class": "personal-google", "route": "agy"}`
or `{"authentication_class": "gemini-enterprise", "route": "agy"}` or
`{"authentication_class": "gemini-enterprise", "route": "gemini"}`. AGY is preferred.
Personal Google Sign-In requires AGY. Gemini Enterprise OAuth may select Gemini only when
AGY is absent. Pass the same file as `--google-selector-receipt` to the selected wrapper's preflight,
every family render, and dispatch, and never rerun or replace it for that round. Pass the resulting
canonical `google_preflight_file` as `--google-preflight-receipt` to every render and to the selected
wrapper's dispatch. The renderer and wrapper require its review ID, executable, route, selector
SHA-256, exact receipt SHA-256, model, effort, and ordered AGY route arguments to remain bound. The renderer
derives the common admission digest and Google tool contract from the receipt; the wrapper executes
its canonical executable directly instead of resolving PATH or accepting another caller pin. After selection,
any provider, auth, entitlement, model, policy, capacity, or schema failure invalidates the
round; it never switches to the other route.

For a prepared-directory round, pass the exact digest printed by `capture` as each render's
`--content-digest` input. The renderer verifies that prepared digest and emits one route-bound
`metadata.content_digest`; bind `review_digest` to that emitted value. Every family in the round
must have the same route-bound value. A missing, foreign-round, or mixed selector receipt is invalid.

For an AGY receipt, the wrapper proves `"$google_executable" --version` is at least 1.1.20 and parses
only literal tab-separated rows from `"$google_executable" models`; the exact first-column slug must
advertise `gemini-3.1-pro-high`. Run this provider-free wrapper preflight:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/antigravity_wrapper.py" \
  --prompt-file "$review_task_file" \
  --google-selector-receipt "$google_selector_receipt" \
  --expected-review-id "$review_id" \
  --cwd "$review_shared" \
  --sandbox read-only \
  --model gemini-3.1-pro-high \
  --effort high \
  --preflight-only \
  > "$google_preflight_file"
```

The receipt must report `"provider_started": false`. A preflight failure stops
the round before Claude, Google, or Codex starts. For a Gemini receipt, run the
provider-free Gemini preflight instead:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/gemini_wrapper.py" \
  --prompt-file "$review_task_file" \
  --google-selector-receipt "$google_selector_receipt" \
  --expected-review-id "$review_id" \
  --cwd "$review_shared" \
  --preflight-only \
  > "$google_preflight_file"
```

The preflight prompt is the current task file, so no family prompt exists yet. It executes the
receipt's Gemini CLI, validates the packaged read-only policy, and runs
only `gemini --help` with competing auth and model selectors removed. It must prove
`--model`, native `--approval-mode plan`, and `--policy` help-surface support and
report `"provider_started": false`, model `auto`, requested approval mode `plan`,
effective approval mode `unexposed`, the mode-independent packaged policy as the
read-only enforcement boundary, the review ID, selected executable, route, and
selector-receipt SHA-256. Help output does not attest merged settings or workspace
trust. The AGY preflight reports the same common
binding fields. Each subsequent `render` or `render-worktree` invocation must include:

```text
--google-selector-receipt "$google_selector_receipt" \
--google-preflight-receipt "$google_preflight_file"
```

Only after the selected preflight succeeds may the leader render the family prompts and start the
families. For an AGY receipt, use:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/antigravity_wrapper.py" \
  --prompt-file "$review_prompt_file" \
  --google-selector-receipt "$google_selector_receipt" \
  --google-preflight-receipt "$google_preflight_file" \
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

For a Gemini receipt, use the same rendered Google prompt and binding values through the
existing packaged Gemini wrapper:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/gemini_wrapper.py" \
  --prompt-file "$review_prompt_file" \
  --google-selector-receipt "$google_selector_receipt" \
  --google-preflight-receipt "$google_preflight_file" \
  --cwd "$review_shared" \
  --timeout 1800 \
  --pydantic verdict_schema:LegVerdict \
  --expected-review-id "$review_id" \
  --expected-family google \
  --expected-content-digest "$review_digest" \
  > "$google_result_file"
```

The formal Gemini route uses the existing organization Sign in with Google/OAuth cache and
preserves required Cloud-project selection. It removes competing API-key, ADC, Vertex, base-URL,
Cloud Shell, and compute-ADC selectors without reading their values. The caller does not pass
permission, model, or policy flags: the wrapper injects explicit `-m auto`, requests
native `--approval-mode plan`, and applies the packaged
`bin/policies/gemini-formal-readonly.toml`; effective approval mode is `unexposed`.
That mode-independent user-tier policy allows only Gemini native
`read_file`, `read_many_files`, `list_directory`, `glob`, `grep_search`, `google_web_search`,
`web_fetch`, and `get_internal_docs`; it explicitly denies writes, shell, Plan Mode transitions,
and every other tool. Admin policy remains a higher tier. The prompt forbids AGY native tool names,
subagents, experiments, and `enter_plan_mode`/`exit_plan_mode`. The wrapper never
adds `--skip-trust` or speculatively reads user settings. CLI Auto router remains unpinned;
the current JSON envelope exposes no authoritative single model identity, so record exactly
`runtime_identity: "unexposed"` and never infer it from `stats.models`, account class, or route. The exact formal
bindings are required before provider resolution and checked locally after the one provider call.
Capacity failure or invalid output is terminal; there is no capacity retry, schema-repair call,
or post-start route fallback.

The same packaged AGY wrapper supports either personal Google Sign-In or
Business Sign-In for Gemini Enterprise with an owner-provisioned GE Standard
or GE Plus seat. It uses `stream-json`, then validates the terminal result
locally. Matching the deployed Claude-led TRIAD,
formal AGY passes `--sandbox`, uses native `--mode plan`, and brackets the call in a transient global-settings
transaction that unions `write_file(*)`, `command(*)`, `unsandboxed(*)`,
`execute_url(*)`, and `mcp(*)`, and restores the original bytes. The formal route
also receives the wrapper-owned `--dangerously-skip-permissions` adaptation so
headless read tools work, unless the operator sets
`AGY_NO_HEADLESS_AUTOAPPROVE=1`. After the required version preflight, it passes
a review-bound native `--json-schema` in plan mode and consumes the terminal
`structured_output`. It then repeats strict local `LegVerdict` validation and
exact review-binding checks. Human-readable response text and diagnostic finish
messages are not verdict transport.
A missing, malformed, or schema-invalid structured output terminates the leg with no
schema-repair provider call. The formal AGY prompt authorizes only
AGY native file-read/search tools for local inspection, and undecidable
uncertainty goes to `open_questions`. The explicit deny rules remain the
action-namespace enforcement backstop and block matching calls before execution.
The formal AGY settings transaction denies all MCP calls. Approved AGY
native official-web reads remain available only when the review objective and
authorized external data boundary expressly permit them.
Headless auto-approve removes interactive approval prompts but does not remove
those explicit deny entries. Round-integrity mutation detection is separate.
The formal AGY leg remains read-only by intent plus explicit deny and
separate round-integrity checks. Callers never pass the flag. The
formal AGY child environment removes known API-key, ADC, Vertex, SDK-enterprise,
cloud project/location/quota, and `AGY_ADC_AUTH` route selectors without reading
their values. Native sign-in state remains provider-owned; TRIAD does not log
in, switch accounts, or choose a billed API route.

The selected formal AGY leg uses the explicit 1,800-second end-to-end wrapper
deadline.
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
`open_questions`. Formal `step_update` telemetry is diagnostic vendor output,
not an admission schema: added fields, changed optional tool arguments, denied
attempts, and duplicate progress events do not invalidate an otherwise valid
terminal verdict. The prompt and native `--mode plan` define the static-review
behavior. A tool attempt in a named denied namespace is also blocked by its
matching deny entry. The explicit deny rules remain the action-namespace
enforcement backstop. Local verdict and review-binding checks establish
provisional validity; round-integrity verification decides final admission. Round-integrity
mutation detection is separate.
Do not edit files, change external state, or execute candidate code, tests,
builds, hooks, or scripts. If the selected provider contract is unavailable,
invalidate the round. Clean it and repair that same selected route and
authentication class before restarting every required family under a fresh
review ID. Do not change authentication class or route as recovery.
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
A mismatch invalidates admission for the complete round; treat outputs only as untrusted leads
that require independent reproduction. Verification does not retroactively prevent the mutation.
