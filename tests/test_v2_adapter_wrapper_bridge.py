"""The adapter's actual argv passes each existing Google wrapper's parser."""
from test_v2_google_wrappers import route
from review_roster import resolve_roster
import review_adapters_v2


def test_real_google_wrapper_consumes_adapter_preflight_without_inference(route, monkeypatch):
    roster = resolve_roster(route["home"])
    for entry in roster["legs"]:
        entry["enabled"] = entry["vendor"] == "google"
        if entry["enabled"]:
            entry["name"] = "google-second"
            entry["google"]["route"] = route["name"]
            entry["timeout_s"] = 610
    monkeypatch.setattr(review_adapters_v2, "resolve_binary",
                        lambda name: str(route["home"] / name) if name == route["name"] else None)

    def wrapper(argv, *, cwd, env=None):
        assert "--preflight-only" in argv
        rc, output, error = route["invoke"](base=argv[2:])
        assert rc == 0, error
        assert route["calls"] == []
        return output

    monkeypatch.setattr(review_adapters_v2, "probe", wrapper)
    result = review_adapters_v2.prepare_adapters(
        roster, review_id="round-2", cwd=route["home"], authentication_class="gemini-enterprise",
        native_capabilities={}, receipt_root=route["home"] / "bridge", attempt=2)
    assert result["google-second"]["cli_version"] == ("1.2.7" if route["name"] == "agy" else "0.60.0")
    assert route["calls"] == []
