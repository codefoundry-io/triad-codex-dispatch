#!/usr/bin/env python3
"""Create or rewrite the same pinned package from a verified wheel; no install.

An existing package must already match the approved content pin. --write is not
a pin migration; an equal-content rebuilt wheel may update wheel provenance.
"""
import argparse
import base64
import csv
from email.parser import BytesParser
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import stat
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
sys.dont_write_bytecode = True

from library_adoption import COMMIT, LICENSE, PACKAGE, RECORD, ROOT, VERSION, bundle_ids, verify_approved_content, verify_library


def wheel_files(wheel, source_commit):
    if source_commit != COMMIT:
        raise ValueError("source commit differs from approved library commit")
    artifact = Path(wheel).read_bytes()
    prefix = f"triad_dispatch_lib-{VERSION}.dist-info/"
    with zipfile.ZipFile(io.BytesIO(artifact)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("duplicate wheel member")
        for info in archive.infolist():
            path = PurePosixPath(info.filename)
            mode = info.external_attr >> 16
            if (path.is_absolute() or ".." in path.parts or "\\" in info.filename
                    or info.is_dir() or (stat.S_IFMT(mode) not in (0, stat.S_IFREG))
                    or not (info.filename.startswith("triad_dispatch_lib/") or info.filename.startswith(prefix))):
                raise ValueError("unsafe or unexpected wheel member")
        data = {name: archive.read(name) for name in names}
    metadata = BytesParser().parsebytes(data.get(prefix + "METADATA", b""))
    if metadata.get("Name") != "triad-dispatch-lib" or metadata.get("Version") != VERSION or metadata.get("Requires-Python") != ">=3.12":
        raise ValueError("wrong wheel metadata")
    rows = list(csv.reader(io.StringIO(data[prefix + "RECORD"].decode())))
    if len(rows) != len(data) or {row[0] for row in rows} != set(data):
        raise ValueError("wheel RECORD inventory mismatch")
    for name, digest, size in rows:
        if name == prefix + "RECORD":
            if digest or size:
                raise ValueError("invalid self RECORD")
            continue
        expected = "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(data[name]).digest()).decode().rstrip("=")
        if digest != expected or size != str(len(data[name])):
            raise ValueError("wheel RECORD hash mismatch")
    files = {"bin/" + name: body for name, body in data.items() if name.startswith("triad_dispatch_lib/")}
    if f"{PACKAGE}/__init__.py" not in files:
        raise ValueError("missing package")
    files[LICENSE] = data[prefix + "licenses/LICENSE"]
    record = {"schema_version": 1, "name": "triad-dispatch-lib", "version": VERSION,
              "source_commit": source_commit, "wheel_sha256": hashlib.sha256(artifact).hexdigest(),
              "bundle_ids": bundle_ids(files),
              "sha256": {name: hashlib.sha256(body).hexdigest() for name, body in sorted(files.items())}}
    verify_approved_content(record["sha256"])
    return files, record


def refresh(wheel, source_commit, root=ROOT):
    """Validate all inputs and old managed files before making any write."""
    root = Path(root)
    try:
        old = verify_library(root) if (root / RECORD).exists() or (root / RECORD).is_symlink() else None
        files, record = wheel_files(wheel, source_commit)
        destinations = set(files) | {RECORD}
        for name in destinations:
            path = root
            for component in Path(name).parts[:-1]:
                path /= component
                if path.is_symlink() or (path.exists() and not path.is_dir()):
                    raise ValueError("unsafe destination parent")
            target = root / name
            if target.is_symlink() or (target.exists() and (old is None or name not in set(old["sha256"]) | {RECORD})):
                raise ValueError("unmanaged destination conflict")
        if old is None and (root / PACKAGE).exists():
            raise ValueError("unmanaged package tree")
        for name, body in files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        if old:
            for name in set(old["sha256"]) - set(files):
                (root / name).unlink()
        target = root / RECORD
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        return verify_library(root)
    except (OSError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        raise ValueError(f"invalid wheel refresh: {exc}") from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--source-commit")
    args = parser.parse_args()
    if args.write and (not args.wheel or not args.source_commit):
        parser.error("--write requires --wheel and --source-commit")
    try:
        result = verify_library() if args.check else refresh(args.wheel, args.source_commit)
    except ValueError as exc:
        parser.exit(1, f"library adoption refused: {exc}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
