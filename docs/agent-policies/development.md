# TRIAD development contracts

## Scope and source boundary

- Manage only the Codex-hosted TRIAD implementation. Treat the Claude-hosted `codefoundry-io/triad-dispatch` repository as a read-only reference. For shared defects, provide an evidence-backed fix prompt for its maintainer; do not modify that repository.
- Shared-spec authoring and cross-host coordination follow [the shared authoring reference](https://github.com/codefoundry-io/triad-dispatch-spec/blob/main/reference/spec-authoring.md) (`R-AUTHORING-SYNC`). This is a maintainer reference, not an installed revision override.
- Treat this checkout's plugin manifest, skills, scripts, tests, and public documentation as the development source surface. Do not edit an installed plugin cache or copied distribution as a substitute for source changes.
- `migration/AGENTS.recommended.md` is shipped consumer guidance; it does not govern development of this checkout.

## Project contracts

- For a release or version change, keep `.codex-plugin/plugin.json` version, the current `CHANGELOG.md` heading, and the upgrade headings in `README.md` and `README.ko.md` synchronized as required by `tests/test_distribution_contract.py`.
- When user-visible behavior, authentication, security posture, or update flow changes, update the affected English, Korean, security, migration, and contract-test surfaces in the same bounded change.
- Preserve the bootstrap runtime requirement of Python 3.12 or newer unless the owner explicitly approves a compatibility change.

## Formal review

- Select guarded existing-worktree review for this repository. When the owner
  workspace's formal-review policy applies, its current four-leg policy supplies
  the common full-scope criteria and conditional native advice. An independent
  checkout must obtain an explicit owner composition before starting a formal
  gate if none is applicable. Do not infer extra legs from historical plans or
  the two-focus reference. Local orchestration instructions need not be exposed
  merely to explain reviewer composition; shipped skills and behavioral
  documentation remain review material.
- Supply the objective, diff and existing worktree. Reviewers discover related
  unchanged code, tests and documents themselves; a changed-file inventory is
  not a read allowlist. Do not enumerate or approve their individual source reads.
  Preserve explicit private-data exclusions and the existing read-only controls.
- Normal collection validates results, bindings, required route evidence and
  source integrity. Inspect provider/read logs only for a concrete failure,
  access or contamination concern, or an explicit audit request, limited to that
  issue. Do not add a routine source-read audit or reject a relevant file because
  it was absent from the diff inventory.

## Review custody and cleanup


Keep current task/status/diff custody under the existing worktree's ignored
`_runs/review-custody/<review_id>/`; keep prompts, results, logs and ledger
separately in the workspace root's `_runs/reviews/<review_id>/`. Preserve
durable evidence there. After terminal collection, integrity and adjudication,
remove only the exact current source-SOT temporary stage/cwd handles. Do not
delete historical custody, ignored work, or unrelated worktrees.
