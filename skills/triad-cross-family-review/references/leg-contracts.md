# Review leg contracts

## Contents

- [Claude](#claude)
- [Google family](#google-family)
- [Fresh Codex](#fresh-codex)
- [Shared containment boundary](#shared-containment-boundary)

Resolve one canonical toolkit root and one current review target. Render every
family prompt with that toolkit and bind each dynamic path, review ID, digest,
and result location to a task-specific shell variable before invoking a wrapper.
Use double-quoted expansions and write wrapper stdout directly to the result
file so launcher output cannot contaminate the terminal JSON.

These sections own provider-specific argv and terminal receipt handling.
`review_round.py` owns lifecycle paths, inventory, collision checks, prompt
metadata, and Google receipt selection and binding. Google selectors and wrappers
enforce the selected Google route; the Claude wrapper enforces formal binding
completeness, native Plan Mode, schema, local verdict validation, and output
handling. The exact argv below owns Claude and fresh Codex route parameters. Use
[reviewer routing](reviewer-routing.md) for route choice and
[convergence](convergence.md) for every setup, launch, result, integrity, or
finding outcome.

Before any provider preflight or dispatch, bind one route-neutral working
directory. Use `review_target_cwd="$review_shared"` for a prepared-directory
round and `review_target_cwd="$review_worktree"` for worktree-first review.

## Claude

Use the packaged wrapper with the formal-quality route:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/claude_wrapper.py" \
  --prompt-file "$review_prompt_file" \
  --cwd "$review_target_cwd" \
  --model opus \
  --effort xhigh \
  --timeout 1200 \
  --pydantic verdict_schema:LegVerdict \
  --expected-review-id "$review_id" \
  --expected-family claude \
  --expected-content-digest "$review_digest" \
  > "$claude_result_file"
```

The wrapper adds Claude's native `--permission-mode plan` and requires the exact
`opus`/`xhigh`/1,200-second/no-fallback route before provider resolution. It also
checks formal bindings and locally validates the terminal JSON. Read/search tools
remain available inside the authorized boundary under existing user permissions.
The result stays provisional until final integrity succeeds.

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

For worktree-first review, bind `review_task_file` to the canonical current-round
path also passed to `render-worktree --task-file`. It must exist before selection
and is the preflight's sole prompt input. Bind `google_authentication_class` to
`personal-google` or `gemini-enterprise` as selected under
[reviewer routing](reviewer-routing.md).

For an installed operational skill whose bootstrap-managed launcher targets that installed
toolkit root, bind it normally:

```text
google_selector_launcher="$(command -v review_round.py)"
```

For source-SOT pre-deployment, stage an isolated launcher group from that exact
toolkit before packet capture. Keep the required project root as the outer host
working directory; the inner bootstrap child uses the neutral temporary working
directory. Preserve the login user's `HOME`, isolate Codex with `CODEX_HOME`,
and pass the canonical review worktree for deterministic containment checks:

```text
selector_bootstrap_cwd_raw="$(mktemp -d "${TMPDIR:-/tmp}/triad-selector-cwd.${review_id}.XXXXXX")"
selector_stage_root_raw="$(mktemp -d "${TMPDIR:-/tmp}/triad-selector-stage.${review_id}.XXXXXX")"
selector_bootstrap_cwd="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve(strict=True))' "$selector_bootstrap_cwd_raw")"
selector_stage_root="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve(strict=True))' "$selector_stage_root_raw")"
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
  TRIAD_BOOTSTRAP_SOURCE_SOT_REVIEW_ROOT="$review_worktree" \
  TRIAD_BOOTSTRAP_BIN_DIR="$selector_launcher_dir" \
  PATH="$selector_launcher_dir:$PATH" \
    "$toolkit_root/scripts/bootstrap.sh" --install
)
google_selector_launcher="$selector_launcher_dir/review_round.py"
```

Require two distinct canonical temporary directories outside one another, the
toolkit, and the review worktree. Record both as exact current-round cleanup
handles. A staging or executable check failure closes provider launch and follows
[convergence](convergence.md).
The bootstrap guard rejects the bootstrap cwd, staged launcher directory, Codex
home, classifier directory, or shell rc when it resolves inside the toolkit or
review worktree; this check runs before any installation step. After normal
terminal completion or any failure before a provider starts, remove only
`selector_bootstrap_cwd` and `selector_stage_root`, then confirm both paths are
absent.

Then exclusive-create one round-owned selector receipt:

```text
"$google_selector_launcher" select-google-route \
  --review-id "$review_id" \
  --authentication-class "$google_authentication_class" \
  --output "$google_selector_receipt"
```

Invoke this bootstrap-managed launcher directly; it supplies install-resolved
vendor executable pins. The exclusive-created receipt and subsequent preflight
receipt are immutable current-round inputs. Pass both to every render and to the
selected Google wrapper. The renderer and wrapper validate all route, executable,
model, effort, receipt-hash, and review-ID bindings.

For a prepared-directory round, pass the digest printed by `capture` to each
render and bind `review_digest` to the renderer's route-bound
`metadata.content_digest`. Every family uses that same value.

For an AGY receipt, the wrapper proves `"$google_executable" --version` is at least 1.1.20 and parses
only literal tab-separated rows from `"$google_executable" models`; the exact first-column slug must
advertise `gemini-3.1-pro-high`. Run this provider-free wrapper preflight:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/antigravity_wrapper.py" \
  --prompt-file "$review_task_file" \
  --google-selector-receipt "$google_selector_receipt" \
  --expected-review-id "$review_id" \
  --cwd "$review_target_cwd" \
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
  --cwd "$review_target_cwd" \
  --preflight-only \
  > "$google_preflight_file"
```

The selected wrapper validates its provider-free capability surface and emits
`provider_started:false` plus the canonical route bindings. Every subsequent
`render` or `render-worktree` invocation includes:

```text
--google-selector-receipt "$google_selector_receipt" \
--google-preflight-receipt "$google_preflight_file"
```

After the selected preflight succeeds, render the family prompts. For an AGY
receipt, dispatch with:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/antigravity_wrapper.py" \
  --prompt-file "$review_prompt_file" \
  --google-selector-receipt "$google_selector_receipt" \
  --google-preflight-receipt "$google_preflight_file" \
  --cwd "$review_target_cwd" \
  --sandbox read-only \
  --model gemini-3.1-pro-high \
  --effort high \
  --timeout 600 \
  --pydantic verdict_schema:LegVerdict \
  --expected-review-id "$review_id" \
  --expected-family google \
  --expected-content-digest "$review_digest" \
  > "$google_result_file"
```

For a Gemini receipt, dispatch the same rendered Google prompt and bindings with:

```text
TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \
python3 "$toolkit_root/bin/gemini_wrapper.py" \
  --prompt-file "$review_prompt_file" \
  --google-selector-receipt "$google_selector_receipt" \
  --google-preflight-receipt "$google_preflight_file" \
  --cwd "$review_target_cwd" \
  --timeout 600 \
  --pydantic verdict_schema:LegVerdict \
  --expected-review-id "$review_id" \
  --expected-family google \
  --expected-content-digest "$review_digest" \
  > "$google_result_file"
```

The wrappers own the mechanical formal contracts:

- Gemini injects CLI Auto, requested native Plan Mode, and
  `bin/policies/gemini-formal-readonly.toml`; it removes competing route
  selectors without reading them and records runtime identity and effective
  approval mode as `unexposed`. TRIAD never adds `--skip-trust`.
- AGY validates the pinned version/model catalog, uses native Plan Mode and a
  review-bound JSON schema, applies the transient deny transaction, restores its
  original settings bytes, and consumes terminal `structured_output`. A tool
  attempt in a named denied namespace is also blocked by its matching deny entry.
  Preserve `AGY_NO_HEADLESS_AUTOAPPROVE=1` when the operator sets it.
- Both routes make one provider call, validate the terminal `LegVerdict` and
  review bindings locally, and treat invalid output or capacity failure as a
  terminal result. They do not retry capacity, call a schema-repair provider, or
  switch routes after selection.

Rendered prompts carry each route's exact native read/search vocabulary and
forbid candidate execution, writes, command tools, subagents, scratch tools, and
experiments. Static uncertainty belongs in `open_questions`. Provider telemetry
is diagnostic rather than verdict transport. Local verdict and review-binding
checks establish provisional validity; post-review integrity decides admission.

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

Give it the rendered Codex prompt and the same guarded target. Keep available
read/search tools inside the authorized boundary, save terminal JSON outside the
target, and observe it with a native `1,200,000`-millisecond observation wait.
If the child is still running when that observation returns, issue the same wait again.
Apply [convergence](convergence.md) to each observation and eventual
terminal result, then validate it with:

```text
python3 "$toolkit_root/bin/verdict_schema.py" validate \
  --result-file "$codex_result_file" \
  --expected-review-id "$review_id" \
  --expected-family codex \
  --expected-content-digest "$review_digest"
```

## Shared containment boundary

The no-edit contract is prompt-controlled unless runtime metadata proves a
stronger boundary. Admission relies on mutation detection rather than a sandbox
label: prepared-directory digest, canonical-worktree fingerprint, and selected
member comparisons cover their declared paths. Other ignored paths, paths
outside those scopes, and network egress are not mechanically observed. Because
legs read concurrently, final verification detects but cannot retroactively
prevent a mid-round mutation. Handle every mismatch through
[convergence](convergence.md).
