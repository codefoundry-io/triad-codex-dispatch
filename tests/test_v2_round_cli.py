"""Operational v2 commands admit actual host observations, never model receipts."""
import json
from pathlib import Path

import pytest

from test_v2_rounds import round_fixture, worktree, start, finish
from test_v2_producer_adapter import verdict
import review_round


def native_files(allocation, *, text=None, terminal="completed"):
    folder = Path(allocation["folder"])
    raw = json.dumps(verdict(**allocation["binding"])) if text is None else text
    result = folder / "native-final.txt"
    result.write_text(raw)
    receipt = folder / "native-host.json"
    receipt.write_text(json.dumps({"review_binding": allocation["binding"],
        "agent_id": "native-child-" + allocation["binding"]["leg_name"],
        "terminal_status": terminal, "runtime_model": None, "runtime_effort": None}))
    return receipt, result


def cli_files(allocation, basis, *, failed=False):
    folder = Path(allocation["folder"])
    adapter = allocation["adapter"]
    cli = "antigravity" if adapter["route"] == "agy" else adapter["transport_route"]
    run_dir = folder / "logs" / cli / "runs"
    run_dir.mkdir(parents=True)
    output = folder / "wrapper.stdout"
    data = verdict(**allocation["binding"])
    output.write_text("" if failed else json.dumps(data))
    (folder / "wrapper.stderr").write_text("wrapper diagnostic")
    run_log = run_dir / "provider.json"
    run_log.write_text(json.dumps({"cli": cli, "review_binding": allocation["binding"],
        "wrapper_cmd": allocation["invocation"]["argv"][1:],
        "vendor_cmd": [adapter["binary"], "--model", adapter["model"]],
        "exit_code": 1 if failed else 0, "vendor_exit_code": 1 if failed else 0,
        "classification": "unknown" if failed else "ok", "runtime_identity": "unexposed",
        "stdout": "original provider envelope, not reformatted", "stderr": "provider diagnostic",
        "final_answer": "" if failed else json.dumps(data), "validated": None if failed else data,
        "transport": {"schema_version": 2, "route": adapter["transport_route"],
            "binary": adapter["binary"], "cli_version": adapter["cli_version"],
            "attempt": allocation["binding"]["attempt"],
            "stdin_delivery": "complete" if adapter["family"] == "claude" else "not-used"}}))
    return run_log, output


def test_native_cli_records_verbatim_final_and_unexposed_metadata(round_fixture, capsys):
    fixture = round_fixture()
    mod, basis, *_ = fixture
    rc = review_round.main(["v2-allocate", "--basis", basis["basis_file"], "--leg", "codex"])
    assert rc == 0
    allocation = json.loads(capsys.readouterr().out)
    receipt, result = native_files(allocation)
    rc = review_round.main(["v2-record-native", "--basis", basis["basis_file"], "--leg", "codex",
                            "--host-receipt", str(receipt), "--result-file", str(result)])
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["state"] == "COMPLETE"
    assert Path(allocation["result_file"]).read_bytes() == result.read_bytes()
    stored = json.loads(Path(allocation["receipt_file"]).read_text())
    assert stored["runtime_identity"] == "unexposed"
    assert stored["transport"]["binary"] is None and stored["transport"]["cli_version"] is None
    assert mod.collect(Path(basis["basis_file"]))["legs"]["codex"]["state"] == "COMPLETE"


@pytest.mark.parametrize("name", ["claude", "google"])
def test_cli_record_owns_original_run_log_and_wrapper_stdout(round_fixture, capsys, name):
    fixture = round_fixture()
    mod, basis, *_ = fixture
    allocation = start(fixture, name)
    log, output = cli_files(allocation, basis)
    assert review_round.main(["v2-record-cli", "--basis", basis["basis_file"], "--leg", name,
                              "--run-log", str(log)]) == 0
    assert json.loads(capsys.readouterr().out)["state"] == "COMPLETE"
    assert Path(allocation["result_file"]).read_bytes() == output.read_bytes()
    stored = json.loads(Path(allocation["receipt_file"]).read_text())
    assert stored["stdout"] == "original provider envelope, not reformatted"
    log.write_text(log.read_text() + " ")
    with pytest.raises(ValueError):
        mod.collect(Path(basis["basis_file"]))


@pytest.mark.parametrize("fault", ["sibling-log", "altered-command", "wrong-source-kind"])
def test_cli_ingestion_refuses_wrong_owner_or_invocation(round_fixture, capsys, fault):
    fixture = round_fixture()
    _, basis, root, *_ = fixture
    allocation = start(fixture, "claude")
    log, _ = cli_files(allocation, basis)
    if fault == "sibling-log":
        wrong = root / "results" / "other.json"
        wrong.write_bytes(log.read_bytes())
        log = wrong
    elif fault == "altered-command":
        value = json.loads(log.read_text())
        value["wrapper_cmd"] += ["--web"]
        log.write_text(json.dumps(value))
    else:
        value = json.loads(log.read_text())
        value["cli"] = "gemini"
        log.write_text(json.dumps(value))
    assert review_round.main(["v2-record-cli", "--basis", basis["basis_file"], "--leg", "claude",
                              "--run-log", str(log)]) != 0
    assert not (Path(allocation["folder"]) / "terminal.json").exists()


