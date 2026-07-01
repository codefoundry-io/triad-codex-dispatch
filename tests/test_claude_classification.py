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
    assert r.returncode != 0, "is_error mode must fail (rc != 0)"
    assert _cls(r.stderr) == "oauth-env", (
        f"is_error should classify as 'oauth-env'; got {_cls(r.stderr)!r}\n"
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
