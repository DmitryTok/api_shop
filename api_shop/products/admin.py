from django.contrib import admin
from product_variants.models import ProductVariant

from .models import Product


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

    fields = (
        "sku",
        "size",
        "color",
        "gender",
        "stock",
        "is_active",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
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

    inlines = (ProductVariantInline,)
