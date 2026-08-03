from rest_framework import serializers

from validators.validators_categories import CategoryNameValidator
from .models import Category, Subcategory
from addons.slugify import generate_unique_slug


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.CharField(required=False)

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
        validators = [CategoryNameValidator()]


class SubcategorySerializer(serializers.ModelSerializer):
    slug = serializers.CharField(required=False)

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
        validators = [CategoryNameValidator()]
