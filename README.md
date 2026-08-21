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
- Formal Google review uses native AGY CLI sign-in: personal Google Sign-In or
  Gemini Enterprise Business Sign-In for company use. Like the deployed
  Claude-led TRIAD, `--sandbox read-only` brackets AGY in a transient
  global-settings transaction that unions five deny rules and restores the
  original bytes. AGY 1.1.3+ also needs the wrapper-owned
  `--dangerously-skip-permissions` headless adaptation unless the operator sets
  `AGY_NO_HEADLESS_AUTOAPPROVE=1`. The auto-approve removes interactive approval
  prompts, while the transaction's explicit deny rules still block their named
  action namespaces. MCP calls are denied in the formal Google transaction;
  conditionally authorized external evidence uses AGY's native official-web read
  path. This is not OS-level confinement; round-integrity mutation detection
  remains a separate fail-closed check.
- Classifier gaps use a fresh native proposal-only child. The owner applies an
  accepted proposal locally from the same authenticated login terminal with the
  bootstrap-printed `python3 bin/apply_patch.py ... --classifier-file ...`
  command. No repair Custom Agent or apply launcher is installed.

## Required (~2 minutes)

Three steps get you a working install in ordinary Codex. Everything past this
section is optional.

1. **Native vendor logins.** Use the same authenticated login terminal and
   project worktree used for development. Install and log in to the leader `codex` and the
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

   The script installs the three provider wrapper launchers as one staged,
   all-or-nothing command group. It does not install a Codex permission profile,
   command rule, repair-agent registration, or pre-spawn
   `[shell_environment_policy]`. It preserves owner-authored `config.toml`,
   rules, permission settings, credentials, and unrelated files. Personal or
   Gemini Enterprise authentication is owner-provisioned; bootstrap installs no
   persistent global AGY permission policy.

   Bootstrap pins the install-resolved classifier path in every provider
   launcher and prints the direct owner apply argv, rendered with Python
   `shlex.join`, for login-shell `python3 bin/apply_patch.py` with the same
   required explicit `--classifier-file`. There is no installed apply launcher,
   and the owner apply path never recomputes an ambient classifier default.

   Native permission handling is an execution-time boundary, not owner workflow
   authorization. Commit, push, plugin or dependency installation, release, and
   publication remain separate owner decisions; the leader must not initiate
   them merely because `approvals_reviewer = "auto_review"` is active.

   > **Placement invariant (hard).** Run bootstrap from your project workspace,
   > not from a directory that contains the install targets. Bootstrap writes the
   > classifier patches under `~/.config/triad-codex-dispatch/`, and launchers under
   > `~/.local/bin` (or `TRIAD_BOOTSTRAP_BIN_DIR`). Those targets — and everything
   > they exec (the plugin cache, the `python3` runtime) — must live outside all
   > sandbox-writable roots; bootstrap hard-fails if any resolves inside the
   > directory it runs from (for example `$HOME`).

   Start ordinary `codex` from the same authenticated login terminal and actual
   project worktree. Authenticate AGY through personal Google Sign-In or its
   Gemini Enterprise Business Sign-In. Formal review invokes AGY with
   `--sandbox read-only` under the transient settings lease used by the
   Claude-led deployment. Trusted Python and `PATH` are
   prerequisites; wrapper child-process scrubbing remains after the trusted
   launcher and interpreter start.

   Then start a fresh ordinary Codex session from the target workspace:

   ```bash
   codex
   ```

   Use `/status` to verify the active approval policy and `/debug-config` when a
   project, profile, or managed layer changes the expected reviewer.

