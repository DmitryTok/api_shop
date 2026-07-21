from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Currency
from .serializers import CurrencySerializer


class CurrencyListAPIView(ListAPIView):
    queryset = Currency.objects.select_related("product_variant").all()
    serializer_class = CurrencySerializer


class CurrencyRetrieveAPIView(RetrieveAPIView):
    queryset = Currency.objects.select_related("product_variant").all()
    serializer_class = CurrencySerializer


