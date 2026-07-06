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
- Wrapper launchers for Claude, agy, and Gemini.
- No in-session repair agents. When a dispatch hits a classifier gap, the SKILL
  surfaces a ready-to-paste top-level `codex exec -s read-only` analyzer command
  you run in a fresh terminal; it proposes ONE classifier entry, which the
  deterministic `bin/apply_patch.py` validates and applies. There is no
  write-capable in-session repair worker.
- A generated Codex profile on the Codex permission-profile system
  (`default_permissions = "triad_leader"`, extending `:workspace`; no legacy
  `sandbox_mode` keys) plus command rules for the wrapper launchers.
- An optional managed `codex-triad` shell entry
  (`TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1`) — the required start for the
  no-prompt posture.

## Requirements

Install and log in before running bootstrap:

- `codex`
- `claude` — Claude Code `>= 2.1.170`; bootstrap warns on older versions.
- `agy`

Optional:

- `gemini`, only for business, Vertex, or API-key Gemini accounts. Individual
  Google-family users should use `agy`.

Host tools:

- `git`, `jq`, and `python3 >= 3.12`
- Linux/WSL2: install `bubblewrap` (`bwrap`) for Codex sandbox support.
- Make sure `~/.local/bin` is on `PATH`, or set `TRIAD_BOOTSTRAP_BIN_DIR` to a
  directory already on `PATH`.

The installer does not perform OAuth login and does not install OS packages.

## Setup checklist (do these in order)

The split is **manual login (human) → config (script) → manual repair (human)**;
the wrapper NEVER manages tokens (a deliberate safety boundary — see
[SECURITY.md](SECURITY.md)).

1. **Manual login (human)** — native login to the leader `codex` and the workers
   `agy`, `claude` (and `gemini` only for business/Vertex/API-key accounts). The
   toolkit issues/refreshes no credentials; `--install` runs live auth probes.
2. **Config (script)** — `scripts/bootstrap.sh --install` with your env gates
   (see Install) writes the profile, command rules, and launchers, and pins
   `features.multi_agent = false`; the no-prompt posture adds the managed
   `codex-triad` shell entry.
3. **Repair (manual, human)** — on a novel `unknown` error the SKILL surfaces a
   top-level `codex exec -s read-only` analyzer you paste into a fresh terminal
   (read-only; cannot write), whose proposal you pipe to `bin/apply_patch.py`
   (the single deterministic writer). Manual BY DESIGN — the run-log reader has
   no write authority.

## Install

Install directly from the public GitHub repository. No local clone is required
for normal users.

Repository: https://github.com/codefoundry-io/triad-codex-dispatch

**Placement invariant (hard).** Bootstrap writes the generated profile and
command rules under `$CODEX_HOME` (default `~/.codex/`);
classifier patches under `~/.config/triad-codex-dispatch/`; and wrapper
launchers under `~/.local/bin` (or `TRIAD_BOOTSTRAP_BIN_DIR`). These install
targets — and everything they execute: the installed plugin cache and the
`python3` runtime — must live outside all sandbox-writable roots. Bootstrap
hard-fails when any of them resolves inside the directory it is run from,
including when you run bootstrap from a directory that contains the targets
(for example `$HOME`). Run bootstrap from your project workspace and keep
`CODEX_HOME` / `XDG_CONFIG_HOME` / `TRIAD_BOOTSTRAP_BIN_DIR` overrides outside
every Codex workspace.

```bash
codex plugin marketplace add codefoundry-io/triad-codex-dispatch --ref main

TRIAD_PLUGIN_DIR="$(
  codex plugin add triad-codex-dispatch@triad-codex-dispatch --json |
    jq -r '.installedPath'
)"

# Conservative install — the default posture: approval_policy stays
# on-request, so Codex asks before each external-CLI wrapper call.
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --install
```

`--check` is a deprecated alias for `--install`, kept for one release.

`--install` runs LIVE vendor auth probes: `codex login status`, plus one
minimal "Return exactly OK." call each to `claude` and `agy` (and `gemini`
when installed). Set `TRIAD_BOOTSTRAP_SKIP_AUTH=1` to skip them (CI or
scheduled jobs only).

Then start a new Codex session from the target workspace:

```bash
codex --profile triad-codex-dispatch --search
```

Important install behavior:

- The generated wrapper launchers call files from the installed plugin cache.
  Rerun bootstrap after every plugin update so those paths stay current.
- The launchers pin resolved vendor CLI paths. Rerun bootstrap after upgrading
  or moving `claude`, `agy`, or optional `gemini`.
