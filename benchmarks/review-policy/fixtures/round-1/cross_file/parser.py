def parse_token(raw: object) -> str | None:
    if not isinstance(raw, str):
        return None
    token = raw.strip()
    return token or None
