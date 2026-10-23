"""Authenticated host storage and dispatch for shared TRIAD command groups.

Pure compatibility/identity/retention decisions belong to the pinned library.
Immutable assets are retained; receipts alone represent installation ownership.
"""
from __future__ import annotations

import argparse
import ast
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

sys.dont_write_bytecode = True
import bootstrap_repair as repair
import library_adoption
from triad_dispatch_lib.runtime_compat import (
    validate_consumer_binding, validate_runtime_descriptor,
    select_consumer_binding, plan_runtime_retention,
)

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ('claude_wrapper.py', 'gemini_wrapper.py', 'antigravity_wrapper.py', 'review_round.py')
VENDORS = {'claude_wrapper.py': ('claude',), 'gemini_wrapper.py': ('gemini',),
           'antigravity_wrapper.py': ('agy',), 'review_round.py': ('agy', 'gemini')}
SCRUB = ('LD_PRELOAD', 'LD_LIBRARY_PATH', 'LD_AUDIT', 'LD_DEBUG',
         'DYLD_INSERT_LIBRARIES', 'DYLD_LIBRARY_PATH', 'DYLD_FRAMEWORK_PATH',
         'NODE_OPTIONS', 'NODE_PATH', 'PYTHONPATH', 'PYTHONHOME', 'PYTHONSTARTUP',
         'BASH_ENV', 'ENV', 'PERL5LIB', 'RUBYOPT', 'RUBYLIB')
RUNTIME_REFERENCES = ('README.md', 'README.ko.md', 'SECURITY.md', 'docs/installation.md',
                      'docs/installation.ko.md', 'docs/shared-runtime.md', 'docs/shared-runtime.ko.md',
                      'docs/references/repair-protocol.md')
SCOPES = ('bin', 'contracts', 'prompts', 'skills', 'scripts', 'vendor', 'requirements.txt',
          'plugin.json', '.codex-plugin', *RUNTIME_REFERENCES)
MARKER = '# triad-dispatch shared launcher v1'
CAPABILITIES = ['hardened-launcher-v1']


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _id(value):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{64}', value) is None:
        raise ValueError('invalid runtime identity')
    return value


def _path(path):
    path = Path(path)
    if not path.is_absolute() or path != Path(os.path.normpath(path)):
        raise ValueError('runtime path must be canonical and absolute')
    repair.require_safe_ancestors(path / 'leaf')
    return path


def _state(path):
    path = Path(path)
    try:
        repair.require_safe_ancestors(path)
        state = repair.read_state(path)
    except repair.Refusal as error:
        raise ValueError(str(error)) from error
    if state is not None and path.lstat().st_nlink != 1:
        raise ValueError('hardlinked runtime file')
    return state


def _read(path):
    state = _state(path)
    if state is None:
        raise ValueError('missing runtime file')
    return state.data


def _object(path):
    raw = _read(path)
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != canonical(value):
        raise ValueError('noncanonical runtime metadata')
    return value


def _write(path, data, mode=0o444):
    path = Path(path)
    repair.require_safe_ancestors(path)
    state = _state(path)
    if state is not None:
        if state.data != data or state.mode != mode:
            raise ValueError('immutable runtime asset changed')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = repair.stage(path, data, mode)
    journal = []
    failure = None
    try:
        repair.publish_to(temp, path, None, journal)
    except BaseException as error:
        failure = error
    repair.finalize_transaction(failure, journal, repair.cleanup_all([temp]))


def inventory(root, scopes=SCOPES):
    root = _path(root)
    result = {}

    def walk(path):
        relative = path.relative_to(root).as_posix()
        # Do not descend into or inspect dynamic log/debug/cache contents.
        if path.name == '__pycache__' or relative in ('bin/_logs', 'bin/_debug'):
            return
        mode = path.lstat().st_mode
        if stat.S_ISDIR(mode):
            for child in sorted(path.iterdir()):
                walk(child)
        elif stat.S_ISREG(mode) and path.suffix not in ('.pyc', '.pyo'):
            result[relative] = digest(_read(path))
        elif not stat.S_ISREG(mode):
            raise ValueError('unsafe toolkit asset')

    for name in scopes:
        path = root / name
        if path.exists() or path.is_symlink():
            walk(path)
    return result


