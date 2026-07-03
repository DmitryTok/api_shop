from categories.views import CategoryViewSet, SubcategoryViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("categories", CategoryViewSet)
router.register("subcategories", SubcategoryViewSet)

urlpatterns = router.urls
