# Root-Anchored File Hashing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure review-integrity hashing and bounded payload reads never follow a substituted symlink at the selected leaf or any intermediate path component.

**Architecture:** Resolve a normalized path relative to an already selected canonical root, pre-inspect its component chain, then reopen the root and every component with descriptor-relative `O_NOFOLLOW`. Validate every descriptor with `fstat`, stream file bytes in fixed chunks, and compare file identity/state after reading. Fail closed when required primitives are unavailable.

**Tech Stack:** Python 3.12 standard library (`os.open`, `dir_fd`, `O_DIRECTORY`, `O_NOFOLLOW`, `fstat`), pytest 9, macOS and Linux/WSL2.

## Global constraints

- S-class: 80-150 production lines, 70-120 novel-core lines, one behavioral claim.
- Do not generalize into a filesystem abstraction or metadata-preservation feature.
- Root authors all tests/code; two fresh dedicated executor instances establish RED and GREEN.

---

### Task 1: Author deterministic race and streaming RED tests

**Files:**
- Modify: `tests/test_review_round.py`

- [ ] Add a leaf-race test that returns the original `lstat` result, swaps the prepared file to a symlink before the read, and asserts fail-closed behavior rather than hashing the escape target.
- [ ] Add the same deterministic race for an intermediate directory component.
- [ ] Add untracked-file leaf and intermediate substitution cases through `_worktree_fingerprint()`.
- [ ] Cover FIFO/device or directory leaves as unsupported entries.
- [ ] Write a file larger than two 1 MiB chunks, assert the digest matches `hashlib.sha256`, and instrument reads to prove the implementation never requests more than the fixed chunk size or uses `Path.read_bytes()` for digest-only paths.
- [ ] Add a primitive-availability case that removes `O_NOFOLLOW` or descriptor-relative `os.open` support and asserts a bounded fail-closed diagnostic.

### Task 2: Obtain RED from a fresh dedicated executor

- [ ] Spawn `agent_type="triad-skill-executor"`, `fork_turns="none"` with no edits/providers.
- [ ] Require SOT realpath, commit/status/fingerprint before and after, login-shell Python provenance, focused test output, and cleanup.
- [ ] Admit RED only when each attack fixture proves the substitution happened and the current path-based read followed or failed to reject it.

### Task 3: Implement rooted descriptor readers

**Files:**
- Modify: `bin/review_round.py`

- [ ] Add a fixed 1 MiB chunk constant and an availability guard for `O_NOFOLLOW`, `O_DIRECTORY`, and descriptor-relative `os.open`/`os.stat`/`os.readlink` support used by the implementation.
- [ ] Add one helper that validates a relative component chain, opens the canonical root directory with no-follow flags, opens each parent via `dir_fd`, and returns an anchored parent descriptor plus leaf metadata.
- [ ] Add a digest-only regular-file reader that opens the leaf with `O_NOFOLLOW`, checks `S_ISREG`, compares `lstat`/`fstat` identity, streams directly into SHA-256, and verifies device/inode/size/mtime after EOF.
- [ ] Add a bounded payload variant using the same descriptor path only for JSON/prompt callers that require bytes.
- [ ] Add a no-follow symlink-payload branch for the existing untracked symlink representation; never dereference its target.
- [ ] Replace prepared digest/manifest/source-recheck, untracked fingerprint, lifecycle metadata/member-list, and worktree prompt custody reads that currently use lstat-then-path-read. Keep their external formats unchanged.

### Task 4: Obtain GREEN and regression evidence

- [ ] A separate fresh executor runs the focused race/stream tests, all `tests/test_review_round.py`, the complete `tests/` suite, and `git diff --check`.
- [ ] Require unchanged SOT fingerprint and cleanup. Unsupported-platform behavior must be an explicit fail-closed result, not a skip that claims coverage.

### Task 5: Commit and run the operational gate

- [ ] Stage only source/tests for this slice; commit as `fix: anchor review file hashing to descriptors`.
- [ ] The root leader runs a fresh-ID three-family review focused on descriptor lifetime, intermediate-component races, portability, streaming memory, and unchanged digest formats.
- [ ] Reproduce every claim; any bounded fix repeats RED/GREEN and the full three-leg review.
