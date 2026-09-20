"""Actual roster adapters select supported controls before any paid inference."""
import copy
import hashlib
import importlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import review_round
from review_roster import resolve_roster


def implementation():
    assert importlib.util.find_spec("review_adapters_v2") is not None, "roster invocation adapter is required"
    return importlib.import_module("review_adapters_v2")


@pytest.fixture
def adapter_case(tmp_path, monkeypatch):
    def build():
        mod = implementation()
        cwd = tmp_path / "project"
        cwd.mkdir()
        binaries = {}
        for cli in ("claude", "agy", "gemini"):
            binary = tmp_path / cli
            binary.write_text("#!/bin/sh\nexit 0\n")
            binary.chmod(0o755)
            binaries[cli] = str(binary)
        monkeypatch.setattr(mod, "resolve_binary", lambda name: binaries.get(name))
        calls = []

        def probe(argv, *, cwd, env=None):
            calls.append(argv)
            executable = Path(argv[0]).name
            if "--version" in argv:
                return "2.1.271 (Claude Code)\n"
            if "--help" in argv:
                return "--print --model --effort --agent --no-session-persistence --permission-mode --output-format\n"
            if argv[-1] == "/model":
                return "Current model: `Opus 5 (1M context)` (effort: xhigh)\n"
            if argv[-1].startswith("/model "):
                if "bad-model" in argv:
                    return "Model not found: bad-model\n"
                if "--agent" in argv and argv[argv.index("--agent") + 1] == "missing-agent":
                    raise ValueError("agent does not exist")
                return "Set model to Opus 5 for this session only\n"
            if "--preflight-only" in argv:
                assert "--pydantic" in argv and argv[argv.index("--pydantic") + 1] == "verdict_v2:LegVerdict"
                def value(flag):
                    return argv[argv.index(flag) + 1]
                route = value("--expected-route")
                selector_file = Path(value("--google-selector-receipt"))
                selector = json.loads(selector_file.read_text())
                record = {"schema_version": 2, "review_id": value("--expected-review-id"),
                    "leg_name": value("--expected-leg-name"), "attempt": int(value("--expected-attempt")),
                    "route": route, "cwd": str(cwd), "timeout_s": int(value("--timeout")),
                    "executable": binaries[route], "provider_started": False,
                    "google_selector_receipt_sha256": hashlib.sha256(selector_file.read_bytes()).hexdigest(),
                    "model": value("--model"), "effort": value("--effort") if route == "agy" else None,
                    "route_args": ["--model", value("--model"), "--effort", value("--effort")] if route == "agy"
                                  else ["-m", value("--model")]}
                if route == "agy":
                    record["agy_version"] = "1.2.7"
                else:
                    policy = ROOT / "bin/policies/gemini-formal-readonly.toml"
                    record.update({"gemini_version": "0.60.0", "requested_approval_mode": "plan",
                        "effective_approval_mode": "unexposed", "read_only_enforcement": "packaged-mode-independent-policy",
                        "policy": str(policy), "policy_sha256": hashlib.sha256(policy.read_bytes()).hexdigest()})
                assert selector["route"] == route
                return review_round._canonical_json_bytes(record).decode()
            raise AssertionError("unexpected or inference invocation: " + str(argv))

        monkeypatch.setattr(mod, "probe", probe)
        native = {"source": "native-spawn-tool", "models": {"gpt-5.6-terra": ["high", "xhigh"], "gpt-6-astra": ["high"]},
                  "default_model": "gpt-5.6-terra", "default_effort": "high"}
        kwargs = {"review_id": "adapter-fixture", "cwd": cwd, "authentication_class": "gemini-enterprise",
                  "native_capabilities": native, "receipt_root": tmp_path / "preflight"}
        return mod, resolve_roster(cwd), kwargs, calls, binaries
    return build


def test_resolved_three_family_invocations_have_real_capability_evidence(adapter_case):
    mod, roster, kwargs, calls, _ = adapter_case()
    output = mod.prepare_adapters(roster, **kwargs)
    assert set(output) == {"claude", "codex", "google"}
    assert output["codex"]["transport_route"] == "native" and output["codex"]["binary"] is None
    assert output["claude"]["model"] == "opus" and output["claude"]["effort"] == "xhigh"
    assert output["google"]["route"] == "agy"
    assert all(item["capabilities_checked"] for item in output.values())
    assert Path(output["google"]["preflight_file"]).is_file()
    assert any("--preflight-only" in call for call in calls)
    assert not any(Path(call[0]).name == "codex" for call in calls)


