"""C37/R-CLASSIFY contract fixtures, not additional vendor captures.

Mutations caught: flattening envelope provenance, capacity/timeout before auth,
raw-answer auth matching, and lost STOP during wrapper extraction or signals.
"""
import json
import signal
import sys
from pathlib import Path

import pytest
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
import _common
import antigravity_wrapper
import claude_wrapper


@pytest.fixture(autouse=True)
def isolated_runtime(monkeypatch, tmp_path):
    monkeypatch.setattr(_common, "_classifier_extension_path", lambda: tmp_path / "extension.json")
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", True)
    monkeypatch.setattr(_common, "prune_stale_tmp_dirs", lambda *a, **kw: None)
    monkeypatch.setenv("TRIAD_SERVER_CAP_NO_BACKOFF", "1")


def agy(result):
    return json.dumps({"event": "result", "result": result})


LOGIN = "Not logged in · Please run /login"
BANNER = "Authentication required. Please visit the URL to sign in"
CARRIERS = [
    ("codex", "", json.dumps({"type": "error", "message": "unexpected status 401 Unauthorized: Incorrect API key provided"})),
    ("codex", "", json.dumps({"type": "turn.failed", "error": {"message": "Your access token could not be refreshed"}})),
    ("codex", "Error loading configuration: Please log out and sign in again.", ""),
    ("claude", "", json.dumps({"is_error": True, "api_error_status": 401, "result": ""})),
    ("claude", "", json.dumps({"is_error": True, "result": LOGIN})),
    ("gemini", "", json.dumps({"error": {"code": 400, "message": "API key not valid. Please pass a valid API key."}})),
    ("gemini", '[ERROR] {\n"error": {"code": 401, "message": "failure"}\n}', ""),
    ("gemini", "Cached credentials are not valid: refresh failed", ""),
    ("antigravity", BANNER, ""),
    ("antigravity", "", agy({"status": "ERROR", "error": "authentication failed or timed out", "num_turns": 0})),
]


@pytest.mark.parametrize("cli,stderr,stdout", CARRIERS)
@pytest.mark.parametrize("exit_code", [1, _common.EXIT_TIMEOUT])
def test_C37_auth_carrier_precedes_capacity_and_timeout(cli, stderr, stdout, exit_code):
    assert _common.classify(cli, "MODEL_CAPACITY_EXHAUSTED\n" + stderr, stdout,
                            exit_code, vendor_exit_code=1) == "oauth-env"


@pytest.mark.parametrize("cli", ["codex", "claude", "gemini", "antigravity"])
def test_C37_quoted_authentication_outside_carrier_is_not_a_stop(cli):
    assert _common.classify(cli, "", 'review quotes "401 Unauthorized" and "auth error"',
                            1, vendor_exit_code=1) == "unknown"


@pytest.mark.parametrize("cli,stdout", [
    ("codex", json.dumps({"type": "item.completed", "item": {"type": "command_execution", "output": "401 Unauthorized"}})),
    ("claude", json.dumps({"is_error": False, "result": "401 Unauthorized"})),
    ("gemini", json.dumps({"error": {"code": 1, "message": "Error executing tool shell: 401 Unauthorized"}})),
    ("antigravity", agy({"status": "ERROR", "error": "Schema validation failed\nquoted 401 Unauthorized"})),
])
def test_C37_tool_or_reflected_answer_text_is_not_authentication(cli, stdout):
    # Other phrase lists are a separate unit; retain the existing schema token.
    want = "schema-rejected" if cli == "antigravity" else "unknown"
    assert _common.classify(cli, "", stdout, 1, vendor_exit_code=1) == want


@pytest.mark.parametrize("separator,want", [("\n", "oauth-env"), ("\r", "schema-rejected"), ("\u2028", "schema-rejected")])
def test_C37_schema_report_banner_uses_json_line_feeds_only(separator, want):
    stdout = agy({"status": "ERROR", "error": "Schema validation failed" + separator + BANNER})
    assert _common.classify("antigravity", "", stdout, 1, vendor_exit_code=1) == want


def test_C37_banner_inside_stderr_sentence_is_not_a_carrier():
    assert _common.classify("antigravity", "quoted: " + BANNER, "", 1, vendor_exit_code=1) == "unknown"


