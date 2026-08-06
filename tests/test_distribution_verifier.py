from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_distribution.py"


def _load_verifier():
    assert SCRIPT.is_file(), "distribution verifier is missing"
    spec = importlib.util.spec_from_file_location("verify_distribution", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "source"
    (repo / ".codex-plugin").mkdir(parents=True)
    (repo / "skills" / "triad-cross-family-review").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / ".gitignore").write_text("_runs/\n", encoding="utf-8")
    (repo / ".codex-plugin" / "plugin.json").write_text(
        json.dumps({"name": "triad-codex-dispatch", "version": "0.2.533"}) + "\n",
        encoding="utf-8",
    )
    (repo / "skills" / "triad-cross-family-review" / "SKILL.md").write_text(
        "---\nname: triad-cross-family-review\n---\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_packaged.py").write_text(
        "def test_packaged_bytes():\n    assert True\n",
        encoding="utf-8",
    )
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Distribution Test")
    _git(repo, "config", "user.email", "distribution@example.invalid")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "fixture")
    return repo


def test_verifier_rejects_existing_output_directory(fixture_repo: Path) -> None:
    verifier = _load_verifier()
    output = fixture_repo / "_runs" / "distribution" / "existing"
    output.mkdir(parents=True)

    with pytest.raises(ValueError, match="must not already exist"):
        verifier.verify_distribution(fixture_repo, output)


def test_verifier_rejects_output_outside_workspace_runs(
    fixture_repo: Path, tmp_path: Path
) -> None:
    verifier = _load_verifier()

    with pytest.raises(ValueError, match="must be below"):
        verifier.verify_distribution(fixture_repo, tmp_path / "outside")


@pytest.mark.parametrize("dirty_kind", ["tracked", "untracked"])
def test_verifier_rejects_dirty_source(
    fixture_repo: Path, dirty_kind: str
) -> None:
    verifier = _load_verifier()
    if dirty_kind == "tracked":
        target = fixture_repo / ".codex-plugin" / "plugin.json"
        target.write_text(target.read_text(encoding="utf-8") + " ", encoding="utf-8")
    else:
        (fixture_repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    output = fixture_repo / "_runs" / "distribution" / dirty_kind
    with pytest.raises(ValueError, match="worktree must be clean"):
        verifier.verify_distribution(fixture_repo, output)


def test_safe_extract_rejects_archive_links(tmp_path: Path) -> None:
    verifier = _load_verifier()
    archive = tmp_path / "linked.tar"
    with tarfile.open(archive, "w") as bundle:
        root = tarfile.TarInfo("triad-codex-dispatch-0.2.533")
        root.type = tarfile.DIRTYPE
        bundle.addfile(root)
        link = tarfile.TarInfo("triad-codex-dispatch-0.2.533/escape")
        link.type = tarfile.SYMTYPE
        link.linkname = "/private/tmp"
        bundle.addfile(link, io.BytesIO())

    with pytest.raises(ValueError, match="link or special member"):
        verifier.safe_extract(archive, tmp_path / "unpacked")


def test_verifier_archives_head_compares_hashes_and_runs_package_tests(
    fixture_repo: Path,
) -> None:
    verifier = _load_verifier()
    output = fixture_repo / "_runs" / "distribution" / "success"

    report = verifier.verify_distribution(fixture_repo, output)

    manifest = ".codex-plugin/plugin.json"
    skill = "skills/triad-cross-family-review/SKILL.md"
    expected_manifest_hash = hashlib.sha256(
        (fixture_repo / manifest).read_bytes()
    ).hexdigest()
    assert report["version"] == "0.2.533"
    assert report["tests"]["returncode"] == 0
    assert report["tests"]["argv"][:3] == [sys.executable, "-m", "pytest"]
    assert report["hashes"][manifest] == {
        "source": expected_manifest_hash,
        "archive": expected_manifest_hash,
        "match": True,
    }
    assert report["hashes"][skill]["match"] is True
    assert Path(report["archive"]).is_file()
    assert Path(report["extracted_root"]).is_dir()
    assert json.loads(
        (output / "verification.json").read_text(encoding="utf-8")
    ) == report


def test_verifier_ignores_external_pytest_configuration(
    fixture_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    verifier = _load_verifier()
    (fixture_repo.parent / "pytest.ini").write_text(
        "[pytest]\naddopts = --external-option-must-not-load\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PYTEST_ADDOPTS", "--external-env-option-must-not-load")
    output = fixture_repo / "_runs" / "distribution" / "isolated-pytest"

    report = verifier.verify_distribution(fixture_repo, output)

    assert report["tests"]["passed"] == 1
    assert report["tests"]["environment"] == {
        "PYTEST_ADDOPTS": "unset",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
    }
    assert report["tests"]["argv"][-8:] == [
        "-c",
        "/dev/null",
        "--rootdir",
        report["extracted_root"],
        "--confcutdir",
        report["extracted_root"],
        "-p",
        "no:cacheprovider",
    ]


def test_verifier_cli_runs_the_exact_archive_flow(fixture_repo: Path) -> None:
    output = fixture_repo / "_runs" / "distribution" / "cli"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--source-root",
            str(fixture_repo),
            "--output-dir",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["tests"]["returncode"] == 0
    assert Path(report["archive"]).is_file()
