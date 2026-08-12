import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import CustomUser


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        email="user@example.com",
        password="testpassword123",
        is_active=True,
    )


@pytest.fixture
def second_user():
    return CustomUser.objects.create_user(
        email="second@example.com",
        password="testpassword123",
        is_active=True,
    )


@pytest.mark.django_db
def test_profile_list_requires_authentication(api_client):
    url = reverse("profile-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_own_profile(api_client, user):
    api_client.force_authenticate(user=user)

    url = reverse(
        "profile-detail",
        kwargs={"profile_id": user.profile.pk},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == user.profile.pk
    assert response.data["user"]["email"] == user.email


@pytest.mark.django_db
def test_cannot_retrieve_another_users_profile(
    api_client,
    user,
    second_user,
):
    api_client.force_authenticate(user=user)

    url = reverse(
        "profile-detail",
        kwargs={"profile_id": second_user.profile.pk},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_patch_own_profile(api_client, user):
    api_client.force_authenticate(user=user)

    url = reverse(
        "profile-detail",
        kwargs={"profile_id": user.profile.pk},
    )
    response = api_client.patch(
        url,
        {"first_name": "Anna"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    user.profile.refresh_from_db()

    assert user.profile.first_name == "Anna"


@pytest.mark.django_db
def test_put_own_profile(api_client, user):
    api_client.force_authenticate(user=user)

    url = reverse(
        "profile-detail",
        kwargs={"profile_id": user.profile.pk},
    )
    response = api_client.put(
        url,
        {
            "first_name": "Anna",
            "last_name": "Smith",
            "gender": 2,
            "clothing_size": 3,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    user.profile.refresh_from_db()

    assert user.profile.first_name == "Anna"
    assert user.profile.last_name == "Smith"


@pytest.mark.django_db
def test_profile_list_excludes_staff_users(api_client, user):
    staff_user = CustomUser.objects.create_user(
        email="staff@example.com",
        password="testpassword123",
        is_active=True,
        is_staff=True,
    )

    api_client.force_authenticate(user=user)

    url = reverse("profile-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    profile_ids = [profile["id"] for profile in response.data]

    assert user.profile.pk in profile_ids
    assert staff_user.profile.pk not in profile_ids
    