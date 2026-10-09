from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OrderSerializer


class OrderCreateAPIView(APIView):
    @extend_schema(
        request=OrderSerializer,
        responses={201: OrderSerializer},
    )
    def post(self, request):
        serializer = OrderSerializer(
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
