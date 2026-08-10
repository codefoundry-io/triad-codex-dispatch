# TRIAD Skill SOT Behavioral Test Status

Date: 2026-08-09

Plan: `docs/superpowers/plans/2026-08-09-triad-skill-sot-behavior-test.md`

## Current Task 4 result: GREEN, leader reproduction, and verification complete

Task 4 is GREEN. The fresh executor, independent leader lifecycle
reproduction, and the complete recorded verification set all completed on the
current candidate. This is behavior-characterization evidence only; it is not
formal pre-merge admission, packaging, push, installation, tagging,
publication, merge, or release evidence. Pre-merge r3 completed but failed
closed, and two bounded existing-design corrections are implemented. The owner
rejected a separate required-criteria validator/CLI binding as format-centered
overdesign; no validator change is pending before a fresh r4 over new bytes.

The pre-documentation basis was workspace root branch
`codex/workspace-argus-agents`, HEAD
`7554c18031ee51f6275ad4625a302971c1803c14`, status fingerprint
`57614738d5858764aa49fb2ecfc61c56c8773416b3e56d81db55e4c6a6235753`, and
diff fingerprint
`011b7afc437e687b4e1d662cb716def1f2b817200e717248086c7fdcbe8a6aee`.
The plugin worktree was branch `release/0.2.532`, HEAD
`8b2f66edae8af6fc9bd32cdf35cf4cbb3006879c`, status fingerprint
`32cc9d8fd7a29bf330732e6247aedcd070f42b9fba7581bb5765e827171fd4e4`, and
diff fingerprint
`2f5f903f54ca64b3187db2bad6539700662adea68104d7ceafe9a4d3b903d1b0`.
Those plugin fingerprints are snapshots before this documentation update; the
update itself changes the plugin diff, so later work records a new baseline.

The reloaded live catalog exposed `triad-skill-executor`. Its profile requested
`gpt-5.6-terra` at `high` with `fork_turns="none"`; runtime metadata did not
expose independent actual model or effort values. The profile SHA-256 was
`819148f8f6c59bba5b24f9fd4d0acb01d116b78f2f68afb3ebde675a45bdcef3`.
The four canonical instruction sources remained byte-identical before and
after the behavior run:

| File | SHA-256 |
|---|---|
| `/Users/chaniri/codex_workspace/AGENTS.md` | `75aaa503c8588a39295e5646e69768f35d732355c75ad1bf14f13105dba57418` |
| source `SKILL.md` | `4aed9e7d831e9895f524a3fe84e2e1648c5dd2dcc76e014858f1cd6ac4b20811` |
| `review-prompt-contract.md` | `3489d805d95af6736b4a44c750175df727a9108e243f3abddeea52399e613a31` |
| `leg-contracts.md` | `3c6a76ecc3061e9699f5d8b36e06436d65e46f58fe92ecd1db87b09b82b1ea15` |

### Attempt 5 diagnosis and cleanup

Fresh executor `/root/triad_skill_green_r5`, review ID
`4342324e-88b3-4677-96b9-c7380851e8e4`, returned `WORKFLOW_DEFECT` after
`prepare` exit `0` and `manifest` exit `2` with
`review_round: missing lifecycle packet member: REVIEW.diff`. It created the
exact fixture and `prepare` created the managed root and copied the packet
source, so write capability was present and not causal. The executor had
skipped the source skill's explicit Flow step 3 packet-member write before
`manifest`. Existing source, tool, and tests already required current `TASK.md`
and `REVIEW.diff`; no source, profile, tool, or test edit was warranted.
Supported cleanup returned `removed: true`, and independent checks confirmed
the exact managed root and fixture absent with unchanged root/plugin
fingerprints. Leader reproduction under review ID
`c125a800-0d08-4b72-b213-3a91d7db249e` reproduced the same prepare `0`,
manifest `2`, message, cleanup, exact fixture removal, and unchanged
fingerprints.

### Attempt 6 GREEN and independent lifecycle reproduction

Fresh executor `/root/triad_skill_green_r6`, review ID
`triad-skill-green-r6-20260810-6c1630fd`, returned valid `SUCCESS` with an
empty failures array, the exact four canonical instruction sources, payload
JSON round-trip true, non-null managed paths, and one rendered prompt.
`prepare`, `manifest`, `capture`, payload comparison, `render`, `verify`, and
`cleanup` each self-reported exit `0`; no provider wrapper command ran. The
capture digest was
`b4329708c044a1ea384868781039c224c946cb41864e1da762e16c4937a66b9b`.
Cleanup reported `removed: true`, with absent managed root and fixture leaf and
empty residue and swept-root lists. Independent checks again found no managed
root or fixture and unchanged root/plugin fingerprints and instruction-source
hashes.

Leader reproduction used distinct review ID
`3862d6a7-f262-40e5-bab4-2e135a9f8781` and the exact separate fixture under
`_runs/skill-executor-leader/<id>`. It added current `TASK.md` and
`REVIEW.diff`, then observed `prepare` exit `0`, `manifest` exit `0` with
`file_count: 4`, `capture` exit `0` with digest
`5c979be061071da3a2a041a45afb25505bc1e0eaebbcc9cf32cf9febb83f07c7`, decoded
payload comparison `PAYLOAD_JSON_EQUAL`, `render` exit `0`, and `verify` exit
`0` with stdout `ROUND_INTEGRITY_OK`. Supported cleanup returned
`removed: true`; the exact managed root and fixture leaf are absent, no managed
sibling exists, and canonical fingerprints remained unchanged.

### Fresh verification and remaining boundary

