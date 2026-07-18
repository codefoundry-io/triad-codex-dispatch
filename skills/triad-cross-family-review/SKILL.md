---
name: triad-cross-family-review
description: Use when the Codex leader is about to merge review-worthy or correctness-critical work and wants a cross-family pre-merge review — three INDEPENDENT reviewers (two other model families, claude + a Google-family leg, plus a fresh-context codex reviewer), each framing suspect decisions as questions, consolidated until the verdict is unanimous SAFE. Triggering signals — before committing/merging a risky change; the user asks to run a cross-review, cross-check before merge, or get a review from the other model families; the standing review rule "review before merge". Composes the dispatch legs (triad-claude-dispatch + triad-antigravity-dispatch/triad-gemini-dispatch); it does NOT itself patch code.
---

# triad-cross-family-review

A **Codex leader's** pre-merge review by three INDEPENDENT reviewers — two
other model families plus a fresh-context codex reviewer (context-independent,
same family). The inverted mirror of the Claude-led toolkit's
cross-family review: here **codex is the leader family**, so the codex reviewer
must be a FRESH context (not the leader's own thread) to keep the three voices
independent.

## Use when

- About to merge / commit review-worthy or correctness-critical work.
- A higher-level flow wants a diverse-family sanity check before shipping.

Independence is the whole point: three independent reviewers — two other model
families plus a fresh-context codex — catch failure modes a single family (or
the author) would miss.

## The three reviewers

1. **claude** — via `triad-claude-dispatch`, `--sandbox read-only` (never let a
   reviewer mutate the tree). Use max-depth review settings:
   `--effort max` (claude's family-MAX reasoning tier). Here the claude leg is a
   CLI dispatch, not an in-session Agent, so `--sandbox read-only` MECHANICALLY
   restricts it to the `Read, Glob, Grep` tool allowlist (the wrapper synthesizes
   `--tools "Read,Glob,Grep"`) — the no-execute contract is enforced by the tool
   set, not by the prompt directive alone.
2. **Google family** — via `triad-antigravity-dispatch` (agy, PRIMARY) or, for a
   business-tier gemini account, `triad-gemini-dispatch`. `--sandbox read-only`.
   Runtime selection: `TRIAD_GOOGLE_REVIEW_CLI` env (`agy` | `antigravity` |
   `gemini`; `antigravity` is an alias normalized to agy), else agy, else gemini. If neither Google leg is available, log it (NOT an
   error) and run a two-family ADVISORY review with the remaining families —
   advisory rounds do not satisfy the rule-7 release gate. For agy review, pass
   `--model "${TRIAD_GOOGLE_REVIEW_MODEL:-Gemini 3.1 Pro (High)}"` when that
   model is available; if it is not available, log the fallback instead of
   inventing a model name. For business-tier gemini, pass an owner-verified
   `TRIAD_GOOGLE_REVIEW_MODEL` when configured; otherwise use the CLI default and
   log that the business-tier model is unpinned. Business-tier Gemini read-only
   is unverified until the owner has run a write-attempt check in that account.
   **Do NOT treat the agy leg as the more-trusted release gate on agy ≥1.1.3**:
   its `--sandbox read-only` is VOIDED there by the wrapper's skip-perms gate
   (see `triad-antigravity-dispatch` § Headless soft-deny adaptation), so on
   ≥1.1.3 agy is read-only by INTENT only — a business-tier gemini
   `--sandbox read-only` (Policy-Engine-enforced, once verified) is the STRONGER
   gate. On agy ≤1.1.2 the agy deny transaction is genuinely enforced and this
   preference holds.
3. **codex (fresh)** — a FRESH codex reviewer for independence: use Codex
   multi-agent `spawn_agent` to start a fresh subagent with the same packet,
   produced and saved BEFORE it sees the other legs' outputs. The leader does
   NOT review in its own thread (its context is polluted by having
   authored/orchestrated the change). Give the reviewer an explicit deep,
   adversarial prompt ("assume a subtle coverage gap is present"), and where the
   `spawn_agent` tool exposes a `reasoning_effort` parameter, set it to the
   highest supported tier — the prompt carries the adversarial stance; the
   parameter (when present) carries the depth. Prefer defining the reviewer
   ONCE as a custom agent file (`.codex/agents/reviewer.toml` — per the
   Codex subagents doc: `name` / `description` / `developer_instructions`,
   plus `sandbox_mode = "read-only"` and a high `model_reasoning_effort`):
   the sandbox and the reasoning effort are then CONFIG-pinned for every
   spawn instead of relying on the prompt, so neither can be forgotten at
   dispatch time.

## Hard rules

1. **Read-only reviewers.** The two CLI legs (claude + Google) are dispatched
   `--sandbox read-only`. **Caveat — agy ≥1.1.3 is read-only by INTENT, not
   enforcement**: the wrapper inserts `--dangerously-skip-permissions` on agy
   ≥1.1.3 (headless soft-deny adaptation), voiding the deny transaction + OS-ring,
   so a ≥1.1.3 agy Google leg can read outside `--cwd` / exfiltrate over the
   network when fed an adversarial packet — the `--sandbox read-only` dispatch
   form below is still correct as an INSTRUCTION but is not enforced containment
   there (see `triad-antigravity-dispatch` § Headless soft-deny adaptation;
   opt-out `AGY_NO_HEADLESS_AUTOAPPROVE=1`). Enforced on agy ≤1.1.2 and on gemini.
   The fresh-codex `spawn_agent` reviewer is not a CLI
   dispatch, so it carries no `--sandbox` flag — it INHERITS the leader session's
   sandbox UNLESS it is spawned from a custom agent file that pins
   `sandbox_mode = "read-only"` (reviewer #3's recommended setup, which
   config-enforces the sandbox per spawn), and is otherwise held to read-only
   only by its prompt (the clause
   below + Step 2: review by reading only, do not modify files), so give it that
   instruction explicitly; for a release gate, prefer the custom-agent pin or
   running the review turn
   under a read-only profile so the enforced sandbox matches what the prompt
   requests. A reviewer that edits the tree is a bug regardless of the mechanism.
   The reviewer prompt for every leg also says: "Do NOT run scripts/tests, spawn
   subprocesses, invoke vendor CLIs, or modify files; review by reading the packet
   and referenced files only." This avoids hangs and keeps reviewers from
   live-running the code under review.
   Two scoped exceptions keep the contract single-reading: the fresh-codex leg's
   ONLY write is its own verdict file (`_runs/reviews/<id>/codex-verdict.md`) —
   and under a read-only profile even that write is blocked, so there it returns
   the verdict INLINE as its final message and the leader saves it verbatim; and
   the agy leg may READ official web docs to verify a fact — web reading is
   read-only; code execution is not.
   Known-harmless artifact of the read-only profile: a reviewer may REPORT
   that it lacks permission to persist its own session/scratch file. When the
   verdict still returns complete, treat that specific self-persistence
   complaint as expected — do NOT widen the sandbox for it, and do NOT
   normalize OTHER permission failures under this note.
2. **Independence before consolidation.** Collect all three verdicts BEFORE the
   leader reasons across them. Do not feed one reviewer another's output. The
   fresh-codex verdict is captured first — its file, or the leader saving the
   inline verdict verbatim — before the leader reads any other leg.
3. **Frame suspect decisions as QUESTIONS.** Each reviewer is asked to surface
   its doubts as questions ("why is X safe when Y?"), not verdicts — questions
   expose hidden assumptions; bare "LGTM/NAK" hides them.
4. **Fix → re-confirm loop with a circuit breaker — and non-convergence is a
   STOP, not another round.** Consolidate the questions,
   the leader fixes the real issues, then RE-RUN the three reviewers on the fix.
   Repeat until all three return no blocking questions, but stop after
   `TRIAD_REVIEW_MAX_ROUNDS` (default 2) full review rounds — and stop EARLY,
   regardless of the budget, when a new round — WITHOUT adding material new
   evidence — merely flips a prior round's settled decision, contradicts
   another live leg head-on, or re-litigates an already-adjudicated point:
   consolidate the conflicting claims into a table (claim / leg / round /
   evidence) and hand it to the owner for adjudication instead of
   dispatching again. When a flip or contradiction DOES carry new evidence,
   adjudicate that evidence with a deterministic probe first (grep the
   source, read official docs) and let the probe decide whether another
   round is warranted. Independent legs finding the SAME defect is not a
   conflict — it is a convergence floor: fix it and run one final confirm.
   One family's
   unresolved blocking question = NOT SAFE to merge. If the round budget is
   exhausted, stop and record an owner decision instead of looping.
5. **File-IPC for the packet.** Pre-assemble ONE review packet at
   `_runs/reviews/<id>/packet.md` under the repo root (the diff + intent + the
   suspect decisions). Each leg reads ONLY that file by **referencing its path
   inside the dispatch `--prompt`** (a short instruction — "Read
   `_runs/reviews/<id>/packet.md` and review it") and running with `--cwd
   <repo-root>` so the read-only leg's Read tool can open it. Keep the `--prompt`
   SHORT — a path, NEVER the packet's content. Never inline a large diff into a
   dispatch prompt. (Path-IPC is safe for every leg here: the CLI legs Read the
   repo-relative packet under their own tools, and the fresh-codex `spawn_agent`
   reviewer reads repo files natively — unlike a sandboxed codex CLI dispatch,
   which would need the packet inlined; that inline rule belongs to the
   Claude-host edition's codex leg, not to this host.) The leg skills must invoke wrappers as literal absolute
   wrapper commands — the execpolicy allowlist matches that literal shape, so an
   indirection layer (heredoc command substitution, `bash -lc`, `zsh -lc`,
   `python3`, `/usr/bin/env`) falls outside the allowed prefix and is refused.
6. **Fresh Codex is subagent-only.** The Codex-family reviewer MUST be spawned
   with the multi-agent `spawn_agent` tool using `fork_context=false`. Do not
   shell out to a second Codex CLI process from this repo. If `spawn_agent` is
   unavailable, log the Codex-family reviewer as unavailable for that round.
7. **Release gate is stricter than advisory review.** For pre-release or merge
   gating, all three families must be present and return **Claude SAFE**,
   **agy SAFE** (or owner-verified business-tier Gemini SAFE), and
   **fresh Codex SAFE**. If any family is unavailable or NOT-SAFE, the automated
   gate does not pass; degraded two-family mode is advisory only, and merging on
   fewer than three families requires a recorded owner decision (matching the
   Claude-host edition). If read-only enforcement is unavailable for the
   fresh-codex leg (no custom-agent `sandbox_mode` pin AND no read-only
   session profile), treat that leg as advisory for release gating too.
8. **Adversarial framing on EVERY leg, not just the fresh-codex one.** A leg at its
   top reasoning tier still rubber-stamps when its prompt only asks it to "check if
   this looks fine" — the tier is necessary but not sufficient. Give the claude and
   Google legs the same adversarial framing the fresh-codex leg gets (assume a defect
   is present; do not deflate a real correctness/safety issue to minor), and require
   every leg to (a) enumerate which decisions/rules it checked before concluding and
   (b) treat a bare "SAFE / none" verdict as a failed review, not a pass. A fast,
   terse SAFE/none from any leg (e.g. a sub-30s pass over a large packet) is a
   rubber-stamp signal — re-dispatch that leg with the adversarial framing.
9. **Leg orchestration: hub-and-spoke, event-driven waits, no polling.**
   Subagents do not talk to each other — the leader is the coordinator: it
   spawns each leg, routes any follow-up instruction, waits for results, and
   closes finished threads (per the Codex subagents doc; steer a RUNNING leg
   by asking Codex to send it input rather than respawning it).
   Each leg prompt states three things up front:
   how the work is divided, whether the leader waits for all legs before
   continuing, and exactly what to return — a distilled verdict plus findings
   with evidence paths, never raw logs (subagents exist to keep noisy
   intermediate output OFF the main thread: context pollution / context rot).
   Waiting discipline: prefer ONE generous event-driven wait per leg over
   short repeated polls. A wait that expires is a wake-up boundary, not
   evidence the leg failed: inspect that leg's state ONCE, keep a healthy
   running leg alive through its completion, and move a leg to the
   degraded-mode handling only on a documented terminal failure or an
   explicit owner decision to end the wait; never interrupt or respawn a
   healthy leg because a wait elapsed, and never re-wait a leg whose
   result already arrived. While legs run, the leader does only
   review-adjacent prep (fact-check planning, packet hygiene) — unrelated
   work interleaved into the leader's context pollutes later consolidation.
   Consolidate once every dispatched leg has either returned a result or
   been logged as missing via that terminal path (rule 2's independence
   still applies) — never by silently dropping one. Close completed threads
   when done so the configured `agents.max_threads` cap stays available,
   and keep `agents.max_depth` low enough that legs cannot fan out
   recursively (see the Codex agents config reference for the current
   defaults).

## Flow

### Step 1 — Assemble the packet

Write `_runs/reviews/<id>/packet.md`: the change (`git diff` scoped to intended
paths), a 2–3 line intent, and the 2–5 decisions you most want scrutinized.

Where the leader's exec policy permits `python3`, prefer creating `<id>` via the
bundled lifecycle helper — `python3 <plugin-dir>/skills/triad-cross-family-review/lib/review_scratch.py
open <abs-repo>/_runs/reviews <slug>` — which also prunes stale packet dirs
stranded by crashed past reviews (only helper-created dirs whose `.active`
heartbeat marker carries the helper's provenance magic; 7-day floor,
`TRIAD_REVIEW_SCRATCH_MAX_AGE_DAYS` overrides; symlinks refused,
unmanaged/non-date entries never touched). If
the exec allowlist does not cover the helper, add
its literal command prefix or fall back to `mkdir -p` + the Step 5 cleanup —
the helper is a crash backstop, not a new dependency.

### Step 2 — Dispatch the three reviewers (concurrent)

Fan out — each gets the same packet path and the same framing prompt:

> "Review the change in `<packet-path>`. Assume a real defect is present and find it;
> a bare 'SAFE — no issues' is a failed review unless you can name the decisions you
> checked. Frame every doubt as a QUESTION about a specific decision (file:line), and
> enumerate which decisions/rules you checked. Do not fix anything. Do NOT run
> scripts/tests, spawn subprocesses, invoke vendor CLIs, or modify files (fresh
> codex: writing your own verdict file is the one exception); review by reading the
> packet and referenced files only (agy: reading official web docs to verify a fact
> is allowed). Do not deflate a real
> correctness/safety issue to minor. List blocking questions (merge-stoppers)
> separately from minor ones. End with SAFE / NOT-SAFE and, if NOT-SAFE, the blocking
> questions."

- claude leg: `triad-claude-dispatch` — `--sandbox read-only --effort max
  --cwd <repo-root>`; the packet path is referenced in the prompt (the leg Reads
  it under read-only). The repo cwd is safe here despite that skill's
  sibling-dir isolation contract: `--sandbox read-only` synthesizes
  `--setting-sources user`, which blocks the dispatched-into repo's CLAUDE.md
  from loading — the reviewer reads the packet without inheriting the repo
  frame.
- Google leg: `triad-antigravity-dispatch` (or `triad-gemini-dispatch`) —
  `--sandbox read-only --cwd <repo-root>`. For agy, prefer `--model "Gemini 3.1
  Pro (High)"` (or `TRIAD_GOOGLE_REVIEW_MODEL`) after verifying the model exists;
  agy may read official web docs to verify a fact (rule 1's scoped exception).
- fresh codex: use multi-agent `spawn_agent` with `fork_context=false` so the
  reviewer starts from a fresh context. Tell it to read the packet path, not the
  other reviewers' outputs, to reason deeply/adversarially, and to deliver its
  verdict BEFORE the leader reads the other two — written to
  `_runs/reviews/<id>/codex-verdict.md` when it has that write grant, otherwise
  returned inline as its final message (the leader saves it verbatim).
  Call `wait_agent` for that spawned reviewer before reading its verdict;
  reading the file before the wait completes is a race.

### Step 3 — Consolidate (leader, after all three land)

Gather the three verdicts + their blocking questions. Deduplicate. A question
raised by any one family is in scope. If all three are SAFE with no blocking
questions → proceed to merge.

The leader's consolidation role is three duties, in order:

1. **Fact-check every finding against the source before acting on it** —
   read the cited lines, reproduce the claim with a deterministic probe
   (grep, official docs). A finding can be plausible and wrong; a reviewer's
   confidence is not evidence. A probe-refuted finding is closed by
   recording the probe.
2. **Classify the round**: CONVERGING (new real findings, or independent
   legs hitting the SAME defect — fix it and run one final confirm),
   **CONFLICTED** (legs contradict HEAD-ON on the SAME decision — one leg
   approves what another requires changed, or two demand mutually
   exclusive changes — and BOTH sides survive the duty-1 probe; owner
   directive 2026-07-18), or OSCILLATING (verdict flips / re-litigation
   without new evidence).
3. **On a CONFLICTED item or an oscillating round, CALL THE OWNER
   IMMEDIATELY** with the rule-4 conflict table (claim / leg / round /
   evidence + the leader's fact-check) — the owner adjudicates. The
   leader never self-adjudicates a compromise between live contradicting
   legs, however plausible the middle path, and never spends another
   round on the conflicted item; non-conflicted findings keep their fix
   loop running in parallel while the call is pending. Probe-refuted
   sides, complementary findings, and same-defect convergence are NOT
   conflicts.

### Step 4 — Fix → re-confirm

For each real blocking question, the leader fixes it (or justifies why it is a
non-issue, recorded). Then RE-RUN Step 2 on the fixed change. Loop until the
verdict is **unanimous SAFE**, but stop after `TRIAD_REVIEW_MAX_ROUNDS`
(default 2) full rounds. If a reviewer still blocks after that, do not keep
dispatching; record the remaining questions and get an owner decision. Only a
unanimous SAFE verdict is merge-eligible.

### Step 5 — Cleanup

`rm -rf _runs/reviews/<id>` once merged — or, when the helper created the dir,
`python3 <plugin-dir>/skills/triad-cross-family-review/lib/review_scratch.py close <abs-dir>`
(`close` acts only on dirs carrying the helper's `.active` marker — an
arbitrary date-named dir is refused). Keep the final packet + verdicts as a
review record if the change is significant — owner judgment; note a kept dir
retains its `.active` heartbeat and a later helper `open` prunes it once the
heartbeat passes the age floor, so move long-term records outside the packet
root.

## Degraded modes (log, not error)

- No Google-family leg available (gemini individual tier dead + agy absent) →
  run claude + fresh-codex only; log the missing family.
- No multi-agent `spawn_agent` tool available → log the Codex-family reviewer as
  unavailable for this round. Do not replace it with another Codex CLI process.
- A leg returns a terminal/repair-routed failure → surface it; that family's
  review is unavailable for this round (do not treat a wrapper failure as SAFE).

## See also

- `triad-claude-dispatch` / `triad-antigravity-dispatch` / `triad-gemini-dispatch`
  — the legs this skill composes.
- Design spec §9 (cross-family review) + §3a (Google-family = agy).
