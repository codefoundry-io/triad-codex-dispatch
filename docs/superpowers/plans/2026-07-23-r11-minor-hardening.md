# R11 Minor Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` and
> `superpowers:test-driven-development`. Implementation is Lunar-only, review
> is Terra-only, and the root leader owns orchestration and verification.

**Goal:** Close the three R11 Minor findings while preserving the proven
worktree-first formal-review boundary and using the AGY route that is verified
to work today.

**Architecture:** Make AGY model and effort transport honest passthroughs,
identify a managed repair-agent registration by parsed structural effect rather
than raw duplicate text, and expose the paired legacy shell-entry flags in
bootstrap help. Keep current provider routing policy in skills and retain all
external-state prohibitions.

**Tech Stack:** Python 3.12, pytest, Bash, TOML, Markdown.

## Global constraints

- Work only in `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`.
- Preserve every pre-existing staged and unstaged change; do not revert or
  normalize unrelated files.
- Do not commit, push, install, merge, release, create a PR, or modify
  `/Users/chaniri/triad-codex-dispatch`.
- Formal plan and pre-merge gates use one leader-prepared shared review directory
  containing current approved production source, configuration, and
  documentation. Every leg receives that same directory and task; no prompt
  inlines a diff or file body. Project instructions or the owner supply exact
  test-source exclusions; if unavailable, stop and ask the owner. Record one
  simple content digest before dispatch and compare it after every required leg
  terminates. Normal SDD implementation review includes relevant test source;
  classify every test failure as a production defect, test-case defect, or
  intentional specification change.
- Run direct `python3` commands from `/Users/chaniri/codex_workspace` in the
  user's login shell and pass nested test paths explicitly.
- Each implementation task follows RED, minimal GREEN, focused verification,
  then a fresh Terra no-edit review before the next task.
- AGY's current formal argv is `--model "Gemini 3.1 Pro (High)"` with no
  `--effort`; `gemini-3.1-pro-high` remains catalog/policy evidence only.

---

### Task 1: Replace AGY aliasing with honest model/effort passthrough

**Files:**

- Modify: `bin/antigravity_wrapper.py`
- Modify: `tests/test_antigravity_packet_context.py`
- Modify: `tests/test_distribution_contract.py`
- Modify: `skills/triad-antigravity-dispatch/SKILL.md`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `skills/triad-cross-family-review/references/reviewer-routing.md`

**Interface:** The wrapper consumes optional `--model VALUE` and
`--effort {low,medium,high}` and sends each unchanged to AGY. Preflight reports
the requested `model` and `effort`, never a locally invented effective model.

- [x] **Step 1: Write RED command and preflight tests**

Replace the alias-normalization assertion with passthrough coverage equivalent
to:

```python
cmd = wrapper._build_cmd(
    "review", sentinel, True, "Gemini 3.1 Pro (High)", 1200
)
assert cmd[cmd.index("--model") + 1] == "Gemini 3.1 Pro (High)"
assert "--effort" not in cmd

future_cmd = wrapper._build_cmd(
    "review", sentinel, True, "gemini-3.1-pro", 1200, effort="high"
)
assert future_cmd[future_cmd.index("--model") + 1] == "gemini-3.1-pro"
assert future_cmd[future_cmd.index("--effort") + 1] == "high"
```

Change the sealed preflight test to pass the display label and assert:

```python
assert receipt["model"] == "Gemini 3.1 Pro (High)"
assert receipt["effort"] is None
assert "effective_model" not in receipt
```

Add a second preflight case with `--model gemini-3.1-pro --effort high` and
assert both requested values are echoed. Add an argparse boundary case that
passes `--effort extreme` and requires `SystemExit(2)` before provider,
settings, or filesystem work.

Add one mocked normal-dispatch regression that supplies
`--model gemini-3.1-pro --effort high` through `sys.argv`, captures the final
argv passed to the existing PTY/driver seam, and asserts:

```python
assert final_argv[final_argv.index("--model") + 1] == "gemini-3.1-pro"
assert final_argv[final_argv.index("--effort") + 1] == "high"
```

This live `main()` test is required in addition to direct `_build_cmd()`
coverage so the parser and the single run-site forwarding cannot drift apart.

Extend the distribution contract so it fails while the hidden alias and old
skill invocation remain.