From the login shell, `python3` resolved to
`/opt/homebrew/opt/python@3.12/libexec/bin/python3`, Python `3.12.13`, and
pytest `9.0.3`. `py_compile` of `bin/review_round.py` passed; the recorded
results were `78 passed in 6.26s` for `tests/test_review_round.py`, `16 passed
in 0.01s` for `tests/test_distribution_contract.py`, `8 passed in 0.96s` for
`tests/test_distribution_verifier.py`, `132 passed in 7.34s` for the
established focused set, `1 passed in 0.43s` for the lifecycle smoke selector,
and `501 passed in 128.86s` for the full suite. The skill validator returned
`Skill is valid!`; `bash -n scripts/bootstrap.sh` exited `0`; root and plugin
`git diff --check` both exited `0`.

## Current pre-merge attempt: r1 superseded by bounded corrections

Combined pre-merge round `20260810-combined-premerge-r1-d7027cbf-8c02-4049-8781-80f67ba27f78`
used digest `a5329e8abb117a758950eb0f55e3f41f666d552ea986eb0c70888087a0fee5b3`.
Google and fresh Codex returned `SAFE` with no findings; Claude returned
`SAFE` with four Minor claims. Every leg ended with `ROUND_INTEGRITY_OK`.
Leader adjudication reproduced claim 1 as stale `permission-unavailable` /
`truncated-answer` documentation in README, README.ko, and SECURITY, and
claim 3 as missing strict Claude/Google ID, family, and digest validator
commands in `leg-contracts.md`. Claims 2 (route-mismatch mapping) and 4
(fenced Claude envelope) were rejected as unsupported-route hypotheses outside
the approved scope.

Claims 1 and 3 required edits, so r1 is superseded and its verdicts cannot be
reused. Exact lifecycle cleanup returned `removed: true` and the managed root
is absent. The ordinary development subagent's bounded TDD correction produced
the existing selectors RED with two failures and GREEN with `2 passed`; the
leader reran those two tests with `2 passed` and
`tests/test_distribution_contract.py` with `16 passed`. The Task 4 packet
root cause remains an executor omission: r5 had write capability but skipped
creating current `TASK.md` / `REVIEW.diff` before manifest, not a permission
defect.

Historical continuation at that point: the observed post-correction verification used login-shell Python
`3.12.13` and pytest `9.0.3`: `py_compile` exit `0`; review-round `78 passed
in 6.32s`; distribution-contract `16 passed in 0.01s`; distribution-verifier
`8 passed in 1.04s`; established focused set `132 passed in 7.33s`; lifecycle
smoke `1 passed in 0.43s`; and full suite `501 passed in 128.52s`. The skill
validator returned `Skill is valid!`; `bash -n scripts/bootstrap.sh` and plugin
`git diff --check` exited `0`. Post-document distribution-contract `16` then
passed before r2. R2 and r3 later ran as recorded below, and neither is a
current admission. Package, commit, install, and release gates remain blocked;
keep lifecycle Task 10 paused.

## Current pre-merge attempt: r2 superseded by bounded corrections

Combined pre-merge round `20260810-combined-premerge-r2-433c7ff0-a217-4660-9eb5-3cd01f5809d5`
used digest `8d851f9d70e76a682a567e9d66ff2ae0ca29654cb901a0e4a4334ae8f7d103b5`
over the fresh current 82-member, 33-dirty, 14-target closure; its manifest
contained 85 members. Google was `SAFE` with no findings in 157.4s, fresh Codex
was `SAFE` with no findings, and Claude was `SAFE` with two Minor findings in
681.6s. Every result passed strict ID/family/digest validation and final
verification printed `ROUND_INTEGRITY_OK`.

Both Minors reproduced inside the approved design: the shared renderer omitted
the second credential/auth/environment/provider-log/unrelated-path exclusion
sentence required by `review-prompt-contract`; and configured-root failed-result
audit storage failure was hidden when the failure run-log succeeded. r2 is
superseded, its verdicts cannot be reused, and exact cleanup returned
`removed: true` with the managed root absent. Two ordinary development
subagents, not the designated executor, performed independent TDD in
non-overlapping files: the renderer selector went RED then GREEN with module
`78`, and the audit selector went RED then GREEN with module `38`. The leader
reran the exact selectors (`1 + 1` passed) and modules `78` and `38` passed.

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

## Current pre-merge attempt: r3 failed closed; owner decision required

Round `20260810-combined-premerge-r3-965062bc-d585-4cef-8da0-80904dc806a8`
used digest `ef0df860cc5cd20a94e3348382a43ac95c3129f006725f2e53a3240523c19790`
over a fresh 82-member/33-dirty/14-target closure with manifest 85. Google and
fresh Codex returned admitted `NOT-SAFE`; Claude returned admitted `SAFE` with
three Minor findings. All three results bound the same review ID, family, and
digest, and every post-leg verification returned `ROUND_INTEGRITY_OK`. The
round is superseded and cannot be reused. Supported exact cleanup returned
`removed: true`; its managed root is absent and managed siblings were
unchanged.

The Google claim against the wrapper-internal
`--dangerously-skip-permissions` element was rejected as a reversal of the
approved child-only route. Claude's success-path diagnostic rename was rejected
because the owner-approved plan explicitly retains `run-log-unavailable` for
that case. Claude's other two Minors reproduced: destination I/O during
preparation was misclassified as a source-integrity failure, and Flow step 2
omitted the already-enforced canonical-path/regular-member-list input contract.

Ordinary development subagents, not the designated executor, corrected those
two bounded defects with RED/GREEN TDD. The preparation regression also exposed
a first-fix source-FD cleanup leak during root review; both source-race variants
were made RED and then fixed by restoring an outer cleanup. Leader reruns are
the combined focused `3 passed`, full review-round `79 passed`, Flow-2 focused
`1 passed`, and full distribution-contract `16 passed`.

