from django.urls import path

from .views import FavoriteDestroyAPIView, FavoriteListCreateAPIView


urlpatterns = [
    path("", FavoriteListCreateAPIView.as_view(), name="favorite-list-create"),
    path(
        "<int:pk>/",
        FavoriteDestroyAPIView.as_view(),
        name="favorite-destroy",
    ),
]
