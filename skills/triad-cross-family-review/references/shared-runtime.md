# Select an installed consumer runtime

Apply this procedure before either public-v2 or legacy installed operation,
including ordinary provider dispatch. A common command name does not identify
the calling host. Existing unqualified calls keep their established legacy
consumer; do not use that default to select Codex.

## Resolve once before preparing a round

Resolve `plugin_root` from the canonical installed skill's realpath. Use that
root only as the installation lookup key, then run its packaged resolver:

```sh
python3 "$plugin_root/bin/shared_runtime.py" resolve --plugin-root "$plugin_root" --json
```

When the owner selected an exact binding, add `--binding "$binding_id"`.
Read the JSON as data; never source or evaluate its contents as shell text.
Require successful authentication of the exact canonical plugin root, immutable
binding and retained toolkit. Capture `binding_id`, `toolkit_root`, `launcher_dir`,
`runtime_context` and provenance from the result. An absent, invalid, changed or
ambiguous receipt stops preparation; do not fall back to another host, cache,
binding or an unqualified command. Do not pick the latest receipt.

Use this verified retained `toolkit_root` for all lifecycle, rendering, helper,
reference and schema paths. Read this retained toolkit's relevant instructions.
Keep the same resolved binding for the whole round. Never re-resolve a current
installation receipt during retries or collection. The original plugin cache
may be replaced or removed after resolution; the retained assets stay available.
Do not weaken toolkit-path or receipt equality checks to accommodate a move.

## Calls and review requests

For installed provider calls and the legacy Google selector, use the immutable
per-binding hardened command at `"$launcher_dir/<command>"`, with the same
arguments documented for the packaged wrapper. This applies the selected
interpreter, classifier path, vendor pins and trusted PATH even in a new tool
invocation whose parent environment has none of those variables. Direct Python
wrapper examples elsewhere describe source-SOT execution; installed calls use
the corresponding hardened command with unchanged arguments.

When deliberately using a common generic command, provide the selected binding
for that call only:

```sh
TRIAD_RUNTIME_BINDING="$binding_id" review_round.py --help
```

Do not write a global shell export. A malformed or unknown explicit selector
must refuse, and must not fall back to the legacy consumer.

For public v2, add `"runtime_binding": "<verified binding_id>"` to the request
and execute `v2-create` from the retained toolkit. It authenticates and seals
the immutable execution context. Execute every allocated invocation exactly as
returned, including its immutable launcher path and environment. CLI allocations
carry their context without relying on the leader's current shell; native Codex
allocations still use the actual host native-spawn tool and unchanged settings.
Retry and collection verify the sealed context, not the newest installation.

For legacy review, set `google_selector_launcher="$launcher_dir/review_round.py"`
and use the same retained root and per-binding provider launchers throughout.
Pass the original arguments and selector/preflight receipts unchanged.

## Source-SOT and lifecycle limits

Source-SOT development uses the source root directly and the existing isolated
bootstrap stage selected by `TRIAD_BOOTSTRAP_SOURCE_SOT_REVIEW_ROOT`. It does not
resolve installed receipts or register a shared consumer. Do not combine that
mode with an installed runtime binding.

Updates preserve existing bindings and their retained assets. Removal unregisters
only the selected installation receipt; unknown consumers or active uses cause
conservative retention. Do not delete retained runtime directories manually as
cleanup. Rounds begun before migration with a direct legacy cache path still
need that original cache; their receipts cannot be moved to a new path. An
independent older AGY installer/remover and external Python/provider dependency
removal remain outside this shared installer's lifecycle guarantee.
