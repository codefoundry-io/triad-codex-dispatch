# Triad Codex Dispatch current state

Updated: 2026-07-24

## Authoritative checkout

- Development root: `/Users/chaniri/codex_workspace`
- Product worktree:
  `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`
- Branch: `release/0.2.529`
- Local `HEAD`: `f0376dfc34006e0ee73e6ea4673a0d7f1c4a8586`
  (`feat: streamline worktree-first triad review`)
- This branch has no configured upstream. The worktree contains staged release
  edits plus the current unstaged simplification and Agent Review corrections.

Preserve the unrelated dirty checkout at
`/Users/chaniri/triad-codex-dispatch`. Do not reset, clean, copy over, merge
into, or otherwise modify it.

Do not commit, push, merge, release, or create a pull request as an incidental
verification step. Git history and remote-state mutations remain separately
authorized and may present an automatic security review approval request.

`codex plugin list --json` reports the local plugin enabled at `0.2.529` from
this worktree. The plugin cache and managed launchers/rules were refreshed: the
three exact wrapper rules resolve to `prompt`, and no dedicated profile or
`codex-triad` shell entry exists. Bootstrap preserved the owner's edited
`[shell_environment_policy]` table and warned rather than overwriting it; the
operator then manually reconciled only `inherit = "all"` and the documented
loader/language exclusions while preserving the existing
`[shell_environment_policy.set]` values. A fresh ephemeral ordinary-Codex
session exposed all four distributed triad skills.

## Shared-directory review contract

The current owner-operated formal-review path uses one leader-prepared shared
review directory containing current approved production source, configuration,
and documentation. Project instructions or the owner supply exact test-source
exclusions; do not infer them. If the exact boundary is unavailable, stop and
ask the owner.

Every leg receives the same directory and task. No prompt inlines a diff or file
body. Record one simple content digest before dispatch and compare it after every
required leg terminates; a mismatch invalidates the round. Formal plan and
pre-merge review excludes test source only when the exact project-or-owner
boundary is supplied. Normal SDD implementation review includes relevant test
source. Before a formal gate, classify every test failure as production defect,
test-case defect, or intentional specification change and resolve or approve it.
Provider legs use only their approved read-only inspection route and must not run
candidate code, tests, builds, hooks, or generated scripts.

The historical R14-R17 path-list attempts below remain preserved verbatim as
historical evidence; they do not direct the current shared-directory flow.

The bounded review routes are:

- fresh Codex: `gpt-5.6-terra`, `xhigh`, `fork_turns="none"`;
- Claude: `opus`, `xhigh`;
- primary Google route: authenticated `agy models` catalog selector
  `gemini-3.1-pro-high`; exact outbound model argument `Gemini 3.1 Pro (High)`
  with no `--effort`.

Sol- or Fable-class long-running models are not routine reviewers. They remain
conditional escalations for genuinely ambiguous, security-sensitive, deeply
integrative, or adjudication-heavy work. Gemini is fallback-only after proven
pre-submission agy route unavailability.

The shipped distribution carries no qualifying enforcement proof, so formal
Gemini fallback remains unavailable. Ordinary/non-formal fallback remains
available after proven pre-submission agy unavailability. The canonical admission
details are in the
[formal reviewer routing contract](../../skills/triad-cross-family-review/references/reviewer-routing.md).

## Agent-review distribution contract

The normal human-run `scripts/bootstrap.sh --install` keeps ordinary `codex` and
installs exact managed-launcher `prefix_rule` entries with
`decision = "prompt"`. It does not install a dedicated profile or replace the
owner's approval, reviewer, sandbox, or Auto-review policy.

That combination routes eligible exact Claude, agy, and Gemini wrapper calls to
Codex Agent review instead of bypassing review or repeatedly asking the owner.
The generated justification identifies an owner-authorized triad review and
excludes credentials, tokens, cookies, authentication files, environment dumps,
provider logs, and unrelated paths.

Agent Review requires `approvals_reviewer = "auto_review"` and an interactive
approval category. `approval_policy = "on-request"` is sufficient. If the owner
uses a granular approval policy, both `granular.rules = true` and
`granular.sandbox_approval = true` are required; other granular choices remain
owner-owned. A false category is rejected before Agent Review sees the request.
Do not auto-install `[auto_review].policy`; it would replace owner instructions
and cannot override a managed guardian policy. `/approve` is only a narrow
owner override for one exact recorded denial.

The legacy profile generator remains explicit opt-in migration compatibility.
It is not the normal start path.

An explicit owner invocation of the matching triad skill authorizes the named
provider review calls once while provider, destination, worktree, scope, and
data boundary remain unchanged. Agent review is the execution-time security
decision. Commit, push, install/update, merge, release, publication, and any
other provider remain separate owner decisions.

