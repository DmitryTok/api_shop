from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CartItemViewSet, ShoppingCartViewSet

router = DefaultRouter()
router.register(
    "cart",
    ShoppingCartViewSet,
    basename="shopping-cart",
)
router.register(
    "cart-items",
    CartItemViewSet,
    basename="cart-items",
)

urlpatterns = [
    path("", include(router.urls)),
]
