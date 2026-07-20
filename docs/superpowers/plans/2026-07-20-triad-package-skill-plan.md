# Triad Package Integrity and Skill Convergence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Release `0.3.0` with byte-attested package/cache/source trees, a static runtime report, concise review routers, and one executable documentation contract.

**Architecture:** A stdlib-only manifest CLI owns the closed runtime file set, SHA-256 hashes, version comparison, and source/cache attestation. Bootstrap and `triad-doctor` consume it by argv only; docs and skills expose helpers rather than reconstructing shell commands. The cross-family skill keeps ordinary mode concise and directly links the complete formal contract.

**Tech Stack:** Bash 3.2-compatible bootstrap, Python 3.12 stdlib, pytest, JSON, Markdown/YAML, Codex `execpolicy`, and `skill-prompt-review`.

## Global Constraints

- Set `.codex-plugin/plugin.json`, `package-manifest.json`, and the first `CHANGELOG.md` heading to `0.3.0`. During this unreleased slice the candidate manifest is regenerated as code changes; `compare-release` enforces that any manifested-byte change relative to an already released equal-version manifest requires a new version.
- Manifest exactly covers `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `bin/**/*.py`, `bin/policies/**/*.toml`, `scripts/**/*.sh`, `skills/**/SKILL.md`, `skills/**/agents/openai.yaml`, `skills/**/lib/**/*.py`, `skills/**/references/**/*.md`, and `schemas/**/*.json`. Reject symlinks, absolute/`..` paths, missing required files, and unexpected covered files.
- Entries are sorted POSIX-relative `path`, SHA-256 `sha256`, integer `bytes`, plus `schema_version: 1`, `package`, `version`, and deterministic `tree_sha256`.
- `bootstrap.sh --install` and default `triad-doctor` are offline. Provider calls are exclusive to owner-run `triad-doctor --live`; no `shell=True`, `sh -c`, `bash -c`, `zsh -c`, `eval`, or command-string interface.
- Malformed/mutated package or equal-version source/install drift is `version-config`, exits `78`, and blocks dispatch. Unknown source commit is JSON `null`, never guessed.
- Formal fresh Codex uses a default child with explicit current leader-selected `model`, `reasoning_effort`, and `fork_turns="none"`; record exposed actual values or `unexposed`, never a Custom Agent or `fork_context`. Shipped skill text uses moving-target placeholders rather than pinning an aging model identifier.
- Deterministic tests have no provider dependency. Korean docs remain semantically equivalent to English.
- Every Python/test/lint command is an authoritative run in the user's normal macOS login-terminal environment, outside the filesystem sandbox. First record `command -v python3`, `python3 --version`, and `python3 -m pytest --version`; when it lacks pytest, use the already verified `/opt/homebrew/bin/python3.12` without altering the environment. Snippets assume the repository worktree is supplied as the command working directory.

## File Map

| Path | Change |
|---|---|
| `bin/package_manifest.py` | New deterministic generate/verify/compare-release/attest CLI. |
| `package-manifest.json` | Generated checked-in `0.3.0` runtime manifest. |
| `bin/triad_runtime.py`, `scripts/bootstrap.sh` | Extend Delivery 1's doctor subcommand with the static report/attestation bridge; install remains free of live probe behavior. |
| `tests/test_package_manifest.py`, `tests/test_bootstrap.py`, `tests/test_documentation_contract.py` | Package, hostile argv/large archive, offline bootstrap, and doc/skill regressions. |
| `skills/*/SKILL.md`, `skills/triad-cross-family-review/references/formal-review.md` | Concise helper-first routers and direct formal contract. |
| `README*`, `SECURITY.md`, `migration/*`, metadata, `CHANGELOG.md` | One setup/doctor/attestation/review contract. |

## Interfaces

```text
python3 bin/package_manifest.py generate --root ABS_ROOT --output ABS_ROOT/package-manifest.json --version 0.3.0 --changelog ABS_ROOT/CHANGELOG.md
python3 bin/package_manifest.py verify --root ABS_ROOT --manifest ABS_ROOT/package-manifest.json
python3 bin/package_manifest.py compare-release --previous OLD.json --current NEW.json
python3 bin/package_manifest.py attest --installed-root ABS_CACHE --installed-manifest ABS_CACHE/package-manifest.json [--source-root ABS_SOURCE --source-manifest ABS_SOURCE/package-manifest.json]
triad-doctor --report-json --installed-root ABS_CACHE [--source-root ABS_SOURCE]
```

Successful `attest` returns:

```json
{"status":"ok","error_family":null,"plugin_version":"0.3.0","packaged_manifest_sha256":"<sha256>","installed_tree_sha256":"<sha256>","installed_path":"/absolute/cache","source_path":"/absolute/source-or-null","source_commit":"40-hex-or-null","source_tree_sha256":"<sha256-or-null>","source_matches_installed":true}
```

Integrity failures use the same shape with `status: "error"`, `error_family: "version-config"`, and exit `78`.

---

### Task 1: Define and implement the package manifest contract

**Files:**
- Create: `bin/package_manifest.py`
- Create: `package-manifest.json`
- Create: `tests/test_package_manifest.py`
- Modify: `.codex-plugin/plugin.json`
- Modify: `CHANGELOG.md`

**Interfaces:** Produces the four CLI commands above. Later tasks consume only their JSON/exit contract.

- [ ] **Step 1: Write failing package tests**

Create `tests/test_package_manifest.py` with `run_manifest(*args)` using `subprocess.run([sys.executable, str(MANIFEST), *args], text=True, capture_output=True, check=False)`. Add:

```python
def test_generate_verify_and_closed_runtime_inventory(tmp_path: Path) -> None:
    root = copy_runtime_tree(tmp_path / "root")
    made = run_manifest("generate", "--root", str(root), "--output", str(root / "package-manifest.json"),
                        "--version", "0.3.0", "--changelog", str(root / "CHANGELOG.md"))
    assert made.returncode == 0, made.stderr
    manifest = json.loads((root / "package-manifest.json").read_text())
    assert manifest["schema_version"] == 1 and manifest["version"] == "0.3.0"
    assert "bin/_common.py" in {row["path"] for row in manifest["files"]}
    assert all(not row["path"].startswith(("tests/", "docs/", "bin/_logs/")) for row in manifest["files"])
    assert run_manifest("verify", "--root", str(root), "--manifest", str(root / "package-manifest.json")).returncode == 0

def test_mutation_unlisted_file_and_symlink_fail_closed(tmp_path: Path) -> None:
    root = generated_tree(tmp_path)
    (root / "bin" / "_common.py").write_text("drift\n", encoding="utf-8")
    assert run_manifest("verify", "--root", str(root), "--manifest", str(root / "package-manifest.json")).returncode == 78
    (root / "bin" / "unexpected.py").write_text("x\n", encoding="utf-8")
    assert run_manifest("verify", "--root", str(root), "--manifest", str(root / "package-manifest.json")).returncode == 78
    (root / "bin" / "link.py").symlink_to(root / "bin" / "_common.py")
    assert run_manifest("verify", "--root", str(root), "--manifest", str(root / "package-manifest.json")).returncode == 78

def test_equal_version_source_cache_drift_is_version_config(tmp_path: Path) -> None:
    source, cache = generated_tree(tmp_path / "source"), copied_tree(tmp_path / "cache")
    (cache / "skills" / "triad-claude-dispatch" / "SKILL.md").write_text("drift\n", encoding="utf-8")
    result = run_manifest("attest", "--installed-root", str(cache), "--installed-manifest", str(cache / "package-manifest.json"),
                          "--source-root", str(source), "--source-manifest", str(source / "package-manifest.json"))
    assert result.returncode == 78
    assert json.loads(result.stdout)["error_family"] == "version-config"
```

Add `test_changed_manifest_requires_version_bump`: copy the old manifest, change `bin/_common.py`, generate a candidate with unchanged `0.3.0`, then assert `compare-release` exits `78` with `manifested files changed without a version change`.

- [ ] **Step 2: Verify red state**

Run:

```bash
command -v python3
python3 --version
python3 -m pytest --version
python3 -m pytest -q tests/test_package_manifest.py -p no:cacheprovider
```

Expected: Python is 3.12+; pytest fails because `bin/package_manifest.py` does not exist.

- [ ] **Step 3: Implement the closed manifest CLI**

Create `bin/package_manifest.py` with this core, then strict JSON/path/schema validation and atomic output:

```python
EXIT_VERSION_CONFIG = 78
PACKAGE = "triad-codex-dispatch"

def sha256_file(path: Path) -> tuple[str, int]:
    digest, size = hashlib.sha256(), 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk); size += len(chunk)
    return digest.hexdigest(), size

def tree_digest(rows: list[dict[str, object]]) -> str:
    wire = "".join(f"{row['path']}\0{row['sha256']}\0{row['bytes']}\n" for row in rows)
    return hashlib.sha256(wire.encode("utf-8")).hexdigest()
```

Enumerate with `Path.iterdir()` rather than silent glob, reject every symlink, require the global-constraint paths/suffixes, and sort by POSIX path. `generate` requires metadata version and heading `## 0.3.0 —` and writes `indent=2`, `sort_keys=True` plus newline using `mkstemp`/`os.replace`. `attest` verifies installed first, compares optional source manifest/tree/version, and runs `git -C <source> rev-parse HEAD` only as argv with `shell=False`; a non-Git source returns `null` commit.

- [ ] **Step 4: Update release values, generate, and prove green**

Set metadata version to `0.3.0` and insert first changelog release:

```markdown
## 0.3.0 — 2026-07-20

**Reliability redesign.** Package bytes are SHA-256 attested at install and doctor time; setup/live verification is owner-triggered; immutable review and concise skill routers share one runtime contract.
```

Run:

```bash
python3 bin/package_manifest.py generate --root "$PWD" --output "$PWD/package-manifest.json" --version 0.3.0 --changelog "$PWD/CHANGELOG.md"
python3 bin/package_manifest.py verify --root "$PWD" --manifest "$PWD/package-manifest.json"
python3 -m pytest -q tests/test_package_manifest.py -p no:cacheprovider
```

Expected: all commands exit `0`; negative tests retain `78`.

- [ ] **Step 5: Commit**

```bash
git add bin/package_manifest.py package-manifest.json tests/test_package_manifest.py .codex-plugin/plugin.json CHANGELOG.md
git commit -m "feat: attest packaged runtime bytes"
```

---

### Task 2: Bridge static package attestation into bootstrap and doctor

**Files:**
- Modify: `scripts/bootstrap.sh`
- Modify: `bin/triad_runtime.py`
- Modify: `tests/test_bootstrap.py`
- Modify: `tests/test_documentation_contract.py`

**Interfaces:** Consumes Task 1. Produces offline install attestation at the XDG `triad-codex-dispatch/install-attestation.json` location and `triad-doctor --report-json`.

- [ ] **Step 1: Write failing static-boundary tests**

Replace live-auth assertions in `tests/test_bootstrap.py` with:

```python
def test_install_is_static_and_never_runs_provider_commands(tmp_path):
    marker = tmp_path / "provider-called"
    scripts = {name: f"touch {marker}\nexit 91" for name in ("codex", "claude", "agy", "gemini")}
    result, _env, _launchers = _run_bootstrap(tmp_path, fake_scripts=scripts, arg="--install")
    assert result.returncode == 0, result.stderr + result.stdout
    assert not marker.exists()
    assert "provider probes are available only through triad-doctor --live" in result.stdout

def test_install_records_static_attestation_and_blocks_drift(tmp_path):
    result, env, _launchers = _run_bootstrap(tmp_path, arg="--install")
    assert result.returncode == 0, result.stderr + result.stdout
    record = Path(env["XDG_CONFIG_HOME"]) / "triad-codex-dispatch" / "install-attestation.json"
    assert json.loads(record.read_text())["status"] == "ok"
    repo = Path(env["TRIAD_BOOTSTRAP_REPO_ROOT"])
    (repo / "bin" / "_common.py").write_text("drift\n")
    rerun, _env2, _launchers2 = _run_bootstrap(tmp_path, repo_root=repo, arg="--install")
    assert rerun.returncode == 78 and "version-config" in rerun.stderr
```

Add source assertions that bootstrap contains neither `run_auth_probe` nor `shell=True` and invokes doctor with literal `--report-json`, `--installed-root`, and `--source-root` argv elements.

- [ ] **Step 2: Verify red state**

Run:

```bash
python3 -m pytest -q tests/test_bootstrap.py -p no:cacheprovider
```

Expected: failures name the current live probe path and absent doctor/attestation.

- [ ] **Step 3: Implement the offline bridge**

Delivery 1 already deleted `AUTH_TIMEOUT`, `run_auth_probe`, `check_auth`, and `TRIAD_BOOTSTRAP_SKIP_AUTH` handling. Preserve that absence. After canonical path validation and before launchers, run by argv:

```bash
python3 "$REPO_ROOT/bin/package_manifest.py" verify --root "$REPO_ROOT" --manifest "$REPO_ROOT/package-manifest.json"
```

On failure preserve diagnostic JSON, record `version-config`, and exit `78` before mutable installer work. Add `--report-json`, `--installed-root`, `--source-root`, and `--write-attestation` to the existing `doctor` subcommand in `bin/triad_runtime.py` and therefore to the generated `triad-doctor` launcher. Make `--workspace` conditionally required for normal static/live doctor mode and reject it as ambiguous when it conflicts with report roots; report mode requires `--installed-root` and derives its source boundary from the explicit optional `--source-root`. Build the helper command as a list:

```python
command = [sys.executable, str(package_helper), "attest", "--installed-root", str(installed_root),
           "--installed-manifest", str(installed_root / "package-manifest.json")]
if source_root is not None:
    command += ["--source-root", str(source_root), "--source-manifest", str(source_root / "package-manifest.json")]
result = subprocess.run(command, text=True, capture_output=True, shell=False, check=False)
```

Require `--installed-root` for report mode and reject `--report-json --live`. Relay helper `78` and JSON unchanged; atomically write successful report with RFC-3339 `installed_at_utc`. Bootstrap calls static doctor after local artifacts, prints `provider probes are available only through triad-doctor --live` and `new Codex session required when runtime configuration changed`.

- [ ] **Step 4: Green verification and commit**

Run:

```bash
python3 -m pytest -q tests/test_bootstrap.py tests/test_package_manifest.py -p no:cacheprovider
bash -n scripts/bootstrap.sh
python3 bin/triad_runtime.py doctor --report-json --installed-root "$PWD" --source-root "$PWD"
```

Expected: all exit `0`; report has `status: "ok"`, `plugin_version: "0.3.0"`, matching tree digests, absolute installed path, and `source_matches_installed: true`, with no provider call.

```bash
git add scripts/bootstrap.sh bin/triad_runtime.py tests/test_bootstrap.py tests/test_package_manifest.py package-manifest.json
git commit -m "feat: report installed package attestation"
```

---

### Task 3: Converge skill routers, formal reference, metadata, and documentation

**Files:**
- Modify: `skills/triad-{claude,antigravity,gemini}-dispatch/SKILL.md`
- Modify: `skills/triad-cross-family-review/SKILL.md`
- Create: `skills/triad-cross-family-review/references/formal-review.md`
- Modify: `skills/*/agents/openai.yaml`, `.agents/plugins/marketplace.json`
- Modify: `README.md`, `README.ko.md`, `SECURITY.md`, `migration/COMPANY-SETUP.md`, `migration/COMPANY-SETUP.ko.md`, `migration/AGENTS.recommended.md`, `migration/triad-codex-dispatch.rules`, `CHANGELOG.md`
- Create: `tests/test_documentation_contract.py`

**Interfaces:** Router calls use an absolute generated launcher plus `--prompt-file`. Formal review uses `<review-record>/packet/{manifest.json,manifest.sha256,coverage.json,brief.md,inputs/,context/}` as the immutable boundary and sibling `<review-record>/{exports/,receipts/,verdicts/,provenance/,resolution/}` trees for provider material and mutable results.

- [ ] **Step 1: Add documentation/router red tests**

Create `tests/test_documentation_contract.py`:

```python
def test_docs_name_the_single_install_setup_doctor_contract() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in ACTIVE_DOCS)
    for word in ("triad-setup", "triad-doctor", "package-manifest.json", "version-config"):
        assert word in text
    for stale in ("TRIAD_BOOTSTRAP_SKIP_AUTH", "fork_context=false", "custom repair agent"):
        assert stale not in text

