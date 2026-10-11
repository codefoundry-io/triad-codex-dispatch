"""U7: actual wrapper calls never acquire or restore global permission state."""
import json
from pathlib import Path
import sys

import pytest

from test_antigravity_stream_json import wrapper, _run_result, _stream


@pytest.fixture
def invocation(tmp_path, monkeypatch):
    directory = tmp_path / 'operator'
    directory.mkdir()
    target = directory / 'settings.json'
    monkeypatch.setenv('AGY_SETTINGS_PATH', str(target))
    monkeypatch.delenv('AGY_SETTINGS_LOCK_TIMEOUT', raising=False)
    monkeypatch.setattr(wrapper._common, 'require_binary', lambda _: '/fixture/agy')
    monkeypatch.setattr(wrapper, '_probe_agy_version', lambda _: (1, 3, 3))
    monkeypatch.setattr(wrapper._common, 'prune_stale_run_logs', lambda _: None)
    monkeypatch.setattr(wrapper._common, 'persist_result_artifacts', lambda *a, **k: None)
    monkeypatch.delenv('AGY_NO_HEADLESS_AUTOAPPROVE', raising=False)
    args = ['antigravity_wrapper.py', '--prompt', 'inspect fixture', '--cwd', str(tmp_path)]
    monkeypatch.setattr(sys, 'argv', args)
    return target, args


@pytest.mark.parametrize('readonly', [False, True])
@pytest.mark.parametrize('state', ['absent', 'existing', 'stale', 'concurrent', 'provider-error'])
def test_c68_global_state_untouched_during_and_after_call(invocation, monkeypatch, readonly, state):
    target, args = invocation
    if readonly:
        args += ['--sandbox', 'read-only']
    if state != 'absent':
        target.write_bytes(b'{"permissions":{"deny":[]},"owner":"initial"}\n')
    if state == 'stale':
        target.with_name('.agybak').write_bytes(b'old or malformed backup belongs to the operator')
        target.with_name('.agy_settings.lock').write_bytes(b'legacy lock')
        target.with_name('.agy_settings.shared.json').write_bytes(b'legacy lease')
        holders = target.with_name('.agy_settings.holders')
        holders.mkdir()
        (holders / 'old').write_bytes(b'legacy holder')
    def snap():
        return {str(p.relative_to(target.parent)): p.read_bytes()
                for p in target.parent.rglob('*') if p.is_file()}
    before = snap()
    calls = []
    def provider(_cli, cmd, *a, **k):
        assert snap() == before
        calls.append(cmd)
        if readonly:
            assert cmd[cmd.index('--agent') + 1] == 'triad-codex-readonly-research'
            assert '--dangerously-skip-permissions' not in cmd
            assert '--sandbox' in cmd and cmd[cmd.index('--mode') + 1] == 'plan'
        else:
            assert '--agent' not in cmd
            assert '--dangerously-skip-permissions' in cmd
        if state == 'concurrent':
            target.write_bytes(b'{"owner":"intervening writer"}\n')
        return _run_result(_stream({'status':'SUCCESS','response':'answer'}),
                           rc=7 if state == 'provider-error' else 0)
    monkeypatch.setattr(wrapper._common, '_run_once', provider)
    result = wrapper.main()
    assert len(calls) == 1
    assert (result == 0) is (state != 'provider-error')
    if state == 'concurrent':
        before['settings.json'] = b'{"owner":"intervening writer"}\n'
    assert snap() == before


@pytest.mark.parametrize('version,accepted', [((1, 1, 20),False), ((1, 2, 0),False),
                                           ((1, 2, 1),True), ((1, 3, 3),True)])
def test_c72_readonly_requires_exclusion_capable_cli(invocation, monkeypatch, version, accepted):
    _, args = invocation
    args += ['--sandbox','read-only']
    monkeypatch.setattr(wrapper, '_probe_agy_version', lambda _: version)
    calls=[]
    monkeypatch.setattr(wrapper._common, '_run_once', lambda *a, **k:
        calls.append(a) or _run_result(_stream({'status':'SUCCESS','response':'ok'})))
    assert (wrapper.main() == 0) is accepted
    assert bool(calls) is accepted


@pytest.mark.parametrize('web', [False,True])
def test_c72_profile_explicit_tools_survive_exclusion(web):
    import _agy_agent
    _, raw = _agy_agent.profile(web)
    text = raw.decode()
    assert 'excludeDefaultComponents: true' in text
    for tool in ('view_file','grep_search','list_dir','find_by_name','finish'):
        assert '\n  - '+tool+'\n' in text
    assert ('\n  - search_web\n' in text) is web
    assert ('\n  - read_url_content\n' in text) is web
    assert 'inheritCustomizations: false' not in text


def test_c72_raw_readonly_missing_profile_refuses_before_provider(invocation, monkeypatch):
    _, args=invocation
    args += ['--sandbox','read-only']
    def missing(*a,**k):
        raise ValueError('AGY profile missing')
    monkeypatch.setattr(wrapper._agy_agent,'controls',missing)
    monkeypatch.setattr(wrapper._common,'_run_once',lambda *a,**k: pytest.fail('provider started'))
    assert wrapper.main() == wrapper._common.EXIT_TERMINAL


def test_c68_retired_lock_timeout_does_not_affect_dispatch(invocation, monkeypatch):
    monkeypatch.setenv('AGY_SETTINGS_LOCK_TIMEOUT', 'not-a-number')
    calls=[]
    monkeypatch.setattr(wrapper._common,'_run_once',lambda *a,**k:
        calls.append(a) or _run_result(_stream({'status':'SUCCESS','response':'ok'})))
    assert wrapper.main() == 0
    assert len(calls) == 1
