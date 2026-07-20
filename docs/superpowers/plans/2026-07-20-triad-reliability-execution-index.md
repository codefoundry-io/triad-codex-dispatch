# Triad Reliability Redesign Execution Index

> **For agentic workers:** Execute one task at a time with `superpowers:subagent-driven-development`. A fresh implementation worker owns the bounded task; the root leader runs authoritative tests outside the filesystem sandbox and reviews the resulting full files before the next task.

**Goal:** Provide the single dependency order and cross-plan invariants for the approved reliability redesign.

## Execution Order

1. [Runtime install](2026-07-20-triad-runtime-install-plan.md)
   - deterministic `--install`, explicit setup, offline/static doctor, argv-only live doctor, static execpolicy proof;
   - resolves the known stale optional-Gemini bootstrap assertion and bounded second-run hang.
2. [Immutable review packet](2026-07-20-triad-review-packet-plan.md)
   - distinct staged/unstaged/committed-range/untracked bytes, affected unchanged context, coverage gaps, immutable packet and exports.
3. [Review and repair protocol](2026-07-20-triad-review-repair-plan.md)
   - side-effect-free preflight receipts, local verdict validation, fresh native repair analysis, deterministic classifier persistence.
4. [Package integrity and skill convergence](2026-07-20-triad-package-skill-plan.md)
   - release manifest/attestation, documentation convergence, full tests, hostile argv/long-context proof, final skill/prompt gate.

Later plans may consume earlier interfaces but may not retrofit an earlier skill with a not-yet-implemented command. When two plans touch the same file, the later task starts from the earlier committed state and preserves its tested contract.

## Cross-Plan Invariants

- All direct Python, test, lint, and bootstrap verification commands run in the user's normal macOS login-terminal environment, outside the filesystem sandbox. Record `command -v python3`, `python3 --version`, and `python3 -m pytest --version`. If that interpreter lacks pytest, inspect an already installed versioned `python3.12`, record the same evidence, and use it without installing or changing the user's environment. On 2026-07-20 this selected `/opt/homebrew/bin/python3.12` because the login-shell `python3` was 3.14.6 without pytest. The root leader supplies the repository worktree as `workdir`; no `cd ... && ...` command string is needed.
- External process transport is list-form argv with `shell=False`. Prompts and hostile literals travel through a UTF-8 prompt file or a typed argument, never shell interpolation.
- Registering a random temporary pathname before a mutating syscall does not prove ownership. Cleanup may destructively remove only a descriptor- or device/inode-attested private entry; a create call interrupted before returning ownership evidence leaves a loud path-specific `state-preserved`/`cleanup incomplete` result. A stably observed foreign live destination always takes precedence over ambiguous source state and is never snapshot-restored.
- `<review-record>/packet/` is immutable after sealing. Exports, receipts, verdicts, provenance, and resolution records are sibling subtrees of `<review-record>`.
- Every raw external path is absolute, checks all existing components for symlinks before resolution, and is then proved canonically contained below its allowed root.
- A coverage ledger is required before review dispatch. It contains affected unchanged callers, callees, imports, tests, build configuration, and public contracts, plus explicit unresolved edges.
- Native Codex review/repair uses direct `spawn_agent` with `fork_turns="none"` and explicit current leader-selected `model` and `reasoning_effort`. The shipped skill does not pin an aging identifier or replace model selection with a Custom Agent.
- Actual child model/effort is recorded only when exposed by runtime metadata; otherwise it is the literal `unexposed`.
- Claude capacity remains unavailable until the owner says otherwise. The final skill/prompt quality gate is therefore labeled `interim-four-leg` and uses two independent exact Gemini Pro High legs plus two independent fresh Codex legs on identical frozen bytes. It is not represented as a formal three-family review.
- The final gate runs deterministic `skill-prompt-review` lint on every changed skill, reference, and authored dispatch prompt, then fresh semantic reviews and clean/planted-defect behavior controls. Findings are reconciled by evidence, not votes.

## Timeout accounting and progress checks

- Static analysis/build/test time and LLM review time are separate measurements. A static command gets a deterministic hang guard sized to that command; it never donates or removes time from an LLM leg.
- LLM dispatch timeout is chosen from the selected route/model, reasoning effort, frozen input bytes, and requested review depth. Higher reasoning, a more capable/slower model, or a larger affected-code archive increases the allowance; the shipped workflow must not reuse a fixed ten-minute static-analysis limit for every LLM call.
- Native subagent waits are event-driven. A `wait_agent` timeout is only a leader wake-up boundary, not failure evidence. The leader may request an intermediate checkpoint or inspect agent status when useful, and does not interrupt or respawn a healthy agent merely because one wait boundary elapsed.
- External provider legs record the configured timeout, elapsed time, last observable progress/classification, and whether a bounded follow-up or rerun was requested. A timeout is terminal only when the provider process actually reaches its configured deadline and the wrapper classifies it as such.
- Long-running reviewers may be asked for a compact progress checkpoint (current phase, files inspected, blocker, remaining work) without changing their review scope or contaminating independent conclusions.

## Platform contract

- Shipped runtime, bootstrap, packet, repair, and skill artifacts support both Ubuntu 24.04 and current macOS. Portable implementation paths use Python 3.12 standard-library and POSIX-common behavior available on both; macOS-only `chflags`, Linux-only `renameat2`/`/proc`, descriptor execution/link tricks, and shell features newer than Bash 3.2 are forbidden in shared runtime paths.
- Deterministic suites run on both platforms before each task that changes shared runtime, bootstrap, packet, repair, or skill behavior may commit or advance, and again before final integration. The macOS lane uses the owner's actual terminal Python. The Ubuntu 24.04 lane uses an exact digest-pinned container or CI image, records the image digest, Python/Bash/test-runner versions, exact commands, and results, and runs the same hermetic suites. Platform-specific skips require an evidence-backed documented reason and may not cover a core safety contract.

## Task Gate

For each task:

1. record the intended red test and run it;
2. implement the smallest contract with `apply_patch`;
3. rerun the focused green test outside the filesystem sandbox;
4. inspect full affected files and downstream callers, not only the diff;
5. for shared runtime, bootstrap, packet, repair, or skill changes, run and record the identical hermetic suite on the macOS lane and the digest-pinned Ubuntu 24.04 lane with no core-contract skip;
6. commit only the task-owned coherent slice;
7. run a fresh task review before advancing.

The pre-existing baseline contains one stale optional-Gemini expectation and one second-bootstrap-run hang. Delivery 1 owns both; no later task may classify them as an accepted baseline failure.
