# Codex Plugin CLI Evidence

Date: 2026-07-04

Purpose: retained evidence for the public install command surface used by the
README and setup docs.

## Local CLI Help

`codex plugin add --help` includes:

- `codex plugin add [OPTIONS] <PLUGIN[@MARKETPLACE]>`
- `--json` — output install result as JSON

`codex plugin marketplace add --help` includes:

- `codex plugin marketplace add [OPTIONS] <SOURCE>`
- source forms: local path, `owner/repo[@ref]`, HTTPS Git URL, SSH Git URL
- `--ref <REF>`
- `--json`

## Public Repository

`gh repo view codefoundry-io/triad-codex-dispatch --json nameWithOwner,visibility,defaultBranchRef,url`
returned:

```json
{
  "defaultBranchRef": {"name": "main"},
  "nameWithOwner": "codefoundry-io/triad-codex-dispatch",
  "url": "https://github.com/codefoundry-io/triad-codex-dispatch",
  "visibility": "PUBLIC"
}
```

`git ls-remote --symref origin HEAD` returned `ref: refs/heads/main HEAD`.

## Public Git Marketplace Install Shape

Executed in an isolated temp scope:

```bash
env HOME=/private/tmp/triad-plugin-evidence-git-home \
  CODEX_HOME=/private/tmp/triad-plugin-evidence-git-codex \
  codex plugin marketplace add codefoundry-io/triad-codex-dispatch --ref main --json
```

Output:

```json
{
  "marketplaceName": "triad-codex-dispatch",
  "installedRoot": "/private/tmp/triad-plugin-evidence-git-codex/.tmp/marketplaces/triad-codex-dispatch",
  "alreadyAdded": false
}
```

Then:

```bash
env HOME=/private/tmp/triad-plugin-evidence-git-home \
  CODEX_HOME=/private/tmp/triad-plugin-evidence-git-codex \
  codex plugin add triad-codex-dispatch@triad-codex-dispatch --json
```

Output:

```json
{
  "pluginId": "triad-codex-dispatch@triad-codex-dispatch",
  "name": "triad-codex-dispatch",
  "marketplaceName": "triad-codex-dispatch",
  "version": "0.1.0",
  "installedPath": "/private/tmp/triad-plugin-evidence-git-codex/plugins/cache/triad-codex-dispatch/triad-codex-dispatch/0.1.0",
  "authPolicy": "ON_INSTALL"
}
```

The README's `jq -r '.installedPath'` is based on this retained output.

## Auth Policy Note

The marketplace entry uses the Codex marketplace default
`policy.authentication = "ON_INSTALL"`; `codex plugin add --json` reports that as
`authPolicy`. In this plugin, that is marketplace metadata only. Bootstrap still
does not perform OAuth/login for `codex`, `claude`, `agy`, or optional `gemini`;
users must already be authenticated in those CLIs.
