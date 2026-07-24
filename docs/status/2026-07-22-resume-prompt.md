# Triad Codex Dispatch restart prompt

Start the new Codex session with saved project root exactly:

`/Users/chaniri/codex_workspace`

Then paste:

```text
Resume the worktree-first Agent-review distribution slice for triad-codex-dispatch.

Development root:
/Users/chaniri/codex_workspace

Product worktree:
/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability

Read these documents completely, in this exact order:
1. /Users/chaniri/codex_workspace/AGENTS.md
2. /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-07-22-current-state.md
3. /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-07-22-resume-prompt.md

First verify the exact worktree, branch, local HEAD, upstream state, and dirty
source/documentation set. Expected branch is release/0.2.529 at local HEAD
f0376dfc34006e0ee73e6ea4673a0d7f1c4a8586, with no configured upstream at this
boundary. Derive the live state from Git rather than assuming it is unchanged.

Preserve the unrelated dirty checkout at
/Users/chaniri/triad-codex-dispatch. Do not reset, clean, copy over, merge into,
or otherwise modify it.

Do not commit, push, merge to another branch, reinstall, release, or create a
pull request as an incidental step. Git history and remote-state mutations need
their applicable authorization and may present an automatic security review
approval request.

This restart/resume handoff stops before a new external formal round. Do not
dispatch providers, invoke wrappers, or claim a new review occurred until the
owner confirms local verification and fresh SDD review.

Any formal plan/pre-merge review uses one leader-prepared shared review directory
containing current approved production source, configuration, and documentation.
Project instructions or the owner supply exact test-source exclusions; if those
exclusions are unavailable, stop and ask the owner. Every leg receives the same
directory and task. No prompt inlines a diff or file body. Record one simple
content digest before dispatch and compare it after every required leg terminates;
a mismatch invalidates the round. Reviewers use only the approved data boundary.
Formal plan/pre-merge legs do not receive test source; normal SDD implementation
review includes relevant test source. Before a formal gate, classify every test
failure as production defect, test-case defect, or intentional specification
change and resolve or approve it.

Provider legs use only their approved read-only inspection route and must not run
candidate code, tests, builds, hooks, or generated scripts. Local test execution
and result verification remain leader operations.

Use fresh Codex gpt-5.6-terra/xhigh/fork_turns none, Claude opus/xhigh, and
primary agy authenticated `agy models` catalog selector
`gemini-3.1-pro-high`; exact outbound model argument `Gemini 3.1 Pro (High)`
with no `--effort`. Sol/Fable are conditional long-running escalations, not
routine reviewers. Gemini is fallback-only after proven
pre-submission agy route unavailability.

Do not admit a formal Gemini fallback: the shipped distribution has no qualifying
enforcement proof and runs no automatic probe. Ordinary/non-formal fallback
remains available after proven pre-submission agy unavailability. Apply the
[formal reviewer routing contract](../../skills/triad-cross-family-review/references/reviewer-routing.md)
if the owner later records route-specific proof.

The normal bootstrap keeps ordinary codex, does not install a dedicated profile,
and does not replace owner approval, reviewer, sandbox, or Auto-review policy.
Exact managed launcher rules use decision=prompt. Agent Review requires
approvals_reviewer=auto_review plus an interactive approval policy:
approval_policy=on-request is sufficient; granular policy additionally needs
granular.rules=true and granular.sandbox_approval=true. Do not auto-install an
[auto_review].policy. The explicit owner skill invocation supplies one
authorization within an unchanged provider/worktree/scope/data boundary;
credentials, authentication files, environment dumps, provider logs, and
unrelated paths stay excluded. Do not ask again for each matching leg. `/approve`
is only for one exact recorded denial, never a broad bypass.

Commit 94a24cb2e59972cd8fccefd06c05a6a7b77166b8 was integrated only at the
functional level: exact own-line bytes/lines truncation markers now produce
terminal `truncated-answer`, quarantine stdout, and bypass schema repair. A
required formal agy leg is invalid and requests a new bounded, compact result;
it does not switch to Gemini after submission. The generic write-file and
sandbox-relaxation workaround, upstream history merge, and release metadata
were rejected.

The first live same-prompt worktree round used Claude Opus/xhigh, primary agy
gemini-3.1-pro-high, and fresh Codex Terra/xhigh. AGY returned SAFE; Claude and
Codex returned NOT-SAFE with reproducible bootstrap/docs findings. The pre/post
fingerprint matched. The fixes make global wrapper rules always prompt, require
the legacy profile before any shell-entry opt-in, restore the native
loader-environment guard, replace stale README profile starts with plain codex,
and restore the 0.2.527 changelog boundary. The corrected 0.2.529 plugin,
launchers, exact prompt rules, and loader-environment guard are installed; a
fresh ordinary-Codex session exposes all four triad skills. That round is closed
and a complete fresh round is required after final verification.

The second complete worktree-first round also kept an equal pre/post fingerprint.
AGY returned SAFE; fresh Codex found the unchanged hand-maintained migration
rules still used allow; Claude found the initially-absent config repeated-install
failure and security/documentation residuals. Those findings were reproduced,
fixed, and covered by the then-current full-suite result: 631 passed and 6 subtests
passed. Because the fixes changed reviewed bytes, that round is closed and is
not PASS; run one new complete three-family round over the final bytes.

A later full-input round was invalid because Claude timed out after AGY and Codex
returned SAFE. Its compact fresh-ID rerun kept an equal pre/post fingerprint;
AGY returned SAFE, while Codex and Claude found the last smoke/profile wording
and fresh-layout registration parser defect. Those were fixed with explicit
owner-edit/owner-tail and byte-exact round-trip coverage.

The next compact round used prompt SHA-256
928a87c3e9c72ff9df870e54da7065dc2d03ff205cfa100c21dfa81e5d6e02da
with an equal pre/post fingerprint. AGY returned SAFE; Claude returned SAFE with
low-severity release-hardening observations; fresh Codex returned NOT-SAFE over
stale allow-list wording. The accepted fixes suppress rules and the legacy shell
entry after late repair-registration failure, update migration guidance, and
clarify remove/changelog coverage. The then-current full suite was 635 passed and 6
subtests passed. These fixes changed reviewed bytes, so run one final complete
three-family round.

R6 used prompt SHA-256
b396689de4524360a58072025f15caf53ffb35c4a1c848785691513f0e176b05
with an equal pre/post fingerprint. Claude and fresh Codex returned NOT-SAFE;
AGY returned SAFE but exposed `Gemini 3.6 Flash (High)` after receiving the
slug selector, so its route was invalid. The accepted corrections attach the
captured diff body to the native-child message, align Agent Review exclusions
and security/remove/runtime wording. The R6 historical record documented a
temporary normalization to agy's effective `Gemini 3.1 Pro (High)` label; it is
superseded by the current exact `--model`/optional `--effort` passthrough. R6 is
closed; run a new complete round only after
the final suite is green. The refreshed installed wrapper returned
`Gemini 3.1 Pro`, effort `High`, and `ROUTE_SPIKE_OK` for the stable selector.
The historical R16 full suite was 687 passed plus 6 subtests in 158.50s.

R7 used prompt SHA-256
68debad2d5acb7d15091941a717c70a65ffa1373facb5fa70148d34c6fe4ec79;
the prompt contained the identical 141,294-byte captured status/diff and the
pre/post fingerprint matched. AGY was valid SAFE on Gemini 3.1 Pro High; Claude
was SAFE with minor findings. Fresh Codex required a whole-bootstrap rollback
transaction and returned NOT-SAFE, but that requirement conflicts with the
governing bounded-repair design's explicit non-goal. Accepted minor corrections
cover fresh-config backup suppression, requested/effective AGY preflight model
values, the real dangling-classifier regression, usage/security text, and
explicit fail-closed bare-key coverage. Those corrections changed bytes, so R7
is closed and one new complete round is required.

R8 used prompt SHA-256
dcd22b1ffaa75d072148676a55cd07aa341faf3eb432e38e38217f1953578797;
the exact 148,124-byte prompt had an equal pre/post fingerprint. AGY's content
concluded safe but omitted required result sections, so its leg was invalid.
Fresh Codex found removal of a pre-existing empty config; Claude found that a
rules opt-out skipped the loader guard even when owner-maintained rules remained.
Those reproduced defects are fixed and covered by regressions. Effective AGY
route proof, provider-log exclusions, and the superseded-plan marker are also
updated. These changes close R8 and require one new complete round.

R9 used prompt SHA-256
7e8f42e7f5278f7ee8f52cb09ec9011be63cbd1594d1fa8323eb9422b81fc5bf;
its 198,571-byte shared prompt had an equal pre/post fingerprint. Claude and
fresh Codex were SAFE with Minor findings. AGY produced section-complete SAFE
content on Gemini 3.1 Pro High but omitted the wrapper completion sentinel, so
the wrapper failed closed with extraction-error/no-sentinel and the leg was
invalid. The accepted fixes align bootstrap help, mark the legacy approval plan
superseded, and restore a no-final-newline owner config byte-for-byte. Those
changes close R9 and require a fresh-ID complete round with the lightweight JSON
result contract.

The historical packet-era R15 packet-first dispatch was cancelled before provider execution.
The historical packet-era R14 archive does not cover these bytes. The later worktree-first
round is evidence but not PASS because accepted findings changed the reviewed
bytes.

Finish source and test verification first. Confirm that ordinary codex resolves
on-request/auto_review and that refreshed exact wrapper rules resolve to prompt,
not allow. Verify fresh-session skill exposure and the requested three-provider
spike only after the applicable install/provider authorization is established.
Do not continue Argus until triad review is working, then report and ask the owner
before resuming it.
```

