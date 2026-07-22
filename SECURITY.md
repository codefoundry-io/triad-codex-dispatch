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
Pydantic 2 surface used by formal review before any persistent mutation. It
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

A formal triad review freezes all reviewed bytes and hashes under one review ID.
Changing any reviewed byte invalidates that round. A targeted rerun can be
advisory, but only a fresh ID with every required family is a new formal gate.
Formal legs use the exact packaged `triad_formal_review_schema:FormalReview`
operand, the `Critical | Major | Minor` severity vocabulary, and citations to
exact manifest-enumerated paths under the immutable packet root. Claude and
Gemini wrappers accept only the paired root/digest context required by that
schema. A sealed formal call verifies `PACKET_SHA256, SHA256SUMS, and
INPUT_SHA256SUMS` before provider resolution and fails before provider startup
when that context is incomplete or unsupported. The model reads
`INPUT_SHA256SUMS` and cited files through no-follow, root-confined descriptors,
then verifies the digest, UTF-8 text, and line range. Gemini fallback is
restricted to explicit pre-submission agy route unavailability; uncertain and
post-dispatch outcomes remain on the agy failure path.

Sealed formal wrapper invocations do not perform a hidden schema-repair retry:
`schema-fail is terminal for that invocation`. A leader may make an explicit new
invocation after deciding what to do. This schema rule does not disable
documented same-prompt capacity/transport recovery or the Antigravity headless
soft-deny adaptation; those preserve the review prompt and packet identity and
do not create a replacement formal leg. Every normal non-`--repair-mode`
wrapper invocation that reaches its dispatch driver performs best-effort cleanup of managed
UUID/file-IPC entries older than 3,600 seconds before provider execution; Antigravity performs it
before `--preflight-only` as well; cleanup errors never block dispatch, and no perfect garbage
collector is claimed.

## Authentication and reports

The toolkit neither issues nor copies credentials. Owners authenticate provider
CLIs in their normal terminals. It has no credential copying, sandbox-login
attempt, company setup flow, or authorization store. Report security-sensitive issues on the product
issue tracker with a `[security]` title and never include credentials or tokens.

See [the repair protocol](docs/references/repair-protocol.md) for the exact
handoff and apply contract.
