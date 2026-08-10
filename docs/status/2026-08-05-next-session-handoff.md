# TRIAD 0.2.533 Next-Session Handoff

Date: 2026-08-10

Status: skill-SOT Tasks 1 through 4 are complete. Attempt 5 was preserved as a
cleaned `WORKFLOW_DEFECT`; Attempt 6 returned GREEN, and an independent leader
lifecycle reproduction plus complete fresh verification passed. Combined
pre-merge r1 and r2 were superseded by bounded corrections. R3 ran to
completion, failed closed, was adjudicated, and its exact managed root was
cleaned. Two reproduced existing-design defects received bounded ordinary-agent
TDD corrections. The owner rejected the remaining required-criteria
validator/CLI proposal as format-centered overdesign: all current routes already
request JSON successfully, while substantive review meaning and leader
adjudication—not exact `criteria_checked` serialization—decide findings. No
validator change is pending; a fresh r4 over the corrected current bytes is the
next gate. The separate lifecycle plan remains paused between completed Task 9
and pending Task 10.

## 2026-08-10 active Task 4 completion and pre-merge boundary

The fresh live catalog exposed `triad-skill-executor`; its profile SHA-256 was
`819148f8f6c59bba5b24f9fd4d0acb01d116b78f2f68afb3ebde675a45bdcef3`, requested
`gpt-5.6-terra` at `high`, and used `fork_turns="none"`. Runtime metadata did
not independently expose actual model or effort. The canonical source hashes
were root `AGENTS.md`
`75aaa503c8588a39295e5646e69768f35d732355c75ad1bf14f13105dba57418`, source
`SKILL.md` `4aed9e7d831e9895f524a3fe84e2e1648c5dd2dcc76e014858f1cd6ac4b20811`,
`review-prompt-contract.md`
`3489d805d95af6736b4a44c750175df727a9108e243f3abddeea52399e613a31`, and
`leg-contracts.md`
`3c6a76ecc3061e9699f5d8b36e06436d65e46f58fe92ecd1db87b09b82b1ea15`.

Attempt 5 executor `/root/triad_skill_green_r5` with review ID
`4342324e-88b3-4677-96b9-c7380851e8e4` stopped at `manifest` exit `2` after
`prepare` exit `0`: it had skipped the source skill's explicit Flow step 3
write of `REVIEW.diff`, yielding `review_round: missing lifecycle packet
member: REVIEW.diff`. Write capability was present and not causal. Existing
source, tool, and tests already required both current `TASK.md` and
`REVIEW.diff`, so no edit was warranted. Supported cleanup returned
`removed: true`; exact managed-root and fixture absence and unchanged
fingerprints were independently confirmed. Leader reproduction
`c125a800-0d08-4b72-b213-3a91d7db249e` observed the same result and cleanup.

Attempt 6 executor `/root/triad_skill_green_r6`, review ID
`triad-skill-green-r6-20260810-6c1630fd`, returned valid `SUCCESS`, empty
failures, exactly the four canonical instruction sources, payload JSON
round-trip true, non-null managed paths, and one rendered prompt. All lifecycle
steps through cleanup self-reported exit `0`, no provider wrapper ran, and
capture digest was
`b4329708c044a1ea384868781039c224c946cb41864e1da762e16c4937a66b9b`.
Cleanup returned `removed: true` with no residue or sweeps; independent checks
confirmed the exact managed root and fixture absent and all fingerprints and
instruction hashes unchanged.

Leader reproduction under separate ID
`3862d6a7-f262-40e5-bab4-2e135a9f8781` independently observed `prepare`,
`manifest`, `capture`, `render`, and `verify` exit `0`, `file_count: 4`, capture
digest `5c979be061071da3a2a041a45afb25505bc1e0eaebbcc9cf32cf9febb83f07c7`,
`PAYLOAD_JSON_EQUAL`, and `ROUND_INTEGRITY_OK`. Supported cleanup returned
`removed: true`; its exact root and fixture are absent, no managed sibling
exists, and the canonical fingerprints remained unchanged.

Fresh verification used login-shell Python `3.12.13` and pytest `9.0.3`:
`py_compile` passed; review-round `78`, distribution-contract `16`,
distribution-verifier `8`, focused `132`, lifecycle smoke `1`, and full suite
`501` passed. Skill validation, `bash -n scripts/bootstrap.sh`, and root/plugin
`git diff --check` passed. The pre-documentation repository basis was root
`7554c18031ee51f6275ad4625a302971c1803c14` with status/diff fingerprints
`57614738d5858764aa49fb2ecfc61c56c8773416b3e56d81db55e4c6a6235753` /
`011b7afc437e687b4e1d662cb716def1f2b817200e717248086c7fdcbe8a6aee`, and
plugin `8b2f66edae8af6fc9bd32cdf35cf4cbb3006879c` with status/diff fingerprints
`32cc9d8fd7a29bf330732e6247aedcd070f42b9fba7581bb5765e827171fd4e4` /
`2f5f903f54ca64b3187db2bad6539700662adea68104d7ceafe9a4d3b903d1b0`.
This documentation edit necessarily changes the plugin diff, so later work
must establish a new post-handoff baseline.

### Combined pre-merge r1 and bounded correction

