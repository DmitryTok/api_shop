from django_filters import rest_framework as filters
from .models import Category


class CategoryFilter(filters.FilterSet):
    is_active = filters.BooleanFilter(field_name="is_active")
    is_hidden = filters.BooleanFilter(field_name="is_hidden")

    class Meta:
        model = Category
        fields = ["is_active", "is_hidden"]