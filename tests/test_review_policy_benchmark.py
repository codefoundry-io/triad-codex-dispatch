from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
sys.path.insert(0, str(BIN))

import review_policy_benchmark as benchmark  # noqa: E402


FIXTURES = ROOT / "benchmarks" / "review-policy"


def _load(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


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
