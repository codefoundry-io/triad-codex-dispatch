# Changelog

## 0.2.534 — 2026-08-11

- This is the first immutable release tag containing the post-`v0.2.533`
  review-lifecycle revision already merged to `main`; the public `v0.2.533` tag
  predates those bytes.
- Publishes the unique-ID system-temporary review lifecycle, exact member-list
  copying, canonical `SOURCE_SHA256SUMS` manifests, metadata-bound prompts and
  verdicts, prepared-directory plus prepare-source-bound and member-rechecked
  canonical-worktree integrity verification, exact-root cleanup, current-root wrapper logs, and
  the documented packaged AGY headless selection without changing user settings.
- Qualifies the focused-review benchmark so its preregistered 3/3 recall is
  distinct from the amended checked-in 4/4 aggregate.
- Defines how non-blocking hardening suggestions, missing correctness context,
  and correctness-relevant surfaces omitted from a prepared directory travel
  through the existing `Minor` and `open_questions` carriers without expanding
  the verdict schema or path-root protocol.
- States the exact native-tool containment residual: the prepared-directory and
  canonical-worktree fingerprints do not prevent or detect mutations in
  Git-ignored worktree paths not selected as packet members or elsewhere, or
  network egress; final verification discards rather than prevents verdicts
  produced from mid-round tampered bytes.
- Tightens the review skill instructions with shell-safe path arguments,
  explicit metadata binding, exact manifest coverage, pre-root failure cleanup,
  and direct leg-contract navigation.

## 0.2.533 — 2026-08-05

- Replaces batched review evidence with one focused directory and one strict
  Claude, Google, and fresh Codex `LegVerdict` per round.
- Retains the formal Claude leg's existing 1,800-second deadline and adds an
  explicit 1,800-second deadline to the selected AGY leg; the AGY wrapper default
  and separately authorized Gemini fallback remain unchanged, and shorter leader
  polls remain wake-up boundaries rather than provider failures.
- Preserves provider-native, installed CLI, and configured MCP read/search
  tools for formal review, forbids only mutation, external-state change, and
  candidate execution, and requires `SOURCE_SHA256SUMS` in every managed
  lifecycle `shared/` directory produced by `prepare`.
- Qualifies the packaged AGY child's `always-proceed` selection in formal routing
  and documents that configured wrapper allowed roots must include the canonical
  system temp base used by formal review paths.
- Makes every packaged headless AGY call internally insert
  `--dangerously-skip-permissions`; callers do not pass the flag. This does not
  edit user settings, add a sandbox or command-specific allowlist, or suppress
  installed CLI, MCP, read, or search tools. The review prompt controls the
  no-mutation boundary, and a denied or invalid leg requires a fresh-ID
  complete restart.
- Retains the existing caller-facing `--preflight-only` version/route receipt;
  it does not inspect or gate permission state. Only the rejected permission
  `--init-preflight` and `--expected-permission-mode` paths remain removed.
- Implements the unique-ID system-temp lifecycle guarantee: exclusive
  `prepare`, exact JSON member-list source copying, current-packet manifest
  validation, exact-root `cleanup`, and next-prepare cleanup for managed roots
  inactive for strictly more than 30 days.
- Makes `prepare` require exactly one non-empty `--required-members-json` array
  of unique paths and reject repeated arguments, duplicate paths, or any required
  path absent from the full member list before root creation.
  This replaces the fallible leader-side subset command without adding another
  file, subcommand, Git inference, state record, lock, or registry.
- Defines the member list as a sorted JSON array of non-empty normalized POSIX
  relative paths and generates `SOURCE_SHA256SUMS` exclusively through the
  lifecycle tool. The manifest is a sorted JSON array of exact decoded
  `{path, sha256}` objects in canonical bytes, matching capture validation and
  rejecting even a semantically equivalent manual reformat before review.
- The lifecycle reader rejects non-regular member-list nodes before reading and
  maps prepared-file I/O failures to the controlled lifecycle error instead of
  blocking on a FIFO or leaking a traceback.
