# Reviewed library refresh evidence

## Scope and identity

The dependency refresh uses library `0.1.0.dev3` at
`2d1e62e7de6f33fa13a918a39579c6b5e74def00`. Library PR #1 merged at
`9489543ee24f338e9c6d0e3b032a1aa389986429`; its tree remains
`2352629956b4fed0d4d3d0173612209674f83e64`, identical to the reviewed source.
That library candidate passed 864 source tests and 864 extracted-sdist tests on
each native macOS/Ubuntu Python 3.12/3.14 CI combination, plus isolated wheel checks
([run 38635251129](https://github.com/codefoundry-io/triad-dispatch-lib/actions/runs/38635251129)).
Those are library results, not Codex host or provider proof.

Codex task commit `1c365febb588f13c2c328da76775f0deca6ce8da` refreshes the bundle
and adds a host regression. Existing facades consume JSON, verdict/binding,
roster and prompt semantics. The host does not adopt the library review scheduler.

- Built wheel SHA-256: `df1e84b56a7238bab2a019064c850c30bde5b6b15268a81a1e74d76df0c187b8`.
- Independent complete-content pin: `ccc38ebfa4f7af4151da8fa51ddd1e60d9af01e4b25c98f8742af919ce224846`.
- All 23 managed package/license files match exact Git source bytes and wheel
  contents. Only `dispatch.py` changes (+5/-2); the other 22 files and three
  bundle IDs are unchanged. The package remains unpublished.

## Transition and task verification

The old generated tree was verified under its old independent pin. The unchanged
vendor CLI generated the new bundle in an owned empty stage after source-byte
comparison. Old managed bytes and verifier were rechecked immediately before
replacement; the complete new tree passed the new independent pin afterward.
No generated source was hand-edited and no old-tree conflict check was bypassed.

The regression observed an owned callback still pending after overflowing wait
setup on the old bundle (RED: one failure). It checks before event-loop shutdown
and settles any leaked test task. The updated bundle passes it and the related
adoption, integration, toolkit-input, runtime and distribution-verifier tests:
76 passed in 9.89 seconds. `vendor_library.py --check` passed.

The public isolated runtime verifier passed on macOS 26.6.2 arm64/Python 3.12.13:
four routes, 24 binding refusals, three overflow refusals, one duplicate refusal,
no skips, and temporary-root removal confirmed. An initial direct invocation of
the private probe lacked its isolated dependencies; the supported public verifier
created its own environment and passed. No dependency or source workaround was made.

An independent Sol 6.1/high task review returned Spec PASS / Quality PASS, with no
actionable findings. It independently compared all 23 managed files, wheel RECORD,
pins, stage and frozen task bytes, without executing candidate code or tests.
Task artifacts and that report are retained in the owner's ignored review/SDD
workspace; these observations do not replace full host verification or formal review.

## Integration gates

After the implementation and release-documentation writers stopped, the complete
host suite passed on macOS 26.6.2 arm64 / Python 3.12.13: **2535 passed, 4 skipped
in 602.05 seconds**. The four existing skips cover two AGY JSON-schema transport
cases and Gemini CLI model/effort contracts. The invocation exported its own
canonical TMPDIR before Python started, used the required login shell and host
permission mode, and terminated with exit 0. Generated-content verification and
`git diff --check` also passed. Independent documentation review returned Spec
PASS / Quality PASS after correcting a stale plan approval-status statement.

The 0.2.561 source candidate additionally updates release metadata, installation
guidance and independent Claude/Google-route handoffs. Native Ubuntu/archive CI,
a fresh complete four-model formal review, release and installed
fresh-session exposure are separate gates. The earlier PR #44 round failed because
a required Claude verdict was unavailable; it grants this candidate no admission
credit. Results for the current candidate must identify their commit and platform.
