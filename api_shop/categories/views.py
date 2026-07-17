from rest_framework.views import APIView
from rest_framework.response import Response

from categories.models import Category, Subcategory
from categories.serializers import (
    CategorySerializer,
    SubcategorySerializer,
)


class CategoryAPIView(APIView):

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class SubcategoryAPIView(APIView):

    def get(self, request):
        subcategories = Subcategory.objects.select_related("category")
        serializer = SubcategorySerializer(subcategories, many=True)
        return Response(serializer.data)
    