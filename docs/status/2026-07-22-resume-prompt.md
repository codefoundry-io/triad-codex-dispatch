# Triad Codex Dispatch restart prompt

Start the new Codex session with saved project root exactly:

`/Users/chaniri/codex_workspace`

Then paste the fenced prompt below.

```text
Resume triad-codex-dispatch from its authoritative 0.2.527 approval-inheritance
repair checkpoint.

Development root:
/Users/chaniri/codex_workspace

Product repository:
/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability

Read first, in order:
1. /Users/chaniri/codex_workspace/AGENTS.md
2. /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-07-22-current-state.md
3. /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-07-22-resume-prompt.md

Read the current-state document completely. It preserves immutable R14 history
and records the completed bounded repair plus its intentional uncommitted
final-review fixes. The local profile was hotfixed by omitting both
`approval_policy` and `approvals_reviewer`; that is local proof, not
distribution verification.

The intended source contract is:

1. Default generated profiles omit `approval_policy` and `approvals_reviewer`,
   preserving the owner's layered approval configuration unchanged.
2. A nonempty `TRIAD_CODEX_PROFILE_APPROVAL_POLICY` in `on-request`, `never`,
   or `untrusted` emits only `approval_policy`.
3. `approvals_reviewer` is never generated and
   `default_permissions = "triad_leader"` remains.
4. `TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never` remains an advanced opt-in; do
   not enable it unless the owner explicitly asks.

The recorded local proof is:

`TRIAD_LOCAL_CLEAN effective_approval=on-request/auto_review pins=3/3 skills=4/4 catalog_version=0.2.527 profile_permission=triad_leader`

Completed source evidence is:

- Workspace-root literal `python3`: Python 3.12.13; pytest 9.0.3.
- Focused bootstrap tests: 4 passed.
- Distribution contract: 52 passed.
- Final tests-directory run: 608 passed, 6 subtests passed in 125.65s.
- Task reviews: approved.
- The initial whole-diff review returned `With fixes` only for the handoff and
  test-plan findings addressed in the intentional uncommitted fix wave.
- Final frozen-artifact re-review: `APPROVED`; no Critical, Important, or Minor
  findings remained, and all supplied artifact hashes matched.

The owner authorized commit and push for this bounded repair. Git history and
remote-state changes go through the workspace's automatic security review and
may present an approval request. Version/changelog changes, reinstall, release,
and pull-request creation remain separate and pending.

Preserve the reviewed repair content and documentation state, whether it is
still uncommitted or already published. Do not modify `~/.codex`, `~/.zshrc`,
plugin installation, provider authentication, or the unrelated dirty checkout
at `/Users/chaniri/triad-codex-dispatch`. Do not invoke providers, reinstall,
remove, open a pull request, bump the version or changelog, or claim a release.

First, verify that the exact completed evidence above and the final-review fixes
remain present without rewriting `_runs/reviews/20260722-triad-reliability-formal-r14`.
The final re-review is already approved. Verify the actual local `HEAD`,
worktree, and remote branch before assuming whether publication completed. If
commit or push is still pending, the owner's authorization applies only to this
reviewed bounded repair; wait for any workspace security approval request before
continuing. Report a compact evidence table that separates the local hotfix,
tests, final review, and Git publication state. Do not open a pull request or
perform a release, reinstall, or version/changelog change without new owner
authorization.

The repair base was exact commit
`09b4c59f43d76d2b9c47b13e58bff970b9b7d819` on product branch
`codex/triad-reliability-redesign`. Verify the branch's current local and remote
commit instead of expecting the original uncommitted repair state.
```
