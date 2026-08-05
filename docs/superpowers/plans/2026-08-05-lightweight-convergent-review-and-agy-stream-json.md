# Lightweight Convergent Review and AGY Stream-JSON Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace batch/full-coverage review with a distributable, benchmarked three-family convergence loop and migrate Google review to AGY 1.1.10 native stream-JSON with explicit high effort.

**Architecture:** One focused immutable directory is reviewed once by each family per round. Every leg returns the same compact `LegVerdict`; the leader reproduces findings, applies only bounded corrections inside the approved design, asks the owner before design/specification changes, and starts a fresh three-family round after material changes. Batch receipts, patch shards, coverage admission, PTY/sentinel/transcript extraction, and compatibility-only formal schemas are removed.

**Tech Stack:** Python 3.12, Pydantic 2, pytest, Bash bootstrap, Codex plugin manifest, Claude CLI, AGY 1.1.10, native Codex subagents.

## Global Constraints

- Modify only `/Users/chaniri/codex_workspace/**`; `/Users/chaniri/triad-dispatch` is read-only reference material.
- Formal AGY uses `--model gemini-3.1-pro-high --effort high` with `--output-format stream-json --json-schema`.
- Reviewers inspect and judge only; they do not edit or execute candidate code, tests, builds, hooks, or generated scripts.
- The Codex leader is the only writer and reproduces every finding before acting.
- Design/specification changes, generalizations, new capabilities, and scope expansions require an explicit owner decision before editing.
- One round means one Claude, one Google-family, and one fresh Codex leg. Bounded fixes create fresh rounds until unanimous admissible `SAFE`, owner adjudication, or evidence-backed conflict/oscillation.
- No batch/full-coverage compatibility path remains in active runtime, skills, package inventory, or current documentation.
- Source-only success is insufficient: verify packaged bytes and a fresh process. Remote push, tag, release, or publication is out of scope without separate authorization.
- Run every direct `python3` command via `/bin/zsh -lic` with `/Users/chaniri/codex_workspace` as cwd and the literal `python3` name.

---

## File Map

**Create**

- `bin/verdict_schema.py`: compact `LegFinding`/`LegVerdict` schema and validation CLI.
- `bin/review_round.py`: prepared-directory digest, worktree fingerprint snapshot/verify, and shared prompt rendering.
- `bin/review_policy_benchmark.py`: deterministic benchmark aggregation and policy decision.
- `tests/test_verdict_schema.py`, `tests/test_review_round.py`, `tests/test_antigravity_stream_json.py`, `tests/test_review_policy_benchmark.py`.
- `benchmarks/review-policy/cases.json`, `benchmarks/review-policy/baseline-batched.json`.
- `skills/triad-cross-family-review/references/leg-contracts.md`, `skills/triad-cross-family-review/references/convergence.md`.
- `docs/status/2026-08-05-lightweight-review-red-baseline.md`, `docs/status/2026-08-05-lightweight-review-benchmark.md`, `docs/status/2026-08-05-v0.2.533-release-candidate.md`.

**Rewrite or modify**

- `skills/triad-cross-family-review/SKILL.md` and `references/review-prompt-contract.md`.
- All four provider `SKILL.md` files.
- `bin/antigravity_wrapper.py`, `bin/_common.py`.
- `scripts/bootstrap.sh`, `.codex-plugin/plugin.json`, `CHANGELOG.md`, `README.md`, `README.ko.md`, `SECURITY.md`.
- `tests/test_distribution_contract.py`, `tests/test_provider_packet_context.py`, `tests/test_bootstrap.py`, `tests/test_log_cleanup.py`, `tests/test_migration_contract.py`.

**Delete after replacement tests pass**

- `bin/review_evidence.py`, `bin/review_coverage.py`, `bin/triad_formal_review_schema.py`, `bin/_pty.py`.
- `tests/test_review_evidence.py`, `tests/test_review_coverage.py`, `tests/test_formal_review_schema.py`, `tests/test_antigravity_packet_context.py`, `tests/test_pty_process_group.py`.
- `skills/triad-cross-family-review/references/fresh-codex-formal-review.md`, `skills/triad-cross-family-review/references/reviewer-routing.md` after required rules are folded into the two focused references.

---

### Task 1: Capture RED Policy and Benchmark Baselines

