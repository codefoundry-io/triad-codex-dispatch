# Worktree-First Review and Auto-Review Distribution Design

## Problem

The current formal-review path turns every cross-family review into a sealed,
code-complete repository copy with manifests and packet hashes. That machinery
prevents the normal workflow the owner wants: reviewers enter the existing Git
worktree, inspect one trusted leader-captured diff, and follow affected callers, tests,
configuration, and documentation directly from the repository.

The distribution also currently installs exact wrapper rules with
`decision = "allow"`. Those rules avoid prompts, but bypass Codex Auto-review.
The intended boundary is instead: the owner authorizes a triad review once,
exact managed provider calls are reviewed automatically, and unrelated external
or destructive operations retain their existing boundaries.

## Goals

- Make the existing worktree the default and only source root for an ordinary
  or formal triad cross-family review.
- Have the leader capture the selected Git status/diff once with fixed,
  non-mutating Git argv and give identical output to every reviewer. Have each
  reviewer independently
  trace affected unchanged files.
- Create no source copy, packet, manifest, allowlist, or Python-generated
  related-file list for the default review path.
- Detect a worktree change during a review with a lightweight pre/post Git state
  fingerprint and rerun only when that fingerprint changed.
- Treat an explicit owner request to use the triad review skill as authorization
  for the named Claude and Google-family review calls over the stated source
  scope. Do not ask again for each leg.
- Route exact installed provider-wrapper commands through Codex Auto-review.
- Ship the required Codex profile and rules through the existing human-run
  bootstrap because a sandboxed Codex session cannot reliably write the user's
  `$CODEX_HOME`.
- Preserve separate owner authorization before commit, push, plugin install or
  update, release, merge, or publication.

## Non-goals

- Do not weaken the sandbox globally or grant broad shell prefixes.
- Do not customize model or reasoning defaults for normal development sessions.
- Do not include credentials, authentication stores, environment dumps, or
  provider logs as review inputs.
- Do not make a source archive a hidden prerequisite for a formal gate.
- Do not make a provider call imply permission to commit, push, install, merge,
  or release.

## Review source and scope

The leader resolves one absolute Git worktree root and one review scope:

- uncommitted changes, including staged, unstaged, and untracked paths;
- a base branch or revision range; or
- one commit.

The leader gives each reviewer the same worktree root, scope selector, objective,
suspect decisions, and trusted Git status/diff output. Provider read-only modes
keep their general shell denied. The diff is an entry point, not the review boundary. Each
reviewer must inspect affected unchanged callers, consumers, tests, build files,
configuration, and governing documentation when relevant.

Reviewers are no-edit. Claude and Google-family wrapper calls use the absolute
worktree as `--cwd` with `--sandbox read-only`. The fresh Codex reviewer receives
the same absolute worktree and scope in a no-edit prompt. Reviewers may use Git
inspection, file reads, and searches; they do not execute candidate code, tests,
builds, hooks, or generated scripts during the review.

## Lightweight consistency guard

Before dispatch, the leader records a review ID plus a digest of:

1. `git rev-parse HEAD`;
2. the selected diff as emitted by Git without an external diff driver;
3. the complete untracked-path inventory; and
4. Git object hashes for the untracked path contents.

This is a read-only Git fingerprint. It does not copy source bytes, generate a
review file list, or constrain what related files a reviewer may inspect.

After all legs return, the leader recomputes the same digest. A different digest
invalidates that round because the reviewers may have observed different source
states. An unchanged digest admits reconciliation. The leader must not edit the
worktree while independent legs are running.

Small review records may retain the review ID, scope, pre/post digest, exact
provider commands, and reviewer outputs. They must not contain a copied source
tree or authentication material.

## Reviewer result contract

Each reviewer returns:

- `SAFE` or `NOT-SAFE`;
- prioritized findings with worktree-relative path and line evidence;
- the triggering condition and correction direction for every material finding;
- affected unchanged surfaces inspected; and
- unresolved questions.

The packet-bound `FormalReview` schema and sealed-packet flags are not used by
the worktree-first path. Existing wrapper support for those flags may remain for
backward compatibility, but no skill or default gate directs users through it.

## Auto-review boundary

The generated triad Codex profile uses:

```toml
approval_policy = "on-request"
approvals_reviewer = "auto_review"
```

The settings apply to the dedicated triad profile installed by bootstrap, not
to the owner's normal Codex configuration.

Bootstrap-generated rules match only the absolute managed launchers for
`claude_wrapper.py`, `antigravity_wrapper.py`, and `gemini_wrapper.py`. Each rule
uses `decision = "prompt"`. With the profile above, the prompt is sent to the
Agent reviewer rather than the person. The justification states that an exact
managed wrapper call is an owner-authorized triad review and may send relevant
review source to the authenticated named provider while excluding credentials,
authentication files, environment dumps, and unrelated paths.

The rules do not match a repository wrapper path, a generic Python invocation,
`bash -lc`, `zsh -lc`, or another shell entry point. A reviewer denial remains a
security result; the leader may choose a materially safer call or stop. The
skill must not repeatedly ask the owner to approve each already-authorized leg.

## Distribution and migration

The plugin installation continues to print the absolute bootstrap command. The
owner runs that command once in a normal authenticated terminal. Bootstrap owns
the generated profile, exact launcher rules, and launchers under `$CODEX_HOME`
and the configured launcher directory.

Re-running bootstrap replaces its provenance-marked old `allow` rules with the
new `prompt` rules and refreshes the dedicated profile. It preserves foreign
files and refuses to overwrite unmanaged same-name artifacts. No post-install
hook silently edits `$CODEX_HOME`.

README instructions must describe this exact flow:

1. install the plugin;
2. run the printed bootstrap command in the owner's terminal;
3. start a new session with the installed triad profile; and
4. invoke the triad skill once without per-leg approval repetition.

## Acceptance criteria

- A fresh agent given the updated skill chooses the existing worktree and does
  not create a packet or snapshot.
- The skill explicitly requires review beyond changed files into affected
  unchanged files.
- Distribution tests prove the generated profile selects Auto-review and the
  exact wrapper rules evaluate to `prompt`.
- Tests prove broad shell, raw repository wrapper, and generic Python forms do
  not match the installed rules.
- Documentation states that bootstrap is human-run and that commit, push,
  install/update, merge, and release remain separately authorized operations.
- No install, commit, push, provider dispatch, or release occurs as part of this
  implementation without its separate approval.
