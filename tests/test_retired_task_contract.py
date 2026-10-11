"""DL-91: retired task failures cannot become active classifier repairs."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bin'))
import _common


@pytest.mark.parametrize('cli', ['claude', 'gemini'])
@pytest.mark.parametrize('phrase', ['spawn_agent failed', 'agent quota exceeded',
                                   'could not spawn subagent'])
def test_retired_fanout_phrase_is_not_a_terminal_diagnosis(cli, phrase, monkeypatch):
    monkeypatch.setattr(_common, '_load_classifier_extension', lambda: {})
    assert _common.classify(cli, phrase, '', 1, vendor_exit_code=7) == 'unknown'


@pytest.mark.parametrize('cli', ['claude', 'gemini'])
def test_retired_pattern_is_ignored_without_rewriting_extension(cli, tmp_path, monkeypatch):
    path = tmp_path / 'extension.json'
    original = json.dumps({cli: {'patterns': {
        'FANOUT_SPAWN_PATTERNS': ['retired fixture failure'],
        'SERVER_CAPACITY_PATTERNS': ['valid capacity fixture']}}})
    path.write_text(original)
    monkeypatch.setattr(_common, '_classifier_extension_path', lambda: path)
    assert _common.classify(cli, 'retired fixture failure', '', 1, vendor_exit_code=7) == 'unknown'
    assert _common.classify(cli, 'valid capacity fixture', '', 1, vendor_exit_code=7) == 'server-capacity'
    assert path.read_text() == original


@pytest.mark.parametrize('cli', ['claude', 'gemini'])
def test_retired_pattern_proposal_is_refused_without_write(cli, tmp_path):
    path = tmp_path / 'extension.json'
    path.write_text('{}\n')
    proposal = {'classification': 'fanout-spawn-error', 'reason': 'Retired task fixture',
                'pattern_list': 'FANOUT_SPAWN_PATTERNS', 'substring': 'retired fixture failure'}
    with pytest.raises(ValueError):
        _common.apply_classifier_patch(cli, proposal, extension_path=path)
    assert path.read_text() == '{}\n'
