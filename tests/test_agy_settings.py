from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))

import _agy_settings  # noqa: E402


_TRANSACTION_ARTIFACTS = (
    "settings.json",
    ".agybak",
    ".agy_settings.shared.json",
)


@pytest.mark.parametrize("target_exists", (True, False))
def test_guard_rejects_symlink_settings_before_transaction(
    tmp_path: Path,
    monkeypatch,
    target_exists: bool,
) -> None:
    settings = tmp_path / "settings.json"
    target = tmp_path / "owner-settings.json"
    original = b'{"owner": true}\n'
    if target_exists:
        target.write_bytes(original)
    settings.symlink_to(target)
    before = {entry.name for entry in tmp_path.iterdir()}
    monkeypatch.setenv("AGY_SETTINGS_PATH", str(settings))

    with pytest.raises(OSError, match="symbolic link"):
        with _agy_settings.agy_settings_guard(_agy_settings._READ_ONLY_DENY):
            pass

    assert settings.is_symlink()
    assert {entry.name for entry in tmp_path.iterdir()} == before
    if target_exists:
        assert target.read_bytes() == original


@pytest.mark.parametrize("artifact_name", _TRANSACTION_ARTIFACTS)
@pytest.mark.parametrize("foreign_kind", ("symlink", "fifo", "hardlink"))
def test_atomic_write_ignores_predictable_nonregular_or_foreign_temp_leaf(
    tmp_path: Path,
    artifact_name: str,
    foreign_kind: str,
) -> None:
    artifact = tmp_path / artifact_name
    artifact.write_bytes(b"before")
    predictable_temp = artifact.with_name(artifact.name + ".tmp")
    foreign = tmp_path / f"foreign-{foreign_kind}-{artifact.name.lstrip('.')}"
    reader_fd: int | None = None

    if foreign_kind == "symlink":
        foreign.write_bytes(b"foreign")
        predictable_temp.symlink_to(foreign)
    elif foreign_kind == "fifo":
        os.mkfifo(predictable_temp)
        reader_fd = os.open(predictable_temp, os.O_RDONLY | os.O_NONBLOCK)
    else:
        foreign.write_bytes(b"foreign")
        os.link(foreign, predictable_temp)

    try:
        _agy_settings._atomic_write(artifact, "after")
    finally:
        if reader_fd is not None:
            os.close(reader_fd)

    assert stat.S_ISREG(artifact.lstat().st_mode)
    assert artifact.read_bytes() == b"after"
    if foreign_kind == "fifo":
        assert stat.S_ISFIFO(predictable_temp.lstat().st_mode)
    else:
        assert foreign.read_bytes() == b"foreign"
        assert predictable_temp.read_bytes() == b"foreign"


def test_atomic_write_uses_exclusive_nofollow_cloexec_directory_relative_open(
    tmp_path: Path, monkeypatch
) -> None:
    artifact = tmp_path / "settings.json"
    real_open = os.open
    created: list[tuple[object, int, int | None]] = []

    def recording_open(
        path,
        flags: int,
        mode: int = 0o777,
        *,
        dir_fd: int | None = None,
    ) -> int:
        if flags & os.O_CREAT and flags & os.O_EXCL:
            created.append((path, flags, dir_fd))
        return real_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(_agy_settings.os, "open", recording_open)

    _agy_settings._atomic_write(artifact, "content")

    assert len(created) == 1
    temp_name, flags, dir_fd = created[0]
    required = os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC
    assert flags & required == required
    assert dir_fd is not None
    assert Path(os.fspath(temp_name)).name == os.fspath(temp_name)


def test_atomic_write_bounds_exclusive_name_collisions(
    tmp_path: Path, monkeypatch
) -> None:
    artifact = tmp_path / "settings.json"
    artifact.write_bytes(b"before")
    foreign = tmp_path / "foreign"
    foreign.write_bytes(b"foreign")
    fixed_hex = "0" * 32
    candidate = tmp_path / f"{artifact.name}.tmp.{os.getpid()}.{fixed_hex}"
    candidate.symlink_to(foreign)
    calls = 0

    class FixedUuid:
        hex = fixed_hex

    def repeated_uuid() -> FixedUuid:
        nonlocal calls
        calls += 1
        if calls > 64:
            raise AssertionError("exclusive temp creation retried without a bound")
        return FixedUuid()

    monkeypatch.setattr(_agy_settings.uuid, "uuid4", repeated_uuid)

    with pytest.raises(FileExistsError):
        _agy_settings._atomic_write(artifact, "after")

    assert calls <= 64
    assert artifact.read_bytes() == b"before"
    assert candidate.is_symlink()
    assert foreign.read_bytes() == b"foreign"


def test_atomic_write_retries_short_descriptor_writes(
    tmp_path: Path, monkeypatch
) -> None:
    artifact = tmp_path / "settings.json"
    real_write = os.write
    write_sizes: list[int] = []

    def short_write(fd: int, data) -> int:
        write_sizes.append(len(data))
        return real_write(fd, data[:2])

    monkeypatch.setattr(_agy_settings.os, "write", short_write)

    _agy_settings._atomic_write(artifact, "abcdefgh")

    assert artifact.read_bytes() == b"abcdefgh"
    assert len(write_sizes) > 1


