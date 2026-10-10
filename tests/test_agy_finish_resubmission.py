"""C23/DL-113 constructed stream cases, not vendor captures.

Catch lost same-run recovery, false admission, and bypassed verdict guards.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
import _common
import antigravity_wrapper as wrapper
from verdict_schema import LegVerdict


def step(name=None, state='DONE', *, kind='tool', index=1, error=None, alias=None):
    value = {'step_type': kind, 'state': state, 'step_index': index}
    if name is not None:
        value['tool_name'] = name
    info = {}
    if alias is not None:
        info['name'] = alias
    if error is not None:
        info['error'] = error
    if info:
        value['tool_info'] = info
    return {'event': 'step_update', 'step_update': value}


def payload():
    return {'review_id': 'resubmit-r1', 'family': 'google', 'content_digest': 'a' * 64,
            'verdict': 'SAFE', 'criteria_checked': ['correctness'], 'findings': [],
            'affected_surfaces_inspected': ['src/example.py'], 'open_questions': []}


def failed_finish():
    return step('finish', 'ERROR', index=2, error={'type': 'TOOL_ERROR', 'message': 'schema rejected'})


def finished():
    return step(kind='finish', index=3)


def recovery_steps():
    return [step('view_file'), failed_finish(), finished()]


def run_result(events=None, *, status='ERROR', rc=0, answer=None, error='finish failed'):
    items = recovery_steps() if events is None else events
    terminal = {'event': 'result', 'result': {'status': status, 'error': error,
                'response': 'final review', 'structured_output': payload() if answer is None else answer}}
    return _common.RunResult(exit_code=0 if rc == 0 else 1,
        stdout='\n'.join(json.dumps(x) for x in [*items, terminal]), stderr='',
        elapsed_s=0.1, classification='unclassified', vendor_exit_code=rc)


def interpret(run, **kwargs):
    return wrapper._interpret_run(run, LegVerdict,
        expected_review_id='resubmit-r1', expected_family='google',
        expected_content_digest='a' * 64, plan_mode=True, **kwargs)


@pytest.fixture(autouse=True)
def isolate_extension(monkeypatch, tmp_path):
    monkeypatch.setattr(_common, '_classifier_extension_path', lambda: tmp_path / 'absent.json')


@pytest.mark.parametrize('read', ['view_file', 'grep_search', 'list_dir', 'find_by_name'])
def test_c23_later_finish_recovers_final_validated_answer(read):
    run = run_result([step(read), failed_finish(), finished()])
    original = run.stdout
    result = interpret(run)
    assert (result.classification, result.exit_code) == ('ok', 0)
    assert json.loads(result.final_answer) == payload() == result.validated
    assert result.stdout == original and result.vendor_exit_code == 0


@pytest.mark.parametrize('events', [
    [step('view_file'), failed_finish()],
    [step('view_file'), finished(), failed_finish()],
    [step('view_file'), failed_finish(), step('finish')],
    [step('view_file'), failed_finish(), step(kind='finish', state='ACTIVE')],
    [step('view_file'), failed_finish(), step(kind='finish', error={'message': 'bad'})],
    [failed_finish(), finished()],
    [step('view_file', 'ERROR', error={'message': 'missing'}), failed_finish(), finished()],
    [step('view_file'), finished()],
    [step('view_file'), failed_finish(), finished(), step('finish', 'ERROR', index=4)],
])
def test_missing_later_success_or_successful_read_refuses(events):
    result = interpret(run_result(events))
    assert (result.classification, result.exit_code) == ('vendor-error', 65)
    assert result.final_answer == ''


@pytest.mark.parametrize('extra', [
    step('run_command'),
    step('manage_task', 'ERROR', error={'type': 'TOOL_ERROR', 'message': 'argument rejected'}),
    step('view_file', alias='run_command'),
    step(),
    step('run_command', 'DONE', error={'message': 'user denied permission'}),
    step('run_command', 'ERROR', error={'message': 'quoted: user denied permission'}),
    step('run_command', 'ERROR', error={'type': 'TOOL_ERROR'}),
    step('run_command', 'ERROR', error='user denied permission'),
])
def test_other_executed_or_unknown_error_does_not_get_hidden(extra):
    result = interpret(run_result([*recovery_steps(), extra]))
    assert (result.classification, result.exit_code) == ('vendor-error', 65)
    assert result.final_answer == ''


@pytest.mark.parametrize('message', [
    'Tool call denied by pre-tool hook: forbidden',
    '\n  USER DENIED PERMISSION for run_command',
    'permission check failed for command "x": user denied permission',
    'permission check failed for command "x": permission denied for command',
])
def test_denied_before_execution_is_not_executed_work(message):
    denied = step('run_command', 'ERROR', index=4,
                  error={'type': 'TOOL_ERROR', 'message': message})
    result = interpret(run_result([step('run_command', 'ACTIVE', index=4), denied, *recovery_steps()]))
    assert (result.classification, result.exit_code) == ('ok', 0)


@pytest.mark.parametrize('index', [None, True, '4', 5])
def test_unmatched_or_untrusted_active_identity_cannot_be_hidden(index):
    denied = step('run_command', 'ERROR', index=4, error={'message': 'user denied permission'})
    result = interpret(run_result([step('run_command', 'ACTIVE', index=index), denied, *recovery_steps()]))
    assert (result.classification, result.exit_code) == ('vendor-error', 65)


def test_allowed_read_error_can_precede_a_real_read_and_resubmission():
    result = interpret(run_result([step('view_file', 'ERROR', index=0,
        error={'message': 'no such file'}), *recovery_steps()]))
    assert (result.classification, result.exit_code) == ('ok', 0)


@pytest.mark.parametrize('change', ['schema', 'binding', 'model', 'auth', 'timeout', 'stdin', 'output', 'nonzero'])
def test_recovery_preserves_existing_validation_and_failure_priority(change):
    run = run_result(); kwargs = {}
    if change in ('schema', 'binding'):
        bad = payload(); bad['family'] = 'claude' if change == 'binding' else 'invalid'
        run = run_result(answer=bad); expected = ('schema-fail', 66)
    elif change == 'model':
        run.stdout = json.dumps({'event': 'init', 'init': {'model': 'different'}}) + '\n' + run.stdout
        kwargs['expected_model'] = 'requested'; expected = ('route-mismatch', 65)
    elif change == 'auth':
        run.stderr = 'Authentication required. Please visit the URL to log in:'
        expected = ('oauth-env', 65)
    elif change == 'timeout':
        run.exit_code = 2; expected = ('timeout', 2)
    elif change in ('stdin', 'output'):
        setattr(run, '_stdin_delivery_failed' if change == 'stdin' else '_output_transport_failed', True)
        run.classification, run.exit_code = ('input-delivery-failed', 65) if change == 'stdin' else ('unknown', 1)
        expected = (run.classification, run.exit_code)
    else:
        run = run_result(rc=1); expected = ('unknown', 1)
    result = interpret(run, **kwargs)
    assert (result.classification, result.exit_code) == expected
    assert result.final_answer == ''


def test_success_and_existing_post_completion_denial_are_unchanged():
    assert interpret(run_result([], status='SUCCESS')).exit_code == 0
    assert interpret(run_result([], error='permission check failed for command "x"')).exit_code == 0
    assert wrapper._interpret_run(run_result(), LegVerdict, plan_mode=False).exit_code == 65


def test_resubmission_does_not_borrow_finish_from_another_terminal_result():
    run = run_result()
    run.stdout += '\n' + json.dumps({'event': 'result', 'result': {
        'status': 'ERROR', 'structured_output': payload(), 'response': 'unrelated'}})
    result = interpret(run)
    assert (result.classification, result.exit_code) == ('vendor-error', 65)


from test_v2_google_wrappers import route, ready
from test_v2_producer_adapter import verdict as v2_verdict


@pytest.mark.parametrize('route', ['agy'], indirect=True)
@pytest.mark.parametrize('web', [False, True])
def test_main_uses_bound_web_profile_for_recovery(route, web, monkeypatch):
    options, _ = ready(route, web=web)
    answer = v2_verdict(route='agy', leg_name='google-second')
    def provider(*args, **kwargs):
        return run_result([step('read_url_content'), failed_finish(), finished()], answer=answer)
    monkeypatch.setattr(_common, '_run_once', provider)
    rc, output, error = route['invoke'](base=options)
    assert rc == (0 if web else 65), error
    if web:
        assert json.loads(output) == answer
    else:
        assert output == ''
