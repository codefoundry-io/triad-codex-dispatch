# Triad R5 Review Repair Amendment

## Objective

Repair only the evidence-backed R4 gate defects, retain the simple one-hour best-effort IPC
cleanup unchanged, and rerun the complete macOS/Ubuntu and four-leg review gate before any
commit, push, or install.

## R4 decision

R4 packet `f218b348ceadbc202cc234c8abee8ed204047185ed1cfde9d0a44739a7f64913` is immutable and
`NOT-SAFE`. All four required legs completed. The Google rules-field finding is rejected because
the current official Codex manual explicitly defines `match` and `not_match` as supported inline
tests, and the live `codex execpolicy` parser accepts the shipped file. The following five defects
are confirmed:

1. Selected unmanaged regular Codex profile/rules targets are discovered only after wrapper
   publication, leaving a predictable partial install.
2. A malformed managed shell block can make refresh/removal truncate unrelated shell RC bytes.
3. A PTY child exec failure is collapsed into exit 127 plus `extraction-error`, hiding proof that
   AGY never started and preventing the documented eligible fallback.
4. Profile/rules/legacy-agent removal checks ownership and then deletes by mutable pathname,
   allowing an ordinary concurrent atomic save or second bootstrap to lose foreign bytes.
5. Formal packet verification checks only manifest-listed paths and accepts an additional
   provider-visible unlisted file or filesystem object.

## Scope limits

- Do not redesign the one-hour cleanup, add a daemon, add a database, or promise perfect cleanup.
- Do not make the whole bootstrap lifecycle transactionally atomic. Add only early ownership
  rejection for the common install conflict and reuse the existing claim/verify primitive for
  destructive removal.
- Do not add OS-specific product commands or dependencies. Use Python 3.12 standard-library
  primitives supported on macOS and Ubuntu 24.04.
- Do not add a new public dispatch phase or classification solely for PTY start failure. Mirror
  existing pre-resolution binary failure: an explicit first-attempt pre-submission error and exit
  code 4. A start failure after any successful provider exec remains post-dispatch and ineligible
  for fallback.
- Do not change valid `match` or `not_match` rule fields.
- Do not restore company-only setup or the removed runtime commands.

## Task 1: Formal packet tree closure

Files: `bin/triad_formal_review_schema.py`, `tests/test_formal_review_schema.py`,
`tests/test_provider_packet_context.py`, `tests/test_antigravity_packet_context.py`.

1. Add failing tests for an unlisted regular file, symlink, FIFO, and empty directory; keep all
   manifest and packet hashes unchanged.
2. Add provider-boundary tests proving an unlisted regular entry fails before binary resolution,
   settings mutation, or PTY execution.
3. Implement one descriptor-rooted, sorted, no-follow tree scan.
4. Require the actual regular-file set to equal the `SHA256SUMS` entries plus `SHA256SUMS` and
   `PACKET_SHA256`; require the input manifest set to equal the outer set minus
   `INPUT_SHA256SUMS`; reject symlinks, non-regular entries, and unbound empty directories.
5. Keep the existing digest and finding-location validation unchanged.

## Task 2: PTY start-result distinction

Files: `bin/_pty.py`, `bin/antigravity_wrapper.py`, focused PTY/Antigravity tests.

1. Add failing tests for a missing shebang interpreter and for a successfully execed child that
   intentionally exits 127; keep the existing distribution fixture aligned with the real outer
   and inner manifest convention.
2. Add a close-on-exec child-to-parent status pipe around `pty.fork()` and a dedicated internal
   start exception containing only stage and errno. Create the existing timeout deadline before
   fork, poll the status pipe within it, and close/kill/reap on expiry.
3. Track whether any attempt successfully execed. Only a first-attempt `exec` failure whose errno
   proves the executable route is missing or unstartable logs the pre-submission reason, returns
   existing exit code 4, and creates no repair handoff. `chdir`, `E2BIG`, resource/config errors,
   and every later retry failure remain post-dispatch/ineligible.
4. Do not infer start failure from exit code 127.

## Task 3: Bootstrap bounded ownership repairs

Files: `scripts/bootstrap.sh`, `bin/bootstrap_repair.py`, `tests/test_bootstrap.py`, and
`tests/test_bootstrap_repair_transaction.py` only if the reused primitive needs a direct seam.

1. Strengthen existing unmanaged profile/rules tests first: no wrapper, config, classifier, shell,
   or repair artifact may change.
2. During the existing read-only preflight, require any selected existing regular profile/rules
   target to contain its current managed marker; reject unreadable or foreign bytes before
   `begin_command_group`. Keep the existing final-write checks.
3. Add install/remove malformed shell-marker tests for begin-only, reversed, and duplicate blocks,
   including CRLF input; require byte-exact preservation and nonzero status.
4. Validate exactly one canonical begin/end pair before stripping. Do not add unrelated shell
   parsing or a new shell dependency.
5. Add deterministic swap tests for profile, rules, and legacy-agent removal.
6. Reuse `read_state` plus the existing UUID private-claim and verified-delete primitives in
   `bootstrap_repair.py`; delete only the claimed managed inode and preserve any replacement at the
   public path. Do not introduce a global lock or a new OS-specific utility.

## Task 4: Verification and R5 gate

1. Run focused RED/GREEN tests for each task from `/Users/chaniri/codex_workspace` using the
   user's normal outside-sandbox Python 3.12 environment.
2. Run the full pytest suite, standalone cleanup harness, shell syntax, Python compile, plugin
   validator, deterministic skill lint, and the existing Ubuntu 24.04 container verification.
3. Run the final `skill-prompt-review` stage. Change prompts only for a concrete contradiction.
4. Freeze a new immutable R5 packet and verify `PACKET_SHA256`, `SHA256SUMS`, and
   `INPUT_SHA256SUMS` before dispatch.
5. Launch two exact Gemini 3.1 Pro (High) legs and two independent fresh Codex legs against the
   newly frozen inputs before consuming verdicts. Reconcile evidence, not votes.
6. Only a clean R5 gate authorizes staging, commit, branch push, documented installation, and
   fresh-session installed-plugin verification.
