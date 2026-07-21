from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import ProductVariant
from .serializers import ProductVariantSerializer


class ProductVariantListAPIView(ListAPIView):
    queryset = ProductVariant.objects.select_related("product", "size", "color").all()
    serializer_class = ProductVariantSerializer


class ProductVariantRetrieveAPIView(RetrieveAPIView):
    queryset = ProductVariant.objects.select_related("product", "size", "color").all()
    serializer_class = ProductVariantSerializer


