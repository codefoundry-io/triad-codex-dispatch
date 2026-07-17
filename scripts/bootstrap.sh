#!/usr/bin/env bash
# Workspace-escape invariant (HARD):
#   Allow-listed files and everything they exec must live OUTSIDE all
#   sandbox-writable roots.
# The generated exec-policy rules run the wrapper launchers outside the Codex
# sandbox WITHOUT prompting. That is only safe when the launchers, the pinned
# python3 runtime, the checkout bin/ wrappers they exec, and the Codex policy
# surface (CODEX_HOME rules/profiles/agents) plus the classifier patch dir are
# NOT writable from inside a sandboxed session. A workspace-writable launcher
# (or exec target) is a promptless sandbox-escape chain: the sandbox rewrites
# the allow-listed file, then asks Codex to run it outside the sandbox.
# check_workspace_escape enforces this against the workspace bootstrap is run
# from ($PWD, the sandbox-writable root) and hard-fails on violation.
set -u

usage() {
  cat <<'EOF'
Usage: scripts/bootstrap.sh --install
       scripts/bootstrap.sh --remove

--install checks local prerequisites for triad-codex-dispatch and installs
local launcher scripts. It installs NO in-session repair agents: codex-host
repair is a top-level read-only analyzer the owner runs in a fresh terminal
(see the dispatch SKILL Step 5). It also quarantines any legacy personal-scope
repair-agent TOMLs (bootstrap-authored provenance only — a same-name file
without that provenance is left in place) left by an older install into a
timestamped directory outside agents/, recoverable if needed. (--check is a
deprecated alias for --install, kept for one release.)

--remove uninstalls the managed artifacts: wrapper launchers, the optional
runtime profile and command rules, and the managed codex-triad shell entry. It
also removes any bootstrap-managed (provenance-matched) legacy personal-scope
repair-agent TOMLs left by an older install; a non-matching same-name file is
preserved. Learned classifier patches are preserved.

Assumes codex, claude, and agy are already installed and OAuth logged in.

Install targets must resolve OUTSIDE the workspace bootstrap runs from:
allow-listed launchers and everything they exec must live outside all
sandbox-writable roots (see the header of this script). Bootstrap hard-fails
otherwise.

By DEFAULT, --install installs/updates the runtime Codex profile at
$CODEX_HOME/triad-codex-dispatch.config.toml AND the user-layer command rules at
$CODEX_HOME/rules/triad-codex-dispatch.rules — so a plain --install with 0 env
vars yields the recommended setup. The profile uses the Codex permission-profile
system (default_permissions = "triad_leader"); it never emits legacy sandbox_mode
/ [sandbox_workspace_write], which would disable permission profiles and
neutralize the triad_leader profile's scoping. It defaults to
approval_policy=on-request (Codex prompts before each external-CLI wrapper call).
Set TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never only for explicitly approved
heavy-user no-prompt deployments — that is the ONLY setting that trades away the
safety prompt, and it stays opt-in.

Alongside the profile, --install merges codex's native loader-env allowlist
([shell_environment_policy] inherit="core") into $CODEX_HOME/config.toml under a
provenance marker (with a .bak backup), so codex drops loader/interpreter
injection vars (LD_PRELOAD/NODE_OPTIONS/PYTHONPATH/...) from every subprocess it
spawns, including the outside-sandbox wrapper launchers. It preserves every
other key (marker-delimited append, never a re-emit) and leaves a user's own
[shell_environment_policy] untouched (warns instead). --remove strips exactly
that marker block. See migration/config-fragment.recommended.toml.

To opt OUT of the default profile install, set
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=0 (or TRIAD_BOOTSTRAP_SKIP_CODEX_PROFILE=1).
To opt OUT of the default command rules, set TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=0
(or TRIAD_BOOTSTRAP_SKIP_CODEX_RULES=1). The generated rules allow only this
checkout's authenticated absolute wrapper launchers.

Set TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1 to append the managed codex-triad
shell function to your shell RC (idempotent; TRIAD_BOOTSTRAP_SHELL_RC overrides
the RC file path). codex-triad pins TRIAD_WRAPPER_ALLOWED_ROOTS,
TRIAD_WRAPPER_HARDENED=1, and TRIAD_CLAUDE_ENFORCE_SANDBOX=1 — it is the only
supported no-prompt start; do not start no-prompt dispatch with a bare codex
invocation.
EOF
}

MODE=""
CHECK_ALIAS_USED=0
case "${1:-}" in
  --install)
    MODE="install"
    ;;
  --check)
    MODE="install"
    CHECK_ALIAS_USED=1
    ;;
  --remove | --uninstall)
    MODE="remove"
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RAW_REPO_ROOT="${TRIAD_BOOTSTRAP_REPO_ROOT:-$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)}"
RAW_LAUNCHER_DIR="${TRIAD_BOOTSTRAP_BIN_DIR:-$HOME/.local/bin}"
LAUNCHER_DIR="$RAW_LAUNCHER_DIR"
RAW_CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CODEX_HOME="$RAW_CODEX_HOME"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
RAW_CLASSIFIER_PATH="${TRIAD_CLASSIFIER_EXTENSION:-$CONFIG_HOME/triad-codex-dispatch/classifier-patches.json}"
REPO_ROOT="$RAW_REPO_ROOT"
CLASSIFIER_PATH="$RAW_CLASSIFIER_PATH"
AUTH_TIMEOUT="${TRIAD_BOOTSTRAP_AUTH_TIMEOUT:-30}"
CODEX_PROFILE_NAME="${TRIAD_CODEX_PROFILE_NAME:-triad-codex-dispatch}"
CODEX_PROFILE_APPROVAL_POLICY="${TRIAD_CODEX_PROFILE_APPROVAL_POLICY:-on-request}"
CODEX_RULES_NAME="${TRIAD_CODEX_RULES_NAME:-triad-codex-dispatch.rules}"
CLAUDE_MIN_VERSION="2.1.170"
SHELL_ENTRY_BEGIN="# >>> triad-codex-dispatch codex-triad >>>"
SHELL_ENTRY_END="# <<< triad-codex-dispatch codex-triad <<<"
# Provenance markers for the managed [shell_environment_policy] block that
# merge_codex_config_fragment appends to $CODEX_HOME/config.toml (and
# remove_codex_config_fragment strips). Keyed on these two literal comment
# lines so --remove deletes exactly OUR block and nothing else.
CONFIG_FRAGMENT_BEGIN="# >>> triad-codex-dispatch managed shell_environment_policy >>>"
CONFIG_FRAGMENT_END="# <<< triad-codex-dispatch managed shell_environment_policy <<<"
SHELL_RC="${TRIAD_BOOTSTRAP_SHELL_RC:-}"
if [ -z "$SHELL_RC" ]; then
  case "${SHELL:-}" in
    */zsh) SHELL_RC="$HOME/.zshrc" ;;
    *) SHELL_RC="$HOME/.bashrc" ;;
  esac
fi

errors=0
# SEC2_FLAGGED_SELECTORS -- NEWLINE-joined set of triad-codex-dispatch@*
# selectors check_local_writable_agent_residual (SEC-2) already warned
# about. Populated by that function (called BEFORE check_duplicate_selectors
# in the --install flow, per R3) so DIST-1's hygiene warn can de-duplicate
# rather than emit a second, overlapping warning for the same
# selector/state.
# NEWLINE-joined + exact-LINE membership compare, deliberately NOT a
# space-joined string matched via a `case " $LIST " in *" $item "*)`
# substring test: TOML string keys can contain literal spaces, so a
# pathological selector name equal to two OTHER flagged names joined by a
# single space would false-match that substring test (task-3 review,
# Minor). A bash ARRAY would also fix this, but this script is deliberately
# written array-free/`[[ ]]`-free throughout (see e.g. path_has_dir()) —
# this repo's own hermetic test harness (tests/system/export/
# s3-codex-bootstrap-migration.sh's run_bootstrap()) execs this script via
# a narrowed PATH that resolves `bash` to Apple's frozen /bin/bash 3.2.57,
# where `"${arr[@]}"` on an empty array is a hard "unbound variable" error
# under `set -u` (fixed only in bash 4.4+) -- confirmed by spike.
# add_flagged_selector() (below) appends via a literal embedded newline,
# flagged_selector_matches() reads it back line-by-line with exact
# `[ "$x" = "$name" ]` equality — a name can only spoof a match this way if
# it itself contains a literal embedded newline, which the existing
# read_plugin_selectors TSV wire format (name/flag split on a literal tab,
# one selector per line) already cannot carry through intact, so this
# introduces no new assumption.
# Initialized here (not only inside check_local_writable_agent_residual) so
# it is always bound under `set -u` even if the call order ever changes.
SEC2_FLAGGED_SELECTORS=""

# add_flagged_selector NAME -- appends NAME to the newline-joined
# SEC2_FLAGGED_SELECTORS accumulator (see its declaration comment above).
add_flagged_selector() {
  if [ -z "$SEC2_FLAGGED_SELECTORS" ]; then
    SEC2_FLAGGED_SELECTORS="$1"
  else
    SEC2_FLAGGED_SELECTORS="$SEC2_FLAGGED_SELECTORS
$1"
  fi
}

# flagged_selector_matches NAME -- true (0) iff NAME is present in
# SEC2_FLAGGED_SELECTORS as an exact, whole-line match. See the
# SEC2_FLAGGED_SELECTORS declaration comment above for why this is a
# line-exact compare rather than a substring/case-pattern test.
flagged_selector_matches() {
  target="$1"
  while IFS= read -r flagged_name; do
    [ -z "$flagged_name" ] && continue
    [ "$flagged_name" = "$target" ] && return 0
  done <<EOF
$SEC2_FLAGGED_SELECTORS
EOF
  return 1
}

ok() {
  printf '[ok] %s\n' "$1"
}

warn() {
  printf '[warn] %s\n' "$1"
}

fail() {
  printf '[error] %s\n' "$1" >&2
  errors=$((errors + 1))
}

path_has_dir() {
  case ":$PATH:" in
    *":$1:"*) return 0 ;;
    *) return 1 ;;
  esac
}

launcher_is_managed() {
  launcher="$1"
  wrapper="$2"
  if [ ! -e "$launcher" ]; then
    return 0
  fi
  python3 - "$launcher" "$wrapper" <<'PY'
from pathlib import Path
import sys

MARKER = "# triad-codex-dispatch managed launcher"
path = Path(sys.argv[1])
wrapper = sys.argv[2]
try:
    text = path.read_text(encoding="utf-8")
except UnicodeDecodeError:
    raise SystemExit(1)

legacy_generated = (
    "triad-codex-dispatch" in text
    and f"/bin/{wrapper}" in text
    and "os.execv(" in text
    and "TRIAD_REQUIRE_PINNED_VENDOR" in text
)
raise SystemExit(0 if MARKER in text or legacy_generated else 1)
PY
}

is_expected_wrapper() {
  resolved="$1"
  target="$2"
  launcher="$3"
  if [ -z "$resolved" ] || [ ! -x "$resolved" ]; then
    return 1
  fi
  python3 - "$resolved" "$target" "$launcher" <<'PY'
from pathlib import Path
import shutil
import sys

resolved, target, launcher = (Path(arg).resolve() for arg in sys.argv[1:])
raise SystemExit(0 if resolved in {target, launcher} else 1)
PY
}