def _context(context):
    if not isinstance(context, dict) or set(context) != {'python', 'path', 'classifier', 'providers'}:
        raise ValueError('invalid launcher context')
    if not isinstance(context['path'], str) or not context['path']:
        raise ValueError('missing trusted PATH')
    for key in ('python', 'classifier'):
        if not isinstance(context[key], str) or not Path(context[key]).is_absolute():
            raise ValueError('invalid pinned path')
    if any(char.isspace() for char in context['python']):
        raise ValueError('unusable pinned interpreter shebang')
    if set(context['providers']) != {'claude', 'gemini', 'agy'}:
        raise ValueError('invalid provider pin inventory')
    if any(value is not None and (not isinstance(value, str) or not Path(value).is_absolute())
           for value in context['providers'].values()):
        raise ValueError('invalid provider pin')
    return context


def launcher_bytes(toolkit, name, context):
    context = _context(context)
    lines = [f'#!{context["python"]} -E', '# triad-codex-dispatch managed launcher',
             'import os', 'import sys', f'_SCRUB = {SCRUB!r}',
             'env = {k: v for k, v in os.environ.items() if k not in _SCRUB}',
             f'env["PATH"] = {context["path"]!r}', 'env["TRIAD_AUDIT_REDACT_PROMPTS"] = "1"',
             f'env["TRIAD_CLASSIFIER_EXTENSION"] = {context["classifier"]!r}',
             'env["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"']
    for vendor in VENDORS[name]:
        key, value = 'TRIAD_' + vendor.upper() + '_BIN', context['providers'][vendor]
        lines.append(f'env[{key!r}] = {value!r}' if value else f'env.pop({key!r}, None)')
    lines += ['env.pop("TRIAD_RUNTIME_BINDING", None)',
              f'os.execve({context["python"]!r}, [{context["python"]!r}, "-E", "-B", '
              f'{str(Path(toolkit) / "bin" / name)!r}] + sys.argv[1:], env)']
    return ('\n'.join(lines) + '\n').encode()


def _legacy_context(payloads):
    contexts, roots, markers = [], [], []
    providers = {}
    for name, data in payloads.items():
        text = data.decode()
        lines = text.splitlines()
        marker = lines[1] if len(lines) > 1 else ''
        if marker not in ('# triad-codex-dispatch managed launcher', '# agy-triad-dispatch managed launcher'):
            raise ValueError('unrecognized legacy launcher')
        normalized = text.replace(marker, '# triad-codex-dispatch managed launcher', 1).encode()
        if not lines[0].endswith(' -E') or not repair.command_data_is_managed(name, 'launcher', normalized):
            raise ValueError('unrecognized hardened legacy AST')
        tree = ast.parse(text)
        values = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Subscript):
                key = node.targets[0].slice.value
                values[key] = ast.literal_eval(node.value)
        python, argv = repair._exec_call(tree.body[-1], 'execve', env_arg=True)
        root = _path(Path(argv[-1]).parent.parent)
        if not values.get('TRIAD_CLASSIFIER_EXTENSION'):
            raise ValueError('legacy classifier must be explicitly pinned')
        contexts.append((python, values['PATH'], values['TRIAD_CLASSIFIER_EXTENSION']))
        roots.append(root)
        markers.append(marker)
        for vendor in VENDORS[name]:
            value = values.get('TRIAD_' + vendor.upper() + '_BIN')
            if vendor in providers and providers[vendor] != value:
                raise ValueError('mixed legacy provider context')
            providers[vendor] = value
    if len(set(contexts)) != 1 or len(set(roots)) != 1 or len(set(markers)) != 1:
        raise ValueError('mixed legacy command group')
    python, path, classifier = contexts[0]
    return roots[0], _context(dict(python=python, path=path, classifier=classifier, providers=providers)), markers[0]


