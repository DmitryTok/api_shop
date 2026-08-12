import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from brands.models import Brand
from categories.models import Category, Subcategory
from products.models import Product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def product_dependencies():
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

    return brand, subcategory


@pytest.mark.django_db
def test_product_list(api_client, product_dependencies):
    brand, subcategory = product_dependencies

    Product.objects.create(
        name="Air Max",
        slug="air-max",
        brand=brand,
        subcategory=subcategory,
    )
    Product.objects.create(
        name="Air Force",
        slug="air-force",
        brand=brand,
        subcategory=subcategory,
    )

    url = reverse("product-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_product_detail(api_client, product_dependencies):
    brand, subcategory = product_dependencies

    product = Product.objects.create(
        name="Air Max",
        slug="air-max",
        description="Running shoes",
        brand=brand,
        subcategory=subcategory,
    )

    url = reverse("product-detail", kwargs={"pk": product.pk})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Air Max"
    assert response.data["slug"] == "air-max"
    assert response.data["description"] == "Running shoes"
    assert response.data["brand"] == brand.pk
    assert response.data["subcategory"] == subcategory.pk
    assert response.data["is_active"] is True
    assert response.data["is_hidden"] is False


@pytest.mark.django_db
def test_product_detail_not_found(api_client):
    url = reverse("product-detail", kwargs={"pk": 99999})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_product_list_empty(api_client):
    url = reverse("product-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
    