# TRIAD Review Integrity SOT Design

**Status:** Owner-approved design.

**Date:** 2026-08-11

## Objective

Close the reproduced review-integrity defects without creating a second skill
source or a parallel test harness. The workspace-discovered
`triad-cross-family-review` skill and its packaged scripts remain the single
source of truth (SOT), while a dedicated `triad-skill-executor` child performs
behavior and test execution against those exact bytes.

## Current SOT and runtime path

The workspace discovery link
`.agents/skills/triad-cross-family-review` resolves to:

```text
workspace/triad-codex-dispatch-reliability/skills/triad-cross-family-review
```

The registered `triad-skill-executor` profile enables that exact canonical
`SKILL.md`. The skill resolves the toolkit root from its own canonical path and
invokes the tracked packaged script at `bin/review_round.py`. Development must
therefore edit these source files directly; it must not copy them into a test
skill, installed cache, or alternate checkout.

Fresh executor children reload the configured source path. The catalog path and
profile remain unchanged, so this work does not require a workspace catalog
configuration edit. A new child is still required for every independent
behavior observation.

## Ownership and test boundary

The root Codex leader owns design, test-source authoring, SOT edits, result
adjudication, operational three-family reviews, commits, packaging, and release
work. The dedicated executor:

- is spawned with `agent_type="triad-skill-executor"` and
  `fork_turns="none"`;
- executes the configured skill and exact requested tests or behavior scenario;
- may create only an explicitly bounded disposable fixture;
- does not edit the SOT, tests, repository configuration, or user-global state;
- does not dispatch providers or claim a review verdict; and
- returns raw commands, outcomes, fingerprints, and cleanup evidence.

The root leader does not execute the skill's Python test suite or behavior
fixture directly. It writes the failing test first, delegates RED execution to
a fresh executor, makes the minimal SOT correction, then delegates GREEN and
regression execution to another fresh executor. Read-only source inspection,
Git inspection, and reviewer-result validation remain leader responsibilities.

Operational `triad-cross-family-review` gates remain root-led. The executor is
development/test infrastructure only and never becomes the operational review
leader.

## Slice decomposition

Each slice is an independent merge-gate unit with one behavioral claim. The
slices accumulate on one isolated feature branch, but each receives its own
test cycle, commit, and three-family review over the exact slice delta.

### Slice 1: Deterministic, non-executing Git diff fingerprint

**Behavioral claim:** Fingerprinting is hermetic to repository-local Git diff
configuration.

Add one canonical fingerprint diff-flag tuple in `bin/review_round.py` and use
it for both staged and unstaged diff arms. Retain the existing binary,
full-index, color, and external-diff controls, and additionally pin:

```text
--unified=3
--inter-hunk-context=0
--diff-algorithm=myers
--no-indent-heuristic
--no-renames
--no-textconv
--src-prefix=a/
--dst-prefix=b/
```

Use `--no-renames` rather than `--find-renames=50%`: fingerprinting needs a
stable byte representation, not semantic rename presentation, and disabling
rename detection also avoids configuration-dependent rename limits. Explicit
source and destination prefixes close the independently reproduced
`diff.noprefix` gap left by the proposed flag set.

The RED test must prove that current bytes either change under a raw
configuration-sensitive fixture or execute a configured textconv sentinel.
The GREEN test must cover staged and unstaged arms, the listed local diff
settings, `diff.noprefix`, and a textconv sentinel that remains absent.

Forecast: 15-30 production lines, zero novel algorithmic-core lines, one
behavioral claim; S-class.

### Slice 2: Refuse fingerprint-blinding index flags

**Behavioral claim:** No fingerprint is emitted for a worktree containing an
`assume-unchanged` or `skip-worktree` tracked entry.

Read `git ls-files -v -z` at every fingerprint boundary. Reject any lowercase
tag or `S` tag before returning a digest. If `core.sparseCheckout` is enabled,
return a dedicated sparse-checkout refusal that does not recommend
materializing out-of-cone paths. Otherwise return a bounded diagnostic with the
repository path escaped using `repr`-style rendering. Fold the accepted raw
index-flag inventory into an `INDEXFLAGS` arm after the refusal check.

The RED fixture must show a tracked file mutation hidden from status, staged
diff, unstaged diff, and the current fingerprint. GREEN covers
`assume-unchanged`, `skip-worktree`, their combined lowercase form,
sparse-checkout messaging, an ordinary index, capture, verify, and the direct
`fingerprint-worktree` CLI.

Forecast: 40-80 production lines, 30-50 novel-core lines, one behavioral claim;
S-class.

### Slice 3: Root-anchored no-follow file hashing

