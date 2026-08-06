def validate_count(raw: object) -> bool:
    if type(raw) is not int:
        return False
    return raw >= 0