That is the whole required path. Repair is a proposal-only native-child step
surfaced only when needed (see [Custom Subagents](#custom-subagents) and
[Security](#security)).

## Optional / Advanced

Nothing in this section is needed for a normal individual install. Reach for a
subsection only when its "do this ONLY if…" line applies to you.

### Gemini Enterprise Business Sign-In

*Do this only in a company environment with a GE Standard or GE Plus seat.* Use
AGY 1.1.17 or newer and select its Business Sign-In with the organization-owned
Google Cloud project. The same formal AGY wrapper, settings transaction, and
`--sandbox read-only` plus native `--mode plan` lifecycle apply. The wrapper
parses the terminal response JSON and applies the strict local verdict and
review-binding checks, accepting AGY's optional single Markdown fence around
the sole JSON object. TRIAD never changes the active account or falls back to
a personal sign-in. The separate `triad-gemini-dispatch` skill remains a
standalone compatibility consult; it is not the Gemini Enterprise formal leg.
See the official [AGY changelog](https://antigravity.google/changelog?plan=free).

### Linux / WSL2 sandbox support

*Do this ONLY on Linux or WSL2.* Install `bubblewrap` (`bwrap`) for Codex sandbox
support. The installer does not install OS packages.

### Read the security model

*Do this ONLY if you want the full threat model before relying on the toolkit.*
See [SECURITY.md](SECURITY.md) — the durable boundaries are explicit data
authorization, pinned executables, digest/mutation checks, strict result custody,
and deterministic owner apply. Provider/user/project settings retain all
permission choices outside the documented packaged AGY child selection, and
no-edit/no-execution containment is prompt-controlled unless a provider actually
enforces it (summarized under [Security](#security) below).

### Notes on re-running bootstrap

- The generated wrapper launchers call files from the installed plugin cache;
  rerun bootstrap after every plugin update so those paths stay current.
- The launchers pin resolved vendor CLI paths; rerun bootstrap after upgrading or
  moving `claude`, `agy`, or optional `gemini`.
- Existing Codex sessions may not see newly installed plugin skills; start a new
  session after install or update.
- `codex plugin add --json` reports marketplace `authPolicy`; this plugin still
  does not perform CLI OAuth/login.

### Upgrading to 0.2.543

0.2.543 stops treating post-completion AGY `step_update` telemetry as a
verdict-admission schema. Added metadata fields, changed optional tool
arguments, denied attempts, and conflicting duplicate progress events cannot
retroactively invalidate an otherwise valid terminal review. Static-review
containment remains enforced by the prompt, native `--mode plan`, and the
explicit deny transaction; strict local `LegVerdict` and review-binding checks
plus round-integrity verification remain the admission gates.

The formal Google-family prompt remains explicitly static-only: it permits
native file read/search and conditionally authorized AGY native official-web
reads, denies MCP calls, forbids command, write, experiment, notebook, subagent,
browser-actuation, and scratch tools, and sends unresolved static uncertainty to
`open_questions`. Inside the prepared directory it uses native `list_dir`,
`find_by_name`, and `view_file` as needed, and uses native `grep_search` with the
required `SearchPath` and `Query` arguments. Every view supplies the required `AbsolutePath` argument; large files use explicit
positive-integer `StartLine` and `EndLine` ranges.
`ContentOffset`, `IsSkillFile`, and implicit `another page` continuation remain
forbidden.
It corrects 0.2.540's plan-mode structured-output regression by omitting native
`--json-schema` on the formal plan-mode route, requiring the terminal
`response` to contain one JSON object, accepting AGY's optional single Markdown
fence around that object, and applying strict local `LegVerdict` plus exact
review-binding validation. It requires AGY 1.1.17 or newer, personal or
Gemini Enterprise Business Sign-In, transient global-settings transaction, `--sandbox read-only`,
operator opt-out, billed API/ADC/Vertex route-selector removal, local result
binding, and immediate whole-round fail-fast cancellation.

Ordinary `--install` and `--remove` clean up only exact plugin-owned legacy
profiles, launcher rules, repair-agent registration, pre-spawn
`[shell_environment_policy]`, and retired apply/repair launchers whose markers
and expected bytes match. Foreign, edited, linked, or non-regular targets are
preserved and reported. This cleanup preserves owner-authored settings, rules,
permission profiles, and credentials; unrelated files remain untouched.

The review runtime now uses one complete focused directory, one `LegVerdict`
from each required family, and fresh complete rounds after bounded fixes. Batch,
packet, receipt, PTY, and sentinel review transports are removed. AGY requires
1.1.17 or newer and uses native `stream-json`; the formal plan-mode route
deliberately omits native `--json-schema` and validates the terminal JSON
locally. It passes `gemini-3.1-pro-high` with `high` effort. The documented packaged
AGY child selection is the sole permission-mode exception; other provider
permission and all project-trust policy remain native. Ordinary `codex` remains
the normal path.

Maintainers can verify exact clean-HEAD archive bytes before installation:

```bash
/bin/zsh -lic 'python3 scripts/verify_distribution.py --source-root . --output-dir _runs/distribution/0.2.543-final-r1'
```

Use a new output label for every attempt; the verifier refuses an existing
directory. It rejects a dirty source tree, archives `HEAD`, safely extracts the
archive, compares the manifest and core review-skill hashes, runs the full test
suite from the extracted bytes, and writes `verification.json`. Authenticated
fresh-process skill exposure remains a separate release procedure.

## Use

Ask Codex to use these installed skills:

- `triad-claude-dispatch`: single-shot Claude Code consult.
- `triad-antigravity-dispatch`: primary Google-family consult through `agy`.
- `triad-gemini-dispatch`: standalone compatibility consult through the
  separately installed `gemini` CLI; not the Gemini Enterprise formal leg.
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
documentation. For this release, the exact no-exclusion boundary includes all
repository test source. Normal SDD implementation review includes relevant test
source. Other advisory review follows its separately owner-approved data scope.

Every leg receives the same directory and task. No prompt inlines a diff or file
body. Record one simple content digest before dispatch and compare it after every
required leg terminates; a mismatch invalidates the round. Before a formal gate,
classify every test failure as production defect, test-case defect, or intentional
specification change and resolve or approve it. Reviewers do not run candidate
code, tests, builds, hooks, or generated scripts.

The full diff is navigation evidence, not the review boundary. The leader
prepares one focused directory containing the complete current files,
configuration, and governing documentation relevant to the decision. Every
required family reviews that same complete directory once and returns one
strict `LegVerdict` bound to its family, review ID, and directory digest.
The leader captures the directory digest and canonical-worktree fingerprint
before dispatch, verifies both after all legs terminate, and reproduces every
finding against the canonical worktree. Reviewer coverage is prompt-controlled
unless the provider exposes a stronger boundary; it is never promoted from a
manifest path or provider confidence statement alone.

Commit, push, install/update, merge, release, and publication still require
their own owner authorization.

Normal code-write dispatch should run from the target workspace. Path
containment is OPT-IN: the wrappers reject a `--cwd` / `--prompt-file` outside a
trusted root ONLY when `TRIAD_WRAPPER_ALLOWED_ROOTS` is set by the operator. By
default they do not constrain paths; approved-path containment is
prompt-controlled unless a provider actually enforces it. The boundary otherwise
rests on the selected `--cwd` worktree, native provider permissions,
immutable-directory digests, and leader mutation checks.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Gemini rejects the project worktree as untrusted | Gemini owns workspace trust after removal of `--skip-trust` | Make the provider-native trust decision for that worktree, or stop. TRIAD has no trust bypass or speculative detector. |
| A dispatch fails with `oauth-env` | The worker CLI's login expired or is missing | Re-run that vendor's native login (`claude` / `agy` OAuth, or `codex login`). The toolkit never re-authenticates for you — it surfaces the signal so you log in. |
| The gemini leg fails with `IneligibleTier` | The Gemini CLI *individual* tier is deprecated | Use the `agy` (Antigravity) leg — it is the Google-family leg for individual users. `gemini` is only for business / Vertex / API-key accounts. |
| A new skill isn't available after install/update | Existing Codex sessions don't see newly installed skills | Start a new Codex session (and rerun `bootstrap.sh --install` after a plugin update so launcher paths stay current). |
| A dispatch returns non-zero and you want to know what happened | The numeric exit code is always authoritative; a completed wrapper failure normally also emits a final classification | See the exit-code legend below. When a final `[wrapper] …` stderr line exists, use its classification; preserve an early no-summary failure as-is. |

**Exit-code legend** (the wrapper's process exit code; when a final wrapper
summary exists, its class appears on the `[wrapper] <cli> <class> …` stderr line):

| Exit | Meaning | What to do |
|---|---|---|
| `0` | Success — the answer follows | Nothing. |
| `4` | The configured provider binary was missing or not executable before submission | Fix that binary. Formal Google review requires AGY for both personal and Gemini Enterprise authentication; never switch accounts as recovery. |
| `64` | Server capacity exhausted after retries | Transient vendor overload; wait and retry. |
| `65` | Authentication, configuration, quota, or another terminal provider failure (for example `oauth-env`, `cli-subscription-cap`, or `token-limit`) | Resolve the cited provider state, then make an explicit new invocation. |
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
  yourself; the installer writes the three provider wrapper launchers while
  preserving owner-authored configuration. If the
  selected Python is missing Pydantic 2, bootstrap stops before mutation and
  prints the exact `python3 -m pip install -r .../requirements.txt` command for
  that interpreter.
- **The self-improving classifier is a heuristic, not an oracle.** It can route a
  genuine failure to a wrong-but-plausible class. The worst case is an *integrity*
  issue — a persistent routing mis-classification, NOT code execution (see
  [Security](#security)) — but you should periodically review the applied deltas in
  `~/.config/triad-codex-dispatch/classifier-patches.json`. Bootstrap pins the
  resolved absolute path into every provider launcher and the printed owner
  apply argv; rerun bootstrap
  after changing `TRIAD_CLASSIFIER_EXTENSION`.
- **Wrapper containment is process-level, not OS-level confinement.**
  The wrapper-containment envs gate path/pydantic handling in the wrapper process;
  they are not a claim of OS-level isolation. Formal AGY uses `--sandbox`, the
  transient deny lease, the disposable `--cwd` review directory, digest and
  mutation checks, and your review before commit. On AGY 1.1.3+ the headless
  auto-approve removes interactive approval prompts, while the transaction's
  explicit deny rules still block their named action namespaces. The sandbox
  remains provider-managed rather than OS-level confinement; round-integrity
  mutation detection is a separate fail-closed check.
  Formal review places wrapper `--cwd` and `--prompt-file` paths under the reserved
  `triad-review-` system-temp root. When `TRIAD_WRAPPER_ALLOWED_ROOTS` is configured,
  it must include the canonical system temp base, including in hardened mode.

## Update

```bash
codex plugin marketplace upgrade triad-codex-dispatch
python3 -c 'import json,pathlib,shlex,subprocess; result=subprocess.run(["codex","plugin","add","triad-codex-dispatch@triad-codex-dispatch","--json"],check=True,capture_output=True,text=True); data=json.loads(result.stdout); root=pathlib.Path(data["installedPath"]); assert root.is_absolute(); print(shlex.join([str(root / "scripts" / "bootstrap.sh"),"--install"]))'
```

Run the newly printed absolute command. A plain `--install` republishes the
three provider wrapper launchers and performs exact plugin-owned legacy cleanup
without creating permission state. Start a new ordinary Codex session after
updating.

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

That `[wrapper] antigravity ok …` line is your signal the dispatch worked — the plugin
and launchers are wired to the native provider environment. `ok` is the classification; other values
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

`--remove` deletes the three provider wrapper launchers and exact plugin-owned
legacy launchers, profiles, command rules, repair-agent registration, and
`[shell_environment_policy]` fragments only when their markers and expected
bytes match. It also removes exact legacy three-agent TOMLs. Foreign, edited,
linked, and non-regular targets are preserved and reported. Owner-authored
`config.toml` settings, rules, permission profiles, credentials, and unrelated
files are preserved; an owner file is never removed merely because no managed
bytes remain.
Learned classifier patches are intentionally preserved; they are
outside managed uninstall and should be deleted separately only when the owner
intends to discard learned routing.

## Custom Subagents

Classifier repair uses a fresh native proposal-only child with prompt-controlled
no-edit behavior. It returns a proposal or escalation and cannot apply a patch.
The leader stores only the proposal in a unique UTF-8 JSON file. Bootstrap
renders the direct owner command from an argv list with Python `shlex.join`:

`python3 bin/apply_patch.py --cli <cli> --proposal-file <absolute-path> --classifier-file <pinned-absolute-path>`.

Run the printed absolute command in the same authenticated login terminal. The
run log remains until age-floor cleanup.

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

Cross-family review uses the focused prepared-directory digest, the canonical
worktree fingerprint, and one strict `LegVerdict` per family. The leader keeps
results and snapshots outside reviewed evidence and starts a fresh complete
round after any bounded correction.

Formal review reserves the `triad-review-` namespace under the canonical system
temp root. Each round owns its returned root, including `results/_logs`; a later
prepare removes only managed interrupted roots without activity for strictly
more than 30 days. Normal cleanup removes the exact completed root and leaves
other managed sibling roots untouched.

Every normal non-`--repair-mode` wrapper invocation that reaches its dispatch
driver performs best-effort cleanup of managed UUID/file-IPC entries older than
3,600 seconds before provider execution; Antigravity performs it before
`--preflight-only` as well. Cleanup errors never block dispatch, and this is not
a perfect garbage collector.

## Security

The durable controls are explicit data authorization, pinned executables,
digest/mutation checks, strict result custody, and a native proposal-only repair
child followed by deterministic owner apply. Provider/user/project settings
retain permission selection outside the documented packaged AGY child exception.
Full threat model: [SECURITY.md](SECURITY.md).

## Support

- Bugs and questions: https://github.com/codefoundry-io/triad-codex-dispatch/issues
- Security-sensitive reports: same tracker, title prefixed `[security]`; do not
  include secrets or tokens in the report body.

## Notes

- Apart from the approved internal AGY flag and the disclosed transient AGY
  global-settings transaction, TRIAD accepts no caller-supplied yolo, bypass,
  skip-trust, accept-edits, or equivalent permission controls. The transaction
  changes AGY settings only for its lease and restores the original bytes; a
  hard crash can leave deny residue for the next guarded call to heal.
- Native permission decisions never supply owner workflow authorization for commit,
  push, install, release, or publication.
- The fresh repair child returns a proposal or escalation and never applies a
  classifier change.
