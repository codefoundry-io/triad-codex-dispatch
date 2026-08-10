# Formal Review Contract Remediation Implementation Plan

> Historical plan. Its `--formal-read-tools` and `--tools Read,Glob,Grep`
> instructions were superseded on 2026-08-08 by the owner's requirement to
> preserve provider-native, installed CLI, and configured MCP read/search tools.
> Do not execute those superseded steps; retain this file as the record of the
> earlier admitted round.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve user-configured Claude MCP inspection tools while keeping the formal route non-mutating, and make the review-directory manifest required everywhere that the inspection contract depends on it.

**Architecture:** Keep the existing formal argv `--tools Read,Glob,Grep`; Claude documents this as restricting only built-in tools, leaving configured MCP tools unaffected. Do not add `--safe-mode`, MCP configuration overrides, or new permission overrides. Existing user permissions continue to govern MCP calls, while the review contract permits in-boundary reads/searches and invalidates mutation or candidate execution. Resolve the packet-contract mismatch by adding `SOURCE_SHA256SUMS` as a structural member of every active prepared-directory recipe, then bind the distributed wording and verify it through one exact fresh-agent RED/GREEN scenario. Keep the owner-approved digest, 23 benchmark files, and record-only closure policy unchanged.

**Tech Stack:** Python 3.12, pytest, Claude Code CLI `>= 2.1.170`, Markdown agent skill, packaged TRIAD review tooling.

## Global Constraints

- Owner approval for the original remediation was given on 2026-08-08 after review round `20260808-triad-maintenance-premerge-r1` returned Claude `NOT-SAFE`. After formal-plan R3, the owner explicitly superseded the proposed MCP suppression: user-installed CLI tools must remain available, and only unintended mutation or candidate execution is prohibited.
- Keep `--formal-read-tools` as `--tools Read,Glob,Grep`. This restricts the built-in set only; do not add `--safe-mode`, `--strict-mcp-config`, `--mcp-config`, `--allowedTools`, or `--disallowedTools`.
- Preserve configured MCP servers and existing user permission settings. Permit their read/search operations only within the authorized review boundary; any mutation, external-state change, or candidate code/test/build/hook/script execution invalidates the leg.
- Require `SOURCE_SHA256SUMS` as a prepared-directory member; do not add a second digest algorithm or change `_prepared_digest`.
- Keep all 23 benchmark evidence files and do not add a closure-size ceiling.
- Do not implement MCP-process monitoring, a Claude version preflight, invalid-family generalization, or Google official-web wording change. MCP server startup is expected behavior, not a failed gate.
- Freeze all six pre-remediation dirty-file SHA-256 values from formal-plan R1:
  - `bin/claude_wrapper.py`: `6a345840d1f80f5eea1308d7ac6443a64801874e3d423e29b0de7f14aeb725f7`
  - `bin/review_round.py`: `22a5abcb44aae418f40a1ade60aa4ec75ef78d5d7080ffbadd3f0bb9c4f54490`
  - `skills/triad-cross-family-review/references/leg-contracts.md`: `56be0c592b9f6b03a3725cd93e4b5fb410327cd8eb725794085dd8c62bacd918`
  - `skills/triad-cross-family-review/references/review-prompt-contract.md`: `08573046035917b5f818098569a0a01dc9a6c86ff113d18d563d3278ad227eff`
  - `tests/test_provider_wrappers.py`: `7e7dce3b5352721931ded9eab733f220f15454087f751905331549b6db6bcc04`
  - `tests/test_review_round.py`: `1de3cc67b939d90a579f2c8cf4edf50626362823c5c7fdd523b856db593d5e59`
- Preserve `bin/claude_wrapper.py` at its frozen value. In `bin/review_round.py`, change only the Claude branch of `render_review_prompt`; keep `_prepared_digest`, capture, and verify behavior unchanged. In `tests/test_review_round.py`, change only the matching Claude-renderer regression. `tests/test_provider_wrappers.py` and `leg-contracts.md` may change only through Task 2; `review-prompt-contract.md` may change only through the approved Task 2 and Task 3 deltas.
- Do not commit, push, merge, install, tag, publish, or release without separate owner approval.
- Run every direct Python command through `/bin/zsh -lic` from `/Users/chaniri/codex_workspace` using literal `python3`.
- Run a fresh three-family formal-plan gate before Task 2 and a fresh three-family pre-merge gate after Task 5.

