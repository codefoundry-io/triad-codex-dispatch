from __future__ import annotations

import sys
import subprocess
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
sys.path.insert(0, str(BIN))

import _common  # noqa: E402
import antigravity_wrapper  # noqa: E402
import claude_wrapper  # noqa: E402
import gemini_wrapper  # noqa: E402


class _StructuredAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


def _ok() -> _common.RunResult:
    return _common.RunResult(
        exit_code=0,
        stdout="",
        stderr="",
        elapsed_s=0.1,
        final_answer="ok",
        vendor_exit_code=0,
    )


def test_packaged_leg_verdict_loads_under_hardened_wrapper(monkeypatch) -> None:
    monkeypatch.setenv("TRIAD_WRAPPER_HARDENED", "1")
    monkeypatch.delenv("TRIAD_ALLOW_PYDANTIC_IMPORT", raising=False)

    schema = _common.load_pydantic_class("verdict_schema:LegVerdict")

    assert schema.__name__ == "LegVerdict"
    assert "batch_id" not in schema.model_fields


def test_packaged_leg_verdict_loads_in_a_clean_python_process() -> None:
    program = (
        "import sys; "
        f"sys.path.insert(0, {str(BIN)!r}); "
        "import _common; "
        "cls = _common.load_pydantic_class('verdict_schema:LegVerdict'); "
        "print(cls.model_json_schema()['title'])"
    )
    result = subprocess.run(
        [sys.executable, "-c", program],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "LegVerdict"


def test_hardened_wrapper_requires_opt_in_for_arbitrary_schema(monkeypatch) -> None:
    monkeypatch.setenv("TRIAD_WRAPPER_HARDENED", "1")
    monkeypatch.delenv("TRIAD_ALLOW_PYDANTIC_IMPORT", raising=False)

    with pytest.raises(PermissionError, match="trusted schema modules"):
        _common.load_pydantic_class("tests.fake:Schema")


@pytest.mark.parametrize(
    "module",
    [claude_wrapper, gemini_wrapper],
)
def test_provider_wrappers_reject_retired_review_and_permission_flags(
    module, monkeypatch
) -> None:
    modules = (antigravity_wrapper, module) if module is claude_wrapper else (module,)
    for current_module in modules:
        for retired in (
            "--sandbox",
            "--sealed-packet-root",
            "--expected-packet-sha256",
            "--dangerously-skip-permissions",
        ):
            monkeypatch.setattr(
                sys,
                "argv",
                [current_module.__file__, "--prompt", "x", retired, "x"],
            )
            with pytest.raises(SystemExit) as caught:
                current_module.main()
            assert caught.value.code == 2


def test_claude_route_forwards_model_effort_and_native_json(monkeypatch, capsys) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude")
    monkeypatch.setattr(claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None)

    def fake_driver(_cli, builder, prompt, **kwargs):
        captured["cmd"] = builder(prompt)
        captured["kwargs"] = kwargs
        return _ok()

    monkeypatch.setattr(claude_wrapper, "run_cli_with_retry", fake_driver)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--model",
            "opus",
            "--effort",
            "xhigh",
        ],
    )

    assert claude_wrapper.main() == 0
    assert capsys.readouterr().out == "ok\n"
    assert captured["cmd"] == [
        "/opt/bin/claude",
        "-p",
        "review",
        "--output-format",
        "json",
        "--model",
        "opus",
        "--effort",
        "xhigh",
    ]


def test_claude_structured_route_uses_native_schema_once(monkeypatch, capsys) -> None:
    calls: list[list[str]] = []
    pruned: list[str] = []
    monkeypatch.setattr(claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude")
    monkeypatch.setattr(claude_wrapper, "load_pydantic_class", lambda _spec: _StructuredAnswer)
    monkeypatch.setattr(claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None)
    monkeypatch.setattr(_common, "prune_stale_run_logs", pruned.append)
    monkeypatch.setattr(
        claude_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("generic retry path used")),
    )

    def fake_once(_cli, cmd, _cwd, _timeout, *, classify_and_log):
        calls.append(cmd)
        assert classify_and_log is False
        return _common.RunResult(
            exit_code=0,
            stdout='{"is_error":false,"result":"{\\"ok\\":true}","structured_output":{"ok":true}}',
            stderr="",
            elapsed_s=0.2,
            vendor_exit_code=0,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--model",
            "opus",
            "--effort",
            "xhigh",
            "--pydantic",
            "fake:Answer",
        ],
    )

    assert claude_wrapper.main() == 0
    assert capsys.readouterr().out == '{"ok": true}\n'
    assert len(calls) == 1
    assert "--tools" not in calls[0]
    for forbidden in (
        "--safe-mode",
        "--strict-mcp-config",
        "--mcp-config",
        "--allowedTools",
        "--disallowedTools",
    ):
        assert not any(
            arg == forbidden or arg.startswith(f"{forbidden}=")
            for arg in calls[0]
        )
    assert "--json-schema" in calls[0]
    assert pruned == ["claude"]


def test_claude_wrapper_rejects_removed_formal_read_tools_flag(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        claude_wrapper,
        "require_binary",
        lambda _name: (_ for _ in ()).throw(AssertionError("provider resolved")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "fake:Answer",
            "--formal-read-tools",
        ],
    )

    with pytest.raises(SystemExit) as exc:
        claude_wrapper.main()

    assert exc.value.code == 2
    assert "unrecognized arguments: --formal-read-tools" in capsys.readouterr().err


