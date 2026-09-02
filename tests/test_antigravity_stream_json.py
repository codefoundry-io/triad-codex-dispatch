from __future__ import annotations

import contextlib
import hashlib
import json
import sys
from pathlib import Path

import pytest
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
            json.dumps(
                {"event": "step_update", "step_update": {"text_delta": "ignored"}}
            ),
            json.dumps({"event": "result", "result": result}),
        ]
    )


def _formal_payload() -> dict:
    return {
        "review_id": "review-r1",
        "family": "google",
        "content_digest": "a" * 64,
        "verdict": "SAFE",
        "criteria_checked": ["correctness"],
        "findings": [],
        "affected_surfaces_inspected": ["source/product/file.py"],
        "open_questions": [],
    }


def _google_selector_fixture(
    tmp_path: Path, *, route: str = "agy", family: str = "google"
) -> tuple[Path, str, Path]:
    executable = (tmp_path / f"selected-{route}").resolve()
    executable.write_text("#!/bin/sh\nexit 91\n", encoding="utf-8")
    executable.chmod(0o755)
    record = {
        "authentication_class": (
            "personal-google" if route == "agy" else "gemini-enterprise"
        ),
        "executable": str(executable),
        "provider_started": False,
        "review_id": "review-r1",
        "route": route,
        "wrapper": str(
            (
                BIN
                / ("antigravity_wrapper.py" if route == "agy" else "gemini_wrapper.py")
            ).resolve()
        ),
    }
    payload = (
        json.dumps(
            record,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
        + b"\n"
    )
    receipt_path = (tmp_path / f"{route}-selector.json").resolve()
    receipt_path.write_bytes(payload)
    preflight_common = {
        "executable": str(executable),
        "google_selector_receipt_sha256": hashlib.sha256(payload).hexdigest(),
        "provider_started": False,
        "review_id": "review-r1",
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
            "policy": str((BIN / "policies" / "gemini-formal-readonly.toml").resolve()),
            "read_only_enforcement": "packaged-mode-independent-policy",
            "requested_approval_mode": "plan",
        }
    metadata = {
        "content_digest": "a" * 64,
        "family": family,
        "google_authentication_class": record["authentication_class"],
        "google_executable": str(executable),
        "google_provider_started": False,
        "google_preflight_effort": "high" if route == "agy" else None,
        "google_preflight_model": preflight_record["model"],
        "google_preflight_receipt_sha256": hashlib.sha256(
            json.dumps(
                preflight_record,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("ascii")
            + b"\n"
        ).hexdigest(),
        "google_route": route,
        "google_selector_receipt_sha256": hashlib.sha256(payload).hexdigest(),
        "google_wrapper": record["wrapper"],
        "review_id": "review-r1",
    }
    prompt = "Review metadata: " + json.dumps(
        metadata,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return receipt_path, prompt, executable


def _agy_preflight_fixture(
    tmp_path: Path,
    selector_receipt: Path,
    executable: Path,
    *,
    review_id: str = "review-r1",
) -> Path:
    receipt = {
        "agy_version": "1.1.20",
        "effort": "high",
        "executable": str(executable),
        "google_selector_receipt_sha256": hashlib.sha256(
            selector_receipt.read_bytes()
        ).hexdigest(),
        "model": "gemini-3.1-pro-high",
        "provider_started": False,
        "review_id": review_id,
        "route": "agy",
        "route_args": ["--model", "gemini-3.1-pro-high", "--effort", "high"],
    }
    path = (tmp_path / "agy-preflight.json").resolve()
    path.write_bytes(
        json.dumps(
            receipt,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
        + b"\n"
    )
    return path


def _plan_stream(*tool_calls: tuple[str, dict]) -> str:
    events = [
        {"event": "init", "init": {"model": "gemini-3.1-pro-high"}},
    ]
    for step_index, (tool_name, parameters) in enumerate(tool_calls, start=1):
        events.append(
            {
                "event": "step_update",
                "step_update": {
                    "step_index": step_index,
                    "state": "ACTIVE",
                    "step_type": "tool",
                    "tool_name": tool_name,
                    "tool_info": {"name": tool_name, "parameters": parameters},
                },
            }
        )
    events.append(
        {
            "event": "result",
            "result": {
                "status": "SUCCESS",
                "response": json.dumps(_formal_payload()),
                "structured_output": _formal_payload(),
            },
        }
    )
    return "\n".join(json.dumps(event) for event in events)


def _interpret_plan_stream(*tool_calls: tuple[str, dict]) -> _common.RunResult:
    return wrapper._interpret_run(
        _run_result(_plan_stream(*tool_calls)),
        LegVerdict,
        "gemini-3.1-pro-high",
        expected_review_id="review-r1",
        expected_family="google",
        expected_content_digest="a" * 64,
        plan_mode=True,
    )


def _interpret_plan_updates(*updates: dict) -> _common.RunResult:
    events = [{"event": "init", "init": {"model": "gemini-3.1-pro-high"}}]
    events.extend({"event": "step_update", "step_update": update} for update in updates)
    events.append(
        {
            "event": "result",
            "result": {
                "status": "SUCCESS",
                "response": json.dumps(_formal_payload()),
                "structured_output": _formal_payload(),
            },
        }
    )
    return wrapper._interpret_run(
        _run_result("\n".join(json.dumps(event) for event in events)),
        LegVerdict,
        "gemini-3.1-pro-high",
        expected_review_id="review-r1",
        expected_family="google",
        expected_content_digest="a" * 64,
        plan_mode=True,
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


def test_formal_route_uses_plan_mode_with_sandbox() -> None:
    cmd = wrapper._build_cmd(
        "/opt/bin/agy",
        "review the directory",
        model="gemini-3.1-pro-high",
        effort="high",
        timeout=90,
        json_schema='{"type":"object"}',
        sandbox=True,
        skip_permissions=True,
    )

    assert cmd[0:3] == ["/opt/bin/agy", "--dangerously-skip-permissions", "-p"]
    assert "--sandbox" in cmd
    assert cmd[cmd.index("--mode") : cmd.index("--mode") + 2] == ["--mode", "plan"]
    assert "--project" not in cmd


def test_operator_can_opt_out_of_claude_headless_adaptation(monkeypatch) -> None:
    monkeypatch.setenv("AGY_NO_HEADLESS_AUTOAPPROVE", "1")

    assert wrapper._agy_needs_skip_permissions((1, 1, 12)) is False


def test_formal_child_environment_removes_separately_billed_route_selectors() -> None:
    parent = {
        "PATH": "/usr/bin",
        "GEMINI_API_KEY": "secret",
        "GOOGLE_API_KEY": "secret",
        "GOOGLE_APPLICATION_CREDENTIALS": "/credentials.json",
        "GOOGLE_GENAI_USE_VERTEXAI": "true",
        "GOOGLE_GENAI_USE_ENTERPRISE": "true",
        "GOOGLE_CLOUD_PROJECT": "billing-project",
    }

    child = _common.scrubbed_child_env(parent, remove=wrapper.FORMAL_AGY_ENV_REMOVE)

    assert child == {"PATH": "/usr/bin"}
    assert parent["GEMINI_API_KEY"] == "secret"


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


def test_version_floor_requires_headless_static_review_support() -> None:
    assert wrapper.AGY_VERSION_FLOOR == (1, 1, 20)
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


def test_plan_mode_locally_validates_native_structured_output() -> None:
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
        plan_mode=True,
    )

    assert admitted.exit_code == _common.EXIT_OK
    assert admitted.validated == payload
    assert admitted.final_answer == json.dumps(payload)


def test_plan_mode_admits_direct_source_view_without_prior_grep() -> None:
    admitted = _interpret_plan_stream(
        ("view_file", {"AbsolutePath": "/review/shared/source/product/file.py"})
    )

    assert admitted.exit_code == _common.EXIT_OK
    assert admitted.classification == "ok"


@pytest.mark.parametrize(
    "path",
    (
        "/review/shared/TASK.md",
        "/review/shared/EVIDENCE.md",
        "/review/shared/REVIEW.diff",
        "/review/shared/SOURCE_SHA256SUMS",
    ),
)
def test_plan_mode_admits_one_direct_view_of_leader_packet_control(path: str) -> None:
    admitted = _interpret_plan_stream(("view_file", {"AbsolutePath": path}))

    assert admitted.exit_code == _common.EXIT_OK
    assert admitted.classification == "ok"


@pytest.mark.parametrize(
    "step_update",
    (
        {
            "step_index": 1,
            "step_type": "tool",
            "tool_name": "view_file",
            "tool_info": {
                "parameters": {
                    "AbsolutePath": "/review/shared/TASK.md",
                    "TelemetryRevision": 2,
                },
                "vendor_metadata": {"schema_revision": 2},
            },
        },
        {
            "step_index": "opaque-v2",
            "step_type": "tool",
            "tool_name": "run_command",
            "tool_info": {
                "parameters": {"CommandLine": "git status --short"},
                "error": {"type": "permission", "message": "denied permission"},
            },
            "vendor_metadata": {"schema_revision": 2},
        },
    ),
)
def test_plan_mode_terminal_verdict_admission_is_independent_of_tool_telemetry_schema(
    step_update: dict,
) -> None:
    admitted = _interpret_plan_updates(step_update)

    assert admitted.exit_code == _common.EXIT_OK
    assert admitted.classification == "ok"


def test_plan_mode_admits_conflicting_duplicate_tool_event_representation() -> None:
    first_update = {
        "step_index": 1,
        "step_type": "tool",
        "tool_name": "view_file",
        "tool_info": {
            "parameters": {"AbsolutePath": "/review/shared/TASK.md"},
        },
    }
    conflicting_update = {
        "step_index": 1,
        "step_type": "tool",
        "tool_name": "run_command",
        "tool_info": {
            "parameters": {"CommandLine": "git status --short"},
            "error": {"type": "permission", "message": "denied permission"},
        },
    }

    admitted = _interpret_plan_updates(first_update, conflicting_update)

    assert admitted.exit_code == _common.EXIT_OK
    assert admitted.classification == "ok"


@pytest.mark.parametrize(
    "line_range",
    (
        {"StartLine": 1},
        {"EndLine": 200},
        {"StartLine": 201, "EndLine": 400},
    ),
)
def test_plan_mode_admits_documented_view_line_range(line_range: dict) -> None:
    path = "/review/shared/source/product/file.py"
    admitted = _interpret_plan_stream(
        ("view_file", {"AbsolutePath": path, **line_range}),
    )

    assert admitted.exit_code == _common.EXIT_OK
    assert admitted.classification == "ok"


def test_plan_mode_admits_repeated_read_only_view_for_one_path() -> None:
    path = "/review/shared/source/product/file.py"
    admitted = _interpret_plan_stream(
        ("view_file", {"AbsolutePath": path}),
        ("view_file", {"AbsolutePath": path}),
    )

    assert admitted.exit_code == _common.EXIT_OK
    assert admitted.classification == "ok"


@pytest.mark.parametrize(
    "search_path",
    (
        "/review/shared/source/product/file.py",
        "/review/shared/source/product",
    ),
)
def test_plan_mode_admits_agy_1_1_17_public_grep_search(search_path: str) -> None:
    admitted = _interpret_plan_stream(
        (
            "grep_search",
            {
                "SearchPath": search_path,
                "Query": "decision",
            },
        ),
    )

    assert admitted.exit_code == _common.EXIT_OK
    assert admitted.classification == "ok"


def test_plan_mode_admits_native_structured_output_independent_of_response() -> None:
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
    raw = _run_result(
        _stream(
            {
                "status": "SUCCESS",
                "response": f"```json\n{json.dumps(payload)}\n```\nextra telemetry",
                "structured_output": payload,
            }
        )
    )

    admitted = wrapper._interpret_run(
        raw,
        LegVerdict,
        expected_review_id="review-r1",
        expected_family="google",
        expected_content_digest="a" * 64,
        plan_mode=True,
    )

    assert admitted.exit_code == _common.EXIT_OK
    assert admitted.validated == payload
    assert admitted.final_answer == json.dumps(payload)


def test_plan_mode_admits_valid_verdict_after_denied_post_completion_write() -> None:
    payload = _formal_payload()
    raw = _run_result(
        _stream(
            {
                "status": "ERROR",
                "error": (
                    "permission check failed for command \"cat << 'EOF' > result.json\""
                ),
                "response": f"```json\n{json.dumps(payload)}\n```\n",
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
        plan_mode=True,
    )

    assert admitted.exit_code == _common.EXIT_OK
    assert admitted.classification == "ok"
    assert admitted.validated == payload
    assert admitted.final_answer == json.dumps(payload)


def test_plan_mode_rejects_valid_verdict_after_arbitrary_terminal_error() -> None:
    payload = _formal_payload()
    raw = _run_result(
        _stream(
            {
                "status": "ERROR",
                "error": "model backend failed after generating a response",
                "response": json.dumps(payload),
            }
        )
    )

    admitted = wrapper._interpret_run(
        raw,
        LegVerdict,
        expected_review_id="review-r1",
        expected_family="google",
        expected_content_digest="a" * 64,
        plan_mode=True,
    )

    assert admitted.exit_code == _common.EXIT_TERMINAL
    assert admitted.classification == "vendor-error"
    assert admitted.final_answer == ""


@pytest.mark.parametrize(
    "response",
    (
        "```json\n{payload}",
        "{payload}\n```",
    ),
)
def test_plan_mode_rejects_missing_native_structured_output(response: str) -> None:
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
    raw = _run_result(
        _stream(
            {
                "status": "SUCCESS",
                "response": response.format(payload=json.dumps(payload)),
            }
        )
    )

    admitted = wrapper._interpret_run(raw, LegVerdict, plan_mode=True)

    assert admitted.exit_code == _common.EXIT_SCHEMA_FAIL
    assert admitted.classification == "schema-fail"
    assert admitted.final_answer == ""
    assert "structured_output" in (admitted.validation_error or "")


@pytest.mark.parametrize(
    "response",
    (
        "prose\n{payload}",
        "{payload}\nprose",
        "{payload}\n{payload}",
        "```json\n```json\n{payload}\n```\n```",
    ),
)
def test_plan_mode_ignores_response_transport_when_native_output_is_valid(
    response: str,
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
    raw = _run_result(
        _stream(
            {
                "status": "SUCCESS",
                "response": response.format(payload=json.dumps(payload)),
                "structured_output": payload,
            }
        )
    )

    admitted = wrapper._interpret_run(raw, LegVerdict, plan_mode=True)

    assert admitted.exit_code == _common.EXIT_OK
    assert admitted.classification == "ok"
    assert admitted.validated == payload


def test_plan_mode_rejects_schema_invalid_native_structured_output() -> None:
    raw = _run_result(
        _stream(
            {
                "status": "SUCCESS",
                "response": "not a JSON object",
                "structured_output": {"review_id": "wrong"},
            }
        )
    )

    admitted = wrapper._interpret_run(raw, LegVerdict, plan_mode=True)

    assert admitted.exit_code == _common.EXIT_SCHEMA_FAIL
    assert admitted.classification == "schema-fail"
    assert admitted.final_answer == ""
    assert "LegVerdict" in (admitted.validation_error or "")


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
                json.dumps({"event": "init", "init": {"model": "gemini-3.1-pro-high"}}),
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
        _stream(
            {
                "status": "ERROR",
                "response": "looks useful",
                "structured_output": {"ok": True},
            }
        )
    )

    admitted = wrapper._interpret_run(raw, _Answer)

    assert admitted.exit_code == _common.EXIT_TERMINAL
    assert admitted.classification == "vendor-error"
    assert admitted.final_answer == ""


def test_step_text_without_terminal_result_is_extraction_error() -> None:
    raw = _run_result(
        json.dumps({"event": "step_update", "step_update": {"text_delta": "partial"}})
    )

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
    tmp_path: Path, monkeypatch, capsys
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setenv("AGY_SETTINGS_PATH", str(tmp_path / "settings.json"))
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _name: "/opt/bin/agy")
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _bin: (1, 1, 20))
    monkeypatch.setattr(
        wrapper._common, "persist_result_artifacts", lambda *_a, **_k: None
    )
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


def test_main_uses_native_schema_and_binds_formal_leg_locally(
    monkeypatch, capsys, tmp_path
) -> None:
    calls: list[list[str]] = []
    guarded: list[list[str]] = []
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
    preflight_receipt = _agy_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _bin: (1, 1, 20))
    monkeypatch.setattr(
        wrapper._common, "persist_result_artifacts", lambda *_a, **_k: None
    )
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)

    @contextlib.contextmanager
    def fake_guard(deny_rules, *, lock_timeout):
        assert lock_timeout == 30.0
        guarded.append(list(deny_rules))
        yield

    monkeypatch.setattr(wrapper._agy_settings, "agy_settings_guard", fake_guard)

    def fake_run(_cli, cmd, _cwd, _timeout, *, classify_and_log, remove_env):
        calls.append(cmd)
        assert set(remove_env) == set(wrapper.FORMAL_AGY_ENV_REMOVE)
        schema_index = cmd.index("--json-schema")
        schema = json.loads(cmd[schema_index + 1])
        assert schema["properties"]["review_id"]["const"] == "review-r1"
        assert schema["properties"]["family"]["const"] == "google"
        assert schema["properties"]["content_digest"]["const"] == "a" * 64
        return _run_result(
            _stream(
                {
                    "status": "SUCCESS",
                    "response": '{"draft":true}\n{"toolAction":"Finishing task"}\n',
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
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
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
            "--sandbox",
            "read-only",
        ],
    )

    assert wrapper.main() == 0
    assert json.loads(capsys.readouterr().out) == payload
    assert len(calls) == 1
    assert calls[0][0] == str(selected)
    assert "--sandbox" in calls[0]
    assert calls[0][calls[0].index("--mode") : calls[0].index("--mode") + 2] == [
        "--mode",
        "plan",
    ]
    assert "--dangerously-skip-permissions" in calls[0]
    assert guarded == [wrapper._agy_settings._READ_ONLY_DENY]


def test_formal_provider_failure_restores_settings_bytes(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "settings.json"
    backup = tmp_path / ".agybak"
    baseline = b'{\n  "permissions": {"allow": ["command(git)"]}\n}'
    target.write_bytes(baseline)
    monkeypatch.setenv("AGY_SETTINGS_PATH", str(target))
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _agy_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _bin: (1, 1, 20))
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(
        wrapper._common, "persist_result_artifacts", lambda *_args, **_kwargs: None
    )

    def fake_run(_cli, _cmd, _cwd, _timeout, *, classify_and_log, remove_env):
        assert classify_and_log is False
        assert set(remove_env) == set(wrapper.FORMAL_AGY_ENV_REMOVE)
        live = json.loads(target.read_text())
        assert live["permissions"]["allow"] == ["command(git)"]
        assert live["permissions"]["deny"] == wrapper._agy_settings._READ_ONLY_DENY
        assert backup.exists()
        return _run_result("", rc=7, stderr="provider failed")

    monkeypatch.setattr(wrapper._common, "_run_once", fake_run)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
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
            "--sandbox",
            "read-only",
        ],
    )

    assert wrapper.main() == _common.EXIT_CLI_FAIL
    assert target.read_bytes() == baseline
    assert not backup.exists()
    assert not target.with_name(".agy_settings.shared.json").exists()


def test_formal_main_stops_before_provider_without_read_only_sandbox(
    monkeypatch, capsys
) -> None:
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _name: "/opt/bin/agy")
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _bin: (1, 1, 20))
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
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
            "review",
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

    assert wrapper.main() == _common.EXIT_ARG_ERROR
    assert "--sandbox read-only" in capsys.readouterr().err


