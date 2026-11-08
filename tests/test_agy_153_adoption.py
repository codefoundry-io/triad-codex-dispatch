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


@pytest.mark.parametrize('name,alias,allowed', [
    ('manage_task', 'run_command', False), ('run_command', 'manage_task', False),
    ('manage_task', 'manage_task', True), ('manage_task', None, True),
    (None, 'manage_task', True), ('manage_task', [], False),
])
@pytest.mark.parametrize('active', [False, True])
def test_task_denial_requires_consistent_exposed_names(name, alias, allowed, active):
    denial = step(name, 'ERROR', index=2, alias=alias,
                  error={'message': 'tool call denied by pre-tool hook'})
    events = ([step('manage_task', 'ACTIVE', index=2)] if active else []) + [denial]
    result = interpret(run_result(events, status='SUCCESS'))
    assert (result.classification, result.exit_code) == (('ok', 0) if allowed else ('admission-refused', 65))


@pytest.mark.parametrize('body,expected', [
    ('"x":1,"x":2', 'duplicate_member'),
    ('"x":NaN', 'nonfinite_number'),
    ('"x":NaN,"x":2', 'duplicate_member'),
])
@pytest.mark.parametrize('schema', [False, True])
def test_original_json_diagnostics_survive_trailing_non_json_whitespace(body, expected, schema):
    run = run_result([], status='SUCCESS')
    run.stdout = '{"event":"step_update",' + body + '}\u00a0\n' + run.stdout
    cls = wrapper._common.load_pydantic_class('verdict_schema:LegVerdict') if schema else None
    result = wrapper._interpret_run(run, cls, read_only=True)
    assert (result.classification, result.exit_code) == (('schema-fail', 66) if schema else ('admission-refused', 65))
    if schema:
        assert result.validation_error == expected
    assert result.final_answer == '' and result.validated is None


@pytest.mark.parametrize('active_name,active_alias', [('manage_task', 'run_command'), ('run_command', 'manage_task')])
def test_ambiguous_active_names_cannot_borrow_consistent_denial(active_name, active_alias):
    events = [step(active_name, 'ACTIVE', index=2, alias=active_alias),
              step('manage_task', 'ERROR', index=2,
                   error={'message': 'tool call denied by pre-tool hook'})]
    result = interpret(run_result(events, status='SUCCESS'))
    assert (result.classification, result.exit_code) == ('admission-refused', 65)


@pytest.mark.parametrize('parameters,other_parameters,allowed', [
    ({'Action': 'create'}, {'Action': 'list'}, False),
    ({'Action': 'list'}, {'Action': 'list'}, True),
    ({'Action': 'list', 'count': 1}, {'count': True, 'Action': 'list'}, False),
    ({'Action': 'list', 'count': 1}, {'count': 1, 'Action': 'list'}, True),
    (None, {'Action': 'list'}, True), ({'Action': 'list'}, None, True), (None, None, True),
])
def test_task_denial_cannot_contradict_exposed_parameters(parameters, other_parameters, allowed):
    active = step('manage_task', 'ACTIVE', index=2)
    denial = step('manage_task', 'ERROR', index=2,
                  error={'message': 'tool call denied by pre-tool hook'})
    for event, value in ((active, parameters), (denial, other_parameters)):
        if value is not None:
            event['step_update'].setdefault('tool_info', {})['parameters'] = value
    result = interpret(run_result([active, denial], status='SUCCESS'))
    assert (result.classification, result.exit_code) == (('ok', 0) if allowed else ('admission-refused', 65))


