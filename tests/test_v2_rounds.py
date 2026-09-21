"""Named-entry accounting uses real capture, immutable custody and v2 validation."""
from __future__ import annotations

import copy
import importlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import review_round
from test_review_round import worktree, _lifecycle_packet
from test_v2_producer_adapter import verdict


def implementation():
    assert importlib.util.find_spec("review_round_v2") is not None, "operational v2 collector is required"
    return importlib.import_module("review_round_v2")


@pytest.fixture
def round_fixture(tmp_path, monkeypatch, worktree):
    def build(*, make_basis=True, adapter_transform=None):
        mod = implementation()
        config_dir = worktree / ".agents"
        config_dir.mkdir()
        config = config_dir / "triad-review-legs.json"
        config.write_text(json.dumps({"schema": "triad-review-legs.v2", "legs": [{
            "name": "trial", "vendor": "codex", "enabled": True,
            "acceptance": "informational", "timeout_s": 120,
            "codex": {"model": "gpt-5.6-terra", "reasoning": "high"}}]}))
        root, shared = _lifecycle_packet(tmp_path, monkeypatch, "v2-fixture", source_root=worktree)
        calls = []

        def adapters(roster, *, review_id, cwd, authentication_class, native_capabilities, receipt_root, attempt=1,
                     review_web_authorized=False):
            calls.append([entry["name"] for entry in roster["legs"] if entry["enabled"]])
            output = {}
            for entry in roster["legs"]:
                if not entry["enabled"]:
                    continue
                family = entry["vendor"]
                route = "agy" if family == "google" else None
                block = entry[route or family]
                output[entry["name"]] = {
                    "family": family, "route": route, "transport_route": route or ("native" if family == "codex" else "claude"),
                    "binary": None if family == "codex" else "/fixture/" + (route or family),
                    "cli_version": None if family == "codex" else "1.2.7",
                    "model": block["model"], "effort": block.get("reasoning", block.get("effort")),
                    "agent": block.get("agent"), "timeout_s": entry["timeout_s"],
                    "cwd": str(cwd), "capabilities_checked": True,
                    "preflight_sha256": "b" * 64 if route else None,
                    "preflight_file": None, "selector_file": None,
                }
                output[entry["name"]]["review_web_authorized"] = review_web_authorized
                if family == "codex" and review_web_authorized:
                    output[entry["name"]]["native_web_available"] = native_capabilities.get("web_available") is True
            return adapter_transform(output) if adapter_transform is not None else output

        monkeypatch.setattr(mod, "prepare_adapters", adapters)
        request = {"review_id": "v2-fixture", "project_root": str(worktree),
                   "prepared_dir": str(shared), "worktree": str(worktree), "mode": "guarded-worktree",
                   "objective": "Check complete API", "criteria": ["contract", "correctness"],
                   "approved_boundary": ["local plugin"], "authentication_class": "personal-google",
                   "native_capabilities": {"source": "native-spawn-tool", "models": {"gpt-5.6-terra": ["high", "xhigh"]}},
                   "prior_residual": "Prior finding and rebuttal: no inherited approval."}
        basis = mod.create_basis(request, root=root) if make_basis else None
        return mod, basis, root, worktree, request, calls
    return build


def start(fixture, name):
    mod, basis, *_ = fixture
    return mod.allocate_attempt(Path(basis["basis_file"]), name)


