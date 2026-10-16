# Gemini Argon: inspect and adopt the Google-route boundary

> Historical handoff for Codex 0.2.561 and library dev3 (2026-10-15).
> The package identity and diagnostic limits below describe that snapshot.
> For a new adoption, use the published
> [dev4 release](https://github.com/codefoundry-io/triad-dispatch-lib/releases/tag/v0.1.0.dev4)
> and its [host adoption guide](https://github.com/codefoundry-io/triad-dispatch-lib/blob/v0.1.0.dev4/docs/host-adoption.md).

This is a handoff for the owner to forward to the Argon agent. It is not an
already executed Google-host migration or authorization to message another agent.
There is no separate Gemini host in the current architecture: `gemini` and `agy`
are Google routes inside Claude host A or Codex host B. Identify the owner's target
repository before editing and follow its instructions. Coordinate file ownership
if working concurrently; do not modify another host's native internals.

## Shared source and scope

Use `codefoundry-io/triad-dispatch-lib` for both common implementation and `spec/`.
Reviewed source `2d1e62e7de6f33fa13a918a39579c6b5e74def00` is included unchanged in
main merge `9489543ee24f338e9c6d0e3b032a1aa389986429`. Library version is
`0.1.0.dev3`, Python 3.12+. The package is not published to a package index.
Use immutable dependency and resource identities, recorded as described in the
[adoption handoff](claude-library-adoption.md#target-and-ownership). Keep host
releases independent; the old spec repository is historical, not the editing SOT.

1. Inventory the selected host's Google extraction, six binding checks, roster
   merging, prompt rendering, classifiers and execution/custody adapters. Compare
   them with the pinned library API and conformance/case maps linked in the handoff.
   Report actual gaps before changing behavior. Codex already consumes common v2
   roster/prompt/verdict facades; its production scheduler remains host-owned.
2. Reuse shared deterministic semantics. Preserve arbitrary entry names, repeated
   families, all four routes and opaque model/effort values. Do not hard-code Argon
   as a route or silently replace the owner's chosen models. Requested identity
   and observed runtime identity are separate; missing metadata is `UNEXPOSED`.
3. Pass original provider envelopes to `gemini-json` / `agy-stream-json`; do not
   pass previously extracted wrapper JSON as an original carrier. Keep native
   structured output where supported and let common admission check schema and
   all six bindings without repairing malformed responses.
4. Preserve the existing C23 AGY ERROR/exit0 recovery decision in the host. The
   library's strict stream accepts one SUCCESS terminal. After proving ordered
   failed-then-successful finish evidence and existing exit/auth/read/tool-error/
   timeout checks, use original final JSON through `native-final` with truthful
   metadata and the same binding. Never turn arbitrary ERROR streams into success.
5. Retain native process control, authentication, file permissions, packet seals,
   terminal acknowledgement, token/error classification and cleanup in the host.
   Preserve the established Gemini noninteractive-plan workaround. MCP migration
   is excluded; openai-codex stays TODO. Do not introduce a parallel scheduler.
6. Use host A clauses and `agy_hook_active=True` only when that hook is actually
   enforced. For host B, preserve the exact sealed-packet include-directory rule
   and no provider-settings mutation. Do not exchange these host-specific controls.
   Encode scalar prompt path replacements as JSON strings while preserving actual
   filesystem paths and CLI arguments; the renderer requires single-line values.

## Required evidence and deliverable

The current shared schema-error API supplies fixed messages and stable codes,
without JSON-location/validator detail. Preserve that boundary instead of adding
another host validator or relying on suppressed exception context. A richer
diagnostic contract must be implemented once in the library. Source tests prove
lossless JSON path encoding, not the provider's native file-read fidelity; keep
those evidence claims separate.

Add focused regressions for genuine gaps: successful original carriers, strict
JSON/schema/six-binding refusals, positive and invalid AGY recovery, requested vs
effective identity, timeout/cancellation and terminal cleanup. If adopting shared
coordination, also cover the integrity-fault and cancellation-custody contracts in
the handoff; shared `integrity_ok=False` does not prove a host check finished.

Verify installed packages from a neutral directory, native macOS and Ubuntu, and
supported Python versions. Separate synthetic library results, real authenticated
provider behavior, host review, distribution, fresh installed-session exposure
and release. Preserve user-modified and unrelated installer files; test interrupted
upgrade and concurrent cold-cache imports if the host verifies runtime inventory.

Research current CLI/model behavior using official documentation or version-tagged
upstream sources, recording date, installed version and URLs. Allow current web
research in reviews and use 40-minute reviewer budgets. Historical feature lists
do not establish today's behavior. Return a spec-to-host mapping, reproduced gaps,
minimal proposed/final changes, exact test evidence, independent review results and
remaining limits. Common semantic corrections belong in library spec/code/tests
once, followed by an independent pinned refresh in each host.
