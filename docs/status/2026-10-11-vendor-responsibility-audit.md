# Vendor responsibility and TRIAD scope audit

Owner direction,2026-10-11: audit all features from the premise that vendor
CLIs already manage their execution and handles. Stop expanding pending work
merely to satisfy an over-specified contract.

## Basis and method

B: `b6868d8036ebe7fd55d975b896f587c8adb18300`; read-only A:
`1de943af4436b3eca2aea903d05c223c8d56f92d`; shared draft `c66e515`.
Remote main freshly fetched: `3afc4d7e931e55d601dd74877bdbe65e610a8e59`.
PR13 has no newer A reply after the recorded exchange through6100271567.
Local version-only commands observed Claude2.1.289, AGY1.3.3, Gemini0.60.0.
Gemini is below the project's0.63.0 floor; it was not used for live inference.
Current online docs can describe a newer release than an installed executable.

This is a static feature/responsibility audit of shipped wrappers, review
lifecycle, policy, installation and diagnostics: entry points, related consumers,
shared rules and primary vendor evidence. It is not exhaustive runtime testing
of every branch. No new provider experiment or runtime edit was made for it.
The previously started U9 diagnoses/test finished separately.

The earlier reasoning conflated two questions: whether a wrapper-created
failure is reproducible, and whether TRIAD should own that mechanism at all.
A failing synthetic test establishes the first, not the second. Test the
responsibility and value of the shared rule before choosing its implementation.

## Boundary

Vendor owns its agent loop, tools, background tasks, internal retries, model/
effort/permission interpretation and session lifecycle. TRIAD owns reviewer
selection, objective/diff/worktree delivery, the direct invocation's observed
completion, result identity/validation, agreement and its exact own artifacts.
The parent must still observe/cancel the call it starts. That does not justify
a second vendor process manager. Prefer native flags and ordinary process APIs;
switching Python to shell or introducing an SDK is not itself simplification.

## Complete feature inventory

Keep means essential result behavior. Simplify/Hold are recommendations, not
authorization to remove a working public contract without a shared decision.

