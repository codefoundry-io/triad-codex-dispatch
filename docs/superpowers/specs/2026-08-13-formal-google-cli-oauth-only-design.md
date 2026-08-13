# Formal Google CLI OAuth-Only Design

**Owner decision:** Formal three-family review must use the subscription-backed
Antigravity CLI (`agy`) OAuth session for its Google-family leg. It must never
fall back to a Gemini API-key, Vertex, service-account, or other separately
billed route.

## Behavioral claim

A formal Google-family review leg is dispatched only through authenticated
`agy`; if the binary, required model, or OAuth session is unavailable before
submission, or if the submitted AGY call fails, the complete round is invalid
and stops without selecting `gemini`.

## Design

- Keep `agy` 1.1.10 or newer and `gemini-3.1-pro-high` as the formal Google
  route. The installed `agy` owns Google Sign-In and reads its existing system
  keyring session; TRIAD does not create, copy, inject, or refresh credentials.
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
- Do not add API-key detection or secret inspection. Removing the formal
  Gemini route is deterministic and does not expose credential material.
- Do not build a new interactive PTY permission broker. That is a separate,
  larger containment design.

## Verification

1. A skill-executor baseline must show that the current SOT permits the Gemini
   fallback when AGY OAuth is unavailable.
2. Static contract tests must require AGY-only formal routing and reject active
   fallback language or a bootstrap success based on `gemini` alone.
3. Focused bootstrap and distribution tests must pass.
4. A fresh skill-executor scenario must stop the formal round without invoking
   any provider when AGY OAuth is unavailable and an API key is available.
5. No live API-key, Vertex, service-account, Gemini, or AGY model call is part
   of verification; `agy --version` and `agy models` are the only permitted
   local route preflight commands.

## Slice size

This is one S/M behavioral claim. Forecast: fewer than 40 production/script
lines changed, no new algorithmic core, with documentation and tests outside
the production-line budget. No L-class exception is required.
