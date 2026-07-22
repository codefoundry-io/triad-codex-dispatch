import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_REPAIR = ROOT / "bin" / "bootstrap_repair.py"


def _load_bootstrap_repair_module():
    spec = importlib.util.spec_from_file_location(
        "bootstrap_repair_transaction_test", BOOTSTRAP_REPAIR
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_staged_cleanup_preserves_replacement_after_ownership_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "target"
    staged = helper.stage(target, b"owned staged bytes\n", 0o600)
    staged_path = getattr(staged, "path", staged)
    foreign_source = tmp_path / "foreign-staged-replacement"
    foreign = b"foreign staged replacement\n"
    foreign_source.write_bytes(foreign)
    original_same = helper.same
    swapped = False

    def swap_after_successful_check(state):
        nonlocal swapped
        matched = original_same(state)
        if state.path == staged_path and matched and not swapped:
            swapped = True
            os.replace(foreign_source, staged_path)
        return matched

    monkeypatch.setattr(helper, "same", swap_after_successful_check)

    with pytest.raises(helper.Refusal, match="path changed"):
        helper.cleanup(staged)

    assert swapped
    assert staged_path.read_bytes() == foreign


def test_failed_stage_cleanup_preserves_replacement_and_reports_recovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "target"
    foreign = b"foreign replacement during failed stage cleanup\n"
    staged_path: Path | None = None

    def replace_stage_then_fail_fsync(_fd):
        nonlocal staged_path
        candidates = list(tmp_path.glob(".target.*.tmp"))
        assert len(candidates) == 1
        staged_path = candidates[0]
        foreign_source = tmp_path / "foreign-stage-fsync"
        foreign_source.write_bytes(foreign)
        os.replace(foreign_source, staged_path)
        raise OSError("injected stage fsync failure")

    monkeypatch.setattr(helper.os, "fsync", replace_stage_then_fail_fsync)

    with pytest.raises(helper.TransactionFailure) as captured:
        helper.stage(target, b"owned staged bytes\n", 0o600)

    assert "injected stage fsync failure" in str(captured.value)
    assert "path changed" in str(captured.value)
    assert staged_path is not None
    assert staged_path.read_bytes() == foreign


def test_private_backup_cleanup_preserves_replacement_after_ownership_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "target"
    target.write_bytes(b"owned target bytes\n")
    expected = helper.read_state(target)
    assert expected is not None
    backup, backup_dir = helper._claim_expected(target, expected)
    foreign_source = tmp_path / "foreign-backup-replacement"
    foreign = b"foreign private backup replacement\n"
    foreign_source.write_bytes(foreign)
    original_same = helper.same
    swapped = False

    def swap_after_successful_check(state):
        nonlocal swapped
        matched = original_same(state)
        if state.path == backup.path and matched and not swapped:
            swapped = True
            os.replace(foreign_source, backup.path)
        return matched

    monkeypatch.setattr(helper, "same", swap_after_successful_check)

    with pytest.raises(helper.Refusal, match="path changed"):
        helper._cleanup_private_state(backup, backup_dir)

    assert swapped
    assert backup.path.read_bytes() == foreign
    assert backup_dir.is_dir()


def _managed_command_data(name: str, kind: str) -> bytes:
    if kind == "launcher":
        vendor_env, vendor_path = {
            "claude_wrapper.py": ("TRIAD_CLAUDE_BIN", "/usr/bin/claude"),
            "gemini_wrapper.py": ("TRIAD_GEMINI_BIN", "/usr/bin/gemini"),
            "antigravity_wrapper.py": ("TRIAD_AGY_BIN", "/usr/bin/agy"),
        }[name]
        return (
            b"#!/usr/bin/python3 -E\n"
            b"# triad-codex-dispatch managed launcher\n"
            b"import os\nimport sys\n"
            b"_SCRUB = (\n"
            b'    "LD_PRELOAD", "LD_LIBRARY_PATH", "LD_AUDIT", "LD_DEBUG",\n'
            b'    "DYLD_INSERT_LIBRARIES", "DYLD_LIBRARY_PATH", '
            b'"DYLD_FRAMEWORK_PATH",\n'
            b'    "NODE_OPTIONS", "NODE_PATH",\n'
            b'    "PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP",\n'
            b'    "BASH_ENV", "ENV", "PERL5LIB", "RUBYOPT", "RUBYLIB",\n'
            b")\n"
            b"env = {k: v for k, v in os.environ.items() if k not in _SCRUB}\n"
            b'env["PATH"] = "/usr/bin:/bin"\n'
            b'env["TRIAD_CLASSIFIER_EXTENSION"] = "/config/classifier.json"\n'
            b'env["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"\n'
            + f'env["{vendor_env}"] = "{vendor_path}"\n'.encode()
            + (
                'os.execve("/usr/bin/python3", ["/usr/bin/python3", "-E", '
                f'"/plugin/bin/{name}"] + sys.argv[1:], env)\n'
            ).encode()
        )
    return (
        b"#!/usr/bin/python3 -E\n"
        b"# triad-codex-dispatch managed runtime command\n"
        b"import os\nimport sys\n"
        + (
            'os.execv("/usr/bin/python3", ["/usr/bin/python3", "-E", '
            f'"/plugin/bin/triad_runtime.py", '
            f'{json.dumps(name.removeprefix("triad-"))}] + sys.argv[1:])\n'
        ).encode()
    )


def _command_artifacts(helper, tmp_path: Path):
    commands = (
        ("claude_wrapper.py", "launcher"),
        ("gemini_wrapper.py", "launcher"),
        ("antigravity_wrapper.py", "launcher"),
        ("triad-setup", "runtime"),
        ("triad-doctor", "runtime"),
    )
    return [
        helper.CommandArtifact(
            name=name,
            target=tmp_path / name,
            data=_managed_command_data(name, kind),
            kind=kind,
        )
        for name, kind in commands
    ]


@pytest.mark.parametrize("action", ("install", "remove"))
@pytest.mark.parametrize("placement", ("embedded", "later-line"))
def test_command_group_preserves_foreign_launcher_with_nonprovenance_marker(
    tmp_path: Path, action: str, placement: str
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "claude_wrapper.py"
    marker = "# triad-codex-dispatch managed launcher"
    if placement == "embedded":
        foreign = f'#!/usr/bin/env python3\nprint("{marker}")\n'.encode()
    else:
        foreign = f"#!/usr/bin/env python3\nprint('owner')\n{marker}\n".encode()
    target.write_bytes(foreign)
    artifact = helper.CommandArtifact(
        name="claude_wrapper.py",
        target=target,
        data=(
            b"#!/usr/bin/python3 -E\n"
            b"# triad-codex-dispatch managed launcher\n"
            b"import os\nimport sys\n"
            b'env["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"\n'
            b'os.execve("/usr/bin/python3", ["/usr/bin/python3", "-E", '
            b'"/plugin/bin/claude_wrapper.py"] + sys.argv[1:], env)\n'
        ),
        kind="launcher",
    )

    if action == "install":
        with pytest.raises(helper.Refusal, match="unmanaged command"):
            helper.install_command_group([artifact])
    else:
        helper.remove_command_group([artifact], preserve_foreign=True)

    assert target.read_bytes() == foreign


@pytest.mark.parametrize(
    ("name", "kind", "data"),
    (
        (
            "claude_wrapper.py",
            "launcher",
            b"#!/usr/bin/python3\n"
            b"# triad-codex-dispatch managed launcher\n"
            b"import os\nimport sys\n"
            b'os.environ["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"\n'
            b'os.environ["TRIAD_CLAUDE_BIN"] = "/usr/bin/claude"\n'
            b'os.execv("/usr/bin/python3", ["/usr/bin/python3", '
            b'"/plugin/bin/claude_wrapper.py"] + sys.argv[1:])\n',
        ),
        (
            "gemini_wrapper.py",
            "launcher",
            b"#!/usr/bin/python3\n"
            b"# triad-codex-dispatch managed launcher\n"
            b"import os\nimport sys\n"
            b'os.execv("/usr/bin/python3", ["/usr/bin/python3", '
            b'"/plugin/bin/gemini_wrapper.py"] + sys.argv[1:])\n',
        ),
        (
            "gemini_wrapper.py",
            "launcher",
            b"#!/usr/bin/python3\n"
            b"# triad-codex-dispatch managed launcher\n"
            b"import os\nimport sys\n"
            b'os.environ["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"\n'
            b'os.environ["TRIAD_GEMINI_BIN"] = "/usr/bin/gemini"\n'
            b'os.execv("/usr/bin/python3", ["/usr/bin/python3", '
            b'"/plugin/bin/gemini_wrapper.py"] + sys.argv[1:])\n',
        ),
        (
            "triad-setup",
            "runtime",
            b"#!/usr/bin/python3 -E\n"
            b"# triad-codex-dispatch managed runtime command\n"
            b"import os\nimport sys\n"
            b'os.execv("/usr/bin/python3", ["/usr/bin/python3", "-E", '
            b'"/plugin/bin/triad_runtime.py", "setup"] + sys.argv[1:])\n',
        ),
        (
            "triad-doctor",
            "runtime",
            b"#!/usr/bin/python3 -E\n"
            b"# triad-codex-dispatch managed runtime command\n"
            b"import os\nimport sys\n"
            b'os.execv("/usr/bin/python3", ["/usr/bin/python3", "-E", '
            b'"/plugin/bin/triad_runtime.py", "doctor"] + sys.argv[1:])\n',
        ),
    ),
)
def test_command_ownership_accepts_supported_historical_generated_grammar(
    tmp_path: Path, name: str, kind: str, data: bytes
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / name
    target.write_bytes(data)

    assert helper.command_ownership_state(target, name, kind) == "managed"


@pytest.mark.parametrize("mutation", ("arbitrary-body", "wrong-final-target"))
def test_command_ownership_rejects_altered_current_launcher_grammar(
    tmp_path: Path, mutation: str
) -> None:
    helper = _load_bootstrap_repair_module()
    data = _managed_command_data("claude_wrapper.py", "launcher")
    if mutation == "arbitrary-body":
        data = data.replace(
            b'env["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"\n',
            b'print("owner custom code")\n'
            b'env["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"\n',
        )
    else:
        data = data.replace(
            b'"/plugin/bin/claude_wrapper.py"] + sys.argv[1:]',
            b'"/plugin/bin/claude_wrapper.py/foreign"] + sys.argv[1:]',
        )
    target = tmp_path / "claude_wrapper.py"
    target.write_bytes(data)

    assert helper.command_ownership_state(
        target, "claude_wrapper.py", "launcher"
    ) == "unmanaged"


@pytest.mark.parametrize(
    ("name", "kind", "data"),
    (
        (
            "claude_wrapper.py",
            "launcher",
            _managed_command_data("claude_wrapper.py", "launcher").replace(
                b"#!/usr/bin/python3 -E\n", b"#!/foreign/python -E\n", 1
            ),
        ),
        (
            "claude_wrapper.py",
            "launcher",
            b"#!/foreign/python\n"
            b"# triad-codex-dispatch managed launcher\n"
            b"import os\nimport sys\n"
            b'os.environ["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"\n'
            b'os.environ["TRIAD_CLAUDE_BIN"] = "/usr/bin/claude"\n'
            b'os.execv("/usr/bin/python3", ["/usr/bin/python3", '
            b'"/plugin/bin/claude_wrapper.py"] + sys.argv[1:])\n',
        ),
        (
            "triad-setup",
            "runtime",
            b"#!/foreign/python -E\n"
            b"# triad-codex-dispatch managed runtime command\n"
            b"import os\nimport sys\n"
            b'os.execv("/usr/bin/python3", ["/usr/bin/python3", "-E", '
            b'"/plugin/bin/triad_runtime.py", "setup"] + sys.argv[1:])\n',
        ),
    ),
)
def test_command_ownership_rejects_shebang_exec_interpreter_mismatch(
    tmp_path: Path, name: str, kind: str, data: bytes
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / name
    target.write_bytes(data)

    assert helper.command_ownership_state(target, name, kind) == "unmanaged"


@pytest.mark.parametrize(
    "assignment",
    (
        b'os.environ["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"\n',
        b'os.environ["TRIAD_GEMINI_BIN"] = "/usr/bin/gemini"\n',
    ),
)
def test_command_ownership_rejects_partial_legacy_gemini_pin_grammar(
    tmp_path: Path, assignment: bytes
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / "gemini_wrapper.py"
    target.write_bytes(
        b"#!/usr/bin/python3\n"
        b"# triad-codex-dispatch managed launcher\n"
        b"import os\nimport sys\n"
        + assignment
        + b'os.execv("/usr/bin/python3", ["/usr/bin/python3", '
        b'"/plugin/bin/gemini_wrapper.py"] + sys.argv[1:])\n'
    )

    assert helper.command_ownership_state(
        target, "gemini_wrapper.py", "launcher"
    ) == "unmanaged"


def _invoke_command_group(
    helper,
    tmp_path: Path,
    artifact,
    *,
    action: str,
    entrypoint: str,
) -> int | None:
    if entrypoint == "api":
        if action == "install":
            helper.install_command_group([artifact])
        else:
            helper.remove_command_group([artifact], preserve_foreign=True)
        return

    payload = tmp_path / f"{artifact.name}.payload"
    payload.write_bytes(artifact.data)
    manifest = tmp_path / f"{artifact.name}.{action}.manifest"
    item = {
        "name": artifact.name,
        "kind": artifact.kind,
        "target": str(artifact.target),
        "mode": artifact.mode,
    }
    if action == "install":
        item["data_path"] = str(payload)
    manifest.write_text(json.dumps(item) + "\n", encoding="utf-8")
    argv = [f"commands-{action}", "--manifest", str(manifest)]
    if action == "remove":
        argv.append("--preserve-foreign")
    return helper.main(argv)


@pytest.mark.parametrize("entrypoint", ("api", "manifest"))
@pytest.mark.parametrize("action", ("install", "remove"))
def test_command_group_rejects_relative_target_before_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    entrypoint: str,
    action: str,
) -> None:
    helper = _load_bootstrap_repair_module()
    monkeypatch.chdir(tmp_path)
    data = b"# triad-codex-dispatch managed runtime command\nrelative\n"
    target = Path("relative-parent") / f"{entrypoint}-{action}"
    artifact = helper.CommandArtifact(
        name=f"relative-{entrypoint}-{action}",
        target=target,
        data=data,
        kind="runtime",
    )
    if action == "remove":
        target.parent.mkdir()
        target.write_bytes(data)

    if entrypoint == "api":
        with pytest.raises(helper.Refusal, match="must be absolute"):
            _invoke_command_group(
                helper, tmp_path, artifact, action=action, entrypoint=entrypoint
            )
    else:
        assert (
            _invoke_command_group(
                helper, tmp_path, artifact, action=action, entrypoint=entrypoint
            )
            == 3
        )

    if action == "install":
        assert not target.exists()
    else:
        assert target.read_bytes() == data


@pytest.mark.parametrize("entrypoint", ("api", "manifest"))
@pytest.mark.parametrize("action", ("install", "remove"))
def test_command_group_rejects_nested_symlink_parent_before_mutation(
    tmp_path: Path, entrypoint: str, action: str
) -> None:
    helper = _load_bootstrap_repair_module()
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(real_parent, target_is_directory=True)
    target = linked_parent / f"{entrypoint}-{action}"
    data = b"# triad-codex-dispatch managed runtime command\nsymlink parent\n"
    artifact = helper.CommandArtifact(
        name=f"symlink-parent-{entrypoint}-{action}",
        target=target,
        data=data,
        kind="runtime",
    )
    if action == "remove":
        target.write_bytes(data)

    if entrypoint == "api":
        with pytest.raises(helper.Refusal, match="unsafe ancestor"):
            _invoke_command_group(
                helper, tmp_path, artifact, action=action, entrypoint=entrypoint
            )
    else:
        assert (
            _invoke_command_group(
                helper, tmp_path, artifact, action=action, entrypoint=entrypoint
            )
            == 3
        )

    if action == "install":
        assert not target.exists()
    else:
        assert target.read_bytes() == data


@pytest.mark.parametrize("unmanaged_index", (2, 3, 5))
def test_install_command_group_preflights_every_target_before_mutation(
    tmp_path: Path, unmanaged_index: int
) -> None:
    helper = _load_bootstrap_repair_module()
    artifacts = _command_artifacts(helper, tmp_path)
    foreign = artifacts[unmanaged_index - 1]
    foreign.target.write_bytes(b"foreign command\n")

    with pytest.raises(helper.Refusal, match="unmanaged"):
        helper.install_command_group(artifacts)

    assert foreign.target.read_bytes() == b"foreign command\n"
    assert all(not artifact.target.exists() for artifact in artifacts if artifact != foreign)


def test_install_command_group_rolls_back_before_later_foreign_create(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    artifacts = _command_artifacts(helper, tmp_path)[:3]
    foreign = b"foreign later publication\n"
    original_link = helper.os.link

    def create_before_second_publication(source, target):
        if target == artifacts[1].target:
            target.write_bytes(foreign)
        return original_link(source, target)

    monkeypatch.setattr(helper.os, "link", create_before_second_publication)

    with pytest.raises(helper.Refusal, match="without overwriting"):
        helper.install_command_group(artifacts)

    assert not artifacts[0].target.exists()
    assert artifacts[1].target.read_bytes() == foreign
    assert not artifacts[2].target.exists()


def test_install_command_group_rolls_back_in_reverse_on_second_fsync_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    artifacts = _command_artifacts(helper, tmp_path)[:3]
    original_fsync_parent = helper.fsync_parent
    rollback_order: list[Path] = []
    failed = False

    def fail_second_parent_fsync(path: Path) -> None:
        nonlocal failed
        if path == artifacts[1].target and not failed:
            failed = True
            raise OSError("second publication fsync failure")
        original_fsync_parent(path)

    original_rollback = helper.rollback_mutation

    def record_reverse_rollback(mutation) -> None:
        rollback_order.append(mutation.target)
        original_rollback(mutation)

    monkeypatch.setattr(helper, "fsync_parent", fail_second_parent_fsync)
    monkeypatch.setattr(helper, "rollback_mutation", record_reverse_rollback)

    with pytest.raises(OSError, match="second publication fsync failure"):
        helper.install_command_group(artifacts)

    assert rollback_order == [artifacts[1].target, artifacts[0].target]
    assert all(not artifact.target.exists() for artifact in artifacts)
    assert not list(tmp_path.glob(".*.tmp"))
    assert not list(tmp_path.glob(".*.triad-claim-*"))


def test_install_command_group_rolls_back_on_keyboard_interrupt_after_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    artifacts = _command_artifacts(helper, tmp_path)[:2]
    prior = artifacts[0].data.replace(b"import sys\n", b"import sys\n# prior version\n")
    artifacts[0].target.write_bytes(prior)
    artifacts[0].target.chmod(0o701)
    original_fsync_parent = helper.fsync_parent
    interrupted = False
    interruption = KeyboardInterrupt("injected after command publication")

    def interrupt_after_first_publication(path: Path) -> None:
        nonlocal interrupted
        original_fsync_parent(path)
        if path == artifacts[0].target and not interrupted:
            interrupted = True
            raise interruption

    monkeypatch.setattr(helper, "fsync_parent", interrupt_after_first_publication)

    with pytest.raises(KeyboardInterrupt, match="after command publication") as captured:
        helper.install_command_group(artifacts)

    assert interrupted
    assert captured.value is interruption
    assert artifacts[0].target.read_bytes() == prior
    assert artifacts[0].target.stat().st_mode & 0o777 == 0o701
    assert not artifacts[1].target.exists()
    assert not list(tmp_path.glob(".*.tmp"))
    assert not list(tmp_path.glob(".*.triad-claim-*"))


def test_remove_command_group_rolls_back_on_keyboard_interrupt_after_removal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    artifacts = _command_artifacts(helper, tmp_path)[:2]
    for index, artifact in enumerate(artifacts):
        artifact.target.write_bytes(artifact.data)
        artifact.target.chmod(0o701 + index)
    before = {
        artifact.target: (
            artifact.target.read_bytes(),
            artifact.target.stat().st_mode & 0o777,
        )
        for artifact in artifacts
    }
    original_fsync_parent = helper.fsync_parent
    interrupted = False
    interruption = KeyboardInterrupt("injected after command removal")

    def interrupt_after_first_removal(path: Path) -> None:
        nonlocal interrupted
        original_fsync_parent(path)
        if path == artifacts[0].target and not interrupted:
            interrupted = True
            raise interruption

    monkeypatch.setattr(helper, "fsync_parent", interrupt_after_first_removal)

    with pytest.raises(KeyboardInterrupt, match="after command removal") as captured:
        helper.remove_command_group(artifacts)

    assert interrupted
    assert captured.value is interruption
    assert {
        artifact.target: (
            artifact.target.read_bytes(),
            artifact.target.stat().st_mode & 0o777,
        )
        for artifact in artifacts
    } == before
    assert not list(tmp_path.glob(".*.tmp"))
    assert not list(tmp_path.glob(".*.triad-claim-*"))


def test_remove_command_group_rolls_back_interrupt_immediately_after_claim_rename(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    artifact = _command_artifacts(helper, tmp_path)[0]
    artifact.target.write_bytes(artifact.data)
    artifact.target.chmod(0o701)
    before = (artifact.target.read_bytes(), artifact.target.stat().st_mode & 0o777)
    original_rename = helper.os.rename
    interruption = KeyboardInterrupt("injected immediately after claim rename")
    raised = False

    def rename_then_interrupt(source, target, *args, **kwargs):
        nonlocal raised
        result = original_rename(source, target, *args, **kwargs)
        if source == artifact.target and not raised:
            raised = True
            raise interruption
        return result

    monkeypatch.setattr(helper.os, "rename", rename_then_interrupt)

    with pytest.raises(KeyboardInterrupt, match="immediately after claim rename"):
        helper.remove_command_group([artifact])

    assert raised
    assert (
        artifact.target.read_bytes(),
        artifact.target.stat().st_mode & 0o777,
    ) == before
    assert not list(tmp_path.glob(".*.triad-claim-*"))


def test_install_command_group_rolls_back_interrupt_immediately_after_public_link(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    artifact = _command_artifacts(helper, tmp_path)[0]
    original_link = helper.os.link
    interruption = KeyboardInterrupt("injected immediately after public link")
    raised = False

    def link_then_interrupt(source, target, *args, **kwargs):
        nonlocal raised
        result = original_link(source, target, *args, **kwargs)
        if target == artifact.target and not raised:
            raised = True
            raise interruption
        return result

    monkeypatch.setattr(helper.os, "link", link_then_interrupt)

    with pytest.raises(KeyboardInterrupt, match="immediately after public link"):
        helper.install_command_group([artifact])

    assert raised
    assert not artifact.target.exists()
    assert not list(tmp_path.glob(".*.tmp"))
    assert not list(tmp_path.glob(".*.triad-claim-*"))


def test_install_command_group_rolls_back_on_keyboard_interrupt_during_cleanup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    artifacts = _command_artifacts(helper, tmp_path)[:2]
    prior = artifacts[0].data.replace(b"import sys\n", b"import sys\n# prior version\n")
    artifacts[0].target.write_bytes(prior)
    artifacts[0].target.chmod(0o703)
    original_cleanup = helper.cleanup
    interruption = KeyboardInterrupt("injected during staged cleanup")
    interrupted = False

    def cleanup_then_interrupt(temp) -> None:
        nonlocal interrupted
        original_cleanup(temp)
        if not interrupted:
            interrupted = True
            raise interruption

    monkeypatch.setattr(helper, "cleanup", cleanup_then_interrupt)

    with pytest.raises(KeyboardInterrupt, match="during staged cleanup") as captured:
        helper.install_command_group(artifacts)

    assert captured.value is interruption
    assert artifacts[0].target.read_bytes() == prior
    assert artifacts[0].target.stat().st_mode & 0o777 == 0o703
    assert not artifacts[1].target.exists()
    assert not list(tmp_path.glob(".*.tmp"))
    assert not list(tmp_path.glob(".*.triad-claim-*"))


def test_rollback_continues_after_keyboard_interrupt_recovery_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    artifacts = _command_artifacts(helper, tmp_path)[:3]
    before = {}
    for index, artifact in enumerate(artifacts):
        prior = artifact.data.replace(
            b"import sys\n", f"import sys\n# prior {index}\n".encode()
        )
        artifact.target.write_bytes(prior)
        artifact.target.chmod(0o701 + index)
        before[artifact.target] = (prior, 0o701 + index)

    original_fsync_parent = helper.fsync_parent
    primary = OSError("injected after third publication")
    publication_failed = False

    def fail_after_third_publication(path: Path) -> None:
        nonlocal publication_failed
        original_fsync_parent(path)
        if path == artifacts[2].target and not publication_failed:
            publication_failed = True
            raise primary

    original_rollback = helper.rollback_mutation
    interruption = KeyboardInterrupt("injected after first rollback")
    rollback_interrupted = False

    def rollback_then_interrupt(mutation) -> None:
        nonlocal rollback_interrupted
        original_rollback(mutation)
        if mutation.target == artifacts[2].target and not rollback_interrupted:
            rollback_interrupted = True
            raise interruption

    monkeypatch.setattr(helper, "fsync_parent", fail_after_third_publication)
    monkeypatch.setattr(helper, "rollback_mutation", rollback_then_interrupt)

    with pytest.raises(helper.TransactionFailure) as captured:
        helper.install_command_group(artifacts)

    assert captured.value.cause is primary
    assert interruption in captured.value.failures
    assert {
        artifact.target: (
            artifact.target.read_bytes(),
            artifact.target.stat().st_mode & 0o777,
        )
        for artifact in artifacts
    } == before
    assert not list(tmp_path.glob(".*.tmp"))
    assert not list(tmp_path.glob(".*.triad-claim-*"))


def test_install_command_group_rolls_back_when_staged_cleanup_fails_after_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    artifacts = _command_artifacts(helper, tmp_path)[:2]
    old = artifacts[0].data
    artifacts[0].target.write_bytes(old)
    original_cleanup_all = helper.cleanup_all
    commit_calls = 0

    def cleanup_then_report_failure(temps):
        failures = original_cleanup_all(temps)
        assert not failures
        return [OSError("injected post-publication staged cleanup failure")]

    original_commit_all = helper.commit_all

    def record_original_commit(journal):
        nonlocal commit_calls
        commit_calls += 1
        return original_commit_all(journal)

    monkeypatch.setattr(helper, "cleanup_all", cleanup_then_report_failure)
    monkeypatch.setattr(helper, "commit_all", record_original_commit)

    with pytest.raises(OSError, match="post-publication staged cleanup failure"):
        helper.install_command_group(artifacts)

    assert commit_calls == 0
    assert artifacts[0].target.read_bytes() == old
    assert not artifacts[1].target.exists()
    assert not list(tmp_path.glob(".*.tmp"))
    assert not list(tmp_path.glob(".*.triad-claim-*"))


@pytest.mark.parametrize("action", ("install", "remove"))
def test_command_group_commit_cleanup_failure_keeps_committed_state_without_rollback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, action: str
) -> None:
    helper = _load_bootstrap_repair_module()
    artifacts = _command_artifacts(helper, tmp_path)[:2]
    for artifact in artifacts:
        artifact.target.write_bytes(artifact.data)
    rollback_calls = 0

    def fail_commit_cleanup(_journal):
        return [OSError("injected committed backup cleanup failure")]

    def record_rollback(_journal):
        nonlocal rollback_calls
        rollback_calls += 1
        return []

    monkeypatch.setattr(helper, "commit_all", fail_commit_cleanup)
    monkeypatch.setattr(helper, "rollback_all", record_rollback)

    with pytest.raises(helper.TransactionFailure) as captured:
        if action == "install":
            helper.install_command_group(artifacts)
        else:
            helper.remove_command_group(artifacts)

    assert rollback_calls == 0
    assert "transaction committed but backup cleanup failed" in str(captured.value.cause)
    assert "injected committed backup cleanup failure" in str(captured.value)
    assert "rollback" not in str(captured.value)
    if action == "install":
        assert {artifact.target.read_bytes() for artifact in artifacts} == {
            artifact.data for artifact in artifacts
        }
    else:
        assert all(not artifact.target.exists() for artifact in artifacts)


def test_commit_cleanup_continues_after_keyboard_interrupt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    artifacts = _command_artifacts(helper, tmp_path)[:2]
    for index, artifact in enumerate(artifacts):
        prior = artifact.data.replace(
            b"import sys\n", f"import sys\n# prior {index}\n".encode()
        )
        artifact.target.write_bytes(prior)
    original_cleanup_private_state = helper._cleanup_private_state
    interruption = KeyboardInterrupt("injected during commit cleanup")
    interrupted = False

    def cleanup_then_interrupt(state, directory) -> None:
        nonlocal interrupted
        original_cleanup_private_state(state, directory)
        if not interrupted:
            interrupted = True
            raise interruption

    monkeypatch.setattr(helper, "_cleanup_private_state", cleanup_then_interrupt)

    with pytest.raises(helper.TransactionFailure) as captured:
        helper.install_command_group(artifacts)

    assert interruption in captured.value.failures
    assert all(artifact.target.read_bytes() == artifact.data for artifact in artifacts)
    assert not list(tmp_path.glob(".*.tmp"))
    assert not list(tmp_path.glob(".*.triad-claim-*"))


def _repair_args(helper, tmp_path: Path, *, existing_config: bool = False):
    source = tmp_path / "source.toml"
    source.write_text(
        f'{helper.ANALYZER_MARKER}\nname = "{helper.NAME}"\nversion = 1\n',
        encoding="utf-8",
    )
    apply_patch = tmp_path / "apply_patch.py"
    apply_patch.write_text("# apply\n", encoding="utf-8")
    config = tmp_path / "config.toml"
    if existing_config:
        config.write_text('owner = "preserve"\n', encoding="utf-8")
    analyzer = tmp_path / "agents" / f"{helper.NAME}.toml"
    launcher = tmp_path / "triad-apply-repair"
    args = helper.parser().parse_args(
        [
            "install",
            "--source",
            str(source),
            "--config",
            str(config),
            "--analyzer",
            str(analyzer),
            "--launcher",
            str(launcher),
            "--apply-patch",
            str(apply_patch),
        ]
    )
    return args, source, config, analyzer, launcher


def _inject_cleanup_failure_after_real_cleanup(helper, monkeypatch):
    original_cleanup_all = helper.cleanup_all

    def cleanup_then_report_failure(temps):
        failures = original_cleanup_all(temps)
        assert not failures
        return [OSError("injected post-publication staged cleanup failure")]

    monkeypatch.setattr(helper, "cleanup_all", cleanup_then_report_failure)


def test_repair_install_rolls_back_when_staged_cleanup_fails_after_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    args, source, config, analyzer, launcher = _repair_args(helper, tmp_path)
    helper.install(args)
    before = {path: path.read_bytes() for path in (config, analyzer, launcher)}
    source.write_text(
        f'{helper.ANALYZER_MARKER}\nname = "{helper.NAME}"\nversion = 2\n',
        encoding="utf-8",
    )
    commit_calls = 0
    original_commit_all = helper.commit_all

    def record_commit(journal):
        nonlocal commit_calls
        commit_calls += 1
        return original_commit_all(journal)

    _inject_cleanup_failure_after_real_cleanup(helper, monkeypatch)
    monkeypatch.setattr(helper, "commit_all", record_commit)

    with pytest.raises(OSError, match="post-publication staged cleanup failure"):
        helper.install(args)

    assert commit_calls == 0
    assert {path: path.read_bytes() for path in (config, analyzer, launcher)} == before
    assert not list(tmp_path.rglob(".*.tmp"))
    assert not list(tmp_path.rglob(".*.triad-claim-*"))


def test_repair_remove_rolls_back_when_staged_cleanup_fails_after_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    args, _source, config, analyzer, launcher = _repair_args(
        helper, tmp_path, existing_config=True
    )
    helper.install(args)
    before = {path: path.read_bytes() for path in (config, analyzer, launcher)}
    remove_args = helper.parser().parse_args(
        [
            "remove",
            "--config",
            str(config),
            "--analyzer",
            str(analyzer),
            "--launcher",
            str(launcher),
        ]
    )
    commit_calls = 0
    original_commit_all = helper.commit_all

    def record_commit(journal):
        nonlocal commit_calls
        commit_calls += 1
        return original_commit_all(journal)

    _inject_cleanup_failure_after_real_cleanup(helper, monkeypatch)
    monkeypatch.setattr(helper, "commit_all", record_commit)

    with pytest.raises(OSError, match="post-publication staged cleanup failure"):
        helper.remove(remove_args)

    assert commit_calls == 0
    assert {path: path.read_bytes() for path in (config, analyzer, launcher)} == before
    assert not list(tmp_path.rglob(".*.tmp"))
    assert not list(tmp_path.rglob(".*.triad-claim-*"))


def test_remove_command_group_preflights_every_target_before_mutation(tmp_path: Path) -> None:
    helper = _load_bootstrap_repair_module()
    artifacts = _command_artifacts(helper, tmp_path)
    for artifact in artifacts:
        artifact.target.write_bytes(artifact.data)
        artifact.target.chmod(artifact.mode)
    artifacts[2].target.write_bytes(b"foreign command\n")
    before = {artifact.target: artifact.target.read_bytes() for artifact in artifacts}

    with pytest.raises(helper.Refusal, match="unmanaged"):
        helper.remove_command_group(artifacts)

    assert {artifact.target: artifact.target.read_bytes() for artifact in artifacts} == before


def test_classifier_ensure_refuses_dangling_symlink_after_absent_preflight(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    classifier = tmp_path / "classifier" / "patches.json"
    external = tmp_path / "external-classifier"

    assert helper.preflight_classifier(classifier) == "absent"
    classifier.parent.mkdir()
    classifier.symlink_to(external)

    with pytest.raises(helper.Refusal, match="unsafe path"):
        helper.ensure_classifier(classifier)

    assert classifier.is_symlink()
    assert not external.exists()


def test_classifier_ensure_creates_with_current_umask_and_never_clobbers(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    classifier = tmp_path / "classifier" / "patches.json"
    original_umask = os.umask(0o027)
    try:
        assert helper.ensure_classifier(classifier) == "created"
    finally:
        os.umask(original_umask)

    assert classifier.read_bytes() == b"{}\n"
    assert classifier.stat().st_mode & 0o777 == 0o640
    assert helper.ensure_classifier(classifier) == "ready"


@pytest.mark.parametrize(
    ("kind", "marker"),
    (
        ("profile", b"# triad-codex-dispatch managed runtime profile"),
        ("rules", b"# triad-codex-dispatch managed command rules"),
    ),
)
def test_managed_artifact_requires_exact_first_logical_line(
    tmp_path: Path, kind: str, marker: bytes
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / kind
    target.write_bytes(b"# owner line\n" + marker + b"\n")

    with pytest.raises(helper.Refusal, match="unmanaged"):
        helper.preflight_managed_artifact(target, kind)


@pytest.mark.parametrize(
    ("kind", "marker"),
    (
        ("profile", b"# triad-codex-dispatch managed runtime profile"),
        ("rules", b"# triad-codex-dispatch managed command rules"),
    ),
)
def test_managed_artifact_install_preserves_regular_replacement_after_capture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    marker: bytes,
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / kind
    target.write_bytes(marker + b"\nold\n")
    foreign = b"foreign regular replacement\n"
    original_stage = helper.stage
    swapped = False

    def stage_then_swap(path, data, mode):
        nonlocal swapped
        staged = original_stage(path, data, mode)
        if path == target and not swapped:
            replacement = tmp_path / f"{kind}-foreign"
            replacement.write_bytes(foreign)
            os.replace(replacement, target)
            swapped = True
        return staged

    monkeypatch.setattr(helper, "stage", stage_then_swap)

    with pytest.raises(helper.Refusal, match="path changed"):
        helper.install_managed_artifact(target, kind, marker + b"\nnew\n")

    assert swapped
    assert target.read_bytes() == foreign


def test_managed_artifact_install_preserves_existing_mode_and_new_umask(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    marker = b"# triad-codex-dispatch managed runtime profile"
    existing = tmp_path / "existing-profile"
    existing.write_bytes(marker + b"\nold\n")
    existing.chmod(0o604)

    assert helper.install_managed_artifact(existing, "profile", marker + b"\nnew\n") == "updated"
    assert existing.stat().st_mode & 0o777 == 0o604

    created = tmp_path / "created-profile"
    original_umask = os.umask(0o027)
    try:
        assert helper.install_managed_artifact(created, "profile", marker + b"\nnew\n") == "created"
    finally:
        os.umask(original_umask)
    assert created.stat().st_mode & 0o777 == 0o640


def test_shell_entry_transaction_preserves_existing_mode_and_owner_bytes(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    shell_rc = tmp_path / "shellrc"
    owner = b"# owner bytes before managed block\r\n"
    block = (
        b"# >>> triad-codex-dispatch codex-triad >>>\n"
        b"codex-triad() { :; }\n"
        b"# <<< triad-codex-dispatch codex-triad <<<\n"
    )
    shell_rc.write_bytes(owner + block)
    shell_rc.chmod(0o604)

    assert (
        helper.update_shell_entry(shell_rc, "install", "triad-codex-dispatch")
        == "installed"
    )
    assert shell_rc.stat().st_mode & 0o777 == 0o604
    assert shell_rc.read_bytes().startswith(owner)
    assert shell_rc.read_bytes().count(helper.SHELL_ENTRY_BEGIN) == 1
    assert helper.update_shell_entry(shell_rc, "remove", None) == "removed"
    assert shell_rc.stat().st_mode & 0o777 == 0o604
    assert shell_rc.read_bytes() == owner


def test_managed_quarantine_rolls_back_without_clobbering_foreign_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    source = tmp_path / "agents" / "claude-wrapper-repair.toml"
    source.parent.mkdir()
    managed = (
        b"# Codex named subagent for Claude wrapper repair agent\n"
        b"# Installed by bootstrap to the Codex personal agent-discovery scope\n"
        b'name = "claude-wrapper-repair"\n'
    )
    source.write_bytes(managed)
    source.chmod(0o604)
    destination = tmp_path / "quarantine" / source.name
    destination.parent.mkdir()
    foreign = b"foreign quarantine destination\n"
    original_link = helper.os.link
    injected = False

    def create_destination_before_publish(link_source, link_target, *args, **kwargs):
        nonlocal injected
        if Path(link_target) == destination and not injected:
            destination.write_bytes(foreign)
            injected = True
        return original_link(link_source, link_target, *args, **kwargs)

    monkeypatch.setattr(helper.os, "link", create_destination_before_publish)

    with pytest.raises(helper.Refusal, match="publish without overwriting"):
        helper.quarantine_managed_artifact(source, "legacy-agent", destination)

    assert injected
    assert source.read_bytes() == managed
    assert source.stat().st_mode & 0o777 == 0o604
    assert destination.read_bytes() == foreign


def test_managed_quarantine_preserves_captured_bytes_and_mode(
    tmp_path: Path,
) -> None:
    helper = _load_bootstrap_repair_module()
    source = tmp_path / "agents" / "claude-wrapper-repair.toml"
    source.parent.mkdir()
    managed = (
        b"# Codex named subagent for Claude wrapper repair agent\n"
        b"# Installed by bootstrap to the Codex personal agent-discovery scope\n"
        b'name = "claude-wrapper-repair"\n'
    )
    source.write_bytes(managed)
    source.chmod(0o604)

    assert (
        helper.quarantine_managed_artifact(
            source, "legacy-agent", quarantine_parent=tmp_path
        )
        == "quarantined"
    )
    quarantine_dirs = list(tmp_path.glob(".triad-quarantine-*"))
    assert len(quarantine_dirs) == 1
    destination = quarantine_dirs[0] / source.name
    assert not source.exists()
    assert destination.read_bytes() == managed
    assert destination.stat().st_mode & 0o777 == 0o604


@pytest.mark.parametrize("backup_kind", ("regular", "live-symlink", "dangling-symlink"))
def test_config_fragment_merge_uses_bak2_without_mutating_existing_backup(
    tmp_path: Path, backup_kind: str
) -> None:
    helper = _load_bootstrap_repair_module()
    config = tmp_path / "config.toml"
    original = b'owner = "preserve"\n'
    config.write_bytes(original)
    backup = Path(str(config) + ".bak")
    external = tmp_path / "external-backup"
    if backup_kind == "regular":
        backup.write_bytes(b"foreign backup\n")
    else:
        if backup_kind == "live-symlink":
            external.write_bytes(b"external backup target\n")
        backup.symlink_to(external)

    assert helper.merge_config_fragment(config) == "merged"

    assert config.read_bytes() != original
    assert config.read_bytes().startswith(original)
    if backup_kind == "regular":
        assert backup.read_bytes() == b"foreign backup\n"
    else:
        assert backup.is_symlink()
        if backup_kind == "live-symlink":
            assert external.read_bytes() == b"external backup target\n"
        else:
            assert not external.exists()
    assert Path(str(config) + ".bak2").read_bytes() == original


def test_config_fragment_merge_uses_first_free_numbered_backup(tmp_path: Path) -> None:
    helper = _load_bootstrap_repair_module()
    config = tmp_path / "config.toml"
    original = b'owner = "preserve"\n'
    config.write_bytes(original)
    Path(str(config) + ".bak").write_bytes(b"first backup\n")
    Path(str(config) + ".bak2").write_bytes(b"second backup\n")

    assert helper.merge_config_fragment(config) == "merged"

    assert Path(str(config) + ".bak").read_bytes() == b"first backup\n"
    assert Path(str(config) + ".bak2").read_bytes() == b"second backup\n"
    assert Path(str(config) + ".bak3").read_bytes() == original


def test_config_fragment_merge_keeps_backup_and_preserves_concurrent_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    config = tmp_path / "config.toml"
    original = b'owner = "preserve"\n'
    foreign = b'owner = "concurrent"\n'
    config.write_bytes(original)
    original_publish = helper.publish_to
    swapped = False

    def swap_before_config_publish(temp, target, expected, journal):
        nonlocal swapped
        if target == config and not swapped:
            replacement = tmp_path / "config-concurrent"
            replacement.write_bytes(foreign)
            os.replace(replacement, config)
            swapped = True
        return original_publish(temp, target, expected, journal)

    monkeypatch.setattr(helper, "publish_to", swap_before_config_publish)

    with pytest.raises(helper.Refusal, match="path changed"):
        helper.merge_config_fragment(config)

    assert swapped
    assert config.read_bytes() == foreign
    assert Path(str(config) + ".bak").read_bytes() == original


def test_config_fragment_remove_preserves_concurrent_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _load_bootstrap_repair_module()
    config = tmp_path / "config.toml"
    original = (
        b'# prefix\nowner = "preserve"\n\n'
        + helper.current_config_fragment(b"\n")
        + b"\n# suffix\n"
    )
    foreign = b'owner = "concurrent"\n'
    config.write_bytes(original)
    original_publish = helper.publish_to
    swapped = False

    def swap_before_config_publish(temp, target, expected, journal):
        nonlocal swapped
        if target == config and not swapped:
            replacement = tmp_path / "config-remove-concurrent"
            replacement.write_bytes(foreign)
            os.replace(replacement, config)
            swapped = True
        return original_publish(temp, target, expected, journal)

    monkeypatch.setattr(helper, "publish_to", swap_before_config_publish)

    with pytest.raises(helper.Refusal, match="path changed"):
        helper.remove_config_fragment(config)

    assert swapped
    assert config.read_bytes() == foreign


def test_narrow_bootstrap_commands_emit_only_path_or_status(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    helper = _load_bootstrap_repair_module()

    assert helper.main(["runtime-path"]) == 0
    assert Path(capsys.readouterr().out.strip()).is_absolute()

    classifier = tmp_path / "classifier" / "patches.json"
    assert helper.main(
        ["classifier", "--action", "preflight", "--path", str(classifier)]
    ) == 0
    assert capsys.readouterr().out == "absent\n"
    assert helper.main(
        ["classifier", "--action", "ensure", "--path", str(classifier)]
    ) == 0
    assert capsys.readouterr().out == "created\n"

    profile = tmp_path / "profile.toml"
    payload = tmp_path / "profile.payload"
    payload.write_bytes(b"# triad-codex-dispatch managed runtime profile\nbody\n")
    assert helper.main(
        [
            "managed-artifact",
            "--action",
            "preflight",
            "--kind",
            "profile",
            "--path",
            str(profile),
        ]
    ) == 0
    assert capsys.readouterr().out == "absent\n"
    assert helper.main(
        [
            "managed-artifact",
            "--action",
            "install",
            "--kind",
            "profile",
            "--path",
            str(profile),
            "--payload-file",
            str(payload),
        ]
    ) == 0
    assert capsys.readouterr().out == "created\n"

    config = tmp_path / "config.toml"
    assert helper.main(
        ["config-fragment", "--action", "merge", "--path", str(config)]
    ) == 0
    assert capsys.readouterr().out == "merged\n"
    assert helper.main(
        ["config-fragment", "--action", "remove", "--path", str(config)]
    ) == 0
    assert capsys.readouterr().out == "removed-file\n"


@pytest.mark.parametrize(
    ("kind", "marker"),
    (
        ("profile", b"# triad-codex-dispatch managed runtime profile"),
        ("rules", b"# triad-codex-dispatch managed command rules"),
    ),
)
@pytest.mark.parametrize("placement", ("embedded", "later-line"))
def test_managed_removal_requires_marker_on_exact_first_logical_line(
    tmp_path: Path, kind: str, marker: bytes, placement: str
) -> None:
    helper = _load_bootstrap_repair_module()
    target = tmp_path / kind
    if placement == "embedded":
        original = b'owner = "' + marker + b'"\n'
    else:
        original = b"# owner file\n" + marker + b"\n"
    target.write_bytes(original)

    assert helper.remove_managed_artifact(target, kind) == "unmanaged"
    assert target.read_bytes() == original


@pytest.mark.parametrize("existing", (False, True), ids=("absent", "existing"))
def test_config_fragment_merge_uses_private_new_mode_and_preserves_existing_mode(
    tmp_path: Path, existing: bool
) -> None:
    helper = _load_bootstrap_repair_module()
    config = tmp_path / "config.toml"
    if existing:
        config.write_bytes(b'owner = "preserve"\n')
        config.chmod(0o644)

    original_umask = os.umask(0)
    try:
        assert helper.merge_config_fragment(config) == "merged"
    finally:
        os.umask(original_umask)

    expected_mode = 0o644 if existing else 0o600
    assert config.stat().st_mode & 0o777 == expected_mode
