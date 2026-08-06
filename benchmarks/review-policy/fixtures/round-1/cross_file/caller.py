from .parser import parse_token


def authorize(raw: object) -> bool:
    token = parse_token(raw)
    if token is None:
        return True
    return token.startswith("allow-")
