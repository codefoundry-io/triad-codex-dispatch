# TRIAD Maintenance Decisions

Date: 2026-08-08

Formal-plan review: `20260808-triad-maintenance-items-formal-plan-r1`

Reviewed digest: `667582cc4c7a77d0f30ff98abed7376cbc9c0fc4417319137f76427ac87e8c7c`

Review outcome: three admitted `SAFE` verdicts and `ROUND_INTEGRITY_OK`.

## Decision 1: Keep the prepared-directory digest

Keep `_prepared_digest` in `bin/review_round.py` unchanged.

`git hash-object` provides a content blob identity but does not bind the complete relative-path
tree without another canonical manifest or Git-tree construction. Replacing the current walk would
therefore retain bespoke path framing while adding a Git process dependency. `_record` would also
remain because `_worktree_fingerprint` uses it independently.

The deterministic-tar alternative is not portable to the supported local environment. The
observed `bsdtar 3.5.3` rejects `tar --sort=name`; a portable archive digest would additionally need
explicit rules for timestamps, ownership, modes, directory entries, and archive format.

The retained digest binds sorted regular-file relative paths and SHA-256 content hashes. It rejects
symlinks and unsupported entries. It intentionally does not bind file mode bits or empty
directories. This is a leader-owned review directory bracketed by capture and verify, not a
hostile concurrently writable packet store. A new digest basis still requires a fresh round; this
decision does not add a compatibility shim.

## Decision 2: Keep the benchmark evidence tracked and distributed

Keep all 23 files below `benchmarks/review-policy/` in the repository and the clean-HEAD plugin
archive.

Five files are direct pytest inputs: `baseline-batched.json`, `cases.json`,
`focused-convergent-runtime.json`, `focused-convergent-report.json`, and
`fixtures/round-2/local_defect/validator.py`. The remaining 18 retain the planted-defect source and
correction rounds plus the skill-pressure evidence needed to reconstruct the focused-convergent
policy decision. `tests/test_review_policy_benchmark.py` now owns an exact 23-path inventory so the
extracted-archive test run rejects an accidental omission.

The measurements below were taken from clean commit
`8b2f66edae8af6fc9bd32cdf35cf4cbb3006879c`:

```text
git ls-files benchmarks/review-policy | wc -l
23

git ls-files benchmarks/review-policy | xargs wc -c | tail -1
10991 total

git archive --format=tar HEAD | wc -c
1515520
```

The evidence is approximately 0.7% of the uncompressed Git archive by file bytes. Moving it to an
evidence-only branch would make the recorded benchmark less reproducible and would break the
current package-test contract for negligible distribution savings. Distribution verification
archives clean `HEAD`, extracts those exact bytes, and runs the complete `tests` tree from the
archive.

## Decision 3: Record closure-selection pressure without a ceiling

Do not add a file-count or byte ceiling to `triad-cross-family-review`, and do not modify the skill.

The captured R46 baseline combined 24 planned provider calls, 465 patch artifacts, 93 impact paths,
and 186,634 prompt bytes before provider file reads. The focused-convergent runtime benchmark used
4,665 and 4,743 prompt bytes in its two rounds, with three calls per round and no batch artifacts.
Those observations show that the old batched architecture failed and the focused replacement
reduced pressure; they do not establish a universal safe closure threshold.

A mechanical ceiling could force one cross-file decision to omit required callers, consumers, or
governing documentation. If a concrete future closure is too large to review coherently, the
leader returns to the owner under the existing authorize-and-bound step and asks to narrow the
decision itself. Closure sizing remains a recorded leader cost, not a new runtime or skill rule.

## Scope of Decisions 1-3

These decisions change no wrapper, digest algorithm, benchmark evidence byte, packaging behavior,
or skill contract. The only executable change is the benchmark evidence inventory regression test.

## Formal Review Contract Remediation

The first maintenance pre-merge round,
`20260808-triad-maintenance-premerge-r1`, was integrity-valid but split: Claude returned
`NOT-SAFE`, while Google and fresh Codex returned `SAFE`. Leader reproduction confirmed a mismatch
between the prepared-directory recipe and the renderer's required `SOURCE_SHA256SUMS`, plus the
missing changelog entry and misleading benchmark-test name. The initial proposal to suppress
configured MCP servers was rejected by the owner. The superseding contract keeps installed MCP
read/search tools and existing user permissions available, while any mutation, external-state
change, or candidate execution invalidates the leg. Decisions 1-3 above remain unchanged.

