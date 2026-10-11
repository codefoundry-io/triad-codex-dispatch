"""C18/C34: generated argv keeps opaque pins through actual wrapper parsers."""
import argparse
import importlib
import json
import sys

import pytest

import _common
import review_adapters_v2
import review_round_v2
from review_roster import resolve_roster
from test_v2_google_wrappers import route, ready
from test_v2_producer_adapter import verdict

PINS = ["--help", "--yolo", "--", "unknown-future-model", "model with spaces"]


def parser_loses_pin(pin):
    """Measure gh-109475 without requiring a particular patch release."""
    if pin != "--":
        return False
    parser = argparse.ArgumentParser()
    parser.add_argument("--model")
    parsed = parser.parse_args(["--model=--"]).model
    assert parsed == "--" or parsed == []
    return parsed == []


@pytest.mark.parametrize("provider", ["claude", "agy", "gemini"])
def test_C18_C34_malformed_parsed_model_refuses_before_io(provider, monkeypatch, capsys):
    """CPython gh-109475 returned [] for --model=-- before 3.12.2."""
    wrapper = importlib.import_module("antigravity_wrapper" if provider == "agy" else provider + "_wrapper")
    real_parse = argparse.ArgumentParser.parse_args

    def old_parser_result(parser, *args, **kwargs):
        parsed = real_parse(parser, *args, **kwargs)
        assert parsed.model == "ordinary-model"
        parsed.model = []
        return parsed

    def no_io(*args, **kwargs):
        pytest.fail("malformed model must refuse before prompt or provider I/O")

    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", old_parser_result)
    monkeypatch.setattr(_common, "load_prompt_text", no_io)
    if hasattr(wrapper, "load_prompt_text"):
        monkeypatch.setattr(wrapper, "load_prompt_text", no_io)
    monkeypatch.setattr(sys, "argv", [provider, "--prompt", "review", "--model=ordinary-model"])
    assert wrapper.main() == _common.EXIT_ARG_ERROR
    assert "model" in capsys.readouterr().err.lower()


@pytest.mark.parametrize("pin", [*PINS, None])
@pytest.mark.parametrize("provider", ["claude", "agy", "gemini"])
def test_C18_C34_generated_invocation_reaches_actual_wrapper_parser(provider, pin, tmp_path, monkeypatch):
    loses_pin = parser_loses_pin(pin)
    family = "claude" if provider == "claude" else "google"
    entry = dict(family=family, transport_route=provider, model=pin, effort=None,
                 cwd=str(tmp_path), timeout_s=600, binary="/unused/provider")
    command = review_round_v2._invocation(
        verdict(family=family, route=None if family == "claude" else provider), entry, tmp_path, "review")["argv"]
    wrapper = importlib.import_module("antigravity_wrapper" if provider == "agy" else provider + "_wrapper")
    real_parse = argparse.ArgumentParser.parse_args

    class Parsed(Exception):
        pass

    def parse_then_stop(parser, *args, **kwargs):
        parsed = real_parse(parser, *args, **kwargs)
        if loses_pin:
            assert parsed.model == []
            return parsed
        assert parsed.model == pin
        raise Parsed

    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", parse_then_stop)
    monkeypatch.setattr(sys, "argv", command[1:])
    if loses_pin:
        def no_io(*args, **kwargs):
            pytest.fail("lost pin must refuse before prompt or provider I/O")
        monkeypatch.setattr(_common, "load_prompt_text", no_io)
        if hasattr(wrapper, "load_prompt_text"):
            monkeypatch.setattr(wrapper, "load_prompt_text", no_io)
        assert wrapper.main() == _common.EXIT_ARG_ERROR
        return
    with pytest.raises(Parsed):
        wrapper.main()


