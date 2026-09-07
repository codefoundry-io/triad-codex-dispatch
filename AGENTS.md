# Triad Codex Dispatch Repository Instructions

## Scope and source boundary

- These instructions apply to this entire Git repository.
- Treat this checkout's plugin manifest, skills, scripts, tests, and public documentation as the development source surface. Do not edit an installed plugin cache or copied distribution as a substitute for source changes.
- `migration/AGENTS.recommended.md` is shipped consumer guidance; it does not govern development of this checkout.

## Project contracts

- For a release or version change, keep `.codex-plugin/plugin.json` version, the current `CHANGELOG.md` heading, and the upgrade headings in `README.md` and `README.ko.md` synchronized as required by `tests/test_distribution_contract.py`.
- When user-visible behavior, authentication, security posture, or update flow changes, update the affected English, Korean, security, migration, and contract-test surfaces in the same bounded change.
- Preserve the bootstrap runtime requirement of Python 3.12 or newer unless the owner explicitly approves a compatibility change.

## Formal review

- Select guarded existing-worktree review for this repository. The workspace's
  current four-leg policy supplies common full-scope criteria and conditional
  native advice; the former two-focus reference is historical, not an extra-leg
  requirement. Governance files are not reviewer evidence.

## Verification

- Resolve this checkout's canonical absolute root before invocation and pass it as `$1` while the
  host command remains at the saved workspace root. Run the full repository suite with
  `/bin/zsh -lic 'python3 -m pytest -q "$1/tests" --rootdir "$1" -p no:cacheprovider' triad-tests /absolute/path/to/this-checkout`.
- When `scripts/bootstrap.sh` changes, also run
  `/bin/zsh -lic 'bash -n "$1/scripts/bootstrap.sh"' triad-bootstrap /absolute/path/to/this-checkout`.
- Run
  `/bin/zsh -lic 'python3 "$1/scripts/verify_distribution.py" --source-root "$1" --output-dir "$1/_runs/distribution/<label>"' triad-distribution /absolute/path/to/this-checkout`
  only for a release candidate from a clean committed HEAD and use a unique label. Archive
  verification does not prove fresh-process exposure or public release. Never use a bare
  repository-relative path for these commands when the host command starts outside this checkout.
