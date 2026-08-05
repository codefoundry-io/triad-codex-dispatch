# Focused Formal Review and AGY Stream-JSON Design

**Date:** 2026-08-05  
**Status:** Proposed for owner review  
**Repository:** `triad-codex-dispatch-reliability`

## Goal

Make the normal TRIAD formal review path small enough to use routinely while
preserving the controls required for a valid three-family gate.

The default formal round will make exactly one Claude call, one Google-family
call, and one fresh-context Codex call over one leader-prepared directory. The
existing family-by-batch receipt matrix remains available only as an explicit
full-audit profile.

At the same time, replace the Google wrapper's PTY, completion-sentinel, and
shared-transcript extraction path with AGY 1.1.10's native stream-JSON output
and JSON-schema request surface. The formal Google selector remains the
live-verified `gemini-3.1-pro-high` slug with no separate effort flag.

## Owner-approved decisions

1. `formal-gate` becomes the operational default for formal plan and
   pre-merge review.
2. A default formal round has three provider calls total: one per family.
3. `batched-full-coverage` remains available as an explicit `full-audit`
   choice. TRIAD never escalates to it automatically.
4. The leader selects an exact decision-relevant evidence boundary. The
   prepared directory contains complete current files for that boundary,
   governing documentation, and one canonical readable diff file.
5. Every family receives the same prepared directory, task, boundary, and
   digest. No prompt contains an inline diff or file body.
6. A compact structured leg result replaces per-path and per-hunk receipts in
   the default profile.
7. Prepared-directory digest and canonical-worktree fingerprint checks remain
   mandatory before and after dispatch.
8. Provider findings remain advisory claims. The root leader reproduces and
   classifies each finding before any edit.
9. The Claude-led checkout outside `codex_workspace` is a read-only reference,
   not an implementation target.
10. AGY behavior from versions before 1.1.10 is not copied into this design.

## Non-goals

- Removing the current full-audit evidence, batch, receipt, or admission code.
- Claiming that a focused formal gate proves every tracked repository path was
  read by every provider.
- Inferring test-source exclusions or expanding the owner-approved data
  boundary.
- Changing provider authentication, Codex approval policy, sandbox policy, or
  native permission inheritance.
- Modifying `/Users/chaniri/triad-dispatch` or any other checkout outside
  `/Users/chaniri/codex_workspace`.
- Publishing, pushing, tagging, or releasing the result.

## Default evidence model

The leader prepares one immutable review directory containing only the current
source, configuration, tests when applicable, and documentation needed to
decide the stated question. Selection is semantic and exact; it is not a sample
of a larger declared scope.

The directory also contains:

- one task file stating the review kind, objective, acceptance criteria, and
  exact approved data boundary;
- one canonical diff file, generated from the recorded base and candidate
  state for the changed paths inside that boundary, used as the navigation
  entry point;
- the compact leg-result JSON schema; and
- candidate metadata recording the base identity, candidate identity, diff
  digest, and worktree fingerprint.

Formal plan and pre-merge review excludes test source only when project
instructions or the owner provide exact test roots. Normal implementation
review includes relevant test source. The implementation must not infer or
broaden either boundary.

The existing `review_evidence.py` and `review_coverage.py` machinery is not run
for the default profile. It remains the implementation of explicit full-audit
mode. This prevents the default path from materializing per-hunk shards,
provider batch manifests, or a family-by-batch receipt matrix.

## Compact result contract

Add a strict `FocusedFormalReview` model beside the existing legacy
`FormalReview` model. The existing sealed-packet model and validator remain
unchanged for compatibility.

`FocusedFormalReview` contains:

- `review_id`
- `family`: `claude`, `google`, or `codex`
- `content_digest`: the leader-supplied prepared-directory digest
- `verdict`: `SAFE` or `NOT-SAFE`
- `criteria_checked`: a non-empty list of the substantive criteria evaluated
- `findings`: structured findings using the existing severity, location,
  trigger, evidence, and correction-direction fields
- `affected_surfaces_inspected`: the prepared-directory-relative paths that
  materially informed the result
- `open_questions`

Unknown fields are rejected. `SAFE` is valid only when there is no Critical or
Major finding and no open question. Minor findings may accompany `SAFE`.
`NOT-SAFE` requires at least one Critical/Major finding or open question.

Each external wrapper validates the result locally against this model. The
fresh Codex leg returns the same JSON object, and the leader validates it with
the repository validator before admitting the leg. A positive summary or
provider disclaimer that omits the exact contract is not a verdict.

The surface list is review transparency, not machine proof of exhaustive file
reads. The focused profile claims complete evaluation of the leader-selected
decision boundary, not the old per-family assigned-path coverage guarantee.

## Dispatch flow

1. The leader states the review decision and exact evidence boundary.
2. The leader prepares the shared directory with complete current files and
   one canonical diff.
3. The leader records the prepared-directory content digest and current
   worktree fingerprint.