## Current route and latest invalid round

Use the catalog selector `gemini-3.1-pro-high` only as authenticated `agy
models` evidence. The exact outbound `Gemini 3.1 Pro (High)` route uses no
`--effort`; preflight reports requested argv values, exposed identity must
agree, and absent identity is `unexposed` once. Adopt the base slug with
`--effort high` only after a fresh acceptance and identity probe.

The prior R11 formal round recorded prompt SHA-256
`85414ff304e4b6f5f583de08da71d9fefcce6e86f669af64caf3ab6646d60394`, diff SHA
`0711255908f5dde70bbf19e09bb85b8b6a36fcc4b6215d0306a73075c07f2574`, equal
fingerprint `d810c09e5e4d751ad9303d1469ebaabfdb124ab08e86c26202cea753fb47df84`,
fresh Terra SAFE, Claude Opus SAFE with three Minor findings, AGY display-label
route SAFE, and 644 tests plus 6 subtests.

R12 handoff ledger:

- review ID: `20260723-r11-minor-hardening-r12`
- prompt SHA-256: `4d771be60a54a698dea7fe080ad98ab335106b7befe6ec6d4a5baed1450cac01`
- equal pre/post fingerprint: `cd3885d0f85631320409ba8eb12fe016dd279dad7e731059a70f8255c20dd454`
- fresh Codex: `NOT-SAFE` with one Major
- Claude: `SAFE` with six Minor findings
- AGY: `extraction-error`, post-dispatch, fallback-ineligible (exit 1, phase post-dispatch-cleanup)
- repair analyzer: `escalate`, proposal null/no classifier change
- local verification: 648 passed plus 6 subtests; leader verification: 648 passed + 6 subtests
- round status: invalid and requires a fresh complete round

