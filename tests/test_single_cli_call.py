"""C78: the host must not purchase another CLI answer after capacity/schema failure."""
import json
from pathlib import Path
import sys

import pytest
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
import _common


class Answer(BaseModel):
    ok: bool


SCRIPT = '''
import json, pathlib, sys
record, output, error, code = sys.argv[1:]
with pathlib.Path(record).open('a') as stream:
    stream.write(json.dumps({'prompt': sys.stdin.read()}) + '\\n')
print(output)
print(error, file=sys.stderr)
sys.exit(int(code))
'''


@pytest.fixture
def invoke(tmp_path, monkeypatch):
    # Existing old-driver test seam avoids minutes of deliberate capacity backoff.
    # The new policy must still launch once regardless of this legacy variable.
    monkeypatch.setenv('TRIAD_SERVER_CAP_NO_BACKOFF', '1')
    monkeypatch.setenv('TRIAD_DISPATCH_LOG_DIR', str(tmp_path / 'logs'))
    monkeypatch.setattr(_common, 'prune_stale_run_logs', lambda _cli: None)
    journal = tmp_path / 'launches.jsonl'

    def call(cli, output, error='', code=0, schema=None, **kwargs):
        result = _common.run_cli_with_retry(
            cli, lambda _p: [sys.executable, '-c', SCRIPT, str(journal),
                             json.dumps(output), error, str(code)],
            'review the selected diff', str(tmp_path), 5,
            pydantic_cls=schema, prompt_via_stdin=True,
            prompt_suffix='AUTHORIZED WEB CLAUSE', **kwargs)
        launches = [json.loads(line) for line in journal.read_text().splitlines()]
        return result, launches
    return call


@pytest.mark.parametrize('cli,output,error,code', [
    ('claude', {'is_error': True, 'result': 'overloaded_error'}, '', 0),
    ('claude', {}, 'overloaded_error', 1),
    ('gemini', {'error': {'code': 429, 'message': 'RESOURCE_EXHAUSTED'}}, 'RESOURCE_EXHAUSTED', 1),
])
def test_c78_capacity_returns_first_failure_without_cli_replay(invoke, cli, output, error, code):
    result, launches = invoke(cli, output, error, code)
    assert len(launches) == 1
    assert (result.exit_code, result.classification) == (64, 'server-capacity')
    assert result.vendor_exit_code == code
    assert json.loads(result.stdout) == output
    assert result.final_answer == ''
    assert launches[0]['prompt'] == 'review the selected diff\n\nAUTHORIZED WEB CLAUSE'


@pytest.mark.parametrize('cli,key', [('claude', 'result'), ('gemini', 'response')])
def test_c78_schema_invalid_answer_is_not_repaired_by_another_call(invoke, cli, key):
    result, launches = invoke(cli, {key: json.dumps({'ok': 'not-a-boolean'})}, schema=Answer)
    assert len(launches) == 1
    assert (result.exit_code, result.classification) == (66, 'schema-fail')
    assert result.vendor_exit_code == 0 and result.validation_error
    assert result.final_answer == '' and result.validated is None
    assert result.schema_repair_attempt == 0 and result.mode == 'normal'
    assert 'review the selected diff' in launches[0]['prompt']
    assert launches[0]['prompt'].endswith('AUTHORIZED WEB CLAUSE')
    assert 'previous response failed' not in launches[0]['prompt']


@pytest.mark.parametrize('cli,key', [('claude', 'result'), ('gemini', 'response')])
def test_c78_valid_schema_answer_still_succeeds_once(invoke, cli, key):
    result, launches = invoke(cli, {key: json.dumps({'ok': True})}, schema=Answer)
    assert len(launches) == 1
    assert (result.exit_code, result.classification) == (0, 'ok')
    assert result.validated == {'ok': True}
    assert result.schema_repair_attempt == 0


def test_c78_gemini_auth_exit_stops_once(invoke):
    result, launches = invoke('gemini', {}, 'Authentication required', 41)
    assert len(launches) == 1
    assert (result.exit_code, result.classification) == (65, 'oauth-env')
    assert result.vendor_exit_code == 41


def test_c78_explicit_single_call_compatibility_stays_single(invoke):
    result, launches = invoke('claude', {'is_error': True, 'result': 'overloaded_error'},
                              single_provider_call=True)
    assert len(launches) == 1
    assert (result.exit_code, result.classification) == (64, 'server-capacity')
