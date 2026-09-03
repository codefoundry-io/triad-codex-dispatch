from __future__ import annotations

import io
import hashlib
import json
import os
import signal
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
from verdict_schema import LegVerdict  # noqa: E402


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


def _canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
        + b"\n"
    )


def _google_selector_fixture(
    tmp_path: Path,
    *,
    review_id: str = "review-r1",
    route: str = "gemini",
    content_digest: str = "a" * 64,
    family: str = "google",
) -> tuple[Path, str, Path]:
    executable = (tmp_path / f"selected-{route}").resolve()
    executable.write_text("#!/bin/sh\nexit 91\n", encoding="utf-8")
    executable.chmod(0o755)
    wrapper = (
        BIN / ("antigravity_wrapper.py" if route == "agy" else "gemini_wrapper.py")
    ).resolve()
    record = {
        "authentication_class": (
            "personal-google" if route == "agy" else "gemini-enterprise"
        ),
        "executable": str(executable),
        "provider_started": False,
        "review_id": review_id,
        "route": route,
        "wrapper": str(wrapper),
    }
    receipt_path = (tmp_path / f"{route}-selector.json").resolve()
    receipt_payload = _canonical_json_bytes(record)
    receipt_path.write_bytes(receipt_payload)
    preflight_common = {
        "executable": str(executable),
        "google_selector_receipt_sha256": hashlib.sha256(receipt_payload).hexdigest(),
        "provider_started": False,
        "review_id": review_id,
        "route": route,
    }
    if route == "agy":
        preflight_record = {
            **preflight_common,
            "agy_version": "1.1.20",
            "effort": "high",
            "model": "gemini-3.1-pro-high",
            "route_args": [
                "--model",
                "gemini-3.1-pro-high",
                "--effort",
                "high",
            ],
        }
    else:
        preflight_record = {
            **preflight_common,
            "effective_approval_mode": "unexposed",
            "model": "auto",
            "policy": str(
                (ROOT / "bin" / "policies" / "gemini-formal-readonly.toml").resolve()
            ),
            "read_only_enforcement": "packaged-mode-independent-policy",
            "requested_approval_mode": "plan",
        }
    metadata = {
        "content_digest": content_digest,
        "family": family,
        "google_authentication_class": record["authentication_class"],
        "google_executable": record["executable"],
        "google_provider_started": False,
        "google_preflight_effort": "high" if route == "agy" else None,
        "google_preflight_model": preflight_record["model"],
        "google_preflight_receipt_sha256": hashlib.sha256(
            _canonical_json_bytes(preflight_record)
        ).hexdigest(),
        "google_route": route,
        "google_selector_receipt_sha256": hashlib.sha256(receipt_payload).hexdigest(),
        "google_wrapper": record["wrapper"],
        "review_id": review_id,
    }
    prompt = "Review metadata: " + _canonical_json_bytes(metadata).decode(
        "ascii"
    ).rstrip("\n")
    return receipt_path, prompt, executable


def _google_preflight_fixture(
    tmp_path: Path,
    selector_receipt: Path,
    executable: Path,
    *,
    review_id: str = "review-r1",
) -> Path:
    receipt = {
        "effective_approval_mode": "unexposed",
        "executable": str(executable),
        "google_selector_receipt_sha256": hashlib.sha256(
            selector_receipt.read_bytes()
        ).hexdigest(),
        "model": "auto",
        "policy": str(
            (ROOT / "bin" / "policies" / "gemini-formal-readonly.toml").resolve()
        ),
        "provider_started": False,
        "read_only_enforcement": "packaged-mode-independent-policy",
        "requested_approval_mode": "plan",
        "review_id": review_id,
        "route": "gemini",
    }
    path = (tmp_path / "gemini-preflight.json").resolve()
    path.write_bytes(_canonical_json_bytes(receipt))
    return path


def _formal_gemini_help() -> str:
    return (
        "  --model  Model  [string]\n"
        "  --approval-mode  Set the approval mode  [string] "
        '[choices: "default", "auto_edit", "yolo", "plan"]\n'
        "  --policy  Additional policy files or directories to load  [array]\n"
    )


