from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_REQUIRED_ENVIRONMENT_NAMES = [
    "TRIAD_WRAPPER_ALLOWED_ROOTS",
    "TRIAD_WRAPPER_HARDENED",
    "TRIAD_CLAUDE_ENFORCE_SANDBOX",
]


@dataclass(frozen=True)
class ProbeResult:
    argv: tuple[str, ...]
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool
    family: str


def _output_text(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value or ""


def classify_probe_failure(stderr: str) -> str:
    message = stderr.lower()
    if any(term in message for term in ("login", "oauth", "credential")):
        return "auth"
    if any(
        term in message
        for term in ("sandbox", "environment", "permission denied")
    ):
        return "sandbox-env"
    if any(term in message for term in ("quota", "rate limit", "capacity")):
        return "quota-capacity"
    if any(
        term in message for term in ("unknown option", "unsupported", "version")
    ):
        return "version-config"
    return "transport"


def _signal_process_group(process_id: int, signal_number: int) -> None:
    try:
        os.killpg(process_id, signal_number)
    except (ProcessLookupError, PermissionError):
        pass


def run_argv(
    argv: Sequence[str], *, timeout_seconds: int, env: Mapping[str, str] | None = None
) -> ProbeResult:
    if not argv or any(not isinstance(token, str) or not token for token in argv):
        raise ValueError("probe argv must contain non-empty string tokens")
    if timeout_seconds <= 0:
        raise ValueError("probe timeout must be positive")

    normalized_argv = tuple(argv)
    try:
        process = subprocess.Popen(
            list(normalized_argv),
            shell=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=None if env is None else dict(env),
            start_new_session=True,
        )
    except OSError as exc:
        return ProbeResult(normalized_argv, None, "", str(exc), False, "transport")

    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        _signal_process_group(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            _signal_process_group(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        return ProbeResult(
            normalized_argv,
            None,
            _output_text(stdout),
            _output_text(stderr),
            True,
            "transport",
        )

    family = "" if process.returncode == 0 else classify_probe_failure(stderr)
    return ProbeResult(
        normalized_argv,
        process.returncode,
        stdout,
        stderr,
        False,
        family,
    )


def setup_state_path(workspace: Path) -> Path:
    digest = hashlib.sha256(str(workspace).encode("utf-8")).hexdigest()
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    if not config_home.is_absolute():
        raise ValueError("XDG_CONFIG_HOME must be absolute")
    return config_home / "triad-codex-dispatch" / "setup" / f"{digest}.json"


def _workspace_from_argument(value: str) -> Path:
    supplied = Path(value).expanduser()
    if not supplied.is_absolute() or not supplied.is_dir():
        raise ValueError("workspace must be an existing absolute directory")
    return supplied.resolve()


def _setup_state(workspace: Path, args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "workspace_root": str(workspace),
        "external_review_authorized": True,
        "provider_routes": ["claude", "google"],
        "approval_policy": args.approval_policy,
        "no_prompt": args.no_prompt,
        "required_environment_names": _REQUIRED_ENVIRONMENT_NAMES,
    }


def _atomic_write_json(path: Path, state: dict[str, Any]) -> None:
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary_path = Path(stream.name)
            json.dump(state, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
        parent_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def setup_main(args: argparse.Namespace) -> int:
    workspace = _workspace_from_argument(args.workspace)
    if not args.authorize_external_review:
        raise ValueError("setup requires --authorize-external-review")
    if args.no_prompt and args.approval_policy != "never":
        raise ValueError("--no-prompt requires --approval-policy never")

    state_path = setup_state_path(workspace)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_json(state_path, _setup_state(workspace, args))
    print("setup recorded; use native provider login commands, then start a fresh Codex session")
    return 0


def static_findings(workspace: Path) -> list[str]:
    """Inspect local setup state only; never call provider or network transports."""
    state_path = setup_state_path(workspace)
    if not state_path.is_file():
        return ["setup state is missing"]
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return ["setup state is unreadable"]
    if not isinstance(state, dict):
        return ["setup state is unreadable"]
    if state.get("workspace_root") != str(workspace):
        return ["setup state workspace does not match doctor workspace"]
    return []


def emit_report(report: dict[str, Any], as_json: bool) -> int:
    if as_json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        for finding in report["findings"]:
            print(f"finding: {finding}")
    return 0 if not report["findings"] else 1


def doctor_main(args: argparse.Namespace) -> int:
    workspace = _workspace_from_argument(args.workspace)
    findings = static_findings(workspace)
    if args.live:
        raise ValueError("live doctor is not available until the runtime launchers are installed")
    print("static doctor: no provider probes run")
    return emit_report({"mode": "static", "findings": findings}, args.json)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)

    setup = commands.add_parser("setup", allow_abbrev=False)
    setup.add_argument("--workspace", required=True)
    setup.add_argument("--authorize-external-review", action="store_true")
    setup.add_argument(
        "--approval-policy", choices=("on-request", "never"), required=True
    )
    setup.add_argument("--no-prompt", action="store_true")

    doctor = commands.add_parser("doctor", allow_abbrev=False)
    doctor.add_argument("--workspace", required=True)
    doctor.add_argument("--live", action="store_true")
    doctor.add_argument("--timeout", type=int, default=30)
    doctor.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    return setup_main(args) if args.command == "setup" else doctor_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
