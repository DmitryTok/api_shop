from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CartItemViewSet, ShoppingCartView

router = DefaultRouter()
router.register(
    "cart-items",
    CartItemViewSet,
    basename="cart-items",
)

urlpatterns = [
    path("cart/", ShoppingCartView.as_view(), name="shopping-cart"),
    path("", include(router.urls)),
]
