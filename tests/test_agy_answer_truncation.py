"""C43/DL-102 constructed selected-answer cases, not fresh vendor captures."""
import json
import sys
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
import _common
import antigravity_wrapper as wrapper
import apply_patch as applier


class Answer(BaseModel):
    model_config = ConfigDict(extra='forbid')
    ok: bool


def make_run(response, *, structured=None, events=(), rc=0, status='SUCCESS'):
    result = {'status': status, 'response': response}
    if structured is not None:
        result['structured_output'] = structured
    stream = [*events, {'event': 'result', 'result': result}]
    return _common.RunResult(0 if rc == 0 else 1,
        '\n'.join(json.dumps(event) for event in stream), '', 0.1,
        classification='unclassified', vendor_exit_code=rc)


@pytest.mark.parametrize('response', [
    'start\n<truncated 123 bytes>\nend', '<truncated 2 lines>',
    'start\n \t<truncated 12 lines>\t \nend',
    'start\r\n<truncated 123 bytes>\r\nend',
    'start\r\n<truncated 12 lines>\r\nend',
])
def test_C43_raw_own_line_marker_withholds_answer_and_keeps_evidence(response):
    run = make_run(response)
    original = run.stdout
    result = wrapper._interpret_run(run, None)
    assert (result.classification, result.exit_code) == ('truncated-answer', 65)
    assert result.final_answer == '' and result.validated is None
    assert result.stdout == original and result.vendor_exit_code == 0
    assert result.dispatch_phase == 'post-dispatch-result'


@pytest.mark.parametrize('response', [
    'The marker is <truncated 123 bytes> in this example.',
    'prefix <truncated 2 lines>\nend', '<truncated 2 lines> suffix',
    '<truncated many bytes>', '<truncated 2 tokens>', 'x' * 30000,
])
def test_C43_inline_near_miss_and_large_intact_answers_are_usable(response):
    result = wrapper._interpret_run(make_run(response), None)
    assert (result.classification, result.exit_code) == ('ok', 0)
    assert result.final_answer == response


@pytest.mark.parametrize('tool', ['view_file', 'search_web'])
def test_C43_tool_output_marker_does_not_discard_intact_answer(tool):
    event = {'event': 'step_update', 'step_update': {
        'step_type': 'tool', 'tool_name': tool, 'state': 'DONE', 'text_delta': '<truncated 99 bytes>'}}
    result = wrapper._interpret_run(make_run('complete', events=[event]), None,
                                    web=tool == 'search_web')
    assert (result.classification, result.exit_code, result.final_answer) == ('ok', 0, 'complete')


@pytest.mark.parametrize('plan_mode', [False, True])
def test_C43_incidental_response_marker_does_not_discard_valid_schema_answer(plan_mode):
    result = wrapper._interpret_run(make_run('<truncated 99 lines>', structured={'ok': True}),
                                    Answer, plan_mode=plan_mode)
    assert (result.classification, result.exit_code) == ('ok', 0)
    assert json.loads(result.final_answer) == {'ok': True}
    assert result.validated == {'ok': True}


@pytest.mark.parametrize('structured', [None, {'wrong': True}, {'ok': True}])
def test_C43_marker_never_bypasses_schema_or_binding_checks(structured):
    result = wrapper._interpret_run(make_run('<truncated 99 lines>', structured=structured),
                                    Answer, expected_review_id='required-binding')
    assert (result.classification, result.exit_code) == ('schema-fail', 66)
    assert result.final_answer == ''


@pytest.mark.parametrize('priority', ['auth', 'timeout', 'stdin', 'nonzero', 'status', 'route'])
def test_C43_existing_failure_priority_precedes_raw_marker(monkeypatch, priority):
    monkeypatch.setattr(_common, '_load_classifier_extension', lambda: {})
    run = make_run('<truncated 99 bytes>', rc=1 if priority in ('auth', 'nonzero') else 0,
                   status='ERROR' if priority == 'status' else 'SUCCESS')
    kwargs = {}
    if priority == 'auth':
        run.stderr = 'Authentication required. Please visit the URL to log in:'
        expected = ('oauth-env', 65)
    elif priority == 'timeout':
        run.exit_code = 2
        expected = ('timeout', 2)
    elif priority == 'stdin':
        run._stdin_delivery_failed = True
        run.classification, run.exit_code = expected = ('input-delivery-failed', 65)
    elif priority == 'nonzero':
        expected = ('unknown', 1)
    elif priority == 'status':
        expected = ('vendor-error', 65)
    else:
        run.stdout = json.dumps({'event': 'init', 'init': {'model': 'different'}}) + '\n' + run.stdout
        kwargs['expected_model'] = 'requested'
        expected = ('route-mismatch', 65)
    result = wrapper._interpret_run(run, None, **kwargs)
    assert (result.classification, result.exit_code) == expected
    assert result.final_answer == ''


@pytest.mark.parametrize('response', [
    '<truncated 99 bytes>', 'start\r\n<truncated 123 bytes>\r\nend',
    'start\r\n<truncated 12 lines>\r\nend',
])
def test_C43_stored_raw_result_uses_same_selected_channel_rule(response):
    run = make_run(response)
    record = {'cli': 'antigravity', 'classification': 'unknown', 'exit_code': 1,
              'vendor_exit_code': 0, 'stdout': run.stdout, 'stderr': '',
              'transport': {'stdin_delivery': 'complete'}}
    assert applier._stored_failure_classification('antigravity', record) == 'truncated-answer'
