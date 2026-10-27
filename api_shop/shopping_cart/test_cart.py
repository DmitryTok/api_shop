from decimal import Decimal

import pytest
from currencies.models import Currency
from django.urls import reverse
from drf_spectacular.generators import SchemaGenerator
from rest_framework.test import APIClient

from shopping_cart.models import CartItem, ShoppingCart

pytestmark = pytest.mark.django_db


def add_to_cart(user, variant, quantity=1):
    cart, _ = ShoppingCart.objects.get_or_create(user=user)
    return CartItem.objects.create(
        cart=cart, product_variant=variant, quantity=quantity
    )


def post_item(client, variant, quantity=None):
    body = {"product_variant": variant.id}

    if quantity is not None:
        body["quantity"] = quantity

    return client.post(reverse("cart-items-list"), body, format="json")


def test_cart_endpoints_require_authentication():
    client = APIClient()

    assert client.get(reverse("shopping-cart")).status_code == 401
    assert client.get(reverse("cart-items-list")).status_code == 401
    assert client.post(reverse("cart-items-list"), {}, format="json").status_code == 401


def test_cart_is_created_empty_on_first_get(api_client, user):
    response = api_client.get(reverse("shopping-cart"))

    assert response.status_code == 200

    body = response.json()
    assert body["user"] == user.id
    assert body["currency_code"] == "UAH"
    assert body["items"] == []
    assert Decimal(body["total_amount"]) == Decimal("0.00")
    assert ShoppingCart.objects.filter(user=user).count() == 1


def test_add_item_returns_product_info_and_price(api_client, make_variant):
    variant = make_variant(price="1500.00", stock=5)

    response = post_item(api_client, variant, quantity=2)

    assert response.status_code == 201

    body = response.json()
    assert body["product_variant"] == variant.id
    assert body["product_name"] == variant.product.name
    assert body["sku"] == variant.sku
    assert body["size"] == "M"
    assert body["color"] == "Black"
    assert body["quantity"] == 2
    assert Decimal(body["unit_price"]) == Decimal("1500.00")
    assert Decimal(body["line_total"]) == Decimal("3000.00")


def test_add_item_without_quantity_defaults_to_one(api_client, make_variant):
    variant = make_variant()

    response = post_item(api_client, variant)

    assert response.status_code == 201
    assert response.json()["quantity"] == 1


def test_adding_same_variant_again_increases_quantity(api_client, make_variant):
    variant = make_variant(price="10.00", stock=10)

    first = post_item(api_client, variant, quantity=2)
    second = post_item(api_client, variant, quantity=3)

    assert first.status_code == 201
    assert second.status_code == 200

    body = second.json()
    assert body["id"] == first.json()["id"]
    assert body["quantity"] == 5
    assert Decimal(body["line_total"]) == Decimal("50.00")
    assert CartItem.objects.count() == 1


@pytest.mark.parametrize("quantity", [0, -1])
def test_add_item_with_non_positive_quantity_is_rejected(
    api_client, make_variant, quantity
):
    variant = make_variant()

    response = post_item(api_client, variant, quantity=quantity)

    assert response.status_code == 400
    assert "quantity" in response.json()
    assert CartItem.objects.count() == 0


def test_add_item_over_stock_is_rejected(api_client, make_variant):
    variant = make_variant(stock=2)

    response = post_item(api_client, variant, quantity=3)

    assert response.status_code == 400
    assert CartItem.objects.count() == 0


def test_merged_quantity_over_stock_is_rejected(api_client, make_variant):
    variant = make_variant(stock=3)

    assert post_item(api_client, variant, quantity=2).status_code == 201
    assert post_item(api_client, variant, quantity=2).status_code == 400
    assert CartItem.objects.get().quantity == 2


def test_cart_total_sums_priced_items(api_client, user, make_variant):
    first = make_variant(price="100.00")
    second = make_variant(price="250.50")
    add_to_cart(user, first, 2)
    add_to_cart(user, second, 1)

    response = api_client.get(reverse("shopping-cart"))

    assert response.status_code == 200

    body = response.json()
    assert [item["sku"] for item in body["items"]] == [first.sku, second.sku]
    assert Decimal(body["total_amount"]) == Decimal("450.50")