def test_run_once_interrupt_terminates_provider_process_group(monkeypatch) -> None:
    interruption = KeyboardInterrupt("cancel invalid round")
    signals: list[tuple[int, int]] = []

    class InterruptingProcess:
        pid = 4242
        stdin = None
        stdout = io.StringIO("")
        stderr = io.StringIO("")
        returncode = None

        def __init__(self) -> None:
            self.wait_calls: list[int] = []

        def wait(self, timeout: int) -> int:
            self.wait_calls.append(timeout)
            if len(self.wait_calls) == 1:
                raise interruption
            self.returncode = -signal.SIGTERM
            return self.returncode

    process = InterruptingProcess()
    monkeypatch.setattr(subprocess, "Popen", lambda *_a, **_k: process)
    monkeypatch.setattr(os, "getpgid", lambda pid: pid)
    monkeypatch.setattr(os, "killpg", lambda pgid, sig: signals.append((pgid, sig)))

    with pytest.raises(KeyboardInterrupt) as caught:
        _common._run_once("claude", ["claude", "-p", "review"], None, 60)

    assert caught.value is interruption
    assert signals == [(process.pid, signal.SIGTERM)]
    assert process.wait_calls == [60, 5]


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


def test_claude_route_forwards_model_effort_and_native_json(
    monkeypatch, capsys
) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude"
    )
    monkeypatch.setattr(
        claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )

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
    monkeypatch.setattr(
        claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude"
    )
    monkeypatch.setattr(
        claude_wrapper, "load_pydantic_class", lambda _spec: _StructuredAnswer
    )
    monkeypatch.setattr(
        claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", pruned.append)
    monkeypatch.setattr(
        claude_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: (_ for _ in ()).throw(
            AssertionError("generic retry path used")
        ),
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
            arg == forbidden or arg.startswith(f"{forbidden}=") for arg in calls[0]
        )
    assert "--json-schema" in calls[0]
    assert pruned == ["claude"]


def test_claude_formal_leg_binds_native_schema_and_local_admission(
    monkeypatch, capsys
) -> None:
    calls: list[list[str]] = []
    payload = {
        "review_id": "review-r1",
        "family": "claude",
        "content_digest": "a" * 64,
        "verdict": "SAFE",
        "criteria_checked": ["correctness"],
        "findings": [],
        "affected_surfaces_inspected": ["src/parser.py"],
        "open_questions": [],
    }
    monkeypatch.setattr(
        claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude"
    )
    monkeypatch.setattr(claude_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, _cwd, _timeout, *, classify_and_log):
        calls.append(cmd)
        assert _timeout == 1800
        schema = json.loads(cmd[cmd.index("--json-schema") + 1])
        properties = schema["properties"]
        assert properties["review_id"]["const"] == "review-r1"
        assert properties["family"]["const"] == "claude"
        assert properties["content_digest"]["const"] == "a" * 64
        return _common.RunResult(
            exit_code=0,
            stdout=json.dumps(
                {
                    "is_error": False,
                    "result": json.dumps(payload),
                    "structured_output": payload,
                }
            ),
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
            "--timeout",
            "1800",
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "claude",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert claude_wrapper.main() == 0
    assert json.loads(capsys.readouterr().out) == payload
    assert len(calls) == 1
    for option in ("--model", "--effort", "--permission-mode", "--json-schema"):
        assert calls[0].count(option) == 1
    assert calls[0][calls[0].index("--model") + 1] == "opus"
    assert calls[0][calls[0].index("--effort") + 1] == "xhigh"
    assert calls[0][calls[0].index("--permission-mode") + 1] == "plan"
    assert "--fallback-model" not in calls[0]


def test_claude_formal_leg_rejects_locally_valid_binding_mismatch(
    monkeypatch, capsys
) -> None:
    payload = {
        "review_id": "review-r1",
        "family": "claude",
        "content_digest": "b" * 64,
        "verdict": "SAFE",
        "criteria_checked": ["correctness"],
        "findings": [],
        "affected_surfaces_inspected": ["src/parser.py"],
        "open_questions": [],
    }
    monkeypatch.setattr(
        claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude"
    )
    monkeypatch.setattr(claude_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(
        _common,
        "_run_once",
        lambda *_a, **_k: _common.RunResult(
            exit_code=0,
            stdout=json.dumps(
                {
                    "is_error": False,
                    "result": json.dumps(payload),
                    "structured_output": payload,
                }
            ),
            stderr="",
            elapsed_s=0.2,
            vendor_exit_code=0,
        ),
    )
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
            "--timeout",
            "1800",
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "claude",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert claude_wrapper.main() == _common.EXIT_SCHEMA_FAIL
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    "route_args",
    (
        ("--effort", "xhigh", "--timeout", "1800"),
        ("--model", "sonnet", "--effort", "xhigh", "--timeout", "1800"),
        ("--model", "opus", "--timeout", "1800"),
        ("--model", "opus", "--effort", "high", "--timeout", "1800"),
        ("--model", "opus", "--effort", "xhigh"),
        ("--model", "opus", "--effort", "xhigh", "--timeout", "1799"),
        (
            "--model",
            "opus",
            "--effort",
            "xhigh",
            "--timeout",
            "1800",
            "--fallback-model",
            "sonnet",
        ),
        (
            "--model",
            "opus",
            "--effort",
            "xhigh",
            "--timeout",
            "1800",
            "--fallback-model",
            "",
        ),
    ),
    ids=(
        "missing-model",
        "wrong-model",
        "missing-effort",
        "wrong-effort",
        "default-timeout",
        "wrong-timeout",
        "fallback-model",
        "empty-fallback-model",
    ),
)
def test_claude_formal_leg_rejects_unpinned_route_before_provider_resolution(
    monkeypatch, capsys, route_args
) -> None:
    monkeypatch.setattr(claude_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        claude_wrapper,
        "require_binary",
        lambda _name: pytest.fail("provider resolved"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "claude",
            "--expected-content-digest",
            "a" * 64,
            *route_args,
        ],
    )

    assert claude_wrapper.main() == _common.EXIT_ARG_ERROR
    assert (
        "formal Claude route requires --model opus --effort xhigh --timeout 1800 "
        "and forbids --fallback-model" in capsys.readouterr().err
    )


@pytest.mark.parametrize(
    ("binding_args", "expected_error"),
    (
        (
            (),
            "formal verdict schema requires all formal verdict bindings",
        ),
        (
            ("--expected-review-id", "review-r1"),
            "formal verdict schema requires all formal verdict bindings",
        ),
        (
            (
                "--expected-review-id",
                "review-r1",
                "--expected-family",
                "claude",
                "--expected-content-digest",
                "a" * 64,
                "--pydantic",
                f"{__name__}:_StructuredAnswer",
            ),
            "formal verdict bindings require --pydantic verdict_schema:LegVerdict",
        ),
        (
            (
                "--expected-review-id",
                "invalid/review",
                "--expected-family",
                "claude",
                "--expected-content-digest",
                "a" * 64,
            ),
            "expected review ID has invalid syntax",
        ),
        (
            (
                "--expected-review-id",
                "review-r1",
                "--expected-family",
                "claude",
                "--expected-content-digest",
                "A" * 64,
            ),
            "expected content digest must be 64 lowercase hexadecimal characters",
        ),
    ),
)
def test_claude_formal_leg_rejects_invalid_bindings_before_provider_resolution(
    monkeypatch, capsys, binding_args, expected_error
) -> None:
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
            "verdict_schema:LegVerdict",
            *binding_args,
        ],
    )

    assert claude_wrapper.main() == _common.EXIT_ARG_ERROR
    assert expected_error in capsys.readouterr().err


