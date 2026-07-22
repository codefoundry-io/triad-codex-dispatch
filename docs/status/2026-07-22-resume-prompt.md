# Triad Codex Dispatch restart prompt

Start the new Codex session with saved project root exactly:

`/Users/chaniri/codex_workspace`

Then paste the fenced prompt below.

```text
Resume triad-codex-dispatch from its authoritative 0.2.527 post-install
checkpoint.

Development root:
/Users/chaniri/codex_workspace

Product repository:
/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability

Read first, in order:
1. /Users/chaniri/codex_workspace/AGENTS.md
2. /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-07-22-current-state.md
3. /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability/docs/status/2026-07-22-resume-prompt.md

The first turn is an evidence-only installed-skill test. Do not modify source,
~/.codex, ~/.zshrc, plugin installation, Git state, or provider authentication.
Do not commit, push, remove, reinstall, or repair anything yet.

The owner installed the managed codex-triad shell function and started this new
session to test it. Preserve the owner's existing approval configuration:
approval_policy=on-request and approvals_reviewer=auto_review. Never set
approval_policy=never. The known defect is that the generated triad profile
currently says approvals_reviewer=user; test and report this fact rather than
silently changing it.

Prove, using live current-session evidence:
1. Whether this session has the codex-triad environment pins
   TRIAD_WRAPPER_ALLOWED_ROOTS, TRIAD_WRAPPER_HARDENED=1, and
   TRIAD_CLAUDE_ENFORCE_SANDBOX=1. Read only; do not print credentials or the
   full environment.
2. The exact effective approval_policy and approvals_reviewer source values
   from the base, workspace, and triad profile files. Read only the named keys.
3. Whether all four installed skills are exposed in this fresh session:
   triad-antigravity-dispatch, triad-claude-dispatch,
   triad-cross-family-review, and triad-gemini-dispatch.
4. Use the native spawn surface with agent_type exactly
   triad-repair-analyzer and a unique task name. Give it a controlled nonexistent
   /private/tmp run_log_path and the installed 0.2.527 toolkit_root. It must
   return the bounded escalate/proposal:null result. Do not use codex exec, a
   generic agent, an alias, or a prompt-only role claim as a substitute.
5. Invoke the installed triad-antigravity-dispatch skill for one minimal real
   token-using smoke call through the owner's already authenticated AGY route.
   Ask the provider to return exactly TRIAD_SKILL_OK. Do not log in, copy
   credentials, change provider settings permanently, or use the Gemini
   Enterprise fallback unless AGY is genuinely unavailable.

Run provider/Python operations in the owner's normal terminal boundary as the
installed skill specifies. The skill invocation must perform its normal
best-effort cleanup of managed temporary IPC older than 3,600 seconds. Do not
broaden the test into a formal four-leg review.

Report a compact evidence table with session pins, config values, skill
exposure, exact selector proof, AGY smoke result, and any approval prompt that
actually occurred. Reconcile ambiguity as leader. Stop after the report and ask
the owner whether to proceed with the bounded profile-inheritance repair. Do
not implement that repair in the test turn.

Preserve the unrelated dirty checkout at /Users/chaniri/triad-codex-dispatch.
The authoritative product branch is codex/triad-reliability-redesign at commit
177c9901d3e43b10f3736742455ad8da70068bed plus this handoff-only commit.
```
