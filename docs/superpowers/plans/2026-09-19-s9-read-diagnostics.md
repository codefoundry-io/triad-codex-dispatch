# S9: Read-only Google CLI diagnostic snapshot

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. The leader writes source and tests; fresh dedicated executors observe RED and GREEN, and independent agents review.

**Goal:** Produce a private-output-safe snapshot of one selected Google CLI's metadata without inference or configuration changes.

**Architecture:** A standalone `bin/google_diagnostics.py` reuses the existing executable resolver and child-environment scrubber. It runs a fixed version/help sequence in an owned neutral temporary cwd, with optional help-gated inventory. It has no wrapper or admission integration and retains no baseline or history.

**Tech Stack:** Python 3.12+, standard library, existing repository modules and pytest.

**Spec:** `../specs/2026-09-18-dispatch-adoption-design.md`, S9.

## Global constraints and budget

- Entry condition: S8's four-leg gate, CI and authorized merge must complete before S9 implementation starts.
- No new dependencies, provider inference, permissions, authentication, updates, installation, settings mutation, or deployment.
- Preserve the existing resolver: valid pin wins; absent or invalid non-strict pin may use PATH; strict absent/invalid pin cannot fall back. Call `_selectable_google_binary()` once without environment mutation or duplicate pin validation.
- Prefix a relative selection with its original cwd before neutral launch, without normalizing symlink-sensitive components or selecting again. Verify both CLIs with a relative PATH fixture.
- CLI arguments are `--cli agy|gemini` and optional `--inventory`. Ordinary argparse help/errors remain conventional. Handled runtime outcomes produce one JSON snapshot; exit 0 means complete, 1 incomplete.
- Resolver `RoundIntegrityError` and unavailable (`None`) produce fixed root `error` codes `selection_failed` and `binary_missing`, respectively, with status incomplete and an empty probes list. No exception strings or paths are returned.
- Default sequence: `--version`, then `--help`. Each invoked probe uses stdin DEVNULL, captured bytes, a five-second communicate deadline plus the existing S1 bounded cleanup grace, scrubbed injection and known Google API/ADC/Vertex selectors, and the same owned neutral cwd. Stop on an invoked-probe failure. This is not a strict five-second total wall-clock promise.
- Pass the existing `antigravity_wrapper.FORMAL_AGY_ENV_REMOVE` tuple to the scrubber's `remove` argument. Fake executables check every name in that existing set without dumping real environment data.
- Metadata includes fixed probe arguments, status, exit code, stdout byte count/hash, and bounded parsed version/capabilities. No raw stdout, stderr, environment, executable path, extension name or private label is emitted.
- Inventory is opt-in. Advertised AGY `models` requires successful `models --help`; advertised AGY `plugin` or Gemini `extensions` also requires an advertised `list` in group help before its concrete `list` command. No alias guessing. Unsupported capabilities are observations, not failures.
- Parse only bounded tab-separated AGY model slugs; unsupported output stays an opaque hash with an unrecognized-format observation. Extension output stays opaque; line count is not extension count.
- Successful models output exposes `model_format` and `model_slugs`: at most 128 unique ASCII slugs of at most 128 characters, matching `[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}`, with a nonempty tab-separated label on every nonblank row. Any invalid row, empty catalog or exceeded cap yields `model_format: unrecognized` and no slugs, retaining the full stdout hash; never return labels or partial claims. Recognized output uses `model_format: tab-separated` and first-seen slugs.
- No TRIAD-managed persistent state. Vendor executables can maintain their own caches/telemetry; the helper is not an OS sandbox or a baseline drift verdict.
- Estimate: production +220/-0, novel core below 190; tests about +280; docs about +80. The private probe seam reuses S1 cleanup to avoid leaving a metadata CLI descendant after a deadline. Growth within the selected function updates the estimate without automatic class escalation.

## Task 1: Snapshot, packaging and public contract

**Files:** create `bin/google_diagnostics.py`, `tests/test_google_diagnostics.py`; modify `scripts/verify_distribution.py`, `tests/test_distribution_verifier.py`, `README.md`, `README.ko.md`, `SECURITY.md`.

