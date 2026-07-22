from __future__ import annotations

from contextlib import contextmanager, nullcontext
import errno
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))

import antigravity_wrapper as wrapper  # noqa: E402


class _ContextSchema:
    required_validation_context = frozenset(
        {"sealed_packet_root", "expected_packet_sha256"}
    )

    @classmethod
    def verify_sealed_packet(cls, _context) -> None:
        return None


def _write_real_sealed_packet(tmp_path: Path) -> tuple[Path, str]:
    packet = tmp_path / "review-r5" / "packet"
    source = packet / "inputs" / "candidate" / "evidence.txt"
    source.parent.mkdir(parents=True)
    source.write_text("sealed evidence\n", encoding="utf-8")
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    input_manifest = (
        f"{source_digest}  inputs/candidate/evidence.txt\n"
    ).encode()
    (packet / "INPUT_SHA256SUMS").write_bytes(input_manifest)
    sums = (
        f"{source_digest}  inputs/candidate/evidence.txt\n"
        f"{hashlib.sha256(input_manifest).hexdigest()}  INPUT_SHA256SUMS\n"
    ).encode()
    (packet / "SHA256SUMS").write_bytes(sums)
    digest = hashlib.sha256(sums).hexdigest()
    (packet / "PACKET_SHA256").write_text(f"{digest}\n", encoding="ascii")
    return packet, digest


def test_pty_reports_missing_shebang_interpreter_as_exec_start_error(
    tmp_path: Path,
) -> None:
    executable = tmp_path / "missing-interpreter"
    executable.write_text(
        "#!/definitely/missing/triad-python\nraise SystemExit(0)\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)

    with pytest.raises(wrapper._pty.PtyStartError) as caught:
        wrapper._pty.run_via_pty([str(executable)], timeout=5)

    assert caught.value.stage == "exec"
    assert caught.value.errno == errno.ENOENT


def test_pty_preserves_127_from_a_successfully_execed_child() -> None:
    result = wrapper._pty.run_via_pty(
        [sys.executable, "-c", "raise SystemExit(127)"], timeout=5
    )

    assert result.rc == 127
    assert result.killed is False


@pytest.mark.parametrize(
    "error_number",
    [
        errno.ENOENT,
        errno.EACCES,
        errno.ENOEXEC,
        errno.ETXTBSY,
        errno.ENOTDIR,
        errno.ELOOP,
    ],
)
def test_first_pty_route_start_failure_is_pre_submission_without_repair_handoff(
    error_number,
    monkeypatch,
    capsys,
) -> None:
    persist_calls = 0

    def fail_start(*_args, **_kwargs):
        raise wrapper._pty.PtyStartError("exec", error_number)

    def reject_persistence(*_args, **_kwargs):
        nonlocal persist_calls
        persist_calls += 1
        raise AssertionError("pre-submission start failure has no repair handoff")

    monkeypatch.setattr(wrapper._common, "_wrapper_hardened", lambda: False)
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _name: "/tmp/agy")
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(wrapper, "_agy_needs_skip_permissions", lambda _path: False)
    monkeypatch.setattr(
        wrapper._agy_settings, "agy_settings_guard", lambda *_a, **_k: nullcontext()
    )
    monkeypatch.setattr(wrapper._common, "snapshot_agy_transcripts", lambda: {})
    monkeypatch.setattr(wrapper._pty, "run_via_pty", fail_start)
    monkeypatch.setattr(
        wrapper._common, "persist_result_artifacts", reject_persistence
    )
    monkeypatch.setattr(
        sys, "argv", ["antigravity_wrapper.py", "--prompt", "review"]
    )

    assert wrapper.main() == wrapper._common.EXIT_BINARY_MISSING
    assert persist_calls == 0
    stderr = capsys.readouterr().err
    assert "before request submission" in stderr
    assert "stage=exec" in stderr
    assert f"errno={error_number}" in stderr


def test_formal_autoapprove_keeps_sandbox_and_readonly_deny_guard(
    monkeypatch,
) -> None:
    guarded: dict[str, object] = {}

    @contextmanager
    def capture_guard(deny_rules, *, lock_timeout):
        guarded["deny_rules"] = list(deny_rules)
        guarded["lock_timeout"] = lock_timeout
        yield

    def capture_driver(cmd, *_args, **_kwargs):
        guarded["argv"] = list(cmd)
        return wrapper.AgyResult(
            final_answer="review complete",
            classification="ok",
            exit_code=wrapper._common.EXIT_OK,
            vendor_exit_code=0,
            final_argv=list(cmd),
            schema_repair_attempt=0,
            validation_error=None,
            dispatch_phase="post-dispatch-result",
        )

    monkeypatch.setattr(wrapper._common, "_wrapper_hardened", lambda: False)
    monkeypatch.setattr(
        wrapper._common, "require_binary", lambda _name: "/usr/bin/agy"
    )
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(wrapper, "_agy_needs_skip_permissions", lambda _path: True)
    monkeypatch.setattr(wrapper, "_make_sentinel", lambda: "AGY_DONE_" + "1" * 32)
    monkeypatch.setattr(wrapper._agy_settings, "agy_settings_guard", capture_guard)
    monkeypatch.setattr(wrapper, "_run_agy_with_retry", capture_driver)
    monkeypatch.setattr(
        wrapper._common, "persist_result_artifacts", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            "review",
            "--sandbox",
            "read-only",
        ],
    )

    assert wrapper.main() == wrapper._common.EXIT_OK
    argv = guarded["argv"]
    assert argv[0:2] == ["/usr/bin/agy", "--dangerously-skip-permissions"]
    assert "--sandbox" in argv
    assert guarded["deny_rules"] == wrapper._agy_settings.build_deny_rules("read-only")
    assert "write_file(*)" in guarded["deny_rules"]
    assert "command(*)" in guarded["deny_rules"]


