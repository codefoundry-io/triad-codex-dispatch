# Focused Convergent Runtime Benchmark

Date: 2026-08-05

## Outcome

The reviewer-only focused policy converged in two complete rounds with six
provider calls. The defect round returned three admissible `NOT-SAFE` verdicts.
After bounded fixture corrections, the confirmation round returned three
admissible `SAFE` verdicts for one new digest.

Both rounds passed prepared-directory and worktree integrity verification.
All six terminal results passed schema, review ID, family, and digest binding.
No reviewer mutation was admitted.

## Comparison

| Metric | Captured batched policy | Focused convergent policy |
|---|---:|---:|
| Calls per round | 24 planned | 3 actual |
| Calls across two rounds | 48 projected | 6 actual |
| Call reduction | - | 87.5% |
| Batch artifacts | 465 | 0 |
| Prompt bytes across two rounds | 373,268 projected | 9,408 actual |
| Prompt-byte reduction | - | 97.48% |
| Adjudicated planted-defect recall | unavailable | 4/4 |
| Clean-control false findings | unavailable | 0 |
| Confirmation verdicts | round did not finish | 3/3 `SAFE` |

The batched figures are a captured planned round, not a completed quality
result. The focused figures are observed runtime results. Fresh Codex elapsed
time and normalized provider token usage were not exposed by the result
contract, so they are not estimated.

## Routes

- Claude: `opus`, `xhigh`, one native `--json-schema` call per round.
- Google: AGY 1.1.10, `gemini-3.1-pro-high`, `high`, native `stream-json` and
  `json-schema`, one call per round.
- Codex: fresh default child, requested `gpt-5.6-terra`, `xhigh`,
  `fork_turns = "none"`; actual runtime identity was unexposed.

The first pre-fix calibration attempt is excluded from steady-state metrics.
It consumed four provider calls because the old Claude wrapper made a schema
repair call, and the round was invalid due to malformed results and a changed
worktree fingerprint. That failure directly motivated the single-call native
schema transport and exact result-shape prompt.

## Convergence evidence

- `benchmark-r1b`, digest
  `6cc042980940aa1e5adbf901f67fc004e255f993f8d982bc57f91aed80feb021`:
  three `NOT-SAFE`, all four reproduced findings detected, integrity OK.
- `benchmark-r2`, digest
  `f0069c48a10c17abe116af2d533868670c178b053119a9dd91b3499d3d09221e`:
  three `SAFE`, no findings or open questions, integrity OK.

Machine-readable inputs and aggregate output are
`benchmarks/review-policy/focused-convergent-runtime.json` and
`benchmarks/review-policy/focused-convergent-report.json`.
