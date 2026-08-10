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
    assert manifest["version"] == "0.2.533"
    assert manifest["skills"] == "./skills/"
    prompts = "\n".join(manifest["interface"]["defaultPrompt"])
    assert "triad-cross-family-review" in prompts
    assert "same complete focused directory" in prompts
    assert "batched-full-coverage" not in prompts


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
        SKILLS
        / "triad-cross-family-review"
        / "references"
        / "leg-contracts.md"
    )
    prompt_contract = _text(
        SKILLS
        / "triad-cross-family-review"
        / "references"
        / "review-prompt-contract.md"
    )
    reviewer_routing = _text(
        SKILLS
        / "triad-cross-family-review"
        / "references"
        / "reviewer-routing.md"
    )
    agy = _text(SKILLS / "triad-antigravity-dispatch" / "SKILL.md")
    gemini = _text(SKILLS / "triad-gemini-dispatch" / "SKILL.md")
    compact_leg_contracts = " ".join(leg_contracts.split())
    compact_prompt_contract = " ".join(prompt_contract.split())
    compact_reviewer_routing = " ".join(reviewer_routing.split())

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
        assert "Existing user permission settings continue to govern MCP calls" in compact
        assert "Approved official-web reads through read-only MCP tools remain available" in compact
        assert "Do not edit files, change external state, or execute candidate code" in compact
    assert (
        "Round integrity verification binds prepared-directory and canonical worktree bytes only"
        in compact_reviewer_routing
    )
    assert (
        "External-state change through a configured MCP tool is prompt-controlled and "
        "reviewer-disclosed"
        in compact_reviewer_routing
    )
    assert (
        "The prepared-directory digest and canonical-worktree fingerprint monitor "
        "exactly those two surfaces"
        in compact_leg_contracts
    )
    assert (
        "mutation outside both surfaces and network egress of packet content are "
        "neither prevented nor detected by those fingerprints"
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
    assert "1.1.10 or newer" in agy
    assert "--model gemini-3.1-pro-high" in agy
    assert "--effort high" in agy
    assert "--timeout 1800" in agy
    assert "stream-json" in agy and "json-schema" in agy
    for text in (agy, leg_contracts):
        compact = " ".join(text.split())
        assert "internally inserts `--dangerously-skip-permissions`" in compact
        assert "Callers do not pass this flag" in compact
        assert "does not edit user settings" in compact
        assert "command-specific allowlist" in compact
        assert "--expected-permission-mode" not in compact
        assert "--init-preflight" not in compact
    log_assignment = 'TRIAD_DISPATCH_LOG_DIR="<returned-root>/results/_logs"'
    assert leg_contracts.count(log_assignment) == 3
    provider_commands = (
        (
            "bin/claude_wrapper.py",
            '  --prompt-file "<leader-owned-prompt>" \\',
            '  --cwd "<prepared-directory>" \\',
            "  --model opus \\",
            "  --effort xhigh \\",
            "  --timeout 1800 \\",
            "  --pydantic verdict_schema:LegVerdict \\",
            '  > "<returned-root>/results/claude.json"',
        ),
        (
            "bin/antigravity_wrapper.py",
            '  --prompt-file "<leader-owned-prompt>" \\',
            '  --cwd "<prepared-directory>" \\',
            "  --model gemini-3.1-pro-high \\",
            "  --effort high \\",
            "  --timeout 1800 \\",
            "  --pydantic verdict_schema:LegVerdict \\",
            '  > "<returned-root>/results/google.json"',
        ),
        (
            "bin/gemini_wrapper.py",
            '  --prompt-file "<leader-owned-prompt>" \\',
            '  --cwd "<prepared-directory>" \\',
            '  --model "<owner-authorized-gemini-model>" \\',
            "  --pydantic verdict_schema:LegVerdict \\",
            '  > "<returned-root>/results/google.json"',
        ),
    )
    for wrapper, *options in provider_commands:
        expected = "\n".join(
            (
                f"{log_assignment} \\",
                f'python3 "<toolkit>/{wrapper}" \\',
                *options,
            )
        )
        assert expected in leg_contracts
    assert "inside that launcher command" in compact_leg_contracts
    assert "Never strip or filter a contaminated result" in compact_leg_contracts
    for family in ("claude", "google", "codex"):
        assert "\n".join(
            (
                'python3 "<toolkit>/bin/verdict_schema.py" validate \\',
                f'  --result-file "<{family}-result>" \\',
                '  --expected-review-id "<review-id>" \\',
                f"  --expected-family {family} \\",
                '  --expected-content-digest "<digest>"',
            )
        ) in leg_contracts
    assert "reviews only" in claude
    assert "reviews only" in agy
    assert "reviews only" in gemini


def test_cross_family_skill_stops_on_packet_workflow_bugs() -> None:
    skill = " ".join(
        _text(SKILLS / "triad-cross-family-review" / "SKILL.md").split()
    )

    assert "A packet workflow defect invalidates the round" in skill
    assert "fix the skill or tool and its regression test before another dispatch" in skill
    assert "start again from preparation with a fresh review ID" in skill
    assert "Never reuse an earlier review ID" in skill
    assert "Never manually rebuild or alter a packet to bypass the defect" in skill
    assert (
        "When `prepare` fails before returning a review root, record the failure and "
        "restart from preparation with a fresh review ID; no root exists to clean up"
        in skill
    )
    assert "Otherwise clean up the returned root" in skill


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
        'python3 bin/review_round.py capture --prepared-dir "<shared>" '
        '--worktree "<canonical-worktree>" '
        '--output "<returned-root>/results/snapshot.json"'
    ) in skill
    assert "bin/review_round.py prepare" in skill
    assert '--source-root "<root>"' in skill
    assert '--member-list "<file>"' in skill
    assert '--required-members-json "$review_members_json"' in skill
    assert 'manifest --prepared-dir "<shared>"' in skill
    assert '--expected-root "<returned-root>"' in skill
    assert canonical_prepare_inputs in skill
    assert (
        "For every JSON-valued lifecycle option, pass the serialized JSON as one "
        "shell argument"
    ) in skill
    assert (
        "pass a placeholder command name before the serialized JSON so zsh assigns "
        "that name to `$0` and the JSON to `$1`"
        in skill
    )
    assert (
        "Assign `$1` to a task-specific variable and expand that variable double-quoted"
        in skill
    )
    assert "never splice nested quote fragments or leave JSON exposed to glob expansion" in skill
    assert "Use the exact digest printed by `capture`" in skill
    assert "Do not parse the snapshot JSON to recover or recheck that digest" in skill
    assert skill.index("Record a fresh review ID") < skill.index("bin/review_round.py prepare")
    assert "reserved `triad-review-<review-id>` system-temp namespace" in skill
    assert "creates the root exclusively" in skill
    assert "exact member list from the canonical source root" in skill
    assert "member-list file is the only source-copy IPC" in skill
    assert "`shared/source/product/<member>`" in skill
    assert "no unlisted source member is copied" in skill
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
    assert "Record the review ID and returned root in the active `TASK.md` or plan" in skill
    assert (
        "Carry the printed digest mechanically through every rendered prompt and every admitted "
        "result"
        in skill
    )
    assert "results and prompts under the returned review root" in skill
    assert "snapshots and verdicts under that same current root" in skill
    assert '`TRIAD_DISPATCH_LOG_DIR="<returned-root>/results/_logs"`' in skill
    assert "bin/review_round.py cleanup" in skill
    assert "Normal cleanup occurs only after final integrity verification and adjudication" in skill
    assert "compare the expected root" in skill
    assert "first cleanup result reports `removed: true`" in skill
    assert "including a shell invocation that fails before Python starts" in skill
    assert "never retry a corrected command under the same ID" in skill
    assert "confirm that exact root is absent" in skill
    assert "other managed sibling roots remain untouched" in skill
    assert "strictly more than 30 days" in skill
    assert "Prepare a durable handoff directly at its owner-approved destination" in skill
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
    assert "make no review-admission, convergence, adjudication, or gate-passage claim" in skill
    assert "use supported exact cleanup, and return without entering provider dispatch" in skill
    assert (
        "For review rounds, after all required legs terminate, run "
        "`python3 bin/review_round.py verify`"
    ) in skill
    assert (
        "the task-authorized zero-provider characterization runs "
        "`python3 bin/review_round.py verify` through the Flow step 4 branch"
    ) in skill
    assert "For review rounds, the gate passes only when all required families" in skill
    assert "For review rounds: Normal cleanup occurs only after final integrity" in skill
    assert (
        "the task-authorized zero-provider characterization uses the Flow step 4 "
        "verify-and-exact-cleanup branch"
    ) in skill
    assert (
        "Do not modify the canonical worktree until every required leg has terminated and "
        "verify prints `ROUND_INTEGRITY_OK`"
    ) in skill


