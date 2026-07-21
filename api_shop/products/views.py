from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Product
from .serializers import ProductSerializer


class ProductListAPIView(ListAPIView):
    queryset = Product.objects.select_related("brand", "subcategory").all()
    serializer_class = ProductSerializer


class ProductRetrieveAPIView(RetrieveAPIView):
    queryset = Product.objects.select_related("brand", "subcategory").all()
    serializer_class = ProductSerializer