**Files:**
- Create: `benchmarks/review-policy/cases.json`
- Create: `benchmarks/review-policy/baseline-batched.json`
- Create: `tests/test_review_policy_benchmark.py`
- Create: `docs/status/2026-08-05-lightweight-review-red-baseline.md`

**Interfaces:**
- Consumes: existing R46 artifacts and current skill behavior.
- Produces: literal synthetic cases and captured old-policy metrics consumed by Task 6.

- [ ] **Step 1: Record the Python environment**

Run from `/Users/chaniri/codex_workspace`:

```bash
/bin/zsh -lic 'command -v python3; python3 --version; python3 -m pytest --version'
```

Expected: login-shell Python 3.12.x and pytest. If missing, record the exact result before changing dependencies.

- [ ] **Step 2: Write the failing aggregate test**

```python
def test_focused_policy_replaces_captured_batch_fanout_without_losing_recall():
    report = benchmark.aggregate(BASELINE, FOCUSED_RESULTS, CASES)
    assert report["focused"]["calls_per_round"] == 3
    assert report["baseline"]["calls_per_round"] == 24
    assert report["focused"]["planted_defect_recall"] == 1.0
    assert report["focused"]["contract_validity_rate"] == 1.0
    assert report["focused"]["batch_artifacts"] == 0
```

The production change is the benchmark aggregator and focused result set; the test fails now because both are absent.

- [ ] **Step 3: Verify RED**

```bash
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_policy_benchmark.py -q'
```

Expected: missing module/fixture failure.

- [ ] **Step 4: Run five fresh no-guidance policy samples**

Use one fixed pressure scenario combining deadline, sunk compatibility cost, a request to keep full coverage, and a reviewer proposing an unapproved generalization. Record verbatim whether samples preserve batching, stop after one round, implement the design change, or omit package verification. No private source leaves the workspace.

- [ ] **Step 5: Commit RED evidence**

```bash
git add benchmarks/review-policy tests/test_review_policy_benchmark.py docs/status/2026-08-05-lightweight-review-red-baseline.md
git commit -m "test: capture lightweight review policy baseline"
```

---

### Task 2: Add Compact Verdict and Round Integrity

**Files:**
- Create: `bin/verdict_schema.py`, `bin/review_round.py`
- Create: `tests/test_verdict_schema.py`, `tests/test_review_round.py`

**Interfaces:**
- Produces: `validate_verdict_file(path, expected_review_id, expected_family, expected_content_digest) -> LegVerdict`.
- Produces: `capture_round(prepared_dir: Path, worktree: Path) -> RoundSnapshot`, `verify_round(snapshot, prepared_dir, worktree) -> None`, and `render_review_prompt(brief: ReviewBrief) -> str`.

- [ ] **Step 1: Write strict verdict RED tests**

```python
def test_safe_rejects_open_question():
    with pytest.raises(ValidationError):
        LegVerdict.model_validate({**VALID, "verdict": "SAFE", "open_questions": ["Choose API semantics"]})

def test_not_safe_requires_blocker_or_open_question():
    with pytest.raises(ValidationError):
        LegVerdict.model_validate({**VALID, "verdict": "NOT-SAFE", "findings": [], "open_questions": []})

def test_file_validation_binds_family(tmp_path):
    result = write_result(tmp_path, family="claude", content_digest="a" * 64)
    with pytest.raises(ValueError, match="family mismatch"):
        validate_verdict_file(result, "r1", "google", "a" * 64)
```

- [ ] **Step 2: Write round-integrity RED tests**

```python
def test_verify_round_rejects_prepared_mutation(prepared, worktree):
    snapshot = capture_round(prepared, worktree)
    (prepared / "source.py").write_text("changed\n")
    with pytest.raises(RoundIntegrityError, match="prepared directory digest mismatch"):
        verify_round(snapshot, prepared, worktree)

def test_capture_round_rejects_symlink(prepared, worktree):
    (prepared / "escape").symlink_to(worktree / "outside.py")
    with pytest.raises(RoundIntegrityError, match="symlink"):
        capture_round(prepared, worktree)
```

- [ ] **Step 3: Verify RED**

```bash
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_verdict_schema.py workspace/triad-codex-dispatch-reliability/tests/test_review_round.py -q'
```

- [ ] **Step 4: Implement minimal strict models**

