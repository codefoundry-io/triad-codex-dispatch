"""Original JSON must reach canonical verdict admission without ambiguity."""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common
import antigravity_wrapper
import claude_wrapper


def _answer(family):
    return json.dumps({
        "review_id": "review-r1", "family": family, "content_digest": "a" * 64,
        "verdict": "SAFE", "criteria_checked": ["correctness"], "findings": [],
        "affected_surfaces_inspected": ["src/parser.py"], "open_questions": [],
    })


def _run(raw):
    return _common.RunResult(exit_code=0, stdout=raw, stderr="", elapsed_s=0.1,
                             vendor_exit_code=0)


def _envelope(route, answer):
    if route == "claude":
        return '{"is_error":false,"structured_output":' + answer + '}'
    if route == "gemini":
        return '{"response":' + answer + '}'
    return 'noise\n{invalid\n{"event":"result","result":{"status":"SUCCESS","structured_output":' + answer + '}}\n'


def _admit(route, raw, cls, monkeypatch):
    calls = []
    def fake_run(*args, **kwargs):
        calls.append(args)
        return _run(raw)
    monkeypatch.setattr(_common, "_run_once", fake_run)
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda *_args: None)
    if route == "claude":
        result = claude_wrapper._run_native_structured_once(
            ["synthetic"], str(ROOT), 1200, cls,
            expected_review_id="review-r1", expected_family="claude",
            expected_content_digest="a" * 64)
        assert len(calls) == 1
    elif route == "gemini":
        result = _common.run_cli_with_retry(
            "gemini", lambda _prompt: ["synthetic"], "review", str(ROOT), 600,
            pydantic_cls=cls, single_provider_call=True)
        assert len(calls) == 1
    else:
        result = antigravity_wrapper._interpret_run(
            _run(raw), cls, expected_review_id="review-r1", expected_family="google",
            expected_content_digest="a" * 64, plan_mode=True)
        assert calls == []
    return result


@pytest.mark.parametrize("route", ["answer", "claude", "gemini", "agy"])
@pytest.mark.parametrize("field,wrong", [
    ("review_id", "stale-review"), ("family", "codex"), ("content_digest", "b" * 64)])
@pytest.mark.parametrize("escaped", [False, True])
def test_duplicate_binding_is_rejected_before_normalization(route, field, wrong, escaped, monkeypatch):
    family = "claude" if route in ("answer", "claude") else "google"
    key = ("\\u" + format(ord(field[0]), "04x") + field[1:]) if escaped else field
    answer = '{"' + key + '":' + json.dumps(wrong) + ',' + _answer(family)[1:]
    cls = _common.load_pydantic_class("verdict_schema:LegVerdict")
    if route == "answer":
        ok, error = _common.validate_response(answer, cls)
        assert not ok
        assert "duplicate JSON member" in error
        assert wrong not in error
        return
    result = _admit(route, _envelope(route, answer), cls, monkeypatch)
    assert result.exit_code == _common.EXIT_SCHEMA_FAIL
    assert result.classification == "schema-fail"
    assert result.final_answer == ""
    assert result.validated is None
    assert wrong not in (result.validation_error or "")


def test_custom_schema_keeps_legacy_duplicate_handling():
    class Custom(BaseModel):
        content_digest: str
    assert _common.validate_response('{"content_digest":"old","content_digest":"new"}', Custom) == (True, {"content_digest": "new"})


@pytest.mark.parametrize("route", ["claude", "gemini", "agy"])
def test_custom_wrapper_schema_keeps_legacy_duplicate_handling(route, monkeypatch):
    class Custom(BaseModel):
        model_config = {"extra": "allow"}
    family = "claude" if route == "claude" else "google"
    answer = '{"content_digest":"old",' + _answer(family)[1:]
    result = _admit(route, _envelope(route, answer), Custom, monkeypatch)
    assert result.exit_code == 0
    assert result.validated["content_digest"] == "a" * 64


