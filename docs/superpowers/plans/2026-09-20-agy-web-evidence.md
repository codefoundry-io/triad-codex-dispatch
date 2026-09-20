# AGY web evidence implementation plan

> **For agentic workers:** Use superpowers:executing-plans. The repository leader owns source and tests; fresh dedicated executors observe RED and GREEN.

**Goal:** Make authorized AGY web investigations fetch source pages through the existing shared C29 procedure and verify actual calls.

**Architecture:** Add raw `--web` to the current wrapper. Lazily load the single shared clause from a byte-identical vendored document and append it last. Existing guards, schema handling and artifact writers consume the same final prompt.

**Tech stack:** Python 3.12+, existing pytest/Pydantic and AGY 1.2.7 native CLI.

**Spec:** Shared `prompts/investigation.md`, C29, R-INVEST and `spikes/2026-09-20-b-agy-web-evidence.md` in codefoundry-io/triad-dispatch-spec. Latest remote main checked at `2eb883fee59e66556ee7c7f87189b38231136622`.

## Global constraints

- Preserve caller bytes; append `"\n\n" + clause` after blank/read-only checks.
- Refuse formal REVIEW/preflight web combinations; no policy or authentication redesign.
- Preserve hardened redaction, raw/custom-schema behavior and provider cleanup.
- Modify only B; inspect and report corresponding A lines.
- Support macOS and Ubuntu 24.04; source correctness, live evidence and deployment are separate claims.

## Budget and review focus

One functional plan; expected production +40/-0 (40 net), novel core under 40,
two prompt assets, one wrapper and distribution manifest. Tests about +180;
documentation about +120. Review full affected consumers, not just changed lines.

Boundary cases: empty caller prompt; no read-only flag; formal binding/preflight;
missing/corrupt packaged clause; Unicode/trailing whitespace and custom schema.
Live failure risks: search-only answers, unsuccessful fetches reported as facts,
owner-denied web tools, invented citations and incorrect interpretation of a fetched page.

## Task 1: authorized web investigation

**Files:** `tests/test_agy_web_evidence.py`, `bin/antigravity_wrapper.py`,
`prompts/{investigation.md,source-manifest.json}`, `scripts/verify_distribution.py`,
English/Korean README, SECURITY and leg-contract reference.

**Interfaces:** consumes existing prompt loading/guard/dispatch/custody helpers;
produces `--web` with unchanged output/error schemas and a lazily loaded clause.

- [x] Write focused tests invoking real `main()` with only provider calls replaced;
  assert actual argv and persisted audit/failure logs, validation before provider,
  packaged-clause errors and no-flag compatibility.
- [x] Fresh dedicated RED: run `tests/test_agy_web_evidence.py`; expected missing
  `--web`/loader support. Record source fingerprint and exact terminal result.
- [x] Vendor the shared document and its digest, implement validation and:

  ```python
  if args.web:
      prompt = prompt + "\n\n" + _load_web_evidence_clause()
  ```

  Call only after rejecting empty/non-read-only/formal inputs. Extract exactly one
  nonempty terminated text fence, otherwise return argument error before AGY.
- [x] Separate fresh GREEN: focused and complete regressions, skill validator and
  provider-free lifecycle. Run Ubuntu 24.04 regressions with executable temporary storage.
- [x] Live paired controlled investigation using existing CLI/auth and scoped
  logs: compare page-fetch events/citations, independently verify factual claims,
  record failures rather than changing policy to force success.
- [ ] Complete required multi-family review of all current bytes; root validates
  findings, fixes only reproduced defects and reruns a full round after changes.
- [ ] Commit, verify clean distribution, push branch/PR and update shared handoff
  with source lines, commands, results and limits. Final merge/deployment remain
  separate from source verification.

## Verification before review

Fresh RED observed 18 expected failures. After the fix, focused checks passed
37 tests; skill validation and the provider-free lifecycle succeeded. Three
distribution-fixture failures were corrected by listing the two newly hashed
prompt assets in the synthetic fixture inventory. A separate fresh GREEN then
passed all 1,348 macOS tests; Ubuntu 24.04 passed 1,346 with two existing
case-insensitive-filesystem skips.

The one-pair live experiment observed completed page fetches increase from 1 to
12. The after answer reported UNSURE for incomplete evidence. Two delivered
page bodies were strict prefixes of the official sources; the vendor truncation
cause remains unisolated. This completes the planned measurement, not a claim
that all web research is now correct. The shared spike records that residual.
The owner rejected adding a permanent web-evidence store; ordinary masking and
failure logging remain. Source review, archive verification and integration are
separate subsequent steps.