```python
@dataclass(frozen=True)
class ReviewBrief:
    review_id: str
    review_kind: Literal["formal-plan", "pre-merge", "implementation-review"]
    objective: str
    prepared_dir: Path
    content_digest: str
    criteria: tuple[str, ...]
    approved_boundary: tuple[str, ...]

@dataclass(frozen=True)
class RoundSnapshot:
    prepared_dir: str
    prepared_digest: str
    worktree: str
    worktree_fingerprint: str

class LegFinding(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    severity: Literal["Critical", "Major", "Minor"]
    path: str
    line: int | None = Field(default=None, ge=1)
    trigger: str
    evidence: str
    correction: str

class LegVerdict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    review_id: str
    family: Literal["claude", "google", "codex"]
    content_digest: str
    verdict: Literal["SAFE", "NOT-SAFE"]
    criteria_checked: list[str] = Field(min_length=1)
    findings: list[LegFinding]
    affected_surfaces_inspected: list[str] = Field(min_length=1)
    open_questions: list[str]
```

Add strict whitespace/path/digest checks and SAFE/NOT-SAFE cross-field validation. Add tagged, length-prefixed prepared-tree hashing and the existing full Git-visible fingerprint semantics without impact/hunk/batch concepts.

- [ ] **Step 5: Run GREEN and commit**

```bash
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_verdict_schema.py workspace/triad-codex-dispatch-reliability/tests/test_review_round.py -q'
git add bin/verdict_schema.py bin/review_round.py tests/test_verdict_schema.py tests/test_review_round.py
git commit -m "feat: add compact review verdict and round integrity"
```

---

### Task 3: Replace the Skill With a Convergent Three-Leg Policy

**Files:**
- Rewrite: `skills/triad-cross-family-review/SKILL.md`, `references/review-prompt-contract.md`
- Create: `references/leg-contracts.md`, `references/convergence.md`
- Modify: four provider skills, `tests/test_distribution_contract.py`
- Delete after folding: `fresh-codex-formal-review.md`, `reviewer-routing.md`

**Interfaces:**
- Consumes: `verdict_schema:LegVerdict` and `review_round.py`.
- Produces: one round recipe and two result states for leader action: `NEW_ROUND_REQUIRED` and `OWNER_DECISION_REQUIRED`.

- [ ] **Step 1: Add failing consumer-behavior tests**

```python
def test_rendered_prompt_binds_one_focused_round_without_batch_operands():
    prompt = render_review_prompt(BRIEF)
    assert prompt.count(BRIEF.review_id) == 1
    assert prompt.count(BRIEF.content_digest) == 1
    assert BRIEF.prepared_dir.as_posix() in prompt
    assert "LegVerdict" in prompt
    assert "BatchReceipt" not in prompt
    assert "batch_manifest" not in prompt

def test_design_change_pressure_case_requires_owner_decision():
    result = run_recorded_policy_sample(case="reviewer-proposes-new-capability")
    assert result.action == "OWNER_DECISION_REQUIRED"
    assert result.edited is False

def test_bounded_fix_pressure_case_requires_fresh_round():
    result = run_recorded_policy_sample(case="verified-bounded-defect")
    assert result.action == "NEW_ROUND_REQUIRED"
    assert result.next_round_families == ["claude", "google", "codex"]
```

The prompt test exercises the real rendered provider input. The two recorded policy cases are RED/GREEN skill-consumer results, not source-text assertions.

- [ ] **Step 2: Verify RED**

```bash
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -q'
```

- [ ] **Step 3: Write the minimal positive recipe**

```text
authorize exact provider/data boundary
prepare one focused immutable directory
capture digest and worktree fingerprint
start Claude + Google + fresh Codex
validate three LegVerdict objects
verify unchanged evidence/worktree
reproduce and classify findings
bounded defect -> fix, verify, fresh round
design/spec/capability/scope delta -> ask owner before editing
conflict/oscillation -> ask owner; never replay unchanged bytes
all required SAFE -> gate passes
```

Do not add an alternate full-audit mode, batch threshold, per-path receipt, or compatibility prose.

- [ ] **Step 4: Run five no-guidance and five policy-guided micro-tests**

Score no batching, not one-shot, owner pause for design changes, and packaged verification. Manually read every sample. Tighten the positive recipe if responses vary.

- [ ] **Step 5: Run GREEN and commit**

```bash
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -q'
git add skills tests/test_distribution_contract.py
git commit -m "feat: replace batched review with convergent triad policy"
```