Round `20260810-combined-premerge-r1-d7027cbf-8c02-4049-8781-80f67ba27f78`
used digest `a5329e8abb117a758950eb0f55e3f41f666d552ea986eb0c70888087a0fee5b3`.
Google and fresh Codex were `SAFE` with no findings; Claude was `SAFE` with
four Minor claims; every leg ended with `ROUND_INTEGRITY_OK`. Leader
adjudication reproduced claims 1 and 3: stale `permission-unavailable` /
`truncated-answer` documentation in README, README.ko, and SECURITY, and
missing strict Claude/Google ID, family, and digest validator commands in
`leg-contracts.md`. Claims 2 and 4 were rejected as unsupported-route
hypotheses outside the approved scope. Since claims 1 and 3 required edits,
r1 is superseded and its verdicts cannot be reused. Exact cleanup returned
`removed: true`; the managed root is absent. The bounded TDD correction was
RED with two selector failures, then GREEN with `2 passed`; leader reruns were
`2 passed` and distribution-contract `16 passed`.

Historical continuation at that point: the observed post-correction verification used login-shell
Python `3.12.13` and pytest `9.0.3`: `py_compile` exit `0`; review-round
`78 passed in 6.32s`; distribution-contract `16 passed in 0.01s`;
distribution-verifier `8 passed in 1.04s`; established focused set `132 passed
in 7.33s`; lifecycle smoke `1 passed in 0.43s`; and full suite `501 passed in
128.52s`. The skill validator returned `Skill is valid!`; `bash -n
scripts/bootstrap.sh` and plugin `git diff --check` exited `0`. Post-document
distribution-contract `16` then passed before r2. R2 and r3 later ran as
recorded below; none of these historical results is a current admission.
Package, commit, install, and release gates remain blocked.
Preserve the Task 4 root cause as executor omission with write capability, not
a permission defect.

### Combined pre-merge r2 and bounded correction

Round `20260810-combined-premerge-r2-433c7ff0-a217-4660-9eb5-3cd01f5809d5`
used digest `8d851f9d70e76a682a567e9d66ff2ae0ca29654cb901a0e4a4334ae8f7d103b5`
over the fresh current 82-member/33-dirty/14-target closure with manifest 85.
Google was `SAFE` with no findings (157.4s), fresh Codex was `SAFE` with no
findings, and Claude was `SAFE` with two Minor findings (681.6s). Every result
passed strict ID/family/digest validation and final `ROUND_INTEGRITY_OK`.
Both Minors independently reproduced inside the approved design: the shared
renderer omitted the second credential/auth/environment/provider-log/unrelated-
path exclusion sentence required by `review-prompt-contract`, and configured-
root failed-result audit storage failure was hidden when the failure run-log
succeeded. r2 is superseded; verdicts are not reusable. Exact cleanup returned
`removed: true` and the managed root is absent. Two ordinary development
subagents, not the designated executor, performed independent TDD in
non-overlapping files: renderer selector RED then GREEN with module `78`, and
audit selector RED then GREEN with module `38`; leader reruns were exact
selectors `1 + 1` passed and modules `78`/`38` passed.

Historical continuation at that point: observed post-r2-correction verification used login-shell
Python `3.12.13` and pytest `9.0.3`: `py_compile` of `review_round.py` and
`_common.py` exited `0`; review-round `78 passed in 6.47s`; log-cleanup `38 in
1.23s`; distribution-contract `16 in 0.02s`; distribution-verifier `8 in
1.12s`; focused `132 in 7.40s`; lifecycle smoke `1 in 0.46s`; and full suite
`501 in 128.91s`. The skill validator returned `Skill is valid!`; `bash -n`
and `git diff --check` exited `0`. Leader post-document distribution-contract
`16` then passed and r3 ran as recorded below. R3 did not pass; package, commit,
install, and release gates remain blocked. Preserve the Task 4 packet-generation
root cause as executor omission with write capability, not a permissions defect.

### Combined pre-merge r3, bounded corrections, and owner decision

Round `20260810-combined-premerge-r3-965062bc-d585-4cef-8da0-80904dc806a8`
used digest `ef0df860cc5cd20a94e3348382a43ac95c3129f006725f2e53a3240523c19790`
over a fresh 82-member/33-dirty/14-target closure with manifest 85. Google
returned admitted `NOT-SAFE` in 216.9s, fresh Codex returned admitted
`NOT-SAFE`, and Claude returned admitted `SAFE` with three Minor findings in
910.0s. All three results bound the same ID/family/digest and every leg ended
with `ROUND_INTEGRITY_OK`. R3 is not a pre-merge pass and none of its verdicts
or packet material is reusable.

Leader adjudication rejected Google's AGY-flag claim as an explicit reversal of
the owner-approved wrapper-internal, child-only
`--dangerously-skip-permissions` route; no source or documentation removal was
authorized. Claude Minor 1 was also rejected as a previously adjudicated
diagnostic-name change: the approved success-path configured-audit failure
remains `run-log-unavailable`. Claude Minors 2 and 3 reproduced inside the
current design: destination-side preparation `OSError` was falsely reported as
source attestation failure, and Flow step 2 omitted the already-enforced
absolute canonical no-symlink/regular-member-list input contract.

Two ordinary development subagents, not `triad-skill-executor`, implemented
those bounded corrections test-first in non-overlapping files. The preparation
selector first exposed the destination misclassification; root review then
found the first correction's source-FD cleanup regression, which was separately
made RED for both source-race variants before the outer cleanup was restored.
The final focused result is `3 passed` and `tests/test_review_round.py` is
`79 passed`. The Flow-2 selector went RED then GREEN with `1 passed`, and
`tests/test_distribution_contract.py` is `16 passed`; skill validation and
`git diff --check` passed.

