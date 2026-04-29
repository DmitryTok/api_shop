from rest_framework import serializers
from .models import Category
from django.utils.text import slugify


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Category
        fields = "__all__"

    def validate_name(self, value):
        value = value.strip()

        if len(value) < 2:
            raise serializers.ValidationError("Name is too short")

        return value

    
    def validate_slug(self, value):
        if value:
            value = slugify(value)

            if Category.objects.filter(slug=value).exists():
                raise serializers.ValidationError("Slug already exists")

        return value

    
    def create(self, validated_data):
        name = validated_data.get("name")
        slug = validated_data.get("slug")

        
        if not slug and name:
            validated_data["slug"] = slugify(name)

        return Category.objects.create(**validated_data)