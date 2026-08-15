from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from .models import CartItem, ShoppingCart
from .serializers import CartItemSerializer, ShoppingCartSerializer


class ShoppingCartViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, _ = ShoppingCart.objects.get_or_create(
            user=request.user,
        )

        serializer = ShoppingCartSerializer(cart)
        return Response(serializer.data)


class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user,
        ).select_related("cart", "product_variant")

    def create(self, request, *args, **kwargs):
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

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(existing_item)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
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
