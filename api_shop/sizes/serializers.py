from rest_framework import serializers

from .models import Size


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = (
            "id",
            "name",
            "size_type",
            "sort_order",
        )
