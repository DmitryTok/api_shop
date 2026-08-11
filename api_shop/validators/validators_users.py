import os
import re
from typing import Any, Callable

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import Q
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def google_token_validator(token: str) -> dict[str, Any]:
    try:
        id_info = id_token.verify_oauth2_token(
            token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID')
        )

        if id_info['iss'] not in [
            'accounts.google.com',
            'https://accounts.google.com',
        ]:
            raise serializers.ValidationError('Wrong issuer.')

        return id_info
    except Exception as e:
        raise serializers.ValidationError(
            f'Invalid Google token: {str(e)}'
        )


def accept_terms_validator(accept_terms: bool) -> bool:
    if accept_terms is not True:
        raise serializers.ValidationError(
            "You must accept the user agreement."
        )
    return accept_terms


def custom_token_validator(validate_func: Callable, attrs: dict) -> None:
    try:
        data = validate_func(attrs)
    except User.DoesNotExist:
        raise InvalidToken("User not found")
    except Exception as e:
        raise e

    return data


def validate_login_and_password(attrs: dict) -> dict:
    login = attrs.get("email_or_phone").lower().strip()
    password = attrs.get("password")

    if not login or not password:
        raise serializers.ValidationError(
            {"detail": "Both email_or_phone and password are required"}
        )

    try:
        user_obj = User.objects.filter(is_active=True).get(
            Q(email=login) | Q(profile__phone=login)
        )
    except User.DoesNotExist:
        raise serializers.ValidationError(
            {"detail": "No active account found with given credentials"}
        )

    if not user_obj.check_password(password):
        raise serializers.ValidationError({"detail": "Invalid password"})

    if not user_obj.is_active:
        raise serializers.ValidationError(
            {"detail": "User account is inactive"}
        )

    refresh = RefreshToken.for_user(user_obj)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def register_user_email_validator(email: str) -> None:
    lower_email = email.lower()
    if User.objects.filter(email__iexact=lower_email).exists():
        raise serializers.ValidationError(
            "A user with this email already exists."
        )


def register_user_password_validator(data: dict) -> None:
    user_password = data.get("password", "").replace(' ', '')
    confirm_password = data.get("confirm_password", "").replace(' ', '')

    data["password"] = user_password
    data["confirm_password"] = confirm_password

    if user_password != confirm_password:
        raise serializers.ValidationError(
            {"password": "Password fields do not match."}
        )

    try:
        validate_password(user_password)
    except serializers.ValidationError as e:
        raise serializers.ValidationError({"password": list(e.messages)})


def password_reset_confirm_validator(attrs: dict) -> dict:
    if attrs['new_password'] != attrs['confirm_password']:
        raise serializers.ValidationError(
            {"confirm_password": "Passwords do not match."}
        )

    code = attrs['code']
    redis_key = f"password_reset:{code}:user_id"
    user_id = cache.get(redis_key)

    if not user_id:
        raise serializers.ValidationError(
            {"code": "Invalid or expired reset code."}
        )
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise serializers.ValidationError({"code": "User not found."})

    attrs['user'] = user
    attrs['redis_key'] = redis_key

    return attrs



def validate_change_password(user, attrs: dict) -> dict:
    old_password = attrs.get("old_password")
    new_password = attrs.get("new_password")
    confirm_password = attrs.get("confirm_password")

    if not user.check_password(old_password):
        raise serializers.ValidationError(
            {"old_password": "Password not correct"}
        )

    if user.check_password(new_password):
        raise serializers.ValidationError(
            {
                "new_password": "New password cannot be the same as the old password"
            }
        )

    if new_password != confirm_password:
        raise serializers.ValidationError(
            {"confirm_password": "Password fields didn't match"}
        )
    return attrs


class RegexPasswordValidator:
    def validate(self, password, user=None):

        if len(password) < 8:
            raise ValidationError(
                _(
                    "This password is too short. It must contain at least 8 characters."
                ),
                code='password_too_short',
            )

        if len(password) > 128:
            raise ValidationError(
                _(
                    "This password is too long. It must not exceed 128 characters."
                ),
                code='password_too_long',
            )

        if not re.fullmatch(r'[A-Za-z0-9!@#$%^&*(),.?":{}|<>]*', password):
            raise ValidationError(
                _(
                    "Password must contain only Latin letters, numbers, and standard symbols."
                ),
                code='password_invalid_characters',
            )

        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _(
                    "This password must contain at least one uppercase letter (A-Z)."
                ),
                code='password_no_upper',
            )

        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _(
                    "This password must contain at least one lowercase letter (a-z)."
                ),
                code='password_no_lower',
            )

        if not re.search(r'\d', password):
            raise ValidationError(
                _("This password must contain at least one digit."),
                code='password_no_digit',
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _(
                    "This password must contain at least one special character (!@#$%^&*...)."
                ),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Your password must be at least 8 characters long, contain upper and lower case letters, "
            "one digit and one special character."
        )
