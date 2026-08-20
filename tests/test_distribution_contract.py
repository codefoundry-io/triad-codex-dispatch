from __future__ import annotations

import json
import re
import stat
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
SKILLS = ROOT / "skills"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_manifest_describes_the_convergent_distribution() -> None:
    manifest = json.loads(_text(MANIFEST))

    assert manifest["name"] == "triad-codex-dispatch"
    assert manifest["version"] == "0.2.542"
    assert manifest["skills"] == "./skills/"
    prompts = "\n".join(manifest["interface"]["defaultPrompt"])
    assert "triad-cross-family-review" in prompts
    assert "same complete focused directory" in prompts
    assert "batched-full-coverage" not in prompts


def test_current_release_heading_matches_manifest_and_readme_contract() -> None:
    version = json.loads(_text(MANIFEST))["version"]
    changelog = _text(ROOT / "CHANGELOG.md")

    assert f"## {version} — 2026-08-21" in changelog
    assert f"### Upgrading to {version}" in _text(ROOT / "README.md")
    assert f"### {version} 업그레이드" in _text(ROOT / "README.ko.md")
    assert "## 0.2.541 — 2026-08-20" in changelog
    assert "Formal review excludes `grep_search` because AGY 1.1.16" in changelog


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


def test_gemini_agent_metadata_is_standalone_not_formal_fallback() -> None:
    metadata = _text(SKILLS / "triad-gemini-dispatch" / "agents" / "openai.yaml")

    assert "Standalone Gemini CLI compatibility consult" in metadata
    assert "not a formal Google-family review leg or fallback" in metadata
    assert "Vertex, or API-key fallback" not in metadata
    assert "only after agy is proven unavailable" not in metadata


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

    assert "one Claude LegVerdict" in text
    assert "one Google LegVerdict" in text
    assert "one fresh Codex LegVerdict" in text
    assert "OWNER_DECISION_REQUIRED" in text
    assert "There is no arbitrary round cap" in text
    assert "Do not retain review batches" in compact
    assert "fresh Codex process" in compact
    for owner_slot in (
        "Proposed delta:",
        "Evidence:",
        "Impact:",
        "Decision needed:",
    ):
        assert owner_slot in convergence
    assert "Do not implement the proposed delta while asking" in convergence


