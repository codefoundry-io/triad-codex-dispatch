#!/usr/bin/env python3
"""Explicit offline v2 validation; existing dispatch/gate routes remain legacy."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from referencing import Registry
from referencing.exceptions import Unresolvable

from verdict_schema import _read_canonical_regular_file, _reject_duplicate_members


CONTRACT_ROOT = Path(__file__).resolve().parents[1] / "contracts"
SOURCE_REPOSITORY = "https://github.com/codefoundry-io/triad-dispatch-spec"
SOURCE_COMMIT = "055204c83e57bf87eeac5b2422f2b17340f7c53b"
PAYLOADS = ("leg-verdict.schema.json", "review-legs.schema.json", "receipt-fields.json")
BINDING_FIELDS = ("review_id", "family", "content_digest", "leg_name", "attempt", "route")


def _invalid_constant(value: str) -> None:
    raise ValueError("non-JSON numeric constant")


def _json(raw: str | bytes):
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    # The legacy hook checks every original object but deliberately discards it.
    json.loads(raw, object_pairs_hook=_reject_duplicate_members,
               parse_constant=_invalid_constant)
    return json.loads(raw, parse_constant=_invalid_constant)


def load_contracts() -> dict:
    """Read the fixed candidate bundle; hashes establish integrity, not a signature."""
    try:
        manifest = _json(_read_canonical_regular_file(CONTRACT_ROOT / "source-manifest.json"))
    except (OSError, ValueError):
        raise ValueError("invalid candidate contract: source-manifest.json") from None
    if (
        not isinstance(manifest, dict)
        or set(manifest) != {"source_repository", "source_commit", "status", "sha256"}
        or manifest["source_repository"] != SOURCE_REPOSITORY
        or manifest["source_commit"] != SOURCE_COMMIT
        or manifest["status"] != "candidate"
        or not isinstance(manifest["sha256"], dict)
        or set(manifest["sha256"]) != set(PAYLOADS)
    ):
        raise ValueError("invalid candidate source manifest")
    schemas = {}
    for name in PAYLOADS:
        try:
            raw = _read_canonical_regular_file(CONTRACT_ROOT / name)
        except (OSError, ValueError):
            raise ValueError(f"unreadable candidate contract: {name}") from None
        if hashlib.sha256(raw).hexdigest() != manifest["sha256"][name]:
            raise ValueError(f"contract digest mismatch: {name}")
        try:
            schema = _json(raw)
            if not isinstance(schema, dict) or schema.get("$schema") != Draft202012Validator.META_SCHEMA["$id"]:
                raise ValueError("unsupported schema dialect")
            Draft202012Validator.check_schema(schema)
        except (ValueError, SchemaError):
            raise ValueError(f"invalid candidate contract: {name}") from None
        schemas[name] = schema
    return schemas


def validate_verdict(raw: str | bytes, *, expected: dict) -> dict:
    """Validate original JSON and all invocation bindings without rewriting values."""
    try:
        data = _json(raw)
        schema = load_contracts()["leg-verdict.schema.json"]
        # An explicit empty Registry refuses retrieval, including file/HTTP URIs.
        Draft202012Validator(schema, registry=Registry()).validate(data)
        binding_schema = {
            "type": "object", "additionalProperties": False,
            "required": list(BINDING_FIELDS),
            "properties": {name: schema["properties"][name] for name in BINDING_FIELDS},
        }
        if not Draft202012Validator(binding_schema, registry=Registry()).is_valid(expected):
            raise ValueError("invalid expected binding")
        for name in BINDING_FIELDS:
            if data[name] != expected[name]:
                raise ValueError(f"binding mismatch: {name}")
        return data
    except ValidationError as error:
        # Report location/constraint, not the possibly sensitive failing value.
        raise ValueError(f"schema violation at {error.json_path}: {error.validator}") from None
    except Unresolvable:
        raise ValueError("external or unresolved schema reference") from None
    except RecursionError:
        raise ValueError("JSON/schema nesting exceeds decoder limit") from None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--result-file", type=Path, required=True)
    validate.add_argument("--expected-review-id", required=True)
    validate.add_argument("--expected-family", choices=("claude", "codex", "google"), required=True)
    validate.add_argument("--expected-content-digest", required=True)
    validate.add_argument("--expected-leg-name", required=True)
    validate.add_argument("--expected-attempt", type=int, required=True)
    validate.add_argument("--expected-route", choices=("null", "agy", "gemini"), required=True)
    args = parser.parse_args(argv)
    expected = {name: getattr(args, "expected_" + name) for name in BINDING_FIELDS}
    if expected["route"] == "null":
        expected["route"] = None
    try:
        result = validate_verdict(_read_canonical_regular_file(args.result_file), expected=expected)
    except (OSError, ValueError) as error:
        print(f"invalid v2 LegVerdict: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
