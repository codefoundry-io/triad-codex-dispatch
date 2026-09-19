"""The explicit project route must not acquire or mutate global permission state."""
from dataclasses import replace
import hashlib
import json
import sys
from pathlib import Path

import pytest

from test_antigravity_stream_json import (
    _google_selector_fixture, _formal_payload, _run_result, _stream, wrapper,
)
from test_four_leg_custody import _brief, PRO, FLASH
from test_review_round import worktree, _review_metadata  # noqa: F401

review_round = wrapper.review_round
PROJECT = "a0613764-eb21-4d72-86e6-eac3cbd20d76"
OTHER_PROJECT = "c6a7db00-14a9-4bd2-bda5-9466dfd86de5"
DENIES = ["write_file(*)", "command(*)", "unsandboxed(*)", "execute_url(*)", "mcp(*)", "read_url(*)"]


def _canonical(record):
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode() + b"\n"


@pytest.fixture
def project_case(tmp_path, monkeypatch):
    # Real permission files and real wrapper validation; only provider I/O is replaced.
    home = tmp_path / "home"
    cwd = tmp_path / "review space"
    cwd.mkdir()
    project_path = home / ".gemini" / "config" / "projects" / f"{PROJECT}.json"
    project_path.parent.mkdir(parents=True)
    record = {
        "id": PROJECT, "name": "review space",
        "projectResources": {"resources": [{"folderUri": cwd.as_uri()}]},
        "permissionGrants": {"permissionGrants": {"deny": DENIES + ["read_file(/excluded)"]}},
    }
    project_path.write_bytes(_canonical(record))
    global_path = home / ".gemini" / "antigravity-cli" / "settings.json"
    global_path.parent.mkdir()
    global_path.write_bytes(b'{"unchanged":true}\n')
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    monkeypatch.setenv("AGY_SETTINGS_PATH", str(global_path))
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _: (1, 2, 2))
    monkeypatch.setattr(wrapper, "_probe_agy_models", lambda _: {PRO, FLASH})
    monkeypatch.setattr(wrapper._common, "prune_stale_run_logs", lambda _: None)
    monkeypatch.setattr(wrapper._common, "persist_result_artifacts", lambda *a, **k: None)

    def no_lease(*a, **k):
        pytest.fail("project route entered global settings transaction")

    monkeypatch.setattr(wrapper._agy_settings, "agy_settings_guard", no_lease)
    selector_path, _, _ = _google_selector_fixture(tmp_path)
    args = ["antigravity_wrapper.py", "--prompt", "inspect approved source",
            "--cwd", str(cwd), "--sandbox", "read-only", "--project", PROJECT,
            "--model", PRO, "--effort", "high", "--google-selector-receipt",
            str(selector_path), "--expected-review-id", "review-r1", "--preflight-only"]
    return home, cwd, project_path, record, selector_path, args


