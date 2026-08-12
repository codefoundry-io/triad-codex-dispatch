from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import BaseModel, ConfigDict


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
sys.path.insert(0, str(BIN))

import _common  # noqa: E402
import antigravity_wrapper as wrapper  # noqa: E402
from verdict_schema import LegVerdict  # noqa: E402


class _Answer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


def _run_result(stdout: str, *, rc: int = 0, stderr: str = "") -> _common.RunResult:
    return _common.RunResult(
        exit_code=_common.EXIT_OK if rc == 0 else _common.EXIT_CLI_FAIL,
        stdout=stdout,
        stderr=stderr,
        elapsed_s=0.25,
        classification="unclassified",
        vendor_exit_code=rc,
    )


def _stream(result: dict) -> str:
    return "\n".join(
        [
            json.dumps({"event": "init", "init": {"model": "gemini-3.1-pro-high"}}),
            json.dumps({"event": "step_update", "step_update": {"text_delta": "ignored"}}),
            json.dumps({"event": "result", "result": result}),
        ]
    )


def test_agy_110_route_uses_native_stream_schema_and_effort() -> None:
    cmd = wrapper._build_cmd(
        "/opt/bin/agy",
        "review the directory",
        model="gemini-3.1-pro-high",
        effort="high",
        timeout=90,
        json_schema='{"type":"object"}',
    )

    assert cmd == [
        "/opt/bin/agy",
        "--dangerously-skip-permissions",
        "-p",
        "review the directory",
        "--output-format",
        "stream-json",
        "--print-timeout",
        "80s",
        "--json-schema",
        '{"type":"object"}',
        "--model",
        "gemini-3.1-pro-high",
        "--effort",
        "high",
    ]
    assert "--sandbox" not in cmd
    assert cmd.count("--dangerously-skip-permissions") == 1


def test_schema_argv_is_redacted_from_logs() -> None:
    redacted = _common._redact_prompt_args(
        ["agy", "-p", "private prompt", "--json-schema", '{"type":"object"}']
    )

    assert redacted == [
        "agy",
        "-p",
        "<redacted:14 chars>",
        "--json-schema",
        "<redacted:17 chars>",
    ]


def test_version_floor_is_110() -> None:
    assert wrapper.AGY_VERSION_FLOOR == (1, 1, 10)
    assert wrapper._parse_agy_version("1.1.10\n") == (1, 1, 10)
    assert wrapper._parse_agy_version("agy 2.0.1") == (2, 0, 1)
    assert wrapper._parse_agy_version("unknown") is None


def test_parser_admits_only_the_last_terminal_result() -> None:
    first = json.dumps({"event": "result", "result": {"status": "ERROR"}})
    second = json.dumps(
        {"event": "result", "result": {"status": "SUCCESS", "response": "final"}}
    )
    events, result = wrapper.parse_agy_stream(
        "not-json\n" + first + "\n{truncated\n" + second + "\n"
    )

    assert len(events) == 2
    assert result == {"status": "SUCCESS", "response": "final"}


def test_structured_result_uses_native_payload_then_local_validation() -> None:
    raw = _run_result(
        _stream(
            {
                "status": "SUCCESS",
                "response": "prose is not the custody object",
                "structured_output": {"ok": True},
            }
        )
    )

    admitted = wrapper._interpret_run(raw, _Answer, "gemini-3.1-pro-high")

    assert admitted.exit_code == _common.EXIT_OK
    assert admitted.classification == "ok"
    assert admitted.validated == {"ok": True}
    assert admitted.final_answer == '{"ok": true}'
    assert admitted.runtime_identity == "gemini-3.1-pro-high"


