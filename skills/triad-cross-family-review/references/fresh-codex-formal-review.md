# Fresh Codex review

## Contents

- [Leader preparation](#leader-preparation)
- [Prompt contract](#prompt-contract)
- [Native spawn](#native-spawn)
- [Result admission](#result-admission)

## Leader preparation

Use one leader-prepared shared review directory containing the current approved
production source, configuration, and documentation relevant to the decision.
Every reviewer receives the same absolute directory, review task, objective,
and perspective. Prompts carry directory and task metadata while source bytes
remain in the prepared directory.

For formal plan and pre-merge review, test-source exclusions must be stated by
project instructions or the owner. Only the exact test-source roots supplied by
project instructions or the owner are physically absent from the shared
directory. Use that supplied boundary exactly. If exact roots are unavailable,
stop and return an open question; the leader asks the owner before dispatch and
never infers roots. Normal SDD implementation review includes
relevant test source; here SDD means software-development delivery. Before a formal gate,
classify every test failure as a production defect, test-case defect, or
intentional specification change and resolve or approve it.

Record one simple content digest for the prepared directory before dispatch and
compare it after all required legs terminate. A changed digest invalidates the
round. The leader chooses the digest implementation; this reference does not
define an algorithm, encoding, fixed vector, or portable format.

For an operational batched round, resolve `toolkit_root` once from the selected
local checkout or installed skill package. Generate the strict receipt schema
through the exact absolute `toolkit_root / "bin" / "review_coverage.py"`
`schema` command, prepare evidence through the exact absolute
`toolkit_root / "bin" / "review_evidence.py"` path, and run its `validate`
subcommand before dispatch. The prepared schema path is
`change-evidence/BATCH_RECEIPT.schema.json`. Keep `content_digest` for whole-
directory custody; `source_tree_digest` and `change_evidence_digest` are the
additional machine-admission bindings.

The prepared directory is read-only review evidence. Keep credentials,
authentication files, environment dumps, provider logs, and unrelated material
outside it. Reviewer operations are limited to file reads and searches; a
mutation or candidate execution invalidates the leg, and a changed digest
invalidates the round.

## Prompt contract

Read the
[shared review prompt contract](review-prompt-contract.md)
completely. The operational template selects `batched-full-coverage` after
all exact batch metadata is available. The unbatched `formal-gate` profile
remains a compatibility path with the unchanged four semantic elements.
The batched path returns one strict `BatchReceipt` per provider/batch.

The exact formal test-source boundary is required. If it is unavailable, stop
before assigning values or rendering the prompt and ask the owner.

```python
review_mode = "batched-full-coverage"
review_kind = "<formal-plan | pre-merge>"
review_target = "/absolute/path/to/prepared-review-directory"
review_objective = "<leader-controlled objective>"
reviewer_perspective = "<leader-controlled fresh-Codex perspective>"
provider = "OpenAI"
destination = "fresh native Codex child"
approved_data = "/absolute/path/to/prepared-review-directory"
excluded_data = (
    "credentials, tokens, cookies, authentication files, environment dumps, "
    "provider logs, and unrelated paths"
)
test_source_boundary = "<exact project-or-owner boundary>"
content_digest = "<leader-owned simple digest>"
source_tree_digest = "<validated source-tree digest>"
change_evidence_digest = "<validated change-evidence digest>"
batch_receipt_contract_path = "change-evidence/BATCH_RECEIPT.schema.json"
batch_id = "<exact batch ID>"
batch_manifest = "<prepared-directory-relative exact batch manifest>"
selected_result_profile = "batched-full-coverage: strict BatchReceipt JSON"

shared_prompt_values = {
    "review_mode": review_mode,
    "review_kind": review_kind,
    "review_target": review_target,
    "review_objective": review_objective,
    "reviewer_perspective": reviewer_perspective,
    "provider": provider,
    "destination": destination,
    "approved_data": approved_data,
    "excluded_data": excluded_data,
    "test_source_boundary": test_source_boundary,
    "content_digest": content_digest,
    "source_tree_digest": source_tree_digest,
    "change_evidence_digest": change_evidence_digest,
    "batch_receipt_contract_path": batch_receipt_contract_path,
    "batch_id": batch_id,
    "batch_manifest": batch_manifest,
}
```

The shared review prompt contract is the single source for the prompt envelope.
Render its envelope as `review_message` using `shared_prompt_values`, the
selected result profile, mode-specific review-depth block, and mode-specific
output constraints. This Fresh-Codex reference supplies only the values and
native-spawn transport; it does not carry a second copy of the envelope.
Preserve the canonical tail position of its inspection and output constraints.

The prompt carries the directory and task, not source bytes. The leader keeps
the before-dispatch digest and records the after-leg digest separately. A
digest mismatch invalidates the round and requires a fresh complete dispatch.

The five batched assignments above are required before rendering. The simple
`content_digest` is never the sole batched evidence binding. Use the
same native spawn contract below for every batch, and require Fresh Codex to
finish the exact batch set assigned to the other families.

## Native spawn

Use a fresh default child with omitted `agent_type`. The native spawn request
is:

```text
spawn_agent(
  task_name="review_codex_<unique-suffix>",
  fork_turns="none",
  model="gpt-5.6-terra",
  reasoning_effort="xhigh",
  message=review_message
)
```

Keep agent_type omitted. Use a collision-resistant task label and
retry with a new suffix if necessary. A running handle is pending, not failed
or unavailable. Collect the terminal result unless the owner cancels the leg.
Requested model and effort are evidence when accepted; record unavailable
runtime metadata as unexposed once rather than probing repeatedly. An exposed
route mismatch invalidates the leg.

The no-edit and no-execution contract is prompt-controlled unless runtime
metadata proves a stronger containment boundary. Invalidate a leg that edits
the directory or executes candidate material.

## Result admission

For the unbatched `formal-gate` compatibility profile, native spawn returns a
terminal agent message, not CLI output. Admit the four semantic elements
directly: `verdict`, `findings`,
`affected_surfaces_inspected`, and `open_questions`. Ordinary Markdown,
labeled prose, or JSON are valid renderings; JSON parsing is not required.
Markdown fences do not invalidate a result. Presentation style alone is never
a finding. Missing or ambiguous semantic content is invalid.

Each material finding identifies severity, a prepared-directory-relative path and
positive line number when applicable, the triggering condition, evidence, and
correction direction. `SAFE` requires no Critical or Major finding and no
unresolved open question. Unsupported or evidence-free output remains invalid
and returns to the leader without silent repair.

The leader admits the result only when all four elements are present, evidence
is grounded in the prepared directory, the terminal evidence shows no
mutation or prohibited execution, and the post-review digest equals the
pre-review digest. The leader reproduces findings independently and combines
the fresh result with the other two legs. Use unanimous admission rather than
voting or averaging labels.

For `batched-full-coverage`, persist the exact original UTF-8 terminal-message
bytes under the same `<family>/<batch-id>.json` custody rule as external
provider responses. Accept raw JSON or exactly one outer Markdown fence using
the shared contract's strict grammar; inner triple backticks remain JSON data.
Validate every strict receipt and admit the complete three-family tree only
through the exact absolute `toolkit_root / "bin" / "review_coverage.py"`
`admit` command. A successful `coverage-admission.json` with matching
candidate/source/evidence bindings is the sole machine-admissible result. An
unbatched four-element message cannot replace a batch receipt.
