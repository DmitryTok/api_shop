import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from sizes.models import Kind, Size


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_size_list(api_client):
    Size.objects.create(
        name="M",
        size_type=Kind.CLOTHING,
        sort_order=2,
    )
    Size.objects.create(
        name="S",
        size_type=Kind.CLOTHING,
        sort_order=1,
    )

    url = reverse("size-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]["name"] == "S"
    assert response.data[1]["name"] == "M"


@pytest.mark.django_db
def test_size_detail(api_client):
    size = Size.objects.create(
        name="M",
        size_type=Kind.CLOTHING,
        sort_order=2,
    )

    url = reverse("size-detail", kwargs={"pk": size.pk})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "M"
    assert response.data["size_type"] == Kind.CLOTHING
    assert response.data["sort_order"] == 2


@pytest.mark.django_db
def test_size_detail_not_found(api_client):
    url = reverse("size-detail", kwargs={"pk": 99999})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_size_list_empty(api_client):
    url = reverse("size-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0
    