# Codex shared-library adoption evidence

This records evidence available when the source review basis was frozen.
[Codex PR #44](https://github.com/codefoundry-io/triad-codex-dispatch/pull/44)
records subsequent native CI and formal review outcomes. No release, global
install or fresh installed-session claim.

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
| Dedicated GREEN, before readiness correction | Strict JSON probe passed; full host suite 2515 passed, 4 skipped in 572.78s; four skill validators and vendor check passed |
| Readiness correction RED | 6 expected failures: 3 missing/damaged bundle cases, 2 missing dependency API cases, 1 archive inventory case |
| Readiness correction focused GREEN | 10 bootstrap checks and 13 distribution/runtime checks passed; real-dependency readiness exited 0 |
| Fresh dedicated GREEN after readiness correction | Strict JSON passed; complete bootstrap and transaction suites 338 passed, 0 skipped in 148.24s; four skill validators and vendor check passed |
| Formal-review cache publication reproduction | 2 failed, 30 passed before correction; real CPython import paused at atomic replacement |
| Cache publication correction | 40 focused tests passed in 0.60s; generated-content check passed |

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

Task 3 review identified a P2 gap: bootstrap readiness checked external schema
APIs but did not exercise the bundled package. A temporary copied host reproduced
exit 0 with the entire package missing and with damaged implementation bytes.
Commit `bfd19a3` reuses the existing verified import boundary and exercises all
three bundled resources before persistent setup writes. It separately checks
the `Resource`/`DRAFT202012` dependency APIs. Damaged packages receive restoration
guidance; missing external dependencies retain the owner-terminal installation
guidance. No automatic install or launcher ownership change was introduced.
The original successful full suite above predates this correction; final native
CI reruns both complete source and archive suites on the corrected candidate.

The exact committed `e247634` archive also passed the fresh-venv four-route smoke
on native macOS. Every import originated under that extracted host's `bin/`.
The environment, source archive and extraction were removed after terminal
completion. That smoke predates the bootstrap-only correction; native CI covers
the final corrected archive separately.

The second dedicated executor observed unchanged runtime, test and skill hashes.
Its broader manifest detected the concurrent workflow-only commit `75688f6`;
that CI configuration change is explicitly excluded from its frozen runtime
claim. It did not rerun the unrelated complete host suite.

Initial native Ubuntu CI at `02f82a5` returned 12 failed, 2501 passed and 6 skipped
in 812.49s. The failures came from a missing `/bin/zsh` and CI installing
dependencies only in the parent test venv while child `python3`/bootstrap used
the action's base runtime. The workflow now installs zsh on Ubuntu, installs
test dependencies in the action-provisioned job Python and verifies parent/child
interpreter identity. Isolated runtime probes retain their separate fresh venvs.
No product permission or runtime selection contract was changed. Final CI runs
the full source and archived suite again; its result is recorded in the PR.

The first formal round reviewed `b80d08e`. All four producers started before
collection; all reached terminal state, and the fresh post-review fingerprint
matched. Google Pro and Flash returned `SAFE`. Native Sol/xhigh returned
`NOT-SAFE` for a concurrent CPython bytecode publication race in the host's
generated-package verifier. Claude returned API 429 without a verdict, so the
round's gate is failed despite valid custody. Its available results are advisory;
the corrected source still requires a new complete formal round.

The Sol finding was reproduced with a real CPython 3.12 import paused immediately
before its atomic cache replacement. Both a present `.pyc.<numeric-id>` temporary
file and its disappearance between enumeration and `lstat` caused false refusal.
The correction retains the existing final `.pyc` exception and additionally
tolerates numeric-suffix CPython temporary files for the bundled modules,
including their disappearance during publication. Existing links, special files,
unexpected files and changed generated payloads remain rejected. The generated
library bytes and approved content pin are unchanged. These deterministic tests
intercept the real publication boundary; they are not a timing-based stress run.
The original independent Task 1 reviewer inspected the frozen correction and
relevant consumers, found no new issues, and confirmed unchanged scoped hashes.
This scoped source review does not substitute for the new four-leg formal round.

Google Pro's non-blocking request to remove the roster compatibility facade was
declined after checking its actual adapter consumer. The proposed direct call
would validate host display metadata against a schema that disallows extra
properties and would omit retained host guards. The existing signature therefore
remains; this is not an unresolved correctness defect.

## Final evidence and limits

The PR records the final native Ubuntu/macOS CI and whole-branch/formal review
against this source basis, including exact commits and any failed attempt.
Preserved untracked translation/history documents prevent claiming a clean local
release checkout; the existing verifier's clean-source rule remains intact.
Clean native CI runs that verifier against committed source and records its
archive hash and full regression results. Offline facades and installed runtime
probes do not establish authenticated behavior for all four provider routes.

No actual global installation, fresh installed-session exposure, package
publication, host release or final merge has occurred. Claude receives only the
[independent port handoff](../handoffs/claude-library-adoption.md).