Formal-plan R1 was also integrity-valid but split: Claude and Google returned `NOT-SAFE`, and fresh
Codex returned `SAFE`. Its reproduced findings were bounded plan corrections. R2 was invalid because
its manifest omitted four nested benchmark members. R3 used a repaired member list and returned
Claude `NOT-SAFE`, Google `SAFE`, and fresh Codex `SAFE`; the owner rejected its MCP-suppression
proposal and required the read/search-capable contract above. R4's three `NOT-SAFE` results are
advisory only because the directory omitted three public dispatch skills opened by the affected
distribution test. R5 repaired that closure; Google returned `SAFE`, while Claude and fresh Codex
returned `NOT-SAFE` with reproduced test-literal and plan-boundary corrections.

The admitted formal-plan round is `20260808-triad-formal-review-contract-plan-r6`, digest
`3d933f24fdec17d56c036f200c2620d88e079b7f36511e1d8cf78466817351c9`. Claude, Google, and fresh
Codex all returned schema-valid `SAFE`, and final integrity was `ROUND_INTEGRITY_OK`. Claude's four
Minor findings were accepted as bounded clarity corrections: retain the unavailable-tool open
question, use the exact prompt-contract anchor, expose `--formal-read-tools` in the Claude dispatch
skill, and load the prompt contract explicitly in its distribution test.

The exact post-edit fresh-agent characterization returned:

```json
{"source_sha256sums_required":true,"required_named_members":["TASK.md","SOURCE_SHA256SUMS","one readable canonical diff"]}
```

No commit, push, merge, install, tag, publish, or release action is implied by this remediation
record.

## Owner supersession: preserve read and search tools

Later on 2026-08-08, the owner superseded only the formal tool-selection part of the admitted R6
candidate. Formal review must not pass `--formal-read-tools` or otherwise suppress provider-native,
installed CLI, configured MCP, or approved web read/search tools. The prompt-controlled contract
still forbids file mutation, external-state change, and candidate code, test, build, hook, or script
execution. The digest, benchmark, closure-policy, manifest, verdict, and convergence decisions above
remain unchanged.

The packet-workflow bootstrap now provides unique-ID system-temp `prepare` and exact-root `cleanup`,
copies only an exact canonical-source member list, retains explicitly listed nested fixture files
named `TASK.md` or `REVIEW.diff`, rejects prior-round artifacts at capture, and sweeps only managed
roots inactive for strictly more than 30 days. The pre-R10 bootstrap checks passed with
`48 passed` and `454 passed`, respectively, under Python 3.12.13 and pytest 9.0.3.

Formal-plan R8 was integrity-valid but not admitted. Its reproduced packet lifecycle defects were
fixed through RED/GREEN tests. Formal-plan R9 was invalid because AGY denied
`shasum -a 256 -c SOURCE_SHA256SUMS` and produced no schema verdict; its other two legs are advisory
only. The exact managed R9 root was removed. At that time, an ambient owner-selected AGY setting
exposed init `permission_mode: "always-proceed"` and a same-route smoke verified the manifest. R12
later proved that relying on this ambient setting was not a durable headless route. The distributed
skills preserve installed CLI, MCP, read, and search tools and require a fresh-ID complete-round
restart after a denied or invalid leg.

The owner rejected R9's proposed stale-reclaim/allocation lock as over-design. The advisory race
requires concurrent reuse of the same review ID, while the approved workflow assigns every round
and retry a new unique ID and never reuses an earlier one. Existing exclusive root creation remains
the collision guard; no `flock`, lock file, registry, daemon, or coordination layer is added. The
bootstrap remains pending a fresh formal-plan triad and is not a release claim.

