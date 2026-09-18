# S5: Effective working-directory audit receipt

> Execute this plan with Superpowers TDD and the repository's dedicated fresh
> skill executor. The root leader owns source and tests under project policy;
> independent agents provide execution evidence and review findings.

## Outcome and scope

Record the host-resolved launch directory in the existing audit record after a
provider child starts. This makes wrong-root diagnosis possible without reading
human stderr or dumping the environment. It is host launch evidence, not proof
of the provider's later working directory or review coverage.

Keep `Popen` arguments, provider dispatch, classification, retry behavior, and
admission unchanged. Store the directory privately on `RunResult`, then project
it as optional `effective_cwd` in audit JSON. Resolve the supplied directory (or
inherited host cwd) once before launch. Omit it on pre-launch failures. Redacted
and hardened audit modes replace the entire path with `<redacted:cwd-path>`.
Do not add the field to failure/repair IPC or introduce another persistence path.

Expected production delta: about 10 additions / 1 deletion, net below 20;
novel core below 20 lines. Files: `bin/_common.py`, one focused test module,
`README.md`, `README.ko.md`, and `SECURITY.md`. Tests and docs are counted
separately. No version, installation, provider-settings, or governance change.

## Task 1: Receipt behavior and privacy

1. Add provider-free tests using actual short Python child processes and the
   existing audit writer. Cover explicit and inherited cwd, snapshot custody
   after the parent changes cwd, redacted/hardened modes, nonzero and timeout
   results, encoding/spawn failures, and unchanged failure IPC.
2. A fresh `triad-skill-executor` at Terra/high with no inherited turns runs the
   focused tests against the canonical source and records intended RED.
3. The leader adds only the private capture and optional audit projection.
4. Update English/Korean logging guidance and security custody documentation.
5. A separate fresh executor runs focused GREEN, the full repository suite,
   skill validation, and packaged provider-free lifecycle characterization.
   Preserve source fingerprints and exact cleanup evidence. Release-archive
   verification remains at the later clean release-candidate boundary.

## Task 2: Review and integration

1. Obtain an independent native task review of the diff, tests, and relevant
   unchanged provider consumers. Verify findings against source and apply only
   reproduced in-scope corrections.
2. Freeze the complete S5 candidate and run the workspace-required four-leg
   formal merge gate with identical source/criteria custody. Review full test
   changes as well as production and public documentation.
3. Preserve every started leg, adjudication, and integrity receipt. Any changed
   reviewed bytes require a fresh complete round.
4. After admission, verify CI and protected-file hashes, merge the S5 PR under
   the owner's standing campaign authorization, and verify remote main and tree.
   Continue the next roadmap slice; stop before deployment.

If source validation establishes an approved/existing design defect, stop
implementation and integration, obtain read-only Claude/Google/fresh-Codex
diagnosis, and brief the owner before any continuation.

## Verification commands

Run from the workspace host cwd through `/bin/zsh -lic`, passing the canonical
repository as `$1` and using `PYTHONDONTWRITEBYTECODE=1`:

```sh
python3 -m pytest -q "$1/tests/test_effective_cwd_receipt.py" --rootdir "$1" -p no:cacheprovider
python3 -m pytest -q "$1/tests" --rootdir "$1" -p no:cacheprovider
python3 "$TRIAD_SKILL_VALIDATOR" "$1/skills/triad-cross-family-review"
python3 "$1/skills/triad-cross-family-review/scripts/verify_lifecycle.py"
```

Resolve the system validator path for the host into `TRIAD_SKILL_VALIDATOR`; never substitute installed
TRIAD cache content for the canonical source.