- [x] **Step 2: Run the focused tests and preserve the expected failure**

```bash
python3 -m pytest -q \
  workspace/triad-codex-dispatch-reliability/tests/test_antigravity_packet_context.py \
  workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py
```

The failure must be caused by missing effort passthrough, the stale
`effective_model` receipt, or stale formal-route text—not an environment error.

- [x] **Step 3: Implement the minimum wrapper transport**

Use this shape without provider-specific aliasing:

```python
def _build_cmd(..., *, effort=None, pydantic=False, skip_permissions=False):
    ...
    if model:
        cmd += ["--model", model]
    if effort:
        cmd += ["--effort", effort]

p.add_argument("--model", default=None)
p.add_argument("--effort", choices=["low", "medium", "high"], default=None)
```

Forward `args.effort` at the single `_build_cmd()` run site. In preflight emit
`"model": args.model` and `"effort": args.effort`; remove
`effective_model`.

- [x] **Step 4: Align the formal-review skills**

Use this current invocation in both dispatch skills:

```python
"--model", "Gemini 3.1 Pro (High)",
```

Document the advertised stable selector separately from the exact outbound
display label. State that preflight proves argv only, exposed identity must
agree, absent identity is `unexposed`, and the base-slug plus effort route is
adopted only after a fresh post-update probe succeeds.

- [x] **Step 5: Run focused GREEN verification**

Run the Step 2 command and require zero failures. Record the exact command and
result for Terra review; do not commit.

Task evidence: Lunar `/root/r11_task1_agy_passthrough` observed four intended
RED failures with 110 passing, then reached 114 passing. Leader rerun: 114
passing. Terra spec review `/root/r11_task1_spec_review` approved. Terra quality
review `/root/r11_task1_quality_review` found one preflight-construction Minor;
the same Lunar repaired it with a shared pure route-argument helper and the
Terra re-review approved with no remaining finding.

---

### Task 2: Identify the active managed TOML registration structurally

**Files:**

- Modify: `bin/bootstrap_repair.py`
- Modify: `tests/test_bootstrap.py`

**Interface:** `split_registration()` returns the exact `before` and `after`
bytes for one structurally owned registration, while string-contained copies
remain foreign data.

- [x] **Step 1: Write the exact-block RED regression**

Construct foreign TOML with the byte-exact generated block inside a multiline
string:

```python
foreign = (
    'description = """\n'
    + helper.registration_block(analyzer, True)
    + '"""\n'
).encode("utf-8")
```

Assert first install produces exactly
`foreign + b"\n" + registration_block(..., True).encode()`, second install is
byte-idempotent, and remove restores `foreign` exactly.

- [x] **Step 2: Run the single regression and observe RED**

```bash
python3 -m pytest -q \
  workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py \
  -k preserves_exact_registration_block_inside_multiline_string
```

Require the current duplicate-text refusal as the expected failure.

- [x] **Step 3: Implement candidate-by-removal parsing**

For both supported generated block shapes, enumerate every exact occurrence.
For each occurrence, remove only that occurrence and parse the remainder. Add a
candidate only if the original active registration equals `expected`, the
remainder has no `NAME`, and reserved markers equal `[REG_BEGIN, REG_END]`.
Return the sole candidate, refuse multiple candidates, preserve the existing
reserved-marker refusal when none qualifies, and retain `before + after`
unchanged.

- [x] **Step 4: Run focused GREEN and nearby refusal coverage**

```bash
python3 -m pytest -q \
  workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py \
  -k 'registration or config_markers_inside_multiline_string or noncanonical_marker_wrapped'
```

Require zero failures and no byte changes outside the two owned files.

Task evidence: Lunar `/root/r11_task2_registration` reproduced the duplicate
text refusal as one failed focused test, then reached 12 passing with 233
deselected. Leader rerun matched that result. Terra spec review
`/root/r11_task2_spec_review` and quality review
`/root/r11_task2_quality_review` both approved with no findings.

---

### Task 3: Document both legacy shell-entry opt-in flags

**Files:**

- Modify: `scripts/bootstrap.sh`
- Modify: `tests/test_bootstrap.py`

**Interface:** The rendered `usage()` text exposes the same paired-flag
precondition already enforced before mutation.

