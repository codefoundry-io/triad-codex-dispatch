#!/usr/bin/env python3
"""Single-shot AGY wrapper using the 1.1.17 headless plan-mode contract.

The wrapper forwards one prompt through ``stream-json``, admits only the
terminal ``result`` event, and validates contracted output locally. Formal
plan-mode calls omit the unsupported native finish schema. Read-only calls use
the same transient global-settings transaction and headless adaptation as the
deployed Claude-led TRIAD wrapper.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Any

import _common
import _agy_settings
from _common import load_pydantic_class, validate_response


AGY_VERSION_FLOOR = (1, 1, 17)
OFFSET_S = 10
MIN_PRINT_TIMEOUT_S = 5
HEADLESS_SOFTDENY_FLOOR = (1, 1, 3)
FORMAL_AGY_ENV_REMOVE = (
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GOOGLE_GENAI_USE_ENTERPRISE",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    "GOOGLE_CLOUD_REGION",
    "GOOGLE_CLOUD_QUOTA_PROJECT",
    "AGY_ADC_AUTH",
)
_FORMAL_PLAN_READ_TOOLS = frozenset(
    {
        "code_search",
        "find_by_name",
        "grep_search",
        "list_dir",
        "read_url_content",
        "search_web",
        "view_file",
    }
)


def _parse_agy_version(text: str) -> tuple[int, int, int] | None:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", text or "")
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def _probe_agy_version(agy_bin: str) -> tuple[int, int, int] | None:
    try:
        result = subprocess.run(
            [agy_bin, "--version"],
            capture_output=True,
            text=True,
            timeout=15,
            env=_common.scrubbed_child_env(),
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return _parse_agy_version(result.stdout)


def _route_args(model: str | None, effort: str | None) -> list[str]:
    args: list[str] = []
    if model:
        args += ["--model", model]
    if effort:
        args += ["--effort", effort]
    return args


def _agy_needs_skip_permissions(version: tuple[int, int, int] | None) -> bool:
    if os.environ.get("AGY_NO_HEADLESS_AUTOAPPROVE") == "1":
        return False
    return version is not None and version >= HEADLESS_SOFTDENY_FLOOR


def _build_cmd(
    agy_bin: str,
    prompt: str,
    *,
    model: str | None,
    effort: str | None,
    timeout: int,
    json_schema: str | None,
    sandbox: bool = False,
    skip_permissions: bool = True,
) -> list[str]:
    print_timeout = max(timeout - OFFSET_S, MIN_PRINT_TIMEOUT_S)
    cmd = [agy_bin]
    if skip_permissions:
        cmd.append("--dangerously-skip-permissions")
    cmd += [
        "-p",
        prompt,
        "--output-format",
        "stream-json",
        "--print-timeout",
        f"{print_timeout}s",
    ]
    if json_schema is not None:
        cmd += ["--json-schema", json_schema]
    if sandbox:
        cmd += ["--mode", "plan", "--sandbox"]
    return cmd + _route_args(model, effort)


def parse_agy_stream(text: str) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Return parsed events and the last complete terminal result payload."""
    events: list[dict[str, Any]] = []
    terminal: dict[str, Any] | None = None
    for line in (text or "").split("\n"):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        events.append(event)
        payload = event.get("result")
        if event.get("event") == "result" and isinstance(payload, dict):
            terminal = payload
    return events, terminal


