import os
import re

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


User = get_user_model()


class GoogleAuthTokenValidator:
    def __call__(self, attrs: dict) -> None:
        token = attrs.get("token")
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


class AcceptTermsValidator:
    def __call__(self, attrs: dict) -> None:
        accept_terms = attrs.get("accept_terms")

        if accept_terms is not True:
            raise serializers.ValidationError(
                "You must accept the user agreement."
            )



class TokenExceptionWrapperValidator:
    def validate(self, validate_func, attrs):
        try:
            validate_func(attrs)
        except User.DoesNotExist:
            raise InvalidToken("User not found")
        except Exception as e:
            raise e


class LoginAndPasswordValidator:
    def __call__(self, attrs: dict) -> None:
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

        attrs["user"] = user_obj

        return attrs


class UserRegisterEmailValidator:
    def __call__(self, attrs: dict) -> None:
        email = attrs.get("email")
        lower_email = email.lower()
        if User.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )


class UserRegisterPasswordValidator:
    def __call__(self, attrs: dict) -> None:
        user_password = attrs.get("password", "").replace(' ', '')
        confirm_password = attrs.get("confirm_password", "").replace(' ', '')

        attrs["password"] = user_password
        attrs["confirm_password"] = confirm_password

        if user_password != confirm_password:
            raise serializers.ValidationError(
                {"password": "Password fields do not match."}
            )

        try:
            validate_password(user_password)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})


class PasswordResetConfirmValidator:
    def __call__(self, attrs: dict) -> None:
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


class PasswordChangeValidator:
    def __call__(self, attrs: dict) -> None:
        user = self.context["request"].user

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