- [x] **Step 1: Write a RED help assertion**

Add a usage test that invokes an invalid option, normalizes rendered stderr with
`" ".join(result.stderr.split())`, and asserts one complete clause equivalent
to:

```text
The legacy codex-triad shell entry is migration-only and requires both
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 and
TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1; it is not the normal start path.
```

The test must prove the two flags are jointly required for the migration-only
entry, not merely present elsewhere in help.

- [x] **Step 2: Run the focused test and observe RED**

```bash
python3 -m pytest -q \
  workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py \
  -k 'usage_documents_paired_legacy_shell_entry_flags'
```

- [x] **Step 3: Add the minimum help-only sentence**

Place it beside the existing dedicated-profile migration paragraph. Do not
change runtime branching or add `codex-triad` to README files.

- [x] **Step 4: Run focused GREEN verification**

Run the Step 2 command plus the existing shell-entry compatibility tests and
require zero failures.

Task evidence: Lunar `/root/r11_task3_bootstrap_help` observed the missing-help
RED, then passed the focused test and 11 legacy shell-entry tests. Leader rerun
matched 11 passing with 235 deselected; Bash syntax and scoped diff checks
passed. Terra spec review `/root/r11_task3_spec_review` and quality review
`/root/r11_task3_quality_review` both approved with no findings.

---

### Task 4: Reconcile the R12 documentation findings

**Files:**

- Modify: `CHANGELOG.md`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `docs/status/2026-07-22-current-state.md`
- Modify: `docs/status/2026-07-22-resume-prompt.md`
- Modify: `docs/status/2026-07-22-formal-review-routing-verification.md`
- Modify: `docs/superpowers/plans/2026-07-22-formal-review-routing-policy.md`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `tests/test_distribution_contract.py`

**Interface:** All current operator-facing documents agree on catalog evidence,
exact outbound AGY argv, preflight scope, runtime identity admission, uninstall
file preservation, and the latest review/test ledger.

- [x] **Step 1: Write RED distribution-contract assertions**

Require the following current contracts:

- changelog says `--model` and optional `--effort` pass through unchanged and
  preflight reports requested `model`/`effort` only;
- the formal-review-routing implementation plan begins with a `Superseded`
  status pointing to the current routing reference and R11 hardening design;
- every current status/resume/routing document distinguishes
  `gemini-3.1-pro-high` catalog evidence from outbound
  `Gemini 3.1 Pro (High)` with no effort and exposed-or-`unexposed` identity;
- both public READMEs say `config.toml` is deleted only when it did not exist
  before install as well as containing no owner bytes; and
- the cross-family skill names `gemini-3.1-pro-high` inline as the selector that
  authenticated `agy models` must advertise.

For each of the current-state, resume, and routing-verification documents, also
assert the exact R12 ledger fields:

```text
review ID: 20260723-r11-minor-hardening-r12
prompt SHA-256: 4d771be60a54a698dea7fe080ad98ab335106b7befe6ec6d4a5baed1450cac01
equal pre/post fingerprint: cd3885d0f85631320409ba8eb12fe016dd279dad7e731059a70f8255c20dd454
fresh Codex: NOT-SAFE with one Major
Claude: SAFE with six Minor findings
AGY: extraction-error, post-dispatch, fallback-ineligible
repair analyzer: escalate, proposal null/no classifier change
local verification: 648 passed plus 6 subtests
round status: invalid and requires a fresh complete round
```

Assert that no handoff invents an `R10 used prompt SHA-256` record when no
verified R10 hash is available.

- [x] **Step 2: Run RED**

```bash
python3 -m pytest -q \
  workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py
```

The failures must identify stale documentation, not source behavior.

- [x] **Step 3: Apply the minimum English/Korean documentation repair**

Preserve prior review history. Add the known R11 PASS evidence and the R12
invalid record with prompt hash, equal fingerprint, per-leg terminal states,
accepted findings, repair-analyzer escalation, and 648 plus 6-subtest local
verification. Do not invent R10 evidence that is absent from the handoff.

Keep the cross-family skill body within its 200-line post-frontmatter limit by
clarifying the existing selector sentence without adding a line.

- [x] **Step 4: Run focused GREEN and Terra reviews**

Run the Step 2 command, `git diff --check`, and require fresh Terra spec and
quality approval. Do not commit.