---

### Task 1: Freeze the reproduced design basis and pass the formal-plan gate

**Files:**
- Read: `_runs/reviews/20260808-triad-maintenance-premerge-r1/round-status.md`
- Read: `_runs/reviews/20260808-triad-formal-review-contract-plan-r1/round-status.md`
- Read: formal-plan R3, R4, and R5 result files plus leader adjudication
- Review: `docs/superpowers/plans/2026-08-08-formal-review-contract-remediation.md`

**Interfaces:**
- Consumes: the owner-approved R3 design correction, reproduced R4/R5 findings, and the current-skill fresh-agent RED result recorded below.
- Produces: one immutable formal-plan directory and unanimous admitted Claude, Google, and fresh Codex verdicts before product edits.

- [ ] **Step 1: Record the current-skill RED behavior**

Use this exact fresh-agent prompt, captured before any Task 3 skill edit:

```text
You are running one bounded RED characterization scenario for an existing skill. Inspect ONLY this file: /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/SKILL.md. Do not inspect any linked reference or any other file. Do not edit, create, delete, or execute repository files. Scenario: You are the review leader preparing the shared directory immediately before integrity capture. Based solely on mandatory preparation instructions in that SKILL.md, determine whether SOURCE_SHA256SUMS is a required member and enumerate the explicitly required named artifact members. Return EXACTLY one compact JSON object on one line with keys in this order: source_sha256sums_required (boolean), required_named_members (array of strings). No markdown and no explanation. The root leader will wait for and record your exact result.
```

Fresh default child `/root/manifest_skill_red_r4_basis`, requested as
`gpt-5.6-terra`/`medium`/`fork_turns=none`, returned exactly:

```json
{"source_sha256sums_required":false,"required_named_members":["TASK.md","one readable canonical diff"]}
```

The prompt and result embedded here are the durable baseline evidence. Do not regenerate a post-edit result and call it RED evidence.

- [ ] **Step 2: Bind the six pre-remediation hashes**

Copy the six literal values from Global Constraints into the next formal-plan packet and the later
pre-merge packet. Formal-plan R1 `SOURCE_SHA256SUMS` is their frozen source. Always label all six as
pre-remediation values; never present a post-edit recomputation as the frozen basis.

- [ ] **Step 3: Prepare one complete formal-plan directory**

Include this plan, both earlier R1 status records and results, formal-plan R3 and advisory R4/R5
results plus leader adjudication, the embedded RED prompt/result, all six frozen hashes, the active 0.2.533
release plan, current complete affected files and tests, all four public dispatch/review `SKILL.md`
files, governing docs, `TASK.md`, `SOURCE_SHA256SUMS`, and one readable canonical diff. Build the
allow-list from every file opened by the affected tests as well as the implementation closure.
Exact test-source exclusion: none. R4 is not an admission basis because it omitted three public
dispatch skills read by `test_formal_routes_are_explicit_and_reviewer_only`; its findings are
advisory and independently reproduced. R5 repaired that packet closure but is also advisory because
its prescribed renderer test could not reach GREEN and its change-boundary wording conflicted with
Task 3.

- [ ] **Step 4: Run the formal-plan review**

Use the installed packaged capture, schema-validation, convergence, and integrity workflow. Because
the installed Claude prompt renderer is the defect under review, render the R6 Claude prompt with
the exact owner-corrected inspection text specified in Task 2; keep it outside the prepared bytes
and record this bounded routing exception. Do not add `--safe-mode` or treat configured MCP startup
as failure. Dispatch Claude `opus`/`xhigh`, Google `gemini-3.1-pro-high`/`high`, and a fresh Codex
default child requested as `gpt-5.6-terra`/`xhigh`/`fork_turns=none` over the same directory, task,
criteria, and digest.

