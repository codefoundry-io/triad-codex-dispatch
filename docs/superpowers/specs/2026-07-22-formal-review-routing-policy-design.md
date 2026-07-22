# Formal Review Routing Policy Design

Date: 2026-07-22

## Goal

Make the cross-family review skill select the owner's proven bounded-review
routes consistently while preserving deeper models as explicit escalation
options rather than incorrectly describing them as review-ineligible.

## Approved behavior

For a bounded formal three-family review, the routing baseline is:

- fresh Codex: `gpt-5.6-terra` with `xhigh` and `fork_turns="none"`;
- Claude: the owner-proven `opus` selector with `--effort xhigh`;
- primary Google-family route: agy `gemini-3.1-pro-high`.

This is an owner routing policy, not a vendor capability claim. The leader may
select a deeper or longer-horizon route, including a Sol- or Fable-class model,
for an ambiguous, security-sensitive, deeply integrative, or adjudication-heavy
review. The review record must identify the exact route and the reason. A
Sol/Fable selection does not itself invalidate a review.

The leader continues to decide convergence from frozen reproducible evidence.
An unresolved head-on contradiction or evidence-free oscillation remains
`CONFLICTED` and requires owner adjudication.

## Approaches considered

1. **Central routing contract plus executable examples — selected.** Add one
   progressively disclosed routing reference, require the cross-family skill to
   read it before resolving providers, and make each load-bearing example carry
   the selected model and effort. This keeps policy and invocation consistent.
2. **Wrapper help only.** This is too weak because the cross-family skill can
   dispatch without reading wrapper help and the Codex leg has no wrapper.
3. **Hard-coded wrapper defaults.** This would alter generic single-shot calls,
   silently override owner intent, and turn rotating model selectors into
   transport behavior rather than an explicit review decision.

## File responsibilities

- `skills/triad-cross-family-review/references/reviewer-routing.md` owns the
  review-only default, exception, availability, and recording rules.
- `skills/triad-cross-family-review/SKILL.md` requires that contract before
  provider resolution without expanding its already dense body.
- The fresh Codex, Claude, and Antigravity formal invocation examples carry the
  exact current owner-selected route.
- `bin/claude_wrapper.py` describes the flag without presenting the local route
  split as an Anthropic capability rule.
- `tests/test_distribution_contract.py` locks the link, exact route fields,
  escalation conditions, and non-prohibition language.
- The current-state and resume documents distinguish this new uncommitted work
  from the immutable R14 and approval-inheritance evidence.

## Verification

Use skill TDD: capture a fresh-agent baseline against the unchanged skill,
write and observe a failing distribution-contract test, implement the minimum
policy, then run the focused test, distribution contract, complete test suite,
skill lint/validation, and a fresh forward-use probe. Any changed reviewed byte
requires a new immutable formal review ID; R14 remains untouched history.

## External-state boundary

This design authorizes source, test, and handoff-document changes only. It does
not authorize reinstall, version or changelog changes, a release, pull-request
creation, or modification of `/Users/chaniri/triad-codex-dispatch`. Commit and
push for this new change remain a separate owner decision after fresh review.
