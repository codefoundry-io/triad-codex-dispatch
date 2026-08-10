# Operational TRIAD Prompt Ownership Design

Date: 2026-08-11

## Goal

Restore the existing TRIAD contract: the Codex leader selects review points from the current task,
diff, governing decisions, and affected contracts, while deterministic tooling only binds that
leader-authored brief to common custody, containment, and result-shape instructions.

One behavioral claim defines this S/M slice:

> An operational TRIAD round carries one situation-specific, leader-authored brief to all three
> families without inserting a prompt-review meta-round.

## Existing contract

The worktree-first design already assigns the leader the worktree, scope, objective, suspect
decisions, and trusted status/diff. Reviewers independently trace the changed decisions into
affected unchanged surfaces. The current renderer similarly accepts objective, criteria, and
boundary as leader inputs; it serializes them but does not decide them.

The 2026-08-11 owner clarification is therefore a restoration constraint, not a new review model:

- review points remain situation-specific leader judgment;
- reviewers retain independent search and finding authority;
- mechanical rendering never invents, selects, ranks, or broadens review points; and
- `skill-prompt-review` is never a prerequisite, child phase, or recursive gate of an operational
  three-family review.

The owner separately approved an explicit-only discovery boundary for the personal
`skill-prompt-review` installation. Its frontmatter description may trigger only when the user
directly invokes that skill or explicitly requests a prompt/skill best-practices review. Merely
authoring, editing, or dispatching a prompt or skill is not a trigger.

## Failure to correct

Argus explicitly selects worktree-first review while the current packaged renderer describes an
immutable prepared directory. The leader manually authored worktree prompts to bridge that local
override. The broad `skill-prompt-review` trigger then treated those operational prompts as new
artifacts requiring fresh-eye review. Two completed prompt-review children and one interrupted
child consumed review effort before any Claude, Google, or fresh Codex product-review leg started.

The prompt reviewers found omissions that the prepared-directory renderer normally prevents,
including the missing `LegVerdict` shape. Those omissions show that the worktree envelope needs
deterministic rendering; they do not justify generating the substantive review brief or adding a
meta-review phase.

## Considered approaches

### 1. Leader-authored brief with a deterministic worktree envelope — selected

Add a worktree-specific rendering entry point beside the existing prepared-directory renderer.
The leader supplies the exact objective, criteria, review points, approved boundary, worktree,
fingerprint, and trusted task/status/diff locations. The renderer validates and serializes those
values, adds the fixed no-edit/no-execution and `LegVerdict` contracts, and changes none of the
leader-authored semantics.

This removes the omissions that caused the meta-review loop without replacing review judgment.
It also leaves prepared-directory review unchanged.

### 2. Continue authoring complete prompts manually — rejected

This is the smallest source change but repeats schema, custody, and authority wording by hand in
every round. The observed missing-schema defect demonstrates that it is not a reliable operating
boundary.

### 3. Generate review points from the diff — rejected

Automatic focus selection would turn a decision review into a generic checklist, could miss the
owner-approved behavioral decision, and would improperly move review judgment from the leader to
the transport layer.

## Components

### Explicit-only prompt-review activation

Change only the `description` field in
`/Users/chaniri/.codex/skills/skill-prompt-review/SKILL.md`. Keep the skill name, body, references,
scripts, and user-global settings unchanged. The description must state both positive explicit
triggers and the negative non-trigger for ordinary authoring, editing, and dispatch.

This is a separately testable configuration slice. It precedes the operational TRIAD correction
so later work does not re-enter prompt meta-review automatically. Because the owner named the exact
outside-workspace target, delta, and impact in the current conversation, this one frontmatter edit
is within the approved hard user-environment boundary.

### Worktree review brief

Add a typed worktree brief containing only leader inputs:

- review ID, kind, and family;
- objective and acceptance criteria;
- exact situation-specific review points;
- approved data and test-source boundary;
- canonical worktree and guarded fingerprint; and
- canonical current-round task, status, and diff files inside that worktree plus their content
  digests.

The objective, criteria, and review points must be non-empty. Validation checks shape and custody;
it does not judge whether the selected review points are good.

