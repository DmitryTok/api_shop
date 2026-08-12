from unittest.mock import patch

import pytest
from django.core.cache import cache
from rest_framework.test import APIRequestFactory, force_authenticate

from profiles.models import Profile
from users.models import CustomUser, Term
from users.views import (
    ActivateUserView,
    CurrentUserView,
    CustomTokenObtainPairView,
    GoogleAuthView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegistrationView,
    ResendActivationCodeView,
)


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
@patch("users.views.threading.Thread")
def test_registration_view(mock_thread):
    Term.objects.create(
        version="1.0",
        text="Test terms",
        is_active=True,
    )

    request = APIRequestFactory().post(
        "/register/",
        {
            "email": "user@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "accept_terms": True,
        },
        format="json",
    )

    response = RegistrationView.as_view()(request)

    assert response.status_code == 201
    assert response.data == "Activation email has been sended"

    user = CustomUser.objects.get(email="user@example.com")

    mock_thread.assert_called_once()
    mock_thread.return_value.start.assert_called_once()

    assert user.is_active is False


@pytest.mark.django_db
def test_current_user_view():
    user = CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
        is_active=True,
    )

    profile, _ = Profile.objects.get_or_create(user=user)

    request = APIRequestFactory().get("/current-user/")
    force_authenticate(request, user=user)

    response = CurrentUserView.as_view()(request)

    assert response.status_code == 200
    assert response.data["id"] == profile.id


@pytest.mark.django_db
def test_activate_user_view():
    user = CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
        is_active=False,
    )

    cache.set(
        "activation:123456:user_id",
        user.id,
        timeout=300,
    )

    request = APIRequestFactory().patch(
        "/activate/",
        {"code": "123456"},
        format="json",
    )

    response = ActivateUserView.as_view()(request)

    assert response.status_code == 200
    assert response.data["detail"] == (
        "Your account has been successfully activated!"
    )

    user.refresh_from_db()
    assert user.is_active is True
    assert cache.get("activation:123456:user_id") is None


@pytest.mark.django_db
def test_activate_user_view_invalid_code():
    cache.delete("activation:123456:user_id")

    request = APIRequestFactory().patch(
        "/activate/",
        {"code": "123456"},
        format="json",
    )

    response = ActivateUserView.as_view()(request)

    assert response.status_code == 400
    assert response.data["error"] == (
        "Invalid or expired activation code."
    )


@pytest.mark.django_db
def test_activate_user_view_user_not_found():
    cache.set(
        "activation:123456:user_id",
        999999,
        timeout=300,
    )

    request = APIRequestFactory().patch(
        "/activate/",
        {"code": "123456"},
        format="json",
    )

    response = ActivateUserView.as_view()(request)

    assert response.status_code == 404
    assert response.data["error"] == "Not found."


@pytest.mark.django_db
def test_activate_user_view_already_active():
    user = CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
        is_active=True,
    )

    cache.set(
        "activation:123456:user_id",
        user.id,
        timeout=300,
    )

    request = APIRequestFactory().patch(
        "/activate/",
        {"code": "123456"},
        format="json",
    )

    response = ActivateUserView.as_view()(request)

    assert response.status_code == 400
    assert response.data["error"] == (
        "User account is already activated."
    )


@pytest.mark.django_db
def test_resend_activation_code_user_not_found():
    request = APIRequestFactory().post(
        "/resend_activation_code/",
        {"email": "unknown@example.com"},
        format="json",
    )

    response = ResendActivationCodeView.as_view()(request)

    assert response.status_code == 200
    assert response.data["detail"] == (
        "If the account exists, a new activation code has been sent."
    )


@pytest.mark.django_db
def test_resend_activation_code_already_active():
    CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
        is_active=True,
    )

    request = APIRequestFactory().post(
        "/resend_activation_code/",
        {"email": "user@example.com"},
        format="json",
    )

    response = ResendActivationCodeView.as_view()(request)

    assert response.status_code == 400
    assert response.data["error"] == (
        "This account is already activated."
    )


