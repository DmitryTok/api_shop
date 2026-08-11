from rest_framework.generics import ListAPIView, RetrieveAPIView

from categories.models import Category, Subcategory
from categories.serializers import (
    CategorySerializer,
    SubcategorySerializer,
)


class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryRetrieveAPIView(RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubcategoryListAPIView(ListAPIView):
    queryset = Subcategory.objects.select_related("category")
    serializer_class = SubcategorySerializer


class SubcategoryRetrieveAPIView(RetrieveAPIView):
    queryset = Subcategory.objects.select_related("category")
    serializer_class = SubcategorySerializer
