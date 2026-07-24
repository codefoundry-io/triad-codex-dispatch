# Changelog

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
- Keeps provider results authoritative when audit/debug storage fails and uses
  unique private file IPC if the configured run-log root is unavailable.
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