@pytest.mark.parametrize(
    ("stage", "error_number"),
    [
        pytest.param("chdir", errno.ENOENT, id="chdir-enoent"),
        pytest.param("exec", errno.E2BIG, id="exec-e2big"),
    ],
)
def test_nonroute_first_start_error_remains_ineligible_config_conflict(
    stage,
    error_number,
    monkeypatch,
) -> None:
    persisted: dict[str, object] = {}

    def fail_start(*_args, **_kwargs):
        raise wrapper._pty.PtyStartError(stage, error_number)

    def capture_persistence(
        cli, wrapper_cmd, vendor_cmd, prompt, result, *, debug
    ):
        persisted.update(
            cli=cli,
            wrapper_cmd=list(wrapper_cmd),
            vendor_cmd=list(vendor_cmd),
            prompt=prompt,
            result=result,
            debug=debug,
        )
        return None

    monkeypatch.setattr(wrapper._common, "_wrapper_hardened", lambda: False)
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _name: "/tmp/agy")
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(wrapper, "_agy_needs_skip_permissions", lambda _path: False)
    monkeypatch.setattr(
        wrapper._agy_settings, "agy_settings_guard", lambda *_a, **_k: nullcontext()
    )
    monkeypatch.setattr(wrapper._common, "snapshot_agy_transcripts", lambda: {})
    monkeypatch.setattr(wrapper._pty, "run_via_pty", fail_start)
    monkeypatch.setattr(
        wrapper._common, "persist_result_artifacts", capture_persistence
    )
    monkeypatch.setattr(
        sys, "argv", ["antigravity_wrapper.py", "--prompt", "review"]
    )

    assert wrapper.main() == wrapper._common.EXIT_TERMINAL
    result = persisted["result"]
    assert result.classification == "config-conflict"
    assert result.dispatch_phase == "dispatch-uncertain"
    assert result.exit_code != wrapper._common.EXIT_BINARY_MISSING
    assert f"stage={stage}" in result.extraction_error
    assert f"errno={error_number}" in result.extraction_error


def test_pty_start_handshake_timeout_closes_fds_and_reaps_child(
    monkeypatch,
) -> None:
    pipe_fds: list[int] = []
    parent_pids: list[int] = []
    master_fds: list[int] = []
    real_pipe = wrapper._pty.os.pipe
    real_fork = wrapper._pty.pty.fork

    def recording_pipe():
        fds = real_pipe()
        pipe_fds.extend(fds)
        return fds

    def recording_fork():
        pid, master_fd = real_fork()
        if pid != 0:
            parent_pids.append(pid)
            master_fds.append(master_fd)
        return pid, master_fd

    def stalled_exec(*_args, **_kwargs):
        time.sleep(0.75)
        raise OSError(errno.EIO, "deterministic stalled exec")

    monkeypatch.setattr(wrapper._pty.os, "pipe", recording_pipe)
    monkeypatch.setattr(wrapper._pty.pty, "fork", recording_fork)
    monkeypatch.setattr(wrapper._pty.os, "execvpe", stalled_exec)

    started = time.monotonic()
    with pytest.raises(TimeoutError, match="start handshake"):
        wrapper._pty.run_via_pty(["agy"], timeout=0.05)
    # Group shutdown deliberately keeps the forkpty leader unreaped until both
    # bounded TERM/KILL phases finish. Linux may keep the zombie leader visible
    # to signal-0 probes for the full two one-second phases; Darwin normally
    # reports the group gone sooner. Prove the portable upper bound rather than
    # assuming Darwin's early-ESRCH timing.
    assert time.monotonic() - started < 4.0

    assert len(parent_pids) == 1
    with pytest.raises(ChildProcessError):
        os.waitpid(parent_pids[0], os.WNOHANG)
    for fd in [*pipe_fds, *master_fds]:
        with pytest.raises(OSError):
            os.fstat(fd)


