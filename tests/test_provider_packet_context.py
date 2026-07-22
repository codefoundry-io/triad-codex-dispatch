from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))

import _common  # noqa: E402
import claude_wrapper  # noqa: E402
import gemini_wrapper  # noqa: E402


CONTEXT_KEYS = frozenset(
    {"sealed_packet_root", "expected_packet_sha256"}
)
WRAPPERS = (claude_wrapper, gemini_wrapper)


class _ContextSchema:
    required_validation_context = CONTEXT_KEYS

    @classmethod
    def verify_sealed_packet(cls, _context) -> None:
        return None


class _PlainSchema:
    pass


def _write_sealed_packet(tmp_path: Path, review_id: str = "review-r4") -> tuple[Path, str]:
    packet = tmp_path / review_id / "packet"
    packet.mkdir(parents=True)
    source = packet / "inputs" / "candidate" / "evidence.txt"
    source.parent.mkdir(parents=True)
    source.write_text("sealed evidence\n", encoding="utf-8")
    input_manifest = (
        f"{hashlib.sha256(source.read_bytes()).hexdigest()}  "
        "inputs/candidate/evidence.txt\n"
    ).encode()
    (packet / "INPUT_SHA256SUMS").write_bytes(input_manifest)
    sums = (
        f"{hashlib.sha256(source.read_bytes()).hexdigest()}  "
        "inputs/candidate/evidence.txt\n"
        f"{hashlib.sha256(input_manifest).hexdigest()}  INPUT_SHA256SUMS\n"
    ).encode()
    (packet / "SHA256SUMS").write_bytes(sums)
    digest = hashlib.sha256(sums).hexdigest()
    (packet / "PACKET_SHA256").write_text(f"{digest}\n", encoding="ascii")
    return packet, digest


