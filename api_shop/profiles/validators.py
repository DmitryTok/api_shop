import re
from datetime import date

from django.core.exceptions import ValidationError

PHONE_E164_REGEX = re.compile(r"^\+\d{9,15}$", re.UNICODE)


def int_enum_validator(value, enum_class):
    if value not in (e.value for e in enum_class):
        raise ValidationError(
            f"{value} is not a valid type",
            params={"value": value},
        )


def validate_phone(value: str | None) -> str | None:
    if not value:
        return None
    if not PHONE_E164_REGEX.match(value):
        raise ValidationError(
            "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )
    return value


def validate_birthday(value):
    today = date.today()
    age = (
        today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    )

    if value > date.today():
        raise ValidationError("The date of birth cannot be in the future.")
    elif age > 125:
        raise ValidationError("You can't be more than 125 years old.")

    return value
