# Shared commands and consumer compatibility

[한국어](shared-runtime.ko.md) · [Installation](installation.md)

Starting with 0.2.564, the four generic commands under `~/.local/bin` can serve
multiple explicitly registered consumers. The shared library decides binding
identity, compatibility, selection and conservative retention. Each host still
owns its native spawning, models, effort, authentication and provider adapters.
Installing Codex does not make existing bare AGY calls select Codex.

## Installation and selection

Run the installed `scripts/bootstrap.sh --install` from the target project as
described in the installation guide. Bootstrap authenticates the entire existing
command group before publishing a replacement:

| Existing group | Result |
| --- | --- |
| All four commands absent | Register Codex and establish its first legacy default |
| Verified supported direct Codex launchers | Preserve the original legacy target; add a retained Codex binding |
| Verified supported AGY launchers | Preserve the original AGY payload, target and default; add Codex |
| Verified shared generation | Preserve existing bindings/default; add or reuse Codex |
| Partial, mixed, edited or unknown group | Refuse without replacing the group |

Supported direct Codex inputs are 0.2.563 with the exact published dev5 package
and source pins, or direct source-SOT launchers with this release's exact dev6
package. Older Codex releases (including 0.2.562/dev4 and 0.2.561/dev3) are not
admitted by this migration and are left unchanged. Keep their original toolkit
and use a separately reviewed transition; do not delete their launchers or
caches to bypass authentication while another consumer or direct round needs them.

The supported direct AGY baseline is source commit
`00f255826e894b82105d2b32e68b209d761f964b`: 80 runtime files, with canonical
inventory digest `1b40aaf00c786a4595333a0d389cb6fba5d51ee002dc04f8e1c2add7500a6d83`.
A marker is insufficient: bootstrap verifies hardened launcher structure,
coherent pinned context, complete runtime inventory, regular files and safe
ancestors. Other AGY revisions need an independently reviewed baseline update.

Immutable snapshots, bindings and dispatcher generations live under
`~/.local/share/triad-dispatch-runtime`. Codex installation receipts live under
`~/.local/share/triad-codex-dispatch/installations`. The four public entry points
and the new receipt use one rollback transaction; publication is not a claim of
simultaneous atomic replacement across four files. Existing entries and retained
assets remain valid while the group changes.

Resolve the canonical installed plugin root through its packaged resolver:

```sh
python3 "$plugin_root/bin/shared_runtime.py" resolve --plugin-root "$plugin_root" --json
```

Treat the response as JSON data. It returns the authenticated `binding_id`,
`toolkit_root`, `launcher_dir`, execution context and provenance. Distinct
contexts for the same plugin root require an explicit `--binding ID`; no lookup
chooses the latest receipt. Unknown, malformed, changed or ambiguous context
refuses before provider execution. A bare generic command uses only the
established legacy default, never the installer name, `CODEX_HOME` or PATH order.

For a deliberate generic call, set `TRIAD_RUNTIME_BINDING` for that command only:

```sh
TRIAD_RUNTIME_BINDING="$binding_id" review_round.py --help
```

Do not add a global export. Installed skills use the authenticated per-binding
hardened launchers, which pin the interpreter, vendor paths, trusted PATH and
classifier path. The classifier's learned contents remain mutable under their
existing policy. CLI calls preserve arguments, standard streams and exit status.

Save `binding_id` from bootstrap's installation JSON. A provider-path or PATH
change can create a second binding for the same plugin root. To recover a lost
ID, inspect only regular JSON receipts in the installation directory whose
`plugin_root` exactly matches the canonical root. The parent directory name of
each receipt's `binding_file` is a candidate ID; authenticate it with
`resolve --plugin-root "$plugin_root" --binding "$binding_id" --json` before use.
Compare the returned context to select deliberately; do not choose by recency.
To unregister one superseded receipt, use a command-local selector:

```sh
TRIAD_RUNTIME_BINDING="$old_binding_id" bash "$plugin_root/scripts/bootstrap.sh" --remove
```

This retains its binding and active-round assets. It does not change the legacy
default or unregister other receipts. Use the selected new ID explicitly until
only the intended receipt remains for that root.

## Rounds, updates and removal

Resolve once before creating a round. Use its retained toolkit for every helper,
schema, reference and receipt. Public v2 seals `runtime_binding` and its execution
context, returns immutable launcher allocations and checks that same context on
retry and collection. A later generic launcher update, installation receipt
removal or original plugin cache removal does not redirect such a round. Native
Codex allocations retain their host-native spawning contract.

Run bootstrap after each plugin update or provider path change; matching root
and context reuse a binding, while a new root/context keeps prior bindings.
`--remove` unregisters only that installation receipt. Shared commands, other
consumers and retained assets remain available. Unknown active dependencies cause
conservative retention; this release has no automatic garbage collector. Preserve
these directories rather than deleting them as cache cleanup.
Normal shared installation/removal also preserves global shell and Codex
configuration, including recognized legacy-managed fragments. Their cleanup is
separate work; isolated source-SOT staging retains its scoped cleanup behavior.

### Interrupted publication or unexpected files

A killed install can leave `.<target-name>.<random>.tmp` hard-link residue;
unexpected files such as `.DS_Store` in the receipt directory also cause refusal.
Do not clear a runtime directory or ignore failed authentication. Stop its
install/remove writers and retain the exact error, file paths and backups.
An operator may unlink one confirmed temporary duplicate only after checking
that it and its expected destination are regular, owner-owned files with the
same device/inode, link count two, and expected bytes. Recheck authentication
afterward. Unknown files require individual ownership review and preservation
outside the managed directory; their names alone authorize no deletion.
A mixed command group after interruption needs a reviewed recovery from the
captured original group; removing a temporary link does not repair that group.

The guarantees have explicit limits:

- Rounds begun with direct legacy cache paths before migration still require
  those original caches. Their receipts are never rewritten to a new toolkit.
- The retained AGY legacy target still requires its original installation.
  An independent older AGY installer/remover is not governed by this installer.
- External Python environments, user-site dependencies, vendor executables and
  provider authentication remain owner-managed prerequisites.
- Source-SOT development uses its existing isolated direct-source stage and
  does not register or resolve an installed shared binding.

Claude and AGY maintainers must adopt their own compatible installation and
round-pinning paths before claiming independent update/removal interoperability.
Use [installed skill instructions](../skills/triad-cross-family-review/references/shared-runtime.md)
for the execution procedure. Source verification, synthetic dispatch, live
provider behavior, public publication and fresh skill exposure are separate
evidence claims.