def test_claude_wrapper_rejects_removed_formal_read_tools_flag(
    monkeypatch, capsys
) -> None:
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
    monkeypatch.setattr(
        claude_wrapper, "require_binary", lambda _name: "/opt/bin/claude"
    )
    monkeypatch.setattr(
        claude_wrapper, "load_pydantic_class", lambda _spec: _StructuredAnswer
    )
    monkeypatch.setattr(
        claude_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
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
            "claude_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "fake:Answer",
        ],
    )

    assert claude_wrapper.main() == _common.EXIT_SCHEMA_FAIL
    assert capsys.readouterr().out == ""
    assert calls == 1


def test_claude_rejects_repair_mode_on_structured_route(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        claude_wrapper, "load_pydantic_class", lambda _spec: _StructuredAnswer
    )
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


def test_gemini_route_keeps_native_json_without_review_protocol(
    monkeypatch, capsys
) -> None:
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        gemini_wrapper, "require_binary", lambda _name: "/opt/bin/gemini"
    )
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )

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


def test_gemini_formal_leg_uses_plan_policy_scrubbed_oauth_and_bound_result(
    monkeypatch, capsys, tmp_path
) -> None:
    captured: dict[str, object] = {}
    payload = {
        "review_id": "review-r1",
        "family": "google",
        "content_digest": "a" * 64,
        "verdict": "SAFE",
        "criteria_checked": ["correctness"],
        "findings": [],
        "affected_surfaces_inspected": ["src/parser.py"],
        "open_questions": [],
    }
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.1-pro")
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )

    def fake_driver(_cli, builder, prompt, **kwargs):
        captured["cmd"] = builder(prompt)
        captured["kwargs"] = kwargs
        return _common.RunResult(
            exit_code=0,
            stdout="",
            stderr="",
            elapsed_s=0.1,
            final_answer=json.dumps(payload),
            validated=payload,
            vendor_exit_code=0,
        )

    monkeypatch.setattr(gemini_wrapper, "run_cli_with_retry", fake_driver)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == 0
    assert json.loads(capsys.readouterr().out) == payload
    cmd = captured["cmd"]
    assert cmd[0] == str(selected)
    assert cmd[cmd.index("--approval-mode") + 1] == "plan"
    policy = Path(cmd[cmd.index("--policy") + 1])
    assert policy == ROOT / "bin" / "policies" / "gemini-formal-readonly.toml"
    assert policy.is_file()
    assert cmd.count("-m") == 1
    assert cmd[cmd.index("-m") + 1] == "auto"
    kwargs = captured["kwargs"]
    assert kwargs["single_provider_call"] is True
    assert set(kwargs["remove_env"]) == {
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_GENAI_USE_VERTEXAI",
        "GOOGLE_GEMINI_BASE_URL",
        "GOOGLE_VERTEX_BASE_URL",
        "CLOUD_SHELL",
        "GEMINI_CLI_USE_COMPUTE_ADC",
        "GEMINI_MODEL",
    }


