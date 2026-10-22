"""AGY provider metadata must not change strict verdict or terminal admission."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from pydantic import AliasChoices, AliasPath, BaseModel, ConfigDict, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
import _common
import antigravity_wrapper as wrapper
from test_agy_finish_resubmission import recovery_steps
from test_antigravity_stream_json import _formal_payload
from test_v2_producer_adapter import binding, verdict
from verdict_schema import LegVerdict
from verdict_v2 import bound_verdict


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ok: bool


def interpret(payload, cls=Answer, *, status="SUCCESS", error=None, events=(), raw=None, plan_mode=True):
    terminal = {"status": status, "response": "final answer", "structured_output": payload}
    if error is not None:
        terminal["error"] = error
    stdout = "\n".join([*(json.dumps(event) for event in events),
                        json.dumps({"event": "result", "result": terminal})])
    run = _common.RunResult(exit_code=0, vendor_exit_code=0,
                           stdout=stdout if raw is None else raw, stderr="", elapsed_s=0.1)
    original = run.stdout
    result = wrapper._interpret_run(run, cls, plan_mode=plan_mode)
    assert result.stdout == original
    return result


@pytest.mark.parametrize("metadata", [
    {"toolAction": "finish", "toolSummary": "검토 완료"},
    {"toolAction": None, "toolSummary": {"items": [1, True, "text"]}},
])
@pytest.mark.parametrize("plan_mode", [False, True])
def test_undeclared_metadata_is_separated_before_custom_schema_validation(metadata, plan_mode):
    result = interpret({"ok": True, **metadata}, plan_mode=plan_mode)
    assert result.exit_code == 0
    assert result.validated == {"ok": True}
    assert json.loads(result.final_answer) == {"ok": True}


@pytest.mark.parametrize("status,error,events,expected", [
    ("SUCCESS", None, (), 0),
    ("ERROR", 'permission check failed for command "write result.json"', (), 0),
    ("ERROR", "finish failed", recovery_steps(), 0),
    ("ERROR", "backend failed", (), _common.EXIT_TERMINAL),
])
def test_legacy_verdict_metadata_retains_terminal_and_recovery_rules(status, error, events, expected):
    payload = _formal_payload()
    result = interpret({**payload, "toolAction": "finish", "toolSummary": "done"},
                       LegVerdict, status=status, error=error, events=events)
    assert result.exit_code == expected
    assert result.validated == (payload if expected == 0 else None)
    assert (json.loads(result.final_answer) if result.final_answer else None) == (
        payload if expected == 0 else None)


@pytest.mark.parametrize("payload", [
    {"ok": True, "toolAction": "finish", "unexpected": "extra"},
    {"toolSummary": "done"},
    {"ok": "invalid", "toolSummary": "done"},
    {"ok": True, "nested": {"toolAction": "finish"}},
])
def test_metadata_does_not_admit_invalid_payload(payload):
    result = interpret(payload)
    assert result.exit_code == _common.EXIT_SCHEMA_FAIL
    assert result.final_answer == "" and result.validated is None


@pytest.mark.parametrize("field_name,alias", [
    ("toolAction", None), ("toolSummary", None), ("action", "toolAction"),
])
@pytest.mark.parametrize("value,expected", [(7, 0), ("invalid", _common.EXIT_SCHEMA_FAIL)])
def test_declared_metadata_names_and_aliases_keep_their_validation(field_name, alias, value, expected):
    from pydantic import create_model
    cls = create_model("Declared", __config__=ConfigDict(extra="forbid", strict=True),
                       **{field_name: (int, Field(alias=alias))})
    result = interpret({alias or field_name: value}, cls)
    assert result.exit_code == expected
    if expected == 0:
        assert result.validated == {field_name: 7}


@pytest.mark.parametrize("alias,value", [
    (AliasChoices("action", "toolAction"), 7),
    (AliasPath("toolAction", "value"), {"value": 7}),
])
def test_metadata_name_in_validation_alias_is_not_discarded(alias, value):
    class Declared(BaseModel):
        model_config = ConfigDict(extra="forbid", strict=True)
        action: int = Field(validation_alias=alias)

    result = interpret({"toolAction": value, "toolSummary": "done"}, Declared)
    assert result.exit_code == 0
    assert result.validated == {"action": 7}


def test_unresolved_top_level_schema_keeps_metadata_for_original_validation():
    class Composed(Answer):
        @classmethod
        def model_json_schema(cls, **kwargs):
            return {"allOf": [super().model_json_schema(**kwargs)]}

    result = interpret({"ok": True, "toolSummary": "done"}, Composed)
    assert result.exit_code == _common.EXIT_SCHEMA_FAIL


def test_nested_metadata_names_remain_payload_data():
    class Nested(BaseModel):
        model_config = ConfigDict(extra="forbid")
        detail: dict

    result = interpret({"detail": {"toolAction": "user field", "toolSummary": 7},
                        "toolAction": "finish"}, Nested)
    assert result.exit_code == 0
    assert result.validated == {"detail": {"toolAction": "user field", "toolSummary": 7}}


@pytest.mark.parametrize("failure", ["missing-verdict", "duplicate-metadata"])
def test_v2_metadata_retains_missing_verdict_and_original_duplicate_refusals(failure):
    payload = verdict()
    cls = bound_verdict(binding(payload))
    if failure == "missing-verdict":
        payload.pop("verdict")
    payload["toolSummary"] = "done"
    raw_payload = json.dumps(payload)
    if failure == "duplicate-metadata":
        raw_payload = raw_payload[:-1] + ',"toolSummary":"other"}'
    raw = '{"event":"result","result":{"status":"SUCCESS","structured_output":' + raw_payload + '}}'
    result = interpret(None, cls, raw=raw)
    assert result.exit_code == _common.EXIT_SCHEMA_FAIL
    assert result.final_answer == "" and result.validated is None


@pytest.mark.parametrize("fragment", [
    '"toolAction":"finish","toolAction":"finish"',
    '"toolSummary":NaN', '"toolSummary":Infinity',
    '"toolSummary":1e999', '"toolSummary":{"nested":1,"nested":2}',
])
def test_original_invalid_metadata_is_rejected_before_custom_schema_projection(fragment):
    raw = ('{"event":"result","result":{"status":"SUCCESS",'
           '"structured_output":{"ok":true,' + fragment + '}}}')
    result = interpret(None, raw=raw)
    assert result.exit_code == _common.EXIT_SCHEMA_FAIL
    assert result.final_answer == "" and result.validated is None
