# TRIAD source-skill development

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
- Use the dedicated `agent_type="triad-skill-executor"` at `gpt-6.1-sol` /
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
  code tests, static checks, or catalog presence do not replace Sol/high behavior.
- If the dedicated role is unavailable, resolves another source, or the source
  changes during execution, stop the affected test and report the evidence. Do
  not substitute a default agent, same-thread rerun, or installed cache.
- Keep skill behavior, operational review, distribution integrity, installation,
  fresh-process exposure, and public release as separate claims. Follow applicable
  host permissions; changing global settings/caches or merging requires the
  corresponding explicit owner authorization.
