# U7: AGY profiles without global settings transactions

Owner approved the bounded in-chat design and actual probe follow-up on2026-10-11.
Leader implements inline with executing-plans/TDD; fresh dedicated source-skill
executors run RED/GREEN. The required existing four-leg unit review follows.

**Goal:** preserve native review reads/search and authorized web using existing
profiles, without writing/locking/restoring user-global AGY permission state.
**Spec:** shared R-CONTAIN/R-REVIEW-WEB, C6/C68/C72 and
`decisions/2026-10-11-b-agy-profile-only.md`.

**Production estimate:** +50-110/-490-580 (net-530..-380), <=70 novel core lines,
`bin/_agy_settings.py`, `bin/antigravity_wrapper.py` and two existing profiles.
Tests: replace obsolete transaction tests, add ~130 lines of route/invariance
cases. Docs: ~70-140 changed lines across current English/Korean route guides.
No new API/service, hook, cwd architecture or native-leg changes.

Owner 2026-10-11: Claude maintainer replies are asynchronous input, not a
prerequisite. Continue independent spec/source/execution verification, share
established differences, and ask the owner only for actual unresolved design
decisions or separately required external changes. Required unit review stays.

## Constraints and review focus

- Read-only profile uses exclusion, explicit native tools, inherited rules,
  native plan/sandbox and no autoapproval. Formal bindings/results remain.
- Raw read-only reuses the research profile; permissive raw retains its version
  gate/autoapproval opt-out without any settings transaction or required profile.
- Minimum1.2.1 only on read-only routes; ordinary baseline1.1.20 stays.
- Requested web reads settings to reject known URL-wide deny/malformed existing
  JSON only; absent settings stay absent. Project validation stays non-mutating.
- Old backups/locks/leases are never healed/deleted. Concurrent user writes
  survive; provider failures never trigger settings restoration.
- Profile drift still withholds a completed result while preserving diagnostics.
- The live probe proves useful tools and no write after a request, not a denied
  attempted write or universal execution prevention. No new audit is added.

## One implementation task

Interfaces: preserve wrapper public flags and profile receipt keys. Keep
`agy_project_guard` read-only; replace global mutation helpers with
`check_web_settings() -> None`, raising ValueError/OSError for unusable existing
settings or an observed `read_url(*)` deny. `_settings_path` remains the existing
test injection seam, not a claimed vendor setting override.

- [x] Publish shared decision/cases and request A review before product changes.
- [x] Write `tests/test_agy_no_global_settings.py`; fresh dedicated RED on the
  canonical source. Assert bytes during provider execution and after completion,
  absent-state preservation, stale residue, concurrent writer and failure path;
  exercise actual wrapper/profile choices and the version boundary.
- [x] Remove global transaction code; retain project checker/known web-deny read.
  Add exclusion to shipped profiles, select them for read-only raw, and retain
  before/after definition checks. Remove only obsolete mutation tests/mocks;
  retain unaffected schema, custody, web, transport and profile-drift coverage.
- [x] Align current route/security/install/migration English/Korean references;
  preserve historical release notes. Describe old residue as preserved and
  explicit profile setup separately from deployment.
- [x] Fresh dedicated GREEN: focused modules, full suite, four validators;
  invocation-owned TMPDIR before Python starts, source/log fingerprint and cleanup.
- [x] Complete fresh opus/xhigh, AGY Pro/high, AGY Flash/high, Astra/high review,
  custody/adjudication and exact cleanup. Any required installed-profile update
  remains an explicit exact-path approval boundary, after reviewable changes.
- [x] Update completion evidence and SoT; publish source/spec with this record. Retain whole-task startup hook.

## Evidence ledger

2026-10-11: shared authoring1/1 and182 tests pass. Live probe from2026-10-10 is
retained, not repeated: two successes, real read/search/web, no write attempt,
protected hashes unchanged. Shared 07ee684 is pushed; PR13 comment6099196142
requests A review. Dedicated valid RED:16 failed/2 passed, all ten state cases
reached provider entry and observed mutation. The initial confounded RED is
preserved separately. Implementation and documentation are now ready for fresh
dedicated GREEN. Leader diagnostics:324 passed/4 skipped and42 distribution
tests passed. Installed profiles remain unchanged; formal review is pending.

First dedicated GREEN:366 focused passed/4 skipped; full2354 passed/4 skipped
and3 failed. Two failures accessed the removed fixture `guards` key; one pinned
the retired settings-restore documentation. These are test migration defects,
not demonstrated runtime failures. Corrected the two test modules to assert the
bound research profile/no autoapproval and current non-mutating contract. No
production changes. Source/log fingerprints matched and exact fixture cleanup
passed. A new executor must run corrected focused modules, full suite and the
previously unreached validators/bootstrap check; initial failure is retained.

Final dedicated GREEN:413 focused passed/4 skipped;2357 full passed/4 skipped.
Bootstrap syntax, four skill validators and diff check all exit0. All313 source
paths and21 source log files matched; exact invocation temp removed. macOS26.6.2,
arm64, Python3.12.13; Ubuntu not run. Evidence: `green-final/report.md` under the
workspace U7 evidence root. Owner then approved the exact two-profile update;
both installed hashes match source and known permission-setting hashes remain
unchanged (`profile-install-receipt.json`). Next: required formal review. Prepared
review runners are not executed; no provider started at this checkpoint.

R1 subsequently completed: all four valid, integrity matched; Pro/Flash SAFE and
Opus/Astra NOT-SAFE. Confirmed current docs/prompt claimed removed deny/restore
behavior. Corrected those claims and the v2 receipt minimum literal, preserved
optional project rules and added raw/formal timeout-plus-profile-drift coverage.
Correction RED5failed/3passed: stale prompt/docs and two unsupported receipt
versions failed; minimum1.2.1 and both existing timeout paths passed. No new
runtime timeout defect or permission mechanism. Source production grows by two
literal corrections only; documentation/test changes are separate. New GREEN
and full R2 remain. Shared0d7073d and PR13comment6099813534 record the clarification.

Fresh correction GREEN:584focused/2362full passed,4skipped; bootstrap syntax,
four validators and diff check passed. Source/status/log hashes matched; exact
owned test root removed after terminal collection. Evidence correction-green/REPORT.md.
Complete R2 next; no admission. Remote main refreshed unchanged at3afc4d7.

R2: all four SAFE, ROUND_INTEGRITY_OK; custody exported and exact stage cleanup.
Confirmed nonblocking test-isolation issue reproduced by fresh RED2failed: the
shared route fixture read ambient vendor settings. Pin its settings seam to
invocation-owned home and extend existing success/profile-drift capture assertions.
Product bytes unchanged. Fresh GREEN/R3 follow; editorial/import/refactor-only
suggestions are dispositioned without new changes or backlog.

Final fixture GREEN:304affected/2364full passed,4skipped; bootstrap/four validators/
diff check and source/status/log integrity pass, exact owned temp removed.
Evidence fixture-green/report.md. Final R3 starts on these bytes; only internal
progress documentation changed after GREEN. Main refreshed unchanged3afc4d7.

Final R3: all four SAFE, ALL_SELECTED_APPROVED/ROUND_INTEGRITY_OK. Six Minor
suggestions dispositioned, no remaining functional blocker. Exact stages removed
after custody export. U7 complete; source/spec publication accompanies this record.
Two installed profiles already match source; no full plugin installation or release.
Remaining task: U6b, U9, U2 reconciliation and U10; keep startup hook.
