from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import sys
import types
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))

import _common  # noqa: E402
import triad_formal_review_schema as formal_schema  # noqa: E402


CANONICAL_OPERAND = "triad_formal_review_schema:FormalReview"
DEFAULT_FINDING_PATH = "inputs/candidate/bin/_common.py"
DEFAULT_PACKET_DATA = "".join(f"line {line}\n" for line in range(1, 665)).encode()
DEFAULT_INPUT_MANIFEST = (
    f"{hashlib.sha256(DEFAULT_PACKET_DATA).hexdigest()}  "
    f"{DEFAULT_FINDING_PATH}\n"
).encode()
DEFAULT_SHA256SUMS = (
    f"{hashlib.sha256(DEFAULT_PACKET_DATA).hexdigest()}  "
    f"{DEFAULT_FINDING_PATH}\n"
    f"{hashlib.sha256(DEFAULT_INPUT_MANIFEST).hexdigest()}  INPUT_SHA256SUMS\n"
).encode()
DEFAULT_PACKET_SHA256 = hashlib.sha256(DEFAULT_SHA256SUMS).hexdigest()


def _load_canonical(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TRIAD_WRAPPER_HARDENED", "1")
    monkeypatch.delenv("TRIAD_ALLOW_PYDANTIC_IMPORT", raising=False)
    monkeypatch.setattr(_common, "_packaged_formal_review_module", None)
    return _common.load_pydantic_class(CANONICAL_OPERAND)


def _packet_context(tmp_path: Path, review_id: str = "review-r3") -> dict[str, str]:
    packet = tmp_path / review_id / "packet"
    packet.mkdir(parents=True, exist_ok=True)
    leaf = packet / DEFAULT_FINDING_PATH
    leaf.parent.mkdir(parents=True, exist_ok=True)
    leaf.write_bytes(DEFAULT_PACKET_DATA)
    (packet / "INPUT_SHA256SUMS").write_bytes(DEFAULT_INPUT_MANIFEST)
    (packet / "SHA256SUMS").write_bytes(DEFAULT_SHA256SUMS)
    (packet / "PACKET_SHA256").write_text(
        f"{DEFAULT_PACKET_SHA256}\n", encoding="ascii"
    )
    return {
        "sealed_packet_root": str(packet),
        "expected_packet_sha256": DEFAULT_PACKET_SHA256,
    }


def _review(
    *,
    review_id: str = "review-r3",
    packet_sha256: str = DEFAULT_PACKET_SHA256,
    severity: str = "Minor",
    verdict: str = "SAFE",
    open_questions: list[str] | None = None,
    location: str = f"{DEFAULT_FINDING_PATH}:664",
) -> dict[str, object]:
    return {
        "review_id": review_id,
        "packet_sha256": packet_sha256,
        "verdict": verdict,
        "findings": [
            {
                "severity": severity,
                "location": location,
                "trigger": "the formal schema operand is loaded",
                "evidence": "the packaged sibling is selected",
                "correction": "keep the canonical loader path-bound",
            }
        ],
        "open_questions": [] if open_questions is None else open_questions,
    }


def test_canonical_operand_loads_under_hardening_without_broad_opt_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    schema = _load_canonical(monkeypatch)

    assert schema.__name__ == "FormalReview"
    assert schema.required_validation_context == frozenset(
        {"sealed_packet_root", "expected_packet_sha256"}
    )


def test_native_review_file_uses_canonical_sealed_packet_validation(
    tmp_path: Path,
) -> None:
    context = _packet_context(tmp_path)
    result_file = tmp_path / "native-review.json"
    result_file.write_text(json.dumps(_review()), encoding="utf-8")

    result = formal_schema.validate_formal_review_file(
        result_file.resolve(),
        Path(context["sealed_packet_root"]),
        context["expected_packet_sha256"],
    )

    assert result.model_dump(mode="json") == _review()


def test_native_review_file_rejects_wrong_identity_and_symlink(
    tmp_path: Path,
) -> None:
    context = _packet_context(tmp_path)
    result_file = tmp_path / "native-review.json"
    result_file.write_text(
        json.dumps(_review(review_id="wrong-review")), encoding="utf-8"
    )
    with pytest.raises(ValidationError, match="identity mismatch"):
        formal_schema.validate_formal_review_file(
            result_file.resolve(),
            Path(context["sealed_packet_root"]),
            context["expected_packet_sha256"],
        )

    result_file.write_text(json.dumps(_review()), encoding="utf-8")
    result_link = tmp_path / "native-review-link.json"
    result_link.symlink_to(result_file)
    with pytest.raises(ValueError, match="canonical existing regular file"):
        formal_schema.validate_formal_review_file(
            result_link,
            Path(context["sealed_packet_root"]),
            context["expected_packet_sha256"],
        )


def test_native_review_validator_cli_accepts_only_schema_valid_file(
    tmp_path: Path,
) -> None:
    context = _packet_context(tmp_path)
    result_file = (tmp_path / "native-review.json").resolve()
    argv = [
        sys.executable,
        str((BIN / "triad_formal_review_schema.py").resolve()),
        "--result-file",
        str(result_file),
        "--sealed-packet-root",
        context["sealed_packet_root"],
        "--expected-packet-sha256",
        context["expected_packet_sha256"],
    ]
    result_file.write_text(json.dumps(_review()), encoding="utf-8")

    accepted = subprocess.run(argv, capture_output=True, text=True, check=False)

    assert accepted.returncode == 0, accepted.stderr
    assert json.loads(accepted.stdout) == _review()

    result_file.write_text(
        json.dumps(_review(review_id="wrong-review")), encoding="utf-8"
    )
    rejected = subprocess.run(argv, capture_output=True, text=True, check=False)

    assert rejected.returncode == 2
    assert rejected.stdout == ""
    assert "identity mismatch" in rejected.stderr


def test_canonical_operand_ignores_same_named_sys_path_attacker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    attacker = tmp_path / "attacker"
    attacker.mkdir()
    (attacker / "triad_formal_review_schema.py").write_text(
        "raise AssertionError('sys.path attacker was imported')\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(attacker))
    monkeypatch.delitem(sys.modules, "triad_formal_review_schema", raising=False)

    schema = _load_canonical(monkeypatch)

    assert schema.__name__ == "FormalReview"
    assert "triad_formal_review_schema" not in sys.modules


@pytest.mark.parametrize(
    "module_name",
    ["triad_formal_review_schema", "_triad_packaged_formal_review_schema"],
)
def test_canonical_operand_ignores_poisoned_module_cache(
    monkeypatch: pytest.MonkeyPatch, module_name: str
) -> None:
    poisoned = types.ModuleType(module_name)
    poisoned.FormalReview = type("AttackerFormalReview", (), {})
    monkeypatch.setitem(sys.modules, module_name, poisoned)

    schema = _load_canonical(monkeypatch)

    assert schema is not poisoned.FormalReview
    assert schema.__module__ == "_triad_packaged_formal_review_schema"


@pytest.mark.parametrize(
    "operand",
    [
        "triad_formal_review_schema.FormalReview",
        "triad_formal_review_schema:FormalFinding",
        "triad_formal_review_schema:formalreview",
        "Triad_formal_review_schema:FormalReview",
        "package.triad_formal_review_schema:FormalReview",
        "triad_formal_review_schema_extra:FormalReview",
        "triad_formal_review_schema:FormalReview.extra",
        "triad_formal_review_schema:",
        ":FormalReview",
        " triad_formal_review_schema:FormalReview",
        "triad_formal_review_schema:FormalReview ",
        "triad_formal_review_schema::FormalReview",
    ],
)
def test_near_miss_canonical_operands_keep_the_broad_hardened_gate(
    monkeypatch: pytest.MonkeyPatch, operand: str
) -> None:
    monkeypatch.setenv("TRIAD_WRAPPER_HARDENED", "1")
    monkeypatch.delenv("TRIAD_ALLOW_PYDANTIC_IMPORT", raising=False)

    with pytest.raises(PermissionError):
        _common.load_pydantic_class(operand)


def test_noncanonical_schema_still_requires_the_broad_hardened_opt_in(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "custom_review_schema.py").write_text(
        "from pydantic import BaseModel\n"
        "class Review(BaseModel):\n"
        "    value: str\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setenv("TRIAD_WRAPPER_HARDENED", "1")
    monkeypatch.delenv("TRIAD_ALLOW_PYDANTIC_IMPORT", raising=False)

    with pytest.raises(PermissionError):
        _common.load_pydantic_class("custom_review_schema:Review")

    monkeypatch.setenv("TRIAD_ALLOW_PYDANTIC_IMPORT", "1")
    schema = _common.load_pydantic_class("custom_review_schema:Review")
    assert schema.__name__ == "Review"


@pytest.mark.parametrize("leaf_kind", ["symlink", "directory", "fifo"])
def test_packaged_source_reader_rejects_nonregular_or_followed_leaf(
    tmp_path: Path, leaf_kind: str
) -> None:
    leaf = tmp_path / "triad_formal_review_schema.py"
    if leaf_kind == "symlink":
        target = tmp_path / "target.py"
        target.write_text("SAFE = True\n", encoding="utf-8")
        leaf.symlink_to(target)
    elif leaf_kind == "directory":
        leaf.mkdir()
    else:
        os.mkfifo(leaf)

    with pytest.raises((ImportError, OSError)):
        _common._read_exact_regular_nofollow(leaf)


@pytest.mark.parametrize("mismatch", ["fstat", "lstat"])
def test_packaged_source_reader_rejects_open_path_identity_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mismatch: str
) -> None:
    leaf = tmp_path / "triad_formal_review_schema.py"
    leaf.write_text("HELD = True\n", encoding="utf-8")
    real_fstat = os.fstat
    real_lstat = Path.lstat

    def changed(identity: os.stat_result) -> types.SimpleNamespace:
        return types.SimpleNamespace(
            st_mode=identity.st_mode,
            st_dev=identity.st_dev,
            st_ino=identity.st_ino + 1,
        )

    if mismatch == "fstat":
        monkeypatch.setattr(
            _common.os,
            "fstat",
            lambda fd: changed(real_fstat(fd)),
        )
    else:
        monkeypatch.setattr(
            Path,
            "lstat",
            lambda self: changed(real_lstat(self)),
        )

    with pytest.raises(ImportError, match="exact regular sibling"):
        _common._read_exact_regular_nofollow(leaf)


def test_packaged_source_reader_uses_held_bytes_if_path_changes_after_attestation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    leaf = tmp_path / "triad_formal_review_schema.py"
    packaged = b"HELD_PACKAGED_BYTES = True\n"
    leaf.write_bytes(packaged)
    real_fdopen = os.fdopen

    def replace_then_open(fd: int, *args, **kwargs):
        leaf.unlink()
        leaf.write_bytes(b"ATTACKER_BYTES = True\n")
        return real_fdopen(fd, *args, **kwargs)

    monkeypatch.setattr(_common.os, "fdopen", replace_then_open)

    assert _common._read_exact_regular_nofollow(leaf) == packaged


def test_formal_review_accepts_minor_safe_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    schema = _load_canonical(monkeypatch)
    context = _packet_context(tmp_path)

    result = schema.model_validate(_review(), context=context)

    assert result.model_dump(mode="json") == _review()


def test_representative_fresh_codex_json_round_trip_uses_context_and_json_dump(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    schema = _load_canonical(monkeypatch)
    payload = _review()

    result = schema.model_validate_json(
        json.dumps(payload), context=_packet_context(tmp_path)
    )

    assert result.model_dump(mode="json") == payload


def test_formal_review_documents_json_only_nonportable_model_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    schema = _load_canonical(monkeypatch)

    assert schema.__doc__ is not None
    assert "JSON-only" in schema.__doc__
    assert "model_validate_json" in schema.__doc__
    assert "model_dump" in schema.__doc__
    assert "pickling" in schema.__doc__
    assert "re-import" in schema.__doc__


def test_canonical_prompt_block_exposes_full_nested_contract_and_verdict_rules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    schema = _load_canonical(monkeypatch)

    block = _common.schema_block_for_prompt(schema)
    prompt_schema = schema.model_json_schema()
    prompt_schema.pop("description", None)
    complete_schema = json.dumps(
        prompt_schema,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )

    assert complete_schema in block
    assert (
        "Required top-level fields: `review_id`, `packet_sha256`, `verdict`, "
        "`findings`, `open_questions`."
    ) in block
    assert (
        "Each finding requires: `severity`, `location`, `trigger`, `evidence`, "
        "`correction`."
    ) in block
    assert "`verdict` must be exactly `SAFE` or `NOT-SAFE`." in block
    assert "`severity` must be exactly `Critical`, `Major`, or `Minor`." in block
    assert "A Critical or Major finding requires `NOT-SAFE`." in block
    assert "Any non-empty `open_questions` requires `NOT-SAFE`." in block
    assert "Otherwise `verdict` must be `SAFE`." in block
    assert "cross-process pickling" not in block


def test_canonical_prompt_block_few_shots_keep_the_full_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    schema = _load_canonical(monkeypatch)

    block = _common.schema_block_for_prompt(schema)

    assert "NO FINDINGS — emit the complete envelope" in block
    assert (
        '{"review_id": "<review-id>", "packet_sha256": "<sha256>", '
        '"verdict": "SAFE", "findings": [], "open_questions": []}'
    ) in block
    assert "ONE BLOCKING FINDING — still emit the complete envelope" in block
    assert '"findings": [{"severity": "Major"' in block
    assert '"location": "inputs/candidate/<path>:<positive-line>"' in block
    assert "Return one complete top-level envelope" in block
    assert (
        "Set `review_id` and `packet_sha256` exactly to the trusted values in "
        "the runtime material"
    ) in block
    assert (
        "Use exactly one manifest-listed packet-relative path and one positive "
        "decimal line number in each `location`"
    ) in block
    assert "Use line numbers rather than function or symbol names" in block
    assert "Every required string must contain non-whitespace text" in block
    assert (
        "Represent no findings or open questions with the empty arrays `[]` and "
        "include both fields"
    ) in block
    assert "Never return" not in block
    assert "Never join" not in block


def test_canonical_formal_prompt_places_contract_after_the_user_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    schema = _load_canonical(monkeypatch)

    prompt = _common.inject_schema_to_prompt("LONG USER REQUEST", schema)

    assert (
        "<runtime_review_input>\nLONG USER REQUEST\n</runtime_review_input>"
        in prompt
    )
    assert prompt.index("=== USER REQUEST ===") < prompt.index(
        "=== FORMAL REVIEW RESPONSE CONTRACT ==="
    )
    assert (
        "The runtime material above determines review scope and evidence. The "
        "FormalReview response contract below controls the output shape."
        in prompt
    )
    assert "No markdown fences. No prose. No commentary." not in prompt
    assert prompt.rstrip().endswith(
        "Based on the user request and FormalReview contract above, return "
        "exactly one valid JSON object with no surrounding content.\nJSON:"
    )


def test_generic_pydantic_prompt_block_keeps_the_existing_compact_shape() -> None:
    class GenericPromptModel(BaseModel):
        value: str

    assert _common.schema_block_for_prompt(GenericPromptModel) == (
        "You are a JSON-only response API. Your output MUST be valid JSON "
        "and nothing else. No markdown fences. No prose. No commentary. "
        "Just a single JSON object.\n\n"
        "The JSON object must match exactly this shape:\n"
        '{"value": <string>}\n\n'
        "JSON output example:\n"
        '{"value": "<value>"}\n\n'
        "Now produce the JSON output for the user's request below. "
        "Return ONLY the JSON object — no ```, no explanation."
    )


def test_generic_body_semantics_mode_omits_transport_framing() -> None:
    class GenericPromptModel(BaseModel):
        value: str

    prompt = _common.inject_schema_to_prompt(
        "USER REQUEST",
        GenericPromptModel,
        body_semantics_only=True,
    )

    assert '"value": <string>' in prompt
    assert '{"value": "<value>"}' in prompt
    assert (
        "<runtime_review_input>\nUSER REQUEST\n</runtime_review_input>"
        in prompt
    )
    assert "valid JSON and nothing else" not in prompt
    assert "Return ONLY the JSON object" not in prompt
    assert "No markdown fences" not in prompt


def test_formal_review_body_semantics_mode_omits_transport_framing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    schema = _load_canonical(monkeypatch)

    prompt = _common.inject_schema_to_prompt(
        "LONG USER REQUEST",
        schema,
        body_semantics_only=True,
    )

    assert "LONG USER REQUEST" in prompt
    assert "complete canonical FormalReview JSON Schema" in prompt
    assert "no surrounding content" not in prompt
    assert not prompt.rstrip().endswith("JSON:")
    assert prompt.rstrip().endswith(
        "Based on the runtime review input above, perform the review and "
        "produce a FormalReview JSON body that satisfies the response contract."
    )


@pytest.mark.parametrize(
    ("severity", "open_questions"),
    [
        ("Major", []),
        ("Minor", ["A blocking evidence question remains"]),
    ],
)
def test_formal_review_accepts_consistent_not_safe_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    severity: str,
    open_questions: list[str],
) -> None:
    schema = _load_canonical(monkeypatch)
    payload = _review(
        severity=severity,
        verdict="NOT-SAFE",
        open_questions=open_questions,
    )

    result = schema.model_validate(payload, context=_packet_context(tmp_path))

    assert result.verdict == "NOT-SAFE"


@pytest.mark.parametrize("severity", ["Important", "critical", "MAJOR"])
def test_formal_finding_rejects_noncanonical_severity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, severity: str
) -> None:
    schema = _load_canonical(monkeypatch)

    with pytest.raises(ValidationError):
        schema.model_validate(
            _review(severity=severity, verdict="NOT-SAFE"),
            context=_packet_context(tmp_path),
        )


@pytest.mark.parametrize("target", ["review", "finding"])
def test_formal_models_forbid_extra_keys(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, target: str
) -> None:
    schema = _load_canonical(monkeypatch)
    payload = _review()
    if target == "review":
        payload["unexpected"] = True
    else:
        findings = payload["findings"]
        assert isinstance(findings, list) and isinstance(findings[0], dict)
        findings[0]["unexpected"] = True

    with pytest.raises(ValidationError):
        schema.model_validate(payload, context=_packet_context(tmp_path))


@pytest.mark.parametrize("mismatch", ["hash", "review"])
def test_formal_review_rejects_packet_identity_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mismatch: str
) -> None:
    schema = _load_canonical(monkeypatch)
    payload = _review()
    if mismatch == "hash":
        payload["packet_sha256"] = "b" * 64
    else:
        payload["review_id"] = "another-review"

    with pytest.raises(ValidationError, match="identity mismatch"):
        schema.model_validate(payload, context=_packet_context(tmp_path))


