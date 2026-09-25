from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from shopping_cart.models import CartItem

from .models import Order, OrderItem
from .serializers import OrderSerializer


class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=OrderSerializer,
        responses={201: OrderSerializer},
    )
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_item_ids = serializer.validated_data.pop("cart_item_ids")

        with transaction.atomic():
            cart_items = list(
                CartItem.objects.filter(
                    id__in=cart_item_ids,
                    cart__user=request.user,
                )
                .select_related("product_variant")
                .select_for_update()
            )

            if len(cart_items) != len(set(cart_item_ids)):
                return Response(
                    {"detail": "Invalid cart items."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            total_amount = 0
            order_items = []
            variants_to_update = []
            purchased_cart_item_ids = []
            unavailable_items = []

            for cart_item in cart_items:
                variant = cart_item.product_variant

                if variant.price is None or cart_item.quantity > variant.stock:
                    unavailable_items.append(variant.sku)
                    continue

                total_amount += variant.price * cart_item.quantity

                order_items.append(
                    OrderItem(
                        product_variant=variant,
                        quantity=cart_item.quantity,
                        price=variant.price,
                    )
                )

                variant.stock -= cart_item.quantity
                variants_to_update.append(variant)
                purchased_cart_item_ids.append(cart_item.id)

            if not order_items:
                return Response(
                    {
                        "detail": "Selected items are unavailable.",
                        "unavailable_items": unavailable_items,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            order = Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                **serializer.validated_data,
            )

            for order_item in order_items:
                order_item.order = order

            OrderItem.objects.bulk_create(order_items)

            type(variants_to_update[0]).objects.bulk_update(
                variants_to_update,
                ["stock"],
            )

            CartItem.objects.filter(
                id__in=purchased_cart_item_ids,
                cart__user=request.user,
            ).delete()

        return Response(
            {
                "order": OrderSerializer(order).data,
                "unavailable_items": unavailable_items,
            },
            status=status.HTTP_201_CREATED,
        )