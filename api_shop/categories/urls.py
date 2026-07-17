from django.urls import path

from categories.views import (
    CategoryListAPIView,
    CategoryRetrieveAPIView,
    SubcategoryListAPIView,
    SubcategoryRetrieveAPIView,
)

urlpatterns = [
    path(
        "categories/",
        CategoryListAPIView.as_view(),
        name="category-list",
    ),
    path(
        "categories/<int:pk>/",
        CategoryRetrieveAPIView.as_view(),
        name="category-detail",
    ),
    path(
        "subcategories/",
        SubcategoryListAPIView.as_view(),
        name="subcategory-list",
    ),
    path(
        "subcategories/<int:pk>/",
        SubcategoryRetrieveAPIView.as_view(),
        name="subcategory-detail",
    ),
]