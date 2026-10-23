# Security model

TRIAD coordinates external model families; it does not turn their output into a
trusted control plane. Its durable boundaries are explicit data authorization,
pinned executable paths, immutable-directory digests, mutation detection,
strict result custody, and deterministic owner apply.

## Bundled shared library candidate

Explicit v2 uses the pinned generated `triad-dispatch-lib` package and verifies
its adoption inventory. Existing toolkit custody includes the package code,
resource manifests and adoption record. A changed dependency requires a fresh
review basis. The host retains native permission, terminal and output custody
guards; no provider permissions or authentication settings change.

Legacy formal metadata parsing and web-clause loading also transitively use the
shared parser and its inventory check. A damaged bundle therefore stops legacy
formal preparation or wrapper preflight before inference as well. Integrity
`RuntimeError` propagation is deliberate; its process failure is not a provider
verdict or evidence that the provider ran. Restore the verified distribution
through the normal update procedure before retrying.

The adoption hashes establish consistency with the reviewed build, not a signed
publisher identity. Third-party Python dependencies still use the selected host
runtime. Existing interpreter startup, user-site and bytecode-cache trust
boundaries continue to apply. Runtime imports never download dependencies.

## Native permission boundary

AGY read-only calls select explicit native read/search tools with
`excludeDefaultComponents: true` (CLI >=1.2.1). The research twin adds authorized
web tools. Legacy/v2 preflight binds name/path/hash; missing/drifted definitions
refuse before inference, and changes during execution withhold the result.
Dispatch never installs profiles. Explicit setup is described in
[installation](docs/installation.md#agy-review-profile-setup-pending-candidate).
The1.3.3 probe established actual read/search/web and no write after a requested
write. No write was attempted: it does not prove provider-enforced denial or a
universal permission boundary. Native plan/sandbox and result/integrity checks
remain separate. Inherited owner/project customizations are not disabled.

Formal Google review selects and freezes one route before any family starts.
AGY is preferred and personal Google Sign-In requires it. When the owner selects
Gemini Enterprise OAuth and AGY is absent, the selector may choose the already
authenticated Legacy Gemini CLI instead. This label distinguishes the `gemini`
executable from AGY; it does not change the `gemini-enterprise` authentication
class, version floor or preflight requirements. All AGY paths leave global settings and old backup/lock/lease files untouched.
There is no transaction, restoration or automatic crash healing. Requested web
only reads existing settings for a known URL-wide deny/malformed JSON; absent
settings stay absent. Explicit project records retain read-only validation.
All read-only calls omit headless autoapproval. Permissive raw calls retain the
version-gated adaptation unless `AGY_NO_HEADLESS_AUTOAPPROVE=1` opts out.
Public v2 binds standing web authorization. Legacy REVIEW defaults to no web; a
direct owner request may enable its bound all-leg
[review web option](skills/triad-cross-family-review/references/review-web.md). AGY profiles/prompts prohibit MCP calls.
The provider-managed sandbox is not OS-level
confinement, and round-integrity mutation detection is a separate fail-closed
check. The formal Gemini wrapper explicitly requests CLI Auto and native Plan
Mode, but records the effective approval mode as `unexposed`. Its exact
mode-independent packaged read/search-only user-tier policy is the enforcement
boundary: it denies writes, shell, Plan Mode transitions, and all other tools in
every mode; an enterprise admin policy remains a higher tier. Bootstrap installs
no persistent global permission policy, Enterprise authentication, or pre-spawn
`shell_environment_policy`.

Public v2 guarded Gemini calls add only their exact canonical managed `shared`
packet directory to the vendor workspace through `--include-directories`.
The preflight receipt and allocation bind this launch control; missing/changed
controls or invalid packet roots refuse before inference. Sibling receipts,
logs and results are not included. Product cwd, read-only policy and result
bindings remain unchanged; no user setting is edited.

The default selected B Gemini profile explicitly denies `google_web_search` and
`web_fetch`, retaining its 999/998 rule priorities and Plan Mode transition
denies. The wrapper checks the complete rule set, exact bytes and adjacent
`bin/policies/source-manifest.json` provenance. This is candidate payload adoption,
not a tagged spec revision. B1-B3 in the shared verification manifest remain
NOT RUN; a local preflight cannot prove effective admin-policy precedence.
AGY's default prompt also prohibits both `search_web` and `read_url_content`. The selected
profile and a successful local review do not attest how every vendor web tool
maps to permission actions; do not infer complete mechanical web denial from them.

Run TRIAD from the same authenticated login terminal and project worktree used
for development. The outer Codex host sandbox is separate from each provider's
native containment: Codex-launched TRIAD lifecycle, provider, test, and
development commands run outside the workspace sandbox under the user's selected
host policy. TRIAD does not install or mutate that host policy. Trusted Python
and `PATH` values are prerequisites. Wrapper child-process scrubbing remains
defense in depth after trusted startup: loader and interpreter injection
variables are removed only after the trusted launcher and interpreter have
begun. It is not a substitute for native permission or project-trust selection.

Bootstrap pins the installer-selected Python. This is an explicit installation
and operation precondition, not a fully closed launcher guarantee:
credential-compatible/user-site mode requires a trusted `HOME` because
`sitecustomize.py`/`usercustomize.py` can run before launcher scrubbing. A
trusted isolated Python environment is acceptable only when it preserves the
provider login workflow.

Source-SOT staging uses `TRIAD_BOOTSTRAP_CODEX_ROOT` to scope bootstrap's Codex
checks and provenance-managed cleanup without assigning `HOME` or `CODEX_HOME`.
It reuses the absolute-path and containment checks; it does not redirect provider
authentication or broaden permission to mutate a user-global target.

An explicit `--project <canonical-lowercase-UUID>` with `--cwd` and
`--sandbox read-only` selects an owner-provisioned AGY project record under
`~/.gemini/config/projects/<UUID>.json`. Before inference, the wrapper checks
its ID, its single cwd resource, and the five raw read-only deny entries. Default
no-web formal preflight and dispatch additionally require `read_url(*)`.
Explicitly requested review web retains the five raw denies and refuses an existing
`read_url(*)` deny before inference, preserving the owner's rule. Missing required
rules also refuse before inference. No route creates or edits global permission
or lease files; this path adds read-only project validation.
Additional project denies remain intact. Preflight and dispatch must select the
same UUID, bound through the existing hashed `route_args`; a paired Argon/Flash
review must use one project. The owner keeps the project configuration stable
during the call. This local check neither prevents arbitrary external
configuration edits nor proves runtime policy
attestation. Project provisioning remains an explicit owner operation.

The current fixed AGY review base requests `gemini-4-argon-high`/`high`; the paired
Flash member remains `gemini-3.8-flash-high`/`high`. Both preflight receipts and
the selected member remain bound in the common review digest. This requested
selection does not attest the provider's runtime identity or change permissions.
Raw and public v2 explicit model selection retain their existing validation.

Formal AGY calls use owner-provisioned native AGY CLI sign-in. Formal Gemini
calls preserve the existing organization Sign in with
Google/OAuth cache and Cloud-project selection while removing competing API-key,
ADC, and Vertex selectors without reading their values. TRIAD does not change an
active account or workspace-trust decision.

## Provider data and executable boundary

External dispatch requires explicit owner authorization for the provider,
destination, objective, and approved data. Exclude credentials, tokens,
cookies, authentication files, environment dumps, provider logs, and unrelated
paths. TRIAD neither issues nor copies credentials and does not run login or
model probes during install.

Wrappers build argv arrays, validate prompt and result paths, and pin the
install-resolved provider executable and classifier paths. These are data and
executable-custody controls, not provider or OS sandbox enforcement.

The local Claude wrapper sends the effective prompt as UTF-8 text on the provider's stdin, preserving JSON and native-schema output. Use `--prompt-file` to keep the prompt out of the outer wrapper command line too. Claude documents a [10MB stdin cap](https://code.claude.com/docs/en/headless#pipe-data-through-claude); the vendor enforces that cap and model context/token limits still apply. The wrapper does not truncate, split, or add requests to bypass these limits. The wrapper prepares the full UTF-8 input in an anonymous temporary file before launch. Preparation failure prevents launch; `stdin_delivery=complete` means availability to the CLI, not consumption. Early stdin closure alone is not a delivery failure. Stdin removes prompt text from the inner provider argv; argv lists already prevent shell expansion. Existing sensitive prompt and transcript logs remain, and stdin does not encrypt input, prevent prompt injection, or reduce token usage.

A zero provider exit is insufficient if output capture fails, contains invalid
UTF-8, or lacks a complete valid result. Capture diagnostics identify only the
stream and exception class. Separate anonymous output files are read as finite
snapshots after direct-child completion without changing shared offsets or
waiting for descendant EOF. Captured stderr remains confidential under existing
failure-artifact rules; it is not mirrored live. Best-effort wrapper display
failures cannot replace the result or replay a failed line.
Vendor descendants retaining output descriptors can keep writing to an unlinked
temporary file until those descriptors close; these later bytes are not wrapper
evidence, and their resource lifetime remains vendor-owned.

The wrapper terminates/reaps only its direct child on timeout/cancellation using
bounded waits. Vendor descendants and remote work remain vendor-owned. There is
no process-group sweep after normal exit, universal no-orphan guarantee, remote
cancellation guarantee or identical record across every signal window. This is
not OS containment. Cancellation cannot admit an answer even if the child exits with status 0.
AGY profile drift still withholds the answer; earlier timeout/provider failures
retain priority. No stronger provider permission boundary is introduced.
AGY's measured own stderr print-timeout line withholds raw and structured partial
answers at any vendor exit. A partial SUCCESS/exit0 envelope cannot suppress an
authentication STOP; existing wrapper-timeout and transport precedence remains.

## Guarded symlink review boundary

The leader records scoped link metadata/text in TASK before capture. Reviewers
inspect that bound evidence without traversing leaf or ancestor symlinks; target
content requires a separately authorized bound input. Missing necessary evidence
remains an open question. This restriction is prompt-controlled, not OS-level
path confinement. The link fingerprint does not bind external target contents.
Prepared-copy refusal and cleanup's existing no-follow checks remain in force.

## Repair boundary

The optional `fingerprint-worktree --require-clean-head` check constrains an
existing checkout's HEAD and Git-visible clean state at setup time. It neither
creates isolation nor changes reviewer permissions or AGY root binding. Ignored
files remain outside the claim; shared Git metadata and later mutations still
require normal review custody and final integrity verification. Never use a
different checkout to bypass protected changes in a governing worktree.

The common `transport` object adds execution metadata to existing audit and
failure-log envelopes, without prompt/page storage or a new log directory.
Catchable SIGTERM/SIGHUP on the wrapper main thread during child collection
uses scoped handlers, owned-group cleanup and existing failure persistence;
previous handlers are restored. It does not cover SIGKILL or host failure.
An attempted executable and probed version do not attest provider model identity,
authentication or successful interpretation. Delivery observations never replace
the primary timeout/vendor error. Existing masking and retention remain.

The optional audit `effective_cwd` records the host-resolved launch directory
only after a child starts. Hardened/redacted mode masks the entire path. It
shares existing private audit retention and is excluded from failure/repair IPC;
it does not attest the provider's later cwd or read coverage. No environment dump
is added. Existing unredacted streams and human stderr remain sensitive.

AGY plan-mode `agy_read_telemetry` counts observed DONE view_file tool events,
including repeated or failed reads. It projects only up to 128 unique relative
paths (1024 valid-UTF-8 characters each) currently resolving inside that captured
cwd; malformed/relative/`..`-containing/outside/symlink-escaping paths are omitted.
It retains no tool output, error, unrelated argument or provider identifier. Redacted/hardened
audit retains only the count. The projection cannot change a verdict and is
excluded from result and failure/repair IPC. It is neither coverage/permission
proof nor historical filesystem attestation; existing raw-stream custody and
private audit retention remain unchanged.

Claude's optional audit `claude_receipt` projects only validated session/model
identifiers, bounded numeric usage/cost estimates, and an array-length denial
count (omitted above 1,000,000). It never copies tool arguments, denial objects,
answer text or arbitrary envelope fields into that receipt. Redacted audit mode
omits the session and entire model map. This projection does not sanitize the
existing unredacted streams or failure run logs; those remain sensitive under
the existing retention policy. Receipt persistence is advisory and does not
control classification, retries, model attestation or review admission.

Vendor run logs are untrusted. Repair analysis uses a fresh native proposal-only
child with prompt-controlled no-edit behavior. The child receives an absolute
run-log path as data and returns only a proposal or escalation; it cannot apply
a classifier change.

Bounded AGY terminal-error summaries remain untrusted diagnostic data under the
existing audit redaction and failure-log retention rules; they do not drive
classification, retries, or admission.

The leader stores a proposal in one unique UTF-8 JSON file. Bootstrap prints a
direct owner argv using Python `shlex.join` for login-shell
`python3 bin/apply_patch.py --cli <cli> --proposal-file <absolute-path>
--classifier-file <pinned-absolute-path>`. The explicit classifier path is the
same install-resolved path pinned into provider launchers. There is no installed
apply launcher and no ambient-default recomputation. The deterministic apply
path validates the proposal before mutation; invalid input leaves classifier
state unchanged.
All `oauth-env` proposals are refused before storage access; the user handles
authentication recovery. Existing valid curated entries retain their loading behavior.
The extension loader ignores unsupported vendor-exit classes and exit-zero
entries with a diagnostic; it preserves valid siblings and never rewrites the
file. Existing curated authentication remains separate from new-proposal refusal.
The applier keeps semantic checks, locking and atomic replacement, without
reason-length or per-CLI entry-count caps.
The same CLI's `--verify-run-log` mode reads a saved eligible failure and the
explicit classifier file without mutation or vendor execution. Recorded argv
are data, not commands. A match proves classification only; unusable evidence
or mismatch is reported, and never grants review admission. Unchanged classes
and transport failures that bypassed runtime classification cannot verify a learned
repair. Retained nonzero vendor diagnoses follow the existing runtime path. Timeout and auth
recovery do not enter phrase repair.

That coarse proposal validation is not semantic proof. Fine-grained substring
specificity and residual misclassification remain analyzer and owner
responsibility.

Wrapper-launcher command groups use the existing staged transaction and roll
back caught publication failures. This is not crash-atomic publication: a killed
writer may leave temporary links or a mixed group requiring reviewed recovery.
Normal shared mode preserves retired repair artifacts; exact cleanup is limited
to isolated source-SOT staging. See [interruption recovery](docs/shared-runtime.md#interrupted-publication-or-unexpected-files).

## Review and coverage boundary

Formal plan and pre-merge three-family gates use one leader-prepared shared
review directory containing current approved production source, configuration,
and documentation. The exact project or owner boundary determines test-source
exclusions; absent that exact boundary, dispatch stops for owner input. Normal
SDD implementation review includes
relevant test source; other advisory review uses its separately owner-approved
data scope.

The prepared directory and round-owned `results/_logs` live in a mode-0700 root
under the reserved `triad-review-` system-temp namespace. Cleanup and stale sweep
require an external allocation record and reverified evidence export. Unknown,
unexported or changed roots are preserved; a proven partial claim can resume.
Stale eligibility remains strictly more than 30 days without activity. Export
retains symlink text without following targets. All writers must be terminal and
one leader must clean an allocation at a time; same-UID forgery or concurrent
open-FD mutation is not contained. See [recovery](README.md#review-evidence-cleanup).
Formal wrapper `--cwd` and `--prompt-file` paths therefore live under that root.
When `TRIAD_WRAPPER_ALLOWED_ROOTS` is configured, it must include the canonical
system temp base, including when hardened mode requires the setting.

Every leg receives the same directory and task. No prompt inlines a diff or file
body. The prepared-directory digest protects packet bytes; the renderer binds it,
every common review condition, and the Google receipts into one result-admission
content digest shared by every family. Both renderers bind the exact renderer
and schema file hashes, so toolkit changes require a new basis. Compare both
packet integrity and result bindings after every
started leg terminates. In a partial-start round, record the actual start failure and each remaining
required leg as not started because launch was closed before comparison. Reviewers do not execute candidate code, tests, builds,
hooks, or generated scripts.

Before a formal gate, classify every test failure as production defect,
test-case defect, or intentional specification change and resolve or approve it.

Each required family inspects the same complete focused directory once per
round. One strict `LegVerdict` binds the family, review ID, and route-bound content digest.
The immutable prepared-directory digest, canonical-worktree fingerprint, local schema
validation, independent family review, and leader reproduction protect result
integrity. They do not prove that a provider read every byte or choose runtime
permissions.

Once any provider leg has started, a later required-leg start or result failure invalidates
admission but already-started sibling families finish. Their structurally valid
results remain provisional until post-review integrity succeeds; valid findings
are advisory only and must be reproduced. They never admit the failed round or
supply admission credit to a later round. The leader must correct the classified
failure or verify recovery from a transient vendor incident, and correct every reproduced in-scope defect before a fresh complete round.

## Formal Google boundary

Record `personal-google` or `gemini-enterprise` before dispatch, then use the
packaged selector receipt. Personal Google requires AGY. Enterprise prefers AGY
and chooses Gemini only when AGY is absent. The exclusive-created receipt binds
the review ID, authentication class, route, canonical executable, wrapper, and
SHA through selected-wrapper preflight, every render, and dispatch. The canonical
preflight receipt repeats the review ID, route, executable, and selector SHA; its own
SHA, exact model, and nullable effort are bound into every family digest, and every
render and dispatch rejects a mismatch. The selected wrapper executes the receipt
executable directly. Its provider-free preflight finishes before any family starts;
the route is then immutable. AGY
version, executable, bound-profile and optional project checks precede submission.
Requested web also checks for known existing local settings conflicts without writes. Gemini preflight probes the receipt binary's `--version` before help,
with a maximum 15-second version timeout and the same scrubbed environment. It
requires SemVer >=0.63.0 and records the exact `gemini_version` in the bound
receipt; malformed, missing, failed or unsupported versions refuse before inference.
Gemini preflight also validates the model/Plan Mode/policy
CLI surfaces, and mode-independent packaged policy without a model call. It
records a SHA-256 of the same policy bytes it validates; render and dispatch
reject a missing or stale policy hash. This binds policy bytes, not effective
runtime settings. It records requested Plan Mode and effective mode `unexposed`; the policy, not a
speculative settings or trust probe, supplies the fail-closed read-only boundary.
Raw Gemini calls check the same version floor before provider submission.
An unsupported or unprobeable version returns local refusal exit 3. Upgrade
versions below 0.63.0; otherwise diagnose the selected executable before a new
invocation. No model-list probe gates Google preflight, render or dispatch;
the standalone diagnostic catalog inventory remains informational.
The current Gemini JSON route records literal `runtime_identity: "unexposed"`;
it does not infer a single model from `stats.models`. Neither route falls back after
provider start, auth failure, capacity failure, or invalid output. Failure of the
selected route invalidates the round. See the
[formal reviewer routing contract](skills/triad-cross-family-review/references/reviewer-routing.md).

## Installation, cleanup, and owner state

The shared runtime authenticates full consumer bindings, installation receipts,
retained toolkit inventories and generated launchers before selecting a target.
The supported direct AGY migration verifies its complete pinned runtime baseline
and hardened AST; an AGY marker alone never establishes ownership. The ordinary
Codex managed-command recognizer retains its stricter ownership boundary.
Partial or mixed command groups and explicit unknown bindings refuse without
fallback. See [compatibility boundaries](docs/shared-runtime.md).

Bindings cover exact toolkit and classifier paths, interpreter/provider pins,
trusted PATH and launcher bytes. Classifier contents remain mutable. Public v2
authenticates and seals the installed context once; retries and collection do
not follow the latest installation receipt. Native spawning remains host-owned.
Snapshots do not attest external interpreters, user-site packages, provider
binaries or credentials. Original AGY targets and pre-migration direct rounds
still depend on their original installations.

Publishing four common entry points plus an installation receipt uses rollback
on failure, not simultaneous atomic replacement of every path. Prior bindings
and assets remain retained. Shared removal unregisters the selected receipt;
unknown dependencies cause conservative retention rather than asset deletion.
Independent older AGY installers/removers remain outside that guarantee.

Bootstrap installs three provider wrapper launchers plus one review-round
selector launcher that supplies both install-resolved Google executable pins,
and prints the owner apply argv. Normal shared install/remove does not clean up
global shell or Codex configuration, including exact legacy-managed fragments.
Those fragments may remain for separately authorized cleanup. The existing
isolated source-SOT branch retains exact plugin-owned cleanup for old
profiles, command rules, repair-agent registration, pre-spawn
`[shell_environment_policy]` fragments, legacy agent TOMLs, and retired
launchers only when their marker and expected content match. Foreign, edited,
linked, unreadable, or non-regular targets are preserved and reported.
Legacy agent ownership requires the SHA256 of the complete file to match a known
unchanged-copy original. Headers alone do not establish ownership. Unknown or
machine-rendered variants are preserved with the existing unmanaged-file warning.

Owner-authored `config.toml`, rules, permission profiles, provider settings,
credentials, and unrelated files are preserved. Cleanup never follows a link
and never removes an owner file merely because no managed bytes remain.

Commit, push, install/update, merge, tag, release, publication, and every new
provider/data boundary require their own owner authorization. Native permission
success is not workflow authority.

## Disabled AGY hook helper

The packaged `bin/agy_hook.py` only evaluates a fixed tool-name allowlist and
prints decisions or an always-disabled configuration. It never executes the
requested action, follows payload paths, records input, or installs policy.
Its bounded JSON adapter rejects malformed, duplicate-member, oversized and
over-64-container-depth input (root counts as one); a name allowance is not
path/content/egress containment.

The explicit `allow` decision may interact with existing permissions. Do not
enable the helper without separate authorized live proof of discovery, normal
reads, off-list denial without effects, and preservation of existing deny rules
at the exact target UUID/cwd. Offline tests prove only the helper contract.
Helper crash/timeout handling is not certified as fail-closed. The helper is
outside verdict transport and admission; bootstrap and wrappers do not wire it.

The disabled renderer's bare `python3` must be replaced with a verified trusted
absolute interpreter before authorized activation. Matcher `*` covers every
tool call in that enabled session: prove complete review completion while
off-list tools remain denied. Include oversized-input stdin-write/broken-pipe
and helper process-failure outcomes in the live proof; a local deny response
does not by itself establish the provider's enforcement.

## Raw verdict-file member validation

The canonical regular-file reader still reads once. `validate_verdict_file`
rejects duplicate decoded member names at any object level before passing the
same raw bytes to strict schema and identity validation. Duplicate errors do
not reflect names or values; decoder recursion failure follows the existing
invalid-result CLI path. Canonical wrapper admission checks the original answer
and native envelope/event JSON before success, preserving primary failure
precedence and malformed AGY-noise handling. Both reserved schema spellings
(`verdict_schema:LegVerdict`, `verdict_schema.LegVerdict`) use the packaged file
loader and require complete expected bindings before dispatch. Arbitrary schema
imports retain their hardened opt-in. Schema-free raw replies, direct custom-schema
validation and other providers' custom-schema handling retain their existing behavior. No
provider re-ask, permission change or broader transport guarantee is introduced.
A result-file reader alone cannot recover evidence discarded by another caller.

AGY schema admission, including legacy and custom schemas, strictly parses original
JSON object event lines before metadata separation. Duplicate members and non-finite
numbers are rejected in intermediate events as well as the terminal event; existing
malformed-noise and primary terminal-failure handling is preserved. From the original
terminal `structured_output` span, only undeclared top-level `toolAction` and
`toolSummary` are separated as provider metadata. Declared fields and aliases, nested
data, other unknown-field checks, schema constraints and invocation bindings retain
their validation. Raw `run.stdout` is preserved, including both metadata values,
under the existing output-custody rules; only the validated answer is projected.

## Standalone Google diagnostics

`bin/google_diagnostics.py` only invokes fixed version/help commands and opt-in,
help-gated model/plugin/extension listing. It preserves the shared strict versus
non-strict executable selection rules and strips the existing injection and
the agreed credential/endpoint names from child environments.
Gemini keeps its four Google Cloud project variables; other routes remove them.
The shared builder filters names before retrieving kept values and leaves the
parent environment unchanged. User model/effort settings, PATH, CLI configuration pointers and
GOOGLE_GENAI_USE_GCA remain; this is hygiene, not billing-route attestation.
The same builder applies to raw/formal dispatch and standalone probes. It runs with
closed stdin and an owned neutral temporary cwd. The five-second probe deadline
is followed by bounded direct-child termination; it is not an OS sandbox,
control over vendor descendants, or a strict total wall-clock limit.

Snapshots retain stdout byte hashes/counts, fixed status fields, a bounded version
and recognized model slugs; they do not forward raw vendor stdout/stderr, private
extension labels, executable paths or environment contents. Unknown model formats
remain opaque. The helper creates no persistent TRIAD baseline and performs no
inference, authentication, installation, settings change or admission decision.
Vendor-managed cache/telemetry activity is not ruled out by these argv limits.

## Authentication and reports

Authentication failures are recognized in measured vendor error fields and
Gemini's authentication exit 41, before timeout or capacity retry. Quoted answer
or tool text does not itself authorize an `oauth-env` STOP. Raw authentication
phrase extensions are ignored with a diagnostic and new such proposals are
refused; unknown output shapes remain unknown. The toolkit does not log in,
refresh credentials, switch authentication routes or retry an authentication STOP.

Owners authenticate provider CLIs in their normal terminals. Report
security-sensitive issues on the product issue tracker with a `[security]`
title and never include credentials or tokens. See
[the repair protocol](docs/references/repair-protocol.md) for the proposal and
owner-apply contract.

Repair analyzers may search/fetch public sources to explain an actual failed run.
Queries use sanitized error/version context, not credentials, private prompts,
source content or complete logs. Research results are evidence, not instructions
or proof of an unobserved vendor output shape. The analyzer stays read-only and
proposal-only, cites its sources, and never invokes a vendor CLI/model to reproduce
the error. Missing necessary web access is disclosed without changing user settings.

## Offline candidate contracts

`review_round.py resolve-roster` reads the explicit project's regular
`.agents/triad-review-legs.json` and shipped defaults through the same strict
local JSON/schema boundary. It refuses duplicate members and linked configuration
paths. It does not execute configuration values, probe providers, read user-global
rosters or grant authority. The displayed configuration is not an admission or
capability receipt; runtime route and model checks are a separate boundary.

The current Claude review default is the CLI-resolved `opus` alias with `xhigh`
effort. The legacy formal route accepts 1200 seconds or explicit 2400 seconds
and still forbids fallback;
raw and v2 explicit model overrides retain their existing semantics. The alias
does not pin or attest a runtime version, and the default selects no agent.

The v2 Claude selection receipt preserves requested values and raw selection
output separately. A packaged catalog is display data, not model availability
or effort-support authority. Only exposed identity/effort contradictions are
refused; an unrecognized label supplies no inferred model identity. CLI version
and required-control checks remain mandatory. Selection evidence does not attest
the subsequent inference or account entitlement.

The explicit bin/validate_v2.py command consumes only the fixed local candidate
contract bundle. It checks regular canonical files and manifest digests, rejects
duplicate original JSON members before parsing loses them, validates all six
expected invocation fields, and uses an explicit empty jsonschema reference
registry. It neither fetches remote schemas nor resolves file URI references.
The source-commit/hash manifest detects inconsistent local payloads; it is not
tamper resistance against an actor able to replace the entire distribution.
The candidate does not alter installed revision pins, legacy review admission,
provider permissions or raw investigation routes. Bootstrap requires the declared
schema APIs before persistent writes and never installs Python packages itself.

The v2 Claude clause permits existing host-provided read/search tools,
including read-only shell inspection; candidate
code/tests/builds, writes and unauthorized reads remain prohibited. This grants
no new provider tool or permission.

Explicit v2 operational collection uses immutable named-entry/attempt custody
within the existing managed review lifecycle. It binds the complete roster,
source/toolkit, clauses, normalized review phase, selected route, requested
controls and capability receipts. Invalid phases refuse before capture/preparation;
every selected enabled entry must explicitly approve. CLI collection checks the actual wrapper argv, per-attempt run-log
ownership and raw stdout/stderr; native collection uses host terminal metadata
and original final-message bytes. Never accept model-authored host receipts.
Unexposed observations remain null, separate from observed empty sets.
An available preflight version is not copied into an unexposed runtime version.

The same existing raw run-log format is retained for explicitly bound v2 review
success as well as failure under caller-configured per-attempt roots. It may
contain task-sensitive provider output and is exported/cleaned with owned review
evidence. Ordinary raw/legacy success does not gain full-output logging. Audit
redaction, failure diagnostics, provider permissions, no-follow custody and
export-before-cleanup remain in effect. Original host-file mutation invalidates
collection. These hashes detect drift, not an actor rewriting all custody.

## Explicit web permission

Public v2 explicitly binds `review_web_authorized` from the owner's standing
authorization, currently true. Only recorded owner revocation changes the source
policy constant; caller booleans cannot override it and other types refuse.
An absent condition in a previously bound record means false. Legacy remains
per-request, default false. This is never a persistent roster permission. All CLI review invocations require matching
metadata and preflight. Claude adds only native WebSearch/WebFetch preapproval;
AGY selects the web profile and preserves owner settings; Gemini selects the
complete `gemini-formal-web.toml` plus `web-source-manifest.json`, differing only
in its two web tools. Its default profile remains unchanged. Native Codex uses
existing host web capabilities; permission does not create a missing tool.
Authenticated Gemini web checks remain NOT RUN. No permanent policy is installed.

## Explicit web investigations

AGY `--web` requires `--sandbox read-only`. In REVIEW it must match the current
bound authorization and preflight. It does not relax any pre-existing owner deny rule.
On the raw route it appends the single vendored investigation clause after validating the caller
prompt and operation. Missing or malformed clause content fails before provider
work. The prompt manifest and distribution checks track copied source bytes;
they do not attest runtime tool permission or factual correctness. Existing
settings/project guards, audit masking and failure-log custody are unchanged.

Gemini raw `--web` appends that same clause with Gemini tool names. It changes
neither native permission policy nor authentication. All raw wrappers accept
explicit `--add-dir` inputs with entry-cwd/root validation; REVIEW refuses the
unbound expansion. Native directory grants are not filesystem read-only
enforcement. Success path evidence and refusal candidates use existing audit
masking, without adding permanent prompt/page storage or changing failure IPC.

### Wrapper retry boundary

A wrapper dispatch starts inference once. Capacity or local schema-validation
failure does not replay the workload; existing64/66 outcomes and captured evidence
are returned. Vendor-internal retries and explicit diagnosed review-level retries
are separate. Authentication STOP, transport failure and review-binding validation
remain authoritative; no user setting or native-leg policy changes.