- Every rendered prompt carries dynamic values only in one canonical
  `Review metadata: ` JSON record, so quotes, backslashes, line controls, and
  Unicode separators are not reinterpreted as prompt framing.
- Makes the exact digest printed by `capture` the only supported digest handoff
  into prompt rendering and verdict validation. Leaders do not parse snapshot
  fields to recover or recheck it; the packaged `verify` command owns final
  snapshot validation.
- Aligns three reviewed contract edges without adding lifecycle machinery:
  out-of-base lifecycle-shaped paths report the boundary error before review-ID
  parsing, managed JSON records use canonical compact serialization with one final LF, and
  rendered prompts carry the governing affected-consumer tracing instruction.
- Creates `.last_activity` only after every exact source copy succeeds, uses a
  regular non-symlink marker mtime when available, and uses the exact managed
  root mtime for sweep and successful lifecycle CLI activity only when that
  marker is absent or safely identified as unsafe. Marker inspection or update
  failure remains best-effort and does not change the completed operation
  result; no second completion marker or lifecycle registry is added.
- Preserves the owner-approved prepared-directory digest algorithm, including
  its symlink and unsupported-entry rejection. The reviewed `git hash-object` replacement proposal is not adopted;
  a reviewer finding alone does not reopen that decision.
- Treats review IDs as single-use and relies on exclusive root creation for
  collision handling, without adding `flock`, lock files, registries, or
  background coordination.
- Excludes the currently requested ID from the 30-day stale sweep, so an old
  same-ID root still collides instead of being deleted and silently reused.
- Binds source copying to no-follow file descriptors, rejects lifecycle-shaped
  paths outside the current temp base, reports ineligible managed-prefix roots,
  rejects member paths with no POSIX component, maps unrepresentable path input
  to the controlled error contract, and never treats a remaining dangling
  symlink as successful cleanup.
- Rejects capture/render/verify for a canonical managed review root itself and
  every descendant other than its exact `shared/` child.
- Makes lifecycle verification reuse the existing packet validator before
  reporting success and brackets worktree fingerprinting with packet-digest
  checks; digest equality does not replace semantic packet and manifest validation.
- Routes formal wrapper logs into the configured current review root, reports a
  real configured review-root storage error as unavailable for either successful
  or failed provider results, and does not fall back outside that root. Advisory
  lock contention or attestation skips and post-append rotation failure do not
  mislabel a healthy successful result. Unconfigured wrapper fallback behavior
  remains unchanged.
- Makes the current owner-supplied task or explicitly designated executable
  plan the `triad-cross-family-review` execution authority. It must carry every
  retained or rejected decision needed for execution; an omitted needed
  decision requires owner clarification, not runtime recovery from this file.
- Repeats complete three-family rounds after bounded fixes until unanimous
  admitted `SAFE`, conflict, oscillation, invalidity, or an owner decision.
- Requires owner approval before design, specification, capability,
  generalization, or scope changes; external reviewers never write code.
- Migrates AGY to the 1.1.10 native `stream-json` and `json-schema` contract,
  uses the exact `gemini-3.1-pro-high --effort high` route, invalidates every
  exposed model conflict, and removes PTY, sentinel, sandbox, caller-facing
  permission controls, packet, batch, and receipt runtime paths.
- Requires packaged-byte and fresh-process evidence before a distribution claim.
- Limits the separately authorized formal Gemini fallback to one provider call;
  capacity failure and invalid structured output are terminal without hidden
  capacity or schema-repair calls. The ceiling applies to both supported
  packaged `LegVerdict` operand syntaxes.
- Records `unexposed` runtime identity when an AGY request times out before an
  init event can expose the selected model.
- Rejects benchmark inputs with zero cases or zero planted findings, and adds a
  clean-HEAD distribution verifier that stages exact archive bytes, compares
  load-bearing hashes, and runs tests from the extracted package.
