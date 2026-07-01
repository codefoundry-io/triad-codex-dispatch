# triad-codex-dispatch

**Status: WIP / design phase.** A **Codex-led** mirror of the Claude-Code-led
[`triad-dispatch`](../triad-dispatch) toolkit, for internal company
distribution — for teams who want **Codex** as the orchestrator instead of
Claude Code.

Codex is the leader; it dispatches **claude** (new `claude -p` single-shot leg),
**gemini**, and **antigravity (agy)** as single-shot workers, with
classification-aware routing, a self-improving classifier, Codex-native repair
subagents, and a cross-family pre-merge review.

## Where things are

- **Design spec:** [docs/specs/2026-07-01-codex-led-triad-dispatch-design.md](docs/specs/2026-07-01-codex-led-triad-dispatch-design.md)
- **References** (`docs/references/`):
  - `codex-draft-plan.md` — Codex's own xhigh + web-search draft plan (read the source repo, verified constraints).
  - `claude-leg-spec.md` — the `claude -p` single-shot leg spec (wrapper-oriented).
  - `claude-headless-reference.md` — full `claude -p` headless reference (682 lines).
  - `spike-evidence-*` — proof that Codex named-subagent repair works (see the design spec §Repair).

Nothing is implemented yet — the design spec must be reviewed and approved, then
an implementation plan (writing-plans) drives the build.