def test_gemini_formal_leg_persists_literal_unexposed_runtime_identity(
    monkeypatch, capsys, tmp_path
) -> None:
    payload = {
        "review_id": "review-r1",
        "family": "google",
        "content_digest": "a" * 64,
        "verdict": "SAFE",
        "criteria_checked": ["correctness"],
        "findings": [],
        "affected_surfaces_inspected": ["src/parser.py"],
        "open_questions": [],
    }
    provider_calls = 0
    persisted: list[_common.RunResult] = []
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        gemini_wrapper,
        "persist_result_artifacts",
        lambda _cli, _argv, _cmd, _prompt, result, **_kwargs: persisted.append(result),
    )

    def fake_driver(_cli, _builder, _prompt, **_kwargs):
        nonlocal provider_calls
        provider_calls += 1
        return _common.RunResult(
            exit_code=0,
            stdout="",
            stderr="",
            elapsed_s=0.1,
            final_answer=json.dumps(payload),
            validated=payload,
            vendor_exit_code=0,
        )

    monkeypatch.setattr(gemini_wrapper, "run_cli_with_retry", fake_driver)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == 0
    assert json.loads(capsys.readouterr().out) == payload
    assert provider_calls == 1
    assert len(persisted) == 1
    assert persisted[0].runtime_identity == "unexposed"


