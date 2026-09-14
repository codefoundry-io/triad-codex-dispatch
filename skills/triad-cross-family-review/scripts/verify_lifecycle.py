#!/usr/bin/env python3
"""Verify one synthetic lifecycle; version/catalog probes only, never inference.

Run from a source checkout with Python 3.12+, Git and AGY available. The JSON
report contains synthetic data and actual subprocess results, not a review verdict.
All writes are confined to newly allocated temporary roots. AGY_SETTINGS_PATH
isolates the Python guard only; this is not a vendor-settings isolation test.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

TOOLKIT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(TOOLKIT / "scripts"))
from verify_distribution import HASH_TARGETS, sha256_file


def _source_hashes():
    return {name: sha256_file(TOOLKIT / name) for name in HASH_TARGETS}


def verify_lifecycle():
    review_id = str(uuid.uuid4())
    report = {
        "status": "WORKFLOW_DEFECT", "review_id": review_id,
        "toolkit_root": str(TOOLKIT), "source_before": None, "source_after": None,
        "commands": [], "failures": [], "cleanup": [],
        "payload_round_trip_verified": False, "integrity_stdout": "",
    }
    owned = []
    managed_root = None
    env = os.environ.copy()
    cli = [sys.executable, str(TOOLKIT / "bin/review_round.py")]

    def run(step, argv, cwd):
        argv = [str(arg) for arg in argv]
        result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True)
        report["commands"].append({
            "step": step, "argv": argv, "cwd": str(cwd),
            "returncode": result.returncode, "stdout": result.stdout,
            "stderr": result.stderr,
        })
        if result.returncode:
            raise RuntimeError(f"{step} exited {result.returncode}")
        return result.stdout

    def temporary(label):
        path = Path(tempfile.mkdtemp(prefix=f"triad-lifecycle-{label}-")).resolve()
        owned.append(path)
        return path

    try:
        report["source_before"] = _source_hashes()
        base = temporary("fixture")
        neutral = temporary("cwd")
        stage = temporary("stage")
        source = base / "source"
        source.mkdir()
        payload = {
            "quote": 'a "quote"', "backslash": "C:\\review\\packet",
            "newline": "first\nsecond", "tab": "left\tright", "unicode": "한글 ✓",
        }
        (source / "input.txt").write_text("Synthetic lifecycle sentinel.\n", encoding="utf-8")
        (source / "payload.json").write_text(json.dumps(payload), encoding="utf-8")
        members_json = json.dumps(["input.txt", "payload.json"])
        members = base / "members.json"
        members.write_text(members_json, encoding="utf-8")
        run("fixture-init", ["git", "init", "--quiet", source], base)
        run("fixture-add", ["git", "add", "input.txt", "payload.json"], source)
        run("fixture-commit", [
            "git", "-c", "user.name=Lifecycle test", "-c", "user.email=lifecycle@example.invalid",
            "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
            "commit", "--quiet", "-m", "Synthetic lifecycle fixture",
        ], source)
        # Private TMPDIR also confines prepare's stale-root scan to this test.
        env.update({
            "TMPDIR": str(base),
            "TRIAD_BOOTSTRAP_CODEX_ROOT": str(stage / "codex-home"),
            "XDG_CONFIG_HOME": str(stage / "config-home"),
            "TRIAD_CLASSIFIER_EXTENSION": str(stage / "config-home/triad-codex-dispatch/classifier-patches.json"),
            "TRIAD_BOOTSTRAP_SHELL_RC": str(stage / "shellrc"),
            "TRIAD_BOOTSTRAP_REPO_ROOT": str(TOOLKIT),
            "TRIAD_BOOTSTRAP_SOURCE_SOT_REVIEW_ROOT": str(source),
            "TRIAD_BOOTSTRAP_BIN_DIR": str(stage / "bin"),
            "PATH": str(stage / "bin") + os.pathsep + env["PATH"],
            "AGY_SETTINGS_PATH": str(base / "agy-settings.json"),
            "TRIAD_DISPATCH_LOG_DIR": str(base / "logs"),
        })
        run("bootstrap", [TOOLKIT / "scripts/bootstrap.sh", "--install"], neutral)
        prepared = json.loads(run("prepare", [
            *cli, "prepare", "--review-id", review_id, "--source-root", source,
            "--member-list", members, "--required-members-json", members_json,
        ], neutral))
        managed_root = Path(prepared["root"])
        shared = Path(prepared["shared_dir"])
        (shared / "TASK.md").write_text(
            "Synthetic JSON transport verification. No review or provider inference.\n", encoding="utf-8"
        )
        diff = run("fixture-diff", ["git", "show", "--format=", "--no-ext-diff", "HEAD"], source)
        (shared / "REVIEW.diff").write_text(diff, encoding="utf-8")
        run("manifest", [*cli, "manifest", "--prepared-dir", shared], neutral)
        snapshot = base / "snapshot.json"
        digest = run("capture", [
            *cli, "capture", "--prepared-dir", shared, "--worktree", source, "--output", snapshot,
        ], neutral).strip()
        selector = base / "selector.json"
        run("select", [
            stage / "bin/review_round.py", "select-google-route", "--review-id", review_id,
            "--authentication-class", "personal-google", "--output", selector,
        ], neutral)
        preflight = base / "preflight.json"
        receipt = run("preflight", [
            sys.executable, TOOLKIT / "bin/antigravity_wrapper.py",
            "--prompt-file", shared / "TASK.md", "--google-selector-receipt", selector,
            "--expected-review-id", review_id, "--cwd", shared, "--sandbox", "read-only",
            "--model", "gemini-3.1-pro-high", "--effort", "high", "--preflight-only",
        ], neutral)
        preflight.write_text(receipt, encoding="utf-8")
        if json.loads(receipt)["provider_started"] is not False:
            raise RuntimeError("preflight did not prove provider_started=false")
        run("render", [
            *cli, "render", "--review-id", review_id, "--review-kind", "implementation-review",
            "--family", "codex", "--google-selector-receipt", selector,
            "--google-preflight-receipt", preflight, "--objective", "Verify synthetic JSON transport",
            "--prepared-dir", shared, "--content-digest", digest,
            "--criterion", "Decoded payload and captured source remain unchanged",
            "--approved-boundary", "Only input.txt and payload.json synthetic fixture",
            "--output", base / "codex-prompt.txt",
        ], neutral)
        report["integrity_stdout"] = run("verify", [
            *cli, "verify", "--prepared-dir", shared, "--worktree", source, "--snapshot", snapshot,
        ], neutral)
        if report["integrity_stdout"].strip() != "ROUND_INTEGRITY_OK":
            raise RuntimeError("missing integrity marker")
        copied_payload = json.loads((Path(prepared["source_dir"]) / "payload.json").read_text(encoding="utf-8"))
        if copied_payload != payload:
            raise RuntimeError("decoded payload changed")
        report["payload_round_trip_verified"] = True
    except Exception as exc:
        report["failures"].append(f"{type(exc).__name__}: {exc}")
    finally:
        if managed_root is not None:
            try:
                run("cleanup", [*cli, "cleanup", "--review-id", review_id, "--expected-root", managed_root], neutral)
            except Exception as exc:
                report["failures"].append(f"cleanup: {type(exc).__name__}: {exc}")
        # Even failed prepare/cleanup may leave artifacts inside our private base.
        # Only roots allocated above are removed; never recurse into a caller path.
        for root in reversed(owned):
            try:
                shutil.rmtree(root)
            except OSError as exc:
                report["failures"].append(f"remove {root}: {exc}")
        roots = ([managed_root] if managed_root is not None else []) + owned
        report["cleanup"] = [{"path": str(root), "absent": not root.exists()} for root in roots]
        try:
            report["source_after"] = _source_hashes()
            if report["source_before"] != report["source_after"]:
                report["failures"].append("packaged source hashes changed")
        except Exception as exc:
            report["failures"].append(f"postcheck: {type(exc).__name__}: {exc}")
    if not report["failures"] and report["payload_round_trip_verified"]:
        report["status"] = "SUCCESS"
    return report


if __name__ == "__main__":
    result = verify_lifecycle()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    raise SystemExit(0 if result["status"] == "SUCCESS" else 1)
