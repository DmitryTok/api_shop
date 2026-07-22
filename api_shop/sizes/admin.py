from django.contrib import admin

from .models import Size


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "size_type",
        "sort_order",
    )
    search_fields = ("name",)
    list_filter = ("size_type",)
    readonly_fields = ("created_at", "updated_at")
