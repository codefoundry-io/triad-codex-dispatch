"""Shared context transport and preparation-date custody, without provider calls."""
import copy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_v2_review_prompts import arguments, renderer
from test_v2_rounds import round_fixture, worktree, start, finish, implementation


class PreparationClock:
    @classmethod
    def now(cls, tz):
        assert tz == timezone.utc
        return datetime(2026, 10, 10, 23, 59, 59, tzinfo=tz)


class NoRenderClock:
    @classmethod
    def now(cls, tz):
        raise AssertionError("render/retry must reuse the prepared date")


def test_prepared_utc_date_survives_all_legs_and_retry(round_fixture, monkeypatch):
    mod = implementation()
    monkeypatch.setattr(mod, "datetime", PreparationClock, raising=False)
    fixture = round_fixture()
    _, basis, *_ = fixture
    assert basis.get("review_date") == "2026-10-10"
    monkeypatch.setattr(mod, "datetime", NoRenderClock)
    for name in basis["enabled"]:
        allocation = start(fixture, name)
        text = Path(allocation["prompt_file"]).read_text()
        assert "2026-10-10 (UTC)" in text and "<review-date>" not in text
        finish(fixture, allocation, failed=name == "trial")
    second = mod.allocate_attempt(Path(basis["basis_file"]), "trial", diagnosis="diagnosed fixture transport failure")
    assert second["binding"]["attempt"] == 2
    assert second["binding"]["content_digest"] == basis["content_digest"]
    assert "2026-10-10 (UTC)" in Path(second["prompt_file"]).read_text()
    finish(fixture, second)
    assert mod.collect(Path(basis["basis_file"]))["status"] == "AGREED"


def test_preparation_date_is_bound_for_allocation_and_collection(round_fixture, monkeypatch):
    monkeypatch.setattr(implementation(), "datetime", PreparationClock)
    mod, basis, *_ = round_fixture()
    assert "review_date" in basis
    path = Path(basis["basis_file"])
    changed = copy.deepcopy(basis)
    changed["review_date"] = "2026-10-11"
    assert changed["review_date"] != basis["review_date"]
    raw = mod._bytes(changed)
    path.write_bytes(raw)
    path.with_suffix(".json.sha256").write_text(mod._hash(raw) + "\n")
    with pytest.raises(ValueError, match="content digest mismatch"):
        mod.allocate_attempt(path, "codex")
    with pytest.raises(ValueError, match="content digest mismatch"):
        mod.collect(path)


@pytest.mark.parametrize("family", ["claude", "codex", "google"])
@pytest.mark.parametrize("web", [False, True])
def test_every_leg_renders_the_same_shared_context(tmp_path, family, web):
    mod = renderer()
    payload = mod.load_bundle()["common-clauses.md"]
    names = ("current-date", "deployment-context", "review-no-web", "review-web-permission",
             "severity-instruction", "code-purpose")
    assert all("## " + name + " (" in payload for name in names)
    # Extract expected fenced bytes independently of the production parser.
    common = {name: payload.split("## " + name + " (", 1)[1].split("```text\n", 1)[1]
              .split("\n```", 1)[0] for name in names}
    args = arguments(tmp_path, family)
    args["review_date"] = "2026-10-10"
    text = mod.render_prompt(**args, review_web_authorized=web)
    for name in ("deployment-context", "severity-instruction", "code-purpose"):
        assert text.count(common[name]) == 1
    assert common["current-date"].replace("<review-date>", "2026-10-10") in text
    selected = "review-web-permission" if web else "review-no-web"
    other = "review-no-web" if web else "review-web-permission"
    assert common[selected] in text and common[other] not in text


def test_host_only_clause_is_selected_by_header_marker(tmp_path, monkeypatch):
    mod = renderer()
    bundle = mod.load_bundle()
    # Rename an existing A-only clause in both its header and order. Its host
    # marker, not its historical identifier, still excludes it from B.
    bundle["leg-claude.md"] = bundle["leg-claude.md"].replace(
        "claude-output-shape-notice", "host-a-shape-fixture")
    monkeypatch.setattr(mod, "load_bundle", lambda: bundle)
    text = mod.render_prompt(**arguments(tmp_path, "claude"))
    assert "OUTPUT-SHAPE NOTICE:" not in text
    assert "<END-VERDICT>" not in text