Leader verification after both corrections used login-shell Python `3.12.13`
and pytest `9.0.3`: `py_compile` exited `0`; the review-round/log-cleanup/
distribution-contract focused set was `133 passed in 7.48s`;
distribution-verifier was `8 passed in 1.10s`; lifecycle smoke was `1 passed in
0.49s`; and the complete suite was `502 passed in 128.69s`. The source skill
validator returned `Skill is valid!`; `bash -n`, root/plugin `git diff --check`,
and the final r3-root absence check exited `0`.

Fresh Codex's Major finding is rejected under the owner's clarified semantic
review contract. The three current formal routes already request JSON and r1,
r2, and r3 all returned validator-readable JSON; no formatting defect occurred.
`criteria_checked` spelling or exact-list coverage is not a separate admission
authority when the reviewer inspected the correct immutable current packet and
delivered a substantive review that the leader can understand and reproduce.
Do not add `--expected-criterion`, exact-copy prompt wording, Markdown parsing,
normalization, a new schema field, or another admission mechanism. JSON remains
the convenient requested transport; Markdown or fenced output is not by itself
a substantive review failure.

R3 result hashes were Claude
`1d0e44c2fcbe0fd3ff2ab53582a3b880b02b7a5193f1533fc0479c75656d3609`,
Google `12077fe11b25734c68c20a0176c8b76aa4433092e8b04e880aaace679400ff01`,
Codex `c3b600325a893ad6d2edae464ca59f03f49768513e3559946daa574c884ade20`,
and snapshot
`9a71f09bbb2c9a7a0a15fbefc295b572a9c0fd5f87b7af92a98616c34c9d3b04`.
Supported exact cleanup returned `removed: true`; the r3 managed root is absent
and no managed sibling was changed. Before either correction, the canonical
status/diff fingerprints remained exactly
`32cc9d8fd7a29bf330732e6247aedcd070f42b9fba7581bb5765e827171fd4e4` /
`f1479038dab3cc1004854a00b778f9869a946b17c8f80af139f6b51559092ce1`.

Current continuation: rerun the required verification after this owner-decision
record, then start Claude, Google, and a fresh default Codex child under one new
r4 ID over the same new current packet. R3 remains superseded because its two
reproduced bounded defects changed the reviewed bytes, not because of result
format. Package, commit, push, install, tag, publish, merge, and release remain
blocked. Preserve the Task 4 packet-generation root cause as executor omission
with proven write capability, not a permissions defect.

## Historical 2026-08-10 owner-corrected Task 4 restart gate (superseded)

Do not reuse `/root/triad_skill_green`, `/root/triad_skill_green_r2`,
`/root/triad_skill_green_r3`, or `/root/triad_skill_green_r4`, or any of their
review IDs. They are historical failure observations, not GREEN evidence.

The current Custom Agent TOML contains only its stable model/effort, one minimal
no-edit behavior-executor instruction, and the exact source `SKILL.md`
enablement entry. It contains no per-run receipt schema, lifecycle command,
shell transport, cleanup criterion, or workflow correction. The leader-owned
exact Task 1/Task 4 scenario in the executable plan carries the complete
per-run test and receipt contract. Workflow behavior belongs only to the source
skill or its scripts.

Attempts 3 and 4 both failed before Python on malformed JSON shell quoting and
then retried under the same ID. The existing managed-lifecycle selector first
failed on the missing contract and then passed after the source `SKILL.md`
required JSON-valued lifecycle options to be transported as one shell argument
and required any failed lifecycle process, including pre-Python shell failure,
to stop without a corrected same-ID retry. No `review_round.py`, provider
wrapper, reference contract, tool availability, permission, MCP, installed
cache, user-global setting, or other workspace changed for this correction.
Fresh read-only prompt review found no failure in the corrected source skill or
the final exact spawn message; the message now fixes the hostile JSON fixture,
decoded round-trip observation, and recursive receipt types without duplicating
lifecycle command construction.
Final pre-reload checks passed the 16-case distribution-contract module, the
existing special-JSON round-trip selector, skill validation, minimal-profile
TOML validation, and both repository diff checks. Task 4 behavior GREEN itself
remains unstarted under the corrected profile.

These repository fingerprints were taken immediately before this handoff edit.
The edit necessarily changes the plugin diff fingerprint, so the next session
records a new plugin baseline instead of comparing it for equality.

| Repository | Branch | HEAD | Status fingerprint | Diff fingerprint |
|---|---|---|---|---|
| workspace root | `codex/workspace-argus-agents` | `7554c18031ee51f6275ad4625a302971c1803c14` | `57614738d5858764aa49fb2ecfc61c56c8773416b3e56d81db55e4c6a6235753` | `011b7afc437e687b4e1d662cb716def1f2b817200e717248086c7fdcbe8a6aee` |
| plugin worktree | `release/0.2.532` | `8b2f66edae8af6fc9bd32cdf35cf4cbb3006879c` | `32cc9d8fd7a29bf330732e6247aedcd070f42b9fba7581bb5765e827171fd4e4` | `40099e6d8323373ee804f64c40ad7e34cb59d9832032731480c411d74c605fe7` |

Exact reload bindings:

