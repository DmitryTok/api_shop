from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Discount
from .serializers import DiscountSerializer


class DiscountListAPIView(ListAPIView):
    queryset = Discount.objects.select_related("product_variant").all()
    serializer_class = DiscountSerializer


class DiscountRetrieveAPIView(RetrieveAPIView):
    queryset = Discount.objects.select_related("product_variant").all()
    serializer_class = DiscountSerializer