def _plan_tool_contract_error(events: list[dict[str, Any]]) -> str | None:
    seen_steps: dict[int, tuple[object, object]] = {}
    for event in events:
        update = event.get("step_update")
        if event.get("event") != "step_update" or not isinstance(update, dict):
            continue
        if update.get("step_type") != "tool":
            continue
        step_index = update.get("step_index")
        if type(step_index) is not int:
            return "formal plan tool has missing or non-integer step_index"
        tool_name = update.get("tool_name")
        tool_info = update.get("tool_info")
        parameters = (
            tool_info.get("parameters") if isinstance(tool_info, dict) else None
        )
        representation = (tool_name, parameters)
        if step_index in seen_steps:
            if seen_steps[step_index] != representation:
                return f"formal plan tool step {step_index} has conflicting duplicate telemetry"
            continue
        seen_steps[step_index] = representation
        if tool_name not in _FORMAL_PLAN_READ_TOOLS:
            return f"formal plan attempted forbidden tool {tool_name!r}"
        if not isinstance(parameters, dict):
            return f"formal plan tool {tool_name!r} has invalid parameters"
        if tool_name == "grep_search":
            allowed = {
                "SearchPath",
                "Query",
                "IsRegex",
                "CaseInsensitive",
                "Includes",
                "MatchPerLine",
            }
            unexpected = sorted(set(parameters) - allowed)
            if unexpected:
                return f"formal plan grep_search has forbidden arguments {unexpected!r}"
            for name in ("SearchPath", "Query"):
                value = parameters.get(name)
                if not isinstance(value, str) or not value:
                    return f"formal plan grep_search has invalid {name}"
        if tool_name == "view_file":
            allowed = {"AbsolutePath", "StartLine", "EndLine"}
            if "AbsolutePath" not in parameters or not set(parameters) <= allowed:
                unexpected = sorted(set(parameters) - allowed)
                return f"formal plan view_file has forbidden arguments {unexpected!r}"
            view_path = parameters.get("AbsolutePath")
            if not isinstance(view_path, str) or not view_path:
                return "formal plan view_file has invalid AbsolutePath"
            for name in ("StartLine", "EndLine"):
                value = parameters.get(name)
                if name in parameters and (type(value) is not int or value < 1):
                    return f"formal plan view_file has invalid line range {name}"
            if (
                "StartLine" in parameters
                and "EndLine" in parameters
                and parameters["EndLine"] < parameters["StartLine"]
            ):
                return "formal plan view_file has invalid line range"
    return None


def _fail(
    run: _common.RunResult,
    classification: str,
    exit_code: int,
    detail: str,
) -> _common.RunResult:
    run.classification = classification
    run.exit_code = exit_code
    run.final_answer = ""
    run.extraction_error = detail
    run.dispatch_phase = "post-dispatch-result"
    return run


def _interpret_run(
    run: _common.RunResult,
    pydantic_cls: Any,
    expected_model: str | None = None,
    *,
    expected_review_id: str | None = None,
    expected_family: str | None = None,
    expected_content_digest: str | None = None,
    plan_mode: bool = False,
) -> _common.RunResult:
    """Admit one terminal AGY result after enforcing formal tool telemetry."""
    run.runtime_identity = "unexposed"
    events, result = parse_agy_stream(run.stdout)
    exposed_model = None
    route_conflict = None
    for event in events:
        if event.get("event") != "init":
            continue
        init = event.get("init")
        if isinstance(init, dict) and isinstance(init.get("model"), str):
            exposed_model = init["model"]
            if (
                expected_model is not None
                and exposed_model != expected_model
                and route_conflict is None
            ):
                route_conflict = exposed_model
    run.runtime_identity = route_conflict or exposed_model or run.runtime_identity
    if run.exit_code == _common.EXIT_TIMEOUT:
        return _fail(run, "timeout", _common.EXIT_TIMEOUT, "provider timed out")

    status = result.get("status") if isinstance(result, dict) else None

    if run.vendor_exit_code != 0:
        detail = "\n".join(
            part for part in (run.stderr, f"agy result status={status}") if part
        )
        classification = _common.classify(
            "antigravity",
            stderr=detail,
            stdout="",
            exit_code=_common.EXIT_CLI_FAIL,
            vendor_exit_code=run.vendor_exit_code,
        )
        return _fail(
            run,
            classification,
            _common.map_classification_to_exit(classification),
            detail or "AGY exited without an admissible result",
        )

    if result is None:
        return _fail(
            run,
            "extraction-error",
            _common.EXIT_CLI_FAIL,
            "missing terminal result event",
        )
    if status != "SUCCESS":
        return _fail(
            run,
            "vendor-error",
            _common.EXIT_TERMINAL,
            f"terminal result status is {status!r}",
        )
    if expected_model is not None and route_conflict is not None:
        return _fail(
            run,
            "route-mismatch",
            _common.EXIT_TERMINAL,
            f"requested model {expected_model!r} but AGY exposed {route_conflict!r}",
        )
    if plan_mode and (tool_error := _plan_tool_contract_error(events)) is not None:
        return _fail(
            run,
            "tool-contract-violation",
            _common.EXIT_TERMINAL,
            tool_error,
        )

    if pydantic_cls is not None:
        if plan_mode:
            response = result.get("response")
            if not isinstance(response, str) or (
                response.strip().startswith("```") != response.strip().endswith("```")
            ):
                run.validation_error = (
                    "plan-mode terminal response is not a valid JSON object"
                )
                return _fail(
                    run,
                    "schema-fail",
                    _common.EXIT_SCHEMA_FAIL,
                    run.validation_error,
                )
            encoded = response
        else:
            structured = result.get("structured_output")
            if structured is None:
                run.validation_error = "terminal result has no structured_output"
                return _fail(
                    run,
                    "schema-fail",
                    _common.EXIT_SCHEMA_FAIL,
                    run.validation_error,
                )
            encoded = json.dumps(structured, ensure_ascii=False, separators=(",", ":"))
        valid, payload = validate_response(encoded, pydantic_cls)
        if not valid:
            run.validation_error = (
                f"plan-mode terminal response is not a valid JSON object matching "
                f"LegVerdict: {payload}"
                if plan_mode
                else str(payload)
            )
            return _fail(
                run,
                "schema-fail",
                _common.EXIT_SCHEMA_FAIL,
                f"local schema validation failed: {payload}",
            )
        for field, expected in (
            ("review_id", expected_review_id),
            ("family", expected_family),
            ("content_digest", expected_content_digest),
        ):
            if expected is not None and payload.get(field) != expected:
                run.validation_error = f"{field.replace('_', ' ')} mismatch"
                return _fail(
                    run,
                    "schema-fail",
                    _common.EXIT_SCHEMA_FAIL,
                    run.validation_error,
                )
        run.validated = payload
        run.final_answer = json.dumps(payload, ensure_ascii=False)
    else:
        response = result.get("response")
        if not isinstance(response, str) or not response.strip():
            return _fail(
                run,
                "extraction-error",
                _common.EXIT_CLI_FAIL,
                "terminal result has no non-empty response",
            )
        run.final_answer = response.rstrip()

    run.exit_code = _common.EXIT_OK
    run.classification = "ok"
    run.dispatch_phase = "post-dispatch-result"
    return run