def test_native_malformed_final_retains_raw_terminal_without_admission(round_fixture, capsys):
    fixture = round_fixture()
    _, basis, *_ = fixture
    allocation = start(fixture, "codex")
    receipt, result = native_files(allocation, text='{"review_id":"a","review_id":"b"}')
    assert review_round.main(["v2-record-native", "--basis", basis["basis_file"], "--leg", "codex",
                              "--host-receipt", str(receipt), "--result-file", str(result)]) == 0
    assert json.loads(capsys.readouterr().out)["state"] == "INVALID"
    assert Path(allocation["result_file"]).read_bytes() == result.read_bytes()


def test_native_exposed_model_mismatch_does_not_count_as_selected_reviewer(round_fixture, capsys):
    fixture = round_fixture()
    _, basis, *_ = fixture
    allocation = start(fixture, "codex")
    receipt, result = native_files(allocation)
    data = json.loads(receipt.read_text())
    data["runtime_model"] = "gpt-6-astra"
    receipt.write_text(json.dumps(data))
    assert review_round.main(["v2-record-native", "--basis", basis["basis_file"], "--leg", "codex",
                              "--host-receipt", str(receipt), "--result-file", str(result)]) == 0
    assert json.loads(capsys.readouterr().out)["state"] == "INVALID"


def test_failed_start_is_recorded_without_inventing_provider_version(round_fixture, capsys):
    fixture = round_fixture()
    mod, basis, *_ = fixture
    allocation = start(fixture, "claude")
    record = Path(allocation["folder"]) / "launch-failure.json"
    record.write_text(json.dumps({"review_binding": allocation["binding"],
        "provider_started": False, "exit_code": 2, "stderr": "executable could not start"}))
    assert review_round.main(["v2-record-start-failure", "--basis", basis["basis_file"], "--leg", "claude",
                              "--host-receipt", str(record)]) == 0
    terminal = json.loads(capsys.readouterr().out)
    assert terminal["state"] == "FAILED_TO_RUN"
    receipt = json.loads(Path(allocation["receipt_file"]).read_text())
    assert receipt["transport"]["stdin_delivery"] == "not-started"
    assert receipt["transport"]["cli_version"] is None
    retry = mod.allocate_attempt(Path(basis["basis_file"]), "claude", diagnosis="missing executable diagnosed")
    assert retry["binding"]["attempt"] == 2


def test_explicit_v2_collector_reports_incomplete_without_rewriting_legacy_wire(round_fixture, capsys):
    fixture = round_fixture()
    _, basis, *_ = fixture
    assert review_round.main(["v2-collect", "--basis", basis["basis_file"]]) == 0
    outcome = json.loads(capsys.readouterr().out)
    assert outcome["status"] == "INCOMPLETE" and len(outcome["missing"]) == 4
    assert "SAFE" not in outcome


def test_preparation_failure_can_resume_without_deleting_or_reusing_partial_receipts(round_fixture, monkeypatch):
    mod, _, root, _, request, _ = round_fixture(make_basis=False)
    prepare = mod.prepare_adapters
    first_failure = []

    def partial(roster, **kwargs):
        receipt_root = kwargs["receipt_root"]
        receipt_root.mkdir(parents=True, exist_ok=True)
        partial_file = receipt_root / "partial.json"
        with partial_file.open("x") as handle:
            handle.write('{"provider_started":false}')
        if not first_failure:
            first_failure.append(partial_file)
            raise ValueError("known preparation fault before dispatch")
        return prepare(roster, **kwargs)

    monkeypatch.setattr(mod, "prepare_adapters", partial)
    with pytest.raises(ValueError):
        mod.create_basis(request, root=root)
    completed = mod.create_basis(request, root=root)
    assert first_failure[0].read_text() == '{"provider_started":false}'
    assert completed["enabled"] == ["claude", "codex", "google", "trial"]
    assert mod.collect(Path(completed["basis_file"]))["status"] == "INCOMPLETE"


def test_boolean_attempt_in_read_receipt_cannot_equal_integer_binding(round_fixture):
    fixture = round_fixture()
    allocation = start(fixture, "codex")
    reads = {"review_binding": {**allocation["binding"], "attempt": True},
             "exposure": "unexposed", "observations": None}
    with pytest.raises(ValueError):
        finish(fixture, allocation, reads=reads)