- Records a two-round runtime benchmark: six total provider calls, 3/3
  preregistered defect recall, 3/3 confirmation `SAFE`, zero admitted mutations,
  and an 87.5% call reduction against the captured 24-call batch plan. `LOCAL-2`
  was added to the expected IDs after reviewer output, so the checked-in 4/4 and
  zero-false-finding aggregate uses amended ground truth; the call and artifact
  measurements are unaffected.

## 0.2.532 — 2026-08-03

- Adopts AGY 1.1.10's repaired headless model-selection contract for formal
  Google review. Authenticated `agy --version` must report 1.1.10 or newer,
  authenticated `agy models` must expose catalog selector
  `gemini-3.1-pro-high`, and the outbound model argument
  `gemini-3.1-pro-high` uses no `--effort`. The display-label compatibility
  route is historical; generic wrapper model/effort passthrough remains
  unchanged. This 0.2.532 route is historical and superseded by the exact
  0.2.533 route above.
- Candidate release: provider, user, and project settings now own permission
  selection and workspace trust. TRIAD does not install or inject a permission
  profile, command rule, pre-spawn `shell_environment_policy`, read-only repair
  agent, sandbox mode, or bypass. Trusted terminal/Python/`PATH` startup remains
  a prerequisite; wrapper child-process scrubbing remains after trusted startup.
  This 0.2.532 permission statement is historical; 0.2.533 supersedes it with
  the disclosed wrapper-internal AGY flag and no user-settings mutation.
- Binds the full diff to the complete affected-source closure and exact current
  candidate bytes. Formal plan and pre-merge gates include all repository test
  source for this release, while normal SDD implementation review includes
  relevant test source. Every required family reviews every affected production
  source in every deterministic batch with source-grounded observations, exact
  full-file ranges, and strict digest-bound coverage admission.
- Retains the packaged `FormalReview` operand and unbatched `formal-gate` result
  only for explicit compatibility callers. Operational pre-merge review uses
  `batched-full-coverage` and the strict `BatchReceipt` contract; the two result
  shapes are not interchangeable.
- Makes native AGY `permission-unavailable` a terminal post-dispatch result.
  Ordinary/non-formal Gemini fallback is limited to no-final-summary exit `4`
  plus the wrapper-owned pre-submission `PtyStartError` diagnostic. Every
  final-summary result is fallback-ineligible. Missing/invalid `TRIAD_AGY_BIN`
  and missing `agy` on `PATH` are direct route-setup errors, not fallback
  triggers.
- Requires separate owner authorization for an exact formal Gemini route and
  preserves the same immutable prepared directory, prompt-controlled no-edit
  contract, digest/mutation invalidation, full batch matrix, and strict
  admission. An unavailable required family leaves an invalid round.
- Replaces the installed repair Custom Agent and apply launcher with a fresh
  native proposal-only child and a bootstrap-printed login-shell
  `python3 bin/apply_patch.py` owner argv carrying the same explicit pinned
  `--classifier-file` used by provider launchers.
- Removes wrapper `--sandbox` flags and current permission-controller setup.
  Install/remove clean up only exact plugin-owned legacy profiles, rules,
  repair registration, pre-spawn environment-policy fragments, and retired
  launchers; owner-authored settings and credentials are preserved.
- Current non-UTF-8 source fails closed with `non-UTF-8 source`; it cannot be
  omitted from closure. Candidate verification, formal admission, installation,
  and publication remain pending and are not release facts in this changelog.

## 0.2.531 — 2026-07-25

- Adds one provider-neutral review prompt contract for Claude, Google-family,
  and fresh Codex legs. It records the review mode, objective, perspective,
  provider and destination, approved and excluded data, test-source boundary,
  digest, inspection rules, evidence rules, and selected result profile before
  dispatch.
- Separates `consult`, `advisory-review`, and `formal-gate` result profiles.
  Formal review retains the existing semantic verdict, evidence, citation,
  digest, and invalidation rules; consult and advisory results cannot be
  promoted to formal gate passes.