@pytest.mark.parametrize(
    "location",
    [
        f"/{DEFAULT_FINDING_PATH}:1",
        "inputs\\candidate\\bin\\_common.py:1",
        f"../{DEFAULT_FINDING_PATH}:1",
        "inputs/candidate/bin/not-listed.py:1",
        f"{DEFAULT_FINDING_PATH}:0",
        f"{DEFAULT_FINDING_PATH}:-1",
        f"{DEFAULT_FINDING_PATH}:line",
        f"{DEFAULT_FINDING_PATH}:665",
    ],
)
def test_formal_finding_rejects_unsafe_nonmanifest_or_invalid_line_location(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    location: str,
) -> None:
    schema = _load_canonical(monkeypatch)

    with pytest.raises(ValidationError, match="finding location"):
        schema.model_validate(
            _review(location=location),
            context=_packet_context(tmp_path),
        )


@pytest.mark.parametrize(
    "manifest_case",
    ["missing", "invalid-utf8", "malformed", "duplicate", "unsafe-entry"],
)
def test_formal_review_rejects_missing_or_malformed_input_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    manifest_case: str,
) -> None:
    schema = _load_canonical(monkeypatch)
    context = _packet_context(tmp_path)
    manifest = Path(context["sealed_packet_root"]) / "INPUT_SHA256SUMS"
    original = manifest.read_bytes()
    if manifest_case == "missing":
        manifest.unlink()
    elif manifest_case == "invalid-utf8":
        manifest.write_bytes(b"\xff")
    elif manifest_case == "malformed":
        manifest.write_text("not-a-manifest-entry\n", encoding="utf-8")
    elif manifest_case == "duplicate":
        manifest.write_bytes(original + original)
    else:
        manifest.write_text(
            f"{'a' * 64}  ../outside.py\n",
            encoding="utf-8",
        )

    with pytest.raises(ValidationError, match="INPUT_SHA256SUMS"):
        schema.model_validate(_review(), context=context)


