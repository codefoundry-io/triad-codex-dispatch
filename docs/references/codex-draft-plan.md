# Codex-Led Triad Dispatch Implementation Plan

I read the existing `bin/`, `skills/`, `agents/`, `migration/`, READMEs, and plugin metadata. The current engine is already mostly leader-agnostic; the main porting work is Codex-side orchestration plus a new `claude_wrapper.py`.

## Verified Constraints

Codex skills are `SKILL.md` folders with YAML frontmatter and procedural instructions for Codex to follow, not deterministic function calls. They can still be written as step-by-step runbooks. Codex discovers skills from repo `.agents/skills`, user `~/.agents/skills`, admin `/etc/codex/skills`, and system locations; plugin distribution is recommended for reusable bundles. Optional `agents/openai.yaml` controls UI metadata, invocation policy, dependencies, and `allow_implicit_invocation`; explicit `$skill` invocation still works when implicit invocation is disabled.

Codex has real multi-agent support: `features.multi_agent` enables `spawn_agent`, `send_input`, `resume_agent`, `wait_agent`, and `close_agent` by default. Named agent roles are configured through `agents.<name>.config_file`, `description`, and nicknames. But Codex docs do not describe a Claude-compatible `Agent(subagent_type=..., run_in_background=true)` contract. They describe explicit parallel subagent workflows and say Codex should only spawn subagents when explicitly instructed.

Codex distribution should use plugins and marketplaces. Plugins bundle skills, apps, and MCP servers; marketplaces can be repo-scoped or personal; CLI marketplace add/upgrade/list/remove exists; installed plugin copies live under `~/.codex/plugins/cache/...`. Admins can restrict marketplace sources through `requirements.toml`.

Claude Code headless mode is current and usable: `claude -p` runs non-interactively; `--output-format` supports `text`, `json`, `stream-json`; JSON output includes `result`, `session_id`, metadata, and optional `structured_output`; `--json-schema` is now documented for validated JSON output. `claude -p` reads stdin, but piped stdin is capped at 10 MB; larger packets should be written to files and referenced by path. Model, session persistence, permission mode, max turns, and schema flags are documented. There is no general documented exit-code taxonomy for all `claude -p` failures; the wrapper must treat vendor exit code as opaque and classify stderr/stdout plus JSON error events.

## Repository Layout

```text
triad-codex-dispatch/
  .codex-plugin/plugin.json              # new Codex plugin manifest
  .agents/plugins/marketplace.json       # new repo marketplace entry for local/team install
  bin/
    _common.py                           # adapted from existing: namespace + Claude schema handling
    _pty.py                              # reused verbatim
    _agy_settings.py                     # reused verbatim
    gemini_wrapper.py                    # reused verbatim initially
    antigravity_wrapper.py               # reused verbatim initially
    claude_wrapper.py                    # new
  skills/
    triad-claude-dispatch/SKILL.md       # new Codex runbook
    triad-gemini-dispatch/SKILL.md       # adapted from Claude skill
    triad-antigravity-dispatch/SKILL.md  # adapted from Claude skill
    triad-cross-family-review/SKILL.md   # adapted/inverted for Codex leader
    */agents/openai.yaml                 # new metadata/invocation policy
  codex/
    config.snippet.toml                  # named repair-agent config snippets
    agents/
      claude-wrapper-repair.config.toml  # new Codex agent role
      gemini-wrapper-repair.config.toml  # adapted
      agy-wrapper-repair.config.toml     # adapted
    repair-prompts/*.md                  # repair-agent instructions
  migration/
    COMPANY-SETUP.md
    COMPANY-SETUP.ko.md
    AGENTS.recommended.md
  tests/
    fixtures/fake_claude.py
    test_claude_wrapper.py
    test_classifier_path.py
    test_docs_constraints.py
    test_log_cleanup.py
```

Do not ship `codex_wrapper.py` as a dispatch leg in the main path. Codex is now
the leader family, and this repo should not shell out to a second Codex CLI
process for dispatch or repair.

## Claude Leg

`claude_wrapper.py` should be a thin `_common.run_cli_with_retry("claude", ...)` wrapper, mirroring `gemini_wrapper.py`. Existing `_common.py` already has `CLAUDE_VENDOR_EXIT_MAP` and `extract_claude_answer`, but it must be updated for current `structured_output`.

Default command shape:

```text
claude -p "<short instruction>" --output-format json --no-session-persistence
```

Feed the real prompt over stdin to avoid argv limits; the short instruction tells Claude to follow stdin exactly. This must be spiked because Claude treats piped content as additional context, not necessarily the only instruction.

Flags:
- `--model` passthrough to Claude `--model`.
- `--pydantic module:Class`: generate JSON Schema, pass compact JSON via `--json-schema`, parse `.structured_output`, then still Pydantic-validate locally.
- `--timeout`: wrapper outer timeout only; Claude has `--max-turns`, not a general print timeout.
- `--bare`: opt-in only for CI, because Anthropic docs say bare skips OAuth/keychain and requires API key/settings auth.
- `--sandbox read-only|workspace-write`: map to Claude permission/tool policy. V1 should be read-only by default; workspace-write requires isolated `--cwd`.

Classification mapping:
- `timeout`: wrapper kill.
- `token-limit`: stdin cap, max output tokens, context/input too large.
- `oauth-env`: auth failed, org not allowed, login/token errors.
- `cli-subscription-cap`: billing/quota/rate-limit subscription failures.
- `server-capacity`: overloaded/server retry exhaustion.
- `schema-fail`: post-hoc pydantic validation failure or Claude structured-output
  retry exhaustion.
