import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from colors.models import Color


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_color_list(api_client):
    Color.objects.create(name="Black", hex_code="#000000")
    Color.objects.create(name="White", hex_code="#FFFFFF")

    url = reverse("color-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]["name"] == "Black"
    assert response.data[1]["name"] == "White"


@pytest.mark.django_db
def test_color_detail(api_client):
    color = Color.objects.create(
        name="Black",
        hex_code="#000000",
    )

    url = reverse("color-detail", kwargs={"pk": color.pk})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Black"
    assert response.data["hex_code"] == "#000000"
    assert response.data["is_active"] is True


@pytest.mark.django_db
def test_color_detail_not_found(api_client):
    url = reverse("color-detail", kwargs={"pk": 99999})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_color_list_empty(api_client):
    url = reverse("color-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
    