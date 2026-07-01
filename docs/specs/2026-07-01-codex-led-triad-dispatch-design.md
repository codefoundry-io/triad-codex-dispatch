# Codex-Led Triad Dispatch — Design Spec

**Date:** 2026-07-01 · **Status:** DRAFT (for owner review) · **Toolchain
verified:** codex-cli 0.142.4, claude 2.1.196

A separate repo that mirrors the Claude-Code-led `triad-dispatch` plugin with
**Codex as the leader/orchestrator**, for internal company distribution. This
spec consolidates: (a) Codex's own draft plan (`docs/references/codex-draft-plan.md`),
(b) live Tier-1 doc verification, and (c) an empirical feasibility spike that
proved the riskiest mechanism. It supersedes the draft plan where they differ.

---

## 1. Goal & context

The Claude-led `triad-dispatch` plugin is popular internally; many users want
Codex as the orchestrator. We build a **Codex-led mirror**:

- **Codex = leader.** It dispatches single-shot workers when it needs an answer
  from outside its own context.
- **Legs = claude (NEW), gemini, antigravity (agy).** The Claude family becomes a
  dispatched leg (a new `claude_wrapper.py` around `claude -p`), symmetric with
  the other legs. Gemini / agy leg wrappers are **reused** from the source repo.
- **Repair agents** are ported to Codex's world (Codex-dispatched named
  subagents), including a **new `claude-wrapper-repair`**.
- **Cross-family review** inverts: reviewers = claude leg + Google-family leg +
  Codex's own (fresh) perspective.

Decision (owner, this session): **separate repo** — the Claude plugin packaging
(`.claude-plugin/` + `/plugin install`) and Codex's distribution differ enough
that co-housing is not worth the complexity.

---

## 2. Verified constraints (evidence-backed)

### 2.1 Codex named-subagent repair mechanism — **VERIFIED by spike** ✅

The riskiest element (the whole repair loop depends on it). Spike on this
machine (codex-cli 0.142.4), evidence in `docs/references/spike-evidence-*`:

- A `codex --search exec` leader **spawned a personal-scope named agent**
  (`~/.codex/agents/spike-repair.toml`) **by name** (`collab: SpawnAgent` →
  "Spawn returned agent id … for the named `spike-repair` role"), **waited**
  (`collab: Wait`), and the subagent **did a web search** (`web_search_used:true`,
  correct fact) and **wrote a JSON result file** the leader read back.
- `[agents]` global config: `max_threads` (user has 12), `max_depth=1` (a direct
  child may spawn; deeper nesting blocked by default).
- **Named agent format:** `<scope>/<name>.toml` with `name`, `description`,
  `developer_instructions`, plus optional `sandbox_mode`, `model`,
  `model_reasoning_effort`, `mcp_servers`, `skills.config`. Scopes:
  `~/.codex/agents/` (personal), `.codex/agents/` (project).
- **Conclusion:** the repair loop is **Codex named subagents** (spawn → wait →
  read `<run_log>.repair.json`) — a clean mirror of Claude's
  `Agent(subagent_type, run_in_background)` + file-IO contract. Codex-family
  work in this repo uses Codex subagents, not a second Codex CLI process.
