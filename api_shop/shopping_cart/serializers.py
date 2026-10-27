from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import CartItem, ShoppingCart


class CartItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1, required=False)

    product_name = serializers.CharField(
        source="product_variant.product.name",
        read_only=True,
    )
    sku = serializers.CharField(
        source="product_variant.sku",
        read_only=True,
    )
    size = serializers.CharField(
        source="product_variant.size.name",
        read_only=True,
    )
    color = serializers.CharField(
        source="product_variant.color.name",
        read_only=True,
    )
    unit_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        allow_null=True,
        help_text="Price of one unit in the requested currency; null if the "
        "variant has no price in that currency.",
    )
    line_total = serializers.SerializerMethodField(
        help_text="unit_price * quantity; null if unit_price is null.",
    )

    @extend_schema_field(
        serializers.DecimalField(max_digits=14, decimal_places=2, allow_null=True)
    )
    def get_line_total(self, obj):
        unit_price = getattr(obj, "unit_price", None)

        if unit_price is None:
            return None

        return str(unit_price * obj.quantity)

    def validate(self, attrs):
        product_variant = attrs.get("product_variant")
        quantity = attrs.get("quantity", 1)

        if self.instance:
            product_variant = product_variant or self.instance.product_variant
            quantity = quantity if quantity is not None else self.instance.quantity

        if quantity < 0:
            raise serializers.ValidationError({"error": "Quantity cannot be negative."})

        if quantity > product_variant.stock:
            raise serializers.ValidationError(
                {"error": "Quantity cannot exceed available stock."}
            )

        return attrs

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product_variant",
            "product_name",
            "sku",
            "size",
            "color",
            "quantity",
            "unit_price",
            "line_total",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        source="priced_items",
        many=True,
        read_only=True,
    )
    currency_code = serializers.CharField(
        read_only=True,
        help_text="Currency the cart is priced in.",
    )
    total_amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        read_only=True,
        help_text="Sum of line totals of the items that have a price.",
    )

    class Meta:
        model = ShoppingCart
        fields = (
            "id",
            "user",
            "currency_code",
            "items",
            "total_amount",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "currency_code",
            "items",
            "total_amount",
            "created_at",
            "updated_at",
        )
