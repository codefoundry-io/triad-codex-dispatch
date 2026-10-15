"""Exercise the runtime probe in a fresh isolated interpreter using a copied host."""
import json
import os
from pathlib import Path
import shutil
import site
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_library_runtime.py"


def copied_host(tmp_path):
    root = tmp_path / "host"
    for name in ("bin", "contracts", "prompts", "vendor"):
        shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns("__pycache__"))
    return root.resolve()


def probe(root, cwd):
    # Unit probe supplies the test runner's dependency site explicitly. The
    # public driver separately creates a fresh venv and installs requirements.
    bootstrap = ("import runpy,sys; sys.path.append(" + repr(site.getusersitepackages())
                 + "); sys.argv=" + repr([str(SCRIPT), "--probe", "--root", str(root)])
                 + "; runpy.run_path(" + repr(str(SCRIPT)) + ", run_name='__main__')")
    return subprocess.run([sys.executable, "-I", "-c", bootstrap],
                          cwd=cwd, text=True, capture_output=True, timeout=90)


def test_probe_uses_supplied_host_and_exercises_four_routes(tmp_path):
    root = copied_host(tmp_path)
    result = probe(root, tmp_path)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["library_origin"] == str(root / "bin/triad_dispatch_lib/__init__.py")
    assert report["routes"] == ["claude", "codex", "agy", "gemini"]
    assert report["binding_refusals"] == 24
    assert report["overflow_refusals"] == 3
    assert report["roster_names"] == ["claude", "codex", "google", "codex-second"]
    assert all(Path(path).is_relative_to(root / "bin") for path in report["host_origins"].values())
    assert report["os"] and report["architecture"] and report["python"]
    assert not list(root.rglob("__pycache__")), "probe must not write into supplied host"


def test_probe_refuses_damaged_supplied_package_instead_of_using_checkout(tmp_path):
    root = copied_host(tmp_path)
    (root / "bin/triad_dispatch_lib/verdict.py").write_text("damaged")
    result = probe(root, tmp_path)
    assert result.returncode != 0
    assert "hash mismatch" in result.stderr


def test_driver_cleans_temporary_environment_after_pip_failure(tmp_path):
    root = tmp_path / "host"
    root.mkdir()
    (root / "requirements.txt").write_text("invalid requirement !!!\n")
    result = subprocess.run([sys.executable, "-I", str(SCRIPT), "--root", str(root.resolve())],
                            cwd=tmp_path, env=dict(os.environ, TMPDIR=str(tmp_path.resolve())),
                            text=True, capture_output=True, timeout=120)
    assert result.returncode == 1
    assert "Invalid requirement" in result.stderr
    assert not list(tmp_path.glob("triad-library-runtime-*"))


def test_public_driver_accepts_encoded_paths_under_tricky_tmpdir(tmp_path):
    root = copied_host(tmp_path)
    shutil.copy2(ROOT / "requirements.txt", root / "requirements.txt")
    tricky_base = (tmp_path / r'TMP 한글 "quoted" \n').resolve()
    tricky_base.mkdir()
    result = subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "--root", str(root)],
        cwd=tmp_path,
        env=dict(os.environ, TMPDIR=str(tricky_base)),
        text=True,
        capture_output=True,
        timeout=900,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["root"] == str(root)
    assert report["library_origin"] == str(root / "bin/triad_dispatch_lib/__init__.py")
    assert set(report["host_origins"]) == {
        "library_adoption", "review_prompts_v2", "review_roster", "validate_v2", "verdict_v2"
    }
    assert all(Path(path).is_relative_to(root / "bin") for path in report["host_origins"].values())
    assert report["routes"] == ["claude", "codex", "agy", "gemini"]
    assert report["binding_refusals"] == 24
    assert report["overflow_refusals"] == 3
    assert report["duplicate_refusals"] == 1
    assert report["roster_names"] == ["claude", "codex", "google", "codex-second"]
    assert report["skips"] == []
    temporary_root = Path(report["temporary_root"])
    assert temporary_root.parent == tricky_base
    assert report["temporary_root_removed"] is True
    assert not temporary_root.exists()
    assert not list(root.rglob("__pycache__")), "public driver must not write into supplied host"
