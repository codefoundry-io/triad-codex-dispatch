# Fingerprint Index-Flag Refusal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refuse to emit a worktree fingerprint when tracked entries are hidden by `assume-unchanged` or `skip-worktree`.

**Architecture:** Parse the NUL-delimited `git ls-files -v` inventory at every fingerprint boundary, fail before digest return on a forbidden tag, and bind the accepted raw inventory as an `INDEXFLAGS` record. Sparse checkout gets a dedicated diagnostic; ordinary paths use escaped rendering.

**Tech Stack:** Python 3.12 standard library, Git index plumbing, pytest 9.

## Global constraints

- S-class: 40-80 production lines, 30-50 novel-core lines, one behavioral claim.
- Begin only after the preceding slice is committed and independently reviewed.
- Root authors tests and code; fresh `triad-skill-executor` instances alone execute RED/GREEN.

---

### Task 1: Author hidden-mutation RED tests

**Files:**
- Modify: `tests/test_review_round.py`

- [ ] Prove the fixture: after `git update-index --assume-unchanged source.py` and a file rewrite, status, cached diff, and unstaged diff are empty and the pre-change fingerprint stays equal.
- [ ] Assert `_worktree_fingerprint()` instead raises `RoundIntegrityError` naming `assume-unchanged` and an escaped repository-relative path.
- [ ] Add equivalent cases for uppercase `S` (`skip-worktree`) and lowercase `s` (both flags).
- [ ] Add a sparse-checkout case whose diagnostic names sparse checkout and does not recommend `--no-skip-worktree`.
- [ ] Add success coverage for an ordinary index, `capture_round`, `verify_round`, and the `fingerprint-worktree` CLI.

### Task 2: Obtain RED from a fresh dedicated executor

- [ ] Spawn `agent_type="triad-skill-executor"`, `fork_turns="none"`; prohibit edits and providers.
- [ ] Require exact SOT realpath, source commit/status/fingerprint before and after, login-shell Python provenance, focused commands/results, and fixture cleanup.
- [ ] Admit RED only when the hidden-mutation precondition passes and the missing refusal is the failure.

### Task 3: Implement fail-closed index inventory

**Files:**
- Modify: `bin/review_round.py`

- [ ] Add a helper that obtains `git ls-files -v -z`, rejects malformed records, and classifies `tag.islower()` as assume-unchanged and `tag == b"S"` as skip-worktree.
- [ ] Query `core.sparseCheckout` without treating an unset key as a Git inspection failure.
- [ ] For sparse checkout, raise a dedicated refusal that does not prescribe materializing excluded paths.
- [ ] Otherwise report the exact flag and `repr(os.fsdecode(raw_path))`; include only bounded `git update-index --no-assume-unchanged` or `--no-skip-worktree` guidance applicable to that flag.
- [ ] After accepting every record, bind the untouched NUL-delimited inventory with `_record(hasher, b"INDEXFLAGS", inventory)` before returning the fingerprint.

### Task 4: Obtain GREEN and regression evidence

- [ ] A separate fresh executor runs the focused cases, `tests/test_review_round.py`, all `tests/`, and `git diff --check` from the workspace-root login shell.
- [ ] Require unchanged source fingerprint and complete fixture cleanup; otherwise classify `UNTESTED`.

### Task 5: Commit and run the operational gate

- [ ] Stage only this slice's source and tests; commit as `fix: refuse fingerprint-blinding index flags`.
- [ ] The root leader runs a fresh-ID three-family implementation review focused on Git tag parsing, sparse-checkout semantics, non-UTF-8/control-character diagnostics, and capture/verify/CLI coverage.
- [ ] Reproduce findings and restart the complete slice gate for any bounded correction.