| Feature and source | Disposition | Minimum value / candidate reduction |
| --- | --- | --- |
| Native spawning, `review_adapters_v2._native` | Keep boundary | Consume host result/handle; each host owns native internals. No external Claude-agent backlog. |
| CLI argv/cwd/prompt, three wrappers | Keep thin | One vendor invocation, exact prompt and opaque model values; no new launch abstraction. |
| Timeout, `_run_once_owned`, AGY `_build_cmd` | Simplify | AGY already receives `--print-timeout`. Native deadline plus one outer ceiling if required; no nested timeout state machine. |
| Post-success group sweep, `_common.py:1549-1558` | Priority simplify | Current code probes/kills remaining group members after normal CLI exit. Vendor-owned background work is not automatically a leak. Verify normal exit/cancel behavior before removing the assumption. |
| Group escalation, `_terminate_provider_process_group` | Simplify | Retain cancellation of the direct call. Do not promise discovery/reaping of every vendor descendant. Any emergency fallback is an explicit bounded choice. |
| Signal normalization, `_run_once`, `_mark_signal_failure` | Simplify spec | Cancellation must not become success. Producing identical summary/audit/run-log records in every signal window is separate complexity; observed exit/cancellation can express failure. |
| Reader/writer threads, mirror, polling, `_run_once_owned` | Priority simplify | Preserve prompt delivery/final output/exit through standard process APIs or owned output files. Live stderr mirroring is optional, not a review prerequisite. |
| Failed diagnostic/replay handling, `log`, `_drain` | Hold U9 patch | First remove unnecessary mirroring/guarantees. A small best-effort diagnostic can remain; no new logger or expanded failure matrix is selected. |
| Automatic capacity restart, `run_cli_with_retry` | Priority simplify | Vendor retries a request internally; TRIAD restarts a whole CLI. Raw Claude/Gemini can start three calls. Recommend one call, then diagnosed leader/repair retry. Formal Google/structured Claude already have narrower paths; no AGY outer retry is claimed. |
| Schema repair loop, `run_cli_with_retry` | Simplify | Prefer native structured output where available, then local validation. Do not automatically buy another answer to repair formatting without an intentional policy. |
| Final envelope extraction, three wrappers | Keep bounded | Normalize documented/observed terminal output. A vendor envelope is not yet a TRIAD verdict; do not reconstruct its entire agent session. |
| AGY finish recovery/telemetry, stream helpers | Conditional keep | Existing measured compatibility can be necessary. It is not authority for a universal tool audit. Retire only with supported-version evidence. |
| Classification and repair, `_common`, `apply_patch.py` | Keep narrow | Preserve vendor exit/message and known common outcomes. Unknown errors go to evidence-first repair/web research, not speculative taxonomy or automatic config mutation. |
| Model/effort, adapter `_claude` | Simplify | Pass owner selection. Separate `/model` process is not actual review-process attestation; reconsider its parser/receipt prerequisite, retain meaningful exposed contradictions. |
| Binary/version/flag preflight, adapters | Keep minimal | One absence/known-interface check. No repeated catalog or speculative entitlement gates. Existing version floors stay until separately decided. |
| AGY native-tool profiles, `_agy_agent` | Keep evidenced adapter | Concrete need: native read/search availability. Preserve explicit web choice; no generic Claude/Codex agent selection, new hook or global settings transaction. |
| AGY project/settings JSON checks, `_agy_settings` | Simplify candidate | Vendor applies effective permissions. Local UUID/root/deny requirements can be stricter and are not policy attestation. Never change user settings; decide whether extra preflight refusals remain valuable. |
| Auth route/environment, selector/scrubber | Keep owner policy | Account/billing route and authentication STOP rules are deliberate constraints. Do not remove them or change user settings as collateral cleanup. Loader-variable hardening is a separate installation-trust decision. |
| Worktree/read/web scope, renderers/policies | Keep minimal | Objective+diff+worktree and related-code discovery. No leader-constructed related-file list or routine read-log audit; preserve explicit exclusions/native controls. |
| Packet preparation, `review_round.py` | Keep core | Current task/diff/result identity; no separate checkout/full copy when existing-worktree review is selected. Prepared-directory compatibility is a separate public surface. |
| Verdict bindings, `verdict_*`, `validate_v2` | Keep | Reject another round/leg/attempt or malformed answer. Vendors cannot implement TRIAD cross-family agreement. |
| Repeated tree/toolkit hashes, `_load_basis`, `_toolkit` | Simplify | Routine allocate/record/collect reverify whole source/toolkit, sometimes twice per operation. R-RETRY already says pre-retry tree hashing is not required. Preserve immutable basis/final integrity; remove only proved redundant intermediate work. |
| Attempt/receipt/seal files, `review_round_v2` | Keep identity, assess consolidation | TRIAD owns review association, not vendor session state. Reduce duplicate files only while preserving old-answer rejection and failed-to-run versus completed-result distinctions. |
| Audit/run-log/debug/rotation, `_common` | Simplify candidate | Retain enough failure evidence and the collector's actual record. Three copies and fallback/rotation machinery are not inherently review features. Change the collector before removing its required run-log. |
| Own temp cleanup, review helper/fallback IPC | Keep ownership; hold U6b | Vendor cannot clean TRIAD files. Exact allocated-root cleanup is justified. First determine remaining artifacts; do not automatically add role-config framework, new debug pruner or general deletion API. |
| Install/update/uninstall, bootstrap/repair | Keep bounded | Vendors do not install TRIAD launchers. Preserve user files/known managed migrations. U8 coexistence stays withdrawn; old removal code is not active execution supervision. |
| Offline hook/diagnostic/benchmark helpers | Hold optional | AGY hook renders disabled config; no activation found in inspected runtime paths. Diagnostics/benchmark are opt-in/offline. Check packaging/compatibility users before deletion; do not activate dormant enforcement. |

