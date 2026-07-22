# Triad R4 Bounded Repair Design

## Goal

Close the deterministic defects confirmed after the invalid R3 review without
expanding triad dispatch into a larger runtime or transaction system.

## Scope

R4 makes six bounded repairs:

1. A formal wrapper dispatch verifies the actual sealed packet before resolving
   or starting a provider. `PACKET_SHA256` must equal the caller's expected
   digest and the SHA-256 of `SHA256SUMS`; every `SHA256SUMS` entry must match
   its packet-relative regular file.
2. A sealed formal dispatch does not perform an internal schema-repair retry.
   It returns the existing deterministic schema-failure result so any retry can
   be rendered, archived, hashed, and dispatched by the leader as a new leg.
   Ordinary non-formal schema use retains its one retry.
3. Bootstrap rejects unsafe Codex profile or rules targets before publishing
   wrapper commands. Existing profile/rules leaves must not be symlinks or
   non-regular files, and the existing `rules` ancestor must be a real
   directory rather than a symlink.
4. Bootstrap removal attempts the managed command group first and stops before
   any other managed state is removed when that group fails. The optional shell
   entry is removed only after command removal succeeds.
5. The unused `triad-setup`, `triad-doctor`, and `bin/triad_runtime.py` surface
   is removed. Provider login remains user-owned; bootstrap installs the
   wrappers and deterministic support artifacts only.
6. A first shared Antigravity reader restores the original settings immediately
   if deny installation raises after replacing the settings file.

## Lightweight IPC cleanup

Existing run-log IPC remains one uniquely named file per failed invocation.
Before a normal provider dispatch, the wrapper makes a best-effort attempt to
remove its own managed run-log files and fallback directories older than 3,600
seconds. It examines only the existing managed filename patterns and temp-dir
prefixes. Existing no-follow helpers are reused so a symlinked managed root or
leaf is skipped rather than followed. Fresh files, unrelated files, deletion
races, permissions errors, and already-removed paths are tolerated. Cleanup
failure never changes the provider result and does not prevent dispatch.

No cleanup daemon, registry, database, global scan, provider call, lock
protocol, or retry loop is introduced. Small temporary overflow and abandoned
holes are accepted.

## Error flow

- Packet preflight failure: return the existing argument/preflight failure
  before provider resolution, settings mutation, or request submission.
- Formal schema failure: preserve provider output in the normal evidence path,
  return `schema-fail`, and do not create a hidden second provider prompt.
- Bootstrap target preflight failure: publish no wrapper commands and perform no
  later install mutation.
- Command-group removal failure: preserve all later managed state and return a
  failed removal.
- Cleanup failure: ignore it and continue the dispatch.
- Antigravity settings entry failure: attempt immediate byte-exact restore and
  propagate the original transaction failure.

## Compatibility and exclusions

- Runtime code uses Python standard-library APIs and the existing POSIX wrapper
  boundary on macOS and Ubuntu 24.04; no new dependency or OS-specific cleanup
  command is added.
- Windows is not claimed for the POSIX shell/bootstrap or `fcntl`-based
  Antigravity settings transaction.
- The owner-accepted prompt-controlled Antigravity permission boundary is not
  redesigned in R4.
- R4 does not build a whole-install or whole-remove transaction.
- R4 does not add a new authorization database. The owner's standing external
  review authorization remains a leader/workflow concern.

## Verification and gate

Every behavior change follows red-green TDD. Focused tests run first, followed
by the existing complete macOS suite and the Ubuntu 24.04 verification path.
After deterministic verification, one fresh immutable R4 packet is reviewed by
two independent Gemini 3.1 Pro (High) legs and two independent fresh-context
Codex legs. The packet remains private but is authorized for those official
provider interfaces. No commit, push, or install occurs before that gate is
reconciled.
