# Published dev4 adoption evidence

The Codex host refreshes its bundled library from dev3 to the published
[v0.1.0.dev4 artifact](https://github.com/codefoundry-io/triad-dispatch-lib/releases/tag/v0.1.0.dev4).
The source identity is `087af94a7078de0ae9701fb057840b5492f51f66`; later library
main changes are not substituted into this bundle.

| Identity | Value |
|---|---|
| Wheel SHA-256 | `c5bfdf10c4ce81f431ec7f77106e4d77b1556ac9c7b6b01bdb6616f988e8b2cc` |
| Source archive SHA-256 | `1ff4f11124544301d07883c104a2cb833c71786a1833ce06c7d0ca2b092e8c4c` |
| Independent package/license content pin | `5cf26be0ab354c0565ade6d5f04971ff3689a6188b648d70edcffd6474b5c1f2` |
| Managed files | 26 |
| Resource bundles | verdict, roster, prompt, receipt |

Both release assets match the published manifest's size and SHA-256. Every
wheel package/license byte matches Git objects at the exact tagged source.
The old tree passed its old independent pin before staging; the new package
was generated and verified in an owned empty directory. Old managed bytes
were rechecked immediately before replacement, followed by complete new-tree
verification. Generated library files were not hand-edited.

The host adds the receipt module and bundle to integrity and archive inventories.
Existing facade calls and their default return values remain compatible. New
library diagnostics, split roster functions, prompt manifests and receipt APIs
ship as upstream package content; this update does not change host execution,
model/effort defaults, the Gemini workaround or the scheduler. Python 3.12+
and runtime dependency requirements remain unchanged.

## Local verification

macOS 26.6.2 arm64, Python 3.12.13, pytest 9.0.3. Python/tests ran through the
login shell with a separate canonical invocation-owned TMPDIR set before
Python started.

- Seven receipt inventory tests failed against the old bundle, then passed
  after the refresh. Focused adoption, distribution, integration, toolkit,
  verdict, roster and prompt tests: **295 passed**.
- Missing/tampered receipt module, manifest and schema are rejected by package
  and distribution verification; receipt CPython atomic cache files are allowed.
- The public isolated runtime verifier installed requirements in a fresh venv,
  imported the exact supplied host and dev4 package, and exercised all four
  route labels. It confirmed 24 binding refusals, three overflow refusals, one
  duplicate refusal, the four-entry roster, no skips and temporary-root removal.
  These are provider-free facade tests, not provider inference results.

The selected source worktree contains pre-existing untracked owner documents.
They are preserved in place. The clean-source archive verifier is run by native
macOS/Ubuntu CI; local artifact identity can be checked against immutable Git
objects without removing those documents or creating another source checkout.

Full-suite, exact candidate CI, formal review, release and installation outcomes
are recorded in the update PR and release evidence. This source record does not
assert those later outcomes. Other hosts consume the library's
[adoption guide](https://github.com/codefoundry-io/triad-dispatch-lib/blob/v0.1.0.dev4/docs/host-adoption.md)
and released artifacts under their own deployment process.
