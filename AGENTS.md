# Triad Codex Dispatch Repository Instructions

## Scope and source boundary

- These instructions apply to this entire Git repository.
- Treat this checkout's plugin manifest, skills, scripts, tests, and public documentation as the development source surface. Do not edit an installed plugin cache or copied distribution as a substitute for source changes.
- `migration/AGENTS.recommended.md` is shipped consumer guidance; it does not govern development of this checkout.

## Project contracts

- For a release or version change, keep `.codex-plugin/plugin.json` version, the current `CHANGELOG.md` heading, and the upgrade headings in `README.md` and `README.ko.md` synchronized as required by `tests/test_distribution_contract.py`.
- When user-visible behavior, authentication, security posture, or update flow changes, update the affected English, Korean, security, migration, and contract-test surfaces in the same bounded change.
- Preserve the bootstrap runtime requirement of Python 3.12 or newer unless the owner explicitly approves a compatibility change.

## Verification

- Run the full repository suite with `/bin/zsh -lic 'python3 -m pytest -q tests/ -p no:cacheprovider'`.
- When `scripts/bootstrap.sh` changes, also run `bash -n scripts/bootstrap.sh`.
- Run `scripts/verify_distribution.py` only for a release candidate from a clean committed HEAD and use a unique `_runs/distribution/<label>` output path. Archive verification does not prove fresh-process exposure or public release.
