"""Resolve wrapper arguments at entry without changing provider or audit policy."""
from __future__ import annotations

import contextlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common
import antigravity_wrapper
import claude_wrapper
import gemini_wrapper

WRAPPERS = [claude_wrapper, gemini_wrapper, antigravity_wrapper]
TEXT = "caller 한글 ' $() `text`\nsecond line"


@pytest.fixture
def paths(tmp_path, monkeypatch):
    caller = tmp_path.resolve() / "caller"
    child = caller / "child"
    child.mkdir(parents=True)
    (caller / "prompt.txt").write_text(TEXT, encoding="utf-8")
    (child / "prompt.txt").write_text("wrong child prompt", encoding="utf-8")
    monkeypatch.chdir(caller)
    monkeypatch.setenv("TRIAD_WRAPPER_ALLOWED_ROOTS", str(caller))
    return caller, child


@pytest.fixture
def fake_provider(monkeypatch):
    calls = []
    binaries = []

    def binary(name):
        binaries.append(name)
        return "/synthetic/" + name

    def completed(cli, prompt, cwd):
        calls.append(dict(cli=cli, prompt=prompt, cwd=cwd))
        stdout = json.dumps({"event": "result", "result": {"status": "SUCCESS", "response": "ok"}})
        return _common.RunResult(exit_code=0, stdout=stdout, stderr="", elapsed_s=0,
                                 classification="ok", vendor_exit_code=0, final_answer="ok")

    def ordinary(cli, build_cmd, prompt, *, cwd, **kwargs):
        build_cmd(prompt)
        return completed(cli, prompt, cwd)

    def agy(cli, cmd, cwd, timeout, **kwargs):
        return completed(cli, cmd[cmd.index("-p") + 1], cwd)

    def forbidden(*args, **kwargs):
        pytest.fail("unexpected real subprocess")

    monkeypatch.setattr(_common.subprocess, "Popen", forbidden)
    monkeypatch.setattr(_common, "require_binary", binary)
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda *a, **k: None)
    monkeypatch.setattr(_common, "persist_result_artifacts", lambda *a, **k: None)
    monkeypatch.setattr(_common, "_run_once", agy)
    for wrapper in (claude_wrapper, gemini_wrapper):
        monkeypatch.setattr(wrapper, "require_binary", binary)
        monkeypatch.setattr(wrapper, "run_cli_with_retry", ordinary)
        monkeypatch.setattr(wrapper, "persist_result_artifacts", lambda *a, **k: None)
    monkeypatch.setattr(antigravity_wrapper, "_probe_agy_version", lambda _: (1, 2, 7))
    monkeypatch.setattr(antigravity_wrapper._agy_settings, "agy_settings_guard",
                        lambda *a, **k: contextlib.nullcontext())
    return calls, binaries


def test_relative_helpers_use_process_directory(paths):
    caller, child = paths
    assert _common.load_prompt_text(None, "prompt.txt") == TEXT
    assert _common.validate_wrapper_cwd("child") == str(child)
    assert _common.load_prompt_text(None, str(caller / "prompt.txt")) == TEXT
    assert _common.validate_wrapper_cwd(str(child)) == str(child)
    assert _common.validate_wrapper_cwd(None) is None
    assert _common.load_prompt_text(TEXT, None) == TEXT


def test_explicit_snapshot_survives_later_process_directory_change(paths, monkeypatch):
    caller, child = paths
    monkeypatch.chdir(child)
    assert _common.load_prompt_text(None, "prompt.txt", process_cwd=caller) == TEXT
    assert _common.validate_wrapper_cwd("child", process_cwd=caller) == str(child)


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize("absolute", [False, True])
def test_every_wrapper_sends_caller_prompt_and_resolved_child_cwd(
    wrapper, absolute, paths, fake_provider, monkeypatch
):
    caller, child = paths
    prompt_arg = str(caller / "prompt.txt") if absolute else "prompt.txt"
    cwd_arg = str(child) if absolute else "child"
    monkeypatch.setattr(sys, "argv", [wrapper.__file__, "--prompt-file", prompt_arg, "--cwd", cwd_arg])
    assert wrapper.main() == 0
    calls, binaries = fake_provider
    assert len(calls) == len(binaries) == 1
    assert calls[0]["prompt"] == TEXT
    assert calls[0]["cwd"] == str(child)


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_entry_snapshot_is_shared_by_both_path_loaders(wrapper, paths, fake_provider, monkeypatch):
    caller, child = paths
    original = _common.load_prompt_text

    def load_then_move(*args, **kwargs):
        text = original(*args, **kwargs)
        monkeypatch.chdir(child)
        return text

    target = _common if wrapper is antigravity_wrapper else wrapper
    monkeypatch.setattr(target, "load_prompt_text", load_then_move)
    monkeypatch.setattr(sys, "argv", [wrapper.__file__, "--prompt-file", "prompt.txt", "--cwd", "child"])
    assert wrapper.main() == 0
    assert fake_provider[0][0]["prompt"] == TEXT
    assert fake_provider[0][0]["cwd"] == str(child)


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize("damage", [
    "missing-prompt", "directory-prompt", "utf8", "blank", "file-cwd",
    "missing-cwd", "outside-prompt", "outside-cwd", "nul",
])
def test_invalid_paths_fail_before_vendor_resolution(wrapper, damage, paths, fake_provider, monkeypatch):
    caller, child = paths
    prompt_arg, cwd_arg = "prompt.txt", "child"
    if damage == "missing-prompt":
        prompt_arg = "missing.txt"
    elif damage == "directory-prompt":
        prompt_arg = "child"
    elif damage == "utf8":
        (caller / prompt_arg).write_bytes(b"\xff")
    elif damage == "blank":
        (caller / prompt_arg).write_text(" \n")
    elif damage == "file-cwd":
        cwd_arg = "prompt.txt"
    elif damage == "missing-cwd":
        cwd_arg = "missing"
    elif damage == "outside-prompt":
        (caller.parent / "outside.txt").write_text("outside")
        prompt_arg = "../outside.txt"
    elif damage == "outside-cwd":
        cwd_arg = ".."
    else:
        prompt_arg = "bad\x00path"
    monkeypatch.setattr(sys, "argv", [wrapper.__file__, "--prompt-file", prompt_arg, "--cwd", cwd_arg])
    assert wrapper.main() == _common.EXIT_ARG_ERROR
    assert fake_provider == ([], [])