@pytest.mark.parametrize("leaf_kind", ["symlink", "directory"])
def test_formal_review_rejects_symlink_or_nonregular_manifest_leaf(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    leaf_kind: str,
) -> None:
    schema = _load_canonical(monkeypatch)
    context = _packet_context(tmp_path)
    leaf = Path(context["sealed_packet_root"]) / DEFAULT_FINDING_PATH
    leaf.unlink()
    if leaf_kind == "symlink":
        target = tmp_path / "outside.py"
        target.write_text("outside\n", encoding="utf-8")
        leaf.symlink_to(target)
    else:
        leaf.mkdir()

    with pytest.raises(ValidationError, match="regular packet file"):
        schema.model_validate(_review(), context=context)


@pytest.mark.parametrize(
    "entry_kind", ["regular", "symlink", "fifo", "empty-directory"]
)
def test_formal_review_rejects_unlisted_packet_tree_entry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    entry_kind: str,
) -> None:
    schema = _load_canonical(monkeypatch)
    context = _packet_context(tmp_path)
    packet = Path(context["sealed_packet_root"])
    entry = packet / "unlisted"
    if entry_kind == "regular":
        entry.write_text("not in either manifest\n", encoding="utf-8")
    elif entry_kind == "symlink":
        target = tmp_path / "outside.txt"
        target.write_text("outside\n", encoding="utf-8")
        entry.symlink_to(target)
    elif entry_kind == "fifo":
        os.mkfifo(entry)
    else:
        entry.mkdir()

    with pytest.raises(ValidationError, match="packet tree"):
        schema.model_validate(_review(), context=context)


