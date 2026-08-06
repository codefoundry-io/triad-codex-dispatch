def public_profile(record: dict[str, str]) -> dict[str, str]:
    return {"display_name": record["name"]}