def test_formal_routes_are_explicit_and_reviewer_only() -> None:
    claude = _text(SKILLS / "triad-claude-dispatch" / "SKILL.md")
    leg_contracts = _text(
        SKILLS / "triad-cross-family-review" / "references" / "leg-contracts.md"
    )
    prompt_contract = _text(
        SKILLS
        / "triad-cross-family-review"
        / "references"
        / "review-prompt-contract.md"
    )
    reviewer_routing = _text(
        SKILLS / "triad-cross-family-review" / "references" / "reviewer-routing.md"
    )
    agy = _text(SKILLS / "triad-antigravity-dispatch" / "SKILL.md")
    gemini = _text(SKILLS / "triad-gemini-dispatch" / "SKILL.md")
    readme = _text(ROOT / "README.md")
    readme_ko = _text(ROOT / "README.ko.md")
    compact_leg_contracts = " ".join(leg_contracts.split())
    compact_prompt_contract = " ".join(prompt_contract.split())
    compact_reviewer_routing = " ".join(reviewer_routing.split())
    compact_antigravity = " ".join(agy.split())
    compact_readme = " ".join(readme.split())
    compact_readme_ko = " ".join(readme_ko.split())

    for compact in (compact_readme, compact_readme_ko):
        assert "`AbsolutePath`" in compact
        assert "another page" in compact
        assert "`ContentOffset`" in compact
        assert "`StartLine`" in compact
        assert "`EndLine`" in compact
    assert "uses native `grep_search`" in compact_readme
    assert "native `grep_search`를 사용합니다" in compact_readme_ko

    assert "## Contents" in leg_contracts
    for entry in (
        "[Claude](#claude)",
        "[Google family](#google-family)",
        "[Fresh Codex](#fresh-codex)",
        "[Shared containment boundary](#shared-containment-boundary)",
    ):
        assert entry in leg_contracts

    assert "--model opus" in claude and "--effort xhigh" in claude
    assert "--timeout 1800" in claude
    assert '--expected-review-id "$review_id"' in claude
    assert "--expected-family claude" in claude
    assert '--expected-content-digest "$review_digest"' in claude
    assert (
        "Claude: `opus`, `xhigh`, retained 1,800-second end-to-end wrapper deadline."
        in compact_reviewer_routing
    )
    assert "--formal-read-tools" not in claude
    assert "--formal-read-tools" not in leg_contracts
    assert "--timeout 1800" in leg_contracts
    assert "wake-up boundaries" in leg_contracts
    for compact in (compact_leg_contracts, compact_prompt_contract):
        assert "installed CLI tools" in compact
        assert "Configured MCP servers remain available" in compact
        assert (
            "Existing user permission settings continue to govern MCP calls" in compact
        )
        assert (
            "Approved official-web reads through read-only MCP tools remain available"
            in compact
        )
        assert (
            "Do not edit files, change external state, or execute candidate code"
            in compact
        )
        assert "formal Google settings transaction denies all MCP calls" in compact
        assert "Approved AGY native official-web reads remain available" in compact
    assert "MCP calls are unavailable for the formal Google leg" in compact_antigravity
    assert "AGY native official-web reads" in compact_antigravity
    for compact in (
        compact_leg_contracts,
        compact_prompt_contract,
        compact_antigravity,
    ):
        assert "Use `grep_search` with the required `SearchPath` and `Query`" in compact
        assert "inside the review target identified by Review metadata" in compact
        assert "use `list_dir`, `find_by_name`, and `view_file` as needed" in compact
        assert "For every `view_file` call" in compact
        assert "explicit positive-integer `StartLine` and `EndLine` ranges" in compact
        assert "Never request `ContentOffset` or `IsSkillFile`" in compact
    telemetry_contract = (
        "The wrapper scans formal `step_update` telemetry, admits only the fixed "
        "native read/search tool set, and terminates the leg as "
        "`tool-contract-violation` for any other tool, non-object parameters, a "
        "missing or non-integer step index, or conflicting duplicate step telemetry."
    )
    for compact in (
        compact_leg_contracts,
        compact_prompt_contract,
        compact_antigravity,
        " ".join(_text(ROOT / "CHANGELOG.md").split()),
    ):
        assert telemetry_contract in compact
    assert "MCP calls are denied" in compact_readme
    assert "MCP 호출은 차단" in compact_readme_ko
    assert (
        "Round integrity verification binds the selected prepared-directory bytes or "
        "worktree review digest plus canonical worktree fingerprint"
        in compact_reviewer_routing
    )
    assert (
        "External-state change through a configured MCP tool is prompt-controlled and "
        "reviewer-disclosed" in compact_reviewer_routing
    )
    assert (
        "The prepared-directory digest monitors every prepared regular file"
        in compact_leg_contracts
    )
    assert (
        "the canonical-worktree fingerprint monitors Git HEAD, staged and unstaged "
        "tracked changes, and non-ignored untracked entries" in compact_leg_contracts
    )
    assert (
        "separate selected-member comparisons cover listed source members even when "
        "Git-ignored" in compact_leg_contracts
    )
    assert (
        "Mutations in other Git-ignored worktree paths, paths outside both directories, "
        "and network egress of packet content are neither prevented nor detected"
        in compact_leg_contracts
    )
    assert (
        "a mid-round mutation may affect another leg's reads before final verification"
        in compact_leg_contracts
    )
    assert (
        "invalidates the complete round and discards every verdict"
        in compact_leg_contracts
    )
    assert "1.1.17 or newer" in agy
    assert "AGY 1.1.17 or newer" in reviewer_routing
    assert "--model gemini-3.1-pro-high" in agy
    assert "--effort high" in agy
    assert "--timeout 1800" in agy
    assert "stream-json" in agy
    assert "omits native `--json-schema` in plan mode" in agy
    compact_agy = " ".join(agy.split())
    compact_leg_contracts = " ".join(leg_contracts.split())
    assert "internally inserts `--dangerously-skip-permissions`" in compact_agy
    assert "Callers do not pass this flag" in compact_agy
    assert "`AGY_NO_HEADLESS_AUTOAPPROVE=1`" in compact_agy
    assert "transient global-settings transaction" in compact_agy
    assert "restores the original bytes" in compact_agy
    assert "read-only by intent" in compact_agy
    assert "does not edit user settings" not in compact_agy
    assert "--sandbox read-only" in agy
    assert "--sandbox read-only" in leg_contracts
    assert "uses native `--mode plan`" in compact_agy
    assert "uses native `--mode plan`" in compact_leg_contracts
    for compact in (compact_agy, compact_leg_contracts):
        assert "omits native `--json-schema` in plan mode" in compact
        assert "terminal `response` to be one JSON object" in compact
        assert "optional single Markdown fence" in compact
        assert "strict local `LegVerdict` validation" in compact
        assert (
            "Unmatched, nested, repeated, prose-bearing, and multiple-object "
            "responses are rejected locally" in compact
        )
        assert "no schema-repair provider call" in compact
    assert "transient global-settings transaction" in compact_leg_contracts
    assert "restores the original bytes" in compact_leg_contracts
    assert "read-only by intent" in compact_leg_contracts
    for compact in (compact_agy, compact_leg_contracts):
        normalized = compact.lower()
        assert (
            "formal Google prompt authorizes only AGY native file-read/search tools "
            "for local inspection".lower()
            in normalized
        )
        assert "undecidable uncertainty goes to `open_questions`" in normalized
        assert (
            "explicit deny rules remain the action-namespace enforcement backstop"
            in normalized
        )
        assert "round-integrity mutation detection is separate" in normalized
    assert "Before starting any family" in leg_contracts
    assert "--preflight-only" in leg_contracts
    assert '"provider_started": false' in leg_contracts
    assert "personal Google Sign-In" in compact_leg_contracts
    assert "Business Sign-In for Gemini Enterprise" in compact_leg_contracts
    assert "GE Standard or GE Plus" in compact_leg_contracts
    assert "same packaged AGY wrapper" in compact_leg_contracts
    assert "bin/gemini_wrapper.py" not in leg_contracts
    cross_family_skill = _text(SKILLS / "triad-cross-family-review" / "SKILL.md")
    assert (
        "missing binary, model, or settings transaction stops with zero "
        "provider legs started" in " ".join(cross_family_skill.split())
    )
    for compact in (compact_agy, compact_leg_contracts):
        assert "--expected-permission-mode" not in compact
        assert "--init-preflight" not in compact
    log_assignment = 'TRIAD_DISPATCH_LOG_DIR="$review_log_dir"'
    assert leg_contracts.count(log_assignment) == 3
    assert (
        "\n".join(
            (
                f"{log_assignment} \\",
                'python3 "$toolkit_root/bin/antigravity_wrapper.py" \\',
                '  --prompt-file "$review_prompt_file" \\',
                '  --cwd "$review_shared" \\',
                "  --sandbox read-only \\",
                "  --model gemini-3.1-pro-high \\",
                "  --effort high \\",
                "  --preflight-only \\",
                '  > "$google_preflight_file"',
            )
        )
        in leg_contracts
    )
    provider_commands = (
        (
            "bin/claude_wrapper.py",
            '  --prompt-file "$review_prompt_file" \\',
            '  --cwd "$review_shared" \\',
            "  --model opus \\",
            "  --effort xhigh \\",
            "  --timeout 1800 \\",
            "  --pydantic verdict_schema:LegVerdict \\",
            '  --expected-review-id "$review_id" \\',
            "  --expected-family claude \\",
            '  --expected-content-digest "$review_digest" \\',
            '  > "$claude_result_file"',
        ),
        (
            "bin/antigravity_wrapper.py",
            '  --prompt-file "$review_prompt_file" \\',
            '  --cwd "$review_shared" \\',
            "  --sandbox read-only \\",
            "  --model gemini-3.1-pro-high \\",
            "  --effort high \\",
            "  --timeout 1800 \\",
            "  --pydantic verdict_schema:LegVerdict \\",
            '  --expected-review-id "$review_id" \\',
            "  --expected-family google \\",
            '  --expected-content-digest "$review_digest" \\',
            '  > "$google_result_file"',
        ),
    )
    for wrapper, *options in provider_commands:
        expected = "\n".join(
            (
                f"{log_assignment} \\",
                f'python3 "$toolkit_root/{wrapper}" \\',
                *options,
            )
        )
        assert expected in leg_contracts
    assert "inside that launcher command" in compact_leg_contracts
    assert "Never strip or filter a contaminated result" in compact_leg_contracts
    for family in ("claude", "google", "codex"):
        assert (
            "\n".join(
                (
                    'python3 "$toolkit_root/bin/verdict_schema.py" validate \\',
                    f'  --result-file "${family}_result_file" \\',
                    '  --expected-review-id "$review_id" \\',
                    f"  --expected-family {family} \\",
                    '  --expected-content-digest "$review_digest"',
                )
            )
            in leg_contracts
        )
    assert "reviews only" in claude
    assert "reviews only" in agy
    assert "reviews only" in gemini


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
    assert "Gemini is eligible only when AGY is proven unavailable" not in gemini
    assert "standalone compatibility consult only" in gemini
    assert (
        "same packaged AGY wrapper supports either personal Google Sign-In"
        in leg_contracts
    )


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
    leg_contracts = " ".join(
        _text(
            SKILLS / "triad-cross-family-review" / "references" / "leg-contracts.md"
        ).split()
    )

    assert (
        "A tool attempt in a named denied namespace is also blocked by its matching "
        "deny entry" in leg_contracts
    )
    assert (
        "Other prompt-forbidden actions remain contract obligations"
        not in leg_contracts
    )
    assert "`tool-contract-violation`" in leg_contracts


