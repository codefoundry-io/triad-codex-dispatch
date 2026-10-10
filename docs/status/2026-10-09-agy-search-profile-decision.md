# AGY search capability: approved implementation

## Observed defect

U1b R2: Claude, Flash and fresh Codex SAFE; Pro NOT-SAFE because native search
tools were not exposed. Integrity matched; all producers terminated. Evidence
and cleanup: workspace `_runs/reviews/triad-opus-default-20261009-r2/`.
No verdict is admitted by majority, and R2 approvals cannot carry forward.

A separate bounded AGY Pro/high diagnostic on installed 1.3.2 used the existing
wrapper, plan/read-only posture, forced formal deny rules, formal environment
scrub and no autoapproval flag. It reported no native content-search declaration;
the read control returned the actual fixture marker. Captured events show one
view_file call, no search call. This is not proof from complete tool declarations
alone, but the vendor's own versioned changelog independently explains it.

`agy changelog`, 1.2.7, states that find_by_name, grep_search and list_dir were
retired from the default toolset and remain available to custom agents explicitly
listing them in tools. The complete CLI-supplied record is retained in workspace
`_runs/infra/20261009-spec-to-code/agy-tool-discovery-probe/agy-changelog.txt`.
The probe's prompt, script, result and captured tool events are beside it.
No global settings, provider permissions or persistent agents were changed;
the existing wrapper's temporary settings transaction restored its own state.

## Cross-host evidence

A read-only source check at clean `9e16880dc05e89b15669d42e9f62204d05349c7d`:
`3rd-Agent/wrappers/antigravity_wrapper.py:276-283,322-359` ships explicit
read-only tools in a main-agent profile, model inherited, subagent false.
`.claude/skills/triad-cross-family-review/references/leg-contracts.md:358-377`
describes setup-once `--agent triad-readonly-review` with a workspace read grant.
No current A provider run was performed; its live search capability is not claimed.
B's diagnosed baseline supplied no --agent and its rendered Google contract assumed those
legacy search names. File lists cannot repair this capability loss, and reading
every file for the reviewer would defeat independent discovery.

## Approved bounded design (2026-10-09)

1. Ship a B-owned AGY main-agent review tool profile, with view_file, grep_search,
   list_dir, find_by_name and finish; no shell, write, MCP, web or subagents.
   Its web-authorized twin additionally exposes read_url_content/search_web,
   preserving existing formal --web behavior. Use these for legacy/v2 formal
   preflight and dispatch; raw invocation behavior is outside this bounded fix.
   A reviewable draft is at workspace
   `_runs/infra/20261009-spec-to-code/agy-tool-discovery-probe/proposed-triad-codex-readonly-review.md`.
2. Keep model/effort as direct CLI parameters, the existing plan-mode/sandbox,
   formal environment scrub, read-only deny rules, result schema/bindings and
   source integrity controls. This is AGY tool selection, not a Claude Opus
   subagent or a model/effort preset.
3. Define setup/install ownership and check the selected definition before
   dispatch; bind the control for same-basis review. Do not fall back silently
   when absent or changed. Verify supported current lookup before deciding the
   final installation path. The likely global path needs a separate concrete
   write approval; no existing A-owned profile is overwritten or silently reused.
4. Record the shared contract change and ask A to review the same spec commit;
   preserve each host's native leg. Test a real search and read control under the
   final profile before a fresh complete formal review.

Scope: shipped profiles, wrapper/preflight binding, installation/check docs and
focused regressions. Initial estimate was +60-120/-0-30 production lines; current
estimate is about +150/-10 (net +140), novel core about 100, plus 40 profile lines,
tests and docs. Growth covers explicit safe setup and synthetic lifecycle
provisioning within this approved outcome. The separately approved global
installation and one native-search probe are complete; fresh R3 is all four SAFE
with matching integrity. Minor documentation follow-up remains in the SoT.

Decision: owner approved option 1 ("1번이긴 한데 그럼 이전에는 어떻게 검증한거야?")
and subsequently instructed "진행". Implementation is authorized. Global
activation received separate concrete path/delta approval later that day. A's current
lookup source identifies ~/.gemini/config/agents; AGY 1.3.2 --help confirms
--agent selects the current session's agent. B's subsequent real-lookup probe
proved native search/read under its own selected profile, as recorded below.