- Requires explicit invocation for Claude, Antigravity, and Gemini provider
  dispatch skills. Implicit cross-family activation may prepare a bounded review
  but waits for an explicit owner request or matching standing authorization
  before sending repository data externally.
- Replaces broad independent-opinion defaults with prompts that require the
  objective, approved data, exclusions, and result profile. Wrapper, model,
  effort, fallback, extraction, repair, and AGY compatibility behavior remain
  unchanged.

## 0.2.530 — 2026-07-25

- Revalidates the formal AGY route against authenticated AGY 1.1.7. Controlled
  runtime probes and AGY's `/model` response exposed both
  `--model gemini-3.1-pro-high` and
  `--model gemini-3.1-pro --effort high` as Gemini 3.6 Flash High, while
  `--model "Gemini 3.1 Pro (High)"` with no `--effort` exposed Gemini 3.1 Pro
  High. The current formal display-label route therefore remains selected.
- Requires every future AGY update to compare the completed catalog selector,
  base selector plus effort, and current display-label control as separate
  runtime probes. Catalog presence or provider acceptance alone never
  authorizes a formal-route change; exposed identity must also agree.
- Keeps the wrapper transport unchanged because its exact `--model` and optional
  `--effort` passthrough already supports all three candidates without
  inventing an effective model.

## 0.2.529 — 2026-07-23

- Applies the owner-approved minimal formal-review correction: formal plan and
  pre-merge gates use one leader-prepared shared review directory containing
  current approved production source, configuration, and documentation. Project
  instructions or the owner supply exact test-source exclusions; if unavailable,
  stop and ask the owner. Every leg receives the same directory and task. No
  prompt inlines a diff or file body. Record one simple content digest before
  dispatch and compare it after every required leg terminates; a mismatch
  invalidates the round. Normal SDD implementation review includes relevant
  test source, and classify every test failure as production defect,
  test-case defect, or intentional specification change before a formal gate.
- Historical R14-R17 path-list attempts remain preserved verbatim as historical
  evidence and do not direct the current shared-directory flow. Provider
  authorization, route selection, and result handling remain governed by their
  existing skills.
- Keeps ordinary/non-formal fallback available after proven pre-submission agy
  unavailability and centralizes the complete formal Gemini admission policy in
  the [formal reviewer routing contract](skills/triad-cross-family-review/references/reviewer-routing.md).
  The shipped distribution carries no qualifying proof and runs no automatic
  enforcement probe, so formal fallback remains closed by default.
- Uses fresh Codex `gpt-5.6-terra`/`xhigh`, Claude `opus`/`xhigh`, and primary
  agy authenticated `agy models` catalog selector `gemini-3.1-pro-high`; its
  exact outbound model argument `Gemini 3.1 Pro (High)` with no `--effort`.
  Sol and Fable remain conditional long-running escalation routes rather than
  routine reviewers.
- Keeps ordinary `codex` as the normal path, leaves the owner's approval,
  reviewer, sandbox, and Auto-review policy unchanged, installs exact wrapper
  rules with `decision = "prompt"`, and adds a provenance-marked native
  loader-environment guard before those launchers execute. Agent Review requires
  `on-request`/`auto_review`; granular policies must also keep `rules` and
  `sandbox_approval` interactive. Commit, push, install, merge, tag, and release
  remain separate owner decisions.
- Keeps agy's own-line truncation marker fail-closed as terminal
  `truncated-answer` while requiring a new bounded, compact read-only dispatch;
  it does not restore the 0.2.528 generic `write_file` or sandbox-bypass
  workaround.
- Keeps the hand-maintained migration rules on the same Agent Review `prompt`
  boundary as generated rules, and preserves repair-analyzer registration order
  across repeated installs when `config.toml` was initially absent, its managed
  environment policy was edited, or owner keys were appended later.
- Removes the expired `--check`/`--uninstall` aliases. The legacy profile uses
  `TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1`; the shell entry requires both that
  flag and `TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1`. Ordinary installs continue
  to use `--install`/`--remove` and plain `codex`.
