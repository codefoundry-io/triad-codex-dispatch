# Triad Runtime Install Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate deterministic installation from explicit owner setup and classified live verification, without reintroducing shell-parsed probes.

**Architecture:** `scripts/bootstrap.sh` remains the public installer but delegates runtime operations to a new stdlib-only `bin/triad_runtime.py`. Bootstrap performs local artifact installation and static policy checks only; generated `triad-setup` records owner authority and `triad-doctor` is offline unless `--live` is explicitly requested.

**Tech Stack:** Bash 3.2, Python 3.12 standard library, pytest, `tomllib`, native `codex execpolicy check`.

## Global Constraints

- Delivery 1 covers deterministic install/setup/doctor, argv-only probes, static execpolicy checks, bounded aliases, and Gemini hardened ordering only; packet, repair, manifest, and documentation convergence are later deliveries.
- `--install` makes no provider/model call and accepts no arbitrary shell command configuration. Every new process call uses `list[str]` plus `shell=False`.
- Static doctor makes no provider/network call. Live doctor uses absolute launchers, a finite timeout, and preserves `auth`, `sandbox-env`, `quota-capacity`, `version-config`, or `transport`; it never automatically retries `auth`.
- Setup persists no credential values: only canonical workspace root, fixed routes `claude`/`google`, authorization, approval posture, no-prompt boolean, and required environment-variable names.
- Preserve managed-file refusal, workspace-escape validation, pinned launchers, and `--remove` behavior.
- The only legacy aliases are `--check -> --install` and `--uninstall -> --remove`; both warn `removed in the next release after 0.2.526`.
- Every Python/test command is an authoritative run in the user's normal macOS login-terminal environment, outside the filesystem sandbox. First record `command -v python3`, `python3 --version`, and `python3 -m pytest --version`. If that interpreter lacks pytest, verify and use an already installed versioned interpreter rather than installing into or changing the user's environment; the current verified test interpreter is `/opt/homebrew/bin/python3.12`. Command snippets assume the repository worktree is supplied as the command working directory; do not implement them as `cd ... && ...` command strings.
- `--no-prompt` is valid only with `--approval-policy never`; reject every contradictory setup request before writing state.

## File Structure

- Create: `bin/triad_runtime.py` — setup state, static/live doctor, argv-only process transport, static rule validation.
- Create: `tests/test_triad_runtime.py` — no-network unit tests for runtime commands and probe transport.
- Modify: `scripts/bootstrap.sh` — deterministic install, generated runtime commands, static policy verification, two bounded aliases.
- Modify: `tests/test_bootstrap.py` — installer boundary, generated command, alias, and native execpolicy assertions.
- Modify: `bin/gemini_wrapper.py` and `tests/test_gemini_sandbox.py` — hardened implicit read-only ordering regression.

---

### Task 1: Add owner setup, offline doctor, and safe argv transport

**Files:**
- Create: `bin/triad_runtime.py`
- Create: `tests/test_triad_runtime.py`

**Interfaces:**
- Produces: `main(argv: Sequence[str] | None = None) -> int`
- Produces: `run_argv(argv: Sequence[str], *, timeout_seconds: int, env: Mapping[str, str] | None = None) -> ProbeResult`
- Produces: `setup_main(args: argparse.Namespace) -> int`, `doctor_main(args: argparse.Namespace) -> int`
- Produces: CLI `setup --workspace ABSOLUTE --authorize-external-review --approval-policy {on-request,never} [--no-prompt]`
- Produces: CLI `doctor --workspace ABSOLUTE [--live] [--timeout SECONDS] [--json]`

- [ ] **Step 1: Write failing runtime tests**

