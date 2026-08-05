# TRIAD 0.2.533 Next-Session Handoff

Date: 2026-08-05

## Start here

Work from:

```text
/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
```

The implementation branch is `release/0.2.532`; the intended plugin manifest
version is `0.2.533`. The bounded post-review correction is commit `1d53775`
(`fix: bind review routes to captured evidence`). A later handoff-only commit
may be the session HEAD.

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
- Source tests after final bounded corrections: `406 passed in 120.99s`.

Important commits, newest last before this handoff:

```text
33dd517 docs: record convergent runtime benchmark
1d53775 fix: bind review routes to captured evidence
```

## Final review state

Final review round `final-0.2.533-r1` used prepared digest:

```text
8c7d3ca6614b2ae08f624f07e26c427ad9604f9500b0bd14a4cf52e8c8293e8f
```

- Google: valid `SAFE`.
- Claude: valid `NOT-SAFE`.
- Fresh Codex: valid `NOT-SAFE`.
- Prepared directory and worktree: `ROUND_INTEGRITY_OK`.

The reproduced approved-design defects were corrected in `1d53775`:

- render-time digest is recomputed from the prepared bytes;
- unusable review IDs fail before dispatch;
- the prompt correctly allows `NOT-SAFE` with an open question and no finding;
- AGY invalidates an exposed model conflict and records exposed/unexposed
  runtime identity;
- structured Claude and AGY preflight restore stale-run-log pruning;
- `--repair-mode` plus Claude structured output fails explicitly;
- the English and Korean READMEs no longer advertise retired deterministic
  batch/receipt/coverage behavior;
- distribution tests reject the remaining retired documentation phrases.

No fresh three-family round has reviewed `1d53775` yet. A fresh round over a
new prepared directory and digest is required after the remaining owner
decisions are applied.

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

An earlier archive was staged at:

```text
_runs/distribution/0.2.533/triad-codex-dispatch-0.2.533.tar
```

Its SHA-256 was
`a6a61ea548031e1f9c2d72f9072b5409bf6596bddd50b37150d2663c714cc7d2`
and its unpacked bytes passed `402` tests, but it predates `1d53775`. It is stale
and must not be installed or used as final evidence.

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

Do not push, tag, publish, merge, or create a release unless separately
authorized.

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
