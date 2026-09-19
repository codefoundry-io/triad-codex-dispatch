# REVIEW web separation with preserved AGY concurrency

Baseline B `71388383de307fbccdf593f913bc36d562ee2e41`; shared remote main
`2eb883fee59e66556ee7c7f87189b38231136622`. The existing R-CONTAIN requires
REVIEW no-web for every family and no permissive bypass on review. Implement
this settled subset of P5; D-B1 Gemini policy composition and D-B2 exact
investigation-evidence custody remain separate pending decisions.

## Smallest coherent change

Remove positive web allowances from both Google tool contracts and prepared
native review. Add one common no-web clause to both renderers for every family;
require unresolved external-evidence questions to return to the leader's separate
authorized investigation. Preserve local read/search tools and raw invocations.

Reuse AGY's existing `selected_context` (formal bindings or preflight). That
context selects the existing five raw read-only denies plus `read_url(*)` and
omits the headless autoapproval flag at formal dispatch. Project validation
requires the same six denies, without writing the owner-provisioned project.
Raw read-only and permissive calls retain existing rules and version/env-based
headless compatibility. Do not activate dormant hooks or add an agent layer.

Recognize exactly the two known ordered deny lists as shareable. Preserve the
existing deny-key comparison: identical six-rule Pro/Flash leases overlap;
raw-five versus formal-six remain isolated and wait/refuse under the existing
timeout. Keep crash recovery, holder liveness, exact restoration and cleanup.

Leave Gemini policy bytes and get_internal_docs unchanged pending D-B1; renderer
web prohibition is not a claim of mechanical Gemini web denial/full C15 closure.
Official headless and permission documentation supports removing the bypass
from REVIEW; their interaction under the installed release is not independently
attested. Current repeated Pro/Flash review success with optout=1 is bounded
compatibility evidence, not universal policy enforcement proof.
Sources: https://antigravity.google/docs/cli/headless/ and
https://www.antigravity.google/docs/permissions?tab=cli.

## TDD, preservation and gate

Fresh Terra/high RED and separate GREEN cover both renderers and all families,
AGY formal project/transient preflight and dispatch for Pro/Flash, flag absence
without env opt-out, raw compatibility, exact six-rule overlap, mixed-mode
refusal and restoration. Retain existing provider-failure restoration and raw
schema tests. Run full macOS/Ubuntu 24.04, validator/lifecycle and all required
fresh reviewers over the complete scope before integration. V1–V5 remain unrun.

Expected production delta <=75 additions/40 deletions, novel core <=50, in
review_round.py, _agy_settings.py and antigravity_wrapper.py. Tests/fixtures and
English/Korean/security/reference documentation are separate. No line-size gate.
Align the standalone AGY skill and shipped consumer guidance with the formal/raw
split; remove obsolete generic autoapproval assertions from both README copies.
The full-suite documentation-contract failures are specification-alignment
failures, not provider failures; update those checks and observe fresh RED/GREEN.
The first whole-scope review identified missing preflight rejection when
`--sandbox read-only` is absent and stale consumer autoapproval wording. Add the
early argument guard and align the affected text; retain raw builder coverage
under an accurate test name. Clarify local-only Gemini documentation reads and
AGY permission-attestation limits without changing vendor policy or schemas.

A stays read-only at `92c8afd500499d8736afcc28b39a87a4f87fed50`: its AGY read-only
branch already omits autoapproval and separates a local REVIEW agent from --web
RESEARCH (`3rd-Agent/wrappers/antigravity_wrapper.py:1180-1239,1381-1393`). Do not
port B's lease/project machinery there. A's Codex REVIEW still passes --search
(`.claude/skills/triad-cross-family-review/lib/review_scratch.py:3076-3079` and
SKILL.md:475-490); record that separate A omission in the shared handoff.
