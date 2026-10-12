"""C79: generated Gemini calls expose the bound packet, not sibling custody."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from test_review_round import worktree, _lifecycle_packet
from test_v2_google_wrappers import route, ready
import review_adapters_v2
import review_round_v2


@pytest.fixture
def packet_round(tmp_path, monkeypatch, worktree):
    monkeypatch.setenv("TMPDIR", str(tmp_path.resolve()))
    monkeypatch.setenv("TRIAD_WRAPPER_ALLOWED_ROOTS", str(tmp_path.resolve()))
    config = worktree / ".agents"
    config.mkdir()
    (config / "triad-review-legs.json").write_text(json.dumps({
        "schema": "triad-review-legs.v2", "legs": [
            {"name": "claude", "enabled": False},
            {"name": "codex", "enabled": False},
            {"name": "google", "google": {"route": "gemini"}}]}))
    (worktree / "related.py").write_text("RELATED_PRODUCT_MARKER\n")
    root, shared = _lifecycle_packet(tmp_path, monkeypatch, "packet-case", source_root=worktree)
    executable = tmp_path / "gemini"
    journal = tmp_path / "vendor-call.json"
    # Only the vendor boundary is replaced. The actual producer, preflight,
    # wrapper, subprocess transport and collector run together.
    executable.write_text(f"#!{sys.executable}\n" + '''
import json, pathlib, sys
args = sys.argv[1:]
if args == ["--version"]:
    print("0.63.0"); sys.exit(0)
if args == ["--help"]:
    print('  -m, --model Model [string]')
    print('  --approval-mode Set the approval mode [choices: "default", "plan"]')
    print('  --policy Additional policy files or directories to load [array]')
    print('  --include-directories Additional directories to include in the workspace [array]')
    sys.exit(0)
prompt = args[args.index("-p") + 1]
if (pathlib.Path(JOURNAL).parent / "fail-provider").exists():
    print("fixture provider failed", file=sys.stderr); sys.exit(1)
metadata = json.loads(next(line.removeprefix("Review v2 metadata: ")
    for line in prompt.splitlines() if line.startswith("Review v2 metadata: ")))
roots = [pathlib.Path.cwd(), *(pathlib.Path(args[i + 1]) for i, flag in enumerate(args)
                             if flag == "--include-directories")]
files = [pathlib.Path(PACKET) / "TASK.md", pathlib.Path(PACKET) / "REVIEW.diff",
         pathlib.Path.cwd() / "related.py"]
read = {str(file): file.read_text() for file in files
        if any(file.is_relative_to(root) for root in roots)
        and not ((pathlib.Path(JOURNAL).parent / "deny-packet").exists() and file.parent == pathlib.Path(PACKET))}
pathlib.Path(JOURNAL).write_text(json.dumps({"argv": args, "roots": list(map(str, roots)), "read": read}))
data = {key: metadata[key] for key in ("review_id", "family", "content_digest", "leg_name", "attempt", "route")}
data.update(schema_version=2, verdict="SAFE TO MERGE" if len(read) == 3 else "DO NOT MERGE",
            criteria_checked=["correctness"], findings=[], affected_surfaces_inspected=[pathlib.Path(file).name for file in read],
            open_questions=[] if len(read) == 3 else ["Required packet is outside workspace"])
print(json.dumps({"response": json.dumps(data)}))
'''.replace("PACKET", repr(str(shared))).replace("JOURNAL", repr(str(journal))))
    executable.chmod(0o755)
    monkeypatch.setattr(review_adapters_v2, "resolve_binary",
                        lambda name: str(executable) if name == "gemini" else None)
    request = {"review_id": "packet-case", "project_root": str(worktree),
        "prepared_dir": str(shared), "worktree": str(worktree), "mode": "guarded-worktree",
        "objective": "Read the task, diff and related source", "criteria": ["correctness"],
        "approved_boundary": ["product source"], "authentication_class": "gemini-enterprise",
        "native_capabilities": {}}
    return request, root, shared, journal


def launch(allocation):
    invocation = allocation["invocation"]
    result = subprocess.run(invocation["argv"], env={**os.environ, **invocation["env"]},
                            capture_output=True, text=True, timeout=30)
    Path(invocation["stdout_file"]).write_text(result.stdout)
    Path(invocation["stderr_file"]).write_text(result.stderr)
    return result


def record(basis, allocation):
    logs = list((Path(allocation["folder"]) / "logs/gemini/runs").glob("*.json"))
    assert len(logs) == 1
    return review_round_v2.record_cli_attempt(Path(basis["basis_file"]), "google", run_log=logs[0])


def test_C79_generated_formal_call_reads_external_packet_and_related_source(packet_round):
    request, root, shared, journal = packet_round
    basis = review_round_v2.create_basis(request, root=root)
    allocation = review_round_v2.allocate_attempt(Path(basis["basis_file"]), "google")
    result = launch(allocation)
    assert result.returncode == 0, result.stderr
    verdict = json.loads(result.stdout)
    assert verdict["verdict"] == "SAFE TO MERGE", verdict["open_questions"]
    observation = json.loads(journal.read_text())
    assert observation["read"][str(shared / "TASK.md")] == "current task\n"
    assert observation["read"][str(shared / "REVIEW.diff")] == "current diff\n"
    assert observation["read"][str(Path(request["worktree"]) / "related.py")] == "RELATED_PRODUCT_MARKER\n"
    assert observation["roots"] == [request["worktree"], str(shared)]
    assert "--policy" in observation["argv"]
    assert observation["argv"][observation["argv"].index("--approval-mode") + 1] == "plan"
    receipt = json.loads(Path(allocation["adapter"]["preflight_file"]).read_text())
    assert receipt["review_packet_dir"] == str(shared)
    assert receipt["route_args"][-2:] == ["--include-directories", str(shared)]
    assert record(basis, allocation)["state"] == "COMPLETE"
    assert review_round_v2.collect(Path(basis["basis_file"]))["status"] == "AGREED"


def test_C79_access_gap_remains_complete_negative_not_transport_retry(packet_round):
    request, root, _, journal = packet_round
    (journal.parent / "deny-packet").touch()
    basis = review_round_v2.create_basis(request, root=root)
    path = Path(basis["basis_file"])
    allocation = review_round_v2.allocate_attempt(path, "google")
    result = launch(allocation)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["verdict"] == "DO NOT MERGE"
    assert record(basis, allocation)["state"] == "COMPLETE"
    assert review_round_v2.collect(path)["status"] == "BLOCKED"
    with pytest.raises(ValueError, match="failed-to-run"):
        review_round_v2.allocate_attempt(path, "google", diagnosis="native read denied")


def test_C79_failed_provider_retry_retains_packet_control(packet_round):
    request, root, shared, journal = packet_round
    failure = journal.parent / "fail-provider"
    failure.touch()
    basis = review_round_v2.create_basis(request, root=root)
    path = Path(basis["basis_file"])
    allocation = review_round_v2.allocate_attempt(path, "google")
    assert launch(allocation).returncode != 0
    assert record(basis, allocation)["state"] == "FAILED_TO_RUN"
    failure.unlink()
    retry = review_round_v2.allocate_attempt(path, "google", diagnosis="fixture failure removed")
    assert retry["adapter"]["review_packet_dir"] == str(shared)
    assert launch(retry).returncode == 0
    assert record(basis, retry)["state"] == "COMPLETE"
    assert review_round_v2.collect(path)["status"] == "AGREED"


@pytest.mark.parametrize("route", ["gemini"], indirect=True)
@pytest.mark.parametrize("fault", ["missing", "parent", "sibling", "wrong-round", "relative", "dotdot", "symlink", "comma"])
def test_C79_invalid_packet_root_refuses_before_provider(route, monkeypatch, fault):
    import review_round
    home = route["home"]
    monkeypatch.setattr(review_round.tempfile, "gettempdir", lambda: str(home))
    shared = home / "triad-review-round-2" / "shared"
    shared.mkdir(parents=True)
    bad = {"missing": shared / "missing", "parent": shared.parent,
           "sibling": shared.parent / "results", "wrong-round": home / "triad-review-other" / "shared",
           "relative": Path("shared"), "dotdot": str(shared) + "/../shared",
           "symlink": home / "linked", "comma": home / "triad-review-round-2,other" / "shared"}[fault]
    if fault in ("sibling", "wrong-round", "comma"):
        bad.mkdir(parents=True)
    if fault == "symlink":
        bad.symlink_to(shared, target_is_directory=True)
    rc, _, error = route["invoke"](["--preflight-only", "--review-packet-dir", str(bad)])
    assert rc == 3, error
    assert route["calls"] == []


@pytest.mark.parametrize("route", ["gemini"], indirect=True)
def test_C79_receipt_refuses_omitted_packet_control_before_provider(route, monkeypatch):
    import review_round
    shared = route["home"] / "triad-review-round-2" / "shared"
    shared.mkdir(parents=True)
    monkeypatch.setattr(review_round.tempfile, "gettempdir", lambda: str(route["home"]))
    route["options"] += ["--review-packet-dir", str(shared)]
    options, _ = ready(route)
    index = options.index("--review-packet-dir")
    del options[index:index + 2]
    rc, _, error = route["invoke"](base=options)
    assert rc == 3, error
    assert route["calls"] == []


def test_C79_prepared_directory_does_not_add_a_second_root(packet_round):
    request, root, shared, _ = packet_round
    request["mode"] = "prepared-directory"
    basis = review_round_v2.create_basis(request, root=root)
    allocation = review_round_v2.allocate_attempt(Path(basis["basis_file"]), "google")
    assert allocation["adapter"]["cwd"] == str(shared)
    assert "--review-packet-dir" not in allocation["invocation"]["argv"]
    receipt = json.loads(Path(allocation["adapter"]["preflight_file"]).read_text())
    assert "review_packet_dir" not in receipt


@pytest.mark.parametrize("route", ["gemini"], indirect=True)
def test_C79_packet_preflight_requires_native_include_directory_control(route, monkeypatch):
    import gemini_wrapper
    import review_round
    shared = route["home"] / "triad-review-round-2" / "shared"
    shared.mkdir(parents=True)
    monkeypatch.setattr(review_round.tempfile, "gettempdir", lambda: str(route["home"]))
    original = gemini_wrapper.subprocess.run

    def missing_control(argv, **kwargs):
        result = original(argv, **kwargs)
        if argv[-1] == "--help":
            result.stdout = "\n".join(line for line in result.stdout.splitlines()
                                     if "--include-directories" not in line)
        return result

    monkeypatch.setattr(gemini_wrapper.subprocess, "run", missing_control)
    rc, _, error = route["invoke"](["--preflight-only", "--review-packet-dir", str(shared)])
    assert rc == 3 and "--include-directories" in error
    assert route["calls"] == []


@pytest.mark.parametrize("route", ["gemini"], indirect=True)
def test_C79_raw_call_cannot_use_formal_packet_control(route):
    rc, _, error = route["invoke"](base=["--prompt", "read", "--cwd", str(route["home"]),
        "--review-packet-dir", str(route["home"])])
    assert rc == 3 and "formal v2" in error
    assert route["calls"] == []
