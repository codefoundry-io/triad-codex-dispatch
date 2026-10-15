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

Native [CI run 38654506055](https://github.com/codefoundry-io/triad-codex-dispatch/actions/runs/38654506055)
passed for candidate `2d646bc20ee5495d05524c6b61d4c36b0f967295`. Both job logs name
synthetic merge `a9e05737231109599f23dc5e936c39840dc547fa`; its parents are the
candidate and `bd96cdbf0eb83e2187b2b7fa3ac9cd701b58db7e`, and its tracked tree
`52cc9cb596085d5344b858dfeb7073debb269f97` equals the candidate tree.

| Native runner | Runtime | Source tests | Extracted archive tests |
| --- | --- | --- | --- |
| Ubuntu 24.04 x86_64 | Python 3.12.15 | 2533 passed, 6 skipped | 2533 passed, 6 skipped |
| macOS 15.7.9 arm64 | Python 3.12.10 | 2535 passed, 4 skipped | 2535 passed, 4 skipped |

Ubuntu additionally skips two tests requiring a case-insensitive filesystem.
Both source/archive isolated runtime probes passed, including all 24 binding
refusals and temporary-root removal. The two jobs produced archive SHA-256
`a6fb34d8a58bf4aa831ef5ca74a52d48502191c05aa02b645f6b7af4ed9792f1`
for that synthetic merge. This is evidence for that immutable tree, before the
follow-up corrections below, not a release artifact or fresh installed-session
claim. The corrected candidate requires its own native CI.

## Follow-up review corrections

The public v2 round at Codex `2d646bc20ee5495d05524c6b61d4c36b0f967295`
completed Opus, native Sol and AGY Flash reviews, each with `SAFE TO MERGE`.
AGY 1.3.5 rejected the selected Pro model/effort before a verdict, so the collector
reported `INCOMPLETE`; these three votes do not authorize admission. Collection
rechecked source/custody integrity, and the terminal round was exported before
its exact managed root and selector stage/cwd were removed. Its findings remain
part of the next review's evidence.

Sol identified a host encoding gap: canonical filesystem paths may contain CR/LF,
but the shared renderer requires caller-encoded single-line replacements. Twelve
new cases first failed on the old host: eight CR/LF paths were refused by the
shared renderer, and four quoted-path cases exposed missing JSON encoding.
The correction JSON-string encodes only worktree, brief and gated-patch display
values. Tests check lossless path decoding, single-pass placeholder handling,
complete clause placement and unchanged native argv; no provider read-fidelity
claim follows from these source tests.

Claude's four Minor findings were independently checked. Legacy metadata and
web-clause helpers do transitively use the verified shared parser; current
English/Korean/security guidance now states this dependency while preserving
deliberate integrity exceptions. The old design is labeled historical and linked
to this record. All four compatibility prompt files and the phase schema are
identical to the adopted bundle today; five regression cases guard future refresh
parity without adding a new runtime mechanism. Same-pin vendoring can rewrite
files and update rebuilt-wheel provenance, but cannot migrate pins; its docstring
now says so. The unreachable removal branch is a nonfunctional cleanup suggestion
and is left unchanged.

The corrected source passed 168 focused tests in 125.41 seconds, including all
12 path regressions and five resource-parity checks, on the same macOS/Python
runtime with an owned canonical TMPDIR. Independent Astra/high scoped re-review
found no actionable issue; this is separate from the required formal vote.
The first full follow-up run had 2551 passes, four existing skips and one stale
test assertion expecting an unquoted prepared-directory path. That assertion
now decodes the JSON path and compares its original identity while retaining the
adapter cwd assertion; all ten runtime-boundary tests passed in 9.43 seconds.
The final full replay passed **2552 tests, with four existing skips, in 619.65
seconds** on macOS 26.6.2 arm64/Python 3.12.13. The invocation used a new owned
canonical TMPDIR, retained the failed earlier run, and terminated with exit 0.
Generated-package verification and `git diff --check` passed as well. The
corrected source still requires native CI and an entire new formal round.
The owner selected `opus`/xhigh with 40 minutes and approved
Argon/high in place of unavailable Pro, retaining Sol 6.1/xhigh and Flash/high.
This per-round choice changes no standing model defaults. Release and installation
remain separate gates.

## Second follow-up adjudication

The next public v2 round reviewed `d5dce32422c20497798cc2dbe19f4faec5101e1d`
with the owner-selected Opus alias, Sol 6.1, Argon and Flash. All four returned
`SAFE TO MERGE`; canonical collection returned `AGREED` with no missing leg.
The collector verified source/custody integrity, and the terminal round was
exported before its managed root and selector stage/cwd were removed. This
approval applies to that source only; the corrections below require a fresh round.

Sol identified two older assertions that compared raw filesystem spelling with
JSON-encoded prompt paths. This is a verifier/test defect, not a production
encoding failure. The correction compares encoded path tokens, preserving native
path comparisons; the regression invokes the supported public verifier from a
fresh process with a canonical temporary path containing Hangul, quotes and a
backslash. It does not substitute the private probe or inject a dependency site.
The public-driver case and all three family assertions first failed on the old
checks (four failures in 3.35 seconds); after correction, all 88 affected tests
passed in 14.99 seconds on macOS/Python 3.12.13. The public-driver report confirms
all four routes, 24 binding refusals, three overflow refusals, one duplicate
refusal, exact supplied-host origins and removal of its temporary environment.

Claude's inventory diagnostic finding was independently confirmed: missing or
unexpected paths were known but omitted, and bootstrap hid the verifier cause.
Five regression cases failed on the old messages. The host now reports sorted
relative missing/unexpected names or the unexpected directory, JSON-escaped to
keep filenames on one diagnostic line. Bootstrap retains the narrow verified
library cause and restoration guidance. Twenty-one focused tests passed in 1.66
seconds, including refusal, conflict preservation and dependency-readiness cases.
No generated library bytes, pin, admission decision or automatic repair changed.

The schema diagnostic suggestion reflects an intentional pinned API tradeoff:
stable codes and fixed messages omit JSON location/validator details. Revalidating
in the host would duplicate the shared semantics. Both handoffs now record this
limit and direct any required extension to the shared contract. The provider-path
finding supplied no actual native read failure; retain ASCII JSON encoding and
the explicit lack of provider read-fidelity proof. Flash's repeated unreachable
same-pin removal-loop suggestion adds no functional counterexample; its original
diff-like line number is preserved in custody, with actual source lines 91–92
recorded in adjudication. No unrelated vendor migration is introduced.

After both corrections, the complete host suite passed **2558 tests, with four
existing skips, in 631.58 seconds** on macOS 26.6.2 arm64/Python 3.12.13. The
invocation used an owned canonical TMPDIR and terminated with exit 0. The
generated-content check and `git diff --check` also passed. Independent
Astra/high scoped re-review found no actionable issue in the implementation,
regressions and handoffs; that read-only review is separate from the formal vote.
Native source/archive CI and the fresh complete formal round remain required for
this corrected candidate. No publication or installed-session proof is claimed.

## Third follow-up adjudication

The public v2 round at `06e3777860f4fafe68705c6367e4454476e2d00f` completed
all four owner-selected reviewers with `SAFE TO MERGE`; canonical collection
returned `AGREED`, verified integrity and found no missing leg. The round was
exported and its exact managed root and selector stage/cwd were removed.

Claude identified a non-blocking cost in the new public-driver pytest case:
it provisions dependencies again during both default source and archive suites,
although CI already runs explicit public-driver checks for both. Independent
source inspection confirmed four such installations per CI job. No inspected
contract promises an entirely offline suite, and no product failure was observed.
The bounded correction retains a fresh-process encoded-path probe using the
test environment's installed dependencies and moves the real public-driver
tricky-TMPDIR assertions into those two existing native CI calls. Provisioning
failures remain failures; there is no network-based skip or extra test mode.
The source/archive report checks retain root and import origins, all four routes,
24 binding refusals, three overflow refusals, one duplicate refusal, roster names,
no skips, temporary-parent identity and verified cleanup.

The fixture includes a literal backslash followed by `n`, not an actual newline.
Argon's original review wording is preserved in custody and qualified by the
leader's adjudication. Actual CR/LF paths are covered separately by the renderer
regressions. Neither kind of source test establishes native provider tool-read
fidelity. This follow-up changes test placement and documentation only; it keeps
production code, library pins, model defaults and installation behavior intact.

The fresh probe regression failed with the old raw-path assertion (one failure
in 0.45 seconds) and passed after restoring the encoded-token assertion. All
three runtime-verifier tests then passed in 3.83 seconds; YAML parsing and the
extracted workflow's `bash -n` check passed. The complete suite passed **2557
tests, with four existing route skips, in 614.35 seconds** on macOS 26.6.2
arm64/Python 3.12.13, using an owned canonical TMPDIR and exiting with status 0.
The test count decreases by one because the default probe now covers the special
path and the duplicate provisioning case is removed. Generated-content and
whitespace checks passed. Independent Astra/high scoped review found no
actionable issue. Native source/archive CI and a fresh complete formal round
remain required for the final candidate; publication and installation are not
claimed by these source results.
