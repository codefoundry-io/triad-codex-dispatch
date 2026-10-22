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
    monkeypatch.setenv("AGY_SETTINGS_PATH", str(home / "agy-settings.json"))
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
    model = "gemini-4-argon-high" if name == "agy" else "gemini-3.1-pro-preview"
    calls = []


    monkeypatch.setattr(agy, "_probe_agy_version", lambda _: (1, 2, 7))

    state = {"output": {}, "vendor_exit": 0, "gemini_version": "0.63.0"}

    def probe(cmd, **kwargs):
        assert cmd in ([str(executable), "--version"], [str(executable), "--help"])
        text = state["gemini_version"] + "\n" if cmd[-1] == "--version" else (
            '  -m, --model Model [string]\n'
            '  --approval-mode Set the approval mode [choices: "default", "plan"]\n'
            '  --policy Additional policy files or directories to load [array]\n'
            '  --include-directories Additional directories to include in the workspace [array]\n')
        return subprocess.CompletedProcess(cmd, 0, text, "")

    monkeypatch.setattr(gemini.subprocess, "run", probe)

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

    return dict(name=name, home=home, model=model, calls=calls,
                state=state, options=options, invoke=invoke, selector=selector)


def ready(route, *, web=False):
    rc, output, error = route["invoke"](["--preflight-only", *(["--web"] if web else [])])
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
    options = [*route["options"], *(["--web"] if web else [])]
    if web:
        metadata["review_web_authorized"] = True
    options[options.index("--prompt") + 1] = "Review v2 metadata: " + json.dumps(metadata, sort_keys=True) + "\nRead the bound source."
    options += ["--expected-family", "google", "--expected-content-digest", "a" * 64,
                "--google-preflight-receipt", str(file)]
    return options, file


@pytest.mark.parametrize("route", ["agy"], indirect=True)
@pytest.mark.parametrize("ambient", ['{"permissions":{"deny":["read_url(*)"]}}', 'malformed'])
def test_web_fixture_is_independent_of_ambient_settings(route, monkeypatch, ambient):
    owner_settings = route["home"] / "owner-settings.json"
    owner_settings.write_text(ambient)
    monkeypatch.setattr(agy._agy_settings, "_DEFAULT_PATH", owner_settings)
    options, _ = ready(route, web=True)
    rc, _, error = route["invoke"](base=options)
    assert rc == 0, error
    assert len(route["calls"]) == 1
    assert owner_settings.read_text() == ambient


def test_v2_preflight_is_provider_free_and_actual_dispatch_uses_requested_settings(route):
    options, _ = ready(route)
    rc, output, error = route["invoke"](base=options)
    assert rc == 0, error
    assert json.loads(output)["attempt"] == 2
    assert len(route["calls"]) == 1
    cmd, cwd, timeout, kwargs = route["calls"][0]
    if route["name"] == "agy":
        assert cmd[cmd.index("--model") + 1] == route["model"]
    else:
        assert "--model=" + route["model"] in cmd
    assert cwd == str(route["home"]) and timeout == 610
    assert kwargs["remove_env"]
    if route["name"] == "gemini":
        assert "--policy" in cmd and cmd[cmd.index("--approval-mode") + 1] == "plan"
    else:
        assert "--skip-permissions" not in cmd
        assert cmd[cmd.index("--agent") + 1] == "triad-codex-readonly-review"
        assert "--dangerously-skip-permissions" not in cmd
    cli = "antigravity" if route["name"] == "agy" else "gemini"
    record = json.loads((route["home"] / "logs" / cli / "audit.jsonl").read_text())
    assert record["transport"]["attempt"] == 2
    assert record["transport"]["cli_version"] == ("1.2.7" if route["name"] == "agy" else None)


