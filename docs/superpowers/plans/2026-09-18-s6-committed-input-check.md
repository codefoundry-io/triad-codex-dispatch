# S6: Explicit committed-input check on an existing worktree

> Use Superpowers TDD with the repository's separate fresh Terra/high RED and
> GREEN executors. The root leader owns source and tests; independent agents
> execute checks and review findings.

## Selected outcome

Add `fingerprint-worktree --require-clean-head <full-commit-id>` as an opt-in
check for a caller-provided existing checkout. Require the exact HEAD and an
empty Git status before and after the existing fingerprint operation. Preserve
the existing index-flag/sparse-checkout refusal. Without this option, retain the
current dirty-worktree fingerprint behavior. The opt-in status predicate passes
`--ignore-submodules=none` so configured submodule ignoring cannot hide modified,
untracked, or changed-HEAD submodule state from these checks.

This is a setup check, not a checkout creator, OS isolation, admission, or an
immutable-byte guarantee. Git-ignored material remains outside the clean-state
claim and must stay outside the review boundary. Shared Git metadata and later
mutation still require the existing post-review integrity check.

Run the optional clean check before creating review custody files, then follow
the normal custody/fingerprint/render workflow. It does not add receipt fields
or change the review digest. AGY still requires a pre-existing UUID whose single
resource matches the actual review cwd and whose read-only guard is valid.
Never borrow another checkout's UUID or fall back to global settings.

This repository continues to review its protected existing worktree through the
normal route; do not invoke this clean-only option on it or create another
checkout to bypass its intentional changes. Synthetic test repositories may
create/remove their own detached worktree to prove committed-input semantics.

Expected production delta: about 25–40 additions / 2 deletions, net below 40;
novel core below 40. Files: `bin/review_round.py`, focused additions to
`tests/test_review_round.py`, README English/Korean and SECURITY guidance.
No provider settings, project registration, automatic worktree lifecycle,
runtime dependency, bootstrap, version, or installation change.

## Task 1: Opt-in setup validation

1. Add actual Git/CLI tests: detached review checkout retains committed bytes
   while its developer fixture is dirty; exact clean HEAD succeeds; wrong or
   symbolic commit, staged/unstaged/untracked input and hidden index flags fail;
   the default dirty-worktree mode still succeeds; inspection does not mutate
   either fixture checkout. Dirty submodules remain refused even when the
   superproject config ignores them. File or clean-HEAD drift injected during
   fingerprinting is rejected.
2. A fresh dedicated source executor records the intended focused RED.
3. Add only the optional CLI argument and bounded clean-state checks around the
   existing fingerprint. Accept full lowercase SHA-1 or SHA-256 commit IDs.
4. Document the setup ordering, exact AGY root prerequisite, ignored-file/shared
   metadata limits, default dirty-review preservation, and no admission credit.
5. A distinct fresh executor runs focused GREEN, full repository regressions,
   skill validation and provider-free lifecycle; record source identity and
   exact fixture cleanup. Keep release/deployment verification separate.

## Task 2: Review and merge

Obtain an independent static task review, then freeze the whole S6 diff and run
the required four-leg plan-completion/pre-merge gate. Inspect tests and unchanged
fingerprint/render/AGY consumers. Validate each finding against source; preserve
all started results and use a fresh complete round after any reviewed-byte
change. Verify CI, remote/base/head and protected files before the authorized S6
merge. Continue the next slice without deploying.

A confirmed defect in the approved/existing design invokes the owner's stop,
independent Claude/Google/fresh-Codex diagnosis, and briefing boundary.

## Verification

From the workspace host cwd through `/bin/zsh -lic`, use literal `python3`,
`PYTHONDONTWRITEBYTECODE=1`, canonical repository `$1` and no pytest cache:

```sh
python3 -m pytest -q "$1/tests/test_review_round.py" -k committed_input --rootdir "$1" -p no:cacheprovider
python3 -m pytest -q "$1/tests" --rootdir "$1" -p no:cacheprovider
python3 "$TRIAD_SKILL_VALIDATOR" "$1/skills/triad-cross-family-review"
python3 "$1/skills/triad-cross-family-review/scripts/verify_lifecycle.py"
```

Resolve `TRIAD_SKILL_VALIDATOR` to the host's system skill-creator validator.
