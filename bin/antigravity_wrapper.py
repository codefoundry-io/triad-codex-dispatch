#!/usr/bin/env python3
"""Single-shot Antigravity CLI (agy) wrapper — pty transport + dedicated driver.

agy -p drops stdout on a non-TTY and has no --output-format json, so this
wrapper drives agy through a pty (_pty), scrubs control bytes, checks a
per-call completion sentinel, and classifies via _common pure helpers in a
dedicated extract-then-classify driver (the generic run_cli_with_retry
classifies before extracting, which can't host agy's rc=0 auth-banner case).

Permission behavior is inherited from native AGY configuration. A headless
permission denial is surfaced as a terminal wrapper result without retry.
Audit log: _logs/antigravity/audit.jsonl (gitignored).
"""
from __future__ import annotations

import argparse
import errno
import os
import re
import secrets
import sys
import time
from dataclasses import dataclass
from typing import Optional

import json

import _common
import _pty
from _common import load_pydantic_class, inject_schema_to_prompt, validate_response

OFFSET_S = 10  # agy --print-timeout = max(timeout - OFFSET, MIN); pty kill is backstop
MIN_PRINT_TIMEOUT_S = 5
SERVER_CAP_RETRIES = 2
_PRE_SUBMISSION_EXEC_ERRNOS = frozenset(
    {
        errno.ENOENT,
        errno.EACCES,
        errno.ENOEXEC,
        errno.ETXTBSY,
        errno.ENOTDIR,
        errno.ELOOP,
    }
)


@dataclass
class AgyResult:
    final_answer: Optional[str]
    classification: str
    exit_code: int
    vendor_exit_code: int
    final_argv: list[str]
    schema_repair_attempt: int
    validation_error: Optional[str]
    dispatch_phase: str
    # Raw scrubbed pty transcript is preserved on every return path so the
    # run-log and audit retain complete analyzer evidence.
    scrubbed_output: str = ""
    extraction_error: Optional[str] = None
    validated: Optional[dict] = None


@dataclass
class AgyAttemptState:
    """Latest provider-attempt evidence, including exceptional driver exits."""

    final_argv: list[str]
    schema_repair_attempt: int = 0
    validation_error: Optional[str] = None
    exec_succeeded: bool = False


def _make_sentinel() -> str:
    """Per-INVOCATION identity marker, generated ONCE in main() and held constant
    across the schema-repair re-run (reproducibility comes from reuse, not from
    deriving it from the prompt).

    A random 128-bit id (secrets.token_hex(16)) so two concurrent calls — even
    with an IDENTICAL prompt AND identical cwd — get DISTINCT sentinels, and a
    marker embedded in a reviewed document/log cannot forge a live call's
    identity. Randomness defeats prediction and copy-from-a-past-log; the
    transcript-extractor's structural "the marker is the USER_INPUT footer" check
    (see _common._scan_transcript) defeats copy-from-a-concurrent-live-prompt.
    Format AGY_DONE_<32 lowercase hex>; the extractor + fake-agy match the marker
    length-agnostically."""
    return f"AGY_DONE_{secrets.token_hex(16)}"


def _seal_pydantic_prompt(unsealed_prompt: str, sentinel: str) -> str:
    """Apply AGY's sole whole-response contract to one schema-body prompt."""
    return (
        f"{unsealed_prompt.rstrip()}\n\n"
        "Your complete response must contain exactly two parts:\n"
        "1. One valid JSON object matching the schema requirements above.\n"
        "2. The exact completion marker shown below on the line immediately "
        "after the JSON object's closing brace.\n"
        "The marker is a transport delimiter and is not part of the JSON body. "
        "Output no prose or markdown fences. Nothing may follow the marker.\n"
        f"<<<{sentinel}>>>"
    )


def _build_route_args(model: str | None, effort: str | None) -> list[str]:
    """Build the provider route flags shared by preflight and dispatch."""
    route_args = []
    if model:
        route_args += ["--model", model]
    if effort:
        route_args += ["--effort", effort]
    return route_args


def _build_cmd(prompt, sentinel, model, timeout, *, effort=None, pydantic=False):
    if pydantic:
        sealed = _seal_pydantic_prompt(prompt, sentinel)
    else:
        sealed = (
            f"{prompt}\n\n"
            f"End your final answer with the exact marker <<<{sentinel}>>> "
            f"on its own line."
        )
    print_to = max(timeout - OFFSET_S, MIN_PRINT_TIMEOUT_S)
    cmd = ["agy", "-p", sealed, "--print-timeout", f"{print_to}s"]
    cmd += _build_route_args(model, effort)
    return cmd