@pytest.mark.parametrize("route", ["claude", "gemini", "agy"])
def test_duplicate_outer_answer_member_is_rejected(route, monkeypatch):
    family = "claude" if route == "claude" else "google"
    raw = _envelope(route, _answer(family))
    key = "response" if route == "gemini" else "structured_output"
    raw = raw.replace('"' + key + '":', '"' + key + '":null,"' + key + '":', 1)
    cls = _common.load_pydantic_class("verdict_schema:LegVerdict")
    result = _admit(route, raw, cls, monkeypatch)
    assert result.exit_code == _common.EXIT_SCHEMA_FAIL
    assert result.final_answer == "" and result.validated is None


@pytest.mark.parametrize("noise", [
    '{"event":"progress","payload":{"x":1,"x":2}} trailing',
    '{"event":"progress","payload":{"x":1,"x":2}',
])
def test_agy_ignores_malformed_noise_even_with_nested_duplicate(noise, monkeypatch):
    raw = noise + "\n" + _envelope("agy", _answer("google"))
    cls = _common.load_pydantic_class("verdict_schema:LegVerdict")
    result = _admit("agy", raw, cls, monkeypatch)
    assert result.exit_code == 0
    assert result.validated["content_digest"] == "a" * 64


@pytest.mark.parametrize("route", ["claude", "agy"])
@pytest.mark.parametrize("spec", ["verdict_schema:LegVerdict", "verdict_schema.LegVerdict"])
@pytest.mark.parametrize("partial", [False, True])
def test_reserved_verdict_requires_bindings_before_probe(route, spec, partial, monkeypatch, capsys):
    monkeypatch.delenv("TRIAD_WRAPPER_HARDENED", raising=False)
    argv = ["wrapper.py", "--prompt", "review", "--pydantic", spec]
    if partial:
        argv += ["--expected-review-id", "review-r1"]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(_common, "require_binary", lambda *_args: pytest.fail("binary resolution reached"))
    monkeypatch.setattr(claude_wrapper, "require_binary", lambda *_args: pytest.fail("binary resolution reached"))
    monkeypatch.setattr(antigravity_wrapper, "_probe_agy_version", lambda *_args: pytest.fail("binary probe reached"))
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda *_args: None)
    wrapper = claude_wrapper if route == "claude" else antigravity_wrapper
    assert wrapper.main() == _common.EXIT_ARG_ERROR
    output = capsys.readouterr()
    assert output.out == ""
    assert "bindings" in output.err


@pytest.mark.parametrize("route", ["claude", "agy"])
def test_dotted_verdict_retains_formal_route_guard(route, monkeypatch, capsys):
    monkeypatch.delenv("TRIAD_WRAPPER_HARDENED", raising=False)
    family = "claude" if route == "claude" else "google"
    argv = ["wrapper.py", "--prompt", "review", "--pydantic", "verdict_schema.LegVerdict",
            "--expected-review-id", "review-r1", "--expected-family", family,
            "--expected-content-digest", "a" * 64]
    if route == "claude":
        argv += ["--model", "opus", "--effort", "xhigh", "--timeout", "1199"]
        expected = "formal Claude route requires"
    else:
        argv += ["--sandbox", "read-only", "--timeout", "599"]
        expected = "formal AGY review requires"
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(_common, "require_binary", lambda *_args: pytest.fail("binary resolution reached"))
    monkeypatch.setattr(claude_wrapper, "require_binary", lambda *_args: pytest.fail("binary resolution reached"))
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda *_args: None)
    wrapper = claude_wrapper if route == "claude" else antigravity_wrapper
    assert wrapper.main() == _common.EXIT_ARG_ERROR
    output = capsys.readouterr()
    assert output.out == ""
    assert expected in output.err


@pytest.mark.parametrize("spec", ["verdict_schema:LegVerdict", "verdict_schema.LegVerdict"])
@pytest.mark.parametrize("hardened", ["0", "1"])
def test_packaged_alias_ignores_import_shadow(spec, hardened, monkeypatch):
    class Shadow(BaseModel):
        sentinel: str
    monkeypatch.setenv("TRIAD_WRAPPER_HARDENED", hardened)
    monkeypatch.delenv("TRIAD_ALLOW_PYDANTIC_IMPORT", raising=False)
    monkeypatch.setitem(sys.modules, "verdict_schema", types.SimpleNamespace(LegVerdict=Shadow))
    cls = _common.load_pydantic_class(spec)
    assert cls.model_validate_json(_answer("google")).review_id == "review-r1"
