"""Check the real host table against the immutable shared token contract."""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import _common
import antigravity_wrapper
import claude_wrapper
import gemini_wrapper

PAYLOAD = ROOT / "tests/fixtures/shared-spec/exit-tokens.json"
CONTRACT = json.loads(PAYLOAD.read_text())
TOKENS = {row["token"]: row["exit"] for row in CONTRACT["tokens"]}
MAP_ONLY = {"admission-refused", "vendor-timeout", "input-delivery-failed"}


def test_fixture_has_exact_published_bytes():
    assert hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() == (
        "0e27186c915d0bc4f26246830daabed2dd1f737c491dbdf5144afcd5bd943bfd"
    )


@pytest.mark.parametrize("row", CONTRACT["tokens"], ids=lambda row: row["token"])
def test_every_shared_token_maps_to_its_contract_exit(row):
    assert _common.map_classification_to_exit(row["token"]) == row["exit"]
    assert getattr(_common, row["exit_name"]) == row["exit"]


def test_shared_exit_constants_and_classifier_membership():
    for name, code in CONTRACT["exit_codes"].items():
        assert getattr(_common, name) == code
    assert _common.CLASSIFICATION_TOKENS <= TOKENS.keys()
    assert _common.REPAIR_CLASSIFICATION_TOKENS <= _common.CLASSIFICATION_TOKENS
    for vendor in ("CLAUDE", "CODEX", "GEMINI", "ANTIGRAVITY"):
        assert set(getattr(_common, vendor + "_VENDOR_EXIT_MAP").values()) <= TOKENS.keys()


def _literal_classifications(module):
    """Census fixed producer literals; registries cover their dynamic values."""
    values = set()
    tree = ast.parse(inspect.getsource(module))
    for node in ast.walk(tree):
        candidates = []
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Attribute) and target.attr == "classification"
            for target in node.targets
        ):
            candidates.append(node.value)
        elif isinstance(node, ast.keyword) and node.arg == "classification":
            candidates.append(node.value)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id == "_fail" and len(node.args) >= 2):
            candidates.append(node.args[1])
        elif isinstance(node, ast.FunctionDef) and node.name == "classify":
            for returned in ast.walk(node):
                if isinstance(returned, ast.Return) and returned.value is not None:
                    candidates.extend(ast.walk(returned.value))
        values.update(value.value for value in candidates
                      if isinstance(value, ast.Constant) and isinstance(value.value, str))
    return values


@pytest.mark.parametrize("module", [_common, claude_wrapper, gemini_wrapper, antigravity_wrapper])
def test_producer_literals_are_registered_or_explicitly_internal(module):
    literals = _literal_classifications(module)
    # This state exists only between _run_once(classify_and_log=False) and the
    # AGY interpreter. The terminal-result regression below checks its replacement.
    internal = {"unclassified"} if module is _common else set()
    direct = {"route-mismatch"} if module is antigravity_wrapper else set()
    assert literals - internal - direct <= TOKENS.keys()
    assert not MAP_ONLY & literals


def test_alias_and_direct_exception_do_not_expand_repair_targets():
    assert CONTRACT["b_delta"]["inert_compatibility_aliases"] == ["permission-unavailable"]
    assert _common.map_classification_to_exit("permission-unavailable") == 65
    assert any(row.startswith("route-mismatch ")
               for row in CONTRACT["b_delta"]["emitted_without_map_row"])
    assert not (MAP_ONLY | {"route-mismatch", "permission-unavailable"}) & _common.CLASSIFICATION_TOKENS
    assert _common.map_classification_to_exit("not-a-registered-token") == 1


@pytest.mark.parametrize("mismatch", [False, True])
def test_agy_terminal_result_replaces_internal_state_and_preserves_direct_exit(mismatch):
    observed = "different-model" if mismatch else "gemini-3.1-pro-high"
    stream = "\n".join([
        json.dumps({"event": "init", "init": {"model": observed}}),
        json.dumps({"event": "result", "result": {"status": "SUCCESS", "response": "answer"}}),
    ])
    raw = _common.RunResult(exit_code=0, stdout=stream, stderr="", elapsed_s=0,
                            classification="unclassified", vendor_exit_code=0)
    result = antigravity_wrapper._interpret_run(raw, None, "gemini-3.1-pro-high")
    if mismatch:
        assert result.classification == "route-mismatch"
        assert result.exit_code == CONTRACT["exit_codes"]["EXIT_TERMINAL"]
    else:
        assert result.classification == "ok"
        assert result.exit_code == TOKENS["ok"]
