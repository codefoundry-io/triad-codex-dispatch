from __future__ import annotations

import hashlib
import importlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "bin/google_diagnostics.py"
GOOGLE_ENV = (
    "GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_GENAI_USE_VERTEXAI", "GOOGLE_GENAI_USE_ENTERPRISE",
    "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION", "GOOGLE_CLOUD_REGION",
    "GOOGLE_CLOUD_QUOTA_PROJECT", "AGY_ADC_AUTH",
)
RESPONSES = {
    "--version": {"out": "AGY 1.2.5\n"},
    "--help": {"out": "Commands:\n  models    List models\n  plugin    Manage plugins\n  extensions    Manage extensions\n"},
    "models --help": {"out": "Usage: agy models\n"},
    "models": {"out": "gemini-3.1-pro-high\tPublic label\ngemini-3.8-flash-high\tOther label\n"},
    "plugin --help": {"out": "Commands:\n  list    List installed plugins\n"},
    "plugin list": {"out": "PRIVATE_PLUGIN\n/private/plugin/path\n", "err": "PRIVATE_STDERR"},
    "extensions --help": {"out": "Commands:\n  list    List installed extensions\n"},
    "extensions list": {"out": "PRIVATE_EXTENSION\n/private/extension/path\n"},
}


def _fake(tmp_path, responses=None, name="agy"):
    binary = tmp_path / name
    calls = tmp_path / (name + "-calls.jsonl")
    table = RESPONSES if responses is None else responses
    binary.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        f"table = {table!r}\n"
        f"omitted = {GOOGLE_ENV + ('NODE_OPTIONS', 'PYTHONPATH', 'BASH_ENV')!r}\n"
        "record = {'args': sys.argv[1:], 'cwd': os.getcwd(), 'stdin_empty': sys.stdin.buffer.read() == b'', 'present': [k for k in omitted if k in os.environ]}\n"
        f"with open({str(calls)!r}, 'a') as out: out.write(json.dumps(record) + '\\n')\n"
        "entry = table.get(' '.join(sys.argv[1:]), {'code': 97})\n"
        "sys.stdout.buffer.write(entry.get('out', '').encode('utf-8'))\n"
        "sys.stderr.write(entry.get('err', ''))\n"
        "raise SystemExit(entry.get('code', 0))\n"
    )
    binary.chmod(0o700)
    return binary, calls


