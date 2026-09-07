from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
SKILLS = ROOT / "skills"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_manifest_describes_the_convergent_distribution() -> None:
    manifest = json.loads(_text(MANIFEST))

    assert manifest["name"] == "triad-codex-dispatch"
    assert manifest["version"] == "0.2.553"
    assert manifest["skills"] == "./skills/"
    prompts = "\n".join(manifest["interface"]["defaultPrompt"])
    assert "triad-cross-family-review" in prompts
    assert "same complete focused directory" in prompts
    assert "batched-full-coverage" not in prompts


def test_current_release_heading_matches_manifest_and_readme_contract() -> None:
    version = json.loads(_text(MANIFEST))["version"]
    changelog = _text(ROOT / "CHANGELOG.md")
    readme = _text(ROOT / "README.md")
    readme_ko = _text(ROOT / "README.ko.md")

    assert f"## {version} — 2026-09-07" in changelog
    assert f"### Upgrading to {version}" in readme
    assert f"### {version} 업그레이드" in readme_ko
    assert f"_runs/distribution/{version}-final-r1" in readme
    assert f"_runs/distribution/{version}-final-r1" in readme_ko
    historical_en = readme.split("### Upgrading to 0.2.551", 1)[1].split(
        "### Upgrading to 0.2.550", 1
    )[0]
    historical_ko = readme_ko.split("### 0.2.551 업그레이드", 1)[1].split(
        "### 0.2.550 업그레이드", 1
    )[0]
    assert "1,800-second timeout" in historical_en
    assert "1,800초 timeout" in historical_ko
    assert "## 0.2.541 — 2026-08-20" in changelog
    assert "Formal review excludes `grep_search` because AGY 1.1.16" in changelog
    assert (
        "Post-completion `step_update` telemetry is diagnostic vendor output"
        in changelog
    )
    assert "Historical 0.2.541 behavior, superseded in 0.2.543" in changelog


def test_distribution_contains_only_the_four_public_skills() -> None:
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    assert [path.parent.name for path in skill_files] == [
        "triad-antigravity-dispatch",
        "triad-claude-dispatch",
        "triad-cross-family-review",
        "triad-gemini-dispatch",
    ]
    for path in skill_files:
        text = _text(path)
        assert text.startswith("---\n")
        assert f"name: {path.parent.name}\n" in text.split("---", 2)[1]
        assert len(text.splitlines()) <= 200


def test_cross_family_skill_entrypoint_has_a_bounded_instruction_budget() -> None:
    skill = _text(SKILLS / "triad-cross-family-review" / "SKILL.md")
    body = skill.split("---", 2)[2]

    assert len(body.splitlines()) <= 125
    assert len(body.split()) <= 1600


def test_gemini_agent_metadata_is_standalone_and_not_the_formal_leader() -> None:
    metadata = _text(SKILLS / "triad-gemini-dispatch" / "agents" / "openai.yaml")

    assert "Standalone Gemini CLI compatibility consult" in metadata
    assert "does not lead a formal Google-family review" in metadata
    assert (
        "cross-family review may select the packaged Gemini wrapper for Enterprise OAuth"
        in metadata
    )
    assert "Vertex, or API-key fallback" not in metadata
    assert "never after AGY has started" in metadata


def test_active_skill_links_resolve_inside_each_skill() -> None:
    for skill in SKILLS.glob("*/SKILL.md"):
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", _text(skill)):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (skill.parent / target.split("#", 1)[0]).resolve()
            assert resolved.is_file(), f"broken link from {skill}: {target}"


def test_cross_family_skill_has_one_round_unit_and_owner_design_gate() -> None:
    text = _text(SKILLS / "triad-cross-family-review" / "SKILL.md")
    convergence = _text(
        SKILLS / "triad-cross-family-review" / "references" / "convergence.md"
    )
    compact = " ".join(text.split())

    for leg in (
        "one Claude `LegVerdict`",
        "one Google `LegVerdict`",
        "one fresh Codex `LegVerdict`",
    ):
        assert leg in compact
    assert "OWNER_DECISION_REQUIRED" in text
    assert "There is no fixed round cap" in " ".join(convergence.split())
    assert "Batches, shards, and mixed-round evidence are not supported" in compact
    assert "fresh Codex process" in compact
    for owner_slot in (
        "Proposed delta:",
        "Evidence:",
        "Impact:",
        "Decision needed:",
    ):
        assert owner_slot in convergence
    assert "Preserve the affected source while awaiting that decision" in convergence


