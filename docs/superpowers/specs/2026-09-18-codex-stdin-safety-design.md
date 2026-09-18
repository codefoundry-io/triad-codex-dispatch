# Codex-host TRIAD stdin safety design

## Authority and scope

The owner approved proceeding after the S3 safety briefing. This design applies only to `/Users/chaniri/codex_workspace/workspace/triad-codex-dispatch-reliability`, branch `codex/triad-adoption-stdin-safety`, based on `05ca5443bece2337925e6431214981c8dc1b92b7`. The existing dirty `AGENTS.md` is protected (recorded SHA-256 `b7fc91cc9c2003984300c2e2f921e98956dbb89287e725ca208f5156db8568ee`). Preserve all unrelated changes. Claude-host `codefoundry-io/triad-dispatch`, upstream checkouts, reference copies, and frozen snapshots remain read-only; the upstream handoff was already delivered.

Evidence: `/Users/chaniri/codex_workspace/_runs/infra/20260918-triad-s3-stdin-safety-TkGVT5/{briefing.md,results.json,probe.py}`. Implementation records belong under `/Users/chaniri/codex_workspace/_runs/infra/20260918-triad-s3-implementation-gnccFU`. The 828-test baseline already passed; do not rerun it before adding causal RED tests.

## Confirmed problem

`bin/_common.py:_run_once` swallows write/flush/close exceptions and never reconciles its daemon writer. A real child consuming only one of 1,518,000 bytes, closing stdin, printing plausible success, and exiting zero is accepted. An invalid Unicode surrogate similarly becomes empty-input success. Valid large UTF-8 and concurrent output already work in the synthetic probe; preserve that behavior. The current Claude wrapper still places the full prompt in its child argv, even when the caller supplies `--prompt-file`.

## Two separate merge-gate units

| Unit | Single behavioral claim | Production delta forecast | Novel core |
| --- | --- | --- | --- |
| A | Failed or incomplete stdin delivery cannot become accepted success or induce retries, while actual vendor failures and cancellation retain precedence. | 65–105 net lines | 45–75 lines |
| B | Local external Claude receives the effective prompt as UTF-8 text stdin, with unchanged output, binding, settings, and call-count contracts. | 8–18 net lines | under 10 lines |

Total forecast is below 150 net production lines. Tests/docs are separate from that production budget. No new framework, broad refactor, provider expansion, version bump, changelog rewrite, skill change, migration change, installation, or release belongs here. A can ship with Claude still using argv. B depends on reviewed A and receives its own review decision. Root commits the plan/spec first; implementers commit only their owned changes after RED/GREEN and self-review, then root supplies independent review packages. This workflow performs no formal admission; final merge requires explicit owner approval.

## A: transport contract

Keep `_run_once`'s existing signature and `RunResult`'s public artifact schemas. Add one private defaulted `RunResult._stdin_delivery_failed: bool = False`. Audit and failure records in `_common.audit` and `_common.write_run_log` explicitly enumerate fields; they do not serialize the dataclass wholesale. The private flag therefore does not expand those schemas. Human evidence uses the existing `extraction_error` field with a fixed prompt-free diagnostic, and the existing `unknown` classification/`EXIT_CLI_FAIL` failure route. No classifier token, exit code, or `LegVerdict` field is added.

When stdin is present, strictly encode UTF-8 before spawning. An encoding failure returns the private transport failure with raw vendor rc `-1` (no provider existed), without sending a billed empty request. The writer writes those bytes to `proc.stdin.buffer`. This retains current stdout/stderr text-reader behavior and avoids locale encoding and newline translation of stdin (including CRLF). Require a full byte-count return, successful flush, and successful close. The writer alone closes stdin; the parent must never close its buffered stream while another thread may hold its lock. An event publishes completion after the close attempt; record only stable phase names (`write`, `close`, `incomplete`), never exception strings or input bytes.

