# Formal Google CLI OAuth-Only Design

**Owner decision:** Formal three-family review must use the subscription-backed
Antigravity CLI (`agy`) OAuth session for its Google-family leg. It must never
fall back to a Gemini API-key, Vertex, service-account, or other separately
billed route.

## Behavioral claim

A formal Google-family review leg is dispatched only through authenticated
`agy` in an explicitly bound AGY Project whose project-scoped permissions deny
write and execution tools; if that binding, the binary, required model, or
OAuth session is unavailable before submission, or if the submitted AGY call
fails, the complete round is invalid and stops without selecting `gemini`.

## Design

- Keep `agy` 1.1.10 or newer and `gemini-3.1-pro-high` as the formal Google
  route. The installed `agy` owns Google Sign-In and reads its existing system
  keyring session; TRIAD does not create, copy, inject, or refresh credentials.
- Remove known API-key, Vertex, ADC, and cloud-project route-selector variables
  from the formal AGY child environment by variable name without reading or
  logging their values. This prevents an ambient separately billed route from
  overriding native Google Sign-In while leaving the owner session untouched.
- Bind every formal call to an existing AGY Project with `--project`. The
  Project must name the reviewed workspace as its sole resource and its
  project-specific configuration must deny `write_file(*)`, `command(*)`,
  `unsandboxed(*)`, `execute_url(*)`, and `mcp(*)`. AGY stores that configuration
  in its project registry under `~/.gemini/config/projects/`; it is not the
  global `~/.gemini/antigravity-cli/settings.json` policy and affects only the
  selected Project.
- Require `--sandbox` and remove `--dangerously-skip-permissions`. AGY 1.1.4
  fixed headless print mode to honor persisted permissions; the supported
  1.1.10+ floor is therefore entirely after that fix. A missing/malformed
  Project binding or an incomplete deny set stops before provider submission.
- Remove every active cross-family-review instruction that permits a formal
  `gemini` fallback. The packaged Gemini wrapper and its standalone dispatch
  skill may remain available for explicitly requested non-formal enterprise
  work, but they are not a substitute family inside the formal gate.
- Bootstrap formal readiness requires `agy`. A discovered `gemini` executable
  remains optional and does not satisfy the Google-route prerequisite.
- Before submission, a missing AGY binary, unsupported version, missing model,
  or failed OAuth-backed preflight stops the round. After submission, every AGY
  failure likewise invalidates the round. In both cases all required families
  restart only after the AGY CLI OAuth route is repaired.
- Documentation states the billing boundary directly: individual subscription
  access uses AGY Google Sign-In; formal review does not invoke the separately
  billed Gemini API/Vertex routes.

## Rejected alternatives

- Do not port Claude-host's Google-leg `ADVISORY` policy; the current product
  requires all three families and weakening that gate is unrelated.
- Do not port its global `~/.gemini/antigravity-cli/settings.json` transaction;
  it directly controls user-global state and does not solve authentication.
- Do not synthesize a repository-local AGY `settings.json`; AGY does not consume
  that as its project permission source. Use its native Project registry and
  explicit `--project` selection while keeping the policy project-scoped.
- Do not add API-key value detection or secret inspection. Formal-child
  environment scrubbing is name-based and does not expose credential material.
- Do not build a new interactive PTY permission broker. That is a separate,
  larger containment design.

## Verification

1. A skill-executor baseline must show that the current SOT permits the Gemini
   fallback when AGY OAuth is unavailable.
2. Static contract tests must require AGY-only formal routing and reject active
   fallback language, a bootstrap success based on `gemini` alone, a formal
   command without `--project`/`--sandbox`, an incomplete Project deny set, or
   any `--dangerously-skip-permissions` formal route.
3. Focused bootstrap and distribution tests must pass.
4. A fresh skill-executor scenario must stop the formal round without invoking
   any provider when AGY OAuth is unavailable and an API key is available.
5. A disposable-project OAuth spike must prove on the installed AGY version
   that a file-view read succeeds while `write_file` and `command` are denied,
   with no danger flag. It must use the native Google Sign-In route and no API
   key, Vertex, service account, or Gemini CLI.
6. Routine regression verification makes no live API-key, Vertex,
   service-account, Gemini, or AGY model call; `agy --version` and `agy models`
   are the only ordinary local route preflight commands.

## Slice size

This is one S/M behavioral claim. Forecast: at most 260 production/script lines
changed, at most 140 lines of novel project-binding/validation core, with
documentation and tests outside the production-line budget. No L-class
exception is required.