# repair_agent_is_managed <path> — SEC-1 provenance predicate for a legacy
# personal-scope repair-agent TOML (an older install left write-capable
# claude/gemini/agy-wrapper-repair.toml files at $CODEX_HOME/agents/; the
# current --install creates none, but must migrate any left behind — see
# migrate_legacy_repair_agents / the --remove loop below). Managed means the
# file carries the BOOTSTRAP-AUTHORED provenance, matched as a START-OF-FILE
# header (first ~5 lines only — never a substring anywhere in the file):
#   (the line-1 pair "# Codex named subagent" AND "wrapper repair agent")
#   OR "Installed by bootstrap to the Codex personal agent-discovery scope"
# This is bootstrap-emitted boilerplate verified present verbatim in the real
# legacy TOMLs and ABSENT from every shipped doc. `default_permissions =
# "triad_repair"` is a WEAK corroborator only (doc-published in
# AGENTS.recommended.md) and is deliberately NOT checked here — it must never
# by itself trigger quarantine/removal of a user's own same-name file.
# lstat BEFORE read: a symlink is never followed/treated as managed, even
# when its target would otherwise match (callers additionally branch on
# `-L` themselves, before ever calling this, so they can warn+skip instead
# of taking the managed/unmanaged action). The bash `[ -L ]` guard and the
# python read below are two syscalls separated by a process spawn, so a
# symlink swapped in during that window would otherwise be silently
# followed by Path.open()'s default behavior; the python side additionally
# opens with O_NOFOLLOW to close that TOCTOU gap (open() fails with ELOOP
# on a symlink, treated the same as any other read failure: NOT managed).
repair_agent_is_managed() {
  path="$1"
  if [ -L "$path" ] || [ ! -f "$path" ]; then
    return 1
  fi
  python3 - "$path" <<'PY'
from pathlib import Path
import os
import sys

HEADER_LINES = 5
TOKEN_HEADER_A = "# Codex named subagent"
TOKEN_HEADER_B = "wrapper repair agent"
TOKEN_SCOPE = "Installed by bootstrap to the Codex personal agent-discovery scope"

path = Path(sys.argv[1])
try:
    # O_NOFOLLOW: never follow a symlink swapped in between the bash-level
    # lstat guard (above) and this open() (TOCTOU) — ELOOP is caught below
    # and treated as NOT managed, same as any other read failure.
    fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "r", encoding="utf-8") as fh:
        head = "".join(next(fh, "") for _ in range(HEADER_LINES))
except (OSError, UnicodeDecodeError):
    raise SystemExit(1)

pair_match = TOKEN_HEADER_A in head and TOKEN_HEADER_B in head
scope_match = TOKEN_SCOPE in head
raise SystemExit(0 if (pair_match or scope_match) else 1)
PY
}

check_binary() {
  if command -v "$1" >/dev/null 2>&1; then
    ok "found binary: $1"
  else
    fail "missing required binary: $1"
  fi
}

check_optional_binary() {
  if command -v "$1" >/dev/null 2>&1; then
    ok "found optional binary: $1"
  else
    warn "optional binary not found: $1"
  fi
}

check_python() {
  if ! command -v python3 >/dev/null 2>&1; then
    fail "missing required binary: python3"
    return
  fi
  if python3 - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 12) else 1)
PY
  then
    ok "python3 >= 3.12"
  else
    fail "python3 >= 3.12 required"
  fi
}

check_claude_version() {
  if ! command -v claude >/dev/null 2>&1; then
    return
  fi
  claude_version_raw="$(claude --version 2>/dev/null || true)"
  claude_version_parsed="$(python3 - "$claude_version_raw" "$CLAUDE_MIN_VERSION" <<'PY'
import re
import sys

raw, minimum = sys.argv[1], sys.argv[2]
match = re.search(r"\d+(?:\.\d+)+", raw)
if match is None:
    raise SystemExit(2)
found = [int(part) for part in match.group(0).split(".")]
want = [int(part) for part in minimum.split(".")]
width = max(len(found), len(want))
found += [0] * (width - len(found))
want += [0] * (width - len(want))
print(match.group(0))
raise SystemExit(0 if found >= want else 1)
PY
)"
  claude_version_rc="$?"
  if [ "$claude_version_rc" -eq 0 ] && [ -n "$claude_version_parsed" ]; then
    ok "claude version $claude_version_parsed >= minimum $CLAUDE_MIN_VERSION"
  elif [ "$claude_version_rc" -eq 1 ] && [ -n "$claude_version_parsed" ]; then
    warn "claude version $claude_version_parsed is older than minimum $CLAUDE_MIN_VERSION; upgrade claude before dispatching the claude leg"
  else
    warn "could not determine claude version (output: $claude_version_raw)"
  fi
}

# MUST-land 1 (workspace-escape guard). See the header invariant: allow-listed
# files and everything they exec must live outside all sandbox-writable roots.
# Hard-fails when any install target (or the checkout / python runtime the
# launchers exec) resolves inside the workspace bootstrap runs from ($PWD).
check_workspace_escape() {
  workspace_guard_output="$(python3 - "$PWD" "$LAUNCHER_DIR" "$CODEX_HOME" "$(dirname -- "$CLASSIFIER_PATH")" "$REPO_ROOT" <<'PY'
from pathlib import Path
import os
import sys

pwd_raw, launcher_raw, codex_home_raw, classifier_dir_raw, repo_root_raw = sys.argv[1:]
workspace = Path(pwd_raw).resolve()


def _fs_case_insensitive(probe):
    # A case-insensitive filesystem (macOS APFS default) resolves an upper- and
    # lower-cased variant of the same existing path to ONE inode; a case-sensitive
    # FS (Linux ext4) does not. This decides whether the containment compare below
    # must case-fold. Without it, Path.is_relative_to compares case-sensitively,
    # so on macOS a mixed-case install target (WS vs ws) slipped past the guard
    # and installed into the sandbox-writable workspace (finding #2, 2026-07-05).
    # os.path.normcase is NOT usable here: it only folds case on Windows (nt) and
    # is a no-op on Darwin/Linux, so it would not have closed the macOS bypass.
    # Known Minor edge (re-confirm 2026-07-05, all 3 legs rated non-blocking): a
    # non-round-trip Unicode casing char in the workspace path (e.g. 'ß'.upper()
    # == 'SS', length changes) makes os.path.exists(up) miss, so this returns
    # False (exact compare) and could miss a mixed-case escape — but only on a
    # case-insensitive FS with a non-ASCII install path AND an attacker-crafted
    # target; realistic install paths are ASCII, and is_expected_wrapper /
    # launcher-managed checks are additional barriers. Defense-in-depth edge, not
    # the sole gate.
    s = str(probe)
    try:
        up, lo = s.upper(), s.lower()
        if not (os.path.exists(up) and os.path.exists(lo)):
            return False
        return os.path.samestat(os.stat(up), os.stat(lo))
    except OSError:
        return False


_CASE_INSENSITIVE = _fs_case_insensitive(workspace)


def _within(target, root):
    t = os.path.normpath(str(target))
    r = os.path.normpath(str(root))
    if _CASE_INSENSITIVE:
        t, r = t.lower(), r.lower()
    # exact match OR a path-boundary-anchored prefix (so /a/ws-dispatch is NOT
    # treated as inside /a/ws — the trailing sep prevents the sibling-prefix trap).
    return t == r or t.startswith(r.rstrip(os.sep) + os.sep)


targets = (
    ("launcher directory (TRIAD_BOOTSTRAP_BIN_DIR)", Path(launcher_raw)),
    ("CODEX_HOME", Path(codex_home_raw)),
    (
        "classifier directory (TRIAD_CLASSIFIER_EXTENSION / XDG_CONFIG_HOME)",
        Path(classifier_dir_raw),
    ),
    ("plugin/checkout root (TRIAD_BOOTSTRAP_REPO_ROOT)", Path(repo_root_raw)),
    ("python3 runtime", Path(sys.executable)),
)
failures = []
for label, target in targets:
    resolved = target.expanduser().resolve()
    if _within(resolved, workspace):
        failures.append(
            f"workspace-escape guard: {label} resolves inside the "
            f"sandbox-writable workspace: {resolved} (workspace root {workspace})"
        )
for line in failures:
    print(line)
raise SystemExit(1 if failures else 0)
PY
)"
  if [ "$?" -ne 0 ]; then
    while IFS= read -r line; do
      [ -n "$line" ] && fail "$line"
    done <<EOF
$workspace_guard_output
EOF
    fail "invariant: allow-listed launchers and everything they exec must live outside all sandbox-writable roots; run bootstrap from a directory that does not contain the install targets, or point the TRIAD_BOOTSTRAP_* / CODEX_HOME overrides outside this workspace"
  fi
}

check_legacy_sandbox_config() {
  base_config="$CODEX_HOME/config.toml"
  if [ -f "$base_config" ] \
    && grep -Eq '^[[:space:]]*sandbox_mode[[:space:]]*=|^\[sandbox_workspace_write\]' "$base_config"; then
    warn "legacy sandbox settings (sandbox_mode / [sandbox_workspace_write]) found in $base_config; any loaded config layer with them disables permission profiles, neutralizing the triad_leader profile's default_permissions scoping — migrate the base config to permission profiles"
  fi
}

# read_plugin_selectors — shared python3 tomllib reader for
# check_duplicate_selectors (DIST-1) and check_local_writable_agent_residual
# (SEC-2). Reads $CODEX_HOME/config.toml (the canonicalized CODEX_HOME) and
# prints one "<selector>\t<true|false>" line per [plugins."triad-codex-dispatch@..."]
# table found — real TOML table parsing via tomllib, not a bash line-follower,
# so a table with `enabled` OMITTED is never confused with an adjacent,
# unrelated table's own `enabled` key. An omitted `enabled` key is treated as
# ENABLED (true): this is codex's documented default — PluginConfig's
# `enabled: bool` field is `#[serde(default = "default_enabled")]` with
# `default_enabled() -> bool { true }` (codex-rs/config/src/types.rs, verified
# against the openai/codex GitHub source 2026-07-16; the top-level `[plugins]`
# table itself deserializes as `pub plugins: HashMap<String, PluginConfig>` in
# codex-rs/config/src/config_toml.rs, keyed by the exact `PLUGIN@MARKETPLACE`
# selector string codex's own `plugin add`/`plugin remove` CLI uses). Any
# `[plugins.*]` table whose name does not start with "triad-codex-dispatch@"
# is ignored (never counted, never misassociated).
#
# A MISSING config.toml is not a failure (a fresh install has zero plugins
# configured yet) — exit 0 with no output. Exit 3 signals the file EXISTS but
# could not be read or parsed (permission error / malformed TOML); the two
# callers deliberately react differently to that signal —
# check_duplicate_selectors treats it as a graceful no-op (hygiene, not a SEC
# surface) while check_local_writable_agent_residual treats it as a WARN (a
# SEC surface must not be silently skipped).
read_plugin_selectors() {
  python3 - "$CODEX_HOME/config.toml" <<'PY'
import sys
import tomllib

path = sys.argv[1]
try:
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
except FileNotFoundError:
    raise SystemExit(0)
except (OSError, tomllib.TOMLDecodeError):
    raise SystemExit(3)

plugins = data.get("plugins")
if not isinstance(plugins, dict):
    raise SystemExit(0)

PREFIX = "triad-codex-dispatch@"
for key, table in plugins.items():
    if not isinstance(key, str) or not key.startswith(PREFIX):
        continue
    if not isinstance(table, dict):
        continue
    enabled = table.get("enabled", True) is True
    print(f"{key}\t{'true' if enabled else 'false'}")
raise SystemExit(0)
PY
}