Expected: every required leg is schema-valid, integrity remains `ROUND_INTEGRITY_OK`, and all three return `SAFE` with no Critical/Major finding or open question.

### Task 2: Preserve configured MCP inspection while keeping the formal route non-mutating

**Files:**
- Modify: `bin/review_round.py:192-202`
- Modify: `tests/test_review_round.py:161-181`
- Modify: `tests/test_provider_wrappers.py:133-181`
- Modify: `tests/test_distribution_contract.py:78-99`
- Modify: `skills/triad-cross-family-review/references/leg-contracts.md:22-31`
- Modify: `skills/triad-cross-family-review/references/review-prompt-contract.md:22-31`
- Modify: `skills/triad-claude-dispatch/SKILL.md:25-26`

**Interfaces:**
- Consumes: `args.formal_read_tools: bool` and `ReviewBrief.family == "claude"`.
- Produces: formal argv containing `--tools Read,Glob,Grep` with no MCP-suppression or
  permission-override flags, plus a rendered prompt that permits configured in-boundary MCP
  read/search while invalidating mutation, external-state change, and candidate execution.
  Ordinary Claude argv remains byte-for-byte equivalent to the current route.

- [ ] **Step 1: Write the failing renderer and distributed-contract tests; bind argv exclusions**

Replace `test_rendered_claude_prompt_forbids_shell_fallback_and_prescribes_native_reads` with this
complete final test body:

```python
def test_rendered_claude_prompt_preserves_mcp_reads_and_forbids_mutation(prepared):
    brief = ReviewBrief(
        review_id="review-r1",
        review_kind="formal-plan",
        family="claude",
        objective="Check plan completeness.",
        prepared_dir=prepared,
        content_digest=_prepared_digest(prepared),
        criteria=("correctness", "completeness"),
        approved_boundary=("all prepared files",),
    )

    prompt = render_review_prompt(brief)

    assert "Treat the prepared directory as the only local filesystem input" in prompt
    assert "Start with provider-native Read of TASK.md and SOURCE_SHA256SUMS" in prompt
    assert "configured MCP read/search tools" in prompt
    assert "Configured MCP servers remain available" in prompt
    assert "Existing user permission settings continue to govern MCP calls" in prompt
    assert "Approved official-web reads through read-only MCP tools remain available" in prompt
    assert "Configured MCP server startup is expected" in prompt
    assert "Never invoke Bash, shell, command, terminal" in prompt
    assert "`find`, `true`" in prompt
    assert "one such call invalidates the leg" in prompt
    assert "mutation, external-state change" in prompt
    assert "candidate code, test, build, hook, or script execution" in prompt
    assert "do not substitute a shell command" in prompt
    assert "record the coverage limitation as an open question and finish the verdict" in prompt
    assert "outside the authorized boundary" in prompt
    assert "Use provider-native Read, Glob, and Grep only" not in prompt
    assert "use Glob or Grep only for prepared-directory navigation" not in prompt
```

In `test_formal_routes_are_explicit_and_reviewer_only`, load and whitespace-normalize
`review-prompt-contract.md` as well as `leg-contracts.md`, then assert:

```python
prompt_contract = _text(
    SKILLS
    / "triad-cross-family-review"
    / "references"
    / "review-prompt-contract.md"
)
compact_leg_contracts = " ".join(leg_contracts.split())
compact_prompt_contract = " ".join(prompt_contract.split())
for compact in (compact_leg_contracts, compact_prompt_contract):
    assert "Configured MCP servers remain available" in compact
    assert "Existing user permission settings continue to govern MCP calls" in compact
    assert "Approved official-web reads through read-only MCP tools remain available" in compact
    assert "do not substitute a shell command" in compact
    assert "record the coverage limitation as an open question and finish the verdict" in compact
assert "Read `TASK.md` and `SOURCE_SHA256SUMS` first" in compact_leg_contracts
assert "Start with `TASK.md` and `SOURCE_SHA256SUMS`" in compact_prompt_contract
assert "--formal-read-tools" in claude
```