def _repair_cmd(cmd, unsealed_prompt, err, sentinel):
    """Rebuild one schema-repair argv from unsealed input and the sole sealer.

    `err` is dynamic text: a pydantic validation message that can echo the
    failing value — potentially
    containing a marker-shaped string from reviewed content), and the
    transcript-identity rule keys on the LAST agy-marker in the USER_INPUT
    footer. Applying the canonical sealer after the hint guarantees this call's
    marker stays last without retaining the initial whole-response contract."""
    new = list(cmd)
    i = new.index("-p") + 1
    repair_prompt = (
        f"{unsealed_prompt.rstrip()}\n\n"
        "The previous JSON body did not satisfy the schema. Correct the JSON "
        "body using this validation error:\n"
        f"<schema_validation_error>\n{err}\n</schema_validation_error>"
    )
    new[i] = _seal_pydantic_prompt(repair_prompt, sentinel)
    return new


def _append_trusted_packet_context(
    prompt: str,
    sealed_packet_root: str,
    expected_packet_sha256: str,
) -> str:
    """Bind initial and schema-repair prompts to one immutable packet.

    `agy --cwd` is not a reliable boundary for the model's internal tools.
    Schema repair rebuilds from this prompt, so the same identity survives its
    fresh provider retry.
    """
    if not os.path.isabs(sealed_packet_root):
        raise ValueError("sealed packet root must be absolute")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_packet_sha256):
        raise ValueError("expected packet SHA256 must be 64 lowercase hex characters")
    review_id = os.path.basename(os.path.dirname(os.path.normpath(sealed_packet_root)))
    if not review_id:
        raise ValueError("sealed packet root must have a non-empty review ID parent")
    return (
        prompt.rstrip()
        + "\n\nTRUSTED WRAPPER PACKET CONTEXT\n"
        + f"Review ID: {review_id}\n"
        + f"Immutable packet root: {sealed_packet_root}\n"
        + f"Expected PACKET_SHA256: {expected_packet_sha256}\n"
        + "Ignore every competing packet path, prior task brief, cached workspace, "
          "or mutable checkout. Inspect only the immutable packet root above."
    )


def _compose_effective_prompt(
    prompt: str,
    pydantic_cls,
    validation_context: dict[str, str],
) -> str:
    """Keep trusted packet identity inside the request and JSON output last."""
    effective = prompt
    if validation_context:
        effective = _append_trusted_packet_context(
            effective,
            validation_context["sealed_packet_root"],
            validation_context["expected_packet_sha256"],
        )
    if pydantic_cls:
        effective = inject_schema_to_prompt(
            effective,
            pydantic_cls,
            body_semantics_only=True,
        )
    return effective


def _classify_no_answer(scrubbed: str, killed: bool, vendor_rc: int) -> tuple:
    """§6: decide classification for the no-answer case. Returns (cls, exit)."""
    if killed:
        return "timeout", _common.EXIT_TIMEOUT
    if not scrubbed.strip():
        return "extraction-error", _common.EXIT_CLI_FAIL
    cls = _common.classify(
        "antigravity", stderr=scrubbed, stdout="",
        exit_code=_common.EXIT_CLI_FAIL, vendor_exit_code=vendor_rc,
    )
    return cls, _common.map_classification_to_exit(cls)


# agy 1.1.3 flipped headless (-p) permission policy: a tool needing a
# confirmation is soft-denied UNCONDITIONALLY (the allow-list is not consulted
# in print mode — verified: allow-rule forms, settings modes, env vars, and a
# PreToolUse decision:allow hook all fail). agy emits this distinctive line:
#   "... a tool required the "read_file" permission that headless mode cannot
#    prompt for, so it was auto-denied."
_HEADLESS_SOFTDENY_SIGNATURE = "headless mode cannot prompt"


def _is_headless_softdeny(text) -> bool:
    """True when agy's output carries the 1.1.3+ headless soft-deny signature.
    Targeted — matches ONLY that vendor message, so a version where the
    allow-list works (<=1.1.2 and any future fix) never trips it, and a plain
    empty/extraction failure is untouched."""
    return _HEADLESS_SOFTDENY_SIGNATURE in (text or "").lower()


