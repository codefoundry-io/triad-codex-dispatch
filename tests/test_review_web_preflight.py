"""Requested review web refuses missing host tools and known URL-wide denies."""
from dataclasses import replace
import json
import sys

import pytest

from test_v2_adapters import adapter_case
from test_review_round import prepared, worktree, review_round
from test_review_conditions import _prepared_brief
from test_four_leg_custody import _brief
from test_agy_project_boundary import project_case, _canonical, wrapper
from test_v2_google_wrappers import route
import _agy_settings

REAL_GLOBAL_GUARD = _agy_settings.agy_settings_guard


@pytest.mark.parametrize("available", ["missing", False, None, 1, "true"])
def test_native_web_capability_required_before_adapter_seal(adapter_case, available):
    mod, roster, kwargs, calls, _ = adapter_case()
    roster["legs"] = [entry for entry in roster["legs"] if entry["vendor"] == "codex"]
    if available != "missing":
        kwargs["native_capabilities"]["web_available"] = available
    with pytest.raises(ValueError, match="native.*web"):
        mod.prepare_adapters(roster, **kwargs, review_web_authorized=True)
    assert calls == []
    assert not list(kwargs["receipt_root"].rglob("adapter.json"))
    failure = json.loads(next(kwargs["receipt_root"].rglob("preparation-failure.json")).read_text())
    assert failure["provider_started"] is False


def test_native_host_web_observation_is_bound_in_adapter(adapter_case):
    mod, roster, kwargs, calls, _ = adapter_case()
    roster["legs"] = [entry for entry in roster["legs"] if entry["vendor"] == "codex"]
    kwargs["native_capabilities"]["web_available"] = True
    controls = mod.prepare_adapters(roster, **kwargs, review_web_authorized=True)["codex"]
    assert controls["native_web_available"] is True
    assert controls["review_web_authorized"] is True and calls == []
    assert json.loads((kwargs["receipt_root"] / "codex/attempt-1/adapter.json").read_text()) == controls


@pytest.mark.parametrize("mode", ["prepared", "worktree"])
def test_legacy_web_requires_host_observation_before_render(prepared, worktree, mode):
    brief = _prepared_brief(prepared) if mode == "prepared" else replace(_brief(worktree), google_flash_preflight_receipt=None)
    brief = replace(brief, review_web_authorized=True,
                    google_selector_receipt=replace(brief.google_selector_receipt, review_web_authorized=True))
    render = review_round.render_review_prompt if mode == "prepared" else review_round.render_worktree_review_prompt
    with pytest.raises(review_round.RoundIntegrityError, match="native.*web"):
        render(brief)
    prompt = render(replace(brief, native_web_available=True))
    metadata = json.loads(next(line.split(": ", 1)[1] for line in prompt.splitlines() if line.startswith("Review metadata: ")))
    assert metadata["native_web_available"] is True


@pytest.mark.parametrize("phase", ["preflight", "dispatch"])
def test_project_whole_url_deny_refuses_requested_review_web(project_case, monkeypatch, capsys, tmp_path, phase):
    home, _, project_path, record, selector_path, args = project_case
    calls = []
    monkeypatch.setattr(wrapper._common, "_run_once", lambda *a, **k: calls.append(a) or pytest.fail("provider started"))
    args.append("--web")
    monkeypatch.setattr(sys, "argv", args)
    if phase == "dispatch":
        record["permissionGrants"]["permissionGrants"]["deny"].remove("read_url(*)")
        project_path.write_bytes(_canonical(record))
        assert wrapper.main() == 0
        receipt_path = tmp_path / "web-preflight.json"
        receipt_path.write_text(capsys.readouterr().out)
        selector = review_round.load_google_selector_receipt(selector_path, expected_review_id="review-r1")
        bound = review_round.validate_google_preflight_receipt(receipt_path, selector, expected_review_id="review-r1")
        metadata = {"review_id": "review-r1", "family": "google", "content_digest": "a" * 64,
                    "review_web_authorized": True, **review_round._google_selector_metadata(bound),
                    **review_round._google_preflight_metadata(bound)}
        args.remove("--preflight-only")
        args[args.index("--prompt") + 1] = "Review metadata: " + json.dumps(metadata)
        args.extend(["--google-preflight-receipt", str(receipt_path), "--pydantic", "verdict_schema:LegVerdict",
                     "--expected-family", "google", "--expected-content-digest", "a" * 64])
        record["permissionGrants"]["permissionGrants"]["deny"].append("read_url(*)")
        project_path.write_bytes(_canonical(record))
    before = {str(path): path.read_bytes() for path in home.rglob("*") if path.is_file()}
    assert wrapper.main() == wrapper._common.EXIT_TERMINAL
    assert "web" in capsys.readouterr().err and calls == []
    assert {str(path): path.read_bytes() for path in home.rglob("*") if path.is_file()} == before


@pytest.mark.parametrize("blocked", [False, True])
def test_active_local_web_guard_preserves_owner_rules_and_restores(tmp_path, monkeypatch, blocked):
    path = tmp_path / "settings.json"
    original = json.dumps({"permissions": {"deny": ["read_url(*)"] if blocked else ["read_file(/private)"]}}).encode()
    path.write_bytes(original)
    monkeypatch.setenv("AGY_SETTINGS_PATH", str(path))
    entered = False
    try:
        with _agy_settings.agy_settings_guard(_agy_settings.build_deny_rules("read-only"), require_web=True):
            entered = True
    except ValueError as error:
        assert blocked and "web" in str(error)
    assert entered is not blocked
    assert path.read_bytes() == original


@pytest.mark.parametrize("available", [False, True])
def test_legacy_cli_forwards_current_host_web_report(prepared, worktree, tmp_path, available):
    from test_review_round import _cli_operation_args
    brief = _prepared_brief(prepared)
    args = _cli_operation_args("render", brief.prepared_dir, worktree, tmp_path, "native-web",
                               review_id=brief.review_id)
    receipt = tmp_path / "preflight-native-web.json"
    data = json.loads(receipt.read_text())
    data["review_web_authorized"] = True
    receipt.write_bytes(review_round._canonical_json_bytes(data))
    args += ["--web-authorized"] + (["--native-web-available"] if available else [])
    assert review_round.main(args[2:]) == (0 if available else 2)
    output = tmp_path / "render-native-web.txt"
    assert output.exists() is available
    if available:
        metadata = json.loads(next(line.split(": ", 1)[1] for line in output.read_text().splitlines()
                                   if line.startswith("Review metadata: ")))
        assert metadata["native_web_available"] is True


@pytest.mark.parametrize("route", ["agy"], indirect=True)
def test_global_web_preflight_uses_the_real_known_deny_check(route, tmp_path, monkeypatch):
    settings = tmp_path / "owner-settings.json"
    original = b'{"permissions":{"deny":["read_url(*)"]}}\n'
    settings.write_bytes(original)
    monkeypatch.setenv("AGY_SETTINGS_PATH", str(settings))
    monkeypatch.setattr(_agy_settings, "agy_settings_guard", REAL_GLOBAL_GUARD)
    rc, output, error = route["invoke"](["--preflight-only", "--web"])
    assert rc == wrapper._common.EXIT_TERMINAL and output == "" and "web" in error
    assert route["calls"] == [] and settings.read_bytes() == original