```python
# tests/test_triad_runtime.py
import argparse
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import triad_runtime as runtime


def test_run_argv_preserves_hostile_value_without_shell(tmp_path: Path) -> None:
    script = tmp_path / "argv.py"
    script.write_text("import json,sys; print(json.dumps(sys.argv[1:]))\n")
    hostile = 'space "quote" \'single\' `tick` $(sub)\n한글 --dash ;|&'
    result = runtime.run_argv([sys.executable, str(script), hostile], timeout_seconds=2)
    assert result.returncode == 0
    assert json.loads(result.stdout) == [hostile]


def test_setup_records_canonical_authorization_without_credentials(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    workspace = tmp_path / "work space"
    workspace.mkdir()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    rc = runtime.main([
        "setup", "--workspace", str(workspace), "--authorize-external-review",
        "--approval-policy", "on-request",
    ])
    state = json.loads(next((tmp_path / ".config" / "triad-codex-dispatch" / "setup").glob("*.json")).read_text())
    assert rc == 0
    assert state == {
        "schema_version": 1, "workspace_root": str(workspace.resolve()),
        "external_review_authorized": True, "provider_routes": ["claude", "google"],
        "approval_policy": "on-request", "no_prompt": False,
        "required_environment_names": ["TRIAD_WRAPPER_ALLOWED_ROOTS", "TRIAD_WRAPPER_HARDENED", "TRIAD_CLAUDE_ENFORCE_SANDBOX"],
    }
    assert "TOKEN" not in json.dumps(state) and "SECRET" not in json.dumps(state)


def test_static_doctor_cannot_run_a_probe(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(runtime, "static_findings", lambda _workspace: [])
    monkeypatch.setattr(runtime, "run_argv", lambda *_args, **_kwargs: pytest.fail("probe executed"))
    assert runtime.doctor_main(argparse.Namespace(workspace=str(tmp_path), live=False, timeout=30, json=False)) == 0


def test_no_prompt_requires_never_policy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    workspace = tmp_path / "workspace"; workspace.mkdir()
    with pytest.raises(ValueError, match="no-prompt.*never"):
        runtime.main(["setup", "--workspace", str(workspace), "--authorize-external-review",
                      "--approval-policy", "on-request", "--no-prompt"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run outside the filesystem sandbox with workdir `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`: `python3 -m pytest tests/test_triad_runtime.py -q -p no:cacheprovider`

Expected: collection fails because `bin/triad_runtime.py` does not exist.

- [ ] **Step 3: Implement the minimal runtime contract**

```python
# bin/triad_runtime.py
from __future__ import annotations

import argparse, hashlib, json, os, subprocess, tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ProbeResult:
    argv: tuple[str, ...]; returncode: int | None; stdout: str; stderr: str
    timed_out: bool; family: str


def run_argv(argv: Sequence[str], *, timeout_seconds: int,
             env: Mapping[str, str] | None = None) -> ProbeResult:
    if not argv or any(not isinstance(x, str) or not x for x in argv):
        raise ValueError("probe argv must contain non-empty string tokens")
    try:
        completed = subprocess.run(list(argv), shell=False, text=True, capture_output=True,
                                   timeout=timeout_seconds, env=None if env is None else dict(env))
    except subprocess.TimeoutExpired as exc:
        return ProbeResult(tuple(argv), None, exc.stdout or "", exc.stderr or "", True, "transport")
    family = "" if completed.returncode == 0 else classify_probe_failure(completed.stderr)
    return ProbeResult(tuple(argv), completed.returncode, completed.stdout, completed.stderr, False, family)


def setup_state_path(workspace: Path) -> Path:
    digest = hashlib.sha256(str(workspace).encode()).hexdigest()
    base = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return base / "triad-codex-dispatch" / "setup" / f"{digest}.json"


