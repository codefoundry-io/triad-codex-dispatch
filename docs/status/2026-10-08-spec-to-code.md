# Spec-to-code conformance — 2026-10-08

Historical evidence checkpoint. The single live stage, checklist and next action
now live in [spec-to-code-sot.md](spec-to-code-sot.md). Preserve this record as
evidence; do not maintain a second progress checklist here.

Current shared basis: fetched `triad-dispatch-spec` main `3afc4d7`.
Product baseline: `632f42633d3a92d6cb27168cd15c4d4debd8558c`.
Owner authorizes spec review and implementation in small coherent units,
cross-checking uncertain shared behavior against Claude source. Each host's
native leg is excluded from the other host's implementation audit and changes.
Common input/result contracts remain shared. Existing dirty work is preserved.

The October 2 implementation checkpoint predates the completed v0.2.558 release;
do not restart its already implemented review-strategy plan.

## Current unit: C43 / DL-117 quota classification

Confirmed cause: B's shared lists lack the two measured quota sentences; a
global addition would also apply to the wrong CLI. Add a small CLI-specific
built-in table through the existing list resolver, matching the established A
composition pattern. Keep extension behavior, success, timeout and exit mapping.

Scope: `bin/_common.py`, `tests/test_vendor_quota_contract.py`, this record and
the shared evidence/request document. Estimated production +15/-2/net +13,
novel core under 20 lines; tests under 70 lines; documentation separate.
No prompt, schema, native-leg, installer or global configuration change.

RED: the two positive quota cases returned `unknown` (2 failed, 13 passed).
Two redundant no-op parameter combinations were then removed.
Focused GREEN: new quota tests plus `test_exit_token_contract.py`, 40 passed.
Environment: macOS host, Python 3.12.13, pytest 9.0.3 via `/bin/zsh -lic` with
`sandbox_permissions=require_escalated`. Full suite: 1,846 passed, 4 skipped
in 397.24 seconds. Independent Sol/medium read-only review found no defect in
the bounded change; actual AGY quota carrier integration remains unmeasured.
Formal review `triad-c43-quota-20261008-r1` used the saved Astra/high owner
override. Claude, Google Flash and Astra returned SAFE; Google Pro returned
NOT-SAFE with an open AGY carrier question. Final result: NOT_APPROVED,
ROUND_INTEGRITY_OK. No result was rewritten; no next implementation unit started.

The vendor changelog confirms the quota sentence but not its stream position
or exit code. AGY's `_interpret_run` supplies only stderr/status to classification
on nonzero exit and skips it on zero-exit ERROR. The current change therefore
proves classifier-data behavior, not AGY runtime conformance. Installed AGY
1.3.1 is a Mach-O executable; the public vendor repository exposes documentation
and examples, not the implementation that would settle the path. No guessed
carrier handling or quota-exhaustion experiment was added. The shared audit
requests a sanitized carrier, exit code, CLI version and source evidence.
Claude's optional codex JSONL test suggestion remains follow-up; its existing
helper path was verified statically. Evidence is in the durable review root's
`leader-adjudication.json` and `owner-selected-review-receipt.json`.

The shared audit is in the existing specification checkout on
`codex/spec-to-code-20261008`, `decisions/2026-10-08-codex-conformance-audit.md`.
It requests Claude follow-up for the AGY quota sentence and model gates;
native Claude presets are excluded. With owner approval, commit `7cb188a8` was
published as draft spec PR #13; shared main was not changed.

## Claude reply verified — 2026-10-09

Read the maintainer reply at
`/Users/chaniri/triad/.superpowers/sdd/2026-10-08-claude-host-implementation/pr13-reply.md`.
Verified A source in the clean `impl/claude-host-2026-10` checkout at
`3b79a8e54c34f0baa86f96ae27cf2f801f127c1e`, and remote spec PR #12 at
`1a5ab9a68bce42101b150a972d80adfae1788fd7`. The reply file itself is local;
its full content is also published in [PR #13 comment](https://github.com/codefoundry-io/triad-dispatch-spec/pull/13#issuecomment-6071390137),
verified on 2026-10-09. PR #12 contains the DL-116/DL-117 status updates.
The initial check inspected PR #12's tree only and missed the PR #13 comment;
the reply is available remotely and needs no additional publication.

- `af50c468`: A's AGY-specific quota pattern exists; the exit mapping is 65.
  `tests/unit/wrappers/t14-agy-classify.sh` checks the positive phrase and
  cross-CLI negative control. These are classifier inputs, not a captured
  AGY quota event.
- `86cffe93`: A removed the AGY model-catalog call and Gemini packaged model
  gate. Verified source, `t71-agy-model-passthrough-c18.sh` P0/P1/P2,
  `t57-gemini-preflight-c16.sh` axis 12, and the export absence assertion.
  The old audit observation that A still has these gates is historical;
  B's corresponding work remains open. Native legs were excluded.
- `3626aab7`: A's `agy_classify_signals` reads the result-level error's first
  non-empty line; `_classify_no_answer` combines those signals with stderr
  and status. This is implementation evidence for supported carriers, not
  evidence that the credits sentence actually occurs in one of them.

This pass inspected source and test assertions; it did not rerun A's suite.
The maintainer explicitly confirms no captured quota event, CLI version,
exit code, channel or event field. Therefore the C43 round remains
NOT_APPROVED: the reply closes the question about A's classifier and gate
implementation, but not the Google Pro carrier question. No runtime behavior
was inferred, no next implementation unit started, and no existing review
verdict was changed. Preserve the original round and require a fresh complete
review if its evidence basis or candidate changes.

## Subsequent units, after the current required review

- R-MODEL / C34: preserve independent requested/selected identity checks, remove
  catalogue gates, then apply the measured Claude alias; model defaults for
  the native Codex leg are excluded. A's gates were removed in `86cffe93`, as
  verified in the October 9 reply above; B's implementation remains open.
- R-CLASSIFY / R-AUTH: remaining measured sentences and vendor-owned error
  carriers. The first quota correction is not complete C43 or authentication
  conformance; keep DL-117's remaining check open.
- R-CLEANUP: declarative roots and deletion ownership, preserving B custody,
  export and floor checks; separate plan because this changes lifecycle structure.
- DL-107 containment and DL-108/109 installation coexistence: inspect required
  non-native host differences and machine-wide state; no native-leg redesign.

This is a bounded initial audit, not an exhaustive disposition of all open B
rows. Refine the remaining units against source and shared cases before coding.
Each completed implementation unit receives its required multi-family review
before the next unit starts. Product merge/install/release are not authorized
by this work record.
