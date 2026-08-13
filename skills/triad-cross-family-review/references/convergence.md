# Finding convergence and owner decisions

The leader reproduces every finding against the exact reviewed bytes and the
canonical worktree. Reviewer labels are claims, not repair instructions.

## Classification

| Reproduced state | Action |
|---|---|
| Defect or underspecification inside approved design | Smallest bounded correction, project verification, fresh complete round |
| Contradicted by reviewed source | Record refutation; no edit |
| Design/specification change | `OWNER_DECISION_REQUIRED` |
| Generalization, new capability, or scope expansion | `OWNER_DECISION_REQUIRED` |
| Contradictory verified findings | `CONFLICTED`; owner adjudication |
| Alternating advice without changed candidate/evidence | `OSCILLATING`; stop unchanged redispatch and ask owner |

## Owner question

When owner input is required, report these four slots:

```text
Proposed delta: <what would change beyond the approved design>
Evidence: <reproduced file:line or runtime evidence>
Impact: <behavior, compatibility, cost, or scope consequence>
Decision needed: <one concrete owner choice>
```

Do not implement the proposed delta while asking. Continue unrelated bounded
work only when it cannot pre-decide or conflict with the owner's choice.

## Round loop

One round ends after all three legs terminate and integrity is verified. A
bounded fix, owner-approved design decision, corrected route, or material new
evidence creates a new review basis and permits a fresh complete round.
At the first required-leg failure, terminate every still-running leg and its
exact provider process group, discard every current-round verdict, and never
continue a sibling merely to collect advisory evidence. Confirm termination,
verify integrity, clean the exact round, and repair the defect before a fresh ID.

There is no fixed maximum round count. Stop only on unanimous admissible
`SAFE`, an owner decision, `CONFLICTED`, `OSCILLATING`, or an invalid required
leg that cannot be corrected without new authority or external-state change.

Do not split a round into batches or preserve batch receipts for compatibility.
The convergence unit is one complete focused directory reviewed once by each
required family.
