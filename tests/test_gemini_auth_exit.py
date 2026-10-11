"""C37/DL-99: Gemini v0.63.0 exitCodes.ts defines authentication exit 41.

These are provider-free code-carrier tests, not invented vendor output shapes.
"""
import signal
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
import _common


@pytest.fixture(autouse=True)
def isolated_classifier(monkeypatch, tmp_path):
    monkeypatch.setattr(_common, "_load_classifier_extension", lambda: {})
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", True)
    # Global stale-log sweeping is unrelated to authentication classification.
    monkeypatch.setattr(_common, "prune_stale_tmp_dirs", lambda *args, **kwargs: None)


@pytest.mark.parametrize("exit_code", [1, _common.EXIT_TIMEOUT])
def test_C37_gemini_auth_exit_precedes_capacity_and_timeout(exit_code):
    assert _common.classify("gemini", "MODEL_CAPACITY_EXHAUSTED", "", exit_code,
                            vendor_exit_code=41) == "oauth-env"


@pytest.mark.parametrize("cli", ["claude", "codex", "antigravity"])
def test_C37_exit_41_is_not_an_auth_code_on_another_cli(cli):
    assert _common.classify(cli, "", "", 1, vendor_exit_code=41) == "unknown"


@pytest.mark.parametrize("classify_and_log", [True, False])
def test_C37_real_child_auth_exit_is_terminal_without_output(tmp_path, classify_and_log):
    result = _common._run_once("gemini", [sys.executable, "-c", "raise SystemExit(41)"],
                               str(tmp_path), 5, classify_and_log=classify_and_log)
    assert (result.classification, result.exit_code, result.vendor_exit_code) == ("oauth-env", 65, 41)
    assert result.final_answer == "" and result.validated is None


def test_C37_gemini_auth_exit_never_retries(tmp_path):
    starts = tmp_path / "starts"
    script = ("from pathlib import Path; "
              f"p=Path({str(starts)!r}); p.write_text(p.read_text()+'x' if p.exists() else 'x'); "
              "raise SystemExit(41)")
    result = _common.run_cli_with_retry("gemini", lambda _: [sys.executable, "-c", script],
                                        "fixture", str(tmp_path), 5)
    assert (result.classification, result.exit_code) == ("oauth-env", 65)
    assert starts.read_text() == "x"


def test_C37_capacity_stderr_plus_auth_exit_runs_only_once(monkeypatch, tmp_path):
    monkeypatch.setenv("TRIAD_SERVER_CAP_NO_BACKOFF", "1")
    starts = tmp_path / "starts"
    script = ("import sys; from pathlib import Path; "
              f"p=Path({str(starts)!r}); p.write_text(p.read_text()+'x' if p.exists() else 'x'); "
              "print('MODEL_CAPACITY_EXHAUSTED', file=sys.stderr); sys.exit(41)")
    result = _common.run_cli_with_retry("gemini", lambda _: [sys.executable, "-c", script],
                                        "fixture", str(tmp_path), 5)
    assert (result.classification, result.exit_code) == ("oauth-env", 65)
    assert starts.read_text() == "x"


def test_C37_timeout_term_handler_auth_exit_preserves_stop(tmp_path):
    script = "import signal,sys,time; signal.signal(signal.SIGTERM, lambda *args: sys.exit(41)); time.sleep(30)"
    result = _common._run_once("gemini", [sys.executable, "-c", script], str(tmp_path), 1)
    assert (result.classification, result.exit_code, result.vendor_exit_code) == ("oauth-env", 65, 41)


@pytest.mark.parametrize("signum", [signal.SIGTERM, signal.SIGHUP])
def test_C37_signal_after_captured_auth_exit_preserves_stop(monkeypatch, tmp_path, signum):
    original = _common._run_once_owned

    def signal_after_collect(*args):
        result = original(*args)
        # Real child has terminated and its exit is known; signal reaches parent
        # at the final ownership boundary, without racing an arbitrary sleep.
        signal.raise_signal(signum)
        return result

    monkeypatch.setattr(_common, "_run_once_owned", signal_after_collect)
    result = _common._run_once("gemini", [sys.executable, "-c", "raise SystemExit(41)"],
                               str(tmp_path), 5)
    assert (result.classification, result.exit_code, result.vendor_exit_code) == ("oauth-env", 65, 41)
    assert result._output_transport_failed and result.final_answer == "" and result.validated is None
    assert "interrupted" in result.extraction_error
