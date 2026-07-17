from django.urls import path

from .views import ColorListAPIView, ColorRetrieveAPIView


urlpatterns = [
    path("", ColorListAPIView.as_view(), name="color-list"),
    path("<int:pk>/", ColorRetrieveAPIView.as_view(), name="color-detail"),
]