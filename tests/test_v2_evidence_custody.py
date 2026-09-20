"""Actual wrapper persistence must retain exclusive v2 evidence on all outcomes."""
from __future__ import annotations

import json

import pytest

from test_v2_claude_wrapper import invoke
from test_v2_google_wrappers import route, ready
from test_v2_producer_adapter import binding, verdict
import _common


def evidence(cli):
    root = _common._LOG_DIR / cli
    audit = [json.loads(line) for line in (root / "audit.jsonl").read_text().splitlines()]
    paths = list((root / "runs").glob("*.json"))
    assert len(paths) == 1, "one original per-attempt provider record is required, including success"
    return audit[-1], json.loads(paths[0].read_text())


@pytest.mark.parametrize("vendor_exit", [0, 1])
def test_claude_original_provider_evidence_and_six_fields_survive_masked_audit(invoke, vendor_exit):
    rc, output, _, calls, _, expected = invoke(vendor_exit=vendor_exit)
    assert bool(rc) == bool(vendor_exit)
    audit, raw = evidence("claude")
    assert audit["review_binding"] == raw["review_binding"] == binding(expected)
    assert json.loads(raw["stdout"])["structured_output"] == expected
    assert raw["transport"] == audit["transport"]
    assert raw["transport"]["attempt"] == 2
    assert audit.get("stdout", audit.get("stdout_head")) == "<redacted>"
    assert len(calls) == 1


@pytest.mark.parametrize("vendor_exit", [0, 1])
def test_google_original_provider_evidence_owns_entry_and_attempt(route, vendor_exit):
    options, _ = ready(route)
    route["state"]["vendor_exit"] = vendor_exit
    rc, _, _ = route["invoke"](base=options)
    assert bool(rc) == bool(vendor_exit)
    audit, raw = evidence("antigravity" if route["name"] == "agy" else "gemini")
    expected = binding(verdict(route=route["name"], leg_name="google-second"))
    assert audit["review_binding"] == raw["review_binding"] == expected
    assert "google-second" in raw["stdout"]
    assert raw["transport"] == audit["transport"]
    assert audit.get("stdout", audit.get("stdout_head")) == "<redacted>"


def test_unconfigured_claude_v2_log_root_refuses_before_binary_resolution(invoke, monkeypatch):
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", False)
    rc, _, _, calls, resolutions, _ = invoke()
    assert rc == _common.EXIT_ARG_ERROR
    assert calls == resolutions == []


def test_unconfigured_google_v2_log_root_refuses_before_inference(route, monkeypatch):
    options, _ = ready(route)
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", False)
    rc, _, _ = route["invoke"](base=options)
    assert rc == _common.EXIT_ARG_ERROR and route["calls"] == []


def test_schema_failure_keeps_expected_binding_and_original_mismatched_reply(invoke):
    rc, _, _, _, _, expected = invoke(output={"leg_name": "wrong-sibling"})
    assert rc == _common.EXIT_SCHEMA_FAIL
    audit, raw = evidence("claude")
    assert raw["review_binding"] == audit["review_binding"] == binding(expected)
    assert json.loads(raw["stdout"])["structured_output"]["leg_name"] == "wrong-sibling"
    assert raw["validated"] is None


def test_legacy_success_still_writes_no_raw_run_log(tmp_path, monkeypatch):
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path)
    result = _common.RunResult(exit_code=0, stdout="legacy", stderr="", elapsed_s=0)
    assert _common.emit_run_log("claude", [], [], "prompt", result) is None
    assert list(tmp_path.iterdir()) == []
