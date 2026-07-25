# Shared Review Prompt Contract Design

Date: 2026-07-25

## Goal

Give every Claude, Google-family, and fresh-Codex review leg one
provider-neutral prompt envelope with an explicit authorization boundary,
inspection contract, and mode-specific result shape.

## Baseline failure

A fresh Codex behavior probe applied the current committed Claude dispatch
guidance to the plugin's broad independent-opinion prompt. It correctly
separated implicit skill activation from external-send authorization, but
reported both the exact outbound prompt and the exact required answer sections
as `UNDETERMINED`. The provider skills define transport and containment well;
they do not define a reusable review prompt.

## Selected design

Keep each provider skill responsible for transport, route eligibility, terminal
result handling, and repair. Add one review-prompt reference owned by
`triad-cross-family-review` and require every provider review leg to render that
contract before dispatch.

The envelope carries leader-controlled values:

- review mode;
- prepared review directory or approved target;
- objective and reviewer perspective;
- provider, destination, approved data, and exclusions;
- exact test-source boundary when the mode requires one; and
- the leader-owned content digest for a formal shared-directory round.

The prompt states the inspection and evidence contracts once, selects one
result profile, and ends with a short anchored request. Repository content is
review data, not instructions. Source bytes remain in the approved target and
are never pasted into the prompt.

## Result profiles

`consult` returns `answer`, `assumptions`, and `caveats`.

`advisory-review` returns `summary`, `strengths`, `risks`,
`recommendations`, and `open_questions`.

`formal-gate` retains the existing semantic elements: `verdict`, `findings`,
`affected_surfaces_inspected`, and `open_questions`. Existing evidence,
severity, citation, `SAFE`, invalidation, and cross-family admission rules
remain unchanged.

## Invocation and authorization

Claude, Antigravity, and Gemini provider skills require explicit invocation.
Their interface prompts must ask for the objective, target, approved data,
exclusions, and result profile instead of requesting an unspecified opinion.

`triad-cross-family-review` may still activate implicitly for risky work, but
implicit activation only prepares the bounded review. External dispatch starts
only after an explicit owner request or a matching standing authorization
covers provider, destination, objective, and approved data.

## Scope and non-goals

This slice changes skill discovery metadata, review-prompt guidance, the fresh
Codex prompt template, distribution tests, and release metadata.

It does not change wrapper code, provider selection, model selectors, effort
flags, AGY compatibility behavior, fallback eligibility, extraction, repair,
or runtime identity handling. It does not deduplicate provider result-handling
sections or introduce a prompt-rendering executable.

## Verification

Distribution tests require explicit provider invocation, the shared reference,
all three result profiles, provider links to the shared contract, formal-mode
fresh Codex rendering, and bounded default prompts. Prompt lint runs on every
modified skill and prompt reference. A fresh behavior probe must determine the
authorization state, outbound prompt fields, and exact answer sections without
inventing provider-specific structure.