# cache_write_capable_state MARKETPLACE — SEC-2 helper: does
# $CODEX_HOME/plugins/cache/<MARKETPLACE>/triad-codex-dispatch/*/agents/*.toml
# (any installed version) declare `default_permissions = "triad_repair"`?
# Deliberately walks with Path.iterdir/Path.exists, NOT Path.glob: spike-
# verified 2026-07-16 that pathlib's glob() silently swallows PermissionError
# and returns an empty match list on an unreadable directory — making an
# unreadable cache indistinguishable from an absent one — while
# iterdir()/exists() correctly raise/propagate PermissionError from an
# unreadable directory, which is exactly the signal this SEC-2 check needs in
# order to warn rather than silently report "no residual found". Prints
# exactly one of:
#   absent      — the marketplace/plugin cache directory does not exist
#                 (clean; a plugin that was never installed cannot be a
#                 discovery path)
#   clean       — cache dir readable, every candidate agent TOML parsed
#                 cleanly, and none declares default_permissions = "triad_repair"
#   found       — at least one write-capable agent TOML found (SEC-2 residual)
#   unreadable  — the cache dir (or a file under it) could not be opened, OR
#                 a candidate agent TOML exists and is readable but fails to
#                 PARSE (broken TOML syntax) — a SEC surface must not treat a
#                 file it cannot actually inspect as "clean" just because the
#                 failure was a parse error rather than an OSError (task-3
#                 review, Important; a `found` elsewhere in the same scan
#                 still wins — this only changes what an all-skipped/no-match
#                 scan reports instead of "clean")
cache_write_capable_state() {
  python3 - "$CODEX_HOME/plugins/cache" "$1" <<'PY'
import sys
import tomllib
from pathlib import Path

cache_root = Path(sys.argv[1])
marketplace = sys.argv[2]


def scan() -> str:
    malformed_seen = False
    marketplace_dir = cache_root / marketplace / "triad-codex-dispatch"
    if not marketplace_dir.exists():
        return "absent"
    for version_dir in sorted(p for p in marketplace_dir.iterdir() if p.is_dir()):
        agents_dir = version_dir / "agents"
        if not agents_dir.exists():
            continue
        for toml_file in sorted(agents_dir.iterdir()):
            if not toml_file.is_file() or toml_file.suffix != ".toml":
                continue
            try:
                with open(toml_file, "rb") as fh:
                    data = tomllib.load(fh)
            except tomllib.TOMLDecodeError:
                # Readable but syntactically broken: cannot rule out that
                # THIS file is the write-capable one, so it must not be
                # silently treated the same as "no candidate here" (clean).
                # A later `found` in the same scan still wins outright; only
                # the final "nothing matched" fallback is downgraded below.
                malformed_seen = True
                continue
            if isinstance(data, dict) and data.get("default_permissions") == "triad_repair":
                return "found"
    return "unreadable" if malformed_seen else "clean"


try:
    print(scan())
except OSError:
    print("unreadable")
PY
}

# check_local_writable_agent_residual — SEC-2 preflight (read-only,
# NON-fatal — only ever calls warn, never fail; mutates nothing). Co-located
# with check_legacy_sandbox_config / check_duplicate_selectors, canonicalized
# CODEX_HOME, using the shared read_plugin_selectors tomllib reader.
#
# Confused-deputy write-capable discovery path: an ENABLED
# `triad-codex-dispatch@*-local` selector makes codex discover every agent
# TOML bundled in that plugin's cache directory by name, including
# write-capable ones (default_permissions = "triad_repair") meant only for
# the read-only top-level repair-agent workflow — a stale local-dev
# registration left enabled alongside the real marketplace plugin silently
# reopens that discovery path. Both AND-conditions must hold: (a) an ENABLED
# `-local` selector present in config.toml, AND (b) a write-capable agent
# TOML found under its matching plugins/cache/<...-local>/triad-codex-dispatch/*/agents/.
# Either half missing → no warn.
#
# If config.toml OR the cache dir is UNREADABLE, this warns regardless of
# whether the AND-condition can be confirmed — a SEC surface must not be
# silently skipped (contrast check_duplicate_selectors' graceful hygiene
# read of the identical fault).
#
# Populates SEC2_FLAGGED_SELECTORS (via add_flagged_selector) with every
# selector this warned about, so check_duplicate_selectors — called AFTER
# this, per R3 — can de-duplicate rather than emit a second, overlapping
# hygiene warning for the same selector/state.
check_local_writable_agent_residual() {
  SEC2_FLAGGED_SELECTORS=""
  selectors="$(read_plugin_selectors)"
  read_rc=$?
  if [ "$read_rc" -ne 0 ]; then
    warn "could not read or parse $CODEX_HOME/config.toml to check for a local-scope write-capable plugin-agent residual (SEC-2); verify manually: codex plugin list --json"
    return
  fi
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    name="${line%%$'\t'*}"
    flag="${line#*$'\t'}"
    [ "$flag" = "true" ] || continue
    case "$name" in
      triad-codex-dispatch@*-local) ;;
      *) continue ;;
    esac
    marketplace="${name#triad-codex-dispatch@}"
    state="$(cache_write_capable_state "$marketplace")"
    case "$state" in
      found)
        warn "confused-deputy write-capable discovery path: $name is ENABLED and its plugin cache ($CODEX_HOME/plugins/cache/$marketplace/triad-codex-dispatch/) bundles a write-capable agent TOML (default_permissions = \"triad_repair\"); a local-scope selector should not stay registered alongside the real plugin — remediation: codex plugin remove $name"
        add_flagged_selector "$name"
        ;;
      unreadable)
        warn "could not verify the plugin cache for $name (unreadable: $CODEX_HOME/plugins/cache/$marketplace/triad-codex-dispatch/) — cannot rule out a confused-deputy write-capable discovery path; verify manually, then: codex plugin remove $name"
        add_flagged_selector "$name"
        ;;
      absent | clean) ;;
    esac
  done <<EOF
$selectors
EOF
}

# check_duplicate_selectors — DIST-1 preflight (read-only, NON-fatal — only
# ever calls warn, never fail; mutates nothing). Co-located with
# check_legacy_sandbox_config / check_local_writable_agent_residual,
# canonicalized CODEX_HOME, using the shared read_plugin_selectors tomllib
# reader. Counts ENABLED `triad-codex-dispatch@*` plugin selectors in
# config.toml; more than one enabled at once is a distribution hygiene
# problem (a leftover local-dev registration alongside the real marketplace
# one, or any other accidental duplicate) — warns naming every duplicate plus
# a one-line remediation. Ignores unrelated plugin tables (any `[plugins.*]`
# whose name does not match) and never counts a disabled or commented-out
# selector table.
#
# De-dup contract (R3): never re-report a selector check_local_writable_agent_residual
# (SEC-2, called BEFORE this) already warned about via SEC2_FLAGGED_SELECTORS
# — that selector's state was already reported with the stronger SEC framing,
# so repeating it here would be a second, overlapping warning for the same
# state. Membership is an exact-line compare via flagged_selector_matches()
# (not a space-joined substring test — see the SEC2_FLAGGED_SELECTORS
# declaration comment for why that would not be collision-proof). If
# excluding SEC-2-flagged selectors leaves 1 or 0 remaining candidates, this
# stays silent even though the raw enabled count may be >1.
#
# Malformed/unreadable config.toml → graceful (no crash, no false warn) —
# this is hygiene, not a SEC surface (contrast check_local_writable_agent_residual).
check_duplicate_selectors() {
  selectors="$(read_plugin_selectors)"
  read_rc=$?
  if [ "$read_rc" -ne 0 ]; then
    return
  fi
  enabled_count=0
  names_joined=""
  stale_count=0
  stale_names=""
  stale_cmds=""
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    name="${line%%$'\t'*}"
    flag="${line#*$'\t'}"
    [ "$flag" = "true" ] || continue
    flagged_selector_matches "$name" && continue
    enabled_count=$((enabled_count + 1))
    if [ -z "$names_joined" ]; then
      names_joined="$name"
    else
      names_joined="$names_joined, $name"
    fi
    case "$name" in
      *-local)
        stale_count=$((stale_count + 1))
        if [ -z "$stale_names" ]; then
          stale_names="$name"
          stale_cmds="codex plugin remove $name"
        else
          stale_names="$stale_names, $name"
          stale_cmds="$stale_cmds && codex plugin remove $name"
        fi
        ;;
    esac
  done <<EOF
$selectors
EOF
  if [ "$enabled_count" -le 1 ]; then
    return
  fi
  if [ "$stale_count" -eq 1 ]; then
    warn "duplicate ENABLED triad-codex-dispatch plugin selectors in $CODEX_HOME/config.toml: $names_joined; remove the stale one: $stale_cmds"
  elif [ "$stale_count" -gt 1 ]; then
    warn "duplicate ENABLED triad-codex-dispatch plugin selectors in $CODEX_HOME/config.toml: $names_joined; remove each of the stale ones ($stale_names): $stale_cmds"
  else
    warn "duplicate ENABLED triad-codex-dispatch plugin selectors in $CODEX_HOME/config.toml: $names_joined; keep only one of them (codex plugin remove <selector>)"
  fi
}

# migrate_legacy_repair_agents — SEC-1 (--install side). QUARANTINES any
# provenance-managed legacy repair-agent TOML found at $CODEX_HOME/agents/
# into a timestamped sibling directory OUTSIDE agents/ (Codex only discovers
# agents under agents/, so a sibling dir is provably not a discovery path).
# Idempotent (a second --install finds nothing left to quarantine). Never
# halts --install: a quarantine-dir-create or move failure just warns and
# continues to the next name. Called AFTER the errors!=0 -> exit 1 preflight
# gate and check_legacy_sandbox_config, BEFORE install_launchers.
migrate_legacy_repair_agents() {
  quarantine_dir=""
  quarantine_attempted=0
  for name in claude-wrapper-repair gemini-wrapper-repair agy-wrapper-repair; do
    agent_file="$CODEX_HOME/agents/$name.toml"
    if [ -L "$agent_file" ]; then
      warn "leaving legacy repair-agent symlink in place (never following a symlink target): $agent_file"
      continue
    fi
    if [ ! -e "$agent_file" ]; then
      continue
    fi
    if ! repair_agent_is_managed "$agent_file"; then
      warn "leaving unmanaged repair agent in place: $agent_file"
      continue
    fi
    if [ "$quarantine_attempted" -eq 0 ]; then
      quarantine_attempted=1
      quarantine_dir="$(mktemp -d "$CODEX_HOME/.triad-quarantine-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX" 2>/dev/null)"
    fi
    if [ -z "$quarantine_dir" ] || [ ! -d "$quarantine_dir" ]; then
      warn "could not create quarantine directory under $CODEX_HOME; leaving legacy repair agent in place: $agent_file"
      continue
    fi
    quarantine_dest="$quarantine_dir/$name.toml"
    if mv "$agent_file" "$quarantine_dest" 2>/dev/null; then
      warn "quarantined legacy repair agent: $agent_file -> $quarantine_dest"
    else
      warn "could not quarantine legacy repair agent (leaving in place): $agent_file"
    fi
  done
}