In `test_claude_structured_route_uses_native_schema_once`, retain the existing exact `--tools`
assertion and add these exclusions:

```python
for forbidden in (
    "--safe-mode",
    "--strict-mcp-config",
    "--mcp-config",
    "--allowedTools",
    "--disallowedTools",
):
    assert not any(
        arg == forbidden or arg.startswith(f"{forbidden}=")
        for arg in calls[0]
    )
```

The existing `test_claude_route_forwards_model_effort_and_native_json` exact argv continues to
protect the ordinary route.

- [ ] **Step 2: Run the tests and verify RED**

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_rendered_claude_prompt_preserves_mcp_reads_and_forbids_mutation workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py::test_formal_routes_are_explicit_and_reviewer_only workspace/triad-codex-dispatch-reliability/tests/test_provider_wrappers.py::test_claude_structured_route_uses_native_schema_once -q'
```

Expected: `2 failed, 1 passed`. The renderer and distributed-contract nodes fail because the current
prompt says `Read, Glob, and Grep only` and the reference contracts lack the exact MCP-preservation
sentences. The argv-exclusion node is a regression guard and passes immediately.

- [ ] **Step 3: Align the runtime renderer and both exact reference contracts**

Change only the Claude `inspection_contract` branch in `render_review_prompt`. Keep the Codex and
Google branches, result schema, digest, capture, and verify code unchanged. Its final text must:

- treat the prepared directory as the only local filesystem input and forbid other local paths;
- start with `TASK.md` and `SOURCE_SHA256SUMS`;
- allow built-in `Read`, `Glob`, and `Grep` plus configured MCP read/search tools when their input
  stays inside the authorized review data boundary;
- allow approved official-web reads through read-only MCP tools when the objective and authorized
  external data boundary permit them;
- leave existing user permission settings in control and state that MCP server startup is expected;
- invalidate mutation, external-state change, shell/command/notebook use, empirical execution, and
  candidate code/test/build/hook/script execution; and
- turn evidence outside the authorized boundary into an open question.

Use this exact Claude branch body so the RED/GREEN assertions are deterministic:

```python
inspection_contract = (
    "Treat the prepared directory as the only local filesystem input. Do not inspect canonical "
    "worktrees or other local paths. Start with provider-native Read of TASK.md and "
    "SOURCE_SHA256SUMS. Use Claude's built-in Read, Glob, and Grep plus configured MCP read/search "
    "tools when their input stays within the authorized review data boundary. Configured MCP "
    "servers remain available. Existing user permission settings continue to govern MCP calls. "
    "Approved official-web reads through read-only MCP tools remain available when the review "
    "objective and authorized external data boundary permit them. "
    "Configured MCP server startup is expected and does not itself invalidate the leg. Never invoke "
    "Bash, shell, command, terminal, notebook, or execution tools, including `find`, `true`, "
    "run_command, command_status, send_command_input, or notebook_execution; one such call invalidates "
    "the leg. Do not use any tool for mutation, external-state change, or candidate code, test, build, "
    "hook, or script execution. If a built-in inspection tool is unavailable, do not substitute a "
    "shell command; record the coverage limitation as an open question and finish the verdict. If "
    "required evidence is outside the authorized boundary, record the limitation as an open "
    "question and finish the verdict. Do not create scratch projects or perform empirical "
    "execution. "
)
```

Replace the complete explanatory prose after the Claude command and before `## Google family` in
`leg-contracts.md` with this exact text:

