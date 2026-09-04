from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import FavoriteUserListAPIView, FavoriteViewSet

router = DefaultRouter()
router.register("", FavoriteViewSet, basename="favorite")

urlpatterns = [
    path(
        "favorites-user-list/",
        FavoriteUserListAPIView.as_view(),
        name="favorite-user-list",
    ),
]


urlpatterns += router.urls
