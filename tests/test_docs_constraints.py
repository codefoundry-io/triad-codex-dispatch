import re
import subprocess
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_READMES = ("README.md", "README.ko.md")
DETAILED_SETUP_DOCS = (
    "migration/COMPANY-SETUP.md",
    "migration/COMPANY-SETUP.ko.md",
)
SETUP_DOCS = PUBLIC_READMES + DETAILED_SETUP_DOCS


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
    text = (ROOT / "skills/triad-cross-family-review/SKILL.md").read_text(encoding="utf-8")
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
    text = (ROOT / "skills/triad-gemini-dispatch/SKILL.md").read_text(encoding="utf-8")
    assert "approval-mode default|auto_edit" in text
    assert "--approval-mode plan" in text
    assert "[--approval-mode default|auto_edit|plan|yolo]" not in text
    assert "[--approval-mode default|auto_edit]" in text
    assert "plan/yolo" in text.lower()


def test_distribution_repo_does_not_ship_duplicate_repo_local_skills():
    tracked = [path.relative_to(ROOT).as_posix() for path in _tracked_files()]
    assert not [path for path in tracked if path.startswith(".agents/skills/")]
    manifest = (ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
    assert '"skills": "./skills/"' in manifest


def test_distribution_docs_name_all_user_home_write_targets():
    for rel in SETUP_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "$CODEX_HOME/agents" in text
        assert "~/.codex/agents" in text
        assert "~/.config/triad-codex-dispatch" in text
        assert "~/.local/bin" in text


def test_public_readmes_are_split_public_and_user_facing():
    en = (ROOT / "README.md").read_text(encoding="utf-8")
    ko = (ROOT / "README.ko.md").read_text(encoding="utf-8")

    assert "[한국어 README](README.ko.md)" in en
    assert "[English README](README.md)" in ko
    assert len(en.splitlines()) <= 220
    assert len(ko.splitlines()) <= 220

    for text in (en, ko):
        assert "https://github.com/codefoundry-io/triad-codex-dispatch" in text
        assert "codex plugin marketplace add codefoundry-io/triad-codex-dispatch --ref main" in text
        assert "codex plugin add triad-codex-dispatch@triad-codex-dispatch --json" in text
        assert "jq -r '.installedPath'" in text
        assert '"$TRIAD_PLUGIN_DIR/scripts/bootstrap.sh" --check' in text
        assert "codex plugin marketplace upgrade triad-codex-dispatch" in text
        assert "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1" in text
        assert "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1" in text
        assert "TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never" in text
        assert "codex --profile triad-codex-dispatch --search" in text
        assert "git clone" not in text
        assert "git pull" not in text
        assert "codex plugin marketplace add ." not in text
        assert "`codex`" in text
        assert "`claude`" in text
        assert "`agy`" in text
        assert "OAuth login" in text
        assert "OS package" in text
        assert "CODEX_HOME" in text
        assert "TRIAD_BOOTSTRAP_BIN_DIR" in text
        assert "TRIAD_WRAPPER_ALLOWED_ROOTS" in text
        assert "skills.config" in text
        assert "public" in text.lower()
        assert "COMPANY-SETUP" not in text
        assert "<internal" not in text
        assert "com.company" not in text
        assert "사내" not in text
        assert "Internal Git marketplace" not in text


def test_install_docs_state_auth_assumption_and_target_choices():
    for rel in DETAILED_SETUP_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "OAuth logged" in text or "OAuth login" in text
        assert "`codex`, `claude`, and `agy`" in text or "`codex`, `claude`, `agy`" in text
        assert "does not perform OAuth/login" in text or "OAuth/login 설정을 대신하지" in text
        assert "User-home install is the default and recommended path" in text or "사용자 홈 설치가 기본이자 권장 경로" in text
        assert "Workspace-contained install is advanced only" in text or "workspace-contained 설치는 advanced 옵션" in text
        assert "logged-in folder-scoped `CODEX_HOME`" in text or "이미 로그인된" in text
        compact = " ".join(text.split())
        assert "`CODEX_HOME`, `XDG_CONFIG_HOME`, `TRIAD_BOOTSTRAP_BIN_DIR`, and `PATH`" in compact or "`CODEX_HOME`, `XDG_CONFIG_HOME`, `TRIAD_BOOTSTRAP_BIN_DIR`, `PATH`" in compact
        assert "codex plugin marketplace add" in text
        assert "codex plugin add" in text
        assert "classifier patches" in text or "classifier patch" in text
        assert ".triad-codex-home/" in text
        assert ".triad-config/" in text
        assert ".triad-bin/" in text

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".triad-codex-home/" in gitignore
    assert ".triad-config/" in gitignore
    assert ".triad-bin/" in gitignore


def test_readme_remove_docs_cover_default_and_workspace_targets():
    expected = [
        "codex plugin remove triad-codex-dispatch@triad-codex-dispatch",
        "codex plugin marketplace remove triad-codex-dispatch",
        "~/.codex/agents/claude-wrapper-repair.toml",
        "~/.codex/agents/gemini-wrapper-repair.toml",
        "~/.codex/agents/agy-wrapper-repair.toml",
        "~/.codex/triad-codex-dispatch.config.toml",
        "~/.codex/rules/triad-codex-dispatch.rules",
        "~/.local/bin/claude_wrapper.py",
        "~/.local/bin/gemini_wrapper.py",
        "~/.local/bin/antigravity_wrapper.py",
        "~/.config/triad-codex-dispatch",
        "TRIAD_BOOTSTRAP_BIN_DIR",
        "CODEX_HOME",
    ]

    en = (ROOT / "README.md").read_text(encoding="utf-8")
    ko = (ROOT / "README.ko.md").read_text(encoding="utf-8")
    assert "Default user-home removal" in en
    assert "기본 user-home 설치 삭제" in ko
    for text in (en, ko):
        for phrase in expected:
            assert phrase in text

    for rel in DETAILED_SETUP_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "XDG_CONFIG_HOME" in text
        assert ".triad-codex-home/" in text
        assert ".triad-config/" in text
        assert ".triad-bin/" in text


def test_distribution_docs_explain_bootstrap_pinned_paths():
    for rel in DETAILED_SETUP_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "TRIAD_CLASSIFIER_EXTENSION" in text
        assert "bootstrap" in text
        assert "pinned" in text or "고정" in text
        assert "checkout" in text
        assert "absolute checkout path" in " ".join(text.split())


def test_distribution_docs_document_bounded_runtime_artifacts():
    for rel in DETAILED_SETUP_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "bin/_logs/<cli>/" in text
        assert "100" in text
        assert "20 MB" in text
        assert "10 MB" in text
        assert "audit.jsonl" in text


def test_distribution_docs_use_codex_specific_profile_name():
    forbidden = "triad-dispatch.config.toml"
    for rel in SETUP_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert forbidden not in text


def test_runtime_convenience_profile_keeps_install_targets_read_only():
    for rel in DETAILED_SETUP_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "/Users/YOUR_USER" not in text
        assert "YOUR_USER" not in text
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
            and "/absolute/home/path/.config/triad-codex-dispatch" in body
        ]
        assert matching, f"runtime profile block not found in {rel}"
        body = matching[0]
        assert "~/.local/bin" not in body
        assert "~/.codex/agents" not in body
        assert "~/.config/triad-codex-dispatch" not in body
        assert "/absolute/home/path/.config/triad-codex-dispatch" in body
        assert "do not rely on shell expansion inside TOML" in text or "TOML 안의 shell expansion에 의존하지" in text
        assert "/path/to/triad-codex-dispatch/bin/_logs" in body
        assert 'approval_policy = "on-request"' in body
        assert 'sandbox_mode = "workspace-write"' in body


