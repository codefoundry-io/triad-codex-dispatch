"""C77: ordinary extension edits cannot inject wrapper/unknown result classes."""
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common


def extension(tmp_path, monkeypatch, cli, entries):
    path = tmp_path / "extension.json"
    raw = json.dumps({cli: {"vendor_exit_map": entries}}) + "\n"
    path.write_text(raw)
    monkeypatch.setenv("TRIAD_CLASSIFIER_EXTENSION", str(path))
    return path, raw


@pytest.mark.parametrize("cli", ["codex", "claude", "gemini", "antigravity"])
@pytest.mark.parametrize("bad", ["timeout", "schema-fail", "task-blocked",
    "fanout-spawn-error", "config-conflict", "ok", "unknown", "not-a-contract-token"])
def test_c77_unsupported_exit_class_cannot_escape_loader(tmp_path, monkeypatch, capsys, cli, bad):
    path, raw = extension(tmp_path, monkeypatch, cli, {"7": bad, "8": "server-capacity"})
    loaded = _common._load_classifier_extension()
    assert loaded[cli]["vendor_exit_map"] == {"8": "server-capacity"}
    assert len(capsys.readouterr().err.splitlines()) == 1
    assert _common.classify(cli, "", "", 1, vendor_exit_code=7) == "unknown"
    assert _common.classify(cli, "", "", 1, vendor_exit_code=8) == "server-capacity"
    assert path.read_text() == raw


@pytest.mark.parametrize("cli", ["codex", "claude", "gemini", "antigravity"])
@pytest.mark.parametrize("classification", ["server-capacity", "cli-subscription-cap",
    "token-limit", "oauth-env", "schema-rejected", "extraction-error"])
def test_c77_curated_supported_failure_classes_remain(tmp_path, monkeypatch, cli, classification):
    path, raw = extension(tmp_path, monkeypatch, cli, {"7": classification})
    assert _common.classify(cli, "", "", 1, vendor_exit_code=7) == classification
    assert path.read_text() == raw


@pytest.mark.parametrize("cli", ["codex", "claude", "gemini", "antigravity"])
def test_c77_zero_keys_are_removed_under_classifier_integer_semantics(tmp_path, monkeypatch, capsys, cli):
    entries = {key: "server-capacity" for key in ("0", "00", "+0", "-0", " 0 ")}
    entries["7"] = "token-limit"
    path, raw = extension(tmp_path, monkeypatch, cli, entries)
    assert _common._load_classifier_extension()[cli]["vendor_exit_map"] == {"7": "token-limit"}
    assert len(capsys.readouterr().err.splitlines()) == 5
    assert _common.classify(cli, "", "", 0, vendor_exit_code=0) == "ok"
    assert path.read_text() == raw


def test_c77_wrong_typed_values_do_not_discard_valid_siblings(tmp_path, monkeypatch):
    path, raw = extension(tmp_path, monkeypatch, "gemini",
                          {"7": [], "8": None, "9": 42, "10": "token-limit"})
    assert _common._load_classifier_extension()["gemini"]["vendor_exit_map"] == {"10": "token-limit"}
    assert _common.classify("gemini", "", "", 1, vendor_exit_code=10) == "token-limit"
    assert path.read_text() == raw
