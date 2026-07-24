# Triad R9 Review Repair Amendment

## Objective

Repair the twelve evidence-backed R8 gate defects, preserve the complete immutable R8 packet and
sibling result record, and rerun the full macOS/Ubuntu and four-leg formal review gate before any
commit, push, plugin installation, or bootstrap application.

## R8 decision

R8 packet `d95f94d4d89a88577f69195dca6f8900112c72779962359abed4687677dbbc50`
is immutable and `INVALID / NOT-SAFE`. All four results were schema- and identity-valid and all
four returned `NOT-SAFE`. Reconciliation found one Critical, ten Major, and one Minor unique
defect. The reported nonregular-claim Critical was downgraded to Major because the object remains
at an explicit recovery path; the mutable bootstrap command-input Critical remains Critical.

## Scope limits

- Keep portable Python 3.12 behavior on macOS and Ubuntu 24.04. Do not add OS-specific product
  commands, a daemon, database, or platform-only filesystem API.
- Keep AGY primary and Gemini Enterprise fallback only after proven pre-dispatch AGY
  unavailability. Do not change provider authentication or copy credentials into a sandbox.
- Keep bootstrap network-free and non-privileged. It may prove a dependency and print an
  argv-safe owner command, but it must not install Python packages or write `/etc` itself.
- Prefer exact refusal and owner-visible recovery over a complicated claim of impossible
  same-user filesystem atomicity. Do not broaden this repair into a general transaction library.

## Owner scope reduction

The owner subsequently narrowed this release to normal-operation reliability: get the triad
dispatch/review path working, avoid adversarial over-design, and do not block distribution on
rare same-UID filesystem swaps or injected low-level I/O failures once the ordinary path is
proven. This section supersedes the release-gate wording below where they conflict.

- Keep the small Pydantic 2 readiness check because a missing or incompatible dependency blocks
  every formal review before provider dispatch.
- Keep the PTY EOF deadline fix because an ordinary provider can close output while its process
  remains alive; verify it on macOS and Ubuntu 24.04.
- Revert the large AGY and snapshot transaction expansions. The R8 implementations and their
  explicit residual-risk boundaries remain the shipped behavior for this release.
- Treat the R8 same-UID pathname races, FIFO/tree-swap injections, and unexpected PTY I/O
  injection as deferred hardening, not release blockers.
- Run real token-using smoke calls, the portable regression suite, and a functionality-focused
  four-leg review before distribution. Do not solicit speculative adversarial findings.
- No authored skill or dispatch prompt is changed by this reduction; skip the separate
  skill/prompt-review pass unless a later implementation actually changes one.

## Task 1: Remove mutable bootstrap command inputs

1. Add deterministic RED tests that replace the command manifest and each launcher payload after
   shell preparation but before helper consumption. Require zero public mutation and no foreign
   byte publication.
2. Remove manifest/payload pathname IPC from `commands-install`. Pass validated scalar inputs to
   one Python helper invocation and generate the exact three provider launcher byte strings and
   canonical targets in memory inside `bootstrap_repair.py`.
3. Make `commands-remove` derive its exact allowed target set from a canonical launcher directory,
   not a mutable manifest. Validate the complete set before its first mutation.
4. Keep shell quoting limited to argv construction. Preserve the current Python-generated
   escaping and launcher environment policy.

## Task 2: Exact bootstrap custody and ownership

1. Add a post-`same()` nonregular-swap RED test. Recover a claimed symlink or other portable
   non-directory object to its public name without clobber; if portable exact restoration is not
   possible, retain it at a stable explicit recovery path and report that path without masking the
   original refusal.
2. Replace shape-only `triad-apply-repair` ownership with exact current and explicitly supported
   legacy launcher grammar. Validate interpreter identity, fixed argv, classifier assignment, and
   apply target. Install must reject and remove must preserve every near-match.
3. Stop treating generic legacy-agent substrings as ownership. Automatically quarantine/remove
   only an exact supported historical generated form; otherwise preserve the file and emit a
   manual-reconciliation diagnostic.
4. Treat a marker-delimited but edited `codex-triad` shell block as user-owned. Recognize only the
   exact generated grammar for a valid profile; install and remove preserve every edited near-match.

## Task 3: AGY expected-state and release completion

1. Add deterministic RED tests for a temporary source swap after successful attestation and a
   concurrent destination update immediately before publication.
2. Publish settings, backup, and shared-state bytes through a same-parent private stage and
   no-clobber expected-state transition. Attest the published inode/content before provider use;
   preserve or surface every foreign replacement instead of overwriting it.
3. Return and retain the exact deny-installed state so restoration cannot overwrite an update made
   during the provider call.
4. Make shared-state loading distinguish valid, absent, and invalid/unreadable states. After a
   successful join, absence or invalidity is never successful release: restore from backup only
   when safely last, otherwise retain recovery evidence and raise so the wrapper suppresses output.

## Task 4: PTY and formal evidence bounds

1. Add a real child regression that closes its PTY descriptors and remains alive beyond the
   requested timeout. Poll `waitpid(..., WNOHANG)` against the existing deadline, terminate the
   process group on expiry, and reap exactly once.
2. Stream manifest-entry hashing through the existing descriptor-relative packet opener. Keep full
   reads only for bounded control data and files whose text is actually needed.
3. Open and retain the candidate directory descriptor before closure enumeration. Enumerate and
   re-enumerate descriptor-relatively; bind file hash, inode, type, and sealed mode to the same held
   descriptor; finally prove the public candidate name still names that retained directory.
4. Reject source paths containing CR or LF before snapshot mutation so the inner snapshot contract
   matches the required outer line-manifest grammar. Do not redesign every outer manifest format.

## Task 5: Formal dependency readiness

1. Add RED tests for Python 3.12 with Pydantic absent and with a Pydantic-1-compatible import
   surface. Both must fail before any persistent bootstrap mutation.
2. Feature-probe the exact Pydantic 2 APIs used by the canonical formal schema, without pinning a
   Python minor or excluding a future compatible Pydantic release.
3. Document the dependency and print a Python `shlex.join` owner-terminal install command when it
   is missing. Keep plugin installation and bootstrap free of implicit package downloads.

## Task 6: Verification and R9 gate

1. Run focused RED/GREEN tests and bounded token-using provider spikes in the owner's normal
   authenticated terminal where appropriate.
2. Run independent implementation reviews for the bootstrap, AGY, PTY, schema/snapshot, and
   installation-document boundaries, then repeat the final skill/prompt review.
3. Run the live suite, standalone cleanup harness, Bash syntax, Python compile, plugin validation,
   skill lint, and pinned Ubuntu 24.04 checks from one frozen candidate snapshot.
4. Freeze a new immutable R9 packet and verify `PACKET_SHA256`, `SHA256SUMS`, and
   `INPUT_SHA256SUMS` before dispatch.
5. Admit two exact Gemini 3.1 Pro (High) legs and two independent fresh
   `gpt-5.6-sol`/`high`/`fork_turns="none"` Codex legs against the same R9 packet before consuming
   results. Reconcile evidence rather than votes.
6. Only four valid `SAFE` legs with no blocking findings or open questions authorize commit, push,
   local plugin installation, bootstrap application, and fresh-session verification.