def setup_main(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    if not workspace.is_absolute() or not workspace.is_dir() or not args.authorize_external_review:
        raise ValueError("setup needs an existing absolute workspace and --authorize-external-review")
    if args.no_prompt and args.approval_policy != "never":
        raise ValueError("--no-prompt requires --approval-policy never")
    state = {"schema_version": 1, "workspace_root": str(workspace), "external_review_authorized": True,
             "provider_routes": ["claude", "google"], "approval_policy": args.approval_policy,
             "no_prompt": args.no_prompt,
             "required_environment_names": ["TRIAD_WRAPPER_ALLOWED_ROOTS", "TRIAD_WRAPPER_HARDENED", "TRIAD_CLAUDE_ENFORCE_SANDBOX"]}
    path = setup_state_path(workspace); path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as out:
        json.dump(state, out, indent=2, sort_keys=True); out.write("\n"); temporary = out.name
    os.replace(temporary, path)
    print("setup recorded; use native provider login commands, then start a fresh Codex session")
    return 0


def doctor_main(args: argparse.Namespace) -> int:
    findings = static_findings(Path(args.workspace).expanduser().resolve())
    if not args.live:
        print("static doctor: no provider probes run")
        return emit_report({"mode": "static", "findings": findings}, args.json)
    return live_doctor(Path(args.workspace).expanduser().resolve(), findings, args.timeout, args.json)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("setup", allow_abbrev=False)
    setup.add_argument("--workspace", required=True); setup.add_argument("--authorize-external-review", action="store_true")
    setup.add_argument("--approval-policy", choices=("on-request", "never"), required=True); setup.add_argument("--no-prompt", action="store_true")
    doctor = commands.add_parser("doctor", allow_abbrev=False)
    doctor.add_argument("--workspace", required=True); doctor.add_argument("--live", action="store_true")
    doctor.add_argument("--timeout", type=int, default=30); doctor.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    return setup_main(args) if args.command == "setup" else doctor_main(args)
```

`classify_probe_failure(stderr)` must return `auth` for `login|oauth|credential`, `sandbox-env` for `sandbox|environment|permission denied`, `quota-capacity` for `quota|rate limit|capacity`, `version-config` for `unknown option|unsupported|version`, otherwise `transport`. `static_findings()` checks only setup-state/root correspondence, managed launcher/profile/rules markers, `bash -n`, Python compilation, and Task 3 execpolicy verification; it must not call `run_argv()`.

- [ ] **Step 4: Run tests to verify they pass**

Run outside the filesystem sandbox with the repository as workdir: `python3 -m pytest tests/test_triad_runtime.py -q -p no:cacheprovider`

Expected: `3 passed`; no network or provider binary is invoked.

- [ ] **Step 5: Commit**

```bash
git add bin/triad_runtime.py tests/test_triad_runtime.py
git commit -m "feat: add triad setup and static doctor runtime"
```

### Task 2: Make bootstrap deterministic and install bounded runtime commands

**Files:**
- Modify: `scripts/bootstrap.sh:16-97,824-885,886-1066,1954-2052`
- Modify: `tests/test_bootstrap.py:82-134,162-304,788-826`

**Interfaces:**
- Consumes: `bin/triad_runtime.py` from Task 1.
- Produces: executable absolute `<launcher-dir>/triad-setup` and `<launcher-dir>/triad-doctor` launchers.
- Removes: `run_auth_probe`, `check_auth`, `TRIAD_BOOTSTRAP_AUTH_TIMEOUT`, `TRIAD_BOOTSTRAP_SKIP_AUTH`, and every `TRIAD_BOOTSTRAP_*_AUTH_CMD` variable.

- [ ] **Step 1: Write failing installer-boundary and alias tests**

```python
def test_install_never_executes_provider_binaries(tmp_path: Path) -> None:
    marker = tmp_path / "provider-called"
    scripts = {name: f'[ "${{1:-}}" = "--version" ] && {{ echo "2.1.170"; exit 0; }}; touch "{marker}"; exit 19' for name in ("codex", "claude", "agy", "gemini")}
    result, env, launchers = _run_bootstrap(
        tmp_path, arg="--install", fake_scripts=scripts,
        env_overrides={"TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "0"},
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert not marker.exists()
    for name in ("triad-setup", "triad-doctor"):
        assert (launchers / name).is_file()
        assert os.access(launchers / name, os.X_OK)
        assert "triad_runtime.py" in (launchers / name).read_text(encoding="utf-8")


@pytest.mark.parametrize(("alias", "canonical"), [("--check", "--install"), ("--uninstall", "--remove")])
def test_legacy_aliases_are_bounded(tmp_path: Path, alias: str, canonical: str) -> None:
    result, _env, _launchers = _run_bootstrap(tmp_path, arg=alias)
    assert result.returncode == 0, result.stderr + result.stdout
    assert f"deprecated alias for {canonical}" in result.stdout
    assert "removed in the next release after 0.2.526" in result.stdout


def test_optional_gemini_launcher_remains_pinned_and_fails_closed_when_pin_is_missing(tmp_path: Path) -> None:
    result, _env, launchers = _run_bootstrap(
        tmp_path, arg="--install", fake_names=("codex", "claude", "agy"),
        env_overrides={"TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES": "0"},
    )
    assert result.returncode == 0, result.stderr + result.stdout
    launcher = (launchers / "gemini_wrapper.py").read_text(encoding="utf-8")
    assert "TRIAD_REQUIRE_PINNED_VENDOR" in launcher
    assert 'env["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"' in launcher
    assert "TRIAD_GEMINI_BIN" not in launcher
```

- [ ] **Step 2: Run tests to verify they fail**

Run outside the filesystem sandbox with the repository as workdir: `python3 -m pytest tests/test_bootstrap.py::test_install_never_executes_provider_binaries tests/test_bootstrap.py::test_legacy_aliases_are_bounded tests/test_bootstrap.py::test_optional_gemini_launcher_remains_pinned_and_fails_closed_when_pin_is_missing -q -p no:cacheprovider`

Expected: FAIL: current bootstrap runs live probes unless the harness injects `TRIAD_BOOTSTRAP_SKIP_AUTH`, writes neither runtime command, and lacks the removal-boundary text.

- [ ] **Step 3: Replace the auth-probe path with local installation**

```bash
# scripts/bootstrap.sh argument contract
case "${1:-}" in
  --install) MODE="install" ;;
  --check) MODE="install"; warn "--check is a deprecated alias for --install; removed in the next release after 0.2.526" ;;
  --remove) MODE="remove" ;;
  --uninstall) MODE="remove"; warn "--uninstall is a deprecated alias for --remove; removed in the next release after 0.2.526" ;;
  *) usage >&2; exit 2 ;;