- Prevents a late repair-analyzer registration failure from publishing provider
  wrapper launchers, `triad-apply-repair`, analyzer/registration, command rules,
  or the legacy shell entry, avoiding a partially activated install.
- `--model` and optional `--effort` pass through unchanged to agy; preflight
  reports the requested `model` and `effort` only, while provider identity is
  admitted separately when exposed and recorded as `unexposed` when absent.
- Avoids a registration-only backup on a fresh config and keeps malformed
  registration edits fail-closed during removal.
- Preserves a pre-existing empty `config.toml` across install/remove while still
  deleting a bootstrap-created config that did not exist before installation.
- Scopes absent-file restoration to the case where both provenance-marked managed
  registration and environment-policy blocks remain intact; owner files and
  altered or partial managed blocks are preserved.
- Keeps the loader-environment guard when command-rule publication is opted out
  but owner-maintained rules remain at the configured path and may still launch
  the managed wrappers.
- Removes the managed separator with the loader guard so a pre-existing owner
  config that lacked a final newline round-trips byte-for-byte.
- On upgrade, a plain install retains exact managed legacy profile and
  `codex-triad` shell artifacts and warns with their paths; it never deletes
  them automatically. Use deliberate `--remove` followed by ordinary
  reinstall, or explicitly opt into the legacy profile and shell entry. An
  unsafe or unreadable unselected path is reported with its refusal detail but
  is not followed or changed, and selected ordinary installation continues;
  selected profile, rules, and shell targets remain strict.
- Ordinary `codex` remains the normal start path. The retired no-prompt
  `allow` posture is not restored; exact launcher rules remain `prompt`.
- A pre-0.2.529 config that was initially absent but carries stale
  `original config existed = true` provenance is left as a safe zero-byte file,
  because it is indistinguishable from a genuinely pre-existing empty file.

## 0.2.528 — 2026-07-22

- Added terminal `truncated-answer` detection for agy's lossy own-line
  `<truncated N bytes|lines>` marker. This release also documented an
  absolute-path `write_file` workaround; 0.2.529 supersedes that workaround
  with the bounded, compact, read-only re-dispatch contract.

## 0.2.527 — 2026-07-21

- Gives every Pydantic Antigravity call one JSON-body-plus-sentinel response
  contract; schema repair rebuilds from the unsealed prompt and uses the same
  sealer instead of stacking conflicting output instructions.
- Treats an Antigravity terminal `DONE` whose `truncated_fields` includes
  `content` as incomplete and falls back to the existing PTY extraction path.
- Lets a byte-identical sealed review snapshot move between packet parents while
  retaining its generated directory name as the logical snapshot identity;
  renaming still invalidates verification.
- Installs the exact read-only `triad-repair-analyzer` registration and stable
  `triad-apply-repair` argv launcher with transactional, provenance-checked
  install and removal.
- Bootstrap performs no provider, authentication, or model probes. It prefers
  `agy` and reports a discovered `gemini` executable only as a fallback
  candidate; the formal workflow accepts that Gemini Enterprise/Business,
  Vertex, or API-key route only after owner-terminal proof.
- Keeps wrapper file IPC shell-safe, preserves fresh concurrent run logs during
  age-floor pruning, and renders dynamic owner commands from argv with Python
  `shlex.join`.
- Verified the shipped test suite on macOS and Ubuntu 24.04 using Python 3.12;
  bootstrap verification does not invoke a provider CLI.
- Formal sealed calls verify `PACKET_SHA256, SHA256SUMS, and INPUT_SHA256SUMS`
  before provider resolution, so cached workspaces cannot substitute review
  evidence. `schema-fail is terminal for that invocation`; a leader may make an
  explicit new invocation after deciding what to do.
