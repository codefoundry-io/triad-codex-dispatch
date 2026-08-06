---
name: triad-cross-family-review
description: Use when an owner requests independent cross-family review or when a review-worthy architecture, compatibility, deployment, causality, security, data-loss, or pre-merge decision needs evidence from Claude, Google, and fresh Codex families.
---

# Triad Cross-Family Review

## Overview

Run independent Claude, Google-family, and fresh Codex review over one focused
immutable directory. The Codex leader owns scope, writes fixes, reproduces every
claim, and repeats complete rounds until the evidence converges.

## Supported execution shape

One round is exactly:

```text
one prepared directory
  -> one Claude LegVerdict
  -> one Google LegVerdict
  -> one fresh Codex LegVerdict
  -> leader reproduction and classification
```

A candidate change creates a new directory/digest and a new complete round.
Old and new leg results are never mixed.

Batching is removed from the supported architecture. Do not retain review
batches, shards, family-by-batch matrices, or batch receipts as a default,
optional, compatibility, or complete-coverage mode. Complete coverage means
that each of the three families reviews the same complete focused directory in
the round.

## Flow

1. **Authorize and bound.** Record the providers, objective, exact external
   data boundary, and exact test-source rule. Exclude credentials,
   authentication files, environment dumps, provider logs, and unrelated data.
2. **Prepare once.** Create one directory containing complete current files
   relevant to the decision, governing documentation, `TASK.md`, and one
   readable canonical diff. Prompts name the directory; they do not inline file
   bodies.
3. **Capture integrity.** Use the packaged `bin/review_round.py capture` before
   dispatch. Keep the snapshot and reviewer results outside the prepared
   directory.
4. **Dispatch the round.** Read
   [leg contracts](references/leg-contracts.md) and start all three independent
   legs before consuming a verdict. Reviewers may read and search only; they do
   not edit or execute candidate code, tests, builds, hooks, or scripts.
5. **Admit results.** Each family returns one JSON object matching
   `verdict_schema:LegVerdict`. Bind review ID, family, and content digest with
   the packaged validator. A missing, refused, malformed, route-mismatched, or
   incomplete required leg invalidates the round.
6. **Verify integrity.** After all required legs terminate, run
   `bin/review_round.py verify`. A prepared-directory or worktree fingerprint
   mismatch invalidates the round.
7. **Reproduce and converge.** Read
   [convergence](references/convergence.md). Verify every finding against the
   canonical worktree. Apply only the smallest correction inside the approved
   design, run project verification, prepare changed evidence, and start a new
   complete round.
8. **Ask before design changes.** A proposed design/specification change,
   generalization, new capability, or scope expansion is
   `OWNER_DECISION_REQUIRED`. Present the concrete delta, evidence, impact, and
   decision needed; do not edit the affected area first.
9. **Finish on evidence.** The gate passes only when all required families
   return admitted `SAFE` for the same digest. Conflict or oscillation goes to
   the owner. There is no arbitrary round cap and no unchanged redispatch to
   seek a preferred label.

## Result contract

Read [review prompt contract](references/review-prompt-contract.md) before
rendering a round. `SAFE` permits Minor findings but no Critical/Major finding
or open question. `NOT-SAFE` requires a Critical/Major finding or open question.
Provider prose, confidence, or policy disclaimers never substitute for the
structured result.

## Distribution acceptance

Repository tests and a successful review round are necessary but do not prove
that the distributable plugin works. Before a release claim, verify the
packaged manifest and skill bytes, install or stage those exact bytes through
the supported consumer path, and use a fresh Codex process to prove the skill
is exposed with an exact current marker. Installed inventory, source-only
imports, or an already-running session are not acceptance evidence.

## Quick reference

| Event | Leader action |
|---|---|
| All three admitted `SAFE` | Pass the round |
| Verified bounded defect | Fix, verify, fresh three-family round |
| Refuted finding | Record contradictory evidence; no edit |
| Design/spec/capability/scope delta | Ask owner before editing |
| Conflicting verified claims | Ask owner to adjudicate |
| Alternating advice on unchanged bytes | Stop and ask owner |
| Missing/invalid required leg | Invalidate the round |