def test_gemini_formal_leg_rejects_binding_mismatch_without_stdout(
    monkeypatch, capsys, tmp_path
) -> None:
    payload = {
        "review_id": "review-r1",
        "family": "google",
        "content_digest": "b" * 64,
        "verdict": "SAFE",
        "criteria_checked": ["correctness"],
        "findings": [],
        "affected_surfaces_inspected": ["src/parser.py"],
        "open_questions": [],
    }
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(
        gemini_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: _common.RunResult(
            exit_code=0,
            stdout="",
            stderr="",
            elapsed_s=0.1,
            final_answer=json.dumps(payload),
            validated=payload,
            vendor_exit_code=0,
        ),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema.LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_SCHEMA_FAIL
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize(
    "binding_args",
    (
        (),
        ("--expected-review-id", "review-r1"),
        (
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
            "--pydantic",
            f"{__name__}:_StructuredAnswer",
        ),
        (
            "--expected-review-id",
            "invalid/review",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ),
        (
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "A" * 64,
        ),
        (
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
            "--timeout",
            "0",
        ),
        (
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
            "--model",
            "gemini-3.1-pro",
        ),
    ),
)
def test_gemini_formal_leg_rejects_invalid_bindings_before_provider_resolution(
    monkeypatch, binding_args
) -> None:
    monkeypatch.setattr(
        gemini_wrapper,
        "require_binary",
        lambda _name: (_ for _ in ()).throw(AssertionError("provider resolved")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--pydantic",
            "verdict_schema:LegVerdict",
            *binding_args,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR


def test_gemini_formal_preflight_is_provider_free_and_scrubs_competing_auth(
    monkeypatch, capsys, tmp_path
) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []
    competing_auth = (
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "GOOGLE_GENAI_USE_VERTEXAI",
        "GOOGLE_GEMINI_BASE_URL",
        "GOOGLE_VERTEX_BASE_URL",
        "CLOUD_SHELL",
        "GEMINI_CLI_USE_COMPUTE_ADC",
        "GEMINI_MODEL",
    )
    for name in competing_auth:
        monkeypatch.setenv(name, "must-not-reach-child")
    selector_receipt, _prompt, selected = _google_selector_fixture(tmp_path)
    monkeypatch.setattr(
        gemini_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("provider started")),
    )

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=_formal_gemini_help(),
            stderr="",
        )

    monkeypatch.setattr(gemini_wrapper.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert gemini_wrapper.main() == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["provider_started"] is False
    assert receipt["route"] == "gemini"
    assert receipt["executable"] == str(selected)
    assert receipt["review_id"] == "review-r1"
    assert (
        receipt["google_selector_receipt_sha256"]
        == hashlib.sha256(selector_receipt.read_bytes()).hexdigest()
    )
    assert receipt["requested_approval_mode"] == "plan"
    assert receipt["effective_approval_mode"] == "unexposed"
    assert receipt["model"] == "auto"
    assert receipt["read_only_enforcement"] == ("packaged-mode-independent-policy")
    assert "approval_mode" not in receipt
    assert Path(receipt["policy"]) == (
        ROOT / "bin" / "policies" / "gemini-formal-readonly.toml"
    )
    assert len(calls) == 1
    cmd, kwargs = calls[0]
    assert cmd == [str(selected), "--help"]
    child_env = kwargs["env"]
    for name in competing_auth:
        assert name not in child_env


def test_gemini_formal_preflight_rejects_unbound_help_tokens(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, _prompt, _selected = _google_selector_fixture(tmp_path)

    def fake_run(cmd, **_kwargs):
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=(
                "--approval-mode supports only default\n"
                "plan is mentioned in unrelated prose\n"
                "--policy was removed and accepts no path\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(gemini_wrapper.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "did not prove Plan Mode, policy, and Auto model support" in (
        capsys.readouterr().err
    )


def test_gemini_formal_preflight_requires_explicit_auto_model_surface(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, _prompt, _selected = _google_selector_fixture(tmp_path)

    def fake_run(cmd, **_kwargs):
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=(
                "  --approval-mode  Set the approval mode  [string] "
                '[choices: "default", "auto_edit", "yolo", "plan"]\n'
                "  --policy  Additional policy files or directories to load  [array]\n"
            ),
            stderr="",
        )

    monkeypatch.setattr(gemini_wrapper.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "did not prove Plan Mode, policy, and Auto model support" in (
        capsys.readouterr().err
    )


def test_gemini_formal_preflight_honors_required_receipt_pin_over_path(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, _prompt, selected = _google_selector_fixture(tmp_path)
    shadow = tmp_path / "shadow" / "gemini"
    for executable in (shadow,):
        executable.parent.mkdir()
        executable.write_text("#!/bin/sh\nexit 91\n", encoding="utf-8")
        executable.chmod(0o755)
    calls: list[list[str]] = []

    def fake_run(cmd, **_kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(
            cmd,
            0,
            stdout=_formal_gemini_help(),
            stderr="",
        )

    monkeypatch.setenv("PATH", str(shadow.parent))
    monkeypatch.setenv("TRIAD_REQUIRE_PINNED_VENDOR", "1")
    monkeypatch.setenv("TRIAD_GEMINI_BIN", str(shadow))
    monkeypatch.setattr(gemini_wrapper.subprocess, "run", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert gemini_wrapper.main() == 0
    assert json.loads(capsys.readouterr().out)["executable"] == str(selected)
    assert calls == [[str(selected), "--help"]]


def test_gemini_formal_rejects_wrong_route_receipt_before_preflight(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, _prompt, _selected = _google_selector_fixture(
        tmp_path, route="agy"
    )
    monkeypatch.setattr(
        gemini_wrapper.subprocess,
        "run",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("preflight started")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "selector receipt route mismatch" in capsys.readouterr().err


def test_gemini_formal_preflight_rejects_foreign_review_before_help_probe(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, _prompt, _selected = _google_selector_fixture(
        tmp_path, review_id="foreign-r1"
    )
    monkeypatch.setattr(
        gemini_wrapper.subprocess,
        "run",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("help probed")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            "review",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "selector receipt review ID mismatch" in capsys.readouterr().err


def test_gemini_formal_rejects_preflight_selector_mismatch_before_provider(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    record = json.loads(preflight_receipt.read_text(encoding="ascii"))
    record["google_selector_receipt_sha256"] = "0" * 64
    preflight_receipt.write_bytes(_canonical_json_bytes(record))
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        gemini_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("provider started")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "Google preflight receipt selector mismatch" in capsys.readouterr().err


def test_gemini_formal_rejects_prompt_receipt_mismatch_before_provider(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    mismatched_prompt = prompt.replace(str(selected), f"{selected}-other", 1)
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        gemini_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("provider started")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            mismatched_prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "formal prompt selector binding mismatch" in capsys.readouterr().err


def test_gemini_formal_rejects_non_google_prompt_before_provider(
    monkeypatch, tmp_path, capsys
) -> None:
    selector_receipt, prompt, selected = _google_selector_fixture(
        tmp_path, family="codex"
    )
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(gemini_wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(
        gemini_wrapper,
        "run_cli_with_retry",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("provider started")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gemini_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert "formal prompt selector binding mismatch" in capsys.readouterr().err


def test_gemini_formal_policy_rejects_an_additional_allow_rule(tmp_path) -> None:
    policy = tmp_path / "gemini-formal-readonly.toml"
    policy.write_text(
        gemini_wrapper._formal_policy_path().read_text(encoding="utf-8")
        + "\n[[rule]]\n"
        + 'toolName = "run_shell_command"\n'
        + 'decision = "allow"\n'
        + "priority = 999\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="exact fail-closed rule set"):
        gemini_wrapper._validate_formal_policy(policy)


def test_gemini_formal_policy_rejects_mode_scoped_rules(tmp_path) -> None:
    policy = tmp_path / "gemini-formal-readonly.toml"
    policy.write_text(
        gemini_wrapper._formal_policy_path()
        .read_text(encoding="utf-8")
        .replace(
            "priority = 999",
            'priority = 999\nmodes = ["plan"]',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="exact fail-closed rule set"):
        gemini_wrapper._validate_formal_policy(policy)


def test_gemini_formal_verdict_route_does_not_make_schema_repair_call(
    monkeypatch, capsys, tmp_path
) -> None:
    calls: list[list[str]] = []
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, cwd, timeout, *, stdin_text=None, remove_env=()):
        calls.append(cmd)
        assert cwd is None
        assert timeout == 600
        assert stdin_text is None
        assert "GEMINI_API_KEY" in remove_env
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
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_SCHEMA_FAIL
    assert capsys.readouterr().out == ""
    assert len(calls) == 1


def test_gemini_formal_verdict_route_does_not_make_capacity_retry_call(
    monkeypatch, capsys, tmp_path
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setenv("TRIAD_SERVER_CAP_NO_BACKOFF", "1")
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, cwd, timeout, *, stdin_text=None, remove_env=()):
        calls.append(cmd)
        assert cwd is None
        assert timeout == 600
        assert stdin_text is None
        assert "GEMINI_API_KEY" in remove_env
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
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_RATE_GIVE_UP
    assert capsys.readouterr().out == ""
    assert len(calls) == 1


def test_gemini_dotted_packaged_verdict_route_does_not_make_capacity_retry_call(
    monkeypatch, capsys, tmp_path
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setenv("TRIAD_SERVER_CAP_NO_BACKOFF", "1")
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _google_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)

    def fake_once(_cli, cmd, cwd, timeout, *, stdin_text=None, remove_env=()):
        calls.append(cmd)
        assert cwd is None
        assert timeout == 600
        assert stdin_text is None
        assert "GEMINI_API_KEY" in remove_env
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
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--pydantic",
            "verdict_schema.LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
        ],
    )

    assert gemini_wrapper.main() == _common.EXIT_RATE_GIVE_UP
    assert capsys.readouterr().out == ""
    assert len(calls) == 1


def test_gemini_custom_schema_keeps_existing_schema_repair_call(
    monkeypatch, capsys
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(
        gemini_wrapper, "require_binary", lambda _name: "/opt/bin/gemini"
    )
    monkeypatch.setattr(
        gemini_wrapper, "load_pydantic_class", lambda _spec: _StructuredAnswer
    )
    monkeypatch.setattr(
        gemini_wrapper, "persist_result_artifacts", lambda *_a, **_k: None
    )
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
