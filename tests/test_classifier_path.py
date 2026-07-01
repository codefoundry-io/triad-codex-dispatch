import importlib, os, sys
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
