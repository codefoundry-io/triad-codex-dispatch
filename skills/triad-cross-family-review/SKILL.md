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
   `--effort max` (claude's family-MAX reasoning tier).
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
   is unverified until the owner has run a write-attempt check in that account;
   use agy for release gating when that write-attempt evidence is absent.
3. **codex (fresh)** — a FRESH codex reviewer for independence: use Codex
   multi-agent `spawn_agent` to start a fresh subagent with the same packet,
   produced and saved BEFORE it sees the other legs' outputs. The leader does
   NOT review in its own thread (its context is polluted by having
   authored/orchestrated the change). Give the reviewer an explicit deep,
   adversarial prompt ("assume a subtle coverage gap is present"), and where the
   `spawn_agent` tool exposes a `reasoning_effort` parameter, set it to the
   highest supported tier — the prompt carries the adversarial stance; the
   parameter (when present) carries the depth.

## Hard rules

1. **Read-only reviewers.** The two CLI legs (claude + Google) are dispatched
   `--sandbox read-only`. The fresh-codex `spawn_agent` reviewer is not a CLI
   dispatch, so it carries no `--sandbox` flag — it INHERITS the leader session's
   sandbox and is otherwise held to read-only only by its prompt (the clause
   below + Step 2: review by reading only, do not modify files), so give it that
   instruction explicitly; for a release gate, prefer running the review turn
   under a read-only profile so the inherited sandbox enforces what the prompt
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
2. **Independence before consolidation.** Collect all three verdicts BEFORE the
   leader reasons across them. Do not feed one reviewer another's output. The
   fresh-codex verdict is captured first — its file, or the leader saving the
   inline verdict verbatim — before the leader reads any other leg.
3. **Frame suspect decisions as QUESTIONS.** Each reviewer is asked to surface
   its doubts as questions ("why is X safe when Y?"), not verdicts — questions
   expose hidden assumptions; bare "LGTM/NAK" hides them.
4. **Fix → re-confirm loop with a circuit breaker.** Consolidate the questions,
   the leader fixes the real issues, then RE-RUN the three reviewers on the fix.
   Repeat until all three return no blocking questions, but stop after
   `TRIAD_REVIEW_MAX_ROUNDS` (default 2) full review rounds. One family's
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
   fresh-codex leg, treat that leg as advisory for release gating too.
8. **Adversarial framing on EVERY leg, not just the fresh-codex one.** A leg at its
   top reasoning tier still rubber-stamps when its prompt only asks it to "check if
   this looks fine" — the tier is necessary but not sufficient. Give the claude and
   Google legs the same adversarial framing the fresh-codex leg gets (assume a defect
   is present; do not deflate a real correctness/safety issue to minor), and require
   every leg to (a) enumerate which decisions/rules it checked before concluding and
   (b) treat a bare "SAFE / none" verdict as a failed review, not a pass. A fast,
   terse SAFE/none from any leg (e.g. a sub-30s pass over a large packet) is a
   rubber-stamp signal — re-dispatch that leg with the adversarial framing.

## Flow

### Step 1 — Assemble the packet

Write `_runs/reviews/<id>/packet.md`: the change (`git diff` scoped to intended
paths), a 2–3 line intent, and the 2–5 decisions you most want scrutinized.

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

### Step 4 — Fix → re-confirm

For each real blocking question, the leader fixes it (or justifies why it is a
non-issue, recorded). Then RE-RUN Step 2 on the fixed change. Loop until the
verdict is **unanimous SAFE**, but stop after `TRIAD_REVIEW_MAX_ROUNDS`
(default 2) full rounds. If a reviewer still blocks after that, do not keep
dispatching; record the remaining questions and get an owner decision. Only a
unanimous SAFE verdict is merge-eligible.

### Step 5 — Cleanup

`rm -rf _runs/reviews/<id>` once merged (or keep the final packet + verdicts as a
review record if the change is significant — owner judgment).

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
