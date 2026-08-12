import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from categories.models import Category, Subcategory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_category_list(api_client):
    Category.objects.create(name="Women", slug="women")
    Category.objects.create(name="Men", slug="men")

    url = reverse("category-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_category_detail(api_client):
    category = Category.objects.create(
        name="Women",
        slug="women",
    )

    url = reverse("category-detail", kwargs={"pk": category.pk})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Women"
    assert response.data["slug"] == "women"


@pytest.mark.django_db
def test_category_detail_not_found(api_client):
    url = reverse("category-detail", kwargs={"pk": 99999})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_category_list_empty(api_client):
    url = reverse("category-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


@pytest.mark.django_db
def test_subcategory_list(api_client):
    category = Category.objects.create(
        name="Women",
        slug="women",
    )
    Subcategory.objects.create(
        category=category,
        name="Dresses",
        slug="dresses",
    )
    Subcategory.objects.create(
        category=category,
        name="Shoes",
        slug="shoes",
    )

    url = reverse("subcategory-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db
def test_subcategory_detail(api_client):
    category = Category.objects.create(
        name="Women",
        slug="women",
    )
    subcategory = Subcategory.objects.create(
        category=category,
        name="Dresses",
        slug="dresses",
    )

    url = reverse(
        "subcategory-detail",
        kwargs={"pk": subcategory.pk},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Dresses"
    assert response.data["slug"] == "dresses"


@pytest.mark.django_db
def test_subcategory_detail_not_found(api_client):
    url = reverse(
        "subcategory-detail",
        kwargs={"pk": 99999},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_subcategory_list_empty(api_client):
    url = reverse("subcategory-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
    