Final leader verification after both corrections was `py_compile` exit `0`,
focused review-round/log-cleanup/distribution-contract `133 passed in 7.48s`,
distribution-verifier `8 passed in 1.10s`, lifecycle smoke `1 passed in 0.49s`,
and complete suite `502 passed in 128.69s`. The source skill validator returned
`Skill is valid!`; shell syntax, root/plugin diff checks, and final r3-root
absence checks passed.

Fresh Codex's Major is rejected under the owner's clarified semantic review
contract. Every current route already requests JSON and all three r1/r2/r3
families produced validator-readable JSON, so no formatting defect occurred.
Exact `criteria_checked` serialization is not a separate admission authority
when a reviewer inspected the correct immutable packet and delivered a
substantive review that the leader can understand and reproduce. No
`--expected-criterion`, exact-copy wording, Markdown parser, normalization,
schema field, or other admission mechanism will be added. JSON remains a
convenient requested transport; Markdown or fenced output alone is not a
substantive review failure.

Current continuation: rerun verification after this owner-decision record and
start a complete fresh-ID r4 over the corrected new bytes. R3 remains
superseded because two reproduced defects changed its reviewed bytes, not
because of result format. Packaging and every later release/integration action
remain blocked. The Task 4 packet-generation root cause remains executor
omission despite proven write capability, not a permission defect.

## Initial workspace basis

The root session was opened at `/Users/chaniri/codex_workspace`. The live
native agent schema exposed `triad-skill-executor`; no default-agent fallback
was used. The registered profile requested `gpt-5.6-terra` at `high` with
`fork_turns="none"`. Runtime metadata did not expose an independent actual
model or effort value.

Before the RED executor ran, the recorded Git basis was:

| Repository | Branch | HEAD | Status fingerprint | Diff fingerprint |
|---|---|---|---|---|
| workspace root | `codex/workspace-argus-agents` | `7554c18031ee51f6275ad4625a302971c1803c14` | `4c39e484a7380c1bb488e4e4208613536e5d379695176e71c8b4778362f9c2ee` | `011b7afc437e687b4e1d662cb716def1f2b817200e717248086c7fdcbe8a6aee` |
| plugin worktree | `release/0.2.532` | `8b2f66edae8af6fc9bd32cdf35cf4cbb3006879c` | `dad361d9b5e9122f3aaf48e78955d0bae6b728d5c985bca42bf3a5fd963a248a` | `f7c9b82bed5ca6562396ff154dacfe64ac0c049c071f0c2f45e2e8daccabea69` |

The plugin checkout was already a linked worktree whose Git directory was
`/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch/.git/worktrees/triad-codex-dispatch-reliability`;
no additional worktree was created. The complete pre-existing dirty status was
captured in the session transcript and preserved.

## Task 1 RED characterization

Executor identity: `/root/triad_skill_red` (registered agent type
`triad-skill-executor`; provider-enforced read-only containment was not exposed,
so the no-edit boundary was prompt-controlled and checked by fingerprints).

Exact scenario:

```text
Execute one RED characterization of the configured triad-cross-family-review skill as its leader. Do not review or edit the skill source. Do not invoke another skill. Do not dispatch external provider legs yet. First identify every non-system instruction source that the configured skill requires you to read before packet preparation. Then exercise the deterministic current-packet lifecycle through prepare, manifest, capture, render, verify, and exact cleanup using one new unique review ID, the exact disposable fixture /Users/chaniri/codex_workspace/_runs/skill-executor/<same-review-id>/, and the canonical plugin worktree. Create that unique leaf exclusively and never delete or overwrite its parent or a sibling. Include JSON strings containing a quote, backslash, newline, tab, and Unicode text. Do not manually rebuild or salvage any failed artifact. On a workflow defect, clean the exact managed review root when the supported cleanup command can do so, report WORKFLOW_DEFECT, and stop. Remove only the exact disposable fixture leaf you created after lifecycle cleanup. Return one valid JSON object with keys status, skill, instruction_sources, review_id, commands, artifacts, cleanup, worktree_changed, and failures. Encode every string as JSON; do not use delimiter-based IPC.
```

The executor returned this valid JSON object:

