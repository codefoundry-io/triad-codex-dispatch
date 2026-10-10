# CLI selector precedence investigation

Status: PROPOSAL WITHDRAWN by the owner on2026-10-09. Historical evidence only.
Do not implement the proposed environment warning, add selector modification or
effective-effort checks, or continue priority spikes from this record. The owner
withdrew the preceding preserve-and-warn request and directed that existing
effort behavior and user settings remain. All proposal, prerequisite and next-step
wording below is superseded; factual measurements retain their stated limits.
Shared decision: D-SELECTOR-PROPOSAL-WITHDRAWN-20261009. The independent broader
U2c candidate is still unadmitted; this withdrawal does not certify or ship it.

## Evidence and limits

Claude Code 2.1.289, isolated HOME/CLAUDE_CONFIG_DIR, synthetic environment,
`--bare --print`, no tools, no MCP servers, no persistent session:

| Input | Observed result | Strength |
| --- | --- | --- |
| ANTHROPIC_MODEL=haiku, no model flag | Current model: Haiku 4.5 | Local selection report |
| ANTHROPIC_MODEL=haiku, --model opus | Current model: Opus 5.5 | Local selection report |
| ANTHROPIC_DEFAULT_OPUS_MODEL=claude-haiku-4-5, --model opus | Current model: Haiku 4.5 | Local alias-resolution report |
| --effort xhigh, no effort environment variable | Request output_config.effort=xhigh | Actual CLI request to a loopback stub |
| CLAUDE_CODE_EFFORT_LEVEL=low, --effort xhigh | Request output_config.effort=low | Actual CLI request to a loopback stub |
| CLAUDE_CODE_EFFORT_LEVEL=xhigh, --effort low | Request output_config.effort=xhigh | Actual CLI request to a loopback stub |

The `/model` display followed the effort flag even when the generated request
followed the environment variable. It is insufficient proof of effective effort.
The loopback stub used a synthetic key, captured only path/model/output_config/
thinking, and deliberately returned HTTP400 LOCAL_PRECEDENCE_CAPTURE_ONLY.
All three children ended with exit1 as expected; no vendor inference or real
credential was used. This proves request construction on this isolated API test
path, not a live subscription response. No production configuration was changed.

Official Claude documentation independently states --model overrides
ANTHROPIC_MODEL, while CLAUDE_CODE_EFFORT_LEVEL overrides --effort and /effort:
https://code.claude.com/docs/en/env-vars#precedence
Alias pinning is separately documented:
https://code.claude.com/docs/en/model-config#model-aliases

Gemini CLI 0.63.0: extracted and executed the exact four model-resolution
statements from the previously downloaded official npm bundle, lines8455ff.
The three cases selected flag over environment/settings, environment over
settings, and settings when both were absent. Bundle SHA256:
`a64b06d8a06673cfae0134558e162e5b015d088a3751639c7d6dc4a88c67c1f8`.
This is isolated vendor-code execution, not full startup or inference. Official
documentation agrees: https://geminicli.com/docs/cli/model-routing/#model-selection-precedence
No Gemini effort-precedence claim was tested.

AGY 1.3.2: official headless docs expose --model and --effort but do not settle
environment conflict precedence. Three isolated `-p /model` attempts (control,
explicit flags, flags with synthetic GEMINI_MODEL) all stopped at authentication
with exit1. Therefore AGY priority remains UNMEASURED; do not infer equivalence
with Gemini CLI. https://www.agy.dev/docs/cli/headless/#select-a-model-effort-or-agent

## Disposition

- The initial U2c tests establish agreement-list parity and name-filter behavior;
  they do not establish that every list entry is needed to enforce explicit pins.
- Direct model defaults, alias remapping, effective effort and authentication
  routing require separate justification. CLI model priority does not settle
  authentication/endpoint hygiene or omitted-option behavior.
- Current R-NOCOST lists ANTHROPIC_MODEL and GEMINI_MODEL; it does not list
  CLAUDE_CODE_EFFORT_LEVEL or ANTHROPIC_DEFAULT_OPUS_MODEL. Do not silently add
  names, delete existing names, or claim the current list guarantees exact pins.
- Keep existing auth handling and host-native mechanisms unchanged. Preserve
  the applied U2c candidate and its baseline without admitting or deploying it.
- Record these findings in the shared spec, obtain the other host's diagnosis,
  and resolve required design decisions before a normative change and dependent
  implementation. Assess the current `/model` effort check against this evidence.
  No extra agent definition is required by these results.

## Reproducible local artifacts

Workspace `_runs/infra/20261009-spec-to-code/u2c/`:
`precedence-spike.py`, `precedence/claude.json`,
`precedence-request-spike.py`, `precedence-request/claude.json`,
`precedence-request/gemini-resolution.mjs`, `precedence-request/gemini.json`,
`agy-precedence/result.json`. All child processes and the loopback servers ended.
Provider execution used the required `/bin/zsh -lic` escalation path. These
artifacts contain synthetic selectors, not captured ambient credentials.

## Owner direction: preserve selectors and report possible override

