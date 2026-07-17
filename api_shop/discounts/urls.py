from django.urls import path

from .views import DiscountListAPIView, DiscountRetrieveAPIView


urlpatterns = [
    path("", DiscountListAPIView.as_view(), name="discount-list"),
    path("<int:pk>/", DiscountRetrieveAPIView.as_view(), name="discount-detail"),
]