| File | SHA-256 |
|---|---|
| `/Users/chaniri/codex_workspace/.codex/agents/triad-skill-executor.toml` | `819148f8f6c59bba5b24f9fd4d0acb01d116b78f2f68afb3ebde675a45bdcef3` |
| `/Users/chaniri/codex_workspace/AGENTS.md` | `75aaa503c8588a39295e5646e69768f35d732355c75ad1bf14f13105dba57418` |
| `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/SKILL.md` | `4aed9e7d831e9895f524a3fe84e2e1648c5dd2dcc76e014858f1cd6ac4b20811` |
| `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/review-prompt-contract.md` | `3489d805d95af6736b4a44c750175df727a9108e243f3abddeea52399e613a31` |
| `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/leg-contracts.md` | `3c6a76ecc3061e9699f5d8b36e06436d65e46f58fe92ecd1db87b09b82b1ea15` |

### Historical copy/paste prompt for the next Task 4 trial (do not use)

```text
Continue the TRIAD work in /Users/chaniri/codex_workspace. First apply $superpowers:using-superpowers, $superpowers:executing-plans, $superpowers:test-driven-development, and $superpowers:writing-skills. Read the root AGENTS.md, then read these files completely:

- /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-08-05-next-session-handoff.md
- /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-08-09-triad-skill-sot-behavior-test.md
- /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/superpowers/plans/2026-08-09-triad-skill-sot-behavior-test.md

Preserve both dirty trees. Tasks 1 through 3 are complete. The first four Task 4 executor attempts are failed-closed historical observations; do not reuse their threads, review IDs, packets, or results. Keep the separate lifecycle plan paused after Task 9.

Record fresh root/plugin branch, HEAD, status fingerprint, and diff fingerprint. Confirm that the live catalog exposes triad-skill-executor, that its loaded TOML equals the minimal profile hash recorded in the current handoff, and that it contains only the stable model/effort, minimal no-edit executor role, and exact source SKILL.md enablement. Verify the source and reference hashes and the canonical .agents/skills discovery symlink. Diagnose a mismatch without a default-agent or installed-cache fallback.

Then spawn exactly one new agent_type="triad-skill-executor" instance with fork_turns="none". Copy the complete exact Task 1 behavior scenario code block from the current executable plan into spawn_agent.message unchanged. Do not add lifecycle or receipt rules to the TOML. The child is only the clean-context observation surface; it must not edit or repair the skill.

If the scenario exposes a workflow defect, preserve and clean its exact evidence, reproduce it as leader, and correct only the implicated source SKILL.md or skill script plus its existing regression surface. Do not patch the executor profile to make the trial pass. Start the next trial with a new child and review ID; no parent restart is needed while the TOML/catalog remains unchanged. Stop for owner approval before any new mechanism or design expansion.

If the scenario is GREEN, complete the plan's leader lifecycle reproduction and exact Task 4 verification before a fresh three-family pre-merge round. Do not start lifecycle Task 10, package, push, install, tag, publish, merge, or release before those gates.
```

## Historical 2026-08-10 profile-level Task 4 correction (superseded)

Do not reuse `/root/triad_skill_green`, `/root/triad_skill_green_r2`,
`/root/triad_skill_green_r3`, or `/root/triad_skill_green_r4`. All four returned
`WORKFLOW_DEFECT`, cleaned their exact fixture and managed-root scope, and left
the canonical root and plugin worktrees unchanged.

Attempt 1 selected the installed-cache skill rather than the configured source.
The reproduced cause is that `skills.config` is an enablement override, while
repository-local skill discovery occurs under `.agents/skills`. The smallest
workspace catalog fix added one source pointer and no duplicate skill bytes:

```text
/Users/chaniri/codex_workspace/.agents/skills/triad-cross-family-review
  -> /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review
```

Attempt 2 proved source discovery but then followed the skill's bare
`bin/review_round.py` spelling and received exit `126` because the tracked file
mode is `100644`. The existing managed-lifecycle selector supplied the RED; the
minimum source GREEN now requires `python3 bin/review_round.py` for prepare,
manifest, capture, render, verify, and cleanup. The same selector passed `1`
and the exact distribution-contract module passed `16`. The skill validator,
executor TOML parse, and both `git diff --check` commands passed.

Attempt 3 selected the canonical source skill and reached `capture`. The source
skill named the packaged command but omitted its required `--worktree` and
`--output` arguments, so argparse exited `2`. Leader reproduction observed the
same controlled error. The existing managed-lifecycle selector supplied the
RED; the minimum GREEN now spells capture as `python3 bin/review_round.py
capture --prepared-dir <shared> --worktree <canonical-worktree> --output
<returned-root>/results/snapshot.json`. The selector passed `1`, the complete
distribution-contract module passed `16`, the skill validator passed, and
`git diff --check` passed. Attempt 3's earlier malformed shell quoting and
same-ID prepare retry also make that trial invalid; the next executor must have
no failed invocation or retry.

Attempt 4 read the canonical source skill but did not derive its packaged
toolkit root from that source. Ignore-aware root searches missed the nested
repository, after which the executor searched outside the workspace and
selected `/Users/chaniri/triad-codex-dispatch`. That unrelated file had only
the stale `capture`, `verify`, and `render` commands, so corrected `prepare`
exited `2`; no managed root was created. The existing managed-lifecycle
selector supplied the RED for a canonical toolkit-root binding. The minimum
source GREEN now resolves the toolkit from the canonical source `SKILL.md`
realpath and forbids another checkout or installed-cache substitution. The
selector passed `1`, the distribution-contract module passed `16`, the skill
validator passed, and `git diff --check` passed.

