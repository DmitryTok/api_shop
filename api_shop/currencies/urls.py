from django.urls import path

from .views import CurrencyListAPIView, CurrencyRetrieveAPIView

urlpatterns = [
    path("", CurrencyListAPIView.as_view(), name="currency-list"),
    path("<int:pk>/", CurrencyRetrieveAPIView.as_view(), name="currency-detail"),
]
