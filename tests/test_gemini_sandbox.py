# Hermetic tests for gemini_wrapper.py --sandbox read-only (Policy Engine).
# A fake `gemini` on PATH captures the argv the wrapper builds; we assert
# --policy <readonly.toml> is attached for read-only and NOT otherwise.
# (The policy's actual enforcement needs a live gemini — verified company-side.)
import os
import stat
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "bin" / "policies" / "gemini-readonly.toml"


def _fake_gemini_dir(tmp_path):
    fixture = tmp_path / "fake_gemini.py"
    fixture.write_text(
        "import json, os, sys\n"
        "open(os.environ['ARGV_FILE'], 'w').write('\\n'.join(sys.argv[1:]))\n"
        "error = os.environ.get('FAKE_GEMINI_ERROR')\n"
        "if error:\n"
        "    print(json.dumps({'response': '', 'stats': {}, 'error': error}))\n"
        "    raise SystemExit(int(os.environ.get('FAKE_GEMINI_RC', '0')))\n"
        "stderr_error = os.environ.get('FAKE_GEMINI_STDERR_ERROR')\n"
        "if stderr_error:\n"
        "    print('gemini warning before trailing json', file=sys.stderr)\n"
        "    print(json.dumps({'response': '', 'stats': {}, 'error': {'message': stderr_error}}), file=sys.stderr)\n"
        "    raise SystemExit(int(os.environ.get('FAKE_GEMINI_RC', '0')))\n"
        "response = os.environ.get('FAKE_GEMINI_RESPONSE', 'FAKE-OK')\n"
        "print(json.dumps({'response': response, 'stats': {}, 'error': None}))\n"
    )
    shim = tmp_path / "gemini"
    shim.write_text(f'#!/usr/bin/env bash\nexec python3 {fixture} "$@"\n')
    shim.chmod(shim.stat().st_mode | stat.S_IEXEC)
    return str(tmp_path)


def _run(tmp_path, *extra, env_overrides=None):
    argv_file = tmp_path / "argv.txt"
    pathdir = _fake_gemini_dir(tmp_path)
    env = dict(
        os.environ,
        PATH=pathdir + os.pathsep + os.environ["PATH"],
        ARGV_FILE=str(argv_file),
    )
    if env_overrides:
        env.update(env_overrides)
    r = subprocess.run(
        [sys.executable, str(ROOT / "bin/gemini_wrapper.py"), "--prompt", "hi", *extra],
        capture_output=True, text=True, env=env,
    )
    argv = argv_file.read_text() if argv_file.exists() else ""
    return r, argv


def _last_wrapper_class(stderr: str) -> str | None:
    token = None
    for line in stderr.splitlines():
        marker = "[wrapper] gemini "
        if marker in line:
            token = line.split(marker, 1)[1].split(" ", 1)[0]
    return token


def test_readonly_attaches_policy(tmp_path):
    _r, argv = _run(tmp_path, "--sandbox", "read-only")
    assert "--policy" in argv
    assert str(POLICY) in argv


def test_workspace_write_has_no_policy(tmp_path):
    _r, argv = _run(tmp_path, "--sandbox", "workspace-write")
    assert "--policy" not in argv


def test_default_attaches_readonly_policy(tmp_path):
    _r, argv = _run(tmp_path)
    assert "--policy" in argv
    assert str(POLICY) in argv


def test_yolo_approval_mode_rejected_before_spawn(tmp_path):
    r, argv = _run(tmp_path, "--approval-mode", "yolo")
    assert r.returncode != 0, "yolo approval mode must be rejected"
    assert "invalid choice" in r.stderr
    assert argv == "", "gemini must not be spawned on the rejected combo"


def test_plan_approval_mode_rejected_before_spawn(tmp_path):
    r, argv = _run(tmp_path, "--approval-mode", "plan")
    assert r.returncode != 0, "plan approval mode must be rejected"
    assert "invalid choice" in r.stderr
    assert argv == "", "gemini must not be spawned on the rejected combo"


def test_readonly_plus_auto_edit_rejected_before_spawn(tmp_path):
    r, argv = _run(tmp_path, "--sandbox", "read-only", "--approval-mode", "auto_edit")
    assert r.returncode != 0, "read-only + auto_edit must be rejected"
    assert "conflicts" in r.stderr
    assert argv == "", "gemini must not be spawned on the rejected combo"


def test_pydantic_validation_failure_reemits_schema_fail(tmp_path):
    pytest = __import__("pytest")
    pytest.importorskip("pydantic")
    model_file = tmp_path / "schema_model.py"
    model_file.write_text(
        textwrap.dedent(
            """
            from pydantic import BaseModel

            class Payload(BaseModel):
                count: int
            """
        ),
        encoding="utf-8",
    )
    r, _argv = _run(
        tmp_path,
        "--pydantic",
        "schema_model:Payload",
        env_overrides={
            "PYTHONPATH": str(tmp_path),
            "TRIAD_ALLOW_PYDANTIC_IMPORT": "1",
            "FAKE_GEMINI_RESPONSE": '{"count": "not-an-int"}',
        },
    )

    assert r.returncode == 66
    assert _last_wrapper_class(r.stderr) == "schema-fail", r.stderr


def test_ineligible_tier_error_is_terminal_not_repair(tmp_path):
    r, _argv = _run(
        tmp_path,
        env_overrides={
            "FAKE_GEMINI_ERROR": (
                "IneligibleTierError: This client is no longer supported for "
                "Gemini Code Assist. Please migrate to Antigravity."
            ),
        },
    )

    assert r.returncode == 65
    assert _last_wrapper_class(r.stderr) == "cli-subscription-cap", r.stderr


def test_ineligible_tier_error_in_nested_stderr_envelope_is_terminal(tmp_path):
    r, _argv = _run(
        tmp_path,
        env_overrides={
            "FAKE_GEMINI_STDERR_ERROR": (
                "IneligibleTierError: This client is no longer supported for "
                "Gemini Code Assist. Please migrate to Antigravity."
            ),
        },
    )

    assert r.returncode == 65
    assert _last_wrapper_class(r.stderr) == "cli-subscription-cap", r.stderr