canonicalize_path_inputs() {
  canonicalize_err="$(mktemp "${TMPDIR:-/tmp}/triad-codex-canonicalize.XXXXXX")" || {
    fail "could not create temporary file for path canonicalization"
    return
  }
  canonicalized="$(python3 - "$RAW_REPO_ROOT" "$RAW_CLASSIFIER_PATH" "$RAW_LAUNCHER_DIR" "$RAW_CODEX_HOME" 2>"$canonicalize_err" <<'PY'
from pathlib import Path
import shutil
import sys

repo_raw, classifier_raw, launcher_raw, codex_home_raw = sys.argv[1:]
repo = Path(repo_raw).expanduser()
classifier = Path(classifier_raw).expanduser()
launcher = Path(launcher_raw).expanduser()
codex_home = Path(codex_home_raw).expanduser()
errors = []
if not repo.is_absolute():
    errors.append(f"TRIAD_BOOTSTRAP_REPO_ROOT must be an absolute path: {repo_raw}")
elif not repo.is_dir():
    errors.append(f"TRIAD_BOOTSTRAP_REPO_ROOT is not an existing directory: {repo_raw}")
if not classifier.is_absolute():
    errors.append(f"TRIAD_CLASSIFIER_EXTENSION must be an absolute path: {classifier_raw}")
if not launcher.is_absolute():
    errors.append(f"TRIAD_BOOTSTRAP_BIN_DIR must be an absolute path: {launcher_raw}")
if not codex_home.is_absolute():
    errors.append(f"CODEX_HOME must be an absolute path: {codex_home_raw}")
if errors:
    for error in errors:
        print(error)
    raise SystemExit(1)
print(repo.resolve())
print(classifier.parent.resolve(strict=False) / classifier.name)
print(launcher.resolve(strict=False))
print(codex_home.resolve(strict=False))
PY
  )"
  if [ "$?" -ne 0 ]; then
    canonicalize_output="$(
      printf '%s\n' "$canonicalized"
      cat "$canonicalize_err"
    )"
    while IFS= read -r line; do
      [ -n "$line" ] && fail "$line"
    done <<EOF
$canonicalize_output
EOF
    rm -f "$canonicalize_err"
    return
  fi
  if [ -s "$canonicalize_err" ]; then
    while IFS= read -r line; do
      [ -n "$line" ] && warn "$line"
    done <"$canonicalize_err"
  fi
  rm -f "$canonicalize_err"
  REPO_ROOT="$(printf '%s\n' "$canonicalized" | sed -n '1p')"
  CLASSIFIER_PATH="$(printf '%s\n' "$canonicalized" | sed -n '2p')"
  LAUNCHER_DIR="$(printf '%s\n' "$canonicalized" | sed -n '3p')"
  CODEX_HOME="$(printf '%s\n' "$canonicalized" | sed -n '4p')"
}

run_auth_probe() {
  name="$1"
  cmd="$2"
  required="${3:-required}"
  python3 - "$AUTH_TIMEOUT" "$cmd" <<'PY'
import subprocess
import sys

timeout = int(sys.argv[1])
cmd = sys.argv[2]
try:
    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
    )
except subprocess.TimeoutExpired:
    raise SystemExit(124)
raise SystemExit(result.returncode)
PY
  rc=$?
  if [ "$rc" -eq 0 ]; then
    ok "$name auth probe passed"
  elif [ "$rc" -eq 124 ]; then
    if [ "$required" = "required" ]; then
      fail "$name auth probe timed out after ${AUTH_TIMEOUT}s"
    else
      warn "$name auth probe timed out after ${AUTH_TIMEOUT}s"
    fi
  else
    if [ "$required" = "required" ]; then
      fail "$name auth probe failed"
    else
      warn "$name auth probe failed"
    fi
  fi
}

check_auth() {
  if [ "${TRIAD_BOOTSTRAP_SKIP_AUTH:-0}" = "1" ]; then
    warn "auth probes skipped by TRIAD_BOOTSTRAP_SKIP_AUTH=1"
    return
  fi

  run_auth_probe "codex" "${TRIAD_BOOTSTRAP_CODEX_AUTH_CMD:-codex login status}"
  run_auth_probe "claude" "${TRIAD_BOOTSTRAP_CLAUDE_AUTH_CMD:-\"$LAUNCHER_DIR/claude_wrapper.py\" --prompt 'Return exactly OK.' --sandbox read-only --timeout $AUTH_TIMEOUT}"
  run_auth_probe "agy" "${TRIAD_BOOTSTRAP_AGY_AUTH_CMD:-\"$LAUNCHER_DIR/antigravity_wrapper.py\" --prompt 'Return exactly OK.' --sandbox read-only --timeout $AUTH_TIMEOUT}"
  if command -v gemini >/dev/null 2>&1; then
    if [ "${TRIAD_BOOTSTRAP_REQUIRE_GEMINI:-0}" = "1" ]; then
      run_auth_probe "gemini" "${TRIAD_BOOTSTRAP_GEMINI_AUTH_CMD:-\"$LAUNCHER_DIR/gemini_wrapper.py\" --prompt 'Return exactly OK.' --sandbox read-only --timeout $AUTH_TIMEOUT}"
    else
      run_auth_probe "gemini" "${TRIAD_BOOTSTRAP_GEMINI_AUTH_CMD:-\"$LAUNCHER_DIR/gemini_wrapper.py\" --prompt 'Return exactly OK.' --sandbox read-only --timeout $AUTH_TIMEOUT}" optional
    fi
  elif [ "${TRIAD_BOOTSTRAP_REQUIRE_GEMINI:-0}" = "1" ]; then
    fail "missing required binary: gemini"
  else
    warn "gemini auth probe skipped because gemini is not installed"
  fi
}

install_launchers() {
  repo_bin="$REPO_ROOT/bin"
  if [ ! -d "$repo_bin" ]; then
    fail "missing repo bin directory: $repo_bin"
    return
  fi

  all_wrappers_ready=1
  for wrapper in claude_wrapper.py gemini_wrapper.py antigravity_wrapper.py; do
    target="$repo_bin/$wrapper"
    resolved="$(command -v "$wrapper" 2>/dev/null || true)"
    if ! is_expected_wrapper "$resolved" "$target" "$target"; then
      all_wrappers_ready=0
    fi
  done
  if [ "$all_wrappers_ready" -eq 1 ]; then
    ok "wrapper commands resolve to this checkout"
  fi

  mkdir -p "$LAUNCHER_DIR" || {
    fail "could not create launcher directory: $LAUNCHER_DIR"
    return
  }

  for wrapper in claude_wrapper.py gemini_wrapper.py antigravity_wrapper.py; do
    target="$repo_bin/$wrapper"
    launcher="$LAUNCHER_DIR/$wrapper"
    if [ ! -f "$target" ]; then
      fail "missing wrapper: $target"
      continue
    fi
    if ! launcher_is_managed "$launcher" "$wrapper"; then
      fail "refusing to overwrite unmanaged launcher: $launcher"
      continue
    fi
    escaped_target="$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$target")" || {
      fail "could not quote launcher target: $target"
      continue
    }
python_exe="$(python3 - <<'PY'
from pathlib import Path
import sys
print(Path(sys.executable).resolve())
PY
)" || {
      fail "could not resolve python executable for launcher: $wrapper"
      continue
    }
    escaped_python="$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$python_exe")" || {
      fail "could not quote launcher python: $python_exe"
      continue
    }
    case "$wrapper" in
      claude_wrapper.py)
        vendor_cmd="claude"
        vendor_env="TRIAD_CLAUDE_BIN"
        ;;
      antigravity_wrapper.py)
        vendor_cmd="agy"
        vendor_env="TRIAD_AGY_BIN"
        ;;
      gemini_wrapper.py)
        vendor_cmd="gemini"
        vendor_env="TRIAD_GEMINI_BIN"
        ;;
      *)
        fail "unknown wrapper: $wrapper"
        continue
        ;;
    esac
    vendor_path=""
    if command -v "$vendor_cmd" >/dev/null 2>&1; then
      vendor_path="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$(command -v "$vendor_cmd")")" || {
        fail "could not resolve vendor binary for $wrapper: $vendor_cmd"
        continue
      }
    fi
    escaped_vendor_env="$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$vendor_env")" || {
      fail "could not quote vendor env for $wrapper"
      continue
    }
    escaped_vendor_path="$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$vendor_path")" || {
      fail "could not quote vendor path for $wrapper"
      continue
    }
    # Trusted PATH for the launcher's constructed env: the install-time PATH,
    # which already resolved the vendor + its runtime and is the operator's env
    # (a sandboxed session cannot influence it), NOT a session-runtime PATH. Pins
    # where the vendor's own `#!/usr/bin/env node` (or a python shim) resolves its
    # interpreter, closing the PATH-shim sub-channel.
    escaped_path="$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "${PATH:-/usr/bin:/bin}")" || {
      fail "could not quote launcher PATH for $wrapper"
      continue
    }
    {
      # SEC-3 POSITIVE ENVIRONMENT POLICY. This launcher is allow-listed by
      # install_codex_rules and runs OUTSIDE the codex sandbox, so the whole
      # inherited environment is a trust boundary: any inherited loader/runtime
      # var makes an outside-sandbox process run workspace code. The pre-merge
      # re-review (codex + claude legs, 2026-07-16) converged that enumerating
      # bad vars one at a time is structurally incomplete; instead the launcher
      # hands the wrapper + vendor a DELIBERATELY CONSTRUCTED env: start from the
      # inherited env, DROP the known code-injection loader/interpreter vars, and
      # pin PATH to the trusted install-time value. os.execve (not execv) applies
      # it, and the wrapper's own vendor subprocess inherits it in turn (so the
      # shared _common Popen needs no change -- it inherits this clean env).
      #
      # -E on the shebang isolates THIS launcher's OWN interpreter startup from
      # PYTHONPATH/PYTHONHOME (the env construction below runs after startup, too
      # late for the launcher itself); -E on the exec is belt-and-suspenders for
      # the wrapper. -E, not -I: -I drops user site-packages, breaking a
      # --user-installed pydantic the wrappers import.
      #
      # RESIDUALS this launcher CANNOT self-close (documented, tracked):
      #   * HOME -> user-site: -E keeps user-site (for pydantic), and CPython
      #     derives ~/.local/... user-site from HOME, so a poisoned HOME points
      #     user-site at a workspace sitecustomize.py that runs before line 1.
      #     Dropping HOME would break vendor auth; the real close is relocating
      #     the wrapper deps into a venv/trusted dir so user-site can be disabled.
      #   * LD_PRELOAD/DYLD_* into THIS launcher's OWN process: the dynamic linker
      #     honors them at exec, before any launcher code -- only the boundary
      #     that SPAWNS the launcher (codex's shell_environment_policy) can
      #     neutralize that. We still drop them from the constructed env so the
      #     wrapper + vendor are protected.
      printf '#!%s -E\n' "$python_exe"
      printf '# triad-codex-dispatch managed launcher\n'
      printf 'import os\n'
      printf 'import sys\n'
      printf '_SCRUB = (\n'
      printf '    "LD_PRELOAD", "LD_LIBRARY_PATH", "LD_AUDIT", "LD_DEBUG",\n'
      printf '    "DYLD_INSERT_LIBRARIES", "DYLD_LIBRARY_PATH", "DYLD_FRAMEWORK_PATH",\n'
      printf '    "NODE_OPTIONS", "NODE_PATH",\n'
      printf '    "PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP",\n'
      printf '    "BASH_ENV", "ENV", "PERL5LIB", "RUBYOPT", "RUBYLIB",\n'
      printf ')\n'
      printf 'env = {k: v for k, v in os.environ.items() if k not in _SCRUB}\n'
      printf 'env["PATH"] = %s\n' "$escaped_path"
      # ALWAYS require a pin (SEC-3 / C1): a resolved vendor bakes TRIAD_<CLI>_BIN
      # below; an absent one leaves the require flag with NO pin so
      # _common.require_binary fails closed (EXIT_BINARY_MISSING, "refusing PATH
      # fallback") rather than PATH-resolving or honoring an injected pin.
      printf 'env["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"\n'
      if [ -n "$vendor_path" ]; then
        printf 'env[%s] = %s\n' "$escaped_vendor_env" "$escaped_vendor_path"
      else
        # Absent: the launcher OWNS the pin by dropping any inherited value from
        # the constructed env -- require_binary trusts a VALID pin over the
        # require flag, so an injected TRIAD_<CLI>_BIN=/workspace/evil would
        # otherwise be exec'd.
        printf 'env.pop(%s, None)\n' "$escaped_vendor_env"
      fi
      printf 'os.execve(%s, [%s, "-E", %s] + sys.argv[1:], env)\n' "$escaped_python" "$escaped_python" "$escaped_target"
    } >"$launcher" || {
      fail "could not write launcher: $launcher"
      continue
    }
    chmod 0755 "$launcher" || fail "could not chmod launcher: $launcher"
  done

  if ! path_has_dir "$LAUNCHER_DIR"; then
    fail "launcher directory is not on PATH: $LAUNCHER_DIR"
    return
  fi

  for wrapper in claude_wrapper.py gemini_wrapper.py antigravity_wrapper.py; do
    target="$repo_bin/$wrapper"
    launcher="$LAUNCHER_DIR/$wrapper"
    resolved="$(command -v "$wrapper" 2>/dev/null || true)"
    if ! is_expected_wrapper "$resolved" "$target" "$launcher"; then
      fail "wrapper command is shadowed or stale on PATH: $wrapper resolves to ${resolved:-<missing>} (expected $launcher or $target)"
    fi
  done

  if [ "$errors" -eq 0 ]; then
    ok "launcher scripts installed and active on PATH: $LAUNCHER_DIR"
  fi
}

