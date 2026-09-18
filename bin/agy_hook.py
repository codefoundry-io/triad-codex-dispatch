#!/usr/bin/env python3
"""Offline AGY name allowlist; configuration output is always disabled."""
from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path


MAX_INPUT_BYTES = 1024 * 1024
READ_TOOLS = frozenset({
    "view_file", "grep_search", "list_dir", "find_by_name",
    "search_web", "read_url_content",
})


def decide(payload: object) -> dict[str, str]:
    tool = payload.get("toolCall") if isinstance(payload, dict) else None
    allowed = (
        isinstance(tool, dict)
        and isinstance(tool.get("name"), str)
        and isinstance(tool.get("args"), dict)
        and tool["name"] in READ_TOOLS
    )
    return {
        "decision": "allow" if allowed else "deny",
        "reason": "Listed read/search tool." if allowed else "Invalid or unlisted tool request.",
    }


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate member")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("non-JSON numeric constant")


def handle(raw: bytes) -> dict[str, str]:
    if len(raw) > MAX_INPUT_BYTES:
        return decide(None)
    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                             parse_constant=_reject_constant)
    except (ValueError, RecursionError):
        return decide(None)
    return decide(payload)


def render_disabled_config(script_path: Path) -> dict:
    return {"triad-readonly-allowlist": {
        "enabled": False,
        "PreToolUse": [{"matcher": "*", "hooks": [{
            "type": "command",
            "command": shlex.join(["python3", str(script_path.resolve())]),
            "timeout": 5,
        }]}],
    }}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-config", action="store_true",
                        help="print disabled configuration without writing or activating it")
    args = parser.parse_args()
    result = (render_disabled_config(Path(__file__)) if args.render_config
              else handle(sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)))
    print(json.dumps(result, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
