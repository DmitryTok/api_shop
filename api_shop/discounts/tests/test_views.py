from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from brands.models import Brand
from categories.models import Category, Subcategory
from colors.models import Color
from discounts.models import Discount
from products.models import Product
from product_variants.models import Gender, ProductVariant
from sizes.models import Kind, Size


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def variant():
    brand = Brand.objects.create(
        name="Nike",
        slug="nike",
    )
    category = Category.objects.create(
        name="Women",
        slug="women",
    )
    subcategory = Subcategory.objects.create(
        category=category,
        name="Shoes",
        slug="shoes",
    )
    product = Product.objects.create(
        name="Air Max",
        slug="air-max",
        brand=brand,
        subcategory=subcategory,
    )
    size = Size.objects.create(
        name="M",
        size_type=Kind.CLOTHING,
        sort_order=1,
    )
    color = Color.objects.create(
        name="Black",
        hex_code="#000000",
    )

    return ProductVariant.objects.create(
        product=product,
        size=size,
        color=color,
        sku="AIR-MAX-BLACK-M",
        stock=10,
        gender=Gender.UNISEX,
    )


@pytest.mark.django_db
def test_discount_list(api_client, variant):
    now = timezone.now()

    Discount.objects.create(
        product_variant=variant,
        discount_type="percentage",
        amount="20.00",
        start_at=now,
        end_at=now + timedelta(days=7),
    )

    url = reverse("discount-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["discount_type"] == "percentage"
    assert response.data[0]["amount"] == "20.00"


@pytest.mark.django_db
def test_discount_detail(api_client, variant):
    now = timezone.now()

    discount = Discount.objects.create(
        product_variant=variant,
        discount_type="percentage",
        amount="20.00",
        start_at=now,
        end_at=now + timedelta(days=7),
    )

    url = reverse(
        "discount-detail",
        kwargs={"pk": discount.pk},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["product_variant"] == variant.pk
    assert response.data["discount_type"] == "percentage"
    assert response.data["amount"] == "20.00"
    assert response.data["is_active"] is True


@pytest.mark.django_db
def test_discount_detail_not_found(api_client):
    url = reverse(
        "discount-detail",
        kwargs={"pk": 99999},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_discount_list_empty(api_client):
    url = reverse("discount-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
    