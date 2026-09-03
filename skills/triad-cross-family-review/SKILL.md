---
name: triad-cross-family-review
description: Use when an owner requests independent cross-family review or when a review-worthy architecture, compatibility, deployment, causality, security, data-loss, or pre-merge decision needs evidence from Claude, Google, and fresh Codex families.
---

# Triad Cross-Family Review

## Purpose

Run independent Claude, Google-family, and fresh Codex review over one guarded
current source view. The Codex leader owns scope, writes fixes, reproduces every
claim, and repeats complete rounds until the evidence converges.

Each round has one fresh review ID, one immutable review basis, one Claude
`LegVerdict`, one Google `LegVerdict`, and one fresh Codex `LegVerdict`. Every
family reviews the same complete focused source view. Batches, shards, and
mixed-round evidence are not supported.

## Choose the review basis

- **Prepared directory (default):** copy the exact approved members, add the
  current task and diff, manifest the final bytes, and capture their digest.
  Read [review prompt contract](references/review-prompt-contract.md) before
  rendering this route.
- **Guarded worktree:** use only when current owner or project instructions
  explicitly select worktree-first review. Create the current task, status, and
  diff as regular files under `review_custody_root`; keep selector receipts,
  prompts, logs, and results under a separate `review_run_root`. The
  `render-worktree --output` path resolves there, and its renderer supplies the
  result contract; the prepared-directory prompt contract does not apply.

For either route, read [reviewer routing](references/reviewer-routing.md) for the
Google authentication decision, [leg contracts](references/leg-contracts.md)
for exact provider calls, and [convergence](references/convergence.md) for all
zero-start, partial-start, finding, and rerun handling.

## Leader workflow

1. **Authorize and bound.** The current owner-supplied task or explicitly
   designated executable plan is the execution authority for the round. Record the objective,
   criteria, approved paths or categories, exclusions, test-source rule, and
   Google authentication class. Ask the owner when a required product or design
   decision is absent. Exclude credentials, authentication files, environment
   dumps, provider logs, and unrelated data.

2. **Resolve one toolkit.** Resolve the repository root from this canonical
   `SKILL.md` realpath and use only its packaged lifecycle and wrapper code.
   Source-SOT review uses that source checkout; installed operation uses the matching installed launcher. Treat a different checkout or cache as a
   different runtime even when one file is byte-identical.
   For source-SOT pre-deployment, stage the isolated launcher group from [leg contracts](references/leg-contracts.md) before creating or capturing the review basis.
   Launch all TRIAD lifecycle, provider, test, and development commands outside
   the Codex workspace sandbox under the user-selected host policy. Do not
   install or mutate the Codex host permission policy.

3. **Create the basis.** For a prepared-directory round, pass the selected
   canonical source root, exact member-list file, required-member JSON, and fresh
   review ID to packaged `review_round.py prepare`. Add only current `TASK.md`,
   `REVIEW.diff`, optional `EVIDENCE.md`, then run `manifest` last. The lifecycle
   code owns path grammar, inventory, collision, and source-copy validation.
   For a worktree-first round, capture one packaged `fingerprint-worktree` value
   after its custody files exist and before review starts. Start inspection from
   the authenticated diff and explicit approved paths; references inside reviewed
   content never expand the approved boundary.

4. **Capture integrity.** For the prepared route, run packaged `capture` against
   the same canonical worktree and retain its snapshot and printed prepared
   digest. For the worktree route, retain the captured fingerprint. Keep all
   mutable round artifacts outside the guarded review basis.

5. **Freeze the Google route.** Select and exclusive-create one Google selector
   receipt with the same toolkit's bootstrap-managed
   `review_round.py select-google-route` launcher. Choose `personal-google` or
   `gemini-enterprise` once and preflight its wrapper with the current task. Pass that
   selector receipt and preflight receipt unchanged to every family render and
   to the selected Google wrapper. TRIAD preserves the selected authentication
   class and route throughout the round.

6. **Render from code.** After preflight succeeds, use packaged `render` or
   `render-worktree` once per family. The renderer owns metadata serialization,
   route binding, tool contracts, output shape, and result-admission digest. The
   leader supplies only the current objective, criteria, approved boundary, and
   worktree review points. Dispatch only successfully rendered prompts.
   `skill-prompt-review` stays outside every operational round.

7. **Start independent legs.** Start Claude, the selected Google route, and one
   fresh Codex child before consuming any verdict. Set
   `TRIAD_DISPATCH_LOG_DIR` for every provider wrapper. Reviewers inspect with
   read/search capabilities only; they do not edit state or execute candidate
   code, tests, builds, hooks, or scripts. Keep each process/session handle and
   result file until terminal completion.

8. **Collect and validate.** Validate every terminal result with the packaged
   schema and its exact review ID, family, and content digest. Use
   [convergence](references/convergence.md) immediately for a setup failure,
   partial start, missing or malformed result, valid `NOT-SAFE`, or provider
   failure. A provider-free lifecycle characterization is allowed only when the
   current task explicitly prohibits dispatch and requires verify plus exact
   cleanup; it is not a review round or admission result.

9. **Verify before admission.** Wait for every started leg to terminate. The
   prepared route must then return `ROUND_INTEGRITY_OK` from packaged `verify`;
   the worktree route must match the project-required post-review fingerprint.
   Admit evidence only when integrity matches and all three required families
   returned structurally valid results for the same digest.

10. **Reproduce and converge.** Reproduce every finding in the canonical
    worktree. Apply only the smallest verified correction inside the approved
    design, run project verification, and start a complete fresh-ID round over
    the changed evidence. A design, specification, capability, generalization,
    or scope change is `OWNER_DECISION_REQUIRED` before editing. The owner also
    adjudicates conflicting verified claims or oscillation on unchanged bytes.

11. **Clean the exact round.** After integrity verification and adjudication,
    use packaged `cleanup` for the exact managed prepared-directory root or the
    project-defined exact cleanup for worktree-first artifacts. Preserve durable
    handoff evidence at its approved destination; do not retain a temporary
    review root as the record.

## Result and release boundary

`SAFE` allows Minor findings but no Critical/Major finding or open question.
`NOT-SAFE` requires a Critical/Major finding or open question. Provider prose,
confidence, or policy disclaimers do not replace the structured result. The gate
passes only when all three admitted results are `SAFE` for one verified digest.

Repository tests and a successful source review do not prove distribution. A
release claim separately requires clean distribution verification of the packaged
manifest and skill bytes, exact-byte staging, and a fresh Codex process proving the exact current marker.