def test_claude_structured_route_rejects_result_text_fallback(
    monkeypatch, capsys
) -> None:
    calls = 0
    monkeypatch.setattr(claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude")
    monkeypatch.setattr(claude_wrapper, "load_pydantic_class", lambda _spec: _StructuredAnswer)
    monkeypatch.setattr(claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None)
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, _cmd, _cwd, _timeout, *, classify_and_log):
        nonlocal calls
        calls += 1
        assert classify_and_log is False
        return _common.RunResult(
            exit_code=0,
            stdout='{"is_error":false,"result":"{\\"ok\\":true}"}',
            stderr="",
            elapsed_s=0.2,
            vendor_exit_code=0,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py", "--prompt", "review", "--pydantic", "fake:Answer",
        ],
    )

    assert claude_wrapper.main() == _common.EXIT_SCHEMA_FAIL
    assert capsys.readouterr().out == ""
    assert calls == 1


def test_claude_rejects_repair_mode_on_structured_route(monkeypatch, capsys) -> None:
    monkeypatch.setattr(claude_wrapper, "load_pydantic_class", lambda _spec: _StructuredAnswer)
    monkeypatch.setattr(
        claude_wrapper,
        "require_binary",
        lambda _name: (_ for _ in ()).throw(AssertionError("provider resolved")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "fake:Answer",
            "--repair-mode",
        ],
    )

    assert claude_wrapper.main() == _common.EXIT_ARG_ERROR
    assert capsys.readouterr().out == ""


def test_gemini_route_keeps_native_json_without_review_protocol(monkeypatch, capsys) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(gemini_wrapper, "require_binary", lambda _name: "/opt/bin/gemini")
    monkeypatch.setattr(gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None)

    def fake_driver(_cli, builder, prompt, **kwargs):
        captured["cmd"] = builder(prompt)
        return _ok()

    monkeypatch.setattr(gemini_wrapper, "run_cli_with_retry", fake_driver)
    monkeypatch.setattr(
        sys,
        "argv",
        ["gemini_wrapper.py", "--prompt", "review", "--model", "gemini-enterprise"],
    )

    assert gemini_wrapper.main() == 0
    assert capsys.readouterr().out == "ok\n"
    assert captured["cmd"] == [
        "/opt/bin/gemini",
        "-p",
        "review",
        "--output-format",
        "json",
        "-m",
        "gemini-enterprise",
    ]


def test_gemini_formal_verdict_route_does_not_make_schema_repair_call(
    monkeypatch, capsys
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(gemini_wrapper, "require_binary", lambda _name: "/opt/bin/gemini")
    monkeypatch.setattr(gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None)
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, cwd, timeout, *, stdin_text=None):
        calls.append(cmd)
        assert cwd is None
        assert timeout == 600
        assert stdin_text is None
        return _common.RunResult(
            exit_code=0,
            stdout='{"response":"{}"}',
            stderr="",
            elapsed_s=0.1,
            classification="ok",
            vendor_exit_code=0,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "verdict_schema:LegVerdict",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_SCHEMA_FAIL
    assert capsys.readouterr().out == ""
    assert len(calls) == 1


def test_gemini_formal_verdict_route_does_not_make_capacity_retry_call(
    monkeypatch, capsys
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setenv("TRIAD_SERVER_CAP_NO_BACKOFF", "1")
    monkeypatch.setattr(gemini_wrapper, "require_binary", lambda _name: "/opt/bin/gemini")
    monkeypatch.setattr(gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None)
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, cwd, timeout, *, stdin_text=None):
        calls.append(cmd)
        assert cwd is None
        assert timeout == 600
        assert stdin_text is None
        return _common.RunResult(
            exit_code=_common.EXIT_CLI_FAIL,
            stdout="",
            stderr="capacity exhausted",
            elapsed_s=0.1,
            classification="server-capacity",
            vendor_exit_code=1,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "verdict_schema:LegVerdict",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_RATE_GIVE_UP
    assert capsys.readouterr().out == ""
    assert len(calls) == 1


def test_gemini_dotted_packaged_verdict_route_does_not_make_capacity_retry_call(
    monkeypatch, capsys
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setenv("TRIAD_SERVER_CAP_NO_BACKOFF", "1")
    monkeypatch.setattr(gemini_wrapper, "require_binary", lambda _name: "/opt/bin/gemini")
    monkeypatch.setattr(gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None)
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, cwd, timeout, *, stdin_text=None):
        calls.append(cmd)
        assert cwd is None
        assert timeout == 600
        assert stdin_text is None
        return _common.RunResult(
            exit_code=_common.EXIT_CLI_FAIL,
            stdout="",
            stderr="capacity exhausted",
            elapsed_s=0.1,
            classification="server-capacity",
            vendor_exit_code=1,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "verdict_schema.LegVerdict",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_RATE_GIVE_UP
    assert capsys.readouterr().out == ""
    assert len(calls) == 1


def test_gemini_custom_schema_keeps_existing_schema_repair_call(
    monkeypatch, capsys
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(gemini_wrapper, "require_binary", lambda _name: "/opt/bin/gemini")
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: _StructuredAnswer)
    monkeypatch.setattr(gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None)
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, cwd, timeout, *, stdin_text=None):
        calls.append(cmd)
        assert cwd is None
        assert timeout == 600
        assert stdin_text is None
        return _common.RunResult(
            exit_code=0,
            stdout='{"response":"{}"}',
            stderr="",
            elapsed_s=0.1,
            classification="ok",
            vendor_exit_code=0,
        )

    monkeypatch.setattr(_common, "_run_once", fake_once)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "example:StructuredAnswer",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_SCHEMA_FAIL
    assert capsys.readouterr().out == ""
    assert len(calls) == 2
