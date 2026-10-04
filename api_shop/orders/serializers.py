from product_variants.serializers import ProductVariantForFavoriteSerializer
from rest_framework import serializers
from shopping_cart.models import CartItem

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantForFavoriteSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_variant",
            "quantity",
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    cart_item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        write_only=True,
        required=False,
    )
    product_variant_id = serializers.IntegerField(
        write_only=True,
        required=False,
    )

    quantity = serializers.IntegerField(
        min_value=1,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "cart_item_ids",
            "product_variant_id",
            "quantity",
            "guest_first_name",
            "guest_last_name",
            "guest_phone",
            "guest_email",
            "payment_method",
            "payment_status",
            "status",
            "total_amount",
            "created_at",
            "items",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "guest_first_name": {"required": False},
            "guest_last_name": {"required": False},
            "guest_phone": {"required": False},
            "guest_email": {"required": False},
            "payment_status": {"read_only": True},
            "status": {"read_only": True},
            "total_amount": {"read_only": True},
            "created_at": {"read_only": True},
        }

    def validate_cart_item_ids(self, value):
        request = self.context["request"]

        if not request.user.is_authenticated:
            return value

        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate cart items.")

        valid_items = CartItem.objects.filter(
            id__in=value,
            cart__user=request.user,
        ).count()

        if valid_items != len(value):
            raise serializers.ValidationError("Invalid cart items.")

        return value

    def validate(self, attrs):
        request = self.context["request"]

        if request.user.is_authenticated:
            if not attrs.get("cart_item_ids"):
                raise serializers.ValidationError(
                    {"cart_item_ids": "This field is required."}
                )

            return attrs

        guest_fields = (
            "guest_first_name",
            "guest_last_name",
            "guest_phone",
            "guest_email",
            "product_variant_id",
            "quantity",
        )

        errors = {
            field: "This field is required."
            for field in guest_fields
            if not attrs.get(field)
        }

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
