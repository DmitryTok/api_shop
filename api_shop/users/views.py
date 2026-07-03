import threading

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from profiles.models import Profile
from profiles.serializers import ProfileSerializer
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from users.serializers import (
    ActivationCodeSerializer,
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    GoogleAuthSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ResendActivationCodeSerializer,
    UserRegisterSerializer
)
from users.services.email import send_email_code

from api_shop.settings import MAX_REFRESH_ATTEMPTS, REFRESH_TOKEN_TIMEOUT

User = get_user_model()


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GoogleAuthSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.save()

        return Response(tokens, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        user_refresh_token = request.data.get("refresh")

        if not user_refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(user_refresh_token, verify=False)
            user_ip = token.get('user_id')

        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        cache_key = f"refresh_limit_{user_ip}"
        block_key = f"refresh_block_{user_ip}"

        if cache.get(block_key):
            return Response(
                {"detail": "Too many refresh attempts. Try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        attempts = cache.get(cache_key, 0)

        if attempts >= MAX_REFRESH_ATTEMPTS:
            cache.set(block_key, True, timeout=REFRESH_TOKEN_TIMEOUT)
            return Response(
                {
                    "detail": f"Limit of {MAX_REFRESH_ATTEMPTS} attempts reached."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            if attempts == 0:
                cache.set(cache_key, 1, timeout=REFRESH_TOKEN_TIMEOUT)
            else:
                cache.incr(cache_key)

        return response


class RegistrationView(APIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()

        email_thread = threading.Thread(
            target=send_email_code, args=(new_user, "activation", request)
        )

        email_thread.start()

        return Response(
            "Activation email has been sended", status=status.HTTP_201_CREATED
        )


class CurrentUserView(APIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(query)
        return Response(serializer.data)


class ActivateUserView(APIView):
    serializer_class = ActivationCodeSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code'].strip()

        user_id = cache.get(f"activation:{code}:user_id")

        if user_id is None:
            return Response(
                {"error": "Invalid or expired activation code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.is_active:
            return Response(
                {"error": "User account is already activated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save()

        cache.delete(f"activation:{code}:user_id")

        return Response(
            {"detail": "Your account has been successfully activated!"},
            status=status.HTTP_200_OK,
        )


class ResendActivationCodeView(APIView):
    serializer_class = ResendActivationCodeSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(
                email=serializer.validated_data['email'].lower().strip()
            )
        except User.DoesNotExist:
            return Response(
                {
                    "detail": "If the account exists, a new activation code has been sent."
                },
                status=status.HTTP_200_OK,
            )

        if user.is_active:
            return Response(
                {"error": "This account is already activated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_thread = threading.Thread(
            target=send_email_code, args=(user, "activation", request)
        )

        email_thread.start()

        return Response(
            {"detail": "A new activation code has been sent to your email."},
            status=status.HTTP_200_OK,
        )


class CustomTokenObtainPairView(APIView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(
                email=serializer.validated_data['email'].lower().strip()
            )
        except User.DoesNotExist:
            return Response(
                {
                    "detail": "If the account exists, a password reset code has been sent."
                },
                status=status.HTTP_200_OK,
            )

        if not user.is_active:
            return Response(
                {"error": "This account is not activated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email_thread = threading.Thread(
            target=send_email_code, args=(user, "password_reset", request)
        )

        email_thread.start()

        return Response(
            {"detail": "Password reset code has been sent to your email."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        redis_key = serializer.validated_data['redis_key']
        new_password = serializer.validated_data['new_password']

        user.set_password(new_password)
        user.save()

        cache.delete(redis_key)
        cache.delete(f"user:{user.id}:password_reset_code")

        return Response(
            {
                "detail": "Password has been successfully reset. You can now log in with your new password."
            },
            status=status.HTTP_200_OK,
        )


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Password has been changed successfully"},
            status=status.HTTP_200_OK,
        )
