# Triad R7 Review Repair Amendment

## Objective

Repair the six evidence-backed R6 gate defects plus the same-scope boundary defects found by the
R7 implementation review, preserve the complete R6 record, and rerun the full macOS/Ubuntu and
four-leg review gate before commit, push, or installation.

## R6 decision

R6 packet `469b0a4904453a3c5f99a0b575657f4e9da029d7f7db4bfdcae70103a7f90e7a` is
immutable and `INVALID / NOT-SAFE`. All four results were schema- and identity-valid: Gemini A,
Codex A, and Codex B returned `NOT-SAFE`; Gemini B returned `SAFE`. Evidence, not vote count,
established these defects:

1. Path-based run-log creation and cap pruning can follow a writable symlink and write or unlink
   outside the managed log root.
2. Public launcher ownership accepts a marker substring outside its generated provenance position.
3. Identity-mismatch prompt instructions require a `FormalReview` that the canonical validator
   necessarily rejects.
4. External-provider prompt injection omits the nested finding contract and verdict rules needed
   to return a valid substantive review.
5. Mutation-time `BaseException` can bypass transaction rollback and finalization.
6. Antigravity settings restoration failure retains a previously validated answer despite the
   answer-suppression contract.

## Scope limits

- Use Python 3.12 standard-library, descriptor-relative filesystem operations already present in
  the product; add no daemon, database, dependency, OS-specific product command, or global lock.
- Keep the one-hour best-effort UUID/file-IPC policy and unique private fallback.
- Keep the canonical strict `FormalReview` validator and exact `SAFE` / `NOT-SAFE` literals.
- Keep AGY primary and Gemini Enterprise/Business fallback eligibility unchanged.
- Do not change provider login, owner authorization, company setup, or deployment posture.

## Task 1: Run-log and command ownership

1. Add red tests for symlinked configured log roots, CLI/runs ancestors, and symlink/hardlink cap
   candidates. Prove no foreign write or unlink and exact fallback payload retention.
2. Create the unique run-log leaf with descriptor-bound `O_CREAT|O_EXCL|O_NOFOLLOW`; retain the
   directory descriptor through cap pruning and revalidate candidates at the deletion boundary.
3. Replace shell/Python marker-substring ownership with one Python predicate requiring the exact
   generated shebang, provenance line, imports, command kind/name, and exec grammar. Preserve
   marker-bearing foreign executables on install and remove. Recognize only the exact current and
   shipped legacy launcher/runtime grammars needed for deterministic upgrade and removal, bind the
   shebang interpreter to the exec interpreter, and reject partial legacy vendor-pin combinations.
4. Recheck the candidate inode and age on the final held file descriptor immediately before
   cap-based or stale-time run-log unlink, preserving IPC refreshed during cleanup.

## Task 2: Formal contract and failure custody

1. Classify every packet or review identity mismatch as invalid/missing outside `FormalReview` in
   both the skill and fresh-Codex reference.
2. For only the packaged canonical `FormalReview`, inject its complete nested JSON Schema plus the
   exact finding fields, severity literals, and verdict/open-question rules. Preserve compact
   generic Pydantic prompt behavior.
3. Catch mutation-time `BaseException` at each transaction entrypoint, run cleanup and rollback,
   then re-raise the original exception when recovery succeeds or the existing
   `TransactionFailure` when recovery fails.
4. Clear Antigravity `validated` state when settings restoration fails so neither stdout nor
   durable failure evidence retains the completed answer.
5. Register replacement, removal, and no-clobber publication mutations before the public
   `rename`/`link`, so an asynchronous interruption immediately after either syscall still has
   complete rollback custody.
6. Close the final skill-review defects: broaden the formal-review trigger contract, define the
   no-summary wrapper branch, validate native Codex results through the packaged schema CLI, and
   require deterministic code-complete snapshot/file-set closure instead of a selected-file
   packet.
7. Keep complete snapshot evidence in file IPC with compact stdout, describe exit `4` and missing
   wrapper summaries without inventing a provider result, require manifest-derived Codex finding
   locations, and reject source bytes or executable modes that differ during the post-copy rehash.

## Task 3: Verification and R7 gate

1. Run focused red/green tests in the owner's normal Python 3.12 environment.
2. Run live `tests/`, the standalone cleanup harness, shell syntax, Python compile, plugin and
   skill validation, and the pinned Ubuntu 24.04 suite from one frozen candidate snapshot.
3. Freeze a new immutable R7 packet and verify `PACKET_SHA256`, `SHA256SUMS`, and
   `INPUT_SHA256SUMS` before dispatch.
4. Admit two exact Gemini 3.1 Pro (High) legs and two independent fresh Codex legs against the same
   R7 bytes before consuming results. Do not normalize or retry an invalid result.
5. Only four valid `SAFE` legs with no blocking findings or open questions authorize commit, push,
   local plugin installation, bootstrap application, and fresh-session verification.
