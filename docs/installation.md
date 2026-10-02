# Installation and personal settings

[한국어](installation.ko.md) · [README](../README.md)

Choose **marketplace installation** or **local installation from Git**. Both
install the same plugin and use the same runtime setup. Do not register both
under the same marketplace name.

## Select the version

The commands below select `main`, the current release line.
[Release v0.2.558](https://github.com/codefoundry-io/triad-codex-dispatch/releases/tag/v0.2.558)
contains the versioned download and checksums. For a reproducible installation,
use route B and check out the full commit ID recorded in the release notes.

## Prerequisites

Use your normal login terminal on macOS, Linux or WSL2. Install Git, Bash,
Python 3.12+, Codex, Claude Code 2.1.280+ for the default Opus 5.5 route,
and at least one Google CLI:

- AGY is preferred and required for personal Google Sign-In.
- **Legacy Gemini CLI** means the `gemini` executable route, distinct from AGY.
  It does not mean downgrading. Formal review requires Gemini CLI `>=0.34.0`,
  successful version/help/policy preflight and the existing Gemini Enterprise
  OAuth sign-in. AGY must be absent for the legacy selector to choose this route.
  The v2 Pro default has separate version support checks; see the
  [roster reference](../README.md#project-review-roster-check).

Claude Code [2.1.280 added Opus 5.5](https://github.com/anthropics/claude-code/releases/tag/v2.1.280).
This release was checked with 2.1.282. The v2 adapter's older preflight-interface
floor is separate from this model requirement; bootstrap checks binary presence,
not model entitlement or effective runtime effort. Upgrade Claude Code before
using the new default.

Sign in using each vendor's native workflow (`codex login` for Codex). TRIAD does
not configure accounts or copy credentials. On Linux/WSL2, install `bubblewrap`
when required by the Codex sandbox. Python runtime dependencies come from the
plugin's `requirements.txt`; bootstrap checks them before making changes and
prints the exact install command if they are missing.

Before running bootstrap, ensure `~/.local/bin` is on `PATH`. If it is missing,
add this line once to your normal shell startup file, preserving its other
contents, then open a new login terminal before continuing:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## A. Marketplace installation

No local clone is needed:

```bash
codex plugin marketplace add codefoundry-io/triad-codex-dispatch --ref main
```

For an already registered marketplace, use [Update](#update) to keep its existing
source and tracked ref. To change either (including a candidate branch to `main`), run
the [Remove procedure](../README.md#remove) in order: installed bootstrap removal,
plugin removal, then marketplace removal. Register the chosen source above or
below and install again. Preserve other marketplace registrations and personal settings.

## B. Local installation from Git

Download the checkout outside the projects you will review. Keep the checkout
for later updates. The destination below must not already exist:

```bash
mkdir -p "$HOME/.local/share"
git clone --branch main --single-branch https://github.com/codefoundry-io/triad-codex-dispatch.git "$HOME/.local/share/triad-codex-dispatch"
git -C "$HOME/.local/share/triad-codex-dispatch" rev-parse HEAD
codex plugin marketplace add "$HOME/.local/share/triad-codex-dispatch"
```

For an exact reviewed commit, clone the branch first, then run
`git -C "$HOME/.local/share/triad-codex-dispatch" checkout --detach <full-commit-id>`
before adding the marketplace. Replace the placeholder with the actual delivered
commit. Codex installs a cache copy; editing the checkout does not update the
installed plugin. `codex plugin add --path` is not an installation command.

## Install the plugin and runtime

After choosing A or B, run this once in the same login terminal:

```bash
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","add","triad-codex-dispatch@triad-codex-dispatch","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); root=pathlib.Path(data["installedPath"]); assert root.is_absolute(); print(shlex.join(["bash",str(root / "scripts" / "bootstrap.sh"),"--install"]))'
```

Move to the project workspace where you will use TRIAD, then execute the printed
absolute `bash .../bootstrap.sh --install` command. Do not run bootstrap from
your home directory or from the plugin cache/checkout. Its launcher, classifier,
Python and plugin targets must stay outside that workspace's writable roots.
If bootstrap reports missing Python dependencies, run its printed requirements
command in your chosen Python environment and retry the same bootstrap command.

Bootstrap installs four launchers under `~/.local/bin` and the classifier file
under `~/.config/triad-codex-dispatch/`. It preserves existing Codex settings,
permission rules and credentials. It does not sign in or install dependencies.

## Personal settings

1. **Codex permissions.** Use `/permissions` to select an interactive workspace
   policy before asking Codex to run TRIAD. For installations using the legacy
   configuration keys, set only these fields in either your existing
   `~/.codex/config.toml` or a trusted project's `.codex/config.toml`:

   ```toml
   sandbox_mode = "workspace-write"
   approval_policy = "on-request"
   approvals_reviewer = "user"
   ```

   Preserve unrelated fields and tables; do not replace the file or duplicate
   existing keys. These root-level fields go before any `[table]` header. Higher
   priority settings can override user values; managed requirements can constrain
   the allowed choices. Where your policy permits
   automatic review, change only `approvals_reviewer` to `"auto_review"`; it
   changes the approval reviewer, not the sandbox or task authorization.
   If you already use the newer permission-profile system, select its workspace
   profile instead and do not add these legacy keys. Confirm the effective
   setting with `/status`; if your Codex build provides `/debug-config`, use it
   to inspect precedence.

2. **Models and review settings.** Choose your leader model in Codex. For an
   explicitly selected v2 workflow, review the packaged
   [default roster](../contracts/review-legs.default.json) and use
   `.agents/triad-review-legs.json` in the target project for supported overrides.
   Keep existing entries. Authentication is selected separately for the review;
   the Legacy Gemini CLI authentication identifier remains `gemini-enterprise`.
   [Resolve the roster](../README.md#project-review-roster-check) before dispatch;
   a successful resolution is not proof of provider access. Gemini has no effort
   flag. Default reviews do not use web; request web verification directly for
   the specific round when needed.

3. **Optional paths.** Default users do not need extra environment variables.
   If you choose `TRIAD_BOOTSTRAP_BIN_DIR` or `TRIAD_CLASSIFIER_EXTENSION`, use an
   absolute path outside reviewed workspaces and rerun bootstrap. Do not add old
   `triad-setup`, `triad-doctor`, repair-agent or `shell_environment_policy`
   snippets: they are not part of this installation.

Settings references: [Codex configuration](https://learn.chatgpt.com/docs/config-file/config-basic),
[sandbox and approvals](https://learn.chatgpt.com/docs/sandboxing),
[permission profiles](https://learn.chatgpt.com/docs/permissions),
[local plugin sources](https://developers.openai.com/plugins/build/plugins).

<a id="gemini-cli-38-high"></a>

### Gemini CLI 3.8 Flash setup

Checked **2026-10-02**. For native Gemini CLI, request `gemini-3.8-flash`;
AGY's `gemini-3.8-flash-high` is a separate selection slug. This model requires
stable CLI **0.61.0 or newer** in TRIAD; upgrade through your existing CLI install
method if needed. Older supported v2 models retain their 0.60.0 floor: this is
a model-specific requirement, not a blanket pin to the latest CLI. Version
0.60.0 lacks the 3.8 alias and can remap strings ending in `flash` to an older
model ([tagged routing source](https://github.com/google-gemini/gemini-cli/blob/v0.60.0/packages/core/src/config/models.ts#L230-L270)).

For a native interactive session, `gemini --model gemini-3.8-flash` requests
the exact ID. The v0.61.0 built-in alias inherits **HIGH** generation configuration
([tagged defaults](https://github.com/google-gemini/gemini-cli/blob/v0.61.0/packages/core/src/config/defaultModelConfigs.ts#L31-L140));
HIGH is not a CLI effort flag or an attestation of provider-internal reasoning.

To persist selection, merge this into your existing `~/.gemini/settings.json`
or `<project-root>/.gemini/settings.json`; project settings override user settings
([tagged settings reference](https://github.com/google-gemini/gemini-cli/blob/v0.61.0/docs/reference/configuration.md#L44-L60)).
Preserve other fields; a CLI `--model` or `GEMINI_MODEL` value can override it.

```json
{"model": {"name": "gemini-3.8-flash"}}
```

Explicit HIGH is optional, for example to override an existing lower setting.
Merge these fields and **append** the rule to existing `customOverrides`; do not
replace existing arrays or the whole file. The supported shape is defined in
the [tagged settings schema](https://github.com/google-gemini/gemini-cli/blob/v0.61.0/packages/cli/src/config/settingsSchema.ts#L1144-L1192).

```json
{
  "model": {"name": "gemini-3.8-flash"},
  "modelConfigs": {
    "customOverrides": [{
      "match": {"model": "gemini-3.8-flash"},
      "modelConfig": {
        "generateContentConfig": {
          "thinkingConfig": {"thinkingLevel": "HIGH"}
        }
      }
    }]
  }
}
```

Neither `previewFeatures` nor enabling `experimental.dynamicModelConfiguration`
is needed. Dynamic configuration, aliases and rollout can alter the effective
ID; more specific/runtime overrides can also win. See the
[tagged ID resolver](https://github.com/google-gemini/gemini-cli/blob/v0.61.0/packages/core/src/config/models.ts#L234-L363).

For TRIAD v2, merge `"gemini": {"model": "gemini-3.8-flash", "effort": null}`
into the **existing selected Google entry** in `.agents/triad-review-legs.json`.
Keep its name, other entries and route/authentication selection; the packaged
default roster is unchanged. Native CLI settings above belong in Gemini's JSON
files, not new TRIAD roster keys. Keep the required authentication route; an API
key is not a bypass for TRIAD's Enterprise OAuth boundary.

Without a new provider request, run `gemini --version`, inspect the applicable
settings and any `--model`/`GEMINI_MODEL` override, and view `/model` in an
**already open** Gemini session without sending a prompt. These show the binary
version and selected/requested model, not backend entitlement or actual runtime
model. Main-chat selection also does not override subagent models.

## Verify the installation

Run `codex plugin list --json` and confirm the installed TRIAD version. In your
project workspace, check that `command -v review_round.py` resolves the installed
launcher, then start a **new Codex session**. Confirm the four TRIAD skills appear.
Do not also copy them into `.agents/skills/`.

Ask for one small read-only consult using the installed skill for your selected
provider. For Legacy Gemini CLI, use `triad-gemini-dispatch`; for AGY, use
`triad-antigravity-dispatch`. Installation and skill discovery do not prove live
authentication or policy enforcement. Validate normal review, permitted reads,
denied writes/shell, and explicitly requested web separately on the chosen route.

## Update

For an explicit cache replacement, first print the current installed bootstrap's
removal command:

```bash
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","list","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); item=next(item for item in data["installed"] if item["pluginId"]=="triad-codex-dispatch@triad-codex-dispatch"); root=pathlib.Path(item["source"]["path"]); assert root.is_absolute(); print(shlex.join(["bash",str(root / "scripts" / "bootstrap.sh"),"--remove"]))'
```

Run the printed command before removing its cache. It preserves owner-authored
settings and learned classifier patches. If removal fails, resolve its reported
problem before continuing. Then remove only this plugin, keeping the marketplace:

```bash
codex plugin remove triad-codex-dispatch@triad-codex-dispatch
```

Refresh the registered source:

- **Git-backed marketplace:** run
  `codex plugin marketplace upgrade triad-codex-dispatch`.
- **Local Git download:** update the checkout with
  `git -C "$HOME/.local/share/triad-codex-dispatch" pull --ff-only`.
  Marketplace upgrade refreshes Git-backed registrations, not local directories.
  For a detached pinned checkout, fetch and
  select the next reviewed full commit instead of pulling. Preserve local edits.

For either route, repeat the plugin-install command above, run its newly printed
bootstrap command from the target project, then start a fresh Codex session.
Also rerun bootstrap after moving or upgrading vendor CLI executables.
