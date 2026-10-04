from django.db import transaction
from drf_spectacular.utils import extend_schema
from product_variants.models import ProductVariant
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from shopping_cart.models import CartItem

from .models import Order, OrderItem
from .serializers import OrderSerializer


class OrderCreateAPIView(APIView):
    @extend_schema(
        request=OrderSerializer,
        responses={201: OrderSerializer},
    )
    def post(self, request):
        serializer = OrderSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        cart_items = None

        if request.user.is_authenticated:
            profile = request.user.profile

            cart_items = CartItem.objects.filter(
                id__in=data.pop("cart_item_ids"),
                cart__user=request.user,
            ).select_related("product_variant")

            items = ((item.product_variant, item.quantity) for item in cart_items)
        else:
            profile = None

            variant = ProductVariant.objects.filter(
                id=data.pop("product_variant_id")
            ).first()

            if variant is None:
                return Response(
                    {"detail": "Invalid product variant."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            items = ((variant, data.pop("quantity")),)

        order_items = []
        variants = []
        total = 0

        for variant, quantity in items:
            if variant.price is None or quantity > variant.stock:
                return Response(
                    {"detail": f"{variant.sku} is unavailable."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            total += variant.price * quantity
            variant.stock -= quantity

            order_items.append(
                OrderItem(
                    product_variant=variant,
                    quantity=quantity,
                )
            )
            variants.append(variant)

        with transaction.atomic():
            order = Order.objects.create(
                profile=profile,
                total_amount=total,
                **data,
            )

            for item in order_items:
                item.order = order

            OrderItem.objects.bulk_create(order_items)
            ProductVariant.objects.bulk_update(variants, ["stock"])

            if cart_items:
                cart_items.delete()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