Attempts 3 and 4 both also failed before Python on malformed JSON shell quoting
and then issued a prohibited corrected retry under the same ID. The minimum
workspace-profile correction transports JSON-valued CLI arguments through a
task-specific variable as one double-quoted argv value and stops after any
nonzero lifecycle attempt without retry or review-ID reuse. Login-shell TOML
validation returned `EXECUTOR_PROFILE_OK`. No lifecycle command, packet rule,
receipt field, provider behavior, tool availability, or user-global setting
changed.

The executor profile additionally requires canonical realpath receipt paths so
the discovery symlink cannot appear in place of the canonical source path. No
plugin cache, user-global configuration, provider setting, permission setting,
MCP setting, or tool availability changed. Because the registered profile was
edited in this session, open a new Codex root session before another executor
spawn.

These fingerprints were taken immediately before this handoff documentation
edit. The edit changes the plugin fingerprint, so the next session records a
new baseline instead of requiring plugin-fingerprint equality.

| Repository | Branch | HEAD | Status fingerprint | Diff fingerprint |
|---|---|---|---|---|
| workspace root | `codex/workspace-argus-agents` | `7554c18031ee51f6275ad4625a302971c1803c14` | `57614738d5858764aa49fb2ecfc61c56c8773416b3e56d81db55e4c6a6235753` | `011b7afc437e687b4e1d662cb716def1f2b817200e717248086c7fdcbe8a6aee` |
| plugin worktree | `release/0.2.532` | `8b2f66edae8af6fc9bd32cdf35cf4cbb3006879c` | `32cc9d8fd7a29bf330732e6247aedcd070f42b9fba7581bb5765e827171fd4e4` | `87a5e9e6c68ae78f2b2c3fe883764417a33e8e28ddc96a517102b007faa78a39` |

Exact reload bindings:

| File | SHA-256 |
|---|---|
| `/Users/chaniri/codex_workspace/.codex/agents/triad-skill-executor.toml` | `d69dc06eae8006bbb02c732e9338d9ed0ad6e0d3f97404af1eeb885c51fc183f` |
| `/Users/chaniri/codex_workspace/AGENTS.md` | `75aaa503c8588a39295e5646e69768f35d732355c75ad1bf14f13105dba57418` |
| `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/SKILL.md` | `60ca9c058324cc1d12efc84dfbc2af1e77172e827e9b95ae86117d0bd0bb4a64` |
| `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/review-prompt-contract.md` | `3489d805d95af6736b4a44c750175df727a9108e243f3abddeea52399e613a31` |
| `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/leg-contracts.md` | `3c6a76ecc3061e9699f5d8b36e06436d65e46f58fe92ecd1db87b09b82b1ea15` |

In the new session, reapply the required skills and reread this handoff, the
current status, and the complete skill-SOT plan. Record fresh root/plugin
fingerprints; confirm the live catalog exposes `triad-skill-executor`; verify
the symlink target, profile hash, and four instruction-source hashes; then
spawn one new executor with `fork_turns="none"` and the exact unchanged Task 1
scenario. Require the exact four canonical instruction-source receipt entries
from Task 4. If the scenario is GREEN, continue with leader reproduction and
the full Task 4 verification. Do not start lifecycle Task 10, pre-merge,
package, push, install, tag, publish, merge, or release before that GREEN.

### Historical copy/paste prompt (do not use)

```text
Continue the TRIAD work in /Users/chaniri/codex_workspace. First apply $superpowers:using-superpowers, $superpowers:executing-plans, $superpowers:test-driven-development, and $superpowers:writing-skills. Read the root AGENTS.md, then read these files completely:

- /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-08-05-next-session-handoff.md
- /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-08-09-triad-skill-sot-behavior-test.md
- /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/superpowers/plans/2026-08-09-triad-skill-sot-behavior-test.md

Preserve both dirty trees. Tasks 1 through 3 are complete. The first four Task 4 executor attempts are failed-closed historical evidence; their exact roots are already absent, so do not reuse their threads, review IDs, packets, or results. The separate lifecycle plan remains paused after Task 9; do not start its Task 10.

Continue only from a fresh Task 4 baseline. Record root and plugin branch, HEAD, git status, status fingerprint, and diff fingerprint. Confirm that /Users/chaniri/codex_workspace/.agents/skills/triad-cross-family-review is a symlink resolving exactly to the canonical plugin-worktree source skill directory. Confirm the live catalog exposes triad-skill-executor and verify the active top-section executor-profile, root AGENTS.md, source SKILL.md, review-prompt-contract.md, and leg-contracts.md hashes in the handoff. Diagnose a mismatch instead of using a default-agent fallback or installed-cache skill.

Then spawn one new agent_type="triad-skill-executor" instance with fork_turns="none" and the exact unchanged Task 1 scenario from the plan. The executor must use only the configured source triad-cross-family-review skill, derive the packaged toolkit only from that canonical source realpath, report canonical realpath instruction sources, transport JSON CLI values as one argv without shell glob exposure, stop rather than retry after any failed lifecycle process, execute every packaged lifecycle subcommand as its own /bin/zsh -lic process with literal python3, avoid all provider wrappers, and clean only its exact managed root and fixture leaf. Require the exact four canonical instruction-source entries and every Task 4 SUCCESS field. Preserve pre/post fingerprints and independently confirm residue absence.

If the unchanged scenario exposes another workflow defect, preserve and clean its evidence and diagnose the reproduced workspace-owned cause without bypass or salvage. Stop for owner approval before any new mechanism or design expansion. If it is GREEN, complete the plan's leader lifecycle reproduction and exact Task 4 verification before a fresh pre-merge review. Do not package, push, install, tag, publish, merge, or release before those gates.
```

