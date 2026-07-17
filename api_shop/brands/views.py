from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Brand
from .serializers import BrandSerializer


class BrandAPIView(APIView):

    def get(self, request):
        brands = Brand.objects.all()
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data)