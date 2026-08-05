from __future__ import annotations

import sys
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
sys.path.insert(0, str(BIN))

import _common  # noqa: E402
import claude_wrapper  # noqa: E402
import gemini_wrapper  # noqa: E402


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
    for retired in (
        "--sandbox",
        "--sealed-packet-root",
        "--expected-packet-sha256",
        "--dangerously-skip-permissions",
    ):
        monkeypatch.setattr(sys, "argv", [module.__file__, "--prompt", "x", retired, "x"])
        with pytest.raises(SystemExit) as caught:
            module.main()
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
