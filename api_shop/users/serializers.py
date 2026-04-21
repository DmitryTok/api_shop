from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import Term, UserTermsAcceptance

User = get_user_model()


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
            user_obj = User.objects.get(
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
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return lower_email

    def validate_accept_terms(self, value):
        if value is not True:
            raise serializers.ValidationError(
                "You must accept the user agreement."
            )
        return value

    def validate(self, data):
        user_password = data.get("password", "")
        confirm_password = data.get("confirm_password", "")

        if " " in user_password or user_password != user_password.strip():
            raise serializers.ValidationError(
                {"password": "Password must not contain spaces."}
            )

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
                terms = Term.objects.filter(is_active=True).latest(
                    "created_at"
                )

                UserTermsAcceptance.objects.create(user=user, terms=terms)

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "is_active")
        read_only_fields = ("id", "email", "is_active")


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        get_object_or_404(User, email=value)
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        required=True, validators=[validate_password]
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        new_password = attrs["new_password"]
        confirm_password = attrs["confirm_password"]

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Password fields didn't match."}
            )

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

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
