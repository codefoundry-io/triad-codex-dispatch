# S8: Diagnostic AGY read telemetry

Use separate fresh Terra/high skill executors for RED and GREEN. The leader
owns source and tests; independent agents report execution or review findings.

## Scope and budget

Implement S8 of `../specs/2026-09-18-dispatch-adoption-design.md`: one private
RunResult field, one AGY event projection and one audit-only field. Expected
production additions below 80 (novel core below 65), tests about 200, and docs
about 40 lines. Files: `bin/_common.py`, `bin/antigravity_wrapper.py`, new
`tests/test_agy_read_telemetry.py`, README.md, README.ko.md and SECURITY.md.
No dependencies, configuration, permission, provider or deployment changes.

Official stream shape: https://antigravity.google/docs/cli/headless/.

Only plan-mode interpretation projects observed `step_update` events whose
nested state is DONE, step_type is tool, and tool_name is exactly view_file.
Count matching events, including repeats and failed reads; do not claim unique
executions, successful reads, review coverage or permission enforcement.

Use the host-captured absolute effective cwd, not provider-supplied cwd. Extract
only tool_info.parameters.AbsolutePath strings. Resolve with strict=False and
retain first-seen unique cwd-relative paths, capped at 128 entries and 1024
characters per entry with valid UTF-8. Skip malformed, relative, outside,
traversing, symlink-escaping and unrepresentable paths. Path-resolution failures
must not affect the provider result. No usable cwd or matching events means no
telemetry. Never retain outputs, errors, other arguments or provider identifiers.

Ordinary audit stores event count and relative paths only for antigravity;
hardened/redacted audit retains count only. Failure/repair IPC, result JSON,
retry, exit classification and admission stay unchanged. Existing raw-stream
custody is unchanged. Current resolution is not historical filesystem proof.

## Implementation and verification

1. Write NDJSON behavior tests covering successful/failed terminal results,
   ordinary-call absence, exact event selection, duplicate/limit handling,
   malformed/outside/symlink/invalid paths, audit redaction and IPC exclusion.
2. Fresh dedicated executor observes RED against the canonical source skill.
3. Add the bounded projection and audit field, then English/Korean/security docs.
4. Separate fresh executor runs focused GREEN, the complete repository suite,
   the resolved system skill validator and the source provider-free lifecycle.
   Keep actual terminal records, pre/final source identity and exact fixture
   cleanup; use the host login-shell Python and no pytest/bytecode caches.
5. Independent static task review; leader checks findings. Freeze the source,
   complete the four-leg gate and integrity, then CI and authorized merge before
   S9 implementation. Ask only before deployment except the owner's confirmed
   design-defect stop boundary.