Complete those custody files before the pre-review fingerprint; the renderer rejects a custody file
outside the canonical worktree so every reviewer running with that worktree as its read boundary can
open it. Keep prompts, provider logs, and results in the exact current-round temporary root outside
the worktree. Capture the worktree fingerprint once before rendering and once after all legs terminate. The
renderer consumes the captured value without rehashing the worktree separately for each family;
this preserves one shared boundary and avoids repeated reads of large untracked files.

### Worktree prompt renderer

Add a separate `render-worktree` lifecycle command rather than weakening or overloading the current
prepared-directory `render` contract. Its output contains:

1. one canonical metadata record with the exact leader-authored brief;
2. fixed instructions distinguishing authenticated custody files from evidentiary authority;
3. the worktree read/search and no-edit/no-execution contract;
4. the exact `LegVerdict` keys and value shapes; and
5. a terminal instruction to return one verdict without asking how to proceed.

The renderer must preserve every review-point string exactly. It must not add generic review
criteria, infer related paths, summarize the brief, or dispatch a provider.

### Operational non-recursion rule

The TRIAD skill owns its operational provider prompts. Add an explicit rule that
`skill-prompt-review` is not invoked before or during an operational round. Reviewing the TRIAD
skill or its prompt implementation remains a separate maintenance task only when the owner
explicitly requests that task; it is never nested into the product review being dispatched.

The only pre-dispatch prompt check is one deterministic renderer/contract-validation pass. A
mechanical failure stops dispatch and is fixed as a workflow defect. A successful render proceeds
directly to the three provider legs.

### Argus routing

Update the Argus worktree-review guide to call `render-worktree` and to preserve its existing
model, containment, fingerprint, and independent-inspection rules. The guide supplies the current
task's leader-authored brief; it does not add a static universal set of review points.

## Data flow

```text
current task + governing decisions + trusted diff
                 |
                 v
       Codex leader writes review brief
                 |
                 v
   render-worktree validates and wraps only
                 |
                 v
 Claude + Google + fresh Codex inspect independently
```

No prompt-review agent or prompt-review round exists in this flow.

## Failure handling

- Missing or empty leader review points: stop before dispatch and complete the brief.
- Task, status, or diff outside the canonical worktree: fail mechanically before dispatch.
- Invalid path, digest, family, review ID, or fingerprint shape: fail mechanically before dispatch.
- Renderer or contract-validation failure: invalidate the attempted setup and use a fresh review ID
  after the bounded workflow correction.
- Provider refusal, malformed result, route mismatch, mutation, or prohibited execution: preserve
  the existing required-leg invalidation rules.
- Review finding: reproduce it against the guarded worktree; never treat it as automatic edit
  authority.

## Tests

TDD adds focused tests proving:

- a worktree prompt preserves leader-authored objective, criteria, and review points exactly;
- changing the leader review points changes only the corresponding metadata value;
- empty review points fail before output;
- a custody file outside the canonical worktree fails before output;
- all three family prompts carry the same task values and family-specific identity;
- the complete `LegVerdict` shape and custody-versus-authority wording are present;
- prepared-directory rendering remains byte-for-byte unchanged; and
- the skill and Argus guide explicitly prohibit operational `skill-prompt-review` recursion.

No provider call is part of the unit-test phase.

## Slice-size budget

Classification: two sequential review units.

Explicit-only activation slice:

- Forecast production net delta: zero lines; one frontmatter configuration line changes.
- Forecast novel algorithmic core: zero lines.
- Behavioral-claim count: one — prompt review triggers only on an explicit user request.

Operational TRIAD correction slice: S/M.

- Forecast production net delta: approximately 150–250 lines, below the 500-line default and
  800-line ceiling.
- Forecast novel algorithmic core: at most 100 lines.
- Behavioral-claim count: one.
- Tests and documentation are outside the production-line budget.
- No new semantic model, provider route, permission mode, or external configuration is introduced.

## Acceptance criteria

- The installed `skill-prompt-review` description selects only explicit user invocation or an
  explicit prompt/skill review request and rejects incidental authoring/editing/dispatch as a
  trigger.
- The leader, not the renderer, selects every substantive review point.
- Rendered prompts preserve the exact leader brief and contain a complete result contract.
- Operational TRIAD review never invokes `skill-prompt-review`.
- One successful mechanical render/validation is followed directly by the three provider legs.
- Default prepared-directory behavior and existing provider routing remain unchanged.
- The Argus review uses a fresh ID and an unchanged pre/post worktree fingerprint.
