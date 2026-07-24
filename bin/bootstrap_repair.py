#!/usr/bin/env python3
from __future__ import annotations
import ast
import argparse
import json
import os
import shlex
import stat
import sys
import tempfile
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path

NAME = "triad-repair-analyzer"
ANALYZER_MARKER = "# triad-codex-dispatch managed repair analyzer"
REG_BEGIN = "# >>> triad-codex-dispatch managed repair analyzer registration >>>"
REG_END = "# <<< triad-codex-dispatch managed repair analyzer registration <<<"
LAUNCHER = "triad-apply-repair"
LAUNCHER_MARKER = "# triad-codex-dispatch managed repair apply launcher"
REG_DESCRIPTION = "Read-only triad repair analyzer for untrusted vendor run logs."
PROFILE_MARKER = b"# triad-codex-dispatch managed runtime profile"
RULES_MARKER = b"# triad-codex-dispatch managed command rules"
PUBLIC_LAUNCHER_MARKER = b"# triad-codex-dispatch managed launcher"
PUBLIC_RUNTIME_MARKER = b"# triad-codex-dispatch managed runtime command"
CONFIG_FRAGMENT_BEGIN = (
    b"# >>> triad-codex-dispatch managed shell_environment_policy >>>"
)
CONFIG_FRAGMENT_END = (
    b"# <<< triad-codex-dispatch managed shell_environment_policy <<<"
)
CONFIG_FRAGMENT_INSERTED_SEPARATOR = (
    b"\n# triad-codex-dispatch managed inserted separator\n"
)
SHELL_ENTRY_BEGIN = b"# >>> triad-codex-dispatch codex-triad >>>"
SHELL_ENTRY_END = b"# <<< triad-codex-dispatch codex-triad <<<"
CURRENT_CONFIG_FRAGMENT_TEXT = (
    b"[shell_environment_policy]\n"
    b'inherit = "all"\n'
    b'exclude = ["LD_*", "DYLD_*", "NODE_OPTIONS", "NODE_PATH", "PYTHON*", '
    b'"BASH_ENV", "ENV", "PERL5LIB", "RUBYOPT", "RUBYLIB"]\n'
)
LEGACY_CONFIG_FRAGMENT_TEXT = (
    b"[shell_environment_policy]\n"
    b'inherit = "core"\n'
)
LEGACY_AGENT_HEADER_A = "# Codex named subagent"
LEGACY_AGENT_HEADER_B = "wrapper repair agent"
LEGACY_AGENT_SCOPE = "Installed by bootstrap to the Codex personal agent-discovery scope"

class Refusal(RuntimeError):
    pass


class MissingExpected(Refusal):
    pass


@dataclass(frozen=True)
class State:
    path: Path
    data: bytes
    mode: int
    ident: tuple[int, int, int, int, int]


@dataclass(frozen=True)
class Staged:
    state: State

    @property
    def path(self) -> Path:
        return self.state.path

    def __fspath__(self) -> str:
        return os.fspath(self.path)

    def unlink(self, *, missing_ok: bool = False) -> None:
        """Path compatibility for callers that explicitly discard a stage."""
        if missing_ok and _path_is_absent(self.path):
            return
        _delete_expected(self.state)


@dataclass(frozen=True)
class CommandArtifact:
    """One public executable managed as part of an all-or-nothing group."""

    name: str
    target: Path
    data: bytes
    kind: str
    mode: int = 0o755


@dataclass(frozen=True)
class RepairInstallPlan:
    source_state: State
    apply_state: State
    runtime_state: State
    config: Path
    analyzer: Path
    launcher: Path
    config_before: State | None
    analyzer_before: State | None
    launcher_before: State | None
    config_data: bytes
    launcher_data: bytes


@dataclass(frozen=True)
class RepairRemovePlan:
    config: Path
    analyzer: Path
    launcher: Path
    config_before: State | None
    analyzer_before: State | None
    launcher_before: State | None
    base: str
    managed_registration: bool
    original_config_existed: bool


@dataclass
class Mutation:
    target: Path
    before: State | None
    after: State | None
    backup: State | None = None
    backup_dir: Path | None = None


class TransactionFailure(Refusal):
    def __init__(self, cause: BaseException, failures: list[BaseException]) -> None:
        super().__init__(f"{cause}; recovery failures: " + "; ".join(map(str, failures)))
        self.cause = cause
        self.failures = failures


def _ident(st: os.stat_result) -> tuple[int, int, int, int, int]:
    return (st.st_dev, st.st_ino, st.st_mode, st.st_size, st.st_mtime_ns)


def require_safe_ancestors(path: Path) -> None:
    """Reject an existing symlink or non-directory above a managed leaf.

    Bootstrap canonicalizes its trusted roots before calling this helper. This
    walk preserves that spelling and deliberately does not resolve an
    intermediate symlink: an `agents/` link must not redirect repair state
    outside the selected Codex home. Missing suffix components are allowed so
    a later transactional install can create its own parent directory.
    """
    if not path.is_absolute():
        raise Refusal(f"managed path must be absolute: {path}")
    parent = path.parent
    current = Path(parent.anchor)
    parts = parent.parts[1:] if parent.anchor else parent.parts
    for component in parts:
        current /= component
        try:
            status = os.lstat(current)
        except FileNotFoundError:
            return
        except OSError as error:
            raise Refusal(f"could not inspect ancestor for {path}: {current}") from error
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
            raise Refusal(f"refusing unsafe ancestor for {path}: {current}")


def _open_regular(path: Path) -> tuple[int, os.stat_result]:
    try:
        before = os.lstat(path)
    except FileNotFoundError:
        raise
    if not stat.S_ISREG(before.st_mode):
        raise Refusal(f"refusing unsafe path: {path}")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(path, flags)
    except OSError as error:
        raise Refusal(f"could not safely open path: {path}") from error
    after = os.fstat(fd)
    if not stat.S_ISREG(after.st_mode) or _ident(before) != _ident(after):
        os.close(fd)
        raise Refusal(f"path changed while opening: {path}")
    return fd, after


def read_state(path: Path) -> State | None:
    try:
        fd, st = _open_regular(path)
    except FileNotFoundError:
        return None
    try:
        with os.fdopen(fd, "rb") as handle:
            data = handle.read()
    except OSError as error:
        raise Refusal(f"could not read path: {path}") from error
    return State(path, data, stat.S_IMODE(st.st_mode), _ident(st))


def same(state: State) -> bool:
    try:
        fd, st = _open_regular(state.path)
    except (FileNotFoundError, Refusal):
        return False
    try:
        with os.fdopen(fd, "rb") as handle:
            return _ident(st) == state.ident and handle.read() == state.data
    except OSError:
        return False


def analyzer_data_is_managed(data: bytes) -> bool:
    header = f"{ANALYZER_MARKER}\n".encode("utf-8")
    if not data.startswith(header):
        return False
    try:
        parsed = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError):
        return False
    return isinstance(parsed, dict) and parsed.get("name") == NAME


def analyzer_is_managed(state: State | None) -> bool:
    return state is not None and analyzer_data_is_managed(state.data)


def launcher_is_managed(state: State | None) -> bool:
    if state is None or not state.data.endswith(b"\n"):
        return False
    try:
        lines = state.data.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return False
    legacy = (
        len(lines) == 5
        and lines[0].startswith("#!")
        and lines[0].endswith(" -E")
        and lines[1] == LAUNCHER_MARKER
        and lines[2:4] == ["import os", "import sys"]
        and lines[4].startswith("os.execv(")
        and lines[4].endswith(" + sys.argv[1:])")
    )
    pinned = (
        len(lines) == 7
        and lines[0].startswith("#!")
        and lines[0].endswith(" -E")
        and lines[1] == LAUNCHER_MARKER
        and lines[2:4] == ["import os", "import sys"]
        and lines[4] == "env = os.environ.copy()"
        and lines[5].startswith('env["TRIAD_CLASSIFIER_EXTENSION"] = ')
        and lines[6].startswith("os.execve(")
        and lines[6].endswith(" + sys.argv[1:], env)")
    )
    return legacy or pinned


def parse_text(state: State | None, path: Path) -> str:
    if state is None:
        return ""
    try:
        return state.data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise Refusal(f"could not decode config: {path}") from error


def parsed_config(text: str, path: Path) -> dict:
    try:
        data = tomllib.loads(text) if text.strip() else {}
    except tomllib.TOMLDecodeError as error:
        raise Refusal(f"could not parse {path}") from error
    if not isinstance(data, dict):
        raise Refusal(f"could not parse {path}")
    return data


def expected_registration(analyzer: Path) -> dict[str, str]:
    return {"description": REG_DESCRIPTION, "config_file": str(analyzer)}


def registration_block(analyzer: Path, original_existed: bool) -> str:
    existed = "true" if original_existed else "false"
    return (
        f"{REG_BEGIN}\n"
        f"# original config existed = {existed}\n"
        f"[agents.{NAME}]\n"
        f"description = {json.dumps(REG_DESCRIPTION)}\n"
        f"config_file = {json.dumps(str(analyzer), ensure_ascii=False)}\n"
        f"{REG_END}\n"
    )


def reserved_registration_markers(text: str, path: Path, parsed: dict) -> list[str]:
    lines = text.splitlines(keepends=True)
    reserved: list[str] = []
    for index, line in enumerate(lines):
        marker = line.rstrip("\r\n")
        if marker not in (REG_BEGIN, REG_END):
            continue
        ending = line[len(marker) :]
        changed = lines.copy()
        changed[index] = f"# triad-codex-dispatch marker context probe {index}{ending}"
        if parsed_config("".join(changed), path) == parsed:
            reserved.append(marker)
    return reserved


