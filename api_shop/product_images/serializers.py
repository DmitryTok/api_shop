from rest_framework import serializers

from .models import ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = (
            "id",
            "product_variant",
            "image",
            "is_main",
            "sort_order",
        )
