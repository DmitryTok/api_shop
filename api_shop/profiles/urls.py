from rest_framework.routers import DefaultRouter
from profiles.views import ProfileViewSet

router = DefaultRouter()
router.register("", ProfileViewSet, basename="profile")

urlpatterns = [] + router.urls
