from django.contrib import admin

from api_shop.admin import CustomModelAdmin
from .models import Product


@admin.register(Product)
class ProductAdmin(CustomModelAdmin):
    list_display = (
        "id",
        "name",
        "brand",
        "subcategory",
        "is_active",
        "is_hidden",
    )
    search_fields = (
        "name",
        "slug",
        "brand__name",
        "subcategory__name",
    )
    list_filter = (
        "brand",
        "subcategory",
        "is_active",
        "is_hidden",
    )
    readonly_fields = ("created_at", "updated_at")
    list_select_related = (
        "brand",
        "subcategory",
    )
