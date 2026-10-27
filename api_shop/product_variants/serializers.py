from colors.serializers import ColorSerializer
from product_images.serializers import (
    ProductImagesForFavoriteSerializer,
)
from rest_framework import serializers
from sizes.serializers import SizeSerializer

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
            "price",
            "gender",
            "is_active",
        )


class ProductVariantForFavoriteSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.name", read_only=True)
    size = SizeSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    images = ProductImagesForFavoriteSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "product_title",
            "images",
            "size",
            "color",
            "sku",
            "stock",
            "price",
            "gender",
            "is_active",
        )
        read_only_fields = fields
