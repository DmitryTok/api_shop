from django.urls import path

from .views import BrandListAPIView, BrandRetrieveAPIView

urlpatterns = [
    path(
        "",
        BrandListAPIView.as_view(),
        name="brand-list",
    ),
    path(
        "<int:pk>/",
        BrandRetrieveAPIView.as_view(),
        name="brand-detail",
    ),
]
