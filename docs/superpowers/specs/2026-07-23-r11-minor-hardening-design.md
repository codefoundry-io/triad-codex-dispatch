# R11 Minor Hardening Design

Date: 2026-07-23

## Goal

Close the three non-blocking R11 findings without weakening the reviewed
worktree-first dispatch boundary, inventing provider identity, or changing the
owner's normal Codex configuration.

## Evidence and approved behavior

The owner authorized continuation with the AGY route that works today while an
upstream update is pending. Live AGY 1.1.5 probes established these distinct
facts:

- authenticated `agy models` advertises the catalog selector
  `gemini-3.1-pro-high`;
- `--model "gemini-3.1-pro" --effort high` is accepted but the controlled
  runtime probe reports Gemini 3.6 Flash High;
- `--model "Gemini 3.1 Pro (High)"` with no separate effort flag reaches the
  requested Gemini 3.1 Pro High route in the same controlled probe;
- the display label rejects a separate `--effort` argument.

Runtime self-report is evidence, not cryptographic attestation. The formal
Google leg therefore records three fields separately:

1. catalog/policy selector: `gemini-3.1-pro-high`;
2. exact outbound CLI model argument: `Gemini 3.1 Pro (High)` with effort
   omitted;
3. provider-exposed runtime identity: exact agreement when exposed, otherwise
   `unexposed` once.

An exposed conflict invalidates the leg. The wrapper preflight proves only the
outbound arguments and must not label a hard-coded transformation as an
`effective_model`.

## Selected approach

### 1. Honest AGY argument passthrough

Remove the wrapper's `_AGY_MODEL_ALIASES` mapping. `--model` is passed to AGY
byte-for-byte. Add an optional `--effort` argument restricted to AGY's current
`low`, `medium`, and `high` values and pass it through unchanged when present.

The current formal-review skills use the working display label and omit
`--effort`. The generic effort passthrough is deliberately not selected for the
current formal route; it exists so an upstream repair can be adopted through a
documentation/route change rather than another wrapper transport change.

After an AGY update, the leader reruns the exact base-slug probe. The formal
route changes to `--model "gemini-3.1-pro" --effort high` only after provider
acceptance and runtime evidence agree. There is no version pin and no inference
from release notes alone.

The preflight receipt retains `model` as the exact requested CLI value, adds
`effort`, and removes `effective_model`. It remains a parse/argv receipt, not
provider availability or identity proof.

### 2. Structural managed-registration ownership

`split_registration()` may encounter an exact generated block inside a TOML
multiline string as well as one syntactically active managed block. Textual
duplication alone is not malformed ownership.

For each supported `original_existed` block shape, collect every exact textual
occurrence. Remove one occurrence at a time and parse the remainder. An
occurrence is the managed candidate only when:

- the original parsed `[agents.triad-repair-analyzer]` value exactly matches the
  expected registration;
- the parsed remainder no longer contains that agent registration; and
- the only syntactically inert reserved marker lines are the canonical begin
  and end pair.

Exactly one qualifying candidate is managed. More than one qualifying
candidate, malformed reserved markers, or an ownership mismatch remains a
fail-closed refusal. The existing `before + after` byte-preserving removal is
retained.

### 3. Discoverable legacy shell-entry contract

Bootstrap help states that the legacy `codex-triad` shell entry is
migration-only and requires both
`TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1` and
`TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1`. Runtime rejects the shell-entry
opt-in unless the profile opt-in is also present; the help text makes that
paired runtime contract discoverable.
README files remain free of `codex-triad` because the distribution contract
intentionally excludes that legacy entry from normal operator guidance.

## Approaches not selected

- **Keep the hidden model alias.** This presents a local workaround as provider
  truth and makes preflight overclaim effective identity.
- **Use the official base slug immediately.** Current controlled execution
  silently reaches the wrong model, so provider acceptance alone is
  insufficient.
- **Pin AGY 1.1.5.** The observed behavior is the problem being bridged, not a
  version to preserve.
- **Treat any duplicate registration text as malformed.** TOML string content
  is data and does not establish managed ownership.
- **Advertise the shell entry in README.** It would conflict with the normal
  ordinary-Codex start path and the existing distribution contract.

## Verification

Use test-driven development for each bounded change:

- AGY command tests first fail on unchanged model/effort passthrough and honest
  preflight fields, then pass after the wrapper and skill contract change.
- The registration regression embeds the exact generated block in a TOML
  multiline string, proves first install, idempotent second install, and exact
  byte restoration on remove.
- The bootstrap usage test first fails on the missing paired-flag sentence and
  passes after the help-only change.

Run focused tests after every task, then the full pytest suite, Bash syntax,
`git diff --check`, distribution/skill contract checks, and a pre/post
worktree fingerprint. Because reviewed bytes change, close with a fresh
three-family read-only formal review over one identical leader-captured diff.