def test_formal_review_requires_input_manifest_to_equal_outer_payload_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    schema = _load_canonical(monkeypatch)
    context = _packet_context(tmp_path)
    packet = Path(context["sealed_packet_root"])
    outer_only = packet / "inputs" / "outer-only.txt"
    outer_only.write_text("bound only by SHA256SUMS\n", encoding="utf-8")
    sums = (
        f"{hashlib.sha256(DEFAULT_PACKET_DATA).hexdigest()}  "
        f"{DEFAULT_FINDING_PATH}\n"
        f"{hashlib.sha256(outer_only.read_bytes()).hexdigest()}  "
        "inputs/outer-only.txt\n"
        f"{hashlib.sha256(DEFAULT_INPUT_MANIFEST).hexdigest()}  "
        "INPUT_SHA256SUMS\n"
    ).encode()
    (packet / "SHA256SUMS").write_bytes(sums)
    digest = hashlib.sha256(sums).hexdigest()
    (packet / "PACKET_SHA256").write_text(f"{digest}\n", encoding="ascii")
    context["expected_packet_sha256"] = digest

    with pytest.raises(ValidationError, match="INPUT_SHA256SUMS entries"):
        schema.model_validate(
            _review(packet_sha256=digest),
            context=context,
        )


def test_formal_review_rejects_manifest_digest_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    schema = _load_canonical(monkeypatch)
    context = _packet_context(tmp_path)
    leaf = Path(context["sealed_packet_root"]) / DEFAULT_FINDING_PATH
    leaf.write_text("changed after manifest\n", encoding="utf-8")

    with pytest.raises(ValidationError, match="digest mismatch"):
        schema.model_validate(_review(location=f"{DEFAULT_FINDING_PATH}:1"), context=context)