def test_cross_family_skill_stops_on_packet_workflow_bugs() -> None:
    skill = " ".join(_text(SKILLS / "triad-cross-family-review" / "SKILL.md").split())

    assert "A packet workflow defect invalidates the round" in skill
    assert (
        "fix the skill or tool and its regression test before another dispatch" in skill
    )
    assert "start again from preparation with a fresh review ID" in skill
    assert "Never reuse an earlier review ID" in skill
    assert "Never manually rebuild or alter a packet to bypass the defect" in skill
    assert (
        "If it neither returned a review root nor named an undeletable partial root, "
        "record the failure; there is no root to clean up" in skill
    )
    assert (
        "If it names a partial review root that could not be removed, stop and report "
        "that exact path; do not retry deletion or redispatch" in skill
    )
    assert "If it returned a review root, clean up that returned root" in skill
    assert "After the first or third outcome" in skill


def test_cross_family_skill_cancels_every_sibling_on_first_leg_failure() -> None:
    skill = " ".join(_text(SKILLS / "triad-cross-family-review" / "SKILL.md").split())
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
    convergence = " ".join(
        _text(
            SKILLS / "triad-cross-family-review" / "references" / "convergence.md"
        ).split()
    )

    for text in (skill, leg_contracts, routing, convergence):
        assert "first required-leg failure" in text
        assert "terminate every still-running leg" in text
        assert "discard every current-round verdict" in text
        assert "never continue a sibling merely to collect advisory evidence" in text
    assert (
        "confirm that every exact provider process tree is gone before integrity verification"
        in skill
    )
    assert (
        "repair the infrastructure defect before preparing a fresh review ID" in skill
    )


