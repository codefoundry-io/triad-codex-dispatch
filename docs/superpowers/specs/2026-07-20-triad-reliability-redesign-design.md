# Triad Dispatch Reliability Redesign

**Date:** 2026-07-20  
**Status:** Approved design, pending written-spec review  
**Target repository:** `triad-codex-dispatch`  
**Implementation branch:** `codex/triad-reliability-redesign`

## Purpose

Make ordinary three-family dispatch and code review reliable enough to run
continuously without repeated authentication, sandbox, consent, escaping, or
incomplete-context interruptions. Preserve a stricter formal review mode for
release and correctness-critical gates without imposing that ceremony on every
ordinary review.

The design responds to reproduced failures in the current `0.2.526` source and
installed package. It does not rely on inferred Codex behavior. Codex runtime
claims are grounded in the live native tool schema and the official
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[Sandbox and approvals](https://learn.chatgpt.com/docs/agent-approvals-security),
[Rules](https://learn.chatgpt.com/docs/agent-configuration/rules),
[Plugins](https://learn.chatgpt.com/docs/plugins), and
[Authentication](https://learn.chatgpt.com/docs/auth) documentation.

## Confirmed Failure Model

### Native Codex review route

The live `spawn_agent` surface accepts separate `model`, `reasoning_effort`, and
`fork_turns` fields. A review-only Custom Agent is therefore not required merely
to select a model or reasoning level. A fresh Codex reviewer will be requested
with:

- `fork_turns="none"`;
- an explicit model;
- an explicit reasoning effort;
- a bounded prompt that forbids edits and identifies immutable input paths.

The requested selector values and fresh task/thread identity are recordable.
If the child runtime does not expose its actual model or effort, provenance must
say `unexposed`; it must not claim that the requested value was independently
verified.

### Installation and authentication boundary

The existing bootstrap writes launchers, profiles, and rules and then performs
live provider probes. A bootstrap process already running inside a Codex
sandbox cannot make its child probes cross a new host approval boundary. Newly
written rules also do not change the currently running session. The result is a
completed installation reported as failed for an unrelated provider login,
quota, capacity, or sandbox condition.

Installation and operational authentication are therefore separate products:

- installation creates deterministic local artifacts;
- setup records owner choices that require human authority;
- doctor verifies static configuration and, only when explicitly requested
  from a normal login terminal, performs live provider probes.

### Incomplete and mutable review evidence

The existing source review workflow treats a path-scoped `git diff` and a short
packet locator as sufficient evidence. That can omit staged changes, untracked
files, unchanged impacted callers and callees, tests, build wiring, contracts,
generated inputs, binaries, and submodules. The live repository and packet can
also change after one reviewer starts, so identical locators do not prove
identical bytes.

The installed `0.2.526` review skill attempts to require stronger packets, but
it differs from the same-version source and names runtime features such as
`--preflight-only` that the shipped wrappers do not implement. Version equality
is not package equality.

### Escaping regression

The provider wrappers use list-form argv and shell-free process creation. That
transport must remain authoritative. Bootstrap authentication probes and skill
copy-paste commands reintroduced shell parsing and incomplete quoting. Paths and
prompts containing spaces, quotes, backticks, `$()`, newlines, or leading dashes
are therefore not covered end to end.

### Repair regression

The removed write-capable vendor repair agents could read untrusted logs and
write classifier state, so removing that confused-deputy path was justified.
Removing the in-session repair capability was not required. Repair must restore
an LLM classification step while keeping persistence deterministic and bounded.

## Architecture

The redesign has four independently testable subsystems.

### 1. Deterministic installer and owner-run setup

`scripts/bootstrap.sh --install` will perform only local, deterministic work:

- validate prerequisites and resolved paths;
- install pinned argv launchers;
- install the Codex profile and command rules chosen by the owner;
- install the review/repair helpers and package manifest;
- run static syntax, manifest, and `codex execpolicy check` verification;
- report that a new Codex session is required when runtime configuration
  changed.

It will not invoke Claude, Gemini, Antigravity, or Codex models. A provider
failure cannot invalidate a successful local installation.

A generated `triad-setup` command will be the human boundary. It will:

- show provider-native login/status commands without handling credentials;
- record an explicit workspace-scoped external-review authorization;
- record the chosen no-prompt posture;
- reconcile required environment-variable names with Codex shell environment
  policy without reading or storing credential values;
- tell the owner to start a fresh Codex session.

The default authorization scope is one canonical workspace root. It covers
owner-approved private source packets sent to the configured Claude and Google
review routes. It never authorizes secrets, credential stores, unrelated
directories, or writes by external reviewers.

A generated `triad-doctor` command has two modes:

- default static mode: no network and no model calls;
- explicit `--live` mode: top-level login-terminal provider status/smoke checks
  using exact absolute launchers and argv transport.

Live failures must preserve provider output classification and distinguish at
least authentication, sandbox/environment, quota/capacity, version/config, and
transport failures. Authentication failures are terminal and never
automatically retried.

### 2. Immutable code-complete review inputs

The review workflow will support two modes.

#### Ordinary mode

Ordinary mode optimizes for routine development flow while still using stable
evidence. A packet builder creates one immutable review directory containing:

- base and current commit identities;
- staged, unstaged, committed-range, and untracked change inventories;
- full postimage bytes for every selected source input;
- the complete diff as navigation evidence, not as the review boundary;
- unchanged impacted context selected from callers, callees, imports, tests,
  build/configuration wiring, and public contracts;
- executed test commands and their captured results when supplied;
- a file manifest and SHA-256 sums;
- a concise review brief and concern scopes.

Reviewers may follow affected code only inside the immutable archive. The
archive is the source of truth; mutable live-worktree paths are not review
inputs. A coverage ledger records why each unchanged context file is present.
An unresolved impact edge is explicit evidence, not silently omitted context.

Ordinary mode does not require release provenance, provider preflight receipts,
or schema signing. It still rejects a mutated archive or missing required leg.

#### Formal mode

Formal mode extends ordinary mode with:

- a non-adoptable unique review ID;
- sanitized per-provider exports;
- hashes for packet, prompts, inputs, exports, and verdicts;
- provider preflight receipts generated by implemented wrapper behavior;
- structured verdict validation using a trusted bundled schema;
- dispatch and acceptance-time hash re-verification;
- provenance for requested and exposed runtime identities;
- an explicit resolution record for every finding.

Formal requirements will not appear in the skill until the corresponding
runtime command and tests exist.

### 3. Dispatch, argv integrity, and long-input handling

All machine-generated commands use argv arrays. No built-in path constructs a
shell command string. User-extensible auth probes, if retained, accept a JSON
argv array rather than arbitrary shell syntax.

Skills will instruct the leader to execute bundled helpers, not reconstruct
quoting by hand. The packet path, workspace path, provider export path, schema
path, and log path are each validated as canonical absolute paths under an
allowed root before dispatch.

Provider prompts identify archived source as untrusted review data. They require
reviewers to:

- read the brief and manifest completely;
- traverse the affected-code coverage ledger rather than stopping at the diff;
- cite archive-relative files and lines for findings;
- record files actually inspected;
- report an explicit coverage gap when a required file cannot be read;
- avoid commands, writes, network expansion, and live-worktree reads.

No arbitrary prompt-size constant is treated as proof of completeness. The
builder records byte counts and the verdict records coverage. Formal mode fails
closed when a required input or citation cannot be resolved.

### 4. In-session repair analyzer with deterministic persistence

Repair is a logical role, not a model-selection Custom Agent. The leader spawns
a fresh child with explicit model, reasoning effort, and `fork_turns="none"`.
The child reads a bounded redacted failure record and returns structured JSON:

- failure family;
- confidence and evidence;
- retryability;
- candidate classifier delta;
- required owner action, if any.

The analyzer is instructed not to edit files or invoke providers. When the
runtime does not mechanically expose a read-only guarantee, the record states
that containment is prompt-controlled.

Only `bin/apply_patch.py` (or a focused successor) may validate and persist an
allowed classifier delta. It enforces the schema, allowed keys, size limits,
locking, atomic replacement, and path containment. The LLM never writes the
classifier and never automatically retries an authentication failure.

## Review Orchestration

An ordinary three-family review launches all required independent legs against
identical verified packet bytes before persisting any verdict. The leader
reconciles evidence rather than votes.

A configured workspace authorization suppresses repeated sharing questions for
the same canonical scope and providers. The workflow interrupts the owner only
for:

- a new Critical or Major defect requiring a product decision;
- evidence-backed nonconvergence after fact checking;
- a required route that cannot be selected or completed;
- missing human authority outside the recorded scope;
- an authentication action that requires native provider interaction.

Ordinary security observations remain review findings and do not trigger a
separate consent loop. Formal mode still fails closed on packet mutation,
missing provenance, unresolved citations, or incomplete required legs.

## Package Integrity

Every packaged release includes a content manifest covering executable scripts,
skills, schemas, policies, and runtime helpers. Bootstrap and doctor compare the
installed tree with that manifest. The package version must change whenever a
manifested file changes.

The runtime report includes:

- plugin version;
- packaged manifest digest;
- installed-tree digest;
- source commit when available;
- installed path;
- whether source and installed bytes match.

A same-version digest mismatch is a hard configuration error. The workflow must
not silently combine a skill from one tree with wrappers from another.

## Error Model

Errors use stable families shared by doctor, wrappers, repair analysis, and
review orchestration:

- `auth`: native login, token, keychain, or OAuth action required;
- `sandbox-env`: inherited sandbox, missing environment, or inaccessible host
  credential boundary;
- `quota-capacity`: provider quota, rate, or capacity state;
- `version-config`: unsupported version, missing pin, policy, or incompatible
  option;
- `transport`: process startup, timeout, malformed output, or transcript
  extraction;
- `packet-integrity`: missing input, mutation, hash, citation, or closure
  failure;
- `review-finding`: a substantive product defect;
- `nonconvergence`: incompatible evidence-backed reviewer conclusions.

Each family declares whether deterministic retry is allowed. `auth`,
`packet-integrity`, and `nonconvergence` are never blind-retried.

## Testing Strategy

Every behavior change follows red-green-refactor. Required test groups are:

1. **Installer boundary tests**
   - installation performs no live provider calls;
   - static doctor is offline;
   - explicit live doctor preserves classified failures;
   - a successful installation remains successful when live verification
     later fails;
   - repeated install aliases terminate with bounded timeouts.
2. **Argv and hostile-input tests**
   - spaces, single and double quotes, backticks, `$()`, newlines, Unicode,
     leading dashes, and shell metacharacters survive exact round trips;
   - built-in execution paths never set `shell=True`;
   - launcher rules are checked against allowed and rejected command shapes.
3. **Packet tests**
   - staged, unstaged, committed-range, and untracked content is included;
   - unchanged impacted context and tests have coverage reasons;
   - symlink and allowed-root escapes fail;
   - mutation between build, dispatch, and acceptance fails;
   - large text files are fully hashed and citation-resolvable.
4. **Review workflow tests**
   - ordinary and formal contracts differ only by documented gates;
   - all legs receive identical packet and prompt hashes;
   - direct fresh Codex dispatch uses explicit model, reasoning, and
     `fork_turns="none"`;
   - unexposed runtime identity is recorded as unexposed;
   - standing workspace authority prevents redundant consent prompts.
5. **Repair tests**
   - analyzer output cannot persist directly;
   - invalid or overbroad deltas are rejected;
   - valid deltas are applied atomically under a lock;
   - authentication failures never enter automatic retry.
6. **Package and documentation tests**
   - source/package/cache manifests agree;
   - documented flags exist in parser help;
   - stale repair-agent and `fork_context` instructions are absent;
   - skills pass structural lint and fresh-context pressure scenarios.

Provider smoke tests are separate from the deterministic unit suite. They run
only through explicit owner-authorized live doctor or release verification.

## Documentation Structure

The cross-family review `SKILL.md` becomes a concise router and ordinary-mode
workflow. Formal packet details move to one directly linked reference file.
Fragile command construction moves to bundled scripts. README, SECURITY,
migration guides, Korean documentation, skill instructions, and bootstrap help
must describe one consistent runtime contract.

## Non-Goals

- Automating browser login, MFA, keychain access, or provider account changes.
- Storing credential values or copying credential files.
- Granting external reviewers write access.
- Treating requested Codex model values as independently verified when runtime
  identity is unexposed.
- Building a language-specific whole-program dependency analyzer in this
  plugin. The packet builder supports deterministic inventories and an explicit
  coverage ledger; project-specific static analyzers may contribute edges.
- Automatically sharing files outside a recorded canonical workspace scope.
- Replacing evidence reconciliation with majority voting.

## Delivery Decomposition

Implementation will be planned and reviewed as four sequential deliverables:

1. deterministic install/setup/doctor and argv transport;
2. immutable packet builder and ordinary/formal review contracts;
3. fresh Codex route and deterministic repair flow;
4. package manifest, documentation convergence, and end-to-end verification.

Each deliverable must be independently testable. A later deliverable may consume
an earlier interface but may not weaken an earlier safety or integrity gate.

## Acceptance Criteria

The redesign is accepted when:

- a clean install performs no provider call and exits deterministically;
- one owner-run setup records workspace-scoped standing authorization without
  storing secrets;
- a top-level doctor can distinguish login, sandbox/environment, quota,
  configuration, transport, and packet failures;
- ordinary review includes complete change state plus affected code context and
  no longer treats diff as the review boundary;
- formal review dispatches identical immutable bytes and validates provenance;
- fresh Codex reviewer selection uses the native model/reasoning/fork fields
  without a review-only Custom Agent;
- repair classification is available in-session while persistence remains
  deterministic;
- hostile path and prompt values survive exact argv transport;
- installed package bytes are attested and same-version drift fails closed;
- documentation and executable CLI surfaces agree;
- deterministic tests pass with bounded runtimes and live provider tests remain
  explicitly owner-triggered.
