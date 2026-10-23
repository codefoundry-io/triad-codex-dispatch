"""Provider-free shared runtime lifecycle and refusal tests."""
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import pytest
from test_v2_rounds import round_fixture, worktree, finish, start
from test_v2_adapters import adapter_case

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ('README.md', 'README.ko.md', 'SECURITY.md', 'docs/installation.md',
              'docs/installation.ko.md', 'docs/shared-runtime.md', 'docs/shared-runtime.ko.md',
              'docs/references/repair-protocol.md')


def runtime():
    assert (ROOT / 'bin/shared_runtime.py').is_file(), 'shared runtime implementation missing'
    return importlib.import_module('shared_runtime')


def fixture(tmp_path):
    module = runtime()
    toolkit = tmp_path / 'plugin'
    for directory in ('bin', 'contracts', 'vendor', 'scripts'):
        shutil.copytree(ROOT / directory, toolkit / directory,
                        ignore=shutil.ignore_patterns('__pycache__', '_logs', '_debug'))
    shutil.copy2(ROOT / 'requirements.txt', toolkit / 'requirements.txt')
    for name in REFERENCES:
        target = toolkit / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    # Synthetic wrapper: observes the actual hardened execution context.
    for name in module.COMMANDS:
        (toolkit / 'bin' / name).write_text(
            'import json,os,sys\nprint(json.dumps({"argv":sys.argv[1:],'
            '"stdin":sys.stdin.read(),"classifier":os.environ.get("TRIAD_CLASSIFIER_EXTENSION"),'
            '"pin":os.environ.get("TRIAD_CLAUDE_BIN"),"selector":os.environ.get("TRIAD_RUNTIME_BINDING")}))\n'
            'sys.exit(7)\n')
    context = {'python': str(Path(sys.executable).resolve()), 'path': '/usr/bin:/bin',
               'classifier': str(tmp_path / 'classifier.json'),
               'providers': {'claude': '/bin/echo', 'gemini': None, 'agy': None}}
    return module, toolkit, context, tmp_path / 'shared', tmp_path / 'receipts', tmp_path / 'commands'


def install(parts):
    module, toolkit, context, shared, receipts, commands = parts
    return module.publish_installation(toolkit, context, shared_root=shared,
                                       receipt_root=receipts, launcher_dir=commands)