**Behavioral claim:** Round integrity reads never follow a symlink substituted
for a selected regular file or one of its path components.

Replace lstat-then-path-read sequences used for prepared-file and untracked-file
hashing with root-anchored descriptor traversal. Open every directory component
relative to an already opened directory descriptor with no-follow semantics,
open the leaf with `O_NOFOLLOW`, verify it with `fstat`, and stream digest-only
content directly into SHA-256. Keep a bounded descriptor-based byte reader only
where callers require the actual payload.

Leaf-only `O_NOFOLLOW` is insufficient because an intermediate directory can be
swapped. The implementation must remain Python-standard-library code supported
on the documented macOS and Linux/WSL2 environments and fail closed when the
required no-follow primitives are unavailable.

RED and GREEN fixtures cover leaf replacement, intermediate-directory
replacement, non-regular entries, multi-chunk digest equivalence, and bounded
memory behavior through the streaming interface.

Forecast: 80-150 production lines, 70-120 novel-core lines, one behavioral
claim; S-class.

### Slice 4: Explicit reviewer context and boundary contract

**Behavioral claim:** Every rendered reviewer prompt distinguishes ruled-out
internal scenarios, declared untrusted system boundaries, evidence-backed
context challenges, and genuinely unknown context.

Add one shared fixed context contract to both prepared-directory and worktree
renderers. It must state that reviewers do not demand validation, fallback, or
error handling for scenarios expressly ruled out by the governing deployment
context or an evidenced framework guarantee; declared untrusted inputs such as
vendor stdout, run logs, and review packets remain system boundaries where
validation is in scope; reviewers may challenge a context claim with concrete
review evidence; and context required to decide current correctness must be
reported in `open_questions`, preserving the existing `NOT-SAFE` rule rather
than guessing a severity.

Document the same fixed contract in the prompt-contract reference. Add a
whitespace-normalized exact drift test so renderer and documentation wording
cannot diverge because of prose wrapping. Situation-specific objective,
criteria, and review points remain leader-authored; this fixed contract does not
generate review points. `skill-prompt-review` remains excluded from operational
rounds.

Forecast: 20-50 production lines, zero novel-core lines, one behavioral claim;
S-class.

## Explicit non-changes

- P4 needs no change: current `capture_round` and `verify_round` compare every
  prepared source member before and after worktree fingerprinting.
- P6 is not adopted: current `prepare` already validates and copies the exact
  member list and binds it to source rechecks. A brief-plus-range orchestration
  command is a separate product capability, not an integrity repair.
- P7 does not authorize a diagnostic sweep. New path-bearing diagnostics in
  Slice 2 use escaped rendering; unrelated diagnostics stay unchanged without a
  reachable reproduced defect.
- No provider model, permission, MCP, wrapper, global configuration, or schema
  change is in scope.

## Verification and gate protocol

For every slice:

1. The root writes the smallest failing test without changing production SOT.
2. A fresh `triad-skill-executor` runs the focused test and returns RED evidence.
3. The root edits the exact discovered `SKILL.md`, its canonical references, or
   packaged `bin/review_round.py` as required by that slice.
4. A fresh executor runs focused GREEN tests, applicable skill validation, the
   complete repository suite, and `git diff --check`; it records source status
   before and after and must not mutate the SOT.
5. The root commits the slice and runs a fresh-ID Claude, Google, and no-history
   Codex review with situation-specific review points. No skill-prompt review is
   attached.
6. Any verified bounded defect restarts that slice's TDD and complete
   three-family gate. A proposal outside this design returns to the owner.

The current pre-edit executor baseline is `BEHAVIOR_RED`: the configured
textconv driver was executed by `fingerprint-worktree`. Its first configuration
fixture did not independently prove raw diff sensitivity, so it is not admitted
as evidence for that half of Slice 1; the focused RED test must establish that
precondition before production changes.

## Distribution and deployment acceptance

The source skill directory and `bin/review_round.py` are already included in
the repository's distribution verifier hash targets. After all admitted slices:

1. commit the exact SOT bytes;
2. have the dedicated executor run clean-HEAD distribution verification, which
   archives `HEAD`, compares source/archive hashes, and runs package tests from
   extracted bytes;
3. preserve the archive SHA-256 and per-target hash report;
4. push the feature branch and prepare the normal release metadata;
5. obtain the owner's target-specific approval before writing an installation
   outside `/Users/chaniri/codex_workspace`;
6. install only the verified archive bytes through the supported bootstrap
   path; and
7. prove exposure from a fresh ephemeral Codex process with an exact current
   marker.

Source tests, formal review, distribution bytes, installation, and fresh skill
exposure remain separate evidence claims. Final merge still requires explicit
owner approval.