def split_registration(
    text: str, path: Path, analyzer: Path
) -> tuple[str, str, bool, bool]:
    parsed = parsed_config(text, path)
    reserved = reserved_registration_markers(text, path, parsed)
    agents = parsed.get("agents", {})
    actual = agents.get(NAME) if isinstance(agents, dict) else None
    expected = expected_registration(analyzer)
    candidates: list[tuple[str, str, bool]] = []
    for original_existed in (False, True):
        block = registration_block(analyzer, original_existed)
        separator = "\n" if original_existed else ""
        needle = separator + block
        start = 0
        while True:
            start = text.find(needle, start)
            if start < 0:
                break
            before = text[:start]
            after = text[start + len(needle) :]
            if actual == expected:
                preserved = before + after
                try:
                    base_agents = parsed_config(preserved, path).get("agents", {})
                except Refusal:
                    base_agents = None
                if (
                    isinstance(base_agents, dict)
                    and NAME not in base_agents
                    and reserved == [REG_BEGIN, REG_END]
                ):
                    candidates.append((before, after, original_existed))
            start += len(needle)
    if len(candidates) > 1:
        raise Refusal(f"malformed managed repair analyzer registration in {path}")
    if candidates:
        before, after, original_existed = candidates[0]
        return before, after, True, original_existed
    if reserved:
        raise Refusal(f"malformed managed repair analyzer registration in {path}")
    return text, "", False, False


def registration(state: State | None, config: Path, analyzer: Path) -> tuple[bytes, bool]:
    original = parse_text(state, config)
    parsed_config(original, config)
    before, after, had, original_existed = split_registration(
        original, config, analyzer
    )
    if not had:
        original_existed = state is not None
    base = before + after
    agents = parsed_config(base, config).get("agents", {})
    if not isinstance(agents, dict) or NAME in agents:
        raise Refusal(f"refusing to overwrite unmanaged repair analyzer registration in {config}")
    block = registration_block(analyzer, original_existed)
    if had:
        result_text = before + ("\n" if original_existed else "") + block + after
    else:
        result_text = before + ("\n" if original_existed else "") + block
    result = result_text.encode("utf-8")
    parsed_config(result.decode("utf-8"), config)
    return result, had


def _state_from_fd(path: Path, fd: int) -> State:
    before = os.fstat(fd)
    chunks: list[bytes] = []
    offset = 0
    while offset < before.st_size:
        chunk = os.pread(fd, min(1024 * 1024, before.st_size - offset), offset)
        if not chunk:
            break
        chunks.append(chunk)
        offset += len(chunk)
    after = os.fstat(fd)
    data = b"".join(chunks)
    if _ident(before) != _ident(after) or len(data) != after.st_size:
        raise Refusal(f"staged descriptor changed while reading: {path}")
    return State(path, data, stat.S_IMODE(after.st_mode), _ident(after))


def _write_all(fd: int, data: bytes) -> None:
    remaining = memoryview(data)
    while remaining:
        written = os.write(fd, remaining)
        if written <= 0:
            raise OSError("could not write staged data")
        remaining = remaining[written:]


def creation_mode(base: int = 0o666) -> int:
    """Return the mode a normal create would receive under the current umask."""
    current = os.umask(0)
    os.umask(current)
    return base & ~current


def stage(path: Path, data: bytes, mode: int) -> Staged:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    staged_path = Path(name)
    staged_state: State | None = None
    try:
        os.fchmod(fd, mode & 0o777)
        _write_all(fd, data)
        staged_state = _state_from_fd(staged_path, fd)
        if staged_state.data != data:
            raise Refusal(f"could not stage complete data: {staged_path}")
        os.fsync(fd)
        staged_state = _state_from_fd(staged_path, fd)
    except BaseException as error:
        failures: list[BaseException] = []
        try:
            if staged_state is None:
                staged_state = _state_from_fd(staged_path, fd)
        except (OSError, Refusal) as state_error:
            failures.append(state_error)
        try:
            os.close(fd)
        except OSError as close_error:
            failures.append(close_error)
        if staged_state is not None:
            try:
                _delete_expected(staged_state)
            except (OSError, Refusal) as cleanup_error:
                failures.append(cleanup_error)
        if failures:
            raise TransactionFailure(error, failures) from error
        raise
    try:
        os.close(fd)
    except OSError as error:
        failures = []
        try:
            _delete_expected(staged_state)
        except (OSError, Refusal) as cleanup_error:
            failures.append(cleanup_error)
        if failures:
            raise TransactionFailure(error, failures) from error
        raise
    return Staged(staged_state)


def fsync_parent(path: Path) -> None:
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _state_matches(actual: State | None, expected: State) -> bool:
    return (
        actual is not None
        and actual.ident == expected.ident
        and actual.mode == expected.mode
        and actual.data == expected.data
    )


def _private_claim_path(target: Path) -> tuple[Path, Path]:
    target.parent.mkdir(parents=True, exist_ok=True)
    directory = Path(
        tempfile.mkdtemp(prefix=f".{target.name}.triad-claim-", dir=target.parent)
    )
    os.chmod(directory, 0o700)
    return directory, directory / "claimed"


def _cleanup_private_state(state: State | None, directory: Path | None) -> None:
    if state is None:
        if directory is not None:
            try:
                os.rmdir(directory)
            except FileNotFoundError:
                pass
        return
    _delete_expected(state, directory)


def _restore_no_clobber(state: State, target: Path, directory: Path) -> None:
    """Restore one claimed inode without overwriting a concurrent path."""
    try:
        os.link(state.path, target)
    except FileExistsError as error:
        raise Refusal(
            f"could not restore path without overwriting foreign bytes; "
            f"recovery retained at {state.path}"
        ) from error
    except OSError as error:
        raise Refusal(
            f"filesystem cannot restore path without clobbering; "
            f"recovery retained at {state.path}"
        ) from error
    fsync_parent(target)
    _cleanup_private_state(state, directory)


def _prepare_expected_claim(target: Path, expected: State) -> tuple[State, Path]:
    """Allocate a private claim and describe it before mutating the public path."""
    if not same(expected):
        if _path_is_absent(target):
            raise MissingExpected(f"path vanished before transaction claim: {target}")
        raise Refusal(f"path changed before transaction claim: {target}")
    directory, claimed_path = _private_claim_path(target)
    return (
        State(claimed_path, expected.data, expected.mode, expected.ident),
        directory,
    )


def _perform_expected_claim(
    target: Path, expected: State, planned: State, directory: Path
) -> State:
    """Move and validate a predeclared claim, restoring on asynchronous failure."""
    try:
        try:
            os.rename(target, planned.path)
        except FileNotFoundError as error:
            if _path_is_absent(target):
                raise MissingExpected(
                    f"path vanished during transaction claim: {target}"
                ) from error
            raise
        claimed = read_state(planned.path)
        if not _state_matches(claimed, expected):
            if claimed is None:
                raise Refusal(f"claimed path vanished: {planned.path}")
            _restore_no_clobber(claimed, target, directory)
            raise Refusal(f"path changed during transaction claim: {target}")
        return claimed
    except BaseException as error:
        recovery_failures: list[BaseException] = []
        try:
            claimed = read_state(planned.path)
            if claimed is not None:
                if _path_is_absent(target):
                    _restore_no_clobber(claimed, target, directory)
                else:
                    recovery_failures.append(
                        Refusal(
                            "could not restore interrupted transaction claim without "
                            f"overwriting {target}; recovery retained at {planned.path}"
                        )
                    )
            else:
                _remove_private_directory(directory)
        except BaseException as recovery_error:
            recovery_failures.append(recovery_error)
        if recovery_failures:
            raise TransactionFailure(error, recovery_failures) from error
        raise


def _claim_expected(target: Path, expected: State) -> tuple[State, Path]:
    """Move a public target aside, then validate the inode that was claimed.

    The preliminary `same` check is a fast refusal and preserves the historical
    diagnostic. Correctness comes from validating the atomically renamed claim:
    a swap after `same` is moved, detected, restored with no-clobber `os.link`,
    and never overwritten or deleted.
    """
    planned, directory = _prepare_expected_claim(target, expected)
    try:
        return _perform_expected_claim(target, expected, planned, directory), directory
    except BaseException:
        try:
            os.rmdir(directory)
        except OSError:
            pass
        raise


def _path_is_absent(path: Path) -> bool:
    try:
        os.lstat(path)
    except FileNotFoundError:
        return True
    return False


def _remove_private_directory(directory: Path) -> None:
    try:
        os.rmdir(directory)
    except FileNotFoundError:
        pass


def _unlink_claimed_state(
    state: State, directory: Path, recovery_path: Path
) -> None:
    """Delete a validated private claim, safely re-claiming before one retry."""
    try:
        os.unlink(state.path)
    except FileNotFoundError:
        _remove_private_directory(directory)
        return
    except OSError:
        if _path_is_absent(state.path):
            _remove_private_directory(directory)
            return
        try:
            retry_state, retry_dir = _claim_expected(state.path, state)
        except MissingExpected:
            _remove_private_directory(directory)
            return
        try:
            os.unlink(retry_state.path)
        except FileNotFoundError:
            pass
        except OSError as error:
            recovery_locations = str(retry_state.path)
            try:
                os.link(retry_state.path, recovery_path)
            except OSError:
                pass
            else:
                recovery_locations = f"{recovery_path} and {retry_state.path}"
            raise Refusal(
                f"could not remove claimed transaction state; "
                f"recovery retained at {recovery_locations}: {error}"
            ) from error
        _remove_private_directory(retry_dir)
    _remove_private_directory(directory)


