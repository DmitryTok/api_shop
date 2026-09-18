from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Product
from .serializers import ProductSerializer


class ProductListAPIView(ListAPIView):
    queryset = Product.objects.select_related("brand", "subcategory").all()
    serializer_class = ProductSerializer
    filterset_fields = ("brand", "subcategory", "is_active", "is_hidden")


class ProductRetrieveAPIView(RetrieveAPIView):
    queryset = Product.objects.select_related("brand", "subcategory").all()
    serializer_class = ProductSerializer