## Accepted AGY upstream behavior

Commit `94a24cb2e59972cd8fccefd06c05a6a7b77166b8` was reviewed functionally,
not merged as Git history. The combined local change ports only its safe
fail-closed behavior:

- a zero-exit own-line `<truncated N bytes>` or `<truncated N lines>` answer is
  quarantined as `truncated-answer` with terminal exit 65;
- nonzero vendor exit remains `vendor-error`, and truncated JSON never enters
  Pydantic validation or schema repair;
- a required formal agy leg with this result is invalid and must request a new
  bounded, compact result; post-dispatch truncation does not enable Gemini
  fallback; and
- the upstream generic `write_file`/sandbox-relaxation workaround, version and
  changelog changes, and upstream Git-history merge were rejected.

## Verification evidence

The current workspace-root login shell resolves
`/opt/homebrew/opt/python@3.12/libexec/bin/python3`, using Python `3.12.13` and
pytest `9.0.3`; no package was installed.

- TDD RED: the old skill required a code-complete archived packet and could not
  satisfy an existing-worktree-only scenario.
- Fresh Terra/xhigh pressure test: GREEN. It selected the existing worktree,
  identical trusted Git diff, affected-unchanged tracing, exact three routes,
  pre/post fingerprint, and no packet/list/repeated-approval workflow.
- Second-round correction set: `8 passed in 11.49s`.
- Bootstrap, repair transaction, migration, and distribution bundle:
  `368 passed`; two temporary-Python children were killed by macOS and both
  affected cases immediately passed alone (`2 passed in 0.51s`).
- Latest focused preserve-empty, repair-transaction, registration, and
  distribution regression: `148 passed in 6.36s`.
- Historical R16 handoff full suite: `687 passed plus 6 subtests in 158.50s`.
- Native codex-cli `0.145.0` evaluator: each managed launcher matched `prompt`;
  raw/repository/shell/Python negative forms matched no rule. The corrected
  generator never emits a global `allow`, including when a legacy profile uses
  `approval_policy=never`.
- `bash -n`, `git diff --check`, and `git diff --cached --check`: passed.

The earlier macOS process kill occurred when tests hard-linked/copied the signed
Homebrew Python executable into synthetic whitespace/oversized paths. The test
fixture now copies and ad-hoc signs that temporary executable on Darwin; product
bootstrap behavior is unchanged and the final combined suite passes.

## Cancelled packet gate and external-state boundary

The historical packet-era R15 packet-first formal dispatch was cancelled. A later live
worktree-first round used one identical prompt with Claude Opus/xhigh, agy
`gemini-3.1-pro-high`, and fresh Codex Terra/xhigh. AGY returned `SAFE`; Claude
and Codex returned `NOT-SAFE` and identified the stale README profile commands,
global `allow` leak, legacy shell/profile mismatch, and loader-environment guard
gap. Its pre/post fingerprint matched. The round is closed because its findings
required source changes; it is not a formal PASS.

A second complete worktree-first round kept an equal pre/post fingerprint. AGY
returned `SAFE`; fresh Codex found the unchanged hand-maintained migration rules
still used `allow`; Claude found the initially-absent config registration-order
failure plus security/documentation residuals. Those findings were reproduced,
fixed, and covered by tests. Because bytes changed again, that round is also
closed and cannot be promoted to PASS.

The next full-input attempt had `SAFE` AGY and Codex legs but the Claude leg hit
its 600-second wrapper limit, so the complete round was invalid. A compact
zero-context-diff rerun kept the same direct-worktree inspection contract and an
equal pre/post fingerprint. AGY returned `SAFE`; Codex and Claude found the
remaining public smoke/profile wording and a fresh-layout registration parser
that rejected an owner-edited policy or appended owner key. Those findings were
reproduced and fixed. Registration is now an exact provenance block recognized
at either legacy or fresh position while every surrounding owner byte and the
installer-added separator newline round-trip exactly. Because bytes changed,
that round is also closed and not PASS.

The next compact round used prompt SHA-256
`928a87c3e9c72ff9df870e54da7065dc2d03ff205cfa100c21dfa81e5d6e02da`.
Its pre/post fingerprint matched. AGY returned `SAFE`; Claude returned `SAFE`
with low-severity release-hardening observations; fresh Codex returned
`NOT-SAFE` because current migration guidance still described the exact rules
as allow-listed. The accepted corrections make a late repair-registration
failure suppress both rules and the legacy shell entry, remove the stale
allow-list wording, and clarify removal and compatibility notes. The two new
failure/documentation regressions are included in the 635-test full-suite result.
Because these fixes changed reviewed bytes, that round is also closed and not
PASS.