def verify_legacy_group(paths, baseline=None):
    payloads = {name: _read(paths[name]) for name in COMMANDS}
    toolkit, context, marker = _legacy_context(payloads)
    if marker.startswith('# agy-'):
        baseline = baseline or json.loads(_read(ROOT / 'bin/data/agy-legacy-baseline.json'))
        assets = inventory(toolkit, baseline['inventory_scope'])
        if assets != baseline['inventory'] or digest(canonical(assets)) != baseline['inventory_serialization']['sha256']:
            raise ValueError('unsupported AGY runtime baseline')
        library = baseline['library']['approved_content_sha256']
        consumer = 'agy'
    else:
        adoption = json.loads(_read(toolkit / library_adoption.RECORD))
        if adoption.get('version') == '0.1.0.dev5':
            # The immediately preceding released Codex library is a supported
            # direct-launcher migration input, not an executable importer.
            expected = adoption.get('sha256', {})
            if (adoption.get('source_commit') != '859f27c07c1123e87b50344f587999a0cbc172a6'
                    or digest(canonical(expected)) != 'ba9eaf2991226d2438e5b207653cc5c71c6d722dd90ffe387f26542e02ee9b08'
                    or any(digest(_read(toolkit / name)) != value for name, value in expected.items())
                    or inventory(toolkit, ('bin/triad_dispatch_lib', 'vendor/triad-dispatch-lib.LICENSE')) != expected):
                raise ValueError('unsupported direct Codex library baseline')
            library = digest(canonical(expected))
        else:
            library_adoption.verify_library(toolkit)
            library = library_adoption.APPROVED_CONTENT_SHA256
        assets = inventory(toolkit)
        consumer = 'codex'
    return dict(toolkit_root=str(toolkit), context=context, launchers={n: b.decode() for n, b in payloads.items()},
                assets=assets, consumer=consumer, library_digest=library, retained=False)


def _binding(shared_root, record):
    description = dict(schema='triad-consumer-binding.v1', consumer=record['consumer'],
                       baseline_digest=digest(canonical(record['assets'])), library_digest=record['library_digest'],
                       adapter='codex-shared-v1' if record['retained'] else 'legacy-hardened-v1',
                       capabilities=CAPABILITIES, commands=list(COMMANDS), context_digest=digest(canonical(record)))
    identity = validate_consumer_binding(description).binding_id
    folder = shared_root / 'bindings' / identity
    value = dict(description=description, record=record)
    for name, source in record['launchers'].items():
        _write(folder / 'launchers' / name, source.encode(), 0o555)
    _write(folder / 'binding.json', canonical(value))
    return folder / 'binding.json'


def create_codex_binding(toolkit, launch_context, *, shared_root):
    toolkit, shared_root = _path(toolkit), _path(shared_root)
    for name in RUNTIME_REFERENCES:
        try:
            _read(toolkit / name)
        except (ValueError, OSError) as error:
            raise ValueError('missing or unsafe required runtime reference: ' + name) from error
    library_adoption.verify_library(toolkit)
    assets = inventory(toolkit)
    snapshot = shared_root / 'snapshots' / digest(canonical(assets))
    for name, expected in assets.items():
        raw = _read(toolkit / name)
        if digest(raw) != expected:
            raise ValueError('toolkit changed during snapshot')
        _write(snapshot / name, raw, 0o555 if (toolkit / name).stat().st_mode & 0o111 else 0o444)
    _write(snapshot / '.runtime-snapshot.json', canonical(assets))
    record = dict(toolkit_root=str(snapshot), context=_context(launch_context), assets=assets,
                  launchers={name: launcher_bytes(snapshot, name, launch_context).decode() for name in COMMANDS},
                  consumer='codex', library_digest=library_adoption.APPROVED_CONTENT_SHA256, retained=True)
    return _binding(shared_root, record)


