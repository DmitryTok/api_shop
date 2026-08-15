from django.contrib import admin
from product_images.models import ProductImage

from .models import ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = (
        "image",
        "is_main",
        "sort_order",
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
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

    inlines = (ProductImageInline,)