def test_formal_review_streams_uncited_manifest_payload_hashes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    context = _packet_context(tmp_path)
    payload = _review()
    payload["findings"] = []
    real_read = formal_schema._read_regular_packet_file

    def reject_whole_payload_read(
        root: Path, relative_path: str, *, label: str
    ) -> bytes:
        if relative_path == DEFAULT_FINDING_PATH:
            pytest.fail(f"manifest payload used whole-file read: {relative_path}")
        return real_read(root, relative_path, label=label)

    monkeypatch.setattr(
        formal_schema, "_read_regular_packet_file", reject_whole_payload_read
    )

    result = formal_schema.FormalReview.model_validate(payload, context=context)

    assert result.model_dump(mode="json") == payload


def test_formal_review_rejects_invalid_utf8_cited_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    schema = _load_canonical(monkeypatch)
    context = _packet_context(tmp_path)
    packet = Path(context["sealed_packet_root"])
    leaf = packet / DEFAULT_FINDING_PATH
    data = b"\xff\n"
    leaf.write_bytes(data)
    (packet / "INPUT_SHA256SUMS").write_text(
        f"{hashlib.sha256(data).hexdigest()}  {DEFAULT_FINDING_PATH}\n",
        encoding="utf-8",
    )
    sums = (
        f"{hashlib.sha256(data).hexdigest()}  {DEFAULT_FINDING_PATH}\n"
        f"{hashlib.sha256((packet / 'INPUT_SHA256SUMS').read_bytes()).hexdigest()}  "
        "INPUT_SHA256SUMS\n"
    ).encode()
    (packet / "SHA256SUMS").write_bytes(sums)
    digest = hashlib.sha256(sums).hexdigest()
    (packet / "PACKET_SHA256").write_text(f"{digest}\n", encoding="ascii")
    context["expected_packet_sha256"] = digest

    with pytest.raises(ValidationError, match="UTF-8"):
        schema.model_validate(
            _review(
                packet_sha256=digest,
                location=f"{DEFAULT_FINDING_PATH}:1",
            ),
            context=context,
        )


