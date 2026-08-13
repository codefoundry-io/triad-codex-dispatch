# Security model

TRIAD coordinates external model families; it does not turn their output into a
trusted control plane. Its durable boundaries are explicit data authorization,
pinned executable paths, immutable-directory digests, mutation detection,
strict result custody, and deterministic owner apply.

## Native permission boundary

Formal Google review uses native AGY CLI sign-in with either personal Google
Sign-In or Gemini Enterprise Business Sign-In. Matching the deployed Claude-led
TRIAD, the wrapper brackets `--sandbox read-only` in a transient global-settings
transaction, unions the exact write/command/unsandboxed/URL/MCP deny set, and
restores the original bytes. Unless the operator sets
`AGY_NO_HEADLESS_AUTOAPPROVE=1`, AGY 1.1.3+ requires the wrapper-owned
`--dangerously-skip-permissions` headless adaptation, which voids deny and OS-ring
enforcement; formal review is therefore read-only by intent plus prepared-tree and
worktree mutation detection. Bootstrap installs no persistent global permission
policy, Enterprise authentication, or pre-spawn `shell_environment_policy`.

Run TRIAD from the same authenticated login terminal and project worktree used
for development. Trusted Python and `PATH` values are prerequisites. Wrapper
child-process scrubbing remains defense in depth after trusted startup: loader
and interpreter injection variables are removed only after the trusted launcher
and interpreter have begun. It is not a substitute for native permission or
project-trust selection.

Bootstrap pins the installer-selected Python. This is an explicit installation
and operation precondition, not a fully closed launcher guarantee:
credential-compatible/user-site mode requires a trusted `HOME` because
`sitecustomize.py`/`usercustomize.py` can run before launcher scrubbing. A
trusted isolated Python environment is acceptable only when it preserves the
provider login workflow.

Formal AGY calls use owner-provisioned personal or Gemini Enterprise native
sign-in and the same transaction lifecycle. TRIAD does not change the active AGY
account or workspace-trust decision.

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
body. Record one simple content digest before dispatch and compare it after every
required leg terminates. Reviewers do not execute candidate code, tests, builds,
hooks, or generated scripts.

Before a formal gate, classify every test failure as production defect,
test-case defect, or intentional specification change and resolve or approve it.

Each required family inspects the same complete focused directory once per
round. One strict `LegVerdict` binds the family, review ID, and content digest.
The immutable directory digest, canonical-worktree fingerprint, local schema
validation, independent family review, and leader reproduction protect result
integrity. They do not prove that a provider read every byte or choose runtime
permissions.

## Formal Google boundary

AGY is the formal Google reviewer for both personal Google Sign-In and Gemini
Enterprise Business Sign-In. Record the selected authentication class before
dispatch. AGY version, executable, model-catalog, and settings-transaction checks
happen before submission; its child removes known API-key, ADC, Vertex,
SDK-enterprise, cloud project/location/quota, and `AGY_ADC_AUTH` route selectors without reading
their values. TRIAD never changes or falls back between authentication classes.
Failure of the selected class invalidates the round. See the
[formal reviewer routing contract](skills/triad-cross-family-review/references/reviewer-routing.md).

## Installation, cleanup, and owner state

Bootstrap installs three provider wrapper launchers and prints the owner apply
argv. Install and remove perform exact plugin-owned legacy cleanup for old
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
