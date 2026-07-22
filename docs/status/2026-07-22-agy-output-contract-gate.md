# AGY output-contract gate status

Date: 2026-07-22

## Outcome

The bounded AGY repair is implemented:

- Pydantic AGY calls use schema-body semantics followed by one canonical
  JSON-body-plus-sentinel response contract.
- Schema repair rebuilds from the unsealed effective prompt and applies the
  same sealer once.
- A terminal AGY transcript record whose `truncated_fields` includes `content`
  is rejected so the existing PTY extractor can recover the complete answer.
- Runtime request and validation-error text use closed prompt-data fences; the
  long FormalReview prompt repeats its task anchor immediately before the
  transport contract.

No broader schema, sentinel, IPC, provider, or non-AGY behavior changed.

## Verification

- Focused TDD: the new contract and truncation cases failed before their
  implementations and passed afterward.
- Relevant modules: `175 passed`.
- macOS, Python 3.12.13, Pydantic 2.13.4, after the R13 correction:
  `603 passed, 6 subtests passed in 122.84s`.
- Ubuntu 24.04 pinned image
  `sha256:4fbb8e6a8395de5a7550b33509421a2bafbc0aab6c06ba2cef9ebffbc7092d90`,
  Python 3.12.3, Pydantic 2.13.3, after the R13 correction:
  `602 passed, 1 skipped, 6 subtests passed in 77.51s`.
- The Ubuntu skip is the existing APFS-only case-insensitive path case.
- macOS and Ubuntu Bash syntax and no-output Python compilation passed.
- Plugin package validation passed.
- Prompt lint found no mechanical candidate. A fresh-context semantic review
  found `0 FAIL, 22 PASS, 7 N-A` and recommended no further prompt change.
- `git diff --check` passed on the candidate.

## Review boundary

R13 dispatched two independent Gemini 3.1 Pro (High) legs and two independent
fresh Codex legs over identical packet bytes. Three legs returned `SAFE` with
no findings. Codex scope B found one reproducible `Major`: the reviewer-visible
packet copy could not verify its snapshot because the receipt required the
original absolute parent path. R13 is therefore `NOT-SAFE`.

The bounded TDD correction treats the generated snapshot directory name as the
logical identity. A byte-identical copy under a different parent now verifies,
while renaming still fails. No receipt schema, packet format, provider route, or
wrapper behavior changed. A new four-leg review ID is required.

This is a small wrapper. Reviewers must report only concrete defects supported
by an ordinary reachable execution path. They must not propose speculative
adversarial hardening, rare-event machinery, architectural expansion, or
style-only refactors. A question is blocking only when the cited evidence
prevents a correctness decision. The root leader fact-checks and consolidates
ambiguity before asking the owner one bounded question.

Managed temporary IPC older than 3,600 seconds is cleaned best-effort at skill
entry and wrapper dispatch. Immutable review records are not temporary IPC.

## R14 result

R14 passed the owner-approved alternative formal gate over packet SHA-256
`8946f4317acdcd047d19520ca9527382c177053f587092b51c6cf273847b9acd`:

- Gemini scope A: `SAFE`, zero findings.
- Gemini scope B: `SAFE`, zero findings.
- fresh Codex scope A: `SAFE`, one Minor.
- fresh Codex scope B: `SAFE`, two Minors.
- all four results passed the packaged FormalReview validator and had no open
  questions.

The three Minors reduce to two nonblocking follow-ups: Claude/Gemini persisted
audit argv is stale for schema-injected or repaired Pydantic calls, and the two
README audit-redaction descriptions do not match the more restrictive runtime
behavior. Neither changes provider execution or returned results. They remain
recorded for a later bounded maintenance change so the reviewed candidate is
not changed and sent through another unnecessary round.

The formal gate is complete and `SAFE`. Commit, push, installation, bootstrap
mutation, and release had not occurred when this record was written.
