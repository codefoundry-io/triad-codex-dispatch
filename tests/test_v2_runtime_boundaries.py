"""Real wrapper transport and preparation failures retain their observed meaning."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from test_v2_adapters import adapter_case
from test_v2_rounds import round_fixture, worktree, start, finish
from test_v2_producer_adapter import verdict
import review_round


@pytest.mark.parametrize("agent", ["Plan\n", "Plan\r", "Plan\x00"])
def test_invalid_agent_refused_before_capability_probe(adapter_case, agent):
    mod, roster, kwargs, calls, _ = adapter_case()
    roster["legs"][0]["claude"]["agent"] = agent
    with pytest.raises(ValueError):
        mod.prepare_adapters(roster, **kwargs)
    assert calls == []


def test_symlink_parent_is_refused_before_creating_external_child(adapter_case):
    mod, roster, kwargs, _, _ = adapter_case()
    outside = kwargs["cwd"].parent / "unselected"
    outside.mkdir()
    link = kwargs["cwd"] / "linked-custody"
    link.symlink_to(outside, target_is_directory=True)
    kwargs["receipt_root"] = link / "child"
    with pytest.raises(ValueError):
        mod.prepare_adapters(roster, **kwargs)
    assert list(outside.iterdir()) == []


def test_relative_custody_refused_before_writing(adapter_case, monkeypatch):
    mod, roster, kwargs, _, _ = adapter_case()
    monkeypatch.chdir(kwargs["cwd"])
    kwargs["receipt_root"] = Path("relative-custody")
    with pytest.raises(ValueError):
        mod.prepare_adapters(roster, **kwargs)
    assert not (kwargs["cwd"] / "relative-custody").exists()


@pytest.mark.parametrize("document", [{}, {"minimum_preflight_version": "2.1.205", "models": {"Opus 5": {}}}])
def test_invalid_capability_document_leaves_preparation_failure(adapter_case, monkeypatch, document):
    mod, roster, kwargs, calls, _ = adapter_case()
    payload_root = kwargs["cwd"].parent / "bad-catalog"
    data = payload_root / "bin/data"
    data.mkdir(parents=True)
    (data / "claude-capabilities.json").write_text(json.dumps(document))
    monkeypatch.setattr(mod, "ROOT", payload_root)
    with pytest.raises(ValueError):
        mod.prepare_adapters(roster, **kwargs)
    assert calls == []
    failure = kwargs["receipt_root"] / "claude/attempt-1/preparation-failure.json"
    assert json.loads(failure.read_text())["provider_started"] is False


def test_retry_preparation_failure_preserves_receipts_and_can_retry_again(round_fixture, monkeypatch):
    fixture = round_fixture()
    mod, basis, *_ = fixture
    allocation = start(fixture, "claude")
    finish(fixture, allocation, failed=True)
    prepare = mod.prepare_adapters
    retained = []

    def partial(roster, **kwargs):
        folder = kwargs["receipt_root"] / "claude" / f"attempt-{kwargs['attempt']}"
        folder.mkdir(parents=True)
        marker = folder / "failure.json"
        marker.write_text("original preparation evidence")
        if not retained:
            retained.append(marker)
            raise ValueError("temporary capability probe failure")
        return prepare(roster, **kwargs)

    monkeypatch.setattr(mod, "prepare_adapters", partial)
    with pytest.raises(ValueError):
        mod.allocate_attempt(Path(basis["basis_file"]), "claude", diagnosis="provider failure diagnosed")
    second = mod.allocate_attempt(Path(basis["basis_file"]), "claude", diagnosis="preparation fault diagnosed")
    assert retained[0].read_text() == "original preparation evidence"
    assert second["binding"]["attempt"] == 2
    finish(fixture, second)
    assert mod.collect(Path(basis["basis_file"]))["legs"]["claude"]["state"] == "COMPLETE"


def test_actual_claude_wrapper_receipt_keeps_unexposed_runtime_version(round_fixture, tmp_path, capsys):
    binary = tmp_path / "fixture-claude"
    # A deterministic vendor stand-in exercises the actual subprocess/stdin,
    # wrapper extraction, raw run-log and collector without paid inference.
    source = (f"#!{sys.executable}\nimport json, sys\n"
              "prompt = sys.stdin.read()\nassert prompt\n"
              "schema = json.loads(sys.argv[sys.argv.index('--json-schema') + 1])\n"
              f"data = {verdict()!r}\n"
              "data.update({key: spec['const'] for key, spec in schema['properties'].items() if 'const' in spec})\n"
              "print(json.dumps({'result': '', 'structured_output': data}))\n")
    binary.write_text(source)
    binary.chmod(0o755)

    def transform(adapters):
        adapters["claude"].update(binary=str(binary), cli_version="2.1.271")
        return adapters

    fixture = round_fixture(adapter_transform=transform)
    mod, basis, *_ = fixture
    allocation = start(fixture, "claude")
    invoke = allocation["invocation"]
    with Path(invoke["stdout_file"]).open("xb") as output, Path(invoke["stderr_file"]).open("xb") as error:
        terminal = subprocess.run(invoke["argv"], env={**os.environ, **invoke["env"]},
                                  stdout=output, stderr=error, timeout=30)
    assert terminal.returncode == 0, Path(invoke["stderr_file"]).read_text()
    logs = list((Path(allocation["folder"]) / "logs/claude/runs").glob("*.json"))
    assert len(logs) == 1
    raw = json.loads(logs[0].read_text())
    assert raw["transport"]["cli_version"] is None
    assert raw["transport"]["stdin_delivery"] == "complete"
    assert review_round.main(["v2-record-cli", "--basis", basis["basis_file"], "--leg", "claude",
                              "--run-log", str(logs[0])]) == 0
    assert json.loads(capsys.readouterr().out)["state"] == "COMPLETE"
    stored = json.loads(Path(allocation["receipt_file"]).read_text())
    assert stored["transport"]["cli_version"] is None
    assert mod.collect(Path(basis["basis_file"]))["legs"]["claude"]["state"] == "COMPLETE"


def test_prepared_directory_selects_packet_as_reviewer_cwd_and_basis(round_fixture):
    mod, _, root, _, request, _ = round_fixture(make_basis=False)
    request["mode"] = "prepared-directory"
    basis = mod.create_basis(request, root=root)
    for name in basis["enabled"]:
        allocation = mod.allocate_attempt(Path(basis["basis_file"]), name)
        assert allocation["adapter"]["cwd"] == request["prepared_dir"]
        if name == "codex":
            assert f"The reviewed basis is at {request['prepared_dir']}." in allocation["invocation"]["arguments"]["message"]
