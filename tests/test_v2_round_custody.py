"""Malformed answers and retry history remain evidence, never admission."""
from pathlib import Path

import pytest

from test_v2_rounds import round_fixture, worktree, start, finish


@pytest.mark.parametrize("answer", [b"not JSON", b'{"review_id":"a","review_id":"b"}', b'{}'])
def test_invalid_original_answer_is_retained_and_not_transport_retry(round_fixture, answer):
    fixture = round_fixture()
    mod, basis, *_ = fixture
    allocation = start(fixture, "codex")
    terminal = finish(fixture, allocation, raw_override=answer)
    assert terminal["state"] == "INVALID"
    assert Path(allocation["result_file"]).read_bytes() == answer
    assert Path(allocation["receipt_file"]).is_file()
    assert mod.collect(Path(basis["basis_file"]))["legs"]["codex"]["state"] == "INVALID"
    with pytest.raises(ValueError):
        mod.allocate_attempt(Path(basis["basis_file"]), "codex", diagnosis="regenerate malformed answer")


def test_receipt_answer_mismatch_is_retained_without_admission(round_fixture):
    fixture = round_fixture()
    allocation = start(fixture, "codex")
    result = finish(fixture, allocation, receipt_changes={"validated": None})
    assert result["state"] == "INVALID"
    assert Path(allocation["result_file"]).is_file()


def test_retry_cannot_discard_previous_terminal_history(round_fixture):
    fixture = round_fixture()
    mod, basis, *_ = fixture
    first = start(fixture, "trial")
    finish(fixture, first, failed=True)
    second = mod.allocate_attempt(Path(basis["basis_file"]), "trial", diagnosis="confirmed outage")
    finish(fixture, second)
    (Path(first["folder"]) / "terminal.json").unlink()
    with pytest.raises(ValueError):
        mod.collect(Path(basis["basis_file"]))


def test_native_unexposed_stdin_is_not_fabricated_into_used_delivery(round_fixture):
    fixture = round_fixture()
    mod, basis, *_ = fixture
    allocation = start(fixture, "codex")
    adapter = basis["adapters"]["codex"]
    transport = {"schema_version": 2, "route": "native", "binary": None,
                 "cli_version": None, "attempt": 1, "stdin_delivery": "unexposed"}
    result = finish(fixture, allocation, receipt_changes={"transport": transport})
    assert result["state"] == "COMPLETE"
    assert adapter["binary"] is None
