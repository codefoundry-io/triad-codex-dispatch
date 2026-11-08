"""AGY 1.5.3 canonical reads retain containment and bounded diagnostics."""
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import agy_hook
import antigravity_wrapper as wrapper
from test_agy_finish_resubmission import step, failed_finish, finished, run_result, interpret
from test_agy_search_profile import profiles  # noqa: F401
from test_v2_google_wrappers import route, ready  # noqa: F401


def test_canonical_read_is_allowed_but_task_management_is_denied():
    assert agy_hook.decide({"toolCall": {"name": "read_file", "args": {"Path": "/review/TASK.md"}}})["decision"] == "allow"
    assert agy_hook.decide({"toolCall": {"name": "manage_task", "args": {}}})["decision"] == "deny"


def test_canonical_read_projects_path_without_using_legacy_argument(tmp_path):
    event = {"event": "step_update", "step_update": {
        "state": "DONE", "step_type": "tool", "tool_name": "read_file",
        "tool_info": {"parameters": {"Path": str(tmp_path / "TASK.md"),
                                      "AbsolutePath": str(tmp_path / "wrong.md")}}}}
    projected = wrapper._project_agy_done_view_files([event], str(tmp_path))
    assert projected is not None
    assert projected["relative_paths"] == ["TASK.md"]


def test_canonical_read_supports_same_run_finish_recovery():
    result = interpret(run_result([step("read_file"), failed_finish(), finished()]))
    assert result.exit_code == 0
    assert result.validated is not None


@pytest.mark.parametrize("status", ["SUCCESS", "ERROR"])
@pytest.mark.parametrize("state", ["DONE", "ACTIVE", "ERROR"])
def test_executed_task_manager_withholds_an_otherwise_valid_success(status, state):
    result = interpret(run_result([step("read_file"), step("manage_task", state, index=2)], status=status))
    assert result.exit_code == 65
    assert result.classification == "admission-refused"
    assert result.validated is None
    assert result.final_answer == ""


def test_task_manager_active_then_recognized_denial_is_not_execution():
    events = [step("read_file"), step("manage_task", "ACTIVE", index=2),
              step("manage_task", "ERROR", index=2,
                   error={"message": "tool call denied by pre-tool hook"})]
    result = interpret(run_result(events, status="SUCCESS"))
    assert result.exit_code == 0


def test_task_manager_hidden_in_secondary_name_is_refused():
    result = interpret(run_result([step("read_file", alias="manage_task")], status="SUCCESS"))
    assert result.exit_code == 65
    assert result.validated is None


@pytest.mark.parametrize("denial_index", [True, 1.0])
def test_task_denial_requires_an_integer_matching_index(denial_index):
    result = interpret(run_result([step("manage_task", "ACTIVE", index=1),
        step("manage_task", "ERROR", index=denial_index,
             error={"message": "tool call denied by pre-tool hook"})], status="SUCCESS"))
    assert result.exit_code == 65


@pytest.mark.parametrize("route", ["agy"], indirect=True)
@pytest.mark.parametrize("sandbox,expected", [("read-only", 65), (None, 0)])
def test_raw_cli_task_manager_refusal_is_limited_to_read_only(profiles, route, monkeypatch, sandbox, expected):
    ready(route)
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _: str(route["home"] / "agy"))
    monkeypatch.setattr(wrapper._common, "_run_once", lambda *a, **k:
                        run_result([step("manage_task")], status="SUCCESS"))
    options = ["--prompt", "Read the fixture", "--cwd", str(route["home"])]
    if sandbox:
        options += ["--sandbox", sandbox]
    rc, output, _ = route["invoke"](base=options)
    assert rc == expected
    if expected:
        assert output == ""


@pytest.mark.parametrize("name", [[], {}])
def test_malformed_diagnostic_tool_name_does_not_change_success(tmp_path, name):
    run = run_result([step(name)], status="SUCCESS")
    run._effective_cwd = str(tmp_path)
    result = interpret(run)
    assert result.exit_code == 0
    assert result._agy_read_telemetry is None

