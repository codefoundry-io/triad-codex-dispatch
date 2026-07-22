# Formal Review Routing Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every bounded formal review resolve the owner's proven Terra/Opus/Gemini routes while retaining Sol/Fable as recorded escalation options and preserving code-complete impact review.

**Architecture:** Keep transport wrappers caller-selectable. Put review-only selection rules in one progressively disclosed routing reference, link it from the cross-family skill, and place exact route arguments in the three load-bearing formal invocation examples. Lock the contract with a distribution test and prove behavior with fresh-context use probes.

**Tech Stack:** Markdown Agent Skills, Python 3.12, pytest, Codex native `spawn_agent`, Claude/Antigravity wrapper argv.

## Global Constraints

- Treat `gpt-5.6-terra`/`xhigh`, Claude `opus`/`xhigh`, and agy `gemini-3.1-pro-high` as owner routing policy, not vendor capability facts.
- Before formal Google dispatch, require authenticated `agy models` evidence
  for the exact selector. Treat sealed packet/argv preflight as packet, argv,
  and schema proof only; require actual provider acceptance and honest handling
  of exposed or `unexposed` effective-model metadata.
- Preserve Sol/Fable as explicit options for ambiguous, security-sensitive, deeply integrative, or adjudication-heavy review; record the exact route and rationale.
- Preserve the existing code-complete snapshot and affected caller/test/schema/configuration/unchanged-consumer trace; the diff remains navigation only.
- Preserve `_runs/reviews/20260722-triad-reliability-formal-r14` unchanged.
- Do not reinstall, invoke external providers, modify version/changelog, release, open a pull request, modify `/Users/chaniri/triad-codex-dispatch`, commit, or push without a separate owner decision for this new change.

---

### Task 1: Lock the missing routing contract with TDD

**Files:**
- Modify: `tests/test_distribution_contract.py`
- Test: `tests/test_distribution_contract.py`

**Interfaces:**
- Consumes: existing `REVIEW_SKILL`, `FRESH_CODEX_REVIEW_REFERENCE`, and `PROVIDER_SKILLS` path constants.
- Produces: `REVIEW_ROUTING_REFERENCE` and `test_formal_review_uses_owner_routing_baseline_and_bounded_escalation()`.

- [x] **Step 1: Preserve the no-guidance baseline**

Record the completed fresh-context probe result: Codex model/effort, Claude model/effort, Google model, and deeper-model escalation rule were all `UNDETERMINED` when the agent followed only the unchanged skill and its directed references.

Actual: the no-guidance baseline was `UNDETERMINED` for all required route
fields and the deeper-model escalation rule.

- [x] **Step 2: Write the failing regression test**

Add the routing reference path beside the other review references:

```python
REVIEW_ROUTING_REFERENCE = (
    ROOT
    / "skills"
    / "triad-cross-family-review"
    / "references"
    / "reviewer-routing.md"
)
```

Add this test near the other formal-review contract tests:

```python
def test_formal_review_uses_owner_routing_baseline_and_bounded_escalation(
) -> None:
    review_skill = _text(REVIEW_SKILL)
    routing = _text(REVIEW_ROUTING_REFERENCE)
    fresh_codex = _text(FRESH_CODEX_REVIEW_REFERENCE)
    claude = _text(PROVIDER_SKILLS[0])
    antigravity = _text(PROVIDER_SKILLS[1])

    assert REVIEW_ROUTING_REFERENCE.is_file()
    assert "[formal reviewer routing contract]" in review_skill
    assert "completely before resolving any reviewer model" in review_skill
    assert 'model="gpt-5.6-terra"' in fresh_codex
    assert 'reasoning_effort="xhigh"' in fresh_codex
    assert '"--model", "opus",' in claude
    assert '"--effort", "xhigh",' in claude
    assert '"--model", "gemini-3.1-pro-high",' in antigravity

    flat = " ".join(routing.split())
    for phrase in (
        "owner routing policy, not a vendor capability claim",
        "ambiguous",
        "security-sensitive",
        "deeply integrative",
        "adjudication-heavy",
        "does not itself invalidate the review",
        "exact route and rationale",
        "Do not silently substitute",
    ):
        assert phrase in flat
```

- [x] **Step 3: Run the test and verify RED**

Run from `/Users/chaniri/codex_workspace` in the user's login shell:

```bash
python3 -m pytest /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py::test_formal_review_uses_owner_routing_baseline_and_bounded_escalation -q
```

Expected: FAIL because `reviewer-routing.md` does not exist.

Actual: the focused test failed for the missing `reviewer-routing.md` reference.

### Task 2: Implement the minimum review-only routing policy

**Files:**
- Create: `skills/triad-cross-family-review/references/reviewer-routing.md`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `skills/triad-cross-family-review/references/fresh-codex-formal-review.md`
- Modify: `skills/triad-claude-dispatch/SKILL.md`
- Modify: `skills/triad-antigravity-dispatch/SKILL.md`
- Modify: `bin/claude_wrapper.py`

