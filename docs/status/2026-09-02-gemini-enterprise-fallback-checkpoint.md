# Gemini Enterprise fallback release checkpoint

## Behavioral claim

For an owner-selected `gemini-enterprise` authentication class, formal Google
review prefers AGY and selects the already installed Gemini CLI only when AGY
is absent before any family starts; the selected route never changes later in
the round. `personal-google` continues to require AGY.

## Review-unit sizing

- Classification: S/M with the owner-approved 500-1,000-line extension envelope.
- Current production net delta: 988 lines across `.codex-plugin/`, `bin/`, and
  `scripts/` relative to the implementation base.
- Novel deterministic core estimate: 260-290 lines.
- Behavioral claims: one.
- Extension rationale: code above the 500-line target is bounded validation,
  receipt custody, fail-closed policy checking, bootstrap wiring, and required
  error handling inside the same approved fallback design. It adds no second
  authentication route, provider retry, dispatcher, semantic model, or later
  route-switch decision.

## Release boundary

- Route selection, preflight, render, and dispatch reuse the packaged Python
  wrappers and `review_round.py`; there is no new long-running process or
  dispatcher.
- AGY preflight proves the exact required model slug from the selected
  executable's tab-separated catalog. The canonical preflight receipt SHA,
  model, and effort enter every family digest, and formal dispatch rejects
  argument drift before probing or provider submission.
- Gemini formal fallback uses explicit `-m auto`, requests Plan Mode, and relies
  on the packaged mode-independent read/search-only policy as its enforcement
  boundary. Effective approval mode and runtime model identity remain
  `unexposed` unless the CLI supplies authoritative evidence.
- Provider authentication, account selection, and user-global configuration
  remain outside product mutation scope.

## Current deterministic evidence

- Focused RED: missing AGY catalog admission, exact AGY route validation, and
  preflight-digest custody failed causally under fresh behavior-only executors.
- Focused GREEN: 10 targeted cases passed after the bounded correction.
- Permission-guidance RED: two focused cases failed while public guidance still
  recommended unrestricted host access. A separate fresh executor then passed
  the corrected three-case selector under `workspace-write` / `on-request`.
- Full repository suite: 671 tests passed on the final integrated candidate.
- Both skill validators and the plugin validator passed.
- Ruff passed for every changed Python source and test path. `git diff --check`
  and `bash -n scripts/bootstrap.sh` passed.
- Prompt lint completed for the changed skills, references, agent prompts, and
  plugin prompt. Exact runtime compatibility pins and fail-closed safety
  negations were retained; independent semantic prompt review remains a release
  gate.

Clean-HEAD distribution verification, independent review admission, push,
release publication, and fresh-process installation proof remain later gates.
