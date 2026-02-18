from rest_framework.views import APIView
from users.serializers import UserRegisterSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationView(APIView):
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_user = serializer.save()

        return Response(
            UserSerializer(new_user).data, status=status.HTTP_201_CREATED
        )


class CurrentUserView(APIView):
    def get(self, request, *args, **kwargs):
        user = User.objects.raw(
            "SELECT * FROM users WHERE id = %s", [request.user.id]
        )
        if not user:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        else:
            serializer = UserSerializer(user)
            return Response(serializer.data)