@pytest.mark.parametrize('observations,allowed', [
    ([('ACTIVE', {'Action': 'create'}), ('ACTIVE', {'Action': 'list'}), ('ERROR', 'absent')], False),
    ([('ACTIVE', {'Action': 'create'}), ('ERROR', {'Action': 'list'}), ('ERROR', 'absent')], False),
    ([('ACTIVE', {'Action': 'list'}), ('ACTIVE', {'Action': 'list'}), ('ERROR', 'absent')], True),
    ([('ACTIVE', 'absent'), ('ACTIVE', {'Action': 'list'}), ('ERROR', 'absent')], True),
    ([('ACTIVE', {'count': 1}), ('ACTIVE', {'count': True}), ('ERROR', 'absent')], False),
    ([('ACTIVE', None), ('ACTIVE', {'Action': 'list'}), ('ERROR', 'absent')], False),
    ([('ACTIVE', {'a': 1, 'b': 2}), ('ACTIVE', {'b': 2, 'a': 1}), ('ERROR', 'absent')], True),
])
def test_task_denial_requires_consistent_group_parameters(observations, allowed):
    events = []
    for state, parameters in observations:
        event = step('manage_task', state, index=2,
                     error={'message': 'tool call denied by pre-tool hook'} if state == 'ERROR' else None)
        event['conversation_id'] = 'same'
        if parameters != 'absent':
            event['step_update'].setdefault('tool_info', {})['parameters'] = parameters
        events.append(event)
    result = interpret(run_result(events, status='SUCCESS'))
    assert (result.classification, result.exit_code) == (('ok', 0) if allowed else ('admission-refused', 65))
    if not allowed:
        assert result.final_answer == '' and result.validated is None


@pytest.mark.parametrize('separation', ['index', 'conversation', 'result'])
def test_separate_task_identity_parameter_groups_do_not_conflict(separation):
    events = []
    for group in (0, 1):
        if group and separation == 'result':
            events.append({'event': 'result', 'result': {'status': 'SUCCESS', 'response': 'first'}})
        for state in ('ACTIVE', 'ERROR'):
            event = step('manage_task', state, index=group if separation == 'index' else 2,
                         error={'message': 'tool call denied by pre-tool hook'} if state == 'ERROR' else None)
            event['conversation_id'] = str(group) if separation == 'conversation' else 'same'
            if state == 'ACTIVE':
                event['step_update'].setdefault('tool_info', {})['parameters'] = {'value': group}
            events.append(event)
    assert interpret(run_result(events, status='SUCCESS')).exit_code == 0


@pytest.mark.parametrize('message,allowed', [
    ('permission check failed for command "x": user denied permission', False),
    ('permission check failed for command "x": permission denied for command', False),
    ('tool call denied by pre-tool hook', True), ('user denied permission', True),
])
@pytest.mark.parametrize('active', [False, True])
@pytest.mark.parametrize('formal', [False, True])
def test_task_denial_does_not_borrow_command_permission_failure(message, allowed, active, formal):
    events = ([step('manage_task', 'ACTIVE', index=2)] if active else [])
    events.append(step('manage_task', 'ERROR', index=2, alias='manage_task', error={'message': message}))
    run = run_result(events, status='SUCCESS')
    result = (interpret(run) if formal else wrapper._interpret_run(run, None, read_only=True))
    assert (result.classification, result.exit_code) == (('ok', 0) if allowed else ('admission-refused', 65))
    permissive = wrapper._interpret_run(run_result(events, status='SUCCESS'), None)
    assert permissive.exit_code == 0


def raw_parameter_task(state, raw, *, index=2, usage=None):
    event = step('manage_task', state, index=index,
                 error={'message': 'tool call denied by pre-tool hook'} if state == 'ERROR' else None)
    event['step_update'].setdefault('tool_info', {})['parameters'] = '__RAW_PARAMETERS__'
    encoded = json.dumps(event).replace('"__RAW_PARAMETERS__"', raw)
    if usage is not None:
        encoded = encoded[:-1] + ',"usage":' + usage + '}'
    return encoded


@pytest.mark.parametrize('left,right,allowed', [
    ('{"count":9007199254740992.0}', '{"count":9007199254740993.0}', False),
    ('{"count":1e-400}', '{"count":2e-400}', False),
    ('{"count":1.0}', '{"count":1.00}', True),
    ('{"count":1.00}', '{"count":1e0}', True),
    ('{"count":0.0012300}', '{"count":123e-5}', True),
    ('{"a":[{"count":9007199254740992.0}]}', '{"a":[{"count":9007199254740993.0}]}', False),
    ('{"count":1.0,"x":[true,null]}', '{"x":[true,null],"count":1e0}', True),
    ('{"count":1.0}', '{"count":"1.0"}', False),
    ('{"count":1.0}', '{"count":["fractional","1.0"]}', False),
    ('{"count":1.0}', '{"count":{"decimal":"1.0"}}', False),
    ('{"count":1.0}', '{"count":1}', False),
    ('{"count":-0.0}', '{"count":0.0}', False),
])
@pytest.mark.parametrize('formal', [False, True])
def test_task_parameter_evidence_preserves_exact_original_numbers(left, right, allowed, formal):
    run = run_result([], status='SUCCESS')
    run.stdout = raw_parameter_task('ACTIVE', left) + '\n' + raw_parameter_task('ERROR', right) + '\n' + run.stdout
    original = run.stdout
    result = interpret(run) if formal else wrapper._interpret_run(run, None, read_only=True)
    assert (result.classification, result.exit_code) == (('ok', 0) if allowed else ('admission-refused', 65))
    assert result.stdout == original
    control = run_result([], status='SUCCESS')
    control.stdout = original
    assert wrapper._interpret_run(control, None).exit_code == 0


