# Review Containment Disclosure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** State exactly what review fingerprints detect and what native reviewer execution leaves outside their preventive and observational boundary.

**Architecture:** Extend the existing final leg-contract paragraph only. Protect the distributed reference contract with focused assertions; do not change permissions, tool access, fingerprint inputs, or verification timing.

**Tech Stack:** Markdown skill contract, pytest 9, Python 3.12.

## Global Constraints

- Keep no-edit and no-external-state behavior prompt-controlled.
- Preserve all provider-native tools, installed CLI tools, configured MCP tools, and approved reads/searches.
- Do not add a sandbox, network monitor, new fingerprint, serialization, or parallelism control.
- Production net delta: 0 lines; novel algorithmic core: 0 lines; behavioral claims: 1; S-class.
- Work from `/Users/chaniri/codex_workspace`; run direct Python through `/bin/zsh -lic` with the nested test path.

---

### Task 1: Publish the exact detection boundary

**Files:**
- Modify: `tests/test_distribution_contract.py`
- Modify: `skills/triad-cross-family-review/references/leg-contracts.md`

**Interfaces:**
- Consumes: the distributed `leg-contracts.md` reference and existing prepared/worktree verification.
- Produces: an explicit human-readable compensating-control boundary; no runtime interface change.

- [ ] **Step 1: Write the failing distribution-contract assertions**

In `test_formal_routes_are_explicit_and_reviewer_only`, after the existing
permission/tool assertions, add:

```python
    assert (
        "The prepared-directory digest and canonical-worktree fingerprint monitor "
        "exactly those two surfaces"
        in compact_leg_contracts
    )
    assert (
        "mutation outside both surfaces and network egress of packet content are "
        "neither prevented nor detected by those fingerprints"
        in compact_leg_contracts
    )
    assert (
        "a mid-round mutation may affect another leg's reads before final verification"
        in compact_leg_contracts
    )
    assert (
        "invalidates the complete round and discards every verdict"
        in compact_leg_contracts
    )
```

These assertions protect the shipped reference contract that operators rely on;
they do not attempt to test sandbox behavior that the product does not provide.

- [ ] **Step 2: Run the selector and verify RED**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py::test_formal_routes_are_explicit_and_reviewer_only'
```

Expected: FAIL on the first missing disclosure.

- [ ] **Step 3: Extend only the final containment paragraph**

Replace the final two sentences of `leg-contracts.md` with:

```text
The no-edit contract is prompt-controlled unless runtime metadata proves a
stronger boundary. Mutation detection, not a sandbox claim, decides admission.
The prepared-directory digest and canonical-worktree fingerprint monitor exactly
those two surfaces. Because legs retain native tools, mutation outside both
surfaces and network egress of packet content are neither prevented nor detected
by those fingerprints. Legs run in parallel against the same prepared directory,
so a mid-round mutation may affect another leg's reads before final verification.
A mismatch invalidates the complete round and discards every verdict; verification
does not retroactively prevent the mutation.
```

- [ ] **Step 4: Run focused verification and verify GREEN**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py::test_formal_routes_are_explicit_and_reviewer_only'
```

Expected: PASS.

- [ ] **Step 5: Run the full distribution-contract module**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'python3 -m pytest -q workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py'
```

Expected: all distribution-contract tests PASS.

- [ ] **Step 6: Check patch hygiene and commit only this slice**

Run `git diff --check`, stage the two listed files, and commit:

```bash
git add tests/test_distribution_contract.py skills/triad-cross-family-review/references/leg-contracts.md
git commit -m "docs: disclose review containment limits"
```
