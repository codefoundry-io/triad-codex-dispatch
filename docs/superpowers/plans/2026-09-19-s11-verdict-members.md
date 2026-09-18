# S11: Reject duplicate members in raw verdict files

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Root writes source/tests; fresh dedicated executors observe RED/GREEN and independent reviewers report findings.

**Goal:** Reject ambiguous repeated JSON members before existing strict verdict-file validation.

**Architecture:** Keep the secure canonical regular-file read and validate the same bytes through two narrow steps: a duplicate-member scan and the unchanged Pydantic model/identity validation. The object-pairs hook applies to every object. There is no wrapper/provider parsing redesign or repair loop.

**Tech Stack:** Python 3.12+ json, existing Pydantic, pytest.

**Spec:** `../specs/2026-09-18-dispatch-adoption-design.md`, selected S11 raw `validate --result-file` transport.

## Entry, boundary and budget

- Start only after S10's gate, CI and authorized merge.
- Preserve all dirty AGENTS.md, source identity guards, model semantics, binding checks and result JSON schema.
- This is a new lexical constraint, not a claim that the existing semantic contract promised duplicate rejection. Earlier provider wrappers may already deserialize/reserialize JSON and are outside this guard's coverage.
- No new input byte/depth policy, extra parser framework, dependency, retry, provider call, permissions or deployment.
- Expected production +18/-3, novel core below 20; tests about +75, docs about +25.

## Task 1: Raw-file ambiguity guard

**Files:** `bin/verdict_schema.py`, `tests/test_verdict_schema.py`, `README.md`, `README.ko.md`, `SECURITY.md`.

- [ ] Extend the direct-file tests with literal raw JSON containing top-level `verdict: NOT-SAFE` then `verdict: SAFE`, identical duplicated `family`, nested finding `severity: Major` then `severity: Minor`, and escaped-equivalent `verdict` keys. Keep the last-value form otherwise valid so existing semantic rejection cannot make the test pass accidentally. Do not construct duplicate-bearing objects with dicts.
- [ ] Add a real CLI refusal test for `validate --result-file`, expecting exit2, empty stdout and fixed duplicate-member error text. Add malformed/deep raw input compatibility and a valid unique-member positive case; preserve the existing symlink/identity tests.
- [ ] Fresh dedicated Terra/high/fork-none executor observes the intended RED against the canonical source; capture complete terminal results and matching pre/post identity, then exact cleanup.
- [ ] Add a private object-pairs hook that records decoded member names and raises `ValueError('duplicate JSON member')` when repeated. Do not reflect the member name. Read raw bytes once, call `json.loads(raw, object_pairs_hook=...)`, discard that decoded value, and pass the same raw bytes to `LegVerdict.model_validate_json(raw, strict=True)`. Convert only scan `RecursionError` to a fixed `ValueError` so the existing CLI error path handles it; retain semantic and identity validation.
- [ ] Document the raw-file-only coverage and preserved provider/admission behavior in EN/KO/security guidance.
- [ ] Fresh dedicated executor runs focused GREEN, full suite, source skill validator and provider-free lifecycle, with actual durable terminal receipts, final source identity and exact owned-fixture cleanup.
- [ ] Independent static task review, root adjudication, scoped commit, four-leg gate/integrity, CI and authorized merge. Preserve the standing design-defect stop boundary. At campaign completion, brief the owner with exact evidence and the concrete deployment proposal; obtain their decision before installation/deployment.