- Uses the packaged `FormalReview` operand and one
  `Critical | Major | Minor` contract across providers. Claude and Gemini now
  carry the paired sealed-packet context through initial validation;
  the model verifies manifest-listed citation bytes and line ranges. Gemini is
  advertised only as a proven pre-dispatch agy-unavailability fallback.
- Historical behavior kept provider results authoritative when audit/debug
  storage failed and used unique private file IPC if the configured run-log root
  was unavailable. 0.2.533 supersedes the configured-root fallback; only an
  unconfigured primary log root may use the private temporary fallback.
- Pins one canonical classifier path into provider/apply launchers and closes
  repair-bootstrap overwrite/removal races with private quarantine plus
  no-clobber publication and recovery.
- Preflights all three provider wrapper command targets before the first
  persistent bootstrap mutation, and stops without partially installing other
  artifacts when any target is unsafe or unmanaged.
- Rejects Python runtime paths that portable macOS/Linux shebangs cannot encode.
- Uses collision-resistant native subagent task labels with explicit collision retry, leaves identical versus perspective-split
  prompt strategy with the leader unless the owner constrains it, and keeps nonterminal tool
  handles pending through event-driven status checks; poll timeouts are wake-up boundaries only.
- Cleans managed UUID/file-IPC entries older than 3,600 seconds best-effort before
  provider execution for each normal non-`--repair-mode` wrapper invocation that reaches its
  dispatch driver, and before Antigravity `--preflight-only`; cleanup errors never block dispatch
  and no perfect garbage collector is claimed. Bootstrap newly publishes only the three
  provider wrapper commands; `triad-setup` and `triad-doctor` are remove-only
  legacy cleanup names. Provider installation and login remain user-owned in a
  normal authenticated terminal, with no credential copying, sandbox-login
  attempt, company setup flow, or authorization store.
- Rejects unlisted files and filesystem objects in a sealed review packet,
  preflights foreign profile/rules files before command publication, preserves
  malformed shell RC blocks, and claims managed profile/rules/legacy-agent
  inodes before removal.
- Distinguishes a genuine first-attempt AGY executable start failure from a
  vendor process that exits 127, bounds the PTY start handshake by the existing
  timeout, and keeps prompt/cwd/resource failures ineligible for Gemini
  fallback.
- Writes and prunes failure run logs through descriptor-bound, no-follow Python
  operations; a symlinked log ancestor or foreign symlink/hardlink leaf is left
  untouched and primary storage falls back to unique private file IPC.
- Recognizes public wrapper ownership only from the exact generated command
  grammar, so copied marker text cannot authorize install-time replacement or
  removal of an unrelated executable.
- Treats every packet/review identity mismatch as an invalid formal leg outside
  `FormalReview`, and injects the complete canonical nested finding schema plus
  verdict rules into every external formal-review prompt.
- Runs transaction finalization and rollback for mutation-time interrupts as
  well as ordinary errors, and suppresses an already validated Antigravity
  answer when settings restoration fails.
- Registers rollback state before public `rename`/`link` mutations, binds each
  managed command's shebang interpreter to its exec interpreter, recognizes
  only exact current or shipped legacy pin/command ASTs, and rechecks IPC age
  on the final held descriptor before stale or cap-based deletion.
- Makes formal review input code-complete for the scoped repository, treats the
  diff only as a navigation index, validates native Codex JSON through the same
  packaged sealed-packet schema, and defines deterministic no-summary wrapper
  handling without inventing repair or Google-fallback evidence. The packaged
  Python snapshot helper keeps complete enumeration evidence in file IPC while
  returning only a compact path/hash receipt on stdout.
- Publishes managed shell-RC changes and legacy repair-agent quarantine through
  exact-state Python transactions, and writes Antigravity settings through
  unique no-follow/no-clobber temporary inodes instead of predictable paths.
- Keeps snapshot source reads beneath a retained repository descriptor, refuses
  filesystem entries Git cannot safely enumerate, normalizes sealed executable
  modes, and streams candidate verification. Personal migration templates no
  longer contain company deployment or managed-configuration instructions.
