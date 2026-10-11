# DL-103 — current AGY v2 schema accepted

2026-10-10. B aa91bde8fa4a65bd355d44eb74667d56e3315ba8; shared73e6613,
main3afc4d7, PR12fc7cd4a. Read-only A abbc684a. This is a diagnostic, not an
operational review, merge approval or full C30 certification.

## Question and current source

Does B's actual AGY v2 wrapper need a producer-schema projection? Current
verdict_v2.bound_verdict already intersects route to enum ['agy'] with const agy.
The actual wrapper retains $schema/$id/allOf, not, uniqueItems and optional
finding correction. A's broader projection is not evidence that every dropped
keyword fails on AGY; its source identifies the null-enum rejection as AGY and
the not/required-correction refusals as Codex. No A/native code is changed.

## Actual normal-wrapper result

One antigravity_wrapper.py invocation, AGY 1.3.3, requested
gemini-3.1-pro-high/high, timeout120s, read-only, packaged verdict_v2:LegVerdict,
six expected bindings, canonical selector and provider-free v2 preflight,
installed matching triad-codex-readonly-review profile, existing settings guard
and formal child-environment filtering. No wrapper bypass, launcher retry,
fallback, global profile installation or environment-default change.

Wrapper exit0 in 13.8s; output matches the supplied synthetic fixture
and passes the unchanged full local canonical validator with all six bindings.
The fixture's SAFE TO MERGE string is test data, not a review/admission verdict.
Bound schema SHA-256: 056ea41f5b41f9f4f106c3e4421887af6122b2b28b2f8e0c2a93e2572ddae1e0.
Source pre/post fingerprint: e8b1acfa8078bac8764e2512f94d14bb027dcba6fbd02438b7c0ed93d1930cfb (equal).
Exact temporary launcher stage/cwd removed; durable local manifest, preflight,
schema, stdout, stderr, result and cleanup receipts retained under
_runs/spec-plan-20261010/u3e in the B checkout. Actual command used literal
/bin/zsh -lic, require_escalated, workspace outer cwd; Python3.12.13/pytest9.0.3,
macOS26.6.2 arm64. Ubuntu NOT RUN. Vendor internal requests are not independently
counted; only one wrapper/provider process invocation is claimed.

The primary [AGY headless documentation](https://www.antigravity.google/docs/cli/headless/#structured-output-with-a-schema)
describes --json-schema and structured_output. It supplies no keyword matrix
that replaces this installed-version check. The successful sample establishes
current-route acceptance, not server enforcement of each keyword or all future
versions/models. Full local validation remains the admission authority.

## Disposition

DL-103 check complete for this current route: no producer projection or new
runtime code is justified. Production/test delta: zero. Retain prior constructed
regressions and their latest full-suite result; no redundant suite or formal
implementation round is added for an unchanged runtime. U3a through U3d retain
their separate completed RED/GREEN and independent review evidence.

## Concurrent A / PR12 evidence

A 4b07949a fixes the C43 CRLF matcher and adds LF-lines/CRLF-bytes/CRLF-lines
controls preserving the original CR bytes. Source and test changes were read at
abbc684a; the commit reports t15 ALL OK and f9 PASS=152 FAIL=0. These are A's
reported results, not tests rerun by B. PR12fc7cd4a records this as DL-145.
The old A CRLF-open claim in B's DL-102 status is therefore superseded.
PR12 also records A internal simplifications in DL-137..144; no automatic B port
or native-leg change follows. Its classifier-guard outcome wording belongs in
the existing U2 evidence reconciliation, not this schema check.