def test_bound_formal_result_rejects_wrong_family_after_local_validation() -> None:
    payload = {
        "review_id": "review-r1",
        "family": "codex",
        "content_digest": "a" * 64,
        "verdict": "SAFE",
        "criteria_checked": ["correctness"],
        "findings": [],
        "affected_surfaces_inspected": ["src/parser.py"],
        "open_questions": [],
    }
    raw = _run_result(
        _stream(
            {
                "status": "SUCCESS",
                "response": json.dumps(payload),
                "structured_output": payload,
            }
        )
    )

    admitted = wrapper._interpret_run(
        raw,
        LegVerdict,
        "gemini-3.1-pro-high",
        expected_review_id="review-r1",
        expected_family="google",
        expected_content_digest="a" * 64,
    )

    assert admitted.exit_code == _common.EXIT_SCHEMA_FAIL
    assert admitted.classification == "schema-fail"
    assert admitted.final_answer == ""
    assert "family mismatch" in (admitted.validation_error or "")


def test_exposed_model_conflict_invalidates_successful_result() -> None:
    raw = _run_result(
        _stream(
            {
                "status": "SUCCESS",
                "response": '{"ok":true}',
                "structured_output": {"ok": True},
            }
        )
    )

    admitted = wrapper._interpret_run(raw, _Answer, "another-model")

    assert admitted.exit_code == _common.EXIT_TERMINAL
    assert admitted.classification == "route-mismatch"
    assert admitted.final_answer == ""
    assert admitted.runtime_identity == "gemini-3.1-pro-high"


def test_exposed_model_conflict_invalidates_unstructured_result() -> None:
    raw = _run_result(
        _stream(
            {
                "status": "SUCCESS",
                "response": "plausible answer from the wrong route",
            }
        )
    )

    admitted = wrapper._interpret_run(raw, None, "another-model")

    assert admitted.exit_code == _common.EXIT_TERMINAL
    assert admitted.classification == "route-mismatch"
    assert admitted.final_answer == ""
    assert admitted.runtime_identity == "gemini-3.1-pro-high"


def test_any_exposed_model_conflict_invalidates_successful_result() -> None:
    raw = _run_result(
        "\n".join(
            [
                json.dumps({"event": "init", "init": {"model": "unexpected-model"}}),
                json.dumps(
                    {"event": "init", "init": {"model": "gemini-3.1-pro-high"}}
                ),
                json.dumps(
                    {
                        "event": "result",
                        "result": {
                            "status": "SUCCESS",
                            "response": '{"ok":true}',
                            "structured_output": {"ok": True},
                        },
                    }
                ),
            ]
        )
    )

    admitted = wrapper._interpret_run(raw, _Answer, "gemini-3.1-pro-high")

    assert admitted.exit_code == _common.EXIT_TERMINAL
    assert admitted.classification == "route-mismatch"
    assert admitted.final_answer == ""
    assert admitted.runtime_identity == "unexpected-model"


def test_structured_result_requires_native_terminal_payload() -> None:
    raw = _run_result(_stream({"status": "SUCCESS", "response": '{"ok":true}'}))

    admitted = wrapper._interpret_run(raw, _Answer)

    assert admitted.exit_code == _common.EXIT_SCHEMA_FAIL
    assert admitted.classification == "schema-fail"
    assert admitted.final_answer == ""
    assert "structured_output" in (admitted.validation_error or "")


def test_non_success_terminal_result_is_never_admitted() -> None:
    raw = _run_result(
        _stream({"status": "ERROR", "response": "looks useful", "structured_output": {"ok": True}})
    )

    admitted = wrapper._interpret_run(raw, _Answer)

    assert admitted.exit_code == _common.EXIT_TERMINAL
    assert admitted.classification == "vendor-error"
    assert admitted.final_answer == ""


def test_step_text_without_terminal_result_is_extraction_error() -> None:
    raw = _run_result(json.dumps({"event": "step_update", "step_update": {"text_delta": "partial"}}))

    admitted = wrapper._interpret_run(raw, None)

    assert admitted.exit_code == _common.EXIT_CLI_FAIL
    assert admitted.classification == "extraction-error"
    assert admitted.final_answer == ""


