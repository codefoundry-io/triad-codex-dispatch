# Workspace Skill Development Test Policy

## Scope

This owner-governed workspace policy applies whenever a skill or any bundled script,
reference, asset, or test is created or changed.

## Trigger

Read this file completely before writing a skill test or modifying any skill source or
bundled asset. Only the complete sequence below authorizes the claim `TESTED`; if any
required step is absent, report the skill as `UNTESTED`.

## Precedence

Direct owner instructions and explicit owner-dated exceptions in root `AGENTS.md` take
precedence. Project-local instructions may add stricter skill checks but may not replace the
canonical-SOT, fresh-executor, RED/GREEN, distribution, or deployment boundaries here.

## Canonical owner

This file is an owner-governed extension of root `AGENTS.md`, not ordinary product
documentation. The root Codex leader owns the canonical live source of truth (SOT), writes
the test source, makes every SOT change, and is the only editor of this policy.

## Canonical source and workspace links

Maintain this policy and `config/codex/agents/triad-skill-executor.toml` in the
Codex-host TRIAD source repository. The workspace paths
`docs/agent-policies/skill-development.md` and
`.codex/agents/triad-skill-executor.toml` must be symlinks to those originals;
do not maintain divergent workspace copies.

## Fail-closed behavior

A missing, stale, or unprovable dedicated test-agent route is a stop condition, not
permission to use a fallback. Static inspection, root-leader test execution, a same-thread
rerun, TOML parsing, path existence, formal multi-family review, package hashes, installed
inventory, or tests against noncanonical bytes may supplement this protocol but never
replace a required step.

## Canonical SOT and RED

- The SOT is the exact skill directory used by workspace discovery and later packaging or
  deployment. A copied skill, installed cache, another checkout, or remembered prompt is not
  an acceptable substitute.
- Before changing skill behavior, the root leader writes a bounded failing scenario or
  automated test against that exact SOT.
- A fresh dedicated skill-test Custom Agent, selected by its exact `agent_type` with
  `fork_turns = "none"`, runs the focused test and must observe the intended RED result
  before the root leader edits production skill content.

## Dedicated behavior-only executor

- The skill-test agent must not edit the SOT or its tests, dispatch operational providers,
  or lead a production review.
- It may create the exact disposable fixture required by the test and must remove that
  fixture afterward.
- Its report records the SOT realpath, source commit and status or fingerprint before and
  after execution, exact commands, results, and cleanup evidence.

## Implementation and GREEN

- After the root leader applies the smallest implementation change, a separate fresh
  instance of the dedicated skill-test agent runs the focused GREEN test, the complete
  relevant regression suite, the skill validator, and distribution checks when applicable.
- The GREEN executor again proves the exact SOT and an unchanged source fingerprint.

## Review, distribution, and deployment boundaries

- Operational review and deployment remain separate gates. The root leader owns any
  operational cross-family review.
- Deployment proof independently binds the tested SOT to packaged and installed bytes and
  demonstrates fresh-process discovery when release scope requires it.
- A source/static pass, formal-review admission, distribution verification, installed-cache
  equality, and fresh-process exposure are separate claims; never substitute one for another.

## TRIAD skill test role

For `triad-cross-family-review`, the required dedicated test role is
`agent_type = "triad-skill-executor"`; that role is never the operational TRIAD leader.

- Baseline TRIAD behavior acceptance requires `gpt-5.6-terra` with `high`
  reasoning effort. Higher-model or higher-effort investigation does not replace
  a passing Terra/high baseline. Record requested settings and actual runtime
  metadata when exposed; otherwise record `UNEXPOSED` without inventing attestation.
- Start every independent scenario, RED, and GREEN with a new dedicated executor
  and `fork_turns = "none"`. Do not reuse a prior executor thread.
- Supply only the current scenario, required source/fixture paths, constraints,
  and output contract. Do not pass earlier decisions, review verdicts, repair
  narratives, or parent conversation history. Governing instructions still apply.
- For provider-free behavior characterization, use the configured skill and its
  packaged verifier; require canonical-source integrity and exact fixture cleanup.
  Record actual execution separately from route discovery, code-test results,
  operational provider review, and complete skill-protocol certification.