def test_preflight_proves_version_and_route_without_provider_submission(
    monkeypatch, capsys, tmp_path
) -> None:
    pruned: list[str] = []
    guarded: list[list[str]] = []
    catalog_probes: list[str] = []
    selector_receipt, _prompt, selected = _google_selector_fixture(tmp_path)
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _bin: (1, 1, 20))
    monkeypatch.setattr(
        wrapper,
        "_probe_agy_models",
        lambda binary: catalog_probes.append(binary) or {"gemini-3.1-pro-high"},
    )
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", pruned.append)

    @contextlib.contextmanager
    def fake_guard(deny_rules, *, lock_timeout):
        assert lock_timeout == 30.0
        guarded.append(list(deny_rules))
        yield

    monkeypatch.setattr(wrapper._agy_settings, "agy_settings_guard", fake_guard)
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
            "--sandbox",
            "read-only",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert wrapper.main() == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt == {
        "agy_version": "1.1.20",
        "effort": "high",
        "executable": str(selected),
        "google_selector_receipt_sha256": hashlib.sha256(
            selector_receipt.read_bytes()
        ).hexdigest(),
        "model": "gemini-3.1-pro-high",
        "provider_started": False,
        "review_id": "review-r1",
        "route": "agy",
        "route_args": ["--model", "gemini-3.1-pro-high", "--effort", "high"],
    }
    assert pruned == ["antigravity"]
    assert catalog_probes == [str(selected)]
    assert guarded == [wrapper._agy_settings._READ_ONLY_DENY]


