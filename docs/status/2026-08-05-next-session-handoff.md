# TRIAD 0.2.533 Next-Session Handoff

Date: 2026-08-06

Status: post-r7 bounded-correction handoff. Review round r7 was invalid because
the Claude leg timed out at the incorrectly reused 600-second deadline. Google
and fresh Codex returned admitted `SAFE`; Codex's one Minor documentation
finding reproduced. The timeout contract and stale progress note are corrected
in the pending r8 candidate; final admission and installation remain incomplete.

## Start here

Work from:

```text
/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
```

The implementation branch is `release/0.2.532`; the plugin manifest version is
`0.2.533`. The pending r8 candidate includes the owner-approved 0.2.533 tasks
and the bounded r2 through r7 corrections recorded below.
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
- Source tests for the pending r8 candidate: `426 passed` under Python 3.12.13
  and pytest 9.0.3. Do not reuse earlier 406-, 422-, 424-, or 425-test snapshots.

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

## Final review state and pending r8

Review round `final-0.2.533-r7` used prepared digest:

```text
8e146f6d412fabb1580a63f81c59c547fc5005f471988b15250ecdb1e82d341c
```

- Google: valid `SAFE`, no findings.
- Claude: invalid; the wrapper timed out at 600 seconds without a `LegVerdict`.
- Fresh Codex: valid `SAFE`, one Minor documentation finding.
- Prepared directory and canonical worktree: `ROUND_INTEGRITY_OK`.

The Codex Minor reproduced against canonical source: the current-authority
release plan still described the post-r5 state and a pending r6 round. The
pending r8 candidate updates that progress note to the completed invalid r7 and
pending r8 state.

The leader also reproduced the timeout contract gap. Prior owner direction and
validated formal dispatch used a generous 1,800-second wrapper deadline, but
the current leg contract omitted `--timeout`; the leader copied the r6
600-second invocation into r7. The pending r8 skill reference requires
`--timeout 1800` for the formal Claude leg while leaving ordinary Claude
dispatch defaults unchanged.

Run a fresh complete `final-0.2.533-r8` round over a new digest, including the
active `docs/references/repair-protocol.md` boundary and the same explicit
80-file boundary. Do not reuse r5 through r7 verdicts for final admission.

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

The latest verified pre-r8 archive was staged at:

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
only after unanimous r8 admission and exact packaged-byte verification. Do not
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

Finish TRIAD 0.2.533, prove the installed skill in a fresh process, ask the
owner to open the new session, then resume the reconciled infrastructure Task
10 before touching the Argus product checkpoint.
