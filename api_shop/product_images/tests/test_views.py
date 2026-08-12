import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from brands.models import Brand
from categories.models import Category, Subcategory
from colors.models import Color
from product_images.models import ProductImage
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
        name="T-Shirts",
        slug="t-shirts",
    )
    product = Product.objects.create(
        name="Nike T-Shirt",
        slug="nike-t-shirt",
        brand=brand,
        subcategory=subcategory,
    )
    size = Size.objects.create(
        name="S",
        size_type=Kind.CLOTHING,
        sort_order=1,
    )
    color = Color.objects.create(
        name="White",
        hex_code="#FFFFFF",
    )

    return ProductVariant.objects.create(
        product=product,
        size=size,
        color=color,
        sku="NIKE-WHITE-S",
        stock=10,
        gender=Gender.UNISEX,
    )


@pytest.fixture
def image_file():
    return SimpleUploadedFile(
        "shirt.jpg",
        b"fake-image-content",
        content_type="image/jpeg",
    )


@pytest.mark.django_db
def test_product_image_list(api_client, variant, image_file):
    ProductImage.objects.create(
        product_variant=variant,
        image=image_file,
        is_main=True,
        sort_order=1,
    )

    url = reverse("product-image-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["product_variant"] == variant.pk
    assert response.data[0]["is_main"] is True
    assert response.data[0]["sort_order"] == 1


@pytest.mark.django_db
def test_product_image_detail(api_client, variant, image_file):
    product_image = ProductImage.objects.create(
        product_variant=variant,
        image=image_file,
        is_main=False,
        sort_order=2,
    )

    url = reverse(
        "product-image-detail",
        kwargs={"pk": product_image.pk},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["product_variant"] == variant.pk
    assert response.data["is_main"] is False
    assert response.data["sort_order"] == 2


@pytest.mark.django_db
def test_product_image_detail_not_found(api_client):
    url = reverse(
        "product-image-detail",
        kwargs={"pk": 99999},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_product_image_list_empty(api_client):
    url = reverse("product-image-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
    