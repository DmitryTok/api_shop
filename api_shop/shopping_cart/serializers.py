from rest_framework import serializers

from .models import CartItem, ShoppingCart


class CartItemSerializer(serializers.ModelSerializer):
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
            "quantity",
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
        many=True,
        read_only=True,
    )

    class Meta:
        model = ShoppingCart
        fields = (
            "id",
            "user",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "items",
            "created_at",
            "updated_at",
        )