## 2026-08-10 Task 3 GREEN restart gate

The exact Task 1 executor scenario produced the intended `WORKFLOW_DEFECT` RED.
Formal-plan R20 then admitted schema-valid `SAFE` from Claude, Google, and fresh
Codex for digest
`c0dbfc5ca7fbb138956691b99feffa45ec33acc0fbddca64d53c85b80fd0be62`
and passed `ROUND_INTEGRITY_OK`. Task 3 made only the admitted minimal changes:
current task/plan execution authority, the bounded zero-provider lifecycle
characterization, the exact source-skill profile pin and receipt rules, and the
fourteen distribution hash targets. No reference, provider wrapper,
`review_round.py`, tool availability, permission, MCP, or user-global setting
changed.

Task 3 verification from `/Users/chaniri/codex_workspace` resolved Python
3.12.13 and pytest 9.0.3. The three exact selectors passed `3`, the exact
distribution modules passed `16` and `8`, `tests/test_review_round.py` passed
`78`, and the established focused command passed `132`. The skill validator
returned `Skill is valid!`; both repositories passed `git diff --check`; the
executor TOML parsed and contained the exact source `SKILL.md` path. The
skill-prompt fresh-eye suggestions were adjudicated as unchanged, out-of-slice
quality work and produced no further edit.

These repository fingerprints are the snapshots immediately before this
handoff documentation edit, as required by the executable plan. This edit
necessarily changes the plugin diff fingerprint, so the next session records a
new post-handoff baseline instead of comparing the plugin snapshot for
equality.

| Repository | Branch | HEAD | Status fingerprint | Diff fingerprint |
|---|---|---|---|---|
| workspace root | `codex/workspace-argus-agents` | `7554c18031ee51f6275ad4625a302971c1803c14` | `c3e78eb18ee88ceda26625832a5dad36012d19265767b81d64b7789a8e0f2067` | `011b7afc437e687b4e1d662cb716def1f2b817200e717248086c7fdcbe8a6aee` |
| plugin worktree | `release/0.2.532` | `8b2f66edae8af6fc9bd32cdf35cf4cbb3006879c` | `e4a6c7729813cebb07db542a60bd351fc2df098cf89bee800d760f72e42e7ad6` | `7f448cd52c833f1eb880087d688bb593c50fe320076dc999ec4fab8b0153b760` |

Exact reload bindings:

| File | SHA-256 |
|---|---|
| `/Users/chaniri/codex_workspace/.codex/agents/triad-skill-executor.toml` | `b6b9546031a9491285f101333efc31b9d720c498d8763d2d229ac0cb61ba71a1` |
| `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/SKILL.md` | `78ca3fa302d3944a3ed12fce21efd4f141823de2b4750e473327fcabcc44f3b5` |
| `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/review-prompt-contract.md` | `3489d805d95af6736b4a44c750175df727a9108e243f3abddeea52399e613a31` |
| `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/leg-contracts.md` | `3c6a76ecc3061e9699f5d8b36e06436d65e46f58fe92ecd1db87b09b82b1ea15` |

The profile's `skills.config.path` is exactly:

```text
/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/SKILL.md
```

End the session that edited that profile. Open a new Codex root session at
`/Users/chaniri/codex_workspace`, apply `superpowers:using-superpowers`,
`superpowers:executing-plans`, `superpowers:test-driven-development`, and
`superpowers:writing-skills`, then reread root `AGENTS.md`, the skill-SOT plan,
this handoff, and the current status. Record new root/plugin status and diff
fingerprints. Require the live catalog to expose `triad-skill-executor`, require
the exact profile hash and source path above, and recheck the three source/
reference hashes before spawning. Diagnose catalog loading instead of using a
default-agent fallback.

Only then spawn a new `agent_type="triad-skill-executor"` instance with
`fork_turns="none"` and the exact unchanged Task 1 scenario from the plan. Do
not reuse the RED thread. Task 4, full verification, fresh pre-merge review,
package, push, install, and fresh installed-skill proof have not started. Do not
start lifecycle Task 10, tag, publish, merge, or release.

All formal-round roots and fixtures created through Task 2, the Task 1 fixture,
and the exact official-doc evidence fixture
`/Users/chaniri/codex_workspace/_runs/openai-docs-skill-sot-r1` are absent.

## Copy/paste prompt for the next root session

Paste the following prompt into a newly opened Codex root session at
`/Users/chaniri/codex_workspace`. It intentionally binds to the hashes and
paths recorded above instead of duplicating them.

