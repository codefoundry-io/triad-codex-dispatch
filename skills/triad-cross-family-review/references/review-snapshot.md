# Review snapshot closure contract

Use the packaged Python helper before a formal dispatch. It defines the default
source-complete universe as:

- every tracked Git index path, except a tracked path deleted in the working tree;
- every non-ignored untracked path;
- an audited inventory of ignored untracked paths whose bytes are not copied;
- explicit, audited exclusions only for untracked review/runtime residue such as
  `_runs`, `_debug`, Python caches, and temporary-file suffixes.

Tracked exclusions are not permitted. Gitlinks/submodules, symlinks, unmerged
index entries, directory entries, and non-regular files fail closed rather than
silently disappearing. The helper repeats repository enumeration around a full
post-copy source rehash, records deleted and excluded paths, writes a canonical
receipt, verifies exact file-set closure, and seals the snapshot read-only. It
does not claim an atomic filesystem transaction: keep the source quiescent while
creating the snapshot; any change observed by the copy, rehash, or enumeration
passes invalidates the attempt.

Use the absolute Python runtime selected by bootstrap. It may be any supported
Python version at or above 3.12; do not pin a minor version or PATH-resolve a
different interpreter. Invoke argv directly with `-E` and no shell:

```python
snapshot_tool = (
    "/absolute/installed/plugin/skills/triad-cross-family-review/"
    "lib/review_snapshot.py"
)
create_snapshot_argv = [
    bootstrap_python,
    "-E",
    snapshot_tool,
    "create",
    "--repo", "/absolute/canonical/project-root",
    "--output-parent", "/absolute/review-id/packet/inputs",
]
verify_snapshot_argv = [
    bootstrap_python,
    "-E",
    snapshot_tool,
    "verify",
    "--snapshot-root", "<absolute snapshot_root from create JSON>",
]
```

Create the snapshot below the not-yet-sealed packet, run `verify`, and freeze
both canonical JSON receipts plus the entire snapshot tree into the packet
manifests. Dispatch only when both commands exit zero and the final packet hash
binds those exact bytes. A byte-identical copy may move to another parent when
it keeps the generated snapshot directory name, which is the receipt's logical
snapshot identity. Renaming that directory invalidates verification.

The `create` command keeps stdout deliberately small for CLI transports: it
returns only the snapshot root, receipt path, manifest hash, file count, and seal
state. The complete enumeration and file evidence remain in the referenced
`SNAPSHOT_RECEIPT.json`; consume that file rather than expecting the full receipt
on stdout.

Git-ignored bytes are visible in the receipt but are outside the default source
snapshot. Inspect that inventory before dispatch. If a generated or ignored file
is a deployed consumer required for the review, the default snapshot is
insufficient: include it with an evidence-equivalent project snapshot and
verifier, or mark the formal gate invalid. A diff remains a navigation index,
not a reason to omit unchanged callers or consumers.

A project-specific snapshot tool may replace this helper only when its frozen
receipt proves the same or stronger enumerated universe, repeated enumeration,
byte hashes, exact file-set closure, and independent verification. A prose claim
of completeness is not equivalent evidence.
