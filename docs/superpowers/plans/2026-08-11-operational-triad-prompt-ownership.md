# Operational TRIAD Prompt Ownership Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve situation-specific leader review judgment, make worktree prompt custody deterministic, and prevent `skill-prompt-review` from auto-triggering inside operational TRIAD review.

**Architecture:** First narrow the installed prompt-review discovery description to explicit user requests. Then add a separate worktree prompt renderer whose typed brief contains exact leader-authored review points and whose fixed envelope binds custody, fingerprint, containment, and `LegVerdict`; the prepared-directory renderer remains unchanged. Finally update the TRIAD skill and Argus guide to select this path and prohibit prompt meta-review.

**Tech Stack:** Python 3, `argparse`, `dataclasses`, SHA-256, pytest, Markdown skill contracts.

## Global Constraints

- The leader selects every substantive objective, criterion, and review point from the current task and evidence.
- The renderer preserves leader-authored values exactly and never generates, ranks, broadens, or summarizes review points.
- Operational TRIAD review never invokes `skill-prompt-review`.
- `skill-prompt-review` discovery triggers only on explicit user invocation or an explicit prompt/skill review request.
- Prepared-directory rendering, provider routing, model selection, permissions, and external configuration remain unchanged.
- Slice A is a one-line configuration change with zero novel core; Slice B is S/M with forecast production delta 150–250 lines, novel core at most 100 lines, and one behavioral claim.

---

### Task 1: Make prompt-review discovery explicit-only

**Files:**
- Modify: `/Users/chaniri/.codex/skills/skill-prompt-review/SKILL.md:1-4`
- Validate: `/Users/chaniri/.codex/skills/.system/skill-creator/scripts/quick_validate.py`

**Interfaces:**
- Consumes: Codex skill frontmatter discovery rules.
- Produces: one `description` that selects only explicit user invocation or an explicit request to review a prompt/skill.

- [ ] **Step 1: Record the Python environment required by the skill validator**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'command -v python3; python3 --version; python3 -c "import yaml; print(yaml.__version__)"'
```

Expected: login-shell `python3`, its version, and the installed PyYAML version.

- [ ] **Step 2: Run the explicit-only description assertion and verify RED**

Run:

```bash
rg -n '^description: Use only when the user explicitly' /Users/chaniri/.codex/skills/skill-prompt-review/SKILL.md
```

Expected: exit 1 because the current description still auto-triggers during ordinary authoring and revision.

- [ ] **Step 3: Replace only the frontmatter description**

Set the exact value to:

```yaml
description: Use only when the user explicitly invokes skill-prompt-review or explicitly requests a best-practices review of a SKILL.md or authored system, worker, or dispatch prompt. Do not trigger merely because a prompt or skill is being authored, revised, or used. For a sub-agent definition file (an agent `.md`), use its agent-definition review workflow instead.
```

- [ ] **Step 4: Verify GREEN and validate the skill folder**

Run:

```bash
rg -n '^description: Use only when the user explicitly' /Users/chaniri/.codex/skills/skill-prompt-review/SKILL.md
/bin/zsh -lic 'python3 /Users/chaniri/.codex/skills/.system/skill-creator/scripts/quick_validate.py /Users/chaniri/.codex/skills/skill-prompt-review'
```

Expected: the exact description is found and the validator reports a valid skill.

- [ ] **Step 5: Prove the change is limited to the approved field**

Record the pre/post SHA-256 of `SKILL.md`, extract the YAML frontmatter, and verify the body beginning at `# skill-prompt-review` is byte-identical to the saved pre-edit body. Do not edit any other file under `/Users/chaniri/.codex`.

- [ ] **Step 6: Run one bounded fresh-context trigger check**

Use one fresh low-cost default child with no inherited turns. Give it the final description plus two classification cases: ordinary dispatch-prompt authoring and an explicit request to run `skill-prompt-review`. Require `DO_NOT_LOAD` for the first and `LOAD` for the second, with no file edits or further agents. This is the explicit maintenance validation for Task 1; it is not part of an operational TRIAD round and must not repeat after a passing result.

---

### Task 2: Add the leader-authored worktree prompt envelope

**Files:**
- Modify: `bin/review_round.py:29-47,963-1035,1060-1150`
- Modify: `tests/test_review_round.py:18-27,2180-2540`

**Interfaces:**
- Consumes: `WorktreeReviewBrief(review_id, review_kind, family, objective, worktree, worktree_fingerprint, task_file, status_file, diff_file, criteria, review_points, approved_boundary)`.
- Produces: `render_worktree_review_prompt(brief: WorktreeReviewBrief) -> str` and CLI subcommand `render-worktree`.
- Binds: returned `content_digest` is SHA-256 over canonical common review inputs, excluding only `family`, so all three family prompts share one digest.

