"""Real lifecycle/guard checks with catalog and CLI-presence doubles; no inference."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/triad-cross-family-review/scripts/verify_lifecycle.py"


@pytest.fixture
def catalog_only_vendor(tmp_path, monkeypatch):
    vendor = tmp_path / "vendor"
    vendor.mkdir()
    calls = tmp_path / "vendor-calls"
    agy = vendor / "agy"
    agy.write_text(
        "#!/bin/sh\n"
        'printf "%s\\n" "$*" >> "$LIFECYCLE_TEST_CALLS"\n'
        'case "$*" in\n'
        '  --version) printf "1.2.2\\n" ;;\n'
        '  models) printf "gemini-3.1-pro-high\\tGemini 3.1 Pro (High)\\n" ;;\n'
        '  *) echo "inference forbidden in this test" >&2; exit 99 ;;\n'
        "esac\n",
        encoding="utf-8",
    )
    agy.chmod(0o755)
    (vendor / "python3").symlink_to(Path(sys.executable).resolve())
    for name in ("codex", "claude"):
        presence_only = vendor / name
        presence_only.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
        presence_only.chmod(0o755)
    monkeypatch.setenv("PATH", str(vendor) + os.pathsep + os.environ["PATH"])
    monkeypatch.setenv("LIFECYCLE_TEST_CALLS", str(calls))
    return calls


def assert_cleanup_and_source(report):
    assert report["source_before"] == report["source_after"]
    assert report["source_before"]
    assert report["cleanup"]
    assert all(item["absent"] for item in report["cleanup"])
    assert all(not Path(item["path"]).exists() for item in report["cleanup"])


def test_fixed_lifecycle_cli_preserves_json_and_never_dispatches(catalog_only_vendor):
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr or result.stdout
    report = json.loads(result.stdout)
    assert report["status"] == "SUCCESS"
    assert report["failures"] == []
    assert report["payload_round_trip_verified"] is True
    assert report["integrity_stdout"].strip() == "ROUND_INTEGRITY_OK"
    steps = [command["step"] for command in report["commands"]]
    lifecycle = ["bootstrap", "prepare", "manifest", "capture", "select", "preflight", "render", "verify", "cleanup"]
    assert [step for step in steps if step in lifecycle] == lifecycle
    assert all(isinstance(command["argv"], list) for command in report["commands"])
    assert all(command["returncode"] == 0 for command in report["commands"])
    assert_cleanup_and_source(report)
    assert set(catalog_only_vendor.read_text().splitlines()) == {"--version", "models"}


def test_lifecycle_test_does_not_need_host_codex_or_claude(catalog_only_vendor, monkeypatch):
    vendor = catalog_only_vendor.parent / "vendor"
    remaining = [entry for entry in os.environ["PATH"].split(os.pathsep)
                 if Path(entry) != vendor and not any((Path(entry) / name).exists()
                                                      for name in ("codex", "claude"))]
    monkeypatch.setenv("PATH", os.pathsep.join([str(vendor), *remaining]))
    result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout or result.stderr
    assert json.loads(result.stdout)["status"] == "SUCCESS"


def test_lifecycle_documentation_states_bootstrap_prerequisites_and_write_scope():
    for name in ("README.md", "README.ko.md"):
        paragraph = (ROOT / name).read_text().split("verify_lifecycle.py", 1)[1].split("\n##", 1)[0]
        assert all(dependency in paragraph for dependency in ("Codex", "Claude", "Pydantic 2"))
    docstring = SCRIPT.read_text().split('"""', 2)[1]
    assert "All writes are confined" not in docstring
    assert "ignored" in docstring


@pytest.mark.parametrize("failure_step", ["render", "cleanup"])
def test_failure_keeps_real_exit_and_runs_postchecks(catalog_only_vendor, monkeypatch, failure_step):
    assert SCRIPT.is_file(), "bounded lifecycle verifier is missing"
    spec = importlib.util.spec_from_file_location("lifecycle_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    real_run = module.subprocess.run

    def injected_run(argv, **kwargs):
        if len(argv) > 2 and argv[2] == failure_step:
            return subprocess.CompletedProcess(argv, 17, "", "injected failure")
        return real_run(argv, **kwargs)

    monkeypatch.setattr(module.subprocess, "run", injected_run)
    report = module.verify_lifecycle()
    assert report["status"] == "WORKFLOW_DEFECT"
    failed = [command for command in report["commands"] if command["returncode"] == 17]
    assert len(failed) == 1
    assert failed[0]["step"] == failure_step
    assert "injected failure" in failed[0]["stderr"]
    assert report["failures"]
    if failure_step == "render":
        assert "verify" not in [command["step"] for command in report["commands"]]
    assert_cleanup_and_source(report)
