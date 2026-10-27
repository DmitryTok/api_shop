import os

from django.core.exceptions import ImproperlyConfigured


def getenv_bool(variable_name: str, default: bool = False) -> bool:
    raw_value = os.getenv(variable_name)

    if raw_value is None:
        return default

    value = raw_value.strip().lower()

    if value in {"1", "true", "yes", "on"}:
        return True

    if value in {"0", "false", "no", "off"}:
        return False

    raise ImproperlyConfigured(
        f"{variable_name} must be a boolean value: true or false"
    )


def getenv_int(variable_name: str, default: int | None = None) -> int:
    raw_value = os.getenv(variable_name)

    if raw_value is None or not raw_value.strip():
        if default is not None:
            return default

        raise ImproperlyConfigured(f"{variable_name} environment variable must be set")

    try:
        return int(raw_value)
    except ValueError as error:
        raise ImproperlyConfigured(f"{variable_name} must be an integer") from error


def getenv_list(variable_name: str, default: str = "") -> list[str]:
    """Read a comma-separated environment variable as a clean list."""
    value = os.getenv(variable_name, default)
    return [item.strip() for item in value.split(",") if item.strip()]