- [ ] **Step 1: Add a failing unit test for exact leader-value preservation**

Add imports for `WorktreeReviewBrief` and `render_worktree_review_prompt`, then add:

```python
def test_worktree_prompt_preserves_leader_authored_review_points(worktree, tmp_path):
    task = (worktree / "TASK.md").resolve()
    status = (worktree / "STATUS.txt").resolve()
    diff = (worktree / "REVIEW.diff").resolve()
    task.write_text("task\n", encoding="utf-8")
    status.write_text("status\n", encoding="utf-8")
    diff.write_text("diff\n", encoding="utf-8")
    brief = WorktreeReviewBrief(
        review_id="argus-r1",
        review_kind="pre-merge",
        family="google",
        objective="Decide whether the Task 4 implementation matches its approved contract.",
        worktree=worktree,
        worktree_fingerprint=review_round._worktree_fingerprint(worktree),
        task_file=task,
        status_file=status,
        diff_file=diff,
        criteria=("correctness", "compatibility"),
        review_points=("Trace the Task 4 state transition into every unchanged consumer.",),
        approved_boundary=("sanitized Argus worktree", "relevant tests"),
    )

    prompt = render_worktree_review_prompt(brief)
    metadata = _review_metadata(prompt)

    assert metadata["review_points"] == list(brief.review_points)
    assert metadata["objective"] == brief.objective
    assert metadata["worktree"] == str(worktree)
    assert metadata["family"] == "google"
    assert metadata["content_digest"] == metadata["worktree_review_digest"]
    assert "authenticated custody locations only" in prompt
    assert "Return exactly one JSON object matching verdict_schema:LegVerdict" in prompt
```

- [ ] **Step 2: Add failing rejection and cross-family digest tests**

Add tests proving an empty `review_points` tuple raises `RoundIntegrityError`, and identical common briefs for `claude`, `google`, and `codex` produce the same `content_digest` while preserving distinct `family` values.

- [ ] **Step 3: Run the focused tests and verify RED**

Run from the saved workspace root, per the Python boundary:

```bash
/bin/zsh -lic 'command -v python3; python3 --version; python3 -m pytest --version; python3 -m pytest /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/tests/test_review_round.py -k worktree_prompt -q'
```

Expected: collection/import failure because the new dataclass and renderer do not exist.

- [ ] **Step 4: Implement the minimal typed brief and renderer**

Add:

```python
@dataclass(frozen=True)
class WorktreeReviewBrief:
    review_id: str
    review_kind: Literal["formal-plan", "pre-merge", "implementation-review"]
    family: Literal["claude", "google", "codex"]
    objective: str
    worktree: Path
    worktree_fingerprint: str
    task_file: Path
    status_file: Path
    diff_file: Path
    criteria: tuple[str, ...]
    review_points: tuple[str, ...]
    approved_boundary: tuple[str, ...]
```

Implement canonical regular-file validation, require every task/status/diff file to be inside the canonical worktree, compute per-file SHA-256 and a canonical common-input digest, and add `render_worktree_review_prompt`. Reuse the exact existing `LegVerdict` shape and verdict semantics. Keep all dynamic values in one `Review metadata: ` JSON record. The fixed prose must direct reviewers to inspect the worktree independently and must state that task/status/diff paths establish custody, not truth.

- [ ] **Step 5: Verify GREEN**

Run the focused command from Step 3.

Expected: all selected worktree prompt tests pass.

- [ ] **Step 6: Add and test the CLI subcommand**

Add `render-worktree` with required repeated `--criterion`, `--review-point`, and `--approved-boundary` arguments plus required worktree/fingerprint/task/status/diff/output arguments. Add a subprocess test proving the output file contains the exact metadata and shared digest.