No verified R10 hash is available, so no value is inferred. A fresh complete
three-family round is required after these bytes.

## R13 invalid formal round

Do not promote this documentation reconciliation:

- review ID: `20260723-r11-minor-hardening-r13`
- prompt SHA-256: `a2396c1afb614a61bbbc29a5e75612f76bd452c3f7679c5f8312b9de530db177`
- equal pre/post fingerprint: `577770d8c4fd05ef3b0271ad21044fcd9dc173a0b7425608af035136d375ad8a`
- fresh Codex: `NOT-SAFE` with one Major
- AGY: `extraction-error`, post-dispatch, fallback-ineligible
- repair analyzer: `escalate`, proposal null/no classifier change
- Claude: invalid fenced JSON framing; diagnostic `SAFE` with two Minor findings
- round status: invalid and requires a fresh complete round

## Task 5 pre-gate hardening

The initially documentation-only closure exposed a real partial-uninstall risk:
after manual registration removal, environment-fragment removal lacked the
original-existence provenance needed to preserve a pre-existing empty
`config.toml`. Lunar `/root/r13_task5_docs_reconcile` added a bootstrap-only
`--preserve-empty` gate with direct CLI and end-to-end regression coverage.
Implementation RED was `5 failed, 73 passed`; focused GREEN was `80 passed`, and
the broader repair/distribution regression was `148 passed in 6.36s`. Terra
specification and quality reviews approved with equal pre/post fingerprint
`085434c5e71fed85f44bf3c68908eb149644bc5705ca659f590a944ca8379b8d`.
Leader verification is `679 passed, 6 subtests passed in 156.35s`; Bash syntax
and both staged and unstaged diff checks pass. Run one fresh-ID complete formal
three-family round over these final bytes before resuming Argus. The owner has
limited that gate to one leader-prepared shared review directory containing
current approved production source, configuration, and documentation plus a
common task as the complete review input. Every leg receives the same directory
and task; no prompt inlines a diff or file body. Record one simple content
digest before dispatch and compare it after every required leg terminates; a
mismatch invalidates the round. Reviewers must not receive, open, or review test
source; local tests and the full-worktree mutation fingerprint remain leader
operations.