After child wait/termination, join the writer with a two-second bound. If incomplete, invoke the existing saved process-group termination helper and join for at most two further seconds. This reuses S1 cleanup, including surviving descendants after direct-child exit. No unbounded join is permitted. A process escaping that saved group is not newly claimed to be contained; a still-incomplete writer is a failure, even after bounded cleanup. Keep output drainers concurrent. The existing main-thread `BaseException` handler still terminates/reaps the provider, bounded-joins output and stdin workers, and re-raises the identical exception.

| State after bounded reconciliation | Result |
| --- | --- |
| Wrapper timeout | `EXIT_TIMEOUT`; never parse output into retry or success |
| Main-thread `BaseException` | Existing cleanup; re-raise same exception |
| Vendor nonzero, writer failed or complete | Existing vendor classification/extraction/retry rules; retain raw rc; do not replace rejection with BrokenPipe |
| Vendor zero, writer failed/incomplete | `EXIT_CLI_FAIL`, `unknown`, private flag true, fixed `extraction_error`, empty final answer/validated value; no extraction or retry |
| Vendor zero, writer complete | Existing extraction/schema route |
| No stdin requested | Existing DEVNULL behavior; no writer or new classification |

In `run_cli_with_retry`, gate the private flag and, only when `prompt_via_stdin=True`, wrapper timeout after attempt/mode fields are assigned, before Claude extraction and retry classification. A adds optional keyword-only `stdin_text: str | None = None` to `_run_native_structured_once`, passed to `_run_once` only when present. Gate private failure and, only when stdin is supplied, timeout before extraction/JSON/schema validation; emit the normal wrapper summary and return. Do not globally change `classify`; the private state is authoritative for this local transport failure and raw vendor output cannot override it. For `classify_and_log=False`, transport failure still has classification `unknown`; ordinary successful native invocations retain `unclassified` until their existing validation path. These timeout gates do not change existing non-stdin consumers.

## B: Claude text stdin contract

Retain `build_cmd(effective_prompt, native_schema=None)` because `run_cli_with_retry` uses that callback shape. Stop adding `effective_prompt` after `-p`; use `-p --input-format text --output-format json`, preserving all current model, effort, fallback, formal permission, and native JSON-schema options. Pass `prompt_via_stdin=True` to the ordinary driver. Call A's native helper with `stdin_text=args.prompt`. Its optional default preserves internal callers/tests; main always supplies the prompt after B.

The outer `--prompt-file` interface and loader remain unchanged. Transport exactness means exact UTF-8 encoding of the loaded/effective Python string; it does not claim to reverse existing prompt-file newline normalization. Formal ID/family/digest binding, `opus`, `xhigh`, 1,200-second timeout, `--permission-mode plan`, no fallback, and one native provider call remain unchanged. Gemini and AGY transport are untouched.

[Claude headless documentation](https://code.claude.com/docs/en/headless#pipe-data-through-claude) documents text stdin and a 10MB cap, enforced by the vendor with nonzero exit. [CLI reference](https://code.claude.com/docs/en/cli-reference) distinguishes text from stream-json input and documents JSON/schema output. Do not guess a numeric byte constant from “10MB,” pre-truncate, chunk, or add calls. Preserve actual vendor size rejection; model context/token limits also remain. Synthetic tests prove the wrapper boundary, not arbitrary vendor/model consumption.

Update current operational text in README.md, README.ko.md, and SECURITY.md: stdin removes the prompt from the inner provider argv; callers still need `--prompt-file` to keep it out of the outer wrapper argv. Existing argv lists already prevent shell expansion. Stdin does not encrypt input, prevent prompt injection, reduce token use, or remove sensitive prompt/transcript logging. Preserve historical changelog/release content.

## Acceptance evidence

Real synthetic subprocesses cover large UTF-8 with Korean/emoji/CRLF/metacharacters, simultaneous output backpressure, EOF, early close with success-shaped output, invalid encoding, nonreading timeout, genuine vendor rejection and retry, and no-stdin callers. Private writer-phase fixtures cover write/flush/close and incomplete completion without leaking diagnostic contents. Ordinary and native/formal consumers must reject success-shaped output after failed delivery, without extra calls. Existing S1 timeout/interrupt/descendant cleanup tests remain required. New fixtures own and independently reap only their own children with bounded waits; no real providers or dependency/global configuration changes are needed.
