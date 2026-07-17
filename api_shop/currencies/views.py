from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Currency
from .serializers import CurrencySerializer


class CurrencyListAPIView(ListAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class CurrencyRetrieveAPIView(RetrieveAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


