"""C9/C10/C12/C16: real wrapper custody and schema-valid adapter boundaries."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
import _common
import review_adapters_v2
import review_round
from review_roster import resolve_roster
from test_review_round import _write_google_selector_receipt
from test_v2_adapters import adapter_case
from test_v2_google_wrappers import route, ready
from test_v2_producer_adapter import verdict
from test_v2_rounds import round_fixture, worktree, start
from test_v2_round_cli import cli_files


REAL_RUN_ONCE = _common._run_once
REAL_SUBPROCESS_RUN = subprocess.run


def test_google_actual_argv_wrapper_log_reaches_terminal_custody(round_fixture, worktree, route, monkeypatch):
    """A stdin-only collector loses healthy Google results after real argv delivery."""
    name = route["name"]
    selector = route["home"] / "collector-selector.json"
    binary = route["home"] / name
    version_probe = subprocess.run
    monkeypatch.setattr(subprocess, "run", lambda argv, **kw: version_probe(argv, **kw)
        if argv in ([str(binary), "--version"], [str(binary), "--help"])
        else REAL_SUBPROCESS_RUN(argv, **kw))
    _write_google_selector_receipt(selector, review_id="v2-fixture",
        authentication_class="personal-google" if name == "agy" else "gemini-enterprise",
        route=name, executable=binary)

    def actual_preflight(adapters):
        options = list(route["options"])
        for flag, value in (("--cwd", str(worktree)), ("--expected-review-id", "v2-fixture"),
                            ("--expected-leg-name", "google"), ("--expected-attempt", "1"),
                            ("--google-selector-receipt", str(selector))):
            options[options.index(flag) + 1] = value
        rc, output, error = route["invoke"](["--preflight-only"], base=options)
        assert rc == 0, error
        preflight = route["home"] / "collector-preflight.json"
        preflight.write_text(output)
        adapters["google"].update(route=name, transport_route=name, binary=str(binary),
            cli_version="1.2.7" if name == "agy" else "0.60.0", model=route["model"],
            effort="high" if name == "agy" else None, timeout_s=610,
            selector_file=str(selector), preflight_file=str(preflight),
            preflight_sha256=hashlib.sha256(preflight.read_bytes()).hexdigest())
        return adapters

    fixture = round_fixture(adapter_transform=actual_preflight)
    mod, basis, *_ = fixture
    item = start(fixture, "google")
    data = verdict(**item["binding"])
    envelope = ({"event": "result", "result": {"status": "SUCCESS", "response": json.dumps(data),
                                               "structured_output": data}}
                if name == "agy" else {"response": json.dumps(data)})
    # Replace only the external provider. Keep the real process, parser, wrapper,
    # persistence, public collector and immutable terminal custody in the path.
    binary.write_text(f"#!{sys.executable}\nimport json, sys\nassert '-p' in sys.argv\n"
                      f"print({json.dumps(envelope)!r})\n")
    monkeypatch.setattr(_common, "_run_once", REAL_RUN_ONCE)
    for key, value in item["invocation"]["env"].items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(_common, "_LOG_DIR", Path(item["folder"]) / "logs")
    rc, output, error = route["invoke"](base=item["invocation"]["argv"][2:])
    assert rc == 0, error
    Path(item["invocation"]["stdout_file"]).write_text(output)
    Path(item["invocation"]["stderr_file"]).write_text(error)
    logs = list((Path(item["folder"]) / "logs").glob("*/runs/*.json"))
    assert len(logs) == 1
    observed = json.loads(logs[0].read_text())
    assert observed["transport"]["stdin_delivery"] == "not-used"
    assert review_round.main(["v2-record-cli", "--basis", basis["basis_file"], "--leg", "google",
                              "--run-log", str(logs[0])]) == 0
    assert mod.collect(Path(basis["basis_file"]))["legs"]["google"]["state"] == "COMPLETE"
    assert Path(item["result_file"]).read_bytes() == output.encode()
    if name == "gemini":
        assert observed["transport"]["cli_version"] is None
        assert json.loads(Path(item["adapter"]["preflight_file"]).read_text())["gemini_version"] == "0.60.0"


def test_google_preflight_remains_separate_from_unexposed_gemini_runtime_version(route):
    options, preflight = ready(route)
    rc, _, error = route["invoke"](base=options)
    assert rc == 0, error
    cli = "antigravity" if route["name"] == "agy" else "gemini"
    logs = list((route["home"] / "logs" / cli / "runs").glob("*.json"))
    observed = json.loads(logs[0].read_text())
    if route["name"] == "gemini":
        assert observed["transport"]["cli_version"] is None
        assert json.loads(preflight.read_text())["gemini_version"] == "0.60.0"
    else:
        assert observed["transport"]["cli_version"] == "1.2.7"


@pytest.mark.parametrize("delivery", ["not-used", "unexposed", "not-started", "partial"])
def test_claude_incomplete_stdin_cannot_gain_google_delivery_exemption(round_fixture, delivery):
    fixture = round_fixture()
    mod, basis, *_ = fixture
    item = start(fixture, "claude")
    log, _ = cli_files(item, basis)
    record = json.loads(log.read_text())
    record["transport"]["stdin_delivery"] = delivery
    log.write_text(json.dumps(record))
    with pytest.raises(ValueError):
        mod.record_cli_attempt(Path(basis["basis_file"]), "claude", run_log=log)
    assert not (Path(item["folder"]) / "terminal.json").exists()


def new_entry_roster(kwargs, vendor, block):
    config = kwargs["cwd"] / ".agents" / "triad-review-legs.json"
    config.parent.mkdir()
    entry = {"name": "additional", "vendor": vendor, "enabled": True,
             "acceptance": "required", "timeout_s": 120, **block}
    config.write_text(json.dumps({"schema": "triad-review-legs.v2", "legs": [
        *({"name": name, "enabled": False} for name in ("claude", "codex", "google")), entry]}))
    return resolve_roster(kwargs["cwd"])


@pytest.mark.parametrize("vendor,block", [
    ("claude", {"claude": {"model": "opus", "effort": "xhigh"}}),
    ("claude", {"claude": {}}),
    ("codex", {"codex": {}}),
    ("google", {"agy": {}}),
])
def test_new_names_preserve_documented_omitted_selection_defaults(adapter_case, vendor, block):
    mod, _, kwargs, calls, _ = adapter_case()
    roster = new_entry_roster(kwargs, vendor, block)
    result = mod.prepare_adapters(roster, **kwargs)["additional"]
    assert result["capabilities_checked"] is True
    if vendor == "codex":
        assert (result["model"], result["effort"]) == ("gpt-5.6-terra", "high")
    elif vendor == "claude":
        assert result["agent"] is None
        assert result["model"] == block["claude"].get("model")
        assert result["effort"] == block["claude"].get("effort")
        assert result["selected_model"] == "claude-opus-5-5"
        assert not any("--agent" in call for call in calls)
    else:
        assert (result["route"], result["model"], result["effort"]) == ("agy", "gemini-3.1-pro-high", "high")


@pytest.mark.parametrize("fault", ["selected-route-missing", "empty-claude-selection", "native-default-unexposed"])
def test_preparation_refusals_keep_evidence_for_schema_valid_inputs(adapter_case, monkeypatch, fault):
    mod, _, kwargs, _, _ = adapter_case()
    if fault == "selected-route-missing":
        roster = new_entry_roster(kwargs, "google", {"gemini": {}})
    elif fault == "empty-claude-selection":
        roster = new_entry_roster(kwargs, "claude", {"claude": {"agent": None, "model": None, "effort": None}})
        probe = mod.probe
        monkeypatch.setattr(mod, "probe", lambda argv, **kw: "Current model: " if argv[-1] == "/model" else probe(argv, **kw))
    else:
        roster = new_entry_roster(kwargs, "codex", {"codex": {}})
        kwargs["native_capabilities"].pop("default_model")
    with pytest.raises(ValueError):
        mod.prepare_adapters(roster, **kwargs)
    receipt = kwargs["receipt_root"] / "additional" / "attempt-1" / "preparation-failure.json"
    evidence = json.loads(receipt.read_text())
    assert evidence["leg_name"] == "additional" and evidence["provider_started"] is False
    assert evidence["error"]
    assert not receipt.with_name("adapter.json").exists()
