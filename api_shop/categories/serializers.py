from rest_framework import serializers
from .models import Category
from addons.slugify import generate_slug

class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.CharField(required=False)

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name cannot be empty")

        if len(value) < 2:
            raise serializers.ValidationError("Name too short")

        return value

    class Meta:
        model = Category
        fields = "__all__"

    def create(self, validated_data):
        name = validated_data.get("name")

        if not validated_data.get("slug"):
           validated_data["slug"] = generate_slug(name)

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        name = validated_data.get("name")

        if name and name != instance.name:
           validated_data["slug"] = generate_slug(name)

        return super().update(instance, validated_data)

