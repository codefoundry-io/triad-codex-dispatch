#!/usr/bin/env python3
"""Thin CLI over `_common.apply_classifier_patch` — the owner-run applier.

The fresh native proposal-only child returns a structured patch proposal. The
leader stores only that proposal as a UTF-8 JSON file, and the owner passes the
file plus bootstrap's install-resolved classifier path to this command from
their normal terminal. This is the single deterministic, validated, no-provider
write path to the classifier extension JSON.

Usage:
  python3 apply_patch.py --cli <name> --classifier-file <absolute-path> < proposal.json
  python3 apply_patch.py --cli <name> --classifier-file <absolute-path> \
      --proposal-file <path>

Proposal shape (see apply_classifier_patch):
  {"classification": <enum>, "reason": <str>,
   "vendor_exit_code": <int>            # OR
   "pattern_list": <NAME>, "substring": <str>}

Exit codes:
  0  applied
  3  invalid proposal (ValueError) or bad input (arg / JSON parse) — file untouched
"""
from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path

from _common import apply_classifier_patch

EXIT_OK = 0
EXIT_INVALID = 3


def _validated_classifier_path(raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise ValueError(f"classifier file must be absolute: {path}")
    if ".." in path.parts:
        raise ValueError(f"classifier path must not contain parent traversal: {path}")

    current = Path(path.anchor)
    for index, part in enumerate(path.parts[1:], start=1):
        current /= part
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            break
        if stat.S_ISLNK(info.st_mode):
            raise ValueError(f"classifier path must not contain symlinks: {current}")
        if index < len(path.parts) - 1 and not stat.S_ISDIR(info.st_mode):
            raise ValueError(f"classifier ancestor is not a directory: {current}")
        if index == len(path.parts) - 1 and not stat.S_ISREG(info.st_mode):
            raise ValueError(f"classifier file is not regular: {current}")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply a validated classifier patch proposal.")
    ap.add_argument("--cli", required=True, help="Target CLI name (codex/gemini/claude/antigravity).")
    ap.add_argument(
        "--classifier-file",
        required=True,
        help="Install-resolved absolute classifier extension path.",
    )
    ap.add_argument(
        "--proposal-file",
        default=None,
        help="Read the proposal JSON from this file instead of stdin.",
    )
    args = ap.parse_args()

    try:
        classifier_path = _validated_classifier_path(args.classifier_file)
    except ValueError as e:
        print(f"[apply_patch] rejected: {e}", file=sys.stderr)
        return EXIT_INVALID

    try:
        if args.proposal_file:
            with open(args.proposal_file, "r", encoding="utf-8") as f:
                raw = f.read()
        else:
            raw = sys.stdin.read()
    except OSError as e:
        print(f"[apply_patch] cannot read proposal: {e}", file=sys.stderr)
        return EXIT_INVALID

    try:
        proposal = json.loads(raw)
    except ValueError as e:
        print(f"[apply_patch] invalid proposal JSON: {e}", file=sys.stderr)
        return EXIT_INVALID

    if not isinstance(proposal, dict):
        print("[apply_patch] proposal must be a JSON object", file=sys.stderr)
        return EXIT_INVALID

    try:
        result = apply_classifier_patch(
            args.cli,
            proposal,
            extension_path=classifier_path,
        )
    except ValueError as e:
        print(f"[apply_patch] rejected: {e}", file=sys.stderr)
        return EXIT_INVALID

    print(result)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