@pytest.mark.parametrize('version,source,inventory_digest,count,archive_digest', [
    ('dev5', '859f27c07c1123e87b50344f587999a0cbc172a6',
     'ba9eaf2991226d2438e5b207653cc5c71c6d722dd90ffe387f26542e02ee9b08', 26,
     '6d36cba0869ef73a9da315a0fdc53f391421966a81f0f47924453702df798b5e'),
    ('dev6', '1872227abd42553635c733e0aa228548a577a732',
     '6929313b5f1cb32f9fb3b148ec77f35486d304c9091ebc073da362d66eaed018', 27,
     'ea1ff46ef16e79d446abfc1d97f75c78eca81ca929466feafc8397a88a12082a'),
])
@pytest.mark.parametrize('damage', [None, 'package', 'adoption', 'extra-file'])
def test_frozen_library_migration_authenticates_before_command_changes(
        tmp_path, damage, version, source, inventory_digest, count, archive_digest):
    parts = fixture(tmp_path)
    module, toolkit, context, _, _, commands = parts
    legacy = tmp_path / ('legacy-' + version)
    shutil.copytree(toolkit, legacy)
    shutil.rmtree(legacy / 'bin/triad_dispatch_lib')
    archive = ROOT / ('tests/fixtures/shared-runtime-' + version + '/library.zip')
    assert module.digest(archive.read_bytes()) == archive_digest
    with zipfile.ZipFile(archive) as frozen:
        record = 'contracts/library-adoption.json'
        adoption = json.loads(frozen.read(record))
        expected = adoption['sha256']
        assert adoption['version'] == '0.1.0.' + version
        assert adoption['source_commit'] == source
        assert len(expected) == count
        assert module.digest(module.canonical(expected)) == inventory_digest
        assert sorted(frozen.namelist()) == sorted([record, *expected])
        for name in frozen.namelist():
            relative = Path(name)
            assert not relative.is_absolute() and '..' not in relative.parts
            payload = frozen.read(name)
            if name != record:
                assert module.digest(payload) == expected[name]
            target = legacy / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
    assert module.inventory(legacy, ('bin/triad_dispatch_lib', 'vendor/triad-dispatch-lib.LICENSE')) == expected
    commands.mkdir()
    for name in module.COMMANDS:
        body = module.launcher_bytes(legacy, name, context).decode()
        body = body.replace('env.pop("TRIAD_RUNTIME_BINDING", None)\n', '').replace('"-E", "-B",', '"-E",')
        (commands / name).write_text(body)
        (commands / name).chmod(0o755)
    before = {name: ((commands / name).read_bytes(), (commands / name).stat()) for name in module.COMMANDS}
    if damage == 'package':
        with (legacy / 'bin/triad_dispatch_lib/errors.py').open('ab') as stream:
            stream.write(b'\n# altered package\n')
    elif damage == 'adoption':
        adoption['source_commit'] = '0' * 40
        (legacy / record).write_text(json.dumps(adoption))
    elif damage == 'extra-file':
        (legacy / 'bin/triad_dispatch_lib/unlisted.py').write_text('# unlisted\n')
    if damage:
        with pytest.raises(ValueError, match='unsupported direct Codex library baseline'):
            install(parts)
        assert {name: ((commands / name).read_bytes(), (commands / name).stat()) for name in module.COMMANDS} == before
    else:
        paths = {name: commands / name for name in module.COMMANDS}
        authenticated = module.verify_legacy_group(paths)
        assert authenticated['consumer'] == 'codex'
        assert authenticated['library_digest'] == module.digest(module.canonical(expected))
        installed = install(parts)
        assert Path(installed['receipt_file']).is_file()
        result = subprocess.run([str(commands / 'claude_wrapper.py'), version], input='old input',
                                capture_output=True, text=True, env={})
        assert result.returncode == 7, result.stderr
        assert json.loads(result.stdout)['argv'] == [version]
        assert json.loads(result.stdout)['stdin'] == 'old input'


def test_empty_install_retains_context_after_cache_and_receipt_removal(tmp_path):
    parts = fixture(tmp_path)
    module, toolkit, context, shared, receipts, commands = parts
    installed = install(parts)
    resolved = module.resolve_installed_runtime(toolkit, receipt_root=receipts)
    assert resolved['binding_id'] == installed['binding_id']
    assert Path(resolved['toolkit_root']) != toolkit
    call = module.provider_invocation(resolved['runtime_context'], 'claude_wrapper.py', ['one', 'two words'])
    module.remove_installation(toolkit, receipt_root=receipts)
    shutil.rmtree(toolkit)
    result = subprocess.run(call['argv'], input='input bytes', text=True, capture_output=True, env={})
    assert result.returncode == 7, result.stderr
    assert json.loads(result.stdout) == {'argv': ['one', 'two words'], 'stdin': 'input bytes',
                                        'classifier': context['classifier'], 'pin': '/bin/echo', 'selector': None}
    assert all((commands / name).is_file() for name in module.COMMANDS)


def test_explicit_selector_refuses_without_starting_and_preserves_legacy_default(tmp_path):
    parts = fixture(tmp_path)
    module, toolkit, context, shared, receipts, commands = parts
    first = install(parts)
    context['classifier'] = str(tmp_path / 'second.json')
    second = install(parts)
    assert first['binding_id'] != second['binding_id']
    with pytest.raises(ValueError, match='ambiguous'):
        module.resolve_installed_runtime(toolkit, receipt_root=receipts)
    selected = module.resolve_installed_runtime(toolkit, second['binding_id'], receipt_root=receipts)
    assert selected['binding_id'] == second['binding_id']
    for selector in ('malformed', '0' * 64):
        result = subprocess.run([str(commands / 'claude_wrapper.py')], capture_output=True,
                                text=True, env={'TRIAD_RUNTIME_BINDING': selector})
        assert result.returncode != 7
        assert result.stdout == ''
    result = subprocess.run([str(commands / 'claude_wrapper.py')], input='', capture_output=True, text=True, env={})
    assert json.loads(result.stdout)['classifier'] == str(tmp_path / 'classifier.json')


