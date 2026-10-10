"""Owner's common Gemini 0.63.0 boundary, independent of model catalogs."""
import json
import subprocess
import sys

import pytest

from test_provider_wrappers import _common, _ok, gemini_wrapper
from test_gemini_version_floor import _probe, version_case
from test_v2_google_wrappers import ready, route


@pytest.mark.parametrize("version", ["0.34.0", "0.60.0", "0.61.0", "0.62.9", "0.63.0-preview.1"])
def test_C18_old_gemini_refuses_before_help_or_inference(version_case, monkeypatch, capsys, version):
    rc, calls = _probe(version_case, monkeypatch, version=version)
    assert rc == _common.EXIT_ARG_ERROR
    assert [cmd[-1] for cmd, _ in calls] == ["--version"]
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("version,accepted", [("0.62.9", False), ("0.63.0-preview.1", False),
    ("0.63.0", True), ("0.63.0+build.1", True), ("0.64.0", True)])
def test_C18_raw_gemini_support_floor(tmp_path, monkeypatch, capsys, version, accepted):
    calls = []
    monkeypatch.setattr(gemini_wrapper, "require_binary", lambda _: "/selected/gemini")
    def probe(argv, **kwargs):
        assert argv == ["/selected/gemini", "--version"]
        assert "GEMINI_API_KEY" not in kwargs["env"]
        return subprocess.CompletedProcess(argv, 0, version + "\n", "")
    monkeypatch.setattr(gemini_wrapper.subprocess, "run", probe)
    monkeypatch.setattr(gemini_wrapper, "run_cli_with_retry", lambda *a, **kw: calls.append(a) or _ok())
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(sys, "argv", ["gemini_wrapper.py", "--prompt", "read only", "--cwd", str(tmp_path)])
    rc = gemini_wrapper.main()
    assert (rc == 0) is accepted
    assert len(calls) == int(accepted)
    if not accepted:
        assert rc == _common.EXIT_ARG_ERROR
        assert "0.63.0" in capsys.readouterr().err


@pytest.mark.parametrize("failure", ["nonzero", "timeout", "oserror"])
def test_C18_raw_version_probe_failure_refuses_without_inference(tmp_path, monkeypatch, capsys, failure):
    calls = []
    monkeypatch.setattr(gemini_wrapper, "require_binary", lambda _: "/selected/gemini")
    def probe(argv, **kwargs):
        assert argv == ["/selected/gemini", "--version"]
        if failure == "timeout":
            raise subprocess.TimeoutExpired(argv, 15)
        if failure == "oserror":
            raise OSError("synthetic version probe failure")
        return subprocess.CompletedProcess(argv, 1, "0.63.0\n", "synthetic failure")
    monkeypatch.setattr(gemini_wrapper.subprocess, "run", probe)
    monkeypatch.setattr(gemini_wrapper, "run_cli_with_retry", lambda *a, **kw: calls.append(a) or _ok())
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(sys, "argv", ["gemini_wrapper.py", "--prompt", "read only", "--cwd", str(tmp_path)])
    assert gemini_wrapper.main() == _common.EXIT_ARG_ERROR
    assert calls == []
    assert "Gemini version check failed" in capsys.readouterr().err


def test_C18_v2_unlisted_pin_is_not_a_catalog_gate(route):
    route["model"] = "future-user-pinned-model"
    route["options"][route["options"].index("--model") + 1] = route["model"]
    route["state"]["gemini_version"] = "0.63.0"
    options, _ = ready(route)
    rc, output, error = route["invoke"](base=options)
    assert rc == 0, error
    assert json.loads(output)["attempt"] == 2
    assert len(route["calls"]) == 1
    cmd = route["calls"][0][0]
    if route["name"] == "agy":
        assert cmd[cmd.index("--model") + 1] == route["model"]
    else:
        assert "--model=" + route["model"] in cmd