def test_atomic_write_refuses_replaced_temp_inode_before_publication(
    tmp_path: Path, monkeypatch
) -> None:
    artifact = tmp_path / "settings.json"
    artifact.write_bytes(b"before")
    held = tmp_path / "held-created-inode"
    real_fsync = os.fsync
    swapped: dict[str, Path] = {}

    def fsync_then_replace(fd: int) -> None:
        real_fsync(fd)
        if swapped:
            return
        candidates = [
            child
            for child in tmp_path.iterdir()
            if child.name.startswith(artifact.name + ".tmp")
        ]
        assert len(candidates) == 1
        candidate = candidates[0]
        candidate.rename(held)
        candidate.write_bytes(b"foreign replacement")
        swapped["candidate"] = candidate

    monkeypatch.setattr(_agy_settings.os, "fsync", fsync_then_replace)

    with pytest.raises(OSError):
        _agy_settings._atomic_write(artifact, "after")

    assert artifact.read_bytes() == b"before"
    assert held.read_bytes() == b"after"
    assert swapped["candidate"].read_bytes() == b"foreign replacement"


def test_atomic_write_cleans_only_its_created_inode_after_failure(
    tmp_path: Path, monkeypatch
) -> None:
    artifact = tmp_path / "settings.json"
    artifact.write_bytes(b"before")
    real_fsync = os.fsync

    def fail_file_fsync(fd: int) -> None:
        if stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError("injected file fsync failure")
        real_fsync(fd)

    monkeypatch.setattr(_agy_settings.os, "fsync", fail_file_fsync)

    with pytest.raises(OSError, match="injected file fsync failure"):
        _agy_settings._atomic_write(artifact, "after")

    assert artifact.read_bytes() == b"before"
    assert list(tmp_path.iterdir()) == [artifact]


def test_atomic_write_preserves_foreign_replacement_when_publication_fails(
    tmp_path: Path, monkeypatch
) -> None:
    artifact = tmp_path / "settings.json"
    artifact.write_bytes(b"before")
    replaced: dict[str, Path] = {}

    def replace_with_foreign_then_fail(
        source,
        destination,
        *,
        src_dir_fd: int | None = None,
        dst_dir_fd: int | None = None,
    ) -> None:
        del destination, dst_dir_fd
        candidate = tmp_path / os.fspath(source)
        if src_dir_fd is None:
            candidate = Path(source)
        candidate.unlink()
        candidate.write_bytes(b"foreign replacement")
        replaced["candidate"] = candidate
        raise OSError("injected publication failure")

    monkeypatch.setattr(_agy_settings.os, "replace", replace_with_foreign_then_fail)

    with pytest.raises(OSError, match="injected publication failure"):
        _agy_settings._atomic_write(artifact, "after")

    candidate = replaced["candidate"]
    assert candidate.name != artifact.name + ".tmp"
    assert candidate.read_bytes() == b"foreign replacement"
    assert artifact.read_bytes() == b"before"


def test_shared_guard_restore_ignores_predictable_settings_temp_symlink(
    tmp_path: Path,
) -> None:
    settings = tmp_path / "settings.json"
    original = b'{"original": true}\n'
    settings.write_bytes(original)
    backup = tmp_path / ".agybak"
    lock = tmp_path / ".agy_settings.lock"
    predictable_temp = tmp_path / "settings.json.tmp"
    foreign = tmp_path / "foreign-settings"

    with _agy_settings._shared_readonly_guard(
        settings,
        backup,
        lock,
        _agy_settings._READ_ONLY_DENY,
        0.5,
    ):
        foreign.write_bytes(b"foreign")
        predictable_temp.symlink_to(foreign)

    assert settings.read_bytes() == original
    assert foreign.read_bytes() == b"foreign"
    assert predictable_temp.is_symlink()
    assert not backup.exists()
    assert not _agy_settings._shared_state_path(settings).exists()


def test_shared_guard_restores_backup_when_deny_installation_raises(
    tmp_path: Path, monkeypatch
) -> None:
    settings = tmp_path / "settings.json"
    original = b'{"original": true}\n'
    settings.write_bytes(original)
    backup = tmp_path / ".agybak"
    lock = tmp_path / ".agy_settings.lock"

    def changed_then_fails(path: Path, _deny_rules: list) -> None:
        path.write_bytes(b'{"permissions": {"deny": ["write_file(*)"]}}\n')
        raise OSError("deny installation failed")

    monkeypatch.setattr(_agy_settings, "_merge_deny", changed_then_fails)

    with pytest.raises(OSError, match="deny installation failed"):
        with _agy_settings._shared_readonly_guard(
            settings,
            backup,
            lock,
            _agy_settings._READ_ONLY_DENY,
            0.5,
        ):
            pass

    assert settings.read_bytes() == original
    assert not backup.exists()


def test_shared_guard_restores_crlf_settings_bytes(tmp_path: Path) -> None:
    settings = tmp_path / "settings.json"
    original = b'{"original": true}\r\n'
    settings.write_bytes(original)
    backup = tmp_path / ".agybak"
    lock = tmp_path / ".agy_settings.lock"

    with _agy_settings._shared_readonly_guard(
        settings,
        backup,
        lock,
        _agy_settings._READ_ONLY_DENY,
        0.5,
    ):
        pass

    assert settings.read_bytes() == original


def test_shared_guard_preserves_deny_error_when_restore_also_fails(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    settings = tmp_path / "settings.json"
    settings.write_bytes(b'{"original": true}\n')
    backup = tmp_path / ".agybak"
    lock = tmp_path / ".agy_settings.lock"

    monkeypatch.setattr(
        _agy_settings,
        "_merge_deny",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("deny failed")),
    )
    monkeypatch.setattr(
        _agy_settings,
        "_restore",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("restore failed")),
    )

    with pytest.raises(OSError, match="deny failed"):
        with _agy_settings._shared_readonly_guard(
            settings,
            backup,
            lock,
            _agy_settings._READ_ONLY_DENY,
            0.5,
        ):
            pass

    assert backup.exists()
    assert "restore failed after entry error: restore failed" in capsys.readouterr().err
