# Triad R8 Review Repair Amendment

## Objective

Repair the five evidence-backed R7 gate defects, preserve the complete immutable R7 packet and
sibling result record, and rerun the full macOS/Ubuntu and four-leg formal review gate before any
commit, push, plugin installation, or bootstrap application.

## R7 decision

R7 packet `bd1a9bfaa1c7d565ea0f2121793cd0a9e8157857d4c5f232e8b3ee24d5c05a75` is
immutable and `INVALID / NOT-SAFE`. All four results were schema- and identity-valid: Gemini A
returned `SAFE`; Gemini B, Codex A, and Codex B returned `NOT-SAFE`. Evidence, not vote count,
established these compatible Major defects:

1. Shell-entry refresh, append, and removal can overwrite a concurrently replaced user shell RC.
2. Install-time legacy repair-agent migration can quarantine a concurrently replaced foreign file.
3. Antigravity settings transactions can follow predictable temporary-file symlinks and truncate
   foreign targets.
4. The review snapshot source opener does not reject symlinked directory ancestors.
5. The recommended requirements template retains company/organization deployment language that
   was explicitly removed, while its stale-term test omits migration templates.

## Scope limits

- Keep Python 3.12 standard-library and existing Git CLI prerequisites; add no product dependency,
  daemon, database, global lock, shell-only filesystem primitive, or platform-specific product path.
- Preserve the existing AGY-primary and proven-unavailability Gemini Enterprise fallback contract.
- Keep user-owned provider authentication, ordinary approval posture, and manual bootstrap boundary.
- Do not broaden the repair into a general filesystem transaction framework or unrelated threat
  model. Reuse the existing bootstrap transaction primitives and exact-path helpers.

## Task 1: Bootstrap user-file custody

1. Add deterministic seam-based red tests for shell-RC replacement during install refresh, initial
   append, and remove. Require byte-exact preservation of the replacement and no partial managed
   block.
2. Move the complete shell-entry transformation/publication into `bootstrap_repair.py`: capture one
   exact regular-file state, transform in memory, stage once, and publish only against that state;
   use no-clobber publication when absent and preserve the prior mode.
3. Add a deterministic red test that swaps a provenance-managed legacy repair-agent after capture
   but before quarantine. Require the foreign replacement to remain at the public path.
4. Add a bounded managed-quarantine operation using the existing state, claim, journal,
   no-clobber-publication, rollback, and recovery-custody primitives. Keep remove-side behavior
   unchanged.

## Task 2: AGY temporary-file custody

1. Add red tests for pre-existing symlink and non-regular temporary leaves for `settings.json`,
   `.agybak`, and `.agy_settings.shared.json`, including restore-time behavior and foreign-byte
   preservation.
2. Replace fixed `p.name + ".tmp"` writes with a unique same-directory regular file opened through
   `O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC`, write/fsync through the descriptor, attest the
   created inode before publication, and clean only that exact inode.
3. Preserve settings restoration and answer-suppression semantics on every failure.

## Task 3: Snapshot source boundary

1. Add tracked and non-ignored-untracked red tests that swap a source directory to a symlinked
   ancestor after Git enumeration. Require immediate refusal without captured external bytes or
   snapshot residue.
2. Open and retain the canonical repository directory descriptor, traverse every source path
   component descriptor-relatively with `O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC`, and open only a
   regular leaf with `O_NOFOLLOW` on both copy and post-copy rehash.
3. Detect real source-universe symlinks and nonregular filesystem entries that Git does not report,
   normalize every executable source to sealed mode `0555` and every other regular source to
   `0444`, and close every descriptor on partial traversal failure.
4. Stream candidate hash verification instead of buffering the largest candidate file in memory.
   Preserve compact stdout, complete file IPC receipts, quiescent-source wording, and macOS/Ubuntu
   portability.

## Task 4: Personal-only migration documentation

1. Remove ChatGPT Business/Enterprise, organization deployment, managed-fleet, and MDM setup
   wording from the personal requirements template without removing the separate Gemini
   Enterprise fallback route.
2. Include every shipped migration template in stale company/fleet terminology tests.
3. Keep the optional personal machine `/etc/codex/requirements.toml` remediation only if its text
   no longer describes organizational distribution or a company setup workflow.

## Task 5: Pre-freeze skill-contract repair

1. Replace fixed native `task_name` examples with collision-resistant lowercase/underscore labels so
   repeated repair handoffs and fresh Codex reviews remain callable in one parent thread.
2. Preserve leader orchestration: the leader chooses identical, perspective-split, or hybrid
   prompts unless the owner explicitly constrains that choice.
3. Treat nonterminal tool session/cell handles as pending, use event-driven status checks, and
   treat poll timeouts only as wake-up boundaries.
4. Correct formal-review Markdown spans and describe cleanup timing at the actual dispatch boundary.

## Task 6: Verification and R8 gate

1. Run focused red/green tests in the owner's normal Python 3.12 environment.
2. Run implementation reviews for the bootstrap, AGY, snapshot, and documentation boundaries, then
   repeat the final skill/prompt review.
3. Run the live test suite, standalone cleanup harness, shell syntax, Python compile, plugin and
   skill validation, and pinned Git-equipped Ubuntu 24.04 suite from one frozen candidate snapshot.
4. Freeze a new immutable R8 packet and verify `PACKET_SHA256`, `SHA256SUMS`, and
   `INPUT_SHA256SUMS` before dispatch.
5. Admit two exact Gemini 3.1 Pro (High) legs and two independent fresh Codex legs against the same
   R8 packet bytes before consuming results. Do not normalize or retry an invalid result.
6. Only four valid `SAFE` legs with no blocking findings or open questions authorize commit, push,
   local plugin installation, bootstrap application, and fresh-session verification.
