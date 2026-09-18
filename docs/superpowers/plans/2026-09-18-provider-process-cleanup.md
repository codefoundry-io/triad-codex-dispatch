# Provider process-group cleanup implementation plan

> Execute with `superpowers:subagent-driven-development` and test-driven development.

**Goal:** Terminate surviving provider-group descendants on timeout/interruption
even when the direct child exits first.

**Architecture:** Capture a verified child-owned group at spawn, pass that
identity to the shared cleanup helper, and make group escalation independent
of direct-child reaping. Preserve direct-process fallback.

**Tech stack:** Python 3.12+, stdlib subprocess/os/signal, pytest; POSIX lifecycle
fixture with platform skip outside supported group APIs.

**Spec:** `docs/superpowers/specs/2026-09-18-dispatch-adoption-design.md`, S1.

## Global constraints

- Codex remains native; no provider policy, retry, schema, binding, admission,
  default model, or permission changes.
- Preserve unrelated dirty `AGENTS.md`; stage only explicitly owned files.
- Use the existing `codex/triad-adoption-process-cleanup` branch in the
  `triad-codex-dispatch-reliability` checkout. No new real-project worktree.
- Bound every wait and every fixture. Never signal the wrapper's own process
  group. Never rediscover an exited provider leader's group at teardown.
- Keep timeout result classification and original interruption propagation.
- Planned production net delta <100 lines and novel core <100 lines; one claim.
- No installation, global settings, formal admission, merge, or publication.

### Task 1: close the direct-child-exits-first cleanup gap

**Files owned by the implementer:**

- Modify `bin/_common.py`: shared spawn and cleanup path only.
- Modify `tests/test_provider_wrappers.py`: focused lifecycle and identity tests.
- Modify `README.md`, `README.ko.md`, and `SECURITY.md`: brief current timeout
  cleanup contract and platform/session limitations; no release/version bump.

**Inputs:** Read the spec's S1 section and constraints. Local spike evidence is
at host workspace `_runs/infra/20260918-triad-adoption-spike-Tcszot/process/`.
The reproducer demonstrates the causal case, not production code to copy whole.
Base product is `2abfc071390e7c7aae06f0ab8af905a382b87a80`.

1. **RED:** Add a real POSIX-gated subprocess regression. The provider fixture
   starts a same-group descendant that ignores TERM, publishes a ready receipt,
   and exits on TERM. Invoke `_run_once` with a bounded timeout. Assert the
   timeout, direct-child TERM receipt, and descendant termination before a
   bounded deadline. Do not confuse a startup/fixture failure with expected RED.
   In `finally`, clean only recorded fixture processes after validating group
   identity. Record the failure showing the descendant survives current code.
2. Cover the saved-identity edge and own-group fallback with narrow doubles.
   An exited leader must not require another `getpgid`; an unsafe/shared group
   must receive no signal at all, including liveness probes. Preserve fallback
   TERM/KILL behavior where group APIs or safe identity are absent. Update the
   existing interruption test to model group liveness realistically.
3. **GREEN:** Immediately after `Popen`, capture the PGID when supported;
   require it equal the child's PID and differ from `os.getpgrp()`. Handle an
   absent/unavailable identity as direct-child fallback. Pass the saved optional
   PGID to `_terminate_provider_process_group` on both timeout and interruption.
4. In that helper, send TERM to the verified group (or direct fallback), retain
   the bounded direct-child wait, and probe the saved group for survivors even
   after the direct child was reaped. Send KILL to surviving group members;
   bound remaining direct-child reaping. Treat an absent group as empty;
   preserve current handling of permission failures without unsafe targeting.
5. Add concise English/Korean docs and security limits: best-effort POSIX
   group cleanup, direct-process fallback, escaped sessions outside guarantee,
   and residual identifier reuse. Do not describe this as an OS sandbox.
6. Run focused tests while iterating, then the full suite once. Self-review the
   diff against the single behavioral claim. Commit only the five owned files
   with a subject such as `fix: reap provider groups after direct child exit`.
7. Write the implementer report in the controller-provided SDD report path:
   RED/GREEN exact commands and output, full-suite result, changed files,
   source commit, fixture cleanup result, and residual concerns.

**Focused command**, invoked from `/Users/chaniri/codex_workspace`:

```sh
/bin/zsh -lic 'python3 -m pytest -q "$1/tests/test_provider_wrappers.py" -k "process_group or provider_descendant" --rootdir "$1" -p no:cacheprovider' triad-tests /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
```

**Full-suite command**, same host cwd:

```sh
/bin/zsh -lic 'python3 -m pytest -q "$1/tests" --rootdir "$1" -p no:cacheprovider' triad-tests /Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability
```

## Review and completion

A fresh task reviewer checks the diff, spec, and test evidence without executing
providers. The leader validates findings before correction. A separate fresh
whole-branch reviewer checks the final implementation and affected contracts.
Use prompt-controlled no-edit review and verify the worktree fingerprint before
and after. These native reviews do not substitute for formal cross-family
admission. Record exact test totals and commit IDs before reporting this slice
implemented; leave later adoption rows as separate planned work.
