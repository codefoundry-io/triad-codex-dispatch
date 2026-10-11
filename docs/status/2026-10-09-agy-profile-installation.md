# AGY profile installation — exact owner approval scope

Status: installed and capability probe passed on 2026-10-09. The owner explicitly
approved this exact installation and probe ("승인 gemini 사용에는 같은 문제가 없지?").

## Approved writes completed

Created these two previously absent regular files (1,244 bytes total):

| Destination | Source | SHA-256 |
|---|---|---|
| `/Users/chaniri/.gemini/config/agents/triad-codex-readonly-review.md` | `bin/agents/triad-codex-readonly-review.md` (565 bytes) | `a46fbede83f362a0c6c3e0f138ce9fa5f7fbdc75858469671960279a22bedd08` |
| `/Users/chaniri/.gemini/config/agents/triad-codex-readonly-research.md` | `bin/agents/triad-codex-readonly-research.md` (679 bytes) | `0eb5ff73947530923b4bf48dd8cb5df5b42c03fae467e1920866cc4a6b823d75` |

Execute the canonical source's `python3 bin/_agy_agent.py --install`, without
`--replace`, through the required owner login shell. If a different file appears
at either destination, setup refuses it. Existing Claude-host profiles, CLI
defaults, authentication, permission settings and native legs are unchanged.
This is profile provisioning only, not installation of the candidate plugin.
The profiles become available to sessions explicitly selecting their names.
Source copy/hash/existence evidence: `_runs/spec-plan-20261009/agy-profile/install-manifest.json`.

## Verification after approval

1. Confirm installed bytes match this manifest; no implicit replacement.
2. Execute one bounded AGY Pro/high search/read probe through the canonical
   formal v2 wrapper with its real profile lookup, preflight and existing guards.
   Use the synthetic fixture only; capture init.agent and successful native
   grep_search/view_file events. A SAFE answer alone is insufficient.
3. Retain the incident evidence. If capability is still missing, stop the
   dependent review and diagnose the concrete result; no shell fallback,
   permission weakening or silent alternate profile.
4. After successful capability proof, prepare a new complete four-leg review.
   Prior R2 remains NOT_APPROVED; no partial approval carries forward.

## Observed result

Canonical setup exited 0 without `--replace`; installed files match both manifest
hashes. Existing A-owned profile hashes are unchanged. Evidence:
`_runs/spec-plan-20261009/agy-profile/installed.json` (the copied `target_exists`
fields describe the pre-install snapshot; `verified` records the post-install check).

Workspace `_runs/infra/20261009-spec-to-code/agy-profile-capability/run.py` ran
once, 15:37:40–15:38:11 KST. AGY 1.3.2 Pro/high selected
`triad-codex-readonly-review` through real global lookup and formal v2 preflight.
Captured `grep_search` DONE found `receipt.txt:TRIAD_DISCOVERY_PROBE=cedar-4827`;
`view_file` DONE then read that fixture. Vendor and wrapper exited 0. The first
finish call used schema_version 1 and was rejected; the same conversation
corrected it to 2 and completed. No wrapper retry or schema relaxation occurred.
This proves this Pro/no-web fixture path, not every model/web combination or a
product SAFE verdict. Evidence: `summary.json`, `observed-tools.json`, `result.json`
beside the script. Logs were inspected for this explicit capability incident only.

Separate Gemini CLI: local version remains 0.60.0, below the required 0.63.0 floor.
Official v0.63.0 `packages/core/src/config/config.ts` lines 3756–3817 register
directory, file, grep/ripgrep and glob tools by default unless configured otherwise.
The B Gemini policy allows these native tools; it does not select an AGY profile.
No supported-version Gemini live search was run, and no global upgrade occurred.

Fresh R3 review completed with all four selected reviewers SAFE and matching
integrity; six nonblocking Minor findings have recorded dispositions. Evidence:
workspace `_runs/reviews/triad-opus-default-20261009-r3/`. This does not authorize product
merge, release, global permission edits, or removal of the task's SoT hook.