- `schema-rejected`: submit-time schema refusal.
- `task-blocked`: permission denial / tool blocked with no usable result.
- `fanout-spawn-error`: Codex leader could not spawn a required reviewer/repair subagent.
- `config-conflict`: local config/settings lock contention or conflicting runtime
  config. Lock-shaped conflicts may wait briefly and re-dispatch once; repeated
  or parse/config-shaped conflicts are surfaced. Never route to repair.
- `extraction-error`: rc 0 but no `.result`/`.structured_output`.
- `unknown`: nonzero rc with no known pattern.

Run-log schema: `cli`, `wrapper_cmd`, `vendor_cmd`, `prompt_head`, `prompt_len`,
`prompt`, `exit_code`, `vendor_exit_code`, `classification`, `mode`, `elapsed_s`,
`stderr`, `stdout`, `final_answer`, `extraction_error`, `validation_error`.

## Codex Leader Artifacts

Each dispatch skill keeps the existing operational pattern:
- invoke the absolute wrapper launcher directly, without shell wrapping;
- read the last `[wrapper] <cli> <classification> ...` line;
- branch on the fixed token set;
- extract `run-log: <path>`;
- route only `unknown`, `extraction-error`, and `timeout` to repair;
- clean up run-log and repair JSON after completion.

The skills should be Codex `SKILL.md` files with imperative steps and optional `agents/openai.yaml`. Set `allow_implicit_invocation: true` for the three dispatch skills and cross-family review; consider `false` for any low-level repair helper skill.

## Repair-Agent Story

Preferred design: Codex named subagents.

Add config snippets declaring `claude-wrapper-repair`, `gemini-wrapper-repair`, and `agy-wrapper-repair` with high reasoning, live web search, and a permission profile that can write only to:
- the classifier config directory (`~/.config/triad-codex-dispatch/` by default);
- the bounded `bin/_logs/<cli>/` IPC area for run logs, `.repair.json`, and temporary repair prompt files.

The skill asks Codex to spawn the named repair agent, continue foreground work, then `wait_agent` and read `<run_log>.repair.json`.

If the named-subagent spike fails, do not add a same-family CLI fallback in this
repo. Mark repair unavailable for that route and surface the failure; inline
leader repair is a last-resort manual diagnosis, not an automated dispatch path.

## Classifier Extension

Keep the JSON schema exactly as-is. Add a `claude` top-level key. Default to a new namespace:

```text
~/.config/triad-codex-dispatch/classifier-patches.json
```

Keep `TRIAD_CLASSIFIER_EXTENSION` override. A migration script that imports existing `gemini` and `antigravity` patches from `~/.config/triad-dispatch/classifier-patches.json` is future work unless the owner explicitly requests it.

Owner decision: share the old path for cross-tool learning, or isolate paths to avoid one repo’s repair agent changing the other repo’s behavior. I recommend isolation plus import.

## Cross-Family Review

New reviewers:
- Claude: `claude_wrapper.py` in read-only mode.
- Google family: `antigravity_wrapper.py` preferred, `gemini_wrapper.py` fallback.
- Codex family: Codex leader’s own perspective.

To preserve independence, the Codex verdict must be produced by a fresh Codex
subagent before reading Claude/Google outputs, saved to a review file, and not
revised until consolidation. Same-thread self-review is not accepted for
merge-gate review.

Large reviews should keep the current file-IPC rule: preassemble one repo-relative packet under `_runs/reviews/<id>/packet.md`; vendor reviewers read only that file. Claude stdin is capped at 10 MB, so large Claude reviews must use file path references, not giant stdin.

## Distribution

Ship as a Codex plugin with `.codex-plugin/plugin.json` and a marketplace entry. For teams:
1. `codex plugin marketplace add <internal repo or local root>`
2. `codex plugin marketplace upgrade`
3. install from `/plugins` or preconfigure marketplace policy.
4. run `scripts/bootstrap.sh --check` to verify `codex`, `claude`, `gemini`, `agy`, Python, `jq`, auth, PATH, and writable classifier path.

For locked-down fleets, publish repo marketplace metadata and admin
`requirements.toml` allowing only the internal marketplace source. If plugin
install does not expose `bin/` on PATH, bootstrap installs small launcher files;
do not ship symlinks as artifacts.

## Phased Build Order

1. Riskiest spike first: prove Codex can spawn a named repair subagent that runs concurrently, uses web search, writes `<run_log>.repair.json`, and patches classifier JSON.
2. Spike `claude -p`: JSON envelope, schema output, stdin semantics, nonzero failures, auth modes, permission denials, large-file references.
3. Port `_common.py` namespace and Claude extraction.
4. Implement `claude_wrapper.py` and fake-CLI tests.
5. Adapt Gemini/Agy skills to Codex skill format.
6. Add Codex repair-agent configs using named subagents only.
7. Adapt cross-family review.
8. Package plugin/marketplace/bootstrap docs.
9. Run daily checks and end-to-end fake vendor tests before real vendor smoke tests.

## No Clean Codex Equivalent

Codex has subagent workflows and spawn/wait tools; the named, background,
file-writing repair loop must be proven in the target Codex runtime. If that
mechanism is unavailable, the route is unavailable rather than replaced with a
same-family CLI subprocess.

Plugin distribution exists in Codex, but it is not a direct Claude `/plugin install` mirror. It uses Codex marketplaces, cache installs, and restart/upgrade flows.

Codex's own review perspective is not naturally independent when Codex is the
orchestrator. Use a fresh Codex subagent for strict independence.