def test_probe_agy_models_parses_the_advertised_catalog_and_scrubs_auth_env(
    monkeypatch,
) -> None:
    observed: dict[str, object] = {}

    def fake_run(command, **kwargs):
        observed["command"] = command
        observed["kwargs"] = kwargs
        return wrapper.subprocess.CompletedProcess(
            command,
            0,
            stdout=(
                "gemini-3.1-pro-high\tGemini 3.1 Pro (High)\n"
                "gemini-3.1-pro-low\tGemini 3.1 Pro (Low)\n"
            ),
            stderr="Fetching available models...\n",
        )

    monkeypatch.setattr(wrapper.subprocess, "run", fake_run)

    assert wrapper._probe_agy_models("/selected/agy") == {
        "gemini-3.1-pro-high",
        "gemini-3.1-pro-low",
    }
    assert observed["command"] == ["/selected/agy", "models"]
    kwargs = observed["kwargs"]
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert kwargs["check"] is False
    assert kwargs["timeout"] == 30
    assert "GOOGLE_API_KEY" not in kwargs["env"]


def test_preflight_rejects_when_required_agy_model_is_not_advertised(
    monkeypatch, capsys, tmp_path
) -> None:
    selector_receipt, _prompt, _selected = _google_selector_fixture(tmp_path)
    catalog_probes: list[str] = []
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _bin: (1, 1, 20))
    monkeypatch.setattr(
        wrapper,
        "_probe_agy_models",
        lambda binary: catalog_probes.append(binary) or {"gemini-3.1-pro-low"},
        raising=False,
    )
    monkeypatch.setattr(
        wrapper._agy_settings,
        "agy_settings_guard",
        lambda *_a, **_k: (_ for _ in ()).throw(
            AssertionError("settings guard entered")
        ),
    )
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
            "--sandbox",
            "read-only",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert wrapper.main() == _common.EXIT_TERMINAL
    assert catalog_probes == [str(_selected)]
    assert "does not advertise required model gemini-3.1-pro-high" in (
        capsys.readouterr().err
    )