```json
{
  "status": "WORKFLOW_DEFECT",
  "skill": "triad-codex-dispatch:triad-cross-family-review",
  "instruction_sources": [
    {
      "path": "/Users/chaniri/.codex/plugins/cache/triad-codex-dispatch/triad-codex-dispatch/0.2.533/skills/triad-cross-family-review/SKILL.md",
      "dependency": "configured workflow"
    },
    {
      "path": "/Users/chaniri/codex_workspace/AGENTS.md",
      "dependency": "applicable workspace instructions"
    },
    {
      "path": "/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/review-prompt-contract.md",
      "dependency": "required by the skill before render"
    }
  ],
  "review_id": "skill-executor-442e57fa-eda4-4aa4-8184-647e23fab247",
  "commands": [
    {
      "command": "sed -n '1,240p' /Users/chaniri/.codex/plugins/cache/triad-codex-dispatch/0.2.533/skills/triad-cross-family-review/SKILL.md",
      "exit_state": 2
    },
    {
      "command": "rg --files /Users/chaniri/.codex/plugins/cache/triad-codex-dispatch | rg '/triad-cross-family-review/SKILL\\.md$'",
      "exit_state": 0
    },
    {
      "command": "sed -n '1,260p' /Users/chaniri/.codex/plugins/cache/triad-codex-dispatch/triad-codex-dispatch/0.2.533/skills/triad-cross-family-review/SKILL.md",
      "exit_state": 0
    },
    {
      "command": "python3 --version && command -v python3 && python3 -m pytest --version && python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py --help",
      "exit_state": 0
    },
    {
      "command": "/bin/zsh -lic 'sed -n \"1,260p\" workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/review-prompt-contract.md; python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py prepare --help; python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py manifest --help; python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py capture --help; python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py render --help; python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py verify --help; python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py cleanup --help'",
      "exit_state": 0
    },
    {
      "command": "/bin/zsh -lic 'review_id=\"skill-executor-$(uuidgen | tr \"[:upper:]\" \"[:lower:]\")\"; fixture=\"/Users/chaniri/codex_workspace/_runs/skill-executor/${review_id}\"; test ! -e \"$fixture\" && mkdir -p \"$fixture\" && printf \"%s\\n%s\\n\" \"$review_id\" \"$fixture\"'",
      "exit_state": 0
    },
    {
      "command": "apply_patch: created TASK.md, payload.json, and member-list.txt under the exact fixture leaf",
      "exit_state": 0
    },
    {
      "command": "/bin/zsh -lic 'command -v python3; python3 --version; python3 -m pytest --version; git -C /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability status --porcelain=v1; python3 workspace/triad-codex-dispatch-reliability/bin/review_round.py prepare --review-id skill-executor-442e57fa-eda4-4aa4-8184-647e23fab247 --source-root /Users/chaniri/codex_workspace/_runs/skill-executor/skill-executor-442e57fa-eda4-4aa4-8184-647e23fab247 --member-list /Users/chaniri/codex_workspace/_runs/skill-executor/skill-executor-442e57fa-eda4-4aa4-8184-647e23fab247/member-list.txt --required-members-json \"[\\\"TASK.md\\\",\\\"payload.json\\\"]\"'",
      "exit_state": 1
    },
    {
      "command": "rm -rf /Users/chaniri/codex_workspace/_runs/skill-executor/skill-executor-442e57fa-eda4-4aa4-8184-647e23fab247 && test ! -e /Users/chaniri/codex_workspace/_runs/skill-executor/skill-executor-442e57fa-eda4-4aa4-8184-647e23fab247",
      "exit_state": 0
    },
    {
      "command": "/bin/zsh -lic 'git -C /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability status --porcelain=v1; test ! -e /Users/chaniri/codex_workspace/_runs/skill-executor/skill-executor-442e57fa-eda4-4aa4-8184-647e23fab247'",
      "exit_state": 0
    }
  ],
  "artifacts": {
    "fixture_leaf": "/Users/chaniri/codex_workspace/_runs/skill-executor/skill-executor-442e57fa-eda4-4aa4-8184-647e23fab247",
    "fixture_contents_removed": [
      "TASK.md",
      "payload.json",
      "member-list.txt"
    ],
    "special_json_strings_in_removed_payload": [
      "a \"quote\"",
      "C:\\review\\packet",
      "first\nsecond",
      "left\tright",
      "한글 ✓"
    ],
    "managed_review_root": null,
    "prepared_directory": null,
    "manifest": null,
    "snapshot": null,
    "rendered_prompts": [],
    "provider_dispatches": []
  },
  "cleanup": {
    "managed_root_cleanup": "not invoked: prepare rejected input before reporting or creating an exact managed review root",
    "fixture_cleanup": "exact fixture leaf removed and absence verified",
    "residue": []
  },
  "worktree_changed": false,
  "failures": [
    {
      "stage": "prepare",
      "message": "review_round: member list must be valid JSON",
      "classification": "WORKFLOW_DEFECT",
      "effect": "manifest, capture, render, verify, and lifecycle cleanup could not be reached; no artifact was rebuilt, adapted, or salvaged"
    }
  ]
}
```

### Leader reproduction and containment

- The selected runtime skill bytes were the installed cache path above, SHA-256
  `69f12b4e07dc39600dcb9383e7023220dea83bcefebc4be87051965173f3c395`.
  They differed from the catalog profile's configured source skill at
  `skills/triad-cross-family-review/SKILL.md`, SHA-256
  `5301380170c0a07e903f430db4dca881e95aa1015e153a290f37fffacfbe7484`.
  This is observed behavior, not a conclusion that either path may be silently
  substituted.
- The runtime instruction-source list consequently omitted the source skill's
  required pre-prepare `../../CHANGELOG.md` dependency. It also omitted the
  configured source `SKILL.md` itself. This failed the scenario's instruction-
  source receipt requirement.
- The first Python/tool inspection command ran outside the workspace-required
  interactive login shell. The later lifecycle command used `/bin/zsh -lic`,
  but that does not erase the earlier contract violation.
- The raw executor JSON's `commands[].exit_state` value `1` for the failed
  `prepare` command is a self-reported observation, not a leader-observed
  process status. Leader reproduction with the same invalid newline member-list
  shape under review ID
  `exit-repro-ecd5931b-9aeb-44b6-a220-f5c82432501b` printed
  `review_round: member list must be valid JSON` and exited `2`, matching the
  packaged controlled-error contract. The exact reproduction fixture was
  removed and no managed review root was created. The amended executor contract
  therefore defines `exit_state` as the exact observed process status, and the
  Task 4 leader independently observes the verify status and stdout marker.
- `prepare` failed before a managed root was reported or created. Independent
  leader verification found the expected managed path
  `/var/folders/zl/9462906j0x55xpj9zhz_84yc0000gn/T/triad-review-skill-executor-442e57fa-eda4-4aa4-8184-647e23fab247`
  absent. The exact fixture leaf was absent after cleanup.
- Before writing this durable record, both root and plugin HEAD, status
  fingerprint, and diff fingerprint exactly matched the pre-executor values in
  the table. The trial therefore made no canonical-worktree change. Creating
  this status file is a subsequent leader-owned documentation change and is not
  part of the executor containment comparison.

