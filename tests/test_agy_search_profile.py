"""C72: formal AGY discovery requires an installed, unchanged tool profile."""
import contextlib
import hashlib
import json
import sys
from pathlib import Path

import pytest

from test_antigravity_stream_json import wrapper, _google_selector_fixture
from test_v2_google_wrappers import route, ready  # noqa: F401
import _agy_agent


@pytest.fixture
def profiles(tmp_path, monkeypatch):
    directory = tmp_path / "profiles"
    _agy_agent.install(directory)
    monkeypatch.setattr(_agy_agent, "agents_dir", lambda: directory)
    return directory


@pytest.mark.parametrize("web", [False, True])
@pytest.mark.parametrize("route", ["agy"], indirect=True)
def test_c72_formal_selection_binds_profile_and_preserves_route(profiles, route, web):
    if route["name"] != "agy":
        pytest.skip("AGY profile contract")
    options, receipt = ready(route, web=web)
    record = json.loads(receipt.read_text())
    name = "triad-codex-readonly-" + ("research" if web else "review")
    path = profiles / f"{name}.md"
    assert record["agent"] == name
    assert record["agent_path"] == str(path)
    assert record["agent_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    rc, _, error = route["invoke"](base=options)
    assert rc == 0, error
    cmd = route["calls"][0][0]
    assert cmd[cmd.index("--agent") + 1] == name
    assert cmd[cmd.index("--model") + 1] == route["model"]
    assert cmd[cmd.index("--effort") + 1] == "high"
    assert cmd[cmd.index("--mode") + 1] == "plan" and "--sandbox" in cmd
    assert "--dangerously-skip-permissions" not in cmd


@pytest.mark.parametrize("route", ["agy"], indirect=True)
def test_c72_profile_drift_after_preflight_stops_before_provider(profiles, route):
    if route["name"] != "agy":
        pytest.skip("AGY profile contract")
    options, _ = ready(route)
    (profiles / "triad-codex-readonly-review.md").write_text("drift")
    rc, output, error = route["invoke"](base=options)
    assert rc == 65 and output == "" and "profile" in error
    assert route["calls"] == []


@pytest.mark.parametrize("route", ["agy"], indirect=True)
def test_c72_profile_change_during_provider_withholds_result(profiles, route, monkeypatch):
    options, _ = ready(route)
    original = wrapper._common._run_once
    captured = []
    def changed(*args, **kwargs):
        result = original(*args, **kwargs)
        captured.append(result.stdout)
        (profiles / "triad-codex-readonly-review.md").write_text("changed during run")
        return result
    monkeypatch.setattr(wrapper._common, "_run_once", changed)
    rc, output, error = route["invoke"](base=options)
    assert rc == 65 and output == "" and "profile" in error
    assert len(route["calls"]) == 1
    records = list((route["home"] / "logs/antigravity/runs").glob("*.json"))
    assert len(records) == 1
    record = json.loads(records[0].read_text())
    assert record["classification"] == "config-conflict"
    assert record["stdout"] == captured[0]


@pytest.mark.parametrize("web", [False, True])
def test_c72_binding_refuses_other_profile_or_hash(profiles, web):
    record = _agy_agent.controls(web)
    _agy_agent.validate_binding(record, web, source_bin=Path(wrapper.__file__).parent)
    for key, value in {"agent": "default", "agent_sha256": "0" * 64,
                       "agent_path": "relative.md"}.items():
        with pytest.raises(ValueError, match="binding mismatch"):
            _agy_agent.validate_binding({**record, key: value}, web, source_bin=Path(wrapper.__file__).parent)
    with pytest.raises(ValueError, match="binding mismatch"):
        _agy_agent.validate_binding(record, not web, source_bin=Path(wrapper.__file__).parent)


@pytest.mark.parametrize("route", ["agy"], indirect=True)
@pytest.mark.parametrize("formal", [False, True])
def test_c72_timeout_with_profile_drift_preserves_failure_evidence(profiles, route, monkeypatch, formal):
    options, _ = ready(route)
    if not formal:
        options = ["--prompt", "Read the fixture", "--cwd", str(route["home"]), "--sandbox", "read-only"]
        monkeypatch.setattr(wrapper._common, "require_binary", lambda _: str(route["home"] / "agy"))
    raw = '{"event":"step_update","step_update":{"text_delta":"captured partial"}}'
    def provider(*args, **kwargs):
        name = "review" if formal else "research"
        (profiles / f"triad-codex-readonly-{name}.md").write_text("drift")
        return wrapper._common.RunResult(exit_code=wrapper._common.EXIT_TIMEOUT,
            vendor_exit_code=-15, stdout=raw, stderr="timeout fixture", elapsed_s=.1)
    monkeypatch.setattr(wrapper._common, "_run_once", provider)
    rc, output, error = route["invoke"](base=options)
    assert rc == wrapper._common.EXIT_TIMEOUT and output == ""
    records = list((route["home"] / "logs/antigravity/runs").glob("*.json"))
    assert len(records) == 1
    record = json.loads(records[0].read_text())
    assert record["classification"] == "timeout"
    assert record["stdout"] == raw


def test_c72_setup_is_explicit_idempotent_and_preserves_other_hosts(tmp_path):
    other = tmp_path / "triad-readonly-review.md"
    other.write_text("Claude-owned")
    paths = _agy_agent.install(tmp_path)
    before = {p: p.read_bytes() for p in paths}
    assert _agy_agent.install(tmp_path) == paths
    assert before == {p: p.read_bytes() for p in paths}
    paths[0].write_text("operator change")
    with pytest.raises(ValueError, match="review before --replace"):
        _agy_agent.install(tmp_path)
    assert paths[0].read_text() == "operator change"
    _agy_agent.install(tmp_path, replace=True)
    assert before == {p: p.read_bytes() for p in paths}
    assert other.read_text() == "Claude-owned"


@pytest.mark.parametrize("web", [False, True])
def test_c72_packaged_profile_declares_discovery_and_inherited_model(web):
    _, body = _agy_agent.profile(web)
    front = body.decode().split("---", 2)[1]
    tools = {line[4:] for line in front.splitlines() if line.startswith("  - ")}
    expected = {"view_file", "grep_search", "list_dir", "find_by_name", "finish"}
    if web:
        expected |= {"read_url_content", "search_web"}
    assert tools == expected
    assert "mainAgent: true" in front and "subagent: false" in front
    assert "model: inherit" in front and "commandExecutionPolicy: off" in front


def test_c72_legacy_preflight_roundtrips_unicode_profile_path(tmp_path, monkeypatch, capsys):
    directory = tmp_path / "프로필"
    _agy_agent.install(directory)
    monkeypatch.setattr(_agy_agent, "agents_dir", lambda: directory)
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _: (1, 3, 2))
    selector, _, _ = _google_selector_fixture(tmp_path)
    monkeypatch.setattr(sys, "argv", ["antigravity_wrapper.py", "--prompt", "preflight",
        "--cwd", str(tmp_path), "--sandbox", "read-only", "--model", "gemini-4-argon-high",
        "--effort", "high", "--expected-review-id", "review-r1",
        "--google-selector-receipt", str(selector), "--preflight-only"])
    assert wrapper.main() == 0
    receipt = tmp_path / "preflight.json"
    receipt.write_text(capsys.readouterr().out)
    selected = wrapper.review_round.load_google_selector_receipt(selector, expected_review_id="review-r1")
    wrapper.review_round.validate_google_preflight_receipt(receipt, selected, expected_review_id="review-r1")


@pytest.mark.parametrize("state", ["missing", "drifted"])
def test_c72_preflight_refuses_unprovisioned_profile(tmp_path, monkeypatch, capsys, state):
    home = tmp_path / "home"
    directory = home / ".gemini/config/agents"
    directory.mkdir(parents=True)
    if state == "drifted":
        (directory / "triad-codex-readonly-review.md").write_text("tools: []\n")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _: (1, 3, 2))
    monkeypatch.setattr(wrapper._common, "_run_once", lambda *a, **k: pytest.fail("provider started"))
    selector, _, _ = _google_selector_fixture(tmp_path)
    monkeypatch.setattr(sys, "argv", ["antigravity_wrapper.py", "--prompt", "preflight",
        "--cwd", str(tmp_path), "--sandbox", "read-only", "--model", "gemini-4-argon-high",
        "--effort", "high", "--expected-review-id", "review-r1",
        "--google-selector-receipt", str(selector), "--preflight-only"])
    assert wrapper.main() == 65
    output = capsys.readouterr()
    assert output.out == ""
    assert "profile" in output.err.lower()
