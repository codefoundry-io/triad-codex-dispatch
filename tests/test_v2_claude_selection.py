"""Selection observations are evidence, never a model availability catalog."""
import json
from pathlib import Path

import pytest

from test_v2_adapters import adapter_case


def selection_case(adapter_case, monkeypatch, model, output, *, models=None):
    mod, roster, kwargs, calls, _ = adapter_case()
    roster["legs"][0]["claude"]["model"] = model
    original = mod.probe
    def probe(argv, **kw):
        if argv[-1].startswith("/model"):
            calls.append(argv)
            return output
        return original(argv, **kw)
    monkeypatch.setattr(mod, "probe", probe)
    if models is not None:
        read = mod._json
        def without_catalog(value):
            document = read(value)
            if isinstance(document, dict) and "minimum_preflight_version" in document:
                document["models"] = models
            return document
        monkeypatch.setattr(mod, "_json", without_catalog)
    return mod, roster, kwargs, calls


@pytest.mark.parametrize("model,reported", [
    ("opus", "Sonnet 5"), ("sonnet", "Opus 5.5"),
    ("claude-opus-5-5", "Opus 5"), ("claude-opus-5", "Opus 5.5"),
    ("claude-opus-5-5", "Sonnet 5"),
    ("opus", "claude-sonnet-5"),
    ("claude-opus-5-5-20261001", "claude-opus-5-5-20261002"),
    ("claude-opus-5-5", "claude-opus-5-5-20261001"),
    ("opus", "Sonnet 5 (effort: xhigh)"),
    ("claude-opus-5-5", "Sonnet 5 (effort: xhigh)"),
    ("opus", "Sonnet 5 additional annotation"),
    ("claude-opus-5-5", "Opus 5 additional annotation"),
    ("opus[1m]", "Sonnet 5"),
    ("opus[1m]", "claude-sonnet-5[1m] additional annotation"),
])
def test_C34_observed_identity_mismatch_refuses_without_catalog(adapter_case, monkeypatch, model, reported):
    mod, roster, kwargs, _ = selection_case(adapter_case, monkeypatch, model,
        f"Set model to {reported} for this session only\n", models={})
    with pytest.raises(ValueError, match="substituted a different requested model"):
        mod.prepare_adapters(roster, **kwargs)


@pytest.mark.parametrize("model,reported", [
    ("opus", "Opus 5.5"), ("claude-opus-5-5", "Opus 5.5"),
    ("future-user-pin", "Unlisted provider label"),
])
def test_R_MODEL_catalog_absence_does_not_refuse_or_invent_identity(adapter_case, monkeypatch, model, reported):
    mod, roster, kwargs, calls = selection_case(adapter_case, monkeypatch, model,
        f"Set model to {reported} for this session only\n", models={})
    result = mod.prepare_adapters(roster, **kwargs)["claude"]
    assert (result["model"], result["effort"]) == (model, "xhigh")
    assert result["selected_model"] == reported
    assert result["capability_scope"] == "cli-selection"
    assert result["provider_started"] is False
    assert any(call[-1] == "/model " + model and call[call.index("--model") + 1] == model for call in calls)
    receipt = json.loads(Path(result["capability_file"]).read_text())
    assert receipt["selection_output"] == f"Set model to {reported} for this session only\n"


def test_R_MODEL_stale_effort_catalog_is_not_capability_evidence(adapter_case, monkeypatch):
    mod, roster, kwargs, _ = selection_case(adapter_case, monkeypatch, "claude-opus-5-5",
        "Set model to Opus 5.5 for this session only\n",
        models={"Opus 5.5": {"id": "claude-opus-5-5", "efforts": ["low"]}})
    result = mod.prepare_adapters(roster, **kwargs)["claude"]
    assert result["effort"] == "xhigh"
    assert result["capability_scope"] == "cli-selection"


@pytest.mark.parametrize("tail", ["", "Additional information\n", "Additional information (effort: low)\n"])
@pytest.mark.parametrize("effort,accepted", [("xhigh", True), ("high", False)])
def test_C34_observed_effort_is_checked_without_inventing_support(adapter_case, monkeypatch, effort, accepted, tail):
    mod, roster, kwargs, _ = selection_case(adapter_case, monkeypatch, None,
        f"Current model: `Opus 5.5 (1M context)` (effort: {effort})\n{tail}", models={})
    if not accepted:
        with pytest.raises(ValueError, match="different requested effort"):
            mod.prepare_adapters(roster, **kwargs)
        return
    result = mod.prepare_adapters(roster, **kwargs)["claude"]
    assert result["model"] is None
    assert result["selected_model"] == "Opus 5.5 (1M context)"


@pytest.mark.parametrize("model,reported", [
    ("opus[1m]", "Opus 5.5 (effort: xhigh)"),
    ("claude-opus-5-5", "claude-opus-5-5 (effort: xhigh)"),
])
def test_matching_set_identity_with_effort_annotation(adapter_case, monkeypatch, model, reported):
    mod, roster, kwargs, _ = selection_case(adapter_case, monkeypatch, model,
        f"Set model to {reported}\nAdditional information\n")
    result = mod.prepare_adapters(roster, **kwargs)["claude"]
    assert result["model"] == model
    assert result["selected_model"] == "claude-opus-5-5"


def test_effort_on_unrelated_trailing_line_is_not_selection_evidence(adapter_case, monkeypatch):
    mod, roster, kwargs, _ = selection_case(adapter_case, monkeypatch, None,
        "Current model: `Opus 5.5`\nAdditional information (effort: low)\n")
    assert mod.prepare_adapters(roster, **kwargs)["claude"]["effort"] == "xhigh"


def test_wrapper_effort_vocabulary_is_checked_before_vendor_probe(adapter_case):
    mod, roster, kwargs, calls, _ = adapter_case()
    roster["legs"][0]["claude"]["effort"] = "future-effort"
    with pytest.raises(ValueError, match="Claude wrapper.*effort"):
        mod.prepare_adapters(roster, **kwargs)
    assert calls == []


@pytest.mark.parametrize("label", ["Unlisted provider label", "Opus 5 experimental", "[1m]"])
def test_unknown_label_is_retained_without_known_identity_claim(adapter_case, monkeypatch, label):
    mod, roster, kwargs, _ = selection_case(adapter_case, monkeypatch, "future-user-pin",
        f"Set model to {label} for this session only\n")
    result = mod.prepare_adapters(roster, **kwargs)["claude"]
    assert result["selected_model"] == label
    assert result["model"] == "future-user-pin"


def test_historical_21282_session_only_capture(adapter_case, monkeypatch):
    # Captured on 2026-09-25 with explicit claude-opus-5-5 / xhigh.
    output = "Set model to `Opus 5.5` for this session only\n"
    mod, roster, kwargs, _ = selection_case(adapter_case, monkeypatch, "claude-opus-5-5", output)
    result = mod.prepare_adapters(roster, **kwargs)["claude"]
    assert result["selected_model"] == "claude-opus-5-5"
    assert json.loads(Path(result["capability_file"]).read_text())["selection_output"] == output