_TRUNCATED_ANSWER_RE = re.compile(
    r"^[ \t]*<truncated [0-9]+ (?:bytes|lines)>[ \t]*$",
    re.MULTILINE,
)


def _has_truncated_answer_marker(answer) -> bool:
    """True only for agy's own-line lossy-output marker."""
    return bool(_TRUNCATED_ANSWER_RE.search(answer or ""))


def _run_agy_with_retry(cmd, unsealed_prompt, timeout, *, expected_sentinel,
                        cwd=None, repair_mode=False, pydantic_cls=None,
                        validation_context=None,
                        attempt_state=None) -> AgyResult:
    """Dedicated driver (design §6): pty-run -> scrub -> extract -> classify
    with a bounded server-capacity retry (cap SERVER_CAP_RETRIES).

    Decision table (extract-then-classify so a rc=0 auth banner the model
    quotes inside a real answer never mis-classifies; ORDER MATTERS):
      - killed          -> ("timeout", EXIT_TIMEOUT)   [FIRST — P4 round 2:
                            a killed run has no complete DONE record, so any
                            pty "answer" is partial, and its rc=128+signal
                            would otherwise hit the rc gate and mislabel a
                            retriable timeout as terminal vendor-error]
      - answer present + non-empty, vendor rc==0, no truncation marker
                         -> ("ok", EXIT_OK)          [classify NOT called]
      - answer present + non-empty, vendor rc!=0 -> ("vendor-error",
                            EXIT_TERMINAL)   [P4 rc gate — never a silent ok,
                            never via classify; answer quarantined from stdout,
                            bounded copy in extraction_error -> run-log]
      - answer present + own-line truncation marker, rc=0
                         -> ("truncated-answer", EXIT_TERMINAL)
                            [direct driver gate — quarantined, never schema repair]
      - sentinel found, body empty -> ("extraction-error", EXIT_CLI_FAIL)
                                       [direct — NOT via classify, whose blob
                                        still holds the marker and would
                                        misroute an empty answer to unknown]
      - clean + empty   -> ("extraction-error", EXIT_CLI_FAIL)
      - else            -> classify(antigravity, scrubbed) -> mapped exit;
                            server-capacity retries the whole pty run.

    Two INDEPENDENT retry budgets (F-Q2): `server_attempt` governs the
    server-capacity retry (cap SERVER_CAP_RETRIES), while
    `schema_repair_attempt` counts the single schema-repair re-run. They are
    decoupled — a transient server-capacity blip never consumes the lone
    schema-repair slot, and a schema repair never reduces the server-cap
    budget. The schema-repair re-run fires exactly once regardless of
    `repair_mode` (schema validity is orthogonal to the classifier re-run
    that `repair_mode` governs).

    `repair_mode` is a compatibility flag for an explicit single-attempt
    diagnostic invocation: it disables the server-capacity retry. The current
    read-only analyzer never invokes provider wrappers. `cwd` is a normal kwarg
    (defaults None), with no instance state. The scrubbed transcript is carried
    on every return path so the failure run-log retains the literal evidence.
    """
    max_retries = 0 if repair_mode else SERVER_CAP_RETRIES
    server_attempt = 0       # server-capacity retry budget (independent)
    state = attempt_state or AgyAttemptState(final_argv=list(cmd))
    def finish(
        final_answer,
        classification,
        exit_code,
        vendor_exit_code,
        *,
        scrubbed_output="",
        extraction_error=None,
        validated=None,
    ) -> AgyResult:
        """Capture the exact argv and schema state at every driver exit."""
        return AgyResult(
            final_answer,
            classification,
            exit_code,
            vendor_exit_code,
            final_argv=list(state.final_argv),
            schema_repair_attempt=state.schema_repair_attempt,
            validation_error=state.validation_error,
            dispatch_phase="post-dispatch-result",
            scrubbed_output=scrubbed_output,
            extraction_error=extraction_error,
            validated=validated,
        )

    while True:
        # P4.5 transcript-read transport (spike-verified 2026-07-05): snapshot
        # agy's per-conversation transcript store BEFORE the run so the new
        # conversation (this call's) is identifiable afterward.
        _brain_before = _common.snapshot_agy_transcripts()
        # Record immediately before the PTY call so every exceptional transport
        # outcome retains the exact argv that was attempted.
        state.final_argv = list(cmd)
        # env=None => _pty inherits the SCRUBBED child env (loader/interpreter
        # injection vars dropped via _common.scrubbed_child_env, I-2/I-3) — the
        # agy-transport equivalent of _run_once's Popen env= scrub.
        result = _pty.run_via_pty(cmd, cwd=cwd, timeout=timeout, env=None)
        state.exec_succeeded = True
        scrubbed = _common.scrub_agy_output(result.output_bytes)
        if result.killed:
            # Killed short-circuit (P4 review round 2, 3-family convergent):
            # a killed run has no complete DONE record — that is exactly why
            # transcript-read is skipped for it — so any pty-scrub "answer"
            # (e.g. an early-echoed marker) is partial and unreliable, and a
            # kill reaps rc=128+signal, which would otherwise fall into the
            # rc gate and mislabel a retriable timeout as terminal
            # vendor-error. The scrubbed partial output still reaches the
            # run-log for inspection.
            return finish(None, "timeout", _common.EXIT_TIMEOUT,
                          result.rc, scrubbed_output=scrubbed)
        # PRIMARY: read the complete answer from agy's own transcript.jsonl
        # (the identity anchor is the USER_INPUT footer, so a long answer that
        # drops the trailing marker is still recovered). FALLBACK to
        # pty-scrub+sentinel.
        answer = _common.extract_agy_answer_from_transcript(
            None, _brain_before, sentinel=expected_sentinel)
        ext_err = None
        if answer is None:
            answer, ext_err = _common.extract_antigravity_answer(
                scrubbed, result.killed, expected_sentinel)
        if answer is not None and answer.strip():
            if result.rc != 0:
                # rc gate (P4). success => rc=0 (agy audit: 36/36 ok at rc=0).
                # A non-empty answer at a FAILING vendor rc is NOT a silent ok,
                # and is NOT fed to classify (a real answer can quote error-shaped
                # tokens -> a spurious server-capacity re-run / oauth-env terminal
                # that discards a valid answer). A DISTINCT token routed to
                # surface-not-repair: reusing `extraction-error` would MANDATE a
                # repair-routed classification and violate its documented
                # "rc=0, no answer" invariant. The answer is
                # QUARANTINED from stdout (final_answer=None, like every other
                # failure); a bounded copy rides in extraction_error so the
                # RUN-LOG genuinely carries it even when it was recovered from
                # the transcript (not the pty output) — review round-2 fix.
                snippet = answer if len(answer) <= 2000 else answer[:2000] + " …[truncated]"
                return finish(None, "vendor-error", _common.EXIT_TERMINAL,
                              result.rc, scrubbed_output=scrubbed,
                              extraction_error=(
                                  f"vendor rc={result.rc} returned a non-empty "
                                  f"answer; surfaced as vendor-error (not ok, "
                                  f"not repair). quarantined answer: {snippet}"))
            if _has_truncated_answer_marker(answer):
                snippet = answer if len(answer) <= 2000 else answer[:2000] + " …[truncated]"
                return finish(
                    None,
                    "truncated-answer",
                    _common.EXIT_TERMINAL,
                    result.rc,
                    scrubbed_output=scrubbed,
                    extraction_error=(
                        "vendor rc=0 returned an answer containing an own-line "
                        "truncation marker; surfaced as truncated-answer (not ok, "
                        f"not repair). quarantined answer: {snippet}"
                    ),
                )
            if pydantic_cls is None:
                return finish(answer, "ok", _common.EXIT_OK, result.rc,
                              scrubbed_output=scrubbed)
            ok, payload = validate_response(
                answer, pydantic_cls, context=validation_context
            )
            if ok:
                return finish(answer, "ok", _common.EXIT_OK, result.rc,
                              scrubbed_output=scrubbed, validated=payload)
            state.validation_error = str(payload)
            if state.schema_repair_attempt == 0 and not validation_context:
                # Ordinary schemas retain exactly one schema-repair re-run.
                cmd = _repair_cmd(
                    cmd,
                    unsealed_prompt,
                    state.validation_error,
                    expected_sentinel,
                )
                state.schema_repair_attempt += 1
                continue
            return finish(answer, "schema-fail", _common.EXIT_SCHEMA_FAIL,
                          result.rc, scrubbed_output=scrubbed,
                          extraction_error=f"schema: {payload}")
        if answer is not None:
            # Sentinel present but the answer body is empty — a real
            # extraction failure, NOT a silent empty ok. Do not fall through
            # to classify (the scrubbed blob still carries the marker).
            return finish(None, "extraction-error", _common.EXIT_CLI_FAIL,
                          result.rc, scrubbed_output=scrubbed,
                          extraction_error="empty-answer-body")
        if _is_headless_softdeny(scrubbed):
            return finish(
                None,
                "permission-unavailable",
                _common.EXIT_TERMINAL,
                result.rc,
                scrubbed_output=scrubbed,
                extraction_error="native headless permission unavailable",
            )
        cls, code = _classify_no_answer(scrubbed, result.killed, result.rc)
        if cls == "server-capacity" and server_attempt < max_retries:
            _server_cap_backoff(server_attempt)
            server_attempt += 1
            continue
        return finish(None, cls, code, result.rc, scrubbed_output=scrubbed,
                      extraction_error=ext_err)


