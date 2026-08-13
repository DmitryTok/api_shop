from rest_framework import serializers


def category_name_validator(name: str) -> None:
    if not name:
        raise serializers.ValidationError("Name cannot be empty")

    if len(name) < 2:
        raise serializers.ValidationError("Name too short")
