"""Use each actual Google wrapper through preflight, producer and audit custody."""
from __future__ import annotations

import contextlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common
import antigravity_wrapper as agy
import gemini_wrapper as gemini
from test_review_round import _fake_executable, _write_google_selector_receipt
from test_v2_producer_adapter import verdict


@pytest.fixture(params=["agy", "gemini"])
def route(request, tmp_path, monkeypatch, capsys):
    name = request.param
    wrapper = agy if name == "agy" else gemini
    home = tmp_path.resolve()
    executable = home / name
    _fake_executable(executable)
    selector = home / "selector.json"
    _write_google_selector_receipt(selector, review_id="round-2",
        authentication_class="personal-google" if name == "agy" else "gemini-enterprise",
        route=name, executable=executable)
    monkeypatch.setattr(_common, "_LOG_DIR", home / "logs")
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", True)
    monkeypatch.setenv("TRIAD_WRAPPER_ALLOWED_ROOTS", str(home))
    monkeypatch.setenv("TRIAD_WRAPPER_HARDENED", "1")
    model = "gemini-3.1-pro-high" if name == "agy" else "gemini-3.1-pro-preview"
    calls, guards = [], []

    def guard(rules, **kwargs):
        guards.append(rules)
        return contextlib.nullcontext()

    monkeypatch.setattr(agy._agy_settings, "agy_settings_guard", guard)
    monkeypatch.setattr(agy, "_probe_agy_version", lambda _: (1, 2, 7))
    monkeypatch.setattr(agy, "_probe_agy_models", lambda _: {model})

    def probe(cmd, **kwargs):
        assert cmd in ([str(executable), "--version"], [str(executable), "--help"])
        text = "0.60.0\n" if cmd[-1] == "--version" else (
            '  -m, --model Model [string]\n'
            '  --approval-mode Set the approval mode [choices: "default", "plan"]\n'
            '  --policy Additional policy files or directories to load [array]\n')
        return subprocess.CompletedProcess(cmd, 0, text, "")

    monkeypatch.setattr(gemini.subprocess, "run", probe)
    state = {"output": {}, "vendor_exit": 0}

    def provider(cli, cmd, cwd, timeout, **kwargs):
        calls.append((cmd, cwd, timeout, kwargs))
        data = {**verdict(route=name, leg_name="google-second"), **state["output"]}
        envelope = ({"event": "result", "result": {"status": "SUCCESS", "response": json.dumps(data),
                                                      "structured_output": data}}
                    if name == "agy" else {"response": json.dumps(data)})
        return _common.RunResult(exit_code=state["vendor_exit"], vendor_exit_code=state["vendor_exit"],
                                 stdout=json.dumps(envelope), stderr="", elapsed_s=0.1)

    monkeypatch.setattr(_common, "_run_once", provider)
    options = ["--prompt", "preflight", "--cwd", str(home), "--timeout", "610",
               "--model", model, "--pydantic", "verdict_v2:LegVerdict",
               "--expected-review-id", "round-2", "--expected-leg-name", "google-second",
               "--expected-attempt", "2", "--expected-route", name,
               "--google-selector-receipt", str(selector)]
    if name == "agy":
        options += ["--effort", "high", "--sandbox", "read-only"]

    def invoke(extra=(), *, base=None):
        monkeypatch.setattr(sys, "argv", [str(wrapper.__file__), *(options if base is None else base), *extra])
        try:
            rc = wrapper.main()
        except SystemExit as error:
            rc = error.code
        output = capsys.readouterr()
        return rc, output.out, output.err

    return dict(name=name, home=home, model=model, calls=calls, guards=guards,
                state=state, options=options, invoke=invoke, selector=selector)