def test_cross_family_router_has_direct_formal_reference() -> None:
    router = (ROOT / "skills/triad-cross-family-review/SKILL.md").read_text(encoding="utf-8")
    assert "references/formal-review.md" in router
    assert 'fork_turns="none"' in router
    assert (ROOT / "skills/triad-cross-family-review/references/formal-review.md").is_file()

def test_documented_helpers_exist_in_help() -> None:
    doctor = subprocess.run([sys.executable, str(ROOT / "bin/triad_runtime.py"), "doctor", "--help"], text=True, capture_output=True)
    assert doctor.returncode == 0 and "--report-json" in doctor.stdout
    attest = subprocess.run([sys.executable, str(ROOT / "bin/package_manifest.py"), "attest", "--help"], text=True, capture_output=True)
    assert attest.returncode == 0 and "--installed-manifest" in attest.stdout
```

Also assert every `SKILL.md` is below 160 lines and contains none of `bash -lc`, `zsh -lc`, `P=$(codex exec`, `fork_context`, or hand-built repair shell programs.

- [ ] **Step 2: Verify red state**

Run:

```bash
python3 -m pytest -q tests/test_documentation_contract.py -p no:cacheprovider
```

Expected: it fails for the absent formal reference and stale bootstrap/repair/reviewer claims.

- [ ] **Step 3: Write the concise contract**

Keep each dispatch skill frontmatter but reduce body to `Use when`, `Do not use when`, `Required inputs`, `Run`, `Classify result`, `Repair`, and `See also`. `Run` gives only this argv shape:

```text
<absolute-launcher> --cwd <absolute-workspace> --sandbox read-only --prompt-file <absolute-utf8-prompt-file>
```

State that quotes, dollar signs, backticks, newlines, leading dashes, and multi-line prompts go through the bundled helper to one UTF-8 file; do not show shell construction. State `auth`, `packet-integrity`, and `nonconvergence` are never blindly retried.

Cross-family router keeps ordinary mode (build/verify archive; Claude + selected Google + fresh Codex receive identical hashes; wait, reconcile cited evidence, log missing legs) and ends exactly:

```markdown
For formal mode, read and follow [Formal review contract](references/formal-review.md) before creating a packet.
```

Its native Codex text is exactly: `spawn a fresh default child with model="<selected-codex-model>", reasoning_effort="<selected-reasoning-effort>", and fork_turns="none"; substitute explicit current policy values, record requested values/task identity and exposed actual values or "unexposed"; no-edit containment is prompt-controlled unless the runtime exposes an enforced boundary.`

The formal reference has sections `When formal mode is required`, `Freeze the archive`, `Provider exports and prompts`, `Independent legs`, `Verdict schema and acceptance`, `Failure handling`, and `Owner resolution`. It requires hash rechecks, untrusted archive fencing, archive-relative citations, `files_inspected`, `coverage_gaps`, and explicit finding resolution. Missing Claude/Google/Codex is `required_leg_unavailable` and invalidates formal mode; it is never replaced by another family.

Update both READMEs/company guides to show:

```bash
"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --install
triad-setup --workspace "$(pwd -P)"
triad-doctor
triad-doctor --live
```

State install is offline/static; setup records workspace authorization/no-prompt choices but no credentials; `--live` is owner action whose failure does not undo install; equal-version digest mismatch blocks dispatch. Remove live bootstrap probe, personal repair-agent, and `fork_context` claims. Update `SECURITY.md` to Deliverable-3 fresh in-session repair analyzer (bounded redacted record, no provider/edit instruction, prompt-controlled containment if unenforced) and `bin/apply_patch.py` as sole locked/atomic persistence writer. Set YAML short descriptions to: `Run an argv-safe single-shot Claude leg with classified results`, `Run an argv-safe single-shot agy Google-family leg`, `Run an argv-safe business-tier Gemini leg`, and `Build immutable packets and run ordinary or formal three-family review`.

- [ ] **Step 4: Green verification and commit**

Run:

```bash
python3 -m pytest -q tests/test_documentation_contract.py -p no:cacheprovider
rg -n 'fork_context|TRIAD_BOOTSTRAP_SKIP_AUTH|run_auth_probe|shell=True|custom repair agent|P=\$\(codex exec' README.md README.ko.md SECURITY.md migration skills scripts bin
python3 bin/package_manifest.py generate --root "$PWD" --output "$PWD/package-manifest.json" --version 0.3.0 --changelog "$PWD/CHANGELOG.md"
python3 bin/package_manifest.py verify --root "$PWD" --manifest "$PWD/package-manifest.json"
```

Expected: pytest/manifest commands exit `0`; `rg` exits `1` with no output.

```bash
git add skills .agents README.md README.ko.md SECURITY.md migration CHANGELOG.md tests/test_documentation_contract.py package-manifest.json
git commit -m "docs: converge attested triad workflow"
```

---

### Task 4: Prove hostile argv/long archive behavior and run the final skill-prompt gate

**Files:**
- Modify: `tests/test_package_manifest.py`, `tests/test_bootstrap.py`, `tests/test_documentation_contract.py`
- Modify: `migration/COMPANY-SETUP.md`, `migration/COMPANY-SETUP.ko.md`, `package-manifest.json`

**Interfaces:** Consumes Tasks 1-3 and Deliverable-2 packet validation. Produces frozen review evidence and only final test/doc adjustments.

- [ ] **Step 1: Add hostile argv and long-context red tests**

Add a bootstrap/doctor test whose cache directory literal is `cache space ' quote $(not-run)\n--leading`, invokes bootstrap/doctor by `subprocess.run([...])`, and uses fake providers creating a marker. Assert `returncode == 0`, marker absent, `installed_path == str(cache.resolve())`, and `source_matches_installed is True`.

Add a Deliverable-2 packet test: archive `("αβγ\n" * 262_145) + "final sentinel\n"`; assert archive byte count and streaming SHA-256 equal source, then accept a citation to `final sentinel` after line `65536`. Mutate one archived byte and assert acceptance exits `78` with `packet-integrity`. This proves full bytes/citations without a made-up prompt-size limit.

- [ ] **Step 2: Run deterministic release evidence**

Run:

```bash
command -v python3
python3 --version
python3 -m pytest --version
python3 -m pytest -q tests/ -p no:cacheprovider
bash -n scripts/bootstrap.sh
python3 bin/package_manifest.py verify --root "$PWD" --manifest "$PWD/package-manifest.json"
python3 bin/triad_runtime.py doctor --report-json --installed-root "$PWD" --source-root "$PWD"
```

Expected: all exit `0`, no marker exists, and doctor reports matching source/installed digests. Add the latter four release commands to both company guides; state `triad-doctor --live` is intentionally excluded from deterministic release evidence.

- [ ] **Step 3: Run structural lint and freeze exact review inputs**

Run and save reports before review:

```bash
mkdir -p _runs/reviews/0.3.0-skill-review/lint
python3 /Users/chaniri/.codex/skills/skill-prompt-review/scripts/lint.py skills/triad-claude-dispatch/SKILL.md > _runs/reviews/0.3.0-skill-review/lint/claude.txt
python3 /Users/chaniri/.codex/skills/skill-prompt-review/scripts/lint.py skills/triad-antigravity-dispatch/SKILL.md > _runs/reviews/0.3.0-skill-review/lint/antigravity.txt
python3 /Users/chaniri/.codex/skills/skill-prompt-review/scripts/lint.py skills/triad-gemini-dispatch/SKILL.md > _runs/reviews/0.3.0-skill-review/lint/gemini.txt
python3 /Users/chaniri/.codex/skills/skill-prompt-review/scripts/lint.py skills/triad-cross-family-review/SKILL.md > _runs/reviews/0.3.0-skill-review/lint/cross-family.txt
python3 /Users/chaniri/.codex/skills/skill-prompt-review/scripts/lint.py --kind reference skills/triad-cross-family-review/references/formal-review.md > _runs/reviews/0.3.0-skill-review/lint/formal-reference.txt
```

Expected: each exits `0`; hits are candidates, not verdicts. Freeze four skills, formal reference, `openai.yaml` files, lint reports, manifest, documentation test, and exact copies of `skill-prompt-review/references/{common,openai,anthropic,google,ai-authorship}.md` in the named archive. Create one canonical `prompts/skill-review.md`, `manifest.json` with SHA-256/bytes for every input including the prompt and criteria, and `brief.md` requiring per-criterion PASS/FAIL/N-A evidence, positive fixes, and archive-only read behavior. Every leg receives the same canonical prompt bytes; family-specific transport instructions live outside that prompt and are recorded in provenance.

Create two additional immutable behavior controls from the same final skill contract: one clean target expected to pass and one planted-defect target containing a diff-only instruction, a shell-interpolated prompt, and an unresolved affected-code edge. Include a hostile literal path/prompt with a space, quote, newline, leading dash, and `$()` text. Reviewers must classify the planted defects and avoid false findings on the clean control; neither control is executable.

- [ ] **Step 4: Fresh-context review, final green, and commit**

Because Claude capacity is explicitly exhausted for this release window, this final skill/prompt quality gate is an interim four-leg review, not a formal three-family result. Dispatch two independent fresh default Codex reviewers with `fork_turns="none"` and explicit current leader-selected model/effort, plus two independent exact Gemini Pro High legs, all against identical immutable archive and prompt hashes. Each leg receives only the frozen archive, criteria, and lint reports. Record identities, requested selector data, exposed actual values or `unexposed`, and terminal transport classifications.

Immediately before the Google legs, run `agy models` outside the filesystem sandbox and archive its exact output. Select the literal accepted display name matching the owner-requested Gemini Pro High tier and record it in both dispatch records. Invoke the absolute Antigravity launcher twice as separate processes with list-form argv equivalent to `<launcher> --prompt-file <canonical-prompt> --sandbox read-only --model <literal-accepted-display-name> --cwd <review-record> --timeout 600`; no shell variable or command-string reconstruction is part of the executable path. For each Codex leg, archive the direct `spawn_agent` request fields and returned task identity separately.

Record `claude: unavailable` with the standing capacity reason without invoking or replacing it, and label the result `interim-four-leg`. A bare SAFE without per-criterion evidence is invalid and gets one fresh rerun on that same family route. Reconcile evidence rather than votes; contradictory evidence that remains after fact-checking is nonconvergence and stops for owner resolution.

Fact-check FAILs against frozen bytes and require all valid legs to detect the planted defects while preserving the clean control. Fix only evidence-backed product defects, regenerate manifest/tests/lint/archive under a new ID, and stop fact-checked nonconvergence for owner resolution rather than voting. Then run:

```bash
git diff --check
git diff --cached --check
python3 -m pytest -q tests/ -p no:cacheprovider
bash -n scripts/bootstrap.sh
python3 bin/package_manifest.py verify --root "$PWD" --manifest "$PWD/package-manifest.json"
```

Expected: all exit `0`; archive proves independent Codex and every available-provider outcome.

```bash
git add tests/test_package_manifest.py tests/test_bootstrap.py tests/test_documentation_contract.py migration/COMPANY-SETUP.md migration/COMPANY-SETUP.ko.md package-manifest.json
git commit -m "test: verify attested triad release workflow"
```

## Plan Self-Review

The four tasks cover manifest generation/attestation/version discipline, bootstrap/doctor reports, docs/metadata/skill convergence, hostile argv/long archive proof, and the required interim two-Codex plus two-Gemini `skill-prompt-review` gate with Claude capacity recorded honestly. Every interface, file, red test, expected failure, green command, version, error family, and commit is explicit; moving-target selector placeholders are intentional and must be substituted at dispatch.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-20-triad-package-skill-plan.md`.

1. **Subagent-Driven (recommended)** — use `superpowers:subagent-driven-development`, one fresh implementation agent per task plus review between tasks.
2. **Inline Execution** — use `superpowers:executing-plans`, preserving task checkpoints and gates.