- [ ] **Step 7: Prove prepared-directory rendering did not regress**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/tests/test_review_round.py -q'
```

Expected: all `test_review_round.py` tests pass, including existing prepared-directory render tests.

---

### Task 3: Wire the operational non-recursion contract

**Files:**
- Modify: `tests/test_distribution_contract.py`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `/Users/chaniri/codex_workspace/workspace/Argus-codex/docs/guides/triad-review-dispatch-recovery.md`

**Interfaces:**
- Consumes: `render-worktree` from Task 2 and explicit owner/project worktree-first selection.
- Produces: durable selection and non-recursion instructions; no provider or permission changes.

- [ ] **Step 1: Add a failing distribution contract test**

Add:

```python
def test_cross_family_skill_owns_operational_prompts_without_meta_review() -> None:
    skill = _text(SKILLS / "triad-cross-family-review" / "SKILL.md")

    assert "render-worktree" in skill
    assert "project instructions explicitly select worktree-first review" in skill
    assert "Do not invoke `skill-prompt-review` before or during an operational round" in skill
    assert "proceeds directly to provider dispatch" in skill
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
/bin/zsh -lic 'python3 -m pytest /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -k owns_operational_prompts -q'
```

Expected: failure because the skill does not yet contain the selection and non-recursion contract.

- [ ] **Step 3: Add the minimal conditional flow to the TRIAD skill**

Keep prepared-directory review as the default. Add one observable conditional: when current owner or project instructions explicitly select worktree-first review, the leader authors the complete task-specific brief and invokes `render-worktree`. State that deterministic render validation proceeds directly to provider dispatch and that `skill-prompt-review` is not invoked before or during an operational round.

- [ ] **Step 4: Update the Argus recovery guide**

Replace manual full-prompt authorship with the canonical `render-worktree` call. Preserve Argus model, fingerprint, read/search, no-edit/no-execution, and worktree-relative finding rules. Require the leader to supply situation-specific review points; do not prescribe a universal checklist.

- [ ] **Step 5: Verify GREEN and documentation consistency**

Run the focused distribution test, `git diff --check` in both repositories, and an exact search confirming the Argus guide contains `render-worktree`, `review-point`, and the operational no-prompt-review rule.

---

### Task 4: Full local verification and commits

**Files:**
- Verify all files changed in Tasks 1–3.

**Interfaces:**
- Consumes: completed RED/GREEN evidence.
- Produces: verified TRIAD source commits and recorded installed-skill checksum; no release, install, or merge claim.

- [ ] **Step 1: Run the TRIAD full suite**

Run from the saved workspace root:

```bash
/bin/zsh -lic 'python3 -m pytest /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/tests -q'
```

Expected: zero failures.

- [ ] **Step 2: Validate skill packaging and diffs**

Run the skill folder validator, `git diff --check`, and the repository's documented distribution verifier if the test suite does not already execute it.

- [ ] **Step 3: Commit the TRIAD implementation intentionally**

Stage only `bin/review_round.py`, `tests/test_review_round.py`, `tests/test_distribution_contract.py`, `skills/triad-cross-family-review/SKILL.md`, and the plan/spec documentation. Commit with:

```bash
git commit -m "fix: keep operational triad prompts leader owned"
```

- [ ] **Step 4: Preserve the dirty Argus guide boundary**

The Argus guide was already modified before this implementation. Do not stage or commit it. Record the pre-edit file digest, apply only the bounded non-recursion/rendering amendment against its current bytes, and report that exact addition separately from the pre-existing user-owned diff.

---

### Task 5: Run the fresh operational Argus three-family review

**Files:**
- Read: current Argus worktree and a fresh workspace-managed temporary review root.
- Create inside the worktree before fingerprinting: current-round task/status/diff.
- Create in the temporary review root: rendered prompts, logs, and verdicts.

**Interfaces:**
- Consumes: verified `render-worktree`, leader-authored Task 4 review brief, Argus route rules.
- Produces: one Claude, one Google, and one fresh Codex `LegVerdict` for one fresh ID and digest.

- [ ] **Step 1: Prepare a fresh ID and leader-authored brief**

Write situation-specific objective, acceptance criteria, and review points from the current Argus Task 4 decision. Do not reuse the invalidated prompt-review setup or any prior verdict.

- [ ] **Step 2: Capture fingerprint and render once**

Create the trusted task/status/diff as canonical regular files inside the worktree, capture one pre-review fingerprint, and render all three prompts with `render-worktree`. Run only deterministic contract/schema checks; do not invoke `skill-prompt-review` or any prompt-review child.

- [ ] **Step 3: Start all three actual legs**

Launch Claude Opus/xhigh, AGY `gemini-3.1-pro-high`, and one fresh default Codex child with `fork_turns="none"`, `model="gpt-5.6-terra"`, and `reasoning_effort="xhigh"`. Do not consume a verdict until all three legs have started.

- [ ] **Step 4: Admit and verify**

Validate each result as `LegVerdict`, recompute the equal post-review fingerprint, reproduce every finding, and report the formal result. Any invalid required leg invalidates the round; do not substitute a prompt review or salvage a prior result.