Task evidence: Lunar `/root/r12_task4_docs_reconcile` first observed six
documentation-contract failures, then reached 69 passing. Terra spec review
`/root/r12_task4_spec_review` approved. Terra quality review
`/root/r12_task4_quality_review` found stale current summaries/R6 tense and one
missing changelog negative assertion; Lunar repaired them with focused
regressions, the suite reached 71 passing, and final Terra re-review approved.

---

### Task 5: Integrate, document state, and close a fresh formal gate

**Files:**

- Modify: `.superpowers/sdd/progress.md`
- Modify: `docs/status/2026-07-22-current-state.md`
- Modify: `docs/status/2026-07-22-resume-prompt.md`
- Modify: `docs/status/2026-07-22-formal-review-routing-verification.md`
- Modify: `docs/superpowers/specs/2026-07-22-formal-review-routing-policy-design.md`
- Modify: `CHANGELOG.md`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `scripts/bootstrap.sh`
- Modify: `bin/bootstrap_repair.py`
- Modify: `tests/test_bootstrap.py`
- Modify: `tests/test_bootstrap_repair_transaction.py`
- Modify: `tests/test_distribution_contract.py`

**Interface:** Status documents distinguish the prior immutable R11/R14
evidence from this new uncommitted hardening round and give one exact Argus
resume condition.

- [ ] **Step 1: Append SDD and handoff state without rewriting history**

Record Lunar implementation identities, Terra task-review results, focused test
commands, the AGY compatibility bridge, and the no-commit boundary. Do not edit
older immutable hashes as if they covered new bytes.

Before the next gate, add RED distribution assertions and minimum documentation
for the R13 reconciliation:

- the 2026-07-22 routing design is explicitly superseded;
- bootstrap help, both READMEs, and the changelog scope absent-file restoration
  to intact provenance-marked registration and environment-policy blocks; and
- all three handoffs record R13 review ID, exact prompt/fingerprint, fresh Codex
  Major, AGY post-dispatch extraction failure, analyzer escalation/proposal
  null, Claude invalid fenced framing with diagnostic two Minors, equal
  fingerprint, invalid round, and fresh-complete-round requirement.

Observe focused RED before changing documentation. The test contract must pin:

```text
review ID: 20260723-r11-minor-hardening-r13
prompt SHA-256: a2396c1afb614a61bbbc29a5e75612f76bd452c3f7679c5f8312b9de530db177
equal pre/post fingerprint: 577770d8c4fd05ef3b0271ad21044fcd9dc173a0b7425608af035136d375ad8a
fresh Codex: NOT-SAFE with one Major
AGY: extraction-error, post-dispatch, fallback-ineligible
repair analyzer: escalate, proposal null/no classifier change
Claude: invalid fenced JSON framing; diagnostic SAFE with two Minor findings
round status: invalid and requires a fresh complete round
```

It must also assert that the plan preserves separate staged and unstaged
zero-context evidence. After the RED failures are recorded, make the minimum
documentation changes and run focused distribution GREEN before the full suite.

Task-level Terra quality review found that this wording-only closure leaves a
real partial-uninstall deletion path. Add a second focused RED before changing
implementation:

1. create a pre-existing zero-byte `config.toml`;
2. run normal bootstrap install;
3. remove only the exact managed repair-analyzer registration, leaving the
   exact managed environment-policy fragment;
4. run full bootstrap `--remove`; and
5. assert that `config.toml` still exists and is exactly zero bytes.

The current implementation deletes the file because fragment removal runs
first and independently treats an empty remainder as a bootstrap-created file.
Implement one bounded provenance gate with this exact internal interface:

- `remove_config_fragment(path, *, preserve_empty=False)` retains its current
  default behavior;
- `config-fragment --preserve-empty` is a `store_true` parser flag and `main()`
  forwards it only to removal;
- when the flag is set and the managed fragment leaves an empty remainder,
  publish a zero-byte file and return `removed`;
- without the flag, retain `removed-file` and delete a fragment-only file; and
- `scripts/bootstrap.sh` passes `--preserve-empty` only from full-bootstrap
  removal, leaving repair lifecycle removal solely responsible for deleting a
  config after it reads intact registration provenance.

