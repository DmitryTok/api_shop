from django.contrib import admin

from api_shop.admin import CustomModelAdmin
from .models import Size


@admin.register(Size)
class SizeAdmin(CustomModelAdmin):
    list_display = (
        "id",
        "name",
        "size_type",
        "sort_order",
    )
    search_fields = ("name",)
    list_filter = ("size_type",)
    readonly_fields = ("created_at", "updated_at")
