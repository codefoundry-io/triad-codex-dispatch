"""C11/C37/C75: independent agreed-name fixture; synthetic values only."""
LOADER = ('LD_PRELOAD', 'LD_LIBRARY_PATH', 'LD_AUDIT', 'LD_DEBUG', 'DYLD_INSERT_LIBRARIES', 'DYLD_LIBRARY_PATH', 'DYLD_FRAMEWORK_PATH', 'NODE_OPTIONS', 'NODE_PATH', 'PYTHONPATH', 'PYTHONHOME', 'PYTHONSTARTUP', 'BASH_ENV', 'ENV', 'PERL5LIB', 'RUBYOPT', 'RUBYLIB')
CREDENTIALS = ('GOOGLE_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_APPLICATION_CREDENTIALS', 'GOOGLE_GENAI_USE_VERTEXAI', 'GEMINI_CLI_USE_COMPUTE_ADC', 'CLOUD_SHELL', 'GOOGLE_GEMINI_BASE_URL', 'GOOGLE_VERTEX_BASE_URL', 'GEMINI_DEFAULT_AUTH_TYPE', 'GOOGLE_CLOUD_ACCESS_TOKEN', 'AGY_ADC_AUTH', 'GOOGLE_GENAI_USE_ENTERPRISE', 'OPENAI_API_KEY', 'CODEX_API_KEY', 'CODEX_ACCESS_TOKEN', 'OPENAI_BASE_URL', 'OPENAI_ORGANIZATION', 'OPENAI_PROJECT', 'ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_BASE_URL', 'CLAUDE_CODE_USE_BEDROCK', 'CLAUDE_CODE_USE_VERTEX', 'CLAUDE_CODE_USE_FOUNDRY', 'CLAUDE_CODE_USE_ANTHROPIC_AWS', 'CLAUDE_CODE_USE_ANTHROPIC_GOOGLE_CLOUD', 'CLAUDE_CODE_USE_GATEWAY', 'CLAUDE_CODE_USE_MANTLE', 'CLAUDE_CODE_API_BASE_URL', 'CLAUDE_CODE_API_KEY_FILE_DESCRIPTOR', 'CLAUDE_CODE_OAUTH_TOKEN', 'CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR', 'CLAUDE_CODE_OAUTH_REFRESH_TOKEN', 'CLAUDE_CODE_GATEWAY_TOKEN', 'CLAUDE_CODE_GATEWAY_TOKEN_FILE_DESCRIPTOR', 'ANTHROPIC_FOUNDRY_API_KEY', 'ANTHROPIC_FOUNDRY_AUTH_TOKEN', 'ANTHROPIC_AWS_API_KEY', 'AWS_BEARER_TOKEN_BEDROCK', 'ANTHROPIC_IDENTITY_TOKEN', 'ANTHROPIC_IDENTITY_TOKEN_FILE', 'ANTHROPIC_FEDERATION_RULE_ID', 'ANTHROPIC_SERVICE_ACCOUNT_ID', 'ANTHROPIC_PROFILE', 'ANTHROPIC_ORGANIZATION_ID', 'ANTHROPIC_WORKSPACE_ID')
PROJECTS = ('GOOGLE_CLOUD_PROJECT', 'GOOGLE_CLOUD_LOCATION', 'GOOGLE_CLOUD_REGION', 'GOOGLE_CLOUD_QUOTA_PROJECT')

import collections.abc
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
import _common as common
import antigravity_wrapper as agy
import gemini_wrapper as gemini
import google_diagnostics as diagnostics

ALL = set(LOADER + CREDENTIALS + PROJECTS)
KEEP = {'GEMINI_MODEL': 'owner-model', 'ANTHROPIC_MODEL': 'owner-model',
        'ANTHROPIC_SMALL_FAST_MODEL': 'owner-small-model',
        'CLAUDE_CODE_EFFORT_LEVEL': 'owner-effort',
        'ANTHROPIC_DEFAULT_OPUS_MODEL': 'owner-alias',
        'PATH': '/synthetic/bin', 'HOME': '/synthetic/home',
        'XDG_CONFIG_HOME': '/synthetic/config', 'CODEX_HOME': '/synthetic/codex',
        'CLAUDE_CONFIG_DIR': '/synthetic/claude', 'GOOGLE_GENAI_USE_GCA': 'true'}