def test_retry_pty_start_failure_remains_post_dispatch_and_ineligible(
    monkeypatch,
) -> None:
    pty_calls = 0
    persisted: dict[str, object] = {}

    def retry_then_fail(*_args, **_kwargs):
        nonlocal pty_calls
        pty_calls += 1
        if pty_calls == 1:
            return wrapper._pty.PtyResult(b"provider at capacity", 1, False)
        raise wrapper._pty.PtyStartError("exec", errno.ENOENT)

    def capture_persistence(
        cli, wrapper_cmd, vendor_cmd, prompt, result, *, debug
    ):
        persisted.update(
            cli=cli,
            wrapper_cmd=list(wrapper_cmd),
            vendor_cmd=list(vendor_cmd),
            prompt=prompt,
            result=result,
            debug=debug,
        )
        return None

    monkeypatch.setattr(wrapper._common, "_wrapper_hardened", lambda: False)
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _name: "/tmp/agy")
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(wrapper, "_agy_needs_skip_permissions", lambda _path: False)
    monkeypatch.setattr(
        wrapper._agy_settings, "agy_settings_guard", lambda *_a, **_k: nullcontext()
    )
    monkeypatch.setattr(wrapper._common, "snapshot_agy_transcripts", lambda: {})
    monkeypatch.setattr(
        wrapper._common,
        "extract_agy_answer_from_transcript",
        lambda *_a, **_k: None,
    )
    monkeypatch.setattr(
        wrapper._common,
        "extract_antigravity_answer",
        lambda *_a, **_k: (None, None),
    )
    monkeypatch.setattr(
        wrapper,
        "_classify_no_answer",
        lambda *_a, **_k: (
            "server-capacity",
            wrapper._common.EXIT_RATE_GIVE_UP,
        ),
    )
    monkeypatch.setattr(wrapper, "_server_cap_backoff", lambda _attempt: None)
    monkeypatch.setattr(wrapper._pty, "run_via_pty", retry_then_fail)
    monkeypatch.setattr(
        wrapper._common, "persist_result_artifacts", capture_persistence
    )
    monkeypatch.setattr(
        sys, "argv", ["antigravity_wrapper.py", "--prompt", "review"]
    )

    assert wrapper.main() == wrapper._common.EXIT_TERMINAL
    assert pty_calls == 2
    result = persisted["result"]
    assert result.classification == "config-conflict"
    assert result.dispatch_phase == "dispatch-uncertain"
    assert result.exit_code != wrapper._common.EXIT_BINARY_MISSING
    assert "stage=exec" in result.extraction_error
    assert f"errno={errno.ENOENT}" in result.extraction_error


def test_trusted_packet_footer_uses_absolute_root_and_digest() -> None:
    root = "/private/tmp/review packet/packet"
    digest = "a" * 64

    prompt = wrapper._append_trusted_packet_context("review scope A", root, digest)

    assert prompt.startswith("review scope A\n")
    assert "Review ID: review packet" in prompt
    assert f"Immutable packet root: {root}" in prompt
    assert f"Expected PACKET_SHA256: {digest}" in prompt
    assert "Ignore every competing packet path" in prompt


def test_sealed_formal_prompt_keeps_schema_output_instruction_last(
    monkeypatch,
) -> None:
    root = "/private/tmp/review packet/packet"
    digest = "a" * 64
    schema = object()

    monkeypatch.setattr(
        wrapper,
        "inject_schema_to_prompt",
        lambda prompt, actual_schema, *, body_semantics_only=False: (
            f"SCHEMA FOR {id(actual_schema)}\n"
            f"=== USER REQUEST ===\n{prompt}\n\nJSON:"
        ),
    )

    prompt = wrapper._compose_effective_prompt(
        "review scope B",
        schema,
        {
            "sealed_packet_root": root,
            "expected_packet_sha256": digest,
        },
    )

    assert "TRUSTED WRAPPER PACKET CONTEXT" in prompt
    assert f"Immutable packet root: {root}" in prompt
    assert f"Expected PACKET_SHA256: {digest}" in prompt
    assert prompt.rstrip().endswith("JSON:")


def test_agy_pydantic_initial_prompt_uses_body_semantics_and_one_sealer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sentinel = "AGY_DONE_" + "a" * 32
    body_modes: list[bool] = []

    def fake_inject(
        prompt,
        _schema,
        *,
        body_semantics_only=False,
    ):
        body_modes.append(body_semantics_only)
        return f"SCHEMA BODY\n=== USER REQUEST ===\n{prompt}"

    monkeypatch.setattr(wrapper, "inject_schema_to_prompt", fake_inject)

    unsealed = wrapper._compose_effective_prompt("review", object(), {})
    cmd = wrapper._build_cmd(
        unsealed,
        sentinel,
        True,
        "gemini-3.1-pro-high",
        1200,
        pydantic=True,
    )
    sealed = cmd[cmd.index("-p") + 1]

    assert body_modes == [True]
    assert sealed.count("Your complete response must contain exactly two parts:") == 1
    assert sealed.count(f"<<<{sentinel}>>>") == 1
    assert sealed.index("SCHEMA BODY") < sealed.index(
        "Your complete response must contain exactly two parts:"
    )
    assert "Respond with the JSON object only" not in sealed
    assert "valid JSON and nothing else" not in sealed
    assert "no surrounding content" not in sealed

    plain_cmd = wrapper._build_cmd(
        "plain response",
        sentinel,
        False,
        None,
        1200,
        pydantic=False,
    )
    plain_prompt = plain_cmd[plain_cmd.index("-p") + 1]
    assert "End your final answer with the exact marker" in plain_prompt
    assert "Your complete response must contain exactly two parts:" not in plain_prompt