@pytest.mark.parametrize("model", [PRO, FLASH])
def test_project_preflight_and_dispatch_preserve_permissions_and_bind_uuid(
    project_case, monkeypatch, capsys, tmp_path, model,
):
    home, cwd, project_path, _, selector_path, args = project_case
    monkeypatch.delenv("AGY_NO_HEADLESS_AUTOAPPROVE", raising=False)
    before = {str(p): p.read_bytes() for p in home.rglob("*") if p.is_file()}
    args[args.index("--model") + 1] = model
    monkeypatch.setattr(sys, "argv", args)
    calls = []
    verdict = _formal_payload()

    def native(_cli, cmd, child_cwd, _timeout, **kwargs):
        calls.append(cmd)
        assert child_cwd == str(cwd)
        assert cmd[-6:] == ["--model", model, "--effort", "high", "--project", PROJECT]
        assert cmd[cmd.index("--mode") + 1] == "plan"
        assert "--sandbox" in cmd
        assert "--dangerously-skip-permissions" not in cmd
        event = _stream({"status": "SUCCESS", "structured_output": verdict})
        event = event.replace(PRO, model)
        return _run_result(event)

    monkeypatch.setattr(wrapper._common, "_run_once", native)
    assert wrapper.main() == 0
    assert calls == []
    receipt_bytes = capsys.readouterr().out.encode()
    receipt = json.loads(receipt_bytes)
    assert receipt["provider_started"] is False
    assert receipt["route_args"] == ["--model", model, "--effort", "high", "--project", PROJECT]
    receipt_path = tmp_path / "preflight.json"
    receipt_path.write_bytes(receipt_bytes)
    selector = review_round.load_google_selector_receipt(selector_path, expected_review_id="review-r1")
    bound = review_round.validate_google_preflight_receipt(receipt_path, selector, expected_review_id="review-r1")
    # Both routes use the existing fixed pair contract; Flash cannot dispatch a singular prompt.
    other_model = FLASH if model == PRO else PRO
    other_record = {**receipt, "model": other_model,
                    "route_args": ["--model", other_model, "--effort", "high", "--project", PROJECT]}
    other_path = tmp_path / "other-preflight.json"
    other_path.write_bytes(_canonical(other_record))
    other = review_round.validate_google_preflight_receipt(other_path, selector, expected_review_id="review-r1")
    common = {"review_id": "review-r1", **review_round._google_selector_metadata(bound),
              "google_preflight_pair": {r.model: review_round._google_preflight_metadata(r) for r in (bound, other)}}
    digest = hashlib.sha256(_canonical(common)).hexdigest()
    metadata = {**common, "family": "google", "content_digest": digest, "worktree_review_digest": digest,
                **review_round._google_preflight_metadata(bound)}
    verdict["content_digest"] = digest
    args.remove("--preflight-only")
    args[args.index("--prompt") + 1] = "Review metadata: " + json.dumps(metadata)
    args.extend(["--google-preflight-receipt", str(receipt_path), "--pydantic", "verdict_schema:LegVerdict",
                 "--expected-family", "google", "--expected-content-digest", digest])
    assert wrapper.main() == 0
    assert len(calls) == 1
    assert json.loads(capsys.readouterr().out) == verdict
    # Formal dispatch rechecks the record even when the receipt and UUID still match.
    original_project = project_path.read_bytes()
    project_path.write_bytes(_canonical({"id": PROJECT}))
    invalid_project = project_path.read_bytes()
    assert wrapper.main() == wrapper._common.EXIT_TERMINAL
    assert len(calls) == 1
    assert capsys.readouterr().out == ""
    assert project_path.read_bytes() == invalid_project
    project_path.write_bytes(original_project)
    # Switching or dropping the project after preflight must reject before inference.
    args[args.index("--project") + 1] = OTHER_PROJECT
    assert wrapper.main() == wrapper._common.EXIT_ARG_ERROR
    assert len(calls) == 1
    index = args.index("--project")
    del args[index:index + 2]
    assert wrapper.main() == wrapper._common.EXIT_ARG_ERROR
    assert len(calls) == 1
    assert {str(p): p.read_bytes() for p in home.rglob("*") if p.is_file()} == before


@pytest.mark.parametrize("defect", ["missing", "json", "id", "cwd", "multi-root", "deny-shape",
                                  "missing-grants", "resources-shape", "root-shape", "nonstring-deny", *DENIES])
def test_project_configuration_defect_rejects_before_inference(project_case, monkeypatch, capsys, defect):
    home, cwd, path, record, _, args = project_case
    if defect == "missing":
        path.unlink()
    elif defect == "json":
        path.write_text("not JSON")
    else:
        if defect == "id":
            record["id"] = OTHER_PROJECT
        elif defect == "cwd":
            record["projectResources"]["resources"][0]["folderUri"] = home.as_uri()
        elif defect == "multi-root":
            record["projectResources"]["resources"].append({"folderUri": home.as_uri()})
        elif defect == "deny-shape":
            record["permissionGrants"]["permissionGrants"]["deny"] = {d: True for d in DENIES}
        elif defect == "missing-grants":
            del record["permissionGrants"]
        elif defect == "resources-shape":
            record["projectResources"] = []
        elif defect == "root-shape":
            record = []
        elif defect == "nonstring-deny":
            record["permissionGrants"]["permissionGrants"]["deny"].append(None)
        else:
            record["permissionGrants"]["permissionGrants"]["deny"].remove(defect)
        path.write_bytes(_canonical(record))
    before = {str(p): p.read_bytes() for p in home.rglob("*") if p.is_file()}
    monkeypatch.setattr(sys, "argv", args)
    monkeypatch.setattr(wrapper._common, "_run_once", lambda *a, **k: pytest.fail("provider started"))
    assert wrapper.main() == wrapper._common.EXIT_TERMINAL
    assert capsys.readouterr().out == ""
    assert {str(p): p.read_bytes() for p in home.rglob("*") if p.is_file()} == before


