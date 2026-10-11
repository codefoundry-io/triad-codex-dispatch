"""C43: documented quota sentences are terminal only on their emitting CLI.

Source: triad-dispatch-spec 3afc4d7, contracts/vendor-failure-lines.json,
and shared-dev-log DL-117. This covers its two missing quota sentences,
not all C43 carriers or the separate authentication STOP contract. The text is
fed directly to the classifier; these inputs do not assert an AGY stream shape.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bin"))
import _common


QUOTA_SENTENCES = [
    ("codex", "You've hit your usage limit…"),
    ("antigravity", "Your AI credits balance is too low to continue."),
]
CLIS = ("codex", "claude", "gemini", "antigravity")


@pytest.fixture(autouse=True)
def no_operator_extension(monkeypatch):
    # C43 explicitly has no user extension; do not read the operator's config.
    monkeypatch.setattr(_common, "_load_classifier_extension", lambda: {})


@pytest.mark.parametrize("cli,sentence", QUOTA_SENTENCES)
def test_C43_measured_quota_is_terminal_on_its_cli(cli, sentence):
    result = _common.classify(cli, sentence, "", 1, vendor_exit_code=1)
    assert result == "cli-subscription-cap"
    assert _common.map_classification_to_exit(result) == 65


@pytest.mark.parametrize("cli,sentence", [
    (cli, sentence) for owner, sentence in QUOTA_SENTENCES for cli in CLIS if cli != owner
])
def test_C43_quota_sentence_does_not_classify_another_cli(cli, sentence):
    assert _common.classify(cli, sentence, "", 1, vendor_exit_code=1) == "unknown"


@pytest.mark.parametrize("cli,sentence", QUOTA_SENTENCES)
def test_C43_successful_answer_quoting_quota_stays_successful(cli, sentence):
    assert _common.classify(cli, "", sentence, 0, vendor_exit_code=0) == "ok"


@pytest.mark.parametrize("cli,sentence", QUOTA_SENTENCES)
def test_C43_quota_does_not_replace_wrapper_timeout(cli, sentence):
    assert _common.classify(cli, sentence, "", _common.EXIT_TIMEOUT) == "timeout"


def test_C43_existing_extension_remains_scoped_to_its_cli(monkeypatch):
    monkeypatch.setattr(_common, "_load_classifier_extension", lambda: {
        "claude": {"patterns": {"CLI_SUB_CAP_PATTERNS": ["fixture quota exhausted"]}},
    })
    assert _common.classify("claude", "fixture quota exhausted", "", 1) == "cli-subscription-cap"
    assert _common.classify("antigravity", "fixture quota exhausted", "", 1) == "unknown"
