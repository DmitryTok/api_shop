import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_create_user_defaults_is_active_false():
    user = User.objects.create_user(email="newuser@example.com", password="Test1234!")

    assert user.is_active is False
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_create_superuser_is_active_and_staff():
    user = User.objects.create_superuser(
        email="admin@example.com", password="Test1234!"
    )

    assert user.is_active is True
    assert user.is_staff is True
    assert user.is_superuser is True


@pytest.mark.django_db
def test_activate_user_view_with_valid_code_activates_user(client):
    user = User.objects.create_user(
        email="activateme@example.com", password="Test1234!"
    )
    cache.set("activation:111111:user_id", user.id, timeout=300)

    response = client.patch(
        reverse("activate-user"),
        data={"code": "111111"},
        content_type="application/json",
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.is_active is True
    assert cache.get("activation:111111:user_id") is None


@pytest.mark.django_db
def test_activate_user_view_with_invalid_code_returns_400(client):
    response = client.patch(
        reverse("activate-user"),
        data={"code": "222222"},
        content_type="application/json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_activate_user_view_already_active_returns_400(client):
    user = User.objects.create_user(
        email="alreadyactive@example.com", password="Test1234!", is_active=True
    )
    cache.set("activation:333333:user_id", user.id, timeout=300)

    response = client.patch(
        reverse("activate-user"),
        data={"code": "333333"},
        content_type="application/json",
    )

    assert response.status_code == 400