def test_parameterless_denial_cannot_hide_distinct_exact_number_observations():
    run = run_result([], status='SUCCESS')
    denial = json.dumps(step('manage_task', 'ERROR', index=2,
                             error={'message': 'tool call denied by pre-tool hook'}))
    run.stdout = '\n'.join([raw_parameter_task('ACTIVE', '{"count":1e-400}'),
                            raw_parameter_task('ACTIVE', '{"count":2e-400}'), denial, run.stdout])
    result = interpret(run)
    assert (result.classification, result.exit_code) == ('admission-refused', 65)


def test_unrelated_fractional_metadata_does_not_change_parameter_evidence():
    run = run_result([], status='SUCCESS')
    raw = '{"Action":"list"}'
    huge_underflow = '1e-' + '9' * 100
    run.stdout = '\n'.join([raw_parameter_task('ACTIVE', raw, usage=huge_underflow),
                            raw_parameter_task('ERROR', raw, usage=huge_underflow), run.stdout])
    assert interpret(run).exit_code == 0


@pytest.mark.parametrize('kind', [None, 'message'])
@pytest.mark.parametrize('state', ['ACTIVE', 'DONE', 'ERROR'])
def test_task_named_step_with_unknown_type_cannot_prove_containment(kind, state):
    event = step('manage_task', state, kind=kind, index=2,
                 error={'message': 'tool call denied by pre-tool hook'} if state == 'ERROR' else None)
    if kind is None:
        del event['step_update']['step_type']
    denial = step('manage_task', 'ERROR', index=2,
                  error={'message': 'tool call denied by pre-tool hook'})
    result = interpret(run_result([event, denial], status='SUCCESS'))
    assert (result.classification, result.exit_code) == ('admission-refused', 65)


def test_exact_parameter_side_evidence_does_not_change_returned_event_types():
    raw = raw_parameter_task('ACTIVE', '{"float":9007199254740993.0,"integer":1,"boolean":true}')
    signatures, errors = {}, []
    events, result = wrapper.parse_agy_stream(raw, decode_errors=errors, parameter_signatures=signatures)
    assert events == [json.loads(raw)] and result is None and errors == []
    params = events[0]['step_update']['tool_info']['parameters']
    assert type(params['float']) is float and type(params['integer']) is int and type(params['boolean']) is bool
    assert set(signatures) == {0}


@pytest.mark.parametrize('name,expected', [('manage_task', 65), ('read_file', 0)])
def test_unavailable_exact_parameter_signature_fails_closed_only_for_task_correlation(name, expected):
    raw = '{"count":1e-' + '9' * 5000 + '}'
    run = run_result([], status='SUCCESS')
    run.stdout = '\n'.join([raw_parameter_task('ACTIVE', raw).replace('manage_task', name),
                            raw_parameter_task('ERROR', raw).replace('manage_task', name), run.stdout])
    previous = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(4300)
        result = interpret(run)
    finally:
        sys.set_int_max_str_digits(previous)
    assert result.exit_code == expected


def test_exact_parameter_evidence_positions_follow_accepted_events():
    active = raw_parameter_task('ACTIVE', '{"count":1.00}')
    other = json.dumps(step('read_file'))
    denial = raw_parameter_task('ERROR', '{"count":1e0}')
    raw = '\n'.join(['banner', active, '{invalid', other, 'noise', denial])
    signatures, errors = {}, []
    events, _ = wrapper.parse_agy_stream(raw, decode_errors=errors, parameter_signatures=signatures)
    assert len(events) == 3 and errors == ['undecodable AGY event']
    assert set(signatures) == {0, 2} and signatures[0] == signatures[2]
    assert events[1]['step_update']['tool_name'] == 'read_file'
