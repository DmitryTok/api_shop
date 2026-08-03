from django.contrib import admin

from api_shop.admin import CustomModelAdmin
from .models import Discount


@admin.register(Discount)
class DiscountAdmin(CustomModelAdmin):
    list_display = (
        "id",
        "product_variant",
        "discount_type",
        "amount",
        "start_at",
        "end_at",
        "is_active",
    )
    search_fields = (
        "discount_type",
        "product_variant__sku",
    )
    list_filter = (
        "discount_type",
        "is_active",
        "start_at",
        "end_at",
    )
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("product_variant",)