def finish(fixture, allocation, *, changes=None, failed=False, reads=None,
           raw_override=None, receipt_changes=None):
    mod, basis, *_ = fixture
    expected = allocation["binding"]
    adapter = basis["adapters"][expected["leg_name"]]
    data = verdict(**expected, **(changes or {}))
    transport = {"schema_version": 2, "route": adapter["transport_route"],
                 "binary": adapter["binary"], "cli_version": adapter["cli_version"],
                 "attempt": expected["attempt"],
                 "stdin_delivery": "complete" if adapter["family"] == "claude" else "not-used"}
    # Host receipt is an observation, not model-produced verdict content.
    receipt = {"review_binding": expected, "transport": transport,
               "exit_code": 1 if failed else 0, "vendor_exit_code": 1 if failed else 0,
               "classification": "unknown" if failed else "ok", "runtime_identity": "unexposed",
               "observation_source": "native-host" if adapter["family"] == "codex" else "cli-run-log",
               "provider_reference": "fixture-terminal-" + expected["leg_name"],
               "stdout": "" if failed else json.dumps(data), "stderr": "fixture failure" if failed else "",
               "validated": None if failed else data}
    read_evidence = {"review_binding": expected, "exposure": "unexposed", "observations": None}
    if reads is not None:
        read_evidence = reads
    receipt.update(receipt_changes or {})
    return mod.record_attempt(Path(basis["basis_file"]), expected["leg_name"],
                              receipt=receipt, raw_verdict=(raw_override if raw_override is not None
                                                          else b"" if failed else json.dumps(data).encode()),
                              read_evidence=read_evidence)


def all_success(fixture):
    return {name: finish(fixture, start(fixture, name)) for name in fixture[1]["enabled"]}


def test_all_n_entries_and_resolved_invocations_are_bound_before_inference(round_fixture):
    round_fixture = round_fixture()
    mod, basis, root, _, _, calls = round_fixture
    assert calls == [["claude", "codex", "google", "trial"]]
    assert basis["enabled"] == ["claude", "codex", "google", "trial"]
    outputs = [start(round_fixture, name) for name in basis["enabled"]]
    assert len({row["result_file"] for row in outputs}) == 4
    assert len({row["read_evidence_file"] for row in outputs}) == 4
    for item in outputs:
        assert Path(item["prompt_file"]).is_file()
        assert item["binding"]["content_digest"] == basis["content_digest"]
        assert item["binding"]["attempt"] == 1
        assert "Prior finding and rebuttal" in Path(item["prompt_file"]).read_text()
        invocation = item["invocation"]
        if item["binding"]["family"] == "codex":
            assert invocation["tool"] == "collaboration.spawn_agent"
            assert invocation["arguments"]["fork_turns"] == "none"
            assert invocation["arguments"]["model"] == basis["adapters"][item["binding"]["leg_name"]]["model"]
        else:
            assert "--expected-leg-name" in invocation["argv"]
            assert "--expected-attempt" in invocation["argv"]
            assert str(root / "results" / item["binding"]["leg_name"]) in invocation["env"]["TRIAD_DISPATCH_LOG_DIR"]


def test_unfinished_entry_blocks_and_all_n_positive_completion_agrees(round_fixture):
    round_fixture = round_fixture()
    mod, basis, *_ = round_fixture
    outcome = mod.collect(Path(basis["basis_file"]))
    assert outcome["status"] == "INCOMPLETE" and set(outcome["missing"]) == set(basis["enabled"])
    all_success(round_fixture)
    outcome = mod.collect(Path(basis["basis_file"]))
    assert outcome["status"] == "AGREED"
    assert outcome["families"] == ["claude", "codex", "google"]
    assert len(outcome["legs"]) == 4


@pytest.mark.parametrize("kind", ["blocking", "uncertainty", "minor-negative"])
def test_informational_label_never_exempts_findings_or_questions(round_fixture, kind):
    round_fixture = round_fixture()
    mod, basis, *_ = round_fixture
    for name in basis["enabled"]:
        alloc = start(round_fixture, name)
        changes = {}
        if name == "trial":
            changes = {"verdict": "DO NOT MERGE"}
            if kind == "uncertainty":
                changes["open_questions"] = ["necessary evidence missing"]
            else:
                changes["findings"] = [{"path": "source.py", "line": 1,
                    "severity": "must-fix" if kind == "blocking" else "Minor",
                    "summary": "fixture", "trigger": "fixture input", "evidence": "source.py:1",
                    "context_known": True}]
        finish(round_fixture, alloc, changes=changes)
    outcome = mod.collect(Path(basis["basis_file"]))
    assert outcome["status"] == ("AGREED" if kind == "minor-negative" else "BLOCKED")
    if kind == "minor-negative":
        assert outcome["selection_deviations"] == ["trial"]


