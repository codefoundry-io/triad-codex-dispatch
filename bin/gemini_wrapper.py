#!/usr/bin/env python3
"""Single-shot Gemini CLI subprocess wrapper.

Always runs in vendor JSON mode:
  gemini -p ... --output-format json --approval-mode ...

Stdout = Gemini's final response text (or, with --pydantic, the validated
JSON object). Stderr = wrapper log + Gemini's two-line warning noise
(Ripgrep / 256-color).

Audit log: _logs/gemini/audit.jsonl (gitignored).

Options:
  --model <name>
        Pin a specific model (free-form). Default = CLI Auto router.
        Use sparingly — model names rot; verify with `/model manage`.
  --pydantic module.path:ClassName
        Inject a JSON schema block into the prompt and validate the answer
        with `cls.model_validate_json()`. On validation fail, retry once
        with a clarifying suffix; second failure → exit 66.
  --repair-mode
        Internal: invoked by Codex repair subagent (server-cap retry=0).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _common import (
    EXIT_ARG_ERROR,
    audit,
    debug_log,
    emit_run_log,
    load_pydantic_class,
    load_prompt_text,
    log,
    require_binary,
    run_cli_with_retry,
    validate_wrapper_cwd,
)


APPROVAL_CHOICES = ("default", "auto_edit")
SANDBOX_CHOICES = ("read-only", "workspace-write")

# Per-call READ-ONLY via the Gemini CLI Policy Engine (--policy) instead of the
# crashy `--approval-mode plan` (plan mode OOMs the Node/V8 heap on heavy files
# — gemini-cli issues #11321 / #18331 / #26588). The policy denies mutation +
# shell tools for THIS call only, so the same leg still does code work under
# `--sandbox workspace-write` (per-call, mirrors codex/agy). The exact policy
# tool identifiers are per the Policy Engine docs but NOT e2e-verified here
# (individual-tier gemini auth is deprecated) — see the policy file header.
_READONLY_POLICY = Path(__file__).resolve().parent / "policies" / "gemini-readonly.toml"


def main() -> int:
    p = argparse.ArgumentParser(description="Gemini CLI single-shot wrapper")
    prompt_group = p.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="User prompt")
    prompt_group.add_argument("--prompt-file", help="Read user prompt from a UTF-8 file")
    p.add_argument(
        "--approval-mode",
        default="default",
        choices=APPROVAL_CHOICES,
        help="Approval mode (default: default — read auto, write/shell prompt)",
    )
    p.add_argument("--cwd", default=None, help="Process working directory")
    p.add_argument("--timeout", type=int, default=600, help="Timeout in seconds")
    p.add_argument(
        "--skip-trust",
        action="store_true",
        help="Skip workspace trust dialog",
    )
    p.add_argument(
        "--sandbox",
        choices=SANDBOX_CHOICES,
        default="read-only",
        help="read-only -> attach a per-call Policy Engine deny (write_file/replace/"
             "run_shell_command) INSTEAD of the crashy plan mode; workspace-write -> "
             "write-enabled (code-agent). Default: read-only.",
    )
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
        help="Internal: invoked by Codex repair subagent (server-cap retry=0)",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        help="Append a human-readable markdown row to "
             "_debug/<UTC-YYYY-MM-DD>/gemini.md (per-call summary)",
    )
    args = p.parse_args()

    try:
        prompt = load_prompt_text(args.prompt, args.prompt_file)
    except Exception as e:
        log(f"prompt load failed: {e}")
        return EXIT_ARG_ERROR

    if not prompt.strip():
        log("empty prompt")
        return EXIT_ARG_ERROR

    try:
        cwd = validate_wrapper_cwd(args.cwd)
    except Exception as e:
        log(f"--cwd validation failed: {e}")
        return EXIT_ARG_ERROR

    if args.sandbox == "read-only" and args.approval_mode == "auto_edit":
        log(f"--sandbox read-only conflicts with --approval-mode {args.approval_mode} "
            "(a write-auto-approving mode). Use --approval-mode default with read-only.")
        return EXIT_ARG_ERROR
    if args.sandbox == "read-only" and not _READONLY_POLICY.is_file():
        log(f"read-only policy file missing: {_READONLY_POLICY}")
        return EXIT_ARG_ERROR

    gemini_bin = require_binary("gemini")

    pydantic_cls = None
    if args.pydantic:
        try:
            pydantic_cls = load_pydantic_class(args.pydantic)
        except Exception as e:
            log(f"--pydantic load failed: {e}")
            return EXIT_ARG_ERROR

    def build_cmd(effective_prompt: str) -> list[str]:
        cmd = [
            gemini_bin,
            "-p", effective_prompt,
            "--approval-mode", args.approval_mode,
            "--output-format", "json",
        ]
        if args.model:
            cmd += ["-m", args.model]
        if args.skip_trust:
            cmd.append("--skip-trust")
        if args.sandbox == "read-only":
            cmd += ["--policy", str(_READONLY_POLICY)]
        return cmd

    result = run_cli_with_retry(
        "gemini",
        build_cmd,
        prompt,
        cwd=cwd,
        timeout=args.timeout,
        pydantic_cls=pydantic_cls,
        last_msg_path=None,
        repair_mode=args.repair_mode,
    )

    audit_cmd = build_cmd(prompt)
    audit("gemini", audit_cmd, prompt, result)

    if args.debug:
        debug_log("gemini", prompt, result)

    # Per-execution run-log (failure only) — dispatch SKILL input artifact.
    run_log_path = emit_run_log("gemini", sys.argv, audit_cmd, prompt, result)
    if run_log_path is not None:
        log(f"run-log: {run_log_path}")

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
