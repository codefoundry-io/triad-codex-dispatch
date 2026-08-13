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


def test_read_only_rules_match_the_deployed_claude_wrapper() -> None:
    assert settings.build_deny_rules("read-only") == [
        "write_file(*)",
        "command(*)",
        "unsandboxed(*)",
        "execute_url(*)",
        "mcp(*)",
    ]
    with pytest.raises(ValueError, match="unknown sandbox mode"):
        settings.build_deny_rules("workspace-write")


def test_absent_settings_are_created_for_the_lease_then_removed(
    tmp_path: Path, monkeypatch
) -> None:
    target, backup = _bind(tmp_path, monkeypatch)

    with settings.agy_settings_guard(settings._READ_ONLY_DENY):
        assert (
            json.loads(target.read_text())["permissions"]["deny"]
            == settings._READ_ONLY_DENY
        )
        assert backup.exists()

    assert not target.exists()
    assert not backup.exists()


def test_present_settings_are_unioned_then_restored_byte_exactly(
    tmp_path: Path, monkeypatch
) -> None:
    target, backup = _bind(tmp_path, monkeypatch)
    target.write_bytes(BASELINE)

    with settings.agy_settings_guard(settings._READ_ONLY_DENY):
        live = json.loads(target.read_text())
        assert live["permissions"]["allow"] == ["command(git)"]
        assert set(live["permissions"]["deny"]) == {
            "command(sudo)",
            *settings._READ_ONLY_DENY,
        }
        assert live["colorScheme"] == "dark"

    assert target.read_bytes() == BASELINE
    assert not backup.exists()


def test_stale_absent_origin_sentinel_is_recovered_before_entry(
    tmp_path: Path, monkeypatch
) -> None:
    target, backup = _bind(tmp_path, monkeypatch)
    target.write_bytes(BASELINE)
    backup.write_text(json.dumps({"existed": False, "content": ""}))

    with settings.agy_settings_guard(settings._READ_ONLY_DENY):
        pass

    assert not target.exists()
    assert not backup.exists()


def test_empty_lease_is_noop_and_heals_a_stale_sentinel(
    tmp_path: Path, monkeypatch
) -> None:
    target, backup = _bind(tmp_path, monkeypatch)
    with settings.agy_settings_guard([]):
        assert not target.exists()
    target.write_bytes(BASELINE)
    backup.write_text(json.dumps({"existed": False, "content": ""}))

    with settings.agy_settings_guard([]):
        pass

    assert not target.exists()
    assert not backup.exists()


def test_body_exception_still_restores_original_bytes(
    tmp_path: Path, monkeypatch
) -> None:
    target, backup = _bind(tmp_path, monkeypatch)
    target.write_bytes(BASELINE)

    with pytest.raises(RuntimeError, match="boom"):
        with settings.agy_settings_guard(settings._READ_ONLY_DENY):
            raise RuntimeError("boom")

    assert target.read_bytes() == BASELINE
    assert not backup.exists()


def test_corrupt_sentinel_is_dropped_without_sticking_the_guard(
    tmp_path: Path, monkeypatch
) -> None:
    target, backup = _bind(tmp_path, monkeypatch)
    target.write_bytes(BASELINE)
    backup.write_text("{ invalid")

    with settings.agy_settings_guard([]):
        pass

    assert target.read_bytes() == BASELINE
    assert not backup.exists()


def test_valid_sentinel_survives_a_recovery_failure(
    tmp_path: Path, monkeypatch
) -> None:
    target, backup = _bind(tmp_path, monkeypatch)
    backup.write_text(json.dumps({"existed": True, "content": BASELINE.decode()}))
    monkeypatch.setattr(
        settings,
        "_restore",
        lambda *_a, **_k: (_ for _ in ()).throw(OSError("transient restore failure")),
    )

    with pytest.raises(OSError, match="transient restore failure"):
        settings._crash_recover(target, backup)

    assert backup.exists()


def test_atomic_write_persists_a_large_complete_payload(tmp_path: Path) -> None:
    target = tmp_path / "large.json"
    payload = '{"k":"' + ("z" * 300_000) + '"}'

    settings._atomic_write(target, payload)

    assert target.read_text() == payload
