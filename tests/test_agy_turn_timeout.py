"""C43/DL-102 constructed carrier cases, not new vendor captures.

Catch missing terminal-error admission, broad phrase scans, and lost priority.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
import _common
import antigravity_wrapper as wrapper

PHRASE = 'timeout waiting for response'


@pytest.fixture(autouse=True)
def isolate_extension(monkeypatch, tmp_path):
    monkeypatch.setattr(_common, '_classifier_extension_path', lambda: tmp_path / 'absent.json')


def run_result(*, error=PHRASE, status='ERROR', response='', rc=1, stderr='', events=()):
    stream = [*events, {'event': 'result', 'result': {
        'status': status, 'error': error, 'response': response,
    }}]
    return _common.RunResult(exit_code=0 if rc == 0 else 1,
        stdout='\n'.join(json.dumps(event) for event in stream), stderr=stderr,
        elapsed_s=0.1, classification='unclassified', vendor_exit_code=rc)


@pytest.mark.parametrize('suffix', ['', ': turn deadline reached'])
@pytest.mark.parametrize('plan_mode', [False, True])
def test_terminal_turn_timeout_returns_existing_terminal_token(suffix, plan_mode):
    run = run_result(error=PHRASE + suffix)
    original = run.stdout
    result = wrapper._interpret_run(run, None, plan_mode=plan_mode)
    assert (result.classification, result.exit_code) == ('vendor-timeout', 65)
    assert result.final_answer == ''
    assert result.stdout == original and result.vendor_exit_code == 1
    assert PHRASE in result.extraction_error
    assert result.dispatch_phase == 'post-dispatch-result'


@pytest.mark.parametrize('change', [
    {'error': 'schema rejected quoted text: ' + PHRASE},
    {'error': {'message': PHRASE}},
    {'error': None},
    {'error': 'timeout waiting for responses'},
    {'status': 'SUCCESS'},
    {'response': 'usable answer quoting ' + PHRASE},
    {'rc': 0},
    {'rc': 2},
])
def test_unobserved_combinations_keep_existing_classification(change):
    result = wrapper._interpret_run(run_result(**change), None)
    expected = ('vendor-error', 65) if change == {'rc': 0} else ('unknown', 1)
    assert (result.classification, result.exit_code) == expected
    assert result.final_answer == ''


@pytest.mark.parametrize('carrier', ['stderr', 'tool', 'answer'])
def test_phrase_outside_terminal_error_does_not_classify_turn_timeout(carrier):
    kwargs = {'error': 'another failure'}
    if carrier == 'stderr':
        kwargs['stderr'] = PHRASE
    elif carrier == 'tool':
        kwargs['events'] = [{'event': 'step_update', 'step_update': {
            'step_type': 'tool', 'state': 'ERROR', 'tool_info': {'error': {'message': PHRASE}},
        }}]
    else:
        kwargs.update(status='SUCCESS', response=PHRASE, rc=0)
    result = wrapper._interpret_run(run_result(**kwargs), None)
    assert (result.classification, result.exit_code) == (('ok', 0) if carrier == 'answer' else ('unknown', 1))
    assert result.final_answer == (PHRASE if carrier == 'answer' else '')


@pytest.mark.parametrize('priority', ['auth', 'timeout', 'stdin', 'output'])
def test_existing_terminal_priorities_survive(priority):
    run = run_result()
    if priority == 'auth':
        run.stderr = 'Authentication required. Please visit the URL to log in:'
        expected = ('oauth-env', 65)
    elif priority == 'timeout':
        run.exit_code = _common.EXIT_TIMEOUT
        expected = ('timeout', 2)
    else:
        setattr(run, '_stdin_delivery_failed' if priority == 'stdin' else '_output_transport_failed', True)
        run.classification = 'input-delivery-failed' if priority == 'stdin' else 'unknown'
        run.exit_code = 65 if priority == 'stdin' else 1
        expected = (run.classification, run.exit_code)
    result = wrapper._interpret_run(run, None)
    assert (result.classification, result.exit_code) == expected
    assert result.final_answer == ''
