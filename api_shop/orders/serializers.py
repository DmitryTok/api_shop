from profiles.validators import validate_phone
from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_variant",
            "product_name",
            "sku",
            "size",
            "color",
            "unit_price",
            "quantity",
            "line_total",
        )
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "currency_code",
            "total_amount",
            "first_name",
            "last_name",
            "phone",
            "email",
            "shipping_address",
            "comment",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    """Checkout form. The items come from the user's cart, not from the body."""

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(
        max_length=16,
        validators=[validate_phone],
        help_text="International format, e.g. +380501234567.",
    )
    shipping_address = serializers.CharField(max_length=500)
    comment = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
    )
    currency_code = serializers.CharField(
        min_length=3,
        max_length=3,
        required=False,
        help_text=(
            "Currency to price the order in, e.g. UAH. Defaults to the store "
            "currency. Every item in the cart must have a price in it."
        ),
    )
