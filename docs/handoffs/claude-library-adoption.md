# Claude host: adopt triad-dispatch-lib independently

The owner will forward this handoff. It authorizes no message from the Codex
implementation task and makes no claim that Claude has already adopted the library.

## Target and ownership

Implement in the Claude host repository, `codefoundry-io/triad-dispatch`, under its
own instructions, branch, tests and release. Keep Claude and Codex distributions
separate. Shared specification and deterministic behavior belong together in
`codefoundry-io/triad-dispatch-lib`; do not maintain another common implementation
or treat the historical `triad-dispatch-spec` repository as the editing source.

The Codex candidate targets library **0.1.0.dev3**, source commit
`81748d721e56dfc3463888f02328902e18398600`. It is unpublished and library PR #1 is
still a candidate. Pin an exact reviewed build; record the wheel SHA-256, library
commit/version, host commit and consumed bundle IDs. Consult the Codex candidate's
`contracts/library-adoption.json` for its exact built artifact and managed hashes.
Do not resolve mutable `main` or perform network/package installation during review.

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

## Verification and installer requirements

- Test arbitrary named entries and all four routes, repeated families, model/effort
  values preserved as opaque data, all six binding swaps, duplicate/invalid/overflow
  JSON, missing/negative/failed entries, timeout/cancellation and cleanup.
- Check host A prompt profiles for all phases, web on/off, AGY hook enabled/disabled,
  hostile residual text, exact placeholders and absence of host B-only clauses.
- Run installed-package tests from a neutral directory without the library source
  checkout on the import path. Run native macOS and Ubuntu checks; distinguish
  synthetic responses from real authenticated provider evidence.
- Keep a managed-file ledger with the source version and last-written hash. Before
  replacing/removing files, refuse conflicts and preserve user changes/unrelated
  content. Verify upgrade interruption/recovery. Do not confuse a package manager's
  cache replacement with a host installer proving edit preservation.
- Record library conformance, Claude native behavior, source review, distribution,
  fresh installed-session exposure and publication as separate results.

If a common semantic change is needed, implement it once with specification and
tests in the library, then refresh each host's pinned dependency independently.
Do not copy Codex bootstrap/launcher internals into Claude merely for parity.
