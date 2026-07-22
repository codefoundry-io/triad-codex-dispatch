# triad-codex-dispatch

[한국어 README](README.ko.md)

**Your AI coding assistant shares blind spots with its own reviewers.** Ask
codex to check codex's work and it inherits the same framing — the reasoning that
produced the bug is the reasoning that reviews it. triad-codex-dispatch gets you a
second and third opinion from a **different model family**: codex stays the leader
and dispatches **Claude Code** (Anthropic) and **antigravity / `agy`** (Google) as
single-shot workers, and before you merge a risky change it runs a review where
each family independently challenges the decision — so the bug your main model
rationalized away gets caught by a model that never had that blind spot.

You install it as a codex plugin and keep driving from codex; when a question
needs an outside opinion, or a change is risky enough to merge-block, the leader
reaches out to the other families for you.

> **Sibling product:** if your team leads with **Claude Code** instead of the
> codex CLI, see **[triad-dispatch](https://github.com/codefoundry-io/triad-dispatch)**
> — the same three-family model with Claude Code as the driver. This one is for a
> codex driver.

## What You Get

- Codex plugin skills under `skills/`.
- Bootstrap newly publishes only three provider wrapper commands: Claude, agy,
  and Gemini. `triad-setup` and `triad-doctor` are remove-only legacy cleanup
  names.
- A generated Codex profile on the Codex permission-profile system
  (`default_permissions = "triad_leader"`, extending `:workspace`; no legacy
  `sandbox_mode` keys) plus command rules for the wrapper launchers — both
  installed by default. By default, the generated triad profile omits
  `approval_policy` and `approvals_reviewer`, so Codex inherits the owner's
  existing layered approval configuration unchanged.
- One installed read-only `triad-repair-analyzer` Custom Agent for classifier
  gaps. The analyzer returns a proposal; the leader writes only that proposal
  to a unique UTF-8 JSON file. The owner applies it with the deterministic
  installed `triad-apply-repair` executable from a normal authenticated
  terminal. Legacy three-agent files are migration quarantine or removal
  material, not an active repair route.
- An optional managed `codex-triad` shell entry
  (`TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1`) — the required start for the
  no-prompt posture.

## Required (~2 minutes)

Three steps get you a working install that preserves your existing approval
configuration. Everything past this section is optional.

1. **Native vendor logins.** Install and log in to the leader `codex` and the
   workers you will use — the toolkit issues/refreshes no credentials:
   - `codex` — install, then `codex login`.
   - `agy` — install + OAuth sign-in (the Google-family worker for individual
     users).
   - `claude` — Claude Code `>= 2.1.170`; bootstrap checks binary presence only
     and does not run a version probe.

   You also need `git`, `python3 >= 3.12`, and Pydantic 2 in that same Python
   runtime. The runtime dependency is declared in the shipped
   `requirements.txt`. Keep
   `~/.local/bin` on `PATH` (or set `TRIAD_BOOTSTRAP_BIN_DIR` to a directory
   already on `PATH`). `gemini` is optional — see
   [Optional / Advanced](#optional--advanced).

2. **Plugin install (Codex can do).** No local clone is required for normal
   users. Codex may run these commands when its current approval boundary
   permits the install:

   ```bash
   codex plugin marketplace add codefoundry-io/triad-codex-dispatch --ref main
   python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","add","triad-codex-dispatch@triad-codex-dispatch","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); root=pathlib.Path(data["installedPath"]); assert root.is_absolute(); print(shlex.join([str(root / "scripts" / "bootstrap.sh"),"--install"]))'
   ```

3. **User-run runtime setup.** The plugin installer does not run arbitrary
   post-install code. The last command in step 2 prints a safely quoted absolute
   bootstrap command from the returned `installedPath` with Python
   `shlex.join`. Run that printed command exactly in your normal login terminal.
   Its shebang makes the shipped script directly executable.

   Before its first mutation, the script verifies that the selected Python can
   import the Pydantic 2 APIs used by formal review. If not, it stops and prints
   an argv-safe command equivalent to
   `python3 -m pip install -r <absolute-plugin-path>/requirements.txt`. Run that
   command in the Python environment you own, then rerun bootstrap. Bootstrap
   does not install Python packages itself.

   The script installs the runtime profile, command rules, and three provider
   wrapper commands. It does not run provider login or model probes. The
   installed absolute-launcher rules automatically allow those wrapper commands
   to run outside the sandbox without a repeated approval prompt. Other
   commands continue to use your inherited approval configuration.

   > **Placement invariant (hard).** Run bootstrap from your project workspace,
   > not from a directory that contains the install targets. Bootstrap writes the
   > profile + command rules under `$CODEX_HOME` (default `~/.codex/`), classifier
   > patches under `~/.config/triad-codex-dispatch/`, and launchers under
   > `~/.local/bin` (or `TRIAD_BOOTSTRAP_BIN_DIR`). Those targets — and everything
   > they exec (the plugin cache, the `python3` runtime) — must live outside all
   > sandbox-writable roots; bootstrap hard-fails if any resolves inside the
   > directory it runs from (for example `$HOME`).

   Then start a new Codex session from the target workspace:

   ```bash
   codex --profile triad-codex-dispatch --search
   ```

That is the whole required path. Repair is a manual, read-only step surfaced only
when needed (see [Custom Subagents](#custom-subagents) and [Security](#security)).

## Optional / Advanced

Nothing in this section is needed for a normal individual install. Reach for a
subsection only when its "do this ONLY if…" line applies to you.

### No-prompt posture (heavy users)

The installed absolute-launcher rules automatically allow the three provider
launchers; other commands use your inherited approval configuration. *Do this ONLY if
you want the whole dedicated triad session
to have no interactive approval requests and to start with the hardened wrapper
environment pinned.* Add `TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never` plus the
managed shell entry to the bootstrap command.

Setting `TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never` explicitly emits only
`approval_policy = "never"`; it remains an opt-in advanced mode and never
changes `approvals_reviewer`.

> **Warning — session-wide scope.**
> `approval_policy=never` applies to the whole triad Codex session, not only this
> plugin. Do not run unrelated work in that session.

Set the two options in the normal terminal:

```bash
export TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1
export TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never
```

Then run the freshly printed absolute bootstrap command again. Re-run the step
2 printer first if the plugin has been updated or reinstalled.

The ONLY supported start for this session-wide no-prompt posture is the managed `codex-triad`
function that `TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1` appends to your shell RC
(default `~/.bashrc`; `~/.zshrc` for zsh; `TRIAD_BOOTSTRAP_SHELL_RC` overrides).
It pins the wrapper-containment envs (these gate path/pydantic handling in the
wrapper process; they are not a claim of OS-level confinement — see
[SECURITY.md](SECURITY.md)):

```bash
codex-triad() {
  TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}" \
  TRIAD_WRAPPER_HARDENED=1 \
  TRIAD_CLAUDE_ENFORCE_SANDBOX=1 \
    command codex --profile triad-codex-dispatch --search "$@"
}
```

Open a new terminal (or source your shell RC), then run `codex-triad` from the
target workspace. Never start the no-prompt profile with a bare
`codex --profile ...` line: it lacks the pinned wrapper containment envs.

### Enterprise Gemini worker

*Do this ONLY if you have a business / Vertex / API-key Gemini account.* Install
`gemini` and log in; individual Google-family users should use `agy` instead. Set
`TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1` if a team wants bootstrap to require it.
Bootstrap labels executable presence as a Gemini fallback candidate only; it
does not run authentication, model, or version probes. Before a formal review
counts this fallback, prove it with a successful preflight or dispatch in the
owner's normal authenticated terminal. Gemini fallback is eligible only when
the agy route is explicitly missing or unstartable before request submission;
`phase=pre-dispatch-settings` is necessary but not sufficient, and uncertain or
post-dispatch phases are ineligible. A direct Gemini request does not bypass the
agy-first rule; content, schema, timeout, capacity, or post-dispatch failures
remain on the agy failure path.

### Opt out of the default profile or rules

*Do this ONLY if you do not want the profile and/or command rules installed.*
The profile and rules install by default; suppress either with an explicit `=0`
or the `SKIP` escape:

Export `TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=0` and/or
`TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=0` in the normal terminal, then run the
freshly printed absolute bootstrap command. The equivalent skip flags are
`TRIAD_BOOTSTRAP_SKIP_CODEX_PROFILE=1` and
`TRIAD_BOOTSTRAP_SKIP_CODEX_RULES=1`.

### Linux / WSL2 sandbox support

*Do this ONLY on Linux or WSL2.* Install `bubblewrap` (`bwrap`) for Codex sandbox
support. The installer does not install OS packages.

### Read the security model

*Do this ONLY if you want the full threat model before relying on the toolkit.*
See [SECURITY.md](SECURITY.md) — the durable control is privilege separation, not
model trust (summarized under [Security](#security) below).

### Notes on re-running bootstrap

- `--check` is a deprecated alias for `--install`, kept for one release.
- The generated wrapper launchers call files from the installed plugin cache;
  rerun bootstrap after every plugin update so those paths stay current.
- The launchers pin resolved vendor CLI paths; rerun bootstrap after upgrading or
  moving `claude`, `agy`, or optional `gemini`.
- Existing Codex sessions may not see newly installed plugin skills; start a new
  session after install or update.
- agy calls may transact against Antigravity CLI runtime settings under
  `~/.gemini/antigravity-cli/`; that is provider runtime state, not a bootstrap
  install target.
- `codex plugin add --json` reports marketplace `authPolicy`; this plugin still
  does not perform CLI OAuth/login.

## Use

Ask Codex to use these installed skills:

- `triad-claude-dispatch`: single-shot Claude Code consult.
- `triad-antigravity-dispatch`: primary Google-family consult through `agy`.
- `triad-gemini-dispatch`: fallback-only after proven pre-submission agy
  unavailability for Gemini business/Vertex/API-key accounts.
- `triad-cross-family-review`: pre-merge review across Claude, Google-family,
  and a fresh Codex subagent.

### Your first dispatch

From the target workspace, start the leader and ask for a single consult:

```bash
codex --profile triad-codex-dispatch --search
```

Then, in that session:

> Use triad-claude-dispatch to ask Claude: what does `git rebase --onto` do? One paragraph.

Codex runs the `triad-claude-dispatch` skill, which calls the Claude launcher and
returns Claude's answer. You will see a one-line success summary on stderr:

```
[wrapper] claude ok exit=0 vendor=0 elapsed=6.4s
```

`[wrapper] claude` is the worker that ran; `ok` is the classification (a clean
answer); `exit=0` is success. Swap `triad-claude-dispatch` for
`triad-antigravity-dispatch` to consult the Google-family (`agy`) leg the same way.

Normal code-write dispatch should run from the target workspace. Path
containment is OPT-IN: the wrappers reject a `--cwd` / `--prompt-file` outside a
trusted root ONLY when `TRIAD_WRAPPER_ALLOWED_ROOTS` is set (the managed
`codex-triad` shell entry pins it together with `TRIAD_WRAPPER_HARDENED=1` — the
hardened path). By default they do not constrain paths; the boundary rests on the
isolated `--cwd` worktree + the Codex profile/rules.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Codex asks for approval before an installed wrapper call | The generated absolute-launcher rules are missing, disabled, or stale | Rerun the freshly printed bootstrap command with rules enabled. If you intentionally opted out of rules, the prompt is expected. Unrelated commands continue to use your inherited approval configuration; see [No-prompt posture](#no-prompt-posture-heavy-users). |
| A dispatch fails with `oauth-env` | The worker CLI's login expired or is missing | Re-run that vendor's native login (`claude` / `agy` OAuth, or `codex login`). The toolkit never re-authenticates for you — it surfaces the signal so you log in. |
| The gemini leg fails with `IneligibleTier` | The Gemini CLI *individual* tier is deprecated | Use the `agy` (Antigravity) leg — it is the Google-family leg for individual users. `gemini` is only for business / Vertex / API-key accounts. |
| A new skill isn't available after install/update | Existing Codex sessions don't see newly installed skills | Start a new Codex session (and rerun `bootstrap.sh --install` after a plugin update so launcher paths stay current). |
| A dispatch returns non-zero and you want to know what happened | The numeric exit code is always authoritative; a completed wrapper failure normally also emits a final classification | See the exit-code legend below. When a final `[wrapper] …` stderr line exists, use its classification; preserve an early no-summary failure as-is. |

**Exit-code legend** (the wrapper's process exit code; when a final wrapper
summary exists, its class appears on the `[wrapper] <cli> <class> …` stderr line):

| Exit | Meaning | What to do |
|---|---|---|
| `0` | Success — the answer follows | Nothing. |
| `4` | The configured provider binary was missing or not executable before submission | Fix that binary. For the AGY route only, Gemini Enterprise fallback is eligible when the wrapper-owned diagnostic also proves this pre-submit failure. |
| `64` | Server capacity exhausted after retries | Transient vendor overload; wait and retry. |
| `65` | Auth / config / quota (e.g. `oauth-env`, `cli-subscription-cap`) | Re-login or wait for the quota reset — see the classification word. |
| `66` | Structured-output (`--pydantic`) schema validation failed | In a sealed formal call, `schema-fail` is terminal for that invocation; the leader may make an explicit new invocation after deciding what to do. |
| `69` | A code task was blocked / needs more context (codex `--task code`) | Provide the missing context and re-dispatch. |

## Scope & Limits — What This Does NOT Do

Honest boundaries, so you know where the toolkit stops:

- **It does NOT manage vendor auth or tokens.** No token issue/refresh, no API-key
  injection, and no install-time provider probes. You log in with each vendor
  CLI's native login; an auth-shaped runtime error is surfaced for you to
  re-login. There is no credential copying, sandbox-login attempt, company setup
  flow, or authorization store.
- **It does NOT install OS or Python packages.** You install the vendor CLIs,
  `python3`, the shipped Python requirements, and (on Linux/WSL2) `bubblewrap`
  yourself; the installer only writes the profile, rules, and launchers. If the
  selected Python is missing Pydantic 2, bootstrap stops before mutation and
  prints the exact `python3 -m pip install -r .../requirements.txt` command for
  that interpreter.
- **The self-improving classifier is a heuristic, not an oracle.** It can route a
  genuine failure to a wrong-but-plausible class. The worst case is an *integrity*
  issue — a persistent routing mis-classification, NOT code execution (see
  [Security](#security)) — but you should periodically review the applied deltas in
  `~/.config/triad-codex-dispatch/classifier-patches.json`. Bootstrap pins the
  resolved absolute path into every provider and apply launcher; rerun bootstrap
  after changing `TRIAD_CLASSIFIER_EXTENSION`.
- **Wrapper containment is process/permission-level, not OS-level confinement.**
  The wrapper-containment envs gate path/pydantic handling in the wrapper process;
  they are not a claim of OS-level isolation. The boundary rests on the isolated
  `--cwd` worktree + the Codex profile/rules + your review before commit.

## Update

```bash
codex plugin marketplace upgrade triad-codex-dispatch
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","add","triad-codex-dispatch@triad-codex-dispatch","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); root=pathlib.Path(data["installedPath"]); assert root.is_absolute(); print(shlex.join([str(root / "scripts" / "bootstrap.sh"),"--install"]))'
```

Run the newly printed absolute command. A plain `--install` reapplies the
default profile and rules; set any opt-in flags again before running it. Start a
new Codex session after updating.

## Verify The Install

### Plugin-only smoke test (no clone required)

This is the normal path — it confirms the toolkit is live without cloning
anything. Start the leader from your target workspace and ask codex to run a
trivial Google-family dispatch:

```bash
codex --profile triad-codex-dispatch --search
```

Then, in that session:

> Use triad-antigravity-dispatch to ask agy: what does `git rebase --onto` do? One paragraph.

Expect agy's answer plus a one-line success summary on stderr:

```
[wrapper] antigravity ok exit=0 vendor=0 elapsed=6.4s
```

That `[wrapper] antigravity ok …` line is your signal the dispatch worked — the plugin,
launchers, and profile are all wired. `ok` is the classification; other values
(e.g. `oauth-env`, `server-capacity`) name a specific failure — see
[Troubleshooting](#troubleshooting).

### Developer path (optional — clone + pytest)

If you want to run the bundled unit tests, clone the repository and run them.
This needs `pytest` (`python3 -m pip install pytest`), a test-only dependency not
needed to run the dispatch tools themselves:

```bash
git clone https://github.com/codefoundry-io/triad-codex-dispatch
cd triad-codex-dispatch
python3 -m pytest -q tests/ -p no:cacheprovider   # expect all tests to pass
```

## Remove

Resolve the current installed plugin path in a fresh shell and print the managed
uninstall command before removing the plugin cache (the script lives inside
it):

```bash
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","list","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); item=next(item for item in data["installed"] if item["pluginId"]=="triad-codex-dispatch@triad-codex-dispatch"); root=pathlib.Path(item["source"]["path"]); assert root.is_absolute(); print(shlex.join([str(root / "scripts" / "bootstrap.sh"),"--remove"]))'
```

Run that printed absolute removal command, then remove the plugin registration:

```bash
codex plugin remove triad-codex-dispatch@triad-codex-dispatch
codex plugin marketplace remove triad-codex-dispatch
```

`--remove` (alias `--uninstall`) deletes the wrapper launchers, the installed
`triad-repair-analyzer`, the managed profile and command rules, and the managed
`codex-triad` shell entry. It also deletes legacy three-agent TOMLs left by an
older install. Learned classifier patches are intentionally preserved; they are
outside managed uninstall and should be deleted separately only when the owner
intends to discard learned routing.

## Custom Subagents

Classifier repair uses the installed read-only
`agent_type="triad-repair-analyzer"` with `fork_turns="none"`; `task_name` is
only a label. The installed agent owns its model, effort, and sandbox settings.
It returns a proposal or escalation and cannot apply a patch. The leader stores
only the proposal in a unique UTF-8 JSON file, then renders the owner command
from an argv list with Python `shlex.join`:

`triad-apply-repair --cli <cli> --proposal-file <absolute-path>`.

Run that installed executable in the owner's normal authenticated terminal. If
the agent selector is unavailable, run bootstrap there and restart Codex; do not
downgrade to a generic agent. The run log remains until age-floor cleanup.

If you create your own Codex custom subagent that should call triad dispatch
skills, opt in explicitly with Codex `skills.config` entries pointing at the
needed `SKILL.md` files under the current installed plugin `source.path` from
live `codex plugin list --json` output.

After editing custom-agent TOML files, start a new Codex session.

## Runtime Logs And Local Data

Runtime telemetry is local under the installed plugin's `bin/_logs/<cli>/`.
`audit.jsonl` keeps redacted argv, prompt length, status, 500-character
stdout/stderr heads, and structured-output presence/length only. Failure run
logs keep full prompts and vendor transcripts as untrusted repair evidence and
remain until their age-floor cleanup. Treat these files as sensitive and remove
`bin/_logs/` when needed.

For a formal sealed call, the wrapper verifies `PACKET_SHA256, SHA256SUMS, and
INPUT_SHA256SUMS` before provider resolution. Every normal non-`--repair-mode`
wrapper invocation that reaches its dispatch driver performs best-effort cleanup of managed
UUID/file-IPC entries older than 3,600 seconds before provider execution; Antigravity performs it
before `--preflight-only` as well; cleanup errors never block dispatch, and this is not a perfect
garbage collector. A sealed formal schema failure is terminal: `schema-fail is terminal
for that invocation`; the leader may make an explicit new invocation after
deciding what to do. This schema rule does not disable documented same-prompt
capacity/transport recovery or the Antigravity headless soft-deny adaptation;
those preserve the review prompt and packet identity and do not create a
replacement formal leg.

Antigravity settings under `~/.gemini/antigravity-cli/` are transacted during
agy calls. Avoid editing agy permissions during triad calls or running another
Antigravity settings change at the same time.

## Security

The durable control is **privilege separation**, not model trust: the installed
read-only analyzer reads the untrusted run log and returns a proposal only; the
owner-run deterministic `triad-apply-repair` executable validates and applies
that proposal. Full threat model: [SECURITY.md](SECURITY.md).

## Support

- Bugs and questions: https://github.com/codefoundry-io/triad-codex-dispatch/issues
- Security-sensitive reports: same tracker, title prefixed `[security]`; do not
  include secrets or tokens in the report body.

## Notes

- This plugin avoids `danger-full-access`.
- Generated command rules automatically allow only the absolute launcher files
  installed under `~/.local/bin` or `TRIAD_BOOTSTRAP_BIN_DIR`; those launchers
  validate their argv and call the installed plugin cache. Other commands remain
  under the profile's normal approval policy.
- The exact installed `triad-repair-analyzer` uses its pinned read-only sandbox;
  it returns a proposal or escalation and never applies a classifier change.