def _run_wrapper(
    wrapper,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    schema,
    *context_args: str,
) -> tuple[int, dict[str, object], int]:
    captured: dict[str, object] = {}
    binary_calls = 0

    def fake_binary(_name: str) -> str:
        nonlocal binary_calls
        binary_calls += 1
        return "/usr/bin/provider"

    def fake_driver(*_args, **kwargs):
        captured.update(kwargs)
        return _common.RunResult(
            _common.EXIT_OK,
            "",
            "",
            0.0,
            final_answer="ok",
        )

    monkeypatch.delenv("TRIAD_CLAUDE_ENFORCE_SANDBOX", raising=False)
    if hasattr(wrapper, "_wrapper_hardened"):
        monkeypatch.setattr(wrapper, "_wrapper_hardened", lambda: False)
    monkeypatch.setattr(wrapper, "load_pydantic_class", lambda _spec: schema)
    monkeypatch.setattr(wrapper, "require_binary", fake_binary)
    monkeypatch.setattr(wrapper, "run_cli_with_retry", fake_driver)
    monkeypatch.setattr(wrapper, "persist_result_artifacts", lambda *_a, **_k: None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            f"{wrapper.__name__}.py",
            "--prompt",
            "review",
            "--pydantic",
            "ledger:Review",
            *context_args,
        ],
    )

    return wrapper.main(), captured, binary_calls


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_provider_wrappers_propagate_exact_sealed_validation_context(
    wrapper, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    packet, digest = _write_sealed_packet(tmp_path)

    rc, captured, binary_calls = _run_wrapper(
        wrapper,
        monkeypatch,
        tmp_path,
        _ContextSchema,
        "--sealed-packet-root",
        str(packet),
        "--expected-packet-sha256",
        digest,
    )

    assert rc == _common.EXIT_OK
    assert binary_calls == 1
    assert captured["validation_context"] == {
        "sealed_packet_root": str(packet.resolve()),
        "expected_packet_sha256": digest,
    }


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize(
    "packet_state",
    [
        "valid",
        "tampered-manifest",
        "tampered-input",
        "replaced-input-manifest",
        "unlisted-file",
        "wrong-digest",
    ],
)
def test_provider_wrappers_verify_sealed_packet_before_resolution(
    wrapper, packet_state: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    packet, digest = _write_sealed_packet(tmp_path)
    schema = _common.load_pydantic_class("triad_formal_review_schema:FormalReview")
    if packet_state == "tampered-manifest":
        (packet / "SHA256SUMS").write_text("tampered\n", encoding="utf-8")
    elif packet_state == "tampered-input":
        (packet / "inputs" / "candidate" / "evidence.txt").write_text(
            "tampered evidence\n", encoding="utf-8"
        )
    elif packet_state == "replaced-input-manifest":
        source = packet / "inputs" / "candidate" / "evidence.txt"
        sums = (
            f"{hashlib.sha256(source.read_bytes()).hexdigest()}  "
            "inputs/candidate/evidence.txt\n"
        ).encode()
        (packet / "SHA256SUMS").write_bytes(sums)
        digest = hashlib.sha256(sums).hexdigest()
        (packet / "PACKET_SHA256").write_text(f"{digest}\n", encoding="ascii")
        injected = packet / "inputs" / "injected" / "evidence.txt"
        injected.parent.mkdir(parents=True)
        injected.write_text("injected evidence\n", encoding="utf-8")
        (packet / "INPUT_SHA256SUMS").write_text(
            f"{hashlib.sha256(injected.read_bytes()).hexdigest()}  "
            "inputs/injected/evidence.txt\n",
            encoding="utf-8",
        )
    elif packet_state == "unlisted-file":
        (packet / "unlisted.txt").write_text(
            "not bound by either manifest\n", encoding="utf-8"
        )
    elif packet_state == "wrong-digest":
        digest = "0" * 64

    rc, _captured, binary_calls = _run_wrapper(
        wrapper,
        monkeypatch,
        tmp_path,
        schema,
        "--sealed-packet-root",
        str(packet),
        "--expected-packet-sha256",
        digest,
    )

    assert rc == (
        _common.EXIT_OK if packet_state == "valid" else _common.EXIT_ARG_ERROR
    )
    assert binary_calls == (1 if packet_state == "valid" else 0)


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_provider_wrappers_keep_non_context_custom_schemas_working(
    wrapper, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    rc, captured, binary_calls = _run_wrapper(
        wrapper, monkeypatch, tmp_path, _PlainSchema
    )

    assert rc == _common.EXIT_OK
    assert binary_calls == 1
    assert captured["validation_context"] is None


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize(
    ("schema", "context_args"),
    [
        pytest.param(_ContextSchema, (), id="required-context-absent"),
        pytest.param(
            type(
                "PartialSchema",
                (),
                {"required_validation_context": {"sealed_packet_root"}},
            ),
            (
                "--sealed-packet-root",
                "{packet}",
                "--expected-packet-sha256",
                "a" * 64,
            ),
            id="partial-schema-contract",
        ),
        pytest.param(
            type(
                "ExtraSchema",
                (),
                {"required_validation_context": CONTEXT_KEYS | {"review_id"}},
            ),
            (),
            id="unsupported-schema-context",
        ),
        pytest.param(
            type(
                "MalformedSchema",
                (),
                {"required_validation_context": ["sealed_packet_root"]},
            ),
            (),
            id="malformed-schema-context",
        ),
        pytest.param(
            _ContextSchema,
            ("--sealed-packet-root", "{packet}"),
            id="missing-digest-flag",
        ),
        pytest.param(
            _ContextSchema,
            ("--expected-packet-sha256", "a" * 64),
            id="missing-root-flag",
        ),
        pytest.param(
            _ContextSchema,
            (
                "--sealed-packet-root",
                "{packet}",
                "--expected-packet-sha256",
                "A" * 64,
            ),
            id="malformed-digest",
        ),
        pytest.param(
            _ContextSchema,
            (
                "--sealed-packet-root",
                "relative/review-r3/packet",
                "--expected-packet-sha256",
                "a" * 64,
            ),
            id="relative-packet-root",
        ),
        pytest.param(
            _ContextSchema,
            (
                "--sealed-packet-root",
                "{review_root}",
                "--expected-packet-sha256",
                "a" * 64,
            ),
            id="noncanonical-packet-root",
        ),
    ],
)
def test_provider_wrappers_reject_bad_context_before_provider_resolution(
    wrapper,
    schema,
    context_args: tuple[str, ...],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    packet = tmp_path / "review-r3" / "packet"
    packet.mkdir(parents=True)
    rendered_args = tuple(
        (
            str(packet)
            if item == "{packet}"
            else str(packet.parent)
            if item == "{review_root}"
            else item
        )
        for item in context_args
    )

    rc, captured, binary_calls = _run_wrapper(
        wrapper,
        monkeypatch,
        tmp_path,
        schema,
        *rendered_args,
    )

    assert rc == _common.EXIT_ARG_ERROR
    assert binary_calls == 0
    assert captured == {}


def test_generic_sealed_context_returns_schema_failure_without_hidden_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contexts: list[object] = []
    attempts = 0

    def fake_run_once(*_args, **_kwargs):
        nonlocal attempts
        attempts += 1
        return _common.RunResult(
            _common.EXIT_OK,
            f"answer-{attempts}",
            "",
            0.0,
        )

    def fake_validate(_answer, _schema, *, context=None):
        contexts.append(context)
        return False, "identity mismatch"

    context = {
        "sealed_packet_root": "/absolute/review-r3/packet",
        "expected_packet_sha256": "b" * 64,
    }
    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(
        _common, "inject_schema_to_prompt", lambda prompt, _schema: prompt
    )
    monkeypatch.setattr(_common, "_run_once", fake_run_once)
    monkeypatch.setattr(
        _common,
        "extract_gemini_answer",
        lambda stdout, _stderr: (stdout, None),
    )
    monkeypatch.setattr(_common, "validate_response", fake_validate)

    result = _common.run_cli_with_retry(
        "gemini",
        lambda prompt: ["gemini", "-p", prompt],
        "review",
        cwd=None,
        timeout=30,
        pydantic_cls=_ContextSchema,
        validation_context=context,
    )

    assert result.classification == "schema-fail"
    assert result.schema_repair_attempt == 0
    assert contexts == [context]
    assert contexts[0] is context


def test_generic_plain_schema_retains_one_schema_repair_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = 0

    def fake_run_once(*_args, **_kwargs):
        nonlocal attempts
        attempts += 1
        return _common.RunResult(_common.EXIT_OK, f"answer-{attempts}", "", 0.0)

    def fake_validate(_answer, _schema, *, context=None):
        assert context is None
        if attempts == 1:
            return False, "ordinary schema mismatch"
        return True, {"verdict": "SAFE"}

    monkeypatch.setattr(_common, "prune_stale_run_logs", lambda _cli: None)
    monkeypatch.setattr(_common, "inject_schema_to_prompt", lambda prompt, _schema: prompt)
    monkeypatch.setattr(_common, "_run_once", fake_run_once)
    monkeypatch.setattr(_common, "extract_gemini_answer", lambda stdout, _stderr: (stdout, None))
    monkeypatch.setattr(_common, "validate_response", fake_validate)

    result = _common.run_cli_with_retry(
        "gemini",
        lambda prompt: ["gemini", "-p", prompt],
        "review",
        cwd=None,
        timeout=30,
        pydantic_cls=_PlainSchema,
    )

    assert result.validated == {"verdict": "SAFE"}
    assert result.schema_repair_attempt == 1
