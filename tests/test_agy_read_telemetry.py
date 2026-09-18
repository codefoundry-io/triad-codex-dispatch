"""Diagnostic projection must not participate in formal result admission."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common  # noqa: E402
import antigravity_wrapper as wrapper  # noqa: E402
from verdict_schema import LegVerdict  # noqa: E402


def event(path, **changes):
    step = {"state": "DONE", "step_type": "tool", "tool_name": "view_file",
            "tool_info": {"parameters": {"AbsolutePath": path},
                          "output": "DO_NOT_PROJECT_OUTPUT",
                          "error": {"message": "DO_NOT_PROJECT_ERROR"}}}
    step.update(changes)
    return {"event": "step_update", "step_update": step}


def interpret(events, cwd, *, status="SUCCESS", plan_mode=True):
    payload = {"review_id": "s8-r1", "family": "google", "content_digest": "a" * 64,
               "verdict": "SAFE", "criteria_checked": ["correctness"],
               "findings": [], "affected_surfaces_inspected": ["file.py"],
               "open_questions": []}
    terminal = {"event": "result", "result": {"status": status,
                "structured_output": payload, "response": json.dumps(payload)}}
    stream = "\n".join(json.dumps(item) for item in [*events, terminal])
    run = _common.RunResult(0, stream, "", 0.1, vendor_exit_code=0)
    run._effective_cwd = cwd
    result = wrapper._interpret_run(run, LegVerdict, plan_mode=plan_mode,
        expected_review_id="s8-r1", expected_family="google",
        expected_content_digest="a" * 64)
    assert result is run
    if status == "SUCCESS":
        assert result.exit_code == 0
        assert result.validated == payload
    else:
        assert result.exit_code == _common.EXIT_TERMINAL
        assert result.classification == "vendor-error"
        assert result.validated is None
    assert result.stdout == stream
    return result


@pytest.mark.parametrize("status", ["SUCCESS", "ERROR"])
def test_count_observed_done_events_without_claiming_success_or_unique_reads(tmp_path, status):
    root = tmp_path.resolve()
    steps = [event(str(root / "src/a.py")), event(str(root / "src/a.py")),
             event(str(root / "src/b.py")), event(str(root / "active"), state="ACTIVE"),
             event(str(root / "other"), tool_name="write_to_file"),
             event(str(root / "text"), step_type="agent_response"),
             {"event": "other", "step_update": event(str(root / "ignored"))["step_update"]},
             {"event": "step_update", "step_update": None}]
    run = interpret(steps, str(root), status=status)
    assert run._agy_read_telemetry == {"done_view_file_event_count": 3,
                                       "relative_paths": ["src/a.py", "src/b.py"]}


@pytest.mark.parametrize("cwd", [None, "relative", "bad\x00cwd"])
def test_no_usable_host_cwd_means_no_telemetry(tmp_path, cwd):
    run = interpret([event(str(tmp_path / "a.py"))], cwd)
    assert run._agy_read_telemetry is None


def test_no_events_and_ordinary_calls_have_no_telemetry(tmp_path):
    assert interpret([], str(tmp_path.resolve()))._agy_read_telemetry is None
    run = interpret([event(str(tmp_path / "a.py"))], str(tmp_path.resolve()), plan_mode=False)
    assert run._agy_read_telemetry is None


def test_paths_are_bounded_relative_projections_not_tool_output(tmp_path):
    root = tmp_path.resolve() / "work"
    root.mkdir()
    outside = tmp_path.resolve() / "outside"
    outside.mkdir()
    (root / "escape").symlink_to(outside, target_is_directory=True)
    (root / "alias").symlink_to(root / "inside", target_is_directory=True)
    bad = [None, [], {}, 17, "relative.py", str(outside / "DO_NOT_PROJECT_OUTSIDE"),
           str(root / "sub/../in-cwd.py"),
           str(root / "../outside/file.py"), str(root / "escape/file.py"),
           str(root) + "/null\x00", str(root) + "/surrogate\ud800"]
    steps = [event(path) for path in bad]
    steps += [event(None, tool_info=None), event(None, tool_info={"parameters": []}),
              event(str(root / "alias/한글.py")), event(str(root / "inside/한글.py"))]
    data = interpret(steps, str(root))._agy_read_telemetry
    assert data == {"done_view_file_event_count": len(steps),
                    "relative_paths": ["inside/한글.py"]}
    assert "DO_NOT_PROJECT" not in json.dumps(data)


def test_relative_path_length_and_list_caps(tmp_path):
    root = tmp_path.resolve()
    prefix = ("a" * 250 + "/") * 4
    exact = prefix + "b" * (1024 - len(prefix))
    steps = [event(str(root / exact)), event(str(root / (exact + "b")))]
    steps += [event(str(root / f"file-{i}")) for i in range(140)]
    data = interpret(steps, str(root))._agy_read_telemetry
    assert data["done_view_file_event_count"] == 142
    assert data["relative_paths"] == [exact] + [f"file-{i}" for i in range(127)]


@pytest.mark.parametrize("failure", [OSError, RuntimeError, ValueError])
def test_path_resolution_error_never_changes_verdict(monkeypatch, tmp_path, failure):
    root = tmp_path.resolve()
    original = Path.resolve

    def resolve(path, *args, **kwargs):
        if path.name == "broken":
            raise failure("path cannot be resolved")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)
    run = interpret([event(str(root / "broken")), event(str(root / "good"))], str(root))
    assert run._agy_read_telemetry == {"done_view_file_event_count": 2,
                                       "relative_paths": ["good"]}


@pytest.mark.parametrize("redaction", [None, "TRIAD_AUDIT_REDACT_PROMPTS", "TRIAD_WRAPPER_HARDENED"])
def test_audit_projection_privacy_and_failure_ipc_exclusion(monkeypatch, tmp_path, redaction):
    root = tmp_path.resolve()
    logs = root / "logs"
    monkeypatch.setattr(_common, "_LOG_DIR", logs)
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", True)
    for name in ("TRIAD_AUDIT_REDACT_PROMPTS", "TRIAD_WRAPPER_HARDENED"):
        monkeypatch.delenv(name, raising=False)
    if redaction:
        monkeypatch.setenv(redaction, "1")
    run = interpret([event(str(root / "private-file.py"))], str(root), status="ERROR")
    for cli in ("antigravity", "claude"):
        assert _common.audit(cli, [cli], "review", run) is True
        rec = json.loads((logs / cli / "audit.jsonl").read_text().splitlines()[-1])
        if cli == "claude":
            assert "agy_read_telemetry" not in rec
        else:
            expected = {"done_view_file_event_count": 1}
            if not redaction:
                expected["relative_paths"] = ["private-file.py"]
            assert rec["agy_read_telemetry"] == expected
            if redaction:
                assert "private-file.py" not in json.dumps(rec)
    path = _common.emit_run_log("antigravity", ["wrapper"], ["agy"], "review", run)
    ipc = json.loads(path.read_text())
    assert "agy_read_telemetry" not in ipc and "_agy_read_telemetry" not in ipc
    assert ipc["exit_code"] == run.exit_code