Add focused helper/CLI coverage proving default fragment-only removal returns
`removed-file` and deletes the file, while `--preserve-empty` returns `removed`
and retains a zero-byte file. GREEN must also include the end-to-end partial-
registration RED plus the existing initially-absent and pre-existing-empty
intact round trips.

At the same time, close the three quality-test weaknesses without broadening
runtime scope:

- retain the English literal in English surfaces, but require Korean guidance to
  say `provenance-marked managed registration과 environment-policy block이 둘
  다 그대로 남아 있는 경우에만` and reject the full English sentence there;
- give each handoff the stable heading `## R13 invalid formal round`, extract
  from that heading to the next level-two heading or EOF, and assert every
  literal terminal field only inside that bounded slice; and
- extract from `- [ ] **Step 3: Capture one guarded formal-review input**` to
  `- [ ] **Step 4: Run the fresh read-only three-family round**`, then require
  both zero-context commands, the counteracted `MM` rationale, and the rule
  that a net diff is supplemental only inside that slice.

Run focused RED/GREEN for the new end-to-end bootstrap regression and the
distribution contract before integrated verification. Do not change classifier
or provider fallback behavior.

- [ ] **Step 2: Run integrated local verification**

```bash
python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests
bash -n workspace/triad-codex-dispatch-reliability/scripts/bootstrap.sh
git -C workspace/triad-codex-dispatch-reliability diff --check
git -C workspace/triad-codex-dispatch-reliability diff --cached --check
```

All commands must pass. Record the complete pytest count and shell/diff status.

> **Historical, superseded, and non-executable:** Task 5 Steps 3-5 below
> preserve the retired diff/hash/fingerprint/path-evidence plan. Do not execute
> them. Step 8 is the only active continuation.

- [ ] **Step 3: Capture one guarded formal-review input**

The leader records `HEAD`, full staged diff, full unstaged diff, untracked
inventory and untracked content hashes for the mutation fingerprint, then
captures sanitized non-test Git status plus non-test staged and unstaged diffs
for reviewer navigation. Every reviewer receives that identical trusted
non-test evidence and the same canonical worktree. Exclude test source,
credentials, tokens, cookies, authentication files, environment dumps,
provider logs, and unrelated paths. Reviewers may follow the diff only into
directly related non-test source, documentation, configuration, schema, and
build files.

For the next retry, attach separate zero-context non-test staged and unstaged
diffs (`git diff --cached --unified=0 -- . ':(exclude)tests/**'` and
`git diff --unified=0 -- . ':(exclude)tests/**'`) plus matching non-test status
and non-test untracked inventory/hashes. This compacts navigation evidence
without hiding counteracted non-test `MM` bytes or generating a related-file
allowlist. Keep the stronger full staged/unstaged fingerprint algorithm, which
continues to cover test changes locally. A net diff may be included only as
additional evidence, never as a replacement for either non-test component.

- [ ] **Step 4: Run the fresh read-only three-family round**

- Fresh Codex: default child, `gpt-5.6-terra`, `xhigh`,
  `fork_turns="none"`, prompt-controlled no-edit contract.
- Claude: owner-authorized Opus route, read-only formal review.
- Google: authenticated catalog evidence plus wrapper
  `--model "Gemini 3.1 Pro (High)"`, no `--effort`, read-only formal review.

Require three valid terminal verdicts and recompute the fingerprint. Any
mutation, missing leg, identity conflict, or unresolved blocker invalidates the
round. Reviewers must not open or review test source; they receive only the
leader's local test-result summary.

- [ ] **Step 5: Handoff without external mutation**

If the round is SAFE, update the status/resume documents with new IDs, hashes,
tests, terminal states, and the exact Argus restart instruction. Leave all work
uncommitted and do not install, push, merge, or release.

---

### Task 6: Reconcile R14 upgrade and containment Minors

**Files:**

- Modify: `scripts/bootstrap.sh`
- Modify: `bin/bootstrap_repair.py`
- Modify: `tests/test_bootstrap.py`
- Modify: `tests/test_bootstrap_repair_transaction.py`
- Modify: `tests/test_distribution_contract.py`
- Modify: `SECURITY.md`
- Modify: `CHANGELOG.md`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `docs/status/2026-07-22-current-state.md`
- Modify: `docs/status/2026-07-22-resume-prompt.md`
- Modify: `docs/status/2026-07-22-formal-review-routing-verification.md`

