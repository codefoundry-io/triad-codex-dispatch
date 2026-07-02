#!/usr/bin/env bash
set -u

usage() {
  cat <<'EOF'
Usage: scripts/bootstrap.sh --check

Checks local prerequisites for triad-codex-dispatch and installs local launcher
scripts plus personal-scope Codex repair agents when needed.

Assumes codex, claude, and agy are already installed and OAuth logged in.

Set TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 to also install/update the optional
runtime Codex profile at $CODEX_HOME/triad-codex-dispatch.config.toml.
That profile defaults to approval_policy=on-request. Set
TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never only for explicitly approved
heavy-user no-prompt deployments.

Set TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 to install/update user-layer Codex
rules at $CODEX_HOME/rules/triad-codex-dispatch.rules. The generated rules
allow only this checkout's authenticated absolute wrapper launchers.
EOF
}

if [ "${1:-}" != "--check" ]; then
  usage >&2
  exit 2
fi

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
      printf 'import os\n'
      printf 'import sys\n'
      printf 'os.environ["TRIAD_REQUIRE_PINNED_VENDOR"] = "1"\n'
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

install_repair_agents() {
  src="$REPO_ROOT/agents"
  dest="$CODEX_HOME/agents"
  classifier_dir="$(dirname -- "$CLASSIFIER_PATH")"
  python_info="$(python3 - <<'PY'
from pathlib import Path
import sys

print(Path(sys.executable).resolve())
print(Path(sys.executable).resolve().parent)
print(Path(sys.base_prefix).resolve())
print(Path(sys.prefix).resolve())
PY
)" || {
    fail "could not resolve python3 runtime paths"
    return
  }
  python_exe="$(printf '%s\n' "$python_info" | sed -n '1p')"
  python_exe_dir="$(printf '%s\n' "$python_info" | sed -n '2p')"
  python_root="$(printf '%s\n' "$python_info" | sed -n '3p')"
  python_prefix="$(printf '%s\n' "$python_info" | sed -n '4p')"
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
    python3 - "$file" "$dest/$name.toml" "$REPO_ROOT" "$CLASSIFIER_PATH" "$classifier_dir" "$python_exe" "$python_exe_dir" "$python_root" "$python_prefix" <<'PY' || fail "could not install repair agent: $name"
from pathlib import Path
import shutil
import sys

src, dest, repo_root, classifier_path, classifier_dir, python_exe, python_exe_dir, python_root, python_prefix = map(Path, sys.argv[1:])

def toml_string(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace('"', '\\"')

text = src.read_text(encoding="utf-8")
seen_filesystem_keys = {
    toml_string(repo_root),
    toml_string(repo_root / "bin" / "_logs"),
    toml_string(classifier_dir),
}

def read_grant_lines(paths):
    lines = []
    for path in paths:
        key = toml_string(path)
        if key in seen_filesystem_keys:
            continue
        seen_filesystem_keys.add(key)
        lines.append(f'"{key}" = "read"')
    return "\n".join(lines)

python_roots = []
for candidate in (python_exe_dir, python_root, python_prefix):
    if candidate not in python_roots:
        python_roots.append(candidate)
python_root_lines = read_grant_lines(python_roots)
vendor_roots = []
for executable in ("claude", "agy", "gemini", "node"):
    found = shutil.which(executable)
    if not found:
        continue
    for candidate in (Path(found).parent, Path(found).resolve().parent):
        if candidate not in vendor_roots:
            vendor_roots.append(candidate)
vendor_root_lines = read_grant_lines(vendor_roots)
for old, new in {
    "__TRIAD_REPO_ROOT__": toml_string(repo_root),
    "__TRIAD_CLASSIFIER_PATH__": toml_string(classifier_path),
    "__TRIAD_CLASSIFIER_DIR__": toml_string(classifier_dir),
    "__TRIAD_PYTHON3__": toml_string(python_exe),
}.items():
    text = text.replace(old, new)
text = text.replace('"__TRIAD_PYTHON_READ_ROOTS__" = "read"', python_root_lines)
text = text.replace('"__TRIAD_VENDOR_READ_ROOTS__" = "read"', vendor_root_lines)
dest.write_text(text, encoding="utf-8")
PY
  done
  ok "repair agents installed to personal Codex scope: $dest"
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
  if [ "${TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE:-0}" != "1" ]; then
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
# Generated by scripts/bootstrap.sh --check.
# Re-run with TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1 to refresh.
# Explicit external-CLI consent profile: triad dispatch may send relevant
# prompt/repo review material to authenticated claude, agy, and gemini CLIs.
approval_policy = "{approval_policy}"
approvals_reviewer = "user"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
writable_roots = [
  {toml_string(classifier_dir)},
  {toml_string(log_dir)},
]
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
  if [ "${TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES:-0}" != "1" ]; then
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
    "# Generated by scripts/bootstrap.sh --check.",
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
if [ "$errors" -eq 0 ]; then
  canonicalize_path_inputs
fi
printf 'repo root: %s\n' "$REPO_ROOT"
printf 'reminder: trust this workspace in Codex before relying on project-local skills.\n'
if [ "$errors" -ne 0 ]; then
  fail "required prerequisite checks failed; skipping installation steps"
  exit 1
fi
if [ "${TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE:-0}" = "1" ] \
  && [ "$CODEX_PROFILE_APPROVAL_POLICY" = "never" ] \
  && [ "${TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES:-0}" != "1" ]; then
  warn "approval_policy=never without TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1 can auto-deny sandbox escapes; install rules too for no-prompt dispatch"
fi
install_launchers
install_repair_agents
ensure_log_dir
ensure_classifier
install_codex_runtime_profile
install_codex_rules
check_auth

if [ "$errors" -eq 0 ]; then
  ok "bootstrap check passed"
  exit 0
fi

fail_count="$errors"
printf '[error] bootstrap check failed with %s issue(s)\n' "$fail_count" >&2
exit 1
