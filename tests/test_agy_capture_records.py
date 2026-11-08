"""Original AGY records survive the local byte capture boundary."""
import json
import signal
import sys
from pathlib import Path

import pytest
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
import _common
import antigravity_wrapper as wrapper


class Answer(BaseModel):
    ok: bool


SUCCESS = json.dumps({'event': 'result', 'result': {
    'status': 'SUCCESS', 'response': 'done', 'structured_output': {'ok': True}}}).encode()
AUTH = json.dumps({'event': 'result', 'result': {'status': 'ERROR', 'error': 'not logged in'}}).encode()


def capture(tmp_path, data, *, timeout=False, stderr=b'', cli='antigravity', rc=0):
    code = f'import os,time; os.write(1,{data!r}); os.write(2,{stderr!r})'
    if timeout:
        code += '; time.sleep(30)'
    code += f'; raise SystemExit({rc})'
    return _common._run_once(cli, [sys.executable, '-c', code], str(tmp_path),
                             1 if timeout else 5, classify_and_log=False)


@pytest.mark.parametrize('mode', ['permissive', 'readonly', 'schema'])
@pytest.mark.parametrize('suffix', [b'\rgarbage\n', b'\r\n', b'\n', b''])
def test_capture_preserves_original_success_records(tmp_path, mode, suffix):
    data = SUCCESS + suffix
    run = capture(tmp_path, data)
    assert run.stdout == data.decode()
    result = wrapper._interpret_run(run, Answer if mode == 'schema' else None,
                                    read_only=mode != 'permissive')
    if suffix == b'\rgarbage\n' and mode != 'permissive':
        assert result.exit_code != 0 and result.final_answer == '' and result.validated is None
    else:
        assert result.exit_code == 0


@pytest.mark.parametrize('tail', [b'\rgarbage\n', b'\xff', b'\r\xff'])
@pytest.mark.parametrize('timeout', [False, True])
@pytest.mark.parametrize('independent_auth', [False, True])
def test_capture_does_not_manufacture_auth(tmp_path, tail, timeout, independent_auth):
    data = (AUTH + b'\n' if independent_auth else b'') + AUTH + tail
    run = capture(tmp_path, data, timeout=timeout)
    result = wrapper._interpret_run(run, None, read_only=True)
    if independent_auth:
        assert (result.classification, result.exit_code) == ('oauth-env', 65)
    else:
        assert result.classification != 'oauth-env'
        assert result.exit_code == (2 if timeout else (1 if b'\xff' in tail else 65))
    assert result.final_answer == ''


@pytest.mark.parametrize('tail', [b'\rgarbage\n', b'\xff'])
def test_signal_cannot_promote_a_corrupted_auth_record(tmp_path, tail):
    run = capture(tmp_path, AUTH + tail)
    _common._mark_signal_failure(run, signal.SIGTERM, 'antigravity')
    assert (run.classification, run.exit_code) == ('unknown', 1)


@pytest.mark.parametrize('ending', [b'', b'\n', b'\r\n'])
def test_clean_auth_records_still_override_timeout(tmp_path, ending):
    result = capture(tmp_path, AUTH + ending, timeout=True)
    assert (result.classification, result.exit_code) == ('oauth-env', 65)


@pytest.mark.parametrize('mode', ['permissive', 'readonly', 'schema'])
def test_permissive_completed_answer_still_vetoes_banner(tmp_path, mode):
    run = capture(tmp_path, SUCCESS + b'\rnoise\n', stderr=b'Authentication required. Please visit the URL to log in:\n')
    result = wrapper._interpret_run(run, Answer if mode == 'schema' else None, read_only=mode != 'permissive')
    assert result.classification != 'oauth-env'
    assert result.exit_code == (0 if mode == 'permissive' else 65)


@pytest.mark.parametrize('cli', ['claude', 'gemini', 'codex'])
def test_other_providers_keep_newline_normalization(tmp_path, cli):
    assert capture(tmp_path, b'a\rb\r\nc\n', cli=cli).stdout == 'a\nb\nc\n'


def test_saved_run_retains_original_records_for_replay(tmp_path, monkeypatch):
    import apply_patch
    monkeypatch.setattr(_common, '_LOG_DIR', tmp_path / 'logs')
    monkeypatch.setattr(_common, '_LOG_DIR_CONFIGURED', True)
    monkeypatch.setattr(_common, '_load_classifier_extension', lambda: {})
    raw = AUTH + b'\rgarbage\n'
    run = capture(tmp_path, raw)
    # Permissive replay may decode legacy records but cannot manufacture
    # positive auth from their malformed original framing.
    run = wrapper._interpret_run(run, None)
    assert run.classification == 'vendor-error'
    path = _common.emit_run_log('antigravity', ['fixture'], ['fixture'], 'fixture', run)
    assert path is not None and path.is_relative_to(tmp_path / 'logs')
    record = json.loads(path.read_text())
    assert record['stdout'] == raw.decode()
    # Repair eligibility is separate; exercise its reclassification with the
    # same original evidence, as for a previously unknown provider failure.
    record.update(classification='unknown', exit_code=1, vendor_exit_code=1)
    assert apply_patch._stored_failure_classification('antigravity', record) != 'oauth-env'


@pytest.mark.parametrize('first_status', ['ERROR', 'SUCCESS', None])
@pytest.mark.parametrize('ending', [b'\rgarbage\n', b'\r\n'])
def test_schema_status_and_payload_use_same_original_record(tmp_path, first_status, ending):
    first = b'' if first_status is None else json.dumps({'event': 'result', 'result': {
        'status': first_status, 'response': 'first', 'structured_output': {'ok': False}}}).encode() + b'\n'
    result = wrapper._interpret_run(capture(tmp_path, first + SUCCESS + ending), Answer)
    if ending == b'\r\n':
        assert result.exit_code == 0 and result.validated == {'ok': True}
    elif first_status == 'SUCCESS':
        assert result.exit_code == 0 and result.validated == {'ok': False}
    else:
        assert result.exit_code != 0 and result.validated is None and result.final_answer == ''


@pytest.mark.parametrize('mode', ['permissive', 'readonly', 'schema'])
@pytest.mark.parametrize('tail', [b'\n', b'\rgarbage\n'])
@pytest.mark.parametrize('real_banner', [False, True])
def test_status_diagnostic_is_not_an_authentication_carrier(tmp_path, mode, tail, real_banner):
    banner = 'Authentication required. Please visit the URL to log in:'
    raw = json.dumps({'event': 'result', 'result': {'status': 'ERROR\n' + banner}}).encode() + tail
    run = capture(tmp_path, raw, stderr=banner.encode() if real_banner else b'', rc=1)
    result = wrapper._interpret_run(run, Answer if mode == 'schema' else None,
                                    read_only=mode == 'readonly')
    if real_banner:
        assert (result.classification, result.exit_code) == ('oauth-env', 65)
    elif mode == 'readonly' and tail == b'\rgarbage\n':
        assert (result.classification, result.exit_code) == ('admission-refused', 65)
    else:
        assert (result.classification, result.exit_code) == ('unknown', 1)
    assert result.final_answer == '' and result.validated is None
