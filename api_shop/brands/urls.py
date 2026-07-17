from django.urls import path

from .views import BrandAPIView


urlpatterns = [
    path("", BrandAPIView.as_view(), name="brands"),
]