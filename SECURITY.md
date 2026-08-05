# Security model

TRIAD coordinates external model families; it does not turn their output into a
trusted control plane. Its durable boundaries are explicit data authorization,
pinned executable paths, immutable-directory digests, mutation detection,
strict result custody, and deterministic owner apply.

## Native permission boundary

Provider, user, and project settings own permission selection and workspace
trust. TRIAD does not select or override a permission mode, strengthen or
weaken native authority, or insert yolo, bypass, accept-edits, dont-ask,
`--skip-trust`, or equivalent controls. Bootstrap does not install permission
profiles, command rules, or a pre-spawn `shell_environment_policy`.

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

Native AGY headless permission denial is terminal `permission-unavailable`. It
is distinct from authentication, quota, capacity, extraction, and
`truncated-answer`; it neither triggers a broader retry nor activates Gemini in
the same round. Gemini owns its workspace-trust decision after removal of
`--skip-trust`; TRIAD has no trust bypass or speculative detector.

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

## Google fallback boundary

AGY is the primary Google route. Version, executable, and model-catalog checks
happen before a formal round. If AGY is unavailable before submission, the
leader may select a separately authorized Gemini route before starting a fresh
round. Any result event, timeout, vendor failure, or schema failure is
post-submission and cannot activate a replacement inside that round.

Formal Gemini fallback requires separate owner authorization for the exact
route, provider, data boundary, and objective. It uses the same immutable
prepared directory, prompt-controlled no-edit/no-execution contract,
digest/mutation invalidation, complete three-family round, and strict
`LegVerdict` admission. An
unavailable required family leaves an invalid round. See the
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