# The profile + command rules install by DEFAULT (a plain --install with 0 env
# vars yields the recommended setup). want_codex_profile / want_codex_rules
# encode that default-ON with two opt-outs each: an explicit ...=0, or the
# ...SKIP_... escape. The approval-policy prompt is NOT affected by these — it
# stays on-request unless TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never is set
# separately, so defaulting the profile ON never silently auto-approves.
want_codex_profile() {
  [ "${TRIAD_BOOTSTRAP_SKIP_CODEX_PROFILE:-0}" != "1" ] \
    && [ "${TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE:-1}" != "0" ]
}

want_codex_rules() {
  [ "${TRIAD_BOOTSTRAP_SKIP_CODEX_RULES:-0}" != "1" ] \
    && [ "${TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES:-1}" != "0" ]
}

ensure_log_dir() {
  dir="$REPO_ROOT/bin/_logs"
  mkdir -p "$dir" || {
    fail "could not create runtime log directory: $dir"
    return
  }
  ok "runtime log directory exists: $dir"
}

install_codex_runtime_profile() {
  if ! want_codex_profile; then
    return
  fi

  classifier_dir="$(dirname -- "$CLASSIFIER_PATH")"
  log_dir="$REPO_ROOT/bin/_logs"
  debug_dir="$REPO_ROOT/bin/_debug"
  bin_dir="$REPO_ROOT/bin"
  codex_home="$CODEX_HOME"

  # SEC-3 exec-target write-denies (R1): the profile denies write on the
  # wrapper .py exec targets (bin_dir), the allow-listed launchers
  # (LAUNCHER_DIR), the resolved python3 runtime, and each resolved vendor
  # binary the wrappers exec -- see the header invariant + the python
  # heredoc comment below for why. Resolve the python3 runtime the same way
  # install_launchers resolves it for the launcher shebang (bare `python3`
  # on PATH; sys.executable canonicalized) so the deny matches the actual
  # exec target.
  python_runtime="$(python3 - <<'PY'
from pathlib import Path
import sys
print(Path(sys.executable).resolve())
PY
)" || {
    fail "could not resolve the python3 runtime path for the Codex profile deny-list"
    return
  }

  # Vendor binaries (claude, gemini, agy -- the ones this product's wrappers
  # exec). Resolved IDENTICALLY to install_launchers' bare `command -v $cmd`
  # (deliberately NOT the same resolution _common.require_binary uses at
  # wrapper-runtime, and deliberately NOT consulting a TRIAD_<CLI>_BIN pin
  # from bootstrap's own environment): install_launchers unconditionally
  # writes `os.environ[TRIAD_<CLI>_BIN] = <command -v result>` into the
  # launcher it emits, so the launcher's own env-var write OVERWRITES
  # whatever pin was set in bootstrap's invoking shell before the wrapper
  # ever reads it -- the launcher's `command -v`-resolved path is what
  # actually gets exec'd, every time. A deny keyed off a pin that
  # install_launchers ignores would protect a path the launcher never uses,
  # while leaving its real exec target uncovered. A vendor not found (e.g.
  # optional gemini) resolves to an empty line and is skipped -- never a
  # fail, per R1 ("skip a vendor not installed").
  claude_bin=""
  if command -v claude >/dev/null 2>&1; then
    claude_bin="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$(command -v claude)")" || {
      fail "could not resolve vendor binary for the Codex profile deny-list: claude"
      return
    }
  fi
  gemini_bin=""
  if command -v gemini >/dev/null 2>&1; then
    gemini_bin="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$(command -v gemini)")" || {
      fail "could not resolve vendor binary for the Codex profile deny-list: gemini"
      return
    }
  fi
  agy_bin=""
  if command -v agy >/dev/null 2>&1; then
    agy_bin="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$(command -v agy)")" || {
      fail "could not resolve vendor binary for the Codex profile deny-list: agy"
      return
    }
  fi

  profile_err="$(mktemp "${TMPDIR:-/tmp}/triad-codex-profile.XXXXXX")" || {
    fail "could not create temporary file for Codex profile install"
    return
  }
  installed="$(python3 - "$codex_home" "$CODEX_PROFILE_NAME" "$CODEX_PROFILE_APPROVAL_POLICY" "$classifier_dir" "$log_dir" "$bin_dir" "$LAUNCHER_DIR" "$debug_dir" "$python_runtime" "$claude_bin" "$gemini_bin" "$agy_bin" 2>"$profile_err" <<'PY'
from pathlib import Path
import sys

MARKER = "# triad-codex-dispatch managed runtime profile"

(
    codex_home_raw, profile_name, approval_policy, classifier_dir_raw, log_dir_raw,
    bin_dir_raw, launcher_dir_raw, debug_dir_raw, python_runtime_raw,
    claude_bin_raw, gemini_bin_raw, agy_bin_raw,
) = sys.argv[1:]
if not profile_name or "/" in profile_name or "\\" in profile_name:
    print(f"invalid TRIAD_CODEX_PROFILE_NAME: {profile_name!r}")
    raise SystemExit(1)
if approval_policy not in {"never", "on-request", "untrusted"}:
    print(f"invalid TRIAD_CODEX_PROFILE_APPROVAL_POLICY: {approval_policy!r}")
    raise SystemExit(1)

codex_home = Path(codex_home_raw).expanduser()
classifier_dir = Path(classifier_dir_raw)
log_dir = Path(log_dir_raw)
bin_dir = Path(bin_dir_raw)
launcher_dir = Path(launcher_dir_raw)
debug_dir = Path(debug_dir_raw)
python_runtime = Path(python_runtime_raw)
vendor_bins = [Path(p) for p in (claude_bin_raw, gemini_bin_raw, agy_bin_raw) if p]
profile_path = codex_home / f"{profile_name}.config.toml"

def toml_string(value: Path) -> str:
    text = str(value)
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'

# --- SEC-3: exec-target write-denies ------------------------------------
# Workspace-escape invariant (see this script's header): the wrapper .py
# exec targets (bin_dir), the allow-listed launchers (launcher_dir), the
# python3 runtime, and the vendor CLI binaries the wrappers exec must be
# non-writable from inside a sandboxed session -- otherwise a tampered exec
# target is a promptless sandbox-escape chain (spike-proven 2026-07-16: a
# codex session with cwd=the checkout CAN overwrite bin/*.py under the
# shipped :workspace-extending profile; a "read" deny blocks it; codex's
# more-specific-wins precedence lets the nested bin/_logs and bin/_debug
# re-allows below survive the bin_dir deny, so logging/--debug keep working).
#
# _is_broad_root guards the two DIRECTORY-level denies (bin_dir,
# launcher_dir): denying an entire directory is only safe when that
# directory is dedicated to OUR exec targets. If either resolves to a
# broad shared root (the filesystem root, $HOME itself, or a
# system/package-manager bin directory shared with unrelated tools -- e.g.
# TRIAD_BOOTSTRAP_BIN_DIR pointed at /opt/homebrew/bin), a directory-wide
# deny would lock the operator out of far more than our own exec targets.
# In that case, fall back to denying just the exec-target FILES actually
# present under it (still closes the attack, without the collateral
# lockout). python_runtime and each vendor binary are ALWAYS denied at the
# file level (never their containing directory), for the same reason --
# they routinely live in a directory shared with many unrelated binaries.
_HOME = Path.home().resolve()
_BROAD_ROOTS = {
    # .resolve()d once, same as _HOME above: a broad root can itself be a
    # symlink (macOS /tmp -> /private/tmp; Ubuntu usrmerge /lib -> /usr/lib),
    # and the candidate directory this is compared against (bin_dir /
    # launcher_dir) is always already resolved by canonicalize_path_inputs
    # before this heredoc runs. Comparing an unresolved literal against a
    # resolved candidate would silently miss the guard on those platforms
    # and fall through to a whole-directory deny -- the over-restrictive
    # failure mode this guard exists to prevent.
    Path(p).resolve() for p in (
        "/", "/usr", "/usr/local", "/usr/local/bin", "/usr/local/sbin",
        "/usr/bin", "/usr/sbin", "/bin", "/sbin",
        "/opt", "/opt/homebrew", "/opt/homebrew/bin", "/opt/homebrew/sbin",
        "/lib", "/lib64", "/etc", "/var", "/tmp", "/root",
    )
}

def _is_broad_root(path: Path) -> bool:
    return path in _BROAD_ROOTS or path == _HOME

