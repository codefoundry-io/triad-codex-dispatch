#!/usr/bin/env bash
# Constructed-launcher trust invariant: the launcher, its pinned Python runtime,
# and the checkout wrapper it executes must remain outside the mutable project
# worktree. Bootstrap installs no persistent permission policy; the AGY wrapper
# selects its approved native headless child mode internally at dispatch time.
set -u

usage() {
  cat <<'EOF'
Usage: scripts/bootstrap.sh --install
       scripts/bootstrap.sh --remove

--install checks local prerequisites for triad-codex-dispatch, removes exact
plugin-owned repair and permission artifacts from older installs, and installs
the provider launcher group. Applying a validated proposal remains an explicit
owner action through the bootstrap-printed login-shell Python argv (see
docs/references/repair-protocol.md).
It also quarantines any legacy personal-scope
repair-agent TOMLs (bootstrap-authored provenance only — a same-name file
without that provenance is left in place) left by an older install into a
timestamped directory outside agents/, recoverable if needed.

--remove uninstalls managed wrapper launchers and exact legacy plugin-owned
profile, command-rule, config-fragment, shell-entry, and repair artifacts. It
preserves owner-authored or edited artifacts and refuses unsafe targets without
following or changing them. It
also removes any bootstrap-managed (provenance-matched) legacy personal-scope
repair-agent TOMLs left by an older install; a non-matching same-name file is
preserved. Learned classifier patches are preserved.

Assumes codex and claude, plus agy, or configured Gemini Enterprise/Business,
Vertex, or API-key routing, are already installed.

Install targets must resolve outside the project worktree. Run TRIAD from the
same authenticated login terminal and worktree used for development. TRIAD
does not install or inject a separate Codex profile, command rule, shell
environment policy, shell entry, or permission requirement. The Codex-led AGY
wrapper deliberately selects AGY native headless always-proceed for that child
through its internal --dangerously-skip-permissions flag; callers do not pass
the flag, and this does not change stored or global user/project settings.
Wrapper descendants remain scrubbed after trusted launcher and interpreter
startup.

Start a fresh ordinary Codex session after installation so the updated native
repair protocol loads.
EOF
}

MODE=""
if [ "$#" -ne 1 ]; then
  usage >&2
  exit 2
fi
case "${1:-}" in
  --install)
    MODE="install"
    ;;
  --remove)
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
CODEX_PROFILE_NAME="${TRIAD_CODEX_PROFILE_NAME:-triad-codex-dispatch}"
CODEX_RULES_NAME="${TRIAD_CODEX_RULES_NAME:-triad-codex-dispatch.rules}"
REPAIR_ANALYZER_NAME="triad-repair-analyzer"
APPLY_REPAIR_LAUNCHER="triad-apply-repair"
SHELL_RC="${TRIAD_BOOTSTRAP_SHELL_RC:-}"
if [ -z "$SHELL_RC" ]; then
  case "${SHELL:-}" in
    */zsh) SHELL_RC="$HOME/.zshrc" ;;
    *) SHELL_RC="$HOME/.bashrc" ;;
  esac
fi

errors=0
# Exact-line set used to de-duplicate selector safety warnings under Bash 3.2.
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

validate_codex_profile_name() {
  case "$CODEX_PROFILE_NAME" in
    ""|[!0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz]*|*[!0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz._-]*)
      fail "invalid TRIAD_CODEX_PROFILE_NAME: must match [A-Za-z0-9][A-Za-z0-9._-]*"
      return 1
      ;;
  esac
  return 0
}

