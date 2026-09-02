# Security model

TRIAD coordinates external model families; it does not turn their output into a
trusted control plane. Its durable boundaries are explicit data authorization,
pinned executable paths, immutable-directory digests, mutation detection,
strict result custody, and deterministic owner apply.

## Native permission boundary

Formal Google review selects and freezes one route before any family starts.
AGY is preferred and personal Google Sign-In requires it. When the owner selects
Gemini Enterprise OAuth and AGY is absent, the selector may choose the already
authenticated Gemini CLI instead. Matching the deployed Claude-led TRIAD, the
AGY wrapper brackets `--sandbox read-only` in a transient global-settings
transaction, unions the exact write/command/unsandboxed/URL/MCP deny set, and
restores the original bytes. Unless the operator sets
`AGY_NO_HEADLESS_AUTOAPPROVE=1`, AGY 1.1.3+ requires the wrapper-owned
`--dangerously-skip-permissions` headless adaptation. Headless auto-approve
removes interactive approval prompts but does not remove explicit deny entries.
On the AGY route, MCP calls are denied; conditionally authorized external evidence uses the AGY
native official-web read path. The provider-managed sandbox is not OS-level
confinement, and round-integrity mutation detection is a separate fail-closed
check. The formal Gemini wrapper explicitly requests CLI Auto and native Plan
Mode, but records the effective approval mode as `unexposed`. Its exact
mode-independent packaged read/search-only user-tier policy is the enforcement
boundary: it denies writes, shell, Plan Mode transitions, and all other tools in
every mode; an enterprise admin policy remains a higher tier. Bootstrap installs
no persistent global permission policy, Enterprise authentication, or pre-spawn
`shell_environment_policy`.

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

Formal AGY calls use owner-provisioned native AGY CLI sign-in and the same transaction
lifecycle. Formal Gemini calls preserve the existing organization Sign in with
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

## Repair boundary

Vendor run logs are untrusted. Repair analysis uses a fresh native proposal-only
child with prompt-controlled no-edit behavior. The child receives an absolute
run-log path as data and returns only a proposal or escalation; it cannot apply
a classifier change.

The leader stores a proposal in one unique UTF-8 JSON file. Bootstrap prints a
direct owner argv using Python `shlex.join` for login-shell
`python3 bin/apply_patch.py --cli <cli> --proposal-file <absolute-path>
--classifier-file <pinned-absolute-path>`. The explicit classifier path is the
same install-resolved path pinned into provider launchers. There is no installed
apply launcher and no ambient-default recomputation. The deterministic apply
path validates the proposal before mutation; invalid input leaves classifier
state unchanged.

That coarse proposal validation is not semantic proof. Fine-grained substring
specificity and residual misclassification remain analyzer and owner
responsibility.

Wrapper-launcher command groups continue to publish all-or-nothing through the
existing staged transaction. That publication contract is separate from
retired repair-agent cleanup, so failure does not expose a partial launcher
group.

## Review and coverage boundary

Formal plan and pre-merge three-family gates use one leader-prepared shared
review directory containing current approved production source, configuration,
and documentation. The exact project or owner boundary determines test-source
exclusions; absent that exact boundary, dispatch stops for owner input. Normal
SDD implementation review includes
relevant test source; other advisory review uses its separately owner-approved
data scope.

The prepared directory and round-owned `results/_logs` live in a mode-0700 root
under the reserved `triad-review-` system-temp namespace; normal cleanup removes
completed roots exactly, while an interrupted root can persist until a later
prepare removes it after strictly more than 30 days.
Formal wrapper `--cwd` and `--prompt-file` paths therefore live under that root.
When `TRIAD_WRAPPER_ALLOWED_ROOTS` is configured, it must include the canonical
system temp base, including when hardened mode requires the setting.

Every leg receives the same directory and task. No prompt inlines a diff or file
body. The prepared-directory digest protects packet bytes; the renderer binds it
with the canonical Google selector receipt into one result-admission content digest shared by
every family. Compare both packet integrity and result bindings after every
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
version, executable, exact tabular model-catalog, and settings-transaction checks precede
submission. Gemini preflight validates the receipt binary, model/Plan Mode/policy
CLI surfaces, and mode-independent packaged policy without a model call. It
records requested Plan Mode and effective mode `unexposed`; the policy, not a
speculative settings or trust probe, supplies the fail-closed read-only boundary.
The current Gemini JSON route records literal `runtime_identity: "unexposed"`;
it does not infer a single model from `stats.models`. Neither route falls back after
provider start, auth failure, capacity failure, or invalid output. Failure of the
selected route invalidates the round. See the
[formal reviewer routing contract](skills/triad-cross-family-review/references/reviewer-routing.md).

## Installation, cleanup, and owner state

Bootstrap installs three provider wrapper launchers plus one review-round
selector launcher that supplies both install-resolved Google executable pins,
and prints the owner apply argv. Install and remove perform exact plugin-owned legacy cleanup for old
profiles, command rules, repair-agent registration, pre-spawn
`[shell_environment_policy]` fragments, legacy agent TOMLs, and retired
launchers only when their marker and expected content match. Foreign, edited,
linked, unreadable, or non-regular targets are preserved and reported.

Owner-authored `config.toml`, rules, permission profiles, provider settings,
credentials, and unrelated files are preserved. Cleanup never follows a link
and never removes an owner file merely because no managed bytes remain.

Commit, push, install/update, merge, tag, release, publication, and every new
provider/data boundary require their own owner authorization. Native permission
success is not workflow authority.

## Authentication and reports

Owners authenticate provider CLIs in their normal terminals. Report
security-sensitive issues on the product issue tracker with a `[security]`
title and never include credentials or tokens. See
[the repair protocol](docs/references/repair-protocol.md) for the proposal and
owner-apply contract.