def test_formal_routes_are_explicit_and_reviewer_only() -> None:
    skill_root = SKILLS / "triad-cross-family-review"
    routing = " ".join(_text(skill_root / "references" / "reviewer-routing.md").split())
    legs = _text(skill_root / "references" / "leg-contracts.md")
    prompt_contract = " ".join(
        _text(skill_root / "references" / "review-prompt-contract.md").split()
    )

    for route_contract in (
        "Claude | `opus`, `xhigh`, 1,200-second wrapper deadline",
        "AGY 1.1.20 or newer, `gemini-3.1-pro-high`, `high`, 600-second wrapper deadline",
        "Gemini Enterprise OAuth with CLI Auto, requested Plan Mode, packaged read/search-only policy, and a 600-second wrapper deadline",
        'Fresh Codex | `gpt-5.6-terra`, `xhigh`, `fork_turns="none"`, default child rather than a registered reviewer agent, repeatable 1,200-second native observation waits',
    ):
        assert route_contract in routing

    for section in (
        "[Claude](#claude)",
        "[Google family](#google-family)",
        "[Fresh Codex](#fresh-codex)",
        "[Shared containment boundary](#shared-containment-boundary)",
    ):
        assert section in legs

    for command_contract in (
        'python3 "$toolkit_root/bin/claude_wrapper.py"',
        'python3 "$toolkit_root/bin/antigravity_wrapper.py"',
        'python3 "$toolkit_root/bin/gemini_wrapper.py"',
        'python3 "$toolkit_root/bin/verdict_schema.py" validate',
        '--expected-review-id "$review_id"',
        '--expected-content-digest "$review_digest"',
        "--pydantic verdict_schema:LegVerdict",
    ):
        assert command_contract in legs

    assert "`bin/review_round.py` is the canonical generator" in prompt_contract
    assert "`bin/verdict_schema.py` is the canonical validator" in prompt_contract
    assert "Evaluate every criterion" in prompt_contract
    assert "does not implement them or ask the leader how to proceed" in prompt_contract
    for provider_specific_detail in (
        "--permission-mode plan",
        "--approval-mode plan",
        "gemini-3.1-pro-high",
        "AGY native tool names",
    ):
        assert provider_specific_detail not in prompt_contract

    for standalone_skill in (
        SKILLS / "triad-claude-dispatch" / "SKILL.md",
        SKILLS / "triad-antigravity-dispatch" / "SKILL.md",
        SKILLS / "triad-gemini-dispatch" / "SKILL.md",
    ):
        assert "reviews only" in _text(standalone_skill)
    fenced_blocks = re.findall(r"```text\n(.*?)\n```", legs, re.DOTALL)

    def one_wrapper_block(wrapper: str, discriminator: str) -> str:
        matches = [
            block
            for block in fenced_blocks
            if f'python3 "$toolkit_root/bin/{wrapper}"' in block
            and discriminator in block
        ]
        assert len(matches) == 1
        return matches[0]

    provider_blocks = {
        "claude_wrapper.py": one_wrapper_block(
            "claude_wrapper.py", "--expected-family claude"
        ),
        "antigravity_wrapper.py": one_wrapper_block(
            "antigravity_wrapper.py", "--expected-family google"
        ),
        "gemini_wrapper.py": one_wrapper_block(
            "gemini_wrapper.py", "--expected-family google"
        ),
    }
    required_arguments = {
        "claude_wrapper.py": (
            '--prompt-file "$review_prompt_file"',
            '--cwd "$review_target_cwd"',
            "--model opus",
            "--effort xhigh",
            "--timeout 1200",
            "--pydantic verdict_schema:LegVerdict",
            '--expected-review-id "$review_id"',
            "--expected-family claude",
            '--expected-content-digest "$review_digest"',
            '> "$claude_result_file"',
        ),
        "antigravity_wrapper.py": (
            '--prompt-file "$review_prompt_file"',
            '--google-selector-receipt "$google_selector_receipt"',
            '--google-preflight-receipt "$google_preflight_file"',
            '--cwd "$review_target_cwd"',
            "--sandbox read-only",
            "--model gemini-3.1-pro-high",
            "--effort high",
            "--timeout 600",
            "--pydantic verdict_schema:LegVerdict",
            '--expected-review-id "$review_id"',
            "--expected-family google",
            '--expected-content-digest "$review_digest"',
            '> "$google_result_file"',
        ),
        "gemini_wrapper.py": (
            '--prompt-file "$review_prompt_file"',
            '--google-selector-receipt "$google_selector_receipt"',
            '--google-preflight-receipt "$google_preflight_file"',
            '--cwd "$review_target_cwd"',
            "--timeout 600",
            "--pydantic verdict_schema:LegVerdict",
            '--expected-review-id "$review_id"',
            "--expected-family google",
            '--expected-content-digest "$review_digest"',
            '> "$google_result_file"',
        ),
    }
    for wrapper, expected_arguments in required_arguments.items():
        block = provider_blocks[wrapper]
        assert block.startswith('TRIAD_DISPATCH_LOG_DIR="$review_log_dir"')
        for argument in expected_arguments:
            assert argument in block

    claude_block = provider_blocks["claude_wrapper.py"]
    for option in ("--model", "--effort", "--timeout"):
        assert (
            len(re.findall(rf"(?m)^\s+{re.escape(option)}(?:\s|=)", claude_block)) == 1
        )
    assert "--fallback-model" not in claude_block
    for binding in (
        'review_target_cwd="$review_shared"',
        'review_target_cwd="$review_worktree"',
    ):
        assert binding in legs
    assert legs.count('  --cwd "$review_target_cwd" \\') == 5
    assert '--cwd "$review_shared"' not in legs

    for family in ("claude", "google", "codex"):
        validator_blocks = [
            block
            for block in fenced_blocks
            if 'python3 "$toolkit_root/bin/verdict_schema.py" validate' in block
            and f'--result-file "${family}_result_file"' in block
        ]
        assert len(validator_blocks) == 1
        validator = validator_blocks[0]
        assert '--expected-review-id "$review_id"' in validator
        assert f"--expected-family {family}" in validator
        assert '--expected-content-digest "$review_digest"' in validator

    assert legs.count('TRIAD_DISPATCH_LOG_DIR="$review_log_dir"') == 5
    for retired_argument in (
        "--formal-read-tools",
        "--expected-permission-mode",
        "--init-preflight",
        "--google-route",
        "TRIAD_REQUIRE_PINNED_VENDOR",
    ):
        assert retired_argument not in legs


def test_formal_duration_and_terminal_outcome_contract_is_single_sourced() -> None:
    skill_root = SKILLS / "triad-cross-family-review"
    convergence = _text(skill_root / "references" / "convergence.md")
    legs = _text(skill_root / "references" / "leg-contracts.md")
    routing = _text(skill_root / "references" / "reviewer-routing.md")
    claude = _text(SKILLS / "triad-claude-dispatch" / "SKILL.md")
    agy = _text(SKILLS / "triad-antigravity-dispatch" / "SKILL.md")
    gemini = _text(SKILLS / "triad-gemini-dispatch" / "SKILL.md")
    readme = " ".join(_text(ROOT / "README.md").split())
    readme_ko = " ".join(_text(ROOT / "README.ko.md").split())

    assert convergence.count("<!-- TERMINAL_OUTCOME_CONTRACT_START -->") == 1
    assert convergence.count("<!-- TERMINAL_OUTCOME_CONTRACT_END -->") == 1
    for clause in (
        "A poll, snapshot, or wait timeout is only a nonterminal wake-up boundary",
        "does not authorize the leader to interrupt a still-running leg",
        "Only the route-owning wrapper's full provider-process deadline or another "
        "observable terminal result may classify a provider leg failure",
        "Leader elapsed time, poll count, and observation timeout never do",
        "For fresh Codex, repeat observation waits until its terminal result arrives",
    ):
        assert clause in " ".join(convergence.split())

    assert "native `1,200,000`-millisecond observation wait" in legs
    assert "issue the same wait again" in legs
    assert "FORMAL_CLAUDE_TIMEOUT = 1200" in _text(ROOT / "bin" / "claude_wrapper.py")
    assert "FORMAL_AGY_TIMEOUT = 600" in _text(ROOT / "bin" / "antigravity_wrapper.py")
    assert "FORMAL_GEMINI_TIMEOUT = 600" in _text(ROOT / "bin" / "gemini_wrapper.py")
    assert "any timeout other than `1200`" in claude
    assert "--timeout 600" in agy
    assert "--timeout 600" in gemini
    for clause in (
        "1,200-second Claude wrapper deadline",
        "600-second AGY or Gemini wrapper deadline",
        "repeatable 1,200-second fresh Codex observation waits",
    ):
        assert clause in readme
    for clause in (
        "Claude wrapper deadline 1,200초",
        "AGY 또는 Gemini wrapper deadline 600초",
        "fresh Codex의 반복 가능한 1,200초 observation wait",
    ):
        assert clause in readme_ko

    convergence_link = "../triad-cross-family-review/references/convergence.md"
    assert f"[convergence]({convergence_link})" in agy
    assert f"[convergence]({convergence_link})" in gemini
    assert "shorter leader polling waits do not terminate it" not in agy

    single_owner_clause = (
        "A poll, snapshot, or wait timeout is only a nonterminal wake-up boundary"
    )
    for non_owner in (
        _text(skill_root / "SKILL.md"),
        legs,
        routing,
        claude,
        agy,
        gemini,
    ):
        assert single_owner_clause not in " ".join(non_owner.split())

    route_neutral_surfaces = (
        _text(ROOT / "bin" / "review_round.py"),
        _text(skill_root / "references" / "review-prompt-contract.md"),
        *(_text(path) for path in SKILLS.glob("*/agents/openai.yaml")),
    )
    for route_neutral in route_neutral_surfaces:
        assert "1,200-second wrapper deadline" not in route_neutral
        assert "1,200,000" not in route_neutral
        assert "600-second wrapper deadline" not in route_neutral
        assert single_owner_clause not in " ".join(route_neutral.split())


