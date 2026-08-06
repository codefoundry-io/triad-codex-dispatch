#!/usr/bin/env python3
"""Single-shot Claude CLI transport wrapper.

Forwards a prompt to Claude's JSON output mode along with only native model,
effort, fallback-model, working-directory, timeout, schema, and debug controls.
Provider-owned permission and trust settings are left to the native CLI.

Stdout is the final answer text from envelope `.result` (or, with
``--pydantic``, the validated JSON object). Stderr is wrapper logging and
Claude's progress noise. Audit results are written to
``_logs/claude/audit.jsonl`` (gitignored).
"""
from __future__ import annotations

import argparse
import json
import sys

import _common
from _common import (
    validate_wrapper_cwd,
    load_prompt_text,
    EXIT_ARG_ERROR,
    persist_result_artifacts,
    load_pydantic_class,
    log,
    require_binary,
    run_cli_with_retry,
)


EFFORT_CHOICES = ("low", "medium", "high", "xhigh", "max")


def _run_native_structured_once(
    cmd: list[str], cwd: str, timeout: int, pydantic_cls
) -> _common.RunResult:
    """Run one Claude call and validate its native structured output."""
    _common.prune_stale_run_logs("claude")
    result = _common._run_once(
        "claude", cmd, cwd, timeout, classify_and_log=False
    )
    answer, extraction_error = _common.extract_claude_answer(
        result.stdout, result.stderr
    )
    try:
        envelope = json.loads(result.stdout)
    except (TypeError, ValueError, json.JSONDecodeError):
        envelope = None
    has_native_structured_output = (
        isinstance(envelope, dict)
        and envelope.get("structured_output") is not None
    )

    if result.exit_code != _common.EXIT_OK:
        classification = _common.classify(
            "claude",
            result.stderr,
            result.stdout,
            result.exit_code,
            vendor_exit_code=result.vendor_exit_code,
        )
        result.classification = classification
        result.exit_code = _common.map_classification_to_exit(classification)
        result.final_answer = ""
    elif extraction_error is not None:
        result.extraction_error = extraction_error
        classification = _common.classify(
            "claude", extraction_error, "", _common.EXIT_CLI_FAIL,
            vendor_exit_code=result.vendor_exit_code,
        )
        if classification == "unknown":
            classification = "extraction-error"
        result.classification = classification
        result.exit_code = _common.map_classification_to_exit(classification)
        result.final_answer = ""
    elif not has_native_structured_output:
        result.classification = "schema-fail"
        result.exit_code = _common.EXIT_SCHEMA_FAIL
        result.validation_error = "claude native structured_output is missing"
        result.final_answer = ""
    else:
        valid, validated_or_error = _common.validate_response(
            answer, pydantic_cls
        )
        if valid:
            result.classification = "ok"
            result.validated = validated_or_error
            result.final_answer = json.dumps(
                validated_or_error, ensure_ascii=False
            )
        else:
            result.classification = "schema-fail"
            result.exit_code = _common.EXIT_SCHEMA_FAIL
            result.validation_error = str(validated_or_error)
            result.final_answer = ""

    log(
        f"[wrapper] claude {result.classification} "
        f"exit={result.exit_code} vendor={result.vendor_exit_code} "
        f"elapsed={result.elapsed_s:.1f}s"
    )
    return result


