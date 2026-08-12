from types import SimpleNamespace

import pytest
from rest_framework import serializers

from shopping_cart.serializers import CartItemSerializer


def test_cart_item_serializer_valid_quantity():
    product_variant = SimpleNamespace(stock=10)

    serializer = CartItemSerializer()

    attrs = {
        "product_variant": product_variant,
        "quantity": 5,
    }

    result = serializer.validate(attrs)

    assert result == attrs


def test_cart_item_serializer_negative_quantity():
    product_variant = SimpleNamespace(stock=10)

    serializer = CartItemSerializer()

    with pytest.raises(
        serializers.ValidationError,
        match="Quantity cannot be negative.",
    ):
        serializer.validate(
            {
                "product_variant": product_variant,
                "quantity": -1,
            }
        )


def test_cart_item_serializer_quantity_exceeds_stock():
    product_variant = SimpleNamespace(stock=5)

    serializer = CartItemSerializer()

    with pytest.raises(
        serializers.ValidationError,
        match="Quantity cannot exceed available stock.",
    ):
        serializer.validate(
            {
                "product_variant": product_variant,
                "quantity": 6,
            }
        )


def test_cart_item_serializer_update_uses_instance_product_variant():
    product_variant = SimpleNamespace(stock=10)

    instance = SimpleNamespace(
        product_variant=product_variant,
        quantity=2,
    )

    serializer = CartItemSerializer(instance=instance)

    attrs = {
        "quantity": 5,
    }

    result = serializer.validate(attrs)

    assert result == attrs


def test_cart_item_serializer_update_uses_instance_quantity():
    product_variant = SimpleNamespace(stock=10)

    instance = SimpleNamespace(
        product_variant=product_variant,
        quantity=5,
    )

    serializer = CartItemSerializer(instance=instance)

    attrs = {
        "product_variant": product_variant,
        "quantity": None,
    }

    result = serializer.validate(attrs)

    assert result == attrs
    