Task 1 is RED and complete. No plugin SOT or runtime implementation was fixed
in this task.

## Task 2 pre-implementation formal-plan gate

Task 2 completed on 2026-08-10. Each dispatched round used a fresh review ID,
one leader-prepared directory, the same current packet for Claude, Google, and
fresh-context Codex, and no test-source exclusion. The final packet contained
82 product regular files and 85 manifest entries, including every one of the 31
current dirty paths. Failed or superseded rounds were never mixed into a later
round.

The round ledger is:

| Round | Fresh ID suffix | Claude | Google | Codex | Disposition |
|---|---|---|---|---|---|
| R1 | retained in the session transcript | `NOT-SAFE` | `SAFE` | `NOT-SAFE` | superseded |
| R2 | `92f22a22-6fe5-4f39-b57b-ea59dbdd0c34` | `NOT-SAFE` | `NOT-SAFE` | `NOT-SAFE` | superseded |
| R3 | `d8ce4b1f-6399-4b5b-9258-2aed96a42ba8` | `NOT-SAFE` | `SAFE` | `SAFE` | superseded |
| R4 | `b9fb1030-f9c8-4bde-8904-f46584a8da8f` | `NOT-SAFE` | `SAFE` | `NOT-SAFE` | superseded |
| R5 | `4927caf6-3096-4910-85db-fd5b1e3fc09b` | `NOT-SAFE` | `SAFE` | `NOT-SAFE` | superseded |
| R6 | `c3578573-e069-4941-aeab-9ae6c743d09f` | `NOT-SAFE` | `SAFE` | `SAFE` | superseded |
| R7 | `37ec41ef-9cf1-46de-800a-3008e3436815` | `NOT-SAFE` | `SAFE` | `SAFE` | superseded |
| R8 | `cf7bfa82-617c-4c6d-b2cf-607675ce9817` | `NOT-SAFE` | `SAFE` | `NOT-SAFE` | superseded |
| R9 | `50377dd1-518d-47eb-8704-cb85f993d2d1` | `SAFE` | `SAFE` | `NOT-SAFE` | superseded |
| R10 | `96880857-160a-4881-a1f1-fdf0b3610621` | `NOT-SAFE` | `NOT-SAFE` | `SAFE` | superseded |
| R11 | `133f498f-020f-413b-9933-2e232c6e37f6` | `SAFE` | `NOT-SAFE` | `SAFE` | superseded |
| R12 | `389efbca-093f-4721-8b95-04280e94c94f` | not dispatched | not dispatched | not dispatched | invalid before prepare; cleaned |
| R13 | `1ff6da27-958d-4ef8-b5eb-e0a1de2b9838` | `NOT-SAFE` | `SAFE` | `SAFE` | superseded |
| R14 | `87b662cb-ca12-4705-9d17-8c1511905428` | `NOT-SAFE` | `SAFE` | `NOT-SAFE` | superseded |
| R15 | `b3980240-0a04-4b2a-8c5b-ea3d7207cbce` | `SAFE` | `NOT-SAFE` | `SAFE` | invalid framing; superseded |
| R16 | `87db9865-71dc-4877-a2eb-947ef57b6af6` | `SAFE` | `NOT-SAFE` | `SAFE` | invalid framing; superseded |
| R17 | `2d94709c-47a7-4dee-a8b0-62425feac7fb` | `SAFE` | `SAFE` | `NOT-SAFE` | exact branch selector accepted |
| R18 | `2dafcde2-de17-4575-894f-6c4b281446b1` | `NOT-SAFE` | `SAFE` | `SAFE` | packaged render/verify qualification accepted |
| R19 | `1d95c108-cde4-4a3a-b849-7b6bf6ec43e5` | `NOT-SAFE` | `SAFE` | `NOT-SAFE` | provider-wrapper exclusion accepted |
| R20 | `349b5631-3435-4a30-9018-aa50793ab273` | `SAFE` | `SAFE` | `SAFE` | admitted |

The admitted formal round was
`20260809-triad-skill-sot-formal-plan-r20-349b5631-3435-4a30-9018-aa50793ab273`
with content digest
`c0dbfc5ca7fbb138956691b99feffa45ec33acc0fbddca64d53c85b80fd0be62`.
Its captured plugin-worktree fingerprint was
`298e53be3ec68c46d0dc5ace2fd3ee7e7265fc3c8f826c14ef4508243e4508de`
before dispatch and after every leg. All three result files passed the strict
verdict schema with the bound ID, family, and digest, and the final lifecycle
verification printed `ROUND_INTEGRITY_OK`.

Claude returned two Minor suggestions in the admitted round. The leader did
not adopt them: adding a receipt channel for the conditional old-root sweep is
outside the unchanged no-sibling scenario, and pinning one more exact prose
sentence is wording hardening rather than a required behavioral correction.
Neither suggestion identifies a Critical or Major defect in the approved
minimal design. No generalized protocol or extra skill capability was added.

The supported cleanup command returned `removed: true` for the exact R20
managed root. The exact R20 fixture leaf was then removed after directory and
symlink checks. Post-cleanup inventory contained neither that managed root nor
that fixture and showed no sibling managed review root or sibling fixture.

Task 2 is admitted and complete. Task 3 may now perform only the bounded TDD
changes named by the admitted plan.

## Task 3 minimum TDD correction

The test-only RED edit changed no collected case. The three exact selectors
failed for the intended missing contracts:

- current task/plan authority: the source skill still linked and required the
  current `CHANGELOG.md` release entry;
- managed lifecycle: the prompt and leg contracts were first loaded after the
  render point and the bounded zero-provider characterization was absent;
- distribution verifier: the report contained only two hash targets instead of
  the required fourteen.