def _delete_expected(expected: State, owner_directory: Path | None = None) -> None:
    """Atomically claim and validate owned state before deleting only that claim."""
    try:
        claimed, claim_dir = _claim_expected(expected.path, expected)
    except MissingExpected:
        if owner_directory is not None:
            _remove_private_directory(owner_directory)
        return
    _unlink_claimed_state(claimed, claim_dir, expected.path)
    if not _path_is_absent(expected.path):
        raise Refusal(f"foreign path appeared during transaction cleanup: {expected.path}")
    if owner_directory is not None:
        _remove_private_directory(owner_directory)


def _legacy_agent_data_is_managed(data: bytes) -> bool:
    try:
        head = "".join(data.decode("utf-8").splitlines(keepends=True)[:5])
    except UnicodeDecodeError:
        return False
    pair_match = LEGACY_AGENT_HEADER_A in head and LEGACY_AGENT_HEADER_B in head
    return pair_match or LEGACY_AGENT_SCOPE in head


def managed_removal_data_is_owned(data: bytes, kind: str) -> bool:
    if kind in ("profile", "rules"):
        return _managed_artifact_data_is_owned(data, kind)
    if kind == "legacy-agent":
        return _legacy_agent_data_is_managed(data)
    raise Refusal(f"unknown managed removal kind: {kind}")


def remove_managed_artifact(path: Path, kind: str) -> str:
    """Remove only the managed inode observed by this ownership check."""
    require_safe_ancestors(path)
    state = read_state(path)
    if state is None:
        return "absent"
    if not managed_removal_data_is_owned(state.data, kind):
        return "unmanaged"

    # Deterministic race seam: replace the public pathname after ownership was
    # established. The verified private-claim primitive must refuse that new
    # inode and leave its bytes untouched.
    swap_env = {
        "profile": "TRIAD_BOOTSTRAP_TEST_SWAP_PROFILE_BEFORE_REMOVE",
        "rules": "TRIAD_BOOTSTRAP_TEST_SWAP_RULES_BEFORE_REMOVE",
        "legacy-agent": "TRIAD_BOOTSTRAP_TEST_SWAP_LEGACY_AGENT_BEFORE_REMOVE",
    }[kind]
    swap_source = os.environ.get(swap_env)
    if swap_source:
        os.replace(swap_source, path)

    _delete_expected(state)
    fsync_parent(path)
    return "removed"


def quarantine_managed_artifact(
    path: Path,
    kind: str,
    destination: Path | None = None,
    *,
    quarantine_parent: Path | None = None,
) -> str:
    """Move one captured managed inode to a no-clobber quarantine path."""
    if (destination is None) == (quarantine_parent is None):
        raise Refusal(
            "managed quarantine requires exactly one destination or quarantine parent"
        )
    require_safe_ancestors(path)
    before = read_state(path)
    if before is None:
        return "absent"
    if not managed_removal_data_is_owned(before.data, kind):
        return "unmanaged"
    created_directory: Path | None = None
    try:
        if destination is None:
            assert quarantine_parent is not None
            require_safe_ancestors(quarantine_parent / ".triad-quarantine-probe")
            try:
                parent_status = os.lstat(quarantine_parent)
            except OSError as error:
                raise Refusal(
                    f"could not inspect quarantine parent: {quarantine_parent}"
                ) from error
            if stat.S_ISLNK(parent_status.st_mode) or not stat.S_ISDIR(
                parent_status.st_mode
            ):
                raise Refusal(
                    f"refusing unsafe quarantine parent: {quarantine_parent}"
                )
            timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
            created_directory = Path(
                tempfile.mkdtemp(
                    prefix=f".triad-quarantine-{timestamp}-",
                    dir=quarantine_parent,
                )
            )
            os.chmod(created_directory, 0o700)
            destination = created_directory / path.name
        require_safe_ancestors(destination)
        if not _path_is_absent(destination):
            raise Refusal(f"quarantine destination already exists: {destination}")

        swap_source = os.environ.get(
            "TRIAD_BOOTSTRAP_TEST_SWAP_LEGACY_AGENT_BEFORE_QUARANTINE"
        )
        if kind == "legacy-agent" and swap_source:
            replacement = Path(swap_source)
            if read_state(replacement) is None:
                raise Refusal(
                    f"missing legacy-agent replacement test input: {replacement}"
                )
            os.replace(replacement, path)

        journal: list[Mutation] = []
        failure: BaseException | None = None
        try:
            source_mutation = remove_state(before, journal)
            if source_mutation.backup is None:
                raise Refusal(f"missing quarantine claim for {path}")
            publish_to(Staged(source_mutation.backup), destination, None, journal)
        except BaseException as error:
            failure = error
        finalize_transaction(failure, journal, [])
    except BaseException as error:
        if created_directory is not None:
            try:
                _remove_private_directory(created_directory)
            except BaseException as cleanup_error:
                raise TransactionFailure(error, [cleanup_error]) from error
        raise
    return "quarantined"


def publish_to(
    temp: Staged, target: Path, expected: State | None, journal: list[Mutation]
) -> Mutation:
    staged = temp.state
    if not same(staged):
        raise Refusal(f"missing or changed staged path: {temp.path}")
    after = State(target, staged.data, staged.mode, staged.ident)
    backup: State | None = None
    backup_dir: Path | None = None
    if expected is None:
        try:
            os.lstat(target)
        except FileNotFoundError:
            pass
        else:
            raise Refusal(f"path changed before replacement: {target}")
    else:
        backup, backup_dir = _prepare_expected_claim(target, expected)
    mutation = Mutation(target, expected, after, backup, backup_dir)
    journal.append(mutation)
    if expected is not None:
        assert backup is not None and backup_dir is not None
        _perform_expected_claim(target, expected, backup, backup_dir)
    try:
        # Hard-link publication is an atomic no-clobber create on both macOS
        # and Linux. If a foreign path appears after the absence/claim check,
        # EEXIST preserves it. Never fall back to os.replace.
        os.link(temp.path, target)
    except OSError as error:
        raise Refusal(f"could not publish without overwriting path: {target}") from error
    fsync_parent(target)
    current = read_state(target)
    if not _state_matches(current, after):
        raise Refusal(f"could not publish path: {target}")
    return mutation


def remove_state(expected: State, journal: list[Mutation]) -> Mutation:
    backup, backup_dir = _prepare_expected_claim(expected.path, expected)
    mutation = Mutation(expected.path, expected, None, backup, backup_dir)
    journal.append(mutation)
    _perform_expected_claim(expected.path, expected, backup, backup_dir)
    fsync_parent(expected.path)
    try:
        os.lstat(expected.path)
    except FileNotFoundError:
        pass
    else:
        raise Refusal(f"could not remove path: {expected.path}")
    return mutation


def _publish_single(
    target: Path, data: bytes, expected: State | None, mode: int
) -> None:
    temp: Staged | None = None
    journal: list[Mutation] = []
    failure: BaseException | None = None
    try:
        temp = stage(target, data, mode)
        publish_to(temp, target, expected, journal)
    except BaseException as error:
        failure = error
    cleanup_failures = cleanup_all([temp] if temp is not None else [])
    finalize_transaction(failure, journal, cleanup_failures)


def _remove_single(expected: State) -> None:
    journal: list[Mutation] = []
    failure: BaseException | None = None
    try:
        remove_state(expected, journal)
    except BaseException as error:
        failure = error
    finalize_transaction(failure, journal, [])


def command_data_is_managed(name: str, kind: str, data: bytes) -> bool:
    """Recognize only the generated public-command grammar we own.

    The marker is a provenance line, not a substring token.  Binding it to the
    generated shebang/import/exec shape prevents a copied comment or string in
    a user executable from granting install/remove ownership.
    """
    vendor_envs = {
        "claude_wrapper.py": "TRIAD_CLAUDE_BIN",
        "gemini_wrapper.py": "TRIAD_GEMINI_BIN",
        "antigravity_wrapper.py": "TRIAD_AGY_BIN",
    }
    if kind == "launcher":
        marker = PUBLIC_LAUNCHER_MARKER
        if name not in vendor_envs:
            return False
    elif kind == "runtime":
        marker = PUBLIC_RUNTIME_MARKER
        if name not in {"triad-setup", "triad-doctor"}:
            return False
    else:
        raise Refusal(f"unknown managed command kind for {name}: {kind}")

    try:
        text = data.decode("utf-8")
        lines = text.splitlines()
        tree = ast.parse(text)
    except (UnicodeDecodeError, SyntaxError, ValueError):
        return False
    if (
        len(lines) < 5
        or not lines[0].startswith("#!")
        or lines[1] != marker.decode("ascii")
        or len(tree.body) < 3
        or not _exact_import(tree.body[0], "os")
        or not _exact_import(tree.body[1], "sys")
    ):
        return False
    body = tree.body[2:]
    if kind == "runtime":
        shebang_python = _shebang_python(lines[0], isolated=True)
        return shebang_python is not None and _managed_runtime_ast(
            name, shebang_python, body
        )
    if lines[0].endswith(" -E"):
        shebang_python = _shebang_python(lines[0], isolated=True)
        return shebang_python is not None and _managed_hardened_launcher_ast(
            name, vendor_envs[name], shebang_python, body
        )
    shebang_python = _shebang_python(lines[0], isolated=False)
    return shebang_python is not None and _managed_legacy_launcher_ast(
        name, vendor_envs[name], shebang_python, body
    )


