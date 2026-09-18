from __future__ import annotations

import importlib.util
import json
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "bin" / "agy_hook.py"


def _invoke(tmp_path, raw=b"", *args):
    return subprocess.run([sys.executable, "-B", str(SCRIPT), *args], input=raw,
                          capture_output=True, cwd=tmp_path, check=False)


@pytest.mark.parametrize("name, decision", [
    ("view_file", "allow"), ("grep_search", "allow"), ("list_dir", "allow"),
    ("find_by_name", "allow"), ("search_web", "allow"), ("read_url_content", "allow"),
    ("run_command", "deny"), ("write_to_file", "deny"), ("replace_file_content", "deny"),
    ("ask_permission", "deny"), ("invoke_subagent", "deny"), ("finish", "deny"),
    ("VIEW_FILE", "deny"), (" view_file", "deny"), ("view_file ", "deny"),
    ("view_file_extra", "deny"), ("mcp.view_file", "deny"),
])
def test_hook_filters_exact_names_without_actions_or_input_reflection(tmp_path, name, decision):
    raw = json.dumps({"toolCall": {"name": name, "args": {
        "AbsolutePath": "/private/DO_NOT_REFLECT", "CommandLine": "touch side-effect",
    }}, "transcriptPath": "/private/DO_NOT_OPEN"}).encode()
    result = _invoke(tmp_path, raw)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["decision"] == decision
    assert set(payload) == {"decision", "reason"}
    assert "DO_NOT_" not in result.stdout.decode()
    assert result.stderr == b""
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("raw", [
    b"", b"{", b"\xff", b"null", b"[]", b"{}", b'{"toolCall":null}',
    b'{"toolCall":{"name":[],"args":{}}}',
    b'{"toolCall":{"name":"view_file"}}',
    b'{"toolCall":{"name":"view_file","args":[]}}',
    b'{"toolCall":{"name":"run_command","name":"view_file","args":{}}}',
    b'{"toolCall":{"name":"view_file","args":{"x":1,"x":2}}}',
    b"[" * 1500 + b"0" + b"]" * 1500,
    b" " * (1024 * 1024 + 1),
], ids=["empty", "broken", "invalid-utf8", "null", "array", "empty-object",
        "null-tool", "non-string-name", "missing-args", "array-args",
        "duplicate-name", "duplicate-argument", "deep", "oversize"])
def test_hook_returns_deny_json_for_invalid_input(tmp_path, raw):
    result = _invoke(tmp_path, raw)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["decision"] == "deny"
    assert result.stderr == b""
    assert len(result.stdout) < 200
    assert list(tmp_path.iterdir()) == []


def test_config_renderer_is_disabled_stdout_only_and_has_no_enable_option(tmp_path):
    result = _invoke(tmp_path, b"", "--render-config")
    assert result.returncode == 0, result.stderr
    config = json.loads(result.stdout)
    hook = config["triad-readonly-allowlist"]
    assert hook["enabled"] is False
    assert set(hook) == {"enabled", "PreToolUse"}
    event, = hook["PreToolUse"]
    assert event["matcher"] == "*"
    command, = event["hooks"]
    assert command["type"] == "command"
    assert command["timeout"] == 5
    assert shlex.split(command["command"]) == ["python3", str(SCRIPT.resolve())]
    assert _invoke(tmp_path, b"", "--enable").returncode == 2
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("constant", [b"NaN", b"Infinity", b"-Infinity"])
def test_hook_rejects_non_json_numeric_constants(tmp_path, constant):
    raw = b'{"toolCall":{"name":"view_file","args":{"value":' + constant + b'}}}'
    result = _invoke(tmp_path, raw)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["decision"] == "deny"


def test_renderer_quotes_shell_special_script_path_without_executing_it(tmp_path):
    assert SCRIPT.is_file(), "missing packaged hook helper"
    spec = importlib.util.spec_from_file_location("triad_hook_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path = tmp_path / "space ' quote $(touch injected) 한글.py"
    config = module.render_disabled_config(path)
    command = config["triad-readonly-allowlist"]["PreToolUse"][0]["hooks"][0]["command"]
    assert shlex.split(command) == ["python3", str(path.resolve())]
    assert list(tmp_path.iterdir()) == []
