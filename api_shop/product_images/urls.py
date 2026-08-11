from django.urls import path

from .views import ProductImageListAPIView, ProductImageRetrieveAPIView

urlpatterns = [
    path("", ProductImageListAPIView.as_view(), name="product-image-list"),
    path(
        "<int:pk>/", ProductImageRetrieveAPIView.as_view(), name="product-image-detail"
    ),
]