def _deny_targets(directory: Path) -> list[Path]:
    # Broad root: deny the REAL regular files actually present in the
    # directory at install time, enumerated dynamically -- not a hardcoded
    # filename list. bin_dir ships more than the 3 wrapper launchers (e.g.
    # _common.py, _pty.py, _agy_settings.py, apply_patch.py -- the single
    # trusted classifier-patch write path; see export_plugin.py
    # CODEX_HOST_BIN), and a hardcoded list would silently stop covering
    # whatever bin/ ships next. Non-recursive (top-level only): nested
    # subdirectories (log_dir/debug_dir under bin_dir) are handled
    # separately by the re-allows below. Left uncaught on purpose: an
    # enumeration failure (e.g. permission denied) propagates as an
    # uncaught exception, failing the whole profile install loudly rather
    # than silently shipping an incomplete deny-list.
    if not _is_broad_root(directory):
        return [directory]
    return sorted(p for p in directory.iterdir() if p.is_file())

deny_paths: list[Path] = []
deny_paths.extend(_deny_targets(bin_dir))
deny_paths.extend(_deny_targets(launcher_dir))
deny_paths.append(python_runtime)
deny_paths.extend(vendor_bins)

# De-dupe while preserving first-seen (deny-then-reallow) order -- e.g.
# bin_dir == launcher_dir in a degenerate override, or the broad-root
# fallback for both landing on the same file list -- TOML tables reject
# duplicate keys.
seen: set[str] = set()
deny_lines = []
for p in deny_paths:
    key = str(p)
    if key in seen:
        continue
    seen.add(key)
    deny_lines.append(f'{toml_string(p)} = "read"')

reallow_lines = []
for p in (classifier_dir, log_dir, debug_dir):
    key = str(p)
    if key in seen:
        continue
    seen.add(key)
    reallow_lines.append(f'{toml_string(p)} = "write"')

deny_block = "\n".join(deny_lines)
reallow_block = "\n".join(reallow_lines)

codex_home.mkdir(parents=True, exist_ok=True)
if profile_path.exists():
    existing = profile_path.read_text(encoding="utf-8")
    if MARKER not in existing:
        print(f"refusing to overwrite unmanaged Codex profile: {profile_path}")
        raise SystemExit(1)

profile_path.write_text(
    f"""{MARKER}
# Generated by scripts/bootstrap.sh --install.
# Re-run with TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 to refresh.
# Explicit external-CLI consent profile: triad dispatch may send relevant
# prompt/repo review material to authenticated claude, agy, and gemini CLIs.
# Permission-profile system (developers.openai.com/codex/permissions).
# Do NOT reintroduce legacy sandbox_mode / [sandbox_workspace_write] in this
# or any loaded config layer: legacy sandbox settings disable
# default_permissions, which would neutralize the triad_leader permission
# profile's scoping.
approval_policy = "{approval_policy}"
approvals_reviewer = "user"
default_permissions = "triad_leader"

[permissions.triad_leader]
description = "Triad leader session: workspace writes plus triad runtime dirs; network on."
extends = ":workspace"

[permissions.triad_leader.filesystem]
# --- SEC-3 exec-target write-denies (wrapper .py / launchers / python3 / vendor CLIs) ---
{deny_block}
# --- re-allows: log_dir/debug_dir are nested under bin_dir (more-specific-wins survives that deny); classifier_dir is a separate, non-nested directory allowed independently ---
{reallow_block}

[permissions.triad_leader.network]
enabled = true
""",
    encoding="utf-8",
)
print(profile_path)
PY
  )"
  if [ "$?" -ne 0 ]; then
    profile_output="$(
      printf '%s\n' "$installed"
      cat "$profile_err"
    )"
    while IFS= read -r line; do
      [ -n "$line" ] && fail "$line"
    done <<EOF
$profile_output
EOF
    rm -f "$profile_err"
    return
  fi
  if [ -s "$profile_err" ]; then
    while IFS= read -r line; do
      [ -n "$line" ] && warn "$line"
    done <"$profile_err"
  fi
  rm -f "$profile_err"
  ok "Codex runtime profile installed: $installed"
}

# merge_codex_config_fragment — SEC-3 native env-boundary close (Slice A
# Layer ②, task-3-brief.md). Merges codex's NATIVE loader-env allowlist
# ([shell_environment_policy] inherit = "core") into $CODEX_HOME/config.toml so
# Codex drops loader/interpreter injection vars (LD_PRELOAD, LD_LIBRARY_PATH,
# DYLD_INSERT_LIBRARIES, NODE_OPTIONS, PYTHONPATH, ...) from the environment of
# EVERY subprocess it spawns -- including the allow-listed wrapper launchers
# that run OUTSIDE the sandbox. This is the native close of the one residual
# the launcher's own env scrub cannot reach: an LD_PRELOAD/DYLD_* aimed at the
# launcher's OWN process, which the dynamic linker honors at exec BEFORE any
# launcher line runs (see the SEC-3 launcher comment in install_launchers).
# Codex's default inherit="all" strips only *KEY*/*SECRET*/*TOKEN* names, so
# loader vars pass through UNSCRUBBED by default; inherit="core" keeps only a
# positive allowlist (PATH/HOME/USER/SHELL/TERM/LANG/LC_*), dropping every
# loader var (Tier-1: learn.chatgpt.com/docs/config-file/config-advanced #
# shell_environment_policy; the table is read from $CODEX_HOME/config.toml).
#
# G4 (never clobber a user's own config): there is NO stdlib TOML *writer*
# (tomllib is read-only), so a hand-rolled full-file re-emit would destroy the
# user's comments/formatting/ordering. Instead the python heredoc uses tomllib
# ONLY to PARSE the existing config.toml and CHECK whether a
# [shell_environment_policy] table already exists:
#   * OUR managed marker block already present -> no-op (idempotent).
#   * a [shell_environment_policy] table present but NOT ours (user's own)
#       -> leave it untouched; WARN (respect the user's config).
#   * absent -> APPEND the marker-delimited managed block (preserving every
#       other key), written atomically (temp + os.replace) after a .bak backup
#       of the prior file.
# NON-fatal by design (defense-in-depth on top of the always-on launcher env
# scrub): never calls fail -- any read/parse/write error just WARNs and leaves
# config.toml untouched, so a config.toml hiccup never blocks --install.
# Gated on want_codex_profile (same gate the replaced WARN used): the fragment
# reinforces the same exec-target trust boundary the managed profile protects.
# bash-3.2-safe: array-free/[[ ]]-free; the python heredoc does the TOML work
# (mirrors install_codex_runtime_profile / check_legacy_sandbox_config).
merge_codex_config_fragment() {
  if ! want_codex_profile; then
    return
  fi
  config_path="$CODEX_HOME/config.toml"
  merge_status="$(python3 - "$config_path" "$CONFIG_FRAGMENT_BEGIN" "$CONFIG_FRAGMENT_END" <<'PY'
import os
import sys
import tempfile
import tomllib
from pathlib import Path

config_path = Path(sys.argv[1])
begin = sys.argv[2]
end = sys.argv[3]

FRAGMENT = '[shell_environment_policy]\ninherit = "core"\n'
managed_block = begin + "\n" + FRAGMENT + end + "\n"

# Step 1. Read the existing file; graceful if absent or unreadable.
try:
    existing = config_path.read_text(encoding="utf-8")
    existed = True
except FileNotFoundError:
    existing = ""
    existed = False
except (OSError, UnicodeDecodeError):
    print("unreadable")
    raise SystemExit(0)

# Step 2. Idempotent -- our own managed marker already present means no-op.
if begin in existing:
    print("already-managed")
    raise SystemExit(0)

# Step 3. Parse ONLY to detect a pre-existing [shell_environment_policy] table.
# There is no stdlib TOML writer, so we never re-emit the existing file.
try:
    data = tomllib.loads(existing) if existing else {}
except tomllib.TOMLDecodeError:
    print("malformed")
    raise SystemExit(0)

if "shell_environment_policy" in data:
    # The user has their own policy -> never clobber it.
    print("user-policy")
    raise SystemExit(0)

# Step 4. Absent -> append the marker-delimited managed block, preserving every
# prior byte. Back up the prior file to .bak, then atomic temp + os.replace.
try:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if existed:
        Path(str(config_path) + ".bak").write_text(existing, encoding="utf-8")
    if existing.strip():
        new_text = existing.rstrip("\n") + "\n\n" + managed_block
    else:
        new_text = managed_block
    fd, tmp_name = tempfile.mkstemp(
        dir=str(config_path.parent), prefix=".config.toml.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(new_text)
        os.replace(tmp_name, config_path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
except (OSError, UnicodeError):
    print("writeerror")
    raise SystemExit(0)

print("merged")
raise SystemExit(0)
PY
)"
  merge_rc=$?
  if [ "$merge_rc" -ne 0 ]; then
    merge_status="crash"
  fi
  case "$merge_status" in
    merged)
      ok "merged native [shell_environment_policy] inherit=\"core\" into $config_path (backup: $config_path.bak); Codex now drops loader env vars (LD_PRELOAD/NODE_OPTIONS/PYTHONPATH/...) before spawning the wrapper launchers"
      ;;
    already-managed)
      ok "native [shell_environment_policy] fragment already present (managed) in $config_path; no change"
      ;;
    user-policy)
      warn "$config_path already defines its own [shell_environment_policy]; leaving it untouched. For loader-env hardening set inherit=\"core\" (or add exclude=[\"LD_*\",\"DYLD_*\",\"NODE_OPTIONS\",\"PYTHON*\",...]); see migration/config-fragment.recommended.toml"
      ;;
    malformed)
      warn "$config_path is not valid TOML; skipped the [shell_environment_policy] merge (fix the file, then re-run --install). The launcher's own env scrub still applies"
      ;;
    unreadable)
      warn "could not read $config_path to merge the [shell_environment_policy] fragment; skipped (the launcher's own env scrub still applies)"
      ;;
    writeerror)
      warn "could not write the [shell_environment_policy] fragment to $config_path; skipped (the launcher's own env scrub still applies)"
      ;;
    *)
      warn "the [shell_environment_policy] merge did not complete for $config_path; skipped (the launcher's own env scrub still applies)"
      ;;
  esac
}