@pytest.mark.parametrize(
    "malformed_hash",
    ["", "a" * 63, "a" * 65, "A" * 64, "g" * 64, 64],
)
def test_formal_review_rejects_malformed_expected_hash(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    malformed_hash: object,
) -> None:
    schema = _load_canonical(monkeypatch)
    context: dict[str, object] = _packet_context(tmp_path)
    context["expected_packet_sha256"] = malformed_hash
    payload = _review(packet_sha256=malformed_hash)  # type: ignore[arg-type]

    with pytest.raises(ValidationError, match="expected packet SHA-256"):
        schema.model_validate(payload, context=context)


@pytest.mark.parametrize(
    "root_kind",
    [
        "review-root",
        "filesystem-root",
        "blank-review-id",
        "relative",
        "symlink",
        "file",
    ],
)
def test_formal_review_requires_exact_review_id_packet_root_shape(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, root_kind: str
) -> None:
    schema = _load_canonical(monkeypatch)
    review = tmp_path / "review-r3"
    packet = review / "packet"
    review.mkdir()
    if root_kind == "review-root":
        root = review
        review_id = "review-r3"
    elif root_kind == "filesystem-root":
        root = Path("/")
        review_id = ""
    elif root_kind == "blank-review-id":
        blank_review = tmp_path / "   "
        root = blank_review / "packet"
        root.mkdir(parents=True)
        review_id = "   "
    elif root_kind == "relative":
        root = Path("review-r3/packet")
        review_id = "review-r3"
    elif root_kind == "symlink":
        real_packet = review / "real-packet"
        real_packet.mkdir()
        packet.symlink_to(real_packet)
        root = packet
        review_id = "review-r3"
    else:
        packet.write_text("not a directory", encoding="utf-8")
        root = packet
        review_id = "review-r3"
    context = {
        "sealed_packet_root": str(root),
        "expected_packet_sha256": "a" * 64,
    }

    with pytest.raises(ValidationError, match="sealed_packet_root"):
        schema.model_validate(_review(review_id=review_id), context=context)