def test_cross_family_skill_requires_the_review_source_manifest() -> None:
    skill = " ".join(
        _text(SKILLS / "triad-cross-family-review" / "SKILL.md").split()
    )
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
        "`TASK.md`, `REVIEW.diff`, optional `EVIDENCE.md`, and "
        "`SOURCE_SHA256SUMS`"
    )
    assert fixed_members in prompt_contract
    assert fixed_members in release_plan
    member_rule = "sorted JSON array of non-empty normalized POSIX relative paths"
    assert member_rule in skill
    assert 'python3 bin/review_round.py manifest --prepared-dir "<shared>"' in skill
    inventory_rule = "sorted JSON array of exact decoded `{path, sha256}` objects"
    assert inventory_rule in skill
    assert inventory_rule in prompt_contract
    assert inventory_rule in release_plan
    assert inventory_rule in changelog
    manifest_coverage_rule = (
        "The manifest covers every regular file in the prepared directory except "
        "`SOURCE_SHA256SUMS` itself"
    )
    assert manifest_coverage_rule in skill
    assert manifest_coverage_rule in prompt_contract
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
        ROOT / "skills" / "triad-cross-family-review" / "references" / "fresh-codex-formal-review.md",
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
            "deliberately select AGY's native headless auto-approval mode `always-proceed`",
            "replacing `request-review` for that child",
            "approved internal `--dangerously-skip-permissions` flag",
            "not caller-supplied",
            "does not change stored or global user/project settings",
            "does not install permission profiles or command rules",
            "does not select a sandbox",
            "does not change project-trust configuration",
            "does not restrict installed CLI, MCP, read, or search tools",
        ),
        "README.ko.md": (
            "승인된 내부 `--dangerously-skip-permissions` flag",
            "`request-review`를 대체",
            "AGY native headless auto-approval `always-proceed`를 의도적으로 선택",
            "caller-supplied가 아닙니다",
            "stored/global user 또는 project setting을 변경하지",
            "permission profile이나 command rule을 설치하지",
            "sandbox를 선택하지",
            "project-trust configuration을 변경하지",
            "installed CLI, MCP, read, search tool을 제한하지",
        ),
        "SECURITY.md": (
            "deliberately select AGY's native headless auto-approval mode `always-proceed`",
            "replacing `request-review` for that child",
            "approved internal `--dangerously-skip-permissions` flag",
            "not caller-supplied",
            "does not change stored or global user/project settings",
            "does not install permission profiles or command rules",
            "does not select a sandbox",
            "does not change project-trust configuration",
            "does not restrict installed CLI, MCP, read, or search tools",
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
        "skills/triad-cross-family-review/references/reviewer-routing.md": (
            "Native provider and project permissions remain in force.",
        ),
    }
    for name, claims in contradictory_claims.items():
        compact = " ".join(public_docs[name].split())
        for claim in claims:
            assert claim not in compact, (name, claim)
    routing = public_docs[
        "skills/triad-cross-family-review/references/reviewer-routing.md"
    ]
    assert "documented packaged AGY child `always-proceed` selection" in routing
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


def test_current_release_docs_bind_superseded_agy_route_and_current_review_boundary() -> None:
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
    assert "Preserves the owner-approved prepared-directory digest algorithm" in changelog
    assert "`git hash-object` replacement proposal is not adopted" in changelog
    assert "Implements the unique-ID system-temp lifecycle guarantee" in changelog
    assert "the exact digest printed by `capture` the only supported digest handoff" in changelog
    assert "rejects non-regular member-list nodes before reading" in changelog
    assert "maps prepared-file I/O failures to the controlled lifecycle error" in changelog
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
    assert "docs/references/repair-protocol.md" in handoff
    assert "stale 80-file count" in handoff


def test_wrapper_sources_have_no_retired_permission_or_packet_transport() -> None:
    antigravity = _text(ROOT / "bin" / "antigravity_wrapper.py")
    other_wrappers = "\n".join(
        _text(ROOT / "bin" / name)
        for name in ("claude_wrapper.py", "gemini_wrapper.py")
    )
    for stale in (
        "--sandbox",
        "--sealed-packet-root",
        "--expected-packet-sha256",
        "run_via_pty",
    ):
        assert stale not in antigravity
        assert stale not in other_wrappers
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