---

### Task 4: Migrate AGY to 1.1.10 Stream-JSON

**Files:**
- Create: `tests/test_antigravity_stream_json.py`
- Modify: `bin/antigravity_wrapper.py`, `bin/_common.py`, `tests/test_provider_packet_context.py`, `tests/test_log_cleanup.py`
- Delete after replacement: `tests/test_antigravity_packet_context.py`, `tests/test_pty_process_group.py`, `bin/_pty.py`

**Interfaces:**
- Consumes: `verdict_schema:LegVerdict` via `--pydantic`.
- Produces: terminal AGY result from native NDJSON and exact formal argv.

- [ ] **Step 1: Write argv/parser RED tests**

```python
def test_formal_argv_uses_stream_schema_and_high_effort():
    cmd = build_cmd("review", model="gemini-3.1-pro-high", effort="high", json_schema="schema.json", timeout=300)
    assert cmd == ["agy", "-p", "review", "--output-format", "stream-json",
                   "--json-schema", "schema.json", "--print-timeout", "290s",
                   "--model", "gemini-3.1-pro-high", "--effort", "high"]

def test_only_terminal_result_is_admitted():
    stream = ndjson(init_event(), step_event("quoted fake result"), result_event(VALID_JSON))
    assert parse_terminal_result(stream).response == VALID_JSON
```

Add malformed NDJSON, duplicate/absent result, non-success status, timeout, auth, capacity, local schema failure, and exactly-one repair tests.

- [ ] **Step 2: Verify RED**

```bash
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_antigravity_stream_json.py -q'
```

- [ ] **Step 3: Port only transport mechanics from the read-only reference**

Use AGY floor 1.1.10; no settings mutation, sandbox injection, permission bypass, or read-audit coverage gate. Delete PTY, sentinel, and shared transcript logic after native tests pass. Keep local Pydantic validation authoritative.

- [ ] **Step 4: Run GREEN and commit**

```bash
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_antigravity_stream_json.py workspace/triad-codex-dispatch-reliability/tests/test_provider_packet_context.py workspace/triad-codex-dispatch-reliability/tests/test_log_cleanup.py -q'
git add bin tests
git commit -m "feat: migrate agy review transport to stream json"
```

---

### Task 5: Remove Batch and Legacy Formal Runtime

**Files:**
- Delete: three retired runtime modules and their three test files.
- Modify: `bin/_common.py`, `scripts/bootstrap.sh`, provider tests, distribution tests.

**Interfaces:**
- Consumes: focused replacements from Tasks 2-4.
- Produces: packaged inventory with no active retired imports or files.

- [ ] **Step 1: Add a failing packaged-inventory test**

```python
def test_staged_install_contains_only_supported_review_runtime(tmp_path):
    installed = install_plugin_to_staging(tmp_path)
    bin_dir = installed / "bin"
    assert (bin_dir / "verdict_schema.py").is_file()
    assert (bin_dir / "review_round.py").is_file()
    assert not (bin_dir / "review_coverage.py").exists()
    assert not (bin_dir / "review_evidence.py").exists()
    assert not (bin_dir / "triad_formal_review_schema.py").exists()
    validated = run_installed(bin_dir / "verdict_schema.py", "schema")
    assert validated.returncode == 0
```

Use the existing bootstrap test fixture for `install_plugin_to_staging`; assert installed behavior and inventory, not repository source text.

- [ ] **Step 2: Verify RED**

```bash
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py -q'
```

- [ ] **Step 3: Trace callers, remove runtime, and run GREEN**

Use `rg` across active code, skills, bootstrap, README, and current tests. Historical plans/status may retain labeled history. Delete only after active callers are zero.

```bash
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py workspace/triad-codex-dispatch-reliability/tests/test_provider_packet_context.py -q'
git add -A bin tests skills scripts
git commit -m "refactor: remove batched review runtime"
```

---

### Task 6: Implement and Run the Policy Benchmark

**Files:**
- Create: `bin/review_policy_benchmark.py`
- Modify: `tests/test_review_policy_benchmark.py`
- Create: `docs/status/2026-08-05-lightweight-review-benchmark.md`

**Interfaces:**
- Consumes: literal cases, captured batch baseline, focused provider results.
- Produces: canonical metrics and a policy decision.