```text
Continue the TRIAD work in /Users/chaniri/codex_workspace. First apply $superpowers:using-superpowers, $superpowers:executing-plans, $superpowers:test-driven-development, and $superpowers:writing-skills. Read the root AGENTS.md, then read these files completely:

- /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-08-05-next-session-handoff.md
- /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-08-09-triad-skill-sot-behavior-test.md
- /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/superpowers/plans/2026-08-09-triad-skill-sot-behavior-test.md

Preserve both dirty trees. Before changing anything, record the root and plugin branch, HEAD, git status, status fingerprint, and diff fingerprint. Tasks 1 through 3 of the skill-SOT plan are complete. Do not rerun them. The separate lifecycle plan remains paused after Task 9; do not start its Task 10.

Continue only from skill-SOT Task 4. Confirm that the fresh live agent catalog exposes triad-skill-executor. Verify that the loaded profile has the exact absolute source SKILL.md pin and the executor-profile SHA-256 recorded in the handoff, then verify the current source SKILL.md, review-prompt-contract.md, and leg-contracts.md hashes against the handoff. If catalog loading, the profile pin, or a hash differs, diagnose that mismatch and repair only the smallest workspace-owned cause. Do not use a default-agent fallback, change user-global configuration, or restrict CLI, MCP, read, search, or web capabilities.

After the reload proof, spawn one new agent_type="triad-skill-executor" instance with fork_turns="none" and give it the exact unchanged Task 1 scenario from the plan. Do not reuse the RED thread or rewrite the scenario. The executor must use only the configured triad-cross-family-review skill and must not edit its SOT or invoke another skill. Require a new unique review ID, exact-root lifecycle and fixture cleanup, pre/post fingerprints, and a durable Task 4 status record. Touch only the exact unique roots created for this run; preserve siblings and other processes' files.

If the unchanged scenario exposes a workflow defect, preserve and clean its evidence, repair the implicated workspace skill, profile, or tool with the existing regression surface, and restart the entire Task 4 procedure under a new ID. Do not bypass, manually rebuild, salvage, or broaden the design. Stop and report concrete delta, evidence, impact, and the owner decision needed only if completion requires a design expansion.

After Task 4 GREEN, run the plan's complete verification and a fresh-ID Claude, Google, and fresh-Codex pre-merge review over the same current bytes. Treat findings as advisory and implement only reproduced defects inside the approved current specification. The goal is to improve the current workflow through three-family review, not to perform general skill-quality improvement. Reject unrelated polish, new abstractions, protocols, capability gates, or hypothetical hardening.

Only the bytes that pass that fresh pre-merge gate may be packaged and pushed. Before installing outside /Users/chaniri/codex_workspace, state the exact install target, exact delta, and impact and obtain target-specific owner approval in the current conversation. Then install those same bytes and perform a fresh ephemeral installed-skill proof. Do not tag, publish, merge, or release. Record verification, review custody, package hashes, push/install evidence, fresh exposure, fingerprints, and exact cleanup in the current status and handoff.
```

## Historical 2026-08-09 initial skill-executor restart gate

The section below records the earlier pre-RED catalog checkpoint and is
superseded by the 2026-08-10 gate above. It preserves the historical
post-r8 bounded-correction handoff label required by the current documentation
contract and the prior `current lifecycle/JSON-IPC bounded-correction candidate`
label without making either the active restart state.

Pause the existing lifecycle plan between completed Task 9 and pending Task 10.
Formal-plan R30 returned admitted `SAFE` from all three families for digest
`58b02cf6eaedafebc37c90c7f19995504e1af53e6dfdb81ef27a759bedc45051`,
passed final integrity verification, and was cleaned exactly. The current
candidate's recorded 501-test verification predates this restart and must not be
presented as a newly rerun result.

The owner approved a project-scoped fresh behavior executor for
`triad-cross-family-review` and a minimal SOT correction before the pending
pre-merge gate. Continue from
`docs/superpowers/plans/2026-08-09-triad-skill-sot-behavior-test.md`. The root
catalog change requires a new Codex session opened at
`/Users/chaniri/codex_workspace`. Do not start lifecycle-plan Task 10, package,
push, or install before the new plan's fresh-agent RED/GREEN and amended formal
plan gate finish.

The current session created
`/Users/chaniri/codex_workspace/.codex/agents/triad-skill-executor.toml` and
registered it in `/Users/chaniri/codex_workspace/.codex/config.toml`. The agent
pins `gpt-5.6-terra` at `high`, enables the source
`triad-cross-family-review` skill folder through `skills.config`, inherits the
session's tool and permission configuration, and duplicates no TRIAD workflow
rules. Login-shell Python 3.12.13 parsed both TOML files and verified the skill
folder plus `SKILL.md`; no executor was spawned from the pre-change session.

## Start here

Work from:

```text
/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
```

The implementation branch is `release/0.2.532`; the plugin manifest version is
`0.2.533`. The current candidate includes the owner-approved 0.2.533 tasks and
the bounded r2 through current corrections recorded below.
Resolve the exact candidate with `git rev-parse HEAD`; do not infer it from an
earlier review digest or distribution archive.

Before changing anything, verify:

```text
git status -sb
git rev-parse HEAD
codex plugin list --json
```

The source worktree was clean when this handoff was written. Preserve unrelated
workspace and child-repository state.

## Completed work

- Replaced batching, receipts, packet review, PTY, sentinel, and provider code
  writing with one focused directory and one reviewer-only Claude, Google, and
  fresh Codex leg per round.
- Added strict `LegVerdict`, prepared-directory digest, canonical-worktree
  fingerprint, convergence rules, oscillation/conflict stops, and the owner
  design-decision gate.
- Moved AGY to 1.1.10 native `stream-json` plus `json-schema`, explicit
  `gemini-3.1-pro-high`, and `high` effort.
- Moved Claude structured review to one native `--json-schema` call with no
  schema-repair provider call.
- Added pressure tests and a real two-round benchmark. Steady-state results:
  3 calls per round instead of 24 planned, 87.5% call reduction, 4/4
  adjudicated finding recall, zero clean-control false findings, and 3/3
  confirmation `SAFE`.
- Limited the formal Gemini fallback to one provider call, rejected zero-case
  and zero-planted-finding benchmarks, and added clean-HEAD exact-archive
  verification.
- Explicitly superseded the conflicting 0.2.532 AGY design and implementation
  plan, and regression-bound their current-authority banners.
