# B v2 offline validation foundation

**Goal:** Validate a v2 verdict against exact published shared schemas without
network access, while preserving every existing dispatch and legacy gate route.

**Shared source:** `codefoundry-io/triad-dispatch-spec` commit
`055204c83e57bf87eeac5b2422f2b17340f7c53b` (reviewed candidate branch).
Remote main was fetched as `2eb883fee59e66556ee7c7f87189b38231136622`.
This is not tagged revision adoption, host conformance, or V1–V5 evidence.

**Architecture:** Vendor the three contract payloads unchanged under `contracts/`
with an adjacent host-owned commit/hash manifest. Use maintained `jsonschema`
Draft 2020-12 validation and a registry that refuses external retrieval. Reuse
the existing canonical-file reader and duplicate-member check; keep the legacy
validator file unchanged and independently executable when copied alone.
No new wrapper schema alias, provider SDK, schema engine, scheduler or hook.

**Budget:** Production +140–220/-0–8, novel core about 100–160 lines; vendored
JSON data about 680 lines separately; tests +180–260; docs +70–110. Growth within
this outcome is recorded, not an automatic scope escalation.

## Implementation and verification

1. Root writes tests before production changes. A fresh dedicated Terra/high
   executor reads the canonical source skill and observes missing v2 validation
   and missing dependency refusal (RED). Source/tests remain fixed during runs.
2. Add `bin/validate_v2.py`, exposing a raw-JSON validation function and an
   explicit CLI with required expected review ID, family, digest, leg name,
   attempt and route (`null` for non-Google). Preserve the original representation;
   never convert legacy verdict labels or synthesize absent evidence.
3. Reject duplicate original members, malformed JSON, schema errors, wrong
   expected binding, missing/tampered payloads, noncanonical result files and
   external schema retrieval. Closed canonical types come from the shared schema.
   The manifest records provenance/integrity, not a cryptographic signature.
4. Add `jsonschema>=4.26,<5` to requirements. Extend bootstrap readiness to require
   the used API before persistent mutation; report the owner-terminal dependency
   command without auto-installation. Preserve the Pydantic 2 check and messages.
5. Add the validator and exact payload/manifest paths to distribution hashes.
   Document the explicit offline CLI and its candidate status in both READMEs,
   security guidance and the contract directory. Preserve installed revision pins.
6. A separate fresh executor runs focused GREEN, full regressions, source skill
   validation and the packaged provider-free lifecycle. Distribution archive checks
   run only from a clean committed HEAD; record inapplicability before that point.
   Run the full suite in Ubuntu 24.04 with declared dependencies and no network.
7. Compare A's matching source and record exact line references and adoption
   instructions without editing A. Refresh shared main before final review.
   Complete the required full-scope four-leg review; verify and fix findings,
   then rerun every leg on changed bytes. Commit/push the reviewed slice and
   verify clean-HEAD archive bytes before the next implementation plan.

## Preservation and exclusions

Legacy copied-file validation, wrapper/custom-schema routing, native Codex,
Claude subprocess, Google auth/model routing, investigation, stdin collection,
read-evidence ownership and worktree/cleanup behavior remain unchanged.
Roster, receipts, retry, prompt/collector activation and public v2 dispatch are
later coherent slices. D-B1 policy composition and D-B2 evidence custody remain
owner decisions; this foundation does not pre-empt them.

## Evidence record

Execution receipts and the cross-family review identify exact source bytes and
terminal outcomes. Authenticated CLI checks and V1–V5 remain NOT RUN.
