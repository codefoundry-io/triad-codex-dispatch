"""C12/C23: invalid inputs refuse before changing invocation custody."""
import json
from pathlib import Path

import pytest

from test_v2_rounds import round_fixture, worktree, start
from test_v2_round_cli import cli_files, native_files
import review_round


@pytest.mark.parametrize("name", ["claude", "codex"])
@pytest.mark.parametrize("reserved", ["read-evidence.json", "provider-receipt.json",
                                     "terminal.json", "terminal.json.sha256"])
def test_reserved_evidence_input_refuses_without_partial_writes_and_can_recover(
        round_fixture, name, reserved, capsys):
    fixture = round_fixture()
    mod, basis, *_ = fixture
    item = start(fixture, name)
    folder = Path(item["folder"])
    if name == "claude":
        log, _ = cli_files(item, basis)
        command = ["v2-record-cli", "--run-log", str(log)]
    else:
        receipt, result = native_files(item)
        command = ["v2-record-native", "--host-receipt", str(receipt), "--result-file", str(result)]
    command += ["--basis", basis["basis_file"], "--leg", name]
    evidence = folder / reserved
    evidence.write_text(json.dumps({"review_binding": item["binding"],
                                   "exposure": "observed", "observations": []}))

    def snapshot():
        return {str(path.relative_to(folder)): path.read_bytes()
                for path in folder.rglob("*") if path.is_file()}

    before = snapshot()
    assert review_round.main([*command, "--read-evidence", str(evidence)]) == 2
    assert snapshot() == before, "refusal must not leave a partial result or terminal"
    assert capsys.readouterr().err.startswith("review_round:")
    original = evidence.read_bytes()
    renamed = evidence.with_name("host-read-observations.json")
    evidence.rename(renamed)
    assert review_round.main([*command, "--read-evidence", str(renamed)]) == 0
    assert renamed.read_bytes() == original
    assert mod.collect(Path(basis["basis_file"]))["legs"][name]["state"] == "COMPLETE"


@pytest.mark.parametrize("field,value", [("review_id", 23), ("project_root", 23),
                                         ("prepared_dir", []), ("worktree", {})])
def test_malformed_request_values_use_the_command_refusal_contract_before_preparation(
        round_fixture, field, value, capsys):
    _, _, root, _, request, calls = round_fixture(make_basis=False)
    request[field] = value
    request_file = root.parent / "malformed-request.json"
    request_file.write_text(json.dumps(request))
    assert review_round.main(["v2-create", "--request-file", str(request_file), "--root", str(root)]) == 2
    error = capsys.readouterr().err
    assert error.startswith("review_round:") and "Traceback" not in error
    assert calls == []
    assert not (root / "basis-v2.json").exists()
    assert not (root / "preflight-v2").exists()
