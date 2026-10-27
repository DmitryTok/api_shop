from decimal import Decimal

import pytest
from currencies.models import Currency
from django.urls import reverse
from drf_spectacular.generators import SchemaGenerator
from product_variants.models import ProductVariant
from products.models import Product
from rest_framework.test import APIClient
from shopping_cart.models import CartItem, ShoppingCart

from orders.models import Order, OrderItem, OrderStatus

pytestmark = pytest.mark.django_db

CHECKOUT = {
    "first_name": "Ivan",
    "last_name": "Petrenko",
    "phone": "+380501234567",
    "shipping_address": "Kyiv, Khreshchatyk St, 1",
}


def add_to_cart(user, variant, quantity=1):
    cart, _ = ShoppingCart.objects.get_or_create(user=user)
    return CartItem.objects.create(
        cart=cart, product_variant=variant, quantity=quantity
    )


def place_order(client, **overrides):
    return client.post(reverse("orders-list"), {**CHECKOUT, **overrides}, format="json")


def test_orders_require_authentication():
    client = APIClient()

    assert client.get(reverse("orders-list")).status_code == 401
    assert client.get(reverse("orders-detail", args=[1])).status_code == 401
    assert place_order(client).status_code == 401


def test_order_is_created_from_the_cart(api_client, user, make_variant):
    shirt = make_variant(price="1500.00", stock=10, color_name="Black")
    socks = make_variant(price="99.99", stock=5, color_name="White")
    add_to_cart(user, shirt, 2)
    add_to_cart(user, socks, 1)

    response = place_order(api_client, comment="Call before delivery")

    assert response.status_code == 201

    body = response.json()
    assert body["status"] == "PENDING"
    assert body["currency_code"] == "UAH"
    assert Decimal(body["total_amount"]) == Decimal("3099.99")
    assert body["email"] == user.email
    assert body["first_name"] == "Ivan"
    assert body["last_name"] == "Petrenko"
    assert body["phone"] == "+380501234567"
    assert body["shipping_address"] == "Kyiv, Khreshchatyk St, 1"
    assert body["comment"] == "Call before delivery"

    lines = {line["sku"]: line for line in body["items"]}
    assert set(lines) == {shirt.sku, socks.sku}

    shirt_line = lines[shirt.sku]
    assert shirt_line["product_variant"] == shirt.id
    assert shirt_line["product_name"] == shirt.product.name
    assert shirt_line["size"] == "M"
    assert shirt_line["color"] == "Black"
    assert Decimal(shirt_line["unit_price"]) == Decimal("1500.00")
    assert shirt_line["quantity"] == 2
    assert Decimal(shirt_line["line_total"]) == Decimal("3000.00")

    order = Order.objects.get()
    assert order.user == user
    assert order.status == OrderStatus.PENDING
    assert order.items.count() == 2

    shirt.refresh_from_db()
    socks.refresh_from_db()
    assert shirt.stock == 8
    assert socks.stock == 4
    assert not CartItem.objects.filter(cart__user=user).exists()


def test_empty_cart_cannot_be_ordered(api_client):
    response = place_order(api_client)

    assert response.status_code == 400
    assert response.json() == {"detail": "Cart is empty."}
    assert Order.objects.count() == 0


def test_second_checkout_does_not_duplicate_the_order(api_client, user, make_variant):
    variant = make_variant(stock=5)
    add_to_cart(user, variant, 2)

    first = place_order(api_client)
    second = place_order(api_client)

    assert first.status_code == 201
    assert second.status_code == 400
    assert Order.objects.count() == 1
    variant.refresh_from_db()
    assert variant.stock == 3


def test_not_enough_stock_changes_nothing(api_client, user, make_variant):
    variant = make_variant(stock=5)
    add_to_cart(user, variant, 3)
    ProductVariant.objects.filter(pk=variant.pk).update(stock=2)

    response = place_order(api_client)

    assert response.status_code == 400
    assert response.json() == {
        "detail": f"Not enough stock for {variant.sku}: requested 3, available 2."
    }
    assert Order.objects.count() == 0
    assert CartItem.objects.count() == 1
    variant.refresh_from_db()
    assert variant.stock == 2


def test_one_bad_item_blocks_the_whole_order(api_client, user, make_variant):
    good = make_variant(stock=5)
    bad = make_variant(stock=5)
    add_to_cart(user, good, 1)
    add_to_cart(user, bad, 1)
    ProductVariant.objects.filter(pk=bad.pk).update(stock=0)

    response = place_order(api_client)

    assert response.status_code == 400
    assert Order.objects.count() == 0
    assert CartItem.objects.count() == 2
    good.refresh_from_db()
    assert good.stock == 5


@pytest.mark.parametrize(
    "options",
    [
        {"is_active": False},
        {"product_is_active": False},
        {"product_is_hidden": True},
    ],
)
def test_unavailable_variant_cannot_be_ordered(api_client, user, make_variant, options):
    variant = make_variant(**options)
    add_to_cart(user, variant, 1)

    response = place_order(api_client)

    assert response.status_code == 400
    assert response.json() == {"detail": f"{variant.sku} is not available."}
    assert Order.objects.count() == 0


def test_item_without_price_in_currency_cannot_be_ordered(
    api_client, user, make_variant
):
    variant = make_variant(price="10.00", currency="UAH")
    add_to_cart(user, variant, 1)

    response = place_order(api_client, currency_code="USD")

    assert response.status_code == 400
    assert response.json() == {"detail": f"{variant.sku} has no price in USD."}
    assert Order.objects.count() == 0