**Interface:** A plain install never deletes legacy artifacts. With profile or
shell opt-in off, it warns only for the corresponding exact managed artifact,
names its path, and points to deliberate removal/reinstall or explicit legacy
opt-in. Local tests remain leader-only and are never gate-review input.

- [x] **Step 1: Add focused RED for exact managed legacy warnings**

Create local bootstrap regressions for these cases:

1. an exact managed legacy profile exists while profile opt-in is off;
2. an exact managed `codex-triad` shell entry exists while shell opt-in is off;
3. the corresponding absent/unmanaged state does not produce the managed-
   legacy warning; and
4. explicit legacy opt-in suppresses the warning and retains the existing
   install/update behavior.

Add helper/CLI RED coverage for `managed-artifact --action inspect`: a safe
missing path returns `absent`, exact marker-owned regular content returns
`managed`, and a safe foreign regular file returns `unmanaged`; unsafe ancestor,
symlink, non-regular, and read failures retain nonzero refusal behavior.

The warnings must name the exact path, say no automatic deletion occurred, and
offer `--remove` followed by ordinary reinstall or the exact legacy opt-in.
Observe focused RED before changing `scripts/bootstrap.sh`.

- [x] **Step 2: Implement the read-only warning gate**

Add `managed-artifact --action inspect` as a read-only safe tri-state operation:
return `absent`, `managed`, or `unmanaged` for safe regular paths without
changing the stricter `preflight` contract used when an artifact is selected.
Unsafe ancestors, symlinks, non-regular files, and read failures remain
refusals. Use that action for the opt-out profile and existing
`shell-entry --action preflight-remove` for the opt-out shell entry. Run both
before `begin_command_group`; warn on `managed`, ignore safe `absent`/`unmanaged`,
and abort before persistent mutation on any refusing probe. Do not remove,
rewrite, quarantine, or follow an unmanaged or unsafe artifact.

- [x] **Step 3: Close the non-test documentation Minors**

- Qualify `SECURITY.md` with the exact rules-opt-out/absent-path condition and
  retain the launcher scrub as defense in depth.
- Add English/Korean upgrade notes for retained managed legacy profile/shell
  artifacts, ordinary `codex`, explicit legacy opt-in, and the retired
  no-prompt `allow` posture.
- Add the same upgrade facts to the 0.2.529 changelog and date the current
  hardening content 2026-07-23.
- Document that a pre-0.2.529 initially absent config with stale `true`
  provenance is left as a safe zero-byte file because it is indistinguishable
  from a genuinely pre-existing empty file.
- Record R14 exactly in all three handoffs: review ID, prompt SHA, equal
  fingerprint, AGY `SAFE`/identity `unexposed`, Claude `SAFE` with four Minors,
  initial Terra false positive and corrected `SAFE`, accepted corrections, and
  fresh-round requirement.

Before changing documentation, add local distribution RED assertions with the
stable heading `## R14 corrected formal round` in each handoff. Slice from that
heading to the next level-two heading or EOF and pin these literals inside it:

```text
review ID: 20260723-r11-minor-hardening-r14
prompt bytes: 147,929
prompt SHA-256: f5e69a2095449b28b413c87df390429adee19f7413c23d3b266a316a5fd0d74c
equal pre/post fingerprint: ea0f1264fe892c98eede5c3437a796b120df83b33cb3f42ccf450ceeea7835e7
AGY: SAFE, no findings, identity unexposed
Claude: SAFE with four Minor findings
fresh Terra: initial false Major retracted; corrected SAFE with no findings
round status: reviewed bytes SAFE; accepted Minor corrections change bytes and require a fresh complete round
```

Also pin the exact `SECURITY.md` opt-out condition and launcher-scrub defense in
depth, the `## 0.2.529 — 2026-07-23` heading, English/Korean legacy upgrade
guidance, and the stale `original config existed = true` zero-byte fail-safe
outcome. Observe this documentation RED before edits and focused GREEN after.
These are local assertions only; formal reviewers must not receive or inspect
their source.

- [x] **Step 4: Focused GREEN and Terra implementation review**

