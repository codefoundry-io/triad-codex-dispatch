#!/usr/bin/env bash
# Workspace-escape invariant (HARD):
#   Policy-matched files and everything they exec must live OUTSIDE all
#   sandbox-writable roots.
# The generated exec-policy rules run the wrapper launchers outside the Codex
# sandbox after automatic review by default, or without review only in the
# explicit `never` posture. Both are safe only when the launchers, the pinned
# python3 runtime, the checkout bin/ wrappers they exec, and the Codex policy
# surface (CODEX_HOME rules/profiles/agents) plus the classifier patch dir are
# NOT writable from inside a sandboxed session. A workspace-writable launcher
# (or exec target) lets the sandbox rewrite a trusted executable before asking
# Codex to run it outside the sandbox.
# check_workspace_escape enforces this against the workspace bootstrap is run
# from ($PWD, the sandbox-writable root) and hard-fails on violation.
set -u

usage() {
  cat <<'EOF'
Usage: scripts/bootstrap.sh --install
       scripts/bootstrap.sh --remove

--install checks local prerequisites for triad-codex-dispatch and installs
local launcher scripts, the read-only triad-repair-analyzer Custom Agent, and
the triad-apply-repair executable. Applying a validated proposal remains an
explicit owner action through the installed launcher (see the shared repair
protocol in docs/references/repair-protocol.md).
It also quarantines any legacy personal-scope
repair-agent TOMLs (bootstrap-authored provenance only — a same-name file
without that provenance is left in place) left by an older install into a
timestamped directory outside agents/, recoverable if needed. (--check is a
deprecated alias for --install, kept for one release.)

--remove uninstalls the managed artifacts: wrapper launchers, the optional
runtime profile and command rules, and the managed codex-triad shell entry. It
also removes any bootstrap-managed (provenance-matched) legacy personal-scope
repair-agent TOMLs left by an older install; a non-matching same-name file is
preserved. Learned classifier patches are preserved.

Assumes codex and claude, plus agy, or configured Gemini Enterprise/Business,
Vertex, or API-key routing, are already installed.

Install targets must resolve OUTSIDE the workspace bootstrap runs from:
policy-matched launchers and everything they exec must live outside all
sandbox-writable roots (see the header of this script). Bootstrap hard-fails
otherwise.

By DEFAULT, --install installs/updates the runtime Codex profile at
$CODEX_HOME/triad-codex-dispatch.config.toml AND the user-layer command rules at
$CODEX_HOME/rules/triad-codex-dispatch.rules — so a plain --install with 0 env
vars yields the recommended setup. The profile uses the Codex permission-profile
system (default_permissions = "triad_leader"); it never emits legacy sandbox_mode
/ [sandbox_workspace_write], which would disable permission profiles and
neutralize the triad_leader profile's scoping. By default, the dedicated profile
sets approval_policy=on-request and approvals_reviewer=auto_review. The installed
absolute-launcher rules prompt on the managed wrapper commands so eligible calls
route through automatic approval review. TRIAD_CODEX_PROFILE_APPROVAL_POLICY is
the only triad-specific approval-policy override and remains opt-in. For an
explicitly approved heavy-user no-prompt deployment, set it to never; that
advanced exception keeps the managed wrapper rules on allow.

Alongside the profile, --install merges Codex's native loader-environment
policy ([shell_environment_policy] inherit="all" plus explicit
loader/interpreter excludes) into $CODEX_HOME/config.toml under a provenance
marker (with the first free .bak, .bak2, ... backup). It preserves every other
key and leaves a user's own or edited policy block untouched (warns instead).
The launcher-level environment scrub remains defense in depth. --remove strips
exactly that marker block. See migration/config-fragment.recommended.toml.

To opt OUT of the default profile install, set
TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=0 (or TRIAD_BOOTSTRAP_SKIP_CODEX_PROFILE=1).
To opt OUT of the default command rules, set TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=0
(or TRIAD_BOOTSTRAP_SKIP_CODEX_RULES=1). The generated rules match only this
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
LEGACY_ALIAS_TARGET=""
if [ "$#" -ne 1 ]; then
  usage >&2
  exit 2
fi
case "${1:-}" in
  --install)
    MODE="install"
    ;;
  --check)
    MODE="install"
    LEGACY_ALIAS_TARGET="--install"
    ;;
  --remove)
    MODE="remove"
    ;;
  --uninstall)
    MODE="remove"
    LEGACY_ALIAS_TARGET="--remove"
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
CODEX_PROFILE_APPROVAL_POLICY="${TRIAD_CODEX_PROFILE_APPROVAL_POLICY:-on-request}"
CODEX_PROFILE_APPROVAL_POLICY_EXPLICIT=0
if [ -n "${TRIAD_CODEX_PROFILE_APPROVAL_POLICY:-}" ]; then
  CODEX_PROFILE_APPROVAL_POLICY_EXPLICIT=1