def ready(route):
    rc, output, error = route["invoke"](["--preflight-only"])
    assert rc == 0, error
    assert route["calls"] == []
    receipt = json.loads(output)
    assert receipt["schema_version"] == 2
    assert receipt["model"] == route["model"]
    assert receipt["leg_name"] == "google-second" and receipt["attempt"] == 2
    assert receipt["cwd"] == str(route["home"]) and receipt["timeout_s"] == 610
    assert receipt["provider_started"] is False
    file = route["home"] / "preflight.json"
    file.write_text(output)
    import hashlib
    metadata = {**{key: verdict(route=route["name"], leg_name="google-second")[key]
                  for key in ("review_id", "family", "content_digest", "leg_name", "attempt", "route")},
                "google_preflight_receipt_sha256": hashlib.sha256(file.read_bytes()).hexdigest()}
    options = list(route["options"])
    options[options.index("--prompt") + 1] = "Review v2 metadata: " + json.dumps(metadata, sort_keys=True) + "\nRead the bound source."
    options += ["--expected-family", "google", "--expected-content-digest", "a" * 64,
                "--google-preflight-receipt", str(file)]
    return options, file


def test_v2_preflight_is_provider_free_and_actual_dispatch_uses_requested_settings(route):
    options, _ = ready(route)
    rc, output, error = route["invoke"](base=options)
    assert rc == 0, error
    assert json.loads(output)["attempt"] == 2
    assert len(route["calls"]) == 1
    cmd, cwd, timeout, kwargs = route["calls"][0]
    model_flag = "--model" if route["name"] == "agy" else "-m"
    assert cmd[cmd.index(model_flag) + 1] == route["model"]
    assert cwd == str(route["home"]) and timeout == 610
    assert kwargs["remove_env"]
    if route["name"] == "gemini":
        assert "--policy" in cmd and cmd[cmd.index("--approval-mode") + 1] == "plan"
    else:
        assert "--skip-permissions" not in cmd
        assert route["guards"]
    cli = "antigravity" if route["name"] == "agy" else "gemini"
    record = json.loads((route["home"] / "logs" / cli / "audit.jsonl").read_text())
    assert record["transport"]["attempt"] == 2
    assert record["transport"]["cli_version"] == ("1.2.7" if route["name"] == "agy" else None)


@pytest.mark.parametrize("change", [{"leg_name": "sibling"}, {"attempt": 1}, {"open_questions": ["missing source"]}])
def test_v2_output_binding_and_full_schema_reject_without_schema_retry(route, change):
    options, _ = ready(route)
    route["state"]["output"] = change
    rc, output, _ = route["invoke"](base=options)
    assert rc == _common.EXIT_SCHEMA_FAIL
    assert output == "" and len(route["calls"]) == 1


@pytest.mark.parametrize("field,value", [
    ("leg_name", "sibling"), ("attempt", 1), ("timeout_s", 600),
    ("model", "different"), ("cwd", "/different"), ("provider_started", True),
])
def test_sibling_or_changed_preflight_cannot_authorize_inference(route, field, value):
    options, file = ready(route)
    payload = json.loads(file.read_text())
    payload[field] = value
    file.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    rc, _, _ = route["invoke"](base=options)
    assert rc == _common.EXIT_ARG_ERROR and route["calls"] == []


def test_v2_prompt_metadata_is_checked_before_inference(route):
    options, _ = ready(route)
    options[options.index("--prompt") + 1] = "unbound prompt"
    rc, _, _ = route["invoke"](base=options)
    assert rc == _common.EXIT_ARG_ERROR and route["calls"] == []


def test_review_web_is_not_implied_by_v2_preflight(route):
    rc, output, _ = route["invoke"](["--preflight-only"])
    assert rc == 0 and route["calls"] == []
    assert json.loads(output).get("review_web_authorized", False) is False


def test_v2_unknown_requested_model_refuses_before_inference(route):
    options = list(route["options"])
    options[options.index("--model") + 1] = "not-an-installed-model"
    rc, _, _ = route["invoke"](["--preflight-only"], base=options)
    assert rc != 0 and route["calls"] == []