@pytest.mark.parametrize('damage', ['receipt', 'snapshot', 'launcher'])
def test_resolver_rejects_tampering(tmp_path, damage):
    parts = fixture(tmp_path)
    module, toolkit, _, _, receipts, _ = parts
    item = install(parts)
    target = {'receipt': Path(item['receipt_file']),
              'snapshot': Path(item['toolkit_root']) / 'bin/claude_wrapper.py',
              'launcher': Path(item['launcher_dir']) / 'claude_wrapper.py'}[damage]
    target.chmod(0o644)
    target.write_bytes(target.read_bytes() + b'\n')
    with pytest.raises((ValueError, OSError)):
        module.resolve_installed_runtime(toolkit, receipt_root=receipts)


@pytest.mark.parametrize('kind', ['partial', 'foreign', 'symlink', 'fifo', 'hardlink'])
def test_unsafe_group_is_unchanged(tmp_path, kind):
    parts = fixture(tmp_path)
    module, _, _, _, _, commands = parts
    commands.mkdir()
    first = commands / module.COMMANDS[0]
    if kind == 'symlink':
        first.symlink_to(tmp_path / 'absent')
    elif kind == 'fifo':
        os.mkfifo(first)
    else:
        first.write_text('foreign')
        if kind == 'hardlink':
            os.link(first, commands / 'other')
        if kind == 'foreign':
            for name in module.COMMANDS[1:]:
                (commands / name).write_text('foreign')
    before = first.lstat()
    with pytest.raises((ValueError, OSError)):
        install(parts)
    assert first.lstat() == before


def test_repeat_install_reuses_receipt_and_changed_root_retains_previous(tmp_path):
    parts = fixture(tmp_path)
    first = install(parts)
    assert install(parts)['receipt_file'] == first['receipt_file']
    module, toolkit, context, shared, receipts, commands = parts
    updated = tmp_path / 'updated'
    shutil.copytree(toolkit, updated)
    second = install((module, updated, context, shared, receipts, commands))
    assert second['receipt_file'] != first['receipt_file']
    assert Path(first['receipt_file']).is_file()
    with pytest.raises(ValueError):
        module.resolve_installed_runtime(tmp_path / 'wrong-root', receipt_root=receipts)


def test_v2_installed_invocation_uses_bound_launcher_and_independent_log_command(tmp_path, monkeypatch):
    import review_round_v2 as rounds
    parts = fixture(tmp_path)
    installed = install(parts)
    monkeypatch.setattr(rounds, 'TOOLKIT', Path(installed['toolkit_root']))
    binding = dict(review_id='runtime-test', family='claude', content_digest='a' * 64,
                   leg_name='claude', attempt=1, route=None)
    adapter = dict(family='claude', transport_route='claude', cwd=str(tmp_path), timeout_s=120,
                   model=None, effort=None, binary='/bin/echo')
    invocation = rounds._invocation(binding, adapter, tmp_path, 'prompt',
                                    runtime_context=installed['runtime_context'])
    assert invocation['argv'][0] == installed['launcher_dir'] + '/claude_wrapper.py'
    assert invocation['expected_wrapper_cmd'][0] == installed['toolkit_root'] + '/bin/claude_wrapper.py'
    assert invocation['expected_wrapper_cmd'][1:] == invocation['argv'][1:]
    assert 'TRIAD_CLAUDE_BIN' not in invocation['env']