**Interfaces:**
- Consumes: owner-selected model routes and existing formal packet/identity contracts.
- Produces: one routing decision record per review ID and exact model/effort argv for each default leg.

- [x] **Step 1: Add the routing reference**

The reference must define the bounded-review baseline, distinguish local policy from vendor facts, require live route proof and no silent substitution, define the four escalation predicates, and state that Sol/Fable selection is valid when recorded.

- [x] **Step 2: Make the cross-family skill load the reference**

Before provider resolution, require the leader to read the complete reference, resolve all routes, and archive the routing decision with the rendered prompts. Keep the skill body at or below its existing 200-line progressive-disclosure limit.

- [x] **Step 3: Put exact routes in executable examples**

Use these exact fields:

```python
model="gpt-5.6-terra"
reasoning_effort="xhigh"
```

```python
"--model", "opus",
"--effort", "xhigh",
```

```python
"--model", "gemini-3.1-pro-high",
```

For the Google leg, authenticate `agy models` discovery before formal dispatch.
Packet/argv preflight remains mandatory but does not prove availability. Archive
actual provider acceptance and exposed effective identity; record absent
telemetry once as `unexposed`. Selector absence/rejection or an exposed conflict
leaves the leg missing or invalid.

- [x] **Step 4: Correct wrapper help semantics**

Keep `--model` free-form and caller-selected. Direct formal-review callers to the cross-family routing contract without claiming Fable is incapable of review.

- [x] **Step 5: Run the focused test and verify GREEN**

Run the Task 1 command again. Expected: `1 passed`.

Actual: focused GREEN result was `1 passed`; wrapper defaults remain
caller-selected.

### Task 3: Verify distribution and real skill behavior

**Files:**
- Modify: `docs/status/2026-07-22-current-state.md`
- Modify: `docs/status/2026-07-22-resume-prompt.md`
- Create: a routing-specific verification record under `docs/status/`

**Interfaces:**
- Consumes: green source tree, prior immutable R14 evidence, and the existing snapshot closure helper.
- Produces: fresh deterministic test evidence and fresh-context routing proof;
  after owner authorization and completion of Step 3, also produces a new
  immutable review ID and verdict.

- [x] **Step 1: Run deterministic validation**

From `/Users/chaniri/codex_workspace`, record `command -v python3`, `python3 --version`, and `python3 -m pytest --version`, then run:

```bash
python3 -m pytest /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -q
python3 -m pytest /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/tests -q
```

Run the skill validator and `skill-prompt-review` linter against every touched skill or prompt file. Confirm the cross-family skill body remains at or below 200 lines.

Actual: focused `1 passed`, distribution `53 passed`, and final post-correction
full suite `609 passed, 6 subtests passed in 138.06s`. Post-correction
Antigravity `quick_validate` reported `Skill is valid!`. Post-correction prompt
lint produced only the same Sol/Fable C8 candidate; the prior two semantic
reviews adjudicated the verified router/config context `APPROVED`.

- [x] **Step 2: Forward-test without leaked expected output**

Start a fresh `fork_turns="none"` Codex agent and ask it to use the finished skill to prepare a bounded formal routing record. It must return the exact three routes and the conditional escalation rule without consulting tests, history, wrapper help, or prior verdicts.

- [ ] **Step 3: Freeze and review the changed bytes**

Create a new review ID without altering R14. Include the code-complete snapshot, full diff, tests, design, plan, official model-guidance evidence, and routing probe. Run all required independent family legs over identical immutable inputs when owner authorization and provider availability cover the dispatch. Reconcile evidence rather than votes.

- [x] **Step 4: Update the handoff**

Record local/upstream `80f7a57` as the completed prior publication, list the new
uncommitted routing files and exact verification results, and either name the
fresh review ID and verdict when they exist or explicitly record their absence
while the formal gate remains pending. Keep
reinstall/version/changelog/release/PR plus commit/push pending their respective
owner decisions.

Actual: the post-fix fresh behavioral probe read neither tests nor history and
invoked no providers. It independently recovered the exact routes,
authenticated `agy models` discovery, preflight limitation, provider
acceptance/effective-metadata handling, impact scope, and convergence. It
correctly withheld `FORMAL PASS` because real receipts, providers, and formal
native legs were not permitted; this is successful fail-closed contract
comprehension, not a formal verdict or product failure. The Important Google
proof gap and Minor plan inconsistency found by final whole-change review were
corrected and closed by the local sealed Codex closure re-review. Its verified
75-file read-only snapshot had manifest SHA-256
`ef8e1a947b7908ee108adb23e1962a34e2ebc72fa64393e669dac0855b2558a4`;
the result was `APPROVED` with no Critical, Important, or Minor findings. The
requested reviewer route was Terra/xhigh; actual model/effort metadata was
unexposed. The reviewer found the source ready for the pending immutable
external formal gate, but this is not authorization, merge/release readiness,
or a formal three-family verdict. These handoff edits postdate the approved
snapshot and require a final doc-only closure check. No formal review ID or
verdict exists: Step 3 freeze and external three-family dispatch remain
unchecked and require separate owner authorization and identical immutable
inputs. Handoff updated.
