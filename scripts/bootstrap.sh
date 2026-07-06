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
(see the dispatch SKILL Step 5). (--check is a deprecated alias for --install,
kept for one release.)

--remove uninstalls the managed artifacts: wrapper launchers, the optional
runtime profile and command rules, and the managed codex-triad shell entry. It
also deletes any legacy personal-scope repair-agent TOMLs left by an older
install. Learned classifier patches are preserved.

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
SHELL_RC="${TRIAD_BOOTSTRAP_SHELL_RC:-}"
if [ -z "$SHELL_RC" ]; then
  case "${SHELL:-}" in
    */zsh) SHELL_RC="$HOME/.zshrc" ;;
    *) SHELL_RC="$HOME/.bashrc" ;;
  esac
fi

errors=0

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
    {
      printf '#!%s\n' "$python_exe"
      printf '# triad-codex-dispatch managed launcher\n'
      printf 'import os\n'
      printf 'import sys\n'
      if [ "$wrapper" != "gemini_wrapper.py" ] || [ -n "$vendor_path" ]; then
        printf 'os.environ["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"\n'
      fi
      if [ -n "$vendor_path" ]; then
        printf 'os.environ[%s] = %s\n' "$escaped_vendor_env" "$escaped_vendor_path"
      fi
      printf 'os.execv(%s, [%s, %s] + sys.argv[1:])\n' "$escaped_python" "$escaped_python" "$escaped_target"
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
  codex_home="$CODEX_HOME"
  profile_err="$(mktemp "${TMPDIR:-/tmp}/triad-codex-profile.XXXXXX")" || {
    fail "could not create temporary file for Codex profile install"
    return
  }
  installed="$(python3 - "$codex_home" "$CODEX_PROFILE_NAME" "$CODEX_PROFILE_APPROVAL_POLICY" "$classifier_dir" "$log_dir" 2>"$profile_err" <<'PY'
from pathlib import Path
import sys

MARKER = "# triad-codex-dispatch managed runtime profile"

codex_home_raw, profile_name, approval_policy, classifier_dir_raw, log_dir_raw = sys.argv[1:]
if not profile_name or "/" in profile_name or "\\" in profile_name:
    print(f"invalid TRIAD_CODEX_PROFILE_NAME: {profile_name!r}")
    raise SystemExit(1)
if approval_policy not in {"never", "on-request", "untrusted"}:
    print(f"invalid TRIAD_CODEX_PROFILE_APPROVAL_POLICY: {approval_policy!r}")
    raise SystemExit(1)

codex_home = Path(codex_home_raw).expanduser()
classifier_dir = Path(classifier_dir_raw)
log_dir = Path(log_dir_raw)
profile_path = codex_home / f"{profile_name}.config.toml"

def toml_string(value: Path) -> str:
    text = str(value)
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'

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
{toml_string(classifier_dir)} = "write"
{toml_string(log_dir)} = "write"

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
    if [ ! -e "$agent_file" ]; then
      continue
    fi
    if rm -f "$agent_file"; then
      ok "removed repair agent: $agent_file"
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
install_launchers
ensure_log_dir
ensure_classifier
install_codex_runtime_profile
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
