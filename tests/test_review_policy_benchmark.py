from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
sys.path.insert(0, str(BIN))

import review_policy_benchmark as benchmark  # noqa: E402


FIXTURES = ROOT / "benchmarks" / "review-policy"
EXPECTED_BENCHMARK_FILES = frozenset(
    {
        "baseline-batched.json",
        "cases.json",
        "fixtures/round-1/REVIEW.diff",
        "fixtures/round-1/TASK.md",
        "fixtures/round-1/clean/contract.md",
        "fixtures/round-1/clean/profile.py",
        "fixtures/round-1/config_doc/deployment.md",
        "fixtures/round-1/config_doc/settings.json",
        "fixtures/round-1/cross_file/caller.py",
        "fixtures/round-1/cross_file/parser.py",
        "fixtures/round-1/local_defect/validator.py",
        "fixtures/round-2/REVIEW.diff",
        "fixtures/round-2/TASK.md",
        "fixtures/round-2/clean/contract.md",
        "fixtures/round-2/clean/profile.py",
        "fixtures/round-2/config_doc/deployment.md",
        "fixtures/round-2/config_doc/settings.json",
        "fixtures/round-2/cross_file/caller.py",
        "fixtures/round-2/cross_file/parser.py",
        "fixtures/round-2/local_defect/validator.py",
        "focused-convergent-report.json",
        "focused-convergent-runtime.json",
        "focused-convergent-skill.json",
    }
)


def _load(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_benchmark_evidence_filesystem_inventory_is_exact() -> None:
    # Stray untracked files intentionally fail because the complete distributed
    # evidence directory is contract-bound.
    actual = {
        path.relative_to(FIXTURES).as_posix()
        for path in FIXTURES.rglob("*")
        if path.is_file()
    }

    assert actual == EXPECTED_BENCHMARK_FILES


def test_focused_policy_replaces_captured_batch_fanout_without_losing_recall():
    baseline = _load("baseline-batched.json")
    cases = _load("cases.json")
    focused = {
        "batch_artifacts": 0,
        "calls_per_round": 3,
        "results": [
            {"case_id": case["case_id"], "contract_valid": True,
             "finding_ids": case["expected_finding_ids"], "mutation_admitted": False}
            for case in cases
        ],
    }

    report = benchmark.aggregate(baseline, focused, cases)

    assert report["focused"]["calls_per_round"] == 3
    assert report["baseline"]["calls_per_round"] == 24
    assert report["focused"]["planted_defect_recall"] == 1.0
    assert report["focused"]["contract_validity_rate"] == 1.0
    assert report["focused"]["batch_artifacts"] == 0
    assert report["policy"] == "focused-convergent"


def test_corrected_fixture_closes_both_local_contract_defects() -> None:
    cases = _load("cases.json")
    local = next(case for case in cases if case["case_id"] == "local-defect")
    corrected = (
        FIXTURES / "fixtures" / "round-2" / "local_defect" / "validator.py"
    ).read_text(encoding="utf-8")

    assert local["expected_finding_ids"] == ["LOCAL-1", "LOCAL-2"]
    assert "type(raw) is not int" in corrected
    assert "int(raw)" not in corrected


def test_checked_in_runtime_benchmark_proves_two_round_convergence() -> None:
    baseline = _load("baseline-batched.json")
    cases = _load("cases.json")
    focused = _load("focused-convergent-runtime.json")

    report = benchmark.aggregate(baseline, focused, cases)

    assert focused["total_calls"] == 6
    assert [round_["verdicts"] for round_ in focused["rounds"]] == [
        {"claude": "NOT-SAFE", "google": "NOT-SAFE", "codex": "NOT-SAFE"},
        {"claude": "SAFE", "google": "SAFE", "codex": "SAFE"},
    ]
    assert all(round_["integrity"] == "ROUND_INTEGRITY_OK" for round_ in focused["rounds"])
    assert report["focused"]["planted_defect_recall"] == 1.0
    assert report["focused"]["contract_validity_rate"] == 1.0
    assert report["focused"]["false_finding_count"] == 0
    assert report["focused"]["mutation_admitted_count"] == 0
    assert report["focused"]["call_reduction"] == 0.875
    assert report == _load("focused-convergent-report.json")


def test_benchmark_rejects_zero_cases() -> None:
    with pytest.raises(ValueError, match="at least one case"):
        benchmark.aggregate(
            {"planned_calls_per_round": 24},
            {"calls_per_round": 3, "results": []},
            [],
        )


def test_benchmark_rejects_zero_planted_findings() -> None:
    cases = [{"case_id": "clean", "expected_finding_ids": []}]
    focused = {
        "calls_per_round": 3,
        "results": [
            {
                "case_id": "clean",
                "contract_valid": True,
                "finding_ids": [],
                "mutation_admitted": False,
            }
        ],
    }

    with pytest.raises(ValueError, match="at least one planted finding"):
        benchmark.aggregate(
            {"planned_calls_per_round": 24},
            focused,
            cases,
        )
