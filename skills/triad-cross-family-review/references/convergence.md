# Finding convergence and round recovery

This file is the single normative contract for finding classification,
zero-start failure, partial-start failure, reruns, and owner decisions. Other
TRIAD instructions link here instead of restating these rules.

## Finding classification

The leader reproduces every finding against the exact reviewed bytes and the
canonical worktree. Reviewer labels are claims, not repair instructions.

| Reproduced state | Action |
|---|---|
| Defect or underspecification inside approved design | Apply the smallest bounded correction, run project verification, and start a fresh complete round |
| Contradicted by reviewed source | Record the refutation and preserve the source unchanged |
| Design/specification change | `OWNER_DECISION_REQUIRED` |
| Generalization, new capability, or scope expansion | `OWNER_DECISION_REQUIRED` |
| Contradictory verified findings | `CONFLICTED`; owner adjudication |
| Alternating advice without changed candidate/evidence | `OSCILLATING`; stop unchanged redispatch and ask the owner |

When owner input is required, report:

```text
Proposed delta: <what would change beyond the approved design>
Evidence: <reproduced file:line or runtime evidence>
Impact: <behavior, compatibility, cost, or scope consequence>
Decision needed: <one concrete owner choice>
```

Preserve the affected source while awaiting that decision. Continue unrelated
bounded work only when it cannot pre-decide or conflict with the owner's choice.

## Failure before any provider starts

A packet, selector, preflight, or launch-setup defect with zero started provider
legs invalidates the attempt. Record the exact non-secret failure evidence, use
supported cleanup for an exact managed root when one exists, correct the defect
or verify recovery from a transient vendor incident, and restart with a fresh
review ID.

After a second comparable zero-provider failure, stop allocating review IDs.
Compare the retained receipts and command context, identify and verify the shared
cause, then run one controlled setup-only probe. A changed command without cause
evidence is not recovery, and the probe is not a formal review round.

## Failure after a provider starts

<!-- PARTIAL_START_CONTRACT_START -->
The partial-start contract applies once any provider leg has started. A later leg
start or result failure that is missing, refused, malformed, route-mismatched, or
incomplete invalidates admission. Close further launch, record each required leg
that did not start, and wait for every already-started sibling to terminate.
Strictly validate every structurally available terminal result and confirm the
exact provider process trees are gone; run integrity verification only after every
started leg terminates.

Structurally valid results remain provisional until post-review integrity succeeds.
After a matching integrity check, preserve and reproduce every valid sibling
finding as advisory only while classifying the failure as a workflow, skill, tool,
instruction, operator, or vendor problem. A valid `NOT-SAFE` result is not a
failed leg and receives the same complete sibling collection. No sibling result
admits the failed round or supplies admission credit to a later round.

If integrity fails, use outputs only as untrusted leads and independently
reproduce any claim; diagnose and correct the integrity mismatch before a fresh
round. In either case, reproduce every collected finding before the next round,
correct and verify every reproduced in-scope defect, and correct the classified
leg failure or verify recovery from a transient vendor incident. A finding that
expands design still requires owner approval. Clean the exact round, prepare a
fresh ID, and rerun all three required families over one current basis.
<!-- PARTIAL_START_CONTRACT_END -->

## Convergence

A bounded fix, owner-approved design decision, corrected route, or material new
evidence creates a new review basis and requires a fresh complete round. There is
no fixed round cap. Stop on unanimous admissible `SAFE`, an owner decision,
`CONFLICTED`, `OSCILLATING`, or a required-leg failure that cannot be corrected
without new authority or external-state change.

The convergence unit is one complete focused source view reviewed once by each
required family. It is never divided into batches or satisfied by receipts from
different rounds.