The R14-R17 ledger blocks below are historical-only records. Their path-list-era
next-run wording is superseded by the current shared-directory flow and must not
direct a future review.

## R14 corrected formal round

review ID: 20260723-r11-minor-hardening-r14
prompt bytes: 147,929
prompt SHA-256: f5e69a2095449b28b413c87df390429adee19f7413c23d3b266a316a5fd0d74c
equal pre/post fingerprint: ea0f1264fe892c98eede5c3437a796b120df83b33cb3f42ccf450ceeea7835e7
AGY: SAFE, no findings, identity unexposed
Claude: SAFE with four Minor findings
fresh Terra: initial false Major retracted; corrected SAFE with no findings
round status: reviewed bytes SAFE; accepted Minor corrections change bytes and require a fresh complete round
SECURITY.md opt-out condition: when rules are opted out and no configured rules path remains, bootstrap may skip the native loader guard; the launcher's own scrub remains defense in depth.

The accepted bytes retain exact managed legacy profile and shell artifacts on
plain install, preserve ordinary codex, and keep the no-prompt allow posture
retired. Start a fresh complete round before resuming Argus.

## R15 invalid formal round

review ID: 20260723-r11-minor-hardening-r15
prompt bytes: 159,396
prompt SHA-256: e176aaa948488a42db5ee8a9be00db0c99d7cdbd79b2688b5daa04babe2c205e
equal pre/post fingerprint: 5acc6a14cc0886f268d20ef3745b574eee948531756146be2366a76efe28d21c
fresh Terra: NOT-SAFE with one Major formal test-scope finding
AGY: substantive SAFE, fenced JSON invalid, identity unexposed
Claude: NOT-SAFE with one Major, two Minor findings, and two open questions
round status: invalid and NOT-SAFE; accepted corrections change bytes and require a fresh complete round

Continue only after local verification and fresh SDD review. The next formal
plan/pre-merge round must use one identical non-test prompt across all three
families; normal SDD review remains responsible for relevant test source.

## R16 corrected formal round

review ID: 20260723-r11-minor-hardening-r16
external prompt bytes: 191,591
external prompt SHA-256: 465688443d27be45113aa6bbaba43162b609c039dc676dd5cc2220bb154db1bb
native prompt bytes: 191,437
native prompt SHA-256: ee923a22d3c2924281607924c0cc4316f898911b9935624a6cd96a5eafae5db6
equal pre/post fingerprint: 7f5021078cd769056a279ca864bbea0e1132a769f39a44c406e88158282de91d
AGY: initial false Major retracted; corrected SAFE with no findings; identity unexposed
Claude: SAFE with two Minor findings
fresh Terra: SAFE with no findings
round status: reviewed bytes SAFE; accepted Minor corrections change bytes and require a fresh complete round

Every leg received the same canonical worktree, objective, approved non-test
boundary, and identical leader-captured non-test evidence; only the
route-specific result-contract suffix differed.

1. AGY preflight now publishes the already-constructed ordered route_args;
   Lunar RED was two KeyError: route_args failures, focused GREEN was 2 passed,
   packet-context GREEN was 52 passed, and fresh Terra task review was spec PASS
   / quality Approved.
2. The historical R16 handoff count was 687 passed plus 6 subtests in 158.50s.

Argus remains gated until one new complete formal round passes over the
corrected bytes.

## R17 invalid formal round