```markdown
Claude receives no implementation task. Its terminal validated JSON is the
Claude leg result. The formal Claude leg uses the explicit 1,800-second
end-to-end wrapper deadline; shorter polling waits are wake-up boundaries, not
provider failures. `--formal-read-tools` passes `--tools Read,Glob,Grep`, which
restricts only Claude's built-in tool set. Configured MCP servers remain
available. Existing user permission settings continue to govern MCP calls.
Approved official-web reads through read-only MCP tools remain available when
the review objective and authorized external data boundary permit them. Read
`TASK.md` and `SOURCE_SHA256SUMS` first. Built-in reads/searches and configured
MCP read/search tools may be used only within the authorized review data
boundary. Mutation, external-state change, shell/command/notebook use,
empirical execution, or candidate code, test, build, hook, or script execution
through any tool invalidates the leg. Configured MCP server startup alone is
expected and does not invalidate the leg. If required evidence is outside the
authorized boundary, record the limitation as an open question and finish the
verdict. If a built-in inspection tool is unavailable, do not substitute a
shell command; record the coverage limitation as an open question and finish
the verdict.
```

Replace the complete Claude paragraph in `review-prompt-contract.md` with this exact text:

```markdown
Treat the prepared directory as the only local filesystem input. Do not inspect
a canonical worktree or another local path. Start with `TASK.md` and
`SOURCE_SHA256SUMS`. Claude's wrapper restricts only its built-in tool set to
`Read`, `Glob`, and `Grep`. Configured MCP servers remain available. Existing
user permission settings continue to govern MCP calls. Approved official-web
reads through read-only MCP tools remain available when the review objective
and authorized external data boundary permit them. Claude may use built-in
reads/searches and configured MCP read/search tools only within the authorized
review data boundary. It must not use any tool for mutation, external-state
change, shell/command/notebook use, empirical execution, or candidate code,
test, build, hook, or script execution; one such action invalidates the leg.
Configured MCP server startup alone is expected and does not invalidate the
leg. If required evidence is outside the authorized boundary, record the
limitation as an open question and finish the verdict.
If a built-in inspection tool is unavailable, do not substitute a shell
command; record the coverage limitation as an open question and finish the
verdict.
```

Do not change `bin/claude_wrapper.py`. In `skills/triad-claude-dispatch/SKILL.md`, add
`--formal-read-tools` to the existing formal-route flag sentence and make no other change.

- [ ] **Step 4: Verify GREEN and ordinary-route preservation**

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_round.py::test_rendered_claude_prompt_preserves_mcp_reads_and_forbids_mutation workspace/triad-codex-dispatch-reliability/tests/test_provider_wrappers.py::test_claude_route_forwards_model_effort_and_native_json workspace/triad-codex-dispatch-reliability/tests/test_provider_wrappers.py::test_claude_structured_route_uses_native_schema_once workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py::test_formal_routes_are_explicit_and_reviewer_only -q'
```

Expected: `4 passed`.

### Task 3: Make the checksum manifest a structural skill requirement

**Files:**
- Modify: `tests/test_distribution_contract.py`
- Modify: `skills/triad-cross-family-review/SKILL.md:40-43`
- Modify: `skills/triad-cross-family-review/references/review-prompt-contract.md:16-18`
- Modify: `docs/superpowers/plans/2026-08-05-triad-0.2.533-owner-decisions-and-release.md:305-307`
- Verify: the exact RED prompt/result embedded in Task 1

**Interfaces:**
- Consumes: the existing Claude prompt requirement to read `SOURCE_SHA256SUMS` first.
- Produces: a preparation recipe whose `SOURCE_SHA256SUMS` lists every other regular file before capture and dispatch.

- [ ] **Step 1: Write the failing distribution-contract test**

Add a dedicated package assertion:

```python
def test_cross_family_skill_requires_the_review_source_manifest() -> None:
    skill = " ".join(_text(SKILLS / "triad-cross-family-review" / "SKILL.md").split())
    prompt_contract = " ".join(_text(
        SKILLS / "triad-cross-family-review" / "references" / "review-prompt-contract.md"
    ).split())
    release_plan = " ".join(_text(
        ROOT / "docs" / "superpowers" / "plans"
        / "2026-08-05-triad-0.2.533-owner-decisions-and-release.md"
    ).split())

    required_members = "`TASK.md`, `SOURCE_SHA256SUMS`, and one readable canonical diff"
    explicit_named_members = (
        "The required named artifacts are exactly `TASK.md`, "
        "`SOURCE_SHA256SUMS`, and one readable canonical diff."
    )
    assert required_members in skill
    assert explicit_named_members in skill
    assert required_members in prompt_contract
    assert required_members in release_plan
    inventory_rule = "one sorted SHA-256 line for every other regular file"
    assert inventory_rule in skill
    assert inventory_rule in prompt_contract
    assert inventory_rule in release_plan
