#!/usr/bin/env bash
set -u

usage() {
  cat <<'EOF'
Usage: scripts/bootstrap.sh --check

Checks local prerequisites for triad-codex-dispatch and installs local launcher
scripts plus personal-scope Codex repair agents when needed.
EOF
}

if [ "${1:-}" != "--check" ]; then
  usage >&2
  exit 2
fi

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${TRIAD_BOOTSTRAP_REPO_ROOT:-$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)}"
LAUNCHER_DIR="${TRIAD_BOOTSTRAP_BIN_DIR:-$HOME/.local/bin}"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
CLASSIFIER_PATH="${TRIAD_CLASSIFIER_EXTENSION:-$CONFIG_HOME/triad-codex-dispatch/classifier-patches.json}"
AUTH_TIMEOUT="${TRIAD_BOOTSTRAP_AUTH_TIMEOUT:-30}"

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

  run_auth_probe "codex" "${TRIAD_BOOTSTRAP_CODEX_AUTH_CMD:-codex doctor}"
  run_auth_probe "claude" "${TRIAD_BOOTSTRAP_CLAUDE_AUTH_CMD:-claude -p 'Return exactly OK.' --output-format json --permission-mode dontAsk --allowedTools Read}"
  run_auth_probe "agy" "${TRIAD_BOOTSTRAP_AGY_AUTH_CMD:-agy -p 'Return exactly OK.'}"
  if command -v gemini >/dev/null 2>&1; then
    if [ "${TRIAD_BOOTSTRAP_REQUIRE_GEMINI:-0}" = "1" ]; then
      run_auth_probe "gemini" "${TRIAD_BOOTSTRAP_GEMINI_AUTH_CMD:-gemini -p 'Return exactly OK.'}"
    else
      run_auth_probe "gemini" "${TRIAD_BOOTSTRAP_GEMINI_AUTH_CMD:-gemini -p 'Return exactly OK.'}" optional
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
    resolved="$(command -v "$wrapper" 2>/dev/null || true)"
    if [ -z "$resolved" ] || [ ! -x "$resolved" ]; then
      all_wrappers_ready=0
    fi
  done
  if [ "$all_wrappers_ready" -eq 1 ]; then
    ok "wrapper commands already executable on PATH"
    return
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
    escaped_target="$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$target")" || {
      fail "could not quote launcher target: $target"
      continue
    }
    {
      printf '#!/usr/bin/env python3\n'
      printf 'import os\n'
      printf 'import sys\n'
      printf 'os.execv(sys.executable, [sys.executable, %s] + sys.argv[1:])\n' "$escaped_target"
    } >"$launcher" || {
      fail "could not write launcher: $launcher"
      continue
    }
    chmod 0755 "$launcher" || fail "could not chmod launcher: $launcher"
  done

  if path_has_dir "$LAUNCHER_DIR"; then
    ok "launcher scripts installed in PATH: $LAUNCHER_DIR"
  else
    fail "launcher directory is not on PATH: $LAUNCHER_DIR"
  fi
}

install_repair_agents() {
  src="$REPO_ROOT/agents"
  dest="$HOME/.codex/agents"
  mkdir -p "$dest" || {
    fail "could not create Codex agents directory: $dest"
    return
  }

  for name in claude-wrapper-repair gemini-wrapper-repair agy-wrapper-repair; do
    file="$src/$name.toml"
    if [ ! -f "$file" ]; then
      fail "missing repair agent source: $file"
      continue
    fi
    cp "$file" "$dest/$name.toml" || fail "could not install repair agent: $name"
  done
  ok "repair agents installed to personal Codex scope: $dest"
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

printf 'triad-codex-dispatch bootstrap check\n'
printf 'repo root: %s\n' "$REPO_ROOT"
printf 'reminder: trust this workspace in Codex before relying on project-local skills.\n'

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
install_launchers
install_repair_agents
ensure_classifier
check_auth

if [ "$errors" -eq 0 ]; then
  ok "bootstrap check passed"
  exit 0
fi

fail_count="$errors"
printf '[error] bootstrap check failed with %s issue(s)\n' "$fail_count" >&2
exit 1