The module ledgers were exactly `2 failed, 14 passed` for
`tests/test_distribution_contract.py` and `1 failed, 7 passed` for
`tests/test_distribution_verifier.py`. The candidate correction changes only
the existing selectors, source skill, workspace executor reporting/profile
pin, verifier target tuple, current changelog entry, and this current status.
No `review_round.py` change or new regression case is warranted: its existing
invalid-member-list regression already covers the Task 1 tool rejection.

The 2026-08-08 maintenance-status statement that the public skill reads the
current `CHANGELOG.md` release entry before packet preparation is historical and
superseded. The current owner-supplied task or explicitly designated executable
plan is now the execution authority and must carry every retained or rejected
decision needed to execute that task; a missing needed decision goes to the
owner and is not recovered from release history at runtime. The historical
2026-08-08 status file remains unchanged.

The same three selectors then passed `3 passed`. The exact modules passed
`16 passed` and `8 passed`, `tests/test_review_round.py` passed `78`, and the
established focused command passed `132`. The workspace executor profile now
pins the exact source `SKILL.md`; its added text defines only receipt and process
reporting, while lifecycle behavior remains in the source skill. The verifier
hash tuple is exactly the fourteen admitted distribution targets.

The skill-creator validator returned `Skill is valid!`. The mechanical
skill-prompt linter reported only candidates in existing text. A new
prompt-controlled, no-edit fresh Codex child reviewed the source skill and its
references and returned five suggested failures. Pre/post root and plugin
fingerprints were identical around that review. The leader rejected all five:
removing the existing distribution-acceptance section, adding a table of
contents to an unchanged reference, and rewriting unchanged placeholder command
examples are general skill-quality work outside this slice. The cited command
examples use the existing no-space approved paths in the current workflow and
the Task 3 behavior does not alter invocation construction. No source or
reference change was made for those suggestions.

Task 3's bounded implementation and focused GREEN are complete. A mandatory
workspace-root Codex restart is still required before Task 4 so the edited
registered-agent profile is reloaded.

## Historical checkpoint: Task 4 fresh-session attempts and bounded restart gate

At this checkpoint, Task 4 had not passed. Two fresh
`agent_type="triad-skill-executor"` threads
used the unchanged Task 1 scenario, returned `WORKFLOW_DEFECT`, cleaned their
exact disposable paths, and left both canonical worktrees unchanged.

The first attempt was `/root/triad_skill_green`, review ID
`skill-executor-dfc455e5-4eaf-49c6-8ada-88ce174beab2`. It selected the stale
installed-cache skill at
`/Users/chaniri/.codex/plugins/cache/triad-codex-dispatch/triad-codex-dispatch/0.2.533/skills/triad-cross-family-review/SKILL.md`
instead of the configured source. It reached `prepare`, then passed
`shared/source/product` rather than the exact returned `shared/` directory to
`manifest`; the packaged lifecycle command rejected that path. Supported
cleanup returned `removed: true`, the exact fixture leaf was removed, and the
leader independently confirmed both paths absent. The root and plugin
fingerprints exactly matched their pre-attempt values.

Official Codex documentation and the observed catalog behavior reproduced the
source-selection cause: repository skills are discovered under
`.agents/skills`, while `skills.config` is a per-skill enablement override and
does not make an arbitrary worktree path a discovered skill. The smallest
workspace-owned catalog correction added exactly one symlink:

```text
/Users/chaniri/codex_workspace/.agents/skills/triad-cross-family-review
  -> /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review
```

The symlink is a discovery pointer, not a copy or second SOT. Its resolved
`SKILL.md` SHA-256 equaled the canonical source SHA-256. No user-global skill,
plugin cache, provider setting, permission setting, tool surface, or external
workspace changed.

The second attempt was `/root/triad_skill_green_r2`, review ID
`skill-executor-red-a9898b8e-c5b0-4d8f-a152-8ae3ae5ba636`. It proved the
workspace source skill was now discovered, but reported its discovery-symlink
alias and stopped during `prepare`. The first invocation had a corrected local
quoting retry; the correctly quoted invocation then exited `126` because the
source skill said to execute bare `bin/review_round.py` while the tracked file
mode is `100644`. No managed review root was created. The exact fixture leaf
was removed, and the leader independently confirmed its absence and unchanged
pre/post root and plugin fingerprints.

The behavior failure supplied the skill RED. The existing
`test_cross_family_skill_uses_managed_review_workspace_lifecycle` selector was
extended without adding a collected case to require literal `python3` for all
six packaged lifecycle subcommands. It failed exactly on the missing
`python3 bin/review_round.py prepare` contract. The minimum GREEN changed only
the command spelling in the source skill and added the direct-execution
prohibition. The same selector then passed `1`, and the complete
`tests/test_distribution_contract.py` module passed exactly `16`. The skill
validator returned `Skill is valid!`; the executor TOML parsed; both
repositories passed `git diff --check`.

The workspace executor profile now also requires every filesystem instruction
source receipt to resolve through realpath and report the canonical absolute
target rather than a discovery-symlink alias. This is a reporting correction,
not duplicated lifecycle behavior. Because that registered profile changed,
the current root session cannot supply Task 4 acceptance. End it and open a new
Codex session at `/Users/chaniri/codex_workspace`; do not reuse either failed
executor thread.

These are the pre-handoff-documentation repository snapshots. This status and
the handoff edit necessarily change the plugin fingerprint, so the next
session must record a new plugin baseline rather than compare that fingerprint
for equality.