def test_item_with_zero_price_cannot_be_ordered(api_client, user, make_variant):
    variant = make_variant(price="0.00")
    add_to_cart(user, variant, 1)

    response = place_order(api_client)

    assert response.status_code == 400
    assert response.json() == {"detail": f"{variant.sku} has no price in UAH."}


def test_order_can_be_placed_in_another_currency(api_client, user, make_variant):
    variant = make_variant(price="100.00")
    Currency.objects.create(
        product_variant=variant, currency_code="USD", amount=Decimal("3.00")
    )
    add_to_cart(user, variant, 2)

    response = place_order(api_client, currency_code="usd")

    assert response.status_code == 201

    body = response.json()
    assert body["currency_code"] == "USD"
    assert Decimal(body["total_amount"]) == Decimal("6.00")
    assert Decimal(body["items"][0]["unit_price"]) == Decimal("3.00")


@pytest.mark.parametrize(
    "field", ["first_name", "last_name", "phone", "shipping_address"]
)
def test_required_fields_are_validated(api_client, user, make_variant, field):
    add_to_cart(user, make_variant(), 1)
    body = {key: value for key, value in CHECKOUT.items() if key != field}

    response = api_client.post(reverse("orders-list"), body, format="json")

    assert response.status_code == 400
    assert field in response.json()
    assert Order.objects.count() == 0
    assert CartItem.objects.count() == 1


def test_phone_must_be_in_international_format(api_client, user, make_variant):
    add_to_cart(user, make_variant(), 1)

    response = place_order(api_client, phone="0501234567")

    assert response.status_code == 400
    assert "phone" in response.json()


@pytest.mark.parametrize("code", ["XX", "UAH1", "12A"])
def test_invalid_currency_code_is_rejected(api_client, user, make_variant, code):
    add_to_cart(user, make_variant(), 1)

    response = place_order(api_client, currency_code=code)

    assert response.status_code == 400
    assert "currency_code" in response.json()
    assert Order.objects.count() == 0


def test_zero_quantity_cart_rows_are_ignored(api_client, user, make_variant):
    good = make_variant(stock=5)
    legacy = make_variant(stock=5)
    add_to_cart(user, good, 1)
    add_to_cart(user, legacy, 0)

    response = place_order(api_client)

    assert response.status_code == 201
    assert [line["sku"] for line in response.json()["items"]] == [good.sku]
    legacy.refresh_from_db()
    assert legacy.stock == 5
    assert CartItem.objects.count() == 0


def test_order_does_not_change_when_the_catalog_changes(api_client, user, make_variant):
    variant = make_variant(price="1500.00")
    add_to_cart(user, variant, 2)
    created = place_order(api_client).json()

    Currency.objects.filter(product_variant=variant).update(amount=Decimal("9999.00"))
    Product.objects.filter(pk=variant.product_id).update(name="Renamed product")
    ProductVariant.objects.filter(pk=variant.pk).update(sku="NEW-SKU")

    response = api_client.get(reverse("orders-detail", args=[created["id"]]))

    assert response.status_code == 200

    body = response.json()
    assert body["total_amount"] == created["total_amount"] == "3000.00"
    assert body["items"] == created["items"]
    assert body["items"][0]["unit_price"] == "1500.00"
    assert body["items"][0]["sku"] != "NEW-SKU"


def test_order_survives_deleting_the_variant_from_the_catalog(
    api_client, user, make_variant
):
    variant = make_variant(price="10.00")
    add_to_cart(user, variant, 1)
    created = place_order(api_client).json()
    sku = created["items"][0]["sku"]

    variant.delete()

    body = api_client.get(reverse("orders-detail", args=[created["id"]])).json()
    assert body["items"][0]["product_variant"] is None
    assert body["items"][0]["sku"] == sku
    assert OrderItem.objects.count() == 1


def test_list_returns_only_own_orders_newest_first(
    api_client, other_client, user, other_user, make_variant
):
    for _ in range(2):
        add_to_cart(user, make_variant(), 1)
        assert place_order(api_client).status_code == 201

    add_to_cart(other_user, make_variant(), 1)
    assert place_order(other_client).status_code == 201

    response = api_client.get(reverse("orders-list"))

    assert response.status_code == 200

    own_ids = list(
        Order.objects.filter(user=user).values_list("id", flat=True)
    )  # model ordering: newest first
    assert len(own_ids) == 2
    assert [order["id"] for order in response.json()] == own_ids


def test_other_users_order_is_not_accessible(
    api_client, other_client, other_user, make_variant
):
    add_to_cart(other_user, make_variant(), 1)
    foreign_id = place_order(other_client).json()["id"]

    response = api_client.get(reverse("orders-detail", args=[foreign_id]))

    assert response.status_code == 404


def test_orders_are_documented_in_swagger_schema():
    paths = SchemaGenerator().get_schema(request=None, public=True)["paths"]

    assert set(paths["/api/orders/"]) == {"get", "post"}
    assert set(paths["/api/orders/{id}/"]) == {"get"}

    post = paths["/api/orders/"]["post"]
    request_schema = post["requestBody"]["content"]["application/json"]["schema"]
    response_schema = post["responses"]["201"]["content"]["application/json"]["schema"]
    assert request_schema == {"$ref": "#/components/schemas/OrderCreate"}
    assert response_schema == {"$ref": "#/components/schemas/Order"}