def test_cross_family_skill_uses_current_task_authority_before_preparing() -> None:
    skill = _text(SKILLS / "triad-cross-family-review" / "SKILL.md")

    authority_rule = (
        "The current owner-supplied task or explicitly designated executable plan "
        "is the execution authority for the round."
    )
    assert "[CHANGELOG.md](../../CHANGELOG.md)" not in skill
    assert "Read only the current release section of" not in skill
    assert "1. **Authorize and bound.**" in skill
    assert authority_rule in skill
    assert "Never invert a retained or rejected release decision in `TASK.md`" in skill
    assert skill.index(authority_rule) < skill.index("Record a fresh review ID")


def test_cross_family_skill_owns_operational_prompts_without_meta_review() -> None:
    skill = _text(SKILLS / "triad-cross-family-review" / "SKILL.md")
    compact = " ".join(skill.split())

    assert "render-worktree" in compact
    assert "project instructions explicitly select worktree-first review" in compact
    assert (
        "task, status, and diff as canonical regular files inside that worktree"
        in compact
    )
    assert (
        "Do not invoke `skill-prompt-review` before or during an operational round"
        in compact
    )
    assert "proceeds directly to provider dispatch" in compact


def test_cross_family_skill_uses_managed_review_workspace_lifecycle() -> None:
    raw_skill = _text(SKILLS / "triad-cross-family-review" / "SKILL.md")
    skill = " ".join(raw_skill.split())
    prompt_contract = "[review prompt contract](references/review-prompt-contract.md)"
    leg_contracts = "[leg contracts](references/leg-contracts.md)"
    reviewer_routing = "[reviewer routing](references/reviewer-routing.md)"
    characterization_marker = (
        "A current task may explicitly authorize a lifecycle characterization "
        "with zero provider legs."
    )
    branch_selector = (
        "A current task authorizes this branch only when it both prohibits provider "
        "dispatch and directs the lifecycle through verify and exact cleanup."
    )
    canonical_prepare_inputs = (
        "Both `--source-root` and `--member-list` inputs must be absolute canonical "
        "no-symlink paths, and `--member-list` must name an existing regular file; "
        "any violation is a workflow failure that invalidates the round and requires "
        "a fresh review ID."
    )

    for subcommand in ("prepare", "manifest", "capture", "render", "verify", "cleanup"):
        assert f"python3 bin/review_round.py {subcommand}" in skill
    assert (
        "Resolve the canonical toolkit root from the canonical realpath of this `SKILL.md`"
        in skill
    )
    assert (
        "never search for or substitute another checkout or installed-cache copy"
        in skill
    )
    assert (
        'python3 bin/review_round.py capture --prepared-dir "$review_shared" '
        '--worktree "$review_worktree" --output "$review_snapshot"'
    ) in skill
    assert "bin/review_round.py prepare" in skill
    assert '--source-root "$review_source_root"' in skill
    assert '--member-list "$review_member_list"' in skill
    assert '--required-members-json "$review_members_json"' in skill
    assert 'manifest --prepared-dir "$review_shared"' in skill
    assert '--expected-root "$review_root"' in skill
    assert canonical_prepare_inputs in skill
    assert (
        "For every JSON-valued lifecycle option, pass the serialized JSON as one "
        "shell argument"
    ) in skill
    assert (
        "pass a placeholder command name before the serialized JSON so zsh assigns "
        "that name to `$0` and the JSON to `$1`" in skill
    )
    assert (
        "Assign `$1` to a task-specific variable and expand that variable double-quoted"
        in skill
    )
    assert (
        "Bind every dynamic path, review ID, and model value to a task-specific shell "
        "variable before invocation" in skill
    )
    assert (
        "never splice nested quote fragments or leave JSON exposed to glob expansion"
        in skill
    )
    assert "Use the exact digest printed by `capture`" in skill
    assert "Do not parse the snapshot JSON to recover or recheck that digest" in skill
    assert skill.index("Record a fresh review ID") < skill.index(
        "bin/review_round.py prepare"
    )
    assert "reserved `triad-review-<review-id>` system-temp namespace" in skill
    assert "creates the root exclusively" in skill
    assert "exact member list from the canonical source root" in skill
    assert (
        "Use the canonical Git worktree root as `--source-root`; it must be the same "
        "canonical worktree root passed to `capture` and `verify`" in skill
    )
    assert "member-list file is the only source-copy IPC" in skill
    assert "`shared/source/product/<member>`" in skill
    assert "no unlisted source member is copied" in skill
    assert (
        "`capture` and `verify` also compare every selected prepared source member with "
        "that worktree before and after worktree fingerprinting" in skill
    )
    assert "Never copy an earlier prepared packet" in skill
    for prior_round_artifact in (
        "task",
        "diff",
        "manifest",
        "snapshot",
        "prompt",
        "status",
        "verdict",
    ):
        assert f"prior-round {prior_round_artifact}" in skill
    assert (
        "Outside `shared/source/product/`, the prepared `shared/` inventory is exactly "
        "`TASK.md`, `REVIEW.diff`, `SOURCE_SHA256SUMS`, and optional `EVIDENCE.md`"
        in skill
    )
    assert "same-ID collision" in skill
    assert "different review IDs remain isolated" in skill
    assert (
        "Record the review ID and returned root in the active `TASK.md` or plan"
        in skill
    )
    assert (
        "Carry the printed digest mechanically through every rendered prompt and every admitted "
        "result" in skill
    )
    assert "results and prompts under the returned review root" in skill
    assert "snapshots and verdicts under that same current root" in skill
    assert '`TRIAD_DISPATCH_LOG_DIR="$review_log_dir"`' in skill
    assert "bin/review_round.py cleanup" in skill
    assert (
        "Normal cleanup occurs only after final integrity verification and adjudication"
        in skill
    )
    assert "compare the expected root" in skill
    assert "first cleanup result reports `removed: true`" in skill
    assert "including a shell invocation that fails before Python starts" in skill
    assert "never retry a corrected command under the same ID" in skill
    assert "confirm that exact root is absent" in skill
    assert "other managed sibling roots remain untouched" in skill
    assert "strictly more than 30 days" in skill
    assert (
        "Prepare a durable handoff directly at its owner-approved destination" in skill
    )
    assert prompt_contract in raw_skill
    assert leg_contracts in raw_skill
    assert reviewer_routing in raw_skill
    assert raw_skill.index(prompt_contract) < raw_skill.index(reviewer_routing)
    assert raw_skill.index(leg_contracts) < raw_skill.index(reviewer_routing)
    assert characterization_marker in skill
    assert branch_selector in skill
    assert skill.index(characterization_marker) < skill.index(branch_selector)
    assert skill.index(branch_selector) < skill.index(reviewer_routing)
    assert (
        "render every requested prompt with packaged "
        "`python3 bin/review_round.py render`"
    ) in skill
    assert "This branch is not a review round or gate" in skill
    assert (
        "make no review-admission, convergence, adjudication, or gate-passage claim"
        in skill
    )
    assert (
        "use supported exact cleanup, and return without entering provider dispatch"
        in skill
    )
    assert (
        "For prepared-directory review rounds, after all required legs terminate, run "
        '`python3 bin/review_round.py verify --prepared-dir "$review_shared" '
        '--worktree "$review_worktree" --snapshot "$review_snapshot"`'
    ) in skill
    assert (
        "the task-authorized zero-provider characterization runs "
        "that same command through the Flow step 4 branch"
    ) in skill
    assert "For review rounds, the gate passes only when all required families" in skill
    assert (
        "For review rounds: Normal cleanup occurs only after final integrity" in skill
    )
    assert (
        "the task-authorized zero-provider characterization uses the Flow step 4 "
        "verify-and-exact-cleanup branch"
    ) in skill
    assert (
        "Do not modify the canonical worktree until every required leg has terminated"
    ) in skill
    assert "The prepared-directory route requires `ROUND_INTEGRITY_OK`" in skill
    assert (
        "An explicitly selected worktree-first round instead performs the exact "
        "project-required post-review fingerprint check"
    ) in skill