| Repository | Branch | HEAD | Status fingerprint | Diff fingerprint |
|---|---|---|---|---|
| workspace root | `codex/workspace-argus-agents` | `7554c18031ee51f6275ad4625a302971c1803c14` | `57614738d5858764aa49fb2ecfc61c56c8773416b3e56d81db55e4c6a6235753` | `011b7afc437e687b4e1d662cb716def1f2b817200e717248086c7fdcbe8a6aee` |
| plugin worktree | `release/0.2.532` | `8b2f66edae8af6fc9bd32cdf35cf4cbb3006879c` | `32cc9d8fd7a29bf330732e6247aedcd070f42b9fba7581bb5765e827171fd4e4` | `395823655d869d7dec1a346148d2f10b671c37baca695fa1341f4b40c991ae72` |

Exact next-session reload bindings:

| File | SHA-256 |
|---|---|
| `/Users/chaniri/codex_workspace/.codex/agents/triad-skill-executor.toml` | `cbfd99805f31c8ee06867acd4fdba4c7cadf3ef7bffd9a5713a7bde09babe694` |
| `/Users/chaniri/codex_workspace/AGENTS.md` | `75aaa503c8588a39295e5646e69768f35d732355c75ad1bf14f13105dba57418` |
| `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/SKILL.md` | `686380fe10b405e83d03682482bb4c977eb1d9277acd8875fec76a4ded7e2f7a` |
| `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/review-prompt-contract.md` | `3489d805d95af6736b4a44c750175df727a9108e243f3abddeea52399e613a31` |
| `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review/references/leg-contracts.md` | `3c6a76ecc3061e9699f5d8b36e06436d65e46f58fe92ecd1db87b09b82b1ea15` |

On restart, confirm the live catalog exposes `triad-skill-executor`, confirm
the symlink resolves to the canonical source directory above, verify all five
hashes, and start Task 4 again from its first pre-spawn fingerprint with a new
executor thread and review ID. The returned `instruction_sources` must contain
exactly the canonical source `SKILL.md`, root `AGENTS.md`,
`review-prompt-contract.md`, and `leg-contracts.md` paths required by the plan;
the `.agents/skills` alias itself is not an accepted receipt path. Task 4 leader
reproduction, full verification, pre-merge, package, push, install, and
fresh-process installed-skill proof remain unstarted.

## Task 4 third attempt and bounded capture correction

The fresh executor `/root/triad_skill_green_r3` used review ID
`skill-executor-9f690aa5-20e2-476f-8a4f-e572316bd4c8` and selected the exact
canonical source skill. It returned `WORKFLOW_DEFECT`. Its first `prepare`
shell invocation had malformed argument quoting and exited `1` before Python
or packet creation; the executor then retried with corrected quoting under the
same ID. That retry and `manifest` exited `0`. The attempt remains invalid and
the next trial must contain no such failed invocation or retry.

The deterministic stopping defect occurred at `capture`. The executor followed
the source skill's incomplete spelling and ran packaged `capture` with only
`--prepared-dir`; argparse exited `2` because `--worktree` and `--output` are
required. No snapshot or prompt was created, so the final canonical
instruction-source receipt correctly stopped at root `AGENTS.md` and the source
`SKILL.md` rather than reading the two render references. Supported cleanup
returned `removed: true`; the exact managed root and fixture leaf are absent,
the pre/post root and plugin fingerprints remained
`57614738d5858764aa49fb2ecfc61c56c8773416b3e56d81db55e4c6a6235753` /
`011b7afc437e687b4e1d662cb716def1f2b817200e717248086c7fdcbe8a6aee`
and
`32cc9d8fd7a29bf330732e6247aedcd070f42b9fba7581bb5765e827171fd4e4` /
`1631526861b1bad7f2a58a0934b70a7aa9a26564d836caf26d0b3febadad601b`,
and pre/post inventories contained no sibling managed review root or executor
fixture.

Leader reproduction of the exact incomplete `capture` spelling also exited `2`
and reported the two missing required arguments. The existing managed-lifecycle
selector was extended in place to require
`python3 bin/review_round.py capture --prepared-dir <shared> --worktree
<canonical-worktree> --output <returned-root>/results/snapshot.json`; it failed
for that missing contract. The minimum GREEN changed only the corresponding
source-skill sentence. The selector then passed `1`, the full distribution-
contract module passed `16`, the skill validator returned `Skill is valid!`,
and `git diff --check` passed. The corrected source `SKILL.md` SHA-256 is
`f4707befffdbbbe2aa920f94c39d877504b72d82525a16fbc82e1b673cfab5a6`.
No profile, lifecycle tool, provider wrapper, permission, MCP, installed cache,
or user-global setting changed. Task 4 restarts from a new pre-spawn baseline,
executor thread, and review ID; the third attempt is not reusable evidence for
GREEN acceptance.

## Task 4 fourth attempt and bounded toolkit-root correction

The fresh executor `/root/triad_skill_green_r4` used review ID
`skill-executor-a7316933-c0d8-400f-9395-5661c03daa62` and read the canonical
source skill. It nevertheless failed to derive the packaged toolkit from that
source path. Ignore-aware searches from the workspace root did not enumerate
the nested plugin repository, so it searched outside the authorized workspace
and selected the unrelated `/Users/chaniri/triad-codex-dispatch` checkout. It
made no write there, but that read/command route was outside the configured
canonical source boundary and is not reusable evidence.

The first `prepare` shell invocation again had malformed JSON argument quoting
and exited `1` before Python. Its corrected retry then invoked the wrong
checkout's stale lifecycle tool and exited `2` because that tool exposes only
`capture`, `verify`, and `render`, not `prepare`, `manifest`, or `cleanup`. No
managed review root was created. The exact fixture leaf was removed and the
pre/post root and plugin fingerprints remained
`57614738d5858764aa49fb2ecfc61c56c8773416b3e56d81db55e4c6a6235753` /
`011b7afc437e687b4e1d662cb716def1f2b817200e717248086c7fdcbe8a6aee`
and
`32cc9d8fd7a29bf330732e6247aedcd070f42b9fba7581bb5765e827171fd4e4` /
`f8ab24eaf279d591ebde17e98ad5a7184cf3083aa342c1904c611e5ff4aa02be`.
Independent inventory again found no managed-root or executor-fixture residue.

