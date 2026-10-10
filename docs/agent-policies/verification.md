# TRIAD verification

Read for source checks or release verification.

## Verification

- Each host runs the common regression suite and its own OS-specific checks:
  macOS on macOS, Ubuntu on Ubuntu. Do not launch another OS through Docker or
  emulation to discharge that OS owner's verification responsibility. Record
  another OS as not run on this host and hand it to that OS's owner or native
  CI runner; do not add a release gate solely because the other host is absent.
  Keep each result's commit, OS, architecture, Python version and skips visible.
  Historical container results remain historical observations, not native-host proof.
- Resolve this checkout's canonical absolute root before invocation and pass it as `$1` while the
  host command uses the cwd required by the applicable host policy (otherwise this checkout).
  Before Python tooling, record `command -v python3`, `python3 --version`, and
  `python3 -m pytest --version` in the same `/bin/zsh -lic` environment.
  Run the full repository suite with
  `/bin/zsh -lic 'python3 -m pytest -q "$1/tests" --rootdir "$1" -p no:cacheprovider' triad-tests /absolute/path/to/this-checkout`.
- When `scripts/bootstrap.sh` changes, also run
  `/bin/zsh -lic 'bash -n "$1/scripts/bootstrap.sh"' triad-bootstrap /absolute/path/to/this-checkout`.
- Run
  `/bin/zsh -lic 'python3 "$1/scripts/verify_distribution.py" --source-root "$1" --output-dir "$1/_runs/distribution/<label>"' triad-distribution /absolute/path/to/this-checkout`
  only for a release candidate from a clean committed HEAD and use a unique label. Archive
  verification does not prove fresh-process exposure or public release. Never use a bare
  repository-relative path for these commands when the host command starts outside this checkout.