- [ ] **Step 1: Implement minimal aggregation**

```python
def aggregate(baseline: dict, focused: dict, cases: list[dict]) -> dict:
    return {"baseline": summarize(baseline, cases),
            "focused": summarize(focused, cases),
            "policy": decide_policy(baseline, focused)}
```

Accept focused policy only when contract validity and planted-defect recall are 1.0, no mutation is admitted, and calls per round are 3. Never select batching.

- [ ] **Step 2: Run deterministic GREEN**

```bash
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_review_policy_benchmark.py -q'
```

- [ ] **Step 3: Run synthetic provider benchmark**

Use only synthetic benchmark data. Run one leg per family per case/round and at least one corrected reconfirmation. Record call count, prompt/result bytes, elapsed time, exposed usage, contract validity, recall, false findings, mutation, and convergence. Do not rerun the old 24-call baseline.

- [ ] **Step 4: Update measured policy and commit**

If focused review misses a planted defect, adjust focused boundary/prompt wording and rerun only that case. Do not restore batching.

```bash
git add bin/review_policy_benchmark.py benchmarks tests/test_review_policy_benchmark.py docs/status/2026-08-05-lightweight-review-benchmark.md skills/triad-cross-family-review
git commit -m "test: benchmark convergent review policy"
```

---

### Task 7: Package and Prove Fresh-Process Behavior

**Files:**
- Modify: manifest, changelog, READMEs, SECURITY, bootstrap and distribution tests.
- Create: `docs/status/2026-08-05-v0.2.533-release-candidate.md`

**Interfaces:**
- Consumes: all prior runtime, skill, and benchmark outputs.
- Produces: versioned `0.2.533` distributable plugin and fresh-process proof.

- [ ] **Step 1: Add failing release assertions**

```python
def test_release_candidate_package_contract(staged_plugin):
    manifest = json.loads((staged_plugin / ".codex-plugin/plugin.json").read_text())
    assert manifest["version"] == "0.2.533"
    assert (staged_plugin / "benchmarks/review-policy/cases.json").is_file()
    help_result = run_installed(staged_plugin / "bin/antigravity_wrapper.py", "--help")
    assert help_result.returncode == 0
    assert "--effort" in help_result.stdout
    assert not (staged_plugin / "bin/review_coverage.py").exists()

def test_fresh_process_reports_convergent_policy(fresh_codex_probe):
    assert fresh_codex_probe.stdout.strip() == "TRIAD_CONVERGENT_REVIEW_0_2_533"
```

The first test validates packaged behavior/inventory. The second is backed by the fresh-process probe executed in Step 5, not by grepping skill source.

- [ ] **Step 2: Verify RED**

```bash
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py workspace/triad-codex-dispatch-reliability/tests/test_distribution_contract.py workspace/triad-codex-dispatch-reliability/tests/test_migration_contract.py -q'
```

- [ ] **Step 3: Update package metadata and current documentation**

Document round convergence, owner design gate, AGY route, benchmark result, and package verification. Keep historical evidence labeled historical.

- [ ] **Step 4: Run complete verification**

```bash
/bin/zsh -lic 'python3 -m pytest workspace/triad-codex-dispatch-reliability/tests -q'
bash -n workspace/triad-codex-dispatch-reliability/scripts/bootstrap.sh
git -C workspace/triad-codex-dispatch-reliability diff --check
git -C workspace/triad-codex-dispatch-reliability diff --cached --check
```

- [ ] **Step 5: Verify packaged bytes and fresh process**

Use the supported install path against an owner-authorized or workspace-contained staging target. Compare hashes, start fresh `codex exec --ephemeral`, require an exact convergence/owner-gate marker, and run installed Claude/AGY smoke calls against synthetic data only.

- [ ] **Step 6: Run final pressure and prompt review gates**

Repeat RED scenarios with the installed skill. Every sample must choose one leg/family/round, fresh reconfirmation, owner pause for design changes, no batch preservation, and packaged verification. Run `skill-prompt-review` and resolve every actionable failure.

- [ ] **Step 7: Commit the release candidate**

```bash
git add .codex-plugin CHANGELOG.md README.md README.ko.md SECURITY.md docs/status tests scripts skills bin benchmarks
git commit -m "chore: prepare 0.2.533 lightweight review release"
```

Do not push, tag, publish, or create a GitHub release without separate owner authorization.