def parent():
    return {**dict.fromkeys(ALL, 'synthetic-only'), **KEEP}


def assert_environment(child, cli, *, keep=KEEP):
    allowed_projects = set(PROJECTS) if cli == 'gemini' else set()
    assert not (set(child) & (ALL - allowed_projects))
    assert allowed_projects <= set(child)
    assert {key: child[key] for key in keep} == keep


@pytest.fixture(autouse=True)
def isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(common, '_LOG_DIR', tmp_path / 'logs')
    monkeypatch.setattr(common, '_LOG_DIR_CONFIGURED', True)
    monkeypatch.setattr(common, 'prune_stale_tmp_dirs', lambda *a, **kw: None)
    monkeypatch.setattr(common, '_classifier_extension_path', lambda: tmp_path / 'extension.json')


@pytest.mark.parametrize('cli', [None, 'codex', 'claude', 'gemini', 'antigravity', 'agy', 'unknown'])
def test_C11_C37_exact_name_set_and_route_exception(cli):
    source = parent()
    before = source.copy()
    result = common.scrubbed_child_env(source, cli=cli)
    assert_environment(result, cli)
    assert source == before
    result['PATH'] = 'changed'
    assert source['PATH'] == KEEP['PATH']


@pytest.mark.parametrize('cli', [None, 'gemini', 'antigravity'])
def test_C75_rejected_values_never_retrieved(cli):
    data = parent()
    explicit = {'HOME', 'GOOGLE_CLOUD_PROJECT'}
    forbidden = (ALL - (set(PROJECTS) if cli == 'gemini' else set())) | explicit
    reads = []
    class Guarded(collections.abc.Mapping):
        def __iter__(self): return iter(data)
        def __len__(self): return len(data)
        def __getitem__(self, key):
            assert key not in forbidden, f'retrieved omitted name {key}'
            reads.append(key)
            return data[key]
    result = common.scrubbed_child_env(Guarded(), cli=cli, remove=explicit)
    assert set(result) == set(data) - forbidden
    assert set(reads) == set(result)


def test_C11_existing_remove_only_call_keeps_compatibility():
    result = common.scrubbed_child_env({'PATH': 'keep', 'EXTRA': 'drop'}, remove=('EXTRA',))
    assert result == {'PATH': 'keep'}


@pytest.mark.parametrize('cli', ['codex', 'claude', 'gemini', 'antigravity'])
@pytest.mark.parametrize('classify_and_log', [False, True])
def test_C11_shared_spawn_normal_and_formal_capture(monkeypatch, tmp_path, cli, classify_and_log):
    source = parent()
    monkeypatch.setattr(common.os, 'environ', source)
    command = [sys.executable, '-c', 'import json, os; print(json.dumps(sorted(os.environ)))']
    result = common._run_once(cli, command, str(tmp_path), 5, classify_and_log=classify_and_log)
    assert result.exit_code == 0
    names = set(json.loads(result.stdout))
    projects = set(PROJECTS) if cli == 'gemini' else set()
    assert not names & (ALL - projects)
    assert projects <= names
    assert set(KEEP) <= names
    assert source == parent()


def test_C11_gemini_version_and_help_probes(monkeypatch, tmp_path):
    monkeypatch.setattr(common.os, 'environ', parent())
    calls = []
    def run(argv, **kwargs):
        calls.append((argv, kwargs['env']))
        return SimpleNamespace(returncode=0, stdout='0.63.0' if argv[-1] == '--version' else 'help', stderr='')
    monkeypatch.setattr(gemini.subprocess, 'run', run)
    monkeypatch.setattr(gemini, '_validate_formal_policy', lambda *a, **kw: 'fixture')
    monkeypatch.setattr(gemini, '_supports_formal_help_contract', lambda text: True)
    selector = SimpleNamespace(receipt_sha256='fixture', review_id='fixture')
    assert gemini._run_preflight('/synthetic/gemini', str(tmp_path), 5, selector) == 0
    assert [argv[-1] for argv, env in calls] == ['--version', '--help']
    for argv, env in calls:
        assert_environment(env, 'gemini')


