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

User = get_user_model()


class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    accept_terms = serializers.BooleanField(write_only=True, required=True)

    def validate_token(self, token):
        try:
            id_info = id_token.verify_oauth2_token(
                token, requests.Request(), os.getenv("GOOGLE_CLIENT_ID")
            )

            if id_info["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise serializers.ValidationError("Wrong issuer.")

            return id_info
        except Exception as e:
            raise serializers.ValidationError(f"Invalid Google token: {str(e)}")

    def validate_accept_terms(self, value):
        if value is not True:
            raise serializers.ValidationError("You must accept the user agreement.")
        return value

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
                terms = Term.objects.filter(is_active=True).latest("created_at")

                UserTermsAcceptance.objects.get_or_create(user=user, terms=terms)
            except Term.DoesNotExist:
                pass

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except User.DoesNotExist:
            raise InvalidToken("User not found")
        except Exception as e:
            raise e

        return data


class CustomTokenObtainPairSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
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
            raise serializers.ValidationError({"detail": "User account is inactive"})

        refresh = RefreshToken.for_user(user_obj)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


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

    def validate_email(self, value):
        lower_email = value.lower()
        if User.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return lower_email

    def validate_accept_terms(self, value):
        if value is not True:
            raise serializers.ValidationError("You must accept the user agreement.")
        return value

    def validate(self, data):
        user_password = data.get("password", "").replace(" ", "")
        confirm_password = data.get("confirm_password", "").replace(" ", "")

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
        return data

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
                terms = Term.objects.filter(is_active=True).latest("created_at")

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
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(
        required=True, validators=[validate_password]
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )

        code = attrs["code"]

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

        attrs["user"] = user
        attrs["redis_key"] = redis_key
        return attrs

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

    def validate(self, attrs):
        user = self.context["request"].user

        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Password not correct"})

        if user.check_password(new_password):
            raise serializers.ValidationError(
                {"new_password": "New password cannot be the same as the old password"}
            )

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Password fields didn't match"}
            )

        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
