import re
import datetime
from datetime import date

from django.core.exceptions import ValidationError
from rest_framework import serializers


PHONE_E164_REGEX = re.compile(r"^\+\d{9,15}$", re.UNICODE)


def profile_phone_validator(phone: str) -> None:
    if not phone:
        return None

    if not PHONE_E164_REGEX.match(phone):
        raise serializers.ValidationError(
            "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )


def profile_birthday_validator(birthday: datetime.date) -> None:
    today = date.today()
    age = (
            today.year
            - birthday.year
            - ((today.month, today.day) < (birthday.month, birthday.day))
    )

    if birthday > date.today():
        raise serializers.ValidationError("The date of birth cannot be in the future.")

    elif age > 125:
        raise serializers.ValidationError("You can't be more than 125 years old.")


def int_enum_validator(value, enum_class):
    if value not in (e.value for e in enum_class):
        raise ValidationError(
            f"{value} is not a valid type",
            params={"value": value},
        )
