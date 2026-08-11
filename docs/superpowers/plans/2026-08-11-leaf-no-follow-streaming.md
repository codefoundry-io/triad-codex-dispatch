# Leaf No-Follow Streaming File Reads Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure selected regular-file leaves are never followed after symlink substitution, while digest-only paths stream bytes without whole-file buffering.

**Architecture:** Follow the proven Claude-hosted leaf-reader shape, with one reproduced correction: open each selected leaf with `O_RDONLY | O_NONBLOCK | O_NOFOLLOW`, validate the descriptor with `fstat`, and read fixed-size chunks. `O_NONBLOCK` lets a raced-in FIFO reach the non-regular rejection instead of blocking before `fstat`. Keep a byte-returning helper only where callers need payload bytes; use a digest-only helper for prepared-file and untracked-file hashing. Do not introduce root-anchored component traversal or a generalized filesystem abstraction in this slice.

**Tech Stack:** Python 3.12 standard library (`os.open`, `O_NOFOLLOW`, `fstat`, `os.read`), pytest 9, macOS and Linux/WSL2.

## Global constraints

- S-class: 35-70 production lines, 25-50 novel-core lines, one behavioral claim.
- Preserve current digest and diagnostic formats.
- Intermediate-component substitution and unrelated lifecycle readers are outside this Claude-parity slice.
- Root authors tests and code; fresh `triad-skill-executor` instances alone execute RED/GREEN.

---

### Task 1: Author leaf-race and streaming RED tests

**Files:**
- Modify: `tests/test_review_round.py`

- [ ] Add a deterministic prepared-file race that swaps the regular leaf to a symlink at the read boundary and proves the current path read follows the escape target.
- [ ] Add the same leaf substitution through the untracked fingerprint arm and require fail-closed behavior.
- [ ] Add prepared and untracked FIFO substitutions that require `O_NONBLOCK` and reach the `fstat` non-regular rejection without hanging.
- [ ] Add a multi-chunk digest case that matches `hashlib.sha256`, never calls `Path.read_bytes()` for the digest-only path, and never requests more than the fixed chunk size.
- [ ] Preserve existing rejection of non-regular prepared entries and existing untracked symlink representation.

### Task 2: Obtain RED from a fresh dedicated executor

- [ ] Spawn `agent_type="triad-skill-executor"`, `fork_turns="none"`; prohibit edits and providers.
- [ ] Require exact SOT realpath, source commit/status/fingerprint before and after, login-shell Python provenance, focused commands/results, and exact fixture cleanup.
- [ ] Admit RED only when the fixture proves the leaf was substituted and the current implementation followed or whole-buffered it.

### Task 3: Implement Claude-parity leaf readers

**Files:**
- Modify: `bin/review_round.py`

- [ ] Add one fixed chunk-size constant.
- [ ] Replace `_regular_file_bytes()` with `os.open(... O_NONBLOCK | O_NOFOLLOW ...)`, `fstat()` regular-file validation, and chunked reads that return bytes only for payload callers.
- [ ] Add a digest-only regular-file helper using the same open/fstat contract and streaming directly into SHA-256.
- [ ] Route prepared-directory digest, prepared-source comparison, source-manifest creation/verification, and the untracked regular-file arm through the digest helper.
- [ ] Keep symlink payload hashing, record framing, and digest output bytes unchanged.

### Task 4: Obtain GREEN and regression evidence

- [ ] A separate fresh executor runs the focused cases, all `tests/test_review_round.py`, the complete `tests/` suite, the skill validator, and `git diff --check`.
- [ ] After commit, a fresh executor runs the clean-HEAD distribution verifier.
- [ ] Require unchanged source provenance and exact cleanup; otherwise classify the skill `UNTESTED`.

### Task 5: Commit and run the operational gate

- [ ] Stage only this slice's source, tests, and corrected plan/spec; commit as `fix: no-follow review file hashing`.
- [ ] The root leader runs a fresh-ID three-family implementation review focused on descriptor lifetime, leaf substitution, streaming memory, unchanged formats, and the explicit intermediate-component non-goal.
- [ ] Reproduce findings; any bounded correction repeats GREEN and the complete three-leg review.