def test_currency_code_param_prices_the_cart_in_that_currency(
    api_client, user, make_variant
):
    priced_in_both = make_variant(price="100.00")
    Currency.objects.create(
        product_variant=priced_in_both, currency_code="USD", amount=Decimal("3.00")
    )
    priced_in_uah_only = make_variant(price="200.00")
    add_to_cart(user, priced_in_both, 2)
    add_to_cart(user, priced_in_uah_only, 1)

    response = api_client.get(reverse("shopping-cart"), {"currency_code": "usd"})

    assert response.status_code == 200

    body = response.json()
    assert body["currency_code"] == "USD"
    assert Decimal(body["total_amount"]) == Decimal("6.00")

    by_sku = {item["sku"]: item for item in body["items"]}
    assert Decimal(by_sku[priced_in_both.sku]["unit_price"]) == Decimal("3.00")
    assert by_sku[priced_in_uah_only.sku]["unit_price"] is None
    assert by_sku[priced_in_uah_only.sku]["line_total"] is None


def test_newest_price_row_wins_when_currency_has_duplicates(
    api_client, user, make_variant
):
    variant = make_variant(price="100.00")
    Currency.objects.create(
        product_variant=variant, currency_code="UAH", amount=Decimal("120.00")
    )
    add_to_cart(user, variant, 1)

    response = api_client.get(reverse("shopping-cart"))

    assert Decimal(response.json()["items"][0]["unit_price"]) == Decimal("120.00")


@pytest.mark.parametrize("code", ["XX", "UAH1", "12A", "У"])
def test_invalid_currency_code_is_rejected(api_client, code):
    response = api_client.get(reverse("shopping-cart"), {"currency_code": code})

    assert response.status_code == 400
    assert "currency_code" in response.json()


def test_invalid_currency_code_on_add_does_not_change_the_cart(
    api_client, make_variant
):
    variant = make_variant()

    response = api_client.post(
        reverse("cart-items-list") + "?currency_code=b4d",
        {"product_variant": variant.id},
        format="json",
    )

    assert response.status_code == 400
    assert CartItem.objects.count() == 0


def test_patch_changes_quantity_and_recalculates_line_total(
    api_client, user, make_variant
):
    item = add_to_cart(user, make_variant(price="10.00", stock=10), 1)

    response = api_client.patch(
        reverse("cart-items-detail", args=[item.id]), {"quantity": 4}, format="json"
    )

    assert response.status_code == 200

    body = response.json()
    assert body["quantity"] == 4
    assert Decimal(body["line_total"]) == Decimal("40.00")


def test_patch_over_stock_is_rejected(api_client, user, make_variant):
    item = add_to_cart(user, make_variant(stock=2), 1)

    response = api_client.patch(
        reverse("cart-items-detail", args=[item.id]), {"quantity": 3}, format="json"
    )

    assert response.status_code == 400
    item.refresh_from_db()
    assert item.quantity == 1


def test_patch_with_zero_quantity_removes_item(api_client, user, make_variant):
    item = add_to_cart(user, make_variant(), 2)

    response = api_client.patch(
        reverse("cart-items-detail", args=[item.id]), {"quantity": 0}, format="json"
    )

    assert response.status_code == 204
    assert CartItem.objects.count() == 0


def test_delete_removes_item(api_client, user, make_variant):
    item = add_to_cart(user, make_variant(), 2)

    response = api_client.delete(reverse("cart-items-detail", args=[item.id]))

    assert response.status_code == 204
    assert CartItem.objects.count() == 0


def test_list_returns_only_own_items(api_client, user, other_user, make_variant):
    own = add_to_cart(user, make_variant(), 1)
    add_to_cart(other_user, make_variant(), 1)

    response = api_client.get(reverse("cart-items-list"))

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [own.id]


def test_other_users_item_is_not_accessible(api_client, other_user, make_variant):
    foreign = add_to_cart(other_user, make_variant(), 1)
    url = reverse("cart-items-detail", args=[foreign.id])

    assert api_client.get(url).status_code == 404
    assert api_client.patch(url, {"quantity": 2}, format="json").status_code == 404
    assert api_client.delete(url).status_code == 404
    assert CartItem.objects.filter(pk=foreign.pk).exists()


def test_cart_endpoints_are_documented_in_swagger_schema():
    paths = SchemaGenerator().get_schema(request=None, public=True)["paths"]

    cart_get = paths["/api/shopping-cart/cart/"]["get"]
    ok_schema = cart_get["responses"]["200"]["content"]["application/json"]["schema"]
    assert ok_schema == {"$ref": "#/components/schemas/ShoppingCart"}

    assert set(paths["/api/shopping-cart/cart-items/"]) == {"get", "post"}
    assert set(paths["/api/shopping-cart/cart-items/{id}/"]) == {
        "get",
        "put",
        "patch",
        "delete",
    }

    detail_parameters = {
        parameter["name"]: parameter
        for parameter in paths["/api/shopping-cart/cart-items/{id}/"]["get"][
            "parameters"
        ]
    }
    assert detail_parameters["id"]["in"] == "path"
    assert detail_parameters["id"]["schema"]["type"] == "integer"
    assert detail_parameters["currency_code"]["in"] == "query"
