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
- Exact command rules for the three managed wrapper launchers. They use
  `decision = "prompt"` and work from an ordinary `codex` session. Bootstrap
  does not install a dedicated profile and does not replace the owner's approval
  or reviewer settings, model, reasoning, or sandbox settings.
- One installed read-only `triad-repair-analyzer` Custom Agent for classifier
  gaps. The analyzer returns a proposal; the leader writes only that proposal
  to a unique UTF-8 JSON file. The owner applies it with the deterministic
  installed `triad-apply-repair` executable from a normal authenticated
  terminal. Legacy three-agent files are migration quarantine or removal
  material, not an active repair route.

## Required (~2 minutes)

Three steps get you a working install in ordinary Codex. Everything past this
section is optional.

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

   Bootstrap pins the installer-selected Python into the generated launchers.
   In credential-compatible/user-site mode, start Codex and the launchers with a
   trusted `HOME`: `sitecustomize.py`/`usercustomize.py` under the HOME-selected
   user site can run before launcher scrubbing. The installer may instead select
   a trusted isolated Python environment only if it preserves the provider login
   workflow.

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
   import the Pydantic 2 APIs used by the toolkit. If not, it stops and prints
   an argv-safe command equivalent to
   `python3 -m pip install -r <absolute-plugin-path>/requirements.txt`. Run that
   command in the Python environment you own, then rerun bootstrap. Bootstrap
   does not install Python packages itself.

   The script installs exact command rules and three provider wrapper commands.
   It also appends a provenance-marked repair-analyzer registration to
   `$CODEX_HOME/config.toml` and, when no owner-authored policy exists, a
   provenance-marked loader-environment guard. Every other config key is
   preserved; an owner-authored or edited environment policy is left untouched
   with a warning, and `--remove` strips only exact managed blocks. It does not
   install a dedicated profile, alter the owner's Codex approval/reviewer/sandbox
   keys, or run provider login or model probes. The exact absolute-launcher
   rules use `prompt`.

   Bootstrap publishes the provider wrapper commands only after the repair
   lifecycle has installed its analyzer, registration, and
   `triad-apply-repair` transaction successfully. A late repair-registration
   failure therefore leaves the provider launchers, `triad-apply-repair`,
   analyzer/registration, command rules, and legacy shell entry unpublished.

   For automatic Agent Review, use either:

   ```toml
   approval_policy = "on-request"
   approvals_reviewer = "auto_review"
   ```

   or preserve an existing granular policy while ensuring
   `granular.rules = true` and `granular.sandbox_approval = true`. The former
   keeps every eligible approval category interactive; the latter is required
   so exact rule prompts and sandbox escalation are not auto-rejected before
   Agent Review. Keep all other granular category choices unchanged. With
   `approvals_reviewer = "user"`, the wrappers still work but prompt the person.
   With `approval_policy = "never"`, Agent Review does not run.

   These settings follow OpenAI's [Auto-review](https://learn.chatgpt.com/docs/sandboxing/auto-review),
   [rules](https://learn.chatgpt.com/docs/agent-configuration/rules), and
   [approval-policy](https://learn.chatgpt.com/docs/config-file/config-advanced#approval-policies-and-sandbox-modes)
   documentation.

   The plugin does not install `[auto_review].policy`; doing so could replace
   the owner's reviewer instructions, and managed policy has higher precedence.
   The explicit owner request plus the exact rule justification supplies the
   authorization context. A denied exact action can be selected once through
   `/approve`; do not replace that narrow override with a broad allow rule.

   Automatic review is an execution-time security check, not owner workflow
   authorization. Commit, push, plugin or dependency installation, release, and
   publication remain separate owner decisions; the leader must not initiate
   them merely because `approvals_reviewer = "auto_review"` is active.

   > **Placement invariant (hard).** Run bootstrap from your project workspace,
   > not from a directory that contains the install targets. Bootstrap writes the
   > command rules and provenance-marked config registrations under `$CODEX_HOME`
   > (default `~/.codex/`), classifier
   > patches under `~/.config/triad-codex-dispatch/`, and launchers under
   > `~/.local/bin` (or `TRIAD_BOOTSTRAP_BIN_DIR`). Those targets — and everything
   > they exec (the plugin cache, the `python3` runtime) — must live outside all
   > sandbox-writable roots; bootstrap hard-fails if any resolves inside the
   > directory it runs from (for example `$HOME`).

   The normal path intentionally has no dedicated permission profile. Start
   ordinary `codex` at the actual project/workspace root, not `$HOME` or another
   ancestor of `~/.local/bin`, `$CODEX_HOME`, or the plugin cache. A later
   workspace-write session rooted above those managed executables could rewrite
   them; the install-time placement check cannot enforce a different future
   session root. The legacy profile remains an explicit migration-only option
   for owners who need per-session exec-target denies.

   Then start a fresh ordinary Codex session from the target workspace:

   ```bash
   codex
   ```

   Use `/status` to verify the active approval policy and `/debug-config` when a
   project, profile, or managed layer changes the expected reviewer.

That is the whole required path. Repair is a manual, read-only step surfaced only
when needed (see [Custom Subagents](#custom-subagents) and [Security](#security)).

## Optional / Advanced

Nothing in this section is needed for a normal individual install. Reach for a
subsection only when its "do this ONLY if…" line applies to you.

### Enterprise Gemini worker

*Do this ONLY if you have a business / Vertex / API-key Gemini account.* Install
`gemini` and log in; individual Google-family users should use `agy` instead. Set
`TRIAD_BOOTSTRAP_REQUIRE_GEMINI=1` if a team wants bootstrap to require it.
Bootstrap labels executable presence as a Gemini fallback candidate only; it
does not run authentication, model, or version probes. Ordinary/non-formal
Gemini fallback is eligible only when the agy route is explicitly missing or
unstartable before request submission; `phase=pre-dispatch-settings` is
necessary but not sufficient, and uncertain or post-dispatch phases are
ineligible. A direct Gemini request does not bypass the agy-first rule; content,
schema, timeout, capacity, or post-dispatch failures remain on the agy failure
path. A formal Gemini fallback is a separate gate: the distribution ships no
qualifying enforcement proof and runs no automatic probe. See the
[formal reviewer routing contract](skills/triad-cross-family-review/references/reviewer-routing.md)
for the owner-recorded proof required before formal admission.

### Opt out of the default rules

*Do this ONLY if you do not want the command rules installed.*

Export `TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=0` in the normal terminal, then run
the freshly printed absolute bootstrap command. The equivalent skip flag is
`TRIAD_BOOTSTRAP_SKIP_CODEX_RULES=1`. This also skips the managed
loader-environment guard only when the configured rules path is absent. If that
path already contains owner-maintained rules, bootstrap preserves them and
keeps the guard because those rules may still enable a managed launcher. The
repair-analyzer registration remains independent.

### Linux / WSL2 sandbox support

*Do this ONLY on Linux or WSL2.* Install `bubblewrap` (`bwrap`) for Codex sandbox
support. The installer does not install OS packages.

### Read the security model

*Do this ONLY if you want the full threat model before relying on the toolkit.*
See [SECURITY.md](SECURITY.md) — the durable control is privilege separation, not
model trust (summarized under [Security](#security) below).

### Notes on re-running bootstrap

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

### Upgrading from a pre-0.2.529 install

If an older install left a retained managed legacy profile or shell artifact,
plain `--install` warns with the exact path and performs no automatic deletion.
If an unselected legacy path is unsafe or unreadable, bootstrap reports the
refusal detail, does not follow or change that path, and continues installing
the selected ordinary artifacts. A selected profile, rules file, or shell entry
remains a fatal preflight error.

Use deliberate `--remove` followed by ordinary reinstall, or set
`TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1` when the legacy profile is intentional.
The legacy shell entry requires both
`TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1` and
`TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1`; the shell flag alone is rejected.
This compatibility path is an explicit legacy opt-in. Ordinary `codex` remains
the normal start path; the retired no-prompt `allow` posture is not restored. A
pre-0.2.529 initially absent config with stale
`original config existed = true` provenance is left as a safe zero-byte file
because it cannot be distinguished from a genuinely pre-existing empty file.

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
codex
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

### Shared-directory cross-family review

When the owner explicitly invokes `triad-cross-family-review`, that one request
authorizes the named Claude, Google-family, and fresh Codex review legs over the
stated source scope. The leader records that authorization once and does not ask
again for every leg. Provider-visible inputs must still exclude credentials,
tokens, cookies, authentication files, environment dumps, provider logs, and
unrelated paths.

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
specification change and resolve or approve it. Reviewers do not run candidate
code, tests, builds, hooks, or generated scripts.
Commit, push, install/update, merge, release, and publication still require
their own owner authorization.

Normal code-write dispatch should run from the target workspace. Path
containment is OPT-IN: the wrappers reject a `--cwd` / `--prompt-file` outside a
trusted root ONLY when `TRIAD_WRAPPER_ALLOWED_ROOTS` is set by the operator. By
default they do not constrain paths; approved-path containment is
prompt-controlled unless a provider actually enforces it. The boundary otherwise
rests on the selected `--cwd` worktree, requested wrapper sandbox, ordinary Codex
sandbox, and exact rules.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| A wrapper call pauses for manual approval instead of automatic review | The active reviewer is `user`, a higher-precedence layer overrides it, or the generated rules are missing/stale | Check `/status` and `/debug-config`, restore `approvals_reviewer = "auto_review"` in the applicable layer if desired, rerun bootstrap for stale rules, then restart ordinary `codex`. |
| A wrapper rule is auto-rejected before Agent Review | The active granular policy has `rules = false` or `sandbox_approval = false`, or approvals are `never` | Preserve the other granular choices, enable those two interactive categories, and restart; or use `approval_policy = "on-request"`. |
| Automatic review denies a wrapper call | Authorization is missing/out of scope, provider-visible input includes excluded credential material, or the reviewer found another unsafe condition | Narrow the input or obtain the missing owner authorization. The owner may use `/approve` for one exact recorded denial; never install a broad allow rule. |
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
| `65` | Auth / config / quota, or a lossy AGY answer (for example `oauth-env`, `cli-subscription-cap`, or `truncated-answer`) | For `truncated-answer`, do not repair it or switch to Gemini; request a new bounded, compact result. For other classes, re-login or wait for the quota reset — see the classification word. |
| `66` | Structured-output (`--pydantic`) schema validation failed | `schema-fail` is terminal for that invocation; the leader may make an explicit new invocation after deciding what to do. The shared-directory formal path does not require the legacy packet-bound schema. |
| `67` | Codex rejected the submitted output schema (`schema-rejected`) | Inspect the schema/configuration mismatch and make an explicit new invocation. |
| `1` | The wrapper could not extract an answer (`extraction-error`) or classification was `unknown` | Inspect the final wrapper classification and provider diagnostics, then retry or escalate as appropriate. |

## Scope & Limits — What This Does NOT Do

Honest boundaries, so you know where the toolkit stops:

- **It does NOT manage vendor auth or tokens.** No token issue/refresh, no API-key
  injection, and no install-time provider probes. You log in with each vendor
  CLI's native login; an auth-shaped runtime error is surfaced for you to
  re-login. There is no credential copying, sandbox-login attempt, company setup
  flow, or authorization store.
- **It does NOT install OS or Python packages.** You install the vendor CLIs,
  `python3`, the shipped Python requirements, and (on Linux/WSL2) `bubblewrap`
  yourself; the installer writes exact rules, launchers, and a provenance-marked
  loader-environment guard while preserving the other owner config keys. If the
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
  they are not a claim of OS-level isolation. The boundary rests on process
  permissions, the selected `--cwd` worktree, the Codex rules, and your
  review before commit.

## Update

```bash
codex plugin marketplace upgrade triad-codex-dispatch
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","add","triad-codex-dispatch@triad-codex-dispatch","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); root=pathlib.Path(data["installedPath"]); assert root.is_absolute(); print(shlex.join([str(root / "scripts" / "bootstrap.sh"),"--install"]))'
```

Run the newly printed absolute command. A plain `--install` reapplies the exact
rules, launchers, and managed loader-environment guard without creating a
dedicated profile. Set any legacy opt-in flags again before running it. Start a
new ordinary Codex session after updating.

## Verify The Install

### Plugin-only smoke test (no clone required)

This is the normal path — it confirms the toolkit is live without cloning
anything. Start the leader from your target workspace and ask codex to run a
trivial Google-family dispatch:

```bash
codex
```

Then, in that session:

> Use triad-antigravity-dispatch to ask agy: what does `git rebase --onto` do? One paragraph.

Expect agy's answer plus a one-line success summary on stderr:

```
[wrapper] antigravity ok exit=0 vendor=0 elapsed=6.4s
```

That `[wrapper] antigravity ok …` line is your signal the dispatch worked — the plugin,
launchers, and rules are all wired. `ok` is the classification; other values
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

`--remove` deletes the wrapper launchers, the installed
`triad-repair-analyzer`, `triad-apply-repair`, the exact command rules, and any provenance-matched
legacy profile or shell entry created by an older release. It also deletes
legacy three-agent TOMLs left by an older install. It strips the managed
repair-analyzer registration and exact managed `[shell_environment_policy]`
block from `$CODEX_HOME/config.toml`; if those are the file's only managed
content and no owner bytes remain, it removes `config.toml` only when it did not
exist before installation. This absent-file restoration applies only when both
provenance-marked managed registration and environment-policy blocks remain
intact; a pre-existing file and its owner bytes are preserved.
Learned classifier patches are intentionally preserved; they are
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
`audit.jsonl` keeps redacted argv, prompt length, status, and structured-output
presence/length. For audit retention, generated-launcher/redacted mode stores
redacted stdout/stderr plus their original lengths. The 500-character cap
applies to model-output fields, not those stream fields. An unredacted
non-launcher path may retain full stdout/stderr streams. Failure run logs keep
full prompts and vendor transcripts as untrusted repair evidence and remain
until their age-floor cleanup. Treat these files as sensitive and remove
`bin/_logs/` when needed.

Worktree-first review does not use the packet-bound `FormalReview` schema,
sealed-packet flags, or a source snapshot. Legacy wrapper support for those
options may remain for explicit compatibility, but it is not part of the normal
or formal worktree review and is not a gate prerequisite.

Every normal non-`--repair-mode` wrapper invocation that reaches its dispatch
driver performs best-effort cleanup of managed UUID/file-IPC entries older than
3,600 seconds before provider execution; Antigravity performs it before
`--preflight-only` as well. Cleanup errors never block dispatch, and this is not
a perfect garbage collector.

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
- Generated command rules match only the absolute launcher files installed
  under `~/.local/bin` or `TRIAD_BOOTSTRAP_BIN_DIR`; those launchers validate
  their argv and call the installed plugin cache. They always use `prompt`;
  `approval_policy=never` fails closed because Agent Review is inactive.
- Automatic review never supplies owner workflow authorization for commit,
  push, install, release, or publication.
- The exact installed `triad-repair-analyzer` uses its pinned read-only sandbox;
  it returns a proposal or escalation and never applies a classifier change.