def _invoke(tmp_path, *, cli="agy", inventory=False, responses=None, pin="valid", strict=False):
    assert SCRIPT.is_file(), "missing diagnostic helper"
    binary, calls = _fake(tmp_path, responses, cli)
    neutral_parent = tmp_path / "neutral"
    neutral_parent.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith("TRIAD_")}
    env.update(PATH=str(tmp_path) + ":/usr/bin:/bin", TMPDIR=str(neutral_parent))
    if pin != "absent":
        env[f"TRIAD_{cli.upper()}_BIN"] = str(binary) if pin == "valid" else str(tmp_path / "PRIVATE_MISSING")
    if strict:
        env["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"
    env.update({key: "PRIVATE_SELECTOR" for key in GOOGLE_ENV})
    env.update(NODE_OPTIONS="--trace-warnings", PYTHONPATH="/nonexistent-triad-test", BASH_ENV="/nonexistent-triad-test")
    argv = [sys.executable, "-B", str(SCRIPT), "--cli", cli]
    if inventory:
        argv.append("--inventory")
    result = subprocess.run(argv, cwd=tmp_path, env=env, capture_output=True, text=True, timeout=30)
    observed = [json.loads(line) for line in calls.read_text().splitlines()] if calls.exists() else []
    snapshot = json.loads(result.stdout)
    assert list(neutral_parent.iterdir()) == []
    assert "PRIVATE_" not in result.stdout + result.stderr
    assert str(tmp_path) not in result.stdout + result.stderr
    return result, snapshot, observed


@pytest.mark.parametrize("cli", ["agy", "gemini"])
def test_default_probes_are_metadata_only_with_closed_stdin_and_neutral_cwd(tmp_path, cli):
    result, snapshot, calls = _invoke(tmp_path, cli=cli)
    assert result.returncode == 0
    assert snapshot["status"] == "complete"
    assert snapshot["version"] == "1.2.5"
    assert [x["args"] for x in calls] == [["--version"], ["--help"]]
    assert all(x["stdin_empty"] and not x["present"] for x in calls)
    assert all(Path(x["cwd"]).parent == tmp_path / "neutral" for x in calls)
    assert len({x["cwd"] for x in calls}) == 1
    assert snapshot["probes"][0]["stdout_bytes"] == 10
    assert snapshot["probes"][0]["stdout_sha256"] == hashlib.sha256(b"AGY 1.2.5\n").hexdigest()
    assert "model_slugs" not in snapshot


@pytest.mark.parametrize("pin", ["absent", "invalid"])
@pytest.mark.parametrize("strict", [False, True])
def test_selection_preserves_nonstrict_fallback_and_strict_refusal(tmp_path, pin, strict):
    result, snapshot, calls = _invoke(tmp_path, pin=pin, strict=strict)
    assert result.returncode == int(strict)
    if strict:
        assert snapshot["status"] == "incomplete" and not calls and not snapshot["probes"]
        assert snapshot["error"] == ("binary_missing" if pin == "absent" else "selection_failed")
    else:
        assert [x["args"] for x in calls] == [["--version"], ["--help"]]


def _load():
    assert SCRIPT.is_file(), "missing diagnostic helper"
    sys.path.insert(0, str(ROOT / "bin"))
    return importlib.import_module("google_diagnostics")


def test_valid_pin_wins_over_path_shadow(tmp_path, monkeypatch):
    module = _load()
    pinned, calls = _fake(tmp_path, name="pinned")
    shadow, shadow_calls = _fake(tmp_path, {"--version": {"code": 97}}, name="agy")
    monkeypatch.setenv("TRIAD_AGY_BIN", str(pinned))
    monkeypatch.setenv("PATH", str(tmp_path))
    snapshot = module.collect_snapshot("agy")
    assert snapshot["status"] == "complete"
    assert len(calls.read_text().splitlines()) == 2
    assert not shadow_calls.exists()


@pytest.mark.parametrize("cli", ["agy", "gemini"])
def test_relative_path_selection_survives_neutral_cwd(tmp_path, monkeypatch, cli):
    module = _load()
    relative_bin = tmp_path / "relative-bin"
    relative_bin.mkdir()
    binary, calls = _fake(relative_bin, name=cli)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PATH", "relative-bin")
    monkeypatch.delenv(f"TRIAD_{cli.upper()}_BIN", raising=False)
    monkeypatch.delenv("TRIAD_REQUIRE_PINNED_VENDOR", raising=False)
    snapshot = module.collect_snapshot(cli)
    assert snapshot["status"] == "complete"
    observed = [json.loads(line) for line in calls.read_text().splitlines()]
    assert [x["args"] for x in observed] == [["--version"], ["--help"]]
    assert all(x["cwd"] != str(tmp_path) for x in observed)


@pytest.mark.parametrize("cli, sequence", [
    ("agy", [["--version"], ["--help"], ["models", "--help"], ["models"], ["plugin", "--help"], ["plugin", "list"]]),
    ("gemini", [["--version"], ["--help"], ["extensions", "--help"], ["extensions", "list"]]),
])
def test_inventory_is_explicit_and_uses_only_help_gated_commands(tmp_path, cli, sequence):
    result, snapshot, calls = _invoke(tmp_path, cli=cli, inventory=True)
    assert result.returncode == 0
    assert [x["args"] for x in calls] == sequence
    if cli == "agy":
        assert snapshot["model_format"] == "tab-separated"
        assert snapshot["model_slugs"] == ["gemini-3.1-pro-high", "gemini-3.8-flash-high"]
    assert "extension_count" not in snapshot and "plugin_count" not in snapshot


@pytest.mark.parametrize("root_help, group_help", [
    ("Commands:\n  gemini extensions <command>  Manage Gemini CLI extensions.\n", "Commands:\n  list    Lists installed extensions.\n"),
    ("Commands:\n  extensions    Manage extensions\n", "Commands:\n  gemini extensions list    Lists installed extensions.\n"),
], ids=["qualified-root-with-placeholder", "qualified-group-list"])
def test_gemini_qualified_help_entries_authorize_only_extension_listing(tmp_path, root_help, group_help):
    table = {**RESPONSES, "--help": {"out": root_help}, "extensions --help": {"out": group_help}}
    result, snapshot, calls = _invoke(tmp_path, cli="gemini", inventory=True, responses=table)
    assert result.returncode == 0 and snapshot["status"] == "complete"
    assert [x["args"] for x in calls] == [["--version"], ["--help"], ["extensions", "--help"], ["extensions", "list"]]


@pytest.mark.parametrize("root_help, plugin_help, sequence", [
    ("No plugin or models commands available.\n", "", [["--version"], ["--help"]]),
    ("Commands:\n  plugin    Manage plugins\n", "Description: list is unavailable.\n", [["--version"], ["--help"], ["plugin", "--help"]]),
])
def test_help_words_in_prose_do_not_authorize_inventory(tmp_path, root_help, plugin_help, sequence):
    table = {**RESPONSES, "--help": {"out": root_help}, "plugin --help": {"out": plugin_help}}
    result, snapshot, calls = _invoke(tmp_path, inventory=True, responses=table)
    assert result.returncode == 0 and snapshot["status"] == "complete"
    assert [x["args"] for x in calls] == sequence


@pytest.mark.parametrize("failed, count", [("--version", 1), ("--help", 2), ("models --help", 3), ("models", 4), ("plugin --help", 5), ("plugin list", 6)])
def test_invoked_failure_stops_without_fallback_or_raw_disclosure(tmp_path, failed, count):
    table = {**RESPONSES, failed: {"code": 7, "out": "PRIVATE_OUTPUT", "err": "PRIVATE_ERROR"}}
    result, snapshot, calls = _invoke(tmp_path, inventory=True, responses=table)
    assert result.returncode == 1 and snapshot["status"] == "incomplete"
    assert len(calls) == count
    assert snapshot["probes"][-1]["status"] == "failed"
    assert snapshot["probes"][-1]["exit_code"] == 7


@pytest.mark.parametrize("output", ["", "Unrecognized model table\n", "PRIVATE_BAD/ name\tLabel\n", "x" * 129 + "\tLabel\n", "".join(f"model-{i}\tLabel\n" for i in range(129))], ids=["empty", "unknown", "bad-slug", "long-slug", "too-many"])
def test_unknown_or_oversized_catalog_remains_opaque(tmp_path, output):
    table = {**RESPONSES, "models": {"out": output}}
    result, snapshot, calls = _invoke(tmp_path, inventory=True, responses=table)
    assert result.returncode == 0
    assert snapshot["model_format"] == "unrecognized" and snapshot["model_slugs"] == []
    assert snapshot["probes"][3]["stdout_sha256"] == hashlib.sha256(output.encode()).hexdigest()


def test_model_catalog_accepts_exact_bounds_and_first_seen_unique_slugs(tmp_path):
    slugs = ["a" * 128] + [f"model-{i}" for i in range(127)]
    output = "".join(x + "\tLabel\n" for x in slugs + slugs[:1])
    result, snapshot, calls = _invoke(tmp_path, inventory=True, responses={**RESPONSES, "models": {"out": output}})
    assert result.returncode == 0 and snapshot["model_slugs"] == slugs


def test_launch_failure_is_fixed_incomplete_json(tmp_path, monkeypatch):
    module = _load()
    monkeypatch.setattr(module.review_round, "_selectable_google_binary", lambda name: str(tmp_path / "PRIVATE_GONE"))
    snapshot = module.collect_snapshot("agy")
    assert snapshot["status"] == "incomplete"
    assert snapshot["probes"][0]["status"] == "launch_failed"
    assert "PRIVATE_" not in json.dumps(snapshot)


def test_timeout_cleans_same_group_descendant_without_forwarding_stderr(tmp_path, monkeypatch, capsys):
    module = _load()
    pid_file = tmp_path / "descendant.pid"
    binary = tmp_path / "agy-timeout"
    child = f"import os,signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); open({str(pid_file)!r},'w').write(str(os.getpid())); time.sleep(30)"
    binary.write_text(f"#!{sys.executable}\nimport pathlib,subprocess,sys,time\np=subprocess.Popen([sys.executable,'-c',{child!r}])\nwhile not pathlib.Path({str(pid_file)!r}).exists(): time.sleep(0.01)\nprint('metadata',flush=True)\nprint('PRIVATE_STDERR',file=sys.stderr,flush=True)\ntime.sleep(30)\n")
    binary.chmod(0o700)
    monkeypatch.setenv("TRIAD_AGY_BIN", str(binary))
    monkeypatch.setattr(module, "PROBE_TIMEOUT", 5)
    started = time.monotonic()
    pid = None
    try:
        snapshot = module.collect_snapshot("agy")
        assert time.monotonic() - started < 18
        pid = int(pid_file.read_text())
        assert snapshot["status"] == "incomplete" and len(snapshot["probes"]) == 1
        probe = snapshot["probes"][0]
        assert probe["status"] == "timeout"
        assert probe["stdout_sha256"] == hashlib.sha256(b"metadata\n").hexdigest()
        for _ in range(100):
            state = subprocess.run(["ps", "-p", str(pid), "-o", "stat="], capture_output=True, text=True).stdout.strip()
            if not state or state.startswith("Z"):
                break
            time.sleep(0.02)
        assert not state or state.startswith("Z")
        output = capsys.readouterr()
        assert "PRIVATE_STDERR" not in output.out + output.err + json.dumps(snapshot)
    finally:
        if pid is None and pid_file.exists():
            pid = int(pid_file.read_text())
        if pid is not None:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def test_host_temp_failure_is_fixed_and_does_not_disclose_error(tmp_path, monkeypatch):
    module = _load()
    binary, calls = _fake(tmp_path)
    monkeypatch.setenv("TRIAD_AGY_BIN", str(binary))

    def unavailable(**kwargs):
        raise OSError("PRIVATE_HOST_PATH")

    monkeypatch.setattr(module.tempfile, "TemporaryDirectory", unavailable)
    snapshot = module.collect_snapshot("agy")
    assert snapshot["status"] == "incomplete" and snapshot["error"] == "host_io_failed"
    assert not snapshot["probes"] and not calls.exists()
    assert "PRIVATE_" not in json.dumps(snapshot)


def test_interrupt_cleans_started_probe_and_propagates(tmp_path):
    assert SCRIPT.is_file(), "missing diagnostic helper"
    binary = tmp_path / "interrupt-probe"
    pid_file = tmp_path / "interrupt.pid"
    binary.write_text(f"#!{sys.executable}\nimport os,time\nopen({str(pid_file)!r},'w').write(str(os.getpid()))\ntime.sleep(30)\n")
    binary.chmod(0o700)
    env = dict(os.environ, TRIAD_AGY_BIN=str(binary))
    proc = subprocess.Popen([sys.executable, "-B", str(SCRIPT), "--cli", "agy"],
                            cwd=tmp_path, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pid = None
    try:
        for _ in range(300):
            if pid_file.exists() and pid_file.read_text():
                break
            time.sleep(0.01)
        pid = int(pid_file.read_text())
        proc.send_signal(signal.SIGINT)
        stdout, stderr = proc.communicate(timeout=15)
        assert proc.returncode != 0 and stdout == b""
        assert b"KeyboardInterrupt" in stderr
        state = subprocess.run(["ps", "-p", str(pid), "-o", "stat="], capture_output=True, text=True).stdout.strip()
        assert not state or state.startswith("Z")
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=5)
        proc.stdout.close()
        proc.stderr.close()
        if pid is None and pid_file.exists() and pid_file.read_text():
            pid = int(pid_file.read_text())
        if pid is not None:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
