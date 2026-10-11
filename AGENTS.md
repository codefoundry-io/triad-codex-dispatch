# TRIAD Codex development

- Work from this source checkout. Manage the Codex host; use the Claude host as read-only reference.
- Read `docs/agent-policies/development.md` for source, compatibility and release contracts.
- Keep release version metadata and affected English/Korean/security/migration docs aligned.
- Preserve Python 3.12+ bootstrap compatibility unless the owner approves a change.

## Shared infrastructure

On the owner's managed workstation, read
`/Users/chaniri/codex_workspace/docs/agent-policies/common.md` before work.
Load `execution-environment.md` in that directory before CLI commands and
`development-agents.md` before native delegation; project-specific rules below apply.

## Load for the current operation

| Operation | Reference |
|---|---|
| Source skill or bundled behavior change | `docs/agent-policies/skill-development.md` |
| Tests, bootstrap checks or release archive | `docs/agent-policies/verification.md` |
| Formal review | Project development contract and shared `four-leg-formal-review.md` where adopted |
| Owner-workstation install/update/removal | Shared `triad-installation.md` and this checkout's installation guide |

## Exceptions

- Installed caches and consumer `migration/AGENTS.recommended.md` are not development authority.
- Preserve the selected source skill, dedicated fresh behavior executor and review custody.
  Source checks, formal review, distribution, installation and public release are separate claims.
- Final merge and external configuration changes retain their explicit owner approval boundary.
