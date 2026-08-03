from django.contrib import admin

from api_shop.admin import CustomModelAdmin
from .models import ProductVariant


@admin.register(ProductVariant)
class ProductVariantAdmin(CustomModelAdmin):
    list_display = (
        "id",
        "sku",
        "product",
        "size",
        "color",
        "gender",
        "stock",
        "is_active",
    )
    search_fields = (
        "sku",
        "product__name",
    )
    list_filter = (
        "gender",
        "is_active",
        "size",
        "color",
    )
    readonly_fields = ("created_at", "updated_at")
    list_select_related = (
        "product",
        "size",
        "color",
    )