R6 used prompt SHA-256
`b396689de4524360a58072025f15caf53ffb35c4a1c848785691513f0e176b05`
and an equal pre/post HEAD/diff/status/untracked fingerprint. Claude and fresh
Codex returned `NOT-SAFE`; AGY returned `SAFE` but exposed an effective
`Gemini 3.6 Flash (High)` route despite the requested
`gemini-3.1-pro-high`, so that leg was invalid as well. The accepted findings
cover the missing native-child diff body, incomplete Agent Review exclusion
text, overstated executable-placement documentation, remove/runtime wording,
and stale rule examples. A control-plane spike reproduced agy's slug-to-default
mapping and proved that `Gemini 3.1 Pro (High)` reaches the intended backend;
The R6 historical record documented a temporary normalization to that effective
label; it is superseded by the current exact `--model`/optional `--effort`
passthrough. The refreshed installed wrapper then returned `Gemini 3.1 Pro` with
effort `High` and `ROUTE_SPIKE_OK` for the stable selector. These changes
invalidate R6 and require a new complete round.

R7 used prompt SHA-256
`68debad2d5acb7d15091941a717c70a65ffa1373facb5fa70148d34c6fe4ec79`;
the prompt itself contained the identical 141,294-byte leader-captured status
and diff, and the pre/post fingerprint matched. AGY returned valid `SAFE` on
`Gemini 3.1 Pro (High) / High`; Claude returned `SAFE` with minor findings;
fresh Codex returned `NOT-SAFE` by requiring one whole-bootstrap rollback
transaction. That demand was rejected because the governing bounded-repair
design explicitly excludes a whole-install/whole-remove transaction. Accepted
minor fixes remove the fresh-config registration-only backup, expose requested
and effective AGY model values in preflight, exercise the real dangling-
classifier check, align usage/security text, and add a regression proving that
bare-key edits to the managed registration already fail closed. R7 is closed
because accepted fixes changed bytes; the latest full suite covers 640 tests.

R8 used prompt SHA-256
`dcd22b1ffaa75d072148676a55cd07aa341faf3eb432e38e38217f1953578797`;
the exact 148,124-byte prompt contained the shared captured status/diff and the
pre/post fingerprint matched. AGY's content concluded safe but omitted the
required result sections, so that leg was invalid. Fresh Codex found removal of
a pre-existing zero-byte `config.toml`; Claude found that a rules opt-out could
skip the loader guard even when owner-maintained rules still enabled a managed
launcher. The accepted fixes preserve the pre-existing empty file, retain the
guard whenever the configured rules path still exists, strengthen effective
AGY route proof, align provider-log exclusions, and mark the old dedicated-
profile plan as superseded. R8 is closed because those fixes changed bytes.

R9 used prompt SHA-256
`7e8f42e7f5278f7ee8f52cb09ec9011be63cbd1594d1fa8323eb9422b81fc5bf`;
its 198,571-byte shared prompt and pre/post worktree fingerprint matched. Claude
and fresh Codex returned `SAFE` with Minor documentation and byte-round-trip
findings. AGY returned a section-complete `SAFE` answer on
`Gemini 3.1 Pro (High)`, but omitted the wrapper completion sentinel, so the
wrapper correctly ended `extraction-error/no-sentinel` and the leg was invalid.
Accepted corrections align bootstrap help with the owner-rules guard, mark the
legacy approval-profile plan superseded, and provenance-mark the separator
inserted before a managed config fragment so removal restores an owner file
without a final newline byte-for-byte. R9 is closed because the required Google
leg was invalid and the accepted fixes changed bytes.

The next formal round must use the existing worktree contract above after the
fixes and tests stabilize. Commit, push, merge to another branch, release, and
pull-request creation remain separate owner decisions.

## Current Google route and R12 ledger

The current Google route keeps the catalog selector `gemini-3.1-pro-high`
separate from the exact outbound `Gemini 3.1 Pro (High)` argument with no
`--effort`. Authenticated `agy models` is catalog evidence only. Preflight proves
argv construction and requested values; exposed identity must agree, and absent
identity is `unexposed` once. The base slug plus `--effort high` remains
unselected until a fresh runtime probe proves acceptance and identity agreement.

R11 prior formal-round evidence remains historical: prompt SHA-256
`85414ff304e4b6f5f583de08da71d9fefcce6e86f669af64caf3ab6646d60394`, diff SHA
`0711255908f5dde70bbf19e09bb85b8b6a36fcc4b6215d0306a73075c07f2574`, equal
fingerprint `d810c09e5e4d751ad9303d1469ebaabfdb124ab08e86c26202cea753fb47df84`,
fresh Terra SAFE, Claude Opus SAFE with three Minor findings, AGY display-label
route SAFE, and local verification of 644 tests plus 6 subtests.