def _shebang_python(shebang: str, *, isolated: bool) -> str | None:
    suffix = " -E" if isolated else ""
    if not shebang.startswith("#!") or not shebang.endswith(suffix):
        return None
    runtime = shebang[2 : len(shebang) - len(suffix) if suffix else None]
    if not runtime or not os.path.isabs(runtime) or any(
        char.isspace() for char in runtime
    ):
        return None
    return runtime


def _exact_import(node: ast.stmt, module: str) -> bool:
    return (
        isinstance(node, ast.Import)
        and len(node.names) == 1
        and node.names[0].name == module
        and node.names[0].asname is None
    )


def _string_assignment(
    node: ast.stmt, *, owner: str, key: str
) -> str | None:
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
        return None
    target = node.targets[0]
    if not isinstance(target, ast.Subscript):
        return None
    if owner == "env":
        owner_ok = isinstance(target.value, ast.Name) and target.value.id == "env"
    else:
        owner_ok = (
            isinstance(target.value, ast.Attribute)
            and isinstance(target.value.value, ast.Name)
            and target.value.value.id == "os"
            and target.value.attr == "environ"
        )
    if (
        not owner_ok
        or not isinstance(target.slice, ast.Constant)
        or target.slice.value != key
        or not isinstance(node.value, ast.Constant)
        or not isinstance(node.value.value, str)
    ):
        return None
    return node.value.value


def _matches_expression(node: ast.AST, source: str) -> bool:
    expected = ast.parse(source, mode="eval").body
    return ast.dump(node, include_attributes=False) == ast.dump(
        expected, include_attributes=False
    )


def _exec_call(
    node: ast.stmt, function: str, *, env_arg: bool
) -> tuple[str, list[str]] | None:
    if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
        return None
    call = node.value
    expected_args = 3 if env_arg else 2
    if (
        call.keywords
        or len(call.args) != expected_args
        or not isinstance(call.func, ast.Attribute)
        or not isinstance(call.func.value, ast.Name)
        or call.func.value.id != "os"
        or call.func.attr != function
        or not isinstance(call.args[0], ast.Constant)
        or not isinstance(call.args[0].value, str)
        or not isinstance(call.args[1], ast.BinOp)
        or not isinstance(call.args[1].op, ast.Add)
        or not isinstance(call.args[1].left, ast.List)
        or not _matches_expression(call.args[1].right, "sys.argv[1:]")
    ):
        return None
    if env_arg and not (
        isinstance(call.args[2], ast.Name) and call.args[2].id == "env"
    ):
        return None
    argv: list[str] = []
    for item in call.args[1].left.elts:
        if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
            return None
        argv.append(item.value)
    return call.args[0].value, argv


def _managed_hardened_launcher_ast(
    name: str,
    vendor_env: str,
    shebang_python: str,
    body: list[ast.stmt],
) -> bool:
    if len(body) not in {6, 7, 8}:
        return False
    scrub = body[0]
    expected_scrub = (
        "LD_PRELOAD", "LD_LIBRARY_PATH", "LD_AUDIT", "LD_DEBUG",
        "DYLD_INSERT_LIBRARIES", "DYLD_LIBRARY_PATH", "DYLD_FRAMEWORK_PATH",
        "NODE_OPTIONS", "NODE_PATH", "PYTHONPATH", "PYTHONHOME",
        "PYTHONSTARTUP", "BASH_ENV", "ENV", "PERL5LIB", "RUBYOPT", "RUBYLIB",
    )
    if not (
        isinstance(scrub, ast.Assign)
        and len(scrub.targets) == 1
        and isinstance(scrub.targets[0], ast.Name)
        and scrub.targets[0].id == "_SCRUB"
        and isinstance(scrub.value, ast.Tuple)
        and tuple(
            item.value
            for item in scrub.value.elts
            if isinstance(item, ast.Constant) and isinstance(item.value, str)
        ) == expected_scrub
        and len(scrub.value.elts) == len(expected_scrub)
    ):
        return False
    env_assign = body[1]
    if not (
        isinstance(env_assign, ast.Assign)
        and len(env_assign.targets) == 1
        and isinstance(env_assign.targets[0], ast.Name)
        and env_assign.targets[0].id == "env"
        and _matches_expression(
            env_assign.value,
            "{k: v for k, v in os.environ.items() if k not in _SCRUB}",
        )
    ):
        return False
    index = 2
    path_value = _string_assignment(body[index], owner="env", key="PATH")
    if not path_value:
        return False
    index += 1
    audit_redaction = _string_assignment(
        body[index], owner="env", key="TRIAD_AUDIT_REDACT_PROMPTS"
    )
    if audit_redaction is not None:
        if audit_redaction != "1":
            return False
        index += 1
    classifier = _string_assignment(
        body[index], owner="env", key="TRIAD_CLASSIFIER_EXTENSION"
    )
    if classifier is not None:
        if not classifier or not os.path.isabs(classifier):
            return False
        index += 1
    if _string_assignment(
        body[index], owner="env", key="TRIAD_REQUIRE_PINNED_VENDOR"
    ) != "1":
        return False
    index += 1
    vendor_value = _string_assignment(body[index], owner="env", key=vendor_env)
    if vendor_value is not None:
        if not vendor_value or not os.path.isabs(vendor_value):
            return False
    else:
        pop_node = body[index]
        if not (
            isinstance(pop_node, ast.Expr)
            and _matches_expression(
                pop_node.value, f'env.pop("{vendor_env}", None)'
            )
        ):
            return False
    index += 1
    if index != len(body) - 1:
        return False
    executed = _exec_call(body[index], "execve", env_arg=True)
    if executed is None:
        return False
    python, argv = executed
    return (
        python == shebang_python
        and len(argv) == 3
        and argv[0] == python
        and argv[1] == "-E"
        and os.path.isabs(argv[2])
        and argv[2].endswith(f"/bin/{name}")
    )


def _managed_legacy_launcher_ast(
    name: str,
    vendor_env: str,
    shebang_python: str,
    body: list[ast.stmt],
) -> bool:
    if len(body) not in {1, 2, 3}:
        return False
    assignments = body[:-1]
    seen: set[str] = set()
    for node in assignments:
        require_value = _string_assignment(
            node, owner="os.environ", key="TRIAD_REQUIRE_PINNED_VENDOR"
        )
        vendor_value = _string_assignment(node, owner="os.environ", key=vendor_env)
        if require_value is not None:
            if require_value != "1" or "require" in seen:
                return False
            seen.add("require")
        elif vendor_value is not None:
            if not vendor_value or not os.path.isabs(vendor_value) or "vendor" in seen:
                return False
            seen.add("vendor")
        else:
            return False
    required_pair = {"require", "vendor"}
    if name == "gemini_wrapper.py":
        if seen not in (set(), required_pair):
            return False
    elif seen != required_pair:
        return False
    executed = _exec_call(body[-1], "execv", env_arg=False)
    if executed is None:
        return False
    python, argv = executed
    return (
        python == shebang_python
        and len(argv) == 2
        and argv[0] == python
        and os.path.isabs(argv[1])
        and argv[1].endswith(f"/bin/{name}")
    )


def _managed_runtime_ast(
    name: str, shebang_python: str, body: list[ast.stmt]
) -> bool:
    if len(body) != 1:
        return False
    executed = _exec_call(body[0], "execv", env_arg=False)
    if executed is None:
        return False
    python, argv = executed
    command = name.removeprefix("triad-")
    return (
        python == shebang_python
        and len(argv) == 4
        and argv[0] == python
        and argv[1] == "-E"
        and os.path.isabs(argv[2])
        and argv[2].endswith("/bin/triad_runtime.py")
        and argv[3] == command
    )


def _command_is_managed(artifact: CommandArtifact, state: State) -> bool:
    return command_data_is_managed(artifact.name, artifact.kind, state.data)


def command_ownership_state(path: Path, name: str, kind: str) -> str:
    require_safe_ancestors(path)
    state = read_state(path)
    if state is None:
        return "absent"
    return "managed" if command_data_is_managed(name, kind, state.data) else "unmanaged"


def _preflight_command_group(
    artifacts: list[CommandArtifact], *, removing: bool, preserve_foreign: bool = False
) -> list[State | None]:
    seen: set[Path] = set()
    before: list[State | None] = []
    for artifact in artifacts:
        if not isinstance(artifact.name, str) or not artifact.name:
            raise Refusal(f"invalid managed command artifact: {artifact.name!r}")
        if artifact.kind not in {"launcher", "runtime"}:
            raise Refusal(f"unknown managed command kind for {artifact.name}: {artifact.kind}")
        if artifact.target in seen:
            raise Refusal(f"duplicate managed command target: {artifact.target}")
        seen.add(artifact.target)
        if not isinstance(artifact.data, bytes):
            raise Refusal(f"command payload must be bytes: {artifact.name}")
        # Command transactions are path based, not descriptor anchored. Reject
        # relative targets and unsafe existing ancestors on every install or
        # remove preflight; the parent chain must remain stable afterward.
        require_safe_ancestors(artifact.target)
        try:
            state = read_state(artifact.target)
        except Refusal:
            if preserve_foreign and removing:
                before.append(None)
                continue
            raise
        if state is not None and not _command_is_managed(artifact, state):
            if preserve_foreign and removing:
                before.append(None)
                continue
            action = "remove" if removing else "overwrite"
            raise Refusal(f"refusing to {action} unmanaged command: {artifact.target}")
        before.append(state)
    return before