Run the new warning nodes plus the full bootstrap and distribution files. Then
run Bash syntax and both staged/unstaged diff checks. Normal SDD Terra reviewers
inspect the implementation and relevant test source, including negative and
false-positive coverage, and preserve a full-worktree pre/post fingerprint.

- [x] **Step 5: Full verification and fresh complete round**

Run the full local suite as leader-only evidence, update current counts before
capture, then run a fresh-ID complete Claude/AGY/Terra round with the same
non-test review boundary. Do not resume Argus unless all required legs are valid
and reconciled without an accepted byte-changing correction.

### Task 7: Reconcile R15 review-boundary and partial-activation findings

**Files:**

- Modify: `scripts/bootstrap.sh`
- Modify: `bin/antigravity_wrapper.py`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Modify: `skills/triad-cross-family-review/references/fresh-codex-formal-review.md`
- Modify: `skills/triad-claude-dispatch/SKILL.md`
- Modify: `skills/triad-antigravity-dispatch/SKILL.md`
- Modify: `skills/triad-gemini-dispatch/SKILL.md`
- Modify: `tests/test_bootstrap.py`
- Modify: `tests/test_antigravity_packet_context.py`
- Modify: `tests/test_distribution_contract.py`
- Modify: `CHANGELOG.md`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `SECURITY.md`
- Modify: `docs/status/2026-07-22-current-state.md`
- Modify: `docs/status/2026-07-22-resume-prompt.md`
- Modify: `docs/status/2026-07-22-formal-review-routing-verification.md`

**Interface:** Formal plan and pre-merge three-family gates exclude test source;
normal SDD implementation reviews include it. Unsafe unselected legacy probes
warn without following or changing the target. Selected targets remain strict.
Provider wrapper commands are not published until repair lifecycle install has
succeeded. AGY preflight receipts report the parsed requested values exactly.

- [x] **Step 1: Add RED for the four accepted R15 contracts**

Add focused local assertions before production/docs edits:

1. distribution text distinguishes SDD test review from formal plan/pre-merge
   no-test review in the cross-family skill, all provider dispatch skills, the
   fresh-Codex template, `README.md`, `README.ko.md`, `SECURITY.md`, and
   `CHANGELOG.md`; the template has a leader-controlled data-boundary value and
   no unconditional instruction to inspect tests, while separately
   owner-approved advisory review may retain its approved test scope;
2. an AGY preflight using `--model=--effort --effort high` reports model
   `--effort` and effort `high`, while provider argv passthrough remains exact;
3. unsafe opt-out profile/shell probes return a successful ordinary install,
   emit a non-follow/non-mutation warning naming the path, preserve the unsafe
   object and referent, and still install the selected ordinary artifacts;
4. injected repair-registration publication failure leaves every provider
   wrapper launcher, `triad-apply-repair`, analyzer, managed registration,
   rules, and shell entry absent, while preserving unrelated owner bytes.

Add bounded distribution RED for a stable `## R15 invalid formal round` section
in all three handoffs. Require exactly one such heading, slice from it through
the next level-two heading or EOF, and pin this exact tuple inside the slice:

```text
review ID: 20260723-r11-minor-hardening-r15
prompt bytes: 159,396
prompt SHA-256: e176aaa948488a42db5ee8a9be00db0c99d7cdbd79b2688b5daa04babe2c205e
equal pre/post fingerprint: 5acc6a14cc0886f268d20ef3745b574eee948531756146be2366a76efe28d21c
fresh Terra: NOT-SAFE with one Major formal test-scope finding
AGY: substantive SAFE, fenced JSON invalid, identity unexposed
Claude: NOT-SAFE with one Major, two Minor findings, and two open questions
round status: invalid and NOT-SAFE; accepted corrections change bytes and require a fresh complete round
```

Assert that the R15 review ID, prompt hash, and fingerprint do not occur outside
that bounded section in each handoff, following the existing R13 confinement
pattern.

- [x] **Step 2: Implement boundary and receipt corrections**

In the cross-family and provider skills, state that formal three-family plan and
pre-merge gates receive non-test status/diffs and directly related non-test
files only, while ordinary advisory review uses its owner-approved scope. State
explicitly that normal SDD review is outside that restriction and reviews tests.
Give the fresh-Codex template a rendered review-kind/data-boundary value and
remove its unconditional `tests` impact instruction. Require literal unfenced
SAFE and NOT-SAFE examples for AGY formal prompts; fenced JSON stays invalid.
Apply the same formal-plan/pre-merge versus advisory/SDD distinction to both
READMEs, `SECURITY.md`, and the current changelog entry.

