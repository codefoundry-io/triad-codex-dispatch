"""AGY 1.5.3 canonical reads retain containment and bounded diagnostics."""
from pathlib import Path
import json
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import agy_hook
import antigravity_wrapper as wrapper
from test_agy_finish_resubmission import step, failed_finish, finished, run_result, interpret
from test_agy_search_profile import profiles  # noqa: F401
from test_v2_google_wrappers import route, ready  # noqa: F401
from test_agy_network_carrier import make_run as network_run


def test_canonical_read_is_allowed_but_task_management_is_denied():
    assert agy_hook.decide({"toolCall": {"name": "read_file", "args": {"Path": "/review/TASK.md"}}})["decision"] == "allow"
    assert agy_hook.decide({"toolCall": {"name": "manage_task", "args": {}}})["decision"] == "deny"


def test_observed_agy153_task_list_shape_is_refused():
    records = [json.loads(line) for line in
               (ROOT / "tests/fixtures/agy153-manage-task-list.jsonl").read_text().splitlines()]
    result = interpret(run_result(records, status="SUCCESS"))
    assert (result.classification, result.exit_code) == ("admission-refused", 65)
    assert result.final_answer == "" and result.validated is None


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
    rc, output, error = route["invoke"](base=options)
    assert rc == expected
    if expected:
        assert output == ""
        assert "antigravity admission-refused" in error


@pytest.mark.parametrize("name", [[], {}])
def test_malformed_diagnostic_tool_name_does_not_change_success(tmp_path, name):
    run = run_result([step(name)], status="SUCCESS")
    run._effective_cwd = str(tmp_path)
    result = interpret(run)
    assert result.exit_code == 0
    assert result._agy_read_telemetry is None


@pytest.mark.parametrize("task", [False, True])
@pytest.mark.parametrize("read_only", [False, True])
def test_task_refusal_precedes_completed_network_error(task, read_only, monkeypatch):
    monkeypatch.setattr(wrapper._common, "_load_classifier_extension", lambda: {})
    run = network_run(events=[step("manage_task")] if task else [])
    result = wrapper._interpret_run(run, None, read_only=read_only)
    expected = ("admission-refused", 65) if task and read_only else ("server-capacity", 64)
    assert (result.classification, result.exit_code) == expected
    assert result.final_answer == ""


@pytest.mark.parametrize("bad", [
    '{"event":"step_update",',
    '{"event":"step_update","step_update":{"step_index":' + '9' * 5000 + '}}',
], ids=["truncated", "integer-limit"])
@pytest.mark.parametrize("formal", [False, True])
def test_undecodable_step_withholds_read_only_answer_without_traceback(bad, formal):
    run = run_result([], status="SUCCESS")
    run.stdout = bad + '\n' + run.stdout
    original = run.stdout
    old_limit = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(4300)
        result = wrapper._interpret_run(run, None, plan_mode=formal, read_only=not formal)
    finally:
        sys.set_int_max_str_digits(old_limit)
    assert (result.classification, result.exit_code) == ("admission-refused", 65)
    assert result.final_answer == "" and result.validated is None
    assert result.stdout == original


def test_decoder_recursion_limit_withholds_read_only_answer(monkeypatch):
    # Decoder recursion limits vary by Python version; exercise the documented
    # failure at the decoder boundary without relying on a fixed nesting depth.
    original_loads = wrapper.json.loads
    bad = '{"event":"step_update","step_update":{}}'
    def limited_loads(value, *args, **kwargs):
        if value == bad:
            raise RecursionError("decoder recursion limit")
        return original_loads(value, *args, **kwargs)
    monkeypatch.setattr(wrapper.json, "loads", limited_loads)
    run = run_result([], status="SUCCESS")
    run.stdout = bad + '\n' + run.stdout
    result = wrapper._interpret_run(run, None, read_only=True)
    assert (result.classification, result.exit_code) == ("admission-refused", 65)
    assert result.final_answer == "" and result.validated is None


def test_undecodable_progress_preserves_typed_terminal_timeout():
    run = network_run(error="timeout waiting for response")
    run.stdout = '{"event":"step_update",\n' + run.stdout
    result = wrapper._interpret_run(run, None, read_only=True)
    assert (result.classification, result.exit_code) == ("vendor-timeout", 65)
    assert result.final_answer == ""


@pytest.mark.parametrize("schema", [False, True])
@pytest.mark.parametrize("network_error", [False, True])
@pytest.mark.parametrize("record", [
    '{"event":"step_update","step_update":{"step_type":"tool","state":"DONE","tool_name":"manage_task","tool_name":"read_file"}}',
    '{"event":"step_update","step_update":{"step_type":"tool","state":"DONE","tool_info":{"name":"manage_task","name":"read_file"}}}',
    '{"event":"step_update","event":"ignored","step_update":{"step_type":"tool","state":"DONE","tool_name":"manage_task"}}',
], ids=["tool-name", "info-name", "event-kind"])
def test_ambiguous_tool_event_cannot_hide_task_attempt(record, network_error, schema, monkeypatch):
    monkeypatch.setattr(wrapper._common, "_load_classifier_extension", lambda: {})
    run = network_run() if network_error else network_run(status="SUCCESS", response="answer", rc=0)
    run.stdout = record + '\n' + run.stdout
    original = run.stdout
    cls = wrapper._common.load_pydantic_class("verdict_schema:LegVerdict") if schema else None
    result = wrapper._interpret_run(run, cls, read_only=True, plan_mode=schema)
    expected = ("schema-fail", 66) if schema else ("admission-refused", 65)
    assert (result.classification, result.exit_code) == expected
    assert result.final_answer == "" and result.validated is None
    assert result.stdout == original
    if schema:
        assert result.validation_error == "duplicate_member"
    permissive = network_run() if network_error else network_run(status="SUCCESS", response="answer", rc=0)
    permissive.stdout = original
    control = wrapper._interpret_run(permissive, None)
    assert control.exit_code == (64 if network_error else 0)


