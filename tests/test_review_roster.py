"""C12: real project configuration flows through the public resolver command."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import review_round


def write_config(project, legs=None, *, raw=None):
    path = project / ".agents" / "triad-review-legs.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(raw if raw is not None else json.dumps({
        "schema": "triad-review-legs.v2", "legs": legs,
    }))
    return path


def resolve(project, capsys):
    try:
        code = review_round.main(["resolve-roster", "--project-root", str(project)])
    except SystemExit as error:
        code = error.code
    output = capsys.readouterr()
    return code, output.out, output.err


def test_c12_absent_uses_three_families_without_dispatch(tmp_path, capsys, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("configuration resolution must not execute a provider or probe")
    monkeypatch.setattr(review_round.subprocess, "run", forbidden)
    code, stdout, stderr = resolve(tmp_path, capsys)
    assert code == 0, stderr
    result = json.loads(stdout)
    assert result["config_path"] is None
    assert result["schema"] == "triad-review-legs.v2"
    assert result["enabled"] == ["claude", "codex", "google"]
    assert result["families"] == ["claude", "codex", "google"]
    assert len(result["legs"]) == 3
    assert result["capabilities_checked"] is False
    for entry in result["legs"]:
        assert entry["enabled"] is True
        assert isinstance(entry["timeout_s"], int) and entry["timeout_s"] > 0
    assert result["legs"][0]["claude"]["model"]
    assert result["legs"][1]["codex"]["model"]
    google = result["legs"][2]
    assert google["agy"]["model"] and google["gemini"]["model"]


def test_c12_merge_by_name_preserves_unmentioned_fields_and_order(tmp_path, capsys):
    config = write_config(tmp_path, [
        {"name": "google", "agy": {"model": "trial-model"}},
        {"name": "claude", "enabled": False},
        {"name": "codex", "codex": {"reasoning": "high"}},
    ])
    code, stdout, stderr = resolve(tmp_path, capsys)
    assert code == 0, stderr
    result = json.loads(stdout)
    assert result["config_path"] == str(config.resolve())
    assert [x["name"] for x in result["legs"]] == ["claude", "codex", "google"]
    assert result["enabled"] == ["codex", "google"]
    assert result["families"] == ["codex", "google"]
    assert result["legs"][1]["codex"]["reasoning"] == "high"
    assert result["legs"][2]["agy"] == {"model": "trial-model", "effort": "high"}
    assert result["legs"][2]["gemini"]["model"]


def test_c12_new_informational_same_family_is_an_ordinary_enabled_entry(tmp_path, capsys):
    extra = {"name": "trial", "vendor": "codex", "enabled": True,
             "acceptance": "informational", "timeout_s": 901,
             "codex": {"model": None, "reasoning": "medium"}}
    write_config(tmp_path, [extra])
    code, stdout, stderr = resolve(tmp_path, capsys)
    assert code == 0, stderr
    result = json.loads(stdout)
    assert result["legs"][-1] == extra
    assert result["enabled"] == ["claude", "codex", "google", "trial"]
    assert result["families"] == ["claude", "codex", "google"]


@pytest.mark.parametrize("legs", [
    [{"name": "codex"}, {"name": "codex", "enabled": False}],
    [{"name": "trial"}],
    [{"name": "claude", "codex": {"model": "wrong-family"}}],
    [{"name": "google", "agy": {"model": "<dispatch-time slug>"}}],
    [{"name": "codex", "codex": {"reasoning": "${EFFORT}"}}],
    [{"name": "claude", "enabled": "false"}],
    [{"name": "claude", "timeout_s": True}],
    [{"name": "claude", "timeout_s": 0}],
    [{"name": "codex", "typo": True}],
    [{"name": "codex", "enabled": False, "typo": True}],
    [{"name": "trial", "vendor": "google", "enabled": True,
      "acceptance": "participating", "timeout_s": 600,
      "google": {"route": "gemini"}, "agy": {"model": "known"}}],
])
def test_c12_invalid_configuration_refuses_instead_of_using_defaults(tmp_path, capsys, legs):
    write_config(tmp_path, legs)
    code, stdout, stderr = resolve(tmp_path, capsys)
    assert code == 2
    assert stdout == ""
    assert "invalid roster" in stderr


@pytest.mark.parametrize("raw", [
    '{"schema":"triad-review-legs.v2","legs":[],"legs":[]}',
    '{"schema":"triad-review-legs.v2","legs":[{"name":"codex","name":"claude"}]}',
    '{"schema":"triad-review-legs.v2","legs":[],"unknown":true}',
    '{"schema":"triad-review-legs.v1","legs":[]}',
    '{"schema":"triad-review-legs.v2","legs":[{"name":"claude","timeout_s":NaN}]}',
    "null", "{broken",
])
def test_c12_original_json_and_version_are_not_lossily_normalized(tmp_path, capsys, raw):
    write_config(tmp_path, raw=raw)
    code, stdout, stderr = resolve(tmp_path, capsys)
    assert code == 2 and stdout == ""
    assert "invalid roster" in stderr


@pytest.mark.parametrize("kind", ["file-link", "directory-link", "directory", "invalid-utf8"])
def test_c12_present_but_invalid_file_is_never_treated_as_absent(tmp_path, capsys, kind):
    path = write_config(tmp_path, [])
    if kind == "directory-link":
        path.parent.rename(tmp_path / "elsewhere")
        (tmp_path / ".agents").symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    else:
        path.unlink()
        if kind == "file-link":
            path.symlink_to(tmp_path / "absent")
        elif kind == "directory":
            path.mkdir()
        else:
            path.write_bytes(b"\xff")
    code, stdout, stderr = resolve(tmp_path, capsys)
    assert code == 2 and stdout == ""
    assert "invalid roster" in stderr


def test_c12_second_project_cannot_inherit_first_project_overrides(tmp_path, capsys):
    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    second.mkdir()
    write_config(first, [{"name": "claude", "enabled": False}])
    assert resolve(first, capsys)[0] == 0
    code, stdout, stderr = resolve(second, capsys)
    assert code == 0, stderr
    assert json.loads(stdout)["enabled"] == ["claude", "codex", "google"]
