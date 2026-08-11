from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import ProductImage
from .serializers import ProductImageSerializer


class ProductImageListAPIView(ListAPIView):
    queryset = ProductImage.objects.select_related("product_variant").all()
    serializer_class = ProductImageSerializer


class ProductImageRetrieveAPIView(RetrieveAPIView):
    queryset = ProductImage.objects.select_related("product_variant").all()
    serializer_class = ProductImageSerializer
