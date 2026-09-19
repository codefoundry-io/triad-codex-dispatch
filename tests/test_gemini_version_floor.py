"""Formal Gemini preflight must observe and bind a supported CLI version."""
import json
import subprocess

import pytest

from test_provider_wrappers import (
    _common, _formal_gemini_help, _google_selector_fixture,
    gemini_wrapper,
)
from test_review_round import _canonical_json_bytes, _prepared_digest, _review_metadata, ReviewBrief, prepared, review_round


@pytest.fixture
def version_case(tmp_path):
    path, _, selected = _google_selector_fixture(tmp_path)
    selector = review_round.load_google_selector_receipt(path,
        expected_review_id="review-r1", expected_route="gemini")
    return selector, selected, tmp_path


def _probe(case, monkeypatch, *, version="0.60.0", failure=None):
    selector, selected, cwd = case
    calls = []
    def run(argv, **kwargs):
        calls.append((argv, kwargs))
        if argv[-1] == "--version":
            if failure == "timeout":
                raise subprocess.TimeoutExpired(argv, 15)
            if failure == "oserror":
                raise OSError("synthetic version failure")
            return subprocess.CompletedProcess(argv, 1 if failure == "nonzero" else 0,
                                               version + "\n", "")
        return subprocess.CompletedProcess(argv, 0, _formal_gemini_help(), "")
    monkeypatch.setattr(gemini_wrapper.subprocess, "run", run)
    monkeypatch.setattr(gemini_wrapper, "run_cli_with_retry", lambda *a, **kw:
                        pytest.fail("preflight started provider inference"))
    result = gemini_wrapper._run_preflight(str(selected), str(cwd), 600, selector)
    return result, calls


@pytest.mark.parametrize("version", [
    "0.33.9", "0.34.0-rc.1", "not-a-version", "0.60.0\n0.33.0", "0.34",
    "00.34.0", "0.60.0-01", "0.60.0-alpha..1", "0.60.0+build..1",
])
def test_unsupported_version_refuses_before_help(version_case, monkeypatch, capsys, version):
    result, calls = _probe(version_case, monkeypatch, version=version)
    assert result == _common.EXIT_ARG_ERROR
    assert [argv[-1] for argv, _ in calls] == ["--version"]
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("version", [
    "0.34.0", "0.60.0", "1.0.0", "0.34.0+build.1", "0.34.1-rc.1",
])
def test_supported_version_is_recorded_with_exact_probes(
    version_case, monkeypatch, capsys, version,
):
    monkeypatch.setenv("GEMINI_API_KEY", "synthetic-must-be-scrubbed")
    result, calls = _probe(version_case, monkeypatch, version=version)
    selector, selected, cwd = version_case
    assert result == 0
    record = json.loads(capsys.readouterr().out)
    assert record.get("gemini_version") == version
    assert record["provider_started"] is False
    assert [argv for argv, _ in calls] == [[str(selected), "--version"], [str(selected), "--help"]]
    assert calls[0][1]["timeout"] == 15
    for _, options in calls:
        assert options["cwd"] == str(cwd)
        assert "GEMINI_API_KEY" not in options["env"]
    path = cwd / "record.json"
    path.write_bytes(_canonical_json_bytes(record))
    review_round.validate_google_preflight_receipt(path, selector, expected_review_id="review-r1")


@pytest.mark.parametrize("failure", ["nonzero", "timeout", "oserror"])
def test_version_probe_failure_stops_before_help(version_case, monkeypatch, capsys, failure):
    result, calls = _probe(version_case, monkeypatch, failure=failure)
    assert result == _common.EXIT_ARG_ERROR
    assert [argv[-1] for argv, _ in calls] == ["--version"]
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("bad_version", [None, "", "0.33.9", "0.34.0-rc.1", 123])
def test_receipt_refuses_missing_or_unsupported_observed_version(
    version_case, monkeypatch, capsys, bad_version,
):
    selector, _, cwd = version_case
    assert _probe(version_case, monkeypatch)[0] == 0
    record = json.loads(capsys.readouterr().out)
    if bad_version is None:
        record.pop("gemini_version", None)
    else:
        record["gemini_version"] = bad_version
    path = cwd / "record.json"
    path.write_bytes(_canonical_json_bytes(record))
    with pytest.raises(review_round.RoundIntegrityError):
        review_round.validate_google_preflight_receipt(path, selector, expected_review_id="review-r1")


def test_observed_version_changes_the_common_basis(version_case, prepared, monkeypatch, capsys):
    selector, _, cwd = version_case
    digests = []
    for version in ("0.34.0", "0.60.0"):
        assert _probe(version_case, monkeypatch, version=version)[0] == 0
        path = cwd / "record.json"
        path.write_bytes(_canonical_json_bytes(json.loads(capsys.readouterr().out)))
        receipt = review_round.validate_google_preflight_receipt(
            path, selector, expected_review_id="review-r1")
        brief = ReviewBrief(review_id="review-r1", review_kind="implementation-review",
            family="claude", objective="Review source.", prepared_dir=prepared,
            content_digest=_prepared_digest(prepared), criteria=("correctness",),
            approved_boundary=("source",), google_selector_receipt=receipt)
        digests.append(_review_metadata(review_round.render_review_prompt(brief))["content_digest"])
    assert digests[0] != digests[1]