def test_cross_family_skill_requires_the_review_source_manifest() -> None:
    skill = " ".join(_text(SKILLS / "triad-cross-family-review" / "SKILL.md").split())
    prompt_contract = " ".join(
        _text(
            SKILLS
            / "triad-cross-family-review"
            / "references"
            / "review-prompt-contract.md"
        ).split()
    )
    release_plan = " ".join(
        _text(
            ROOT
            / "docs"
            / "superpowers"
            / "plans"
            / "2026-08-05-triad-0.2.533-owner-decisions-and-release.md"
        ).split()
    )
    changelog = " ".join(_text(ROOT / "CHANGELOG.md").split())

    assert "`TASK.md`, `REVIEW.diff`, and optional `EVIDENCE.md` only" in skill
    fixed_members = (
        "`TASK.md`, `REVIEW.diff`, optional `EVIDENCE.md`, and `SOURCE_SHA256SUMS`"
    )
    assert fixed_members in prompt_contract
    assert fixed_members in release_plan
    member_rule = "sorted JSON array of non-empty normalized POSIX relative paths"
    assert member_rule in skill
    assert (
        'python3 bin/review_round.py manifest --prepared-dir "$review_shared"' in skill
    )
    inventory_rule = "sorted JSON array of exact decoded `{path, sha256}` objects"
    assert inventory_rule in skill
    assert inventory_rule in prompt_contract
    assert inventory_rule in release_plan
    assert inventory_rule in changelog
    manifest_coverage_rule = (
        "The manifest covers every regular file in the prepared directory except "
        "the root `SOURCE_SHA256SUMS` manifest itself"
    )
    assert manifest_coverage_rule in skill
    assert manifest_coverage_rule in prompt_contract
    assert (
        '"affected_surfaces_inspected": ["source/product/bin/review_round.py", '
        '"source/product/skills/triad-cross-family-review/SKILL.md"]' in prompt_contract
    )
    metadata_rule = (
        "Every rendered prompt carries dynamic values only in one canonical "
        "`Review metadata: ` JSON record"
    )
    assert metadata_rule in skill
    assert metadata_rule in prompt_contract
    assert metadata_rule in release_plan
    assert metadata_rule in changelog
    binding_rule = (
        "Set `review_id`, `family`, and `content_digest` exactly to "
        "`metadata.review_id`, `metadata.family`, and `metadata.content_digest`"
    )
    assert binding_rule in prompt_contract
    assert (
        "This workflow prepares `source/product/` from the canonical worktree root"
        in prompt_contract
    )
    assert (
        "Do not ask how to proceed, omit the verdict, wrap JSON in prose"
        in prompt_contract
    )
    for placeholder in (
        '"review_id": "<metadata.review_id>"',
        '"family": "<metadata.family>"',
        '"content_digest": "<metadata.content_digest>"',
    ):
        assert placeholder in prompt_contract


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
        ),
        "README.ko.md": (
            "native AGY CLI 로그인",
            "`--sandbox read-only`",
            "일시적 global-settings transaction",
            "원래 바이트를 복원",
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
        ),
        "README.ko.md": (
            "Native provider permission을 그대로 상속합니다",
            "TRIAD는 permission mode를 선택하거나 override하지",
            "provider permission과 project trust policy는 native 설정을 유지합니다",
            "Permission 선택은 provider/user/project에 남습니다",
            "경계는 provider/user/project가 선택한 permission",
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
    assert "native AGY CLI sign-in" in compact_routing
    assert "personal Google Sign-In" in compact_routing
    assert "Business Sign-In for Gemini Enterprise" in compact_routing
    assert (
        "never signs in, changes the active account, or falls back between "
        "authentication classes" in compact_routing
    )
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
    assert "--dangerously-skip-permissions" not in other_wrappers


def test_provider_wrappers_are_packaged_as_executables() -> None:
    for name in (
        "antigravity_wrapper.py",
        "claude_wrapper.py",
        "gemini_wrapper.py",
    ):
        mode = (ROOT / "bin" / name).stat().st_mode
        assert mode & stat.S_IXUSR, name


def test_distribution_documents_fresh_process_acceptance() -> None:
    readme = _text(ROOT / "README.md")
    skill = _text(SKILLS / "triad-cross-family-review" / "SKILL.md")

    assert "session after install or update" in readme
    assert "packaged manifest and skill bytes" in skill
    assert "exact current marker" in skill
