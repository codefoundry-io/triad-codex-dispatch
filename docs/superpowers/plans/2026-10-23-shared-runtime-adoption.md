# Shared runtime adoption and Codex 0.2.564

Owner authority: implement, merge and deploy; library plus Codex implementation,
with Claude and AGY follow-up notices. The library plan's complete formal gate
and published dev6 artifacts precede implementation of this plan.

## Outcome and scope

One generic launcher group supports the established AGY consumer and explicitly
selected Codex consumers. Preserve existing bare AGY behavior, host-native
execution, authentication, classifier locations, CLI arguments and receipts.
Codex updates/removal retain assets needed by existing consumers and rounds.
Implement C81-C83 for this supported migration; independent old AGY installers
and Claude adoption remain owner-maintainer follow-ups, not certified behavior.

Work in the selected Codex checkout; preserve its intentional untracked files.
Create a normal branch from current origin/main in that checkout after checking
tree equality. No reset, clean, stash, separate checkout, or other-host edits.

## Global Constraints

- Python remains 3.12+. Use published dev6 wheel/source/manifest pins; retain
  library content verification and unchanged schemas/provider defaults.
- All Python/tests/build/Git mutations/provider commands use literal
  `/bin/zsh -lic` with `sandbox_permissions="require_escalated"` first, from
  `/Users/chaniri/codex_workspace`; use the task-owned canonical TMPDIR.
- `TRIAD_RUNTIME_BINDING` is an optional explicit library-derived binding ID.
  Missing context uses only the previously established legacy binding; invalid,
  unknown or ambiguous context refuses before execution. Never infer host from
  installer name, CODEX_HOME, PATH order or the number of installed consumers.
  On an empty four-command directory, an explicit Codex installation establishes
  its first Codex default; this is an installation action, not runtime inference.
- Immutable binding identity covers artifact/baseline/library/adapter/capability
  identities plus exact toolkit path, generated launcher bytes, Python/provider
  pins, trusted PATH and classifier path. Classifier contents stay mutable under
  their existing policy; no new classifier content pin.
- Existing ownership and safe-file/ancestor rules remain. Recognizing an AGY
  marker alone never authorizes replacement. Verify the complete hardened AST,
  coherent four-command context and supported full runtime manifest.
- Preserve strict toolkit/receipt checks. Installed operations resolve once to
  one authenticated retained toolkit and use that root for every lifecycle,
  render, helper, provider and reference access throughout the round.
- Source-SOT bootstrap retains the existing isolated direct-source path and
  bypasses installed receipts/shared registration. Conflicting explicit shared
  context with source-SOT mode refuses.
- Snapshot and generation assets are immutable and retained conservatively;
  use library retention with dependencies_known=False. No GC, process registry
  or refcount. Remove only the exact caller installation receipt; other bindings,
  launchers and retained assets remain usable.
- Do not mutate global shell, Codex permission/model settings or other-host
  source/install configuration as an incidental migration effect.
- The root leader alone edits SKILL/instructions and their behavior scenarios.
  Dedicated fresh triad-skill-executor RED/GREEN is required. Workers own only
  assigned implementation/tests; no recursive agents.

## Design and interfaces

Shared root defaults to `~/.local/share/triad-dispatch-runtime`. Keep immutable
snapshots, bindings and generations beneath it. Codex-owned installation receipts
live beneath `~/.local/share/triad-codex-dispatch/installations`. Provide explicit
test-only/root override seams following existing bootstrap conventions; do not
allow inherited execution environment to redirect an installed generation.

`bin/shared_runtime.py` owns host verification and CLI. Library APIs own pure
description validation, canonical binding identity, compatibility, selection and
retention decisions. Avoid a second copy of those semantics.

Suggested interfaces (names may be adjusted coherently):

- `verify_legacy_group(paths, baseline)` verifies regular files, safe ancestors,
  AST, pins, toolkit assets and exact reviewed AGY baseline.
