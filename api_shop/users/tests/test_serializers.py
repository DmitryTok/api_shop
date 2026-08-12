from unittest.mock import patch

import pytest
from django.core.cache import cache
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser, Term, UserTermsAcceptance
from users.serializers import (
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    GoogleAuthSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    UserRegisterSerializer,
)


@pytest.mark.django_db
def test_user_register_serializer():
    Term.objects.create(
        version="1.0",
        text="Test terms",
        is_active=True,
    )

    serializer = UserRegisterSerializer(
        data={
            "email": "USER@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "accept_terms": True,
        }
    )

    assert serializer.is_valid(), serializer.errors

    user = serializer.save()

    assert user.email == "user@example.com"
    assert user.check_password("TestPassword123!")
    assert user.is_active is False


@pytest.mark.django_db
def test_user_register_serializer_existing_email():
    CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
    )

    serializer = UserRegisterSerializer(
        data={
            "email": "USER@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "accept_terms": True,
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["email"][0] == (
        "A user with this email already exists."
    )


@pytest.mark.django_db
def test_user_register_serializer_requires_terms_acceptance():
    serializer = UserRegisterSerializer(
        data={
            "email": "user@example.com",
            "password": "TestPassword123!",
            "confirm_password": "TestPassword123!",
            "accept_terms": False,
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["accept_terms"][0] == (
        "You must accept the user agreement."
    )


@pytest.mark.django_db
def test_user_register_serializer_passwords_do_not_match():
    serializer = UserRegisterSerializer(
        data={
            "email": "user@example.com",
            "password": "TestPassword123!",
            "confirm_password": "DifferentPassword123!",
            "accept_terms": True,
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["password"][0] == (
        "Password fields do not match."
    )


@pytest.mark.django_db
def test_token_obtain_pair_serializer():
    CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
        is_active=True,
    )

    serializer = CustomTokenObtainPairSerializer(
        data={
            "email_or_phone": "USER@example.com",
            "password": "TestPassword123!",
        }
    )

    assert serializer.is_valid(), serializer.errors
    assert "refresh" in serializer.validated_data
    assert "access" in serializer.validated_data


@pytest.mark.django_db
def test_token_obtain_pair_serializer_user_not_found():
    serializer = CustomTokenObtainPairSerializer(
        data={
            "email_or_phone": "unknown@example.com",
            "password": "TestPassword123!",
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["detail"][0] == (
        "No active account found with given credentials"
    )


@pytest.mark.django_db
def test_token_obtain_pair_serializer_invalid_password():
    CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
        is_active=True,
    )

    serializer = CustomTokenObtainPairSerializer(
        data={
            "email_or_phone": "user@example.com",
            "password": "WrongPassword123!",
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["detail"][0] == "Invalid password"


@pytest.mark.django_db
def test_token_refresh_serializer():
    user = CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
        is_active=True,
    )

    refresh = RefreshToken.for_user(user)

    serializer = CustomTokenRefreshSerializer(
        data={"refresh": str(refresh)}
    )

    assert serializer.is_valid(), serializer.errors
    assert "access" in serializer.validated_data


def test_google_auth_serializer_invalid_token():
    with patch(
        "users.serializers.id_token.verify_oauth2_token",
        side_effect=ValueError("Invalid token"),
    ):
        serializer = GoogleAuthSerializer(
            data={
                "token": "invalid-token",
                "accept_terms": True,
            }
        )

        assert serializer.is_valid() is False
        assert "Invalid Google token" in str(
            serializer.errors["token"][0]
        )


def test_google_auth_serializer_requires_terms_acceptance():
    with patch(
        "users.serializers.id_token.verify_oauth2_token",
        return_value={
            "iss": "accounts.google.com",
            "email": "user@example.com",
        },
    ):
        serializer = GoogleAuthSerializer(
            data={
                "token": "google-token",
                "accept_terms": False,
            }
        )

        assert serializer.is_valid() is False
        assert serializer.errors["accept_terms"][0] == (
            "You must accept the user agreement."
        )


@pytest.mark.django_db
def test_google_auth_serializer():
    Term.objects.create(
        version="1.0",
        text="Test terms",
        is_active=True,
    )

    with patch(
        "users.serializers.id_token.verify_oauth2_token",
        return_value={
            "iss": "accounts.google.com",
            "email": "USER@example.com",
        },
    ):
        serializer = GoogleAuthSerializer(
            data={
                "token": "google-token",
                "accept_terms": True,
            }
        )

        assert serializer.is_valid(), serializer.errors

        result = serializer.save()

        assert "refresh" in result
        assert "access" in result

        user = CustomUser.objects.get(email="user@example.com")
        assert user.is_active is True

        assert UserTermsAcceptance.objects.filter(
            user=user
        ).exists()


@pytest.mark.django_db
def test_google_auth_serializer_disabled_user():
    CustomUser.objects.create_user(
        email="user@example.com",
        password="TestPassword123!",
        is_active=False,
    )

    with patch(
        "users.serializers.id_token.verify_oauth2_token",
        return_value={
            "iss": "accounts.google.com",
            "email": "user@example.com",
        },
    ):
        serializer = GoogleAuthSerializer(
            data={
                "token": "google-token",
                "accept_terms": True,
            }
        )

        assert serializer.is_valid(), serializer.errors

        with pytest.raises(Exception) as exc_info:
            serializer.save()

        assert "User account is disabled." in str(exc_info.value)


@pytest.mark.django_db
def test_password_reset_confirm_serializer():
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

    serializer = PasswordResetConfirmSerializer(
        data={
            "code": "123456",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        }
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["user"] == user
    assert serializer.validated_data["redis_key"] == (
        "password_reset:123456:user_id"
    )


@pytest.mark.django_db
def test_password_reset_confirm_serializer_passwords_do_not_match():
    serializer = PasswordResetConfirmSerializer(
        data={
            "code": "123456",
            "new_password": "NewPassword123!",
            "confirm_password": "DifferentPassword123!",
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["password_confirm"][0] == (
        "Passwords do not match."
    )


@pytest.mark.django_db
def test_password_reset_confirm_serializer_invalid_code():
    cache.delete("password_reset:123456:user_id")

    serializer = PasswordResetConfirmSerializer(
        data={
            "code": "123456",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["code"][0] == (
        "Invalid or expired reset code."
    )


@pytest.mark.django_db
def test_password_reset_confirm_serializer_user_not_found():
    cache.set(
        "password_reset:123456:user_id",
        999999,
        timeout=300,
    )

    serializer = PasswordResetConfirmSerializer(
        data={
            "code": "123456",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        }
    )

    assert serializer.is_valid() is False
    assert serializer.errors["code"][0] == "User not found."


@pytest.mark.django_db
def test_password_change_serializer():
    user = CustomUser.objects.create_user(
        email="user@example.com",
        password="OldPassword123!",
        is_active=True,
    )

    request = APIRequestFactory().post("/")
    request.user = user

    serializer = PasswordChangeSerializer(
        data={
            "old_password": "OldPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        },
        context={"request": request},
    )

    assert serializer.is_valid(), serializer.errors

    serializer.save()

    user.refresh_from_db()
    assert user.check_password("NewPassword123!")


@pytest.mark.django_db
def test_password_change_serializer_wrong_old_password():
    user = CustomUser.objects.create_user(
        email="user@example.com",
        password="OldPassword123!",
        is_active=True,
    )

    request = APIRequestFactory().post("/")
    request.user = user

    serializer = PasswordChangeSerializer(
        data={
            "old_password": "WrongPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        },
        context={"request": request},
    )

    assert serializer.is_valid() is False
    assert serializer.errors["old_password"][0] == (
        "Password not correct"
    )


@pytest.mark.django_db
def test_password_change_serializer_same_password():
    user = CustomUser.objects.create_user(
        email="user@example.com",
        password="OldPassword123!",
        is_active=True,
    )

    request = APIRequestFactory().post("/")
    request.user = user

    serializer = PasswordChangeSerializer(
        data={
            "old_password": "OldPassword123!",
            "new_password": "OldPassword123!",
            "confirm_password": "OldPassword123!",
        },
        context={"request": request},
    )

    assert serializer.is_valid() is False
    assert serializer.errors["new_password"][0] == (
        "New password cannot be the same as the old password"
    )


@pytest.mark.django_db
def test_password_change_serializer_passwords_do_not_match():
    user = CustomUser.objects.create_user(
        email="user@example.com",
        password="OldPassword123!",
        is_active=True,
    )

    request = APIRequestFactory().post("/")
    request.user = user

    serializer = PasswordChangeSerializer(
        data={
            "old_password": "OldPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "DifferentPassword123!",
        },
        context={"request": request},
    )

    assert serializer.is_valid() is False
    assert serializer.errors["confirm_password"][0] == (
        "Password fields didn't match"
    )