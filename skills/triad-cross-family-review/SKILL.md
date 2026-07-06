---
name: triad-cross-family-review
description: Use when the Codex leader is about to merge review-worthy or correctness-critical work and wants a cross-family pre-merge review — three INDEPENDENT reviewers from different model families (claude + a Google-family leg + a fresh codex perspective), each framing suspect decisions as questions, consolidated until the verdict is unanimous SAFE. Triggering signals — before committing/merging a risky change; the user said "크로스 리뷰 돌려줘" / "머지 전에 교차 검증" / "다른 모델들한테 리뷰 받아"; the standing review rule "review before merge". Composes the dispatch legs (triad-claude-dispatch + triad-antigravity-dispatch/triad-gemini-dispatch); it does NOT itself patch code.
---

# triad-cross-family-review

A **Codex leader's** pre-merge review by three INDEPENDENT reviewers from
different model families. The inverted mirror of the Claude-led toolkit's
cross-family review: here **codex is the leader family**, so the codex reviewer
must be a FRESH context (not the leader's own thread) to keep the three voices
independent.

## Use when

- About to merge / commit review-worthy or correctness-critical work.
- A higher-level flow wants a diverse-family sanity check before shipping.

Independence is the whole point: three different model families reviewing the
same packet catch failure modes a single family (or the author) would miss.

## The three reviewers

1. **claude** — via `triad-claude-dispatch`, `--sandbox read-only` (never let a
   reviewer mutate the tree). Use max-depth review settings:
   `--effort max` (claude's family-MAX reasoning tier).
2. **Google family** — via `triad-antigravity-dispatch` (agy, PRIMARY) or, for a
   business-tier gemini account, `triad-gemini-dispatch`. `--sandbox read-only`.
   Runtime selection: `TRIAD_GOOGLE_REVIEW_CLI` env (`antigravity` | `gemini`),
   else agy, else gemini. If neither Google leg is available, log it (NOT an
   error) and run with the remaining two families. For agy review, pass
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
   adversarial prompt ("think as hard as you can; assume a subtle coverage gap is
   present") because there is no separate CLI reasoning flag on `spawn_agent`.

## Hard rules

1. **Read-only reviewers.** Every leg is dispatched `--sandbox read-only`. A
   reviewer that edits the tree is a bug.
   The reviewer prompt MUST also say: "Do NOT run scripts/tests, spawn
   subprocesses, invoke vendor CLIs, or modify files; review by reading the packet
   and referenced files only." This avoids hangs and keeps reviewers from
   live-running the code under review.
2. **Independence before consolidation.** Collect all three verdicts BEFORE the
   leader reasons across them. Do not feed one reviewer another's output. The
   fresh-codex verdict is written to a file before the leader reads any leg.
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
   dispatch prompt. The leg skills must invoke wrappers as literal absolute
   wrapper commands; do not use heredoc command substitution, `bash -lc`,
   `zsh -lc`, `python3`, or `/usr/bin/env` for no-prompt dispatch.
6. **Fresh Codex is subagent-only.** The Codex-family reviewer MUST be spawned
   with the multi-agent `spawn_agent` tool using `fork_context=false`. Do not
   shell out to a second Codex CLI process from this repo. If `spawn_agent` is
   unavailable, log the Codex-family reviewer as unavailable for that round.
7. **Release gate is stricter than advisory review.** For pre-release or merge
   gating, all three families must be present and return **Claude SAFE**,
   **agy SAFE** (or owner-verified business-tier Gemini SAFE), and
   **fresh Codex SAFE**. If any family is unavailable or NOT-SAFE, do not merge;
   degraded two-family mode is advisory only.

## Flow

### Step 1 — Assemble the packet

Write `_runs/reviews/<id>/packet.md`: the change (`git diff` scoped to intended
paths), a 2–3 line intent, and the 2–5 decisions you most want scrutinized.

### Step 2 — Dispatch the three reviewers (concurrent)

Fan out — each gets the same packet path and the same framing prompt:

> "Review the change in `<packet-path>`. Frame every doubt as a QUESTION about a
> specific decision (file:line). Do not fix anything. Do NOT run scripts/tests,
> spawn subprocesses, invoke vendor CLIs, or modify files; review by reading the
> packet and referenced files only. List blocking questions (merge-stoppers)
> separately from minor ones. End with SAFE / NOT-SAFE and, if NOT-SAFE, the
> blocking questions."

- claude leg: `triad-claude-dispatch` — `--sandbox read-only --effort max
  --cwd <repo-root>`; the packet path is referenced in the prompt (the leg Reads
  it under read-only).
- Google leg: `triad-antigravity-dispatch` (or `triad-gemini-dispatch`) —
  `--sandbox read-only --cwd <repo-root>`. For agy, prefer `--model "Gemini 3.1
  Pro (High)"` (or `TRIAD_GOOGLE_REVIEW_MODEL`) after verifying the model exists;
  agy web tools are fine (it may check current docs).
- fresh codex: use multi-agent `spawn_agent` with `fork_context=false` so the
  reviewer starts from a fresh context. Tell it to read the packet path, not the
  other reviewers' outputs, to reason deeply/adversarially, and to write its
  verdict to
  `_runs/reviews/<id>/codex-verdict.md` BEFORE the leader reads the other two.
  Call `wait_agent` for that spawned reviewer before reading
  `codex-verdict.md`; reading the file before the wait completes is a race.

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