Set AGY receipt `model` and `effort` from `args.model` and `args.effort`
directly, removing `_route_arg_value` if unused. Do not change `_build_route_args`
or dispatch argv.

- [x] **Step 3: Implement bounded bootstrap ordering and advisory handling**

Keep helper inspection strict/no-follow. In `warn_legacy_opt_out_artifacts`, a
nonzero opt-out probe becomes a warning that names the unselected path, says it
was not followed or changed, includes refusal detail as warning text, and
continues. Safe managed/absent/unmanaged behavior remains unchanged. Selected
profile/rules/shell preflight remains fatal.

Keep all ownership preflights early, but move provider command-group staging and
publication after a successful `run_repair_lifecycle install`. On repair failure,
exit before `begin_command_group`. Preserve the existing bounded transactional
behavior; do not redesign the entire bootstrap lifecycle.

- [x] **Step 4: Close documentation and R15 ledger**

Correct the paired-flag design/runtime statement, replace stale public formal
review test-scope wording, explain non-blocking unsafe opt-out inspection in
English/Korean/security/changelog guidance, expand the late-repair failure
statement to include provider launchers, and record R15 exactly under
`## R15 invalid formal round` in all three handoffs.

- [x] **Step 5: GREEN, SDD Terra review, and full verification**

Run the new focused nodes, then full bootstrap, Antigravity packet-context, and
distribution test files. Run the full local suite, Bash syntax, and both diff
checks. Fresh Terra SDD specification and quality reviewers inspect relevant
production and test code. Preserve a full-worktree pre/post fingerprint.

- [x] **Step 6: Fresh complete formal round (owner-resumed and completed R16)**

Update the leader-only counts, capture a new full-worktree fingerprint, and run
fresh-ID Claude/AGY/Terra legs over the identical non-test prompt. Unfenced JSON
examples apply only to wrapper-backed Claude/AGY/Gemini legs as applicable. The
native fresh-Codex prompt receives no JSON example or JSON-only command and uses
its semantic result contract. Formal reviewers must not inspect test source.
The owner later resumed R16 explicitly; its corrected formal-round ledger is in
the three handoffs. Argus remains gated until the next complete round passes.

- [x] **Step 7: Apply accepted R16 corrections plus completed R17 attempt**

Apply the accepted route_args receipt correction, run fresh local verification,
obtain Terra SDD specification and quality review, and capture a new complete
Claude/AGY/fresh-Codex formal round over the corrected bytes before resuming
Argus. Keep the non-test review boundary and the native semantic result contract.
The completed R17 attempt is invalid because the required AGY leg ended in
extraction-error.

- [ ] **Step 8: Fresh complete retry after the R17 AGY extraction-error**

Before any new external execution, apply the owner-approved minimal
shared-directory correction:

1. add RED distribution assertions that current formal-review instructions use
   one leader-prepared shared review directory containing current approved
   production source, configuration, and documentation; every leg receives the
   same directory and task; no prompt inlines a diff or file body; and one
   simple content digest is compared after every required leg terminates;
2. update the root workspace dispatch policy, cross-family/provider skills,
   fresh-Codex template, public security/readme guidance, and current handoffs
   without rewriting historical R14-R17 task or round facts;
3. keep formal test-source exclusion and normal SDD test inspection unchanged;
4. preserve the historical R17 record that its external prompt was 195,916
   bytes, including 187,420 inline patch bytes, and that AGY truncation removed
   its result contract and completion marker;
5. do not add byte measurement, prompt-size admission, a wrapper classification,
   fallback, timeout, model, effort, or extraction change.

Lunar owns the RED/GREEN implementation. Fresh Terra reviewers inspect the
resulting production, documentation, and test changes. The leader runs the
canonical outside-sandbox Python verification, preserves the dirty worktree;
and stop before external execution.

The next pending formal round must use one shared review directory and the
owner-supplied test-source boundary. Start that round only in a later
owner-authorized operation after the local correction is green.