- Source tests for the current JSON-amended lifecycle candidate: `502 passed` under Python
  3.12.13 and pytest 9.0.3. Do not reuse earlier 406-, 422-, 424-, 425-, 426-, 431-, 447-, 453-,
  454-, 456-, 457-, or 498-test snapshots.

Important 0.2.533 commits before the bounded r3 correction, newest last:

```text
33dd517 docs: record convergent runtime benchmark
1d53775 fix: bind review routes to captured evidence
e928212 docs: plan 0.2.533 owner-approved completion
0ae7b2d fix: limit formal Gemini fallback to one call
dc59558 fix: reject empty benchmark evidence
62e3df7 feat: verify exact distribution archive bytes
21bb477 docs: supersede stale formal route records
```

## Historical r8 review state and current gate

Review round `final-0.2.533-r8` used prepared digest:

```text
e2e5f1c7e04c9dc6e3b8bfb0382ac4c29e6ee974d9e7417e318c757d43f934b3
```

- Google: valid `SAFE`, no findings.
- Claude: valid `SAFE`, two Minor timeout-contract findings; completed in
  655.7 seconds under the explicit 1,800-second deadline.
- Fresh Codex: valid `SAFE`, one Minor stale release-path finding.
- Prepared directory and canonical worktree: `ROUND_INTEGRITY_OK`.

The Claude Minors reproduced: `triad-claude-dispatch` summarized the formal
route without `--timeout 1800`, and the distribution contract did not bind the
deadline or wake-up-boundary text. The historical r9 candidate corrected both while
leaving ordinary Claude dispatch defaults unchanged.

The Codex Minor also reproduced: Task 5 still used release-specific `final-r2`
review and distribution paths. The historical r9 plan uses `FINAL_REVIEW_ID` and
requires a fresh unused evidence directory for the admitted round.

Run a fresh complete round over a new digest, including the active
`docs/references/repair-protocol.md` boundary and the current owner-authorized
affected-source closure. Do not revive the stale 80-file count or reuse r5
through r8 verdicts for final admission.

## Approved owner decisions

The owner approved all three recommended defaults in the resumed 2026-08-05
session:

1. The separately authorized Gemini formal fallback follows the one-provider-call
   rule.
2. A lightweight workspace-owned verifier stages exact archive bytes and runs
   package tests; authenticated fresh-process skill exposure remains a release
   procedure rather than a normal unit test.
3. A benchmark with zero cases or zero planted findings fails closed.

## Distribution and installation state

When this handoff was written, the live installed inventory reported enabled
version `0.2.532` sourced from this repository. On resumption,
`codex plugin list --json` reported `0.2.533` from the same local source path
because its manifest is already versioned `0.2.533`. That inventory is not
installed/cache byte identity, bootstrap proof, or fresh-process skill exposure;
those acceptance steps have not happened yet.

The latest verified pre-r9 archive was staged at:

```text
_runs/distribution/0.2.533-final-r4/triad-codex-dispatch-0.2.533.tar
```

Its SHA-256 was
`b3648c538a5b61f7655a4838550f7887b4dfc2a6e81f1f78be0c6521ccbdd8c7`
and its unpacked bytes passed `422` tests. It predates the r4 corrections and is
stale; do not install it or use it as final evidence.

After a unanimous fresh review round:

1. Run `scripts/verify_distribution.py` from the login-shell Python environment
   with the new clean HEAD and a new output directory inside `_runs/`.
2. Compare manifest and core-skill SHA-256 values between source and archive.
3. Run the full suite from the unpacked archive bytes.
4. Obtain explicit permission before mutating `~/.codex`, `~/.local/bin`, or
   other non-workspace installation state.
5. Update the local plugin cache to 0.2.533 and run the installed
   `scripts/bootstrap.sh --install`; `--check` is unsupported.
6. Confirm installed/cache/source byte identity.
7. Run a fresh `codex exec --ephemeral` exact-marker probe proving the current
   convergent skill is exposed.
8. Tell the owner to open a new interactive Codex session. The current session
   cannot reload the updated skill catalog.

The owner authorized remote publication, the skill update, and this bounded
three-family review workflow on 2026-08-06. Execute publication and installation
only after unanimous r9 admission and exact packaged-byte verification. Do not
repeat an approval prompt while provider, objective, and data categories remain
inside that authorization.

## Argus continuation after TRIAD

Only after installed 0.2.533 fresh-process proof, return to:

```text
/Users/chaniri/codex_workspace/workspace/triad-codex-host-sot-refresh/
3rd-Agent/export_assets/codex-host/docs/superpowers/plans/
2026-08-01-argus-triad-review-infrastructure-resume.md
```

That checkpoint says its Task 10 has not started, but it is stale: it assumes
AGY 1.1.9, the older evidence architecture, and installed plugin 0.2.531. Do
not execute the old Task 10 text mechanically. Read the root and project
`AGENTS.md`, the checkpoint's required design/request files, and reconcile Task
10 with the owner-approved AGY 1.1.10 focused-convergent reviewer-only policy
before editing its leader change request. Preserve the separate
`triad-codex-host-sot-refresh` and dirty `Argus-codex` repositories.

## First next-session outcome

Complete Task 4 with a new reloaded `triad-skill-executor` and the unchanged
scenario. Then run the plan's full verification and fresh three-family
pre-merge gate before any same-bytes package, push, install, or installed-skill
proof. Keep lifecycle Task 10 paused and do not tag, publish, merge, or release.