- Existing Codex sessions may not see newly installed plugin skills or custom
  agents. Start a new session after install or update.
- agy calls may transact against Antigravity CLI runtime settings under
  `~/.gemini/antigravity-cli/`; that is provider runtime state, not a bootstrap
  install target.
- `codex plugin add --json` reports marketplace `authPolicy`; this plugin still
  does not perform CLI OAuth/login.

## No-Prompt Opt-In (Heavy Users)

No-prompt install: add `TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never` plus the
managed shell entry to the conservative install above.

> **Warning — session-wide scope.**
> `approval_policy=never` applies to the whole triad Codex session, not only
> this plugin. Do not run unrelated work in that session.

```bash
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1 \
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never \
"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --install
```

The ONLY supported start for the no-prompt posture is the managed `codex-triad`
function that `TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1` appends to your shell RC
(default `~/.bashrc`; `~/.zshrc` for zsh; `TRIAD_BOOTSTRAP_SHELL_RC`
overrides). It pins the wrapper-containment envs (these gate path/pydantic
handling in the wrapper process; they are not a claim of OS-level confinement —
see [SECURITY.md](SECURITY.md)):

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

## Use

Ask Codex to use these installed skills:

- `triad-claude-dispatch`: single-shot Claude Code consult.
- `triad-antigravity-dispatch`: primary Google-family consult through `agy`.
- `triad-gemini-dispatch`: Gemini business/Vertex/API-key accounts only.
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
| Codex asks for approval before each wrapper call | The default posture keeps `approval_policy=on-request` | Expected. For a no-prompt session, use the [No-Prompt Opt-In](#no-prompt-opt-in-heavy-users) and start with the managed `codex-triad` function. |
| A dispatch fails with `oauth-env` | The worker CLI's login expired or is missing | Re-run that vendor's native login (`claude` / `agy` OAuth, or `codex login`). The toolkit never re-authenticates for you — it surfaces the signal so you log in. |
| The gemini leg fails with `IneligibleTier` | The Gemini CLI *individual* tier is deprecated | Use the `agy` (Antigravity) leg — it is the Google-family leg for individual users. `gemini` is only for business / Vertex / API-key accounts. |
| A new skill isn't available after install/update | Existing Codex sessions don't see newly installed skills | Start a new Codex session (and rerun `bootstrap.sh --install` after a plugin update so launcher paths stay current). |
| A dispatch returns non-zero and you want to know what happened | Each failure has a classification + exit code | See the exit-code legend below and the classification word on the `[wrapper] …` stderr line. |

**Exit-code legend** (the wrapper's process exit code; the same failure classes
appear as the word on the `[wrapper] <cli> <class> …` stderr line):

| Exit | Meaning | What to do |
|---|---|---|
| `0` | Success — the answer follows | Nothing. |
| `64` | Server capacity exhausted after retries | Transient vendor overload; wait and retry. |
| `65` | Auth / config / quota (e.g. `oauth-env`, `cli-subscription-cap`) | Re-login or wait for the quota reset — see the classification word. |
| `66` | Structured-output (`--pydantic`) schema validation failed | The model's JSON did not match the schema after one repair retry. |
| `69` | A code task was blocked / needs more context (codex `--task code`) | Provide the missing context and re-dispatch. |

## Scope & Limits — What This Does NOT Do

Honest boundaries, so you know where the toolkit stops:

- **It does NOT manage vendor auth or tokens.** No token issue/refresh, no API-key
  injection. You log in with each vendor CLI's native login; an auth-shaped error
  is surfaced for you to re-login. `bootstrap.sh --install` runs live auth probes
  but performs no login itself.
- **It does NOT install OS packages.** You install the vendor CLIs, `python3`, and
  (on Linux/WSL2) `bubblewrap` yourself; the installer only writes the profile,
  rules, and launchers.
- **The self-improving classifier is a heuristic, not an oracle.** It can route a
  genuine failure to a wrong-but-plausible class. The worst case is an *integrity*
  issue — a persistent routing mis-classification, NOT code execution (see
  [Security](#security)) — but you should periodically review the applied deltas in
  `~/.config/triad-codex-dispatch/classifier-patches.json`.
- **Wrapper containment is process/permission-level, not OS-level confinement.**
  The wrapper-containment envs gate path/pydantic handling in the wrapper process;
  they are not a claim of OS-level isolation. The boundary rests on the isolated
  `--cwd` worktree + the Codex profile/rules + your review before commit.

## Update

```bash
codex plugin marketplace upgrade triad-codex-dispatch

TRIAD_PLUGIN_DIR="$(
  codex plugin add triad-codex-dispatch@triad-codex-dispatch --json |
    jq -r '.installedPath'
)"

# Re-use the same env flags you installed with (incl. the no-prompt opt-in).
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 \
TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 \
"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --install
```

Start a new Codex session after updating.

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
[wrapper] agy ok exit=0 vendor=0 elapsed=6.4s
```

That `[wrapper] agy ok …` line is your signal the dispatch worked — the plugin,
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

Run the managed uninstall BEFORE removing the plugin cache (the script lives
inside it):

```bash
"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --remove

codex plugin remove triad-codex-dispatch@triad-codex-dispatch
codex plugin marketplace remove triad-codex-dispatch
```

`--remove` (alias `--uninstall`) deletes the wrapper launchers, the managed
profile and command rules, and the managed `codex-triad` shell entry. It also
deletes any legacy personal-scope repair-agent TOMLs left by an older install
(current installs write none). Learned classifier patches are preserved;
delete them only to discard learned routing: `rm -rf
~/.config/triad-codex-dispatch`.

Default user-home removal, manual equivalent (the repair-agent lines only apply
if you are cleaning up an older install):

```bash
rm -f ~/.codex/agents/claude-wrapper-repair.toml
rm -f ~/.codex/agents/gemini-wrapper-repair.toml
rm -f ~/.codex/agents/agy-wrapper-repair.toml
rm -f ~/.codex/triad-codex-dispatch.config.toml
rm -f ~/.codex/rules/triad-codex-dispatch.rules

rm -f ~/.local/bin/claude_wrapper.py
rm -f ~/.local/bin/gemini_wrapper.py
rm -f ~/.local/bin/antigravity_wrapper.py
rm -rf ~/.config/triad-codex-dispatch
```

If you installed with a custom `CODEX_HOME`, remove the agent/profile/rules
files from that directory instead of `~/.codex`.
If you used a custom `TRIAD_BOOTSTRAP_BIN_DIR`, remove the three wrapper
launchers from that directory instead of `~/.local/bin`. For custom `XDG_CONFIG_HOME`,
remove `triad-codex-dispatch/` under that config directory instead of
`~/.config/triad-codex-dispatch`.

## Custom Subagents

This distribution ships no repair subagents. Classifier repair runs as a
top-level `codex exec -s read-only` analyzer the SKILL surfaces for you to paste
into a fresh terminal — it only reads (a nested codex under the session sandbox
cannot initialize, and top-level it is hard read-only), and the deterministic
`bin/apply_patch.py` is the only writer. The generated profile also pins
`[features] multi_agent = false` so no stray codex subagent can be spawned.

If you create your own Codex custom subagent that should call triad dispatch
skills, opt in explicitly with Codex `skills.config` entries pointing at the
needed `SKILL.md` files under the `TRIAD_PLUGIN_DIR` value from install/update.

After editing custom-agent TOML files, start a new Codex session.

## Runtime Logs And Local Data

Runtime telemetry is local under the installed plugin's `bin/_logs/<cli>/`.
`audit.jsonl` keeps redacted argv, prompt length, status, 500-character
stdout/stderr heads, and structured-output presence/length only. Failure run
logs keep full prompts and vendor transcripts for repair replay, then skills
delete them after repair; a failsafe caps stale run logs. Treat these files as
sensitive and remove `bin/_logs/` when needed.

Antigravity settings under `~/.gemini/antigravity-cli/` are transacted during
agy calls. Avoid editing agy permissions during triad calls or running another
Antigravity settings change at the same time.

## Security

The durable control is **privilege separation**, not model trust: the component
that reads an untrusted run-log has zero write authority. This product ships no
in-session repair worker — repair is a top-level `codex exec -s read-only`
analyzer (cannot write) whose proposal is applied ONLY by the deterministic,
zero-LLM `bin/apply_patch.py`. "The model resists injection" is NOT the boundary.
Full threat model: [SECURITY.md](SECURITY.md).

## Support

- Bugs and questions: https://github.com/codefoundry-io/triad-codex-dispatch/issues
- Security-sensitive reports: same tracker, title prefixed `[security]`; do not
  include secrets or tokens in the report body.

## Notes

- This plugin avoids `danger-full-access`.
- Generated command rules allow only launcher files installed under
  `~/.local/bin` or `TRIAD_BOOTSTRAP_BIN_DIR`; those launchers call the installed
  plugin cache.
- Repair-agent permissions are declared TOML grants, not a proof that a broader
  parent session or managed runtime override cannot allow more.
- Detailed company/fleet setup lives under `migration/`.
