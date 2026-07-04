import multiprocessing as mp
import os
import pytest
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))

import _agy_settings  # noqa: E402


def _guard_worker(settings_path, deny_rules, entered, release, result, hold):
    os.environ["AGY_SETTINGS_PATH"] = str(settings_path)
    try:
        with _agy_settings.agy_settings_guard(deny_rules, lock_timeout=0.75):
            entered.set()
            if hold:
                release.wait(5)
        result.put("ok")
    except Exception as exc:  # pragma: no cover - asserted through queue text
        result.put(f"{type(exc).__name__}: {exc}")


def test_read_only_transactions_share_settings_lease(tmp_path):
    ctx = mp.get_context("spawn")
    settings_path = tmp_path / "settings.json"
    first_entered = ctx.Event()
    first_release = ctx.Event()
    first_result = ctx.Queue()
    first = ctx.Process(
        target=_guard_worker,
        args=(
            settings_path,
            _agy_settings.build_deny_rules("read-only"),
            first_entered,
            first_release,
            first_result,
            True,
        ),
    )
    first.start()
    try:
        assert first_entered.wait(5), "first read-only transaction did not enter"

        second_entered = ctx.Event()
        second_release = ctx.Event()
        second_result = ctx.Queue()
        second = ctx.Process(
            target=_guard_worker,
            args=(
                settings_path,
                _agy_settings.build_deny_rules("read-only"),
                second_entered,
                second_release,
                second_result,
                False,
            ),
        )
        second.start()
        try:
            assert second_entered.wait(2), (
                "same read-only deny rules should share the active settings lease"
            )
            second.join(2)
            assert not second.is_alive()
            assert second_result.get(timeout=1) == "ok"
        finally:
            if second.is_alive():
                second.terminate()
                second.join(2)
    finally:
        first_release.set()
        first.join(2)
        if first.is_alive():
            first.terminate()
            first.join(2)

    assert first_result.get(timeout=1) == "ok"
    assert not settings_path.exists()
    assert not settings_path.with_name(".agybak").exists()
    assert not settings_path.with_name(".agy_settings.shared.json").exists()


def test_dead_coholder_is_pruned_when_last_live_holder_releases(tmp_path):
    ctx = mp.get_context("spawn")
    settings_path = tmp_path / "settings.json"
    deny_rules = _agy_settings.build_deny_rules("read-only")

    first_entered = ctx.Event()
    first_release = ctx.Event()
    first_result = ctx.Queue()
    first = ctx.Process(
        target=_guard_worker,
        args=(settings_path, deny_rules, first_entered, first_release, first_result, True),
    )
    first.start()
    try:
        assert first_entered.wait(5), "first read-only transaction did not enter"

        second_entered = ctx.Event()
        second_release = ctx.Event()
        second_result = ctx.Queue()
        second = ctx.Process(
            target=_guard_worker,
            args=(
                settings_path,
                deny_rules,
                second_entered,
                second_release,
                second_result,
                True,
            ),
        )
        second.start()
        try:
            assert second_entered.wait(2), "second read-only transaction did not enter"

            first.terminate()
            first.join(2)
            assert not first.is_alive()

            second_release.set()
            second.join(2)
            assert not second.is_alive()
            assert second_result.get(timeout=1) == "ok"
        finally:
            if second.is_alive():
                second_release.set()
                second.terminate()
                second.join(2)
    finally:
        if first.is_alive():
            first_release.set()
            first.terminate()
            first.join(2)

    assert not settings_path.exists()
    assert not settings_path.with_name(".agybak").exists()
    assert not settings_path.with_name(".agy_settings.shared.json").exists()


def test_workspace_write_waits_for_active_read_only_lease(tmp_path):
    ctx = mp.get_context("spawn")
    settings_path = tmp_path / "settings.json"
    first_entered = ctx.Event()
    first_release = ctx.Event()
    first_result = ctx.Queue()
    first = ctx.Process(
        target=_guard_worker,
        args=(
            settings_path,
            _agy_settings.build_deny_rules("read-only"),
            first_entered,
            first_release,
            first_result,
            True,
        ),
    )
    first.start()
    try:
        assert first_entered.wait(5), "first read-only transaction did not enter"

        second_entered = ctx.Event()
        second_release = ctx.Event()
        second_result = ctx.Queue()
        second = ctx.Process(
            target=_guard_worker,
            args=(
                settings_path,
                _agy_settings.build_deny_rules("workspace-write"),
                second_entered,
                second_release,
                second_result,
                False,
            ),
        )
        second.start()
        try:
            assert not second_entered.wait(1), (
                "workspace-write must not share a read-only settings lease"
            )
            second.join(2)
            assert not second.is_alive()
            assert second_result.get(timeout=1).startswith("TimeoutError:")
        finally:
            if second.is_alive():
                second.terminate()
                second.join(2)
    finally:
        first_release.set()
        first.join(2)
        if first.is_alive():
            first.terminate()
            first.join(2)

    assert first_result.get(timeout=1) == "ok"


