# Wrapper contract alignment implementation plan

> **For agentic workers:** Use `superpowers:executing-plans` for leader-owned
> implementation. Fresh dedicated Terra/high executors observe RED/GREEN;
> independent reviewers inspect the complete finished scope.

**Goal:** Align the existing wrappers' input-path interpretation and exit-token
mapping with the published shared contract without changing transport or custody.

**Architecture:** Retain the existing shared helpers and per-provider mains.
Use Python `pathlib` with one process-cwd snapshot per invocation. Add only the
three missing common mapper rows, and check the existing table against an exact
vendored test fixture. No path framework, provider SDK, scheduler or new launcher.

**Tech stack:** Python 3.12+, pathlib, JSON, pytest; existing wrappers and CLIs.

**Spec:** [Published rev-2 candidate](https://github.com/codefoundry-io/triad-dispatch-spec/blob/055204c83e57bf87eeac5b2422f2b17340f7c53b/decisions/rev-2-implementation-spec.md),
[exit tokens](https://github.com/codefoundry-io/triad-dispatch-spec/blob/055204c83e57bf87eeac5b2422f2b17340f7c53b/contracts/exit-tokens.json),
C8/C28 and R-TOKENS/R-CONTAIN. Fresh remote main remains
`2eb883fee59e66556ee7c7f87189b38231136622`.

## Global constraints

- Support macOS and Ubuntu 24.04; preserve Python 3.12 minimum.
- Preserve native Codex, Claude subprocess, both Google authentication routes,
  raw/custom-schema investigation, stdin and terminal collection, and cleanup.
- Keep review results, selector/preflight receipts and read-evidence paths under
  their existing canonical absolute-path contracts.
- D-B1/D-B2 are pending. Do not change policy bytes, redaction, exact evidence
  custody, adopted revision or the public v2 dispatch boundary.
- A is read-only. Record its matching source lines and later adoption work.
- Keep PR #35's `ec3d0df` basis unchanged while its merge approval is pending.
  This plan runs on `codex/host-parity-cli-contracts` in the existing checkout.

**Budget:** Production +35–70/-25–50, novel core under 50 lines; tests +150–240,
shared fixture about 125 lines, docs +80–140. Growth is recorded, not a size gate.

Implemented production delta: +24/-35 (net -11), novel core under 20 lines.
Tests total 261 lines: 21 over the estimate because the shared producer census
and each wrapper's pre-provider refusal matrix cover separate contract risks.
The 125-line fixture is unchanged shared data; documentation growth includes
the source-pinned A adoption instructions required for this handoff.

## Review focus

1. Common map-only tokens must not become classifier-repair targets or new
   emitted transport states (Task 1 contract and eligibility tests).
2. The same relative filename exists in caller and child directories; use the
   caller's prompt and the separately resolved child cwd (Task 2 entry tests).
3. The process cwd changes after prompt loading; retain the entry snapshot for
   cwd validation (Task 2 snapshot test).
4. Missing/nonregular/invalid-UTF8/empty/outside-root input must fail before any
   vendor resolution or settings mutation (Task 2 refusal matrix).
5. Absolute paths and direct helper calls must retain behavior; audit masking
   and phase-specific stdin/timeout precedence remain unchanged (both regressions).

## Task 1: Shared exit-token membership

**Files:** `bin/_common.py`, new `tests/test_exit_token_contract.py`, exact
`tests/fixtures/shared-spec/exit-tokens.json` and adjacent provenance README.

**Interface:** Keep `map_classification_to_exit(cls: str) -> int` and unknown
fallback unchanged. Keep `CLASSIFICATION_TOKENS` unchanged.

- [x] Copy the exact published payload, record source commit/hash, and add a
  contract test that fails for the three absent mapper rows:

  ```python
  @pytest.mark.parametrize("row", contract["tokens"], ids=lambda row: row["token"])
  def test_common_token_exit(row):
      assert _common.map_classification_to_exit(row["token"]) == row["exit"]
  ```

  Check all exit constants, declared classifier tokens/vendor maps, explicit
  `route-mismatch` direct exception and `permission-unavailable` alias. Pin
  non-repairability of the added rows and the unchanged unknown fallback.
- [x] A fresh dedicated executor runs this file and observes the three missing
  rows failing before production changes.
- [x] Add `admission-refused`, `vendor-timeout`, `input-delivery-failed` rows,
  each `EXIT_TERMINAL`. Remove the vacuous `is not None` assertion and correct
  its comment; the contract membership test supplies the real check. Do not
  change producers, phase-specific exits, `_stdin_delivery_failed` or retry.
- [x] Run the new file plus existing stdin and AGY stream regressions. Record
  that map parity does not claim completion of the separately recorded transport
  migration. A already has these rows; it needs the same membership test.

## Task 2: Process-relative wrapper paths

**Files:** `bin/_common.py`, `bin/claude_wrapper.py`, `bin/gemini_wrapper.py`,
`bin/antigravity_wrapper.py`, new `tests/test_wrapper_relative_paths.py`, both
READMEs and a source-pinned Claude handoff note.

**Interfaces:** Extend the helpers compatibly:

```python
def load_prompt_text(prompt, prompt_file, *, process_cwd: Path | None = None): ...
def validate_wrapper_cwd(cwd, *, process_cwd: Path | None = None): ...
```

- [x] Add a helper test with different caller/child directories, and entry tests
  for Claude, Gemini and AGY using synthetic runner boundaries only:

  ```python
  monkeypatch.chdir(caller)
  assert load_prompt_text(None, "prompt.txt") == "caller prompt"
  assert validate_wrapper_cwd("child") == str((caller / "child").resolve())
  ```

  All three mains must pass caller prompt bytes and the normalized child cwd
  to their existing runner. Exercise the five review-focus classes, preserve
  direct helper and absolute-path behavior, and prevent actual provider/settings
  access in the fixture. Keep existing audit-redaction tests unchanged.
- [x] A separate fresh dedicated executor runs this file and observes relative
  acceptance/snapshot failures before production changes.
- [x] Inside each main's existing argument-validation try block, capture
  `process_cwd = Path.cwd()` once before either helper and pass it to both.
  Keep `--help` parsing ahead of this read. Claude adds its missing pathlib
  import. For a relative path replace only its old refusal with:

  ```python
  path = (process_cwd if process_cwd is not None else Path.cwd()) / path
  ```

  Continue through existing strict runtime-root, type and UTF-8 checks. Keep
  XOR, empty-prompt and provider-specific argument checks. Preserve the child's
  Popen cwd behavior; never change the wrapper process directory.
- [x] State relative semantics and unchanged containment in both READMEs.
  Document C28 loader completion separately from pending D-B2 receipt semantics.
  A later needs the matching two helpers, all entrypoints and its absolute-only
  `t16-agy-args.sh` expectation updated; do not modify A.

## Verification and integration

- [x] Separate fresh GREEN executors run focused regressions for each outcome.
  One final fresh executor runs the full suite once, skill quick validation,
  and the fixed provider-free lifecycle once; record source identity/cleanup.
- [x] Run full Ubuntu 24.04 tests in the existing task image with source read-only
  and network disabled. No new dependency or live-provider claim.
- [ ] Refresh shared main. Review this complete plan scope with the required
  four producers and unchanged full-scope criteria, including prior findings as
  data on correction rounds. Revalidate source integrity and clean exact fixtures.
- [ ] Commit/push admitted bytes, verify clean-HEAD archive hashes/tests, and
  integrate only when the exact final-merge approval boundary is satisfied.
  Keep the protected common checkout's dirty `AGENTS.md` unchanged.

Verification before formal review: dedicated focused suites passed 134 and 49
cases; macOS full suite passed 1,330; Ubuntu 24.04.4 passed 1,328 with two existing
filesystem-specific skips. The source skill validator passed. The provider-free
lifecycle returned SUCCESS with matching integrity/source hashes and exact
fixture cleanup. These results do not claim authenticated provider capability.