def test_explicit_gemini_pin_uses_own_block_with_agy_present(adapter_case):
    mod, roster, kwargs, calls, _ = adapter_case()
    roster["legs"][2]["google"]["route"] = "gemini"
    output = mod.prepare_adapters(roster, **kwargs)
    google = output["google"]
    assert google["route"] == "gemini" and google["model"] == "gemini-3.1-pro-preview"
    call = next(call for call in calls if "--preflight-only" in call)
    assert "--effort" not in call and "gemini-3.1-pro-high" not in call


@pytest.mark.parametrize("fault", ["personal-pin", "missing-pin", "gemini-effort", "native-model", "native-effort", "native-source", "claude-agent", "claude-model", "claude-clamped-effort"])
def test_unsupported_settings_are_refused_before_paid_inference(adapter_case, fault):
    mod, roster, kwargs, calls, binaries = adapter_case()
    if fault == "personal-pin":
        kwargs["authentication_class"] = "personal-google"
        roster["legs"][2]["google"]["route"] = "gemini"
    elif fault == "missing-pin":
        roster["legs"][2]["google"]["route"] = "agy"
        binaries.pop("agy")
    elif fault == "gemini-effort":
        roster["legs"][2]["google"]["route"] = "gemini"
        roster["legs"][2]["gemini"]["effort"] = "high"
    elif fault == "native-model":
        roster["legs"][1]["codex"]["model"] = "unknown"
    elif fault == "native-effort":
        roster["legs"][1]["codex"]["reasoning"] = "ultra"
    elif fault == "native-source":
        kwargs["native_capabilities"]["source"] = "roster-guessed"
    elif fault == "claude-agent":
        roster["legs"][0]["claude"]["agent"] = "missing-agent"
    elif fault == "claude-model":
        roster["legs"][0]["claude"]["model"] = "bad-model"
    elif fault == "claude-clamped-effort":
        roster["legs"][0]["claude"]["model"] = "claude-opus-4-6"
        roster["legs"][0]["claude"]["effort"] = "xhigh"
    with pytest.raises(ValueError):
        mod.prepare_adapters(roster, **kwargs)


def test_disabled_entry_never_enters_capability_or_dispatch_probes(adapter_case):
    mod, roster, kwargs, calls, _ = adapter_case()
    roster["legs"][0]["enabled"] = False
    output = mod.prepare_adapters(roster, **kwargs)
    assert "claude" not in output
    assert not any(Path(call[0]).name == "claude" for call in calls)


def test_host_observed_native_defaults_are_frozen_for_nullable_selection(adapter_case):
    mod, roster, kwargs, _, _ = adapter_case()
    roster["legs"][1]["codex"] = {"model": None, "reasoning": None}
    output = mod.prepare_adapters(roster, **kwargs)
    assert (output["codex"]["model"], output["codex"]["effort"]) == ("gpt-5.6-terra", "high")


def test_optional_claude_agent_is_checked_without_inference(adapter_case):
    mod, roster, kwargs, calls, _ = adapter_case()
    roster["legs"][0]["claude"]["agent"] = "Plan"
    output = mod.prepare_adapters(roster, **kwargs)
    assert output["claude"]["agent"] == "Plan"
    assert any("--agent" in call and "Plan" in call for call in calls)


def test_nullable_claude_model_inspects_current_selection_without_resetting_default(adapter_case):
    mod, roster, kwargs, calls, _ = adapter_case()
    roster["legs"][0]["claude"]["model"] = None
    output = mod.prepare_adapters(roster, **kwargs)
    assert output["claude"]["model"] is None
    assert any(call[-1] == "/model" for call in calls)
    assert not any(call[-1] == "/model default" for call in calls)


def test_receipt_is_exclusive_and_retry_rechecks_its_own_attempt(adapter_case):
    mod, roster, kwargs, calls, _ = adapter_case()
    one = mod.prepare_adapters(roster, **kwargs)
    with pytest.raises(ValueError):
        mod.prepare_adapters(roster, **kwargs)
    two = mod.prepare_adapters(roster, **kwargs, attempt=2)
    assert one["google"]["preflight_file"] != two["google"]["preflight_file"]
    assert json.loads(Path(two["google"]["preflight_file"]).read_text())["attempt"] == 2
