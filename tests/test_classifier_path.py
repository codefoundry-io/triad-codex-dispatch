import importlib, os, sys
import pytest
sys.path.insert(0, "bin")

def test_default_path_is_namespaced(monkeypatch):
    monkeypatch.delenv("TRIAD_CLASSIFIER_EXTENSION", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    c = importlib.reload(importlib.import_module("_common"))
    p = c._classifier_extension_path()
    assert p.parts[-2:] == ("triad-codex-dispatch", "classifier-patches.json")

def test_env_override_wins(monkeypatch, tmp_path):
    target = tmp_path / "x.json"
    monkeypatch.setenv("TRIAD_CLASSIFIER_EXTENSION", str(target))
    c = importlib.reload(importlib.import_module("_common"))
    assert c._classifier_extension_path() == target


def test_pydantic_import_requires_explicit_opt_in(monkeypatch):
    pytest.importorskip("pydantic")
    monkeypatch.delenv("TRIAD_ALLOW_PYDANTIC_IMPORT", raising=False)
    c = importlib.reload(importlib.import_module("_common"))
    with pytest.raises(PermissionError):
        c.load_pydantic_class("json:JSONDecoder")