def install_command_group(artifacts: list[CommandArtifact]) -> None:
    """Atomically publish all public commands, or restore every prior target."""
    before = _preflight_command_group(artifacts, removing=False)
    temps: list[Staged] = []
    journal: list[Mutation] = []
    failure: BaseException | None = None
    try:
        for artifact in artifacts:
            temps.append(stage(artifact.target, artifact.data, artifact.mode))
        for artifact, temp, expected in zip(artifacts, temps, before):
            publish_to(temp, artifact.target, expected, journal)
    except BaseException as error:
        failure = error
    cleanup_failures = cleanup_all(temps)
    finalize_transaction(failure, journal, cleanup_failures)


def remove_command_group(
    artifacts: list[CommandArtifact],
    *,
    test_fail_at: str | None = None,
    preserve_foreign: bool = False,
) -> None:
    """Atomically remove every present managed public command in a group."""
    before = _preflight_command_group(
        artifacts, removing=True, preserve_foreign=preserve_foreign
    )
    journal: list[Mutation] = []
    failure: BaseException | None = None
    try:
        for artifact, expected in zip(artifacts, before):
            if expected is not None:
                if test_fail_at == artifact.name:
                    raise OSError(f"injected command removal failure: {artifact.name}")
                remove_state(expected, journal)
    except BaseException as error:
        failure = error
    finalize_transaction(failure, journal, [])


def command_artifacts_from_manifest(path: Path, *, require_data: bool) -> list[CommandArtifact]:
    artifacts: list[CommandArtifact] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise Refusal(f"could not read command manifest: {path}") from error
    for line in lines:
        try:
            item = json.loads(line)
            name = item["name"]
            kind = item["kind"]
            target = Path(item["target"])
            mode = int(item.get("mode", 0o755))
            data_path = item.get("data_path")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise Refusal(f"invalid command manifest entry in {path}") from error
        if require_data:
            if not isinstance(data_path, str):
                raise Refusal(f"missing command payload for {name}")
            try:
                data = Path(data_path).read_bytes()
            except OSError as error:
                raise Refusal(f"could not read command payload for {name}") from error
        else:
            data = b""
        artifacts.append(CommandArtifact(name, target, data, kind, mode))
    return artifacts


def default_classifier_path() -> Path:
    override = os.environ.get("TRIAD_CLASSIFIER_EXTENSION")
    if override:
        return Path(override).expanduser()
    base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "triad-codex-dispatch" / "classifier-patches.json"


def portable_python_shebang(python: Path) -> bytes:
    runtime = os.fspath(python)
    if any(char.isspace() for char in runtime):
        raise Refusal(
            f"portable generated shebang cannot encode this Python runtime path: {python}"
        )
    shebang = b"#!" + os.fsencode(runtime) + b" -E\n"
    if len(shebang) > 256:
        raise Refusal(
            "portable generated shebang exceeds 256 filesystem bytes for "
            f"Python runtime path: {python}"
        )
    return shebang


def runtime_path() -> Path:
    runtime = Path(sys.executable).resolve()
    require_safe_ancestors(runtime)
    if read_state(runtime) is None:
        raise Refusal(f"missing resolved Python runtime: {runtime}")
    portable_python_shebang(runtime)
    return runtime


def formal_schema_dependency_ready(requirements: Path) -> Path:
    """Require the Pydantic 2 API surface used by formal review."""
    runtime = runtime_path()
    if not requirements.is_absolute() or not requirements.is_file():
        raise Refusal(f"requirements file is unavailable: {requirements}")
    requirements = requirements.resolve()
    try:
        import pydantic
        from pydantic import (
            BaseModel,
            ConfigDict,
            ValidationInfo,
            field_validator,
            model_validator,
        )

        version = str(getattr(pydantic, "VERSION", "0"))
        if version.split(".", 1)[0] != "2":
            raise RuntimeError(f"unsupported Pydantic version {version}")
        for attribute in ("model_validate", "model_validate_json", "model_json_schema"):
            if not hasattr(BaseModel, attribute):
                raise RuntimeError(f"Pydantic BaseModel lacks {attribute}")
        if not all(
            item is not None
            for item in (
                ConfigDict,
                ValidationInfo,
                field_validator,
                model_validator,
            )
        ):
            raise RuntimeError("Pydantic 2 validator API is incomplete")
    except (ImportError, AttributeError, RuntimeError, TypeError, ValueError) as error:
        owner_command = shlex.join(
            [
                str(runtime),
                "-m",
                "pip",
                "install",
                "-r",
                str(requirements),
            ]
        )
        raise Refusal(
            "Pydantic 2 formal review APIs are required. Run this in the owner "
            f"terminal, then rerun bootstrap: {owner_command}"
        ) from error
    return runtime


def _require_writable_state(state: State, label: str) -> None:
    flags = os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(state.path, flags)
    except OSError as error:
        raise Refusal(f"{label} is not writable: {state.path}") from error
    try:
        current = os.fstat(fd)
        if not stat.S_ISREG(current.st_mode) or _ident(current) != state.ident:
            raise Refusal(f"{label} changed while checking writability: {state.path}")
    finally:
        os.close(fd)