- `create_codex_binding(toolkit, launch_context)` builds a retained snapshot and
  pinned hardened per-consumer launchers; these remain independent of the plugin
  cache. Exclude runtime logs/debug/cache without inspecting their contents.
- `stage_generation(existing, codex_binding, legacy_binding)` preserves all
  verified prior bindings and the established legacy default. Refuse unknown
  generation state instead of dropping it.
- `resolve_installed_runtime(plugin_root, explicit_binding=None)` authenticates
  a receipt, exact canonical plugin root, artifact/binding and snapshot identity;
  return binding_id, toolkit_root, launcher_dir and provenance. CLI:
  `shared_runtime.py resolve --plugin-root ROOT [--binding ID] --json`.
- `publish_installation(...)` preflights all mutable targets and uses existing
  stage/publish_to/finalize_transaction rollback primitives for the four entry
  points plus receipt. Keep ordinary Codex ownership recognition strict.
- `remove_installation(...)` removes only the matching receipt and emits the
  conservative retention result.
- `dispatch(generation, command, argv, environ)` verifies the generation and
  chosen binding, consumes the selector and execs that binding's original
  hardened launcher with preserved argv/stdin/stdout/stderr/exit semantics.

Installation receipts are anchored to the exact canonical plugin root and
context. A single matching authenticated receipt is sufficient; distinct
contexts for the same root refuse ambiguity unless a matching binding is
explicitly selected. Reinstallation of the same canonical root and same context
reuses its matching receipt. A changed version/root creates a new receipt and
keeps the prior receipt, binding and snapshot; absence of an old root does not
authorize automatic cleanup. A round resolves once and retains that
binding even after the receipt or plugin cache is removed.

| Existing four-command group | Installation transition |
| --- | --- |
| All absent | Establish new Codex binding as first legacy default |
| Verified direct Codex | Retain original payload/target as legacy; add snapshot Codex binding |
| Verified supported AGY | Retain original payload/target and AGY default; add Codex binding |
| Verified shared generation | Preserve all bindings/default; add or reuse Codex binding |
| Partial, mixed or unverified group | Refuse without modifying it |

For a direct Codex migration, a pre-migration round already bound to the old
cache still requires that original cache. Never rewrite its receipts to a new
path. Cache-deletion survival applies to rounds started using a retained binding.
This limit, like independent legacy AGY removal, is explicitly outside this
release's supported lifecycle migration and must appear in the instructions.

Avoid digest cycles: source asset manifest determines snapshot ID/path; then
actual snapshot path, generated launcher bytes and context determine binding ID;
dispatcher/library code manifest determines runtime artifact_digest; finally
runtime metadata and supported bindings determine generation ID/path. Neither
an identity nor a generated path containing it enters its own hash input.

The neutral entry point pins its generation path and interpreter, has an exact
recognized grammar and startup environment isolation, and does not import code
from mutable CWD/PATH. Generated Codex child execution disables new bytecode
cache creation where possible without weakening current interpreter isolation;
legacy AGY payload remains unchanged. External interpreter/site-packages/provider
executable lifecycle is not authenticated by a source manifest.

The supported AGY source baseline is commit
`00f255826e894b82105d2b32e68b209d761f964b`. Evidence is
`_runs/20261023-shared-runtime-implementation/agy-legacy-baseline.json` in the
workspace. Publish only portable runtime inventory, source identity and limits,
not workstation-specific paths or unrelated observations. Inventory is 80 files,
canonical SHA256 `1b40aaf00c786a4595333a0d389cb6fba5d51ee002dc04f8e1c2add7500a6d83`.

## Task 1: Library adoption and shared runtime implementation

