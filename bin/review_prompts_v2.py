"""Render the four exact shared clause files for B's explicit v2 review route."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import review_round
from validate_v2 import _json
from verdict_v2 import bound_verdict

BUNDLE_ROOT = Path(__file__).resolve().parents[1] / "prompts/review-v2"
SOURCE_COMMIT = "6bef14c0c42a13678594e8f2f039d1793b7cb127"
PAYLOADS = ("common-clauses.md", "leg-claude.md", "leg-codex.md", "leg-google.md")
_A_ONLY = {"claude-output-shape-notice", "claude-output-integrity", "google-a-hook-audit"}


def load_bundle() -> dict[str, str]:
    read = review_round._canonical_regular_file_bytes
    try:
        manifest = _json(read(BUNDLE_ROOT / "source-manifest.json", "v2 prompt manifest"))
        if (not isinstance(manifest, dict)
                or set(manifest) != {"source_repository", "source_commit", "status", "sha256"}
                or manifest["source_repository"] != "https://github.com/codefoundry-io/triad-dispatch-spec"
                or manifest["source_commit"] != SOURCE_COMMIT or manifest["status"] != "candidate"
                or not isinstance(manifest["sha256"], dict) or set(manifest["sha256"]) != set(PAYLOADS)):
            raise ValueError("invalid v2 prompt provenance")
        output = {}
        for name in PAYLOADS:
            raw = read(BUNDLE_ROOT / name, "v2 shared prompt")
            if hashlib.sha256(raw).hexdigest() != manifest["sha256"][name]:
                raise ValueError("v2 prompt digest mismatch: " + name)
            output[name] = raw.decode("utf-8")
        return output
    except (OSError, UnicodeError) as error:
        raise ValueError("unreadable v2 prompt bundle") from error


def _clauses(text: str) -> dict[str, str]:
    # This is the fixed published Markdown clause format, not a Markdown engine.
    result = {}
    for section in re.split(r"^## ", text, flags=re.MULTILINE)[1:]:
        name = section.split(None, 1)[0]
        blocks = re.findall(r"^```text\n(.*?)^```$", section, re.MULTILINE | re.DOTALL)
        if blocks:
            if len(blocks) != 1 or name in result:
                raise ValueError("ambiguous shared clause: " + name)
            result[name] = blocks[0].rstrip("\n")
    return result


def _data_fence(value: str) -> str:
    # JSON quoting preserves the input and prevents injected metadata lines.
    length = max([2, *(len(match) for match in re.findall(r"`+", value))]) + 1
    fence = "`" * length
    return fence + "text\n" + json.dumps(value, ensure_ascii=True) + "\n" + fence


def render_prompt(*, expected: dict, worktree: Path, brief_file: Path,
                  packet_files: list[Path], diff_file: Path, objective: str,
                  criteria: list[str], approved_boundary: list[str], residual: str = "",
                  google_preflight_sha256: str | None = None) -> str:
    model = bound_verdict(expected)
    bundle = load_bundle()
    root = review_round._canonical_directory(worktree, "v2 review worktree")
    for path in packet_files:
        review_round._canonical_regular_file_bytes(path, "bound v2 packet file")
    if (brief_file not in packet_files or diff_file not in packet_files
            or len(set(packet_files)) != len(packet_files)):
        raise ValueError("brief and diff must be unique bound packet inputs")
    if (not isinstance(objective, str) or not objective.strip() or not isinstance(residual, str)
            or any(not isinstance(values, list) or not values
                   or any(not isinstance(value, str) or not value.strip() for value in values)
                   for values in (criteria, approved_boundary))):
        raise ValueError("v2 objective, criteria and approved boundary are required")
    metadata = dict(expected)
    if expected["family"] == "google":
        if not isinstance(google_preflight_sha256, str) or re.fullmatch(r"[a-f0-9]{64}", google_preflight_sha256) is None:
            raise ValueError("Google v2 prompt requires its preflight digest")
        metadata["google_preflight_receipt_sha256"] = google_preflight_sha256
    elif google_preflight_sha256 is not None:
        raise ValueError("non-Google prompt cannot own a Google preflight")
    common = _clauses(bundle["common-clauses.md"])
    leg_text = bundle[f"leg-{expected['family']}.md"]
    leg = _clauses(leg_text)
    order = re.findall(r"^\d+\. ([\w:-]+)", leg_text, re.MULTILINE)
    pieces = []
    for name in order:
        if name in _A_ONLY:
            continue
        try:
            pieces.append(common[name.removeprefix("common:")] if name.startswith("common:") else leg[name])
        except KeyError as error:
            raise ValueError("missing ordered shared clause") from error
    replacements = {
        "worktree": str(root), "brief-file": str(brief_file),
        "gated-patch-file": str(diff_file), "packet-files": json.dumps([str(path) for path in packet_files]),
        "review-id": expected["review_id"], "content-digest": expected["content_digest"],
        "leg-name": expected["leg_name"], "attempt": str(expected["attempt"]),
        "google-route": expected["route"] or "null",
    }
    clauses = re.sub(r"<(" + "|".join(replacements) + r")>",
                     lambda match: replacements[match[1]], "\n\n".join(pieces))
    framing = {"objective": objective, "criteria": criteria, "approved_boundary": approved_boundary}
    return ("Review v2 metadata: " + json.dumps(metadata, sort_keys=True, separators=(",", ":"))
            + "\n\n" + clauses + "\n\nBound review scope:\n" + json.dumps(framing, ensure_ascii=True)
            + "\n\n" + common["data-fence-caveat"] + "\nPrior findings and rebuttal evidence:\n"
            + _data_fence(residual) + "\n\nComplete authoritative output schema:\n"
            + json.dumps(model.model_json_schema(), sort_keys=True) + "\n")
