"""Provider-free installed AGY profiles for existing formal-review fixtures."""
import hashlib
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
import _agy_agent


def profile_receipt(web=False):
    name, body = _agy_agent.profile(web)
    return {"agent": name, "agent_path": str(_agy_agent.agents_dir() / f"{name}.md"),
            "agent_sha256": hashlib.sha256(body).hexdigest()}


@pytest.fixture(autouse=True)
def installed_agy_profiles(request, tmp_path_factory, monkeypatch):
    # New C72 tests own their missing/drifted/installed state explicitly.
    if request.module.__name__ == "test_agy_search_profile":
        return
    directory = tmp_path_factory.mktemp("agy-profiles")
    _agy_agent.install(directory)
    monkeypatch.setattr(_agy_agent, "agents_dir", lambda: directory)