def test_same_basis_failed_entry_only_retry_preserves_completed_siblings(round_fixture):
    round_fixture = round_fixture()
    mod, basis, root, *_ = round_fixture
    original = {}
    for name in basis["enabled"]:
        alloc = start(round_fixture, name)
        finish(round_fixture, alloc, failed=name == "trial")
        original[name] = Path(alloc["result_file"]).read_bytes() if name != "trial" else None
    second = mod.allocate_attempt(Path(basis["basis_file"]), "trial", diagnosis="transient provider refusal verified")
    assert second["binding"]["attempt"] == 2
    assert second["binding"]["content_digest"] == basis["content_digest"]
    finish(round_fixture, second)
    assert mod.collect(Path(basis["basis_file"]))["status"] == "AGREED"
    assert (root / "results/trial/attempt-1/terminal.json").is_file()
    for name, raw in original.items():
        if raw is not None:
            assert (root / "results" / name / "attempt-1/result.json").read_bytes() == raw


def test_valid_negative_and_missing_diagnosis_are_not_transport_retry(round_fixture):
    round_fixture = round_fixture()
    mod, basis, *_ = round_fixture
    alloc = start(round_fixture, "codex")
    finish(round_fixture, alloc, changes={"verdict": "DO NOT MERGE", "open_questions": ["unresolved"]})
    with pytest.raises(ValueError):
        mod.allocate_attempt(Path(basis["basis_file"]), "codex", diagnosis="retry because dislike verdict")
    finish(round_fixture, start(round_fixture, "trial"), failed=True)
    with pytest.raises(ValueError):
        mod.allocate_attempt(Path(basis["basis_file"]), "trial")


@pytest.mark.parametrize("swap", ["name", "attempt", "route", "digest"])
def test_sibling_or_changed_read_evidence_is_rejected(round_fixture, swap):
    round_fixture = round_fixture()
    alloc = start(round_fixture, "trial")
    expected = copy.deepcopy(alloc["binding"])
    key, value = {"name": ("leg_name", "codex"), "attempt": ("attempt", 2),
                  "route": ("route", "agy"), "digest": ("content_digest", "f" * 64)}[swap]
    expected[key] = value
    with pytest.raises(ValueError):
        finish(round_fixture, alloc, reads={"review_binding": expected, "exposure": "unexposed", "observations": None})


@pytest.mark.parametrize("changed", ["source", "basis", "prompt", "result", "read-evidence"])
def test_final_integrity_refuses_every_changed_basis_or_evidence(round_fixture, changed):
    round_fixture = round_fixture()
    mod, basis, root, worktree, *_ = round_fixture
    all_success(round_fixture)
    targets = {"source": worktree / "source.py", "basis": Path(basis["basis_file"]),
               "prompt": root / "results/codex/attempt-1/prompt.md",
               "result": root / "results/codex/attempt-1/result.json",
               "read-evidence": root / "results/codex/attempt-1/read-evidence.json"}
    target = targets[changed]
    target.write_bytes(target.read_bytes() + b" ")
    with pytest.raises(ValueError):
        mod.collect(Path(basis["basis_file"]))


def test_no_attempt_or_terminal_result_can_be_overwritten(round_fixture):
    round_fixture = round_fixture()
    mod, basis, *_ = round_fixture
    alloc = start(round_fixture, "codex")
    with pytest.raises(ValueError):
        mod.allocate_attempt(Path(basis["basis_file"]), "codex")
    finish(round_fixture, alloc)
    with pytest.raises(ValueError):
        finish(round_fixture, alloc)