def _classifier_state(path: Path) -> State | None:
    require_safe_ancestors(path)
    state = read_state(path)
    if state is None:
        return None
    try:
        json.loads(state.data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise Refusal(f"classifier file is not valid JSON: {path}") from error
    _require_writable_state(state, "classifier file")
    return state


def preflight_classifier(path: Path) -> str:
    return "ready" if _classifier_state(path) is not None else "absent"


def ensure_classifier(path: Path) -> str:
    if os.environ.get("TRIAD_BOOTSTRAP_TEST_FAIL_CLASSIFIER_ENSURE") == "1":
        raise Refusal("injected classifier ensure failure")
    swap_target = os.environ.get(
        "TRIAD_BOOTSTRAP_TEST_SWAP_CLASSIFIER_TO_SYMLINK_BEFORE_ENSURE"
    )
    if swap_target:
        require_safe_ancestors(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        require_safe_ancestors(path)
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
        os.symlink(swap_target, path)
    before = _classifier_state(path)
    if before is not None:
        return "ready"
    _publish_single(path, b"{}\n", None, creation_mode())
    created = _classifier_state(path)
    if created is None:
        raise Refusal(f"classifier file was not created: {path}")
    return "created"


def _managed_artifact_marker(kind: str) -> bytes:
    if kind == "profile":
        return PROFILE_MARKER
    if kind == "rules":
        return RULES_MARKER
    raise Refusal(f"unknown managed artifact kind: {kind}")


def _managed_artifact_data_is_owned(data: bytes, kind: str) -> bool:
    lines = data.splitlines()
    return bool(lines) and lines[0] == _managed_artifact_marker(kind)


def _managed_artifact_state(path: Path, kind: str) -> State | None:
    require_safe_ancestors(path)
    state = read_state(path)
    if state is not None:
        selected = "Codex runtime profile" if kind == "profile" else "Codex command rules"
        try:
            state.data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise Refusal(f"could not read selected {selected}: {path}") from error
        if not _managed_artifact_data_is_owned(state.data, kind):
            label = "Codex profile" if kind == "profile" else "Codex rules file"
            raise Refusal(f"refusing to overwrite unmanaged {label}: {path}")
    return state


def preflight_managed_artifact(path: Path, kind: str) -> str:
    return "managed" if _managed_artifact_state(path, kind) is not None else "absent"


def inspect_managed_artifact(path: Path, kind: str) -> str:
    """Inspect a legacy artifact without claiming ownership or mutating it.

    Unlike the selected-artifact preflight, a safe regular foreign file is a
    valid observation rather than an overwrite refusal. Unsafe paths and read
    failures remain fail-closed refusals.
    """
    require_safe_ancestors(path)
    state = read_state(path)
    if state is None:
        return "absent"
    return "managed" if _managed_artifact_data_is_owned(state.data, kind) else "unmanaged"


def install_managed_artifact(path: Path, kind: str, payload: bytes) -> str:
    if not _managed_artifact_data_is_owned(payload, kind):
        raise Refusal(f"managed {kind} payload has an invalid first logical line")
    before = _managed_artifact_state(path, kind)
    if before is not None and before.data == payload:
        return "unchanged"
    mode = before.mode if before is not None else creation_mode()
    temp: Staged | None = None
    journal: list[Mutation] = []
    failure: BaseException | None = None
    try:
        temp = stage(path, payload, mode)
        regular_swap_env = {
            "profile": "TRIAD_BOOTSTRAP_TEST_SWAP_PROFILE_TO_REGULAR_BEFORE_WRITE",
            "rules": "TRIAD_BOOTSTRAP_TEST_SWAP_RULES_TO_REGULAR_BEFORE_WRITE",
        }[kind]
        regular_swap_source = os.environ.get(regular_swap_env)
        if regular_swap_source:
            replacement = Path(regular_swap_source)
            if read_state(replacement) is None:
                raise Refusal(f"missing regular replacement test input: {replacement}")
            os.replace(replacement, path)
        swap_env = {
            "profile": "TRIAD_BOOTSTRAP_TEST_SWAP_PROFILE_TO_SYMLINK_BEFORE_WRITE",
            "rules": "TRIAD_BOOTSTRAP_TEST_SWAP_RULES_TO_SYMLINK_BEFORE_WRITE",
        }[kind]
        swap_target = os.environ.get(swap_env)
        if swap_target:
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass
            os.symlink(swap_target, path)
        publish_to(temp, path, before, journal)
    except BaseException as error:
        failure = error
    cleanup_failures = cleanup_all([temp] if temp is not None else [])
    finalize_transaction(failure, journal, cleanup_failures)
    return "updated" if before is not None else "created"


def current_config_fragment(newline: bytes) -> bytes:
    return (
        CONFIG_FRAGMENT_BEGIN
        + newline
        + CURRENT_CONFIG_FRAGMENT_TEXT.replace(b"\n", newline)
        + CONFIG_FRAGMENT_END
        + newline
    )


def legacy_config_fragment(newline: bytes) -> bytes:
    return (
        CONFIG_FRAGMENT_BEGIN
        + newline
        + LEGACY_CONFIG_FRAGMENT_TEXT.replace(b"\n", newline)
        + CONFIG_FRAGMENT_END
        + newline
    )


def _parsed_shared_config(state: State, path: Path) -> dict | None:
    try:
        text = state.data.decode("utf-8")
        data = tomllib.loads(text) if state.data else {}
    except (UnicodeDecodeError, tomllib.TOMLDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _publish_config_backup(config: Path, before: State) -> Path:
    number = 1
    while True:
        suffix = ".bak" if number == 1 else f".bak{number}"
        backup = Path(os.fspath(config) + suffix)
        require_safe_ancestors(backup)
        if _path_is_absent(backup):
            break
        number += 1
    _publish_single(backup, before.data, None, before.mode)
    return backup


def _contains_only_managed_registration(
    existing: bytes, path: Path, data: dict
) -> bool:
    if set(data) != {"agents"}:
        return False
    agents = data.get("agents")
    if not isinstance(agents, dict) or set(agents) != {NAME}:
        return False
    entry = agents.get(NAME)
    if not isinstance(entry, dict):
        return False
    analyzer_raw = entry.get("config_file")
    if not isinstance(analyzer_raw, str) or not Path(analyzer_raw).is_absolute():
        return False
    try:
        before, after, managed, original_existed = split_registration(
            existing.decode("utf-8"), path, Path(analyzer_raw)
        )
    except (UnicodeDecodeError, Refusal):
        return False
    return managed and not original_existed and not before and not after


def merge_config_fragment(path: Path) -> str:
    require_safe_ancestors(path)
    before = read_state(path)
    existing = before.data if before is not None else b""
    if before is not None:
        data = _parsed_shared_config(before, path)
        if data is None:
            return "malformed"
    else:
        data = {}

    has_begin = CONFIG_FRAGMENT_BEGIN in existing
    has_end = CONFIG_FRAGMENT_END in existing
    if has_begin or has_end:
        markers_once = (
            existing.count(CONFIG_FRAGMENT_BEGIN) == 1
            and existing.count(CONFIG_FRAGMENT_END) == 1
        )
        current_blocks = [current_config_fragment(nl) for nl in (b"\n", b"\r\n")]
        legacy_blocks = [legacy_config_fragment(nl) for nl in (b"\n", b"\r\n")]
        current_policy = tomllib.loads(CURRENT_CONFIG_FRAGMENT_TEXT.decode("utf-8"))[
            "shell_environment_policy"
        ]
        exact_current = (
            markers_once
            and data.get("shell_environment_policy") == current_policy
            and sum(existing.count(candidate) for candidate in current_blocks) == 1
        )
        if exact_current:
            return "already-managed"
        exact_legacy = (
            markers_once
            and data.get("shell_environment_policy") == {"inherit": "core"}
            and sum(existing.count(candidate) for candidate in legacy_blocks) == 1
        )
        if not exact_legacy:
            return "edited-managed"
        old = next(candidate for candidate in legacy_blocks if existing.count(candidate) == 1)
        newline = b"\r\n" if b"\r\n" in old else b"\n"
        updated = existing.replace(old, current_config_fragment(newline), 1)
        status = "migrated"
    else:
        if "shell_environment_policy" in data:
            return "user-policy"
        if existing.strip():
            if existing.endswith(b"\r\n"):
                updated = existing + current_config_fragment(b"\r\n")
            elif existing.endswith(b"\n"):
                updated = existing + current_config_fragment(b"\n")
            else:
                updated = (
                    existing
                    + CONFIG_FRAGMENT_INSERTED_SEPARATOR
                    + current_config_fragment(b"\n")
                )
        else:
            updated = current_config_fragment(b"\n")
        status = "merged"

    registration_only = (
        before is not None
        and _contains_only_managed_registration(existing, path, data)
    )
    backup = (
        _publish_config_backup(path, before)
        if before is not None and not registration_only
        else None
    )
    _publish_single(
        path,
        updated,
        before,
        before.mode if before is not None else 0o600,
    )
    if backup is not None:
        print(
            f"[info] retained config backup: {backup}; keep it until Codex starts "
            "normally, then delete it if rollback is no longer needed",
            file=sys.stderr,
        )
    return status


def remove_config_fragment(path: Path, *, preserve_empty: bool = False) -> str:
    if os.environ.get("TRIAD_BOOTSTRAP_TEST_FAIL_CONFIG_FRAGMENT_REMOVE") == "1":
        raise Refusal("injected config fragment remove failure")
    require_safe_ancestors(path)
    before = read_state(path)
    if before is None:
        return "absent"
    existing = before.data
    data = _parsed_shared_config(before, path)
    if data is None:
        return "unrecognized-managed"
    if CONFIG_FRAGMENT_BEGIN not in existing and CONFIG_FRAGMENT_END not in existing:
        return "not-managed"

    markers_once = (
        existing.count(CONFIG_FRAGMENT_BEGIN) == 1
        and existing.count(CONFIG_FRAGMENT_END) == 1
    )
    current_blocks = [current_config_fragment(nl) for nl in (b"\n", b"\r\n")]
    legacy_blocks = [legacy_config_fragment(nl) for nl in (b"\n", b"\r\n")]
    current_policy = tomllib.loads(CURRENT_CONFIG_FRAGMENT_TEXT.decode("utf-8"))[
        "shell_environment_policy"
    ]
    exact_current = (
        markers_once
        and data.get("shell_environment_policy") == current_policy
        and sum(existing.count(candidate) for candidate in current_blocks) == 1
    )
    exact_legacy = (
        markers_once
        and data.get("shell_environment_policy") == {"inherit": "core"}
        and sum(existing.count(candidate) for candidate in legacy_blocks) == 1
    )
    if exact_current:
        managed = next(candidate for candidate in current_blocks if existing.count(candidate) == 1)
    elif exact_legacy:
        managed = next(candidate for candidate in legacy_blocks if existing.count(candidate) == 1)
    else:
        return "unrecognized-managed"

    managed_start = existing.find(managed)
    separator_start = managed_start - len(CONFIG_FRAGMENT_INSERTED_SEPARATOR)
    if (
        separator_start >= 0
        and existing[separator_start:managed_start]
        == CONFIG_FRAGMENT_INSERTED_SEPARATOR
    ):
        managed = CONFIG_FRAGMENT_INSERTED_SEPARATOR + managed
    remainder = existing.replace(managed, b"", 1)
    if not remainder:
        if preserve_empty:
            _publish_single(path, b"", before, before.mode)
            return "removed"
        _remove_single(before)
        return "removed-file"
    _publish_single(path, remainder, before, before.mode)
    return "removed"


def _shell_entry_span(data: bytes, path: Path) -> tuple[int, int] | None:
    spans: list[tuple[int, int, bytes]] = []
    offset = 0
    for line in data.splitlines(keepends=True):
        content = line
        if content.endswith(b"\r\n"):
            content = content[:-2]
        elif content.endswith((b"\n", b"\r")):
            content = content[:-1]
        spans.append((offset, offset + len(line), content))
        offset += len(line)

    begin_spans = [span for span in spans if span[2] == SHELL_ENTRY_BEGIN]
    end_spans = [span for span in spans if span[2] == SHELL_ENTRY_END]
    raw_begin_count = data.count(SHELL_ENTRY_BEGIN)
    raw_end_count = data.count(SHELL_ENTRY_END)
    if raw_begin_count == 0 and raw_end_count == 0:
        return None
    valid = (
        raw_begin_count == 1
        and raw_end_count == 1
        and len(begin_spans) == 1
        and len(end_spans) == 1
        and begin_spans[0][0] < end_spans[0][0]
    )
    if not valid:
        raise Refusal(f"malformed managed codex-triad shell markers in {path}")
    return begin_spans[0][0], end_spans[0][1]


def _shell_entry_state(path: Path, action: str) -> tuple[State | None, tuple[int, int] | None]:
    if action not in {"install", "remove"}:
        raise Refusal(f"unknown shell-entry action: {action}")
    require_safe_ancestors(path)
    before = read_state(path)
    if before is None:
        return None, None
    span = _shell_entry_span(before.data, path)
    if span is None and action == "install" and b"codex-triad" in before.data:
        raise Refusal(
            f"refusing to modify unmanaged codex-triad shell entry in {path}; "
            "remove it manually, then re-run --install"
        )
    return before, span


def _shell_entry_base(
    before: State | None, span: tuple[int, int] | None
) -> bytes:
    existing = before.data if before is not None else b""
    if span is None:
        return existing
    return existing[: span[0]] + existing[span[1] :]


def preflight_shell_entry(path: Path, action: str) -> str:
    before, span = _shell_entry_state(path, action)
    if before is None:
        return "absent"
    if action == "install":
        base = _shell_entry_base(before, span)
        if base and not base.endswith((b"\n", b"\r")):
            raise Refusal(f"shell RC must end with a newline before install: {path}")
    if span is not None:
        return "managed"
    return "unmanaged" if b"codex-triad" in before.data else "absent"


def _shell_entry_block(profile: str) -> bytes:
    first = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    rest = first + "._-"
    if not profile or profile[0] not in first or any(char not in rest for char in profile):
        raise Refusal(
            "invalid shell-entry profile: must match "
            "[A-Za-z0-9][A-Za-z0-9._-]*"
        )
    return (
        SHELL_ENTRY_BEGIN
        + b"\n"
        + b"# Managed by triad-codex-dispatch scripts/bootstrap.sh --install;\n"
        + b"# removed by --remove. Legacy prompt-reviewed posture: wrapper root\n"
        + b"# containment + hardened wrapper mode + enforced claude sandbox.\n"
        + b"codex-triad() {\n"
        + b'  TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}" \\\n'
        + b"  TRIAD_WRAPPER_HARDENED=1 \\\n"
        + b"  TRIAD_CLAUDE_ENFORCE_SANDBOX=1 \\\n"
        + f'    command codex --profile {profile} --search "$@"\n'.encode("ascii")
        + b"}\n"
        + SHELL_ENTRY_END
        + b"\n"
    )


def update_shell_entry(path: Path, action: str, profile: str | None) -> str:
    """Transform and publish one shell RC against the exact captured state."""
    before, span = _shell_entry_state(path, action)
    existing = before.data if before is not None else b""
    if action == "remove" and span is None:
        if before is not None and b"codex-triad" in existing:
            return "unmanaged"
        return "absent"

    transformed = _shell_entry_base(before, span)
    if action == "install":
        if profile is None:
            raise Refusal("shell-entry install requires --profile")
        transformed += _shell_entry_block(profile)
        # Refuse to publish a block that would not occupy exact logical lines,
        # such as an append after an owner file lacking its final newline.
        _shell_entry_span(transformed, path)

    temp: Staged | None = None
    journal: list[Mutation] = []
    failure: BaseException | None = None
    try:
        mode = before.mode if before is not None else creation_mode()
        temp = stage(path, transformed, mode)
        swap_source = os.environ.get(
            "TRIAD_BOOTSTRAP_TEST_SWAP_SHELL_RC_BEFORE_PUBLISH"
        )
        if swap_source:
            replacement = Path(swap_source)
            if read_state(replacement) is None:
                raise Refusal(f"missing shell RC replacement test input: {replacement}")
            os.replace(replacement, path)
        publish_to(temp, path, before, journal)
    except BaseException as error:
        failure = error
    cleanup_failures = cleanup_all([temp] if temp is not None else [])
    finalize_transaction(failure, journal, cleanup_failures)
    return "installed" if action == "install" else "removed"


def launcher_text(
    python: Path,
    apply_patch: Path,
    classifier: Path | None = None,
) -> bytes:
    shebang = portable_python_shebang(python)
    classifier = classifier or default_classifier_path()
    if not classifier.is_absolute():
        raise Refusal(f"classifier path must be absolute: {classifier}")
    runtime = json.dumps(str(python), ensure_ascii=False)
    target = json.dumps(str(apply_patch), ensure_ascii=False)
    classifier_literal = json.dumps(str(classifier), ensure_ascii=False)
    return shebang + (
        f"{LAUNCHER_MARKER}\nimport os\nimport sys\n"
        "env = os.environ.copy()\n"
        f'env["TRIAD_CLASSIFIER_EXTENSION"] = {classifier_literal}\n'
        f"os.execve({runtime}, [{runtime}, \"-E\", {target}] + sys.argv[1:], env)\n"
    ).encode("utf-8")


def cleanup(temp: Staged | None) -> None:
    if temp is not None:
        _delete_expected(temp.state)


def cleanup_all(temps: list[Staged | None]) -> list[BaseException]:
    failures: list[BaseException] = []
    for temp in temps:
        try:
            cleanup(temp)
        except BaseException as error:
            failures.append(error)
    return failures


def rollback_mutation(mutation: Mutation) -> None:
    current = read_state(mutation.target)

    if mutation.before is None:
        if current is None:
            return
        if mutation.after is not None and _state_matches(current, mutation.after):
            _delete_expected(current)
        # A non-matching path was created by somebody else. The transaction
        # never owned it and therefore has nothing to roll back.
        return

    if mutation.backup is None or mutation.backup_dir is None:
        raise Refusal(f"missing rollback recovery for {mutation.target}")
    backup = read_state(mutation.backup.path)
    if backup is None:
        if _state_matches(current, mutation.before):
            _remove_private_directory(mutation.backup_dir)
            return
        _remove_private_directory(mutation.backup_dir)
        raise Refusal(f"missing rollback recovery for {mutation.target}")

    if current is None:
        _restore_no_clobber(backup, mutation.target, mutation.backup_dir)
        fsync_parent(mutation.target)
        return
    if _state_matches(current, mutation.before):
        _cleanup_private_state(backup, mutation.backup_dir)
        fsync_parent(mutation.target)
        return
    if mutation.after is None or not _state_matches(current, mutation.after):
        raise Refusal(
            f"could not restore path without overwriting foreign bytes; "
            f"recovery retained at {mutation.backup.path}"
        )

    claimed_after, claimed_after_dir = _claim_expected(
        mutation.target, mutation.after
    )
    _restore_no_clobber(backup, mutation.target, mutation.backup_dir)
    _cleanup_private_state(claimed_after, claimed_after_dir)
    fsync_parent(mutation.target)


def rollback_all(journal: list[Mutation]) -> list[BaseException]:
    failures: list[BaseException] = []
    for mutation in reversed(journal):
        try:
            rollback_mutation(mutation)
        except BaseException as error:
            failures.append(error)
    return failures


def commit_all(journal: list[Mutation]) -> list[BaseException]:
    failures: list[BaseException] = []
    for mutation in journal:
        if mutation.backup is None:
            continue
        try:
            _cleanup_private_state(mutation.backup, mutation.backup_dir)
        except BaseException as error:
            failures.append(error)
    return failures


def reraise_after_rollback(
    error: BaseException, journal: list[Mutation], cleanup_failures: list[BaseException]
) -> None:
    failures = rollback_all(journal) + cleanup_failures
    if failures:
        raise TransactionFailure(error, failures) from error
    raise error


def finalize_transaction(
    failure: BaseException | None,
    journal: list[Mutation],
    cleanup_failures: list[BaseException],
) -> None:
    """Rollback before commit when publication or staged cleanup failed."""
    if failure is not None:
        reraise_after_rollback(failure, journal, cleanup_failures)
    if cleanup_failures:
        primary, *additional = cleanup_failures
        reraise_after_rollback(primary, journal, additional)
    commit_failures = commit_all(journal)
    if commit_failures:
        # A commit cleanup may already have deleted earlier backups, so the
        # publication remains committed and rollback is no longer promised.
        raise TransactionFailure(
            Refusal("transaction committed but backup cleanup failed"),
            commit_failures,
        )


def prepare_install(args: argparse.Namespace) -> RepairInstallPlan:
    if not args.source or not args.apply_patch:
        raise Refusal("install requires --source and --apply-patch")
    source, config, analyzer, apply = map(
        Path, (args.source, args.config, args.analyzer, args.apply_patch)
    )
    launcher, runtime = Path(args.launcher), Path(args.python).resolve()
    classifier = Path(args.classifier).expanduser()
    for managed_path in (source, config, analyzer, apply, launcher, runtime):
        require_safe_ancestors(managed_path)
    if not classifier.is_absolute():
        raise Refusal(f"classifier path must be absolute: {classifier}")
    portable_python_shebang(runtime)
    source_state, apply_state, runtime_state = (
        read_state(source),
        read_state(apply),
        read_state(runtime),
    )
    if source_state is None or not analyzer_data_is_managed(source_state.data):
        raise Refusal(f"missing managed repair analyzer source: {source}")
    try:
        tomllib.loads(source_state.data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as error:
        raise Refusal(f"invalid repair analyzer source: {source}") from error
    if apply_state is None or runtime_state is None:
        raise Refusal("missing repair applier or resolved Python runtime")
    try:
        config_before = read_state(config)
    except Refusal as error:
        raise Refusal(f"refusing unsafe repair config: {config}") from error
    try:
        analyzer_before = read_state(analyzer)
    except Refusal as error:
        raise Refusal(f"refusing unsafe repair analyzer: {analyzer}") from error
    try:
        launcher_before = read_state(launcher)
    except Refusal as error:
        raise Refusal(f"refusing unsafe repair apply launcher: {launcher}") from error
    if analyzer_before is not None and not analyzer_is_managed(analyzer_before):
        raise Refusal(f"refusing to overwrite unmanaged repair analyzer: {analyzer}")
    if launcher_before is not None and not launcher_is_managed(launcher_before):
        raise Refusal(f"refusing to overwrite unmanaged repair apply launcher: {launcher}")
    config_data, _had = registration(config_before, config, analyzer)
    return RepairInstallPlan(
        source_state=source_state,
        apply_state=apply_state,
        runtime_state=runtime_state,
        config=config,
        analyzer=analyzer,
        launcher=launcher,
        config_before=config_before,
        analyzer_before=analyzer_before,
        launcher_before=launcher_before,
        config_data=config_data,
        launcher_data=launcher_text(runtime, apply, classifier),
    )


def preflight_install(args: argparse.Namespace) -> None:
    """Validate every repair-install input and target without writing anything."""
    prepare_install(args)


def install(args: argparse.Namespace) -> None:
    plan = prepare_install(args)
    temps: list[Staged] = []
    journal: list[Mutation] = []
    failure: BaseException | None = None
    try:
        temps.append(
            stage(
                plan.analyzer,
                plan.source_state.data,
                plan.analyzer_before.mode if plan.analyzer_before else 0o600,
            )
        )
        temps.append(
            stage(
                plan.config,
                plan.config_data,
                plan.config_before.mode if plan.config_before else 0o600,
            )
        )
        temps.append(
            stage(
                plan.launcher,
                plan.launcher_data,
                plan.launcher_before.mode if plan.launcher_before else 0o755,
            )
        )
        if not same(plan.source_state):
            raise Refusal(
                f"repair analyzer source changed before publication: {plan.source_state.path}"
            )
        publish_to(temps[0], plan.analyzer, plan.analyzer_before, journal)
        if os.environ.get("TRIAD_BOOTSTRAP_TEST_FAIL_REPAIR_REGISTRATION_PUBLISH") == "1":
            raise OSError("injected registration publication failure")
        publish_to(temps[1], plan.config, plan.config_before, journal)
        if not same(plan.apply_state) or not same(plan.runtime_state):
            raise Refusal("repair launcher input changed before publication")
        publish_to(temps[2], plan.launcher, plan.launcher_before, journal)
    except BaseException as error:
        failure = error
    finally:
        cleanup_failures = cleanup_all(temps)
    finalize_transaction(failure, journal, cleanup_failures)


def prepare_remove(args: argparse.Namespace) -> RepairRemovePlan:
    config, analyzer, launcher = Path(args.config), Path(args.analyzer), Path(args.launcher)
    for managed_path in (config, analyzer, launcher):
        require_safe_ancestors(managed_path)
    try:
        config_before = read_state(config)
    except Refusal as error:
        raise Refusal(f"refusing unsafe repair config: {config}") from error
    try:
        analyzer_before = read_state(analyzer)
    except Refusal as error:
        raise Refusal(f"refusing unsafe repair analyzer: {analyzer}") from error
    try:
        launcher_before = read_state(launcher)
    except Refusal as error:
        raise Refusal(f"refusing unsafe repair apply launcher: {launcher}") from error
    original = parse_text(config_before, config)
    parsed_config(original, config)
    before, after, managed_registration, original_config_existed = split_registration(
        original, config, analyzer
    )
    base = before + after
    if managed_registration and not original_config_existed and base:
        managed_fragments = {
            current_config_fragment(b"\r\n").decode("utf-8"),
            current_config_fragment(b"\n").decode("utf-8"),
            legacy_config_fragment(b"\r\n").decode("utf-8"),
            legacy_config_fragment(b"\n").decode("utf-8"),
        }
        if base not in managed_fragments:
            original_config_existed = True
    agents = parsed_config(base, config).get("agents", {})
    if not isinstance(agents, dict):
        raise Refusal(f"could not parse {config}")
    if not managed_registration and NAME in agents:
        analyzer_before = None
    elif analyzer_before is not None and not analyzer_is_managed(analyzer_before):
        analyzer_before = None
    if launcher_before is not None and not launcher_is_managed(launcher_before):
        launcher_before = None
    return RepairRemovePlan(
        config=config,
        analyzer=analyzer,
        launcher=launcher,
        config_before=config_before,
        analyzer_before=analyzer_before,
        launcher_before=launcher_before,
        base=base,
        managed_registration=managed_registration,
        original_config_existed=original_config_existed,
    )


def preflight_remove(args: argparse.Namespace) -> None:
    """Validate every repair-removal input and target without writing anything."""
    prepare_remove(args)


def remove(args: argparse.Namespace) -> None:
    plan = prepare_remove(args)
    journal: list[Mutation] = []
    temps: list[Staged] = []
    failure: BaseException | None = None
    try:
        if plan.managed_registration and plan.config_before is not None:
            if plan.original_config_existed:
                temp = stage(
                    plan.config,
                    plan.base.encode("utf-8"),
                    plan.config_before.mode,
                )
                temps.append(temp)
                publish_to(temp, plan.config, plan.config_before, journal)
            else:
                remove_state(plan.config_before, journal)
        if plan.analyzer_before is not None:
            remove_state(plan.analyzer_before, journal)
        if plan.launcher_before is not None:
            remove_state(plan.launcher_before, journal)
    except BaseException as error:
        failure = error
    finally:
        cleanup_failures = cleanup_all(temps)
    finalize_transaction(failure, journal, cleanup_failures)


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    for command in ("install", "remove", "preflight-install", "preflight-remove"):
        child = sub.add_parser(command)
        child.add_argument("--config", required=True)
        child.add_argument("--analyzer", required=True)
        child.add_argument("--launcher", required=True)
        child.add_argument("--source")
        child.add_argument("--python", default=str(Path(sys.executable).resolve()))
        child.add_argument("--apply-patch")
        child.add_argument("--classifier", default=str(default_classifier_path()))
    for command in ("commands-install", "commands-remove"):
        child = sub.add_parser(command)
        child.add_argument("--manifest", required=True)
        if command == "commands-remove":
            child.add_argument("--test-fail-at", default="")
            child.add_argument("--preserve-foreign", action="store_true")
    command_owned = sub.add_parser("command-owned")
    command_owned.add_argument("--path", required=True)
    command_owned.add_argument("--name", required=True)
    command_owned.add_argument(
        "--kind", required=True, choices=("launcher", "runtime")
    )
    managed_remove = sub.add_parser("managed-remove")
    managed_remove.add_argument("--path", required=True)
    managed_remove.add_argument(
        "--kind", required=True, choices=("profile", "rules", "legacy-agent")
    )
    managed_quarantine = sub.add_parser("managed-quarantine")
    managed_quarantine.add_argument("--path", required=True)
    quarantine_target = managed_quarantine.add_mutually_exclusive_group(required=True)
    quarantine_target.add_argument("--destination")
    quarantine_target.add_argument("--quarantine-parent")
    managed_quarantine.add_argument(
        "--kind", required=True, choices=("legacy-agent",)
    )
    shell_entry = sub.add_parser("shell-entry")
    shell_entry.add_argument(
        "--action",
        required=True,
        choices=("preflight-install", "preflight-remove", "install", "remove"),
    )
    shell_entry.add_argument("--path", required=True)
    shell_entry.add_argument("--profile")
    sub.add_parser("runtime-path")
    formal_ready = sub.add_parser("formal-schema-ready")
    formal_ready.add_argument("--requirements", required=True)
    classifier = sub.add_parser("classifier")
    classifier.add_argument("--action", required=True, choices=("preflight", "ensure"))
    classifier.add_argument("--path", required=True)
    managed_artifact = sub.add_parser("managed-artifact")
    managed_artifact.add_argument(
        "--action", required=True, choices=("inspect", "preflight", "install")
    )
    managed_artifact.add_argument("--kind", required=True, choices=("profile", "rules"))
    managed_artifact.add_argument("--path", required=True)
    managed_artifact.add_argument("--payload-file")
    config_fragment = sub.add_parser("config-fragment")
    config_fragment.add_argument("--action", required=True, choices=("merge", "remove"))
    config_fragment.add_argument("--path", required=True)
    config_fragment.add_argument("--preserve-empty", action="store_true")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "install":
            install(args)
        elif args.command == "remove":
            remove(args)
        elif args.command == "preflight-install":
            preflight_install(args)
        elif args.command == "preflight-remove":
            preflight_remove(args)
        elif args.command == "commands-install":
            install_command_group(
                command_artifacts_from_manifest(Path(args.manifest), require_data=True)
            )
        elif args.command == "command-owned":
            state = command_ownership_state(Path(args.path), args.name, args.kind)
            print(state)
            return 0 if state in {"absent", "managed"} else 1
        elif args.command == "managed-remove":
            print(remove_managed_artifact(Path(args.path), args.kind))
            return 0
        elif args.command == "managed-quarantine":
            print(
                quarantine_managed_artifact(
                    Path(args.path),
                    args.kind,
                    Path(args.destination) if args.destination else None,
                    quarantine_parent=(
                        Path(args.quarantine_parent)
                        if args.quarantine_parent
                        else None
                    ),
                )
            )
            return 0
        elif args.command == "shell-entry":
            action = args.action.removeprefix("preflight-")
            if args.action.startswith("preflight-"):
                print(preflight_shell_entry(Path(args.path), action))
            else:
                print(update_shell_entry(Path(args.path), action, args.profile))
            return 0
        elif args.command == "runtime-path":
            print(runtime_path())
            return 0
        elif args.command == "formal-schema-ready":
            formal_schema_dependency_ready(Path(args.requirements))
            return 0
        elif args.command == "classifier":
            action = preflight_classifier if args.action == "preflight" else ensure_classifier
            print(action(Path(args.path)))
            return 0
        elif args.command == "managed-artifact":
            path = Path(args.path)
            if args.action == "inspect":
                print(inspect_managed_artifact(path, args.kind))
                return 0
            if args.action == "preflight":
                print(preflight_managed_artifact(path, args.kind))
                return 0
            if not args.payload_file:
                raise Refusal("managed-artifact install requires --payload-file")
            payload_path = Path(args.payload_file)
            if not payload_path.is_absolute():
                raise Refusal(f"managed artifact payload path must be absolute: {payload_path}")
            payload_state = read_state(payload_path)
            if payload_state is None:
                raise Refusal(f"missing managed artifact payload: {payload_path}")
            print(install_managed_artifact(path, args.kind, payload_state.data))
            return 0
        elif args.command == "config-fragment":
            path = Path(args.path)
            if args.action == "merge":
                status = merge_config_fragment(path)
            else:
                status = remove_config_fragment(
                    path,
                    preserve_empty=args.preserve_empty,
                )
            print(status)
            return 0
        else:
            remove_command_group(
                command_artifacts_from_manifest(Path(args.manifest), require_data=False),
                test_fail_at=args.test_fail_at or None,
                preserve_foreign=args.preserve_foreign,
            )
    except (OSError, Refusal) as error:
        print(f"[error] {error}", file=sys.stderr)
        return 3
    print(f"[ok] repair artifacts {args.command} completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