def test_google_preflight_blocks_bind_exact_provider_free_contract() -> None:
    legs = _text(
        SKILLS / "triad-cross-family-review" / "references" / "leg-contracts.md"
    )
    fenced_blocks = re.findall(r"```text\n(.*?)\n```", legs, re.DOTALL)
    preflight_blocks = [block for block in fenced_blocks if "--preflight-only" in block]

    assert len(preflight_blocks) == 2
    blocks_by_wrapper = {
        wrapper: next(
            block
            for block in preflight_blocks
            if f'python3 "$toolkit_root/bin/{wrapper}"' in block
        )
        for wrapper in ("antigravity_wrapper.py", "gemini_wrapper.py")
    }
    assert blocks_by_wrapper["antigravity_wrapper.py"].splitlines() == [
        'TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \\',
        'python3 "$toolkit_root/bin/antigravity_wrapper.py" \\',
        '  --prompt-file "$review_task_file" \\',
        '  --google-selector-receipt "$google_selector_receipt" \\',
        '  --expected-review-id "$review_id" \\',
        '  --cwd "$review_target_cwd" \\',
        "  --sandbox read-only \\",
        "  --model gemini-3.1-pro-high \\",
        "  --effort high \\",
        "  --preflight-only \\",
        '  > "$google_preflight_file"',
    ]
    assert blocks_by_wrapper["gemini_wrapper.py"].splitlines() == [
        'TRIAD_DISPATCH_LOG_DIR="$review_log_dir" \\',
        'python3 "$toolkit_root/bin/gemini_wrapper.py" \\',
        '  --prompt-file "$review_task_file" \\',
        '  --google-selector-receipt "$google_selector_receipt" \\',
        '  --expected-review-id "$review_id" \\',
        '  --cwd "$review_target_cwd" \\',
        "  --preflight-only \\",
        '  > "$google_preflight_file"',
    ]


def test_source_sot_launcher_stage_precedes_basis_and_cleans_exact_handles() -> None:
    skill = _text(SKILLS / "triad-cross-family-review" / "SKILL.md")
    legs_raw = _text(
        SKILLS / "triad-cross-family-review" / "references" / "leg-contracts.md"
    )
    legs = " ".join(legs_raw.split())
    staging_clause = (
        "For source-SOT pre-deployment, stage the isolated launcher group from "
        "[leg contracts](references/leg-contracts.md) before creating or capturing "
        "the review basis."
    )

    assert skill.index("2. **Resolve one toolkit.**") < skill.index(staging_clause)
    assert skill.index(staging_clause) < skill.index("3. **Create the basis.**")
    assert (
        "After normal terminal completion or any failure before a provider starts, remove "
        "only `selector_bootstrap_cwd` and `selector_stage_root`, then confirm both "
        "paths are absent." in legs
    )
    assert (
        "The bootstrap guard rejects the bootstrap cwd, staged launcher directory, Codex "
        "home, classifier directory, or shell rc when it resolves inside the toolkit or "
        "review worktree; this check runs before any installation step." in legs
    )
    assert 'TRIAD_BOOTSTRAP_SOURCE_SOT_REVIEW_ROOT="$review_worktree" \\' in legs_raw