def test_docs_use_bash_compatible_triad_entrypoint_snippets():
    for rel in SETUP_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "cat >> ~/.zshrc" not in text
        assert "source ~/.zshrc" not in text
        assert "TRIAD_SHELL_RC=\"${HOME}/.bashrc\"" in text
        assert "case \"${SHELL:-}\" in" in text
        assert "cat >> \"$TRIAD_SHELL_RC\" <<'EOF'" in text
        assert ". \"$TRIAD_SHELL_RC\"" in text


def test_repair_named_agents_use_scoped_permission_profile():
    for rel in [
        "agents/claude-wrapper-repair.toml",
        "agents/agy-wrapper-repair.toml",
        "agents/gemini-wrapper-repair.toml",
    ]:
        data = tomllib.loads((ROOT / rel).read_text(encoding="utf-8"))
        assert "sandbox_mode" not in data
        assert data["default_permissions"] == "triad_repair"
        assert "skills" not in data
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
        compact_instructions = " ".join(data["developer_instructions"].split())
        assert "NEVER invoke triad dispatch skills" in compact_instructions
        assert "spawn another repair agent recursively" in compact_instructions
        if rel == "agents/agy-wrapper-repair.toml":
            assert "`--sandbox workspace-write`" in data["developer_instructions"]
            assert "`--sandbox=workspace-write`" in data["developer_instructions"]
            assert "replace that value with `read-only`" in data["developer_instructions"]

    for rel in [
        *DETAILED_SETUP_DOCS,
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
    for rel in DETAILED_SETUP_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "$CODEX_HOME/<name>.config.toml" in text
        assert "top-level" in text
        assert "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1" in text
        assert "TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never" in text
        assert "external-CLI consent" in text or "external-CLI 동의" in text
        assert "refusing to overwrite" in text or "덮어쓰지" in text


def test_docs_explain_user_layer_command_rules_install():
    for rel in DETAILED_SETUP_DOCS:
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
        assert "developers.openai.com/codex/concepts/sandboxing" in text
        assert "Bootstrap does not install OS packages" in text or "Bootstrap은 OS package를 설치하지" in text
        assert "command codex --profile triad-codex-dispatch --search" in text
        assert "Existing Codex sessions must be restarted" in text or "기존 Codex session을 재시작" in text
        assert "skills.config" in text
        assert "custom-agent" in text or "custom agent" in text or "custom repair agent" in text
        assert 'path = "/path/to/triad-codex-dispatch/skills/triad-claude-dispatch/SKILL.md"' in text or "triad-claude-dispatch/SKILL.md" in text
        assert "absolute-wrapper" in text
        assert "--prompt-file" in text
        assert "TRIAD_WRAPPER_ALLOWED_ROOTS" in text
        compact = " ".join(text.split())
        assert "process working directory" in compact
        assert "workspace-write dispatch works without extra env" in compact or "추가 env 없이 workspace-write dispatch" in compact
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


def test_docs_explain_pre_release_gate():
    for rel in DETAILED_SETUP_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "Pre-Release Gate" in text or "배포 전 Gate" in text
        assert "bash <<'TRIAD_RELEASE_GATE'" in text
        assert "set -euo pipefail" in text
        assert "release_base=\"${RELEASE_BASE:-origin/main}\"" in text
        assert "python3 -m pytest -q tests/ -p no:cacheprovider" in text
        assert "bash -n scripts/bootstrap.sh" in text
        assert "\ngit diff --check\n" in text
        assert "git diff --cached --check" in text
        assert "git diff --check \"$release_base\"...HEAD" in text
        assert "tmp_root=\"$(mktemp -d \"${TMPDIR:-/tmp}/triad-codex-dispatch-release-check.XXXXXX\")\"" in text
        assert "trap 'rm -rf \"$tmp_root\"' EXIT" in text
        assert "tmp_root=\"$(cd \"$tmp_root\" && pwd -P)\"" in text
        assert "mkdir -p \"$tmp_root/bin\"" in text
        assert 'case "$release_base" in' in text
        assert "origin/*) git fetch --prune origin ;;" in text
        assert "git rev-parse --verify -q \"$release_base^{commit}\"" in text
        assert "release base not found: $release_base; run git fetch or set RELEASE_BASE" in text
        assert "git status --short > \"$tmp_root/git-status.txt\"" in text
        assert "--untracked-files=no" not in text
        assert "if test -s \"$tmp_root/git-status.txt\"; then" in text
        assert "cat \"$tmp_root/git-status.txt\" >&2" in text
        assert "release gate requires a clean worktree, including untracked files" in text
        assert "TRIAD_RELEASE_GATE" in text
        assert "git fetch --prune origin" in text
        assert "TRIAD_BOOTSTRAP_SKIP_AUTH=1" in text
        assert "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1" in text
        assert "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1" in text
        assert "TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never" in text
        assert "TRIAD_BOOTSTRAP_BIN_DIR=\"$tmp_root/bin\"" in text
        assert "CODEX_HOME=\"$tmp_root/codex\"" in text
        assert "HOME=\"$tmp_root/home\"" in text
        assert "XDG_CONFIG_HOME=\"$tmp_root/config\"" in text
        assert "PATH=\"$tmp_root/bin:$PATH\"" in text
        assert "triad-cross-family-review" in text
        assert "Claude SAFE" in text or "Claude가 SAFE" in text
        assert "agy SAFE" in text or "agy가 SAFE" in text
        assert "fresh Codex SAFE" in text or "fresh Codex가 SAFE" in text
        assert "Do not push" in text or "push하지 않는다" in text


def test_git_marketplace_update_docs_readd_when_ref_changes():
    for rel in [
        *DETAILED_SETUP_DOCS,
        "docs/specs/2026-07-01-codex-led-triad-dispatch-design.md",
    ]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        compact = " ".join(text.split())
        assert "marketplace remove triad-codex-dispatch" in text
        assert (
            "marketplace add <internal-git-url-or-owner/repo> --ref <release-ref>"
            in compact
        )
        assert "git fetch --tags origin <release-ref>" in text
        assert "git checkout --detach FETCH_HEAD" in text
        assert "TRIAD_BOOTSTRAP_INSTALL_CODEX_PROFILE=1" in text
        assert "TRIAD_BOOTSTRAP_INSTALL_CODEX_RULES=1" in text
        assert "TRIAD_CODEX_PROFILE_APPROVAL_POLICY=never" in text
        assert "TRIAD_BOOTSTRAP_SKIP_AUTH=1 scripts/bootstrap.sh --check" not in text
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
