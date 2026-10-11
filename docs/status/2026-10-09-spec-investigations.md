# Shared-spec planning investigations — 2026-10-09

Status: bounded research completed; unresolved live effects are explicitly NOT
RUN. This is evidence for the execution plan, not a formal review or a product
completion/adoption claim. No product code changed during these investigations.

## Basis and concurrent ownership

Shared main `3afc4d7`; PR #12 `1a5ab9a`; PR #13 `cff8a20`, all rechecked remotely.
B HEAD `632f426` plus preserved dirty source. A was inspected at
`32124be528ab736cad6ac8d8f76990d99bdf3556`; source and dirty state may advance
independently. A's ongoing implementation can legitimately lag the shared spec.
The native leg of either host is excluded.

Four fresh research children used requested `gpt-6.1-sol` / `medium`,
`fork_turns="none"`: `credit_carrier_research`, `agy_schema_spike`,
`cross_host_contract_audit`, `model_argument_spike`. These are research roles,
not formal gate reviewers. The leader inspected reports and primary evidence.

## 1. AGY credits sentence: location and exit remain unknown

The official [1.2.15 changelog](https://github.com/google-antigravity/antigravity-cli/blob/main/CHANGELOG.md#1215)
documents the credits sentence. It does not identify its channel or exit.
Official [headless documentation](https://antigravity.google/docs/cli/headless/#handle-exit-codes-and-errors)
describes response stdout, diagnostic stderr and structured result errors.
Changelog 1.2.6/1.2.10 describes `AGY_ERROR` and exit 3 for model/API failures.
No primary evidence connects this particular credits condition to that path.

Disposition: retain the CLI-specific phrase classifier and UNMEASURED carrier.
Do not manufacture a quota event, infer exit 3, or invent a stream fixture.
Use an existing sanitized capture/vendor fixture, or preserve version, separate
channels, exit and terminal fields when the event occurs naturally in an already
authorized run. A balance query alone cannot establish a failure carrier.
Two GitHub issue-search pages failed to load; the search is not proof that no
capture exists anywhere. Public current docs are not installed-version proof.

## 2. DL-103: current route enum is already narrowed

Current dirty `bin/verdict_v2.py:45-46` intersects the bound route with `['agy']`.
`bin/antigravity_wrapper.py:472-478` binds the actual v2 class and `:666-677`
emits its schema. The old null-enum diagnosis is stale for this actual route.
The bound schema still contains `$schema`, `$id`, `allOf`, `not`, `uniqueItems`
and optional finding `correction`. A's projection is broader, but its recorded
AGY rejection concerns null enum; other quoted rejections concern Codex.
That is not evidence that AGY rejects every removed keyword.

Provider-free checks: **95 passed, 4 skipped** (7.18s), Python 3.12.13, pytest
9.0.3, macOS. Exact command and source analysis:
[`findings.md`](../../_runs/spec-plan-20261009/schema/findings.md).
Fixtures replace provider execution/version/settings guards, so they prove
emitted schema and local admission wiring, not vendor acceptance.

Retained artifacts: `../../_runs/spec-plan-20261009/schema/` contains the actual
sanitized bound schema (SHA-256
`dc890584be107a35e5febdbfa06ced265f4ae2bf80995814600e5019401e2bd6`) and a proposed
one-process, 60-second, no-launcher-retry probe. **Live NOT RUN.** The initial
diagnostic runner inherited environment and omitted normal host preflight and
containment integration; the leader rejected executing it. It must remain a
non-executable design until those boundaries are included. Neither plan mode
nor a successful raw schema call alone would prove complete wrapper conformance.
U3 owns the bounded real-route check before any remaining compatibility fix.

## 3. DL-124..126: no new B implementation requirement found

At the inspected A commit:

- `agy_hook.py check <audit> <hook-log>` attributes rows using that attempt's
  conversation IDs. Removed sibling census/retry guards have no B counterpart.
- A and B skip undecodable/non-JSON rows and retain the last dict result on the
  relevant parser path. A's read-only admission still has separate framing and
  one-result controls; this is not a claim of total stream-admission equivalence.
- A writes one override audit, atomically, mode 0600. B has no A-style duplicate
  `read-audit-copy:` publication path to remove.

Disposition: no port. Reconcile historical DL-6/10/11/12/13 pointers, C1/C23/C36
test references and R-CONTAIN's custody-line list in the shared spec. A remains
the owner of its source and test assertions. An unmeasured conversation-ID reuse
is a recorded limit, not a new B refusal mechanism.

## 4. DL-110/121: document the host that still produces the result

PR #12 records these corrections but does not yet apply them:

- `contracts/exit-tokens.json`: keep `task-blocked`; B's external Claude
  wrapper produces it, A retains membership only after its wrapper removal.
- R-CLASSIFY: A has two extractors (codex, gemini), not three.
- C35 `tests.A`: remove the claim about Claude CLI effort reporting.
- C37/C43 `tests.A`: remove obsolete Claude CLI axes; ask A to confirm remaining
  exact test names/counts instead of inventing replacements.

Disposition: concrete pending spec reconciliation, not a B wrapper removal.
Preserve historical withdrawn evidence as history. Do not mark A's ongoing
implementation defective merely because old text has not caught up yet.

## 5. Model argv: Gemini parser evidence now exists

The spike used the official Gemini CLI **0.63.0 npm bundle**, preserving its
actual yargs engine and `parseArguments`; external startup helpers were inert.
It did not invoke configuration/auth/provider startup. Installed global Gemini
0.60.0 was not substituted for the requested version.

| Exact parser input | Observed result |
|---|---|
| `--model --help` or `-m --help` | help, exit 0; model value reinterpreted |
| `--model --yolo` / `--model --made-up-model` | missing-value parse error, exit 1 |
| `--model=--help` / `--model=--yolo` / `--model=--made-up-model` | exact model value; `yolo` false |
| unknown model, spaces/newline/tab inside one token | preserved by this parser in both encodings |

Primary [parser source](https://github.com/google-gemini/gemini-cli/blob/v0.63.0/packages/cli/src/config/config.ts)
and [official npm artifact](https://registry.npmjs.org/@google/gemini-cli/-/gemini-cli-0.63.0.tgz)
are recorded with the extraction boundaries and SHA-256 in
[`report.md`](../../_runs/spec-plan-20261009/model-argv/report.md).
Artifact SHA-256:
`97a6edfc10645463b517f0518d46a8c72efbdc12558a9a948607f726284a0420`.

AGY 1.3.2 / Claude 2.1.289 help-path probes expose no parsed model and remain
inconclusive. No inference or permission escalation was demonstrated. Current
Python wrapper and adapter option parsing is another boundary to test.

Disposition: propose lossless opaque-value transport under existing R-MODEL,
not a new blanket model-name grammar. U1T validates compatible encoding at each
boundary and obtains a new gate before changing product source. Arbitrary
control characters, NUL and future CLI versions were not tested.

## Evidence retention and next actions

The two scratch evidence directories are retained for reproduction; their files
are not product dependencies or runtime instruction sources. No broad cleanup
of other work was performed. Shared facts and maintainer follow-up are recorded
in `decisions/2026-10-09-execution-planning.md` in the shared spec checkout.
The execution plan and SoT identify the next bounded unit and owner decisions.
