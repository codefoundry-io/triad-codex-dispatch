# Distribution Handoff — Codex-Led Triad Dispatch

**For: a Codex leader** (this is written to be handed to Codex as a task brief or
pointed at as a file). **Repo:** `~/triad-codex-dispatch` (its own git repo,
branch `main`, local-only). **Date:** 2026-07-01. **Prereq:** trust this
workspace when codex prompts, and run codex from the repo root so `.agents/skills`
discovers the dispatch skills.

---

## 0. Your task

Build the **distribution layer** for this Codex-led dispatch toolkit so teams can
INSTALL and UPDATE it across machines: a Codex plugin + marketplace, a bootstrap
script, and install/update docs. **Do Spike D FIRST** (§2) — it decides whether
the repair agents ship in the plugin or via bootstrap. Nothing here should
contradict the VERIFIED constraints in §4. Flag every owner decision (§5) rather
than guessing. Use the installed **OpenAI docs MCP** (`developers.openai.com/mcp`)
+ `codex plugin --help` to confirm the exact plugin manifest schema — do NOT
invent config keys.

---

## 1. Current repo state (already built + verified — do not rebuild)

- **Engine** `bin/`: leader-agnostic Python wrappers `claude_wrapper.py`,
  `gemini_wrapper.py`, `antigravity_wrapper.py` + `_common.py` / `_pty.py` /
  `_agy_settings.py`. Single-shot → shared classification token set → run-log
  JSON. `claude -p` leg built; gemini read-only via per-call `--policy` Policy
  Engine (never plan mode). 15/15 hermetic tests (`python3 -m pytest tests/`).
- **Skills** `.agents/skills/` (VERIFIED discoverable by real codex): 4 SKILL.md
  runbooks + `agents/openai.yaml` — `triad-claude-dispatch`,
  `triad-antigravity-dispatch` (PRIMARY Google leg), `triad-gemini-dispatch`
  (business-tier), `triad-cross-family-review`.
- **Repair named subagents** `agents/*.toml`: `claude-`, `agy-`,
  `gemini-wrapper-repair` (Codex `spawn_agent` → `wait_agent` → read
  `<run_log>.repair.json`).
- **Docs** `docs/`: design spec (`specs/2026-07-01-...`), references
  (`claude-leg-spec.md`, `google-family-agy-readonly.md`, `spike-e-*`,
  `codex-draft-plan.md`), and this handoff.

Read `docs/specs/2026-07-01-codex-led-triad-dispatch-design.md` §10 (distribution),
§11 (phased build order), §12 (open items), §13 (owner decisions) before starting.

---

## 2. Spike D — DO THIS FIRST (the one unproven mechanism)

