from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Order
from .serializers import OrderCreateSerializer, OrderSerializer
from .services import create_order_from_cart

ORDER_EXAMPLE = {
    "id": 1,
    "status": "PENDING",
    "currency_code": "UAH",
    "total_amount": "3000.00",
    "first_name": "Ivan",
    "last_name": "Petrenko",
    "phone": "+380501234567",
    "email": "customer@example.com",
    "shipping_address": "Kyiv, Khreshchatyk St, 1",
    "comment": "Call before delivery",
    "items": [
        {
            "id": 1,
            "product_variant": 1,
            "product_name": "Test T-Shirt",
            "sku": "TEST-TSHIRT-M-BLK",
            "size": "M",
            "color": "Black",
            "unit_price": "1500.00",
            "quantity": 2,
            "line_total": "3000.00",
        }
    ],
    "created_at": "2026-10-27T17:30:00Z",
    "updated_at": "2026-10-27T17:30:00Z",
}


@extend_schema_view(
    list=extend_schema(
        summary="List my orders",
        description="Orders of the current user, newest first.",
    ),
    retrieve=extend_schema(
        summary="Get one of my orders",
        description="Other users' orders are not visible (404).",
    ),
    create=extend_schema(
        summary="Place an order from my cart",
        description=(
            "Turns the whole cart of the current user into an order. Product "
            "name, SKU, size, color and unit price are copied into the order at "
            "this moment, so later catalog changes do not affect it. Stock is "
            "reduced and the cart is emptied. Everything happens in one "
            "transaction: if any item is unavailable, has no price in the "
            "currency or exceeds the stock, nothing is changed."
        ),
        request=OrderCreateSerializer,
        responses={
            201: OrderSerializer,
            400: OpenApiResponse(
                description=(
                    "Invalid fields (per-field errors), or the order cannot be "
                    'placed: {"detail": "Cart is empty." | "<SKU> is not '
                    'available." | "<SKU> has no price in UAH." | "Not enough '
                    'stock for <SKU>: requested 5, available 2."}'
                ),
            ),
            401: OpenApiResponse(description="Not authenticated."),
        },
        examples=[
            OpenApiExample(
                "Place an order",
                value={
                    "first_name": "Ivan",
                    "last_name": "Petrenko",
                    "phone": "+380501234567",
                    "shipping_address": "Kyiv, Khreshchatyk St, 1",
                    "comment": "Call before delivery",
                    "currency_code": "UAH",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Created order",
                value=ORDER_EXAMPLE,
                response_only=True,
                status_codes=["201"],
            ),
        ],
    ),
)
class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()

        return Order.objects.filter(user=self.request.user).prefetch_related("items")

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = create_order_from_cart(request.user, serializer.validated_data)

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