## R12 formal-review reconciliation

The first post-hardening complete round, review
`20260723-r11-minor-hardening-r12`, used prompt SHA-256
`4d771be60a54a698dea7fe080ad98ab335106b7befe6ec6d4a5baed1450cac01`.
Its equal pre/post fingerprint was
`cd3885d0f85631320409ba8eb12fe016dd279dad7e731059a70f8255c20dd454`.
The round is invalid: fresh Codex found a Major operator-route drift, AGY ended
`extraction-error` after provider dispatch, and Claude returned `SAFE` with six
Minor documentation findings. The registered repair analyzer returned
`escalate` with no bounded classifier proposal, so no classifier change or
Gemini fallback is justified.

The accepted reconciliation is documentation and contract-test only:

- current status, resume, and routing-verification guidance separates the
  advertised `gemini-3.1-pro-high` catalog selector from the exact outbound
  `Gemini 3.1 Pro (High)` display label and the exposed-or-`unexposed` runtime
  identity rule;
- the changelog describes unchanged model/effort passthrough and honest
  preflight fields rather than alias normalization or an effective-model claim;
- the old formal-routing implementation plan is explicitly superseded;
- English and Korean uninstall documentation include the pre-install-absence
  condition for deleting `config.toml`;
- the cross-family skill names the exact catalog selector inline; and
- the handoff ledger records the known R11 evidence, the R12 invalid result, and
  the current 648-test plus 6-subtest verification without inventing an
  unverified R10 record.

These corrections change reviewed bytes and require a fresh-ID complete round.
R12 cannot be promoted by repairing only its missing Google leg.

## R13 formal-review reconciliation

Review `20260723-r11-minor-hardening-r13` used prompt SHA-256
`a2396c1afb614a61bbbc29a5e75612f76bd452c3f7679c5f8312b9de530db177`
and equal pre/post fingerprint
`577770d8c4fd05ef3b0271ad21044fcd9dc173a0b7425608af035136d375ad8a`.
It is also invalid: fresh Codex found the unmarked 2026-07-22 routing design
still looked current, AGY again ended post-dispatch `extraction-error`, and the
repair analyzer again returned `escalate` with no proposal. Claude exited zero
but wrapped its JSON in Markdown fences, so that leg is invalid under the exact
result-shape contract; its diagnostic content was `SAFE` with two Minor
findings.

The initially accepted corrections were:

- mark the dated routing design superseded just like its paired plan;
- scope the documented empty/absent `config.toml` restoration guarantee to the
  case where both provenance-marked managed blocks remain intact; and
- record R13 exactly in the three handoff documents without promoting it.

Task-level Terra quality review then proved that documentation alone was not a
safe closure. `run_remove` removes the managed environment-policy fragment
before repair registration removal, while the fragment helper deletes the file
when that fragment is its only content. If a pre-existing empty `config.toml`
loses its registration block before `--remove`, the only original-existence bit
is gone and the fragment helper can delete the owner file without provenance.

The accepted bounded correction adds a default-false `preserve_empty` argument
to fragment removal and an internal `config-fragment --preserve-empty` CLI
flag. Full-bootstrap removal passes that flag: an empty remainder is published
as a zero-byte file with status `removed`. Without the flag, the standalone
helper retains status `removed-file` and deletes a fragment-only file. File
deletion in the full-bootstrap path therefore remains the responsibility of
repair lifecycle removal, which can read the intact registration provenance
and distinguish a bootstrap-created file from a pre-existing empty file.
This gives the partial-registration case a fail-safe empty-file result without
changing the normal intact install/remove round trip.

Regression coverage must start RED with a pre-existing empty config, a normal
install, manual removal of only the managed registration, and a full
`--remove`; GREEN requires the config still to exist as zero bytes. Direct CLI
coverage pins both default deletion and flag-enabled preservation. The same
repair also translates the Korean removal guidance instead of enforcing an
English prose fragment, gives every handoff the stable heading
`## R13 invalid formal round` and scopes ledger assertions from that heading to
the next level-two heading or EOF, and scopes the separate-diff assertion from
Task 5 Step 3 to Step 4 with the `MM` and net-diff constraints.

No classifier or fallback change is justified. The next complete round follows
the owner's current gate-review boundary: reviewers receive separate zero-
context staged and unstaged non-test diffs and may inspect only directly
related source, documentation, configuration, schema, and build files. They do
not receive, open, or review test source code. This still preserves
counteracted non-test `MM` bytes that a net diff can hide. The leader retains
test execution, result verification, and a full-worktree fingerprint—including
test changes—as local operational evidence.

## R14 formal-review reconciliation

