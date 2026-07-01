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
  `Agent(subagent_type, run_in_background)` + file-IO contract. The
  nested-`codex exec` fallback is NOT needed for the core mechanism.
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

> **Unverified (→ §11 Spike D):** the exact Codex **plugin manifest** path/format
> and whether a plugin can bundle skills **and** named agents **and** the `bin/`
> wrappers so all three deploy together. The draft plan's `.codex-plugin/plugin.json`
> + `.agents/plugins/marketplace.json` are guesses; confirm against live docs +
> a real `codex plugin marketplace add` of this repo before committing to them.

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

## 4. Repository layout

```text
triad-codex-dispatch/
  bin/
    _common.py              # ADAPTED: namespaced classifier path + claude envelope handling
    _pty.py                 # reused verbatim
    _agy_settings.py        # reused verbatim
    codex_tasks.py          # reused IFF codex `--task` legs are kept (else drop)
    gemini_wrapper.py       # reused verbatim
    antigravity_wrapper.py  # reused verbatim
    claude_wrapper.py       # NEW  (claude -p single-shot; see references/claude-leg-spec.md)
    claude-daily-check.sh   # NEW  drift probe (mirror gemini/agy daily-check)
    gemini-daily-check.sh   # reused
    agy-daily-check.sh      # reused
  skills/                   # Codex SKILL.md runbooks (.agents/skills discovery)
    triad-claude-dispatch/SKILL.md        # NEW
    triad-gemini-dispatch/SKILL.md        # ADAPTED (Codex leader)
    triad-antigravity-dispatch/SKILL.md   # ADAPTED
    triad-cross-family-review/SKILL.md    # ADAPTED/INVERTED (Codex is leader family)
    <name>/agents/openai.yaml             # per-skill metadata / invocation policy
  agents/                   # Codex named subagents (.codex/agents/*.toml at install)
    claude-wrapper-repair.toml            # NEW
    gemini-wrapper-repair.toml            # ADAPTED
    agy-wrapper-repair.toml               # ADAPTED
    repair-prompts/*.md                   # developer_instructions bodies (per-attempt workflow)
  <codex-plugin-manifest>   # TBD — exact path/format per §11 Spike D
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

---

## 5. The claude leg (`claude_wrapper.py`)

A thin `_common.run_cli_with_retry("claude", …)` wrapper mirroring
`gemini_wrapper.py`. Default command shape, read-only/web-search policy, model &
effort mapping, JSON-envelope extraction, and the full classification table live
in **`docs/references/claude-leg-spec.md`**. Highlights:

- Instruction via argv (single-quoted heredoc); large packets via file-IPC
  (`--add-dir` + path reference), because piped stdin is capped at 10 MB and is
  treated as *context*.
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
  orchestrator, produce the Codex verdict from a **fresh Codex subagent** (or
  nested `codex exec`) with the same packet, saved before reading the other
  legs' outputs; the leader only consolidates. **Owner decision:** fresh
  same-family context (recommended) vs same-thread self-review.

Large reviews use the existing file-IPC rule: one packet under
`_runs/reviews/<id>/packet.md`; each leg reads only that file (claude stdin 10 MB
cap → path reference, not giant stdin).

---

## 10. Distribution & onboarding

Ship as a Codex plugin + marketplace (§2.3), pending Spike D:

1. `codex plugin marketplace add <internal repo or local root>`
2. `codex plugin marketplace upgrade`
3. install via `/plugins` or preconfigured marketplace policy (locked fleets:
   publish repo marketplace metadata + admin `requirements.toml` allowing only
   the internal source).
4. `scripts/bootstrap.sh --check` verifies `codex`/`claude`/`gemini`/`agy`,
   Python, `jq`, auth, PATH for `bin/`, and a writable classifier path. If plugin
   install does not expose `bin/` on PATH, bootstrap installs a launcher (no
   symlinks in artifacts — packaging/launcher per user rule).

---

## 11. Phased build order (riskiest-spike-first)

- **Spike D (do FIRST — last mechanism risk):** package a minimal plugin of this
  repo, `codex plugin marketplace add` it locally, and confirm a **plugin-shipped
  named repair agent is spawnable by name** (the open-bug territory). If it
  fails: fall back to a bootstrap that installs repair agents into
  `~/.codex/agents/` (personal scope — proven), decoupled from the plugin.
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

- **Plugin-shipped named agents** (Spike D) — the one unproven mechanism.
- **Codex plugin manifest** exact path/format — unverified (§2.3).
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
6. Distribution fallback if Spike D fails (plugin vs bootstrap-into-`~/.codex/agents`).

---

## 14. Sources & evidence

- Draft plan: `docs/references/codex-draft-plan.md` (Codex xhigh + web search).
- claude leg: `docs/references/claude-leg-spec.md`, `claude-headless-reference.md`.
- Spike evidence: `docs/references/spike-evidence-leader.log`,
  `spike-evidence-result.json`.
- Official: developers.openai.com/codex/{subagents,config-reference},
  code.claude.com/docs/en/{headless,cli-reference,model-config,env-vars}.
- Tier-2: installed `codex --help` / `codex features list` / `claude --help`.
