# Review-strategy implementation and verification — 2026-10-02

The explicit public-v2 path now selects plan or code purpose through a validated,
bound `review_kind`, and requires explicit approval from every selected enabled
entry. A nonempty one-family roster can agree; a valid Minor-only negative cannot.
Legacy entry points and exact model/JSON configuration remain distinct and unchanged.

Normative candidate: [shared 04245c7](https://github.com/codefoundry-io/triad-dispatch-spec/commit/04245c740afc9be36ad7702a134f71aec8ff0b7f).
This records source verification, not installed behavior, shared-spec admission or release.
The approved plan and its R3 approval were not repeated or edited.

## Implementation and evidence

| Unit | Source commit | Verification |
|---|---|---|
| Phase scalar/schema/shared renderer and Google consumer | `64c2e3acb6a647bddf27944ffaafd5c4897c2e02` | RED 29 failed / 203 passed; GREEN 235 passed |
| Normalized frozen request and CLI/retry/wrapper transport | `c77dbd4419b0f4d5e5ddc7332e5c6571f523cb97` | RED 19 failed / 72 passed; GREEN 91 passed |
| Every-selected-entry collector | `f2996d69ff0b76591cc8faa1c5d2ea117aca80d8` | RED 4 failed / 12 passed; GREEN 150 passed |
| Context, evidence cleanup and capability characterization | `20d0bf4cbb99f61e400544b49b491c3586b9d0bf` | 239 focused passed; 21 affected provider checks passed (overlapping coverage) |

Each unit received fresh Sol/high internal review with no remaining actionable
findings. These internal reviews do not replace the separate all-selected formal gate.
Test counts overlap and are not additive unique coverage.

- C13/C33: Minor-only negative tokens remain valid `COMPLETE` entries but block the
  round. Missing, failed and invalid evidence retain `INCOMPLETE` precedence.
  One/same-family/informational rosters participate; empty rosters refuse.
- C60: all three phases, omission default, early null/unknown refusal, exact chosen
  purpose, normalized digest and actual mocked wrapper/collector paths are covered.
  Digest comparisons control one substantive captured payload and root/review ID.
- C61/C62: Korean/escaped strings, supported/locked/observed versions and unknowns
  survive decoded transport; all selected entries receive one current residual.
  Empty residual and regular empty TASK behavior remain the existing contract.
- C20/C63: current EVIDENCE is materialized and bound before old-root export/cleanup;
  independent bytes/hash and final integrity survive. Ownership/export guards
  preserve foreign and unexported resources; the leader owns provider liveness.
- C64: separate stop/exception prose cannot produce approval; bound mutation
  invalidates the old basis. Semantic progress/reopening remain leader judgment.
- C65: later CLI versions and missing controls exercise existing seams. The generic
  Claude 2.1.205 floor is independently tested with Opus 4.6; new Opus 5.5 mocks use
  2.1.280+. AGY 1.1.20, formal Gemini 0.34.0 and v2 Gemini 0.60.0 floors remain.
  These are distinct capability/model seams, not universal runtime support claims.

Leader guidance separates mechanical binding from current prose, verifies findings,
keeps the smallest in-scope fix, preserves refutations, materializes prior evidence
and rebuilds one compact residual. New evidence is required to reopen closed points.
Exhausted wording disputes stop without approval; independent verifiable work may continue.
TRIAD does not arrange prompt/skill efficacy experiments.

## Full-platform and source verification

Tested runtime/test source HEAD: `20d0bf4cbb99f61e400544b49b491c3586b9d0bf`, with the current guidance and Sol-role
correction present. The dedicated executor captured 263 source hashes and Git status
before/after; both were byte-identical. The later report itself does not change runtime code.

| Environment | Result |
|---|---|
| macOS 26.6.2 (25G83), arm64; Python 3.12.13; pytest 9.0.3 | 1818 passed in 404.07s; exit 0; full suite once |
| Ubuntu 24.04.4 LTS, arm64; Python 3.12.3; pytest 9.0.3; uid/gid 1000 | 1816 passed, 2 skipped in 523.49s; exit 0 |
| Canonical skill validator | PASS |
| Fresh source structural observations | 4 PASS; Sol/high configured/requested; effective runtime UNEXPOSED |
| Fixed provider-free lifecycle | SUCCESS; 14/14 commands; payload/integrity verified; all four exact temporary roots removed |

The macOS suite used the owner-authorized outside-sandbox `/bin/zsh -lic`
environment and absolute checkout root:
`python3 -m pytest -q "$1/tests" --rootdir "$1" -p no:cacheprovider`.
Ubuntu used existing image `triad-schema-ubuntu24-verification:20260920`
(`sha256:db85883d3c697f7d11e7d6c821ad36fc2e67bd58b3e34814e70dcc9c97a034f2`) with a read-only source mount, no network, and
`--rm --user 1000:1000`. Its two skips require a case-insensitive filesystem;
both execute on macOS. Only arm64 hosts were tested.

Exact commands, terminal results, source snapshots, RED/GREEN reports and lifecycle
custody are retained in the ignored SDD evidence folder for this plan. The dedicated
structural RED was observed before the owner changed the executor from Terra to Sol;
that attribution is preserved and is not a same-model efficacy experiment.
Fresh execution does not prove disabled memory or inherited instructions.

## Verified corrections and limits

Internal documentation review found stale README bundle provenance and an ambiguous
conditional source-development check. Both were corrected and independently rechecked.
Task 4 corrected two new test-fixture setup errors, with complete fresh regressions;
these were not production RED findings.

Two environment failures were retained and resolved without source weakening:
the initial sandboxed macOS baseline denied `ps` (correct terminal baseline:
1686 passed), and the first Ubuntu run as root bypassed four chmod-sensitive
assertions. Those four passed with the existing ordinary Ubuntu user, followed by
the complete user-mode run above. The executor's report-writing quoting error
failed before starting another suite and was separately recorded.

Production delta from the baseline: 41 additions / 16 deletions / net +25
(including distribution inventory). Canonical payloads: +76/-41; tests: +541/-23.
There is no new environment parser, residual engine, cleanup engine or model registry.
Existing dirty work was preserved; separate owner-requested development-role changes
do not change public model defaults.

This report does not infer authenticated v2 service conformance, hidden runtime
identity, model-quality gains, Claude-host conformance, revision adoption,
installation or release. Formal current-source code review and exact-commit shared
specification review keep separate immutable receipts; prior direction/plan verdicts
provide no admission credit. Product merge/install/release remain separately authorized.