def test_C37_codex_completed_answer_ignores_transient_error():
    stdout = "\n".join(json.dumps(e) for e in [
        {"type": "error", "message": "401 Unauthorized"},
        {"type": "item.completed", "item": {"type": "agent_message", "text": "done"}},
        {"type": "turn.completed"}])
    assert _common.classify("codex", "", stdout, 1, vendor_exit_code=0) == "unknown"


def test_C37_gemini_tool_message_does_not_override_auth_code():
    stdout = json.dumps({"error": {"code": 401, "message": "Error executing tool shell: failure"}})
    assert _common.classify("gemini", "", stdout, 1, vendor_exit_code=1) == "oauth-env"


@pytest.mark.parametrize("prefix", ["quoted: ", "Error executing tool shell: "])
def test_C37_gemini_error_object_inside_other_prose_is_not_a_carrier(prefix):
    stderr = prefix + json.dumps({"error": {"code": 401, "message": "failure"}})
    assert _common.classify("gemini", stderr, "", 1, vendor_exit_code=1) == "unknown"


@pytest.mark.parametrize("value", [None, 42, [], {"message": []}])
@pytest.mark.parametrize("cli", ["codex", "claude", "gemini", "antigravity"])
def test_C37_nontext_error_fields_do_not_raise(cli, value):
    stdout = {"codex": {"type": "turn.failed", "error": value},
              "claude": {"is_error": True, "result": value},
              "gemini": {"error": value},
              "antigravity": {"event": "result", "result": {"status": "ERROR", "error": value}}}[cli]
    assert _common.classify(cli, "", json.dumps(stdout), 1, vendor_exit_code=1) == "unknown"


def child(tmp_path, stdout, stderr="", rc=0):
    starts = tmp_path / "starts"
    script = ("import sys; from pathlib import Path; "
              f"p=Path({str(starts)!r}); p.write_text(p.read_text()+'x' if p.exists() else 'x'); "
              f"print({stdout!r}); print({stderr!r}, file=sys.stderr); sys.exit({rc})")
    return [sys.executable, "-c", script], starts


class Answer(BaseModel):
    ok: bool


@pytest.mark.parametrize("formal", [False, True])
def test_C37_claude_zero_exit_error_envelope_stops_without_retry(tmp_path, formal):
    cmd, starts = child(tmp_path, json.dumps({"is_error": True, "result": LOGIN}), "overloaded_error")
    if formal:
        result = claude_wrapper._run_native_structured_once(cmd, str(tmp_path), 5, Answer)
    else:
        result = _common.run_cli_with_retry("claude", lambda _: cmd, "fixture", str(tmp_path), 5)
    assert (result.classification, result.exit_code) == ("oauth-env", 65)
    assert result.final_answer == "" and starts.read_text() == "x"


@pytest.mark.parametrize("formal", [False, True])
def test_C37_claude_structured_answer_wins_over_error_envelope(tmp_path, formal):
    stdout = json.dumps({"is_error": True, "api_error_status": 401,
                         "result": LOGIN, "structured_output": {"ok": True}})
    cmd, _ = child(tmp_path, stdout)
    result = (claude_wrapper._run_native_structured_once(cmd, str(tmp_path), 5, Answer)
              if formal else _common.run_cli_with_retry("claude", lambda _: cmd, "fixture", str(tmp_path), 5))
    assert (result.classification, result.exit_code) == ("ok", 0)
    assert json.loads(result.final_answer) == {"ok": True}


@pytest.mark.parametrize("rc", [0, 1])
def test_C37_agy_terminal_error_stops_without_flattening(tmp_path, rc):
    cmd, _ = child(tmp_path, agy({"status": "ERROR", "error": "authentication failed or timed out", "num_turns": 0}), rc=rc)
    run = _common._run_once("antigravity", cmd, str(tmp_path), 5, classify_and_log=False)
    result = antigravity_wrapper._interpret_run(run, None)
    assert (result.classification, result.exit_code) == ("oauth-env", 65)
    assert result.final_answer == ""


def test_C37_agy_completed_answer_ignores_banner(tmp_path):
    cmd, _ = child(tmp_path, agy({"status": "SUCCESS", "response": "done"}), BANNER)
    run = _common._run_once("antigravity", cmd, str(tmp_path), 5, classify_and_log=False)
    result = antigravity_wrapper._interpret_run(run, None)
    assert (result.classification, result.exit_code, result.final_answer) == ("ok", 0, "done")