# SEC-3 config-layer remediation (R2, task-2b-brief.md; resolves the
# task-2-report.md STATUS=NEEDS_CONTEXT R2/R3 blocker). The installed profile
# (above) protects THIS session's own exec targets, but Codex composes config
# in LAYERS and permission profiles do not compose with the older sandbox
# settings: a TRUSTED project's own .codex/config.toml can still set a legacy
# sandbox_mode key, which makes Codex use that legacy sandbox for the project
# instead of default_permissions -- overriding the triad_leader exec-target
# denies above for that project. Codex reads requirements.toml -- the Tier-1
# config source that outranks every project-local/per-user layer -- ONLY from
# /etc/codex/ (root-owned), an org-managed cloud config bundle, or macOS MDM;
# NEVER from $CODEX_HOME (a per-user path bootstrap could write unprivileged).
# A copy written there would be silently inert (Codex never loads it) while
# looking like a closed gap -- so bootstrap ships a first-party recommended
# file (migration/requirements.recommended.toml) for a root/admin to install
# and only WARNs here, pointing at it; it never writes to /etc/codex itself
# (that needs root, which bootstrap does not have and must not assume).
# Gated on want_codex_profile() (the artifact only makes sense once the
# triad_leader profile it references is installed) AND on errors -eq 0:
# install_codex_runtime_profile can itself fail (bad profile name/policy,
# vendor-binary resolution failure, a write error) without exiting early or
# changing MODE, and this warning's text asserts "the installed profile ...
# protects ..." -- true only when the profile install actually succeeded.
warn_requirements_remediation() {
  if ! want_codex_profile; then
    return
  fi
  if [ "$errors" -ne 0 ]; then
    return
  fi
  requirements_artifact="$REPO_ROOT/migration/requirements.recommended.toml"
  if [ -f "$requirements_artifact" ]; then
    warn "the installed profile (default_permissions=\"triad_leader\") protects this session's own exec targets, but a TRUSTED project's own .codex/config.toml with a legacy sandbox_mode key disables permission profiles for that project, which can override the exec-target denies above; to ENFORCE the permission-profile model machine-wide (block that legacy-sandbox opt-out -- the per-machine deny BODY stays in this per-user profile; Codex >= 0.138.0 required), a root/admin installs the shipped remediation. Do NOT overwrite an existing /etc/codex/requirements.toml (it may carry unrelated org constraints): sudo cp -n \"$requirements_artifact\" /etc/codex/requirements.toml (the -n refuses to clobber; if it already exists, MERGE default_permissions + [allowed_permission_profiles].triad_leader into it by hand)"
    warn "non-root partial mitigation (per sensitive project, no root needed): add [projects.\"<abs-path>\"] trust_level = \"untrusted\" to ~/.codex/config.toml to stop that project's own .codex/ config layer from loading"
    # The env-boundary hardening ([shell_environment_policy] inherit="core") is
    # no longer a WARN here: merge_codex_config_fragment now MERGES it natively
    # into $CODEX_HOME/config.toml on --install (see that function). The
    # /etc/codex + existing-profile-user variants stay documented in the shipped
    # migration/requirements.recommended.toml + migration/config-fragment.recommended.toml.
  else
    warn "shipped requirements.toml remediation artifact missing: $requirements_artifact (reinstall or update the toolkit to restore it)"
  fi
}

install_codex_rules() {
  if ! want_codex_rules; then
    return
  fi

  codex_home="$CODEX_HOME"
  rules_output="$(mktemp "${TMPDIR:-/tmp}/triad-codex-rules.XXXXXX")" || {
    fail "could not create temporary file for Codex rules install"
    return
  }
  rules_err="$(mktemp "${TMPDIR:-/tmp}/triad-codex-rules-err.XXXXXX")" || {
    fail "could not create temporary file for Codex rules stderr"
    rm -f "$rules_output"
    return
  }
if ! python3 - "$codex_home" "$CODEX_RULES_NAME" "$REPO_ROOT" "$LAUNCHER_DIR" >"$rules_output" 2>"$rules_err" <<'PY'
from pathlib import Path
import shlex
import sys

MARKER = "# triad-codex-dispatch managed command rules"
WRAPPERS = (
    ("claude_wrapper.py", "Claude wrapper"),
    ("antigravity_wrapper.py", "Antigravity wrapper"),
    ("gemini_wrapper.py", "Gemini business-tier wrapper"),
)

codex_home_raw, rules_name, repo_root_raw, launcher_dir_raw = sys.argv[1:]
if not rules_name.endswith(".rules") or "/" in rules_name or "\\" in rules_name:
    print(f"invalid TRIAD_CODEX_RULES_NAME: {rules_name!r}")
    raise SystemExit(1)

codex_home = Path(codex_home_raw).expanduser()
rules_dir = codex_home / "rules"
rules_path = rules_dir / rules_name
repo_root = Path(repo_root_raw)
launcher_dir = Path(launcher_dir_raw)

def starlark_string(value: object) -> str:
    text = str(value)
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'

def starlark_list(values: list[str]) -> str:
    return "[" + ", ".join(starlark_string(value) for value in values) + "]"

def command_example(*args: object) -> str:
    return " ".join(shlex.quote(str(arg)) for arg in args)

def unique(values):
    result = []
    seen = set()
    for value in values:
        text = str(value)
        if text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result

rules_dir.mkdir(parents=True, exist_ok=True)
if rules_path.exists():
    existing = rules_path.read_text(encoding="utf-8")
    if MARKER not in existing:
        print(f"refusing to overwrite unmanaged Codex rules file: {rules_path}")
        raise SystemExit(1)

lines = [
    MARKER,
    "# Generated by scripts/bootstrap.sh --install.",
    "# Re-run with TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 to refresh.",
    "# These rules intentionally allow wrapper-specific command prefixes only.",
    "# They do not allow broad shell entrypoints such as bash -lc or zsh -lc.",
    "",
]

for wrapper, label in WRAPPERS:
    launcher_path = launcher_dir / wrapper
    repo_path = repo_root / "bin" / wrapper
    prompt_path = repo_root / "_runs" / "prompts" / "triad-prompt.txt"
    wrapper_paths = unique([str(launcher_path)])

    lines.extend([
        "prefix_rule(",
        f"    pattern = [{starlark_list(wrapper_paths)}],",
        '    decision = "allow",',
        f'    justification = "Allow authenticated triad {label} commands outside the sandbox.",',
        "    match = [",
        f"        {starlark_string(command_example(launcher_path, '--prompt', 'hi', '--sandbox', 'read-only'))},",
        f"        {starlark_string(command_example(launcher_path, '--prompt-file', prompt_path, '--sandbox', 'read-only'))},",
        "    ],",
        "    not_match = [",
        f"        {starlark_string(wrapper + ' --prompt hi --sandbox read-only')},",
        f"        {starlark_string(command_example(repo_path, '--prompt', 'hi', '--sandbox', 'read-only'))},",
        f"        {starlark_string('bash -lc ' + wrapper + ' --prompt hi')},",
        f"        {starlark_string('zsh -lc ' + wrapper + ' --prompt hi')},",
        f"        {starlark_string(command_example('python3', repo_path, '--prompt', 'hi', '--sandbox', 'read-only'))},",
        f"        {starlark_string(command_example('/usr/bin/env', 'python3', repo_path, '--prompt', 'hi', '--sandbox', 'read-only'))},",
        '        "python3 -c print(\'not a triad wrapper\')",',
        "    ],",
        ")",
        "",
    ])

rules_path.write_text("\n".join(lines), encoding="utf-8")
print(rules_path)
PY
  then
    rules_fail_output="$(
      cat "$rules_output"
      cat "$rules_err"
    )"
    while IFS= read -r line; do
      [ -n "$line" ] && fail "$line"
    done <<EOF
$rules_fail_output
EOF
    rm -f "$rules_output" "$rules_err"
    return
  fi
  if [ -s "$rules_err" ]; then
    while IFS= read -r line; do
      [ -n "$line" ] && warn "$line"
    done <"$rules_err"
  fi
  installed="$(sed -n '1p' "$rules_output")"
  rm -f "$rules_output" "$rules_err"
  ok "Codex command rules installed: $installed"
}

# Strips the managed codex-triad block (markers inclusive) from a shell RC
# file. Used for both idempotent refresh (--install) and uninstall (--remove).
strip_managed_shell_entry() {
  python3 - "$1" "$SHELL_ENTRY_BEGIN" "$SHELL_ENTRY_END" <<'PY'
from pathlib import Path
import sys

path, begin, end = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
kept = []
skipping = False
for line in lines:
    stripped = line.rstrip("\n")
    if stripped == begin:
        skipping = True
        continue
    if stripped == end:
        skipping = False
        continue
    if not skipping:
        kept.append(line)
path.write_text("".join(kept), encoding="utf-8")
PY
}

# MUST-land 6: the managed codex-triad shell function is the pinned no-prompt
# entry. It pins the engine's product-mode envs so no-prompt dispatch always
# runs with wrapper containment + hardened wrapper mode + enforced claude
# sandbox. A bare `codex --profile ...` start is NOT a supported no-prompt
# path and is never emitted by this bootstrap as the primary start.
install_shell_entry() {
  if [ "${TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY:-0}" != "1" ]; then
    return
  fi
  rc_file="$SHELL_RC"
  rc_dir="$(dirname -- "$rc_file")"
  mkdir -p "$rc_dir" || {
    fail "could not create shell RC directory: $rc_dir"
    return
  }
  if [ -e "$rc_file" ] && grep -Fq "$SHELL_ENTRY_BEGIN" "$rc_file" 2>/dev/null; then
    strip_managed_shell_entry "$rc_file" || {
      fail "could not refresh managed codex-triad shell entry in $rc_file"
      return
    }
  elif [ -e "$rc_file" ] && grep -q "codex-triad" "$rc_file" 2>/dev/null; then
    fail "refusing to modify unmanaged codex-triad shell entry in $rc_file; remove it manually, then re-run --install"
    return
  fi
  {
    printf '%s\n' "$SHELL_ENTRY_BEGIN"
    printf '# Managed by triad-codex-dispatch scripts/bootstrap.sh --install;\n'
    printf '# removed by --remove. Pinned no-prompt posture: wrapper root\n'
    printf '# containment + hardened wrapper mode + enforced claude sandbox.\n'
    printf 'codex-triad() {\n'
    printf '  TRIAD_WRAPPER_ALLOWED_ROOTS="${TRIAD_WRAPPER_ALLOWED_ROOTS:-$PWD}" \\\n'
    printf '  TRIAD_WRAPPER_HARDENED=1 \\\n'
    printf '  TRIAD_CLAUDE_ENFORCE_SANDBOX=1 \\\n'
    printf '    command codex --profile %s --search "$@"\n' "$CODEX_PROFILE_NAME"
    printf '}\n'
    printf '%s\n' "$SHELL_ENTRY_END"
  } >>"$rc_file" || {
    fail "could not append codex-triad shell entry to $rc_file"
    return
  }
  ok "codex-triad shell entry installed: $rc_file"
}

report_no_prompt_posture() {
  posture="TRIAD_WRAPPER_ALLOWED_ROOTS (workspace pin) + TRIAD_WRAPPER_HARDENED=1 + TRIAD_CLAUDE_ENFORCE_SANDBOX=1"
  if [ -e "$SHELL_RC" ] && grep -q "codex-triad()" "$SHELL_RC" 2>/dev/null; then
    if grep -q "TRIAD_WRAPPER_HARDENED=1" "$SHELL_RC" 2>/dev/null \
      && grep -q "TRIAD_CLAUDE_ENFORCE_SANDBOX=1" "$SHELL_RC" 2>/dev/null \
      && grep -q "TRIAD_WRAPPER_ALLOWED_ROOTS" "$SHELL_RC" 2>/dev/null; then
      ok "no-prompt entry verified: codex-triad pins $posture ($SHELL_RC)"
    else
      warn "codex-triad entry in $SHELL_RC does not pin the product-mode envs ($posture); remove the stale entry, then re-run --install with TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1"
    fi
  else
    printf 'next step: start Codex through the codex-triad shell function; it pins %s.\n' "$posture"
    printf 'install it with TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY=1; a bare profile start is not a supported no-prompt path.\n'
  fi
}

expand_user_path() {
  python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).expanduser())' "$1"
}