## Scenarios and proposed order

1. **Normal CLI exit:** accept the observed final result; do not assume remaining
   vendor background work must be killed. AGY documents preserving daemons.
2. **Overload after vendor retries:** preserve failure for diagnosis instead of
   automatically repeating the whole prompt/tool workload twice more.
3. **Final-result-only review:** remove live stderr mirroring first; this may
   eliminate the wrapper-created output failure path that prompted U9.
4. **Owner cancellation:** retain observed failure/cancellation and exclude it
   from agreement; do not manufacture a terminal record in every signal window.
5. **Old valid JSON from another round:** retain binding checks. Native JSON
   validity alone cannot establish that this review was completed.
6. **Failed evidence storage:** choose one intentional review record and mark
   incomplete collection honestly, instead of adding layers of copies and sweeps.
7. **Old temporary residue:** remove only proven own artifacts; never turn this
   into a general filesystem cleanup service.

R-TERMINAL currently requires joined reader threads and a reaped process group,
coupling the common spec to an execution mechanism. Propose an observable
completion/cancellation contract instead. R-TOKENS/R-CLASSIFY outer retries,
R-RECEIPT evidence volume, R-BIND repeat verification and R-CLEANUP declarations
need the same value test. A's wrapper also has group escalation/threaded
transport; matching A is not independent evidence that the machinery is needed.
Neither host's native leg is a port/removal target.

U6b/U9 implementation is on hold. Their uncommitted drafts under workspace
`_runs/infra/20261010-spec-to-code/` are evidence-only, not the next executable
plan. Existing U9 RED17failed/3passed includes two mixed Gemini fixture failures;
it proves no all-route behavior or implementation necessity. No GREEN/new formal
round was started. Source fingerprint matched before these documentation edits.

Recommended sequence: decide the reduced invocation/transport boundary; then
the minimum evidence artifacts; only then cleanup. Before public behavior edits,
present exact removal/retention scope and normal/error/cancel consequences for
the owner's substantial-design decision. Amend shared rules first and complete
the applicable independent review. This audit does not approve removal, merge,
installation or release.

## Primary sources and limits

- [Claude headless lifecycle](https://code.claude.com/docs/en/headless): native
  output/exit, background work and SIGTERM handling; current docs are not proof
  for every supported/installed version.
- [Claude CLI](https://code.claude.com/docs/en/cli-reference): model, effort and
  structured-output controls.
- [AGY headless](https://antigravity.google/docs/cli/headless/): terminal statuses,
  schema output and native print timeout.
- [AGY changelog](https://raw.githubusercontent.com/google-antigravity/antigravity-cli/main/CHANGELOG.md):1.1.24 pipe-inheritance fix,1.1.28 daemon/background exit behavior, internal retry changes; these predate local1.3.3.
- [Gemini headless](https://geminicli.com/docs/cli/headless/): final JSON/exit.
- [Gemini0.63.0 retry source](https://raw.githubusercontent.com/google-gemini/gemini-cli/v0.63.0/packages/core/src/utils/retry.ts): vendor backoff/retry.
- [Gemini main cleanup](https://raw.githubusercontent.com/google-gemini/gemini-cli/main/packages/cli/src/utils/cleanup.ts): sync/async cleanup. Exact0.63.0 cleanup fetch was unavailable; no version-pinned whole-process-tree claim.

AGY's1.1.28 changelog also describes partial output with a successful exit when
its print timeout expires. Native timeout alone is therefore not proof of a
complete review: retain verdict/completeness checks instead of treating exit0
as agreement. This is documented behavior, not a new live reproduction.

No source proves every vendor cleans every descendant after every signal/crash.
That uncertainty alone does not authorize replacing vendor supervision.