def test_read_only_entry_failure_after_merge_restores_settings(tmp_path, monkeypatch):
    settings_path = tmp_path / "settings.json"
    original_atomic_write = _agy_settings._atomic_write

    def fail_state_write(path, text):
        if Path(path).name == ".agy_settings.shared.json":
            raise OSError("state write failed")
        original_atomic_write(path, text)

    monkeypatch.setenv("AGY_SETTINGS_PATH", str(settings_path))
    monkeypatch.setattr(_agy_settings, "_atomic_write", fail_state_write)

    with pytest.raises(OSError, match="state write failed"):
        with _agy_settings.agy_settings_guard(
            _agy_settings.build_deny_rules("read-only"),
            lock_timeout=0.75,
        ):
            pass

    assert not settings_path.exists()
    assert not settings_path.with_name(".agybak").exists()
    assert not settings_path.with_name(".agy_settings.shared.json").exists()


def test_release_timeout_preserves_original_body_exception(tmp_path, monkeypatch):
    settings_path = tmp_path / "settings.json"
    calls = 0
    original_lock_until = _agy_settings._lock_until

    def fail_release_lock(lock_fd, deadline):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise TimeoutError("release lock timeout")
        original_lock_until(lock_fd, deadline)

    monkeypatch.setenv("AGY_SETTINGS_PATH", str(settings_path))
    monkeypatch.setattr(_agy_settings, "_lock_until", fail_release_lock)

    with pytest.raises(ValueError, match="body failed"):
        with _agy_settings.agy_settings_guard(
            _agy_settings.build_deny_rules("read-only"),
            lock_timeout=0.75,
        ):
            raise ValueError("body failed")


def test_release_timeout_keeps_holder_file_for_future_cleanup(tmp_path, monkeypatch):
    settings_path = tmp_path / "settings.json"
    calls = 0
    original_lock_until = _agy_settings._lock_until

    def fail_first_release_lock(lock_fd, deadline):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise TimeoutError("release lock timeout")
        original_lock_until(lock_fd, deadline)

    monkeypatch.setenv("AGY_SETTINGS_PATH", str(settings_path))
    monkeypatch.setattr(_agy_settings, "_lock_until", fail_first_release_lock)

    with pytest.raises(TimeoutError, match="release lock timeout"):
        with _agy_settings.agy_settings_guard(
            _agy_settings.build_deny_rules("read-only"),
            lock_timeout=0.75,
        ):
            pass

    holders_dir = settings_path.with_name(".agy_settings.holders")
    assert list(holders_dir.glob("*.lock"))
    assert settings_path.exists()

    monkeypatch.setattr(_agy_settings, "_lock_until", original_lock_until)
    with _agy_settings.agy_settings_guard(
        _agy_settings.build_deny_rules("read-only"),
        lock_timeout=0.75,
    ):
        pass

    assert not settings_path.exists()
    assert not settings_path.with_name(".agybak").exists()
    assert not settings_path.with_name(".agy_settings.shared.json").exists()


def test_corrupt_shared_state_file_self_heals_from_backup(tmp_path, monkeypatch):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(
        '{"permissions": {"deny": ["write_file(*)"]}}',
        encoding="utf-8",
    )
    settings_path.with_name(".agybak").write_text(
        '{"existed": false, "content": ""}',
        encoding="utf-8",
    )
    settings_path.with_name(".agy_settings.shared.json").write_text(
        "{not-json",
        encoding="utf-8",
    )

    monkeypatch.setenv("AGY_SETTINGS_PATH", str(settings_path))
    with _agy_settings.agy_settings_guard(
        _agy_settings.build_deny_rules("read-only"),
        lock_timeout=0.75,
    ):
        assert settings_path.exists()

    assert not settings_path.exists()
    assert not settings_path.with_name(".agybak").exists()
    assert not settings_path.with_name(".agy_settings.shared.json").exists()
