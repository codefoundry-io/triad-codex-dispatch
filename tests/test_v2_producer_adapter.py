"""P3: the wrapper producer consumes, but never replaces, the shared schema."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common
from validate_v2 import BINDING_FIELDS, load_contracts, validate_verdict


def adapter():
    assert (ROOT / "bin/verdict_v2.py").is_file(), "P3 canonical-schema producer adapter is missing"
    return importlib.import_module("verdict_v2")


def verdict(**changes):
    return {
        "schema_version": 2, "review_id": "round-2", "family": "google",
        "content_digest": "a" * 64, "leg_name": "google-trial", "attempt": 2,
        "route": "agy", "verdict": "SAFE TO MERGE", "criteria_checked": ["correctness"],
        "findings": [], "affected_surfaces_inspected": ["src/a.py"], "open_questions": [],
        **changes,
    }


def binding(data):
    return {name: data[name] for name in BINDING_FIELDS}


def test_packaged_v2_adapter_loads_under_hardened_mode_without_arbitrary_import_permission(monkeypatch):
    adapter()
    monkeypatch.setenv("TRIAD_WRAPPER_HARDENED", "1")
    monkeypatch.delenv("TRIAD_ALLOW_PYDANTIC_IMPORT", raising=False)
    cls = _common.load_pydantic_class("verdict_v2:LegVerdict")
    ok, result = _common.validate_response(json.dumps(verdict()), cls)
    assert ok and result == verdict()
    assert cls.model_json_schema() == load_contracts()["leg-verdict.schema.json"]


@pytest.mark.parametrize("changes", [
    {"family": "codex", "route": None},
    {"family": "claude", "route": None},
    {"route": "gemini"},
    {"verdict": "DO NOT MERGE", "open_questions": ["Required source missing"]},
    {"verdict": "MERGE WITH FIXES", "findings": [{
        "severity": "Minor", "path": "src/a.py", "line": None,
        "summary": "Diagnostic label", "trigger": "Invalid input", "evidence": "src/a.py:1",
        "context_known": True,
    }]},
])
def test_full_schema_accepts_exact_valid_original_values(changes):
    data = verdict(**changes)
    cls = adapter().bound_verdict(binding(data))
    ok, result = _common.validate_response(json.dumps(data), cls)
    assert ok and result == data
    assert validate_verdict(json.dumps(result), expected=binding(data)) == data


@pytest.mark.parametrize("field,value", [
    ("review_id", "other"), ("family", "claude"), ("content_digest", "b" * 64),
    ("leg_name", "sibling"), ("attempt", 1), ("route", "gemini"),
])
def test_bound_producer_rejects_all_six_identity_swaps(field, value):
    data = verdict()
    cls = adapter().bound_verdict(binding(data))
    data[field] = value
    ok, error = _common.validate_response(json.dumps(data), cls)
    assert not ok, f"accepted a different {field}: {error}"


@pytest.mark.parametrize("changes", [
    {"attempt": True}, {"attempt": 0}, {"leg_name": "../escape"}, {"route": None},
    {"schema_version": 1}, {"verdict": "SAFE"}, {"criteria_checked": []},
    {"criteria_checked": ["same", "same"]}, {"affected_surfaces_inspected": ["../secret"]},
    {"open_questions": ["unresolved"]}, {"verdict": "DO NOT MERGE"}, {"unknown": "field"},
])
def test_local_adapter_does_not_relax_full_admission_contract(changes):
    cls = adapter().LegVerdict
    ok, error = _common.validate_response(json.dumps(verdict(**changes)), cls)
    assert not ok, f"invalid full-contract output accepted: {error}"


@pytest.mark.parametrize("field", BINDING_FIELDS)
def test_original_duplicate_bindings_rejected_before_lossy_parse(field):
    cls = adapter().LegVerdict
    data = verdict()
    raw = json.dumps(data)
    duplicate = raw[:-1] + "," + json.dumps(field) + ":" + json.dumps(data[field]) + "}"
    ok, _ = _common.validate_response(duplicate, cls)
    assert not ok
    with pytest.raises(ValueError):
        cls.model_validate_json(duplicate)
    with pytest.raises(ValueError):
        _common._check_original_json('{"structured_output":' + duplicate + '}', cls)


def test_binding_does_not_mutate_shared_schema_or_other_invocations():
    module = adapter()
    original = load_contracts()["leg-verdict.schema.json"]
    first = binding(verdict())
    second = binding(verdict(leg_name="sibling", attempt=3))
    a, b = module.bound_verdict(first), module.bound_verdict(second)
    for cls, expected in ((a, first), (b, second)):
        for field in BINDING_FIELDS:
            assert cls.model_json_schema()["properties"][field]["const"] == expected[field]
    assert module.LegVerdict.model_json_schema() == original
    assert load_contracts()["leg-verdict.schema.json"] == original


def test_malformed_expected_binding_refuses_before_generation():
    module = adapter()
    for bad in ({}, {**binding(verdict()), "attempt": True},
                {**binding(verdict()), "extra": 1}, {**binding(verdict()), "route": None}):
        with pytest.raises(ValueError):
            module.bound_verdict(bad)


def test_cli_projection_removes_only_observed_unsupported_top_level_constraints():
    module = adapter()
    cls = module.bound_verdict(binding(verdict()))
    complete = cls.model_json_schema()
    generated = module.producer_schema(cls)
    assert set(complete) - set(generated) == {"$schema", "$id", "allOf"}
    assert generated == {key: value for key, value in complete.items()
                         if key not in {"$schema", "$id", "allOf"}}
    assert "allOf" in cls.model_json_schema()
    # A producer projection cannot authorize a SAFE result with an open question.
    ok, _ = _common.validate_response(json.dumps(verdict(open_questions=["unresolved"])), cls)
    assert not ok
