# Triad Codex Dispatch Repository Instructions

## Scope and source boundary

- Manage only the Codex-hosted TRIAD implementation. Treat the Claude-hosted `codefoundry-io/triad-dispatch` repository as a read-only reference. For shared defects, provide an evidence-backed fix prompt for its maintainer; do not modify that repository.
- Treat this checkout's plugin manifest, skills, scripts, tests, and public documentation as the development source surface. Do not edit an installed plugin cache or copied distribution as a substitute for source changes.
- `migration/AGENTS.recommended.md` is shipped consumer guidance; it does not govern development of this checkout.

## Skill development and behavior tests

- Open development sessions at this checkout's root. Its `AGENTS.md` and
  `.codex/agents/triad-skill-executor.toml` own the TRIAD development/test rules
  and dedicated agent definition. Keep that definition as a regular tracked file.
  A parent workspace may keep a regular copy with only the skill path rebased;
  edit the repository original first and synchronize any copy explicitly.
- The session's Codex leader owns this checkout's skill SOT, test scenarios,
  agent configuration, and instructions. Subagents report behavior or findings;
  they do not edit those surfaces. Only Codex-family agents may inspect agent TOML;
  exclude it from external-family review packets.
- Resolve `skills/triad-cross-family-review/SKILL.md` inside this checkout and
  supply its canonical absolute path with each test scenario. Read that source
  explicitly even when the installed skill has the same name. `skills.config`
  enables the pinned source; it is not a source-skill catalog installation.
- Use the dedicated `agent_type="triad-skill-executor"` at `gpt-5.6-terra` /
  `high`. Start a new instance with `fork_turns="none"` for every independent
  scenario, RED, and GREEN; never reuse a prior executor thread. Supply only the
  current scenario, canonical source/fixture paths, constraints, and output
  contract, without earlier decisions, verdicts, repair narratives, or history.
- Before changing skill behavior, the leader writes a bounded failing scenario
  against the canonical SOT and a fresh executor observes the intended RED.
  After the smallest fix, a separate fresh executor runs GREEN, the relevant
  complete regressions, the skill validator, and applicable distribution checks.
  Claim `TESTED` only when the required sequence is complete; otherwise `UNTESTED`.
- The executor must not edit source/tests, invoke other skills, conduct an
  operational review, or dispatch provider inference. For provider-free lifecycle
  characterization, follow the source skill and use its packaged
  `scripts/verify_lifecycle.py`; create and remove only its exact owned fixtures.
- Record canonical source realpath, HEAD/status or pre/post fingerprint, actual
  commands and terminal results, and exact cleanup. Record requested settings and
  exposed runtime metadata; mark unavailable fields `UNEXPOSED`. Higher-tier runs,
  code tests, static checks, or catalog presence do not replace Terra/high behavior.
- If the dedicated role is unavailable, resolves another source, or the source
  changes during execution, stop the affected test and report the evidence. Do
  not substitute a default agent, same-thread rerun, or installed cache.
- Keep skill behavior, operational review, distribution integrity, installation,
  fresh-process exposure, and public release as separate claims. Follow applicable
  host permissions; changing global settings/caches or merging requires the
  corresponding explicit owner authorization.

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
  the two-focus reference. Governance files are not reviewer evidence.

## Verification

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