def _load_binding(path, *, verify_assets=True):
    path = Path(path)
    value = _object(path)
    if set(value) != {'description', 'record'}:
        raise ValueError('unknown binding metadata')
    binding = validate_consumer_binding(value['description'])
    record = value['record']
    if (not isinstance(record, dict) or set(record) != {'toolkit_root', 'context', 'assets', 'launchers',
                                                      'consumer', 'library_digest', 'retained'}
            or type(record['retained']) is not bool
            or binding.consumer != record['consumer'] or binding.library_digest != record['library_digest']
            or binding.commands != tuple(sorted(COMMANDS)) or binding.capabilities != tuple(CAPABILITIES)
            or binding.adapter != ('codex-shared-v1' if record['retained'] else 'legacy-hardened-v1')):
        raise ValueError('binding description and authenticated record differ')
    if (path.name != 'binding.json' or path.parent.name != binding.binding_id
            or path.parent.parent.name != 'bindings' or digest(canonical(record)) != binding.context_digest
            or digest(canonical(record['assets'])) != binding.baseline_digest):
        raise ValueError('binding identity mismatch')
    _context(record['context'])
    toolkit = _path(record['toolkit_root'])
    if set(record['launchers']) != set(COMMANDS):
        raise ValueError('incomplete binding launcher inventory')
    for name, source in record['launchers'].items():
        if _read(path.parent / 'launchers' / name) != source.encode():
            raise ValueError('binding launcher changed')
    if record['retained']:
        if (toolkit != path.parent.parent.parent / 'snapshots' / binding.baseline_digest
                or _object(toolkit / '.runtime-snapshot.json') != record['assets']):
            raise ValueError('snapshot identity mismatch')
        if any(source.encode() != launcher_bytes(toolkit, name, record['context'])
               for name, source in record['launchers'].items()):
            raise ValueError('invalid retained launcher')
    if verify_assets:
        scopes = SCOPES if record['consumer'] == 'codex' else json.loads(_read(ROOT / 'bin/data/agy-legacy-baseline.json'))['inventory_scope']
        if inventory(toolkit, scopes) != record['assets']:
            raise ValueError('runtime snapshot changed')
    return binding, record


def runtime_context(binding_file):
    binding, record = _load_binding(binding_file)
    return dict(binding_file=str(binding_file), binding_id=binding.binding_id,
                binding_sha256=digest(_read(binding_file)), toolkit_root=record['toolkit_root'])


def verify_runtime_context(context, toolkit=None):
    if not isinstance(context, dict) or set(context) != {'binding_file', 'binding_id', 'binding_sha256', 'toolkit_root'}:
        raise ValueError('invalid immutable runtime context')
    if runtime_context(Path(context['binding_file'])) != context:
        raise ValueError('runtime context changed')
    if toolkit is not None and context['toolkit_root'] != str(_path(toolkit)):
        raise ValueError('runtime binding does not match executing toolkit')
    return _load_binding(Path(context['binding_file']))[1]


def context_for_toolkit(toolkit, binding_id=None):
    toolkit = _path(toolkit)
    retained = toolkit.parent.name == 'snapshots' and (toolkit / '.runtime-snapshot.json').exists()
    if binding_id is None:
        if retained:
            raise ValueError('retained toolkit requires explicit runtime_binding')
        return None
    _id(binding_id)
    if not retained:
        raise ValueError('explicit shared context conflicts with source-SOT toolkit')
    context = runtime_context(toolkit.parent.parent / 'bindings' / binding_id / 'binding.json')
    verify_runtime_context(context, toolkit)
    return context


def provider_invocation(context, command, arguments, *, log_dir=None):
    record = verify_runtime_context(context)
    if command not in COMMANDS:
        raise ValueError('unsupported shared command')
    launcher = Path(context['binding_file']).parent / 'launchers' / command
    return {'argv': [str(launcher), *arguments],
            'env': {} if log_dir is None else {'TRIAD_DISPATCH_LOG_DIR': str(log_dir)},
            'expected_wrapper_cmd': [str(Path(record['toolkit_root']) / 'bin' / command), *arguments]}


def probe_invocation(context, argv):
    record = verify_runtime_context(context)
    pins = record['context']
    if argv[0] not in pins['providers'].values():
        raise ValueError('probe executable differs from runtime pin')
    return [pins['python'], '-E', '-B', str(Path(record['toolkit_root']) / 'bin/shared_runtime.py'),
            'probe', '--binding-file', context['binding_file'], '--', *argv]


def dispatch_probe(binding_file, argv, environ):
    context = runtime_context(binding_file)
    record = verify_runtime_context(context)
    pins = record['context']
    if not argv or argv[0] not in pins['providers'].values():
        raise ValueError('probe executable differs from runtime pin')
    env = {key: value for key, value in environ.items() if key not in SCRUB and key != 'TRIAD_RUNTIME_BINDING'}
    env.update(PATH=pins['path'], TRIAD_CLASSIFIER_EXTENSION=pins['classifier'], TRIAD_REQUIRE_PINNED_VENDOR='1')
    for vendor, binary in pins['providers'].items():
        key = 'TRIAD_' + vendor.upper() + '_BIN'
        if binary is None:
            env.pop(key, None)
        else:
            env[key] = binary
    os.execve(argv[0], argv, env)


