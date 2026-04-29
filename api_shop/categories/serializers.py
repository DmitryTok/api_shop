from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Name cannot be empty")

        if len(value) < 2:
            raise serializers.ValidationError("Name too short")

        return value

    class Meta:
        model = Category
        fields = "__all__"

