import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import Term, UserTermsAcceptance
from validators.validators_users import google_token_validator, google_token_validator, accept_terms_validator, custom_token_validator, validate_login_and_password, register_user_email_validator, register_user_password_validator, password_reset_confirm_validator, validate_change_password

User = get_user_model()


class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, validators=[google_token_validator])
    accept_terms = serializers.BooleanField(write_only=True, required=True, validators=[accept_terms_validator])

    def create(self, validated_data):
        id_info = validated_data.pop("token")
        email = id_info.get("email").lower()

        if not email:
            raise serializers.ValidationError(
                {"detail": "Email not provided by Google."}
            )

        with transaction.atomic():
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"is_active": True},
            )

            if not user.is_active:
                raise serializers.ValidationError(
                    {"detail": "User account is disabled."}
                )

            try:
                terms = Term.objects.filter(is_active=True).latest(
                    "created_at"
                )

                UserTermsAcceptance.objects.get_or_create(
                    user=user, terms=terms
                )
            except Term.DoesNotExist:
                pass

        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs) -> None:
        return custom_token_validator(validate_func=super().validate, attrs=attrs)


class CustomTokenObtainPairSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs) -> dict:
        return validate_login_and_password(attrs=attrs)


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
    )
    accept_terms = serializers.BooleanField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "confirm_password", "accept_terms")
        validators = [register_user_email_validator, accept_terms_validator, register_user_password_validator]


    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("confirm_password")
        accept_terms = validated_data.pop("accept_terms")

        with transaction.atomic():
            user = User.objects.create_user(
                email=validated_data["email"].lower(),
                password=password,
                is_active=False,
            )

            if accept_terms:
                terms = Term.objects.filter(is_active=True).latest(
                    "created_at"
                )

                UserTermsAcceptance.objects.create(user=user, terms=terms)

        return user


class ActivationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(
        required=True, max_length=6, min_length=6, help_text="Activation code"
    )


class ResendActivationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "is_active")
        read_only_fields = ("id", "email", "is_active")


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    new_password = serializers.CharField(
        required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        required=True, validators=[validate_password]
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs) -> dict:
        return password_reset_confirm_validator(attrs=attrs)

    def save(self):
        password = self.validated_data["new_password"]
        self.user.set_password(password)
        self.user.save()
        return self.user


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    def validate(self, attrs) -> dict:
        return validate_change_password(user=self.context["request"].user, attrs=attrs)


    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