def _neutral(generation, command, python, script):
    # Exact literal-only grammar; startup isolation precedes all imports.
    return (f'#!{python} -E\n{MARKER}\nimport os\nimport sys\n'
            f'os.execv({python!r}, [{python!r}, "-E", "-B", {str(script)!r}, '
            f'"dispatch", "--generation", {str(generation)!r}, "--command", {command!r}, "--"] + sys.argv[1:])\n').encode()


def _load_generation(path):
    value = _object(path)
    if set(value) != {'runtime', 'bindings', 'legacy_binding', 'python', 'script', 'artifact_inventory'}:
        raise ValueError('unknown generation metadata')
    if Path(path).parent.name != digest(canonical(value)):
        raise ValueError('generation identity mismatch')
    runtime = validate_runtime_descriptor(value['runtime'])
    artifact_root = Path(value['script']).parent.parent
    assets = _object(artifact_root / '.runtime-snapshot.json')
    expected_artifact = {name: expected for name, expected in assets.items()
                         if name in ('bin/shared_runtime.py', 'bin/bootstrap_repair.py', 'bin/library_adoption.py')
                         or name.startswith('bin/triad_dispatch_lib/')}
    if (artifact_root.name != digest(canonical(assets))
            or value['artifact_inventory'] != expected_artifact):
        raise ValueError('incomplete runtime artifact inventory')
    if (runtime.artifact_digest != digest(canonical(value['artifact_inventory']))
            or 'bin/shared_runtime.py' not in value['artifact_inventory']
            or any(Path(name).is_absolute() or '..' in Path(name).parts
                   or digest(_read(artifact_root / name)) != expected
                   for name, expected in value['artifact_inventory'].items())):
        raise ValueError('runtime artifact identity mismatch')
    library_adoption.verify_library(artifact_root)
    bindings = []
    for identity, binding_file in value['bindings'].items():
        binding, _ = _load_binding(binding_file, verify_assets=False)
        if binding.binding_id != identity:
            raise ValueError('generation binding mismatch')
        bindings.append(binding)
    if set(value['bindings']) != set(runtime.supported_bindings):
        raise ValueError('generation inventory mismatch')
    select_consumer_binding(runtime, bindings, explicit_binding=None, legacy_binding=value['legacy_binding'])
    return value, runtime, bindings


def preflight_group(launcher_dir):
    paths = {name: Path(launcher_dir) / name for name in COMMANDS}
    states = {name: _state(path) for name, path in paths.items()}
    if all(value is None for value in states.values()):
        return states, None
    if any(value is None for value in states.values()):
        raise ValueError('partial shared command group')
    if any(MARKER.encode() in state.data for state in states.values()):
        first = next(iter(states.values())).data.decode()
        tree = ast.parse(first)
        try:
            literals = ast.literal_eval(tree.body[-1].value.args[1].left)
            generation = Path(literals[6])
        except (AttributeError, IndexError, ValueError, TypeError) as error:
            raise ValueError('unknown shared launcher grammar') from error
        value, _, _ = _load_generation(generation)
        for name, state in states.items():
            if state.data != _neutral(generation, name, value['python'], value['script']):
                raise ValueError('mixed or modified shared launcher group')
        return states, value
    return states, verify_legacy_group(paths)


def _receipt_root(root=None):
    return _path(root if root is not None else Path.home() / '.local/share/triad-codex-dispatch/installations')


def preflight_installation(launcher_dir, shared_root=None, receipt_root=None):
    _path(shared_root or Path.home() / '.local/share/triad-dispatch-runtime')
    root = _receipt_root(receipt_root)
    if root.exists():
        for path in root.iterdir():
            _receipt(path)
    return preflight_group(_path(launcher_dir))


