from brands.models import Brand
from categories.models import Category, Subcategory
from django import forms
from django_filters import rest_framework as filters

from .models import ProductVariant


class ProductVariantFilterForm(forms.Form):
    def clean(self):
        cleaned_data = super().clean()

        min_price = cleaned_data.get("min_price")
        max_price = cleaned_data.get("max_price")

        if min_price is not None and max_price is not None and min_price > max_price:
            raise forms.ValidationError("Min price cannot be greater than max price.")

        return cleaned_data


class ProductVariantFilter(filters.FilterSet):
    product_title = filters.CharFilter(
        field_name="product__name",
        lookup_expr="icontains",
        label="Product title",
    )
    sort_by = filters.ChoiceFilter(
        choices=(
            ("price_asc", "Price: Low to High"),
            ("price_desc", "Price: High to Low"),
            ("new_arrivals", "New Arrivals"),
        ),
        method="filter_sort_by",
        label="Sort By",
    )
    min_price = filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        label="Min price",
        min_value=1,
    )
    max_price = filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        label="Max price",
        min_value=1,
    )
    category = filters.ModelChoiceFilter(
        field_name="product__subcategory__category",
        queryset=Category.objects.all(),
        label="Category",
    )
    subcategory = filters.ModelChoiceFilter(
        field_name="product__subcategory",
        queryset=Subcategory.objects.all(),
        label="Subcategory",
        method="filter_subcategory",
    )
    brand = filters.ModelChoiceFilter(
        field_name="product__brand",
        queryset=Brand.objects.all(),
        label="Brand",
    )
    in_stock = filters.BooleanFilter(method="filter_in_stock", label="In stock")

    def filter_sort_by(self, queryset, name, value):
        ordering = {
            "price_asc": "price",
            "price_desc": "-price",
            "new_arrivals": "-created_at",
        }
        return queryset.order_by(ordering[value])

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset

    def filter_subcategory(self, queryset, name, value):
        category = self.data.get("category")

        if category and str(value.category_id) != str(category):
            return queryset.none()

        return queryset.filter(product__subcategory=value)

    class Meta:
        model = ProductVariant
        fields = ("size", "color", "gender")
        form = ProductVariantFilterForm
