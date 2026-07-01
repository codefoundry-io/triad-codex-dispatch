import re
import subprocess
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def test_codex_leader_docs_do_not_shell_out_to_codex_exec():
    forbidden_patterns = [
        re.compile(r"\bcodex\s+exec(?:\s|$)"),
        re.compile(r"\bcodex\s+--search\s+exec(?:\s|$)"),
    ]
    offenders = []
    for path in _tracked_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if path.relative_to(ROOT) == Path("tests/test_docs_constraints.py"):
            continue
        for pattern in forbidden_patterns:
            if pattern.search(text):
                offenders.append(f"{path.relative_to(ROOT)}: {pattern.pattern}")

    assert offenders == []


def test_codex_wrapper_leg_is_documented_as_not_shipped():
    forbidden = [
        "Keep or drop `codex_wrapper.py`",
        "future `codex_wrapper.py`",
        "Codex CLI wrapper",
    ]
    offenders = []
    for path in _tracked_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if path.relative_to(ROOT) == Path("tests/test_docs_constraints.py"):
            continue
        for phrase in forbidden:
            if phrase in text:
                offenders.append(f"{path.relative_to(ROOT)}: {phrase}")

    assert offenders == []
    for rel in [
        "migration/COMPANY-SETUP.md",
        "migration/COMPANY-SETUP.ko.md",
        "docs/specs/2026-07-01-codex-led-triad-dispatch-design.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "spawn_agent" in text
        assert "fork_context=false" in text


def test_cross_family_review_uses_fresh_codex_subagent_only():
    skill_paths = [
        ROOT / ".agents/skills/triad-cross-family-review/SKILL.md",
        ROOT / "skills/triad-cross-family-review/SKILL.md",
    ]
    for path in skill_paths:
        text = path.read_text(encoding="utf-8")
        assert "spawn_agent" in text
        assert "wait_agent" in text
        assert "fork_context=false" in text
        assert "nested" not in text.lower()
        assert "--reasoning xhigh" in text
        assert "Gemini 3.1 Pro (High)" in text
        assert "TRIAD_GOOGLE_REVIEW_MODEL" in text
        assert "Do NOT run scripts/tests" in text
        assert "spawn subprocesses" in text
        assert "invoke vendor CLIs" in text
        assert "reason deeply/adversarially" in text


def test_gemini_dispatch_skills_do_not_offer_yolo_or_plan_modes():
    for rel in [
        ".agents/skills/triad-gemini-dispatch/SKILL.md",
        "skills/triad-gemini-dispatch/SKILL.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "approval-mode default|auto_edit" in text
        assert "--approval-mode plan" in text
        assert "[--approval-mode default|auto_edit|plan|yolo]" not in text
        assert "[--approval-mode default|auto_edit]" in text
        assert "plan/yolo" in text.lower()


def test_distribution_docs_name_all_user_home_write_targets():
    for rel in [
        "README.md",
        "migration/COMPANY-SETUP.md",
        "migration/COMPANY-SETUP.ko.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "~/.codex/agents" in text
        assert "~/.config/triad-codex-dispatch" in text
        assert "~/.local/bin" in text


def test_distribution_docs_explain_bootstrap_pinned_paths():
    for rel in [
        "README.md",
        "migration/COMPANY-SETUP.md",
        "migration/COMPANY-SETUP.ko.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "TRIAD_CLASSIFIER_EXTENSION" in text
        assert "bootstrap" in text
        assert "pinned" in text or "고정" in text
        assert "checkout" in text
        assert "absolute checkout path" in " ".join(text.split())


def test_distribution_docs_document_bounded_runtime_artifacts():
    for rel in [
        "README.md",
        "migration/COMPANY-SETUP.md",
        "migration/COMPANY-SETUP.ko.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "bin/_logs/<cli>/" in text
        assert "100" in text
        assert "20 MB" in text
        assert "10 MB" in text
        assert "audit.jsonl" in text


def test_distribution_docs_use_codex_specific_profile_name():
    forbidden = "triad-dispatch.config.toml"
    for rel in [
        "README.md",
        "migration/COMPANY-SETUP.md",
        "migration/COMPANY-SETUP.ko.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert forbidden not in text


def test_runtime_convenience_profile_keeps_install_targets_read_only():
    for rel in [
        "README.md",
        "migration/COMPANY-SETUP.md",
        "migration/COMPANY-SETUP.ko.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        blocks = []
        cursor = 0
        while True:
            start = text.find("```toml", cursor)
            if start == -1:
                break
            end = text.find("```", start + len("```toml"))
            assert end != -1
            blocks.append(text[start:end])
            cursor = end + len("```")

        matching = [
            body
            for body in blocks
            if "/path/to/triad-codex-dispatch/bin/_logs" in body
            and "/Users/YOUR_USER/.config/triad-codex-dispatch" in body
        ]
        assert matching, f"runtime profile block not found in {rel}"
        body = matching[0]
        assert "~/.local/bin" not in body
        assert "/Users/YOUR_USER/.local/bin" not in body
        assert "~/.codex/agents" not in body
        assert "/Users/YOUR_USER/.codex/agents" not in body
        assert "/Users/YOUR_USER/.config/triad-codex-dispatch" in body
        assert "/path/to/triad-codex-dispatch/bin/_logs" in body
        assert 'approval_policy = "on-request"' in body
        assert 'sandbox_mode = "workspace-write"' in body


def test_repair_named_agents_use_scoped_permission_profile():
    for rel in [
        "agents/claude-wrapper-repair.toml",
        "agents/agy-wrapper-repair.toml",
        "agents/gemini-wrapper-repair.toml",
    ]:
        data = tomllib.loads((ROOT / rel).read_text(encoding="utf-8"))
        assert "sandbox_mode" not in data
        assert data["default_permissions"] == "triad_repair"
        permissions = data["permissions"]["triad_repair"]
        fs = permissions["filesystem"]
        assert fs[":minimal"] == "read"
        assert fs["__TRIAD_REPO_ROOT__"] == "read"
        assert fs["__TRIAD_REPO_ROOT__/bin/_logs"] == "write"
        assert fs["__TRIAD_CLASSIFIER_DIR__"] == "write"
        assert fs["__TRIAD_PYTHON_READ_ROOTS__"] == "read"
        assert fs["__TRIAD_VENDOR_READ_ROOTS__"] == "read"
        assert ":workspace_roots" not in fs
        assert "workspace_roots" not in permissions
        assert permissions["network"]["enabled"] is True
        assert "subprocess.run(argv, shell=False" in data["developer_instructions"]
        assert 'cwd="__TRIAD_REPO_ROOT__"' in data["developer_instructions"]
        assert "original_args_after_argv0_normalized" in data["developer_instructions"]
        assert "REMOVE any original separated `--cwd <path>`" in data["developer_instructions"]
        assert "REMOVE any original equals-form `--cwd=<path>`" in data["developer_instructions"]
        assert "do not apply `shlex.quote` to argv items" in data["developer_instructions"]
        assert "shlex.quote" in data["developer_instructions"]
        if rel == "agents/agy-wrapper-repair.toml":
            assert "`--sandbox workspace-write`" in data["developer_instructions"]
            assert "`--sandbox=workspace-write`" in data["developer_instructions"]
            assert "replace that value with `read-only`" in data["developer_instructions"]

    for rel in [
        "README.md",
        "migration/COMPANY-SETUP.md",
        "migration/COMPANY-SETUP.ko.md",
        "migration/AGENTS.recommended.md",
        "docs/specs/2026-07-01-codex-led-triad-dispatch-design.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert 'default_permissions = "triad_repair"' in text

    evidence = (ROOT / "docs/references/codex-permission-profile-evidence.md").read_text(
        encoding="utf-8"
    )
    assert "default_permissions" in evidence
    assert ":minimal" in evidence
    assert "custom agents" in evidence
    assert "configuration layers" in evidence
    assert "Boundary" in evidence


def test_docs_explain_profile_file_layering():
    for rel in [
        "README.md",
        "migration/COMPANY-SETUP.md",
        "migration/COMPANY-SETUP.ko.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "$CODEX_HOME/<name>.config.toml" in text
        assert "top-level" in text
        assert "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1" in text
        assert "TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never" in text
        assert "external-CLI consent" in text or "external-CLI 동의" in text
        assert "refusing to overwrite" in text or "덮어쓰지" in text


def test_docs_explain_user_layer_command_rules_install():
    for rel in [
        "README.md",
        "migration/COMPANY-SETUP.md",
        "migration/COMPANY-SETUP.ko.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1" in text
        assert "TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never" in text
        assert "$CODEX_HOME/rules/triad-codex-dispatch.rules" in text
        assert "~/.codex/rules/triad-codex-dispatch.rules" in text
        assert "codex execpolicy check" in text
        assert "always run outside the sandbox" in text or "항상 sandbox 밖에서 실행" in text
        assert "codex-triad()" in text
        assert "Ubuntu 20.04" in text
        assert "~/.bashrc" in text
        assert "python3 >= 3.12" in text
        assert "bubblewrap" in text
        assert "command codex --profile triad-codex-dispatch --search" in text
        assert "Existing Codex sessions must be restarted" in text or "기존 Codex session을 재시작" in text
        assert "absolute-wrapper" in text
        assert "--prompt-file" in text
        assert "TRIAD_WRAPPER_ALLOWED_ROOTS" in text
        assert "write-attempt" in text or "write attempt" in text or "write-attempt" in text
        assert "Provider Sandbox Differences" in text or "Provider별 Sandbox 차이" in text
        assert "Gemini Policy Engine" in text
        assert "command substitution" in text or "substitution" in text
        assert "bash -lc" in text
        assert "zsh -lc" in text
        assert "unmanaged" in text
        assert "tenant guardian" in text

    rules = (ROOT / "migration/triad-codex-dispatch.rules").read_text(encoding="utf-8")
    assert "prefix_rule(" in rules
    assert 'decision = "allow"' in rules
    assert "/path/to/launcher-dir/claude_wrapper.py" in rules
    assert "/path/to/triad-codex-dispatch/bin/claude_wrapper.py" in rules
    assert "--prompt-file /path/to/workspace/_runs/prompts/triad-prompt.txt" in rules
    assert "bash -lc" in rules
    assert "zsh -lc" in rules
    assert 'pattern = [["claude_wrapper.py"' not in rules
    assert 'pattern = [["gemini_wrapper.py"' not in rules
    assert 'pattern = [["antigravity_wrapper.py"' not in rules
    assert 'pattern = ["python3"]' not in rules
    assert 'pattern = [["python3"]' not in rules
    assert 'pattern = [["/usr/bin/env"' not in rules
    assert 'pattern = [["env"' not in rules
    assert 'pattern = [["/path/to/triad-codex-dispatch/bin/claude_wrapper.py"' not in rules
    assert "python3 /path/to/triad-codex-dispatch/bin/gemini_wrapper.py" in rules


def test_git_marketplace_update_docs_readd_when_ref_changes():
    for rel in [
        "README.md",
        "migration/COMPANY-SETUP.md",
        "migration/COMPANY-SETUP.ko.md",
        "docs/specs/2026-07-01-codex-led-triad-dispatch-design.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        compact = " ".join(text.split())
        assert "marketplace remove triad-codex-dispatch-local" in text
        assert (
            "marketplace add <internal-git-url-or-owner/repo> --ref <release-ref>"
            in compact
        )
        assert "git fetch --tags origin <release-ref>" in text
        assert "git checkout --detach FETCH_HEAD" in text
        assert "does not change" in compact or "바꾸지 않는다" in compact
        assert "moving branch" in compact


def test_spike_d_docs_do_not_cite_unretained_negative_spawn_claim():
    forbidden = [
        "unknown agent_type",
        "plugin-shipped repair agents are proven not spawnable",
        "Spike D (DONE",
        "DO THIS FIRST (the one unproven mechanism)",
    ]
    offenders = []
    for path in _tracked_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if path.relative_to(ROOT) == Path("tests/test_docs_constraints.py"):
            continue
        for phrase in forbidden:
            if phrase in text:
                offenders.append(f"{path.relative_to(ROOT)}: {phrase}")

    assert offenders == []

    decision = (
        ROOT
        / "docs/references/spike-d-plugin-agent-distribution-decision.md"
    ).read_text(encoding="utf-8")
    assert "does **not** rely on plugin-shipped repair agent TOMLs" in decision
    assert "retained-evidence verified spawnable by name" in decision