```

- [ ] **Step 2: Run the test and verify RED**

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py::test_cross_family_skill_requires_the_review_source_manifest -q'
```

Expected: FAIL because the skill and prompt recipes omit the manifest, while the active release
recipe omits both the manifest member and its sorted-inventory rule.

- [ ] **Step 3: Add the minimal structural requirement**

Set Flow step 2 to this required shape:

```markdown
2. **Prepare once.** Create one directory containing complete current files
   relevant to the decision, governing documentation, and the required named
   artifacts. The required named artifacts are exactly `TASK.md`,
   `SOURCE_SHA256SUMS`, and one readable canonical diff.
   `SOURCE_SHA256SUMS` contains one sorted SHA-256 line for every other regular
   file in the prepared directory. Prompts name the directory; they do not
   inline file bodies.
```

Replace the prompt-contract composition paragraph with:

```markdown
The prepared directory contains complete current files relevant to the decision,
governing documentation, `TASK.md`, `SOURCE_SHA256SUMS`, and one readable
canonical diff. `SOURCE_SHA256SUMS` contains one sorted SHA-256 line for every
other regular file in the prepared directory. The diff is a navigation entry
point, not an inline prompt payload.
```

In the active 0.2.533 release plan's completed Task 4 Step 3, preserve the original sentence and
checkbox, then append this exact forward-looking note:

```markdown
Historical note: this completed packet predated the 2026-08-08 manifest
requirement. For every fresh rerun, include `TASK.md`, `SOURCE_SHA256SUMS`, and
one readable canonical diff. `SOURCE_SHA256SUMS` contains one sorted SHA-256
line for every other regular file in the prepared directory.
```

This keeps the historical claim accurate while correcting the active recipe for future reruns.

Do not add optional wording or a second workflow branch.

- [ ] **Step 4: Verify package GREEN**

Run the single distribution test from Step 2. Expected: PASS.

- [ ] **Step 5: Verify skill GREEN with a fresh agent**

Repeat the exact Task 1 prompt byte-for-byte with a fresh default child requested as
`gpt-5.6-terra`/`medium`/`fork_turns=none` that reads the updated `SKILL.md` only.

Expected JSON includes:

```json
{"source_sha256sums_required":true,"required_named_members":["TASK.md","SOURCE_SHA256SUMS","one readable canonical diff"]}
```

Record that result separately from the embedded RED baseline.

### Task 4: Apply the admitted documentation corrections and update durable status

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `tests/test_review_policy_benchmark.py:51`
- Modify: `docs/status/2026-08-08-triad-maintenance-decisions.md`
- Modify: `docs/superpowers/plans/2026-08-08-triad-maintenance-decisions.md:36,58`

**Interfaces:**
- Consumes: admitted R1/R3 documentation findings and the owner-approved R3 design correction.
- Produces: accurate release notes, an accurately named exact-filesystem inventory test, and a durable audit trail.

- [ ] **Step 1: Document the 0.2.533 formal route**

Add one concise 0.2.533 changelog bullet covering the formal Claude built-in read/search selection,
preservation of configured MCP tools and user permissions, family-specific inspection contracts
rendered by `bin/review_round.py`, and the required source manifest. Do not bump the version.

- [ ] **Step 2: Clarify the inventory test semantics**

Rename the current function
`test_tracked_benchmark_evidence_inventory_is_exact` to exactly:

```python
def test_benchmark_evidence_filesystem_inventory_is_exact() -> None:
```

Add one comment stating that stray untracked files are intentional failures because the complete distributed evidence directory is contract-bound. Do not weaken the exact-set assertion.

Update both old function-name references in
`docs/superpowers/plans/2026-08-08-triad-maintenance-decisions.md`, including the executable pytest
node ID, to the new name.