@pytest.mark.parametrize("cli,stderr,stdout", [CARRIERS[4], CARRIERS[5], CARRIERS[9]])
def test_C37_real_timeout_preserves_printed_auth_carrier(tmp_path, cli, stderr, stdout):
    script = f"import sys,time; print({stdout!r},flush=True); print({stderr!r},file=sys.stderr,flush=True); time.sleep(30)"
    result = _common._run_once(cli, [sys.executable, "-c", script], str(tmp_path), 1, classify_and_log=False)
    assert (result.classification, result.exit_code) == ("oauth-env", 65)
    assert result.final_answer == ""


def test_C37_late_signal_preserves_captured_authentication(monkeypatch, tmp_path):
    original = _common._run_once_owned

    def after_capture(*args):
        result = original(*args)
        signal.raise_signal(signal.SIGTERM)
        return result

    monkeypatch.setattr(_common, "_run_once_owned", after_capture)
    cmd, _ = child(tmp_path, json.dumps({"is_error": True, "result": LOGIN}))
    result = _common._run_once("claude", cmd, str(tmp_path), 5)
    assert (result.classification, result.exit_code) == ("oauth-env", 65)
    assert result._output_transport_failed and result.final_answer == ""


def test_C37_obsolete_raw_auth_extension_is_ignored_and_reported(tmp_path, capsys):
    (tmp_path / "extension.json").write_text(json.dumps({"claude": {"patterns": {"OAUTH_ENV_PATTERNS": ["fabricated auth phrase"]}}}))
    assert _common.classify("claude", "fabricated auth phrase", "", 1) == "unknown"
    assert "OAUTH_ENV_PATTERNS" in capsys.readouterr().err


def test_C37_raw_auth_patch_proposal_is_refused(tmp_path):
    with pytest.raises(ValueError):
        _common.apply_classifier_patch("claude", {"classification": "oauth-env",
            "pattern_list": "OAUTH_ENV_PATTERNS", "substring": "fabricated auth phrase",
            "reason": "synthetic contract control"})
    assert not (tmp_path / "extension.json").exists()


@pytest.mark.parametrize("response,want", [("", ("oauth-env", 65)), ("done", ("ok", 0))])
def test_C37_agy_banner_on_completed_no_answer(response, want):
    run = _common.RunResult(0, agy({"status": "SUCCESS", "response": response}), BANNER,
                            0.1, vendor_exit_code=0)
    result = antigravity_wrapper._interpret_run(run, None)
    assert (result.classification, result.exit_code) == want
    assert result.final_answer == response


@pytest.mark.parametrize("plan_mode,want", [(True, ("ok", 0)), (False, ("vendor-error", 65))])
@pytest.mark.parametrize("command", ["cat > credentials-review.json", "gh auth login",
    "cat << 'EOF' > notes.md\nAuthentication required. Please visit the URL to log in:\nEOF"])
def test_C74_agy_denied_command_is_reflected_text(plan_mode, want, command):
    payload = {"ok": True}
    run = _common.RunResult(0, agy({"status": "ERROR",
        "error": 'permission check failed for command "' + command + '"',
        "response": json.dumps(payload), "structured_output": payload}), "", 0.1, vendor_exit_code=0)
    result = antigravity_wrapper._interpret_run(run, Answer, plan_mode=plan_mode)
    assert (result.classification, result.exit_code) == want
    assert result.validated == (payload if plan_mode else None)


@pytest.mark.parametrize("formal", [True, False])
@pytest.mark.parametrize("quoted", ["400 Bad Request", "too many requests", "schema validation failed"])
def test_C74_claude_denied_tool_input_does_not_change_error_class(tmp_path, formal, quoted):
    stdout = json.dumps({"is_error": True, "api_error_status": 500,
        "result": "API Error: 500 Internal server error", "structured_output": None,
        "permission_denials": [{"tool_name": "Write", "tool_input": {"content": quoted}}]})
    cmd, starts = child(tmp_path, stdout)
    result = (claude_wrapper._run_native_structured_once(cmd, str(tmp_path), 5, Answer)
              if formal else _common.run_cli_with_retry("claude", lambda _: cmd, "fixture", str(tmp_path), 5))
    assert (result.classification, result.exit_code) == ("extraction-error", 1)
    assert result.final_answer == "" and starts.read_text() == "x"
