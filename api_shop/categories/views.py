from rest_framework.viewsets import ModelViewSet

from categories.models import Category, Subcategory
from categories.serializers import (
    CategorySerializer,
    SubcategorySerializer,
)


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "id"


class SubcategoryViewSet(ModelViewSet):
    queryset = Subcategory.objects.select_related("category")
    serializer_class = SubcategorySerializer
    lookup_field = "id"
    