- Declares the formal-review runtime dependency in `requirements.txt`; bootstrap
  feature-probes Pydantic 2 before mutation and prints an argv-safe command for
  the owner-selected Python instead of installing packages itself.
- Refuses a managed shell-entry install during preflight when owner bytes lack a
  final newline, before any persistent install mutation. Documentation now states
  the actual default: exact installed wrapper launchers are auto-approved by
  generated rules, while unrelated commands remain `on-request`.
- Pins audit prompt redaction in every generated provider launcher, including the
  normal profile start that does not use the optional hardened shell entry.
  Sealed Antigravity prompts now place trusted packet identity inside the request
  before applying the existing schema wrapper, keeping the complete
  `FormalReview` JSON instruction last.
- Rejects a symlinked Antigravity `settings.json` before starting a settings
  transaction, preserving both the link and its target.
- Formal Google review prompts put fenced runtime evidence before a compact
  complete-envelope contract, include SAFE and NOT-SAFE few-shots, require
  concrete packet-relative `path:line` locations and empty arrays for no
  issues, and bind both the trusted review ID and packet hash.

## 0.2.526 — 2026-07-18

**Cross-family review v0.17.0 — CONFLICTED verdicts CALL THE OWNER.**
The consolidation rules gain a CONFLICTED round class: a head-on
same-decision contradiction between review legs, with both sides
surviving the deterministic fact-check probe, triggers an IMMEDIATE
owner call (push notification where available, else an OWNER-CALL
conflict table) instead of leader-side compromise adjudication;
non-conflicted findings keep converging in parallel. Probe-refuted
sides, complementary findings, and same-defect convergence remain
non-conflicts (rules 4b/4c/12 + Flow step 5).

_(Prior release 0.2.524 — **claude worker `--model` dispatch-time
selection**: `claude_wrapper.py` accepts `--model <alias-or-name>`,
free string, never pinned in code; `--effort` already wired.)_

_(Prior release 0.2.521 — **agy ≥1.1.3 headless permission fix**: the
wrapper version-gates `--dangerously-skip-permissions` on agy ≥1.1.3
so the soft-denied headless leg runs again. The flag auto-approves
permission prompts, while the injected deny rules retain precedence
and `--sandbox` stays in the provider argv. Strict deployments can opt
out with `AGY_NO_HEADLESS_AUTOAPPROVE=1`.)_

**Review orchestration discipline** (from an earlier release's
hardened-audit custody + agy extraction strictness + review-packet
lifecycle):

- The cross-family-review skill now spells out the LEADER's
  consolidation role (fact-check every finding with a deterministic
  probe, classify the round CONVERGING vs OSCILLATING, and hand an
  oscillating round's conflict table to the user instead of another
  round) and hub-and-spoke leg orchestration (one generous
  event-driven wait per leg — a wait timeout is a wake-up boundary,
  not a failure; steer a running leg instead of respawning it), and
  recommends pinning the fresh reviewer as a `.codex/agents/`
  custom agent with `sandbox_mode = "read-only"` plus a high
  reasoning effort so both are config-enforced per spawn.
- Redact mode (hardened default via bootstrap): the durable audit now
  stores `stdout`/`stdout_head`/`stderr` as `"<redacted>"` plus
  lengths on every record and caps `extraction_error` at 500 chars;
  the transient failure run-log keeps full copies. NOTE: audit files
  written by earlier hardened installs may contain full non-ok
  streams — rotate/purge them once.
- The antigravity pty-fallback extractor accepts its completion marker
  only when TERMINAL (whitespace-only tail AND newline-preceded, per the
  sealed prompt's own-line instruction); a truncated run whose only
  marker is an early echo fails closed instead of returning a partial
  answer as ok.
- Relative `--prompt-file` stays fail-loud; the error now shows the
  caller cwd and a cwd-derived absolute candidate.

Built from the Triad source of truth. Full history: https://github.com/codefoundry-io/triad-codex-dispatch/commits/main (each release commit summarizes its delta).