**Question:** can the **named repair subagents be SHIPPED in a Codex plugin AND
still be spawned by name** by the leader? (Personal-scope `~/.codex/agents/*.toml`
was already verified spawnable; PROJECT-scope `.codex/agents/` has open bug
[#26408](https://github.com/openai/codex/issues/26408). Plugin-shipped is a
THIRD, untested path.)

**How to spike (throwaway):**
1. Package a MINIMAL plugin of this repo (skills + `agents/*.toml` + `bin/`).
2. `codex plugin marketplace add <local repo root>` → `codex plugin add …` →
   install.
3. From a fresh codex session, instruct the leader to `spawn_agent` the
   `claude-wrapper-repair` role BY NAME, have it write a JSON file, `wait_agent`,
   and read it back (mirror the §2.1 spike in the design spec — that harness
   already proved the mechanism works from `~/.codex/agents/`).
4. **Verdict:** if the plugin-shipped agent spawns by name → ship repair agents in
   the plugin. If NOT → **fallback: the bootstrap copies `agents/*.toml` into
   `~/.codex/agents/`** (personal scope — already verified spawnable). Log which
   path you took.

Also confirm (same session): are the **skills shippable via the plugin**, or must
they land in a `.agents/skills` discovery scope? (In-repo `.agents/skills/` is
verified; plugin-shipped skills need confirming against `codex plugin` docs.)

---

## 3. Distribution to build (after Spike D)

1. **Codex plugin manifest** — the exact path/format is UNVERIFIED. Confirm via
   the OpenAI docs MCP + `codex plugin --help` / `codex plugin add --help`, then
   author it. It must bundle: the 4 skills, the `bin/` wrappers, and (per Spike D)
   the repair agents.
2. **Marketplace entry** (repo-scoped) so `codex plugin marketplace add <internal
   git url or local root>` + `codex plugin marketplace upgrade` work. Installed
   copies live under `~/.codex/plugins/cache/…`. For locked fleets, publish
   marketplace metadata + an admin `requirements.toml` allowing only the internal
   source.
3. **`scripts/bootstrap.sh --check`** — verify: `codex` / `claude` / `gemini` /
   `agy` binaries + auth; `python3 >= 3.12`; `jq`; `bin/` on PATH (install a
   launcher if the plugin does not expose it — NO symlinks in artifacts); a
   writable classifier path `~/.config/triad-codex-dispatch/`; and, per Spike D,
   install the repair agents into `~/.codex/agents/`. Also remind the user to
   TRUST the workspace (skills load only after trust).
4. **Install + update docs** `migration/COMPANY-SETUP.md` (+ `.ko.md`) and
   `migration/AGENTS.recommended.md` — the concrete install flow, permission /
   egress setup, and the auth prerequisites (claude independently authenticated;
   `codex --search` for repair web search; agy for Google-family; gemini only on a
   business/Vertex tier).

---

## 4. VERIFIED constraints (do NOT contradict or re-derive)

- **Skills** register ONLY from `.agents/skills/<name>/SKILL.md` (name+description
  frontmatter). `$skill-name` invokes. **Workspace trust gates loading.**
- **Repair named subagents:** `~/.codex/agents/<name>.toml` (personal scope)
  VERIFIED spawnable by name via `spawn_agent`→`wait_agent`→file. Project
  `.codex/agents/` has open bug #26408. `[agents]` config: `max_threads`,
  `max_depth=1`.
- **Codex plugin/marketplace exists:** `codex plugin {add,list,marketplace,remove}`;
  features `plugins` + `plugin_sharing` stable; cache `~/.codex/plugins/cache/`.
- **Repair agents need web search** → the leader session must run `codex --search`
  (subagents inherit it — verified). `--search` is TOP-LEVEL: `codex --search exec`.
- **Classifier extension:** `~/.config/triad-codex-dispatch/classifier-patches.json`
  (per-cli keyed: `claude` / `gemini` / `antigravity`). Must be writable.
- **Google-family = agy** (gemini individual tier is DEAD — IneligibleTierError →
  Antigravity). gemini leg is business/Vertex tier only. agy read-only =
  per-call `--sandbox read-only` (deny transaction, restores — code-agent preserved).
- **claude leg** needs `claude` INDEPENDENTLY authenticated in the shell (keychain
  / API key), not a parent-session token.
- **No dated model IDs in code** (aliases only; `agy models` lists agy's).
- **No `bypassPermissions` / `danger-full-access`** (no-yolo, argparse-banned).

---

## 5. Open owner decisions (ask the human — do not guess)

1. **Repair-agent distribution** — plugin-shipped vs bootstrap-into-`~/.codex/agents/`
   (decided by Spike D's result; if both work, which is preferred?).
2. **Classifier path** — isolate `triad-codex-dispatch` + import old
   `triad-dispatch` gemini/agy patches (recommended) vs share the old path.
3. **Keep or drop `codex_wrapper.py`** (Codex is the leader family — a leg wrapper
   for the leader's own family is only needed for a fresh-Codex reviewer / `--task`).
4. **Marketplace source** — internal git URL vs local-clone (closed network).
5. **Plugin manifest path/format** — confirm the exact schema before committing.

---

## 6. How to verify your work

- **Spike D**: the empirical plugin-install + spawn-by-name test above (throwaway;
  clean up the test plugin + any `~/.codex/agents/` test file after).
- **Install flow**: on a clean shell, run `bootstrap.sh --check` and confirm every
  probe passes; then have a codex leader `$triad-claude-dispatch` a trivial prompt
  and confirm the `[wrapper] claude ok` path (needs claude auth).
- **Regression**: `python3 -m pytest tests/` stays 15/15.

## 7. Guardrails

- Verify plugin/config keys live (OpenAI docs MCP + `codex plugin --help`); cite
  the source. No guessing schema.
- Throwaway spikes clean up after themselves (test plugin, `~/.codex/agents/` test
  files, `~/.codex/config.toml` test entries).
- Do not modify the engine (`bin/`) or the merged skills except where a real
  distribution bug requires it — and if so, surface it, don't silently rewrite.
- Commit on a branch; the human reviews + merges. Do not push / publish a
  marketplace without explicit approval.
