from django.contrib import admin

from api_shop.admin import CustomModelAdmin
from .models import ProductImage


@admin.register(ProductImage)
class ProductImageAdmin(CustomModelAdmin):
    list_display = (
        "id",
        "product_variant",
        "is_main",
        "sort_order",
    )
    search_fields = ("product_variant__sku",)
    list_filter = ("is_main",)
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("product_variant",)
