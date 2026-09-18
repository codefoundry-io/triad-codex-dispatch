#!/usr/bin/env python3
"""Standalone metadata snapshot; no inference, configuration or admission."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile

import _common
import review_round
from antigravity_wrapper import FORMAL_AGY_ENV_REMOVE

PROBE_TIMEOUT = 5


def _run_probe(binary: str, args: list[str], cwd: str, env: dict) -> tuple[dict, bytes]:
    record = {"args": args, "status": "launch_failed", "exit_code": None}
    stdout = b""
    try:
        proc = subprocess.Popen(
            [binary, *args], cwd=cwd, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=os.name == "posix",
        )
    except OSError:
        pass
    else:
        pgid = None
        if os.name == "posix":
            try:
                candidate = os.getpgid(proc.pid)
                if candidate == proc.pid and candidate != os.getpgrp():
                    pgid = candidate
            except OSError:
                pass
        try:
            stdout, _ = proc.communicate(timeout=PROBE_TIMEOUT)
            record.update(status="ok" if proc.returncode == 0 else "failed",
                          exit_code=proc.returncode)
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout or b""
            _common._terminate_provider_process_group(proc, "diagnostic probe timeout", pgid)
            record.update(status="timeout", exit_code=proc.returncode)
        except OSError:
            _common._terminate_provider_process_group(proc, "diagnostic probe I/O failure", pgid)
            record.update(status="io_failed", exit_code=proc.returncode)
        except BaseException:
            _common._terminate_provider_process_group(proc, "diagnostic probe interrupted", pgid)
            raise
        finally:
            proc.stdout.close()
            proc.stderr.close()
    record.update(stdout_bytes=len(stdout), stdout_sha256=hashlib.sha256(stdout).hexdigest())
    return record, stdout


def _advertises(help_bytes: bytes, cli: str, command: str) -> bool:
    # Require a command-entry line, not a word embedded in explanatory prose.
    text = help_bytes.decode("utf-8", errors="replace")
    pattern = rf"(?m)^[ \t]*(?:{re.escape(cli)}[ \t]+)?{re.escape(command)}(?:[ \t]+(?:\[[^\n\]]*\]|<[^\n>]*>))*(?:[ \t]{{2,}}[^\n]+|[ \t]*$)"
    return re.search(pattern, text) is not None


def _model_catalog(raw: bytes) -> dict:
    unknown = {"model_format": "unrecognized", "model_slugs": []}
    try:
        text = raw.decode("utf-8")
    except UnicodeError:
        return unknown
    slugs = []
    for line in text.splitlines():
        if not line.strip():
            continue
        slug, separator, label = line.partition("\t")
        if not separator or not label.strip() or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}", slug):
            return unknown
        if slug not in slugs:
            slugs.append(slug)
            if len(slugs) > 128:
                return unknown
    return {"model_format": "tab-separated", "model_slugs": slugs} if slugs else unknown


def collect_snapshot(cli: str, inventory: bool = False) -> dict:
    snapshot = {"cli": cli, "status": "complete", "probes": [], "capabilities": {}}
    try:
        binary = review_round._selectable_google_binary(cli)
    except review_round.RoundIntegrityError:
        return {**snapshot, "status": "incomplete", "error": "selection_failed"}
    if binary is None:
        return {**snapshot, "status": "incomplete", "error": "binary_missing"}
    env = _common.scrubbed_child_env(remove=FORMAL_AGY_ENV_REMOVE)
    try:
        if not os.path.isabs(binary):
            binary = os.path.join(os.getcwd(), binary)
        with tempfile.TemporaryDirectory(prefix="triad-google-diagnostic-") as cwd:
            def probe(args: list[str]) -> bytes | None:
                record, raw = _run_probe(binary, args, cwd, env)
                snapshot["probes"].append(record)
                if record["status"] != "ok":
                    snapshot["status"] = "incomplete"
                    return None
                return raw

            version = probe(["--version"])
            if version is None:
                return snapshot
            match = re.search(rb"(?<![0-9.])[0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}(?![0-9.])", version)
            if match:
                snapshot["version"] = match.group().decode("ascii")
            help_bytes = probe(["--help"])
            if help_bytes is None:
                return snapshot
            names = ("models", "plugin") if cli == "agy" else ("extensions",)
            snapshot["capabilities"] = {name: _advertises(help_bytes, cli, name) for name in names}
            if not inventory:
                return snapshot
            if cli == "agy" and snapshot["capabilities"]["models"]:
                if probe(["models", "--help"]) is None:
                    return snapshot
                models = probe(["models"])
                if models is None:
                    return snapshot
                snapshot.update(_model_catalog(models))
            group = "plugin" if cli == "agy" else "extensions"
            if snapshot["capabilities"][group]:
                group_help = probe([group, "--help"])
                if group_help is None:
                    return snapshot
                if _advertises(group_help, f"{cli} {group}", "list"):
                    probe([group, "list"])
    except OSError:
        snapshot.update(status="incomplete", error="host_io_failed")
    return snapshot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", choices=("agy", "gemini"), required=True)
    parser.add_argument("--inventory", action="store_true")
    args = parser.parse_args(argv)
    snapshot = collect_snapshot(args.cli, args.inventory)
    print(json.dumps(snapshot, sort_keys=True))
    return 0 if snapshot["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
