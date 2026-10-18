from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    AuthenticatedOrderSerializer,
    GuestOrderSerializer,
    OrderSerializer,
)


class OrderCreateAPIView(APIView):
    @extend_schema(
        request=OrderSerializer,
        responses={201: OrderSerializer},
    )
    def post(self, request):
        serializer_class = (
            AuthenticatedOrderSerializer
            if request.user.is_authenticated
            else GuestOrderSerializer
        )

        serializer = serializer_class(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        return Response(
            OrderSerializer(
                order,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )
