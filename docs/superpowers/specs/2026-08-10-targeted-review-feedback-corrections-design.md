# Targeted 0.2.533 Review Feedback Corrections Design

Date: 2026-08-10

Status: owner-approved design; implementation not started

## Context

The claude-host maintainer supplied five actionable cross-family review claims
against the 0.2.533 review-lifecycle overhaul and one informational upstream
adoption note. The external merge commit `c769a10` and the workspace commit
`c68c6da` resolve to the same Git tree, `7683d2e3b64f4068509a582dbfac86be7f8a0787`,
so the workspace checkout contains the exact reviewed bytes.

Every claim was checked against those bytes before selecting a correction. The
approved response keeps the compact binary verdict and single prepared-directory
boundary. It does not add another path root, a new severity, a context flag, a
permission control, or a truncation detector.

## Goal

Correct the benchmark's evidence-strength claim and make the existing reviewer
result, packet-boundary, and containment semantics explicit without changing the
approved review architecture.

## Global constraints

- Preserve the owner-approved focused prepared-directory lifecycle and strict
  `LegVerdict` shape.
- Keep provider-native tools, installed CLI tools, configured MCP tools, and
  approved read/search capabilities available.
- Do not change provider permissions, model selection, user settings, or global
  configuration.
- Do not add `context_known`, `Suggestion`, `HARDENING-SUGGESTION`, a second path
  root, membership validation, a sandbox, or a network monitor.
- Treat the prior r4/release proof as historical after any changed candidate
  byte. Do not package, install, tag, publish, merge, or claim current release
  readiness from stale evidence.
- Implement and gate the four behavioral claims independently. Do not combine
  the two rendered-prompt behavior changes into one merge-gate unit.

## Review adjudication

### Benchmark methodology

Accepted with a precision correction. Commit `4f4f5e0` changed the local-defect
expected IDs from `LOCAL-1` to `LOCAL-1, LOCAL-2` after reviewer output and
before commit `33dd517` recorded the aggregate. The original preregistered set
was detected 3/3, while the checked-in 4/4 and zero-false-finding aggregate use
amended ground truth. Calls per round and batch-artifact counts are unaffected.

### Verdict expressiveness

Partially accepted. The schema has no context flag or suggestion severity, but
it expressly accepts `SAFE` with `Minor` findings. It also carries unresolved
uncertainty in `open_questions`, which deliberately requires `NOT-SAFE`. The
defect is an undocumented meaning convention, not the absence of every legal
carrier.

### Finding path domain

Partially accepted. Absolute, traversal, and non-normalized paths are invalid,
but the schema does not validate packet membership; a normalized nonexistent
relative path is structurally valid. The semantic inspection contract still
forbids reading or claiming evidence outside the prepared directory. The defect
is the missing convention for reporting a suspected omitted surface.

### Containment wording

Accepted. The prepared digest and canonical-worktree fingerprint monitor two
surfaces. They do not prevent or detect mutation elsewhere or network egress,
and a parallel packet mutation is detected only by final verification. The
round invalidates and all verdicts are discarded, but tampered reads are not
prevented.

### Truncated-answer retirement

Rejected for the current runtime. A schema-free AGY 1.1.11 `stream-json` probe
returned one 33,957-character terminal response without a truncation marker or
`truncated_fields`. The response did not obey the requested exact character
count, but its length is sufficient to disprove the claimed current 4 KiB
terminal-response fold. The free-prose path remains supported, while the
`truncated-answer` exit-map entry remains an inert compatibility alias.

## Slice 1: Benchmark provenance caveat

### Behavioral claim

The checked-in benchmark distinguishes independently preregistered recall from
the post-hoc ground-truth amendment without weakening the unaffected runtime
efficiency evidence.

### Changes

- Add one explicit methodology-caveat field to
  `benchmarks/review-policy/focused-convergent-runtime.json`.
- Amend the 0.2.533 `CHANGELOG.md` entry to say that 3/3 defects were
  preregistered and `LOCAL-2` was added after reviewer output; the 4/4 and
  zero-false-finding aggregate is post-hoc.
- Apply the same qualification to
  `docs/status/2026-08-05-focused-convergent-runtime-benchmark.md`.
- Add a regression assertion that the machine-readable runtime evidence carries
  the caveat.

Do not change `cases.json`, rerun providers, invent a fresh fixture, or alter the
recorded call and artifact counts.

### Slice budget