def test_source_sot_stage_recipe_canonicalizes_with_required_python(
    tmp_path: Path,
) -> None:
    legs = _text(
        SKILLS / "triad-cross-family-review" / "references" / "leg-contracts.md"
    )
    stage_block = next(
        block
        for block in re.findall(r"```text\n(.*?)\n```", legs, re.DOTALL)
        if "selector_bootstrap_cwd_raw=" in block
    )
    setup_lines = stage_block.splitlines()[:4]

    assert "realpath" not in "\n".join(setup_lines)
    assert sum("python3 -c" in line for line in setup_lines) == 2
    result = subprocess.run(
        [
            "bash",
            "-c",
            "\n".join(
                (
                    "set -eu",
                    'review_id="portable-paths"',
                    *setup_lines,
                    "printf '%s\\n' \"$selector_bootstrap_cwd\" \"$selector_stage_root\"",
                )
            ),
        ],
        cwd=ROOT,
        env={**os.environ, "TMPDIR": str(tmp_path)},
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    resolved = [Path(line) for line in result.stdout.splitlines()]
    assert len(resolved) == 2
    assert resolved[0].is_absolute() and resolved[0].is_dir()
    assert resolved[1].is_absolute() and resolved[1].is_dir()
    assert resolved[0] != resolved[1]


def test_leg_contract_assigns_mechanical_ownership_truthfully() -> None:
    legs = " ".join(
        _text(
            SKILLS / "triad-cross-family-review" / "references" / "leg-contracts.md"
        ).split()
    )

    assert (
        "packaged renderer and wrappers own argument, route, binding, schema, and "
        "output validation" not in legs
    )
    for ownership_clause in (
        "`review_round.py` owns lifecycle paths, inventory, collision checks, prompt "
        "metadata, and Google receipt selection and binding.",
        "Google selectors and wrappers enforce the selected Google route; the Claude "
        "wrapper enforces formal binding completeness, native Plan Mode, schema, "
        "local verdict validation, and output handling.",
        "The exact argv below owns Claude and fresh Codex route parameters.",
    ):
        assert ownership_clause in legs


def test_standalone_skills_and_public_docs_keep_provider_read_contracts() -> None:
    claude = " ".join(_text(SKILLS / "triad-claude-dispatch" / "SKILL.md").split())
    agy = " ".join(_text(SKILLS / "triad-antigravity-dispatch" / "SKILL.md").split())
    readme = " ".join(_text(ROOT / "README.md").split())
    readme_ko = " ".join(_text(ROOT / "README.ko.md").split())

    for clause in (
        "Ordinary calls leave Claude permission selection native",
        "fully bound formal `LegVerdict` route adds native per-call Plan Mode",
        "--model opus --effort xhigh --timeout 1200",
        '--expected-review-id "$review_id" --expected-family claude',
    ):
        assert clause in claude

    for clause in (
        "AGY 1.1.20 or newer",
        "`AGY_NO_HEADLESS_AUTOAPPROVE=1`",
        "uses native `--mode plan`",
        "review-bound native `--json-schema` in plan mode",
        "consumes the terminal `structured_output`",
        "strict local `LegVerdict` validation",
        "no schema-repair provider call",
        "MCP calls are unavailable for the formal Google leg",
        "undecidable uncertainty goes to `open_questions`",
        "Round-integrity mutation detection is separate",
    ):
        assert clause in agy

    for public_doc in (readme, readme_ko):
        for tool_argument in (
            "`AbsolutePath`",
            "`ContentOffset`",
            "`StartLine`",
            "`EndLine`",
        ):
            assert tool_argument in public_doc
    assert "uses native `grep_search`" in readme
    assert "native `grep_search`를 사용합니다" in readme_ko
    assert "MCP calls are denied" in readme
    assert "MCP 호출은 차단" in readme_ko


def test_formal_claude_route_is_fail_closed_across_distribution_contracts() -> None:
    claude = " ".join(_text(SKILLS / "triad-claude-dispatch" / "SKILL.md").split())
    readme = " ".join(_text(ROOT / "README.md").split())
    readme_ko = " ".join(_text(ROOT / "README.ko.md").split())
    changelog = " ".join(_text(ROOT / "CHANGELOG.md").split())
    wrapper = _text(ROOT / "bin" / "claude_wrapper.py")

    assert (
        "The fully bound formal route rejects any model other than `opus`, any "
        "effort other than `xhigh`, any timeout other than `1200`, and every "
        "`--fallback-model` before provider resolution." in claude
    )
    assert (
        "A fully bound formal Claude route fails closed before provider resolution "
        "unless it uses `--model opus --effort xhigh --timeout 1200` with no "
        "`--fallback-model`." in readme
    )
    assert (
        "완전히 바인딩된 formal Claude route는 `--model opus --effort xhigh "
        "--timeout 1200`을 사용하고 `--fallback-model`을 지정하지 않은 경우에만 "
        "provider resolution 전에 통과합니다." in readme_ko
    )
    assert "fail-closed formal Claude route pinning" in changelog
    assert 'FORMAL_CLAUDE_MODEL = "opus"' in wrapper
    assert 'FORMAL_CLAUDE_EFFORT = "xhigh"' in wrapper
    assert "FORMAL_CLAUDE_TIMEOUT = 1200" in wrapper


def test_public_agy_permission_and_formal_route_claims_are_consistent() -> None:
    readme = " ".join(_text(ROOT / "README.md").split())
    readme_ko = " ".join(_text(ROOT / "README.ko.md").split())
    security = " ".join(_text(ROOT / "SECURITY.md").split())
    gemini = " ".join(_text(SKILLS / "triad-gemini-dispatch" / "SKILL.md").split())
    leg_contracts = " ".join(
        _text(
            SKILLS / "triad-cross-family-review" / "references" / "leg-contracts.md"
        ).split()
    )
    routing = " ".join(
        _text(
            SKILLS / "triad-cross-family-review" / "references" / "reviewer-routing.md"
        ).split()
    )

    assert "makes no user-setting change" not in readme
    assert "user setting을 변경하지 않습니다" not in readme_ko
    assert "transient AGY global-settings transaction" in readme
    assert "일시적 AGY global-settings transaction" in readme_ko
    assert (
        "auto-approve removes interactive approval prompts, while the transaction's "
        "explicit deny rules still block their named action namespaces" in readme
    )
    assert (
        "auto-approve는 interactive approval prompt를 제거하지만 transaction의 "
        "explicit deny rule은 지정된 action namespace를 계속 차단합니다" in readme_ko
    )
    assert (
        "auto-approve removes interactive approval prompts but does not remove "
        "explicit deny entries" in security
    )
    assert "MCP calls are denied" in security
    assert "AGY native official-web read path" in security
    assert "voids deny" not in security
    assert "If AGY was selected, started, or later failed" in gemini
    assert "standalone compatibility consult only" in gemini
    assert "Personal Google Sign-In requires AGY" in routing
    assert "Gemini Enterprise OAuth" in routing
    assert "transient deny transaction" in leg_contracts


def test_recipient_guidance_uses_codex_host_policy_for_outside_sandbox_execution() -> (
    None
):
    readme = " ".join(_text(ROOT / "README.md").split())
    readme_ko = " ".join(_text(ROOT / "README.ko.md").split())
    security = " ".join(_text(ROOT / "SECURITY.md").split())
    migration = " ".join(_text(ROOT / "migration" / "AGENTS.recommended.md").split())
    cross_family = " ".join(
        _text(SKILLS / "triad-cross-family-review" / "SKILL.md").split()
    )

    for public_doc in (readme, readme_ko):
        assert "https://learn.chatgpt.com/docs/sandboxing" in public_doc
        assert "https://learn.chatgpt.com/docs/config-file/config-basic" in public_doc
        assert (
            "https://learn.chatgpt.com/docs/config-file/config-reference" in public_doc
        )
        assert "https://learn.chatgpt.com/docs/plugins" in public_doc
        assert 'sandbox_mode = "workspace-write"' in public_doc
        assert 'approval_policy = "on-request"' in public_doc
        assert 'approvals_reviewer = "user"' in public_doc
        assert 'approvals_reviewer = "auto_review"' in public_doc
        assert "`/permissions`" in public_doc
        assert 'sandbox_mode = "danger-full-access"' not in public_doc
        assert 'approval_policy = "never"' not in public_doc

    assert "outside the Codex workspace sandbox" in migration
    assert "user-selected Codex host policy" in migration
    assert "no plugin-level install-time sandbox grant" in migration
    assert "outer Codex host sandbox" in security
    assert "does not install or mutate that host policy" in security
    assert (
        "Launch all TRIAD lifecycle, provider, test, and development commands "
        "outside the Codex workspace sandbox"
    ) in cross_family
    assert "Do not install or mutate the Codex host permission policy" in cross_family


def test_enterprise_gemini_fallback_is_pre_dispatch_frozen_and_read_only() -> None:
    skill_root = SKILLS / "triad-cross-family-review"
    cross_family = " ".join(_text(skill_root / "SKILL.md").split())
    routing = " ".join(_text(skill_root / "references" / "reviewer-routing.md").split())
    leg_contracts = _text(skill_root / "references" / "leg-contracts.md")
    prompt_contract = " ".join(
        _text(skill_root / "references" / "review-prompt-contract.md").split()
    )
    policy_path = ROOT / "bin" / "policies" / "gemini-formal-readonly.toml"

    assert "Select and exclusive-create one Google selector receipt" in cross_family
    for route_clause in (
        "Personal Google Sign-In requires AGY",
        "Gemini Enterprise OAuth may select Gemini only when AGY is absent",
        "one frozen route",
        "CLI Auto with `-m auto`",
        "runtime-model identity",
        '`runtime_identity: "unexposed"`',
        "`stats.models`",
    ):
        assert route_clause in routing

    for mechanical_contract in (
        '"$google_selector_launcher" select-google-route',
        '--google-selector-receipt "$google_selector_receipt"',
        '--google-preflight-receipt "$google_preflight_file"',
        'python3 "$toolkit_root/bin/antigravity_wrapper.py"',
        'python3 "$toolkit_root/bin/gemini_wrapper.py"',
        "--preflight-only",
        "bin/policies/gemini-formal-readonly.toml",
        "TRIAD never adds `--skip-trust`",
    ):
        assert mechanical_contract in leg_contracts

    assert "selected Google authentication class" in prompt_contract
    assert "selector and preflight receipt hashes" in prompt_contract
    assert "Gemini Enterprise OAuth" not in prompt_contract
    assert "AGY native tool names" not in prompt_contract

    policy = tomllib.loads(_text(policy_path))
    rules = policy["rule"]
    allowed_tools = {
        tool
        for rule in rules
        if rule["decision"] == "allow" and rule["priority"] == 999
        for tool in (
            [rule["toolName"]]
            if isinstance(rule["toolName"], str)
            else rule["toolName"]
        )
    }
    assert allowed_tools == {
        "read_file",
        "read_many_files",
        "list_directory",
        "glob",
        "grep_search",
        "google_web_search",
        "web_fetch",
        "get_internal_docs",
    }
    denied_tools = {
        tool
        for rule in rules
        if rule["decision"] == "deny" and rule["priority"] == 999
        for tool in (
            [rule["toolName"]]
            if isinstance(rule["toolName"], str)
            else rule["toolName"]
        )
    }
    assert denied_tools == {
        "write_file",
        "replace",
        "run_shell_command",
        "enter_plan_mode",
        "exit_plan_mode",
    }
    assert any(
        rule["toolName"] == "*"
        and rule["decision"] == "deny"
        and rule["priority"] == 998
        for rule in rules
    )

    active_contract_paths = (
        MANIFEST,
        ROOT / "README.md",
        ROOT / "README.ko.md",
        ROOT / "SECURITY.md",
        ROOT / "CHANGELOG.md",
        ROOT
        / "docs"
        / "status"
        / "2026-09-02-gemini-enterprise-fallback-checkpoint.md",
        skill_root / "SKILL.md",
        skill_root / "agents" / "openai.yaml",
        skill_root / "references" / "convergence.md",
        skill_root / "references" / "leg-contracts.md",
        skill_root / "references" / "review-prompt-contract.md",
        skill_root / "references" / "reviewer-routing.md",
        SKILLS / "triad-gemini-dispatch" / "SKILL.md",
        SKILLS / "triad-gemini-dispatch" / "agents" / "openai.yaml",
        ROOT / "migration" / "AGENTS.recommended.md",
        policy_path,
    )
    shipped = "\n".join(_text(path) for path in active_contract_paths).lower()
    for workspace_only_marker in (
        "temporary five-leg formal-review override",
        "five required independent legs",
        "all five before consuming a verdict",
        "temporarily filling the unavailable claude seat",
        "temporary five-leg gate",
    ):
        assert workspace_only_marker not in shipped


def test_changelog_marks_the_superseded_google_permission_claim() -> None:
    changelog = " ".join(_text(ROOT / "CHANGELOG.md").split())

    assert (
        "MCP calls are denied, conditionally authorized external evidence uses AGY "
        "native official-web reads" in changelog
    )
    assert (
        "This 0.2.539 permission statement is historical; 0.2.541 supersedes its "
        "intent-only residual" in changelog
    )


def test_leg_contract_scopes_mechanical_denial_to_named_namespaces() -> None:
    active_contracts = tuple(
        " ".join(_text(path).split())
        for path in (
            SKILLS / "triad-antigravity-dispatch" / "SKILL.md",
            SKILLS / "triad-cross-family-review" / "references" / "leg-contracts.md",
            SKILLS
            / "triad-cross-family-review"
            / "references"
            / "review-prompt-contract.md",
        )
    )
    leg_contracts = active_contracts[1]

    assert (
        "A tool attempt in a named denied namespace is also blocked by its matching "
        "deny entry" in leg_contracts
    )
    assert (
        "Other prompt-forbidden actions remain contract obligations"
        not in leg_contracts
    )
    for active_contract in active_contracts:
        assert "a denied call invalidates the leg" not in active_contract
        assert "`tool-contract-violation`" not in active_contract
    assert "Local verdict and review-binding checks" in leg_contracts


def test_cross_family_skill_routes_workflow_failures_to_one_contract() -> None:
    skill_root = SKILLS / "triad-cross-family-review"
    skill = " ".join(_text(skill_root / "SKILL.md").split())
    convergence = " ".join(_text(skill_root / "references" / "convergence.md").split())

    assert "[convergence](references/convergence.md)" in skill
    for recovery_clause in (
        "zero started provider legs invalidates the attempt",
        "supported cleanup for an exact managed root",
        "restart with a fresh review ID",
        "controlled setup-only probe",
        "not a formal review round",
    ):
        assert recovery_clause in convergence

    for code_owned_detail in (
        "absolute canonical no-symlink paths",
        "sorted JSON array of non-empty normalized POSIX relative paths",
        "If it neither returned a review root",
        "Never manually rebuild or alter a packet",
    ):
        assert code_owned_detail not in skill


def test_cross_family_skill_has_one_partial_start_contract_owner() -> None:
    skill_root = SKILLS / "triad-cross-family-review"
    sources = {
        "skill": _text(skill_root / "SKILL.md"),
        "leg_contracts": _text(skill_root / "references" / "leg-contracts.md"),
        "routing": _text(skill_root / "references" / "reviewer-routing.md"),
        "convergence": _text(skill_root / "references" / "convergence.md"),
    }
    normalized = {name: " ".join(text.split()) for name, text in sources.items()}
    convergence = normalized["convergence"]

    assert sources["convergence"].count("<!-- PARTIAL_START_CONTRACT_START -->") == 1
    assert sources["convergence"].count("<!-- PARTIAL_START_CONTRACT_END -->") == 1
    for name in ("skill", "leg_contracts", "routing"):
        assert "[convergence](" in sources[name]
        assert "once any provider leg has started" not in normalized[name]
        assert "wait for every already-started sibling" not in normalized[name]
        assert (
            "preserve and reproduce every valid sibling finding" not in normalized[name]
        )

    for contract_clause in (
        "once any provider leg has started",
        "later leg start or result failure",
        "invalidates admission",
        "wait for every already-started sibling",
        "remain provisional until post-review integrity succeeds",
        "preserve and reproduce every valid sibling finding",
        "skill, tool, instruction, operator, or vendor",
        "valid `NOT-SAFE`",
        "advisory only",
        "reproduce every collected finding before the next round",
        "correct and verify every reproduced in-scope defect",
        "correct the classified leg failure",
        "diagnose and correct the integrity mismatch before a fresh round",
        "after every started leg terminates",
    ):
        assert contract_clause in convergence

    assert "terminate every still-running leg" not in convergence
    assert "discard every current-round verdict" not in convergence
    assert (
        "never continue a sibling merely to collect advisory evidence"
        not in convergence
    )

    readme = " ".join(_text(ROOT / "README.md").split())
    readme_ko = " ".join(_text(ROOT / "README.ko.md").split())
    security = " ".join(_text(ROOT / "SECURITY.md").split())
    migration = " ".join(_text(ROOT / "migration" / "AGENTS.recommended.md").split())
    for text in (readme, readme_ko, security, migration):
        assert "whole-round fail-fast cancellation" not in text
        assert "immediate whole-round fail-fast cancellation" not in text
    assert "valid sibling findings remain advisory only" in readme.lower()
    assert "유효한 sibling finding은 advisory로만 유지" in readme_ko
    assert "already-started sibling families finish" in security
    assert "already-started sibling families finish" in migration


def test_cross_family_skill_admits_only_a_complete_healthy_round() -> None:
    skill = " ".join(_text(SKILLS / "triad-cross-family-review" / "SKILL.md").split())
    admission = skill.split("9. **Verify before admission.**", 1)[1].split(
        "10. **Reproduce and converge.**", 1
    )[0]

    assert "Wait for every started leg to terminate" in admission
    assert "ROUND_INTEGRITY_OK" in admission
    assert "post-review fingerprint" in admission
    assert "Admit evidence only when integrity matches" in admission
    assert "all three required families" in admission
    assert "same digest" in admission


def test_cross_family_contract_distinguishes_zero_start_from_partial_start() -> None:
    skill_root = SKILLS / "triad-cross-family-review"
    convergence = " ".join(_text(skill_root / "references" / "convergence.md").split())
    skill = " ".join(_text(skill_root / "SKILL.md").split())
    leg_contracts = " ".join(
        _text(skill_root / "references" / "leg-contracts.md").split()
    )

    assert "Failure before any provider starts" in convergence
    assert "zero started provider legs invalidates the attempt" in convergence
    assert "Failure after a provider starts" in convergence
    assert "partial-start contract" in convergence
    assert "Close further launch" in convergence
    assert "advisory only" in convergence
    assert "fresh ID" in convergence
    assert "once any provider leg has started" not in skill
    assert "once any provider leg has started" not in leg_contracts

    readme = " ".join(_text(ROOT / "README.md").split())
    readme_ko = " ".join(_text(ROOT / "README.ko.md").split())
    security = " ".join(_text(ROOT / "SECURITY.md").split())
    for text in (readme, security):
        assert "after every started leg terminates" in text
        assert "record the actual start failure" in text
        assert "not started because launch was closed" in text
    assert "시작된 모든 leg이 끝난 뒤" in readme_ko
    assert "실제 start failure" in readme_ko
    assert "launch가 닫혀 시작하지 않은 상태" in readme_ko


def test_cross_family_contract_escalates_repeated_zero_provider_failures() -> None:
    skill_root = SKILLS / "triad-cross-family-review"
    convergence = " ".join(_text(skill_root / "references" / "convergence.md").split())
    leg_contracts = " ".join(
        _text(skill_root / "references" / "leg-contracts.md").split()
    )

    for recovery_clause in (
        "After a second comparable zero-provider failure",
        "stop allocating review IDs",
        "retained receipts and command context",
        "identify and verify the shared cause",
        "controlled setup-only probe",
    ):
        assert recovery_clause in convergence

    assert "outer host working directory" in leg_contracts
    assert "inner bootstrap child" in leg_contracts
    assert "Preserve the login user's `HOME`" in leg_contracts
    assert "Codex directory with `TRIAD_BOOTSTRAP_CODEX_ROOT`" in leg_contracts


def test_project_agents_verification_commands_are_workspace_root_safe() -> None:
    agents = " ".join(_text(ROOT / "AGENTS.md").split())

    assert '"$1/tests" --rootdir "$1"' in agents
    assert 'bash -n "$1/scripts/bootstrap.sh"' in agents
    assert 'python3 "$1/scripts/verify_distribution.py" --source-root "$1"' in agents
    assert "Never use a bare repository-relative path" in agents


def test_failed_leg_docs_allow_verified_transient_vendor_recovery() -> None:
    for path in (
        ROOT / "README.md",
        ROOT / "SECURITY.md",
        ROOT / "migration" / "AGENTS.recommended.md",
        ROOT / "CHANGELOG.md",
    ):
        assert "verify recovery from a transient vendor incident" in _text(path)

    readme_ko = _text(ROOT / "README.ko.md")
    assert "transient vendor incident" in readme_ko
    assert "복구를 검증" in readme_ko


def test_cross_family_skill_uses_current_task_authority_before_preparing() -> None:
    skill = " ".join(_text(SKILLS / "triad-cross-family-review" / "SKILL.md").split())

    authority_rule = (
        "The current owner-supplied task or explicitly designated executable plan "
        "is the execution authority for the round."
    )
    assert authority_rule in skill
    assert "Ask the owner when a required product or design decision is absent" in skill
    assert "fresh review ID" in skill
    assert "[CHANGELOG.md](../../CHANGELOG.md)" not in skill
    assert "Read only the current release section of" not in skill


def test_cross_family_skill_owns_operational_prompts_without_meta_review() -> None:
    skill = " ".join(_text(SKILLS / "triad-cross-family-review" / "SKILL.md").split())

    assert "project instructions explicitly select worktree-first review" in skill
    assert "current task, status, and diff as regular files" in skill
    assert "`render-worktree --output` path resolves there" in skill
    assert "prepared-directory prompt contract does not apply" in skill
    assert "its renderer supplies the result contract" in skill
    assert "`skill-prompt-review` stays outside every operational round" in skill
    assert "Dispatch only successfully rendered prompts" in skill


def test_cross_family_skill_names_worktree_first_custody_and_run_roots() -> None:
    skill = " ".join(_text(SKILLS / "triad-cross-family-review" / "SKILL.md").split())

    assert "`review_custody_root`" in skill
    assert "`review_run_root`" in skill
    for run_artifact in ("selector receipts", "prompts", "logs", "results"):
        assert run_artifact in skill
    assert "`render-worktree --output`" in skill
    assert "path resolves there" in skill


def test_cross_family_skill_delegates_mechanical_lifecycle_to_code() -> None:
    skill_path = SKILLS / "triad-cross-family-review" / "SKILL.md"
    skill_raw = _text(skill_path)
    skill = " ".join(skill_raw.split())
    lifecycle = _text(ROOT / "bin" / "review_round.py")
    lifecycle_tests = _text(ROOT / "tests" / "test_review_round.py")

    for link in (
        "[review prompt contract](references/review-prompt-contract.md)",
        "[reviewer routing](references/reviewer-routing.md)",
        "[leg contracts](references/leg-contracts.md)",
        "[convergence](references/convergence.md)",
    ):
        assert link in skill_raw

    for subcommand in (
        "prepare",
        "manifest",
        "capture",
        "fingerprint-worktree",
        "select-google-route",
        "render",
        "render-worktree",
        "verify",
        "cleanup",
    ):
        assert subcommand in skill
        assert f'commands.add_parser("{subcommand}")' in lifecycle

    for implementation in (
        "def prepare_review_workspace(",
        "def create_source_manifest(",
        "def capture_round(",
        "def verify_round(",
        "def select_google_route(",
        "def render_review_prompt(",
        "def render_worktree_review_prompt(",
        "def cleanup_review_workspace(",
    ):
        assert implementation in lifecycle

    assert "lifecycle code owns path grammar, inventory, collision" in skill
    assert (
        "renderer owns metadata serialization, route binding, tool contracts" in skill
    )
    for duplicated_parser_detail in (
        "sorted JSON array of non-empty normalized POSIX relative paths",
        "absolute canonical no-symlink paths",
        "reserved `triad-review-<review-id>` system-temp namespace",
        "member-list file is the only source-copy IPC",
        "prior-round snapshot",
        "prior-round verdict",
    ):
        assert duplicated_parser_detail not in skill
    assert "python3 bin/review_round.py" not in skill

    for behavior_test in (
        "test_prepare_copies_exact_members_and_isolates_review_ids",
        "test_capture_and_verify_bind_prepare_source_root_to_worktree",
        "test_rendered_prompt_binds_focused_round_once",
        "test_cli_prepare_and_cleanup_round_trip",
        "test_cli_select_google_route_exclusive_creates_canonical_receipt",
    ):
        assert behavior_test in lifecycle_tests

    assert "provider-free lifecycle characterization" in skill
    assert "not a review round or admission result" in skill
    assert "ROUND_INTEGRITY_OK" in skill
    assert "project-required post-review fingerprint" in skill
    assert "Clean the exact round" in skill


def test_cross_family_skill_requires_the_review_source_manifest() -> None:
    skill_root = SKILLS / "triad-cross-family-review"
    skill = " ".join(_text(skill_root / "SKILL.md").split())
    prompt_contract = " ".join(
        _text(skill_root / "references" / "review-prompt-contract.md").split()
    )
    lifecycle = _text(ROOT / "bin" / "review_round.py")
    lifecycle_tests = _text(ROOT / "tests" / "test_review_round.py")

    assert "exact approved members" in skill
    assert "Add only current `TASK.md`, `REVIEW.diff`, optional `EVIDENCE.md`" in skill
    assert "run `manifest` last" in skill
    for packet_member in (
        "`source/product/`",
        "current `TASK.md`",
        "current `REVIEW.diff`",
        "optional bounded `EVIDENCE.md`",
        "generated `SOURCE_SHA256SUMS`",
    ):
        assert packet_member in prompt_contract

    for code_owned_contract in (
        "SOURCE_SHA256SUMS must be a JSON array",
        "SOURCE_SHA256SUMS must use canonical JSON",
        "SOURCE_SHA256SUMS paths must be sorted",
        "SOURCE_SHA256SUMS path inventory mismatch",
        "SOURCE_SHA256SUMS digest mismatch",
    ):
        assert code_owned_contract in lifecycle

    for behavior_test in (
        "test_capture_rejects_unsorted_lifecycle_manifest",
        "test_capture_rejects_lifecycle_manifest_digest_mismatch",
        "test_capture_rejects_extra_prior_round_artifact_in_lifecycle_packet",
    ):
        assert behavior_test in lifecycle_tests


def test_retired_review_runtime_is_absent() -> None:
    retired = [
        ROOT / "bin" / "_pty.py",
        ROOT / "bin" / "review_evidence.py",
        ROOT / "bin" / "review_coverage.py",
        ROOT / "bin" / "triad_formal_review_schema.py",
        ROOT
        / "skills"
        / "triad-cross-family-review"
        / "references"
        / "fresh-codex-formal-review.md",
    ]
    assert not any(path.exists() for path in retired)


def test_current_public_docs_do_not_advertise_retired_batch_or_packet_modes() -> None:
    public_docs = {
        name: _text(ROOT / name)
        for name in (
            "README.md",
            "README.ko.md",
            "SECURITY.md",
            "skills/triad-cross-family-review/references/reviewer-routing.md",
        )
    }
    current = "\n".join(public_docs.values())
    for stale in (
        "batched-full-coverage",
        "full batch matrix",
        "`BatchReceipt`",
        "packet-bound `FormalReview`",
        "sealed-packet flag",
        "deterministic batch",
        "receipt contract",
        "coverage admission",
        "non-UTF-8 source",
    ):
        assert stale not in current
    for name in ("README.md", "README.ko.md", "SECURITY.md"):
        for stale in ("permission-unavailable", "truncated-answer"):
            assert stale not in public_docs[name], (name, stale)
    for name in ("README.md", "README.ko.md"):
        local_data = " ".join(public_docs[name].split())
        assert "`triad-review-`" in local_data
        assert "`results/_logs`" in local_data
        assert "strictly more than 30 days" in local_data
    permission_contracts = {
        "README.md": (
            "native AGY CLI sign-in",
            "`--sandbox read-only`",
            "transient global-settings transaction",
            "restores the original bytes",
            "formally bound Claude leg adds native `--permission-mode plan`",
        ),
        "README.ko.md": (
            "native AGY CLI 로그인",
            "`--sandbox read-only`",
            "일시적 global-settings transaction",
            "원래 바이트를 복원",
            "formal binding이 완료된 Claude leg는 native `--permission-mode plan`을 추가",
        ),
        "SECURITY.md": (
            "native AGY CLI sign-in",
            "`--sandbox read-only`",
            "transient global-settings transaction",
            "restores the original bytes",
        ),
    }
    for name, phrases in permission_contracts.items():
        compact = " ".join(public_docs[name].split())
        for phrase in phrases:
            assert phrase in compact, (name, phrase)
    contradictory_claims = {
        "README.md": (
            "TRIAD does not select or override a permission mode",
            "Provider permission and project-trust policy remain native",
            "Permission selection remains with the provider/user/project",
            "Provider, user, and project settings decide whether a native operation is allowed, denied, or interactive",
            "The boundary rests on process permissions selected by the provider/user/project",
            "AGY child selection is the sole permission-mode exception",
            "outside the documented packaged AGY child selection",
        ),
        "README.ko.md": (
            "Native provider permission을 그대로 상속합니다",
            "TRIAD는 permission mode를 선택하거나 override하지",
            "provider permission과 project trust policy는 native 설정을 유지합니다",
            "Permission 선택은 provider/user/project에 남습니다",
            "경계는 provider/user/project가 선택한 permission",
            "packaged AGY child 선택만 permission-mode 예외",
            "packaged AGY child 예외 밖의 permission 선택은",
        ),
        "SECURITY.md": (
            "TRIAD does not select or override a permission mode",
            "strengthen or weaken native authority",
        ),
        "skills/triad-cross-family-review/references/reviewer-routing.md": (),
    }
    for name, claims in contradictory_claims.items():
        compact = " ".join(public_docs[name].split())
        for claim in claims:
            assert claim not in compact, (name, claim)
    routing = public_docs[
        "skills/triad-cross-family-review/references/reviewer-routing.md"
    ]
    compact_routing = " ".join(routing.split())
    assert "one frozen route" in compact_routing
    assert "Personal Google Sign-In" in compact_routing
    assert "Gemini Enterprise OAuth" in compact_routing
    assert "does not sign in, change accounts" in compact_routing
    assert "authentication class and route stay fixed" in compact_routing
    temp_root_contracts = {
        "README.md": "must include the canonical system temp base",
        "README.ko.md": "canonical system temp base를 포함해야",
        "SECURITY.md": "must include the canonical system temp base",
    }
    for name, phrase in temp_root_contracts.items():
        assert phrase in " ".join(public_docs[name].split()), (name, phrase)


def test_governing_agy_documents_match_the_current_formal_route() -> None:
    governing = {
        path: _text(ROOT / path)
        for path in (
            "docs/superpowers/specs/2026-08-05-agy-1.1.10-formal-route-design.md",
            "docs/superpowers/plans/2026-08-05-agy-1.1.10-formal-route.md",
        )
    }

    for path, text in governing.items():
        assert "Historical, superseded, and non-executable" in text, path
        assert "2026-08-05-triad-0.2.533-owner-decisions-and-release.md" in text, path
        assert "--model gemini-3.1-pro-high" in text, path
        assert "--effort high" in text, path
        assert "one focused Google leg" in text, path
        assert "one provider call" in text, path


def test_superseded_agy_documents_point_to_the_current_formal_route() -> None:
    superseded = {
        "docs/superpowers/specs/2026-08-12-formal-leg-fail-fast-and-agy-binding-design.md": (
            "native schema binding",
            "skills/triad-antigravity-dispatch/SKILL.md",
        ),
        "docs/superpowers/plans/2026-08-12-formal-leg-fail-fast-and-agy-binding.md": (
            "AGY 1.1.12 native",
            "skills/triad-antigravity-dispatch/SKILL.md",
        ),
        "docs/superpowers/plans/2026-08-13-formal-agy-project-oauth.md": (
            "Run a fresh operational three-family review",
            "skills/triad-antigravity-dispatch/SKILL.md",
        ),
        "docs/superpowers/specs/2026-08-13-formal-google-cli-oauth-only-design.md": (
            "voids both the deny transaction",
            "Matches user-configured deny rule",
        ),
    }

    for path, required_history in superseded.items():
        text = _text(ROOT / path)
        assert "Historical, superseded, and non-executable" in text, path
        assert "0.2.541" in text, path
        for phrase in required_history:
            assert phrase in text, (path, phrase)


def test_current_release_docs_bind_superseded_agy_route_and_current_review_boundary() -> (
    None
):
    changelog = _text(ROOT / "CHANGELOG.md")
    handoff = _text(ROOT / "docs/status/2026-08-05-next-session-handoff.md")
    release_plan = _text(
        ROOT
        / "docs"
        / "superpowers"
        / "plans"
        / "2026-08-05-triad-0.2.533-owner-decisions-and-release.md"
    )

    assert "`gemini-3.1-pro-high --effort high`" in changelog
    assert "0.2.532 route is historical and superseded" in changelog
    assert (
        "Preserves the owner-approved prepared-directory digest algorithm" in changelog
    )
    assert "`git hash-object` replacement proposal is not adopted" in changelog
    assert "Implements the unique-ID system-temp lifecycle guarantee" in changelog
    assert (
        "the exact digest printed by `capture` the only supported digest handoff"
        in changelog
    )
    assert "rejects non-regular member-list nodes before reading" in changelog
    assert (
        "maps prepared-file I/O failures to the controlled lifecycle error" in changelog
    )
    assert "real configured review-root storage error as unavailable" in changelog
    assert "does not fall back outside that root" in changelog
    assert "0.2.533 supersedes the configured-root fallback" in changelog
    assert "post-r8 bounded-correction" in handoff
    assert "current lifecycle/JSON-IPC bounded-correction candidate" in handoff
    assert "pending r9 candidate" not in handoff
    assert "Run a fresh complete round over a new digest" in handoff
    assert "final-0.2.533-r9" in release_plan
    assert "FINAL_REVIEW_ID" in release_plan
    assert "final-r2" not in release_plan
    assert "Historical, superseded, and non-executable" in release_plan
    assert "skills/triad-antigravity-dispatch/SKILL.md" in release_plan
    assert "skills/triad-cross-family-review/SKILL.md" in release_plan
    assert "docs/references/repair-protocol.md" in handoff
    assert "stale 80-file count" in handoff


def test_wrapper_sources_have_no_retired_permission_or_packet_transport() -> None:
    antigravity = _text(ROOT / "bin" / "antigravity_wrapper.py")
    compact_antigravity = " ".join(antigravity.split())
    other_wrappers = "\n".join(
        _text(ROOT / "bin" / name)
        for name in ("claude_wrapper.py", "gemini_wrapper.py")
    )
    for stale in (
        "--sealed-packet-root",
        "--expected-packet-sha256",
        "run_via_pty",
    ):
        assert stale not in antigravity
        assert stale not in other_wrappers
    assert '"--sandbox"' in antigravity
    assert '"--project"' not in antigravity
    assert antigravity.count('"--dangerously-skip-permissions"') == 1
    assert (
        "Formal plan-mode calls pass the review-bound native finish schema"
        in compact_antigravity
    )
    assert (
        "plan-mode calls omit the unsupported native finish schema"
        not in compact_antigravity
    )
    assert "--dangerously-skip-permissions" not in other_wrappers


def test_provider_wrappers_are_packaged_as_executables() -> None:
    for name in (
        "antigravity_wrapper.py",
        "claude_wrapper.py",
        "gemini_wrapper.py",
    ):
        mode = (ROOT / "bin" / name).stat().st_mode
        assert mode & stat.S_IXUSR, name


def test_overviews_distinguish_packet_integrity_from_route_bound_admission() -> None:
    readme = " ".join(_text(ROOT / "README.md").split())
    korean = " ".join(_text(ROOT / "README.ko.md").split())

    for overview in (readme, korean):
        assert "prepared-directory integrity digest" in overview
        assert "route-bound `metadata.content_digest`" in overview


def test_distribution_documents_fresh_process_acceptance() -> None:
    readme = _text(ROOT / "README.md")
    skill = _text(SKILLS / "triad-cross-family-review" / "SKILL.md")

    assert "session after install or update" in readme
    compact_skill = " ".join(skill.split())
    assert "packaged manifest and skill bytes" in compact_skill
    assert "exact current marker" in compact_skill
