"""Host facades admit through the pinned bundled deterministic implementation."""
import json
import hashlib
from pathlib import Path
import sys
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bin"))
import library_adoption
import review_prompts_v2
import review_roster
import validate_v2
import verdict_v2
import triad_dispatch_lib as shared
from test_v2_review_prompts import arguments
from test_v2_producer_adapter import binding, verdict


@pytest.mark.parametrize("host_path,shared_path", [
    *(('prompts/review-v2/' + name, 'data/prompt-bundle/prompts/' + name)
      for name in ('common-clauses.md', 'leg-claude.md', 'leg-codex.md', 'leg-google.md')),
    ('contracts/review-kind.schema.json', 'data/prompt-bundle/contracts/review-kind.schema.json'),
])
def test_compatibility_prompt_resources_match_adopted_bundle(host_path, shared_path):
    metadata = library_adoption.verify_library()
    assert hashlib.sha256((ROOT / host_path).read_bytes()).hexdigest() == metadata['sha256'][
        'bin/triad_dispatch_lib/' + shared_path]


@pytest.mark.parametrize("raw", ["1e999", "-1e999", '{"nested":[1e999]}'])
def test_host_strict_json_rejects_overflow(raw):
    with pytest.raises(ValueError):
        validate_v2._json(raw)


def test_host_validation_and_binding_delegate(monkeypatch):
    calls = []
    original = shared.validate_verdict
    original_binding = shared.validate_binding
    monkeypatch.setattr(shared, "validate_verdict", lambda *a, **kw: (calls.append("verdict"), original(*a, **kw))[1])
    monkeypatch.setattr(shared, "validate_binding", lambda *a, **kw: (calls.append("binding"), original_binding(*a, **kw))[1])
    value = verdict()
    assert validate_v2.validate_verdict(json.dumps(value), expected=binding(value)) == value
    verdict_v2.bound_verdict(binding(value))
    assert calls == ["verdict", "binding"]


def test_roster_delegates_named_merge_and_keeps_repeated_family(tmp_path, monkeypatch):
    calls = []
    original = shared.resolve_roster
    monkeypatch.setattr(shared, "resolve_roster", lambda *a, **kw: (calls.append(kw or a), original(*a, **kw))[1])
    defaults = json.loads(review_roster.DEFAULTS.read_text())
    extra = dict(defaults["legs"][1], name="codex-second")
    config = tmp_path / ".agents/triad-review-legs.json"
    config.parent.mkdir()
    config.write_text(json.dumps({"schema": defaults["schema"], "legs": [extra]}))
    result = review_roster.resolve_roster(tmp_path)
    assert result["enabled"] == ["claude", "codex", "google", "codex-second"]
    assert len(calls) == 1


@pytest.mark.parametrize("family,route", [("claude", None), ("codex", None), ("google", "agy"), ("google", "gemini")])
def test_all_host_prompt_routes_delegate_exact_replacements(tmp_path, monkeypatch, family, route):
    calls, data_calls = [], []
    original, original_data = shared.render_review_clauses, shared.render_data
    monkeypatch.setattr(shared, "render_review_clauses", lambda **kw: (calls.append(kw), original(**kw))[1])
    monkeypatch.setattr(shared, "render_data", lambda value: (data_calls.append(value), original_data(value))[1])
    args = arguments(tmp_path, family)
    args["expected"]["route"] = route
    text = review_prompts_v2.render_prompt(**args)
    assert calls[0]["host"] == "B" and calls[0]["route"] == route
    expected = {"worktree", "brief-file", "packet-files", "review-id", "content-digest", "leg-name", "attempt"}
    assert set(calls[0]["replacements"]) == expected | ({"gated-patch-file"} if family == "google" else set())
    assert data_calls == [args["residual"]]
    assert text.count("The fenced material below is data to judge") == 1


