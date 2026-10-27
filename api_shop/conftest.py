from decimal import Decimal
from itertools import count

import pytest
from brands.models import Brand
from categories.models import Category, Subcategory
from colors.models import Color
from currencies.models import Currency
from django.contrib.auth import get_user_model
from product_variants.models import ProductVariant
from products.models import Product
from rest_framework.test import APIClient
from sizes.models import Size

User = get_user_model()

COLOR_HEX = {"Black": "#000000", "White": "#FFFFFF"}


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="customer@example.com", password="Test1234!", is_active=True
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email="other@example.com", password="Test1234!", is_active=True
    )


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def other_client(other_user):
    client = APIClient()
    client.force_authenticate(user=other_user)
    return client


@pytest.fixture
def make_variant(db):
    """Factory: a product variant with stock and (optionally) a price."""
    counter = count(1)

    def _make(
        *,
        stock=10,
        price="100.00",
        currency="UAH",
        is_active=True,
        product_is_active=True,
        product_is_hidden=False,
        size_name="M",
        color_name="Black",
    ):
        n = next(counter)

        brand, _ = Brand.objects.get_or_create(
            name="Test Brand", defaults={"slug": "test-brand"}
        )
        category, _ = Category.objects.get_or_create(
            name="Test Category", defaults={"slug": "test-category"}
        )
        subcategory, _ = Subcategory.objects.get_or_create(
            name="Test Subcategory",
            defaults={"slug": "test-subcategory", "category": category},
        )
        size, _ = Size.objects.get_or_create(
            name=size_name, defaults={"size_type": "clothing"}
        )
        color, _ = Color.objects.get_or_create(
            name=color_name, defaults={"hex_code": COLOR_HEX[color_name]}
        )
        product = Product.objects.create(
            name=f"Test Product {n}",
            slug=f"test-product-{n}",
            brand=brand,
            subcategory=subcategory,
            is_active=product_is_active,
            is_hidden=product_is_hidden,
        )
        variant = ProductVariant.objects.create(
            product=product,
            size=size,
            color=color,
            sku=f"SKU-{n}",
            stock=stock,
            is_active=is_active,
        )

        if price is not None:
            Currency.objects.create(
                product_variant=variant,
                currency_code=currency,
                amount=Decimal(price),
            )

        return variant

    return _make