def test_schema_repair_retains_trusted_packet_footer() -> None:
    sentinel = "AGY_DONE_" + "b" * 32
    root = "/private/tmp/review packet/packet"
    digest = "c" * 64
    prompt = wrapper._append_trusted_packet_context("review scope B", root, digest)
    cmd = wrapper._build_cmd(
        prompt,
        sentinel,
        True,
        "Gemini 3.1 Pro (High)",
        1200,
        pydantic=True,
        skip_permissions=True,
    )

    repaired = wrapper._repair_cmd(
        cmd,
        prompt,
        "packet digest mismatch",
        sentinel,
    )
    repaired_prompt = repaired[repaired.index("-p") + 1]

    assert f"Immutable packet root: {root}" in repaired_prompt
    assert f"Expected PACKET_SHA256: {digest}" in repaired_prompt
    assert "packet digest mismatch" in repaired_prompt


def test_agy_schema_retry_rebuilds_unsealed_prompt_and_reseals_once() -> None:
    sentinel = "AGY_DONE_" + "1" * 32
    foreign_marker = "<<<AGY_DONE_" + "2" * 32 + ">>>"
    unsealed = "SCHEMA BODY\n=== USER REQUEST ===\nreview"
    cmd = wrapper._build_cmd(
        unsealed,
        sentinel,
        True,
        "gemini-3.1-pro-high",
        1200,
        pydantic=True,
        skip_permissions=True,
    )

    repaired = wrapper._repair_cmd(
        cmd,
        unsealed,
        f"packet digest mismatch; observed {foreign_marker}",
        sentinel,
    )
    repaired_prompt = repaired[repaired.index("-p") + 1]

    assert repaired_prompt.count("SCHEMA BODY") == 1
    assert repaired_prompt.count("packet digest mismatch") == 1
    assert (
        "<schema_validation_error>\n"
        f"packet digest mismatch; observed {foreign_marker}\n"
        "</schema_validation_error>"
        in repaired_prompt
    )
    assert (
        repaired_prompt.count(
            "Your complete response must contain exactly two parts:"
        )
        == 1
    )
    assert repaired_prompt.count(f"<<<{sentinel}>>>") == 1
    assert repaired_prompt.rfind(f"<<<{sentinel}>>>") > repaired_prompt.rfind(
        foreign_marker
    )
    prompt_index = cmd.index("-p") + 1
    assert repaired[:prompt_index] == cmd[:prompt_index]
    assert repaired[prompt_index + 1 :] == cmd[prompt_index + 1 :]


def test_truncated_done_content_falls_back_to_complete_pty_answer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sentinel = "AGY_DONE_" + "3" * 32
    brain = tmp_path / "brain"
    transcript = (
        brain
        / "conversation"
        / ".system_generated"
        / "logs"
        / "transcript.jsonl"
    )
    pty_calls = 0

    def fake_pty(*_args, **_kwargs):
        nonlocal pty_calls
        pty_calls += 1
        transcript.parent.mkdir(parents=True)
        records = [
            {
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "status": "DONE",
                "content": f"prompt\n<<<{sentinel}>>>",
            },
            {
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "status": "DONE",
                "content": (
                    "short head\n<truncated 200 bytes>\nshort tail\n"
                    f"<<<{sentinel}>>>"
                ),
                "truncated_fields": ["content", "thinking"],
            },
        ]
        transcript.write_text(
            "".join(json.dumps(record) + "\n" for record in records),
            encoding="utf-8",
        )
        return wrapper._pty.PtyResult(
            f"complete PTY answer\n<<<{sentinel}>>>\n".encode(),
            0,
            False,
        )

    monkeypatch.setenv("AGY_BRAIN_DIR", str(brain))
    monkeypatch.setattr(wrapper._pty, "run_via_pty", fake_pty)

    result = wrapper._run_agy_with_retry(
        ["agy", "-p", "sealed"],
        "unsealed",
        30,
        expected_sentinel=sentinel,
    )

    assert result.final_answer == "complete PTY answer"
    assert result.classification == "ok"
    assert result.exit_code == wrapper._common.EXIT_OK
    assert pty_calls == 1


def test_preflight_proves_packet_identity_without_starting_provider(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    packet = tmp_path / "packet"
    packet.mkdir()
    digest = "d" * 64
    monkeypatch.setattr(wrapper, "load_pydantic_class", lambda _spec: _ContextSchema)
    sentinel = tmp_path / "provider-started"
    fake_agy = tmp_path / "agy"
    fake_agy.write_text(
        "#!/bin/sh\nprintf invoked > \"$AGY_PREFLIGHT_SENTINEL\"\n",
        encoding="utf-8",
    )
    fake_agy.chmod(0o755)
    monkeypatch.setenv("TRIAD_AGY_BIN", str(fake_agy))
    monkeypatch.setenv("TRIAD_REQUIRE_PINNED_VENDOR", "1")
    monkeypatch.setenv("AGY_PREFLIGHT_SENTINEL", str(sentinel))
    monkeypatch.setattr(
        wrapper._agy_settings,
        "agy_settings_guard",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("provider/settings path must not start")
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt", "review",
            "--model", "Gemini 3.1 Pro (High)",
            "--sandbox", "read-only",
            "--pydantic", "ledger:Review",
            "--sealed-packet-root", str(packet),
            "--expected-packet-sha256", digest,
            "--preflight-only",
        ],
    )

    assert wrapper.main() == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["provider_started"] is False
    assert receipt["dispatch_phase"] == "preflight"
    assert receipt["skip_permissions"] is None
    assert receipt["sealed_packet_root"] == str(packet.resolve())
    assert receipt["expected_packet_sha256"] == digest
    assert not sentinel.exists()