Review `20260723-r11-minor-hardening-r14` used a 147,929-byte non-test prompt
with SHA-256
`f5e69a2095449b28b413c87df390429adee19f7413c23d3b266a316a5fd0d74c`
and equal full-worktree pre/post fingerprint
`ea0f1264fe892c98eede5c3437a796b120df83b33cb3f42ccf450ceeea7835e7`.
AGY returned `SAFE` with no findings; runtime identity was not exposed and is
recorded as `unexposed`. Claude returned `SAFE` with four Minor findings. Fresh
Terra initially reported an overlapping registration candidate, but that claim
confused the literal `original config existed = false` and `= true` forms.
Source tracing and a temporary leader probe proved one candidate and idempotent
second registration; the same reviewer retracted the finding and returned a
corrected `SAFE` result.

Three Claude items are accepted and one is narrowed:

- plain install with legacy opt-ins off must warn, without deleting anything,
  when an exact provenance-marked managed profile or managed `codex-triad`
  shell entry remains from an older install;
- `SECURITY.md` must state that the native loader guard is skipped only when
  rules are opted out and no configured rules path remains, while the launcher's
  own scrub remains defense in depth;
- the changelog and both READMEs need an explicit upgrade note for retained
  managed legacy artifacts, the profile-default flip, ordinary `codex`, and the
  retired no-prompt `allow` posture; the 0.2.529 content date becomes
  2026-07-23; and
- a pre-0.2.529 initially absent config may carry stale `original_existed=true`
  provenance because the old order created the environment fragment first.
  Current removal safely leaves a zero-byte file in that ambiguous upgrade
  state. This cannot be distinguished from a genuinely pre-existing empty file,
  so document the fail-safe outcome rather than infer absence or delete it.

The warning uses a new read-only managed-artifact inspection action because the
existing selected-artifact preflight intentionally refuses unmanaged files.
`managed-artifact --action inspect` returns `absent`, `managed`, or `unmanaged`
for a safe regular profile path without modifying it; unsafe ancestors,
symlinks, non-regular files, or read failures remain refusals. Shell inspection
uses the existing `preflight-remove` tri-state. The install warning gate runs
before `begin_command_group`, warns only for `managed`, silently retains safe
absent/unmanaged opt-out artifacts, and aborts before mutation on an unsafe or
refusing probe. It names exact managed paths and directs the owner to deliberate
`--remove`/reinstall or explicit legacy opt-in.

No automatic deletion, registration algorithm change, classifier change, or
provider fallback change is authorized. Accepted corrections change reviewed
bytes, so R14 is closed and a fresh complete round is required.

## R15 formal-review reconciliation

Review `20260723-r11-minor-hardening-r15` used a 159,396-byte non-test prompt
with SHA-256
`e176aaa948488a42db5ee8a9be00db0c99d7cdbd79b2688b5daa04babe2c205e`
and equal full-worktree pre/post fingerprint
`5acc6a14cc0886f268d20ef3745b574eee948531756146be2366a76efe28d21c`.
Fresh Terra returned `NOT-SAFE` because the distributed fresh-Codex formal
template still told reviewers to inspect tests. AGY's substantive JSON body was
`SAFE`, but Markdown fences violated the exact one-object output contract, so
the Google leg is invalid; runtime identity remained `unexposed`. Claude
returned `NOT-SAFE`: its Major showed that a read-only advisory probe makes
ordinary install fail on a symlinked shell RC or legacy profile, and its Minor
findings covered the stale paired-flag design sentence and value-dependent AGY
receipt extraction. Claude also opened the question whether repair lifecycle
failure leaves provider launchers published without the native loader guard or
prompt rules. Source adjudication confirmed that residual state and rejected
launcher self-scrubbing as an equivalent pre-exec control.

The correction distinguishes review and artifact boundaries explicitly:

- normal Lunar/Terra subagent-driven implementation review may and should
  inspect relevant test source so it can distinguish a product defect from a
  faulty test;
- a formal three-family plan gate or pre-merge gate receives identical
  leader-captured non-test status/diffs plus directly related non-test files
  only; no leg receives, opens, searches, quotes, or reviews test source;
- another advisory cross-family review follows its separately owner-approved
  data scope rather than inheriting either boundary implicitly; and
- the full-worktree mutation fingerprint still covers local test changes even
  when formal reviewer evidence excludes their contents.

The managed-artifact helper remains strict and no-follow. Selected profile,
rules, and shell-entry targets still abort on unsafe or unreadable paths before
mutation. A legacy artifact whose opt-in is off is different: it is observed
only to provide upgrade guidance. If that read-only probe refuses an unsafe or
unreadable path, bootstrap names the unselected path, warns that it was not
followed or changed, and continues the ordinary install. Safe exact managed
content retains the existing migration warning; safe absent or unmanaged
content remains silent. This removes the ordinary-install denial of service
without weakening any selected-target ownership check.

