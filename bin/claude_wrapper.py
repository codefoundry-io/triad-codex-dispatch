#!/usr/bin/env python3
"""Single-shot Claude Code (`claude -p`) subprocess wrapper. Mirrors gemini_wrapper.py."""
from __future__ import annotations
import argparse, json, sys
from _common import (EXIT_ARG_ERROR, audit, debug_log, emit_run_log,
                     load_pydantic_class, load_prompt_text, log, require_binary,
                     run_cli_with_retry, validate_wrapper_cwd)

SANDBOX_CHOICES = ("read-only", "workspace-write")   # bypassPermissions banned (no-yolo)
REASONING_CHOICES = ("low", "medium", "high", "xhigh")
READONLY_TOOLS = "Read,Glob,Grep"

def main() -> int:
    p = argparse.ArgumentParser(description="Claude Code single-shot wrapper")
    prompt_group = p.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt")
    prompt_group.add_argument("--prompt-file")
    p.add_argument("--sandbox", default="read-only", choices=SANDBOX_CHOICES)
    p.add_argument("--search", action="store_true", help="Enable WebSearch/WebFetch")
    p.add_argument("--model", default=None, help="Model alias (opus/sonnet/haiku/fable)")
    p.add_argument("--reasoning", default=None, choices=REASONING_CHOICES)
    p.add_argument("--pydantic", default=None)
    p.add_argument("--cwd", default=None)
    p.add_argument("--timeout", type=int, default=600)
    p.add_argument("--repair-mode", action="store_true")
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()

    try:
        prompt = load_prompt_text(args.prompt, args.prompt_file)
    except Exception as e:
        log(f"prompt load failed: {e}")
        return EXIT_ARG_ERROR

    if not prompt.strip():
        log("empty prompt"); return EXIT_ARG_ERROR

    try:
        cwd = validate_wrapper_cwd(args.cwd)
    except Exception as e:
        log(f"--cwd validation failed: {e}")
        return EXIT_ARG_ERROR

    claude_bin = require_binary("claude")

    pydantic_cls = None
    if args.pydantic:
        try:
            pydantic_cls = load_pydantic_class(args.pydantic)
        except Exception as e:
            log(f"--pydantic load failed: {e}"); return EXIT_ARG_ERROR

    def build_cmd(effective_prompt: str) -> list[str]:
        tools = READONLY_TOOLS + (",WebSearch,WebFetch" if args.search else "")
        perm = "dontAsk" if args.sandbox == "read-only" else "acceptEdits"
        cmd = [claude_bin, "-p", effective_prompt,
               "--output-format", "json", "--no-session-persistence",
               "--permission-mode", perm]
        if args.sandbox == "read-only":
            cmd += ["--allowedTools", tools]
        elif args.search:
            cmd += ["--allowedTools", "WebSearch,WebFetch"]
        if args.model:
            cmd += ["--model", args.model]
        if args.reasoning:
            cmd += ["--effort", args.reasoning]
        if pydantic_cls is not None:
            from _common import pydantic_to_codex_schema
            cmd += ["--json-schema", json.dumps(pydantic_to_codex_schema(pydantic_cls))]
        return cmd

    result = run_cli_with_retry("claude", build_cmd, prompt,
                                cwd=cwd, timeout=args.timeout,
                                pydantic_cls=pydantic_cls, last_msg_path=None,
                                repair_mode=args.repair_mode)

    audit_cmd = build_cmd(prompt)
    audit("claude", audit_cmd, prompt, result)
    if args.debug:
        debug_log("claude", prompt, result)
    run_log_path = emit_run_log("claude", sys.argv, audit_cmd, prompt, result)
    if run_log_path is not None:
        log(f"run-log: {run_log_path}")

    if pydantic_cls and result.validated is not None:
        sys.stdout.write(json.dumps(result.validated, ensure_ascii=False) + "\n")
    else:
        ans = result.final_answer or ""
        sys.stdout.write(ans + ("\n" if ans and not ans.endswith("\n") else ""))
    sys.stdout.flush()
    return result.exit_code

if __name__ == "__main__":
    sys.exit(main())
