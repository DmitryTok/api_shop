import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from brands.models import Brand


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_brand_list(api_client):
    Brand.objects.create(
        name="Nike",
        slug="nike",
    )
    Brand.objects.create(
        name="Adidas",
        slug="adidas",
    )

    url = reverse("brand-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]["name"] == "Adidas"
    assert response.data[1]["name"] == "Nike"


@pytest.mark.django_db
def test_brand_detail(api_client):
    brand = Brand.objects.create(
        name="Nike",
        slug="nike",
    )

    url = reverse("brand-detail", kwargs={"pk": brand.pk})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Nike"
    assert response.data["slug"] == "nike"


@pytest.mark.django_db
def test_brand_detail_not_found(api_client):
    url = reverse("brand-detail", kwargs={"pk": 99999})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_brand_list_empty(api_client):
    url = reverse("brand-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
    