fi
CODEX_RULES_NAME="${TRIAD_CODEX_RULES_NAME:-triad-codex-dispatch.rules}"
# Provenance markers for the managed [shell_environment_policy] block that
# merge_codex_config_fragment appends to $CODEX_HOME/config.toml (and
# remove_codex_config_fragment strips). Keyed on these two literal comment
# lines so --remove deletes exactly OUR block and nothing else.
CONFIG_FRAGMENT_BEGIN="# >>> triad-codex-dispatch managed shell_environment_policy >>>"
CONFIG_FRAGMENT_END="# <<< triad-codex-dispatch managed shell_environment_policy <<<"
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

validate_codex_profile_approval_policy() {
  case "$CODEX_PROFILE_APPROVAL_POLICY" in
    on-request|never|untrusted) return 0 ;;
    *)
      fail "invalid TRIAD_CODEX_PROFILE_APPROVAL_POLICY: must be on-request, never, or untrusted"
      return 1
      ;;
  esac
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
  validate_codex_profile_approval_policy || validation_failed=1
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

runtime_command_is_managed() {
  runtime_command="$1"
  if [ -L "$runtime_command" ]; then
    return 1
  fi
  if [ ! -e "$runtime_command" ]; then
    return 0
  fi
  if [ ! -f "$runtime_command" ]; then
    return 1
  fi
  runtime_name="${runtime_command##*/}"
  python3 "$REPO_ROOT/bin/bootstrap_repair.py" command-owned \
    --kind runtime --name "$runtime_name" --path "$runtime_command" >/dev/null
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
    --launcher "$LAUNCHER_DIR/$APPLY_REPAIR_LAUNCHER" \
    --source "$REPO_ROOT/agents/$REPAIR_ANALYZER_NAME.toml" \
    --apply-patch "$REPO_ROOT/bin/apply_patch.py" \
    --classifier "$CLASSIFIER_PATH"
  if [ "$?" -eq 0 ]; then
    ok "repair artifacts $action completed"
    return 0
  fi
  fail "repair artifact $action failed"
  return 1
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
    fail "invariant: policy-matched launchers and everything they exec must live outside all sandbox-writable roots; run bootstrap from a directory that does not contain the install targets, or point the TRIAD_BOOTSTRAP_* / CODEX_HOME overrides outside this workspace"
  fi
}

check_legacy_sandbox_config() {
  base_config="$CODEX_HOME/config.toml"
  if [ -f "$base_config" ] \
    && grep -Eq '^[[:space:]]*sandbox_mode[[:space:]]*=|^\[sandbox_workspace_write\]' "$base_config"; then
    warn "legacy sandbox settings (sandbox_mode / [sandbox_workspace_write]) found in $base_config; any loaded config layer with them disables permission profiles, neutralizing the triad_leader profile's default_permissions scoping — migrate the base config to permission profiles"
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
# halts --install: a quarantine-dir-create or transaction failure just warns and
# continues to the next name. Called AFTER the errors!=0 -> exit 1 preflight
# gate and check_legacy_sandbox_config, BEFORE install_launchers.
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
      # SEC-3 POSITIVE ENVIRONMENT POLICY. This launcher is policy-matched by
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

# The profile + command rules install by DEFAULT (a plain --install with 0 env
# vars yields the recommended setup). want_codex_profile / want_codex_rules
# encode that default-ON with two opt-outs each: an explicit ...=0, or the
# ...SKIP_... escape. The dedicated profile explicitly selects auto-review and
# stays on-request unless TRIAD_CODEX_PROFILE_APPROVAL_POLICY is set. Exact-
# launcher rules prompt by default; an explicit `never` retains the advanced
# no-prompt allow behavior.
want_codex_profile() {
  [ "${TRIAD_BOOTSTRAP_SKIP_CODEX_PROFILE:-0}" != "1" ] \
    && [ "${TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE:-1}" != "0" ]
}

want_codex_rules() {
  [ "${TRIAD_BOOTSTRAP_SKIP_CODEX_RULES:-0}" != "1" ] \
    && [ "${TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES:-1}" != "0" ]
}

preflight_codex_install_targets() {
  profile_selected="$1"
  rules_selected="$2"
  target_check_failed=0
  if [ "$profile_selected" = "1" ]; then
    profile_path="$CODEX_HOME/$CODEX_PROFILE_NAME.config.toml"
    target_check_output="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" managed-artifact \
      --action preflight --kind profile --path "$profile_path")"
    if [ "$?" -ne 0 ]; then
      target_check_failed=1
      while IFS= read -r line; do
        [ -n "$line" ] && fail "$line"
      done <<EOF
$target_check_output
EOF
    else
      case "$target_check_output" in
        absent | managed) : ;;
        *)
          target_check_failed=1
          fail "unexpected profile preflight status for $profile_path: $target_check_output"
          ;;
      esac
    fi
  fi
  if [ "$rules_selected" = "1" ]; then
    rules_path="$CODEX_HOME/rules/$CODEX_RULES_NAME"
    target_check_output="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" managed-artifact \
      --action preflight --kind rules --path "$rules_path")"
    if [ "$?" -ne 0 ]; then
      target_check_failed=1
      while IFS= read -r line; do
        [ -n "$line" ] && fail "$line"
      done <<EOF
