from currencies.services import resolve_currency_code
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import CartItem, ShoppingCart
from .serializers import CartItemSerializer, ShoppingCartSerializer
from .services import cart_items_queryset, get_cart_with_prices

CURRENCY_PARAMETER = OpenApiParameter(
    name="currency_code",
    type=str,
    location=OpenApiParameter.QUERY,
    required=False,
    description=(
        "3-letter currency code to price the cart in, e.g. UAH or USD. "
        "Defaults to the store currency (DEFAULT_CURRENCY_CODE)."
    ),
)


class ShoppingCartView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShoppingCartSerializer

    @extend_schema(
        summary="Get my cart",
        description=(
            "Returns the current user's cart (created on first use) with "
            "product info, prices and the total."
        ),
        parameters=[CURRENCY_PARAMETER],
    )
    def get(self, request):
        currency_code = resolve_currency_code(request.query_params.get("currency_code"))
        cart = get_cart_with_prices(request.user, currency_code)

        return Response(self.get_serializer(cart).data)


@extend_schema_view(
    list=extend_schema(
        summary="List my cart items",
        parameters=[CURRENCY_PARAMETER],
    ),
    retrieve=extend_schema(
        summary="Get one of my cart items",
        parameters=[CURRENCY_PARAMETER],
    ),
    create=extend_schema(
        summary="Add a product variant to the cart",
        description=(
            "If the variant is already in the cart, its quantity is increased "
            "and 200 is returned instead of 201. The resulting quantity cannot "
            "exceed the variant's stock."
        ),
        parameters=[CURRENCY_PARAMETER],
        responses={200: CartItemSerializer, 201: CartItemSerializer},
        examples=[
            OpenApiExample(
                "Add 2 units",
                value={"product_variant": 1, "quantity": 2},
                request_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary="Replace a cart item (prefer PATCH)",
        parameters=[CURRENCY_PARAMETER],
    ),
    partial_update=extend_schema(
        summary="Change the quantity of a cart item",
        description="Send quantity 0 to remove the item (204).",
        parameters=[CURRENCY_PARAMETER],
        responses={200: CartItemSerializer, 204: None},
        examples=[
            OpenApiExample(
                "Set quantity",
                value={"quantity": 3},
                request_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Remove an item from the cart",
    ),
)
class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return CartItem.objects.none()

        currency_code = resolve_currency_code(
            self.request.query_params.get("currency_code")
        )

        return cart_items_queryset(self.request.user, currency_code)

    def create(self, request, *args, **kwargs):
        # Resolved first so an invalid currency_code fails before anything is saved.
        queryset = self.get_queryset()

        cart, _ = ShoppingCart.objects.get_or_create(
            user=request.user,
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_variant = serializer.validated_data["product_variant"]
        quantity = serializer.validated_data.get("quantity", 1)

        existing_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_variant=product_variant,
            defaults={"quantity": quantity},
        )

        if not created:
            new_quantity = existing_item.quantity + quantity

            serializer = self.get_serializer(
                existing_item,
                data={"quantity": new_quantity},
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        # Re-read so the response carries the annotated price.
        item = queryset.get(pk=existing_item.pk)

        return Response(
            self.get_serializer(item).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        quantity = request.data.get("quantity")

        if quantity == 0:
            instance.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )

        return super().partial_update(
            request,
            *args,
            **kwargs,
        )
