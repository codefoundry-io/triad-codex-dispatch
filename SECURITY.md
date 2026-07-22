# Security model

Vendor run logs are untrusted. A failed provider call can contain model output,
prompt text, stderr, and attacker-controlled instructions, so the component that
reads a log must not be able to edit the classifier it proposes to change.

## Repair boundary

The installed `triad-repair-analyzer` Custom Agent is the sole log reader. Its
registered profile is read-only and its contract permits only a compact JSON
proposal or escalation. It receives an absolute log path as data, not inline
log text, and it does not make provider, authentication, or network calls.

The analyzer never writes a classifier. The owner applies a proposal later with
the installed `triad-apply-repair --cli <cli> --proposal-file <absolute-path>`
executable from a normal authenticated terminal. That deterministic, zero-LLM
path parses and validates the proposal before it changes persistent classifier
state. A proposal that fails validation leaves the classifier unchanged.

The leader renders the owner command from an argv list using Python
`shlex.join`. That preserves one proposal-path argument even for spaces, quotes,
`$()`, or backticks and prevents shell-text reconstruction.

Bootstrap likewise resolves one Python runtime and feature-probes the exact
Pydantic 2 surface used by the toolkit before any persistent mutation. It
does not invoke `pip` or download packages. If the probe fails, it renders an
argv-safe `python -m pip install -r <absolute requirements.txt>` command for the
owner to run in that same Python environment from a normal terminal.

## Selector and lifecycle

The analyzer is selected only with
`agent_type="triad-repair-analyzer"` and `fork_turns="none"`. `task_name` is a
thread label. The installed agent owns its model, reasoning effort, and read-only
sandbox. If the selector is unavailable, the owner runs bootstrap in a normal
terminal and restarts Codex; the repair route does not substitute a generic
agent.

Failure logs remain until their age-floor cleanup. The repair route does not
remove them early because the analyzer and owner apply step may still need the
record.

## Residual risk and formal review

Validation blocks malformed or out-of-policy proposals, but a valid proposal can
still be a poor classification. Treat it as an integrity and routing risk, not a
code-execution boundary. Inspect applied deltas and use the normal review process
for material changes.

A formal triad review uses the existing worktree as its only source root. The
leader resolves one absolute Git worktree and captures one trusted status/diff
with fixed, non-mutating Git arguments. Every family receives the same worktree,
scope, objective, suspect decisions, and captured output. The diff is an entry
point rather than a review boundary: no-edit reviewers directly read and search
affected unchanged callers, consumers, tests, build files, configuration, and
governing documentation when relevant. Reviewers may inspect Git and source but
do not execute candidate code, tests, builds, hooks, or generated scripts.

Before dispatch, the leader records a lightweight fingerprint of `HEAD`, the
selected diff, the complete untracked-path inventory, and Git object hashes for
untracked contents. The same fingerprint is recomputed after all legs return.
Any change invalidates the whole round because families may have observed
different states; an unchanged result admits reconciliation. The leader does
not edit the worktree while reviewers are running.

The default path creates no source copy, packet, manifest, generated related-file
allowlist, or snapshot. A source archive is not a hidden formal-gate
prerequisite. Small review records may retain the review ID, scope, pre/post
fingerprint, exact provider commands, and reviewer outputs, but not copied
source or authentication material. The packet-bound `FormalReview` schema and
sealed-packet flags are not used by normal or formal worktree review. Legacy
wrapper support may remain for explicit compatibility, but no installed skill
or default gate directs users through it.

Gemini fallback is restricted to explicit pre-submission agy route unavailability;
uncertain and post-dispatch outcomes remain on the agy failure path. Every
normal non-`--repair-mode` wrapper invocation that reaches its
dispatch driver performs best-effort cleanup of managed UUID/file-IPC entries
older than 3,600 seconds before provider execution; Antigravity performs it
before `--preflight-only` as well. Cleanup errors never block dispatch, and no
perfect garbage collector is claimed.

## Auto-review boundary

Human-run bootstrap installs a dedicated triad Codex profile with
`approval_policy = "on-request"` and `approvals_reviewer = "auto_review"`.
Provenance-marked rules match only the absolute managed launchers for the Claude,
Antigravity, and Gemini wrappers and use `decision = "prompt"`. They do not grant
a broad shell, generic Python, or repository-wrapper prefix. The prompt
justification identifies the exact call as an owner-authorized triad review and
requires provider-visible input to exclude credentials, tokens, cookies,
authentication files, environment dumps, and unrelated paths.

Automatic review is an execution-time security decision, not a new source of
workflow authorization. Denial, timeout, missing authorization, and unsafe
input fail closed. Commit, push, plugin or dependency install/update, merge,
release, and publication still require separate owner authorization. The
explicit `TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never` compatibility posture is an
advanced exception: it rewrites the managed rules to `allow`, disables automatic
review for that dedicated session, and must not be treated as the default.

## Authentication and reports

The toolkit neither issues nor copies credentials. Owners authenticate provider
CLIs in their normal terminals. It has no credential copying, sandbox-login
attempt, company setup flow, or authorization store. Report security-sensitive issues on the product
issue tracker with a `[security]` title and never include credentials or tokens.

See [the repair protocol](docs/references/repair-protocol.md) for the exact
handoff and apply contract.