@pytest.mark.parametrize("pin", PINS)
def test_C18_google_adapter_pin_survives_real_preflight_parser(route, pin, monkeypatch):
    loses_pin = parser_loses_pin(pin)
    roster = resolve_roster(route["home"])
    for entry in roster["legs"]:
        entry["enabled"] = entry["vendor"] == "google"
        if entry["enabled"]:
            entry["google"]["route"] = route["name"]
            entry[route["name"]]["model"] = pin
    monkeypatch.setattr(review_adapters_v2, "resolve_binary",
                        lambda name: str(route["home"] / name) if name == route["name"] else None)

    def probe(argv, **kwargs):
        rc, output, error = route["invoke"](base=argv[2:])
        if loses_pin:
            assert rc == _common.EXIT_ARG_ERROR and output == ""
            assert "model" in error.lower() and route["calls"] == []
            raise ValueError("host parser did not preserve the model")
        assert rc == 0, error
        assert json.loads(output)["model"] == pin
        assert route["calls"] == []
        return output

    monkeypatch.setattr(review_adapters_v2, "probe", probe)
    def prepare():
        return review_adapters_v2.prepare_adapters(
            roster, review_id="round-2", cwd=route["home"], authentication_class="gemini-enterprise",
            native_capabilities={}, receipt_root=route["home"] / "bridge", attempt=2)
    if loses_pin:
        with pytest.raises(ValueError, match="model"):
            prepare()
        assert route["calls"] == []
        return
    result = prepare()
    assert next(iter(result.values()))["model"] == pin


@pytest.mark.parametrize("pin", PINS)
def test_C18_google_dispatch_preserves_opaque_pin_and_bound_route_args(route, pin):
    route["model"] = pin
    offset = route["options"].index("--model")
    route["options"][offset:offset+2] = ["--model=" + pin]
    if parser_loses_pin(pin):
        rc, output, error = route["invoke"](["--preflight-only"])
        assert rc == _common.EXIT_ARG_ERROR and output == ""
        assert "model" in error.lower()
        assert route["calls"] == [] and route["guards"] == []
        return
    options, receipt = ready(route)
    rc, output, error = route["invoke"](base=options)
    assert rc == 0, error
    assert len(route["calls"]) == 1
    cmd = route["calls"][0][0]
    # Actual vendor parsers were characterized separately; these assertions
    # protect our emitted boundary, without pretending a fake proves a model exists.
    encoded = "--model=" + pin
    if route["name"] == "agy" and not pin.startswith("-"):
        assert cmd[cmd.index("--model") + 1] == pin
        start = cmd.index("--model")
    else:
        assert encoded in cmd
        start = cmd.index(encoded)
    assert "--yolo" not in cmd and "--help" not in cmd
    bound = json.loads(receipt.read_text())["route_args"]
    assert cmd[start:start+len(bound)] == bound
    assert json.loads(output)["route"] == route["name"]


@pytest.mark.parametrize("pin", PINS)
def test_C18_raw_gemini_transports_pin_without_formal_controls(pin, monkeypatch, capsys):
    import gemini_wrapper as wrapper
    calls = []
    monkeypatch.setattr(wrapper, "require_binary", lambda _: "/unused/gemini")
    monkeypatch.setattr(wrapper, "_probe_version", lambda *a: "0.63.0")
    monkeypatch.setattr(wrapper, "persist_result_artifacts", lambda *a, **kw: None)

    def run(cli, builder, prompt, **kwargs):
        calls.append(builder(prompt))
        return _common.RunResult(exit_code=0, vendor_exit_code=0, stdout='{"response":"ok"}', stderr="", elapsed_s=0)

    monkeypatch.setattr(wrapper, "run_cli_with_retry", run)
    monkeypatch.setattr(sys, "argv", ["gemini_wrapper", "--prompt", "test", "--model=" + pin])
    if parser_loses_pin(pin):
        assert wrapper.main() == _common.EXIT_ARG_ERROR
        output = capsys.readouterr()
        assert output.out == "" and "model" in output.err.lower() and calls == []
        return
    assert wrapper.main() == 0
    assert len(calls) == 1 and "--model=" + pin in calls[0]
    assert "--approval-mode" not in calls[0] and "--policy" not in calls[0]