def test_agy_cleanup_precedes_sealed_preflight(tmp_path: Path, monkeypatch, capsys) -> None:
    order: list[str] = []
    packet = tmp_path / "packet"
    packet.mkdir()

    def cleanup(_cli: str) -> None:
        order.append("cleanup")

    def validation_context(*_args, **_kwargs):
        order.append("preflight")
        return {}

    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", cleanup)
    monkeypatch.setattr(wrapper._common, "build_validation_context", validation_context)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt", "review",
            "--sealed-packet-root", str(packet),
            "--expected-packet-sha256", "a" * 64,
            "--preflight-only",
        ],
    )

    assert wrapper.main() == wrapper._common.EXIT_OK
    assert order == ["cleanup", "preflight"]
    assert json.loads(capsys.readouterr().out)["provider_started"] is False


def test_unlisted_packet_entry_stops_before_agy_provider_boundary(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    packet, digest = _write_real_sealed_packet(tmp_path)
    (packet / "unlisted.txt").write_text("not bound by either manifest\n", encoding="utf-8")
    schema = wrapper._common.load_pydantic_class(
        "triad_formal_review_schema:FormalReview"
    )
    calls = {"binary": 0, "settings": 0, "pty": 0}

    def binary_access(_name: str) -> str:
        calls["binary"] += 1
        return "/usr/bin/agy"

    def settings_access(*_args, **_kwargs):
        calls["settings"] += 1
        raise AssertionError("settings must not be accessed")

    def pty_access(*_args, **_kwargs):
        calls["pty"] += 1
        raise AssertionError("PTY must not be accessed")

    monkeypatch.setattr(wrapper, "load_pydantic_class", lambda _spec: schema)
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(wrapper._common, "require_binary", binary_access)
    monkeypatch.setattr(wrapper._agy_settings, "build_deny_rules", settings_access)
    monkeypatch.setattr(wrapper._agy_settings, "agy_settings_guard", settings_access)
    monkeypatch.setattr(wrapper._pty, "run_via_pty", pty_access)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            "review",
            "--sandbox",
            "read-only",
            "--pydantic",
            "triad_formal_review_schema:FormalReview",
            "--sealed-packet-root",
            str(packet),
            "--expected-packet-sha256",
            digest,
        ],
    )

    assert wrapper.main() == wrapper._common.EXIT_ARG_ERROR
    assert calls == {"binary": 0, "settings": 0, "pty": 0}
    assert "packet tree" in capsys.readouterr().err


@pytest.mark.parametrize(
    "required_context",
    [
        pytest.param("absent", id="absent"),
        pytest.param(frozenset(), id="empty"),
        pytest.param(frozenset({"sealed_packet_root"}), id="partial"),
        pytest.param(
            frozenset({"sealed_packet_root", "expected_packet_sha265"}),
            id="misspelled",
        ),
        pytest.param(
            frozenset(
                {
                    "sealed_packet_root",
                    "expected_packet_sha256",
                    "review_id",
                }
            ),
            id="extra",
        ),
        pytest.param(None, id="malformed"),
    ],
)
def test_sealed_context_requires_exact_schema_contract_before_binary_or_settings(
    required_context, tmp_path: Path, monkeypatch
) -> None:
    packet = tmp_path / "packet"
    packet.mkdir()
    schema = type("Schema", (), {})
    if required_context != "absent":
        schema.required_validation_context = required_context

    monkeypatch.setattr(wrapper, "load_pydantic_class", lambda _spec: schema)
    monkeypatch.setattr(
        wrapper._common,
        "require_binary",
        lambda _name: (_ for _ in ()).throw(
            AssertionError("binary access must not start")
        ),
    )
    monkeypatch.setattr(
        wrapper._agy_settings,
        "build_deny_rules",
        lambda _mode: (_ for _ in ()).throw(
            AssertionError("settings access must not start")
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            "review",
            "--sandbox",
            "read-only",
            "--pydantic",
            "ledger:Review",
            "--sealed-packet-root",
            str(packet),
            "--expected-packet-sha256",
            "a" * 64,
            "--preflight-only",
        ],
    )

    assert wrapper.main() == wrapper._common.EXIT_ARG_ERROR