@pytest.mark.parametrize("defect", ["no-cwd", "no-sandbox", "../escape", PROJECT.upper(), "", "default-cli-project"])
def test_project_argument_defect_rejects_before_probing(project_case, monkeypatch, defect):
    *_, args = project_case
    if defect in ("no-cwd", "no-sandbox"):
        flag = "--cwd" if defect == "no-cwd" else "--sandbox"
        index = args.index(flag)
        del args[index:index + 2]
    else:
        args[args.index("--project") + 1] = defect
    monkeypatch.setattr(sys, "argv", args)
    monkeypatch.setattr(wrapper, "_probe_agy_version", lambda _: pytest.fail("invalid project reached AGY"))
    assert wrapper.main() == wrapper._common.EXIT_ARG_ERROR


@pytest.mark.parametrize("suffix", [(), ("--project", PROJECT)])
def test_project_pair_accepts_one_boundary_and_binds_digest(worktree, suffix):
    base = _brief(worktree)
    pro = replace(base.google_selector_receipt, route_args=("--model", PRO, "--effort", "high") + suffix,
                  preflight_receipt_sha256="d" * 64 if suffix else "e" * 64)
    flash = replace(base.google_flash_preflight_receipt, route_args=("--model", FLASH, "--effort", "high") + suffix)
    brief = replace(base, google_selector_receipt=pro, google_flash_preflight_receipt=flash)
    prompts = [review_round.render_worktree_review_prompt(replace(brief, family=family, google_review_model=model))
               for family, model in (("claude", PRO), ("google", PRO), ("google", FLASH), ("codex", PRO))]
    assert len({_review_metadata(p)["content_digest"] for p in prompts}) == 1


@pytest.mark.parametrize("flash_suffix", [(), ("--project", OTHER_PROJECT)])
def test_project_pair_rejects_different_permission_boundaries(worktree, flash_suffix):
    base = _brief(worktree)
    pro = replace(base.google_selector_receipt, route_args=("--model", PRO, "--effort", "high", "--project", PROJECT))
    flash = replace(base.google_flash_preflight_receipt, route_args=("--model", FLASH, "--effort", "high") + flash_suffix)
    with pytest.raises(review_round.RoundIntegrityError):
        review_round.render_worktree_review_prompt(replace(base, google_selector_receipt=pro, google_flash_preflight_receipt=flash))


@pytest.mark.parametrize("suffix", [("--project", PROJECT), ("--project", "../escape"),
                                  ("--project", PROJECT.upper()), ("--project", PROJECT, "--new-project")])
def test_project_receipt_accepts_only_canonical_suffix(project_case, tmp_path, suffix):
    _, _, _, _, selector_path, _ = project_case
    selector = review_round.load_google_selector_receipt(selector_path, expected_review_id="review-r1")
    record = {"agy_version": "1.2.2", "effort": "high", "model": PRO, "provider_started": False,
              "review_id": "review-r1", "route": "agy", "executable": str(selector.executable),
              "google_selector_receipt_sha256": selector.receipt_sha256,
              "route_args": ["--model", PRO, "--effort", "high", *suffix]}
    path = tmp_path / "preflight.json"
    payload = _canonical(record)
    path.write_bytes(payload)
    if suffix == ("--project", PROJECT):
        receipt = review_round.validate_google_preflight_receipt(path, selector, expected_review_id="review-r1")
        assert receipt.preflight_receipt_sha256 == hashlib.sha256(payload).hexdigest()
        assert review_round._google_preflight_metadata(receipt)["google_preflight_receipt_sha256"] == receipt.preflight_receipt_sha256
    else:
        with pytest.raises(review_round.RoundIntegrityError):
            review_round.validate_google_preflight_receipt(path, selector, expected_review_id="review-r1")
