# Formal reviewer routing contract

## Scope

This review-only routing policy is an owner routing policy, not a vendor
capability claim. It does not set generic wrapper defaults. It applies only to
a cross-family review after the owner has authorized external dispatch.

## Bounded formal routes

Unless the review decision records a justified escalation, use these routes:

- Fresh Codex: `gpt-5.6-terra`, `xhigh`, `fork_turns="none"`.
- Claude: `opus`, `xhigh`.
- Primary Google: agy with the exact display label `Gemini 3.1 Pro (High)`;
  catalog evidence uses `gemini-3.1-pro-high`.

Capture live proof of the selected route at the first possible proof point:

- accepted exact Codex spawn
- exact Claude argv/provider acceptance
- authenticated `agy models` evidence for the exact selector before formal dispatch, with the exact selector present

For every review ID, record the exact route and rationale/availability proof.
Rejection or unavailability leaves the required leg missing under the gate
rules. Do not silently substitute a model, provider route, or effort.

## Approval behavior

The exact managed wrapper rules use `decision = "prompt"`. For those prompts
and the wrapper's sandbox escalation to reach Agent Review, the active Codex
configuration must use `approvals_reviewer = "auto_review"` and keep the
applicable approval categories interactive. `approval_policy = "on-request"`
satisfies that requirement. With a granular policy, preserve all owner choices
but require both `granular.rules = true` and
`granular.sandbox_approval = true`. A false category is rejected before Agent
Review sees the request. `approvals_reviewer = "user"` keeps the call usable but
routes it to the person; `approval_policy = "never"` does not run Agent Review.

Do not install a local `[auto_review].policy` automatically because it replaces
the owner's reviewer instructions, and a managed `guardian_policy_config` has
higher precedence. The explicit owner request, exact rule justification, and
sanitized invocation are the authorization evidence. If Agent Review denies one
exact call and the owner elects to override it, `/approve` applies only to that
recorded denial; never generalize it into an unconditional allow or bypass.

## Google route and fallback

AGY is the primary Google-family route. A configured Gemini Enterprise/Business,
Vertex, or API-key route is eligible only after a pre-dispatch availability
failure proves that agy cannot be started on its configured route. A content,
extraction, schema, validation, timeout, capacity, or post-dispatch failure does
not make agy unavailable and does not permit Gemini fallback. A running tool
handle is pending, not unavailable or failed; wait for its terminal result.
If neither Google route is available, the required Google leg is unavailable
and the formal review round is invalid. Preserve an agy content or extraction
failure as an invalid leg rather than substituting Gemini. A missing selector,
request rejection, or exposed identity conflict also leaves the Google leg
missing/invalid.

For Google, authenticated `agy models` output proves that the stable selector is
advertised before formal dispatch. The current formal argv uses the exact display label `Gemini 3.1 Pro (High)` and
omits `--effort`; the catalog selector remains evidence only. Wrapper preflight
reports the requested `model` and `effort` and proves argv construction, never a
locally invented `effective_model`. Record actual provider request acceptance
and require any runtime-exposed identity to agree with the requested label. If
runtime telemetry is absent after the successful preflight, record it as
`unexposed` once without guessing the hidden actual model. After an AGY update,
adopt `--model gemini-3.1-pro --effort high` only after a fresh successful
runtime probe confirms provider acceptance and identity agreement.

A Gemini preflight/dispatch proves route availability only, not formal
read-only containment. The checked-in distribution is not end-to-end
enforcement-proven on supported tiers. ordinary/non-formal Gemini fallback
remains available after proven pre-submission agy unavailability, but Gemini is
ineligible as a formal fallback without separately recorded exact-route denial
evidence that the configured route's read-only policy denies write, replace,
shell, and MCP tools. Without that owner-recorded evidence, the required Google
leg is unavailable and the formal review round is invalid. This policy does not
create or run an automatic probe.

## Conditional escalation and convergence

An escalated reviewer route is conditional and reserved for an ambiguous,
security-sensitive, deeply integrative, or adjudication-heavy review. Its
selection does not itself invalidate a review when the exact route, rationale,
and live proof are recorded for that review ID.

Convergence remains based on reproducible path:line evidence and the unchanged
shared review directory, not model labels or vote counts. An unresolved
contradiction is `CONFLICTED` and requires owner adjudication. A reviewer that
modifies or executes candidate code invalidates that leg; a changed shared
directory invalidates the round and requires a fresh complete review.

## Failure handling

| Failure | Response |
|---|---|
| Reviewer asks for a packet | Point it to the shared review directory and scope |
| Provider unavailable before submission | Preserve evidence and apply the Google fallback rules |
| Required agy leg returns `truncated-answer` | Invalidate the leg and request a compact rerun; post-dispatch truncation does not permit Gemini fallback |
| Commit, push, install, merge, or release is needed | Stop for separate owner authorization |