def _version_text(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AGY native stream-json single-shot wrapper",
        allow_abbrev=False,
    )
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="User prompt")
    prompt_group.add_argument("--prompt-file", help="Read a UTF-8 prompt file")
    parser.add_argument("--cwd", default=None)
    parser.add_argument("--sandbox", choices=("read-only",), default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--effort", choices=("low", "medium", "high"), default=None)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--pydantic", default=None, help="module:Class schema contract")
    parser.add_argument("--expected-review-id", default=None)
    parser.add_argument(
        "--expected-family",
        choices=("claude", "google", "codex"),
        default=None,
    )
    parser.add_argument("--expected-content-digest", default=None)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    try:
        prompt = _common.load_prompt_text(args.prompt, args.prompt_file)
        cwd = _common.validate_wrapper_cwd(args.cwd)
    except Exception as exc:
        _common.log(f"argument validation failed: {exc}")
        return _common.EXIT_ARG_ERROR
    if not prompt.strip() or args.timeout <= 0:
        _common.log("prompt must be non-empty and timeout must be positive")
        return _common.EXIT_ARG_ERROR
    _common.prune_stale_run_logs("antigravity")

    pydantic_cls = None
    if args.pydantic:
        try:
            pydantic_cls = load_pydantic_class(args.pydantic)
        except Exception as exc:
            _common.log(f"--pydantic load failed: {exc}")
            return _common.EXIT_ARG_ERROR

    binding_values = (
        args.expected_review_id,
        args.expected_family,
        args.expected_content_digest,
    )
    if any(value is not None for value in binding_values):
        if not all(value is not None for value in binding_values):
            _common.log("formal verdict bindings must be supplied together")
            return _common.EXIT_ARG_ERROR
        if args.pydantic != "verdict_schema:LegVerdict":
            _common.log(
                "formal verdict bindings require --pydantic verdict_schema:LegVerdict"
            )
            return _common.EXIT_ARG_ERROR
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.expected_review_id) is None:
            _common.log("expected review ID has invalid syntax")
            return _common.EXIT_ARG_ERROR
        if re.fullmatch(r"[0-9a-f]{64}", args.expected_content_digest) is None:
            _common.log(
                "expected content digest must be 64 lowercase hexadecimal characters"
            )
            return _common.EXIT_ARG_ERROR
        if args.sandbox != "read-only":
            _common.log("formal verdict bindings require --sandbox read-only")
            return _common.EXIT_ARG_ERROR

    agy_bin = _common.require_binary("agy")
    version = _probe_agy_version(agy_bin)
    if version is None or version < AGY_VERSION_FLOOR:
        found = _version_text(version) if version is not None else "unprobeable"
        _common.log(f"agy {found} is below required {_version_text(AGY_VERSION_FLOOR)}")
        return _common.EXIT_TERMINAL

    deny_rules = (
        _agy_settings.build_deny_rules(args.sandbox) if args.sandbox is not None else []
    )
    try:
        lock_timeout = float(os.environ.get("AGY_SETTINGS_LOCK_TIMEOUT", "30"))
    except ValueError:
        _common.log("AGY_SETTINGS_LOCK_TIMEOUT must be a number")
        return _common.EXIT_ARG_ERROR

    if args.preflight_only:
        try:
            with _agy_settings.agy_settings_guard(
                deny_rules,
                lock_timeout=lock_timeout,
            ):
                pass
        except (TimeoutError, json.JSONDecodeError, ValueError, OSError) as exc:
            _common.log(f"AGY settings/config conflict: {exc}")
            return _common.EXIT_TERMINAL
        receipt = {
            "agy_version": _version_text(version),
            "effort": args.effort,
            "model": args.model,
            "provider_started": False,
            "route_args": _route_args(args.model, args.effort),
        }
        sys.stdout.write(json.dumps(receipt, ensure_ascii=False) + "\n")
        return _common.EXIT_OK

    local_plan_response = args.sandbox == "read-only" and all(
        value is not None for value in binding_values
    )
    try:
        schema_object = (
            pydantic_cls.model_json_schema()
            if pydantic_cls is not None and not local_plan_response
            else None
        )
        if schema_object is not None:
            properties = schema_object["properties"]
            if all(value is not None for value in binding_values):
                properties["review_id"]["const"] = args.expected_review_id
                properties["family"]["const"] = args.expected_family
                properties["content_digest"]["const"] = args.expected_content_digest
        schema = (
            json.dumps(schema_object, ensure_ascii=True, separators=(",", ":"))
            if schema_object is not None
            else None
        )
    except Exception as exc:
        _common.log(f"schema generation failed: {exc}")
        return _common.EXIT_ARG_ERROR

    cmd = _build_cmd(
        agy_bin,
        prompt,
        model=args.model,
        effort=args.effort,
        timeout=args.timeout,
        json_schema=schema,
        sandbox=args.sandbox == "read-only",
        skip_permissions=_agy_needs_skip_permissions(version),
    )
    run_options: dict[str, Any] = {"classify_and_log": False}
    if all(value is not None for value in binding_values):
        run_options["remove_env"] = FORMAL_AGY_ENV_REMOVE
    try:
        with _agy_settings.agy_settings_guard(
            deny_rules,
            lock_timeout=lock_timeout,
        ):
            raw = _common._run_once(
                "antigravity",
                cmd,
                cwd,
                args.timeout,
                **run_options,
            )
    except (TimeoutError, json.JSONDecodeError, ValueError, OSError) as exc:
        _common.log(f"AGY settings/config conflict: {exc}")
        return _common.EXIT_TERMINAL
    result = _interpret_run(
        raw,
        pydantic_cls,
        args.model,
        expected_review_id=args.expected_review_id,
        expected_family=args.expected_family,
        expected_content_digest=args.expected_content_digest,
        plan_mode=local_plan_response,
    )
    _common.log(
        f"[wrapper] antigravity {result.classification} "
        f"exit={result.exit_code} vendor={result.vendor_exit_code} "
        f"elapsed={result.elapsed_s:.1f}s"
    )
    _common.persist_result_artifacts(
        "antigravity",
        sys.argv,
        cmd,
        prompt,
        result,
        debug=args.debug,
    )

    if result.exit_code == _common.EXIT_OK:
        sys.stdout.write(result.final_answer)
        if result.final_answer and not result.final_answer.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
