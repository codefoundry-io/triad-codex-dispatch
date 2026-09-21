"""Runtime evidence is not an implementation input; policy bytes always are."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
import review_round_v2


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
