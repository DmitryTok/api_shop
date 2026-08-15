from addons.slugify import generate_unique_slug
from rest_framework import serializers

from .models import Category, Subcategory


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.CharField(required=False)

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name cannot be empty")

        if len(value) < 2:
            raise serializers.ValidationError("Name too short")

        return value

    def create(self, validated_data):
        if not validated_data.get("slug"):
            validated_data["slug"] = generate_unique_slug(
                Category,
                validated_data["name"],
            )

        return super().create(validated_data)

    class Meta:
        model = Category
        fields = "__all__"


class SubcategorySerializer(serializers.ModelSerializer):
    slug = serializers.CharField(required=False)

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name cannot be empty")

        if len(value) < 2:
            raise serializers.ValidationError("Name too short")

        return value

    def create(self, validated_data):
        if not validated_data.get("slug"):
            validated_data["slug"] = generate_unique_slug(
                Subcategory,
                validated_data["name"],
            )

        return super().create(validated_data)

    class Meta:
        model = Subcategory
        fields = "__all__"
