# C16/C27: Gemini version preflight and observed-version custody

Baseline B `d3ae06894658e3c7a7ea8ac6560233147957a187` after P3b; shared remote
main `2eb883fee59e66556ee7c7f87189b38231136622` fetched at planning. Close the
original codex-09 floor omission and C27's missing Gemini observed-version field.
C27 is an existing requirement, not deferred shared transport-schema work.

## Bounded implementation

Use the selector-pinned executable, current cwd and scrubbed formal environment
for a provider-free `--version` probe capped at 15 seconds before the existing
help capability probe. Refuse missing, ambiguous, malformed, failed or too-old
version output; retain the current argument-error exit and no-provider boundary.
Require CLI >=0.34.0. Preserve policy validation, help capability checks, route,
authentication and raw/custom invocation behavior. Do not change model choice.

Record the exact accepted SemVer string as `gemini_version` in the existing
private preflight JSON. The receipt validator uses the same Gemini-specific
version check. Its existing canonical receipt hash already binds the version
into every rendered basis; no dataclass, public result wire, roster, selector
field or generic version framework is required. Older receipts regenerate.

Use standard SemVer precedence: 0.34.0-rc.1 is below 0.34.0; build metadata does
not affect ordering; a higher core such as 0.34.1-rc.1 exceeds the floor but must
still satisfy the existing capability probe. Evidence: https://semver.org/spec/v2.0.0.html.
The installed pinned-path observation on this host is `/opt/homebrew/bin/gemini`
printing `0.60.0`; this is CLI metadata only, not inference or enforcement proof.

## TDD and review

Leader writes source/tests; independent fresh Terra/high executors observe RED
and GREEN. Test below/equal/above floor, prerelease/build precedence, malformed
or multi-version output, timeout/OSError/nonzero probes, exact ordered pinned
version/help calls, scrubbed environment, receipt version validation and digest
binding. Preserve raw invocation and existing negative-help cases with updated
fixtures. Full macOS/Ubuntu 24.04 suites, source validator/lifecycle and complete
fresh multi-family gate precede integration. V1–V5 remain separate.

Expected production delta <=60 additions/10 deletions, novel core <=45, in
gemini_wrapper.py and review_round.py. Existing receipt fixtures and relevant
EN/KO/security/source-reference text change together; tests/docs counted separately.

A remains read-only at `92c8afd500499d8736afcc28b39a87a4f87fed50`:
`3rd-Agent/wrappers/gemini_wrapper.py:158` resolves the executable and starts
building the command at :169 without a Gemini version/help preflight. Record an
A-specific later handoff; do not edit its wrapper or import a new common framework.
