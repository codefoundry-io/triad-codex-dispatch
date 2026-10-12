"""Read-only integrity checks for the generated, bundled shared library."""
import hashlib
import json
from pathlib import Path
import re
import stat

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "81748d721e56dfc3463888f02328902e18398600"
VERSION = "0.1.0.dev3"
PACKAGE = "bin/triad_dispatch_lib"
LICENSE = "vendor/triad-dispatch-lib.LICENSE"
RECORD = "contracts/library-adoption.json"
MANIFESTS = {"verdict": "data/source-manifest.json", "roster": "data/roster-bundle/source-manifest.json", "prompt": "data/prompt-bundle/source-manifest.json"}
MODULES = {"__init__", "agreement", "bundle_manifest", "contracts", "dispatch", "errors", "json_input", "output", "prompts", "roster", "verdict"}


def regular_bytes(root, name):
    """Refuse links and special files at every component before reading."""
    path = root
    for part in Path(name).parts:
        path /= part
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise ValueError(f"unsafe managed path: {name}")
    if not stat.S_ISREG(mode):
        raise ValueError(f"not a regular file: {name}")
    return path.read_bytes()


def bundle_ids(files):
    expected = {f"{PACKAGE}/{module}.py" for module in MODULES} | {LICENSE}
    result = {}
    for kind, name in MANIFESTS.items():
        expected.add(f"{PACKAGE}/{name}")
        manifest = json.loads(files[f"{PACKAGE}/{name}"])
        digests = manifest["sha256"]
        identity = hashlib.sha256(b"triad-dispatch-lib:bundle:v1\n" + json.dumps(digests, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
        if manifest["contract_id"] != identity:
            raise ValueError("bundle identity mismatch")
        for relative, digest in digests.items():
            if Path(relative).is_absolute() or ".." in Path(relative).parts:
                raise ValueError("unsafe bundle path")
            data = files[f"{PACKAGE}/{Path(name).parent}/{relative}"]
            expected.add(f"{PACKAGE}/{Path(name).parent}/{relative}")
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError("bundle resource mismatch")
        result[kind] = identity
    if set(files) != expected:
        raise ValueError("incomplete or unexpected pinned package inventory")
    return result


def verify_library(root=ROOT):
    """Verify the complete generated inventory and return adoption metadata.

    CPython's regular .pyc files in __pycache__ are transient, not generated
    distribution inputs. Links and other unexpected cache contents still fail.
    """
    root = Path(root)
    try:
        metadata = json.loads(regular_bytes(root, RECORD))
        if (type(metadata["schema_version"]) is not int or metadata["schema_version"] != 1
                or metadata["name"] != "triad-dispatch-lib" or metadata["version"] != VERSION
                or metadata["source_commit"] != COMMIT
                or not re.fullmatch(r"[0-9a-f]{64}", metadata["wheel_sha256"])):
            raise ValueError("unexpected library adoption identity")
        expected = metadata["sha256"]
        if not isinstance(expected, dict) or LICENSE not in expected:
            raise ValueError("invalid managed inventory")
        for name, digest in expected.items():
            if (not (name.startswith(PACKAGE + "/") or name == LICENSE)
                    or ".." in Path(name).parts or not re.fullmatch(r"[0-9a-f]{64}", digest)):
                raise ValueError("unsafe managed inventory")
        regular_bytes(root, f"{PACKAGE}/__init__.py")
        actual = {LICENSE}
        for path in (root / PACKAGE).rglob("*"):
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                raise ValueError("unsafe generated file")
            relative = path.relative_to(root).as_posix()
            if stat.S_ISREG(mode):
                if path.parent.name == "__pycache__" and path.suffix == ".pyc":
                    continue
                actual.add(relative)
            elif path.name != "__pycache__" and not any(name.startswith(relative + "/") for name in expected):
                raise ValueError("unexpected generated directory")
        if actual != set(expected):
            raise ValueError("generated inventory mismatch")
        files = {name: regular_bytes(root, name) for name in expected}
        if any(hashlib.sha256(data).hexdigest() != expected[name] for name, data in files.items()):
            raise ValueError("generated hash mismatch")
        if bundle_ids(files) != metadata["bundle_ids"]:
            raise ValueError("adoption bundle identity mismatch")
        return metadata
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid library adoption: {exc}") from exc