review ID: 20260723-r11-minor-hardening-r17
external prompt bytes: 195,916
external prompt SHA-256: 3f9bb28ab8b543fa8ce9061532a18dad7bb4de99b687e568f76327de5cbf0db8
native prompt bytes: 195,762
native prompt SHA-256: c0651b1b4dbcf89e71618ff841184613ea3bce6979040da0762dc0dd956fcc22
equal pre/post fingerprint: 726e1fe0d614e08a0be3415d50f56b7add81bbe271bc8345948e15c674fd0bfa
fresh Terra: SAFE with no findings
Claude: SAFE with two Minor packet-era round-label findings
AGY: extraction-error, provider exit 0, wrapper exit 1, post-dispatch-cleanup after 198.3s, fallback-ineligible
round status: invalid because the required AGY leg is missing; Argus remains gated

The shared canonical worktree, approved non-test boundary, and identical
leader-captured non-test evidence were preserved; only route-specific result
suffixes differed. The provider run-log was not read or sent. The two Claude
Minor wording corrections are the packet-era qualifications above. A new
fresh-ID complete three-family round is required; do not claim that retry has
occurred.

R17 root-cause correction: the 195,916 total external prompt bytes included
187,420 inline diff bytes. AGY truncated the input tail, so the route-specific
result contract and completion marker were lost; the wrapper correctly failed
closed. The next round uses path-list-only transport: the canonical worktree,
identical approved non-test path list, fixed read-only Git commands, and hashes
of locally retained status/diff evidence, with no inline patch or file body.

## R20 and 2026-07-24 current state

- Review `20260723-r11-minor-hardening-r20` ended with a fresh Terra `NOT-SAFE`
  verdict and one Major at `scripts/bootstrap.sh:1005` about inherited
  `HOME`/user-site `sitecustomize` or `usercustomize` before launcher line 1.
  Requested and actual model/effort were unexposed to that reviewer, there was
  no retraction, and round-level admissibility was leader-unexposed. R20 did not
  become `SAFE`.
- The product correction already present documents credential-compatible
  trusted-`HOME`/user-site mode in `README.md:60-64`, `README.ko.md:54-58`, and
  `SECURITY.md:152-157`, and emits a post-install warning at
  `scripts/bootstrap.sh:2238`. Regressions are present at
  `tests/test_bootstrap.py:1356-1361` and
  `tests/test_distribution_contract.py:798-830`. This is an explicit
  installer/operator trust boundary, not support for attacker-controlled
  `HOME`.
- Owner workstation acceptance on 2026-07-24 retained global
  `default_permissions = ":workspace"`, selected `chaniri_dev` in the
  workspace, and retained `on-request`/`auto_review`. Ordinary development paths
  work; credential reads and workspace `.codex` writes are denied; strict
  doctor passed 17/17; a fresh session exposed all four TRIAD skills and
  executed a `.gradle` write probe; and the AGY 1.1.5 catalog plus the
  `provider_started=false` display-label preflight passed. This owner-specific
  profile is not a distributed plugin default.
- Fresh full local verification passed on 2026-07-24 with
  `709 passed in 152.64s`; `bash -n scripts/bootstrap.sh`, `git diff --check`,
  and `git diff --cached --check` passed. The prior SDD Terra review including
  tests was `APPROVED` with no findings; a fresh post-correction SDD Terra review
  and complete R22 formal gate remain pending. The formal shared review directory
  must physically exclude the exact test-source root
  `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/tests`;
  local leader tests remain required.
- On 2026-07-24 the owner authorized deployment of `0.2.529` only if the skill
  verification and all gates pass. No deployment has happened yet. This handoff
  does not claim that a commit, push, tag, release, or install occurred.

## R21 accepted documentation corrections

review ID: `20260724-triad-0.2.529-release-r21`
shared-directory pre-dispatch digest: `dc21a239796f28431afd455f8cc8b48c4e2a16a7b6435fe1bed5a831f6cd2f23`
fresh Codex: `SAFE`
AGY: `SAFE`; wrapper exit 0; provider exit 0; requested selector
`Gemini 3.1 Pro (High)`; no effort; runtime identity unexposed once
Claude: `SAFE`; wrapper exit 0; provider exit 0
round status: closed `SAFE`

Fresh Codex had one historical-status Minor; it was rejected because the dated
record is superseded. Claude had three Minors: the README audit-retention and
status-freshness corrections were accepted; the implicit Gemini fallback
`--sandbox` generalization was rejected because supported skill routes
explicitly pass sandbox and omitted-sandbox legacy behavior is outside the
owner-approved use.

R21 is closed `SAFE`, but it cannot be final because the accepted corrections
change bytes. A fresh R22 complete three-family round is required, and
deployment remains pending.
