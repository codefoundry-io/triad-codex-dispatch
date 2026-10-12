# Codex shared-library adoption evidence

Status: implementation and verification in progress; no release, global install
or fresh installed-session claim.

## Source identity and scope

- Host base: `bd96cdb` (the existing v0.2.560 source after PR #43 merge).
- Host branch: `codex/shared-library-adoption`, existing reliability worktree.
- Library: `0.1.0.dev3`, clean source commit
  `81748d721e56dfc3463888f02328902e18398600`.
- Fresh wheel SHA-256:
  `13ab1518aafa44ad67cf0b8793148d2cd8c434ba83b11b11ee9ccdf60b8060fe`.
- Approved complete package/license inventory digest:
  `d91f0caa3438ea1698d322a9ccf67106d932d4b706b5539797164ffe772fea10`.
- All 22 generated package files (81,160 bytes) and the MIT license compared
  byte-for-byte with that clean source and the built wheel. The upstream library
  tracked tree stayed clean. Source/build identity is recorded evidence, not a
  signed publisher attestation.

The port changes Codex's explicit v2 deterministic paths. Provider/native
mechanisms, existing stream exceptions, Gemini workaround, legacy selection and
Claude's separate implementation remain outside this change.

## Local verification

Environment: native macOS, arm64, Python 3.12.13 at
`/opt/homebrew/opt/python@3.12/libexec/bin/python3`, pytest 9.0.3. Python/tests/builds
used `/bin/zsh -lic` with `sandbox_permissions="require_escalated"`; test processes
received an owned canonical TMPDIR before Python startup.

| Check | Result |
| --- | --- |
| Task 1 initial functionality RED | 8 failures before implementation |
| Task 1 approved-content regression RED | 3 failures for self-consistent altered code/license and rewritten target+metadata |
| Task 1 final focused suite | 26 passed; nonwriting check and conflict preservation included |
| Baseline run overlapping Task 1 writes | 2461 passed, 4 skipped, 1 failed; not a clean baseline pass |
| Exact failed baseline parameter group after writes stopped | 11 passed, 32 deselected |
| Fresh dedicated strict-JSON source RED | exit 1: first numeric overflow accepted; normal finite JSON accepted |
| Task 2 integration RED | 14 expected failures before facade delegation |
| Task 2 focused host regressions | 503 passed, 4 skipped in 284.50s; exit 0 |
| Task 3 distribution and isolated-driver focused tests | 13 passed in 5.27s |
| Fresh binary-only environment, source host | Four routes; 24 binding swaps rejected by both validator and producer; 3 overflow and 1 duplicate-key refusals; correct bundled import origins |

The baseline failure was the expected custody refusal when
`bin/library_adoption.py` changed between basis preparation and allocation. The
saved basis comparison identified exactly that changed toolkit file and an
unchanged roster. No product workaround or weakened integrity check was applied.
Final regression must run with all toolkit writers stopped.

Task 2's four skips are existing parametrized wrapper cases for inapplicable
AGY/Gemini routes, not missing-provider skips. Its focused manifest covers the
library integration, roster, verdict producer/validator, prompts, toolkit
fingerprints, rounds/custody and unchanged adapter/wrapper consumers. It does not
replace the final full regression suite.

The RED executor explicitly read the canonical source skill and v2 reference.
Source realpath matched its configured target; skill and `validate_v2.py` hashes
were unchanged during execution. Requested `gpt-6.1-sol/high`; effective settings
were `UNEXPOSED`. Its exact temporary directory was removed after terminal exit.
This is bounded behavior evidence, not an operational provider review.

## Independent review

Task 1 was reviewed by a fresh Sol/high reviewer. Its P2 finding showed that a
self-consistent wheel could claim the approved commit while changing implementation
or license bytes. Commit `e1dae12` adds an independent approved-content digest pin
checked before writes and during installed-tree verification. Scoped re-review
cleared the finding with no new breakage. Reviewers were prompt-controlled read-only;
before/after source state was checked. No hidden effective model settings are claimed.

The owner explicitly replaced the currently unavailable Terra model with Sol for
this port's formal review. The requested native setting is `gpt-6.1-sol/xhigh`;
this exception changes no persistent workspace model default. The canonical
workspace ledger currently fixes the historical `codex-terra` ID, so a recorded
per-run adapter changes only that slot's requested model while retaining canonical
ledger writers, validation, all-started and integrity gates. The source helper is
hash-pinned and left unchanged; the ledger records the actual Sol model.

Task 2 received a separate fresh Sol/high review of commit `317f14f` and affected
unchanged consumers. Specification compliance and code quality cleared with no
findings. Tests were inspected but not rerun by the reviewer.

## Pending evidence

Final frozen regressions, installed archive replay,
native Ubuntu/macOS CI and whole-branch/formal review are pending. The preserved
untracked translation/history documents prevent claiming a clean local release
checkout; the existing verifier's clean-source rule remains intact.

No actual global installation, fresh installed-session exposure, package
publication, host release or final merge has occurred. Claude receives only the
[independent port handoff](../handoffs/claude-library-adoption.md).