@pytest.mark.parametrize("route", ["agy"], indirect=True)
def test_agy_metadata_is_projected_after_bound_v2_admission_and_retained_in_raw_log(route):
    options, _ = ready(route)
    route["state"]["output"] = {"toolAction": "finish", "toolSummary": {"done": True}}
    rc, output, error = route["invoke"](base=options)
    assert rc == 0, error
    expected = verdict(route="agy", leg_name="google-second")
    assert json.loads(output) == expected
    files = list((route["home"] / "logs" / "antigravity" / "runs").glob("*.json"))
    assert len(files) == 1
    record = json.loads(files[0].read_text())
    raw = json.loads(record["stdout"])["result"]["structured_output"]
    assert raw == {**expected, "toolAction": "finish", "toolSummary": {"done": True}}
    assert record["validated"] == expected
    assert json.loads(record["final_answer"]) == expected


@pytest.mark.parametrize("route", ["agy"], indirect=True)
@pytest.mark.parametrize("change", [
    {"review_id": "other"}, {"family": "claude"}, {"content_digest": "b" * 64},
    {"leg_name": "sibling"}, {"attempt": 1}, {"route": "gemini"},
    {"unexpected": "extra"}, {"verdict": None},
])
def test_agy_metadata_does_not_bypass_v2_schema_or_any_binding(route, change):
    options, _ = ready(route)
    route["state"]["output"] = {"toolAction": "finish", "toolSummary": "done", **change}
    rc, output, _ = route["invoke"](base=options)
    assert rc == _common.EXIT_SCHEMA_FAIL
    assert output == "" and len(route["calls"]) == 1


@pytest.mark.parametrize("model", ["gemini-4-argon-high", "gemini-3.8-flash-high", "gemini-3.1-pro-high"])
def test_agy_explicit_models_emit_singleton_bound_route_schema(route, model, monkeypatch):
    if route["name"] != "agy":
        pytest.skip("AGY JSON schema transport contract")
    route["model"] = model
    route["options"][route["options"].index("--model") + 1] = model
    options, _ = ready(route)
    rc, output, error = route["invoke"](base=options)
    assert rc == 0, error
    assert json.loads(output)["route"] == "agy"
    assert len(route["calls"]) == 1
    cmd = route["calls"][0][0]
    assert cmd[cmd.index("--model") + 1] == model
    emitted = json.loads(cmd[cmd.index("--json-schema") + 1])
    assert emitted["properties"]["route"] == {
        "enum": ["agy"], "const": "agy",
    }


def test_gemini_38_exact_model_reaches_actual_wrapper_dispatch(route):
    if route["name"] != "gemini":
        pytest.skip("Gemini CLI model contract")
    route["model"] = "gemini-3.8-flash"
    route["options"][route["options"].index("--model") + 1] = "gemini-3.8-flash"
    route["state"]["gemini_version"] = "0.63.0"
    options, _ = ready(route)
    rc, output, error = route["invoke"](base=options)
    assert rc == 0, error
    assert json.loads(output)["attempt"] == 2
    assert len(route["calls"]) == 1
    cmd = route["calls"][0][0]
    assert "--model=gemini-3.8-flash" in cmd
    assert "--effort" not in cmd


def test_gemini_effort_refuses_before_provider(route):
    if route["name"] != "gemini":
        pytest.skip("Gemini CLI effort contract")
    rc, output, _ = route["invoke"](["--preflight-only", "--effort", "high"])
    assert rc == 2  # argparse refuses the unsupported CLI option.
    assert output == "" and route["calls"] == []


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


@pytest.mark.parametrize("route", ["gemini"], indirect=True)
@pytest.mark.parametrize("version", ["0.60.0", "0.62.9", "0.63.0-preview.1"])
def test_v2_consumption_refuses_stale_gemini_version(route, version):
    from types import SimpleNamespace
    import google_preflight_v2
    import review_round

    _, file = ready(route)
    selector = review_round.load_google_selector_receipt(
        route["selector"], expected_review_id="round-2", expected_route="gemini",
        expected_wrapper=Path(gemini.__file__))
    args = SimpleNamespace(expected_review_id="round-2", expected_leg_name="google-second",
        expected_attempt=2, expected_route="gemini", timeout=610, model=route["model"])
    original = google_preflight_v2.load_preflight(file, selector, args, str(route["home"]))
    assert original["gemini_version"] == "0.63.0"
    file.write_bytes(review_round._canonical_json_bytes({**original, "gemini_version": version}))
    with pytest.raises(ValueError, match="CLI >=0.63.0"):
        google_preflight_v2.load_preflight(file, selector, args, str(route["home"]))
    assert route["calls"] == []


