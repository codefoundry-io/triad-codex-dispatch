#!/usr/bin/env python3
"""Single-shot Gemini CLI transport wrapper.

Forwards ordinary prompts with provider-native controls. The exact formally
bound ``LegVerdict`` route is reserved for preselected Gemini Enterprise OAuth:
it consumes one selector receipt, explicitly requests CLI Auto and native Plan
Mode, uses a mode-independent packaged read/search-only policy as its enforcement
boundary, scrubs competing selectors, makes one provider call, records literal
``unexposed`` mode/model identity, and performs local review-binding admission.

Stdout is Gemini's final response text (or, with ``--pydantic``, the validated
JSON object). Stderr is wrapper logging and Gemini's warning noise. Audit
results are written to ``_logs/gemini/audit.jsonl`` (gitignored).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import _common
import review_round
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


FORMAL_VERDICT_SPECS = {
    "verdict_schema:LegVerdict",
    "verdict_schema.LegVerdict",
}
FORMAL_GEMINI_REMOVED_ENV = (
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
FORMAL_READ_TOOLS = {
    "read_file",
    "read_many_files",
    "list_directory",
    "glob",
    "grep_search",
    "google_web_search",
    "web_fetch",
    "get_internal_docs",
}
FORMAL_DENIED_TOOLS = {
    "write_file",
    "replace",
    "run_shell_command",
    "enter_plan_mode",
    "exit_plan_mode",
}


def _formal_policy_path() -> Path:
    return Path(__file__).resolve().parent / "policies" / "gemini-formal-readonly.toml"


def _rule_tools(rule: dict[str, object]) -> set[str]:
    value = rule.get("toolName")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return set(value)
    return set()


def _validate_formal_policy(path: Path) -> None:
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ValueError(
            f"formal Gemini policy is unavailable or invalid: {error}"
        ) from error
    rules = payload.get("rule")
    if not isinstance(rules, list) or not all(isinstance(rule, dict) for rule in rules):
        raise ValueError("formal Gemini policy has no valid rules")
    actual_rules: list[tuple[str, int, frozenset[str]]] = []
    for rule in rules:
        tools = _rule_tools(rule)
        raw_tools = rule.get("toolName")
        decision = rule.get("decision")
        priority = rule.get("priority")
        if (
            set(rule) - {"toolName", "decision", "priority", "denyMessage"}
            or not tools
            or (isinstance(raw_tools, list) and len(raw_tools) != len(tools))
            or not isinstance(decision, str)
            or not isinstance(priority, int)
        ):
            raise ValueError(
                "formal Gemini policy is not the exact fail-closed rule set"
            )
        actual_rules.append((decision, priority, frozenset(tools)))
    expected_rules = {
        ("allow", 999, frozenset(FORMAL_READ_TOOLS)),
        ("deny", 999, frozenset(FORMAL_DENIED_TOOLS)),
        ("deny", 998, frozenset({"*"})),
    }
    if len(actual_rules) != len(expected_rules) or set(actual_rules) != expected_rules:
        raise ValueError("formal Gemini policy is not the exact fail-closed rule set")


def _supports_formal_help_contract(help_text: str) -> bool:
    model = re.search(
        r"(?m)^\s*(?:-m,\s*)?--model\b[^\n]*\bModel\b[^\n]*\[string\]\s*$",
        help_text,
    )
    approval_mode = re.search(
        r"(?m)^\s*--approval-mode\b[^\n]*Set the approval mode[^\n]*"
        r'\[choices:[^\n]*"plan"[^\n]*\]\s*$',
        help_text,
    )
    policy = re.search(
        r"(?m)^\s*--policy\b[^\n]*Additional policy files or directories to load"
        r"[^\n]*\[array\]\s*$",
        help_text,
    )
    return model is not None and approval_mode is not None and policy is not None


def _run_preflight(
    gemini_bin: str,
    cwd: str | None,
    timeout: int,
    selector_receipt: review_round.GoogleSelectorReceipt,
) -> int:
    policy = _formal_policy_path()
    try:
        _validate_formal_policy(policy)
        completed = subprocess.run(
            [gemini_bin, "--help"],
            cwd=cwd,
            env=_common.scrubbed_child_env(remove=FORMAL_GEMINI_REMOVED_ENV),
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired, ValueError) as error:
        log(f"Gemini formal preflight failed: {error}")
        return EXIT_ARG_ERROR
    help_text = f"{completed.stdout}\n{completed.stderr}"
    if completed.returncode != 0 or not _supports_formal_help_contract(help_text):
        log(
            "Gemini formal preflight did not prove Plan Mode, policy, and Auto model support"
        )
        return EXIT_ARG_ERROR
    sys.stdout.write(
        json.dumps(
            {
                "effective_approval_mode": "unexposed",
                "executable": gemini_bin,
                "google_selector_receipt_sha256": selector_receipt.receipt_sha256,
                "model": "auto",
                "policy": str(policy),
                "provider_started": False,
                "read_only_enforcement": "packaged-mode-independent-policy",
                "requested_approval_mode": "plan",
                "review_id": selector_receipt.review_id,
                "route": "gemini",
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )
    sys.stdout.flush()
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Gemini CLI single-shot wrapper", allow_abbrev=False
    )
    prompt_group = p.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="User prompt")
    prompt_group.add_argument(
        "--prompt-file",
        help="Read the user prompt from a UTF-8 file (>=50K-char prompts: pass "
        "a file, not inline argv — L12; containment applies under "
        "TRIAD_WRAPPER_ALLOWED_ROOTS)",
    )
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
    p.add_argument("--expected-review-id", default=None)
    p.add_argument("--expected-family", choices=("google",), default=None)
    p.add_argument("--expected-content-digest", default=None)
    p.add_argument("--google-selector-receipt", type=Path, default=None)
    p.add_argument("--google-preflight-receipt", type=Path, default=None)
    p.add_argument("--preflight-only", action="store_true")
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

    formal_verdict = args.pydantic in FORMAL_VERDICT_SPECS
    pydantic_cls = None
    if args.pydantic:
        try:
            pydantic_cls = load_pydantic_class(args.pydantic)
        except Exception as e:
            log(f"--pydantic load failed: {e}")
            return EXIT_ARG_ERROR

    binding_values = (
        args.expected_review_id,
        args.expected_family,
        args.expected_content_digest,
    )
    if args.preflight_only:
        if (
            args.expected_review_id is None
            or args.expected_family is not None
            or args.expected_content_digest is not None
        ):
            log("Gemini formal preflight requires only --expected-review-id")
            return EXIT_ARG_ERROR
    else:
        if formal_verdict and not all(value is not None for value in binding_values):
            log("formal verdict schema requires all formal verdict bindings")
            return EXIT_ARG_ERROR
        if any(value is not None for value in binding_values):
            if not all(value is not None for value in binding_values):
                log("formal verdict bindings must be supplied together")
                return EXIT_ARG_ERROR
            if not formal_verdict:
                log("formal verdict bindings require packaged LegVerdict schema")
                return EXIT_ARG_ERROR
            if re.fullmatch(r"[0-9a-f]{64}", args.expected_content_digest) is None:
                log(
                    "expected content digest must be 64 lowercase hexadecimal characters"
                )
                return EXIT_ARG_ERROR
    if (
        args.expected_review_id is not None
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.expected_review_id) is None
    ):
        log("expected review ID has invalid syntax")
        return EXIT_ARG_ERROR
    if formal_verdict and (args.timeout <= 0 or args.model is not None):
        log(
            "formal Gemini review requires a positive timeout and CLI Auto model routing"
        )
        return EXIT_ARG_ERROR
    if args.preflight_only and (
        args.pydantic is not None or args.model is not None or args.repair_mode
    ):
        log("Gemini formal preflight does not accept model, schema, or repair controls")
        return EXIT_ARG_ERROR

    selected_context = formal_verdict or args.preflight_only
    if selected_context and args.google_selector_receipt is None:
        log("formal Gemini route requires --google-selector-receipt")
        return EXIT_ARG_ERROR
    if not selected_context and args.google_selector_receipt is not None:
        log("Google selector receipt is reserved for formal review and preflight")
        return EXIT_ARG_ERROR
    if formal_verdict and args.google_preflight_receipt is None:
        log("formal Gemini review requires --google-preflight-receipt")
        return EXIT_ARG_ERROR
    if not formal_verdict and args.google_preflight_receipt is not None:
        log("Google preflight receipt is reserved for formal dispatch")
        return EXIT_ARG_ERROR
    selector_receipt = None
    if args.google_selector_receipt is not None:
        try:
            selector_receipt = review_round.load_google_selector_receipt(
                args.google_selector_receipt,
                expected_review_id=args.expected_review_id,
                expected_route="gemini",
                expected_wrapper=Path(__file__).resolve(),
            )
            if formal_verdict:
                selector_receipt = review_round.validate_google_preflight_receipt(
                    args.google_preflight_receipt,
                    selector_receipt,
                    expected_review_id=args.expected_review_id,
                )
                review_round.validate_google_selector_prompt(
                    args.prompt,
                    selector_receipt,
                    expected_review_id=args.expected_review_id,
                    expected_content_digest=args.expected_content_digest,
                )
        except review_round.RoundIntegrityError as error:
            log(f"Google selector receipt rejected: {error}")
            return EXIT_ARG_ERROR

    gemini_bin = (
        str(selector_receipt.executable)
        if selector_receipt is not None
        else require_binary("gemini")
    )
    policy = _formal_policy_path()
    if formal_verdict:
        try:
            _validate_formal_policy(policy)
        except ValueError as error:
            log(str(error))
            return EXIT_ARG_ERROR
    if args.preflight_only:
        return _run_preflight(gemini_bin, args.cwd, args.timeout, selector_receipt)

    def build_cmd(effective_prompt: str) -> list[str]:
        cmd = [
            gemini_bin,  # resolved/pinned path (finding #3) — never a bare name
            "-p",
            effective_prompt,
            "--output-format",
            "json",
        ]
        if formal_verdict:
            cmd += [
                "-m",
                "auto",
                "--approval-mode",
                "plan",
                "--policy",
                str(policy),
            ]
        elif args.model:
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
        remove_env=FORMAL_GEMINI_REMOVED_ENV if formal_verdict else (),
    )

    if formal_verdict:
        result.runtime_identity = result.runtime_identity or "unexposed"

    if formal_verdict and result.exit_code == _common.EXIT_OK:
        for field, expected in (
            ("review_id", args.expected_review_id),
            ("family", args.expected_family),
            ("content_digest", args.expected_content_digest),
        ):
            if result.validated is None or result.validated.get(field) != expected:
                result.exit_code = _common.EXIT_SCHEMA_FAIL
                result.classification = "schema-fail"
                result.validation_error = f"{field.replace('_', ' ')} mismatch"
                result.final_answer = ""
                result.validated = None
                break

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
