import os


def getenv_int(variable_name: str, default=None):
    value = os.getenv(variable_name)
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def getenv_bool(variable_name: str, default=False) -> bool:
    value = os.getenv(variable_name)
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "on")