@pytest.mark.parametrize("route", ["agy"], indirect=True)
@pytest.mark.parametrize("version,accepted", [("1.1.20", False), ("1.2.0", False), ("1.2.1", True)])
def test_v2_agy_receipt_uses_readonly_version_floor(route, version, accepted):
    from types import SimpleNamespace
    import google_preflight_v2
    import review_round

    _, file = ready(route)
    selector = review_round.load_google_selector_receipt(
        route["selector"], expected_review_id="round-2", expected_route="agy",
        expected_wrapper=Path(agy.__file__))
    args = SimpleNamespace(expected_review_id="round-2", expected_leg_name="google-second",
        expected_attempt=2, expected_route="agy", timeout=610, model=route["model"], effort="high")
    record = json.loads(file.read_text())
    record["agy_version"] = version
    file.write_bytes(review_round._canonical_json_bytes(record))
    if accepted:
        assert google_preflight_v2.load_preflight(file, selector, args, str(route["home"]))["agy_version"] == version
    else:
        with pytest.raises(ValueError, match="version"):
            google_preflight_v2.load_preflight(file, selector, args, str(route["home"]))
    assert route["calls"] == []


def test_review_web_is_not_implied_by_v2_preflight(route):
    rc, output, _ = route["invoke"](["--preflight-only"])
    assert rc == 0 and route["calls"] == []
    assert json.loads(output).get("review_web_authorized", False) is False


def test_v2_unknown_requested_model_preflight_preserves_pin(route):
    options = list(route["options"])
    options[options.index("--model") + 1] = "not-an-installed-model"
    rc, output, error = route["invoke"](["--preflight-only"], base=options)
    assert rc == 0, error
    assert json.loads(output)["model"] == "not-an-installed-model"
    assert route["calls"] == []


@pytest.mark.parametrize("phase", ["formal-plan", "pre-merge", "implementation-review"])
@pytest.mark.parametrize("web", [False, True])
def test_C60_rendered_google_phase_metadata_reaches_wrapper(route, phase, web):
    import hashlib
    from test_v2_review_prompts import arguments, renderer
    options, receipt = ready(route, web=web)
    args = arguments(route["home"], "google")
    original = json.loads(options[options.index("--prompt") + 1].splitlines()[0].split(": ", 1)[1])
    args["expected"] = {key: original[key] for key in
                        ("review_id", "family", "content_digest", "leg_name", "attempt", "route")}
    args["google_preflight_sha256"] = hashlib.sha256(receipt.read_bytes()).hexdigest()
    options[options.index("--prompt") + 1] = renderer().render_prompt(
        **args, review_kind=phase, review_web_authorized=web)
    rc, output, error = route["invoke"](base=options)
    assert rc == 0, error
    assert json.loads(output)["attempt"] == 2
    assert len(route["calls"]) == 1


@pytest.mark.parametrize("change", [
    {"review_kind": None}, {"review_kind": "unknown"}, {"review_kind": False},
    {"review_kind": 1}, {"review_kind": []}, {"review_kind": {}},
    {"review_kind": "pre-merge", "unrelated": True},
])
def test_C60_invalid_or_extra_google_metadata_refuses_before_provider(route, change):
    options, _ = ready(route)
    prompt = options[options.index("--prompt") + 1]
    metadata = json.loads(prompt.splitlines()[0].split(": ", 1)[1])
    metadata.update(change)
    options[options.index("--prompt") + 1] = "Review v2 metadata: " + json.dumps(metadata) + "\nRead the bound source."
    rc, _, _ = route["invoke"](base=options)
    assert rc == _common.EXIT_ARG_ERROR and route["calls"] == []