$target_check_output
EOF
    else
      case "$target_check_output" in
        absent | managed) : ;;
        *)
          target_check_failed=1
          fail "unexpected rules preflight status for $rules_path: $target_check_output"
          ;;
      esac
    fi
  fi
  [ "$target_check_failed" -eq 0 ]
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
  # wrapper .py exec targets (bin_dir), the policy-matched launchers
  # (LAUNCHER_DIR), the resolved python3 runtime, and each resolved vendor
  # binary the wrappers exec -- see the header invariant + the python
  # heredoc comment below for why. Resolve the python3 runtime the same way
  # install_launchers resolves it for the launcher shebang (bare `python3`
  # on PATH; sys.executable canonicalized) so the deny matches the actual
  # exec target.
  python_runtime="$python_exe"
  if [ -z "$python_runtime" ]; then
    fail "missing preflighted Python runtime for the Codex profile deny-list"
    return
  fi

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
  profile_payload="$(mktemp "${TMPDIR:-/tmp}/triad-codex-profile-payload.XXXXXX")" || {
    fail "could not create temporary payload for Codex profile install"
    rm -f "$profile_err"
    return
  }
  if ! python3 - "$codex_home" "$CODEX_PROFILE_NAME" "$CODEX_PROFILE_APPROVAL_POLICY" "$CODEX_PROFILE_APPROVAL_POLICY_EXPLICIT" "$classifier_dir" "$log_dir" "$bin_dir" "$LAUNCHER_DIR" "$debug_dir" "$python_runtime" "$claude_bin" "$gemini_bin" "$agy_bin" >"$profile_payload" 2>"$profile_err" <<'PY'
from pathlib import Path
import sys

MARKER = "# triad-codex-dispatch managed runtime profile"

(
    codex_home_raw, profile_name, approval_policy, approval_policy_explicit,
    classifier_dir_raw, log_dir_raw,
    bin_dir_raw, launcher_dir_raw, debug_dir_raw, python_runtime_raw,
    claude_bin_raw, gemini_bin_raw, agy_bin_raw,
) = sys.argv[1:]
if not profile_name or "/" in profile_name or "\\" in profile_name:
    print(f"invalid TRIAD_CODEX_PROFILE_NAME: {profile_name!r}")
    raise SystemExit(1)
if approval_policy not in {"never", "on-request", "untrusted"}:
    print(f"invalid TRIAD_CODEX_PROFILE_APPROVAL_POLICY: {approval_policy!r}")
    raise SystemExit(1)
if approval_policy_explicit not in {"0", "1"}:
    print(
        "invalid TRIAD_CODEX_PROFILE_APPROVAL_POLICY explicitness flag: "
        f"{approval_policy_explicit!r}"
    )
    raise SystemExit(1)