R12 is the first post-hardening reconciliation record:

- review ID: `20260723-r11-minor-hardening-r12`
- prompt SHA-256: `4d771be60a54a698dea7fe080ad98ab335106b7befe6ec6d4a5baed1450cac01`
- equal pre/post fingerprint: `cd3885d0f85631320409ba8eb12fe016dd279dad7e731059a70f8255c20dd454`
- fresh Codex: `NOT-SAFE` with one Major
- Claude: `SAFE` with six Minor findings
- AGY: `extraction-error`, post-dispatch, fallback-ineligible (exit 1, phase post-dispatch-cleanup)
- repair analyzer: `escalate`, proposal null/no classifier change
- local verification: 648 passed plus 6 subtests; leader verification: 648 passed + 6 subtests
- round status: invalid and requires a fresh complete round

R12 cannot be promoted by repairing only its missing Google leg. No verified R10
hash is available, so no value is inferred.

## R13 invalid formal round

This documentation-only reconciliation record is not promoted:

- review ID: `20260723-r11-minor-hardening-r13`
- prompt SHA-256: `a2396c1afb614a61bbbc29a5e75612f76bd452c3f7679c5f8312b9de530db177`
- equal pre/post fingerprint: `577770d8c4fd05ef3b0271ad21044fcd9dc173a0b7425608af035136d375ad8a`
- fresh Codex: `NOT-SAFE` with one Major
- AGY: `extraction-error`, post-dispatch, fallback-ineligible
- repair analyzer: `escalate`, proposal null/no classifier change
- Claude: invalid fenced JSON framing; diagnostic `SAFE` with two Minor findings
- round status: invalid and requires a fresh complete round

## Task 5 pre-gate hardening

Lunar `/root/r13_task5_docs_reconcile` first closed the documentation contract
with RED `3 failed, 72 passed` and GREEN `75 passed`. Terra quality review then
found the environment-fragment remover could delete a pre-existing empty
`config.toml` after manual registration removal, because only the registration
retained original-existence provenance. The accepted bounded correction adds
bootstrap-only `--preserve-empty`; full uninstall now leaves a zero-byte file
when provenance is unavailable and lets repair lifecycle removal alone perform
provenance-backed file deletion.

The implementation RED was `5 failed, 73 passed`; focused GREEN was `80 passed`
and the broader repair/distribution regression was `148 passed in 6.36s`.
Terra `/root/r13_provenance_spec_review` and
`/root/r13_provenance_quality_review` both approved, with equal pre/post review
fingerprint `085434c5e71fed85f44bf3c68908eb149644bc5705ca659f590a944ca8379b8d`.
Leader verification is `679 passed, 6 subtests passed in 156.35s`; Bash syntax
and both staged and unstaged diff checks pass. These bytes have not passed a
complete formal three-family round, so Argus remains gated pending a fresh ID.
The current gate uses one leader-prepared shared review directory containing
current approved production source, configuration, and documentation plus a
common task as the complete review input. Every leg receives the same directory
and task; no prompt inlines a diff or file body. Record one simple content
digest before dispatch and compare it after every required leg terminates; a
mismatch invalidates the round. Test source stays out of reviewer scope; local
test execution and the full-worktree mutation fingerprint remain leader
operations.

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

The accepted containment corrections retain exact managed legacy artifacts on
plain install, qualify the rules-opt-out condition and launcher scrub, and
document the stale original config existed = true zero-byte fail-safe. These
reviewed bytes require a fresh complete round.

## R15 invalid formal round

review ID: 20260723-r11-minor-hardening-r15
prompt bytes: 159,396
prompt SHA-256: e176aaa948488a42db5ee8a9be00db0c99d7cdbd79b2688b5daa04babe2c205e
equal pre/post fingerprint: 5acc6a14cc0886f268d20ef3745b574eee948531756146be2366a76efe28d21c
fresh Terra: NOT-SAFE with one Major formal test-scope finding
AGY: substantive SAFE, fenced JSON invalid, identity unexposed
Claude: NOT-SAFE with one Major, two Minor findings, and two open questions
round status: invalid and NOT-SAFE; accepted corrections change bytes and require a fresh complete round

The accepted corrections restore the formal non-test boundary, keep normal SDD
test review explicit, make unselected unsafe legacy probes advisory without
following or changing them, and prevent provider command publication before a
successful repair lifecycle. These new bytes require a fresh complete round.

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
