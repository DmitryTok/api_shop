from django.urls import resolve, reverse

from shopping_cart.views import (
    CartItemViewSet,
    ShoppingCartViewSet,
)


def test_shopping_cart_list_url():
    url = reverse("shopping-cart-list")

    assert resolve(url).func.cls is ShoppingCartViewSet


def test_cart_items_list_url():
    url = reverse("cart-items-list")

    assert resolve(url).func.cls is CartItemViewSet


def test_cart_items_detail_url():
    url = reverse(
        "cart-items-detail",
        kwargs={"pk": 1},
    )

    assert resolve(url).func.cls is CartItemViewSet
    