from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
    default_token_generator
)
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from profiles.models import Profile
from profiles.serializers import ProfileSerializer
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from users.serializers import (
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserRegisterSerializer
)
from users.services.email import (
    send_activation_email,
    send_password_reset_email
)

from api_shop.settings import (
    MAX_PASSWORD_RESET_ATTEMPTS,
    MAX_REFRESH_ATTEMPTS,
    PASSWORD_RESET_TIMEOUT,
    REFRESH_TOKEN_TIMEOUT
)

User = get_user_model()


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
        send_activation_email(new_user, self.request)

        return Response(
            "Activation email has been sended", status=status.HTTP_201_CREATED
        )


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(query)
        return Response(serializer.data)


class ActivateUserView(APIView):
    serializer_class = None
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        return self.activate_user(uidb64, token)

    def patch(self, request, uidb64, token):
        return self.activate_user(uidb64, token)

    def activate_user(self, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_active:
            return Response(
                {"error": "Account already activated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"success": "Account activated successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
        )


class CustomTokenObtainPairView(APIView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            user = get_object_or_404(
                User, email=serializer.validated_data["email"]
            )

            password_reset_key = f"password_resets_{user.email}"
            password_reset_attempts = cache.get(password_reset_key, 0)

            if password_reset_attempts >= MAX_PASSWORD_RESET_ATTEMPTS:
                return Response(
                    {
                        "message": f"You can reset your password only {MAX_PASSWORD_RESET_ATTEMPTS} times per 24 hours"
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            else:
                result = send_password_reset_email(user, request)
                if result:
                    return Response(
                        {"detail": "Email was sent successfully"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "detail": "Email service is temporarily unavailable. Please try again later."
                        },
                        status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        uidb64 = kwargs.get("uidb64")
        token = kwargs.get("token")

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)

        except UnicodeDecodeError:
            return Response(
                {"detail": "Invalid uidb64."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_generator = PasswordResetTokenGenerator()

        if user and token_generator.check_token(user, token):
            serializer = self.serializer_class(data=request.data, user=user)
            if serializer.is_valid():
                serializer.save()

                password_reset_key = f"password_resets_{user.email}"
                block_key = f"password_reset_block_{user.email}"

                if cache.get(block_key):
                    return Response(
                        {
                            "detail": "Password reset limit reached. Try again after 24 hours."
                        },
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )

                password_reset_attempts = cache.get(password_reset_key)

                if password_reset_attempts is None:
                    password_reset_attempts = 1
                    cache.set(
                        password_reset_key,
                        password_reset_attempts,
                        timeout=PASSWORD_RESET_TIMEOUT,
                    )
                else:
                    cache.incr(password_reset_key)
                    password_reset_attempts += 1

                if password_reset_attempts > MAX_PASSWORD_RESET_ATTEMPTS:
                    cache.set(block_key, True, timeout=PASSWORD_RESET_TIMEOUT)
                    return Response(
                        {
                            "detail": "You have reached the limit of 3 password resets per day."
                        },
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )

                return Response(
                    {"detail": "Password has been reset."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
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