def test_legacy_grammar_and_full_inventory_required(tmp_path, monkeypatch):
    parts = fixture(tmp_path)
    module, toolkit, context, _, _, commands = parts
    commands.mkdir()
    for name in module.COMMANDS:
        body = module.launcher_bytes(toolkit, name, context).decode()
        body = body.replace('# triad-codex-dispatch managed launcher', '# agy-triad-dispatch managed launcher')
        body = body.replace('env.pop("TRIAD_RUNTIME_BINDING", None)\n', '').replace('"-E", "-B",', '"-E",')
        (commands / name).write_text(body)
    scopes = json.loads((ROOT / 'bin/data/agy-legacy-baseline.json').read_text())['inventory_scope']
    assets = module.inventory(toolkit, scopes)
    baseline = {'inventory_scope': scopes, 'inventory': assets,
                'inventory_serialization': {'sha256': module.digest(module.canonical(assets))},
                'library': {'approved_content_sha256': 'a' * 64}}
    paths = {name: commands / name for name in module.COMMANDS}
    assert module.verify_legacy_group(paths, baseline)['consumer'] == 'agy'
    target = commands / 'claude_wrapper.py'
    original = target.read_text()
    target.write_text(original + '\nprint("forged marker payload")\n')
    with pytest.raises(ValueError, match='AST'):
        module.verify_legacy_group(paths, baseline)
    target.write_text(original.replace(context['classifier'], str(tmp_path / 'mixed-classifier.json')))
    with pytest.raises(ValueError, match='mixed'):
        module.verify_legacy_group(paths, baseline)
    target.write_text(original)
    (toolkit / 'bin/claude_wrapper.py').write_text('changed')
    with pytest.raises(ValueError, match='baseline'):
        module.verify_legacy_group(paths, baseline)


def test_publication_failure_rolls_back_group_and_receipt(tmp_path, monkeypatch):
    parts = fixture(tmp_path)
    module, _, _, _, receipts, commands = parts
    original = module.repair.publish_to
    def fail(temp, target, expected, journal):
        if target == commands / 'gemini_wrapper.py':
            raise OSError('injected publication failure')
        return original(temp, target, expected, journal)
    monkeypatch.setattr(module.repair, 'publish_to', fail)
    with pytest.raises(OSError, match='injected'):
        install(parts)
    assert not any((commands / name).exists() for name in module.COMMANDS)
    assert not list(receipts.glob('*.json'))


def test_bound_basis_collects_and_retries_after_installation_removal(tmp_path, monkeypatch, round_fixture):
    parts = fixture(tmp_path)
    installed = install(parts)
    case = round_fixture(make_basis=False)
    rounds, _, root, _, request, _ = case
    original = rounds.prepare_adapters
    seen = []
    def prepare(*args, runtime_context=None, **kwargs):
        seen.append(runtime_context)
        return original(*args, **kwargs)
    monkeypatch.setattr(rounds, 'prepare_adapters', prepare)
    monkeypatch.setattr(rounds, 'TOOLKIT', Path(installed['toolkit_root']))
    request['runtime_binding'] = installed['binding_id']
    basis = rounds.create_basis(request, root=root)
    case = (rounds, basis, *case[2:])
    assert basis['runtime_context'] == installed['runtime_context']
    parts[0].remove_installation(parts[1], receipt_root=parts[4])
    shutil.rmtree(parts[1])
    for name in basis['enabled']:
        allocation = start(case, name)
        if allocation['adapter']['family'] == 'codex':
            assert allocation['invocation']['tool'] == 'collaboration.spawn_agent'
        else:
            assert allocation['invocation']['argv'][0].startswith(installed['launcher_dir'])
        finish(case, allocation, failed=True)
        retry = rounds.allocate_attempt(Path(basis['basis_file']), name, diagnosis='fixture transport failure')
        finish(case, retry)
    assert rounds.collect(Path(basis['basis_file']))['status'] == 'AGREED'
    assert all(value == installed['runtime_context'] for value in seen)
    with pytest.raises(ValueError, match='explicit runtime_binding'):
        parts[0].context_for_toolkit(Path(installed['toolkit_root']))


