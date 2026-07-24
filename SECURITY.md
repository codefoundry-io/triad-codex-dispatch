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

Formal plan and pre-merge three-family gates use one leader-prepared shared review
directory containing current approved production source, configuration, and
documentation. Project instructions or the owner supply exact test-source
exclusions; do not infer them. If the exact boundary is unavailable, stop and ask
the owner. Normal SDD implementation review includes relevant test source. Other
advisory review follows its separately owner-approved data scope.

Every leg receives the same directory and task. No prompt inlines a diff or file
body. Record one simple content digest before dispatch and compare it after every
required leg terminates; a mismatch invalidates the round. Before a formal gate,
classify every test failure as production defect, test-case defect, or intentional
specification change and resolve or approve it. Reviewers do not run candidate code,
tests, builds, hooks, or generated scripts.

The provider-visible security boundary remains unchanged: exclude credentials,
tokens, cookies, authentication files, environment dumps, provider logs, and
unrelated paths. Commit, push, install/update, merge, release, and publication
still require separate owner authorization.

Gemini fallback is restricted to explicit pre-submission agy route unavailability;
uncertain and post-dispatch outcomes remain on the agy failure path. Provider-side
enforcement remains unproven, so formal Gemini fallback stays closed unless the
owner supplies the evidence defined by the
[formal reviewer routing contract](skills/triad-cross-family-review/references/reviewer-routing.md).
The distribution does not probe for that evidence. Every
normal non-`--repair-mode` wrapper invocation that reaches its
dispatch driver performs best-effort cleanup of managed UUID/file-IPC entries
older than 3,600 seconds before provider execution; Antigravity performs it
before `--preflight-only` as well. Cleanup errors never block dispatch, and no
perfect garbage collector is claimed.

## Auto-review boundary

Human-run bootstrap preserves the owner's approval, reviewer, sandbox, and other
ordinary Codex keys. It adds a provenance-marked
`[shell_environment_policy]` guard so loader/interpreter injection variables are
removed before a launcher executes outside the sandbox; an owner-authored or
edited policy is preserved with a warning. Provenance-marked rules match only
the absolute managed launchers for the Claude,
Antigravity, and Gemini wrappers and use `decision = "prompt"`. They do not grant
a broad shell, generic Python, or repository-wrapper prefix. The prompt
justification identifies the exact call as an owner-authorized triad review and
requires provider-visible input to exclude credentials, tokens, cookies,
authentication files, environment dumps, provider logs, and unrelated paths.

Those prompts reach Agent Review only when the active configuration uses
`approvals_reviewer = "auto_review"` and keeps the relevant categories
interactive. `approval_policy = "on-request"` is sufficient. Under an existing
granular policy, both `granular.rules = true` and
`granular.sandbox_approval = true` are required; every other category remains
owner-controlled. `approvals_reviewer = "user"` sends the prompt to the person,
and `approval_policy = "never"` means Agent Review does not run.

When rules are opted out and no configured rules path remains
(`TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=0`), bootstrap may skip the native loader
guard. If an owner-managed rules file remains at that path, the guard is
retained because it may still activate a managed launcher; the launcher's own
scrub remains defense in depth in either case.

Bootstrap keeps selected profile, rules, and shell targets under strict,
no-follow preflight. If an unsafe or unreadable legacy profile or shell path is
not selected, its inspection failure is instead a warning: the refusal detail
and path are reported, the target is not followed or changed, and installation
of selected ordinary artifacts continues. The legacy profile requires
`TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1`; the legacy shell entry requires both
that flag and `TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1`.

All ownership preflights run before persistent publication. Provider wrapper
commands are staged and published only after the repair lifecycle has installed
the analyzer, registration, and `triad-apply-repair` transaction successfully.
A late repair-registration failure therefore leaves the provider launchers,
`triad-apply-repair`, analyzer/registration, command rules, and shell entry
absent while preserving unrelated owner bytes.

The setting and rule semantics follow OpenAI's
[Auto-review](https://learn.chatgpt.com/docs/sandboxing/auto-review),
[rules](https://learn.chatgpt.com/docs/agent-configuration/rules), and
[approval-policy](https://learn.chatgpt.com/docs/config-file/config-advanced#approval-policies-and-sandbox-modes)
documentation.

Bootstrap does not install `[auto_review].policy`, because replacing the owner's
reviewer instructions is broader than this plugin and managed policy has higher
precedence. The explicit owner request plus the exact rule justification is the
default-policy authorization evidence. `/approve` is a narrow, owner-operated
retry for one recorded denial and never becomes a broad allow rule.

Automatic review is an execution-time security decision, not a new source of
workflow authorization. Denial, timeout, missing authorization, and unsafe
input fail closed. Commit, push, plugin or dependency install/update, merge,
release, and publication still require separate owner authorization. The normal
distribution does not create a no-prompt or session-wide `never` posture.

The ordinary-Codex path also does not install the legacy profile's per-session
exec-target write denies. Bootstrap checks at install time that its launcher,
runtime, `$CODEX_HOME`, and plugin checkout are outside the
directory from which bootstrap runs. It cannot constrain a later Codex session
started with a broader writable root. Start ordinary Codex at the actual project
or workspace root, not `$HOME` or another ancestor of the managed launchers,
`$CODEX_HOME`, or plugin cache. Otherwise workspace-write access can make a
policy-matched executable rewritable. The legacy profile is explicit opt-in
migration compatibility for owners who require that additional per-session deny.

Bootstrap pins the installer-selected Python into generated launchers. This is
an explicit installation and operation precondition, not a fully closed launcher
guarantee: credential-compatible user-site mode requires a trusted `HOME`,
because `sitecustomize.py`/`usercustomize.py` from the HOME-selected user site can
run before launcher scrubbing. The installer may instead select a trusted
isolated Python environment only if it preserves the provider login workflow.

## Authentication and reports

The toolkit neither issues nor copies credentials. Owners authenticate provider
CLIs in their normal terminals. It has no credential copying, sandbox-login
attempt, company setup flow, or authorization store. Report security-sensitive issues on the product
issue tracker with a `[security]` title and never include credentials or tokens.

See [the repair protocol](docs/references/repair-protocol.md) for the exact
handoff and apply contract.
