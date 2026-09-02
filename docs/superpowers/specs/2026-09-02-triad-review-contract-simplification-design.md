# TRIAD Review Contract Simplification Design

## Status and scope

This is a post-0.2.548 design. It does not change the Gemini Enterprise fallback
release and it does not make the temporary five-leg owner gate part of the shipped
skill.

The single behavioral claim is: a formal cross-family review keeps the current
immutable review basis and admission guarantees while deriving lifecycle commands,
prompts, and receipts from one mechanical contract instead of repeated prose.

Forecast: net production delta from -250 to +250 lines, no more than 150 novel-core
lines, and one behavioral claim. This is an S/M slice. Tests, fixtures, and design
documents are outside the production-line budget.

## Problem

The current workflow has the right integrity properties but repeats parts of the
same contract across `SKILL.md`, reviewer routing, leg contracts, prompt contracts,
and tests. That repetition costs model context and makes a small contract change
require coordinated prose edits. Some lifecycle calls also use version-specific
`python3 <toolkit-root>/bin/...` argv even though bootstrap already publishes stable
launchers.

The review packet itself is not the problem. A trusted leader-captured diff, selected
related source files, a manifest, and a captured digest are what force every reviewer
to inspect the same current bytes. Those properties remain mandatory.

## Selected approach

Keep `review_round.py` as the mechanical orchestration boundary and make the shipped
skill a concise decision guide. The stable bootstrap-managed `review_round.py`
launcher becomes the lifecycle entrypoint. Detailed contracts remain in references,
but each fact has one canonical home:

- `SKILL.md` owns triggers, route choice, stop conditions, and the high-level formal
  lifecycle.
- One lifecycle reference owns prepare, manifest, capture, render, verify, cleanup,
  durable handoff, and completion-aware waiting.
- `reviewer-routing.md` owns only family and authentication routing.
- `leg-contracts.md` owns only provider-specific argv and terminal receipt handling.
- `review-prompt-contract.md` owns only reviewer instructions and the `LegVerdict`
  output contract.
- `review_round.py` owns packet structure, manifest/digest generation, render-time
  binding, schema validation, and integrity checks.

The leader supplies semantic inputs such as the task, criteria, approved paths, base,
candidate, and diff scope. The tool derives mechanical identifiers and rejects any
mismatch. Tests assert generated structures and decision tables instead of pinning the
same prose in several files.

## Immutable review basis

The prepared directory remains the only source input for external formal reviewers.
It contains:

- `shared/source/product/` with the exact owner-approved related files;
- leader-generated `REVIEW.diff` for the declared base, candidate, and scope;
- `TASK.md` with objective, criteria, boundaries, exclusions, and the exact Git argv;
- optional bounded `EVIDENCE.md`;
- `SOURCE_SHA256SUMS`, generated last.

`capture` remains the only source of `basis_digest`. Every rendered prompt and every
receipt binds that digest plus the review ID and leg ID. After all legs terminate,
`verify` compares both the prepared snapshot and canonical worktree state before any
receipt is admitted. `cleanup` removes only the exact managed review root.

The packet includes the diff and related unchanged files because a diff alone can hide
caller, schema, or invariant context. It excludes repository-wide enumeration,
credentials, provider logs, unrelated paths, and any file merely named by untrusted
review content.

## Dispatch and waiting

Each required leg receives the same captured prepared directory and an independently
rendered prompt whose variable fields come from the same contract. Provider processes
start without exposing one result to another.

Long-running wrapper calls keep their original process/session handle. The leader uses
completion-aware waits on that handle and relies on atomic structured result files as
the durable completion proof. Elapsed waits are not failures, and lost conversational
handles do not cause duplicate dispatch; recovery starts from the workspace-owned
handoff and result artifacts.

## Prompt shape

The common prompt is outcome-first: review the approved basis against the criteria and
return one bound `LegVerdict`. Provider-specific references add only capability and
containment details that differ by family. Long packet context precedes the final
review instruction. The renderer uses argv arrays and explicit files; user-controlled
text never becomes shell syntax.

## Alternatives considered

1. Keep all current prose and only shorten `SKILL.md`. This leaves contradictory copies
   and does not reduce maintenance cost.
2. Send only a diff plus a digest. This saves bytes but prevents reviewers from reading
   affected unchanged context, weakening the original TRIAD review goal.
3. Replace the existing lifecycle with a new orchestration framework. This duplicates
   proven machinery and creates a second integrity protocol.

The selected approach changes presentation and mechanical ownership, not review
semantics or provider routing.

## Non-goals

- No new provider, model, authentication, fallback, retry, or repair behavior.
- No permanent five-leg composition.
- No host permission installation; that is a dependent post-release design.
- No retained source archive.
- No weakening of fail-closed round invalidation, mutation checks, or receipt binding.

## Verification

Implementation follows the skill-development RED/GREEN protocol with fresh
`triad-skill-executor` instances. Focused tests must prove identical packet membership,
trusted diff provenance, one captured digest, same-basis prompt rendering, schema-bound
receipts, completion-aware result collection, post-run integrity, and exact cleanup.
The full regression suite, skill validator, prompt linter/review, clean distribution
verification, installed-byte equality, and fresh-process discovery remain separate
release evidence.
