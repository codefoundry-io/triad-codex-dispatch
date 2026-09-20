"""Resolve project review entries without starting a provider or claiming support."""
from __future__ import annotations

import copy
import stat
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from referencing import Registry

from validate_v2 import _json, load_contracts
from verdict_schema import _read_canonical_regular_file


DEFAULTS = Path(__file__).resolve().parents[1] / "contracts/review-legs.default.json"


def _validate(document: object, schema: dict, *, resolved: bool) -> None:
    selected = ({"$defs": schema["$defs"], "$ref": "#/$defs/resolvedRoster"}
                if resolved else schema)
    Draft202012Validator(selected, registry=Registry()).validate(document)
    names = [entry["name"] for entry in document["legs"]]
    if len(names) != len(set(names)):
        raise ValueError("duplicate leg name")
    for entry in document["legs"]:
        for provider in ("claude", "codex", "agy", "gemini"):
            for value in entry.get(provider, {}).values():
                if isinstance(value, str) and any(token in value for token in ("<", ">", "${", "{{", "}}")):
                    raise ValueError("unresolved adapter placeholder")


def _merge(base: dict, override: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in override.items():
        result[key] = (_merge(result[key], value)
                       if isinstance(result.get(key), dict) and isinstance(value, dict)
                       else copy.deepcopy(value))
    return result


def resolve_roster(project_root: Path) -> dict:
    """Return resolved data and its display metadata; execution validates capabilities."""
    try:
        root = project_root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("project root must be an existing directory")
        schema = load_contracts()["review-legs.schema.json"]
        defaults = _json(_read_canonical_regular_file(DEFAULTS))
        _validate(defaults, schema, resolved=True)
        if (len(defaults["legs"]) != 3
                or {leg["vendor"] for leg in defaults["legs"]} != {"claude", "codex", "google"}
                or not all(leg["enabled"] for leg in defaults["legs"])):
            raise ValueError("shipped defaults must enable exactly one entry per family")
        config = root / ".agents" / "triad-review-legs.json"
        configured = False
        try:
            directory = config.parent.lstat()
        except FileNotFoundError:
            pass
        else:
            if not stat.S_ISDIR(directory.st_mode):
                raise ValueError("project .agents must be a real directory")
            try:
                config.lstat()
            except FileNotFoundError:
                pass
            else:
                configured = True
        roster = copy.deepcopy(defaults)
        if configured:
            override = _json(_read_canonical_regular_file(config))
            _validate(override, schema, resolved=False)
            by_name = {entry["name"]: entry for entry in roster["legs"]}
            for entry in override["legs"]:
                by_name[entry["name"]] = _merge(by_name.get(entry["name"], {}), entry)
            roster["legs"] = list(by_name.values())
            if "_comment" in override:
                roster["_comment"] = override["_comment"]
        _validate(roster, schema, resolved=True)
        enabled = [entry for entry in roster["legs"] if entry["enabled"]]
        return {**roster, "config_path": str(config) if configured else None,
                "enabled": [entry["name"] for entry in enabled],
                "families": sorted({entry["vendor"] for entry in enabled}),
                "capabilities_checked": False}
    except ValidationError as error:
        raise ValueError(f"invalid roster at {error.json_path}: {error.validator}") from None
    except (OSError, ValueError, RuntimeError, RecursionError) as error:
        raise ValueError(f"invalid roster: {error}") from None
