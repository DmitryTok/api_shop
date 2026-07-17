from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import ProductVariant
from .serializers import ProductVariantSerializer


class ProductVariantListAPIView(ListAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer


class ProductVariantRetrieveAPIView(RetrieveAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer


