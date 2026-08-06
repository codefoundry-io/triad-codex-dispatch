#!/usr/bin/env python3
"""Single-shot Gemini CLI transport wrapper.

Forwards a prompt to Gemini's JSON output mode along with only native model,
working-directory, timeout, schema, repair, and debug
controls. Provider-owned permission and workspace-trust settings are left to
the native CLI.

Stdout is Gemini's final response text (or, with ``--pydantic``, the validated
JSON object). Stderr is wrapper logging and Gemini's warning noise. Audit
results are written to ``_logs/gemini/audit.jsonl`` (gitignored).
"""
from __future__ import annotations

import argparse
import json
import sys

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


def main() -> int:
    p = argparse.ArgumentParser(description="Gemini CLI single-shot wrapper",
                                allow_abbrev=False)
    prompt_group = p.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="User prompt")
    prompt_group.add_argument(
        "--prompt-file",
        help="Read the user prompt from a UTF-8 file (>=50K-char prompts: pass "
             "a file, not inline argv — L12; containment applies under "
             "TRIAD_WRAPPER_ALLOWED_ROOTS)")
    p.add_argument("--cwd", default=None, help="Process working directory")
    p.add_argument("--timeout", type=int, default=600, help="Timeout in seconds")
    p.add_argument(
        "--model",
        default=None,
        help="Pin a specific model (free-form). Default = CLI Auto router.",
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
             "_debug/<UTC-YYYY-MM-DD>/gemini.md (per-call summary)",
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

    formal_verdict = args.pydantic in {
        "verdict_schema:LegVerdict",
        "verdict_schema.LegVerdict",
    }
    pydantic_cls = None
    if args.pydantic:
        try:
            pydantic_cls = load_pydantic_class(args.pydantic)
        except Exception as e:
            log(f"--pydantic load failed: {e}")
            return EXIT_ARG_ERROR

    gemini_bin = require_binary("gemini")

    def build_cmd(effective_prompt: str) -> list[str]:
        cmd = [
            gemini_bin,   # resolved/pinned path (finding #3) — never a bare name
            "-p", effective_prompt,
            "--output-format", "json",
        ]
        if args.model:
            cmd += ["-m", args.model]
        return cmd

    result = run_cli_with_retry(
        "gemini",
        build_cmd,
        args.prompt,
        cwd=args.cwd,
        timeout=args.timeout,
        pydantic_cls=pydantic_cls,
        last_msg_path=None,
        repair_mode=args.repair_mode,
        single_provider_call=formal_verdict,
    )

    audit_cmd = build_cmd(args.prompt)
    persist_result_artifacts(
        "gemini", sys.argv, audit_cmd, args.prompt, result, debug=args.debug
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