codex_home = Path(codex_home_raw).expanduser()
classifier_dir = Path(classifier_dir_raw)
log_dir = Path(log_dir_raw)
bin_dir = Path(bin_dir_raw)
launcher_dir = Path(launcher_dir_raw)
debug_dir = Path(debug_dir_raw)
python_runtime = Path(python_runtime_raw)
vendor_bins = [Path(p) for p in (claude_bin_raw, gemini_bin_raw, agy_bin_raw) if p]

def toml_string(value: Path) -> str:
    text = str(value)
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'

approval_policy_line = f'approval_policy = {toml_string(approval_policy)}\n'

# --- SEC-3: exec-target write-denies ------------------------------------
# Workspace-escape invariant (see this script's header): the wrapper .py
# exec targets (bin_dir), the policy-matched launchers (launcher_dir), the
# python3 runtime, and the vendor CLI binaries the wrappers exec must be
# non-writable from inside a sandboxed session -- otherwise a tampered exec
# target is a trusted-executable rewrite chain (promptless in the explicit
# `never` posture; spike-proven 2026-07-16: a
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

sys.stdout.write(
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
{approval_policy_line}approvals_reviewer = "auto_review"
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
"""
)
PY
  then
    profile_output="$(cat "$profile_err")"
    while IFS= read -r line; do
      [ -n "$line" ] && fail "$line"
    done <<EOF
$profile_output
EOF
    rm -f "$profile_payload" "$profile_err"
    return
  fi
  profile_path="$codex_home/$CODEX_PROFILE_NAME.config.toml"
  installed="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" managed-artifact \
    --action install --kind profile --path "$profile_path" \
    --payload-file "$profile_payload" 2>>"$profile_err")"
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
    rm -f "$profile_payload" "$profile_err"
    return
  fi
  case "$installed" in
    created | updated | unchanged) : ;;
    *)
      fail "unexpected Codex runtime profile install status for $profile_path: $installed"
      rm -f "$profile_payload" "$profile_err"
      return
      ;;
  esac
  if [ -s "$profile_err" ]; then
    while IFS= read -r line; do
      [ -n "$line" ] && warn "$line"
    done <"$profile_err"
  fi
  rm -f "$profile_payload" "$profile_err"
  ok "Codex runtime profile installed: $profile_path ($installed)"
}

# merge_codex_config_fragment — native env-boundary close. Merges Codex's
# [shell_environment_policy] inherit="all" plus explicit case-insensitive
# loader/interpreter excludes into $CODEX_HOME/config.toml. `inherit="all"`
# retains normal environment values (including the triad wrapper controls) and
# retains Codex's default KEY/SECRET/TOKEN exclusions. The explicit excludes
# drop LD_*, DYLD_*, NODE_OPTIONS, NODE_PATH, PYTHON*, BASH_ENV, ENV,
# PERL5LIB, RUBYOPT, and RUBYLIB before Codex spawns any subprocess, including
# the policy-matched wrapper launchers that run outside the sandbox. The launcher
# env scrub remains defense in depth for its own descendant process.
#
# G4 (never clobber a user's own config): there is NO stdlib TOML *writer*
# (tomllib is read-only), so a hand-rolled full-file re-emit would destroy the
# user's comments/formatting/ordering. Instead the python heredoc uses tomllib
# ONLY to PARSE the existing config.toml and CHECK whether a
# [shell_environment_policy] table already exists:
#   * the exact legacy managed inherit="core" block -> replace only that block
#       with the current managed policy, preserving every outside byte.
#   * any other marker-delimited block -> leave it untouched (an edited block
#       is user-owned until explicitly reconciled).
#   * a [shell_environment_policy] table present but NOT ours (user's own)
#       -> leave it untouched; WARN (respect the user's config).
#   * absent -> APPEND the marker-delimited managed block (preserving every
#       other key), published against captured target state after an absent-only
#       first-free .bak, .bak2, ... backup of the prior file.
# NON-fatal by design (defense-in-depth on top of the always-on launcher env
# scrub): never calls fail -- any read/parse/write error just WARNs and leaves
# config.toml untouched, so a config.toml hiccup never blocks --install.
# Gated on want_codex_profile (same gate the replaced WARN used): the fragment
# reinforces the same exec-target trust boundary the managed profile protects.
# bash-3.2-safe: array-free/[[ ]]-free; bootstrap_repair.py owns the TOML and
# descriptor-checked publication work.
merge_codex_config_fragment() {
  if [ "$errors" -ne 0 ]; then
    return
  fi
  if ! want_codex_profile; then
    return
  fi
  config_path="$CODEX_HOME/config.toml"
  merge_status="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" config-fragment \
    --action merge --path "$config_path")"
  merge_rc=$?
  if [ "$merge_rc" -ne 0 ]; then
    merge_status="crash"
  fi
  case "$merge_status" in
    merged)
      ok "merged native [shell_environment_policy] inherit=\"all\" with explicit loader/interpreter excludes into $config_path; the retained backup path and cleanup guidance were reported above; the launcher env scrub remains defense in depth"
      ;;
    migrated)
      ok "migrated the exact legacy managed [shell_environment_policy] inherit=\"core\" block to inherit=\"all\" with explicit loader/interpreter excludes in $config_path; the retained backup path and cleanup guidance were reported above"
      ;;
    already-managed)
      ok "native [shell_environment_policy] fragment already present (managed) in $config_path; no change"
      ;;
    user-policy)
      warn "$config_path already defines its own [shell_environment_policy]; leaving it untouched. For loader-env hardening keep inherit=\"all\" and add exclude=[\"LD_*\",\"DYLD_*\",\"NODE_OPTIONS\",\"NODE_PATH\",\"PYTHON*\",...]; see migration/config-fragment.recommended.toml"
      ;;
    edited-managed)
      warn "$config_path contains an edited managed [shell_environment_policy] block; leaving it untouched. Reconcile it manually with migration/config-fragment.recommended.toml"
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
# the personal machine's root-owned /etc/codex/requirements.toml; NEVER from
# $CODEX_HOME (a per-user path bootstrap could write unprivileged).
# A copy written there would be silently inert (Codex never loads it) while
# looking like a closed gap -- so bootstrap ships a first-party recommended
# file (migration/requirements.recommended.toml) for the machine owner to
# install with administrator privileges and only WARNs here, pointing at it;
# it never writes to /etc/codex itself (that needs privileges bootstrap does
# not have and must not assume).
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
    warn "the installed profile (default_permissions=\"triad_leader\") protects this session's own exec targets, but a TRUSTED project's own .codex/config.toml with a legacy sandbox_mode key disables permission profiles for that project, which can override the exec-target denies above; to ENFORCE the permission-profile model machine-wide (block that legacy-sandbox opt-out -- the per-machine deny BODY stays in this per-user profile; Codex >= 0.138.0 required), follow the installed plugin's migration/requirements.recommended.toml instructions. Its cwd-independent Python shlex.join command printer resolves the absolute plugin path and emits a no-clobber argv-safe admin command. Do NOT overwrite an existing /etc/codex/requirements.toml; if it exists, MERGE default_permissions + [allowed_permission_profiles].triad_leader into it by hand."
    warn "non-root partial mitigation (per sensitive project, no root needed): add [projects.\"<abs-path>\"] trust_level = \"untrusted\" to ~/.codex/config.toml to stop that project's own .codex/ config layer from loading"
    # The env-boundary hardening ([shell_environment_policy] inherit="all" plus
    # explicit loader/interpreter excludes) is
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
if ! python3 - "$codex_home" "$CODEX_RULES_NAME" "$REPO_ROOT" "$LAUNCHER_DIR" "$CODEX_PROFILE_APPROVAL_POLICY" "$CODEX_PROFILE_APPROVAL_POLICY_EXPLICIT" >"$rules_output" 2>"$rules_err" <<'PY'
from pathlib import Path
import shlex
import sys

MARKER = "# triad-codex-dispatch managed command rules"
WRAPPERS = (
    ("claude_wrapper.py", "Claude wrapper"),
    ("antigravity_wrapper.py", "Antigravity wrapper"),
    ("gemini_wrapper.py", "Gemini business-tier wrapper"),
)

(
    codex_home_raw, rules_name, repo_root_raw, launcher_dir_raw,
    approval_policy, approval_policy_explicit,
) = sys.argv[1:]
if not rules_name.endswith(".rules") or "/" in rules_name or "\\" in rules_name:
    print(f"invalid TRIAD_CODEX_RULES_NAME: {rules_name!r}")
    raise SystemExit(1)
if approval_policy not in {"never", "on-request", "untrusted"}:
    print(f"invalid TRIAD_CODEX_PROFILE_APPROVAL_POLICY: {approval_policy!r}")
    raise SystemExit(1)
if approval_policy_explicit not in {"0", "1"}:
    print(
        "invalid TRIAD_CODEX_PROFILE_APPROVAL_POLICY explicitness flag: "
        f"{approval_policy_explicit!r}"
    )
    raise SystemExit(1)

codex_home = Path(codex_home_raw).expanduser()
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

advanced_no_prompt = approval_policy == "never" and approval_policy_explicit == "1"
decision = "allow" if advanced_no_prompt else "prompt"

lines = [
    MARKER,
    "# Generated by scripts/bootstrap.sh --install.",
    "# Re-run with TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 to refresh.",
    (
        "# Explicit approval_policy=never exception: these rules allow "
        "wrapper-specific command prefixes."
        if advanced_no_prompt
        else "# These rules prompt on wrapper-specific command prefixes for automatic review."
    ),
    "# They do not allow broad shell entrypoints such as bash -lc or zsh -lc.",
    "",
]

for wrapper, label in WRAPPERS:
    launcher_path = launcher_dir / wrapper
    repo_path = repo_root / "bin" / wrapper
    prompt_path = repo_root / "_runs" / "prompts" / "triad-prompt.txt"
    wrapper_paths = unique([str(launcher_path)])
    justification = (
        f"Allow authenticated triad {label} commands outside the sandbox."
        if advanced_no_prompt
        else (
            "Require automatic approval review; approve only an owner-authorized "
            f"triad review through the {label} whose provider-visible input excludes "
            "credentials, tokens, cookies, and authentication files."
        )
    )

    lines.extend([
        "prefix_rule(",
        f"    pattern = [{starlark_list(wrapper_paths)}],",
        f'    decision = "{decision}",',
        f"    justification = {starlark_string(justification)},",
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

print("\n".join(lines), end="")
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
  rules_path="$codex_home/rules/$CODEX_RULES_NAME"
  installed="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" managed-artifact \
    --action install --kind rules --path "$rules_path" \
    --payload-file "$rules_output" 2>>"$rules_err")"
  if [ "$?" -ne 0 ]; then
    rules_fail_output="$installed
$(cat "$rules_err")"
    while IFS= read -r line; do
      [ -n "$line" ] && fail "$line"
    done <<EOF
$rules_fail_output
EOF
    rm -f "$rules_output" "$rules_err"
    return
  fi
  case "$installed" in
    created | updated | unchanged) : ;;
    *)
      fail "unexpected Codex command rules install status for $rules_path: $installed"
      rm -f "$rules_output" "$rules_err"
      return
      ;;
  esac
  if [ -s "$rules_err" ]; then
    while IFS= read -r line; do
      [ -n "$line" ] && warn "$line"
    done <"$rules_err"
  fi
  rm -f "$rules_output" "$rules_err"
  ok "Codex command rules installed: $rules_path ($installed)"
}

# Read-only validation shared by install and remove before public command
# publication/removal. A malformed marker state must never reach the transformer.
preflight_shell_entry() {
  shell_action="$1"
  if [ "$shell_action" = "install" ] \
    && [ "${TRIAD_BOOTSTRAP_INSTALL_SHELL_ENTRY:-0}" != "1" ]; then
    return 0
  fi
  if python3 "$REPO_ROOT/bin/bootstrap_repair.py" shell-entry \
    --action "preflight-$shell_action" --path "$SHELL_RC" \
    --profile "$CODEX_PROFILE_NAME" >/dev/null; then
    return 0
  fi
  fail "shell entry preflight failed: $SHELL_RC"
  return 1
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
  shell_install_status="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" shell-entry \
    --action install --path "$rc_file" --profile "$CODEX_PROFILE_NAME")"
  if [ "$?" -ne 0 ]; then
    fail "could not install codex-triad shell entry in $rc_file"
    return
  fi
  case "$shell_install_status" in
    installed)
      ok "codex-triad shell entry installed: $rc_file"
      ;;
    *)
      fail "unexpected codex-triad shell install status for $rc_file: $shell_install_status"
      ;;
  esac
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

# remove_codex_config_fragment — symmetric to merge_codex_config_fragment.
# Removes exactly one literal current or legacy managed
# [shell_environment_policy] block from $CODEX_HOME/config.toml. Any edited,
# duplicate, incomplete, or otherwise unrecognized marker state is left
# byte-for-byte untouched. Removal is literal replacement, never a marker-range
# scan or newline-normalizing reserialization. If the literal block was the
# entire file, remove the file to restore the pre-install absent state.
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
  if ! preflight_shell_entry remove; then
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

  shell_remove_status="$(python3 "$REPO_ROOT/bin/bootstrap_repair.py" shell-entry \
    --action remove --path "$SHELL_RC" --profile "$CODEX_PROFILE_NAME")"
  if [ "$?" -ne 0 ]; then
    fail "could not remove managed codex-triad shell entry from $SHELL_RC"
  else
    case "$shell_remove_status" in
      removed)
        ok "removed managed codex-triad shell entry from $SHELL_RC"
        ;;
      unmanaged)
        warn "leaving unmanaged codex-triad entry in place: $SHELL_RC (not installed by bootstrap)"
        ;;
      absent)
        ok "no codex-triad shell entry to remove: $SHELL_RC"
        ;;
      *)
        fail "unexpected codex-triad shell remove status for $SHELL_RC: $shell_remove_status"
        ;;
    esac
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

  run_repair_lifecycle remove

  profile_path="$CODEX_HOME/$CODEX_PROFILE_NAME.config.toml"
  remove_owned_artifact \
    profile \
    "$profile_path" \
    "removed Codex runtime profile: $profile_path" \
    "leaving unmanaged Codex profile in place: $profile_path"

  if ! remove_codex_config_fragment; then
    return
  fi

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
  remove_owned_artifact \
    rules \
    "$rules_path" \
    "removed Codex command rules: $rules_path" \
    "leaving unmanaged Codex rules file in place: $rules_path"

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

if [ -n "$LEGACY_ALIAS_TARGET" ]; then
  warn "${1:-} is a deprecated alias for $LEGACY_ALIAS_TARGET; kept through 0.2.527 and scheduled for removal after 0.2.527"
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
if want_codex_profile \
  && [ "$CODEX_PROFILE_APPROVAL_POLICY" = "never" ] \
  && ! want_codex_rules; then
  warn "approval_policy=never with the command rules opted out can auto-deny sandbox escapes; keep the default rules install for no-prompt dispatch"
fi
# Repair targets share config and launcher state with the remaining bootstrap
# steps. Reject unsafe/unmanaged repair inputs before the first persistent
# mutation; the later transactional install revalidates them against races.
if ! run_repair_lifecycle preflight-install; then
  printf '[error] repair artifact preflight failed; skipping installation steps\n' >&2
  exit 1
fi
# All three public commands are independent persistent targets. Validate the
# entire group before migration, profiles, rules, classifier, logs, or shell
# state can be touched. commands-install repeats the check atomically at
# publication time to reject a target changed after this read-only pass.
if ! preflight_install_command_targets; then
  printf '[error] managed command preflight failed; skipping installation steps\n' >&2
  exit 1
fi
if want_codex_profile; then
  profile_selected=1
else
  profile_selected=0
fi
if want_codex_rules; then
  rules_selected=1
else
  rules_selected=0
fi
if ! preflight_codex_install_targets "$profile_selected" "$rules_selected"; then
  printf '[error] Codex profile/rules preflight failed; skipping installation steps\n' >&2
  exit 1
fi
if ! preflight_shell_entry install; then
  printf '[error] shell entry preflight failed; skipping installation steps\n' >&2
  exit 1
fi
if ! preflight_classifier; then
  printf '[error] classifier preflight failed; skipping installation steps\n' >&2
  exit 1
fi
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
migrate_legacy_repair_agents
ensure_log_dir
if ! ensure_classifier; then
  printf '[error] classifier installation failed; skipping remaining installation steps\n' >&2
  exit 1
fi
install_codex_runtime_profile
merge_codex_config_fragment
if run_repair_lifecycle install; then
  check_legacy_sandbox_config
  check_local_writable_agent_residual
  check_duplicate_selectors
fi
warn_requirements_remediation
install_codex_rules
install_shell_entry
report_no_prompt_posture

if [ "$errors" -eq 0 ]; then
  printf 'next step: start a fresh Codex session so the new agent_type %s loads.\n' "$REPAIR_ANALYZER_NAME"
  ok "bootstrap install passed"
  exit 0
fi

fail_count="$errors"
printf '[error] bootstrap install failed with %s issue(s)\n' "$fail_count" >&2
exit 1