@pytest.mark.parametrize('consumer', ['codex', 'agy'])
def test_migrated_direct_group_preserves_bare_behavior_through_update_and_remove(tmp_path, monkeypatch, consumer):
    parts = fixture(tmp_path)
    module, toolkit, context, shared, receipts, commands = parts
    commands.mkdir()
    legacy = tmp_path / 'legacy'
    shutil.copytree(toolkit, legacy)
    legacy_context = {**context, 'classifier': str(tmp_path / 'legacy-classifier.json')}
    for name in module.COMMANDS:
        body = module.launcher_bytes(legacy, name, legacy_context).decode()
        body = body.replace('env.pop("TRIAD_RUNTIME_BINDING", None)\n', '').replace('"-E", "-B",', '"-E",')
        if consumer == 'agy':
            body = body.replace('# triad-codex-dispatch managed launcher', '# agy-triad-dispatch managed launcher')
        (commands / name).write_text(body)
        (commands / name).chmod(0o755)
    if consumer == 'agy':
        scopes = json.loads((ROOT / 'bin/data/agy-legacy-baseline.json').read_text())['inventory_scope']
        assets = module.inventory(legacy, scopes)
        baseline = {'inventory_scope': scopes, 'inventory': assets,
                    'inventory_serialization': {'sha256': module.digest(module.canonical(assets))},
                    'library': {'approved_content_sha256': 'a' * 64}}
        verifier = module.verify_legacy_group
        monkeypatch.setattr(module, 'verify_legacy_group', lambda paths: verifier(paths, baseline))
    before = subprocess.run([str(commands / 'claude_wrapper.py'), 'same'], input='stdin',
                            capture_output=True, text=True, env={})
    first = install(parts)
    for phase in ('installed', 'updated', 'removed'):
        if phase == 'updated':
            context['classifier'] = str(tmp_path / 'updated-classifier.json')
            install(parts)
        if phase == 'removed':
            module.remove_installation(toolkit, first['binding_id'], receipt_root=receipts)
        after = subprocess.run([str(commands / 'claude_wrapper.py'), 'same'], input='stdin',
                               capture_output=True, text=True, env={})
        assert (after.returncode, after.stdout, after.stderr) == (before.returncode, before.stdout, before.stderr)


def test_actual_retained_wrapper_log_accepts_exact_path_and_rejects_cache_path(tmp_path, monkeypatch, round_fixture):
    from test_v2_producer_adapter import verdict
    parts = fixture(tmp_path)
    module, toolkit, context, _, receipts, _ = parts
    shutil.copy2(ROOT / 'bin/claude_wrapper.py', toolkit / 'bin/claude_wrapper.py')
    provider = tmp_path / 'fake-claude'
    provider.write_text(f'#!{sys.executable}\nimport json,sys\nassert sys.stdin.read()\n'
        'schema=json.loads(sys.argv[sys.argv.index("--json-schema")+1])\n'
        f'data={verdict()!r}\n'
        'data.update({k:v["const"] for k,v in schema["properties"].items() if "const" in v})\n'
        'print(json.dumps({"result":"", "structured_output":data}))\n')
    provider.chmod(0o755)
    context['providers']['claude'] = str(provider)
    installed = install(parts)
    def transform(adapters):
        adapters['claude']['binary'] = str(provider)
        return adapters
    case = round_fixture(make_basis=False, adapter_transform=transform)
    rounds, _, root, _, request, _ = case
    prepare = rounds.prepare_adapters
    monkeypatch.setattr(rounds, 'prepare_adapters', lambda *a, runtime_context=None, **k: prepare(*a, **k))
    monkeypatch.setattr(rounds, 'TOOLKIT', Path(installed['toolkit_root']))
    request['runtime_binding'] = installed['binding_id']
    basis = rounds.create_basis(request, root=root)
    item = rounds.allocate_attempt(Path(basis['basis_file']), 'claude')
    module.remove_installation(toolkit, receipt_root=receipts)
    shutil.rmtree(toolkit)
    call = item['invocation']
    with open(call['stdout_file'], 'wb') as out, open(call['stderr_file'], 'wb') as err:
        result = subprocess.run(call['argv'], env=call['env'], stdout=out, stderr=err, timeout=30)
    assert result.returncode == 0, Path(call['stderr_file']).read_text()
    log = next((Path(item['folder']) / 'logs/claude/runs').glob('*.json'))
    original = log.read_bytes()
    data = json.loads(original)
    assert data['wrapper_cmd'] == call['expected_wrapper_cmd']
    data['wrapper_cmd'][0] = str(toolkit / 'bin/claude_wrapper.py')
    log.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='allocated wrapper'):
        rounds.record_cli_attempt(Path(basis['basis_file']), 'claude', run_log=log)
    log.write_bytes(original)
    rounds.record_cli_attempt(Path(basis['basis_file']), 'claude', run_log=log)


