# Triad R6 Review Repair Amendment

## Objective

Repair only the evidence-backed R5 gate defects, retain the simple one-hour best-effort IPC
cleanup, and rerun the complete macOS/Ubuntu and four-leg review gate before commit, push, or
installation.

## R5 decision

R5 packet `2f5e06de36426a342378cdeaf9b82534bfd3afc9fa852d545b0eb97d04932ae0` is
immutable and `INVALID / NOT-SAFE`. The invalid Gemini result used an unapproved verdict literal;
it is archived but is not treated as review evidence. The remaining three valid legs and direct
fact-checking confirm these defects:

1. On macOS, a timed-out PTY session leader can already be a zombie while descendants still hold
   the PTY; `getpgid(leader_pid)` then fails and leaves the descendants alive.
2. Generated absolute-runtime shebangs can exceed the portable 256-byte kernel limit and fail on
   Ubuntu with `ENOEXEC`.
3. Classifier creation can follow a dangling symlink after earlier bootstrap mutations.
4. The fixed `config.toml.bak` path can overwrite or follow an existing filesystem object.
5. Config merge/removal can overwrite an ordinary concurrent atomic-save replacement.
6. Profile/rules installation can truncate a regular replacement made after preflight.
7. A first-attempt AGY `exec` failure with `ENOTDIR` or `ELOOP` is not eligible for the documented
   pre-submission Gemini Enterprise fallback.
8. PTY group termination should avoid the small PID/PGID-reuse window while fixing item 1.

The following R5 claims are rejected as blockers: the documented same-prompt provider-capacity
retry, the writable packet-construction scratch helper, absence of live Enterprise policy proof in
an AGY review round, and the claim that `--dangerously-skip-permissions` bypasses the injected AGY
deny policy. Live token-using containment spikes proved file and command writes were denied.

## Scope limits

- Do not add a daemon, database, global bootstrap lock, whole-bootstrap transaction, or OS-specific
  product utility.
- Keep each classifier, managed artifact, and config fragment operation as an independent
  descriptor-checked transaction using Python 3.12 standard-library primitives.
- Keep the absolute Python runtime in generated shebangs. Reject an emitted shebang longer than
  256 filesystem-encoded bytes before persistent installation changes.
- Keep AGY primary and the existing Gemini Enterprise/Business fallback. Do not weaken the formal
  result schema or accept verdict synonyms.
- Do not redesign the one-hour UUID/file-IPC cleanup or restore company-only setup.

## Task 1: PTY and AGY route repairs

Files: `bin/_pty.py`, `bin/antigravity_wrapper.py`, and focused Antigravity/PTY tests.

1. Add a macOS-compatible regression seam proving that group termination does not call
   `getpgid()` after the PTY child has exited while a descendant remains.
2. Use the `pty.fork()` contract that the child PID is the session/process-group ID. Keep the
   direct leader unreaped until TERM/KILL escalation is complete, then let the existing caller reap
   it. Treat an already-gone group as success.
3. Extend only the first-attempt pre-submission fallback errno set with `ENOTDIR` and `ELOOP`.
   Later failures remain ineligible.
4. Replace stale comments and changelog claims about AGY danger mode bypassing injected denies.
   Add a deterministic composition test proving formal argv retains `--sandbox` and the guarded
   read-only deny policy while permission prompts are auto-approved.

## Task 2: Portable runtime and bounded bootstrap transactions

Files: `bin/bootstrap_repair.py`, `scripts/bootstrap.sh`, `tests/test_bootstrap.py`, and
`tests/test_bootstrap_repair_transaction.py`.

1. Add RED tests for exact 256-byte and 257-byte filesystem-encoded shebangs, including a
   multibyte path, and for rejection before persistent bootstrap mutation.
2. Add `portable_python_shebang()` and a narrow `runtime-path` command. Reuse it in launcher
   generation and install preparation; make bootstrap resolve the runtime through that command.
3. Add narrow `classifier --action preflight|ensure` commands. Reject symlink/non-regular leaves,
   verify existing JSON through a no-follow descriptor, and create absent state with no-clobber
   publication. Run classifier preflight with the other read-only preflights before
   `begin_command_group` or any launcher/profile/rules/config mutation. Add an end-to-end test that
   a live or dangling classifier symlink leaves every seeded install artifact byte-exact.
4. Add narrow `managed-artifact --action preflight|install --kind profile|rules` commands. Require
   the exact first logical line marker, hold payload bytes, and publish only against the captured
   target state. Preserve the existing mode or use the current umask for a new target. Add a
   bootstrap/distribution contract proving the shell no longer mutates the public profile/rules
   targets directly after delegating them to this helper.
5. Add narrow `config-fragment --action merge|remove` commands. Preserve the current exact block
   ownership rules, publish a backup only when its leaf is absent, and replace/remove config only
   against its captured state. A successful backup may remain as recovery evidence when the config
   publication loses a race. Any pre-existing backup filesystem object, including a regular file
   or live/dangling symlink, is an rc-3 refusal and neither it nor config may change. Add a
   bootstrap/distribution contract proving the shell delegates every public config mutation to the
   helper rather than retaining embedded `write_text`, `os.replace`, or `unlink` paths.
6. Keep shell sequencing and payload generation. Replace only the unsafe leaf reads/redirections
   and config mutation heredocs with the narrow Python commands.

### Task 2 implementation-review repairs

The first Task 2 implementation review found five Major integration gaps. Repair them before the
full gate:

1. Reuse exact-first-logical-line ownership for profile/rules removal; a marker appearing only in a
   later comment or string is user-owned and must survive.
2. Create an absent `config.toml` with mode `0600`, independent of umask; preserve captured mode for
   an existing file.
3. Treat a transactional config-fragment remove rc as a bootstrap failure. Keep semantic
   `unrecognized-managed` as the existing warning/no-op.
4. Treat a late classifier `ensure` refusal as a bootstrap failure, including a race after the
   initial read-only preflight.
5. Treat the late profile/rules preflight refusal inside each installer as a bootstrap failure;
   the initial preflight remains fail-closed and the mutation helper still rechecks captured state.

Add unit and end-to-end RED/GREEN tests for each item, including byte-exact preservation of foreign
replacements. Do not add global state or a broader transaction.

## Task 3: Verification and R6 gate

1. Run focused RED/GREEN tests outside the Codex filesystem sandbox in the owner's normal Python
   environment.
2. Run the full pytest suite, standalone cleanup harness, shell syntax, Python compile, plugin
   validator, deterministic skill lint, and pinned Ubuntu 24.04 verification.
3. Run the final `skill-prompt-review` stage and change prompts only for a concrete conflict.
4. Freeze a new immutable R6 packet and verify `PACKET_SHA256`, `SHA256SUMS`, and
   `INPUT_SHA256SUMS` before dispatch.
5. Admit two exact Gemini 3.1 Pro (High) legs and two independent fresh Codex legs against the
   identical immutable packet bytes before consuming results. Remind reviewers that the only
   verdict literals are exactly `SAFE` and `NOT-SAFE`; do not retry or normalize schema-invalid
   output.
6. Reconcile evidence, not votes. Only a clean R6 gate authorizes staging, commit, push, local
   plugin installation, bootstrap application, and fresh-session skill verification.
