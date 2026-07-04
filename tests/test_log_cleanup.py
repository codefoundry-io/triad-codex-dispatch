import os
import json
import sys
import time
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))

import _common  # noqa: E402


def _result(stdout: str = "x") -> _common.RunResult:
    return _common.RunResult(
        exit_code=_common.EXIT_CLI_FAIL,
        stdout=stdout,
        stderr="err",
        elapsed_s=0.1,
        classification="unknown",
        final_answer="",
        vendor_exit_code=1,
    )


def test_stale_run_log_prune_removes_repair_json_pair(tmp_path, monkeypatch):
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path / "_logs")
    runs_dir = tmp_path / "_logs" / "claude" / "runs"
    runs_dir.mkdir(parents=True)
    run_log = runs_dir / "old.json"
    repair = runs_dir / "old.json.repair.json"
    prompt_tmp = runs_dir / "old.prompt.tmp"
    fresh = runs_dir / "fresh.json"
    for path in (run_log, repair, prompt_tmp, fresh):
        path.write_text("{}\n", encoding="utf-8")
    old = time.time() - 10_000
    os.utime(run_log, (old, old))
    os.utime(repair, (old, old))
    os.utime(prompt_tmp, (old, old))

    _common.prune_stale_run_logs("claude", age_floor_s=7200)

    assert not run_log.exists()
    assert not repair.exists()
    assert not prompt_tmp.exists()
    assert fresh.exists()


def test_audit_rotation_prunes_archives_by_count(tmp_path, monkeypatch):
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path / "_logs")
    monkeypatch.setattr(_common, "AUDIT_ROTATE_BYTES", 200)
    monkeypatch.setattr(_common, "AUDIT_MAX_ARCHIVES", 2)
    monkeypatch.setattr(_common, "AUDIT_ARCHIVE_MAX_BYTES", 10_000)

    for _ in range(5):
        _common.audit("claude", ["fake"], "prompt", _result(stdout="x" * 500))

    log_dir = tmp_path / "_logs" / "claude"
    assert (log_dir / "audit.jsonl").is_file()
    assert len(list(log_dir.glob("audit.*.jsonl"))) <= 2


def test_audit_does_not_persist_prompt_bearing_argv_or_full_streams(tmp_path, monkeypatch):
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path / "_logs")
    prompt = "SECRET_PROMPT_BODY"
    result = _common.RunResult(
        exit_code=_common.EXIT_CLI_FAIL,
        stdout="SECRET_STDOUT_" + ("x" * 600),
        stderr="SECRET_STDERR_" + ("y" * 600),
        elapsed_s=0.1,
        classification="unknown",
        final_answer="",
        validated={"payload": "SECRET_VALIDATED_" + ("z" * 600)},
        vendor_exit_code=1,
    )

    _common.audit(
        "antigravity",
        [
            "agy",
            "-p",
            prompt,
            "--prompt",
            "OTHER_SECRET_PROMPT",
            "--prompt-file",
            "/workspace/private-prompt.txt",
        ],
        prompt,
        result,
    )

    path = tmp_path / "_logs" / "antigravity" / "audit.jsonl"
    rec = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    encoded = json.dumps(rec, ensure_ascii=False)

    assert prompt not in encoded
    assert "OTHER_SECRET_PROMPT" not in encoded
    assert "/workspace/private-prompt.txt" not in encoded
    assert "SECRET_VALIDATED" not in encoded
    assert rec["cmd"] == [
        "agy",
        "-p",
        "<redacted:18 chars>",
        "--prompt",
        "<redacted:19 chars>",
        "--prompt-file",
        "<redacted:prompt-file-path>",
    ]
    assert "prompt_head" not in rec
    assert "stderr" not in rec
    assert "stdout" not in rec
    assert "validated" not in rec
    assert rec["stderr_len"] == len(result.stderr)
    assert rec["stdout_len"] == len(result.stdout)
    assert rec["validated_present"] is True
    assert rec["validated_len"] == len(json.dumps(result.validated, ensure_ascii=False))
    assert rec["stderr_head"].startswith("SECRET_STDERR_")
    assert rec["stdout_head"].startswith("SECRET_STDOUT_")
    assert len(rec["stderr_head"]) == 500
    assert len(rec["stdout_head"]) == 500


def test_run_log_preserves_full_prompt_for_repair_replay(tmp_path, monkeypatch):
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path / "_logs")
    prompt = "prefix-" + ("x" * 500)

    path = _common.emit_run_log(
        "claude",
        ["claude_wrapper.py", "--prompt-file", "/workspace/prompt.txt"],
        ["claude", "-p", prompt],
        prompt,
        _result(stdout=""),
    )

    assert path is not None
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["prompt"] == prompt
    assert data["prompt_head"] == prompt[:200]
    assert data["prompt_len"] == len(prompt)


def test_run_log_prune_does_not_delete_just_written_large_log(tmp_path, monkeypatch):
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path / "_logs")
    monkeypatch.setattr(_common, "_RUN_LOG_MAX_BYTES", 100)

    path = _common.emit_run_log(
        "claude",
        ["claude_wrapper.py", "--prompt", "x"],
        ["claude", "-p", "x"],
        "x" * 500,
        _result(stdout=""),
    )

    assert path is not None
    assert path.exists()


def test_run_log_cap_prune_does_not_delete_live_prompt_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(_common, "_LOG_DIR", tmp_path / "_logs")
    monkeypatch.setattr(_common, "_RUN_LOG_MAX_FILES", 1)
    runs_dir = tmp_path / "_logs" / "claude" / "runs"
    runs_dir.mkdir(parents=True)
    prompt_tmp = runs_dir / "live.prompt.tmp"
    prompt_tmp.write_text("prompt", encoding="utf-8")

    path = _common.emit_run_log(
        "claude",
        ["claude_wrapper.py", "--prompt-file", str(prompt_tmp)],
        ["claude", "-p", "x"],
        "x",
        _result(stdout=""),
    )

    assert path is not None
    assert path.exists()
    assert prompt_tmp.exists()
