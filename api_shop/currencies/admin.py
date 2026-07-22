from django.contrib import admin

from .models import Currency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_variant",
        "currency_code",
        "amount",
    )
    search_fields = (
        "currency_code",
        "product_variant__sku",
    )
    list_filter = ("currency_code",)
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("product_variant",)