- Production net delta: 0 lines.
- Novel algorithmic core: 0 lines.
- Behavioral claims: 1.
- Class: S; no L-class exception.

## Slice 2: Suggestion and unresolved-context convention

### Behavioral claim

A reviewer can report a non-blocking hardening suggestion without representing
uncertain current correctness as `SAFE`.

### Semantics

- A `Minor` finding may carry a non-blocking hardening suggestion only when
  packet evidence establishes that current behavior is correct and rules out
  the suggestion's scenario for the current decision.
- Its trigger and evidence must state why the observation is non-blocking for
  the current packet; it must not disguise a current defect as optional work.
- Missing deployment or operational context needed to decide current
  correctness goes into `open_questions` and therefore requires `NOT-SAFE`.
- A reviewer must not suppress genuine uncertainty merely to produce `SAFE`.

### Changes

- Add the convention to
  `skills/triad-cross-family-review/references/review-prompt-contract.md`.
- Add the same operative instruction to the prompt rendered by
  `bin/review_round.py`; editing the reference alone would not change provider
  behavior.
- Add a focused rendered-prompt regression test.

Do not change `bin/verdict_schema.py` or add a new severity or field.

### Slice budget

- Production net delta: approximately 8-15 lines in the rendered prompt.
- Novel algorithmic core: 0 lines.
- Behavioral claims: 1.
- Class: S; no L-class exception.

## Slice 3: Suspected out-of-packet surface convention

### Behavioral claim

A reviewer reports a potentially relevant surface omitted from the prepared
directory as an unresolved question instead of silently dropping it or claiming
uninspected evidence.

### Semantics

- Do not cite an uninspected out-of-packet file as a finding or list it in
  `affected_surfaces_inspected`.
- Put the suspected normalized worktree-relative path and the required check in
  `open_questions`; the leg therefore returns `NOT-SAFE`.
- The leader reproduces the claim against the canonical worktree. If relevant,
  the leader prepares a new complete directory that includes the surface and
  restarts every required family under a fresh review ID.

### Changes

- Add the convention to
  `skills/triad-cross-family-review/references/review-prompt-contract.md`.
- Add the same operative instruction to the prompt rendered by
  `bin/review_round.py`.
- Add a separate focused rendered-prompt regression test.

Do not add a second review root, a path-prefix protocol, or packet-membership
validation to the result schema.

### Slice budget

- Production net delta: approximately 5-10 lines in the rendered prompt.
- Novel algorithmic core: 0 lines.
- Behavioral claims: 1.
- Class: S; no L-class exception.

## Slice 4: Containment disclosure

### Behavioral claim

The leg contract describes mutation verification as a compensating detection
control with exact monitored and unmonitored surfaces, not as preventive
containment.

### Changes

Extend the final containment paragraph in
`skills/triad-cross-family-review/references/leg-contracts.md` to state:

- reviewer legs retain native tools and prompt-controlled restrictions;
- prepared-directory digest and canonical-worktree fingerprint monitor exactly
  those two surfaces;
- mutation elsewhere and network egress are neither prevented nor detected by
  those fingerprints;
- a mutation of the shared prepared directory during parallel review may affect
  another leg's reads before final verification; and
- a mismatch invalidates the complete round and discards every verdict rather
  than retroactively preventing the mutation.

Add a distribution/reference-contract assertion for the disclosure. Do not
change tool availability, permissions, execution profiles, digest inputs, or
verification timing.

### Slice budget

- Production net delta: 0 lines.
- Novel algorithmic core: 0 lines.
- Behavioral claims: 1.
- Class: S; no L-class exception.

## Verification strategy

Each slice receives its own red/green test cycle where behavior is executable.
Documentation-only assertions must fail against the prior bytes before the text
is changed. After every slice:

1. run the narrow affected tests;
2. run the relevant distribution-contract tests;
3. run `git diff --check`;
4. keep later slices out of the candidate until the current slice is admitted;
5. use fresh review identity and evidence for any required formal gate.

After all four independently admitted slices are present together, run the full
repository verification required by the project before any completion claim.
Any package, installed-skill, or release claim requires newly generated evidence
for the final bytes.

## Non-goals

- Rebenchmarking with new providers or fixtures.
- Recording new suggestion/open-question telemetry.
- Changing binary verdict gating semantics.
- Generalizing review paths beyond one prepared directory.
- Adding preventive sandboxing or network controls.
- Restoring legacy AGY output-marker classification.
- Packaging, installing, publishing, merging, or releasing as part of these
  corrections.