def test_C11_agy_version_probe(monkeypatch):
    monkeypatch.setattr(common.os, 'environ', parent())
    observed = []
    def run(argv, **kwargs):
        observed.append(kwargs['env'])
        return SimpleNamespace(returncode=0, stdout='1.3.2', stderr='')
    monkeypatch.setattr(agy.subprocess, 'run', run)
    assert agy._probe_agy_version('/synthetic/agy') == (1, 3, 2)
    assert len(observed) == 1
    assert_environment(observed[0], 'antigravity')


@pytest.mark.parametrize('cli', ['agy', 'gemini'])
def test_C11_diagnostic_probes_use_selected_route(monkeypatch, cli):
    monkeypatch.setattr(common.os, 'environ', parent())
    monkeypatch.setattr(diagnostics.review_round, '_selectable_google_binary', lambda name: '/synthetic/vendor')
    observed = []
    def probe(binary, args, cwd, env):
        observed.append(env)
        return {'status': 'ok'}, b'0.63.0' if args == ['--version'] else b'Usage: vendor'
    monkeypatch.setattr(diagnostics, '_run_probe', probe)
    assert diagnostics.collect_snapshot(cli)['status'] == 'complete'
    assert len(observed) == 2
    for env in observed:
        assert_environment(env, cli)


def test_C75_v2_gemini_adapter_preserves_environment_through_wrapper(monkeypatch, tmp_path):
    import review_adapters_v2 as adapters
    from review_roster import resolve_roster

    observations = tmp_path / 'vendor-probes.jsonl'
    executable = tmp_path / 'gemini'
    executable.write_text(
        f'#!{sys.executable}\n'
        'import json, os, sys\n'
        f'with open({str(observations)!r}, "a") as stream:\n'
        '    stream.write(json.dumps({"args": sys.argv[1:], "env": dict(os.environ)}) + "\\n")\n'
        'if sys.argv[1:] == ["--version"]:\n'
        '    print("0.63.0")\n'
        'elif sys.argv[1:] == ["--help"]:\n'
        '    print(\'--model Model [string]\\n--approval-mode Set the approval mode [choices: "default", "plan"]\\n--policy Additional policy files or directories to load [array]\')\n'
        'else:\n'
        '    raise SystemExit("unexpected inference invocation")\n'
    )
    executable.chmod(0o755)
    roster = resolve_roster(tmp_path)
    for entry in roster['legs']:
        entry['enabled'] = entry['vendor'] == 'google'
        if entry['enabled']:
            entry['google']['route'] = 'gemini'
    monkeypatch.setattr(adapters, 'resolve_binary', lambda name: str(executable) if name == 'gemini' else None)
    source = parent()
    # The real wrapper imports dependencies from the login user's Python site.
    # The vendor itself is the local no-inference executable above.
    source['HOME'] = str(Path.home())
    before = source.copy()
    monkeypatch.setattr(common.os, 'environ', source)
    (tmp_path / 'receipts').mkdir()
    result = adapters.prepare_adapters(
        roster, review_id='env-boundary', cwd=tmp_path,
        authentication_class='gemini-enterprise', native_capabilities={},
        receipt_root=tmp_path / 'receipts')
    assert result['google']['route'] == 'gemini'
    records = [json.loads(row) for row in observations.read_text().splitlines()]
    assert [row['args'] for row in records] == [['--version'], ['--help']]
    for record in records:
        assert_environment(record['env'], 'gemini', keep={**KEEP, 'HOME': before['HOME']})
    assert source == before


def test_C75_adapter_probe_default_keeps_non_gemini_boundary(monkeypatch, tmp_path):
    import review_adapters_v2 as adapters

    source = parent()
    monkeypatch.setattr(common.os, 'environ', source)
    output = adapters.probe(
        [sys.executable, '-c', 'import json, os; print(json.dumps(dict(os.environ)))'],
        cwd=tmp_path)
    assert_environment(json.loads(output), None)
    assert source == parent()
