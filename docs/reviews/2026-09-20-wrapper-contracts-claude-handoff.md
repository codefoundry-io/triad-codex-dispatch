# C8/C28 wrapper contract implementation handoff

This is the C8/C28 slice record. Current whole-host status is maintained in the
[shared Claude handoff](https://github.com/codefoundry-io/triad-dispatch-spec/blob/codex/host-b-preimplementation-audit/decisions/host-b-0555-contract-compliance-handoff.md).

This slice implements the settled token-table and input-path portions of the
[published shared candidate](https://github.com/codefoundry-io/triad-dispatch-spec/blob/055204c83e57bf87eeac5b2422f2b17340f7c53b/decisions/rev-2-implementation-spec.md).
Remote main was fetched again before implementation and remained
`2eb883fee59e66556ee7c7f87189b38231136622`. The candidate is not an adopted tag.
A was inspected read-only at `92c8afd500499d8736afcc28b39a87a4f87fed50`.

## Contract and implementation

| Contract | B implementation and tests | A follow-up |
|---|---|---|
| C8 / R-TOKENS: every shared token maps to the declared exit | `bin/_common.py:69` adds three terminal map rows; `tests/test_exit_token_contract.py:26` checks the exact shared payload, all table rows/constants, classifier/vendor-map membership, literal producers and explicit exceptions. | A already has these rows at [`3rd-Agent/wrappers/_common.py:162`](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/3rd-Agent/wrappers/_common.py#L162-L183). Add meaningful shared membership tests; a fallback mapper returning an integer cannot prove membership through an `is not None` assertion. |
| C28: resolve both input paths from wrapper entry cwd | `bin/_common.py:482` and `:505` accept the optional captured base. `bin/claude_wrapper.py:284`, `bin/gemini_wrapper.py:254`, and `bin/antigravity_wrapper.py:434` capture it once inside argument validation. `tests/test_wrapper_relative_paths.py:74` covers different caller/child prompt contents, absolute paths, entry snapshot stability and refusal before vendor resolution. | A's helpers still refuse relative paths at [`_common.py:1148`](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/3rd-Agent/wrappers/_common.py#L1148-L1190). Apply the same bounded loader change to A's existing mains, including its Codex subprocess; preserve A's native Claude route. |

The exact exit-token fixture and its SHA-256/source commit are recorded in
`tests/fixtures/shared-spec/README.md`. It is a test input; no new runtime
configuration loader or duplicate editable contract was introduced.

## Preserved behavior and limits

- The three added rows are map-only on B. They are not new emitted states or
  repair targets. `permission-unavailable` remains an inert compatibility alias;
  AGY `route-mismatch` retains its direct exit. B's phase-specific stdin failure,
  vendor error/timeout precedence and `_stdin_delivery_failed` flag are unchanged.
  Map parity does not claim the separately recorded transport migration is done.
- Relative paths use `pathlib` and the existing strict resolution/root/type/UTF-8
  checks. Loading the prompt never uses the provider's requested cwd. The process
  does not change directory; `--help` still parses before the entry snapshot.
  Absolute paths and existing direct helper callers remain valid.
- Raw/custom-schema invocation, formal binding, native Codex, Google routing and
  authentication, reader/process collection, settings leases, symlink resolution
  and cleanup retain their existing code paths. No SDK or path framework is added.
- Review custody/result/selector/preflight/read-evidence path contracts remain
  absolute. This change does not relax their independent validation.
- This slice supplied C28 loader semantics. The subsequent P4 implementation at
  `8f12bd5` completed masked path evidence, separate B policy and both Google
  investigation triggers under the settled D-B1/D-B2 answers. Neither slice
  switches operational public v2 dispatch or claims V1–V5; consult the current
  shared handoff for those remaining obligations.

## A maintainer patch scope

1. Inspect the shared contract at the exact candidate commit and latest main.
   Preserve A's actual producer semantics; do not copy B's map-only assertions
   over A's active `admission-refused` or `vendor-timeout` producers.
2. Add the optional process-base parameter to A's two existing helpers. Capture
   it once after parsing in each applicable wrapper and use it for both paths:
   [`codex_wrapper.py:112`](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/3rd-Agent/wrappers/codex_wrapper.py#L112-L213),
   [`gemini_wrapper.py:60`](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/3rd-Agent/wrappers/gemini_wrapper.py#L60-L125),
   [`claude_wrapper.py:76`](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/3rd-Agent/wrappers/claude_wrapper.py#L76-L163),
   and [`antigravity_wrapper.py:1360`](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/3rd-Agent/wrappers/antigravity_wrapper.py#L1360-L1367).
   The presence of an A wrapper is not a recommendation to add a parallel route
   on B or change the host's native-agent architecture.
3. Replace A's relative-path rejection expectation at
   [`tests/unit/wrappers/t16-agy-args.sh:33`](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/tests/unit/wrappers/t16-agy-args.sh#L33-L42)
   with caller-base acceptance and preserved refusal controls. Align the wrapper
   README's argument semantics and applicable invocation instructions; retain
   absolute-path requirements for review artifacts and provider tool reads.
4. Test with distinct caller/child directories, non-ASCII/shell-special prompt
   bytes, missing/nonregular/invalid-UTF8/empty/outside-root paths, unchanged
   absolute callers, stdin/vendor-error precedence and existing A read-audit
   controls. Verify macOS and Ubuntu 24.04; do not infer live conformance from
   synthetic runner tests.

## Verification evidence boundary

The independent focused REDs observed the three missing token rows and eight
relative-path/snapshot failures. An earlier C28 test run used JSON for the
existing path-separated allowed-roots variable; that test fixture was corrected
before the valid RED, without changing production. It was not a provider failure.

Run the named tests and existing stdin/AGY/effective-cwd regressions, the full
suite on both supported operating systems, the source skill validator and fixed
provider-free lifecycle. Formal review and clean-HEAD distribution verification
retain their own receipts. Their actual results are recorded with the review/PR;
this source note does not predeclare acceptance, merge, installation or release.
