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

One round ends after every started leg terminates and integrity is verified. For a partial start, record the actual start failure and each remaining unstarted required leg as not started because launch was closed. A
bounded fix, owner-approved design decision, corrected route, or material new
evidence creates a new review basis and permits a fresh complete round.
After dispatch begins, once any provider leg has started, a later leg start or result failure invalidates admission but does
not cancel sibling execution; do not launch a not-yet-started leg after the failure; wait for every already-started sibling to terminate,
strictly validate every terminal result that is structurally available, and confirm that every exact
provider process tree is gone before integrity verification; run it only after every started leg terminates. Structurally valid results remain
provisional until post-review integrity succeeds. After a matching integrity check, preserve and
reproduce every valid sibling finding as advisory only while classifying the failure as a workflow,
skill, tool, instruction, operator, or vendor problem. A valid `NOT-SAFE` result is not a failed leg
and receives the same complete sibling collection. Valid sibling results never admit the failed
round or supply admission credit to a later round. If integrity fails, treat outputs only as
untrusted leads and independently reproduce any claim before use; diagnose and correct the integrity mismatch before a fresh round. Before preparing a fresh round,
reproduce every collected finding before the next round; correct and verify every reproduced
in-scope defect, and correct the classified leg failure or verify recovery from a transient vendor
incident. A finding that requires a design expansion still stops for owner approval. Clean the exact
round, prepare a fresh ID, and rerun a complete three-family round.

There is no fixed maximum round count. Stop only on unanimous admissible
`SAFE`, an owner decision, `CONFLICTED`, `OSCILLATING`, or an invalid required
leg that cannot be corrected without new authority or external-state change.

Do not split a round into batches or preserve batch receipts for compatibility.
The convergence unit is one complete focused directory reviewed once by each
required family.
