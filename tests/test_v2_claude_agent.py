"""A selected CLI agent is passed as one argument without weakening the plan route."""
from test_v2_claude_wrapper import invoke
import _common


def test_selected_v2_claude_agent_reaches_native_argv_and_keeps_plan_mode(invoke):
    rc, _, _, calls, _, _ = invoke(extra=["--agent", "Plan"])
    assert rc == 0
    cmd = calls[0][1]
    assert cmd[cmd.index("--agent") + 1] == "Plan"
    assert cmd[cmd.index("--permission-mode") + 1] == "plan"


def test_blank_agent_is_refused_before_binary_resolution(invoke):
    rc, _, _, calls, resolutions, _ = invoke(extra=["--agent", " "])
    assert rc == _common.EXIT_ARG_ERROR and calls == resolutions == []


def test_legacy_gate_does_not_accept_new_agent_control(invoke):
    rc, _, _, calls, resolutions, _ = invoke(
        replace={"--pydantic": "verdict_schema:LegVerdict", "--effort": "xhigh"},
        omit=["--expected-leg-name", "--expected-attempt", "--expected-route"],
        extra=["--agent", "Plan"])
    assert rc == _common.EXIT_ARG_ERROR and calls == resolutions == []