def main() -> int:
    p = argparse.ArgumentParser(description="Claude CLI single-shot wrapper",
                                allow_abbrev=False)
    prompt_group = p.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="User prompt")
    prompt_group.add_argument(
        "--prompt-file",
        help="Read the user prompt from a UTF-8 file (>=50K-char prompts: pass "
             "a file, not inline argv — L12; containment applies under "
             "TRIAD_WRAPPER_ALLOWED_ROOTS)")
    p.add_argument(
        "--cwd",
        default=None,
        help="Process working directory (caller-owned — use a sibling directory for isolation)",
    )
    p.add_argument("--timeout", type=int, default=600, help="Timeout in seconds")
    p.add_argument(
        "--model",
        default=None,
        help="Model for the session — claude CLI --model passthrough (an alias "
             "for the latest, or a full model name). Unrestricted FREE STRING "
             "caller passthrough; no generic wrapper default. Formal-review "
             "callers must follow the cross-family routing contract.",
    )
    p.add_argument(
        "--effort",
        default=None,
        choices=EFFORT_CHOICES,
        help="Reasoning effort level (default: vendor default)",
    )
    p.add_argument(
        "--fallback-model",
        default=None,
        help="Auto-fallback model name when default overloaded",
    )
    p.add_argument(
        "--pydantic",
        default=None,
        help="pydantic class spec (module.path:ClassName) for schema enforcement",
    )
    p.add_argument(
        "--repair-mode",
        action="store_true",
        help="Compatibility diagnostic: one provider attempt with retries disabled; "
             "the fresh native proposal-only repair child does not invoke providers",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        help="Append a human-readable markdown row to "
             "_debug/<UTC-YYYY-MM-DD>/claude.md (per-call summary)",
    )
    args = p.parse_args()

    try:
        _prompt_text = load_prompt_text(args.prompt, args.prompt_file)
    except Exception as e:
        log(f"prompt load failed: {e}")
        return EXIT_ARG_ERROR
    args.prompt = _prompt_text  # downstream code keeps using args.prompt

    try:
        args.cwd = validate_wrapper_cwd(args.cwd)
    except Exception as e:
        log(f"--cwd validation failed: {e}")
        return EXIT_ARG_ERROR

    if not args.prompt.strip():
        log("empty prompt")
        return EXIT_ARG_ERROR

    pydantic_cls = None
    if args.pydantic:
        try:
            pydantic_cls = load_pydantic_class(args.pydantic)
        except Exception as e:
            log(f"--pydantic load failed: {e}")
            return EXIT_ARG_ERROR

    if args.repair_mode and pydantic_cls is not None:
        log("--repair-mode is unavailable with --pydantic structured output")
        return EXIT_ARG_ERROR

    claude_bin = require_binary("claude")

    def build_cmd(
        effective_prompt: str, native_schema: str | None = None
    ) -> list[str]:
        cmd = [
            claude_bin,   # resolved/pinned path (finding #3) — never a bare name
            "-p", effective_prompt,
            "--output-format", "json",
        ]
        if args.model:
            cmd += ["--model", args.model]
        if args.effort:
            cmd += ["--effort", args.effort]
        if args.fallback_model:
            cmd += ["--fallback-model", args.fallback_model]
        if native_schema is not None:
            cmd += ["--json-schema", native_schema]
        return cmd

    native_schema = None
    if pydantic_cls is not None:
        native_schema = json.dumps(
            pydantic_cls.model_json_schema(),
            ensure_ascii=False,
            separators=(",", ":"),
        )
        result = _run_native_structured_once(
            build_cmd(args.prompt, native_schema),
            args.cwd,
            args.timeout,
            pydantic_cls,
        )
    else:
        result = run_cli_with_retry(
            "claude",
            build_cmd,
            args.prompt,
            cwd=args.cwd,
            timeout=args.timeout,
            pydantic_cls=None,
            last_msg_path=None,
            repair_mode=args.repair_mode,
        )

    audit_cmd = build_cmd(args.prompt, native_schema)
    persist_result_artifacts(
        "claude", sys.argv, audit_cmd, args.prompt, result, debug=args.debug
    )

    if pydantic_cls and result.validated is not None:
        sys.stdout.write(json.dumps(result.validated, ensure_ascii=False))
        sys.stdout.write("\n")
    else:
        sys.stdout.write(result.final_answer or "")
        if result.final_answer and not result.final_answer.endswith("\n"):
            sys.stdout.write("\n")
    sys.stdout.flush()
    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
