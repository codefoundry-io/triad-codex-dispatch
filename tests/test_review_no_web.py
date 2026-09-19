"""REVIEW must separate web and permission posture without breaking raw use."""
import contextlib
from dataclasses import replace
import json
import sys

import pytest

from test_agy_project_boundary import project_case, _canonical, wrapper, PRO, FLASH
from test_agy_settings import settings, BASELINE, _bind
from test_antigravity_stream_json import _run_result, _stream, _google_selector_fixture
from test_four_leg_custody import _brief
from test_review_conditions import _prepared_brief
from test_review_round import prepared, worktree, _google_selector_receipt, review_round

RAW = ["write_file(*)", "command(*)", "unsandboxed(*)", "execute_url(*)", "mcp(*)"]
FORMAL = RAW + ["read_url(*)"]


@pytest.mark.parametrize("model", [PRO, FLASH])
def test_formal_preflight_requires_read_only_before_probing(
    tmp_path, monkeypatch, capsys, model,
):
    selector, _, _ = _google_selector_fixture(tmp_path)
    observed = []
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _: None)
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _: observed.append("version") or (1, 2, 7))
    monkeypatch.setattr(wrapper, "_probe_agy_models", lambda _: observed.append("models") or {model})
    @contextlib.contextmanager
    def guard(rules, **kwargs):
        observed.append(list(rules))
        yield
    monkeypatch.setattr(settings, "agy_settings_guard", guard)
    monkeypatch.setattr(wrapper._common, "_run_once", lambda *a, **k: pytest.fail("provider started"))
    monkeypatch.setattr(sys, "argv", [
        "antigravity_wrapper.py", "--prompt", "formal route proof",
        "--model", model, "--effort", "high", "--preflight-only",
        "--google-selector-receipt", str(selector), "--expected-review-id", "review-r1",
    ])
    assert wrapper.main() == wrapper._common.EXIT_ARG_ERROR
    assert observed == []
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--sandbox read-only" in captured.err


@pytest.mark.parametrize("mode", ["prepared", "worktree"])
@pytest.mark.parametrize("family,route", [
    ("claude", "agy"), ("codex", "agy"), ("google", "agy"), ("google", "gemini"),
])
def test_all_review_prompts_forbid_web(prepared, worktree, mode, family, route):
    brief = _prepared_brief(prepared) if mode == "prepared" else _brief(worktree)
    selector = _google_selector_receipt(brief.review_id, route=route,
        authentication_class="gemini-enterprise" if route == "gemini" else "personal-google")
    changes = dict(family=family, google_selector_receipt=selector)
    if mode == "worktree":
        changes["google_flash_preflight_receipt"] = None
    render = review_round.render_review_prompt if mode == "prepared" else review_round.render_worktree_review_prompt
    prompt = render(replace(brief, **changes))
    assert "Do not use web search, URL fetching, or other network research in REVIEW" in prompt
    assert "Approved official-web reads" not in prompt
    assert "Approved AGY native official-web reads remain available" not in prompt
    if family == "google":
        prohibited = "search_web or read_url_content" if route == "agy" else "google_web_search or web_fetch"
        assert "Do not call " + prohibited in prompt


def test_identical_formal_leases_overlap_and_restore(tmp_path, monkeypatch):
    target, backup = _bind(tmp_path, monkeypatch)
    target.write_bytes(BASELINE)
    state_path = target.with_name(".agy_settings.shared.json")
    with settings.agy_settings_guard(FORMAL, lock_timeout=0):
        with settings.agy_settings_guard(FORMAL, lock_timeout=0):
            state = json.loads(state_path.read_text())
            assert len(state["holders"]) == 2
            assert set(json.loads(target.read_text())["permissions"]["deny"]) == set(FORMAL + ["command(sudo)"])
        assert len(json.loads(state_path.read_text())["holders"]) == 1
        assert backup.exists()
    assert target.read_bytes() == BASELINE
    assert not backup.exists() and not state_path.exists()
    assert not target.with_name(".agy_settings.holders").exists()


@pytest.mark.parametrize("held,other", [(RAW, FORMAL), (FORMAL, RAW)])
def test_raw_and_formal_leases_do_not_mix(tmp_path, monkeypatch, held, other):
    target, backup = _bind(tmp_path, monkeypatch)
    target.write_bytes(BASELINE)
    with settings.agy_settings_guard(held, lock_timeout=0):
        active = target.read_bytes()
        with pytest.raises(TimeoutError):
            with settings.agy_settings_guard(other, lock_timeout=0):
                pytest.fail("different deny lists shared a lease")
        assert target.read_bytes() == active
    assert target.read_bytes() == BASELINE
    assert not backup.exists()


@pytest.mark.parametrize("model", [PRO, FLASH])
@pytest.mark.parametrize("has_web_deny", [False, True])
def test_project_preflight_requires_web_deny_without_writes(
    project_case, monkeypatch, capsys, model, has_web_deny,
):
    home, _, path, record, _, args = project_case
    record["permissionGrants"]["permissionGrants"]["deny"] = FORMAL if has_web_deny else RAW
    path.write_bytes(_canonical(record))
    before = {str(p): p.read_bytes() for p in home.rglob("*") if p.is_file()}
    args[args.index("--model") + 1] = model
    monkeypatch.setattr(sys, "argv", args)
    monkeypatch.setattr(wrapper._common, "_run_once", lambda *a, **k: pytest.fail("preflight started provider"))
    assert wrapper.main() == (0 if has_web_deny else wrapper._common.EXIT_TERMINAL)
    if has_web_deny:
        assert json.loads(capsys.readouterr().out)["provider_started"] is False
    else:
        assert capsys.readouterr().out == ""
    assert {str(p): p.read_bytes() for p in home.rglob("*") if p.is_file()} == before


@pytest.mark.parametrize("sandbox", [False, True])
def test_raw_invocation_keeps_web_compatible_rules_and_headless_behavior(
    tmp_path, monkeypatch, capsys, sandbox,
):
    monkeypatch.delenv("AGY_NO_HEADLESS_AUTOAPPROVE", raising=False)
    monkeypatch.setattr(wrapper._common, "require_binary", lambda _: sys.executable)
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _: (1, 2, 7))
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _: None)
    monkeypatch.setattr(wrapper._common, "persist_result_artifacts", lambda *a, **k: None)
    rules, calls = [], []
    @contextlib.contextmanager
    def guard(deny_rules, **kwargs):
        rules.append(deny_rules)
        yield
    monkeypatch.setattr(settings, "agy_settings_guard", guard)
    def native(_cli, cmd, *a, **k):
        calls.append(cmd)
        return _run_result(_stream({"status": "SUCCESS", "response": "raw answer"}))
    monkeypatch.setattr(wrapper._common, "_run_once", native)
    args = ["antigravity_wrapper.py", "--prompt", "authorized raw investigation", "--cwd", str(tmp_path)]
    if sandbox:
        args += ["--sandbox", "read-only"]
    monkeypatch.setattr(sys, "argv", args)
    assert wrapper.main() == 0
    assert capsys.readouterr().out.strip() == "raw answer"
    assert "--dangerously-skip-permissions" in calls[0]
    assert rules == [RAW if sandbox else []]
