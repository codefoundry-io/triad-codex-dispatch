# Scoped symlink review evidence implementation plan

> Execution: the Codex leader authors source; fresh dedicated Terra/high agents
> observe RED and GREEN. Use superpowers:executing-plans for this single task.

**Goal:** Make approved symlinks visible without implicit target reads during
guarded worktree review, satisfying the existing C26/R-PREPARE adaptation.

**Architecture:** Reuse the current leader-authored TASK and its digest binding.
The leader records only approved links from HEAD/index/worktree using no-follow
metadata and exact escaped link text. The common worktree renderer requires
reviewing that evidence and reporting missing target coverage, without adding a
collector, schema, public API or third review route.

**Spec:** shared `cases/cases.json` C26 and `reference/review-rules.md` R-PREPARE,
remote main `2eb883fee59e66556ee7c7f87189b38231136622`; B baseline
`14daa4da3755db5d5a70f203deb6b94bb5233e1b`.

## Scope and preservation

No repository-wide reviewer inventory. `approved_boundary` remains prose, not
a path grammar to parse. Include unchanged tracked links and changed/deleted
link states inside explicit approved paths; record absent/non-link states when
needed to explain a type change. Never inspect a target merely because its link
is approved. Target content requires a separately authorized bound input.
Keep prepared-copy refusal, captured-fingerprint reuse, final integrity, raw
INVESTIGATION, cleanup no-follow and all current provider routes unchanged.

Expected production delta: <=12 additions /0 deletions, <=12 novel core lines
in `bin/review_round.py`. Instructions: a short step-3 reference in SKILL.md and
one detailed section in references/leg-contracts.md, with concise English/Korean
README and security-boundary notes. Tests and fixtures separate.
No permission/hook/policy change and no vendor containment claim.

## Single coherent task

- [ ] Add `tests/test_review_link_evidence.py`: all four family/route render
  variants require exact-link evidence, no implicit leaf/ancestor traversal,
  separately bound targets and explicit coverage gaps. Assert the SOT links to
  preparation guidance, then use existing brief helpers to prove changed TASK
  link text changes the common digest with a constant captured fingerprint.
- [ ] Characterize tracked HEAD/index/worktree links: target-only content
  changes leave the fingerprint stable; staged and unstaged link text changes
  alter it. Keep existing untracked, prepare-refusal and cleanup tests.
- [ ] Fresh dedicated RED observes the missing contract. In a provider-free
  preparation scenario, request a TASK draft from an explicit small scope with
  unchanged, staged/unstaged, deleted and dangling links, plus a symlink ancestor.
  Record actual decisions; do not hand the executor the desired procedure.
- [ ] Add the common guarded-review clause and scoped TASK preparation guidance.
  The entrypoint stays within its existing 125-body-line budget. The detailed
  reference explains no-follow inspection, Git link blobs, exact JSON escaping,
  skipped targets and capture ordering; these are evidence, not instructions
  embedded in link text.
- [ ] Separate fresh dedicated GREEN repeats the preparation scenario, focused
  tests, full repository suite, skill validator and provider-free lifecycle.
  Run Ubuntu 24.04 full suite independently. Verify fixture cleanup and stable
  source identity; no installation/distribution claim from dirty source.
- [ ] Fetch shared main, compare A at an exact SHA/path/line, run complete required
  multi-family review, validate every finding against source, and rerun all legs
  after any correction. Commit/push/merge only admitted unchanged bytes.

## Review focus

Unchanged tracked links must not disappear merely because they have no diff.
HEAD, index and working-tree link text must not be conflated. A deleted link and
a path beneath a symlink ancestor need explicit coverage statements. Untrusted
link text must be escaped and treated as data. Target-only changes are outside
the link fingerprint and must never be represented as reviewed target content.
These are covered by the deterministic tests plus the independent fixture task.
