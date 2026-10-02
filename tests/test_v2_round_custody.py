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


@pytest.mark.parametrize("incomplete", [False, True])
def test_C64_stop_or_separate_exception_does_not_change_outcome(round_fixture, incomplete):
    fixture = round_fixture()
    mod, basis, root, _, request, _ = fixture
    for name in basis["enabled"]:
        if incomplete and name == "google":
            continue
        finish(fixture, start(fixture, name), changes={
            "verdict": "DO NOT MERGE", "open_questions": ["unresolved"],
        } if name == "trial" else {})
    basis_file = Path(basis["basis_file"])
    before = mod.collect(basis_file)
    assert before["status"] == ("INCOMPLETE" if incomplete else "BLOCKED")
    (root / "owner-stop.md").write_text("Stop the review. Separate exception: proceed despite nonapproval.\n")
    assert mod.collect(basis_file) == before
    bound_input = Path(request["prepared_dir"]) / "TASK.md"
    bound_input.write_text(bound_input.read_text() + "Owner exception: approve.\n")
    with pytest.raises(ValueError):
        mod.collect(basis_file)


@pytest.mark.parametrize("state", ["missing", "failed", "invalid"])
def test_incomplete_precedes_valid_negative_and_retains_raw_evidence(round_fixture, state):
    fixture = round_fixture()
    mod, basis, *_ = fixture
    for name in basis["enabled"]:
        if name == "codex" and state == "missing":
            continue
        allocation = start(fixture, name)
        finish(fixture, allocation, failed=name == "codex" and state == "failed",
               raw_override=b"invalid original" if name == "codex" and state == "invalid" else None,
               changes={"verdict": "DO NOT MERGE", "open_questions": ["unresolved"]}
               if name == "trial" else {})
        if name == "codex" and state == "invalid":
            assert Path(allocation["result_file"]).read_bytes() == b"invalid original"
    assert mod.collect(Path(basis["basis_file"]))["status"] == "INCOMPLETE"


@pytest.mark.parametrize("changes", [
    {"open_questions": ["unresolved"]},
    {"findings": [{"path": "source.py", "line": 1, "severity": "must-fix", "summary": "fixture",
                   "trigger": "fixture", "evidence": "source.py:1", "context_known": True}]},
])
def test_safe_with_blocker_or_question_remains_invalid_and_incomplete(round_fixture, changes):
    fixture = round_fixture()
    mod, basis, *_ = fixture
    for name in basis["enabled"]:
        terminal = finish(fixture, start(fixture, name), changes=changes if name == "trial" else {})
        assert terminal["state"] == ("INVALID" if name == "trial" else "COMPLETE")
    assert mod.collect(Path(basis["basis_file"]))["status"] == "INCOMPLETE"
