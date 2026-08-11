# Fingerprint diff residuals

Date: 2026-08-11

Scope: committed Slice 1 source at `e537776d972e6f7b6f4e34b8f9b77093f2527bc9`
with Git 2.50.1. A dedicated no-edit `triad-skill-executor` used both staged and
unstaged forms of the exact product command:

```text
git diff [--cached] --binary --full-index --no-color --no-ext-diff --unified=3 --inter-hunk-context=0 --diff-algorithm=myers --no-indent-heuristic --no-renames --no-textconv --src-prefix=a/ --dst-prefix=b/
```

## Reproduced presentation residuals

| Setting | Fixture observation |
|---|---|
| `diff.orderFile` | Default-order bytes and configured reverse-order bytes differed in both arms; the first changed patch path moved from `alpha.txt` to `zeta.txt`. |
| `diff.suppressBlankEmpty` | `false` retained a space before an empty context line while `true` removed it in both arms. |
| `.gitattributes` `diff=probe` plus `diff.probe.xfuncname` | Two regex values changed the hunk-header text from `SECTION_ONE` to `line one` in both arms. |

The same probe refuted a `core.quotePath` residual because the product helper
forces `core.quotepath=true`. A submodule presentation branch was not admitted:
the local fixture could not create a file-transport submodule under the
unchanged user configuration.

## Ruling

The reproduced settings change ordering or presentation, not whether a tracked
mutation is represented. When a residual setting affects rendered bytes and
changes between capture and verification, the digest comparison fails closed.
If configuration instead makes the checked `git diff` subprocess fail, no
fingerprint is emitted. The owner selected the vetted Claude-hosted skill's
bounded patch-diff model and rejected a canonical-index/full-file hash redesign
as over-engineering. These cases remain disclosed residual false-mismatch paths.