def _receipt(path):
    value = _object(path)
    if set(value) != {'schema', 'plugin_root', 'binding_file', 'binding_sha256'} or value['schema'] != 'triad-installation.v1':
        raise ValueError('invalid installation receipt')
    if Path(path).name != digest(canonical(value)) + '.json':
        raise ValueError('installation receipt digest mismatch')
    if digest(_read(value['binding_file'])) != value['binding_sha256']:
        raise ValueError('installation binding changed')
    _load_binding(value['binding_file'])
    return value


def _matching_receipts(plugin_root, explicit_binding, receipt_root):
    plugin = str(_path(plugin_root))
    if explicit_binding is not None:
        _id(explicit_binding)
    matches = []
    root = _receipt_root(receipt_root)
    if root.exists():
        for path in sorted(root.iterdir()):
            value = _receipt(path)
            identity = Path(value['binding_file']).parent.name
            if value['plugin_root'] == plugin and (explicit_binding is None or identity == explicit_binding):
                matches.append((path, value))
    if len(matches) != 1:
        raise ValueError('missing or ambiguous installation receipt')
    return matches[0]


def resolve_installed_runtime(plugin_root, explicit_binding=None, *, receipt_root=None):
    path, value = _matching_receipts(plugin_root, explicit_binding, receipt_root)
    context = runtime_context(Path(value['binding_file']))
    return dict(binding_id=context['binding_id'], toolkit_root=context['toolkit_root'],
                launcher_dir=str(Path(value['binding_file']).parent / 'launchers'), runtime_context=context,
                provenance='authenticated-installation-receipt-v1', receipt_file=str(path))


def publish_installation(toolkit, launch_context, *, shared_root=None, receipt_root=None, launcher_dir=None):
    toolkit = _path(toolkit)
    shared_root = _path(shared_root or Path.home() / '.local/share/triad-dispatch-runtime')
    receipt_root = _receipt_root(receipt_root)
    launcher_dir = _path(launcher_dir or Path.home() / '.local/bin')
    states, existing = preflight_installation(launcher_dir, shared_root, receipt_root)
    # Validate receipt directory before any persistent publication.
    if receipt_root.exists():
        for path in receipt_root.iterdir():
            _receipt(path)
    binding_file = create_codex_binding(toolkit, launch_context, shared_root=shared_root)
    binding, record = _load_binding(binding_file)
    if existing is None:
        bindings, legacy = {}, binding.binding_id
    elif 'runtime' in existing:
        bindings, legacy = dict(existing['bindings']), existing['legacy_binding']
    else:
        old_file = _binding(shared_root, existing)
        old, _ = _load_binding(old_file)
        bindings, legacy = {old.binding_id: str(old_file)}, old.binding_id
    bindings[binding.binding_id] = str(binding_file)
    script = Path(record['toolkit_root']) / 'bin/shared_runtime.py'
    artifact_inventory = {name: expected for name, expected in record['assets'].items()
                          if name in ('bin/shared_runtime.py', 'bin/bootstrap_repair.py', 'bin/library_adoption.py')
                          or name.startswith('bin/triad_dispatch_lib/')}
    value = dict(runtime=dict(schema='triad-runtime-compat.v1', artifact_digest=digest(canonical(artifact_inventory)),
                              commands=list(COMMANDS), capabilities=CAPABILITIES, supported_bindings=sorted(bindings)),
                 bindings=bindings, legacy_binding=legacy, python=launch_context['python'],
                 script=str(script), artifact_inventory=artifact_inventory)
    generation = shared_root / 'generations' / digest(canonical(value)) / 'generation.json'
    _write(generation, canonical(value))
    _load_generation(generation)
    receipt = dict(schema='triad-installation.v1', plugin_root=str(toolkit), binding_file=str(binding_file),
                   binding_sha256=digest(_read(binding_file)))
    receipt_path = receipt_root / (digest(canonical(receipt)) + '.json')
    previous_receipt = _state(receipt_path)
    if previous_receipt is not None and previous_receipt.data != canonical(receipt):
        raise ValueError('installation receipt conflict')
    outputs = [(launcher_dir / name, _neutral(generation, name, value['python'], script), 0o755, states[name])
               for name in COMMANDS]
    if previous_receipt is None:
        outputs.append((receipt_path, canonical(receipt), 0o444, None))
    staged, journal, failure = [], [], None
    try:
        for path, data, mode, previous in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            staged.append(repair.stage(path, data, mode))
        for temp, (path, _, _, previous) in zip(staged, outputs):
            repair.publish_to(temp, path, previous, journal)
    except BaseException as error:
        failure = error
    repair.finalize_transaction(failure, journal, repair.cleanup_all(staged))
    return resolve_installed_runtime(toolkit, binding.binding_id, receipt_root=receipt_root)


