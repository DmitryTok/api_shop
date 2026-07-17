from django.urls import path

from .views import (
    ProductVariantListAPIView,
    ProductVariantRetrieveAPIView,
)

urlpatterns = [
    path("", ProductVariantListAPIView.as_view(), name="product-variant-list"),
    path(
        "<int:pk>/",
        ProductVariantRetrieveAPIView.as_view(),
        name="product-variant-detail",
    ),
]