@pytest.mark.parametrize(
    "preflight_only", [True, False], ids=["preflight", "dispatch"]
)
@pytest.mark.parametrize("root_kind", ["wrong-leaf", "ancestor-alias"])
def test_noncanonical_packet_root_stops_before_binary_settings_or_pty(
    root_kind: str,
    preflight_only: bool,
    tmp_path: Path,
    monkeypatch,
) -> None:
    real_review = tmp_path / "review-r4"
    packet = real_review / "packet"
    packet.mkdir(parents=True)
    if root_kind == "wrong-leaf":
        target = real_review / "evidence"
        target.mkdir()
    else:
        alias = tmp_path / "review-alias"
        alias.symlink_to(real_review, target_is_directory=True)
        target = alias / "packet"

    calls = {"binary": 0, "settings": 0, "pty": 0}

    def fake_binary(_name: str) -> str:
        calls["binary"] += 1
        return "/usr/bin/agy"

    def fake_deny_rules(_mode):
        calls["settings"] += 1
        return []

    @contextmanager
    def fake_settings_guard(*_args, **_kwargs):
        calls["settings"] += 1
        yield

    def fake_pty(*_args, **_kwargs):
        calls["pty"] += 1
        return wrapper._pty.PtyResult(b"", 0, False)

    monkeypatch.setattr(
        wrapper, "load_pydantic_class", lambda _spec: _ContextSchema
    )
    monkeypatch.setattr(
        wrapper,
        "inject_schema_to_prompt",
        lambda prompt, _cls, *, body_semantics_only=False: prompt,
    )
    monkeypatch.setattr(wrapper, "validate_response", lambda *_a, **_k: (True, {}))
    monkeypatch.setattr(wrapper, "_agy_needs_skip_permissions", lambda _path: False)
    monkeypatch.setattr(wrapper._common, "require_binary", fake_binary)
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(wrapper._common, "snapshot_agy_transcripts", lambda: {})
    monkeypatch.setattr(
        wrapper._common,
        "extract_agy_answer_from_transcript",
        lambda *_a, **_k: "{}",
    )
    monkeypatch.setattr(
        wrapper._common,
        "persist_result_artifacts",
        lambda *_a, **_k: None,
    )
    monkeypatch.setattr(wrapper._agy_settings, "build_deny_rules", fake_deny_rules)
    monkeypatch.setattr(wrapper._agy_settings, "agy_settings_guard", fake_settings_guard)
    monkeypatch.setattr(wrapper._pty, "run_via_pty", fake_pty)

    argv = [
        "antigravity_wrapper.py",
        "--prompt",
        "review",
        "--sandbox",
        "read-only",
        "--pydantic",
        "ledger:Review",
        "--sealed-packet-root",
        str(target),
        "--expected-packet-sha256",
        "a" * 64,
    ]
    if preflight_only:
        argv.append("--preflight-only")
    monkeypatch.setattr(sys, "argv", argv)

    assert wrapper.main() == wrapper._common.EXIT_ARG_ERROR
    assert calls == {"binary": 0, "settings": 0, "pty": 0}


def test_sealed_schema_failure_persists_one_provider_response_without_retry(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    packet = tmp_path / "packet"
    packet.mkdir()
    root = str(packet.resolve())
    digest = "e" * 64
    sentinel = "AGY_DONE_" + "f" * 32
    answers = iter(['{"packet": "wrong"}'])
    validations = iter([(False, "packet digest mismatch")])
    pty_calls: list[list[str]] = []
    driver_result: dict[str, object] = {}
    persisted: dict[str, object] = {}

    def fake_pty(cmd, **_kwargs):
        pty_calls.append(list(cmd))
        return wrapper._pty.PtyResult(output_bytes=b"", rc=0, killed=False)

    real_driver = wrapper._run_agy_with_retry

    def capture_driver(*args, **kwargs):
        result = real_driver(*args, **kwargs)
        driver_result["result"] = result
        return result

    def capture_persistence(
        cli, wrapper_cmd, vendor_cmd, prompt, result, *, debug
    ):
        persisted.update(
            cli=cli,
            wrapper_cmd=list(wrapper_cmd),
            vendor_cmd=list(vendor_cmd),
            prompt=prompt,
            result=result,
            debug=debug,
        )
        return None

    monkeypatch.setattr(wrapper, "load_pydantic_class", lambda _spec: _ContextSchema)
    monkeypatch.setattr(
        wrapper,
        "inject_schema_to_prompt",
        lambda prompt, _cls, *, body_semantics_only=False: prompt,
    )
    monkeypatch.setattr(
        wrapper,
        "validate_response",
        lambda *_args, **_kwargs: next(validations),
    )
    monkeypatch.setattr(wrapper, "_make_sentinel", lambda: sentinel)
    monkeypatch.setattr(wrapper, "_agy_needs_skip_permissions", lambda _path: False)
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _name: "/usr/bin/agy")
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(wrapper._common, "snapshot_agy_transcripts", lambda: {})
    monkeypatch.setattr(
        wrapper._common,
        "extract_agy_answer_from_transcript",
        lambda *_args, **_kwargs: next(answers),
    )
    monkeypatch.setattr(wrapper._pty, "run_via_pty", fake_pty)
    monkeypatch.setattr(
        wrapper._agy_settings,
        "agy_settings_guard",
        lambda *_args, **_kwargs: nullcontext(),
    )
    monkeypatch.setattr(wrapper, "_run_agy_with_retry", capture_driver)
    monkeypatch.setattr(
        wrapper._common, "persist_result_artifacts", capture_persistence
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            "review",
            "--model",
            "Gemini 3.1 Pro (High)",
            "--sandbox",
            "read-only",
            "--repair-mode",
            "--pydantic",
            "ledger:Review",
            "--sealed-packet-root",
            root,
            "--expected-packet-sha256",
            digest,
        ],
    )

    assert wrapper.main() == wrapper._common.EXIT_SCHEMA_FAIL
    assert len(pty_calls) == 1

    agy_result = driver_result["result"]
    assert agy_result.final_argv == pty_calls[0]
    assert agy_result.schema_repair_attempt == 0
    assert agy_result.validation_error == "packet digest mismatch"
    assert agy_result.validated is None
    assert agy_result.dispatch_phase == "post-dispatch-cleanup"

    run_result = persisted["result"]
    assert persisted["vendor_cmd"] == pty_calls[0]
    assert run_result.mode == "repair"
    assert run_result.schema_repair_attempt == 0
    assert run_result.validation_error == "packet digest mismatch"
    assert run_result.validated is None
    assert run_result.dispatch_phase == "post-dispatch-cleanup"
    assert capsys.readouterr().out == '{"packet": "wrong"}\n'