Leader comparison showed canonical `bin/review_round.py` SHA-256
`d64598acaeecdbd236975f18a93d06935d442de87c0bc8d055eaa91f0cc36622`
with all six lifecycle subcommands, while the wrongly selected file was
`3c9c63b20d9d2b7cb149d8bf989110b48bb1b908ad54033b15b6290e0b7c1d35`
and had only the three stale subcommands. The source skill had no rule binding
its displayed `bin/review_round.py` paths to the repository containing the
canonical source skill.

The existing managed-lifecycle selector was extended in place to require that
canonical toolkit-root rule and prohibition on searching or substituting
another checkout or installed-cache copy. It failed for the missing contract.
The minimum GREEN added only that path-resolution sentence to Flow step 2. The
selector then passed `1`, the complete distribution-contract module passed
`16`, the skill validator returned `Skill is valid!`, and `git diff --check`
passed. The corrected source `SKILL.md` SHA-256 is
`60ca9c058324cc1d12efc84dfbc2af1e77172e827e9b95ae86117d0bd0bb4a64`.
No profile, runtime tool, provider wrapper, permission, MCP, installed cache,
or user-global setting changed. Task 4 again restarts with a fresh executor
thread and review ID; the fourth attempt is not reusable GREEN evidence.

Attempts 3 and 4 independently reproduced the same executor-level JSON argv
failure and prohibited corrected retry. The workspace profile named JSON
encoding and login-shell execution but did not specify a shell-safe one-argv
transport or require fail-fast behavior before the packaged Python process
starts. The bounded reporting/execution correction now requires every JSON-
valued CLI argument to travel through a task-specific variable as one double-
quoted argv value, forbids nested single-quote splicing and zsh glob exposure,
and requires the executor to stop without a corrected retry or review-ID reuse
after any nonzero lifecycle attempt. It adds no lifecycle command, packet rule,
receipt field, provider behavior, or tool restriction. Login-shell `tomllib`
parsing returned `EXECUTOR_PROFILE_OK`; the corrected profile SHA-256 is
`d69dc06eae8006bbb02c732e9338d9ed0ad6e0d3f97404af1eeb885c51fc183f`.
Because the registered profile changed, the current root session cannot supply
the next Task 4 acceptance trial. Open a new root session at
`/Users/chaniri/codex_workspace`, reapply the required skills, reread the plan,
status, and handoff, verify the new profile and source hashes, and start one new
executor with the exact unchanged scenario.

## Owner correction: executor is the clean-context observation surface

The owner rejected the attempt-3/attempt-4 classification that made the
registered executor profile a workflow-repair surface. The executor exists only
to load the configured source skill in a fresh `fork_turns="none"` context,
execute the leader-supplied scenario, and report the observation without
editing the skill. Per-run commands, receipt fields, success criteria, shell
transport, and lifecycle behavior do not belong in its TOML.

The profile-level correction recorded immediately above is therefore
superseded and removed. The current profile contains only the stable model and
effort, one minimal no-edit executor instruction, and the exact source
`SKILL.md` enablement entry. Its SHA-256 is
`819148f8f6c59bba5b24f9fd4d0acb01d116b78f2f68afb3ebde675a45bdcef3`.
The complete behavior and receipt contract now lives in the exact Task 1/Task 4
`spawn_agent.message` in the executable plan.

A separate fresh default read-only reviewer found no criterion failure in the
corrected source skill and specifically admitted the JSON one-argv and same-ID
fail-fast guidance. The first fresh prompt reviewer found that the leader's
message did not fully type nested receipt values. A second pass also reproduced
that the hostile JSON input had no fixed injection or observation location. The
leader corrected only the plan's spawn message: it now fixes the disposable
fixture layout, exact payload, decoded round-trip check, and recursive JSON
receipt shape. A final fresh default read-only reviewer returned no failures and
confirmed that command construction remains owned by the configured skill.
Final pre-reload verification under Python 3.12.13 and pytest 9.0.3 passed the
complete 16-case distribution-contract module and the existing special-JSON
round-trip selector. Skill validation returned `Skill is valid!`, the profile
check returned `MINIMAL_EXECUTOR_PROFILE_OK`, both repositories passed
`git diff --check`, and the recorded profile/source/reference hashes matched the
current files.

Attempts 3 and 4 remain valid failure observations: both malformed a simple
JSON-valued CLI argument before Python and then retried under the same review
ID. Existing `review_round.py` argv-level tests already prove that the packaged
tool accepts correctly transported JSON, so no lifecycle-script change was
warranted. The existing managed-lifecycle selector was extended first and
failed on the missing source-skill contract. Under Python 3.12.13 and pytest
9.0.3, it then passed after the minimum source `SKILL.md` correction required
each JSON-valued lifecycle option to be one shell argument and invalidated any
failed lifecycle process, including a pre-Python shell failure, without a
corrected same-ID retry. The corrected source `SKILL.md` SHA-256 is
`4aed9e7d831e9895f524a3fe84e2e1648c5dd2dcc76e014858f1cd6ac4b20811`.

Because this owner correction changes the registered TOML itself, one final
workspace-root restart is required to load the minimal profile. After that
reload, further source-skill or script changes require a new clean executor
thread and review ID, not another parent-session restart, unless the TOML or
catalog changes again. None of the first four executor threads or review IDs is
reusable as GREEN evidence.
