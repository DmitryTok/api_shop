from django.urls import path

from .views import SizeListAPIView, SizeRetrieveAPIView


urlpatterns = [
    path("", SizeListAPIView.as_view(), name="size-list"),
    path("<int:pk>/", SizeRetrieveAPIView.as_view(), name="size-detail"),
]