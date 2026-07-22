from __future__ import annotations

import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "triad-cross-family-review" / "lib" / "review_snapshot.py"


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    )


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def writable(root: Path) -> None:
    for current, directories, files in os.walk(root, topdown=False):
        for name in files:
            path = Path(current, name)
            if not path.is_symlink():
                os.chmod(path, 0o600)
        for name in directories:
            path = Path(current, name)
            if not path.is_symlink():
                os.chmod(path, 0o700)
    if root.exists() and not root.is_symlink():
        os.chmod(root, 0o700)


class ReviewSnapshotTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="review-snapshot-test-"))
        self.repo, self.output = self.temp / "repo", self.temp / "snapshots"
        self.repo.mkdir()
        self.output.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "core.excludesFile", str(self.temp / "no-global-ignore"))

    def tearDown(self) -> None:
        writable(self.temp)
        shutil.rmtree(self.temp, ignore_errors=True)

    def commit(self, *paths: str) -> None:
        git(self.repo, "add", "--", *paths)
        git(
            self.repo,
            "-c",
            "user.name=Snapshot Test",
            "-c",
            "user.email=snapshot@example.invalid",
            "commit",
            "-q",
            "-m",
            "fixture",
        )

    def create(self, repo: Path | None = None, output: Path | None = None):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "create",
                "--repo",
                str((repo or self.repo).resolve()),
                "--output-parent",
                str((output or self.output).resolve()),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return result, None
        summary = json.loads(result.stdout)
        receipt = json.loads(Path(summary["receipt_path"]).read_text(encoding="ascii"))
        return result, receipt

    def verify(self, root: Path):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "verify", "--snapshot-root", str(root.resolve())],
            check=False,
            capture_output=True,
            text=True,
        )

    def load(self, name: str):
        spec = importlib.util.spec_from_file_location(name, SCRIPT)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def assert_source_ancestor_swap_refused(self, tracked: bool) -> None:
        source_dir = self.repo / "nested"
        source_dir.mkdir()
        source_path = source_dir / "payload.txt"
        source_path.write_bytes(b"repository bytes\n")
        if tracked:
            self.commit("nested/payload.txt")
        else:
            (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
            self.commit("base.txt")

        external_dir = self.temp / "external"
        external_dir.mkdir()
        external_path = external_dir / "payload.txt"
        external_bytes = b"EXTERNAL BOUNDARY BYTES\n"
        external_path.write_bytes(external_bytes)
        external_identity = external_path.stat().st_dev, external_path.stat().st_ino

        for swap_after_scan in (1, 2):
            with self.subTest(
                source="tracked" if tracked else "untracked_nonignored",
                phase="copy" if swap_after_scan == 1 else "rehash",
            ):
                module = self.load(
                    f"review_snapshot_ancestor_{int(tracked)}_{swap_after_scan}"
                )
                real_scan = module._scan
                real_read = os.read
                held_dir = self.temp / f"held-{int(tracked)}-{swap_after_scan}"
                scan_calls = 0
                captured_external = bytearray()

                def scan_then_swap(repo: Path):
                    nonlocal scan_calls
                    scan_calls += 1
                    result = real_scan(repo)
                    if scan_calls == 1:
                        paths = result.tracked if tracked else result.untracked
                        self.assertIn("nested/payload.txt", paths)
                    if scan_calls == swap_after_scan:
                        source_dir.rename(held_dir)
                        source_dir.symlink_to(external_dir, target_is_directory=True)
                    return result

                def observe_external_read(descriptor: int, size: int) -> bytes:
                    identity = os.fstat(descriptor).st_dev, os.fstat(descriptor).st_ino
                    data = real_read(descriptor, size)
                    if identity == external_identity:
                        captured_external.extend(data)
                    return data

                module._scan = scan_then_swap
                module.os.read = observe_external_read
                try:
                    with self.assertRaises(module.SnapshotError) as raised:
                        module.create_snapshot(self.repo.resolve(), self.output.resolve())
                finally:
                    module.os.read = real_read
                    if source_dir.is_symlink():
                        source_dir.unlink()
                    if held_dir.exists():
                        held_dir.rename(source_dir)

                self.assertNotIn(external_bytes, bytes(captured_external))
                self.assertEqual(scan_calls, swap_after_scan)
                self.assertRegex(str(raised.exception).lower(), r"symlink|directory")
                self.assertEqual(list(self.output.iterdir()), [])

    def test_create_receipt_closure_seal_escape_and_verify(self) -> None:
        (self.repo / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
        (self.repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
        (self.repo / "gone.txt").write_text("gone\n", encoding="utf-8")
        (self.repo / "run.py").write_text("print('ok')\n", encoding="utf-8")
        os.chmod(self.repo / "run.py", 0o755)
        self.commit(".gitignore", "tracked.txt", "gone.txt", "run.py")
        (self.repo / "gone.txt").unlink()
        (self.repo / "notes.txt").write_text("notes\n", encoding="utf-8")
        (self.repo / "ignored.txt").write_text("ignored\n", encoding="utf-8")
        (self.repo / "scratch.tmp").write_text("scratch\n", encoding="utf-8")
        cache = self.repo / "nested" / "__pycache__"
        cache.mkdir(parents=True)
        (cache / "value.bin").write_bytes(b"cache")
        unusual = "line\nbreak.txt"
        (self.repo / unusual).write_text("unusual\n", encoding="utf-8")

        result, receipt = self.create()

        self.assertEqual(result.returncode, 0, result.stderr)
        root = Path(receipt["snapshot_root"])
        self.assertEqual(
            json.loads(result.stdout),
            {
                "schema": "triad.review-snapshot-create.v1",
                "snapshot_root": str(root),
                "receipt_path": str(root / "SNAPSHOT_RECEIPT.json"),
                "manifest_sha256": receipt["manifest_sha256"],
                "file_count": receipt["file_count"],
                "sealed_read_only": True,
            },
        )
        self.assertLess(len(result.stdout), 2048)
        enum = receipt["enumeration"]
        self.assertEqual(enum["deleted_tracked"]["paths"], ["gone.txt"])
        self.assertEqual(enum["ignored_untracked"]["paths"], ["ignored.txt"])
        self.assertIn("notes.txt", enum["untracked_nonignored"]["paths"])
        excluded = {(item["path"], item["reason"]) for item in enum["excluded"]}
        self.assertIn(("scratch.tmp", "suffix:.tmp"), excluded)
        self.assertIn(("nested/__pycache__/value.bin", "directory:__pycache__"), excluded)
        candidate = root / "candidate"
        self.assertTrue((candidate / "tracked.txt").is_file())
        self.assertTrue((candidate / "notes.txt").is_file())
        self.assertFalse((candidate / "gone.txt").exists())
        self.assertEqual(stat.S_IMODE((candidate / "run.py").stat().st_mode), 0o555)
        manifest = (root / "SNAPSHOT_SHA256SUMS").read_text(encoding="ascii")
        self.assertIn(json.dumps(f"candidate/{unusual}", ensure_ascii=True), manifest)
        verified = self.verify(root)
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertTrue(json.loads(verified.stdout)["verified"])

    def test_partial_source_execute_mode_normalizes_to_read_only_executable(self) -> None:
        target = self.repo / "run-owner-only.sh"
        target.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        os.chmod(target, 0o744)
        self.commit("run-owner-only.sh")

        result, receipt = self.create()

        self.assertEqual(result.returncode, 0, result.stderr)
        item = next(item for item in receipt["files"] if item["path"] == target.name)
        self.assertEqual(item["sealed_mode"], 0o555)
        candidate = Path(receipt["snapshot_root"]) / "candidate" / target.name
        self.assertEqual(stat.S_IMODE(candidate.stat().st_mode), 0o555)
        verified = self.verify(Path(receipt["snapshot_root"]))
        self.assertEqual(verified.returncode, 0, verified.stderr)

    def test_verify_accepts_byte_identical_relocation_with_same_snapshot_id(self) -> None:
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        self.commit("base.txt")
        result, receipt = self.create()
        self.assertEqual(result.returncode, 0, result.stderr)
        original = Path(receipt["snapshot_root"])
        relocated_parent = self.temp / "external-packet"
        relocated_parent.mkdir()
        relocated = relocated_parent / original.name
        shutil.copytree(original, relocated, copy_function=shutil.copy2)

        verified = self.verify(relocated)

        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertTrue(json.loads(verified.stdout)["verified"])

        renamed = relocated_parent / "different-snapshot-id"
        shutil.copytree(original, renamed, copy_function=shutil.copy2)
        rejected = self.verify(renamed)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("identity mismatch", rejected.stderr)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_and_gitlink_are_refused_without_residue(self) -> None:
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        self.commit("base.txt")
        (self.repo / "link.txt").symlink_to("base.txt")
        for tracked in (False, True):
            with self.subTest(kind="symlink", tracked=tracked):
                if tracked:
                    git(self.repo, "add", "link.txt")
                result, _ = self.create()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("symlink", result.stderr.lower())
                self.assertEqual(list(self.output.iterdir()), [])
                if tracked:
                    git(self.repo, "reset", "-q", "HEAD", "--", "link.txt")
        (self.repo / "link.txt").unlink()
        nested = self.repo / "vendor"
        nested.mkdir()
        git(nested, "init", "-q")
        (nested / "file.txt").write_text("nested\n", encoding="utf-8")
        git(nested, "add", "file.txt")
        git(
            nested,
            "-c",
            "user.name=Snapshot Test",
            "-c",
            "user.email=snapshot@example.invalid",
            "commit",
            "-q",
            "-m",
            "nested",
        )
        git(self.repo, "add", "vendor")
        result, _ = self.create()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("gitlink", result.stderr.lower())
        self.assertEqual(list(self.output.iterdir()), [])

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_tracked_source_ancestor_swap_is_refused_without_capture(self) -> None:
        self.assert_source_ancestor_swap_refused(tracked=True)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_untracked_source_ancestor_swap_is_refused_without_capture(self) -> None:
        self.assert_source_ancestor_swap_refused(tracked=False)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unavailable")
    def test_real_untracked_fifo_is_refused_without_residue(self) -> None:
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        self.commit("base.txt")
        os.mkfifo(self.repo / "events.pipe")

        result, _ = self.create()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("regular", result.stderr.lower())
        self.assertEqual(list(self.output.iterdir()), [])

    def test_source_universe_closes_child_fd_when_attestation_fails(self) -> None:
        nested = self.repo / "nested"
        nested.mkdir()
        (nested / "base.txt").write_text("base\n", encoding="utf-8")
        self.commit("nested/base.txt")
        module = self.load("review_snapshot_source_universe_fd")
        repo_fd = module._open_directory(self.repo.resolve(), "repo")
        real_fstat = module.os.fstat
        real_close = module.os.close
        attested: list[int] = []
        closed: list[int] = []

        def fail_attestation(descriptor: int):
            attested.append(descriptor)
            raise OSError("forced child attestation failure")

        def observe_close(descriptor: int):
            closed.append(descriptor)
            return real_close(descriptor)

        module.os.fstat = fail_attestation
        module.os.close = observe_close
        try:
            with self.assertRaisesRegex(
                module.SnapshotError, "cannot attest source tree directory"
            ):
                module._check_source_universe(repo_fd, self.repo.resolve(), None)
        finally:
            module.os.fstat = real_fstat
            module.os.close = real_close
            for descriptor in attested:
                if descriptor not in closed:
                    real_close(descriptor)
            real_close(repo_fd)

        self.assertEqual(len(attested), 1)
        self.assertEqual(closed, attested)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unavailable")
    def test_returned_nonregular_input_is_refused(self) -> None:
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        self.commit("base.txt")
        os.mkfifo(self.repo / "events.pipe")
        module = self.load("review_snapshot_fifo")
        scan = module._scan(self.repo.resolve())
        forged = scan._replace(untracked=tuple(sorted((*scan.untracked, "events.pipe"))))
        module._scan = lambda _repo: forged

        with self.assertRaisesRegex(module.SnapshotError, "regular file"):
            module.create_snapshot(self.repo.resolve(), self.output.resolve())
        self.assertEqual(list(self.output.iterdir()), [])

    def test_repeat_enumeration_failure_preserves_foreign_output(self) -> None:
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        self.commit("base.txt")
        keep = self.output / "keep.txt"
        keep.write_text("keep\n", encoding="utf-8")
        module = self.load("review_snapshot_repeat")
        real_scan, calls = module._scan, 0

        def changed(repo: Path):
            nonlocal calls
            calls += 1
            if calls == 2:
                (repo / "late.txt").write_text("late\n", encoding="utf-8")
            return real_scan(repo)

        module._scan = changed
        with self.assertRaisesRegex(module.SnapshotError, "enumeration changed"):
            module.create_snapshot(self.repo.resolve(), self.output.resolve())
        self.assertEqual(list(self.output.iterdir()), [keep])

    def test_source_changed_after_earlier_copy_is_refused(self) -> None:
        (self.repo / "a.txt").write_text("first\n", encoding="utf-8")
        (self.repo / "z.txt").write_text("last\n", encoding="utf-8")
        self.commit("a.txt", "z.txt")
        module = self.load("review_snapshot_mixed_time")
        real_copy = module._copy

        def mutate_after_later_copy(
            repo_fd: int, candidate: Path, path: str, source: str
        ):
            item = real_copy(repo_fd, candidate, path, source)
            if path == "z.txt":
                (self.repo / "a.txt").write_text("changed after copy\n", encoding="utf-8")
            return item

        module._copy = mutate_after_later_copy
        with self.assertRaisesRegex(module.SnapshotError, "source changed after copying"):
            module.create_snapshot(self.repo.resolve(), self.output.resolve())
        self.assertEqual(list(self.output.iterdir()), [])

    def test_verify_rejects_tamper_and_extra_file(self) -> None:
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        self.commit("base.txt")
        result, receipt = self.create()
        self.assertEqual(result.returncode, 0, result.stderr)
        root = Path(receipt["snapshot_root"])
        target = root / "candidate" / "base.txt"
        os.chmod(target, 0o644)
        target.write_text("tampered\n", encoding="utf-8")
        self.assertNotEqual(self.verify(root).returncode, 0)

        result, receipt = self.create()
        self.assertEqual(result.returncode, 0, result.stderr)
        root = Path(receipt["snapshot_root"])
        candidate = root / "candidate"
        os.chmod(candidate, 0o755)
        (candidate / "extra.txt").write_text("extra\n", encoding="utf-8")
        extra = self.verify(root)
        self.assertNotEqual(extra.returncode, 0)
        self.assertIn("file set", extra.stderr.lower())

        result, receipt = self.create()
        self.assertEqual(result.returncode, 0, result.stderr)
        root = Path(receipt["snapshot_root"])
        receipt["enumeration"]["ignored_untracked"]["paths_sha256"] = "0" * 64
        receipt_path = root / "SNAPSHOT_RECEIPT.json"
        os.chmod(receipt_path, 0o644)
        receipt_path.write_text(canonical(receipt) + "\n", encoding="ascii")
        os.chmod(receipt_path, 0o444)
        ignored_digest = self.verify(root)
        self.assertNotEqual(ignored_digest.returncode, 0)
        self.assertIn("ignored path digest", ignored_digest.stderr.lower())

    def test_verify_streams_candidate_hash_without_whole_file_read(self) -> None:
        target = self.repo / "nested" / "payload.bin"
        target.parent.mkdir()
        target.write_bytes(b"small deterministic candidate\n")
        self.commit("nested/payload.bin")
        result, receipt = self.create()
        self.assertEqual(result.returncode, 0, result.stderr)
        root = Path(receipt["snapshot_root"])
        module = self.load("review_snapshot_stream_verify")
        real_read = module._read
        real_hash_source = module._hash_source_regular
        streamed = []

        def control_file_read(path: Path, label: str):
            if label.startswith("candidate/"):
                self.fail(f"candidate used whole-file _read: {label}")
            return real_read(path, label)

        def observe_stream_hash(repo_fd: int, path: str, label: str):
            streamed.append(path)
            return real_hash_source(repo_fd, path, label)

        module._read = control_file_read
        module._hash_source_regular = observe_stream_hash

        verified = module.verify_snapshot(root)

        self.assertTrue(verified["verified"])
        self.assertEqual(streamed, ["nested/payload.bin"])


if __name__ == "__main__":
    unittest.main()
