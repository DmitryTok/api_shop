from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from categories.models import Category
from categories.serializers import CategorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CategoryFilter


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"

    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter

def get_queryset(self):
    qs = super().get_queryset()
    print("FILTER PARAMS:", self.request.query_params)
    return qs
