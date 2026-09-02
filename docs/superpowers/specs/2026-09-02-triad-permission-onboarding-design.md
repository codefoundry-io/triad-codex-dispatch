# TRIAD Permission Onboarding Design

## Status and dependency

This is a post-0.2.548 design. It depends on the review-contract simplification slice
making bootstrap-managed launcher paths the complete shipped execution surface. It
does not change the current release's permission-neutral bootstrap.

The single behavioral claim is: a recipient can explicitly install, inspect, update,
or remove narrow Codex execpolicy rules for the stable TRIAD launchers without changing
the host sandbox or approval policy.

Forecast: 250-450 production net lines, 120-220 novel-core lines, and one behavioral
claim. This is an S/M slice. Tests, fixtures, and documentation are outside the
production-line budget.

## Constraints established by the host

Codex plugins inherit the active host sandbox and approval policy. Plugin installation
does not expose a documented hook that can grant shell permission. A distributed plugin
therefore cannot silently select a permission profile or promise an install-time host
Yes/No dialog.

Managed company environments remain on `workspace-write` with `on-request`. Human
approval uses `approvals_reviewer = "user"`; `auto_review` is an organization-controlled
alternative reviewer, not a permission grant. This feature never selects unrestricted
filesystem access and never edits `sandbox_mode`, `approval_policy`,
`approvals_reviewer`, project trust, or organization requirements.

## Selected approach

Add an explicit, separately invoked permission setup command shipped with the plugin.
Bootstrap stays non-interactive and permission-neutral. After bootstrap has installed
the stable launchers, documentation may offer this command:

```text
python3 scripts/codex_permission_setup.py install \
  --scope project \
  --project-root <trusted-project> \
  --decision prompt
```

The command resolves the exact target, verifies the four bootstrap-managed launcher
paths, renders the complete proposed rule bytes, and asks for a terminal `[y/N]`
decision. EOF, non-TTY input, or anything except an affirmative answer leaves state
unchanged. `--decision prompt` is the documented default. `--decision allow` is an
explicit advanced choice because an allowed prefix executes outside the sandbox without
another prompt.

Supported scopes are:

- `project`: `<trusted-project>/.codex/rules/triad-codex-dispatch.rules`;
- `user`: the active Codex user rules directory resolved by the supported host
  configuration contract.

Project scope requires an explicit canonical project root and reminds the recipient
that Codex loads project configuration only after trust. The command does not infer a
project from the current directory.

## Rule surface

Rules match only the absolute stable launcher paths published by bootstrap:

- `claude_wrapper.py`;
- `antigravity_wrapper.py`;
- `gemini_wrapper.py`;
- `review_round.py`.

There is no prefix for `python3`, `python`, `zsh`, `bash`, `claude`, `agy`, `gemini`, or
another provider binary. Provider subprocesses remain governed by the already-approved
launcher process and the host policy. The rule generator never follows a versioned
plugin-cache path directly.

The generated file has a versioned ownership header and deterministic complete bytes.
Install creates an absent file, or replaces an exact older plugin-owned file after
showing the delta. It refuses symlinks, directories, path traversal, undecodable data,
or any foreign/edited file. `show` is read-only. `remove` deletes only exact recognized
plugin-owned bytes after the same `[y/N]` gate. An interrupted write leaves either the
old complete file or the new complete file.

## Update and removal lifecycle

Marketplace upgrade still requires running the newly installed bootstrap so stable
launchers point at the new installed root. The permission rule does not change because
its prefixes name those stable launcher paths. If launcher placement changes, the setup
command proposes an exact replacement; it never broadens an existing prefix.

Uninstall documentation runs permission removal separately from plugin removal. A
failed or declined permission removal does not authorize deleting a foreign file, and
plugin removal does not claim the rule is gone without checking it.

## Alternatives considered

1. Add rules during plugin installation. No documented plugin hook grants that behavior,
   and silent host-policy mutation violates recipient ownership.
2. Restore automatic rule installation inside bootstrap. That recreates the retired
   behavior and makes ordinary plugin setup mutate host permission state.
3. Recommend blanket Python or shell prefixes. Those prefixes authorize unrelated code
   and do not reliably match login-shell-wrapped commands.
4. Document only per-command prompts. This is safe, but it does not provide the optional
   reusable rule workflow the owner requested.

The selected approach makes the security-sensitive action explicit, inspectable,
reversible, and independent from installation.

## Non-goals

- No Full Access guidance or configuration.
- No organization-policy bypass or automatic trust selection.
- No provider credential, OAuth, keychain, or model configuration.
- No direct provider-binary permission rule.
- No general-purpose Codex rule editor.
- No change to TRIAD review composition, fallback, or admission semantics.

## Verification

Implementation follows the skill-development RED/GREEN protocol with fresh
`triad-skill-executor` instances. Tests cover exact proposed bytes, default `prompt`,
explicit `allow`, project and user target resolution, TTY decline/EOF, owned update,
foreign-file preservation, symlink/path attacks, atomic replacement, exact removal, and
the absence of blanket prefixes or host-config edits. Distribution checks bind the new
script and documentation. Final deployment also verifies installed bytes and a fresh
session, but does not execute `allow` against a recipient's real user rules during tests.
