# Codex adoption of the shared TRIAD library

The owner approved applying `triad-dispatch-lib` to Codex first. Claude remains a
separate implementation and release; provide a handoff document for its owner.

## Boundary

Adopt library `0.1.0.dev3` from commit
`81748d721e56dfc3463888f02328902e18398600`. The specification now lives in that
repository's `spec/` tree. Preserve existing schema identities and explicit v2
selection. Legacy review selection, native spawning, provider authentication,
model/effort resolution, Gemini noninteractive workaround, AGY stream exceptions,
custody and cleanup remain Codex responsibilities. No MCP or SDK migration.

Use a generated, byte-identical library package under `bin/triad_dispatch_lib/`.
This is distribution vendoring, not a fork: common semantic edits belong in the
library repository and arrive through a verified refresh. Build from the exact
clean library commit, retain wheel SHA-256, source commit, package version,
per-file hashes and the three bundle IDs in a separate adoption record. Retain
the MIT license. A refresh checks prior managed hashes before replacement and
refuses local changes or unexpected files. Read-only verification checks the
complete generated tree. No package installation occurs during runtime.

This fits the existing Python 3.12+ host dependency installation contract.
Align `referencing` to `>=0.37,<1`; retain Pydantic and jsonschema constraints.
Do not introduce a new environment manager or alter launcher ownership grammar.
Dependency readiness and archive replay must exercise the bundled package.
The existing runtime dependency/site-package limitations remain documented.

## Delegation of deterministic behavior

- `validate_v2` delegates strict JSON and original-verdict validation to the library.
  Keep host contract loading for receipts and phase compatibility, including its
  integrity checks; do not silently accept damaged old compatibility assets.
- `verdict_v2` keeps its Pydantic/CLI projection interface and delegates binding
  validation. Schema generation consumes the library schema after host checks.
- `review_roster` retains canonical path/file checks, placeholder preflight and
  display metadata; the library owns validation and merge behavior. A display
  command may still show zero enabled entries; execution refuses them as before.
- `review_prompts_v2` retains packet/scope/preflight metadata checks and complete
  bound schemas; the library renders host B clauses and fenced residual data.
  Existing asset verification remains a compatibility guard. Do not duplicate the
  residual caveat or pass extra replacement keys.
- Existing wrapper output already contains final verdict JSON. Feed that JSON to
  shared validation after host terminal guards. Do not relabel it as original
  provider envelopes or remove AGY/Gemini workarounds.

The vendored package and adoption record live below directories already included
by `_toolkit()`. Tests must prove mutations of implementation and resource bytes
invalidate a bound basis. No external installed copy may override the adopted
package on the normal script path. Contract failures fail closed; they must not
become successful ballots or retries.

## Evidence and release

Run host baseline and focused regressions with an owned TMPDIR, then the full
host suite. Verify generated-package integrity and replay the committed archive
with isolated dependencies on native macOS and Ubuntu CI. Preserve intentional
untracked documentation in the existing worktree; do not weaken the clean-source
release verifier to hide it. An exact committed archive can supply CI evidence.

Record source adoption separately from global installation, native provider
success and release. Library PR #1 is still unmerged/unpublished, so this is a
dependent host candidate. Existing independent review and release gates remain.

## Size estimate

Novel production code: 180–300 added lines for vendoring/integrity and thin
adapters; 100–180 deleted duplicated lines. Generated library bytes are reported
separately. Tests: 120–220 lines; documentation/CI: 150–250 lines. Preserve one
coherent adoption plan and perform its required review before any later plan.

Implementation update: non-generated production Python changed by 544 additions
and 123 deletions (net +421), including a 154-line isolated distribution probe.
The verified-package helper and refresh tool account for 223 new lines. This
growth supplies the approved reproducibility and isolated-distribution checks;
it includes the bootstrap readiness correction and adds no runtime environment
manager or provider mechanism. Generated library
code/assets are 22 unchanged files (81,160 bytes), reported separately.