validate_codex_rules_name() {
  case "$CODEX_RULES_NAME" in
    *.rules)
      case "$CODEX_RULES_NAME" in
        */*|*\\*) ;;
        *) return 0 ;;
      esac
      ;;
  esac
  fail "invalid TRIAD_CODEX_RULES_NAME: must be a basename ending in .rules"
  return 1
}

validate_bootstrap_inputs() {
  validation_failed=0
  validate_codex_profile_name || validation_failed=1
  validate_codex_rules_name || validation_failed=1
  return "$validation_failed"
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
  if [ -L "$launcher" ]; then
    return 1
  fi
  if [ ! -e "$launcher" ]; then
    return 0
  fi
  if [ ! -f "$launcher" ]; then
    return 1
  fi
  python3 "$REPO_ROOT/bin/bootstrap_repair.py" command-owned \
    --kind launcher --name "$wrapper" --path "$launcher" >/dev/null
}

COMMAND_MANIFEST=""

begin_command_group() {
  COMMAND_MANIFEST="$(mktemp "${TMPDIR:-/tmp}/triad-command-group.XXXXXX")" || {
    fail "could not create command transaction manifest"
    return 1
  }
}

queue_command_artifact() {
  name="$1"
  kind="$2"
  target="$3"
  payload="$4"
  if ! python3 - "$name" "$kind" "$target" "$payload" >>"$COMMAND_MANIFEST" <<'PY'
import json
import sys

print(json.dumps({
    "name": sys.argv[1],
    "kind": sys.argv[2],
    "target": sys.argv[3],
    "data_path": sys.argv[4],
    "mode": 0o755,
}, ensure_ascii=False))
PY
  then
    rm -f "$payload"
    fail "could not queue managed command: $target"
    return 1
  fi
}

queue_command_removal() {
  name="$1"
  kind="$2"
  target="$3"
  if ! python3 - "$name" "$kind" "$target" >>"$COMMAND_MANIFEST" <<'PY'
import json
import sys

print(json.dumps({
    "name": sys.argv[1],
    "kind": sys.argv[2],
    "target": sys.argv[3],
    "mode": 0o755,
}, ensure_ascii=False))
PY
  then
    fail "could not queue managed command removal: $target"
    return 1
  fi
}

publish_command_group() {
  [ -n "$COMMAND_MANIFEST" ] || return 0
  if ! python3 "$REPO_ROOT/bin/bootstrap_repair.py" commands-install --manifest "$COMMAND_MANIFEST"; then
    fail "could not install managed command group"
  else
    ok "managed command group installed"
  fi
  python3 - "$COMMAND_MANIFEST" <<'PY'
import json
from pathlib import Path
import os
import stat
import sys

for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    try:
        payload = Path(json.loads(line)["data_path"])
        payload.unlink(missing_ok=True)
    except (KeyError, OSError, ValueError, json.JSONDecodeError):
        pass
PY
  rm -f "$COMMAND_MANIFEST"
  COMMAND_MANIFEST=""
}

remove_command_group() {
  [ -n "$COMMAND_MANIFEST" ] || return 0
  if [ ! -s "$COMMAND_MANIFEST" ]; then
    rm -f "$COMMAND_MANIFEST"
    COMMAND_MANIFEST=""
    return 0
  fi
  if ! python3 "$REPO_ROOT/bin/bootstrap_repair.py" commands-remove \
    --manifest "$COMMAND_MANIFEST" \
    --preserve-foreign \
    --test-fail-at "${TRIAD_BOOTSTRAP_TEST_FAIL_COMMAND_REMOVE_AT:-}"; then
    fail "could not remove managed command group"
    rm -f "$COMMAND_MANIFEST"
    COMMAND_MANIFEST=""
    return 1
  else
    ok "managed command group removed"
  fi
  rm -f "$COMMAND_MANIFEST"
  COMMAND_MANIFEST=""
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

run_repair_lifecycle() {
  action="$1"
  python3 "$REPO_ROOT/bin/bootstrap_repair.py" "$action" \
    --config "$CODEX_HOME/config.toml" \
    --analyzer "$CODEX_HOME/agents/$REPAIR_ANALYZER_NAME.toml" \
    --launcher "$LAUNCHER_DIR/$APPLY_REPAIR_LAUNCHER"
  if [ "$?" -eq 0 ]; then
    ok "repair artifacts $action completed"
    return 0
  fi
  fail "repair artifact $action failed"
  return 1
}

print_owner_apply_argv() {
  python3 - "$REPO_ROOT" "$CLASSIFIER_PATH" <<'PY'
from pathlib import Path
import shlex
import sys

toolkit_root = Path(sys.argv[1])
classifier_path = sys.argv[2]
inner = [
    "python3",
    str(toolkit_root / "bin" / "apply_patch.py"),
    "--cli",
    "<cli>",
    "--classifier-file",
    classifier_path,
    "--proposal-file",
    "<absolute-proposal-path>",
]
owner_argv = ["/bin/zsh", "-lic", shlex.join(inner)]
print("owner apply argv: " + shlex.join(owner_argv))
PY
}

remove_owned_artifact() {
  owned_kind="$1"
  owned_path="$2"
  removed_message="$3"
  unmanaged_message="$4"
  owned_status="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" managed-remove \
    --kind "$owned_kind" --path "$owned_path")"
  if [ "$?" -ne 0 ]; then
    fail "could not safely remove managed artifact: $owned_path"
    return 1
  fi
  case "$owned_status" in
    absent)
      return 0
      ;;
    unmanaged)
      warn "$unmanaged_message"
      return 0
      ;;
    removed)
      ok "$removed_message"
      return 0
      ;;
    *)
      fail "unexpected managed removal status for $owned_path: $owned_status"
      return 1
      ;;
  esac
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

GOOGLE_ROUTE=""
check_google_route() {
  if command -v agy >/dev/null 2>&1; then
    GOOGLE_ROUTE="agy"
    ok "found Google route: agy"
  elif command -v gemini >/dev/null 2>&1; then
    GOOGLE_ROUTE="gemini"
    warn "found Gemini fallback candidate: executable presence only; configured route must be proven in the owner's authenticated terminal"
  else
    fail "missing Google route: agy or gemini"
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

check_workspace_escape() {
  workspace_guard_output="$(python3 - "$PWD" "$LAUNCHER_DIR" "$CODEX_HOME" "$(dirname -- "$CLASSIFIER_PATH")" "$REPO_ROOT" <<'PY'
from pathlib import Path
import os
import sys

pwd_raw, launcher_raw, codex_home_raw, classifier_dir_raw, repo_root_raw = sys.argv[1:]
workspace = Path(pwd_raw).resolve()


def _fs_case_insensitive(probe):
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
    fail "invariant: the constructed-launcher trust boundary requires launchers and everything they exec to live outside all sandbox-writable roots; run bootstrap from a directory that does not contain the install targets, or point the TRIAD_BOOTSTRAP_* / CODEX_HOME overrides outside this workspace"
  fi
}

# Read enabled triad plugin selectors through TOML, never line parsing.
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

# Classify cached write-capable legacy repair agents without glob error suppression.
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
# with the duplicate-selector preflight, canonicalized CODEX_HOME, using the
# shared read_plugin_selectors tomllib reader.
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
# ever calls warn, never fail; mutates nothing). Co-located with the local
# write-capable-agent residual check, canonicalized CODEX_HOME, using the
# shared read_plugin_selectors tomllib reader. Counts ENABLED
# `triad-codex-dispatch@*` plugin selectors in
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
# halts --install: a quarantine-dir-create or transaction failure just warns and
# continues to the next name. Called AFTER the errors!=0 -> exit 1 preflight
# gate and retained read-only preflights, BEFORE install_launchers.
migrate_legacy_repair_agents() {
  for name in claude-wrapper-repair gemini-wrapper-repair agy-wrapper-repair; do
    agent_file="$CODEX_HOME/agents/$name.toml"
    if quarantine_status="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" managed-quarantine \
      --kind legacy-agent --path "$agent_file" --quarantine-parent "$CODEX_HOME" \
      2>/dev/null)"; then
      case "$quarantine_status" in
        quarantined)
          warn "quarantined legacy repair agent: $agent_file"
          ;;
        absent)
          ;;
        unmanaged)
          warn "leaving unmanaged repair agent in place: $agent_file"
          ;;
        *)
          warn "unexpected legacy repair-agent quarantine status for $agent_file: $quarantine_status"
          ;;
      esac
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

resolve_python_runtime() {
  python_exe="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" runtime-path)" || {
    fail "could not resolve a portable Python runtime for launchers"
    return
  }
  escaped_python="$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$python_exe")" || {
    fail "could not quote launcher Python runtime"
    return
  }
  escaped_classifier="$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$CLASSIFIER_PATH")" || {
    fail "could not quote classifier path for launchers"
    return
  }
}

check_formal_schema_dependency() {
  if python3 "$REPO_ROOT/bin/bootstrap_repair.py" formal-schema-ready \
    --requirements "$REPO_ROOT/requirements.txt"; then
    ok "Pydantic 2 formal review APIs available"
  else
    fail "formal review dependency readiness failed"
  fi
}

preflight_install_command_targets() {
  command_preflight_failed=0
  for wrapper in claude_wrapper.py gemini_wrapper.py antigravity_wrapper.py; do
    launcher="$LAUNCHER_DIR/$wrapper"
    if [ -L "$launcher" ]; then
      fail "refusing to overwrite symlinked launcher: $launcher"
      command_preflight_failed=1
    elif ! launcher_is_managed "$launcher" "$wrapper"; then
      fail "refusing to overwrite unmanaged launcher: $launcher"
      command_preflight_failed=1
    fi
  done
  [ "$command_preflight_failed" -eq 0 ]
}

install_launchers() {
  repo_bin="$REPO_ROOT/bin"
  if [ ! -d "$repo_bin" ]; then
    fail "missing repo bin directory: $repo_bin"
    return
  fi

  if [ -z "${python_exe:-}" ] || [ -z "${escaped_python:-}" ] || [ -z "${escaped_classifier:-}" ]; then
    fail "missing preflighted Python runtime or classifier path for launchers"
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
    if [ -L "$launcher" ]; then
      fail "refusing to overwrite symlinked launcher: $launcher"
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
    temp_launcher="$(mktemp "${TMPDIR:-/tmp}/triad-${wrapper}.XXXXXX")" || {
      fail "could not create temporary launcher: $launcher"
      continue
    }
    {
      # Constructed launcher environment. The inherited environment is a trust
      # boundary because loader/runtime variables can redirect executable code.
      # The launcher hands the wrapper and vendor a deliberately constructed
      # environment: start from the
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
      #     user-site at workspace sitecustomize.py/usercustomize.py startup code
      #     that runs before line 1.
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
      printf 'env["TRIAD_AUDIT_REDACT_PROMPTS"] = "1"\n'
      # The classifier is install-time state. Pin the canonical absolute path
      # into every provider launcher so a fresh shell cannot silently select a
      # different default or lose a one-shot custom override.
      printf 'env["TRIAD_CLASSIFIER_EXTENSION"] = %s\n' "$escaped_classifier"
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
    } >"$temp_launcher" || {
      rm -f "$temp_launcher"
      fail "could not write launcher: $launcher"
      continue
    }
    if ! chmod 0755 "$temp_launcher"; then
      rm -f "$temp_launcher"
      fail "could not chmod launcher: $launcher"
      continue
    fi
    queue_command_artifact "$wrapper" launcher "$launcher" "$temp_launcher"
  done

  if ! path_has_dir "$LAUNCHER_DIR"; then
    fail "launcher directory is not on PATH: $LAUNCHER_DIR"
    return
  fi

}

verify_installed_launchers() {
  repo_bin="$REPO_ROOT/bin"
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

ensure_log_dir() {
  dir="$REPO_ROOT/bin/_logs"
  mkdir -p "$dir" || {
    fail "could not create runtime log directory: $dir"
    return
  }
  ok "runtime log directory exists: $dir"
}

# Remove the exact current or legacy managed configuration fragment.
# Removes exactly one literal current or legacy managed
# [shell_environment_policy] block from $CODEX_HOME/config.toml. Any edited,
# duplicate, incomplete, or otherwise unrecognized marker state is left
# byte-for-byte untouched. Removal is literal replacement, never a marker-range
# scan or newline-normalizing reserialization. Fragment cleanup preserves any
# owner-authored remainder byte-for-byte and removes a fragment-only config
# directly; it does not defer deletion to the retired repair lifecycle.
remove_codex_config_fragment() {
  if [ "$errors" -ne 0 ]; then
    return
  fi
  config_path="$CODEX_HOME/config.toml"
  remove_err="$(mktemp "${TMPDIR:-/tmp}/triad-config-remove-err.XXXXXX")" || {
    fail "could not create temporary file for config fragment removal stderr"
    return 1
  }
  remove_status="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" config-fragment \
    --action remove --path "$config_path" 2>"$remove_err")"
  remove_rc=$?
  if [ "$remove_rc" -ne 0 ]; then
    fail "config fragment removal helper failed for $config_path"
    while IFS= read -r line; do
      [ -n "$line" ] && printf '[error] %s\n' "$line" >&2
    done <"$remove_err"
    rm -f "$remove_err"
    return 1
  fi
  if [ -s "$remove_err" ]; then
    while IFS= read -r line; do
      [ -n "$line" ] && warn "$line"
    done <"$remove_err"
  fi
  rm -f "$remove_err"
  case "$remove_status" in
    removed | removed-file)
      ok "removed managed [shell_environment_policy] fragment from $config_path"
      ;;
    absent | not-managed)
      : # nothing of ours to remove; stay silent (config.toml is a shared file)
      ;;
    unrecognized-managed | unreadable | writeerror)
      warn "could not remove the managed [shell_environment_policy] fragment from $config_path"
      ;;
    *)
      warn "could not remove the managed [shell_environment_policy] fragment from $config_path"
      ;;
  esac
}

remove_legacy_permission_artifacts() {
  if ! run_repair_lifecycle remove; then
    return 1
  fi

  rules_path="$CODEX_HOME/rules/$CODEX_RULES_NAME"
  if ! remove_owned_artifact \
    rules \
    "$rules_path" \
    "removed Codex command rules: $rules_path" \
    "leaving unmanaged Codex rules file in place: $rules_path"; then
    return 1
  fi

  profile_path="$CODEX_HOME/$CODEX_PROFILE_NAME.config.toml"
  if ! remove_owned_artifact \
    profile \
    "$profile_path" \
    "removed Codex runtime profile: $profile_path" \
    "leaving unmanaged Codex profile in place: $profile_path"; then
    return 1
  fi

  if ! remove_codex_config_fragment; then
    return 1
  fi

  shell_remove_status="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" shell-entry \
    --action remove --path "$SHELL_RC")"
  if [ "$?" -ne 0 ]; then
    fail "could not remove managed codex-triad shell entry from $SHELL_RC"
    return 1
  fi
  case "$shell_remove_status" in
    removed)
      ok "removed managed codex-triad shell entry from $SHELL_RC"
      ;;
    unmanaged)
      warn "leaving unmanaged codex-triad entry in place: $SHELL_RC (not installed by bootstrap)"
      ;;
    absent)
      :
      ;;
    *)
      fail "unexpected codex-triad shell remove status for $SHELL_RC: $shell_remove_status"
      return 1
      ;;
  esac
  return 0
}

run_remove() {
  if ! command -v python3 >/dev/null 2>&1; then
    fail "missing required binary: python3"
    return
  fi
  # Use the same trusted-root spelling as install. Nested paths such as
  # CODEX_HOME/agents remain unresolved and are checked separately, but a
  # stable operator-selected root alias (`/tmp` on macOS or a CODEX_HOME
  # symlink) must not make install succeed and the matching remove fail.
  canonicalize_path_inputs
  if [ "$errors" -ne 0 ]; then
    return
  fi

  # Validate every repair-lifecycle path before uninstall removes any other
  # managed artifact. The transactional remove repeats these checks at commit
  # time; this read-only pass prevents a known-bad target from causing a
  # partial uninstall.
  if ! run_repair_lifecycle preflight-remove; then
    return
  fi

  if ! remove_legacy_permission_artifacts; then
    return
  fi

  if ! begin_command_group; then
    return
  fi
  for wrapper in claude_wrapper.py gemini_wrapper.py antigravity_wrapper.py; do
    launcher="$LAUNCHER_DIR/$wrapper"
    queue_command_removal "$wrapper" launcher "$launcher"
  done
  # Kept only to clean command entries published by older releases.
  for runtime_command in triad-setup triad-doctor; do
    target="$LAUNCHER_DIR/$runtime_command"
    queue_command_removal "$runtime_command" runtime "$target"
  done
  if [ "$errors" -ne 0 ]; then
    rm -f "$COMMAND_MANIFEST"
    COMMAND_MANIFEST=""
    return
  fi
  if ! remove_command_group; then
    return
  fi

  for name in claude-wrapper-repair gemini-wrapper-repair agy-wrapper-repair; do
    agent_file="$CODEX_HOME/agents/$name.toml"
    if [ -L "$agent_file" ]; then
      warn "leaving legacy repair-agent symlink in place (never following a symlink target): $agent_file"
      continue
    fi
    remove_owned_artifact \
      legacy-agent \
      "$agent_file" \
      "removed managed repair agent: $agent_file" \
      "preserving unmanaged repair agent: $agent_file"
  done

  # A root/admin
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

  if [ -e "$CLASSIFIER_PATH" ]; then
    ok "classifier patches preserved (learned classifications): $CLASSIFIER_PATH — remove manually to reset"
  fi
}

preflight_classifier() {
  classifier_status="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" classifier \
    --action preflight --path "$CLASSIFIER_PATH")"
  if [ "$?" -ne 0 ]; then
    while IFS= read -r line; do
      [ -n "$line" ] && fail "$line"
    done <<EOF
$classifier_status
EOF
    return 1
  fi
  case "$classifier_status" in
    absent | ready)
      return 0
      ;;
    *)
      fail "unexpected classifier preflight status for $CLASSIFIER_PATH: $classifier_status"
      return 1
      ;;
  esac
}

ensure_classifier() {
  classifier_err="$(mktemp "${TMPDIR:-/tmp}/triad-classifier-err.XXXXXX")" || {
    fail "could not create temporary file for classifier stderr"
    return 1
  }
  classifier_status="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" classifier \
    --action ensure --path "$CLASSIFIER_PATH" 2>"$classifier_err")"
  classifier_rc=$?
  if [ "$classifier_rc" -ne 0 ]; then
    fail "classifier ensure helper failed for $CLASSIFIER_PATH"
    while IFS= read -r line; do
      [ -n "$line" ] && printf '[error] %s\n' "$line" >&2
    done <"$classifier_err"
    rm -f "$classifier_err"
    return 1
  fi
  if [ -s "$classifier_err" ]; then
    while IFS= read -r line; do
      [ -n "$line" ] && warn "$line"
    done <"$classifier_err"
  fi
  rm -f "$classifier_err"
  case "$classifier_status" in
    created | ready)
      ok "classifier file is writable JSON: $CLASSIFIER_PATH"
      ;;
    *)
      fail "unexpected classifier ensure status for $CLASSIFIER_PATH: $classifier_status"
      return 1
      ;;
  esac
  return 0
}

if ! validate_bootstrap_inputs; then
  printf '[error] bootstrap input validation failed with %s issue(s)\n' "$errors" >&2
  exit 1
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
check_google_route
if [ "${TRIAD_BOOTSTRAP_REQUIRE_GEMINI:-0}" = "1" ]; then
  check_binary gemini
elif [ "$GOOGLE_ROUTE" = "agy" ]; then
  check_optional_binary gemini
fi
check_python
if [ "$errors" -eq 0 ]; then
  canonicalize_path_inputs
fi
if [ "$errors" -eq 0 ]; then
  check_workspace_escape
fi
if [ "$errors" -eq 0 ]; then
  resolve_python_runtime
fi
if [ "$errors" -eq 0 ]; then
  check_formal_schema_dependency
fi
printf 'repo root: %s\n' "$REPO_ROOT"
printf 'reminder: trust this workspace in Codex before relying on project-local skills.\n'
if [ "$errors" -ne 0 ]; then
  fail "required prerequisite checks failed; skipping installation steps"
  exit 1
fi
# Exact legacy repair targets share config and launcher state with the remaining
# bootstrap steps. Reject unsafe removal targets before the first persistent
# mutation; the later transactional cleanup revalidates them against races.
if ! run_repair_lifecycle preflight-remove; then
  printf '[error] legacy repair cleanup preflight failed; skipping installation steps\n' >&2
  exit 1
fi
# All three public commands are independent persistent targets. Validate the
# entire group before migration, classifier, logs, or shell
# state can be touched. commands-install repeats the check atomically at
# publication time to reject a target changed after this read-only pass.
if ! preflight_install_command_targets; then
  printf '[error] managed command preflight failed; skipping installation steps\n' >&2
  exit 1
fi
if ! preflight_classifier; then
  printf '[error] classifier preflight failed; skipping installation steps\n' >&2
  exit 1
fi
if ! remove_legacy_permission_artifacts; then
  printf '[error] legacy plugin artifact cleanup failed; skipping installation steps\n' >&2
  exit 1
fi
migrate_legacy_repair_agents
ensure_log_dir
if ! ensure_classifier; then
  printf '[error] classifier installation failed; skipping remaining installation steps\n' >&2
  exit 1
fi
check_local_writable_agent_residual
check_duplicate_selectors
if begin_command_group; then
  install_launchers
  if [ "$errors" -eq 0 ]; then
    publish_command_group
    if [ "$errors" -eq 0 ]; then
      verify_installed_launchers
    fi
  else
    # publish_command_group also removes only the shell-created payload files.
    # Do not hand an incomplete group to the Python mutation engine.
    python3 - "$COMMAND_MANIFEST" <<'PY'
import json
from pathlib import Path
import sys

for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines():
    try:
        Path(json.loads(line)["data_path"]).unlink(missing_ok=True)
    except (KeyError, OSError, ValueError, json.JSONDecodeError):
        pass
PY
    rm -f "$COMMAND_MANIFEST"
    COMMAND_MANIFEST=""
  fi
fi
if [ "$errors" -ne 0 ]; then
  fail "managed command installation failed; skipping remaining installation steps"
  exit 1
fi
if [ "$errors" -eq 0 ]; then
  warn "launcher Python is installer-selected: credential-compatible user-site mode requires a trusted HOME because sitecustomize/usercustomize can run before launcher scrubbing; alternatively select a trusted isolated Python only if it preserves provider login."
  printf 'native permissions: TRIAD installs no Codex permission state; its AGY wrapper selects approved child-only native headless always-proceed without changing stored user/project settings.\n'
  print_owner_apply_argv
  printf 'next step: start a fresh Codex session so the updated native repair protocol loads.\n'
  ok "bootstrap install passed"
  exit 0
fi

fail_count="$errors"
printf '[error] bootstrap install failed with %s issue(s)\n' "$fail_count" >&2
exit 1
