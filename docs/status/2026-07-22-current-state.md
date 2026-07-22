# Triad Codex Dispatch current state

Date: 2026-07-22

## Authoritative checkout

- Development root: `/Users/chaniri/codex_workspace`
- Product worktree:
  `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`
- Branch: `codex/triad-reliability-redesign`
- Local and upstream `HEAD` at this review boundary:
  `80f7a57188ad1a40059be6a2993a1646ef0e76e6`
  (`fix: inherit owner approval settings`)

The combined local commit is authorized but pending at this review boundary;
all changes described here are still uncommitted relative to the hash above.
This document does not embed a future child hash. After the commit step, verify
that local `HEAD` is its direct child and that the upstream hash remains
unchanged.

Preserve the unrelated dirty checkout at
`/Users/chaniri/triad-codex-dispatch`. Do not reset, clean, copy over, merge
into, or otherwise modify it.

The owner authorized one combined local commit after functional review. Push,
merge to another branch, version/changelog changes, reinstall, release, and
pull-request creation remain separate and pending. Any later Git history or
remote-state mutation goes through the workspace's automatic security review
and may present an approval request.

The installed plugin remains `0.2.527`. The combined local change has not been
installed, released, pushed, merged to another branch, or submitted as a pull
request.

## Worktree-first review contract

The normal formal-review path now uses the existing Git worktree directly:

- one canonical absolute worktree and one exact Git scope;
- one trusted leader-captured Git status/diff attached identically to all legs;
- direct reviewer reads and searches in that worktree;
- impact tracing into affected unchanged callers, consumers, tests, schemas,
  configuration, build files, and governing documentation;
- a pre/post fingerprint covering `HEAD`, the selected diff, the nonignored
  untracked inventory, and Git object hashes for untracked contents; and
- invalidation of the whole round if the fingerprint changes.

Provider read-only policies keep general shell execution denied. The leader
captures the Git navigation evidence with fixed non-mutating Git commands;
reviewers do not need shell access. No source packet, copied worktree, manifest,
allowlist, snapshot, or Python-generated related-file list is created by
default. The snapshot helper remains available only for an explicitly requested
durable archive.

The bounded review routes are:

- fresh Codex: `gpt-5.6-terra`, `xhigh`, `fork_turns="none"`;
- Claude: `opus`, `xhigh`;
- primary Google route: agy with `gemini-3.1-pro-high`.

Sol- or Fable-class long-running models are not routine reviewers. They remain
conditional escalations for genuinely ambiguous, security-sensitive, deeply
integrative, or adjudication-heavy work. Gemini is fallback-only after proven
pre-submission agy route unavailability.

## Agent-review distribution contract

The human-run `scripts/bootstrap.sh --install` now installs, under the selected
`$CODEX_HOME`:

- a dedicated `triad-codex-dispatch` profile with
  `approval_policy = "on-request"` and
  `approvals_reviewer = "auto_review"`; and
- exact managed-launcher `prefix_rule` entries with `decision = "prompt"`.

That combination routes eligible exact Claude, agy, and Gemini wrapper calls to
Codex Agent review instead of bypassing review or repeatedly asking the owner.
The generated justification identifies an owner-authorized triad review and
excludes credentials, tokens, cookies, authentication files, environment dumps,
provider logs, and unrelated paths. Bootstrap preserves the owner's base
approval keys.

`TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never` remains an explicit advanced
compatibility posture. Only that explicit posture rewrites the managed launcher
rules to `allow`; automatic review is inactive there.

An explicit owner invocation of the matching triad skill authorizes the named
provider review calls once while provider, destination, worktree, scope, and
data boundary remain unchanged. Agent review is the execution-time security
decision. Commit, push, install/update, merge, release, publication, and any
other provider remain separate owner decisions.

## Accepted AGY upstream behavior

Commit `94a24cb2e59972cd8fccefd06c05a6a7b77166b8` was reviewed functionally,
not merged as Git history. The combined local change ports only its safe
fail-closed behavior:

- a zero-exit own-line `<truncated N bytes>` or `<truncated N lines>` answer is
  quarantined as `truncated-answer` with terminal exit 65;
- nonzero vendor exit remains `vendor-error`, and truncated JSON never enters
  Pydantic validation or schema repair;
- a required formal agy leg with this result is invalid and must request a new
  bounded, compact result; post-dispatch truncation does not enable Gemini
  fallback; and
- the upstream generic `write_file`/sandbox-relaxation workaround, version and
  changelog changes, and upstream Git-history merge were rejected.

## Verification evidence

The workspace-root login-shell Python was
`/opt/homebrew/opt/python@3.12/libexec/bin/python3`, Python `3.12.13`, with
pytest `9.0.3`.

- TDD RED: the old skill required a code-complete archived packet and could not
  satisfy an existing-worktree-only scenario.
- Fresh Terra/xhigh pressure test: GREEN. It selected the existing worktree,
  identical trusted Git diff, affected-unchanged tracing, exact three routes,
  pre/post fingerprint, and no packet/list/repeated-approval workflow.
- AGY packet-context runtime: `47 passed in 0.60s`.
- `tests/test_distribution_contract.py`: `59 passed in 0.12s`.
- Native codex-cli `0.145.0` evaluator: each default managed launcher matched
  `prompt`; raw/repository/shell/Python negative forms matched no rule; the
  explicit-`never` launcher matched `allow`.
- Final bootstrap run: `233 passed in 118.53s`.
- Archive-compatibility and provider read-only regressions:
  `95 passed, 6 subtests passed in 6.10s`.
- All non-bootstrap tests: `391 passed, 6 subtests passed in 8.08s`.
- `bash -n` and `git diff --check`: passed for the bootstrap-owned slice.

Two monolithic all-test invocations exposed a pre-existing macOS process
stress flake: a temporary Python child was killed at `check_python` in varying
bootstrap edge cases. The changed bootstrap lines do not touch that check. The
most recent complete bootstrap run passed all 233 tests; the preceding run's
sole affected case passed in isolation, and the complete non-bootstrap
partition passed. No speculative source change was made for the nondeterministic
SIGKILL.

## Cancelled packet gate and external-state boundary

The proposed R15 packet-first formal dispatch was cancelled before any provider
leg executed. R14 remains immutable historical evidence but does not cover this
worktree-first slice. No Claude or Google provider was invoked, no fresh formal
three-family verdict exists, and no packet or snapshot is required for the next
round.

The next formal round, when separately authorized, must use the existing
worktree contract above. The combined local commit is authorized; push,
installation, merge to another branch, release, version/changelog changes, and
pull-request creation remain pending separate owner decisions.
