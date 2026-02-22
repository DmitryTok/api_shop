from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from profiles.models import Profile
from profiles.serializers import ProfileSerializer
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers import (
    CustomTokenObtainPairSerializer,
    UserRegisterSerializer
)
from users.services.email import send_activation_email

User = get_user_model()


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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        query = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(query)
        return Response(serializer.data)


class ActivateUserView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, uidb64, token):
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