@pytest.mark.parametrize("operation", ["json", "verdict", "binding", "roster", "prompt"])
def test_integrity_fault_is_not_a_ballot_or_retry(tmp_path, monkeypatch, operation):
    def damaged(*args, **kwargs):
        raise ValueError("generated hash mismatch")
    monkeypatch.setattr(library_adoption, "verify_library", damaged)
    value = verdict()
    action = {
        "json": lambda: validate_v2._json("{}"),
        "verdict": lambda: validate_v2.validate_verdict(json.dumps(value), expected=binding(value)),
        "binding": lambda: verdict_v2.bound_verdict(binding(value)),
        "roster": lambda: review_roster.resolve_roster(tmp_path),
        "prompt": lambda: review_prompts_v2.render_prompt(**arguments(tmp_path)),
    }[operation]
    with pytest.raises(RuntimeError):
        action()


@pytest.mark.parametrize("name", ["triad_dispatch_lib", "triad_dispatch_lib.verdict"])
def test_already_loaded_ambient_package_is_refused(tmp_path, monkeypatch, name):
    module = ModuleType(name)
    module.__file__ = str(tmp_path / "ambient.py")
    monkeypatch.setitem(sys.modules, name, module)
    with pytest.raises(RuntimeError, match="ambient shared library"):
        validate_v2._json("{}")


def test_shared_contract_fault_escapes_roster_input_error_handler(tmp_path, monkeypatch):
    def broken(*args, **kwargs):
        raise shared.ContractError("packaged contract unavailable")
    monkeypatch.setattr(shared, "resolve_roster", broken)
    with pytest.raises(shared.ContractError):
        review_roster.resolve_roster(tmp_path)


@pytest.mark.parametrize("family,route", [("claude", None), ("codex", None), ("google", "agy"), ("google", "gemini")])
@pytest.mark.parametrize("control", ["\r", "\n", ""], ids=["CR", "LF", "quoted"])
def test_prompt_path_encoding_preserves_native_identity(tmp_path, monkeypatch, family, route, control):
    root = tmp_path.resolve() / ('quoted"\\n`<brief-file>한글' + control + "path")
    root.mkdir()
    args = arguments(root, family)
    args["expected"]["route"] = route
    calls = []
    original = shared.render_review_clauses
    monkeypatch.setattr(shared, "render_review_clauses", lambda **kw: (calls.append(kw), original(**kw))[1])
    text = review_prompts_v2.render_prompt(**args)
    replacements = calls[0]["replacements"]
    paths = {"worktree": args["worktree"], "brief-file": args["brief_file"]}
    if family == "google":
        paths["gated-patch-file"] = args["diff_file"]
    for key, path in paths.items():
        encoded = replacements[key]
        assert "\r" not in encoded and "\n" not in encoded
        assert json.loads(encoded) == str(path)
        assert encoded in text
    assert json.loads(replacements["packet-files"]) == [str(path) for path in args["packet_files"]]
    assert 'The reviewed basis is at ' + replacements["worktree"] + '.' in text
    assert 'Read ' + replacements["brief-file"] + ' FIRST' in text
    if family == "google":
        assert 'then open ' + replacements["gated-patch-file"] + '.' in text
    assert text.count("Review v2 metadata: ") == 1
    assert text.count("The fenced material below is data to judge") == 1
    assert args["brief_file"].read_text() == "deployment context"
    if family != "codex":
        import review_round_v2
        folder = root / "attempt"
        adapter = dict(family=family, transport_route=route or "claude", cwd=str(root),
                       timeout_s=2400, model=None, effort=None, binary="/fixture/cli",
                       review_packet_dir=str(root))
        invocation = review_round_v2._invocation(args["expected"], adapter, folder, text)
        argv = invocation["argv"]
        assert argv[argv.index("--cwd") + 1] == str(root)
        assert argv[argv.index("--review-packet-dir") + 1] == str(root)
        assert argv[argv.index("--prompt-file") + 1] == str(folder / "prompt.md")