Owner, 2026-10-09: "환경 변수는 사용자가 일부러 한 설정일수 있으니 안건드리는게
맞을 것 같은데 대신 기계적으로 해당 환경 변수 때문에 원하는 effort가 적용안될수
있다고 출력하도록 해". Preserve model/effort selection variables in the child
as well as in the parent. A deterministic notice names the relevant variable
without printing its value, removing it, overriding it, or claiming an actual
runtime mismatch solely from its presence. This is the requested direction;
shared normative rules/cases and implementation are still pending.

Bounded inventory: nine direct selector candidates, not an exhaustive inventory
of all vendor environment variables or thinking/capability controls:

| Name | Evidence and notice eligibility |
| --- | --- |
| CLAUDE_CODE_EFFORT_LEVEL | Only direct effort override in this inventory; official precedence and loopback request proof. When effort is requested and the variable is present, a value-free possible-override notice is appropriate. |
| ANTHROPIC_DEFAULT_OPUS_MODEL | Alias mapping; observed with opus. Notice only for a matching alias request. |
| ANTHROPIC_DEFAULT_SONNET_MODEL | Official alias mapping; not locally spiked. Matching alias only. |
| ANTHROPIC_DEFAULT_HAIKU_MODEL | Official alias mapping; not locally spiked. Matching alias only. |
| ANTHROPIC_DEFAULT_FABLE_MODEL | Official alias mapping; not locally spiked. Matching alias only. |
| ANTHROPIC_MODEL | Explicit model flag wins; do not warn that this defeats a supplied flag. |
| ANTHROPIC_DEFAULT_MODEL | Official new-session default, lower priority than explicit model selection; not locally spiked. |
| GEMINI_MODEL | Explicit model flag wins in 0.63; no implication for AGY. |
| ANTHROPIC_SMALL_FAST_MODEL | Existing shared-list entry, absent from the current official env reference. Legacy candidate only; active support/impact unverified, no automatic warning yet. |

Eight have current official documentation; the ninth is an existing-list item
whose present behavior is unverified. Current shared removal list contains only
three of these: ANTHROPIC_MODEL, GEMINI_MODEL, ANTHROPIC_SMALL_FAST_MODEL. None of
the nine was discovered by dumping or reading the user's actual environment.
Source: https://code.claude.com/docs/en/env-vars and the Gemini source above.
No AGY-specific selection environment variable is confirmed by this research.

Proposed message for an explicit effort request:
`Warning: CLAUDE_CODE_EFFORT_LEVEL is set; the requested --effort may not take effect. Your environment setting is preserved.`

Emit a deterministic notice on the diagnostic stream once per dispatch, without
an LLM audit, model inference or an environment-value dump. Presence alone does
not cause a refusal. Preserve independently observed identity mismatch handling;
the shared update must distinguish requested effort from verified effective
effort, because /model display is insufficient evidence. Do not expand this
direction into API-key/endpoint preservation or host-native changes.

AGY clarification: the probe deliberately used fresh isolated HOME directories
without the user's login. All three cases stopped with authentication required.
This is a limitation of that probe, not evidence that the user's AGY login or
normal reviews are broken, and not an observed model/effort precedence defect.

## Corrected live verification method

Owner rejected substituting an isolated HOME or mock endpoint for the actual
execution environment. Earlier probes remain limited evidence, not proof of
normal authenticated operation. A separate /model process cannot attest the
effective effort of a subsequent review process.

The replacement probe uses a fresh PTY login shell for each case and the real
inherited HOME, config pointers and login state. It backs up only
CLAUDE_CODE_EFFORT_LEVEL in memory (including whether it was unset), changes it
for the test child, then restores and verifies it in finally. Original values
and the full inherited environment are not logged. No shell profile or global
Claude settings are edited.

A command-line --settings adds a temporary Stop hook. After a real one-turn
request, the hook records only effort.level, CLAUDE_EFFORT, CLAUDE_PID, hook event
and session ID. The parent compares that PID with the spawned Claude PID and the
session ID with the final JSON result. Missing fields are unverified, not filled
from the requested arguments. The hook is invocation-scoped and ends with the
process; this is diagnostic evidence, not a new permanent production audit.

Official source: https://code.claude.com/docs/en/hooks#common-input-fields
This measures the running CLI's reported effective effort, not server-side
internal reasoning. It directly exercises the real CLI; the TRIAD wrapper and
its environment builder are not exercised by this diagnostic invocation.

Live results, Claude2.1.289, inherited real login/settings, modelUsage reports
claude-opus-5-5 in all three cases:

| Test environment effort | CLI effort | Stop effort.level / CLAUDE_EFFORT | Claude PID | Exit |
| --- | --- | --- | --- | --- |
| unset | xhigh | xhigh / xhigh | 68370 | 0 |
| low | xhigh | low / low | 71058 | 0 |
| xhigh | low | xhigh / xhigh | 74622 | 0 |

