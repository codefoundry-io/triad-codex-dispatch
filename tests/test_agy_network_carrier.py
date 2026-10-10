"""C43/DL-101 constructed cases for the recorded AGY network-error carrier."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
import _common
import antigravity_wrapper as wrapper
import apply_patch as applier

PHRASE = 'There was a network issue connecting to the server, please try again.'


@pytest.fixture(autouse=True)
def no_extension(monkeypatch):
    monkeypatch.setattr(_common, '_load_classifier_extension', lambda: {})


def make_run(*, error=PHRASE, status='ERROR', response='', rc=1, stderr='', events=()):
    stream = [*events, {'event': 'result', 'result': {
        'status': status, 'error': error, 'response': response}}]
    return _common.RunResult(0 if rc == 0 else 1,
        '\n'.join(json.dumps(event) for event in stream), stderr, 0.1,
        classification='unclassified', vendor_exit_code=rc)


@pytest.mark.parametrize('plan_mode', [False, True])
def test_C43_network_row_reaches_capacity_without_losing_raw_evidence(plan_mode):
    run = make_run()
    original = run.stdout
    result = wrapper._interpret_run(run, None, plan_mode=plan_mode)
    assert (result.classification, result.exit_code) == ('server-capacity', 64)
    assert result.final_answer == ''
    assert result.stdout == original and result.vendor_exit_code == 1
    assert PHRASE in result.extraction_error
    assert result.dispatch_phase == 'post-dispatch-result'


@pytest.mark.parametrize('change', [
    {'error': {'message': PHRASE}}, {'error': None}, {'error': [PHRASE]},
    {'status': 'SUCCESS'}, {'response': 'nonempty'}, {'response': None},
    {'rc': 0}, {'rc': 2},
    {'error': 'Your AI credits balance is too low to continue.'},
])
def test_C43_unmeasured_carriers_keep_existing_behavior(change):
    result = wrapper._interpret_run(make_run(**change), None)
    expected = ('vendor-error', 65) if change == {'rc': 0} else ('unknown', 1)
    assert (result.classification, result.exit_code) == expected
    assert result.final_answer == ''


@pytest.mark.parametrize('carrier', ['stderr', 'tool', 'answer'])
def test_C43_network_sentence_is_not_a_whole_stream_pattern(carrier):
    args = {'error': 'another error'}
    if carrier == 'stderr':
        args['stderr'] = PHRASE
    elif carrier == 'tool':
        args['events'] = [{'event': 'step_update', 'step_update': {
            'state': 'ERROR', 'step_type': 'tool', 'text_delta': PHRASE}}]
    else:
        args.update(status='SUCCESS', response=PHRASE, rc=0)
    result = wrapper._interpret_run(make_run(**args), None)
    assert (result.classification, result.exit_code) == (('ok', 0) if carrier == 'answer' else ('unknown', 1))
    assert result.final_answer == (PHRASE if carrier == 'answer' else '')


@pytest.mark.parametrize('cli', ['claude', 'gemini', 'codex'])
def test_C43_other_cli_does_not_gain_agy_match(cli):
    assert _common.classify(cli, PHRASE, '', 1, vendor_exit_code=1) == 'unknown'


@pytest.mark.parametrize('priority', ['auth', 'timeout', 'stdin', 'output', 'vendor-map', 'quota'])
def test_C43_earlier_decisions_remain_authoritative(monkeypatch, priority):
    run = make_run()
    if priority == 'auth':
        run.stderr = 'Authentication required. Please visit the URL to log in:'
        expected = ('oauth-env', 65)
    elif priority == 'timeout':
        run.exit_code = 2
        expected = ('timeout', 2)
    elif priority in ('stdin', 'output'):
        setattr(run, '_stdin_delivery_failed' if priority == 'stdin' else '_output_transport_failed', True)
        run.classification = 'input-delivery-failed' if priority == 'stdin' else 'unknown'
        run.exit_code = 65 if priority == 'stdin' else 1
        expected = (run.classification, run.exit_code)
    elif priority == 'vendor-map':
        monkeypatch.setattr(_common, '_load_classifier_extension', lambda: {
            'antigravity': {'vendor_exit_map': {'1': 'token-limit'}}})
        expected = ('token-limit', 65)
    else:
        run.stderr = 'Your AI credits balance is too low to continue.'
        expected = ('cli-subscription-cap', 65)
    result = wrapper._interpret_run(run, None)
    assert (result.classification, result.exit_code) == expected
    assert result.final_answer == ''


def test_C43_stored_failure_uses_the_same_typed_carrier():
    run = make_run()
    record = {'cli': 'antigravity', 'classification': 'unknown', 'exit_code': 1,
              'vendor_exit_code': 1, 'stdout': run.stdout, 'stderr': run.stderr,
              'transport': {'stdin_delivery': 'complete'}}
    assert applier._stored_failure_classification('antigravity', record) == 'server-capacity'
