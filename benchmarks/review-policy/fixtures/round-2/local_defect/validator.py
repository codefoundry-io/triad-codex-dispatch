def validate_count(raw: object) -> bool:
    try:
        count = int(raw)
    except (TypeError, ValueError):
        return False
    return count >= 0
