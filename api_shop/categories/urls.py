from django.urls import path

from categories.views import (
    CategoryAPIView,
    SubcategoryAPIView,
)

urlpatterns = [
    path("categories/", CategoryAPIView.as_view(), name="categories"),
    path("subcategories/", SubcategoryAPIView.as_view(), name="subcategories"),
]