**Interfaces:** consume `review_round._selectable_google_binary(name)` and `_common.scrubbed_child_env(remove=...)`; expose `collect_snapshot(cli, inventory=False) -> dict` plus the standalone CLI. The snapshot has `cli`, `status`, `probes`, `capabilities`; each probe has `args`, `status`, `exit_code`, `stdout_bytes`, `stdout_sha256`. Missing executable and handled host/probe errors use fixed codes, never exception text.

- [ ] Write synthetic executable tests before production. Each fake receives an exact argv-to-output table and appends observed argv/cwd/stdin/environment checks to a test-owned file. Invoke the real diagnostic CLI with the fake pin. Assert literal sequences and public JSON, rather than mocking the helper's subprocess calls.

```python
result, snapshot, calls = invoke_fake(tmp_path, "agy", inventory=False)
assert result.returncode == 0
assert snapshot["status"] == "complete"
assert [call["args"] for call in calls] == [["--version"], ["--help"]]
assert all(call["stdin_empty"] for call in calls)
assert all(call["cwd"] != str(tmp_path) for call in calls)
assert "PRIVATE_PLUGIN" not in result.stdout
```

- [ ] Cover valid-pin precedence, non-strict absent/invalid fallback, strict absent/invalid refusal, no inventory by default, both inventory groups, missing root/group capabilities, nonzero/timeout stop, launch failure, model-format/bounds handling, neutral cwd, closed stdin, scrubbed selectors, and no raw-output disclosure. Include the new module in the expected distribution hash inventory before production inventory changes.
- [ ] A fresh `triad-skill-executor` at Terra/high with no inherited turns reads the canonical source SKILL and runs focused RED. Retain actual terminal receipts and matching source identity, then remove only owned fixtures.
- [ ] Implement one small collector and a private probe seam. Resolve once; create a temporary cwd; spawn each fixed probe with byte pipes, stdin DEVNULL and a POSIX new session. Capture and validate its child-owned PGID, then call `communicate(timeout=5)`. On timeout retain only observed stdout bytes and reuse `_common._terminate_provider_process_group`; do not communicate again or introduce an unbounded context-manager wait. Close owned pipes. On interruption clean this owned process before propagation. Catch expected host/subprocess failures into fixed incomplete outcomes. Hash stdout bytes and never return captured stderr or exception strings. Help matching must recognize command entries, not substrings in prose. Inventory gates extend the fixed list only after successful help probes.
- [ ] Add a real timeout fixture with a same-group descendant ignoring TERM and retaining stdout. The child records readiness after installing its handler; use the production five-second deadline to allow process startup. Check the fixed timeout outcome, exact observed-byte hash, no stderr sentinel disclosure and disappearance of the owned descendant; include the existing cleanup grace in timing tolerance. No real provider is invoked.
- [ ] Recognize the observed Gemini CLI command-entry forms `gemini extensions <command>` and `gemini extensions list`, alongside bare AGY entries. Test these forms independently while still rejecting command words in prose; do not guess unsupported command aliases.
- [ ] Document direct source commands in English/Korean and security limits. Add the helper to the distribution hash targets without changing launchers or bootstrap.
- [ ] A separate fresh dedicated executor runs focused tests, the complete repository suite, the system skill validator, and the canonical provider-free lifecycle. Record actual inner session handles and durable exits; post-fingerprint and cleanup occur after every process terminates.
- [ ] Independent static task review; root verifies every finding and applies only in-scope corrections. Commit exact task files while preserving dirty AGENTS.md.
- [ ] Freeze the candidate and complete a fresh four-leg gate with the whole slice and affected consumers. Require integrity, successful CI, exact commit/tree/remote checks and the owner-authorized merge before S10 implementation. Stop for owner input only at the standing design-defect boundary or immediately before deployment.

## Primary interface references

- https://antigravity.google/docs/cli/headless/ (`agy models`)
- https://antigravity.google/docs/plugins?tab=cli (plugin management)
- https://geminicli.com/docs/extensions/ (`gemini extensions list`)

These references establish documented commands, not installed-version output formats or provider side-effect guarantees. Live help gates the optional inventory; synthetic tests establish this helper's argv and output behavior.
