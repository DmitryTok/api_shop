from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


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

    class Meta:
        model = User
        fields = ("email", "password", "confirm_password")

    def validate_email(self, value):
        lower_email = value.lower()
        if User.objects.filter(email__iexact=lower_email).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return lower_email

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "Password fields do not match."}
            )
        try:
            validate_password(data['password'])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return data

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        validated_data.pop("confirm_password", None)

        user = User.objects.create_user(
            email=validated_data["email"].lower(),
            password=password,
            is_active=False,
        )
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
