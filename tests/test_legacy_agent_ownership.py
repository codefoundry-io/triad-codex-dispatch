"""Bootstrap must prove full legacy-agent content before removal or quarantine.

Historical agent files are inert fixtures, never executable agent configuration.
"""
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bin'))
import bootstrap_repair as helper

FIXTURES = ROOT / 'tests/fixtures/legacy-agents'
ORIGINALS = sorted([*FIXTURES.glob('307745f-*.toml'), *FIXTURES.glob('dca0cd4-*.toml')])
assert len(ORIGINALS) == 6


def act(path, operation, tmp_path):
    if operation == 'remove':
        return helper.remove_managed_artifact(path, 'legacy-agent')
    return helper.quarantine_managed_artifact(path, 'legacy-agent',
                                              quarantine_parent=tmp_path)


@pytest.mark.parametrize('operation', ['remove', 'quarantine'])
@pytest.mark.parametrize('original', ORIGINALS, ids=lambda path: path.stem)
def test_complete_historical_payloads_remain_owned(tmp_path, original, operation):
    target = tmp_path / original.name
    payload = original.read_bytes()
    target.write_bytes(payload)
    assert act(target, operation, tmp_path) == ('removed' if operation == 'remove' else 'quarantined')
    assert not target.exists()
    if operation == 'quarantine':
        saved = list(tmp_path.glob('.triad-quarantine-*/*'))
        assert len(saved) == 1 and saved[0].read_bytes() == payload


@pytest.mark.parametrize('operation', ['remove', 'quarantine'])
@pytest.mark.parametrize('original', ORIGINALS, ids=lambda path: path.stem)
def test_owner_addition_preserves_the_whole_file(tmp_path, original, operation):
    target = tmp_path / original.name
    payload = original.read_bytes() + b'\n# owner addition must survive\n'
    target.write_bytes(payload)
    target.chmod(0o604)
    assert act(target, operation, tmp_path) == 'unmanaged'
    assert target.read_bytes() == payload and target.stat().st_mode & 0o777 == 0o604
    assert not list(tmp_path.glob('.triad-quarantine-*'))


@pytest.mark.parametrize('operation', ['remove', 'quarantine'])
@pytest.mark.parametrize('variant', ['body-edit', 'crlf', 'header-only', 'truncated', 'invalid-utf8', 'rendered'])
def test_headers_do_not_establish_ownership(tmp_path, variant, operation):
    payload = ORIGINALS[0].read_bytes()
    if variant == 'body-edit':
        payload = payload.replace(b'model_reasoning_effort = "high"', b'model_reasoning_effort = "low"')
        assert payload != ORIGINALS[0].read_bytes()
    elif variant == 'crlf':
        payload = payload.replace(b'\n', b'\r\n')
    elif variant == 'header-only':
        payload = (b'# Codex named subagent for Claude wrapper repair agent\n'
                   b'# Installed by bootstrap to the Codex personal agent-discovery scope\n'
                   b'name = "owner-controlled"\n')
    elif variant == 'truncated':
        payload = b''.join(payload.splitlines(keepends=True)[:5])
    elif variant == 'invalid-utf8':
        payload += b'\xff'
    else:
        payload = (FIXTURES / 'rendered-template.toml').read_bytes()
        for key, value in {
            b'__TRIAD_CLASSIFIER_PATH__': b'/example/config/classifier-patches.json',
            b'__TRIAD_CLASSIFIER_DIR__': b'/example/config',
            b'__TRIAD_REPO_ROOT__': b'/example/triad',
            b'__TRIAD_PYTHON3__': b'/example/python3',
            b'"__TRIAD_PYTHON_READ_ROOTS__" = "read"': b'"/example/python" = "read"',
            b'"__TRIAD_VENDOR_READ_ROOTS__" = "read"': b'"/example/vendor" = "read"',
        }.items():
            payload = payload.replace(key, value)
        assert b'__TRIAD_' not in payload
        assert tomllib.loads(payload.decode())['name'] == 'claude-wrapper-repair'
    target = tmp_path / 'claude-wrapper-repair.toml'
    target.write_bytes(payload)
    assert act(target, operation, tmp_path) == 'unmanaged'
    assert target.read_bytes() == payload
    assert not list(tmp_path.glob('.triad-quarantine-*'))