# remove_codex_config_fragment — symmetric to merge_codex_config_fragment.
# Strips exactly OUR marker-delimited [shell_environment_policy] block from
# $CODEX_HOME/config.toml (keyed on CONFIG_FRAGMENT_BEGIN/END), leaving every
# other key untouched. If stripping the block leaves the file effectively empty
# (i.e. --install had CREATED config.toml solely for the fragment), the file is
# removed to restore the pre-install absent state. Our marker absent -> silent
# no-op (config.toml is a SHARED file; a user's own [shell_environment_policy]
# without our marker is left in place). NON-fatal: any read/write error WARNs.
remove_codex_config_fragment() {
  config_path="$CODEX_HOME/config.toml"
  remove_status="$(python3 - "$config_path" "$CONFIG_FRAGMENT_BEGIN" "$CONFIG_FRAGMENT_END" <<'PY'
import os
import sys
import tempfile
from pathlib import Path

config_path = Path(sys.argv[1])
begin = sys.argv[2]
end = sys.argv[3]

try:
    text = config_path.read_text(encoding="utf-8")
except FileNotFoundError:
    print("absent")
    raise SystemExit(0)
except (OSError, UnicodeDecodeError):
    print("unreadable")
    raise SystemExit(0)

if begin not in text:
    # No managed block of ours -> leave a user-authored file untouched.
    print("not-managed")
    raise SystemExit(0)

kept = []
skipping = False
for line in text.splitlines(keepends=True):
    stripped = line.rstrip("\n")
    if stripped == begin:
        skipping = True
        continue
    if stripped == end:
        skipping = False
        continue
    if not skipping:
        kept.append(line)

remainder = "".join(kept)
try:
    if remainder.strip() == "":
        # config.toml existed only for our fragment -> restore absent state.
        config_path.unlink()
        print("removed-file")
        raise SystemExit(0)
    remainder = remainder.rstrip("\n") + "\n"
    fd, tmp_name = tempfile.mkstemp(
        dir=str(config_path.parent), prefix=".config.toml.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(remainder)
        os.replace(tmp_name, config_path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
except (OSError, UnicodeError):
    print("writeerror")
    raise SystemExit(0)

print("removed")
raise SystemExit(0)
PY
)"
  remove_rc=$?
  if [ "$remove_rc" -ne 0 ]; then
    remove_status="crash"
  fi
  case "$remove_status" in
    removed | removed-file)
      ok "removed managed [shell_environment_policy] fragment from $config_path"
      ;;
    absent | not-managed)
      : # nothing of ours to remove; stay silent (config.toml is a shared file)
      ;;
    unreadable | writeerror)
      warn "could not remove the managed [shell_environment_policy] fragment from $config_path"
      ;;
    *)
      warn "could not remove the managed [shell_environment_policy] fragment from $config_path"
      ;;
  esac
}

run_remove() {
  if ! command -v python3 >/dev/null 2>&1; then
    fail "missing required binary: python3"
    return
  fi
  LAUNCHER_DIR="$(expand_user_path "$RAW_LAUNCHER_DIR")"
  CODEX_HOME="$(expand_user_path "$RAW_CODEX_HOME")"
  CLASSIFIER_PATH="$(expand_user_path "$RAW_CLASSIFIER_PATH")"

  if [ -e "$SHELL_RC" ] && grep -Fq "$SHELL_ENTRY_BEGIN" "$SHELL_RC" 2>/dev/null; then
    if strip_managed_shell_entry "$SHELL_RC"; then
      ok "removed managed codex-triad shell entry from $SHELL_RC"
    else
      fail "could not remove managed codex-triad shell entry from $SHELL_RC"
    fi
  elif [ -e "$SHELL_RC" ] && grep -q "codex-triad" "$SHELL_RC" 2>/dev/null; then
    warn "leaving unmanaged codex-triad entry in place: $SHELL_RC (not installed by bootstrap)"
  else
    ok "no codex-triad shell entry to remove: $SHELL_RC"
  fi

  for wrapper in claude_wrapper.py gemini_wrapper.py antigravity_wrapper.py; do
    launcher="$LAUNCHER_DIR/$wrapper"
    if [ ! -e "$launcher" ]; then
      continue
    fi
    if launcher_is_managed "$launcher" "$wrapper"; then
      if rm -f "$launcher"; then
        ok "removed launcher: $launcher"
      else
        fail "could not remove launcher: $launcher"
      fi
    else
      warn "leaving unmanaged launcher in place: $launcher"
    fi
  done

  for name in claude-wrapper-repair gemini-wrapper-repair agy-wrapper-repair; do
    agent_file="$CODEX_HOME/agents/$name.toml"
    if [ -L "$agent_file" ]; then
      warn "leaving legacy repair-agent symlink in place (never following a symlink target): $agent_file"
      continue
    fi
    if [ ! -e "$agent_file" ]; then
      continue
    fi
    if ! repair_agent_is_managed "$agent_file"; then
      warn "preserving unmanaged repair agent: $agent_file"
      continue
    fi
    if rm -f "$agent_file"; then
      ok "removed managed repair agent: $agent_file"
    else
      fail "could not remove repair agent: $agent_file"
    fi
  done

  profile_path="$CODEX_HOME/$CODEX_PROFILE_NAME.config.toml"
  if [ -e "$profile_path" ]; then
    if grep -Fq "# triad-codex-dispatch managed runtime profile" "$profile_path" 2>/dev/null; then
      if rm -f "$profile_path"; then
        ok "removed Codex runtime profile: $profile_path"
      else
        fail "could not remove Codex runtime profile: $profile_path"
      fi
    else
      warn "leaving unmanaged Codex profile in place: $profile_path"
    fi
  fi

  remove_codex_config_fragment

  # C5 (symmetric to warn_requirements_remediation on --install): a root/admin
  # may have installed the shipped /etc/codex/requirements.toml remediation,
  # which names triad_leader as default_permissions + the sole allowed profile.
  # Removing the per-user triad_leader profile above leaves that root file
  # pointing at a now-absent profile (a machine-wide dangling reference). We
  # NEVER touch /etc/codex (root-owned) -- read-only WARN, naming the exact
  # file. Path overridable (test seam / non-standard system-config roots);
  # default is the documented Codex Tier-1 location.
  etc_requirements="${TRIAD_CODEX_REQUIREMENTS_PATH:-/etc/codex/requirements.toml}"
  # -f (regular file only): a FIFO/device at this path could block the grep read;
  # a non-regular file is not our remediation artifact, so skip it.
  if [ -f "$etc_requirements" ]; then
    if [ -r "$etc_requirements" ]; then
      # `--` ends grep options so a path that begins with '-' (an operator-set
      # TRIAD_CODEX_REQUIREMENTS_PATH override) is treated as a filename, not a flag.
      if grep -Fq -- "triad_leader" "$etc_requirements" 2>/dev/null; then
        warn "$etc_requirements still references triad_leader after the per-user profile was removed. Review it: adjust the triad-specific keys (default_permissions and the triad_leader entry in [allowed_permission_profiles]) so it does not select an absent profile, while preserving unrelated org constraints. (If the admin centrally copied the [permissions.triad_leader] body into that file, the selection may still be valid -- confirm before changing.)"
      fi
    else
      warn "$etc_requirements exists but is not readable here; if a root/admin installed the triad_leader remediation there, review it now that the per-user profile is removed -- adjust the triad-specific keys, preserving unrelated constraints"
    fi
  fi

  rules_path="$CODEX_HOME/rules/$CODEX_RULES_NAME"
  if [ -e "$rules_path" ]; then
    if grep -Fq "# triad-codex-dispatch managed command rules" "$rules_path" 2>/dev/null; then
      if rm -f "$rules_path"; then
        ok "removed Codex command rules: $rules_path"
      else
        fail "could not remove Codex command rules: $rules_path"
      fi
    else
      warn "leaving unmanaged Codex rules file in place: $rules_path"
    fi
  fi

  if [ -e "$CLASSIFIER_PATH" ]; then
    ok "classifier patches preserved (learned classifications): $CLASSIFIER_PATH — remove manually to reset"
  fi
}

ensure_classifier() {
  dir="$(dirname -- "$CLASSIFIER_PATH")"
  mkdir -p "$dir" || {
    fail "could not create classifier directory: $dir"
    return
  }
  if [ ! -e "$CLASSIFIER_PATH" ]; then
    printf '{}\n' >"$CLASSIFIER_PATH" || {
      fail "could not create classifier file: $CLASSIFIER_PATH"
      return
    }
  fi
  if [ ! -w "$CLASSIFIER_PATH" ]; then
    fail "classifier file is not writable: $CLASSIFIER_PATH"
    return
  fi
  if python3 - "$CLASSIFIER_PATH" <<'PY'
import json
import sys
with open(sys.argv[1], encoding="utf-8") as fh:
    json.load(fh)
PY
  then
    ok "classifier file is writable JSON: $CLASSIFIER_PATH"
  else
    fail "classifier file is not valid JSON: $CLASSIFIER_PATH"
  fi
}

if [ "$CHECK_ALIAS_USED" -eq 1 ]; then
  warn "--check is deprecated; use --install (--check remains an alias for one release)"
fi

if [ "$MODE" = "remove" ]; then
  printf 'triad-codex-dispatch bootstrap remove\n'
  run_remove
  if [ "$errors" -eq 0 ]; then
    ok "bootstrap remove completed"
    exit 0
  fi
  printf '[error] bootstrap remove failed with %s issue(s)\n' "$errors" >&2
  exit 1
fi

printf 'triad-codex-dispatch bootstrap install\n'
check_binary codex
check_binary claude
check_binary agy
if [ "${TRIAD_BOOTSTRAP_REQUIRE_GEMINI:-0}" = "1" ]; then
  check_binary gemini
else
  check_optional_binary gemini
fi
check_python
check_binary jq
check_claude_version
if [ "$errors" -eq 0 ]; then
  canonicalize_path_inputs
fi
if [ "$errors" -eq 0 ]; then
  check_workspace_escape
fi
printf 'repo root: %s\n' "$REPO_ROOT"
printf 'reminder: trust this workspace in Codex before relying on project-local skills.\n'
if [ "$errors" -ne 0 ]; then
  fail "required prerequisite checks failed; skipping installation steps"
  exit 1
fi
if want_codex_profile \
  && [ "$CODEX_PROFILE_APPROVAL_POLICY" = "never" ] \
  && ! want_codex_rules; then
  warn "approval_policy=never with the command rules opted out can auto-deny sandbox escapes; keep the default rules install for no-prompt dispatch"
fi
check_legacy_sandbox_config
# R2 (SEC-2) BEFORE R1 (DIST-1): the SEC-framed confused-deputy warning must
# not be drowned by / duplicated with the plain hygiene warning, and R1's
# de-dup depends on SEC2_FLAGGED_SELECTORS, which only R2 populates.
check_local_writable_agent_residual
check_duplicate_selectors
migrate_legacy_repair_agents
install_launchers
ensure_log_dir
ensure_classifier
install_codex_runtime_profile
merge_codex_config_fragment
warn_requirements_remediation
install_codex_rules
install_shell_entry
check_auth
report_no_prompt_posture

if [ "$errors" -eq 0 ]; then
  ok "bootstrap install passed"
  exit 0
fi

fail_count="$errors"
printf '[error] bootstrap install failed with %s issue(s)\n' "$fail_count" >&2
exit 1