def test_schema_retry_transport_error_persists_attempt_state(
    monkeypatch,
) -> None:
    sentinel = "AGY_DONE_" + "1" * 32
    pty_calls: list[list[str]] = []
    persisted: dict[str, object] = {}

    def fake_pty(cmd, **_kwargs):
        pty_calls.append(list(cmd))
        if len(pty_calls) == 2:
            raise OSError("transport lost")
        return wrapper._pty.PtyResult(output_bytes=b"", rc=0, killed=False)

    def capture_persistence(
        cli, wrapper_cmd, vendor_cmd, prompt, result, *, debug
    ):
        persisted.update(
            cli=cli,
            wrapper_cmd=list(wrapper_cmd),
            vendor_cmd=list(vendor_cmd),
            prompt=prompt,
            result=result,
            debug=debug,
        )
        return None

    monkeypatch.setattr(wrapper, "load_pydantic_class", lambda _spec: object)
    monkeypatch.setattr(
        wrapper,
        "inject_schema_to_prompt",
        lambda prompt, _cls, *, body_semantics_only=False: f"SCHEMA BODY\n{prompt}",
    )
    monkeypatch.setattr(
        wrapper,
        "validate_response",
        lambda *_args, **_kwargs: (False, "packet digest mismatch"),
    )
    monkeypatch.setattr(wrapper, "_make_sentinel", lambda: sentinel)
    monkeypatch.setattr(wrapper, "_agy_needs_skip_permissions", lambda _path: False)
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _name: "/usr/bin/agy")
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(wrapper._common, "snapshot_agy_transcripts", lambda: {})
    monkeypatch.setattr(
        wrapper._common,
        "extract_agy_answer_from_transcript",
        lambda *_args, **_kwargs: '{"packet": "wrong"}',
    )
    monkeypatch.setattr(wrapper._pty, "run_via_pty", fake_pty)
    monkeypatch.setattr(
        wrapper._agy_settings,
        "agy_settings_guard",
        lambda *_args, **_kwargs: nullcontext(),
    )
    monkeypatch.setattr(
        wrapper._common, "persist_result_artifacts", capture_persistence
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "ledger:Review",
        ],
    )

    assert wrapper.main() == wrapper._common.EXIT_TERMINAL
    assert len(pty_calls) == 2
    repaired_argv = pty_calls[1]
    repaired_prompt = repaired_argv[repaired_argv.index("-p") + 1]
    assert "SCHEMA BODY" in repaired_prompt
    assert "packet digest mismatch" in repaired_prompt
    assert persisted["vendor_cmd"] == repaired_argv

    run_result = persisted["result"]
    assert run_result.classification == "config-conflict"
    assert run_result.mode == "schema_repair"
    assert run_result.schema_repair_attempt == 1
    assert run_result.validation_error == "packet digest mismatch"
    assert run_result.dispatch_phase == "dispatch-uncertain"