Formal-plan R10 (`20260809-review-workspace-lifecycle-plan-r10`) used 62 copied source members and
three current-round artifacts, for 65 manifest entries at digest
`53e97699dc22c1b445ef609fd9b96d6863eee0435d0c2256e6a720c2b3545db2`. Fresh Codex returned
schema-valid `SAFE`; Google and Claude returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`; exact cleanup returned `removed: true` and the root was absent. The next
candidate admits only two bounded corrections: bind rendered review ID to the lifecycle root ID,
and add exact executable commands/count expectations to the lifecycle plan. Provider capability or
permission gates, file-mode copying, empty-directory digest entries, and other lifecycle expansion
remain outside the approved design. The public review skill now reads the current `CHANGELOG.md`
release entry before packet preparation so these packet, tool, and cleanup corrections survive
compaction and restart. The current R10-correction candidate passes the exact affected command with
`87 passed` and the full suite with `456 passed` under Python 3.12.13 and pytest 9.0.3.

Formal-plan R11 (`20260809-review-workspace-lifecycle-plan-r11`) regenerated 62 current source
members, added three current-round artifacts, and validated a 65-entry manifest at digest
`1bf17ff99a4d40638b933d5d25539c460b3961b6a937f04805c2eace0f0b7fbd`. Google returned
schema-valid `SAFE`; fresh Codex and Claude returned schema-valid `NOT-SAFE`; final verification
printed `ROUND_INTEGRITY_OK`; exact cleanup returned `removed: true`; the root and every other
managed `triad-review-*` root were absent afterward. The bounded R11 corrections exclude the
currently requested ID from stale sweeping, replace observed-afterward test counts with an exact
collection ledger, add the missing configured-log-root RED/GREEN contract, align the Korean and
English local-data plan, and identify each command's working directory. No lock, registry, daemon,
provider permission change, MCP restriction, metadata copy, or empty-directory digest is added.
The post-R11 correction baseline passes the exact affected command with `88 passed`, the full suite
with `457 passed`, skill validation, `bash -n scripts/bootstrap.sh`, and `git diff --check`.

Formal-plan R12 (`20260809-review-workspace-lifecycle-plan-r12`) is invalid. Its 62-source,
65-manifest-entry packet had digest
`61ac021699779f1078f39c313ded11dfa1324e0f4b9f71f5e9dc2b9bd7ad600a`, but the live AGY init
event exposed `permission_mode: "request-review"`; the Google leg then auto-denied the `command`
tool and produced no verdict. The leader stopped the still-running Claude and fresh-Codex legs,
cleaned the exact R12 root with `removed: true`, and confirmed that no managed
`triad-review-*` root remained. No R12 result is admissible or reusable. Before another packet is
prepared, the packaged wrapper must use AGY's native headless auto-approval route without changing
owner settings or restricting installed tools.

Comparison with the working Claude-led wrapper, Google's documented AGY code-review invocation,
and a live A/B probe reproduced the cause: the Codex-led wrapper omitted
`--dangerously-skip-permissions`. Without it, init exposed `request-review` and the harmless command
was denied; with it, init exposed `always-proceed` and the command completed. The earlier
init-preflight direction was therefore withdrawn before any new round. The bounded correction is
one fixed argv element inserted internally by the wrapper; callers receive no permission option,
and no user setting, sandbox, allowlist, CLI, MCP, read, or search capability is changed. The
review prompt and round fingerprints retain the no-mutation boundary. The existing route test was
observed RED then GREEN, and removing the four withdrawn preflight cases restores the pre-Task-2
full-suite ledger to `457` cases. No R13 packet or reviewer leg predates this correction.

R13 (`20260809-review-workspace-lifecycle-plan-r13`) freshly copied 62 current source members,
added three current-round artifacts, and validated a 65-line manifest at digest
`6b975105866dbb69b6ae7065125b54a44ddad53512f1b5edf9582ad267b4beb9`. Claude, Google, and fresh
Codex each returned a schema-valid `NOT-SAFE`; final verification printed `ROUND_INTEGRITY_OK`;
exact cleanup returned `removed: true`; no managed `triad-review-*` root remained. The round is
formally invalid because the leader-written `TASK.md` incorrectly described a standard-tool digest
replacement as owner-approved. Durable Decision 1 above explicitly keeps `_prepared_digest`
unchanged. All R13 verdicts are advisory, the Google digest claim is refuted by that approved basis,
and the transient digest code/test change was removed before another packet. The current release
history now states the retained digest decision, and the review skill plus its existing contract
test prohibit inverting a retained or rejected release decision in `TASK.md`.

Independent canonical reproduction retained only bounded plan corrections: reconcile the Task 4
skill wording, define the configured-log-root case as a subprocess with the environment set before
`_common` import, keep the existing library test as the sole expected-root mismatch case, and
enumerate both README languages plus every changed test/contract in Task 1 and Task 5 evidence. The
pre-Task-2 ledgers remain 35 review-round, 88 focused, and 457 full-suite cases.

Claude's proposed future AGY permission-state gate was not admitted. It assumes a later AGY build
ignores the currently proven flag and would reintroduce the capability/preflight layer the owner
explicitly rejected. R13 itself exposed the internal
`--dangerously-skip-permissions` argv and the Google leg completed its tool-backed inspection. No
caller permission option, user-setting mutation, allowlist, sandbox, MCP restriction, or tool
suppression is added.

R14 (`20260809-review-workspace-lifecycle-plan-r14`) freshly copied the same 62-source closure and
three current-round artifacts, validated its 65-line manifest, and captured digest
`42cca50d2d6bfdea3e45902e2fed9e5ac561d1e908b7f52841921feea18b1095`. Fresh Codex returned
schema-valid `SAFE`; Google and Claude returned schema-valid `NOT-SAFE`. The leader reproduced the
shared README-enumeration finding and changed the canonical plan before Claude terminated. Final
verification therefore correctly returned `worktree fingerprint mismatch`; R14 is formally invalid
for both non-convergence and the leader sequencing error. Exact cleanup returned `removed: true`,
the root is absent, and no R14 result is reused.

The reproduced bounded corrections name both README languages in Task 1, add one planned Task 3 case
that rejects a managed-root descendant unless it is the exact `shared/` child, update every
downstream count ledger for that case, and give Task 5's Git checks a literal working directory.
Future evidence describes the retained-decision protection accurately as a documented skill rule
pinned by a contract test. It does not claim a semantic TASK-versus-decision comparator, and no such
new mechanism is added.

R15 (`20260809-review-workspace-lifecycle-plan-r15`) freshly prepared the complete 62-source
direct-reader closure plus three current-round leader artifacts, validated a 65-line manifest, and
captured digest `cc8623c2bc2fb44ffdd655d598f7de1e4f1c17d497b26903224a12b6d4574364`.
Fresh Codex and Google returned schema-valid `SAFE`; Claude returned schema-valid `NOT-SAFE`.
Final verification printed `ROUND_INTEGRITY_OK`; exact cleanup returned `removed: true`; the root is
absent and no R15 result is reused.

Independent canonical reproduction retained only bounded plan corrections: four planned
packet-validation RED cases with amended downstream counts, explicit Task 1 and Task 5
direct-reader closure, the exact managed-descendant fail-closed implementation rule, isolated
`TMPDIR` for every new subprocess test, and smoke-packet inventory assertion before cleanup. R14's
actual leader sequencing defect also caused one workflow correction before another dispatch. The
public skill now forbids canonical worktree mutation until all required legs terminate and verify
prints `ROUND_INTEGRITY_OK`; the existing distribution-contract test was observed RED then GREEN,
so collection counts remain unchanged. No provider, permission, MCP, digest, benchmark,
closure-ceiling, or coordination change is admitted.

R16 (`20260809-review-workspace-lifecycle-plan-r16`) freshly prepared the same 62-source
direct-reader closure, three current-round leader artifacts, and 65-line manifest at digest
`1cdebe33ab207b67e79c221e71378910d8c5f0115f6fc71f4467d9ffbec2ce73`. Google returned
schema-valid `SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`; final verification
printed `ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; the root is absent and no R16
result is reused.

