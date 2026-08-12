import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from brands.models import Brand
from categories.models import Category, Subcategory
from colors.models import Color
from products.models import Product
from product_variants.models import Gender, ProductVariant
from sizes.models import Kind, Size


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def variant_dependencies():
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

    return product, size, color


@pytest.mark.django_db
def test_product_variant_list(api_client, variant_dependencies):
    product, size, color = variant_dependencies

    ProductVariant.objects.create(
        product=product,
        size=size,
        color=color,
        sku="AIR-MAX-BLACK-M",
        stock=10,
        gender=Gender.UNISEX,
    )

    url = reverse("product-variant-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["sku"] == "AIR-MAX-BLACK-M"


@pytest.mark.django_db
def test_product_variant_detail(api_client, variant_dependencies):
    product, size, color = variant_dependencies

    variant = ProductVariant.objects.create(
        product=product,
        size=size,
        color=color,
        sku="AIR-MAX-BLACK-M",
        stock=10,
        gender=Gender.UNISEX,
    )

    url = reverse(
        "product-variant-detail",
        kwargs={"pk": variant.pk},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["product"] == product.pk
    assert response.data["size"] == size.pk
    assert response.data["color"] == color.pk
    assert response.data["sku"] == "AIR-MAX-BLACK-M"
    assert response.data["stock"] == 10
    assert response.data["gender"] == Gender.UNISEX
    assert response.data["is_active"] is True


@pytest.mark.django_db
def test_product_variant_detail_not_found(api_client):
    url = reverse(
        "product-variant-detail",
        kwargs={"pk": 99999},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_product_variant_list_empty(api_client):
    url = reverse("product-variant-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
    