One implementer owns bin/shared_runtime.py, portable baseline data,
bin/bootstrap_repair.py, scripts/bootstrap.sh, bin/review_round_v2.py,
bin/review_adapters_v2.py and Google preflight context plumbing where required,
library-adoption pins/vendored files, and focused bootstrap/shared-runtime tests.
Keep native spawning semantics and receipt schemas unchanged; carry the
authenticated installed execution context through CLI preparation/allocation.
Stage tests first, observe RED, implement minimal
behavior and run focused GREEN. Do not edit source skills, instructions or
version metadata (leader owned).

Public-v2 currently allocates direct `python3` wrapper calls with vendor/log
variables only. Installed operation must add an optional explicit binding input
to the host request, authenticate and seal the immutable binding reference/digest
in the basis, and verify it against TOOLKIT on every load/retry without consulting
the latest receipt. Do not trust a caller-supplied environment dictionary.
An installed CLI allocation executes the immutable per-binding hardened launcher
directly; it does not depend on inherited environment or the latest generic
entry point. The expected run-log wrapper command is independently derived as
`[actual_retained_wrapper, *wrapper_args]`; preserve exact equality and original
arguments instead of assuming `invocation.argv[1:]`. Native allocation retains
its existing behavior. Source-SOT retains direct source calls.

Provider capability/preflight probes must use that same pinned context and
existing subprocess/timeout engine. Carry runtime_context through preparation
and retry. Test fresh invocation with an empty parent environment, old allocation
after generic/receipt replacement or removal, valid retained-wrapper log versus
wrong cache/binding log, and retry/source-SOT/native regressions.

Acceptance tests: empty installation, verified direct Codex migration, changed
canonical-root update, real supported AGY fixture recognition and preservation;
malformed/unknown explicit selection before fake-provider start; exact argv,
stdin, output and exit forwarding; distinct classifier contexts; wrong root or
tampered receipt/snapshot/launcher rejection; mixed/foreign/symlink/FIFO/hardlink
refusal; rollback after publication failure; repeat install; supported update
and remove while AGY remains usable; old Codex bound call and later collection
after cache replacement/removal; cache path differs from retained root with
matching selector/preflight/collection; source-SOT regressions.

## Task 2: Leader skill, documentation and release integration

The fresh RED scenario and expectation are recorded in the workspace evidence
directory. Amend SKILL and relevant public-v2/leg/provider references to resolve
installed runtime and carry explicit binding consistently; retain source-SOT
examples. Add a dedicated scenario regression test and obtain fresh GREEN,
relevant full regressions and skill validation. Update English/Korean
installation, security, migration, README and changelog; synchronize version
0.2.564. Document supported legacy baseline and independent-AGY-installer limit.

Review Task1 implementation and combined integration with independent native
review before formal review. Shared files/interfaces require the leader's
integration check; no parallel code writers.

## Verification, publication and local deployment

- Focused tests, full isolated host pytest, bash-n, vendoring/runtime validators,
  committed distribution verification; native Ubuntu/macOS CI separately.
- Existing guarded-worktree four-leg formal profile, all required legs SAFE,
  exact final integrity. Source-SOT stage remains direct and isolated. Complete
  final branch review using the most capable native reviewer as required by SDD.
- Create/attach PR, verify exact reviewed head and CI, merge under current owner
  authority. Publish 0.2.564 with reviewed release notes and verify actual assets.
- Update/install the released plugin using its supported lifecycle, migrate the
  four authorized generic launchers only after exact legacy verification,
  verify explicit Codex plus unchanged AGY behavior and fresh installed discovery.
- Send actual pins/results and remaining adoption tasks to Codex46, Claude1,
  AGY2. Keep #9 roster diagnostics separate.

Estimated production additions 730-1050, deletions 50-100, net 630-1000; novel core
500-750 Python lines, shell70-130, existing v2 context plumbing80-150.
Tests/fixtures/docs/vendor bytes are separate.
Growth beyond the guide is justified by preserving authenticated legacy context,
immutable toolkit receipt identity and transactional publication in one usable
installation outcome. Record actual delta and any revised estimate; no extra
scope is implied by line growth.