@pytest.mark.parametrize(
    ("guard_case", "expected_phase", "expected_exit", "expected_driver_calls"),
    [
        ("entry", "pre-dispatch-settings", wrapper._common.EXIT_TERMINAL, 0),
        ("body", "dispatch-uncertain", wrapper._common.EXIT_TERMINAL, 1),
        ("normal", "post-dispatch-cleanup", wrapper._common.EXIT_OK, 1),
        ("exit", "post-dispatch-result", wrapper._common.EXIT_TERMINAL, 1),
    ],
)
def test_settings_guard_phase_is_preserved_in_custody_and_summary(
    guard_case,
    expected_phase,
    expected_exit,
    expected_driver_calls,
    monkeypatch,
    capsys,
) -> None:
    driver_calls = 0
    persisted: dict[str, object] = {}

    @contextmanager
    def fake_guard(*_args, **_kwargs):
        if guard_case == "entry":
            raise TimeoutError("guard entry failed")
        try:
            yield
        finally:
            if guard_case == "exit":
                raise OSError("guard exit failed")

    def fake_driver(*_args, **_kwargs):
        nonlocal driver_calls
        driver_calls += 1
        if guard_case == "body":
            raise OSError("provider state unknown")
        return wrapper.AgyResult(
            final_answer='{"decision": "PASS"}',
            classification="ok",
            exit_code=wrapper._common.EXIT_OK,
            vendor_exit_code=0,
            final_argv=["/usr/bin/agy", "-p", "sealed"],
            schema_repair_attempt=0,
            validation_error=None,
            dispatch_phase="post-dispatch-result",
            validated={"decision": "PASS"},
        )

    def capture_persistence(
        cli, wrapper_cmd, vendor_cmd, prompt, result, *, debug
    ):
        persisted.update(
            cli=cli,
            wrapper_cmd=list(wrapper_cmd),
            vendor_cmd=list(vendor_cmd),
            prompt=prompt,
            result=result,
            debug=debug,
        )
        return None

    monkeypatch.setattr(wrapper._common, "require_binary", lambda _name: "/usr/bin/agy")
    monkeypatch.setattr(wrapper, "_agy_needs_skip_permissions", lambda _path: False)
    monkeypatch.setattr(wrapper, "_make_sentinel", lambda: "AGY_DONE_" + "7" * 32)
    monkeypatch.setattr(wrapper._agy_settings, "agy_settings_guard", fake_guard)
    monkeypatch.setattr(wrapper, "_run_agy_with_retry", fake_driver)
    monkeypatch.setattr(wrapper._common, "persist_result_artifacts", capture_persistence)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            "review",
            "--sandbox",
            "read-only",
        ],
    )

    assert wrapper.main() == expected_exit
    assert driver_calls == expected_driver_calls
    result = persisted["result"]
    assert result.dispatch_phase == expected_phase
    if guard_case != "normal":
        assert result.classification == "config-conflict"
    if guard_case in {"entry", "body"}:
        assert result.vendor_exit_code == -1
    captured = capsys.readouterr()
    assert f"phase={expected_phase}" in captured.err
    if guard_case == "exit":
        assert result.validated is None
        assert captured.out == ""


def test_settings_restore_failure_suppresses_validated_provider_answer(
    monkeypatch,
    capsys,
) -> None:
    persisted: dict[str, object] = {}

    @contextmanager
    def restore_failure(*_args, **_kwargs):
        try:
            yield
        finally:
            raise OSError("settings restore failed")

    def validated_driver(*_args, **_kwargs):
        return wrapper.AgyResult(
            final_answer='{"decision": "PASS"}',
            classification="ok",
            exit_code=wrapper._common.EXIT_OK,
            vendor_exit_code=0,
            final_argv=["/usr/bin/agy", "-p", "sealed"],
            schema_repair_attempt=0,
            validation_error=None,
            dispatch_phase="post-dispatch-result",
            validated={"decision": "PASS"},
        )

    def capture_persistence(
        cli, wrapper_cmd, vendor_cmd, prompt, result, *, debug
    ):
        persisted["result"] = result
        return None

    monkeypatch.setattr(wrapper._common, "require_binary", lambda _name: "/usr/bin/agy")
    monkeypatch.setattr(wrapper, "_agy_needs_skip_permissions", lambda _path: False)
    monkeypatch.setattr(wrapper, "_make_sentinel", lambda: "AGY_DONE_" + "8" * 32)
    monkeypatch.setattr(wrapper._agy_settings, "agy_settings_guard", restore_failure)
    monkeypatch.setattr(wrapper, "_run_agy_with_retry", validated_driver)
    monkeypatch.setattr(
        wrapper._common, "persist_result_artifacts", capture_persistence
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            "review",
            "--sandbox",
            "read-only",
        ],
    )

    assert wrapper.main() == wrapper._common.EXIT_TERMINAL
    captured = capsys.readouterr()
    assert captured.out == ""
    result = persisted["result"]
    assert result.classification == "config-conflict"
    assert result.dispatch_phase == "post-dispatch-result"
    assert result.final_answer == ""
    assert result.validated is None
    assert "settings restore failed" in result.extraction_error
    assert "completed vendor result suppressed" in result.extraction_error


def test_audit_and_run_log_preserve_phase_and_exact_validated_object(
    tmp_path: Path, monkeypatch
) -> None:
    validated = {
        "decision": "NEEDS_CHANGES",
        "findings": [{"id": "F-1", "severity": "high"}],
    }
    result = wrapper._common.RunResult(
        exit_code=wrapper._common.EXIT_SCHEMA_FAIL,
        stdout="raw provider transcript",
        stderr="",
        elapsed_s=1.25,
        classification="schema-fail",
        validated=validated,
        dispatch_phase="post-dispatch-cleanup",
    )
    monkeypatch.setattr(wrapper._common, "_LOG_DIR", tmp_path)
    monkeypatch.setattr(wrapper._common, "_audit_redact_enabled", lambda: False)

    wrapper._common.audit("antigravity", ["agy"], "review", result)
    audit_record = json.loads(
        (tmp_path / "antigravity" / "audit.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[-1]
    )
    run_log = wrapper._common.emit_run_log(
        "antigravity", ["wrapper"], ["agy"], "review", result
    )
    assert run_log is not None
    run_record = json.loads(run_log.read_text(encoding="utf-8"))

    assert audit_record["dispatch_phase"] == "post-dispatch-cleanup"
    assert audit_record["validated"] == validated
    assert run_record["dispatch_phase"] == "post-dispatch-cleanup"
    assert run_record["validated"] == validated
