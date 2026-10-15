# Claude host: adopt triad-dispatch-lib independently

The owner will forward this handoff. It authorizes no message from the Codex
implementation task and makes no claim that Claude has already adopted the library.

## Target and ownership

Implement in the Claude host repository, `codefoundry-io/triad-dispatch`, under its
own instructions, branch, tests and release. Keep Claude and Codex distributions
separate. Shared specification and deterministic behavior belong together in
`codefoundry-io/triad-dispatch-lib`; do not maintain another common implementation
or treat the historical `triad-dispatch-spec` repository as the editing source.

The Codex update targets library **0.1.0.dev3**, source commit
`2d1e62e7de6f33fa13a918a39579c6b5e74def00`. Library PR #1 merged into main at
`9489543ee24f338e9c6d0e3b032a1aa389986429` on 2026-10-15 (Asia/Seoul), with the same
reviewed tree. The package remains unpublished. Pin an exact reviewed build; record the wheel SHA-256, library
commit/version, host commit and consumed bundle IDs. Consult the Codex candidate's
`contracts/library-adoption.json` for its exact built artifact and managed hashes.
Do not resolve mutable `main` or perform network/package installation during review.

Integration references: [library PR #1](https://github.com/codefoundry-io/triad-dispatch-lib/pull/1)
and [Codex adoption PR #44](https://github.com/codefoundry-io/triad-codex-dispatch/pull/44).
Use the pinned library identity above; neither PR link is an installation source.

Codex's inspected wheel SHA-256 is
`df1e84b56a7238bab2a019064c850c30bde5b6b15268a81a1e74d76df0c187b8`.
A separately built wheel needs its own recorded hash and source-byte verification;
do not assume reproducible archive timestamps. Consult the pinned
[host contracts](https://github.com/codefoundry-io/triad-dispatch-lib/blob/2d1e62e7de6f33fa13a918a39579c6b5e74def00/docs/host-adoption.md),
[API](https://github.com/codefoundry-io/triad-dispatch-lib/blob/2d1e62e7de6f33fa13a918a39579c6b5e74def00/spec/reference/library-api.md),
[conformance map](https://github.com/codefoundry-io/triad-dispatch-lib/blob/2d1e62e7de6f33fa13a918a39579c6b5e74def00/spec/reference/library-conformance.md)
and [case coverage](https://github.com/codefoundry-io/triad-dispatch-lib/blob/2d1e62e7de6f33fa13a918a39579c6b5e74def00/spec/reference/library-case-coverage.md).

The three resource bundle IDs are:

| Bundle | Content ID |
| --- | --- |
| Verdict | `455dfd8a7d586d04eedb60ee492cf421e076a77bafcccbba12de37cc12bf0340` |
| Roster | `a99fb58dbd920dfed0d88d8c8b9117bd07633b76b5d2565e05f50a5b5c423ed8` |
| Prompts | `c332d95688b9db3dac187a0bebac6ddc0eddfdbdc5401a649697d0601455e843` |

These identify runtime bundles, not the whole normative spec. Preserve schema
`$id` literals. Runtime manifests have six fields; keep release provenance in a
separate host record.

## Implementation sequence

1. Inspect the current Claude source and installer. Inventory its shared semantic
   functions and host-native guards before changing them. The Codex task has not
   inspected or modified Claude's current implementation.
2. Install or vendor the exact library package using Claude's distribution method.
   Python requires 3.12+, `jsonschema>=4.26,<5`, `referencing>=0.37,<1`.
   Preserve any additional Claude dependencies. Native transitive dependencies
   require native macOS/Ubuntu wheel/install verification; the shared Python
   package itself introduces no Rust build step.
3. Replace local roster merging and verdict parsing/binding with `resolve_roster`,
   `parse_json`, `validate_binding`, `validate_verdict` and, where the true original
   carrier is available, `ProviderOutput` plus `admit_output`. Keep file custody,
   terminal observation and provider identity checks in the host.
4. Render common clauses using `render_review_clauses(host="A", ...)`. Pass the
   actual family/route, phase, bound date, web authorization and exact replacement
   keys. Set `agy_hook_active=True` only for an actually enforced Google/AGY host A
   hook. Codex's host B selection is not a Claude default. Use `render_data` once
   for prior findings/rebuttals, including its caveat.
   JSON-string encode scalar path replacements so the shared single-line contract
   preserves quotes, CR/LF and non-ASCII filenames; keep native paths/argv unchanged.
5. Preserve native spawning, requested/effective model and effort distinctions,
   authentication, permission controls, existing AGY exceptions and the Gemini
   noninteractive-plan workaround. No MCP migration; openai-codex remains TODO.
6. If adopting `run_review`, implement preflight/invoke/integrity callbacks in
   Claude. All preflights must finish before invocation. Own native cancellation,
   wait for child cleanup before propagating cancellation, and report late results
   as timeouts. `run_investigations` supplies extra independent perspectives but
   contributes no formal votes. Do not copy the Codex experimental file supervisor
   as a second production scheduler.
7. Bind the consumed library code/resources and adoption metadata into review
   custody. A package or resource change after preparation requires a new basis.
   Keep contract-loading failures distinct from provider failure/negative verdicts.

Do not feed already extracted wrapper verdict JSON to a `claude-json`,
`gemini-json` or `agy-stream-json` extractor. Those carriers mean original provider
envelopes. In particular, direct use of the strict AGY stream extractor can change
existing host stream exceptions; port that boundary only after dedicated tests.

Shared schema refusals expose stable error codes and fixed messages; they do not
currently expose a failing JSON location or validator name. Do not duplicate
schema validation in the host or consume suppressed exception internals to recover
that detail. Any required structured diagnostic extension belongs in the library
contract first. JSON path round-trip tests also do not prove a provider correctly
decodes the displayed path before using a native file tool; record that separately.

Preserve C23 recovery explicitly: the host must establish same-run ordered
failed-then-successful finish evidence, read/tool-error checks and its exit,
authentication, timeout and transport rules. Only then may it submit the original
final verdict through `native-final`, with truthful observed terminal metadata and
the same Google/AGY binding. Test missing/reversed finishes and unrelated errors.

If using shared coordination, preserve host faults separately. An ordinary
integrity callback error, self-cancellation or non-bool result becomes
`integrity_ok=False`; it does not prove the host check ran to completion. Failure
to launch/finish that check aborts collection without a collection record.
`ContractError` propagates after callback cleanup. Keep native requests until a
matching terminal acknowledgement even if cancellation publication or receipt
reading fails. Bad response bytes fail admission without undoing already observed
termination. A timeout initiates cancellation; a late SAFE cannot approve.
Retain host authentication/token/error classifiers and Minor-only negative
selection-deviation records; shared admission does not replace them.

## Verification and installer requirements

- Test arbitrary named entries and all four routes, repeated families, model/effort
  values preserved as opaque data, all six binding swaps, duplicate/invalid/overflow
  JSON, missing/negative/failed entries, timeout/cancellation and cleanup.
- Check host A prompt profiles for all phases, web on/off, AGY hook enabled/disabled,
  hostile residual text, exact placeholders and absence of host B-only clauses.
- Run installed-package tests from a neutral directory without the library source
  checkout on the import path. Run native macOS and Ubuntu checks; distinguish
  synthetic responses from real authenticated provider evidence.
- Exercise concurrent cold-cache imports against the shared installed package.
  If the host checks generated-file inventory at runtime, normal CPython atomic
  bytecode publication must not cause false refusal. Continue rejecting links,
  special files and unexpected distribution inputs.
- Keep a managed-file ledger with the source version and last-written hash. Before
  replacing/removing files, refuse conflicts and preserve user changes/unrelated
  content. Verify upgrade interruption/recovery. Do not confuse a package manager's
  cache replacement with a host installer proving edit preservation.
- Record library conformance, Claude native behavior, source review, distribution,
  fresh installed-session exposure and publication as separate results.
- Check current official vendor documentation or version-tagged upstream source
  for CLI/model claims, and record date, installed version and URLs. Historical
  research is context, not proof of today's behavior. Allow web research in review;
  use the owner-selected composition and 40-minute reviewer budgets.

If a common semantic change is needed, implement it once with specification and
tests in the library, then refresh each host's pinned dependency independently.
Do not copy Codex bootstrap/launcher internals into Claude merely for parity.