- **Caveat (open):** proven at **personal scope**. Open GitHub bugs
  ([#14579](https://github.com/openai/codex/issues/14579),
  [#26408](https://github.com/openai/codex/issues/26408),
  [#19399](https://github.com/openai/codex/issues/19399)) about **project-scope
  / plugin-shipped** named agents not being spawnable did NOT reproduce here, but
  we distribute via a plugin → **§11 Spike D** must confirm plugin-shipped agents
  register as spawnable named agents.

### 2.2 Codex skills — procedural runbooks, portable

Codex skills are `SKILL.md` folders the leader follows as step-by-step
instructions (same spirit as Claude skills), discovered from `.agents/skills`
(repo), `~/.agents/skills` (user), `/etc/codex/skills` (admin), + system.
Optional per-skill `agents/openai.yaml` controls `allow_implicit_invocation`,
interface, dependencies; explicit invocation via `$skill`.

> **Correction to the draft plan:** Codex **skills** (`.agents/skills/*/SKILL.md`
> + `agents/openai.yaml`) and Codex **named subagents** (`.codex/agents/*.toml`)
> are **two different systems**. The draft plan conflated them. This spec keeps
> them separate: dispatch/review logic = skills; repair workers = named agents.

### 2.3 Codex distribution — plugin + marketplace exists

`codex plugin {add,list,marketplace,remove}`; `codex plugin marketplace
{add,list,upgrade,remove}`; installed copies under `~/.codex/plugins/cache/…`;
features `plugins` + `plugin_sharing` are stable/on; admins can restrict sources
via `requirements.toml`.

> **Spike D result (2026-07-01):** the manifest path is
> `.codex-plugin/plugin.json` and the repo marketplace path is
> `.agents/plugins/marketplace.json`, confirmed against the current Codex manual,
> `codex plugin --help`, and a real local install. Plugin-shipped skills work
> through a plugin-root `skills/` package mirror. Plugin-shipped repair agent
> TOMLs are copied into the plugin cache, but a fresh `codex --search exec`
> leader could not spawn `claude-wrapper-repair` by name
> (`unknown agent_type 'claude-wrapper-repair'`). Therefore bootstrap installs
> `agents/*.toml` into `~/.codex/agents/` personal scope.

### 2.4 Claude leg (`claude -p`) — confirmed

Full spec in `docs/references/claude-leg-spec.md`. Key: `claude -p
--output-format json` (single JSON envelope, Gemini-style); `--json-schema`
structured output → `.structured_output`; **no `--sandbox` flag** — read-only =
`--permission-mode dontAsk --allowedTools "Read,Glob,Grep"`; web search opt-in
via `--allowedTools WebSearch,WebFetch`; `--effort {low,medium,high,xhigh,max}`;
model via aliases only; **classify from the JSON envelope**, not exit code
(claude has no documented exit-code taxonomy). `--search` on codex is TOP-LEVEL
(`codex --search exec …`), already handled correctly by the source wrapper.

---

## 3. Architecture overview

Three layers, same as the source toolkit — only the leader-side layer is
re-authored for Codex:

1. **Leg engine (`bin/`) — leader-agnostic, mostly reused.** Pure Python:
   spawn a vendor CLI single-shot, classify into the shared token set, emit a
   run-log JSON. Add a `claude_wrapper.py`; adapt `_common.py` for the claude
   envelope + a namespaced classifier path.
2. **Codex leader-side skills (`skills/`) — re-authored.** `SKILL.md` runbooks
   (Bash-invoke wrapper → grep classification → branch → on
   `unknown`/`extraction-error`/`timeout` spawn the repair **named subagent** →
   cleanup). One per leg + cross-family review.
3. **Codex repair named subagents (`.codex/agents/` or shipped) — re-authored.**
   TOML-defined named agents (per §2.1) that web-search + patch the classifier
   extension JSON + re-run with `--repair-mode`, writing a file-based response.

Shared classification token set (unchanged):
`ok | server-capacity | cli-subscription-cap | token-limit | oauth-env |
schema-rejected | timeout | extraction-error | unknown | …`. Exit codes reuse
`_common`'s scheme.

---

## 3a. Google-family leg = agy — gemini CLI deprecated (VERIFIED 2026-07-01)

Live verification (evidence: `docs/references/google-family-agy-readonly.md`):

- **gemini CLI individual tier is DEAD** — `gemini 0.46.0` auth returns
  `IneligibleTierError … migrate to the Antigravity suite`. So the **Google-family
  dispatch leg = agy** (`triad-antigravity-dispatch`); the gemini leg is deprecated
  for individual tier (keep only for a business / Vertex / API-key path).
- **Read-only heavy-file / consult dispatches use agy `--sandbox read-only`, NOT
  gemini plan mode.** agy is Go — no Node/V8 heap OOM (the crash that kills gemini
  plan mode on heavy files). Verified: a read-only write attempt is blocked and
  agy's settings restore byte-exactly (per-call deny transaction).
- **Read-only is ALWAYS per-call — never a global policy.** A global read-only
  policy would kill the leg's code-agent role. The same leg does write/code work
  under `--sandbox workspace-write`. Mirrors codex's per-call `--sandbox`.
- Pro model via agy `--model "Gemini 3.1 Pro (High)"` (no dated IDs in code).

---

## 4. Repository layout

```text
triad-codex-dispatch/
  bin/
    _common.py              # ADAPTED: namespaced classifier path + claude envelope handling
    _pty.py                 # reused verbatim
    _agy_settings.py        # reused verbatim
    codex_tasks.py          # reused IFF codex `--task` legs are kept (else drop)
    gemini_wrapper.py       # reused; DEPRECATED leg (gemini individual tier dead — §3a); non-default
    antigravity_wrapper.py  # reused — PRIMARY Google-family leg (agy); read-only via per-call --sandbox (§3a)
    claude_wrapper.py       # NEW  (claude -p single-shot; see references/claude-leg-spec.md)
    claude-daily-check.sh   # NEW  drift probe (mirror gemini/agy daily-check)
    gemini-daily-check.sh   # reused
    agy-daily-check.sh      # reused
  .agents/skills/           # Codex SKILL.md runbooks — MUST live here (VERIFIED §4a):
    triad-claude-dispatch/SKILL.md        # NEW
    triad-gemini-dispatch/SKILL.md        # ADAPTED (Codex leader)
    triad-antigravity-dispatch/SKILL.md   # ADAPTED (PRIMARY Google leg)
    triad-cross-family-review/SKILL.md    # ADAPTED/INVERTED (Codex is leader family)
    <name>/agents/openai.yaml             # per-skill metadata / invocation policy
  agents/                   # repo SOURCE for the repair named subagents; the
    claude-wrapper-repair.toml            #   bootstrap INSTALLS these to
    gemini-wrapper-repair.toml            #   ~/.codex/agents/ (personal scope — the
    agy-wrapper-repair.toml               #   spawnable scope verified in §2.1; project
                                          #   .codex/agents/ has open bug #26408)
  .codex-plugin/plugin.json # Codex plugin manifest (verified by Spike D)
  skills/                   # Plugin packaging mirror of .agents/skills/
  .agents/plugins/marketplace.json
  migration/
    COMPANY-SETUP.md / .ko.md             # install + update + egress + auth
    AGENTS.recommended.md                 # recommended Codex AGENTS.md
  scripts/bootstrap.sh                    # NEW: env/auth/PATH/writable-classifier checks
  tests/
    fixtures/fake_claude.py               # NEW fake CLI for hermetic wrapper tests
    test_claude_wrapper.py                # NEW
    test_classifier_extension.py          # reused/adapted
  docs/                     # this spec + references
```

`codex_wrapper.py` is **not** a dispatch leg here (Codex is the leader family).
Keep it only if a fresh-Codex-subagent reviewer or a codex `--task` path reuses
it; otherwise omit.

## 4a. Skill discovery — VERIFIED with real codex (2026-07-01, tmux)

Ran `codex` (v0.142.4) in the repo and drove it via tmux:

- Skills placed in **`.agents/skills/<name>/SKILL.md`** register as first-class
  skills — typing `$triad-claude` surfaced `triad-claude-dispatch [Skill]` with
  the SKILL.md `description`, and it appeared under the `/skills` list with the
  `.agents/skills/` scope. So the **SKILL.md format (name + description
  frontmatter) is correct**.
- The SAME files under a plain **`skills/`** dir do NOT register as skills (they
  show only as filesystem entries under `@`, not as `[Skill]`). So `.agents/skills/`
  is mandatory — NOT the Claude-plugin `skills/` layout.
- Workspace **trust** gates project-local loading: codex prompts "Do you trust
  this directory?" on first entry; skills load only after trusting. The install /
  onboarding docs must tell users to trust the workspace.

Consequence: skills live in `.agents/skills/` (this repo), repair named subagents
install to `~/.codex/agents/` (§4 + §2.1). The `skills/` path in earlier drafts
is superseded by this.

---

## 5. The claude leg (`claude_wrapper.py`)

A thin `_common.run_cli_with_retry("claude", …)` wrapper mirroring
`gemini_wrapper.py`. Default command shape, read-only/web-search policy, model &
effort mapping, JSON-envelope extraction, and the full classification table live
in **`docs/references/claude-leg-spec.md`**. Highlights:

- Instruction via argv (single-quoted heredoc). The wrapper passes the prompt as
  an **argv** (not stdin), so keep it short (argv has an OS `ARG_MAX` limit);
  large packets: reference the file PATH in the prompt and set `--cwd` so the
  read-only leg's Read tool opens it (the leg reads the file itself — the wrapper
  has no `--add-dir`).
- `--sandbox read-only` ⇒ `--permission-mode dontAsk --allowedTools "Read,Glob,Grep"`;
  `--search` ⇒ add `WebSearch,WebFetch`. `bypassPermissions` banned at argparse.
- `--reasoning` ⇒ claude `--effort`; `--model` alias passthrough (no dated IDs in
  code); `--pydantic` ⇒ `--json-schema` → `.structured_output` → local validate.
- Classification maps Claude signals (`is_error`, `api_error_status`, `subtype`,
  error-category enum) onto the shared token set.

---

## 6. Codex leader-side skills

Each dispatch skill keeps the source toolkit's operational pattern, re-expressed
as a Codex `SKILL.md`:

1. Invoke the wrapper **via Bash only** (stderr `[wrapper] <cli> <class> …`
   summary + `run-log:` path surface only through Bash).
2. Read the **last** `[wrapper]` line; extract classification.
3. Branch on the fixed token set.
4. On `unknown` / `extraction-error` / `timeout` → **spawn the repair named
   subagent** (SpawnAgent by name), continue foreground work, then Wait and read
   `<run_log>.repair.json`.
5. Clean up run-log + repair JSON after completion.

`agents/openai.yaml`: `allow_implicit_invocation: true` for the dispatch skills +
cross-family review; consider `false` for any low-level helper.

---

## 7. Repair-agent design (Codex named subagents — verified path)

Per §2.1 the mechanism is proven. Each repair agent is a named TOML subagent:

- **Definition:** `<name>.toml` with `name`, `description`,
  `developer_instructions` (the per-attempt workflow: extract literal error →
  date-anchored web search → patch the classifier extension JSON → validate JSON
  → re-run with `--repair-mode`; 3-attempt ceiling; file-based response),
  `sandbox_mode = "workspace-write"` scoped to the run-log dir + the classifier
  JSON only, `model_reasoning_effort = "high"`.
- **Web search:** enabled by the leader's `codex --search exec …` (propagates to
  the subagent — verified). Confirm the shipped-agent path re-enables it.
- **Dispatch (from the skill):** SpawnAgent by name with a JSON-shaped task
  (`run_log_path`, `output_path`, `output_schema`) → Wait → read `output_path`.
- **Scope guard (HARD):** only write `<run_log>.repair.json` and the classifier
  extension JSON; never touch engine source / retry policy / auth; escalate
  otherwise (carried over from the source repair agents).

---

## 8. Self-improving classifier extension JSON

Keep the two-layer merge design. **Namespace the path** to
`~/.config/triad-codex-dispatch/classifier-patches.json` (isolated from the
Claude-led tool so one repo's repair agent can't change the other's behavior);
keep the `TRIAD_CLASSIFIER_EXTENSION` override. Ship a small **import** helper to
copy existing `gemini`/`antigravity` patches from the old path. Add a top-level
`claude` key for the new leg. **Owner decision:** isolate-plus-import (recommended)
vs share the old path for cross-tool learning.

---

## 9. Cross-family review (adapted)

Reviewers, all independent:

- **claude** — `claude_wrapper.py` read-only leg.
- **Google family** — agy (preferred) or gemini leg.
- **codex** — the leader's own family. To preserve independence when Codex is the
  orchestrator, produce the Codex verdict from a **fresh Codex subagent** spawned
  with the same packet, saved before reading the other legs' outputs; the leader
  only consolidates. Same-thread self-review is not accepted for merge-gate
  review.

Large reviews use the existing file-IPC rule: one packet under
`_runs/reviews/<id>/packet.md`; each leg reads only that file by referencing its
PATH in the (short, argv) prompt with `--cwd <repo-root>` — the read-only leg
Reads it. Never inline the packet content into the prompt (argv `ARG_MAX`).

---

## 10. Distribution & onboarding

Ship as a Codex plugin + marketplace (§2.3), with the Spike D fallback:

1. `codex plugin marketplace add <internal repo or local root>`
2. `codex plugin marketplace upgrade`
3. install via `/plugins` or preconfigured marketplace policy (locked fleets:
   publish repo marketplace metadata + admin `requirements.toml` allowing only
   the internal source).
4. `scripts/bootstrap.sh --check` verifies `codex`/`claude`/`gemini`/`agy`,
   Python, `jq`, auth, PATH for `bin/`, and a writable classifier path. If plugin
   install does not expose `bin/` on PATH, bootstrap installs launchers (no
   symlinks in artifacts — packaging/launcher per user rule). Because
   plugin-shipped named agents are not spawnable, bootstrap also copies
   `agents/*.toml` into `~/.codex/agents/`.

---

## 11. Phased build order (riskiest-spike-first)

- **Spike D (DONE — 2026-07-01):** packaged the repo as a Codex plugin, installed
  it from a local marketplace, and confirmed plugin-shipped named repair agents
  are **not** spawnable by name. Fallback selected: bootstrap installs repair
  agents into `~/.codex/agents/` (personal scope — proven), decoupled from the
  plugin's skill package.
- **Spike E:** claude leg edges — stdin-vs-argv instruction semantics,
  `--json-schema` validation failure, large-file references, auth/permission
  denials mapping.
1. Port `_common.py` (namespaced classifier path + claude extraction).
2. Implement `claude_wrapper.py` + fake-CLI hermetic tests.
3. Adapt gemini/agy dispatch skills to Codex `SKILL.md`.
4. Author the repair named subagents (+ new `claude-wrapper-repair`).
5. Adapt cross-family review (fresh-Codex reviewer).
6. Package plugin/marketplace + bootstrap + migration docs (per Spike D result).
7. Daily checks + end-to-end fake-vendor tests, then real-vendor smoke tests.

---

## 12. Open items / no clean Codex equivalent

- **Plugin-shipped named agents** — Spike D says no; keep personal-scope
  bootstrap fallback until Codex supports plugin-shipped named agent discovery.
- **Codex-as-leader review independence** — not naturally independent; solved via
  a fresh Codex subagent reviewer (§9).
- **No `run_in_background`-identical contract** — Codex uses SpawnAgent + Wait;
  the leader can still do foreground work between spawn and wait (acceptable).

---

## 13. Owner decisions (needed before/within implementation)

1. Classifier path: isolate-plus-import (recommended) vs share old path.
2. Cross-family Codex reviewer: fresh subagent (recommended) vs same-thread.
3. claude `--reasoning` enum: mirror codex `{low..xhigh}` vs allow claude `max`.
4. claude read-only allowlist default set + default model (unset vs alias).
5. Keep or drop `codex_wrapper.py` / codex `--task` legs in the Codex-led repo.
6. Distribution fallback if Spike D fails: **decided by spike** — bootstrap into
   `~/.codex/agents`.

---

## 14. Sources & evidence

- Draft plan: `docs/references/codex-draft-plan.md` (Codex xhigh + web search).
- claude leg: `docs/references/claude-leg-spec.md`, `claude-headless-reference.md`.
- Spike evidence: `docs/references/spike-evidence-leader.log`,
  `spike-evidence-result.json`.
- Official: developers.openai.com/codex/{subagents,config-reference},
  code.claude.com/docs/en/{headless,cli-reference,model-config,env-vars}.
- Tier-2: installed `codex --help` / `codex features list` / `claude --help`.