@pytest.mark.django_db
@patch("users.views.threading.Thread")
def test_resend_activation_code(mock_thread):
    CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
        is_active=False,
    )

    request = APIRequestFactory().post(
        "/resend_activation_code/",
        {"email": "USER@example.com"},
        format="json",
    )

    response = ResendActivationCodeView.as_view()(request)

    assert response.status_code == 200
    assert response.data["detail"] == (
        "A new activation code has been sent to your email."
    )

    mock_thread.assert_called_once()
    mock_thread.return_value.start.assert_called_once()


@pytest.mark.django_db
def test_password_reset_request_user_not_found():
    request = APIRequestFactory().post(
        "/password-reset/",
        {"email": "unknown@example.com"},
        format="json",
    )

    response = PasswordResetRequestView.as_view()(request)

    assert response.status_code == 200
    assert response.data["detail"] == (
        "If the account exists, a password reset code has been sent."
    )


@pytest.mark.django_db
def test_password_reset_request_inactive_user():
    CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
        is_active=False,
    )

    request = APIRequestFactory().post(
        "/password-reset/",
        {"email": "user@example.com"},
        format="json",
    )

    response = PasswordResetRequestView.as_view()(request)

    assert response.status_code == 400
    assert response.data["error"] == (
        "This account is not activated."
    )


@pytest.mark.django_db
@patch("users.views.threading.Thread")
def test_password_reset_request(mock_thread):
    CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
        is_active=True,
    )

    request = APIRequestFactory().post(
        "/password-reset/",
        {"email": "USER@example.com"},
        format="json",
    )

    response = PasswordResetRequestView.as_view()(request)

    assert response.status_code == 200
    assert response.data["detail"] == (
        "Password reset code has been sent to your email."
    )

    mock_thread.assert_called_once()
    mock_thread.return_value.start.assert_called_once()


@pytest.mark.django_db
def test_password_reset_confirm_view():
    user = CustomUser.objects.create_user(
        email="user@example.com",
        password="OldPassword123!",
        is_active=True,
    )

    cache.set(
        "password_reset:123456:user_id",
        user.id,
        timeout=300,
    )

    request = APIRequestFactory().post(
        "/password-reset-confirm/",
        {
            "code": "123456",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        },
        format="json",
    )

    response = PasswordResetConfirmView.as_view()(request)

    assert response.status_code == 200
    assert response.data["detail"] == (
        "Password has been successfully reset. "
        "You can now log in with your new password."
    )

    user.refresh_from_db()
    assert user.check_password("NewPassword123!")
    assert cache.get("password_reset:123456:user_id") is None


@pytest.mark.django_db
def test_password_change_view():
    user = CustomUser.objects.create_user(
        email="user@example.com",
        password="OldPassword123!",
        is_active=True,
    )

    request = APIRequestFactory().post(
        "/password-change/",
        {
            "old_password": "OldPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        },
        format="json",
    )
    force_authenticate(request, user=user)

    response = PasswordChangeView.as_view()(request)

    assert response.status_code == 200
    assert response.data["detail"] == (
        "Password has been changed successfully"
    )

    user.refresh_from_db()
    assert user.check_password("NewPassword123!")


@pytest.mark.django_db
def test_custom_token_obtain_pair_view():
    CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
        is_active=True,
    )

    request = APIRequestFactory().post(
        "/token/",
        {
            "email_or_phone": "user@example.com",
            "password": "TestPassword123!",
        },
        format="json",
    )

    response = CustomTokenObtainPairView.as_view()(request)

    assert response.status_code == 200
    assert "refresh" in response.data
    assert "access" in response.data


@pytest.mark.django_db
@patch("users.serializers.id_token.verify_oauth2_token")
def test_google_auth_view(mock_verify):
    Term.objects.create(
        version="1.0",
        text="Test terms",
        is_active=True,
    )

    mock_verify.return_value = {
        "iss": "accounts.google.com",
        "email": "user@example.com",
    }

    request = APIRequestFactory().post(
        "/auth/google/",
        {
            "token": "google-token",
            "accept_terms": True,
        },
        format="json",
    )

    response = GoogleAuthView.as_view()(request)

    assert response.status_code == 200
    assert "refresh" in response.data
    assert "access" in response.data
