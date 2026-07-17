from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Brand
from .serializers import BrandSerializer


class BrandListAPIView(ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class BrandRetrieveAPIView(RetrieveAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer