from rest_framework import serializers


class CategoryNameValidator:
    def __call__(self, attrs: dict) -> None:
        name = attrs.get("name")

        if not name:
            raise serializers.ValidationError("Name cannot be empty")

        if len(name) < 2:
            raise serializers.ValidationError("Name too short")