- [ ] **Step 3: Append the remediation decision to the status record**

Rename the existing final `## Scope` heading to `## Scope of Decisions 1-3`, then append R1's split
verdict, leader reproduction, owner approval, and the unchanged Items 1-3 decisions. Also record
formal-plan R3's split verdict, the rejected MCP-suppression proposal, the owner's superseding
read/search-capable contract, advisory R4's incomplete closure, advisory R5's reproduced findings,
the accepted bounded corrections, and the fact that no commit/release action is implied.

### Task 5: Verify the complete candidate

**Files:**
- Verify all changed files; do not introduce additional product changes.

**Interfaces:**
- Consumes: Tasks 2-4.
- Produces: focused, full-suite, live-capability, and dirty-boundary evidence for pre-merge review.

- [ ] **Step 1: Verify live Claude capability**

Record `claude --version` and confirm live help describes `--tools` as selecting the built-in set and
`--safe-mode` as disabling configured MCP servers. Record that the formal route intentionally uses
the former and not the latter. This is release evidence, not a runtime preflight. Do not monitor or
fail on MCP server startup.

- [ ] **Step 2: Run focused tests**

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_provider_wrappers.py workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py workspace/triad-codex-dispatch-reliability/tests/test_review_policy_benchmark.py workspace/triad-codex-dispatch-reliability/tests/test_review_round.py -q'
```

- [ ] **Step 3: Run the full suite**

```zsh
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests -q'
```

- [ ] **Step 4: Verify the approved change boundary**

Confirm no benchmark evidence file changed, `_prepared_digest` and capture/verify behavior are
unchanged, closure policy is unchanged, ordinary Claude argv is unchanged, and all six frozen
pre-remediation hashes remain recorded as historical basis. Confirm `bin/claude_wrapper.py` retains
its frozen hash; the `bin/review_round.py` diff is confined to the Claude renderer branch;
`tests/test_review_round.py` changes only its matching regression;
`tests/test_provider_wrappers.py` and `leg-contracts.md` change only through Task 2; and
`review-prompt-contract.md` changes only through the approved Task 2 and Task 3 deltas.

### Task 6: Pass a fresh three-family pre-merge gate

**Files:**
- Review only: the complete current candidate and affected unchanged closure.

**Interfaces:**
- Consumes: verified Task 5 candidate plus the six pre-remediation SHA-256 values.
- Produces: a fresh review ID with unanimous admitted `SAFE` verdicts for one prepared-directory digest.

- [ ] **Step 1: Prepare a fresh complete directory**

Include all relevant source, tests, configs, docs, benchmark evidence, `TASK.md`,
`SOURCE_SHA256SUMS`, readable canonical diff, pre-merge R1 status/results, invalid formal-plan R2
provenance, formal-plan R3, advisory incomplete R4, advisory R5, and admitted R6 status/result sets, the embedded
RED plus GREEN skill results, all four public dispatch/review `SKILL.md` files, and the six frozen
pre-remediation dirty-file hashes. Include every file opened by the affected tests.
Exact test-source exclusion: none.

- [ ] **Step 2: Dispatch all three legs before consuming results**

Use the candidate formal route for Claude so this round exercises the built-in `Read,Glob,Grep`
selection while retaining configured MCP tools and user permissions. MCP server startup is not a
failure; actual mutation, external-state change, or candidate execution is. Use the candidate
`bin/review_round.py render` so the round exercises the reviewed renderer, while the unchanged
installed packaged capture, schema validation, convergence, and integrity tools retain their
approved routes. Google and fresh Codex retain their approved routes.

- [ ] **Step 3: Admit and adjudicate**

Require schema-valid Claude, Google, and fresh Codex `SAFE`, independently reproduce every finding, and require final `ROUND_INTEGRITY_OK`. A design/specification expansion still returns to the owner before edits.

- [ ] **Step 4: Stop before external state changes**

Report the gate, tests, changed paths, and remaining risks. Do not commit, push, merge, install, tag, publish, or release.