def remove_installation(plugin_root, explicit_binding=None, *, receipt_root=None):
    path, value = _matching_receipts(plugin_root, explicit_binding, receipt_root)
    binding_file = Path(value['binding_file'])
    ids = [child.name for child in binding_file.parent.parent.iterdir()]
    retention = plan_runtime_retention(ids, consumer_references=[], active_references=[], dependencies_known=False)
    state = _state(path)
    journal = []
    failure = None
    try:
        repair.remove_state(state, journal)
    except BaseException as error:
        failure = error
    repair.finalize_transaction(failure, journal, [])
    return dataclasses.asdict(retention)


def dispatch(generation, command, argv, environ):
    value, descriptor, bindings = _load_generation(generation)
    binding = select_consumer_binding(descriptor, bindings,
                                     explicit_binding=environ.get('TRIAD_RUNTIME_BINDING'),
                                     legacy_binding=value['legacy_binding'])
    binding_file = Path(value['bindings'][binding.binding_id])
    _load_binding(binding_file)
    if command not in COMMANDS:
        raise ValueError('unknown runtime command')
    env = dict(environ)
    env.pop('TRIAD_RUNTIME_BINDING', None)
    launcher = str(binding_file.parent / 'launchers' / command)
    os.execve(launcher, [launcher, *argv], env)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('resolve', 'install', 'remove', 'preflight', 'dispatch', 'probe'))
    parser.add_argument('--plugin-root', type=Path)
    parser.add_argument('--binding')
    parser.add_argument('--binding-file', type=Path)
    parser.add_argument('--receipt-root', type=Path)
    parser.add_argument('--shared-root', type=Path)
    parser.add_argument('--launcher-dir', type=Path)
    parser.add_argument('--context-file', type=Path)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--generation', type=Path)
    parser.add_argument('--command', choices=COMMANDS)
    parser.add_argument('--json', action='store_true')
    raw = list(sys.argv[1:] if argv is None else argv)
    tail = raw[raw.index('--') + 1:] if '--' in raw else []
    args = parser.parse_args(raw[:raw.index('--')] if '--' in raw else raw)
    if args.operation in ('resolve', 'remove') and args.binding is None:
        args.binding = os.environ.get('TRIAD_RUNTIME_BINDING')
    try:
        if args.operation == 'probe':
            dispatch_probe(args.binding_file, tail, os.environ)
            return
        if args.operation == 'dispatch':
            dispatch(args.generation, args.command, tail, os.environ)
            return
        if args.operation == 'resolve':
            result = resolve_installed_runtime(args.plugin_root, args.binding, receipt_root=args.receipt_root)
        elif args.operation == 'remove':
            result = remove_installation(args.plugin_root, args.binding, receipt_root=args.receipt_root)
        elif args.operation == 'preflight':
            preflight_installation(args.launcher_dir, args.shared_root, args.receipt_root)
            result = {'status': 'verified'}
        else:
            if args.manifest is not None:
                artifacts = repair.command_artifacts_from_manifest(args.manifest, require_data=True)
                if len(artifacts) != len(COMMANDS) or {item.name for item in artifacts} != set(COMMANDS):
                    raise ValueError('incomplete installation manifest')
                payloads = {item.name: item.data for item in artifacts}
                source, context, marker = _legacy_context(payloads)
                if source != args.plugin_root or marker != '# triad-codex-dispatch managed launcher':
                    raise ValueError('installation manifest root mismatch')
            else:
                context = json.loads(_read(args.context_file))
            result = publish_installation(args.plugin_root, context,
                                          receipt_root=args.receipt_root, shared_root=args.shared_root,
                                          launcher_dir=args.launcher_dir)
        print(json.dumps(result, sort_keys=True))
    except (ValueError, OSError, KeyError, TypeError, repair.Refusal) as error:
        parser.exit(1, f'shared runtime refused: {error}\n')


if __name__ == '__main__':
    main()