Prior four Pro preflight receipts (Google pins R4, Claude selection R2, Opus
default R1/R2) all recorded 1.3.2 and provider_started:false. This was not a
new upgrade between rounds; prior preflight never tested native search.

## Execution checklist

PR13 reply #6075351927 (2026-10-09) confirms A's init.agent selected its profile
on 1.3.2, but init.tools advertised 60 names including off-profile tools. Its
OK-only run made no tool call; there is no retained 1.3.2 successful-search
capture. Treat the profile as capability selection, never as a sufficient
permission boundary. Preserve B's guards and measure native search after setup.
No duplicate A probe requested. A agrees with C70/C71 and U1a interpretation.
Shared C72 published at 9bd9d58; main fetched at 3afc4d7. Dedicated source RED:
two missing/drifted cases incorrectly returned 0; hashes stable, no inference.
Evidence: _runs/spec-plan-20261009/agy-profile/red/REPORT.md.

- [x] Record shared rule/case and owner decision; preserve A implementation.
- [x] Dedicated fresh source executor observes missing/drifted-profile RED.
- [x] Package two profiles, explicit setup helper and exact definition checks.
- [x] Bind name/path/hash in legacy and v2 preflight; recheck before/after launch.
- [x] Dedicated fresh GREEN: 12 C72 tests; full suite 1915 passed/4 skipped,
  exit 0 in 404.91s; both source skill validators exit 0.
- [x] Independent code review and exact global installation delta prepared in
  [installation approval record](2026-10-09-agy-profile-installation.md).
- [x] After explicit installation approval, measure native search and read control.
- [x] Fresh complete R3: all four SAFE, ROUND_INTEGRITY_OK; no carried R2 approval.

Independent Astra/high code review found one Unicode-path serialization defect.
It was reproduced by a new regression before fixing ensure_ascii=True; C72's
12 cases then passed. Report: _runs/spec-plan-20261009/agy-profile/code-review.md.
Initial full-suite run retained 71 failures/1841 passes/4 skips: test profile
fixtures polluted tests' own tmp_path, synthetic preflight records and archive
fixtures lacked the new control fields/files, and the lifecycle fixture lacked
profile provisioning. Corrections keep profile fixtures separate, update test
evidence shapes, and provision the lifecycle's owned temporary directory in a
synthetic Python child. HOME and live global profiles remain unchanged. An
intermediate synthetic-HOME attempt hid existing Python user dependencies;
that approach was removed. No provider inference occurred in these tests.

Final dedicated GREEN (macOS arm64, Python 3.12.13, pytest 9.0.3) is at
_runs/spec-plan-20261009/agy-profile/green/. All 55 measured hashes and HEAD/branch
are unchanged. Strict Git status equality is false only because the leader
created the installation approval record during the run; that attributed,
non-executable status document is outside the measured source. Preserve this
distinction rather than silently calling the entire worktree unchanged. The
intermediate integration suite also passed 62 tests. These source tests alone
did not prove provider capability or formal admission.

After exact-path owner approval, canonical setup installed both B-owned profiles
without replacement and verified byte equality; A profiles stayed unchanged.
One real AGY 1.3.2 Pro/high formal-v2 call selected the review profile, completed
grep_search on the synthetic source tree, then view_file on the found receipt.
Vendor/wrapper exit 0. The first finish used schema_version 1; the provider
corrected it to 2 within the same invocation. No schema fallback or extra attempt.
This is Pro/no-web capability evidence only. Separately, full R3 completed with
all four SAFE and matching integrity; six Minor findings are reproduced in the
round adjudication. The SoT records the bounded documentation follow-up.
See [installation evidence and Gemini CLI distinction](2026-10-09-agy-profile-installation.md).

Files: bin/_agy_agent.py, bin/agents/*.md, antigravity_wrapper.py,
review_round.py, google_preflight_v2.py, focused tests and installation/route docs.
Existing SoT is the execution ledger (owner requirement); retain this checkout
and its dirty state. No separate workspace/commit choreography replaces it.
