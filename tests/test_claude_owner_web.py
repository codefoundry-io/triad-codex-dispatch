"""C31/C32: explicit web authorization stays invocation- and basis-scoped."""
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from test_review_round import prepared, worktree, review_round
from test_review_conditions import _prepared_brief
from test_four_leg_custody import _brief
from test_v2_review_prompts import arguments
from test_v2_rounds import round_fixture, finish, start
from test_v2_adapters import adapter_case
from test_v2_producer_adapter import verdict
from test_v2_google_wrappers import route

import _common
import claude_wrapper
import review_prompts_v2
import hashlib
import tomllib


@pytest.fixture
def call_wrapper(tmp_path, monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(_common, "_LOG_DIR_CONFIGURED", True)
    monkeypatch.setenv("TRIAD_WRAPPER_ALLOWED_ROOTS", str(tmp_path))
    monkeypatch.setattr(claude_wrapper, "require_binary", lambda _: "/fixture/claude")

    def run(*, mode="raw", web=False, authorized=None, metadata_changes=None):
        data = verdict(family="claude", route=None, leg_name="claude")
        fields = ("review_id", "family", "content_digest", "leg_name", "attempt", "route")
        if mode == "legacy":
            data = {key: value for key, value in data.items() if key not in ("schema_version", "leg_name", "attempt", "route")}
            data["verdict"] = "SAFE"
            fields = fields[:3]
        options = ["claude_wrapper.py", "--cwd", str(tmp_path)]
        prompt = "Verify the requested external fact."
        if mode != "raw":
            schema = "verdict_v2:LegVerdict" if mode == "v2" else "verdict_schema:LegVerdict"
            options += ["--pydantic", schema, "--model", "opus", "--effort", "xhigh", "--timeout", "1200"]
            for field in fields:
                options += ["--expected-" + field.replace("_", "-"), "null" if data[field] is None else str(data[field])]
            if authorized is not None:
                meta = {key: data[key] for key in fields}
                meta.update(review_web_authorized=authorized)
                meta.update(metadata_changes or {})
                prompt = ("Review v2 metadata: " if mode == "v2" else "Review metadata: ") + json.dumps(meta) + "\n" + prompt
        if web:
            options += ["--web"]
        options += ["--prompt", prompt]

        def provider(cli, cmd, cwd, timeout, **kwargs):
            calls.append((cmd, kwargs))
            output = {"result": "fetched evidence"} if mode == "raw" else {"structured_output": data, "result": ""}
            return _common.RunResult(exit_code=0, vendor_exit_code=0, stdout=json.dumps(output), stderr="", elapsed_s=.1)

        monkeypatch.setattr(_common, "_run_once", provider)
        monkeypatch.setattr(sys, "argv", options)
        try:
            rc = claude_wrapper.main()
        except SystemExit as error:
            rc = error.code
        return rc, calls, capsys.readouterr(), data
    return run


@pytest.mark.parametrize("web", [False, True])
def test_C31_raw_fixed_web_permit(call_wrapper, web):
    rc, calls, output, _ = call_wrapper(web=web)
    assert rc == 0 and output.out.strip() == "fetched evidence"
    cmd, kwargs = calls[0]
    assert ("--allowedTools" in cmd) is web
    if web:
        assert cmd[cmd.index("--allowedTools") + 1:cmd.index("--allowedTools") + 3] == ["WebSearch", "WebFetch"]
    assert kwargs["stdin_text"] == "Verify the requested external fact."
    assert "--tools" not in cmd and "--dangerously-skip-permissions" not in cmd


@pytest.mark.parametrize("mode", ["legacy", "v2"])
@pytest.mark.parametrize("web,authorized,success", [(False, None, True), (False, False, True), (True, True, True),
    (True, None, False), (True, False, False), (False, True, False), (True, "true", False)])
def test_C32_review_permission_must_match_bound_condition(call_wrapper, mode, web, authorized, success):
    rc, calls, output, data = call_wrapper(mode=mode, web=web, authorized=authorized)
    assert rc == (0 if success else _common.EXIT_ARG_ERROR)
    assert len(calls) == int(success)
    if success:
        assert json.loads(output.out) == data
        cmd = calls[0][0]
        assert cmd.count("--permission-mode") == 1 and cmd[cmd.index("--permission-mode") + 1] == "plan"
        assert ("--allowedTools" in cmd) is web
        assert "--json-schema" in cmd


@pytest.mark.parametrize("mode", ["legacy", "v2"])
def test_C32_permission_cannot_be_borrowed_from_other_binding(call_wrapper, mode):
    rc, calls, _, _ = call_wrapper(mode=mode, web=True, authorized=True, metadata_changes={"content_digest": "f" * 64})
    assert rc == _common.EXIT_ARG_ERROR and calls == []


@pytest.mark.parametrize("mode", ["prepared", "worktree"])
def test_C32_common_legacy_permission_preserves_one_digest(prepared, worktree, mode):
    brief = _prepared_brief(prepared) if mode == "prepared" else replace(_brief(worktree), google_flash_preflight_receipt=None)
    render = review_round.render_review_prompt if mode == "prepared" else review_round.render_worktree_review_prompt
    digests = set()
    for family in ("claude", "codex", "google"):
        before = render(replace(brief, family=family))
        receipt = replace(brief.google_selector_receipt, review_web_authorized=True)
        after = render(replace(brief, family=family, review_web_authorized=True, native_web_available=True, google_selector_receipt=receipt))
        metadata = json.loads(next(line.removeprefix("Review metadata: ") for line in after.splitlines() if line.startswith("Review metadata: ")))
        assert metadata["review_web_authorized"] is True
        digests.add(metadata["content_digest"])
        assert "Web verification is explicitly authorized" in after
        assert "Do not use web search, URL fetching" not in after
        assert "Do not call search_web or read_url_content" not in after
        assert metadata["content_digest"] not in before
    assert len(digests) == 1


@pytest.mark.parametrize("family", ["claude", "codex", "google"])
def test_C32_v2_prompt_selects_one_permission_policy(tmp_path, family):
    prompt = review_prompts_v2.render_prompt(**arguments(tmp_path, family), review_web_authorized=True)
    assert "Web verification is explicitly authorized" in prompt
    assert "access the network/web" not in prompt
    assert "Do NOT access the network" not in prompt and "web/search/fetch tools or" not in prompt


@pytest.mark.parametrize("value", [True, "true", 1, None])
def test_C32_v2_request_has_strict_transient_authorization(round_fixture, value):
    mod, _, root, tree, request, calls = round_fixture(make_basis=False)
    request["review_web_authorized"] = value
    if value is not True:
        with pytest.raises(ValueError, match="review_web_authorized"):
            mod.create_basis(request, root=root)
        assert calls == []
        return
    request["native_capabilities"]["web_available"] = True
    config = tree / ".agents/triad-review-legs.json"
    config.write_text(json.dumps({"schema": "triad-review-legs.v2", "legs": [
        {"name": "c", "vendor": "claude", "enabled": True, "acceptance": "required", "timeout_s": 1200,
         "claude": {"model": "opus", "effort": "xhigh"}},
        {"name": "n", "vendor": "codex", "enabled": True, "acceptance": "required", "timeout_s": 120,
         "codex": {"model": "gpt-5.6-terra", "reasoning": "high"}}]}))
    basis = mod.create_basis(request, root=root)
    fixture = (mod, basis, root, tree, request, calls)
    assert basis["request"]["review_web_authorized"] is True
    first = start(fixture, "c")
    assert "--web" in first["invocation"]["argv"]
    assert "Web verification is explicitly authorized" in Path(first["prompt_file"]).read_text()
    assert basis["adapters"]["n"]["native_web_available"] is True
    native = start(fixture, "n")
    assert "Web verification is explicitly authorized" in native["invocation"]["arguments"]["message"]
    finish(fixture, native, failed=True)
    native_retry = mod.allocate_attempt(Path(basis["basis_file"]), "n", diagnosis="transient failure")
    assert native_retry["adapter"]["native_web_available"] is True
    assert native_retry["binding"]["content_digest"] == native["binding"]["content_digest"]
    assert basis["request"]["native_capabilities"]["web_available"] is True
    finish(fixture, first, failed=True)
    retry = mod.allocate_attempt(Path(basis["basis_file"]), "c", diagnosis="transient failure")
    assert "--web" in retry["invocation"]["argv"] and retry["binding"]["content_digest"] == first["binding"]["content_digest"]


@pytest.mark.parametrize("supported", [False, True])
def test_C32_web_capability_is_checked_before_sealing(adapter_case, monkeypatch, supported):
    mod, roster, kwargs, calls, _ = adapter_case()
    probe = mod.probe
    def help_probe(argv, **options):
        value = probe(argv, **options)
        return value + " --allowedTools" if supported and "--help" in argv else value
    monkeypatch.setattr(mod, "probe", help_probe)
    if not supported:
        with pytest.raises(ValueError, match="web|allowedTools"):
            mod.prepare_adapters(roster, **kwargs, review_web_authorized=True)
        assert not any(call[-1].startswith("/model") for call in calls)
    else:
        kwargs["native_capabilities"]["web_available"] = True
        adapters = mod.prepare_adapters(roster, **kwargs, review_web_authorized=True)
        assert all(adapter["review_web_authorized"] is True for adapter in adapters.values())


@pytest.mark.parametrize("dispatch_web", [False, True])
def test_C32_google_preflight_permission_binds_dispatch_and_policy(route, dispatch_web):
    rc, output, error = route["invoke"](["--preflight-only", "--web"])
    assert rc == 0, error
    assert route["calls"] == []
    receipt = json.loads(output)
    assert receipt["review_web_authorized"] is True
    file = route["home"] / "preflight.json"
    file.write_text(output)
    expected = verdict(route=route["name"], leg_name="google-second")
    metadata = {key: expected[key] for key in ("review_id", "family", "content_digest", "leg_name", "attempt", "route")}
    metadata.update(review_web_authorized=True, google_preflight_receipt_sha256=hashlib.sha256(file.read_bytes()).hexdigest())
    options = list(route["options"])
    options[options.index("--prompt") + 1] = "Review v2 metadata: " + json.dumps(metadata) + "\nVerify the requested source."
    options += ["--expected-family", "google", "--expected-content-digest", "a" * 64,
                "--google-preflight-receipt", str(file)]
    if dispatch_web:
        options += ["--web"]
    rc, output, error = route["invoke"](base=options)
    assert rc == (0 if dispatch_web else _common.EXIT_ARG_ERROR), error
    assert len(route["calls"]) == int(dispatch_web)
    if route["name"] == "agy":
        assert route["guards"] and all("read_url(*)" not in rules for rules in route["guards"])
        assert all("write_file(*)" in rules and "command(*)" in rules for rules in route["guards"])
    else:
        policy = tomllib.loads(Path(receipt["policy"]).read_text())
        allow = next(rule["toolName"] for rule in policy["rule"] if rule["decision"] == "allow")
        deny = next(rule["toolName"] for rule in policy["rule"] if rule["decision"] == "deny" and rule["priority"] == 999)
        assert {"google_web_search", "web_fetch"} <= set(allow)
        assert {"write_file", "replace", "run_shell_command", "enter_plan_mode", "exit_plan_mode"} <= set(deny)


def test_C32_google_default_preflight_cannot_be_reused_with_web(route):
    from test_v2_google_wrappers import ready
    options, _ = ready(route)
    rc, output, _ = route["invoke"](["--web"], base=options)
    assert rc == _common.EXIT_ARG_ERROR and route["calls"] == [] and output == ""


def test_C32_legacy_digest_binds_the_selected_shared_permission_clause(prepared, monkeypatch):
    brief = _prepared_brief(prepared)
    brief = replace(brief, review_web_authorized=True, native_web_available=True,
                    google_selector_receipt=replace(brief.google_selector_receipt, review_web_authorized=True))
    digests = []
    for clause in ("permission clause version one", "permission clause version two"):
        monkeypatch.setattr(review_prompts_v2, "review_web_clause", lambda _, value=clause: value)
        prompt = review_round.render_review_prompt(brief)
        metadata = json.loads(next(line.split(": ", 1)[1] for line in prompt.splitlines() if line.startswith("Review metadata: ")))
        digests.append(metadata["content_digest"])
    assert digests[0] != digests[1]
