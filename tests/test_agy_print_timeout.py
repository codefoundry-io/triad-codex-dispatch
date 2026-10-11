"""C43/DL-62 measured print-timeout carrier, replayed without vendor inference."""
import json
import sys
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
import _common
import antigravity_wrapper as wrapper
import apply_patch as applier

LINE = '[agy] print timeout after 19m50s with turn in progress; returning partial output'
AUTH = 'Authentication required. Please visit the URL to log in:'


class Answer(BaseModel):
    model_config = ConfigDict(extra='forbid')
    ok: bool


@pytest.fixture(autouse=True)
def isolate_extension(monkeypatch, tmp_path):
    monkeypatch.setattr(_common, '_classifier_extension_path', lambda: tmp_path / 'absent.json')


def make_run(*, schema=False, rc=0, stderr=LINE, missing=False, response='partial answer', error=None):
    result = {'status': 'SUCCESS', 'response': response}
    if schema:
        result['structured_output'] = {'ok': True}
    if error is not None:
        result['error'] = error
    stdout = '' if missing else json.dumps({'event': 'result', 'result': result})
    return _common.RunResult(0 if rc == 0 else 1, stdout, stderr, 0.1,
                             classification='unclassified', vendor_exit_code=rc)


@pytest.mark.parametrize('schema', [False, True])
@pytest.mark.parametrize('rc', [0, 1, 3])
@pytest.mark.parametrize('stderr', [LINE, 'diagnostic\n' + LINE + '\n', LINE + '\r\n'])
def test_C43_print_timeout_withholds_partial_answer_at_any_exit(schema, rc, stderr):
    run = make_run(schema=schema, rc=rc, stderr=stderr)
    original = (run.stdout, run.stderr, run.vendor_exit_code)
    result = wrapper._interpret_run(run, Answer if schema else None)
    assert (result.classification, result.exit_code) == ('timeout', 2)
    assert result.final_answer == '' and result.validated is None
    assert (result.stdout, result.stderr, result.vendor_exit_code) == original
    assert result.dispatch_phase == 'post-dispatch-result'


@pytest.mark.parametrize('rc', [0, 1])
@pytest.mark.parametrize('missing', [False, True])
def test_C43_print_timeout_without_answer_precedes_extraction(rc, missing):
    result = wrapper._interpret_run(make_run(rc=rc, response='', missing=missing), None)
    assert (result.classification, result.exit_code, result.final_answer) == ('timeout', 2, '')


@pytest.mark.parametrize('stderr', [
    'example: ' + LINE, '"' + LINE + '"', LINE + ' extra text',
    LINE.replace('[agy]', '[other]'), LINE.replace('print timeout', 'print timeouts'),
    'with turn in progress; returning partial output', '',
])
def test_C43_near_matches_keep_a_complete_answer(stderr):
    result = wrapper._interpret_run(make_run(stderr=stderr, response='complete answer'), None)
    assert (result.classification, result.exit_code, result.final_answer) == ('ok', 0, 'complete answer')


@pytest.mark.parametrize('carrier', ['response', 'result-error', 'tool'])
def test_C43_line_outside_stderr_does_not_trigger_print_timeout(carrier):
    run = make_run(stderr='', response=LINE if carrier == 'response' else 'complete')
    if carrier == 'result-error':
        run = make_run(stderr='', response='complete', error=LINE)
    elif carrier == 'tool':
        run.stdout = json.dumps({'event': 'step_update', 'step_update': {
            'step_type': 'tool', 'state': 'DONE', 'text_delta': LINE}}) + '\n' + run.stdout
    result = wrapper._interpret_run(run, None)
    assert (result.classification, result.exit_code) == ('ok', 0)
    assert result.final_answer == (LINE if carrier == 'response' else 'complete')


@pytest.mark.parametrize('schema', [False, True])
@pytest.mark.parametrize('carrier', ['stderr', 'result-error'])
def test_C43_authentication_stop_is_not_hidden_by_partial_success(schema, carrier):
    run = make_run(schema=schema, stderr=(AUTH + '\n' + LINE) if carrier == 'stderr' else LINE,
                   error=AUTH if carrier == 'result-error' else None)
    result = wrapper._interpret_run(run, Answer if schema else None)
    assert (result.classification, result.exit_code, result.final_answer) == ('oauth-env', 65, '')
    assert result.validated is None


@pytest.mark.parametrize('schema', [False, True])
def test_C43_completed_answer_still_ignores_incidental_sign_in_banner(schema):
    result = wrapper._interpret_run(make_run(schema=schema, stderr=AUTH, response='complete'),
                                    Answer if schema else None)
    assert (result.classification, result.exit_code) == ('ok', 0)
    assert result.validated == ({'ok': True} if schema else None)


@pytest.mark.parametrize('priority', ['outer-timeout', 'stdin', 'output'])
def test_C43_existing_transport_and_timeout_decisions_survive(priority):
    run = make_run()
    if priority == 'outer-timeout':
        run.exit_code = 2
        expected = ('timeout', 2)
    else:
        setattr(run, '_stdin_delivery_failed' if priority == 'stdin' else '_output_transport_failed', True)
        run.classification, run.exit_code = expected = (
            ('input-delivery-failed', 65) if priority == 'stdin' else ('unknown', 1))
    result = wrapper._interpret_run(run, None)
    assert (result.classification, result.exit_code) == expected
    assert result.final_answer == ''


def test_C43_stored_repair_eligible_failure_uses_the_same_interpreter():
    run = make_run()
    record = {'cli': 'antigravity', 'classification': 'unknown', 'exit_code': 1,
              'vendor_exit_code': 0, 'stdout': run.stdout, 'stderr': run.stderr,
              'transport': {'stdin_delivery': 'complete'}}
    assert applier._stored_failure_classification('antigravity', record) == 'timeout'
