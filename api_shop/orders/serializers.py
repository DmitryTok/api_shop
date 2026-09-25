from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_variant",
            "quantity",
            "price",
        )

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    cart_item_ids = serializers.ListField(
    child=serializers.IntegerField(),
    allow_empty=False,
    write_only=True,
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "cart_item_ids",
            "first_name",
            "last_name",
            "phone",
            "delivery_method",
            "city",
            "branch_number",
            "payment_method",
            "payment_status",
            "status",
            "total_amount",
            "created_at",
            "items",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "payment_status": {"read_only": True},
            "status": {"read_only": True},
            "total_amount": {"read_only": True},
            "created_at": {"read_only": True},
        }