def test_timeout_records_unexposed_runtime_identity() -> None:
    raw = _run_result("")
    raw.exit_code = _common.EXIT_TIMEOUT

    admitted = wrapper._interpret_run(raw, None, "gemini-3.1-pro-high")

    assert admitted.exit_code == _common.EXIT_TIMEOUT
    assert admitted.classification == "timeout"
    assert admitted.runtime_identity == "unexposed"


def test_timeout_records_exposed_conflicting_runtime_identity() -> None:
    raw = _run_result(
        json.dumps(
            {
                "event": "init",
                "init": {"model": "unexpected-model"},
            }
        )
    )
    raw.exit_code = _common.EXIT_TIMEOUT

    admitted = wrapper._interpret_run(raw, None, "gemini-3.1-pro-high")

    assert admitted.exit_code == _common.EXIT_TIMEOUT
    assert admitted.classification == "timeout"
    assert admitted.final_answer == ""
    assert admitted.runtime_identity == "unexpected-model"


def test_main_forwards_native_route_and_prints_validated_terminal_json(
    monkeypatch, capsys
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _name: "/opt/bin/agy")
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _bin: (1, 1, 10))
    monkeypatch.setattr(wrapper._common, "persist_result_artifacts", lambda *_a, **_k: None)
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)

    def fake_run(_cli, cmd, _cwd, _timeout, *, classify_and_log):
        calls.append(cmd)
        assert classify_and_log is False
        return _run_result(
            _stream(
                {
                    "status": "SUCCESS",
                    "response": '{"ok":true}\n',
                    "structured_output": {"ok": True},
                }
            )
        )

    monkeypatch.setattr(wrapper._common, "_run_once", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            "review",
            "--model",
            "gemini-3.1-pro-high",
            "--effort",
            "high",
            "--pydantic",
            f"{__name__}:_Answer",
        ],
    )

    assert wrapper.main() == 0
    assert json.loads(capsys.readouterr().out) == {"ok": True}
    assert "--output-format" in calls[0]
    assert "--json-schema" in calls[0]
    assert calls[0][calls[0].index("--effort") + 1] == "high"


def test_main_binds_formal_leg_in_native_schema(monkeypatch, capsys) -> None:
    calls: list[list[str]] = []
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
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _name: "/opt/bin/agy")
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _bin: (1, 1, 12))
    monkeypatch.setattr(wrapper._common, "persist_result_artifacts", lambda *_a, **_k: None)
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)

    def fake_run(_cli, cmd, _cwd, _timeout, *, classify_and_log):
        calls.append(cmd)
        schema = json.loads(cmd[cmd.index("--json-schema") + 1])
        properties = schema["properties"]
        assert properties["review_id"]["const"] == "review-r1"
        assert properties["family"]["const"] == "google"
        assert properties["content_digest"]["const"] == "a" * 64
        return _run_result(
            _stream(
                {
                    "status": "SUCCESS",
                    "response": json.dumps(payload),
                    "structured_output": payload,
                }
            )
        )

    monkeypatch.setattr(wrapper._common, "_run_once", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            "review",
            "--model",
            "gemini-3.1-pro-high",
            "--effort",
            "high",
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

    assert wrapper.main() == 0
    assert json.loads(capsys.readouterr().out) == payload
    assert len(calls) == 1


def test_preflight_proves_version_and_route_without_provider_submission(
    monkeypatch, capsys
) -> None:
    pruned: list[str] = []
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _name: "/opt/bin/agy")
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _bin: (1, 1, 10))
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", pruned.append)
    monkeypatch.setattr(
        wrapper._common,
        "_run_once",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("provider started")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            "route proof",
            "--model",
            "gemini-3.1-pro-high",
            "--effort",
            "high",
            "--preflight-only",
        ],
    )

    assert wrapper.main() == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt == {
        "agy_version": "1.1.10",
        "effort": "high",
        "model": "gemini-3.1-pro-high",
        "provider_started": False,
        "route_args": ["--model", "gemini-3.1-pro-high", "--effort", "high"],
    }
    assert pruned == ["antigravity"]
