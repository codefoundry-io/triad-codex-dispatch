from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
sys.path.insert(0, str(BIN))

import _agy_settings as settings  # noqa: E402


BASELINE = b'{\n  "permissions": {\n    "allow": ["command(git)"],\n    "deny": ["command(sudo)"]\n  },\n  "colorScheme": "dark"\n}'


def _bind(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    target = tmp_path / "settings.json"
    monkeypatch.setenv("AGY_SETTINGS_PATH", str(target))
    return target, target.with_name(".agybak")


@pytest.mark.parametrize("payload,refused", [
    (None, False), (b'{"permissions":{"deny":[]}}', False),
    (b'{"permissions":{"deny":["read_url(*)"]}}', True),
    (b'not json', True), (b'[]', True), (b'{"permissions":null}', True),
    (b'{"permissions":{"deny":"read_url(*)"}}', True),
    (b'{"permissions":{"deny":[null]}}', True),
])
def test_requested_web_reads_only_existing_settings(tmp_path, monkeypatch, payload, refused):
    target, backup = _bind(tmp_path, monkeypatch)
    if payload is not None:
        target.write_bytes(payload)
    backup.write_bytes(b'legacy residue stays')
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    if refused:
        with pytest.raises(ValueError, match="web"):
            settings.check_web_settings()
    else:
        settings.check_web_settings()
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before