@pytest.mark.parametrize(
    ("field", "coerced"),
    [
        ("review_id", 123),
        ("packet_sha256", b"a" * 64),
        ("verdict", True),
        ("findings", ()),
        ("open_questions", ()),
        ("open_questions", [123]),
        ("finding.severity", 1),
        ("finding.location", 664),
        ("finding.trigger", True),
        ("finding.evidence", b"bytes"),
        ("finding.correction", 1.0),
    ],
)
def test_formal_review_rejects_strict_type_coercion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    coerced: object,
) -> None:
    schema = _load_canonical(monkeypatch)
    payload = _review()
    if field.startswith("finding."):
        findings = payload["findings"]
        assert isinstance(findings, list) and isinstance(findings[0], dict)
        findings[0][field.removeprefix("finding.")] = coerced
    else:
        payload[field] = coerced

    with pytest.raises(ValidationError):
        schema.model_validate(payload, context=_packet_context(tmp_path))


@pytest.mark.parametrize(
    "context",
    [
        None,
        {},
        {"sealed_packet_root": "/tmp/review-r3/packet"},
        {"expected_packet_sha256": "a" * 64},
        {
            "sealed_packet_root": "/tmp/review-r3/packet",
            "expected_packet_sha256": "a" * 64,
            "unexpected": "value",
        },
    ],
)
def test_formal_review_requires_exact_validation_context(
    monkeypatch: pytest.MonkeyPatch, context: dict[str, str] | None
) -> None:
    schema = _load_canonical(monkeypatch)

    with pytest.raises(ValidationError, match="validation context"):
        schema.model_validate(_review(), context=context)


@pytest.mark.parametrize(
    ("severity", "open_questions"),
    [
        ("Critical", []),
        ("Major", []),
        ("Minor", ["Does the blocking question have an answer?"]),
    ],
)
def test_safe_rejects_blocking_findings_or_open_questions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    severity: str,
    open_questions: list[str],
) -> None:
    schema = _load_canonical(monkeypatch)

    with pytest.raises(ValidationError, match="verdict must be NOT-SAFE"):
        schema.model_validate(
            _review(severity=severity, open_questions=open_questions),
            context=_packet_context(tmp_path),
        )


def test_not_safe_requires_a_blocking_finding_or_open_question(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    schema = _load_canonical(monkeypatch)

    with pytest.raises(ValidationError, match="verdict must be SAFE"):
        schema.model_validate(
            _review(verdict="NOT-SAFE"),
            context=_packet_context(tmp_path),
        )
