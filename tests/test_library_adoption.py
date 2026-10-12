"""The bundled library is verified before use or managed refresh."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def loader():
    path = ROOT / "bin/library_adoption.py"
    assert path.is_file(), "library integrity verifier is missing"
    spec = importlib.util.spec_from_file_location("adoption_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def tree(tmp_path):
    for name in ("bin/triad_dispatch_lib", "contracts", "vendor"):
        source = ROOT / name
        if source.exists():
            shutil.copytree(source, tmp_path / name, ignore=shutil.ignore_patterns("__pycache__"))
    return tmp_path


def test_verified_identity_and_resources():
    metadata = loader().verify_library()
    assert metadata["version"] == "0.1.0.dev3"
    assert metadata["source_commit"] == "81748d721e56dfc3463888f02328902e18398600"
    assert set(metadata["bundle_ids"]) == {"verdict", "roster", "prompt"}
    for resource in ("data/leg-verdict.schema.json", "data/roster-bundle/contracts/review-legs.schema.json", "data/prompt-bundle/prompts/common-clauses.md"):
        assert "bin/triad_dispatch_lib/" + resource in metadata["sha256"]


@pytest.mark.parametrize("damage", ["changed", "missing", "extra", "symlink", "directory_symlink"])
def test_verifier_refuses_damage(tree, damage):
    module = loader()
    target = tree / "bin/triad_dispatch_lib/__init__.py"
    if damage == "changed":
        target.write_text("changed")
    elif damage == "missing":
        target.unlink()
    elif damage == "extra":
        (target.parent / "surprise.py").write_text("user work")
    elif damage == "symlink":
        target.unlink()
        target.symlink_to(ROOT / "bin/triad_dispatch_lib/__init__.py")
    else:
        shutil.rmtree(target.parent / "data")
        (target.parent / "data").symlink_to(ROOT / "bin/triad_dispatch_lib/data", target_is_directory=True)
    with pytest.raises(ValueError):
        module.verify_library(tree)


def test_check_is_nonwriting_and_normal_bin_import():
    before = (ROOT / "contracts/library-adoption.json").read_bytes() if (ROOT / "contracts/library-adoption.json").exists() else b""
    result = subprocess.run([sys.executable, str(ROOT / "scripts/vendor_library.py"), "--check"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert (ROOT / "contracts/library-adoption.json").read_bytes() == before
    result = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import triad_dispatch_lib; print(triad_dispatch_lib.__file__)", str(ROOT / "bin")], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert str(ROOT / "bin/triad_dispatch_lib/__init__.py") in result.stdout


def test_refresh_preserves_conflicts_and_rejects_bad_wheel(tree, tmp_path):
    path = ROOT / "scripts/vendor_library.py"
    assert path.exists(), "wheel refresh tool is missing"
    spec = importlib.util.spec_from_file_location("vendor_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    wheel = tmp_path / "bad.whl"
    import zipfile
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("wrong-1.dist-info/METADATA", "Name: wrong\nVersion: 1\n")
    original = (tree / "contracts/library-adoption.json").read_bytes()
    with pytest.raises(ValueError):
        module.refresh(wheel, "81748d721e56dfc3463888f02328902e18398600", tree)
    assert (tree / "contracts/library-adoption.json").read_bytes() == original
    target = tree / "bin/triad_dispatch_lib/__init__.py"
    target.write_text("intentional user change")
    with pytest.raises(ValueError):
        module.refresh(wheel, "81748d721e56dfc3463888f02328902e18398600", tree)
    assert target.read_text() == "intentional user change"


def make_wheel(destination, root=ROOT, mutation=None):
    """Construct a standard RECORD-bearing wheel without a build dependency."""
    import base64
    import csv
    import hashlib
    import io
    import zipfile
    prefix = "triad_dispatch_lib-0.1.0.dev3.dist-info/"
    files = {path.relative_to(root / "bin").as_posix(): path.read_bytes()
             for path in (root / "bin/triad_dispatch_lib").rglob("*")
             if path.is_file() and "__pycache__" not in path.parts}
    files[prefix + "licenses/LICENSE"] = (root / "vendor/triad-dispatch-lib.LICENSE").read_bytes()
    files[prefix + "METADATA"] = b"Name: triad-dispatch-lib\nVersion: 0.1.0.dev3\nRequires-Python: >=3.12\n"
    if mutation:
        mutation(files)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    for name, body in files.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(body).digest()).decode().rstrip("=")
        writer.writerow([name, "sha256=" + digest, str(len(body))])
    writer.writerow([prefix + "RECORD", "", ""])
    files[prefix + "RECORD"] = buffer.getvalue().encode()
    with zipfile.ZipFile(destination, "w") as archive:
        for name, body in files.items():
            archive.writestr(name, body)
    return destination


def vendor_module():
    spec = importlib.util.spec_from_file_location("vendor_test", ROOT / "scripts/vendor_library.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_valid_refresh_copies_every_byte(tree, tmp_path):
    wheel = make_wheel(tmp_path / "valid.whl")
    metadata = vendor_module().refresh(wheel, loader().COMMIT, tree)
    assert metadata == loader().verify_library(tree)
    for name in metadata["sha256"]:
        assert (tree / name).read_bytes() == (ROOT / name).read_bytes()


@pytest.mark.parametrize("conflict", ["changed", "missing", "extra", "symlink", "license", "extra_directory"])
def test_valid_wheel_refresh_preserves_all_conflicts(tree, tmp_path, conflict):
    wheel = make_wheel(tmp_path / "valid.whl")
    target = tree / "bin/triad_dispatch_lib/__init__.py"
    if conflict == "changed":
        target.write_text("user change")
    elif conflict == "missing":
        target.unlink()
    elif conflict == "extra":
        (target.parent / "extra.py").write_text("user file")
    elif conflict == "symlink":
        target.unlink()
        target.symlink_to(ROOT / "bin/triad_dispatch_lib/__init__.py")
    elif conflict == "license":
        (tree / "vendor/triad-dispatch-lib.LICENSE").write_text("user license change")
    else:
        (target.parent / "user-directory").mkdir()
    before = {path.relative_to(tree).as_posix(): ("link", str(path.readlink())) if path.is_symlink() else ("file", path.read_bytes())
              for path in tree.rglob("*") if path.is_file() or path.is_symlink()}
    with pytest.raises(ValueError):
        vendor_module().refresh(wheel, loader().COMMIT, tree)
    after = {path.relative_to(tree).as_posix(): ("link", str(path.readlink())) if path.is_symlink() else ("file", path.read_bytes())
             for path in tree.rglob("*") if path.is_file() or path.is_symlink()}
    assert after == before


@pytest.mark.parametrize("damage", ["metadata", "resource", "missing_resource", "unsafe_path", "record"])
def test_invalid_input_is_fully_validated_before_write(tree, tmp_path, damage):
    def mutate(files):
        if damage == "metadata":
            files["triad_dispatch_lib-0.1.0.dev3.dist-info/METADATA"] = b"Name: wrong\nVersion: 0.1.0.dev3\nRequires-Python: >=3.12\n"
        elif damage == "resource":
            files["triad_dispatch_lib/data/leg-verdict.schema.json"] = b"{}"
        elif damage == "missing_resource":
            del files["triad_dispatch_lib/data/prompt-bundle/prompts/common-clauses.md"]
        elif damage == "unsafe_path":
            files["triad_dispatch_lib/../../outside"] = b"unsafe"
    wheel = make_wheel(tmp_path / "bad-input.whl", mutation=mutate)
    if damage == "record":
        import zipfile
        with zipfile.ZipFile(wheel, "a") as archive:
            archive.writestr("triad_dispatch_lib/unrecorded.py", b"unexpected")
    original = (tree / "contracts/library-adoption.json").read_bytes()
    with pytest.raises(ValueError):
        vendor_module().refresh(wheel, loader().COMMIT, tree)
    assert (tree / "contracts/library-adoption.json").read_bytes() == original
    loader().verify_library(tree)


def test_check_creates_no_files(tree):
    (tree / "scripts").mkdir()
    shutil.copy2(ROOT / "scripts/vendor_library.py", tree / "scripts/vendor_library.py")
    shutil.copy2(ROOT / "bin/library_adoption.py", tree / "bin/library_adoption.py")
    before = {path.relative_to(tree).as_posix(): path.read_bytes() for path in tree.rglob("*") if path.is_file()}
    result = subprocess.run([sys.executable, str(tree / "scripts/vendor_library.py"), "--check"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    after = {path.relative_to(tree).as_posix(): path.read_bytes() for path in tree.rglob("*") if path.is_file()}
    assert before == after


def test_refresh_refuses_incomplete_python_package(tree, tmp_path):
    wheel = make_wheel(tmp_path / "missing-module.whl", mutation=lambda files: files.pop("triad_dispatch_lib/dispatch.py"))
    with pytest.raises(ValueError):
        vendor_module().refresh(wheel, loader().COMMIT, tree)


def test_verifier_refuses_unknown_adoption_schema(tree):
    path = tree / "contracts/library-adoption.json"
    metadata = json.loads(path.read_text())
    metadata["schema_version"] = 99
    path.write_text(json.dumps(metadata))
    with pytest.raises(ValueError):
        loader().verify_library(tree)


@pytest.mark.parametrize("member", ["triad_dispatch_lib/dispatch.py", "triad_dispatch_lib-0.1.0.dev3.dist-info/licenses/LICENSE"])
def test_self_consistent_altered_wheel_cannot_claim_approved_commit(tree, tmp_path, member):
    def alter(files):
        files[member] += b"\n# changed incoming content\n"
    wheel = make_wheel(tmp_path / "altered.whl", mutation=alter)
    before = {path.relative_to(tree).as_posix(): path.read_bytes() for path in tree.rglob("*") if path.is_file()}
    with pytest.raises(ValueError, match="approved content"):
        vendor_module().refresh(wheel, loader().COMMIT, tree)
    after = {path.relative_to(tree).as_posix(): path.read_bytes() for path in tree.rglob("*") if path.is_file()}
    assert before == after


def test_generated_record_cannot_reauthorize_changed_implementation(tree):
    import hashlib
    target = tree / "bin/triad_dispatch_lib/dispatch.py"
    target.write_bytes(target.read_bytes() + b"\n# unauthorized\n")
    record = tree / "contracts/library-adoption.json"
    metadata = json.loads(record.read_text())
    metadata["sha256"]["bin/triad_dispatch_lib/dispatch.py"] = hashlib.sha256(target.read_bytes()).hexdigest()
    record.write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match="approved content"):
        loader().verify_library(tree)