Each completed one real turn, answered OK, and matched both hook PID and session
ID to the child/result. All selectors restored, all exec sessions reaped, no
global hook installed. Evidence: workspace
`_runs/infra/20261009-spec-to-code/u2c/live-effort/{baseline,env-low,env-xhigh}/result.json`
and each adjacent hook.jsonl; scripts live-effort-probe.py/live-effort-hook.py.
This replaces the earlier isolated evidence as the basis for actual CLI effort
precedence. It does not claim the pending wrapper warning has been implemented.

## AGY live correction

Owner correction: the Pro-high/low case below is INVALID AS AN EFFORT-PRECEDENCE
EXPERIMENT. Model-specific supported effort variants were not established before
the probe. An unsupported or explicitly conflicting combination cannot answer
whether an environment setting overrides a supported CLI effort. Retain the
raw observation, but exclude it from precedence conclusions and warning design.
Do not generalize the failure to AGY models or infer Pro's complete support set.

AGY1.3.2, fresh PTY login shell per case, real inherited HOME/config/login,
direct CLI with --mode plan, --output-format stream-json, model
gemini-3.1-pro-high. Only GEMINI_MODEL was backed up in memory, changed for the
case and restored. No global config or profile edits and no mock endpoint.

| GEMINI_MODEL | --effort | Result |
| --- | --- | --- |
| unset | high | Exit0, SUCCESS, one turn, OK |
| gemini-3.8-flash-medium | high | Exit0, SUCCESS, one turn, OK |
| unset | low | Exit1, ERROR, zero turns: explicit model/effort conflict |

Both successful executions emitted init.model=gemini-3.1-pro-high in their own
stream and logged `Propagating selected model override to backend:
label="Gemini 3.1 Pro (High)"` in the invocation's dedicated --log-file output.
No separate effective-effort field was exposed in stream JSON. Thinking-token
counts are not an effort-setting measurement and are not used as one.

The conflicting case returned the measured vendor error:
`invalid model selection (--model "gemini-3.1-pro-high" --effort "low"): --model gemini-3.1-pro-high conflicts with --effort=low`.
This records rejection of that input only; the test was not designed to isolate
effort precedence. GEMINI_MODEL did not change
the explicit selection in the tested case; this does not distinguish a lower
priority from AGY ignoring that Gemini-CLI variable entirely. No AGY-specific
effort override environment variable has been established by this investigation.

The earlier isolated-HOME authentication failure does not describe the actual
login environment: these real high runs succeeded. Artifacts under workspace
`_runs/infra/20261009-spec-to-code/u2c/live-agy/{baseline,env-model,effort-low}/`:
result.json, stdout.jsonl, stderr.txt and native.log. Inspect only the relevant
selection lines for this diagnostic; do not add routine provider-log audits.
All children ended, sessions were reaped and selector restoration passed. This
was direct CLI diagnostics, not full TRIAD wrapper conformance or a native-leg
change. The default primary agent was used for a no-tools one-turn response.

Official CLI changelog describes --effort as selecting a model's reasoning-effort
variant and the gauge for models exposing multiple variants. This supports
checking model-specific capability first, not treating every CLI-advertised
level as supported by every model:
https://www.antigravity.google/changelog?tab=cli
No new inference was run for this correction. A proposed read-only /effort
inspection was rejected before process creation by automatic approval review
as another live provider probe; it was not retried. The complete Pro variant
matrix is not established here. No AGY effort-environment override is confirmed,
so there is no basis for adding an AGY effort warning from these experiments.

## Existing Flash evidence recovered before further experiments

The owner asked specifically about Gemini3.8 Flash. AGY's official headless
documentation explicitly lists both gemini-3.8-flash-high and
gemini-3.8-flash-medium, with the corresponding High/Medium labels and an example
dispatch of the Medium slug. Thus effort variants for this family are documented:
https://www.agy.dev/docs/cli/headless/#select-a-model-effort-or-agent
Do not misstate the absence of an AGY effort environment variable as absence of
model effort support. Those are different questions.

Existing repository docs/installation.md:179 already distinguishes the native
Gemini CLI ID gemini-3.8-flash from AGY's gemini-3.8-flash-high. Its subsequent
thinkingConfig.thinkingLevel=HIGH guidance is native Gemini CLI evidence pinned
to0.61.0, explicitly awaiting0.63.0 settings verification. It is not an AGY
--effort compatibility table. The shared handoff links the same prior document.
The investigation should have consulted this existing evidence before designing
the Pro-high/low test.

At locally inspected shared595ef35, R-ROSTER/R-MODEL define model/effort as
user data passed unchanged, validate adapter option vocabulary, and forbid a
model-catalog admission gate. They do not supply a complete model-specific
AGY effort matrix or establish an effort-override environment variable. Do not
add such a runtime gate while improving investigation guidance.

Research rule: establish the exact CLI/auth route, accepted model form and
documented compatible effort choices before constructing a conflict probe.
High and Medium variants are confirmed by the official page above; the page
does not establish every possible level or every bare-family alias spelling.
An explicit -high slug plus low tests inconsistent input, not precedence.
Changing a supported effort can test selection, but testing ENVIRONMENT priority
additionally requires an evidenced environment variable that affects that CLI.
No further CLI execution or inference was performed for this document search.