AGY argv construction remains exact free-string passthrough. The preflight
receipt records `args.model` and `args.effort` directly instead of rediscovering
them with `list.index`, so a value equal to `--model` or `--effort` cannot
corrupt the receipt. Provider identity admission remains separate.

Repair lifecycle success becomes a prerequisite for publishing the three
provider wrapper launchers. All ownership preflights still run before any
mutation. Classifier/profile/repair preparation may retain the deliberately
bounded partial-install semantics, but an injected repair registration failure
must roll back its analyzer/config/apply launcher and exit before the provider
command group is begun. No provider launcher, prompt rule, or shell entry may
remain from that failed run. This is a bounded ordering correction, not a claim
that the entire bootstrap lifecycle is one transaction.

The next Google prompt includes literal unfenced SAFE and NOT-SAFE object
examples; fenced JSON remains an invalid post-dispatch result and never enables
provider fallback. All accepted R15 corrections change reviewed bytes, so R15
is closed and a fresh complete round is required.

## R17 path-list-only formal-review correction

> Historical and superseded: this R17 path-list/OID/fingerprint design records
> the failed attempt and is retained only as immutable round history. The
> owner-approved minimal shared-directory correction below replaces its active
> guidance.

R17 proved that the formal prompt transport was carrying the review material at
the wrong layer. Its 195,916-byte external prompt consisted of 8,496 bytes of
instructions and metadata plus 187,420 bytes of inline non-test Git patch
content. AGY completed the provider process, but its stored USER_INPUT replaced
the tail with an explicit truncation notice. That removed both the route-specific
result contract and the wrapper completion marker. The wrapper therefore
correctly failed closed as `extraction-error`; accepting markerless output would
have admitted a review over incomplete input.

The owner approved a workflow correction and explicitly rejected prompt-byte
measurement or a wrapper size gate as unnecessary scope. Formal plan and
pre-merge prompts now carry only:

- the canonical existing worktree path;
- the review ID, objective, review kind, and approved non-test boundary;
- the guarded `HEAD` and Git-visible/nonignored fingerprint;
- the identical inline list of approved changed and related non-test paths;
- the fixed path-scoped read-only Git commands in status, staged-diff, then
  unstaged-diff order against exactly those paths; and
- hashes of the leader-captured status/diff evidence, not the evidence body.

The leader-only Git-visible/nonignored fingerprint uses unscoped
`GIT_OPTIONAL_LOCKS=0` status, staged diff, and unstaged diff commands in that
order, plus `HEAD` and the complete nonignored untracked inventory/content
hashes. The reviewer commands above are separately path-scoped to the inline
approved list. The leader alone renders, executes, captures, and hashes exact
Git commands; command strings and hashes are common receipt/navigation metadata,
not wrapper execution requirements. Wrapper legs use provider-enforced
reads/searches only, must not claim they ran or verified Git, and receive no
shell; only fresh Codex may run fixed commands when permitted. Verified deletion
provenance describes removals without deleted body content.

The leader freezes worktree mutations while the round runs and retains the
captured status/diff locally for reconciliation. Each reviewer reads the same
canonical worktree and computes or inspects the bounded diff itself. No prompt
inlines a patch or file body. No packet, copied worktree, separate generated
related-file artifact/allowlist, or source archive is created; the path list is the prompt's
explicit formal-review data boundary. Formal reviewers never receive or inspect
test source. Approved-path containment is prompt-controlled unless a provider
actually enforces it. Normal Lunar/Terra SDD review remains unchanged and
includes relevant tests.

The wrapper sentinel, extraction, classifier, fallback, timeout, model, effort,
and preflight receipt behavior remain unchanged. This correction addresses the
cause at review-input construction rather than adding a rare-case byte policy.

## Active shared-directory formal-review correction

The pending retry uses one leader-prepared shared review directory containing
current approved production source, configuration, and documentation. Every leg
receives the same directory and task; prompts do not inline a diff or file body.
Project instructions or the owner supply the exact test-source boundary. If that
boundary is unavailable, stop and ask the owner before dispatch. Record one
simple content digest before dispatch and compare it after every required leg
terminates. Normal SDD implementation review includes relevant test source, and
each test failure is classified as a production defect, test-case defect, or
intentional specification change.

The correction preserves the completed R14-R17 task and round history verbatim,
including its exact review IDs, prompt/fingerprint hashes, byte counts,
durations, and terminal verdicts. This local RED/GREEN correction must
stop before external execution; a later owner-authorized formal round may begin only after
local verification is green and must use the shared directory above.

## External-state boundary

This design authorizes only source, tests, skills, and documentation changes in
the existing `release/0.2.529` linked worktree. It does not authorize commit,
push, install, merge, release, pull-request creation, provider-log collection,
or modification of `/Users/chaniri/triad-codex-dispatch`. Existing dirty changes
are owner-owned and must be preserved.
