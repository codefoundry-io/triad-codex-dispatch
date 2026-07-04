# tests/test_claude_classification.py — classification-mapping tests
# Fake CLI → shared token set. Real-CLI evidence grounded in spike-e-claude-findings.md.
import re
import sys
from pathlib import Path

# Import _run helper from the sibling test module.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_claude_wrapper import _run


def _cls(stderr: str):
    """Parse the classification token from the LAST [wrapper] claude <class> stderr line.

    The wrapper may emit two [wrapper] lines in some paths:
      1. The initial classify() result from _run_once (may be "ok" when vendor exits 0).
      2. A re-emit after extraction re-classifies (e.g. "extraction-error", "oauth-env").
    The last line is the authoritative final classification.
    """
    token = None
    for m in re.finditer(r"\[wrapper\] claude (\S+) ", stderr):
        token = m.group(1)
    return token


def test_is_error_maps_to_oauth_env(tmp_path):
    """is_error mode (fake_claude) — real auth-failure text from spike-e-claude-findings.md.

    The fake CLI emits the exact envelope captured from the real 401:
      {"is_error": true, "api_error_status": 401,
       "result": "Failed to authenticate. API Error: 401 Invalid authentication credentials"}

    OAUTH_ENV_PATTERNS contains "invalid authentication credentials" (distinctive,
    FP-safe per the repair-agent guard). classify() finds the phrase in stdout
    (the JSON envelope) → returns "oauth-env" before extraction is attempted.
    Exit code must be EXIT_TERMINAL (65) — not 0 or 1.
    """
    r = _run(tmp_path, fake_mode="is_error")
    assert r.returncode == 65, (
        f"is_error (auth 401) must be terminal EXIT_TERMINAL=65; got {r.returncode}"
    )
    assert _cls(r.stderr) == "oauth-env", (
        f"is_error should classify as 'oauth-env'; got {_cls(r.stderr)!r}\n"
        f"stderr={r.stderr!r}"
    )


def test_is_error_success_envelope_maps_to_oauth_env(tmp_path):
    """Claude can emit auth errors in an rc=0 success envelope; still terminal."""
    r = _run(tmp_path, fake_mode="is_error_success")
    assert r.returncode == 65, (
        f"rc=0 is_error envelope must be terminal EXIT_TERMINAL=65; got {r.returncode}"
    )
    assert _cls(r.stderr) == "oauth-env", (
        f"rc=0 is_error envelope should classify as oauth-env; got {_cls(r.stderr)!r}\n"
        f"stderr={r.stderr!r}"
    )


def test_permission_denial_envelope_is_task_blocked_not_repair(tmp_path):
    """Claude permission_denials with no usable result should not route to repair."""
    r = _run(tmp_path, fake_mode="permission_denied")
    assert r.returncode == 65, (
        f"permission denial envelope must be terminal EXIT_TERMINAL=65; got {r.returncode}"
    )
    assert _cls(r.stderr) == "task-blocked", (
        f"permission denial should classify as task-blocked; got {_cls(r.stderr)!r}\n"
        f"stderr={r.stderr!r}"
    )


def test_empty_stdout_is_extraction_error(tmp_path):
    """empty mode (fake_claude) — no stdout at all.

    extract_claude_answer returns ("", "empty stdout — claude envelope missing").
    run_cli_with_retry promotes exit_code → EXIT_CLI_FAIL and sets
    classification = "extraction-error" directly (bypasses L2 pattern matching).
    """
    r = _run(tmp_path, fake_mode="empty")
    assert _cls(r.stderr) == "extraction-error", (
        f"empty stdout should classify as 'extraction-error'; got {_cls(r.stderr)!r}\n"
        f"stderr={r.stderr!r}"
    )


def test_structured_output_ok(tmp_path):
    """structured mode (fake_claude) — structured_output field present.

    extract_claude_answer detects structured_output and returns the JSON string.
    Wrapper exits 0 and stdout contains the JSON with "todos".
    """
    r = _run(tmp_path, fake_mode="structured")
    assert r.returncode == 0, (
        f"structured mode should succeed (rc=0); got rc={r.returncode}\n"
        f"stderr={r.stderr!r}"
    )
    assert '"todos"' in r.stdout, (
        f"stdout should contain '\"todos\"'; got {r.stdout!r}"
    )


def test_structured_output_retries_are_schema_fail_not_repair(tmp_path):
    """Claude schema retry exhaustion is a schema failure, not repair-agent territory."""
    r = _run(tmp_path, fake_mode="schema_retries")
    assert r.returncode == 66, (
        f"schema retry exhaustion must exit 66; got rc={r.returncode}\n"
        f"stderr={r.stderr!r}"
    )
    assert _cls(r.stderr) == "schema-fail", (
        f"schema retry exhaustion should classify as schema-fail; got {_cls(r.stderr)!r}\n"
        f"stderr={r.stderr!r}"
    )


def test_structured_output_retries_are_schema_fail_even_with_nonzero_vendor_rc(tmp_path):
    """Classify Claude schema retry envelopes from stdout even if vendor rc is generic nonzero."""
    r = _run(tmp_path, fake_mode="schema_retries_nonzero")
    assert r.returncode == 66, (
        f"schema retry envelope must exit 66 even with vendor rc=1; got rc={r.returncode}\n"
        f"stderr={r.stderr!r}"
    )
    assert _cls(r.stderr) == "schema-fail", (
        f"schema retry envelope should classify as schema-fail; got {_cls(r.stderr)!r}\n"
        f"stderr={r.stderr!r}"
    )


def test_structured_output_retries_override_capacity_stderr(tmp_path):
    """Claude schema retry envelopes are schema failures even if stderr has retryable words."""
    r = _run(tmp_path, fake_mode="schema_retries_server_stderr")
    assert r.returncode == 66, (
        f"schema retry envelope must exit 66 instead of capacity retry-give-up; got rc={r.returncode}\n"
        f"stderr={r.stderr!r}"
    )
    assert _cls(r.stderr) == "schema-fail", (
        f"schema retry envelope should classify as schema-fail; got {_cls(r.stderr)!r}\n"
        f"stderr={r.stderr!r}"
    )
