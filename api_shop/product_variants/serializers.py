from rest_framework import serializers

from .models import ProductVariant


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "product",
            "size",
            "color",
            "sku",
            "stock",
            "gender",
            "is_active",
        )