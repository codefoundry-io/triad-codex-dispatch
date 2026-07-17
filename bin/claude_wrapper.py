#!/usr/bin/env python3
"""Single-shot Claude CLI subprocess wrapper.

Always runs in vendor JSON mode:
  claude -p "<prompt>" --output-format json

Stdout = the final answer text from envelope `.result` field (or, with
`--pydantic`, the validated JSON object). Stderr = wrapper log + Claude's
brief progress noise (pre-bootstrap settings/plugin lines).

Audit log: _logs/claude/audit.jsonl (gitignored).

ISOLATION CONTRACT (caller responsibility — wrapper is transport-only):
  Claude worker 의 본 본질 = leader (claude main session) 와 분리된 별
  instance, objective 시각 의무 (CLAUDE.md / project context / leader
  frame 부담 X). 본 isolation 은 caller 가 sibling dir setup 으로 보장:

    1. 사용자 가 sibling dir (e.g. `~/triad-claude-worker/`) 안 1회 cd
    2. `claude` 1회 실행 → OAuth 로그인 (subscription path 정합)
    3. caller (triad-claude-dispatch SKILL) 가 wrapper 호출 시
       `--cwd <sibling-dir>` 명시

  본 dir 안 `CLAUDE.md` 부재 = leader frame 차단 자동. wrapper 안 추가
  isolation flag (--mcp-config / --strict-mcp-config / --setting-sources
  / --no-session-persistence / --exclude-dynamic-system-prompt-sections)
  박지 X — sibling dir 의 본 settings 가 의무.

Options:
  --effort {low,medium,high,xhigh,max}
        Override `--effort` (claude 의 본 reasoning level).
        Default = vendor default. Read-only deep work → high.
  --fallback-model <name>
        Auto-fallback when default model overloaded.
  --permission-mode {default,acceptEdits,auto,bypassPermissions,dontAsk,plan}
        Permission mode override. `bypassPermissions` 박지 X (Triad safety).
  --pydantic module.path:ClassName
        Inject a JSON schema block into the prompt and validate the answer
        with `cls.model_validate_json()`. On validation fail, retry once
        with a clarifying suffix; second failure → exit 66.
  --repair-mode
        Internal: invoked by Sonnet repair sub-agent (server-cap retry=0).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from _common import (
    validate_wrapper_cwd,
    load_prompt_text,
    EXIT_ARG_ERROR,
    audit,
    debug_log,
    emit_run_log,
    load_pydantic_class,
    log,
    require_binary,
    run_cli_with_retry,
)


EFFORT_CHOICES = ("low", "medium", "high", "xhigh", "max")
PERMISSION_CHOICES = (
    "default",
    "acceptEdits",
    "auto",
    "bypassPermissions",
    "dontAsk",
    "plan",
)
PERMISSION_FORBIDDEN = ("bypassPermissions",)


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
        help="Process working directory (caller 의무 — sibling dir for isolation)",
    )
    p.add_argument("--timeout", type=int, default=600, help="Timeout in seconds")
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
        "--sandbox",
        choices=("read-only", "workspace-write"),
        default=None,
        help="Wrapper-ENFORCED worker posture (L13 mode-switch, owner adjudication "
             "#3 2026-07-05). read-only -> --tools Read,Glob,Grep (a real "
             "restriction — --allowedTools only PRE-APPROVES) + --strict-mcp-config "
             "+ --setting-sources user + dontAsk; workspace-write -> acceptEdits + "
             "REQUIRES --cwd (rm/rmdir/sed are auto-approved in acceptEdits — "
             "blast radius must be an isolated dir) + --strict-mcp-config. "
             "Mutually exclusive with --permission-mode. Lab default = omitted "
             "(transport-only; the CALLER owns isolation per the SKILL contract); "
             "TRIAD_CLAUDE_ENFORCE_SANDBOX=1 (public codex-host bootstrap) makes "
             "--sandbox REQUIRED.")
    p.add_argument(
        "--permission-mode",
        default=None,
        choices=PERMISSION_CHOICES,
        help="Permission mode override",
    )
    p.add_argument(
        "--pydantic",
        default=None,
        help="pydantic class spec (module.path:ClassName) for schema enforcement",
    )
    p.add_argument(
        "--repair-mode",
        action="store_true",
        help="Internal: invoked by Sonnet repair sub-agent (server-cap retry=0)",
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

    if args.sandbox and args.permission_mode:
        log("--sandbox and --permission-mode are mutually exclusive "
            "(--sandbox synthesizes the permission posture)")
        return EXIT_ARG_ERROR
    if os.environ.get("TRIAD_CLAUDE_ENFORCE_SANDBOX") == "1" and not args.sandbox:
        log("TRIAD_CLAUDE_ENFORCE_SANDBOX=1: --sandbox read-only|workspace-write "
            "is required (raw transport-only dispatch is disabled on this install)")
        return EXIT_ARG_ERROR
    if args.sandbox == "workspace-write" and not args.cwd:
        log("--sandbox workspace-write requires --cwd (acceptEdits auto-approves "
            "rm/rmdir/sed — the blast radius must be an isolated directory)")
        return EXIT_ARG_ERROR

    if not args.prompt.strip():
        log("empty prompt")
        return EXIT_ARG_ERROR

    if args.permission_mode in PERMISSION_FORBIDDEN:
        log(f"--permission-mode {args.permission_mode} forbidden by Triad safety")
        return EXIT_ARG_ERROR

    claude_bin = require_binary("claude")

    pydantic_cls = None
    if args.pydantic:
        try:
            pydantic_cls = load_pydantic_class(args.pydantic)
        except Exception as e:
            log(f"--pydantic load failed: {e}")
            return EXIT_ARG_ERROR

    def build_cmd(effective_prompt: str) -> list[str]:
        cmd = [
            claude_bin,   # resolved/pinned path (finding #3) — never a bare name
            "-p", effective_prompt,
            "--output-format", "json",
        ]
        if args.effort:
            cmd += ["--effort", args.effort]
        if args.fallback_model:
            cmd += ["--fallback-model", args.fallback_model]
        if args.permission_mode:
            cmd += ["--permission-mode", args.permission_mode]
        if args.sandbox == "read-only":
            # --tools RESTRICTS (vs --allowedTools which only pre-approves);
            # strict-mcp-config blocks settings-inherited MCP servers;
            # --setting-sources user drops project hooks/CLAUDE.md (a
            # dispatched-into repo must not execute hooks on a read leg).
            cmd += ["--tools", "Read,Glob,Grep",
                    "--strict-mcp-config",
                    "--setting-sources", "user",
                    "--permission-mode", "dontAsk"]
        elif args.sandbox == "workspace-write":
            cmd += ["--strict-mcp-config",
                    "--permission-mode", "acceptEdits"]
        return cmd

    result = run_cli_with_retry(
        "claude",
        build_cmd,
        args.prompt,
        cwd=args.cwd,
        timeout=args.timeout,
        pydantic_cls=pydantic_cls,
        last_msg_path=None,
        repair_mode=args.repair_mode,
    )

    audit_cmd = build_cmd(args.prompt)
    audit("claude", audit_cmd, args.prompt, result)

    if args.debug:
        debug_log("claude", args.prompt, result)

    # Per-execution run-log (failure only) — dispatch SKILL input artifact.
    run_log_path = emit_run_log("claude", sys.argv, audit_cmd, args.prompt, result)
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