def test_provider_probe_uses_pinned_context_without_secret_command_arguments(tmp_path, monkeypatch):
    parts = fixture(tmp_path)
    module, toolkit, context, _, _, _ = parts
    provider = tmp_path / 'probe'
    provider.write_text(f'#!{sys.executable}\nimport json,os\nprint(json.dumps({{k:os.environ.get(k) for k in '
                        '("PATH","TRIAD_CLASSIFIER_EXTENSION","NODE_OPTIONS","TRIAD_CLAUDE_BIN")}))\n')
    provider.chmod(0o755)
    context['providers']['claude'] = str(provider)
    installed = install(parts)
    monkeypatch.setenv('EXAMPLE_SECRET', 'must-not-appear-in-argv')
    argv = module.probe_invocation(installed['runtime_context'], [str(provider), '--version'])
    assert 'must-not-appear-in-argv' not in repr(argv)
    result = subprocess.run(argv, capture_output=True, text=True, env={'NODE_OPTIONS': 'poison'})
    assert result.returncode == 0, result.stderr
    observed = json.loads(result.stdout)
    assert observed == {'PATH': context['path'], 'TRIAD_CLASSIFIER_EXTENSION': context['classifier'],
                        'NODE_OPTIONS': None, 'TRIAD_CLAUDE_BIN': str(provider)}


def test_retained_operational_references_survive_cache_removal(tmp_path):
    parts = fixture(tmp_path)
    original = {name: (parts[1] / name).read_bytes() for name in REFERENCES}
    # Deliberately excluded owner document must not enter the snapshot.
    owner = parts[1] / 'docs/owner-held.md'
    owner.write_text('not a runtime asset')
    installed = install(parts)
    shutil.rmtree(parts[1])
    retained = Path(installed['toolkit_root'])
    assert original == {name: (retained / name).read_bytes() for name in REFERENCES}
    assert not (retained / 'docs/owner-held.md').exists()


def test_missing_required_operational_reference_refuses_before_publication(tmp_path):
    parts = fixture(tmp_path)
    (parts[1] / 'docs/references/repair-protocol.md').unlink()
    with pytest.raises(ValueError, match='required runtime reference'):
        install(parts)
    assert not parts[5].exists()


def test_google_preflight_uses_retained_binding_selector_and_wrapper(tmp_path, monkeypatch, adapter_case):
    parts = fixture(tmp_path)
    module, toolkit, context, _, receipts, _ = parts
    adapters, roster, kwargs, calls, binaries = adapter_case()
    context['providers'] = dict(binaries)
    installed = install(parts)
    monkeypatch.setattr(adapters, 'ROOT', Path(installed['toolkit_root']))
    monkeypatch.setattr(adapters.review_round, '__file__', installed['toolkit_root'] + '/bin/review_round.py')
    entry = next(row for row in roster['legs'] if row['vendor'] == 'google')
    entry['google']['route'] = 'agy'
    folder = tmp_path / 'bound-google-preflight'
    folder.mkdir()
    module.remove_installation(toolkit, receipt_root=receipts)
    shutil.rmtree(toolkit)
    result = adapters._google(entry, defaults={'agy': {'model': 'gemini-4-argon-high', 'effort': 'high'}},
        review_id=kwargs['review_id'], cwd=kwargs['cwd'], authentication_class='personal-google',
        folder=folder, attempt=1, runtime_context=installed['runtime_context'])
    call = next(argv for argv in calls if '--preflight-only' in argv)
    assert call[0] == installed['launcher_dir'] + '/antigravity_wrapper.py'
    selector = json.loads(Path(result['selector_file']).read_text())
    assert selector['wrapper'] == installed['toolkit_root'] + '/bin/antigravity_wrapper.py'
    assert selector['executable'] == binaries['agy']
    assert result['preflight_sha256'] == module.digest(Path(result['preflight_file']).read_bytes())