4. The leader starts all three legs before consuming a verdict:
   - Claude through the installed Claude wrapper;
   - Google through the AGY 1.1.10 wrapper with
     `--model gemini-3.1-pro-high` and no `--effort`;
   - a fresh default Codex child with the workspace-native spawn contract.
5. Each leg performs read-only, non-executing inspection and returns one
   `FocusedFormalReview` object.
6. The leader validates all three objects, including review ID, family, and
   content digest.
7. After all required legs terminate, the leader recomputes the directory
   digest and worktree fingerprint. Any mutation invalidates the round.
8. The leader reproduces each finding against the canonical worktree and
   classifies it as a bounded defect/underspecification or an owner-decision
   design change.
9. The gate passes only when all three admitted verdicts are `SAFE` and no
   reproduced contradiction remains.

There is no automatic batching fallback. If one focused packet demonstrably
exceeds a provider limit, the leader reports that evidence and obtains an owner
decision before selecting a smaller boundary or explicit full-audit mode.

## AGY 1.1.10 transport

The Google wrapper invokes AGY non-interactively with native stream output:

```text
agy -p <prompt> --output-format stream-json --json-schema <schema> \
  --model gemini-3.1-pro-high
```

The exact ordering may follow the CLI's accepted syntax. The behavioral
contract is:

- require AGY 1.1.10 or newer;
- preserve the formal selector `gemini-3.1-pro-high`;
- omit a separate effort flag for the formal route;
- do not inject sandbox or permission-bypass arguments;
- parse only events from the current child process stdout;
- accept only the terminal result event for the current request;
- validate the returned object locally even when AGY reports schema success;
- preserve existing timeout, capacity, authorization, and provider-failure
  classifications; and
- allow at most the existing single schema-repair attempt when local
  validation fails.

Once the new path passes regression and live tests, remove the obsolete PTY
driver, completion-sentinel sealing, shared transcript discovery, and
sentinel-based transcript admission from `antigravity_wrapper.py`. Do not copy
the reference checkout's older model-selection or minimum-version policy.

## Explicit full-audit profile

`batched-full-coverage` remains a supported compatibility name and is
documented as explicit `full-audit`. It keeps the existing deterministic impact
closure, patch shards, batch manifests, strict `BatchReceipt` results,
family-complete retry, residual ledger, and `review_coverage.py` admission.

The default skill must not select full-audit because a diff is large, because
zero findings seem suspicious, or because complete-read proof would be nice to
have. It is selected only by an explicit owner request or a separately approved
project gate that names the full-audit profile.

## Failure and invalidation rules

- A missing, refused, malformed, route-mismatched, or semantically incomplete
  required leg invalidates the formal round.
- Provider policy prose is not a verdict.
- A digest or worktree-fingerprint mismatch invalidates the round.
- A provider mutation invalidates its leg; a prepared-directory mutation
  invalidates the whole round.
- A runtime identity conflict with the requested Google route invalidates the
  Google leg. Unexposed identity is recorded as unexposed, not fabricated.
- A corrected candidate, changed boundary, changed digest, or invalid required
  leg requires a fresh review ID and a complete three-leg rerun.
- Findings do not authorize generalized capabilities or design expansion.

## Implementation boundaries

The production change is intentionally narrow:

- extend `bin/triad_formal_review_schema.py` with the focused result model and a
  focused-result file-validation CLI path while preserving the legacy path;
- replace the AGY PTY/transcript transport in `bin/antigravity_wrapper.py` with
  AGY 1.1.10 stream-JSON and native JSON-schema handling;
- make `formal-gate` the default operational profile in
  `skills/triad-cross-family-review/` and provider dispatch references;
- retain and clearly label `batched-full-coverage` as explicit full-audit;
- update distribution copies, bootstrap contracts, and English documentation;
  and
- add focused unit, hostile-input, distribution-contract, skill-pressure, and
  live wrapper tests.

No new generic orchestration framework, custom review agent, provider daemon,
or repository-wide source archive is introduced.

## Verification and acceptance

Implementation is accepted when all of the following are demonstrated:

1. A default formal prompt produces exactly one dispatch per family and does
   not create batch manifests or per-path receipts.
2. All three result routes enforce `FocusedFormalReview`, including digest and
   verdict semantics.
3. Explicit full-audit still passes its existing unit and admission tests.
4. AGY 1.1.10 stream-JSON success, malformed-event, timeout, authorization,
   capacity, schema-failure, and single-repair cases are covered.
5. A live Google smoke proves `gemini-3.1-pro-high` without `--effort` and
   returns an admitted structured result.
6. The full repository test suite, shell syntax checks, distribution contract,
   and diff checks pass.
7. The plugin is exported and installed from the workspace-owned source, and a
   fresh Codex session proves the updated review skill is exposed.
8. No file outside `/Users/chaniri/codex_workspace` is modified.
