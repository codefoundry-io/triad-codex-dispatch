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

- All direct Python, test, lint, and bootstrap verification commands run in the user's normal macOS login-terminal environment, outside the filesystem sandbox. Record `command -v python3`, `python3 --version`, and `python3 -m pytest --version`, then use literal `python3`. The root leader supplies the repository worktree as `workdir`; no `cd ... && ...` command string is needed.
- External process transport is list-form argv with `shell=False`. Prompts and hostile literals travel through a UTF-8 prompt file or a typed argument, never shell interpolation.
- `<review-record>/packet/` is immutable after sealing. Exports, receipts, verdicts, provenance, and resolution records are sibling subtrees of `<review-record>`.
- Every raw external path is absolute, checks all existing components for symlinks before resolution, and is then proved canonically contained below its allowed root.
- A coverage ledger is required before review dispatch. It contains affected unchanged callers, callees, imports, tests, build configuration, and public contracts, plus explicit unresolved edges.
- Native Codex review/repair uses direct `spawn_agent` with `fork_turns="none"` and explicit current leader-selected `model` and `reasoning_effort`. The shipped skill does not pin an aging identifier or replace model selection with a Custom Agent.
- Actual child model/effort is recorded only when exposed by runtime metadata; otherwise it is the literal `unexposed`.
- Claude capacity remains unavailable until the owner says otherwise. The final skill/prompt quality gate is therefore labeled `interim-four-leg` and uses two independent exact Gemini Pro High legs plus two independent fresh Codex legs on identical frozen bytes. It is not represented as a formal three-family review.
- The final gate runs deterministic `skill-prompt-review` lint on every changed skill, reference, and authored dispatch prompt, then fresh semantic reviews and clean/planted-defect behavior controls. Findings are reconciled by evidence, not votes.

## Task Gate

For each task:

1. record the intended red test and run it;
2. implement the smallest contract with `apply_patch`;
3. rerun the focused green test outside the filesystem sandbox;
4. inspect full affected files and downstream callers, not only the diff;
5. commit only the task-owned coherent slice;
6. run a fresh task review before advancing.

The pre-existing baseline contains one stale optional-Gemini expectation and one second-bootstrap-run hang. Delivery 1 owns both; no later task may classify them as an accepted baseline failure.