def _server_cap_backoff(attempt: int) -> None:
    """Politeness sleep before a server-capacity retry. Suppressible
    via AGY_NO_BACKOFF=1 so unit/integration tests don't sleep 15s+."""
    if os.environ.get("AGY_NO_BACKOFF") == "1":
        return
    idx = min(attempt, len(_common.SERVER_CAP_BACKOFF_S) - 1)
    time.sleep(_common.SERVER_CAP_BACKOFF_S[idx])


def main() -> int:
    p = argparse.ArgumentParser(description="Antigravity (agy) single-shot wrapper",
                                allow_abbrev=False)
    prompt_group = p.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="User prompt")
    prompt_group.add_argument(
        "--prompt-file",
        help="Read the user prompt from a UTF-8 file (L12; containment applies "
             "under TRIAD_WRAPPER_ALLOWED_ROOTS)")
    p.add_argument("--cwd", default=None)
    p.add_argument("--model", default=None)
    p.add_argument("--effort", choices=["low", "medium", "high"], default=None)
    p.add_argument("--timeout", type=int, default=600)
    p.add_argument("--repair-mode", action="store_true")
    p.add_argument("--debug", action="store_true")
    p.add_argument(
        "--preflight-only",
        action="store_true",
        help="validate exact route arguments without provider inference",
    )
    p.add_argument("--pydantic", default=None,
                   help="pydantic class spec (module:Class) — prompt-instructed "
                        "JSON + validate (agy has no native schema)")
    p.add_argument("--sealed-packet-root", default=None)
    p.add_argument("--expected-packet-sha256", default=None)
    # NOTE: --dangerously-* are intentionally NOT defined -> argparse rejects
    # them (danger flags are banned).
    args = p.parse_args()

    try:
        _prompt_text = _common.load_prompt_text(args.prompt, args.prompt_file)
    except Exception as e:
        _common.log(f"prompt load failed: {e}")
        return _common.EXIT_ARG_ERROR
    args.prompt = _prompt_text  # downstream code keeps using args.prompt

    try:
        args.cwd = _common.validate_wrapper_cwd(args.cwd)
    except Exception as e:
        _common.log(f"--cwd validation failed: {e}")
        return _common.EXIT_ARG_ERROR

    if not args.prompt.strip():
        _common.log("empty prompt")
        return _common.EXIT_ARG_ERROR

    # agy owns its dedicated driver, so perform the same best-effort normal
    # dispatch cleanup here before preflight or provider work.
    if not args.repair_mode:
        _common.prune_stale_run_logs("antigravity")

    pydantic_cls = None
    if args.pydantic:
        try:
            pydantic_cls = load_pydantic_class(args.pydantic)
        except Exception as e:
            _common.log(f"--pydantic load failed: {e}")
            return _common.EXIT_ARG_ERROR

    try:
        validation_context = _common.build_validation_context(
            pydantic_cls,
            args.sealed_packet_root,
            args.expected_packet_sha256,
        ) or {}
    except Exception as e:
        _common.log(f"sealed validation context failed: {e}")
        return _common.EXIT_ARG_ERROR

    if args.preflight_only:
        route_args = _build_route_args(args.model, args.effort)
        receipt = {
            "provider_started": False,
            "dispatch_phase": "preflight",
            "model": args.model,
            "effort": args.effort,
            "pydantic": args.pydantic,
            "sealed_packet_root": validation_context.get("sealed_packet_root"),
            "expected_packet_sha256": validation_context.get(
                "expected_packet_sha256"
            ),
            "route_args": route_args,
            "timeout": args.timeout,
        }
        sys.stdout.write(json.dumps(receipt, ensure_ascii=False) + "\n")
        return _common.EXIT_OK

    agy_bin = _common.require_binary("agy")

    sentinel = _make_sentinel()
    eff_prompt = _compose_effective_prompt(
        args.prompt,
        pydantic_cls,
        validation_context,
    )
    cmd = _build_cmd(
        eff_prompt,
        sentinel,
        args.model,
        args.timeout,
        effort=args.effort,
        pydantic=pydantic_cls is not None,
    )
    # argv[0] = resolved/pinned agy path (finding #3). _build_cmd stays pure ("agy"
    # literal) so its unit test is unaffected; the pin is substituted here at the
    # run site so a PATH shadow cannot win when the pty execs argv[0].
    cmd[0] = agy_bin
    attempt_state = AgyAttemptState(final_argv=list(cmd))

    start = time.monotonic()
    dispatch_phase = "post-dispatch-result"
    try:
        r = _run_agy_with_retry(
            cmd,
            eff_prompt,
            args.timeout,
            expected_sentinel=sentinel,
            cwd=args.cwd,
            repair_mode=args.repair_mode,
            pydantic_cls=pydantic_cls,
            validation_context=validation_context or None,
            attempt_state=attempt_state,
        )
        dispatch_phase = r.dispatch_phase
    except (
        _pty.PtyStartError,
        TimeoutError,
        json.JSONDecodeError,
        ValueError,
        OSError,
    ) as e:
        if (
            isinstance(e, _pty.PtyStartError)
            and not attempt_state.exec_succeeded
            and e.stage == "exec"
            and e.errno in _PRE_SUBMISSION_EXEC_ERRNOS
        ):
            _common.log(
                "agy start failed before request submission: "
                f"stage={e.stage} errno={e.errno}"
            )
            return _common.EXIT_BINARY_MISSING
        # Driver/config failures without genuine first-attempt exec-route
        # evidence retain their exact attempted argv and schema state on the
        # terminal config-conflict path rather than escaping as tracebacks.
        extraction_error = f"agy driver/config conflict: {e}"
        _common.log(extraction_error)
        r = AgyResult(
            None,
            "config-conflict",
            _common.EXIT_TERMINAL,
            -1,
            final_argv=list(attempt_state.final_argv),
            schema_repair_attempt=attempt_state.schema_repair_attempt,
            validation_error=attempt_state.validation_error,
            dispatch_phase=dispatch_phase,
            scrubbed_output="",
            extraction_error=extraction_error,
            validated=None,
        )
    elapsed = time.monotonic() - start

    # Build a RunResult for the shared audit / run-log / debug helpers.
    # Convention (matches the generic run_cli_with_retry): RunResult.stdout =
    # the RAW vendor transcript (here the scrubbed pty output), final_answer =
    # the extracted answer (or ""). emit_run_log writes result.stdout, so the
    # failure run-log carries the literal transcript for the read-only analyzer
    # instead of an empty string on unknown/oauth-env/extraction-error.
    rr = _common.RunResult(
        exit_code=r.exit_code,
        stdout=r.scrubbed_output,
        stderr="",
        elapsed_s=elapsed,
        classification=r.classification,
        mode=(
            "schema_repair" if r.schema_repair_attempt
            else "repair" if args.repair_mode else "normal"
        ),
        final_answer=r.final_answer or "",
        validated=r.validated,
        schema_repair_attempt=r.schema_repair_attempt,
        extraction_error=r.extraction_error,
        validation_error=r.validation_error,
        vendor_exit_code=r.vendor_exit_code,
        dispatch_phase=r.dispatch_phase,
    )

    # Canonical 1-line summary — preserve the _run_once prefix and append the
    # authoritative dispatch phase used by fallback routing.
    _common.log(
        f"[wrapper] antigravity {r.classification} "
        f"exit={r.exit_code} vendor={r.vendor_exit_code} "
        f"elapsed={elapsed:.1f}s phase={r.dispatch_phase}"
    )

    _common.persist_result_artifacts(
        "antigravity", sys.argv, r.final_argv, args.prompt, rr, debug=args.debug
    )

    if r.exit_code == _common.EXIT_OK and r.validated is not None:
        sys.stdout.write(json.dumps(r.validated, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(r.final_answer or "")
        if r.final_answer and not r.final_answer.endswith("\n"):
            sys.stdout.write("\n")
    sys.stdout.flush()
    return r.exit_code


if __name__ == "__main__":
    sys.exit(main())
