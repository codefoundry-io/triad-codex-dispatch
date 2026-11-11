# Codex host: bounded library follow-up proposal

Status: proposal only, 2026-10-22. This document authorizes no implementation,
dependency refresh, release, publication, or installation. Source inspection is
the evidence below; no runtime or provider behavior was exercised.

## Confirmed basis

The inspected host is [Codex main at db0fe780](https://github.com/codefoundry-io/triad-codex-dispatch/tree/db0fe780ff85483a98bafd3a1668dd8b7ab2f90f).
Its [adoption manifest](https://github.com/codefoundry-io/triad-codex-dispatch/blob/db0fe780ff85483a98bafd3a1668dd8b7ab2f90f/contracts/library-adoption.json)
pins `triad-dispatch-lib` `0.1.0.dev4`, source
`087af94a7078de0ae9701fb057840b5492f51f66`, wheel SHA-256
`c5bfdf10c4ce81f431ec7f77106e4d77b1556ac9c7b6b01bdb6616f988e8b2cc`.
Library main `f043c257ccd748371c34e9d1f23e32064e139354` is a separate
upstream state; it does not change this host's adopted bytes.

The bundled [roster validator](https://github.com/codefoundry-io/triad-codex-dispatch/blob/db0fe780ff85483a98bafd3a1668dd8b7ab2f90f/bin/triad_dispatch_lib/roster.py)
sets `RosterError.path` from `absolute_schema_path`; `.missing` and `.document`
already exist. That path identifies a schema location, not the invalid entry's
instance index. This is the concrete information gap tracked by
[library #9](https://github.com/codefoundry-io/triad-dispatch-lib/issues/9).
The [host facade](https://github.com/codefoundry-io/triad-codex-dispatch/blob/db0fe780ff85483a98bafd3a1668dd8b7ab2f90f/bin/review_roster.py)
then wraps caller refusals as `ValueError("invalid roster: ...")`, retaining only
the fixed message. The public `review_round.py resolve-roster` command reports
that refusal on stderr and returns 2. Contract faults remain a distinct exception
path, as asserted in `tests/test_library_host_integration.py`.

## Selected next task: roster refusal evidence at the host boundary

Prepare one offline regression unit that makes the current information loss
explicit and defines the host's acceptance vector for a future upstream fix.
Do not implement #9 here or infer an instance path from `.path`. The immediate
useful result is reproducible host evidence and a narrow adoption decision.

- [ ] Extend `tests/test_review_roster.py` and, where needed,
  `tests/test_library_host_integration.py` with a multi-entry override whose later
  entry has a string `timeout_s`, then a resolved Google entry selecting `agy`
  while carrying only a `gemini` block. Distinguish override validation from final
  resolved-roster validation. Record the actual current code, schema path, missing member,
  document stage, host stderr, exit status, and absence of provider calls.
- [ ] Include valid repeated-family entries and the same refusal in a disabled
  entry. Validation covers the whole roster, rather than only launched entries.
- [ ] Freeze expected behavior: malformed input produces no success JSON, returns
  2 through the public resolver, and does not become an agreement result or retry.
  Preserve the existing contract-fault separation.
- [ ] Specify the desired future diagnostic: identify the actual offending entry
  and member, with document provenance, without dumping the roster or inventing
  unavailable metadata. Leave the upstream metadata name and semantics pending.

Expected immediate production delta: +0/-0/net 0 lines; novel core 0. Estimated
test/fixture delta: 40–100 lines across the two named test files; documentation
under 40 lines. This is an evidence unit, not a full implementation plan.
Acceptance requires focused offline tests and preservation of the existing
resolver/adoption tests; record commands and outcomes when executed. This proposal
does not claim those tests passed.

## Contingent adoption and deferred work

After #9 has an approved upstream contract and immutable artifact, propose a
separate bounded adoption/formatter change with exact source, wheel, manifest and
bundle evidence. Reuse the vector above and retain exception codes, CLI exit
behavior, host custody and native spawning/provider adapters. Do not hand-edit
vendored library files as a host fix.

[Library #21](https://github.com/codefoundry-io/triad-dispatch-lib/issues/21)
does not permit dropping or making `acceptance` optional: it remains required
data, and every selected enabled entry, including `informational`, must approve.
Existing `test_v2_rounds.py` covers informational blockers and nonempty rosters
without a family minimum. Preserve these checks and the complete selected roster.

[Library PR #20](https://github.com/codefoundry-io/triad-dispatch-lib/pull/20),
head `13bee1422032984be42c7bb24ef74ac5001b5a7c`, is an open wording-only proposal,
not an adopted revision. Its patch changes historical/spec wording and explicitly
orders nothing for host B. Current Codex v2 common clauses already require every
selected leg's explicit approval; the inspected material establishes no matching
runtime defect. Reassess only concrete wording overlap after upstream disposition.

Keep intentional legacy schema identifiers and namespace verification
([#17](https://github.com/codefoundry-io/triad-dispatch-lib/issues/17)); hold extra
extractions ([#5](https://github.com/codefoundry-io/triad-dispatch-lib/issues/5)).
Claude and AGY follow-ups stay with their respective owners; AGY is the third
consumer, not a new shared host profile. Implementation, formal review, merge,
release, local installation and fresh-session/provider proof remain separate gates.