esac
```

```bash
install_runtime_commands() {
  runtime="$REPO_ROOT/bin/triad_runtime.py"
  [ -f "$runtime" ] || { fail "missing runtime helper: $runtime"; return; }
  for command in triad-setup triad-doctor; do
    target="$LAUNCHER_DIR/$command"
    if [ -e "$target" ] && ! grep -Fq '# triad-codex-dispatch managed runtime command' "$target"; then
      fail "refusing to overwrite unmanaged runtime command: $target"; continue
    fi
    printf '#!%s -E\n# triad-codex-dispatch managed runtime command\nimport os,sys\nos.execv(%s,[%s,"-E",%s,%s]+sys.argv[1:])\n' \
      "$python_exe" "$quoted_python" "$quoted_python" "$quoted_runtime" "$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "${command#triad-}")" >"$target" \
      && chmod 0755 "$target" || fail "could not install runtime command: $target"
  done
}
```

Resolve `python_exe`, `quoted_python`, and `quoted_runtime` exactly once with the existing absolute Python resolution/JSON quoting path in `install_launchers`; call `install_runtime_commands` after `install_launchers`. Delete `run_auth_probe`, `check_auth`, their final call, and the obsolete variables/help lines. Do not remove local `command -v` prerequisite checks: they validate executable availability but must not execute a provider.

- [ ] **Step 4: Run the full bootstrap suite to verify it passes**

Run outside the filesystem sandbox with the repository as workdir: `python3 -m pytest tests/test_bootstrap.py -q -p no:cacheprovider`

Expected: PASS; the helper no longer sets `TRIAD_BOOTSTRAP_SKIP_AUTH`, and a successful install leaves all fake-provider markers absent.

- [ ] **Step 5: Commit**

```bash
git add scripts/bootstrap.sh tests/test_bootstrap.py
git commit -m "feat: make bootstrap installation deterministic"
```

### Task 3: Add static execpolicy verification and explicit classified live doctor

**Files:**
- Modify: `bin/triad_runtime.py`
- Modify: `scripts/bootstrap.sh:1528-1681,2000-2052`
- Modify: `tests/test_bootstrap.py:592-637`
- Modify: `tests/test_triad_runtime.py`

**Interfaces:**
- Produces: `verify_execpolicy(codex_bin: Path, rules_path: Path, launcher_dir: Path) -> list[str]`
- Produces internal bounded local runner: `_run_execpolicy_check(codex_bin: Path, rules_path: Path, command: Sequence[str]) -> ProbeResult`
- Produces: `live_probe_argv(paths: RuntimePaths, provider: str, timeout_seconds: int) -> list[str]`
- Produces: `live_doctor(workspace: Path, findings: list[str], timeout_seconds: int, as_json: bool) -> int`
- Produces: installer-owned runtime context for the absolute Codex executable, sibling launcher directory, rules path/enabled posture, and install-time Gemini vendor availability; caller environment and mutable `PATH` cannot override it.
- Produces: `live_outer_timeout(provider: str, provider_timeout_seconds: int) -> int`, including bounded route preflight and cleanup overhead.
- Produces internal CLI: `verify-execpolicy --codex-bin ABSOLUTE --rules ABSOLUTE --launcher-dir ABSOLUTE`
- `RuntimePaths`: `codex_bin`, `claude_launcher`, `antigravity_launcher`, `gemini_launcher: Path | None`.

- [ ] **Step 1: Write failing native-policy and live-doctor tests**

```python
def test_execpolicy_verifier_uses_native_argv_contract_without_provider_calls(tmp_path: Path) -> None:
    fake_codex = write_fake_execpolicy_cli(tmp_path)
    result, env, launchers = _run_bootstrap(
        tmp_path, arg="--install", fake_scripts={"codex": fake_codex},
    )
    assert result.returncode == 0, result.stderr + result.stdout
    rules = Path(env["HOME"]) / ".codex" / "rules" / "triad-codex-dispatch.rules"
    checks = [
        ("allow", [str(launchers / "claude_wrapper.py"), "--prompt", "hi", "--sandbox", "read-only"]),
        ("prompt", ["bash", "-lc", f'{launchers / "claude_wrapper.py"} --prompt hi']),
    ]
    for expected, command in checks:
        completed = subprocess.run([str(tmp_path / "bin" / "codex"), "execpolicy", "check", "--rules", str(rules), *command], text=True, capture_output=True, check=True)
        assert json.loads(completed.stdout).get("decision", "prompt") == expected


def test_live_doctor_auth_is_terminal_and_argv_is_absolute(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    launcher = tmp_path / "claude_wrapper.py"; launcher.write_text("")
    paths = runtime.RuntimePaths(Path("/codex"), launcher, launcher, None)
    monkeypatch.setattr(runtime, "resolve_runtime_paths", lambda: paths)
    monkeypatch.setattr(runtime, "run_argv", lambda argv, **_: runtime.ProbeResult(tuple(argv), 1, "", "OAuth login required", False, "auth"))
    assert runtime.live_doctor(tmp_path, [], 2, True) == 1
    report = json.loads(capsys.readouterr().out)
    claude = next(x for x in report["probes"] if x["provider"] == "claude")
    assert claude["argv"] == [str(launcher.resolve()), "--prompt", "Return exactly OK.", "--sandbox", "read-only", "--timeout", "2", "--repair-mode"]
    assert claude["family"] == "auth" and claude["retry"] is False
```

`write_fake_execpolicy_cli` must be the same fake Codex executable installed into bootstrap's isolated `PATH`, and the shared default fake-binary fixture must recognize `execpolicy check`, record its exact argv, and emit the native object JSON shapes. Rules are enabled by default, so no unrelated bootstrap test may depend on a non-JSON fake Codex response for this local subcommand.

- [ ] **Step 2: Run tests to verify they fail**

Run outside the filesystem sandbox with the repository as workdir: `python3 -m pytest tests/test_bootstrap.py::test_execpolicy_verifier_uses_native_argv_contract_without_provider_calls tests/test_triad_runtime.py::test_live_doctor_auth_is_terminal_and_argv_is_absolute -q -p no:cacheprovider`

Expected: FAIL because generated rules are not evaluated by bootstrap/static doctor and live doctor does not exist.

- [ ] **Step 3: Implement native static verification and live probes**

```python
@dataclass(frozen=True)
class RuntimePaths:
    codex_bin: Path
    claude_launcher: Path
    antigravity_launcher: Path
    gemini_launcher: Path | None


def verify_execpolicy(codex_bin: Path, rules_path: Path, launcher_dir: Path) -> list[str]:
    cases = (("allow", [launcher_dir / "claude_wrapper.py", "--prompt", "static", "--sandbox", "read-only"]),
             ("allow", [launcher_dir / "antigravity_wrapper.py", "--prompt", "static", "--sandbox", "read-only"]),
             ("allow", [launcher_dir / "gemini_wrapper.py", "--prompt", "static", "--sandbox", "read-only"]),
             ("prompt", ["bash", "-lc", f"{launcher_dir / 'claude_wrapper.py'} --prompt static"]))
    findings = []
    for expected, command in cases:
        result = _run_execpolicy_check(codex_bin, rules_path, [str(x) for x in command])
        actual = json.loads(result.stdout).get("decision", "prompt") if result.returncode == 0 else "error"
        if actual != expected:
            findings.append(f"execpolicy expected {expected}, got {actual}: {command!r}")
    return findings


def live_probe_argv(paths: RuntimePaths, provider: str, timeout_seconds: int) -> list[str]:
    if provider == "codex": return [str(paths.codex_bin), "login", "status"]
    launcher = {"claude": paths.claude_launcher, "google": paths.antigravity_launcher, "gemini": paths.gemini_launcher}[provider]
    if launcher is None: raise ValueError("gemini is not installed")
    return [str(launcher.resolve()), "--prompt", "Return exactly OK.", "--sandbox", "read-only", "--timeout", str(timeout_seconds), "--repair-mode"]


def live_doctor(workspace: Path, findings: list[str], timeout_seconds: int, as_json: bool) -> int:
    probes = []
    paths = resolve_runtime_paths()
    for provider in ("codex", "claude", "google") + (("gemini",) if paths.gemini_launcher else ()):
        outer_timeout = live_outer_timeout(provider, timeout_seconds)
        result = run_argv(live_probe_argv(paths, provider, timeout_seconds), timeout_seconds=outer_timeout)
        family = "ok" if result.returncode == 0 else result.family
        probes.append({"provider": provider, "argv": list(result.argv), "returncode": result.returncode,
                       "family": family, "retry": family not in {"auth", "packet-integrity", "nonconvergence"}})
    report = {"mode": "live", "workspace_root": str(workspace), "static_findings": findings, "probes": probes}
    print(json.dumps(report, ensure_ascii=False) if as_json else json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not findings and all(x["family"] == "ok" for x in probes) else 1
```

`_run_execpolicy_check` is a dedicated local-only, list-form, `shell=False` transport whose executable and fixed prefix are exactly `[codex_bin, "execpolicy", "check", "--rules", rules_path]`. It has its own ten-second deterministic hang guard and process cleanup, and it never delegates to the provider-capable public `run_argv`. This preserves the earlier `static_findings()` invariant: among probe transports, static doctor may start only the local Codex policy evaluator; the previously specified local `bash -n` and Python compilation checks remain permitted. Static doctor must still make zero wrapper, vendor, provider, or network calls. Keep the existing monkeypatched-`run_argv` test green and add a focused assertion that the local verifier cannot substitute another executable or command prefix.

The native evaluator contract is exit `0` plus an object-shaped JSON document. An explicit `decision` must equal the expected value; a valid object with no `decision` means `prompt`. Non-zero exit, timeout, empty output, malformed JSON, and non-object JSON each become one stable finding and exit `1`, never a traceback. Stderr warnings accompanying valid stdout JSON are diagnostic only. If command-rule installation refused an unmanaged target, bootstrap must not evaluate that target.

Bootstrap persists its rules posture in the managed `triad-doctor` runtime context. Reinstalling with rules explicitly disabled removes only a bootstrap-managed stale rules file, preserves any unmanaged file, and records the disabled posture independently of file absence. A fresh static doctor with rules disabled emits exactly one non-failing note and performs zero execpolicy, wrapper, vendor, provider, or network calls; a missing rules file while the recorded posture is enabled remains a finding.

The generated runtime command also owns the installer-resolved absolute Codex executable and sibling launcher directory. Prepending hostile same-name commands to `PATH` must not change any live `argv[0]`. Gemini availability is the install-time pinned-vendor state, not the mere presence of the always-generated fail-closed `gemini_wrapper.py` or the later mutable `PATH`; an installation without Gemini probes exactly Codex, Claude, and Google, while an installation with pinned Gemini probes exactly Codex, Claude, Google, and Gemini.

The wrapper's own `--timeout` is the primary provider deadline. `--repair-mode` disables server-capacity retry for this one-shot health probe. `live_outer_timeout` adds exact route overhead rather than model time. Codex uses its direct provider timeout. Claude and Gemini add `15` seconds: two five-second TERM/KILL waits, two two-second drains, and one second of fixed margin. Google adds `82` seconds: `15` seconds for version preflight, `30` for settings acquisition, `2` for PTY TERM/KILL cleanup, `30` for settings release, and `5` seconds of fixed margin. Define named constants for every term and assert the literal terms and sums in tests. Add a hermetic delayed-preflight/lock regression and a nested-session regression: a fake wrapper starts a child with `start_new_session=True`, enforces its own shorter deadline, kills/reaps that group, and exits before the outer deadline; assert no child survives. The test must clean the child explicitly in `finally` even when the assertion fails. Never rely on outer process-group termination to reach a vendor session created by a wrapper.

`run_argv` itself must also remain finite when a defective wrapper exits or is killed while a separately sessioned child retains inherited output pipes. Every TERM, KILL, wait, and pipe-drain phase has an explicit bound; add a failure-path watchdog proving return within the declared timeout plus cleanup bound. The watchdog records the detached PID and kills/reaps it in `finally`, even when the assertion fails. Direct supervision of arbitrary detached descendants is optional future hardening, but supported wrappers must prove they reap their own vendor sessions.

Failure classification consumes combined stdout and stderr. `Not logged in`, login, OAuth, and credential messages on either stream are `auth`; every provider is invoked exactly once and `auth` always reports `retry: false`.

Add an argparse `verify-execpolicy` subcommand that prints one finding per line and returns `0` only when `verify_execpolicy()` returns an empty list. Bootstrap invokes it immediately after `install_codex_rules` with the absolute `command -v codex`, rules path, and launcher directory; any non-zero return calls `fail "static execpolicy verification failed"`. `static_findings` calls the same function directly. When rules are opted out, static doctor emits one note and skips rule evaluation. Do not add command-string overrides or retries.

- [ ] **Step 4: Run focused then complete verification**

Run outside the filesystem sandbox with the repository as workdir: `python3 -m pytest tests/test_bootstrap.py tests/test_triad_runtime.py -q -p no:cacheprovider`

After the hermetic suite is green, run one separate integration proof outside the filesystem sandbox with the real executable returned by `command -v codex`: invoke `codex execpolicy check --rules <installed-rules> <argv...>` once for an allowed launcher argv and once for a shell-wrapped argv. Record the literal JSON decisions. Do not make the unit suite depend on a signed-in Codex installation.

Expected: PASS; native checks return `allow` for absolute launchers and no `decision` (interpreted as `prompt`) for shell entrypoints; fake live failures retain their family and `auth` has `retry: false`.

- [ ] **Step 5: Commit**

```bash
git add bin/triad_runtime.py scripts/bootstrap.sh tests/test_bootstrap.py tests/test_triad_runtime.py
git commit -m "feat: add static policy and live doctor verification"
```

### Task 4: Fix Gemini hardened ordering and verify the delivery

**Files:**
- Modify: `bin/gemini_wrapper.py:130-141`
- Modify: `tests/test_gemini_sandbox.py:42-105`

**Interfaces:**
- Preserves: explicit `read-only` adds `--policy`; explicit `workspace-write` does not; invalid write approval never spawns Gemini.
- Produces: `TRIAD_WRAPPER_HARDENED=1` with omitted `--sandbox` normalizes to read-only before conflict/policy validation.

- [ ] **Step 1: Write failing hardened-mode tests**

```python
def test_hardened_implicit_readonly_attaches_policy(tmp_path: Path) -> None:
    result, argv = _run(tmp_path, env_overrides={"TRIAD_WRAPPER_HARDENED": "1"})
    assert result.returncode == 0, result.stderr
    assert argv.splitlines()[-2:] == ["--policy", str(POLICY)]


def test_hardened_implicit_readonly_rejects_auto_edit_before_spawn(tmp_path: Path) -> None:
    result, argv = _run(tmp_path, "--approval-mode", "auto_edit", env_overrides={"TRIAD_WRAPPER_HARDENED": "1"})
    assert result.returncode != 0 and "conflicts" in result.stderr
    assert argv == ""
```

Extend `_run(tmp_path, *extra, env_overrides: dict[str, str] | None = None)` to merge `env_overrides` into its isolated environment, and add both functions to `TESTS`.

- [ ] **Step 2: Run regression test to verify it fails**

Run: `cd /Users/chaniri/codex_workspace && python3 workspace/triad-codex-dispatch-reliability/tests/test_gemini_sandbox.py`

Expected: FAIL at `test_hardened_implicit_readonly_rejects_auto_edit_before_spawn`; current code checks the conflict before applying hardened read-only.

- [ ] **Step 3: Normalize hardened sandbox before validation**

```python
# bin/gemini_wrapper.py: after the non-empty prompt check, before any sandbox validation
if args.sandbox is None and _wrapper_hardened():
    args.sandbox = "read-only"

if args.sandbox == "read-only" and args.approval_mode == "auto_edit":
    log(f"--sandbox read-only conflicts with --approval-mode {args.approval_mode} "
        "(a write-auto-approving mode). Use --approval-mode default with read-only.")
    return EXIT_ARG_ERROR
if args.sandbox == "read-only" and not _READONLY_POLICY.is_file():
    log(f"read-only policy file missing: {_READONLY_POLICY}")
    return EXIT_ARG_ERROR
```

Delete the existing later hardened block so normalization occurs exactly once.

- [ ] **Step 4: Run all deterministic checks**

Run: `cd /Users/chaniri/codex_workspace && python3 workspace/triad-codex-dispatch-reliability/tests/test_gemini_sandbox.py && python3 -m pytest workspace/triad-codex-dispatch-reliability/tests/test_bootstrap.py workspace/triad-codex-dispatch-reliability/tests/test_triad_runtime.py -q && bash -n workspace/triad-codex-dispatch-reliability/scripts/bootstrap.sh && python3 -m py_compile workspace/triad-codex-dispatch-reliability/bin/triad_runtime.py workspace/triad-codex-dispatch-reliability/bin/gemini_wrapper.py && git -C workspace/triad-codex-dispatch-reliability diff --check`

Expected: Gemini reports `8/8 passed`; pytest, syntax, compilation, and whitespace checks exit `0`.

- [ ] **Step 5: Commit**

```bash
git add bin/gemini_wrapper.py tests/test_gemini_sandbox.py
git commit -m "fix: normalize Gemini hardened sandbox before validation"
git status --short
```

Expected: the final status is empty.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-20-triad-runtime-install-plan.md`. Two execution options:

1. Subagent-Driven (recommended) - fresh subagent per task with review between tasks.

2. Inline Execution - execute tasks in this session with checkpoints.
