from django.db import transaction
from product_variants.models import ProductVariant
from product_variants.serializers import ProductVariantForFavoriteSerializer
from profiles.models import Profile
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

    def _create_order(
        self,
        validated_data: dict,
        quantities: dict[int, int],
        profile: Profile | None,
        cart_item_ids: list[int] | None = None,
    ) -> Order:
        with transaction.atomic():
            variants = list(
                ProductVariant.objects.select_for_update()
                .filter(id__in=quantities)
                .order_by("id")
            )

            if len(variants) != len(quantities):
                raise serializers.ValidationError(
                    {"detail": "Invalid product variant."}
                )

            total = 0
            order_items = []

            for variant in variants:
                quantity = quantities[variant.id]

                if (
                    not variant.is_active
                    or variant.price is None
                    or variant.stock < quantity
                ):
                    raise serializers.ValidationError(
                        {"detail": f"{variant.sku} is unavailable."}
                    )

                total += variant.price * quantity

                order_items.append(
                    OrderItem(
                        product_variant=variant,
                        quantity=quantity,
                    )
                )

                variant.stock -= quantity

            order = Order.objects.create(
                profile=profile,
                total_amount=total,
                **validated_data,
            )

            for item in order_items:
                item.order = order

            OrderItem.objects.bulk_create(order_items)

            ProductVariant.objects.bulk_update(
                variants,
                ["stock"],
            )

            if cart_item_ids is not None:
                CartItem.objects.filter(
                    id__in=cart_item_ids,
                    cart__user=self.context["request"].user,
                ).delete()

        return order


class AuthenticatedOrderSerializer(OrderSerializer):
    class Meta(OrderSerializer.Meta):
        fields = (
            "id",
            "cart_item_ids",
            "payment_method",
            "payment_status",
            "status",
            "total_amount",
            "created_at",
            "items",
        )

    def validate_cart_item_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate cart items.")

        return value

    def validate(self, attrs):
        cart_item_ids = attrs.get("cart_item_ids")

        if not cart_item_ids:
            raise serializers.ValidationError(
                {"cart_item_ids": "This field is required."}
            )

        if CartItem.objects.filter(
            id__in=cart_item_ids,
            cart__user=self.context["request"].user,
        ).count() != len(cart_item_ids):
            raise serializers.ValidationError(
                {"cart_item_ids": ["Invalid cart items."]}
            )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        cart_item_ids = validated_data.pop("cart_item_ids")

        cart_items = CartItem.objects.filter(
            id__in=cart_item_ids,
            cart__user=request.user,
        ).values("product_variant_id", "quantity")

        quantities = {
            item["product_variant_id"]: item["quantity"] for item in cart_items
        }

        return self._create_order(
            validated_data,
            quantities,
            request.user.profile,
            cart_item_ids,
        )


class GuestOrderSerializer(OrderSerializer):
    class Meta(OrderSerializer.Meta):
        fields = (
            "id",
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

    def validate(self, attrs):
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

    def create(self, validated_data):
        product_variant_id = validated_data.pop("product_variant_id")
        quantity = validated_data.pop("quantity")

        return self._create_order(
            validated_data,
            {product_variant_id: quantity},
            None,
        )