def test_preflight_rejects_gemini_selector_receipt_before_binary_probe(
    monkeypatch, capsys, tmp_path
) -> None:
    selector_receipt, _prompt, _selected = _google_selector_fixture(
        tmp_path, route="gemini"
    )
    monkeypatch.setattr(
        wrapper,
        "_probe_agy_version",
        lambda _bin: (_ for _ in ()).throw(AssertionError("binary probed")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            "route proof",
            "--sandbox",
            "read-only",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert wrapper.main() == _common.EXIT_ARG_ERROR
    assert "selector receipt route mismatch" in capsys.readouterr().err


def test_agy_formal_preflight_rejects_foreign_review_before_binary_probe(
    monkeypatch, capsys, tmp_path
) -> None:
    selector_receipt, _prompt, _selected = _google_selector_fixture(tmp_path)
    record = json.loads(selector_receipt.read_text(encoding="ascii"))
    record["review_id"] = "foreign-r1"
    selector_receipt.write_bytes(
        json.dumps(
            record,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
        + b"\n"
    )
    monkeypatch.setattr(
        wrapper,
        "_probe_agy_version",
        lambda _bin: (_ for _ in ()).throw(AssertionError("binary probed")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            "route proof",
            "--sandbox",
            "read-only",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert wrapper.main() == _common.EXIT_ARG_ERROR
    assert "selector receipt review ID mismatch" in capsys.readouterr().err


def test_formal_agy_rejects_preflight_selector_mismatch_before_binary_probe(
    monkeypatch, capsys, tmp_path
) -> None:
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _agy_preflight_fixture(tmp_path, selector_receipt, selected)
    record = json.loads(preflight_receipt.read_text(encoding="ascii"))
    record["google_selector_receipt_sha256"] = "0" * 64
    preflight_receipt.write_bytes(
        json.dumps(
            record,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
        + b"\n"
    )
    monkeypatch.setattr(wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(
        wrapper,
        "_probe_agy_version",
        lambda _bin: (_ for _ in ()).throw(AssertionError("binary probed")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
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
            "--sandbox",
            "read-only",
        ],
    )

    assert wrapper.main() == _common.EXIT_ARG_ERROR
    assert "Google preflight receipt selector mismatch" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("model", "effort"),
    [
        ("gemini-3.1-pro-low", "high"),
        ("gemini-3.1-pro-high", "medium"),
    ],
)
def test_formal_agy_rejects_arguments_different_from_bound_preflight_before_probe(
    monkeypatch,
    capsys,
    tmp_path,
    model,
    effort,
) -> None:
    selector_receipt, prompt, selected = _google_selector_fixture(tmp_path)
    preflight_receipt = _agy_preflight_fixture(tmp_path, selector_receipt, selected)
    metadata = json.loads(prompt.removeprefix("Review metadata: "))
    metadata.update(
        {
            "google_preflight_effort": "high",
            "google_preflight_model": "gemini-3.1-pro-high",
            "google_preflight_receipt_sha256": hashlib.sha256(
                preflight_receipt.read_bytes()
            ).hexdigest(),
        }
    )
    prompt = "Review metadata: " + json.dumps(
        metadata,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    monkeypatch.setattr(wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(
        wrapper,
        "_probe_agy_version",
        lambda _bin: (_ for _ in ()).throw(AssertionError("binary probed")),
    )
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
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
            "--model",
            model,
            "--effort",
            effort,
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "google",
            "--expected-content-digest",
            "a" * 64,
            "--sandbox",
            "read-only",
        ],
    )

    assert wrapper.main() == _common.EXIT_ARG_ERROR
    assert "formal AGY arguments do not match bound preflight" in (
        capsys.readouterr().err
    )


def test_formal_agy_rejects_non_google_prompt_before_binary_probe(
    monkeypatch, capsys, tmp_path
) -> None:
    selector_receipt, prompt, selected = _google_selector_fixture(
        tmp_path, family="codex"
    )
    preflight_receipt = _agy_preflight_fixture(tmp_path, selector_receipt, selected)
    monkeypatch.setattr(wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(
        wrapper,
        "_probe_agy_version",
        lambda _bin: (_ for _ in ()).throw(AssertionError("binary probed")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--google-preflight-receipt",
            str(preflight_receipt),
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
            "--sandbox",
            "read-only",
        ],
    )

    assert wrapper.main() == _common.EXIT_ARG_ERROR
    assert "formal prompt selector binding mismatch" in capsys.readouterr().err


def test_formal_agy_rejects_non_google_expected_family_before_binary_probe(
    monkeypatch, tmp_path
) -> None:
    selector_receipt, prompt, _selected = _google_selector_fixture(tmp_path)
    monkeypatch.setattr(wrapper, "load_pydantic_class", lambda _spec: LegVerdict)
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(
        wrapper,
        "_probe_agy_version",
        lambda _bin: (_ for _ in ()).throw(AssertionError("binary probed")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "antigravity_wrapper.py",
            "--prompt",
            prompt,
            "--google-selector-receipt",
            str(selector_receipt),
            "--model",
            "gemini-3.1-pro-high",
            "--effort",
            "high",
            "--pydantic",
            "verdict_schema:LegVerdict",
            "--expected-review-id",
            "review-r1",
            "--expected-family",
            "codex",
            "--expected-content-digest",
            "a" * 64,
            "--sandbox",
            "read-only",
        ],
    )

    with pytest.raises(SystemExit) as rejected:
        wrapper.main()
    assert rejected.value.code == 2


def test_preflight_settings_failure_stops_before_provider(
    monkeypatch, capsys, tmp_path
) -> None:
    selector_receipt, _prompt, _selected = _google_selector_fixture(tmp_path)
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _bin: (1, 1, 20))
    monkeypatch.setattr(
        wrapper, "_probe_agy_models", lambda _bin: {"gemini-3.1-pro-high"}
    )
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _cli: None)

    @contextlib.contextmanager
    def failing_guard(_deny_rules, *, lock_timeout):
        assert lock_timeout == 30.0
        raise TimeoutError("busy settings")
        yield

    monkeypatch.setattr(wrapper._agy_settings, "agy_settings_guard", failing_guard)
    monkeypatch.setattr(
        wrapper._common,
        "_run_once",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("provider started")
        ),
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
            "--sandbox",
            "read-only",
            "--google-selector-receipt",
            str(selector_receipt),
            "--expected-review-id",
            "review-r1",
            "--preflight-only",
        ],
    )

    assert wrapper.main() == _common.EXIT_TERMINAL
    assert "AGY settings/config conflict: busy settings" in capsys.readouterr().err
