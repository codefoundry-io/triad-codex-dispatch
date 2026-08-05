#!/usr/bin/env python3
"""Aggregate captured batched and focused-review benchmark evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _ratio(numerator: int, denominator: int) -> float:
    return 1.0 if denominator == 0 else numerator / denominator


def aggregate(
    baseline: dict[str, Any],
    focused: dict[str, Any],
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    case_ids = [case.get("case_id") for case in cases]
    if any(not isinstance(case_id, str) or not case_id for case_id in case_ids):
        raise ValueError("every benchmark case needs a non-empty case_id")
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("benchmark case_id values must be unique")
    if not cases:
        raise ValueError("benchmark requires at least one case")

    expected = {
        case["case_id"]: set(case.get("expected_finding_ids", []))
        for case in cases
    }
    results = focused.get("results")
    if not isinstance(results, list):
        raise ValueError("focused results must be a list")
    by_case: dict[str, dict[str, Any]] = {}
    for result in results:
        if not isinstance(result, dict) or result.get("case_id") not in expected:
            raise ValueError("focused result references an unknown case")
        case_id = result["case_id"]
        if case_id in by_case:
            raise ValueError(f"duplicate focused result for {case_id}")
        by_case[case_id] = result

    planted = 0
    detected = 0
    false_findings = 0
    valid = 0
    mutations = 0
    for case_id, expected_ids in expected.items():
        planted += len(expected_ids)
        result = by_case.get(case_id, {})
        actual_ids = set(result.get("finding_ids", []))
        detected += len(expected_ids & actual_ids)
        false_findings += len(actual_ids - expected_ids)
        valid += result.get("contract_valid") is True
        mutations += result.get("mutation_admitted") is True

    if planted == 0:
        raise ValueError("benchmark requires at least one planted finding")

    baseline_calls = baseline.get("planned_calls_per_round")
    focused_calls = focused.get("calls_per_round")
    if not isinstance(baseline_calls, int) or baseline_calls <= 0:
        raise ValueError("baseline planned_calls_per_round must be positive")
    if not isinstance(focused_calls, int) or focused_calls <= 0:
        raise ValueError("focused calls_per_round must be positive")

    case_count = len(cases)
    return {
        "policy": "focused-convergent",
        "baseline": {
            "calls_per_round": baseline_calls,
            "batch_artifacts": baseline.get("batch_artifacts", 0),
            "prompt_bytes": baseline.get("prompt_bytes"),
        },
        "focused": {
            "calls_per_round": focused_calls,
            "batch_artifacts": focused.get("batch_artifacts", 0),
            "planted_defect_recall": _ratio(detected, planted),
            "contract_validity_rate": _ratio(valid, case_count),
            "false_finding_count": false_findings,
            "mutation_admitted_count": mutations,
            "case_count": case_count,
            "call_reduction": 1.0 - (focused_calls / baseline_calls),
        },
    }


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--focused", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    args = parser.parse_args()
    report = aggregate(
        _load(args.baseline),
        _load(args.focused),
        _load(args.cases),
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
