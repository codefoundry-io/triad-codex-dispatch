# AGY Project Permission Boundary

**Authority:** The owner selected option 3 (a scoped AGY project), approved the
two synthetic project configurations, and instructed continuation after the
spike. This plan implements that bounded route in the canonical TRIAD source.

**Evidence:** `_runs/infra/20260914-agy-project-read-boundary-spike` in the
workspace operating repository records AGY 1.2.2 native `view_file` trials.
Pro High and Flash High each read the allowed sentinel, received a native deny
for the restricted file, and read both sentinels in the control project. All
four calls preserved the global settings, project files, and fixture bytes.
This is evidence for native path-deny behavior, not formal review admission or
proof against every possible read mechanism.

**Behavioral claim:** An explicit AGY project binds preflight and dispatch to
that project's configured read-only permissions without a global settings lease.

## Scope and budget

- Production estimate: 100–180 net lines across the wrapper, settings helper,
  and existing receipt validation. Novel core: under 100 lines. One claim.
- Canonical SOT remains the checkout resolved by the workspace skill symlink;
  use a new branch there, not a copied skill or installed cache.
- Keep the legacy no-project transaction, model/authentication selection,
  native schema/result validation, and public receipt keys unchanged.
- No project creation or editing by the wrapper, policy attestation protocol,
  dynamic capability probe, new metadata schema, or installation in this slice.
- The owner controls project permissions for the entire call. The existing
  cooperative global lease does not prevent arbitrary external configuration
  writers either; concurrent owner edits are outside this bounded contract.

## Exact design

`antigravity_wrapper.py --project <canonical lowercase UUID>` requires
`--sandbox read-only` and an explicit validated `--cwd`. Before inference,
read only `~/.gemini/config/projects/<UUID>.json`; require matching `id`, exactly
one `projectResources.resources` entry with `folderUri` equal to the canonical
cwd URI, and a string deny list containing all five existing read-only rules:
`write_file(*)`, `command(*)`, `unsandboxed(*)`, `execute_url(*)`, `mcp(*)`.
Additional owner-defined rules remain untouched. Reject invalid configuration.
The project branch performs no global transaction and writes no permission file.

The native invocation and preflight receipt both append `--project <UUID>` to
the existing model/effort `route_args`. Receipt validation accepts only the
legacy four-token form or the exact six-token form. Existing receipt hashes
and final argument equality bind the project without adding metadata fields.
The Pro/Flash pair must use the same project suffix, including both absent.
Version/model preflight remains free of inference calls.

## Execution and verification

1. Root writes focused regression tests against the exact source. Cover valid
   project preflight and dispatch without permission-file writes, invalid
   project/cwd/id/deny rules before inference, receipt argument substitution,
   malformed UUIDs, and paired project mismatch. Existing tests cover legacy
   transaction restoration and native output contracts.
2. A fresh `triad-skill-executor` (`fork_turns=none`) runs those tests and records
   intended RED, canonical SOT, before/after fingerprints, command and cleanup.
   Root does not edit production until that result is observed.
3. Root implements the exact design in `bin/antigravity_wrapper.py`,
   `bin/_agy_settings.py`, and `bin/review_round.py`; updates affected English,
   Korean, security, migration, and skill contract documentation. No version bump.
4. A separate fresh executor runs focused GREEN, the entire repository pytest
   suite, and the canonical skill validator. Run from the saved workspace root:
   `/bin/zsh -lic 'python3 -m pytest -q "$1/tests" --rootdir "$1" -p no:cacheprovider' triad-tests /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`.
   Record unchanged source fingerprints. Distribution checks follow only on a
   clean committed release candidate, as required by project policy.
5. Root conducts the required fresh four-leg guarded-worktree review, reproduces
   findings within this design, and reruns a full fresh round after corrections.
   Record source tests separately from formal admission and deployment.

## Next owner boundaries

Final merge requires explicit owner approval. A real Argus review project or
changed installed-cache bytes require a concrete exact-path authorization if
not already authorized. The synthetic projects are not repurposed implicitly.
Argus 04B remains at its failed R6 plan gate until the corrected review route is
available and a fresh complete plan review is admitted.