The bounded corrections update the restart handoff from stale `454 passed` to the current
`457 passed` baseline, make the single managed-descendant case exercise capture/render/verify,
preserve direct-child rejection for lifecycle-shaped roots, distinguish regression coverage from
genuinely RED behavior, mark the worktree-ordering assertion already satisfied, and require sibling
preservation in the planned smoke. Fresh Codex's `--preflight-only` removal proposal is refuted by
the reviewed bytes: that existing option emits only the AGY version/route receipt and is separate
from the rejected permission `--init-preflight` and `--expected-permission-mode` paths. The R16
leader task used an overbroad "or preflight" phrase; current release history now preserves this
distinction. No wrapper behavior, provider, permission, MCP, digest, benchmark, closure-ceiling, or
coordination rule changes.

R17 (`20260809-review-workspace-lifecycle-plan-r17`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line manifest at digest
`9f5da517d0b453cba98abb7a57989d2b837d382cbf84cb368653b1c72227a767`. Claude, Google, and fresh
Codex each returned schema-valid `NOT-SAFE`; final verification printed `ROUND_INTEGRITY_OK`.
Exact cleanup returned `removed: true`; the root is absent and no R17 result is reused.

Independent reproduction retained only bounded corrections within the approved design: add a
direct-cleanup foreign-UID rejection case and update the exact count ledger; state the approved
Task 3 managed-descendant fail-closed target in the durable design spec and current changelog; repeat the
isolated-`TMPDIR` constraint in Task 3; and classify the 62-member closure as direct readers versus
leader verification/release tooling and the governing repair protocol. Google's activity-refresh
and explicit-log-root observations concern implementation already assigned to Tasks 3 and 4, not
the current formal-plan admission. Its proposed `--formal-read-tools` addition is rejected because
it contradicts the owner-approved unrestricted-tool decision. No runtime, provider, permission,
MCP, digest, benchmark, closure-ceiling, or coordination behavior changes in this correction.

R18 (`20260809-review-workspace-lifecycle-plan-r18`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line manifest at digest
`e006e22e647727adf06869a8c1e8c0f3e13b8d9024573621d152a348dbe4c762`. Fresh Codex returned
schema-valid `SAFE`; Claude and Google returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; the root is absent and no R18 result
is reused.

Independent reproduction admitted only wording and executable-plan corrections. The R18 task had
incorrectly described the explicit round log root as an absent-variable default and attributed
sibling proof to the skill. The next task states that the leader sets the variable and the CLI
smoke proves sibling preservation. The current changelog no longer claims the planned managed-
descendant rule is already implemented. Task 3 names its genuinely RED managed-descendant case,
classifies three activity-refresh parameters as RED and six negative parameters as regression
coverage, and specifies deterministic foreign-UID simulation. Task 4 pins a failing `RunResult` for
the explicit-log-root test and plans exact-root absence plus sibling-preservation confirmation in
the public skill.

Google's proposed new cases and count increases were rejected after canonical reproduction. The
current 35-case baseline already covers duplicate members, `.git`, CR, same/different-ID isolation,
concurrent leaf/parent symlink replacement, invalid-ID/symlink/non-directory sweep skips, and both
dangling-symlink removal races. The plan now labels those as retained baseline coverage rather than
new Task 2/3 cases. No runtime, provider, permission, MCP, digest, benchmark, closure-ceiling, or
coordination behavior changes in this correction.

R19 (`20260809-review-workspace-lifecycle-plan-r19`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line manifest at digest
`57edbe395adf87c3573d8e51df1b1811954a8f64874fe15928efd802f29c5f89`. Google and fresh Codex
returned schema-valid `SAFE`; Claude returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; the root is absent and no R19 result
is reused.

Both Claude findings reproduced as bounded plan wording gaps. Task 2 now preserves and names the
complete existing `PreparedWorkspace` receipt, including `prompts_dir` and `results_dir`. Task 4
now classifies only the explicit-log-root case as expected RED before its `_common.py` correction;
the collision case, two invalid-argument parameters, and lifecycle-sequence case are retained Task
0 regression coverage that may start GREEN, with state recorded per case. Exact count ledgers and
all runtime, provider, permission, MCP, digest, benchmark, closure-ceiling, and coordination
behavior remain unchanged.

R20 (`20260809-review-workspace-lifecycle-plan-r20`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line manifest at digest
`9145e98d097d78217a51355869427c31d7803458d306408f5d616e5d3931daeb`. Google returned
schema-valid `SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`; final verification
printed `ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; the root is absent and no R20
result is reused.

Reproduced corrections stay inside the approved lifecycle design. Task 2 now classifies all ten
new cases as Task 0 regression coverage that may start GREEN. The specification's existing "may
refresh" wording is pinned to best-effort activity refresh: only an existing regular non-symlink
marker is opened without following links, while a missing/unsafe marker or update error preserves
the completed action, output, and exit status. The existing three success-path cases add an unsafe-
marker subcase without changing collection counts. Task 4 now binds every Claude/Google call to
`TRIAD_DISPATCH_LOG_DIR=<returned-root>/results/_logs` and pins it in an existing distribution
assertion. The pending release-plan round now uses the lifecycle root rather than repository
`_runs/reviews` state. No provider, permission, MCP, digest, benchmark, closure-ceiling, registry,
lock, or coordination behavior changes.

R21 (`20260809-review-workspace-lifecycle-plan-r21`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line manifest at digest
`8d17f52dd1c5e2d41a4c27c0873d43f419941e683e5611c8578d5570e16b4333`. Google returned
schema-valid `SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`; final verification
printed `ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; the root is absent and no R21
result is reused.

Reproduced corrections are plan declarations only. Task 3 now declares its `CHANGELOG.md` update;
the unsafe-marker case asserts that the link remains and both external-target bytes and mtime are
unchanged. The invalid-UTF-8 case uses raw bytes. Task 4 includes
`references/leg-contracts.md`, requires the exact round-owned log environment on every Claude, AGY,
and Gemini formal template, and extends an existing distribution assertion across both the public
skill and templates without a collected-case increase. The release plan labels its completed Task
4 `_runs/reviews` path as historical only and routes fresh reruns through the lifecycle CLI. Counts
and runtime, provider, permission, MCP, digest, benchmark, closure, and coordination behavior remain
unchanged.

R22 (`20260809-review-workspace-lifecycle-plan-r22`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line manifest at digest
`b7f21d976406e0ecd3cf2fc3e6767c3d4de5eafade951a3bc71dd9a7160ea6e9`. Google returned
schema-valid `SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`; final verification
printed `ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; the root is absent and no R22
result is reused.

Bounded plan corrections add no collected cases: managed-root-self and non-`shared/` paths share
the existing lifecycle-operation case; missing-marker success joins each existing activity success
parameter; Task 2 drops two undescribed documentation surfaces; and retained fallback tests remove
the import-time log environment explicitly.

The owner approved the minimal resolution of the remaining R22 ambiguity. `prepare` creates the
existing `.last_activity` only after every exact source copy succeeds. Sweep uses marker mtime only
when that marker is regular and non-symlink, and root mtime when it is absent or unsafe. A successful
lifecycle operation whose marker is missing or unsafe does not follow or recreate it; it makes one
best-effort refresh of the exact managed root mtime. Failure to update an existing regular marker
does not trigger a second fallback. Every refresh failure preserves the completed operation result.
This adds no sentinel, registry, lock, or test count.

R23 (`20260809-review-workspace-lifecycle-plan-r23`) was invalidated before dispatch when `capture`
rejected leader-generated `SOURCE_SHA256SUMS` paths beginning with `./`. Exact cleanup returned
`removed: true`, and no managed review root remained. The existing distribution test now pins the
skill's canonical manifest path format to a POSIX path relative to `shared/` with no leading `./`;
its RED failure and GREEN pass were recorded without adding a collected case. The full 16-case
distribution module and skill validation also pass. No R23 packet or result is reused.

R24 (`20260809-review-workspace-lifecycle-plan-r24`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`550c13e3bfa057b6da5e9a0c56b3f58c37e4a833fdcaffc3eaf2c70c84706176`. Google returned
schema-valid `SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`; final verification
printed `ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; no managed root remained and
no R24 packet or result is reused.

The reproduced corrections add no mechanism or collected case. The existing complete-layout case
will observe `.last_activity` absence from inside the copy helper before asserting its post-copy
presence. Root-mtime fallback is limited to a missing or structurally unsafe marker; failure to
update an existing regular marker remains a plain best-effort failure, and an inspection error is
skipped and reported. Task 4 will bind the existing internal AGY flag to accurate README and
`SECURITY.md` wording through an existing distribution case, transition the pending lifecycle
changelog claim only after GREEN, and mark the already-landed release-plan reconciliation as such.

R25 (`20260809-review-workspace-lifecycle-plan-r25`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`d3ded087d74eb35f134cade57f2e62d91aba22553d8d33419c9060d2fac4bc77`. Google and fresh Codex
returned schema-valid `SAFE`; Claude returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; no managed root remained and no R25
packet or result is reused.

The reproduced R25 corrections change no design or collected count. Each existing activity-success
parameter resets root mtime after marker mutation, distinguishes regular-marker root non-refresh
from missing/unsafe fallback refresh, and includes regular-marker update failure as another subcase.
The existing managed-prefix baseline case includes marker-inspection failure as a skipped/preserved
subcase. The complete-layout name is explicitly one of Task 2's new cases, and explicit log-root
configuration means a present non-empty import-time value, matching current `_common.py` truthiness.

R26 (`20260809-review-workspace-lifecycle-plan-r26`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`da39777700c1f21d8935c714c9066ae345b718fedab9e56b6a5c32975fd26ec5`. Claude, Google, and fresh
Codex returned schema-valid `NOT-SAFE`; final verification printed `ROUND_INTEGRITY_OK`. Exact
cleanup returned `removed: true`; no managed root remained and no R26 packet or result is reused.

Accepted R26 corrections remain subcases or wording inside the fixed ledger: the regular-marker
update-failure subcase pins marker mtime and write-intent opening; the root-mtime sweep case includes
absent, symlink, and unsupported markers; source-parent and malformed-manifest branches join existing
planned cases; and Task 4 wording matches its single module command. Google's unexpected-member
claim is contradicted by the existing prior-round-artifact regression. The hard-link marker proposal
is rejected as a new `st_nlink` validator outside the owner-approved leader-owned-root and regular-
non-symlink marker boundary. No count or lifecycle mechanism changes.

R27 (`20260809-review-workspace-lifecycle-plan-r27`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`dde39feb860b58a9b1c53416ddc93d5152c7cbd9aa07128437367ab80cee07af`. Claude and Google returned
schema-valid `SAFE`; fresh Codex returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; no managed root remained and no R27
packet or result is reused.

The reproduced correction reuses the existing lifecycle packet validator before verification can
succeed and folds a digest-matching verification subcase into the one planned manifest inventory/
syntax case. Claude's Minor findings clarify existing blank-line normalization, the ordinary non-root
premise of the permission-failure subcase, and the no-fallback refresh inspection-error branch. Test
counts, lifecycle mechanisms, provider tools, permission behavior, and owner boundaries are unchanged.

R28 (`20260809-review-workspace-lifecycle-plan-r28`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`2123e0b1c9214b4bef76be079a7c15aaa5f89904650f25f8bbcd923d5396eb83`. Google and fresh Codex
returned schema-valid `SAFE`; Claude returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; no managed root remained and no R28
packet or result is reused.

The reproduced correction marks the existing digest-matching verification subcase as mandatory RED
and adds one pending changelog target for the already approved verify-side reuse of the existing
packet validator. Both transition only after GREEN. No case count, mechanism, or boundary changes.

R29 (`20260809-review-workspace-lifecycle-plan-r29`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`b66260299989b97dfe913070d45520be57ab6fafe0918612f5939936fc512467`. Google returned schema-valid
`SAFE`; Claude and fresh Codex returned schema-valid `NOT-SAFE`; final verification printed
`ROUND_INTEGRITY_OK`. Exact cleanup returned `removed: true`; no managed root remained and no R29
packet or result is reused.

The reproduced corrections keep all counts and mechanisms fixed: Task 0-supplied lifecycle cases are
explicitly GREEN-eligible regression coverage; the existing activity-success parameters gain a
deterministic marker-inspection-error subcase; and the planned import-time configured-log-root boolean
uses the existing test snapshot/restore contract. Google's packet-description Minor is packet-only.

R30 (`20260809-review-workspace-lifecycle-plan-r30`) freshly prepared the same 62-source closure,
three current-round leader artifacts, and a validated 65-line canonical manifest at digest
`58b02cf6eaedafebc37c90c7f19995504e1af53e6dfdb81ef27a759bedc45051`. Claude, Google, and fresh
Codex returned schema-valid `SAFE`; final verification printed `ROUND_INTEGRITY_OK`. Exact cleanup
returned `removed: true`; no managed root remained. The formal plan gate is admitted and no R30
packet or result is reused.

Claude's SAFE Minor findings are execution clarifications only: distinguish closure-reproducible
counts from full-suite totals, pin the in-process temp base, reset root mtime after marker mutation,
record Task 2 pre-implementation state per case, and distinguish macOS execution from Linux API/gate
analysis. No case, mechanism, provider behavior, or owner boundary changes.
