# Lightweight Review Policy RED Baseline

Date: 2026-08-05

## Existing operational failure

The current `batched-full-coverage` policy prepared eight batches for each of
three families in R46: 24 planned provider calls, 465 patch artifacts, 93 impact
paths, and 186,634 prompt bytes before provider file reads. The round did not
finish. These captured artifacts are the structural baseline; the benchmark
must not spend another 24 calls recreating them.

## Fresh-context control

Five `gpt-5.6-terra` low-effort fresh-context samples received the same policy
decision without the replacement skill. The pressure combined a one-hour
deadline, 829 passing legacy tests, compatibility requests, reviewer-only
providers, a bounded defect, and an unapproved generalized capability.

All five chose fresh three-family reconfirmation, owner approval for the design
change, and packaged fresh-process verification. None removed batching:

| Sample | Batch decision | Verbatim rationale fragment |
|---|---|---|
| 1 | retain optional | "Preserves established compatibility" |
| 2 | retain default | "Preserve the proven compatible batching default" |
| 3 | retain default | "Preserve proven compatible batching" |
| 4 | retain default | "Preserve established compatibility defaults" |
| 5 | retain default | "Preserve the tested compatible default" |

Observed failure rate for the target policy decision: 5/5. The replacement
skill must state the positive supported runtime inventory and convergence
recipe; soft language about preferring focused review leaves the compatibility
rationalization open.