@pytest.mark.parametrize("clean_auth", [False, True])
def test_duplicate_event_cannot_fabricate_auth_priority(clean_auth, monkeypatch):
    monkeypatch.setattr(wrapper._common, "_load_classifier_extension", lambda: {})
    run = network_run(error="not logged in") if clean_auth else network_run()
    run.stdout = ('{"event":"step_update","event":"result","result":'
                  '{"status":"ERROR","response":"","error":"not logged in"}}\n') + run.stdout
    result = wrapper._interpret_run(run, None, read_only=True)
    assert (result.classification, result.exit_code) == (("oauth-env", 65) if clean_auth
                                                       else ("admission-refused", 65))
    assert result.final_answer == ""


@pytest.mark.parametrize("edge", ["\u00a0", "\u2003", " \t\r"], ids=["nbsp", "em-space", "json-space"])
@pytest.mark.parametrize("terminal", [False, True])
@pytest.mark.parametrize("read_only", [False, True])
def test_original_event_whitespace_is_not_normalized_before_read_only_admission(edge, terminal, read_only):
    event = '{"event":"result","result":{"status":"SUCCESS","response":"first"}}' if terminal else '{"event":"step_update","step_update":{}}'
    run = network_run(status="SUCCESS", response="done", rc=0)
    run.stdout = edge + event + edge + '\n' + run.stdout
    original = run.stdout
    result = wrapper._interpret_run(run, None, read_only=read_only)
    if read_only and edge != " \t\r":
        assert (result.classification, result.exit_code) == ("admission-refused", 65)
        assert result.final_answer == ""
    else:
        assert (result.classification, result.exit_code, result.final_answer) == ("ok", 0, "done")
    assert result.stdout == original


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity", "1e999"])
@pytest.mark.parametrize("read_only", [False, True])
def test_nonfinite_event_cannot_bypass_read_only_admission(constant, read_only):
    run = network_run(status="SUCCESS", response="done", rc=0)
    run.stdout = '{"event":"step_update","usage":' + constant + '}\n' + run.stdout
    result = wrapper._interpret_run(run, None, read_only=read_only)
    assert (result.classification, result.exit_code) == (("admission-refused", 65) if read_only else ("ok", 0))


@pytest.mark.parametrize("formal", [False, True])
def test_undecodable_record_without_terminal_is_refused(formal):
    run = network_run(rc=0)
    run.stdout = '{"event":"step_update",'
    result = wrapper._interpret_run(run, None, plan_mode=formal, read_only=not formal)
    assert (result.classification, result.exit_code) == ("admission-refused", 65)


def test_task_record_without_terminal_retains_extraction_failure():
    run = network_run(rc=0)
    run.stdout = json.dumps(step("manage_task"))
    result = wrapper._interpret_run(run, None, read_only=True)
    assert (result.classification, result.exit_code) == ("extraction-error", 1)


@pytest.mark.parametrize("earlier", [False, True])
def test_unmatched_or_earlier_denial_does_not_clear_active_task(earlier):
    active = step("manage_task", "ACTIVE", index=1)
    denial = step("manage_task", "ERROR", index=1 if earlier else 2,
                  error={"message": "tool call denied by pre-tool hook"})
    result = interpret(run_result([denial, active] if earlier else [active, denial], status="SUCCESS"))
    assert (result.classification, result.exit_code) == ("admission-refused", 65)


@pytest.mark.parametrize("record,error", [
    ('{"event":"step_update","event":"ignored"}', "duplicate_member"),
    ('{"event":"step_update","usage":NaN}', "nonfinite_number"),
    ('\u00a0{"event":"step_update"}', "invalid_json"),
])
def test_original_json_schema_error_precedes_separate_undecodable_record(record, error):
    run = run_result([], status="SUCCESS")
    run.stdout = '{invalid\n' + record + '\n' + run.stdout
    result = interpret(run)
    assert (result.classification, result.exit_code) == ("schema-fail", 66)
    assert result.validation_error == error and result.validated is None



@pytest.mark.parametrize('active_id,denial_id,allowed', [
    ('a', 'a', True), (None, None, True), ('a', 'b', False),
    ('a', None, False), (None, 'a', False), ('', '', False),
    (1, 1, False), ([], [], False), ({}, {}, False),
])
@pytest.mark.parametrize('boundary', [False, True])
def test_task_denial_requires_same_conversation_and_result_segment(active_id, denial_id, allowed, boundary):
    active = step('manage_task', 'ACTIVE', index=2)
    denial = step('manage_task', 'ERROR', index=2,
                  error={'message': 'tool call denied by pre-tool hook'})
    if active_id is not None:
        active['conversation_id'] = active_id
    if denial_id is not None:
        denial['conversation_id'] = denial_id
    events = [active]
    if boundary:
        events.append({'event': 'result', 'result': {'status': 'SUCCESS', 'response': 'first'}})
    events.append(denial)
    result = interpret(run_result(events, status='SUCCESS'))
    assert (result.classification, result.exit_code) == (('ok', 0) if allowed and not boundary else ('admission-refused', 65))
