"""Runtime evidence is not an implementation input; policy bytes always are."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
import review_round_v2
from test_v2_rounds import round_fixture, worktree


@pytest.mark.parametrize("runtime_directory", ["_logs", "_debug"])
def test_toolkit_digest_ignores_only_wrapper_runtime_evidence(tmp_path, monkeypatch, runtime_directory):
    for directory in ("bin", "contracts", "prompts", "skills/triad-cross-family-review"):
        (tmp_path / directory).mkdir(parents=True)
    policy = tmp_path / "bin/policies/gemini-formal-readonly.toml"
    policy.parent.mkdir()
    policy.write_text('decision = "deny"\n')
    implementation = tmp_path / "bin/example.py"
    implementation.write_text('MODE = "review"\n')
    monkeypatch.setattr(review_round_v2, "TOOLKIT", tmp_path)
    before = review_round_v2._toolkit()
    runtime = tmp_path / "bin" / runtime_directory / "claude" / "audit.jsonl"
    runtime.parent.mkdir(parents=True)
    runtime.write_text('{"exit_code": 0}\n')
    assert review_round_v2._toolkit() == before
    runtime.write_text('{"exit_code": 1}\n')
    assert review_round_v2._toolkit() == before
    policy.write_text('decision = "allow"\n')
    after = review_round_v2._toolkit()
    assert after["bin/policies/gemini-formal-readonly.toml"] != before["bin/policies/gemini-formal-readonly.toml"]
    assert after["bin/example.py"] == before["bin/example.py"]


@pytest.mark.parametrize("managed", [
    "bin/triad_dispatch_lib/verdict.py",
    "bin/triad_dispatch_lib/data/leg-verdict.schema.json",
    "contracts/library-adoption.json",
])
def test_library_inputs_are_bound_and_mutation_refuses_prepared_basis(round_fixture, monkeypatch, tmp_path, managed):
    # Use a miniature toolkit tree so the source package is never mutated.
    toolkit = tmp_path / "toolkit"
    target = toolkit / managed
    target.parent.mkdir(parents=True)
    target.write_bytes(b"prepared shared implementation or resource")
    monkeypatch.setattr(review_round_v2, "TOOLKIT", toolkit)
    mod, basis, *_ = round_fixture()
    assert managed in basis["toolkit"]
    target.write_bytes(b"changed shared implementation or resource")
    with pytest.raises(ValueError, match="toolkit"):
        mod.allocate_attempt(Path(basis["basis_file"]), "codex")
    with pytest.raises(ValueError, match="toolkit"):
        mod.collect(Path(basis["basis_file"]))
